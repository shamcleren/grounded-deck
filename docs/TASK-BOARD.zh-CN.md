# Task Board

[English](TASK-BOARD.md) | [简体中文](TASK-BOARD.zh-CN.md)

这个文件记录当前进行中的任务、下一批待做事项和阻塞项。任何会话开始实作时，都应先同步这里。

## 进行中

- 以已验证的 strongest-demo 基线为起点，在不削弱确定性回归覆盖的前提下扩展 provider-backed planning

## 下一批待做

- 收紧 strongest-demo 路径上的 provider-backed planning 和 grading prompt
- 决定 live strongest-demo 输出里的哪些部分应该上升为未来的回归 fixture 或 acceptance check
- 后续新增 canonical docs 时，保持中英双语并采用独立语言文件

## 后续

- 用 provider-backed planning 替换当前确定性 planner 启发式
- 增加模型辅助的 narrative 和 visual-form grading
- 在最强 demo 之后，再补一个和通用 AI PPT 工具的公开对比样例
- 在 planning contract 稳定之前暂缓 renderer 实现

## 阻塞项

- strongest-demo live verification 路径当前无阻塞项

## 更新规则

当任务开始时，将其移动到 `In Progress`。
当任务完成或失效时，在同一个 change set 中更新本文件和对应英文文件。
