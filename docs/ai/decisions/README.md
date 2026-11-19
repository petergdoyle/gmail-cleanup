# Decisions

How design decisions are captured so the *why* travels with the code. A decision
is captured when it shapes the build and a future reader (human or agent) would
otherwise have to reverse-engineer the reasoning.

## Two homes, by weight

| Decision weight | Where it goes | Shape |
|-----------------|---------------|-------|
| **Significant, hard to reverse** (foundation, stack, architecture, a cross-cutting pattern) | `docs/architecture/decisions/` as an **ADR** (`NNNN-slug.md`) | Context → Decision → Rationale → Consequences → Alternatives Considered → Follow-ups |
| **Lightweight** (a local call, a convention, a small tradeoff) | `docs/product/backlog/design-decision-log.md` | A `D##` entry: a summary row (question, decision, rationale, date) and a Details block with considerations, options and the chosen path. Format in [workflow/03](../workflow/03-backlog-and-logs.md) |

Promote a log entry to a full ADR if it turns out to be more significant than it
first looked.

## What a captured decision must contain

Whether ADR or log line, a decision records **three things**:

1. **The considerations** — what was at stake, the forces in tension, what the
   decision had to satisfy.
2. **The alternatives** — the options genuinely weighed, and *why each was
   rejected* (not just the winner).
3. **The chosen path** — what was decided, and the consequences (positive, negative,
   neutral) that follow.

Capturing the alternatives matters as much as the choice: it's what stops a future
effort from re-litigating settled ground, and what lets a good decision be revisited
honestly if the forces change.

## When to capture

- **At the moment of deciding**, as part of the effort that made the call — not
  retroactively. If an effort makes a direction-setting choice, the ADR or log
  entry is part of that effort's commit (see
  [workflow/03 — Backlog & Logs](../workflow/03-backlog-and-logs.md)).
- A decision that emerges mid-effort still gets captured mid-effort, same as an
  emergent doc (see [workflow/01 — Docs Structure](../workflow/01-docs-structure.md)).

## Why this lives in the working-model tree

This file states the **policy** (where decisions go, what they must contain). The
**decisions themselves** live in the project's `architecture/decisions/` and
`design-decision-log.md` — not here. This tree describes the practice; the
project's own docs hold the instances.
