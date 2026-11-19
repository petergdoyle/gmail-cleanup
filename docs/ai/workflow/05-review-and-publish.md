# 05 — Review & Publish

The checkpoints where the human disposes. Between them the agent works
autonomously; at them it stops and hands over.

## Verify before you present

Nothing is presented for review until it's been **verified**:

- Run the project's **build/compile**, **linter**, and relevant **tests** for what
  the step touched; fix failures before presenting.
- If the project has no test framework and the step added behavior, set up the
  standard one and write tests. (Don't add tests the human didn't ask for on
  unrelated code.)
- For things that need a runtime the local/CI environment can't provide (a native
  dependency, a browser, live credentials), **verify what you can and say plainly
  what you couldn't** — don't imply a pipeline/render/publish works when it wasn't
  exercised.
- Clean up temporary files created during verification.

## The pre-commit review gate (hold for the human)

Before committing, the agent:

1. completes the **pre-commit routine** (backlog + logs updated, publisher
   config/state staged —
   [03](./03-backlog-and-logs.md));
2. runs the **external-content review** (below) if the step touched outward-facing
   docs;
3. **presents the finished, verified work and holds** — it does **not** commit
   until the human says go.

The point of holding is that the human sees the change **color-coded in the IDE**
before it's committed. The agent's hand-off should summarize what changed, what was
verified, and what (if anything) is still `Active` and why.

## External-content review

Any step that affects **architecture, stakeholder, or other external-facing
content** gets an explicit review pass **before commit** for:

- **Gaps** — missing information a reader on another team would need.
- **Overlap** — the same thing now described in two places that can drift.
- **Missing links / index entries** — new docs added to their folder `README` and
  cross-referenced.

If the step introduced a design decision, confirm it's captured where it belongs
([decisions/](../decisions/README.md)). If the effort outgrew the existing docs,
confirm the new docs were created (see [01 — Docs Structure](./01-docs-structure.md)).

## Commit, push, and open the request

After the human says go:

- **Commit** on the branch with a message that explains the *what* and *why*
  (prefer a written message file for anything with special characters).
- **Before pushing, fetch and check how far behind the mainline the branch is** —
  especially for an effort that's been open a while. The mainline can move
  underneath a long-lived branch (a sibling effort merges), and a branch that's
  behind will conflict or, worse, carry now-stale claims into the merge. If it's
  behind, rebase onto the updated mainline and resolve conflicts
  **substantively** — a conflict in a log/decision doc often means a fact changed
  (e.g. "X is unmerged" became false), so rewrite it to match reality rather than
  mechanically keeping one side. Re-run verification after the rebase, since it
  pulls in others' changes. (Rewriting your own feature branch to rebase is fine;
  force-push with `--force-with-lease`, never plain `--force`, and never rewrite
  the mainline.)
- **Push** the branch (never the mainline).
- **Open a pull/merge request** targeting the mainline explicitly, with a summary
  of changes, what was tested, and anything still open. Set it to remove the source
  branch on merge.

See [directives/git-host-and-reviews](../directives/git-host-and-reviews.md) for
the exact request mechanics and safety rules.

## The CI gate and the human merge

- **CI runs on the request.** It is a gate, not a substitute for local
  verification — the agent should already have run the equivalent checks locally.
- **The human merges.** The agent does not merge and does not deploy.
- After merge: the agent **syncs the mainline**, deletes the merged branch, and
  starts the next effort on a **fresh** branch off the updated mainline.

## After a failed approach

If an approach fails twice, stop patching it incrementally. Diagnose the root
cause, explain what went wrong, and try a fundamentally different approach. If the
new approach deviates from the human's original intent or adds an un-agreed
tradeoff, confirm before proceeding.
