/**
 * CvIcon.jsx — React renderer for the ConceptV icon library.
 *
 * Loads cv-icons.js (which puts window.CV_ICONS on the page) and exposes
 * a single component that renders any icon, optionally wrapped in the
 * brand's gold-circle entity-badge treatment.
 *
 * Usage:
 *   <CvIcon name="house" />                          // 24×24, bronze, line style
 *   <CvIcon name="house" size={32} />                // larger
 *   <CvIcon name="house" tone="gold" />              // gold stroke
 *   <CvIcon name="house" tone="ink" />               // dark stroke
 *   <CvIcon name="house" circle />                   // wrapped in gold ring (= shape="circle")
 *   <CvIcon name="property" shape="hex" tone="gold" />   // Property-Wizard hexagon node
 *   <CvIcon name="info" shape="octagon" />               // Virtual-Hub octagon node
 *   <CvIcon name="check" shape="diamond" tone="gold" />  // Vi diamond node
 *   <CvIcon name="house" circle filled />            // filled badge, ink glyph
 *   <CvIcon name="house" desaturated={0.4} />        // for state-strength gradients
 *
 * Stroke weight auto-scales toward the brand's bolder ~1.9px at display
 * sizes and stays crisp (~1.55px) for small UI chrome; pass strokeWidth to pin it.
 * Names resolve through CV_ICONS aliases, so semantic + brand names both work
 * (e.g. "square-meters" === "m2", "settings" === "gear", "price" === "dollar-circle").
 */

const CV_TONES = {
  bronze: 'var(--accent-bronze)',   // #988058 — default illustration tone
  gold:   'var(--accent-gold)',     // #E0C010 — entity badges, emphasis
  ink:    'var(--fg-primary)',      // #1F1A12 — UI chrome
  muted:  'var(--fg-muted)',        // #A89678 — disabled / inactive
  cream:  'var(--bg-canvas)',       // #FBF7EC — on-dark surfaces
};

// Brand entity-node container shapes (100×100 polygon points).
//  circle  = User Portal · hex = Property Wizard · octagon = Virtual Hub · diamond = Vi
//  CANONICAL SOURCE: assets/icons/cv-shapes.js (window.CV_SHAPES). The literal below
//  is a byte-identical FALLBACK for when that module hasn't loaded (keep them in sync).
const CV_SHAPE_PTS = (typeof window !== 'undefined' && window.CV_SHAPES && window.CV_SHAPES.points())
  || {
  hex:     '25,8 75,8 98,50 75,92 25,92 2,50',
  octagon: '30,4 70,4 96,30 96,70 70,96 30,96 4,70 4,30',
  diamond: '50,3 97,50 50,97 3,50',
};

// Brand stroke weight: bolder at display size, crisp for small UI chrome.
function cvBrandStroke(size) {
  return Math.max(1.55, Math.min(2, 1.5 + (size - 16) * 0.025));
}

function CvIcon({
  name,
  size = 24,
  tone = 'bronze',
  strokeWidth,
  circle = false,
  shape,
  filled = false,
  desaturated = 0,
  className = '',
  style = {},
  title,
  ...rest
}) {
  const resolve = window.CV_ICONS && window.CV_ICONS.get;
  const body = resolve ? resolve(name) : (window.CV_ICONS && window.CV_ICONS.data && window.CV_ICONS.data[name]);
  const sw = strokeWidth != null ? strokeWidth : cvBrandStroke(size);
  const containerShape = shape || (circle ? 'circle' : null);
  if (!body) {
    return (
      <span
        className={`cv-icon cv-icon--missing ${className}`}
        title={`Missing icon: ${name}`}
        style={{
          display: 'inline-flex',
          alignItems: 'center', justifyContent: 'center',
          width: size, height: size,
          border: '1px dashed var(--status-error)',
          color: 'var(--status-error)',
          font: `600 ${Math.round(size*0.35)}px var(--font-mono)`,
          borderRadius: 4,
          ...style,
        }}>?</span>
    );
  }

  const strokeColor = CV_TONES[tone] || tone;
  const opacity = desaturated ? Math.max(0.15, 1 - desaturated) : 1;

  if (containerShape && containerShape !== 'circle') {
    // Polygon node shapes (hex / octagon / diamond) — drawn as an SVG behind a centred glyph.
    const inner = Math.round(size * 0.5);
    const ringFill = filled ? strokeColor : 'transparent';
    const innerStroke = filled ? 'var(--fg-primary)' : strokeColor;
    const pts = CV_SHAPE_PTS[containerShape] || CV_SHAPE_PTS.hex;
    return (
      <span
        className={`cv-icon cv-icon--${containerShape} ${className}`}
        style={{
          position: 'relative', display: 'inline-flex',
          alignItems: 'center', justifyContent: 'center',
          width: size, height: size, opacity, color: innerStroke, flex: 'none', ...style,
        }}
        title={title || name}
        {...rest}>
        <svg viewBox="0 0 100 100" width={size} height={size}
          style={{ position: 'absolute', inset: 0 }}
          fill={ringFill} stroke={strokeColor} strokeWidth={7} strokeLinejoin="round">
          <polygon points={pts}/>
        </svg>
        <svg viewBox="0 0 24 24" width={inner} height={inner}
          style={{ position: 'relative' }}
          fill="none" stroke="currentColor"
          strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"
          dangerouslySetInnerHTML={{ __html: body }}
        />
      </span>
    );
  }

  if (containerShape === 'circle') {
    // The gold-ring entity-badge wrapper. The ring colour follows the tone.
    const ringSize = size;
    const inner = Math.round(size * 0.58);
    const ringStroke = Math.max(1.25, size * 0.06);
    const ringFill = filled ? strokeColor : 'transparent';
    const innerStroke = filled ? 'var(--fg-primary)' : strokeColor;
    return (
      <span
        className={`cv-icon cv-icon--circle ${className}`}
        style={{
          display: 'inline-flex',
          alignItems: 'center', justifyContent: 'center',
          width: ringSize, height: ringSize,
          borderRadius: '50%',
          border: `${ringStroke}px solid ${strokeColor}`,
          background: ringFill,
          opacity,
          color: innerStroke,
          flex: 'none',
          ...style,
        }}
        title={title || name}
        {...rest}>
        <svg
          viewBox="0 0 24 24" width={inner} height={inner}
          fill="none" stroke="currentColor"
          strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round"
          dangerouslySetInnerHTML={{ __html: body }}
        />
      </span>
    );
  }

  // Plain icon
  return (
    <svg
      className={`cv-icon ${className}`}
      viewBox="0 0 24 24"
      width={size} height={size}
      fill="none" stroke={strokeColor}
      strokeWidth={sw}
      strokeLinecap="round" strokeLinejoin="round"
      style={{ display: 'inline-block', verticalAlign: 'middle', flex: 'none', opacity, ...style }}
      role={title ? 'img' : undefined}
      aria-label={title}
      {...rest}
      dangerouslySetInnerHTML={{ __html: body }}
    />
  );
}

window.CvIcon = CvIcon;
window.CV_TONES = CV_TONES;
