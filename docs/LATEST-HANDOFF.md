# Latest Handoff

[English](LATEST-HANDOFF.md) | [简体中文](LATEST-HANDOFF.zh-CN.md)

## Session Summary

GroundedDeck now carries the accepted provider-prompt tightening patch on a curator branch, keeps `make eval` green on the current tree, and has a freshly re-verified strongest-demo online result archived alongside the earlier accepted live baseline.

## What Was Just Completed

- added [AGENTS.md](../AGENTS.md) as the AI operating contract
- added [docs/PROJECT-STATE.md](PROJECT-STATE.md) as the canonical current-state record
- added [docs/ARCHITECTURE-DECISIONS.md](ARCHITECTURE-DECISIONS.md) to prevent architecture drift
- extended the harness so continuity artifacts are mandatory
- added [START-HERE.md](../START-HERE.md) as the fast startup entrypoint
- reorganized multilingual docs into separate English and Chinese files with switch links
- added a normalized source-unit schema and fixture files
- implemented deterministic ingest, planning, and quality modules
- extended `make eval` to run pipeline fixture tests
- introduced a provider abstraction for planner and quality modules
- added a runtime pipeline entrypoint and example command
- wired an OpenAI-compatible provider path with strict local response validation
- added an opt-in `make verify-online` path that refuses deterministic fallback
- added automatic verification-summary artifacts for runtime executions
- tightened live-env checks so placeholder values such as `REPLACE_ME` are treated as invalid
- absorbed external product feedback by narrowing near-term focus toward a strongest demo and planning-quality proof points without changing architecture boundaries
- added `docs/AUTOMATION-GOVERNANCE.md` and made automation handling part of startup guidance
- recovered four detached automation worktrees onto named rescue branches so they can be curated instead of lost
- accepted the strongest-demo rescue work by landing a canonical strongest-demo fixture bundle, deterministic quality metrics, and `make strongest-demo`
- added `make curator-finalize` so future curator runs use one repository-owned merge-and-cleanup path
- configured the live provider path against MiniMax-M2.7 and archived the first successful strongest-demo online verification under `reports/live-verification-latest.{json,md}`
- hardened the OpenAI-compatible provider integration so MiniMax reasoning output is split cleanly and `<think>`-wrapped JSON responses can still be parsed and diagnosed
- added a repository-owned automation role-lock utility so worker and curator schedules can be safely increased without overlapping substantive work
- integrated the accepted worker patch from `auto/groundeddeck-auto-sprint/provider-planning-prompt-tightening`
- tightened the OpenAI-compatible provider planner and grader prompts around the strongest-demo baseline structure, layout expectations, and grading focus
- restored `src/visual/__init__.py` and `src/renderer/__init__.py` so the current repository tree satisfies the self-acceptance completeness checks
- re-ran `python3 -m pytest tests/test_pipeline.py` and `make eval`, both of which pass on the curator branch
- linked `.env.runtime.local` from the canonical repo into this worktree, then ran `make check-live-env`, `make live-status`, `make verify-online`, and `make archive-online-verification`
- refreshed `reports/live-verification-latest.{json,md}` with a passing strongest-demo online verification for the tightened prompt baseline

## Current Status

- repository continuity contract: present
- startup and handoff path: present
- deterministic harness: passing
- deterministic pipeline baseline: passing
- provider abstraction: present
- OpenAI-compatible provider path: present and locally testable
- live verification tooling: ready and proven
- placeholder env detection: present
- live status correctly reports environment readiness and the last archived result
- live credentials / real backend: configured and verified for MiniMax-M2.7
- strongest-demo canonical bundle: present
- automation governance for worker / curator / verifier flows: present
- automation role locks for higher-frequency schedules: present
- first successful strongest-demo online verification: archived in `reports/live-verification-latest.json` and `reports/live-verification-latest.md`
- near-term focus: expand provider-backed planning from the verified strongest-demo baseline without weakening deterministic evals
- provider prompt tightening for strongest-demo: integrated on the current curator branch
- self-acceptance after prompt tightening: passing
- strongest-demo online verification after prompt tightening: passing and re-archived
- renderer implementation: still deferred

## Immediate Next Action

Decide which parts of the refreshed strongest-demo online output should become future regression fixtures or acceptance checks.

## First Concrete Tasks

1. treat `reports/live-verification-latest.json` and `reports/live-verification-latest.md` as the canonical first live-run memory
2. compare the refreshed strongest-demo online output against the first accepted live baseline instead of treating every new pass as interchangeable
3. keep `make verify-online` passing on the real provider path while preserving `make eval`
4. record any future provider-specific compatibility decisions in repository docs instead of leaving them implicit

## Do Not Drift

- do not start with renderer work
- do not collapse the project into a single prompt pipeline
- do not skip the intermediate `slide spec`
- do not leave state changes undocumented
- do not let worker automations update canonical state docs or write directly to `main`
- do not fall back to the old example fixture for future claims about the strongest-demo live path

## Resume Hint

If a future session gets only one instruction, it should be:

`Continue GroundedDeck from START-HERE.md and follow the current next action.`
