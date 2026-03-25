#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "reports" / "self-acceptance-latest.md"


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str


def file_contains(path: Path, fragments: list[str]) -> CheckResult:
    if not path.exists():
        return CheckResult(path.name, False, f"missing file: {path}")

    text = path.read_text(encoding="utf-8")
    missing = [fragment for fragment in fragments if fragment not in text]
    if missing:
        return CheckResult(path.name, False, f"missing fragments: {', '.join(missing)}")
    return CheckResult(path.name, True, "required fragments present")


def validate_schema(path: Path) -> CheckResult:
    if not path.exists():
        return CheckResult("slide-spec.schema.json", False, f"missing file: {path}")

    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return CheckResult("slide-spec.schema.json", False, f"invalid json: {exc}")

    required_root = {"deck_goal", "audience", "slides"}
    root_required = set(schema.get("required", []))
    missing_root = sorted(required_root - root_required)
    slides = schema.get("properties", {}).get("slides", {})
    slide_required = set(
        slides.get("items", {}).get("required", [])
    )
    expected_slide_required = {
        "slide_id",
        "title",
        "goal",
        "layout_type",
        "key_points",
        "visual_elements",
        "source_bindings",
        "must_include_checks",
    }
    missing_slide = sorted(expected_slide_required - slide_required)

    problems = []
    if missing_root:
        problems.append(f"missing root required: {', '.join(missing_root)}")
    if missing_slide:
        problems.append(f"missing slide required: {', '.join(missing_slide)}")

    if problems:
        return CheckResult("slide-spec.schema.json", False, "; ".join(problems))
    return CheckResult("slide-spec.schema.json", True, "schema contains required fields")


def validate_normalized_schema(path: Path) -> CheckResult:
    if not path.exists():
        return CheckResult("normalized-source-units.schema.json", False, f"missing file: {path}")

    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return CheckResult("normalized-source-units.schema.json", False, f"invalid json: {exc}")

    required_root = {"pack_id", "deck_goal", "audience", "source_units"}
    root_required = set(schema.get("required", []))
    missing_root = sorted(required_root - root_required)
    unit_required = set(
        schema.get("properties", {}).get("source_units", {}).get("items", {}).get("required", [])
    )
    expected_unit_required = {
        "unit_id",
        "source_id",
        "source_title",
        "section_id",
        "section_heading",
        "unit_kind",
        "language",
        "text",
        "claims",
        "source_binding",
    }
    missing_unit = sorted(expected_unit_required - unit_required)

    problems = []
    if missing_root:
        problems.append(f"missing root required: {', '.join(missing_root)}")
    if missing_unit:
        problems.append(f"missing unit required: {', '.join(missing_unit)}")

    if problems:
        return CheckResult("normalized-source-units.schema.json", False, "; ".join(problems))
    return CheckResult(
        "normalized-source-units.schema.json",
        True,
        "schema contains required normalized source-unit fields",
    )


def validate_rubric(path: Path) -> CheckResult:
    if not path.exists():
        return CheckResult("rubric.json", False, f"missing file: {path}")

    try:
        rubric = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return CheckResult("rubric.json", False, f"invalid json: {exc}")

    criteria = rubric.get("criteria", [])
    if len(criteria) < 7:
        return CheckResult("rubric.json", False, "expected at least 7 criteria")
    return CheckResult("rubric.json", True, f"{len(criteria)} criteria present")


def validate_paths(paths: list[Path]) -> list[CheckResult]:
    results: list[CheckResult] = []
    for path in paths:
        exists = path.exists()
        results.append(
            CheckResult(path.name, exists, "present" if exists else f"missing path: {path}")
        )
    return results


def run_unittest_discovery(start_dir: Path) -> CheckResult:
    command = [sys.executable, "-m", "unittest", "discover", "-s", str(start_dir)]
    proc = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        detail = proc.stdout.strip() or proc.stderr.strip() or "unittest failed"
        return CheckResult("tests", False, detail)
    return CheckResult("tests", True, "unittest discovery passed")


def run_artifact_grading() -> CheckResult:
    """渲染 strongest-demo PPTX 并执行 artifact grading。"""
    try:
        import sys
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))

        from src.ingest.normalize import normalize_source_pack
        from src.llm.provider import DeterministicProvider
        from src.renderer.artifact_grader import grade_pptx_artifact
        from src.renderer.pptx_renderer import render_slide_spec_to_pptx

        source_path = ROOT / "fixtures" / "source-packs" / "strongest-demo-source-pack.json"
        if not source_path.exists():
            return CheckResult("artifact-grading", False, "strongest-demo-source-pack.json not found")

        raw = json.loads(source_path.read_text(encoding="utf-8"))
        provider = DeterministicProvider()
        norm = normalize_source_pack(raw)
        spec = provider.draft_slide_spec(norm)

        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            pptx_path = Path(tmpdir) / "eval-test.pptx"
            render_slide_spec_to_pptx(spec, pptx_path)
            report = grade_pptx_artifact(pptx_path, slide_spec=spec)

        if report["status"] != "pass":
            return CheckResult(
                "artifact-grading",
                False,
                f"artifact grade failed: {report['failures']}",
            )

        metrics = report["metrics"]
        problems = []
        if metrics.get("editability_ratio", 0) < 1.0:
            problems.append(f"editability_ratio={metrics['editability_ratio']}")
        if metrics.get("notes_coverage_ratio", 0) < 0.8:
            problems.append(f"notes_coverage_ratio={metrics['notes_coverage_ratio']}")
        if not metrics.get("chinese_text_found"):
            problems.append("chinese_text_found=false")
        if metrics.get("slide_count", 0) != len(spec.get("slides", [])):
            problems.append(f"slide_count mismatch: {metrics['slide_count']} vs {len(spec['slides'])}")

        if problems:
            return CheckResult("artifact-grading", False, f"artifact quality issues: {'; '.join(problems)}")

        return CheckResult(
            "artifact-grading",
            True,
            f"PPTX artifact grade pass — "
            f"{metrics['slide_count']} slides, "
            f"{metrics['editable_text_boxes']} editable text boxes, "
            f"editability={metrics['editability_ratio']}, "
            f"notes={metrics['notes_coverage_ratio']}, "
            f"source_bindings={metrics['source_binding_coverage_ratio']}",
        )
    except Exception as exc:
        return CheckResult("artifact-grading", False, f"artifact grading error: {exc}")


def run_continuity_grading() -> CheckResult:
    """对仓库的 continuity artifacts 执行质量评估。"""
    try:
        import sys
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))

        from src.quality.continuity_grader import grade_continuity_artifacts

        report = grade_continuity_artifacts(ROOT)

        if report.status != "pass":
            error_details = "; ".join(
                f"{i.name}: {i.detail}" for i in report.error_items
            )
            return CheckResult(
                "continuity-grading",
                False,
                f"continuity grade failed: {error_details}",
            )

        warning_count = report.warnings
        return CheckResult(
            "continuity-grading",
            True,
            f"continuity grade pass — "
            f"{report.passed}/{report.total} checks passed"
            f"{f', {warning_count} warnings' if warning_count else ''}",
        )
    except Exception as exc:
        return CheckResult("continuity-grading", False, f"continuity grading error: {exc}")


def run_acceptance_baseline_check() -> CheckResult:
    """验证已接受的 strongest-demo acceptance baseline 可以被加载并与自身一致。"""
    try:
        import sys
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))

        from src.runtime.verification import (
            ACCEPTED_STRONGEST_DEMO_BASELINE,
            compare_against_accepted_baseline,
        )

        if not ACCEPTED_STRONGEST_DEMO_BASELINE.exists():
            return CheckResult(
                "acceptance-baseline",
                False,
                f"accepted baseline not found: {ACCEPTED_STRONGEST_DEMO_BASELINE}",
            )

        # 验证基线可以被加载为有效 JSON
        baseline = json.loads(ACCEPTED_STRONGEST_DEMO_BASELINE.read_text(encoding="utf-8"))

        # 验证基线包含必需的结构字段
        required_fields = [
            "slide_count", "layout_sequence", "intro_slide",
            "unit_layouts", "covered_unit_ids", "quality_status",
        ]
        missing = [f for f in required_fields if f not in baseline]
        if missing:
            return CheckResult(
                "acceptance-baseline",
                False,
                f"baseline missing required fields: {', '.join(missing)}",
            )

        # 验证基线与自身比较结果为 match（自洽性检查）
        delta = compare_against_accepted_baseline(ACCEPTED_STRONGEST_DEMO_BASELINE)
        if delta["status"] != "match":
            return CheckResult(
                "acceptance-baseline",
                False,
                f"baseline self-comparison failed: {delta.get('error') or delta.get('differences')}",
            )

        # 检查从已接受基线开始的归档 acceptance summaries 是否与基线一致
        baseline_timestamp = baseline.get("generated_at_unix", 0)
        history_dir = ACCEPTED_STRONGEST_DEMO_BASELINE.parent.parent
        drift_snapshots: list[str] = []
        if history_dir.exists():
            for snapshot_dir in sorted(history_dir.iterdir()):
                candidate = snapshot_dir / "acceptance-summary.json"
                if candidate.exists() and candidate != ACCEPTED_STRONGEST_DEMO_BASELINE:
                    candidate_data = json.loads(candidate.read_text(encoding="utf-8"))
                    # 只检查与基线同时代或更新的快照
                    if candidate_data.get("generated_at_unix", 0) < baseline_timestamp:
                        continue
                    # 跳过失败的快照
                    if candidate_data.get("quality_status") != "pass":
                        continue
                    d = compare_against_accepted_baseline(candidate)
                    if d["status"] == "drift":
                        drift_snapshots.append(snapshot_dir.name)

        if drift_snapshots:
            return CheckResult(
                "acceptance-baseline",
                True,  # warning 级别，不阻塞
                f"acceptance baseline valid — "
                f"{len(drift_snapshots)} archived snapshot(s) have drift: {', '.join(drift_snapshots)}",
            )

        return CheckResult(
            "acceptance-baseline",
            True,
            f"acceptance baseline valid — "
            f"slide_count={baseline['slide_count']}, "
            f"quality_status={baseline['quality_status']}, "
            f"layout_sequence={baseline['layout_sequence']}",
        )
    except Exception as exc:
        return CheckResult("acceptance-baseline", False, f"acceptance baseline error: {exc}")


def run_narrative_grading() -> CheckResult:
    """对 strongest-demo slide spec 执行叙事质量评分。"""
    try:
        import sys
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))

        from src.ingest.normalize import normalize_source_pack
        from src.quality.narrative_grader import grade_narrative_deterministic

        source_path = ROOT / "fixtures" / "source-packs" / "strongest-demo-source-pack.json"
        if not source_path.exists():
            return CheckResult("narrative-grading", False, "strongest-demo-source-pack.json not found")

        raw = json.loads(source_path.read_text(encoding="utf-8"))
        norm = normalize_source_pack(raw)

        from src.llm.provider import DeterministicProvider
        provider = DeterministicProvider()
        spec = provider.draft_slide_spec(norm)

        report = grade_narrative_deterministic(norm, spec)

        if report.status != "pass":
            return CheckResult(
                "narrative-grading",
                False,
                f"narrative grade failed: {report.all_issues}",
            )

        if report.avg_composite < 0.7:
            return CheckResult(
                "narrative-grading",
                False,
                f"narrative avg_composite {report.avg_composite} < 0.7",
            )

        return CheckResult(
            "narrative-grading",
            True,
            f"narrative grade pass — "
            f"{report.slide_count} slides, "
            f"coherence={report.avg_coherence}, "
            f"grounding={report.avg_grounding}, "
            f"visual_fit={report.avg_visual_fit}, "
            f"composite={report.avg_composite}",
        )
    except Exception as exc:
        return CheckResult("narrative-grading", False, f"narrative grading error: {exc}")


def render_report(results: list[CheckResult]) -> str:
    passed = sum(1 for result in results if result.ok)
    total = len(results)
    status = "PASS" if passed == total else "FAIL"

    lines = [
        "# Self-Acceptance Report",
        "",
        f"- Status: **{status}**",
        f"- Passed: **{passed}/{total}**",
        "",
        "## Checks",
        "",
    ]

    for result in results:
        mark = "PASS" if result.ok else "FAIL"
        lines.append(f"- {mark} `{result.name}`: {result.detail}")

    lines.append("")
    lines.append("## Next Action")
    lines.append("")
    if status == "PASS":
        lines.append("- Scaffold is internally consistent and ready for implementation work.")
    else:
        lines.append("- Fix failed checks before adding implementation code.")

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    required_paths = [
        ROOT / "START-HERE.md",
        ROOT / "AGENTS.md",
        ROOT / "docs",
        ROOT / "harness",
        ROOT / "reports",
        ROOT / "schemas",
        ROOT / "fixtures",
        ROOT / "fixtures" / "source-packs",
        ROOT / "fixtures" / "normalized-source-units",
        ROOT / "fixtures" / "slide-spec",
        ROOT / "fixtures" / "quality-reports",
        ROOT / "src" / "ingest",
        ROOT / "src" / "planner",
        ROOT / "src" / "visual",
        ROOT / "src" / "renderer",
        ROOT / "src" / "quality",
        ROOT / "tests",
        ROOT / ".claude" / "evals",
    ]

    results: list[CheckResult] = []
    results.extend(validate_paths(required_paths))
    results.append(
        file_contains(
            ROOT / "README.md",
            ["# GroundedDeck", "## AI Continuity", "## Repository Layout", "## Self-Acceptance"],
        )
    )
    results.append(
        file_contains(
            ROOT / "START-HERE.md",
            ["# Start Here", "## 30-Second Startup", "## What To Do Next", "## Before Ending a Session"],
        )
    )
    results.append(
        file_contains(
            ROOT / "AGENTS.md",
            ["# AGENTS", "## Required Read Order", "## Operating Contract", "## Completion Protocol"],
        )
    )
    results.append(
        file_contains(
            ROOT / "docs" / "vision.md",
            ["# Product Vision", "## Quality Bar", "## Differentiators", "## Non-Goals"],
        )
    )
    results.append(
        file_contains(
            ROOT / "docs" / "architecture.md",
            ["# Architecture", "## System Layers", "## Data Flow", "## Guardrails"],
        )
    )
    results.append(
        file_contains(
            ROOT / "docs" / "STRONGEST-DEMO.md",
            ["# Strongest Demo", "## Selected Demo Case", "## Artifact Bundle", "## Success Metrics"],
        )
    )
    results.append(
        file_contains(
            ROOT / "docs" / "evaluation-plan.md",
            ["# Evaluation Plan", "## Capability Evals", "## Regression Evals", "## Next Stage"],
        )
    )
    results.append(
        file_contains(
            ROOT / "docs" / "PROJECT-STATE.md",
            ["# Project State", "## Current Phase", "## Current Next Action", "## Definition of Done for Phase One"],
        )
    )
    results.append(
        file_contains(
            ROOT / "docs" / "LATEST-HANDOFF.md",
            ["# Latest Handoff", "## What Was Just Completed", "## Immediate Next Action", "## Resume Hint"],
        )
    )
    results.append(
        file_contains(
            ROOT / "docs" / "TASK-BOARD.md",
            ["# Task Board", "## In Progress", "## Ready Next", "## Update Rule"],
        )
    )
    results.append(
        file_contains(
            ROOT / "docs" / "ARCHITECTURE-DECISIONS.md",
            ["# Architecture Decisions", "## Fixed Invariants", "## Decision Log", "## Change Policy"],
        )
    )
    results.append(validate_schema(ROOT / "schemas" / "slide-spec.schema.json"))
    results.append(validate_normalized_schema(ROOT / "schemas" / "normalized-source-units.schema.json"))
    results.append(validate_rubric(ROOT / "harness" / "rubric.json"))
    results.append(run_unittest_discovery(ROOT / "tests"))
    results.append(run_artifact_grading())
    results.append(run_narrative_grading())
    results.append(run_continuity_grading())
    results.append(run_acceptance_baseline_check())
    results.append(
        file_contains(
            ROOT / ".claude" / "evals" / "grounded-deck-foundation.md",
            ["### Capability Evals", "### Regression Evals", "reports/self-acceptance-latest.md"],
        )
    )

    report = render_report(results)
    REPORT.write_text(report, encoding="utf-8")
    print(report)
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    sys.exit(main())
