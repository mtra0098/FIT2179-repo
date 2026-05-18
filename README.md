# FIT2179 Assignment 2 — Submission Package

## Contents

- `site/` — Single-page web visualisation. Deploy to GitHub Pages from this folder.
  - `index.html`
  - `css/style.css`
  - `js/main.js`
  - `data/` — Cleaned CSVs and AU states GeoJSON
  - `vega/` — 11 Vega-Lite JSON specs (one per chart)
- `scripts/eda.py` — Python script that produced the cleaned CSVs from raw BOM + GA HBB data.
- `spec/` — Original A2 assignment brief.
- `stitch_prompts.txt` — Design prompt used to scaffold the UI.

## Before submitting on Moodle

1. Replace placeholders in `site/index.html`:
   - `[YOUR NAME]` × 4
   - `[YOUR GITHUB REPO URL]`
   - `[USERNAME]`
2. Push `site/` to a public GitHub repo, enable GitHub Pages.
3. Hand-draw the sketch on paper. Scan to PDF. Add to repo.
4. Submit on Moodle:
   - URL to GitHub Pages site
   - URL to sketch PDF on GitHub
   - 500-word blurb (Domain/Why/Who, What, How)

## Data sources

- Bureau of Meteorology — Climate Data Online (annual + DJF tmean and rain, 8 regions, 1910–2024)
- Geoscience Australia — Historical Bushfire Boundaries v2 ArcGIS Feature Service (queried via REST aggregates)
- AU state GeoJSON — public CC0 file mirrored in `data/au_states.json`

## AI use

Claude (Anthropic) assisted with: prose drafting from outlines, code scaffolding, copy-editing.
All data, source selection, design choices, and analysis are the author's own.
