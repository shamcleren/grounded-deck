# Product Vision

## 中文说明

这个文件描述 GroundedDeck 的质量目标、用户价值、差异化和非目标，用于约束产品方向，避免做成“会排版但不理解内容”的 PPT 生成器。

## Quality Bar

## 质量标准

GroundedDeck targets NotebookLM-like presentation quality, which means all of the following should be true at the same time:

GroundedDeck 的目标是接近 NotebookLM 风格的演示质量，这意味着下面这些条件要同时成立：

1. The system understands sources before it plans slides.
2. Each slide carries a clear claim or takeaway.
3. The deck has narrative progression instead of summary fragments.
4. The system chooses the right visual form for the information structure.
5. Facts, numbers, and claims stay traceable to source material.
6. The output remains editable in PowerPoint.
7. Chinese text and labels remain sharp and layout-stable.

1. 系统在规划 slides 之前先理解来源材料。
2. 每一页都带有明确主张或 takeaway。
3. 整套 deck 具备叙事推进，而不是摘要碎片堆叠。
4. 系统会为对应的信息结构选择正确的视觉形式。
5. 事实、数字和结论都能追溯回来源材料。
6. 输出在 PowerPoint 中保持可编辑。
7. 中文文本和标签清晰、布局稳定。

## User Value

## 用户价值

- Save high-cost thinking work, not only formatting time.
- Reduce hallucinated or untraceable claims in presentations.
- Compress large source packs into a presentation narrative.
- Support Chinese-heavy presentation workflows better than English-first tools.

- 节省高成本思考工作，而不只是节省排版时间。
- 减少演示中幻觉化或不可追溯的结论。
- 将大型 source pack 压缩为有叙事结构的演示内容。
- 比英文优先工具更好地支持重中文场景的演示工作流。

## Differentiators

## 差异化

- Stronger editability than NotebookLM.
- Stronger Chinese readability and rendering stability than NotebookLM.
- Better content coverage control than generic AI PPT generators.
- Harness-engineered self-acceptance instead of subjective “looks good enough” review.

- 比 NotebookLM 更强调可编辑性。
- 比 NotebookLM 提供更强的中文可读性与渲染稳定性。
- 比通用 AI PPT 生成器提供更好的内容覆盖控制。
- 用 harness-engineered self-acceptance 替代主观的“看起来差不多”评审。

## Non-Goals

## 非目标

- A polished end-user UI in phase one.
- Full visual style coverage in phase one.
- Multi-user collaboration in phase one.

- 第一阶段不追求完整 polished 的终端用户 UI。
- 第一阶段不追求覆盖全部视觉风格。
- 第一阶段不做多用户协作。

## Phase One Deliverables

## 第一阶段交付物

- Stable repository boundaries and module ownership.
- A structured `slide spec` intermediate representation.
- Deterministic local self-acceptance commands.
- Clear insertion points for future ingestion, planning, and rendering work.

- 稳定的仓库边界和模块归属。
- 结构化的 `slide spec` 中间表示。
- 确定性的本地 self-acceptance 命令。
- 为未来 ingest、planning、rendering 工作保留清晰插入点。
