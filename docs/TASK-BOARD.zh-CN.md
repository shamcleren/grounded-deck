# Task Board

[English](TASK-BOARD.md) | [简体中文](TASK-BOARD.zh-CN.md)

这个文件记录当前进行中的任务、下一批待做事项和阻塞项。任何会话开始实作时，都应先同步这里。

## 进行中

- 无

## 下一批待做

- 定义 normalized source-unit schema 或 contract
- 创建 sample source fixture
- 创建 sample `slide spec` fixture
- 添加能识别 fixture 的 harness 检查
- 后续新增 canonical docs 时，保持中英双语并采用独立语言文件

## 后续

- 实现最小化 ingest normalization
- 实现最小化 planner 输出
- 为 fixtures 增加质量 grading
- 在 planning contract 稳定之前暂缓 renderer 实现

## 阻塞项

- 当前未记录阻塞项

## 更新规则

当任务开始时，将其移动到 `In Progress`。
当任务完成或失效时，在同一个 change set 中更新本文件和对应英文文件。
