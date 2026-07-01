// components/Badge.jsx
// ------------------------------------------------------------
// The label primitive. Token-class wrapper over .cv-badge (tokens/controls.css).
// Tones map to the system's voices/states: gold (attention), success/warning/
// error (status), comm (sage relationship). Add dot for a leading status dot.
/* global React */
const h = React.createElement;

export function Badge(props) {
  const { tone, dot, as = "span", className = "", children, ...rest } = props || {};
  const cls = [
    "cv-badge",
    tone ? "cv-badge--" + tone : "",
    dot ? "cv-badge--dot" : "",
    className,
  ].filter(Boolean).join(" ");
  return h(as, Object.assign({ className: cls }, rest), children);
}

export default Badge;
