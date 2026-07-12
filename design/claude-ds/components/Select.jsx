// components/Select.jsx — a trigger that reads like an Input, opening a listbox
// through the shared Popover engine (window.CV_POPOVER.Component). Controlled via
// value/onChange. Options are strings or { value, label, disabled }.
/* global React, window */
import React from "react";
const h = React.createElement;

export function Select(props) {
  const { options = [], value, onChange, placeholder = "Select\u2026", disabled, className = "", ...rest } = props || {};
  const anchorRef = React.useRef(null);
  const [open, setOpen] = React.useState(false);
  const norm = (options || []).map((o) => (o && typeof o === "object") ? o : { value: o, label: o });
  const current = norm.find((o) => o.value === value);
  const Popover = (typeof window !== "undefined" && window.CV_POPOVER && window.CV_POPOVER.Component) || null;
  return h("div", Object.assign({ className: ["cv-select", className].filter(Boolean).join(" ") }, rest),
    h("button", {
      ref: anchorRef, type: "button", className: "cv-select__btn",
      "aria-haspopup": "listbox", "aria-expanded": open ? "true" : "false", disabled,
      onClick: () => setOpen((o) => !o),
    },
      h("span", { className: ["cv-select__value", current ? "" : "is-placeholder"].filter(Boolean).join(" ") }, current ? current.label : placeholder),
      h("span", { className: "cv-select__caret", "aria-hidden": "true" }, "\u25BE")),
    (open && Popover) ? h(Popover, {
      open: true, anchorRef, placement: "bottom-start", gap: 6, matchWidth: true,
      role: "listbox", onRequestClose: () => setOpen(false),
    },
      h("div", { className: "cv-select__menu" }, norm.map((o) =>
        h("button", {
          key: String(o.value), type: "button", role: "option",
          className: ["cv-select__opt", o.value === value ? "is-active" : ""].filter(Boolean).join(" "),
          "aria-selected": o.value === value ? "true" : "false",
          "aria-disabled": o.disabled ? "true" : undefined,
          onClick: o.disabled ? undefined : (e) => { if (onChange) onChange(o.value, e); setOpen(false); },
        }, o.label)))) : null);
}
export default Select;
