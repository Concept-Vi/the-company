// axes/space/space-axis.js
// ============================================================================
// THE SPACE AXIS — window.CV_AXES.resolve('space')
//
// Typed view over the strict 8px spacing scale (--s-* in colors_and_type.css).
// Values point at the spacing tokens; meta.px is informational only (the token
// remains the source). One home for "the spacing steps the system offers".
// ============================================================================
(function () {
  'use strict';
  if (!window.CV_AXES) { console.error('space-axis.js: CV_AXIS core must load first'); return; }

  var steps = [
    ['s0', 's-0', 0], ['s1', 's-1', 4], ['s2', 's-2', 8], ['s3', 's-3', 12],
    ['s4', 's-4', 16], ['s5', 's-5', 20], ['s6', 's-6', 24], ['s7', 's-7', 32],
    ['s9', 's-9', 40], ['s12', 's-12', 48], ['s14', 's-14', 56], ['s16', 's-16', 64],
    ['s20', 's-20', 80], ['s24', 's-24', 96],
  ];
  var space = window.CV_AXES.make({
    id: 'space',
    label: 'Space',
    description: 'The 8px spacing rhythm (--s-*). One home for gaps, padding, margins.',
    groups: [
      { id: 'inner', label: 'Inner (chips → cards)' },
      { id: 'between', label: 'Between siblings/sections' },
      { id: 'layout', label: 'Layout (panels → gutters)' },
    ],
    values: steps.map(function (s, i) {
      return { id: s[0], label: s[2] + 'px', token: s[1], zero: s[2] === 0,
               group: i <= 3 ? 'inner' : (i <= 7 ? 'between' : 'layout'), meta: { px: s[2] } };
    }),
    default: 's4',
  });
  window.CV_AXES.register(space);
})();
