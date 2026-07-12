// axes/flow/flow-axis.js
// ============================================================================
// THE FLOW AXIS — window.CV_AXES.resolve('flow')
//
// Typed view over the Group-level arrangement intent (tokens/layout.css §FLOW):
// what a group of N siblings does when its container cannot fit --count columns
// at --item-min. The CSS mechanism (the .flow utility + data-flow attribute +
// the computed --flow-basis equation) lives in tokens/layout.css; this axis is
// its typed, subscribable face. Zero = wrap (the default collapse).
// ============================================================================
(function () {
  'use strict';
  if (!window.CV_AXES) { console.error('flow-axis.js: CV_AXIS core must load first'); return; }

  var flow = window.CV_AXES.make({
    id: 'flow',
    label: 'Flow',
    description: 'Overflow intent for a group of siblings: wrap to rows, keep one sacred row (reel, horizontal scroll + snap), or force exactly N columns (fixed \u2014 known-width surfaces only).',
    values: [
      { id: 'wrap',  label: 'Wrap',  zero: true, css: 'wrap',  meta: { attr: 'wrap' } },
      { id: 'reel',  label: 'Reel',  css: 'reel',  meta: { attr: 'reel' } },
      { id: 'fixed', label: 'Fixed', css: 'fixed', meta: { attr: 'fixed', caution: 'known-width surfaces only \u2014 tracks may crush below the legibility floor' } },
    ],
    default: 'wrap',
  });
  window.CV_AXES.register(flow);
})();
