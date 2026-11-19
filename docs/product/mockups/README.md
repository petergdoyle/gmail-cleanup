# gmail-cleanup — UI Mockups

This project has a UI, so per the working model (workflow 06) mock each
screen **before** writing UI code, and get the mockups agreed first.

## Convention

Each screen is a **matching `.svg` + `.png` pair** on the same base name
(e.g. `01-home.svg` + `01-home.png`). The SVG is the editable source; the
PNG is rendered from it — never hand-made:

```sh
rsvg-convert -w 2048 -h 1400 01-home.svg -o 01-home.png   # commit both
```

Review the PNGs, adjust the SVGs, agree — *then* build the screens.
