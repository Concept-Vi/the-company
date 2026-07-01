// ViStatusPill.jsx — inline pill showing Vi's current activity
function ViStatusPill({ children, live = false }) {
  return (
    <span className={`vi-status-pill ${live ? 'live' : ''}`}>
      <span className="vi-mini"><ViMark size={18} animated={live} showGlyph={false} /></span>
      <span>{children}</span>
    </span>
  );
}
window.ViStatusPill = ViStatusPill;
