# Backlog

Epics and running logs for gmail-cleanup. Authored as **Epic → Feature → Story**
Markdown: each epic is a file (`E{n}-{slug}.md`), features are `### F{n}.{m}`
headings, and stories are rows in a six-column table.

## Format

```markdown
# E1 — Title
**Epic:** One-line summary.

### F1.1 — Feature Title

| ID | Story | Acceptance Criteria | Priority | Tags | Status |
| ---- | ----- | ------------------- | -------- | ---- | ------ |
| S1.1.1 | As a …, I can … | Given/When/Then | High | ai-assisted | Backlog |
```

- **Status:** `Done`/`Resolved` · `Active` · `Backlog` · `Superseded`.
- **Priority:** `High` · `Medium` · `Low`.
- **Tags:** `ai-assisted`, `human-authored`, `test-only`, `spike`, `tech-debt`,
  `nfr`, `infra` (controlled vocabulary).

## Epics

| Epic | Title | Description | Status |
|------|-------|-------------|--------|
| [E1](./E1-first-epic.md) | Delete Old Gmail Messages | CLI + Web UI to safely delete old messages from Gmail inbox/archive by age, with dry-run, confirmation, and credential management | Backlog |

## Logs

| Log | Purpose |
|-----|---------|
| [`task-log.md`](./task-log.md) | Chronological record of completed work, newest first |
| [`bug-log.md`](./bug-log.md) | Defects found and their resolution |
| [`design-decision-log.md`](./design-decision-log.md) | Lightweight decisions not large enough for a full ADR |
