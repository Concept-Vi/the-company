// components/Segmented.jsx — segmented control (the landing audience toggle).
// Token-class wrapper over .cv-segmented; the active option lifts onto a surface.
/* global React */
const h = React.createElement;
export function Segmented(props) {
  const { options = [], value, onChange, className = "", ...rest } = props || {};
  return h("div", Object.assign({ role: "tablist", className: ["cv-segmented", className].filter(Boolean).join(" ") }, rest),
    options.map((op, i) => {
      const id = op && typeof op === "object" ? op.value != null ? op.value : op.label : op;
      const label = op && typeof op === "object" ? op.label : op;
      const active = value != null ? value === id : i === 0;
      return h("button", {
        key: id, type: "button", role: "tab", "aria-selected": active ? "true" : "false",
        className: "cv-segmented__opt", onClick: onChange ? (e) => onChange(id, e) : undefined,
      }, label);
    }));
}
export default Segmented;
