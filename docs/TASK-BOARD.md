# Task Board

## In Progress

- implement Markdown Ingest module: parse Markdown documents and use LLM to deeply understand content, producing internal source pack JSON
- keep strongest-demo provider prompts and live verification aligned to the archived acceptance snapshot before promoting more provider-backed planning changes

## Recently Completed

- implemented theme system in `src/renderer/themes.py` with 5 built-in themes: professional-blue, forest-green, warm-sunset, minimal-gray, ocean-teal
- `SlideTheme` frozen dataclass with 18 color slots; PPTX renderer refactored to consume theme colors
- `render_slide_spec_to_pptx` accepts optional `theme` parameter (string or SlideTheme object)
- wired theme into pipeline (`theme` param), CLI (`--theme` flag), Makefile (`demo-themes` target)
- enhanced speaker notes with structured `_build_speaker_notes`: [开场] [要点] [数据] [过渡] [来源] sections
- regenerated all fixture files to reflect enriched speaker notes
- added 23 new tests: ThemeRegistryTests (8), ThemeRenderingTests (6), SpeakerNotesEnhancementTests (6), PipelineThemeIntegrationTests (3)
- total 332 tests passing, 39/39 evals green
- added heading-priority timeline boost: headings with `timeline`/`evolution`/`history`/`checkpoint` + year refs override comparison/process
- tightened comparison contrast connector rule: single `but`/`while` no longer independently triggers comparison
- moved `landscape` keyword to heading-only scope; added chart keywords: `latency`, `throughput`, `metric`, `benchmark`, `sla`
- created `tech-review-source-pack.json` English source pack (cloud platform migration theme) with 4 sources and 6 sections
- generated full tech-review fixture set: 6 normalized units, 11 slides (7 distinct layouts including section dividers), quality pass
- implemented automatic section divider insertion for long decks (content slides >= 6)
- updated quality grader to exempt section layout from ungrounded and empty key_points checks
- added `demo-tech` Makefile target and updated `demo-all`
- added 15 new tests: TechReviewRenderingTests (9) + SectionDividerTests (6), total 309 passing
- enhanced visual selector English keyword coverage for comparison, process, and timeline layout inference
- enhanced comparison column name extraction with English "X vs Y" and "incumbent vs new entrant" patterns
- enhanced process step extraction with English "Phase 1: ... Phase 2: ..." pattern
- created `saas-launch-source-pack.json` English source pack (SaaS product launch theme) with full fixture set
- saas-launch slide spec covers 5 distinct layouts: cover, summary, timeline, comparison, process, chart
- added `demo-saas` and `demo-all` Makefile targets for multi-sample PPTX rendering
- created `tests/test_diverse_samples.py` with 20 new tests covering rendering, pipeline, fixture compatibility, and English keyword inference
- total test count: 294 passing, 38/38 evals green
- upgraded timeline layout from text-box labels to native python-pptx Table with decorative axis and dot nodes
- upgraded process layout from text-box step cards to native python-pptx Table with decorative arrows
- enhanced section layout with decorative separator lines (top and bottom accent lines)
- all 4 data-bearing layouts (comparison, chart, timeline, process) now use native Table objects
- added 10 NativeTableRenderingTests + 2 SectionEnhancementTests, total 274 passing, 38/38 evals green
- enhanced PPTX renderer with cross-platform CJK font fallback chain (`_detect_cjk_font`, `_set_east_asian_font`, `CJK_FONT_FALLBACK_CHAIN`)
- upgraded comparison layout from text-box cards to native python-pptx Table with colored header row and alternating row backgrounds
- upgraded chart layout from text-box metric cards to native python-pptx Table (2 rows x n columns)
- added 5 ChineseFontFallbackTests and 8 NativeTableRenderingTests, total 262 passing, 38/38 evals green
- added narrative quality post-validation to `OpenAICompatibleProvider.grade_slide_spec`: deterministic narrative grader results attached as `_narrative_validation` metadata for cross-validation of model grading
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

- implement data chart generation (bar, line, pie charts) in PPTX renderer based on numeric data from source understanding
- implement concept diagram generation (flowcharts, architecture diagrams) in PPTX renderer based on structural/relational information
- add PDF ingest adapter as the second supported input format
- add DOCX ingest adapter as the third supported input format
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
