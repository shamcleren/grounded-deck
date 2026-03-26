# Architecture Decisions

[English](ARCHITECTURE-DECISIONS.md) | [简体中文](ARCHITECTURE-DECISIONS.zh-CN.md)

## Fixed Invariants

These decisions should not drift silently:

1. GroundedDeck is a source-grounded presentation system, not a generic prompt-only PPT generator.
2. `slide spec` is the stable contract between planning, rendering, and grading.
3. The renderer must not own source understanding.
4. Editability is a required product property, not an optional enhancement.
5. Chinese rendering quality is a required product property, not a polish pass.
6. Harness engineering is part of the product architecture, not a sidecar test layer.

## Decision Log

### AD-0001: Repository-as-memory

- Status: accepted
- Why: AI-driven development will span many sessions, so project continuity must live in the repository rather than chat history.
- Consequence: `AGENTS.md`, `docs/PROJECT-STATE.md`, and this file become canonical context for future sessions.

### AD-0002: Intermediate representation first

- Status: accepted
- Why: direct slide generation causes dropped content, poor editability, and weak auditability.
- Consequence: all meaningful generation should converge on `slide spec` before rendering.

### AD-0003: Anti-drift quality gates

- Status: accepted
- Why: long-running AI implementation tends to drift toward convenience unless guarded by explicit checks.
- Consequence: harness rules must evolve alongside architecture and must block missing continuity artifacts.

### AD-0004: Source understanding via LLM deep comprehension

- Status: accepted
- Why: GroundedDeck targets NotebookLM-level quality. Without thorough understanding of source materials, the system cannot make intelligent decisions about what to present and how to visualize it. Simple format conversion is not enough.
- Consequence: The ingest layer must use LLM to deeply understand source documents — extracting conclusions, claims, data, logical relationships, and candidate visual structures. The JSON source pack is an internal intermediate format that users never touch; it is automatically generated from raw documents.

### AD-0005: Progressive format support starting with Markdown

- Status: accepted
- Why: The architecture supports PDF, DOCX, web pages, images, and tables as stated in the architecture doc. But implementation should be incremental — start with the simplest text structure (Markdown) and progressively add more formats.
- Consequence: Markdown is the first supported input format. Each new format is a new ingest adapter that produces the same internal source pack structure. The pipeline downstream of source pack remains format-agnostic.

### AD-0006: Dual diagram capability (data charts + concept diagrams)

- Status: accepted
- Why: A presentation system that truly understands content must be able to generate both data visualizations (bar charts, line charts, pie charts) and conceptual diagrams (flowcharts, architecture diagrams, mind maps). Both are essential for effective communication.
- Consequence: The visual selector and renderer must support two categories of visual output: (1) data charts driven by numeric data, and (2) concept diagrams driven by structural/relational information. Both should be generated based on deep understanding of the source material.

### AD-0007: LLM-driven planning strategy

- Status: accepted
- Why: Whether to use single-pass or multi-step LLM calls for source understanding and planning should be determined by quality, not by implementation convenience. The system should use whichever approach produces better results.
- Consequence: The provider abstraction already supports both deterministic and LLM-backed paths. The LLM planning strategy (single-pass vs multi-step) is an implementation detail that can be optimized based on empirical quality comparison. The deterministic baseline serves as the quality floor.

### AD-0008: Testing strategy — developer CLI (A) + internal step-by-step (B)

- Status: accepted
- Why: End users (the project owner) test via CLI with a single command that runs the full pipeline. But internal development testing should be step-by-step to isolate issues at each stage (understanding → planning → rendering).
- Consequence: The CLI provides a single-command end-to-end path for user testing. Internally, the pipeline remains decomposed into testable stages, and the eval harness validates each stage independently.

## Change Policy

If a future change alters a fixed invariant or changes the module split, record a new decision entry in this file and update [docs/PROJECT-STATE.md](PROJECT-STATE.md).
