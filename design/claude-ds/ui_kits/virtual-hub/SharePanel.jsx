// SharePanel.jsx
function ShIcon({ d }) {
  return <svg className="ic" viewBox="0 0 18 18">{d.map((p,i)=><path key={i} d={p}/>)}</svg>;
}

function SharePanel({ onClose, hub }) {
  return (
    <aside className="vh-info-panel">
      <button className="vh-info-close" onClick={onClose}>✕</button>
      <h2 className="vh-info-title">Share this Hub</h2>
      <div className="vh-share-link">
        https://conceptv.io/panotours/<span className="accent">acme</span>/{hub?.id || 'tower-east'}
      </div>
      <div className="vh-share-list">
        <button className="vh-share-row">
          <ShIcon d={["M3 6 L9 11 L15 6 M3 6 V14 H15 V6 Z"]}/>
          Email
        </button>
        <button className="vh-share-row">
          <ShIcon d={["M3 9 L9 9 M9 3 L9 15","M9 9 a6 6 0 1 1 0 .01 Z"]}/>
          Copy link
        </button>
        <button className="vh-share-row">
          <ShIcon d={["M5 9 a4 4 0 0 1 8 0","M6 6 L6 12 M12 6 L12 12"]}/>
          Embed
        </button>
        <button className="vh-share-row">
          <ShIcon d={["M9 3 V12 M5 8 L9 12 L13 8","M3 14 H15"]}/>
          Download PDF brochure
        </button>
      </div>
      <p style={{font:'400 12px/1.5 var(--font-body)',color:'var(--fg-muted)',margin:0,marginTop:8}}>
        Recipients of this link will see the Hub at its current published stage.
      </p>
    </aside>
  );
}
window.SharePanel = SharePanel;
