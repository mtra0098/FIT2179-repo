# EMBER — When the Continent Burns

FIT2179 Data Visualisation 2, Monash University, Semester 1 2026.
Author: mtra0098.

Editorial data visualisation of bushfires in Australia, 1950–2024.

## Structure

```
site/
  index.html         single-page site, all sections
  css/style.css      typography, layout, palette
  js/main.js         vega-embed loader
  data/              CSVs (placeholder until real data wired)
  vega/              Vega-Lite JSON specs, one per chart
  img/               (optional) static images
```

## Local preview

Serve the `site/` folder with any static server, e.g.:

```
cd site
python -m http.server 8080
```

Open <http://localhost:8080>.

## Vega-Lite specs

Each chart on the page is rendered from a separate JSON file in `vega/`.
The JSON files are formatted for human readability and linked from the
GitHub repo per assignment requirement.

| File | Idiom |
| ---- | ----- |
| choropleth.json | Choropleth map of Australia |
| state_rank.json | Ranked horizontal bars |
| timeseries.json | Line + area + annotations |
| radial.json | Radial seasonality |
| donut.json | Donut, cause split |
| stack.json | Stacked area causes over time |
| scatter.json | Scatter with regression line |
| multiples.json | Faceted small multiples |
| bivariate.json | Bivariate choropleth (custom) |
| top10.json | Ranked top-10 bars |
| calendar.json | Calendar heatmap |
| connected.json | Connected scatter |

## Data sources

- Bureau of Meteorology Climate Data Online — <https://www.bom.gov.au/climate/data/>
- Geoscience Australia Historical Bushfire Boundaries — <https://ecat.ga.gov.au/geonetwork/srv/api/records/a82c263f-dba6-457a-aafd-bf869fe7171a>
- Digital Earth Australia Hotspots — <https://hotspots.dea.ga.gov.au/>
- data.gov.au National Bushfire Extents NRT — <https://data.gov.au/data/dataset/national-bushfire-extents-near-real-time>

## AI acknowledgement

Text editing and code scaffolding assisted by Claude (Anthropic). All data,
design decisions, and analysis by the author.

## Licence

Code and text released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
