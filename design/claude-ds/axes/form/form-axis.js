// axes/form/form-axis.js
// ============================================================================
// THE FORM AXIS — window.CV_AXES.resolve('form')
//
// Typed view over the outer-ring geometry (CV_SHAPES.geom). It does NOT define
// geometry — values reference CV_SHAPES shapes by id; the n-gon progression is
// the axis "0 (no ring) → 3..8 sides → ∞ (circle)". Form→type-class MEANING
// stays in CV_SHAPES.shapeTypes (and is contextual via CV_MEANING). One home for
// "which ring forms exist".
//
// Load after axes/axis-core.js AND cv-shapes.js.
// ============================================================================
(function () {
  'use strict';
  if (!window.CV_AXES) { console.error('form-axis.js: CV_AXIS core must load first'); return; }
  var S = window.CV_SHAPES;

  // ordered by side-count (the n+1 progression); names match CV_SHAPES.geom keys
  var ORDER = [
    ['none', 0, 'No ring — symbol alone'],
    ['triangle', 3], ['square', 4], ['diamond', 4], ['pentagon', 5],
    ['hex', 6], ['heptagon', 7], ['septagon', 7], ['octagon', 8],
    ['circle', Infinity, 'Circle — the ∞ end'],
  ];

  var form = window.CV_AXES.make({
    id: 'form',
    label: 'Form',
    description: 'Outer-ring geometry from CV_SHAPES.geom. The n-gon progression 0→3..8→∞. Form→type meaning lives in CV_SHAPES.shapeTypes / CV_MEANING.',
    groups: [
      { id: 'none', label: 'No ring' },
      { id: 'polygon', label: 'Polygon (n-gon)' },
      { id: 'round', label: 'Round' },
    ],
    values: ORDER.filter(function (o) {
      return o[0] === 'none' || o[0] === 'circle' || (S && S.geom && S.geom[o[0]]);
    }).map(function (o) {
      var sides = o[1];
      return {
        id: o[0],
        label: o[2] || (o[0].charAt(0).toUpperCase() + o[0].slice(1)),
        group: o[0] === 'none' ? 'none' : (o[0] === 'circle' ? 'round' : 'polygon'),
        zero: o[0] === 'none',
        meta: { sides: sides, shape: o[0] === 'none' ? null : o[0] },
        // form has no single CSS payload; consumers render via CV_SHAPES.markSVG
        resolve: function () { return null; },
      };
    }),
    default: 'circle',
  });
  window.CV_AXES.register(form);
})();
