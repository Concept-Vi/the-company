// components/Popover.jsx — the shared anchored floating layer (the ONE home for
// popover positioning). Tooltip and Select both render through this; the pure
// placement math is also published as `window.CV_POPOVER.place` so any consumer
// gets the same flip/shift behaviour without importing across modules.
/* global React, window, document */
import React from "react";
const h = React.createElement;

// Pure positioning: place `float` (a position:fixed element) against `anchor`,
// flipping side when there isn't room and shifting to stay in the viewport.
// Returns the resolved side ("top"|"bottom"|"left"|"right").
function placePopover(anchor, float, opts) {
  opts = opts || {};
  const gap = opts.gap == null ? 6 : opts.gap;
  const pad = 8;
  const ar = anchor.getBoundingClientRect();
  const fw = float.offsetWidth, fh = float.offsetHeight;
  const vw = window.innerWidth, vh = window.innerHeight;
  const parts = (opts.placement || "bottom-start").split("-");
  let side = parts[0]; const align = parts[1] || "start";
  if (opts.flip !== false) {
    if (side === "bottom" && ar.bottom + gap + fh > vh - pad && ar.top - gap - fh > pad) side = "top";
    else if (side === "top" && ar.top - gap - fh < pad && ar.bottom + gap + fh < vh - pad) side = "bottom";
    else if (side === "right" && ar.right + gap + fw > vw - pad && ar.left - gap - fw > pad) side = "left";
    else if (side === "left" && ar.left - gap - fw < pad && ar.right + gap + fw < vw - pad) side = "right";
  }
  let top, left;
  if (side === "bottom") top = ar.bottom + gap;
  else if (side === "top") top = ar.top - gap - fh;
  else top = ar.top;
  if (side === "left") left = ar.left - gap - fw;
  else if (side === "right") left = ar.right + gap;
  else if (align === "center") left = ar.left + ar.width / 2 - fw / 2;
  else if (align === "end") left = ar.right - fw;
  else left = ar.left;
  if (side === "left" || side === "right") {
    if (align === "center") top = ar.top + ar.height / 2 - fh / 2;
    else if (align === "end") top = ar.bottom - fh;
  }
  if (opts.shift !== false) {
    left = Math.max(pad, Math.min(left, vw - pad - fw));
    top = Math.max(pad, Math.min(top, vh - pad - fh));
  }
  float.style.position = "fixed";
  float.style.top = Math.round(top) + "px";
  float.style.left = Math.round(left) + "px";
  return side;
}

// Controlled floating layer. Give it an `anchorRef` (ref to the trigger) and
// `open`; it positions on open and repositions on scroll/resize, closes on
// outside-click / Escape via `onRequestClose`. `bare` drops the surface chrome.
export function Popover(props) {
  const { open, anchorRef, placement = "bottom-start", gap, matchWidth, bare,
    role, className = "", children, onRequestClose, ...rest } = props || {};
  const ref = React.useRef(null);
  const [side, setSide] = React.useState((placement || "bottom").split("-")[0]);

  React.useLayoutEffect(() => {
    if (!open) return undefined;
    const float = ref.current, anchor = anchorRef && anchorRef.current;
    if (!float || !anchor) return undefined;
    if (matchWidth) float.style.minWidth = anchor.offsetWidth + "px";
    const reposition = () => { setSide(placePopover(anchor, float, { placement, gap })); };
    reposition();
    const raf = requestAnimationFrame(() => { if (ref.current) ref.current.classList.add("is-open"); });
    window.addEventListener("scroll", reposition, true);
    window.addEventListener("resize", reposition);
    return () => { cancelAnimationFrame(raf); window.removeEventListener("scroll", reposition, true); window.removeEventListener("resize", reposition); };
  }, [open, placement, gap, matchWidth, anchorRef]);

  React.useEffect(() => {
    if (!open || !onRequestClose) return undefined;
    const onDoc = (e) => {
      const float = ref.current, anchor = anchorRef && anchorRef.current;
      if (float && float.contains(e.target)) return;
      if (anchor && anchor.contains(e.target)) return;
      onRequestClose();
    };
    const onKey = (e) => { if (e.key === "Escape") onRequestClose(); };
    document.addEventListener("mousedown", onDoc);
    document.addEventListener("keydown", onKey);
    return () => { document.removeEventListener("mousedown", onDoc); document.removeEventListener("keydown", onKey); };
  }, [open, onRequestClose, anchorRef]);

  if (!open) return null;
  const base = bare ? "cv-pop-bare" : "cv-popover";
  return h("div", Object.assign({ ref, className: [base, className].filter(Boolean).join(" "), "data-placement": side, role, "data-material": "skin" }, rest), children);
}

// Publish the placement engine as the single global home (the CV_* pattern), so
// other components reference ONE implementation without cross-module imports.
if (typeof window !== "undefined") {
  window.CV_POPOVER = window.CV_POPOVER || {};
  window.CV_POPOVER.place = placePopover;
  window.CV_POPOVER.Component = Popover;
}

export default Popover;
