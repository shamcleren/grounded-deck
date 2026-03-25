"""GroundedDeck PPTX 渲染器：将 slide spec 转换为可编辑的 .pptx 文件。

该模块消费 slide spec JSON 并使用 python-pptx 生成结构化的 PowerPoint 文件。
每种 layout_type 都有独立的渲染函数，确保输出可审计且可编辑。

设计原则：
- 零外部模板依赖，纯代码生成
- 每页 slide 保留 source bindings 和 speaker notes 以支持审计
- 所有文本框保持可编辑状态
- 专业蓝灰色调配色方案
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Cm, Emu, Pt

logger = logging.getLogger(__name__)

# ---------- 配色方案 ----------

COLOR_PRIMARY = RGBColor(0x1A, 0x56, 0xDB)      # 主色：深蓝
COLOR_ACCENT = RGBColor(0x2D, 0x8C, 0xF0)        # 辅助色：亮蓝
COLOR_DARK = RGBColor(0x1E, 0x29, 0x3B)           # 深色文字
COLOR_BODY = RGBColor(0x37, 0x41, 0x51)            # 正文文字
COLOR_MUTED = RGBColor(0x6B, 0x72, 0x80)           # 次要文字
COLOR_LIGHT_BG = RGBColor(0xF3, 0xF4, 0xF6)       # 浅色背景
COLOR_WHITE = RGBColor(0xFF, 0xFF, 0xFF)           # 白色
COLOR_BORDER = RGBColor(0xD1, 0xD5, 0xDB)          # 边框色
COLOR_HIGHLIGHT = RGBColor(0xDC, 0x26, 0x26)       # 高亮/强调色

# 布局专用颜色
COLOR_TIMELINE_ACCENT = RGBColor(0x05, 0x96, 0x69)   # 时间线：绿色
COLOR_COMPARISON_LEFT = RGBColor(0x1A, 0x56, 0xDB)    # 对比左：蓝色
COLOR_COMPARISON_RIGHT = RGBColor(0xDC, 0x26, 0x26)   # 对比右：红色
COLOR_PROCESS_ACCENT = RGBColor(0x7C, 0x3A, 0xED)     # 流程：紫色
COLOR_CHART_ACCENT = RGBColor(0xD9, 0x77, 0x06)       # 图表：橙色

# ---------- 字体配置 ----------

FONT_TITLE = "Microsoft YaHei"   # 微软雅黑作为中文标题字体
FONT_BODY = "Microsoft YaHei"    # 微软雅黑作为中文正文字体
FONT_MONO = "Consolas"           # 等宽字体

# ---------- 页面尺寸（宽屏 16:9） ----------

SLIDE_WIDTH = Cm(33.867)   # 13.333 inches
SLIDE_HEIGHT = Cm(19.05)   # 7.5 inches

# ---------- 常用边距和尺寸 ----------

MARGIN_LEFT = Cm(2.0)
MARGIN_TOP = Cm(2.0)
MARGIN_RIGHT = Cm(2.0)
CONTENT_WIDTH = Cm(29.867)  # SLIDE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT
TITLE_HEIGHT = Cm(2.5)
CONTENT_TOP = Cm(5.0)       # 标题区域下方


# ================================================================
# 辅助函数
# ================================================================


def _set_font(run, *, size: int = 14, bold: bool = False, color: RGBColor = COLOR_BODY, name: str = FONT_BODY) -> None:
    """设置 run 的字体属性。"""
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = name


def _add_textbox(
    slide,
    left: Emu,
    top: Emu,
    width: Emu,
    height: Emu,
    text: str,
    *,
    font_size: int = 14,
    bold: bool = False,
    color: RGBColor = COLOR_BODY,
    alignment: PP_ALIGN = PP_ALIGN.LEFT,
    font_name: str = FONT_BODY,
    word_wrap: bool = True,
) -> Any:
    """添加一个简单文本框。"""
    txbox = slide.shapes.add_textbox(left, top, width, height)
    tf = txbox.text_frame
    tf.word_wrap = word_wrap
    p = tf.paragraphs[0]
    p.alignment = alignment
    run = p.add_run()
    run.text = text
    _set_font(run, size=font_size, bold=bold, color=color, name=font_name)
    return txbox


def _add_title_block(slide, title: str, subtitle: str = "") -> None:
    """在 slide 顶部添加标题区域。"""
    # 标题
    _add_textbox(
        slide,
        MARGIN_LEFT,
        MARGIN_TOP,
        CONTENT_WIDTH,
        Cm(1.5),
        title,
        font_size=28,
        bold=True,
        color=COLOR_DARK,
        font_name=FONT_TITLE,
    )
    # 副标题
    if subtitle:
        _add_textbox(
            slide,
            MARGIN_LEFT,
            Cm(3.8),
            CONTENT_WIDTH,
            Cm(1.0),
            subtitle,
            font_size=14,
            color=COLOR_MUTED,
        )


def _add_speaker_notes(slide, slide_data: dict) -> None:
    """将 speaker notes 和 source bindings 写入备注区。"""
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame

    # speaker notes
    speaker_notes = slide_data.get("speaker_notes", "")
    if speaker_notes:
        tf.text = speaker_notes

    # source bindings（追加到备注末尾）
    bindings = slide_data.get("source_bindings", [])
    if bindings:
        p = tf.add_paragraph()
        p.text = ""
        p = tf.add_paragraph()
        p.text = f"[Source Bindings] {', '.join(bindings)}"

    # must_include_checks（追加到备注末尾）
    checks = slide_data.get("must_include_checks", [])
    if checks:
        p = tf.add_paragraph()
        p.text = f"[Must Include] {', '.join(checks)}"


def _add_rounded_rect(
    slide,
    left: Emu,
    top: Emu,
    width: Emu,
    height: Emu,
    fill_color: RGBColor = COLOR_LIGHT_BG,
    line_color: RGBColor | None = None,
) -> Any:
    """添加一个圆角矩形作为背景卡片。"""
    from pptx.enum.shapes import MSO_SHAPE

    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if line_color:
        shape.line.color.rgb = line_color
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    return shape


def _add_bullet_list(slide, left: Emu, top: Emu, width: Emu, height: Emu, items: list[str]) -> Any:
    """添加一个带要点符号的文本框。"""
    txbox = slide.shapes.add_textbox(left, top, width, height)
    tf = txbox.text_frame
    tf.word_wrap = True

    for i, item in enumerate(items):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(8)
        run = p.add_run()
        run.text = f"• {item}"
        _set_font(run, size=16, color=COLOR_BODY)

    return txbox


# ================================================================
# 布局渲染器
# ================================================================


def _render_cover(slide, slide_data: dict) -> None:
    """渲染 cover 布局：大标题 + 目标受众 + source count。"""
    # 背景色块
    _add_rounded_rect(slide, Cm(0), Cm(0), SLIDE_WIDTH, Cm(10), fill_color=COLOR_PRIMARY)

    # 主标题（白色大字）
    _add_textbox(
        slide,
        Cm(3.0),
        Cm(3.0),
        Cm(27.0),
        Cm(4.0),
        slide_data["title"],
        font_size=36,
        bold=True,
        color=COLOR_WHITE,
        font_name=FONT_TITLE,
        alignment=PP_ALIGN.LEFT,
    )

    # key_points 作为副信息
    key_points = slide_data.get("key_points", [])
    if key_points:
        subtitle_text = " | ".join(key_points)
        _add_textbox(
            slide,
            Cm(3.0),
            Cm(7.5),
            Cm(27.0),
            Cm(1.5),
            subtitle_text,
            font_size=16,
            color=RGBColor(0xBF, 0xDB, 0xFE),  # 浅蓝色
            alignment=PP_ALIGN.LEFT,
        )

    # 底部标签
    bindings = slide_data.get("source_bindings", [])
    _add_textbox(
        slide,
        Cm(3.0),
        Cm(11.5),
        Cm(27.0),
        Cm(1.0),
        f"GroundedDeck — {len(bindings)} grounded sources",
        font_size=12,
        color=COLOR_MUTED,
        alignment=PP_ALIGN.LEFT,
    )

    # topic overview（如果有）
    topics = []
    for ve in slide_data.get("visual_elements", []):
        if ve.get("type") == "topic-overview" and "topics" in ve:
            topics = ve["topics"]
            break
    if topics:
        topic_text = "  |  ".join(topics)
        _add_textbox(
            slide,
            Cm(3.0),
            Cm(13.0),
            Cm(27.0),
            Cm(1.5),
            topic_text,
            font_size=13,
            color=COLOR_BODY,
            alignment=PP_ALIGN.LEFT,
        )


def _render_summary(slide, slide_data: dict) -> None:
    """渲染 summary 布局：决策骨架，要点列表 + 来源标注 + claim-source 映射。"""
    _add_title_block(slide, slide_data["title"], slide_data.get("goal", ""))

    key_points = slide_data.get("key_points", [])
    if key_points:
        _add_bullet_list(
            slide,
            MARGIN_LEFT,
            CONTENT_TOP,
            CONTENT_WIDTH,
            Cm(10.0),
            key_points,
        )

    # claim-source-map 可视化（如果有）
    claim_entries = []
    for ve in slide_data.get("visual_elements", []):
        if ve.get("type") == "claim-source-map" and "entries" in ve:
            claim_entries = ve["entries"]
            break
    if claim_entries and not key_points:
        # 如果 key_points 为空但有 claim_entries，作为回退渲染
        items = [f"{e.get('claim', '')} [{e.get('source_binding', '')}]" for e in claim_entries]
        _add_bullet_list(
            slide,
            MARGIN_LEFT,
            CONTENT_TOP,
            CONTENT_WIDTH,
            Cm(10.0),
            items,
        )

    # 底部 source bindings 标签
    bindings = slide_data.get("source_bindings", [])
    if bindings:
        _add_textbox(
            slide,
            MARGIN_LEFT,
            Cm(16.5),
            CONTENT_WIDTH,
            Cm(1.0),
            f"Sources: {', '.join(bindings)}",
            font_size=10,
            color=COLOR_MUTED,
            alignment=PP_ALIGN.LEFT,
        )


def _render_timeline(slide, slide_data: dict) -> None:
    """渲染 timeline 布局：水平时间线 + 里程碑标注 + 事件描述。"""
    _add_title_block(slide, slide_data["title"], slide_data.get("goal", ""))

    # 提取 milestones 和 events
    milestones = []
    events = []
    for ve in slide_data.get("visual_elements", []):
        if ve.get("type") == "timeline" and "milestones" in ve:
            milestones = ve["milestones"]
            events = ve.get("events", [])
            break

    if not milestones:
        milestones = ["Start", "Middle", "End"]

    n = len(milestones)
    line_y = Cm(10.0)
    line_left = Cm(4.0)
    line_width = Cm(25.0)

    # 时间线主轴
    from pptx.enum.shapes import MSO_SHAPE

    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, line_left, line_y, line_width, Cm(0.15),
    )
    line.fill.solid()
    line.fill.fore_color.rgb = COLOR_TIMELINE_ACCENT
    line.line.fill.background()

    # 里程碑节点
    spacing = int(line_width) // max(n, 1)
    for i, ms in enumerate(milestones):
        cx = int(line_left) + spacing * i + spacing // 2
        # 圆形节点
        dot = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            Emu(cx - int(Cm(0.4))),
            line_y - Cm(0.4),
            Cm(0.8),
            Cm(0.95),
        )
        dot.fill.solid()
        dot.fill.fore_color.rgb = COLOR_TIMELINE_ACCENT
        dot.line.fill.background()

        # 标签
        _add_textbox(
            slide,
            Emu(cx - int(Cm(2.5))),
            line_y + Cm(1.0),
            Cm(5.0),
            Cm(1.5),
            str(ms),
            font_size=14,
            bold=True,
            color=COLOR_DARK,
            alignment=PP_ALIGN.CENTER,
        )

        # 事件描述（如果有）
        if i < len(events):
            event_text = str(events[i])
            # 去掉前缀年份（如 "2022: "）以避免重复
            if ":" in event_text:
                event_text = event_text.split(":", 1)[1].strip()
            _add_textbox(
                slide,
                Emu(cx - int(Cm(2.5))),
                line_y + Cm(2.3),
                Cm(5.0),
                Cm(2.0),
                event_text,
                font_size=10,
                color=COLOR_MUTED,
                alignment=PP_ALIGN.CENTER,
            )

    # key_points
    key_points = slide_data.get("key_points", [])
    if key_points:
        _add_textbox(
            slide,
            MARGIN_LEFT,
            Cm(13.5),
            CONTENT_WIDTH,
            Cm(3.0),
            key_points[0],
            font_size=14,
            color=COLOR_BODY,
            alignment=PP_ALIGN.CENTER,
        )


def _render_comparison(slide, slide_data: dict) -> None:
    """渲染 comparison 布局：左右双栏对比，带对比要点。"""
    _add_title_block(slide, slide_data["title"], slide_data.get("goal", ""))

    # 提取列名和列要点
    columns = []
    column_points: dict[str, list[str]] = {}
    for ve in slide_data.get("visual_elements", []):
        if ve.get("type") == "comparison-columns" and "columns" in ve:
            columns = ve["columns"]
            column_points = ve.get("column_points", {})
            break

    if len(columns) < 2:
        columns = ["Option A", "Option B"]

    col_width = Cm(13.5)
    gap = Cm(1.0)
    left_x = MARGIN_LEFT
    right_x = Emu(int(MARGIN_LEFT) + int(col_width) + int(gap))

    # 左侧卡片
    _add_rounded_rect(slide, left_x, CONTENT_TOP, col_width, Cm(11.0), fill_color=RGBColor(0xEF, 0xF6, 0xFF))
    # 左侧标题
    _add_textbox(
        slide,
        Emu(int(left_x) + int(Cm(1.0))),
        Emu(int(CONTENT_TOP) + int(Cm(0.5))),
        Cm(11.5),
        Cm(1.5),
        str(columns[0]),
        font_size=20,
        bold=True,
        color=COLOR_COMPARISON_LEFT,
        alignment=PP_ALIGN.CENTER,
    )

    # 左侧对比要点
    left_points = column_points.get(columns[0], [])
    if left_points:
        _add_bullet_list(
            slide,
            Emu(int(left_x) + int(Cm(0.8))),
            Emu(int(CONTENT_TOP) + int(Cm(2.5))),
            Cm(12.0),
            Cm(8.0),
            left_points[:3],
        )

    # 右侧卡片
    _add_rounded_rect(slide, right_x, CONTENT_TOP, col_width, Cm(11.0), fill_color=RGBColor(0xFE, 0xF2, 0xF2))
    # 右侧标题
    _add_textbox(
        slide,
        Emu(int(right_x) + int(Cm(1.0))),
        Emu(int(CONTENT_TOP) + int(Cm(0.5))),
        Cm(11.5),
        Cm(1.5),
        str(columns[1]),
        font_size=20,
        bold=True,
        color=COLOR_COMPARISON_RIGHT,
        alignment=PP_ALIGN.CENTER,
    )

    # 右侧对比要点
    right_points = column_points.get(columns[1], [])
    if right_points:
        _add_bullet_list(
            slide,
            Emu(int(right_x) + int(Cm(0.8))),
            Emu(int(CONTENT_TOP) + int(Cm(2.5))),
            Cm(12.0),
            Cm(8.0),
            right_points[:3],
        )

    # key_points 放在两栏中间底部
    key_points = slide_data.get("key_points", [])
    if key_points:
        _add_textbox(
            slide,
            MARGIN_LEFT,
            Cm(16.0),
            CONTENT_WIDTH,
            Cm(2.0),
            key_points[0],
            font_size=14,
            color=COLOR_BODY,
            alignment=PP_ALIGN.CENTER,
        )


def _render_process(slide, slide_data: dict) -> None:
    """渲染 process 布局：水平流程步骤（箭头连接）。"""
    _add_title_block(slide, slide_data["title"], slide_data.get("goal", ""))

    # 提取步骤数和步骤标签
    step_count = 1
    ve_step_labels: list[str] = []
    for ve in slide_data.get("visual_elements", []):
        if ve.get("type") == "process-flow":
            step_count = ve.get("steps", 1)
            ve_step_labels = ve.get("step_labels", [])
            break

    # 优先使用 visual_elements 中的 step_labels，回退到 key_points
    if ve_step_labels:
        step_labels = ve_step_labels[:step_count]
    else:
        key_points = slide_data.get("key_points", [])
        step_labels = key_points[:step_count] if key_points else [f"Step {i + 1}" for i in range(max(step_count, 1))]
        # 如果只有一个 key_point 且 steps > 1，拆分成句号分隔的片段
        if len(step_labels) == 1 and step_count > 1:
            parts = step_labels[0].replace("，", "、").split("、")
            step_labels = parts[:step_count]

    # 如果最终步骤标签仍然只有 1 个，但内容暗示多步骤，就按内容展示
    n = len(step_labels)
    if n == 0:
        n = 1
        step_labels = [""]

    from pptx.enum.shapes import MSO_SHAPE

    total_width = int(CONTENT_WIDTH)
    step_width = Cm(6.0)
    arrow_width = Cm(1.5)

    # 计算总内容宽度
    content_needed = int(step_width) * n + int(arrow_width) * max(n - 1, 0)
    start_x = int(MARGIN_LEFT) + (total_width - content_needed) // 2

    step_y = Cm(8.0)
    step_height = Cm(5.0)

    for i, label in enumerate(step_labels):
        sx = start_x + i * (int(step_width) + int(arrow_width))

        # 步骤卡片
        card = _add_rounded_rect(
            slide, Emu(sx), step_y, step_width, step_height,
            fill_color=COLOR_PROCESS_ACCENT if i == n - 1 else COLOR_LIGHT_BG,
            line_color=COLOR_PROCESS_ACCENT,
        )

        # 步骤序号
        _add_textbox(
            slide,
            Emu(sx + int(Cm(0.5))),
            Emu(int(step_y) + int(Cm(0.5))),
            Cm(5.0),
            Cm(1.2),
            f"Step {i + 1}",
            font_size=12,
            bold=True,
            color=COLOR_WHITE if i == n - 1 else COLOR_PROCESS_ACCENT,
            alignment=PP_ALIGN.CENTER,
        )

        # 步骤内容
        text_color = COLOR_WHITE if i == n - 1 else COLOR_BODY
        _add_textbox(
            slide,
            Emu(sx + int(Cm(0.3))),
            Emu(int(step_y) + int(Cm(2.0))),
            Cm(5.4),
            Cm(2.5),
            label,
            font_size=11,
            color=text_color,
            alignment=PP_ALIGN.CENTER,
        )

        # 箭头（不是最后一个步骤时）
        if i < n - 1:
            arrow_x = sx + int(step_width)
            arrow = slide.shapes.add_shape(
                MSO_SHAPE.RIGHT_ARROW,
                Emu(arrow_x),
                Emu(int(step_y) + int(step_height) // 2 - int(Cm(0.4))),
                arrow_width,
                Cm(0.8),
            )
            arrow.fill.solid()
            arrow.fill.fore_color.rgb = COLOR_PROCESS_ACCENT
            arrow.line.fill.background()


def _render_chart(slide, slide_data: dict) -> None:
    """渲染 chart 布局：指标卡片 + 关键数字展示 + 上下文标签。"""
    _add_title_block(slide, slide_data["title"], slide_data.get("goal", ""))

    # 提取指标和标签
    metrics = []
    metric_labels = []
    for ve in slide_data.get("visual_elements", []):
        if ve.get("type") == "metric-cards" and "metrics" in ve:
            metrics = ve["metrics"]
            metric_labels = ve.get("labels", [])
            break

    if not metrics:
        metrics = ["—"]

    n = len(metrics)
    card_width = Cm(8.0)
    card_height = Cm(6.0)
    gap = Cm(2.0)

    total_width = int(card_width) * n + int(gap) * max(n - 1, 0)
    start_x = int(MARGIN_LEFT) + (int(CONTENT_WIDTH) - total_width) // 2
    card_y = Cm(7.0)

    for i, metric in enumerate(metrics):
        cx = start_x + i * (int(card_width) + int(gap))

        # 卡片背景
        _add_rounded_rect(
            slide, Emu(cx), card_y, card_width, card_height,
            fill_color=COLOR_LIGHT_BG,
            line_color=COLOR_CHART_ACCENT,
        )

        # 指标值（大数字）
        _add_textbox(
            slide,
            Emu(cx + int(Cm(0.5))),
            Emu(int(card_y) + int(Cm(1.0))),
            Cm(7.0),
            Cm(3.0),
            str(metric),
            font_size=36,
            bold=True,
            color=COLOR_CHART_ACCENT,
            alignment=PP_ALIGN.CENTER,
            font_name=FONT_TITLE,
        )

        # 指标标签（使用上下文标签如果有）
        label_text = metric_labels[i] if i < len(metric_labels) else f"Metric {i + 1}"
        _add_textbox(
            slide,
            Emu(cx + int(Cm(0.5))),
            Emu(int(card_y) + int(Cm(4.0))),
            Cm(7.0),
            Cm(1.5),
            label_text,
            font_size=10,
            color=COLOR_MUTED,
            alignment=PP_ALIGN.CENTER,
        )

    # key_points
    key_points = slide_data.get("key_points", [])
    if key_points:
        _add_textbox(
            slide,
            MARGIN_LEFT,
            Cm(14.5),
            CONTENT_WIDTH,
            Cm(3.0),
            key_points[0],
            font_size=14,
            color=COLOR_BODY,
            alignment=PP_ALIGN.CENTER,
        )


def _render_section(slide, slide_data: dict) -> None:
    """渲染 section 布局：章节分隔页。"""
    # 背景色块
    _add_rounded_rect(slide, Cm(0), Cm(6.0), SLIDE_WIDTH, Cm(7.0), fill_color=COLOR_PRIMARY)

    # 标题
    _add_textbox(
        slide,
        Cm(3.0),
        Cm(7.5),
        Cm(27.0),
        Cm(3.0),
        slide_data["title"],
        font_size=32,
        bold=True,
        color=COLOR_WHITE,
        alignment=PP_ALIGN.CENTER,
        font_name=FONT_TITLE,
    )

    # 目标描述
    goal = slide_data.get("goal", "")
    if goal:
        _add_textbox(
            slide,
            Cm(3.0),
            Cm(10.5),
            Cm(27.0),
            Cm(1.5),
            goal,
            font_size=16,
            color=RGBColor(0xBF, 0xDB, 0xFE),
            alignment=PP_ALIGN.CENTER,
        )


# 布局路由表
_LAYOUT_RENDERERS: dict[str, Any] = {
    "cover": _render_cover,
    "summary": _render_summary,
    "timeline": _render_timeline,
    "comparison": _render_comparison,
    "process": _render_process,
    "chart": _render_chart,
    "section": _render_section,
}


# ================================================================
# 公开 API
# ================================================================


def render_slide_spec_to_pptx(
    slide_spec: dict,
    output_path: str | Path,
) -> Path:
    """将 slide spec 渲染为可编辑的 .pptx 文件。

    参数：
        slide_spec: 符合 slide-spec schema 的 dict
        output_path: 输出 .pptx 文件路径

    返回：
        输出文件的 Path 对象

    异常：
        ValueError: slide_spec 缺少必要字段
        KeyError: slide 使用了不支持的 layout_type
    """
    output_path = Path(output_path)

    if "slides" not in slide_spec:
        raise ValueError("slide_spec must contain a 'slides' list")
    if not slide_spec["slides"]:
        raise ValueError("slide_spec must contain at least one slide")

    prs = Presentation()
    prs.slide_width = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT

    # 使用空白布局
    blank_layout = prs.slide_layouts[6]  # 空白 layout

    for slide_data in slide_spec["slides"]:
        layout_type = slide_data.get("layout_type", "summary")
        renderer = _LAYOUT_RENDERERS.get(layout_type)

        if renderer is None:
            logger.warning(
                "unsupported layout_type '%s' for slide '%s', falling back to summary",
                layout_type,
                slide_data.get("slide_id", "unknown"),
            )
            renderer = _render_summary

        slide = prs.slides.add_slide(blank_layout)
        renderer(slide, slide_data)
        _add_speaker_notes(slide, slide_data)

    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(output_path))

    logger.info("rendered %d slides to %s", len(slide_spec["slides"]), output_path)
    return output_path


def get_supported_layouts() -> tuple[str, ...]:
    """返回渲染器支持的所有 layout_type。"""
    return tuple(sorted(_LAYOUT_RENDERERS.keys()))
