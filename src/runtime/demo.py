from __future__ import annotations

import json
from pathlib import Path

from src.llm.provider import DeterministicProvider, Provider
from src.runtime.cli import write_pipeline_outputs, write_verification_summary
from src.runtime.pipeline import run_pipeline


def render_strongest_demo_report(
    *,
    input_path: Path,
    output_dir: Path,
    result: dict,
    summary_path: Path,
) -> str:
    quality_report = result["quality_report"]
    coverage = quality_report["coverage"]
    grounding = quality_report.get("grounding", {})
    visual_form = quality_report.get("visual_form", {})
    slide_spec = result["slide_spec"]

    lines = [
        "# Strongest Demo Report",
        "",
        f"- Demo Fixture: `{input_path}`",
        f"- Provider: `{result['provider']}`",
        f"- Model: `{result['model']}`",
        f"- Deck Goal: `{slide_spec['deck_goal']}`",
        f"- Audience: `{slide_spec['audience']}`",
        f"- Slide Count: `{len(slide_spec['slides'])}`",
        f"- Verification Summary: `{summary_path}`",
        "",
        "## Success Metrics",
        "",
        (
            f"- Coverage: `{coverage['covered_units']}/{coverage['required_units']}` "
            "source units retained in `must_include_checks`."
        ),
        (
            f"- Grounding: `{grounding.get('grounded_slides', 0)}/"
            f"{grounding.get('total_content_slides', 0)}` non-cover slides keep valid source bindings."
        ),
        (
            f"- Visual Form: `{visual_form.get('matched_units', 0)}/"
            f"{visual_form.get('expected_units', 0)}` grounded units match deterministic layout expectations."
        ),
        "",
        "## Artifact Bundle",
        "",
        f"- Normalized Pack: `{output_dir / 'normalized-pack.json'}`",
        f"- Slide Spec: `{output_dir / 'slide-spec.json'}`",
        f"- Quality Report: `{output_dir / 'quality-report.json'}`",
        f"- Verification Summary: `{summary_path}`",
        "",
        "## Why This Demo",
        "",
        "- Uses grounded Chinese-language source material instead of generic topic prompts.",
        "- Exercises narrative compression, policy risk retention, and cross-source synthesis in one pass.",
        "- Stays within the current planning boundary without pretending rendering is done.",
        "",
    ]
    return "\n".join(lines)


def write_strongest_demo_bundle(
    *,
    input_path: Path,
    output_dir: Path,
    provider: Provider | None = None,
) -> dict:
    raw_pack = json.loads(input_path.read_text(encoding="utf-8"))
    result = run_pipeline(raw_pack, provider=provider or DeterministicProvider())
    write_pipeline_outputs(output_dir, result)
    summary_path = write_verification_summary(
        output_dir=output_dir,
        result=result,
        mode="strongest-demo",
        input_path=input_path,
    )
    report_path = output_dir / "strongest-demo-report.md"
    report_path.write_text(
        render_strongest_demo_report(
            input_path=input_path,
            output_dir=output_dir,
            result=result,
            summary_path=summary_path,
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "result": result,
        "summary_path": summary_path,
        "report_path": report_path,
    }
