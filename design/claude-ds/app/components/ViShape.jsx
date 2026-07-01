// ViShape.jsx — the Vi diamond mark, reusable as logo / chip / button glyph
function ViShape({ size = 16, animated = false, color = 'var(--accent-gold)' }) {
  const id = `vsh-${Math.random().toString(36).slice(2, 7)}`;
  return (
    <span className="vi-shape" style={{ width: size, height: size, position: 'relative' }}>
      <svg viewBox="0 0 24 24">
        <defs>
          <pattern id={id} patternUnits="userSpaceOnUse" width="3" height="3">
            <line x1="0" y1="0" x2="3" y2="0" stroke={color} strokeWidth="0.4" opacity={animated ? 0.6 : 0.3}>
              {animated && <animate attributeName="opacity" values="0.2;0.7;0.2" dur="1.6s" repeatCount="indefinite"/>}
            </line>
          </pattern>
        </defs>
        <polygon points="12,2 22,12 12,22 2,12" fill="white" stroke={color} strokeWidth="1.5" strokeLinejoin="round"/>
        <polygon points="12,2 22,12 12,22 2,12" fill={`url(#${id})`}/>
      </svg>
    </span>
  );
}
window.ViShape = ViShape;
