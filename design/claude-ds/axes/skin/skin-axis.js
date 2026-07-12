// axes/skin/skin-axis.js
// ============================================================================
// THE SKIN AXIS — window.CV_AXES.resolve('skin') — the REGISTRY OF SKINS.
//
// A skin is a coordinated point across the existing axes (ground × material ×
// shadow × edge × state language), scoped by data-skin and defined as role
// re-bindings in tokens/skins.css. This axis is the enumerable, subscribable
// face: add a skin = ONE scope block there + ONE value here. The SAME blocks,
// tokens, and page specs resolve to each skin in full (analysis/SKINS.md).
// ============================================================================
(function () {
  'use strict';
  if (!window.CV_AXES) { console.error('skin-axis.js: CV_AXIS core must load first'); return; }

  var skin = window.CV_AXES.make({
    id: 'skin',
    label: 'Skin',
    description: 'The coordinated world a page resolves into: ground, default block surface, shadow character, thread/edge language, state glow. data-skin scope; roles re-bound in tokens/skins.css.',
    values: [
      { id: 'glass', label: 'Glass', zero: true, meta: { attr: 'glass', theme: 'dark', renderWorld: 'glass', ground: 'ambient light field', material: 'glass', world: 'dark, translucent, refractive' } },
      { id: 'stone', label: 'Stone', meta: { attr: 'stone', theme: 'light', renderWorld: 'stone', ground: 'champagne plaster', material: 'porcelain', world: 'light, matte, laid-on-the-wall', reference: 'the six May-2026 boards' } },
      { id: 'parchment', label: 'Parchment', meta: { attr: 'parchment', theme: 'light', renderWorld: 'stone', ground: 'woven linen', material: 'vellum sheet', world: 'light, warm, fibrous — softer than stone; sepia shadows, aged-ink accents' } },
      { id: 'carbon', label: 'Carbon', meta: { attr: 'carbon', theme: 'dark', renderWorld: 'glass', ground: 'ink depth', material: 'graphite slab', world: 'dark, matte, engineered — the opaque sibling of glass; steel-gold accents' } },
    ],
    default: 'glass',
  });
  window.CV_AXES.register(skin);
})();
