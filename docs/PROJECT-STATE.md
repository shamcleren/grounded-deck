# Project State

[English](PROJECT-STATE.md) | [简体中文](PROJECT-STATE.zh-CN.md)

## North Star

Build a local-first, source-grounded presentation system that produces NotebookLM-style deck quality with editable PPTX output, stronger Chinese support, and explicit self-acceptance.

## Current Phase

Foundation complete. A deterministic baseline pipeline and provider abstraction are now in place. The repository has:

- product and architecture definitions
- open-source repository docs
- a deterministic self-acceptance harness
- a stable `slide spec` schema
- a normalized source-unit schema
- fixture-backed ingest, planning, and quality checks
- a pluggable provider interface for planner and quality modules
- a repository-as-memory continuity contract for future AI sessions

The strongest deterministic planning demo is now curated back onto `main` as a canonical fixture bundle and report path, and the first successful live verification against that canonical strongest-demo input has been archived.

## Completed So Far

- named the project `GroundedDeck`
- published the public repository scaffold
- defined the architecture split between ingest, planner, visual, renderer, and quality
- defined initial eval-driven project rules
- added open-source community files and templates
- added AI continuity, anti-drift, and project-state artifacts
- added startup, handoff, and task-board artifacts for session continuation
- implemented a deterministic `source pack -> normalized source units -> slide spec draft -> quality checks` baseline
- added fixture-backed pipeline tests and harness validation
- introduced a provider abstraction with a deterministic provider baseline
- added a runtime pipeline entrypoint for fixture-backed execution
- wired an OpenAI-compatible provider path with strict local response validation and mocked transport tests
- defined repository automation governance for worker, curator, and verifier flows
- recovered detached automation worktrees onto named rescue branches so their changes are trackable
- curated the rescued strongest-demo work into one canonical strongest-demo fixture bundle, report path, and deterministic metric baseline
- captured and archived the first successful online verification run against the canonical strongest-demo input with MiniMax-M2.7
- hardened the OpenAI-compatible provider path for MiniMax by splitting reasoning output and tolerating `<think>`-wrapped JSON responses
- integrated the accepted worker patch that tightens provider planner and grader prompts around the strongest-demo baseline
- integrated the accepted worker patch from `auto/groundeddeck-auto-sprint-b/provider-planning-acceptance-alignment` so provider prompts and mocked transport tests encode the archived strongest-demo acceptance summary
- restored the `src/visual` and `src/renderer` package scaffolds so `make eval` remains green on the current repository tree
- refreshed strongest-demo online verification for the tightened prompt baseline and re-archived a passing live result
- promoted the refreshed strongest-demo live run into a repository-owned history snapshot with a structural acceptance summary
- refreshed strongest-demo online verification after the acceptance-alignment patch and archived a matching live snapshot under `reports/live-verification-history/strongest-demo-1774366441/`
- replaced duplicated strongest-demo prompt constants with acceptance-summary-driven prompt guardrails loaded from the archived live snapshot
- tightened strongest-demo prompt rules so summary slides must emit explicit empty evidence arrays instead of omitting required fields
- refreshed strongest-demo online verification after the acceptance-summary-driven guardrail patch and archived a structurally matching live snapshot under `reports/live-verification-history/strongest-demo-1774370225/`
- repointed the strongest-demo provider guardrail baseline and deterministic tests to the accepted repository-owned snapshot `reports/live-verification-history/strongest-demo-1774370225/`
- refreshed strongest-demo online verification after the baseline-pointer alignment and archived another structurally matching live snapshot under `reports/live-verification-history/strongest-demo-1774374429/`
- integrated the accepted worker patch from `auto/groundeddeck-auto-sprint-b/grading-acceptance-delta-check` so strongest-demo acceptance-summary comparisons are explicit in code and tests while tolerating only `generated_at_unix`
- refreshed strongest-demo online verification after the acceptance-delta comparison patch and archived another structurally matching live snapshot under `reports/live-verification-history/strongest-demo-1774381550/`
- extracted the visual form selector from `DeterministicProvider` into a standalone `src/visual/selector.py` module with `infer_layout_type`, `build_visual_elements`, and `select_visual_form` as public APIs
- updated `DeterministicProvider` to delegate to `src/visual/selector.py` while preserving full behavioral compatibility with all existing deterministic fixtures
- added `LayoutSelection` data class that tracks matched signals and confidence level for each layout inference
- added 22 unit tests in `tests/test_visual_selector.py` covering rule inference, visual element building, and strongest-demo regression consistency
- confirmed all 75 tests pass and `make eval` remains 34/34 green
- added `validate_model_layouts` function and `LayoutValidationReport` data class to `src/visual/selector.py` for comparing model-generated layouts against rule-based expectations
- wired visual selector into `OpenAICompatibleProvider.draft_slide_spec` as post-validation: model output now carries `_layout_validation` metadata with match/mismatch counts and per-unit details
- wired visual selector into `OpenAICompatibleProvider.grade_slide_spec`: grader prompt now receives a `layout_validation_hint` from the rule engine as a grading signal
- updated `build_grader_user_prompt` to accept optional `layout_validation_hint` keyword argument
- added 9 new tests in `LayoutValidationTests` covering match/mismatch detection, missing slides, multi-unit slides, grader hint generation, and strongest-demo regression
- confirmed all 84 tests pass and `make eval` remains 34/34 green
- added `model_assisted_infer_layout_type` function in `src/visual/selector.py` that accepts an optional `ModelLayoutCallback` for provider-backed layout inference with automatic rule-based fallback
- added `ModelLayoutCallback` type alias and `ALL_CONTENT_LAYOUTS` tuple as public API in `src/visual/selector.py`
- updated `select_visual_form` to accept optional `layout_callback` keyword argument, routing through model-assisted inference when callback is provided
- added `build_layout_callback` method on `OpenAICompatibleProvider` that creates a callback sending single-unit layout queries to the LLM
- added `_build_layout_system_prompt` and `_build_layout_user_prompt` static methods for layout inference prompts
- added 10 new tests in `ModelAssistedInferenceTests` covering: no-callback fallback, valid model result, model-rule agreement/disagreement, invalid layout fallback, empty string fallback, callback exception handling, select_visual_form callback path, and all content layouts acceptance
- added 4 new tests in `PipelineFixtureTests` covering: build_layout_callback transport, quote stripping, grader prompt hint injection, and no-hint case
- confirmed all 98 tests pass and `make eval` remains 34/34 green
- implemented the PPTX renderer scaffold in `src/renderer/pptx_renderer.py` with `render_slide_spec_to_pptx` entry point
- renderer supports all 7 layout types: cover, summary, timeline, comparison, process, chart, section
- each layout produces styled shapes using python-pptx with professional blue-gray color scheme
- speaker notes and source bindings written to each slide's notes area for auditability
- unsupported layout types gracefully fall back to summary rendering with a warning
- updated `src/renderer/__init__.py` to export `render_slide_spec_to_pptx` and `get_supported_layouts`
- added 29 new tests in `tests/test_pptx_renderer.py` covering: basic rendering, all 7 layout types, strongest-demo fixture regression (6 slides), error handling, file size validation, and example fixture rendering
- confirmed all 127 tests pass and `make eval` remains 34/34 green
- wired PPTX renderer into `src/runtime/pipeline.py` via `render_pptx` keyword argument on `run_pipeline`
- updated `src/runtime/cli.py` with `--render-pptx` CLI argument, defaults to `output.pptx` in the output directory
- updated `src/runtime/demo.py` to automatically render `strongest-demo.pptx` as part of `write_strongest_demo_bundle`
- added `render-demo` Makefile target for end-to-end strongest-demo pipeline + PPTX rendering
- added `*.pptx` to `.gitignore` to keep binary files out of version control
- `make render-demo` successfully produces `reports/strongest-demo/strongest-demo.pptx` (6 slides, 46KB)
- added 8 new pipeline PPTX integration tests in `PipelinePptxIntegrationTests`
- confirmed all 135 tests pass and `make eval` remains 34/34 green
- enriched `build_visual_elements` in `src/visual/selector.py` with source-grounded content extraction:
  - timeline: milestones + event descriptions from text
  - comparison: columns + per-column comparison points from text
  - process: step descriptions + corrected step count from text
  - chart: metrics + contextual labels from text
- added `_extract_comparison_points`, `_extract_process_steps`, `_extract_metric_labels`, `_extract_milestone_events` helper functions
- enriched `DeterministicProvider.build_unit_slide` key_points with `_extract_key_points` method that combines claims + text fragments with normalized deduplication
- updated PPTX renderer to consume enriched visual_elements (events, column_points, step_labels, labels)
- regenerated `fixtures/slide-spec/example-slide-spec.json` and `fixtures/slide-spec/strongest-demo-slide-spec.json`
- added 8 `ContentEnrichmentTests` in `tests/test_visual_selector.py`
- enriched cover slide with source-grounded key_points (audience + core claim + source count) and topic-overview visual element
- enriched summary slide with all-units claim coverage (each claim annotated with [source_binding]) and claim-source-map visual element
- added `_build_cover_key_points`, `_build_cover_visual_elements`, `_build_summary_key_points`, `_build_summary_visual_elements` class methods to DeterministicProvider
- added `narrative_quality` dimension to `DeterministicProvider.grade_slide_spec` quality report (key_points emptiness, source annotations, quality ratio)
- created `src/renderer/artifact_grader.py` with `grade_pptx_artifact` function for PPTX editability, notes coverage, source bindings, and structure validation
- updated PPTX renderer to render topic-overview on cover and claim-source-map fallback on summary
- added 6 ArtifactGradingTests and 7 NarrativeQualityTests
- regenerated both slide-spec fixtures and quality-report fixture
- confirmed all 156 tests pass and `make eval` remains 34/34 green
- wired artifact grader into pipeline, CLI, demo, and eval harness:
  - `run_pipeline` auto-executes `grade_pptx_artifact` when `render_pptx` is provided (controllable via `grade_artifact` param)
  - CLI supports `--grade-artifact`/`--no-grade-artifact` flags; outputs `artifact-grade.json`
  - demo bundle auto-grades artifact and includes Artifact Grade section in report
  - added `make grade-artifact` Makefile target backed by `harness/grade_artifact.py`
  - eval harness now includes `artifact-grading` check (35/35 evals)
  - added 9 PipelineArtifactGradingTests, total 165 passing
  - evaluation-plan.md phase one + phase two marked as complete
- implemented model-based narrative quality grading (evaluation-plan phase three):
  - created `src/quality/narrative_grader.py` with deterministic and model-assisted modes
  - three-dimensional scoring: coherence (key_points quality), grounding (source traceability), visual_fit (layout match)
  - `NarrativeGradeReport` data class with composite scoring, status, and serialization
  - `OpenAICompatibleProvider.build_narrative_callback()` for model-assisted grading via LLM
  - wired narrative grading into pipeline (`grade_narrative_quality` param), CLI, demo, and eval harness
  - demo report includes Narrative Grade section with avg scores
  - eval harness now includes `narrative-grading` check (36/36 evals)
  - added 26 narrative grader tests + 7 pipeline integration tests, total 198 passing
- evaluation-plan phase one + phase two + phase three: all complete
- implemented continuity artifact grading in `src/quality/continuity_grader.py` with `ContinuityGradeReport` data class
- continuity grader checks 6 files across 3 dimensions: structure (existence, required sections), consistency (cross-file next-action alignment), freshness (handoff/task-board content)
- wired continuity grading into eval harness as `continuity-grading` check (37/37 evals)
- added 38 continuity grader tests, total 236 passing
- evaluation-plan continuity grading items: complete
- automated acceptance delta comparison in `src/runtime/verification.py` with `compare_against_accepted_baseline()` and `render_acceptance_delta_report()`
- `ACCEPTED_STRONGEST_DEMO_BASELINE` constant points to the canonical accepted snapshot at `reports/live-verification-history/strongest-demo-1774370225/acceptance-summary.json`
- `archive_verification_summary` now auto-generates `acceptance-delta.json` and `acceptance-delta.md` when archiving
- added `acceptance-baseline` check to eval harness (38/38 evals)
- added `make compare-acceptance` Makefile target for independent baseline comparison
- added 12 acceptance baseline comparison tests, total 248 passing

## Current Next Action

Continue improving provider-backed planning and grading against the strongest-demo path without weakening deterministic coverage.

## Immediate Priorities

1. ~~grade continuity artifacts so future agents can safely resume from repository state alone~~ ✅
2. ~~grade handoff completeness and task-board freshness~~ ✅
3. preserve the repository-owned strongest-demo live acceptance snapshot while keeping `reports/live-verification-latest.*` as the rolling pointer
4. compare future strongest-demo live refreshes against the archived acceptance summary instead of treating every passing run as interchangeable
5. keep provider-backed planning improvements, acceptance-aligned prompt guardrails, and `make verify-online` healthy without weakening deterministic regression coverage

External feedback has been absorbed as a prioritization change, not an architecture change. The environment-variable configuration contract is documented in `docs/runtime-config.md`, placeholder values are rejected during live preflight, and the strongest-demo live path has now been proven once against a real provider while preserving the deterministic baseline.

## Active Constraints

- local-first design
- editable output remains a hard requirement
- Chinese rendering quality is a first-class requirement
- architecture must remain source-grounded and auditable
- repository docs must stay sufficient for AI continuation
- feedback may change priorities and demo strategy, but must not silently change architecture boundaries

## Definition of Done for Phase One

- a source pack can be ingested into normalized units
- a planner can emit a schema-valid `slide spec`
- the harness can grade fixtures and fail on regressions
- project docs explain the current state and next action without relying on chat history

## Update Rule

If the active phase, next action, constraints, or current target changes, update this file in the same change set.
