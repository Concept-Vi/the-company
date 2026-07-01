// components/Switch.jsx — on/off toggle (status switch). Token-class wrapper
// over .cv-switch; track goes gold when on. Controlled via `checked`.
/* global React */
const h = React.createElement;
export function Switch(props) {
  const { checked, onChange, className = "", ...rest } = props || {};
  return h("button", Object.assign({
    type: "button", role: "switch", "aria-checked": checked ? "true" : "false",
    className: ["cv-switch", className].filter(Boolean).join(" "),
    onClick: onChange ? (e) => onChange(!checked, e) : undefined,
  }, rest));
}
export default Switch;
