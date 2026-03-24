from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.runtime.env import load_runtime_env
from src.runtime.verification import (
    archive_verification_summary,
    build_live_acceptance_snapshot,
    build_failure_summary,
    render_verification_report,
    render_live_verification_checklist,
    render_live_verification_status,
    validate_live_verification_env,
    write_live_verification_checklist,
)


ROOT = Path(__file__).resolve().parent.parent


class VerificationArtifactTests(unittest.TestCase):
    def test_load_runtime_env_reads_local_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".env.runtime.local"
            env_path.write_text(
                "GROUNDED_DECK_LLM_PROVIDER=openai-compatible\nGROUNDED_DECK_LLM_MODEL=gpt-4.1-mini\n",
                encoding="utf-8",
            )
            loaded = load_runtime_env(env_path)
            self.assertEqual(loaded["GROUNDED_DECK_LLM_PROVIDER"], "openai-compatible")
            self.assertEqual(loaded["GROUNDED_DECK_LLM_MODEL"], "gpt-4.1-mini")

    def test_validate_live_verification_env_reports_missing_values(self) -> None:
        ok, missing = validate_live_verification_env({})
        self.assertFalse(ok)
        self.assertIn("GROUNDED_DECK_LLM_PROVIDER", missing)
        self.assertIn("GROUNDED_DECK_LLM_MODEL", missing)
        self.assertIn("GROUNDED_DECK_BASE_URL", missing)
        self.assertIn("GROUNDED_DECK_API_KEY", missing)

    def test_validate_live_verification_env_passes_for_openai_compatible(self) -> None:
        ok, missing = validate_live_verification_env(
            {
                "GROUNDED_DECK_LLM_PROVIDER": "openai-compatible",
                "GROUNDED_DECK_LLM_MODEL": "gpt-4.1-mini",
                "GROUNDED_DECK_BASE_URL": "https://api.openai.com/v1",
                "GROUNDED_DECK_API_KEY": "secret",
            }
        )
        self.assertTrue(ok)
        self.assertEqual(missing, [])

    def test_validate_live_verification_env_rejects_placeholder_values(self) -> None:
        ok, missing = validate_live_verification_env(
            {
                "GROUNDED_DECK_LLM_PROVIDER": "openai-compatible",
                "GROUNDED_DECK_LLM_MODEL": "gpt-4.1-mini",
                "GROUNDED_DECK_BASE_URL": "https://api.openai.com/v1",
                "GROUNDED_DECK_API_KEY": "REPLACE_ME",
            }
        )
        self.assertFalse(ok)
        self.assertEqual(missing, ["GROUNDED_DECK_API_KEY"])

    def test_render_verification_report_contains_key_fields(self) -> None:
        summary = {
            "mode": "online-verification",
            "provider": "openai-compatible",
            "model": "gpt-4.1-mini",
            "input_path": "fixtures/source-packs/example-source-pack.json",
            "generated_at_unix": 1774252930,
            "artifacts": {
                "normalized_pack": "/tmp/grounded-deck-online/normalized-pack.json",
                "slide_spec": "/tmp/grounded-deck-online/slide-spec.json",
                "quality_report": "/tmp/grounded-deck-online/quality-report.json",
            },
            "quality_status": "pass",
        }

        report = render_verification_report(summary)

        self.assertIn("# Live Verification Report", report)
        self.assertIn("openai-compatible", report)
        self.assertIn("gpt-4.1-mini", report)
        self.assertIn("quality-report.json", report)

    def test_render_verification_report_includes_failure_reason_when_present(self) -> None:
        report = render_verification_report(
            {
                "mode": "online-verification",
                "provider": "openai-compatible",
                "model": "gpt-4.1-mini",
                "input_path": "fixtures/source-packs/example-source-pack.json",
                "generated_at_unix": 1774252930,
                "artifacts": {},
                "quality_status": "error",
                "error": "timeout contacting provider",
            }
        )
        self.assertIn("timeout contacting provider", report)

    def test_build_failure_summary_marks_error_status(self) -> None:
        summary = build_failure_summary(
            mode="online-verification",
            provider="openai-compatible",
            model="gpt-4.1-mini",
            input_path="fixtures/source-packs/example-source-pack.json",
            error="provider timeout",
        )
        self.assertEqual(summary["quality_status"], "error")
        self.assertEqual(summary["error"], "provider timeout")

    def test_render_live_verification_checklist_shows_blocked_state(self) -> None:
        checklist = render_live_verification_checklist({})
        self.assertIn("Status: `BLOCKED`", checklist)
        self.assertIn("GROUNDED_DECK_API_KEY", checklist)
        self.assertIn("Replace placeholder values", checklist)

    def test_write_live_verification_checklist_writes_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "live-verification-checklist.md"
            write_live_verification_checklist(output_path, {})
            self.assertTrue(output_path.exists())
            self.assertIn("Live Verification Checklist", output_path.read_text(encoding="utf-8"))

    def test_render_live_verification_status_without_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            summary_path = Path(tmpdir) / "missing-summary.json"
            status = render_live_verification_status(summary_path, {})
            self.assertIn("Environment Ready: `no`", status)
            self.assertIn("Summary Present: `no`", status)

    def test_render_live_verification_status_marks_placeholder_api_key_as_not_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            summary_path = Path(tmpdir) / "missing-summary.json"
            status = render_live_verification_status(
                summary_path,
                {
                    "GROUNDED_DECK_LLM_PROVIDER": "openai-compatible",
                    "GROUNDED_DECK_LLM_MODEL": "gpt-4.1-mini",
                    "GROUNDED_DECK_BASE_URL": "https://api.openai.com/v1",
                    "GROUNDED_DECK_API_KEY": "REPLACE_ME",
                },
            )
            self.assertIn("Environment Ready: `no`", status)
            self.assertIn("GROUNDED_DECK_API_KEY", status)

    def test_render_live_verification_status_with_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            summary_path = Path(tmpdir) / "verification-summary.json"
            summary_path.write_text(
                json.dumps(
                    {
                        "mode": "online-verification",
                        "provider": "openai-compatible",
                        "quality_status": "error",
                        "error": "timeout",
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            status = render_live_verification_status(
                summary_path,
                {
                    "GROUNDED_DECK_LLM_PROVIDER": "openai-compatible",
                    "GROUNDED_DECK_LLM_MODEL": "gpt-4.1-mini",
                    "GROUNDED_DECK_BASE_URL": "https://api.openai.com/v1",
                    "GROUNDED_DECK_API_KEY": "secret",
                },
            )
            self.assertIn("Environment Ready: `yes`", status)
            self.assertIn("Summary Present: `yes`", status)
            self.assertIn("Last Error: `timeout`", status)

    def test_archive_verification_summary_writes_json_and_markdown(self) -> None:
        summary = {
            "mode": "online-verification",
            "provider": "openai-compatible",
            "model": "gpt-4.1-mini",
            "input_path": "fixtures/source-packs/example-source-pack.json",
            "generated_at_unix": 1774252930,
            "artifacts": {
                "normalized_pack": "/tmp/grounded-deck-online/normalized-pack.json",
                "slide_spec": "/tmp/grounded-deck-online/slide-spec.json",
                "quality_report": "/tmp/grounded-deck-online/quality-report.json",
            },
            "quality_status": "pass",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            summary_path = Path(tmpdir) / "verification-summary.json"
            summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            output_dir = Path(tmpdir) / "reports"
            archive_verification_summary(summary_path, output_dir)

            archived_json = output_dir / "live-verification-latest.json"
            archived_md = output_dir / "live-verification-latest.md"

            self.assertTrue(archived_json.exists())
            self.assertTrue(archived_md.exists())
            self.assertEqual(json.loads(archived_json.read_text(encoding="utf-8"))["provider"], "openai-compatible")
            self.assertIn("Live Verification Report", archived_md.read_text(encoding="utf-8"))

    def test_archive_verification_summary_copies_live_artifacts_into_history(self) -> None:
        summary = {
            "mode": "online-verification",
            "provider": "openai-compatible",
            "model": "gpt-4.1-mini",
            "input_path": "fixtures/source-packs/example-source-pack.json",
            "generated_at_unix": 1774252930,
            "artifacts": {},
            "quality_status": "pass",
        }

        normalized_pack = {
            "deck_goal": "Recommend an example entry plan.",
            "audience": "Example strategy leaders",
            "source_units": [
                {
                    "unit_id": "src-01:sec-01",
                    "source_binding": "src-01:sec-01",
                }
            ],
        }
        slide_spec = {
            "slides": [
                {
                    "title": "Example Intro",
                    "layout_type": "summary",
                    "source_bindings": [],
                    "must_include_checks": [],
                },
                {
                    "title": "Example Timeline",
                    "layout_type": "timeline",
                    "source_bindings": ["src-01:sec-01"],
                    "must_include_checks": ["src-01:sec-01"],
                },
                {
                    "title": "Decision Backbone",
                    "layout_type": "summary",
                    "source_bindings": ["src-01:sec-01"],
                    "must_include_checks": [],
                },
            ]
        }
        quality_report = {
            "status": "pass",
            "coverage": {
                "covered_units_ids": ["src-01:sec-01"],
            },
            "grounding": {
                "grounded_slides": 2,
                "total_content_slides": 2,
            },
            "visual_form": {
                "matched_units_ids": ["src-01:sec-01"],
            },
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            normalized_path = tmp_path / "normalized-pack.json"
            slide_spec_path = tmp_path / "slide-spec.json"
            quality_report_path = tmp_path / "quality-report.json"
            normalized_path.write_text(json.dumps(normalized_pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            slide_spec_path.write_text(json.dumps(slide_spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            quality_report_path.write_text(json.dumps(quality_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            summary["artifacts"] = {
                "normalized_pack": str(normalized_path),
                "slide_spec": str(slide_spec_path),
                "quality_report": str(quality_report_path),
            }

            summary_path = tmp_path / "verification-summary.json"
            summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            output_dir = tmp_path / "reports"
            archived_json, _ = archive_verification_summary(summary_path, output_dir)

            archived_summary = json.loads(archived_json.read_text(encoding="utf-8"))
            history_dir = output_dir / "live-verification-history" / "example-1774252930"

            self.assertEqual(
                archived_summary["artifacts"]["slide_spec"],
                str(history_dir / "slide-spec.json"),
            )
            self.assertTrue((history_dir / "verification-summary.json").exists())
            self.assertTrue((history_dir / "verification-report.md").exists())
            self.assertTrue((history_dir / "acceptance-summary.json").exists())

            acceptance_summary = json.loads((history_dir / "acceptance-summary.json").read_text(encoding="utf-8"))
            self.assertEqual(acceptance_summary["unit_layouts"], {"src-01:sec-01": "timeline"})
            self.assertEqual(acceptance_summary["decision_backbone"]["title"], "Decision Backbone")

    def test_archive_verification_summary_preserves_failure_details(self) -> None:
        summary = {
            "mode": "online-verification",
            "provider": "openai-compatible",
            "model": "gpt-4.1-mini",
            "input_path": "fixtures/source-packs/example-source-pack.json",
            "generated_at_unix": 1774252930,
            "artifacts": {},
            "quality_status": "error",
            "error": "provider timeout",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            summary_path = Path(tmpdir) / "verification-summary.json"
            summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            output_dir = Path(tmpdir) / "reports"
            archived_json, archived_md = archive_verification_summary(summary_path, output_dir)

            self.assertEqual(json.loads(archived_json.read_text(encoding="utf-8"))["quality_status"], "error")
            self.assertIn("provider timeout", archived_md.read_text(encoding="utf-8"))

    def test_archive_verification_summary_requires_existing_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "reports"
            with self.assertRaises(FileNotFoundError):
                archive_verification_summary(Path(tmpdir) / "missing.json", output_dir)

    def test_committed_strongest_demo_acceptance_summary_matches_archived_artifacts(self) -> None:
        history_dir = ROOT / "reports" / "live-verification-history" / "strongest-demo-1774370225"
        archived_summary = json.loads((history_dir / "verification-summary.json").read_text(encoding="utf-8"))
        expected = json.loads((history_dir / "acceptance-summary.json").read_text(encoding="utf-8"))

        rebuilt = build_live_acceptance_snapshot(
            archived_summary,
            normalized_pack_path=history_dir / "normalized-pack.json",
            slide_spec_path=history_dir / "slide-spec.json",
            quality_report_path=history_dir / "quality-report.json",
        )

        self.assertEqual(rebuilt, expected)


if __name__ == "__main__":
    unittest.main()
