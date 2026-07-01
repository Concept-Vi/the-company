// axes/texture/texture-axis.js
// ============================================================================
// THE TEXTURE AXIS — window.CV_AXES.resolve('texture')
//
// Typed view over surface textures (tokens/texture.css + the pattern set the
// Glyphic compositor knows). One home for "which textures exist"; the actual
// pattern geometry is realised by CV_SHAPES.markSVG / texture.css. Zero = none.
// ============================================================================
(function () {
  'use strict';
  if (!window.CV_AXES) { console.error('texture-axis.js: CV_AXIS core must load first'); return; }

  var texture = window.CV_AXES.make({
    id: 'texture',
    label: 'Texture',
    description: 'Surface pattern on a part. Realised by CV_SHAPES.markSVG / tokens/texture.css. Generalises beyond directional lines.',
    groups: [
      { id: 'none', label: 'None' },
      { id: 'line', label: 'Linear' },
      { id: 'field', label: 'Field' },
    ],
    values: [
      { id: 'none',  label: 'None',       group: 'none', zero: true },
      { id: 'hatch', label: 'Hatch',      group: 'line' },
      { id: 'lines', label: 'Lines',      group: 'line' },
      { id: 'vert',  label: 'Vertical',   group: 'line' },
      { id: 'cross', label: 'Cross-hatch',group: 'field' },
      { id: 'grid',  label: 'Grid',       group: 'field' },
      { id: 'dense', label: 'Dense',      group: 'field' },
      { id: 'dots',  label: 'Dots',       group: 'field' },
    ],
    default: 'none',
  });
  window.CV_AXES.register(texture);
})();
