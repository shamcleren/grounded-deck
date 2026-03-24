# Automation Governance

[English](AUTOMATION-GOVERNANCE.md) | [简体中文](AUTOMATION-GOVERNANCE.zh-CN.md)

This document defines how scheduled or unattended AI work must operate in GroundedDeck.

## Why This Exists

GroundedDeck already uses repository docs as durable memory. Scheduled runs add a second risk: multiple worktrees can drift, overlap, or leave anonymous changes that never become canonical repository state.

The goal is to keep automation useful without letting it corrupt `main`, duplicate state updates, or orphan meaningful work in detached worktrees.

## Fixed Rules

1. No automation run may work directly on `main`.
2. No automation run may stay on `detached HEAD` after it starts making changes.
3. Worker automations must not update canonical state docs:
   - `docs/PROJECT-STATE.md`
   - `docs/LATEST-HANDOFF.md`
   - `docs/TASK-BOARD.md`
4. Only a curator flow may update canonical state docs and prepare changes for `main`.
5. Live verification must be treated as a separate responsibility with explicit archived artifacts.
6. A change is not considered repository memory until it lands in tracked files inside this repository.

## Automation Roles

### 1. Worker

Use worker automations for bounded implementation tasks such as:

- strongest demo fixtures and artifacts
- planner or quality code
- tests
- reports or generated demo bundles

Worker rules:

- start from an isolated worktree
- create or switch to a named branch before editing
- do one coherent subtask at a time
- avoid canonical state docs
- leave either a clean atomic commit or a clearly resumable worktree state

### 2. Curator

Use the curator flow to turn worker output into canonical repository state.

Curator responsibilities:

- review candidate worker branches
- choose one integration baseline
- cherry-pick or manually port non-overlapping changes from other worker branches
- resolve conflicts
- update canonical state docs
- run `make eval`
- prepare the branch that is eligible to merge into `main`
- when all merge gates pass, fast-forward or otherwise intentionally merge the accepted curator branch into `main`
- after a successful merge, clean up the merged curator branch and its dedicated worktree

The curator is the only automation role that should routinely edit:

- `docs/PROJECT-STATE.md`
- `docs/LATEST-HANDOFF.md`
- `docs/TASK-BOARD.md`

### 3. Verifier

Use verifier automation only for live verification.

Verifier responsibilities:

- run `make check-live-env`
- run `make live-status`
- run `make verify-online`
- run `make archive-online-verification`
- confirm `reports/live-verification-latest.json` and `reports/live-verification-latest.md` exist

Verifier runs must not silently substitute deterministic output for online verification.

## Branch And Worktree Rules

- Every automation worktree must be attached to a named branch.
- Branch names should communicate ownership and topic.
- Prefer prefixes like:
  - `auto/<automation-id>/<topic>` for workers
  - `curator/<topic>` for integration branches
  - `verify/<topic>` for live verification
- If the local Git storage format blocks slash-delimited names, use a flat fallback such as `auto-<automation-id>-<topic>`.
- Detached worktrees are considered an incident and must be recovered onto a named branch before further work continues.

## Canonical State Ownership

The repository has three canonical state files:

- `docs/PROJECT-STATE.md`
- `docs/LATEST-HANDOFF.md`
- `docs/TASK-BOARD.md`

Rules:

- worker branches may read them but should not update them as part of routine implementation
- curator branches own final updates to them
- when project state changes, English and Chinese files must stay in sync
- `Current Next Action` must remain singular

## Merge Gates For `main`

Nothing should land on `main` until all of the following are true:

1. the work is on a named branch
2. `make eval` passes
3. canonical state docs reflect the new truth
4. no unresolved conflict remains between worker outputs
5. if live verification is part of the claimed result, the archived verification artifacts exist in `reports/`

When all gates pass, the preferred automation behavior is:

1. merge the accepted curator branch into `main`
2. verify `main` still passes `make eval`
3. delete the merged curator branch
4. remove the merged branch's dedicated worktree

## Recovery Procedure

If automation leaves work in an unsafe state:

1. create a rescue branch from the affected worktree
2. inspect whether the branch is:
   - ready to curate
   - useful only as a patch source
   - obsolete and safe to discard
3. do not merge rescue branches directly into `main`
4. move the accepted content through the curator flow
5. record the state in `docs/LATEST-HANDOFF.md` and `docs/TASK-BOARD.md` if follow-up work remains

## Prompt Requirements For Future Automations

Automation prompts should explicitly say:

- create or switch to a named branch before editing
- do not edit `main`
- workers must not update canonical state docs
- only one subtask should be advanced in one run
- run `make eval` before declaring a branch ready
- stop when a real blocker is reached instead of broadening scope

## Current Policy For GroundedDeck

- strongest-demo implementation work belongs on worker branches
- the rescued strongest-demo candidate work has been curated into the canonical bundle on `main`
- the curator and verifier flow should now focus on the first successful online verification against `fixtures/source-packs/strongest-demo-source-pack.json`
- once a future curator or verifier branch meets the merge gates, it should merge into `main` and clean up its own branch and worktree automatically
