// components/Table.jsx — React wrapper over the CSS-only .cv-table
// (tokens/controls.css: the comparison/pricing table). columns declare
// key/label + num (right-aligned tabular numerals via .cv-table__num) +
// feature (the highlighted gold offer column via .cv-table__feature).
// striped = .cv-table--striped. Pass children for full manual control.
/* global React */
import React from "react";
const h = React.createElement;

export function Table(props) {
  const { columns = [], rows = [], striped, className = "", children, ...rest } = props || {};
  const cls = ["cv-table", striped ? "cv-table--striped" : "", className].filter(Boolean).join(" ");
  if (children != null) return h("table", Object.assign({ className: cls }, rest), children);
  const cellCls = (c) => [c.num ? "cv-table__num" : "", c.feature ? "cv-table__feature" : ""].filter(Boolean).join(" ") || undefined;
  return h("table", Object.assign({ className: cls }, rest),
    columns.length ? h("thead", null, h("tr", null,
      columns.map((c) => h("th", { key: c.key, className: c.num ? "cv-table__num" : undefined, scope: "col" }, c.label)))) : null,
    h("tbody", null, rows.map((r, i) =>
      h("tr", { key: r.key != null ? r.key : i },
        columns.map((c) => h("td", { key: c.key, className: cellCls(c) }, r[c.key]))))));
}
export default Table;
