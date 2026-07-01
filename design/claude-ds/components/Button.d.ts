import * as React from "react";

/** ConceptV action button. Variants map to the source's button vocabulary:
 *  primary = gold decision voice · ink = dark panotour button · outline = gold
 *  stroke pill · ghost = text-only · soft = gold-tint · comm = sage relationship. */
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** Visual emphasis / voice. Default "primary". */
  variant?: "primary" | "ink" | "outline" | "ghost" | "soft" | "comm" | "default";
  /** Size step. Default is the standard control height. */
  size?: "sm" | "lg";
  /** Fully rounded (pill) — the "Virtual Tour" / "Click to View" treatment. */
  pill?: boolean;
  /** Stretch to full width. */
  block?: boolean;
  /** Square icon-only button. */
  icon?: boolean;
  /** Render as a different element/component (e.g. "a"). Inferred as <a> if href is set. */
  as?: any;
  href?: string;
}

export declare function Button(props: ButtonProps): JSX.Element;
export default Button;
