// app/registry/kinds-type.js
// ============================================================================
// OTHER UNIVERSAL-COMPONENT KINDS — declared as Types so the grammar covers the
// whole interface, not just the Glyphic. Info named four kinds: glyphic (done),
// a "compositional template menu panel", a "graph generator system", and a
// "slide system". Graph + slide already exist as engines (core/DiagramSolver,
// core/Slide + the deck-slide surface Types); this file ADDS the missing
// composition-menu panel and registers thin Type declarations that POINT at the
// existing graph/slide engines, so every kind is reachable through one registry
// with parts/slots/sockets — the proof that the grammar is universal.
//
// The headline demonstration: composition-menu declares a socket that ACCEPTS
// the 'glyphic' classification. Because acceptance is declarative, the system
// already knows a glyphic can fill it (CV_REGISTRY.candidatesForSocket) — no
// bespoke wiring, exactly as Info described.
//
// Load after types-core.js + glyphic-type.js + components-type.js.
// ============================================================================
(function () {
  'use strict';
  var R = window.CV_REGISTRY;
  if (!R) { console.error('kinds-type.js: CV_REGISTRY must load first'); return; }

  var defs = [
    {
      id: 'panel.composition-menu', name: 'Composition menu', kind: 'panel', layer: 'surface', family: 'panel',
      classification: ['panel', 'surface', 'container'], icon: 'browser',
      description: 'A compositional template menu panel — a palette of things you can place. Declares a socket that accepts a classification; the system shows the matching library automatically (candidatesForSocket), no per-panel code.',
      valueSlots: {
        title:  { kind: 'text', default: 'Insert', means: 'panel heading' },
        layout: { kind: 'enum', values: ['grid', 'list', 'reel'], default: 'grid', means: 'how items lay out' },
        density: { axis: 'space', groups: ['inner'], default: 's2', means: 'gap between items' },
        // PER-TYPE COLOUR SUBSCRIPTION: a panel is a SURFACE, so its colour slot
        // resolves the `zoning` family of the colour axis (the tonal-zone washes)
        // — NOT brand/semantic, which is what a glyphic mark subscribes to. Same
        // axis, different declared families per component type (the slot rule).
        surface: { axis: 'color', groups: ['zoning'], default: 'zone-panel', means: 'the tonal zone this panel sits in (surface wash)' },
      },
      sockets: {
        // THE demonstration: a socket accepting glyphics. candidatesForSocket
        // resolves the glyphic library with zero bespoke wiring.
        items: { label: 'Items', accepts: ['glyphic', 'atom', 'control'], multiple: true, onPick: 'insert',
                 means: 'anything classified glyphic/atom/control can be placed here' },
        // an event-socket: clicking an item triggers an action at an address
        onItemClick: { label: 'On item click', kind: 'event', event: 'click', accepts: ['action', 'panel', 'surface'], optional: true, onPick: 'open' },
      },
      conditions: [],
      tags: ['kind', 'panel', 'menu', 'universal-component'],
    },
    {
      id: 'kind.graph', name: 'Graph generator', kind: 'graph', layer: 'system', family: 'graph',
      classification: ['graph', 'system'], icon: 'atom',
      description: 'Typed nodes placed by relationship — the graph/diagram engine (core/DiagramSolver). A node is a Glyphic; an edge carries a relationship type. Declared here so the kind is registry-reachable.',
      valueSlots: {
        layout: { kind: 'enum', values: ['force', 'tree', 'radial', 'flow', 'grid'], default: 'flow', means: 'placement strategy' },
      },
      sockets: {
        nodes: { label: 'Nodes', accepts: ['glyphic', 'atom', 'block'], multiple: true, means: 'each node is a universal component (typically a Glyphic)' },
        edges: { label: 'Edges', accepts: ['relationship'], multiple: true, optional: true },
      },
      runtime: { kind: 'engine', key: 'DiagramSolver' },
      tags: ['kind', 'graph', 'universal-component'],
    },
    {
      id: 'kind.slide-system', name: 'Slide system', kind: 'slide', layer: 'doc', family: 'deck',
      classification: ['slide', 'doc', 'container'], icon: 'browser',
      description: 'A slide/deck is content-as-data rendered by the block solver (core/Slide + deck-slide surface Types). Declared here as the slide KIND; the actual archetypes are the deck-slide surfaces.',
      valueSlots: {
        archetype: { kind: 'ref', from: "CV_REGISTRY.query({family:'deck-slide'})", means: 'which slide archetype' },
        theme: { kind: 'enum', values: ['editorial', 'dim', 'dark', 'contrast'], default: 'editorial' },
      },
      sockets: {
        slides: { label: 'Slides', accepts: ['slide', 'surface'], multiple: true },
      },
      runtime: { kind: 'engine', key: 'Slide' },
      tags: ['kind', 'slide', 'deck', 'universal-component'],
    },
    {
      id: 'kind.selection', name: 'Selection', kind: 'selection', layer: 'system', family: 'interaction',
      classification: ['selection', 'container'], icon: 'cursor',
      description: 'A selection is itself a NODE (Root Unity: everything is the one unit) whose members are the selected nodes. Actions apply to a selection uniformly — set-value on a selection sets it on every member; it has a socket that holds its members.',
      valueSlots: {
        mode: { kind: 'enum', values: ['single', 'multi'], default: 'single', means: 'how many members' },
      },
      sockets: {
        members: { label: 'Members', accepts: ['*'], multiple: true, means: 'the selected nodes (by address)' },
      },
      tags: ['kind', 'selection', 'interaction', 'universal-component'],
    },
  ];

  R.registerMany(defs.map(function (d) { return Object.assign({ provenance: 'built-in' }, d); }), { silent: true });
})();
