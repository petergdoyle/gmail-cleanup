# Directive — Deep Scan

**Rule:** A **deep scan** checks whether the project's docs still match the project. It takes real
effort, so it runs **only when the human asks for it**, or after the agent has **suggested** one and
the human agreed. The agent never starts one on its own. Mechanical checks are done by code, not by
the agent, wherever raven has a command for them.

## When

- **The human asks.** "Do a deep scan", "check the docs are up to date", "audit the docs".
- **After a major change, the agent suggests one.** Major means a decision accepted or superseded, an
  epic closed or restructured, a command, option or setting added, removed or renamed, a change to
  the Python floor or a main dependency, a project archived, renamed or split, or a change to what
  the scaffold or a template emits. The suggestion is one sentence ("that changes what the README
  says about X; want a deep scan?"). Then carry on with the effort. Do not stop to run it.
- **Not at every commit.** The pre-commit routine
  ([03 — Backlog & Logs](../workflow/03-backlog-and-logs.md)) already updates the docs a change
  touches. A deep scan looks for drift nobody touched.

## Do

- Follow the steps in [08 — The Deep Scan](../workflow/08-deep-scan.md).
- Work from a checkout of the current mainline, on a new branch or worktree, and open one docs
  request per repository ([git-host-and-reviews](./git-host-and-reviews.md)).
- **Run the mechanical checks with raven.** `raven docs-scan` is planned (raven backlog E30) and may
  not exist yet; check with `raven --help`. Until it does, do the mechanical checks with a throwaway
  script kept outside the repository, say in the report that you did, and note it in the task-log as
  a raven candidate ([use-raven](./use-raven.md)). Once it exists, do not rebuild those checks by hand.
- Test what you claim. If a doc says an option goes before a subcommand, or a default is a number,
  run it; do not assume.
- Hold for the human's review before committing, as with any change.

## Don't

- Don't start a deep scan unasked, and don't run one on a schedule of your own.
- Don't decide for the human. Change a status (an epic, an ADR, a story) only where a decision the
  human already recorded settles it, name that decision, and ask them to confirm. List everything
  else for them.
- Don't delete content to make a finding go away. Retire a file in its own change; git keeps it.
- Don't say a thing was checked when it was not. Say what you read, what you ran, and what you did
  not cover.
- Don't check ignored or generated files, or the example links inside raven-managed `docs/ai` files.
