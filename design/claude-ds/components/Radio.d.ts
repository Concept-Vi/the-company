import * as React from "react";

/** ConceptV radio. Gold checked state (the selection/decision colour-
 *  discipline rule). Provide label/hint/error to get the labelled row +
 *  .cv-field stack (same as Input/Checkbox); omit them for a bare control. */
export interface RadioProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: React.ReactNode;
  hint?: React.ReactNode;
  error?: React.ReactNode;
}
export declare function Radio(props: RadioProps): JSX.Element;
export default Radio;
