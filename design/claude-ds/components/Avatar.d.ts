import * as React from "react";
/** Circular avatar — a photo (src) or initials/children. gold = filled gold variant. */
export interface AvatarProps extends React.HTMLAttributes<HTMLSpanElement> {
  src?: string;
  alt?: string;
  gold?: boolean;
  /** Diameter — number (px) or any CSS length. */
  size?: number | string;
}
export declare function Avatar(props: AvatarProps): JSX.Element;
export default Avatar;
