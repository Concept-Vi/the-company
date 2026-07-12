// canvases/Overview.jsx — system health dashboard
function Overview({ counts, onNav, recentActivity, onExport, onReset, onSearch }) {
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
              <div key={s.id} className="dsa-stat" onClick={() => onNav(s.to)}>
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
              <div key={c.id} className="dsa-canvas-tile" onClick={() => onNav(c.id)}>
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
    </>
  );
}
window.Overview = Overview;
