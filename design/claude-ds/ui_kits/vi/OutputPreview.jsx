// OutputPreview.jsx — the brochure being built, updates live
function BrochureSection({ label, state, children }) {
  const tag = state === 'done' ? <span className="check">✓</span>
            : state === 'pending' ? <span className="clock">●</span>
            : state === 'gap' ? <span className="gap">!</span>
            : null;
  const stateLabel = state === 'done' ? 'Filled' : state === 'pending' ? 'Drafting' : state === 'gap' ? 'Missing' : '';
  return (
    <div className={`vi-brochure-section ${state === 'pending' ? 'pending' : ''}`}>
      <span className="vi-brochure-label">{tag} {label} <span style={{color:'var(--fg-muted)',fontWeight:400,letterSpacing:'0.04em'}}>· {stateLabel}</span></span>
      {children}
    </div>
  );
}

function OutputPreview({ filled }) {
  return (
    <div className="vi-preview">
      <div style={{display:'flex',alignItems:'center',justifyContent:'space-between'}}>
        <span style={{font:'600 11px/1 var(--font-body)',color:'var(--fg-muted)',letterSpacing:'0.08em',textTransform:'uppercase'}}>Live preview · Brochure</span>
        <span style={{font:'500 11px/1 var(--font-body)',color:'var(--fg-muted)'}}>Auto-saves every change</span>
      </div>
      <div className="vi-brochure">
        <div className="vi-brochure-hero">
          <div className="vi-brochure-hero-text">
            <div className="eyebrow">Tower East · Sydney CBD</div>
            <div className="title">{filled.title ? 'Sky Apartments — From the 12th floor' : <span style={{opacity:.4}}>Generating title…</span>}</div>
          </div>
        </div>
        <div className="vi-brochure-body">
          <BrochureSection label="Brand & palette" state={filled.brand ? 'done' : 'pending'}>
            <div style={{display:'flex',gap:6,marginTop:2}}>
              {['#1F1A12','#E0C010','#988058','#F4E89A'].map(c => (
                <span key={c} style={{width:22,height:22,borderRadius:4,background:filled.brand?c:'var(--bg-muted)',border:'1px solid var(--border-faint)'}}/>
              ))}
            </div>
          </BrochureSection>

          <BrochureSection label="Feature stats" state={filled.stats ? 'done' : 'pending'}>
            {filled.stats ? (
              <div className="vi-brochure-grid">
                <div className="feat"><span className="v">2</span>BED</div>
                <div className="feat"><span className="v">2</span>BATH</div>
                <div className="feat"><span className="v">98m²</span>AREA</div>
                <div className="feat"><span className="v">1</span>CAR</div>
              </div>
            ) : (
              <>
                <div className="vi-brochure-value skel"/>
                <div className="vi-brochure-value skel"/>
              </>
            )}
          </BrochureSection>

          <BrochureSection label="Description" state={filled.description ? 'done' : 'pending'}>
            {filled.description ? (
              <div className="vi-brochure-value">Light-filled corner apartment with north-east aspect and harbour glimpses. Open-plan living anchored by a stone-topped island; a separate study nook…</div>
            ) : (
              <>
                <div className="vi-brochure-value skel"/>
                <div className="vi-brochure-value skel"/>
              </>
            )}
          </BrochureSection>

          <BrochureSection label="Starting price" state={filled.price ? 'done' : 'gap'}>
            <div className="vi-brochure-value" style={{color: filled.price ? 'var(--fg-primary)' : 'var(--status-error)'}}>
              {filled.price ? filled.price : '— missing —'}
            </div>
          </BrochureSection>

          <BrochureSection label="Agent contact" state={filled.agent ? 'done' : 'gap'}>
            <div className="vi-brochure-value" style={{color: filled.agent ? 'var(--fg-primary)' : 'var(--status-error)'}}>
              {filled.agent ? filled.agent : '— missing —'}
            </div>
          </BrochureSection>
        </div>
        <div className="vi-brochure-footer">
          <span>Source · Tower East Master Info</span>
          <span className="formats">
            <span className={`fmt ${filled.finalize ? 'active' : ''}`}>PDF</span>
            <span className={`fmt ${filled.finalize ? 'active' : ''}`}>DOC</span>
            <span className={`fmt ${filled.finalize ? 'active' : ''}`}>HTML</span>
          </span>
        </div>
      </div>
    </div>
  );
}

window.OutputPreview = OutputPreview;
