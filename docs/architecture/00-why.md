# 00 — Why gmail-cleanup

## The problem

Gmail inboxes accumulate thousands of old messages that clutter and slow down
search. Manual cleanup can be tedious. Users need a **safe, scriptable tool**
to move old messages to Trash by mailbox (inbox, archive) and age, with
preview, confirmation, and a clear recovery path.

## The approach

**gmail-cleanup** is a dual-interface utility:

- **CLI** for scripting and automation (e.g., cron jobs, pipelines)
- **Web UI** for interactive exploration and admin configuration

It connects to Gmail via the Gmail API, requires OAuth setup, and allows users to:

1. **Configure Gmail credentials** in `.env` or override via the web UI admin panel
2. **Connect and select Google accounts**, and navigate through each account's mailboxes
3. **Preview deletions** in dry-run mode (account, count, criteria, confirmation)
4. **Delete messages** by account, mailbox (inbox, archive), and age
5. **Test the connection** from CLI or web UI before running deletions
6. **Recover** messages through Gmail's Trash, not through this tool

By default both mailboxes are selected: inbox messages older than **6 months**
and archived messages older than **3 months**. Both selections and thresholds
are configurable. Archive means received mail outside Inbox, Sent, Drafts, Spam,
and Trash; it is not a separate Gmail folder. Each account is selected and
previewed separately, and the affected account is identified before any action.

## What it is not

- **Not a full Gmail client.** It does one thing: delete old messages safely.
- **Not immediate permanent destruction.** Messages go to Gmail's Trash, where
  they can be recovered in Gmail until Gmail permanently deletes them (normally
  after 30 days). Retention may be affected by account policies.
- **Not a sync tool.** It doesn't replicate, back up, or export; it only deletes.
- **Not a folder manager.** It selects messages by Gmail labels, not custom
  folder management.
