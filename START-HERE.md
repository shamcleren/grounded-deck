# Start Here

[English](START-HERE.md) | [简体中文](START-HERE.zh-CN.md)

Use this file when a new AI session needs to continue GroundedDeck quickly.

## 30-Second Startup

1. Read [AGENTS.md](AGENTS.md).
2. Read [docs/PROJECT-STATE.md](docs/PROJECT-STATE.md).
3. Read [docs/LATEST-HANDOFF.md](docs/LATEST-HANDOFF.md).
4. Run `make context`.

## What This Project Is

GroundedDeck is a local-first, source-grounded presentation system targeting NotebookLM-like deck quality with editable output and stronger Chinese support.

It is not:

- a prompt-only PPT generator
- a renderer-first project
- a generic slide template filler

## What To Do Next

Use the single item under `Current Next Action` in [docs/PROJECT-STATE.md](docs/PROJECT-STATE.md), unless [docs/LATEST-HANDOFF.md](docs/LATEST-HANDOFF.md) contains a more specific resume point from an unfinished task.

## Before Ending a Session

- update [docs/LATEST-HANDOFF.md](docs/LATEST-HANDOFF.md)
- update [docs/TASK-BOARD.md](docs/TASK-BOARD.md)
- update [docs/PROJECT-STATE.md](docs/PROJECT-STATE.md) if project state changed
- run `make eval`
