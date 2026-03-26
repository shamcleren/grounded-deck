# Latest Handoff

## Session Summary

GroundedDeck now has three diverse sample datasets (strongest-demo Chinese, saas-launch English, tech-review English) covering all 7 layout types. The visual selector rule engine has been significantly improved with heading-priority timeline boost, tightened comparison rules, and expanded chart keywords. A new automatic section divider feature inserts section pages between different sources when decks have 6+ content slides. The tech-review sample produces 11 slides across 7 distinct layouts.

## What Was Just Completed

- added heading-priority timeline boost in `infer_layout_type`: headings containing `timeline`/`evolution`/`history`/`checkpoint` with year references now override comparison/process signals
- tightened comparison contrast connector rule: single `but`/`while` no longer independently triggers comparison without a comparison keyword
- moved `landscape` keyword to heading-only scope to avoid false positives from body text (e.g. "risk landscape")
- added chart keywords: `latency`, `throughput`, `metric`, `benchmark`, `sla`
- created `fixtures/source-packs/tech-review-source-pack.json` English source pack (cloud platform migration / technical architecture review theme) with 4 sources and 6 sections
- generated full tech-review fixture set: 6 normalized units, 11 slides (7 distinct layouts), quality pass
- tech-review layout distribution: cover, summary, timeline, comparison, section, process, section, chart, section, comparison, timeline — 7 distinct layout types
- implemented automatic section divider insertion in `DeterministicProvider.draft_slide_spec`:
  - `_insert_section_dividers` static method inserts section pages between different sources when content slides >= 6
  - section divider title uses source title, goal uses first claim
  - strongest-demo (4 units) and saas-launch (5 units) are unaffected
- updated quality grader to exempt section layout from ungrounded and empty key_points checks
- updated `total_content_slides` calculation to exclude cover and section layouts
- added `demo-tech` Makefile target and updated `demo-all` to include tech-review
- added 15 new tests in `test_diverse_samples.py`:
  - TechReviewRenderingTests (9): rendering, slide count, 7 distinct layouts, section dividers, all content layouts, heading boost, checkpoint timeline, monolith vs microservices, latency/throughput chart
  - SectionDividerTests (6): no dividers for small packs, no dividers for 5 units, dividers for 6+ units, dividers between sources, quality passes, end-to-end pipeline
- total test count: 309 passing
- eval harness: all passing
- added [AGENTS.md](../AGENTS.md) as the AI operating contract
- added [docs/PROJECT-STATE.md](PROJECT-STATE.md) as the canonical current-state record
- added [docs/ARCHITECTURE-DECISIONS.md](ARCHITECTURE-DECISIONS.md) to prevent architecture drift
- extended the harness so continuity artifacts are mandatory
- added [START-HERE.md](../START-HERE.md) as the fast startup entrypoint
- reorganized multilingual docs into separate English and Chinese files with switch links
- added a normalized source-unit schema and fixture files
- implemented deterministic ingest, planning, and quality modules
- extended `make eval` to run pipeline fixture tests
- introduced a provider abstraction for planner and quality modules
- added a runtime pipeline entrypoint and example command
- wired an OpenAI-compatible provider path with strict local response validation
- added an opt-in `make verify-online` path that refuses deterministic fallback
- added automatic verification-summary artifacts for runtime executions
- tightened live-env checks so placeholder values such as `REPLACE_ME` are treated as invalid
- absorbed external product feedback by narrowing near-term focus toward a strongest demo and planning-quality proof points without changing architecture boundaries
- accepted the strongest-demo rescue work by landing a canonical strongest-demo fixture bundle, deterministic quality metrics, and `make strongest-demo`
- configured the live provider path against MiniMax-M2.7 and archived the first successful strongest-demo online verification under `reports/live-verification-latest.{json,md}`
- hardened the OpenAI-compatible provider integration so MiniMax reasoning output is split cleanly and `<think>`-wrapped JSON responses can still be parsed and diagnosed
- integrated the accepted worker patch from `auto/groundeddeck-auto-sprint/provider-planning-prompt-tightening`
- tightened the OpenAI-compatible provider planner and grader prompts around the strongest-demo baseline structure, layout expectations, and grading focus
- restored `src/visual/__init__.py` and `src/renderer/__init__.py` so the current repository tree satisfies the self-acceptance completeness checks
- re-ran `python3 -m pytest tests/test_pipeline.py` and `make eval`, both of which pass on the curator branch
- linked `.env.runtime.local` from the canonical repo into this worktree, then ran `make check-live-env`, `make live-status`, `make verify-online`, and `make archive-online-verification`
- refreshed `reports/live-verification-latest.{json,md}` with a passing strongest-demo online verification for the tightened prompt baseline
- updated `make archive-online-verification` so archived live summaries now point to repository-owned copies under `reports/live-verification-history/`
- captured the refreshed strongest-demo live artifacts and a structural acceptance summary under `reports/live-verification-history/strongest-demo-1774362852/`
- added deterministic tests that verify the archived strongest-demo acceptance summary still matches the committed live slide spec and quality report
- integrated the accepted worker patch from `auto/groundeddeck-auto-sprint-b/provider-planning-acceptance-alignment`
- encoded the archived strongest-demo acceptance summary directly into the OpenAI-compatible provider planner/grader prompts and mocked transport tests
- re-ran `make eval`, `make check-live-env`, `make live-status`, `make verify-online`, and `make archive-online-verification` after the acceptance-alignment patch
- refreshed `reports/live-verification-latest.{json,md}` again and archived a matching strongest-demo live snapshot under `reports/live-verification-history/strongest-demo-1774366441/`
- confirmed `reports/live-verification-history/strongest-demo-1774366441/acceptance-summary.json` matches the prior accepted strongest-demo baseline structurally
- recovered this automation worktree from detached `HEAD` onto `curator/groundeddeck-auto-sprint-2b-curator-20260324` before doing curator review work
- reviewed the remaining local worker prompt-variant branches and confirmed they are alternative prompt shapes without a newer archived verification result beyond the accepted acceptance-aligned strongest-demo baseline
- recovered this automation worktree from detached `HEAD` onto `curator/groundeddeck-auto-sprint-2-20260325`
- integrated the accepted worker direction from `auto/groundeddeck-auto-sprint-b/acceptance-comparison-guardrail` into a curator-owned patch that loads strongest-demo planner and grader guardrails from `reports/live-verification-history/strongest-demo-1774366441/acceptance-summary.json`
- tightened strongest-demo prompt wording so summary slides must set `source_bindings` and `must_include_checks` to explicit empty arrays instead of omitting them
- updated prompt regression tests and the archived-acceptance verification test to point at the current accepted strongest-demo snapshot
- re-ran `python3 -m pytest tests/test_pipeline.py tests/test_verification_artifacts.py` and `make eval`, both of which pass on the current curator branch
- linked `.env.runtime.local` from the canonical repo into this worktree, then re-ran `make check-live-env`, `make live-status`, `make verify-online`, and `make archive-online-verification`
- fixed a live regression where the provider omitted required evidence fields on the intro slide by making the strongest-demo summary-slide array requirements explicit
- refreshed `reports/live-verification-latest.{json,md}` and archived a passing strongest-demo live snapshot under `reports/live-verification-history/strongest-demo-1774370225/`
- confirmed the new `strongest-demo-1774370225` acceptance summary matches the accepted strongest-demo baseline structurally aside from the run timestamp
- corrected `docs/STRONGEST-DEMO.{md,zh-CN.md}` so canonical strongest-demo references now point to the repository-owned accepted snapshot under `reports/live-verification-history/strongest-demo-1774370225/` instead of an obsolete worktree path
- reviewed `auto/groundeddeck-auto-sprint/provider-grading-prompt-tightening`, `auto/groundeddeck-auto-sprint-b/acceptance-comparison-tightening`, and `auto/groundeddeck-auto-sprint-c/strongest-demo-slide-id-guardrails`, and confirmed they are still unverified prompt variants with no newer archived strongest-demo verification to justify promotion
- repointed the strongest-demo provider guardrail baseline, deterministic tests, and canonical next-step docs from `strongest-demo-1774366441` to the currently accepted repository-owned snapshot `strongest-demo-1774370225`
- linked `.env.runtime.local` from the canonical repo into this worktree, then ran `make check-live-env`, `make live-status`, `make verify-online`, and `make archive-online-verification` for the baseline-pointer alignment change
- observed one failed live refresh under `reports/live-verification-history/strongest-demo-1774374274/`, then re-ran live verification and archived a passing strongest-demo live snapshot under `reports/live-verification-history/strongest-demo-1774374429/`
- confirmed `reports/live-verification-history/strongest-demo-1774374429/acceptance-summary.json` matches the accepted strongest-demo baseline structurally aside from the run timestamp
- reviewed the remaining worker branches again and accepted `auto/groundeddeck-auto-sprint-b/grading-acceptance-delta-check` because it codifies the current strongest-demo acceptance-snapshot comparison rule instead of introducing another unverified prompt variant
- integrated the accepted worker patch so `src/runtime/verification.py` now exposes `compare_acceptance_summaries()` and deterministic tests assert that only `generated_at_unix` may differ between accepted and refreshed strongest-demo acceptance summaries
- linked `.env.runtime.local` from the canonical repo into this worktree, then ran `make check-live-env`, `make live-status`, `make verify-online`, and `make archive-online-verification` for the acceptance-delta comparison patch
- observed one transient live grading-format failure while retrying `make verify-online`, then re-ran live verification successfully and archived a passing strongest-demo live snapshot under `reports/live-verification-history/strongest-demo-1774381550/`
- confirmed `reports/live-verification-history/strongest-demo-1774381550/acceptance-summary.json` matches the accepted strongest-demo baseline structurally aside from the run timestamp
- recovered this automation worktree from detached `HEAD` onto `curator/groundeddeck-auto-sprint-2c-20260325-r3` before reviewing candidate branches
- confirmed `main` already points at `f6f72bd` (`Codify strongest-demo acceptance delta checks`), which is the latest accepted curator integration
- re-reviewed every ahead-of-`main` worker branch and confirmed they remain one-commit strongest-demo prompt variants without a newer archived live verification result to justify promotion

## Current Status

- acceptance delta comparison: automated in archive flow and eval harness (38/38 evals)
- continuity artifact grading: complete and wired into eval harness (40/40 checks passing)
- repository continuity contract: present
- startup and handoff path: present
- deterministic harness: passing
- deterministic pipeline baseline: passing
- provider abstraction: present
- OpenAI-compatible provider path: present and locally testable
- live verification tooling: ready and proven
- placeholder env detection: present
- live status correctly reports environment readiness and the last archived result
- live credentials / real backend: configured and verified for MiniMax-M2.7
- strongest-demo canonical bundle: present
- automation governance for worker / curator / verifier flows: retired (documents and tooling removed)
- automation role locks for higher-frequency schedules: retired (documents and tooling removed)
- first successful strongest-demo online verification: archived in `reports/live-verification-latest.json` and `reports/live-verification-latest.md`
- near-term focus: expand provider-backed planning from the verified strongest-demo baseline without weakening deterministic evals
- provider prompt tightening for strongest-demo: integrated on the current curator branch
- strongest-demo acceptance-aligned provider prompt guardrails: integrated on the current curator branch
- self-acceptance after prompt tightening: passing
- strongest-demo online verification after prompt tightening: passing and re-archived
- live verification archive now preserves repo-local copies of the verified artifacts instead of `/tmp` paths
- refreshed strongest-demo live acceptance snapshot: committed under `reports/live-verification-history/strongest-demo-1774362852/`
- refreshed strongest-demo live acceptance snapshot after acceptance alignment: present under `reports/live-verification-history/strongest-demo-1774366441/`
- strongest-demo prompt guardrails now load their baseline from the archived acceptance summary instead of duplicating constants in code
- strongest-demo summary-slide prompt rules now require explicit empty evidence arrays, which restored live provider compliance with the slide-spec validator
- refreshed strongest-demo live acceptance snapshot after the acceptance-summary-driven guardrail patch: present under `reports/live-verification-history/strongest-demo-1774370225/`
- strongest-demo acceptance-delta comparison helper: present in `src/runtime/verification.py` with deterministic regression coverage
- most recent passing strongest-demo live refresh after the acceptance-delta comparison patch: present under `reports/live-verification-history/strongest-demo-1774381550/`
- latest archived strongest-demo live refresh remains structurally aligned with the accepted baseline; only the run timestamp changed
- latest archived strongest-demo acceptance snapshot remains structurally identical to the previously accepted baseline
- canonical strongest-demo docs now reference the repository-owned accepted live snapshot at `reports/live-verification-history/strongest-demo-1774370225/`
- provider guardrail code, deterministic tests, and canonical next-step docs now point at the same accepted strongest-demo snapshot: `reports/live-verification-history/strongest-demo-1774370225/`
- the latest rolling live pointer now references `reports/live-verification-history/strongest-demo-1774381550/`, while the accepted strongest-demo baseline remains `reports/live-verification-history/strongest-demo-1774370225/`
- remaining worker prompt variants: reviewed and currently unverified against a newer archived strongest-demo acceptance delta, so no further worker output is pending integration
- current curator review result: no promotable verified worker output beyond what `main` already contains
- visual form selector: extracted from `DeterministicProvider` into `src/visual/selector.py` with `LayoutSelection` data class, `infer_layout_type`, `build_visual_elements`, and `select_visual_form` public APIs
- `DeterministicProvider` now delegates to `src/visual/selector.py` with full behavioral compatibility
- 22 new tests in `tests/test_visual_selector.py` covering rule inference, visual element building, and strongest-demo regression
- total test count: 75 passing, `make eval` 34/34 green
- visual selector wired into `OpenAICompatibleProvider`: `draft_slide_spec` now runs rule-engine post-validation and attaches `_layout_validation` metadata to model output
- visual selector wired into `OpenAICompatibleProvider`: `grade_slide_spec` now injects rule-engine layout analysis into the grader prompt as a grading signal
- added `validate_model_layouts` function and `LayoutValidationReport` data class with `as_grader_hint()` for generating structured validation summaries
- `build_grader_user_prompt` now accepts optional `layout_validation_hint` keyword argument for rule-engine signal injection
- 9 new tests in `LayoutValidationTests` covering match/mismatch detection, missing slides, multi-unit slides, grader hint generation, and strongest-demo regression
- total test count: 84 passing, `make eval` 34/34 green
- model-assisted layout inference: added `model_assisted_infer_layout_type` function with `ModelLayoutCallback` type and automatic rule-based fallback
- `select_visual_form` now accepts optional `layout_callback` keyword argument for model-assisted inference
- `OpenAICompatibleProvider.build_layout_callback()` generates a callback that sends single-unit layout queries to the LLM
- 10 new tests in `ModelAssistedInferenceTests` + 4 new tests in `PipelineFixtureTests` for layout callback and grader hint
- total test count: 98 passing, `make eval` 34/34 green
- implemented PPTX renderer scaffold in `src/renderer/pptx_renderer.py` with `render_slide_spec_to_pptx` entry point
- renderer supports all 7 layout types: cover, summary, timeline, comparison, process, chart, section
- each layout produces styled shapes with professional blue-gray color scheme, speaker notes, and source binding audit trail
- updated `src/renderer/__init__.py` to export public API
- 29 new tests in `tests/test_pptx_renderer.py` covering all layout types, strongest-demo regression, and error handling
- total test count: 127 passing, `make eval` 34/34 green
- renderer implementation: complete
- wired PPTX renderer into `src/runtime/pipeline.py` via `render_pptx` keyword argument on `run_pipeline`
- updated `src/runtime/cli.py` with `--render-pptx` CLI argument, defaults to `output.pptx` in the output directory
- updated `src/runtime/demo.py` to automatically render `strongest-demo.pptx` as part of `write_strongest_demo_bundle`
- added `render-demo` Makefile target for end-to-end strongest-demo pipeline + PPTX rendering
- added `*.pptx` to `.gitignore`
- `make render-demo` successfully produces `reports/strongest-demo/strongest-demo.pptx` (6 slides, 46KB)
- 8 new pipeline PPTX integration tests in `PipelinePptxIntegrationTests`
- total test count: 198 passing, `make eval` 36/36 green
- end-to-end pipeline: complete (source pack → normalized units → slide spec → quality checks → editable PPTX → artifact grading → narrative grading → continuity grading)
- content enrichment: complete (key_points from claims+text, visual_elements with events/column_points/step_labels/labels)
- cover/summary enrichment: complete (cover has audience+core claim+topic-overview, summary has all-unit claims with [binding] annotations)
- narrative quality grading: complete (deterministic + model-assisted modes, three-dimensional scoring)
- artifact grading: complete and wired into pipeline/CLI/demo/eval (editability, notes coverage, source bindings, slide count, chinese text detection)
- evaluation-plan phase one + phase two + phase three: all complete

## Immediate Next Action

Continue improving provider-backed planning and grading against the strongest-demo path without weakening deterministic coverage.

## First Concrete Tasks

1. compare future strongest-demo online refreshes against `reports/live-verification-history/strongest-demo-1774370225/acceptance-summary.json`
2. keep `make verify-online` passing on the real provider path while preserving `make eval`
3. keep strongest-demo canonical docs pinned to the current accepted repository-owned snapshot until a newer verified snapshot is accepted

## Do Not Drift

- do not collapse the project into a single prompt pipeline
- do not skip the intermediate `slide spec`
- do not leave state changes undocumented
- do not fall back to the old example fixture for future claims about the strongest-demo live path

## Resume Hint

If a future session gets only one instruction, it should be:

`Continue GroundedDeck from START-HERE.md and follow the current next action.`
