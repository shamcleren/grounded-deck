# Latest Handoff

[English](LATEST-HANDOFF.md) | [简体中文](LATEST-HANDOFF.zh-CN.md)

这个文件记录最近一次会话结束时的状态，帮助下一次会话不依赖聊天历史直接恢复工作。

## 会话摘要

GroundedDeck 已从一个静态脚手架升级为具备连续性意识的 AI 项目：仓库文件而不是聊天历史，才是持久记忆。

## 刚刚完成的内容

- 添加了 [AGENTS.md](../AGENTS.md) 作为 AI 操作契约
- 添加了 [docs/PROJECT-STATE.md](PROJECT-STATE.md) 作为规范当前状态记录
- 添加了 [docs/ARCHITECTURE-DECISIONS.md](ARCHITECTURE-DECISIONS.md) 用于防止架构漂移
- 扩展了 harness，使 continuity artifacts 成为必需项
- 添加了 [START-HERE.md](../START-HERE.md) 作为快速启动入口
- 调整文档多语言策略，采用独立语言文件加切换链接，而不是同页混排

## 当前状态

- 仓库连续性契约：已具备
- startup 与 handoff 路径：已具备
- 确定性 harness：通过
- 实现模块：仍然只有脚手架

## 立即下一步

实现第一条真正的流水线切片：

`ingest -> normalized source units -> slide spec draft -> quality checks`

## 第一批具体任务

1. 定义 normalized source-unit contract
2. 添加一个 example source fixture
3. 添加一个 example `slide spec` fixture
4. 扩展 harness，使其不仅检查仓库结构，也校验 fixtures

## 不要漂移

- 不要从 renderer 开始
- 不要把项目压扁成单 prompt 流水线
- 不要跳过中间层 `slide spec`
- 不要让状态变化缺少文档记录

## 恢复提示

如果未来某次会话只收到一句指令，那应该是：

`Continue GroundedDeck from START-HERE.md and follow the current next action.`
