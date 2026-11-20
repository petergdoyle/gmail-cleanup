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

## Local web UI setup

The web UI currently runs **only on localhost** and supports one configured
development user. Its login is separate from Google account authorization.
The local provider is not suitable for network exposure or production;
Authentik and shared multi-user deployment are not implemented.

1. Copy `.env.example` to `.env` in the directory from which you run the app.
   Set `GMAIL_AUTH_PROVIDER=local`, `GMAIL_DEV_USERNAME` and
   `GMAIL_DEV_PASSWORD` to your chosen development credentials. Protect the file
   with `chmod 600 .env`; never commit it. Environment variables override `.env`.
2. Generate an encryption key **once**, after creating `.env`:

   ```bash
   uv run python -c 'from cryptography.fernet import Fernet; from dotenv import set_key; set_key(".env", "GMAIL_ENCRYPTION_KEY", Fernet.generate_key().decode())'
   ```

   The command writes the key to `.env` without displaying it. Keep a secure
   backup separate from the database: losing or replacing this key makes saved
   Google credentials unreadable.
3. In Google Cloud, enable the Gmail API, configure the OAuth consent screen
   and permitted test users, and create an **OAuth client ID for a web
   application**. Add the exact redirect URI
   `http://127.0.0.1:8100/oauth/google/callback` for the default `make ui` or
   `make dev-up` address. If you use another host or port, register its exact
   callback URI instead. Download the client JSON to a private location and set
   `GMAIL_WEB_CREDENTIALS_PATH` to its path in `.env`.
4. Run `make ui` or `make dev-up`, sign in with the development credentials,
   then open **Settings → Connect Google account**. Authorize each account
   separately on Google. Select an account on the Cleanup screen and use
   **Settings → Test selected account** to verify its connection.

Each user identity has separate account and settings records in the ignored
`.run/settings.sqlite` file in the launch directory. Google credentials are
encrypted using `GMAIL_ENCRYPTION_KEY`; SQLite settings are not encrypted.
Removing an account removes its saved local credentials and preferences; it does
not revoke Google's authorization, which can be managed in the Google account.
The encryption key and Google client file must remain outside Git.

## CLI Gmail setup

1. In Google Cloud, enable the Gmail API, configure the OAuth consent screen,
   and create an **OAuth client ID for a desktop application**. Download its
   JSON file to a private location. Google's OAuth testing and verification
   settings may limit which accounts can authorize and how long tokens last.
2. Copy `.env.example` to `.env` in the directory from which you run the app.
   Set `GMAIL_CREDENTIALS_PATH` to the downloaded file (quote paths with spaces),
   or supply the client JSON as `GMAIL_CLIENT_CONFIG_JSON`. Environment variables
   take precedence over `.env`. Never commit credentials or `.env`.
3. Run `uv run gmail auth` for each account and choose the Google account in
   the browser. Each account must grant the Gmail modify permission separately.
   The CLI stores its authorized account credentials in macOS Keychain; these
   accounts are separate from web UI accounts.
4. Run `uv run gmail accounts` to list accounts and
   `uv run gmail test-connection --account you@example.com` to test one.

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
make dev-up      # build, start on http://127.0.0.1:8100, and open a browser
make dev-status  # check the managed process and health endpoint
make dev-down    # stop only the managed process
```

Logs and process metadata are under the ignored `.run/` directory. The UI is
for local use only; Docker/Proxmox deployment and remote authentication are not
implemented. If the browser does not open automatically, visit
http://127.0.0.1:8100 manually. Re-running `make dev-up` opens the already
running managed UI. npm's version-pinned install-script approvals in
`web-src/package.json` must be reviewed when those dependencies change.

## Development

```bash
uv sync --extra dev     # create the venv + install dev deps
uv run pytest -q        # run the tests
uv run ruff check src tests
```

Pull requests run GitHub Actions checks for Python lint, Python tests and the
web build. These checks do not require Google credentials or modify Gmail.

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
