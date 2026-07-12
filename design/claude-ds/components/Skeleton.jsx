// components/Skeleton.jsx — React wrapper over the CSS-only .skeleton
// (tokens/states.css: shimmer placeholder; reduced-motion already gated
// there). variant text|line|circle|block maps to the existing modifier
// classes; width/height are per-instance geometry (the one prop that is
// legitimately instance data, passed as style, not a token).
/* global React */
import React from "react";
const h = React.createElement;

export function Skeleton(props) {
  const { variant = "line", width, height, className = "", style, ...rest } = props || {};
  const cls = ["skeleton", variant !== "block" ? variant : "", className].filter(Boolean).join(" ");
  const s = Object.assign({}, style);
  if (width != null) s.width = typeof width === "number" ? width + "px" : width;
  if (height != null) s.height = typeof height === "number" ? height + "px" : height;
  return h("span", Object.assign({ className: cls, style: s, "aria-hidden": "true" }, rest));
}
export default Skeleton;
