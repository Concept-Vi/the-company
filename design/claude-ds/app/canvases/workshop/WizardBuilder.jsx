// canvases/workshop/WizardBuilder.jsx
// Multi-step flow builder — Property Wizard, Onboarding, or Generic.
// Visual mock OR functional prototype (state-driven, navigable).

const { useState: useState_wz, useEffect: useEffect_wz, useMemo: useMemo_wz } = React;

// ============================================================
// Wizard kinds + defaults
// ============================================================

const WIZARD_KINDS = [
  {
    id: 'property',
    label: 'Property Wizard',
    desc: 'The canonical hexagon flow — capture → enrich → publish → linked hubs.',
    shape: 'hexagon',
    steps: [
      { kind: 'capture',  title: 'Capture',  body: 'Drop in floor plans, brochures, or links. Vi extracts the structured data.', fields: [{label:'Source',kind:'file'},{label:'Property name',kind:'text'},{label:'Lot / unit',kind:'text'}] },
      { kind: 'form',     title: 'Enrich',   body: 'Confirm the details Vi pulled out. Anything missing, add it now.', fields: [{label:'Bedrooms',kind:'number'},{label:'Bathrooms',kind:'number'},{label:'Aspect',kind:'choice',options:['North','North-East','East','South-East','South','South-West','West','North-West']},{label:'Floor',kind:'number'}] },
      { kind: 'choice',   title: 'Audience', body: 'Who is this hub for? Vi tailors voice and visuals.',                  options: ['Investors','Owner-occupiers','Tenants','Agents'] },
      { kind: 'review',   title: 'Review',   body: 'Last look. Anything still off?', fields: [] },
      { kind: 'celebrate',title: 'Publish',  body: 'Hub published to conceptv.io. Capture pages live.', fields: [] },
    ],
  },
  {
    id: 'onboarding',
    label: 'Onboarding',
    desc: 'Sign up → set up workspace → invite the team.',
    shape: 'circle',
    steps: [
      { kind: 'capture',  title: 'Get started', body: 'Tell us who you are.', fields: [{label:'Full name',kind:'text'},{label:'Work email',kind:'text'},{label:'Role',kind:'choice',options:['Founder','Developer','Agent','Marketer','Other']}] },
      { kind: 'choice',   title: 'Workspace',   body: 'What are you using ConceptV for?', options: ['Property marketing','Innovation studio','Team brand kit','All of the above'] },
      { kind: 'form',     title: 'Brand kit',   body: 'Drop your logo. Vi seeds a starter palette + voice rules.', fields: [{label:'Workspace name',kind:'text'},{label:'Primary domain',kind:'text'},{label:'Logo',kind:'file'}] },
      { kind: 'form',     title: 'Invite team', body: 'Add up to 5 teammates now.', fields: [{label:'Email 1',kind:'text'},{label:'Email 2',kind:'text'},{label:'Email 3',kind:'text'}] },
      { kind: 'celebrate',title: "You're in",   body: 'Workspace ready. Vi prepared 3 things you can do first.', fields: [] },
    ],
  },
  {
    id: 'generic',
    label: 'Generic flow',
    desc: 'Multi-step form. Define your own steps, fields, and choices.',
    shape: 'diamond',
    steps: [
      { kind: 'form', title: 'Step 1', body: 'Start with the most important question.', fields: [{label:'Field 1',kind:'text'},{label:'Field 2',kind:'text'}] },
      { kind: 'form', title: 'Step 2', body: 'Second step.', fields: [{label:'Field 1',kind:'text'}] },
      { kind: 'review', title: 'Review', body: 'Confirm and submit.', fields: [] },
    ],
  },
];

const STEP_KINDS = [
  { id: 'capture',   label: 'Capture',   desc: 'Drop files, paste a link, or import.' },
  { id: 'form',      label: 'Form',      desc: 'Structured fields.' },
  { id: 'choice',    label: 'Choice',    desc: 'Single-select.' },
  { id: 'review',    label: 'Review',    desc: 'Summary before submit.' },
  { id: 'celebrate', label: 'Celebrate', desc: 'Success / done state.' },
];

const LAYOUTS = [
  { id: 'sidebar',  label: 'Sidebar',  desc: 'Numbered list down the left, content on the right.' },
  { id: 'progress', label: 'Progress', desc: 'Top progress bar with step pills.' },
  { id: 'cards',    label: 'Cards',    desc: 'One card per step, advances on submit.' },
];

function blankWizard(kindId) {
  const def = WIZARD_KINDS.find(k => k.id === kindId) || WIZARD_KINDS[0];
  return {
    wizardKind: def.id,
    layout: 'sidebar',
    mode: 'mock',
    steps: def.steps.map((s, i) => ({ id: 'wz-' + i + '-' + Math.random().toString(36).slice(2, 7), ...s })),
  };
}

async function viDraftWizard(brief, kindId) {
  const auto = (v) => !v || v === 'auto';
  const fixedKind = auto(kindId) ? null : kindId;
  const kindDoc = WIZARD_KINDS.map(k => `  - "${k.id}" — ${k.label}: ${k.desc}`).join('\n');

  const prompt = `You are Vi, drafting a multi-step wizard inside ConceptV Studio.

${window.CV_AI.get('voice.conceptv').text}
Canonical shapes: Property Wizard → hexagon, Virtual Hub → octagon, Vi → diamond, User Portal → circle.

User's brief: "${brief}"

WIZARD KIND ${fixedKind ? `(LOCKED to "${fixedKind}")` : '(pick the best fit for the brief)'}:
${kindDoc}

Plan 3-6 steps. Step kinds:
  - capture: drop files, paste links, import. Use early for input.
  - form: structured fields (label + kind: text|number|choice|file).
  - choice: single-select between options.
  - review: summary before submit.
  - celebrate: success/done state.

Respond ONLY as JSON:
{
  "wizardKind": "property|onboarding|generic",
  "steps": [
    {"kind":"capture|form|choice|review|celebrate","title":"3-5 word title","body":"one sentence describing what the user does","fields":[{"label":"...","kind":"text|number|choice|file","options":["only for choice"]}],"options":["only for kind=choice"]}
  ]
}

Tailor everything to the brief. Concrete labels. Last step is usually 'review' or 'celebrate'.`;

  const reply = await window.CV_AI.complete(prompt);
  let parsed = null;
  try { parsed = JSON.parse(reply); }
  catch {
    const m = String(reply).match(/\{[\s\S]*\}/);
    if (m) { try { parsed = JSON.parse(m[0]); } catch {} }
  }
  if (!parsed || !Array.isArray(parsed.steps)) throw new Error('Vi returned no parsable wizard');
  const resolvedKind = fixedKind || (WIZARD_KINDS.some(k => k.id === parsed.wizardKind) ? parsed.wizardKind : 'generic');
  return {
    wizardKind: resolvedKind,
    layout: 'sidebar',
    mode: 'mock',
    steps: parsed.steps.slice(0, 8).map((s, i) => ({
      id: 'wz-' + i + '-' + Math.random().toString(36).slice(2, 7),
      kind: ['capture','form','choice','review','celebrate'].includes(s.kind) ? s.kind : 'form',
      title: s.title || 'Step',
      body: s.body || '',
      fields: Array.isArray(s.fields) ? s.fields : [],
      options: Array.isArray(s.options) ? s.options : undefined,
    })),
  };
}

// ============================================================
// Editor
// ============================================================

function WizardBuilder({ doc, saveDoc, closeDoc, onSaveTemplate }) {
  const WSCandidateGallery = window.WSCandidateGallery;
  const [activeStep, setActiveStep] = useState_wz(0);
  const [showExport, setShowExport] = useState_wz(false);
  const [protoStep, setProtoStep] = useState_wz(0);
  const [protoState, setProtoState] = useState_wz({});
  const [galleryState, setGalleryState] = useState_wz(null);

  useEffect_wz(() => {
    if (activeStep > (doc.steps?.length || 1) - 1) setActiveStep(0);
  }, [doc.steps?.length]);

  if (!doc) return null;
  const { wizardKind, layout, mode, steps } = doc;
  const wKind = WIZARD_KINDS.find(k => k.id === wizardKind) || WIZARD_KINDS[0];

  function update(patch) { saveDoc({ ...doc, ...patch }); }

  async function runGallery({ target, title, onPickOverride }) {
    setGalleryState({ title, busy: true, candidates: [], onPickOverride, target });
    try {
      const cands = await window.WS_AI.generateCandidates({ doc, target, count: 3 });
      setGalleryState(s => s ? { ...s, busy: false, candidates: cands } : s);
    } catch {
      setGalleryState(null);
      window.dsaToast?.('Vi could not generate options');
    }
  }
  async function refineGallery(hint) {
    if (!galleryState) return;
    setGalleryState(s => ({ ...s, busy: true }));
    try {
      const cands = await window.WS_AI.generateCandidates({ doc, target: galleryState.target, count: 3, brief: hint });
      setGalleryState(s => s ? { ...s, busy: false, candidates: cands } : s);
    } catch { setGalleryState(s => s ? { ...s, busy: false } : s); }
  }
  function pickCandidate(cand) {
    if (galleryState?.onPickOverride) galleryState.onPickOverride(cand);
    else if (cand.diff) saveDoc(window.WS_AI.applyDiff(doc, cand.diff));
    setGalleryState(null);
    window.dsaToast?.('Applied');
  }
  function setKind(id) {
    if (!confirm(`Switch wizard kind to "${WIZARD_KINDS.find(k => k.id === id)?.label}"? This will replace your steps.`)) return;
    const next = blankWizard(id);
    saveDoc({ ...doc, wizardKind: id, steps: next.steps });
    setActiveStep(0);
  }
  function setStep(i, patch) { update({ steps: steps.map((s, j) => i === j ? { ...s, ...patch } : s) }); }
  function moveStep(from, to) {
    if (to < 0 || to >= steps.length) return;
    const next = [...steps]; const [m] = next.splice(from, 1); next.splice(to, 0, m);
    update({ steps: next });
    setActiveStep(to);
  }
  function removeStep(i) {
    if (steps.length <= 1) { window.dsaToast?.('Need at least one step'); return; }
    update({ steps: steps.filter((_, j) => j !== i) });
    setActiveStep(Math.max(0, Math.min(i, steps.length - 2)));
  }
  function addStep(kind = 'form') {
    const newStep = { id: 'wz-' + Date.now() + '-' + Math.random().toString(36).slice(2, 5), kind, title: STEP_KINDS.find(s => s.id === kind)?.label || 'New step', body: '', fields: kind === 'form' ? [{ label: 'Field', kind: 'text' }] : [], options: kind === 'choice' ? ['Option A', 'Option B'] : undefined };
    update({ steps: [...steps, newStep] });
    setActiveStep(steps.length);
  }

  return (
    <>
      <CanvasHeader
        title={doc.title}
        sub={`Wizard · ${wKind.label} · ${steps.length} step${steps.length === 1 ? '' : 's'} · ${LAYOUTS.find(l => l.id === layout)?.label} layout`}
        actions={<>
          <button className="dsa-btn dsa-btn--ghost" onClick={closeDoc}>← All docs</button>
          <div className="ws-mode-seg">
            <button className={mode === 'mock' ? 'active' : ''} onClick={() => update({ mode: 'mock' })} title="Visual mock — static frame">Mock</button>
            <button className={mode === 'proto' ? 'active' : ''} onClick={() => { update({ mode: 'proto' }); setProtoStep(0); setProtoState({}); }} title="Functional prototype — click through, state preserved">Prototype</button>
          </div>
          <button className="dsa-btn dsa-btn--outline dsa-btn--sm" onClick={async () => {
            window.dsaToast?.('Vi is extracting a Type…');
            try {
              const draft = await window.CV_TYPES_SAVE.fromWizard(doc);
              window.CV_TYPES_PROMPT.open(draft);
            } catch { window.dsaToast?.('Could not promote'); }
          }} title="Promote this wizard into a reusable Type in the Registry">
            <ViShape size={10}/> + Save as Type
          </button>
          <button className="dsa-btn dsa-btn--outline" onClick={() => onSaveTemplate?.(doc)}>+ Save as template</button>
          <span style={{position:'relative'}} onClick={e => e.stopPropagation()}>
            <button className="dsa-btn dsa-btn--primary" onClick={() => setShowExport(s => !s)}>Export ↗</button>
            {showExport && <WizardExportMenu doc={doc} onClose={() => setShowExport(false)}/>}
          </span>
        </>}
      />
      <div className="dsa-canvas-body">
        <div className="ws-doc-head">
          <input className="ws-doc-title" value={doc.title} onChange={e => update({ title: e.target.value })}/>
          <span className="ws-doc-meta">Auto-saved · {new Date(doc.createdAt).toLocaleDateString()}</span>
        </div>

        <div className="ws-wb-bar">
          <div className="ws-wb-group">
            <div className="ws-wb-label">Wizard kind</div>
            <div className="ws-wb-pills">
              {(window.WIZARD_KINDS || WIZARD_KINDS).map(k => (
                <button key={k.id} className={`ws-wb-pill ${wizardKind === k.id ? 'active' : ''}`} onClick={() => setKind(k.id)} title={k.desc}>
                  <ShapeGlyph shape={k.shape} size={12}/>{k.label}
                  {k.provenance && k.provenance !== 'built-in' && <span className="cv-type-prov cv-type-prov-user" style={{marginLeft:6,padding:'1px 4px',fontSize:8}}>{k.provenance}</span>}
                </button>
              ))}
            </div>
          </div>
          <div className="ws-wb-group">
            <div className="ws-wb-label">Layout</div>
            <div className="ws-wb-pills">
              {LAYOUTS.map(l => (
                <button key={l.id} className={`ws-wb-pill ${layout === l.id ? 'active' : ''}`} onClick={() => update({ layout: l.id })} title={l.desc}>
                  {l.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="ws-wz-workspace">
          {/* Top strip: steps list */}
          <header className="ws-wz-strip">
            <div className="ws-wz-strip-label">
              <h5>Steps</h5>
              <span className="dim">{steps.length} total</span>
            </div>
            <div className="ws-wz-strip-list">
              {steps.map((s, i) => (
                <div key={s.id}
                  className={`ws-wz-strip-item ${i === activeStep ? 'active' : ''} ${i === protoStep && mode === 'proto' ? 'proto-active' : ''}`}
                  onClick={() => setActiveStep(i)}>
                  <div className="num">{i + 1}</div>
                  <div className="meta">
                    <div className="title">{s.title}</div>
                    <div className="kind">{s.kind}</div>
                  </div>
                  <div className="actions">
                    <button title="Move left" onClick={(e) => { e.stopPropagation(); moveStep(i, i - 1); }}>←</button>
                    <button title="Move right" onClick={(e) => { e.stopPropagation(); moveStep(i, i + 1); }}>→</button>
                    <button title="Remove" onClick={(e) => { e.stopPropagation(); removeStep(i); }}>✕</button>
                  </div>
                </div>
              ))}
              <div className="ws-wz-strip-add">
                {STEP_KINDS.map(k => (
                  <button key={k.id} onClick={() => addStep(k.id)} title={k.desc}>+ {k.label}</button>
                ))}
                <button
                  onClick={() => runGallery({ target: { kind: 'wizard.step.insert', atIdx: steps.length }, title: '3 Vi step proposals' })}
                  title="Vi: 3 step proposals"
                  style={{background:'var(--bg-dark)',color:'var(--fg-inverse)',border:'none',borderColor:'var(--bg-dark)'}}>
                  + Vi step
                </button>
              </div>
            </div>
          </header>

          {/* Center: preview */}
          <main className="ws-wz-stage">
            <WizardRender
              doc={doc}
              activeIndex={mode === 'proto' ? protoStep : activeStep}
              mode={mode}
              state={protoState}
              setState={setProtoState}
              onAdvance={() => {
                const cur = steps[protoStep];
                // Branching: if this step is a choice with gotoOnChoice rules and the user picked an option, follow it
                if (cur?.kind === 'choice' && cur.gotoOnChoice) {
                  const picked = (protoState[cur.id] || {})._pick;
                  let next = cur.gotoOnChoice[picked] ?? cur.gotoOnChoice._default;
                  if (typeof next === 'string') {
                    if (next === 'next') next = protoStep + 1;
                    else if (next === 'end') next = steps.length - 1;
                  }
                  if (typeof next === 'number' && next >= 0 && next < steps.length) {
                    setProtoStep(next);
                    return;
                  }
                }
                setProtoStep(p => Math.min(p + 1, steps.length - 1));
              }}
              onBack={() => setProtoStep(p => Math.max(p - 1, 0))}
              onJump={(i) => setProtoStep(i)}
            />
            {mode === 'proto' && (
              <div style={{textAlign:'center',marginTop:14,font:'500 11px/1.4 var(--font-body)',color:'var(--fg-muted)'}}>
                Interactive — click <b>Next</b>, type into fields, choose options. State persists across steps.{' '}
                <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={() => { setProtoStep(0); setProtoState({}); }}>Restart</button>
              </div>
            )}
          </main>

          {/* Right: step editor */}
          <aside className="ws-wz-edit">
            {steps[activeStep] && (
              <StepEditor
                step={steps[activeStep]}
                idx={activeStep}
                onChange={(patch) => setStep(activeStep, patch)}
                onAlternate={() => runGallery({ target: { kind: 'wizard.step.alternate', stepIdx: activeStep }, title: `3 alternative versions of "${steps[activeStep].title}"` })}
              />
            )}
          </aside>
        </div>
      </div>
      <WSCandidateGallery
        open={!!galleryState}
        title={galleryState?.title}
        busy={galleryState?.busy}
        candidates={galleryState?.candidates}
        doc={doc}
        onPick={pickCandidate}
        onClose={() => setGalleryState(null)}
        onRefine={refineGallery}
      />
    </>
  );
}

// ============================================================
// Step editor (right panel)
// ============================================================

function StepEditor({ step, idx, onChange, onAlternate }) {
  function setField(i, patch) { onChange({ fields: step.fields.map((f, j) => i === j ? { ...f, ...patch } : f) }); }
  function removeField(i)     { onChange({ fields: step.fields.filter((_, j) => j !== i) }); }
  function addField()         { onChange({ fields: [...(step.fields || []), { label: 'Field', kind: 'text' }] }); }
  function setOption(i, val)  { onChange({ options: step.options.map((o, j) => i === j ? val : o) }); }
  function removeOption(i)    { onChange({ options: step.options.filter((_, j) => j !== i) }); }
  function addOption()        { onChange({ options: [...(step.options || []), 'Option ' + ((step.options || []).length + 1)] }); }

  return (
    <div className="ws-wz-edit-inner">
      <div style={{display:'flex',alignItems:'center',gap:8}}>
        <h5 style={{margin:0,padding:0,borderBottom:'none'}}>Step {idx + 1}</h5>
        {onAlternate && (
          <button
            onClick={onAlternate}
            title="Vi: 3 alternative versions of this step"
            style={{
              marginLeft:'auto', padding:'3px 7px', borderRadius:999,
              background:'var(--bg-dark)', color:'var(--fg-inverse)',
              border:'none', cursor:'pointer',
              font:'600 9px/1 var(--font-body)', letterSpacing:'0.04em',
              display:'inline-flex', alignItems:'center', gap:4,
            }}>
            <ViShape size={10}/> alts
          </button>
        )}
      </div>
      <div style={{height:1,background:'var(--accent-gold-soft)',marginTop:6,marginBottom:10}}/>
      <label className="ws-wb-field"><span>Kind</span>
        <select value={step.kind} onChange={e => onChange({ kind: e.target.value, fields: e.target.value === 'choice' ? [] : step.fields, options: e.target.value === 'choice' ? (step.options || ['Option A', 'Option B']) : undefined })}>
          {STEP_KINDS.map(s => <option key={s.id} value={s.id}>{s.label}</option>)}
        </select>
      </label>
      <label className="ws-wb-field"><span>Title</span>
        <input value={step.title} onChange={e => onChange({ title: e.target.value })}/>
      </label>
      <label className="ws-wb-field"><span>Body</span>
        <textarea rows="2" value={step.body || ''} onChange={e => onChange({ body: e.target.value })}/>
      </label>

      {step.kind === 'form' && (
        <>
          <h5>Fields</h5>
          {(step.fields || []).map((f, i) => (
            <div key={i} className="ws-wb-row">
              <input placeholder="Label" value={f.label || ''} onChange={e => setField(i, { label: e.target.value })}/>
              <select value={f.kind || 'text'} onChange={e => setField(i, { kind: e.target.value })}>
                <option value="text">text</option>
                <option value="number">number</option>
                <option value="choice">choice</option>
                <option value="file">file</option>
              </select>
              <button onClick={() => removeField(i)}>✕</button>
            </div>
          ))}
          <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={addField}>+ Field</button>
        </>
      )}

      {step.kind === 'choice' && (
        <>
          <h5>Options</h5>
          {(step.options || []).map((o, i) => (
            <div key={i} className="ws-wb-row">
              <input value={o} onChange={e => setOption(i, e.target.value)}/>
              <button onClick={() => removeOption(i)}>✕</button>
            </div>
          ))}
          <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={addOption}>+ Option</button>

          <h5>Branching (in prototype mode)</h5>
          <p style={{font:'400 11px/1.5 var(--font-body)',color:'var(--fg-muted)',margin:'0 0 8px'}}>
            When user picks each option, where should the wizard go next?
          </p>
          {(step.options || []).map((o, i) => {
            const cur = (step.gotoOnChoice || {})[o] ?? 'next';
            return (
              <div key={'b-' + i} className="ws-wb-row" style={{gridTemplateColumns:'1fr 1fr'}}>
                <input value={o} readOnly style={{opacity:0.7}}/>
                <select
                  value={String(cur)}
                  onChange={e => {
                    const v = e.target.value;
                    const next = { ...(step.gotoOnChoice || {}) };
                    if (v === 'next') delete next[o]; else next[o] = isNaN(+v) ? v : +v;
                    onChange({ gotoOnChoice: next });
                  }}>
                  <option value="next">→ next step</option>
                  <option value="end">→ end (last step)</option>
                  {(window.WS_AI?.bridge?.getActive?.()?.steps || []).map((_, j) => (
                    <option key={j} value={String(j)}>→ step {j + 1}</option>
                  ))}
                </select>
              </div>
            );
          })}
        </>
      )}

      {step.kind === 'capture' && (
        <p className="dim" style={{font:'400 11px/1.5 var(--font-body)',color:'var(--fg-muted)',marginTop:8}}>
          The capture step shows a dropzone for files. Vi will extract structured data. You can still add fallback fields below.
        </p>
      )}

      <h5>Vi</h5>
      <ViStepRefine step={step} onChange={onChange} wizardKind={null}/>
    </div>
  );
}

function ViStepRefine({ step, onChange }) {
  const [msg, setMsg] = useState_wz('');
  const [busy, setBusy] = useState_wz(false);
  async function go() {
    if (!msg.trim() || busy) return;
    setBusy(true);
    try {
      const prompt = `You are Vi, revising one step in a ConceptV multi-step wizard. Brand voice: sentence case, second person, no exclamation marks, no emoji.

Current step: ${JSON.stringify(step, null, 2)}
User asks: "${msg.trim()}"

Return ONLY JSON for the revised step (same shape — kind, title, body, fields, options). Do not change the kind unless asked.`;
      const reply = await window.CV_AI.complete(prompt);
      let parsed = null;
      try { parsed = JSON.parse(reply); }
      catch {
        const m = String(reply).match(/\{[\s\S]*\}/);
        if (m) { try { parsed = JSON.parse(m[0]); } catch {} }
      }
      if (!parsed) throw new Error();
      onChange({
        title: parsed.title || step.title,
        body: parsed.body || step.body,
        fields: Array.isArray(parsed.fields) ? parsed.fields : step.fields,
        options: Array.isArray(parsed.options) ? parsed.options : step.options,
      });
      window.dsaToast?.('Step refined');
      setMsg('');
    } catch { window.dsaToast?.('Vi could not refine — try again'); }
    finally { setBusy(false); }
  }
  return (
    <div className="ws-wb-vi">
      <ViShape size={14}/>
      <textarea rows="2" placeholder='Ask Vi: "make the copy more urgent", "add an investor-only field"' value={msg} onChange={e => setMsg(e.target.value)}/>
      <button className="dsa-btn dsa-btn--ai dsa-btn--sm" onClick={go} disabled={busy || !msg.trim()}>{busy ? '…' : 'Refine'}</button>
    </div>
  );
}

// ============================================================
// Wizard renderer — the visible flow
// ============================================================

function WizardRender({ doc, activeIndex, mode, state, setState, onAdvance, onBack, onJump }) {
  const { layout, steps, wizardKind } = doc;
  const wKind = WIZARD_KINDS.find(k => k.id === wizardKind) || WIZARD_KINDS[0];
  const step = steps[activeIndex];
  const proto = mode === 'proto';

  return (
    <div className={`ws-wz-frame layout-${layout}`}>
      {layout === 'sidebar' && (
        <>
          <div className="ws-wz-rail">
            <div className="ws-wz-brand">
              <ShapeGlyph shape={wKind.shape} size={22}/>
              <div>
                <div className="brand">ConceptV</div>
                <div className="kind">{wKind.label}</div>
              </div>
            </div>
            <ol className="ws-wz-steps">
              {steps.map((s, i) => (
                <li key={s.id}
                  className={`${i === activeIndex ? 'active' : ''} ${i < activeIndex ? 'done' : ''}`}
                  onClick={() => proto && onJump(i)}
                  style={{ cursor: proto ? 'pointer' : 'default' }}>
                  <div className="dot">{i < activeIndex ? '✓' : i + 1}</div>
                  <div className="label">
                    <div className="title">{s.title}</div>
                    <div className="kind">{s.kind}</div>
                  </div>
                </li>
              ))}
            </ol>
          </div>
          <StepBody
            step={step}
            idx={activeIndex}
            total={steps.length}
            proto={proto}
            state={state}
            setState={setState}
            onAdvance={onAdvance}
            onBack={onBack}
          />
        </>
      )}
      {layout === 'progress' && (
        <div className="ws-wz-progress-shell">
          <div className="ws-wz-progress-top">
            <div className="brand"><ShapeGlyph shape={wKind.shape} size={18}/> {wKind.label}</div>
            <div className="bar">
              <div className="fill" style={{ width: `${((activeIndex + 1) / steps.length) * 100}%` }}/>
            </div>
            <div className="pills">
              {steps.map((s, i) => (
                <button key={s.id} className={`${i === activeIndex ? 'active' : ''} ${i < activeIndex ? 'done' : ''}`} onClick={() => proto && onJump(i)} disabled={!proto}>
                  {i + 1}. {s.title}
                </button>
              ))}
            </div>
          </div>
          <StepBody step={step} idx={activeIndex} total={steps.length} proto={proto} state={state} setState={setState} onAdvance={onAdvance} onBack={onBack}/>
        </div>
      )}
      {layout === 'cards' && (
        <div className="ws-wz-cards-shell">
          <div className="ws-wz-cards-head">
            <div className="brand"><ShapeGlyph shape={wKind.shape} size={18}/> {wKind.label} · step {activeIndex + 1} of {steps.length}</div>
          </div>
          <div className="ws-wz-card-stack">
            {steps.slice(Math.max(0, activeIndex - 1), activeIndex + 2).map((s, oi) => {
              const realIdx = Math.max(0, activeIndex - 1) + oi;
              const offset = realIdx - activeIndex;
              if (offset === 0) {
                return <div key={s.id} className="ws-wz-card front">
                  <StepBody step={s} idx={realIdx} total={steps.length} proto={proto} state={state} setState={setState} onAdvance={onAdvance} onBack={onBack}/>
                </div>;
              }
              return <div key={s.id} className={`ws-wz-card ghost ${offset > 0 ? 'next' : 'prev'}`}>
                <div className="ghost-title">{s.title}</div>
              </div>;
            })}
          </div>
        </div>
      )}
    </div>
  );
}

function StepBody({ step, idx, total, proto, state, setState, onAdvance, onBack }) {
  const value = state[step.id] || {};
  function setValue(field, v) {
    if (!proto) return;
    setState({ ...state, [step.id]: { ...value, [field]: v } });
  }

  return (
    <div className="ws-wz-content">
      <div className="ws-wz-content-head">
        <div className="eyebrow">Step {idx + 1} of {total}</div>
        <h2>{step.title}</h2>
        {step.body && <p>{step.body}</p>}
      </div>

      <div className="ws-wz-content-body">
        {step.kind === 'capture' && (
          <>
            <div className="ws-wz-dropzone">
              <div className="plus">⤓</div>
              <div className="dz-label">Drop files, paste a link</div>
              <div className="dz-hint">Vi extracts plans, brochures, listings, calendar URLs — anything structured.</div>
            </div>
            {(step.fields || []).map((f, i) => (
              <FieldInput key={i} f={f} v={value[f.label]} onChange={v => setValue(f.label, v)} proto={proto}/>
            ))}
          </>
        )}
        {step.kind === 'form' && (
          <div className="ws-wz-fields">
            {(step.fields || []).map((f, i) => (
              <FieldInput key={i} f={f} v={value[f.label]} onChange={v => setValue(f.label, v)} proto={proto}/>
            ))}
          </div>
        )}
        {step.kind === 'choice' && (
          <div className="ws-wz-choice">
            {(step.options || []).map((o, i) => (
              <button key={i}
                className={`ws-wz-choice-card ${value._pick === o ? 'picked' : ''}`}
                onClick={() => proto && setValue('_pick', o)}>
                <span className="bullet">{value._pick === o ? '●' : '○'}</span>
                <span className="lbl">{o}</span>
              </button>
            ))}
          </div>
        )}
        {step.kind === 'review' && (
          <div className="ws-wz-review">
            <div className="row eyebrow">Summary</div>
            <div className="row"><span>Step type</span><span>{step.kind}</span></div>
            {Object.entries(state).flatMap(([sid, sv]) => Object.entries(sv).map(([k, v]) => (
              <div className="row" key={sid + k}><span>{k}</span><span>{String(v)}</span></div>
            )))}
            {!Object.keys(state).length && (
              <div className="row dim">{proto ? "No fields filled yet. Click 'Restart' to walk through." : "Run in Prototype mode to capture state."}</div>
            )}
          </div>
        )}
        {step.kind === 'celebrate' && (
          <div className="ws-wz-celebrate">
            <div className="big">✓</div>
            <div className="head">Done</div>
            <div className="sub">{step.body || 'You finished the flow.'}</div>
          </div>
        )}
      </div>

      <div className="ws-wz-actions">
        <button className="dsa-btn dsa-btn--ghost" onClick={onBack} disabled={idx === 0 || !proto}>← Back</button>
        <span style={{flex:1}}/>
        {idx < total - 1
          ? <button className="dsa-btn dsa-btn--primary" onClick={onAdvance} disabled={!proto && idx < total - 1 ? false : false}>{proto ? 'Continue →' : 'Continue →'}</button>
          : <button className="dsa-btn dsa-btn--primary" onClick={onAdvance} disabled>Finish</button>}
      </div>
    </div>
  );
}

function FieldInput({ f, v, onChange, proto }) {
  if (f.kind === 'choice') {
    return (
      <label className="ws-wz-field">
        <span>{f.label}</span>
        <select value={v || ''} onChange={e => onChange(e.target.value)} disabled={!proto}>
          <option value="">—</option>
          {(f.options || ['Option A', 'Option B']).map(o => <option key={o} value={o}>{o}</option>)}
        </select>
      </label>
    );
  }
  if (f.kind === 'file') {
    return (
      <label className="ws-wz-field file">
        <span>{f.label}</span>
        <div className="filebox">
          <span>⤓ Drop or pick a file</span>
        </div>
      </label>
    );
  }
  return (
    <label className="ws-wz-field">
      <span>{f.label}</span>
      <input
        type={f.kind === 'number' ? 'number' : 'text'}
        value={v || ''}
        onChange={e => onChange(e.target.value)}
        disabled={!proto}
        placeholder={proto ? '' : 'placeholder'}
      />
    </label>
  );
}

function ShapeGlyph({ shape, size = 16 }) {
  const s = size;
  const stroke = 'var(--accent-gold)';
  const fill = 'var(--accent-gold-soft)';
  if (shape === 'hexagon') {
    const r = s / 2 - 1;
    const cx = s / 2, cy = s / 2;
    const pts = [];
    for (let i = 0; i < 6; i++) {
      const a = Math.PI / 6 + i * Math.PI / 3;
      pts.push(`${(cx + r * Math.cos(a)).toFixed(2)},${(cy + r * Math.sin(a)).toFixed(2)}`);
    }
    return <svg width={s} height={s} viewBox={`0 0 ${s} ${s}`}><polygon points={pts.join(' ')} fill={fill} stroke={stroke} strokeWidth="1.5"/></svg>;
  }
  if (shape === 'diamond') {
    return <svg width={s} height={s} viewBox={`0 0 ${s} ${s}`}><polygon points={`${s/2},1 ${s-1},${s/2} ${s/2},${s-1} 1,${s/2}`} fill={fill} stroke={stroke} strokeWidth="1.5"/></svg>;
  }
  // circle
  return <svg width={s} height={s} viewBox={`0 0 ${s} ${s}`}><circle cx={s/2} cy={s/2} r={s/2 - 1} fill={fill} stroke={stroke} strokeWidth="1.5"/></svg>;
}

// ============================================================
// Export
// ============================================================

function WizardExportMenu({ doc, onClose }) {
  const code = useMemo_wz(() => wizardToJSX(doc), [doc]);
  function downloadJSX() {
    const blob = new Blob([code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = `${slugify(doc.title)}-wizard.jsx`; a.click();
    URL.revokeObjectURL(url);
    onClose?.();
  }
  function printPDF() { window.print(); onClose?.(); }
  function copyCode() { navigator.clipboard?.writeText(code); window.dsaToast?.('JSX copied'); }
  return (
    <div className="ws-export-menu" onClick={e => e.stopPropagation()}>
      <button onClick={copyCode}>📋 Copy JSX</button>
      <button onClick={downloadJSX}>⬇ Download .jsx</button>
      <button onClick={printPDF}>🖨 Print → PDF</button>
    </div>
  );
}

function wizardToJSX(doc) {
  return `// ${doc.title} — ConceptV wizard (${doc.wizardKind})
// Generated from ConceptV Studio · Workshop · Wizard Builder
import React, { useState } from 'react';

const STEPS = ${JSON.stringify(doc.steps, null, 2)};

export default function ${pascalCase(doc.title)}Wizard() {
  const [idx, setIdx] = useState(0);
  const [state, setState] = useState({});
  const step = STEPS[idx];
  const total = STEPS.length;

  function update(field, v) {
    setState(s => ({ ...s, [step.id]: { ...(s[step.id] || {}), [field]: v } }));
  }

  return (
    <div style={{display:'grid',gridTemplateColumns:'260px 1fr',minHeight:480,background:'var(--bg-canvas)',borderRadius:'var(--r-xl)',overflow:'hidden',boxShadow:'var(--shadow-pop)',fontFamily:'var(--font-body)'}}>
      <aside style={{padding:'24px 22px',background:'var(--bg-muted)',borderRight:'1px solid var(--border-faint)'}}>
        <div style={{font:'700 14px/1 var(--font-display)',color:'var(--accent-bronze)',marginBottom:18}}>${doc.title}</div>
        <ol style={{listStyle:'none',padding:0,margin:0,display:'flex',flexDirection:'column',gap:10}}>
          {STEPS.map((s, i) => (
            <li key={s.id} style={{
              display:'flex',alignItems:'center',gap:10,
              opacity: i <= idx ? 1 : 0.5,
              cursor: 'pointer',
            }} onClick={() => setIdx(i)}>
              <div style={{
                width:24,height:24,borderRadius:'50%',
                background: i <= idx ? 'var(--accent-gold)' : 'var(--bg-surface)',
                border:'1.5px solid var(--accent-gold)',
                display:'flex',alignItems:'center',justifyContent:'center',
                font:'700 11px/1 var(--font-mono)',color:'var(--fg-primary)',
              }}>{i < idx ? '✓' : i + 1}</div>
              <span style={{font:'500 12px/1.2 var(--font-body)'}}>{s.title}</span>
            </li>
          ))}
        </ol>
      </aside>
      <main style={{padding:'28px 32px',display:'flex',flexDirection:'column',gap:18}}>
        <div>
          <div style={{font:'600 10px/1 var(--font-body)',color:'var(--accent-bronze)',letterSpacing:'0.1em',textTransform:'uppercase',marginBottom:6}}>Step {idx + 1} of {total}</div>
          <h2 style={{font:'700 28px/1.1 var(--font-display)',color:'var(--fg-primary)',margin:0,letterSpacing:'-0.02em'}}>{step.title}</h2>
          {step.body && <p style={{font:'400 13px/1.5 var(--font-body)',color:'var(--fg-secondary)',margin:'8px 0 0'}}>{step.body}</p>}
        </div>

        <div style={{flex:1,display:'flex',flexDirection:'column',gap:12}}>
          {(step.fields || []).map((f, i) => (
            <label key={i} style={{display:'flex',flexDirection:'column',gap:5}}>
              <span style={{font:'600 11px/1 var(--font-body)',color:'var(--fg-secondary)',letterSpacing:'0.04em',textTransform:'uppercase'}}>{f.label}</span>
              {f.kind === 'choice'
                ? <select value={(state[step.id]||{})[f.label] || ''} onChange={e => update(f.label, e.target.value)} style={{padding:'10px 12px',border:'1.5px solid var(--accent-gold)',borderRadius:'var(--r-md)',font:'400 13px/1 var(--font-body)',background:'var(--bg-surface)'}}>
                    <option value="">—</option>
                    {(f.options || []).map(o => <option key={o} value={o}>{o}</option>)}
                  </select>
                : <input type={f.kind === 'number' ? 'number' : 'text'} value={(state[step.id]||{})[f.label] || ''} onChange={e => update(f.label, e.target.value)}
                    style={{padding:'10px 12px',border:'1.5px solid var(--accent-gold)',borderRadius:'var(--r-md)',font:'400 13px/1 var(--font-body)',background:'var(--bg-surface)',outline:'none'}}/>}
            </label>
          ))}
          {step.kind === 'choice' && (step.options || []).map((o, i) => (
            <button key={i}
              onClick={() => update('_pick', o)}
              style={{
                padding:'14px 18px',textAlign:'left',
                background: (state[step.id]||{})._pick === o ? 'var(--accent-gold-soft)' : 'var(--bg-surface)',
                border:'1.5px solid ' + ((state[step.id]||{})._pick === o ? 'var(--accent-gold)' : 'var(--border-default)'),
                borderRadius:'var(--r-md)',cursor:'pointer',
                font:'500 13px/1.3 var(--font-body)',color:'var(--fg-primary)',
              }}>{o}</button>
          ))}
        </div>

        <div style={{display:'flex',gap:8}}>
          <button onClick={() => setIdx(Math.max(0, idx - 1))} disabled={idx === 0}
            style={{padding:'10px 16px',background:'transparent',border:'none',color:'var(--fg-secondary)',cursor:idx === 0 ? 'not-allowed' : 'pointer',font:'600 12px/1 var(--font-body)'}}>← Back</button>
          <span style={{flex:1}}/>
          <button onClick={() => setIdx(Math.min(total - 1, idx + 1))}
            style={{padding:'10px 18px',background:'var(--accent-gold)',color:'var(--fg-primary)',border:'none',borderRadius:'var(--r-md)',cursor:'pointer',font:'600 12px/1 var(--font-body)',boxShadow:'var(--shadow-sm)'}}>
            {idx < total - 1 ? 'Continue →' : 'Finish'}
          </button>
        </div>
      </main>
    </div>
  );
}
`;
}

function pascalCase(s) {
  return String(s).replace(/[^a-z0-9]+/gi, ' ').trim().split(/\s+/).map(w => w[0]?.toUpperCase() + w.slice(1).toLowerCase()).join('') || 'Wizard';
}
function slugify(s) {
  return String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'wizard';
}

// ============================================================
// Exports
// ============================================================

window.WizardBuilder = WizardBuilder;
window.WIZARD_KINDS = WIZARD_KINDS;
window.viDraftWizard = viDraftWizard;
window.blankWizard = blankWizard;
