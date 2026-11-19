# Directive — Publishing Config & State (markdown-tools)

**Rule:** The publisher's **config and state are source-controlled**; only the
**secrets** are not. Commit `markdown-to-*.toml` and the hidden state folders
(`.md2conf/`, `.md2jira/`) and keep them current with every docs/backlog change.
Never commit `.env`.

> **SUBSTITUTE: docs/backlog publisher.** This directive is written for the DPS
> `markdown-tools` suite (`md2conf` → Confluence, `md2jira` → Jira, `md2pdf` → PDF).
> If your project uses a different publisher, swap the file and folder names; the
> rule — *config + drift state are committed, secrets are not* — is tool-neutral.

## Why

The docs and backlog are Markdown in git (the source of truth); Confluence and Jira
are *published views* of them. To publish idempotently and to **detect drift**
(someone hand-edited the page or issue, or the repo moved on), the tools keep two
kinds of file:

- **Run settings** — `markdown-to-confluence.toml`, `markdown-to-jira.toml`,
  `markdown-to-pdf.toml`: which space/folder/project, which `docs/` sections
  publish, labels. Non-secret.
- **State** — `.md2conf/`, `.md2jira/` (e.g. `state.json`, `state-<tag>.json`): the
  page/issue ids and content hashes recorded at the last publish.

If state is git-ignored, the next clone or CI run starts blind: it re-creates pages
that already exist, cannot see drift, and a teammate's publish silently diverges
from yours. Committing the files makes publishing **repeatable by anyone** and makes
drift a reviewable diff. The only thing that must stay out of git is the credential
file, `.env`.

## Do

- **Commit** every `markdown-to-*.toml` at the repo root and the whole `.md2conf/`
  and `.md2jira/` folders (including `*.bak` the tool leaves beside state).
- **Keep them current:** after a publish or sync, stage the updated state files in
  the **same commit/branch** as the docs or backlog change that caused it. A state
  file that lags the docs reports false drift.
- **Never hand-edit** state files. Change settings in the `*.toml`; let the tool
  rewrite state. Review state diffs like any other generated-but-tracked file.
- Before committing, confirm `.gitignore` excludes `.env` **and does not** list
  `markdown-to-*.toml`, `.md2conf/`, or `.md2jira/`. Stage by file name and check
  `.env` is not staged ([secrets-and-env](./secrets-and-env.md)).
- Keep a secret-free **`.env.example`** naming the keys the publishers need
  (`CONFLUENCE_*`, `JIRA_*`) — keys only, never values.
- Treat a drift report as information to reconcile deliberately: decide whether the
  repo or the remote is right, fix the Markdown, republish. The Markdown wins.

## Don't

- Don't add `.md2conf/`, `.md2jira/`, or `markdown-to-*.toml` to `.gitignore`.
- Don't put a secret (token, email, URL with credentials) in a `*.toml`. Settings
  there are committed and visible to everyone with repo access.
- Don't delete state to "fix" a publish error — that discards the id mapping and
  causes duplicate pages/issues. Ask the human first.
- Don't publish from an uncommitted or unreviewed docs tree; publish what the
  human has approved ([05 — Review & Publish](../workflow/05-review-and-publish.md)).
- Don't treat Confluence or Jira as authoritative. Remote hand-edits are drift to
  report, not input to copy back.

## Note

A project scaffolded by raven is checked for the `.gitignore` half of this rule
(`raven check`: `stack-mdtools-tracked` and `stack-env-ignored`). The "commit state with the
change that caused it" half is on you and the agent: make it part of the
pre-commit routine ([03 — Backlog & Logs](../workflow/03-backlog-and-logs.md)).
