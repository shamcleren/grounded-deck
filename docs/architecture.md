# Architecture

[English](architecture.md) | [简体中文](architecture.zh-CN.md)

## System Layers

### 1. Source Understanding

Accepts PDFs, DOCX, web pages, images, and tables, then extracts:

- heading hierarchy
- claims and conclusions
- metrics and numbers
- time information
- roles and object relationships
- candidate visual structures
- source bindings

### 2. Narrative Planner

Builds:

- presentation goal
- audience framing
- deck narrative path
- slide-level outline
- evidence that must be covered per slide

### 3. Visual Form Selector

Maps information structure to visual structure:

- temporal change -> timeline
- option differences -> comparison or matrix
- process steps -> flow
- concept decomposition -> hierarchy
- metric summary -> chart or number cards

### 4. Slide Spec Compiler

Produces the structured intermediate representation used by renderers and graders.

Required properties:

- auditable
- partially regenerable
- editable
- compatible with coverage and grounding checks

### 5. PPTX Renderer

Turns `slide spec` into editable PPTX output with these priorities:

- native text boxes
- native tables
- native charts where possible
- shape-based diagrams instead of screenshots
- explicit Chinese font defaults

### 6. Quality Harness

Provides machine-executable self-acceptance:

- repository completeness
- schema completeness
- eval completeness
- future deck artifact checks for coverage and grounding

## Data Flow

```text
Sources
  -> ingest
  -> planner
  -> visual selector
  -> slide spec
  -> renderer
  -> quality harness
  -> report
```

## Guardrails

- Do not treat long-form summarization as presentation planning.
- Do not push content understanding into the renderer.
- Do not output final PPT artifacts without an auditable intermediate form.
- Do not rely on image-heavy slide baking where editable native objects are possible.
- Do not ignore Chinese typography and layout stability.
