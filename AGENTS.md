# AGENTS

## 中文说明

这个仓库面向长期、跨会话的 AI 驱动开发。聊天历史不是可信记忆，仓库本身才是可持续的上下文来源。

This repository is designed for long-running AI-driven development. Do not depend on chat history as the source of truth. The repository itself is the durable memory.

## Required Read Order

## 必读顺序

Before making changes, read these files in order:

在开始修改之前，按顺序阅读以下文件：

1. [START-HERE.md](START-HERE.md)
2. [README.md](README.md)
3. [docs/PROJECT-STATE.md](docs/PROJECT-STATE.md)
4. [docs/LATEST-HANDOFF.md](docs/LATEST-HANDOFF.md)
5. [docs/ARCHITECTURE-DECISIONS.md](docs/ARCHITECTURE-DECISIONS.md)
6. [docs/architecture.md](docs/architecture.md)
7. [docs/evaluation-plan.md](docs/evaluation-plan.md)

## Operating Contract

## 操作契约

- Treat repository docs as canonical memory.
- Do not rely on prior conversation state when repo docs disagree.
- Use [docs/LATEST-HANDOFF.md](docs/LATEST-HANDOFF.md) as the first session-to-session resume artifact.
- Do not change architecture boundaries without updating [docs/ARCHITECTURE-DECISIONS.md](docs/ARCHITECTURE-DECISIONS.md).
- Do not finish a task without updating [docs/PROJECT-STATE.md](docs/PROJECT-STATE.md) when project state changed.
- Do not leave an in-progress task without updating [docs/LATEST-HANDOFF.md](docs/LATEST-HANDOFF.md) and [docs/TASK-BOARD.md](docs/TASK-BOARD.md).
- Keep the current next action explicit and singular.
- Preserve the `slide spec` intermediate representation as the stable contract between planning, rendering, and grading.
- Run `make eval` before considering a task complete.

- 将仓库文档视为规范记忆。
- 当仓库文档与此前对话冲突时，以仓库文档为准。
- 使用 [docs/LATEST-HANDOFF.md](docs/LATEST-HANDOFF.md) 作为跨会话恢复的首要工件。
- 不要在未更新 [docs/ARCHITECTURE-DECISIONS.md](docs/ARCHITECTURE-DECISIONS.md) 的情况下改变架构边界。
- 如果项目状态发生变化，不要在未更新 [docs/PROJECT-STATE.md](docs/PROJECT-STATE.md) 的情况下结束任务。
- 如果留下未完成任务，不要在未更新 [docs/LATEST-HANDOFF.md](docs/LATEST-HANDOFF.md) 和 [docs/TASK-BOARD.md](docs/TASK-BOARD.md) 的情况下离开。
- 始终保持当前下一步唯一且明确。
- 保留 `slide spec` 作为 planning、rendering 和 grading 之间的稳定契约。
- 在认为任务完成之前运行 `make eval`。

## Anti-Drift Rules

## 防漂移规则

- No direct “one giant prompt” architecture.
- No renderer-owned content understanding.
- No final artifact generation without auditable intermediate state.
- No silent removal of coverage, grounding, or editability requirements.
- No scope expansion without recording the decision and why it was accepted.

- 不允许直接走“一个巨型 prompt”架构。
- 不允许由 renderer 承担内容理解。
- 没有可审计的中间状态时，不允许生成最终工件。
- 不允许静默删除 coverage、grounding 或可编辑性要求。
- 没有记录决策及其原因时，不允许扩张 scope。

## Completion Protocol

## 完成协议

When finishing meaningful work:

完成有意义的工作时：

1. update docs that changed the canonical project memory
2. update current status and next step
3. update handoff and task board files
4. run `make eval`
5. leave the repository in a state where a future agent can continue from repo context alone

1. 更新那些改变了规范项目记忆的文档
2. 更新当前状态和下一步
3. 更新 handoff 和 task board
4. 运行 `make eval`
5. 让仓库处于未来 agent 只靠仓库上下文就能继续的状态
