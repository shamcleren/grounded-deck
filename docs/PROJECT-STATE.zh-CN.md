# Project State

[English](PROJECT-STATE.md) | [简体中文](PROJECT-STATE.zh-CN.md)

这个文件记录 GroundedDeck 当前所处阶段、下一步动作和阶段性完成条件，是跨会话继续工作的主状态文件。

## 北极星目标

构建一个本地优先、基于来源材料约束的演示系统，产出接近 NotebookLM 质量的 deck，支持可编辑 PPTX、更强中文能力，以及显式自验收。

## 当前阶段

基础阶段已完成，并且已经有一条确定性基线流水线和 provider abstraction。仓库目前具备：

- 产品与架构定义
- 开源仓库所需文档
- 可确定性的 self-acceptance harness
- 稳定的 `slide spec` schema
- normalized source-unit schema
- 由 fixture 驱动的 ingest、planning 和 quality checks
- 面向 planner 和 quality 模块的可插拔 provider interface
- 面向未来 AI 会话的 repository-as-memory 连续性契约

另外，最强确定性 planning demo 现在已经通过 curator 流程整合回 `main`，并作为规范 fixture bundle 与报告路径存在；针对这套规范 strongest-demo 输入的第一次成功在线验证也已经归档。

## 已完成内容

- 将项目命名为 `GroundedDeck`
- 发布了公开仓库脚手架
- 定义了 ingest、planner、visual、renderer、quality 的架构拆分
- 定义了初始的 eval-driven 项目规则
- 添加了开源社区所需文档与模板
- 添加了 AI continuity、anti-drift 和 project-state 工件
- 添加了 startup、handoff 和 task-board 工件以支持跨会话恢复
- 实现了确定性的 `source pack -> normalized source units -> slide spec draft -> quality checks` 基线
- 添加了 fixture 驱动的 pipeline 测试和 harness 校验
- 引入了 provider abstraction，并以 deterministic provider 作为基线
- 添加了一个面向 fixture 基线执行的 runtime pipeline 入口
- 接通了 OpenAI-compatible provider 路径，并增加了严格的本地响应校验与 mocked transport 测试
- 为 worker、curator、verifier 三类 automation 定义了仓库级治理规则
- 把 detached 的 automation worktree 恢复到了命名救援分支上，避免改动继续匿名漂浮
- 将 strongest-demo 的救援改动整合成一套规范 fixture bundle、报告路径和确定性指标基线
- 使用 MiniMax-M2.7 针对规范 strongest-demo 输入完成并归档了第一次成功在线验证
- 强化了 OpenAI-compatible provider 路径，使其能够拆分 MiniMax 的推理输出，并兼容 `<think>` 包裹的 JSON 响应
- 增加了带角色锁的 automation 支持，让更高频的 worker / curator 调度不会发生不安全重叠

## 当前唯一下一步

以已归档的 strongest-demo 在线验证为基线，在不削弱确定性回归覆盖的前提下扩展 provider-backed planning。

## 近期优先级

1. 将已归档的 strongest-demo live verification 工件作为第一条被接受的在线基线沉淀进仓库记忆
2. 在保持 `make eval` 稳定的前提下，继续改进 strongest-demo 路径上的 provider-backed planning 和 grading
3. 让 `make verify-online` 保持可复用，作为真实 provider 路径的回归探针

这次吸收外部评价，只调整优先级，不调整架构边界。环境变量配置约定已经写入 `docs/runtime-config.md`，而且 live 预检现在会拦截占位值。现在 strongest-demo 已经在真实 provider 上跑通一次，接下来要做的是在保留确定性基线的前提下继续扩展 provider-backed planning。

## 当前约束

- 本地优先设计
- 输出可编辑仍然是硬性要求
- 中文渲染质量是一等需求
- 架构必须保持 source-grounded 且可审计
- 仓库文档必须足以支持 AI 跨会话继续工作
- 可以因为外部反馈调整优先级和 demo 策略，但不能无记录地改动架构边界
- 定时或无人值守的 AI 工作必须通过 automation governance 流程进入主线，不能直接写 `main`
- 更高频的定时 automation 在开始实质工作前必须使用仓库提供的角色锁机制

## 第一阶段完成定义

- source pack 能被摄取并转换为 normalized units
- planner 能输出 schema-valid 的 `slide spec`
- harness 能对 fixtures 打分，并在回归时失败
- 项目文档能在不依赖聊天历史的情况下说明当前状态与下一步

## 更新规则

如果当前阶段、下一步、约束或目标发生变化，必须在同一个 change set 中更新本文件和对应英文文件。
