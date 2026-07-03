// _demo/verify_edgelaw.js — R1: THE EDGE LAW (Tim, 2026-07-03; CRITERIA AMENDMENT A2 + G6.2).
// "The only valid typed edges are DIRECTIONAL VERBS with an EQUAL AND OPPOSITE."
// The law lands as: every directed edge MEANING FIELD declares its inverse telling ONCE
// (composed at read, never stored twice); symmetric relations declare directed:false;
// relationship Types mirror {directed, inverse} (the Company relation_types convergence);
// readGraph realises the inverse from FOCUS (one stored edge, both tellings, every target);
// parse() understands the inverse telling (round-trip); cv-edges carries LOOK ONLY
// (no verbs table — G3.4) and resolves LOUD (no silent kind default).
// Falsify-first: written against UNMODIFIED code — all law checks must FAIL before the build.
'use strict';
var fs = require('fs');
global.window = global;
global.localStorage = (function () {
  var store = {};
  return { getItem: function (k) { return (k in store ? store[k] : null); },
           setItem: function (k, v) { store[k] = String(v); },
           removeItem: function (k) { delete store[k]; } };
})();
var load = function (p) { eval(fs.readFileSync(p, 'utf8')); };
// same minimal real chain as verify_g3 (run from the repo root)
['app/registry/conditions.js',
 'app/registry/types-core.js',
 'app/registry/kinds-type.js',
 'assets/icons/cv-icons.js', 'assets/icons/cv-vi-glyph.js', 'assets/icons/cv-shapes.js',
 'assets/icons/cv-edges.js', 'assets/icons/cv-meaning.js', 'assets/icons/cv-glyphics.js',
 'app/registry/relationships-seed.js'].forEach(load);

var M = global.CV_MEANING, E = global.CV_EDGES, R = global.CV_REGISTRY;
var pass = 0, total = 0;
function check(l, fn) {
  total++;
  try { if (fn()) { pass++; console.log('OK ' + l); } else console.log('XX ' + l + ' (false)'); }
  catch (e) { console.log('XX ' + l + ' (threw: ' + e.message + ')'); }
}
function throws(fn) { try { fn(); return false; } catch (e) { return true; } }

// ── 1 · the meaning fields declare the law ────────────────────────────────────
check('part-of is directed with an inverse telling', function () {
  var f = M.field('edge', 'part-of');
  return f.directed === true && f.inverse && typeof f.inverse.feeling === 'string' && f.inverse.feeling.length > 0;
});
check('equals is declared SYMMETRIC (directed:false, no inverse needed)', function () {
  var f = M.field('edge', 'equals');
  return f.directed === false;
});
check('EVERY edge field declares directed; every directed one declares inverse', function () {
  var vals = M.valuesFor('edge');
  return Object.keys(vals).every(function (id) {
    var f = M.field('edge', id);
    if (typeof f.directed !== 'boolean') { console.log('   · ' + id + ' has no directed'); return false; }
    if (f.directed && !(f.inverse && f.inverse.feeling)) { console.log('   · ' + id + ' directed but no inverse'); return false; }
    return true;
  });
});
check('face carries the law too (the page-face relation as a verb-pair)', function () {
  var f = M.field('edge', 'face');
  return f.directed === true && f.inverse && !!f.inverse.feeling;
});

// ── 2 · the relationship TYPES mirror it (the Company relation_types shape) ──
check('relationship.part-of Type mirrors {directed:true, inverse}', function () {
  var t = R.resolve('relationship.part-of');
  return t && t.directed === true && t.inverse && !!t.inverse.feeling;
});
check('relationship.equals Type mirrors directed:false', function () {
  var t = R.resolve('relationship.equals');
  return t && t.directed === false;
});

// ── 3 · readGraph realises BOTH tellings from ONE stored edge ────────────────
var G = { nodes: [{ id: 'A', form: 'square', fill: 'paper' }, { id: 'B', form: 'hex', fill: 'paper' }],
          edges: [{ from: 'A', to: 'B', line: 'solid', kind: 'part-of' }] };
check('forward telling unchanged (focus = source)', function () {
  var r = M.readGraph(G, { focus: 'A' });
  return /part of/.test(r.sentence);
});
check('INVERSE telling from the target focus (B tells the same edge with the opposite verb)', function () {
  var r = M.readGraph(G, { focus: 'B' });
  var inv = M.field('edge', 'part-of').inverse.feeling;
  return r.sentence.indexOf(inv) !== -1;
});
check('triples target keeps the STRUCTURE canonical under inverse focus (never (kind B A))', function () {
  var r = M.readGraph(G, { focus: 'B', target: 'triples' });
  return r.sentence.indexOf('(part-of A B)') !== -1 && r.sentence.indexOf('(part-of B A)') === -1;
});

// ── 4 · live authoring: a verb-pair enters through the door, both tellings work ─
check('author a new verb-pair at runtime → both tellings realise, no code edit', function () {
  M.author.setRelation('shelters', 'the shelter of', ['protects', 'holds safe'],
    { directed: true, inverse: { feeling: 'sheltered by', senses: ['protected by'] } });
  var g = { nodes: [{ id: 'R', form: 'square', fill: 'paper' }, { id: 'T', form: 'circle', fill: 'none' }],
            edges: [{ from: 'R', to: 'T', line: 'solid', kind: 'shelters' }] };
  var fwd = M.readGraph(g, { focus: 'R' }).sentence;
  var rev = M.readGraph(g, { focus: 'T' }).sentence;
  return fwd.indexOf('the shelter of') !== -1 && rev.indexOf('sheltered by') !== -1;
});

// ── 5 · parse understands the inverse telling (round-trip: one edge, both sayings) ─
check('parse of the inverse telling yields the SAME stored edge (from/to swapped back)', function () {
  // NOTE: 'part of' is a pre-existing HOMONYM (higher-order + part-of share the feeling —
  // parse picks one; a live-tune item, not an edge-law defect). Use the unique pair frames/
  // framed by so this check proves the SWAP, not homonym disambiguation.
  var fwd = M.parse('This gateway is the frame of this system.').graph;
  var rev = M.parse('This system is framed by this gateway.').graph;   // starter inverse wording
  if (!fwd.edges.length || !rev.edges.length) return false;
  var fe = fwd.edges[0], re = rev.edges[0];
  // both must store kind frames; the inverse saying swaps subject/object BACK to canonical
  var fFrom = fwd.nodes.filter(function (n) { return n.id === fe.from; })[0];
  var rFrom = rev.nodes.filter(function (n) { return n.id === re.from; })[0];
  return fe.kind === 'frames' && re.kind === 'frames' &&
         fFrom.form === 'octagon' && rFrom.form === 'octagon';      // the gateway is the canonical FROM side both times
});

// ── 6 · one home: cv-edges is LOOK ONLY, and loud ─────────────────────────────
check('the verbs table is GONE from cv-edges (G3.4 — no second edge registry)', function () {
  return E.verbs === undefined && E.verb === undefined;
});
check('resolve() with NO kind throws (the silent face-default is dead)', function () {
  return throws(function () { E.resolve({}); });
});
check('resolve() with an unknown kind throws', function () {
  return throws(function () { E.resolve({ kind: 'zzz-not-a-kind' }); });
});
check('resolve() with a real kind still works', function () {
  var r = E.resolve({ kind: 'part-of', line: 'solid' });
  return r && r.kind === 'part-of';
});

console.log('\n' + pass + '/' + total + ' pass');
if (pass !== total) process.exit(1);
