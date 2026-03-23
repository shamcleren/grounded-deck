# Project State

## 中文说明

这个文件记录 GroundedDeck 当前所处阶段、下一步动作和阶段性完成条件，是跨会话继续工作的主状态文件。

## North Star

## 北极星目标

Build a local-first, source-grounded presentation system that produces NotebookLM-style deck quality with editable PPTX output, stronger Chinese support, and explicit self-acceptance.

构建一个本地优先、基于来源材料约束的演示系统，产出接近 NotebookLM 质量的 deck，支持可编辑 PPTX、更强中文能力，以及显式自验收。

## Current Phase

## 当前阶段

Foundation complete. The repository has:

基础阶段已完成，仓库目前具备：

- product and architecture definitions
- open-source repository docs
- a deterministic self-acceptance harness
- a stable `slide spec` schema
- a repository-as-memory continuity contract for future AI sessions

- 产品与架构定义
- 开源仓库所需文档
- 可确定性 self-acceptance harness
- 稳定的 `slide spec` schema
- 面向未来 AI 会话的 repository-as-memory 连续性契约

## Completed So Far

## 已完成内容

- named the project `GroundedDeck`
- published the public repository scaffold
- defined the architecture split between ingest, planner, visual, renderer, and quality
- defined initial eval-driven project rules
- added open-source community files and templates
- added AI continuity, anti-drift, and project-state artifacts
- added startup, handoff, and task-board artifacts for session continuation

- 将项目命名为 `GroundedDeck`
- 发布了公开仓库脚手架
- 定义了 ingest、planner、visual、renderer、quality 的架构拆分
- 定义了初始的 eval-driven 项目规则
- 添加了开源社区所需文档与模板
- 添加了 AI continuity、anti-drift 和 project-state 工件
- 添加了 startup、handoff 和 task-board 工件以支持跨会话恢复

## Current Next Action

## 当前唯一下一步

Implement the first real pipeline slice: `ingest -> normalized source units -> slide spec draft -> quality checks`.

实现第一条真正的流水线切片：`ingest -> normalized source units -> slide spec draft -> quality checks`。

## Immediate Priorities

## 近期优先级

1. define the normalized source-unit format
2. add example input and example `slide spec` fixture
3. add schema validation and fixture grading to the harness

1. 定义 normalized source-unit 格式
2. 添加示例输入和示例 `slide spec` fixture
3. 为 harness 增加 schema 校验和 fixture grading

## Active Constraints

## 当前约束

- local-first design
- editable output remains a hard requirement
- Chinese rendering quality is a first-class requirement
- architecture must remain source-grounded and auditable
- repository docs must stay sufficient for AI continuation

- 本地优先设计
- 输出可编辑仍然是硬性要求
- 中文渲染质量是一等需求
- 架构必须保持 source-grounded 且可审计
- 仓库文档必须足以支持 AI 跨会话继续工作

## Definition of Done for Phase One

## 第一阶段完成定义

- a source pack can be ingested into normalized units
- a planner can emit a schema-valid `slide spec`
- the harness can grade fixtures and fail on regressions
- project docs explain the current state and next action without relying on chat history

- source pack 能被摄取并转换为 normalized units
- planner 能输出 schema-valid 的 `slide spec`
- harness 能对 fixtures 打分，并在回归时失败
- 项目文档能在不依赖聊天历史的情况下说明当前状态与下一步

## Update Rule

## 更新规则

If the active phase, next action, constraints, or current target changes, update this file in the same change set.

如果当前阶段、下一步、约束或目标发生变化，必须在同一个 change set 中更新本文件。
