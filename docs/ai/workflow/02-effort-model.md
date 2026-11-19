# 02 — The Effort Model

Work is organized into **efforts**. An effort is one coherent, product-guided unit
of change — a **feature or capability**, a bug fix, or an enhancement — scoped so a
human can review it as a whole.

## What defines an effort

- It is **product-guided**: it delivers a feature or capability the backlog
  describes, not an arbitrary code change. An effort may span **multiple stories**
  and even touch **multiple epics**, as long as it hangs together as one reviewable
  change.
- It has a **clear boundary**: you can say in a sentence what it does and what
  "done" means for it.
- It produces a **reviewable branch** ending in a pull/merge request.

Each effort is recorded as a **task** in the task-log from the moment it is agreed
(open), through the work (in progress), to its finish (done), so the log always shows
what is being worked on. See [03 — Backlog & Logs](./03-backlog-and-logs.md).

When the human asks the agent to **plan** an effort, the agent first **scans the
backlog** for stories, bugs and decisions that already cover part of it and proposes
what to pull in, before writing new stories (see
[03 — Planning a feature](./03-backlog-and-logs.md#planning-a-feature-scan-the-backlog-first)).

Prefer a **docs + backlog effort first** (reviewable, low-risk), then a code
effort, over one sprawling branch that mixes planning and implementation.

If the effort builds or reshapes a **UI**, it also carries a mockup step before
any UI code — mock the screens as PNGs, get them agreed, then build. See
[06 — UI Mockups](./06-ui-mockups.md).

## Always work on a branch named for the effort

Never work directly on the mainline (the one exception is the initial scaffold —
see [04 — Scaffolding & mainline](./04-scaffolding-and-main.md)). Create a branch
whose name captures the nature of the work:

| Kind of effort | Branch prefix | Example |
|----------------|---------------|---------|
| A feature / capability / epic build | `feature/` | `feature/e5-import-pipeline` |
| A bug fix | `fix/` | `fix/b02-config-path` |
| Docs / process / backlog only | `docs/` | `docs/ai-working-model` |
| Refactor / tech-debt | `chore/` or `refactor/` | `chore/reconcile-config` |

Branch off the **current** mainline (fetch first). After an effort merges, start
the next one on a **fresh** branch off the updated mainline — don't reuse a branch
whose request removed it on merge.

## Commit step by step as features complete

Commits track the **completion of a step** — a feature, a bug fix, an enhancement —
not arbitrary save points. Each commit should:

- leave the tree in a **working, verified** state (build/lint/tests green for what
  it touches — see [05 — Review & Publish](./05-review-and-publish.md));
- carry the **backlog + logs update** for that step (see
  [03 — Backlog & Logs](./03-backlog-and-logs.md));
- be preceded by a **human review gate** — the agent holds before committing.

A single effort may be several commits (one per feature/step) before the request,
or a single commit when the step is the whole effort. Either way, the pre-commit
routine runs before each one.

## Scope discipline

Solve the effort that was asked for. Don't fold in unrelated cleanup, extra
abstraction, or defensive code beyond what the task needs. If an effort reveals
adjacent work, note it (a new story, a bug-log entry) rather than expanding the
current branch to swallow it. A larger capability may legitimately reshape existing
design — that's fine when it's part of the stated effort and the human has agreed
to the direction.
