// components/Sheet.jsx — mobile-first slide-in panel, the touch sibling of
// Modal. Shares Modal's overlay/backdrop/Escape/close-button conventions
// (reuses .cv-modal__head/__title/__close/__foot — one home for dialog
// chrome, never a second). side="right" (a desktop-leaning drawer) |
// "bottom" (a mobile sheet, carries a --touch-min-guarded drag handle).
// Controlled via `open`; stays mounted through the exit transition so the
// slide-out is a motion, never a teleport.
/* global React */
import React from "react";
const h = React.createElement;

function reducedMotion() {
  return typeof window !== "undefined" && window.matchMedia
    && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export function Sheet(props) {
  const { open, onClose, side = "bottom", title, footer, className = "", children, ...rest } = props || {};
  const [mounted, setMounted] = React.useState(!!open);
  const [entered, setEntered] = React.useState(false);
  const closeTimer = React.useRef();

  React.useEffect(() => {
    if (open) {
      clearTimeout(closeTimer.current);
      setMounted(true);
      const raf = requestAnimationFrame(() => setEntered(true));
      return () => cancelAnimationFrame(raf);
    }
    setEntered(false);
    closeTimer.current = setTimeout(() => setMounted(false), reducedMotion() ? 0 : 260);
    return () => clearTimeout(closeTimer.current);
  }, [open]);

  React.useEffect(() => {
    if (!mounted || !onClose) return undefined;
    const onKey = (e) => { if (e.key === "Escape") onClose(); };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [mounted, onClose]);

  if (!mounted) return null;
  return h("div", { className: "cv-sheet-overlay", onClick: onClose ? (e) => { if (e.target === e.currentTarget) onClose(); } : undefined },
    h("div", Object.assign({
      className: ["cv-sheet", entered ? "is-open" : "", !open ? "is-closing" : "", className].filter(Boolean).join(" "),
      "data-side": side, role: "dialog", "aria-modal": "true", "data-material": "skin",
    }, rest),
      side === "bottom" ? h("div", { className: "cv-sheet__handle-hit" }, h("span", { className: "cv-sheet__handle", "aria-hidden": "true" })) : null,
      (title != null || onClose) ? h("div", { className: "cv-modal__head" },
        title != null ? h("h2", { className: "cv-modal__title" }, title) : h("span", { style: { flex: 1 } }),
        onClose ? h("button", { className: "cv-modal__close", "aria-label": "Close", onClick: onClose }, "×") : null) : null,
      h("div", null, children),
      footer != null ? h("div", { className: "cv-modal__foot" }, footer) : null));
}
export default Sheet;
