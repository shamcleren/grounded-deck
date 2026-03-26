# 任务板

[English](TASK-BOARD.md) | [简体中文](TASK-BOARD.zh-CN.md)

## 进行中

- 保持 strongest-demo 提供者提示词和在线验证与已归档的 acceptance snapshot 对齐，然后再推进更多提供者支持的规划变更
- 通过独立语言文件和切换链接保持规范文档双语

## 最近完成

- 在 `src/runtime/verification.py` 中实现了自动化 acceptance delta 比较
- `compare_against_accepted_baseline()` 函数将任意候选 acceptance summary 与已接受的基线进行比较
- `render_acceptance_delta_report()` 将 delta 结果渲染为 Markdown
- `ACCEPTED_STRONGEST_DEMO_BASELINE` 常量指向规范的已接受快照
- `archive_verification_summary` 现在在归档时自动生成 `acceptance-delta.json` 和 `acceptance-delta.md`
- 在 eval harness 中添加了 `acceptance-baseline` 检查（38/38 评估通过）
- 添加了 `make compare-acceptance` Makefile 目标用于独立基线比较
- 添加了 12 个 acceptance 基线比较测试，总计 248 个通过
- 在 `src/quality/continuity_grader.py` 中实现了连续性构件评分
- `ContinuityGradeReport` 包含结构、一致性和新鲜度检查，覆盖 6 个连续性文件
- 检查文件存在性、必需章节、章节非空、跨文件下一步行动对齐、交接完整性、任务板新鲜度
- 将连续性评分接入 eval harness（`continuity-grading` 检查，37/37 评估通过）
- 添加了 38 个连续性评分器测试，总计 236 个通过
- 评估计划连续性评分项：完成
- 实现了基于模型的叙事质量评分（评估计划第三阶段）
- 创建了 `src/quality/narrative_grader.py`，支持确定性和模型辅助模式
- 三维评分：连贯性（key_points 质量）、溯源性（来源可追溯性）、视觉适配性（布局匹配）
- `NarrativeGradeReport` 数据类，包含综合评分、状态和序列化
- `OpenAICompatibleProvider.build_narrative_callback()` 用于模型辅助评分
- 将叙事评分接入管道（`grade_narrative_quality` 参数）、CLI、demo 和 eval harness
- eval harness 现在包含 `narrative-grading` 检查（36/36 评估通过）
- 添加了 26 个叙事评分器测试 + 7 个管道集成测试，总计 198 个通过
- 评估计划第一阶段 + 第二阶段 + 第三阶段：全部完成
- 在 `DeterministicProvider.grade_slide_spec` 质量报告中添加了 `narrative_quality` 维度
- 创建了 `src/renderer/artifact_grader.py`，包含 `grade_pptx_artifact` 用于 PPTX 可编辑性/备注/来源绑定验证
- 更新了 PPTX 渲染器以消费丰富的封面/摘要内容
- 添加了 6 个 ArtifactGradingTests + 7 个 NarrativeQualityTests，总计 156 个通过
- 丰富了 `src/visual/selector.py` 中 `build_visual_elements` 的来源溯源内容提取（events、column_points、step_labels、labels）
- 添加了 `_extract_comparison_points`、`_extract_process_steps`、`_extract_metric_labels`、`_extract_milestone_events` 辅助函数
- 丰富了 `DeterministicProvider.build_unit_slide` 的 key_points，使用 `_extract_key_points` 方法
- 更新了 PPTX 渲染器以消费丰富的 visual_elements
- 重新生成了两个 slide-spec fixture，添加了 8 个 ContentEnrichmentTests
- 通过 `run_pipeline` 的 `render_pptx` 关键字参数将 PPTX 渲染器接入 `src/runtime/pipeline.py`
- 更新了 `src/runtime/cli.py`，添加 `--render-pptx` CLI 参数
- 更新了 `src/runtime/demo.py`，自动渲染 `strongest-demo.pptx`
- 添加了 `render-demo` Makefile 目标用于端到端管道 + PPTX 渲染
- `make render-demo` 生成 `reports/strongest-demo/strongest-demo.pptx`（6 张幻灯片，46KB）
- 8 个新的管道 PPTX 集成测试，总计 135 个通过
- 在 `src/renderer/pptx_renderer.py` 中实现了 PPTX 渲染器脚手架，入口为 `render_slide_spec_to_pptx`
- 渲染器支持全部 7 种布局类型：cover、summary、timeline、comparison、process、chart、section
- 每种布局使用专业蓝灰配色方案生成样式化形状，包含演讲者备注和来源绑定审计追踪
- 添加了 `model_assisted_infer_layout_type` 函数，包含 `ModelLayoutCallback` 类型和自动规则回退
- 将 `src/visual/selector.py` 接入 `OpenAICompatibleProvider` 用于后验证和评分信号注入
- 从 `DeterministicProvider` 中提取视觉形式选择器到独立的 `src/visual/selector.py` 模块

## 待办

- 继续改进提供者支持的规划和评分，针对 strongest-demo 路径，同时不削弱确定性覆盖
- 在接受另一个提示词变更之前，将未来的 strongest-demo 在线刷新与 `reports/live-verification-history/strongest-demo-1774370225/acceptance-summary.json` 进行比较
- 将 strongest-demo 规范文档固定在当前已接受的仓库拥有快照上，直到接受更新的已验证快照
- 通过独立语言文件和切换链接保持规范文档双语

## 稍后

- 通过 OpenAI 兼容提供者添加模型辅助叙事和视觉形式评分
- 在 strongest demo 存在后，添加与通用 AI PPT 工具的公开对比案例

## 阻塞项

- 当前 strongest-demo 规划基线无阻塞项

## 更新规则

当任务开始时，将其移至 `进行中`。
当任务完成或过时时，在同一变更集中更新此文件。
