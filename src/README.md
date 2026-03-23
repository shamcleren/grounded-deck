# Source Modules

[English](README.md) | [简体中文](README.zh-CN.md)

- `ingest`: source parsing and source binding.
- `planner`: narrative planning and deck outline generation.
- `visual`: visual form selection and diagram planning.
- `renderer`: editable PPTX rendering.
- `quality`: coverage, grounding and style checks.

这些目录当前只作为边界占位，后续实现代码按这个责任切分。

GroundedDeck intentionally separates source understanding, planning, visual selection, rendering, and quality grading so the project does not collapse into a single prompt-driven PPT generator.
