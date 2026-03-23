# Start Here

## 中文说明

当一个新的 AI 会话需要快速继续 GroundedDeck 时，先读这个文件。

Use this file when a new AI session needs to continue GroundedDeck quickly.

中文读者可先快速浏览 [docs/README.zh-CN.md](docs/README.zh-CN.md)。

## 30-Second Startup

## 30 秒启动

1. Read [AGENTS.md](AGENTS.md).
2. Read [docs/PROJECT-STATE.md](docs/PROJECT-STATE.md).
3. Read [docs/LATEST-HANDOFF.md](docs/LATEST-HANDOFF.md).
4. Run `make context`.

1. 阅读 [AGENTS.md](AGENTS.md)。
2. 阅读 [docs/PROJECT-STATE.md](docs/PROJECT-STATE.md)。
3. 阅读 [docs/LATEST-HANDOFF.md](docs/LATEST-HANDOFF.md)。
4. 运行 `make context`。

## What This Project Is

## 这个项目是什么

GroundedDeck is a local-first, source-grounded presentation system targeting NotebookLM-like deck quality with editable output and stronger Chinese support.

GroundedDeck 是一个本地优先、基于来源材料进行内容约束的演示文稿系统，目标是达到接近 NotebookLM 的成稿质量，同时保证输出可编辑，并对中文场景提供更强支持。

It is not:

它不是什么：

- a prompt-only PPT generator
- a renderer-first project
- a generic slide template filler

- 不是只靠单次 prompt 生成 PPT 的工具
- 不是以 renderer 为中心的项目
- 不是通用的模板填充器

## What To Do Next

## 接下来该做什么

Use the single item under `Current Next Action` in [docs/PROJECT-STATE.md](docs/PROJECT-STATE.md), unless [docs/LATEST-HANDOFF.md](docs/LATEST-HANDOFF.md) contains a more specific resume point from an unfinished task.

默认遵循 [docs/PROJECT-STATE.md](docs/PROJECT-STATE.md) 里 `Current Next Action` 的单一下一步；如果 [docs/LATEST-HANDOFF.md](docs/LATEST-HANDOFF.md) 记录了某个未完成任务的更具体恢复点，则以 handoff 为准。

## Before Ending a Session

## 结束本次会话前

- update [docs/LATEST-HANDOFF.md](docs/LATEST-HANDOFF.md)
- update [docs/TASK-BOARD.md](docs/TASK-BOARD.md)
- update [docs/PROJECT-STATE.md](docs/PROJECT-STATE.md) if project state changed
- run `make eval`

- 更新 [docs/LATEST-HANDOFF.md](docs/LATEST-HANDOFF.md)
- 更新 [docs/TASK-BOARD.md](docs/TASK-BOARD.md)
- 如果项目状态发生变化，更新 [docs/PROJECT-STATE.md](docs/PROJECT-STATE.md)
- 运行 `make eval`
