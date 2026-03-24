# Strongest Demo

[English](STRONGEST-DEMO.md) | [简体中文](STRONGEST-DEMO.zh-CN.md)

## Selected Demo Case

GroundedDeck's strongest planning demo is the Chinese EV market-entry case at:

- [strongest-demo-source-pack.json](/Users/renjinming/code/my_porjects/shamcleren/grounded-deck/fixtures/source-packs/strongest-demo-source-pack.json)

It keeps the current architecture honest because one compact source pack must drive:

- a Chinese-language narrative
- one concrete strategic recommendation
- multiple visual structures in the same deck
- explicit source bindings on every content slide

## Artifact Bundle

The deterministic strongest-demo bundle is:

- source pack: [strongest-demo-source-pack.json](/Users/renjinming/code/my_porjects/shamcleren/grounded-deck/fixtures/source-packs/strongest-demo-source-pack.json)
- normalized units: [strongest-demo-normalized-source-units.json](/Users/renjinming/code/my_porjects/shamcleren/grounded-deck/fixtures/normalized-source-units/strongest-demo-normalized-source-units.json)
- slide spec: [strongest-demo-slide-spec.json](/Users/renjinming/code/my_porjects/shamcleren/grounded-deck/fixtures/slide-spec/strongest-demo-slide-spec.json)
- quality report: [strongest-demo-quality-report.json](/Users/renjinming/code/my_porjects/shamcleren/grounded-deck/fixtures/quality-reports/strongest-demo-quality-report.json)

## Success Metrics

The demo is only considered convincing if all of the following stay true:

1. Coverage: every normalized source unit is present in `must_include_checks`, with `coverage_ratio = 1.0`.
2. Grounding: every non-cover slide keeps at least one valid source binding, with `grounding_ratio = 1.0`.
3. Visual form: the planner selects the intended visual structure for each grounded unit, with `match_ratio = 1.0`.

## Expected Visual Forms

- `src-01:sec-01` -> `timeline`
- `src-01:sec-02` -> `comparison`
- `src-02:sec-01` -> `process`
- `src-03:sec-01` -> `chart`

## Why This Demo First

This case is the strongest current proof point because it demonstrates grounded planning quality before rendering:

- the source pack is small enough to inspect manually
- the deck still needs four different layout decisions
- the output remains fully auditable through `slide spec`
- the same bundle can be reused later for live-provider verification
