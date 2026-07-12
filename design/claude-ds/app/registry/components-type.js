// app/registry/components-type.js
// ============================================================================
// TOTAL COMPONENT COVERAGE — registers every React UI component (components/*.jsx)
// into CV_REGISTRY as a universal-component Type, the same grammar as the Glyphic.
//
// "Everything on an interface is a templated dynamic component … and they're all
// in registries" (Info). Each component declares: its CLASSIFICATION (what
// sockets elsewhere accept it as), its value-SLOTS (props — subscribing to an
// AXIS where the prop is an axis value, e.g. size→size axis), its SOCKETS (where
// it accepts other components — children/title/footer/items), and CONDITIONS.
// Vocabularies are never copied: enum props list their values inline (the
// component's own contract), axis-backed props point at the axis.
//
// Load after types-core.js (+ conditions, axes). Pure data; renders via the
// existing component bundle (runtime.kind 'react-component').
// ============================================================================
(function () {
  'use strict';
  var R = window.CV_REGISTRY;
  if (!R) { console.error('components-type.js: CV_REGISTRY must load first'); return; }

  // a value-slot from an enum prop (the component's own contract is the source)
  function en(values, def, means) { return { kind: 'enum', values: values, default: def, means: means || '' }; }
  // a value-slot that subscribes to an AXIS (axis is the single source)
  function ax(axis, extra) { return Object.assign({ axis: axis }, extra || {}); }
  // a boolean modifier slot
  function bool(def, means) { return { kind: 'boolean', default: !!def, means: means || '' }; }
  // a content socket (accepts text/components as children/region)
  function content(label, opts) { return Object.assign({ label: label, accepts: ['glyphic', 'atom', 'block', 'text'], optional: true }, opts || {}); }

  var NS = 'ConceptVDesignSystem_c8f43c'; // window namespace the bundle exposes

  var defs = [
    {
      id: 'component.button', name: 'Button', kind: 'button', layer: 'atom', family: 'control',
      classification: ['control', 'action', 'atom'], icon: 'tag',
      description: 'Action button. Variant = voice (gold decision / ink / outline / ghost / soft / sage). Can host an icon + label.',
      valueSlots: {
        variant: en(['primary', 'ink', 'outline', 'ghost', 'soft', 'comm', 'default'], 'primary', 'emphasis / voice'),
        size:    en(['sm', 'lg'], null, 'control height'),
        pill:    bool(false), block: bool(false), icon: bool(false),
      },
      sockets: { label: content('Label'), leadingIcon: { label: 'Leading icon', accepts: ['glyphic', 'symbol'], optional: true, onPick: 'insert' } },
      tags: ['component', 'control', 'cta'],
    },
    {
      id: 'component.badge', name: 'Badge', kind: 'badge', layer: 'atom', family: 'status',
      classification: ['status', 'atom', 'mark'], icon: 'tag',
      description: 'Status label. Tone maps to a system voice/state; optional leading status dot.',
      valueSlots: { tone: en(['gold', 'success', 'warning', 'error', 'comm'], null, 'voice / state'), dot: bool(false, 'leading status dot') },
      sockets: { label: content('Label') },
      tags: ['component', 'status'],
    },
    {
      id: 'component.avatar', name: 'Avatar', kind: 'avatar', layer: 'atom', family: 'media',
      classification: ['media', 'atom'], icon: 'browser-house',
      description: 'Circular avatar — photo (src) or initials. gold = filled variant.',
      valueSlots: { size: ax('size', { default: 'md', means: 'diameter' }), gold: bool(false) },
      sockets: { fallback: { label: 'Initials / glyph', accepts: ['glyphic', 'symbol', 'text'], optional: true } },
      tags: ['component', 'media'],
    },
    {
      id: 'component.card', name: 'Card', kind: 'card', layer: 'block', family: 'surface',
      classification: ['surface', 'block', 'container'], icon: 'browser',
      description: 'Surface card. Variant = paper role; raised/interactive/pad modifiers; optional header + footer.',
      valueSlots: {
        variant: en(['soft', 'surface', 'outline', 'gold'], 'soft', 'surface role'),
        raised:  bool(false), interactive: bool(false),
        pad:     en(['sm', 'lg'], null, 'inner padding'),
        depth:   ax('depth', { default: 'normal', means: 'elevation' }),
      },
      sockets: {
        title:  content('Title', { accepts: ['text', 'glyphic'] }),
        body:   content('Body', { accepts: ['glyphic', 'atom', 'block', 'text'], multiple: true }),
        footer: content('Footer'),
      },
      tags: ['component', 'surface', 'container'],
    },
    {
      id: 'component.input', name: 'Input', kind: 'input', layer: 'atom', family: 'control',
      classification: ['control', 'atom', 'form'], icon: 'edit',
      description: 'Form field — input / textarea / select, with optional label / hint / error.',
      valueSlots: { as: en(['input', 'textarea', 'select'], 'input', 'control element') },
      sockets: { label: content('Label', { accepts: ['text'] }), hint: content('Hint', { accepts: ['text'] }), error: content('Error', { accepts: ['text'] }) },
      conditions: [], tags: ['component', 'control', 'form'],
    },
    {
      id: 'component.switch', name: 'Switch', kind: 'switch', layer: 'atom', family: 'control',
      classification: ['control', 'atom', 'form'], icon: 'check-square',
      description: 'On/off switch — track turns gold (active voice) when checked.',
      valueSlots: { checked: bool(false, 'on/off') },
      tags: ['component', 'control', 'form'],
    },
    {
      id: 'component.tabs', name: 'Tabs', kind: 'tabs', layer: 'block', family: 'nav',
      classification: ['nav', 'block'], icon: 'browser',
      description: 'Dashboard tab bar — active tab gets the gold underline.',
      valueSlots: {},
      sockets: { items: { label: 'Tabs', accepts: ['text', 'glyphic'], multiple: true, onPick: 'insert' } },
      tags: ['component', 'nav'],
    },
    {
      id: 'component.segmented', name: 'Segmented', kind: 'segmented', layer: 'block', family: 'control',
      classification: ['control', 'block'], icon: 'check-square',
      description: 'Segmented control (2–3 options) — active option lifts onto a surface.',
      valueSlots: {},
      sockets: { options: { label: 'Options', accepts: ['text'], multiple: true, conditions: ['options exists'] } },
      tags: ['component', 'control'],
    },
    {
      id: 'component.stepper', name: 'Stepper', kind: 'stepper', layer: 'block', family: 'nav',
      classification: ['nav', 'block', 'process'], icon: 'atom',
      description: 'Linear numbered stepper — done (gold ✓) / active / upcoming.',
      valueSlots: { active: { kind: 'int', default: 0, min: 0, means: 'current step index' } },
      sockets: { steps: { label: 'Steps', accepts: ['text', 'glyphic'], multiple: true } },
      tags: ['component', 'nav', 'process'],
    },
    {
      id: 'component.modal', name: 'Modal', kind: 'modal', layer: 'surface', family: 'overlay',
      classification: ['overlay', 'surface', 'container'], icon: 'browser',
      description: 'Modal dialog — warm-dim backdrop + raised panel. Opens via an event-socket (e.g. a Button onClick).',
      valueSlots: { open: bool(false, 'visibility') },
      sockets: {
        title:   content('Title', { accepts: ['text', 'glyphic'] }),
        body:    content('Body', { accepts: ['glyphic', 'atom', 'block', 'text'], multiple: true }),
        footer:  content('Footer'),
        // an EVENT-socket: what trigger opens this modal (slice B vocabulary)
        trigger: { label: 'Opened by', kind: 'event', event: 'click', accepts: ['control', 'action'], optional: true, onPick: 'open', address: 'component.modal' },
      },
      tags: ['component', 'overlay', 'container'],
    },
    // ---- the floating-layer trio (components landed Jul 9; they had no Type
    //      rows — registered here with the operator set so the catalogue is total)
    {
      id: 'component.popover', name: 'Popover', kind: 'popover', layer: 'surface', family: 'overlay',
      classification: ['overlay', 'surface', 'container'], icon: 'window',
      description: 'The shared anchored floating layer (window.CV_POPOVER) — flips/shifts to stay in view. Select, Tooltip and Menu all position through it; never a second positioning engine.',
      valueSlots: {
        placement: en(['top-start', 'top-center', 'top-end', 'bottom-start', 'bottom-center', 'bottom-end', 'left-start', 'left-center', 'left-end', 'right-start', 'right-center', 'right-end'], 'bottom-start', 'anchor side + alignment'),
        matchWidth: bool(false, 'min-width follows the anchor'),
        bare: bool(false, 'positioning only, no surface chrome'),
      },
      sockets: { body: content('Body', { multiple: true }) },
      tags: ['component', 'overlay'],
    },
    {
      id: 'component.select', name: 'Select', kind: 'select', layer: 'block', family: 'control',
      classification: ['control', 'block', 'form'], icon: 'sort',
      description: 'Trigger that reads like an Input, opening a listbox through the shared Popover engine.',
      valueSlots: {},
      sockets: { options: { label: 'Options', accepts: ['text'], multiple: true } },
      tags: ['component', 'control', 'form'],
    },
    {
      id: 'component.tooltip', name: 'Tooltip', kind: 'tooltip', layer: 'atom', family: 'overlay',
      classification: ['overlay', 'atom'], icon: 'info',
      description: 'Dark hint bubble on hover/focus — positioned through the shared Popover engine.',
      valueSlots: { placement: en(['top', 'bottom', 'left', 'right'], 'top', 'anchor side') },
      sockets: { label: content('Label', { accepts: ['text'] }), anchor: { label: 'Anchor', accepts: ['control', 'atom', 'glyphic'] } },
      tags: ['component', 'overlay'],
    },
    // ---- the operator set (U6) --------------------------------------------
    {
      id: 'component.toast', name: 'ToastHost', kind: 'toast', layer: 'surface', family: 'overlay',
      classification: ['overlay', 'surface', 'status'], icon: 'bell',
      description: 'Global notifier — a window-level queue (window.CV_TOAST.show) rendered by one ToastHost per page. Tones ride the Badge tone vocabulary; auto-dismiss + action slot; enter/exit via the motion primitives (reduced-motion respected).',
      valueSlots: {
        position: en(['top-right', 'top-center', 'top-left', 'bottom-right', 'bottom-center', 'bottom-left'], 'top-right', 'stack corner'),
        tone: en(['gold', 'success', 'warning', 'error', 'comm'], null, 'voice / state (per toast — the Badge vocabulary)'),
      },
      sockets: { action: { label: 'Action', accepts: ['control', 'action'], optional: true } },
      tags: ['component', 'overlay', 'status', 'notify'],
    },
    {
      id: 'component.sheet', name: 'Sheet', kind: 'sheet', layer: 'surface', family: 'overlay',
      classification: ['overlay', 'surface', 'container'], icon: 'sidebar-close',
      description: 'Slide-in panel — the mobile-first sibling of Modal (same overlay/esc/backdrop conventions; reuses the modal head/foot chrome). side=right drawer or bottom sheet with a touch-floor drag handle.',
      valueSlots: {
        open: bool(false, 'visibility'),
        side: en(['right', 'bottom'], 'bottom', 'entry edge'),
      },
      sockets: {
        title:  content('Title', { accepts: ['text', 'glyphic'] }),
        body:   content('Body', { multiple: true }),
        footer: content('Footer'),
        trigger: { label: 'Opened by', kind: 'event', event: 'click', accepts: ['control', 'action'], optional: true, onPick: 'open', address: 'component.sheet' },
      },
      tags: ['component', 'overlay', 'container'],
    },
    {
      id: 'component.list', name: 'List', kind: 'list', layer: 'block', family: 'collection',
      classification: ['collection', 'block', 'container'], icon: 'file-list',
      description: 'Rows — leading glyph/avatar slot, primary+secondary text on the typed-text length budgets (--len-title/--len-desc), trailing meta/action. Selection rides .interactive; row height rides --row-h (density-aware).',
      valueSlots: { divided: bool(true, 'hairline between rows') },
      sockets: {
        rows: { label: 'Rows', accepts: ['atom', 'block', 'text'], multiple: true },
        leading: { label: 'Leading (per row)', accepts: ['glyphic', 'symbol', 'atom'], optional: true },
        trailing: { label: 'Trailing (per row)', accepts: ['atom', 'control', 'text'], optional: true },
      },
      tags: ['component', 'collection'],
    },
    {
      id: 'component.menu', name: 'Menu', kind: 'menu', layer: 'block', family: 'overlay',
      classification: ['overlay', 'block', 'nav'], icon: 'checklist-double',
      description: 'Action menu riding the shared Popover engine — items with icon+label+danger tone, separators, disabled; keyboard navigable (arrows/enter/esc); role=menu.',
      valueSlots: {
        placement: en(['bottom-start', 'bottom-end', 'top-start', 'top-end'], 'bottom-start', 'anchor side + alignment'),
      },
      sockets: {
        trigger: { label: 'Trigger', accepts: ['control', 'action'] },
        items: { label: 'Items', accepts: ['text', 'action'], multiple: true },
      },
      tags: ['component', 'overlay', 'nav', 'action'],
    },
    {
      id: 'component.checkbox', name: 'Checkbox', kind: 'checkbox', layer: 'atom', family: 'control',
      classification: ['control', 'atom', 'form'], icon: 'check-square',
      description: 'Token-styled checkbox — gold checked state (gold = selection/decision). Label+hint ride the same .cv-field stack as Input.',
      valueSlots: { checked: bool(false, 'on/off'), indeterminate: bool(false, 'dash state') },
      sockets: { label: content('Label', { accepts: ['text'] }), hint: content('Hint', { accepts: ['text'] }) },
      tags: ['component', 'control', 'form'],
    },
    {
      id: 'component.radio', name: 'Radio', kind: 'radio', layer: 'atom', family: 'control',
      classification: ['control', 'atom', 'form'], icon: 'check',
      description: 'Token-styled radio — gold checked state (gold = selection/decision). Label+hint ride the same .cv-field stack as Input.',
      valueSlots: { checked: bool(false, 'selected') },
      sockets: { label: content('Label', { accepts: ['text'] }), hint: content('Hint', { accepts: ['text'] }) },
      tags: ['component', 'control', 'form'],
    },
    {
      id: 'component.appshell', name: 'AppShell', kind: 'appshell', layer: 'surface', family: 'chrome',
      classification: ['chrome', 'surface', 'container', 'nav'], icon: 'devices',
      description: 'The console chrome — desktop nav rail that becomes a bottom tab bar on mobile, riding tokens/device.css appbar/tabbar chrome and the data-surface/breakpoint machinery. Slots: header, nav items (icon+label), content.',
      valueSlots: {},
      sockets: {
        header: content('Header'),
        nav: { label: 'Nav items', accepts: ['text', 'action'], multiple: true },
        body: { label: 'Content', accepts: ['glyphic', 'atom', 'block', 'text'], multiple: true },
      },
      tags: ['component', 'chrome', 'nav', 'container'],
    },
    {
      id: 'component.table', name: 'Table', kind: 'table', layer: 'block', family: 'collection',
      classification: ['collection', 'block', 'data'], icon: 'dashboard',
      description: 'React wrapper over the CSS-only .cv-table (comparison/pricing). Columns declare num (tabular numerals) and feature (the gold offer column); striped variant.',
      valueSlots: { striped: bool(false, 'zebra rows') },
      sockets: {
        columns: { label: 'Columns', accepts: ['text'], multiple: true },
        rows: { label: 'Rows', accepts: ['text', 'atom'], multiple: true },
      },
      tags: ['component', 'collection', 'data'],
    },
    {
      id: 'component.search', name: 'Search', kind: 'search', layer: 'atom', family: 'control',
      classification: ['control', 'atom', 'form'], icon: 'search',
      description: 'React wrapper over the CSS-only .cv-search pill — leading icon + input, gold focus-within ring, optional trailing slot.',
      valueSlots: {},
      sockets: {
        icon: { label: 'Leading icon', accepts: ['glyphic', 'symbol'], optional: true },
        trailing: { label: 'Trailing', accepts: ['text', 'atom', 'control'], optional: true },
      },
      tags: ['component', 'control', 'form'],
    },
    {
      id: 'component.skeleton', name: 'Skeleton', kind: 'skeleton', layer: 'atom', family: 'status',
      classification: ['status', 'atom'], icon: 'frame',
      description: 'React wrapper over the CSS-only .skeleton shimmer placeholder (tokens/states.css) — content resolves, never pops. Reduced-motion gated in the token home.',
      valueSlots: { variant: en(['text', 'line', 'circle', 'block'], 'line', 'placeholder shape') },
      tags: ['component', 'status', 'loading'],
    },
  ];

  // attach the shared runtime pointer + provenance, then register.
  R.registerMany(defs.map(function (d) {
    return Object.assign({ provenance: 'built-in', runtime: { kind: 'react-component', global: NS + '.' + d.name } }, d);
  }), { silent: true });
})();
