# Directive — UI Mockup Format

**Rule:** Commit every UI mockup as a **matching `.svg` + `.png` pair** under
`docs/product/mockups/`. The SVG is the editable source; the PNG is always
rendered from that SVG (never hand-made). Author/edit the SVG, render the PNG,
commit both. Never commit only one of the pair.

## Why

The two formats serve two readers, and both are needed:

- **SVG** is text — the only format the agent can author and *edit precisely*
  (move one element without disturbing the rest). It also renders as a vector for
  the human in the IDE and in most git hosts.
- **PNG** is a frozen raster — read reliably when *judging* the rendered result
  (overlap, clipping, spacing), and it renders identically everywhere with no
  toolchain. It's the unambiguous snapshot of what was reviewed.

PNG-only breaks the agent's edit path (forces a full re-author to nudge one
element); SVG-only makes visual review unreliable. Keeping both, with the PNG
generated from the SVG, is cheap and keeps them from drifting.

## Do

- Author/edit the **SVG**, then render the PNG from it:
  `rsvg-convert -w 2048 -h 1400 <name>.svg -o <name>.png`.
- Keep both files on the **same base name** (`dashboard-02-detail.svg` + `.png`).
- When reviewing a mockup, look at the **PNG** (faithful render); when creating or
  changing one, edit the **SVG**.
- Re-render the PNG in the **same commit** as any SVG edit, so the pair stays in
  sync.
- Validate the SVG parses (`xmllint --noout <name>.svg`) before rendering.

## Don't

- Don't commit a PNG without its SVG source, or an SVG without its rendered PNG.
- Don't hand-edit or hand-produce a PNG — it must come from `rsvg-convert` of the
  committed SVG.
- Don't judge layout from raw SVG markup alone — render and look at the PNG.
- Don't let the pair drift: never change the SVG and leave a stale PNG (or vice
  versa).

## Note

Applies to UI mockups (the "mock before UI code" step —
[workflow 06](../workflow/06-ui-mockups.md)). Rendering uses `rsvg-convert`
(librsvg); if it's unavailable, install it rather than committing an unrendered
or mismatched pair.
