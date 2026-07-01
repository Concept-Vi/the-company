// atomicity/Explore.jsx
// ============================================================================
// Explore — select an element directly ON the live product surface, then have
// Vi generate distinct style directions for it; the focused direction applies
// to that element right there on screen. Like/dislike to steer, iterate, then
// promote the keeper into the system. Selection-on-canvas is the core gesture.
// ============================================================================
const { useState: useState_ex, useMemo: useMemo_ex, useReducer: useReducer_ex, useEffect: useEffect_ex } = React;
const { StateDot: StateDot_ex } = window.AcKit;

const HOTSPOTS = [
  { id: 'card', label: 'the card' },
  { id: 'button', label: 'the button' },
  { id: 'price', label: 'the price' },
  { id: 'badge', label: 'the tour tag' },
  { id: 'stat', label: 'a stat' },
];

function AcExplore() {
  const E = window.CV_EXPLORE;
  const [sel, setSel] = useState_ex(null);          // selected element id (on canvas)
  const [variants, setVariants] = useState_ex([]);
  const [liked, setLiked] = useState_ex([]);
  const [disliked, setDisliked] = useState_ex({});
  const [focus, setFocus] = useState_ex(null);      // recipe applied to selected el
  const [intent, setIntent] = useState_ex('');
  const [busy, setBusy] = useState_ex(false);
  const [promoted, setPromoted] = useState_ex(null);
  const [, forceGal] = useReducer_ex(x => x + 1, 0);
  useEffect_ex(() => window.CV_EXPLORE.onGallery(forceGal), []);
  const gal = window.CV_EXPLORE.gallery();
  const taste = useMemo_ex(() => E.tasteProfile(liked), [liked]);
  const labelFor = id => (HOTSPOTS.find(h => h.id === id) || {}).label || id;

  function selectEl(id) { setSel(id); setVariants([]); setLiked([]); setDisliked({}); setFocus(null); setPromoted(null); }
  async function generate(extra, seed) {
    if (!sel) return; setBusy(true); setPromoted(null);
    try {
      const v = await E.variations({ element: sel, intent: extra || intent, n: 4, liked: seed ? [seed] : liked, disliked: Object.values(disliked) });
      setVariants(v); setFocus(v[0] || null);
    } catch (e) { window.dsaToast?.(e.message || 'Generation failed'); }
    setBusy(false);
  }
  function like(v) { setLiked(L => L.some(x => x.id === v.id) ? L : [...L, v]); setDisliked(m => { const n = { ...m }; delete n[v.id]; return n; }); setFocus(v); }
  function dislike(v) { setDisliked(m => ({ ...m, [v.id]: v })); setLiked(L => L.filter(x => x.id !== v.id)); }
  function promote() {
    if (!focus || !sel) return;
    const r = E.promote({ element: sel, recipe: focus, name: focus.name });
    setPromoted({ name: focus.name || labelFor(sel), id: r.id, staged: !!r.staged });
    window.dsaToast?.('“' + (focus.name || sel) + '” is now in your system');
  }

  const appliedStyle = focus ? E.styleFor(focus) : null;

  return (
    <div className="ex3">
      <div className="ex3-head">
        <div className="ex3-head-tx">
          <h1>Explore</h1>
          <p>{sel ? <span>Restyling <b>{labelFor(sel)}</b> — pick a direction below, or generate more.</span> : <span>Click any part of the screen below to restyle it.</span>}</p>
        </div>
        {sel && (
          <div className="ex3-intent-row">
            <input className="ex2-intent" value={intent} onChange={e => setIntent(e.target.value)}
              placeholder={`A direction for ${labelFor(sel)}… (optional)`} onKeyDown={e => { if (e.key === 'Enter') generate(); }}/>
            <button className="fz2-btn solid" disabled={busy} onClick={() => generate()}>
              <CvIcon name="shuffle" size={13} tone="ink"/> {busy ? 'Exploring…' : variants.length ? 'More' : 'Generate'}
            </button>
          </div>
        )}
      </div>

      {gal.length > 0 && (
        <div className="ex3-gallery">
          <div className="ex3-gallery-lbl">Your components <span>{gal.length}</span></div>
          <div className="ex3-gallery-row">
            {gal.map(g => (
              <div key={g.id} className="ex3-gal-item" title={g.name + ' · ' + g.role}>
                <span className="ex3-gal-stage">{renderEl(g.role, window.CV_EXPLORE.styleFor(g.recipe), '')}</span>
                <span className="ex3-gal-name">{g.name}</span>
                <button className="ex3-gal-x" title="Remove" onClick={() => window.CV_EXPLORE.forget(g.id)}>✕</button>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="ex3-body">
        <div className="ex3-canvas-wrap">
          <Canvas sel={sel} appliedStyle={appliedStyle} onSelect={selectEl}/>
          {!sel && <div className="ex3-hint"><ViShape size={18}/> Click a part of the card to restyle it — or switch to <b>Inspect</b> mode (⌘E) to select anything on screen.</div>}
        </div>

        {sel && (
          <aside className="ex3-side">
            {variants.length === 0 && !busy && (
              <div className="ex3-side-empty"><ViShape size={26}/><p>Generate a spread of directions for <b>{labelFor(sel)}</b>.</p></div>
            )}
            {busy && variants.length === 0 && <div className="ex3-side-empty"><ViShape size={26} animated/><p>Sketching…</p></div>}

            {variants.length > 0 && (
              <div className="ex3-side-stack">
                <div className="ex3-strip">
                  {variants.map(v => {
                    const isLiked = liked.some(x => x.id === v.id), isDis = !!disliked[v.id], isFocus = focus && focus.id === v.id;
                    return (
                      <div key={v.id} className={`ex3-chip ${isFocus ? 'focus' : ''} ${isDis ? 'dim' : ''}`}>
                        <button className="ex3-chip-stage" onMouseEnter={() => setFocus(v)} onClick={() => setFocus(v)}>
                          {renderEl(sel, E.styleFor(v), '')}
                          {isFocus && <span className="ex3-chip-dot"><StateDot_ex state="selected"/></span>}
                        </button>
                        <div className="ex3-chip-meta">
                          <span className="ex3-chip-name">{v.name}</span>
                          <span className="ex3-chip-vote">
                            <button className={`ex2-vb ${isLiked ? 'on' : ''}`} title="More like this" onClick={() => like(v)}><CvIcon name="check" size={12} tone={isLiked ? 'gold' : 'bronze'}/></button>
                            <button className="ex2-vb" title="Not this" onClick={() => dislike(v)}><CvIcon name="close" size={12} tone="muted"/></button>
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>

                <div className="ex2-taste">
                  <div className="ex2-taste-head"><CvIcon name="sparkles" size={12} tone="gold"/> Your taste</div>
                  <div className="ex2-taste-body">{taste.summary}</div>
                  {taste.tags.length > 0 && <div className="ex2-conv"><span className="ex2-conv-fill" style={{ width: Math.round((taste.strength || 0) * 100) + '%' }}/></div>}
                </div>

                <div className="ex2-iterate">
                  <button className="ex2-chip" disabled={busy || !liked.length} onClick={() => generate('lean into the liked directions and refine')}>More like these</button>
                  <button className="ex2-chip" disabled={busy} onClick={() => generate('go bolder, diverge hard')}>Bolder</button>
                  <button className="ex2-chip" disabled={busy} onClick={() => generate('quieter, restrained, minimal')}>Quieter</button>
                  {focus && <button className="ex2-chip" disabled={busy} onClick={() => generate('subtle variations around this exact direction', focus)}>Refine this</button>}
                </div>

                {promoted ? (
                  <div className="ex2-done"><StateDot_ex state="active"/>
                    <div><b>“{promoted.name}” is in your system.</b><span>Registered as a {sel} component{promoted.staged ? ' · staged for review' : ''}. Find it in Under the hood › Registries.</span></div>
                  </div>
                ) : (
                  <button className="fz2-btn solid ex2-promote" disabled={!focus} onClick={promote}>
                    <CvIcon name="plus-square" size={14} tone="ink"/> Make “{focus ? (focus.name || labelFor(sel)) : '…'}” real
                  </button>
                )}
              </div>
            )}
          </aside>
        )}
      </div>
    </div>
  );
}

// the live product surface — every part is a selectable hotspot
function Canvas({ sel, appliedStyle, onSelect }) {
  const S = window.CV_EXPLORE.styleFor;
  const def = {
    card: {}, button: S({ bg: '--accent-gold', fg: '--ink', radius: '--r-md', shadow: '--elev-1' }),
    price: {}, badge: {}, stat: {},
  };
  const styleOf = id => (sel === id && appliedStyle) ? appliedStyle : def[id];
  const hot = (id, extra) => `ex3-hot ${sel === id ? 'on' : ''} ${extra || ''}`;
  return (
    <div className={hot('card', 'ex3-card')} style={styleOf('card')} onClick={e => { e.stopPropagation(); onSelect('card'); }}>
      {sel === 'card' && <span className="ex3-tag">the card</span>}
      <div className="ex3-photo">
        <button className={hot('badge', 'ex3-badge')} style={styleOf('badge')} onClick={e => { e.stopPropagation(); onSelect('badge'); }}>
          <CvIcon name="vr-headset" size={11} tone="ink"/> 360° tour{sel === 'badge' && <span className="ex3-tag">tag</span>}
        </button>
      </div>
      <div className="ex3-cbody">
        <div className="ex3-eyebrow">Property Wizard · listing</div>
        <div className="ex3-addr">14 Eclipse Boulevard</div>
        <button className={hot('price', 'ex3-price')} style={styleOf('price')} onClick={e => { e.stopPropagation(); onSelect('price'); }}>
          $1.84m{sel === 'price' && <span className="ex3-tag">price</span>}
        </button>
        <div className="ex3-stats">
          <button className={hot('stat', 'ex3-stat')} style={styleOf('stat')} onClick={e => { e.stopPropagation(); onSelect('stat'); }}>
            <b>23.8k</b> views{sel === 'stat' && <span className="ex3-tag">stat</span>}
          </button>
          <span className="ex3-stat-q"><b>4</b> bed</span><span className="ex3-stat-q"><b>2</b> bath</span>
        </div>
        <button className={hot('button', 'ex3-btn')} style={styleOf('button')} onClick={e => { e.stopPropagation(); onSelect('button'); }}>
          Book inspection{sel === 'button' && <span className="ex3-tag">button</span>}
        </button>
      </div>
    </div>
  );
}

function renderEl(elementId, style, content) {
  if (elementId === 'button') return <button className="ex-el-btn" style={style}>{content || 'Book inspection'}</button>;
  if (elementId === 'price') return <div className="ex-el-price" style={style}>{content || '$1.84m'}</div>;
  if (elementId === 'badge') return <span className="ex-el-badge" style={style}><CvIcon name="vr-headset" size={11} tone="ink"/> {content || '360°'}</span>;
  if (elementId === 'stat') return <div className="ex-el-stat" style={style}><b>{content || '23.8k'}</b></div>;
  return <div className="ex-el-card" style={style}><div className="ex-el-card-eyebrow">Wizard</div><div className="ex-el-card-title">{content || 'Eclipse'}</div></div>;
}

window.AcExplore = AcExplore;
