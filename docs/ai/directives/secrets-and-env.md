# Directive — Secrets & Environment

**Rule:** Secrets live only in a git-ignored `.env`. Never commit it, never echo
its values. Keep a secret-free `.env.example`. Non-secret run settings go in the
project's config file (e.g. a `*.toml`/`*.yaml`), never with the secrets.

## Why

Project `.env` files tend to hold live API tokens (and get copied between
projects). A single careless `git add` or an echoed value leaks a credential. The
split — secrets in `.env`, settings in a committed config file — keeps the leak
surface to one git-ignored file.

## Do

- Confirm `.gitignore` excludes `.env` **before any commit**; stage specific files
  by name and verify no `.env` is staged.
- Keep a committed, **secret-free `.env.example`** listing the keys (no values) each
  component needs.
- Reference secrets **by key name** in output and docs (e.g. "set `API_TOKEN`"),
  never by value.
- Read a token out of `.env` without sourcing the whole file, e.g.
  `grep -E '^API_TOKEN=' .env | cut -d= -f2-`, to avoid the shell-source trap.
- **Quote any `.env` value that contains spaces** (`KEY="a b c"`).
- Commit the **non-secret** companions of `.env`: the publisher's `markdown-to-*.toml`
  settings and `.md2conf/` / `.md2jira/` state are source-controlled, not ignored
  ([publishing-config-and-state](./publishing-config-and-state.md)). Ignore `.env`
  only.

## Don't

- Don't commit `.env` or any file containing a live secret.
- Don't print, log, or paste a secret value back into chat, a commit, or a doc.
- Don't `set -a && source .env` blindly: an **unquoted spaced value** makes
  `source` try to execute the second word as a command, aborting the source partway
  and producing flaky failures that look like network errors.
- Don't read files likely to hold secrets (private keys, credential stores) unless
  the task requires it — and if it does, reference keys, not values.

## Note

Rotate any token that has sat in plaintext `.env`, especially one copied from
another repo. Keep one fresh, appropriately-scoped token per project.
