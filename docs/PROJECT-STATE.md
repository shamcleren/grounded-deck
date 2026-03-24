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

The strongest deterministic planning demo is now curated back onto `main` as a canonical fixture bundle and report path.

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

## Current Next Action

Capture the first successful online verification run against the canonical strongest-demo input without weakening deterministic regression coverage.

## Immediate Priorities

1. replace placeholder values in `.env.runtime.local` with real provider settings
2. run `make check-live-env`, `make live-status`, `make verify-online`, and `make archive-online-verification`
3. store the first successful online verification artifact in repository memory

External feedback has been absorbed as a prioritization change, not an architecture change. The environment-variable configuration contract is documented in `docs/runtime-config.md`, placeholder values are rejected during live preflight, and the next work is to prove product value with a strongest demo while preserving the deterministic baseline.

## Active Constraints

- local-first design
- editable output remains a hard requirement
- Chinese rendering quality is a first-class requirement
- architecture must remain source-grounded and auditable
- repository docs must stay sufficient for AI continuation
- feedback may change priorities and demo strategy, but must not silently change architecture boundaries
- scheduled or unattended AI work must land through the automation governance flow instead of writing directly to `main`

## Definition of Done for Phase One

- a source pack can be ingested into normalized units
- a planner can emit a schema-valid `slide spec`
- the harness can grade fixtures and fail on regressions
- project docs explain the current state and next action without relying on chat history

## Update Rule

If the active phase, next action, constraints, or current target changes, update this file in the same change set.
