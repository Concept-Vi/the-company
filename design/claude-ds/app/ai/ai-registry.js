// app/ai/ai-registry.js
// ============================================================================
// CV_AI — the Universal AI Registry.
//
// The AI layer expressed in the SAME shape as everything else in the unified
// system (cf. app/registry/types-core.js → CV_REGISTRY, core/RenderType.jsx).
// Where CV_REGISTRY answers "what can be composed?", CV_AI answers "what can Vi
// DO, with what, knowing where it is?" — and it does so the same way: a single
// hierarchical registry of parametric, inheritable, resolvable entries, with
// the running interface a *projection* of the registry rather than a parallel
// pile of hand-written functions.
//
// Generative discipline (identical to the rest of the system):
//   ai-output = f(capability, context, params)
// A capability is NOT a bespoke function with an inline prompt. It is a Type:
// it declares which behaviours it composes, which provider it runs on, what
// params (dials) it takes, and how to build its prompt from (resolved context
// + behaviours + params). Add a new AI move = register data, not write code.
//
// === Layers (low → high, atomic composition) ===============================
//   provider   A model endpoint: claude (text/stream), openai-image (image).
//              Capabilities + inference, exactly like the type system's tokens.
//   behaviour  A reusable instruction fragment composed INTO prompts: the
//              ConceptV voice, an "angle" (shorter/formal/specific), a persona.
//   skill      A named parametric intent a user can invoke (the doc transforms:
//              shorten / urgent / audit / …). Binds to a capability + params.
//   capability A tool: one generative operation (insert.block, alternate.block,
//              theme.generate, field.alternate, …). Composes behaviours, picks
//              a provider, resolves context, builds a prompt, parses candidates.
//   context    A resolver keyed by surface: projects "what screen Vi is on"
//              (deck / widget / wizard / brochure + selection) into the compact
//              context object every capability's prompt is built from.
//
// One registry, every surface. The composer, the chat rail, the field toolbar,
// the registry inspector and any future surface all resolve the SAME catalogue
// and the SAME live context — so the AI and the interface are synchronised by
// construction (they read one source), not by hand.
//
// Mirrors CV_REGISTRY's API surface verbatim so the two registries are learnable
// as one: register/registerMany/update/remove/get/all/query/resolve/lineage/
// subscribe, LS-persisted user/vi provenance, built-ins in memory.
// ============================================================================

(function () {
  const LAYERS = ['provider', 'behaviour', 'skill', 'capability', 'context'];
  const LAYER_INFO = {
    provider:   { label: 'Provider',   rank: 0, swatch: '#E0C010', desc: 'Model endpoint — claude (text/stream), openai (image).' },
    behaviour:  { label: 'Behaviour',  rank: 1, swatch: '#B7973C', desc: 'Reusable instruction fragment composed into prompts — voice, angle, persona.' },
    skill:      { label: 'Skill',      rank: 2, swatch: '#988058', desc: 'Named parametric intent a user invokes — shorten, urgent, audit.' },
    capability: { label: 'Capability', rank: 3, swatch: '#7E6539', desc: 'A tool — one generative operation. Composes behaviours, picks a provider.' },
    context:    { label: 'Context',    rank: 4, swatch: '#5B4628', desc: 'Surface-keyed resolver — projects the current screen into Vi’s operating context.' },
  };

  const STORAGE_KEY = 'cv:ai-registry:user-entries';
  const listeners = new Set();
  let suppressNotify = false;

  // Built-ins live in memory (re-seeded each load); user/vi persisted to LS.
  const BUILTIN = new Map();
  const USER = new Map();

  function loadFromStorage() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) for (const t of JSON.parse(raw)) USER.set(t.id, t);
    } catch {}
  }
  function saveUser() {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify([...USER.values()])); } catch {}
  }

  // ---------------------------------------------------------------------------
  // Registry API — mirrors CV_REGISTRY
  // ---------------------------------------------------------------------------
  function register(entry, opts = {}) {
    const t = normalize(entry);
    if (!t.id) { throw new Error('[CV_AI] entry missing id: ' + JSON.stringify(entry).slice(0, 120)); }
    if (!LAYERS.includes(t.layer)) { throw new Error('[CV_AI] entry "' + t.id + '" has unknown layer "' + t.layer + '" (expected one of ' + LAYERS.join('/') + ')'); }
    if (t.provenance === 'built-in') BUILTIN.set(t.id, t);
    else USER.set(t.id, t);
    if (!opts.silent) { if (t.provenance !== 'built-in') saveUser(); notify(); }
    return t;
  }
  function registerMany(entries, opts = {}) {
    suppressNotify = true;
    try { for (const t of entries) register(t, { silent: true }); }
    finally { suppressNotify = false; }
    if (!opts.silent) { saveUser(); notify(); }
  }
  function update(id, patch, opts = {}) {
    const cur = get(id);
    if (!cur) return null;
    if (cur.provenance === 'built-in') {
      // built-ins fork into user space on edit (same contract as CV_REGISTRY)
      return register({ ...cur, ...patch, id: cur.id, provenance: 'user', forkedFrom: cur.id, updatedAt: Date.now(), version: (cur.version || 1) + 1 }, opts);
    }
    return register({ ...cur, ...patch, updatedAt: Date.now(), version: (cur.version || 1) + 1 }, opts);
  }
  function remove(id, opts = {}) {
    if (BUILTIN.has(id)) return false;
    const removed = USER.delete(id);
    if (removed && !opts.silent) { saveUser(); notify(); }
    return removed;
  }
  function get(id) { return id ? (USER.get(id) || BUILTIN.get(id) || null) : null; }
  function all() { return [...BUILTIN.values(), ...USER.values()]; }

  function query({ layer, layers, family, families, surface, tags, provenance, extendsId, search } = {}) {
    let out = all();
    if (layer) out = out.filter(t => t.layer === layer);
    if (layers && layers.length) out = out.filter(t => layers.includes(t.layer));
    if (family) out = out.filter(t => t.family === family);
    if (families && families.length) out = out.filter(t => families.includes(t.family));
    if (surface) out = out.filter(t => !t.surfaces || t.surfaces.includes('*') || t.surfaces.includes(surface));
    if (provenance) out = out.filter(t => t.provenance === provenance);
    if (extendsId) out = out.filter(t => t.extends === extendsId);
    if (tags && tags.length) out = out.filter(t => (t.tags || []).some(x => tags.includes(x)));
    if (search) {
      const q = search.toLowerCase();
      out = out.filter(t => t.id.includes(q) || (t.name || '').toLowerCase().includes(q) || (t.description || '').toLowerCase().includes(q) || (t.tags || []).some(x => x.toLowerCase().includes(q)));
    }
    return out.sort(byLayerThenName);
  }
  function byLayerThenName(a, b) {
    const da = LAYER_INFO[a.layer]?.rank ?? 99, db = LAYER_INFO[b.layer]?.rank ?? 99;
    if (da !== db) return da - db;
    return (a.name || '').localeCompare(b.name || '');
  }

  // ---------------------------------------------------------------------------
  // Inheritance — flatten an entry with its ancestors (leaf wins). Lets a
  // capability `extends` a base capability and override params/behaviours, the
  // way a Type extends a Type. Functions (build/parse/resolve) inherit too.
  // ---------------------------------------------------------------------------
  function resolve(id) {
    const chain = lineage(id);
    if (!chain.length) return null;
    const merged = chain.reduceRight((acc, t) => ({
      ...acc, ...t,
      params: { ...(acc.params || {}), ...(t.params || {}) },
      behaviours: [...new Set([...(acc.behaviours || []), ...(t.behaviours || [])])],
      surfaces: t.surfaces || acc.surfaces,
      tags: [...new Set([...(acc.tags || []), ...(t.tags || [])])],
    }), {});
    merged.lineage = chain.map(t => t.id);
    merged.id = chain[0].id; merged.name = chain[0].name; merged.provenance = chain[0].provenance;
    return merged;
  }
  function lineage(id) {
    const out = []; const seen = new Set(); let cur = get(id);
    while (cur && !seen.has(cur.id)) { seen.add(cur.id); out.push(cur); cur = cur.extends ? get(cur.extends) : null; }
    return out;
  }
  function children(id) { return all().filter(t => t.extends === id); }

  // ---------------------------------------------------------------------------
  // Normalize — fill defaults, stamp timestamps (mirrors CV_REGISTRY.normalize)
  // ---------------------------------------------------------------------------
  function normalize(t) {
    const now = Date.now();
    return {
      id: t.id,
      name: t.name || t.id,
      layer: t.layer || 'capability',
      family: t.family || t.layer || 'capability',
      description: t.description || '',
      extends: t.extends || null,
      surfaces: t.surfaces || null,        // which surfaces an entry applies to (null = any)
      behaviours: t.behaviours || [],      // behaviour ids a capability composes
      provider: t.provider || null,        // provider id a capability runs on
      params: t.params || {},              // dials (count, angle, …)
      tags: t.tags || [],
      provenance: t.provenance || 'user',
      icon: t.icon || 'sparkles',
      // functional members (built-ins set these; carried through untouched)
      run: t.run,            // capability: ({doc,target,ctx,params,provider}) -> candidate[] (owns build→complete→parse)
      build: t.build,        // capability: (doc, target, ctx, params) -> prompt string
      parse: t.parse,        // capability: (reply, doc, target, params) -> candidate[]
      resolveCtx: t.resolveCtx, // context: (doc, ctx) -> contextObject
      text: t.text,          // behaviour: instruction fragment (string or fn(params)->string)
      instruction: t.instruction, // skill: the intent text
      target: t.target,      // skill: capability id + target descriptor it invokes
      runtime: t.runtime || null, // provider: { kind } — how to reach the live endpoint
      modality: t.modality || null, // provider: ['text'] | ['text','stream'] | ['image']
      caps: t.caps || null,  // provider: { stream, json, maxPromptChars }
      createdAt: t.createdAt || now,
      updatedAt: t.updatedAt || now,
      version: t.version || 1,
      forkedFrom: t.forkedFrom || null,
    };
  }

  // ---------------------------------------------------------------------------
  // Provider resolution — bind a provider entry to its LIVE runtime, with
  // inference for unknown ids (mirrors openai.js getModelCapabilities). LOUD:
  // if the runtime an entry names isn't present, throw — no silent fallback.
  // ---------------------------------------------------------------------------
  function resolveProvider(id) {
    const p = get(id);
    if (!p) throw new Error('[CV_AI] provider not found: "' + id + '" (registered providers: ' + query({ layer: 'provider' }).map(x => x.id).join(', ') + ')');
    if (p.layer !== 'provider') throw new Error('[CV_AI] "' + id + '" is a ' + p.layer + ', not a provider');
    const kind = p.runtime && p.runtime.kind;
    if (kind === 'claude') {
      if (typeof window === 'undefined' || !window.claude || typeof window.claude.complete !== 'function') {
        throw new Error('[CV_AI] provider "' + id + '" runtime (window.claude.complete) not available');
      }
      return {
        ...p,
        async complete(prompt, opts) {
          // window.claude.complete accepts a string or {messages}
          return opts && opts.messages ? window.claude.complete(opts) : window.claude.complete(prompt);
        },
      };
    }
    if (kind === 'openai-image') {
      const svc = (typeof window !== 'undefined') ? window.cvOpenAI : null;
      if (!svc || typeof svc.generateImage !== 'function' || typeof svc.editImage !== 'function') {
        throw new Error('[CV_AI] provider "' + id + '" runtime (window.cvOpenAI) not available');
      }
      return {
        ...p,
        service: svc,
        generateImage: (opts) => svc.generateImage(opts),
        editImage: (opts) => svc.editImage(opts),
        responsesImage: (opts) => svc.responsesImage(opts),
        getModelCapabilities: (modelId) => svc.getModelCapabilities(modelId),
      };
    }
    // Any other runtime kind is owned by the Host/Environment layer (CV_HOST):
    // filesystem providers, native/MCP model endpoints. Delegate to it so the
    // AI catalogue can name providers it doesn't itself know how to reach. Loud:
    // CV_HOST returns a bound runtime or throws naming how to activate it.
    if (typeof window !== 'undefined' && window.CV_HOST && typeof window.CV_HOST.resolveProviderRuntime === 'function') {
      const bound = window.CV_HOST.resolveProviderRuntime(p);
      if (bound) return bound;
    }
    throw new Error('[CV_AI] provider "' + id + '" has unknown runtime kind "' + kind + '" (no CV_HOST runtime claimed it)');
  }

  // ---------------------------------------------------------------------------
  // Context resolution — "resolve context from what screen Vi is on." Runs the
  // registered context resolver whose surface matches, producing the compact
  // context object capabilities build prompts from. Falls through a generic
  // resolver so every surface gets SOME context, never nothing.
  // ---------------------------------------------------------------------------
  function resolveContext({ surface, doc, ctx } = {}) {
    const sfc = surface || (doc && doc.type) || ACTIVE.surface || 'generic';
    const base = { surface: sfc, doc, ...(ctx || {}) };
    // most specific surface resolver wins; 'generic' is the floor
    const resolver = query({ layer: 'context' }).find(c => (c.surfaces || []).includes(sfc))
      || get('context.generic');
    if (resolver && typeof resolver.resolveCtx === 'function') {
      try { return { ...base, ...resolver.resolveCtx(doc, base) }; }
      catch (e) { throw new Error('[CV_AI] context resolver "' + resolver.id + '" failed: ' + e.message); }
    }
    return base;
  }

  // ---------------------------------------------------------------------------
  // Behaviour composition — concatenate the resolved behaviour fragments a
  // capability declares (+ any extra ids), into the prompt preamble.
  // ---------------------------------------------------------------------------
  function composeBehaviours(ids, params) {
    return (ids || []).map(bid => {
      const b = get(bid);
      if (!b) throw new Error('[CV_AI] behaviour not found: "' + bid + '"');
      const txt = typeof b.text === 'function' ? b.text(params || {}) : b.text;
      return txt || '';
    }).filter(Boolean).join('\n\n');
  }

  // ---------------------------------------------------------------------------
  // execute — THE generative path: ai-output = f(capability, context, params).
  // Resolves the capability (+ inheritance), resolves context from the active
  // surface, composes behaviours, builds the prompt, dispatches to the resolved
  // provider, parses candidates. Every failure is loud.
  // ---------------------------------------------------------------------------
  async function execute(capabilityId, { doc, target, ctx, params, brief, surface } = {}) {
    const cap = resolve(capabilityId);
    if (!cap) throw new Error('[CV_AI] capability not found: "' + capabilityId + '" (registered: ' + query({ layer: 'capability' }).map(x => x.id).join(', ') + ')');
    // A skill is a named intent bound to a capability + instruction — delegate
    // to its target capability, threading the skill's instruction as the brief.
    if (cap.layer === 'skill') {
      const targetId = cap.target && cap.target.capability;
      if (!targetId) throw new Error('[CV_AI] skill "' + capabilityId + '" has no target capability');
      return execute(targetId, {
        doc, target: { ...(cap.target || {}), ...(target || {}) }, ctx,
        params: { ...(params || {}), instruction: cap.instruction, skill: cap.id },
        brief: brief || cap.instruction, surface,
      });
    }
    if (cap.layer !== 'capability') throw new Error('[CV_AI] "' + capabilityId + '" is a ' + cap.layer + ', not a capability');

    const mergedParams = { ...(cap.params || {}), ...(params || {}), brief: brief || (params && params.brief) || '' };
    const resolvedCtx = resolveContext({ surface: surface || (target && target.surface), doc, ctx: { ...ctx, target } });
    // resolve a provider only when the capability DECLARES one — a pure-function run()
    // capability (provider:null, no LLM) must not require a live LLM runtime to execute.
    // The build/parse (LLM) path below resolves 'claude' where it actually needs it.
    const provider = cap.provider ? resolveProvider(cap.provider) : null;

    // run() path — the capability owns build→complete→parse (it needs the
    // composer's prompt helpers). It still receives the resolved provider (or null
    // for a pure-function capability), context and behaviour preamble, so routing stays unified.
    if (typeof cap.run === 'function') {
      const preamble = composeBehaviours(cap.behaviours, mergedParams);
      return (await cap.run({ doc, target, ctx: resolvedCtx, params: mergedParams, provider, preamble, brief: mergedParams.brief })) || [];
    }

    // build/parse path — pure-data capabilities (no helper dependency). This path NEEDS
    // an LLM, so resolve 'claude' here (loud if absent) rather than forcing it on run() caps.
    if (typeof cap.build !== 'function') throw new Error('[CV_AI] capability "' + capabilityId + '" has neither run() nor build()');
    const preamble = composeBehaviours(cap.behaviours, mergedParams);
    const body = cap.build(doc, target, resolvedCtx, mergedParams);
    if (!body) return [];
    const reply = await (provider || resolveProvider('claude')).complete(preamble ? preamble + '\n\n' + body : body);
    return (typeof cap.parse === 'function' ? cap.parse(reply, doc, target, mergedParams) : reply) || [];
  }

  // ---------------------------------------------------------------------------
  // Active surface — the single place "what screen Vi is on" is recorded, so
  // context auto-resolves everywhere. Surfaces push to this on focus; the
  // chat rail / field toolbar / suggestions read from it.
  // ---------------------------------------------------------------------------
  const ACTIVE = { surface: null, doc: null, ctx: null };
  function setActiveSurface(surface, doc, ctx) {
    ACTIVE.surface = surface; ACTIVE.doc = doc != null ? doc : ACTIVE.doc; ACTIVE.ctx = ctx || ACTIVE.ctx;
    notify();
  }

  // ---------------------------------------------------------------------------
  function subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); }
  function notify() { if (suppressNotify) return; for (const fn of listeners) try { fn(); } catch {} }

  // ---------------------------------------------------------------------------
  window.CV_AI = {
    LAYERS, LAYER_INFO,
    register, registerMany, update, remove,
    get, all, query, resolve, lineage, children,
    resolveProvider, resolveContext, composeBehaviours, execute,
    // convenience: route a one-off text completion through the resolved claude
    // provider — the single endpoint every surface should call instead of
    // window.claude.complete directly. Loud if the runtime is absent.
    complete(promptOrOpts) { return resolveProvider('claude').complete(promptOrOpts); },
    get active() { return ACTIVE; }, setActiveSurface,
    subscribe,
    _builtin: BUILTIN, _user: USER,
  };

  loadFromStorage();
})();
