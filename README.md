# gmail-cleanup

a utility to clear out old gmail items

> Archetype: **utility-gui**

Develop it with the project's `make` targets (`make help` for all):

```bash
make setup              # create the venv + install dev deps
make install            # put `gmail` on your PATH (uv tool -> ~/.local/bin)
make ui                 # build-if-needed + serve the web UI (127.0.0.1)
gmail --help              # ...then run it
```

(Raw inner loop without installing: `uv run gmail --help`.) To build a
distributable wheel, run `make web` before `uv build`; install the resulting
wheel with `uv tool install dist/gmail_cleanup-0.1.0-py3-none-any.whl`. The
generated UI is not committed, so a direct source checkout must build it first.

## Gmail setup

1. In Google Cloud, enable the Gmail API, configure the OAuth consent screen,
   and create an **OAuth client ID for a desktop application**. Download its
   JSON file to a private location. Google's OAuth testing and verification
   settings may limit which accounts can authorize and how long tokens last.
2. Copy `.env.example` to `.env` in the directory from which you run the app.
   Set `GMAIL_CREDENTIALS_PATH` to the downloaded file (quote paths with spaces),
   or supply the client JSON as `GMAIL_CLIENT_CONFIG_JSON`. Environment variables
   take precedence over `.env`. Never commit credentials or `.env`.
3. Run `uv run gmail auth` for each account and choose the Google account in
   the browser, or use **Admin → Add account** in the UI. Each account must
   grant the Gmail modify permission separately. The app stores web-authorized
   account credentials in macOS Keychain.
4. Run `uv run gmail accounts` to list accounts and
   `uv run gmail test-connection --account you@example.com` to test one.
   In the UI, select an account and use **Admin → Test connection**.

The Admin client path or JSON override is kept in memory for the current UI
session. The client JSON is never displayed after it is applied.

## Cleanup

```bash
# Preview without changing mail.
uv run gmail delete --account you@example.com --dry-run

# Show a fresh preview and prompt before moving its messages to Gmail Trash.
uv run gmail delete --account you@example.com --inbox-age 6mo --archive-age 3mo

# Example: only archive, for a scheduled run (explicit confirmation).
uv run gmail delete --account you@example.com --no-inbox --archive-age 3mo --yes
```

Both Inbox (6 months) and Archive (3 months) are selected by default; use
`--no-inbox` or `--no-archive` to exclude one. Archive means received mail
outside Inbox, Sent, Drafts, Spam and Trash. The web UI also accepts a specific
cutoff date. Its preview expires after 15 minutes and is tied to one account;
changing a selection requires a new preview. Gmail interprets date searches in
its search timezone, not necessarily the local timezone.

Gmail labels overlap: Archive also includes eligible received messages with
custom labels. Moving a message to Trash affects the whole message, including
its other label views. Selecting custom labels individually is planned
separately; the current version selects only Inbox and Archive.

Messages are **moved to Gmail Trash, not permanently deleted immediately**.
Recover them using Gmail before Gmail removes them, normally after 30 days;
account policies may differ. The app does not restore messages itself.

### Scheduled CLI credentials

Scheduled runs require a previously authorized account. To use a credential
without accessing Keychain at run time, run
`uv run gmail export-credentials --account you@example.com` interactively.
After confirmation, this writes `GMAIL_AUTHORIZED_USER_JSON` to the current
directory's `.env`, replacing any existing injected account credential and
restricting the file to the current user. This credential contains a reusable
refresh token in **plaintext**: protect the file, never commit it, and make
sure the scheduled job runs from that directory. Alternatively inject the same
authorized-user JSON through the job's environment. With multiple accounts,
provide the appropriate credential for each invocation; the CLI checks the
authenticated Gmail address against `--account` before touching mail.

## Local UI lifecycle

```bash
make web         # build the UI after editing web-src
make dev-up      # build the UI and start on http://127.0.0.1:8100
make dev-status  # check the managed process and health endpoint
make dev-down    # stop only the managed process
```

Logs and process metadata are under the ignored `.run/` directory. The UI is
for local use only; Docker/Proxmox deployment and remote authentication are not
implemented.

## Development

```bash
uv sync --extra dev     # create the venv + install dev deps
uv run pytest -q        # run the tests
uv run ruff check src tests
```

## Docs, planning & stakeholder updates
The `docs/` tree and the backlog are Markdown in git; **markdown-tools**
([`md2conf`](https://repo.dpsk12.org/amazon-web-services/dps-productivity/markdown-tools),
`md2jira`, `md2pdf`, `mdmermaid`) publish them to Confluence, Jira, and PDF so
stakeholders see progress without reading the repo. Run `mdtools init` to write the
starter `markdown-to-*.toml` settings (raven does this for you when markdown-tools is
installed). Commit the
`markdown-to-*.toml` settings and the `.md2conf/` / `.md2jira/` state folders
(they detect drift); keep the API keys in `.env`, which is **never** committed. See
[`docs/ai/directives/publishing-config-and-state.md`](docs/ai/directives/publishing-config-and-state.md).

## Status

Scaffolded with [raven](https://repo.dpsk12.org/amazon-web-services/dps-productivity/project-raven).
This project follows the suite's AI-IDE working model — see
[`docs/ai/`](docs/ai/README.md). Start new work from the
[backlog](docs/product/backlog/README.md), architecture-first.
