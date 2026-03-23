# Roadmap

[English](ROADMAP.md) | [简体中文](ROADMAP.zh-CN.md)

路线图描述 GroundedDeck 从脚手架到可演示产品的阶段性目标。里程碑应保持按能力递进，而不是先做 renderer 再回补规划能力。

## 里程碑 1：基础阶段

- 仓库脚手架
- 架构文档
- `slide spec` schema
- 确定性的 self-acceptance harness

## 里程碑 2：规划流水线

- 摄取 source pack 元数据
- 规范化提取出的 source units
- 编译 deck goals 和 slide outlines
- 输出 schema-valid 的 `slide spec`

## 里程碑 3：质量门禁

- coverage grader
- grounding grader
- duplication 和 coherence grader
- 生成 deck review 报告

## 里程碑 4：可编辑渲染

- 原生文本渲染
- 原生表格和图表
- 基于形状的图示模板
- 中文安全的排版默认值

## 里程碑 5：公开演示质量

- 示例数据集
- 可复现实例输出
- 面向发布候选版本的 benchmark rubric
