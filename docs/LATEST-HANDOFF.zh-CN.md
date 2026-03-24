# Latest Handoff

[English](LATEST-HANDOFF.md) | [简体中文](LATEST-HANDOFF.zh-CN.md)

这个文件记录最近一次会话结束时的状态，帮助下一次会话不依赖聊天历史直接恢复工作。

## 会话摘要

GroundedDeck 仍然以已归档的 strongest-demo acceptance snapshot 作为 provider-planning 基线；而这次 curator 轮次已经把 `auto/groundeddeck-auto-sprint-b/grading-acceptance-delta-check` 上被接受的 worker 补丁提升到主线准备分支。当前滚动 live 指针已经刷新到新的通过快照 `strongest-demo-1774381550`，新的 comparison helper 也确认它除时间戳外仍与已接受的 `strongest-demo-1774370225` 基线一致。

## 刚刚完成的内容

- 添加了 [AGENTS.md](../AGENTS.md) 作为 AI 操作契约
- 添加了 [docs/PROJECT-STATE.md](PROJECT-STATE.md) 作为规范当前状态记录
- 添加了 [docs/ARCHITECTURE-DECISIONS.md](ARCHITECTURE-DECISIONS.md) 用于防止架构漂移
- 扩展了 harness，使 continuity artifacts 成为必需项
- 添加了 [START-HERE.md](../START-HERE.md) 作为快速启动入口
- 调整文档多语言策略，采用独立语言文件加切换链接，而不是同页混排
- 添加了 normalized source-unit schema 和 fixture 文件
- 实现了确定性的 ingest、planning 和 quality 模块
- 扩展了 `make eval`，让它执行 pipeline fixture 测试
- 为 planner 和 quality 模块引入了 provider abstraction
- 添加了 runtime pipeline 入口和示例命令
- 接通了 OpenAI-compatible provider 路径，并增加了严格的本地响应校验
- 添加了拒绝 deterministic fallback 的 `make verify-online` 路径
- 为运行时执行增加了自动生成的 verification-summary 工件
- 收紧了 live env 检查，`REPLACE_ME` 这类占位值现在会被视为无效配置
- 吸收了一轮外部产品反馈，把近期重点收敛到最强 demo 和 planning-quality 证明点，但没有改动架构边界
- 添加了 `docs/AUTOMATION-GOVERNANCE.md`，并把 automation 处理规则纳入启动必读
- 将 4 个 detached automation worktree 恢复到命名救援分支上，避免有效工作继续丢在匿名状态
- 验收 strongest-demo 的救援工作，落下一套规范 fixture bundle、确定性质量指标和 `make strongest-demo`
- 添加了 `make curator-finalize`，让后续 curator run 通过同一条仓库内置的合并与清理流程收尾
- 把 live provider 路径配置到 MiniMax-M2.7，并将第一次成功的 strongest-demo 在线验证归档到 `reports/live-verification-latest.{json,md}`
- 强化了 OpenAI-compatible provider 集成，使 MiniMax 的推理输出可以被拆分，`<think>` 包裹的 JSON 结果也能被稳定解析和诊断
- 增加了仓库内置的 automation 角色锁工具，让 worker 和 curator 的更高频调度也能避免实质工作重叠
- 整合了 `auto/groundeddeck-auto-sprint/provider-planning-prompt-tightening` 上被接受的 worker 补丁
- 围绕 strongest-demo 的基线结构、布局预期和评分重点收紧了 OpenAI-compatible provider 的 planner 与 grader prompt
- 补回了 `src/visual/__init__.py` 和 `src/renderer/__init__.py`，让当前仓库树重新满足 self-acceptance 的完整性检查
- 重新运行了 `python3 -m pytest tests/test_pipeline.py` 和 `make eval`，当前 curator 分支均通过
- 将 canonical repo 中的 `.env.runtime.local` 链接到当前 worktree，然后依次运行了 `make check-live-env`、`make live-status`、`make verify-online` 和 `make archive-online-verification`
- 用收紧后的 prompt 基线刷新了 `reports/live-verification-latest.{json,md}`，且 strongest-demo 在线验证结果为通过
- 更新了 `make archive-online-verification`，让归档后的 live summary 现在指向 `reports/live-verification-history/` 下的仓库内副本
- 将刷新后的 strongest-demo live artifacts 和结构化 acceptance summary 固化到 `reports/live-verification-history/strongest-demo-1774362852/`
- 增加了确定性测试，校验 strongest-demo 的已归档 acceptance summary 仍然和提交进仓库的 live slide spec / quality report 一致
- 整合了 `auto/groundeddeck-auto-sprint-b/provider-planning-acceptance-alignment` 上被接受的 worker 补丁
- 让 OpenAI-compatible provider 的 planner / grader prompt 以及 mocked transport 测试直接编码已归档 strongest-demo acceptance summary
- 在 acceptance-alignment 补丁落地后重新运行了 `make eval`、`make check-live-env`、`make live-status`、`make verify-online` 和 `make archive-online-verification`
- 再次刷新 `reports/live-verification-latest.{json,md}`，并将一致的 strongest-demo live 快照归档到 `reports/live-verification-history/strongest-demo-1774366441/`
- 确认 `reports/live-verification-history/strongest-demo-1774366441/acceptance-summary.json` 与此前接受的 strongest-demo 基线在结构上保持一致
- 在执行 curator review 之前，将当前 automation worktree 从 detached `HEAD` 恢复并挂接到 `curator/groundeddeck-auto-sprint-2b-curator-20260324`
- 复核了剩余本地 worker prompt 变体分支，确认它们只是替代性 prompt 结构，没有比当前 acceptance-aligned strongest-demo 基线更新的归档验证结果
- 将当前 automation worktree 从 detached `HEAD` 恢复并挂接到 `curator/groundeddeck-auto-sprint-2-20260325`
- 以 curator 自有补丁的方式整合了 `auto/groundeddeck-auto-sprint-b/acceptance-comparison-guardrail` 的已接受方向，让 strongest-demo planner / grader guardrail 直接读取 `reports/live-verification-history/strongest-demo-1774366441/acceptance-summary.json`
- 收紧 strongest-demo prompt 文案，让 summary slide 必须把 `source_bindings` 和 `must_include_checks` 设置为显式空数组，而不是省略这些字段
- 更新了 prompt 回归测试以及归档 acceptance 校验测试，使其指向当前已接受 strongest-demo 快照
- 重新运行了 `python3 -m pytest tests/test_pipeline.py tests/test_verification_artifacts.py` 和 `make eval`，当前 curator 分支均通过
- 将 canonical repo 中的 `.env.runtime.local` 链接到当前 worktree，然后重新运行了 `make check-live-env`、`make live-status`、`make verify-online` 和 `make archive-online-verification`
- 修复了一次 live 回归：provider 在封面 summary slide 上省略了必填 evidence 字段；现在 strongest-demo prompt 已明确要求输出空数组
- 刷新 `reports/live-verification-latest.{json,md}`，并将通过的 strongest-demo live 快照归档到 `reports/live-verification-history/strongest-demo-1774370225/`
- 确认新的 `strongest-demo-1774370225` acceptance summary 除运行时间戳外，与已接受 strongest-demo 基线在结构上保持一致
- 修正了 `docs/STRONGEST-DEMO.{md,zh-CN.md}`，让 strongest-demo 的 canonical 引用改为指向仓库内已接受的 `reports/live-verification-history/strongest-demo-1774370225/`，不再引用过时的 worktree 路径
- 复核了 `auto/groundeddeck-auto-sprint/provider-grading-prompt-tightening`、`auto/groundeddeck-auto-sprint-b/acceptance-comparison-tightening` 和 `auto/groundeddeck-auto-sprint-c/strongest-demo-slide-id-guardrails`，确认它们仍是未经过更新归档验证的 prompt 变体，暂时没有足够依据继续上升
- 将 strongest-demo provider guardrail 基线、确定性测试和 canonical 下一步文档里的引用统一从 `strongest-demo-1774366441` 切换到当前已接受的仓库内快照 `strongest-demo-1774370225`
- 将 canonical repo 中的 `.env.runtime.local` 链接到当前 worktree，然后为这次基线指针统一改动运行了 `make check-live-env`、`make live-status`、`make verify-online` 和 `make archive-online-verification`
- 记录了一次失败的 live refresh：`reports/live-verification-history/strongest-demo-1774374274/`；随后重新执行 live verification，并将通过的 strongest-demo live 快照归档到 `reports/live-verification-history/strongest-demo-1774374429/`
- 确认 `reports/live-verification-history/strongest-demo-1774374429/acceptance-summary.json` 除运行时间戳外，与已接受 strongest-demo 基线在结构上保持一致
- 再次复核剩余 worker 分支后，接受了 `auto/groundeddeck-auto-sprint-b/grading-acceptance-delta-check`，因为它是在代码里固化当前 strongest-demo acceptance-snapshot 对比规则，而不是继续引入未验证的 prompt 变体
- 整合了该 worker 补丁，使 `src/runtime/verification.py` 现在提供 `compare_acceptance_summaries()`，并由确定性测试断言：已接受 strongest-demo acceptance summary 与后续刷新结果之间，只有 `generated_at_unix` 可以不同
- 将 canonical repo 中的 `.env.runtime.local` 链接到当前 worktree，然后为这次 acceptance-delta comparison 补丁运行了 `make check-live-env`、`make live-status`、`make verify-online` 和 `make archive-online-verification`
- 第一次重试 `make verify-online` 时遇到一次瞬时的 live grader 格式失败；随后重新执行 live verification，并将通过的 strongest-demo live 快照归档到 `reports/live-verification-history/strongest-demo-1774381550/`
- 确认 `reports/live-verification-history/strongest-demo-1774381550/acceptance-summary.json` 除运行时间戳外，与已接受 strongest-demo 基线在结构上保持一致

## 当前状态

- 仓库连续性契约：已具备
- startup 与 handoff 路径：已具备
- 确定性 harness：通过
- 确定性 pipeline 基线：通过
- provider abstraction：已具备
- OpenAI-compatible provider 路径：已具备，且可在本地测试
- live verification 工具链：已就绪，且已被验证
- placeholder env detection：已具备
- live status 已能正确报告环境是否就绪以及最近一次归档结果
- live 凭证 / 真实后端：已配置，并用 MiniMax-M2.7 验证通过
- strongest-demo 规范工件包：已存在
- worker / curator / verifier 流程的 automation governance：已具备
- 面向更高频调度的 automation 角色锁：已具备
- 第一次 strongest-demo 成功 online verification：已归档到 `reports/live-verification-latest.json` 和 `reports/live-verification-latest.md`
- 近期重点：以已验证的 strongest-demo 基线继续扩展 provider-backed planning，同时不削弱确定性 eval
- strongest-demo 的 provider prompt 收紧：已整合到当前 curator 分支
- strongest-demo 的 acceptance-aligned provider prompt guardrail：已整合到当前 curator 分支
- prompt 收紧后的 self-acceptance：通过
- prompt 收紧后的 strongest-demo online verification：通过且已重新归档
- live verification archive 现在会保留已验证工件的仓库内副本，而不再只记录 `/tmp` 路径
- 刷新后的 strongest-demo live acceptance snapshot：已提交到 `reports/live-verification-history/strongest-demo-1774362852/`
- acceptance alignment 之后再次刷新的 strongest-demo live acceptance snapshot：已存在于 `reports/live-verification-history/strongest-demo-1774366441/`
- strongest-demo prompt guardrail 现在直接从已归档 acceptance summary 加载，而不是在代码里重复维护常量
- strongest-demo 的 summary-slide prompt 现在会显式要求空 evidence 数组，从而恢复 live provider 对 slide-spec 校验的满足
- acceptance-summary 驱动 guardrail 补丁落地后的 strongest-demo live acceptance snapshot：已存在于 `reports/live-verification-history/strongest-demo-1774370225/`
- strongest-demo acceptance-delta comparison helper：已存在于 `src/runtime/verification.py`，并有确定性回归测试覆盖
- acceptance-delta comparison 补丁落地之后最近一次通过的 strongest-demo live refresh：已存在于 `reports/live-verification-history/strongest-demo-1774381550/`
- 最新归档 strongest-demo live refresh 与已接受基线在结构上仍然对齐，变化只有运行时间戳
- 最新归档 strongest-demo acceptance snapshot 与此前接受的基线在结构上保持一致
- strongest-demo 的 canonical 文档引用现在已经固定到仓库内已接受的 live 快照 `reports/live-verification-history/strongest-demo-1774370225/`
- provider guardrail 代码、确定性测试和 canonical 下一步文档现在都指向同一个已接受的 strongest-demo 快照：`reports/live-verification-history/strongest-demo-1774370225/`
- 当前滚动 live 指针现在指向 `reports/live-verification-history/strongest-demo-1774381550/`，而已接受的 strongest-demo 基线仍然是 `reports/live-verification-history/strongest-demo-1774370225/`
- 剩余 worker prompt 变体：已经复核，但都没有针对更新归档 strongest-demo acceptance delta 的验证结果，因此暂时没有进一步的 worker 输出等待整合
- renderer 实现：仍然延后

## 立即下一步

使用已归档的 strongest-demo live acceptance snapshot 对比后续 live refresh，再决定后续 provider-backed planning 改动是否可以继续上升。

## 第一批具体任务

1. 将 `reports/live-verification-latest.json` 和 `reports/live-verification-latest.md` 视为指向最新 live 历史快照的滚动指针
2. 让后续 strongest-demo 在线刷新结果与 `reports/live-verification-history/strongest-demo-1774370225/acceptance-summary.json` 做对比
3. 在保留 `make eval` 稳定性的前提下，让 `make verify-online` 在真实 provider 路径上持续可用
4. 在出现比 `strongest-demo-1774381550` 更新的已验证 worker 补丁或 live refresh 差异之前，不要继续上升新的 provider prompt 改动

## 不要漂移

- 不要从 renderer 开始
- 不要把项目压扁成单 prompt 流水线
- 不要跳过中间层 `slide spec`
- 不要让状态变化缺少文档记录
- 不要让 worker automation 修改 canonical state docs，也不要让它们直接写 `main`
- 后续再讨论 strongest-demo live path 时，不要回退到旧的 example fixture

## 恢复提示

如果未来某次会话只收到一句指令，那应该是：

`Continue GroundedDeck from START-HERE.md and follow the current next action.`
