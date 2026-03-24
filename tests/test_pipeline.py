from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.ingest.normalize import normalize_source_pack
from src.llm.provider import (
    DeterministicProvider,
    OpenAICompatibleProvider,
    ProviderConfig,
    build_provider_from_env,
)
from src.planner.draft import draft_slide_spec
from src.quality.checks import grade_slide_spec
from src.runtime.cli import write_pipeline_outputs, write_verification_summary
from src.runtime.pipeline import run_pipeline


ROOT = Path(__file__).resolve().parent.parent
RAW_FIXTURE = ROOT / "fixtures" / "source-packs" / "example-source-pack.json"
NORMALIZED_FIXTURE = ROOT / "fixtures" / "normalized-source-units" / "example-normalized-source-units.json"
SLIDE_SPEC_FIXTURE = ROOT / "fixtures" / "slide-spec" / "example-slide-spec.json"
SLIDE_SCHEMA = ROOT / "schemas" / "slide-spec.schema.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class PipelineFixtureTests(unittest.TestCase):
    def test_fixtures_exist(self) -> None:
        self.assertTrue(RAW_FIXTURE.exists(), RAW_FIXTURE)
        self.assertTrue(NORMALIZED_FIXTURE.exists(), NORMALIZED_FIXTURE)
        self.assertTrue(SLIDE_SPEC_FIXTURE.exists(), SLIDE_SPEC_FIXTURE)

    def test_normalize_source_pack_matches_fixture(self) -> None:
        raw_pack = load_json(RAW_FIXTURE)
        normalized = normalize_source_pack(raw_pack)
        expected = load_json(NORMALIZED_FIXTURE)
        self.assertEqual(normalized, expected)

    def test_draft_slide_spec_matches_fixture(self) -> None:
        normalized = load_json(NORMALIZED_FIXTURE)
        slide_spec = draft_slide_spec(normalized)
        expected = load_json(SLIDE_SPEC_FIXTURE)
        self.assertEqual(slide_spec, expected)

    def test_drafted_slide_spec_passes_quality_checks(self) -> None:
        normalized = load_json(NORMALIZED_FIXTURE)
        slide_spec = draft_slide_spec(normalized)
        report = grade_slide_spec(normalized, slide_spec)
        self.assertEqual(report["status"], "pass")
        self.assertFalse(report["failures"])

    def test_explicit_deterministic_provider_keeps_fixture_output_stable(self) -> None:
        normalized = load_json(NORMALIZED_FIXTURE)
        provider = DeterministicProvider()

        slide_spec = draft_slide_spec(normalized, provider=provider)
        report = grade_slide_spec(normalized, slide_spec, provider=provider)

        self.assertEqual(slide_spec, load_json(SLIDE_SPEC_FIXTURE))
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["provider"], "deterministic")

    def test_build_provider_from_env_defaults_to_deterministic(self) -> None:
        provider = build_provider_from_env({})
        self.assertIsInstance(provider, DeterministicProvider)

    def test_provider_config_round_trip(self) -> None:
        provider = DeterministicProvider(
            ProviderConfig(
                provider="deterministic",
                model="baseline-fixture",
                api_key_env="IGNORED",
                base_url="http://localhost:11434",
            )
        )

        self.assertEqual(provider.config.provider, "deterministic")
        self.assertEqual(provider.config.model, "baseline-fixture")
        self.assertEqual(provider.config.base_url, "http://localhost:11434")

    def test_build_provider_from_env_supports_openai_compatible(self) -> None:
        provider = build_provider_from_env(
            {
                "GROUNDED_DECK_LLM_PROVIDER": "openai-compatible",
                "GROUNDED_DECK_LLM_MODEL": "gpt-4.1-mini",
                "GROUNDED_DECK_BASE_URL": "https://api.example.com/v1",
                "GROUNDED_DECK_API_KEY": "secret",
            }
        )

        self.assertIsInstance(provider, OpenAICompatibleProvider)
        self.assertEqual(provider.config.model, "gpt-4.1-mini")
        self.assertEqual(provider.config.base_url, "https://api.example.com/v1")

    def test_openai_compatible_provider_requires_base_url(self) -> None:
        with self.assertRaises(ValueError):
            build_provider_from_env(
                {
                    "GROUNDED_DECK_LLM_PROVIDER": "openai-compatible",
                    "GROUNDED_DECK_LLM_MODEL": "gpt-4.1-mini",
                    "GROUNDED_DECK_API_KEY": "secret",
                }
            )

    def test_openai_compatible_provider_builds_chat_request(self) -> None:
        provider = OpenAICompatibleProvider(
            ProviderConfig(
                provider="openai-compatible",
                model="gpt-4.1-mini",
                api_key_env="GROUNDED_DECK_API_KEY",
                base_url="https://api.example.com/v1",
            ),
            api_key="secret",
        )

        request = provider.build_chat_request(
            system_prompt="You are a planner.",
            user_prompt="Summarize the source pack.",
            response_format={"type": "json_object"},
        )

        self.assertEqual(request["url"], "https://api.example.com/v1/chat/completions")
        self.assertEqual(request["headers"]["Authorization"], "Bearer secret")
        self.assertEqual(request["json"]["model"], "gpt-4.1-mini")
        self.assertEqual(request["json"]["response_format"], {"type": "json_object"})
        self.assertEqual(len(request["json"]["messages"]), 2)

    def test_openai_compatible_provider_parses_json_content(self) -> None:
        provider = OpenAICompatibleProvider(
            ProviderConfig(
                provider="openai-compatible",
                model="gpt-4.1-mini",
                api_key_env="GROUNDED_DECK_API_KEY",
                base_url="https://api.example.com/v1",
            ),
            api_key="secret",
        )

        parsed = provider.parse_json_response(
            {
                "choices": [
                    {
                        "message": {
                            "content": '{"status":"pass","failures":[],"coverage":{"required_units":3,"covered_units":3}}'
                        }
                    }
                ]
            }
        )

        self.assertEqual(parsed["status"], "pass")
        self.assertEqual(parsed["coverage"]["covered_units"], 3)

    def test_openai_compatible_provider_can_draft_with_mock_transport(self) -> None:
        expected = load_json(SLIDE_SPEC_FIXTURE)

        def fake_transport(request: dict) -> dict:
            self.assertEqual(request["json"]["response_format"], {"type": "json_object"})
            self.assertIn("deck_goal", request["json"]["messages"][1]["content"])
            return {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(expected, ensure_ascii=False)
                        }
                    }
                ]
            }

        provider = OpenAICompatibleProvider(
            ProviderConfig(
                provider="openai-compatible",
                model="gpt-4.1-mini",
                api_key_env="GROUNDED_DECK_API_KEY",
                base_url="https://api.example.com/v1",
            ),
            api_key="secret",
            transport=fake_transport,
        )

        drafted = provider.draft_slide_spec(load_json(NORMALIZED_FIXTURE))
        self.assertEqual(drafted, expected)

    def test_openai_compatible_provider_rejects_invalid_slide_spec_shape(self) -> None:
        def fake_transport(_: dict) -> dict:
            return {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps({"deck_goal": "missing slides"}, ensure_ascii=False)
                        }
                    }
                ]
            }

        provider = OpenAICompatibleProvider(
            ProviderConfig(
                provider="openai-compatible",
                model="gpt-4.1-mini",
                api_key_env="GROUNDED_DECK_API_KEY",
                base_url="https://api.example.com/v1",
            ),
            api_key="secret",
            transport=fake_transport,
        )

        with self.assertRaises(ValueError):
            provider.draft_slide_spec(load_json(NORMALIZED_FIXTURE))

    def test_openai_compatible_provider_can_grade_with_mock_transport(self) -> None:
        expected = {
            "status": "pass",
            "failures": [],
            "coverage": {"required_units": 3, "covered_units": 3},
            "provider": "openai-compatible",
            "model": "gpt-4.1-mini",
        }

        def fake_transport(request: dict) -> dict:
            self.assertIn("slide_spec", request["json"]["messages"][1]["content"])
            return {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(expected, ensure_ascii=False)
                        }
                    }
                ]
            }

        provider = OpenAICompatibleProvider(
            ProviderConfig(
                provider="openai-compatible",
                model="gpt-4.1-mini",
                api_key_env="GROUNDED_DECK_API_KEY",
                base_url="https://api.example.com/v1",
            ),
            api_key="secret",
            transport=fake_transport,
        )

        report = provider.grade_slide_spec(
            load_json(NORMALIZED_FIXTURE),
            load_json(SLIDE_SPEC_FIXTURE),
        )
        self.assertEqual(report, expected)

    def test_openai_compatible_provider_rejects_invalid_quality_report_shape(self) -> None:
        def fake_transport(_: dict) -> dict:
            return {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps({"status": "pass"}, ensure_ascii=False)
                        }
                    }
                ]
            }

        provider = OpenAICompatibleProvider(
            ProviderConfig(
                provider="openai-compatible",
                model="gpt-4.1-mini",
                api_key_env="GROUNDED_DECK_API_KEY",
                base_url="https://api.example.com/v1",
            ),
            api_key="secret",
            transport=fake_transport,
        )

        with self.assertRaises(ValueError):
            provider.grade_slide_spec(
                load_json(NORMALIZED_FIXTURE),
                load_json(SLIDE_SPEC_FIXTURE),
            )

    def test_slide_spec_fixture_has_required_schema_fields(self) -> None:
        schema = load_json(SLIDE_SCHEMA)
        slide_spec = load_json(SLIDE_SPEC_FIXTURE)

        required_root = set(schema["required"])
        self.assertTrue(required_root.issubset(slide_spec.keys()))

        slide_required = set(schema["properties"]["slides"]["items"]["required"])
        for slide in slide_spec["slides"]:
            self.assertTrue(slide_required.issubset(slide.keys()), slide["slide_id"])

    def test_run_pipeline_returns_all_intermediate_outputs(self) -> None:
        result = run_pipeline(load_json(RAW_FIXTURE), provider=DeterministicProvider())

        self.assertEqual(result["normalized_pack"], load_json(NORMALIZED_FIXTURE))
        self.assertEqual(result["slide_spec"], load_json(SLIDE_SPEC_FIXTURE))
        self.assertEqual(result["quality_report"]["status"], "pass")
        self.assertEqual(result["provider"], "deterministic")

    def test_write_pipeline_outputs_writes_expected_files(self) -> None:
        result = run_pipeline(load_json(RAW_FIXTURE), provider=DeterministicProvider())
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            write_pipeline_outputs(output_dir, result)

            self.assertTrue((output_dir / "normalized-pack.json").exists())
            self.assertTrue((output_dir / "slide-spec.json").exists())
            self.assertTrue((output_dir / "quality-report.json").exists())

    def test_write_verification_summary_writes_metadata_file(self) -> None:
        result = run_pipeline(load_json(RAW_FIXTURE), provider=DeterministicProvider())
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            write_pipeline_outputs(output_dir, result)
            summary_path = write_verification_summary(
                output_dir=output_dir,
                result=result,
                mode="offline-example",
                input_path=RAW_FIXTURE,
            )

            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(summary["mode"], "offline-example")
            self.assertEqual(summary["provider"], "deterministic")
            self.assertEqual(summary["artifacts"]["slide_spec"], str(output_dir / "slide-spec.json"))


if __name__ == "__main__":
    unittest.main()
