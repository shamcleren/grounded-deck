"""视觉形式选择器的单元测试。"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from src.visual.selector import (
    LAYOUT_CHART,
    LAYOUT_COMPARISON,
    LAYOUT_PROCESS,
    LAYOUT_SUMMARY,
    LAYOUT_TIMELINE,
    LayoutSelection,
    LayoutValidationItem,
    LayoutValidationReport,
    ModelLayoutCallback,
    build_visual_elements,
    infer_layout_type,
    model_assisted_infer_layout_type,
    select_visual_form,
    unique_preserving_order,
    validate_model_layouts,
)

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


class VisualSelectorTests(unittest.TestCase):
    """测试视觉形式选择器的规则推断和视觉元素构建逻辑。"""

    # ---------- unique_preserving_order ----------

    def test_unique_preserving_order_removes_duplicates(self) -> None:
        result = unique_preserving_order(["a", "b", "a", "c", "b"])
        self.assertEqual(result, ["a", "b", "c"])

    def test_unique_preserving_order_empty_list(self) -> None:
        result = unique_preserving_order([])
        self.assertEqual(result, [])

    # ---------- infer_layout_type ----------

    def test_infer_comparison_from_vs_keyword(self) -> None:
        unit = {"section_heading": "欧洲 vs 东南亚对比", "text": "欧洲 vs 东南亚的差异"}
        result = infer_layout_type(unit)
        self.assertIsInstance(result, LayoutSelection)
        self.assertEqual(result.layout_type, LAYOUT_COMPARISON)
        self.assertEqual(result.confidence, "rule-based")
        self.assertTrue(any("vs" in s for s in result.matched_signals))

    def test_infer_comparison_from_duibi_keyword(self) -> None:
        unit = {"section_heading": "对比分析", "text": "两者对比很明显"}
        result = infer_layout_type(unit)
        self.assertEqual(result.layout_type, LAYOUT_COMPARISON)

    def test_infer_process_from_lujing_keyword(self) -> None:
        unit = {"section_heading": "进入路径", "text": "建议先进入东南亚再进入欧洲"}
        result = infer_layout_type(unit)
        self.assertEqual(result.layout_type, LAYOUT_PROCESS)
        self.assertTrue(any("路径" in s or "进入" in s for s in result.matched_signals))

    def test_infer_process_from_buzhou_keyword(self) -> None:
        unit = {"section_heading": "实施步骤", "text": "分三个步骤落地"}
        result = infer_layout_type(unit)
        self.assertEqual(result.layout_type, LAYOUT_PROCESS)

    def test_infer_timeline_from_year_refs(self) -> None:
        unit = {"section_heading": "出口时间线", "text": "2022 年到 2024 年的变化"}
        result = infer_layout_type(unit)
        self.assertEqual(result.layout_type, LAYOUT_TIMELINE)
        self.assertTrue(any("year_refs" in s for s in result.matched_signals))

    def test_infer_timeline_from_jieduan_keyword(self) -> None:
        unit = {"section_heading": "发展阶段", "text": "三个阶段的演变"}
        result = infer_layout_type(unit)
        self.assertEqual(result.layout_type, LAYOUT_TIMELINE)

    def test_infer_chart_from_cost_keyword(self) -> None:
        unit = {"section_heading": "成本与利润指标", "text": "成本下降了18%"}
        result = infer_layout_type(unit)
        self.assertEqual(result.layout_type, LAYOUT_CHART)
        self.assertTrue(any("成本" in s for s in result.matched_signals))

    def test_infer_chart_from_percentage(self) -> None:
        unit = {"section_heading": "市场份额", "text": "占据全球15%的份额"}
        result = infer_layout_type(unit)
        self.assertEqual(result.layout_type, LAYOUT_CHART)

    def test_infer_chart_from_digits(self) -> None:
        unit = {"section_heading": "产能", "text": "年产能达到50万辆"}
        result = infer_layout_type(unit)
        self.assertEqual(result.layout_type, LAYOUT_CHART)
        self.assertTrue(any("contains_digits" in s for s in result.matched_signals))

    def test_infer_summary_fallback(self) -> None:
        unit = {"section_heading": "总结", "text": "这是一个总结性的内容描述"}
        result = infer_layout_type(unit)
        self.assertEqual(result.layout_type, LAYOUT_SUMMARY)
        self.assertTrue(any("fallback" in s for s in result.matched_signals))

    # ---------- build_visual_elements ----------

    def test_build_timeline_elements(self) -> None:
        unit = {"text": "2022 年开始试点，2023 年加速，2024 年深化", "claims": []}
        result = build_visual_elements(LAYOUT_TIMELINE, unit)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["type"], "timeline")
        self.assertEqual(result[0]["milestones"], ["2022", "2023", "2024"])

    def test_build_comparison_elements_with_labels(self) -> None:
        unit = {"text": "欧洲单车收入更高，东南亚渠道建立更快", "claims": []}
        result = build_visual_elements(LAYOUT_COMPARISON, unit)
        self.assertEqual(result[0]["type"], "comparison-columns")
        self.assertEqual(result[0]["columns"], ["欧洲", "东南亚"])

    def test_build_comparison_elements_fallback(self) -> None:
        unit = {"text": "A方案和B方案的对比", "claims": []}
        result = build_visual_elements(LAYOUT_COMPARISON, unit)
        self.assertEqual(result[0]["columns"], ["Option A", "Option B"])

    def test_build_process_elements(self) -> None:
        unit = {"text": "先做A再做B", "claims": ["步骤1", "步骤2"]}
        result = build_visual_elements(LAYOUT_PROCESS, unit)
        self.assertEqual(result[0]["type"], "process-flow")
        self.assertEqual(result[0]["steps"], 2)
        self.assertEqual(result[0]["step_labels"], ["做A", "做B"])

    def test_build_process_elements_minimum_one_step(self) -> None:
        unit = {"text": "一步到位", "claims": []}
        result = build_visual_elements(LAYOUT_PROCESS, unit)
        self.assertEqual(result[0]["steps"], 1)

    def test_build_chart_elements(self) -> None:
        unit = {"text": "成本下降18%，利润率提升到12%", "claims": []}
        result = build_visual_elements(LAYOUT_CHART, unit)
        self.assertEqual(result[0]["type"], "metric-cards")
        self.assertIn("18%", result[0]["metrics"])
        self.assertIn("12%", result[0]["metrics"])
        self.assertIn("labels", result[0])
        self.assertEqual(len(result[0]["labels"]), len(result[0]["metrics"]))

    def test_build_summary_elements(self) -> None:
        unit = {"text": "这是一个总结", "claims": []}
        result = build_visual_elements(LAYOUT_SUMMARY, unit)
        self.assertEqual(result, [{"type": "bullet-list"}])

    # ---------- select_visual_form ----------

    def test_select_visual_form_returns_complete_result(self) -> None:
        unit = {
            "section_heading": "出口时间线",
            "text": "2022年到2024年的变化",
            "claims": [],
        }
        result = select_visual_form(unit)
        self.assertEqual(result["layout_type"], LAYOUT_TIMELINE)
        self.assertIn("visual_elements", result)
        self.assertEqual(result["confidence"], "rule-based")
        self.assertIsInstance(result["matched_signals"], list)
        self.assertTrue(len(result["matched_signals"]) > 0)

    # ---------- 与 strongest-demo fixture 的回归一致性 ----------

    def test_strongest_demo_units_match_expected_layouts(self) -> None:
        """确保 visual selector 对 strongest-demo 的所有 source unit 推断出的布局
        与确定性基线完全一致。"""
        normalized_path = (
            FIXTURES_DIR
            / "normalized-source-units"
            / "strongest-demo-normalized-source-units.json"
        )
        normalized_pack = json.loads(normalized_path.read_text(encoding="utf-8"))

        expected_layouts = {
            "src-01:sec-01": LAYOUT_TIMELINE,
            "src-01:sec-02": LAYOUT_COMPARISON,
            "src-02:sec-01": LAYOUT_PROCESS,
            "src-03:sec-01": LAYOUT_CHART,
        }

        for unit in normalized_pack["source_units"]:
            unit_id = unit["unit_id"]
            selection = infer_layout_type(unit)
            self.assertEqual(
                selection.layout_type,
                expected_layouts[unit_id],
                f"unit {unit_id} expected {expected_layouts[unit_id]} but got {selection.layout_type}",
            )

    def test_strongest_demo_visual_elements_match_deterministic_baseline(self) -> None:
        """确保 visual selector 构建的视觉元素与确定性基线的 slide spec fixture 一致。"""
        normalized_path = (
            FIXTURES_DIR
            / "normalized-source-units"
            / "strongest-demo-normalized-source-units.json"
        )
        slide_spec_path = (
            FIXTURES_DIR / "slide-spec" / "strongest-demo-slide-spec.json"
        )
        normalized_pack = json.loads(normalized_path.read_text(encoding="utf-8"))
        slide_spec = json.loads(slide_spec_path.read_text(encoding="utf-8"))

        # 跳过 cover 和 summary slides，只检查 unit-backed content slides
        content_slides = [
            s for s in slide_spec["slides"]
            if len(s.get("must_include_checks", [])) == 1
        ]
        unit_by_id = {u["unit_id"]: u for u in normalized_pack["source_units"]}

        for slide in content_slides:
            unit_id = slide["must_include_checks"][0]
            unit = unit_by_id[unit_id]
            layout = infer_layout_type(unit).layout_type
            elements = build_visual_elements(layout, unit)
            self.assertEqual(
                layout,
                slide["layout_type"],
                f"unit {unit_id} layout mismatch",
            )
            self.assertEqual(
                elements,
                slide["visual_elements"],
                f"unit {unit_id} visual_elements mismatch",
            )


class LayoutValidationTests(unittest.TestCase):
    """测试模型输出布局验证逻辑。"""

    def _make_normalized_pack(self, units: list[dict]) -> dict:
        return {
            "pack_id": "test-pack",
            "deck_goal": "Test",
            "audience": "Testers",
            "source_units": units,
        }

    def _make_unit(self, unit_id: str, heading: str, text: str) -> dict:
        return {
            "unit_id": unit_id,
            "source_id": "src-01",
            "section_id": "sec-01",
            "section_heading": heading,
            "text": text,
            "claims": [],
            "source_binding": unit_id,
        }

    def _make_slide(self, unit_id: str, layout_type: str) -> dict:
        return {
            "slide_id": f"slide-{unit_id}",
            "title": "Test Slide",
            "goal": "Test",
            "layout_type": layout_type,
            "key_points": [],
            "visual_elements": [],
            "source_bindings": [unit_id],
            "must_include_checks": [unit_id],
            "speaker_notes": "Test",
        }

    # ---------- validate_model_layouts ----------

    def test_all_layouts_match(self) -> None:
        """模型与规则推断完全一致时，报告 all_matched。"""
        unit = self._make_unit("u1", "出口时间线", "2022 年到 2024 年的变化")
        pack = self._make_normalized_pack([unit])
        slide_spec = {"slides": [self._make_slide("u1", LAYOUT_TIMELINE)]}

        report = validate_model_layouts(pack, slide_spec)
        self.assertTrue(report.all_matched)
        self.assertEqual(report.matched_count, 1)
        self.assertEqual(report.mismatched_count, 0)
        self.assertEqual(report.match_ratio, 1.0)

    def test_layout_mismatch_detected(self) -> None:
        """模型布局与规则推断不一致时，报告 mismatch。"""
        unit = self._make_unit("u1", "出口时间线", "2022 年到 2024 年的变化")
        pack = self._make_normalized_pack([unit])
        slide_spec = {"slides": [self._make_slide("u1", LAYOUT_SUMMARY)]}

        report = validate_model_layouts(pack, slide_spec)
        self.assertFalse(report.all_matched)
        self.assertEqual(report.mismatched_count, 1)
        self.assertEqual(len(report.mismatches), 1)
        self.assertEqual(report.mismatches[0].rule_layout, LAYOUT_TIMELINE)
        self.assertEqual(report.mismatches[0].model_layout, LAYOUT_SUMMARY)

    def test_missing_slide_treated_as_mismatch(self) -> None:
        """当 unit 没有对应的 slide 时，model_layout 为 None，视为 mismatch。"""
        unit = self._make_unit("u1", "成本分析", "成本下降了18%")
        pack = self._make_normalized_pack([unit])
        slide_spec = {"slides": []}

        report = validate_model_layouts(pack, slide_spec)
        self.assertFalse(report.all_matched)
        self.assertEqual(report.mismatches[0].model_layout, None)

    def test_multiple_units_mixed_results(self) -> None:
        """多个 unit 中部分匹配部分不匹配。"""
        u1 = self._make_unit("u1", "出口时间线", "2022 年的变化")
        u2 = self._make_unit("u2", "成本指标", "成本下降了18%")
        pack = self._make_normalized_pack([u1, u2])
        slide_spec = {
            "slides": [
                self._make_slide("u1", LAYOUT_TIMELINE),  # 匹配
                self._make_slide("u2", LAYOUT_SUMMARY),   # 不匹配，应为 chart
            ]
        }

        report = validate_model_layouts(pack, slide_spec)
        self.assertEqual(report.matched_count, 1)
        self.assertEqual(report.mismatched_count, 1)
        self.assertEqual(report.match_ratio, 0.5)

    def test_ignores_multi_unit_slides(self) -> None:
        """只验证恰好绑定单个 unit 的 slide，忽略 cover/summary 等多 unit 绑定。"""
        unit = self._make_unit("u1", "阶段", "三个阶段的演变")
        pack = self._make_normalized_pack([unit])
        multi_check_slide = {
            "slide_id": "s-cover",
            "title": "Cover",
            "goal": "Cover",
            "layout_type": "cover",
            "key_points": [],
            "visual_elements": [],
            "source_bindings": ["u1"],
            "must_include_checks": ["u1", "u2"],
            "speaker_notes": "",
        }
        slide_spec = {
            "slides": [
                multi_check_slide,
                self._make_slide("u1", LAYOUT_TIMELINE),
            ]
        }

        report = validate_model_layouts(pack, slide_spec)
        self.assertTrue(report.all_matched)

    # ---------- LayoutValidationReport.as_grader_hint ----------

    def test_grader_hint_all_matched(self) -> None:
        """全部匹配时的 grader hint 包含 'all' 关键词。"""
        report = LayoutValidationReport(items=[
            LayoutValidationItem("u1", LAYOUT_TIMELINE, LAYOUT_TIMELINE, True, ["keyword:时间线"]),
        ])
        hint = report.as_grader_hint()
        self.assertIn("all", hint.lower())
        self.assertIn("1", hint)

    def test_grader_hint_with_mismatches(self) -> None:
        """存在 mismatch 时 grader hint 包含详细信息。"""
        report = LayoutValidationReport(items=[
            LayoutValidationItem("u1", LAYOUT_TIMELINE, LAYOUT_SUMMARY, False, ["keyword:时间线"]),
            LayoutValidationItem("u2", LAYOUT_CHART, LAYOUT_CHART, True, ["keyword:成本"]),
        ])
        hint = report.as_grader_hint()
        self.assertIn("Mismatches", hint)
        self.assertIn("u1", hint)
        self.assertIn("timeline", hint)
        self.assertIn("summary", hint)
        self.assertNotIn("u2", hint)  # 匹配的 unit 不出现在 mismatch 部分

    def test_grader_hint_missing_slide(self) -> None:
        """缺失 slide 时显示 'missing'。"""
        report = LayoutValidationReport(items=[
            LayoutValidationItem("u1", LAYOUT_PROCESS, None, False, ["keyword:步骤"]),
        ])
        hint = report.as_grader_hint()
        self.assertIn("missing", hint)

    # ---------- 与 strongest-demo fixture 的完整验证 ----------

    def test_strongest_demo_validate_model_layouts_all_match(self) -> None:
        """确保 strongest-demo 的确定性基线 slide spec 通过模型布局验证。"""
        normalized_path = (
            FIXTURES_DIR
            / "normalized-source-units"
            / "strongest-demo-normalized-source-units.json"
        )
        slide_spec_path = (
            FIXTURES_DIR / "slide-spec" / "strongest-demo-slide-spec.json"
        )
        normalized_pack = json.loads(normalized_path.read_text(encoding="utf-8"))
        slide_spec = json.loads(slide_spec_path.read_text(encoding="utf-8"))

        report = validate_model_layouts(normalized_pack, slide_spec)
        self.assertTrue(
            report.all_matched,
            f"strongest-demo layouts should all match, but got mismatches: "
            f"{[(m.unit_id, m.rule_layout, m.model_layout) for m in report.mismatches]}",
        )
        self.assertEqual(report.total_count, 4)
        self.assertEqual(report.match_ratio, 1.0)


class ModelAssistedInferenceTests(unittest.TestCase):
    """测试 model-assisted 布局推断逻辑。"""

    def _make_unit(self, heading: str, text: str) -> dict:
        return {
            "unit_id": "test-unit",
            "source_id": "src-01",
            "section_id": "sec-01",
            "section_heading": heading,
            "text": text,
            "claims": [],
            "source_binding": "test-unit",
        }

    # ---------- 无 callback 时回退到规则引擎 ----------

    def test_no_callback_falls_back_to_rule_based(self) -> None:
        """当 callback 为 None 时，等同于纯规则推断。"""
        unit = self._make_unit("出口时间线", "2022 年到 2024 年的变化")
        result = model_assisted_infer_layout_type(unit, callback=None)
        self.assertEqual(result.layout_type, LAYOUT_TIMELINE)
        self.assertEqual(result.confidence, "rule-based")

    # ---------- callback 返回有效布局 ----------

    def test_valid_callback_uses_model_result(self) -> None:
        """callback 返回有效布局时，使用模型结果。"""
        unit = self._make_unit("出口时间线", "2022 年到 2024 年的变化")

        def mock_callback(u: dict) -> str:
            return "chart"

        result = model_assisted_infer_layout_type(unit, callback=mock_callback)
        self.assertEqual(result.layout_type, LAYOUT_CHART)
        self.assertEqual(result.confidence, "model-assisted")
        self.assertTrue(any("model_layout:chart" in s for s in result.matched_signals))
        self.assertTrue(any("rule_layout:timeline" in s for s in result.matched_signals))
        self.assertTrue(any("model_rule_disagree" in s for s in result.matched_signals))

    def test_model_agrees_with_rule(self) -> None:
        """模型与规则一致时，matched_signals 中有 'agree' 标记。"""
        unit = self._make_unit("出口时间线", "2022 年到 2024 年的变化")

        def mock_callback(u: dict) -> str:
            return "timeline"

        result = model_assisted_infer_layout_type(unit, callback=mock_callback)
        self.assertEqual(result.layout_type, LAYOUT_TIMELINE)
        self.assertEqual(result.confidence, "model-assisted")
        self.assertTrue(any("model_rule_agree" in s for s in result.matched_signals))

    # ---------- callback 返回无效布局 ----------

    def test_invalid_layout_falls_back_to_rule(self) -> None:
        """callback 返回不在 ALL_CONTENT_LAYOUTS 中的布局时，回退到规则引擎。"""
        unit = self._make_unit("出口时间线", "2022 年到 2024 年的变化")

        def mock_callback(u: dict) -> str:
            return "fancy-3d-view"

        result = model_assisted_infer_layout_type(unit, callback=mock_callback)
        self.assertEqual(result.layout_type, LAYOUT_TIMELINE)
        self.assertEqual(result.confidence, "rule-based")
        self.assertTrue(any("model_invalid_layout:fancy-3d-view" in s for s in result.matched_signals))

    def test_empty_string_layout_falls_back(self) -> None:
        """callback 返回空字符串时回退。"""
        unit = self._make_unit("成本指标", "成本下降了18%")

        def mock_callback(u: dict) -> str:
            return ""

        result = model_assisted_infer_layout_type(unit, callback=mock_callback)
        self.assertEqual(result.layout_type, LAYOUT_CHART)
        self.assertEqual(result.confidence, "rule-based")

    # ---------- callback 抛出异常 ----------

    def test_callback_exception_falls_back_to_rule(self) -> None:
        """callback 抛出异常时，安全回退到规则引擎。"""
        unit = self._make_unit("对比分析", "欧洲 vs 东南亚的差异")

        def exploding_callback(u: dict) -> str:
            raise ConnectionError("API unreachable")

        result = model_assisted_infer_layout_type(unit, callback=exploding_callback)
        self.assertEqual(result.layout_type, LAYOUT_COMPARISON)
        self.assertEqual(result.confidence, "rule-based")
        self.assertTrue(any("model_callback_error:ConnectionError" in s for s in result.matched_signals))

    def test_callback_value_error_falls_back(self) -> None:
        """callback 抛出 ValueError 时也安全回退。"""
        unit = self._make_unit("步骤", "分三个步骤落地")

        def bad_callback(u: dict) -> str:
            raise ValueError("invalid JSON from model")

        result = model_assisted_infer_layout_type(unit, callback=bad_callback)
        self.assertEqual(result.layout_type, LAYOUT_PROCESS)
        self.assertEqual(result.confidence, "rule-based")
        self.assertTrue(any("model_callback_error:ValueError" in s for s in result.matched_signals))

    # ---------- select_visual_form 的 callback 路径 ----------

    def test_select_visual_form_with_callback(self) -> None:
        """select_visual_form 传入 layout_callback 时使用 model-assisted 路径。"""
        unit = self._make_unit("市场", "这是一个普通的市场描述")

        def mock_callback(u: dict) -> str:
            return "process"

        result = select_visual_form(unit, layout_callback=mock_callback)
        self.assertEqual(result["layout_type"], LAYOUT_PROCESS)
        self.assertEqual(result["confidence"], "model-assisted")
        # visual_elements 应该是 process 类型的
        self.assertEqual(result["visual_elements"][0]["type"], "process-flow")

    def test_select_visual_form_without_callback_remains_rule_based(self) -> None:
        """select_visual_form 不传 callback 时保持纯规则推断。"""
        unit = self._make_unit("出口时间线", "2022 年到 2024 年的变化")
        result = select_visual_form(unit)
        self.assertEqual(result["layout_type"], LAYOUT_TIMELINE)
        self.assertEqual(result["confidence"], "rule-based")

    # ---------- 所有布局类型的模型选择 ----------

    def test_all_content_layouts_accepted_from_model(self) -> None:
        """模型可以返回任何有效的 content layout。"""
        unit = self._make_unit("通用", "通用内容")
        for layout in (LAYOUT_TIMELINE, LAYOUT_COMPARISON, LAYOUT_PROCESS, LAYOUT_CHART, LAYOUT_SUMMARY):
            result = model_assisted_infer_layout_type(
                unit, callback=lambda u, lt=layout: lt,
            )
            self.assertEqual(result.layout_type, layout)
            self.assertEqual(result.confidence, "model-assisted")


class ContentEnrichmentTests(unittest.TestCase):
    """visual_elements 和 key_points 内容丰富化测试。"""

    def test_timeline_events_extracted(self) -> None:
        """timeline 布局包含事件描述。"""
        unit = {
            "text": "2022 年试点为主，2023 年双主线形成",
            "claims": [],
        }
        result = build_visual_elements(LAYOUT_TIMELINE, unit)
        self.assertIn("events", result[0])
        self.assertEqual(len(result[0]["events"]), 2)
        self.assertTrue(result[0]["events"][0].startswith("2022"))

    def test_comparison_column_points_extracted(self) -> None:
        """comparison 布局包含各列的对比要点。"""
        unit = {
            "text": "欧洲单车收入高；东南亚渠道快",
            "claims": [],
        }
        result = build_visual_elements(LAYOUT_COMPARISON, unit)
        self.assertIn("column_points", result[0])
        self.assertIn("欧洲", result[0]["column_points"])
        self.assertIn("东南亚", result[0]["column_points"])
        self.assertGreater(len(result[0]["column_points"]["欧洲"]), 0)

    def test_process_step_labels_extracted(self) -> None:
        """process 布局包含步骤描述标签。"""
        unit = {
            "text": "先建立渠道，再进入欧洲，然后扩大规模",
            "claims": [],
        }
        result = build_visual_elements(LAYOUT_PROCESS, unit)
        self.assertIn("step_labels", result[0])
        self.assertEqual(result[0]["steps"], len(result[0]["step_labels"]))
        self.assertGreaterEqual(result[0]["steps"], 2)

    def test_chart_metric_labels_extracted(self) -> None:
        """chart 布局包含指标上下文标签。"""
        unit = {
            "text": "电池成本下降 18%，利润缓冲增加",
            "claims": [],
        }
        result = build_visual_elements(LAYOUT_CHART, unit)
        self.assertIn("labels", result[0])
        self.assertEqual(len(result[0]["labels"]), len(result[0]["metrics"]))

    def test_timeline_milestones_no_trailing_comma(self) -> None:
        """timeline 事件描述不包含尾随逗号。"""
        unit = {
            "text": "2022 年试点为主，2023 年双主线",
            "claims": [],
        }
        result = build_visual_elements(LAYOUT_TIMELINE, unit)
        for event in result[0]["events"]:
            self.assertFalse(event.endswith("，"), f"event '{event}' has trailing comma")
            self.assertFalse(event.endswith(","), f"event '{event}' has trailing comma")

    def test_process_step_labels_match_step_count(self) -> None:
        """process 的 step_labels 长度和 steps 数量一致。"""
        unit = {
            "text": "先完成设计，再开发实现，然后测试验证，最后部署上线",
            "claims": [],
        }
        result = build_visual_elements(LAYOUT_PROCESS, unit)
        self.assertEqual(result[0]["steps"], len(result[0]["step_labels"]))

    def test_comparison_without_known_columns_uses_defaults(self) -> None:
        """当没有匹配已知列名时使用默认列名。"""
        unit = {
            "text": "方案A成本低，方案B质量高",
            "claims": [],
        }
        result = build_visual_elements(LAYOUT_COMPARISON, unit)
        self.assertEqual(result[0]["columns"], ["Option A", "Option B"])

    def test_key_points_dedup_across_claims_and_text(self) -> None:
        """key_points 在 claims 和 text 之间不重复。"""
        from src.llm.provider import DeterministicProvider

        unit = {
            "unit_id": "test:01",
            "source_id": "test",
            "source_title": "Test",
            "section_id": "01",
            "section_heading": "测试",
            "unit_kind": "section-summary",
            "language": "zh-CN",
            "text": "测试 这是唯一的声明。 这是唯一的声明",
            "claims": ["这是唯一的声明。"],
            "source_binding": "test:01",
        }
        kp = DeterministicProvider._extract_key_points(unit)
        # claims 中有 "这是唯一的声明。"，text 中的 "这是唯一的声明" 应该不会重复加入
        for i, a in enumerate(kp):
            for j, b in enumerate(kp):
                if i != j:
                    self.assertNotEqual(
                        a.rstrip("。；;.,"),
                        b.rstrip("。；;.,"),
                        f"key_points contain near-duplicates: '{a}' and '{b}'",
                    )


if __name__ == "__main__":
    unittest.main()
