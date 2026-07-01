// FloorplanOverlay.jsx
function FloorplanOverlay({ onClose, activeHub, onPick }) {
  // Coordinates are percent within the floorplan canvas
  const rooms = [
    { id: 'entry',  left: 6,  top: 65, w: 18, h: 25, label: 'Entry' },
    { id: 'living', left: 26, top: 8,  w: 36, h: 56, label: 'Living / Kitchen' },
    { id: 'bed1',   left: 26, top: 66, w: 18, h: 24, label: 'Bed 1' },
    { id: 'bath',   left: 46, top: 66, w: 16, h: 24, label: 'Bath' },
    { id: 'bed2',   left: 64, top: 8,  w: 30, h: 36, label: 'Bed 2' },
    { id: 'balcony',left: 64, top: 46, w: 30, h: 44, label: 'Balcony' },
  ];
  const dots = [
    { id: 'entry',  x: 14, y: 78 },
    { id: 'living', x: 44, y: 32 },
    { id: 'bed2',   x: 79, y: 26 },
    { id: 'balcony',x: 79, y: 68 },
  ];
  return (
    <div className="vh-floorplan" onClick={onClose}>
      <div className="vh-floorplan-card" onClick={e=>e.stopPropagation()}>
        <button className="vh-info-close" onClick={onClose} style={{top:18,right:18}}>✕</button>
        <h2 className="vh-floorplan-title">Floorplan — Apartment A</h2>
        <div className="vh-floorplan-canvas">
          {rooms.map(r => (
            <div key={r.id} className="vh-fp-room"
              style={{left:`${r.left}%`,top:`${r.top}%`,width:`${r.w}%`,height:`${r.h}%`}}>
              {r.label}
            </div>
          ))}
          {dots.map(d => (
            <button key={d.id} className={`vh-fp-dot ${activeHub === d.id ? 'active' : ''}`}
              style={{left:`${d.x}%`,top:`${d.y}%`,position:'absolute',transform:'translate(-50%,-50%)',border:'2px solid var(--bg-canvas)'}}
              onClick={() => onPick?.(d.id)}/>
          ))}
        </div>
        <p style={{font:'400 12px/1.5 var(--font-body)',color:'var(--fg-secondary)',margin:'12px 0 0',textAlign:'center'}}>
          Tap a position to jump there in the Hub.
        </p>
      </div>
    </div>
  );
}
window.FloorplanOverlay = FloorplanOverlay;
