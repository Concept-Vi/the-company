// canvases/Inbox.jsx — drop zone with real AI tagging
const { useState: useState_in, useRef: useRef_in } = React;

const CATEGORIES = [
  { id: 'icons',    label: 'Icons',    cat: 'icons',    desc: 'Glyphs for the icon library' },
  { id: 'colors',   label: 'Colors',   cat: 'colors',   desc: 'Swatches / palette refs' },
  { id: 'logos',    label: 'Logos',    cat: 'logos',    desc: 'Marks, wordmarks, lockups' },
  { id: 'imagery',  label: 'Imagery',  cat: 'imagery',  desc: 'Photos, renders, illustrations' },
  { id: 'voice',    label: 'Voice',    cat: 'voice',    desc: 'Copy, examples, brand language' },
  { id: 'components', label: 'Components', cat: 'components', desc: 'UI patterns + screenshots' },
  { id: 'templates', label: 'Templates', cat: 'templates', desc: 'Slide / brochure refs' },
  { id: 'type',     label: 'Type',     cat: 'type',     desc: 'Fonts, specimens' },
];

async function readAsDataUrl(file) {
  return new Promise((res, rej) => {
    const r = new FileReader();
    r.onload = () => res(r.result);
    r.onerror = rej;
    r.readAsDataURL(file);
  });
}

function fmtSize(n) {
  if (n < 1024) return n + ' B';
  if (n < 1024*1024) return (n/1024).toFixed(1) + ' KB';
  return (n/1024/1024).toFixed(1) + ' MB';
}

function Inbox({ items, setItems, onApplied }) {
  const [over, setOver] = useState_in(false);
  const [selected, setSelected] = useState_in(new Set());
  const [bulkTagging, setBulkTagging] = useState_in(false);
  const fileRef = useRef_in(null);

  function toggleSelect(id) {
    setSelected(s => {
      const n = new Set(s);
      if (n.has(id)) n.delete(id); else n.add(id);
      return n;
    });
  }
  function selectAll() {
    const allIds = items.filter(i => !i.appliedCat).map(i => i.id);
    setSelected(new Set(allIds));
  }
  function clearSelection() { setSelected(new Set()); }

  async function bulkApply() {
    const ids = [...selected];
    for (const id of ids) {
      const item = items.find(it => it.id === id);
      if (item?.suggestedCat) applyTag(id, item.suggestedCat);
    }
    setSelected(new Set());
    window.dsaToast?.(`Applied ${ids.length} item${ids.length===1?'':'s'}`);
  }
  async function bulkRetag() {
    setBulkTagging(true);
    for (const id of selected) await autoTag(id);
    setBulkTagging(false);
  }
  function bulkReject() {
    if (!confirm(`Discard ${selected.size} item${selected.size===1?'':'s'}?`)) return;
    setItems(prev => prev.filter(it => !selected.has(it.id)));
    setSelected(new Set());
  }

  async function handleFiles(files) {
    const list = [...files];
    for (const f of list) {
      const dataUrl = f.type.startsWith('image/') ? await readAsDataUrl(f) : null;
      const id = `inb-${Date.now()}-${Math.random().toString(36).slice(2,7)}`;
      const item = {
        id,
        name: f.name,
        type: f.type || 'application/octet-stream',
        size: f.size,
        dataUrl,
        suggestedCat: null,
        appliedCat: null,
        thinking: false,
        receivedAt: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setItems(prev => [item, ...prev]);
      // Kick off AI tagging
      autoTag(id);
    }
  }

  async function autoTag(id) {
    setItems(prev => prev.map(it => it.id === id ? { ...it, thinking: true } : it));
    let item;
    setItems(prev => { item = prev.find(it => it.id === id); return prev; });
    if (!item) return;
    try {
      const isImg = item.type.startsWith('image/') && item.dataUrl;
      let reply;
      if (isImg) {
        // Visual classification: send the image to the model
        reply = await window.CV_AI.complete({
          messages: [{
            role: 'user',
            content: [
              { type: 'image', source: { type: 'base64', media_type: item.type, data: item.dataUrl.split(',')[1] } },
              { type: 'text', text: `Classify this image for a brand design-system inbox. Pick the single best category id from this list:
${CATEGORIES.map(c => `- ${c.id}: ${c.desc}`).join('\n')}

Look at the actual image content — what's drawn, photographed, or rendered. The filename is "${item.name}".

Respond with ONLY the category id (one word, lowercase). No explanation.` },
            ],
          }],
        });
      } else {
        const prompt = `A user uploaded a file to a brand design-system inbox. Pick the single best category for it from this list:
${CATEGORIES.map(c => `- ${c.id}: ${c.desc}`).join('\n')}

File details:
- name: "${item.name}"
- type: ${item.type}
- size: ${fmtSize(item.size)}

Respond with ONLY the category id (one word, lowercase). No explanation. No punctuation.`;
        reply = await window.CV_AI.complete(prompt);
      }
      const guess = String(reply || '').trim().toLowerCase().split(/\s+/)[0].replace(/[^a-z]/g, '');
      const valid = CATEGORIES.find(c => c.id === guess);
      const cat = valid ? valid.id : 'imagery';
      setItems(prev => prev.map(it => it.id === id ? { ...it, thinking: false, suggestedCat: cat } : it));
    } catch (err) {
      setItems(prev => prev.map(it => it.id === id ? { ...it, thinking: false, suggestedCat: 'imagery' } : it));
    }
  }

  function applyTag(id, cat) {
    setItems(prev => prev.map(it => it.id === id ? { ...it, appliedCat: cat, suggestedCat: cat } : it));
    const item = items.find(it => it.id === id);
    onApplied?.(cat);
    window.dsaToast?.(`Filed "${item?.name || 'item'}" to ${CATEGORIES.find(c=>c.id===cat)?.label || cat}`);
  }

  function reject(id) {
    setItems(prev => prev.filter(it => it.id !== id));
  }

  // Bulk operations
  const untagged = items.filter(it => !it.appliedCat);
  function applyAllSuggestions() {
    items.forEach(it => {
      if (!it.appliedCat && it.suggestedCat) {
        setItems(prev => prev.map(x => x.id === it.id ? { ...x, appliedCat: it.suggestedCat } : x));
        onApplied?.(it.suggestedCat);
      }
    });
    window.dsaToast?.(`Applied ${untagged.filter(i => i.suggestedCat).length} suggested tags`);
  }
  function retagAll() {
    untagged.filter(it => !it.thinking).forEach(it => autoTag(it.id));
  }
  function clearTagged() {
    setItems(prev => prev.filter(it => !it.appliedCat));
    window.dsaToast?.('Cleared tagged items');
  }

  return (
    <>
      <CanvasHeader
        title="Inbox"
        sub="Drop anything in here. Vi auto-tags by content and proposes where it belongs. Approve or reroute — nothing enters your system until you accept it."
      />
      <div className="dsa-canvas-body">

        <div
          className={`dsa-drop ${over ? 'over' : ''}`}
          onClick={() => fileRef.current.click()}
          onDragEnter={e => { e.preventDefault(); setOver(true); }}
          onDragLeave={e => { e.preventDefault(); setOver(false); }}
          onDragOver={e => e.preventDefault()}
          onDrop={e => {
            e.preventDefault(); setOver(false);
            if (e.dataTransfer.files) handleFiles(e.dataTransfer.files);
          }}
        >
          <div className="plus">+</div>
          <div className="label">Drop files here, or click to browse</div>
          <div className="hint">Images, logos, screenshots, brand docs, fonts, anything. Vi reads the filename + type and proposes where it belongs in your system.</div>
          <input ref={fileRef} type="file" multiple onChange={e => handleFiles(e.target.files)}/>
        </div>

        {items.length > 0 && (
          <div className="dsa-section" style={{marginTop:28}}>
            <div className="dsa-section-head">
              <h3 className="dsa-section-title">Awaiting your call · {items.length}</h3>
              <span className="dsa-section-meta">Vi's suggestion appears in gold — click to apply, or pick a different category</span>
              <div style={{marginLeft:'auto',display:'flex',gap:6}}>
                {items.some(i => i.suggestedCat && !i.thinking && !i.appliedCat) && (
                  <button className="dsa-btn dsa-btn--ai dsa-btn--sm" onClick={applyAllSuggestions}>
                    <ViShape size={12}/> Apply all ({items.filter(i => i.suggestedCat && !i.appliedCat).length})
                  </button>
                )}
                <button className="dsa-btn dsa-btn--outline dsa-btn--sm" onClick={retagAll}>Re-tag all</button>
                {items.some(i => i.appliedCat) && (
                  <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={clearTagged}>Clear tagged</button>
                )}
              </div>
            </div>

            {/* Bulk-select toolbar */}
            <div style={{
              display:'flex', alignItems:'center', gap:8, marginBottom:10,
              padding: selected.size > 0 ? '10px 14px' : '6px 14px',
              background: selected.size > 0 ? 'var(--accent-gold-50)' : 'transparent',
              borderRadius: 'var(--r-md)',
              transition: 'background 200ms',
            }}>
              <label style={{display:'flex',alignItems:'center',gap:8,font:'500 12px/1 var(--font-body)',color:'var(--fg-primary)',cursor:'pointer'}}>
                <input type="checkbox" checked={items.filter(i=>!i.appliedCat).every(i=>selected.has(i.id)) && items.some(i=>!i.appliedCat)} onChange={e=>e.target.checked ? selectAll() : clearSelection()}/>
                Select all
              </label>
              {selected.size > 0 && (
                <>
                  <span style={{font:'600 11px/1 var(--font-body)',color:'var(--accent-bronze)'}}>{selected.size} selected</span>
                  <button className="dsa-btn dsa-btn--primary dsa-btn--sm" onClick={bulkApply}>Apply Vi's suggestions</button>
                  <button className="dsa-btn dsa-btn--ai dsa-btn--sm" onClick={bulkRetag} disabled={bulkTagging}>
                    <ViShape size={11}/> {bulkTagging ? 'Re-tagging…' : 'Re-tag with Vi'}
                  </button>
                  <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={bulkReject}>Discard</button>
                  <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={clearSelection} style={{marginLeft:'auto'}}>Clear</button>
                </>
              )}
            </div>

            <div className="dsa-inbox-list">
              {items.map(it => (
                <InboxItem key={it.id} item={it} onApply={applyTag} onReject={reject} onRetag={autoTag}
                  selected={selected.has(it.id)} onSelect={() => toggleSelect(it.id)}/>
              ))}
            </div>
          </div>
        )}

        {items.length === 0 && (
          <div className="dsa-section" style={{marginTop:28,textAlign:'center'}}>
            <p style={{font:'400 13px/1.55 var(--font-body)',color:'var(--fg-muted)',margin:0}}>Your inbox is empty. Drop some files to get started.</p>
          </div>
        )}

      </div>
    </>
  );
}

function InboxItem({ item, onApply, onReject, onRetag, selected, onSelect }) {
  const [open, setOpen] = useState_in(false);
  const isImg = item.dataUrl && item.type.startsWith('image/');
  const cat = item.appliedCat || item.suggestedCat;
  const catObj = cat ? CATEGORIES.find(c => c.id === cat) : null;
  return (
    <div className={`dsa-inbox-item ${item.appliedCat ? 'tagged applied' : item.suggestedCat ? 'tagged' : ''}`}
      style={{gridTemplateColumns: '20px 56px 1fr auto auto', borderColor: selected ? 'var(--accent-gold)' : undefined}}>
      <input type="checkbox" checked={!!selected} onChange={onSelect} disabled={!!item.appliedCat} style={{cursor:'pointer'}}/>
      <div className="dsa-inbox-thumb">
        {isImg
          ? <img src={item.dataUrl} alt=""/>
          : <CvIcon name={item.type.includes('pdf') ? 'file-pdf' : 'file'} size={26} tone="bronze"/>
        }
      </div>
      <div className="dsa-inbox-meta">
        <div className="dsa-inbox-name">{item.name}</div>
        <div className="dsa-inbox-info">
          {item.type || 'file'} · {fmtSize(item.size)} · {item.receivedAt}
          {isImg && <span style={{marginLeft:6,color:'var(--accent-gold)',font:'600 10px/1 var(--font-body)',letterSpacing:'0.06em',textTransform:'uppercase'}}>· Vi reads visually</span>}
        </div>
      </div>
      <div>
        {item.thinking
          ? <span className="dsa-inbox-thinking">Vi is reading…</span>
          : item.appliedCat
            ? <span className="dsa-inbox-tag" style={{color:'var(--status-success)',borderColor:'var(--status-success)',background:'var(--status-success-bg)'}}>✓ {catObj?.label}</span>
            : (
              <>
                <span
                  className={`dsa-inbox-tag ${item.suggestedCat ? 'suggested' : ''}`}
                  onClick={() => setOpen(o => !o)}
                  style={{cursor:'pointer'}}
                >{catObj?.label || 'Tag…'}</span>
                {open && (
                  <div style={{
                    position:'relative', zIndex:5, marginTop:6,
                    background:'var(--bg-surface)', border:'1px solid var(--border-default)',
                    borderRadius:'var(--r-md)', boxShadow:'var(--shadow-pop)',
                    padding:6, display:'flex', flexWrap:'wrap', gap:4, maxWidth:300,
                  }}>
                    {CATEGORIES.map(c => (
                      <button key={c.id} className="dsa-btn dsa-btn--ghost dsa-btn--sm"
                        onClick={() => { setOpen(false); onApply(item.id, c.id); }}>{c.label}</button>
                    ))}
                  </div>
                )}
              </>
            )
        }
      </div>
      <div className="dsa-inbox-actions">
        {!item.appliedCat && item.suggestedCat && !item.thinking && (
          <>
            <button className="dsa-btn dsa-btn--primary dsa-btn--sm" onClick={() => onApply(item.id, item.suggestedCat)}>Apply</button>
            <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={() => onRetag(item.id)}>Re-tag</button>
          </>
        )}
        <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={() => onReject(item.id)} title="Discard">✕</button>
      </div>
    </div>
  );
}

window.Inbox = Inbox;
