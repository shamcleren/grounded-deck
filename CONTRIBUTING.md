# Contributing

[English](CONTRIBUTING.md) | [简体中文](CONTRIBUTING.zh-CN.md)

## Before You Start

- read [README.md](README.md)
- read [docs/architecture.md](docs/architecture.md)
- run `make eval` before submitting changes

## Contribution Rules

- keep module ownership clear across `src/ingest`, `src/planner`, `src/visual`, `src/renderer`, and `src/quality`
- preserve the `slide spec` schema unless the change is deliberate and documented
- update docs when changing architecture, evals, or project goals
- prefer deterministic checks over subjective review when adding new quality gates

## Pull Request Checklist

- `make eval` passes locally
- docs were updated if behavior or scope changed
- new fields in schemas are explained
- regressions are covered by new or updated evals

## Discussions

Use issues for bugs and feature proposals. Use pull requests for concrete code or doc changes.
