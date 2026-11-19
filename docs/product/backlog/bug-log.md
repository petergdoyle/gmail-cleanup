# gmail-cleanup — Bug Log

[Back to Backlog Index](./README.md)

Defects and their resolutions, newest first.

## Open & In-Progress Bugs

None.

## Resolved

| ID | Summary | Area | Resolution | Fixed in | Fixed on |
|----|---------|------|------------|----------|----------|
| B01 | Source-built wheel omitted the generated UI | Packaging | Include built UI in the source distribution and build it before installation. | `feat/e1-delete-old-messages` | 2026-11-19 |

## Details / repro notes

### B01 — Source-built wheel omitted the generated UI — FIXED

- **Area / journey:** Packaging and UI.
- **Severity:** High, proposed; installed users could not open the UI.
- **Noticed:** 2026-11-19, while verifying [T01](./task-log.md).
- **Reproduction:** Build the UI, run `uv build`, then inspect the wheel.
- **Expected:** The wheel contains `ui/web/index.html` and the generated assets.
- **Actual:** The wheel contained no `ui/web` files.
- **Root cause:** The default build creates the wheel from an sdist that omitted
  the ignored generated UI, despite the wheel artifact setting.
- **Fix:** Include UI artifacts in the sdist and build the UI in `make install`.
- **Verification:** After `npm run build` and `uv build`, the wheel contains the
  UI index, JavaScript and CSS. Live installation from a published wheel was not
  exercised.
- **Related:** [T01](./task-log.md).
