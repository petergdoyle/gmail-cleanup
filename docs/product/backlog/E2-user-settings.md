# E2 — Persistent Per-User Settings

[Back to Backlog Index](./README.md)

**Epic:** Provide each authenticated user with durable, isolated account,
cleanup and appearance settings, plus access to help and documentation.

The next local-development effort implements pluggable application login with
an explicitly local-only development provider (Authentik/OIDC is deferred),
separate Google authorization and persistent per-user settings. Use SQLite for
per-user records and an operator-supplied key for encrypted Google refresh
tokens. The operator configures the shared Google OAuth client; users connect
their own Google accounts. Implementation details and shared deployment remain
subject to design and review ([D04](./design-decision-log.md)); no shared-server
deployment is implied. Settings replaces the current local Admin surface. The
supplied UI example informs the visible login, Settings and Help & Docs
navigation; **View as** is out of scope.

## Features

### F2.1 — User Identity and Isolation

| ID | Story | Acceptance Criteria | Priority | Tags | Status |
| ---- | ----- | ------------------- | -------- | ---- | ------ |
| S2.1.1 | As a user, I can see my signed-in identity and sign out | Given an authenticated session, when I open the app, then my identity and a sign-out action are visible | High | ai-assisted | Backlog |
| S2.1.2 | As a user, my settings and connected accounts remain private | Given two different users, when either reads or changes their settings or accounts, then the other user's settings and credentials are inaccessible | High | nfr | Backlog |
| S2.1.3 | As an operator, I can manage sessions securely | Given the agreed deployment identity model, when a session expires or the user signs out, then protected operations require a valid authenticated session | High | nfr | Backlog |

### F2.2 — Connected Accounts and Cleanup Preferences

| ID | Story | Acceptance Criteria | Priority | Tags | Status |
| ---- | ----- | ------------------- | -------- | ---- | ------ |
| S2.2.1 | As a user, I can manage my connected Google accounts in Settings | Given my signed-in user, when I connect, view or remove an account, then the change applies only to my user and persists across sessions | High | ai-assisted | Backlog |
| S2.2.2 | As a user, I can save cleanup settings for each account | Given a connected account, when I save mailbox selections and age or date criteria, then reopening or signing back in restores that account's saved settings | High | ai-assisted | Backlog |
| S2.2.3 | As a user, I can review saved settings before they affect mail | Given saved preferences, when I start cleanup, then the account and criteria are visible and preview and confirmation are still required | High | nfr | Backlog |
| S2.2.4 | As a user, I can securely reauthorize an account | Given an expired or revoked authorization, when I reconnect the account, then I receive an actionable error and can authorize without exposing tokens | High | nfr | Backlog |

### F2.3 — Appearance and Navigation

| ID | Story | Acceptance Criteria | Priority | Tags | Status |
| ---- | ----- | ------------------- | -------- | ---- | ------ |
| S2.3.1 | As a user, I can choose a light or dark theme | Given Settings, when I choose light or dark, then the UI applies that theme and restores my choice in a later session | Medium | ai-assisted | Backlog |
| S2.3.2 | As a user, I can find my settings and help | Given any primary app screen, when I navigate, then Settings and Help & Docs are available with my signed-in identity; no View as control is added | Medium | ai-assisted | Backlog |
| S2.3.3 | As a user, I can open task-oriented help | Given Help & Docs, when I need guidance for connecting accounts, previewing cleanup or recovering mail, then I can reach the relevant user documentation | Medium | ai-assisted | Backlog |

### F2.4 — Deployment Design Prerequisite

| ID | Story | Acceptance Criteria | Priority | Tags | Status |
| ---- | ----- | ------------------- | -------- | ---- | ------ |
| S2.4.1 | As a maintainer, I can choose a shared deployment model | Given the existing homelab provisioning and configuration process, when alternatives are reviewed, then identity, secure credential storage, persistence, backups and operations are documented and the human approves the architecture | High | infra | Backlog |
| S2.4.2 | As a maintainer, I can evaluate deployment automation | Given the existing custom deployment stack and candidate GitHub Actions approaches, when alternatives are evaluated, then permissions, secrets, private connectivity and operational trade-offs are recorded before a choice is made | Medium | spike | Backlog |

## Done When

- [ ] Local identity and persistence decisions are made before implementation;
  shared deployment remains a separate decision.
- [ ] User settings and connected accounts persist and are isolated per user.
- [ ] Cleanup still requires a user-visible preview and confirmation.
- [ ] Theme, signed-in identity, sign-out, Settings and Help & Docs work as agreed.
- [ ] Tests cover persistence, user isolation and the chosen deployment model.
- [ ] UI changes have reviewed mockups and task-oriented user documentation.
