// app/canvases/RegistryInspector.jsx
// Side-panel inspector + persistent Vi rail + quick adder.
// Visual editing. Drag/drop slot zones. Vi conversation always present.

const { useState: useState_ri, useEffect: useEffect_ri, useMemo: useMemo_ri, useRef: useRef_ri } = React;

// ===========================================================================
// TypeInspector — slides in from the right when a Type is clicked
// ===========================================================================
function TypeInspector({ typeId, onClose, onPickRelated, onAddVariant, onAdvanced }) {
  const R = window.CV_REGISTRY;
  const [tick, setTick] = useState_ri(0);
  useEffect_ri(() => R?.subscribe(() => setTick(t => t + 1)), []);

  const type = R?.get(typeId);
  const resolved = R?.resolve(typeId);
  const variants = R?.children(typeId) || [];
  const lineage = R?.lineage(typeId) || [];

  // Live inline edits — applied on blur
  const [name, setName] = useState_ri(type?.name || '');
  const [desc, setDesc] = useState_ri(type?.description || '');
  useEffect_ri(() => { setName(type?.name || ''); setDesc(type?.description || ''); }, [typeId]);

  if (!type) return null;
  const isBuiltIn = type.provenance === 'built-in';

  function commitName() {
    if (name !== type.name && name.trim()) R.update(typeId, { name: name.trim() });
  }
  function commitDesc() {
    if (desc !== type.description) R.update(typeId, { description: desc });
  }
  function duplicate() {
    const t = R.register({
      ...type,
      id: type.id + '-copy-' + Date.now().toString(36),
      name: type.name + ' (copy)',
      provenance: 'user',
      forkedFrom: type.id,
    });
    window.dsaToast?.('Duplicated');
    onPickRelated(t.id);
  }
  function makeVariant() {
    // Variant = a child Type that EXTENDS this one
    if (onAddVariant) {
      onAddVariant(type);
      return;
    }
    const t = R.register({
      id: type.id + '-variant-' + Date.now().toString(36),
      name: type.name + ' variant',
      layer: type.layer,
      family: type.family,
      extends: type.id,
      description: '',
      icon: type.icon,
      provenance: 'user',
      defaults: {},
      slots: {},
      variables: [],
      tags: [...(type.tags || [])],
    });
    window.dsaToast?.('Variant created');
    onPickRelated(t.id);
  }
  function deleteType() {
    if (!confirm(`Delete "${type.name}"? This can't be undone.`)) return;
    R.remove(typeId);
    window.dsaToast?.('Deleted');
    onClose();
  }

  return (
    <aside className="rs-inspector">
      <header className="rs-insp-head">
        <button className="rs-insp-close" onClick={onClose} title="Close (esc)">×</button>
        <div className="rs-insp-crumbs">
          {[...lineage].reverse().map((t, i) => (
            <React.Fragment key={t.id}>
              {i > 0 && <span className="sep">›</span>}
              <button className={`crumb ${t.id === typeId ? 'self' : ''}`} onClick={() => onPickRelated(t.id)}>
                <window.TypeLayerBadge layer={t.layer} size="sm"/>
                <span>{t.name}</span>
              </button>
            </React.Fragment>
          ))}
        </div>
      </header>

      <div className="rs-insp-thumb">
        {window.TypeThumb && <window.TypeThumb type={resolved} width={420} height={250}/>}
      </div>

      <div className="rs-insp-name-row">
        <input
          className="rs-insp-name"
          value={name} onChange={e => setName(e.target.value)} onBlur={commitName}
          placeholder="Type name"
          disabled={isBuiltIn}/>
        <span className={`prov-pill prov-${type.provenance}`}>{type.provenance}</span>
      </div>
      <textarea
        className="rs-insp-desc"
        value={desc} onChange={e => setDesc(e.target.value)} onBlur={commitDesc}
        rows={2}
        placeholder="What does this Type do? (Plain English — Vi reads this too)"
        disabled={isBuiltIn}/>

      {isBuiltIn && (
        <div className="rs-insp-builtin-hint">
          This is a built-in Type. Edit it to create your own forked copy, or use
          <strong> + Variant </strong>to make a child that inherits everything.
        </div>
      )}

      {/* Actions row — primary moves on this Type */}
      <div className="rs-insp-actions">
        <button className="dsa-btn dsa-btn--primary" onClick={makeVariant}>
          + Variant
        </button>
        <button className="dsa-btn dsa-btn--outline" onClick={duplicate} title="Make an editable copy (not a child)">
          Duplicate
        </button>
        {!isBuiltIn && (
          <button className="dsa-btn dsa-btn--ghost" onClick={deleteType} title="Delete this Type" style={{marginLeft:'auto',color:'var(--status-error)'}}>
            Delete
          </button>
        )}
      </div>

      {/* Slots — visual zones, drag-droppable */}
      <SlotZones type={resolved} canEdit={!isBuiltIn} onChange={(patch) => R.update(typeId, patch)}/>

      {/* Variables — tag row, click to mark fields as variable */}
      <VariableTags type={resolved} canEdit={!isBuiltIn} onChange={(patch) => R.update(typeId, patch)}/>

      {/* Variants list — child Types */}
      {variants.length > 0 && (
        <section className="rs-insp-section">
          <h5>Variants <span className="ct">{variants.length}</span></h5>
          <div className="rs-insp-variants">
            {variants.map(v => (
              <button key={v.id} className="rs-insp-variant" onClick={() => onPickRelated(v.id)}>
                {window.TypeThumb && <window.TypeThumb type={v} width={160} height={96} dense/>}
                <span className="lbl">{v.name}</span>
              </button>
            ))}
          </div>
        </section>
      )}

      {/* Scoped Vi conversation */}
      <ViChatScoped type={type}/>

      <footer className="rs-insp-foot">
        <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={onAdvanced} title="Open in Type Builder for advanced authoring">
          Open in advanced editor →
        </button>
      </footer>
    </aside>
  );
}

// ===========================================================================
// SlotZones — visual slot editor. Each slot is a drop zone with a label.
// Click "+ Add slot" to add a new one. Vi can also propose.
// ===========================================================================
function SlotZones({ type, canEdit, onChange }) {
  const R = window.CV_REGISTRY;
  const slots = type?.slots || {};
  const keys = Object.keys(slots);
  const [busy, setBusy] = useState_ri(false);

  function setSlot(name, patch) {
    if (!canEdit) return;
    onChange({ slots: { ...(slots || {}), [name]: { ...(slots[name] || {}), ...patch } } });
  }
  function removeSlot(name) {
    if (!canEdit) return;
    const next = { ...(slots || {}) }; delete next[name];
    onChange({ slots: next });
  }
  function addSlot() {
    const n = 'slot' + (keys.length + 1);
    setSlot(n, { label: 'New zone', accepts: { layers: ['block'] }, multiple: false });
  }
  async function viSuggestSlots() {
    if (!window.CV_TYPES_VI) return;
    setBusy(true);
    try {
      const suggested = await window.CV_TYPES_VI.suggestSlots(type.id);
      if (!suggested.length) { window.dsaToast?.('Vi had no slot ideas this time'); return; }
      const next = { ...(slots || {}) };
      for (const s of suggested) if (!next[s.name]) next[s.name] = { label: s.label, accepts: s.accepts, multiple: !!s.multiple, optional: !!s.optional };
      onChange({ slots: next });
      window.dsaToast?.(`Vi added ${suggested.length} slot${suggested.length===1?'':'s'}`);
    } finally { setBusy(false); }
  }

  return (
    <section className="rs-insp-section">
      <h5>
        Slots <span className="ct">{keys.length}</span>
        <span className="hint">what can go inside this Type</span>
        {canEdit && (
          <span className="head-actions">
            <button onClick={viSuggestSlots} disabled={busy} className="vi" title="Ask Vi for more slot ideas">
              <ViShape size={10}/> {busy ? '…' : 'Vi'}
            </button>
            <button onClick={addSlot} title="Add a blank slot">+</button>
          </span>
        )}
      </h5>
      {keys.length === 0 && (
        <div className="rs-slot-empty">
          {canEdit
            ? <>This Type doesn't compose other Types yet. <button onClick={addSlot}>+ Add a slot</button> or <button className="vi" onClick={viSuggestSlots} disabled={busy}>{busy ? '…' : 'ask Vi'}</button>.</>
            : 'No slots — this Type is a leaf.'}
        </div>
      )}
      <div className="rs-slot-zones">
        {keys.map(k => (
          <SlotZone key={k} name={k} slot={slots[k]} canEdit={canEdit} onChange={(p) => setSlot(k, p)} onRemove={() => removeSlot(k)}/>
        ))}
      </div>
    </section>
  );
}

function SlotZone({ name, slot, canEdit, onChange, onRemove }) {
  const R = window.CV_REGISTRY;
  const matches = R?.candidatesForSlot(slot) || [];
  const [editLabel, setEditLabel] = useState_ri(slot.label || name);
  useEffect_ri(() => { setEditLabel(slot.label || name); }, [name, slot.label]);
  return (
    <div className="rs-slot-zone">
      <div className="rs-slot-head">
        <input className="rs-slot-label" value={editLabel}
          onChange={e => setEditLabel(e.target.value)}
          onBlur={() => editLabel !== slot.label && onChange({ label: editLabel })}
          disabled={!canEdit}/>
        {canEdit && (
          <>
            <button className={`mini ${slot.multiple ? 'on' : ''}`} onClick={() => onChange({ multiple: !slot.multiple })} title="Toggle: allow multiple">×N</button>
            <button className={`mini ${slot.optional ? 'on' : ''}`} onClick={() => onChange({ optional: !slot.optional })} title="Toggle: optional">opt</button>
            <button className="rm" onClick={onRemove}>×</button>
          </>
        )}
      </div>
      <div className="rs-slot-accept">
        accepts:
        {(slot.accepts?.layers || []).map(l => <span key={l} className="acc-chip">{l}</span>)}
        {(slot.accepts?.families || []).map(f => <span key={f} className="acc-chip fam">family·{f}</span>)}
        {(slot.accepts?.tags || []).map(t => <span key={t} className="acc-chip tag">tag·{t}</span>)}
        {(!slot.accepts?.layers?.length && !slot.accepts?.families?.length && !slot.accepts?.tags?.length) && <span className="acc-chip any">any Type</span>}
      </div>
      <div className="rs-slot-matches">
        {matches.slice(0, 6).map(t => (
          <div key={t.id} className="rs-slot-match" title={t.name}>
            {window.TypeThumb && <window.TypeThumb type={t} width={70} height={42} dense/>}
          </div>
        ))}
        {matches.length > 6 && <span className="more">+{matches.length - 6}</span>}
        {matches.length === 0 && <em className="empty">Nothing matches yet — try a broader filter.</em>}
      </div>
      {canEdit && <AcceptsQuickEdit accepts={slot.accepts || {}} onChange={(acc) => onChange({ accepts: acc })}/>}
    </div>
  );
}

function AcceptsQuickEdit({ accepts, onChange }) {
  const R = window.CV_REGISTRY;
  return (
    <div className="rs-accepts-edit">
      <span className="dim">change to accept:</span>
      {R.LAYERS.filter(l => l !== 'template').map(l => {
        const on = (accepts.layers || []).includes(l);
        return (
          <button key={l} className={`layer-toggle ${on ? 'on' : ''}`}
            onClick={() => {
              const cur = accepts.layers || [];
              const next = on ? cur.filter(x => x !== l) : [...cur, l];
              onChange({ ...accepts, layers: next });
            }}>
            <span className="pip" style={{background:R.LAYER_INFO[l].swatch}}/>
            {R.LAYER_INFO[l].label}
          </button>
        );
      })}
    </div>
  );
}

// ===========================================================================
// VariableTags — values that change between Template runs
// ===========================================================================
function VariableTags({ type, canEdit, onChange }) {
  const vars = type?.variables || [];
  function addVar() {
    if (!canEdit) return;
    onChange({ variables: [...vars, { key: 'var_' + (vars.length + 1), label: 'New variable', default: '', kind: 'text' }] });
  }
  function setVar(i, patch) { onChange({ variables: vars.map((v, j) => i === j ? { ...v, ...patch } : v) }); }
  function rmVar(i)   { onChange({ variables: vars.filter((_, j) => i !== j) }); }
  return (
    <section className="rs-insp-section">
      <h5>
        Variables <span className="ct">{vars.length}</span>
        <span className="hint">what changes between Template runs</span>
        {canEdit && <span className="head-actions"><button onClick={addVar}>+</button></span>}
      </h5>
      {vars.length === 0 && (
        <div className="rs-var-empty">
          {canEdit
            ? <>No variables. Tap <button onClick={addVar}>+ Add</button> when you want this Type to power Templates.</>
            : 'No variables.'}
        </div>
      )}
      <div className="rs-var-tags">
        {vars.map((v, i) => (
          <div key={i} className="rs-var-tag">
            <input className="key" value={v.key} onChange={e => setVar(i, { key: e.target.value })} disabled={!canEdit} placeholder="key"/>
            <input className="lbl" value={v.label || ''} onChange={e => setVar(i, { label: e.target.value })} disabled={!canEdit} placeholder="label"/>
            <input className="def" value={v.default || ''} onChange={e => setVar(i, { default: e.target.value })} disabled={!canEdit} placeholder="default"/>
            {canEdit && <button className="rm" onClick={() => rmVar(i)}>×</button>}
          </div>
        ))}
      </div>
    </section>
  );
}

// ===========================================================================
// ViChatScoped — conversational Vi rail, scoped to the current Type
// ===========================================================================
function ViChatScoped({ type }) {
  const [msgs, setMsgs] = useState_ri([]);
  const [input, setInput] = useState_ri('');
  const [busy, setBusy] = useState_ri(false);
  const R = window.CV_REGISTRY;
  useEffect_ri(() => { setMsgs([]); setInput(''); }, [type?.id]);

  const suggestions = useMemo_ri(() => suggestionsFor(type), [type?.id]);

  async function send(text) {
    const q = (text ?? input).trim();
    if (!q || !type) return;
    setInput('');
    setMsgs(m => [...m, { from: 'me', text: q }]);
    setBusy(true);
    try {
      const r = await runViAction({ type, prompt: q });
      if (r?.applied) {
        setMsgs(m => [...m, { from: 'vi', text: r.summary || 'Done.', applied: true }]);
        window.dsaToast?.('Applied via Vi');
      } else if (r?.proposal) {
        // Show pending — confirm to apply
        setMsgs(m => [...m, { from: 'vi', text: r.summary || 'Proposed.', proposal: r.proposal }]);
      } else {
        setMsgs(m => [...m, { from: 'vi', text: r?.text || 'Sorry, I could not act on that. Try rewording.' }]);
      }
    } catch (e) {
      setMsgs(m => [...m, { from: 'vi', text: 'Vi hit an error. Try again or rephrase.' }]);
    } finally { setBusy(false); }
  }

  function applyProposal(p) {
    if (p.kind === 'update') { R.update(type.id, p.patch); }
    else if (p.kind === 'create-variant') {
      const t = R.register(p.draft);
      window.dsaToast?.('Variant registered');
    }
    setMsgs(m => m.map(x => x.proposal === p ? { ...x, applied: true, proposal: null } : x));
  }

  return (
    <section className="rs-insp-section rs-vi">
      <h5><ViShape size={12}/> Ask Vi about this Type<span className="hint">apply a change, request a variant, or just ask</span></h5>
      <div className="rs-vi-msgs">
        {msgs.length === 0 && (
          <div className="rs-vi-empty">
            <p>Tell Vi what you'd like to change or add. Some ideas:</p>
            <div className="rs-vi-sugs">
              {suggestions.map((s, i) => (
                <button key={i} onClick={() => send(s)}>{s}</button>
              ))}
            </div>
          </div>
        )}
        {msgs.map((m, i) => (
          <div key={i} className={`rs-vi-msg from-${m.from}`}>
            {m.from === 'vi' && <ViShape size={11}/>}
            <div className="bubble">
              {m.text}
              {m.proposal && !m.applied && (
                <div className="rs-vi-actions">
                  <button className="dsa-btn dsa-btn--primary dsa-btn--sm" onClick={() => applyProposal(m.proposal)}>Apply</button>
                </div>
              )}
              {m.applied && <span className="applied-pill">applied</span>}
            </div>
          </div>
        ))}
        {busy && <div className="rs-vi-msg from-vi"><ViShape size={11} animated/><div className="bubble dim">Thinking…</div></div>}
      </div>
      <div className="rs-vi-input">
        <textarea rows="1" value={input} placeholder="e.g. add a CTA slot · rename to Funnel system · make it accept media blocks too"
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } }}/>
        <button className="dsa-btn dsa-btn--ai dsa-btn--sm" onClick={() => send()} disabled={busy || !input.trim()}>
          <ViShape size={10}/> Ask
        </button>
      </div>
    </section>
  );
}

function suggestionsFor(t) {
  if (!t) return [];
  const out = [];
  if (Object.keys(t.slots || {}).length === 0) out.push('Add a slot for an image');
  else out.push('Make the main slot accept multiple');
  if ((t.variables || []).length === 0) out.push('Identify variables for Templates');
  out.push('Make a softer variant');
  out.push('Make a denser variant');
  if (t.layer === 'system') out.push('What other systems would pair well with this?');
  if (t.family === 'widget') out.push('Suggest a new widget kind that uses this');
  return out.slice(0, 4);
}

async function runViAction({ type, prompt }) {
  const R = window.CV_REGISTRY;
  const ctx = `You are Vi inside the ConceptV Type Registry. The user is inspecting a Type and asking for a change or addition.

Type:
  id: ${type.id}
  name: ${type.name}
  layer: ${type.layer}
  family: ${type.family}
  description: ${type.description}
  slots: ${JSON.stringify(type.slots || {})}
  defaults: ${JSON.stringify(type.defaults || {}).slice(0, 600)}
  variables: ${JSON.stringify(type.variables || [])}
  tags: ${(type.tags || []).join(', ')}
  provenance: ${type.provenance}

User: "${prompt}"

Decide ONE of these intents and respond ONLY as JSON:

A. UPDATE this Type (patch fields, add slots/variables, rename, etc.). Use when the user wants to modify the Type in place.
   { "intent": "update", "summary": "one-line plain-English description of what you're changing", "patch": { "name": "...", "description": "...", "slots": {...}, "variables": [...], "tags": [...], "defaults": {...} } }

B. CREATE a VARIANT (a child Type extending this one). Use when the user wants a new variant/subtype.
   { "intent": "create-variant", "summary": "...", "draft": { "id": "kebab.id", "name": "...", "layer": "${type.layer}", "family": "${type.family}", "extends": "${type.id}", "description": "...", "slots": {}, "defaults": {}, "variables": [], "tags": [...], "icon": "...", "provenance": "vi" } }

C. ANSWER a question without changes.
   { "intent": "answer", "text": "..." }

Brand voice: sentence case, second-person, no exclamation marks, no emoji. Be concise.`;
  // Unified: resolve the Claude provider through CV_AI (loud if absent), don't
  // call the raw endpoint. A confused/malformed reply still returns a graceful
  // "try rewording" (that's a model-quality outcome, not a swallowed error).
  if (!window.CV_AI) throw new Error('[RegistryInspector] CV_AI registry not loaded');
  const reply = await window.CV_AI.resolveProvider('claude').complete(ctx);
  let parsed = null;
  try { parsed = JSON.parse(reply); }
  catch { const m = reply.match(/\{[\s\S]*\}/); if (m) try { parsed = JSON.parse(m[0]); } catch {} }
  if (!parsed) return { text: 'Vi gave a confused answer. Try rewording.' };

  if (parsed.intent === 'update') {
    return { proposal: { kind: 'update', patch: parsed.patch || {} }, summary: parsed.summary };
  }
  if (parsed.intent === 'create-variant') {
    return { proposal: { kind: 'create-variant', draft: parsed.draft }, summary: parsed.summary };
  }
  return { text: parsed.text || 'No change suggested.' };
}

// ===========================================================================
// AIRegistryPanel — a live PROJECTION of CV_AI, shown beside the type registry.
// The AI catalogue (providers · behaviours · skills · capabilities · context)
// is inspectable exactly as CV_REGISTRY's Types are — same idea, one screen.
// Reads from CV_AI and re-renders on its notify, so it's always in sync with
// what Vi can actually resolve and do.
// ===========================================================================
function AIRegistryPanel() {
  const AI = window.CV_AI;
  const [, force] = useState_ri(0);
  const [open, setOpen] = useState_ri(false);
  useEffect_ri(() => AI ? AI.subscribe(() => force(x => x + 1)) : undefined, []);
  if (!AI) return null;
  const active = AI.active && AI.active.surface;
  const byLayer = AI.LAYERS.map(layer => ({ layer, info: AI.LAYER_INFO[layer], items: AI.query({ layer }) }));
  const total = byLayer.reduce((n, g) => n + g.items.length, 0);
  return (
    <section className="rs-ai-reg" style={{ borderBottom: '1px solid var(--rule, rgba(0,0,0,.08))', padding: '10px 12px' }}>
      <button
        onClick={() => setOpen(o => !o)}
        style={{ all: 'unset', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8, width: '100%', font: '600 11px/1.3 var(--font-body)', color: 'var(--ink-2, #5b4628)', textTransform: 'uppercase', letterSpacing: '.04em' }}>
        <span style={{ display: 'inline-block', width: 7, height: 7, borderRadius: 2, background: 'var(--accent-gold, #E0C010)' }}></span>
        AI registry
        <span style={{ opacity: .6, fontWeight: 500 }}>{total} · CV_AI</span>
        {active && <span style={{ marginLeft: 'auto', fontWeight: 500, opacity: .7, textTransform: 'none', letterSpacing: 0 }}>on: {active}</span>}
        <span style={{ opacity: .5 }}>{open ? '⌄' : '⌃'}</span>
      </button>
      {open && (
        <div style={{ marginTop: 8, display: 'flex', flexDirection: 'column', gap: 8 }}>
          {byLayer.map(g => (
            <div key={g.layer}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, font: '600 10px/1.2 var(--font-body)', color: 'var(--ink-3, #7E6539)', marginBottom: 4 }}>
                <span style={{ display: 'inline-block', width: 6, height: 6, borderRadius: '50%', background: g.info.swatch }}></span>
                {g.info.label}<span style={{ opacity: .55 }}>{g.items.length}</span>
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                {g.items.map(t => (
                  <span key={t.id} title={t.description || t.id}
                    style={{ font: '500 10px/1.4 var(--font-mono, monospace)', padding: '1px 6px', borderRadius: 4, background: 'var(--zone-1, rgba(0,0,0,.04))', color: 'var(--ink-2, #5b4628)', boxShadow: 'inset 0 0 0 1px rgba(0,0,0,.06)' }}>
                    {t.id}{t.provenance !== 'built-in' ? ' ·' + t.provenance : ''}
                  </span>
                ))}
              </div>
            </div>
          ))}
          <p style={{ font: '500 10px/1.4 var(--font-body)', color: 'var(--ink-3, #7E6539)', opacity: .8, margin: '2px 0 0' }}>
            Every Vi move resolves from this catalogue — the interface and the AI read one source.
          </p>
        </div>
      )}
    </section>
  );
}

// ===========================================================================
// ViStudioRail — global Vi conversation (when nothing selected)
// ===========================================================================
function ViStudioRail({ context, onPickType }) {
  const [open, setOpen] = useState_ri(true);
  const [msgs, setMsgs] = useState_ri([
    { from: 'vi', text: "I'm Vi. Tell me what you want to add to your Workshop, or what's missing. I can also rename, restyle, or create variants of anything you've made." },
  ]);
  const [input, setInput] = useState_ri('');
  const [busy, setBusy] = useState_ri(false);
  if (context) return null; // Inspector takes over

  const quickIdeas = [
    'A funnel widget system',
    'A capture step that uses video',
    'A pitch deck variant focused on agents',
    'What\'s missing from my Workshop?',
  ];

  async function send(text) {
    const q = (text ?? input).trim();
    if (!q) return;
    setInput('');
    setMsgs(m => [...m, { from: 'me', text: q }]);
    setBusy(true);
    try {
      const r = await runStudioAction({ prompt: q });
      if (r?.proposal) {
        setMsgs(m => [...m, { from: 'vi', text: r.summary || 'Proposed.', proposal: r.proposal }]);
      } else {
        setMsgs(m => [...m, { from: 'vi', text: r?.text || 'No suggestion.' }]);
      }
    } catch { setMsgs(m => [...m, { from: 'vi', text: 'Vi hit an error. Try again.' }]); }
    finally { setBusy(false); }
  }
  function applyProposal(p) {
    if (p.kind === 'create-type') {
      const t = window.CV_REGISTRY.register(p.draft);
      onPickType?.(t.id);
    }
    setMsgs(m => m.map(x => x.proposal === p ? { ...x, applied: true, proposal: null } : x));
  }

  return (
    <aside className={`rs-vi-rail ${open ? 'open' : 'closed'}`}>
      <header onClick={() => setOpen(o => !o)}>
        <ViShape size={14}/>
        <strong>Vi · ready</strong>
        <span className="caret">{open ? '⌄' : '⌃'}</span>
      </header>
      {open && (
        <>
          <AIRegistryPanel/>
          <div className="rs-vi-msgs">
            {msgs.map((m, i) => (
              <div key={i} className={`rs-vi-msg from-${m.from}`}>
                {m.from === 'vi' && <ViShape size={11}/>}
                <div className="bubble">
                  {m.text}
                  {m.proposal && !m.applied && (
                    <div className="rs-vi-actions">
                      <button className="dsa-btn dsa-btn--primary dsa-btn--sm" onClick={() => applyProposal(m.proposal)}>Add to Workshop</button>
                    </div>
                  )}
                  {m.applied && <span className="applied-pill">added</span>}
                </div>
              </div>
            ))}
            {busy && <div className="rs-vi-msg from-vi"><ViShape size={11} animated/><div className="bubble dim">Thinking…</div></div>}
            {msgs.length <= 1 && !busy && (
              <div className="rs-vi-sugs">
                {quickIdeas.map((s, i) => <button key={i} onClick={() => send(s)}>{s}</button>)}
              </div>
            )}
          </div>
          <div className="rs-vi-input">
            <textarea rows="1" value={input} placeholder="Add a Type, ask for a variant, or describe what's missing…"
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } }}/>
            <button className="dsa-btn dsa-btn--ai dsa-btn--sm" onClick={() => send()} disabled={busy || !input.trim()}>
              <ViShape size={10}/> Ask
            </button>
          </div>
        </>
      )}
    </aside>
  );
}

async function runStudioAction({ prompt }) {
  if (!window.CV_TYPES_VI) return { text: 'Type AI not loaded' };
  // For now: any open-ended brief becomes a proposeType call
  try {
    const draft = await window.CV_TYPES_VI.proposeType({ brief: prompt });
    return {
      proposal: { kind: 'create-type', draft },
      summary: `New ${draft.layer} Type: "${draft.name}" — ${draft.description}`,
    };
  } catch (e) {
    return { text: 'Vi could not work that out — try a more concrete brief.' };
  }
}

// ===========================================================================
// QuickAdder — modal when "+" is pressed
// ===========================================================================
function QuickAdder({ adder, stationDef, onClose, onSaved, onAdvanced }) {
  const R = window.CV_REGISTRY;
  const ws = stationDef;
  const shelf = ws && adder.shelfIdx != null ? ws.shelves[adder.shelfIdx] : null;
  const parent = adder.parent || null;

  const [brief, setBrief] = useState_ri('');
  const [busy, setBusy] = useState_ri(false);

  const promptHint = adder.parent
    ? `Make a variant of "${adder.parent.name}". What's different? e.g. "more visual" / "with a video field" / "branded for agents"`
    : ws?.addPrompt || 'Describe what you want to add — Vi will design the Type.';

  async function go() {
    if (!brief.trim() || !window.CV_TYPES_VI) return;
    setBusy(true);
    try {
      let draft;
      if (parent) {
        draft = await window.CV_TYPES_VI.proposeType({
          brief: brief.trim(),
          parentId: parent.id,
          layerHint: parent.layer,
          familyHint: parent.family,
        });
      } else if (shelf) {
        draft = await window.CV_TYPES_VI.proposeType({
          brief: brief.trim(),
          layerHint: shelf.addLayer,
          familyHint: shelf.addFamily,
          parentId: shelf.addParent || null,
        });
      } else {
        draft = await window.CV_TYPES_VI.proposeType({ brief: brief.trim() });
      }
      const t = R.register(draft);
      window.dsaToast?.(`Added "${t.name}"`);
      onSaved(t);
    } catch { window.dsaToast?.('Vi could not draft — try a more concrete brief'); }
    finally { setBusy(false); }
  }

  return (
    <div className="rs-modal" onClick={onClose}>
      <div className="rs-modal-inner" onClick={e => e.stopPropagation()}>
        <header>
          <ViShape size={14}/>
          <strong>
            {parent ? `+ Variant of "${parent.name}"`
             : shelf ? `+ ${shelf.label.replace(/s$/, '')} in ${ws.headline}`
             : '+ New Type'}
          </strong>
          <button className="x" onClick={onClose}>×</button>
        </header>
        <div className="body">
          <p className="hint">{promptHint}</p>
          <textarea autoFocus rows="3" value={brief} placeholder="Describe in plain English…"
            onChange={e => setBrief(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) go(); }}/>
        </div>
        <footer>
          <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={onAdvanced}>Advanced editor</button>
          <span style={{flex:1}}/>
          <button className="dsa-btn dsa-btn--ghost" onClick={onClose}>Cancel</button>
          <button className="dsa-btn dsa-btn--ai" onClick={go} disabled={busy || !brief.trim()}>
            <ViShape size={12} animated={busy}/> {busy ? 'Vi is drafting…' : 'Add to Workshop'}
          </button>
        </footer>
      </div>
    </div>
  );
}

Object.assign(window, {
  TypeInspector, SlotZones, SlotZone, VariableTags, ViChatScoped, ViStudioRail, QuickAdder,
});
