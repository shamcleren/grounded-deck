# Automation Governance

[English](AUTOMATION-GOVERNANCE.md) | [简体中文](AUTOMATION-GOVERNANCE.zh-CN.md)

这个文件定义 GroundedDeck 中定时任务和无人值守 AI 任务的运行规则。

## 为什么需要它

GroundedDeck 已经把仓库文档当作长期记忆。定时任务会带来第二层风险：多个 worktree 可能彼此漂移、修改重叠，或者把有价值的工作留在匿名的 detached worktree 里，始终没有进入仓库主线。

目标不是减少自动化，而是让自动化持续产出，同时不污染 `main`，不重复改状态文档，也不让有效工作遗失在 worktree 里。

## 固定规则

1. 任何 automation 都不能直接在 `main` 上工作。
2. 任何 automation 一旦开始修改，就不能继续停留在 `detached HEAD`。
3. worker automation 不得更新 canonical state docs：
   - `docs/PROJECT-STATE.md`
   - `docs/LATEST-HANDOFF.md`
   - `docs/TASK-BOARD.md`
4. 只有 curator 流程可以更新 canonical state docs，并为进入 `main` 做整理。
5. live verification 必须被当作独立职责处理，并留下归档工件。
6. 只有进入本仓库受跟踪文件的结果，才算真正进入 repository memory。

## Automation 角色

### 1. Worker

worker automation 只处理边界明确的实现任务，例如：

- strongest demo 的 fixture 和产物
- planner 或 quality 代码
- tests
- 报告或 demo bundle

worker 规则：

- 从隔离 worktree 启动
- 编辑前先创建或切换到命名分支
- 一次只推进一个连贯子任务
- 不碰 canonical state docs
- 结束时要么留下一个干净的原子提交，要么留下明确可恢复的 worktree 状态

### 2. Curator

curator 流程负责把 worker 的结果整理成规范仓库状态。

curator 职责：

- 审查候选 worker 分支
- 选一个整合基线
- 从其他 worker 分支中 cherry-pick 或手工移植不重叠的改动
- 解决冲突
- 更新 canonical state docs
- 运行 `make eval`
- 准备好可进入 `main` 的整合分支
- 当所有门槛都满足后，以 fast-forward 或其他有意识的方式把已验收 curator 分支合入 `main`
- 合并成功后，清理已合入的 curator 分支及其专属 worktree

只有 curator 角色才应当常规修改以下文件：

- `docs/PROJECT-STATE.md`
- `docs/LATEST-HANDOFF.md`
- `docs/TASK-BOARD.md`

### 3. Verifier

verifier automation 只负责 live verification。

verifier 职责：

- 运行 `make check-live-env`
- 运行 `make live-status`
- 运行 `make verify-online`
- 运行 `make archive-online-verification`
- 确认 `reports/live-verification-latest.json` 和 `reports/live-verification-latest.md` 已生成

verifier 不得静默用 deterministic 输出冒充 online verification。

## 分支与 Worktree 规则

- 每个 automation worktree 都必须绑定到命名分支。
- 分支名应当能表达归属和主题。
- 优先使用这些前缀：
  - `auto/<automation-id>/<topic>` 用于 worker
  - `curator/<topic>` 用于整合分支
  - `verify/<topic>` 用于 live verification
- 如果本地 Git ref 存储格式不支持带 `/` 的命名，就退化为平铺命名，例如 `auto-<automation-id>-<topic>`。
- detached worktree 视为事故，必须先恢复到命名分支，再继续工作。

## Canonical State Ownership

仓库有三份 canonical state 文件：

- `docs/PROJECT-STATE.md`
- `docs/LATEST-HANDOFF.md`
- `docs/TASK-BOARD.md`

规则如下：

- worker 分支可以读取，但不应在常规实现过程中修改它们
- curator 分支负责最终更新
- 一旦项目状态变化，中英文文件必须保持同步
- `Current Next Action` 必须始终唯一

## 进入 `main` 的门槛

只有同时满足以下条件，变更才应该进入 `main`：

1. 工作位于命名分支上
2. `make eval` 通过
3. canonical state docs 已反映最新事实
4. worker 输出之间没有遗留未解决冲突
5. 如果声称完成了 live verification，则 `reports/` 中必须存在归档后的验证工件

当所有门槛都满足时，推荐的 automation 行为是：

1. 将已验收的 curator 分支合入 `main`
2. 确认 `main` 上的 `make eval` 仍然通过
3. 删除已合入的 curator 分支
4. 移除该分支对应的专属 worktree

## 故障恢复流程

如果 automation 把工作留在不安全状态：

1. 先从对应 worktree 建立救援分支
2. 判断该分支属于以下哪类：
   - 可以进入 curator 整理
   - 只适合当 patch 来源
   - 已经过时，可以丢弃
3. 不要把救援分支直接合入 `main`
4. 通过 curator 流程把可接受内容整合进来
5. 如果还有后续工作，在 `docs/LATEST-HANDOFF.md` 和 `docs/TASK-BOARD.md` 里记录

## 未来 Automation Prompt 的必备内容

automation prompt 应明确写出：

- 编辑前先创建或切换到命名分支
- 不要修改 `main`
- worker 不得更新 canonical state docs
- 一次运行只推进一个子任务
- 在声明可交付前先跑 `make eval`
- 遇到真实阻塞时停止，不要顺手扩 scope

## GroundedDeck 当前策略

- strongest-demo 的实现工作归 worker 分支负责
- 已恢复的 strongest-demo 候选工作已经通过 curator 流程整合成 `main` 上的规范工件包
- 接下来 curator 和 verifier 流程应聚焦于针对 `fixtures/source-packs/strongest-demo-source-pack.json` 的第一次成功 online verification
- 未来如果 curator 或 verifier 分支满足合并门槛，应自动合入 `main`，并清理自己的分支与 worktree
