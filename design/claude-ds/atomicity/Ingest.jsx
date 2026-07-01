// atomicity/Ingest.jsx
// ============================================================================
// Ingest — upload source material; Vi recognises what it is, reads it deeply,
// and brings the design DNA forward as reviewable proposals. Composed from
// AcKit; all model work runs through CV_SOURCE (→ CV_AI / CV_HOST).
// ============================================================================
const { useState: useState_ig, useEffect: useEffect_ig, useReducer: useReducer_ig, useRef: useRef_ig } = React;
const { StateDot: StateDot_ig } = window.AcKit;

const DIM = {
  color:     { label: 'Colour',    icon: 'color-swatches' },
  type:      { label: 'Type',      icon: 'type' },
  voice:     { label: 'Voice',     icon: 'chat' },
  structure: { label: 'Structure', icon: 'hierarchy' },
  value:     { label: 'Values',    icon: 'star' },
  motif:     { label: 'Motifs',    icon: 'atom' },
};
const TYPE_LABEL = {
  'brand-guide': 'Brand guide', 'voice-sample': 'Voice sample', 'palette-image': 'Image',
  'deck': 'Deck', 'stylesheet': 'Styles', 'notes': 'Notes', 'data': 'Data', 'web-capture': 'Web',
};

function AcIngest() {
  const [, force] = useReducer_ig(x => x + 1, 0);
  useEffect_ig(() => window.CV_SOURCE.on(force), []);
  const sources = window.CV_SOURCE.list();
  const [selId, setSelId] = useState_ig(sources[0] && sources[0].id);
  const sel = window.CV_SOURCE.get(selId) || sources[0] || null;

  async function onFiles(files) {
    for (const f of Array.from(files)) {
      const isImg = /^image\//.test(f.type);
      const reader = new FileReader();
      await new Promise(res => {
        reader.onload = () => {
          const s = window.CV_SOURCE.addSource({ name: f.name, mime: f.type, kind: isImg ? 'image' : 'text', text: isImg ? '' : String(reader.result || ''), dataUrl: isImg ? String(reader.result) : '' });
          window.CV_SOURCE.recognize(s.id); setSelId(s.id); res();
        };
        reader.onerror = res;
        isImg ? reader.readAsDataURL(f) : reader.readAsText(f);
      });
    }
  }
  function onPaste(text) {
    if (!text.trim()) return;
    const s = window.CV_SOURCE.addSource({ name: 'Pasted note · ' + new Date().toLocaleTimeString(), kind: 'text', text });
    window.CV_SOURCE.recognize(s.id); setSelId(s.id);
  }

  return (
    <div className="ig">
      <div className="ig-rail">
        <Dropzone onFiles={onFiles} onPaste={onPaste}/>
        <div className="ig-list">
          {sources.length === 0 && <div className="ig-empty-rail">Nothing yet. Drop a brand doc, some copy, an image, or paste notes.</div>}
          {sources.map(s => (
            <button key={s.id} className={`ig-src ${selId === s.id ? 'on' : ''}`} onClick={() => setSelId(s.id)}>
              <CvIcon name={s.kind === 'image' ? 'image' : 'document'} size={15} tone={selId === s.id ? 'gold' : 'bronze'}/>
              <span className="ig-src-id"><b>{s.name}</b><i>{TYPE_LABEL[s.type] || 'reading…'}{s.findings && s.findings.length ? ` · ${s.findings.length} found` : ''}</i></span>
              <StateDot_ig state={s.status === 'analyzed' ? 'active' : s.status === 'analyzing' ? 'edited' : selId === s.id ? 'selected' : 'idle'}/>
            </button>
          ))}
        </div>
      </div>

      <div className="ig-detail">
        {sel ? <SourceView key={sel.id} s={sel} onChange={force} onRemove={() => { window.CV_SOURCE.remove(sel.id); setSelId(null); }}/>
             : <div className="ig-blank"><ViShape size={32}/><h2>Bring in source material</h2><p>Upload a brand guide, sample copy, a competitor screenshot, a moodboard image, or paste raw notes. Vi recognises what it is, reads it for depth, and proposes how it could improve your system.</p></div>}
      </div>
    </div>
  );
}

function Dropzone({ onFiles, onPaste }) {
  const fileRef = useRef_ig(null);
  const [over, setOver] = useState_ig(false);
  const [paste, setPaste] = useState_ig('');
  const [mode, setMode] = useState_ig('drop');
  return (
    <div className="ig-drop-wrap">
      <div className="ig-drop-tabs">
        <button className={mode === 'drop' ? 'on' : ''} onClick={() => setMode('drop')}>Upload</button>
        <button className={mode === 'paste' ? 'on' : ''} onClick={() => setMode('paste')}>Paste</button>
      </div>
      {mode === 'drop' ? (
        <div className={`ig-drop ${over ? 'over' : ''}`}
          onDragOver={e => { e.preventDefault(); setOver(true); }} onDragLeave={() => setOver(false)}
          onDrop={e => { e.preventDefault(); setOver(false); onFiles(e.dataTransfer.files); }}
          onClick={() => fileRef.current && fileRef.current.click()}>
          <CvIcon name="cloud-upload" size={22} tone="bronze"/>
          <span>Drop files or click — docs, copy, images, CSS</span>
          <input ref={fileRef} type="file" multiple style={{ display: 'none' }} onChange={e => { onFiles(e.target.files); e.target.value = ''; }}/>
        </div>
      ) : (
        <div className="ig-paste">
          <textarea value={paste} onChange={e => setPaste(e.target.value)} placeholder="Paste brand copy, notes, a transcript, hex codes…" rows={4}/>
          <button className="fz2-btn solid" disabled={!paste.trim()} onClick={() => { onPaste(paste); setPaste(''); }}>Add</button>
        </div>
      )}
    </div>
  );
}

function SourceView({ s, onChange, onRemove }) {
  const [busy, setBusy] = useState_ig(false);
  const [err, setErr] = useState_ig(null);
  async function analyze() {
    setBusy(true); setErr(null);
    try { await window.CV_SOURCE.analyze(s.id); onChange(); }
    catch (e) { setErr(e.message); }
    setBusy(false);
  }
  function forward(fid) { try { window.CV_SOURCE.bringForward(s.id, fid); window.dsaToast?.('Brought forward — staged for review'); } catch (e) { window.dsaToast?.(e.message); } onChange(); }
  function forwardAll() { const n = (s.findings || []).filter(f => f.proposal).length; window.CV_SOURCE.bringAll(s.id); window.dsaToast?.(`Staged ${n} proposal${n === 1 ? '' : 's'}`); onChange(); }

  const byDim = {};
  for (const f of (s.findings || [])) (byDim[f.dimension] = byDim[f.dimension] || []).push(f);
  const dims = Object.keys(byDim);
  const proposalCount = (s.findings || []).filter(f => f.proposal).length;

  return (
    <div className="ig-view">
      <header className="ig-head">
        <div>
          <div className="ig-head-eyebrow">{TYPE_LABEL[s.type] || 'Source'}</div>
          <h1>{s.name}</h1>
          {s.context && <p className="ig-context">{s.context}</p>}
        </div>
        <button className="ig-remove" onClick={onRemove} title="Remove"><CvIcon name="close" size={14} tone="muted"/></button>
      </header>

      {s.kind === 'image' && s.dataUrl && <div className="ig-img"><img src={s.dataUrl} alt={s.name}/></div>}

      {s.status !== 'analyzed' && (
        <div className="ig-cta">
          <button className="fz2-btn solid" disabled={busy} onClick={analyze}>
            <ViShape size={14} animated={busy}/>{busy ? 'Reading deeply…' : 'Analyse for depth'}
          </button>
          <span>Vi reads the material and brings forward what could improve your system.</span>
        </div>
      )}
      {err && <div className="ig-err">{err}</div>}

      {dims.length > 0 && (
        <div className="ig-findings">
          <div className="ig-findings-head">
            <span><b>{s.findings.length}</b> findings across {dims.length} dimension{dims.length === 1 ? '' : 's'}</span>
            {proposalCount > 0 && <button className="fz2-btn solid" onClick={forwardAll}>Bring all {proposalCount} forward</button>}
          </div>
          {dims.map(d => (
            <div key={d} className="ig-dim">
              <div className="ig-dim-lbl"><CvIcon name={(DIM[d] || {}).icon || 'star'} size={13} tone="gold"/> {(DIM[d] || { label: d }).label}</div>
              {byDim[d].map(f => (
                <div key={f.id} className="ig-finding">
                  {f.dimension === 'color' && /^#[0-9a-f]{3,8}$/i.test(f.evidence) && <span className="ig-sw" style={{ background: f.evidence }}/>}
                  <div className="ig-finding-body">
                    <div className="ig-finding-title">{f.title}</div>
                    {f.detail && <div className="ig-finding-detail">{f.detail}</div>}
                    {f.evidence && <div className="ig-finding-ev">“{f.evidence}”</div>}
                  </div>
                  {f.proposal && <button className="ig-bring" onClick={() => forward(f.id)} title="Bring forward into the system"><CvIcon name="plus" size={12} tone="ink"/> Bring forward</button>}
                </div>
              ))}
            </div>
          ))}
        </div>
      )}
      {s.status === 'analyzed' && dims.length === 0 && <div className="ig-none">No strong DNA signals found in this one.</div>}
    </div>
  );
}

window.AcIngest = AcIngest;
