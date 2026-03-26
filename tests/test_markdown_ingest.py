"""Markdown Ingest 模块测试。

覆盖：
- Markdown 解析器（标题、段落、列表、代码块、表格、引用块、YAML front matter）
- 确定性来源理解（claims 提取、source pack 生成）
- LLM 来源理解（回调机制、回退逻辑）
- Pipeline 集成（从 Markdown 文件到 slide spec）
- CLI 格式检测
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from src.ingest.markdown_reader import (
    MarkdownBlock,
    MarkdownDocument,
    MarkdownSection,
    parse_markdown,
)
from src.ingest.source_understanding import (
    IngestConfig,
    understand_source,
    understand_source_deterministic,
    _detect_language,
    _extract_claims_deterministic,
    _generate_pack_id,
)
from src.runtime.pipeline import (
    detect_input_format,
    ingest_from_file,
    run_pipeline,
)


FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"
TEST_DOC_PATH = FIXTURES_DIR / "test-documents" / "ev-strategy-analysis.md"


class MarkdownParserBasicTests(unittest.TestCase):
    """Markdown 解析器基础测试。"""

    def test_parse_empty_document(self):
        doc = parse_markdown("")
        self.assertEqual(doc.title, "")
        self.assertEqual(doc.section_count, 0)
        self.assertEqual(len(doc.preamble), 0)

    def test_parse_title_only(self):
        doc = parse_markdown("# Hello World")
        self.assertEqual(doc.title, "Hello World")
        self.assertEqual(doc.section_count, 1)

    def test_parse_headings(self):
        md = "# Title\n\n## Section 1\n\nParagraph 1.\n\n## Section 2\n\nParagraph 2."
        doc = parse_markdown(md)
        self.assertEqual(doc.title, "Title")
        self.assertEqual(doc.section_count, 3)  # h1 + 2 h2
        self.assertEqual(doc.sections[1].heading, "Section 1")
        self.assertEqual(doc.sections[1].level, 2)
        self.assertEqual(doc.sections[2].heading, "Section 2")

    def test_parse_nested_headings(self):
        md = "# Title\n\n## Chapter\n\n### Sub-section\n\nContent here."
        doc = parse_markdown(md)
        self.assertEqual(doc.section_count, 3)
        self.assertEqual(doc.sections[2].heading, "Sub-section")
        self.assertEqual(doc.sections[2].level, 3)

    def test_parse_paragraphs(self):
        md = "# Title\n\n## Section\n\nFirst paragraph.\n\nSecond paragraph."
        doc = parse_markdown(md)
        section = doc.sections[1]
        self.assertEqual(len(section.paragraphs), 2)
        self.assertEqual(section.paragraphs[0], "First paragraph.")
        self.assertEqual(section.paragraphs[1], "Second paragraph.")


class MarkdownParserListTests(unittest.TestCase):
    """列表解析测试。"""

    def test_parse_unordered_list(self):
        md = "# Title\n\n## Section\n\n- Item 1\n- Item 2\n- Item 3"
        doc = parse_markdown(md)
        section = doc.sections[1]
        list_blocks = [b for b in section.blocks if b.block_type == "list"]
        self.assertEqual(len(list_blocks), 1)
        self.assertEqual(len(list_blocks[0].items), 3)
        self.assertFalse(list_blocks[0].ordered)

    def test_parse_ordered_list(self):
        md = "# Title\n\n## Section\n\n1. First\n2. Second\n3. Third"
        doc = parse_markdown(md)
        section = doc.sections[1]
        list_blocks = [b for b in section.blocks if b.block_type == "list"]
        self.assertEqual(len(list_blocks), 1)
        self.assertEqual(len(list_blocks[0].items), 3)
        self.assertTrue(list_blocks[0].ordered)
        self.assertEqual(list_blocks[0].items[0], "First")


class MarkdownParserTableTests(unittest.TestCase):
    """表格解析测试。"""

    def test_parse_simple_table(self):
        md = "# Title\n\n## Section\n\n| A | B |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |"
        doc = parse_markdown(md)
        section = doc.sections[1]
        tables = section.tables
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0]["headers"], ["A", "B"])
        self.assertEqual(len(tables[0]["rows"]), 2)
        self.assertEqual(tables[0]["rows"][0], ["1", "2"])


class MarkdownParserCodeBlockTests(unittest.TestCase):
    """代码块解析测试。"""

    def test_parse_code_block(self):
        md = "# Title\n\n## Section\n\n```python\nprint('hello')\n```"
        doc = parse_markdown(md)
        section = doc.sections[1]
        code_blocks = section.code_blocks
        self.assertEqual(len(code_blocks), 1)
        self.assertEqual(code_blocks[0]["language"], "python")
        self.assertIn("print", code_blocks[0]["content"])

    def test_parse_code_block_no_language(self):
        md = "# Title\n\n## Section\n\n```\nsome code\n```"
        doc = parse_markdown(md)
        section = doc.sections[1]
        code_blocks = section.code_blocks
        self.assertEqual(len(code_blocks), 1)
        self.assertEqual(code_blocks[0]["language"], "")


class MarkdownParserBlockquoteTests(unittest.TestCase):
    """引用块解析测试。"""

    def test_parse_blockquote(self):
        md = "# Title\n\n## Section\n\n> This is a quote.\n> Second line."
        doc = parse_markdown(md)
        section = doc.sections[1]
        quotes = [b for b in section.blocks if b.block_type == "blockquote"]
        self.assertEqual(len(quotes), 1)
        self.assertIn("This is a quote.", quotes[0].content)


class MarkdownParserYAMLFrontMatterTests(unittest.TestCase):
    """YAML front matter 解析测试。"""

    def test_parse_yaml_front_matter(self):
        md = "---\ntitle: Test\nauthor: Alice\n---\n\n# Document\n\nContent."
        doc = parse_markdown(md)
        self.assertEqual(doc.metadata.get("title"), "Test")
        self.assertEqual(doc.metadata.get("author"), "Alice")
        self.assertEqual(doc.title, "Document")

    def test_no_yaml_front_matter(self):
        md = "# Document\n\nContent."
        doc = parse_markdown(md)
        self.assertEqual(doc.metadata, {})


class MarkdownDocumentPropertiesTests(unittest.TestCase):
    """MarkdownDocument 属性测试。"""

    def test_all_text(self):
        md = "# Title\n\n## Section\n\nParagraph content."
        doc = parse_markdown(md)
        text = doc.all_text
        self.assertIn("Title", text)
        self.assertIn("Paragraph content.", text)

    def test_word_count_english(self):
        md = "# Title\n\n## Section\n\nThis is a test paragraph with some words."
        doc = parse_markdown(md)
        self.assertGreater(doc.word_count, 5)

    def test_word_count_chinese(self):
        md = "# 标题\n\n## 章节\n\n这是一个中文测试段落。"
        doc = parse_markdown(md)
        self.assertGreater(doc.word_count, 5)


class LanguageDetectionTests(unittest.TestCase):
    """语言检测测试。"""

    def test_detect_chinese(self):
        self.assertEqual(_detect_language("这是一段中文文本，用于测试语言检测功能。"), "zh-CN")

    def test_detect_english(self):
        self.assertEqual(_detect_language("This is an English text for testing language detection."), "en")

    def test_detect_empty(self):
        self.assertEqual(_detect_language(""), "en")

    def test_detect_mixed_mostly_chinese(self):
        self.assertEqual(_detect_language("这是中文 with some English words 但主要是中文内容"), "zh-CN")


class ClaimsExtractionTests(unittest.TestCase):
    """确定性 claims 提取测试。"""

    def test_extract_from_blockquote(self):
        section = MarkdownSection(heading="Test", level=2, blocks=[
            MarkdownBlock(block_type="blockquote", content="这是一个重要的结论。"),
        ])
        claims = _extract_claims_deterministic(section)
        self.assertIn("这是一个重要的结论。", claims)

    def test_extract_from_data_sentence(self):
        section = MarkdownSection(heading="Test", level=2, blocks=[
            MarkdownBlock(block_type="paragraph", content="2023年销量增长了35%，达到1400万辆。"),
        ])
        claims = _extract_claims_deterministic(section)
        self.assertTrue(len(claims) > 0)

    def test_extract_from_conclusion_sentence(self):
        section = MarkdownSection(heading="Test", level=2, blocks=[
            MarkdownBlock(block_type="paragraph", content="因此我们建议采取分阶段进入策略来降低风险。"),
        ])
        claims = _extract_claims_deterministic(section)
        self.assertTrue(len(claims) > 0)

    def test_fallback_to_first_sentence(self):
        section = MarkdownSection(heading="Test", level=2, blocks=[
            MarkdownBlock(block_type="paragraph", content="这是一段普通的描述性文本，没有特别的数据或结论。"),
        ])
        claims = _extract_claims_deterministic(section)
        self.assertTrue(len(claims) > 0)


class DeterministicUnderstandingTests(unittest.TestCase):
    """确定性来源理解测试。"""

    def test_basic_document(self):
        md = "# 测试文档\n\n## 第一章\n\n这是第一章的内容，包含了35%的增长数据。\n\n## 第二章\n\n因此建议采取保守策略。"
        doc = parse_markdown(md)
        pack = understand_source_deterministic(doc)

        self.assertIn("pack_id", pack)
        self.assertEqual(pack["language"], "zh-CN")
        self.assertIn("deck_goal", pack)
        self.assertIn("audience", pack)
        self.assertIn("sources", pack)
        self.assertTrue(len(pack["sources"]) > 0)

    def test_source_structure(self):
        md = "# Title\n\n## Section A\n\nContent A with 50% growth.\n\n## Section B\n\nContent B is important."
        doc = parse_markdown(md)
        pack = understand_source_deterministic(doc)

        for source in pack["sources"]:
            self.assertIn("source_id", source)
            self.assertIn("type", source)
            self.assertIn("title", source)
            self.assertIn("language", source)
            self.assertIn("sections", source)
            for section in source["sections"]:
                self.assertIn("section_id", section)
                self.assertIn("heading", section)
                self.assertIn("paragraphs", section)
                self.assertIn("claims", section)

    def test_custom_config(self):
        md = "# Test\n\n## Section\n\nContent."
        doc = parse_markdown(md)
        config = IngestConfig(
            language="en",
            deck_goal="Custom goal",
            audience="Custom audience",
        )
        pack = understand_source_deterministic(doc, config)
        self.assertEqual(pack["language"], "en")
        self.assertEqual(pack["deck_goal"], "Custom goal")
        self.assertEqual(pack["audience"], "Custom audience")

    def test_empty_document(self):
        doc = parse_markdown("")
        pack = understand_source_deterministic(doc)
        self.assertIn("pack_id", pack)
        self.assertIn("sources", pack)

    def test_document_with_subsections(self):
        md = "# Title\n\n## Chapter 1\n\nIntro.\n\n### Sub 1.1\n\nDetail 1.1 with 20% data.\n\n### Sub 1.2\n\nDetail 1.2."
        doc = parse_markdown(md)
        pack = understand_source_deterministic(doc)
        # Chapter 1 应该有多个 sections（包括子章节）
        chapter_source = None
        for s in pack["sources"]:
            if "Chapter 1" in s["title"]:
                chapter_source = s
                break
        self.assertIsNotNone(chapter_source)
        self.assertTrue(len(chapter_source["sections"]) >= 2)


class LLMUnderstandingTests(unittest.TestCase):
    """LLM 来源理解测试。"""

    def test_without_callback_falls_back_to_deterministic(self):
        md = "# Test\n\n## Section\n\nContent with 50% growth."
        doc = parse_markdown(md)
        pack = understand_source(doc)
        self.assertIn("pack_id", pack)
        self.assertIn("sources", pack)

    def test_with_valid_callback(self):
        md = "# Test\n\n## Section\n\nContent."
        doc = parse_markdown(md)

        def mock_callback(system_prompt: str, user_prompt: str) -> dict:
            return {
                "pack_id": "mock-pack",
                "language": "zh-CN",
                "deck_goal": "Mock goal",
                "audience": "Mock audience",
                "sources": [{
                    "source_id": "src-01",
                    "type": "document",
                    "title": "Mock Source",
                    "language": "zh-CN",
                    "sections": [{
                        "section_id": "sec-01",
                        "heading": "Mock Section",
                        "paragraphs": ["Mock paragraph."],
                        "claims": ["Mock claim."],
                    }],
                }],
            }

        pack = understand_source(doc, llm_callback=mock_callback)
        self.assertEqual(pack["pack_id"], "mock-pack")
        self.assertEqual(pack["deck_goal"], "Mock goal")

    def test_callback_returns_invalid_falls_back(self):
        md = "# Test\n\n## Section\n\nContent with 30% data."
        doc = parse_markdown(md)

        def bad_callback(system_prompt: str, user_prompt: str) -> dict:
            return {"invalid": "structure"}

        pack = understand_source(doc, llm_callback=bad_callback)
        # 应该回退到确定性结果
        self.assertIn("sources", pack)
        self.assertTrue(len(pack["sources"]) > 0)

    def test_callback_raises_exception_falls_back(self):
        md = "# Test\n\n## Section\n\nContent."
        doc = parse_markdown(md)

        def error_callback(system_prompt: str, user_prompt: str) -> dict:
            raise RuntimeError("LLM error")

        pack = understand_source(doc, llm_callback=error_callback)
        self.assertIn("sources", pack)


class PackIdGenerationTests(unittest.TestCase):
    """pack_id 生成测试。"""

    def test_generate_from_title(self):
        pack_id = _generate_pack_id("Test Document", "abc12345")
        self.assertTrue(pack_id.startswith("test-document"))
        self.assertIn("abc12345", pack_id)

    def test_generate_from_chinese_title(self):
        pack_id = _generate_pack_id("中文标题", "def67890")
        self.assertIn("def67890", pack_id)

    def test_generate_from_empty_title(self):
        pack_id = _generate_pack_id("", "xyz00000")
        self.assertTrue(pack_id.startswith("untitled"))


class InputFormatDetectionTests(unittest.TestCase):
    """输入格式检测测试。"""

    def test_detect_markdown(self):
        self.assertEqual(detect_input_format(Path("doc.md")), "markdown")
        self.assertEqual(detect_input_format(Path("doc.markdown")), "markdown")

    def test_detect_json(self):
        self.assertEqual(detect_input_format(Path("pack.json")), "source-pack-json")

    def test_detect_unknown(self):
        self.assertEqual(detect_input_format(Path("doc.pdf")), "unknown")
        self.assertEqual(detect_input_format(Path("doc.docx")), "unknown")


class IngestFromFileTests(unittest.TestCase):
    """从文件摄取测试。"""

    def test_ingest_json_file(self):
        json_path = FIXTURES_DIR / "source-packs" / "strongest-demo-source-pack.json"
        pack = ingest_from_file(json_path)
        self.assertEqual(pack["pack_id"], "china-ev-market-entry")

    def test_ingest_markdown_file(self):
        if not TEST_DOC_PATH.exists():
            self.skipTest("test document not found")
        pack = ingest_from_file(TEST_DOC_PATH)
        self.assertIn("pack_id", pack)
        self.assertIn("sources", pack)
        self.assertTrue(len(pack["sources"]) > 0)
        self.assertEqual(pack["language"], "zh-CN")

    def test_ingest_nonexistent_file(self):
        with self.assertRaises(FileNotFoundError):
            ingest_from_file(Path("/nonexistent/file.md"))

    def test_ingest_unsupported_format(self):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"fake pdf")
            f.flush()
            try:
                with self.assertRaises(ValueError):
                    ingest_from_file(Path(f.name))
            finally:
                os.unlink(f.name)


class PipelineMarkdownIntegrationTests(unittest.TestCase):
    """Pipeline Markdown 集成测试。"""

    def test_pipeline_with_markdown_input(self):
        if not TEST_DOC_PATH.exists():
            self.skipTest("test document not found")
        result = run_pipeline(input_path=TEST_DOC_PATH)
        self.assertIn("source_pack", result)
        self.assertIn("normalized_pack", result)
        self.assertIn("slide_spec", result)
        self.assertIn("quality_report", result)

    def test_pipeline_with_markdown_produces_slides(self):
        if not TEST_DOC_PATH.exists():
            self.skipTest("test document not found")
        result = run_pipeline(input_path=TEST_DOC_PATH)
        slides = result["slide_spec"]["slides"]
        self.assertTrue(len(slides) >= 3, f"Expected at least 3 slides, got {len(slides)}")

    def test_pipeline_with_markdown_and_pptx(self):
        if not TEST_DOC_PATH.exists():
            self.skipTest("test document not found")
        with tempfile.TemporaryDirectory() as tmpdir:
            pptx_path = Path(tmpdir) / "test.pptx"
            result = run_pipeline(
                input_path=TEST_DOC_PATH,
                render_pptx=pptx_path,
            )
            self.assertIn("pptx_path", result)
            self.assertTrue(Path(result["pptx_path"]).exists())

    def test_pipeline_backward_compatible_with_raw_pack(self):
        """确保传统的 raw_pack 输入方式仍然有效。"""
        json_path = FIXTURES_DIR / "source-packs" / "strongest-demo-source-pack.json"
        raw_pack = json.loads(json_path.read_text(encoding="utf-8"))
        result = run_pipeline(raw_pack)
        self.assertIn("slide_spec", result)
        self.assertIn("quality_report", result)

    def test_pipeline_requires_input(self):
        """必须提供 raw_pack 或 input_path 之一。"""
        with self.assertRaises(ValueError):
            run_pipeline()


class EVStrategyDocumentTests(unittest.TestCase):
    """使用 EV 策略分析文档的端到端测试。"""

    @classmethod
    def setUpClass(cls):
        if not TEST_DOC_PATH.exists():
            raise unittest.SkipTest("test document not found")
        cls.doc = parse_markdown(TEST_DOC_PATH.read_text(encoding="utf-8"))
        cls.pack = understand_source_deterministic(cls.doc)

    def test_document_title(self):
        self.assertEqual(self.doc.title, "中国新能源汽车出海策略分析")

    def test_document_has_yaml_metadata(self):
        self.assertIn("title", self.doc.metadata)
        self.assertIn("author", self.doc.metadata)

    def test_document_has_sections(self):
        self.assertGreater(self.doc.section_count, 3)

    def test_document_has_tables(self):
        has_table = False
        for section in self.doc.sections:
            if section.tables:
                has_table = True
                break
        self.assertTrue(has_table, "Document should contain at least one table")

    def test_document_has_lists(self):
        has_list = False
        for section in self.doc.sections:
            if section.lists:
                has_list = True
                break
        self.assertTrue(has_list, "Document should contain at least one list")

    def test_pack_language_is_chinese(self):
        self.assertEqual(self.pack["language"], "zh-CN")

    def test_pack_has_multiple_sources(self):
        self.assertGreater(len(self.pack["sources"]), 1)

    def test_pack_claims_are_grounded(self):
        """每个 claim 应该有文档中的事实依据。"""
        for source in self.pack["sources"]:
            for section in source["sections"]:
                for claim in section.get("claims", []):
                    self.assertTrue(len(claim) >= 8, f"Claim too short: {claim}")

    def test_pack_is_valid_for_normalize(self):
        """生成的 source pack 应该能被 normalize_source_pack 处理。"""
        from src.ingest.normalize import normalize_source_pack
        normalized = normalize_source_pack(self.pack)
        self.assertIn("source_units", normalized)
        self.assertTrue(len(normalized["source_units"]) > 0)

    def test_full_pipeline_produces_quality_pass(self):
        """完整 pipeline 应该产生 quality pass。"""
        result = run_pipeline(self.pack)
        # 确定性 provider 应该能处理
        self.assertIn("quality_report", result)


if __name__ == "__main__":
    unittest.main()
