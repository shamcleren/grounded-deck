from __future__ import annotations

from src.llm.provider import DeterministicProvider, Provider


def grade_slide_spec(
    normalized_pack: dict,
    slide_spec: dict,
    provider: Provider | None = None,
) -> dict:
    active_provider = provider or DeterministicProvider()
    return active_provider.grade_slide_spec(normalized_pack, slide_spec)
