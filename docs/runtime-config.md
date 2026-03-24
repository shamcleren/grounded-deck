# Runtime Configuration

[English](runtime-config.md) | [简体中文](runtime-config.zh-CN.md)

GroundedDeck now supports a pluggable provider interface for planner and quality modules.

The deterministic provider remains the default regression baseline for local tests and `make eval`.

## Environment Variables

- `GROUNDED_DECK_LLM_PROVIDER`
  Supported values:
  - `deterministic`
  - `openai-compatible`
- `GROUNDED_DECK_LLM_MODEL`
  Model name passed to the selected provider.
- `GROUNDED_DECK_BASE_URL`
  Required for `openai-compatible`.
  Expected form: `https://host/v1`
- `GROUNDED_DECK_API_KEY_ENV`
  Optional.
  Defaults to `GROUNDED_DECK_API_KEY`.
- `GROUNDED_DECK_API_KEY`
  API key for the provider named by `GROUNDED_DECK_API_KEY_ENV`.

## Current Behavior

- `deterministic`:
  used by default, produces fixture-stable output, and is exercised by repository tests.
- `openai-compatible`:
  currently supports configuration loading, request construction, JSON response parsing, and local validation of returned payload shapes.
  Live HTTP calls are wired through the provider transport path, but repository tests use mocked transports rather than real network calls.

## Recommended Setup

For local repository verification:

```bash
unset GROUNDED_DECK_LLM_PROVIDER
make eval
```

For future runtime experimentation with an OpenAI-compatible backend:

```bash
make init-live-env
export GROUNDED_DECK_LLM_PROVIDER=openai-compatible
export GROUNDED_DECK_LLM_MODEL=gpt-4.1-mini
export GROUNDED_DECK_BASE_URL=https://api.openai.com/v1
export GROUNDED_DECK_API_KEY=YOUR_KEY
```

The repository also includes [.env.runtime.example](../.env.runtime.example) as a configuration template.
If `.env.runtime.local` exists, GroundedDeck now auto-loads values from it before reading the live verification commands.

`make init-live-env` creates `.env.runtime.local` from the example file only when it does not already exist.

It does ship a local example runtime entrypoint for the fixture-backed pipeline:

```bash
make example-pipeline
```

This writes:

- `/tmp/grounded-deck-example/normalized-pack.json`
- `/tmp/grounded-deck-example/slide-spec.json`
- `/tmp/grounded-deck-example/quality-report.json`
- `/tmp/grounded-deck-example/verification-summary.json`

For opt-in live verification against a configured non-deterministic provider:

```bash
make prepare-live-verification
make check-live-env
make live-status
make verify-online
```

This command fails fast if `GROUNDED_DECK_LLM_PROVIDER` still resolves to `deterministic`.

`make check-live-env` reports which required values are still missing before you attempt a live run.
`make prepare-live-verification` writes `reports/live-verification-checklist.md`.
`make live-status` shows whether the environment is ready and whether a recent verification summary exists in `/tmp/grounded-deck-online/`.

When it succeeds, it also writes:

- `/tmp/grounded-deck-online/verification-summary.json`

To archive the latest online verification attempt into repository memory:

```bash
make archive-online-verification
```

This writes:

- `reports/live-verification-latest.json`
- `reports/live-verification-latest.md`

To read the archived report:

```bash
make report-live-verification
```

The archived report can represent either a successful run or a failed attempt with an explicit error section.
