# Start Here

[English](START-HERE.md) | [简体中文](START-HERE.zh-CN.md)

当一个新的 AI 会话需要快速继续 GroundedDeck 时，先读这个文件。

## 30 秒启动

1. 阅读 [AGENTS.zh-CN.md](AGENTS.zh-CN.md)。
2. 阅读 [docs/PROJECT-STATE.zh-CN.md](docs/PROJECT-STATE.zh-CN.md)。
3. 阅读 [docs/LATEST-HANDOFF.zh-CN.md](docs/LATEST-HANDOFF.zh-CN.md)。
4. 如果任务涉及定时任务或已恢复的 worktree，阅读 [docs/AUTOMATION-GOVERNANCE.zh-CN.md](docs/AUTOMATION-GOVERNANCE.zh-CN.md)。
5. 运行 `make context`。

## 这个项目是什么

GroundedDeck 是一个本地优先、基于来源材料约束的演示文稿系统，目标是达到接近 NotebookLM 的成稿质量，同时保证输出可编辑，并对中文场景提供更强支持。

它不是什么：

- 不是只靠单次 prompt 生成 PPT 的工具
- 不是以 renderer 为中心的项目
- 不是通用的模板填充器

## 接下来该做什么

默认遵循 [docs/PROJECT-STATE.zh-CN.md](docs/PROJECT-STATE.zh-CN.md) 里 `Current Next Action` 的单一下一步；如果 [docs/LATEST-HANDOFF.zh-CN.md](docs/LATEST-HANDOFF.zh-CN.md) 记录了某个未完成任务的更具体恢复点，则以 handoff 为准。如果未完成工作来自 automation 分支或 worktree，则按照 [docs/AUTOMATION-GOVERNANCE.zh-CN.md](docs/AUTOMATION-GOVERNANCE.zh-CN.md) 的 curator 规则恢复。

## 结束本次会话前

- 更新 [docs/LATEST-HANDOFF.zh-CN.md](docs/LATEST-HANDOFF.zh-CN.md)
- 更新 [docs/TASK-BOARD.zh-CN.md](docs/TASK-BOARD.zh-CN.md)
- 如果项目状态发生变化，更新 [docs/PROJECT-STATE.zh-CN.md](docs/PROJECT-STATE.zh-CN.md)
- 运行 `make eval`
