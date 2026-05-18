# FIT2179 Assignment 2: Submission Package

## Contents

- `site/`: Single-page web visualisation. Deploy to GitHub Pages from this folder.
  - `index.html`
  - `css/style.css`
  - `js/main.js`
  - `data/`: Cleaned CSVs and AU states GeoJSON
  - `vega/`: 11 Vega-Lite JSON specs (one per chart)
- `scripts/eda.py`: Python script that produced the cleaned CSVs from raw BOM + GA HBB data.
- `spec/`: Original A2 assignment brief.

## Data sources

- Bureau of Meteorology: Climate Data Online (annual + DJF tmean and rain, 8 regions, 1910-2024)
- Geoscience Australia: Historical Bushfire Boundaries v2 ArcGIS Feature Service (queried via REST aggregates)
- AU state GeoJSON: public CC0 file mirrored in `data/au_states.json`

## AI use

Claude (Anthropic) assisted with: prose drafting from outlines, code scaffolding, copy-editing.
All data, source selection, design choices, and analysis are the author's own.
