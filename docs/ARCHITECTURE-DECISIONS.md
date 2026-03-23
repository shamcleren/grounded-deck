# Architecture Decisions

## Fixed Invariants

These decisions should not drift silently:

1. GroundedDeck is a source-grounded presentation system, not a generic prompt-only PPT generator.
2. `slide spec` is the stable contract between planning, rendering, and grading.
3. The renderer must not own source understanding.
4. Editability is a required product property, not an optional enhancement.
5. Chinese rendering quality is a required product property, not a polish pass.
6. Harness engineering is part of the product architecture, not a sidecar test layer.

## Decision Log

### AD-0001: Repository-as-memory

- Status: accepted
- Why: AI-driven development will span many sessions, so project continuity must live in the repository rather than chat history.
- Consequence: `AGENTS.md`, `docs/PROJECT-STATE.md`, and this file become canonical context for future sessions.

### AD-0002: Intermediate representation first

- Status: accepted
- Why: direct slide generation causes dropped content, poor editability, and weak auditability.
- Consequence: all meaningful generation should converge on `slide spec` before rendering.

### AD-0003: Anti-drift quality gates

- Status: accepted
- Why: long-running AI implementation tends to drift toward convenience unless guarded by explicit checks.
- Consequence: harness rules must evolve alongside architecture and must block missing continuity artifacts.

## Change Policy

If a future change alters a fixed invariant or changes the module split, record a new decision entry in this file and update [docs/PROJECT-STATE.md](PROJECT-STATE.md).
