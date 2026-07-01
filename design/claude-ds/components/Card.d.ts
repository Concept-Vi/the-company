import * as React from "react";

/** ConceptV surface card. Variants: soft (cream deck panel) · surface (white
 *  content card) · outline (stroke only) · gold (gold-tinted) · plus raised /
 *  interactive / padding modifiers. Optional header (title/sub) + footer. */
export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "soft" | "surface" | "outline" | "gold";
  raised?: boolean;
  interactive?: boolean;
  pad?: "sm" | "lg";
  title?: React.ReactNode;
  sub?: React.ReactNode;
  footer?: React.ReactNode;
  as?: any;
}

export declare function Card(props: CardProps): JSX.Element;
export default Card;
