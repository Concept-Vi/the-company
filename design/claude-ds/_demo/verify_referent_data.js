// _demo/verify_referent_data.js — R2: the REFERENT WORDS ARE PROFILE DATA (A1 — a G0.1
// completion). The kind words (octagon→'gateway'…), the op phrases (triangle→'action on'…)
// and the DETERMINER ladder were module-private consts the author API could not reach —
// the engine violating its own law ("nothing has one fixed meaning — a fixed interpretation
// anywhere the author API can't reach is a violation", Tim 2026-07-03). After R2 they are
// FIELD DATA on form/fill/outline (the shape line fields' `phrase` already uses):
// referent() AND parse() read them from the ACTIVE PROFILE, so authoring a word changes
// the read-out and the parse live, with no code edit.
// Falsify-first: written against pre-R2 code — the law checks must FAIL before the build.
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
 'app/registry/relationships-seed.js'].forEach(load);

var M = global.CV_MEANING;
var pass = 0, total = 0;
function check(l, fn) {
  total++;
  try { if (fn()) { pass++; console.log('OK ' + l); } else console.log('XX ' + l + ' (false)'); }
  catch (e) { console.log('XX ' + l + ' (threw: ' + e.message + ')'); }
}

// ── 1 · the words live on the FIELDS (the profile), not in consts ─────────────
check('form octagon carries its kind word as field data', function () {
  return M.field('form', 'octagon').kindWord === 'gateway';
});
check('form triangle carries its op phrase as field data', function () {
  return M.field('form', 'triangle').opWord === 'action on';
});
check('fill none carries its determiner as field data', function () {
  return M.field('fill', 'none').determiner === 'the';
});
check('outline dashed carries its determiner as field data', function () {
  return M.field('outline', 'dashed').determiner === 'a possible';
});

// ── 2 · referent() reads the profile (baseline wording unchanged) ─────────────
check('baseline referent unchanged: octagon+wash → "this … gateway"', function () {
  var p = M.referent({ form: 'octagon', symbol: 'house', fill: 'wash' });
  return p === 'this home gateway';
});
check('baseline op referent unchanged: triangle → "a action on …"-shape', function () {
  var p = M.referent({ form: 'triangle', symbol: 'house', fill: 'paper' });
  return p.indexOf('action on') !== -1;
});

// ── 3 · THE LAW: authoring the word changes read-out AND parse, live, no code edit ─
check('setField changes the KIND WORD live in the read-out', function () {
  var f0 = M.field('form', 'octagon');
  M.author.setField('form', 'octagon', f0.feeling, f0.senses, { kindWord: 'portal' });
  var p = M.referent({ form: 'octagon', symbol: 'house', fill: 'wash' });
  return p === 'this home portal';
});
check('…and the PARSE learns the new word for free (the inverse vocabulary is live)', function () {
  var g = M.parse('This home portal.').graph;
  return g.nodes.length === 1 && g.nodes[0].form === 'octagon';
});
check('…and the OLD word is gone from the parse (one home — no ghost vocabulary)', function () {
  try { M.parse('This home gateway.'); return false; }   // 'gateway' no longer any field's word
  catch (e) { return /gateway/.test(e.message); }        // loud, naming the token
});
check('setField changes a DETERMINER live (read-out + parse)', function () {
  var f0 = M.field('fill', 'wash');
  M.author.setField('fill', 'wash', f0.feeling, f0.senses, { determiner: 'the featured' });
  var p = M.referent({ form: 'octagon', symbol: 'house', fill: 'wash' });
  if (p !== 'the featured home portal') return false;
  var g = M.parse('The featured home portal.').graph;
  return g.nodes.length === 1 && g.nodes[0].form === 'octagon' && g.nodes[0].fill === 'wash';
});

// restore the starter words (harness hygiene — later checks/other runs see seed state)
(function () {
  var f = M.field('form', 'octagon'); M.author.setField('form', 'octagon', f.feeling, f.senses, { kindWord: 'gateway' });
  var w = M.field('fill', 'wash');   M.author.setField('fill', 'wash', w.feeling, w.senses, { determiner: 'this' });
})();

// ── 4 · the consts are GONE (no second home to drift from) ────────────────────
check('no REFERENT_KIND / REFERENT_OP consts remain in the source', function () {
  var src = fs.readFileSync('assets/icons/cv-meaning.js', 'utf8');
  return src.indexOf('REFERENT_KIND') === -1 && src.indexOf('REFERENT_OP') === -1;
});

// ── 5 · loudness holds: an unknown form still throws before any wording ───────
check('referent still throws loud on an unknown form', function () {
  try { M.referent({ form: 'nonagon' }); return false; } catch (e) { return /nonagon|unknown|form/.test(e.message); }
});

console.log('\n' + pass + '/' + total + ' pass');
if (pass !== total) process.exit(1);
