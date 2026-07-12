import * as React from "react";
/** Hint bubble shown on hover/focus of its child. Positioned by the shared
 *  Popover engine (flips/shifts to stay in view). */
export interface TooltipProps extends Omit<React.HTMLAttributes<HTMLSpanElement>, "children"> {
  /** Bubble contents. */
  label: React.ReactNode;
  placement?: "top" | "bottom" | "left" | "right" |
    "top-start" | "top-end" | "bottom-start" | "bottom-end";
  /** Hover-in delay (ms) before showing. Default 120. */
  delay?: number;
  children?: React.ReactNode;
}
export declare function Tooltip(props: TooltipProps): JSX.Element;
export default Tooltip;
