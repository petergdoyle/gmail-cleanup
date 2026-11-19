# 00 — Why gmail-cleanup

## The problem

Gmail inboxes accumulate thousands of old messages that clutter and slow down
search. Manual deletion is tedious; Gmail's built-in filters don't offer
age-based bulk deletion. Users need a **safe, scriptable tool** to delete old
messages in bulk by mailbox (inbox, archive) and age, with confirmation and
recovery guarantees.

## The approach

**gmail-cleanup** is a dual-interface utility:

- **CLI** for scripting and automation (e.g., cron jobs, pipelines)
- **Web UI** for interactive exploration and admin configuration

It connects to Gmail via the Gmail API, requires OAuth setup, and allows users to:

1. **Configure Gmail credentials** in `.env` or override via the web UI admin panel
2. **Preview deletions** in dry-run mode (count, criteria, confirmation)
3. **Delete messages** by mailbox (inbox, archive) and age (e.g., 6 months)
4. **Test the connection** from CLI or web UI before running deletions
5. **Recover** via Gmail's trash/recovery (not undeleted by this tool, but
   preservable)

Default behavior: delete messages **6 months+ old** from inbox, **3 months+ old**
from archive. Both mailbox selections and age thresholds are configurable.

## What it is not

- **Not a full Gmail client.** It does one thing: delete old messages safely.
- **Not permanent destruction.** Deleted messages go to Gmail's trash for 30 days
  (Gmail's native recovery window).
- **Not a sync tool.** It doesn't replicate, back up, or export; it only deletes.
- **Not a folder manager.** It works on mailbox labels (inbox, archive), not custom
  labels.
