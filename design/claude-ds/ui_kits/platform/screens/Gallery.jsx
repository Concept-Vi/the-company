// screens/Gallery.jsx
const { useState: useState_g } = React;

function MediaTile({ selected, video, onClick }) {
  return (
    <div className={`cv-tile ${selected ? 'selected' : ''} ${video ? 'cv-tile--video' : ''}`} onClick={onClick}>
      {video && <div className="cv-play"><svg viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="10" fill="rgba(31,26,18,.08)"/><path d="M10 8 L17 12 L10 16 Z" fill="currentColor"/></svg></div>}
    </div>
  );
}

function Gallery() {
  const [sel, setSel] = useState_g(new Set([0, 6, 8]));
  const [view, setView] = useState_g('grid');
  const toggle = (i) => {
    const s = new Set(sel);
    s.has(i) ? s.delete(i) : s.add(i);
    setSel(s);
  };
  return (
    <>
      <h1 className="cv-screen-title">Gallery</h1>
      <ActionToolbar showSelect showCreate showUpload search="" onSearch={()=>{}} />
      <div className="cv-section-divider">
        <h3>Images</h3>
        <div className="cv-view-toggle" style={{marginLeft:'auto'}}>
          <button className={view==='grid'?'active':''} onClick={()=>setView('grid')} aria-label="Grid">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.5"><rect x="2" y="2" width="4" height="4"/><rect x="8" y="2" width="4" height="4"/><rect x="2" y="8" width="4" height="4"/><rect x="8" y="8" width="4" height="4"/></svg>
          </button>
          <button className={view==='list'?'active':''} onClick={()=>setView('list')} aria-label="List">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"><path d="M2 4 H12 M2 7 H12 M2 10 H12"/></svg>
          </button>
        </div>
      </div>
      <div className="cv-tile-grid">
        {Array.from({length: 15}).map((_, i) => (
          <MediaTile key={i} selected={sel.has(i)} onClick={() => toggle(i)} />
        ))}
      </div>
      <div className="cv-section-divider" style={{marginTop: 36}}>
        <h3>Videos</h3>
        <span className="link">View All</span>
      </div>
      <div className="cv-tile-grid">
        {Array.from({length: 5}).map((_, i) => <MediaTile key={i} video />)}
      </div>
    </>
  );
}

window.Gallery = Gallery;
