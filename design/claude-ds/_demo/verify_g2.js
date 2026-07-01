// verify_g2.js — the G2 FACET remainder, verified BY RUNNING the real engine.
// (a) edge LINE-COLOUR = relation state, as a meaning field + rendered in edgeSVG.
// (b) SIZE-as-comparison: a size difference between two related nodes reads "more than".
// (c) INDEPENDENT ring vs symbol: ring (frame) and symbol carry colour/motion separately,
//     in compose + markSVG; the read-out reflects ring-state on the reference, symbol-state
//     on the thing.
// Bar (LAW): present-unknown value THROWS; absent contributes nothing; valid reads.
const fs = require('fs'); global.window = global;
const load = p => { eval(fs.readFileSync(p, 'utf8')); };
['assets/icons/cv-icons.js','assets/icons/cv-vi-glyph.js','assets/icons/cv-shapes.js',
 'assets/icons/cv-edges.js','assets/icons/cv-meaning.js','assets/icons/cv-glyphics.js'].forEach(load);
const M = window.CV_MEANING, G = window.CV_GLYPHIC, S = window.CV_SHAPES;
let pass = 0, fail = 0;
const ok = (label, cond, extra) => { if (cond) { pass++; console.log('  ✓', label, extra ? '— ' + extra : ''); } else { fail++; console.log('  ✗ FAIL:', label, extra ? '— ' + extra : ''); } };
const threw = (label, fn) => { try { fn(); fail++; console.log('  ✗ DID NOT THROW:', label); } catch (e) { pass++; console.log('  ✓ threw:', label, '—', e.message.slice(0, 56)); } };

console.log('=== (a) LINE-COLOUR is a meaning FIELD (relation state) ===');
['blocked','approved','active','pending','neutral'].forEach(v => {
  const f = M.field('lineColor', v);
  ok('field(lineColor,' + v + ')', !!f.feeling && f.type === 'relation-state', JSON.stringify({feeling:f.feeling, token:f.token, phrase:f.phrase}));
});

console.log('\n=== (a) LINE-COLOUR renders in CV_SHAPES.edgeSVG (explicit colour wins) ===');
const clayCss = G.colorForValue('clay');           // the CSS the clay token resolves to
const edgeRed = S.edgeSVG({ line:'solid', direction:'to', ink:'gold' }, { color: clayCss });
ok('edgeSVG uses the passed colour (not the ink default)', edgeRed.includes(clayCss) && !edgeRed.includes('var(--accent-gold)'), 'col=' + clayCss);
const edgeDefault = S.edgeSVG({ line:'solid', direction:'to', ink:'gold' }, {});
ok('edgeSVG without a colour falls to the edge-kind ink', edgeDefault.includes('var(--accent-gold)'));

console.log('\n=== (a) LINE-COLOUR threads through composeRelation (render + read-out) ===');
const baseRel = { source:{form:'square',symbol:'house',fill:'paper'}, target:{form:'octagon',symbol:'browser',fill:'wash'} };
const relBlocked = G.composeRelation(Object.assign({}, baseRel, { edge:{ line:'solid', kind:'face', lineColor:'blocked' } }));
ok('blocked relation read-out says its state', /blocked/.test(relBlocked.sentence), relBlocked.sentence);
ok('blocked relation renders the clay line colour', relBlocked.html.includes(G.colorForValue('clay')) || relBlocked.html.includes(M.field('lineColor','blocked').token));
const relApproved = G.composeRelation(Object.assign({}, baseRel, { edge:{ line:'solid', kind:'face', lineColor:'approved' } }));
ok('approved relation read-out says its state', /approved/.test(relApproved.sentence), relApproved.sentence);

console.log('\n=== (a) LINE-COLOUR loud-fail trichotomy ===');
threw('present-unknown lineColor (describeRelation)', () => M.describeRelation({ source:{form:'square'}, target:{form:'octagon'}, edge:{ line:'solid', lineColor:'ultraviolet' } }));
threw('present-unknown lineColor (composeRelation)', () => G.composeRelation(Object.assign({}, baseRel, { edge:{ line:'solid', kind:'face', lineColor:'ultraviolet' } })));
const relNoColor = G.composeRelation(Object.assign({}, baseRel, { edge:{ line:'solid', kind:'face' } }));
ok('ABSENT lineColor contributes nothing (no throw, no fabricated state)', !!relNoColor.sentence && !relNoColor.read.edge.state);

console.log('\n=== (b) SIZE-as-comparison: a size difference reads "more than" ===');
const cmpMore = M.compareSize(80, 40);
ok('compareSize(80,40) → "more"', cmpMore && cmpMore.value === 'more', cmpMore && cmpMore.phrase);
ok('compareSize(40,80) → "less"', M.compareSize(40,80).value === 'less');
ok('compareSize(50,50) → "equal"', M.compareSize(50,50).value === 'equal');
ok('compareSize(null,null) → null (nothing to compare)', M.compareSize(null,null) === null);
ok('compareSize(80,null) → null (only one authored)', M.compareSize(80,null) === null);
const relSize = M.describeRelation({ source:{form:'square',symbol:'house',fill:'paper',size:90}, target:{form:'square',symbol:'file',fill:'paper',size:40}, edge:{ line:'solid', kind:'part-of' } });
ok('relation with a size difference reads "more than"', /more than/.test(relSize.sentence), relSize.sentence);
const relSameSize = M.describeRelation({ source:{form:'square',symbol:'house',fill:'paper'}, target:{form:'square',symbol:'file',fill:'paper'}, edge:{ line:'solid', kind:'part-of' } });
ok('relation with NO authored sizes → no comparison clause', !/more than|less than|as much as/.test(relSameSize.sentence), relSameSize.sentence);
threw('present-unknown size outcome (field)', () => M.field('size', 'gigantic'));

console.log('\n=== (c) INDEPENDENT ring vs symbol — COLOUR ===');
// NB: ring='positive'(sage) is DELIBERATELY non-default — the default ring is gold, so a
// gold ring-state would not discriminate (it passes whether or not per-part resolution ran).
// sage ≠ default ≠ the symbol's clay → this assertion actually proves the ring path works.
const split = G.compose({ form:'hex', symbol:'gear', fill:'paper', value:{ ring:'positive', symbol:'error' } });
const ringCss = G.colorForValue('positive'), symCss = G.colorForValue('error');
const defaultRing = G.colorForValue('gold');
ok('ring stroke uses ring-state colour (non-default, discriminating)', split.svg.includes(ringCss) && ringCss !== defaultRing, 'ring=' + ringCss + ' (default was ' + defaultRing + ')');
ok('symbol ink uses symbol-state colour (different from ring)', split.svg.includes(symCss) && ringCss !== symCss, 'symbol=' + symCss);
const descSplit = M.describe({ form:'hex', symbol:'gear', fill:'paper', value:{ ring:'positive', symbol:'error' } });
ok('read-out carries ring-state AND symbol-state separately', descSplit.meaningSet.some(m=>m.type==='ring-state') && descSplit.meaningSet.some(m=>m.type==='symbol-state'), descSplit.sentence);
const descShared = M.describe({ form:'hex', symbol:'gear', fill:'paper', value:'active' });
ok('a single value → both parts share one "state" (back-compat)', descShared.meaningSet.some(m=>m.type==='state') && !descShared.meaningSet.some(m=>m.type==='ring-state'));

console.log('\n=== (c) INDEPENDENT ring vs symbol — MOTION (two distinct hooks) ===');
const moSplit = G.compose({ form:'hex', symbol:'gear', fill:'paper', motion:{ ring:'spin', symbol:'none' } });
const ringHook = G.motionClassFor('spin');
ok('the composed SVG has a ring motion <g> hook', moSplit.svg.includes('class="' + ringHook + '"'), 'ring hook=' + ringHook);
ok('the wrapper stays still under per-part motion (whole-glyphic class is none)', moSplit.motionClass === '' );
const moBoth = G.compose({ form:'hex', symbol:'gear', fill:'paper', motion:{ ring:'spin', symbol:'pulse' } });
const symHook = G.motionClassFor('pulse');
ok('ring and symbol carry DIFFERENT motion hooks', moBoth.svg.includes(ringHook) && moBoth.svg.includes(symHook) && ringHook !== symHook, ringHook + ' / ' + symHook);
const moSingle = G.compose({ form:'hex', symbol:'gear', fill:'paper', motion:'glow' });
ok('single motion value → wrapper carries it (back-compat, no per-part hooks)', moSingle.motionClass === G.motionClassFor('glow'));

console.log('\n=== (c) loud-fail trichotomy on per-part state (at the MEANING/read-out layer) ===');
// NB: loud-fail for ring/symbol STATE is enforced by field('color',…) inside describe — the
// MEANING layer. compose's colour path (colorForValue→tok) passes an unknown through as a
// literal (pre-existing colour-facet behaviour, NOT introduced here); the read-out is where a
// present-unknown state throws. The NEW facets (lineColor, size) loud-fail directly via field().
threw('present-unknown ring state (describe → field)', () => M.describe({ form:'hex', symbol:'gear', fill:'paper', value:{ ring:'chartreuse' } }));
threw('present-unknown symbol state (describe → field)', () => M.describe({ form:'hex', symbol:'gear', fill:'paper', value:{ symbol:'chartreuse' } }));
const descRingOnly = M.describe({ form:'hex', symbol:'gear', fill:'paper', value:{ ring:'active' } });
ok('ABSENT symbol-state contributes nothing (ring-only authored, no throw)', !!descRingOnly.sentence);

console.log('\n=== facet wiring gate: both lists carry the new facets ===');
ok('lineColor in MEANING_FACETS (else field() would throw)', M.facets.indexOf('lineColor') !== -1);
ok('size in MEANING_FACETS', M.facets.indexOf('size') !== -1);
ok('lineColor + size have a meaning-type', M.types().lineColor === 'relation-state' && M.types().size === 'comparison');

console.log('\n----------------------------------------');
console.log('G2 verify:  ' + pass + ' passed, ' + fail + ' failed');
if (fail) process.exit(1);
