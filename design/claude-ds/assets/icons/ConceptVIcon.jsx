// ConceptVIcon.jsx — composable icon renderer
// ⚠️ DEPRECATED — prefer `CvIcon` (CvIcon.jsx + cv-icons.js), the single live icon home.
// This renders the legacy `window.CONCEPTV_ICONS` list (icon-paths.js) and is kept only
// for back-compat. New work: <CvIcon name="…" tone="…" shape="…"/>.
// Usage:
//   <ConceptVIcon name="search" />                       // default size 20, currentColor
//   <ConceptVIcon name="building-house" size={32} color="var(--accent-bronze)" />
//   <ConceptVIcon name="success" size={18} />            // filled status icon
//   <ConceptVIcon name="check" weight={2} />             // override stroke weight
//
// Load order in HTML:
//   <script src="path/to/icon-paths.js"></script>        // populates window.CONCEPTV_ICONS
//   <script type="text/babel" src="path/to/ConceptVIcon.jsx"></script>

function ConceptVIcon({ name, size = 20, color = 'currentColor', weight = 1.5, bg, style, ...rest }) {
  const def = window.CONCEPTV_ICONS && window.CONCEPTV_ICONS[name];
  if (!def) {
    // Unknown name — render a small placeholder square so missing icons are visible
    return (
      <svg viewBox="0 0 24 24" width={size} height={size} style={style} {...rest}>
        <rect x="3" y="3" width="18" height="18" rx="2" fill="none" stroke="currentColor" strokeWidth="1.5" strokeDasharray="2 2"/>
        <text x="6" y="14" fontSize="3" fill="currentColor">?{name}</text>
      </svg>
    );
  }
  const inner = bg ? def.body.replace(/var\(--cv-icon-bg, ?#fff\)/g, bg) : def.body;
  const wrapStyle = bg ? { ...style, ['--cv-icon-bg']: bg } : style;
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill="none"
      stroke={color}
      strokeWidth={weight}
      strokeLinecap="round"
      strokeLinejoin="round"
      style={wrapStyle}
      dangerouslySetInnerHTML={{ __html: inner }}
      {...rest}
    />
  );
}

// Convenience: a gold-circle entity badge (the iconography family 2 from the brand)
function ConceptVBadge({ name, size = 56, color = 'var(--accent-gold)', bg = 'var(--accent-gold-faint)', strokeWeight = 1.5, iconSize }) {
  const inner = iconSize ?? Math.round(size * 0.5);
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
      width: size, height: size, borderRadius: '50%',
      background: bg, border: `${strokeWeight}px solid ${color}`,
      color,
    }}>
      <ConceptVIcon name={name} size={inner} color={color}/>
    </span>
  );
}

window.ConceptVIcon = ConceptVIcon;
window.ConceptVBadge = ConceptVBadge;
