# Task Board

[English](TASK-BOARD.md) | [简体中文](TASK-BOARD.zh-CN.md)

## In Progress

- keep strongest-demo provider prompts and live verification aligned to the archived acceptance snapshot before promoting more provider-backed planning changes
- use `compare_acceptance_summaries()` against `reports/live-verification-history/strongest-demo-1774370225/acceptance-summary.json` before accepting another strongest-demo live refresh as structurally equivalent

## Ready Next

- continue improving provider-backed planning and grading against the strongest-demo path without weakening deterministic coverage
- compare future strongest-demo live refreshes against `reports/live-verification-history/strongest-demo-1774370225/acceptance-summary.json` before accepting another prompt change
- wait for a new verified worker patch or a strongest-demo live-refresh delta beyond `strongest-demo-1774381550` before promoting another prompt change
- keep strongest-demo canonical docs pinned to the current accepted repository-owned snapshot until a newer verified snapshot is accepted
- keep canonical docs bilingual via separate language files and switch links

## Later

- replace deterministic planner heuristics with provider-backed planning
- add model-assisted narrative and visual-form grading
- add a public comparison case against generic AI PPT tools after the strongest demo exists
- defer renderer implementation until the planning contract is stable

## Blockers

- none for the current strongest-demo planning baseline

## Update Rule

When a task begins, move it to `In Progress`.
When it finishes or becomes obsolete, update this file in the same change set.
