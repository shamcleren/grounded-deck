"""来源摄取模块：将原始文档转换为 GroundedDeck 内部 source pack 格式。

支持的格式：
- Markdown (.md)
- 更多格式将逐步添加（PDF、DOCX 等）
"""

from src.ingest.markdown_reader import parse_markdown, MarkdownDocument
from src.ingest.normalize import normalize_source_pack
from src.ingest.source_understanding import (
    understand_source,
    understand_source_deterministic,
    IngestConfig,
)

__all__ = [
    "parse_markdown",
    "MarkdownDocument",
    "normalize_source_pack",
    "understand_source",
    "understand_source_deterministic",
    "IngestConfig",
]
