from __future__ import annotations

from src.llm.provider import DeterministicProvider, Provider


def draft_slide_spec(normalized_pack: dict, provider: Provider | None = None) -> dict:
    active_provider = provider or DeterministicProvider()
    return active_provider.draft_slide_spec(normalized_pack)
