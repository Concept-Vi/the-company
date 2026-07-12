import React from "react";

/**
 * Glyphic — React socket around the one renderer (window.CV_GLYPHIC.compose).
 * It does NOT redraw anything: it assembles a facet-spec from props and asks the
 * single composition source for SVG + a motion class. If CV_GLYPHIC isn't loaded
 * (e.g. a bare bundle preview) it renders a labelled placeholder rather than
 * silently nothing.
 */
export function Glyphic({
  form = "circle",
  symbol = "person",
  fill = "paper",
  ringColor = "gold",
  symbolColor = "bronze",
  texture = "none",
  motion = "none",
  depth = "normal",
  size = 56,
  value,
  className = "",
  style,
  ...rest
}) {
  const spec = {
    form, symbol, fill, texture, motion, depth, size,
    color: { ring: ringColor, symbol: symbolColor },
  };
  if (value) spec.value = value;

  const GL = typeof window !== "undefined" ? window.CV_GLYPHIC : null;

  if (!GL) {
    // graceful, loud-ish fallback — never a blank
    return (
      <span
        className={`cv-glyphic cv-glyphic--unresolved ${className}`}
        title="CV_GLYPHIC not loaded — include assets/icons/cv-*.js"
        style={{
          display: "inline-flex", alignItems: "center", justifyContent: "center",
          width: size, height: size, borderRadius: 8,
          border: "2px dashed var(--accent-bronze)",
          color: "var(--accent-bronze)", font: "600 10px/1 monospace",
          ...style,
        }}
        {...rest}
      >
        {symbol}
      </span>
    );
  }

  const { svg, motionClass } = GL.compose(spec, { size });
  return (
    <span
      className={`cv-glyphic ${motionClass} ${className}`.trim()}
      style={{ display: "inline-flex", ...style }}
      dangerouslySetInnerHTML={{ __html: svg }}
      {...rest}
    />
  );
}

export default Glyphic;
