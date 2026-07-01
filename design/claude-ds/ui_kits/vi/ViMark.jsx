// ViMark.jsx — the Vi diamond avatar
function ViMark({ size = 32, animated = false, showGlyph = true }) {
  const id = `vi-pat-${Math.random().toString(36).slice(2, 7)}`;
  return (
    <div className="vi-mark" style={{ width: size, height: size, position: 'relative', fontSize: size * 0.42 }}>
      <svg viewBox="0 0 100 100">
        <defs>
          <pattern id={id} patternUnits="userSpaceOnUse" width="6" height="6">
            <line x1="0" y1="0" x2="6" y2="0" stroke="#E0C010" strokeWidth="0.7" opacity={animated ? 0.55 : 0.35}>
              {animated && <animate attributeName="opacity" values="0.2;0.7;0.2" dur="1.6s" repeatCount="indefinite"/>}
            </line>
          </pattern>
        </defs>
        <polygon points="50,8 92,50 50,92 8,50" fill="#fff" stroke="#E0C010" strokeWidth="2"/>
        <polygon points="50,8 92,50 50,92 8,50" fill={`url(#${id})`}/>
      </svg>
      {showGlyph && (
        <span className="glyph">V<span className="i" style={{ fontSize: '0.62em' }}>i</span></span>
      )}
    </div>
  );
}
window.ViMark = ViMark;
