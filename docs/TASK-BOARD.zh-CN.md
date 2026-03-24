# Task Board

[English](TASK-BOARD.md) | [简体中文](TASK-BOARD.zh-CN.md)

这个文件记录当前进行中的任务、下一批待做事项和阻塞项。任何会话开始实作时，都应先同步这里。

## 进行中

- 针对规范 strongest-demo 输入完成第一次成功 online verification

## 下一批待做

- 把 `.env.runtime.local` 中的占位值替换为真实配置，并跑通第一次 `make verify-online`
- 留下一次成功 live verification 的记录或工件形态
- 把第一次成功的 `verification-summary.json` 工件形态沉淀进仓库记忆
- 后续新增 canonical docs 时，保持中英双语并采用独立语言文件

## 后续

- 用 provider-backed planning 替换当前确定性 planner 启发式
- 增加模型辅助的 narrative 和 visual-form grading
- 在最强 demo 之后，再补一个和通用 AI PPT 工具的公开对比样例
- 在 planning contract 稳定之前暂缓 renderer 实现

## 阻塞项

- `make verify-online` 所需的真实 provider 凭证和可访问后端尚未配置

## 更新规则

当任务开始时，将其移动到 `In Progress`。
当任务完成或失效时，在同一个 change set 中更新本文件和对应英文文件。
