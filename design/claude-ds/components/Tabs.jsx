// components/Tabs.jsx — data-driven tab bar (product dashboard tabs). Token-class
// wrapper over .cv-tabs/.cv-tab; the active tab carries the gold underline.
// items: [{id,label}]; controlled via `value` + `onChange`.
/* global React */
const h = React.createElement;
export function Tabs(props) {
  const { items = [], value, onChange, className = "", ...rest } = props || {};
  return h("div", Object.assign({ role: "tablist", className: ["cv-tabs", className].filter(Boolean).join(" ") }, rest),
    items.map((it, i) => {
      const id = it && typeof it === "object" ? it.id != null ? it.id : it.label : it;
      const label = it && typeof it === "object" ? it.label : it;
      const active = value != null ? value === id : i === 0;
      return h("button", {
        key: id, type: "button", role: "tab", "aria-selected": active ? "true" : "false",
        className: "cv-tab", onClick: onChange ? (e) => onChange(id, e) : undefined,
      }, label);
    }));
}
export default Tabs;
