// canvases/Patterns.jsx — Motion & space: spacing / radii / shadow / motion tokens
const { useState: useState_pt, useMemo: useMemo_pt } = React;

const BASE_SPACING = [
  { name: 's-0',  px:  0 }, { name: 's-1',  px:  4 }, { name: 's-2',  px:  8 },
  { name: 's-3',  px: 12 }, { name: 's-4',  px: 16 }, { name: 's-5',  px: 20 },
  { name: 's-6',  px: 24 }, { name: 's-8',  px: 32 }, { name: 's-10', px: 40 },
  { name: 's-12', px: 48 }, { name: 's-16', px: 64 }, { name: 's-20', px: 80 },
  { name: 's-24', px: 96 },
];

const BASE_RADII = [
  { name: 'r-xs',   px: 4   },
  { name: 'r-sm',   px: 6   },
  { name: 'r-md',   px: 8   },
  { name: 'r-lg',   px: 12  },
  { name: 'r-xl',   px: 16  },
  { name: 'r-2xl',  px: 20  },
  { name: 'r-pill', px: 999 },
];

const BASE_SHADOWS = [
  { name: 'shadow-xs',    use: 'tiny lift',         value: '0 1px 2px rgba(31, 26, 18, 0.05)' },
  { name: 'shadow-sm',    use: 'buttons, chips',    value: '0 1px 3px rgba(31, 26, 18, 0.06), 0 1px 2px rgba(31, 26, 18, 0.04)' },
  { name: 'shadow-card',  use: 'cards, tiles',      value: '0 1px 2px rgba(31, 26, 18, 0.04), 0 4px 14px rgba(31, 26, 18, 0.05)' },
  { name: 'shadow-pop',   use: 'hover, popovers',   value: '0 8px 28px rgba(31, 26, 18, 0.12), 0 2px 6px rgba(31, 26, 18, 0.06)' },
  { name: 'shadow-modal', use: 'modals, sheets',    value: '0 24px 64px rgba(31, 26, 18, 0.22)' },
  { name: 'shadow-inset', use: 'paper / inner glow', value: 'inset 0 1px 0 rgba(255,255,255,0.6), inset 0 -1px 0 rgba(31,26,18,0.04)' },
];

const BASE_MOTION = [
  { name: 'ease-out',     value: 'cubic-bezier(.2, .8, .2, 1)',       kind: 'easing', use: 'enter, settle'   },
  { name: 'ease-in-out',  value: 'cubic-bezier(.65, 0, .35, 1)',      kind: 'easing', use: 'transitions'     },
  { name: 'dur-fast',     value: '120ms',                              kind: 'duration', use: 'hover, focus' },
  { name: 'dur-base',     value: '200ms',                              kind: 'duration', use: 'most UI'      },
  { name: 'dur-slow',     value: '360ms',                              kind: 'duration', use: 'reveals'      },
];

const TAB_DEFS = [
  { id: 'spacing', label: 'Spacing',  count: BASE_SPACING.length },
  { id: 'radii',   label: 'Radii',    count: BASE_RADII.length   },
  { id: 'shadows', label: 'Shadows',  count: BASE_SHADOWS.length },
  { id: 'motion',  label: 'Motion',   count: BASE_MOTION.length  },
];

function Patterns({ edits, setEdit, snapshot, setSnapshot, locked, toggleLock }) {
  const [tab, setTab] = useState_pt('spacing');
  const [genOpen, setGenOpen] = useState_pt(false);
  const [genPrompt, setGenPrompt] = useState_pt('A taller shadow scale that feels like paper, not glass');
  const [generating, setGenerating] = useState_pt(false);
  const [proposal, setProposal] = useState_pt(null);

  const editsObj = edits || {};

  function get(name, fallback) { return editsObj[name] ?? fallback; }
  function isLocked(name) { return (locked || []).includes(name); }
  function copy(s) { navigator.clipboard?.writeText(s); window.dsaToast?.(`Copied ${s}`); }

  async function generate() {
    const ask = genPrompt.trim();
    if (!ask) return;
    setGenerating(true);
    setProposal(null);
    try {
      const lockedNote = (locked || []).length
        ? `\n\nLOCKED tokens to keep exactly:\n${(locked||[]).map(n => `- --${n}`).join('\n')}\n`
        : '';
      const prompt = `You are extending the ConceptV design-system token set inside ConceptV Studio.

The brand sits on warm ivory paper (#FBF7EC) with near-black ink (#1F1A12) and saturated gold (#E0C010) accents. The aesthetic is paper-first, not glassmorphism. Shadows are warm-tinted (rgba(31,26,18,…)) and short, not blue-grey blurs. Motion is calm — ease-out 200ms is the default. Radii ramp 4 → 6 → 8 → 12 → 16 → 20 → pill. Spacing is an 8-px base with a 4-px half-step.

Active focus: ${TAB_DEFS.find(t => t.id === tab)?.label || tab} tokens.
${lockedNote}
User asks: "${ask}"

Propose 3–6 token edits or new tokens that fit the focus. For each, return: kebab-case name (prefix \`s-\` for spacing, \`r-\` for radii, \`shadow-\` for shadow, \`ease-\` or \`dur-\` for motion), the value as a CSS-valid string, and a one-line use case.

Respond as compact JSON only (no prose, no markdown fences):
{"intent":"<short description>","entries":[{"name":"...","value":"...","use":"..."}]}`;
      const reply = await window.CV_AI.complete(prompt);
      let parsed = null;
      try { parsed = JSON.parse(reply); }
      catch {
        const m = String(reply).match(/\{[\s\S]*\}/);
        if (m) { try { parsed = JSON.parse(m[0]); } catch {} }
      }
      if (parsed && Array.isArray(parsed.entries)) {
        setProposal({
          intent: parsed.intent || ask,
          entries: parsed.entries.filter(e => e.name && e.value).slice(0, 8),
        });
      } else {
        window.dsaToast?.('Vi returned something I could not parse. Try again.');
      }
    } catch {
      window.dsaToast?.('Generation failed. Try again.');
    } finally {
      setGenerating(false);
    }
  }

  function adoptOne(name, value) {
    if (isLocked(name)) {
      window.dsaToast?.(`${name} is locked — unlock first`);
      return;
    }
    setEdit(name, value);
    window.dsaToast?.(`Adopted --${name}`);
  }
  function adoptAll() {
    if (!proposal) return;
    let n = 0;
    for (const e of proposal.entries) {
      if (isLocked(e.name)) continue;
      setEdit(e.name, e.value);
      n++;
    }
    setProposal(null);
    setGenOpen(false);
    window.dsaToast?.(`Adopted ${n} token${n === 1 ? '' : 's'} from Vi`);
  }

  const editCount = Object.keys(editsObj).length;

  return (
    <>
      <CanvasHeader
        title="Motion & space"
        sub={`Spacing · radii · shadows · motion — ${BASE_SPACING.length + BASE_RADII.length + BASE_SHADOWS.length + BASE_MOTION.length} tokens that quietly hold every component together`}
        actions={<>
          {(locked || []).length > 0 && (
            <span style={{display:'inline-flex',alignItems:'center',gap:6,padding:'5px 10px',background:'var(--accent-gold-50)',borderRadius:999,font:'500 11px/1 var(--font-body)',color:'var(--fg-primary)'}}>
              🔒 {locked.length} locked
            </span>
          )}
          {editCount > 0 && (
            <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={() => {
              if (!confirm(`Revert all ${editCount} pattern edit${editCount === 1 ? '' : 's'} back to defaults?`)) return;
              Object.keys(editsObj).forEach(k => setEdit(k, undefined));
              window.dsaToast?.('Pattern edits reverted');
            }}>↺ Revert {editCount}</button>
          )}
          <button className="dsa-btn dsa-btn--outline" onClick={() => {
            if (snapshot) { setSnapshot(null); window.dsaToast?.('Snapshot cleared'); }
            else {
              setSnapshot({ edits: { ...editsObj }, takenAt: new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'}) });
              window.dsaToast?.('Snapshot saved · live preview shows side-by-side');
            }
          }}>{snapshot ? 'Clear snapshot' : '📷 Save snapshot'}</button>
          <button className="dsa-btn dsa-btn--ai" onClick={() => setGenOpen(o => !o)}>
            <ViShape size={14}/> Generate with Vi
          </button>
        </>}
      />

      <div className="dsa-canvas-body">

        {/* Vi generation panel */}
        {genOpen && (
          <div className="dsa-gen-panel">
            <div className="dsa-gen-head">
              <ViShape size={18}/>
              <span className="dsa-gen-title">Tune {TAB_DEFS.find(t => t.id === tab)?.label.toLowerCase() || tab} with Vi</span>
              <button className="dsa-gen-close" onClick={() => { setGenOpen(false); setProposal(null); }}>✕</button>
            </div>
            <textarea
              className="dsa-gen-input" rows="2"
              placeholder='What do you need? e.g. "A taller shadow scale", "Tighter radii that feel sharper", "Add a snap easing"'
              value={genPrompt} onChange={e => setGenPrompt(e.target.value)}
            />
            <div className="dsa-gen-actions">
              <span className="dsa-gen-hint">Vi respects your locked tokens and the paper aesthetic.</span>
              <button className="dsa-btn dsa-btn--primary" onClick={generate} disabled={generating || !genPrompt.trim()}>
                {generating ? 'Generating…' : 'Generate'}
              </button>
            </div>
            {generating && (
              <div className="dsa-gen-loading">
                <ViShape size={14} animated/> Vi is shaping tokens that match your rhythm…
              </div>
            )}
            {proposal && (
              <div style={{marginTop:14}}>
                <div style={{font:'600 12px/1 var(--font-body)',color:'var(--fg-secondary)',marginBottom:10}}>
                  Proposed: <b style={{color:'var(--fg-primary)'}}>{proposal.intent}</b>
                </div>
                <div style={{display:'flex',flexDirection:'column',gap:6}}>
                  {proposal.entries.map((e, i) => (
                    <div key={i} style={{
                      display:'grid',gridTemplateColumns:'150px 1fr 80px',gap:14,alignItems:'center',
                      padding:'10px 12px',background:'var(--bg-surface)',borderRadius:'var(--r-md)',
                      border:'1px dashed var(--accent-gold-dashed)',
                    }}>
                      <div>
                        <div style={{font:'700 12px/1.1 var(--font-display)',color:'var(--fg-primary)'}}>--{e.name}</div>
                        {e.use && <div style={{font:'400 10px/1.2 var(--font-body)',color:'var(--fg-muted)',marginTop:3}}>{e.use}</div>}
                      </div>
                      <div style={{font:'500 11px/1.4 var(--font-mono)',color:'var(--accent-bronze)',wordBreak:'break-all'}}>{e.value}</div>
                      <button className="dsa-btn dsa-btn--outline dsa-btn--sm" onClick={() => adoptOne(e.name, e.value)}>Adopt</button>
                    </div>
                  ))}
                </div>
                <div style={{marginTop:14,display:'flex',gap:8,justifyContent:'flex-end'}}>
                  <button className="dsa-btn dsa-btn--ghost" onClick={() => setProposal(null)}>Discard</button>
                  <button className="dsa-btn dsa-btn--primary" onClick={adoptAll}>Adopt all →</button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Tab bar */}
        <div className="dsa-cat-bar" style={{marginBottom: 20}}>
          {TAB_DEFS.map(t => (
            <button key={t.id} className={tab === t.id ? 'active' : ''} onClick={() => setTab(t.id)}>
              {t.label} <span style={{
                marginLeft:6, padding:'2px 6px', borderRadius:999,
                background: tab === t.id ? 'var(--accent-gold-soft)' : 'var(--bg-muted)',
                font:'600 9px/1 var(--font-mono)', color:'var(--fg-secondary)',
              }}>{t.count}</span>
            </button>
          ))}
        </div>

        {tab === 'spacing' && (
          <SpacingPanel base={BASE_SPACING} get={get} setEdit={setEdit} isLocked={isLocked} toggleLock={toggleLock} editsObj={editsObj} copy={copy}/>
        )}
        {tab === 'radii' && (
          <RadiiPanel base={BASE_RADII} get={get} setEdit={setEdit} isLocked={isLocked} toggleLock={toggleLock} editsObj={editsObj} copy={copy}/>
        )}
        {tab === 'shadows' && (
          <ShadowsPanel base={BASE_SHADOWS} get={get} setEdit={setEdit} isLocked={isLocked} toggleLock={toggleLock} editsObj={editsObj} copy={copy}/>
        )}
        {tab === 'motion' && (
          <MotionPanel base={BASE_MOTION} get={get} setEdit={setEdit} isLocked={isLocked} toggleLock={toggleLock} editsObj={editsObj} copy={copy}/>
        )}

        {/* Live preview — uses all four scales together */}
        <div className="dsa-section" style={{marginTop:36}}>
          <div className="dsa-section-head">
            <h3 className="dsa-section-title">Live preview</h3>
            <span className="dsa-section-meta">Every component on every kit picks these up the moment you change a value.</span>
          </div>

          <PatternPreviewBlock label={snapshot ? 'Current (live edits)' : null} edits={editsObj}/>

          {snapshot && (
            <div style={{marginTop:14}}>
              <PatternPreviewBlock label={`Snapshot · ${snapshot.takenAt}`} edits={snapshot.edits || {}}/>
            </div>
          )}

          {editCount > 0 && (
            <div style={{
              marginTop:14, padding:'12px 14px',
              background:'var(--accent-gold-50)', borderRadius:'var(--r-md)',
              display:'flex',alignItems:'center',gap:12,
              font:'400 12px/1.4 var(--font-body)', color:'var(--fg-primary)',
            }}>
              <span style={{color:'var(--accent-gold)'}}>◆</span>
              <span><b>{editCount} pattern token{editCount === 1 ? '' : 's'}</b> edited in this session. Use <b>Export to disk</b> on the Overview to grab the CSS patch.</span>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

// ---------- Spacing panel ----------
function SpacingPanel({ base, get, setEdit, isLocked, toggleLock, editsObj, copy }) {
  return (
    <div className="dsa-section">
      <div className="dsa-section-head">
        <h3 className="dsa-section-title">Spacing scale</h3>
        <span className="dsa-section-meta">8-px base. Click a bar to retune; hold the rhythm — components break above ±2px.</span>
      </div>

      <div style={{
        background:'var(--bg-surface)', borderRadius:'var(--r-lg)',
        padding:'16px 18px', boxShadow:'var(--shadow-card)',
        display:'flex',flexDirection:'column',gap:6,
      }}>
        {base.map(t => {
          const px = Number(get(t.name, t.px));
          const edited = editsObj[t.name] != null;
          const locked = isLocked(t.name);
          return (
            <div key={t.name} style={{
              display:'grid',gridTemplateColumns:'72px 26px 1fr 80px 60px 28px',
              alignItems:'center',gap:12,
              padding:'6px 8px', borderRadius:'var(--r-sm)',
              background: edited ? 'var(--accent-gold-50)' : 'transparent',
            }}>
              <div style={{font:'600 12px/1 var(--font-mono)',color:'var(--accent-bronze)',display:'flex',alignItems:'center',gap:4}}>
                --{t.name}
                {edited && <span style={{font:'700 8px/1 var(--font-body)',color:'var(--accent-gold)',background:'var(--accent-gold-soft)',padding:'2px 4px',borderRadius:2,letterSpacing:'0.06em',textTransform:'uppercase'}}>edit</span>}
              </div>
              <button
                onClick={() => toggleLock(t.name)}
                title={locked ? 'Unlock' : 'Lock'}
                style={{
                  width:20,height:20,padding:0,borderRadius:'50%',
                  background: locked ? 'var(--accent-gold)' : 'transparent',
                  border:'1px solid ' + (locked ? 'var(--accent-gold)' : 'var(--border-faint)'),
                  color: locked ? 'var(--fg-primary)' : 'var(--fg-muted)',
                  cursor:'pointer',font:'400 10px/1 var(--font-body)',
                  display:'flex',alignItems:'center',justifyContent:'center',
                }}>{locked ? '🔒' : '🔓'}</button>
              <div style={{display:'flex',alignItems:'center',gap:6}}>
                <div style={{
                  height:14, width: Math.min(px, 600), background:'var(--accent-gold)',
                  borderRadius:2, transition:'width 160ms var(--ease-out)',
                }}/>
                {px === 0 && <span style={{font:'400 10px/1 var(--font-mono)',color:'var(--fg-muted)'}}>(no space)</span>}
              </div>
              <input
                type="number" min={0} max={400} value={px}
                onChange={e => setEdit(t.name, `${Math.max(0, parseInt(e.target.value || '0', 10))}px`)}
                disabled={locked}
                style={{
                  width:72, padding:'4px 8px',
                  background:'var(--bg-canvas)', border:'1px solid var(--border-faint)',
                  borderRadius:'var(--r-sm)', font:'500 11px/1.2 var(--font-mono)',
                  color:'var(--fg-primary)', outline:'none',
                  opacity: locked ? 0.5 : 1,
                }}
              />
              <button onClick={() => copy(`var(--${t.name})`)} style={{
                background:'transparent', border:'none', cursor:'pointer',
                font:'400 10px/1 var(--font-mono)', color:'var(--fg-muted)',
                padding:'4px 6px', textAlign:'left',
              }}>copy var</button>
              {edited && (
                <button onClick={() => setEdit(t.name, undefined)} title="Revert" style={{
                  background:'transparent', border:'none', cursor:'pointer',
                  color:'var(--fg-muted)', fontSize:14, padding:0,
                }}>↺</button>
              )}
              {!edited && <span/>}
            </div>
          );
        })}
      </div>

      {/* Rhythm preview */}
      <div style={{
        marginTop:16, padding:'16px 18px', background:'var(--bg-surface)',
        borderRadius:'var(--r-lg)', boxShadow:'var(--shadow-card)',
      }}>
        <div style={{font:'600 10px/1 var(--font-body)',letterSpacing:'0.08em',textTransform:'uppercase',color:'var(--fg-muted)',marginBottom:14}}>
          Rhythm in a stacked card
        </div>
        <div style={{
          background:'var(--bg-canvas)', borderRadius:'var(--r-md)',
          padding: `var(--s-6) var(--s-6)`,
          border: '1px solid var(--border-faint)',
        }}>
          <div style={{font:'700 italic 13px/1.1 var(--font-display)',color:'var(--accent-bronze)',marginBottom:'var(--s-3)'}}>Property overview</div>
          <div style={{font:'700 22px/1.1 var(--font-display)',color:'var(--fg-primary)',marginBottom:'var(--s-2)',letterSpacing:'-0.02em'}}>Tower East</div>
          <div style={{font:'400 13px/1.5 var(--font-body)',color:'var(--fg-secondary)',marginBottom:'var(--s-5)'}}>2 bed apartment with north-east aspect. Floor 14 of 22, completed Q4 2024.</div>
          <div style={{display:'flex',gap:'var(--s-2)',flexWrap:'wrap'}}>
            <button style={{background:'var(--accent-gold)',color:'var(--fg-primary)',border:'none',padding:'var(--s-2) var(--s-4)',borderRadius:'var(--r-md)',font:'600 12px/1 var(--font-body)',cursor:'pointer'}}>Publish</button>
            <button style={{background:'transparent',color:'var(--fg-primary)',border:'1.5px solid var(--accent-gold)',padding:'var(--s-2) var(--s-4)',borderRadius:'var(--r-md)',font:'600 12px/1 var(--font-body)',cursor:'pointer'}}>Preview</button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ---------- Radii panel ----------
function RadiiPanel({ base, get, setEdit, isLocked, toggleLock, editsObj, copy }) {
  return (
    <div className="dsa-section">
      <div className="dsa-section-head">
        <h3 className="dsa-section-title">Radii</h3>
        <span className="dsa-section-meta">Corners ramp from chip-sharp to pill. Stick to the scale — ad-hoc px values are the most common drift.</span>
      </div>
      <div style={{
        display:'grid',gridTemplateColumns:'repeat(auto-fill, minmax(160px, 1fr))',gap:12,
      }}>
        {base.map(t => {
          const px = Number(get(t.name, t.px));
          const edited = editsObj[t.name] != null;
          const locked = isLocked(t.name);
          const cap = Math.min(px, 60);
          return (
            <div key={t.name} className="dsa-swatch" style={edited ? {borderColor:'var(--accent-gold)'} : undefined}>
              <div className="dsa-swatch-color" style={{
                background: 'var(--accent-gold-soft)',
                height: 96, position: 'relative',
                display:'flex',alignItems:'center',justifyContent:'center',
              }}>
                <div style={{
                  width:72, height:72,
                  background:'var(--accent-gold)',
                  borderRadius: cap === 999 ? '50%' : `${cap}px`,
                  boxShadow:'var(--shadow-sm)',
                  transition:'border-radius 160ms var(--ease-out)',
                }}/>
                <button
                  onClick={(e) => { e.stopPropagation(); toggleLock(t.name); }}
                  title={locked ? 'Unlock' : 'Lock'}
                  style={{
                    position:'absolute', top:6, left:6,
                    width:20,height:20,padding:0,borderRadius:'50%',
                    background: locked ? 'var(--accent-gold)' : 'rgba(255,255,255,.85)',
                    border:'1px solid ' + (locked ? 'var(--accent-gold)' : 'var(--border-default)'),
                    color: locked ? 'var(--fg-primary)' : 'var(--fg-muted)',
                    cursor:'pointer', font:'400 10px/1 var(--font-body)',
                    display:'flex',alignItems:'center',justifyContent:'center',
                  }}>{locked ? '🔒' : '🔓'}</button>
                {edited && <span style={{position:'absolute',top:8,right:8,font:'700 8px/1 var(--font-body)',color:'var(--accent-gold)',background:'var(--accent-gold-soft)',padding:'3px 5px',borderRadius:2,letterSpacing:'0.06em',textTransform:'uppercase'}}>edit</span>}
              </div>
              <div className="dsa-swatch-meta">
                <div className="dsa-swatch-name">--{t.name}</div>
                <div style={{display:'flex',gap:6,alignItems:'center',marginTop:4}}>
                  {t.name === 'r-pill' ? (
                    <span className="dsa-swatch-hex">9999px</span>
                  ) : (
                    <input
                      type="number" min={0} max={120} value={px}
                      disabled={locked}
                      onChange={e => setEdit(t.name, `${Math.max(0, parseInt(e.target.value || '0', 10))}px`)}
                      style={{
                        width:64, padding:'3px 6px',
                        background:'var(--bg-canvas)', border:'1px solid var(--border-faint)',
                        borderRadius:'var(--r-sm)', font:'500 11px/1 var(--font-mono)',
                        color:'var(--accent-bronze)', outline:'none',
                        opacity: locked ? 0.5 : 1,
                      }}
                    />
                  )}
                  <button onClick={() => copy(`var(--${t.name})`)} style={{
                    marginLeft:'auto', background:'transparent', border:'none', cursor:'pointer',
                    font:'400 10px/1 var(--font-mono)', color:'var(--fg-muted)',
                  }}>copy</button>
                  {edited && (
                    <button onClick={() => setEdit(t.name, undefined)} title="Revert" style={{
                      background:'transparent',border:'none',cursor:'pointer',color:'var(--fg-muted)',fontSize:13,padding:0,
                    }}>↺</button>
                  )}
                </div>
                <div className="dsa-swatch-role">corners</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ---------- Shadows panel ----------
function ShadowsPanel({ base, get, setEdit, isLocked, toggleLock, editsObj, copy }) {
  return (
    <div className="dsa-section">
      <div className="dsa-section-head">
        <h3 className="dsa-section-title">Shadows</h3>
        <span className="dsa-section-meta">Warm-tinted (rgba(31,26,18,…)) — never cool grey. Layered Y-axis offsets give the paper feel.</span>
      </div>
      <div style={{
        display:'grid',gridTemplateColumns:'repeat(auto-fill, minmax(240px, 1fr))',gap:14,
      }}>
        {base.map(t => {
          const value = get(t.name, t.value);
          const edited = editsObj[t.name] != null;
          const locked = isLocked(t.name);
          return (
            <div key={t.name} style={{
              background:'var(--bg-surface)', borderRadius:'var(--r-md)',
              padding:'14px 16px 14px',
              border: edited ? '1px solid var(--accent-gold)' : '1px solid var(--border-faint)',
              display:'flex',flexDirection:'column',gap:10,
            }}>
              <div style={{
                background:'var(--bg-canvas)', borderRadius:'var(--r-md)',
                padding:'24px 18px 28px',
                display:'flex',alignItems:'center',justifyContent:'center',
                border:'1px dashed var(--border-faint)',
              }}>
                <div style={{
                  width:96,height:64,background:'var(--bg-surface)',
                  borderRadius:'var(--r-md)',boxShadow:value,
                  transition:'box-shadow 200ms var(--ease-out)',
                }}/>
              </div>
              <div style={{display:'flex',alignItems:'center',gap:6}}>
                <div style={{font:'700 12px/1.1 var(--font-display)',color:'var(--fg-primary)',display:'flex',alignItems:'center',gap:6}}>
                  --{t.name}
                  {edited && <span style={{font:'700 8px/1 var(--font-body)',color:'var(--accent-gold)',background:'var(--accent-gold-soft)',padding:'2px 4px',borderRadius:2,letterSpacing:'0.06em',textTransform:'uppercase'}}>edit</span>}
                </div>
                <button onClick={() => toggleLock(t.name)} title={locked ? 'Unlock' : 'Lock'} style={{
                  marginLeft:'auto',
                  width:20,height:20,padding:0,borderRadius:'50%',
                  background: locked ? 'var(--accent-gold)' : 'transparent',
                  border:'1px solid ' + (locked ? 'var(--accent-gold)' : 'var(--border-faint)'),
                  color: locked ? 'var(--fg-primary)' : 'var(--fg-muted)',
                  cursor:'pointer', font:'400 10px/1 var(--font-body)',
                  display:'flex',alignItems:'center',justifyContent:'center',
                }}>{locked ? '🔒' : '🔓'}</button>
              </div>
              <div style={{font:'400 10px/1 var(--font-body)',color:'var(--fg-muted)',textTransform:'uppercase',letterSpacing:'0.1em'}}>{t.use}</div>
              <textarea
                value={value} disabled={locked}
                onChange={e => setEdit(t.name, e.target.value)}
                rows={2}
                style={{
                  width:'100%', padding:'8px 10px',
                  background:'var(--bg-canvas)', border:'1px solid var(--border-faint)',
                  borderRadius:'var(--r-sm)', font:'400 10.5px/1.45 var(--font-mono)',
                  color:'var(--accent-bronze)', outline:'none', resize:'vertical',
                  opacity: locked ? 0.5 : 1,
                }}
              />
              <div style={{display:'flex',gap:6,alignItems:'center'}}>
                <button onClick={() => copy(`var(--${t.name})`)} className="dsa-btn dsa-btn--ghost dsa-btn--sm">Copy var</button>
                {edited && (
                  <button onClick={() => setEdit(t.name, undefined)} className="dsa-btn dsa-btn--ghost dsa-btn--sm">↺ Revert</button>
                )}
                <RefinePop
                  mode="dot"
                  placeholder={`Change "${t.name}" — e.g. softer, longer, warmer`}
                  onRefine={async (msg) => {
                    try {
                      const prompt = `Revise this CSS box-shadow value for ConceptV's warm paper-first system. Stay rgba(31,26,18,…) — no cool blue-grey shadows.

Current: ${value}
User wants: "${msg}"

Return ONLY JSON: {"value":"<new box-shadow CSS value>"}`;
                      const reply = await window.CV_AI.complete(prompt);
                      let parsed = null;
                      try { parsed = JSON.parse(reply); }
                      catch {
                        const m = String(reply).match(/\{[\s\S]*\}/);
                        if (m) { try { parsed = JSON.parse(m[0]); } catch {} }
                      }
                      if (parsed?.value) {
                        setEdit(t.name, parsed.value);
                        window.dsaToast?.(`Refined --${t.name}`);
                      } else {
                        window.dsaToast?.('Vi returned nothing usable');
                      }
                    } catch {
                      window.dsaToast?.('Refine failed');
                    }
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ---------- Motion panel ----------
function MotionPanel({ base, get, setEdit, isLocked, toggleLock, editsObj, copy }) {
  const easings = base.filter(t => t.kind === 'easing');
  const durations = base.filter(t => t.kind === 'duration');
  const [playKey, setPlayKey] = useState_pt(0);

  function parseBezier(v) {
    const m = String(v).match(/cubic-bezier\(([^)]+)\)/);
    if (!m) return null;
    const parts = m[1].split(',').map(s => parseFloat(s.trim()));
    if (parts.length === 4 && parts.every(n => !Number.isNaN(n))) return parts;
    return null;
  }

  return (
    <div className="dsa-section">
      <div className="dsa-section-head">
        <h3 className="dsa-section-title">Motion</h3>
        <span className="dsa-section-meta">Calm by default — ease-out 200ms is the workhorse. Click the curve to replay.</span>
      </div>

      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:14}}>
        {/* Easings */}
        <div style={{background:'var(--bg-surface)',borderRadius:'var(--r-lg)',padding:'18px 20px',boxShadow:'var(--shadow-card)'}}>
          <div style={{font:'600 10px/1 var(--font-body)',letterSpacing:'0.08em',textTransform:'uppercase',color:'var(--fg-muted)',marginBottom:14}}>Easings</div>
          <div style={{display:'flex',flexDirection:'column',gap:14}}>
            {easings.map(t => {
              const value = get(t.name, t.value);
              const edited = editsObj[t.name] != null;
              const locked = isLocked(t.name);
              const b = parseBezier(value);
              return (
                <div key={t.name} style={{
                  padding:12, borderRadius:'var(--r-md)',
                  background: edited ? 'var(--accent-gold-50)' : 'var(--bg-canvas)',
                  border:'1px solid var(--border-faint)',
                }}>
                  <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:8}}>
                    <div style={{font:'700 12px/1.1 var(--font-display)',color:'var(--fg-primary)',display:'flex',alignItems:'center',gap:6}}>
                      --{t.name}
                      {edited && <span style={{font:'700 8px/1 var(--font-body)',color:'var(--accent-gold)',background:'var(--accent-gold-soft)',padding:'2px 4px',borderRadius:2,letterSpacing:'0.06em',textTransform:'uppercase'}}>edit</span>}
                    </div>
                    <span style={{font:'400 10px/1 var(--font-body)',color:'var(--fg-muted)',textTransform:'uppercase',letterSpacing:'0.1em'}}>{t.use}</span>
                    <button onClick={() => toggleLock(t.name)} title={locked ? 'Unlock' : 'Lock'} style={{
                      marginLeft:'auto',
                      width:20,height:20,padding:0,borderRadius:'50%',
                      background: locked ? 'var(--accent-gold)' : 'transparent',
                      border:'1px solid ' + (locked ? 'var(--accent-gold)' : 'var(--border-faint)'),
                      color: locked ? 'var(--fg-primary)' : 'var(--fg-muted)',
                      cursor:'pointer', font:'400 10px/1 var(--font-body)',
                      display:'flex',alignItems:'center',justifyContent:'center',
                    }}>{locked ? '🔒' : '🔓'}</button>
                  </div>
                  <div style={{display:'grid',gridTemplateColumns:'120px 1fr',gap:14,alignItems:'center'}}>
                    <svg viewBox="0 0 100 100" width="100" height="100" onClick={() => setPlayKey(k => k+1)} style={{cursor:'pointer',background:'var(--bg-surface)',borderRadius:'var(--r-sm)',border:'1px solid var(--border-faint)'}}>
                      <defs><pattern id={`grid-${t.name}`} width="20" height="20" patternUnits="userSpaceOnUse"><path d="M 20 0 L 0 0 0 20" fill="none" stroke="var(--border-faint)" strokeWidth="0.5"/></pattern></defs>
                      <rect width="100" height="100" fill={`url(#grid-${t.name})`}/>
                      {b && (
                        <path
                          d={`M 0 100 C ${b[0]*100} ${100 - b[1]*100}, ${b[2]*100} ${100 - b[3]*100}, 100 0`}
                          fill="none" stroke="var(--accent-gold)" strokeWidth="2"/>
                      )}
                      {/* play dot */}
                      <circle r="3" fill="var(--accent-bronze)">
                        <animateMotion key={playKey} dur={`${(editsObj['dur-base'] || '600ms')}`} repeatCount="1" fill="freeze"
                          path={b ? `M 0 100 C ${b[0]*100} ${100 - b[1]*100}, ${b[2]*100} ${100 - b[3]*100}, 100 0` : 'M 0 100 L 100 0'}/>
                      </circle>
                    </svg>
                    <div style={{display:'flex',flexDirection:'column',gap:6}}>
                      <input
                        value={value} disabled={locked}
                        onChange={e => setEdit(t.name, e.target.value)}
                        style={{
                          padding:'6px 10px',background:'var(--bg-surface)',
                          border:'1px solid var(--border-faint)',borderRadius:'var(--r-sm)',
                          font:'500 11px/1.2 var(--font-mono)',color:'var(--accent-bronze)',outline:'none',
                          opacity: locked ? 0.5 : 1,
                        }}/>
                      {/* Animated dot demo */}
                      <div style={{
                        background:'var(--bg-surface)',border:'1px solid var(--border-faint)',
                        borderRadius:'var(--r-sm)', padding:'8px 10px', overflow:'hidden', position:'relative', height: 22,
                      }}>
                        <div key={playKey + '-' + t.name + '-' + value} style={{
                          width:14,height:14,borderRadius:'50%',background:'var(--accent-gold)',
                          position:'absolute',top:'50%',left:0,marginTop:-7,
                          animation: `dsa-pat-slide 900ms ${value} 1 forwards`,
                        }}/>
                      </div>
                      <div style={{display:'flex',gap:6}}>
                        <button onClick={() => setPlayKey(k => k+1)} className="dsa-btn dsa-btn--outline dsa-btn--sm">▶ Replay</button>
                        <button onClick={() => copy(`var(--${t.name})`)} className="dsa-btn dsa-btn--ghost dsa-btn--sm">Copy var</button>
                        {edited && <button onClick={() => setEdit(t.name, undefined)} className="dsa-btn dsa-btn--ghost dsa-btn--sm">↺ Revert</button>}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Durations */}
        <div style={{background:'var(--bg-surface)',borderRadius:'var(--r-lg)',padding:'18px 20px',boxShadow:'var(--shadow-card)'}}>
          <div style={{font:'600 10px/1 var(--font-body)',letterSpacing:'0.08em',textTransform:'uppercase',color:'var(--fg-muted)',marginBottom:14}}>Durations</div>
          <div style={{display:'flex',flexDirection:'column',gap:10}}>
            {durations.map(t => {
              const value = get(t.name, t.value);
              const edited = editsObj[t.name] != null;
              const locked = isLocked(t.name);
              const ms = parseInt(String(value).replace(/\D+/g, ''), 10) || 0;
              return (
                <div key={t.name} style={{
                  display:'grid',gridTemplateColumns:'100px 28px 1fr 80px 28px',
                  alignItems:'center',gap:10,
                  padding:'10px 12px', borderRadius:'var(--r-md)',
                  background: edited ? 'var(--accent-gold-50)' : 'var(--bg-canvas)',
                  border:'1px solid var(--border-faint)',
                }}>
                  <div style={{display:'flex',flexDirection:'column',gap:3}}>
                    <div style={{font:'700 12px/1.1 var(--font-display)',color:'var(--fg-primary)'}}>--{t.name}</div>
                    <div style={{font:'400 9px/1 var(--font-body)',color:'var(--fg-muted)',textTransform:'uppercase',letterSpacing:'0.1em'}}>{t.use}</div>
                  </div>
                  <button onClick={() => toggleLock(t.name)} title={locked ? 'Unlock' : 'Lock'} style={{
                    width:20,height:20,padding:0,borderRadius:'50%',
                    background: locked ? 'var(--accent-gold)' : 'transparent',
                    border:'1px solid ' + (locked ? 'var(--accent-gold)' : 'var(--border-faint)'),
                    color: locked ? 'var(--fg-primary)' : 'var(--fg-muted)',
                    cursor:'pointer', font:'400 10px/1 var(--font-body)',
                    display:'flex',alignItems:'center',justifyContent:'center',
                  }}>{locked ? '🔒' : '🔓'}</button>
                  <div style={{position:'relative',height:18,background:'var(--bg-surface)',borderRadius:'var(--r-sm)',border:'1px solid var(--border-faint)',overflow:'hidden'}}>
                    <div key={playKey + '-' + t.name + '-' + value} style={{
                      width:14,height:14,borderRadius:'50%',background:'var(--accent-gold)',
                      position:'absolute',top:'50%',left:0,marginTop:-7,
                      animation: `dsa-pat-slide ${value} var(--ease-out) 1 forwards`,
                    }}/>
                  </div>
                  <input
                    type="number" min={0} max={3000} step={20} value={ms}
                    disabled={locked}
                    onChange={e => setEdit(t.name, `${Math.max(0, parseInt(e.target.value || '0', 10))}ms`)}
                    style={{
                      width:72, padding:'4px 8px',
                      background:'var(--bg-canvas)', border:'1px solid var(--border-faint)',
                      borderRadius:'var(--r-sm)', font:'500 11px/1.2 var(--font-mono)',
                      color:'var(--accent-bronze)', outline:'none',
                      opacity: locked ? 0.5 : 1,
                    }}
                  />
                  {edited
                    ? <button onClick={() => setEdit(t.name, undefined)} title="Revert" style={{background:'transparent',border:'none',cursor:'pointer',color:'var(--fg-muted)',fontSize:14,padding:0}}>↺</button>
                    : <span/>}
                </div>
              );
            })}
            <button onClick={() => setPlayKey(k => k+1)} className="dsa-btn dsa-btn--outline dsa-btn--sm" style={{alignSelf:'flex-start',marginTop:6}}>▶ Replay all</button>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes dsa-pat-slide {
          from { left: 0%; transform: translateX(0); }
          to   { left: 100%; transform: translateX(-100%); }
        }
      `}</style>
    </div>
  );
}

// ---------- Live preview ----------
function PatternPreviewBlock({ label, edits }) {
  const editsObj = edits || {};
  function v(name, fallback) { return editsObj[name] ?? fallback; }

  // Local style object so this preview ignores the global :root edits when
  // showing the snapshot.
  const local = {
    '--s-1':  v('s-1',  '4px'),
    '--s-2':  v('s-2',  '8px'),
    '--s-3':  v('s-3',  '12px'),
    '--s-4':  v('s-4',  '16px'),
    '--s-5':  v('s-5',  '20px'),
    '--s-6':  v('s-6',  '24px'),
    '--r-sm': v('r-sm', '6px'),
    '--r-md': v('r-md', '8px'),
    '--r-lg': v('r-lg', '12px'),
    '--r-xl': v('r-xl', '16px'),
    '--shadow-sm':    v('shadow-sm',    '0 1px 3px rgba(31, 26, 18, 0.06), 0 1px 2px rgba(31, 26, 18, 0.04)'),
    '--shadow-card':  v('shadow-card',  '0 1px 2px rgba(31, 26, 18, 0.04), 0 4px 14px rgba(31, 26, 18, 0.05)'),
    '--shadow-pop':   v('shadow-pop',   '0 8px 28px rgba(31, 26, 18, 0.12), 0 2px 6px rgba(31, 26, 18, 0.06)'),
    '--ease-out':     v('ease-out',     'cubic-bezier(.2, .8, .2, 1)'),
    '--dur-base':     v('dur-base',     '200ms'),
  };

  return (
    <div style={{
      ...local,
      background: 'var(--bg-canvas)',
      borderRadius: 'var(--r-lg)',
      padding: 'var(--s-5) var(--s-6) var(--s-6)',
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
      <div style={{font:'600 10px/1 var(--font-body)',letterSpacing:'0.08em',textTransform:'uppercase',color:'var(--fg-muted)',marginBottom:'var(--s-4)'}}>One card · all four scales</div>

      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:'var(--s-4)'}}>
        {/* Card with shadow + radii + spacing */}
        <div style={{
          background:'var(--bg-surface)',
          borderRadius:'var(--r-lg)',
          padding:'var(--s-5) var(--s-6)',
          boxShadow:'var(--shadow-card)',
          transition:'box-shadow var(--dur-base) var(--ease-out), transform var(--dur-base) var(--ease-out)',
        }}>
          <div style={{font:'700 italic 11px/1 var(--font-display)',color:'var(--accent-bronze)',letterSpacing:'-0.005em',marginBottom:'var(--s-2)'}}>Property</div>
          <div style={{font:'700 18px/1.1 var(--font-display)',color:'var(--fg-primary)',letterSpacing:'-0.02em',marginBottom:'var(--s-2)'}}>Tower East</div>
          <div style={{font:'400 12px/1.5 var(--font-body)',color:'var(--fg-secondary)',marginBottom:'var(--s-4)'}}>2 bed apartment with north-east aspect.</div>
          <div style={{display:'flex',gap:'var(--s-2)',flexWrap:'wrap'}}>
            <button style={{background:'var(--accent-gold)',color:'var(--fg-primary)',border:'none',padding:'var(--s-2) var(--s-3)',borderRadius:'var(--r-md)',font:'600 11px/1 var(--font-body)',cursor:'pointer',boxShadow:'var(--shadow-sm)',transition:'box-shadow var(--dur-fast) var(--ease-out)'}}>Publish</button>
            <button style={{background:'transparent',color:'var(--fg-primary)',border:'1.5px solid var(--accent-gold)',padding:'var(--s-2) var(--s-3)',borderRadius:'var(--r-md)',font:'600 11px/1 var(--font-body)',cursor:'pointer'}}>Preview</button>
          </div>
        </div>

        {/* Tag + popover demo */}
        <div style={{
          background:'var(--accent-gold-50)',
          borderRadius:'var(--r-md)',
          padding:'var(--s-4) var(--s-5)',
          display:'flex',flexDirection:'column',gap:'var(--s-2)',
        }}>
          <div style={{display:'flex',gap:'var(--s-1)',flexWrap:'wrap'}}>
            {['gold','bronze','approved','review'].map(t => (
              <span key={t} style={{
                font:'600 10px/1 var(--font-body)',
                padding:'var(--s-1) var(--s-3)',
                background:'var(--bg-surface)',
                color:'var(--accent-bronze)',
                borderRadius:'var(--r-pill)',
                border:'1px solid var(--border-default)',
                boxShadow:'var(--shadow-sm)',
              }}>{t}</span>
            ))}
          </div>
          <div style={{
            background:'var(--bg-surface)',borderRadius:'var(--r-md)',
            padding:'var(--s-3) var(--s-4)',boxShadow:'var(--shadow-pop)',
            font:'500 11px/1.4 var(--font-body)',color:'var(--fg-primary)',
            marginTop:'var(--s-2)',
          }}>
            <div style={{font:'700 italic 11px/1 var(--font-display)',color:'var(--accent-bronze)',marginBottom:'var(--s-1)'}}>Popover</div>
            Floating surface uses <code style={{font:'500 10px/1 var(--font-mono)',color:'var(--accent-gold)'}}>--shadow-pop</code> and <code style={{font:'500 10px/1 var(--font-mono)',color:'var(--accent-gold)'}}>--r-md</code>.
          </div>
        </div>
      </div>

      {/* Motion strip */}
      <div style={{marginTop:'var(--s-4)',display:'flex',alignItems:'center',gap:'var(--s-3)',padding:'var(--s-3) var(--s-4)',background:'var(--bg-surface)',borderRadius:'var(--r-md)',boxShadow:'var(--shadow-sm)'}}>
        <div style={{font:'600 10px/1 var(--font-body)',letterSpacing:'0.08em',textTransform:'uppercase',color:'var(--fg-muted)',width:96}}>Motion</div>
        <PatternMotionStrip easing={local['--ease-out']} duration={local['--dur-base']}/>
      </div>
    </div>
  );
}

function PatternMotionStrip({ easing, duration }) {
  const [k, setK] = useState_pt(0);
  return (
    <div style={{flex:1,position:'relative',height:18,background:'var(--bg-canvas)',borderRadius:'var(--r-sm)',border:'1px solid var(--border-faint)',overflow:'hidden',cursor:'pointer'}} onClick={() => setK(x => x+1)}>
      <div key={k} style={{
        width:14,height:14,borderRadius:'50%',background:'var(--accent-gold)',
        position:'absolute',top:'50%',left:0,marginTop:-7,
        animation: `dsa-pat-slide ${duration} ${easing} 1 forwards`,
      }}/>
      <div style={{position:'absolute',right:8,top:'50%',transform:'translateY(-50%)',font:'400 10px/1 var(--font-mono)',color:'var(--fg-muted)',pointerEvents:'none'}}>{duration} · click to replay</div>
    </div>
  );
}

window.Patterns = Patterns;
