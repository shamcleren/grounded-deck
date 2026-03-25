from __future__ import annotations

import json
from pathlib import Path

from src.llm.provider import DeterministicProvider, Provider
from src.renderer.artifact_grader import grade_pptx_artifact
from src.renderer.pptx_renderer import render_slide_spec_to_pptx
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
    narrative = quality_report.get("narrative_quality", {})
    slide_spec = result["slide_spec"]
    artifact_grade = result.get("artifact_grade", {})
    narrative_grade = result.get("narrative_grade", {})

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
        (
            f"- Narrative Quality: `{narrative.get('quality_ratio', 'N/A')}` quality ratio, "
            f"`{narrative.get('total_key_points', 0)}` key points, "
            f"`{narrative.get('source_annotated_points', 0)}` source-annotated."
        ),
        "",
        "## Artifact Grade",
        "",
        f"- Status: `{artifact_grade.get('status', 'N/A')}`",
        f"- Editability: `{artifact_grade.get('metrics', {}).get('editability_ratio', 'N/A')}`",
        f"- Notes Coverage: `{artifact_grade.get('metrics', {}).get('notes_coverage_ratio', 'N/A')}`",
        f"- Source Bindings Coverage: `{artifact_grade.get('metrics', {}).get('source_binding_coverage_ratio', 'N/A')}`",
        f"- Chinese Text: `{artifact_grade.get('metrics', {}).get('chinese_text_found', 'N/A')}`",
        "",
        "## Narrative Grade",
        "",
        f"- Status: `{narrative_grade.get('status', 'N/A')}`",
        f"- Mode: `{narrative_grade.get('mode', 'N/A')}`",
        f"- Avg Coherence: `{narrative_grade.get('avg_coherence', 'N/A')}`",
        f"- Avg Grounding: `{narrative_grade.get('avg_grounding', 'N/A')}`",
        f"- Avg Visual Fit: `{narrative_grade.get('avg_visual_fit', 'N/A')}`",
        f"- Avg Composite: `{narrative_grade.get('avg_composite', 'N/A')}`",
        f"- Issues: `{len(narrative_grade.get('issues', []))}`",
        "",
        "## Artifact Bundle",
        "",
        f"- Normalized Pack: `{output_dir / 'normalized-pack.json'}`",
        f"- Slide Spec: `{output_dir / 'slide-spec.json'}`",
        f"- Quality Report: `{output_dir / 'quality-report.json'}`",
        f"- PPTX Output: `{output_dir / 'strongest-demo.pptx'}`",
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

    # 渲染 PPTX 文件
    pptx_path = output_dir / "strongest-demo.pptx"
    render_slide_spec_to_pptx(result["slide_spec"], pptx_path)
    result["pptx_path"] = str(pptx_path)

    # Artifact grading
    artifact_report = grade_pptx_artifact(pptx_path, slide_spec=result["slide_spec"])
    result["artifact_grade"] = artifact_report
    (output_dir / "artifact-grade.json").write_text(
        json.dumps(artifact_report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # Narrative grading 报告
    if "narrative_grade" in result:
        (output_dir / "narrative-grade.json").write_text(
            json.dumps(result["narrative_grade"], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

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
