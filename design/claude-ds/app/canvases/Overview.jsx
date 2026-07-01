// canvases/Overview.jsx — system health dashboard

// ── FaceMarker: the page-face marker that sits ON a real thing that has a face ──────────────────
// window.CV_FACES is keyed by the real Studio thing's id ('colors' → the Colors canvas's OWN face,
// model-authored from its real tokens). The marker only appears where a real thing actually has a
// face; clicking it opens that thing's real page (:8774). HOW it presents is the `style` prop,
// which is driven by a real TweakRadio variable (window.useTweaks) — flip it and every marker re-renders.
function FaceMarker({ id, style, mode }) {
  // MODE GATE — faces/how-tos only surface when the surface is in a relational mode (system-creator,
  // "show how it works", higher-order, contextual-nav). In normal use they're hidden — an end user
  // isn't meant to see them without purpose. `off` = hidden everywhere.
  if (mode === 'off') return null;
  const face = (window.CV_FACES || {})[id];
  if (!face) return null;                                  // no face on this thing → no marker (the real lens)
  const open = (e) => { if (e) e.stopPropagation(); window.open(face.url, '_blank', 'noopener'); };
  const tip = 'Open the page — ' + face.title;
  // FOUR presentations of the same real face, all sitting ON the real tile, all opening the real page.
  if (style === 'preview') {                               // A — the page's real excerpt, in-tile
    return (
      <div className="dsa-face-strip" onClick={open} title={tip}>
        <span className="ex">{face.excerpt}</span>
        <span className="open">▦ Open face ↗</span>
      </div>
    );
  }
  if (style === 'relational') {                            // B — the relation, as a GENERATED glyphic
    // The marker is composed by CV_GLYPHIC.composeRelation from the typed registry data (face.rel:
    // source node-type → edge kind → target/page node-type). NOT hand-drawn — delete the old hand-CSS
    // and this still renders, because the shape/line/arrow come out of the engine (Glyphics + CV_EDGES).
    const GL = typeof window !== 'undefined' ? window.CV_GLYPHIC : null;
    if (GL && GL.composeRelation && face.rel) {
      const r = GL.composeRelation(face.rel, { nodeSize: 22, edgeLength: 26 });
      return <div className="dsa-face-glyph" onClick={open} title={tip}
                  dangerouslySetInnerHTML={{ __html: r.html }}/>;
    }
    return <button className="dsa-face-marker" onClick={open} title={tip}>▦ Face ↗</button>;
  }
  if (style === 'inline') {                                // C — a small face panel inline on the tile
    return (
      <div className="dsa-face-inline-tile" onClick={open} title={tip}>
        <span className="cap">Its face</span>
        <span className="ttl">{face.title}</span>
        <span className="open">Open ↗</span>
      </div>
    );
  }
  return (                                                 // D — the compact lens badge (default)
    <button className="dsa-face-marker" onClick={open} title={tip}>▦ Face ↗</button>
  );
}

function Overview({ counts, onNav, recentActivity, onExport, onReset, onSearch }) {
  // the marker presentation is a REAL tweak variable (the system's own tweak mechanism)
  const [tw, setTweak] = window.useTweaks({ faceStyle: 'relational', faceMode: 'explain' });

  const stats = [
    { id: 'colors',   icon: 'color-swatches', label: 'Colors',   value: counts.colorCount,   sub: 'tokens',     to: 'colors',   delta: '+2 this week', deltaKind: 'up' },
    { id: 'icons',    icon: 'star',           label: 'Icons',    value: counts.iconCount,    sub: 'glyphs',     to: 'icons',    delta: '+12 new',      deltaKind: 'up' },
    { id: 'comps',    icon: 'check-square',   label: 'Components', value: counts.componentCount, sub: 'patterns', to: 'components', delta: '3 to triage', deltaKind: 'gap' },
    { id: 'inbox',    icon: 'files-stack',    label: 'Inbox',    value: counts.inboxCount,   sub: 'untriaged',  to: 'inbox',    delta: counts.inboxNew ? 'needs you' : 'clear', deltaKind: counts.inboxNew ? 'gap' : 'up' },
  ];
  const canvases = [
    { id: 'colors',    label: 'Colors',    icon: 'color-swatches', sub: counts.colorCount + ' tokens' },
    { id: 'icons',     label: 'Icons',     icon: 'star',           sub: counts.iconCount + ' glyphs' },
    { id: 'voice',     label: 'Voice & tone', icon: 'chat-double', sub: 'Rules, examples, rewriter' },
    { id: 'templates', label: 'Templates', icon: 'browser',        sub: 'Slides, brochures, hubs' },
    { id: 'logos',     label: 'Logos & marks', icon: 'tag',        sub: counts.logoCount + ' assets' },
    { id: 'patterns',  label: 'Motion & space', icon: 'adjustments', sub: 'Shadows, radii, easing' },
  ];

  return (
    <>
      <CanvasHeader
        title="Overview"
        sub="Everything ConceptV owns, at a glance. Click any tile to dive into that part of the system."
        actions={<>
          <button className="dsa-btn dsa-btn--ghost" onClick={() => window.postMessage({type:'__activate_edit_mode'}, '*')} title="Tweak how page-faces show">⚙ Face tweak</button>
          <button className="dsa-btn dsa-btn--ghost" onClick={onSearch} title="Search everything · ⌘K">
            <CvIcon name="search" size={14}/> Search <span style={{font:'500 10px/1 var(--font-mono)',color:'var(--fg-muted)',background:'var(--bg-muted)',padding:'2px 5px',borderRadius:3,marginLeft:6}}>⌘K</span>
          </button>
          <button className="dsa-btn dsa-btn--ghost" onClick={onReset} title="Clear all session edits">↺ Reset</button>
          <button className="dsa-btn dsa-btn--outline" onClick={onExport}>Export to disk</button>
          <button className="dsa-btn dsa-btn--ai" onClick={() => onNav('build')}>
            <ViShape size={14}/> Build something
          </button>
        </>}
      />
      <div className="dsa-canvas-body">

        <div className="dsa-section">
          <div className="dsa-section-head">
            <h3 className="dsa-section-title">System at a glance</h3>
            <span className="dsa-section-meta">Live · last updated 1m ago</span>
          </div>
          <div className="dsa-stat-grid">
            {stats.map(s => (
              <div key={s.id} className="dsa-stat" onClick={() => onNav(s.to)} style={{position:'relative'}}>
                <FaceMarker id={s.to} style={tw.faceStyle} mode={tw.faceMode}/>
                <div className="label">
                  <span className="gly"><CvIcon name={s.icon} size={14}/></span>
                  {s.label}
                </div>
                <div className="v">{s.value}<span className="sub">{s.sub}</span></div>
                <div className={`delta ${s.deltaKind}`}>{s.delta}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="dsa-section">
          <div className="dsa-section-head">
            <h3 className="dsa-section-title">Canvases</h3>
            <span className="dsa-section-meta">Open any to browse, edit, or generate</span>
          </div>
          <div className="dsa-canvas-grid">
            {canvases.map(c => (
              <div key={c.id} className="dsa-canvas-tile" onClick={() => onNav(c.id)} style={{position:'relative'}}>
                <FaceMarker id={c.id} style={tw.faceStyle} mode={tw.faceMode}/>
                <div className="preview">
                  <CvIcon name={c.icon} size={36} tone="bronze"/>
                </div>
                <div>
                  <div className="name">{c.label}</div>
                  <div className="meta">{c.sub}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="dsa-section">
          <div className="dsa-section-head">
            <h3 className="dsa-section-title">Recent activity</h3>
            <span className="dsa-section-link">View all →</span>
          </div>
          <div className="dsa-activity">
            {recentActivity.map((a, i) => (
              <div key={i} className="dsa-activity-row">
                <span className="bullet" aria-hidden="true">▶</span>
                <span><span style={{color: a.color || 'var(--accent-bronze)',marginRight:6,display:'inline-flex',verticalAlign:'-2px'}}>
                  <CvIcon name={a.icon} size={14} tone={a.color ? 'gold' : 'bronze'}/>
                </span>{a.text} <span className="by">{a.by}</span></span>
                <span className="time">{a.time}</span>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* the marker presentation is a real tweak — flip it, every marker on the surface re-renders */}
      <TweaksPanel title="Page-faces">
        <TweakSection label="Mode"/>
        <TweakRadio label="Faces visible in" value={tw.faceMode} options={['off', 'explain']}
                    onChange={(v) => setTweak('faceMode', v)}/>
        <TweakSection label="Page-face marker"/>
        <TweakRadio label="Show as" value={tw.faceStyle}
                    options={['badge', 'preview', 'relational', 'inline']}
                    onChange={(v) => setTweak('faceStyle', v)}/>
      </TweaksPanel>
    </>
  );
}
window.Overview = Overview;
