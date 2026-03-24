from __future__ import annotations

import json
import os
import re
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
    @staticmethod
    def unique_preserving_order(values: list[str]) -> list[str]:
        seen: set[str] = set()
        ordered: list[str] = []
        for value in values:
            if value in seen:
                continue
            seen.add(value)
            ordered.append(value)
        return ordered

    @staticmethod
    def infer_layout_type(unit: dict) -> str:
        text = f'{unit["section_heading"]} {unit["text"]}'.lower()

        if "vs" in text or "对比" in text or "差异" in text:
            return "comparison"
        if "路径" in text or "步骤" in text or "进入" in text or "落地" in text:
            return "process"
        if "时间线" in text or "阶段" in text or re.search(r"\b20\d{2}\b", text):
            return "timeline"
        if (
            "成本" in text
            or "利润" in text
            or "指标" in text
            or "份额" in text
            or "%" in text
            or re.search(r"\d", text)
        ):
            return "chart"
        return "summary"

    @staticmethod
    def build_visual_elements(layout_type: str, unit: dict) -> list[dict]:
        if layout_type == "timeline":
            milestones = DeterministicProvider.unique_preserving_order(
                re.findall(r"\b(20\d{2})\b", unit["text"])
            )
            return [{"type": "timeline", "milestones": milestones[:4]}]
        if layout_type == "comparison":
            columns = []
            for label in ("欧洲", "东南亚"):
                if label in unit["text"] and label not in columns:
                    columns.append(label)
            return [{"type": "comparison-columns", "columns": columns or ["Option A", "Option B"]}]
        if layout_type == "process":
            return [{"type": "process-flow", "steps": max(1, len(unit.get("claims", [])))}]
        if layout_type == "chart":
            metrics = DeterministicProvider.unique_preserving_order(
                re.findall(r"\d+%|\d+\.\d+%|\d+", unit["text"])
            )
            return [{"type": "metric-cards", "metrics": metrics[:4]}]
        return [{"type": "bullet-list"}]

    @classmethod
    def build_unit_slide(cls, unit: dict) -> dict:
        layout_type = cls.infer_layout_type(unit)
        claim_points = unit.get("claims", []) or [unit["text"]]
        goals = {
            "timeline": "Show how the grounded evidence changes over time.",
            "comparison": "Contrast grounded market options without losing source traceability.",
            "process": "Turn grounded evidence into an ordered action path.",
            "chart": "Surface the grounded numeric signal that should shape the decision.",
            "summary": "Retain the grounded claim in a compact, editable form.",
        }

        return {
            "slide_id": f'slide-{unit["source_id"]}-{unit["section_id"]}',
            "title": unit["section_heading"],
            "goal": goals[layout_type],
            "layout_type": layout_type,
            "key_points": claim_points[:3],
            "visual_elements": cls.build_visual_elements(layout_type, unit),
            "source_bindings": [unit["source_binding"]],
            "must_include_checks": [unit["unit_id"]],
            "speaker_notes": f'Ground this slide in {unit["source_binding"]} and keep the structure editable.',
        }

    def draft_slide_spec(self, normalized_pack: dict) -> dict:
        source_units = normalized_pack["source_units"]
        summary_points: list[str] = []
        for unit in source_units:
            summary_points.extend(unit.get("claims", []))

        content_slides = [self.build_unit_slide(unit) for unit in source_units]

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
                    "title": "Decision Backbone",
                    "goal": "Compress the source pack into the minimum grounded claims the deck must preserve.",
                    "layout_type": "summary",
                    "key_points": summary_points[:3],
                    "visual_elements": [
                        {"type": "bullet-list"},
                    ],
                    "source_bindings": [unit["source_binding"] for unit in source_units],
                    "must_include_checks": [unit["unit_id"] for unit in source_units],
                    "speaker_notes": "This slide compresses the source pack into the minimum set of claims the deck must retain.",
                },
            ]
            + content_slides,
        }

    def grade_slide_spec(self, normalized_pack: dict, slide_spec: dict) -> dict:
        failures: list[str] = []

        available_bindings = {unit["source_binding"] for unit in normalized_pack["source_units"]}
        required_units = {unit["unit_id"] for unit in normalized_pack["source_units"]}

        covered_units = set()
        grounded_slide_ids: list[str] = []
        ungrounded_slide_ids: list[str] = []
        for slide in slide_spec["slides"]:
            for binding in slide.get("source_bindings", []):
                if binding not in available_bindings:
                    failures.append(f'unknown source binding on {slide["slide_id"]}: {binding}')

            covered_units.update(slide.get("must_include_checks", []))

            if slide["layout_type"] == "cover":
                continue

            if slide.get("source_bindings"):
                grounded_slide_ids.append(slide["slide_id"])
            else:
                ungrounded_slide_ids.append(slide["slide_id"])

        missing_units = sorted(required_units - covered_units)
        if missing_units:
            failures.append(f"uncovered source units: {', '.join(missing_units)}")

        if ungrounded_slide_ids:
            failures.append(f"ungrounded slides: {', '.join(ungrounded_slide_ids)}")

        layout_mismatches: list[dict] = []
        matched_units = 0
        for unit in normalized_pack["source_units"]:
            expected_layout = self.infer_layout_type(unit)
            matching_slide = next(
                (
                    slide
                    for slide in slide_spec["slides"]
                    if slide.get("must_include_checks") == [unit["unit_id"]]
                ),
                None,
            )

            if matching_slide is None:
                layout_mismatches.append(
                    {
                        "unit_id": unit["unit_id"],
                        "expected_layout": expected_layout,
                        "actual_layout": None,
                    }
                )
                continue

            actual_layout = matching_slide["layout_type"]
            if actual_layout == expected_layout:
                matched_units += 1
            else:
                layout_mismatches.append(
                    {
                        "unit_id": unit["unit_id"],
                        "expected_layout": expected_layout,
                        "actual_layout": actual_layout,
                    }
                )

        if layout_mismatches:
            failures.append(
                "visual-form mismatches: "
                + ", ".join(
                    f'{item["unit_id"]} expected {item["expected_layout"]} got {item["actual_layout"] or "missing"}'
                    for item in layout_mismatches
                )
            )

        total_content_slides = len(slide_spec["slides"]) - 1 if slide_spec["slides"] else 0

        return {
            "status": "pass" if not failures else "fail",
            "failures": failures,
            "coverage": {
                "required_units": len(required_units),
                "covered_units": len(required_units & covered_units),
                "coverage_ratio": round(len(required_units & covered_units) / max(1, len(required_units)), 2),
            },
            "grounding": {
                "total_content_slides": total_content_slides,
                "grounded_slides": len(grounded_slide_ids),
                "ungrounded_slide_ids": ungrounded_slide_ids,
                "grounding_ratio": round(len(grounded_slide_ids) / max(1, total_content_slides), 2),
            },
            "visual_form": {
                "expected_units": len(required_units),
                "matched_units": matched_units,
                "mismatches": layout_mismatches,
                "match_ratio": round(matched_units / max(1, len(required_units)), 2),
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
                "Return only valid JSON with status, failures, coverage, grounding, visual_form, provider, and model. "
                "Required fields: status, failures, coverage, grounding, visual_form. "
                "Coverage must include required_units and covered_units. "
                "Grounding must include total_content_slides and grounded_slides. "
                "Visual_form must include expected_units and matched_units."
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
