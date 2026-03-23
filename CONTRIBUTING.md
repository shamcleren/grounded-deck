# Contributing

## 中文说明

这个文件说明参与 GroundedDeck 的基本流程。提交代码或文档前，应先理解架构边界并运行本地 eval。

## Before You Start

## 开始之前

- read [README.md](README.md)
- read [docs/architecture.md](docs/architecture.md)
- run `make eval` before submitting changes

- 阅读 [README.md](README.md)
- 阅读 [docs/architecture.md](docs/architecture.md)
- 提交修改前先运行 `make eval`

## Contribution Rules

## 贡献规则

- keep module ownership clear across `src/ingest`, `src/planner`, `src/visual`, `src/renderer`, and `src/quality`
- preserve the `slide spec` schema unless the change is deliberate and documented
- update docs when changing architecture, evals, or project goals
- prefer deterministic checks over subjective review when adding new quality gates

- 在 `src/ingest`、`src/planner`、`src/visual`、`src/renderer`、`src/quality` 之间保持清晰的模块归属
- 除非变更是有意且有文档记录，否则保留 `slide spec` schema 不变
- 变更架构、eval 或项目目标时同步更新文档
- 添加新的质量门禁时，优先选择确定性检查而不是主观评审

## Pull Request Checklist

## Pull Request 清单

- `make eval` passes locally
- docs were updated if behavior or scope changed
- new fields in schemas are explained
- regressions are covered by new or updated evals

- 本地 `make eval` 通过
- 如果行为或范围变化，相关文档已更新
- schema 中新增字段已得到说明
- 回归风险已被新的或更新后的 eval 覆盖

## Discussions

## 讨论渠道

Use issues for bugs and feature proposals. Use pull requests for concrete code or doc changes.

bug 和 feature proposal 请走 issue；具体代码或文档修改请走 pull request。
