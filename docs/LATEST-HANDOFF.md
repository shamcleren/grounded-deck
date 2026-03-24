# Latest Handoff

[English](LATEST-HANDOFF.md) | [简体中文](LATEST-HANDOFF.zh-CN.md)

## Session Summary

GroundedDeck now drives strongest-demo provider guardrails directly from the archived acceptance snapshot, and this curator pass verified that the refreshed live run still matches the accepted strongest-demo structure after tightening the prompt to require explicit empty evidence arrays on summary slides.

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
- updated `make archive-online-verification` so archived live summaries now point to repository-owned copies under `reports/live-verification-history/`
- captured the refreshed strongest-demo live artifacts and a structural acceptance summary under `reports/live-verification-history/strongest-demo-1774362852/`
- added deterministic tests that verify the archived strongest-demo acceptance summary still matches the committed live slide spec and quality report
- integrated the accepted worker patch from `auto/groundeddeck-auto-sprint-b/provider-planning-acceptance-alignment`
- encoded the archived strongest-demo acceptance summary directly into the OpenAI-compatible provider planner/grader prompts and mocked transport tests
- re-ran `make eval`, `make check-live-env`, `make live-status`, `make verify-online`, and `make archive-online-verification` after the acceptance-alignment patch
- refreshed `reports/live-verification-latest.{json,md}` again and archived a matching strongest-demo live snapshot under `reports/live-verification-history/strongest-demo-1774366441/`
- confirmed `reports/live-verification-history/strongest-demo-1774366441/acceptance-summary.json` matches the prior accepted strongest-demo baseline structurally
- recovered this automation worktree from detached `HEAD` onto `curator/groundeddeck-auto-sprint-2b-curator-20260324` before doing curator review work
- reviewed the remaining local worker prompt-variant branches and confirmed they are alternative prompt shapes without a newer archived verification result beyond the accepted acceptance-aligned strongest-demo baseline
- recovered this automation worktree from detached `HEAD` onto `curator/groundeddeck-auto-sprint-2-20260325`
- integrated the accepted worker direction from `auto/groundeddeck-auto-sprint-b/acceptance-comparison-guardrail` into a curator-owned patch that loads strongest-demo planner and grader guardrails from `reports/live-verification-history/strongest-demo-1774366441/acceptance-summary.json`
- tightened strongest-demo prompt wording so summary slides must set `source_bindings` and `must_include_checks` to explicit empty arrays instead of omitting them
- updated prompt regression tests and the archived-acceptance verification test to point at the current accepted strongest-demo snapshot
- re-ran `python3 -m pytest tests/test_pipeline.py tests/test_verification_artifacts.py` and `make eval`, both of which pass on the current curator branch
- linked `.env.runtime.local` from the canonical repo into this worktree, then re-ran `make check-live-env`, `make live-status`, `make verify-online`, and `make archive-online-verification`
- fixed a live regression where the provider omitted required evidence fields on the intro slide by making the strongest-demo summary-slide array requirements explicit
- refreshed `reports/live-verification-latest.{json,md}` and archived a passing strongest-demo live snapshot under `reports/live-verification-history/strongest-demo-1774370225/`
- confirmed the new `strongest-demo-1774370225` acceptance summary matches the accepted strongest-demo baseline structurally aside from the run timestamp

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
- strongest-demo acceptance-aligned provider prompt guardrails: integrated on the current curator branch
- self-acceptance after prompt tightening: passing
- strongest-demo online verification after prompt tightening: passing and re-archived
- live verification archive now preserves repo-local copies of the verified artifacts instead of `/tmp` paths
- refreshed strongest-demo live acceptance snapshot: committed under `reports/live-verification-history/strongest-demo-1774362852/`
- refreshed strongest-demo live acceptance snapshot after acceptance alignment: present under `reports/live-verification-history/strongest-demo-1774366441/`
- strongest-demo prompt guardrails now load their baseline from the archived acceptance summary instead of duplicating constants in code
- strongest-demo summary-slide prompt rules now require explicit empty evidence arrays, which restored live provider compliance with the slide-spec validator
- refreshed strongest-demo live acceptance snapshot after the acceptance-summary-driven guardrail patch: present under `reports/live-verification-history/strongest-demo-1774370225/`
- latest archived strongest-demo live refresh remains structurally aligned with the accepted baseline; only the run timestamp changed
- latest archived strongest-demo acceptance snapshot remains structurally identical to the previously accepted baseline
- remaining worker prompt variants: reviewed and currently superseded by the accepted strongest-demo live baseline, so no new verified worker output is pending integration
- renderer implementation: still deferred

## Immediate Next Action

Use the archived strongest-demo live acceptance snapshot to compare future live refreshes before promoting more provider-backed planning changes.

## First Concrete Tasks

1. treat `reports/live-verification-latest.json` and `reports/live-verification-latest.md` as rolling pointers to the latest archived live snapshot
2. compare future strongest-demo online refreshes against `reports/live-verification-history/strongest-demo-1774366441/acceptance-summary.json`
3. keep `make verify-online` passing on the real provider path while preserving `make eval`
4. wait for a new verified worker patch or a live refresh delta before promoting another provider prompt change

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
