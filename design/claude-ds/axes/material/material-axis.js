// axes/material/material-axis.js
// ============================================================================
// THE MATERIAL AXIS — window.CV_AXES.resolve('material')
//
// Typed view over the surface materials in tokens/material.css (glass binds to
// tokens/glass.css — its home). A Block's SURFACE part subscribes to this axis;
// the value's meta carries the data-material attribute + depth-modifier class
// the block solver emits. Zero = none (a block with no surface: pure layout).
// Values reference the material scopes — never a copied literal.
// ============================================================================
(function () {
  'use strict';
  if (!window.CV_AXES) { console.error('material-axis.js: CV_AXIS core must load first'); return; }

  var material = window.CV_AXES.make({
    id: 'material',
    label: 'Material',
    description: 'What a Block\u2019s surface is made of. Translucent materials refract the ground behind them; opaque ones occlude it. One consuming utility (.material), one scope per material (tokens/material.css). \u201cskin\u201d = the active skin\u2019s own surface.',
    groups: [
      { id: 'translucent', label: 'Translucent', description: 'Backdrop-filtered: the ground reads through.' },
      { id: 'opaque', label: 'Opaque', description: 'Occludes the ground; texture is the material\u2019s own.' },
      { id: 'zero', label: 'None' },
    ],
    values: [
      { id: 'none',      label: 'None (pure layout)', group: 'zero', zero: true, meta: { attr: 'none' } },
      { id: 'skin',      label: 'Skin default', group: 'translucent', meta: { attr: 'skin', means: 'the active skin\u2019s own surface (tokens/skins.css binds it per data-skin scope)' } },
      { id: 'glass',     label: 'Glass',      group: 'translucent', token: 'glass-fill',     meta: { attr: 'glass' } },
      { id: 'velum',     label: 'Velum',      group: 'translucent', token: 'velum-fill',     meta: { attr: 'velum' } },
      { id: 'parchment', label: 'Parchment',  group: 'opaque',      token: 'parchment-fill', meta: { attr: 'parchment' } },
      { id: 'stone',     label: 'Stone',      group: 'opaque',      token: 'stone-fill',     meta: { attr: 'stone' } },
    ],
    default: 'glass',
  });
  window.CV_AXES.register(material);
})();
