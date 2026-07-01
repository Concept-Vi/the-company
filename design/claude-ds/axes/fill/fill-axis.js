// axes/fill/fill-axis.js
// ============================================================================
// THE FILL AXIS — window.CV_AXES.resolve('fill')
//
// Typed view over the ring's inner-space treatment (the fill plane). Values are
// token RECIPES (resolved against the colour axis / token graph), not raw
// colours. Zero = none (α-0, transparent). One home for "which fills exist".
// The actual gradient ramps live in CV_GLYPHIC (FILL_RAMPS); this axis is the
// vocabulary + meaning surface.
// ============================================================================
(function () {
  'use strict';
  if (!window.CV_AXES) { console.error('fill-axis.js: CV_AXIS core must load first'); return; }

  var fill = window.CV_AXES.make({
    id: 'fill',
    label: 'Fill',
    description: 'Ring inner-space treatment. Token recipes, not raw colours. Zero = none (transparent).',
    groups: [
      { id: 'none', label: 'None' },
      { id: 'surface', label: 'Surface' },
      { id: 'colour', label: 'Colour' },
    ],
    values: [
      { id: 'none',  label: 'None · α0', group: 'none', zero: true },
      { id: 'paper', label: 'Paper',     group: 'surface', meta: { ramp: 'paper' } },
      { id: 'wash',  label: 'Wash',      group: 'surface', meta: { ramp: 'wash' } },
      { id: 'tint',  label: 'Tint',      group: 'colour', meta: { ramp: 'tint', fromColor: true } },
    ],
    default: 'paper',
  });
  window.CV_AXES.register(fill);
})();
