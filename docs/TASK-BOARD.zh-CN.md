# Task Board

[English](TASK-BOARD.md) | [简体中文](TASK-BOARD.zh-CN.md)

这个文件记录当前进行中的任务、下一批待做事项和阻塞项。任何会话开始实作时，都应先同步这里。

## 进行中

- 保持 strongest-demo provider prompt 与已归档 acceptance snapshot 对齐，并让后续 live refresh 先和它对比，再决定后续 provider-backed planning 改动是否继续上升

## 下一批待做

- 在不削弱确定性回归覆盖的前提下，继续改进 strongest-demo 路径上的 provider-backed planning 与 grading
- 复核剩余 worker prompt 变体是否还能在当前 acceptance-aligned strongest-demo 基线之外带来增益
- 后续新增 canonical docs 时，保持中英双语并采用独立语言文件

## 后续

- 用 provider-backed planning 替换当前确定性 planner 启发式
- 增加模型辅助的 narrative 和 visual-form grading
- 在最强 demo 之后，再补一个和通用 AI PPT 工具的公开对比样例
- 在 planning contract 稳定之前暂缓 renderer 实现

## 阻塞项

- 当前 strongest-demo planning 基线没有阻塞项

## 更新规则

当任务开始时，将其移动到 `In Progress`。
当任务完成或失效时，在同一个 change set 中更新本文件和对应英文文件。
