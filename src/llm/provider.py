from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Callable
from urllib import request

from src.llm.validation import validate_quality_report_like, validate_slide_spec_like
from src.runtime.env import load_runtime_env


@dataclass(frozen=True)
class ProviderConfig:
    provider: str = "deterministic"
    model: str = "baseline-fixture"
    api_key_env: str = "GROUNDED_DECK_API_KEY"
    base_url: str | None = None


class Provider:
    def __init__(self, config: ProviderConfig | None = None) -> None:
        self.config = config or ProviderConfig()

    @property
    def name(self) -> str:
        return self.config.provider

    def draft_slide_spec(self, normalized_pack: dict) -> dict:
        raise NotImplementedError

    def grade_slide_spec(self, normalized_pack: dict, slide_spec: dict) -> dict:
        raise NotImplementedError


class DeterministicProvider(Provider):
    def draft_slide_spec(self, normalized_pack: dict) -> dict:
        source_units = normalized_pack["source_units"]
        summary_points: list[str] = []
        for unit in source_units:
            summary_points.extend(unit.get("claims", []))

        return {
            "deck_goal": normalized_pack["deck_goal"],
            "audience": normalized_pack["audience"],
            "slides": [
                {
                    "slide_id": "s1-cover",
                    "title": normalized_pack["deck_goal"],
                    "goal": "Orient the audience to the presentation goal and source scope.",
                    "layout_type": "cover",
                    "key_points": [
                        normalized_pack["audience"],
                        f'{len(source_units)} grounded source units',
                    ],
                    "visual_elements": [
                        {"type": "title-block"},
                        {"type": "source-count", "value": len(source_units)},
                    ],
                    "source_bindings": [unit["source_binding"] for unit in source_units],
                    "must_include_checks": [unit["unit_id"] for unit in source_units],
                    "speaker_notes": "Introduce the deck goal and emphasize that claims stay grounded to source material.",
                },
                {
                    "slide_id": "s2-summary",
                    "title": "Key Takeaways",
                    "goal": "Summarize the main grounded claims that must be carried into the deck.",
                    "layout_type": "summary",
                    "key_points": summary_points[:3],
                    "visual_elements": [
                        {"type": "bullet-list"},
                    ],
                    "source_bindings": [unit["source_binding"] for unit in source_units],
                    "must_include_checks": [unit["unit_id"] for unit in source_units],
                    "speaker_notes": "This slide compresses the source pack into the minimum set of claims the deck must retain.",
                },
            ],
        }

    def grade_slide_spec(self, normalized_pack: dict, slide_spec: dict) -> dict:
        failures: list[str] = []

        available_bindings = {unit["source_binding"] for unit in normalized_pack["source_units"]}
        required_units = {unit["unit_id"] for unit in normalized_pack["source_units"]}

        covered_units = set()
        for slide in slide_spec["slides"]:
            for binding in slide.get("source_bindings", []):
                if binding not in available_bindings:
                    failures.append(f'unknown source binding on {slide["slide_id"]}: {binding}')

            covered_units.update(slide.get("must_include_checks", []))

        missing_units = sorted(required_units - covered_units)
        if missing_units:
            failures.append(f"uncovered source units: {', '.join(missing_units)}")

        return {
            "status": "pass" if not failures else "fail",
            "failures": failures,
            "coverage": {
                "required_units": len(required_units),
                "covered_units": len(required_units & covered_units),
            },
            "provider": self.name,
            "model": self.config.model,
        }


class OpenAICompatibleProvider(Provider):
    def __init__(
        self,
        config: ProviderConfig,
        api_key: str | None = None,
        transport: Callable[[dict], dict] | None = None,
    ) -> None:
        super().__init__(config)
        if not self.config.base_url:
            raise ValueError("openai-compatible provider requires GROUNDED_DECK_BASE_URL")
        self.api_key = api_key
        self.transport = transport or self._default_transport

    def build_chat_request(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_format: dict | None = None,
    ) -> dict:
        if not self.api_key:
            raise ValueError("openai-compatible provider requires an API key")

        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        if response_format is not None:
            payload["response_format"] = response_format

        return {
            "url": f'{self.config.base_url.rstrip("/")}/chat/completions',
            "headers": {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            "json": payload,
        }

    def parse_json_response(self, response_json: dict) -> dict:
        choices = response_json.get("choices", [])
        if not choices:
            raise ValueError("response did not include choices")

        content = choices[0].get("message", {}).get("content")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("response did not include message content")

        return json.loads(content)

    def draft_slide_spec(self, normalized_pack: dict) -> dict:
        request_payload = self.build_chat_request(
            system_prompt=(
                "You are GroundedDeck's planner. "
                "Return only valid JSON matching the slide-spec schema. "
                "Required root fields: deck_goal, audience, slides. "
                "Each slide must include slide_id, title, goal, layout_type, key_points, visual_elements, source_bindings, must_include_checks."
            ),
            user_prompt=(
                "Draft a grounded slide spec from this normalized source pack:\n"
                f"{json.dumps(normalized_pack, ensure_ascii=False)}"
            ),
            response_format={"type": "json_object"},
        )
        parsed = self.parse_json_response(self.transport(request_payload))
        validate_slide_spec_like(parsed)
        return parsed

    def grade_slide_spec(self, normalized_pack: dict, slide_spec: dict) -> dict:
        request_payload = self.build_chat_request(
            system_prompt=(
                "You are GroundedDeck's quality grader. "
                "Return only valid JSON with status, failures, coverage, provider, and model. "
                "Required fields: status, failures, coverage. "
                "Coverage must include required_units and covered_units."
            ),
            user_prompt=(
                "Grade this slide_spec against the normalized source pack.\n"
                f"normalized_pack={json.dumps(normalized_pack, ensure_ascii=False)}\n"
                f"slide_spec={json.dumps(slide_spec, ensure_ascii=False)}"
            ),
            response_format={"type": "json_object"},
        )
        parsed = self.parse_json_response(self.transport(request_payload))
        validate_quality_report_like(parsed)
        return parsed

    def _default_transport(self, prepared_request: dict) -> dict:
        req = request.Request(
            prepared_request["url"],
            data=json.dumps(prepared_request["json"]).encode("utf-8"),
            headers=prepared_request["headers"],
            method="POST",
        )
        with request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))


def build_provider_from_env(env: dict[str, str] | None = None) -> Provider:
    values = load_runtime_env() if env is None else dict(env)
    config = ProviderConfig(
        provider=values.get("GROUNDED_DECK_LLM_PROVIDER", "deterministic"),
        model=values.get("GROUNDED_DECK_LLM_MODEL", "baseline-fixture"),
        api_key_env=values.get("GROUNDED_DECK_API_KEY_ENV", "GROUNDED_DECK_API_KEY"),
        base_url=values.get("GROUNDED_DECK_BASE_URL"),
    )

    if config.provider == "deterministic":
        return DeterministicProvider(config)
    if config.provider == "openai-compatible":
        api_key = values.get(config.api_key_env)
        return OpenAICompatibleProvider(config, api_key=api_key)

    raise ValueError(f"unsupported provider: {config.provider}")
