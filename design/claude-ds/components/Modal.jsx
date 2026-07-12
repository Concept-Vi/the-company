// components/Modal.jsx — overlay + panel dialog. Token-class wrapper over
// .cv-modal-overlay/.cv-modal. Controlled via `open`; closes on backdrop click,
// Escape, or the close button. Renders nothing when closed.
/* global React */
const h = React.createElement;
export function Modal(props) {
  const { open, onClose, title, footer, className = "", children, ...rest } = props || {};
  React.useEffect(() => {
    if (!open || !onClose) return undefined;
    const onKey = (e) => { if (e.key === "Escape") onClose(); };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onClose]);
  if (!open) return null;
  return h("div", { className: "cv-modal-overlay", onClick: onClose ? (e) => { if (e.target === e.currentTarget) onClose(); } : undefined },
    h("div", Object.assign({ className: ["cv-modal", className].filter(Boolean).join(" "), role: "dialog", "aria-modal": "true", "data-material": "skin" }, rest),
      (title != null || onClose) ? h("div", { className: "cv-modal__head" },
        title != null ? h("h2", { className: "cv-modal__title" }, title) : h("span", { style: { flex: 1 } }),
        onClose ? h("button", { className: "cv-modal__close", "aria-label": "Close", onClick: onClose }, "\u00D7") : null) : null,
      h("div", null, children),
      footer != null ? h("div", { className: "cv-modal__foot" }, footer) : null));
}
export default Modal;
