# 04 — Scaffolding & the Mainline

There is exactly one time it's correct to commit straight to the mainline, and it's
the very beginning of a project.

## The initial scaffold is a chore, merged directly to the mainline

A brand-new repository's **first commit(s)** establish the project skeleton:

- the `docs/` tree (taxonomy, architecture framing, the story-driven backlog, the
  logs, this `ai/` working-model tree);
- project scaffolding (package layout, build config, task runner / CLI front end,
  CI, `.gitignore`, `.env.example`).

This foundational scaffolding is a **chore**: it has no prior mainline to branch a
reviewable diff against, and it blocks everything else. It may be committed and
pushed **directly to the mainline** — this is the legitimate exception to
"never commit to the mainline."

Mechanics when the remote mainline doesn't exist yet:

- If the repo has a local initial commit and the remote is empty
  (`git ls-remote --heads origin` returns nothing), just
  `git push -u origin <mainline>`. This is allowed precisely because the remote
  mainline doesn't exist yet and so isn't protected.
- Keep the scaffold commit **secret-free** (no `.env`) and **license-correct** for
  the project's nature (see the project's own convention).

After the scaffold lands, **protect the mainline** so all further change flows
through pull/merge requests.

## Everything after the scaffold: branch + request

Once the mainline exists and is protected, every subsequent effort follows the full
loop:

1. branch off the current mainline, named for the effort;
2. implement, verifying each step;
3. run the pre-commit routine (backlog + logs);
4. hold for human review, then commit;
5. push the branch and open a **pull/merge request** to the mainline;
6. the human merges; the agent syncs and cleans up.

See [02 — Effort Model](./02-effort-model.md) and
[05 — Review & Publish](./05-review-and-publish.md) for the detail.

> **SUBSTITUTE: mainline name + git host.** "Mainline" is whatever your default
> protected branch is (`main`, `master`, `trunk`). The protect-after-scaffold and
> branch+request flow are host-neutral; the exact request mechanics live in the
> [git-host-and-reviews directive](../directives/git-host-and-reviews.md).
