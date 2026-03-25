#!/usr/bin/env python3
"""独立的 PPTX artifact grading 脚本，供 `make grade-artifact` 调用。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.renderer.artifact_grader import grade_pptx_artifact


def main() -> int:
    pptx_path = ROOT / "reports" / "strongest-demo" / "strongest-demo.pptx"
    spec_path = ROOT / "reports" / "strongest-demo" / "slide-spec.json"

    if not pptx_path.exists():
        print("ERROR: PPTX not found. Run 'make render-demo' first.")
        return 1

    spec = json.loads(spec_path.read_text(encoding="utf-8")) if spec_path.exists() else None
    report = grade_pptx_artifact(pptx_path, slide_spec=spec)

    out_path = ROOT / "reports" / "strongest-demo" / "artifact-grade.json"
    out_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    m = report["metrics"]
    print(f"Status: {report['status']}")
    print(f"Slides: {m['slide_count']}")
    print(f"Shapes: {m['total_shapes']}")
    print(f"Text boxes: {m['total_text_boxes']} (editable: {m['editable_text_boxes']})")
    print(f"Editability: {m['editability_ratio']}")
    print(f"Notes coverage: {m['notes_coverage_ratio']}")
    print(f"Source bindings coverage: {m['source_binding_coverage_ratio']}")
    print(f"Chinese text: {m['chinese_text_found']}")
    if report["failures"]:
        print(f"Failures: {report['failures']}")
    if report["warnings"]:
        print(f"Warnings: {report['warnings']}")
    print(f"Report saved to: {out_path}")

    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
