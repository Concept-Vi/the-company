// components/Tooltip.jsx — a dark hint bubble on hover/focus. Wraps its child as
// the anchor and renders the bubble through the shared Popover engine
// (window.CV_POPOVER.Component) so positioning/flip/shift is single-sourced.
/* global React, window */
import React from "react";
const h = React.createElement;

export function Tooltip(props) {
  const { label, placement = "top", delay = 120, className = "", children, ...rest } = props || {};
  const anchorRef = React.useRef(null);
  const [open, setOpen] = React.useState(false);
  const timer = React.useRef();
  const show = () => { clearTimeout(timer.current); timer.current = setTimeout(() => setOpen(true), delay); };
  const hide = () => { clearTimeout(timer.current); setOpen(false); };
  React.useEffect(() => () => clearTimeout(timer.current), []);
  const Popover = (typeof window !== "undefined" && window.CV_POPOVER && window.CV_POPOVER.Component) || null;
  return h(React.Fragment, null,
    h("span", Object.assign({
      ref: anchorRef, className: "cv-tooltip-anchor", tabIndex: 0,
      onMouseEnter: show, onMouseLeave: hide, onFocus: show, onBlur: hide,
      "aria-describedby": undefined,
    }, rest), children),
    (open && label != null && Popover)
      ? h(Popover, { open: true, anchorRef, placement, gap: 6, bare: true, role: "tooltip" },
          h("span", { className: ["cv-tooltip", className].filter(Boolean).join(" ") }, label))
      : null);
}
export default Tooltip;
