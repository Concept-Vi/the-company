// verify_g8b.js — DATA-BINDING (G8b), verified BY RUNNING the real engine.
// A glyphic facet value can be a BINDING ({bind, map}) that RESOLVES LIVE from a data
// context. The binding IS an encoding set (the EXISTING grammar generalised) run through
// CV_MEANING's ONE resolver (resolveSet) — never a parallel binder.
//
// THE DEMO (the mandate): a glyphic bound to {status:'pending'} renders amber and reads
// "caution"; the SAME spec against {status:'sold'} → sage/green and the read-out changes.
//
// Bars: (1) liveness+purity — the SAME bound spec re-resolves as data changes, both the
// colour token AND describe().sentence differ; (2) the binding is an encoding set (reuse,
// not a fork); (3) the loud-fail trichotomy — missing source / unmapped value / no context
// all THROW; an unbound spec is unchanged.
const fs = require('fs'); global.window = global;
const load = p => { eval(fs.readFileSync(p, 'utf8')); };
['assets/icons/cv-icons.js','assets/icons/cv-vi-glyph.js','assets/icons/cv-shapes.js',
 'assets/icons/cv-edges.js','assets/icons/cv-meaning.js','assets/icons/cv-glyphics.js'].forEach(load);
const M = window.CV_MEANING, G = window.CV_GLYPHIC;
let pass = 0, fail = 0;
const ok = (label, cond, extra) => { if (cond) { pass++; console.log('  ✓', label, extra ? '— ' + extra : ''); } else { fail++; console.log('  ✗ FAIL:', label, extra ? '— ' + extra : ''); } };
const threw = (label, fn) => { try { fn(); fail++; console.log('  ✗ DID NOT THROW:', label); } catch (e) { pass++; console.log('  ✓ threw:', label, '—', e.message.slice(0, 64)); } };

// the property-sale glyphic: a square (a specific listing) holding a house, whose STATE
// (value) is BOUND to the live `status` field. pending→amber/caution, sold→sage/good.
const SALE = {
  form: 'square', symbol: 'house', fill: 'paper',
  value: { bind: 'status', map: { pending: 'warning', accepted: 'active', sold: 'positive' } },
};

console.log('=== isBinding / hasBindings detect a binding (not a per-part {ring,symbol}) ===');
ok('isBinding({bind,map}) true', M.isBinding(SALE.value));
ok('isBinding({ring,symbol}) false (per-part object, not a binding)', !M.isBinding({ ring: 'active', symbol: 'error' }));
ok('isBinding("active") false (a literal)', !M.isBinding('active'));
ok('hasBindings(SALE) true', M.hasBindings(SALE));
ok('hasBindings(literal spec) false', !M.hasBindings({ form: 'square', value: 'active' }));

console.log('\n=== resolveBindings is PURE — never mutates the source spec ===');
const before = JSON.stringify(SALE);
const rPending = M.resolveBindings(SALE, { status: 'pending' });
ok('source spec UNCHANGED after resolve (binding still present)', JSON.stringify(SALE) === before && M.isBinding(SALE.value));
ok('resolved spec has value=\'warning\' (the facet-VALUE, not a token)', rPending.value === 'warning', JSON.stringify(rPending.value));
ok('a non-bound facet copied through (form=square)', rPending.form === 'square' && rPending.symbol === 'house');

console.log('\n=== LIVENESS: the SAME spec, two data contexts — colour AND read-out both change ===');
const goldTok = G.colorForValue('gold');
// pending
const composedPending = G.compose(SALE, { data: { status: 'pending' } });
const descPending = G.describe(SALE, { status: 'pending' });
const amberTok = G.colorForValue('amber');
ok('pending → renders AMBER (the warning token)', composedPending.svg.includes(amberTok), 'amber=' + amberTok);
ok('pending → read-out says "caution"', /caution/.test(descPending.sentence), descPending.sentence);
// sold — the SAME SALE object, new context
const composedSold = G.compose(SALE, { data: { status: 'sold' } });
const descSold = G.describe(SALE, { status: 'sold' });
const sageTok = G.colorForValue('sage');
ok('sold → renders SAGE/green (the positive token)', composedSold.svg.includes(sageTok), 'sage=' + sageTok);
ok('sold → read-out changes to "good — go"', /good — go/.test(descSold.sentence), descSold.sentence);
// the load-bearing assertions: the SAME spec produced DIFFERENT colour AND DIFFERENT sentence
ok('LIVE: same spec, the rendered colour DIFFERS (amber ≠ sage)', composedPending.svg.includes(amberTok) && composedSold.svg.includes(sageTok) && amberTok !== sageTok);
ok('LIVE: same spec, the read-out DIFFERS (pending ≠ sold sentence)', descPending.sentence !== descSold.sentence);
// accepted → active/gold, a third value off the same spec
const descAccepted = G.describe(SALE, { status: 'accepted' });
ok('accepted → read-out says "active"', /active/.test(descAccepted.sentence), descAccepted.sentence);

console.log('\n=== REUSE: the binding IS an encoding set through the ONE resolver (resolveSet) ===');
// the SAME resolver the System-Map channels run through, given a glyphic-style set.
const setVal = M.encodings.resolveSet({ facet: 'status', kind: 'discrete', values: { pending: 'warning', sold: 'positive' } }, { status: 'sold' });
ok('resolveSet (discrete) maps a data value → appearance', setVal === 'positive', setVal);
// a SCALE set (continuous) — interpolates across stops, the same path the link-heat channel uses.
const heat = M.encodings.resolveSet({ facet: 'links', kind: 'scale', domain: [0, 100], stops: [[90,84,72],[224,162,16],[224,90,60]] }, { links: 100 });
ok('resolveSet (scale) interpolates to the top stop at the domain max', heat[0] === 224 && heat[2] === 60, JSON.stringify(heat));
const heatMid = M.encodings.resolveSet({ facet: 'links', kind: 'scale', domain: [0, 100], stops: [[0,0,0],[100,100,100]] }, { links: 50 });
ok('resolveSet (scale) interpolates the MIDPOINT', heatMid[0] === 50, JSON.stringify(heatMid));

console.log('\n=== LOUD-FAIL trichotomy (the law) ===');
// (a) the bound source field is MISSING from the context → throw ("missing binding source")
threw('(a) missing binding source (field absent from context)', () => G.compose(SALE, { data: { foo: 'bar' } }));
threw('(a) missing binding source (describe)', () => G.describe(SALE, { other: 1 }));
// (b) the data value is NOT in the map and there is no fallback → throw
threw('(b) data value not in the map, no fallback', () => G.compose(SALE, { data: { status: 'withdrawn' } }));
// (c) the spec carries a binding but NO context is given → throw (clear message, not downstream)
threw('(c) bound spec, no data context (compose)', () => G.compose(SALE));
threw('(c) bound spec, no data context (describe)', () => G.describe(SALE));
threw('(c) bound spec, no data context (resolveBindings direct)', () => M.resolveBindings(SALE));
// present-but-empty source (null) is not a silent skip — it throws
threw('(c′) present-but-empty source (status:null)', () => G.compose(SALE, { data: { status: null } }));
// (d) an UNBOUND spec + no context → unchanged (the pure pass-through; NO throw)
const plain = G.describe({ form: 'square', symbol: 'house', fill: 'paper', value: 'active' });
ok('(d) unbound spec, no context → composes/reads unchanged (no throw)', /active/.test(plain.sentence), plain.sentence);
const plainCompose = G.compose({ form: 'square', symbol: 'house', fill: 'paper', value: 'active' });
ok('(d) unbound compose → renders gold (active token), no binding needed', plainCompose.svg.includes(goldTok));

console.log('\n=== fallback path (authored) resolves instead of throwing ===');
const SALE_FB = { form: 'square', symbol: 'house', fill: 'paper',
  value: { bind: 'status', map: { sold: 'positive' }, fallback: 'neutral' } };
const descFb = G.describe(SALE_FB, { status: 'withdrawn' });   // 'withdrawn' not in map → fallback 'neutral'
ok('a binding WITH a fallback resolves an unmapped value to the fallback', /quiet default/.test(descFb.sentence), descFb.sentence);

console.log('\n=== a RELATION can be data-bound too (G8b.4 foreshadow: a graph of bound glyphics) ===');
// the listing —part-of→ the agency, edge state bound to the same status.
const REL = {
  source: { form: 'square', symbol: 'house', fill: 'paper', value: { bind: 'status', map: { pending: 'warning', sold: 'positive' } } },
  target: { form: 'hex', symbol: 'gear', fill: 'paper' },
  edge: { line: 'solid', kind: 'part-of', lineColor: { bind: 'status', map: { pending: 'pending', sold: 'approved' } } },
};
const relPending = G.composeRelation(REL, { data: { status: 'pending' } });
const relSold = G.composeRelation(REL, { data: { status: 'sold' } });
ok('relation: pending edge reads "pending"', /pending/.test(relPending.sentence), relPending.sentence);
ok('relation: sold edge reads "approved"', /approved/.test(relSold.sentence), relSold.sentence);
ok('relation: the SAME relation spec, the sentence DIFFERS by data', relPending.sentence !== relSold.sentence);
ok('relation: source still UNMUTATED (binding intact)', M.isBinding(REL.source.value));

console.log('\n----------------------------------------');
console.log('G8b verify:  ' + pass + ' passed, ' + fail + ' failed');
if (fail) process.exit(1);
