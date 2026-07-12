// app/registry/vars.js
// ============================================================================
// CV_VARS — the ONE variable-resolution mechanism.
//
// Idea (Info/Tim): actions, context-sharing, conditions and projection all need
// "variable resolution, the same mechanism." This is that mechanism — a single
// resolver that turns a value-spec into a concrete value against a CONTEXT. Used
// by CV_COND (gating), CV_ACTIONS (param binding), CV_PROJECT (UI + AI schema)
// and the Studio context. One reader, so a path means the same thing everywhere.
//
// A value-spec is one of:
//   · literal           42, "gold", true, ["a","b"]      → returned as-is
//   · path string       "{{ selection.node.kind }}"      → read from ctx
//   · interpolation     "for {{ selection.id }} now"      → string with paths spliced
//   · var object        { var: "selection.id", default: "—" }
//   · ref object        { ref: "glyphic", field: "name" } → a registry entry's field
//   · computed          { op: "join"|"eq"|"not"|"coalesce"|"map", args: [...] }
//
// A CONTEXT is a plain object (the Studio's live state — selection, screen,
// clicks, doc, plus anything a context resolver contributed). Paths are dotted,
// array indices allowed: "items.0.label". Missing path → undefined (loud only
// where the caller wants it; resolution itself is total so UIs don't crash).
//
// Load early (pure, no deps). CV_COND delegates to it when present.
// ============================================================================
(function () {
  'use strict';

  // dotted-path read — the canonical one (CV_COND.getField delegates here)
  function getPath(ctx, path) {
    if (ctx == null || path == null) return undefined;
    if (typeof path !== 'string') return undefined;
    return path.split('.').reduce(function (o, k) {
      if (o == null) return undefined;
      // support "a[0]" as well as "a.0"
      return o[k];
    }, ctx);
  }

  var INTERP = /\{\{\s*([^}]+?)\s*\}\}/g;
  function isPlain(v) { return v && typeof v === 'object' && !Array.isArray(v); }

  function resolveString(str, ctx) {
    // whole-string single path → return the RAW value (number/obj/array preserved)
    var whole = str.match(/^\{\{\s*([^}]+?)\s*\}\}$/);
    if (whole) return resolvePathToken(whole[1].trim(), ctx);
    // otherwise interpolate to a string
    if (str.indexOf('{{') < 0) return str;             // plain literal string
    return str.replace(INTERP, function (_, expr) {
      var v = resolvePathToken(expr.trim(), ctx);
      return v == null ? '' : String(v);
    });
  }

  // a path token may carry a "| default" tail: "{{ a.b | n/a }}"
  function resolvePathToken(tok, ctx) {
    var parts = tok.split('|');
    var v = getPath(ctx, parts[0].trim());
    if ((v === undefined || v === null) && parts.length > 1) return parts.slice(1).join('|').trim();
    return v;
  }

  var OPS = {
    join:     function (a) { return (a[0] || []).join(a[1] != null ? a[1] : ', '); },
    eq:       function (a) { return a[0] === a[1]; },
    not:      function (a) { return !a[0]; },
    coalesce: function (a) { for (var i = 0; i < a.length; i++) if (a[i] != null && a[i] !== '') return a[i]; return null; },
    concat:   function (a) { return a.map(function (x) { return x == null ? '' : String(x); }).join(''); },
    length:   function (a) { return (a[0] && a[0].length) || 0; },
  };

  // the resolver — total (never throws); returns the concrete value
  function resolve(spec, ctx) {
    ctx = ctx || {};
    if (spec == null) return spec;
    if (typeof spec === 'string') return resolveString(spec, ctx);
    if (typeof spec !== 'object') return spec;          // number / boolean
    if (Array.isArray(spec)) return spec.map(function (s) { return resolve(s, ctx); });
    if ('var' in spec) {
      var v = getPath(ctx, spec.var);
      return (v === undefined || v === null) ? (('default' in spec) ? spec.default : undefined) : v;
    }
    if ('ref' in spec) {
      var reg = window.CV_REGISTRY;
      var ent = reg && reg.get ? reg.get(spec.ref) : null;
      return ent ? (spec.field ? ent[spec.field] : ent) : (spec.default != null ? spec.default : null);
    }
    if ('query' in spec) {
      // derive-by-query (same principle as CV_QUERY): a value computed by asking
      // a single-source registry, never stored. q = { from, where?, relation?,
      // field?, select? }. relation:true → CV_QUERY.relations against ctx.node.
      var Q = window.CV_QUERY;
      if (!Q) return ('default' in spec) ? spec.default : null;
      var q = spec.query || {};
      var res = q.relation ? Q.relations(q.node ? resolve(q.node, ctx) : ctx.node, q) : Q.find(q.from, q.where);
      if (q.select) return Array.isArray(res) ? res.map(function (r) { return r && r[q.select]; }) : (res && res[q.select]);
      return res;
    }
    if ('op' in spec) {
      var fn = OPS[spec.op];
      if (!fn) return undefined;
      return fn((spec.args || []).map(function (a) { return resolve(a, ctx); }));
    }
    // a plain object of specs → resolve each value
    return resolveAll(spec, ctx);
  }

  // deep-resolve every value-spec in a plain object (used for action arg maps)
  function resolveAll(obj, ctx) {
    if (Array.isArray(obj)) return obj.map(function (o) { return resolve(o, ctx); });
    if (!isPlain(obj)) return resolve(obj, ctx);
    var out = {};
    Object.keys(obj).forEach(function (k) { out[k] = resolve(obj[k], ctx); });
    return out;
  }

  // does a spec REFERENCE the context (is it dynamic) — for editor hints
  function isDynamic(spec) {
    if (typeof spec === 'string') return spec.indexOf('{{') >= 0;
    if (isPlain(spec)) return ('var' in spec) || ('ref' in spec) || ('op' in spec);
    return false;
  }

  window.CV_VARS = {
    getPath: getPath,
    resolve: resolve,
    resolveAll: resolveAll,
    isDynamic: isDynamic,
    OPS: Object.keys(OPS),
  };
})();
