// screens/BrandKit.jsx
const { useState: useState_bk } = React;

function ColourRow({ value, label }) {
  return (
    <div style={{display:'flex',alignItems:'center',gap:14,padding:'8px 0'}}>
      <div style={{width:40,height:40,borderRadius:'var(--r-sm)',border:'1px solid var(--border-faint)',background:value}}/>
      <span style={{font:'500 14px/1 var(--font-body)',color:'var(--fg-primary)'}}>{label}</span>
    </div>
  );
}

function BrandKit() {
  const [name, setName] = useState_bk('Acme Architecture');
  return (
    <>
      <h1 className="cv-screen-title">Brand Kit</h1>

      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:48,marginBottom:36}}>
        <div className="cv-field">
          <span className="cv-field-label">Main Logo <span className="cv-info-i">i</span></span>
          <div className="cv-dropzone" style={{minHeight:160}}><div className="add">+</div></div>
        </div>
        <div className="cv-field">
          <span className="cv-field-label">Company Name</span>
          <div className="cv-help">
            This name will appear in all your hyperlinks. URL preview:<br/>
            <span style={{fontFamily:'var(--font-mono)',fontSize:13}}>https://conceptv.io/panotours/<span className="accent">{name.toLowerCase().replace(/\s+/g,'-')}</span>/projectname</span>
          </div>
          <input className="cv-input" value={name} onChange={e=>setName(e.target.value)} style={{marginTop:8}}/>
        </div>
      </div>

      <div className="cv-field" style={{marginBottom:32}}>
        <span className="cv-field-label">Additional Logos <span className="cv-info-i">i</span></span>
        <div className="cv-help muted">You can upload variations of your logo, or logos of collaborators.</div>
        <div className="cv-dropzone" style={{minHeight:140,marginTop:8}}><div className="add">+</div></div>
      </div>

      <div className="cv-panel" style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:36}}>
        <div>
          <h3 className="cv-panel-header">Colour Scheme <span className="cv-info-i">i</span></h3>
          <ColourRow value="#1F1A12" label="Menu background colour"/>
          <ColourRow value="#FFFFFF" label="Menu text colour"/>
          <ColourRow value="#D8B820" label="Button colour"/>
          <ColourRow value="#FFFFFF" label="Button text colour"/>
          <ColourRow value="#988058" label="Title colour"/>
          <ColourRow value="#A89678" label="Icon colour"/>
          <ColourRow value="#6B5F47" label="Description text colour"/>
          <div style={{display:'flex',alignItems:'center',gap:14,marginTop:14,paddingTop:14,borderTop:'1px solid rgba(31,26,18,.08)'}}>
            <span className="cv-check off"><span className="box"></span></span>
            <span style={{font:'500 13px/1 var(--font-body)',color:'var(--fg-secondary)'}}>Revert back to Default</span>
          </div>
        </div>
        <div>
          <h3 className="cv-panel-header">Preview</h3>
          <div style={{background:'var(--bg-surface)',borderRadius:'var(--r-lg)',padding:'18px 20px',boxShadow:'var(--shadow-card)'}}>
            <div style={{font:'700 22px/1 var(--font-display)',color:'var(--accent-bronze)',textAlign:'center',marginBottom:14}}>Title Text</div>
            <div style={{display:'flex',justifyContent:'space-around',gap:8,padding:'10px 0',borderTop:'1px solid var(--border-faint)',borderBottom:'1px solid var(--border-faint)',marginBottom:14}}>
              <span style={{fontSize:18,color:'var(--accent-bronze)'}}>🛏</span>
              <span style={{fontSize:18,color:'var(--accent-bronze)'}}>🛋</span>
              <span style={{fontSize:18,color:'var(--accent-bronze)'}}>🛁</span>
              <span style={{fontSize:18,color:'var(--accent-bronze)'}}>🚗</span>
            </div>
            <div style={{font:'600 11px/1.4 var(--font-body)',color:'var(--fg-primary)',textAlign:'center',marginBottom:6}}>Description text</div>
            <div style={{font:'400 11px/1.45 var(--font-body)',color:'var(--fg-secondary)',textAlign:'center',marginBottom:14}}>
              Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            </div>
            <button className="cv-btn cv-btn--primary" style={{display:'block',margin:'0 auto'}}>Button Text</button>
          </div>
        </div>
      </div>
    </>
  );
}

window.BrandKit = BrandKit;
