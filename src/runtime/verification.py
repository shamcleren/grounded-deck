from __future__ import annotations

import json
import os
from pathlib import Path
from shutil import copy2
from time import time

from src.runtime.env import load_runtime_env


PLACEHOLDER_VALUES = {
    "",
    "REPLACE_ME",
    "YOUR_KEY",
    "YOUR_API_KEY",
    "YOUR_MODEL",
    "https://example.com/v1",
}


def _strip_acceptance_summary_keys(value: object, ignored_keys: set[str]) -> object:
    if isinstance(value, dict):
        return {
            key: _strip_acceptance_summary_keys(item, ignored_keys)
            for key, item in value.items()
            if key not in ignored_keys
        }
    if isinstance(value, list):
        return [_strip_acceptance_summary_keys(item, ignored_keys) for item in value]
    return value


def compare_acceptance_summaries(
    baseline: dict,
    candidate: dict,
    *,
    ignored_keys: set[str] | None = None,
) -> list[str]:
    ignored = {"generated_at_unix"} if ignored_keys is None else set(ignored_keys)

    normalized_baseline = _strip_acceptance_summary_keys(baseline, ignored)
    normalized_candidate = _strip_acceptance_summary_keys(candidate, ignored)
    if normalized_baseline == normalized_candidate:
        return []

    differences: list[str] = []

    def _walk(path: str, left: object, right: object) -> None:
        if type(left) is not type(right):
            differences.append(
                f"{path}: type mismatch baseline={type(left).__name__} candidate={type(right).__name__}"
            )
            return
        if isinstance(left, dict):
            left_keys = set(left.keys())
            right_keys = set(right.keys())
            for missing in sorted(left_keys - right_keys):
                differences.append(f"{path}.{missing}: missing from candidate")
            for added in sorted(right_keys - left_keys):
                differences.append(f"{path}.{added}: unexpected in candidate")
            for key in sorted(left_keys & right_keys):
                _walk(f"{path}.{key}", left[key], right[key])
            return
        if isinstance(left, list):
            if len(left) != len(right):
                differences.append(f"{path}: length mismatch baseline={len(left)} candidate={len(right)}")
                return
            for index, (left_item, right_item) in enumerate(zip(left, right)):
                _walk(f"{path}[{index}]", left_item, right_item)
            return
        if left != right:
            differences.append(f"{path}: baseline={left!r} candidate={right!r}")

    _walk("acceptance_summary", normalized_baseline, normalized_candidate)
    return differences


def render_verification_report(summary: dict) -> str:
    lines = [
        "# Live Verification Report",
        "",
        f'- Mode: `{summary["mode"]}`',
        f'- Provider: `{summary["provider"]}`',
        f'- Model: `{summary["model"]}`',
        f'- Quality Status: `{summary["quality_status"]}`',
        f'- Input: `{summary["input_path"]}`',
        "",
        "## Artifacts",
        "",
        f'- Normalized Pack: `{summary.get("artifacts", {}).get("normalized_pack", "n/a")}`',
        f'- Slide Spec: `{summary.get("artifacts", {}).get("slide_spec", "n/a")}`',
        f'- Quality Report: `{summary.get("artifacts", {}).get("quality_report", "n/a")}`',
        "",
    ]
    if summary.get("error"):
        lines.extend(
            [
                "## Error",
                "",
                summary["error"],
                "",
            ]
        )
    return "\n".join(lines)


def build_failure_summary(
    *,
    mode: str,
    provider: str,
    model: str,
    input_path: str,
    error: str,
) -> dict:
    return {
        "mode": mode,
        "provider": provider,
        "model": model,
        "input_path": input_path,
        "generated_at_unix": int(time()),
        "artifacts": {},
        "quality_status": "error",
        "error": error,
    }


def build_live_acceptance_snapshot(
    summary: dict,
    *,
    normalized_pack_path: Path,
    slide_spec_path: Path,
    quality_report_path: Path,
) -> dict:
    normalized_pack = json.loads(normalized_pack_path.read_text(encoding="utf-8"))
    slide_spec = json.loads(slide_spec_path.read_text(encoding="utf-8"))
    quality_report = json.loads(quality_report_path.read_text(encoding="utf-8"))

    slides = slide_spec.get("slides", [])
    intro_slide = slides[0] if slides else {}

    covered_unit_ids = quality_report.get("coverage", {}).get("covered_units_ids") or [
        unit["unit_id"] for unit in normalized_pack.get("source_units", [])
    ]
    unit_layouts: dict[str, str] = {}
    unit_slide_titles: dict[str, str] = {}
    unit_slide_evidence: dict[str, dict[str, list[str]]] = {}
    decision_backbone = {}

    for slide in slides:
        checks = slide.get("must_include_checks", [])
        if len(checks) == 1:
            unit_id = checks[0]
            unit_layouts[unit_id] = slide.get("layout_type", "unknown")
            unit_slide_titles[unit_id] = slide.get("title", "")
            unit_slide_evidence[unit_id] = {
                "source_bindings": slide.get("source_bindings", []),
                "must_include_checks": checks,
            }
        if (
            slide.get("layout_type") == "summary"
            and not checks
            and slide.get("source_bindings")
            and set(slide["source_bindings"]) == set(covered_unit_ids)
        ):
            decision_backbone = {
                "title": slide.get("title", ""),
                "layout_type": slide.get("layout_type", "unknown"),
                "source_bindings": slide.get("source_bindings", []),
                "must_include_checks": slide.get("must_include_checks", []),
            }

    return {
        "mode": summary.get("mode", "unknown"),
        "provider": summary.get("provider", "unknown"),
        "model": summary.get("model", "unknown"),
        "input_path": summary.get("input_path", "unknown"),
        "generated_at_unix": summary.get("generated_at_unix"),
        "quality_status": quality_report.get("status", summary.get("quality_status", "unknown")),
        "slide_count": len(slides),
        "layout_sequence": [slide.get("layout_type", "unknown") for slide in slides],
        "intro_slide": {
            "title": intro_slide.get("title", ""),
            "layout_type": intro_slide.get("layout_type", "unknown"),
            "source_bindings": intro_slide.get("source_bindings", []),
            "must_include_checks": intro_slide.get("must_include_checks", []),
        },
        "unit_layouts": unit_layouts,
        "unit_slide_titles": unit_slide_titles,
        "unit_slide_evidence": unit_slide_evidence,
        "decision_backbone": decision_backbone,
        "covered_unit_ids": covered_unit_ids,
        "grounded_content_slides": quality_report.get("grounding", {}).get("grounded_slides"),
        "total_content_slides": quality_report.get("grounding", {}).get("total_content_slides"),
        "visual_matched_unit_ids": quality_report.get("visual_form", {}).get("matched_units_ids", []),
    }


def _is_placeholder(value: str | None) -> bool:
    if value is None:
        return True
    normalized = value.strip()
    return normalized in PLACEHOLDER_VALUES or normalized.startswith("YOUR_")


def validate_live_verification_env(env: dict[str, str] | None = None) -> tuple[bool, list[str]]:
    values = load_runtime_env() if env is None else dict(env)
    missing: list[str] = []
    invalid: list[str] = []

    if values.get("GROUNDED_DECK_LLM_PROVIDER") != "openai-compatible":
        missing.append("GROUNDED_DECK_LLM_PROVIDER")
    if not values.get("GROUNDED_DECK_LLM_MODEL"):
        missing.append("GROUNDED_DECK_LLM_MODEL")
    elif _is_placeholder(values.get("GROUNDED_DECK_LLM_MODEL")):
        invalid.append("GROUNDED_DECK_LLM_MODEL")
    if not values.get("GROUNDED_DECK_BASE_URL"):
        missing.append("GROUNDED_DECK_BASE_URL")
    elif _is_placeholder(values.get("GROUNDED_DECK_BASE_URL")):
        invalid.append("GROUNDED_DECK_BASE_URL")

    api_key_env = values.get("GROUNDED_DECK_API_KEY_ENV", "GROUNDED_DECK_API_KEY")
    if not values.get(api_key_env):
        missing.append(api_key_env)
    elif _is_placeholder(values.get(api_key_env)):
        invalid.append(api_key_env)

    return (len(missing) == 0 and len(invalid) == 0, missing + invalid)


def _history_dir_name(summary: dict) -> str:
    input_stem = Path(summary.get("input_path", "live-verification")).stem
    if input_stem.endswith("-source-pack"):
        input_stem = input_stem[: -len("-source-pack")]
    generated_at_unix = summary.get("generated_at_unix", "unknown")
    return f"{input_stem}-{generated_at_unix}"


def archive_verification_summary(summary_path: Path, output_dir: Path) -> tuple[Path, Path]:
    if not summary_path.exists():
        raise FileNotFoundError(f"verification summary not found: {summary_path}")

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    history_dir = output_dir / "live-verification-history" / _history_dir_name(summary)
    history_dir.mkdir(parents=True, exist_ok=True)

    archived_summary = dict(summary)
    archived_artifacts: dict[str, str] = {}
    for artifact_name, artifact_path in summary.get("artifacts", {}).items():
        artifact_value = str(artifact_path)
        artifact_source = Path(artifact_value)
        if artifact_source.exists():
            archived_target = history_dir / artifact_source.name
            copy2(artifact_source, archived_target)
            archived_artifacts[artifact_name] = str(archived_target)
        else:
            archived_artifacts[artifact_name] = artifact_value
    archived_summary["artifacts"] = archived_artifacts

    verification_summary_target = history_dir / "verification-summary.json"
    verification_report_target = history_dir / "verification-report.md"
    verification_summary_target.write_text(
        json.dumps(archived_summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    verification_report_target.write_text(render_verification_report(archived_summary) + "\n", encoding="utf-8")

    if {
        "normalized_pack",
        "slide_spec",
        "quality_report",
    }.issubset(archived_artifacts):
        archived_paths = {key: Path(value) for key, value in archived_artifacts.items()}
        if all(path.exists() for path in archived_paths.values()):
            acceptance_summary = build_live_acceptance_snapshot(
                archived_summary,
                normalized_pack_path=archived_paths["normalized_pack"],
                slide_spec_path=archived_paths["slide_spec"],
                quality_report_path=archived_paths["quality_report"],
            )
            (history_dir / "acceptance-summary.json").write_text(
                json.dumps(acceptance_summary, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

    json_target = output_dir / "live-verification-latest.json"
    md_target = output_dir / "live-verification-latest.md"

    json_target.write_text(json.dumps(archived_summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_target.write_text(render_verification_report(archived_summary) + "\n", encoding="utf-8")

    return json_target, md_target


def render_live_verification_checklist(env: dict[str, str] | None = None) -> str:
    ok, missing = validate_live_verification_env(env)
    status = "READY" if ok else "BLOCKED"
    missing_text = ", ".join(missing) if missing else "none"

    lines = [
        "# Live Verification Checklist",
        "",
        f"- Status: `{status}`",
        f"- Missing Or Invalid Config: `{missing_text}`",
        "",
        "## Steps",
        "",
        "1. Run `make check-live-env` and confirm it returns `OK`.",
        "2. Replace placeholder values copied from `.env.runtime.example` before attempting a live run.",
        "3. Run `make verify-online` to execute the live provider path.",
        "4. Inspect `/tmp/grounded-deck-online/verification-summary.json`.",
        "5. Run `make archive-online-verification` to copy the latest result into `reports/` and `reports/live-verification-history/`.",
        "6. Update `docs/LATEST-HANDOFF.md` and `docs/TASK-BOARD.md` with the observed result.",
        "",
        "## Success Criteria",
        "",
        "- `quality_status` is `pass` in `verification-summary.json`.",
        "- The summary references `normalized-pack.json`, `slide-spec.json`, and `quality-report.json`.",
        "- `reports/live-verification-latest.json` and `.md` are present after archiving.",
        "- A repo-owned live snapshot exists under `reports/live-verification-history/` after archiving.",
        "- `make live-status` reports `Environment Ready: yes` before the live run starts.",
        "",
    ]
    return "\n".join(lines)


def write_live_verification_checklist(output_path: Path, env: dict[str, str] | None = None) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_live_verification_checklist(env) + "\n", encoding="utf-8")
    return output_path


def render_live_verification_status(summary_path: Path, env: dict[str, str] | None = None) -> str:
    ok, missing = validate_live_verification_env(env)
    lines = [
        "# Live Verification Status",
        "",
        f"- Environment Ready: `{'yes' if ok else 'no'}`",
        f"- Missing Or Invalid Config: `{', '.join(missing) if missing else 'none'}`",
        f"- Summary Present: `{'yes' if summary_path.exists() else 'no'}`",
    ]

    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        lines.extend(
            [
                f'- Last Mode: `{summary.get("mode", "unknown")}`',
                f'- Last Provider: `{summary.get("provider", "unknown")}`',
                f'- Last Quality Status: `{summary.get("quality_status", "unknown")}`',
            ]
        )
        if summary.get("error"):
            lines.append(f'- Last Error: `{summary["error"]}`')

    lines.append("")
    return "\n".join(lines)
