from __future__ import annotations

from pathlib import Path

from src.ingest.normalize import normalize_source_pack
from src.llm.provider import DeterministicProvider, Provider
from src.planner.draft import draft_slide_spec
from src.quality.checks import grade_slide_spec
from src.quality.narrative_grader import grade_narrative
from src.renderer.artifact_grader import grade_pptx_artifact
from src.renderer.pptx_renderer import render_slide_spec_to_pptx


def run_pipeline(
    raw_pack: dict,
    provider: Provider | None = None,
    *,
    render_pptx: str | Path | None = None,
    theme: str | None = None,
    grade_artifact: bool = True,
    grade_narrative_quality: bool = True,
) -> dict:
    """运行完整的 GroundedDeck pipeline。

    参数：
        raw_pack: 原始 source pack dict
        provider: LLM provider（默认 DeterministicProvider）
        render_pptx: 如果提供，将 slide spec 渲染为 .pptx 文件并输出到该路径
        theme: PPTX 主题名称（默认 professional-blue）
        grade_artifact: 如果为 True 且 render_pptx 已提供，则自动执行 PPTX artifact grading
        grade_narrative_quality: 如果为 True，执行叙事质量评分

    返回：
        包含 normalized_pack、slide_spec、quality_report 以及可选的 pptx_path、artifact_grade、narrative_grade 的 dict
    """
    active_provider = provider or DeterministicProvider()
    normalized_pack = normalize_source_pack(raw_pack)
    slide_spec = draft_slide_spec(normalized_pack, provider=active_provider)
    quality_report = grade_slide_spec(normalized_pack, slide_spec, provider=active_provider)

    result = {
        "normalized_pack": normalized_pack,
        "slide_spec": slide_spec,
        "quality_report": quality_report,
        "provider": active_provider.name,
        "model": active_provider.config.model,
    }

    # 叙事质量评分
    if grade_narrative_quality:
        narrative_report = grade_narrative(normalized_pack, slide_spec)
        result["narrative_grade"] = narrative_report.as_dict()

    # 可选的 PPTX 渲染步骤
    if render_pptx is not None:
        pptx_path = render_slide_spec_to_pptx(slide_spec, render_pptx, theme=theme)
        result["pptx_path"] = str(pptx_path)
        if theme:
            result["theme"] = theme

        # 自动 artifact grading
        if grade_artifact:
            artifact_report = grade_pptx_artifact(pptx_path, slide_spec=slide_spec)
            result["artifact_grade"] = artifact_report

    return result