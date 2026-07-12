// app/registry/actions.js
// ============================================================================
// CV_ACTIONS — the ACTIONS registry (the eighth single-source registry).
//
// Idea (Info/Tim): a Studio where you assemble from a library AND talk to it.
// For that, every "thing the system can DO" — a verb / tool / function call —
// must live in ONE catalogue, dynamically, with variable-resolved params and a
// per-action Skill (its AI-facing how/when). Then BOTH the click-UI and the
// chat/voice AI invoke the SAME action. The interface and the AI are two inputs
// to one action layer; nothing is hand-wired per surface.
//
// An ACTION is a Type (same shape as the other registries):
//   id            stable id (the function name the AI calls)
//   verb          imperative label ("Set value", "Insert", "Generate")
//   actionType    select | mutate | create | remove | navigate | generate | query
//   params        { name: { type|axis|from, required?, default?, means? } }
//                 each param is a value-spec resolved by CV_VARS against context
//   skill         the instruction fragment (the per-action "Skill") describing
//                 WHEN/HOW to use it — composed into the AI tool description
//   targets       classifications/kinds it applies to ('*' = any) → applicable()
//   surfaces      which surfaces it shows on (null = any)
//   run(args,ctx) performs it (loud-fail); args are CV_VARS-resolved; returns a result
//
// One mechanism: invoke(id, rawArgs, ctx) resolves args via CV_VARS (same
// variable mechanism as conditions + projection + context), checks required
// params, runs. A generative action's run delegates to CV_AI.execute — never the
// raw model. CV_PROJECT turns these into UI buttons AND an AI tool schema.
//
// Load after vars.js / conditions.js / types-core.js. CV_AI read lazily.
// ============================================================================
(function () {
  'use strict';
  var VARS = function () { return window.CV_VARS; };
  var COND = function () { return window.CV_COND; };
  var AI   = function () { return window.CV_AI; };
  var AX   = function () { return window.CV_AXES; };
  var DEC  = function () { return window.CV_DECORATORS; };

  // verbs that DO things to nodes, plus the meta/ui/macro kinds:
  //   define — a META-action that builds the BACKEND through the interface
  //            (define a kind, add a field, relate sockets, declare a rule…)
  //   ui     — an interface effect (highlight, focus) usually fired by an event
  //   macro  — a recorded chain of action invocations (a Skill that is steps,
  //            not a prompt). "Everything is the one unit" — a saved sequence is
  //            itself a registered action.
  var ACTION_TYPES = ['select', 'mutate', 'create', 'remove', 'navigate', 'generate', 'query', 'define', 'ui', 'macro'];

  var byId = {};
  var order = [];
  var listeners = new Set();
  function notify() { listeners.forEach(function (fn) { try { fn(); } catch (e) {} }); }

  function normalize(a) {
    if (!a || !a.id) throw new Error('CV_ACTIONS: an action needs an id');
    if (a.actionType && ACTION_TYPES.indexOf(a.actionType) < 0) throw new Error('CV_ACTIONS: "' + a.id + '" has unknown actionType "' + a.actionType + '"');
    return {
      id: a.id,
      verb: a.verb || a.id,
      actionType: a.actionType || 'mutate',
      label: a.label || a.verb || a.id,
      description: a.description || '',
      params: a.params || {},
      skill: a.skill || '',                 // per-action Skill (AI how/when)
      targets: a.targets || ['*'],          // classifications/kinds it applies to
      surfaces: a.surfaces || null,
      // who this verb is FOR ('maker' = regular person, 'author' = system-builder,
      // 'dev' = debug). null/unset = everyone. Projections filter by audience.
      audience: a.audience || null,
      conditions: a.conditions || [],       // when the action is available (CV_COND)
      run: typeof a.run === 'function' ? a.run : null,
      invert: typeof a.invert === 'function' ? a.invert : null, // (args,result) -> {action,args} inverse, for undo
      steps: a.steps || null,               // macro: a sequence of {action,args} to replay
      icon: a.icon || 'play',
      provenance: a.provenance || 'built-in',
    };
  }

  function register(a) { var n = normalize(a); if (!byId[n.id]) order.push(n.id); byId[n.id] = n; notify(); return n; }
  function registerMany(arr) { arr.forEach(function (a) { var n = normalize(a); if (!byId[n.id]) order.push(n.id); byId[n.id] = n; }); notify(); }
  function resolve(id) { var a = byId[id]; if (!a) throw new Error('CV_ACTIONS: no action "' + id + '" (have: ' + order.join(', ') + ')'); return a; }
  function tryResolve(id) { return byId[id] || null; }
  function all() { return order.map(function (id) { return byId[id]; }); }
  function query(q) {
    q = q || {}; var out = all();
    if (q.actionType) out = out.filter(function (a) { return a.actionType === q.actionType; });
    if (q.surface) out = out.filter(function (a) { return !a.surfaces || a.surfaces.indexOf('*') >= 0 || a.surfaces.indexOf(q.surface) >= 0; });
    if (q.search) { var s = String(q.search).toLowerCase(); out = out.filter(function (a) { return a.id.indexOf(s) >= 0 || a.verb.toLowerCase().indexOf(s) >= 0; }); }
    return out;
  }
  function subscribe(fn) { listeners.add(fn); return function () { listeners.delete(fn); }; }

  // which actions apply to a node — by target classification/kind match + conditions
  function applicable(node, ctx) {
    if (!node) return [];
    var aud = (ctx && ctx.audience) || null;
    var cls = [node.kind].concat(node.classification || []).filter(Boolean);
    return all().filter(function (a) {
      var targetOK = a.targets.indexOf('*') >= 0 || a.targets.some(function (t) { return cls.indexOf(t) >= 0; });
      if (!targetOK) return false;
      if (aud && a.audience && a.audience.indexOf(aud) < 0) return false;   // audience projection
      if (a.conditions && a.conditions.length && COND()) return COND().testAll(a.conditions, Object.assign({ node: node }, ctx || {}));
      return true;
    });
  }

  // the value space of a param (for projection: UI picker options + AI enum).
  // A param can name an axis directly, or { axisFrom:'<otherParamName>' } to take
  // the axis of whatever slot another param selected (e.g. value follows slot).
  function paramOptions(action, paramName, node, args) {
    var p = (action.params || {})[paramName]; if (!p) return null;
    // flattened value-slots include a node's PARTS' slots (a glyphic's form lives
    // on its ring part) — one editable facet set, via CV_NODE (single source).
    var flat = (window.CV_NODE && node) ? window.CV_NODE.flatValueSlots(node) : ((node && node.valueSlots) || {});
    var axisId = p.axis || null;
    if (!axisId && p.axisFrom && args && args[p.axisFrom] != null) {
      var slot = flat[args[p.axisFrom]];
      axisId = slot && slot.axis;
    }
    if (axisId && AX() && AX().has(axisId)) return AX().resolve(axisId).ids();
    if (p.from === 'node.valueSlots') return Object.keys(flat);
    if (p.from === 'node.sockets' && node) return Object.keys(node.sockets || {});
    if (p.values) return p.values.slice();
    return null;
  }

  // THE one entry point: resolve raw args through CV_VARS (same variable
  // mechanism), check required, run. ctx carries the live state (node, selection,
  // screen, host). Loud on missing action / required param / no run.
  function invoke(id, rawArgs, ctx) {
    var a = resolve(id);
    ctx = ctx || {};
    rawArgs = rawArgs || {};
    // resolve each arg through CV_VARS — EXCEPT params marked `raw` (they carry a
    // template to STORE, not to resolve now: a trigger's args, a macro's steps).
    var args = {};
    Object.keys(rawArgs).forEach(function (k) {
      var p = a.params[k];
      args[k] = (p && p.raw) ? rawArgs[k] : (VARS() ? VARS().resolve(rawArgs[k], ctx) : rawArgs[k]);
    });
    Object.keys(a.params).forEach(function (k) {
      var p = a.params[k];
      if (p.required && (args[k] === undefined || args[k] === null || args[k] === '')) {
        if (p.default !== undefined) args[k] = p.default;
        else throw new Error('CV_ACTIONS: "' + id + '" missing required param "' + k + '"');
      } else if (args[k] === undefined && p.default !== undefined) args[k] = p.default;
    });
    // macro: a recorded chain IS an action — replay its steps through invoke.
    if (!a.run && a.steps) return a.steps.map(function (s) { return invoke(s.action, s.args || {}, ctx); });
    if (!a.run) throw new Error('CV_ACTIONS: "' + id + '" has no run() or steps');
    return a.run(args, ctx);
  }

  // compute the inverse of an invocation (for undo). Uses the action's invert();
  // returns a { action, args } to invoke, or null if the action isn't invertible.
  function inverse(id, args, result) {
    var a = resolve(id);
    return a.invert ? a.invert(args || {}, result || {}) : null;
  }

  // ========================================================================
  // SEED — real verbs that operate on a node model held in ctx.node (a live
  // spec object the Studio re-renders). Each carries its Skill (AI how/when).
  // ========================================================================
  registerMany([
    {
      id: 'select', verb: 'Select', actionType: 'select', icon: 'cursor', targets: ['*'], audience: ['author', 'dev'],
      description: 'Make a node the current selection.',
      skill: 'Use to focus a node before editing it. Pass the node id (or "{{ hover.id }}" for whatever the user is pointing at).',
      params: { target: { type: 'string', required: true, means: 'node id to select' } },
      run: function (a, ctx) { if (ctx.state) ctx.state.selection = a.target; return { selected: a.target }; },
    },
    {
      id: 'set-value', verb: 'Set value', actionType: 'mutate', icon: 'edit', targets: ['*'],
      description: 'Set one value-slot of the selected node (form, colour, fill, motion, size, depth…).',
      skill: 'The everyday edit. `slot` is one of the node\u2019s value-slots; `value` must be a value of that slot\u2019s axis (the options are resolved live). E.g. set form=octagon, or color=gold.',
      params: {
        slot:  { type: 'string', required: true, from: 'node.valueSlots', means: 'which value-slot' },
        value: { type: 'string', required: true, axisFrom: 'slot', means: 'a value of that slot\u2019s axis' },
        part:  { type: 'string', required: false, means: 'optional sub-part (ring/fill/symbol) to set the slot ON — per-part independence' },
      },
      run: function (a, ctx) {
        var n = ctx.node || (ctx.state && ctx.state.node);
        if (!n) throw new Error('set-value: no target node in ctx.node');
        if (a.part) {
          // per-part write — the value lives on the node's part tree, so ring/fill/
          // symbol stay independent (renderer + projection read the same tree).
          n.parts = n.parts || {};
          n.parts[a.part] = Object.assign({}, n.parts[a.part]);
          var prevp = n.parts[a.part][a.slot];
          n.parts[a.part][a.slot] = a.value;
          return { set: a.part + '.' + a.slot, to: a.value, from: prevp, part: a.part, slot: a.slot };
        }
        var prev = n[a.slot];
        n[a.slot] = a.value; return { set: a.slot, to: a.value, from: prev };
      },
      invert: function (args, result) { return { action: 'set-value', args: { part: args.part, slot: args.slot, value: result.from } }; },
    },
    {
      id: 'add-behaviour', verb: 'Add a behaviour', actionType: 'create', icon: 'decision-tree', targets: ['glyphic', 'mark', '*'],
      description: 'Add a data-driven rule to a glyphic: when a data field meets a condition, change one of its axes. Persisted onto the kind (spec.behaviours) + as a CV_EVENTS trigger, so it travels into real systems.',
      skill: 'Use to make a mark react to its data. field = a data-field slot (the kind\u2019s spec.dataSlots); op = ==/!=/>/<; value = the field value; axis = which look-axis to change; set = the axis value. e.g. when status == error, color = red.',
      params: {
        field: { type: 'string', required: true, means: 'data-field slot' },
        op: { type: 'string', required: true, values: ['==', '!=', '>', '<'], default: '==' },
        value: { type: 'string', required: true, means: 'the field value to match' },
        axis: { type: 'string', required: true, means: 'look-axis to change (color/form/fill/...)' },
        set: { type: 'string', required: true, axisFrom: 'axis', means: 'the axis value to apply' }
      },
      run: function (a, ctx) {
        var kindId = (ctx.node && ctx.node.kindId) || ctx.kind || 'glyphic';
        var k = window.CV_REGISTRY && window.CV_REGISTRY.get(kindId); if (!k) throw new Error('add-behaviour: no kind "' + kindId + '"');
        k.spec = k.spec || {}; k.spec.behaviours = k.spec.behaviours || [];
        var r = { field: a.field, op: a.op, value: a.value, axis: a.axis, set: a.set };
        k.spec.behaviours.push(r);
        if (window.CV_EVENTS && window.CV_EVENTS.register) { try { window.CV_EVENTS.register({ id: 'glyphic.behaviour.' + (k.spec.behaviours.length - 1) + '.' + a.field, on: 'data.change', when: [a.field + ' ' + a.op + ' ' + a.value], do: 'set-value', args: { slot: a.axis, value: a.set }, provenance: 'user', description: 'When ' + a.field + ' ' + a.op + ' ' + a.value + ', set ' + a.axis + ' to ' + a.set + '.' }); } catch (e) {} }
        return { added: r, count: k.spec.behaviours.length };
      },
    },
    {
      id: 'add-data-field', verb: 'Add a data field', actionType: 'define', icon: 'database', targets: ['glyphic', 'mark', '*'],
      description: 'Add a data-field slot (a column a system would fill in) to a glyphic kind, so behaviours can read it. Persisted onto the kind (spec.dataSlots) so it travels.',
      skill: 'Use to declare a new piece of data a mark can react to. field = id (e.g. region); values = the possible values. Then add-behaviour can condition on it.',
      params: {
        field: { type: 'string', required: true, means: 'field id, e.g. region' },
        label: { type: 'string', means: 'human label' },
        values: { type: 'string', raw: true, means: 'JSON array of values, or comma list' }
      },
      run: function (a, ctx) {
        var kindId = (ctx.node && ctx.node.kindId) || ctx.kind || 'glyphic';
        var k = window.CV_REGISTRY && window.CV_REGISTRY.get(kindId); if (!k) throw new Error('add-data-field: no kind "' + kindId + '"');
        var vals = a.values; if (typeof vals === 'string') { try { vals = JSON.parse(vals); } catch (e) { vals = String(vals).split(/[\s,]+/).filter(Boolean); } }
        k.spec = k.spec || {}; k.spec.dataSlots = k.spec.dataSlots || [];
        var f = { field: a.field, label: a.label || a.field, icon: 'hash', values: (vals && vals.length) ? vals : ['yes', 'no'] };
        k.spec.dataSlots.push(f); return { added: f, count: k.spec.dataSlots.length };
      },
    },
    {
      id: 'fill-socket', verb: 'Insert', actionType: 'create', icon: 'plus', targets: ['*'], audience: ['author', 'dev'],
      description: 'Place an occupant into one of the node\u2019s sockets (e.g. a glyphic into a panel\u2019s items).',
      skill: 'Use to compose: put a thing into a socket. `socket` is a socket name; `occupant` is the id of a thing the socket accepts (validate with CV_NODE.accepts).',
      params: {
        socket:   { type: 'string', required: true, from: 'node.sockets' },
        occupant: { type: 'string', required: true, means: 'id of the thing to insert' },
      },
      run: function (a, ctx) {
        var n = ctx.node || (ctx.state && ctx.state.node);
        if (!n) throw new Error('fill-socket: no target node');
        n.filled = n.filled || {}; n.filled[a.socket] = a.occupant; return { filled: a.socket, with: a.occupant };
      },
    },
    {
      id: 'open', verb: 'Open', actionType: 'navigate', icon: 'arrow-right', targets: ['*'], audience: ['author', 'dev'],
      description: 'Follow an event-socket\u2019s address — open/navigate to the thing it points at.',
      skill: 'Use for event-sockets (onClick \u2192 open). Pass the socket\u2019s address.',
      params: { address: { type: 'string', required: true } },
      run: function (a, ctx) { if (ctx.state) ctx.state.open = a.address; return { opened: a.address }; },
    },
    {
      id: 'generate', verb: 'Generate', actionType: 'generate', icon: 'sparkles',
      targets: ['glyphic', 'mark', 'symbol'],
      description: 'Ask Vi to generate candidates for this node (routes through the CV_AI capability that produces its kind).',
      skill: 'Use when the user wants new options (\u201cmake me three drone icons\u201d). Routes to the generatable capability for the node\u2019s kind; never call a model directly.',
      conditions: [],
      params: { brief: { type: 'string', required: false, means: 'what to make' }, count: { type: 'number', default: 4 } },
      run: function (a, ctx) {
        var n = ctx.node || (ctx.state && ctx.state.node) || {};
        var cap = DEC() ? (DEC().decoratorsOf(n.payload || n).find(function (d) { return d.id === 'generatable'; }) || {}).value : null;
        if (!cap) throw new Error('generate: nothing generatable for kind "' + n.kind + '"');
        if (!AI()) throw new Error('generate: CV_AI not loaded');
        return AI().execute(cap, { params: { brief: a.brief, count: a.count }, surface: ctx.surface });
      },
    },
    {
      id: 'remove', verb: 'Remove', actionType: 'remove', icon: 'trash', targets: ['*'],
      description: 'Clear a value-slot (back to its axis default/zero) or empty a socket.',
      skill: 'Use to undo a choice: clear a slot (it returns to its default/zero) or empty a socket.',
      params: { slot: { type: 'string', required: true, from: 'node.valueSlots' } },
      run: function (a, ctx) { var n = ctx.node || (ctx.state && ctx.state.node); if (!n) throw new Error('remove: no node'); var prev = n[a.slot]; delete n[a.slot]; return { cleared: a.slot, from: prev }; },
      invert: function (args, result) { return { action: 'set-value', args: { slot: args.slot, value: result.from } }; },
    },
    {
      id: 'highlight', verb: 'Highlight', actionType: 'ui', icon: 'cursor', targets: ['*'], audience: ['author', 'dev'],
      description: 'Highlight a node in the viewer (a UI effect). Usually fired by an EVENT TRIGGER — e.g. the AI emits where it is looking and a rule highlights it — not called intentionally.',
      skill: 'You rarely call this directly: emit ai.focus and the highlight rule reacts. Pass target=null to clear.',
      params: { target: { type: 'string', required: false, means: 'node id to highlight (null clears)' }, source: { type: 'string', required: false, means: 'ai | user' } },
      run: function (a, ctx) { if (ctx.state) ctx.state.highlight = a.target ? { target: a.target, source: a.source || 'ai' } : null; return { highlight: a.target || null, source: a.source }; },
    },
  ]);

  // ========================================================================
  // META-ACTIONS — build the BACKEND through the interface. Their targets are
  // the REGISTRIES themselves (not a node's classification), so they don't clutter
  // node inspectors; the Studio surfaces them via query({actionType:'define'}).
  // Each writes to the ONE home for what it defines (no second store). This is
  // the system becoming able to grow itself, by its own verbs. (Root Unity.)
  // ========================================================================
  var asArray = function (v) { return Array.isArray(v) ? v : (v == null || v === '' ? [] : String(v).split(/[\s,]+/).filter(Boolean)); };
  registerMany([
    {
      id: 'define-kind', verb: 'Define a kind', actionType: 'define', icon: 'plus', targets: ['system'],
      description: 'Register a NEW kind/part as a Type in CV_REGISTRY — a new distinct role/placement that is still the same one unit (like the Glyphic).',
      skill: 'Use to introduce a new component kind. Give an id; optionally kind/layer/classification. It becomes composable + projectable immediately.',
      params: { id: { type: 'string', required: true }, kind: { type: 'string' }, layer: { type: 'string', default: 'atom' }, classification: { type: 'string', means: 'space/comma list' }, name: { type: 'string' }, description: { type: 'string' } },
      run: function (a) { var R = window.CV_REGISTRY; if (!R) throw new Error('define-kind: CV_REGISTRY not loaded'); R.register({ id: a.id, name: a.name || a.id, kind: a.kind || a.id, layer: a.layer || 'atom', classification: asArray(a.classification), description: a.description || '', provenance: 'user' }); return { defined: a.id }; },
    },
    {
      id: 'add-field', verb: 'Add a field / tag', actionType: 'define', icon: 'tag', targets: ['system'],
      description: 'Add or extend a field on a registry entry (a tag, a classification, any field) — annotate the backend live.',
      skill: 'Use to tag/extend a Type. tags & classification are merged (set-union); any other field is set.',
      params: { target: { type: 'string', required: true, means: 'entry id' }, field: { type: 'string', required: true }, value: { type: 'string', required: true } },
      run: function (a) { var R = window.CV_REGISTRY; var t = R && R.get(a.target); if (!t) throw new Error('add-field: no entry "' + a.target + '"'); var patch = {}; if (a.field === 'tags' || a.field === 'classification') { var cur = Array.isArray(t[a.field]) ? t[a.field] : []; patch[a.field] = Array.from(new Set(cur.concat(asArray(a.value)))); } else patch[a.field] = a.value; R.update(a.target, patch); return { target: a.target, field: a.field, value: patch[a.field] }; },
    },
    {
      id: 'relate', verb: 'Relate (what slots into what)', actionType: 'define', icon: 'link', targets: ['system'],
      description: 'Declare that a Type has a socket accepting a classification — i.e. what can be placed into what. Adds/extends the socket’s accepts.',
      skill: 'Use to wire composition: relate(from=panel, socket=items, accepts=glyphic) means a glyphic can go in a panel’s items. candidatesForSocket then resolves it with no bespoke code.',
      params: { from: { type: 'string', required: true, means: 'type id' }, socket: { type: 'string', required: true }, accepts: { type: 'string', required: true, means: 'classification(s)' } },
      run: function (a) { var R = window.CV_REGISTRY; var t = R && R.get(a.from); if (!t) throw new Error('relate: no type "' + a.from + '"'); var sockets = Object.assign({}, t.sockets || {}); var ex = sockets[a.socket] || { accepts: [] }; var exAcc = Array.isArray(ex.accepts) ? ex.accepts : []; sockets[a.socket] = Object.assign({}, ex, { accepts: Array.from(new Set(exAcc.concat(asArray(a.accepts)))) }); R.update(a.from, { sockets: sockets, slots: sockets }); return { related: a.from + '.' + a.socket, accepts: asArray(a.accepts) }; },
    },
    {
      id: 'define-rule', verb: 'Define a rule', actionType: 'define', icon: 'check-square', targets: ['system'],
      description: 'Attach a condition (a rule, e.g. "texture requires fill != none") to a registry entry. Evaluated everywhere by the one CV_COND engine.',
      skill: 'Use to constrain: define-rule(target=glyphic-ring, condition="texture requires fill != none"). Gates slots/sockets/acceptance identically in validation and the editor.',
      params: { target: { type: 'string', required: true }, condition: { type: 'string', required: true } },
      run: function (a) { var R = window.CV_REGISTRY; var t = R && R.get(a.target); if (!t) throw new Error('define-rule: no entry "' + a.target + '"'); R.update(a.target, { conditions: (t.conditions || []).concat([a.condition]) }); return { target: a.target, rule: a.condition }; },
    },
    {
      id: 'define-decorator', verb: 'Define a decorator', actionType: 'define', icon: 'tag', targets: ['system'],
      description: 'Register a new cross-cutting decorator in the @decorator vocabulary (CV_DECORATORS).',
      skill: 'Use to add a new aspect that can attach to many kinds (e.g. “pinned”, “reviewed”). Give id/group/form/applies.',
      params: { id: { type: 'string', required: true }, group: { type: 'string', default: 'general' }, form: { type: 'string', default: 'marker' }, applies: { type: 'string', default: '*' }, description: { type: 'string' } },
      run: function (a) { var D = window.CV_DECORATORS; if (!D) throw new Error('define-decorator: CV_DECORATORS not loaded'); D.register({ id: a.id, group: a.group, form: a.form, applies: asArray(a.applies), label: a.label || a.id, description: a.description || '', provenance: 'user' }); return { decorator: a.id }; },
    },
    {
      id: 'define-axis', verb: 'Define an axis', actionType: 'define', icon: 'sliders', targets: ['system'],
      description: 'Register a new AXIS (a new visual/semantic dimension) in CV_AXES, with its value units.',
      skill: 'Use to add a dimension every component can subscribe to. Give id + values (comma list, or JSON of {id,label,token}).',
      params: { id: { type: 'string', required: true }, label: { type: 'string' }, values: { type: 'string', required: true, means: 'comma list or JSON array' } },
      run: function (a) { var AXr = window.CV_AXES; if (!AXr) throw new Error('define-axis: CV_AXES not loaded'); var vals; try { vals = a.values.trim()[0] === '[' ? JSON.parse(a.values) : asArray(a.values).map(function (v) { return { id: v }; }); } catch (e) { vals = asArray(a.values).map(function (v) { return { id: v }; }); } AXr.register({ id: a.id, label: a.label || a.id, values: vals }); return { axis: a.id, values: vals.length }; },
    },
    {
      id: 'define-trigger', verb: 'Define a trigger', actionType: 'define', icon: 'sparkles', targets: ['system'],
      description: 'Declare an event→action rule in CV_EVENTS (e.g. on ai.focus do highlight). Reactive wiring, no bespoke code.',
      skill: 'Use to make something react: define-trigger(on=selection.change, do=highlight, args={target:"{{ event.target }}"}).',
      params: { id: { type: 'string', required: true }, on: { type: 'string', required: true }, do: { type: 'string', required: true }, args: { type: 'string', raw: true, means: 'JSON object of value-specs (kept as a template)' } },
      run: function (a) { var E = window.CV_EVENTS; if (!E) throw new Error('define-trigger: CV_EVENTS not loaded'); var args = {}; if (a.args) { try { args = JSON.parse(a.args); } catch (e) {} } E.register({ id: a.id, on: a.on, do: a.do, args: args, provenance: 'user', description: a.description || '' }); return { trigger: a.id }; },
    },
    {
      id: 'define-action', verb: 'Define an action', actionType: 'define', icon: 'play', targets: ['system'],
      description: 'Register a new verb in CV_ACTIONS (declarative; give steps to make it runnable as a macro).',
      skill: 'Use to add a new verb. For a runnable one, pass steps (JSON array of {action,args}) — it becomes a macro.',
      params: { id: { type: 'string', required: true }, verb: { type: 'string' }, actionType: { type: 'string', default: 'mutate' }, targets: { type: 'string', default: '*' }, skill: { type: 'string' }, steps: { type: 'string', raw: true, means: 'JSON array of {action,args}' } },
      run: function (a) { var steps = null; if (a.steps) { try { steps = JSON.parse(a.steps); } catch (e) { throw new Error('define-action: steps must be JSON'); } } register({ id: a.id, verb: a.verb || a.id, actionType: steps ? 'macro' : (a.actionType || 'mutate'), targets: asArray(a.targets).length ? asArray(a.targets) : ['*'], skill: a.skill || '', steps: steps, provenance: 'user' }); return { action: a.id, macro: !!steps }; },
    },
    {
      id: 'define-macro', verb: 'Record a macro', actionType: 'define', icon: 'play', targets: ['system'],
      description: 'Register a recorded chain of action invocations as a NEW action — a Skill that is steps, not a prompt.',
      skill: 'Use to save a repeatable sequence: define-macro(id, steps=[{action,args},…]). Invoking it replays the chain.',
      params: { id: { type: 'string', required: true }, verb: { type: 'string' }, steps: { type: 'string', required: true, raw: true, means: 'JSON array of {action,args}' } },
      run: function (a) { var steps = a.steps; if (typeof steps === 'string') { try { steps = JSON.parse(steps); } catch (e) { throw new Error('define-macro: steps must be a JSON array'); } } register({ id: a.id, verb: a.verb || a.id, actionType: 'macro', steps: steps, targets: ['*'], skill: a.skill || 'A recorded chain of actions.', provenance: 'user' }); return { macro: a.id, steps: (steps || []).length }; },
    },
  ]);

  window.CV_ACTIONS = {
    ACTION_TYPES: ACTION_TYPES,
    register: register, registerMany: registerMany, resolve: resolve, tryResolve: tryResolve,
    all: all, query: query, subscribe: subscribe,
    applicable: applicable, paramOptions: paramOptions, invoke: invoke, inverse: inverse,
  };
})();
