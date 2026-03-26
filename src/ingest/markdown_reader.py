"""Markdown 文档解析器。

将 Markdown 文档解析为结构化的中间表示，保留：
- 标题层级和嵌套关系
- 段落文本
- 列表项（有序和无序）
- 代码块
- 表格
- 引用块
- 元数据（如果有 YAML front matter）

这是来源理解层的第一步：结构化解析。
解析后的结构将传递给 LLM 进行深度理解。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class MarkdownBlock:
    """Markdown 文档中的一个内容块。"""
    block_type: str  # heading, paragraph, list, code, table, blockquote
    content: str  # 原始文本内容
    level: int = 0  # 标题级别（1-6），仅对 heading 有效
    language: str = ""  # 代码块语言，仅对 code 有效
    items: list[str] = field(default_factory=list)  # 列表项，仅对 list 有效
    rows: list[list[str]] = field(default_factory=list)  # 表格行，仅对 table 有效
    headers: list[str] = field(default_factory=list)  # 表格头，仅对 table 有效
    ordered: bool = False  # 是否有序列表


@dataclass
class MarkdownSection:
    """Markdown 文档中的一个章节（由标题划分）。"""
    heading: str
    level: int
    blocks: list[MarkdownBlock] = field(default_factory=list)

    @property
    def text(self) -> str:
        """将章节内所有块合并为纯文本。"""
        parts: list[str] = []
        for block in self.blocks:
            if block.block_type == "paragraph":
                parts.append(block.content)
            elif block.block_type == "list":
                for item in block.items:
                    parts.append(f"- {item}")
            elif block.block_type == "blockquote":
                parts.append(block.content)
            elif block.block_type == "code":
                parts.append(block.content)
            elif block.block_type == "table":
                if block.headers:
                    parts.append(" | ".join(block.headers))
                for row in block.rows:
                    parts.append(" | ".join(row))
        return "\n".join(parts)

    @property
    def paragraphs(self) -> list[str]:
        """提取所有段落文本。"""
        return [b.content for b in self.blocks if b.block_type == "paragraph"]

    @property
    def lists(self) -> list[list[str]]:
        """提取所有列表。"""
        return [b.items for b in self.blocks if b.block_type == "list"]

    @property
    def tables(self) -> list[dict]:
        """提取所有表格为 dict 列表。"""
        result = []
        for b in self.blocks:
            if b.block_type == "table":
                result.append({"headers": b.headers, "rows": b.rows})
        return result

    @property
    def code_blocks(self) -> list[dict]:
        """提取所有代码块。"""
        return [
            {"language": b.language, "content": b.content}
            for b in self.blocks
            if b.block_type == "code"
        ]


@dataclass
class MarkdownDocument:
    """解析后的 Markdown 文档。"""
    title: str = ""  # 文档标题（第一个 h1）
    metadata: dict = field(default_factory=dict)  # YAML front matter
    sections: list[MarkdownSection] = field(default_factory=list)
    preamble: list[MarkdownBlock] = field(default_factory=list)  # 标题前的内容

    @property
    def all_text(self) -> str:
        """获取文档的全部纯文本内容。"""
        parts: list[str] = []
        if self.title:
            parts.append(self.title)
        for block in self.preamble:
            if block.block_type == "paragraph":
                parts.append(block.content)
        for section in self.sections:
            parts.append(section.heading)
            parts.append(section.text)
        return "\n\n".join(part for part in parts if part)

    @property
    def section_count(self) -> int:
        return len(self.sections)

    @property
    def word_count(self) -> int:
        """粗略的字数统计（中文按字符计，英文按空格分词）。"""
        text = self.all_text
        # 中文字符数
        cjk_chars = len(re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf]', text))
        # 英文单词数（去掉中文后按空格分）
        non_cjk = re.sub(r'[\u4e00-\u9fff\u3400-\u4dbf]', ' ', text)
        english_words = len(non_cjk.split())
        return cjk_chars + english_words


# ---------- 解析器实现 ----------

_HEADING_RE = re.compile(r'^(#{1,6})\s+(.+)$')
_ORDERED_LIST_RE = re.compile(r'^\d+\.\s+(.+)$')
_UNORDERED_LIST_RE = re.compile(r'^[-*+]\s+(.+)$')
_CODE_FENCE_RE = re.compile(r'^```(\w*)$')
_TABLE_SEP_RE = re.compile(r'^\|?\s*[-:]+[-|:\s]*$')
_TABLE_ROW_RE = re.compile(r'^\|(.+)\|$')
_BLOCKQUOTE_RE = re.compile(r'^>\s*(.*)$')
_YAML_FENCE_RE = re.compile(r'^---\s*$')


def _parse_yaml_front_matter(lines: list[str]) -> tuple[dict, int]:
    """解析 YAML front matter，返回 (metadata_dict, 跳过的行数)。"""
    if not lines or not _YAML_FENCE_RE.match(lines[0]):
        return {}, 0

    end_idx = -1
    for i in range(1, len(lines)):
        if _YAML_FENCE_RE.match(lines[i]):
            end_idx = i
            break

    if end_idx < 0:
        return {}, 0

    metadata: dict = {}
    for line in lines[1:end_idx]:
        line = line.strip()
        if ':' in line:
            key, _, value = line.partition(':')
            key = key.strip()
            value = value.strip()
            if value:
                metadata[key] = value
    return metadata, end_idx + 1


def _parse_table(lines: list[str], start: int) -> tuple[MarkdownBlock, int]:
    """从 start 位置解析表格，返回 (block, 消耗的行数)。"""
    headers: list[str] = []
    rows: list[list[str]] = []

    # 第一行是表头
    header_line = lines[start].strip()
    if header_line.startswith('|') and header_line.endswith('|'):
        headers = [cell.strip() for cell in header_line[1:-1].split('|')]
    else:
        headers = [cell.strip() for cell in header_line.split('|')]

    consumed = 1

    # 第二行是分隔符
    if start + 1 < len(lines) and _TABLE_SEP_RE.match(lines[start + 1].strip()):
        consumed = 2
    else:
        # 不是有效表格
        return MarkdownBlock(block_type="paragraph", content=header_line), 1

    # 后续行是数据行
    idx = start + consumed
    while idx < len(lines):
        line = lines[idx].strip()
        if not line or (not line.startswith('|') and '|' not in line):
            break
        if line.startswith('|') and line.endswith('|'):
            cells = [cell.strip() for cell in line[1:-1].split('|')]
        else:
            cells = [cell.strip() for cell in line.split('|')]
        rows.append(cells)
        idx += 1
        consumed += 1

    content_parts = [" | ".join(headers)]
    for row in rows:
        content_parts.append(" | ".join(row))

    return MarkdownBlock(
        block_type="table",
        content="\n".join(content_parts),
        headers=headers,
        rows=rows,
    ), consumed


def parse_markdown(text: str) -> MarkdownDocument:
    """将 Markdown 文本解析为结构化的 MarkdownDocument。

    参数：
        text: Markdown 文本内容

    返回：
        MarkdownDocument 对象
    """
    lines = text.split('\n')
    doc = MarkdownDocument()

    # 解析 YAML front matter
    metadata, skip = _parse_yaml_front_matter(lines)
    doc.metadata = metadata
    lines = lines[skip:]

    current_section: MarkdownSection | None = None
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 空行跳过
        if not stripped:
            i += 1
            continue

        # 标题
        heading_match = _HEADING_RE.match(stripped)
        if heading_match:
            level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()

            if level == 1 and not doc.title:
                doc.title = heading_text
                i += 1
                # h1 后面的内容也归入一个 section
                current_section = MarkdownSection(heading=heading_text, level=level)
                doc.sections.append(current_section)
                continue

            current_section = MarkdownSection(heading=heading_text, level=level)
            doc.sections.append(current_section)
            i += 1
            continue

        # 代码块
        code_match = _CODE_FENCE_RE.match(stripped)
        if code_match:
            language = code_match.group(1)
            code_lines: list[str] = []
            i += 1
            while i < len(lines):
                if lines[i].strip().startswith('```'):
                    i += 1
                    break
                code_lines.append(lines[i])
                i += 1
            block = MarkdownBlock(
                block_type="code",
                content="\n".join(code_lines),
                language=language,
            )
            if current_section:
                current_section.blocks.append(block)
            else:
                doc.preamble.append(block)
            continue

        # 表格检测（当前行包含 | 且下一行是分隔符）
        if '|' in stripped and i + 1 < len(lines) and _TABLE_SEP_RE.match(lines[i + 1].strip()):
            table_block, consumed = _parse_table(lines, i)
            if current_section:
                current_section.blocks.append(table_block)
            else:
                doc.preamble.append(table_block)
            i += consumed
            continue

        # 引用块
        quote_match = _BLOCKQUOTE_RE.match(stripped)
        if quote_match:
            quote_lines: list[str] = []
            while i < len(lines):
                qm = _BLOCKQUOTE_RE.match(lines[i].strip())
                if qm:
                    quote_lines.append(qm.group(1))
                    i += 1
                else:
                    break
            block = MarkdownBlock(
                block_type="blockquote",
                content="\n".join(quote_lines),
            )
            if current_section:
                current_section.blocks.append(block)
            else:
                doc.preamble.append(block)
            continue

        # 有序列表
        ol_match = _ORDERED_LIST_RE.match(stripped)
        if ol_match:
            items: list[str] = []
            while i < len(lines):
                m = _ORDERED_LIST_RE.match(lines[i].strip())
                if m:
                    items.append(m.group(1))
                    i += 1
                else:
                    break
            block = MarkdownBlock(
                block_type="list",
                content="\n".join(f"{idx+1}. {item}" for idx, item in enumerate(items)),
                items=items,
                ordered=True,
            )
            if current_section:
                current_section.blocks.append(block)
            else:
                doc.preamble.append(block)
            continue

        # 无序列表
        ul_match = _UNORDERED_LIST_RE.match(stripped)
        if ul_match:
            items = []
            while i < len(lines):
                m = _UNORDERED_LIST_RE.match(lines[i].strip())
                if m:
                    items.append(m.group(1))
                    i += 1
                else:
                    break
            block = MarkdownBlock(
                block_type="list",
                content="\n".join(f"- {item}" for item in items),
                items=items,
                ordered=False,
            )
            if current_section:
                current_section.blocks.append(block)
            else:
                doc.preamble.append(block)
            continue

        # 普通段落（合并连续非空行）
        para_lines: list[str] = []
        while i < len(lines):
            l = lines[i].strip()
            if not l:
                i += 1
                break
            # 如果遇到其他结构化元素，停止段落收集
            if (_HEADING_RE.match(l) or _CODE_FENCE_RE.match(l) or
                _BLOCKQUOTE_RE.match(l) or _ORDERED_LIST_RE.match(l) or
                _UNORDERED_LIST_RE.match(l)):
                break
            # 表格检测
            if '|' in l and i + 1 < len(lines) and _TABLE_SEP_RE.match(lines[i + 1].strip()):
                break
            para_lines.append(l)
            i += 1

        if para_lines:
            block = MarkdownBlock(
                block_type="paragraph",
                content=" ".join(para_lines),
            )
            if current_section:
                current_section.blocks.append(block)
            else:
                doc.preamble.append(block)

    return doc
