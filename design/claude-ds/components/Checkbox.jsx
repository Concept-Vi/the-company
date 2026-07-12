// components/Checkbox.jsx — token-styled checkbox (gold = the selection/
// decision colour-discipline rule). Native input restyled via .cv-checkbox;
// label+hint ride the SAME .cv-field/.cv-label/.cv-hint stack as Input —
// never a second labelled-field convention.
/* global React */
import React from "react";
const h = React.createElement;

export function Checkbox(props) {
  const { label, hint, error, id, indeterminate, className = "", ...rest } = props || {};
  const ref = React.useRef(null);
  React.useEffect(() => { if (ref.current) ref.current.indeterminate = !!indeterminate; }, [indeterminate]);
  const control = h("input", Object.assign({
    ref, type: "checkbox", id,
    className: ["cv-checkbox", className].filter(Boolean).join(" "),
    "aria-invalid": error ? "true" : undefined,
  }, rest));
  if (label == null && hint == null && error == null) return control;
  return h("div", { className: "cv-field" },
    h("span", { className: "cv-check-row" }, control, label != null ? h("label", { className: "cv-label", htmlFor: id }, label) : null),
    (error != null || hint != null)
      ? h("span", { className: "cv-hint" + (error != null ? " cv-hint--error" : "") }, error != null ? error : hint)
      : null);
}
export default Checkbox;
