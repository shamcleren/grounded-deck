"""GroundedDeck 主题样式系统：为 PPTX 渲染器提供可切换的配色方案。

每个主题定义了完整的颜色槽位，渲染器通过主题对象获取颜色而非硬编码。
支持内置主题和自定义主题扩展。

内置主题：
- professional-blue: 专业蓝灰色调（默认，与原有配色一致）
- forest-green: 自然绿色调，适合环保/可持续发展主题
- warm-sunset: 暖色调，适合创意/营销主题
- minimal-gray: 极简灰色调，适合技术/数据主题
- ocean-teal: 海洋青色调，适合科技/创新主题
"""

from __future__ import annotations

from dataclasses import dataclass

from pptx.dml.color import RGBColor


@dataclass(frozen=True)
class SlideTheme:
    """PPTX 渲染主题，定义完整的颜色槽位。"""

    name: str
    display_name: str

    # 主色调
    primary: RGBColor
    accent: RGBColor

    # 文字颜色
    text_dark: RGBColor
    text_body: RGBColor
    text_muted: RGBColor
    text_white: RGBColor

    # 背景颜色
    bg_light: RGBColor
    bg_white: RGBColor

    # 边框和高亮
    border: RGBColor
    highlight: RGBColor

    # 布局专用颜色
    timeline_accent: RGBColor
    comparison_left: RGBColor
    comparison_right: RGBColor
    process_accent: RGBColor
    chart_accent: RGBColor

    # cover 副标题颜色
    cover_subtitle: RGBColor

    # 表格交替行背景
    table_alt_left: RGBColor
    table_alt_right: RGBColor


# ── 内置主题定义 ──────────────────────────────────────────────────────


THEME_PROFESSIONAL_BLUE = SlideTheme(
    name="professional-blue",
    display_name="Professional Blue",
    primary=RGBColor(0x1A, 0x56, 0xDB),
    accent=RGBColor(0x2D, 0x8C, 0xF0),
    text_dark=RGBColor(0x1E, 0x29, 0x3B),
    text_body=RGBColor(0x37, 0x41, 0x51),
    text_muted=RGBColor(0x6B, 0x72, 0x80),
    text_white=RGBColor(0xFF, 0xFF, 0xFF),
    bg_light=RGBColor(0xF3, 0xF4, 0xF6),
    bg_white=RGBColor(0xFF, 0xFF, 0xFF),
    border=RGBColor(0xD1, 0xD5, 0xDB),
    highlight=RGBColor(0xDC, 0x26, 0x26),
    timeline_accent=RGBColor(0x05, 0x96, 0x69),
    comparison_left=RGBColor(0x1A, 0x56, 0xDB),
    comparison_right=RGBColor(0xDC, 0x26, 0x26),
    process_accent=RGBColor(0x7C, 0x3A, 0xED),
    chart_accent=RGBColor(0xD9, 0x77, 0x06),
    cover_subtitle=RGBColor(0xBF, 0xDB, 0xFE),
    table_alt_left=RGBColor(0xEF, 0xF6, 0xFF),
    table_alt_right=RGBColor(0xFE, 0xF2, 0xF2),
)

THEME_FOREST_GREEN = SlideTheme(
    name="forest-green",
    display_name="Forest Green",
    primary=RGBColor(0x16, 0x5B, 0x33),
    accent=RGBColor(0x22, 0xC5, 0x5E),
    text_dark=RGBColor(0x14, 0x53, 0x2D),
    text_body=RGBColor(0x37, 0x41, 0x51),
    text_muted=RGBColor(0x6B, 0x72, 0x80),
    text_white=RGBColor(0xFF, 0xFF, 0xFF),
    bg_light=RGBColor(0xF0, 0xFD, 0xF4),
    bg_white=RGBColor(0xFF, 0xFF, 0xFF),
    border=RGBColor(0xBB, 0xF7, 0xD0),
    highlight=RGBColor(0xEA, 0xB3, 0x08),
    timeline_accent=RGBColor(0x05, 0x96, 0x69),
    comparison_left=RGBColor(0x16, 0x5B, 0x33),
    comparison_right=RGBColor(0xEA, 0xB3, 0x08),
    process_accent=RGBColor(0x0D, 0x94, 0x88),
    chart_accent=RGBColor(0x16, 0xA3, 0x4A),
    cover_subtitle=RGBColor(0xBB, 0xF7, 0xD0),
    table_alt_left=RGBColor(0xDC, 0xFC, 0xE7),
    table_alt_right=RGBColor(0xFE, 0xF9, 0xC3),
)

THEME_WARM_SUNSET = SlideTheme(
    name="warm-sunset",
    display_name="Warm Sunset",
    primary=RGBColor(0xC2, 0x41, 0x0C),
    accent=RGBColor(0xF9, 0x73, 0x16),
    text_dark=RGBColor(0x43, 0x1A, 0x07),
    text_body=RGBColor(0x37, 0x41, 0x51),
    text_muted=RGBColor(0x6B, 0x72, 0x80),
    text_white=RGBColor(0xFF, 0xFF, 0xFF),
    bg_light=RGBColor(0xFF, 0xF7, 0xED),
    bg_white=RGBColor(0xFF, 0xFF, 0xFF),
    border=RGBColor(0xFE, 0xD7, 0xAA),
    highlight=RGBColor(0xDC, 0x26, 0x26),
    timeline_accent=RGBColor(0xEA, 0x58, 0x0C),
    comparison_left=RGBColor(0xC2, 0x41, 0x0C),
    comparison_right=RGBColor(0x7C, 0x3A, 0xED),
    process_accent=RGBColor(0xDB, 0x27, 0x77),
    chart_accent=RGBColor(0xD9, 0x77, 0x06),
    cover_subtitle=RGBColor(0xFE, 0xD7, 0xAA),
    table_alt_left=RGBColor(0xFF, 0xED, 0xD5),
    table_alt_right=RGBColor(0xF5, 0xF3, 0xFF),
)

THEME_MINIMAL_GRAY = SlideTheme(
    name="minimal-gray",
    display_name="Minimal Gray",
    primary=RGBColor(0x37, 0x41, 0x51),
    accent=RGBColor(0x6B, 0x72, 0x80),
    text_dark=RGBColor(0x11, 0x18, 0x27),
    text_body=RGBColor(0x37, 0x41, 0x51),
    text_muted=RGBColor(0x9C, 0xA3, 0xAF),
    text_white=RGBColor(0xFF, 0xFF, 0xFF),
    bg_light=RGBColor(0xF9, 0xFA, 0xFB),
    bg_white=RGBColor(0xFF, 0xFF, 0xFF),
    border=RGBColor(0xE5, 0xE7, 0xEB),
    highlight=RGBColor(0xEF, 0x44, 0x44),
    timeline_accent=RGBColor(0x4B, 0x55, 0x63),
    comparison_left=RGBColor(0x37, 0x41, 0x51),
    comparison_right=RGBColor(0x9C, 0xA3, 0xAF),
    process_accent=RGBColor(0x4B, 0x55, 0x63),
    chart_accent=RGBColor(0x37, 0x41, 0x51),
    cover_subtitle=RGBColor(0xD1, 0xD5, 0xDB),
    table_alt_left=RGBColor(0xF3, 0xF4, 0xF6),
    table_alt_right=RGBColor(0xF9, 0xFA, 0xFB),
)

THEME_OCEAN_TEAL = SlideTheme(
    name="ocean-teal",
    display_name="Ocean Teal",
    primary=RGBColor(0x0F, 0x76, 0x6E),
    accent=RGBColor(0x14, 0xB8, 0xA6),
    text_dark=RGBColor(0x13, 0x4E, 0x4A),
    text_body=RGBColor(0x37, 0x41, 0x51),
    text_muted=RGBColor(0x6B, 0x72, 0x80),
    text_white=RGBColor(0xFF, 0xFF, 0xFF),
    bg_light=RGBColor(0xF0, 0xFD, 0xFA),
    bg_white=RGBColor(0xFF, 0xFF, 0xFF),
    border=RGBColor(0x99, 0xF6, 0xE4),
    highlight=RGBColor(0xF5, 0x9E, 0x0B),
    timeline_accent=RGBColor(0x0D, 0x94, 0x88),
    comparison_left=RGBColor(0x0F, 0x76, 0x6E),
    comparison_right=RGBColor(0xF5, 0x9E, 0x0B),
    process_accent=RGBColor(0x06, 0x69, 0xA2),
    chart_accent=RGBColor(0x0E, 0xA5, 0xE9),
    cover_subtitle=RGBColor(0x99, 0xF6, 0xE4),
    table_alt_left=RGBColor(0xCC, 0xFB, 0xF1),
    table_alt_right=RGBColor(0xFE, 0xF3, 0xC7),
)


# ── 主题注册表 ────────────────────────────────────────────────────────

BUILTIN_THEMES: dict[str, SlideTheme] = {
    "professional-blue": THEME_PROFESSIONAL_BLUE,
    "forest-green": THEME_FOREST_GREEN,
    "warm-sunset": THEME_WARM_SUNSET,
    "minimal-gray": THEME_MINIMAL_GRAY,
    "ocean-teal": THEME_OCEAN_TEAL,
}

DEFAULT_THEME_NAME = "professional-blue"


def get_theme(name: str | None = None) -> SlideTheme:
    """根据名称获取主题，默认返回 professional-blue。

    参数：
        name: 主题名称，None 或空字符串返回默认主题

    返回：
        SlideTheme 实例

    异常：
        ValueError: 主题名称不存在
    """
    if not name:
        return BUILTIN_THEMES[DEFAULT_THEME_NAME]
    if name not in BUILTIN_THEMES:
        available = ", ".join(sorted(BUILTIN_THEMES.keys()))
        raise ValueError(f"unknown theme '{name}', available themes: {available}")
    return BUILTIN_THEMES[name]


def list_themes() -> list[str]:
    """返回所有可用主题名称列表。"""
    return sorted(BUILTIN_THEMES.keys())
