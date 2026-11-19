# 07 — Weekly Updates

A weekly update tells stakeholders what moved in a project during a period. It is
**built on request from the project's own logs** (the task-log, bug-log and
design-decision-log) and links back to the stories and entries behind each line. It
adds no facts of its own. Because of that, an update is only as good as the logs, and
this is why [03 — Backlog & Logs](./03-backlog-and-logs.md) requires them to be kept
current as the work happens.

## Purpose and audience

- **Readers:** technical stakeholders, product owners, and managers who want a regular
  picture of progress. They read outcomes and decisions first and follow the links when
  they want detail. A person or an agent reading it cold should understand how the
  overall effort is moving.
- **Cadence:** every Friday, or when the engineer asks. The agent builds it only when
  asked.
- **Not a replacement for the logs.** The logs are the record. The update is a dated
  reading of them for a particular period.

## Where it lives

```text
docs/product/updates/
├── README.md                       # index: one row per update, newest first
├── 2026-11-20-weekly-update.md     # named by the date it was created
└── 2026-11-13-weekly-update.md
```

- **Folder:** `docs/product/updates/` (next to `backlog/` and `journeys/`).
- **File name:** `YYYY-MM-DD-weekly-update.md`, where the date is the day the update
  was **created** (normally the Friday). The period it covers is in the front matter.
  An update over another span is `YYYY-MM-DD-update-<span>.md` (for example
  `2026-12-04-update-2wk.md`).
- **Index:** `README.md` lists every update (date, period, status, a one-line headline).
  The agent adds a row when it creates an update.
- **Published** with the rest of `docs/` by the project's docs publisher. The folder
  must be in the publisher's sections. It is not a backlog and is never pushed to an
  issue tracker.
- A **program roll-up** (several projects in one document) is built elsewhere, from
  approved updates. See [Roll-up](#roll-up-across-projects).

## Inputs

| Input | Default if not given |
|-------|----------------------|
| **Project** | The repository the agent is working in |
| **Period end** | The most recent Friday on or before today. A different date if the human gives one |
| **Period start** | The day after the previous update's `period_end`. If there is no previous update, seven days before the period end (Saturday to Friday) |
| **Audience** | `stakeholders` (the readers above). The human may name another; see [Derived forms](#derived-forms) |

If the project or period cannot be defaulted sensibly, the agent asks. It never guesses
a period silently.

## What it is built from

The logs only. Every statement traces to a row or a Details block in one of them.

| Source | Selected by |
|--------|-------------|
| `task-log.md` | **Done** rows whose *Done* date is in the period; **open and in-progress** rows (status as of the period end); rows whose *Created* date is in the period |
| `bug-log.md` | Bugs whose *Noticed* date is in the period; **Resolved** rows whose *Fixed on* date is in the period; **open** bugs as of the period end |
| `design-decision-log.md` | Decisions whose *Raised* or *Decided on* date is in the period; **open** decisions as of the period end |
| `backlog/README.md` and the epic files | Only to look up what a referenced story or epic is, and the epic's current status. Never to infer work that the logs do not mention |

**Cross-checks (read-only, not sources of facts).** `git log` for the period and the
merge requests may be used to catch what the logs missed (see
[Log gaps](#log-gaps-check-the-logs-before-writing)) and to fill in a merge request
number. They do not add accomplishments.

## How to build one

The agent follows these steps in order.

1. **Fix the period** (see Inputs). Read the previous update, if any, for its end date.
2. **Run the log-gaps check** (next section). Do not write around a gap: report it.
3. **Select the entries** from each log by the rules above. Write the list down first
   (IDs only) so the counts come from the list.
4. **Group the work.** Group completed and in-progress tasks by epic (or by `Area` when
   a task has no epic), so the reader sees movement per theme, not a list of chores.
5. **Fill the template** below, section by section. Every highlight carries the IDs it
   came from (`T07`, `B03`, `D05`, `S3.1.2`).
6. **Count from the lists.** Every number in *At a glance* is a count of selected rows.
   Never estimate.
7. **Write *Not verified*.** List what the update could not check: logs read in an old
   shape, claims in the logs that say "not verified", anything the agent could not
   reach (for example no access to the merge request host).
8. **Set `status: draft`, add the index row, and stop.** Hold for human review. The
   agent does not mark it `approved`, send it, publish it or commit it on its own. The
   human edits, approves, and then the normal commit and publish steps apply.

Creating an update is not itself a task-log entry. Fixing the logs the update
exposed is.

### Log gaps: check the logs before writing

Before building, compare the logs with what the repository shows for the period and
list the differences. This is what keeps the update honest.

- Commits or merge requests in the period that no task-log entry mentions.
- Stories whose status in the backlog changed in the period with no task behind it.
- Fix or bug language in commits with no bug-log entry.
- Rows with no date, or a date outside any sensible range.
- Open tasks with no activity for the whole period and no `blocked` status.
- Logs still in an [older shape](./03-backlog-and-logs.md#older-log-shapes).

The agent reports the gaps to the human, proposes the log entries that would close
them, and waits. The human decides whether to fix the logs first (best) or to publish
the update with the gaps listed in *Not verified*.

## Writing rules

- **Outcomes before activity.** Lead with what changed for the product or the people
  who use it, then the work behind it.
- **Plain statements, in the logs' terms.** Use the project's own epic, story and area
  names. No hype, no adjectives the logs do not support.
- **Source every line.** An entry without an ID behind it is cut.
- **Say how sure you are.** "Done and verified" and "built, not yet verified" are
  different. Carry the log's own *Verified* and *Not verified* wording through.
- **Dates in full** (`2026-11-13`), never "yesterday" or "last week".
- **No secrets, no student-level or personal data, no internal hostnames.** The update
  is read more widely than the logs. Leave out anything a stakeholder should not see.
- **Short.** One screen of summary and tables, with detail one click away in the logs.

## The template

Copy this shape. Keep the sections in this order. Remove guidance in italics. A section
with nothing to report says "None this period." and is not dropped.

```markdown
---
title: <Project> — Update for <period_start> to <period_end>
project: <project name>
period_start: YYYY-MM-DD
period_end: YYYY-MM-DD
created: YYYY-MM-DD
audience: stakeholders
status: draft
author: <who asked for it>, drafted by the agent
approved_by:
approved_on:
sources: task-log, bug-log, design-decision-log, backlog index
---

# <Project> — Update for <period_start> to <period_end>

[← Back to Updates Index](./README.md)

## Summary

*Two to four sentences: what moved this period, the most important result, and the one
thing the reader should act on, if any. Cite IDs.*

## At a glance

| | This period | Open at period end |
|---|---|---|
| Tasks | *done count* | *open and in progress count* |
| Stories | *moved to Done count* · *planned (new) count* | *Backlog or Active, for the epics touched* |
| Bugs | *found* · *fixed* | *open, by severity* |
| Decisions | *made* · *raised* | *open* |

## Completed

*Done tasks in the period, grouped by epic or area.*

| ID | What was delivered | Implements | Verified |
|----|--------------------|------------|----------|
| T07 | *One sentence of outcome* | [E3](../backlog/E3-reports.md) · S3.1.2 | *What was checked, and what was not* |

## In progress

*Open and in-progress tasks as of the period end.*

| ID | What is being done | Status | Next step |
|----|--------------------|--------|-----------|
| T08 | *One sentence* | in progress | *The next concrete step* |

## Planned

*Epics and stories added or reshaped this period (planning tasks), and where they live.*

## Bugs

*Found, fixed, and still open. Open blockers and high-severity bugs are listed
individually.*

| ID | Summary | Severity | State | Date |
|----|---------|----------|-------|------|
| B06 | *One sentence* | high | fixed | 2026-11-12 |

## Decisions

*Decisions made, with the one-line why. Then questions still waiting for an answer, and
who needs to answer them.*

| ID | Decision or question | State | Date |
|----|----------------------|-------|------|
| D06 | *One sentence* | decided | 2026-11-10 |

## Risks and blockers

*Blocked tasks, open blocker or high bugs, and open decisions that stop work. Say what
each is waiting on.*

## Needs from stakeholders

*Specific asks: a decision, an approval, access, a review. Each names the log entry it
comes from. "None this period." if empty.*

## Next period

*The in-progress tasks to finish and the highest-priority open tasks to start, from the
task-log and the backlog build sequencing.*

## Not verified and log gaps

*What the update could not check, the log gaps found when building it, and any logs
read in an older shape.*

## References

- [Task log](../backlog/task-log.md) · [Bug log](../backlog/bug-log.md) ·
  [Design decision log](../backlog/design-decision-log.md) · [Backlog](../backlog/README.md)
```

## Derived forms

An email, a chat post or a one-page brief for a particular reader is a **derived,
shorter form of an approved update**. It leads with the summary and the asks, and it
adds no fact that is not in the update. If the reader needs something the update does
not say, fix the logs and the update first. The update stays the source.

## Roll-up across projects

A program view (several projects in one document) is **not built in a project**. It is
built in the program's own repository, from the projects' **approved updates**, by that
repository's own routine. This is why each project's update links back to its logs and
states its period plainly: the program view reads the updates, not the raw logs. A
project does not need to do anything extra to be included.

## After the update is approved

1. The human sets `status: approved`, `approved_by` and `approved_on`.
2. The normal steps apply: pre-commit routine, review gate, commit on a branch, merge
   request, merge by the human, and publish with the docs publisher.
3. Next Friday's update starts from this one's `period_end`.

## Related

- [03 — Backlog & Logs](./03-backlog-and-logs.md): the formats this reads, and when each log is written
- [01 — The Docs Structure](./01-docs-structure.md): where `product/updates/` sits
- [00 — The Working Relationship](../00-working-relationship.md): the review gate that applies to every update
