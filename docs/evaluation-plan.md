# Evaluation Plan

## 中文说明

GroundedDeck 采用 eval-driven development：先定义成功标准，再实现；优先使用确定性 grader；并保证本地可以用单一命令运行评估。

## Principles

## 原则

GroundedDeck uses eval-driven development:

GroundedDeck 采用 eval-driven development：

- define success before implementation
- prefer deterministic graders whenever possible
- keep local evaluation runnable from a single command
- treat regression checks as first-class project artifacts

- 在实现前先定义成功标准
- 尽量优先使用确定性 grader
- 保持本地评估可以通过单一命令运行
- 将 regression 检查视为一等项目工件

## Capability Evals

## 能力评估

- the repository defines the product target and architecture boundaries
- the repository defines the AI continuity contract and current project state
- the repository defines a startup path and explicit handoff artifacts
- the repository defines a structured `slide spec` intermediate representation
- the repository provides local harness and rubric files
- the repository can generate a standard self-acceptance report

- 仓库定义了产品目标和架构边界
- 仓库定义了 AI continuity 契约和当前项目状态
- 仓库定义了 startup 路径和显式 handoff 工件
- 仓库定义了结构化的 `slide spec` 中间表示
- 仓库提供本地 harness 和 rubric 文件
- 仓库能够生成标准 self-acceptance 报告

## Regression Evals

## 回归评估

- key project docs and harness files must remain present after refactors
- schema updates must not silently remove required fields
- eval definitions must keep both capability and regression sections
- AI continuity files must keep readable next-step and anti-drift guidance
- startup and handoff files must keep a clear resume path for a new session

- 重构后关键项目文档和 harness 文件必须仍然存在
- schema 更新不能静默删除必需字段
- eval 定义必须保留 capability 和 regression 两部分
- AI continuity 文件必须保留可读的 next-step 与 anti-drift 指引
- startup 和 handoff 文件必须保留清晰的新会话恢复路径

## Grader Strategy

## Grader 策略

- phase one: code-based graders for files, schema, and eval definitions
- phase two: artifact graders for PPT editability, source coverage, and font constraints
- phase three: model-based graders for narrative quality and visual selection quality

- 第一阶段：针对文件、schema、eval 定义的代码式 grader
- 第二阶段：针对 PPT 可编辑性、来源覆盖和字体约束的 artifact grader
- 第三阶段：针对叙事质量和视觉选择质量的模型式 grader

## Outputs

## 输出

- standard output summary
- markdown report
- non-zero exit code on failure

- 标准输出摘要
- markdown 报告
- 失败时返回非零退出码

## Next Stage

## 下一阶段

- validate example `slide spec` instances against schema
- grade sample decks for coverage and grounding
- inspect exported PPT artifacts for editable object usage and Chinese font rules
- grade continuity artifacts so future agents can safely resume from repository state alone
- grade handoff completeness and task-board freshness

- 用 schema 校验示例 `slide spec` 实例
- 对 sample deck 做 coverage 和 grounding grading
- 检查导出的 PPT 工件是否使用可编辑对象并遵守中文字体规则
- 对 continuity artifacts 打分，确保未来 agent 仅凭仓库状态即可恢复
- 检查 handoff 完整性和 task-board 新鲜度
