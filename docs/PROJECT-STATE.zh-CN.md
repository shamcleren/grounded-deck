# 项目状态

[English](PROJECT-STATE.md) | [简体中文](PROJECT-STATE.zh-CN.md)

## 北极星

构建一个本地优先、来源溯源的演示文稿系统，产出 NotebookLM 级别的演示文稿质量，支持可编辑 PPTX 输出、更强的中文支持和明确的自验收。

## 当前阶段

基础建设完成。确定性基线管道和提供者抽象已就位。仓库已具备：

- 产品和架构定义
- 开源仓库文档
- 确定性自验收工具
- 稳定的 `slide spec` Schema
- 规范化的 source-unit Schema
- 基于 fixture 的摄入、规划和质量检查
- 可插拔的提供者接口，用于规划器和质量模块
- 面向未来 AI 会话的仓库即记忆连续性合约

最强确定性规划 demo 已作为规范 fixture 包和报告路径整理回 `main` 分支，首次成功的在线验证已归档。

## 已完成内容

- 项目命名为 `GroundedDeck`
- 发布了公共仓库脚手架
- 定义了摄入、规划器、视觉、渲染器和质量之间的架构分层
- 定义了初始评估驱动项目规则
- 添加了开源社区文件和模板
- 添加了 AI 连续性、防漂移和项目状态构件
- 添加了启动、交接和任务板构件用于会话延续
- 实现了确定性 `source pack → normalized source units → slide spec draft → quality checks` 基线
- 添加了基于 fixture 的管道测试和工具验证
- 引入了提供者抽象，包含确定性提供者基线
- 添加了运行时管道入口用于基于 fixture 的执行
- 接入了 OpenAI 兼容提供者路径，包含严格的本地响应验证和模拟传输测试
- 定义了 worker、curator 和 verifier 流程的仓库自动化治理
- 将分离的自动化工作树恢复到命名的救援分支以便追踪变更
- 将救援的 strongest-demo 工作整理为一个规范的 fixture 包、报告路径和确定性指标基线
- 捕获并归档了首次成功的在线验证运行（使用 MiniMax-M2.7 针对规范 strongest-demo 输入）
- 强化了 OpenAI 兼容提供者路径（MiniMax），分离推理输出并容忍 `<think>` 包裹的 JSON 响应
- 集成了收紧提供者规划器和评分器提示词的已接受 worker 补丁
- 恢复了 `src/visual` 和 `src/renderer` 包脚手架
- 刷新了 strongest-demo 在线验证并重新归档通过结果
- 将刷新的 strongest-demo 在线运行提升为仓库拥有的历史快照，包含结构化 acceptance summary
- 用从已归档在线快照加载的 acceptance-summary 驱动的提示词护栏替换了重复的 strongest-demo 提示词常量
- 收紧了 strongest-demo 提示词规则，要求摘要幻灯片必须发出显式空 evidence 数组
- 多次刷新 strongest-demo 在线验证并归档结构匹配的在线快照
- 集成了 acceptance delta 比较的已接受 worker 补丁
- 从 `DeterministicProvider` 中提取视觉形式选择器到独立的 `src/visual/selector.py` 模块
- 添加了 `LayoutSelection` 数据类、`validate_model_layouts` 函数和 `LayoutValidationReport` 数据类
- 将视觉选择器接入 `OpenAICompatibleProvider` 用于后验证和评分信号注入
- 添加了模型辅助布局推断功能
- 实现了 PPTX 渲染器脚手架，支持全部 7 种布局类型
- 将 PPTX 渲染器接入运行时管道、CLI 和 demo
- `make render-demo` 成功生成 `reports/strongest-demo/strongest-demo.pptx`（6 张幻灯片，46KB）
- 丰富了视觉元素的来源溯源内容提取
- 丰富了封面和摘要幻灯片的内容
- 添加了 `narrative_quality` 维度到质量报告
- 创建了 `src/renderer/artifact_grader.py` 用于 PPTX 构件评分
- 将构件评分器接入管道、CLI、demo 和 eval harness
- 实现了基于模型的叙事质量评分（确定性 + 模型辅助模式）
- 评估计划第一阶段 + 第二阶段 + 第三阶段：全部完成
- 在 `src/quality/continuity_grader.py` 中实现了连续性构件评分
- 将连续性评分接入 eval harness（40/40 检查通过）
- 在 `src/runtime/verification.py` 中实现了自动化 acceptance delta 比较
- 添加了 `acceptance-baseline` 检查到 eval harness（38/38 评估通过）
- 添加了 `make compare-acceptance` Makefile 目标
- 总计 248 个测试通过

## 当前下一步行动

继续改进提供者支持的规划和评分，针对 strongest-demo 路径，同时不削弱确定性覆盖。

## 即时优先级

1. 评估连续性构件，确保未来代理能仅从仓库状态安全恢复
2. 评估交接完整性和任务板新鲜度
3. 保留仓库拥有的 strongest-demo 在线 acceptance 快照，同时保持 `reports/live-verification-latest.*` 作为滚动指针
4. 将未来的 strongest-demo 在线刷新与已归档的 acceptance summary 进行比较，而非将每次通过的运行视为可互换
5. 保持提供者支持的规划改进、acceptance 对齐的提示词护栏和 `make verify-online` 健康，同时不削弱确定性回归覆盖

外部反馈已作为优先级变更而非架构变更被吸收。环境变量配置合约记录在 `docs/runtime-config.md` 中，占位符值在在线预检时被拒绝，strongest-demo 在线路径已在真实提供者上验证通过，同时保留了确定性基线。

## 活跃约束

- 本地优先设计
- 可编辑输出仍是硬性要求
- 中文渲染质量是一等要求
- 架构必须保持来源溯源和可审计
- 仓库文档必须足以支持 AI 延续
- 反馈可以改变优先级和 demo 策略，但不得静默改变架构边界

## 第一阶段完成定义

- source pack 可以被摄入为规范化 units
- 规划器可以发出符合 Schema 的 `slide spec`
- 工具可以对 fixture 评分并在回归时失败
- 项目文档能在不依赖聊天历史的情况下解释当前状态和下一步行动

## 更新规则

如果活跃阶段、下一步行动、约束或当前目标发生变化，在同一变更集中更新此文件。
