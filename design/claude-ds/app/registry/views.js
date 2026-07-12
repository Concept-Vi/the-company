// app/registry/views.js
// ============================================================================
// VIEWS — generation-from-data for the interface. A VIEW is a node (kind 'view')
// whose spec is { query, project?, onPick?, pickArgs? }. CV_PROJECT.toCollection
// runs the query (CV_QUERY / an axis) and projects each result into a UI row, so
// EVERY collection-UI — a library, a palette, a menu, a gallery — is generated
// from data, live, with no per-surface code. Register a Type / axis value /
// action / decorator and it appears in the relevant view automatically; that is
// "the interface is a projection of the registries" made literal and dynamic.
//
// Views are themselves nodes in CV_REGISTRY (kind 'view') — so there is a view
// OF views, and a view can be generated/projected like anything else (Root Unity:
// everything is the one unit). A view with onPick wires the row back to an action
// (assemble-from-library = click a palette item → CV_ACTIONS.invoke).
//
// Load after types-core.js (+ the registries the queries read). Lazy/tolerant.
// ============================================================================
(function () {
  'use strict';
  var R = window.CV_REGISTRY;
  if (!R) { console.error('views.js: CV_REGISTRY must load first'); return; }

  var views = [
    {
      id: 'view.library', name: 'Library — composable kinds', kind: 'view', layer: 'surface',
      classification: ['view'], icon: 'browser', provenance: 'built-in',
      description: 'Every composable Type at atom/block layer — the palette of things you can place.',
      spec: { query: { from: 'types', where: { layer: { in: ['atom', 'block'] } } }, project: { label: 'name', sub: 'kind' } },
    },
    {
      id: 'view.palette-form', name: 'Palette — Form', kind: 'view', layer: 'surface',
      classification: ['view'], icon: 'hexagon', provenance: 'built-in',
      description: 'Every value of the Form axis, as a clickable palette that sets a glyphic\u2019s form.',
      spec: { query: { axis: 'form' }, onPick: 'set-value', pickArgs: { slot: 'form', value: '{{ item.id }}' } },
    },
    {
      id: 'view.palette-symbol', name: 'Palette — Symbol', kind: 'view', layer: 'surface',
      classification: ['view'], icon: 'star', provenance: 'built-in',
      description: 'Every value of the Symbol axis (the icon library), as a palette that sets the symbol.',
      spec: { query: { axis: 'symbol' }, onPick: 'set-value', pickArgs: { slot: 'symbol', value: '{{ item.id }}' } },
    },
    {
      id: 'view.palette-color', name: 'Palette — Colour', kind: 'view', layer: 'surface',
      classification: ['view'], icon: 'square', provenance: 'built-in',
      description: 'Every value of the Colour axis (the colour tokens), as a swatch palette.',
      spec: { query: { axis: 'color' }, onPick: 'set-value', pickArgs: { slot: 'color', value: '{{ item.id }}' } },
    },
    {
      id: 'view.actions', name: 'Actions', kind: 'view', layer: 'surface',
      classification: ['view'], icon: 'play', provenance: 'built-in',
      description: 'Every verb the system can do — the actions registry, projected.',
      spec: { query: { from: 'actions' }, project: { label: 'verb', sub: 'actionType' } },
    },
    {
      id: 'view.decorators', name: 'Decorators', kind: 'view', layer: 'surface',
      classification: ['view'], icon: 'tag', provenance: 'built-in',
      description: 'The @decorator vocabulary, projected.',
      spec: { query: { from: 'decorators' }, project: { label: 'label', sub: 'group' } },
    },
    {
      id: 'view.views', name: 'Views (of views)', kind: 'view', layer: 'surface',
      classification: ['view'], icon: 'browser', provenance: 'built-in',
      description: 'Every view — a view of views. Generation-from-data all the way down.',
      spec: { query: { from: 'types', where: { kind: 'view' } }, project: { label: 'name', sub: 'id' } },
    },
  ];

  R.registerMany(views.map(function (v) { return Object.assign({ provenance: 'built-in' }, v); }), { silent: true });

  // convenience accessor (a view of views, computed)
  R.views = function () { return R.query({ family: undefined }).filter(function (t) { return t.kind === 'view'; }); };
})();
