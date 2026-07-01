// app/registry/glyphic-type.js
// ============================================================================
// Registers the GLYPHIC into CV_REGISTRY as the reference universal component —
// the first worked example of the parts / slots / sockets / declarations grammar
// every other component kind (panel, graph, slide …) will share.
//
// SINGLE SOURCE: this file declares STRUCTURE only (which parts, which sockets,
// which slot belongs to which part). The slot VOCABULARIES are read live from
// CV_GLYPHIC.facets — there is no second list of forms/fills/textures here.
//
// Vocabulary (from the Glyphic spec, system/glyphic-system.html §5c–§5e):
//   · slot   — a parameter that takes a VALUE from a single-source vocabulary
//   · socket — an attachment point that takes a TYPE (another component), or an
//              event; carries accepts/forbid conditions + an address to occupant
//   · part   — a named sub-component with its own slots/sockets/conditions
//
// Load order: types-core.js → cv-shapes/cv-icons/cv-glyphics → glyphic-type.js
// ============================================================================
(function () {
  'use strict';
  var R = window.CV_REGISTRY;
  if (!R) { console.error('glyphic-type.js: CV_REGISTRY must load first'); return; }
  var G = window.CV_GLYPHIC;

  // A value-slot declaration = a SUBSCRIPTION to an axis (CV_AXES). The slot
  // names the axis and (optionally) which groups/values of it this part accepts;
  // the vocabulary is resolved live from the axis — never copied here. This is
  // what an editor/foundry reads via CV_AXES.candidates(subscription).
  function sub(axisId, extra) {
    var AX = window.CV_AXES;
    var def = (AX && AX.has && AX.has(axisId)) ? AX.resolve(axisId).default() : undefined;
    return Object.assign({ axis: axisId, default: def }, extra || {});
  }

  // ---- the three part sub-types (each registerable, each declares its own) ---
  // They are 'token'-ish atoms; classified so the parent's sockets accept them.
  var partTypes = [
    {
      id: 'glyphic-ring', name: 'Outer ring', kind: 'ring', layer: 'atom',
      family: 'glyphic-part', classification: ['ring'],
      description: 'A regular n-gon with a stroke weight. Bounds an inner space (the fill plane) and an outer space (ring → square edge).',
      icon: 'hexagon',
      valueSlots: {
        form:      sub('form'),
        thickness: { axis: null, vocab: 'CV_SHAPES.markBox.stroke', default: 2.5, means: 'ring line weight' },
        color:     sub('color', { groups: ['brand', 'semantic', 'communication'], default: 'gold', means: 'ring colour' }),
        texture:   sub('texture'),
      },
      sockets: {
        innerSpace: { label: 'Inner space (fill)', accepts: ['fill'], optional: true,
                      means: 'the plane between ring and symbol; α-0 = none' },
        outerSpace: { label: 'Outer space', accepts: ['fill', 'glyphic'], optional: true,
                      means: 'ring → square edge; normally α-0, available when needed' },
      },
      conditions: ['texture requires fill != none'],
    },
    {
      id: 'glyphic-symbol', name: 'Symbol', kind: 'symbol', layer: 'atom',
      family: 'glyphic-part', classification: ['symbol'],
      description: 'The distinct inner glyph (a CV_ICONS id). Its meaning is intrinsic — the one facet a loadable meaning profile never governs.',
      icon: 'star',
      valueSlots: {
        symbol:  sub('symbol'),
        color:   sub('color', { default: 'bronze', means: 'symbol colour' }),
        texture: sub('texture'),
      },
    },
    {
      id: 'glyphic-fill', name: 'Fill', kind: 'fill', layer: 'token',
      family: 'glyphic-part', classification: ['fill'],
      description: 'A space treatment that occupies the ring’s inner (or outer) space socket. Its zero is α-0 (none).',
      icon: 'square',
      valueSlots: { fill: sub('fill'), color: sub('color', { groups: ['brand', 'neutral'], default: 'gold-soft' }) },
    },
  ];

  // ---- the parent Glyphic Type --------------------------------------------
  var glyphicType = {
    id: 'glyphic', name: 'Glyphic', kind: 'glyphic', layer: 'atom',
    family: 'glyphic', classification: ['glyphic', 'mark', 'atom'],
    description: 'The universal compositional mark — a perfect-square element with an outer-ring socket and a symbol socket, plus whole-unit slots (size, motion, depth, allocated value). The reference universal component.',
    icon: 'hexagon',
    provenance: 'built-in',
    // whole-unit value slots (parent-level) — each a subscription to an axis
    valueSlots: {
      size:   sub('size'),
      motion: sub('motion'),
      depth:  sub('depth'),
      value:  { axis: null, vocab: 'CV_MEANING.valuesFor("color")', default: null, optional: true,
                means: 'an allocated value (state/type/category) that drives colour via the active meaning profile' },
    },
    // named sub-component sockets (which part-types plug into the parent)
    sockets: {
      ring:   { label: 'Outer ring', accepts: ['ring'],   address: 'glyphic-ring' },
      symbol: { label: 'Symbol',     accepts: ['symbol'], address: 'glyphic-symbol' },
    },
    // the part-tree, inlined so the parent's declaration is self-contained
    parts: {
      ring:   { type: 'glyphic-ring' },
      symbol: { type: 'glyphic-symbol' },
    },
    conditions: ['symbol meaning is intrinsic (never profile-governed)'],
    defaults: (G && G.defaults) || {},
    tags: ['glyphic', 'mark', 'icon', 'universal-component'],
  };

  R.registerMany(
    partTypes.map(function (t) { return Object.assign({ provenance: 'built-in' }, t); }),
    { silent: true }
  );
  R.register(glyphicType, { silent: true });

  // expose the live slot-vocabulary resolver so editors/the foundry can read
  // a glyphic Type's value spaces without duplicating CV_GLYPHIC.
  R.glyphic = {
    type: function () { return R.resolve('glyphic'); },
    valuesFor: function (facet) { return G ? G.valuesOf(facet) : null; },
  };
})();
