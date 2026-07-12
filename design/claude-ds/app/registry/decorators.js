// app/registry/decorators.js
// ============================================================================
// CV_DECORATORS — the @decorator VOCABULARY (the seventh single-source registry).
//
// Idea (Info/Tim): "a @decorators vocabulary so it's easy to search / find / use
// — and other things decorators can do — then a registry for it, retrospectively."
//
// WHAT A DECORATOR IS
// -------------------
// Where a node's KIND answers "what IS this" (glyphic / panel / slide / token),
// a DECORATOR answers "what is ALSO TRUE of this, or what can it ALSO do." It is
// a CROSS-CUTTING annotation that attaches to many kinds of node without being
// part of their structural identity. The system was already full of these —
// scattered and un-named:
//   provenance · classification · tags · layer · axis · zero · token · optional ·
//   multiple · event · address · accepts · conditions · means · @dsCard · @template
// This registry is their ONE catalogue. It is RETROSPECTIVE: it does NOT copy any
// value out of a node — each decorator carries a `derive(node)` that READS the
// value from the node's existing field. The vocabulary lives here; the values
// stay in their single home. (CLAUDE.md: no second home for any value.)
//
// WHAT DECORATORS CAN DO ("other things")
// ---------------------------------------
//   · FIND   — every decorator is searchable: find({decorator,value}) locates
//              every node carrying it. "all Vi-made things", "everything that
//              counts as a glyphic", "everything Vi can generate".
//   · GATE   — a `condition` decorator carries a CV_COND rule; behaviour() evals it.
//   · GENERATE — a `generatable` decorator names a CV_AI capability; behaviour()
//              routes to CV_AI.execute (never the raw model).
//   · EDIT   — an `editable` decorator names the fields an inspector should expose.
//   · ACCEPT — a socket may `requires`/`forbids` decorators; CV_NODE.accepts honours it.
//
// Mirrors the other registries' shape: register / resolve / all / query /
// subscribe, plus decoratorsOf / applicable / find / decorate / parseAnnotations.
//
// Load AFTER conditions.js (uses CV_COND for the condition decorator's behaviour);
// CV_REGISTRY / CV_AI are read lazily (optional). Pure + window-assigning.
// ============================================================================
(function () {
  'use strict';

  var COND = function () { return window.CV_COND; };
  var REG  = function () { return window.CV_REGISTRY; };
  var AI   = function () { return window.CV_AI; };

  // forms a decorator can take (how it reads / what UI it implies)
  var FORMS = {
    identity:  'the node\u2019s own kind/layer identity',
    enum:      'one value from a fixed set',
    'tag-set': 'a set of free or typed labels',
    marker:    'present-or-absent (a flag)',
    ref:       'a pointer to another entry (id / address / token)',
    note:      'a human semantic note',
    behaviour: 'carries a runnable behaviour (gate / generate / edit)',
    annotation:'a source-level @tag on a file',
  };

  // "What is generatable" is NOT a hardcoded map (that was a class problem). It
  // is DERIVE-BY-QUERY (CV_QUERY.relation): the capability that declares it
  // `generates` this node's kind/classification — its single source. The SAME
  // pattern dissolves every "kind → thing" map across the system (see query.js).
  function generatorFor(n) {
    if (n && n.generatable) return n.generatable;            // explicit per-node override
    var Q = window.CV_QUERY;
    if (Q) return Q.relation(n, { from: 'ai', field: 'generates' });
    // fallback if CV_QUERY isn't loaded: query CV_AI directly (same logic)
    var ai = AI(); if (!ai || !ai.query) return undefined;
    var cls = [n && n.kind].concat((n && n.classification) || []).filter(Boolean);
    var hit = ai.query({ layer: 'capability' }).find(function (c) {
      return (c.generates || []).some(function (g) { return cls.indexOf(g) >= 0; });
    });
    return hit ? hit.id : undefined;
  }

  var byId = {};
  var order = [];
  var listeners = new Set();

  function notify() { listeners.forEach(function (fn) { try { fn(); } catch (e) {} }); }

  function normalize(d) {
    if (!d || !d.id) throw new Error('CV_DECORATORS: a decorator needs an id');
    return {
      id: d.id,
      label: d.label || d.id,
      description: d.description || '',
      form: d.form || 'marker',
      // which nodes this decorator can apply to: '*' or kinds/layers/'socket'/'value'/'file'
      applies: d.applies || ['*'],
      // value space hint (enum options, 'string', 'string[]', etc.) — for editors
      value: d.value || null,
      searchable: d.searchable !== false,
      group: d.group || 'general',
      // who this decorator is FOR. The seeded decorators are all technical, so
      // they default to author/dev — a regular 'maker' never sees raw provenance/
      // classification/intrinsic chips. Tag a decorator ['maker'] to surface it.
      audience: d.audience || ['author', 'dev'],
      // derive(node) → the value present on the node (READS its single-source field)
      derive: typeof d.derive === 'function' ? d.derive : null,
      // behaviour(node, ctx) → runs the decorator's action (gate/generate/edit)
      behaviour: typeof d.behaviour === 'function' ? d.behaviour : null,
      provenance: d.provenance || 'built-in',
    };
  }

  function register(d) {
    var n = normalize(d);
    if (!byId[n.id]) order.push(n.id);
    byId[n.id] = n;
    notify();
    return n;
  }
  function resolve(id) { var d = byId[id]; if (!d) throw new Error('CV_DECORATORS: no decorator "' + id + '" (have: ' + order.join(', ') + ')'); return d; }
  function tryResolve(id) { return byId[id] || null; }
  function all() { return order.map(function (id) { return byId[id]; }); }

  function query(q) {
    q = q || {};
    var out = all();
    if (q.form) out = out.filter(function (d) { return d.form === q.form; });
    if (q.group) out = out.filter(function (d) { return d.group === q.group; });
    if (q.applies) out = out.filter(function (d) { return matchesApplies(d, { kind: q.applies }); });
    if (q.behaviour) out = out.filter(function (d) { return !!d.behaviour; });
    if (q.search) {
      var s = String(q.search).toLowerCase();
      out = out.filter(function (d) { return d.id.indexOf(s) >= 0 || d.label.toLowerCase().indexOf(s) >= 0 || d.description.toLowerCase().indexOf(s) >= 0; });
    }
    return out;
  }

  function subscribe(fn) { listeners.add(fn); return function () { listeners.delete(fn); }; }

  // -- does decorator def `d` apply to `node`? (by kind / layer / pseudo-kind) --
  function nodeKinds(node) {
    if (!node) return [];
    var ks = [];
    if (node.kind) ks.push(node.kind);
    if (node.layer) ks.push(node.layer);
    if (node.__file) ks.push('file');
    // a socket-entry (from socketsOf) is recognised by having `accepts`/`address`
    if (node.accepts !== undefined || node.address !== undefined || node.onPick !== undefined) ks.push('socket');
    if (node.token !== undefined || node.axisValue !== undefined) ks.push('value');
    return ks;
  }
  function matchesApplies(d, node) {
    if (d.applies.indexOf('*') >= 0) return true;
    var ks = nodeKinds(node);
    return d.applies.some(function (a) { return ks.indexOf(a) >= 0; });
  }

  // -- THE retrospective read: which decorators are PRESENT on a node, derived
  //    from its existing fields (never copied — derive() reads the field). --
  function decoratorsOf(node) {
    if (!node) return [];
    var out = [];
    all().forEach(function (d) {
      if (!d.derive) return;
      var v;
      try { v = d.derive(node); } catch (e) { v = undefined; }
      if (v !== undefined && v !== null && !(Array.isArray(v) && v.length === 0) && v !== false) {
        out.push({ id: d.id, value: v, def: d });
      }
    });
    // explicitly-attached decorators with no field home live in node.decorators
    if (node.decorators) Object.keys(node.decorators).forEach(function (k) {
      if (!out.some(function (o) { return o.id === k; })) out.push({ id: k, value: node.decorators[k], def: tryResolve(k) });
    });
    return out;
  }

  // -- which decorators COULD apply to this node (for an editor's empty slots) --
  function applicable(node) { return all().filter(function (d) { return matchesApplies(d, node); }); }

  // -- attach a decorator. If it has a field home, the caller should set that
  //    field; for home-less decorators we stash on node.decorators (single place). --
  function decorate(node, id, value) {
    resolve(id); // throws if unknown — loud
    node.decorators = node.decorators || {};
    node.decorators[id] = value === undefined ? true : value;
    return node;
  }

  // -- SEARCH: every node in `pool` carrying decorator `q.decorator` (optionally
  //    == q.value). pool defaults to the whole Type registry. The find payoff. --
  function find(q, pool) {
    q = q || {};
    var items = pool || (REG() && REG().all ? REG().all() : []);
    var want = q.decorator, val = q.value;
    return items.filter(function (it) {
      var decs = decoratorsOf(it);
      return decs.some(function (dd) {
        if (dd.id !== want) return false;
        if (val === undefined) return true;
        if (Array.isArray(dd.value)) return dd.value.indexOf(val) >= 0;
        return dd.value === val;
      });
    });
  }

  // -- run a decorator's behaviour on a node (gate / generate / edit) --
  function run(id, node, ctx) {
    var d = resolve(id);
    if (!d.behaviour) throw new Error('CV_DECORATORS: "' + id + '" has no behaviour to run');
    return d.behaviour(node, ctx || {});
  }

  // -- parse source @annotations (the @dsCard / @template family) from a string --
  function parseAnnotations(text) {
    if (!text) return [];
    var ann = all().filter(function (d) { return d.form === 'annotation'; }).map(function (d) { return d.id; });
    var out = [];
    var re = /@([A-Za-z][\w-]*)\b([^\n>]*)/g, m;
    while ((m = re.exec(text))) { if (ann.indexOf(m[1]) >= 0) out.push({ id: m[1], raw: (m[2] || '').trim() }); }
    return out;
  }

  // ========================================================================
  // RETROSPECTIVE SEED — the vocabulary already in use, catalogued. Each derive
  // READS the node's existing single-source field; nothing is duplicated.
  // ========================================================================
  [
    // ---- identity / classification ----
    { id: 'kind', group: 'identity', form: 'identity', applies: ['*'],
      label: 'Kind', description: 'The universal-component kind this node is an instance of.',
      derive: function (n) { return n.kind || undefined; } },
    { id: 'layer', group: 'identity', form: 'enum', value: ['token','atom','block','system','surface','doc','template'], applies: ['*'],
      label: 'Layer', description: 'Where the node sits in the atomic-composition ladder.',
      derive: function (n) { return n.layer || undefined; } },
    { id: 'classification', group: 'identity', form: 'tag-set', applies: ['*'],
      label: 'Classification', description: 'The labels other components\u2019 sockets accept this node AS.',
      derive: function (n) { return (n.classification && n.classification.length) ? n.classification : undefined; } },
    { id: 'tags', group: 'identity', form: 'tag-set', applies: ['*'],
      label: 'Tags', description: 'Free-form search labels.',
      derive: function (n) { return (n.tags && n.tags.length) ? n.tags : undefined; } },

    // ---- provenance / lifecycle ----
    { id: 'provenance', group: 'lifecycle', form: 'enum', value: ['built-in','user','vi','imported'], applies: ['*'],
      label: 'Provenance', description: 'Who authored this — built-in, the user, Vi, or imported.',
      derive: function (n) { return n.provenance || undefined; } },
    { id: 'forkedFrom', group: 'lifecycle', form: 'ref', applies: ['*'],
      label: 'Forked from', description: 'The built-in this user/Vi entry was forked from.',
      derive: function (n) { return n.forkedFrom || undefined; } },
    { id: 'deprecated', group: 'lifecycle', form: 'marker', applies: ['*'],
      label: 'Deprecated', description: 'Kept for consumers but no longer recommended; value may name a replacement.',
      derive: function (n) { return n.deprecated || undefined; } },
    { id: 'experimental', group: 'lifecycle', form: 'marker', applies: ['*'],
      label: 'Experimental', description: 'In development, not yet stable (e.g. the Glyphic foundry UI).',
      derive: function (n) { return n.experimental || undefined; } },

    // ---- axis / value (tokens are the value-units of an axis) ----
    { id: 'axis', group: 'axis', form: 'ref', applies: ['*'],
      label: 'Axis', description: 'Which axis this node is a typed value-unit of.',
      derive: function (n) { return n.axis || undefined; } },
    { id: 'token', group: 'axis', form: 'ref', applies: ['value','token'],
      label: 'Token', description: 'The CSS token this value canonically is (var(--token)).',
      derive: function (n) { return (n.payload && n.payload.token) || n.token || undefined; } },
    { id: 'zero', group: 'axis', form: 'marker', applies: ['value','token'],
      label: 'Zero', description: 'The zero of an axis — no ring (0 sides), \u03b1-0 fill, no texture, no motion.',
      derive: function (n) { return ((n.payload && n.payload.zero) || n.zero) ? true : undefined; } },

    // ---- socket / slot decorators ----
    { id: 'optional', group: 'socket', form: 'marker', applies: ['socket'],
      label: 'Optional', description: 'A socket that need not be filled.',
      derive: function (n) { return n.optional ? true : undefined; } },
    { id: 'multiple', group: 'socket', form: 'marker', applies: ['socket'],
      label: 'Multiple', description: 'A socket that holds many occupants (e.g. a panel\u2019s items).',
      derive: function (n) { return n.multiple ? true : undefined; } },
    { id: 'event', group: 'socket', form: 'enum', value: ['click','hover','open','submit'], applies: ['socket'],
      label: 'Event', description: 'An event-socket: the attachment is a trigger (onClick \u2192 open), not a slot.',
      derive: function (n) { return (n.kind === 'event' || n.event) ? (n.event || 'click') : undefined; } },
    { id: 'address', group: 'socket', form: 'ref', applies: ['socket'],
      label: 'Address', description: 'A stable pointer to the occupying component \u2014 referenced, never copied.',
      derive: function (n) { return n.address || undefined; } },
    { id: 'accepts', group: 'socket', form: 'tag-set', applies: ['socket'],
      label: 'Accepts', description: 'What a socket admits \u2014 an axis (value-socket) or classifications (thing-socket).',
      derive: function (n) { return (n.accepts !== undefined) ? n.accepts : undefined; } },
    { id: 'means', group: 'socket', form: 'note', applies: ['socket','*'],
      label: 'Means', description: 'A human note on what a slot/socket signifies.',
      derive: function (n) { return n.means || undefined; } },

    // ---- behaviour decorators (the "other things decorators can do") ----
    { id: 'condition', group: 'behaviour', form: 'behaviour', applies: ['*','socket'],
      label: 'Condition', description: 'A rule that gates this thing (\u201ctexture requires fill != none\u201d), evaluated by CV_COND.',
      derive: function (n) { var c = n.conditions; return (c && c.length) ? c : undefined; },
      behaviour: function (n, ctx) { return COND() ? COND().testAll(n.conditions || [], ctx || {}) : true; } },
    { id: 'intrinsic', group: 'behaviour', form: 'marker', applies: ['*'],
      label: 'Intrinsic meaning', description: 'Meaning is intrinsic (a symbol is always itself) \u2014 never governed by a loadable meaning profile.',
      derive: function (n) { return (n.kind === 'symbol' || (n.classification || []).indexOf('symbol') >= 0 || (n.conditions || []).some(function (c) { return /intrinsic/i.test(String(c)); })) ? true : undefined; } },
    { id: 'generatable', group: 'behaviour', form: 'behaviour', value: 'CV_AI capability id', applies: ['*'],
      label: 'Generatable', description: 'Vi can generate this; value is the CV_AI capability. behaviour() routes through CV_AI.execute \u2014 never the raw model.',
      derive: function (n) { return generatorFor(n); },
      behaviour: function (n, ctx) { var cap = generatorFor(n); if (!AI()) throw new Error('generatable: CV_AI not loaded'); if (!cap) throw new Error('generatable: no CV_AI capability generates kind "' + n.kind + '"'); return AI().execute(cap, ctx || {}); } },
    { id: 'editable', group: 'behaviour', form: 'behaviour', applies: ['*'],
      label: 'Editable', description: 'The value-slots an inspector should expose for direct editing.',
      derive: function (n) { var k = n.valueSlots ? Object.keys(n.valueSlots) : []; return k.length ? k : undefined; },
      behaviour: function (n) { return n.valueSlots ? Object.keys(n.valueSlots) : []; } },

    // ---- source-level @annotations (the existing @tag family) ----
    { id: 'dsCard', group: 'annotation', form: 'annotation', applies: ['file'],
      label: '@dsCard', description: 'Marks an HTML file as a Design-System tab card (group / name / subtitle / viewport).' },
    { id: 'template', group: 'annotation', form: 'annotation', applies: ['file'],
      label: '@template', description: 'Marks a .dc.html as a copyable template entry (name / description).' },
  ].forEach(register);

  window.CV_DECORATORS = {
    FORMS: FORMS,
    register: register, resolve: resolve, tryResolve: tryResolve, all: all,
    query: query, subscribe: subscribe,
    decoratorsOf: decoratorsOf, applicable: applicable, decorate: decorate,
    find: find, run: run, parseAnnotations: parseAnnotations,
    matchesApplies: matchesApplies,
  };
})();
