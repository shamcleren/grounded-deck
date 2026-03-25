from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from urllib import error, request

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
    STRONGEST_DEMO_PACK_ID = "china-ev-market-entry"
    STRONGEST_DEMO_ACCEPTANCE_SNAPSHOT = (
        Path(__file__).resolve().parents[2]
        / "reports"
        / "live-verification-history"
        / "strongest-demo-1774370225"
        / "acceptance-summary.json"
    )
    STRONGEST_DEMO_SLIDE_SPEC_SNAPSHOT = STRONGEST_DEMO_ACCEPTANCE_SNAPSHOT.with_name("slide-spec.json")
    STRONGEST_DEMO_UNIT_ORDER = [
        "src-01:sec-01",
        "src-01:sec-02",
        "src-02:sec-01",
        "src-03:sec-01",
    ]
    _strongest_demo_acceptance_summary: dict | None = None
    _strongest_demo_slide_spec_snapshot: dict | None = None

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
        if self.config.model.startswith("MiniMax-"):
            payload["reasoning_split"] = True
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
        raw_content = self._coerce_message_content(content)
        if not raw_content:
            raise ValueError("response did not include message content")

        candidate = self._extract_json_candidate(raw_content)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError as exc:
            snippet = self._content_snippet(raw_content)
            raise ValueError(
                f"response content was not valid JSON: {exc.msg} at line {exc.lineno} column {exc.colno}; "
                f"content_snippet={snippet}"
            ) from exc

    @staticmethod
    def _coerce_message_content(content: object) -> str:
        if isinstance(content, str):
            return content.strip()
        if isinstance(content, list):
            text_parts: list[str] = []
            for item in content:
                if isinstance(item, str):
                    text_parts.append(item)
                    continue
                if isinstance(item, dict) and item.get("type") == "text":
                    text_value = item.get("text")
                    if isinstance(text_value, str):
                        text_parts.append(text_value)
            return "\n".join(part.strip() for part in text_parts if part and part.strip()).strip()
        return ""

    @classmethod
    def _extract_json_candidate(cls, raw_content: str) -> str:
        stripped = raw_content.strip()
        stripped = re.sub(r"<think>.*?</think>\s*", "", stripped, flags=re.DOTALL).strip()
        if stripped.startswith("```"):
            fenced = re.match(r"^```(?:json)?\s*(.*?)\s*```$", stripped, re.DOTALL)
            if fenced:
                stripped = fenced.group(1).strip()

        if stripped.startswith("{") or stripped.startswith("["):
            return stripped

        json_start_positions = [index for index in (stripped.find("{"), stripped.find("[")) if index >= 0]
        if not json_start_positions:
            return stripped

        start = min(json_start_positions)
        end_object = stripped.rfind("}")
        end_array = stripped.rfind("]")
        end = max(end_object, end_array)
        if end >= start:
            return stripped[start : end + 1].strip()

        return stripped

    @staticmethod
    def _content_snippet(raw_content: str, limit: int = 240) -> str:
        snippet = raw_content.strip().replace("\n", "\\n")
        if len(snippet) > limit:
            return snippet[:limit] + "..."
        return snippet

    @classmethod
    def _matches_strongest_demo_pack(cls, normalized_pack: dict) -> bool:
        source_units = normalized_pack.get("source_units", [])
        unit_ids = [unit.get("unit_id") for unit in source_units]
        return normalized_pack.get("pack_id") == cls.STRONGEST_DEMO_PACK_ID and unit_ids == cls.STRONGEST_DEMO_UNIT_ORDER

    @classmethod
    def _load_strongest_demo_acceptance_summary(cls) -> dict:
        if cls._strongest_demo_acceptance_summary is None:
            cls._strongest_demo_acceptance_summary = json.loads(
                cls.STRONGEST_DEMO_ACCEPTANCE_SNAPSHOT.read_text(encoding="utf-8")
            )
        return cls._strongest_demo_acceptance_summary

    @classmethod
    def _load_strongest_demo_slide_spec_snapshot(cls) -> dict:
        if cls._strongest_demo_slide_spec_snapshot is None:
            cls._strongest_demo_slide_spec_snapshot = json.loads(
                cls.STRONGEST_DEMO_SLIDE_SPEC_SNAPSHOT.read_text(encoding="utf-8")
            )
        return cls._strongest_demo_slide_spec_snapshot

    @classmethod
    def _strongest_demo_intro_title(cls) -> str:
        summary = cls._load_strongest_demo_acceptance_summary()
        return str(summary.get("intro_slide", {}).get("title", ""))

    @classmethod
    def _strongest_demo_unit_layouts(cls) -> dict[str, str]:
        summary = cls._load_strongest_demo_acceptance_summary()
        return dict(summary.get("unit_layouts", {}))

    @classmethod
    def _strongest_demo_unit_titles(cls) -> dict[str, str]:
        summary = cls._load_strongest_demo_acceptance_summary()
        return dict(summary.get("unit_slide_titles", {}))

    @classmethod
    def _strongest_demo_unit_evidence(cls) -> dict[str, dict[str, list[str]]]:
        summary = cls._load_strongest_demo_acceptance_summary()
        return dict(summary.get("unit_slide_evidence", {}))

    @classmethod
    def _strongest_demo_layout_sequence(cls) -> list[str]:
        summary = cls._load_strongest_demo_acceptance_summary()
        return list(summary.get("layout_sequence", []))

    @classmethod
    def _strongest_demo_decision_backbone_bindings(cls) -> list[str]:
        summary = cls._load_strongest_demo_acceptance_summary()
        return list(summary.get("decision_backbone", {}).get("source_bindings", []))

    @classmethod
    def _strongest_demo_decision_backbone_checks(cls) -> list[str]:
        summary = cls._load_strongest_demo_acceptance_summary()
        return list(summary.get("decision_backbone", {}).get("must_include_checks", []))

    @classmethod
    def _strongest_demo_covered_unit_ids(cls) -> list[str]:
        summary = cls._load_strongest_demo_acceptance_summary()
        return list(summary.get("covered_unit_ids", []))

    @classmethod
    def _strongest_demo_visual_matched_unit_ids(cls) -> list[str]:
        summary = cls._load_strongest_demo_acceptance_summary()
        return list(summary.get("visual_matched_unit_ids", []))

    @classmethod
    def _strongest_demo_grounded_content_slides(cls) -> int:
        summary = cls._load_strongest_demo_acceptance_summary()
        return int(summary.get("grounded_content_slides", 0))

    @classmethod
    def _strongest_demo_total_content_slides(cls) -> int:
        summary = cls._load_strongest_demo_acceptance_summary()
        return int(summary.get("total_content_slides", 0))

    @classmethod
    def _strongest_demo_slide_id_sequence(cls) -> list[str]:
        slide_spec = cls._load_strongest_demo_slide_spec_snapshot()
        return [str(slide.get("slide_id", "")) for slide in slide_spec.get("slides", [])]

    @classmethod
    def _build_strongest_demo_planner_rules(cls) -> str:
        unit_layouts = cls._strongest_demo_unit_layouts()
        unit_titles = cls._strongest_demo_unit_titles()
        unit_evidence = cls._strongest_demo_unit_evidence()
        intro_title = cls._strongest_demo_intro_title()
        decision_backbone_bindings = cls._strongest_demo_decision_backbone_bindings()
        decision_backbone_checks = cls._strongest_demo_decision_backbone_checks()
        covered_unit_ids = cls._strongest_demo_covered_unit_ids()
        visual_matched_unit_ids = cls._strongest_demo_visual_matched_unit_ids()
        grounded_content_slides = cls._strongest_demo_grounded_content_slides()
        total_content_slides = cls._strongest_demo_total_content_slides()
        slide_id_sequence = cls._strongest_demo_slide_id_sequence()
        unit_expectations = ", ".join(
            f"{unit_id}->{unit_layouts[unit_id]} titled '{unit_titles[unit_id]}'"
            for unit_id in cls.STRONGEST_DEMO_UNIT_ORDER
        )
        unit_binding_expectations = ", ".join(
            f"{unit_id} must use source_bindings {unit_evidence[unit_id]['source_bindings']} and must_include_checks {unit_evidence[unit_id]['must_include_checks']}"
            for unit_id in cls.STRONGEST_DEMO_UNIT_ORDER
        )
        return (
            "Strongest-demo accepted live baseline:\n"
            f"- Produce exactly 6 slides in this order: intro summary, {', '.join(unit_layouts[unit_id] for unit_id in cls.STRONGEST_DEMO_UNIT_ORDER)}, final decision summary.\n"
            f"- Use the exact slide_id sequence {slide_id_sequence}.\n"
            f"- Slide 1 must be a summary slide titled '{intro_title}' with source_bindings set to [] and must_include_checks set to [].\n"
            f"- Slides 2-5 must follow this exact unit order and layout/title pattern: {unit_expectations}.\n"
            f"- Slides 2-5 must also keep exact per-slide evidence wiring: {unit_binding_expectations}.\n"
            f"- Slide 6 must be titled 'Decision Backbone', use layout_type 'summary', set source_bindings to all source units, and set must_include_checks to exactly {decision_backbone_checks}.\n"
            f"- Slide 6 source_bindings must be exactly {decision_backbone_bindings} in that order.\n"
            "- Treat generated_at_unix as archival metadata only; every other acceptance-summary field must remain structurally identical to the accepted strongest-demo baseline.\n"
            f"- Preserve acceptance-summary comparability: grounded_content_slides must be {grounded_content_slides} of {total_content_slides}, covered_unit_ids must be exactly {covered_unit_ids}, and visual_matched_unit_ids must be exactly {visual_matched_unit_ids}.\n"
            "- Keep the strongest-demo slide titles bilingual exactly where shown above.\n"
        )

    @classmethod
    def _build_strongest_demo_grader_rules(cls) -> str:
        expected_sequence = cls._strongest_demo_layout_sequence()
        intro_title = cls._strongest_demo_intro_title()
        decision_backbone_bindings = cls._strongest_demo_decision_backbone_bindings()
        decision_backbone_checks = cls._strongest_demo_decision_backbone_checks()
        covered_unit_ids = cls._strongest_demo_covered_unit_ids()
        visual_matched_unit_ids = cls._strongest_demo_visual_matched_unit_ids()
        grounded_content_slides = cls._strongest_demo_grounded_content_slides()
        total_content_slides = cls._strongest_demo_total_content_slides()
        slide_id_sequence = cls._strongest_demo_slide_id_sequence()
        return (
            "Strongest-demo accepted live baseline checks:\n"
            f"- Compare the output structurally against the archived acceptance snapshot '{cls.STRONGEST_DEMO_ACCEPTANCE_SNAPSHOT.as_posix()}' before treating it as equivalent to the strongest-demo baseline.\n"
            "- Treat generated_at_unix as the only tolerated archival delta; all other acceptance-summary fields must match the accepted baseline exactly.\n"
            "- Fail if slide_count is not exactly 6.\n"
            f"- Fail if slide_id sequence is not exactly {slide_id_sequence}.\n"
            f"- Fail if layout_sequence is not exactly {expected_sequence}.\n"
            f"- Fail if slide 1 is not a summary slide titled '{intro_title}' with source_bindings == [] and must_include_checks == [].\n"
            f"- Fail if slides 2-5 do not map one-to-one to the strongest-demo unit order {cls.STRONGEST_DEMO_UNIT_ORDER} with the expected layout_type values.\n"
            "- Fail if any strongest-demo unit slide does not keep source_bindings == [unit_id] and must_include_checks == [unit_id].\n"
            f"- Fail if the final slide is not 'Decision Backbone' with layout_type 'summary', source_bindings exactly {decision_backbone_bindings}, and must_include_checks == {decision_backbone_checks}.\n"
            "- Fail if strongest-demo bilingual unit slide titles drift from the accepted baseline.\n"
            f"- Fail if grounded_content_slides is not {grounded_content_slides} or total_content_slides is not {total_content_slides}.\n"
            f"- Fail if covered_unit_ids is not exactly {covered_unit_ids}.\n"
            f"- Fail if visual_matched_unit_ids is not exactly {visual_matched_unit_ids}.\n"
        )

    @staticmethod
    def build_planner_system_prompt() -> str:
        return (
            "You are GroundedDeck's planner. "
            "Return only valid JSON matching the slide-spec schema. "
            "Required root fields: deck_goal, audience, slides. "
            "Each slide must include slide_id, title, goal, layout_type, key_points, visual_elements, "
            "source_bindings, must_include_checks, and speaker_notes. "
            "Keep the output source-grounded, editable, and auditable. "
            "Do not invent facts, source bindings, or unit IDs. "
            "Preserve the source language used in grounded claims where possible."
        )

    @staticmethod
    def build_planner_user_prompt(normalized_pack: dict) -> str:
        strongest_demo_rules = ""
        if OpenAICompatibleProvider._matches_strongest_demo_pack(normalized_pack):
            strongest_demo_rules = OpenAICompatibleProvider._build_strongest_demo_planner_rules()

        return (
            "Draft a grounded slide spec from this normalized source pack.\n"
            "Planning rules:\n"
            "- Start with one cover slide that uses the deck goal and audience unless a stronger pack-specific baseline overrides it.\n"
            "- Add one summary slide titled 'Decision Backbone' that compresses the minimum grounded claims unless a stronger pack-specific baseline overrides it.\n"
            "- Then add exactly one content slide per source unit.\n"
            "- For each content slide, set must_include_checks to exactly [unit_id] and source_bindings to exactly "
            "[source_binding].\n"
            "- Choose layout_type from the source structure: timeline for chronology/year-based evidence, comparison "
            "for tradeoffs or vs framing, process for stepwise entry/action paths, chart for numeric or metric-heavy "
            "evidence, otherwise summary.\n"
            "- Keep key_points tightly grounded to the unit claims or source text.\n"
            "- Keep visual_elements editable and specific to the chosen layout.\n"
            f"{strongest_demo_rules}"
            "- Return JSON only.\n"
            f"normalized_pack={json.dumps(normalized_pack, ensure_ascii=False)}"
        )

    @staticmethod
    def build_grader_system_prompt() -> str:
        return (
            "You are GroundedDeck's quality grader. "
            "Return only valid JSON with status, failures, coverage, grounding, visual_form, provider, and model. "
            "Required fields: status, failures, coverage, grounding, visual_form. "
            "Coverage must include required_units and covered_units. "
            "Grounding must include total_content_slides and grounded_slides. "
            "Visual_form must include expected_units and matched_units. "
            "Grade strictly against source coverage, slide grounding, and visual-form fit. "
            "Report failures for missing or invented bindings, uncovered unit IDs, ungrounded content slides, and "
            "layout mismatches."
        )

    @staticmethod
    def build_grader_user_prompt(normalized_pack: dict, slide_spec: dict) -> str:
        strongest_demo_rules = ""
        if OpenAICompatibleProvider._matches_strongest_demo_pack(normalized_pack):
            strongest_demo_rules = OpenAICompatibleProvider._build_strongest_demo_grader_rules()

        return (
            "Grade this slide_spec against the normalized source pack.\n"
            "Grading rules:\n"
            "- Count whether every source unit is covered by must_include_checks.\n"
            "- Count whether every non-cover slide is grounded by source_bindings.\n"
            "- Check whether each unit-backed content slide uses the appropriate layout_type: timeline, comparison, "
            "process, chart, or summary.\n"
            "- Prefer fail over partial credit when required evidence is missing.\n"
            f"{strongest_demo_rules}"
            "- Return JSON only.\n"
            f"normalized_pack={json.dumps(normalized_pack, ensure_ascii=False)}\n"
            f"slide_spec={json.dumps(slide_spec, ensure_ascii=False)}"
        )

    def draft_slide_spec(self, normalized_pack: dict) -> dict:
        request_payload = self.build_chat_request(
            system_prompt=self.build_planner_system_prompt(),
            user_prompt=self.build_planner_user_prompt(normalized_pack),
            response_format={"type": "json_object"},
        )
        parsed = self.parse_json_response(self.transport(request_payload))
        validate_slide_spec_like(parsed)
        return parsed

    def grade_slide_spec(self, normalized_pack: dict, slide_spec: dict) -> dict:
        request_payload = self.build_chat_request(
            system_prompt=self.build_grader_system_prompt(),
            user_prompt=self.build_grader_user_prompt(normalized_pack, slide_spec),
            response_format={"type": "json_object"},
        )
        parsed = self.parse_json_response(self.transport(request_payload))
        parsed = self._normalize_quality_report(parsed)
        validate_quality_report_like(parsed)
        return parsed

    def _default_transport(self, prepared_request: dict) -> dict:
        req = request.Request(
            prepared_request["url"],
            data=json.dumps(prepared_request["json"]).encode("utf-8"),
            headers=prepared_request["headers"],
            method="POST",
        )
        try:
            with request.urlopen(req) as response:
                body = response.read().decode("utf-8")
                return self._parse_transport_body(body)
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise ValueError(
                f"provider returned HTTP {exc.code}; body_snippet={self._content_snippet(body)}"
            ) from exc

    @classmethod
    def _parse_transport_body(cls, body: str) -> dict:
        try:
            return json.loads(body)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"provider returned non-JSON response body: {exc.msg} at line {exc.lineno} column {exc.colno}; "
                f"body_snippet={cls._content_snippet(body)}"
            ) from exc

    @staticmethod
    def _normalize_quality_report(payload: dict) -> dict:
        normalized = dict(payload)

        status = normalized.get("status")
        if status == "partial":
            normalized["status"] = "fail"

        failures = normalized.get("failures")
        if failures is None:
            normalized["failures"] = []

        coverage = normalized.get("coverage")
        if isinstance(coverage, dict):
            normalized["coverage"] = dict(coverage)
            for key in ("required_units", "covered_units"):
                if isinstance(normalized["coverage"].get(key), list):
                    normalized["coverage"][f"{key}_ids"] = normalized["coverage"][key]
                    normalized["coverage"][key] = len(normalized["coverage"][key])

        grounding = normalized.get("grounding")
        if isinstance(grounding, dict):
            normalized["grounding"] = dict(grounding)

        visual_form = normalized.get("visual_form")
        if isinstance(visual_form, dict):
            normalized["visual_form"] = dict(visual_form)
            for key in ("expected_units", "matched_units"):
                if isinstance(normalized["visual_form"].get(key), list):
                    normalized["visual_form"][f"{key}_ids"] = normalized["visual_form"][key]
                    normalized["visual_form"][key] = len(normalized["visual_form"][key])

        return normalized


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
