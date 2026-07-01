// app/ai/ai-glyphic-language.js
// ============================================================================
// The Glyphic LANGUAGE, in the AI registry — so the integrated AI has EQUAL tools
// to the user: read the language in-context AND author it live. One capability =
// a DUAL surface by construction: both `CV_AI.execute('glyphic.author', …)` (the
// AI move) and a UI panel call the SAME entry. This is Tim's mandate — the language
// is written over time, by Tim AND the AI, through the system itself.
//
// SIBLING, not extension: ai-glyphic.js operates on CV_ICONS (symbols — intrinsic);
// THIS operates on CV_MEANING (contextual meaning — the loadable dictionary). The
// two are kept apart exactly as CV_GLYPHIC/CV_MEANING keep geometry/denotation apart
// from contextual meaning. Load AFTER ai-registry.js + cv-meaning.js.
//
// LOUD-FAIL: the wrapped CV_MEANING.author throws on malformed input; capabilities
// do not swallow it. If CV_AI / CV_MEANING aren't loaded, fail loud (convention:
// console.error + bail, matching glyphic-type.js) — never silently register nothing.
// ============================================================================
(function () {
  'use strict';
  var AI = window.CV_AI;
  if (!AI) { console.error('ai-glyphic-language.js: CV_AI must load before this (ai-registry.js)'); return; }
  var M = window.CV_MEANING;
  if (!M) { console.error('ai-glyphic-language.js: CV_MEANING must load before this (cv-meaning.js)'); return; }

  // glyphic.author — WRITE a meaning field (facet/value → feeling/senses) into the
  // active profile. No LLM. Wraps CV_MEANING.author.setField (which loud-fails).
  AI.register({
    id: 'glyphic.author', name: 'Author language field', layer: 'capability', family: 'language',
    surfaces: ['glyphic', 'meaning', '*'], behaviours: [], provider: null,
    params: { facet: '', value: '', feeling: '', senses: [] }, icon: 'edit', provenance: 'built-in',
    description: 'Write/update a meaning FIELD (facet/value → feeling + senses) in the active profile — the language, written live. Wraps CV_MEANING.author.setField; loud-fails on malformed input.',
    run: function (a) { var p = a.params || {}; return M.author.setField(p.facet, p.value, p.feeling, p.senses, p.extra); },
  }, { silent: true });

  // glyphic.author-relation / -operator / -gloss — the rest of the authoring surface,
  // same one-API-two-faces shape.
  AI.register({
    id: 'glyphic.author-relation', name: 'Author relation', layer: 'capability', family: 'language',
    surfaces: ['glyphic', 'meaning', '*'], behaviours: [], provider: null,
    params: { id: '', feeling: '', senses: [], operator: false, symbol: '' }, icon: 'connector', provenance: 'built-in',
    description: 'Write/update an edge RELATION (or universal operator) in the active profile. Wraps CV_MEANING.author.setRelation/setOperator.',
    run: function (a) { var p = a.params || {}; return p.operator ? M.author.setOperator(p.id, p.feeling, p.senses, p.symbol) : M.author.setRelation(p.id, p.feeling, p.senses, p.extra); },
  }, { silent: true });

  AI.register({
    id: 'glyphic.author-gloss', name: 'Author symbol gloss', layer: 'capability', family: 'language',
    surfaces: ['glyphic', 'meaning', '*'], behaviours: [], provider: null,
    params: { symbol: '', word: '' }, icon: 'tag', provenance: 'built-in',
    description: 'Map a symbol id to its plain word (used by the read-out). Wraps CV_MEANING.author.setGloss.',
    run: function (a) { var p = a.params || {}; return M.author.setGloss(p.symbol, p.word); },
  }, { silent: true });

  // glyphic.read — LOOK UP a field (facet+value) or LIST the active profile. No LLM.
  // Gives the AI the language in-context.
  AI.register({
    id: 'glyphic.read', name: 'Read the language', layer: 'capability', family: 'language',
    surfaces: ['glyphic', 'meaning', '*'], behaviours: [], provider: null,
    params: { facet: '', value: '' }, icon: 'book-open', provenance: 'built-in',
    description: 'Look up a meaning field, or (no params) list the active profile + meaning-types. The AI reads the language in-context.',
    run: function (a) {
      var p = a.params || {};
      if (p.facet && p.value) return M.field(p.facet, p.value);
      return { profile: M.active, types: M.types(), bindings: M.activeProfile().bindings };
    },
  }, { silent: true });

  // glyphic.describe — the INSPECTOR. Narrates what a mark is MADE OF (its facets):
  // "a square, present, frosted, at rest". This is a DESCRIPTION for checking a glyph —
  // it is NOT the language's meaning. (Tim, 2026-06-30: descriptions of glyphics are a
  // separate layer from the actual language / actual meanings — do not conflate them.)
  AI.register({
    id: 'glyphic.describe', name: 'Describe (inspect a mark)', layer: 'capability', family: 'language',
    surfaces: ['glyphic', 'meaning', '*'], behaviours: [], provider: null,
    params: { spec: null }, icon: 'eye', provenance: 'built-in',
    description: 'INSPECT what a glyphic is made of — narrates its facets (form/fill/texture/motion). A DESCRIPTION of the mark, NOT the language meaning. Wraps CV_MEANING.describe.',
    run: function (a) { var p = a.params || {}; return M.describe(p.spec || p); },
  }, { silent: true });

  // glyphic.transglyph — RESERVED for the real MEANING read-out (referent + relations:
  // "this file could become a page"). NOT built yet: the referent-based readGraph is the
  // gated piece whose WORDING waits for Tim's ear. Registering it now would re-blur the
  // inspector with the language. It lands when readGraph exists and rings true by feel.

  // context.glyphic — projects "the language as it stands" into the prompt context,
  // so the AI authors ON-SYSTEM (knows the facets, types, active profile) — matching
  // ai-glyphic.js's inline CV_ICONS read pattern.
  AI.register({
    id: 'context.glyphic', name: 'Glyphic language context', layer: 'context',
    surfaces: ['glyphic', 'meaning'], provenance: 'built-in', icon: 'book',
    resolveCtx: function () {
      if (!window.CV_MEANING) return {};
      var P = window.CV_MEANING.activeProfile();
      return {
        activeProfile: window.CV_MEANING.active,
        meaningFacets: window.CV_MEANING.facets,
        meaningTypes: window.CV_MEANING.types(),
        facetCounts: Object.keys(P.bindings || {}).reduce(function (o, f) { o[f] = Object.keys(P.bindings[f]).length; return o; }, {}),
      };
    },
  }, { silent: true });
})();
