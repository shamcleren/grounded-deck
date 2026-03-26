"""模型辅助叙事质量评分器：评估 slide spec 中 key_points 的叙事质量和视觉选择合理性。

该模块实现 evaluation-plan phase three 的 model-based grading 能力：
- narrative coherence: key_points 是否连贯、具体、source-grounded
- visual selection quality: layout_type 选择是否与内容结构匹配
- audience alignment: 叙事是否面向目标受众

支持两种模式：
- deterministic: 基于规则的启发式评分（无需 LLM）
- model-assisted: 通过 OpenAI-compatible provider 获取 LLM 评分
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Callable


# ---------- 叙事质量评分结果 ----------

@dataclass(frozen=True)
class NarrativeGradeItem:
    """单个 slide 的叙事质量评分。"""

    slide_id: str
    layout_type: str
    coherence_score: float  # 0.0-1.0: key_points 连贯性和具体性
    grounding_score: float  # 0.0-1.0: source-grounded 程度
    visual_fit_score: float  # 0.0-1.0: layout 与内容的匹配度
    issues: list[str] = field(default_factory=list)

    @property
    def composite_score(self) -> float:
        """综合评分：三个维度的加权平均。"""
        return round(
            0.4 * self.coherence_score + 0.3 * self.grounding_score + 0.3 * self.visual_fit_score,
            2,
        )


@dataclass(frozen=True)
class NarrativeGradeReport:
    """完整的叙事质量评分报告。"""

    items: list[NarrativeGradeItem]
    mode: str = "deterministic"  # deterministic | model-assisted

    @property
    def slide_count(self) -> int:
        return len(self.items)

    @property
    def avg_coherence(self) -> float:
        if not self.items:
            return 0.0
        return round(sum(i.coherence_score for i in self.items) / len(self.items), 2)

    @property
    def avg_grounding(self) -> float:
        if not self.items:
            return 0.0
        return round(sum(i.grounding_score for i in self.items) / len(self.items), 2)

    @property
    def avg_visual_fit(self) -> float:
        if not self.items:
            return 0.0
        return round(sum(i.visual_fit_score for i in self.items) / len(self.items), 2)

    @property
    def avg_composite(self) -> float:
        if not self.items:
            return 0.0
        return round(sum(i.composite_score for i in self.items) / len(self.items), 2)

    @property
    def all_issues(self) -> list[str]:
        issues: list[str] = []
        for item in self.items:
            for issue in item.issues:
                issues.append(f"[{item.slide_id}] {issue}")
        return issues

    @property
    def status(self) -> str:
        """pass 如果所有 slide 的 composite_score >= 0.6，否则 fail。"""
        if not self.items:
            return "fail"
        return "pass" if all(i.composite_score >= 0.6 for i in self.items) else "fail"

    def as_dict(self) -> dict:
        """转换为可序列化的 dict。"""
        return {
            "status": self.status,
            "mode": self.mode,
            "slide_count": self.slide_count,
            "avg_coherence": self.avg_coherence,
            "avg_grounding": self.avg_grounding,
            "avg_visual_fit": self.avg_visual_fit,
            "avg_composite": self.avg_composite,
            "issues": self.all_issues,
            "slides": [
                {
                    "slide_id": item.slide_id,
                    "layout_type": item.layout_type,
                    "coherence_score": item.coherence_score,
                    "grounding_score": item.grounding_score,
                    "visual_fit_score": item.visual_fit_score,
                    "composite_score": item.composite_score,
                    "issues": item.issues,
                }
                for item in self.items
            ],
        }


# ---------- 确定性叙事评分（规则引擎） ----------

def _score_coherence_deterministic(slide: dict) -> tuple[float, list[str]]:
    """基于规则评估 key_points 的连贯性和具体性。

    评分标准：
    - 有 key_points 且非空: +0.4
    - key_points 平均长度 >= 10 字符: +0.3（具体性）
    - key_points 包含中文字符: +0.15（保留源语言）
    - key_points 数量 >= 2: +0.15（充分性）
    """
    score = 0.0
    issues: list[str] = []
    kp = slide.get("key_points", [])

    if not kp:
        issues.append("no key_points")
        return 0.0, issues

    # 基础分：有 key_points
    score += 0.4

    # 具体性：平均长度
    avg_len = sum(len(str(p)) for p in kp) / len(kp)
    if avg_len >= 10:
        score += 0.3
    elif avg_len >= 5:
        score += 0.15
        issues.append(f"key_points average length {avg_len:.0f} is short")
    else:
        issues.append(f"key_points average length {avg_len:.0f} is too short")

    # 源语言保留
    has_chinese = any(
        any(ord(c) > 0x4E00 for c in str(p)) for p in kp
    )
    if has_chinese:
        score += 0.15

    # 充分性
    if len(kp) >= 2:
        score += 0.15
    else:
        issues.append("only 1 key_point")

    return min(1.0, round(score, 2)), issues


def _score_grounding_deterministic(slide: dict) -> tuple[float, list[str]]:
    """基于规则评估 slide 的 source-grounded 程度。

    评分标准：
    - 有 source_bindings 且非空: +0.5
    - 有 must_include_checks 且非空: +0.2
    - speaker_notes 包含 source 引用: +0.15
    - key_points 包含 [binding] 标注: +0.15
    """
    score = 0.0
    issues: list[str] = []

    bindings = slide.get("source_bindings", [])
    if bindings:
        score += 0.5
    else:
        if slide.get("layout_type") != "cover":
            issues.append("no source_bindings")

    checks = slide.get("must_include_checks", [])
    if checks:
        score += 0.2

    notes = str(slide.get("speaker_notes", ""))
    if "source" in notes.lower() or "ground" in notes.lower() or any(b in notes for b in bindings):
        score += 0.15

    # key_points 中的 source annotation
    kp = slide.get("key_points", [])
    annotated = sum(1 for p in kp if isinstance(p, str) and "[" in p and "]" in p)
    if annotated > 0:
        score += 0.15

    return min(1.0, round(score, 2)), issues


def _score_visual_fit_deterministic(slide: dict, unit: dict | None = None) -> tuple[float, list[str]]:
    """基于规则评估 layout_type 与内容的匹配度。

    评分标准：
    - 有 visual_elements 且非空: +0.4
    - visual_elements 类型与 layout_type 一致: +0.3
    - visual_elements 包含 source-grounded 内容（非空 milestones/columns/steps/metrics）: +0.3
    """
    score = 0.0
    issues: list[str] = []
    layout = slide.get("layout_type", "")
    elements = slide.get("visual_elements", [])

    if not elements:
        issues.append("no visual_elements")
        return 0.0, issues

    # 确保 elements 中的每个元素都是 dict（兼容字符串列表等非标准格式）
    dict_elements = [e for e in elements if isinstance(e, dict)]
    if not dict_elements:
        issues.append("visual_elements contains no dict entries")
        return 0.4, issues  # 有元素但格式不标准，给基础分

    score += 0.4

    # 类型一致性检查
    expected_types = {
        "timeline": "timeline",
        "comparison": "comparison-columns",
        "process": "process-flow",
        "chart": "metric-cards",
        "summary": "bullet-list",
        "cover": "title-block",
    }
    expected_type = expected_types.get(layout, "")
    has_matching_type = any(
        e.get("type", "") == expected_type for e in dict_elements
    )
    if has_matching_type:
        score += 0.3
    else:
        # cover slide 可能有多种 visual element types
        if layout == "cover":
            score += 0.3  # cover 总是匹配
        else:
            issues.append(f"visual_elements type mismatch for layout '{layout}'")

    # source-grounded 内容丰富度
    has_rich_content = False
    for elem in dict_elements:
        etype = elem.get("type", "")
        if etype == "timeline" and elem.get("milestones"):
            has_rich_content = True
        elif etype == "comparison-columns" and elem.get("columns"):
            has_rich_content = True
        elif etype == "process-flow" and elem.get("step_labels"):
            has_rich_content = True
        elif etype == "metric-cards" and elem.get("metrics"):
            has_rich_content = True
        elif etype == "bullet-list":
            has_rich_content = True  # bullet-list 总是有效
        elif etype in ("title-block", "source-count", "topic-overview", "claim-source-map"):
            has_rich_content = True  # cover/summary 特殊元素

    if has_rich_content:
        score += 0.3
    else:
        issues.append("visual_elements lack source-grounded content")

    return min(1.0, round(score, 2)), issues


def grade_narrative_deterministic(
    normalized_pack: dict,
    slide_spec: dict,
) -> NarrativeGradeReport:
    """确定性叙事质量评分：基于规则引擎对每个 slide 进行三维评分。"""
    unit_by_id = {u["unit_id"]: u for u in normalized_pack.get("source_units", [])}
    items: list[NarrativeGradeItem] = []

    for slide in slide_spec.get("slides", []):
        sid = slide.get("slide_id", "unknown")
        layout = slide.get("layout_type", "")

        # 找到对应的 source unit（如果有）
        checks = slide.get("must_include_checks", [])
        unit = unit_by_id.get(checks[0]) if len(checks) == 1 else None

        coherence, c_issues = _score_coherence_deterministic(slide)
        grounding, g_issues = _score_grounding_deterministic(slide)
        visual_fit, v_issues = _score_visual_fit_deterministic(slide, unit)

        items.append(
            NarrativeGradeItem(
                slide_id=sid,
                layout_type=layout,
                coherence_score=coherence,
                grounding_score=grounding,
                visual_fit_score=visual_fit,
                issues=c_issues + g_issues + v_issues,
            )
        )

    return NarrativeGradeReport(items=items, mode="deterministic")


# ---------- 模型辅助叙事评分 ----------

# 模型叙事评分回调类型
ModelNarrativeCallback = Callable[[dict, dict], dict]


def build_narrative_grader_system_prompt() -> str:
    """构建叙事质量评分的 system prompt。"""
    return (
        "You are GroundedDeck's narrative quality grader. "
        "For each slide in the slide spec, evaluate three dimensions:\n"
        "1. coherence_score (0.0-1.0): Are the key_points coherent, specific, and non-generic? "
        "Do they tell a clear story that supports the slide goal?\n"
        "2. grounding_score (0.0-1.0): Are the key_points and visual_elements traceable to source material? "
        "Do source_bindings and must_include_checks correctly reference the source pack?\n"
        "3. visual_fit_score (0.0-1.0): Does the layout_type match the content structure? "
        "Are visual_elements appropriate for the chosen layout?\n\n"
        "Return valid JSON with this structure:\n"
        '{"slides": [{"slide_id": "...", "coherence_score": 0.0, "grounding_score": 0.0, '
        '"visual_fit_score": 0.0, "issues": ["..."]}]}\n'
        "Be strict: generic key_points like 'overview' or empty visual_elements should score low. "
        "Source-grounded Chinese content that preserves the original language should score high."
    )


def build_narrative_grader_user_prompt(
    normalized_pack: dict,
    slide_spec: dict,
) -> str:
    """构建叙事质量评分的 user prompt。"""
    return (
        "Grade the narrative quality of each slide in this slide spec.\n"
        "For each slide, provide coherence_score, grounding_score, visual_fit_score (all 0.0-1.0), "
        "and a list of issues (empty if none).\n"
        "- Return JSON only.\n"
        f"normalized_pack={json.dumps(normalized_pack, ensure_ascii=False)}\n"
        f"slide_spec={json.dumps(slide_spec, ensure_ascii=False)}"
    )


def _parse_model_narrative_response(
    response: dict,
    slide_spec: dict,
) -> NarrativeGradeReport:
    """解析模型返回的叙事评分 JSON。"""
    slides_data = response.get("slides", [])
    spec_slides = slide_spec.get("slides", [])

    # 构建 slide_id -> model grade 映射
    model_grades = {s.get("slide_id", ""): s for s in slides_data}

    items: list[NarrativeGradeItem] = []
    for spec_slide in spec_slides:
        sid = spec_slide.get("slide_id", "unknown")
        layout = spec_slide.get("layout_type", "")
        grade = model_grades.get(sid, {})

        items.append(
            NarrativeGradeItem(
                slide_id=sid,
                layout_type=layout,
                coherence_score=min(1.0, max(0.0, float(grade.get("coherence_score", 0.5)))),
                grounding_score=min(1.0, max(0.0, float(grade.get("grounding_score", 0.5)))),
                visual_fit_score=min(1.0, max(0.0, float(grade.get("visual_fit_score", 0.5)))),
                issues=list(grade.get("issues", [])),
            )
        )

    return NarrativeGradeReport(items=items, mode="model-assisted")


def grade_narrative_model_assisted(
    normalized_pack: dict,
    slide_spec: dict,
    callback: ModelNarrativeCallback,
) -> NarrativeGradeReport:
    """模型辅助叙事质量评分：通过 LLM 获取每个 slide 的三维评分。

    如果模型调用失败，自动回退到确定性评分。
    """
    try:
        prompts = {
            "system": build_narrative_grader_system_prompt(),
            "user": build_narrative_grader_user_prompt(normalized_pack, slide_spec),
        }
        response = callback(prompts, slide_spec)
        return _parse_model_narrative_response(response, slide_spec)
    except Exception:
        # 回退到确定性评分
        return grade_narrative_deterministic(normalized_pack, slide_spec)


def grade_narrative(
    normalized_pack: dict,
    slide_spec: dict,
    *,
    callback: ModelNarrativeCallback | None = None,
) -> NarrativeGradeReport:
    """叙事质量评分主入口。

    当提供 callback 时使用 model-assisted 模式，否则使用确定性模式。
    """
    if callback is not None:
        return grade_narrative_model_assisted(normalized_pack, slide_spec, callback)
    return grade_narrative_deterministic(normalized_pack, slide_spec)
