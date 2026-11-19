# gmail-cleanup — Documentation

a utility to clear out old gmail items

This is the project's documentation tree. It follows the suite's standard
taxonomy so the project reads consistently and stays legible to people who don't
read the code. Work is **architecture-first**: the docs that frame an effort exist
before the code that realizes them.

Start with [why & how](architecture/00-why.md), then the
[backlog](product/backlog/README.md).

## Documentation Map

| Area | What lives here |
|------|-----------------|
| [`architecture/`](architecture/) | System design — the "why" and "how" — plus ADRs for significant decisions |
| [`product/`](product/) | The backlog (epics + logs) and the journeys the project serves |
| [`operations/`](operations/) | How to set up, run, publish and operate the project: environment setup, procedures, deployment, runbooks |
| [`ai/`](ai/) | **How we work with an AI coding agent** — the working relationship, the effort workflow, the docs guide, decision capture, and directives (the vendored working model) |

`help/` and `stakeholders/` are added when content for them exists (end-user help,
ecosystem positioning) — following the taxonomy in
[`ai/workflow/01-docs-structure.md`](ai/workflow/01-docs-structure.md).

This tree is also the **publish surface**: **markdown-tools** pushes it to
Confluence (`md2conf`) and the backlog to Jira (`md2jira`). Its settings
(`markdown-to-*.toml`) and drift state (`.md2conf/`, `.md2jira/`) are committed;
`.env` is not — see
[`ai/directives/publishing-config-and-state.md`](ai/directives/publishing-config-and-state.md).

## Conventions

- **Numbered files** (`00-…`, `01-…`) order documents within a folder.
- **Each folder has a `README.md`** acting as its index.
- **Backlog epics** are `E{n}-{slug}.md`; running logs are `task-log.md`,
  `bug-log.md`, `design-decision-log.md`.
- Plain Markdown throughout.

## Current Focus

Scaffolded by raven. Fill in the first architecture doc and the
foundational ADR, then grow the backlog. Follow the loop in
[`ai/`](ai/README.md): architecture → plan → implement → update progress.
