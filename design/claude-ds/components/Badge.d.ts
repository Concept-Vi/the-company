import * as React from "react";

/** ConceptV badge / status label. Tone maps to a system voice or state:
 *  gold (attention) · success / warning / error (status) · comm (sage
 *  relationship). Default (no tone) is a neutral ink label. */
export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  tone?: "gold" | "success" | "warning" | "error" | "comm";
  /** Leading status dot in the current colour. */
  dot?: boolean;
  as?: any;
}

export declare function Badge(props: BadgeProps): JSX.Element;
export default Badge;
