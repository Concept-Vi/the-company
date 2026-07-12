// core/cv-node.js
// ============================================================================
// CV_NODE — the universal NODE: the collapse of the registries into ONE
// fundamental unit, ONE relation, and ONE mechanic.
//
// Idea (Info/Tim): "every component, every content on a screen is the same
// fundamental unit as a Glyphic. All tokens, all slots and sockets — one
// mechanic, one thing, instanced into everything."
//
// This file does NOT create a second home for any value. It is a LENS + a
// RECURSIVE RESOLVER over the homes that already exist — it references them and
// never copies their data; it throws (loud) on a missing home:
//   · Types        window.CV_REGISTRY  (kind / classification / slots / sockets / parts / valueSlots / conditions)
//   · Axis values  window.CV_AXES      (tokens ARE the value-units of an axis)
//   · Glyphics     window.CV_GLYPHIC   (compose geometry + symbol)
//   · Conditions   window.CV_COND      (gate any socket / slot)
//   · Render       window.__cvRenderType (block/surface/doc → the one engine)
//
// THE THREE COLLAPSES
// -------------------
//   1 · ONE UNIT     lens(entry) projects a Type, an axis value (a token), or a
//                    glyphic spec into the SAME node shape:
//                      { id, kind, layer, classification, axis, axisValue,
//                        valueSlots, sockets, parts, conditions, payload }
//                    A token is a leaf node (kind 'token'); a glyphic, a panel,
//                    a slide, a deck are interior nodes — same shape, different
//                    `kind`. Unity lives in the MECHANIC, not in flattening type:
//                    `kind` still carries solver + behaviour. (CLAUDE.md §3.)
//
//   2 · ONE RELATION a slot and a socket are one attachment point with `accepts`.
//                    accepts an AXIS  → a value-socket (a token/axis value plugs
//                    in). accepts a CLASSIFICATION → a thing-socket (a component
//                    plugs in). socketsOf() merges valueSlots + sockets; accepts()
//                    / candidates() take ONE path that branches only on what
//                    `accepts` names — so "pick a colour for a ring" and "pick a
//                    glyphic for a panel region" are the same call.
//
//   3 · ONE MECHANIC resolve(node) fills every socket by ADDRESS (never a copy),
//                    recurses, and yields a fully-resolved IR; render(node) hands
//                    that IR to the node's KIND solver. token → ring → glyphic →
//                    panel → slide → deck is the same call at every radius.
//                    Solvers are pluggable per kind (glyphic → CV_GLYPHIC.compose;
//                    token → axis resolveCSS; block/surface/doc → __cvRenderType).
//                    CV_NODE invents no renderer — it unifies the existing ones
//                    under one recursive entry point.
//
// Load AFTER conditions.js / axis-core.js (+ axes) / types-core.js / cv-glyphics.
// Pure + window-assigning; safe inside the compiled bundle.
// ============================================================================
(function () {
  'use strict';

  function fail(msg) { throw new Error('CV_NODE: ' + msg); }
  var R   = function () { return window.CV_REGISTRY; };
  var AX  = function () { return window.CV_AXES; };
  var GL  = function () { return window.CV_GLYPHIC; };
  var CND = function () { return window.CV_COND; };

  // -- canonical shape (the ONE node) -----------------------------------------
  function canonical(n) {
    return {
      id: n.id || null,
      kind: n.kind || 'node',
      layer: n.layer || 'block',
      classification: n.classification || [],
      axis: n.axis || null,
      axisValue: n.axisValue || null,
      valueSlots: n.valueSlots || {},     // value-taking attachment points (axis subscriptions)
      sockets: n.sockets || {},           // type-taking attachment points (classification)
      parts: n.parts || {},               // named sub-nodes
      conditions: n.conditions || [],
      payload: n.payload != null ? n.payload : null, // pointer to the source entry (never a copy)
    };
  }

  // ========================================================================
  // 1 · ONE UNIT — lens any registry entry into the canonical node shape
  // ========================================================================
  function detect(e) {
    if (typeof e === 'string') return 'type';                       // an id → resolve as a Type
    if (e.axis && e.value !== undefined && !e.kind) return 'axis-value';
    if (e.token !== undefined && e.id && !e.kind) return 'axis-value';
    if (e.form !== undefined || e.symbol !== undefined) return 'glyphic';
    return 'type';
  }

  function lens(entry, source) {
    if (entry == null) fail('lens(): nothing to project');
    source = source || detect(entry);
    if (source === 'type')       return fromType(entry);
    if (source === 'axis-value') return fromAxisValue(entry);
    if (source === 'glyphic')    return fromGlyphic(entry);
    fail('lens(): unknown source "' + source + '"');
  }

  // a Type (resolved through inheritance) IS already the node shape — we only
  // re-expose it canonically and keep a pointer to it. No copy of its data.
  function fromType(t) {
    var reg = R(); if (!reg) fail('lens(type): CV_REGISTRY not loaded');
    var type = (typeof t === 'string') ? reg.resolve(t) : t;
    if (!type) fail('lens(type): no Type "' + t + '"');
    return canonical({
      id: type.id, kind: type.kind || type.family || 'type', layer: type.layer,
      classification: type.classification || [],
      axis: type.axis || null, axisValue: type.axisValue || null,
      valueSlots: type.valueSlots || {},
      sockets: type.sockets || type.slots || {},
      parts: type.parts || {},
      conditions: type.conditions || [],
      payload: type,
    });
  }

  // an axis value (a TOKEN) is a LEAF node: kind 'token'. Its axis + value are
  // its identity; its CSS its payload. No sockets, no parts — the floor of the
  // recursion. (Tokens ARE the value-units of an axis — axis-core.js.)
  function fromAxisValue(v) {
    var axisId = v.axis || (v.meta && v.meta.axis) || null;
    var valueId = v.value !== undefined ? v.value : v.id;
    return canonical({
      id: (axisId ? axisId + '.' : '') + valueId,
      kind: 'token', layer: 'token',
      classification: ['token'].concat(axisId ? [axisId] : []),
      axis: axisId, axisValue: valueId,
      payload: v,
    });
  }

  // a glyphic spec → a node of kind 'glyphic' whose ring/symbol parts are
  // pre-filled from the spec; structure mirrors the registered glyphic Type.
  function fromGlyphic(spec) {
    return canonical({
      id: 'glyphic:' + (spec.symbol || '?') + '/' + (spec.form || '?'),
      kind: 'glyphic', layer: 'atom',
      classification: ['glyphic', 'mark', 'atom'],
      parts: {
        ring:   { kind: 'ring',   value: { form: spec.form, color: spec.color && spec.color.ring, texture: spec.texture } },
        symbol: { kind: 'symbol', value: { symbol: spec.symbol, color: spec.color && spec.color.symbol } },
      },
      payload: spec,
    });
  }

  // ========================================================================
  // 2 · ONE RELATION — slots & sockets are one attachment point
  // ========================================================================
  // Merge a node's value-slots and thing-sockets into one map. Each entry:
  //   { name, kind:'value'|'thing', accepts, ...rest }
  // value-slot.accepts = its axis id; thing-socket.accepts = a classification.
  function socketsOf(node) {
    var n = (node && node.kind) ? node : lens(node);
    var out = {};
    Object.keys(n.valueSlots || {}).forEach(function (k) {
      var s = n.valueSlots[k] || {};
      out[k] = Object.assign({}, s, { name: k, kind: 'value', accepts: s.axis || s.accepts || null });
    });
    Object.keys(n.sockets || {}).forEach(function (k) {
      var s = n.sockets[k] || {};
      out[k] = Object.assign({}, s, { name: k, kind: 'thing', accepts: s.accepts || null });
    });
    return out;
  }

  // the merged value-slots of a node INCLUDING its parts' slots (a glyphic's
  // form/symbol/fill live on its ring/symbol parts, not the parent) — flattened
  // so the projection + actions see one editable facet set. Parent wins on a
  // name collision; a part-type's slots are resolved from the registry.
  function flatValueSlots(node) {
    var n = (node && n_ok(node)) ? node : lens(node);
    var out = {};
    // Walk the WHOLE part subtree depth-first (a glyphic's fill now nests inside
    // its ring, not as a peer) so every descendant part's slots flatten into one
    // editable facet set. First writer wins on a name collision (parent → ring →
    // its fill → symbol), which is why per-part colour/texture currently collapse
    // to one shared slot — the dedicated per-part pass will key them by part path.
    function walk(slots, parts) {
      Object.keys(slots || {}).forEach(function (k) { if (!(k in out)) out[k] = slots[k]; });
      Object.keys(parts || {}).forEach(function (pn) {
        var p = parts[pn] || {};
        var pt = (p.type && R()) ? R().get(p.type) : null;
        var vs = pt ? (pt.valueSlots || {}) : (p.valueSlots || {});
        var sub = pt ? (pt.parts || {}) : (p.parts || {});
        walk(vs, sub);
      });
    }
    walk(n.valueSlots, n.parts);
    return out;
  }

  // partSlots(node): the per-part slot GROUPS, NOT collapsed — the basis for
  // per-part editing (a glyphic's ring / fill / symbol each shown with their OWN
  // colour / texture / motion). Walks the part subtree depth-first; each group is
  // { part, label, type, slots } where slots is the part-type's valueSlots. The
  // parent's own valueSlots are the WHOLE-UNIT facets (size/depth/whole-motion),
  // returned separately by the projection — so the inspector can show "the whole"
  // then each part. (flatValueSlots stays for back-compat / the collapsed view.)
  function partSlots(node) {
    var n = (node && n_ok(node)) ? node : lens(node);
    var out = [];
    (function walk(parts) {
      Object.keys(parts || {}).forEach(function (pn) {
        var p = parts[pn] || {};
        var pt = (p.type && R()) ? R().get(p.type) : null;
        var vs = pt ? (pt.valueSlots || {}) : (p.valueSlots || {});
        var sub = pt ? (pt.parts || {}) : (p.parts || {});
        if (Object.keys(vs).length) out.push({ part: pn, label: (pt && pt.name) || pn, type: p.type || null, slots: vs });
        walk(sub);
      });
    })(n.parts);
    return out;
  }
  function n_ok(x) { return x && x.kind; }

  // resolve which axis (if any) a socket's `accepts` names — the value-socket test.
  function axisOf(socket) {
    var acc = socket && socket.accepts;
    if (typeof acc === 'string' && AX() && AX().has(acc)) return acc;
    if (acc && acc.axis) return acc.axis;
    if (socket && socket.axis) return socket.axis;
    return null;
  }

  // does `candidate` fit `socket`? ONE matcher now lives in CV_REGISTRY.accepts —
  // since the fold (spec §09) it handles BOTH the value-socket/axis path and the
  // thing-socket/classification path. CV_NODE adds the one thing the registry
  // doesn't: DECORATOR requirements (socket.requires / .forbids checked against
  // the candidate's CV_DECORATORS.decoratorsOf) — "other things decorators can
  // do": participate in acceptance.
  function accepts(socket, candidate, ctx) {
    if (!socket) return false;
    var DEC = window.CV_DECORATORS;
    if (DEC && (socket.requires || socket.forbids)) {
      var subj = (candidate && candidate.payload && (candidate.payload.classification || candidate.payload.provenance)) ? candidate.payload : candidate;
      var have = DEC.decoratorsOf(subj || {}).map(function (d) { return d.id; });
      var req = socket.requires ? (Array.isArray(socket.requires) ? socket.requires : [socket.requires]) : [];
      var forb = socket.forbids ? (Array.isArray(socket.forbids) ? socket.forbids : [socket.forbids]) : [];
      if (!req.every(function (r) { return have.indexOf(r) >= 0; })) return false;
      if (forb.some(function (f) { return have.indexOf(f) >= 0; })) return false;
    }
    if (!R()) fail('accepts(): CV_REGISTRY not loaded');
    var type = (candidate && (candidate.classification || candidate.axisValue !== undefined)) ? candidate
             : (candidate && candidate.payload) ? candidate.payload
             : (typeof candidate === 'string' ? R().get(candidate) : candidate);
    return R().accepts({ accepts: socket.accepts, axis: axisOf(socket), groups: socket.groups, values: socket.values, conditions: socket.conditions }, type || {}, ctx);
  }

  // everything that fits a socket — value-nodes OR thing-nodes — as ONE list of
  // canonical nodes. This is exactly what an editor / the foundry shows.
  // An accepts of 'action' resolves against CV_ACTIONS (the verbs registry) —
  // the same call, a different home.
  function candidates(socket, ctx) {
    var axisId = axisOf(socket);
    if (axisId) {
      if (!AX()) fail('candidates(): CV_AXES not loaded for a value-socket');
      return AX().resolve(axisId)
        .candidates({ axis: axisId, groups: socket.groups, values: socket.values })
        .map(function (v) { return fromAxisValue(Object.assign({ axis: axisId }, v)); });
    }
    var acc = socket && socket.accepts;
    var wantsAction = acc && (Array.isArray(acc) ? acc.indexOf('action') >= 0 : acc === 'action');
    if (wantsAction && window.CV_ACTIONS) {
      return window.CV_ACTIONS.all().map(function (a) {
        return canonical({ id: 'action:' + a.id, kind: 'action', layer: 'system', classification: ['action', a.actionType], payload: a });
      });
    }
    if (!R()) fail('candidates(): CV_REGISTRY not loaded for a thing-socket');
    return R().candidatesForSocket({ accepts: socket && socket.accepts, conditions: socket && socket.conditions }, ctx)
      .map(function (t) { return fromType(t); });
  }

  // ========================================================================
  // 3 · ONE MECHANIC — recursive resolve + pluggable per-kind solvers
  // ========================================================================
  var SOLVERS = {};
  function solver(kind, fn) { SOLVERS[kind] = fn; return fn; }
  function hasSolver(kind) { return !!(SOLVERS[kind] || SOLVERS['*']); }

  // a node contributes its own state DOWN to its children's ctx, so a condition
  // deep in the tree can read an ancestor's state (e.g. a ring's "texture
  // requires fill != none" reads the glyphic's fill). A spec payload (no `id`)
  // is instance state → spread it; a Type payload (has `id`) is structure → skip.
  function contributeCtx(n) {
    var c = {};
    if (n.payload && typeof n.payload === 'object' && n.payload.id === undefined) Object.assign(c, n.payload);
    if (n.axis && n.axisValue !== undefined) c[n.axis] = n.axisValue;
    return c;
  }

  // fill a node's sockets by ADDRESS (by reference, from the registry — never a
  // copy), resolve its parts, and recurse — threading CTX downward so conditions
  // gate by accumulated ancestor state. Returns a fully-resolved IR (data). The
  // SAME call runs at every radius: token → ring → glyphic → panel → slide.
  function resolve(node, ctx) {
    var n = (node && node.kind) ? node : lens(node);
    ctx = ctx || {};
    var childCtx = Object.assign({}, ctx, contributeCtx(n));
    var enabled = !n.conditions || !CND() || CND().testAll(n.conditions, childCtx); // this node, gated by ctx
    var sk = socketsOf(n);
    var filled = {}, gates = {}, skipped = [];
    Object.keys(sk).forEach(function (name) {
      var s = sk[name];
      var on = !s.conditions || !CND() || CND().testAll(s.conditions, childCtx);
      gates[name] = on;
      if (!on) { skipped.push(name); return; }
      if (s.kind === 'thing' && s.address && typeof s.address === 'string' && s.address.indexOf('action:') === 0) {
        // ACTION-socket fill — the address names a CV_ACTIONS verb. Actions stay
        // in their one home (the actions registry); this lenses the verb into a
        // canonical LEAF node (no recursion — an action has no sub-sockets here).
        var ACT = window.CV_ACTIONS;
        var act = ACT && ACT.tryResolve(s.address.slice(7));
        if (act) filled[name] = canonical({ id: 'action:' + act.id, kind: 'action', layer: 'system', classification: ['action', act.actionType], payload: act });
        return;
      }
      if (s.kind === 'thing' && s.address && R()) {
        var occ = R().get(s.address);                 // address → occupant, by reference
        if (occ) filled[name] = resolve(fromType(occ), childCtx); // recurse — identical call, ctx flows down
      }
    });
    var parts = {};
    Object.keys(n.parts || {}).forEach(function (name) {
      var p = n.parts[name];
      if (p && p.type && R() && R().get(p.type)) parts[name] = resolve(fromType(R().get(p.type)), childCtx);
      else parts[name] = p;                            // inline part (already a sub-spec)
    });
    return Object.assign({}, n, { filled: filled, parts: parts, gates: gates, skipped: skipped, enabled: enabled, ctx: childCtx, resolved: true });
  }

  // resolve, then hand the IR to the node's KIND solver. Loud-fail if no solver.
  function render(node, ctx) {
    var ir = resolve(node, ctx);
    var fn = SOLVERS[ir.kind] || SOLVERS['*'];
    if (!fn) fail('render(): no solver for kind "' + ir.kind + '" (have: ' + Object.keys(SOLVERS).join(', ') + ')');
    return fn(ir, ctx || {});
  }

  // ---- seed the kind-solvers that just re-point at existing homes -----------
  // token → the axis resolves the value to its CSS (var(--token)).
  solver('token', function (ir) {
    if (!AX()) fail('token solver: CV_AXES not loaded');
    if (!ir.axis) return null;
    return AX().resolve(ir.axis).resolveCSS(ir.axisValue);
  });
  // glyphic → the existing compositor (geometry via CV_SHAPES, symbol via CV_ICONS).
  solver('glyphic', function (ir, ctx) {
    if (!GL()) fail('glyphic solver: CV_GLYPHIC not loaded');
    return GL().compose(ir.payload || {}, (ctx && ctx.opts) || {});
  });
  // block / surface / doc → the one engine bridge (React). Present only when the
  // bundle is loaded; otherwise a glyphic/token still resolves standalone.
  solver('*', function (ir, ctx) {
    if (typeof window !== 'undefined' && window.__cvRenderType && ir.payload) {
      return { component: window.__cvRenderType, props: { type: ir.payload, data: (ctx && ctx.data) || null } };
    }
    return ir; // no engine on this page → hand back the resolved IR
  });

  // ---- tokens-as-nodes view: axis values projected as canonical nodes -------
  // CV_AXES is the store; this is a VIEW (no copy). tokens() → every value of
  // every axis as a leaf node; tokens(axisId) → one axis's values as nodes.
  function tokens(axisId) {
    if (!AX()) fail('tokens(): CV_AXES not loaded');
    var axes = axisId ? [AX().resolve(axisId)] : AX().all();
    var out = [];
    axes.forEach(function (ax) {
      ax.values().forEach(function (v) { out.push(fromAxisValue(Object.assign({ axis: ax.id }, v))); });
    });
    return out;
  }

  // a SELECTION is a node too (kind 'selection') — Root Unity: everything is the
  // one unit. Build one from member ids so actions apply to it uniformly.
  function selection(ids) {
    ids = Array.isArray(ids) ? ids : (ids ? [ids] : []);
    return canonical({
      id: 'selection:' + ids.join(','),
      kind: 'selection', layer: 'system',
      classification: ['selection', 'container'],
      parts: { members: { kind: 'members', value: ids } },
      payload: { members: ids, mode: ids.length > 1 ? 'multi' : 'single' },
    });
  }

  // decorators present on a node — delegate to the one vocabulary (CV_DECORATORS).
  function decoratorsOf(node) {
    var DEC = window.CV_DECORATORS;
    if (!DEC) return [];
    var n = (node && node.payload !== undefined) ? node : (typeof node === 'string' ? fromType(node) : node);
    return DEC.decoratorsOf((n && n.payload) ? n.payload : n);
  }

  // ========================================================================
  // public surface (mirrors the other registries' verbs)
  // ========================================================================
  window.CV_NODE = {
    canonical: canonical,
    lens: lens,
    socketsOf: socketsOf,
    axisOf: axisOf,
    accepts: accepts,
    candidates: candidates,
    solver: solver,
    hasSolver: hasSolver,
    resolve: resolve,
    render: render,
    tokens: tokens,
    flatValueSlots: flatValueSlots,
    partSlots: partSlots,
    selection: selection,
    decoratorsOf: decoratorsOf,
    _solvers: SOLVERS,
  };
})();
