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
    // R1b: the DECLARED params name the whole write surface — R2's referent words (kindWord/opWord/
    // determiner) and any free extra ride `extra` into setField; an introspecting AI or a params-built
    // form now DISCOVERS the channel (discoverability = correctability, A5).
    params: { facet: '', value: '', feeling: '', senses: [], kindWord: '', opWord: '', determiner: '', extra: null }, icon: 'edit', provenance: 'built-in',
    description: 'Write/update a meaning FIELD (facet/value → feeling + senses [+ kindWord/opWord on form; determiner on fill/outline; any extra]) in the active profile — the language, written live. Wraps CV_MEANING.author.setField; loud-fails on malformed input.',
    run: function (a) {
      var p = a.params || {};
      var extra = Object.assign({}, p.extra || {});
      ['kindWord', 'opWord', 'determiner'].forEach(function (k) { if (p[k]) extra[k] = p[k]; });
      return M.author.setField(p.facet, p.value, p.feeling, p.senses, extra);
    },
  }, { silent: true });

  // glyphic.author-relation / -operator / -gloss — the rest of the authoring surface,
  // same one-API-two-faces shape.
  AI.register({
    id: 'glyphic.author-relation', name: 'Author relation', layer: 'capability', family: 'language',
    surfaces: ['glyphic', 'meaning', '*'], behaviours: [], provider: null,
    // R1b: THE EDGE LAW is declared on the write surface — a directed relation is authored WITH its
    // equal-and-opposite ({directed:true, inverse:{feeling,senses}}); symmetric = directed:false.
    params: { id: '', feeling: '', senses: [], operator: false, symbol: '', directed: null, inverse: null, extra: null }, icon: 'connector', provenance: 'built-in',
    description: 'Write/update an edge RELATION (or universal operator) in the active profile — a directed relation declares {directed:true, inverse:{feeling,senses}} (the edge law: a verb-pair, declared once, composed at read); symmetric relations declare directed:false. Wraps CV_MEANING.author.setRelation/setOperator.',
    run: function (a) {
      var p = a.params || {};
      var extra = Object.assign({}, p.extra || {});
      if (typeof p.directed === 'boolean') extra.directed = p.directed;
      if (p.inverse) extra.inverse = p.inverse;
      return p.operator ? M.author.setOperator(p.id, p.feeling, p.senses, p.symbol)
                        : M.author.setRelation(p.id, p.feeling, p.senses, extra);
    },
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

  // glyphic.transglyph — RESERVED as a capability id. The real MEANING read-out
  // (CV_MEANING.referent/readGraph) EXISTS and is consumed directly by the surfaces;
  // its WORDING is live-tunable starter data (Tim's ear). A capability wrapper stays
  // unregistered until a caller needs the read-out THROUGH the registry — registering
  // it earlier would just alias a direct call.

  // glyphic.assist — A6, the COLLABORATIVE hand: a natural instruction about the CURRENT
  // glyphgraph (the shared CV_GLYPHGRAPH_SESSION: the one graph + the human's live selection)
  // → TYPED GRAPH-OPS from the Company's glyph_assist role — validated here against the live
  // registries, ATOMICALLY (one bad op = the whole set refused, loud), never free mutation
  // (the one-IR law). The surface applies the ops through the SAME code paths the mouse uses.
  AI.register({
    id: 'glyphic.assist', name: 'Collaborative graph assist', layer: 'capability', family: 'language',
    surfaces: ['glyphic', 'meaning', '*'], behaviours: [], provider: null, role: null,
    params: { instruction: '' }, icon: 'atom', provenance: 'built-in',
    description: 'Two hands on one graph: turn a natural instruction (scoped to the shared selection) into typed, registry-validated graph ops via the Company glyph_assist role. Atomic loud-fail validation; ops apply through the surface’s own edit paths.',
    run: async function (a) {
      var p = a.params || {};
      var instruction = String(p.instruction || '').trim();
      if (!instruction) throw new Error('glyphic.assist: an instruction is required');
      var S = window.CV_GLYPHGRAPH_SESSION;
      if (!S || !S.graph) throw new Error('glyphic.assist: no CV_GLYPHGRAPH_SESSION on this surface (open the glyphgraph generator)');
      // the runtime must be role-capable — follow the TEXT binding (no literal provider pin);
      // on a surface where text→claude (no runRole), this fails loud with the honest reason.
      var rt = AI.resolveProvider(AI.providerForRole('text'));
      if (typeof rt.runRole !== 'function') throw new Error('glyphic.assist: the bound text provider ("' + AI.providerForRole('text') + '") cannot fire roles — flip the binding to the Company (setRoleProvider) on a same-origin surface');
      // build the shared-context payload: the graph AS THE AI SEES IT + the LEGAL vocab (with
      // meanings, so states are chosen by MEANING not word-guess — the registries stay the truth).
      var gloss = {}; try { gloss = M.resolve(M.active).symbolGloss || {}; } catch (_) {}
      var v = this.buildVocab();
      if (!v.states.length || !v.relations.length) throw new Error('glyphic.assist: the meaning registry has no state/edge vocab loaded');
      var payload = {
        instruction: instruction,
        selection: (S.selection || []).slice(),
        nodes: (S.graph.nodes || []).map(function (n) { return { id: n.id, symbol: n.symbol || '', word: gloss[n.symbol] || n.symbol || n.form, state: n.value || '' }; }),
        edges: (S.graph.edges || []).map(function (e) { return { from: e.from, to: e.to, kind: e.kind, line: e.line || 'solid' }; }),
        // R1b: the vocab carries THE EDGE LAW — each relation is the FULL field (feeling/directed/
        // inverse), so the role can reason about which way an edge points and that an inverse telling
        // exists; edge_kinds (bare ids) kept for role-schema compatibility during the transition.
        vocab: { states: v.states, relations: v.relations, edge_kinds: v.relations.map(function (r) { return r.id; }) },
      };
      var out = (await rt.runRole('glyph_assist', JSON.stringify(payload), { max_tokens: 768 })).output;
      var ops = (out && out.ops) || [];
      if (!ops.length) throw new Error('glyphic.assist: the role returned no ops');
      // ATOMIC validation against the live graph + registries — one bad op refuses the set (loud).
      var ids = {}; (S.graph.nodes || []).forEach(function (n) { ids[n.id] = true; });
      var stateIds = v.states.map(function (s) { return s.id; });
      var edgeKinds = v.relations.map(function (r) { return r.id; });
      ops.forEach(function (o, i) {
        var bad = function (why) { throw new Error('glyphic.assist: op ' + (i + 1) + ' (' + o.op + ') refused — ' + why + ' (nothing applied; ops are atomic)'); };
        if (o.op === 'set_state') { if (!(o.ids || []).length) bad('no target ids'); (o.ids || []).forEach(function (id) { if (!ids[id]) bad('unknown node "' + id + '"'); }); if (stateIds.indexOf(o.value) < 0) bad('"' + o.value + '" is not a state (' + stateIds.join(', ') + ')'); }
        else if (o.op === 'add_edge') { if (!ids[o.from_id]) bad('unknown from "' + o.from_id + '"'); if (!ids[o.to_id]) bad('unknown to "' + o.to_id + '"'); if (edgeKinds.indexOf(o.kind) < 0) bad('"' + o.kind + '" is not an edge-meaning yet (' + edgeKinds.join(', ') + ') — teach the relation first'); }
        else if (o.op === 'add_node') { if (!String(o.value || '').trim()) bad('no word for the new thing'); }
        else if (o.op === 'remove') { if (!(o.ids || []).length) bad('no target ids'); (o.ids || []).forEach(function (id) { if (!ids[id]) bad('unknown node "' + id + '"'); }); }
        else if (o.op === 'narrate') { if (!String(o.text || '').trim()) bad('empty narration'); }
        else bad('unknown op');
      });
      return ops;
    },
    // the LEGAL vocab, law-carrying — one builder for the payload, the tests, and any panel.
    // Each relation = the FULL meaning field (id/feeling/senses/directed/inverse/negates/symbol).
    buildVocab: function () {
      var states = [];
      try { var sv = M.valuesFor('color'); Object.keys(sv).forEach(function (id) { states.push({ id: id, means: sv[id].feeling || sv[id].meaning || '' }); }); } catch (_) {}
      var relations = [];
      try {
        Object.keys(M.valuesFor('edge')).forEach(function (id) {
          var f = M.field('edge', id);   // loud on a seeded kind with no field
          relations.push({ id: id, feeling: f.feeling, senses: f.senses,
                           directed: f.directed, inverse: f.inverse || null,
                           negates: !!f.negates, symbol: f.symbol || null });
        });
      } catch (_) {}
      return { states: states, relations: relations };
    },
  }, { silent: true });

  // context.glyphic — projects "the language as it stands" into the prompt context,
  // so the AI authors ON-SYSTEM (knows the facets, types, active profile) — matching
  // ai-glyphic.js's inline CV_ICONS read pattern.
  AI.register({
    id: 'context.glyphic', name: 'Glyphic language context', layer: 'context',
    surfaces: ['glyphic', 'meaning'], provenance: 'built-in', icon: 'book',
    resolveCtx: function () {
      if (!window.CV_MEANING) return {};
      var P = window.CV_MEANING.activeProfile();
      // R1b: the ambient context carries THE EDGE LAW's shape per relation (directed/inverse),
      // not just binding counts — an AI reading "the language as it stands" sees the verb-pairs.
      var relations = [];
      try {
        Object.keys(window.CV_MEANING.valuesFor('edge')).forEach(function (id) {
          var f = window.CV_MEANING.field('edge', id);
          relations.push({ id: id, feeling: f.feeling, directed: f.directed, inverse: f.inverse || null });
        });
      } catch (_) {}
      return {
        activeProfile: window.CV_MEANING.active,
        meaningFacets: window.CV_MEANING.facets,
        meaningTypes: window.CV_MEANING.types(),
        facetCounts: Object.keys(P.bindings || {}).reduce(function (o, f) { o[f] = Object.keys(P.bindings[f]).length; return o; }, {}),
        relations: relations,
      };
    },
  }, { silent: true });
})();
