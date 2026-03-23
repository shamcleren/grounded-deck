# Task Board

## 中文说明

这个文件记录当前进行中的任务、下一批待做事项和阻塞项。任何会话开始实作时，都应先同步这里。

## In Progress

## 进行中

- none

- 无

## Ready Next

## 下一批待做

- define normalized source-unit schema or contract
- create sample source fixture
- create sample `slide spec` fixture
- add fixture-aware harness checks
- keep newly added canonical docs bilingual when extending repository memory
- keep [README.zh-CN.md](README.zh-CN.md) aligned with canonical doc changes

- 定义 normalized source-unit schema 或 contract
- 创建 sample source fixture
- 创建 sample `slide spec` fixture
- 添加能识别 fixture 的 harness 检查
- 后续新增 canonical docs 时，保持中英双语
- 当 canonical docs 变化时，同步维护 [README.zh-CN.md](README.zh-CN.md)

## Later

## 后续

- implement minimal ingest normalization
- implement minimal planner output
- add quality grading for fixtures
- defer renderer implementation until the planning contract is stable

- 实现最小化 ingest normalization
- 实现最小化 planner 输出
- 为 fixtures 增加质量 grading
- 在 planning contract 稳定之前暂缓 renderer 实现

## Blockers

## 阻塞项

- none currently recorded

- 当前未记录阻塞项

## Update Rule

## 更新规则

When a task begins, move it to `In Progress`.
When it finishes or becomes obsolete, update this file in the same change set.

当任务开始时，将其移动到 `In Progress`。
当任务完成或失效时，在同一个 change set 中更新本文件。
