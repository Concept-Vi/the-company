// app/registry/text-type.js
// ============================================================================
// Registers TEXT into CV_REGISTRY — the typed-text primitive that lives inside
// block sockets ("other typed things like all text"). A text node is a LEAF
// occupant: a role on the type ladder + a string written to that role's LENGTH
// BUDGET (tokens/text.css — the typed-text doctrine: truncation is not design;
// the copy.budgets behaviour in CV_AI enforces the budget at authoring time).
//
// SINGLE SOURCE: the roles + budgets live in tokens/text.css (--len-*) and the
// type ladder (--fs-*); this file declares the TYPE + the solver that maps a
// role to its consuming class (.t-<role>). No literal leaves the token files.
//
// Load after types-core.js (+ axes); before/after cv-node.js (solver is
// registered load-order-tolerantly, like block-type.js).
// ============================================================================
(function () {
  'use strict';
  var R = window.CV_REGISTRY;
  if (!R) { console.error('text-type.js: CV_REGISTRY must load first'); return; }

  var ROLES = ['micro', 'label', 'title', 'desc', 'body', 'src'];

  R.register({
    id: 'text', name: 'Text', kind: 'text', layer: 'atom',
    family: 'text', classification: ['text', 'atom'],
    description: 'The typed-text primitive. A role on the type ladder + a string written to that role\u2019s length budget (tokens/text.css). Fills any content socket that accepts \u2018text\u2019.',
    icon: 'edit', provenance: 'built-in',
    valueSlots: {
      role:  { axis: null, values: ROLES, default: 'body',
               means: 'type-ladder role \u2014 sets size, voice, and the LENGTH BUDGET (--len-<role>)' },
      color: { axis: 'color', groups: ['ink', 'brand', 'semantic'], optional: true, default: null,
               means: 'ink override; defaults to the role\u2019s own ink' },
    },
    conditions: ['value fits the role\u2019s length budget (copy.budgets, CV_AI)'],
    tags: ['text', 'typography', 'primitive'],
  }, { silent: true });

  // ---- the text solver: role → consuming class (tokens/text.css §ROLES) ----
  function textSolver(ir, ctx) {
    var spec = (ctx && ctx.spec) || (ir.payload && ir.payload.id === undefined ? ir.payload : {}) || {};
    var role = spec.role || 'body';
    if (ROLES.indexOf(role) < 0) throw new Error('text solver: unknown role "' + role + '" (have: ' + ROLES.join(', ') + ')');
    var out = { tag: role === 'title' ? 'h3' : 'span', classes: ['t-' + role], style: {}, text: spec.value != null ? String(spec.value) : '' };
    if (spec.color && window.CV_AXES && window.CV_AXES.has('color')) {
      var css = window.CV_AXES.css('color', spec.color);
      if (css) out.style.color = css;
    }
    return out;
  }
  function ensureSolver() {
    // check the kind-specific slot directly — hasSolver() also matches the '*'
    // fallback, which would silently skip this registration.
    if (window.CV_NODE && !window.CV_NODE._solvers.text) window.CV_NODE.solver('text', textSolver);
    return !!window.CV_NODE;
  }
  if (!ensureSolver() && typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', ensureSolver);
  }

  R.text = { type: function () { return R.resolve('text'); }, roles: ROLES.slice(), ensureSolver: ensureSolver };
})();
