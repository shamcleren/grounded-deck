"""Continuity artifact 质量评估器：检查仓库的 AI 连续性文件是否完整、一致、新鲜。

该模块实现 evaluation-plan.md 中的 continuity grading 能力：
- 检查所有 continuity artifacts 是否存在且包含必需的结构
- 检查 handoff 和 task-board 的新鲜度（是否与 PROJECT-STATE 一致）
- 检查跨文件的一致性（next action 是否对齐、状态是否同步）
- 确保未来的 AI agent 可以仅从仓库状态安全恢复
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---------- 评分结果数据结构 ----------

@dataclass(frozen=True)
class ContinuityCheckItem:
    """单个 continuity 检查项的结果。"""

    name: str
    category: str  # structure | consistency | freshness
    ok: bool
    detail: str
    severity: str = "error"  # error | warning


@dataclass
class ContinuityGradeReport:
    """完整的 continuity 质量评分报告。"""

    items: list[ContinuityCheckItem] = field(default_factory=list)

    @property
    def passed(self) -> int:
        return sum(1 for i in self.items if i.ok)

    @property
    def failed(self) -> int:
        return sum(1 for i in self.items if not i.ok and i.severity == "error")

    @property
    def warnings(self) -> int:
        return sum(1 for i in self.items if not i.ok and i.severity == "warning")

    @property
    def total(self) -> int:
        return len(self.items)

    @property
    def status(self) -> str:
        """pass 如果没有 error 级别的失败，否则 fail。"""
        return "pass" if self.failed == 0 else "fail"

    @property
    def error_items(self) -> list[ContinuityCheckItem]:
        return [i for i in self.items if not i.ok and i.severity == "error"]

    @property
    def warning_items(self) -> list[ContinuityCheckItem]:
        return [i for i in self.items if not i.ok and i.severity == "warning"]

    def as_dict(self) -> dict:
        """转换为可序列化的 dict。"""
        return {
            "status": self.status,
            "passed": self.passed,
            "failed": self.failed,
            "warnings": self.warnings,
            "total": self.total,
            "errors": [
                {"name": i.name, "category": i.category, "detail": i.detail}
                for i in self.error_items
            ],
            "warning_details": [
                {"name": i.name, "category": i.category, "detail": i.detail}
                for i in self.warning_items
            ],
            "checks": [
                {
                    "name": i.name,
                    "category": i.category,
                    "ok": i.ok,
                    "detail": i.detail,
                    "severity": i.severity,
                }
                for i in self.items
            ],
        }


# ---------- 辅助函数 ----------

def _read_text(path: Path) -> str | None:
    """安全读取文件内容，不存在时返回 None。"""
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def _extract_sections(text: str) -> dict[str, str]:
    """从 Markdown 文本中提取 ## 级别的 section 标题和内容。"""
    sections: dict[str, str] = {}
    current_heading = ""
    current_lines: list[str] = []

    for line in text.split("\n"):
        match = re.match(r"^##\s+(.+)$", line)
        if match:
            if current_heading:
                sections[current_heading] = "\n".join(current_lines).strip()
            current_heading = match.group(1).strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_heading:
        sections[current_heading] = "\n".join(current_lines).strip()

    return sections


def _extract_bullet_items(section_text: str) -> list[str]:
    """从 section 文本中提取 bullet 列表项（- 开头的行）。"""
    items: list[str] = []
    for line in section_text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
    return items


# ---------- 结构完整性检查 ----------

def _check_file_exists(path: Path, name: str) -> ContinuityCheckItem:
    """检查文件是否存在。"""
    if path.exists():
        return ContinuityCheckItem(
            name=f"{name}_exists",
            category="structure",
            ok=True,
            detail=f"{name} present",
        )
    return ContinuityCheckItem(
        name=f"{name}_exists",
        category="structure",
        ok=False,
        detail=f"{name} missing: {path}",
    )


def _check_required_sections(
    text: str | None,
    file_name: str,
    required_sections: list[str],
) -> list[ContinuityCheckItem]:
    """检查文件是否包含所有必需的 section。"""
    items: list[ContinuityCheckItem] = []

    if text is None:
        items.append(
            ContinuityCheckItem(
                name=f"{file_name}_sections",
                category="structure",
                ok=False,
                detail=f"{file_name} not readable",
            )
        )
        return items

    sections = _extract_sections(text)
    section_names = set(sections.keys())

    for required in required_sections:
        found = required in section_names
        items.append(
            ContinuityCheckItem(
                name=f"{file_name}_section_{required.lower().replace(' ', '_')}",
                category="structure",
                ok=found,
                detail=f"section '{required}' {'present' if found else 'missing'} in {file_name}",
            )
        )

    return items


def _check_section_non_empty(
    text: str | None,
    file_name: str,
    section_name: str,
    severity: str = "error",
) -> ContinuityCheckItem:
    """检查指定 section 是否非空。"""
    if text is None:
        return ContinuityCheckItem(
            name=f"{file_name}_{section_name.lower().replace(' ', '_')}_non_empty",
            category="structure",
            ok=False,
            detail=f"{file_name} not readable",
            severity=severity,
        )

    sections = _extract_sections(text)
    content = sections.get(section_name, "").strip()

    return ContinuityCheckItem(
        name=f"{file_name}_{section_name.lower().replace(' ', '_')}_non_empty",
        category="structure",
        ok=bool(content),
        detail=f"section '{section_name}' in {file_name} is {'non-empty' if content else 'empty'}",
        severity=severity,
    )


# ---------- 跨文件一致性检查 ----------

def _check_next_action_alignment(
    project_state_text: str | None,
    handoff_text: str | None,
    task_board_text: str | None,
) -> list[ContinuityCheckItem]:
    """检查 PROJECT-STATE、LATEST-HANDOFF、TASK-BOARD 中的 next action 是否对齐。

    不要求完全相同的文字，但要求语义上一致（通过关键词重叠检测）。
    """
    items: list[ContinuityCheckItem] = []

    # 提取各文件中的 next action 内容
    ps_next = ""
    if project_state_text:
        ps_sections = _extract_sections(project_state_text)
        ps_next = ps_sections.get("Current Next Action", "").strip().lower()

    hf_next = ""
    if handoff_text:
        hf_sections = _extract_sections(handoff_text)
        hf_next = hf_sections.get("Immediate Next Action", "").strip().lower()

    tb_in_progress = ""
    if task_board_text:
        tb_sections = _extract_sections(task_board_text)
        tb_in_progress = tb_sections.get("In Progress", "").strip().lower()

    # 检查 PROJECT-STATE 和 HANDOFF 的 next action 是否有关键词重叠
    if ps_next and hf_next:
        ps_words = set(re.findall(r"\w+", ps_next)) - {"the", "a", "an", "and", "or", "is", "to", "from", "for", "in", "on", "of"}
        hf_words = set(re.findall(r"\w+", hf_next)) - {"the", "a", "an", "and", "or", "is", "to", "from", "for", "in", "on", "of"}
        overlap = ps_words & hf_words
        # 至少有 3 个有意义的关键词重叠
        aligned = len(overlap) >= 3
        items.append(
            ContinuityCheckItem(
                name="next_action_ps_hf_alignment",
                category="consistency",
                ok=aligned,
                detail=(
                    f"PROJECT-STATE and HANDOFF next action aligned ({len(overlap)} keyword overlap)"
                    if aligned
                    else f"PROJECT-STATE and HANDOFF next action may be misaligned (only {len(overlap)} keyword overlap)"
                ),
                severity="warning" if not aligned else "error",
            )
        )
    elif not ps_next:
        items.append(
            ContinuityCheckItem(
                name="next_action_ps_hf_alignment",
                category="consistency",
                ok=False,
                detail="PROJECT-STATE 'Current Next Action' section is empty",
            )
        )

    # 检查 TASK-BOARD In Progress 是否与 next action 有关键词重叠
    if tb_in_progress and (ps_next or hf_next):
        reference = ps_next or hf_next
        ref_words = set(re.findall(r"\w+", reference)) - {"the", "a", "an", "and", "or", "is", "to", "from", "for", "in", "on", "of"}
        tb_words = set(re.findall(r"\w+", tb_in_progress)) - {"the", "a", "an", "and", "or", "is", "to", "from", "for", "in", "on", "of"}
        overlap = ref_words & tb_words
        aligned = len(overlap) >= 3
        items.append(
            ContinuityCheckItem(
                name="next_action_tb_alignment",
                category="consistency",
                ok=aligned,
                detail=(
                    f"TASK-BOARD In Progress aligned with next action ({len(overlap)} keyword overlap)"
                    if aligned
                    else f"TASK-BOARD In Progress may be misaligned with next action (only {len(overlap)} keyword overlap)"
                ),
                severity="warning" if not aligned else "error",
            )
        )

    return items


def _check_task_board_structure(
    task_board_text: str | None,
) -> list[ContinuityCheckItem]:
    """检查 TASK-BOARD 的结构完整性。"""
    items: list[ContinuityCheckItem] = []

    if task_board_text is None:
        items.append(
            ContinuityCheckItem(
                name="task_board_structure",
                category="structure",
                ok=False,
                detail="TASK-BOARD not readable",
            )
        )
        return items

    sections = _extract_sections(task_board_text)

    # In Progress 应该有内容
    in_progress = sections.get("In Progress", "").strip()
    items.append(
        ContinuityCheckItem(
            name="task_board_in_progress_non_empty",
            category="freshness",
            ok=bool(in_progress),
            detail=(
                "TASK-BOARD has active In Progress items"
                if in_progress
                else "TASK-BOARD In Progress is empty — no active work tracked"
            ),
            severity="warning",
        )
    )

    # Recently Completed 应该有内容（表明有工作记录）
    recently_completed = sections.get("Recently Completed", "").strip()
    items.append(
        ContinuityCheckItem(
            name="task_board_recently_completed_non_empty",
            category="freshness",
            ok=bool(recently_completed),
            detail=(
                "TASK-BOARD has Recently Completed items"
                if recently_completed
                else "TASK-BOARD Recently Completed is empty — no work history"
            ),
            severity="warning",
        )
    )

    # Ready Next 应该有内容（表明有规划）
    ready_next = sections.get("Ready Next", "").strip()
    items.append(
        ContinuityCheckItem(
            name="task_board_ready_next_non_empty",
            category="freshness",
            ok=bool(ready_next),
            detail=(
                "TASK-BOARD has Ready Next items"
                if ready_next
                else "TASK-BOARD Ready Next is empty — no planned work"
            ),
            severity="warning",
        )
    )

    return items


def _check_handoff_completeness(
    handoff_text: str | None,
) -> list[ContinuityCheckItem]:
    """检查 LATEST-HANDOFF 的完整性。"""
    items: list[ContinuityCheckItem] = []

    if handoff_text is None:
        items.append(
            ContinuityCheckItem(
                name="handoff_completeness",
                category="structure",
                ok=False,
                detail="LATEST-HANDOFF not readable",
            )
        )
        return items

    sections = _extract_sections(handoff_text)

    # What Was Just Completed 应该有内容
    completed = sections.get("What Was Just Completed", "").strip()
    items.append(
        ContinuityCheckItem(
            name="handoff_completed_non_empty",
            category="freshness",
            ok=bool(completed),
            detail=(
                "HANDOFF has completed work description"
                if completed
                else "HANDOFF 'What Was Just Completed' is empty"
            ),
        )
    )

    # Current Status 应该有内容
    status = sections.get("Current Status", "").strip()
    items.append(
        ContinuityCheckItem(
            name="handoff_status_non_empty",
            category="freshness",
            ok=bool(status),
            detail=(
                "HANDOFF has current status description"
                if status
                else "HANDOFF 'Current Status' is empty"
            ),
        )
    )

    # Immediate Next Action 应该有内容
    next_action = sections.get("Immediate Next Action", "").strip()
    items.append(
        ContinuityCheckItem(
            name="handoff_next_action_non_empty",
            category="freshness",
            ok=bool(next_action),
            detail=(
                "HANDOFF has immediate next action"
                if next_action
                else "HANDOFF 'Immediate Next Action' is empty"
            ),
        )
    )

    # Resume Hint 应该有内容
    resume = sections.get("Resume Hint", "").strip()
    items.append(
        ContinuityCheckItem(
            name="handoff_resume_hint_non_empty",
            category="freshness",
            ok=bool(resume),
            detail=(
                "HANDOFF has resume hint"
                if resume
                else "HANDOFF 'Resume Hint' is empty"
            ),
            severity="warning",
        )
    )

    # Do Not Drift 应该有内容
    drift = sections.get("Do Not Drift", "").strip()
    items.append(
        ContinuityCheckItem(
            name="handoff_do_not_drift_present",
            category="structure",
            ok=bool(drift),
            detail=(
                "HANDOFF has anti-drift rules"
                if drift
                else "HANDOFF 'Do Not Drift' is empty"
            ),
            severity="warning",
        )
    )

    return items


def _check_project_state_completeness(
    project_state_text: str | None,
) -> list[ContinuityCheckItem]:
    """检查 PROJECT-STATE 的完整性。"""
    items: list[ContinuityCheckItem] = []

    if project_state_text is None:
        items.append(
            ContinuityCheckItem(
                name="project_state_completeness",
                category="structure",
                ok=False,
                detail="PROJECT-STATE not readable",
            )
        )
        return items

    sections = _extract_sections(project_state_text)

    # Current Phase 应该有内容
    phase = sections.get("Current Phase", "").strip()
    items.append(
        ContinuityCheckItem(
            name="project_state_current_phase_non_empty",
            category="freshness",
            ok=bool(phase),
            detail=(
                "PROJECT-STATE has current phase description"
                if phase
                else "PROJECT-STATE 'Current Phase' is empty"
            ),
        )
    )

    # Completed So Far 应该有内容
    completed = sections.get("Completed So Far", "").strip()
    items.append(
        ContinuityCheckItem(
            name="project_state_completed_non_empty",
            category="freshness",
            ok=bool(completed),
            detail=(
                "PROJECT-STATE has completed work history"
                if completed
                else "PROJECT-STATE 'Completed So Far' is empty"
            ),
        )
    )

    # Current Next Action 应该有内容
    next_action = sections.get("Current Next Action", "").strip()
    items.append(
        ContinuityCheckItem(
            name="project_state_next_action_non_empty",
            category="freshness",
            ok=bool(next_action),
            detail=(
                "PROJECT-STATE has current next action"
                if next_action
                else "PROJECT-STATE 'Current Next Action' is empty"
            ),
        )
    )

    # Active Constraints 应该有内容
    constraints = sections.get("Active Constraints", "").strip()
    items.append(
        ContinuityCheckItem(
            name="project_state_constraints_non_empty",
            category="structure",
            ok=bool(constraints),
            detail=(
                "PROJECT-STATE has active constraints"
                if constraints
                else "PROJECT-STATE 'Active Constraints' is empty"
            ),
            severity="warning",
        )
    )

    return items


def _check_agents_contract(
    agents_text: str | None,
) -> list[ContinuityCheckItem]:
    """检查 AGENTS.md 的操作契约完整性。"""
    items: list[ContinuityCheckItem] = []

    if agents_text is None:
        items.append(
            ContinuityCheckItem(
                name="agents_contract",
                category="structure",
                ok=False,
                detail="AGENTS.md not readable",
            )
        )
        return items

    sections = _extract_sections(agents_text)

    # Operating Contract 应该有内容
    contract = sections.get("Operating Contract", "").strip()
    items.append(
        ContinuityCheckItem(
            name="agents_operating_contract_non_empty",
            category="structure",
            ok=bool(contract),
            detail=(
                "AGENTS has operating contract"
                if contract
                else "AGENTS 'Operating Contract' is empty"
            ),
        )
    )

    # Operating Contract 应该包含关键规则
    if contract:
        key_rules = [
            "LATEST-HANDOFF",
            "PROJECT-STATE",
            "TASK-BOARD",
            "make eval",
        ]
        missing_rules = [r for r in key_rules if r.lower() not in contract.lower()]
        items.append(
            ContinuityCheckItem(
                name="agents_contract_key_rules",
                category="structure",
                ok=len(missing_rules) == 0,
                detail=(
                    "AGENTS operating contract references all key artifacts"
                    if not missing_rules
                    else f"AGENTS operating contract missing references to: {', '.join(missing_rules)}"
                ),
                severity="warning",
            )
        )

    # Anti-Drift Rules 应该有内容
    anti_drift = sections.get("Anti-Drift Rules", "").strip()
    items.append(
        ContinuityCheckItem(
            name="agents_anti_drift_non_empty",
            category="structure",
            ok=bool(anti_drift),
            detail=(
                "AGENTS has anti-drift rules"
                if anti_drift
                else "AGENTS 'Anti-Drift Rules' is empty"
            ),
        )
    )

    # Completion Protocol 应该有内容
    completion = sections.get("Completion Protocol", "").strip()
    items.append(
        ContinuityCheckItem(
            name="agents_completion_protocol_non_empty",
            category="structure",
            ok=bool(completion),
            detail=(
                "AGENTS has completion protocol"
                if completion
                else "AGENTS 'Completion Protocol' is empty"
            ),
        )
    )

    return items


def _check_start_here_resume_path(
    start_here_text: str | None,
) -> list[ContinuityCheckItem]:
    """检查 START-HERE.md 是否提供了清晰的恢复路径。"""
    items: list[ContinuityCheckItem] = []

    if start_here_text is None:
        items.append(
            ContinuityCheckItem(
                name="start_here_resume_path",
                category="structure",
                ok=False,
                detail="START-HERE.md not readable",
            )
        )
        return items

    # 应该引用 AGENTS.md 和 PROJECT-STATE.md
    references = ["AGENTS.md", "PROJECT-STATE.md", "LATEST-HANDOFF.md"]
    missing = [r for r in references if r not in start_here_text]
    items.append(
        ContinuityCheckItem(
            name="start_here_references",
            category="structure",
            ok=len(missing) == 0,
            detail=(
                "START-HERE references all key continuity files"
                if not missing
                else f"START-HERE missing references to: {', '.join(missing)}"
            ),
        )
    )

    # 应该有 30-Second Startup section
    sections = _extract_sections(start_here_text)
    startup = sections.get("30-Second Startup", "").strip()
    items.append(
        ContinuityCheckItem(
            name="start_here_startup_non_empty",
            category="structure",
            ok=bool(startup),
            detail=(
                "START-HERE has 30-Second Startup instructions"
                if startup
                else "START-HERE '30-Second Startup' is empty"
            ),
        )
    )

    return items


# ---------- 主入口 ----------

def grade_continuity_artifacts(
    root: str | Path,
) -> ContinuityGradeReport:
    """对仓库的 continuity artifacts 执行完整的质量评估。

    检查维度：
    1. structure: 文件存在性、必需 section、关键引用
    2. consistency: 跨文件的 next action 对齐
    3. freshness: handoff 和 task-board 的内容新鲜度

    参数：
        root: 仓库根目录路径

    返回：
        ContinuityGradeReport 包含所有检查结果
    """
    root = Path(root)
    report = ContinuityGradeReport()

    # ---------- 定义文件路径 ----------
    agents_path = root / "AGENTS.md"
    start_here_path = root / "START-HERE.md"
    project_state_path = root / "docs" / "PROJECT-STATE.md"
    handoff_path = root / "docs" / "LATEST-HANDOFF.md"
    task_board_path = root / "docs" / "TASK-BOARD.md"
    arch_decisions_path = root / "docs" / "ARCHITECTURE-DECISIONS.md"

    # ---------- 1. 文件存在性检查 ----------
    file_checks = [
        (agents_path, "AGENTS.md"),
        (start_here_path, "START-HERE.md"),
        (project_state_path, "PROJECT-STATE.md"),
        (handoff_path, "LATEST-HANDOFF.md"),
        (task_board_path, "TASK-BOARD.md"),
        (arch_decisions_path, "ARCHITECTURE-DECISIONS.md"),
    ]
    for path, name in file_checks:
        report.items.append(_check_file_exists(path, name))

    # ---------- 2. 读取文件内容 ----------
    agents_text = _read_text(agents_path)
    start_here_text = _read_text(start_here_path)
    project_state_text = _read_text(project_state_path)
    handoff_text = _read_text(handoff_path)
    task_board_text = _read_text(task_board_path)
    arch_decisions_text = _read_text(arch_decisions_path)

    # ---------- 3. 结构完整性检查 ----------
    # AGENTS.md
    report.items.extend(_check_agents_contract(agents_text))

    # START-HERE.md
    report.items.extend(_check_start_here_resume_path(start_here_text))

    # PROJECT-STATE.md
    report.items.extend(
        _check_required_sections(
            project_state_text,
            "PROJECT-STATE.md",
            ["Current Phase", "Completed So Far", "Current Next Action", "Active Constraints"],
        )
    )
    report.items.extend(_check_project_state_completeness(project_state_text))

    # LATEST-HANDOFF.md
    report.items.extend(
        _check_required_sections(
            handoff_text,
            "LATEST-HANDOFF.md",
            [
                "What Was Just Completed",
                "Current Status",
                "Immediate Next Action",
                "Resume Hint",
            ],
        )
    )
    report.items.extend(_check_handoff_completeness(handoff_text))

    # TASK-BOARD.md
    report.items.extend(
        _check_required_sections(
            task_board_text,
            "TASK-BOARD.md",
            ["In Progress", "Ready Next", "Update Rule"],
        )
    )
    report.items.extend(_check_task_board_structure(task_board_text))

    # ARCHITECTURE-DECISIONS.md
    report.items.extend(
        _check_required_sections(
            arch_decisions_text,
            "ARCHITECTURE-DECISIONS.md",
            ["Fixed Invariants", "Decision Log", "Change Policy"],
        )
    )

    # ---------- 4. 跨文件一致性检查 ----------
    report.items.extend(
        _check_next_action_alignment(
            project_state_text,
            handoff_text,
            task_board_text,
        )
    )

    return report
