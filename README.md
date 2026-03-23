# GroundedDeck

NotebookLM-style source-grounded PPT generation with editable output, stronger Chinese support, and self-acceptance harnesses.

## Why GroundedDeck

Most AI PPT tools generate slides too early. They skip the hard part:

- understanding source materials
- deciding what story the deck should tell
- choosing the right visual form for each page
- preserving traceability back to the original sources
- keeping the output editable instead of baking everything into images

GroundedDeck is designed as a local-first presentation compiler, not a generic slide filler.

## Target Outcome

GroundedDeck aims to produce decks that feel closer to NotebookLM than to template-driven PPT generators:

- source-grounded planning before slide writing
- narrative compression instead of summary slicing
- automatic visual form selection for timelines, comparisons, flows, hierarchies, and matrices
- editable `.pptx` output using native objects wherever possible
- explicit coverage checks to reduce dropped facts and key claims
- Chinese-friendly typography and rendering constraints

## Project Status

This repository currently contains the foundation scaffold:

- product definition and architecture docs
- `slide spec` schema
- deterministic self-acceptance harness
- open-source repository documents
- implementation module boundaries for future work

The first milestone is to build an end-to-end `ingest -> slide spec -> quality checks` path before adding a full renderer.

## Architecture

```text
Sources
  -> ingest
  -> planner
  -> visual selector
  -> slide spec
  -> renderer
  -> quality harness
  -> report
```

## Repository Layout

```text
.
├── .claude/evals/            # Eval definitions
├── .github/                  # GitHub community files and templates
├── docs/                     # Product, architecture, and evaluation docs
├── harness/                  # Deterministic self-acceptance harness
├── reports/                  # Generated self-acceptance reports
├── schemas/                  # Structured intermediate representations
└── src/                      # Future implementation modules
```

## Core Modules

- `src/ingest`: source parsing, chunking, and source binding
- `src/planner`: deck narrative planning and outline generation
- `src/visual`: visual form selection and diagram planning
- `src/renderer`: editable `slide spec -> pptx` rendering
- `src/quality`: coverage, grounding, repetition, and coherence checks

## Self-Acceptance

This repository uses harness engineering from day one.

Current checks verify:

- required project directories exist
- key docs define goals, constraints, and evaluation strategy
- the `slide spec` schema contains grounding and coverage fields
- eval definitions include both capability and regression checks
- a standard markdown report is generated locally

Run the local harness:

```bash
make eval
```

Read the latest report:

```bash
make report
```

Latest report path:
[reports/self-acceptance-latest.md](/Users/renjinming/code/my_porjects/shamcleren/grounded-deck/reports/self-acceptance-latest.md)

## Roadmap

1. Build a minimal `ingest -> slide spec` pipeline.
2. Add coverage and grounding graders for source completeness.
3. Introduce editable PPTX rendering with Chinese-safe defaults.
4. Add artifact-level grading for layout type selection and output editability.

See [docs/ROADMAP.md](/Users/renjinming/code/my_porjects/shamcleren/grounded-deck/docs/ROADMAP.md) for the current plan.

## Contributing

See [CONTRIBUTING.md](/Users/renjinming/code/my_porjects/shamcleren/grounded-deck/CONTRIBUTING.md), [CODE_OF_CONDUCT.md](/Users/renjinming/code/my_porjects/shamcleren/grounded-deck/CODE_OF_CONDUCT.md), and [SECURITY.md](/Users/renjinming/code/my_porjects/shamcleren/grounded-deck/SECURITY.md).

## License

MIT. See [LICENSE](/Users/renjinming/code/my_porjects/shamcleren/grounded-deck/LICENSE).
