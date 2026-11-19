# gmail-cleanup — UI Mockups

Proposed UI for navigating Google accounts, selecting messages to move to Gmail
Trash, and configuring Gmail access. The revised mockups were approved on
2026-11-19. On the same date, cleanup and confirmation mockups were updated
with label-overlap warnings; these warning changes await review. Account names
and counts are illustrative. Keep each account's selections while the app
remains open.

The shared style uses a dark sidebar, light background, blue primary actions,
and a 1200 × 980 canvas. Message counts and paths are illustrative.

| Screen | Editable source | Review image |
|--------|-----------------|--------------|
| Cleanup and preview | [SVG](./01-cleanup.svg) | [PNG](./01-cleanup.png) |
| Confirm move to Trash | [SVG](./02-confirm.svg) | [PNG](./02-confirm.png) |
| Admin and connection | [SVG](./03-admin.svg) | [PNG](./03-admin.png) |

## Convention

Each screen is a **matching `.svg` + `.png` pair** on the same base name
(e.g. `01-home.svg` + `01-home.png`). The SVG is the editable source; the
PNG is rendered from it — never hand-made:

```sh
rsvg-convert -w 2048 -h 1400 01-cleanup.svg -o 01-cleanup.png
```

Run the same command for the other screen names. Review the PNGs, adjust the
SVGs, agree — *then* build the screens.
