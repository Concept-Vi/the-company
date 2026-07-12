// axes/density/density-axis.js
// ============================================================================
// THE DENSITY AXIS — window.CV_AXES.resolve('density')
//
// Typed view over the density knob (tokens/density.css): one scalar that
// re-tunes every --d-* spacing token. The MECHANISM stays in density.css
// (data-density + --density); this axis is its subscribable face — a block's
// density slot resolves its vocabulary here. meta.scalar is informational
// (the token file remains the source of the multiplier).
// ============================================================================
(function () {
  'use strict';
  if (!window.CV_AXES) { console.error('density-axis.js: CV_AXIS core must load first'); return; }

  var density = window.CV_AXES.make({
    id: 'density',
    label: 'Density',
    description: 'Breathing room. One scalar (data-density \u2192 --density) scales every density-aware token; compact tightens, spacious relaxes.',
    values: [
      { id: 'compact',     label: 'Compact \u00b7 0.8\u00d7',  css: 'compact',     meta: { scalar: 0.8,  attr: 'compact' } },
      { id: 'comfortable', label: 'Comfortable \u00b7 1\u00d7', css: 'comfortable', zero: true, meta: { scalar: 1,    attr: 'comfortable' } },
      { id: 'spacious',    label: 'Spacious \u00b7 1.25\u00d7', css: 'spacious',    meta: { scalar: 1.25, attr: 'spacious' } },
    ],
    default: 'comfortable',
  });
  window.CV_AXES.register(density);
})();
