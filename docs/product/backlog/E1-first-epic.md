# E1 — Delete Old Gmail Messages

[← Back to Backlog Index](./README.md)

**Epic:** Implement CLI + Web UI to safely delete old messages from Gmail inbox
and archive by age threshold, with dry-run preview, confirmation, and credential
management.

---

## Features

### F1.1 — Gmail API Connection & Credential Management

| ID | Story | Acceptance Criteria | Priority | Tags | Status |
| ---- | ----- | ------------------- | -------- | ---- | ------ |
| S1.1.1 | Load Gmail API credentials from `.env` or admin override | Given a user has set `GMAIL_CREDENTIALS_PATH` in `.env` (or via web UI admin panel), when the CLI/web service starts, then it loads the OAuth token without error | High | cli, web, auth | Backlog |
| S1.1.2 | Implement OAuth flow or service-account auth setup guide | Given a user is new, when they run `gmail auth` or visit the admin tab, then they see clear instructions to set up Gmail API credentials (OAuth or service account) | High | cli, web, auth | Backlog |
| S1.1.3 | Test Gmail API connection (CLI + Web) | Given credentials are configured, when user runs `gmail test-connection` or clicks "Test Connection" in admin tab, then the tool verifies access and reports success/failure | High | cli, web, auth | Backlog |

### F1.2 — CLI Deletion Command

| ID | Story | Acceptance Criteria | Priority | Tags | Status |
| ---- | ----- | ------------------- | -------- | ---- | ------ |
| S1.2.1 | Implement `gmail delete` CLI command with mailbox + age options | Given a user runs `gmail delete --inbox --archive --inbox-age 6mo --archive-age 3mo`, then the CLI parses options, builds a deletion query, and reports the count of matching messages | High | cli | Backlog |
| S1.2.2 | Implement dry-run mode | Given a user runs `gmail delete ... --dry-run`, then the tool counts matching messages without deletion and shows the count and query criteria | High | cli | Backlog |
| S1.2.3 | Implement confirmation prompt before deletion | Given dry-run shows N messages will be deleted, when the user proceeds to live deletion, then the CLI prompts "Delete N messages? (yes/no)" and waits for confirmation | High | cli, safety | Backlog |
| S1.2.4 | Report deletion results | Given messages are deleted, when deletion completes, then the CLI reports: messages deleted count, errors (if any), and timestamp | High | cli | Backlog |

### F1.3 — Web UI Deletion Interface

| ID | Story | Acceptance Criteria | Priority | Tags | Status |
| ---- | ----- | ------------------- | -------- | ---- | ------ |
| S1.3.1 | Build mailbox + age selection form (inbox/archive toggles + date pickers) | Given a user opens the web UI, when they select mailboxes and age thresholds (default 6mo inbox, 3mo archive), then the form captures the selections | High | web, ui | Backlog |
| S1.3.2 | Implement "Preview" button to show dry-run results | Given a user configures mailbox/age and clicks "Preview", then the UI shows: count of matching messages, matching criteria, and a "Delete" button | High | web, ui | Backlog |
| S1.3.3 | Implement "Delete" button with confirmation modal | Given the preview shows N messages, when the user clicks "Delete", then a modal prompts "Permanently delete N messages?" with Cancel/Confirm buttons | High | web, ui, safety | Backlog |
| S1.3.4 | Show deletion progress and results | Given a user confirms deletion, then the UI shows: progress indicator (if applicable), completion status, count of messages deleted, and any errors | High | web, ui | Backlog |

### F1.4 — Admin Panel (Web UI)

| ID | Story | Acceptance Criteria | Priority | Tags | Status |
| ---- | ----- | ------------------- | -------- | ---- | ------ |
| S1.4.1 | Build admin tab with credential configuration UI | Given a user visits the admin tab, when they see a form to set/override `GMAIL_CREDENTIALS_PATH`, then they can enter a file path or select a file | Medium | web, auth | Backlog |
| S1.4.2 | Implement "Test Connection" button in admin tab | Given credentials are set/overridden, when the user clicks "Test Connection", then the UI calls the backend test endpoint and reports success/failure | High | web, auth | Backlog |
| S1.4.3 | Show current credential status in admin tab | Given a user visits the admin tab, when they see the current state (path, last-tested, connection status), then they can decide whether to reconfigure | Medium | web, auth | Backlog |

---

## Done When

- ✅ CLI command `gmail delete` accepts mailbox + age options, dry-run, and confirmation
- ✅ Web UI form captures mailbox/age selections with Preview + Delete flow
- ✅ Admin tab allows credential configuration and test connection (both CLI + Web)
- ✅ All acceptance criteria pass
- ✅ Tests pass (unit + integration with mock Gmail API)
- ✅ No hardcoded credentials in code or git
- ✅ `.env.example` documents required variables
