# Source Modules

## 中文说明

`src/` 目录按职责边界拆分模块，避免把 ingest、planning、rendering 和 quality 混成一个大模块。

- `ingest`: source parsing and source binding.
- `planner`: narrative planning and deck outline generation.
- `visual`: visual form selection and diagram planning.
- `renderer`: editable PPTX rendering.
- `quality`: coverage, grounding and style checks.

- `ingest`：来源解析和 source binding。
- `planner`：叙事规划和 deck outline 生成。
- `visual`：视觉形式选择和图示规划。
- `renderer`：可编辑 PPTX 渲染。
- `quality`：coverage、grounding 和风格检查。

这些目录当前只作为边界占位，后续实现代码按这个责任切分。

GroundedDeck intentionally separates source understanding, planning, visual selection, rendering, and quality grading so the project does not collapse into a single prompt-driven PPT generator.

GroundedDeck 有意把来源理解、规划、视觉选择、渲染和质量 grading 分开，以避免项目退化成单一 prompt 驱动的 PPT 生成器。
