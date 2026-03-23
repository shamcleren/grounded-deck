# AGENTS

This repository is designed for long-running AI-driven development. Do not depend on chat history as the source of truth. The repository itself is the durable memory.

## Required Read Order

Before making changes, read these files in order:

1. [README.md](README.md)
2. [docs/PROJECT-STATE.md](docs/PROJECT-STATE.md)
3. [docs/ARCHITECTURE-DECISIONS.md](docs/ARCHITECTURE-DECISIONS.md)
4. [docs/architecture.md](docs/architecture.md)
5. [docs/evaluation-plan.md](docs/evaluation-plan.md)

## Operating Contract

- Treat repository docs as canonical memory.
- Do not rely on prior conversation state when repo docs disagree.
- Do not change architecture boundaries without updating [docs/ARCHITECTURE-DECISIONS.md](docs/ARCHITECTURE-DECISIONS.md).
- Do not finish a task without updating [docs/PROJECT-STATE.md](docs/PROJECT-STATE.md) when project state changed.
- Keep the current next action explicit and singular.
- Preserve the `slide spec` intermediate representation as the stable contract between planning, rendering, and grading.
- Run `make eval` before considering a task complete.

## Anti-Drift Rules

- No direct “one giant prompt” architecture.
- No renderer-owned content understanding.
- No final artifact generation without auditable intermediate state.
- No silent removal of coverage, grounding, or editability requirements.
- No scope expansion without recording the decision and why it was accepted.

## Completion Protocol

When finishing meaningful work:

1. update docs that changed the canonical project memory
2. update current status and next step
3. run `make eval`
4. leave the repository in a state where a future agent can continue from repo context alone
