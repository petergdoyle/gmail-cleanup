# gmail-cleanup — Task Log

[Back to Backlog Index](./README.md)

Scoped work, newest first. The initial scaffold predates the structured log.

## Open & In-Progress Tasks

| ID | Summary | Area | Implements | Priority | Status | Created |
|----|---------|------|------------|----------|--------|---------|
| T04 | Add GitHub pull request checks | CI | — | medium | under review | 2026-11-20 |
| T03 | Design and implement authenticated per-user settings | Identity and settings | [E2](./E2-user-settings.md) | high | under review | 2026-11-19 |
| T02 | Plan future per-user settings, label selection and deployment discussion | Planning | [E2](./E2-user-settings.md), [E3](./E3-custom-label-selection.md), [D04](./design-decision-log.md) | medium | under review | 2026-11-19 |
| T01 | Implement safe Gmail cleanup via CLI and web UI | Cleanup | [E1](./E1-first-epic.md), F1.1–F1.4 | high | in progress | 2026-11-19 |

## Done

No structured tasks completed yet.

## Details

### T04 — GitHub pull request checks — UNDER REVIEW

- **Scope:** Run Python lint, tests and a web build for GitHub pull requests;
  no deployment or Google credentials are involved.
- **Raven candidate:** CI pipeline setup has no raven command yet; this workflow
  was added manually with the user's approval.
- **Verified:** Workflow YAML parses and declares the pull request trigger;
  locked Python lint and tests (38 passed), plus the web build, passed locally.
- **Verified on GitHub:** The first pull request run passed all three jobs.
  Action versions were updated afterward to address Node runtime warnings.

### T03 — Authenticated per-user settings — UNDER REVIEW

Implements [E2](./E2-user-settings.md), F2.1–F2.3; relates to
[D07](./design-decision-log.md).

- **Status:** Under review; login and Settings mockups approved.
- **Priority:** High.
- **Area:** Application identity, Gmail authorization, settings and UI.
- **Scope:** Pluggable login with a local-only development provider, separate Google account
  authorization, persistent isolated account and cleanup settings, light/dark
  theme, and visible signed-in user and sign-out. The operator configures the
  shared Google OAuth client. Shared Proxmox deployment is not part of this effort.
- **Acceptance:** Users cannot access each other's accounts or settings; settings
  persist across sessions; the UI explains Google connection setup and indicates
  the signed-in user. Existing CLI scripting behavior is preserved.
- **Framing:** [ADR 0002](../../architecture/decisions/0002-user-identity-and-settings.md)
  records the agreed identity and storage direction.
- **Verified:** Python lint and 33 tests; UI build; UI assets in a source-built
  wheel; isolated local lifecycle startup, health and shutdown. A browser
  exercise with a mocked Google backend covered sign-in, account connection,
  test connection, saved preferences, theme, preview, confirmation and sign-out.
- **Not verified:** Real Google authorization, Gmail operations, or Authentik;
  no real Gmail account was accessed. The local provider supports one configured
  development user, not shared deployment. Help & Docs remains backlog work.

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
