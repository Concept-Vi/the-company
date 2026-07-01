// axes/size/size-axis.js
// ============================================================================
// THE SIZE AXIS — window.CV_AXES.resolve('size')
//
// The element/mark size ramp. Its VALUE-UNITS ARE TOKENS (--size-* in
// tokens/sizing.css) — the axis is those tokens, typed and ordered, not a
// replacement for them. resolveCSS → var(--size-*); meta.px is the resolved
// number for computational consumers (e.g. SVG width in the Glyphic). The
// inline --icon-* scale (tokens/icons.css) is the icon-within-chrome sub-scale.
// ============================================================================
(function () {
  'use strict';
  if (!window.CV_AXES) { console.error('size-axis.js: CV_AXIS core must load first'); return; }

  var sizes = [
    ['xs', 'size-xs', 16], ['sm', 'size-sm', 24], ['md', 'size-md', 40],
    ['lg', 'size-lg', 56], ['xl', 'size-xl', 72], ['hero', 'size-hero', 96],
  ];
  var size = window.CV_AXES.make({
    id: 'size',
    label: 'Size',
    description: 'Element/mark size ramp. Value-units are the --size-* tokens (tokens/sizing.css). meta.px = the resolved number for SVG/JS consumers.',
    groups: [
      { id: 'inline', label: 'Inline / chip' },
      { id: 'standard', label: 'Standard' },
      { id: 'feature', label: 'Feature / hero' },
    ],
    values: sizes.map(function (s, i) {
      return { id: s[0], label: s[0] + ' · ' + s[2] + 'px', token: s[1],
               group: i <= 1 ? 'inline' : (i <= 3 ? 'standard' : 'feature'), meta: { px: s[2] } };
    }),
    default: 'md',
  });
  window.CV_AXES.register(size);
})();
