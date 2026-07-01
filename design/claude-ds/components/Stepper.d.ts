import * as React from "react";
export interface StepItem { label: React.ReactNode; }
/** Linear numbered stepper. Steps before `active` show as done (gold ✓ dots),
 *  `active` is highlighted, the rest are upcoming. */
export interface StepperProps extends React.HTMLAttributes<HTMLDivElement> {
  steps: Array<StepItem | string>;
  active?: number;
}
export declare function Stepper(props: StepperProps): JSX.Element;
export default Stepper;
