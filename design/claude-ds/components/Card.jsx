// components/Card.jsx
// ------------------------------------------------------------
// The container primitive. A token-class wrapper over .cv-card (tokens/
// controls.css): soft cream deck panel, white content card, outline, gold, or
// raised. Optional title/sub header and footer; children are the body.
/* global React */
const h = React.createElement;

export function Card(props) {
  const {
    variant, raised, interactive, pad,
    title, sub, footer,
    as = "div", className = "", children, ...rest
  } = props || {};
  const cls = [
    "cv-card",
    variant ? "cv-card--" + variant : "",
    raised ? "cv-card--raised" : "",
    interactive ? "cv-card--interactive" : "",
    pad ? "cv-card--pad-" + pad : "",
    className,
  ].filter(Boolean).join(" ");
  const header = (title != null || sub != null)
    ? h("div", { key: "h", className: "cv-card__head", style: { flexDirection: "column", alignItems: "flex-start", gap: "2px" } },
        title != null ? h("h3", { key: "t", className: "cv-card__title" }, title) : null,
        sub != null ? h("p", { key: "s", className: "cv-card__sub" }, sub) : null)
    : null;
  const foot = footer != null ? h("div", { key: "f", className: "cv-card__foot" }, footer) : null;
  // MATERIAL SLOT (unification sweep §2.6): the attribute binds the skin's
  // --mat-* roles on this card; the consuming rule ([data-skin] .cv-card,
  // tokens/controls.css) only fires under a skin scope — un-skinned pages
  // are byte-identical.
  return h(as, Object.assign({ className: cls, "data-material": "skin" }, rest), header, children, foot);
}

export default Card;
