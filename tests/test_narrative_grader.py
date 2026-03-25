"""叙事质量评分器测试。"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from src.quality.narrative_grader import (
    NarrativeGradeItem,
    NarrativeGradeReport,
    grade_narrative,
    grade_narrative_deterministic,
    grade_narrative_model_assisted,
    build_narrative_grader_system_prompt,
    build_narrative_grader_user_prompt,
    _score_coherence_deterministic,
    _score_grounding_deterministic,
    _score_visual_fit_deterministic,
)

ROOT = Path(__file__).resolve().parent.parent
STRONGEST_DEMO_NORMALIZED = ROOT / "fixtures" / "normalized-source-units" / "strongest-demo-normalized-source-units.json"
STRONGEST_DEMO_SLIDE_SPEC = ROOT / "fixtures" / "slide-spec" / "strongest-demo-slide-spec.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class CoherenceScoringTests(unittest.TestCase):
    """key_points 连贯性评分测试。"""

    def test_empty_key_points_scores_zero(self) -> None:
        slide = {"key_points": []}
        score, issues = _score_coherence_deterministic(slide)
        self.assertEqual(score, 0.0)
        self.assertIn("no key_points", issues)

    def test_missing_key_points_scores_zero(self) -> None:
        slide = {}
        score, issues = _score_coherence_deterministic(slide)
        self.assertEqual(score, 0.0)

    def test_rich_chinese_key_points_scores_high(self) -> None:
        slide = {
            "key_points": [
                "中国新能源汽车出口量从2020年的7万辆增长到2023年的120万辆",
                "欧洲市场占比最高，东南亚增速最快",
                "政策补贴退坡后企业需要寻找新的增长点",
            ]
        }
        score, issues = _score_coherence_deterministic(slide)
        self.assertGreaterEqual(score, 0.85)
        self.assertEqual(len(issues), 0)

    def test_short_key_points_penalized(self) -> None:
        slide = {"key_points": ["ok"]}
        score, issues = _score_coherence_deterministic(slide)
        self.assertLess(score, 0.7)
        self.assertTrue(any("short" in i or "only 1" in i for i in issues))

    def test_single_long_key_point_partial_score(self) -> None:
        slide = {"key_points": ["This is a sufficiently long key point about market analysis"]}
        score, issues = _score_coherence_deterministic(slide)
        self.assertGreater(score, 0.5)
        self.assertTrue(any("only 1" in i for i in issues))


class GroundingScoringTests(unittest.TestCase):
    """source-grounded 评分测试。"""

    def test_fully_grounded_slide_scores_high(self) -> None:
        slide = {
            "source_bindings": ["src-01:sec-01"],
            "must_include_checks": ["src-01:sec-01"],
            "speaker_notes": "Ground this slide in src-01:sec-01",
            "key_points": ["出口增长 [src-01:sec-01]"],
        }
        score, issues = _score_grounding_deterministic(slide)
        self.assertGreaterEqual(score, 0.85)
        self.assertEqual(len(issues), 0)

    def test_no_bindings_non_cover_penalized(self) -> None:
        slide = {
            "layout_type": "timeline",
            "source_bindings": [],
            "must_include_checks": [],
            "speaker_notes": "",
            "key_points": [],
        }
        score, issues = _score_grounding_deterministic(slide)
        self.assertLess(score, 0.5)
        self.assertIn("no source_bindings", issues)

    def test_cover_slide_no_bindings_no_penalty(self) -> None:
        slide = {
            "layout_type": "cover",
            "source_bindings": [],
            "must_include_checks": [],
            "speaker_notes": "",
            "key_points": [],
        }
        score, issues = _score_grounding_deterministic(slide)
        # cover 没有 source_bindings 不应被惩罚
        self.assertNotIn("no source_bindings", issues)


class VisualFitScoringTests(unittest.TestCase):
    """layout 与内容匹配度评分测试。"""

    def test_timeline_with_milestones_scores_high(self) -> None:
        slide = {
            "layout_type": "timeline",
            "visual_elements": [
                {"type": "timeline", "milestones": ["2020", "2021", "2022"], "events": ["a", "b", "c"]}
            ],
        }
        score, issues = _score_visual_fit_deterministic(slide)
        self.assertGreaterEqual(score, 0.9)

    def test_empty_visual_elements_scores_zero(self) -> None:
        slide = {"layout_type": "timeline", "visual_elements": []}
        score, issues = _score_visual_fit_deterministic(slide)
        self.assertEqual(score, 0.0)
        self.assertIn("no visual_elements", issues)

    def test_mismatched_type_penalized(self) -> None:
        slide = {
            "layout_type": "timeline",
            "visual_elements": [{"type": "bullet-list"}],
        }
        score, issues = _score_visual_fit_deterministic(slide)
        self.assertLess(score, 0.8)
        self.assertTrue(any("mismatch" in i for i in issues))

    def test_cover_always_matches(self) -> None:
        slide = {
            "layout_type": "cover",
            "visual_elements": [{"type": "title-block"}, {"type": "source-count", "value": 4}],
        }
        score, issues = _score_visual_fit_deterministic(slide)
        self.assertGreaterEqual(score, 0.9)


class NarrativeGradeReportTests(unittest.TestCase):
    """NarrativeGradeReport 数据类测试。"""

    def test_report_status_pass_when_all_high(self) -> None:
        items = [
            NarrativeGradeItem("s1", "cover", 0.9, 0.8, 0.9),
            NarrativeGradeItem("s2", "timeline", 0.8, 0.9, 0.8),
        ]
        report = NarrativeGradeReport(items=items)
        self.assertEqual(report.status, "pass")

    def test_report_status_fail_when_low_composite(self) -> None:
        items = [
            NarrativeGradeItem("s1", "cover", 0.9, 0.8, 0.9),
            NarrativeGradeItem("s2", "timeline", 0.1, 0.1, 0.1, issues=["bad"]),
        ]
        report = NarrativeGradeReport(items=items)
        self.assertEqual(report.status, "fail")

    def test_report_as_dict_structure(self) -> None:
        items = [NarrativeGradeItem("s1", "cover", 0.9, 0.8, 0.9)]
        report = NarrativeGradeReport(items=items)
        d = report.as_dict()
        self.assertIn("status", d)
        self.assertIn("mode", d)
        self.assertIn("avg_coherence", d)
        self.assertIn("avg_grounding", d)
        self.assertIn("avg_visual_fit", d)
        self.assertIn("avg_composite", d)
        self.assertIn("slides", d)
        self.assertEqual(len(d["slides"]), 1)
        self.assertIn("composite_score", d["slides"][0])

    def test_empty_report_fails(self) -> None:
        report = NarrativeGradeReport(items=[])
        self.assertEqual(report.status, "fail")
        self.assertEqual(report.avg_composite, 0.0)

    def test_all_issues_aggregated(self) -> None:
        items = [
            NarrativeGradeItem("s1", "cover", 0.5, 0.5, 0.5, issues=["issue1"]),
            NarrativeGradeItem("s2", "timeline", 0.5, 0.5, 0.5, issues=["issue2", "issue3"]),
        ]
        report = NarrativeGradeReport(items=items)
        self.assertEqual(len(report.all_issues), 3)
        self.assertTrue(all("[s" in i for i in report.all_issues))


class DeterministicNarrativeGradingTests(unittest.TestCase):
    """确定性叙事评分集成测试。"""

    def test_strongest_demo_passes_narrative_grading(self) -> None:
        normalized = load_json(STRONGEST_DEMO_NORMALIZED)
        slide_spec = load_json(STRONGEST_DEMO_SLIDE_SPEC)
        report = grade_narrative_deterministic(normalized, slide_spec)
        self.assertEqual(report.status, "pass")
        self.assertEqual(report.slide_count, len(slide_spec["slides"]))

    def test_strongest_demo_all_slides_above_threshold(self) -> None:
        normalized = load_json(STRONGEST_DEMO_NORMALIZED)
        slide_spec = load_json(STRONGEST_DEMO_SLIDE_SPEC)
        report = grade_narrative_deterministic(normalized, slide_spec)
        for item in report.items:
            self.assertGreaterEqual(
                item.composite_score, 0.6,
                f"slide {item.slide_id} composite_score {item.composite_score} < 0.6",
            )

    def test_strongest_demo_avg_composite_above_07(self) -> None:
        normalized = load_json(STRONGEST_DEMO_NORMALIZED)
        slide_spec = load_json(STRONGEST_DEMO_SLIDE_SPEC)
        report = grade_narrative_deterministic(normalized, slide_spec)
        self.assertGreaterEqual(report.avg_composite, 0.7)

    def test_strongest_demo_mode_is_deterministic(self) -> None:
        normalized = load_json(STRONGEST_DEMO_NORMALIZED)
        slide_spec = load_json(STRONGEST_DEMO_SLIDE_SPEC)
        report = grade_narrative_deterministic(normalized, slide_spec)
        self.assertEqual(report.mode, "deterministic")


class ModelAssistedNarrativeGradingTests(unittest.TestCase):
    """模型辅助叙事评分测试。"""

    def test_model_callback_used_when_provided(self) -> None:
        normalized = load_json(STRONGEST_DEMO_NORMALIZED)
        slide_spec = load_json(STRONGEST_DEMO_SLIDE_SPEC)

        def fake_callback(prompts: dict, spec: dict) -> dict:
            # 返回每个 slide 的高分
            return {
                "slides": [
                    {
                        "slide_id": s["slide_id"],
                        "coherence_score": 0.95,
                        "grounding_score": 0.9,
                        "visual_fit_score": 0.92,
                        "issues": [],
                    }
                    for s in spec["slides"]
                ]
            }

        report = grade_narrative(normalized, slide_spec, callback=fake_callback)
        self.assertEqual(report.mode, "model-assisted")
        self.assertEqual(report.status, "pass")
        self.assertGreaterEqual(report.avg_composite, 0.9)

    def test_model_callback_failure_falls_back_to_deterministic(self) -> None:
        normalized = load_json(STRONGEST_DEMO_NORMALIZED)
        slide_spec = load_json(STRONGEST_DEMO_SLIDE_SPEC)

        def failing_callback(prompts: dict, spec: dict) -> dict:
            raise RuntimeError("model unavailable")

        report = grade_narrative(normalized, slide_spec, callback=failing_callback)
        # 应回退到确定性模式
        self.assertEqual(report.mode, "deterministic")
        self.assertEqual(report.status, "pass")

    def test_no_callback_uses_deterministic(self) -> None:
        normalized = load_json(STRONGEST_DEMO_NORMALIZED)
        slide_spec = load_json(STRONGEST_DEMO_SLIDE_SPEC)
        report = grade_narrative(normalized, slide_spec)
        self.assertEqual(report.mode, "deterministic")


class NarrativePromptsTests(unittest.TestCase):
    """叙事评分 prompt 构建测试。"""

    def test_system_prompt_includes_scoring_dimensions(self) -> None:
        prompt = build_narrative_grader_system_prompt()
        self.assertIn("coherence_score", prompt)
        self.assertIn("grounding_score", prompt)
        self.assertIn("visual_fit_score", prompt)
        self.assertIn("0.0-1.0", prompt)

    def test_user_prompt_includes_pack_and_spec(self) -> None:
        normalized = load_json(STRONGEST_DEMO_NORMALIZED)
        slide_spec = load_json(STRONGEST_DEMO_SLIDE_SPEC)
        prompt = build_narrative_grader_user_prompt(normalized, slide_spec)
        self.assertIn("normalized_pack=", prompt)
        self.assertIn("slide_spec=", prompt)
        self.assertIn("china-ev-market-entry", prompt)


if __name__ == "__main__":
    unittest.main()
