#!/usr/bin/env python3

from __future__ import annotations

import json
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


def validate_rubric(path: Path) -> CheckResult:
    if not path.exists():
        return CheckResult("rubric.json", False, f"missing file: {path}")

    try:
        rubric = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return CheckResult("rubric.json", False, f"invalid json: {exc}")

    criteria = rubric.get("criteria", [])
    if len(criteria) < 5:
        return CheckResult("rubric.json", False, "expected at least 5 criteria")
    return CheckResult("rubric.json", True, f"{len(criteria)} criteria present")


def validate_paths(paths: list[Path]) -> list[CheckResult]:
    results: list[CheckResult] = []
    for path in paths:
        exists = path.exists()
        results.append(
            CheckResult(path.name, exists, "present" if exists else f"missing path: {path}")
        )
    return results


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
        ROOT / "AGENTS.md",
        ROOT / "docs",
        ROOT / "harness",
        ROOT / "reports",
        ROOT / "schemas",
        ROOT / "src" / "ingest",
        ROOT / "src" / "planner",
        ROOT / "src" / "visual",
        ROOT / "src" / "renderer",
        ROOT / "src" / "quality",
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
            ROOT / "docs" / "ARCHITECTURE-DECISIONS.md",
            ["# Architecture Decisions", "## Fixed Invariants", "## Decision Log", "## Change Policy"],
        )
    )
    results.append(validate_schema(ROOT / "schemas" / "slide-spec.schema.json"))
    results.append(validate_rubric(ROOT / "harness" / "rubric.json"))
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
