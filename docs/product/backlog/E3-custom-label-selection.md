# E3 — Custom Gmail Label Selection

[Back to Backlog Index](./README.md)

**Epic:** Discover and select a Google account's custom Gmail labels for
age-based cleanup in addition to the existing Inbox and Archive choices.

This is a **separate future effort**, after the current Inbox/Archive work. A
custom label is not an independent mailbox: a message can have several labels.
Moving a message to Trash affects the whole message and its other label views.
Archive continues to include otherwise eligible received messages with custom
labels even when those labels are not separately selected. The UI and CLI must
explain this clearly; an unchecked custom label does not protect its messages
from an Inbox or Archive selection.

## Features

### F3.1 — Discover and Select Labels

| ID | Story | Acceptance Criteria | Priority | Tags | Status |
| ---- | ----- | ------------------- | -------- | ---- | ------ |
| S3.1.1 | As a user, I can see the selected account's custom labels | Given an authorized account, when I open cleanup or request labels in the CLI, then its current custom Gmail labels are listed without treating them as separate accounts | High | ai-assisted | Backlog |
| S3.1.2 | As a user, I can select custom labels for cleanup | Given discovered custom labels, when I select one or more, then each additional label starts unchecked and can have an age or date cutoff; Inbox and Archive retain their existing defaults | High | ai-assisted | Backlog |
| S3.1.3 | As a scripting user, I can select a custom label | Given an authorized account, when I specify an unambiguous label and an age in the CLI, then I can preview or confirm cleanup for that label alongside the existing mailbox options | High | ai-assisted | Backlog |
| S3.1.4 | As a user, I can distinguish account label lists | Given two connected accounts with different labels, when I switch accounts, then only the selected account's labels and its in-session selections are shown | High | ai-assisted | Backlog |

### F3.2 — Safe Preview and Cleanup

| ID | Story | Acceptance Criteria | Priority | Tags | Status |
| ---- | ----- | ------------------- | -------- | ---- | ------ |
| S3.2.1 | As a user, I can understand overlapping label selection | Given a selected label or Archive, when I preview and confirm, then the UI and CLI explain that moving a message to Trash affects the whole message and that Archive includes eligible custom-labeled mail | High | nfr | Backlog |
| S3.2.2 | As a user, I see unique message totals | Given messages matching multiple selected labels or mailboxes, when I preview, then per-selection counts and the deduplicated total are clear and each message is moved at most once | High | nfr | Backlog |
| S3.2.3 | As a user, I keep the existing safety controls | Given a label selection, when I preview or clean up, then account verification, dry-run, confirmation, preview invalidation and Gmail Trash recovery remain in effect | High | nfr | Backlog |
| S3.2.4 | As a user, I see discovery and access errors | Given Gmail label retrieval fails or a selected label is unavailable, when I try to preview, then I see an actionable error and no messages are moved | High | nfr | Backlog |

## Done When

- [ ] Revised mailbox-selection mockups are reviewed before UI changes.
- [ ] Custom labels are discovered per account and selectable in both interfaces.
- [ ] The overlap and Archive behavior are explained before cleanup.
- [ ] Tests cover overlapping messages, account isolation, error cases and safety.
- [ ] Live Gmail verification is performed or its absence is explicitly recorded.
