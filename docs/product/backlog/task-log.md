# gmail-cleanup — Task Log

[Back to Backlog Index](./README.md)

Scoped work, newest first. The initial scaffold predates the structured log.

## Open & In-Progress Tasks

| ID | Summary | Area | Implements | Priority | Status | Created |
|----|---------|------|------------|----------|--------|---------|
| T02 | Plan future per-user settings, label selection and deployment discussion | Planning | [E2](./E2-user-settings.md), [E3](./E3-custom-label-selection.md), [D04](./design-decision-log.md) | medium | under review | 2026-11-19 |
| T01 | Implement safe Gmail cleanup via CLI and web UI | Cleanup | [E1](./E1-first-epic.md), F1.1–F1.4 | high | in progress | 2026-11-19 |

## Done

No structured tasks completed yet.

## Details

### T02 — Plan future settings, label selection and deployment discussion — UNDER REVIEW

Plans [E2](./E2-user-settings.md) and [E3](./E3-custom-label-selection.md);
relates to [D04](./design-decision-log.md) and [D06](./design-decision-log.md).

- **Status:** Under review; backlog and deployment options await human review.
- **Priority:** Medium.
- **Area:** Planning.
- **Scope:** Capture user-specific settings, connected accounts, theme, identity,
  Help & Docs, custom label selection and deployment design prerequisites without
  implementing them.
- **Acceptance:** The future epic and deferred deployment discussion are reviewable
  and do not claim a chosen deployment model.
- **Verified:** The candidate deployment Mermaid diagram parsed with Mermaid.
  CLI and UI label-overlap warnings were added; Python lint, all 29 tests and
  the UI build passed. Updated mockup SVGs parsed and their PNGs were reviewed.
- **Not verified:** Shared deployment, authentication, persistence, and
  GitHub Actions connectivity have not been implemented or exercised.

### T01 — Implement safe Gmail cleanup via CLI and web UI — IN PROGRESS

Implements [E1](./E1-first-epic.md), F1.1–F1.4.

- **Status:** In progress; revised multi-account mockups approved on 2026-11-19.
  Implementation is ready for review, pending live Gmail verification.
- **Priority:** High.
- **Area:** Gmail API, CLI, web UI.
- **Branch:** `feat/e1-delete-old-messages`.
- **Scope:** Connect and navigate multiple Google accounts; preview and move
  eligible inbox and archived received messages in the selected account to Gmail
  Trash; configure OAuth and test connectivity through the CLI and web UI. Add
  local `make dev-up`, `dev-down`, and `dev-status` targets. Preserve each
  account's selections while the UI is open.
- **Acceptance:** The approved epic is implemented and verified; recovery uses
  Gmail Trash; the user reviews the mockups before UI implementation.
- **Verified:** `make lint`; `make test` (29 tests); React build; source-built
  wheel contains UI assets; `make dev-up`, health, `dev-status`, and `dev-down`.
  A browser exercise against a mocked Gmail backend checked account navigation,
  retained settings, preview invalidation, date queries, confirmation, and results.
- **Not verified:** Real Google authorization, Keychain storage, Gmail API
  matching, or moving and recovering real messages; no live account was accessed.
- **Deferred:** Proxmox/Docker deployment and remote access; see
  [D04](./design-decision-log.md).

## Earlier entries

| Date | Task | Epic | Notes |
|------|------|------|-------|
| _date_ | Initial scaffold | — | Project scaffolded by raven (stack skeleton + docs tree + working model). |
