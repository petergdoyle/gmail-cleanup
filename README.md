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

(Raw inner loop without installing: `uv run gmail --help`.) Once released,
users install it with `uv tool install <this-repo-url>` — no `make` needed.

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
