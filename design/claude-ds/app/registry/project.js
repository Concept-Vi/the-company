// app/registry/project.js
// ============================================================================
// CV_PROJECT — the ONE projection: a node → both the UI and the AI.
//
// Idea (Info/Tim): "this single node system would use the same mechanism for
// projection to BOTH my UI and the AI." This is that mechanism. A node already
// declares everything about itself (kind · value-slots = axis subscriptions ·
// sockets · parts · decorators · conditions) and CV_ACTIONS declares what can be
// DONE to it. CV_PROJECT reads that ONE declaration and emits:
//
//   toInspector(node, ctx) → a UI descriptor: a control per editable slot (its
//        options resolved live from the axis), a dropzone per socket (its
//        candidates resolved live), a button per applicable action, the present
//        decorators as badges. The Studio renders this — no per-node UI code.
//
//   toToolSchema(node, ctx) → an AI function-calling schema: one function per
//        applicable action, its params typed (enums resolved from the same
//        axis/candidate sources), its description = the action's Skill. This is
//        what the chat/voice AI is handed — no per-node tool code.
//
//   toContext(studioState) → the shared CONTEXT blob (selection · node · screen
//        · hover · clicks) that BOTH the AI prompt and CV_VARS/CV_ACTIONS resolve
//        against. One context, one variable mechanism, both consumers.
//
// The two projections are the SAME set of actions + slots from the SAME source,
// so the click-UI and the AI can never drift: a new action/slot/axis-value
// appears in both at once. Add a verb to CV_ACTIONS → it's a button AND a tool.
//
// Load after cv-node.js / actions.js / axis-core.js / decorators.js.
// ============================================================================
(function () {
  'use strict';
  var N   = function () { return window.CV_NODE; };
  var ACT = function () { return window.CV_ACTIONS; };
  var AX  = function () { return window.CV_AXES; };
  var DEC = function () { return window.CV_DECORATORS; };

  function nodeOf(x) {
    var n = N(); if (!n) throw new Error('CV_PROJECT: CV_NODE not loaded');
    return (x && x.kind) ? x : n.lens(x);
  }

  // ---- the value space + current value of a value-slot (live from the axis) --
  function slotView(name, slot, node) {
    var axisId = slot.axis || null;
    var options = null, current;
    if (axisId && AX() && AX().has(axisId)) {
      var ax = AX().resolve(axisId);
      var cand = ax.candidates({ axis: axisId, groups: slot.groups, values: slot.values });
      options = cand.map(function (v) { return { id: v.id, label: v.label, token: v.token || null, zero: !!v.zero }; });
      current = slot.default != null ? slot.default : ax.default();
    } else if (slot.values) {
      options = slot.values.map(function (v) { return { id: v, label: v }; });
      current = slot.default;
    }
    return { name: name, axis: axisId, means: slot.means || '', options: options, current: current, editable: true };
  }

  // ============================ UI projection ===============================
  function toInspector(nodeOrId, ctx) {
    var node = nodeOf(nodeOrId);
    var n = N();
    var aud = (ctx && ctx.audience) || null;
    var sk = n.socketsOf(node);

    // value-slots include the node's PARTS' slots (a glyphic's form/symbol/fill
    // live on its ring/symbol parts) — flattened to one editable facet set
    // (back-compat: the collapsed view). wholeSlots + partGroups below give the
    // PER-PART view (proper independence): the whole-unit facets, then each part.
    var flat = n.flatValueSlots ? n.flatValueSlots(node) : (node.valueSlots || {});
    var slots = [], sockets = [];
    Object.keys(flat).forEach(function (name) { slots.push(slotView(name, flat[name], node)); });

    // WHOLE-UNIT slots — the parent's own valueSlots (size/depth/whole-motion/value).
    var ownVS = node.valueSlots || {};
    var wholeSlots = Object.keys(ownVS).map(function (name) { return slotView(name, ownVS[name], node); });

    // PER-PART groups — each part with its OWN slots (colour/texture/motion + part
    // specifics). Current value is read by the consumer from the live node's
    // per-part value (CV_INSPECTOR uses CV_GLYPHIC.expandParts), so this is pure
    // structure + live options — the value-side twin of the part tree.
    var partGroups = (n.partSlots ? n.partSlots(node) : []).map(function (g) {
      return { part: g.part, label: g.label, slots: Object.keys(g.slots).map(function (nm) {
        var v = slotView(nm, g.slots[nm], node); v.part = g.part; return v;
      }) };
    });

    Object.keys(sk).forEach(function (name) {
      var s = sk[name];
      if (s.kind === 'value') return;                 // already covered by flat
      var cands = [];
      try { cands = n.candidates(s, ctx).map(function (c) { return { id: c.id, label: (c.payload && c.payload.name) || c.id }; }); } catch (e) {}
      sockets.push({ name: name, accepts: s.accepts, multiple: !!s.multiple, optional: !!s.optional, event: s.kind === 'event' || s.event ? (s.event || 'click') : null, candidates: cands });
    });

    var actions = (ACT() ? ACT().applicable(node, ctx) : []).map(function (a) {
      var params = {};
      Object.keys(a.params || {}).forEach(function (pn) {
        params[pn] = { type: a.params[pn].type || 'string', required: !!a.params[pn].required, means: a.params[pn].means || '', options: ACT().paramOptions(a, pn, node, {}) };
      });
      return { id: a.id, verb: a.verb, actionType: a.actionType, icon: a.icon, skill: a.skill, params: params };
    });

    var decorators = (DEC() ? DEC().decoratorsOf(node.payload || node) : []).map(function (d) {
      return { id: d.id, value: d.value, group: d.def && d.def.group, behaviour: !!(d.def && d.def.behaviour), audience: (d.def && d.def.audience) || ['author', 'dev'] };
    }).filter(function (d) { return !aud || d.audience.indexOf(aud) >= 0; });

    return { id: node.id, kind: node.kind, layer: node.layer, slots: slots, wholeSlots: wholeSlots, partGroups: partGroups, sockets: sockets, actions: actions, decorators: decorators };
  }

  // ========================== AI tool projection ============================
  // JSON-schema-ish function list (the shape Claude/OpenAI tool calling expects).
  function paramSchema(action, pn, node) {
    var p = (action.params || {})[pn] || {};
    var opts = ACT() ? ACT().paramOptions(action, pn, node, {}) : null;
    var schema = { type: p.type === 'number' ? 'number' : 'string', description: p.means || '' };
    if (opts && opts.length) schema.enum = opts;
    else if (p.axisFrom) schema.description = (schema.description ? schema.description + ' ' : '') + '(a value of the axis of the chosen "' + p.axisFrom + '")';
    return schema;
  }
  function toToolSchema(nodeOrId, ctx) {
    var node = nodeOf(nodeOrId);
    var actions = ACT() ? ACT().applicable(node, ctx) : [];
    return actions.map(function (a) {
      var props = {}, required = [];
      Object.keys(a.params || {}).forEach(function (pn) {
        props[pn] = paramSchema(a, pn, node);
        if (a.params[pn].required) required.push(pn);
      });
      return {
        name: a.id,
        description: (a.description || '') + (a.skill ? ' — ' + a.skill : ''),
        parameters: { type: 'object', properties: props, required: required },
      };
    });
  }

  // ========================== shared CONTEXT ================================
  // project the live Studio state into the ONE context blob that the AI prompt
  // AND CV_VARS / CV_ACTIONS resolve against. Same context, same variable paths.
  function toContext(state) {
    state = state || {};
    var node = state.node ? nodeOf(state.node) : null;
    return {
      surface: state.surface || 'studio',
      selection: state.selection || (node && node.id) || null,
      node: node ? { id: node.id, kind: node.kind, layer: node.layer, classification: node.classification, spec: state.node && state.node.payload ? state.node : state.node } : null,
      hover: state.hover || null,
      clicks: state.clicks || [],
      screen: state.screen || { surface: state.surface || 'studio' },
      // a flat alias so "{{ selection }}" / "{{ node.kind }}" resolve directly
    };
  }

  // a small consistency check (used by QA + the registry inspector): the UI's
  // action set and the AI tool set are the SAME functions (one source).
  function coherent(nodeOrId, ctx) {
    var ui = toInspector(nodeOrId, ctx).actions.map(function (a) { return a.id; }).sort();
    var ai = toToolSchema(nodeOrId, ctx).map(function (t) { return t.name; }).sort();
    return JSON.stringify(ui) === JSON.stringify(ai);
  }

  // ===================== generation-from-data (views) ======================
  // A VIEW is a node (kind 'view') whose spec is { query, project?, onPick?,
  // pickArgs? }. toCollection runs the query (CV_QUERY / an axis) and projects
  // each result into a UI-ready row — so every collection-UI (a library, a
  // palette, a menu, a gallery) is GENERATED FROM DATA, live, with no per-surface
  // code. Add a registry entry → it appears in the relevant view automatically.
  function runQuery(q, ctx) {
    if (!q) return [];
    if (q.axis) { var AX2 = AX(); return (AX2 && AX2.has(q.axis)) ? AX2.resolve(q.axis).values() : []; }
    var Q = window.CV_QUERY; if (!Q) return [];
    if (q.relation) return Q.relations(q.node || (ctx && ctx.node), q);
    return Q.find(q.from, q.where);
  }
  function pick(e, key, fallback) { return (key && e && e[key] != null) ? e[key] : (e && (e[fallback] != null ? e[fallback] : undefined)); }
  function toCollection(viewOrId, ctx) {
    var v = (typeof viewOrId === 'string') ? (window.CV_REGISTRY && window.CV_REGISTRY.resolve(viewOrId)) : viewOrId;
    if (!v) throw new Error('CV_PROJECT.toCollection: no view "' + viewOrId + '"');
    var spec = v.spec || {};
    var rows = runQuery(spec.query, ctx);
    var p = spec.project || {};
    return rows.map(function (e) {
      return {
        id: e.id,
        label: pick(e, p.label, 'label') != null ? pick(e, p.label, 'label') : (e.name || e.id),
        sub: p.sub ? e[p.sub] : (e.description || e.group || ''),
        kind: e.kind || null,
        token: e.token || null,
        onPick: spec.onPick || null,     // an action id to invoke when this row is chosen
        pickArgs: spec.pickArgs || null, // value-specs (CV_VARS) resolved with { item: entry, … }
        entry: e,
      };
    });
  }

  window.CV_PROJECT = {
    toInspector: toInspector,
    toToolSchema: toToolSchema,
    toContext: toContext,
    toCollection: toCollection,
    coherent: coherent,
  };
})();
