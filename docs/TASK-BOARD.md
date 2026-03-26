# Task Board

[English](TASK-BOARD.md) | [简体中文](TASK-BOARD.zh-CN.md)

## In Progress

- keep strongest-demo provider prompts and live verification aligned to the archived acceptance snapshot before promoting more provider-backed planning changes
- narrative quality post-validation in `OpenAICompatibleProvider.grade_slide_spec` — deterministic narrative grader cross-validates model grading results

## Recently Completed

- added narrative quality post-validation to `OpenAICompatibleProvider.grade_slide_spec`: deterministic narrative grader results attached as `_narrative_validation` metadata for cross-validation of model grading
- completed bilingual documentation for all canonical project docs: created `.zh-CN.md` files for evaluation-plan, TASK-BOARD, PROJECT-STATE, LATEST-HANDOFF, AGENTS, and START-HERE; updated all English source files with `| [简体中文]` language switch links
- automated acceptance delta comparison in `src/runtime/verification.py`
- `compare_against_accepted_baseline()` function compares any candidate acceptance summary against the accepted baseline
- `render_acceptance_delta_report()` renders delta results as Markdown
- `ACCEPTED_STRONGEST_DEMO_BASELINE` constant points to the canonical accepted snapshot
- `archive_verification_summary` now auto-generates `acceptance-delta.json` and `acceptance-delta.md` when archiving
- added `acceptance-baseline` check to eval harness (38/38 evals)
- added `make compare-acceptance` Makefile target for independent baseline comparison
- added 12 acceptance baseline comparison tests, total 248 passing
- implemented continuity artifact grading in `src/quality/continuity_grader.py`
- `ContinuityGradeReport` with structure, consistency, and freshness checks across 6 continuity files
- checks file existence, required sections, section non-emptiness, cross-file next-action alignment, handoff completeness, task-board freshness
- wired continuity grading into eval harness (`continuity-grading` check, 37/37 evals)
- added 38 continuity grader tests, total 236 passing
- evaluation-plan continuity grading items: complete
- implemented model-based narrative quality grading (evaluation-plan phase three)
- created `src/quality/narrative_grader.py` with deterministic and model-assisted modes
- three-dimensional scoring: coherence (key_points quality), grounding (source traceability), visual_fit (layout match)
- `NarrativeGradeReport` data class with composite scoring, status, and serialization
- `OpenAICompatibleProvider.build_narrative_callback()` for model-assisted grading
- wired narrative grading into pipeline (`grade_narrative_quality` param), CLI, demo, and eval harness
- eval harness now includes `narrative-grading` check (36/36 evals)
- added 26 narrative grader tests + 7 pipeline integration tests, total 198 passing
- evaluation-plan phase one + phase two + phase three: all complete
- added `narrative_quality` dimension to `DeterministicProvider.grade_slide_spec` quality report
- created `src/renderer/artifact_grader.py` with `grade_pptx_artifact` for PPTX editability/notes/source-binding validation
- updated PPTX renderer for enriched cover/summary content consumption
- added 6 ArtifactGradingTests + 7 NarrativeQualityTests, total 156 passing
- enriched `build_visual_elements` in `src/visual/selector.py` with source-grounded content extraction (events, column_points, step_labels, labels)
- added `_extract_comparison_points`, `_extract_process_steps`, `_extract_metric_labels`, `_extract_milestone_events` helper functions
- enriched `DeterministicProvider.build_unit_slide` key_points with `_extract_key_points` method
- updated PPTX renderer to consume enriched visual_elements
- regenerated both slide-spec fixtures, 8 new ContentEnrichmentTests
- wired PPTX renderer into `src/runtime/pipeline.py` via `render_pptx` keyword argument on `run_pipeline`
- updated `src/runtime/cli.py` with `--render-pptx` CLI argument
- updated `src/runtime/demo.py` to automatically render `strongest-demo.pptx`
- added `render-demo` Makefile target for end-to-end pipeline + PPTX rendering
- `make render-demo` produces `reports/strongest-demo/strongest-demo.pptx` (6 slides, 46KB)
- 8 new pipeline PPTX integration tests, total 135 passing
- implemented PPTX renderer scaffold in `src/renderer/pptx_renderer.py` with `render_slide_spec_to_pptx` entry point
- renderer supports all 7 layout types: cover, summary, timeline, comparison, process, chart, section
- each layout produces styled shapes with professional blue-gray color scheme, speaker notes, and source binding audit trail
- added `model_assisted_infer_layout_type` function with `ModelLayoutCallback` type and automatic rule-based fallback
- wired `src/visual/selector.py` into `OpenAICompatibleProvider` for post-validation and grading signal injection
- extracted visual form selector from `DeterministicProvider` into standalone `src/visual/selector.py` module

## Ready Next

- continue improving provider-backed planning and grading against the strongest-demo path without weakening deterministic coverage
- compare future strongest-demo live refreshes against `reports/live-verification-history/strongest-demo-1774370225/acceptance-summary.json` before accepting another prompt change
- keep strongest-demo canonical docs pinned to the current accepted repository-owned snapshot until a newer verified snapshot is accepted

## Later

- add a public comparison case against generic AI PPT tools after the strongest demo exists

## Blockers

- none for the current strongest-demo planning baseline

## Update Rule

When a task begins, move it to `In Progress`.
When it finishes or becomes obsolete, update this file in the same change set.
