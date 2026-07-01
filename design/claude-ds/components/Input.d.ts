import * as React from "react";

/** ConceptV form field. Renders a text input by default (gold focus ring from
 *  the source composer); set as="textarea" or as="select". Provide label / hint
 *  / error to wrap it in the labelled .cv-field stack; omit them for a bare control. */
export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  /** Which control element to render. Default "input". */
  as?: "input" | "textarea" | "select";
  /** Field label (renders the .cv-field wrapper). */
  label?: React.ReactNode;
  /** Helper text below the control. */
  hint?: React.ReactNode;
  /** Error message — sets aria-invalid and the reject styling. */
  error?: React.ReactNode;
}

export declare function Input(props: InputProps): JSX.Element;
export default Input;
