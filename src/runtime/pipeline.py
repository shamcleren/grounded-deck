from __future__ import annotations

import json
from pathlib import Path

from src.ingest.markdown_reader import parse_markdown
from src.ingest.normalize import normalize_source_pack
from src.ingest.source_understanding import (
    IngestConfig,
    SourceUnderstandingCallback,
    understand_source,
)
from src.llm.provider import DeterministicProvider, Provider
from src.planner.draft import draft_slide_spec
from src.quality.checks import grade_slide_spec
from src.quality.narrative_grader import grade_narrative
from src.renderer.artifact_grader import grade_pptx_artifact
from src.renderer.pptx_renderer import render_slide_spec_to_pptx


# 支持的输入文件格式
SUPPORTED_EXTENSIONS = {".md", ".markdown"}


def detect_input_format(path: Path) -> str:
    """检测输入文件格式。

    返回：
        格式标识符：'markdown', 'source-pack-json', 或 'unknown'
    """
    suffix = path.suffix.lower()
    if suffix in SUPPORTED_EXTENSIONS:
        return "markdown"
    if suffix == ".json":
        return "source-pack-json"
    return "unknown"


def ingest_from_file(
    path: Path,
    *,
    ingest_config: IngestConfig | None = None,
    llm_callback: SourceUnderstandingCallback | None = None,
) -> dict:
    """从文件路径摄取来源材料，返回 source pack JSON。

    自动检测文件格式：
    - .md / .markdown → Markdown 解析 + 来源理解
    - .json → 直接作为 source pack 加载

    参数：
        path: 输入文件路径
        ingest_config: 摄取配置
        llm_callback: LLM 回调（可选，用于深度理解）

    返回：
        source pack JSON dict
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"输入文件不存在: {path}")

    fmt = detect_input_format(path)

    if fmt == "source-pack-json":
        return json.loads(path.read_text(encoding="utf-8"))

    if fmt == "markdown":
        text = path.read_text(encoding="utf-8")
        doc = parse_markdown(text)
        return understand_source(doc, ingest_config, llm_callback=llm_callback)

    raise ValueError(
        f"不支持的文件格式: {path.suffix}。"
        f"当前支持: {', '.join(sorted(SUPPORTED_EXTENSIONS | {'.json'}))}"
    )


def run_pipeline(
    raw_pack: dict | None = None,
    provider: Provider | None = None,
    *,
    input_path: str | Path | None = None,
    ingest_config: IngestConfig | None = None,
    render_pptx: str | Path | None = None,
    theme: str | None = None,
    grade_artifact: bool = True,
    grade_narrative_quality: bool = True,
) -> dict:
    """运行完整的 GroundedDeck pipeline。

    参数：
        raw_pack: 原始 source pack dict（与 input_path 二选一）
        provider: LLM provider（默认 DeterministicProvider）
        input_path: 输入文件路径（支持 .md、.json）
        ingest_config: 来源摄取配置（仅当 input_path 为非 JSON 格式时使用）
        render_pptx: 如果提供，将 slide spec 渲染为 .pptx 文件并输出到该路径
        theme: PPTX 主题名称（默认 professional-blue）
        grade_artifact: 如果为 True 且 render_pptx 已提供，则自动执行 PPTX artifact grading
        grade_narrative_quality: 如果为 True，执行叙事质量评分

    返回：
        包含 normalized_pack、slide_spec、quality_report 以及可选的
        source_pack、pptx_path、artifact_grade、narrative_grade 的 dict
    """
    active_provider = provider or DeterministicProvider()

    # 从文件路径摄取 source pack
    if raw_pack is None and input_path is not None:
        input_path = Path(input_path)
        # 如果 provider 是 OpenAI-compatible，构建 LLM callback
        llm_callback = None
        if hasattr(active_provider, 'build_chat_request') and hasattr(active_provider, 'parse_json_response'):
            def _llm_callback(system_prompt: str, user_prompt: str) -> dict:
                req = active_provider.build_chat_request(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    response_format={"type": "json_object"},
                )
                return active_provider.parse_json_response(active_provider.transport(req))
            llm_callback = _llm_callback

        raw_pack = ingest_from_file(
            input_path,
            ingest_config=ingest_config,
            llm_callback=llm_callback,
        )
    elif raw_pack is None:
        raise ValueError("必须提供 raw_pack 或 input_path 之一")

    normalized_pack = normalize_source_pack(raw_pack)
    slide_spec = draft_slide_spec(normalized_pack, provider=active_provider)
    quality_report = grade_slide_spec(normalized_pack, slide_spec, provider=active_provider)

    result = {
        "source_pack": raw_pack,
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