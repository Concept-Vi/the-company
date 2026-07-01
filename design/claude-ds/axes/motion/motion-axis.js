// axes/motion/motion-axis.js
// ============================================================================
// THE MOTION AXIS — window.CV_AXES.resolve('motion')
//
// Motion is a first-class axis, NOT a glyphic-owned feature. Many typed values
// organised into GROUPS (ambient · attention · interactive · process), each
// value pointing at a keyframe/class whose ANIMATION lives in motion.css (one
// home). Any consumer (a Glyphic, a card, a node, a future panel) SUBSCRIBES to
// a subset and resolves the CSS class from here — no consumer redefines motion.
//
// resolveCSS(id) → the CSS class name that motion.css realises ('' for 'none').
// Aligns with tokens/motion.css ("nothing teleports") for durations/easing.
//
// Load after axes/axis-core.js; motion.css must be linked for the animations.
// ============================================================================
(function () {
  'use strict';
  if (!window.CV_AXES) { console.error('motion-axis.js: CV_AXIS core must load first'); return; }

  var motion = window.CV_AXES.make({
    id: 'motion',
    label: 'Motion',
    description: 'Ambient/entrance/interactive animation. Typed groups; each value is a CSS class realised in axes/motion/motion.css.',
    groups: [
      { id: 'static',      label: 'Static',      description: 'No motion — settled.' },
      { id: 'ambient',     label: 'Ambient',     description: 'Continuous low-energy life (idle-active).' },
      { id: 'attention',   label: 'Attention',   description: 'Draws the eye — new / urgent / active.' },
      { id: 'interactive', label: 'Interactive', description: 'Responds to the user (hover/feedback).' },
      { id: 'process',     label: 'Process',     description: 'Indicates work happening.' },
    ],
    // each value: token-free; css = the class motion.css defines. zero on 'none'.
    values: [
      { id: 'none',    label: 'None',    group: 'static',      zero: true, css: '' },
      { id: 'breathe', label: 'Breathe', group: 'ambient',     css: 'mo-breathe', meta: { loop: true } },
      { id: 'float',   label: 'Float',   group: 'ambient',     css: 'mo-float',   meta: { loop: true } },
      { id: 'pulse',   label: 'Pulse',   group: 'attention',   css: 'mo-pulse',   meta: { loop: true } },
      { id: 'glow',    label: 'Glow',    group: 'attention',   css: 'mo-glow',    meta: { loop: true } },
      { id: 'bob',     label: 'Bob',     group: 'attention',   css: 'mo-bob',     meta: { loop: true } },
      { id: 'tilt',    label: 'Tilt',    group: 'interactive', css: 'mo-tilt',    meta: { hover: true } },
      { id: 'spin',    label: 'Spin',    group: 'process',     css: 'mo-spin',    meta: { loop: true } },
    ],
    default: 'none',
  });

  window.CV_AXES.register(motion);
})();
