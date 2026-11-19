# gmail-cleanup — Web UI source

A lightweight Vite/React app, served over loopback by the FastAPI backend
in `src/*/ui/server.py`.

## Run it

```bash
gmail ui        # build-if-needed + serve (127.0.0.1, Ctrl-C to stop)
```

`gmail ui` **builds the UI automatically** the first time (it runs the
npm build when `src/*/ui/web/` is missing), then serves it and opens your
browser. No separate build step is required. `make ui` does the same from
the repo root; `make web` builds without serving (e.g. for packaging/CI).

The backend holds any secrets; the browser never does, and nothing is
exposed beyond localhost.
