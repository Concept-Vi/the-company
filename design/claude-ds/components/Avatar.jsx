// components/Avatar.jsx — circular initials/photo holder (team / personnel).
// Token-class wrapper over .cv-avatar. Pass src for a photo, else initials/children.
/* global React */
const h = React.createElement;
export function Avatar(props) {
  const { src, alt, gold, size, className = "", children, ...rest } = props || {};
  const style = size ? Object.assign({ "--avatar-size": typeof size === "number" ? size + "px" : size }, rest.style) : rest.style;
  return h("span", Object.assign({}, rest, {
    className: ["cv-avatar", gold ? "cv-avatar--gold" : "", className].filter(Boolean).join(" "), style,
  }), src ? h("img", { src, alt: alt || "" }) : (children != null ? children : null));
}
export default Avatar;
