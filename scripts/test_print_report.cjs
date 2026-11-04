// Run with: node --test scripts/test_print_report.cjs
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

function app() {
  const nodes = new Map();
  const context = vm.createContext({
    window: { addEventListener() {} },
    document: {
      addEventListener() {},
      querySelector(selector) {
        if (!nodes.has(selector)) nodes.set(selector, { innerHTML: '', value: selector === '#climate-preset' ? 'climate_controlled' : '40' });
        return nodes.get(selector);
      },
    },
    setTimeout, clearTimeout,
  });
  vm.runInContext(fs.readFileSync('src/aquapulse/static/app.js', 'utf8'), context);
  return { run: code => vm.runInContext(code, context), html: id => nodes.get(id)?.innerHTML || '' };
}

test('specifications and care use the analyzed tank, including zero values', () => {
  const a = app();
  a.run(`state.lang = 'en'; state.analysis = { tank: { volume_l: 80, volume_gal: 21.134, filter_gph: 0, water_change_pct: 40, water_change_freq_days: 3, feeding_per_day: 0, food_amount_g: 2, feeding_level: 0 }, budget: null }; renderTankSpecs(); renderCare();`);
  assert.match(a.html('#tank-specs'), /80 L/);
  assert.match(a.html('#tank-specs'), /0 GPH/);
  assert.match(a.html('#tank-specs'), /40% every 3 days/);
  assert.match(a.html('#care-list'), /Feed 0x\/day, 0.0 g/);
});

test('selected blueprint supplies report before analysis is available', () => {
  const a = app();
  a.run(`state.lang = 'en'; state.currentBlueprint = { tank: { volume_l: 60, filter_gph: 250 }, lines: [{ item: 'Filter', category: 'hardware', qty: 2, cost_usd: 5 }] }; renderTankSpecs(); renderReceipt();`);
  assert.match(a.html('#tank-specs'), /60 L/);
  assert.match(a.html('#tank-specs'), /250 GPH/);
  assert.match(a.html('#budget-list'), /Filter/);
  assert.match(a.html('#budget-totals'), /1,200/);
});

test('null and non-finite report values have clean fallbacks', () => {
  const a = app();
  a.run(`state.analysis = { tank: { filter_gph: null, ph: NaN, food_amount_g: Infinity }, budget: null }; renderTankSpecs(); renderReceipt(); renderCare();`);
  for (const id of ['#tank-specs', '#budget-list', '#budget-totals', '#care-list']) {
    assert.ok(a.html(id));
    assert.doesNotMatch(a.html(id), /null|undefined|NaN|Infinity/);
  }
});

test('receipt guards partial items and localizes both currencies in both languages', () => {
  const a = app();
  for (const lang of ['bn', 'en']) for (const currency of ['BDT', 'USD']) {
    a.run(`state.lang = '${lang}'; state.currency = '${currency}'; renderReceipt([null, { item: 'Filter', qty: 2, cost_usd: 5 }, { item: null, qty: null, cost_usd: null }]);`);
    assert.doesNotMatch(a.html('#budget-list'), /null|undefined|NaN/);
    assert.match(a.html('#budget-totals'), /—/);
    a.run(`renderReceipt([null, { item: 'Filter', qty: 2, cost_usd: 5 }]);`);
    const html = a.html('#budget-totals');
    assert.doesNotMatch(html + a.html('#budget-list'), /null|undefined|NaN/);
    assert.match(html, currency === 'USD' ? /\$[০-৯0-9]/ : /(?:৳|BDT )[০-৯0-9]/);
    assert.match(html, lang === 'bn' ? /১,২০০/ : /1,200/);
  }
});

test('full tank overrides preserve schedules, water level and valid zeros', () => {
  const a = app();
  const tank = a.run(`state._tankOverride = { water_level_pct: 70, filter_gph: 0, temperature_c: 0, ph: 0, gh: 0, feeding_per_day: 0, food_amount_g: 0, feeding_level: 0, water_change_pct: 0, water_change_freq_days: 4 }; readTankConfig();`);
  for (const key of ['filter_gph', 'temperature_c', 'ph', 'gh', 'feeding_per_day', 'food_amount_g', 'feeding_level', 'water_change_pct']) assert.equal(tank[key], 0);
  assert.equal(tank.water_level_pct, 70);
  assert.equal(tank.water_change_freq_days, 4);
  a.run(`state._tankOverride = { filter_gph: Infinity, ph: NaN }; renderTankSpecs(); renderCare();`);
  assert.doesNotMatch(a.html('#tank-specs') + a.html('#care-list'), /NaN|Infinity/);
});

test('input edits discard stale analysis and blueprint receipt immediately', () => {
  const a = app();
  a.run(`state.lang = 'en'; state.analysis = { budget: [{ item: 'Old fish', qty: 1, cost_usd: 5 }] }; state.currentBlueprint = { lines: state.analysis.budget }; scheduleAnalyze(); clearTimeout(_analyzeTimer);`);
  assert.doesNotMatch(a.html('#budget-list'), /Old fish/);
  assert.match(a.html('#budget-list'), /calculate/);
  assert.equal(a.run('state.analysis'), null);
  assert.equal(a.run('state.currentBlueprint'), null);
});

test('late analysis responses cannot overwrite a newer result', async () => {
  const a = app();
  a.run(`
    state.stocking.set('guppy', 2);
    const pending = [];
    api = () => new Promise(resolve => pending.push(resolve));
    renderStatus = renderIssues = renderMeters = renderWaterSummary = renderCycleSummary = renderChart = () => {};
    const older = analyze();
    const newer = analyze();
    pending[2]({ tank: { filter_gph: 250 }, compatibility: { score: 100, issues: [] }, budget: [] });
    pending[3]({ steps: [] });
  `);
  await a.run('newer');
  a.run(`pending[0]({ tank: { filter_gph: 50 }, compatibility: { score: 100, issues: [] }, budget: [] }); pending[1]({ steps: [] });`);
  await a.run('older');
  assert.equal(a.run('state.analysis.tank.filter_gph'), 250);
  assert.match(a.html('#tank-specs'), /২৫০ GPH/);
});
