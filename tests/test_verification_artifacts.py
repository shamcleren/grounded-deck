from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.runtime.env import load_runtime_env
from src.runtime.verification import (
    ACCEPTED_STRONGEST_DEMO_BASELINE,
    archive_verification_summary,
    build_live_acceptance_snapshot,
    build_failure_summary,
    compare_acceptance_summaries,
    compare_against_accepted_baseline,
    render_acceptance_delta_report,
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

    def test_latest_strongest_demo_refresh_matches_accepted_baseline_except_timestamp(self) -> None:
        accepted = json.loads(
            (
                ROOT
                / "reports"
                / "live-verification-history"
                / "strongest-demo-1774370225"
                / "acceptance-summary.json"
            ).read_text(encoding="utf-8")
        )
        latest_refresh = json.loads(
            (
                ROOT
                / "reports"
                / "live-verification-history"
                / "strongest-demo-1774374429"
                / "acceptance-summary.json"
            ).read_text(encoding="utf-8")
        )

        self.assertEqual(compare_acceptance_summaries(accepted, latest_refresh), [])

    def test_compare_acceptance_summaries_reports_non_timestamp_deltas(self) -> None:
        baseline = {
            "generated_at_unix": 1,
            "slide_count": 6,
            "intro_slide": {"title": "Baseline"},
        }
        candidate = {
            "generated_at_unix": 2,
            "slide_count": 5,
            "intro_slide": {"title": "Changed"},
        }

        differences = compare_acceptance_summaries(baseline, candidate)

        self.assertEqual(
            differences,
            [
                "acceptance_summary.intro_slide.title: baseline='Baseline' candidate='Changed'",
                "acceptance_summary.slide_count: baseline=6 candidate=5",
            ],
        )

    def test_build_live_acceptance_snapshot_tracks_unit_evidence_and_decision_checks(self) -> None:
        history_dir = ROOT / "reports" / "live-verification-history" / "strongest-demo-1774370225"
        archived_summary = json.loads((history_dir / "verification-summary.json").read_text(encoding="utf-8"))

        rebuilt = build_live_acceptance_snapshot(
            archived_summary,
            normalized_pack_path=history_dir / "normalized-pack.json",
            slide_spec_path=history_dir / "slide-spec.json",
            quality_report_path=history_dir / "quality-report.json",
        )

        self.assertEqual(
            rebuilt["unit_slide_evidence"]["src-01:sec-01"],
            {
                "source_bindings": ["src-01:sec-01"],
                "must_include_checks": ["src-01:sec-01"],
            },
        )
        self.assertEqual(rebuilt["decision_backbone"]["must_include_checks"], [])


class AcceptanceBaselineComparisonTests(unittest.TestCase):
    """Acceptance baseline 比较功能测试。"""

    def test_accepted_baseline_exists(self) -> None:
        """已接受的基线文件必须存在。"""
        self.assertTrue(
            ACCEPTED_STRONGEST_DEMO_BASELINE.exists(),
            f"accepted baseline not found: {ACCEPTED_STRONGEST_DEMO_BASELINE}",
        )

    def test_accepted_baseline_is_valid_json(self) -> None:
        """已接受的基线必须是有效的 JSON。"""
        data = json.loads(ACCEPTED_STRONGEST_DEMO_BASELINE.read_text(encoding="utf-8"))
        self.assertIsInstance(data, dict)

    def test_accepted_baseline_has_required_fields(self) -> None:
        """已接受的基线必须包含必需的结构字段。"""
        data = json.loads(ACCEPTED_STRONGEST_DEMO_BASELINE.read_text(encoding="utf-8"))
        required_fields = [
            "slide_count", "layout_sequence", "intro_slide",
            "unit_layouts", "covered_unit_ids", "quality_status",
        ]
        for field in required_fields:
            self.assertIn(field, data, f"baseline missing field: {field}")

    def test_compare_against_accepted_baseline_self_match(self) -> None:
        """基线与自身比较应该返回 match。"""
        delta = compare_against_accepted_baseline(ACCEPTED_STRONGEST_DEMO_BASELINE)
        self.assertEqual(delta["status"], "match")
        self.assertEqual(delta["differences"], [])

    def test_compare_against_accepted_baseline_with_drift(self) -> None:
        """与基线不一致的候选应该返回 drift。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            candidate_path = Path(tmpdir) / "candidate.json"
            candidate_data = json.loads(
                ACCEPTED_STRONGEST_DEMO_BASELINE.read_text(encoding="utf-8")
            )
            candidate_data["slide_count"] = 999  # 故意修改
            candidate_path.write_text(
                json.dumps(candidate_data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            delta = compare_against_accepted_baseline(candidate_path)
            self.assertEqual(delta["status"], "drift")
            self.assertTrue(len(delta["differences"]) > 0)

    def test_compare_against_accepted_baseline_timestamp_only_is_match(self) -> None:
        """仅 generated_at_unix 不同应该返回 match。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            candidate_path = Path(tmpdir) / "candidate.json"
            candidate_data = json.loads(
                ACCEPTED_STRONGEST_DEMO_BASELINE.read_text(encoding="utf-8")
            )
            candidate_data["generated_at_unix"] = 9999999999  # 仅修改时间戳
            candidate_path.write_text(
                json.dumps(candidate_data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            delta = compare_against_accepted_baseline(candidate_path)
            self.assertEqual(delta["status"], "match")

    def test_compare_against_missing_candidate_returns_error(self) -> None:
        """候选文件不存在应该返回 error。"""
        delta = compare_against_accepted_baseline(Path("/nonexistent/file.json"))
        self.assertEqual(delta["status"], "error")
        self.assertIn("not found", delta["error"])

    def test_compare_against_missing_baseline_returns_error(self) -> None:
        """基线文件不存在应该返回 error。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            candidate_path = Path(tmpdir) / "candidate.json"
            candidate_path.write_text("{}", encoding="utf-8")
            delta = compare_against_accepted_baseline(
                candidate_path,
                baseline_path=Path("/nonexistent/baseline.json"),
            )
            self.assertEqual(delta["status"], "error")
            self.assertIn("baseline not found", delta["error"])

    def test_render_acceptance_delta_report_match(self) -> None:
        """渲染 match 状态的 delta 报告。"""
        delta = {
            "status": "match",
            "baseline_path": "/path/to/baseline.json",
            "candidate_path": "/path/to/candidate.json",
            "differences": [],
            "error": None,
        }
        report = render_acceptance_delta_report(delta)
        self.assertIn("# Acceptance Delta Report", report)
        self.assertIn("match", report)
        self.assertIn("matches the accepted baseline", report)

    def test_render_acceptance_delta_report_drift(self) -> None:
        """渲染 drift 状态的 delta 报告。"""
        delta = {
            "status": "drift",
            "baseline_path": "/path/to/baseline.json",
            "candidate_path": "/path/to/candidate.json",
            "differences": ["slide_count: baseline=6 candidate=5"],
            "error": None,
        }
        report = render_acceptance_delta_report(delta)
        self.assertIn("drift", report)
        self.assertIn("## Differences", report)
        self.assertIn("slide_count", report)

    def test_render_acceptance_delta_report_error(self) -> None:
        """渲染 error 状态的 delta 报告。"""
        delta = {
            "status": "error",
            "baseline_path": "/path/to/baseline.json",
            "candidate_path": "/path/to/candidate.json",
            "differences": [],
            "error": "file not found",
        }
        report = render_acceptance_delta_report(delta)
        self.assertIn("error", report)
        self.assertIn("## Error", report)
        self.assertIn("file not found", report)

    def test_all_archived_snapshots_match_accepted_baseline(self) -> None:
        """从已接受基线开始的所有通过的归档 acceptance summaries 应该与基线一致（仅 generated_at_unix 可以不同）。

        注意：
        - 早期快照（1774370225 之前）可能缺少后来添加的字段（如 unit_slide_evidence），因此跳过。
        - 失败的快照（quality_status != "pass"）本身就不应该与基线一致，因此跳过。
        """
        history_dir = ACCEPTED_STRONGEST_DEMO_BASELINE.parent.parent
        self.assertTrue(history_dir.exists())

        baseline_data = json.loads(
            ACCEPTED_STRONGEST_DEMO_BASELINE.read_text(encoding="utf-8")
        )
        # 获取已接受基线的时间戳作为起始点
        baseline_timestamp = baseline_data.get("generated_at_unix", 0)

        for snapshot_dir in sorted(history_dir.iterdir()):
            candidate = snapshot_dir / "acceptance-summary.json"
            if not candidate.exists():
                continue
            candidate_data = json.loads(candidate.read_text(encoding="utf-8"))
            # 只检查与基线同时代或更新的快照
            candidate_timestamp = candidate_data.get("generated_at_unix", 0)
            if candidate_timestamp < baseline_timestamp:
                continue
            # 跳过失败的快照
            if candidate_data.get("quality_status") != "pass":
                continue
            differences = compare_acceptance_summaries(baseline_data, candidate_data)
            self.assertEqual(
                differences,
                [],
                f"snapshot {snapshot_dir.name} has drift from accepted baseline: {differences}",
            )


if __name__ == "__main__":
    unittest.main()
