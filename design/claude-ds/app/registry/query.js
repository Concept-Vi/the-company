// app/registry/query.js
// ============================================================================
// CV_QUERY — uniform, cross-registry QUERY, and the generalised DERIVE-BY-QUERY.
//
// Info/Tim: "that generatable decorator — that class of issue is in many places;
// generalise it." The class: a RELATIONSHIP stored as a hardcoded map (kind →
// capability, type → editor, …) instead of COMPUTED by querying a single source.
// The fix-as-a-pattern: never store the map; query the registry that already
// owns the fact. This file is that pattern, named once and reused.
//
// THE RULE (Root Unity): a lookup is a query over a single source, never a copy.
// If you catch yourself writing `MAP[x] = y`, ask which registry already knows
// the y for x, and `CV_QUERY.relations`/`find` it instead.
//
//   CV_QUERY.from(name)            → every entry of a named registry
//   CV_QUERY.find(name, where)     → entries matching a where-spec
//   CV_QUERY.relations(node, opts) → THE generatable pattern, generalised:
//        entries of registry `opts.from` whose array field `opts.field` contains
//        one of the node's kind/classification. (e.g. {from:'ai',field:'generates'}
//        → the capability that produces this node.) Single-source, computed.
//
// where-spec: { field: value }              exact ===
//             { field: { contains: v } }     array includes v
//             { field: { in: [..] } }         value is one of
//             { field: { exists: true } }     present + non-empty
//             function(entry) -> boolean      escape hatch
//
// Load after the registries it reads (lazy refs; tolerant of absent ones).
// ============================================================================
(function () {
  'use strict';

  // the named single sources — each already exposes all()/query()
  var SOURCES = {
    ai:         function () { return window.CV_AI; },
    types:      function () { return window.CV_REGISTRY; },
    actions:    function () { return window.CV_ACTIONS; },
    decorators: function () { return window.CV_DECORATORS; },
    axes:       function () { return window.CV_AXES; },
    events:     function () { return window.CV_EVENTS; },
  };

  function from(name) {
    var get = SOURCES[name];
    if (!get) throw new Error('CV_QUERY: unknown registry "' + name + '" (have: ' + Object.keys(SOURCES).join(', ') + ')');
    var reg = get();
    if (!reg) return [];                       // not loaded on this page → empty, not a throw
    if (typeof reg.all === 'function') return reg.all();
    if (typeof reg.list === 'function') return reg.list();
    return [];
  }

  function matchField(val, spec) {
    if (spec && typeof spec === 'object' && !Array.isArray(spec)) {
      if ('contains' in spec) return Array.isArray(val) ? val.indexOf(spec.contains) >= 0 : val === spec.contains;
      if ('in' in spec) return (spec.in || []).indexOf(val) >= 0;
      if ('exists' in spec) { var has = val !== undefined && val !== null && !(Array.isArray(val) && !val.length) && val !== ''; return spec.exists ? has : !has; }
      return false;
    }
    return val === spec;
  }

  function where(list, spec) {
    if (!spec) return list;
    if (typeof spec === 'function') return list.filter(spec);
    return list.filter(function (e) {
      return Object.keys(spec).every(function (f) { return matchField(e ? e[f] : undefined, spec[f]); });
    });
  }

  function find(name, spec) { return where(from(name), spec); }

  // THE generalised derive-by-query: which entries of `from` declare (via an
  // array field) that they relate to this node's kind/classification.
  // opts = { from, field, classes? }  → returns matching entries (most-specific
  // ordering is the registry's own). Use [0] for "the one".
  function relations(node, opts) {
    opts = opts || {};
    var classes = opts.classes || [node && node.kind].concat((node && node.classification) || []).filter(Boolean);
    var field = opts.field;
    return from(opts.from).filter(function (e) {
      var v = e ? e[field] : null;
      if (!Array.isArray(v)) return false;
      return v.some(function (g) { return classes.indexOf(g) >= 0; });
    });
  }

  // convenience: the single best relation id (or null)
  function relation(node, opts) { var r = relations(node, opts); return r.length ? r[0].id : null; }

  // register a new named source (e.g. a registry added later) — keeps the façade open
  function registerSource(name, getter) { SOURCES[name] = getter; }

  window.CV_QUERY = {
    SOURCES: SOURCES,
    from: from, where: where, find: find,
    relations: relations, relation: relation,
    registerSource: registerSource,
  };
})();
