# AI 代理操作合约

[English](AGENTS.md) | [简体中文](AGENTS.zh-CN.md)

本仓库专为长期 AI 驱动开发设计。不要依赖聊天历史作为事实来源，仓库本身才是持久记忆。

## 必读顺序

在进行任何修改之前，请按顺序阅读以下文件：

1. [START-HERE.md](START-HERE.md)
2. [README.md](README.md)
3. [docs/PROJECT-STATE.md](docs/PROJECT-STATE.md)
4. [docs/LATEST-HANDOFF.md](docs/LATEST-HANDOFF.md)
5. [docs/ARCHITECTURE-DECISIONS.md](docs/ARCHITECTURE-DECISIONS.md)
6. [docs/architecture.md](docs/architecture.md)
7. [docs/evaluation-plan.md](docs/evaluation-plan.md)

## 操作合约

- 将仓库文档视为规范记忆。
- 当仓库文档与先前对话状态不一致时，以仓库文档为准。
- 使用 [docs/LATEST-HANDOFF.md](docs/LATEST-HANDOFF.md) 作为会话间恢复的首要构件。
- 不得在未更新 [docs/ARCHITECTURE-DECISIONS.md](docs/ARCHITECTURE-DECISIONS.md) 的情况下更改架构边界。
- 不得在项目状态发生变化时未更新 [docs/PROJECT-STATE.md](docs/PROJECT-STATE.md) 就结束任务。
- 不得在未更新 [docs/LATEST-HANDOFF.md](docs/LATEST-HANDOFF.md) 和 [docs/TASK-BOARD.md](docs/TASK-BOARD.md) 的情况下离开进行中的任务。
- 保持当前下一步行动明确且唯一。
- 保留 `slide spec` 中间表示作为规划、渲染和评分之间的稳定合约。
- 在认为任务完成之前运行 `make eval`。

## 防漂移规则

- 禁止"一个巨型提示词"架构。
- 渲染器不得拥有内容理解能力。
- 不得在没有可审计中间状态的情况下生成最终构件。
- 不得静默移除覆盖率、溯源或可编辑性要求。
- 不得在未记录决策及其原因的情况下扩展范围。

## 完成协议

完成有意义的工作时：

1. 更新涉及规范项目记忆变更的文档
2. 更新当前状态和下一步
3. 更新交接和任务板文件
4. 运行 `make eval`
5. 将仓库保持在未来 AI 代理能仅从仓库上下文继续工作的状态
