// axes/depth/depth-axis.js
// ============================================================================
// THE DEPTH AXIS — window.CV_AXES.resolve('depth')
//
// Typed view over elevation. Mirrors the --elev-* ramp in tokens/depth.css
// (flat=0 → d6=deep) plus 'normal' (the renderer default). The SVG drop-shadow
// geometry a Glyphic uses lives in CV_GLYPHIC (it must follow the polygon, not a
// CSS box), but the SCALE + tint single-source here / tokens/depth.css. Zero=flat.
// ============================================================================
(function () {
  'use strict';
  if (!window.CV_AXES) { console.error('depth-axis.js: CV_AXIS core must load first'); return; }

  var depth = window.CV_AXES.make({
    id: 'depth',
    label: 'Depth',
    description: 'Elevation / shadow. Mirrors tokens/depth.css --elev-* ramp. Tint from --shadow-c. Glyphic realises the polygon-accurate shadow.',
    groups: [
      { id: 'flat', label: 'Flat' },
      { id: 'raised', label: 'Raised' },
      { id: 'system', label: 'System default' },
    ],
    values: [
      { id: 'flat',   label: 'Flat · 0', group: 'flat', zero: true, token: 'elev-0' },
      { id: 'd1',     label: 'Lift',     group: 'raised', token: 'elev-1', meta: { dy: 1, blur: 1, opacity: 0.16 } },
      { id: 'd2',     label: 'Low',      group: 'raised', token: 'elev-2', meta: { dy: 2, blur: 1.8, opacity: 0.20 } },
      { id: 'd3',     label: 'Base',     group: 'raised', token: 'elev-3', meta: { dy: 3, blur: 2.6, opacity: 0.24 } },
      { id: 'd4',     label: 'Raised',   group: 'raised', token: 'elev-4', meta: { dy: 4.5, blur: 3.6, opacity: 0.28 } },
      { id: 'd5',     label: 'High',     group: 'raised', token: 'elev-5', meta: { dy: 6, blur: 5, opacity: 0.30 } },
      { id: 'd6',     label: 'Deep',     group: 'raised', meta: { dy: 8, blur: 6.5, opacity: 0.32 } },
      { id: 'normal', label: 'Normal',   group: 'system' },
    ],
    default: 'normal',
  });
  window.CV_AXES.register(depth);
})();
