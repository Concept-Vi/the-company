import * as React from "react";
export interface SegmentedOption { value?: string; label: React.ReactNode; }
/** Segmented control (2–3 options) — the audience toggle. Active option lifts onto a surface. */
export interface SegmentedProps extends Omit<React.HTMLAttributes<HTMLDivElement>, "onChange"> {
  options: Array<SegmentedOption | string>;
  value?: string;
  onChange?: (value: string, e: React.MouseEvent) => void;
}
export declare function Segmented(props: SegmentedProps): JSX.Element;
export default Segmented;
