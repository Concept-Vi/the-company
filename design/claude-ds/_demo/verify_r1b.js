// _demo/verify_r1b.js — R1b: the edge law's census tails (ROADMAP R1b; evidence census/wave reports).
//  1 · cv-edges' EDGE_KINDS `means:` sentences DELETED (the second meaning home, resolving live) and
//      resolve() no longer returns `means` — meaning has ONE home (CV_MEANING fields).
//  2 · glyphic.assist's payload carries the edge law: vocab.relations = FULL FIELDS per kind
//      (directed/inverse/feeling), not bare ids — the collaborative AI can know which way an edge points.
//  3 · context.glyphic surfaces the directed/inverse shape per relation (not just binding counts).
//  4 · glyphic.author / glyphic.author-relation DECLARE the authorable extras in params
//      (directed, inverse, kindWord, opWord, determiner) — discoverability = correctability.
//  5 · describeRelation can realise the INVERSE telling (focus:'target') — same law, second read-path.
// Falsify-first: run against unmodified code; the law checks must FAIL before the build.
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
['app/registry/conditions.js',
 'app/registry/types-core.js',
 'app/registry/kinds-type.js',
 'assets/icons/cv-icons.js', 'assets/icons/cv-vi-glyph.js', 'assets/icons/cv-shapes.js',
 'assets/icons/cv-edges.js', 'assets/icons/cv-meaning.js', 'assets/icons/cv-glyphics.js',
 'app/registry/relationships-seed.js',
 'app/ai/ai-registry.js', 'app/ai/ai-seed.js', 'app/ai/ai-glyphic-language.js'].forEach(load);

var M = global.CV_MEANING, E = global.CV_EDGES, AI = global.CV_AI;
var pass = 0, total = 0;
function check(l, fn) {
  total++;
  try { if (fn()) { pass++; console.log('OK ' + l); } else console.log('XX ' + l + ' (false)'); }
  catch (e) { console.log('XX ' + l + ' (threw: ' + e.message + ')'); }
}

// ── 1 · one meaning home: cv-edges carries LOOK only ─────────────────────────
check('EDGE_KINDS entries carry NO means: sentences', function () {
  return E.kinds.every(function (k) { return !('means' in k); });
});
check('resolve() returns NO means field', function () {
  var r = E.resolve({ kind: 'face', line: 'dashed' });
  return !('means' in r) && r.kind === 'face';
});
check('CV_EDGES.means() helper is gone (no reader of the dead home)', function () {
  return E.means === undefined;
});

// ── 2 · the collaborative AI sees the law ─────────────────────────────────────
check('glyphic.assist builds vocab.relations with directed/inverse per kind', function () {
  var cap = AI.get('glyphic.assist');
  if (!cap || typeof cap.buildVocab !== 'function') return false;   // the payload-vocab builder, exposed for test + reuse
  var v = cap.buildVocab();
  if (!Array.isArray(v.relations) || !v.relations.length) return false;
  var pf = v.relations.filter(function (r) { return r.id === 'part-of'; })[0];
  var eq = v.relations.filter(function (r) { return r.id === 'equals'; })[0];
  return pf && pf.directed === true && pf.inverse && !!pf.inverse.feeling && !!pf.feeling &&
         eq && eq.directed === false;
});

// ── 3 · the ambient context surfaces the shape ────────────────────────────────
check('context.glyphic includes relations with directed/inverse (not just counts)', function () {
  var ctx = AI.get('context.glyphic');
  if (!ctx || typeof ctx.resolveCtx !== 'function') return false;
  var c = ctx.resolveCtx({});
  if (!c || !Array.isArray(c.relations)) return false;
  var pf = c.relations.filter(function (r) { return r.id === 'part-of'; })[0];
  return pf && pf.directed === true && pf.inverse && !!pf.inverse.feeling;
});

// ── 4 · the write surface is discoverable ─────────────────────────────────────
check('glyphic.author declares kindWord/opWord/determiner (+extra) in params', function () {
  var cap = AI.get('glyphic.author');
  var p = cap && cap.params;
  return p && ('kindWord' in p) && ('opWord' in p) && ('determiner' in p);
});
check('glyphic.author-relation declares directed/inverse in params', function () {
  var cap = AI.get('glyphic.author-relation');
  var p = cap && cap.params;
  return p && ('directed' in p) && ('inverse' in p);
});

// ── 5 · describeRelation realises the inverse telling ─────────────────────────
var rel = { source: { form: 'square', symbol: 'house', fill: 'paper' },
            edge: { line: 'solid', kind: 'part-of' },
            target: { form: 'hex', fill: 'paper' } };
check('describeRelation forward telling unchanged', function () {
  var r = M.describeRelation(rel);
  return /part of/.test(r.sentence);
});
check('describeRelation({focus:"target"}) speaks the INVERSE from the target side', function () {
  var r = M.describeRelation(rel, { focus: 'target' });
  var inv = M.field('edge', 'part-of').inverse.feeling;
  // the target (the system) becomes the SUBJECT (inspector voice: "a system, …"); the inverse verb
  // appears; the source (the home) lands on the object side.
  return r.sentence.indexOf(inv) !== -1 && /^a system/i.test(r.sentence) &&
         r.sentence.indexOf(inv) < r.sentence.indexOf('home');
});
check('inverse telling still folds negation (is NOT the container of)', function () {
  var r = M.describeRelation({ source: rel.source, edge: { line: 'solid', kind: 'part-of', negate: true },
                               target: rel.target }, { focus: 'target' });
  return /is not/.test(r.sentence) && r.sentence.indexOf(M.field('edge', 'part-of').inverse.feeling) !== -1;
});

console.log('\n' + pass + '/' + total + ' pass');
if (pass !== total) process.exit(1);
