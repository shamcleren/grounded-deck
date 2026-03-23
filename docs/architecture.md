# Architecture

## 中文说明

GroundedDeck 的架构按“来源理解、叙事规划、视觉选择、结构化中间表示、渲染、质量验证”来分层，避免把所有能力压缩进单一 prompt。

## System Layers

## 系统分层

### 1. Source Understanding

### 1. 来源理解

Accepts PDFs, DOCX, web pages, images, and tables, then extracts:

接收 PDF、DOCX、网页、图片和表格，并提取：

- heading hierarchy
- claims and conclusions
- metrics and numbers
- time information
- roles and object relationships
- candidate visual structures
- source bindings

- 标题层级
- 结论与主张
- 指标与数字
- 时间信息
- 角色与对象关系
- 候选视觉结构
- source bindings

### 2. Narrative Planner

### 2. 叙事规划器

Builds:

生成：

- presentation goal
- audience framing
- deck narrative path
- slide-level outline
- evidence that must be covered per slide

- 演示目标
- 受众 framing
- deck 的叙事路径
- slide 级 outline
- 每页必须覆盖的证据

### 3. Visual Form Selector

### 3. 视觉形式选择器

Maps information structure to visual structure:

将信息结构映射为视觉结构：

- temporal change -> timeline
- option differences -> comparison or matrix
- process steps -> flow
- concept decomposition -> hierarchy
- metric summary -> chart or number cards

- 时间变化 -> timeline
- 选项差异 -> comparison 或 matrix
- 流程步骤 -> flow
- 概念拆解 -> hierarchy
- 指标总结 -> chart 或 number cards

### 4. Slide Spec Compiler

### 4. Slide Spec 编译器

Produces the structured intermediate representation used by renderers and graders.

生成供 renderer 和 grader 使用的结构化中间表示。

Required properties:

必须具备的属性：

- auditable
- partially regenerable
- editable
- compatible with coverage and grounding checks

- 可审计
- 可部分重生成
- 可编辑
- 与 coverage、grounding 检查兼容

### 5. PPTX Renderer

### 5. PPTX 渲染器

Turns `slide spec` into editable PPTX output with these priorities:

将 `slide spec` 渲染成可编辑 PPTX，优先级如下：

- native text boxes
- native tables
- native charts where possible
- shape-based diagrams instead of screenshots
- explicit Chinese font defaults

- 原生文本框
- 原生表格
- 尽可能使用原生图表
- 用基于形状的图示替代截图
- 明确的中文字体默认值

### 6. Quality Harness

### 6. 质量 Harness

Provides machine-executable self-acceptance:

提供机器可执行的自验收：

- repository completeness
- schema completeness
- eval completeness
- future deck artifact checks for coverage and grounding

- 仓库完整性
- schema 完整性
- eval 完整性
- 未来 deck artifact 的 coverage 和 grounding 检查

## Data Flow

## 数据流

```text
Sources
  -> ingest
  -> planner
  -> visual selector
  -> slide spec
  -> renderer
  -> quality harness
  -> report
```

这条数据流体现了一个核心原则：内容理解发生在前面，renderer 只消费已经规划好的 `slide spec`。

## Guardrails

## 护栏规则

- Do not treat long-form summarization as presentation planning.
- Do not push content understanding into the renderer.
- Do not output final PPT artifacts without an auditable intermediate form.
- Do not rely on image-heavy slide baking where editable native objects are possible.
- Do not ignore Chinese typography and layout stability.

- 不要把长文本摘要等同于 presentation planning。
- 不要把内容理解推给 renderer。
- 没有可审计中间形式时，不要输出最终 PPT 工件。
- 只要能用原生可编辑对象，就不要依赖重图片化的 slide baking。
- 不要忽视中文排版与布局稳定性。
