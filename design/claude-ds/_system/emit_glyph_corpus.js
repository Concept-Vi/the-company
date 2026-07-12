// _system/emit_glyph_corpus.js — emit the GLYPH MEANING CORPUS (glyph-corpus.json).
//
// A3 of the AI fusion: the glyph_meaning embedding space is populated from THIS file,
// which is GENERATED from the one engine source (CV_ICONS + CV_MEANING) — never hand-
// written (the re-runnable-index law: re-run after any symbol/gloss/field change; the
// embed build re-embeds only changed content_hashes). Two entry kinds:
//
//   glyph://symbol/<id>          — a SYMBOL: its id + name + domain/kind/tags + gloss
//                                  (the noun→glyph leg of meaning-resolution)
//   glyph://field/<facet>/<val>  — a MEANING FIELD value: its feeling + senses
//                                  (the feeling→facet leg — "meaning is a field")
//
// Output: design/claude-ds/glyph-corpus.json  = [{address, text}, ...]
// Loud-fail: engine load errors throw; an empty corpus throws (never a silent []).
'use strict';
const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');

global.window = global;
for (const f of ['cv-icons', 'cv-vi-glyph', 'cv-shapes', 'cv-edges', 'cv-meaning', 'cv-glyphics']) {
  eval(fs.readFileSync(path.join(ROOT, 'assets/icons', f + '.js'), 'utf8'));
}
const ICN = window.CV_ICONS, M = window.CV_MEANING;
if (!ICN || !M) throw new Error('engine failed to load (CV_ICONS/CV_MEANING absent)');

const corpus = [];

// ---- symbols: glyph://symbol/<id> ------------------------------------------
const ids = Object.keys(ICN.data);
if (!ids.length) throw new Error('CV_ICONS.data is empty — refusing to emit an empty corpus');
for (const id of ids) {
  const f = (ICN.facets && ICN.facets[id]) || {};
  // glosses live in the ACTIVE profile's symbolGloss (runtime-authored data — empty in the shipped
  // default until authored+saved; a re-run picks them up then). Absent contributes nothing.
  let gloss = null;
  try { gloss = (M.resolve(M.active).symbolGloss || {})[id] || null; } catch (_) { gloss = null; }
  const parts = [
    id.replace(/-/g, ' '),
    f.name || null,
    f.description || null,
    gloss && gloss !== id ? ('reads as: ' + gloss) : null,
    f.domain ? ('domain: ' + f.domain) : null,
    f.kind ? ('kind: ' + f.kind) : null,
    (f.tags && f.tags.length) ? ('tags: ' + f.tags.join(', ')) : null,
  ].filter(Boolean);
  corpus.push({ address: 'glyph://symbol/' + id, text: parts.join(' · ') });
}

// ---- meaning fields: glyph://field/<facet>/<value> --------------------------
// valuesFor(facet) → { value: {feeling, senses, ...} } from the ACTIVE profile.
const FACETS = ['form', 'fill', 'color', 'texture', 'depth', 'motion', 'outline', 'line', 'lineColor', 'edge', 'direction'];
for (const facet of FACETS) {
  let vals = null;
  try { vals = M.valuesFor(facet); } catch (_) { continue; }   // a facet absent from the profile contributes nothing
  for (const [val, field] of Object.entries(vals || {})) {
    if (!field || typeof field !== 'object') continue;
    const feeling = field.feeling || field.meaning || null;
    const senses = Array.isArray(field.senses) ? field.senses.join(', ') : null;
    if (!feeling && !senses) continue;                          // nothing meaningful to embed — skip honestly
    const parts = [facet + ' = ' + val, feeling, senses ? ('senses: ' + senses) : null].filter(Boolean);
    corpus.push({ address: 'glyph://field/' + facet + '/' + val, text: parts.join(' · ') });
  }
}

if (corpus.length < ids.length) throw new Error('corpus smaller than the symbol set — emission bug');
const out = path.join(ROOT, 'glyph-corpus.json');
fs.writeFileSync(out, JSON.stringify({
  _generated: 'by _system/emit_glyph_corpus.js from CV_ICONS + CV_MEANING (the one source) — DO NOT hand-edit; re-run the emitter',
  _counts: { symbols: ids.length, fields: corpus.length - ids.length, total: corpus.length },
  entries: corpus,
}, null, 1));
console.log('wrote', out, '·', ids.length, 'symbols +', corpus.length - ids.length, 'field-values =', corpus.length, 'entries');
