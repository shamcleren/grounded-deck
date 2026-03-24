PYTHON ?= python3

.PHONY: eval report context handoff test example-pipeline strongest-demo verify-online archive-online-verification check-live-env prepare-live-verification report-live-verification live-status init-live-env curator-finalize automation-lock-status-worker automation-lock-status-curator

eval:
	$(PYTHON) harness/self_accept.py

test:
	$(PYTHON) -m unittest discover -s tests

example-pipeline:
	$(PYTHON) -m src.runtime.cli \
		--input fixtures/source-packs/example-source-pack.json \
		--output-dir /tmp/grounded-deck-example

strongest-demo:
	$(PYTHON) -c "from pathlib import Path; from src.runtime.demo import write_strongest_demo_bundle; result = write_strongest_demo_bundle(input_path=Path('fixtures/source-packs/strongest-demo-source-pack.json'), output_dir=Path('reports/strongest-demo')); print(result['report_path'])"

verify-online:
	$(PYTHON) -m src.runtime.cli \
		--input fixtures/source-packs/strongest-demo-source-pack.json \
		--output-dir /tmp/grounded-deck-online \
		--require-live-provider

check-live-env:
	$(PYTHON) -c "from src.runtime.verification import validate_live_verification_env; ok, missing = validate_live_verification_env(); print('OK' if ok else 'MISSING:' + ','.join(missing)); raise SystemExit(0 if ok else 1)"

prepare-live-verification:
	$(PYTHON) -c "from pathlib import Path; from src.runtime.verification import write_live_verification_checklist; p = write_live_verification_checklist(Path('reports/live-verification-checklist.md')); print(p)"

archive-online-verification:
	$(PYTHON) -c "from pathlib import Path; from src.runtime.verification import archive_verification_summary; archive_verification_summary(Path('/tmp/grounded-deck-online/verification-summary.json'), Path('reports'))"

report-live-verification:
	@if [ -f reports/live-verification-latest.md ]; then \
		sed -n '1,240p' reports/live-verification-latest.md; \
	else \
		echo "live verification report not found, run 'make archive-online-verification' after verify-online"; \
	fi

live-status:
	$(PYTHON) -c "from pathlib import Path; from src.runtime.verification import render_live_verification_status; print(render_live_verification_status(Path('/tmp/grounded-deck-online/verification-summary.json')))"

init-live-env:
	@if [ -f .env.runtime.local ]; then \
		echo ".env.runtime.local already exists"; \
	else \
		cp .env.runtime.example .env.runtime.local; \
		echo "created .env.runtime.local from .env.runtime.example"; \
	fi

report:
	@if [ -f reports/self-acceptance-latest.md ]; then \
		sed -n '1,220p' reports/self-acceptance-latest.md; \
	else \
		echo "report not found, run 'make eval' first"; \
	fi

context:
	@sed -n '1,220p' START-HERE.md
	@printf '\n'
	@sed -n '1,220p' AGENTS.md
	@printf '\n'
	@sed -n '1,220p' docs/PROJECT-STATE.md

handoff:
	@sed -n '1,240p' docs/LATEST-HANDOFF.md
	@printf '\n'
	@sed -n '1,240p' docs/TASK-BOARD.md

curator-finalize:
	@./scripts/curator_finalize.sh

automation-lock-status-worker:
	$(PYTHON) -m src.runtime.automation_lock status worker

automation-lock-status-curator:
	$(PYTHON) -m src.runtime.automation_lock status curator
