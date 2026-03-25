from __future__ import annotations

import argparse
import json
from pathlib import Path
from time import time

from src.llm.provider import build_provider_from_env
from src.runtime.pipeline import run_pipeline
from src.runtime.verification import build_failure_summary


def write_pipeline_outputs(output_dir: Path, result: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "normalized-pack.json").write_text(
        json.dumps(result["normalized_pack"], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "slide-spec.json").write_text(
        json.dumps(result["slide_spec"], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "quality-report.json").write_text(
        json.dumps(result["quality_report"], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_verification_summary(
    *,
    output_dir: Path,
    result: dict,
    mode: str,
    input_path: Path,
) -> Path:
    summary_path = output_dir / "verification-summary.json"
    summary = {
        "mode": mode,
        "provider": result["provider"],
        "model": result["model"],
        "input_path": str(input_path),
        "generated_at_unix": int(time()),
        "artifacts": {
            "normalized_pack": str(output_dir / "normalized-pack.json"),
            "slide_spec": str(output_dir / "slide-spec.json"),
            "quality_report": str(output_dir / "quality-report.json"),
        },
        "quality_status": result["quality_report"]["status"],
    }
    if "artifact_grade" in result:
        summary["artifact_grade_status"] = result["artifact_grade"]["status"]
        summary["artifacts"]["artifact_grade"] = str(output_dir / "artifact-grade.json")
    if "narrative_grade" in result:
        summary["narrative_grade_status"] = result["narrative_grade"]["status"]
        summary["artifacts"]["narrative_grade"] = str(output_dir / "narrative-grade.json")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the grounded-deck pipeline on a source-pack JSON file.")
    parser.add_argument("--input", required=True, help="Path to a source-pack JSON file.")
    parser.add_argument("--output-dir", required=True, help="Directory for normalized, slide-spec, and quality outputs.")
    parser.add_argument(
        "--require-live-provider",
        action="store_true",
        help="Fail unless GROUNDED_DECK_LLM_PROVIDER resolves to a non-deterministic provider.",
    )
    parser.add_argument(
        "--render-pptx",
        default=None,
        help="If provided, render the slide spec to a .pptx file at this path.",
    )
    parser.add_argument(
        "--grade-artifact",
        action="store_true",
        default=True,
        help="Grade the rendered PPTX artifact for editability, notes coverage, etc. (default: True)",
    )
    parser.add_argument(
        "--no-grade-artifact",
        action="store_false",
        dest="grade_artifact",
        help="Skip PPTX artifact grading.",
    )
    args = parser.parse_args()

    raw_pack = json.loads(Path(args.input).read_text(encoding="utf-8"))
    provider = build_provider_from_env()
    if args.require_live_provider and provider.name == "deterministic":
        raise SystemExit(
            "live provider required, but GROUNDED_DECK_LLM_PROVIDER resolved to deterministic"
        )

    output_dir = Path(args.output_dir)
    mode = "online-verification" if args.require_live_provider else "offline-example"

    try:
        # 确定 PPTX 渲染路径
        render_pptx = args.render_pptx
        if render_pptx is None and output_dir:
            # 如果没有显式指定 --render-pptx，默认输出到 output_dir
            render_pptx = str(output_dir / "output.pptx")

        result = run_pipeline(
            raw_pack,
            provider=provider,
            render_pptx=render_pptx,
            grade_artifact=args.grade_artifact,
        )
        write_pipeline_outputs(output_dir, result)
        write_verification_summary(
            output_dir=output_dir,
            result=result,
            mode=mode,
            input_path=Path(args.input),
        )
    except Exception as exc:
        output_dir.mkdir(parents=True, exist_ok=True)
        failure_summary = build_failure_summary(
            mode=mode,
            provider=provider.name,
            model=provider.config.model,
            input_path=str(Path(args.input)),
            error=str(exc),
        )
        (output_dir / "verification-summary.json").write_text(
            json.dumps(failure_summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        raise

    output_info = {"provider": result["provider"], "model": result["model"]}
    if "pptx_path" in result:
        output_info["pptx_path"] = result["pptx_path"]
    if "artifact_grade" in result:
        output_info["artifact_grade_status"] = result["artifact_grade"]["status"]
        # 写入 artifact grading 报告
        artifact_report_path = output_dir / "artifact-grade.json"
        artifact_report_path.write_text(
            json.dumps(result["artifact_grade"], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        output_info["artifact_grade_path"] = str(artifact_report_path)
    if "narrative_grade" in result:
        output_info["narrative_grade_status"] = result["narrative_grade"]["status"]
        # 写入 narrative grading 报告
        narrative_report_path = output_dir / "narrative-grade.json"
        narrative_report_path.write_text(
            json.dumps(result["narrative_grade"], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        output_info["narrative_grade_path"] = str(narrative_report_path)
    print(json.dumps(output_info, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
