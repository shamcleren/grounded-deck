PYTHON ?= python3

.PHONY: eval report context handoff

eval:
	$(PYTHON) harness/self_accept.py

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
