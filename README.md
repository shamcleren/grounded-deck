# GroundedDeck

[English](README.md) | [简体中文](README.zh-CN.md)

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
- normalized source-unit schema
- deterministic self-acceptance harness
- open-source repository documents
- a deterministic fixture-backed `ingest -> normalized source units -> slide spec -> quality checks` baseline

The current codebase now includes:

- a provider abstraction for planner and quality modules, with a deterministic provider acting as the regression baseline
- a canonical strongest-demo fixture bundle with explicit coverage, grounding, and visual-form metrics
- a `make strongest-demo` path that regenerates the strongest-demo artifact bundle locally
- an archived successful strongest-demo online verification under `reports/live-verification-latest.{json,md}`

The next milestone is to use that verified strongest-demo live path as the baseline for provider-backed planning improvements before adding a full renderer.

## AI Continuity

This repository is built to survive long-running AI-driven development across many sessions.

- repository docs are the canonical memory
- future agents should resume from repo state, not chat context
- architecture changes must be recorded, not implied
- project status and the single next action must remain explicit

Read [START-HERE.md](START-HERE.md), [AGENTS.md](AGENTS.md), [docs/PROJECT-STATE.md](docs/PROJECT-STATE.md), [docs/LATEST-HANDOFF.md](docs/LATEST-HANDOFF.md), and [docs/ARCHITECTURE-DECISIONS.md](docs/ARCHITECTURE-DECISIONS.md) before continuing implementation work.

Provider configuration notes live in [docs/runtime-config.md](docs/runtime-config.md).
The repository includes [.env.runtime.example](.env.runtime.example) for live-provider setup.
If present, `.env.runtime.local` is auto-loaded by the runtime verification commands.
`make init-live-env` only creates the template file; placeholder values still need to be replaced before `make verify-online` can succeed.

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
├── START-HERE.md             # Quick startup entrypoint for new sessions
├── AGENTS.md                 # AI continuation contract
├── .github/                  # GitHub community files and templates
├── docs/                     # Product, architecture, and evaluation docs
├── harness/                  # Deterministic self-acceptance harness
├── reports/                  # Generated self-acceptance reports
├── schemas/                  # Structured intermediate representations
└── src/                      # Future implementation modules
```

## Core Modules

- `src/ingest`: source parsing, chunking, and source binding
- `src/llm`: provider abstraction and runtime model configuration
- `src/planner`: deck narrative planning and outline generation
- `src/visual`: visual form selection and diagram planning
- `src/renderer`: editable `slide spec -> pptx` rendering
- `src/quality`: coverage, grounding, repetition, and coherence checks

## Self-Acceptance

This repository uses harness engineering from day one.

Current checks verify:

- required project directories exist
- key docs define goals, constraints, and evaluation strategy
- AI continuity docs define current state and anti-drift rules
- a startup and handoff path exists for future sessions
- the `slide spec` schema contains grounding and coverage fields
- eval definitions include both capability and regression checks
- a standard markdown report is generated locally

Run the local harness:

```bash
make eval
```

Run the example deterministic pipeline:

```bash
make example-pipeline
```

Run the opt-in online verification path:

```bash
make init-live-env
make prepare-live-verification
make check-live-env
make live-status
make verify-online
```

This command is not part of `make eval`; it is only for explicit live-provider checks.

Read the latest report:

```bash
make report
```

Latest report path:
[reports/self-acceptance-latest.md](reports/self-acceptance-latest.md)

## Roadmap

1. Preserve deterministic regression coverage while expanding provider-backed planning from the verified strongest-demo baseline.
2. Introduce editable PPTX rendering with Chinese-safe defaults.
3. Add artifact-level grading for layout type selection and output editability.

See [docs/ROADMAP.md](docs/ROADMAP.md) for the current plan.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md), and [SECURITY.md](SECURITY.md).

## License

MIT. See [LICENSE](LICENSE).
