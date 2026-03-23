# GroundedDeck 中文总览

这个页面给中文读者提供一个统一入口，帮助快速理解 GroundedDeck 的目标、当前状态、关键约束和下一步工作。

## 建议阅读顺序

1. [START-HERE.md](../START-HERE.md)
2. [AGENTS.md](../AGENTS.md)
3. [README.md](../README.md)
4. [docs/PROJECT-STATE.md](./PROJECT-STATE.md)
5. [docs/LATEST-HANDOFF.md](./LATEST-HANDOFF.md)
6. [docs/ARCHITECTURE-DECISIONS.md](./ARCHITECTURE-DECISIONS.md)
7. [docs/architecture.md](./architecture.md)
8. [docs/evaluation-plan.md](./evaluation-plan.md)

## 这个项目是什么

GroundedDeck 是一个本地优先、基于来源材料约束的演示文稿系统。

它的目标不是“输入一句话，立刻吐出一份成品 PPT”，而是先理解来源内容，再完成叙事规划、视觉形式选择和结构化中间表示编译，最后才进入渲染和质量检查。

## 当前项目状态

当前仓库已经完成：

- 产品与架构定义
- `slide spec` schema
- 基础自验收 harness
- 仓库连续性文档
- 未来实现模块的边界划分

当前还没有完成：

- 真正的 ingest 实现
- 真正的 planner 输出
- fixture 级质量 grading
- 可编辑 PPTX renderer

## 当前唯一下一步

根据 [docs/PROJECT-STATE.md](./PROJECT-STATE.md) 与 [docs/LATEST-HANDOFF.md](./LATEST-HANDOFF.md)，当前唯一明确的下一步是：

`ingest -> normalized source units -> slide spec draft -> quality checks`

可拆分为：

1. 定义 normalized source-unit contract
2. 添加 example source fixture
3. 添加 example `slide spec` fixture
4. 扩展 harness，使其能校验 fixture，而不只是仓库结构

## 关键架构约束

- 不允许把项目退化成单一 giant prompt 流水线
- 不允许由 renderer 负责内容理解
- 不允许跳过 `slide spec` 直接产出最终工件
- 可编辑性是硬要求，不是后续增强
- 中文渲染质量是硬要求，不是收尾 polish
- harness engineering 是产品架构的一部分

## 关键文档作用

- [README.md](../README.md)：项目总览、目标、模块与路线图
- [START-HERE.md](../START-HERE.md)：新会话快速启动入口
- [AGENTS.md](../AGENTS.md)：AI 会话操作契约
- [docs/PROJECT-STATE.md](./PROJECT-STATE.md)：当前状态、阶段目标、唯一下一步
- [docs/LATEST-HANDOFF.md](./LATEST-HANDOFF.md)：最近一次会话交接
- [docs/TASK-BOARD.md](./TASK-BOARD.md)：进行中、待做和阻塞项
- [docs/ARCHITECTURE-DECISIONS.md](./ARCHITECTURE-DECISIONS.md)：固定架构不变量与决策日志
- [docs/architecture.md](./architecture.md)：系统分层与数据流
- [docs/evaluation-plan.md](./evaluation-plan.md)：评估策略与阶段性 grader 规划
- [docs/ROADMAP.md](./ROADMAP.md)：里程碑路线图
- [docs/vision.md](./vision.md)：产品质量标准、差异化与非目标

## 文档约定

- canonical memory 仍以仓库文档为准，而不是聊天历史
- 核心规范文档保持中英双语
- 新增会改变项目记忆的 canonical docs 时，应继续保持双语
- 结束一次有意义的工作前，要更新 handoff、task board 和必要的状态文档，并运行 `make eval`
