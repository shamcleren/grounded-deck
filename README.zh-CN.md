# GroundedDeck

[English](README.md) | [简体中文](README.zh-CN.md)

GroundedDeck 是一个本地优先、基于来源材料约束的 PPT 生成系统，目标是实现接近 NotebookLM 风格的演示质量，同时保证输出可编辑、对中文更友好，并从一开始就具备自验收能力。

## 为什么做 GroundedDeck

大多数 AI PPT 工具太早开始生成页面，跳过了真正困难的部分：

- 理解来源材料
- 决定整套 deck 应该讲什么故事
- 为每一页选择合适的视觉形式
- 保持内容可以追溯到原始资料
- 保持输出可编辑，而不是把内容都烤成图片

GroundedDeck 被设计为一个本地优先的 presentation compiler，而不是通用的 slide template filler。

## 目标结果

GroundedDeck 希望产出的 deck 更接近 NotebookLM，而不是模板驱动的 PPT 生成器：

- 在写 slide 之前先做基于来源材料的规划
- 做叙事压缩，而不是把摘要机械切片
- 对时间线、对比、流程、层级、矩阵等结构自动选择合适的视觉形式
- 尽量使用原生对象输出可编辑 `.pptx`
- 用显式 coverage 检查减少事实和关键结论遗漏
- 对中文排版和渲染稳定性设置明确约束

## 当前项目状态

当前仓库已经包含基础脚手架：

- 产品定义和架构文档
- `slide spec` schema
- 确定性的 self-acceptance harness
- 开源仓库文档
- 为后续实现预留的模块边界

第一个里程碑是在加入完整 renderer 之前，先打通 `ingest -> slide spec -> quality checks` 的端到端路径。

## AI 连续性

这个仓库被设计为支持跨多个会话的长期 AI 驱动开发。

- 仓库文档是规范记忆
- 后续 agent 应从仓库状态恢复，而不是依赖聊天上下文
- 架构变化必须被记录，而不是默认约定
- 项目状态和唯一下一步必须保持明确

继续实现前，请先阅读 [START-HERE.zh-CN.md](START-HERE.zh-CN.md)、[AGENTS.zh-CN.md](AGENTS.zh-CN.md)、[docs/PROJECT-STATE.zh-CN.md](docs/PROJECT-STATE.zh-CN.md)、[docs/LATEST-HANDOFF.zh-CN.md](docs/LATEST-HANDOFF.zh-CN.md) 和 [docs/ARCHITECTURE-DECISIONS.zh-CN.md](docs/ARCHITECTURE-DECISIONS.zh-CN.md)。

中文读者也可以先看 [docs/README.zh-CN.md](docs/README.zh-CN.md) 获取总览。

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

## 核心模块

- `src/ingest`：来源解析、切分和 source binding
- `src/planner`：叙事规划和 deck outline 生成
- `src/visual`：视觉形式选择和图示规划
- `src/renderer`：将 `slide spec` 可编辑地渲染为 `pptx`
- `src/quality`：coverage、grounding、重复和连贯性检查

## 自验收

这个仓库从第一天起就把 harness engineering 当作产品的一部分。

当前检查覆盖：

- 必需的项目目录是否存在
- 关键文档是否定义了目标、约束和评估策略
- AI continuity 文档是否定义了当前状态和 anti-drift 规则
- 是否存在 startup 和 handoff 路径供未来会话恢复
- `slide spec` schema 是否包含 grounding 和 coverage 字段
- eval 定义是否同时包含 capability 和 regression 检查
- 是否能在本地生成标准 markdown 报告

运行本地 harness：

```bash
make eval
```

查看最新报告：

```bash
make report
```

最新报告路径：
[reports/self-acceptance-latest.md](reports/self-acceptance-latest.md)

## 路线图

1. 构建最小可用的 `ingest -> slide spec` 流水线。
2. 增加 coverage 和 grounding grader，用于检查来源覆盖完整性。
3. 引入带中文安全默认值的可编辑 PPTX 渲染。
4. 增加对布局类型选择和输出可编辑性的 artifact 级打分。

当前计划见 [docs/ROADMAP.zh-CN.md](docs/ROADMAP.zh-CN.md)。

## 参与贡献

贡献方式见 [CONTRIBUTING.zh-CN.md](CONTRIBUTING.zh-CN.md)、[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) 和 [SECURITY.md](SECURITY.md)。

## 许可证

采用 MIT 许可证，见 [LICENSE](LICENSE)。
