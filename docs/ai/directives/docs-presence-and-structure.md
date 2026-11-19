# Directive — Docs Presence & Structure

**Rule:** The working-model structure under `docs/` is a **precondition for work**, not an
output of it. If it is not there, **stop and tell the human before writing code.** Create it
only on their go-ahead.

"Not there" means any of these:

- no `docs/` folder;
- no `docs/ai/` (this working model);
- no `docs/product/backlog/` with at least one epic (`E{n}-*.md`) and the three logs
  (`task-log.md`, `bug-log.md`, `design-decision-log.md`).

Anything smaller (an index, one architecture doc) is a gap to report and close as part of the
effort. It is not a reason to stop (see [Do](#do)).

## Why

The loop is **architecture → plan → implement → record**. It only holds if the structure that
carries intent exists first: `architecture/` holds the design, `product/backlog/` holds the
plan, the logs hold the memory. Code written before that exists has no reviewable intent and
leaves nothing durable behind, and backfilling it later costs more than stopping at the start.

## Check

- **At the start of a session,** run `raven check` (read-only) and read what it reports. If raven
  is not installed, look for the three things above by hand and say raven is missing
  ([use-raven](./use-raven.md)).
- **Before every commit,** the pre-commit routine in
  [03 — Backlog & Logs](../workflow/03-backlog-and-logs.md) applies. If the effort has no stories
  in a backlog epic, stop and say so before committing.

## When the structure is missing

| Situation | What to do |
|-----------|------------|
| A new project, nothing there yet | `raven new NAME --archetype KIND` writes `docs/` and `docs/ai/`. Run it with `--dry-run` first and show the human |
| `docs/` exists but `docs/ai/` is missing or behind | `raven docs-ai update` (preview with `--dry-run`). Never copy the tree by hand |
| The rest of the skeleton is missing (indexes, backlog, logs) in a project raven did not scaffold | raven has **no command** for this yet (`raven adopt` is planned, E26). Say so, then follow [use-raven](./use-raven.md): offer the human the choice of waiting or building it by hand now. If by hand, keep it a small scaffold chore ([04](../workflow/04-scaffolding-and-main.md)) and note in the task-log that it was a raven candidate |

## Do

- Tell the human what is missing and what you propose, and wait for the go-ahead before
  scaffolding. The scaffold is a direction-setting step
  ([00 — Working Relationship](../00-working-relationship.md)).
- Once the structure exists, follow the loop: framing docs, stories, implement, update the logs.
- If an effort turns up one missing doc partway through (an architecture note, an ADR), create it
  as part of the effort and say so in the task-log ([01](../workflow/01-docs-structure.md)). That
  is not a stop.

## Don't

- Don't implement into a project that has no working-model structure.
- Don't create the whole `docs/` tree silently. The human should see and approve the scaffold.
- Don't rebuild by hand what a raven command does.
- Don't treat `docs/` as documentation to backfill later.
