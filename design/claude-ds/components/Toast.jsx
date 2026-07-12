// components/Toast.jsx — global notifier: a window-level queue + <ToastHost/>.
// window.CV_TOAST is the ONE queue (the CV_* global-home pattern already used
// by window.CV_POPOVER) — call CV_TOAST.show({...}) from anywhere; mount ONE
// <ToastHost/> per page to render it. Tones ride the Badge tone vocabulary
// (gold/success/warning/error/comm). Enter/exit use the tokens/motion.css
// primitives (.enter-*/.exit-*), which already gate prefers-reduced-motion;
// the JS-side removal delay additionally collapses to 0 under reduced motion
// so a dismissed toast never leaves a lingering gap.
/* global React, window */
import React from "react";
const h = React.createElement;

function reducedMotion() {
  return typeof window !== "undefined" && window.matchMedia
    && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

let _id = 0;
const _listeners = new Set();
const _queue = [];

function _emit() { _listeners.forEach((fn) => fn(_queue.slice())); }

// opts: { tone, title, message, action:{label,onClick}, duration }
// duration: ms before auto-dismiss; 0 disables auto-dismiss. Default 4200.
function show(opts) {
  opts = opts || {};
  const toast = {
    id: ++_id,
    tone: opts.tone,
    title: opts.title,
    message: opts.message,
    action: opts.action || null,
    duration: opts.duration == null ? 4200 : opts.duration,
    exiting: false,
  };
  _queue.push(toast);
  _emit();
  if (toast.duration !== 0) {
    toast._timer = setTimeout(() => dismiss(toast.id), toast.duration);
  }
  return toast.id;
}

function dismiss(id) {
  const t = _queue.find((x) => x.id === id);
  if (!t || t.exiting) return;
  clearTimeout(t._timer);
  t.exiting = true;
  _emit();
  // let the exit animation play before removing from the queue (skipped under
  // reduced motion, where the CSS transition itself already collapses to 1ms)
  setTimeout(() => {
    const i = _queue.findIndex((x) => x.id === id);
    if (i !== -1) _queue.splice(i, 1);
    _emit();
  }, reducedMotion() ? 0 : 260);
}

function subscribe(fn) { _listeners.add(fn); fn(_queue.slice()); return () => _listeners.delete(fn); }

if (typeof window !== "undefined") {
  window.CV_TOAST = window.CV_TOAST || {};
  window.CV_TOAST.show = show;
  window.CV_TOAST.dismiss = dismiss;
  window.CV_TOAST.subscribe = subscribe;
}

const ENTER = { top: "enter-down", bottom: "enter-up" };
const EXIT = { top: "exit-up", bottom: "exit-down" };

// One host per page. position = "top-right"(default) | "top-center" |
// "top-left" | "bottom-right" | "bottom-center" | "bottom-left".
export function ToastHost(props) {
  const { position = "top-right", className = "" } = props || {};
  const [items, setItems] = React.useState(() => _queue.slice());
  React.useEffect(() => subscribe(setItems), []);
  const corner = position.indexOf("bottom") === 0 ? "bottom" : "top";
  if (!items.length) return null;
  return h("div", { className: ["cv-toast-host", className].filter(Boolean).join(" "), "data-position": position },
    items.map((t) => h("div", {
      key: t.id,
      className: ["cv-toast", t.tone ? "cv-toast--" + t.tone : "", t.exiting ? EXIT[corner] : ENTER[corner]].filter(Boolean).join(" "),
      role: "status", "aria-live": "polite", "data-material": "skin",
    },
      h("span", { className: "cv-toast__dot", "aria-hidden": "true" }),
      h("div", { className: "cv-toast__body" },
        t.title != null ? h("div", { className: "cv-toast__title" }, t.title) : null,
        t.message != null ? h("div", { className: "cv-toast__msg" }, t.message) : null),
      t.action ? h("button", {
        type: "button", className: "cv-toast__action",
        onClick: () => { if (t.action.onClick) t.action.onClick(); dismiss(t.id); },
      }, t.action.label) : null,
      h("button", { type: "button", className: "cv-toast__close", "aria-label": "Dismiss", onClick: () => dismiss(t.id) }, "×"))));
}

export default ToastHost;
