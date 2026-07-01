// screens/HubSettings.jsx
const { useState: useState_hs } = React;

function HubSettings() {
  const initial = {
    info: true, share: true, floorplan: true, renders: false, map: false, gyro: true, vr: false,
    arrows: false, hideNav: false, quickNav: false, filter: false, applyAll: true,
    addStyle: false, addStages: false, addHub: true, entry: true, aptA: true, aptB: true,
  };
  const [s, setS] = useState_hs(initial);
  const toggle = k => setS({...s, [k]: !s[k]});

  const Check = ({k, label, link}) => (
    <div className={`cv-check ${!s[k] ? 'off' : ''}`} onClick={() => toggle(k)}>
      <span className="box"></span>
      {link ? <a className="link">{label}</a> : <span>{label}</span>}
    </div>
  );

  return (
    <>
      <h1 className="cv-screen-title">Virtual Hub Settings</h1>

      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:48,marginBottom:32}}>
        <div className="cv-field">
          <span className="cv-field-label">Hub Name <span className="cv-info-i">i</span></span>
          <input className="cv-input" defaultValue="Tower East — Stage 1"/>
          <div className="cv-help">URL preview:<br/>
            <span style={{fontFamily:'var(--font-mono)',fontSize:13}}>
              https://conceptv.io/panotours/<span className="accent">acme</span>/<span className="accent">tower-east</span> 🔒
            </span>
          </div>
        </div>
        <div className="cv-field">
          <span className="cv-field-label">Meta Description <span className="cv-info-i">i</span></span>
          <textarea className="cv-input" rows="4" style={{resize:'none',fontFamily:'var(--font-body)',color:'var(--fg-muted)'}} defaultValue="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris."/>
        </div>
      </div>

      <div className="cv-panel" style={{marginBottom:24}}>
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr 1fr',gap:24}}>
          <div>
            <h3 className="cv-panel-header">Menu Options › <span className="cv-info-i">i</span></h3>
            <div style={{font:'400 12px/1.4 var(--font-body)',color:'var(--fg-secondary)',marginBottom:10}}>Double click to see a Preview.</div>
            <Check k="info" label="Information Panel"/>
            <Check k="share" label="Share Panel"/>
            <Check k="floorplan" label="Floorplan" link/>
            <Check k="renders" label="Renders & Videos"/>
            <Check k="map" label="Map"/>
            <Check k="gyro" label="Gyroscope"/>
            <Check k="vr" label="VR Mode"/>
          </div>
          <div>
            <h3 className="cv-panel-header">Navigation Options <span className="cv-info-i">i</span></h3>
            <div style={{font:'400 12px/1.4 var(--font-body)',color:'var(--fg-secondary)',marginBottom:10}}>&nbsp;</div>
            <Check k="arrows" label="Show turning arrows"/>
            <Check k="hideNav" label="Show Hide Navigation option"/>
            <Check k="quickNav" label="Show Quick Navigation menu"/>
            <Check k="filter" label="Show filter options"/>
            <Check k="applyAll" label="Apply to all Hubs in this Project"/>
          </div>
          <div style={{background:'var(--bg-sunken)',borderRadius:'var(--r-md)',minHeight:180,display:'flex',alignItems:'center',justifyContent:'center',color:'var(--accent-bronze)'}}>
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="24" cy="24" r="20"/><path d="M19 16 L33 24 L19 32 Z" fill="currentColor"/></svg>
          </div>
        </div>
      </div>

      <div className="cv-panel">
        <h3 className="cv-panel-header">Link Hubs › <span className="cv-info-i">i</span></h3>
        <div style={{font:'400 13px/1.55 var(--font-body)',color:'var(--fg-secondary)',marginBottom:14,maxWidth:540}}>
          Showcase variations in design, revision stages, and allow users to quickly switch between different Hubs. Double click to see a Preview.
        </div>
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr 1fr',gap:24}}>
          <div>
            <Check k="addStyle" label="Add Style Switch"/>
            <Check k="addStages" label="Add Project Stages"/>
          </div>
          <div>
            <Check k="addHub" label="Add Hub Switch"/>
            <div style={{paddingLeft:32,marginTop:6}}>
              <Check k="entry" label="Entry"/>
              <Check k="aptA" label="Apartment A"/>
              <Check k="aptB" label="Apartment B"/>
            </div>
          </div>
          <div style={{background:'var(--bg-sunken)',borderRadius:'var(--r-md)',minHeight:160,display:'flex',alignItems:'center',justifyContent:'center',color:'var(--accent-bronze)'}}>
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="24" cy="24" r="20"/><path d="M19 16 L33 24 L19 32 Z" fill="currentColor"/></svg>
          </div>
        </div>
      </div>
    </>
  );
}

window.HubSettings = HubSettings;
