// components/Menu.jsx — action menu riding the shared Popover engine
// (window.CV_POPOVER.Component — the ONE floating-layer implementation;
// Menu adds no second positioning system). `trigger` is cloned with the
// anchor ref + open toggle. items = [{icon,label,danger,disabled,onSelect}]
// or {separator:true}. Keyboard: arrow keys move focus, Enter/Space select,
// Escape/outside-click close (already handled by Popover). role="menu".
/* global React, window */
import React from "react";
const h = React.createElement;

export function Menu(props) {
  const { trigger, items = [], placement = "bottom-start", className = "", onOpenChange } = props || {};
  const anchorRef = React.useRef(null);
  const [open, setOpen] = React.useState(false);
  const [focusIdx, setFocusIdx] = React.useState(-1);
  const selectable = items.map((it, i) => ((it && it.separator) ? -1 : i)).filter((i) => i !== -1);

  const setOpenState = (next) => {
    setOpen(next);
    if (onOpenChange) onOpenChange(next);
    if (!next) setFocusIdx(-1);
  };
  const close = () => setOpenState(false);

  const CvIcon = (typeof window !== "undefined" && window.CvIcon) || null;
  const Popover = (typeof window !== "undefined" && window.CV_POPOVER && window.CV_POPOVER.Component) || null;

  const onKeyDown = (e) => {
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      if (!selectable.length) return;
      const dir = e.key === "ArrowDown" ? 1 : -1;
      const cur = selectable.indexOf(focusIdx);
      const next = selectable[(cur + dir + selectable.length) % selectable.length];
      setFocusIdx(next);
    } else if (e.key === "Enter" || e.key === " ") {
      if (focusIdx === -1) return;
      e.preventDefault();
      const it = items[focusIdx];
      if (it && !it.disabled && it.onSelect) { it.onSelect(); close(); }
    } else if (e.key === "Home") { e.preventDefault(); if (selectable.length) setFocusIdx(selectable[0]); }
    else if (e.key === "End") { e.preventDefault(); if (selectable.length) setFocusIdx(selectable[selectable.length - 1]); }
  };

  const triggerEl = trigger ? React.cloneElement(trigger, {
    ref: anchorRef,
    "aria-haspopup": "menu",
    "aria-expanded": open ? "true" : "false",
    onClick: (e) => { if (trigger.props.onClick) trigger.props.onClick(e); setOpenState(!open); },
  }) : null;

  return h(React.Fragment, null,
    triggerEl,
    (open && Popover) ? h(Popover, { open: true, anchorRef, placement, gap: 6, onRequestClose: close },
      h("div", { className: ["cv-menu", className].filter(Boolean).join(" "), role: "menu", onKeyDown },
        items.map((it, i) => {
          if (it && it.separator) return h("div", { key: "sep" + i, className: "cv-menu__sep", role: "separator" });
          const icon = (it.icon && CvIcon) ? h(CvIcon, { name: it.icon, size: 16 }) : null;
          return h("button", {
            key: it.value != null ? it.value : i, type: "button", role: "menuitem", tabIndex: -1,
            className: ["cv-menu__item", it.danger ? "cv-menu__item--danger" : "", i === focusIdx ? "is-focused" : ""].filter(Boolean).join(" "),
            "aria-disabled": it.disabled ? "true" : undefined,
            onMouseEnter: () => setFocusIdx(i),
            onClick: it.disabled ? undefined : () => { if (it.onSelect) it.onSelect(); close(); },
          }, icon, h("span", { className: "cv-menu__label" }, it.label));
        }))) : null);
}
export default Menu;
