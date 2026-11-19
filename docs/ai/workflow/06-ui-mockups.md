# 06 — UI Mockups Before UI Code

When an effort builds or meaningfully changes a **user interface**, add a mockup
step *before* writing UI code. It is cheaper to agree on the layout, the tab/screen
set, and the interaction model as static art than to discover them in the
framework. The mockups give the human a concrete thing to react to — and to
adjust — before any component exists.

This step is **UI-specific**. Efforts with no UI (a library, a CLI change, a
service, a docs change) skip it entirely.

## When it applies

Insert the mockup step when the effort introduces or reshapes a surface a user
operates — a web UI, a new screen or tab, a redesigned flow. Pure services and
command-line tools don't get mockups; if a component in a larger UI is CLI-only,
the mockup for it is just a short note saying so and why.

In the effort loop it sits **after the work is broken into stories and before
implementation** — the same place framing docs sit for non-UI work. Treat it as
part of the "ensure framing exists" gate.

## Mockups live under `product/mockups/` as SVG + PNG pairs

- Store each screen under `docs/product/mockups/` as **two files with the same
  base name** — a vector **`.svg`** and a rendered **`.png`** (e.g.
  `dashboard-02-detail.svg` + `.png`). Name them so the screen is obvious.
- Add a `README.md` index in that folder: what the UI is, the shared style
  vocabulary (colors, canvas size), the screen table, and the regenerate command.

**Why both — the two serve different readers.** This is deliberate, not
redundant:

- **SVG is the editable source.** A mockup is authored and edited as text, so SVG
  is the precise create/recreate path: an element can move or change without
  disturbing the rest. An agent cannot author or edit a raster. The human reads it
  fine too — it renders as a vector in the IDE and in most git hosts.
- **PNG is the frozen rendered artifact.** Judging a mockup (overlap, clipping,
  spacing, hierarchy) is a *visual* act, and a rasterized image is read reliably
  for that, by agent and human alike. A PNG also renders identically everywhere
  with no toolchain, so it's an unambiguous snapshot of what was reviewed.

The split maps to perspective: the **human** optimizes for UX and sees either
equally well; the **agent** needs SVG to create/recreate accurately and PNG to
interpret the result faithfully. Disk is cheap; keep both.

**The PNG is generated from the SVG, never hand-made** — so the pair can't drift.
Edit the SVG, then re-render:

```sh
rsvg-convert -w 2048 -h 1400 <name>.svg -o <name>.png   # commit both files
```

This pairing is a hard rule, stated imperatively in the
[ui-mockup-format directive](../directives/ui-mockup-format.md).

## Review before code

The mockup set is a **review gate**, like any framing. Present the rendered PNGs,
hold for the human to react, and adjust the SVG (re-rendering the PNG) until
they're agreed — *then* start building. Record the "mock first" decision in the
design-decision log (or an ADR if the UI direction is significant), link the
mockups from the relevant epic, and note the mockup step in the task-log.

The build then realizes what the mockups describe, the same way code realizes the
framing docs. If the implementation forces a layout change, update the mockup too
so the artifact and the app don't drift.

## Why this is in the model

It serves the two convictions directly. **Human agency:** the human shapes the UI
by reacting to something concrete before it's built, rather than reviewing a
finished app and asking for rework. **Durability:** the mockups are plain files in
the repo — SVG and PNG both open forever with no AI, IDE, or design tool required.
