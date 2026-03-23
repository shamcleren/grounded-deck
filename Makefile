PYTHON ?= python3

.PHONY: eval report

eval:
	$(PYTHON) harness/self_accept.py

report:
	@if [ -f reports/self-acceptance-latest.md ]; then \
		sed -n '1,220p' reports/self-acceptance-latest.md; \
	else \
		echo "report not found, run 'make eval' first"; \
	fi
