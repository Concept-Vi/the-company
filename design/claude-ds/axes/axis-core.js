// axes/axis-core.js
// ============================================================================
// CV_AXIS / CV_AXES — the universal AXIS foundation.
//
// Every primary axis of the design language (Motion, Colour, Space, Size, Form,
// Texture, Depth, Fill, Symbol, Meaning, …) is its own dedicated, hierarchical,
// typed system with the SAME shape. Everything visual RESOLVES its value of an
// axis FROM that axis — no consumer owns or hardcodes a value table.
//
// TOKENS ARE THE VALUE-UNITS OF AN AXIS. An axis does NOT replace or wrap "over"
// the tokens — the colour axis IS the colour tokens, typed and organised; the
// size axis IS the --size-* tokens; and so on. A value carries `token` as its
// CANONICAL identity wherever a token home exists; resolveCSS() returns
// var(--token). A component's slot declares a token (via an axis value), and the
// axis is simply the typed dimension those token-units sit on. Tokens stay the
// single source of the literal; the axis adds the type/grouping/meaning around
// them. (Clarified by Info, slice 60.)
//
// This mirrors the other registries (CV_REGISTRY / CV_AI / CV_MEANING): the same
// register / resolve / list / query / subscribe verbs, plus a value hierarchy
// (group → value) and a resolveCSS() that turns a value into the token/CSS it
// references (never a copied literal — the value points at its single source).
//
// A SUBSCRIPTION is what a component slot declares to consume an axis:
//   { axis, groups?:[...], values?:[...], default, conditions? }
// candidates(sub) → the allowed value ids; that is exactly what an editor or the
// foundry shows for that slot. No bespoke per-slot code.
//
// Load FIRST among axes (before any axes/<name>/*). No dependencies.
// ============================================================================
(function () {
  'use strict';

  function fail(msg) { throw new Error('CV_AXIS: ' + msg); }

  // ---- one Axis instance -------------------------------------------------
  // spec: { id, label, description?, groups?:[{id,label,parent?,description?}],
  //         values:[{ id, label?, group?, css?|token?|resolve?, meta?, zero? }],
  //         default? }
  // A value's payload is resolved lazily by resolveCSS(): `token` → var(--token),
  // `css` → literal CSS string (only for things with no token home, e.g. a
  // keyframe name), `resolve` → fn(value, ctx) for computed payloads.
  function makeAxis(spec) {
    if (!spec || !spec.id) fail('axis needs an id');
    var byId = {};
    var order = [];
    var groups = {};
    var groupOrder = [];

    (spec.groups || []).forEach(function (g) {
      groups[g.id] = { id: g.id, label: g.label || g.id, parent: g.parent || null, description: g.description || '' };
      groupOrder.push(g.id);
    });

    function addValue(v) {
      if (!v || !v.id) fail('value in axis "' + spec.id + '" needs an id');
      if (v.group && !groups[v.group]) {
        // tolerate implicit groups (declared on the value)
        groups[v.group] = { id: v.group, label: v.group, parent: null, description: '' };
        groupOrder.push(v.group);
      }
      if (!byId[v.id]) order.push(v.id);
      byId[v.id] = {
        id: v.id, label: v.label || v.id, group: v.group || null,
        token: v.token || null, css: v.css || null, resolve: v.resolve || null,
        zero: !!v.zero, meta: v.meta || {},
      };
      return byId[v.id];
    }
    (spec.values || []).forEach(addValue);

    var defId = spec.default || (order[0] || null);

    var axis = {
      id: spec.id,
      label: spec.label || spec.id,
      description: spec.description || '',
      meta: spec.meta || {},

      // --- the shared verbs ---
      register: function (v) { return addValue(v); },                 // add/override a value
      registerGroup: function (g) { groups[g.id] = { id: g.id, label: g.label || g.id, parent: g.parent || null, description: g.description || '' }; if (groupOrder.indexOf(g.id) < 0) groupOrder.push(g.id); return groups[g.id]; },
      has: function (id) { return !!byId[id]; },
      resolve: function (id) { var v = byId[id]; if (!v) fail('axis "' + spec.id + '" has no value "' + id + '" (have: ' + order.join(', ') + ')'); return v; },
      tryResolve: function (id) { return byId[id] || null; },
      values: function () { return order.map(function (id) { return byId[id]; }); },
      ids: function () { return order.slice(); },
      groups: function () { return groupOrder.map(function (id) { return groups[id]; }); },
      group: function (id) { return groups[id] || null; },
      valuesIn: function (groupId) { return order.map(function (i) { return byId[i]; }).filter(function (v) { return v.group === groupId; }); },
      default: function () { return defId; },
      setDefault: function (id) { this.resolve(id); defId = id; return id; },
      zero: function () { var z = order.map(function (i) { return byId[i]; }).filter(function (v) { return v.zero; }); return z.length ? z[0].id : null; },

      // query by group/meta predicate
      query: function (pred) { return this.values().filter(pred); },

      // resolve a value id → its CSS payload (token var / literal / computed).
      // ctx is passed to resolve() fns. Returns null for a value with no payload
      // (e.g. a pure-semantic 'none').
      resolveCSS: function (id, ctx) {
        var v = this.resolve(id);
        if (v.resolve) return v.resolve(v, ctx || {});
        if (v.token) return 'var(--' + v.token + ')';
        if (v.css) return v.css;
        return null;
      },

      // --- subscription helpers ---
      // candidates allowed by a subscription against THIS axis.
      candidates: function (sub) {
        sub = sub || {};
        var out = this.values();
        if (sub.groups && sub.groups.length) out = out.filter(function (v) { return sub.groups.indexOf(v.group) >= 0; });
        if (sub.values && sub.values.length) out = out.filter(function (v) { return sub.values.indexOf(v.id) >= 0; });
        return out;
      },

      // --- change notification (mirrors registry subscribe) ---
      _subs: [],
      subscribe: function (fn) { var s = this._subs; s.push(fn); return function () { var i = s.indexOf(fn); if (i >= 0) s.splice(i, 1); }; },
      _emit: function (ev) { this._subs.slice().forEach(function (fn) { try { fn(ev); } catch (e) {} }); },
    };

    // re-wrap register/setDefault to emit
    var _reg = axis.register, _sd = axis.setDefault;
    axis.register = function (v) { var r = _reg(v); this._emit({ type: 'register', value: r }); return r; };
    axis.setDefault = function (id) { var r = _sd.call(this, id); this._emit({ type: 'default', id: r }); return r; };

    return axis;
  }

  // ---- the registry of axes (axes are themselves enumerable/typed) -------
  var axes = {};
  var CV_AXES = {
    make: makeAxis,
    register: function (spec) {
      var ax = (spec && spec.id && spec.resolveCSS) ? spec : makeAxis(spec); // accept a built axis or a spec
      axes[ax.id] = ax;
      return ax;
    },
    resolve: function (id) { var a = axes[id]; if (!a) fail('no axis "' + id + '" (have: ' + Object.keys(axes).join(', ') + ')'); return a; },
    tryResolve: function (id) { return axes[id] || null; },
    has: function (id) { return !!axes[id]; },
    list: function () { return Object.keys(axes).map(function (k) { return { id: k, label: axes[k].label }; }); },
    all: function () { return Object.keys(axes).map(function (k) { return axes[k]; }); },

    // resolve a {axis,value} pair → CSS, from anywhere. The universal entry point.
    css: function (axisId, valueId, ctx) { return this.resolve(axisId).resolveCSS(valueId, ctx); },

    // candidates for a subscription { axis, groups?, values? } — what an editor shows.
    candidates: function (sub) { if (!sub || !sub.axis) fail('subscription needs an axis'); return this.resolve(sub.axis).candidates(sub); },

    // validate a chosen value against a subscription (loud-list, never coerce).
    validate: function (sub, valueId) {
      var ax = this.resolve(sub.axis);
      if (!ax.has(valueId)) return ['axis "' + sub.axis + '" has no value "' + valueId + '"'];
      var ok = ax.candidates(sub).some(function (v) { return v.id === valueId; });
      return ok ? [] : ['"' + valueId + '" not permitted by subscription on axis "' + sub.axis + '"'];
    },
  };

  if (typeof window !== 'undefined') { window.CV_AXIS = makeAxis; window.CV_AXES = CV_AXES; }
})();
