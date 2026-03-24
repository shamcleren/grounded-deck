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

## 当前唯一下一步

在不削弱确定性回归覆盖的前提下，补齐 live provider 验证约定，并留下一次成功的在线验证记录。

## 近期优先级

1. 记录 `make verify-online` 的预期配置、成功标准和失败模式
2. 保留 fixture 驱动的确定性输出，作为 `make eval` 的回归基线
3. 留下一次成功的在线验证工件，并根据真实响应继续收紧 prompt

环境变量配置约定已经写入 `docs/runtime-config.md`，剩余工作是把在线 provider 调用真正接通。

## 当前约束

- 本地优先设计
- 输出可编辑仍然是硬性要求
- 中文渲染质量是一等需求
- 架构必须保持 source-grounded 且可审计
- 仓库文档必须足以支持 AI 跨会话继续工作

## 第一阶段完成定义

- source pack 能被摄取并转换为 normalized units
- planner 能输出 schema-valid 的 `slide spec`
- harness 能对 fixtures 打分，并在回归时失败
- 项目文档能在不依赖聊天历史的情况下说明当前状态与下一步

## 更新规则

如果当前阶段、下一步、约束或目标发生变化，必须在同一个 change set 中更新本文件和对应英文文件。
