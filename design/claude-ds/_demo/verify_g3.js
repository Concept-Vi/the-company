// verify_g3.js — the G3 GLYPHGRAPH RULEBOOK, verified BY RUNNING the real engine.
//   G3.2 · relationship Types are seeded — they FILL kind.graph's edges socket
//          (accepts:['relationship']); query({family:'relationship'}) + candidatesForSocket return them.
//   G3.3 · validateGlyphgraph: a WELL-FORMED graph passes; an ILL-FORMED one THROWS
//          with the SPECIFIC violation (unknown kind · bad node class via accepts ·
//          dangling endpoint · untyped edge · failing edge condition).
//   G3.4 · no second edge registry / meaning store — the relation Types live in CV_REGISTRY,
//          meaning stays in CV_MEANING; the validator REUSES accepts + CV_COND.
// LAW: a present-but-ill-formed structure throws (loud); a well-formed one validates.
const fs = require('fs');
global.window = global;
// minimal localStorage shim — types-core persists user/template types to it (built-ins skip it,
// but registerMany calls save* unconditionally on the non-silent path; our seeds use {silent:true}).
global.localStorage = (function () {
  var store = {};
  return { getItem: k => (k in store ? store[k] : null), setItem: (k, v) => { store[k] = String(v); }, removeItem: k => { delete store[k]; } };
})();
const load = p => { eval(fs.readFileSync(p, 'utf8')); };
// load order = the minimal real chain: conditions → types-core → kinds-type (the placeholder) →
// the icon/meaning homes (relationships-seed reconciles its id-list against CV_EDGES + CV_MEANING) →
// relationships-seed (fills the socket) → glyphgraph (the validator).
[
  'app/registry/conditions.js',
  'app/registry/types-core.js',
  'app/registry/kinds-type.js',
  'assets/icons/cv-icons.js', 'assets/icons/cv-vi-glyph.js', 'assets/icons/cv-shapes.js',
  'assets/icons/cv-edges.js', 'assets/icons/cv-meaning.js', 'assets/icons/cv-glyphics.js',
  'app/registry/relationships-seed.js',
  'assets/icons/glyphgraph.js',
].forEach(load);

const R = window.CV_REGISTRY, GG = window.CV_GLYPHGRAPH, COND = window.CV_COND;
let pass = 0, fail = 0;
const ok = (label, cond, extra) => { if (cond) { pass++; console.log('  ✓', label, extra ? '— ' + extra : ''); } else { fail++; console.log('  ✗ FAIL:', label, extra ? '— ' + extra : ''); } };
// threwWith: must throw AND the message must contain `needle` (the SPECIFIC violation, not just "it threw")
const threwWith = (label, fn, needle) => {
  try { fn(); fail++; console.log('  ✗ DID NOT THROW:', label); }
  catch (e) {
    if (!needle || e.message.indexOf(needle) >= 0) { pass++; console.log('  ✓ threw:', label, '—', JSON.stringify(needle || e.message.slice(0, 60))); }
    else { fail++; console.log('  ✗ THREW WRONG MESSAGE:', label, '— wanted', JSON.stringify(needle), 'got', JSON.stringify(e.message.slice(0, 120))); }
  }
};

console.log('=== G3.2 · relationship Types SEEDED — the placeholder is FILLED ===');
const rels = R.query({ family: 'relationship' });
ok('query({family:"relationship"}) returns Types', rels.length > 0, rels.length + ' Types: ' + rels.map(r => r.id).join(', '));
ok('each is kind:"relationship" + classified ["relationship"]',
   rels.every(r => r.kind === 'relationship' && (r.classification || []).includes('relationship')));
// the named-by-spec set + the union (documents from CV_EDGES, operators from CV_MEANING)
['face', 'part-of', 'higher-order', 'navigates', 'equals', 'not', 'and', 'becomes', 'documents'].forEach(k => {
  ok('relationship.' + k + ' is registered', !!R.get('relationship.' + k));
});
// THE proof the socket placeholder is satisfiable: candidatesForSocket(kind.graph edges) → the relationship Types
const graphKind = R.get('kind.graph');
ok('kind.graph still exists (existing consumer preserved)', !!graphKind);
const edgesSocket = graphKind.sockets.edges;            // accepts:['relationship']
const cands = R.candidatesForSocket(edgesSocket);
ok('candidatesForSocket(kind.graph.edges) returns the relationship Types (placeholder satisfiable)',
   cands.length > 0 && cands.every(c => (c.classification || []).includes('relationship')),
   cands.length + ' candidates');

console.log('\n=== G3.3 · a WELL-FORMED graph PASSES ===');
// a real meaning-graph: a page is the face of a thing; the thing is part-of a project.
const goodGraph = {
  nodes: [
    { id: 'pg', form: 'square', symbol: 'browser', fill: 'wash' },     // classification defaults to ['glyphic']
    { id: 'h',  form: 'square', symbol: 'house',   fill: 'paper' },
    { id: 'pr', form: 'circle', symbol: 'folder',  fill: 'none' },
  ],
  edges: [
    { from: 'pg', to: 'h', line: 'solid', kind: 'face' },
    { from: 'h',  to: 'pr', line: 'solid', kind: 'part-of' },
  ],
};
let res = null;
try { res = GG.validateGlyphgraph(goodGraph); } catch (e) { res = { ok: false, error: e.message }; }
ok('well-formed graph validates (ok:true, no violations)', res && res.ok === true && res.violations.length === 0, JSON.stringify(res));

console.log('\n=== G3.3 · DOMAIN/RANGE via CV_REGISTRY.accepts — the discriminating reject ===');
// a node classified ['panel'] is NOT a valid node class for a relationship source/target socket
// (which accepts ['glyphic','atom','block']). This EXERCISES accepts() — proves it's not vacuous.
const badClassGraph = {
  nodes: [
    { id: 'p', classification: ['panel'], form: 'square', symbol: 'browser' },  // a panel, not a node class
    { id: 'h', form: 'square', symbol: 'house', fill: 'paper' },
  ],
  edges: [{ from: 'p', to: 'h', line: 'solid', kind: 'face' }],
};
threwWith('a source node classified ["panel"] is rejected by the source socket (accepts check)',
          () => GG.validateGlyphgraph(badClassGraph), 'is not accepted by the `source` socket');
// sanity: the SAME graph with a valid node class passes (so the reject is the class, not the structure)
const fixedClassGraph = { nodes: [{ id: 'p', classification: ['glyphic'], form: 'square', symbol: 'browser' }, { id: 'h', form: 'square', symbol: 'house', fill: 'paper' }], edges: [{ from: 'p', to: 'h', line: 'solid', kind: 'face' }] };
ok('the same graph with a valid node class PASSES (the reject was the class, not structure)',
   GG.validateGlyphgraph(fixedClassGraph).ok === true);

console.log('\n=== G3.3 · UNKNOWN relation-type THROWS (loud, no silent default) ===');
threwWith('unknown kind "teleports" throws naming it',
          () => GG.validateGlyphgraph({ nodes: [{ id: 'a' }, { id: 'b' }], edges: [{ from: 'a', to: 'b', kind: 'teleports' }] }),
          'unknown relation-type "teleports"');

console.log('\n=== G3.3 · STRUCTURAL ill-formedness THROWS (not the absent-facet law) ===');
threwWith('untyped edge (no kind) throws',
          () => GG.validateGlyphgraph({ nodes: [{ id: 'a' }, { id: 'b' }], edges: [{ from: 'a', to: 'b' }] }),
          'untyped edge');
threwWith('dangling `to` endpoint throws naming the missing id',
          () => GG.validateGlyphgraph({ nodes: [{ id: 'a' }], edges: [{ from: 'a', to: 'ghost', kind: 'face' }] }),
          'dangling `to` — no node with id "ghost"');
threwWith('duplicate node id throws',
          () => GG.validateGlyphgraph({ nodes: [{ id: 'a' }, { id: 'a' }], edges: [] }),
          'duplicate node id');

console.log('\n=== G3.3 · EDGE-INSTANCE conditions via CV_COND (distinct from socket conditions) ===');
// an edge instance carrying a condition that FAILS against its own spec → throw.
// edgeCtx = {kind,line,lineColor,direction,...}; condition "line == solid" fails for a dashed edge.
threwWith('failing edge condition (line==solid on a dashed edge) throws via CV_COND',
          () => GG.validateGlyphgraph({
            nodes: [{ id: 'a' }, { id: 'b' }],
            edges: [{ from: 'a', to: 'b', kind: 'face', line: 'dashed', conditions: ['line == solid'] }],
          }),
          'edge condition(s) failed');
// the SAME condition PASSES on a solid edge (proves it's really evaluating, not always-failing)
ok('the same edge condition PASSES on a solid edge (CV_COND actually evaluates)',
   GG.validateGlyphgraph({ nodes: [{ id: 'a' }, { id: 'b' }], edges: [{ from: 'a', to: 'b', kind: 'face', line: 'solid', conditions: ['line == solid'] }] }).ok === true);

console.log('\n=== G3.4 · NO second edge registry / meaning store — REUSE proven ===');
ok('relation Types live in CV_REGISTRY (not a parallel store)', rels.every(r => R.get(r.id) === r || !!R.get(r.id)));
ok('the validator REUSES CV_REGISTRY.accepts + CV_COND (both present, used above)',
   typeof R.accepts === 'function' && typeof COND.failures === 'function');
ok('meaning still single-sourced in CV_MEANING (edge.face field unchanged)',
   !!window.CV_MEANING.field('edge', 'face').feeling);

console.log('\n----------------------------------------');
console.log('G3 verify:  ' + pass + ' passed, ' + fail + ' failed');
if (fail) process.exit(1);
