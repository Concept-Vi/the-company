// InfoPanel.jsx
function FeatIcon({ d }) {
  return <svg viewBox="0 0 24 24">{d.map((p,i)=><path key={i} d={p}/>)}</svg>;
}

function InfoPanel({ onClose, hub }) {
  return (
    <aside className="vh-info-panel">
      <button className="vh-info-close" onClick={onClose} aria-label="Close">✕</button>
      <h2 className="vh-info-title">{hub?.title || 'Apartment A — Level 12'}</h2>
      <div className="vh-info-features">
        <div className="vh-info-feature">
          <FeatIcon d={["M3 13 V20 H21 V13","M3 13 a3 3 0 0 1 3 -3 h12 a3 3 0 0 1 3 3","M7 10 V7 a2 2 0 0 1 2 -2 h6 a2 2 0 0 1 2 2 v3"]}/>
          <span>2 BED</span>
        </div>
        <div className="vh-info-feature">
          <FeatIcon d={["M3 15 H21 V20 H3 Z","M5 15 V11 a3 3 0 0 1 3 -3 h8 a3 3 0 0 1 3 3 v4"]}/>
          <span>LIVING</span>
        </div>
        <div className="vh-info-feature">
          <FeatIcon d={["M5 11 V8 a2 2 0 0 1 2 -2 h10 a2 2 0 0 1 2 2 v3","M3 11 H21","M5 11 V19","M19 11 V19"]}/>
          <span>2 BATH</span>
        </div>
        <div className="vh-info-feature">
          <FeatIcon d={["M5 16 L7 11 H17 L19 16","M3 16 H21 V20 H3 Z","M6.5 18.5 a1 1 0 1 1 0 .01 Z M17.5 18.5 a1 1 0 1 1 0 .01 Z"]}/>
          <span>1 CAR</span>
        </div>
      </div>
      <div className="vh-info-desc">
        <h4 className="vh-info-desc-title">Description text</h4>
        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla.</p>
      </div>
      <button className="vh-info-cta">Enquire about this apartment</button>
    </aside>
  );
}
window.InfoPanel = InfoPanel;
