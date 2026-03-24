# Project State

[English](PROJECT-STATE.md) | [简体中文](PROJECT-STATE.zh-CN.md)

## North Star

Build a local-first, source-grounded presentation system that produces NotebookLM-style deck quality with editable PPTX output, stronger Chinese support, and explicit self-acceptance.

## Current Phase

Foundation complete. A deterministic baseline pipeline and provider abstraction are now in place. The repository has:

- product and architecture definitions
- open-source repository docs
- a deterministic self-acceptance harness
- a stable `slide spec` schema
- a normalized source-unit schema
- fixture-backed ingest, planning, and quality checks
- a pluggable provider interface for planner and quality modules
- a repository-as-memory continuity contract for future AI sessions

The strongest deterministic planning demo is now curated back onto `main` as a canonical fixture bundle and report path, and the first successful live verification against that canonical strongest-demo input has been archived.

## Completed So Far

- named the project `GroundedDeck`
- published the public repository scaffold
- defined the architecture split between ingest, planner, visual, renderer, and quality
- defined initial eval-driven project rules
- added open-source community files and templates
- added AI continuity, anti-drift, and project-state artifacts
- added startup, handoff, and task-board artifacts for session continuation
- implemented a deterministic `source pack -> normalized source units -> slide spec draft -> quality checks` baseline
- added fixture-backed pipeline tests and harness validation
- introduced a provider abstraction with a deterministic provider baseline
- added a runtime pipeline entrypoint for fixture-backed execution
- wired an OpenAI-compatible provider path with strict local response validation and mocked transport tests
- defined repository automation governance for worker, curator, and verifier flows
- recovered detached automation worktrees onto named rescue branches so their changes are trackable
- curated the rescued strongest-demo work into one canonical strongest-demo fixture bundle, report path, and deterministic metric baseline
- captured and archived the first successful online verification run against the canonical strongest-demo input with MiniMax-M2.7
- hardened the OpenAI-compatible provider path for MiniMax by splitting reasoning output and tolerating `<think>`-wrapped JSON responses
- added lock-protected automation support so higher-frequency worker and curator schedules do not overlap unsafely
- integrated the accepted worker patch that tightens provider planner and grader prompts around the strongest-demo baseline
- integrated the accepted worker patch from `auto/groundeddeck-auto-sprint-b/provider-planning-acceptance-alignment` so provider prompts and mocked transport tests encode the archived strongest-demo acceptance summary
- restored the `src/visual` and `src/renderer` package scaffolds so `make eval` remains green on the current repository tree
- refreshed strongest-demo online verification for the tightened prompt baseline and re-archived a passing live result
- promoted the refreshed strongest-demo live run into a repository-owned history snapshot with a structural acceptance summary
- refreshed strongest-demo online verification after the acceptance-alignment patch and archived a matching live snapshot under `reports/live-verification-history/strongest-demo-1774366441/`
- replaced duplicated strongest-demo prompt constants with acceptance-summary-driven prompt guardrails loaded from the archived live snapshot
- tightened strongest-demo prompt rules so summary slides must emit explicit empty evidence arrays instead of omitting required fields
- refreshed strongest-demo online verification after the acceptance-summary-driven guardrail patch and archived a structurally matching live snapshot under `reports/live-verification-history/strongest-demo-1774370225/`
- repointed the strongest-demo provider guardrail baseline and deterministic tests to the accepted repository-owned snapshot `reports/live-verification-history/strongest-demo-1774370225/`
- refreshed strongest-demo online verification after the baseline-pointer alignment and archived another structurally matching live snapshot under `reports/live-verification-history/strongest-demo-1774374429/`
- integrated the accepted worker patch from `auto/groundeddeck-auto-sprint-b/grading-acceptance-delta-check` so strongest-demo acceptance-summary comparisons are explicit in code and tests while tolerating only `generated_at_unix`
- refreshed strongest-demo online verification after the acceptance-delta comparison patch and archived another structurally matching live snapshot under `reports/live-verification-history/strongest-demo-1774381550/`

## Current Next Action

Use the archived strongest-demo live acceptance snapshot to compare future live refreshes before promoting more provider-backed planning changes.

## Immediate Priorities

1. preserve the repository-owned strongest-demo live acceptance snapshot while keeping `reports/live-verification-latest.*` as the rolling pointer
2. compare future strongest-demo live refreshes against the archived acceptance summary instead of treating every passing run as interchangeable
3. keep provider-backed planning improvements, acceptance-aligned prompt guardrails, and `make verify-online` healthy without weakening deterministic regression coverage

External feedback has been absorbed as a prioritization change, not an architecture change. The environment-variable configuration contract is documented in `docs/runtime-config.md`, placeholder values are rejected during live preflight, and the strongest-demo live path has now been proven once against a real provider while preserving the deterministic baseline.

## Active Constraints

- local-first design
- editable output remains a hard requirement
- Chinese rendering quality is a first-class requirement
- architecture must remain source-grounded and auditable
- repository docs must stay sufficient for AI continuation
- feedback may change priorities and demo strategy, but must not silently change architecture boundaries
- scheduled or unattended AI work must land through the automation governance flow instead of writing directly to `main`
- higher-frequency scheduled automation must use the repository role-lock mechanism before substantive work

## Definition of Done for Phase One

- a source pack can be ingested into normalized units
- a planner can emit a schema-valid `slide spec`
- the harness can grade fixtures and fail on regressions
- project docs explain the current state and next action without relying on chat history

## Update Rule

If the active phase, next action, constraints, or current target changes, update this file in the same change set.
