// canvases/Icons.jsx — icon library with real AI generation
const { useState: useState_ic, useMemo: useMemo_ic } = React;

const ICON_CATEGORIES = {
  'People & roles':      ['person','people','person-add','person-clock','handshake','team','user-network','user-card'],
  'Files & docs':        ['file','files-stack','file-upload','file-download','file-pdf','file-list','file-edit','file-gear','folder','folder-gear','brochure','document','clipboard'],
  'Communication':       ['chat','chat-double','chat-tree','megaphone','megaphone-link','bell','share','link','email'],
  'Architecture':        ['house','house-multi','building-tall','building-dollar','crane','m2','floorplan','blueprint','axes-3d','floor-pattern','vr-headset','drone','3d-cube'],
  'Browser & dashboard': ['browser','browser-house','browser-info','browser-chart','browser-pen','monitor-house','devices','dashboard','video-player','image','image-stack'],
  'Actions':             ['plus','minus','check','close','edit','eye','eye-off','search','filter','sort','swap','refresh'],
  'System & status':     ['gear','cloud','cloud-upload','cloud-download','database','dollar-circle','info-circle','lightbulb','location-pin','pin-route','calendar','color-swatches','sun-moon','adjustments'],
  'Logic & flow':        ['network','decision-tree','hierarchy','atom','globe','pie-chart','path-flow','check-square','check-square-fill','no-symbol'],
  'Platform':            ['play','pause','lock','unlock','star','tag','workstation','connector','shop-cart'],
};

function Icons({ generated, addGenerated, updateGenerated, removeGenerated }) {
  const [q, setQ] = useState_ic('');
  const [cat, setCat] = useState_ic(null);
  const [tone, setTone] = useState_ic('bronze');
  const [genOpen, setGenOpen] = useState_ic(false);
  const [genPrompt, setGenPrompt] = useState_ic('');
  const [generating, setGenerating] = useState_ic(false);
  const [proposals, setProposals] = useState_ic([]);
  const [inspect, setInspect] = useState_ic(null); // name being inspected

  const allNames = Object.keys(window.CV_ICONS.data);

  const filteredCats = useMemo_ic(() => {
    const out = {};
    for (const [c, names] of Object.entries(ICON_CATEGORIES)) {
      if (cat && cat !== c) continue;
      const f = names.filter(n => !q || n.toLowerCase().includes(q.toLowerCase()) || c.toLowerCase().includes(q.toLowerCase()));
      if (f.length) out[c] = f;
    }
    if (generated.length) {
      const genFiltered = generated.filter(g => !q || g.name.toLowerCase().includes(q.toLowerCase()));
      if (genFiltered.length && (!cat || cat === 'Recently generated')) {
        out['Recently generated'] = genFiltered.map(g => g.name);
      }
    }
    return out;
  }, [q, cat, generated]);

  async function generate() {
    const ask = genPrompt.trim();
    if (!ask) return;
    setGenerating(true);
    setProposals([]);
    try {
      const prompt = `You are extending the ConceptV icon library. Every icon is on a 24×24 viewBox, single 1.5px stroke, rounded caps + joins, no fills (use stroke="currentColor", fill="none"). Geometric and architectural, like Lucide or Feather but slightly thicker.

The user wants: ${ask}

Propose 4 distinct icon ideas. For each, return:
- a short kebab-case name (e.g. "credit-card")
- the SVG inner markup ONLY (the <path>, <circle>, <rect> elements that go inside <svg viewBox="0 0 24 24">). Do not include the <svg> wrapper. Do not include fill or stroke attributes — they are set globally.

Respond as compact JSON only (no prose, no markdown fences):
[{"name":"...","body":"<path d=\\"...\\"/>..."}, ...]`;
      const reply = await window.CV_AI.complete(prompt);
      // Try to parse out JSON
      let parsed = null;
      try {
        parsed = JSON.parse(reply);
      } catch {
        const m = String(reply).match(/\[[\s\S]*\]/);
        if (m) { try { parsed = JSON.parse(m[0]); } catch {} }
      }
      if (Array.isArray(parsed)) {
        setProposals(parsed.filter(p => p.name && p.body).slice(0, 8));
      } else {
        setProposals([]);
        window.dsaToast?.('Vi returned something I could not parse. Try a different prompt.');
      }
    } catch (err) {
      window.dsaToast?.('Generation failed. Try again.');
    } finally {
      setGenerating(false);
    }
  }

  function adopt(p) {
    // Insert into CV_ICONS.data and notify parent
    if (!p.name || window.CV_ICONS.data[p.name]) {
      // Ensure unique name
      p.name = `${p.name}-${Math.floor(Math.random()*900+100)}`;
    }
    window.CV_ICONS.data[p.name] = p.body;
    addGenerated({ name: p.name, body: p.body });
    setProposals(prev => prev.map(x => x.name === p.name ? { ...x, adopted: true } : x));
    window.dsaToast?.(`Adopted "${p.name}" into the system`);
  }

  function renderIcon(name, size = 28) {
    const body = window.CV_ICONS.data[name];
    if (!body) return null;
    const color = tone === 'gold' ? 'var(--accent-gold)' : tone === 'ink' ? 'var(--fg-primary)' : 'var(--accent-bronze)';
    return <svg viewBox="0 0 24 24" width={size} height={size} fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" dangerouslySetInnerHTML={{__html: body}}/>;
  }

  async function refineIcon(name, message) {
    const body = window.CV_ICONS.data[name];
    if (!body) return;
    try {
      const prompt = `You are revising one icon in ConceptV's style (24×24, 1.5px stroke, no fills, currentColor, rounded caps).

Original icon: "${name}"
Current SVG body: ${body}

User wants this change: "${message}"

Return ONLY the new icon body (path/circle/rect markup that goes inside <svg viewBox="0 0 24 24">). No wrapper, no fill or stroke attributes on elements.

Respond as compact JSON only:
{"body":"<new svg body>"}`;
      const reply = await window.CV_AI.complete(prompt);
      let parsed = null;
      try { parsed = JSON.parse(reply); }
      catch {
        const m = String(reply).match(/\{[\s\S]*\}/);
        if (m) { try { parsed = JSON.parse(m[0]); } catch {} }
      }
      if (!parsed?.body) {
        window.dsaToast?.('Vi returned no usable SVG — kept the original');
        return;
      }
      window.CV_ICONS.data[name] = parsed.body;
      // If it's a session-generated icon, persist the update too
      if (generated.some(g => g.name === name)) {
        updateGenerated?.(name, parsed.body);
      }
      window.dsaToast?.(`Refined "${name}"`);
    } catch {
      window.dsaToast?.('Refine failed — try again');
    }
  }

  async function duplicateIcon(name, message) {
    const body = window.CV_ICONS.data[name];
    if (!body) return;
    try {
      const prompt = `Create a new variant of this icon in ConceptV's style (24×24, 1.5px stroke, no fills, currentColor, rounded caps).

Source icon: "${name}"
Current SVG body: ${body}

The user wants a new variant that: "${message}"

Return ONLY the new icon. JSON only:
{"name":"<kebab-case name>","body":"<svg body>"}`;
      const reply = await window.CV_AI.complete(prompt);
      let parsed = null;
      try { parsed = JSON.parse(reply); }
      catch {
        const m = String(reply).match(/\{[\s\S]*\}/);
        if (m) { try { parsed = JSON.parse(m[0]); } catch {} }
      }
      if (!parsed?.body) {
        window.dsaToast?.('Vi returned no usable SVG');
        return;
      }
      let newName = parsed.name || `${name}-variant`;
      if (window.CV_ICONS.data[newName]) newName = `${newName}-${Math.floor(Math.random()*900+100)}`;
      window.CV_ICONS.data[newName] = parsed.body;
      addGenerated({ name: newName, body: parsed.body });
      window.dsaToast?.(`Added "${newName}" as a new variant`);
    } catch {
      window.dsaToast?.('Variant failed — try again');
    }
  }

  function deleteIcon(name) {
    delete window.CV_ICONS.data[name];
    removeGenerated?.(name);
    window.dsaToast?.(`Removed "${name}"`);
  }

  return (
    <>
      <CanvasHeader
        title="Icons"
        sub={`${allNames.length} glyphs in your library${generated.length ? ` · ${generated.length} added this session` : ''} · single-stroke, 1.5 px, 24 × 24 grid`}
        actions={<>
          <button className="dsa-btn dsa-btn--outline" onClick={() => window.open('../assets/icons/index.html','_blank')}>Open explorer ↗</button>
          <button className="dsa-btn dsa-btn--ai" onClick={() => setGenOpen(o => !o)}>
            <ViShape size={14}/> Generate with Vi
          </button>
        </>}
      />
      <div className="dsa-canvas-body">

        {genOpen && (
          <div className="dsa-gen-panel">
            <div className="dsa-gen-head">
              <ViShape size={18}/>
              <span className="dsa-gen-title">Generate new icons</span>
              <button className="dsa-gen-close" onClick={() => { setGenOpen(false); setProposals([]); }}>✕</button>
            </div>
            <textarea
              className="dsa-gen-input" rows="2"
              placeholder='What icons do you need? e.g. "credit card, invoice, refund, payment method" — or describe a concept like "things related to closing a sale"'
              value={genPrompt} onChange={e => setGenPrompt(e.target.value)}
            />
            <div className="dsa-gen-actions">
              <span className="dsa-gen-hint">Vi will respect your line style (1.5 px stroke, no fills) and propose 4 options. Click any to adopt.</span>
              <button className="dsa-btn dsa-btn--primary" onClick={generate} disabled={generating || !genPrompt.trim()}>
                {generating ? 'Generating…' : 'Generate'}
              </button>
            </div>
            {generating && (
              <div className="dsa-gen-loading">
                <ViShape size={14} animated/> Vi is drafting four icons in your line style…
              </div>
            )}
            {proposals.length > 0 && (
              <div className="dsa-gen-results">
                {proposals.map((p, i) => (
                  <div key={i} className={`dsa-gen-result ${p.adopted ? 'adopted' : ''}`} onClick={() => !p.adopted && adopt(p)}>
                    <div className="glyph">
                      <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="var(--accent-bronze)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" dangerouslySetInnerHTML={{__html: p.body}}/>
                    </div>
                    <div className="name">{p.name}</div>
                    {p.adopted && <span className="check">✓ in system</span>}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        <div className="dsa-icon-toolbar">
          <div className="dsa-search-pill">
            <CvIcon name="search" size={14} tone="muted"/>
            <input placeholder="Search icons…" value={q} onChange={e => setQ(e.target.value)}/>
          </div>
          <div style={{display:'flex',gap:4,padding:4,background:'var(--bg-muted)',borderRadius:'var(--r-md)'}}>
            {['bronze','gold','ink'].map(t => (
              <button key={t}
                style={{
                  border:'none', cursor:'pointer', padding:'7px 14px', borderRadius:'var(--r-sm)',
                  font:'600 11px/1 var(--font-body)', textTransform:'capitalize',
                  background: tone === t ? 'var(--bg-surface)' : 'transparent',
                  color: tone === t ? 'var(--fg-primary)' : 'var(--fg-secondary)',
                  boxShadow: tone === t ? 'var(--shadow-xs)' : 'none',
                }}
                onClick={() => setTone(t)}>{t}</button>
            ))}
          </div>
        </div>

        <div className="dsa-cat-bar">
          <button className={!cat ? 'active' : ''} onClick={() => setCat(null)}>All</button>
          {Object.keys(ICON_CATEGORIES).map(c => (
            <button key={c} className={cat === c ? 'active' : ''} onClick={() => setCat(c)}>{c}</button>
          ))}
          {generated.length > 0 && (
            <button className={cat === 'Recently generated' ? 'active' : ''} onClick={() => setCat('Recently generated')}>
              ◆ Recently generated · {generated.length}
            </button>
          )}
        </div>

        {Object.entries(filteredCats).map(([category, names]) => (
          <div className="dsa-section" key={category}>
            <div className="dsa-section-head">
              <h3 className="dsa-section-title">{category}</h3>
              <span className="dsa-section-meta">{names.length}</span>
            </div>
            <div className="dsa-icon-grid">
              {names.map(n => {
                const isNew = generated.some(g => g.name === n);
                return (
                  <div key={n} className="dsa-icon-tile-wrap" style={{position:'relative'}}
                       onMouseEnter={() => setInspect(n)}
                       onMouseLeave={() => setInspect(p => p === n ? null : p)}>
                    <div className={`dsa-icon-tile ${isNew ? 'generated' : ''}`}
                      onClick={() => {
                        navigator.clipboard?.writeText(n);
                        window.dsaToast?.(`Copied "${n}"`);
                      }}>
                      {renderIcon(n)}
                      <div className="dsa-icon-name">{n}</div>
                    </div>
                    {isNew && <span className="new-badge">New</span>}
                    {inspect === n && (
                      <div style={{
                        position:'absolute', top:6, right:6, display:'flex', gap:4, zIndex:3,
                      }}>
                        <RefinePop
                          mode="dot"
                          placeholder={`Change "${n}" — e.g. rounder, simpler, larger center`}
                          onRefine={msg => refineIcon(n, msg)}
                        />
                        <button
                          title="Duplicate as a new variant"
                          onClick={(e) => {
                            e.stopPropagation();
                            const msg = prompt(`How should the new "${n}" variant differ?`);
                            if (msg) duplicateIcon(n, msg);
                          }}
                          style={{
                            width:18,height:18,borderRadius:'50%',padding:0,
                            background:'var(--bg-surface)',border:'1px solid var(--accent-gold)',
                            color:'var(--accent-bronze)',font:'700 11px/1 var(--font-body)',
                            cursor:'pointer',
                          }}>+</button>
                        {isNew && (
                          <button
                            title="Remove from system"
                            onClick={(e) => { e.stopPropagation(); deleteIcon(n); }}
                            style={{
                              width:18,height:18,borderRadius:'50%',padding:0,
                              background:'var(--bg-surface)',border:'1px solid var(--status-error)',
                              color:'var(--status-error)',font:'700 11px/1 var(--font-body)',
                              cursor:'pointer',
                            }}>×</button>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ))}

        {Object.keys(filteredCats).length === 0 && (
          <div style={{padding:'40px 20px',textAlign:'center',color:'var(--fg-muted)',font:'400 14px/1.55 var(--font-body)'}}>
            No icons match "<b>{q}</b>". Try <span className="link" style={{color:'var(--accent-gold)',cursor:'pointer',fontWeight:600}} onClick={() => { setGenPrompt(q); setGenOpen(true); setQ(''); }}>generating one with Vi →</span>
          </div>
        )}

      </div>
    </>
  );
}

window.Icons = Icons;
