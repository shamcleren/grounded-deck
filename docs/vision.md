# Product Vision

[English](vision.md) | [简体中文](vision.zh-CN.md)

## Quality Bar

GroundedDeck targets NotebookLM-like presentation quality, which means all of the following should be true at the same time:

1. The system understands sources before it plans slides.
2. Each slide carries a clear claim or takeaway.
3. The deck has narrative progression instead of summary fragments.
4. The system chooses the right visual form for the information structure.
5. Facts, numbers, and claims stay traceable to source material.
6. The output remains editable in PowerPoint.
7. Chinese text and labels remain sharp and layout-stable.

## User Value

- Save high-cost thinking work, not only formatting time.
- Reduce hallucinated or untraceable claims in presentations.
- Compress large source packs into a presentation narrative.
- Support Chinese-heavy presentation workflows better than English-first tools.

## Differentiators

- Stronger editability than NotebookLM.
- Stronger Chinese readability and rendering stability than NotebookLM.
- Better content coverage control than generic AI PPT generators.
- Harness-engineered self-acceptance instead of subjective “looks good enough” review.

## Non-Goals

- A polished end-user UI in phase one.
- Full visual style coverage in phase one.
- Multi-user collaboration in phase one.

## Phase One Deliverables

- Stable repository boundaries and module ownership.
- A structured `slide spec` intermediate representation.
- Deterministic local self-acceptance commands.
- Clear insertion points for future ingestion, planning, and rendering work.
