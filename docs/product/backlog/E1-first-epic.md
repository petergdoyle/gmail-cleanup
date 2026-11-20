# E1 — Delete Old Gmail Messages

[← Back to Backlog Index](./README.md)

**Epic:** Implement CLI + Web UI to safely delete old messages from Gmail inbox
and archive by age threshold, with dry-run preview, confirmation, and credential
management.

Archive means received mail outside Inbox, Sent, Drafts, Spam, and Trash.
Cleanup moves messages to Gmail Trash; recovery is performed in Gmail.
Users can connect multiple Google accounts and navigate each account's Inbox
and Archive, with both selected by default and their respective age defaults.
Each preview and confirmation identifies the affected account.
The [UI mockups](../mockups/README.md) require human review before UI coding.

---

## Features

### F1.1 — Gmail API Connection & Credential Management

| ID | Story | Acceptance Criteria | Priority | Tags | Status |
| ---- | ----- | ------------------- | -------- | ---- | ------ |
| S1.1.1 | Load Gmail API credentials from `.env` or admin override | Given a user has set `GMAIL_CREDENTIALS_PATH` in `.env` (or via web UI admin panel), when the CLI/web service starts, then it loads the OAuth client configuration | High | ai-assisted | Active |
| S1.1.2 | Implement OAuth setup and provide a setup guide | Given a user is new, when they follow the setup guide and run `gmail auth` or add an account in Admin, then they can authorize a Google account | High | ai-assisted | Active |
| S1.1.3 | Test Gmail API connection (CLI + Web) | Given credentials are configured, when user runs `gmail test-connection` or clicks "Test Connection" in admin tab, then the tool verifies access and reports success/failure | High | ai-assisted | Active |
| S1.1.4 | Connect and select Google accounts | Given multiple authorized Google accounts, when a user selects an account in the CLI or web UI, then previews, connection tests, and cleanup apply to the selected account and identify it | High | ai-assisted | Active |

### F1.2 — CLI Deletion Command

| ID | Story | Acceptance Criteria | Priority | Tags | Status |
| ---- | ----- | ------------------- | -------- | ---- | ------ |
| S1.2.1 | Implement `gmail delete` CLI command with mailbox + age options | Given a user selects an account and runs `gmail delete --inbox --archive --inbox-age 6mo --archive-age 3mo`, then the CLI parses options, builds a deletion query, and reports the count of matching messages | High | ai-assisted | Active |
| S1.2.2 | Implement dry-run mode | Given a user runs `gmail delete ... --dry-run`, then the tool counts matching messages without deletion and shows the count and query criteria | High | ai-assisted | Active |
| S1.2.3 | Implement confirmation prompt before deletion | Given a preview shows N messages, when the user proceeds to live cleanup, then the CLI prompts for confirmation unless the user explicitly passes `--yes` | High | ai-assisted | Active |
| S1.2.4 | Report deletion results | Given messages are moved to Trash, when cleanup completes, then the CLI reports the count and timestamp; a failure reports the partial count | High | ai-assisted | Active |

### F1.3 — Web UI Deletion Interface

| ID | Story | Acceptance Criteria | Priority | Tags | Status |
| ---- | ----- | ------------------- | -------- | ---- | ------ |
| S1.3.1 | Build mailbox + age selection form (inbox/archive toggles + date pickers) | Given a user opens the web UI, when they select mailboxes and age thresholds (default 6mo inbox, 3mo archive), then the form captures the selections | High | ai-assisted | Active |
| S1.3.2 | Implement "Preview" button to show dry-run results | Given a user configures mailbox/age and clicks "Preview", then the UI shows: count of matching messages, matching criteria, and a button to move them to Trash | High | ai-assisted | Active |
| S1.3.3 | Implement "Delete" button with confirmation modal | Given the preview shows N messages, when the user clicks "Delete", then a modal asks to move N messages to Gmail Trash with Cancel/Confirm buttons | High | ai-assisted | Active |
| S1.3.4 | Show deletion progress and results | Given a user confirms deletion, then the UI shows: progress indicator (if applicable), completion status, count of messages deleted, and any errors | High | ai-assisted | Active |
| S1.3.5 | Navigate accounts and their mailboxes | Given multiple connected accounts, when a user selects or moves to another account, then the UI shows its Inbox and Archive selections with defaults of 6 and 3 months, and identifies the account in preview and confirmation | High | ai-assisted | Active |

### F1.4 — Admin Panel (Web UI)

| ID | Story | Acceptance Criteria | Priority | Tags | Status |
| ---- | ----- | ------------------- | -------- | ---- | ------ |
| S1.4.1 | Build admin tab with credential configuration UI | Given a user visits the admin tab, when they see a form to set/override `GMAIL_CREDENTIALS_PATH`, then they can enter a file path or select a file | Medium | ai-assisted | Active |
| S1.4.2 | Implement "Test Connection" button in admin tab | Given credentials are set/overridden, when the user clicks "Test Connection", then the UI calls the backend test endpoint and reports success/failure | High | ai-assisted | Active |
| S1.4.3 | Show current credential status in admin tab | Given a user visits the admin tab, when they see the current state (path, last-tested, connection status), then they can decide whether to reconfigure | Medium | ai-assisted | Active |

---

## Done When

- [ ] CLI command `gmail delete` accepts mailbox + age options, dry-run, and confirmation
- [ ] Web UI form captures mailbox/age selections with Preview + Delete flow
- [ ] Admin tab allows credential configuration and test connection (both CLI + Web)
- [ ] All acceptance criteria pass, including live authorization and account access
- [ ] Tests pass (unit + integration with mock Gmail API)
- [ ] No hardcoded credentials in code or git
- [ ] `.env.example` documents required variables
