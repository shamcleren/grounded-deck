"""视觉形式选择器：根据 source unit 的内容结构自动选择合适的 slide 布局和视觉元素。

该模块将内容理解映射到可编辑的视觉结构，是架构中 planner -> visual selector -> slide spec 链路的核心一环。
支持确定性规则推断和未来 provider-backed 推断两种模式。
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Callable

logger = logging.getLogger(__name__)


# ---------- 支持的布局类型常量 ----------

LAYOUT_TIMELINE = "timeline"
LAYOUT_COMPARISON = "comparison"
LAYOUT_PROCESS = "process"
LAYOUT_CHART = "chart"
LAYOUT_SUMMARY = "summary"
LAYOUT_COVER = "cover"

ALL_CONTENT_LAYOUTS = (
    LAYOUT_TIMELINE,
    LAYOUT_COMPARISON,
    LAYOUT_PROCESS,
    LAYOUT_CHART,
    LAYOUT_SUMMARY,
)

# 模型布局回调类型：接受 unit dict，返回 layout_type 字符串
ModelLayoutCallback = Callable[[dict], str]


# ---------- 布局推断结果 ----------

@dataclass(frozen=True)
class LayoutSelection:
    """视觉形式选择结果，包含推断出的布局类型和置信度信号。"""

    layout_type: str
    confidence: str = "rule-based"  # rule-based | model-assisted
    matched_signals: list[str] = field(default_factory=list)


# ---------- 视觉元素构建 ----------

def unique_preserving_order(values: list[str]) -> list[str]:
    """去重但保持原始顺序。"""
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def infer_layout_type(unit: dict) -> LayoutSelection:
    """基于规则推断 source unit 对应的最佳 slide 布局类型。

    规则优先级：
    1. 包含 "vs" / "对比" / "差异" -> comparison
    2. 包含 "路径" / "步骤" / "进入" / "落地" -> process
    3. 包含 "时间线" / "阶段" / 年份数字 -> timeline
    4. 包含 "成本" / "利润" / "指标" / "份额" / 百分比或数字 -> chart
    5. 其他 -> summary
    """
    text = f'{unit["section_heading"]} {unit["text"]}'.lower()
    signals: list[str] = []

    # comparison 信号
    comparison_keywords = ("vs", "对比", "差异")
    for kw in comparison_keywords:
        if kw in text:
            signals.append(f"keyword:{kw}")
    if signals:
        return LayoutSelection(
            layout_type=LAYOUT_COMPARISON,
            matched_signals=signals,
        )

    # process 信号
    process_keywords = ("路径", "步骤", "进入", "落地")
    for kw in process_keywords:
        if kw in text:
            signals.append(f"keyword:{kw}")
    if signals:
        return LayoutSelection(
            layout_type=LAYOUT_PROCESS,
            matched_signals=signals,
        )

    # timeline 信号
    timeline_keywords = ("时间线", "阶段")
    for kw in timeline_keywords:
        if kw in text:
            signals.append(f"keyword:{kw}")
    year_matches = re.findall(r"\b20\d{2}\b", text)
    if year_matches:
        signals.append(f"year_refs:{','.join(unique_preserving_order(year_matches))}")
    if signals:
        return LayoutSelection(
            layout_type=LAYOUT_TIMELINE,
            matched_signals=signals,
        )

    # chart 信号
    chart_keywords = ("成本", "利润", "指标", "份额")
    for kw in chart_keywords:
        if kw in text:
            signals.append(f"keyword:{kw}")
    if "%" in text:
        signals.append("symbol:%")
    if not signals and re.search(r"\d", text):
        signals.append("contains_digits")
    if signals:
        return LayoutSelection(
            layout_type=LAYOUT_CHART,
            matched_signals=signals,
        )

    # 默认 summary
    return LayoutSelection(
        layout_type=LAYOUT_SUMMARY,
        matched_signals=["fallback:no_signal_matched"],
    )


def _extract_comparison_points(text: str, columns: list[str]) -> dict[str, list[str]]:
    """从文本中提取每个对比列的要点。

    策略：按句号/分号拆分，将包含列名的片段归入对应列。
    """
    points: dict[str, list[str]] = {col: [] for col in columns}
    fragments = re.split(r"[；;。]", text)
    for frag in fragments:
        frag = frag.strip()
        if not frag:
            continue
        for col in columns:
            if col in frag and frag not in points[col]:
                points[col].append(frag)
                break
    return points


def _extract_process_steps(text: str) -> list[str]:
    """从文本中提取流程步骤描述。

    策略：识别 "先...再..." / "第一步...第二步..." / 逗号分隔的动作序列。
    """
    # 先...再... 模式
    parts = re.split(r"(?:先|再|然后|接着|最后|随后)", text)
    if len(parts) >= 3:
        # parts[0] 是分隔符前的引导语（通常是标题），跳过它
        steps = [p.strip().rstrip("，,。.；;、") for p in parts[1:] if p.strip()]
        if len(steps) >= 2:
            return steps[:5]

    # 逗号分隔的动作片段
    parts = re.split(r"[，,]", text)
    steps = [p.strip().rstrip("。.；;") for p in parts if p.strip() and len(p.strip()) > 4]
    if len(steps) >= 2:
        return steps[:5]

    return steps[:1] if steps else []


def _extract_metric_labels(text: str, metrics: list[str]) -> list[str]:
    """为提取的数值指标匹配文本上下文标签。

    策略：找到指标在文本中的位置，取其前后若干字符作为标签。
    """
    labels: list[str] = []
    for metric in metrics:
        idx = text.find(metric)
        if idx < 0:
            labels.append(metric)
            continue
        # 取指标前后的上下文（最多15字符）
        start = max(0, idx - 15)
        end = min(len(text), idx + len(metric) + 15)
        context = text[start:end].strip()
        labels.append(context)
    return labels


def _extract_milestone_events(text: str, milestones: list[str]) -> list[str]:
    """为时间线里程碑提取事件描述。

    策略：找到年份在文本中的位置，取其后方的描述片段。
    """
    events: list[str] = []
    for ms in milestones:
        idx = text.find(ms)
        if idx < 0:
            events.append(ms)
            continue
        # 取年份后到下一个年份或句号的内容
        after = text[idx + len(ms):]
        # 截取到下一个年份、句号或文本结束
        end_match = re.search(r"20\d{2}|[。;；]", after)
        event_text = after[:end_match.start()].strip() if end_match else after.strip()
        event_text = event_text.lstrip(" 年，,").rstrip("，,")
        if event_text:
            events.append(f"{ms}: {event_text}")
        else:
            events.append(ms)
    return events


def build_visual_elements(layout_type: str, unit: dict) -> list[dict]:
    """根据布局类型和 source unit 内容构建可编辑的视觉元素描述。

    每种布局类型都会从 unit 的 text/claims 中提取 source-grounded 的结构化内容：
    - timeline: milestones + 事件描述
    - comparison: columns + 每列对比要点
    - process: 步骤描述 + 步骤数
    - chart: metrics + 上下文标签
    - summary/默认: bullet-list
    """
    text = unit.get("text", "")

    if layout_type == LAYOUT_TIMELINE:
        milestones = unique_preserving_order(
            re.findall(r"\b(20\d{2})\b", text)
        )
        milestone_events = _extract_milestone_events(text, milestones[:4])
        return [{"type": "timeline", "milestones": milestones[:4], "events": milestone_events}]

    if layout_type == LAYOUT_COMPARISON:
        columns: list[str] = []
        for label in ("欧洲", "东南亚"):
            if label in text and label not in columns:
                columns.append(label)
        if not columns:
            columns = ["Option A", "Option B"]
        column_points = _extract_comparison_points(text, columns)
        return [{"type": "comparison-columns", "columns": columns, "column_points": column_points}]

    if layout_type == LAYOUT_PROCESS:
        steps = _extract_process_steps(text)
        return [{"type": "process-flow", "steps": max(1, len(steps)), "step_labels": steps}]

    if layout_type == LAYOUT_CHART:
        metrics = unique_preserving_order(
            re.findall(r"\d+%|\d+\.\d+%|\d+", text)
        )
        metric_labels = _extract_metric_labels(text, metrics[:4])
        return [{"type": "metric-cards", "metrics": metrics[:4], "labels": metric_labels}]

    return [{"type": "bullet-list"}]


def model_assisted_infer_layout_type(
    unit: dict,
    callback: ModelLayoutCallback | None = None,
) -> LayoutSelection:
    """模型辅助布局推断：优先使用 provider callback，回退到规则引擎。

    工作流程：
    1. 始终先运行规则引擎获取 baseline 推断
    2. 如果 callback 为 None，直接返回规则结果
    3. 如果 callback 可用，调用它获取模型建议
    4. 模型建议有效（在 ALL_CONTENT_LAYOUTS 中）→ 返回模型结果，confidence="model-assisted"
    5. 模型建议无效或抛出异常 → 回退到规则结果

    无论最终选择哪个，都会在 matched_signals 中记录两种推断的对比信息。
    """
    rule_selection = infer_layout_type(unit)

    if callback is None:
        return rule_selection

    try:
        model_layout = callback(unit)
    except Exception as exc:  # noqa: BLE001 – 回调可能因网络/API/解析等任意原因失败
        logger.warning(
            "model layout callback failed for unit %s, falling back to rule-based: %s",
            unit.get("unit_id", "unknown"),
            exc,
        )
        return LayoutSelection(
            layout_type=rule_selection.layout_type,
            confidence="rule-based",
            matched_signals=[
                *rule_selection.matched_signals,
                f"model_callback_error:{type(exc).__name__}",
            ],
        )

    if model_layout not in ALL_CONTENT_LAYOUTS:
        logger.warning(
            "model suggested invalid layout '%s' for unit %s, falling back to rule-based '%s'",
            model_layout,
            unit.get("unit_id", "unknown"),
            rule_selection.layout_type,
        )
        return LayoutSelection(
            layout_type=rule_selection.layout_type,
            confidence="rule-based",
            matched_signals=[
                *rule_selection.matched_signals,
                f"model_invalid_layout:{model_layout}",
            ],
        )

    # 模型建议有效 → 使用模型结果
    agreement = "agree" if model_layout == rule_selection.layout_type else "disagree"
    return LayoutSelection(
        layout_type=model_layout,
        confidence="model-assisted",
        matched_signals=[
            f"model_layout:{model_layout}",
            f"rule_layout:{rule_selection.layout_type}",
            f"model_rule_{agreement}",
        ],
    )


def select_visual_form(
    unit: dict,
    *,
    layout_callback: ModelLayoutCallback | None = None,
) -> dict:
    """对单个 source unit 执行完整的视觉形式选择，返回布局和视觉元素。

    这是外部调用的主入口，组合了布局推断和 build_visual_elements。
    当提供 layout_callback 时使用 model-assisted 推断，否则使用纯规则推断。
    """
    selection = model_assisted_infer_layout_type(unit, callback=layout_callback)
    elements = build_visual_elements(selection.layout_type, unit)
    return {
        "layout_type": selection.layout_type,
        "visual_elements": elements,
        "confidence": selection.confidence,
        "matched_signals": selection.matched_signals,
    }


# ---------- 模型输出验证 ----------

@dataclass(frozen=True)
class LayoutValidationItem:
    """单个 unit 的布局验证结果。"""

    unit_id: str
    rule_layout: str
    model_layout: str | None
    matched: bool
    matched_signals: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class LayoutValidationReport:
    """模型生成 slide spec 的布局验证报告。"""

    items: list[LayoutValidationItem]

    @property
    def matched_count(self) -> int:
        return sum(1 for item in self.items if item.matched)

    @property
    def mismatched_count(self) -> int:
        return sum(1 for item in self.items if not item.matched)

    @property
    def total_count(self) -> int:
        return len(self.items)

    @property
    def match_ratio(self) -> float:
        return round(self.matched_count / max(1, self.total_count), 2)

    @property
    def all_matched(self) -> bool:
        return self.mismatched_count == 0

    @property
    def mismatches(self) -> list[LayoutValidationItem]:
        return [item for item in self.items if not item.matched]

    def as_grader_hint(self) -> str:
        """生成可注入到 grader prompt 中的验证摘要。"""
        if self.all_matched:
            return (
                f"Visual selector rule-based validation: all {self.total_count} unit layouts "
                f"match rule-based expectations ({self.match_ratio} match ratio)."
            )
        lines = [
            f"Visual selector rule-based validation: {self.matched_count}/{self.total_count} "
            f"unit layouts match ({self.match_ratio} match ratio).",
            "Mismatches detected by rule engine:",
        ]
        for item in self.mismatches:
            lines.append(
                f"  - {item.unit_id}: rule expects '{item.rule_layout}', "
                f"model produced '{item.model_layout or 'missing'}' "
                f"(signals: {', '.join(item.matched_signals)})"
            )
        return "\n".join(lines)


def validate_model_layouts(
    normalized_pack: dict,
    slide_spec: dict,
) -> LayoutValidationReport:
    """对比模型生成的 slide spec 中每个 unit-backed slide 的布局与规则推断结果。

    用于在 OpenAI-compatible provider 路径中作为 post-validation 层，
    让 grader 和开发者知道模型选择和规则引擎的一致程度。
    """
    unit_by_id = {u["unit_id"]: u for u in normalized_pack.get("source_units", [])}

    # 构建 slide lookup：只关注恰好绑定单个 unit 的 content slide
    slide_by_unit: dict[str, dict] = {}
    for slide in slide_spec.get("slides", []):
        checks = slide.get("must_include_checks", [])
        if len(checks) == 1 and checks[0] in unit_by_id:
            slide_by_unit[checks[0]] = slide

    items: list[LayoutValidationItem] = []
    for unit_id, unit in unit_by_id.items():
        selection = infer_layout_type(unit)
        slide = slide_by_unit.get(unit_id)
        model_layout = slide["layout_type"] if slide else None
        items.append(
            LayoutValidationItem(
                unit_id=unit_id,
                rule_layout=selection.layout_type,
                model_layout=model_layout,
                matched=(model_layout == selection.layout_type),
                matched_signals=list(selection.matched_signals),
            )
        )

    return LayoutValidationReport(items=items)
