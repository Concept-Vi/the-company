// app/canvases/TypeBuilder.jsx
// Universal Type Builder — author or edit any Type at any layer.
// Layout (Tweakable): split (default) | wizard | canvas.
// Modes: visual (default), form, Vi-led.

const { useState: useState_tb, useEffect: useEffect_tb, useMemo: useMemo_tb, useRef: useRef_tb } = React;

function TypeBuilder({ initialTypeId, layout: layoutProp, onClose, onSaved }) {
  const R = window.CV_REGISTRY;
  const [layout, setLayout] = useState_tb(layoutProp || 'split');
  useEffect_tb(() => { if (layoutProp) setLayout(layoutProp); }, [layoutProp]);

  // Draft state — either a fresh Type or a fork of an existing one
  const [draft, setDraft] = useState_tb(() => initializeDraft(initialTypeId, R));
  const [browseFilter, setBrowseFilter] = useState_tb({ search: '', layer: null });
  const [mode, setMode] = useState_tb('visual'); // visual | form | vi | json
  const [busy, setBusy] = useState_tb(false);
  const [brief, setBrief] = useState_tb('');
  const [slotBrowser, setSlotBrowser] = useState_tb(null); // {slotName, slot}

  // Track whether draft has unsaved changes vs the source
  const sourceRef = useRef_tb(initialTypeId);
  useEffect_tb(() => {
    sourceRef.current = initialTypeId;
    setDraft(initializeDraft(initialTypeId, R));
  }, [initialTypeId]);

  function patch(p) { setDraft(d => ({ ...d, ...p })); }
  function patchSlot(name, sp) {
    setDraft(d => ({ ...d, slots: { ...(d.slots || {}), [name]: { ...(d.slots?.[name] || {}), ...sp } } }));
  }
  function removeSlot(name) {
    setDraft(d => {
      const next = { ...(d.slots || {}) }; delete next[name];
      return { ...d, slots: next };
    });
  }
  function addSlot() {
    const n = 'slot' + (Object.keys(draft.slots || {}).length + 1);
    patchSlot(n, { label: 'New slot', accepts: { layers: ['block'] }, multiple: false, optional: false });
  }
  function patchVariable(i, vp) {
    setDraft(d => ({ ...d, variables: (d.variables || []).map((v, j) => i === j ? { ...v, ...vp } : v) }));
  }
  function removeVariable(i) {
    setDraft(d => ({ ...d, variables: (d.variables || []).filter((_, j) => i !== j) }));
  }
  function addVariable() {
    setDraft(d => ({ ...d, variables: [...(d.variables || []), { key: 'var_' + ((d.variables||[]).length + 1), label: 'New variable', default: '', kind: 'text' }] }));
  }

  async function viPropose() {
    if (!brief.trim()) { window.dsaToast?.('Type a brief first'); return; }
    setBusy(true);
    try {
      const proposed = await window.CV_TYPES_VI.proposeType({
        brief: brief.trim(),
        parentId: draft.extends,
        layerHint: draft.layer,
        familyHint: draft.family,
      });
      setDraft({
        ...proposed,
        // Preserve the draft id if user already typed one
        id: draft.id?.startsWith('new.') ? proposed.id : (draft.id || proposed.id),
      });
      window.dsaToast?.('Vi drafted a Type — review and Save');
    } catch (e) {
      window.dsaToast?.('Vi could not draft — try a more specific brief');
    } finally { setBusy(false); }
  }

  async function viSuggestSlots() {
    if (!draft.id || !R.get(draft.id)) { window.dsaToast?.('Save first, then ask for slot suggestions'); return; }
    setBusy(true);
    try {
      const slots = await window.CV_TYPES_VI.suggestSlots(draft.id);
      if (!slots.length) { window.dsaToast?.('No suggestions returned'); return; }
      // Merge — don't overwrite existing names
      setDraft(d => {
        const next = { ...(d.slots || {}) };
        for (const s of slots) if (!next[s.name]) next[s.name] = { label: s.label, accepts: s.accepts, multiple: !!s.multiple, optional: !!s.optional };
        return { ...d, slots: next };
      });
      window.dsaToast?.(`Vi suggested ${slots.length} slot${slots.length===1?'':'s'}`);
    } finally { setBusy(false); }
  }

  function save() {
    if (!draft.name?.trim()) { window.dsaToast?.('Name your Type first'); return; }
    if (!draft.id?.trim()) { window.dsaToast?.('Give it a stable id'); return; }
    const existing = R.get(draft.id);
    if (existing && existing.provenance === 'built-in') {
      if (!confirm('Editing a built-in Type forks it into your user space. Continue?')) return;
    }
    const t = R.register({
      ...draft,
      provenance: existing?.provenance === 'built-in' ? 'user' : (draft.provenance || 'user'),
      forkedFrom: existing?.provenance === 'built-in' ? draft.id : (draft.forkedFrom || null),
    });
    window.dsaToast?.(`Saved "${t.name}"`);
    onSaved?.(t);
  }

  function reset() {
    setDraft(initializeDraft(sourceRef.current, R));
    window.dsaToast?.('Reverted');
  }

  function removeType() {
    if (!confirm(`Delete Type "${draft.name}"? This cannot be undone.`)) return;
    R.remove(draft.id);
    window.dsaToast?.('Deleted');
    onClose?.();
  }

  // Compatible parents for extends — same layer
  const parentCandidates = useMemo_tb(() => {
    if (!R) return [];
    return R.query({ layer: draft.layer }).filter(t => t.id !== draft.id);
  }, [draft.layer, draft.id]);

  const isNew = !R.get(draft.id);

  return (
    <>
      <CanvasHeader
        title={isNew ? 'New Type' : `Edit · ${draft.name || draft.id}`}
        sub={`${R.LAYER_INFO[draft.layer]?.label} layer · family "${draft.family || 'general'}"${draft.extends ? ' · extends ' + draft.extends : ''}`}
        actions={<>
          <button className="dsa-btn dsa-btn--ghost" onClick={onClose}>← All Types</button>
          <div className="ws-mode-seg">
            <button className={mode === 'visual' ? 'active' : ''} onClick={() => setMode('visual')} title="Visual editing">Visual</button>
            <button className={mode === 'form' ? 'active' : ''} onClick={() => setMode('form')} title="Form-driven fields">Form</button>
            <button className={mode === 'vi' ? 'active' : ''} onClick={() => setMode('vi')} title="Vi-led authoring">Vi</button>
            <button className={mode === 'json' ? 'active' : ''} onClick={() => setMode('json')} title="JSON (power users)">JSON</button>
          </div>
          <div className="ws-mode-seg">
            <button className={layout === 'split' ? 'active' : ''} onClick={() => setLayout('split')} title="Split pane">Split</button>
            <button className={layout === 'wizard' ? 'active' : ''} onClick={() => setLayout('wizard')} title="Step-by-step">Wizard</button>
            <button className={layout === 'canvas' ? 'active' : ''} onClick={() => setLayout('canvas')} title="Big canvas">Canvas</button>
          </div>
          {!isNew && <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={removeType} title="Delete this Type">Delete</button>}
          <button className="dsa-btn dsa-btn--outline" onClick={reset}>↺ Revert</button>
          <button className="dsa-btn dsa-btn--primary" onClick={save}>{isNew ? 'Save Type' : 'Save changes'}</button>
        </>}
      />
      <div className="dsa-canvas-body">
        {layout === 'split' && <BuilderSplit draft={draft} patch={patch} patchSlot={patchSlot} removeSlot={removeSlot} addSlot={addSlot} patchVariable={patchVariable} removeVariable={removeVariable} addVariable={addVariable} parentCandidates={parentCandidates} browseFilter={browseFilter} setBrowseFilter={setBrowseFilter} mode={mode} brief={brief} setBrief={setBrief} viPropose={viPropose} viSuggestSlots={viSuggestSlots} busy={busy} slotBrowser={slotBrowser} setSlotBrowser={setSlotBrowser}/>}
        {layout === 'wizard' && <BuilderWizard draft={draft} patch={patch} patchSlot={patchSlot} removeSlot={removeSlot} addSlot={addSlot} patchVariable={patchVariable} removeVariable={removeVariable} addVariable={addVariable} parentCandidates={parentCandidates} brief={brief} setBrief={setBrief} viPropose={viPropose} busy={busy}/>}
        {layout === 'canvas' && <BuilderCanvas draft={draft} patch={patch} patchSlot={patchSlot} removeSlot={removeSlot} addSlot={addSlot} patchVariable={patchVariable} removeVariable={removeVariable} addVariable={addVariable} parentCandidates={parentCandidates} mode={mode} brief={brief} setBrief={setBrief} viPropose={viPropose} viSuggestSlots={viSuggestSlots} busy={busy}/>}

        {slotBrowser && (
          <SlotBrowserModal
            slot={slotBrowser.slot}
            onClose={() => setSlotBrowser(null)}
            onApply={(updated) => { patchSlot(slotBrowser.name, updated); setSlotBrowser(null); }}
          />
        )}
      </div>
    </>
  );
}

// ===========================================================================
// Init helper
// ===========================================================================
function initializeDraft(id, R) {
  if (id && R?.get(id)) {
    const t = R.get(id);
    return JSON.parse(JSON.stringify(t));
  }
  return {
    id: 'new.' + Date.now().toString(36),
    name: '',
    layer: 'block',
    family: 'general',
    description: '',
    extends: null,
    slots: {},
    defaults: {},
    variables: [],
    tags: [],
    icon: 'check-square',
    provenance: 'user',
  };
}

// ===========================================================================
// Split layout — tree | canvas | inspector
// ===========================================================================
function BuilderSplit(props) {
  const { draft, mode } = props;
  return (
    <div className="tb-split">
      <aside className="tb-pane tb-left">
        <h6>Type Library</h6>
        <BuilderLibrary draft={draft} {...props}/>
      </aside>
      <main className="tb-pane tb-center">
        <BuilderPreview draft={draft} mode={mode} {...props}/>
      </main>
      <aside className="tb-pane tb-right">
        <BuilderInspector draft={draft} mode={mode} {...props}/>
      </aside>
    </div>
  );
}

// ===========================================================================
// Wizard layout — sequential step-by-step
// ===========================================================================
function BuilderWizard(props) {
  const { draft, patch, brief, setBrief, viPropose, busy, parentCandidates } = props;
  const [step, setStep] = useState_tb(0);
  const STEPS = [
    { label: 'Basics',  desc: 'Name, layer, family, icon' },
    { label: 'Lineage', desc: 'What does it extend?' },
    { label: 'Vi',      desc: 'Optional — let Vi draft the schema' },
    { label: 'Slots',   desc: 'What can it embed?' },
    { label: 'Vars',    desc: 'What changes between runs?' },
    { label: 'Review',  desc: 'Look it over' },
  ];
  return (
    <div className="tb-wizard">
      <ol className="tb-wizard-rail">
        {STEPS.map((s, i) => (
          <li key={i} className={`${i === step ? 'active' : ''} ${i < step ? 'done' : ''}`} onClick={() => setStep(i)}>
            <div className="dot">{i < step ? '✓' : i + 1}</div>
            <div className="meta">
              <div className="t">{s.label}</div>
              <div className="d">{s.desc}</div>
            </div>
          </li>
        ))}
      </ol>
      <div className="tb-wizard-body">
        {step === 0 && <BasicsForm draft={draft} patch={patch}/>}
        {step === 1 && <LineageForm draft={draft} patch={patch} parentCandidates={parentCandidates}/>}
        {step === 2 && <ViForm draft={draft} brief={brief} setBrief={setBrief} viPropose={viPropose} busy={busy}/>}
        {step === 3 && <SlotsEditor {...props}/>}
        {step === 4 && <VariablesEditor {...props}/>}
        {step === 5 && <ReviewPanel draft={draft}/>}
        <div className="tb-wizard-nav">
          <button className="dsa-btn dsa-btn--ghost" onClick={() => setStep(s => Math.max(0, s - 1))} disabled={step === 0}>← Back</button>
          <span style={{flex:1}}/>
          <button className="dsa-btn dsa-btn--primary" onClick={() => setStep(s => Math.min(STEPS.length - 1, s + 1))} disabled={step === STEPS.length - 1}>Continue →</button>
        </div>
      </div>
    </div>
  );
}

// ===========================================================================
// Canvas layout — one full-bleed surface, inspector floats
// ===========================================================================
function BuilderCanvas(props) {
  const { draft, patch, mode } = props;
  const [inspectOpen, setInspectOpen] = useState_tb(true);
  return (
    <div className="tb-canvas">
      <BuilderPreview draft={draft} mode={mode} {...props} big/>
      <button className="tb-canvas-handle" onClick={() => setInspectOpen(o => !o)}>{inspectOpen ? '×' : '⚙'}</button>
      {inspectOpen && (
        <aside className="tb-canvas-inspect">
          <BuilderInspector draft={draft} mode={mode} {...props} embedded/>
        </aside>
      )}
    </div>
  );
}

// ===========================================================================
// Sub-components (split below to keep this file readable)
// ===========================================================================
// — BuilderLibrary, BuilderPreview, BuilderInspector live in TypeBuilder2.jsx

window.TypeBuilder = TypeBuilder;
