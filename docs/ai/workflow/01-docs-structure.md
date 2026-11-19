# 01 — The Docs Structure

Work is grounded in documentation. Before an effort writes code, the docs that
frame it should already exist; the code then realizes what the docs describe. This
keeps intent reviewable and keeps the product legible to people who don't read the
code.

## The standard `docs/` taxonomy

Every project uses the same top-level shape so projects read consistently and so
any publishing tool has a predictable surface:

```text
docs/
├── README.md                 # the documentation index — what lives where
├── architecture/             # system design: the "why" and "how"
│   ├── NN-*.md               # numbered design docs, in reading order
│   └── decisions/            # ADRs (significant, hard-to-reverse decisions)
├── product/                  # product management
│   ├── backlog/              # epics (E{n}-*.md) + task-log, bug-log, design-decision-log
│   ├── updates/              # dated stakeholder updates built from the three logs (07)
│   └── journeys/             # user/persona journeys (design-time)
├── help/                     # end-user help & user guides (see the web-UI rule below)
├── stakeholders/             # positioning for external / oversight audiences
├── operations/               # env & tooling setup, runbooks, operational notes
└── ai/                       # THIS tree — how we work with the agent
```

Conventions that hold everywhere:

- **Numbered files** (`00-…`, `01-…`) order documents within a folder.
- **Every folder has a `README.md`** that acts as its index.
- Content for **external eyes** (architecture, stakeholders) is written to be read
  on its own, not as a comment on the code.

### Web-UI apps: actor/journey help lives under `help/`

If the project ships a **web UI** (anything a user operates in a browser), its
**actor/journey-targeted end-user documentation lives under `docs/help/`** — the
"how do I do this task in the running app" material, framed by the actor performing
it. This is distinct from `product/journeys/`:

- **`product/journeys/`** — *design-time* persona workflows: who we build for and
  the path they take through the product. A planning/design artifact.
- **`help/`** — *end-user* how-to for the running UI: searchable guides an actor
  consults while using the app.

The two are linked, not merged: a journey may **reference the help** relevant to
that journey, and a help page serves the task a journey describes. Keep the
design-time narrative in `journeys/` and the operate-the-app guidance in `help/`.

## Publishing compliance

> **SUBSTITUTE: docs publisher.** This model assumes *some* tool renders the
> `docs/` tree to a shared wiki/space and *some* tool imports the backlog into an
> issue tracker. Name your tools here (or drop the publish step entirely if the
> repo docs are the only surface you need). Nothing below depends on a particular
> product; it depends only on keeping the Markdown clean and the backlog in a
> parseable Epic → Feature → Story shape.
>
> In DPS projects the publisher is **markdown-tools** (`md2conf` → Confluence,
> `md2jira` → Jira, `md2pdf` → PDF, `mdmermaid` → diagram gate), scaffolded
> alongside **raven**. Its run settings (`markdown-to-*.toml`) and drift state
> (`.md2conf/`, `.md2jira/`) are **committed**; only `.env` is not — see the
> [publishing config & state directive](../directives/publishing-config-and-state.md).

The taxonomy is also a **publish surface**, so authoring must stay compatible:

- The `help/`, `architecture/`, `product/`, `stakeholders/`, `operations/` sections
  are intended to publish to a shared **documentation space** (a wiki/Confluence/
  docs site). Keep Markdown clean and section-shaped; keep the publisher's section
  configuration in sync when a new top-level folder is added.
- The backlog under `product/backlog/` is intended to publish to an **issue
  tracker**, so it must follow the epic → feature → story table format
  ([03 — Backlog & Logs](./03-backlog-and-logs.md)). The three logs beside it have
  fixed formats too, because the weekly update reads them.
- `product/updates/` publishes with the other docs sections and is **never** pushed to
  the tracker.
- **Diagrams** (e.g. Mermaid) must validate before they ship. Validate locally
  before committing docs that contain diagrams.

## Create the docs before the effort — but allow emergence

The rule: **the framing docs should exist before the effort starts.** An effort
that changes architecture or adds a capability begins by writing or updating the
architecture/goals/considerations docs, then breaks the work into stories.

The honest corollary: **things emerge.** If an effort turns out to need docs that
don't exist yet — a new architecture doc, an ADR, an operations note — **create
them as part of the effort.** They should have existed first; sometimes direction
shifts mid-flight. Creating them late is correct; skipping them is not. Note in the
task-log that the doc was added.

## Where different content goes

- **System design, rationale, request flow, models** → `architecture/`.
- **A significant, hard-to-reverse decision** (with considerations + alternatives +
  chosen path) → `architecture/decisions/` as an ADR. A lighter call → the design
  decision log. See [decisions/](../decisions/README.md).
- **How to set up, run, or operate the thing; reusable procedures** →
  `operations/`.
- **What we're building and for whom** → `product/` (backlog + journeys).
- **What moved this period, for stakeholders** → `product/updates/`, built from the
  logs ([07 — Weekly Updates](./07-weekly-updates.md)).
- **Positioning for oversight / other teams** → `stakeholders/`.
