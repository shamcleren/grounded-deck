# GroundedDeck

## 中文说明

GroundedDeck 是一个面向演示文稿生成的本地优先系统：先理解来源材料，再规划叙事和页面结构，最后产出可编辑的 PPTX，并通过自验收机制约束质量。

中文读者可以先看 [docs/README.zh-CN.md](docs/README.zh-CN.md) 获取总览。

NotebookLM-style source-grounded PPT generation with editable output, stronger Chinese support, and self-acceptance harnesses.

目标是实现接近 NotebookLM 风格的、基于来源材料约束的 PPT 生成，同时提供更强的中文支持和自验收 harness。

## Why GroundedDeck

## 为什么做 GroundedDeck

Most AI PPT tools generate slides too early. They skip the hard part:

多数 AI PPT 工具太早开始出页，跳过了真正困难的部分：

- understanding source materials
- deciding what story the deck should tell
- choosing the right visual form for each page
- preserving traceability back to the original sources
- keeping the output editable instead of baking everything into images

- 理解来源材料
- 决定整套 deck 应该讲什么故事
- 为每一页选择合适的视觉形式
- 保持内容可以追溯到原始资料
- 保持输出可编辑，而不是把内容都烤成图片

GroundedDeck is designed as a local-first presentation compiler, not a generic slide filler.

GroundedDeck 被设计成一个本地优先的 presentation compiler，而不是通用的 slide filler。

## Target Outcome

## 目标结果

GroundedDeck aims to produce decks that feel closer to NotebookLM than to template-driven PPT generators:

GroundedDeck 希望产出的 deck 更接近 NotebookLM，而不是模板驱动的 PPT 生成器：

- source-grounded planning before slide writing
- narrative compression instead of summary slicing
- automatic visual form selection for timelines, comparisons, flows, hierarchies, and matrices
- editable `.pptx` output using native objects wherever possible
- explicit coverage checks to reduce dropped facts and key claims
- Chinese-friendly typography and rendering constraints

- 在写 slide 之前先做基于来源材料的规划
- 做叙事压缩，而不是把摘要机械切片
- 对时间线、对比、流程、层级、矩阵等结构自动选择合适视觉形式
- 尽量使用原生对象输出可编辑的 `.pptx`
- 通过显式 coverage 检查减少事实和关键结论遗漏
- 为中文排版与渲染稳定性设置明确约束

## Project Status

## 当前项目状态

This repository currently contains the foundation scaffold:

当前仓库包含的是基础脚手架：

- product definition and architecture docs
- `slide spec` schema
- deterministic self-acceptance harness
- open-source repository documents
- implementation module boundaries for future work

- 产品定义与架构文档
- `slide spec` schema
- 可确定性执行的 self-acceptance harness
- 开源仓库所需文档
- 为后续实现预留的模块边界

The first milestone is to build an end-to-end `ingest -> slide spec -> quality checks` path before adding a full renderer.

第一个里程碑是在引入完整 renderer 之前，先打通 `ingest -> slide spec -> quality checks` 的端到端路径。

## AI Continuity

## AI 连续性

This repository is built to survive long-running AI-driven development across many sessions.

这个仓库被设计为支持跨多个会话的长期 AI 驱动开发。

- repository docs are the canonical memory
- future agents should resume from repo state, not chat context
- architecture changes must be recorded, not implied
- project status and the single next action must remain explicit

- 仓库文档是唯一的规范记忆
- 后续 agent 应从仓库状态恢复，而不是依赖聊天上下文
- 架构变化必须被记录，不能靠默认约定
- 项目状态和唯一下一步必须保持明确

Read [START-HERE.md](START-HERE.md), [AGENTS.md](AGENTS.md), [docs/PROJECT-STATE.md](docs/PROJECT-STATE.md), [docs/LATEST-HANDOFF.md](docs/LATEST-HANDOFF.md), and [docs/ARCHITECTURE-DECISIONS.md](docs/ARCHITECTURE-DECISIONS.md) before continuing implementation work.

继续实现前，请先阅读 [START-HERE.md](START-HERE.md)、[AGENTS.md](AGENTS.md)、[docs/PROJECT-STATE.md](docs/PROJECT-STATE.md)、[docs/LATEST-HANDOFF.md](docs/LATEST-HANDOFF.md) 和 [docs/ARCHITECTURE-DECISIONS.md](docs/ARCHITECTURE-DECISIONS.md)。

如果你主要使用中文，可先从 [docs/README.zh-CN.md](docs/README.zh-CN.md) 开始。

## Architecture

## 架构

```text
Sources
  -> ingest
  -> planner
  -> visual selector
  -> slide spec
  -> renderer
  -> quality harness
  -> report
```

上面这条链路表达的是：先理解来源，再规划叙事和视觉形式，再编译为 `slide spec`，最后进行渲染和质量评估。

## Repository Layout

## 仓库结构

```text
.
├── .claude/evals/            # Eval definitions
├── START-HERE.md             # Quick startup entrypoint for new sessions
├── AGENTS.md                 # AI continuation contract
├── .github/                  # GitHub community files and templates
├── docs/                     # Product, architecture, and evaluation docs
├── harness/                  # Deterministic self-acceptance harness
├── reports/                  # Generated self-acceptance reports
├── schemas/                  # Structured intermediate representations
└── src/                      # Future implementation modules
```

核心目录的作用如下：`docs/` 保存规范和状态，`schemas/` 保存结构化中间表示，`harness/` 和 `reports/` 负责自验收，`src/` 则按模块边界放后续实现代码。

## Core Modules

## 核心模块

- `src/ingest`: source parsing, chunking, and source binding
- `src/planner`: deck narrative planning and outline generation
- `src/visual`: visual form selection and diagram planning
- `src/renderer`: editable `slide spec -> pptx` rendering
- `src/quality`: coverage, grounding, repetition, and coherence checks

- `src/ingest`：来源解析、切分和 source binding
- `src/planner`：演示叙事规划与 deck outline 生成
- `src/visual`：视觉形式选择与图示规划
- `src/renderer`：将 `slide spec` 可编辑地渲染为 `pptx`
- `src/quality`：coverage、grounding、重复度和连贯性检查

## Self-Acceptance

## 自验收

This repository uses harness engineering from day one.

这个仓库从第一天起就把 harness engineering 当作产品的一部分。

Current checks verify:

当前检查覆盖：

- required project directories exist
- key docs define goals, constraints, and evaluation strategy
- AI continuity docs define current state and anti-drift rules
- a startup and handoff path exists for future sessions
- the `slide spec` schema contains grounding and coverage fields
- eval definitions include both capability and regression checks
- a standard markdown report is generated locally

- 必需的项目目录是否存在
- 关键文档是否定义了目标、约束和评估策略
- AI continuity 文档是否定义了当前状态和 anti-drift 规则
- 是否存在 startup 和 handoff 路径供未来会话恢复
- `slide spec` schema 是否包含 grounding 和 coverage 字段
- eval 定义是否同时包含 capability 与 regression 检查
- 是否能在本地生成标准 markdown 报告

Run the local harness:

运行本地 harness：

```bash
make eval
```

Read the latest report:

查看最新报告：

```bash
make report
```

Latest report path:
[reports/self-acceptance-latest.md](reports/self-acceptance-latest.md)

## Roadmap

## 路线图

1. Build a minimal `ingest -> slide spec` pipeline.
2. Add coverage and grounding graders for source completeness.
3. Introduce editable PPTX rendering with Chinese-safe defaults.
4. Add artifact-level grading for layout type selection and output editability.

1. 构建最小可用的 `ingest -> slide spec` 流水线。
2. 增加 coverage 和 grounding grader，用于检查来源覆盖完整性。
3. 引入带中文安全默认值的可编辑 PPTX 渲染。
4. 增加对布局类型选择与输出可编辑性的 artifact 级打分。

See [docs/ROADMAP.md](docs/ROADMAP.md) for the current plan.

当前计划见 [docs/ROADMAP.md](docs/ROADMAP.md)。

## Contributing

## 参与贡献

See [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md), and [SECURITY.md](SECURITY.md).

贡献方式见 [CONTRIBUTING.md](CONTRIBUTING.md)、[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) 和 [SECURITY.md](SECURITY.md)。

## License

## 许可证

MIT. See [LICENSE](LICENSE).

采用 MIT 许可证，见 [LICENSE](LICENSE)。
