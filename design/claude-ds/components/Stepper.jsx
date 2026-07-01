// components/Stepper.jsx — linear numbered progress indicator. Token-class
// wrapper over .cv-stepper-line/.cv-step. steps: string[] | {label}[]; `active`
// = current index (steps before it render done, with gold dots).
/* global React */
const h = React.createElement;
export function Stepper(props) {
  const { steps = [], active = 0, className = "", ...rest } = props || {};
  return h("div", Object.assign({ className: ["cv-stepper-line", className].filter(Boolean).join(" ") }, rest),
    steps.map((s, i) => {
      const label = s && typeof s === "object" ? s.label : s;
      const state = i < active ? "is-done" : i === active ? "is-active" : "";
      return h("div", { key: i, className: ["cv-step", state].filter(Boolean).join(" ") },
        h("span", { className: "cv-step__dot" }, i < active ? "✓" : String(i + 1)),
        h("span", { className: "cv-step__label" }, label));
    }));
}
export default Stepper;
