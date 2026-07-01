// components/Input.jsx
// ------------------------------------------------------------
// The field primitive. Token-class wrapper over .cv-input / .cv-textarea /
// .cv-select (tokens/controls.css), with the gold focus ring from the source's
// composer. Pass label/hint/error to get the full .cv-field stack; omit them
// for a bare control.
/* global React */
const h = React.createElement;

export function Input(props) {
  const {
    as = "input", label, hint, error,
    id, className = "", ...rest
  } = props || {};
  const ctrlCls = (as === "textarea" ? "cv-textarea" : as === "select" ? "cv-select" : "cv-input")
    + (className ? " " + className : "");
  const control = h(as, Object.assign(
    { className: ctrlCls, id, "aria-invalid": error ? "true" : undefined },
    rest
  ));
  if (label == null && hint == null && error == null) return control;
  return h("div", { className: "cv-field" },
    label != null ? h("label", { key: "l", className: "cv-label", htmlFor: id }, label) : null,
    control,
    (error != null || hint != null)
      ? h("span", { key: "h", className: "cv-hint" + (error != null ? " cv-hint--error" : "") }, error != null ? error : hint)
      : null);
}

export default Input;
