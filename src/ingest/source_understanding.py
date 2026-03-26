"""来源深度理解模块。

使用 LLM 对解析后的 Markdown 文档进行深度理解，提取：
- 结论与主张（claims）
- 关键数据与指标
- 逻辑关系与论证结构
- 候选视觉结构建议
- 时间信息
- 角色与对象关系

输出为 GroundedDeck 内部 source pack JSON 格式。
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Callable

from src.ingest.markdown_reader import MarkdownDocument, MarkdownSection


@dataclass(frozen=True)
class IngestConfig:
    """来源理解的配置。"""
    # 文档语言（自动检测或手动指定）
    language: str = "auto"
    # deck 目标（如果用户未指定，LLM 会从文档中推断）
    deck_goal: str = ""
    # 目标受众（如果用户未指定，LLM 会从文档中推断）
    audience: str = ""
    # source type 标签
    source_type: str = "document"


# LLM 回调类型：接收 (system_prompt, user_prompt)，返回 JSON dict
SourceUnderstandingCallback = Callable[[str, str], dict]


def _detect_language(text: str) -> str:
    """简单的语言检测：如果中文字符占比超过 20%，判定为 zh-CN。"""
    if not text:
        return "en"
    cjk_count = len(re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf]', text))
    total = len(text.replace(' ', '').replace('\n', ''))
    if total == 0:
        return "en"
    ratio = cjk_count / total
    return "zh-CN" if ratio > 0.2 else "en"


def _generate_pack_id(title: str, content_hash: str) -> str:
    """根据标题和内容哈希生成 pack_id。"""
    # 将标题转为 kebab-case
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[\s_]+', '-', slug).strip('-')
    if not slug:
        slug = "untitled"
    # 截断并附加短哈希
    slug = slug[:40]
    short_hash = content_hash[:8]
    return f"{slug}-{short_hash}"


def _generate_source_id(index: int) -> str:
    """生成 source_id。"""
    return f"src-{index + 1:02d}"


def _generate_section_id(index: int) -> str:
    """生成 section_id。"""
    return f"sec-{index + 1:02d}"


def _content_hash(text: str) -> str:
    """计算内容的 SHA256 哈希。"""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------- 确定性理解（不依赖 LLM） ----------

def _extract_claims_deterministic(section: MarkdownSection) -> list[str]:
    """确定性地从章节中提取主张/结论。

    策略：
    1. 引用块内容视为重要主张
    2. 包含数字/百分比的句子视为数据主张
    3. 包含结论性词汇的句子视为结论
    4. 列表项中的关键要点
    """
    claims: list[str] = []
    seen: set[str] = set()

    def _add_claim(text: str) -> None:
        text = text.strip()
        if text and text not in seen:
            seen.add(text)
            claims.append(text)

    for block in section.blocks:
        if block.block_type == "blockquote":
            _add_claim(block.content)

    # 从段落中提取包含数据的句子
    data_pattern = re.compile(r'\d+\.?\d*\s*[%％]|¥|＄|\$|€|£|\d{4}\s*年|\d+\s*亿|\d+\s*万')
    conclusion_pattern = re.compile(
        r'因此|所以|总之|综上|结论|建议|推荐|关键|核心|重要|'
        r'therefore|thus|conclude|recommend|key|critical|important|suggest',
        re.IGNORECASE,
    )

    for block in section.blocks:
        if block.block_type == "paragraph":
            # 按句号/问号/感叹号分句
            sentences = re.split(r'[。！？.!?]', block.content)
            for sent in sentences:
                sent = sent.strip()
                if not sent or len(sent) < 8:
                    continue
                if data_pattern.search(sent):
                    _add_claim(sent)
                elif conclusion_pattern.search(sent):
                    _add_claim(sent)

        elif block.block_type == "list":
            for item in block.items:
                item = item.strip()
                if len(item) >= 10:
                    if data_pattern.search(item) or conclusion_pattern.search(item):
                        _add_claim(item)

    # 如果没有提取到任何 claim，取第一个段落的第一句作为兜底
    if not claims:
        for block in section.blocks:
            if block.block_type == "paragraph" and block.content.strip():
                first_sent = re.split(r'[。！？.!?]', block.content)[0].strip()
                if first_sent and len(first_sent) >= 8:
                    _add_claim(first_sent)
                    break

    return claims


def understand_source_deterministic(
    doc: MarkdownDocument,
    config: IngestConfig | None = None,
) -> dict:
    """确定性地将 MarkdownDocument 转换为 source pack JSON。

    不依赖 LLM，使用规则引擎提取结构化信息。
    适用于测试和作为 LLM 理解的质量基线。

    参数：
        doc: 解析后的 MarkdownDocument
        config: 摄取配置

    返回：
        source pack JSON dict
    """
    cfg = config or IngestConfig()

    # 语言检测
    language = cfg.language
    if language == "auto":
        language = _detect_language(doc.all_text)

    # 生成 pack_id
    content_hash = _content_hash(doc.all_text)
    pack_id = _generate_pack_id(doc.title or "untitled", content_hash)

    # deck_goal 和 audience
    deck_goal = cfg.deck_goal
    audience = cfg.audience

    if not deck_goal:
        if doc.title:
            deck_goal = f"基于「{doc.title}」生成结构化演示" if language == "zh-CN" else f"Generate a structured presentation based on '{doc.title}'"
        else:
            deck_goal = "基于提供的材料生成结构化演示" if language == "zh-CN" else "Generate a structured presentation from the provided material"

    if not audience:
        audience = "需要了解该主题的决策者和利益相关方" if language == "zh-CN" else "Decision makers and stakeholders who need to understand this topic"

    # 将文档章节转换为 sources 和 sections
    # 策略：将顶级章节（h2）作为独立 source，其下的子章节（h3+）作为 sections
    sources: list[dict] = []

    # 收集顶级章节
    top_sections: list[tuple[MarkdownSection, list[MarkdownSection]]] = []
    current_top: MarkdownSection | None = None
    current_children: list[MarkdownSection] = []

    for section in doc.sections:
        if section.level <= 2:
            if current_top is not None:
                top_sections.append((current_top, current_children))
            current_top = section
            current_children = []
        else:
            if current_top is not None:
                current_children.append(section)
            else:
                # 没有顶级标题的子章节，创建一个虚拟顶级
                current_top = section
                current_children = []

    if current_top is not None:
        top_sections.append((current_top, current_children))

    # 如果没有任何章节，将整个文档作为一个 source
    if not top_sections:
        source_id = _generate_source_id(0)
        section_id = _generate_section_id(0)
        all_text = doc.all_text or ""
        claims = []
        # 从 preamble 中提取
        for block in doc.preamble:
            if block.block_type == "paragraph":
                sents = re.split(r'[。！？.!?]', block.content)
                for s in sents:
                    s = s.strip()
                    if s and len(s) >= 8:
                        claims.append(s)
                        break
                if claims:
                    break

        sources.append({
            "source_id": source_id,
            "type": cfg.source_type,
            "title": doc.title or "Untitled Document",
            "language": language,
            "sections": [{
                "section_id": section_id,
                "heading": doc.title or "Main Content",
                "paragraphs": [b.content for b in doc.preamble if b.block_type == "paragraph"],
                "claims": claims or [all_text[:200] + "..." if len(all_text) > 200 else all_text],
            }],
        })
    else:
        for src_idx, (top_section, children) in enumerate(top_sections):
            source_id = _generate_source_id(src_idx)

            sections_list: list[dict] = []

            if children:
                # 有子章节：每个子章节是一个 section
                for sec_idx, child in enumerate(children):
                    section_id = _generate_section_id(sec_idx)
                    claims = _extract_claims_deterministic(child)
                    sections_list.append({
                        "section_id": section_id,
                        "heading": child.heading,
                        "paragraphs": child.paragraphs,
                        "claims": claims,
                    })
                # 如果顶级章节本身也有内容（不只是标题），也加入
                if top_section.blocks:
                    claims = _extract_claims_deterministic(top_section)
                    sections_list.insert(0, {
                        "section_id": _generate_section_id(len(children)),
                        "heading": top_section.heading,
                        "paragraphs": top_section.paragraphs,
                        "claims": claims,
                    })
                    # 重新编号
                    for idx, sec in enumerate(sections_list):
                        sec["section_id"] = _generate_section_id(idx)
            else:
                # 没有子章节：顶级章节本身就是一个 section
                section_id = _generate_section_id(0)
                claims = _extract_claims_deterministic(top_section)
                sections_list.append({
                    "section_id": section_id,
                    "heading": top_section.heading,
                    "paragraphs": top_section.paragraphs,
                    "claims": claims,
                })

            sources.append({
                "source_id": source_id,
                "type": cfg.source_type,
                "title": top_section.heading,
                "language": language,
                "sections": sections_list,
            })

    return {
        "pack_id": pack_id,
        "language": language,
        "deck_goal": deck_goal,
        "audience": audience,
        "sources": sources,
    }


# ---------- LLM 深度理解 ----------

def _build_understanding_system_prompt() -> str:
    """构建来源理解的 system prompt。"""
    return (
        "你是 GroundedDeck 的来源理解引擎。你的任务是深度理解用户提供的文档内容，"
        "并将其转换为结构化的 source pack JSON 格式。\n\n"
        "你需要：\n"
        "1. 理解文档的核心主题、论点和结论\n"
        "2. 识别关键数据、指标和事实\n"
        "3. 提取逻辑关系和论证结构\n"
        "4. 识别时间线、对比、流程等信息结构\n"
        "5. 为每个章节提取精准的 claims（主张/结论）\n"
        "6. 推断最适合的 deck_goal 和 audience\n\n"
        "输出要求：\n"
        "- 返回严格的 JSON 格式\n"
        "- 每个 claim 必须有文档中的事实依据，不要编造\n"
        "- claims 应该是简洁有力的陈述句\n"
        "- paragraphs 保留原文关键段落\n"
        "- 如果文档是中文，claims 和其他文本也用中文\n"
    )


def _build_understanding_user_prompt(
    doc: MarkdownDocument,
    config: IngestConfig,
    deterministic_pack: dict,
) -> str:
    """构建来源理解的 user prompt。"""
    # 提供确定性基线作为参考结构
    return (
        "请深度理解以下文档内容，并输出 source pack JSON。\n\n"
        f"文档标题：{doc.title or '未知'}\n"
        f"文档字数：约 {doc.word_count} 字\n"
        f"章节数量：{doc.section_count}\n\n"
        "以下是文档的完整内容：\n"
        "---\n"
        f"{doc.all_text}\n"
        "---\n\n"
        "以下是规则引擎的初步结构化结果，你可以参考其结构，但应该基于你的深度理解来改进 claims 和 paragraphs 的质量：\n"
        f"```json\n{json.dumps(deterministic_pack, ensure_ascii=False, indent=2)}\n```\n\n"
        "请输出改进后的 source pack JSON。要求：\n"
        "1. 保持相同的 pack_id、source_id、section_id 结构\n"
        "2. 改进 deck_goal 使其更精准地反映文档核心目的\n"
        "3. 改进 audience 使其更具体\n"
        "4. 改进每个 section 的 claims，使其更精准、更有洞察力\n"
        "5. 保留关键的 paragraphs 原文\n"
        "6. 只返回 JSON，不要其他内容\n"
    )


def understand_source(
    doc: MarkdownDocument,
    config: IngestConfig | None = None,
    *,
    llm_callback: SourceUnderstandingCallback | None = None,
) -> dict:
    """将 MarkdownDocument 转换为 source pack JSON。

    如果提供了 llm_callback，使用 LLM 进行深度理解。
    否则回退到确定性规则引擎。

    参数：
        doc: 解析后的 MarkdownDocument
        config: 摄取配置
        llm_callback: LLM 回调函数，接收 (system_prompt, user_prompt) 返回 JSON dict

    返回：
        source pack JSON dict
    """
    cfg = config or IngestConfig()

    # 先用确定性方法生成基线
    deterministic_pack = understand_source_deterministic(doc, cfg)

    if llm_callback is None:
        return deterministic_pack

    # 使用 LLM 深度理解
    system_prompt = _build_understanding_system_prompt()
    user_prompt = _build_understanding_user_prompt(doc, cfg, deterministic_pack)

    try:
        llm_result = llm_callback(system_prompt, user_prompt)

        # 验证 LLM 输出的基本结构
        if not isinstance(llm_result, dict):
            return deterministic_pack

        required_keys = {"pack_id", "language", "deck_goal", "audience", "sources"}
        if not required_keys.issubset(llm_result.keys()):
            return deterministic_pack

        # 验证 sources 结构
        sources = llm_result.get("sources", [])
        if not isinstance(sources, list) or not sources:
            return deterministic_pack

        for source in sources:
            if not isinstance(source, dict):
                return deterministic_pack
            if "source_id" not in source or "sections" not in source:
                return deterministic_pack
            for section in source.get("sections", []):
                if not isinstance(section, dict):
                    return deterministic_pack
                if "section_id" not in section or "heading" not in section:
                    return deterministic_pack

        return llm_result

    except Exception:
        # LLM 失败时回退到确定性结果
        return deterministic_pack
