# Project State

[English](PROJECT-STATE.md) | [简体中文](PROJECT-STATE.zh-CN.md)

## North Star

Build a local-first, source-grounded presentation system that produces NotebookLM-style deck quality with editable PPTX output, stronger Chinese support, and explicit self-acceptance.

## Current Phase

Foundation complete. The repository has:

- product and architecture definitions
- open-source repository docs
- a deterministic self-acceptance harness
- a stable `slide spec` schema
- a repository-as-memory continuity contract for future AI sessions

## Completed So Far

- named the project `GroundedDeck`
- published the public repository scaffold
- defined the architecture split between ingest, planner, visual, renderer, and quality
- defined initial eval-driven project rules
- added open-source community files and templates
- added AI continuity, anti-drift, and project-state artifacts
- added startup, handoff, and task-board artifacts for session continuation

## Current Next Action

Implement the first real pipeline slice: `ingest -> normalized source units -> slide spec draft -> quality checks`.

## Immediate Priorities

1. define the normalized source-unit format
2. add example input and example `slide spec` fixture
3. add schema validation and fixture grading to the harness

## Active Constraints

- local-first design
- editable output remains a hard requirement
- Chinese rendering quality is a first-class requirement
- architecture must remain source-grounded and auditable
- repository docs must stay sufficient for AI continuation

## Definition of Done for Phase One

- a source pack can be ingested into normalized units
- a planner can emit a schema-valid `slide spec`
- the harness can grade fixtures and fail on regressions
- project docs explain the current state and next action without relying on chat history

## Update Rule

If the active phase, next action, constraints, or current target changes, update this file in the same change set.
