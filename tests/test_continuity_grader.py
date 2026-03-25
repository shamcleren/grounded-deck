"""Continuity grader 测试：验证 continuity artifact 质量评估器的正确性。"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

# 确保项目根目录在 sys.path 中
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.quality.continuity_grader import (
    ContinuityCheckItem,
    ContinuityGradeReport,
    _check_agents_contract,
    _check_file_exists,
    _check_handoff_completeness,
    _check_next_action_alignment,
    _check_project_state_completeness,
    _check_required_sections,
    _check_section_non_empty,
    _check_start_here_resume_path,
    _check_task_board_structure,
    _extract_bullet_items,
    _extract_sections,
    grade_continuity_artifacts,
)


class TestContinuityCheckItem(unittest.TestCase):
    """ContinuityCheckItem 数据结构测试。"""

    def test_default_severity_is_error(self):
        item = ContinuityCheckItem(
            name="test", category="structure", ok=True, detail="ok"
        )
        self.assertEqual(item.severity, "error")

    def test_custom_severity(self):
        item = ContinuityCheckItem(
            name="test", category="structure", ok=False, detail="warn", severity="warning"
        )
        self.assertEqual(item.severity, "warning")


class TestContinuityGradeReport(unittest.TestCase):
    """ContinuityGradeReport 数据结构测试。"""

    def test_empty_report_passes(self):
        report = ContinuityGradeReport()
        self.assertEqual(report.status, "pass")
        self.assertEqual(report.passed, 0)
        self.assertEqual(report.failed, 0)
        self.assertEqual(report.total, 0)

    def test_all_passing(self):
        report = ContinuityGradeReport(items=[
            ContinuityCheckItem("a", "structure", True, "ok"),
            ContinuityCheckItem("b", "consistency", True, "ok"),
        ])
        self.assertEqual(report.status, "pass")
        self.assertEqual(report.passed, 2)
        self.assertEqual(report.failed, 0)

    def test_error_failure(self):
        report = ContinuityGradeReport(items=[
            ContinuityCheckItem("a", "structure", True, "ok"),
            ContinuityCheckItem("b", "structure", False, "missing", severity="error"),
        ])
        self.assertEqual(report.status, "fail")
        self.assertEqual(report.failed, 1)

    def test_warning_only_still_passes(self):
        report = ContinuityGradeReport(items=[
            ContinuityCheckItem("a", "structure", True, "ok"),
            ContinuityCheckItem("b", "freshness", False, "stale", severity="warning"),
        ])
        self.assertEqual(report.status, "pass")
        self.assertEqual(report.warnings, 1)
        self.assertEqual(report.failed, 0)

    def test_as_dict_structure(self):
        report = ContinuityGradeReport(items=[
            ContinuityCheckItem("a", "structure", True, "ok"),
            ContinuityCheckItem("b", "structure", False, "missing"),
        ])
        d = report.as_dict()
        self.assertIn("status", d)
        self.assertIn("passed", d)
        self.assertIn("failed", d)
        self.assertIn("warnings", d)
        self.assertIn("total", d)
        self.assertIn("errors", d)
        self.assertIn("checks", d)
        self.assertEqual(d["total"], 2)

    def test_error_items_and_warning_items(self):
        report = ContinuityGradeReport(items=[
            ContinuityCheckItem("a", "structure", False, "err", severity="error"),
            ContinuityCheckItem("b", "freshness", False, "warn", severity="warning"),
            ContinuityCheckItem("c", "structure", True, "ok"),
        ])
        self.assertEqual(len(report.error_items), 1)
        self.assertEqual(len(report.warning_items), 1)
        self.assertEqual(report.error_items[0].name, "a")
        self.assertEqual(report.warning_items[0].name, "b")


class TestHelperFunctions(unittest.TestCase):
    """辅助函数测试。"""

    def test_extract_sections(self):
        text = "# Title\n\n## Section A\ncontent a\n\n## Section B\ncontent b\n"
        sections = _extract_sections(text)
        self.assertIn("Section A", sections)
        self.assertIn("Section B", sections)
        self.assertIn("content a", sections["Section A"])

    def test_extract_sections_empty(self):
        sections = _extract_sections("")
        self.assertEqual(sections, {})

    def test_extract_bullet_items(self):
        text = "- item one\n- item two\nnot a bullet\n- item three"
        items = _extract_bullet_items(text)
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0], "item one")

    def test_extract_bullet_items_empty(self):
        items = _extract_bullet_items("no bullets here")
        self.assertEqual(items, [])


class TestFileExistsCheck(unittest.TestCase):
    """文件存在性检查测试。"""

    def test_existing_file(self):
        with tempfile.NamedTemporaryFile(suffix=".md") as f:
            result = _check_file_exists(Path(f.name), "test.md")
            self.assertTrue(result.ok)

    def test_missing_file(self):
        result = _check_file_exists(Path("/nonexistent/file.md"), "test.md")
        self.assertFalse(result.ok)
        self.assertEqual(result.category, "structure")


class TestRequiredSectionsCheck(unittest.TestCase):
    """必需 section 检查测试。"""

    def test_all_sections_present(self):
        text = "## Alpha\ncontent\n## Beta\ncontent\n"
        items = _check_required_sections(text, "test.md", ["Alpha", "Beta"])
        self.assertTrue(all(i.ok for i in items))

    def test_missing_section(self):
        text = "## Alpha\ncontent\n"
        items = _check_required_sections(text, "test.md", ["Alpha", "Beta"])
        alpha = [i for i in items if "Alpha" in i.detail][0]
        beta = [i for i in items if "Beta" in i.detail][0]
        self.assertTrue(alpha.ok)
        self.assertFalse(beta.ok)

    def test_none_text(self):
        items = _check_required_sections(None, "test.md", ["Alpha"])
        self.assertEqual(len(items), 1)
        self.assertFalse(items[0].ok)


class TestSectionNonEmptyCheck(unittest.TestCase):
    """Section 非空检查测试。"""

    def test_non_empty_section(self):
        text = "## Target\nsome content\n"
        result = _check_section_non_empty(text, "test.md", "Target")
        self.assertTrue(result.ok)

    def test_empty_section(self):
        text = "## Target\n\n## Other\ncontent\n"
        result = _check_section_non_empty(text, "test.md", "Target")
        self.assertFalse(result.ok)

    def test_missing_section(self):
        text = "## Other\ncontent\n"
        result = _check_section_non_empty(text, "test.md", "Target")
        self.assertFalse(result.ok)


class TestAgentsContractCheck(unittest.TestCase):
    """AGENTS.md 操作契约检查测试。"""

    def test_complete_agents(self):
        text = (
            "## Required Read Order\nfiles\n"
            "## Operating Contract\n"
            "- Use LATEST-HANDOFF.md\n"
            "- Update PROJECT-STATE.md\n"
            "- Update TASK-BOARD.md\n"
            "- Run make eval\n"
            "## Anti-Drift Rules\nrules\n"
            "## Completion Protocol\nsteps\n"
        )
        items = _check_agents_contract(text)
        errors = [i for i in items if not i.ok and i.severity == "error"]
        self.assertEqual(len(errors), 0)

    def test_missing_contract(self):
        text = "## Required Read Order\nfiles\n## Anti-Drift Rules\nrules\n"
        items = _check_agents_contract(text)
        contract_check = [i for i in items if "operating_contract" in i.name]
        self.assertTrue(any(not i.ok for i in contract_check))

    def test_none_text(self):
        items = _check_agents_contract(None)
        self.assertEqual(len(items), 1)
        self.assertFalse(items[0].ok)


class TestStartHereCheck(unittest.TestCase):
    """START-HERE.md 恢复路径检查测试。"""

    def test_complete_start_here(self):
        text = (
            "## 30-Second Startup\n"
            "1. Read AGENTS.md\n"
            "2. Read docs/PROJECT-STATE.md\n"
            "3. Read docs/LATEST-HANDOFF.md\n"
            "## What To Do Next\nfollow next action\n"
        )
        items = _check_start_here_resume_path(text)
        errors = [i for i in items if not i.ok and i.severity == "error"]
        self.assertEqual(len(errors), 0)

    def test_missing_references(self):
        text = "## 30-Second Startup\njust start\n"
        items = _check_start_here_resume_path(text)
        ref_check = [i for i in items if "references" in i.name]
        self.assertTrue(any(not i.ok for i in ref_check))


class TestProjectStateCheck(unittest.TestCase):
    """PROJECT-STATE.md 完整性检查测试。"""

    def test_complete_project_state(self):
        text = (
            "## Current Phase\nphase one\n"
            "## Completed So Far\n- item\n"
            "## Current Next Action\ndo something\n"
            "## Active Constraints\n- constraint\n"
        )
        items = _check_project_state_completeness(text)
        errors = [i for i in items if not i.ok and i.severity == "error"]
        self.assertEqual(len(errors), 0)

    def test_empty_next_action(self):
        text = (
            "## Current Phase\nphase one\n"
            "## Completed So Far\n- item\n"
            "## Current Next Action\n\n"
            "## Active Constraints\n- constraint\n"
        )
        items = _check_project_state_completeness(text)
        next_check = [i for i in items if "next_action" in i.name]
        self.assertTrue(any(not i.ok for i in next_check))


class TestHandoffCompletenessCheck(unittest.TestCase):
    """LATEST-HANDOFF.md 完整性检查测试。"""

    def test_complete_handoff(self):
        text = (
            "## What Was Just Completed\n- work done\n"
            "## Current Status\n- status\n"
            "## Immediate Next Action\ndo next\n"
            "## Resume Hint\nhint\n"
            "## Do Not Drift\n- rule\n"
        )
        items = _check_handoff_completeness(text)
        errors = [i for i in items if not i.ok and i.severity == "error"]
        self.assertEqual(len(errors), 0)

    def test_empty_next_action(self):
        text = (
            "## What Was Just Completed\n- work done\n"
            "## Current Status\n- status\n"
            "## Immediate Next Action\n\n"
            "## Resume Hint\nhint\n"
        )
        items = _check_handoff_completeness(text)
        next_check = [i for i in items if "next_action" in i.name]
        self.assertTrue(any(not i.ok for i in next_check))


class TestTaskBoardStructureCheck(unittest.TestCase):
    """TASK-BOARD.md 结构检查测试。"""

    def test_complete_task_board(self):
        text = (
            "## In Progress\n- task one\n"
            "## Recently Completed\n- done task\n"
            "## Ready Next\n- next task\n"
        )
        items = _check_task_board_structure(text)
        # 所有检查都是 warning 级别，所以即使失败也不影响 status
        self.assertTrue(all(i.severity == "warning" for i in items))

    def test_empty_in_progress(self):
        text = (
            "## In Progress\n\n"
            "## Recently Completed\n- done\n"
            "## Ready Next\n- next\n"
        )
        items = _check_task_board_structure(text)
        ip_check = [i for i in items if "in_progress" in i.name]
        self.assertTrue(any(not i.ok for i in ip_check))


class TestNextActionAlignmentCheck(unittest.TestCase):
    """跨文件 next action 对齐检查测试。"""

    def test_aligned_next_actions(self):
        ps = "## Current Next Action\nGrade continuity artifacts so future agents can safely resume\n"
        hf = "## Immediate Next Action\nGrade continuity artifacts so future agents can safely resume from repository state alone\n"
        tb = "## In Progress\n- grade continuity artifacts so future agents can safely resume from repository state alone\n"
        items = _check_next_action_alignment(ps, hf, tb)
        # 应该有足够的关键词重叠
        self.assertTrue(all(i.ok for i in items))

    def test_misaligned_next_actions(self):
        ps = "## Current Next Action\nBuild the renderer module\n"
        hf = "## Immediate Next Action\nFix the authentication bug in the login page\n"
        tb = "## In Progress\n- deploy to production\n"
        items = _check_next_action_alignment(ps, hf, tb)
        # 应该检测到不对齐
        misaligned = [i for i in items if not i.ok]
        self.assertTrue(len(misaligned) > 0)

    def test_empty_project_state_next_action(self):
        ps = "## Current Next Action\n\n"
        hf = "## Immediate Next Action\ndo something\n"
        tb = "## In Progress\n- task\n"
        items = _check_next_action_alignment(ps, hf, tb)
        empty_check = [i for i in items if "ps_hf" in i.name]
        self.assertTrue(any(not i.ok for i in empty_check))


class TestGradeContinuityArtifactsIntegration(unittest.TestCase):
    """grade_continuity_artifacts 集成测试。"""

    def test_with_real_repository(self):
        """对真实仓库执行 continuity grading。"""
        root = Path(__file__).resolve().parent.parent
        report = grade_continuity_artifacts(root)

        # 基本结构检查
        self.assertGreater(report.total, 0)
        self.assertIsInstance(report.status, str)
        self.assertIn(report.status, ("pass", "fail"))

        # 真实仓库应该通过所有 error 级别的检查
        if report.failed > 0:
            error_details = [
                f"{i.name}: {i.detail}" for i in report.error_items
            ]
            self.fail(
                f"Continuity grading failed with {report.failed} errors:\n"
                + "\n".join(error_details)
            )

    def test_with_empty_directory(self):
        """对空目录执行 continuity grading 应该失败。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            report = grade_continuity_artifacts(tmpdir)
            self.assertEqual(report.status, "fail")
            self.assertGreater(report.failed, 0)

    def test_with_minimal_valid_structure(self):
        """对最小有效结构执行 continuity grading。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            docs = root / "docs"
            docs.mkdir()

            # 创建最小有效的 continuity artifacts
            (root / "AGENTS.md").write_text(
                "# AGENTS\n\n"
                "## Required Read Order\n1. START-HERE.md\n\n"
                "## Operating Contract\n"
                "- Use LATEST-HANDOFF.md\n"
                "- Update PROJECT-STATE.md\n"
                "- Update TASK-BOARD.md\n"
                "- Run make eval\n\n"
                "## Anti-Drift Rules\n- no drift\n\n"
                "## Completion Protocol\n1. update docs\n",
                encoding="utf-8",
            )
            (root / "START-HERE.md").write_text(
                "# Start Here\n\n"
                "## 30-Second Startup\n"
                "1. Read AGENTS.md\n"
                "2. Read docs/PROJECT-STATE.md\n"
                "3. Read docs/LATEST-HANDOFF.md\n\n"
                "## What To Do Next\nfollow next action\n",
                encoding="utf-8",
            )
            (docs / "PROJECT-STATE.md").write_text(
                "# Project State\n\n"
                "## Current Phase\nphase one\n\n"
                "## Completed So Far\n- item\n\n"
                "## Current Next Action\ngrade continuity artifacts for safe resume\n\n"
                "## Active Constraints\n- local first\n",
                encoding="utf-8",
            )
            (docs / "LATEST-HANDOFF.md").write_text(
                "# Latest Handoff\n\n"
                "## What Was Just Completed\n- work\n\n"
                "## Current Status\n- ok\n\n"
                "## Immediate Next Action\ngrade continuity artifacts for safe agent resume\n\n"
                "## Resume Hint\nhint\n\n"
                "## Do Not Drift\n- rule\n",
                encoding="utf-8",
            )
            (docs / "TASK-BOARD.md").write_text(
                "# Task Board\n\n"
                "## In Progress\n- grade continuity artifacts for safe resume\n\n"
                "## Recently Completed\n- done\n\n"
                "## Ready Next\n- next\n\n"
                "## Update Rule\nupdate when done\n",
                encoding="utf-8",
            )
            (docs / "ARCHITECTURE-DECISIONS.md").write_text(
                "# Architecture Decisions\n\n"
                "## Fixed Invariants\n- invariant\n\n"
                "## Decision Log\n### AD-0001\n\n"
                "## Change Policy\npolicy\n",
                encoding="utf-8",
            )

            report = grade_continuity_artifacts(root)
            # 最小有效结构应该通过所有 error 级别的检查
            if report.failed > 0:
                error_details = [
                    f"{i.name}: {i.detail}" for i in report.error_items
                ]
                self.fail(
                    f"Minimal valid structure failed with {report.failed} errors:\n"
                    + "\n".join(error_details)
                )

    def test_report_serialization(self):
        """测试报告序列化。"""
        root = Path(__file__).resolve().parent.parent
        report = grade_continuity_artifacts(root)
        d = report.as_dict()
        self.assertIn("status", d)
        self.assertIn("checks", d)
        self.assertIsInstance(d["checks"], list)
        for check in d["checks"]:
            self.assertIn("name", check)
            self.assertIn("category", check)
            self.assertIn("ok", check)
            self.assertIn("detail", check)
            self.assertIn("severity", check)


if __name__ == "__main__":
    unittest.main()
