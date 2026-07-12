// axes/level/level-axis.js
// ============================================================================
// THE LEVEL AXIS — window.CV_AXES.resolve('level')
//
// The containment LADDER as a typed axis: a block's coordinate in depth.
// This is the zoning/containment ladder (analysis/AXES.md) made subscribable —
// the ONE home for the rungs; app/registry/block-type.js READS it (never a
// parallel list). Each value's meta carries what the rung DERIVES:
//   rank      the numeric depth coordinate
//   modifier  the material depth-modifier (base / raised / inset)
//   keyline   the rung's default content inset (a space-axis value id)
//   gap       the rung's default child gap (a space-axis value id)
// Deeper rungs breathe tighter — the spacing rhythm is a RULE of the ladder,
// not a per-instance choice. Zero = page (the whole artifact).
// ============================================================================
(function () {
  'use strict';
  if (!window.CV_AXES) { console.error('level-axis.js: CV_AXIS core must load first'); return; }

  var level = window.CV_AXES.make({
    id: 'level',
    label: 'Level',
    description: 'The containment-depth coordinate: page \u2192 region \u2192 panel \u2192 card \u2192 well, plus overlay above the flow. The rung derives the material depth-modifier and the spacing rhythm.',
    groups: [
      { id: 'flow', label: 'In the flow' },
      { id: 'above', label: 'Above the flow' },
    ],
    values: [
      { id: 'page',    label: 'Page',    group: 'flow',  zero: true, meta: { rank: 0, modifier: null,     keyline: 's4', gap: 's4', means: 'the whole artifact \u2014 owns the ground; usually material none' } },
      { id: 'region',  label: 'Region',  group: 'flow',  meta: { rank: 1, modifier: null,     keyline: 's4', gap: 's4', means: 'a top-level area (nav rail, main, side panel)' } },
      { id: 'panel',   label: 'Panel',   group: 'flow',  meta: { rank: 2, modifier: 'base',   keyline: 's5', gap: 's4', means: 'a floating surface \u2014 the default block' } },
      { id: 'card',    label: 'Card',    group: 'flow',  meta: { rank: 3, modifier: 'inset',  keyline: 's4', gap: 's3', means: 'a unit INSIDE a panel \u2014 reads recessed' } },
      { id: 'well',    label: 'Well',    group: 'flow',  meta: { rank: 4, modifier: 'inset',  keyline: 's3', gap: 's2', means: 'a carved-in slot inside a card' } },
      { id: 'overlay', label: 'Overlay', group: 'above', meta: { rank: 5, modifier: 'raised', keyline: 's5', gap: 's4', means: 'above the page flow \u2014 menu, popover, modal' } },
    ],
    default: 'panel',
  });
  window.CV_AXES.register(level);
})();
