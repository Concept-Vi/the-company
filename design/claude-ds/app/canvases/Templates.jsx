// canvases/Templates.jsx — saved Build runs as reusable parameterised templates.
// Now grouped by parent Type from the registry, with a built-in "Types" mode
// to surface registered Templates (layer:'template' in the Type Registry).
const { useState: useState_tp, useMemo: useMemo_tp, useEffect: useEffect_tp } = React;

function Templates({ savedTemplates, removeTemplate, onRunBrief, onRunWorkshopTemplate, onOpenRegistry, layout = 'grouped' }) {
  const [tick, setTick] = useState_tp(0);
  useEffect_tp(() => window.CV_REGISTRY?.subscribe(() => setTick(t => t + 1)), []);

  // Decorate each saved template with its parent Type (if any)
  const decorated = useMemo_tp(() => savedTemplates.map(t => {
    const parentId = t.doc?.type ? `doc.${t.doc.type}` : null;
    const parent = parentId ? window.CV_REGISTRY?.get(parentId) : null;
    return { ...t, parent };
  }), [savedTemplates, tick]);

  const groups = useMemo_tp(() => {
    const m = {};
    for (const t of decorated) {
      const k = t.parent?.id || 'other';
      (m[k] = m[k] || { parent: t.parent, items: [] }).items.push(t);
    }
    return m;
  }, [decorated]);

  return (
    <>
      <CanvasHeader
        title="Templates"
        sub={`${savedTemplates.length} saved · re-run any with new parameters to compose fresh variants. Templates are instances of Types — every parameter you fill in is a registered Variable on the parent.`}
        actions={onOpenRegistry && (
          <button className="dsa-btn dsa-btn--outline dsa-btn--sm" onClick={onOpenRegistry}>
            Open Type Registry →
          </button>
        )}
      />
      <div className="dsa-canvas-body">

        {savedTemplates.length === 0 ? (
          <div className="dsa-stub">
            <h3>No templates yet</h3>
            <p>Run something in <b>Build</b> or open a doc in <b>Workshop</b>, then hit <b>Save as template</b>. Vi extracts the variable parts into reusable parameters — re-run with different values to get fresh variants.</p>
            <p style={{font:'400 12px/1.5 var(--font-body)',color:'var(--fg-muted)',marginTop:8}}>
              Tip — every Template is a child of a Type in the Registry. Promote any doc into a Type first, then save Templates against it.
            </p>
          </div>
        ) : layout === 'flat' ? (
          <div className="dsa-section">
            <div className="dsa-section-head">
              <h3 className="dsa-section-title">Saved templates · {savedTemplates.length}</h3>
              <span className="dsa-section-meta">Edit any parameter to fork into a new run</span>
            </div>
            <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill, minmax(320px, 1fr))',gap:14}}>
              {decorated.map(t => (
                <TemplateCard key={t.id} t={t} onDelete={removeTemplate} onRunBrief={onRunBrief} onRunWorkshopTemplate={onRunWorkshopTemplate}/>
              ))}
            </div>
          </div>
        ) : (
          // grouped — by parent Type
          <>
            {Object.entries(groups).map(([key, g]) => (
              <div key={key} className="dsa-section" style={{marginBottom:18}}>
                <div className="dsa-section-head" style={{display:'flex',alignItems:'center',gap:10}}>
                  {g.parent && <window.TypeLayerBadge layer={g.parent.layer} size="md"/>}
                  <h3 className="dsa-section-title">{g.parent?.name || 'Other'}</h3>
                  <span className="dsa-section-meta">{g.parent?.description || 'No matching parent Type'} · {g.items.length} template{g.items.length===1?'':'s'}</span>
                </div>
                <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill, minmax(320px, 1fr))',gap:14}}>
                  {g.items.map(t => (
                    <TemplateCard key={t.id} t={t} onDelete={removeTemplate} onRunBrief={onRunBrief} onRunWorkshopTemplate={onRunWorkshopTemplate}/>
                  ))}
                </div>
              </div>
            ))}
          </>
        )}

      </div>
    </>
  );
}

function TemplateCard({ t, onDelete, onRunBrief, onRunWorkshopTemplate }) {
  const [values, setValues] = useState_tp(() => {
    const init = {};
    (t.params || []).forEach(p => { init[p.key] = p.default || ''; });
    (t.variables || []).forEach(v => { init[v.key] = v.default || ''; });
    return init;
  });
  const isWorkshopDoc = t.kind === 'workshop-doc';
  const vars = isWorkshopDoc ? (t.variables || []) : (t.params || []);
  const resolved = !isWorkshopDoc ? resolveBrief(t.briefPattern || '', values) : '';
  const isDirty = vars.some(p => values[p.key] !== p.default);

  // Build a faux Type for thumbnailing — uses parent doc Type if known.
  const parentTypeId = t.docType ? `doc.${t.docType}` : null;
  const parentType = parentTypeId ? window.CV_REGISTRY?.get(parentTypeId) : null;
  const fauxType = parentType ? {
    ...parentType,
    name: t.name || parentType.name,
    defaults: { ...(parentType.defaults || {}), ...(t.doc || {}) },
    variables: t.variables || [],
  } : null;

  function run() {
    if (isWorkshopDoc) {
      const doc = window.WS_AI?.materializeTemplate({ doc: t.doc, variables: t.variables }, values);
      if (doc) onRunWorkshopTemplate?.(doc);
      else window.dsaToast?.('Could not materialize template');
    } else {
      onRunBrief?.(resolved);
    }
  }

  return (
    <div className="dsa-card cv-template-card">
      {fauxType && window.TypeThumb && (
        <div className="cv-tc-thumb">
          <window.TypeThumb type={fauxType} width={280} height={150}/>
          <span className="cv-tc-vars">𝓋 {vars.length}</span>
          <span className="cv-tc-layer">
            <window.TypeLayerBadge layer="template" size="sm"/>
          </span>
        </div>
      )}
      <div className="cv-tc-body">
        <div style={{display:'flex',alignItems:'baseline',gap:8}}>
          <h4 style={{font:'700 15px/1.2 var(--font-display)',color:'var(--fg-primary)',margin:0,letterSpacing:'-0.01em',flex:1,minWidth:0,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{t.name || 'Untitled'}</h4>
          <span style={{font:'500 10px/1 var(--font-mono)',color:'var(--fg-muted)',flex:'none'}}>{t.savedAt}</span>
        </div>
        {t.description && <p style={{font:'400 12px/1.5 var(--font-body)',color:'var(--fg-secondary)',margin:0}}>{t.description}</p>}
        {isWorkshopDoc && (
          <div style={{font:'400 11px/1 var(--font-mono)',color:'var(--accent-bronze)',background:'var(--accent-gold-50)',padding:'5px 8px',borderRadius:'var(--r-sm)',display:'inline-block',alignSelf:'flex-start',letterSpacing:'0.04em'}}>
            {t.docType || 'workshop'} · reusable
          </div>
        )}

        {vars.length > 0 ? (
          <div style={{display:'flex',flexDirection:'column',gap:8,padding:'12px 14px',background:'var(--accent-gold-faint)',borderRadius:'var(--r-sm)'}}>
            <div style={{font:'600 10px/1 var(--font-body)',color:'var(--accent-bronze)',letterSpacing:'0.08em',textTransform:'uppercase'}}>{isWorkshopDoc ? 'Variables' : 'Parameters'} · {vars.length}</div>
            {vars.map(p => (
              <div key={p.key} style={{display:'flex',flexDirection:'column',gap:4}}>
                <label style={{font:'500 11px/1 var(--font-body)',color:'var(--fg-secondary)'}}>{p.label || p.key}</label>
                <input
                  value={values[p.key] || ''}
                  onChange={e => setValues(v => ({ ...v, [p.key]: e.target.value }))}
                  style={{
                    border:'1px solid var(--border-default)',borderRadius:'var(--r-sm)',
                    padding:'7px 9px', background:'var(--bg-canvas)', outline:'none',
                    font:'400 12px/1.4 var(--font-body)', color:'var(--fg-primary)',
                    fontFamily:'var(--font-body)',
                  }}
                />
              </div>
            ))}
          </div>
        ) : !isWorkshopDoc ? (
          <div style={{font:'400 11px/1.4 var(--font-mono)',color:'var(--fg-muted)',padding:'10px 12px',background:'var(--bg-muted)',borderRadius:'var(--r-sm)',maxHeight:60,overflow:'hidden'}}>
            {t.briefPattern}
          </div>
        ) : (
          <div style={{font:'400 12px/1.5 var(--font-body)',color:'var(--fg-muted)',padding:'10px 12px',background:'var(--bg-muted)',borderRadius:'var(--r-sm)'}}>
            No variables — runs as a fixed copy of the original doc.
          </div>
        )}

        <div style={{display:'flex',gap:6,marginTop:'auto'}}>
          <button className="dsa-btn dsa-btn--ai dsa-btn--sm" onClick={run}>
            <ViShape size={12}/> Run {isDirty ? 'with edits' : ''}
          </button>
          <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" style={{marginLeft:'auto',color:'var(--status-error)'}}
            onClick={() => { if (confirm(`Delete "${t.name}"?`)) onDelete(t.id); }}>Delete</button>
        </div>
      </div>
    </div>
  );
}

function resolveBrief(pattern, values) {
  return String(pattern || '').replace(/\{\{(\w+)\}\}/g, (_, k) => values[k] || `{{${k}}}`);
}

window.Templates = Templates;
