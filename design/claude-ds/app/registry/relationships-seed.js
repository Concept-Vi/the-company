// app/registry/relationships-seed.js
// ============================================================================
// SEED the RELATIONSHIP Types into CV_REGISTRY — the verbs of the glyphgraph.
//
// kinds-type.js declares `kind.graph` with an edges socket `accepts:['relationship']`
// — an UNFILLED PLACEHOLDER (no relationship Types existed). This file FILLS it:
// every edge-kind the glyphgraph uses becomes a first-class Type with
// `kind:'relationship'`, `classification:['relationship']` (so the placeholder
// socket actually has candidates), and source/target SOCKETS whose `accepts`
// list the node classes a relation may join. The Glyphic was the reference NODE
// component (glyphic-type.js); these are the reference RELATION components —
// mirroring types-seed.js's built-in registration shape exactly.
//
// ONE HOME, NO FORK (REUSE law): the relation's MEANING already lives in
// CV_MEANING (the `edge`/`line`/`direction` facet fields) and its rendered look
// in CV_EDGES — this file does NOT re-author meanings; it registers the relation
// kinds AS TYPES so the registry/accepts grammar can validate a graph. The id
// list is the UNION of the real edge homes, reconciled live at seed-time:
//   · CV_EDGES.ids()                         → face / documents / higher-order / navigates
//   · CV_MEANING operator fields (edge.*)     → equals / not / and / becomes / part-of
// so every edge kind a real graph can carry resolves to a relationship Type
// (an unknown kind throws in validateGlyphgraph — loud, never silent).
//
// NOTE: `?` (question) and `!` (matters/urgent) from the operator sign-class are
// ILLOCUTIONARY markers (force/mood on a clause), NOT binary relations between
// two nodes — so they are correctly NOT seeded as relationship Types here.
//
// ID convention: `relationship.<kind>` (keeps the dotted-namespace convention of
// `kind.graph`, `token.color.gold`); validateGlyphgraph maps a bare edge.kind
// (`face`, `part-of`, …) → `relationship.${kind}`. Grepped: no id collision.
//
// Load after types-core.js + kinds-type.js (the placeholder) + cv-edges.js +
// cv-meaning.js (the meaning/look homes this reconciles against).
// ============================================================================
(function () {
  'use strict';
  var R = window.CV_REGISTRY;
  if (!R) { console.error('relationships-seed.js: CV_REGISTRY must load first'); return; }

  // The node classes a relation may join. Mirrors kind.graph's nodes socket
  // (`accepts:['glyphic','atom','block']`) — a glyphgraph node is typically a
  // Glyphic (classified ['glyphic','mark','atom']). Source/target sockets carry
  // this so accepts() can REJECT an endpoint that is not a valid node class.
  var NODE_CLASSES = ['glyphic', 'atom', 'block'];

  // --- reconcile the id list against the real edge homes (no parallel list) ---
  // CV_EDGES.ids() = the rendered edge kinds; CV_MEANING edge.* operator fields =
  // the operator sign-class. Union, de-duped, in a stable order.
  function edgeKindUnion() {
    var ids = [];
    var seen = {};
    function add(id) { if (id && !seen[id]) { seen[id] = true; ids.push(id); } }

    var E = window.CV_EDGES;
    if (E && typeof E.ids === 'function') { E.ids().forEach(add); }

    // operator relations live as edge.* fields in the active CV_MEANING profile.
    // valuesFor('edge') returns that facet's bindings ({face,higher-order,equals,…}).
    var M = window.CV_MEANING;
    if (M && typeof M.valuesFor === 'function') {
      try {
        var edgeFields = M.valuesFor('edge');
        if (edgeFields) { Object.keys(edgeFields).forEach(add); }
      } catch (e) { /* edge not meaning-bearing in this profile — the spec set below still covers it */ }
    }
    // ensure the named-by-spec set is present even if a home is unavailable
    ['face', 'documents', 'higher-order', 'navigates',
     'equals', 'not', 'and', 'becomes', 'part-of'].forEach(add);
    return ids;
  }

  // pull the relation's authored meaning/look from its existing homes (REUSE),
  // so the Type carries provenance metadata without re-authoring it.
  function metaFor(kind) {
    var means = null, symbol = null, negates = false, look = null;
    var directed = null, inverse = null;   // THE EDGE LAW (A2): mirrored from the meaning home
    var E = window.CV_EDGES;
    if (E && typeof E.kind === 'function') {
      var ek = E.kind(kind);
      if (ek) { means = ek.means || null; look = { line: ek.line, direction: ek.direction, ink: ek.ink }; }
    }
    var M = window.CV_MEANING;
    if (M && typeof M.field === 'function') {
      try {
        var f = M.field('edge', kind);   // throws if this edge value has no meaning
        if (f) {
          if (!means) means = f.feeling + (f.senses && f.senses.length ? ' (' + f.senses.join('; ') + ')' : '');
          if (f.symbol) symbol = f.symbol;
          // THE EDGE LAW: the field declares direction + the inverse telling (the verb-pair).
          // Mirrored, never re-authored — the Company relation_types shape ({directed, inverse}).
          if (typeof f.directed === 'boolean') directed = f.directed;
          if (f.inverse) inverse = f.inverse;
          // a profile field may carry operator/negates flags
          var raw = (M.valuesFor ? M.valuesFor('edge') : null);
          var rec = raw && raw[kind];
          if (rec && rec.negates) negates = true;
          if (rec && rec.symbol && !symbol) symbol = rec.symbol;
        }
      } catch (e) { /* this kind has no edge meaning field — fine; CV_EDGES gave the means */ }
    }
    return { means: means, symbol: symbol, negates: negates, look: look, directed: directed, inverse: inverse };
  }

  var defs = edgeKindUnion().map(function (kind) {
    var m = metaFor(kind);
    var name = kind.split('-').map(function (w) { return w.charAt(0).toUpperCase() + w.slice(1); }).join(' ');
    return {
      id: 'relationship.' + kind,
      // the bare edge.kind id the IR uses — validateGlyphgraph maps to this
      relationKind: kind,
      name: name,
      kind: 'relationship',
      layer: 'system',          // a relation composes nodes — sits at the system layer
      family: 'relationship',
      classification: ['relationship'],   // so kind.graph's edges socket (accepts:['relationship']) admits it
      icon: 'atom',
      description: 'Relationship "' + kind + '"' + (m.symbol ? ' (' + m.symbol + ')' : '') +
                   (m.means ? ' — ' + m.means : '') + '. A typed edge joining two glyphgraph nodes; ' +
                   'meaning lives in CV_MEANING (edge.' + kind + '), look in CV_EDGES — this is its TYPE.',
      // operator metadata, mirrored (not re-authored) from the meaning home
      operatorSymbol: m.symbol || null,
      negates: !!m.negates,
      // THE EDGE LAW (Tim, 2026-07-03): a typed edge is a directional verb with an equal
      // and opposite — the Type carries {directed, inverse} mirrored from its meaning field
      // (the same shape as the Company's relation_types records; the G6.2 convergence face).
      directed: m.directed,      // true | false | null (null = the field predates the law — loud at read)
      inverse: m.inverse,        // { feeling, senses? } — the opposite telling, declared once
      // the relation's defining SOCKETS — source/target, each accepting node classes.
      // accepts() rejects an endpoint whose classification isn't a node class.
      sockets: {
        source: { label: 'Source', accepts: NODE_CLASSES.slice(),
                  means: 'the subject node of the relation' },
        target: { label: 'Target', accepts: NODE_CLASSES.slice(),
                  means: 'the object node of the relation' },
      },
      conditions: [],
      tags: ['relationship', 'edge', 'glyphgraph', kind],
    };
  });

  R.registerMany(defs.map(function (d) { return Object.assign({ provenance: 'built-in' }, d); }), { silent: true });

  // expose the seeded relationship ids for diagnostics / the validator
  window.CV_RELATIONSHIPS_SEED = { ids: defs.map(function (d) { return d.id; }) };
})();
