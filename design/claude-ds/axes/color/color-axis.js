// axes/color/color-axis.js
// ============================================================================
// THE COLOUR AXIS — window.CV_AXES.resolve('color')
//
// The colour axis IS the colour TOKENS (colors_and_type.css), typed and grouped
// — not a layer over them. Tokens are the value-units: a value's identity is its
// --token; resolveCSS → var(--token); the hex stays in the stylesheet (one home
// for the literal). The axis adds what the tokens can't know about themselves —
// FAMILY, PAIRING, ROLE, theme-behaviour — so a colour becomes a first-class
// participant in composition (pickable, reasoned-about, AI-offerable).
//
// TWO-TIER SELF-DESCRIPTION (Info/Tim, slice 101). A rule lives at the most
// general level it is true:
//   · FAMILY level (the groups below) carries the general rule — what the family
//     is FOR (role), what foreground it PAIRS-ON, whether it is a saturated VOICE
//     vs structure, and the structural roles its values default to.
//   · VALUE level overrides only when a value genuinely differs (gold pairs on
//     ink and never flips theme; gold-deep is a text/heading colour; …).
// The families are a small RELATIONAL GRAPH — pairsOn / voice-vs-structure are
// computed once here and read everywhere (CV_AXES.pairOn / pairCSS / rolesOf /
// themeInvariant / canonical). This is the ONE home for "what ink sits on this
// colour", dissolving the hardcoded --on-gold and the compositor's solid-fill
// ink literal.
//
// A universal-component TYPE declares which families its colour slot resolves
// (the slot rule = a subscription: {axis:'color', groups:[…]}). A glyphic mark
// subscribes to brand/semantic/communication; a SURFACE subscribes to zoning.
// Same axis, different declared subscription per type — the value-side twin of a
// socket's `accepts`.
//
// Load after axes/axis-core.js.
// ============================================================================
(function () {
  'use strict';
  if (!window.CV_AXES) { console.error('color-axis.js: CV_AXIS core must load first'); return; }

  var color = window.CV_AXES.make({
    id: 'color',
    label: 'Colour',
    description: 'Grouped, typed, self-describing view over the colour token graph. Each value → a role token (var(--…)). MEANING of a value is contextual — see CV_MEANING; the axis carries family, pairing, role and theme-behaviour, not meaning.',

    // ---- FAMILIES (groups) — self-describing + relational --------------------
    groups: [
      { id: 'brand', label: 'Brand', voice: true, roles: ['fill', 'line', 'text'], pairsOn: 'ink',
        role: 'The identity voice — gold + bronze/tan. The signature; used for emphasis, not for default surfaces.' },
      { id: 'semantic', label: 'Semantic / status', voice: false, roles: ['fill', 'line', 'text'], pairsOn: 'paper',
        meta: { themeInvariant: true },
        role: 'STATE, never decoration — success / warning / error / info / pending. Fixed meaning, so theme-invariant.' },
      { id: 'ink', label: 'Ink / text', voice: false, roles: ['text', 'line'], pairsOn: 'paper',
        role: 'Foreground / text. Never a fill. Flips with theme (light↔dark).' },
      { id: 'communication', label: 'Communication', voice: true, roles: ['fill', 'line', 'text'], pairsOn: 'paper',
        meta: { themeInvariant: true },
        role: 'The relationship / flow voice (sage). A second voice beside gold — relationship lines, positive value-flow, sustainability. Never structural.' },
      { id: 'neutral', label: 'Neutral / surface', voice: false, roles: ['fill'], pairsOn: 'ink',
        role: 'Surfaces and grounds — paper / surface. The quiet backgrounds content sits on.' },
      { id: 'zoning', label: 'Zoning (surfaces)', voice: false, roles: ['fill'], pairsOn: null,
        role: 'Tonal-zone washes for SURFACES (not marks) — felt, not seen. Each value is a zone wash mixed from a pigment toward the ground; its legible ink is the zone’s own ink token. Belongs to surface/container component types, never to a glyphic.' },
    ],

    // ---- VALUES — token = single source of the literal; the rest is self-desc -
    values: [
      // brand
      { id: 'gold',      label: 'Gold',        group: 'brand', token: 'accent-gold',      on: 'ink',  themeInvariant: true,  roles: ['fill', 'line', 'text'] },
      { id: 'gold-deep', label: 'Gold deep',   group: 'brand', token: 'accent-gold-deep', on: 'paper', themeInvariant: true, roles: ['text', 'line'] },
      { id: 'gold-soft', label: 'Gold soft',   group: 'brand', token: 'accent-gold-soft', on: 'ink',  roles: ['fill'] },
      { id: 'bronze',    label: 'Bronze',      group: 'brand', token: 'accent-bronze',    on: 'paper', roles: ['line', 'text', 'fill'] },
      { id: 'bronze-2',  label: 'Bronze deep', group: 'brand', token: 'accent-bronze-2',  on: 'paper', roles: ['text', 'line'] },
      { id: 'tan',       label: 'Tan',         group: 'brand', token: 'accent-tan',       on: 'ink',  roles: ['fill', 'line'] },
      // semantic status (theme-invariant from the family; paper ink on a solid fill)
      { id: 'success',   label: 'Success',     group: 'semantic', token: 'status-success' },
      { id: 'warning',   label: 'Warning',     group: 'semantic', token: 'status-warning' },
      { id: 'error',     label: 'Error',       group: 'semantic', token: 'status-error' },
      { id: 'info',      label: 'Info',        group: 'semantic', token: 'status-info' },
      { id: 'pending',   label: 'Pending',     group: 'semantic', token: 'status-pending', on: 'ink' },
      // ink (flips with theme — from family)
      { id: 'ink',       label: 'Ink',         group: 'ink', token: 'fg-primary',   themeInvariant: false },
      { id: 'ink-2',     label: 'Ink 2',       group: 'ink', token: 'fg-secondary' },
      { id: 'muted',     label: 'Muted',       group: 'ink', token: 'fg-muted' },
      { id: 'soft',      label: 'Soft',        group: 'ink', token: 'fg-soft' },
      // communication
      { id: 'sage',      label: 'Sage',        group: 'communication', token: 'accent-communication',      on: 'paper', themeInvariant: true, roles: ['fill', 'line', 'text'] },
      { id: 'sage-soft', label: 'Sage soft',   group: 'communication', token: 'accent-communication-soft', on: 'ink',  roles: ['fill'] },
      // neutral / surface
      { id: 'paper',     label: 'Paper',       group: 'neutral', token: 'paper',      on: 'ink', roles: ['fill'] },
      { id: 'surface',   label: 'Surface',     group: 'neutral', token: 'bg-surface', on: 'ink', roles: ['fill'] },
    ],
    default: 'bronze',
  });

  // ZONING family values — the tonal-zone washes (colors_and_type.css). Each value's
  // `token` is the surface wash (what you paint a panel); `meta` carries the zone's
  // other role-tokens (strong/edge/ink/pigment), all single-sourced in CSS. The
  // legible foreground is the zone's own ink (resolved by pairCSS via meta.ink) — a
  // zone pairs on ITSELF, not on a global ink. These exist so the axis can OFFER a
  // zone (projection/AI), and so a surface-type slot can subscribe to `zoning`.
  [
    ['zone-base',    'Base',    'base'],
    ['zone-content', 'Content', 'content'],
    ['zone-panel',   'Panel',   'panel'],
    ['zone-review',  'Review',  'review'],
    ['zone-source',  'Source',  'source'],
    ['zone-package', 'Package', 'package'],
    ['zone-success', 'Ready',   'success'],
    ['zone-warning', 'Incomplete', 'warning'],
    ['zone-reject',  'Rejected', 'reject'],
  ].forEach(function (z) {
    var id = z[0], label = z[1], x = z[2];
    color.register({
      id: id, label: label, group: 'zoning', token: 'zone-' + x + '-surface', roles: ['fill'],
      meta: { strong: 'zone-' + x + '-strong', edge: 'zone-' + x + '-edge', ink: 'zone-' + x + '-ink', pigment: 'pig-' + x },
    });
  });

  // ALIASES — legacy short names still used across cards. They RESOLVE (loud-fail
  // safe) but mark themselves as synonyms of the canonical id, so a picker can show
  // "amber (= warning)" and CV_AXES.canonical('amber') → 'warning'. Same token, no
  // second home for the value.
  color.register({ id: 'amber', label: 'Amber', group: 'semantic', token: 'status-warning', alias: 'warning' });
  color.register({ id: 'clay',  label: 'Clay',  group: 'semantic', token: 'status-error',   alias: 'error' });
  color.register({ id: 'blue',  label: 'Blue',  group: 'semantic', token: 'status-info',    alias: 'info' });

  window.CV_AXES.register(color);
})();
