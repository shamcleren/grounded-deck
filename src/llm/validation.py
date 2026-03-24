from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_slide_spec_like(payload: dict) -> None:
    schema = _load_json(ROOT / "schemas" / "slide-spec.schema.json")
    required_root = set(schema["required"])
    missing_root = sorted(required_root - set(payload.keys()))
    if missing_root:
        raise ValueError(f"slide spec missing required root fields: {', '.join(missing_root)}")

    if not isinstance(payload.get("slides"), list) or not payload["slides"]:
        raise ValueError("slide spec must include at least one slide")

    slide_required = set(schema["properties"]["slides"]["items"]["required"])
    for index, slide in enumerate(payload["slides"]):
        if not isinstance(slide, dict):
            raise ValueError(f"slide {index} is not an object")
        missing_slide = sorted(slide_required - set(slide.keys()))
        if missing_slide:
            raise ValueError(
                f"slide {index} missing required fields: {', '.join(missing_slide)}"
            )


def validate_quality_report_like(payload: dict) -> None:
    required_root = {"status", "failures", "coverage"}
    missing_root = sorted(required_root - set(payload.keys()))
    if missing_root:
        raise ValueError(f"quality report missing required fields: {', '.join(missing_root)}")

    if payload["status"] not in {"pass", "fail"}:
        raise ValueError("quality report status must be 'pass' or 'fail'")
    if not isinstance(payload["failures"], list):
        raise ValueError("quality report failures must be a list")
    if not isinstance(payload["coverage"], dict):
        raise ValueError("quality report coverage must be an object")

    coverage_required = {"required_units", "covered_units"}
    missing_coverage = sorted(coverage_required - set(payload["coverage"].keys()))
    if missing_coverage:
        raise ValueError(
            f"quality report coverage missing required fields: {', '.join(missing_coverage)}"
        )
