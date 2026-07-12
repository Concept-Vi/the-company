import * as React from "react";

/** Pure placement: position `float` (a fixed element) against `anchor`,
 *  flipping side when out of room and shifting into the viewport. Returns the
 *  resolved side. Also published as `window.CV_POPOVER.place`. */
export interface PlaceOpts {
  placement?: "top" | "bottom" | "left" | "right" |
    "top-start" | "top-center" | "top-end" |
    "bottom-start" | "bottom-center" | "bottom-end" |
    "left-start" | "left-center" | "left-end" |
    "right-start" | "right-center" | "right-end";
  gap?: number;
  flip?: boolean;
  shift?: boolean;
}

/** Shared anchored floating layer behind Tooltip and Select. Controlled via
 *  `open`; positions against `anchorRef`, repositions on scroll/resize, closes
 *  on outside-click / Escape through `onRequestClose`. `bare` drops the surface
 *  chrome (used by Tooltip, which supplies its own bubble). */
export interface PopoverProps extends Omit<React.HTMLAttributes<HTMLDivElement>, "role"> {
  open?: boolean;
  anchorRef: React.RefObject<HTMLElement>;
  placement?: PlaceOpts["placement"];
  gap?: number;
  /** Match the popover's min-width to the anchor's width (used by Select). */
  matchWidth?: boolean;
  /** Positioning only — no background/border/shadow/padding. */
  bare?: boolean;
  role?: string;
  onRequestClose?: () => void;
  children?: React.ReactNode;
}
export declare function Popover(props: PopoverProps): JSX.Element | null;
export default Popover;
