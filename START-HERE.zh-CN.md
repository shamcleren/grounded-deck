# 从这里开始

[English](START-HERE.md) | [简体中文](START-HERE.zh-CN.md)

当新的 AI 会话需要快速继续 GroundedDeck 时，请使用此文件。

## 30 秒启动

1. 阅读 [AGENTS.md](AGENTS.md)。
2. 阅读 [docs/PROJECT-STATE.md](docs/PROJECT-STATE.md)。
3. 阅读 [docs/LATEST-HANDOFF.md](docs/LATEST-HANDOFF.md)。
4. 运行 `make context`。

## 项目简介

GroundedDeck 是一个本地优先、来源溯源的演示文稿系统，目标是达到 NotebookLM 级别的演示文稿质量，同时支持可编辑输出和更强的中文支持。

它不是：

- 一个纯提示词的 PPT 生成器
- 一个渲染器优先的项目
- 一个通用幻灯片模板填充器

## 下一步做什么

使用 [docs/PROJECT-STATE.md](docs/PROJECT-STATE.md) 中 `Current Next Action` 下的单一条目，除非 [docs/LATEST-HANDOFF.md](docs/LATEST-HANDOFF.md) 包含来自未完成任务的更具体的恢复点。

## 结束会话前

- 更新 [docs/LATEST-HANDOFF.md](docs/LATEST-HANDOFF.md)
- 更新 [docs/TASK-BOARD.md](docs/TASK-BOARD.md)
- 如果项目状态发生变化，更新 [docs/PROJECT-STATE.md](docs/PROJECT-STATE.md)
- 运行 `make eval`
