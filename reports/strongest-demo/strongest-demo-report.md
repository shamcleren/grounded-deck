# Strongest Demo Report

- Demo Fixture: `fixtures/source-packs/strongest-demo-source-pack.json`
- Provider: `deterministic`
- Model: `baseline-fixture`
- Deck Goal: `Recommend a grounded China EV market-entry plan for Europe and Southeast Asia.`
- Audience: `Regional strategy leaders deciding 2025 market sequencing`
- Slide Count: `6`
- Verification Summary: `reports/strongest-demo/verification-summary.json`

## Success Metrics

- Coverage: `4/4` source units retained in `must_include_checks`.
- Grounding: `5/5` non-cover slides keep valid source bindings.
- Visual Form: `4/4` grounded units match deterministic layout expectations.

## Artifact Bundle

- Normalized Pack: `reports/strongest-demo/normalized-pack.json`
- Slide Spec: `reports/strongest-demo/slide-spec.json`
- Quality Report: `reports/strongest-demo/quality-report.json`
- Verification Summary: `reports/strongest-demo/verification-summary.json`

## Why This Demo

- Uses grounded Chinese-language source material instead of generic topic prompts.
- Exercises narrative compression, policy risk retention, and cross-source synthesis in one pass.
- Stays within the current planning boundary without pretending rendering is done.

