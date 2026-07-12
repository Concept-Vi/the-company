import * as React from "react";

/** React wrapper over the CSS-only .skeleton shimmer placeholder
 *  (tokens/states.css). Swap for real content with an .enter-* class so
 *  content resolves, never pops. */
export interface SkeletonProps extends React.HTMLAttributes<HTMLSpanElement> {
  /** text = inline text line · line = 8px bar · circle = round (avatar) ·
   *  block = free rectangle. Default "line". */
  variant?: "text" | "line" | "circle" | "block";
  width?: number | string;
  height?: number | string;
}
export declare function Skeleton(props: SkeletonProps): JSX.Element;
export default Skeleton;
