// axes/ground/ground-axis.js
// ============================================================================
// THE GROUND AXIS — window.CV_AXES.resolve('ground') — the registry face for
// a skin's GROUND PLANE (the surface behind the blocks). The actual image URLs
// live ONCE as --tex-* tokens in tokens/skins.css; this axis is the enumerable,
// subscribable list of "which grounds exist" so the interface is a projection
// of the registry, not a parallel list. A skin picks a ground; --skin-ground
// composes it. (analysis/SKINS.md §7.)
// ============================================================================
(function () {
  'use strict';
  if (!window.CV_AXES) { console.error('ground-axis.js: CV_AXIS core must load first'); return; }

  var ground = window.CV_AXES.make({
    id: 'ground',
    label: 'Ground',
    description: 'The plane behind the blocks (a skin\u2019s backdrop). Image URLs are single-sourced as --tex-* in tokens/skins.css; composited with light gradients by --skin-ground.',
    groups: [
      { id: 'stone', label: 'Stone worlds' },
      { id: 'glass', label: 'Glass worlds' },
      { id: 'plain', label: 'Plain' },
    ],
    values: [
      { id: 'plaster',   label: 'Champagne plaster', group: 'stone', token: 'tex-plaster',   meta: { world: 'stone' } },
      { id: 'plaster-cool', label: 'Greige plaster',  group: 'stone', token: 'tex-plaster-cool', meta: { world: 'stone' } },
      { id: 'linen',     label: 'Linen',             group: 'stone', token: 'tex-linen',     meta: { world: 'stone' } },
      { id: 'paper-fiber', label: 'Paper fiber',     group: 'stone', token: 'tex-paper-fiber', meta: { world: 'stone' } },
      { id: 'graphite',  label: 'Graphite',          group: 'glass', token: 'tex-graphite',  meta: { world: 'glass' } },
      { id: 'ink-depth', label: 'Ink depth',         group: 'glass', token: 'tex-ink-depth', meta: { world: 'glass' }, zero: true },
      { id: 'ink-depth-deep', label: 'Ink depth · deep', group: 'glass', token: 'tex-ink-depth-deep', meta: { world: 'glass' } },
      { id: 'none',      label: 'None (canvas)',     group: 'plain' },
    ],
    default: 'ink-depth',
  });
  window.CV_AXES.register(ground);
})();
