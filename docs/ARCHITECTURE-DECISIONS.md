# Architecture Decisions

## 中文说明

这个文件记录不允许被静默漂移的架构决策和不变量。凡是改变架构边界或固定原则的修改，都必须在这里留下记录。

## Fixed Invariants

## 固定不变量

These decisions should not drift silently:

以下决策不允许被静默漂移：

1. GroundedDeck is a source-grounded presentation system, not a generic prompt-only PPT generator.
2. `slide spec` is the stable contract between planning, rendering, and grading.
3. The renderer must not own source understanding.
4. Editability is a required product property, not an optional enhancement.
5. Chinese rendering quality is a required product property, not a polish pass.
6. Harness engineering is part of the product architecture, not a sidecar test layer.

1. GroundedDeck 是基于来源材料约束的演示系统，不是通用 prompt-only PPT 生成器。
2. `slide spec` 是 planning、rendering 和 grading 之间的稳定契约。
3. renderer 不能承担来源理解。
4. 可编辑性是产品硬属性，不是可选增强。
5. 中文渲染质量是产品硬属性，不是后期打磨。
6. harness engineering 是产品架构的一部分，不是旁路测试层。

## Decision Log

## 决策日志

### AD-0001: Repository-as-memory

- Status: accepted
- Why: AI-driven development will span many sessions, so project continuity must live in the repository rather than chat history.
- Consequence: `AGENTS.md`, `docs/PROJECT-STATE.md`, and this file become canonical context for future sessions.

- 状态：accepted
- 原因：AI 驱动开发会跨越多个会话，因此项目连续性必须保存在仓库里，而不是聊天历史里。
- 结果：`AGENTS.md`、`docs/PROJECT-STATE.md` 和本文件成为未来会话的规范上下文。

### AD-0002: Intermediate representation first

- Status: accepted
- Why: direct slide generation causes dropped content, poor editability, and weak auditability.
- Consequence: all meaningful generation should converge on `slide spec` before rendering.

- 状态：accepted
- 原因：直接生成 slide 容易导致内容遗漏、可编辑性差、可审计性弱。
- 结果：所有有意义的生成过程都应先收敛到 `slide spec`，再进入渲染阶段。

### AD-0003: Anti-drift quality gates

- Status: accepted
- Why: long-running AI implementation tends to drift toward convenience unless guarded by explicit checks.
- Consequence: harness rules must evolve alongside architecture and must block missing continuity artifacts.

- 状态：accepted
- 原因：长期 AI 实现如果没有显式检查，很容易朝着“方便但偏离目标”的方向漂移。
- 结果：harness 规则必须随架构一起演进，并阻止 continuity artifacts 缺失。

## Change Policy

## 变更策略

If a future change alters a fixed invariant or changes the module split, record a new decision entry in this file and update [docs/PROJECT-STATE.md](PROJECT-STATE.md).

如果未来修改改变了固定不变量或模块拆分，必须在本文件中增加新的决策记录，并同步更新 [docs/PROJECT-STATE.md](PROJECT-STATE.md)。
