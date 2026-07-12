// axes/shadow/shadow-axis.js
// ============================================================================
// The SHADOW axis — a cast shadow / elevation under a mark. Registered into the
// one CV_AXES registry; default is `none` (off). resolveCSS → a drop-shadow
// filter. (Distinct from `depth`, which is the conceptual elevation step on the
// glyphic's own geometry; this is the surface shadow a mark casts.)
// Load after axes/axis-core.js.
// ============================================================================
(function () {
  'use strict';
  if (typeof window === 'undefined' || !window.CV_AXES) { if (typeof console !== 'undefined') console.error('shadow-axis.js: CV_AXES must load first'); return; }
  window.CV_AXES.register({
    id: 'shadow', label: 'Shadow', description: 'A cast shadow / elevation under a mark. Off by default.',
    default: 'none',
    values: [
      { id: 'none', label: 'No shadow', zero: true },
      { id: 'low', label: 'Low', css: 'drop-shadow(0 2px 4px rgba(90,70,40,.24))' },
      { id: 'medium', label: 'Medium', css: 'drop-shadow(0 6px 11px rgba(90,70,40,.3))' },
      { id: 'high', label: 'High', css: 'drop-shadow(0 12px 20px rgba(90,70,40,.32))' },
      { id: 'deep', label: 'Deep', css: 'drop-shadow(0 20px 34px rgba(90,70,40,.34))' }
    ]
  });
})();
