/**
 * ConceptV — GLYPHGRAPH conformance  (window.CV_GLYPHGRAPH)
 * ============================================================================
 * A glyphgraph is the sentence-as-data: glyphic NODES joined by typed relation
 * EDGES (the CVGraph IR). This module is the GRAMMAR CHECK — `validateGlyphgraph`
 * decides whether a graph is WELL-FORMED (grammatical) by REUSING the registry's
 * type grammar (CV_REGISTRY.accepts — socket domain/range) and the shared
 * condition evaluator (CV_COND) — NOT a second validator, NOT a second edge or
 * meaning store. A well-formed graph passes; an ill-formed one THROWS with the
 * specific violation (the grammar rejecting ungrammatical input — loud, never a
 * silent drop or a swallowed bad edge).
 *
 * What it checks, per edge:
 *   1. STRUCTURE — the edge is typed (`kind` present) and both endpoints
 *      (`from`/`to`) resolve to real nodes in the graph. A missing type or a
 *      dangling endpoint is ill-formed → throw. (This is NOT the "absent facet
 *      contributes nothing" law — that law is about facet VALUES like lineColor;
 *      a relation with no type, or pointing at no node, is a STRUCTURAL error.)
 *   2. RELATION-TYPE — `edge.kind` resolves to a `relationship.<kind>` Type in
 *      CV_REGISTRY (seeded by relationships-seed.js). An unknown kind → throw.
 *   3. DOMAIN/RANGE — the source node satisfies the relationship Type's `source`
 *      socket and the target its `target` socket, via CV_REGISTRY.accepts. A node
 *      whose classification is not a valid node class for that socket → throw.
 *      (Node classification is DERIVED: node.classification || ['glyphic'].)
 *   4. EDGE-INSTANCE CONDITIONS — the edge's own `conditions` (if any) are tested
 *      via CV_COND against the edge spec {kind,line,lineColor,direction,…}. These
 *      are DISTINCT from the SOCKET conditions accepts() already runs internally —
 *      socket conditions gate acceptance; edge conditions gate the relation itself.
 *
 * Lazy resolution: CV_REGISTRY / CV_COND are read at CALL time (inside the
 * function), not at load time — so load order can't leave a stale `undefined`
 * binding. Load after types-core.js + relationships-seed.js + cv-meaning/cv-glyphics
 * (after cv-glyphics per index.html), so the relationship Types exist when called.
 */
(function () {
  'use strict';

  function fail(msg) { throw new Error('CV_GLYPHGRAPH: ' + msg); }

  // a node's classification — what other sockets accept it AS. Derived so a graph
  // CAN carry a node whose class is not a node-class (and be correctly rejected).
  function nodeClassification(node) {
    if (node && Array.isArray(node.classification) && node.classification.length) return node.classification;
    return ['glyphic'];   // a glyphgraph node is a Glyphic by default
  }

  // build the minimal "type" shape CV_REGISTRY.accepts() reads off a node:
  // accepts() looks at type.classification (falling back to [type.kind,type.family]).
  function nodeAsType(node) {
    return { classification: nodeClassification(node), kind: node && node.kind, family: node && node.family, layer: node && node.layer };
  }

  // resolve a bare edge.kind ("face","part-of",…) → its relationship Type record.
  // relationships-seed.js registers them as `relationship.<kind>`.
  function resolveRelationType(R, kind) {
    // prefer the namespaced id; also accept a pre-namespaced kind (defensive)
    var id = (String(kind).indexOf('relationship.') === 0) ? kind : ('relationship.' + kind);
    var t = R.get(id);
    if (!t) {
      // a relationship Type may also carry the bare kind in relationKind — scan as a fallback
      var found = R.query({ family: 'relationship' }).filter(function (rt) { return rt.relationKind === kind || rt.id === kind; })[0];
      t = found || null;
    }
    return t;
  }

  // VALIDATE — returns { ok:true, violations:[] } for a well-formed graph;
  // THROWS (loud) for an ill-formed one. Collect-then-throw so the message
  // names every specific violation, not just the first.
  function validateGlyphgraph(graph) {
    var R = window.CV_REGISTRY;
    var COND = window.CV_COND;
    if (!R) fail('CV_REGISTRY not loaded — cannot resolve relation Types (load types-core + relationships-seed first)');
    if (!graph || typeof graph !== 'object') fail('validateGlyphgraph: needs a graph object {nodes,edges}');

    var nodes = Array.isArray(graph.nodes) ? graph.nodes : fail('validateGlyphgraph: graph.nodes must be an array');
    var edges = Array.isArray(graph.edges) ? graph.edges : [];

    // index nodes by id for endpoint resolution
    var byId = {};
    nodes.forEach(function (n, i) {
      if (!n || n.id == null) fail('node[' + i + '] has no id — every glyphgraph node needs an id');
      if (byId[n.id]) fail('duplicate node id "' + n.id + '" — node ids must be unique');
      byId[n.id] = n;
    });

    var violations = [];
    var note = function (v) { violations.push(v); };

    edges.forEach(function (e, i) {
      var tag = 'edge[' + i + ']' + (e && e.kind ? ' (' + e.kind + ')' : '');

      // (1) STRUCTURE — typed + both endpoints resolve
      if (!e || typeof e !== 'object') { note(tag + ': not an edge object'); return; }
      var kind = e.kind;
      if (!kind) { note(tag + ': untyped edge — no `kind` (a relation must name its relationship type)'); }
      if (e.from == null) note(tag + ': edge has no `from` endpoint');
      else if (!byId[e.from]) note(tag + ': dangling `from` — no node with id "' + e.from + '"');
      if (e.to == null) note(tag + ': edge has no `to` endpoint');
      else if (!byId[e.to]) note(tag + ': dangling `to` — no node with id "' + e.to + '"');

      if (!kind) return;   // can't resolve a type without a kind

      // (2) RELATION-TYPE resolves
      var relType = resolveRelationType(R, kind);
      if (!relType) { note(tag + ': unknown relation-type "' + kind + '" — no relationship Type registered (loud, never a silent default)'); return; }

      var sockets = relType.sockets || {};
      var src = e.from != null ? byId[e.from] : null;
      var tgt = e.to != null ? byId[e.to] : null;

      // (3) DOMAIN/RANGE via CV_REGISTRY.accepts (the type grammar — reused)
      if (src && sockets.source) {
        if (!R.accepts(sockets.source, nodeAsType(src), e)) {
          note(tag + ': source node "' + e.from + '" (classified [' + nodeClassification(src).join(',') +
               ']) is not accepted by the `source` socket of "' + relType.id + '" (accepts [' +
               (Array.isArray(sockets.source.accepts) ? sockets.source.accepts.join(',') : JSON.stringify(sockets.source.accepts)) + '])');
        }
      }
      if (tgt && sockets.target) {
        if (!R.accepts(sockets.target, nodeAsType(tgt), e)) {
          note(tag + ': target node "' + e.to + '" (classified [' + nodeClassification(tgt).join(',') +
               ']) is not accepted by the `target` socket of "' + relType.id + '" (accepts [' +
               (Array.isArray(sockets.target.accepts) ? sockets.target.accepts.join(',') : JSON.stringify(sockets.target.accepts)) + '])');
        }
      }

      // (4) EDGE-INSTANCE conditions (distinct from socket conditions accepts() ran).
      // The relationship Type may carry `conditions` the edge must satisfy, and the
      // edge instance may carry its own. Evaluate against the edge spec.
      var edgeCtx = { kind: kind, line: e.line, lineColor: e.lineColor, direction: e.direction,
                      from: e.from, to: e.to, source: src, target: tgt };
      var typeConds = relType.conditions || [];
      var edgeConds = e.conditions || [];
      var allConds = typeConds.concat(edgeConds);
      if (allConds.length) {
        if (!COND) fail('CV_COND not loaded — cannot evaluate edge conditions on ' + tag);
        var failed = COND.failures(allConds, edgeCtx);
        if (failed.length) {
          note(tag + ': edge condition(s) failed — [' + failed.join(' ; ') + ']');
        }
      }
    });

    if (violations.length) {
      fail('ill-formed glyphgraph — ' + violations.length + ' violation(s):\n  · ' + violations.join('\n  · '));
    }
    return { ok: true, violations: [] };
  }

  // a non-throwing companion for editors/UI — collects violations without raising.
  function checkGlyphgraph(graph) {
    try { validateGlyphgraph(graph); return { ok: true, violations: [] }; }
    catch (e) { return { ok: false, error: e.message, violations: (e.message.split('\n  · ').slice(1)) }; }
  }

  var CV_GLYPHGRAPH = {
    validateGlyphgraph: validateGlyphgraph,
    checkGlyphgraph: checkGlyphgraph,
    // exposed for harness/diagnostics
    _nodeClassification: nodeClassification,
    _resolveRelationType: function (kind) { return resolveRelationType(window.CV_REGISTRY, kind); },
  };

  if (typeof window !== 'undefined') window.CV_GLYPHGRAPH = CV_GLYPHGRAPH;
  if (typeof module !== 'undefined' && module.exports) module.exports = CV_GLYPHGRAPH;
})();
