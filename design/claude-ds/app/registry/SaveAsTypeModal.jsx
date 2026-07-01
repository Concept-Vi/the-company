// app/registry/SaveAsTypeModal.jsx
// A small modal that surfaces anywhere — wraps Vi's promoteInstance result
// in a quick review/edit step before committing to the registry.

const { useState: useState_sat, useEffect: useEffect_sat } = React;

function SaveAsTypeModal() {
  const [draft, setDraft] = useState_sat(null);
  const [busy, setBusy] = useState_sat(false);

  useEffect_sat(() => {
    return window.CV_TYPES_PROMPT?.subscribe((d) => setDraft(d));
  }, []);

  if (!draft) return null;

  function patch(p) { setDraft(d => ({ ...d, ...p })); }
  function patchVar(i, vp) {
    setDraft(d => ({ ...d, variables: (d.variables || []).map((v, j) => i === j ? { ...v, ...vp } : v) }));
  }
  function rmVar(i) { setDraft(d => ({ ...d, variables: (d.variables || []).filter((_, j) => i !== j) })); }
  function addVar() {
    setDraft(d => ({ ...d, variables: [...(d.variables || []), { key: 'var_' + ((d.variables||[]).length + 1), label: 'New', default: '', kind: 'text' }] }));
  }

  function save() {
    if (!draft.name?.trim()) { window.dsaToast?.('Name your Type'); return; }
    if (!draft.id?.trim())   { window.dsaToast?.('Give it an id'); return; }
    setBusy(true);
    try {
      const t = window.CV_REGISTRY.register(draft);
      window.dsaToast?.(`Registered "${t.name}" · find it in Registry`);
      setDraft(null);
    } finally { setBusy(false); }
  }

  return (
    <div className="tb-modal" onClick={() => setDraft(null)}>
      <div className="tb-modal-inner" onClick={e => e.stopPropagation()}>
        <header>
          <ViShape size={16}/>
          <h3>Save as new Type</h3>
          <span style={{marginLeft:'auto',font:'500 11px/1.4 var(--font-body)',color:'var(--fg-muted)'}}>
            Vi extracted a draft — review and Save
          </span>
          <button onClick={() => setDraft(null)}>×</button>
        </header>
        <div className="tb-modal-body" style={{gridTemplateColumns:'1fr'}}>
          <div className="tb-form" style={{gap:10}}>
            <div className="tb-row">
              <label><span>Name</span>
                <input value={draft.name || ''} onChange={e => patch({ name: e.target.value })} placeholder="Type name"/>
              </label>
              <label><span>Id (stable)</span>
                <input className="mono" value={draft.id || ''} onChange={e => patch({ id: e.target.value })}/>
              </label>
            </div>
            <div className="tb-row">
              <label><span>Layer</span>
                <select value={draft.layer} onChange={e => patch({ layer: e.target.value })}>
                  {window.CV_REGISTRY.LAYERS.map(l => <option key={l} value={l}>{window.CV_REGISTRY.LAYER_INFO[l].label}</option>)}
                </select>
              </label>
              <label><span>Family</span>
                <input className="mono" value={draft.family || ''} onChange={e => patch({ family: e.target.value })}/>
              </label>
            </div>
            <label><span>Description</span>
              <textarea rows="2" value={draft.description || ''} onChange={e => patch({ description: e.target.value })}/>
            </label>
            <div>
              <div style={{display:'flex',alignItems:'center',gap:8,margin:'6px 0'}}>
                <strong style={{font:'700 11px/1 var(--font-body)',letterSpacing:'0.06em',textTransform:'uppercase',color:'var(--accent-bronze)'}}>Variables · {(draft.variables||[]).length}</strong>
                <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={addVar}>+ Add</button>
                <span style={{font:'400 10px/1.4 var(--font-body)',color:'var(--fg-muted)',marginLeft:'auto'}}>
                  These become Template parameters when the Type is run.
                </span>
              </div>
              <div className="tb-vars">
                {(draft.variables || []).map((v, i) => (
                  <div key={i} className="tb-var-row">
                    <input placeholder="key" className="mono" value={v.key} onChange={e => patchVar(i, { key: e.target.value })}/>
                    <input placeholder="label" value={v.label || ''} onChange={e => patchVar(i, { label: e.target.value })}/>
                    <input placeholder="default" value={v.default || ''} onChange={e => patchVar(i, { default: e.target.value })}/>
                    <select value={v.kind || 'text'} onChange={e => patchVar(i, { kind: e.target.value })}>
                      <option value="text">text</option><option value="number">number</option><option value="url">url</option><option value="choice">choice</option>
                    </select>
                    <button className="rm" onClick={() => rmVar(i)}>×</button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
        <footer>
          <button className="dsa-btn dsa-btn--ghost" onClick={() => setDraft(null)}>Cancel</button>
          <button className="dsa-btn dsa-btn--primary" onClick={save} disabled={busy}>{busy ? 'Saving…' : 'Save Type'}</button>
        </footer>
      </div>
    </div>
  );
}

window.SaveAsTypeModal = SaveAsTypeModal;
