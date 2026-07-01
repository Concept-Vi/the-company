// axes/color/color-axis.js
// ============================================================================
// THE COLOUR AXIS — window.CV_AXES.resolve('color')
//
// The colour axis IS the colour TOKENS (colors_and_type.css), typed and grouped
// — not a layer over them. Tokens are the value-units of this axis: each value's
// canonical identity is its --token; resolveCSS → var(--token); the hex stays in
// the stylesheet (one home for the literal). The axis adds type/grouping; a
// component's colour slot declares a token through it.
//
// Groups: brand · semantic (status) · ink (text) · communication · neutral.
// Consumers (Glyphic ring/symbol/fill, badges, nodes…) subscribe to a subset.
//
// Load after axes/axis-core.js.
// ============================================================================
(function () {
  'use strict';
  if (!window.CV_AXES) { console.error('color-axis.js: CV_AXIS core must load first'); return; }

  var color = window.CV_AXES.make({
    id: 'color',
    label: 'Colour',
    description: 'Grouped, typed view over the colour token graph. Each value → a role token (var(--…)). Meaning of a value is contextual — see CV_MEANING.',
    groups: [
      { id: 'brand',         label: 'Brand' },
      { id: 'semantic',      label: 'Semantic / status' },
      { id: 'ink',           label: 'Ink / text' },
      { id: 'communication', label: 'Communication' },
      { id: 'neutral',       label: 'Neutral' },
    ],
    values: [
      // brand
      { id: 'gold',        label: 'Gold',         group: 'brand', token: 'accent-gold' },
      { id: 'gold-deep',   label: 'Gold deep',    group: 'brand', token: 'accent-gold-deep' },
      { id: 'gold-soft',   label: 'Gold soft',    group: 'brand', token: 'accent-gold-soft' },
      { id: 'bronze',      label: 'Bronze',       group: 'brand', token: 'accent-bronze' },
      { id: 'bronze-2',    label: 'Bronze deep',  group: 'brand', token: 'accent-bronze-2' },
      { id: 'tan',         label: 'Tan',          group: 'brand', token: 'accent-tan' },
      // semantic status
      { id: 'success',     label: 'Success',      group: 'semantic', token: 'status-success' },
      { id: 'warning',     label: 'Warning',      group: 'semantic', token: 'status-warning' },
      { id: 'error',       label: 'Error',        group: 'semantic', token: 'status-error' },
      { id: 'info',        label: 'Info',         group: 'semantic', token: 'status-info' },
      { id: 'pending',     label: 'Pending',      group: 'semantic', token: 'status-pending' },
      // ink
      { id: 'ink',         label: 'Ink',          group: 'ink', token: 'fg-primary' },
      { id: 'ink-2',       label: 'Ink 2',        group: 'ink', token: 'fg-secondary' },
      { id: 'muted',       label: 'Muted',        group: 'ink', token: 'fg-muted' },
      { id: 'soft',        label: 'Soft',         group: 'ink', token: 'fg-soft' },
      // communication
      { id: 'sage',        label: 'Sage',         group: 'communication', token: 'accent-communication' },
      { id: 'sage-soft',   label: 'Sage soft',    group: 'communication', token: 'accent-communication-soft' },
      // neutral
      { id: 'paper',       label: 'Paper',        group: 'neutral', token: 'paper' },
      { id: 'surface',     label: 'Surface',      group: 'neutral', token: 'bg-surface' },
    ],
    default: 'bronze',
  });

  // alias map so legacy short names used across cards resolve (amber→warning, clay→error, blue→info)
  color.register({ id: 'amber', label: 'Amber', group: 'semantic', token: 'status-warning' });
  color.register({ id: 'clay',  label: 'Clay',  group: 'semantic', token: 'status-error' });
  color.register({ id: 'blue',  label: 'Blue',  group: 'semantic', token: 'status-info' });

  window.CV_AXES.register(color);
})();
