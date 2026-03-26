PYTHON ?= python3

.PHONY: eval report context handoff test example-pipeline strongest-demo render-demo demo-saas demo-tech demo-themes demo-all grade-artifact verify-online archive-online-verification check-live-env prepare-live-verification report-live-verification live-status init-live-env compare-acceptance

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

render-demo:
	@echo "==> Running strongest-demo pipeline and rendering PPTX..."
	$(PYTHON) -c "\
from pathlib import Path; \
from src.runtime.demo import write_strongest_demo_bundle; \
result = write_strongest_demo_bundle( \
    input_path=Path('fixtures/source-packs/strongest-demo-source-pack.json'), \
    output_dir=Path('reports/strongest-demo'), \
); \
pptx_path = result['result'].get('pptx_path', 'reports/strongest-demo/strongest-demo.pptx'); \
print(f'PPTX rendered to: {pptx_path}'); \
print(f'Report: {result[\"report_path\"]}'); \
ag = result['result'].get('artifact_grade', {}); \
print(f'Artifact grade: {ag.get(\"status\", \"N/A\")}'); \
print(f'Editability: {ag.get(\"metrics\", {}).get(\"editability_ratio\", \"N/A\")}'); \
print(f'Notes coverage: {ag.get(\"metrics\", {}).get(\"notes_coverage_ratio\", \"N/A\")}'); \
print(f'Source bindings: {ag.get(\"metrics\", {}).get(\"source_binding_coverage_ratio\", \"N/A\")}')"

grade-artifact:
	@echo "==> Grading PPTX artifact..."
	$(PYTHON) harness/grade_artifact.py

demo-saas:
	@echo "==> Running saas-launch pipeline and rendering PPTX..."
	@mkdir -p reports/saas-launch
	$(PYTHON) -c "\
from pathlib import Path; \
import json; \
from src.runtime.pipeline import run_pipeline; \
from src.renderer.pptx_renderer import render_slide_spec_to_pptx; \
raw = json.loads(Path('fixtures/source-packs/saas-launch-source-pack.json').read_text()); \
result = run_pipeline(raw, render_pptx=Path('reports/saas-launch/saas-launch.pptx')); \
print(f'PPTX: {result.get(\"pptx_path\", \"N/A\")}'); \
print(f'Slides: {len(result[\"slide_spec\"][\"slides\"])}'); \
print(f'Quality: {result[\"quality_report\"][\"status\"]}'); \
print(f'Artifact: {result.get(\"artifact_grade\", {}).get(\"status\", \"N/A\")}'); \
Path('reports/saas-launch/slide-spec.json').write_text(json.dumps(result['slide_spec'], ensure_ascii=False, indent=2), encoding='utf-8'); \
Path('reports/saas-launch/quality-report.json').write_text(json.dumps(result['quality_report'], ensure_ascii=False, indent=2), encoding='utf-8')"

demo-tech:
	@echo "==> Running tech-review pipeline and rendering PPTX..."
	@mkdir -p reports/tech-review
	$(PYTHON) -c "\
from pathlib import Path; \
import json; \
from src.runtime.pipeline import run_pipeline; \
from src.renderer.pptx_renderer import render_slide_spec_to_pptx; \
raw = json.loads(Path('fixtures/source-packs/tech-review-source-pack.json').read_text()); \
result = run_pipeline(raw, render_pptx=Path('reports/tech-review/tech-review.pptx')); \
print(f'PPTX: {result.get(\"pptx_path\", \"N/A\")}'); \
print(f'Slides: {len(result[\"slide_spec\"][\"slides\"])}'); \
print(f'Quality: {result[\"quality_report\"][\"status\"]}'); \
print(f'Artifact: {result.get(\"artifact_grade\", {}).get(\"status\", \"N/A\")}'); \
Path('reports/tech-review/slide-spec.json').write_text(json.dumps(result['slide_spec'], ensure_ascii=False, indent=2), encoding='utf-8'); \
Path('reports/tech-review/quality-report.json').write_text(json.dumps(result['quality_report'], ensure_ascii=False, indent=2), encoding='utf-8')"

demo-all: render-demo demo-saas demo-tech demo-themes
	@echo "==> All demos rendered successfully."
	@echo "  - reports/strongest-demo/strongest-demo.pptx"
	@echo "  - reports/saas-launch/saas-launch.pptx"
	@echo "  - reports/tech-review/tech-review.pptx"
	@echo "  - reports/themes/ (5 themed variants)"

demo-themes:
	@echo "==> Rendering all theme variants..."
	@mkdir -p reports/themes
	$(PYTHON) -c "\
from pathlib import Path; \
import json; \
from src.runtime.pipeline import run_pipeline; \
from src.renderer.themes import list_themes; \
raw = json.loads(Path('fixtures/source-packs/strongest-demo-source-pack.json').read_text()); \
for theme in list_themes(): \
    result = run_pipeline(raw, render_pptx=Path(f'reports/themes/{theme}.pptx'), theme=theme); \
    print(f'  {theme}: {result.get(\"pptx_path\", \"N/A\")}'); \
print(f'All {len(list_themes())} themes rendered.')"

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

compare-acceptance:
	@echo "==> Comparing latest archived acceptance summary against accepted baseline..."
	$(PYTHON) -c "\
from pathlib import Path; \
from src.runtime.verification import compare_against_accepted_baseline, render_acceptance_delta_report, ACCEPTED_STRONGEST_DEMO_BASELINE; \
import sys; \
history = ACCEPTED_STRONGEST_DEMO_BASELINE.parent.parent; \
snapshots = sorted([d for d in history.iterdir() if (d / 'acceptance-summary.json').exists()], reverse=True); \
latest = snapshots[0] / 'acceptance-summary.json' if snapshots else None; \
print(f'Baseline: {ACCEPTED_STRONGEST_DEMO_BASELINE}'); \
print(f'Latest:   {latest}'); \
delta = compare_against_accepted_baseline(latest) if latest else {'status': 'error', 'error': 'no snapshots found', 'baseline_path': str(ACCEPTED_STRONGEST_DEMO_BASELINE), 'candidate_path': 'none', 'differences': []}; \
print(render_acceptance_delta_report(delta)); \
sys.exit(0 if delta['status'] in ('match',) else 1)"

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


