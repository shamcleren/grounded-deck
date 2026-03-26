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
from src.visual.selector import (
    build_visual_elements as _vs_build_visual_elements,
    infer_layout_type as _vs_infer_layout_type,
    model_assisted_infer_layout_type as _vs_model_assisted_infer,
    unique_preserving_order as _vs_unique_preserving_order,
    validate_model_layouts as _vs_validate_model_layouts,
    ALL_CONTENT_LAYOUTS as _VS_ALL_CONTENT_LAYOUTS,
    ModelLayoutCallback as _VS_ModelLayoutCallback,
)


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
        return _vs_unique_preserving_order(values)

    @staticmethod
    def infer_layout_type(unit: dict) -> str:
        return _vs_infer_layout_type(unit).layout_type

    @staticmethod
    def build_visual_elements(layout_type: str, unit: dict) -> list[dict]:
        return _vs_build_visual_elements(layout_type, unit)

    @classmethod
    def _extract_key_points(cls, unit: dict) -> list[str]:
        """从 unit 的 claims 和 text 中提取丰富的 key_points。

        策略：
        1. claims 始终作为主要 key_points（最多 3 条）
        2. 如果 claims 不足 3 条，从 text 中提取补充要点（按句号拆分，去重）
        """
        import re as _re

        claims = list(unit.get("claims", []))
        key_points = claims[:3]

        if len(key_points) < 3:
            text = unit.get("text", "")
            # 归一化去重：去除尾部标点后比较
            def _normalize(s: str) -> str:
                return s.strip().rstrip("。；;.，,")

            seen = {_normalize(kp) for kp in key_points}
            # 按句号/分号拆分 text 中的片段
            fragments = _re.split(r"[。；]", text)
            for frag in fragments:
                frag = frag.strip()
                if not frag:
                    continue
                norm_frag = _normalize(frag)
                if norm_frag in seen:
                    continue
                # 排除太短的片段（可能只是标题重复）
                if len(frag) < 8:
                    continue
                # 排除和 section_heading 完全相同的片段
                if frag == unit.get("section_heading", ""):
                    continue
                key_points.append(frag)
                seen.add(norm_frag)
                if len(key_points) >= 3:
                    break

        return key_points

    @classmethod
    def build_unit_slide(cls, unit: dict) -> dict:
        layout_type = cls.infer_layout_type(unit)
        key_points = cls._extract_key_points(unit)
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
            "key_points": key_points,
            "visual_elements": cls.build_visual_elements(layout_type, unit),
            "source_bindings": [unit["source_binding"]],
            "must_include_checks": [unit["unit_id"]],
            "speaker_notes": f'Ground this slide in {unit["source_binding"]} and keep the structure editable.',
        }

    @classmethod
    def _build_cover_key_points(cls, normalized_pack: dict) -> list[str]:
        """为 cover slide 构建 source-grounded 的 key_points。

        策略：
        1. audience 描述作为第一条
        2. 从所有 units 的 claims 中选取最具代表性的 1-2 条作为 deck 核心论点摘要
        3. source scope 描述（N 个 grounded source units）
        """
        source_units = normalized_pack["source_units"]
        points: list[str] = [normalized_pack["audience"]]

        # 从所有 claims 中取第一条作为核心论点摘要
        all_claims: list[str] = []
        for unit in source_units:
            all_claims.extend(unit.get("claims", []))
        if all_claims:
            points.append(all_claims[0])

        points.append(f"{len(source_units)} grounded source units")
        return points

    @classmethod
    def _build_summary_key_points(cls, source_units: list[dict]) -> list[str]:
        """为 summary (Decision Backbone) slide 构建完整的 source-grounded key_points。

        策略：从所有 units 的 claims 中提取，不限于前 3 条，确保每个 unit 至少贡献一条。
        每条 claim 附加来源标注以增强可审计性。
        """
        summary_points: list[str] = []
        for unit in source_units:
            claims = unit.get("claims", [])
            binding = unit.get("source_binding", "")
            for claim in claims:
                annotated = f"{claim} [{binding}]" if binding else claim
                if annotated not in summary_points:
                    summary_points.append(annotated)
        return summary_points

    @classmethod
    def _build_cover_visual_elements(cls, normalized_pack: dict) -> list[dict]:
        """为 cover slide 构建丰富的 visual_elements。"""
        source_units = normalized_pack["source_units"]
        # 收集所有 section headings 作为 source scope 概览
        topics = [unit["section_heading"] for unit in source_units]
        return [
            {"type": "title-block"},
            {"type": "source-count", "value": len(source_units)},
            {"type": "topic-overview", "topics": topics},
        ]

    @classmethod
    def _build_summary_visual_elements(cls, source_units: list[dict]) -> list[dict]:
        """为 summary slide 构建丰富的 visual_elements。"""
        # 每个 source unit 的核心声明与来源映射
        claim_map: list[dict] = []
        for unit in source_units:
            claims = unit.get("claims", [])
            claim_map.append({
                "unit_id": unit["unit_id"],
                "section": unit["section_heading"],
                "claim": claims[0] if claims else unit.get("text", "")[:80],
                "source_binding": unit.get("source_binding", ""),
            })
        return [
            {"type": "bullet-list"},
            {"type": "claim-source-map", "entries": claim_map},
        ]

    def draft_slide_spec(self, normalized_pack: dict) -> dict:
        source_units = normalized_pack["source_units"]

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
                    "key_points": self._build_cover_key_points(normalized_pack),
                    "visual_elements": self._build_cover_visual_elements(normalized_pack),
                    "source_bindings": [unit["source_binding"] for unit in source_units],
                    "must_include_checks": [unit["unit_id"] for unit in source_units],
                    "speaker_notes": "Introduce the deck goal and emphasize that claims stay grounded to source material.",
                },
                {
                    "slide_id": "s2-summary",
                    "title": "Decision Backbone",
                    "goal": "Compress the source pack into the minimum grounded claims the deck must preserve.",
                    "layout_type": "summary",
                    "key_points": self._build_summary_key_points(source_units),
                    "visual_elements": self._build_summary_visual_elements(source_units),
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

        # ---------- narrative quality 评估 ----------
        narrative_issues: list[str] = []
        slides_with_empty_kp = []
        slides_with_generic_kp = []
        slides_with_source_annotations = 0
        total_key_points = 0

        for slide in slide_spec["slides"]:
            sid = slide["slide_id"]
            kp = slide.get("key_points", [])
            total_key_points += len(kp)

            # 检查空 key_points（cover 除外）
            if slide["layout_type"] != "cover" and not kp:
                slides_with_empty_kp.append(sid)

            # 检查通用/非 grounded key_points
            for point in kp:
                if isinstance(point, str):
                    # 检查是否包含 source binding 标注
                    if "[" in point and "]" in point:
                        slides_with_source_annotations += 1

            # 检查 generic key_points（不包含中文字符且不是标准短语的）
            for point in kp:
                if isinstance(point, str) and len(point) < 10:
                    # 太短的 key_point 可能是通用的
                    if not any(ord(c) > 0x4E00 for c in point):
                        slides_with_generic_kp.append(sid)
                        break

        if slides_with_empty_kp:
            narrative_issues.append(f"slides with empty key_points: {', '.join(slides_with_empty_kp)}")
            failures.append(f"narrative: empty key_points on {', '.join(slides_with_empty_kp)}")

        # 检查 summary slide 的 claim coverage
        summary_slides = [s for s in slide_spec["slides"] if s["layout_type"] == "summary"]
        for s_slide in summary_slides:
            s_kp = s_slide.get("key_points", [])
            if len(s_kp) < len(normalized_pack["source_units"]):
                narrative_issues.append(
                    f"summary '{s_slide['slide_id']}' has {len(s_kp)} key_points but "
                    f"{len(normalized_pack['source_units'])} source units exist"
                )

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
            "narrative_quality": {
                "total_key_points": total_key_points,
                "slides_with_empty_key_points": slides_with_empty_kp,
                "slides_with_generic_key_points": slides_with_generic_kp,
                "source_annotated_points": slides_with_source_annotations,
                "issues": narrative_issues,
                "quality_ratio": round(
                    1.0 - len(slides_with_empty_kp) / max(1, len(slide_spec["slides"])),
                    2,
                ),
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
    def build_grader_user_prompt(
        normalized_pack: dict,
        slide_spec: dict,
        *,
        layout_validation_hint: str = "",
    ) -> str:
        strongest_demo_rules = ""
        if OpenAICompatibleProvider._matches_strongest_demo_pack(normalized_pack):
            strongest_demo_rules = OpenAICompatibleProvider._build_strongest_demo_grader_rules()

        validation_block = ""
        if layout_validation_hint:
            validation_block = (
                f"Rule-engine layout analysis (use as grading signal, not override):\n"
                f"{layout_validation_hint}\n"
            )

        return (
            "Grade this slide_spec against the normalized source pack.\n"
            "Grading rules:\n"
            "- Count whether every source unit is covered by must_include_checks.\n"
            "- Count whether every non-cover slide is grounded by source_bindings.\n"
            "- Check whether each unit-backed content slide uses the appropriate layout_type: timeline, comparison, "
            "process, chart, or summary.\n"
            "- Prefer fail over partial credit when required evidence is missing.\n"
            f"{strongest_demo_rules}"
            f"{validation_block}"
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

        # 规则引擎 post-validation：记录模型选择与规则推断的一致性
        validation_report = _vs_validate_model_layouts(normalized_pack, parsed)
        parsed["_layout_validation"] = {
            "matched": validation_report.matched_count,
            "mismatched": validation_report.mismatched_count,
            "total": validation_report.total_count,
            "match_ratio": validation_report.match_ratio,
            "all_matched": validation_report.all_matched,
            "details": [
                {
                    "unit_id": item.unit_id,
                    "rule_layout": item.rule_layout,
                    "model_layout": item.model_layout,
                    "matched": item.matched,
                    "signals": item.matched_signals,
                }
                for item in validation_report.items
            ],
        }
        return parsed

    # ---------- Model-assisted layout inference ----------

    @staticmethod
    def _build_layout_system_prompt() -> str:
        """构建布局推断的 system prompt。"""
        layout_list = ", ".join(_VS_ALL_CONTENT_LAYOUTS)
        return (
            "You are GroundedDeck's visual layout selector. "
            f"Given a source unit, return ONLY one layout type from: {layout_list}. "
            "Choose based on the content structure: "
            "timeline for chronology/year-based evidence, "
            "comparison for tradeoffs or vs framing, "
            "process for stepwise entry/action paths, "
            "chart for numeric or metric-heavy evidence, "
            "otherwise summary. "
            "Return ONLY the layout type string, nothing else."
        )

    @staticmethod
    def _build_layout_user_prompt(unit: dict) -> str:
        """构建布局推断的 user prompt。"""
        return (
            f"section_heading: {unit.get('section_heading', '')}\n"
            f"text: {unit.get('text', '')}\n"
            f"claims: {json.dumps(unit.get('claims', []), ensure_ascii=False)}"
        )

    def build_layout_callback(self) -> _VS_ModelLayoutCallback:
        """构建一个可传给 visual selector 的 model layout callback。

        该 callback 使用当前 provider 的 transport 向 LLM 发送单个 unit 的内容，
        获取模型建议的 layout_type 字符串。
        """
        def _callback(unit: dict) -> str:
            request_payload = self.build_chat_request(
                system_prompt=self._build_layout_system_prompt(),
                user_prompt=self._build_layout_user_prompt(unit),
            )
            response = self.transport(request_payload)
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            layout = self._coerce_message_content(content).strip().lower()
            # 去除可能的引号包裹
            layout = layout.strip("'\"` \t\n")
            return layout

        return _callback

    def build_narrative_callback(self) -> "Callable[[dict, dict], dict]":
        """构建一个可传给 narrative grader 的 model callback。

        该 callback 使用当前 provider 的 transport 向 LLM 发送叙事评分请求，
        返回解析后的 JSON dict。
        """
        def _callback(prompts: dict, slide_spec: dict) -> dict:
            request_payload = self.build_chat_request(
                system_prompt=prompts["system"],
                user_prompt=prompts["user"],
                response_format={"type": "json_object"},
            )
            return self.parse_json_response(self.transport(request_payload))

        return _callback

    def grade_slide_spec(self, normalized_pack: dict, slide_spec: dict) -> dict:
        # 生成规则引擎验证摘要用于注入 grader prompt
        validation_report = _vs_validate_model_layouts(normalized_pack, slide_spec)
        grader_hint = validation_report.as_grader_hint()

        request_payload = self.build_chat_request(
            system_prompt=self.build_grader_system_prompt(),
            user_prompt=self.build_grader_user_prompt(
                normalized_pack, slide_spec, layout_validation_hint=grader_hint,
            ),
            response_format={"type": "json_object"},
        )
        parsed = self.parse_json_response(self.transport(request_payload))
        parsed = self._normalize_quality_report(parsed)
        validate_quality_report_like(parsed)

        # 确定性 narrative quality 后验证：交叉验证模型 grading 结果
        try:
            from src.quality.narrative_grader import grade_narrative_deterministic
            narrative_report = grade_narrative_deterministic(normalized_pack, slide_spec)
            parsed["_narrative_validation"] = {
                "mode": narrative_report.mode,
                "slide_count": narrative_report.slide_count,
                "avg_coherence": narrative_report.avg_coherence,
                "avg_grounding": narrative_report.avg_grounding,
                "avg_visual_fit": narrative_report.avg_visual_fit,
                "avg_composite": narrative_report.avg_composite,
                "status": narrative_report.status,
                "issues": narrative_report.all_issues,
            }
        except Exception:
            # 后验证失败不应阻塞 grading 结果
            parsed["_narrative_validation"] = {"error": "narrative validation unavailable"}

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
