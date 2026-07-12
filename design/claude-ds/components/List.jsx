// components/List.jsx — rows: leading glyph/avatar slot · primary+secondary
// text (length-budgeted to the SAME tokens tokens/text.css declares,
// --len-title/--len-desc — not a re-invented number) · trailing meta/action.
// Selection/hover state rides .interactive (tokens/states.css) — no second
// interaction language. Row height is --row-h (density-aware, tokens/density.css).
/* global React */
import React from "react";
const h = React.createElement;

export function ListRow(props) {
  const {
    leading, primary, secondary, trailing, selected, onSelect,
    className = "", children, ...rest
  } = props || {};
  const interactive = !!onSelect;
  return h("div", Object.assign({
    className: ["cv-list-row", interactive ? "interactive" : "", className].filter(Boolean).join(" "),
    role: interactive ? "option" : undefined,
    tabIndex: interactive ? 0 : undefined,
    "aria-selected": interactive ? (selected ? "true" : "false") : undefined,
    onClick: onSelect,
    onKeyDown: interactive ? (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onSelect(e); } } : undefined,
  }, rest),
    leading != null ? h("span", { className: "cv-list-row__leading" }, leading) : null,
    (primary != null || secondary != null || children != null)
      ? h("span", { className: "cv-list-row__body min0" },
          primary != null ? h("span", { className: "cv-list-row__primary truncate" }, primary) : null,
          secondary != null ? h("span", { className: "cv-list-row__secondary truncate" }, secondary) : null,
          children)
      : null,
    trailing != null ? h("span", { className: "cv-list-row__trailing" }, trailing) : null);
}

export function List(props) {
  const { rows = [], divided = true, className = "", children, ...rest } = props || {};
  const content = children != null
    ? children
    : rows.map((r, i) => h(ListRow, Object.assign({ key: r.key != null ? r.key : i }, r)));
  return h("div", Object.assign({
    className: ["cv-list", divided ? "cv-list--divided" : "", className].filter(Boolean).join(" "),
    role: (rows.length || children) ? "list" : undefined,
  }, rest), content);
}

export default List;
