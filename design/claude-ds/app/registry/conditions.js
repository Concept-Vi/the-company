// app/registry/conditions.js
// ============================================================================
// CV_COND — the shared CONDITION evaluator.
//
// "Everything can have conditions for their slots and sockets and declarations"
// (Info). A condition gates whether a slot is enabled, whether a socket accepts
// a thing, or whether a declaration applies — evaluated against a CONTEXT (the
// current spec/state of the component). One evaluator, used everywhere, so the
// rule is single-sourced and the same in validation and in the editor UI.
//
// A condition may be expressed three ways (all normalise to the same eval):
//   · structured  { field, op, value }            e.g. { field:'fill', op:'!=', value:'none' }
//                 { all:[...] } / { any:[...] } / { not: cond }   (boolean trees)
//   · string DSL  "fill != none", "size >= md", "texture requires fill != none"
//                 ("A requires B" → if A-side present, B must hold; sugar for any)
//   · predicate   function(ctx) -> boolean        (escape hatch)
//
// ops: == != > >= < <= in !in exists !exists truthy falsy
// Load after nothing (pure); before types-core uses it (types-core guards).
// ============================================================================
(function () {
  'use strict';

  var OPS = {
    '==': function (a, b) { return a === b; },
    '!=': function (a, b) { return a !== b; },
    '>':  function (a, b) { return Number(a) >  Number(b); },
    '>=': function (a, b) { return Number(a) >= Number(b); },
    '<':  function (a, b) { return Number(a) <  Number(b); },
    '<=': function (a, b) { return Number(a) <= Number(b); },
    'in': function (a, b) { return (Array.isArray(b) ? b : String(b).split('|')).indexOf(a) >= 0; },
    '!in':function (a, b) { return (Array.isArray(b) ? b : String(b).split('|')).indexOf(a) < 0; },
    'exists':  function (a) { return a !== undefined && a !== null && a !== ''; },
    '!exists': function (a) { return a === undefined || a === null || a === ''; },
    'truthy':  function (a) { return !!a; },
    'falsy':   function (a) { return !a; },
  };

  function getField(ctx, path) {
    if (!ctx) return undefined;
    // single source for dotted-path reads: delegate to CV_VARS when present
    // (so "a.b.c" means the same thing in conditions, actions, vars, projection).
    if (typeof window !== 'undefined' && window.CV_VARS && window.CV_VARS.getPath) {
      return window.CV_VARS.getPath(ctx, path);
    }
    return String(path).split('.').reduce(function (o, k) { return (o == null ? undefined : o[k]); }, ctx);
  }

  // coerce a literal token from the DSL ("none" → 'none', "3" → 3, "true" → true)
  function lit(s) {
    if (s == null) return s;
    s = String(s).trim();
    if (/^-?\d+(\.\d+)?$/.test(s)) return Number(s);
    if (s === 'true') return true;
    if (s === 'false') return false;
    if (/^['"].*['"]$/.test(s)) return s.slice(1, -1);
    if (s.indexOf('|') >= 0) return s.split('|').map(function (x) { return lit(x); });
    return s;
  }

  // parse a single comparison "field op value" or "field exists"
  function parseSimple(str) {
    str = str.trim();
    // "A requires B" → present(A) implies (B). Sugar; A is a field name.
    var req = str.split(/\s+requires\s+/i);
    if (req.length === 2) {
      return { any: [ { field: req[0].trim(), op: '!exists' }, parseSimple(req[1]) ] };
    }
    var m = str.match(/^([\w.$-]+)\s*(==|!=|>=|<=|>|<|!in|in)\s*(.+)$/);
    if (m) return { field: m[1], op: m[2], value: lit(m[3]) };
    var m2 = str.match(/^([\w.$-]+)\s+(exists|!exists|truthy|falsy)$/);
    if (m2) return { field: m2[1], op: m2[2] };
    // bare "field" → truthy
    return { field: str, op: 'truthy' };
  }

  function normalize(cond) {
    if (cond == null) return null;
    if (typeof cond === 'function') return { fn: cond };
    if (typeof cond === 'string') {
      // split top-level " and " / " or " (simple, no nesting in strings)
      if (/\s+and\s+/i.test(cond)) return { all: cond.split(/\s+and\s+/i).map(normalize) };
      if (/\s+or\s+/i.test(cond))  return { any: cond.split(/\s+or\s+/i).map(normalize) };
      return parseSimple(cond);
    }
    if (Array.isArray(cond)) return { all: cond.map(normalize) };
    if (cond.all) return { all: cond.all.map(normalize) };
    if (cond.any) return { any: cond.any.map(normalize) };
    if (cond.not) return { not: normalize(cond.not) };
    return cond; // already structured {field,op,value}
  }

  function evalOne(cond, ctx) {
    var c = normalize(cond);
    if (!c) return true;
    if (c.fn) { try { return !!c.fn(ctx); } catch (e) { return false; } }
    if (c.all) return c.all.every(function (x) { return evalOne(x, ctx); });
    if (c.any) return c.any.some(function (x) { return evalOne(x, ctx); });
    if (c.not) return !evalOne(c.not, ctx);
    var op = OPS[c.op]; if (!op) return true;          // unknown op → permissive (loud elsewhere)
    return op(getField(ctx, c.field), c.value);
  }

  var CV_COND = {
    OPS: Object.keys(OPS),
    normalize: normalize,
    // evaluate a single condition (any form) against ctx
    test: function (cond, ctx) { return evalOne(cond, ctx); },
    // evaluate a LIST of conditions (all must pass). Empty/undefined → true.
    testAll: function (conds, ctx) {
      if (!conds) return true;
      var arr = Array.isArray(conds) ? conds : [conds];
      return arr.every(function (c) { return evalOne(c, ctx); });
    },
    // explain which conditions FAIL (for editors / loud validation)
    failures: function (conds, ctx) {
      if (!conds) return [];
      var arr = Array.isArray(conds) ? conds : [conds];
      return arr.filter(function (c) { return !evalOne(c, ctx); })
                .map(function (c) { return typeof c === 'string' ? c : JSON.stringify(c); });
    },
  };

  if (typeof window !== 'undefined') window.CV_COND = CV_COND;
  if (typeof module !== 'undefined' && module.exports) module.exports = CV_COND;
})();
