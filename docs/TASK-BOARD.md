# Task Board

[English](TASK-BOARD.md) | [简体中文](TASK-BOARD.zh-CN.md)

## In Progress

- none

## Ready Next

- define one strongest end-to-end planning demo case
- write explicit success metrics for coverage, grounding, and visual-form accuracy
- replace placeholder values in `.env.runtime.local` and run the first successful `make verify-online`
- capture one successful live verification transcript or artifact shape
- store the first successful `verification-summary.json` artifact shape in repo memory
- keep canonical docs bilingual via separate language files and switch links

## Later

- replace deterministic planner heuristics with provider-backed planning
- add model-assisted narrative and visual-form grading
- add a public comparison case against generic AI PPT tools after the strongest demo exists
- defer renderer implementation until the planning contract is stable

## Blockers

- real provider credentials and reachable backend not yet configured for `make verify-online`

## Update Rule

When a task begins, move it to `In Progress`.
When it finishes or becomes obsolete, update this file in the same change set.
