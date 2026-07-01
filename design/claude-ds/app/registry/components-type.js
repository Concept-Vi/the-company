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
  ];

  // attach the shared runtime pointer + provenance, then register.
  R.registerMany(defs.map(function (d) {
    return Object.assign({ provenance: 'built-in', runtime: { kind: 'react-component', global: NS + '.' + d.name } }, d);
  }), { silent: true });
})();
