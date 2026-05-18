/* EMBER — main.js
 * Loads Vega-Lite specs + state rank list + KPI values.
 */

const VEGA_CONFIG = {
  background: null,
  font: 'Inter, system-ui, sans-serif',
  title: {
    font: 'Playfair Display, Georgia, serif',
    fontSize: 16,
    fontWeight: 600,
    anchor: 'start',
    color: '#2B2B2B',
    subtitleFont: 'Inter, sans-serif',
    subtitleFontSize: 11,
    subtitleColor: '#8C8C8C'
  },
  axis: {
    labelColor: '#8C8C8C',
    labelFont: 'JetBrains Mono, monospace',
    labelFontSize: 10,
    titleColor: '#2B2B2B',
    titleFont: 'JetBrains Mono, monospace',
    titleFontSize: 10,
    titleFontWeight: 500,
    domainColor: '#2B2B2B',
    domainWidth: 0.75,
    tickColor: '#8C8C8C',
    tickSize: 4,
    gridColor: '#E6E0D0',
    gridWidth: 0.5,
    grid: true,
    domain: true
  },
  axisX: { grid: false },
  legend: {
    labelColor: '#2B2B2B',
    titleColor: '#2B2B2B',
    labelFont: 'Inter, sans-serif',
    titleFont: 'Inter, sans-serif',
    labelFontSize: 11,
    titleFontSize: 11,
    titlePadding: 8
  },
  view: { stroke: null },
  range: {
    category: ['#B23A1A', '#2B2B2B', '#4A7A4A', '#B4B0A6'],
    ramp: { scheme: 'oranges' }
  }
};

const VEGA_OPTS = {
  actions: false,
  renderer: 'svg',
  config: VEGA_CONFIG
};

const CHARTS = [
  ['#vis-choropleth', 'vega/choropleth.json'],
  ['#vis-timeseries', 'vega/timeseries.json'],
  ['#vis-radial',     'vega/radial.json'],
  ['#vis-donut',      'vega/donut.json'],
  ['#vis-stack',      'vega/stack.json'],
  ['#vis-scatter',    'vega/scatter.json'],
  ['#vis-multiples',  'vega/multiples.json'],
  ['#vis-bivariate',  'vega/bivariate.json'],
  ['#vis-top10',      'vega/top10.json'],
  ['#vis-calendar',   'vega/calendar.json'],
  ['#vis-connected',  'vega/connected.json']
];

function embedAll() {
  CHARTS.forEach(([sel, spec]) => {
    const el = document.querySelector(sel);
    if (!el) return;
    vegaEmbed(sel, spec, VEGA_OPTS).catch(err => {
      el.innerHTML = `<div style="color:#8C8C8C;font-size:12px;padding:24px">Chart unavailable: ${spec}</div>`;
      console.warn('vega-embed failed', spec, err);
    });
  });
}

function loadKpis() {
  fetch('data/kpis.json')
    .then(r => r.json())
    .then(k => {
      document.querySelectorAll('[data-kpi]').forEach(el => {
        const key = el.dataset.kpi;
        if (key && k[key] !== undefined) {
          const span = el.querySelector('span');
          if (span) span.textContent = k[key];
        }
      });
    })
    .catch(() => {});
}

function loadStateRank() {
  fetch('data/fires_state.csv')
    .then(r => r.text())
    .then(csv => {
      const lines = csv.trim().split('\n').slice(1);
      const rows = lines.map(l => {
        const [state, km2, n] = l.split(',');
        return { state, km2: +km2, n: +n };
      }).filter(r => r.km2 > 0).sort((a, b) => b.km2 - a.km2).slice(0, 5);
      const max = rows[0]?.km2 || 1;
      const host = document.querySelector('#state-rank-list');
      if (!host) return;
      host.innerHTML = rows.map((r, i) => `
        <div class="rank-row">
          <span class="ri">${String(i + 1).padStart(2, '0')}</span>
          <div class="rn">
            <span class="rname">${r.state} <b>${r.km2.toLocaleString()}</b></span>
            <div class="rbar"><i style="width:${(r.km2 / max * 100).toFixed(1)}%"></i></div>
          </div>
        </div>
      `).join('');
    })
    .catch(() => {});
}

function buildBivLegend() {
  const host = document.querySelector('#biv-legend');
  if (!host) return;
  const palette = [
    ['#E4E0CB', '#E5C9A6', '#E5A883'],
    ['#B5BFA1', '#C49E7C', '#C57250'],
    ['#82A085', '#A06B4E', '#B23A1A']
  ];
  let cells = '';
  for (let r = 0; r < 3; r++) {
    for (let c = 0; c < 3; c++) {
      cells += `<div style="background:${palette[r][c]}"></div>`;
    }
  }
  host.innerHTML = `
    <div class="biv-legend-row">
      <div style="display:flex;flex-direction:column;align-items:flex-end;gap:8px">
        <span class="biv-axes" style="writing-mode:vertical-rl;transform:rotate(180deg);text-align:center">← FIRE FREQUENCY ↑</span>
      </div>
      <div>
        <div class="biv-legend-grid">${cells}</div>
        <div style="display:flex;justify-content:space-between;margin-top:6px" class="biv-axes">
          <span>COOL</span><span>HOT →</span>
        </div>
      </div>
    </div>
  `;
}

document.addEventListener('DOMContentLoaded', () => {
  embedAll();
  loadKpis();
  loadStateRank();
  buildBivLegend();
});
