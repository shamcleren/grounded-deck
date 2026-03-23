# Architecture

[English](architecture.md) | [简体中文](architecture.zh-CN.md)

GroundedDeck 的架构按“来源理解、叙事规划、视觉选择、结构化中间表示、渲染、质量验证”来分层，避免把所有能力压缩进单一 prompt。

## 系统分层

### 1. 来源理解

接收 PDF、DOCX、网页、图片和表格，并提取：

- 标题层级
- 结论与主张
- 指标与数字
- 时间信息
- 角色与对象关系
- 候选视觉结构
- source bindings

### 2. 叙事规划器

生成：

- 演示目标
- 受众 framing
- deck 的叙事路径
- slide 级 outline
- 每页必须覆盖的证据

### 3. 视觉形式选择器

将信息结构映射为视觉结构：

- 时间变化 -> timeline
- 选项差异 -> comparison 或 matrix
- 流程步骤 -> flow
- 概念拆解 -> hierarchy
- 指标总结 -> chart 或 number cards

### 4. Slide Spec 编译器

生成供 renderer 和 grader 使用的结构化中间表示。

必须具备的属性：

- 可审计
- 可部分重生成
- 可编辑
- 与 coverage 和 grounding 检查兼容

### 5. PPTX 渲染器

将 `slide spec` 渲染成可编辑 PPTX，优先级如下：

- 原生文本框
- 原生表格
- 尽可能使用原生图表
- 用基于形状的图示替代截图
- 明确的中文字体默认值

### 6. 质量 Harness

提供机器可执行的自验收：

- 仓库完整性
- schema 完整性
- eval 完整性
- 未来 deck artifact 的 coverage 和 grounding 检查

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

## 护栏规则

- 不要把长文本摘要等同于 presentation planning。
- 不要把内容理解推给 renderer。
- 没有可审计中间形式时，不要输出最终 PPT 工件。
- 只要能用原生可编辑对象，就不要依赖重图片化的 slide baking。
- 不要忽视中文排版与布局稳定性。
