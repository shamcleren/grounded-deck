# Live Verification Checklist

- Status: `BLOCKED`
- Missing Config: `GROUNDED_DECK_LLM_PROVIDER, GROUNDED_DECK_LLM_MODEL, GROUNDED_DECK_BASE_URL, GROUNDED_DECK_API_KEY`

## Steps

1. Run `make check-live-env` and confirm it returns `OK`.
2. Run `make verify-online` to execute the live provider path.
3. Inspect `/tmp/grounded-deck-online/verification-summary.json`.
4. Run `make archive-online-verification` to copy the successful result into `reports/`.
5. Update `docs/LATEST-HANDOFF.md` and `docs/TASK-BOARD.md` with the observed result.

## Success Criteria

- `quality_status` is `pass` in `verification-summary.json`.
- The summary references `normalized-pack.json`, `slide-spec.json`, and `quality-report.json`.
- `reports/live-verification-latest.json` and `.md` are present after archiving.

