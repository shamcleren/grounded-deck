# AGENTS

[English](AGENTS.md) | [简体中文](AGENTS.zh-CN.md)

这个仓库面向长期、跨会话的 AI 驱动开发。聊天历史不是可信记忆，仓库本身才是可持续的上下文来源。

## 必读顺序

在开始修改之前，按顺序阅读以下文件：

1. [START-HERE.zh-CN.md](START-HERE.zh-CN.md)
2. [README.zh-CN.md](README.zh-CN.md)
3. [docs/PROJECT-STATE.zh-CN.md](docs/PROJECT-STATE.zh-CN.md)
4. [docs/LATEST-HANDOFF.zh-CN.md](docs/LATEST-HANDOFF.zh-CN.md)
5. [docs/ARCHITECTURE-DECISIONS.zh-CN.md](docs/ARCHITECTURE-DECISIONS.zh-CN.md)
6. [docs/architecture.zh-CN.md](docs/architecture.zh-CN.md)
7. [docs/evaluation-plan.zh-CN.md](docs/evaluation-plan.zh-CN.md)
8. 如果任务涉及定时任务、worktree 或无人值守 AI 工作，再阅读 [docs/AUTOMATION-GOVERNANCE.zh-CN.md](docs/AUTOMATION-GOVERNANCE.zh-CN.md)

## 操作契约

- 将仓库文档视为规范记忆。
- 当仓库文档与此前对话冲突时，以仓库文档为准。
- 使用 [docs/LATEST-HANDOFF.zh-CN.md](docs/LATEST-HANDOFF.zh-CN.md) 作为跨会话恢复的首要工件。
- 不要在未更新 [docs/ARCHITECTURE-DECISIONS.zh-CN.md](docs/ARCHITECTURE-DECISIONS.zh-CN.md) 和对应英文文件的情况下改变架构边界。
- 如果项目状态发生变化，不要在未更新 [docs/PROJECT-STATE.zh-CN.md](docs/PROJECT-STATE.zh-CN.md) 和对应英文文件的情况下结束任务。
- 如果留下未完成任务，不要在未更新 [docs/LATEST-HANDOFF.zh-CN.md](docs/LATEST-HANDOFF.zh-CN.md) 和 [docs/TASK-BOARD.zh-CN.md](docs/TASK-BOARD.zh-CN.md) 的情况下离开。
- 始终保持当前下一步唯一且明确。
- 保留 `slide spec` 作为 planning、rendering 和 grading 之间的稳定契约。
- 任何定时、后台或多 worktree 的 AI 工作，都遵循 [docs/AUTOMATION-GOVERNANCE.zh-CN.md](docs/AUTOMATION-GOVERNANCE.zh-CN.md)。
- 在认为任务完成之前运行 `make eval`。

## 防漂移规则

- 不允许直接走“一个巨型 prompt”架构。
- 不允许由 renderer 承担内容理解。
- 没有可审计的中间状态时，不允许生成最终工件。
- 不允许静默删除 coverage、grounding 或可编辑性要求。
- 没有记录决策及其原因时，不允许扩张 scope。
- 不允许把 automation 的匿名改动遗留在 detached worktree 上。

## 完成协议

完成有意义的工作时：

1. 更新那些改变了规范项目记忆的文档
2. 更新当前状态和下一步
3. 更新 handoff 和 task board 文件
4. 运行 `make eval`
5. 让仓库处于未来 agent 只靠仓库上下文就能继续的状态
