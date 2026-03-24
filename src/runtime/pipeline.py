from __future__ import annotations

from src.ingest.normalize import normalize_source_pack
from src.llm.provider import DeterministicProvider, Provider
from src.planner.draft import draft_slide_spec
from src.quality.checks import grade_slide_spec


def run_pipeline(raw_pack: dict, provider: Provider | None = None) -> dict:
    active_provider = provider or DeterministicProvider()
    normalized_pack = normalize_source_pack(raw_pack)
    slide_spec = draft_slide_spec(normalized_pack, provider=active_provider)
    quality_report = grade_slide_spec(normalized_pack, slide_spec, provider=active_provider)

    return {
        "normalized_pack": normalized_pack,
        "slide_spec": slide_spec,
        "quality_report": quality_report,
        "provider": active_provider.name,
        "model": active_provider.config.model,
    }
