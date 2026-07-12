import * as React from "react";

/** Mobile-first slide-in panel — the touch sibling of Modal. Shares Modal's
 *  overlay/Escape/close-button conventions. side="right" (drawer) |
 *  "bottom" (sheet, drag handle guarded to --touch-min). Controlled via
 *  `open`; stays mounted through the exit transition. */
export interface SheetProps extends React.HTMLAttributes<HTMLDivElement> {
  open?: boolean;
  onClose?: () => void;
  side?: "right" | "bottom";
  title?: React.ReactNode;
  footer?: React.ReactNode;
}
export declare function Sheet(props: SheetProps): JSX.Element | null;
export default Sheet;
