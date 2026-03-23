# Contributing

[English](CONTRIBUTING.md) | [简体中文](CONTRIBUTING.zh-CN.md)

这个文件说明参与 GroundedDeck 的基本流程。提交代码或文档前，应先理解架构边界并运行本地 eval。

## 开始之前

- 阅读 [README.zh-CN.md](README.zh-CN.md)
- 阅读 [docs/architecture.zh-CN.md](docs/architecture.zh-CN.md)
- 提交修改前先运行 `make eval`

## 贡献规则

- 在 `src/ingest`、`src/planner`、`src/visual`、`src/renderer`、`src/quality` 之间保持清晰的模块归属
- 除非变更是有意且有文档记录，否则保留 `slide spec` schema 不变
- 变更架构、eval 或项目目标时同步更新文档
- 添加新的质量门禁时，优先选择确定性检查而不是主观评审

## Pull Request 清单

- 本地 `make eval` 通过
- 如果行为或范围变化，相关文档已更新
- schema 中新增字段已得到说明
- 回归风险已被新的或更新后的 eval 覆盖

## 讨论渠道

bug 和 feature proposal 请走 issue；具体代码或文档修改请走 pull request。
