# Source Modules

[English](README.md) | [简体中文](README.zh-CN.md)

- `ingest`：来源解析和 source binding。
- `planner`：叙事规划和 deck outline 生成。
- `visual`：视觉形式选择和图示规划。
- `renderer`：可编辑 PPTX 渲染。
- `quality`：coverage、grounding 和风格检查。

这些目录当前只作为边界占位，后续实现代码按这个责任切分。

GroundedDeck 有意把来源理解、规划、视觉选择、渲染和质量 grading 分开，以避免项目退化成单一 prompt 驱动的 PPT 生成器。
