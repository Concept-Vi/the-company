/**
 * ConceptV — EDGE REGISTRY  (window.CV_EDGES)
 * ============================================================================
 * The RELATIONAL sibling of CV_SHAPES.shapeTypes. Where a FORM types a NODE
 * (circle=Entity, hex=System, …), an EDGE KIND types a RELATION between two
 * nodes. This is the ONE home for edge kinds + their facets — exactly the
 * single-source, extend-by-registration shape of the geometry/form registry.
 *
 * An edge is faceted like a node: a `line` (the textured relational line —
 * the relation's material/sub-class, mirroring node `texture`), a `direction`
 * (the directional edge: to/from/both/none), and an `ink` (the relational
 * signal — an allocated colour value, mirroring node `color`). The GEOMETRY of
 * the line+arrow lives in CV_SHAPES.edgeSVG (geometry single source);
 * CV_GLYPHIC.composeRelation reads THIS for the kind→facets and composes a
 * node→edge→node relational glyphic.
 *
 * Add an edge kind = add an entry here; it is available everywhere (the
 * `higher-order` / `navigates` kinds below are the contextual-navigation modes
 * Tim named — edge KINDS, not separate systems). Load after cv-shapes.js,
 * before cv-glyphics.js.
 *
 * CONVERGENCE with the registry grammar (app/registry/glyphic-type.js): a glyphic
 * `socket` already takes a TYPE (another glyphic) + an address-to-occupant + accepts/
 * forbid conditions — the STRUCTURAL relation. An edge KIND here is the *type of that
 * relation* (face / documents / …) and its rendered facets; CV_GLYPHIC.composeRelation
 * is how a socketed relation is DRAWN. Sockets = structure; edge-kinds = the relation's
 * type + look. They compose; this is not a second relation model.
 */
(function () {
  'use strict';

  // EDGE KINDS — the typed relations. `means` is the semantic (like shapeTypes.meaning).
  var EDGE_KINDS = [
    { id: 'face',         type: 'Face',         line: 'dashed', direction: 'to', ink: 'gold',
      means: 'this thing has a viewable PAGE — the page is the visible face/projection of the source.' },
    { id: 'documents',    type: 'Documents',    line: 'dashed', direction: 'to', ink: 'bronze',
      means: 'the source explains/teaches the target — a how-to or guide for it.' },
    { id: 'higher-order', type: 'Higher-order', line: 'lines',  direction: 'to', ink: 'sage',
      means: 'the source connects UP to a higher-order concept it is an instance or part of.' },
    { id: 'navigates',    type: 'Navigates',    line: 'dots',   direction: 'both', ink: 'muted',
      means: 'contextual navigation — moving between related places in the system.' },
  ];

  var CV_EDGES = {
    kinds: EDGE_KINDS,
    kind: function (id) { return EDGE_KINDS.find(function (k) { return k.id === id; }) || null; },
    ids: function () { return EDGE_KINDS.map(function (k) { return k.id; }); },
    means: function (id) { var k = this.kind(id); return k ? k.means : null; },

    // Resolve a partial edge-spec {kind, line?, direction?, ink?} → full facets, applying the kind's
    // defaults. Loud: an unknown kind that also gives no facets falls back to 'face' but keeps the id
    // visible so a typo is seen, never silently a different relation.
    resolve: function (spec) {
      spec = spec || {};
      var k = this.kind(spec.kind) || {};
      return {
        kind: spec.kind || k.id || 'face',
        type: k.type || 'Relation',
        line: spec.line || k.line || 'dashed',
        direction: spec.direction || k.direction || 'to',
        ink: spec.ink || k.ink || 'bronze',
        means: k.means || null,
      };
    },
  };

  if (typeof window !== 'undefined') window.CV_EDGES = CV_EDGES;
})();
