// components/Button.jsx
// ------------------------------------------------------------
// The action primitive. A thin, token-class wrapper over .cv-btn (tokens/
// controls.css) — every visual comes from the design tokens, so it themes and
// recalibrates for free. Renders <button> by default, <a> when given href.
/* global React */
const h = React.createElement;

export function Button(props) {
  const {
    variant = "primary", size, pill, block, icon,
    as, className = "", children, ...rest
  } = props || {};
  const cls = [
    "cv-btn",
    variant && variant !== "default" ? "cv-btn--" + variant : "",
    size ? "cv-btn--" + size : "",
    pill ? "cv-btn--pill" : "",
    block ? "cv-btn--block" : "",
    icon ? "cv-btn--icon" : "",
    className,
  ].filter(Boolean).join(" ");
  const Tag = as || (rest.href ? "a" : "button");
  return h(Tag, Object.assign({ className: cls }, rest), children);
}

export default Button;
