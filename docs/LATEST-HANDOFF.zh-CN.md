# Latest Handoff

[English](LATEST-HANDOFF.md) | [简体中文](LATEST-HANDOFF.zh-CN.md)

这个文件记录最近一次会话结束时的状态，帮助下一次会话不依赖聊天历史直接恢复工作。

## 会话摘要

GroundedDeck 现在除了连续性仓库结构之外，还包含一条由 fixture 驱动的确定性流水线切片。

## 刚刚完成的内容

- 添加了 [AGENTS.md](../AGENTS.md) 作为 AI 操作契约
- 添加了 [docs/PROJECT-STATE.md](PROJECT-STATE.md) 作为规范当前状态记录
- 添加了 [docs/ARCHITECTURE-DECISIONS.md](ARCHITECTURE-DECISIONS.md) 用于防止架构漂移
- 扩展了 harness，使 continuity artifacts 成为必需项
- 添加了 [START-HERE.md](../START-HERE.md) 作为快速启动入口
- 调整文档多语言策略，采用独立语言文件加切换链接，而不是同页混排
- 添加了 normalized source-unit schema 和 fixture 文件
- 实现了确定性的 ingest、planning 和 quality 模块
- 扩展了 `make eval`，让它执行 pipeline fixture 测试
- 为 planner 和 quality 模块引入了 provider abstraction
- 添加了 runtime pipeline 入口和示例命令
- 接通了 OpenAI-compatible provider 路径，并增加了严格的本地响应校验
- 添加了拒绝 deterministic fallback 的 `make verify-online` 路径
- 为运行时执行增加了自动生成的 verification-summary 工件
- 收紧了 live env 检查，`REPLACE_ME` 这类占位值现在会被视为无效配置
- 吸收了一轮外部产品反馈，把近期重点收敛到最强 demo 和 planning-quality 证明点，但没有改动架构边界

## 当前状态

- 仓库连续性契约：已具备
- startup 与 handoff 路径：已具备
- 确定性 harness：通过
- 确定性 pipeline 基线：通过
- provider abstraction：已具备
- OpenAI-compatible provider 路径：已具备，且可在本地测试
- live verification 工具链：已就绪
- placeholder env detection：已具备
- live status 已能把占位配置识别为未就绪
- live 凭证 / 真实后端：尚未配置
- 近期重点：最强端到端 planning demo，以及显式 planning-quality metrics
- renderer 实现：仍然延后

## 立即下一步

在保留确定性 fixture pipeline 的前提下，先做一个最强端到端 planning demo，再留下一次成功的在线验证记录。

## 第一批具体任务

1. 选一个最强 demo 输入包，并定义“有说服力输出”的标准
2. 写清楚 coverage、grounding、visual-form selection 的 planning-quality success metrics
3. 把 `.env.runtime.local` 里的占位值替换成真实 provider 配置
4. 运行 `make check-live-env`、`make live-status`、`make verify-online`，并归档生成的 `verification-summary.json`

## 不要漂移

- 不要从 renderer 开始
- 不要把项目压扁成单 prompt 流水线
- 不要跳过中间层 `slide spec`
- 不要让状态变化缺少文档记录

## 恢复提示

如果未来某次会话只收到一句指令，那应该是：

`Continue GroundedDeck from START-HERE.md and follow the current next action.`
