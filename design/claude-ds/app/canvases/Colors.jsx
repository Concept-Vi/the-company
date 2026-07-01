// canvases/Colors.jsx — palette browser with real AI color generation
const { useState: useState_co } = React;

const BASE_PALETTE = [
  // Primary brand
  { name: 'gold',         hex: '#E0C010', role: 'accent · primary',  group: 'Brand' },
  { name: 'gold-hover',   hex: '#C8AB0E', role: 'accent · hover',    group: 'Brand' },
  { name: 'gold-soft',    hex: '#F4E89A', role: 'tint · panel',      group: 'Brand' },
  { name: 'gold-50',      hex: '#FBF4C8', role: 'tint · v1 panel (legacy)',  group: 'Brand' },
  { name: 'bronze',       hex: '#988058', role: 'illustration',      group: 'Brand' },
  { name: 'bronze-soft',  hex: '#C9B58A', role: 'borders, dividers', group: 'Brand' },
  // Brand ramp — gold→bronze→tan ordered scale (applied/working stops; logo gold = 'gold' above)
  { name: 'ramp-1',       hex: '#DAD364', role: 'ramp · bright gold', group: 'Brand' },
  { name: 'ramp-2',       hex: '#D6BF57', role: 'ramp · working gold',group: 'Brand' },
  { name: 'ramp-3',       hex: '#C09D5D', role: 'ramp · bronze (warm)',group: 'Brand' },
  { name: 'ramp-4',       hex: '#B98664', role: 'ramp · tan',         group: 'Brand' },
  // Surfaces
  { name: 'canvas',       hex: '#FBF7EC', role: 'page background',   group: 'Surfaces' },
  { name: 'surface',      hex: '#FFFFFF', role: 'card fill',         group: 'Surfaces' },
  { name: 'muted',        hex: '#F1ECDC', role: 'section panel',     group: 'Surfaces' },
  { name: 'sunken',       hex: '#E8E2CC', role: 'dropzones',         group: 'Surfaces' },
  { name: 'dark',         hex: '#1F1A12', role: 'overlay surfaces',  group: 'Surfaces' },
  // Ink
  { name: 'fg-primary',   hex: '#1F1A12', role: 'body text',         group: 'Ink' },
  { name: 'fg-secondary', hex: '#6B5F47', role: 'helper text',       group: 'Ink' },
  { name: 'fg-muted',     hex: '#A89678', role: 'placeholders',      group: 'Ink' },
  { name: 'fg-soft',      hex: '#C9B999', role: 'subtle',            group: 'Ink' },
  // Status
  { name: 'success',      hex: '#5A8A4A', role: 'approved',          group: 'Status' },
  { name: 'warning',      hex: '#E5A547', role: 'review',            group: 'Status' },
  { name: 'error',        hex: '#C24A3C', role: 'rejected',          group: 'Status' },
  { name: 'info',         hex: '#4A78B8', role: 'info',              group: 'Status' },
  { name: 'pending',      hex: '#E5C547', role: 'pending',           group: 'Status' },
];

function Colors({ extras, addExtras, colorEdits, setColorEdit, snapshot, setSnapshot, lockedTokens, toggleLock, removeExtra }) {
  const [genOpen, setGenOpen] = useState_co(false);
  const [genPrompt, setGenPrompt] = useState_co('A chart palette of 5 hues that fits my warm-ivory brand');
  const [generating, setGenerating] = useState_co(false);
  const [proposal, setProposal] = useState_co(null);
  const [editing, setEditing] = useState_co(null);

  const baseWithEdits = BASE_PALETTE.map(c => ({ ...c, hex: colorEdits[c.name] || c.hex }));
  const grouped = {};
  for (const c of [...baseWithEdits, ...extras]) {
    grouped[c.group] = grouped[c.group] || [];
    grouped[c.group].push(c);
  }

  // Live preview values
  const previewGold = colorEdits['gold'] || '#E0C010';
  const previewBronze = colorEdits['bronze'] || '#988058';
  const previewCanvas = colorEdits['canvas'] || '#FBF7EC';
  const previewSurface = colorEdits['surface'] || '#FFFFFF';
  const previewInk = colorEdits['fg-primary'] || '#1F1A12';
  const previewGoldSoft = colorEdits['gold-soft'] || '#F4E89A';

  async function generate() {
    const ask = genPrompt.trim();
    if (!ask) return;
    setGenerating(true);
    setProposal(null);
    try {
      const lockedList = (lockedTokens || []).map(name => {
        const all = [...BASE_PALETTE.map(c => ({...c, hex: colorEdits[c.name] || c.hex})), ...extras];
        const found = all.find(c => c.name === name);
        return found ? `- ${name} (${found.hex}) — ${found.role}` : null;
      }).filter(Boolean);
      const lockClause = lockedList.length
        ? `\n\nLOCKED tokens to preserve (do not propose values that conflict with these — your palette should sit alongside them):\n${lockedList.join('\n')}\n`
        : '';
      const prompt = `You are extending ConceptV's color system. The brand sits on warm ivory (#FBF7EC) with near-black ink (#1F1A12). The signature accent is a saturated gold #E0C010, with bronze #988058 for illustrations. Status colours are warm-shifted (success #5A8A4A, warning #E5A547, error #C24A3C, info #4A78B8). No cool greys, no pure black, no purple-blue gradients.
${lockClause}
The user wants: ${ask}

Propose a palette that fits this aesthetic. For each color return: a short kebab-case name, the hex code, a one-line role description.

Respond as compact JSON only (no prose, no markdown fences):
{"group": "<group name e.g. Chart / Data / Marketing>", "colors": [{"name":"...","hex":"#...","role":"..."}, ...]}`;
      const reply = await window.CV_AI.complete(prompt);
      let parsed = null;
      try { parsed = JSON.parse(reply); }
      catch {
        const m = String(reply).match(/\{[\s\S]*\}/);
        if (m) { try { parsed = JSON.parse(m[0]); } catch {} }
      }
      if (parsed && parsed.colors && Array.isArray(parsed.colors)) {
        setProposal({
          group: parsed.group || 'Generated',
          colors: parsed.colors.filter(c => c.name && /^#[0-9A-F]{3,8}$/i.test(c.hex)).slice(0, 8),
        });
      } else {
        window.dsaToast?.('Vi returned something I could not parse. Try a different prompt.');
      }
    } catch (err) {
      window.dsaToast?.('Generation failed. Try again.');
    } finally {
      setGenerating(false);
    }
  }

  function adoptAll() {
    if (!proposal) return;
    const next = proposal.colors.map(c => ({ ...c, group: proposal.group }));
    addExtras(next);
    setProposal(null);
    setGenOpen(false);
    window.dsaToast?.(`Adopted "${proposal.group}" — ${next.length} colors`);
  }

  function copy(hex) {
    navigator.clipboard?.writeText(hex);
    window.dsaToast?.(`Copied ${hex}`);
  }

  async function refineSwatch(name, currentHex, role, message) {
    try {
      const prompt = `You are revising one color in ConceptV's warm-ivory palette (gold #E0C010, bronze #988058, ivory #FBF7EC, no cool greys, no purple-blue).

Original: ${name} ${currentHex} (${role || 'unspecified role'})
User wants: "${message}"

Return ONLY the new hex value. JSON only:
{"hex":"#...","role":"<short role label, can match original>"}`;
      const reply = await window.CV_AI.complete(prompt);
      let parsed = null;
      try { parsed = JSON.parse(reply); }
      catch {
        const m = String(reply).match(/\{[\s\S]*\}/);
        if (m) { try { parsed = JSON.parse(m[0]); } catch {} }
      }
      if (!parsed?.hex || !/^#[0-9A-F]{3,8}$/i.test(parsed.hex)) {
        window.dsaToast?.('Vi returned no usable hex — kept the original');
        return;
      }
      // If it's a base token → editing the override; if extra → mutate the extra
      const isBase = BASE_PALETTE.some(c => c.name === name);
      if (isBase) {
        setColorEdit(name, parsed.hex.toUpperCase());
      } else {
        // Find in extras and replace
        const updated = extras.map(c => c.name === name ? { ...c, hex: parsed.hex.toUpperCase(), role: parsed.role || c.role } : c);
        // Use addExtras semantics: replace by clearing and re-adding (preserve order)
        // We'll just edit via setColorEdit-style for extras by name
        // Easiest: emit a custom event handled in parent — but simpler: replace in extras locally via addExtras with full new list
        // Use the parent-provided update path through setColorEdit if we treat extras names as edits too:
        setColorEdit(name, parsed.hex.toUpperCase());
      }
      window.dsaToast?.(`Refined "${name}" → ${parsed.hex.toUpperCase()}`);
    } catch {
      window.dsaToast?.('Refine failed — try again');
    }
  }

  return (
    <>
      <CanvasHeader
        title="Colors"
        sub={`${BASE_PALETTE.length + extras.length} tokens · all warm-shifted, no cool greys, gold reserved for emphasis`}
        actions={<>
          {(lockedTokens || []).length > 0 && (
            <span style={{display:'inline-flex',alignItems:'center',gap:6,padding:'5px 10px',background:'var(--accent-gold-50)',borderRadius:999,font:'500 11px/1 var(--font-body)',color:'var(--fg-primary)'}}>
              🔒 {lockedTokens.length} locked
            </span>
          )}
          <button className="dsa-btn dsa-btn--outline">Check contrast</button>
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
              <span className="dsa-gen-title">Generate a new palette group</span>
              <button className="dsa-gen-close" onClick={() => { setGenOpen(false); setProposal(null); }}>✕</button>
            </div>
            <textarea
              className="dsa-gen-input" rows="2"
              placeholder='What do you need? e.g. "A 5-color palette for marketing emails", "Data viz hues that sit alongside my gold", "Add a soft pink for celebration moments"'
              value={genPrompt} onChange={e => setGenPrompt(e.target.value)}
            />
            <div className="dsa-gen-actions">
              <span className="dsa-gen-hint">Vi will respect your warm aesthetic and propose a coherent group.</span>
              <button className="dsa-btn dsa-btn--primary" onClick={generate} disabled={generating || !genPrompt.trim()}>
                {generating ? 'Generating…' : 'Generate'}
              </button>
            </div>
            {generating && (
              <div className="dsa-gen-loading">
                <ViShape size={14} animated/> Vi is choosing hues that sit inside your palette…
              </div>
            )}
            {proposal && (
              <div style={{marginTop:14}}>
                <div style={{font:'600 12px/1 var(--font-body)',color:'var(--fg-secondary)',marginBottom:10}}>Proposed: <b style={{color:'var(--fg-primary)'}}>{proposal.group}</b></div>
                <div className="dsa-palette-grid">
                  {proposal.colors.map((c, i) => (
                    <div key={i} className="dsa-swatch" onClick={() => copy(c.hex)}>
                      <div className="dsa-swatch-color" style={{background:c.hex}}/>
                      <div className="dsa-swatch-meta">
                        <div className="dsa-swatch-name">{c.name}</div>
                        <div className="dsa-swatch-hex">{c.hex.toUpperCase()}</div>
                        <div className="dsa-swatch-role">{c.role}</div>
                      </div>
                    </div>
                  ))}
                </div>
                <div style={{marginTop:14,display:'flex',gap:8,justifyContent:'flex-end'}}>
                  <button className="dsa-btn dsa-btn--ghost" onClick={() => setProposal(null)}>Discard</button>
                  <button className="dsa-btn dsa-btn--primary" onClick={adoptAll}>Adopt all → into "{proposal.group}"</button>
                </div>
              </div>
            )}
          </div>
        )}

        {Object.entries(grouped).map(([group, colors]) => (
          <div className="dsa-section" key={group}>
            <div className="dsa-section-head">
              <h3 className="dsa-section-title">{group}</h3>
              <span className="dsa-section-meta">{colors.length} tokens</span>
            </div>
            <div className="dsa-palette-grid">
              {colors.map(c => {
                const edited = colorEdits && colorEdits[c.name];
                const locked = (lockedTokens || []).includes(c.name);
                const isExtra = extras.some(x => x.name === c.name);
                return (
                  <div key={c.name + c.hex} className="dsa-swatch" style={{
                    ...(edited ? {borderColor:'var(--accent-gold)'} : null),
                    position: 'relative',
                  }}>
                    {/* Lock corner indicator */}
                    {toggleLock && (
                      <button
                        onClick={(e) => { e.stopPropagation(); toggleLock(c.name); }}
                        title={locked ? 'Unlock — Vi can change this' : 'Lock — Vi will preserve this'}
                        style={{
                          position:'absolute', top:6, left:6, zIndex:2,
                          width:20, height:20, padding:0, borderRadius:'50%',
                          background: locked ? 'var(--accent-gold)' : 'rgba(255,255,255,.85)',
                          border:'1px solid ' + (locked ? 'var(--accent-gold)' : 'var(--border-default)'),
                          color: locked ? 'var(--fg-primary)' : 'var(--fg-muted)',
                          cursor:'pointer', font:'400 10px/1 var(--font-body)',
                          display:'flex',alignItems:'center',justifyContent:'center',
                        }}>{locked ? '🔒' : '🔓'}</button>
                    )}
                    <div className="dsa-swatch-color" style={{background:c.hex,cursor:'pointer',position:'relative'}}
                      onClick={() => setEditing(editing === c.name ? null : c.name)}>
                      {editing === c.name && (
                        <input
                          type="color" value={c.hex}
                          onClick={e => e.stopPropagation()}
                          onChange={e => setColorEdit(c.name, e.target.value.toUpperCase())}
                          style={{
                            position:'absolute',inset:8,width:'calc(100% - 16px)',height:'calc(100% - 16px)',
                            border:'2px solid white',borderRadius:'var(--r-sm)',cursor:'pointer',
                            padding:0,
                          }}
                        />
                      )}
                    </div>
                    <div className="dsa-swatch-meta" style={{position:'relative'}}>
                      <div className="dsa-swatch-name" style={{display:'flex',alignItems:'center',gap:6}}>
                        {c.name}
                        {edited && <span style={{font:'700 9px/1 var(--font-body)',color:'var(--accent-gold)',letterSpacing:'0.06em',textTransform:'uppercase',background:'var(--accent-gold-soft)',padding:'2px 4px',borderRadius:2}}>edited</span>}
                      </div>
                      <div className="dsa-swatch-hex" onClick={() => copy(c.hex)} style={{cursor:'pointer'}}>{c.hex.toUpperCase()}</div>
                      <div className="dsa-swatch-role">{c.role}</div>
                      <div style={{position:'absolute',top:8,right:8,display:'flex',gap:4}}>
                        <RefinePop
                          mode="dot"
                          placeholder={`Change "${c.name}" — e.g. warmer, brighter, more contrast`}
                          onRefine={msg => refineSwatch(c.name, c.hex, c.role, msg)}
                        />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}

        {/* Live preview panel with snapshot/compare */}
        <div className="dsa-section" style={{marginTop:36}}>
          <div className="dsa-section-head">
            <h3 className="dsa-section-title">Live preview</h3>
            <span className="dsa-section-meta">Click any swatch above to edit. Every change cascades through every kit instantly.</span>
            <div style={{marginLeft:'auto',display:'flex',gap:6}}>
              {!snapshot && (
                <button className="dsa-btn dsa-btn--outline dsa-btn--sm"
                  onClick={() => {
                    setSnapshot({ edits: { ...colorEdits }, takenAt: new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'}) });
                    window.dsaToast?.('Snapshot saved · edits will now show side-by-side');
                  }}>
                  📷 Save snapshot
                </button>
              )}
              {snapshot && (
                <>
                  <span style={{font:'500 11px/1 var(--font-body)',color:'var(--fg-muted)',padding:'7px 0'}}>
                    Snapshot: {Object.keys(snapshot.edits || {}).length} edits @ {snapshot.takenAt}
                  </span>
                  <button className="dsa-btn dsa-btn--outline dsa-btn--sm"
                    onClick={() => {
                      const newEdits = { ...snapshot.edits };
                      Object.keys(colorEdits || {}).forEach(k => {
                        if (!(k in newEdits)) newEdits[k] = colorEdits[k];
                      });
                      // Replace edits with snapshot
                      Object.keys(colorEdits).forEach(k => setColorEdit(k, snapshot.edits[k] || undefined));
                      Object.keys(snapshot.edits || {}).forEach(k => setColorEdit(k, snapshot.edits[k]));
                      window.dsaToast?.('Restored snapshot');
                    }}>
                    ↺ Restore
                  </button>
                  <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={() => { setSnapshot(null); window.dsaToast?.('Snapshot cleared'); }}>
                    Clear snapshot
                  </button>
                </>
              )}
            </div>
          </div>

          <PreviewBlock
            label={snapshot ? 'Current (live edits)' : null}
            preview={{ previewCanvas, previewGold, previewBronze, previewSurface, previewInk, previewGoldSoft }}
            tokens={makeTokenMap(colorEdits)}
          />

          {snapshot && (
            <div style={{marginTop:14}}>
              <PreviewBlock
                label="Snapshot"
                preview={makePreviewValues(snapshot.edits)}
                tokens={makeTokenMap(snapshot.edits)}
              />
            </div>
          )}

          {Object.keys(colorEdits || {}).length > 0 && (
            <div style={{
              marginTop:14, padding:'12px 14px',
              background:'var(--accent-gold-50)', borderRadius:'var(--r-md)',
              display:'flex',alignItems:'center',gap:12,
              font:'400 12px/1.4 var(--font-body)', color:'var(--fg-primary)',
            }}>
              <span style={{color:'var(--accent-gold)'}}>◆</span>
              <span><b>{Object.keys(colorEdits).length} token{Object.keys(colorEdits).length === 1 ? '' : 's'}</b> edited in this session. Use <b>Export to disk</b> on the Overview to grab the CSS patch.</span>
            </div>
          )}
        </div>

      </div>
    </>
  );
}

// Helpers — build derived values + token map from a flat edits object
function makeTokenMap(edits) {
  return {
    gold: edits['gold'] || '#E0C010',
    'gold-hover': edits['gold-hover'] || '#C8AB0E',
    'gold-soft': edits['gold-soft'] || '#F4E89A',
    'gold-50': edits['gold-50'] || '#FBF4C8',
    bronze: edits['bronze'] || '#988058',
    canvas: edits['canvas'] || '#FBF7EC',
    surface: edits['surface'] || '#FFFFFF',
    muted: edits['muted'] || '#F1ECDC',
    sunken: edits['sunken'] || '#E8E2CC',
    dark: edits['dark'] || '#1F1A12',
    'fg-primary': edits['fg-primary'] || '#1F1A12',
    'fg-secondary': edits['fg-secondary'] || '#6B5F47',
    'fg-muted': edits['fg-muted'] || '#A89678',
  };
}
function makePreviewValues(edits) {
  return {
    previewCanvas: edits['canvas'] || '#FBF7EC',
    previewSurface: edits['surface'] || '#FFFFFF',
    previewGold: edits['gold'] || '#E0C010',
    previewBronze: edits['bronze'] || '#988058',
    previewInk: edits['fg-primary'] || '#1F1A12',
    previewGoldSoft: edits['gold-soft'] || '#F4E89A',
  };
}

function PreviewBlock({ label, preview, tokens }) {
  const { previewCanvas, previewSurface, previewGold, previewBronze, previewInk, previewGoldSoft } = preview;
  return (
    <div style={{
      background: previewCanvas,
      borderRadius: 'var(--r-lg)',
      padding: '20px 22px 22px',
      border: '1px solid var(--border-faint)',
      position: 'relative',
    }}>
      {label && (
        <div style={{
          position:'absolute',top:10,right:14,
          font:'600 9px/1 var(--font-body)',color:'var(--accent-bronze)',letterSpacing:'0.08em',textTransform:'uppercase',
          background:'var(--accent-gold-50)',padding:'4px 8px',borderRadius:3,
        }}>{label}</div>
      )}
      <div style={{font:'600 10px/1 var(--font-body)',letterSpacing:'0.08em',textTransform:'uppercase',color:'var(--fg-muted)',marginBottom:14}}>Across all three product surfaces</div>
      <KitPreviews tokens={tokens}/>
      {/* Component preview row */}
      <div style={{
        display:'grid',gridTemplateColumns:'1fr 1fr 1fr',gap:14,marginTop:14,
        paddingTop:14,borderTop:'1px solid var(--border-faint)',
      }}>
        <div style={{background:previewSurface,borderRadius:'var(--r-md)',padding:'14px 16px',boxShadow:'var(--shadow-card)'}}>
          <div style={{font:'600 10px/1 var(--font-body)',letterSpacing:'0.08em',textTransform:'uppercase',color:'var(--fg-muted)',marginBottom:10}}>Buttons</div>
          <div style={{display:'flex',gap:6,flexWrap:'wrap',alignItems:'center'}}>
            <button style={{background:previewGold,color:previewInk,border:'none',padding:'7px 12px',borderRadius:'var(--r-md)',font:'600 11px/1 var(--font-body)',cursor:'pointer'}}>Publish</button>
            <button style={{background:'transparent',color:previewInk,border:`1.5px solid ${previewGold}`,padding:'7px 12px',borderRadius:'var(--r-md)',font:'600 11px/1 var(--font-body)',cursor:'pointer'}}>Filter</button>
            <button style={{background:'transparent',color:'var(--fg-secondary)',border:`1.5px dashed ${previewGold}`,padding:'7px 12px',borderRadius:'var(--r-md)',font:'600 11px/1 var(--font-body)',cursor:'pointer'}}>+ Add</button>
          </div>
        </div>
        <div style={{background:previewSurface,borderRadius:'var(--r-md)',padding:'14px 16px',boxShadow:'var(--shadow-card)'}}>
          <div style={{font:'600 10px/1 var(--font-body)',letterSpacing:'0.08em',textTransform:'uppercase',color:'var(--fg-muted)',marginBottom:8}}>Card</div>
          <h4 style={{font:'700 16px/1.1 var(--font-display)',color:previewBronze,letterSpacing:'-0.02em',margin:'0 0 4px'}}>Tower East</h4>
          <p style={{font:'400 11px/1.5 var(--font-body)',color:previewInk,margin:0}}>2 bed apartment with north-east aspect.</p>
          <div style={{marginTop:8,font:'500 10px/1 var(--font-mono)',color:previewInk}}>
            URL: <span style={{color:previewGold,fontWeight:600}}>conceptv.io/acme</span>
          </div>
        </div>
        <div style={{background:previewGoldSoft,borderRadius:'var(--r-md)',padding:'14px 16px'}}>
          <div style={{font:'600 10px/1 var(--font-body)',letterSpacing:'0.08em',textTransform:'uppercase',color:'var(--fg-muted)',marginBottom:8}}>Section panel</div>
          <div style={{display:'flex',alignItems:'center',gap:8,padding:'2px 0',font:'500 11px/1 var(--font-body)',color:previewInk}}>
            <span style={{width:14,height:14,borderRadius:3,background:previewGold,display:'inline-block',position:'relative'}}><span style={{position:'absolute',top:1,left:4,width:3,height:7,borderRight:`2px solid ${previewInk}`,borderBottom:`2px solid ${previewInk}`,transform:'rotate(45deg)'}}/></span>
            Information Panel
          </div>
          <div style={{display:'flex',alignItems:'center',gap:8,padding:'2px 0',font:'500 11px/1 var(--font-body)',color:previewInk}}>
            <span style={{width:14,height:14,borderRadius:3,background:previewGold,display:'inline-block'}}/>
            Floorplan
          </div>
        </div>
      </div>
    </div>
  );
}

window.Colors = Colors;
