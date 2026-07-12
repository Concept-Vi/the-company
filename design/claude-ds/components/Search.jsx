// components/Search.jsx — React wrapper over the CSS-only .cv-search pill
// (tokens/controls.css: rounded search field, icon + input, gold focus-within).
// The leading icon resolves through window.CvIcon from the ONE icon library
// (assets/icons/cv-icons.js). onChange receives the string value.
/* global React, window */
import React from "react";
const h = React.createElement;

export function Search(props) {
  const { value, onChange, placeholder = "Search…", icon = "search", trailing, className = "", ...rest } = props || {};
  const CvIcon = (typeof window !== "undefined" && window.CvIcon) || null;
  return h("div", Object.assign({ className: ["cv-search", className].filter(Boolean).join(" "), role: "search" }, rest),
    (icon && CvIcon) ? h(CvIcon, { name: icon, size: 16, tone: "muted" }) : null,
    h("input", {
      type: "search", value, placeholder, "aria-label": typeof placeholder === "string" ? placeholder : "Search",
      onChange: onChange ? (e) => onChange(e.target.value, e) : undefined,
    }),
    trailing != null ? trailing : null);
}
export default Search;
