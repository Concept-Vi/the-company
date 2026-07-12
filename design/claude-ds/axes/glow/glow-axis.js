// axes/glow/glow-axis.js
// ============================================================================
// The GLOW axis — a soft luminous halo a mark can carry. Registered into the one
// CV_AXES registry like every other visual dimension; default is `none` (off).
// resolveCSS → a drop-shadow filter (tinted to the mark's own colour).
// Load after axes/axis-core.js.
// ============================================================================
(function () {
  'use strict';
  if (typeof window === 'undefined' || !window.CV_AXES) { if (typeof console !== 'undefined') console.error('glow-axis.js: CV_AXES must load first'); return; }
  window.CV_AXES.register({
    id: 'glow', label: 'Glow', description: 'A soft luminous halo around a mark. Off by default.',
    default: 'none',
    values: [
      { id: 'none', label: 'No glow', zero: true },
      { id: 'soft', label: 'Soft', css: 'drop-shadow(0 0 5px color-mix(in srgb, currentColor 55%, transparent))' },
      { id: 'medium', label: 'Medium', css: 'drop-shadow(0 0 11px color-mix(in srgb, currentColor 68%, transparent))' },
      { id: 'strong', label: 'Strong', css: 'drop-shadow(0 0 20px color-mix(in srgb, currentColor 80%, transparent))' }
    ]
  });
})();
