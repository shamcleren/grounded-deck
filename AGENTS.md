# AGENTS

This repository is designed for long-running AI-driven development. Do not depend on chat history as the source of truth. The repository itself is the durable memory.

## Required Read Order

Before making changes, read these files in order:

1. [START-HERE.md](START-HERE.md)
2. [README.md](README.md)
3. [docs/PROJECT-STATE.md](docs/PROJECT-STATE.md)
4. [docs/LATEST-HANDOFF.md](docs/LATEST-HANDOFF.md)
5. [docs/ARCHITECTURE-DECISIONS.md](docs/ARCHITECTURE-DECISIONS.md)
6. [docs/architecture.md](docs/architecture.md)
7. [docs/evaluation-plan.md](docs/evaluation-plan.md)

## Operating Contract

- Treat repository docs as canonical memory.
- Do not rely on prior conversation state when repo docs disagree.
- Use [docs/LATEST-HANDOFF.md](docs/LATEST-HANDOFF.md) as the first session-to-session resume artifact.
- Do not change architecture boundaries without updating [docs/ARCHITECTURE-DECISIONS.md](docs/ARCHITECTURE-DECISIONS.md).
- Do not finish a task without updating [docs/PROJECT-STATE.md](docs/PROJECT-STATE.md) when project state changed.
- Do not leave an in-progress task without updating [docs/LATEST-HANDOFF.md](docs/LATEST-HANDOFF.md) and [docs/TASK-BOARD.md](docs/TASK-BOARD.md).
- Keep the current next action explicit and singular.
- Preserve the `slide spec` intermediate representation as the stable contract between planning, rendering, and grading.
- Run `make eval` before considering a task complete.
- When modifying a document that has a `.zh-CN.md` bilingual counterpart, update both the English and Chinese versions in the same change set to keep them in sync.

## Anti-Drift Rules

- No direct "one giant prompt" architecture.
- No renderer-owned content understanding.
- No final artifact generation without auditable intermediate state.
- No silent removal of coverage, grounding, or editability requirements.
- No scope expansion without recording the decision and why it was accepted.

## Completion Protocol

When finishing meaningful work:

1. update docs that changed the canonical project memory
2. update current status and next step
3. update handoff and task board files
4. run `make eval`
5. leave the repository in a state where a future agent can continue from repo context alone
