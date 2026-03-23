PYTHON ?= python3

.PHONY: eval report context

eval:
	$(PYTHON) harness/self_accept.py

report:
	@if [ -f reports/self-acceptance-latest.md ]; then \
		sed -n '1,220p' reports/self-acceptance-latest.md; \
	else \
		echo "report not found, run 'make eval' first"; \
	fi

context:
	@sed -n '1,220p' AGENTS.md
	@printf '\n'
	@sed -n '1,220p' docs/PROJECT-STATE.md
