# Evaluation Plan

## Principles

GroundedDeck uses eval-driven development:

- define success before implementation
- prefer deterministic graders whenever possible
- keep local evaluation runnable from a single command
- treat regression checks as first-class project artifacts

## Capability Evals

- the repository defines the product target and architecture boundaries
- the repository defines a structured `slide spec` intermediate representation
- the repository provides local harness and rubric files
- the repository can generate a standard self-acceptance report

## Regression Evals

- key project docs and harness files must remain present after refactors
- schema updates must not silently remove required fields
- eval definitions must keep both capability and regression sections

## Grader Strategy

- phase one: code-based graders for files, schema, and eval definitions
- phase two: artifact graders for PPT editability, source coverage, and font constraints
- phase three: model-based graders for narrative quality and visual selection quality

## Outputs

- standard output summary
- markdown report
- non-zero exit code on failure

## Next Stage

- validate example `slide spec` instances against schema
- grade sample decks for coverage and grounding
- inspect exported PPT artifacts for editable object usage and Chinese font rules
