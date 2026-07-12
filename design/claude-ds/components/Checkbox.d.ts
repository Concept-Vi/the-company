import * as React from "react";

/** ConceptV checkbox. Gold checked state (the selection/decision colour-
 *  discipline rule). Provide label/hint/error to get the labelled row +
 *  .cv-field stack (same as Input); omit them for a bare control. */
export interface CheckboxProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: React.ReactNode;
  hint?: React.ReactNode;
  error?: React.ReactNode;
  /** Visual dash state — does not affect `checked`/`onChange`. */
  indeterminate?: boolean;
}
export declare function Checkbox(props: CheckboxProps): JSX.Element;
export default Checkbox;
