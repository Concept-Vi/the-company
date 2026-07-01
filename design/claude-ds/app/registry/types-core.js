// app/registry/types-core.js
// Universal Type Registry — single source of truth for every composable
// definition in ConceptV Studio. Atomic-composition model: Types stack from
// Tokens up to Templates, can extend one another, and can EMBED other Types
// through named slots.
//
// One node shape, everywhere. The same engine drives the Widget kind picker,
// the Wizard step picker, the slide block library, the Templates browser,
// and the in-place Vi composer.
//
// === Layers (low → high, atomic composition) =================================
//   token    Design primitive: a colour, type token, spacing step, motif.
//   atom     Single visual unit: an icon glyph, a status dot, a stamp.
//   block    Composable content unit: KPI tile, sparkline, hero, callout.
//   system   A composition rule over blocks: kpi-set, media-led, hybrid.
//   surface  A framed container with context: dashboard tile, hub panel,
//            wizard step kind, slide layout.
//   doc      Top-level document Type: deck, brochure, widget, wizard, …
//   template A doc bound with extracted variables (a re-runnable instance).
//
// === Schema ==================================================================
// Type = {
//   id            kebab-case stable id
//   name          display name
//   layer         one of LAYERS
//   family        loose grouping: 'widget'|'wizard'|'deck'|'brochure'|
//                 'block'|'icon'|'token'|'wizard-step'|'system'|…
//   description   1-2 sentence summary
//   extends       parent type id (single-inheritance) | null
//   slots         { [name]: { label, accepts, multiple?, default?, optional? } }
//                  accepts = { layers?:string[], families?:string[], tags?:string[] }
//   defaults      default data blob (the schema "shape")
//   variables     [{ key, label, default, kind:'text'|'number'|'url'|'choice', options? }]
//                  used by Templates to surface re-runnable parameters
//   tags          string[] — free-form, used in filter chips
//   provenance    'built-in' | 'user' | 'vi' | 'imported'
//   icon          CV icon name for the registry tile
//   render        OPTIONAL function — only built-ins set this; user/Vi-authored
//                 types fall back to a generic block renderer based on `defaults`
//   createdAt, updatedAt
//   version       monotonically increasing on edit
// }

(function () {
  const LAYERS = ['token', 'atom', 'block', 'system', 'surface', 'doc', 'template'];
  const LAYER_INFO = {
    token:    { label: 'Token',    rank: 0, swatch: '#E0C010', desc: 'Design primitive — colour, type, spacing, motif.' },
    atom:     { label: 'Atom',     rank: 1, swatch: '#B7973C', desc: 'Single visual unit — icon, dot, stamp.' },
    block:    { label: 'Block',    rank: 2, swatch: '#988058', desc: 'Composable content unit — KPI, sparkline, hero, callout.' },
    system:   { label: 'System',   rank: 3, swatch: '#7E6539', desc: 'Composition rule over blocks — kpi-set, media-led, hybrid.' },
    surface:  { label: 'Surface',  rank: 4, swatch: '#5B4628', desc: 'Framed container with context — tile, panel, slide, step.' },
    doc:      { label: 'Doc',      rank: 5, swatch: '#3D2F1B', desc: 'Top-level document Type — deck, brochure, widget, wizard.' },
    template: { label: 'Template', rank: 6, swatch: '#1F1A12', desc: 'A doc bound with extracted variables — a re-runnable instance.' },
  };

  const STORAGE_KEY = 'cv:registry:user-types';
  const TEMPLATES_KEY = 'cv:registry:templates';
  const listeners = new Set();
  let suppressNotify = false;

  // ---------------------------------------------------------------------------
  // Storage — built-ins live in memory; user/vi/imported persisted to LS
  // ---------------------------------------------------------------------------
  const BUILTIN = new Map();   // id -> Type
  const USER = new Map();      // id -> Type
  const TEMPLATES = new Map(); // id -> Template (which is also a Type at layer=template)

  function loadFromStorage() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const arr = JSON.parse(raw);
        for (const t of arr) USER.set(t.id, t);
      }
    } catch {}
    try {
      const raw = localStorage.getItem(TEMPLATES_KEY);
      if (raw) {
        const arr = JSON.parse(raw);
        for (const t of arr) TEMPLATES.set(t.id, t);
      }
    } catch {}
  }
  function saveUserTypes() {
    try {
      const arr = [...USER.values()];
      localStorage.setItem(STORAGE_KEY, JSON.stringify(arr));
    } catch {}
  }
  function saveTemplates() {
    try {
      const arr = [...TEMPLATES.values()];
      localStorage.setItem(TEMPLATES_KEY, JSON.stringify(arr));
    } catch {}
  }

  // ---------------------------------------------------------------------------
  // Registry API
  // ---------------------------------------------------------------------------
  function register(type, opts = {}) {
    const t = normalize(type);
    if (!t.id) { console.warn('[Registry] type missing id', type); return null; }
    if (t.provenance === 'built-in') BUILTIN.set(t.id, t);
    else if (t.layer === 'template') TEMPLATES.set(t.id, t);
    else USER.set(t.id, t);
    if (!opts.silent) {
      if (t.provenance !== 'built-in') {
        if (t.layer === 'template') saveTemplates(); else saveUserTypes();
      }
      notify();
    }
    return t;
  }

  function registerMany(types, opts = {}) {
    suppressNotify = true;
    try { for (const t of types) register(t, { silent: true }); }
    finally { suppressNotify = false; }
    // persist once
    if (!opts.silent) {
      saveUserTypes(); saveTemplates();
      notify();
    }
  }

  function update(id, patch, opts = {}) {
    const cur = get(id);
    if (!cur) return null;
    if (cur.provenance === 'built-in') {
      // built-ins forked into user space on edit
      const forked = {
        ...cur, ...patch,
        id: cur.id,
        provenance: 'user',
        forkedFrom: cur.id,
        updatedAt: Date.now(),
        version: (cur.version || 1) + 1,
      };
      return register(forked, opts);
    }
    const next = { ...cur, ...patch, updatedAt: Date.now(), version: (cur.version || 1) + 1 };
    return register(next, opts);
  }

  function remove(id, opts = {}) {
    if (BUILTIN.has(id)) return false; // can't remove built-ins
    let removed = false;
    if (USER.delete(id)) removed = true;
    if (TEMPLATES.delete(id)) removed = true;
    if (removed && !opts.silent) { saveUserTypes(); saveTemplates(); notify(); }
    return removed;
  }

  function get(id) {
    if (!id) return null;
    return USER.get(id) || BUILTIN.get(id) || TEMPLATES.get(id) || null;
  }

  function all() {
    return [...BUILTIN.values(), ...USER.values(), ...TEMPLATES.values()];
  }

  function query({ layer, layers, family, families, tags, provenance, extendsId, search } = {}) {
    let out = all();
    if (layer) out = out.filter(t => t.layer === layer);
    if (layers && layers.length) out = out.filter(t => layers.includes(t.layer));
    if (family) out = out.filter(t => t.family === family);
    if (families && families.length) out = out.filter(t => families.includes(t.family));
    if (provenance) out = out.filter(t => t.provenance === provenance);
    if (extendsId) out = out.filter(t => t.extends === extendsId);
    if (tags && tags.length) out = out.filter(t => (t.tags || []).some(x => tags.includes(x)));
    if (search) {
      const q = search.toLowerCase();
      out = out.filter(t =>
        t.id.includes(q) ||
        (t.name || '').toLowerCase().includes(q) ||
        (t.description || '').toLowerCase().includes(q) ||
        (t.tags || []).some(x => x.toLowerCase().includes(q))
      );
    }
    return out.sort(byLayerThenName);
  }

  function byLayerThenName(a, b) {
    const da = LAYER_INFO[a.layer]?.rank ?? 99;
    const db = LAYER_INFO[b.layer]?.rank ?? 99;
    if (da !== db) return da - db;
    return (a.name || '').localeCompare(b.name || '');
  }

  // ---------------------------------------------------------------------------
  // Inheritance resolution — flatten a Type with its ancestors
  // ---------------------------------------------------------------------------
  function resolve(id) {
    const chain = lineage(id);
    if (!chain.length) return null;
    // Merge from root → leaf so leaf wins
    const merged = chain.reduceRight((acc, t) => {
      return {
        ...acc, ...t,
        defaults: { ...(acc.defaults || {}), ...(t.defaults || {}) },
        slots: { ...(acc.slots || {}), ...(t.slots || {}) },
        variables: mergeVariables(acc.variables, t.variables),
        tags: [...new Set([...(acc.tags || []), ...(t.tags || [])])],
      };
    }, {});
    merged.lineage = chain.map(t => t.id);
    merged.id = chain[0].id;
    merged.name = chain[0].name;
    merged.provenance = chain[0].provenance;
    return merged;
  }

  function lineage(id) {
    const out = [];
    const seen = new Set();
    let cur = get(id);
    while (cur && !seen.has(cur.id)) {
      seen.add(cur.id);
      out.push(cur);
      cur = cur.extends ? get(cur.extends) : null;
    }
    return out; // [self, parent, grandparent, …]
  }

  function children(id) {
    return all().filter(t => t.extends === id);
  }

  function descendants(id) {
    const out = [];
    const walk = (pid) => {
      for (const c of children(pid)) { out.push(c); walk(c.id); }
    };
    walk(id);
    return out;
  }

  function mergeVariables(a = [], b = []) {
    const map = new Map();
    for (const v of a) map.set(v.key, v);
    for (const v of b) map.set(v.key, { ...map.get(v.key), ...v });
    return [...map.values()];
  }

  // ---------------------------------------------------------------------------
  // Embed validation — can Type X be dropped into a slot/socket accepting Y?
  // ---------------------------------------------------------------------------
  function accepts(slot, type, ctx) {
    if (!slot || !type) return false;
    // socket-level conditions (e.g. only accept when some state holds) — shared
    // evaluator so the rule is the same in validation and in the editor UI.
    if (slot.conditions && window.CV_COND && !window.CV_COND.testAll(slot.conditions, ctx || {})) return false;
    const acc = slot.accepts || {};
    // classification-based acceptance (the universal-component path): a socket
    // lists the classifications it admits; a type lists what it's classified as.
    if (Array.isArray(acc)) {
      const cls = type.classification || [type.kind, type.family].filter(Boolean);
      return acc.some(a => cls.includes(a));
    }
    if (acc.classification?.length) {
      const cls = type.classification || [type.kind, type.family].filter(Boolean);
      if (!acc.classification.some(a => cls.includes(a))) return false;
    }
    if (acc.forbid?.length) {
      const cls = type.classification || [type.kind, type.family].filter(Boolean);
      if (acc.forbid.some(a => cls.includes(a))) return false;
    }
    if (acc.layers?.length && !acc.layers.includes(type.layer)) return false;
    if (acc.families?.length && !acc.families.includes(type.family)) return false;
    if (acc.tags?.length && !(type.tags || []).some(t => acc.tags.includes(t))) return false;
    return true;
  }

  function candidatesForSlot(slot, ctx) {
    return all().filter(t => accepts(slot, t, ctx));
  }
  // socket is the universal-component word for a type-accepting slot.
  const candidatesForSocket = candidatesForSlot;

  // is a (value or type) slot ENABLED given the current ctx? Reads the slot's
  // own conditions through the shared evaluator. Used by editors to grey-out a
  // slot (e.g. texture disabled while fill == none).
  function slotEnabled(slot, ctx) {
    if (!slot || !slot.conditions) return true;
    return window.CV_COND ? window.CV_COND.testAll(slot.conditions, ctx || {}) : true;
  }

  // resolve a SOCKET's kind/address (event-sockets, slice B). A socket may be a
  // spatial slot (kind:'slot', the default) or an event trigger (kind:'event',
  // e.g. onClick→open), and carries an `address` pointing at the occupying Type.
  function socketInfo(socket) {
    if (!socket) return null;
    return {
      kind: socket.kind || 'slot',          // 'slot' | 'event'
      event: socket.event || null,           // e.g. 'click' for event-sockets
      address: socket.address || null,       // stable ref to the occupant Type
      onPick: socket.onPick || null,         // what happens when filled ('insert'|'open'|…)
      multiple: !!socket.multiple,
      optional: !!socket.optional,
      accepts: socket.accepts || {},
      conditions: socket.conditions || [],
    };
  }

  // ---------------------------------------------------------------------------
  // Normalize — fill in defaults, stamp timestamps
  // ---------------------------------------------------------------------------
  function normalize(t) {
    const now = Date.now();
    return {
      id: t.id,
      name: t.name || t.id,
      layer: t.layer || 'block',
      family: t.family || 'block',
      // 'kind' = which universal-component KIND this Type is an instance of
      // (glyphic | panel | graph | slide | …). Distinct from family/layer; it is
      // the answer to "what one thing is this an infinite-variation of".
      kind: t.kind || null,
      // 'classification' = the labels OTHER components' sockets accept it AS.
      // (a glyphic is classified ['glyphic','mark']; a panel socket accepting
      // 'glyphic' will admit it). Defaults to include its own kind + family.
      classification: t.classification || [t.kind, t.family].filter(Boolean),
      description: t.description || '',
      extends: t.extends || null,
      // slots: type-accepting attachment points (the registry's original sense).
      // These ARE "sockets" in the Glyphic-spec vocabulary; `sockets` is a
      // first-class alias so new declarations can use the clearer word.
      slots: t.slots || t.sockets || {},
      sockets: t.sockets || t.slots || {},
      // valueSlots: value-taking parameters (a token/axis value, not a Type).
      // The "slots" of the Glyphic-spec vocabulary. { [name]:{ vocab, default,
      // zero?, conditions? } } — vocab names a single-source value space.
      valueSlots: t.valueSlots || {},
      // parts: named sub-components, each its own mini-declaration
      // { [name]: { valueSlots?, sockets?, conditions? } }.
      parts: t.parts || {},
      // conditions: free rules governing slots/sockets (strings or predicates).
      conditions: t.conditions || [],
      // axis reconciliation: a token Type may name the AXIS + value it is a unit
      // of (token.color.gold → axis 'color', value 'gold'), so tokens and axes
      // are one model (tokens ARE the value-units of an axis).
      axis: t.axis || null,
      axisValue: t.axisValue || null,
      defaults: t.defaults || {},
      variables: t.variables || [],
      tags: t.tags || [],
      provenance: t.provenance || 'user',
      icon: t.icon || 'check-square',
      render: t.render, // may be a function or undefined
      createdAt: t.createdAt || now,
      updatedAt: t.updatedAt || now,
      version: t.version || 1,
      forkedFrom: t.forkedFrom || null,
      // Optional: pointer back to a built-in seed runtime (for hybrid rendering)
      runtime: t.runtime || null,
    };
  }

  // ---------------------------------------------------------------------------
  // Subscriptions — for React hooks
  // ---------------------------------------------------------------------------
  function subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); }
  function notify() { if (suppressNotify) return; for (const fn of listeners) try { fn(); } catch {} }

  // ---------------------------------------------------------------------------
  // Public surface
  // ---------------------------------------------------------------------------
  window.CV_REGISTRY = {
    LAYERS, LAYER_INFO,
    register, registerMany, update, remove,
    get, all, query, resolve, lineage, children, descendants,
    accepts, candidatesForSlot, candidatesForSocket, slotEnabled, socketInfo,
    subscribe,
    // direct access for diagnostics
    _builtin: BUILTIN, _user: USER, _templates: TEMPLATES,
  };

  loadFromStorage();
})();
