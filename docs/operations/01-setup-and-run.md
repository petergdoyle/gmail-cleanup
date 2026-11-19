# 01 — Setup and run

[← Back to Operations](./README.md)

How to get gmail-cleanup running on a development machine. Keep this page true: when a
step changes, change it here in the same commit.

## Set up

```bash
make setup      # install the dependencies with uv
make lint       # ruff
make test       # pytest
raven check .   # audit the project against the suite's conformances
```

If the project runs a service or a UI, `make up` starts it in the background and
`make down` stops it (the Makefile lists every target: `make help`).

## Settings and secrets

- Non-secret settings are committed (for example the `markdown-to-*.toml` files).
- Secrets live in a git-ignored `.env`. `.env.example` lists the key **names** only.
  Copy it to `.env` and fill the values in; never commit `.env`.

## Publish the docs

`docs/` publishes to Confluence and the backlog to Jira with markdown-tools. Plan first,
then publish:

```bash
mdtools ui        # the web UI: md2conf for docs, md2jira for the backlog
```

See `ai/directives/publishing-config-and-state.md` for what is committed (settings and
state) and what is not (`.env`).

> **Stub.** Replace this page with the real steps as gmail-cleanup takes shape:
> prerequisites, first run, environment variables by name, and how to tell it is healthy.
