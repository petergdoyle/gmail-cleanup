# 03 — Backlog & Logs

The backlog is the plan; the logs are the memory. Together they let a fresh session
(or a different agent) pick up exactly where the last one left off, and they are the
**only source** the [weekly update](./07-weekly-updates.md) is built from. Keeping
them current is not optional bookkeeping. It is part of every commit.

## Why keeping them current matters

- **Work that is not logged is invisible.** A stakeholder, a product owner, or the
  next agent session sees only what the backlog and the three logs say. If a task
  was finished but not logged, it did not happen as far as they can tell.
- **The weekly update is a view over the logs.** It selects dated entries from the
  task-log, bug-log and design-decision-log and links back to the stories they
  touched. It does not invent anything. If the logs are late, thin or undated, the
  update is wrong, however well it is written.
- **A fresh session resumes from the logs.** Open tasks, open bugs and open decisions
  are the first things an agent reads. Stale logs send it back to rediscover work.
- **Honest status is what makes the plan trustworthy.** A story marked `Done` that is
  not verified, or a bug found and not recorded, turns every later summary into a
  guess.

So the agent keeps all four documents (backlog, task-log, bug-log, design-decision-log)
current **as the work happens**, at the moments listed in
[When to write what](#when-to-write-what), and never leaves it for the end.

## The backlog format (issue-tracker-compatible)

Work is defined as **Epic → Feature → Story** in Markdown that an issue-tracker
importer can consume, so the same files that plan the work also publish to the
tracker:

- **Epic** = a file, `E{n}-{slug}.md`, starting with `# E{n} — Title` and an
  `**Epic:**` one-line summary.
- **Feature** = a `### F{n}.{m} — Title` heading within the epic.
- **Story** = a row in a six-column table:

```markdown
### F1.1 — Feature Title

| ID | Story | Acceptance Criteria | Priority | Tags | Status |
| ---- | ----- | ------------------- | -------- | ---- | ------ |
| S1.1.1 | As a …, I can … | Given/When/Then | High | ai-assisted | Backlog |
```

- **Status**: `Done`/`Resolved` (done), `Active` (in progress), `Backlog` (not
  started), `Superseded` (made obsolete; say by what).
- **Priority**: `High`, `Medium`, `Low`.
- **Tags**: from the project's controlled vocabulary (e.g. `ai-assisted`,
  `human-authored`, `test-only`, `spike`, `tech-debt`, `nfr`, `blocker`, `infra`).

> **SUBSTITUTE: issue tracker.** The Epic → Feature → Story shape above is a
> generic, tracker-neutral structure. Keep it as-is if you publish the backlog to
> a tracker via an importer that reads this format, or map these fields to your
> tracker's import schema. If you don't push to a tracker at all, the format still
> serves as the in-repo plan — keep it parseable regardless.

The backlog folder also carries a `README.md` index (epics table + build
sequencing) and the three logs below.

### Planning a feature: scan the backlog first

Stories wait in the backlog until the human is ready to work on them. An effort is
usually defined inside one epic, but that is a convention and not a rule. A feature
or task may pull stories from several epics, or start a new epic.

When the human asks the agent to plan a new feature or task, the agent:

1. **Scans the backlog first**: the epics index, the epic files, and the open entries
   in the task-log, bug-log and design-decision-log.
2. **Lists what is relevant**: existing stories that already cover part of the
   request, stories it would supersede or split, open bugs in the same area, and open
   decisions it depends on.
3. **Proposes the pull-in** to the human (which existing stories join the effort, which
   new stories are needed, where they live) before writing anything.
4. **Plans the remainder**: only the stories not already covered, in an existing epic
   or a new one, with stable IDs that continue the numbering.

Planning is a unit of work like any other. It gets a task-log entry (see
[Planning efforts](#planning-efforts)).

## The three logs

| Log | ID | Purpose | Answers |
|-----|----|---------|---------|
| `task-log.md` | `T##` | The scoped efforts (features, tasks, planning) opened, in progress and done | What was worked on, what is being worked on, and how do we know it is finished |
| `bug-log.md` | `B##` | Defects found and their resolution | What was wrong, what caused it, how it was fixed and verified |
| `design-decision-log.md` | `D##` | Lightweight decisions not big enough for a full ADR | What was decided or is waiting for a decision, why, and what else was considered |

All three live in `docs/product/backlog/` next to the epics. Their shape is fixed so
a person, an agent and the weekly update can all read them the same way.

### Rules common to all three logs

1. **One entry per ID.** IDs (`T01`, `B07`, `D12`) are assigned in order, never reused
   and never renumbered. Use at least two digits; add a digit when needed (`T100`).
2. **A summary row plus a details section.** Each log has summary tables for scanning
   and a `## Details` section with one `###` block per ID for the full account. A table
   cell holds a sentence or two. Anything longer goes in Details.
3. **Newest first.** Rows in each table and blocks in Details are ordered newest first
   by the date that table is keyed on (Created, Done, Noticed, Fixed on, Raised,
   Decided on).
4. **Every row is dated, in ISO form** (`2026-11-13`). The weekly update selects
   entries by these dates. An undated entry cannot be reported.
5. **Link, don't repeat.** Refer to stories by ID and link to the epic file (`S3.1.2`,
   `[E3](./E3-converter.md)`), and to other log entries by ID (`B04`, `D07`, `T12`).
   Use relative links.
6. **State what was verified and what was not.** A finished entry says what was run or
   checked (tests, build, a live exercise) and what was not. Never write "verified"
   about something that was not exercised.
7. **Status words are controlled** (per log, below). Do not invent new ones.
8. **Do not hand-edit publisher front matter.** If a log starts with a block such as
   `md2conf_id: …`, the publisher owns it.
9. **Keep the Markdown valid.** A literal `|` inside a table cell breaks the row.
   Escape it or rephrase.

### `task-log.md`

A task is **one scoped effort**: a feature, a capability, a fix, a planning pass, a
piece of operational work. It is the unit the human and the agent agree on, work
through together and review as a whole (see [02 — The Effort Model](./02-effort-model.md)).
One task usually implements several stories and may touch several epics.

Structure of the file, in order:

1. Title: `# <Project> — Task Log`, then a back link to the backlog index.
2. A short purpose paragraph, then **How to use**, the **Status** values and the
   **Priority** values.
3. `## Open & In-Progress Tasks` (table).
4. `## Done` (table).
5. `## Details` (one block per task).

```markdown
# Example — Task Log

[← Back to Backlog Index](./README.md)

A running list of scoped efforts. Companion to the [bug log](./bug-log.md) (defects)
and the [design decision log](./design-decision-log.md) (the why).

**How to use:**
- Add a row with the next `T##` ID when an effort is agreed.
- Keep the summary to one sentence; put scope, acceptance and results in **Details**.
- Set **Area** and **Implements** so the work traces to the backlog.
- Move the row to **Done** when the effort is finished and verified.

**Status:** `open` → `in progress` → `done` (or `blocked` / `dropped`)
**Priority:** `high` · `medium` · `low`

---

## Open & In-Progress Tasks

| ID | Summary | Area | Implements | Priority | Status | Created |
|----|---------|------|------------|----------|--------|---------|
| T04 | Add CSV export to the report page | Reports | [E3 F3.2](./E3-reports.md) · S3.2.1, S3.2.2 | medium | in progress | 2026-11-10 |

## Done

| ID | Summary | Area | Implements | Resolution | Done |
|----|---------|------|------------|------------|------|
| T03 | Plan the reporting epic | Planning | [E3](./E3-reports.md) | Added E3 with 3 features and 11 stories; no code. Verified the tables parse. Merged in !14. | 2026-11-09 |

---

## Details

### T04 — Add CSV export to the report page  🔵 IN PROGRESS

Implements **[E3 F3.2](./E3-reports.md)** · relates to [B05](./bug-log.md) · design [D06](./design-decision-log.md)

- **Status:** 🔵 In progress, branch `feature/e3-csv-export`.
- **Priority:** Medium.
- **Area:** Reports (`src/reports/export.py`, `web/src/pages/Report.tsx`).
- **Owner:** A. Person

**Scope.** What is in the effort, as a short list.

**Acceptance.** How we will know it is done, as checkable conditions.
```

**Columns, open table**

| Column | Content |
|--------|---------|
| ID | `T##`. |
| Summary | One sentence, starting with a verb or a noun phrase for the outcome. |
| Area | Where the work sits (for example `Auth`, `Infra`, `Docs`, `Planning`). Use a short, repeated set per project so entries can be grouped. |
| Implements | The epic or feature (linked) and the story IDs it delivers. Add related `B##` and `D##`. A task with no story states why (for example a fix or an operations task). |
| Priority | `high`, `medium`, `low`. |
| Status | `open`, `in progress`, `blocked`, or `under review`. |
| Created | The date the effort was agreed or opened. |

**Columns, Done table:** the same first four, then **Resolution** (what was built and
where, how it was verified, the branch or merge request) and **Done** (the date the
work was finished: the merge date if known, otherwise the date of the final commit).

**The details block** for each task has, in order:

1. A heading `### T## — Title` ending in a status marker: `⚪ OPEN`, `🔵 IN PROGRESS`,
   `🟠 BLOCKED` or `UNDER REVIEW`, `✅ DONE`, `⏹ DROPPED`.
2. An `Implements …` line with links.
3. A bullet list with **Status** (with dates: created, delivered), **Priority**,
   **Area** and optionally **Owner** and **Branch / MR**.
4. **Scope** while open, and **Acceptance** (checkable conditions).
5. When done, a **Resolution** paragraph (what changed and where), then:
   - **Verified:** what was run or checked, with results (test counts, build, live check).
   - **Not verified:** what was not run, and why. Write "nothing outstanding" only when
     that is true.
   - Optionally a table mapping each acceptance criterion to where it landed.
6. Optionally the original spec, kept for the record in a `<details>` block.

**What counts as a task.** If it needed its own branch, or the human would want to see
it in a summary, it is a task. A one-line typo fix is not. A planning pass is.

#### Planning efforts

An effort that only plans (new epics, new stories, a reshaped backlog) is a task with
Area `Planning`. Its Resolution states the numbers (epics, features and stories added
or changed), that no code was written, and what was checked (for example that the
backlog tables parse). The new stories start as `Backlog`. The task is `done` when the
plan is merged, and the stories stay `Backlog` until someone works them.

### `bug-log.md`

A bug is **behavior that is wrong** against what was intended: found by the human,
found by the agent, or found by a test, a review or a user. Record it **when it is
found**, even if it is not fixed in this effort.

Structure, in order: title and back link; purpose paragraph; **How to use**;
**Status** and **Severity** values; `## Open & In-Progress Bugs`; `## Resolved`;
`## Details / repro notes`.

```markdown
**Status:** `open` → `in progress` → `fixed` → `verified` (or `wontfix` / `cannot reproduce`)
**Severity:** `blocker` (stops the journey) · `high` (major, has a workaround) ·
`medium` (annoying) · `low` (cosmetic)

## Open & In-Progress Bugs

| ID | Summary | Area | Severity | Status | Noticed | Related |
|----|---------|------|----------|--------|---------|---------|
| B06 | Export drops rows with an empty name | Reports | high | open | 2026-11-11 | [T04](./task-log.md) · S3.2.2 |

## Resolved

| ID | Summary | Area | Resolution | Fixed in | Fixed on |
|----|---------|------|------------|----------|----------|
| B05 | Report page shows the wrong total after a filter | Reports | Total now computed after the filter is applied; regression test added. | `fix/b05-filter-total` (!15) → `main` | 2026-11-10 |

## Details / repro notes

### B06 — Export drops rows with an empty name
- **Area / journey:** Reports
- **Severity:** high (data is silently missing from the file users hand to others)
- **Noticed:** 2026-11-11, while building [T04](./task-log.md).
- **Steps to reproduce:**
  1. Load a report that has a row with an empty name.
  2. Press **Export CSV**.
- **Expected:** every row is in the file.
- **Actual:** the row is missing.
- **Root cause:** (once known) the cause, with the file and line.
- **Fix:** (once applied) what changed, the date and the branch.
- **Verification:** what was run, with results. A regression test is expected for a fix.
- **Related:** E3 F3.2, T04, D06
```

Rules specific to the bug log:

- **Open bugs** have no `Fixed on`. When fixed, **move the row** from Open to Resolved
  and fill in **Resolution**, **Fixed in** (branch and merge request) and **Fixed on**
  (ISO date). The `Fixed on` column is what places the fix in a weekly update.
- **`Noticed`** is the date the bug was first recorded. It is never changed.
- The Details block carries the **Root cause**, **Fix** and **Verification** as they
  become known. A bug found now and fixed next week has an entry now.
- A bug that is really missing work (a feature gap) is a story or a task, not a bug.
  Say so in the entry and point to where it is tracked.
- Heading marker for resolved entries: `✅ FIXED (branch)` or `✅ RESOLVED`.
- **Severity** is the human's call. The agent proposes one with a reason.

### `design-decision-log.md`

A design decision is **a choice that shapes the build and that a later reader would
otherwise have to reverse-engineer**, and is not big enough for an ADR. Questions that
are waiting for an answer are recorded too, so they are not lost mid-effort.
Significant, hard-to-reverse decisions go to `architecture/decisions/` as an ADR (see
[decisions/](../decisions/README.md)). Promote an entry to an ADR if it turns out to
be larger than it first looked.

Structure, in order: title and back link; purpose paragraph; **How to use**; **Status**
values; `## Open Decisions`; `## Decided`; `## Details`.

```markdown
**Status:** `open` (needs a decision) · `decided` · `deferred` (revisit later) ·
`built` (decided and implemented) · `superseded` (replaced; say by which `D##`)

## Open Decisions

| ID | Question | Area | Status | Raised | Related |
|----|----------|------|--------|--------|---------|
| D07 | Should exports include archived rows? | Reports | open | 2026-11-11 | [T04](./task-log.md) |

## Decided

| ID | Question | Decision | Rationale | Decided on |
|----|----------|----------|-----------|------------|
| D06 | How do we stream large exports? | Write the file in chunks from a generator. | Keeps memory flat and needs no new dependency; a queue was heavier than the size warrants. | 2026-11-10 |

## Details

### D06 — Streaming large exports  ✅ DECIDED
- **Area / journey:** Reports
- **Considerations:** what the decision had to satisfy (limits, constraints, people affected).
- **Options:**
  - **A. Chunked generator (chosen).** Why it won.
  - **B. Background job and download link.** Why it was rejected.
  - **C. Load all rows and write once.** Why it was rejected.
- **Decision:** what will be done, in one or two sentences.
- **Rationale:** why this over the others.
- **Consequences:** what follows, good and bad, including anything it rules out.
- **Open questions:** anything still undecided, or "none".
- **Related:** E3 F3.2, T04, B05
```

Rules specific to the decision log:

- **Capture at the moment of deciding**, as part of the effort that made the call. A
  question that comes up and is not answered yet goes in **Open Decisions** with its
  `Raised` date.
- A decision records **three things**: the considerations, the alternatives (and why
  each was rejected), and the chosen path. A row with only the winner is not complete
  (see [decisions/](../decisions/README.md)).
- When decided, **move the row** from Open to Decided with the **Decision**,
  **Rationale** and **Decided on** (ISO date). When built, add `built` and the task ID
  to Details.
- **Never rewrite a decided entry.** If the call changes, add a new `D##` that says it
  supersedes the old one, and mark the old one `superseded by D##`.
- Heading markers: `✅ DECIDED`, `✅ BUILT`, `⏸ DEFERRED`, `↪ SUPERSEDED BY D##`.

### Older log shapes

Some projects began with a lighter, date-keyed shape (for example
`| Date | Task | Epic | Notes |` for the task-log). Those logs stay readable. When
touching one, **start new entries in the format above** and migrate the older rows when
the project is brought up to the working model (assign IDs in date order, keep the
dates). The weekly update can read both shapes but notes in its *Not verified* section
when it had to read an old one.

## When to write what

The agent writes at these moments, not only at commit time.

| Moment | The agent updates |
|--------|-------------------|
| The human agrees an effort (before work starts) | **task-log:** a new `T##` row, `open`, with Area, Implements and Created. **backlog:** any new stories as `Backlog` |
| Planning a feature | Scan the backlog first (see above). **backlog:** new or changed stories. **task-log:** a `Planning` task |
| Work begins on the branch | **task-log:** set the row to `in progress` |
| A story genuinely changes state | **backlog:** its Status, honestly (`Active` when in place but not fully verified; `Done` only when verified) |
| A defect is found (even if not fixed now) | **bug-log:** a new `B##` row, `open`, with the Noticed date and a Details block |
| A defect is fixed | **bug-log:** move to Resolved with Resolution, Fixed in, Fixed on; fill Root cause, Fix and Verification |
| A question comes up that needs an answer | **design-decision-log:** a new `D##`, `open`, with the Raised date |
| A call is made | **design-decision-log:** move to Decided with Decision, Rationale, Decided on; or add the entry if it was never raised |
| The effort is finished and verified | **task-log:** move the row to Done with Resolution and Done date; write Verified and Not verified in Details |
| Before every commit | The pre-commit routine below |
| The merge request merges | If the merge request number or merge date was not known at commit time, add it to the Resolution in the next effort's first commit |
| Each Friday, or when asked | Build the [weekly update](./07-weekly-updates.md) from the logs (it only reads them) |

## The pre-commit routine (run before EVERY commit)

Before each commit, in order:

1. **Scan the backlog story statuses** and update any that genuinely changed in
   this step. Be honest: mark `Done` only when real implementation warrants it;
   use `Active` when something is in place but not fully verified; don't mark a
   docs/scaffolding story `Done` just because docs were written. Note partial
   completion in the acceptance-criteria cell when useful.
2. **Update `task-log.md`**: set the task's row and Details to match what this step did
   (status, stories touched) and, importantly, **what was verified and what was not**.
   Enough that a fresh session could resume from the log alone. When the effort is
   finished, move it to Done with the Done date.
3. **Update `bug-log.md`** for any defect this step found (add it) or fixed (move it to
   Resolved with the Fixed on date).
4. **Update `design-decision-log.md`** (or write an ADR, see
   [decisions/](../decisions/README.md)) for any question raised or decision made in
   this step.
5. **Check the dates and links.** Every row you touched has its ISO date, and every
   story, bug and decision it names exists. A dated, linked entry is what the weekly
   update can pick up.
6. **Stage the publisher's config + state with the change.** If the step touched
   `docs/` or the backlog and you published or synced (Confluence, Jira), the
   updated `markdown-to-*.toml` and `.md2conf/` / `.md2jira/` state files are
   committed in the same step. They are source-controlled; `.env` never is
   ([directive](../directives/publishing-config-and-state.md)).

This is what lets a session resume cleanly if it disconnects, keeps any tracker push
and docs publish honest on every merge, and keeps the weekly update accurate.

## Validate before publishing

Before committing backlog/doc changes, keep them parseable: the backlog must stay
valid for whatever importer consumes it, and any diagrams in docs must validate. A
broken table or diagram shouldn't reach the mainline.

## Related

- [02 — The Effort Model](./02-effort-model.md): what an effort is, and the branch and commit rhythm
- [07 — Weekly Updates](./07-weekly-updates.md): how the logs become a stakeholder update
- [decisions/](../decisions/README.md): ADR versus the design-decision-log
