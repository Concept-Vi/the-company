// CanvasHeader.jsx — shared canvas header
function CanvasHeader({ title, sub, actions }) {
  return (
    <div className="dsa-canvas-header">
      <div className="dsa-canvas-title-block">
        <h1 className="dsa-canvas-title">{title}</h1>
        {sub && <p className="dsa-canvas-sub">{sub}</p>}
      </div>
      {actions && <div className="dsa-canvas-actions">{actions}</div>}
    </div>
  );
}
window.CanvasHeader = CanvasHeader;
