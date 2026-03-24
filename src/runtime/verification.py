from __future__ import annotations

import json
import os
from pathlib import Path
from time import time

from src.runtime.env import load_runtime_env


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


def validate_live_verification_env(env: dict[str, str] | None = None) -> tuple[bool, list[str]]:
    values = load_runtime_env() if env is None else dict(env)
    missing: list[str] = []

    if values.get("GROUNDED_DECK_LLM_PROVIDER") != "openai-compatible":
        missing.append("GROUNDED_DECK_LLM_PROVIDER")
    if not values.get("GROUNDED_DECK_LLM_MODEL"):
        missing.append("GROUNDED_DECK_LLM_MODEL")
    if not values.get("GROUNDED_DECK_BASE_URL"):
        missing.append("GROUNDED_DECK_BASE_URL")

    api_key_env = values.get("GROUNDED_DECK_API_KEY_ENV", "GROUNDED_DECK_API_KEY")
    if not values.get(api_key_env):
        missing.append(api_key_env)

    return (len(missing) == 0, missing)


def archive_verification_summary(summary_path: Path, output_dir: Path) -> tuple[Path, Path]:
    if not summary_path.exists():
        raise FileNotFoundError(f"verification summary not found: {summary_path}")

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)

    json_target = output_dir / "live-verification-latest.json"
    md_target = output_dir / "live-verification-latest.md"

    json_target.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_target.write_text(render_verification_report(summary) + "\n", encoding="utf-8")

    return json_target, md_target


def render_live_verification_checklist(env: dict[str, str] | None = None) -> str:
    ok, missing = validate_live_verification_env(env)
    status = "READY" if ok else "BLOCKED"
    missing_text = ", ".join(missing) if missing else "none"

    lines = [
        "# Live Verification Checklist",
        "",
        f"- Status: `{status}`",
        f"- Missing Config: `{missing_text}`",
        "",
        "## Steps",
        "",
        "1. Run `make check-live-env` and confirm it returns `OK`.",
        "2. Run `make verify-online` to execute the live provider path.",
        "3. Inspect `/tmp/grounded-deck-online/verification-summary.json`.",
        "4. Run `make archive-online-verification` to copy the successful result into `reports/`.",
        "5. Update `docs/LATEST-HANDOFF.md` and `docs/TASK-BOARD.md` with the observed result.",
        "",
        "## Success Criteria",
        "",
        "- `quality_status` is `pass` in `verification-summary.json`.",
        "- The summary references `normalized-pack.json`, `slide-spec.json`, and `quality-report.json`.",
        "- `reports/live-verification-latest.json` and `.md` are present after archiving.",
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
        f"- Missing Config: `{', '.join(missing) if missing else 'none'}`",
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
