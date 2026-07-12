// components/AppShell.jsx — the console chrome: a desktop nav rail that
// becomes a bottom tab bar on mobile. RIDES tokens/device.css's existing
// .cv-appbar/.cv-tabbar CSS verbatim (never a hand-rolled phone chrome —
// the DESIGN-LANGUAGE law); the rail is the only genuinely new chrome,
// since device.css only ever covered the phone. Surface switching is the
// [data-surface]/@media machinery declared alongside .cv-appshell in
// tokens/controls.css. Slots: header (or a plain title), nav items, content.
/* global React, window */
import React from "react";
const h = React.createElement;

function navIcon(name) {
  const CvIcon = (typeof window !== "undefined" && window.CvIcon) || null;
  return (name && CvIcon) ? h(CvIcon, { name, size: 20 }) : null;
}

export function AppShell(props) {
  const { nav = [], activeId, onNavigate, header, title, className = "", children, ...rest } = props || {};
  const headerEl = header !== undefined
    ? header
    : (title != null ? h("div", { className: "cv-appbar" }, h("span", { className: "cv-appbar__title" }, title)) : null);

  return h("div", Object.assign({ className: ["cv-appshell", className].filter(Boolean).join(" ") }, rest),
    headerEl,
    h("div", { className: "cv-appshell__body" },
      nav.length ? h("nav", { className: "cv-appshell__rail", "aria-label": "Primary" },
        nav.map((it) => h("button", {
          key: it.id, type: "button", className: "cv-rail-item",
          "aria-current": it.id === activeId ? "page" : undefined,
          onClick: onNavigate ? () => onNavigate(it.id) : undefined,
        },
          it.icon ? h("span", { className: "cv-rail-item__icon" }, navIcon(it.icon)) : null,
          h("span", { className: "truncate" }, it.label)))) : null,
      h("div", { className: "cv-appshell__content" },
        h("div", { className: "cv-appshell__scroll" }, children))),
    nav.length ? h("nav", { className: "cv-tabbar cv-appshell__tabbar", "aria-label": "Primary" },
      nav.map((it) => h("button", {
        key: it.id, type: "button", className: "cv-tab", "aria-selected": it.id === activeId ? "true" : "false",
        onClick: onNavigate ? () => onNavigate(it.id) : undefined,
      },
        it.icon ? navIcon(it.icon) : null,
        h("span", null, it.label)))) : null);
}
export default AppShell;
