## EVAL DEFINITION: grounded-deck-foundation

### Capability Evals

[CAPABILITY EVAL: repository-foundation]
Task: The repository must define product intent, architecture boundaries, schema, and harness artifacts.
Success Criteria:
  - [ ] `README.md` explains project goal, layout, and self-acceptance entrypoints.
  - [ ] `docs/vision.md` defines quality bar, differentiators, and non-goals.
  - [ ] `docs/architecture.md` defines system layers, data flow, and guardrails.
  - [ ] `schemas/slide-spec.schema.json` exists and is parseable.
Expected Output: A local repository scaffold ready for iterative implementation.

[CAPABILITY EVAL: ai-continuity-contract]
Task: The repository must preserve durable context for future AI sessions.
Success Criteria:
  - [ ] `AGENTS.md` defines the required read order and completion protocol.
  - [ ] `docs/PROJECT-STATE.md` defines current phase and current next action.
  - [ ] `docs/ARCHITECTURE-DECISIONS.md` defines invariants and decision log.
Expected Output: A future AI agent can resume from repository state instead of chat history.

[CAPABILITY EVAL: self-acceptance-harness]
Task: The repository must generate a local self-acceptance report with one command.
Success Criteria:
  - [ ] `make eval` runs successfully.
  - [ ] the harness returns a non-zero exit code on failure.
  - [ ] the harness writes `reports/self-acceptance-latest.md`.
Expected Output: Deterministic local self-acceptance output.

### Regression Evals

[REGRESSION EVAL: eval-definition-integrity]
Baseline: initial-scaffold
Tests:
  - capability-evals-present: PASS/FAIL
  - regression-evals-present: PASS/FAIL
  - report-target-defined: PASS/FAIL
Result: pending

[REGRESSION EVAL: schema-integrity]
Baseline: initial-scaffold
Tests:
  - deck-goal-required: PASS/FAIL
  - audience-required: PASS/FAIL
  - slides-required: PASS/FAIL
  - slide-source-bindings-required: PASS/FAIL
Result: pending

[REGRESSION EVAL: continuity-integrity]
Baseline: initial-scaffold
Tests:
  - agents-read-order-present: PASS/FAIL
  - project-state-next-action-present: PASS/FAIL
  - architecture-decisions-present: PASS/FAIL
Result: pending
