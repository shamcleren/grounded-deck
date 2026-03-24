from __future__ import annotations


def normalize_source_pack(raw_pack: dict) -> dict:
    source_units: list[dict] = []

    for source in raw_pack["sources"]:
        for section in source["sections"]:
            unit_id = f'{source["source_id"]}:{section["section_id"]}'
            claims = list(section.get("claims", []))
            text_parts = [section["heading"], *section.get("paragraphs", []), *claims]

            source_units.append(
                {
                    "unit_id": unit_id,
                    "source_id": source["source_id"],
                    "source_title": source["title"],
                    "section_id": section["section_id"],
                    "section_heading": section["heading"],
                    "unit_kind": "section-summary",
                    "language": source.get("language", raw_pack.get("language", "zh-CN")),
                    "text": " ".join(part.strip() for part in text_parts if part.strip()),
                    "claims": claims,
                    "source_binding": f'{source["source_id"]}:{section["section_id"]}',
                }
            )

    return {
        "pack_id": raw_pack["pack_id"],
        "deck_goal": raw_pack["deck_goal"],
        "audience": raw_pack["audience"],
        "source_units": source_units,
    }
