# Latest Handoff

[English](LATEST-HANDOFF.md) | [简体中文](LATEST-HANDOFF.zh-CN.md)

这个文件记录最近一次会话结束时的状态，帮助下一次会话不依赖聊天历史直接恢复工作。

## 会话摘要

GroundedDeck 现在除了由 fixture 驱动的确定性流水线、连续性仓库结构和显式 automation governance 之外，还拥有一套规范 strongest-demo 工件包，以及一条已经归档的 strongest-demo 成功在线验证记录。

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
- 添加了 `docs/AUTOMATION-GOVERNANCE.md`，并把 automation 处理规则纳入启动必读
- 将 4 个 detached automation worktree 恢复到命名救援分支上，避免有效工作继续丢在匿名状态
- 验收 strongest-demo 的救援工作，落下一套规范 fixture bundle、确定性质量指标和 `make strongest-demo`
- 添加了 `make curator-finalize`，让后续 curator run 通过同一条仓库内置的合并与清理流程收尾
- 把 live provider 路径配置到 MiniMax-M2.7，并将第一次成功的 strongest-demo 在线验证归档到 `reports/live-verification-latest.{json,md}`
- 强化了 OpenAI-compatible provider 集成，使 MiniMax 的推理输出可以被拆分，`<think>` 包裹的 JSON 结果也能被稳定解析和诊断
- 增加了仓库内置的 automation 角色锁工具，让 worker 和 curator 的更高频调度也能避免实质工作重叠

## 当前状态

- 仓库连续性契约：已具备
- startup 与 handoff 路径：已具备
- 确定性 harness：通过
- 确定性 pipeline 基线：通过
- provider abstraction：已具备
- OpenAI-compatible provider 路径：已具备，且可在本地测试
- live verification 工具链：已就绪，且已被验证
- placeholder env detection：已具备
- live status 已能正确报告环境是否就绪以及最近一次归档结果
- live 凭证 / 真实后端：已配置，并用 MiniMax-M2.7 验证通过
- strongest-demo 规范工件包：已存在
- worker / curator / verifier 流程的 automation governance：已具备
- 面向更高频调度的 automation 角色锁：已具备
- 第一次 strongest-demo 成功 online verification：已归档到 `reports/live-verification-latest.json` 和 `reports/live-verification-latest.md`
- 近期重点：以已验证的 strongest-demo 基线继续扩展 provider-backed planning，同时不削弱确定性 eval
- renderer 实现：仍然延后

## 立即下一步

以已归档的 strongest-demo 在线验证为基线，推进下一轮 provider-backed planning，同时保持确定性回归覆盖稳定。

## 第一批具体任务

1. 将 `reports/live-verification-latest.json` 和 `reports/live-verification-latest.md` 视为第一条规范 live-run 记忆
2. 继续改进 strongest-demo 路径上的 provider-backed planning 与 grading 行为
3. 在保留 `make eval` 稳定性的前提下，让 `make verify-online` 在真实 provider 路径上持续可用
4. 后续如果再出现 provider 兼容性细节，必须记录进仓库文档，而不是留在隐式上下文里

## 不要漂移

- 不要从 renderer 开始
- 不要把项目压扁成单 prompt 流水线
- 不要跳过中间层 `slide spec`
- 不要让状态变化缺少文档记录
- 不要让 worker automation 修改 canonical state docs，也不要让它们直接写 `main`
- 后续再讨论 strongest-demo live path 时，不要回退到旧的 example fixture

## 恢复提示

如果未来某次会话只收到一句指令，那应该是：

`Continue GroundedDeck from START-HERE.md and follow the current next action.`
