import * as React from "react";

/**
 * ConceptV Glyphic — the universal compositional mark.
 *
 * A perfect-square element composed of independent, meaning-bearing parts:
 *  · Outer ring  — a regular n-gon (form), with thickness, colour, texture, and
 *                  two spaces (inner = fill plane, outer = ring→edge).
 *  · Symbol      — the distinct inner glyph (intrinsic meaning).
 * Plus whole-unit slots: size, motion, depth, and an allocated `value` that
 * drives colour through the active meaning profile.
 *
 * Geometry/symbols/colour/texture/motion/depth all resolve from their single
 * sources via window.CV_GLYPHIC.compose — this component is the React socket
 * around that one renderer, not a second implementation.
 */
export interface GlyphicProps extends React.HTMLAttributes<HTMLSpanElement> {
  /** Outer-ring form: "none" (no ring) · 3–8-gon by name · "circle". */
  form?: "none" | "triangle" | "square" | "pentagon" | "hex" | "septagon" | "octagon" | "diamond" | "circle";
  /** Inner glyph — a CV_ICONS id (e.g. "house", "person", "drone"). */
  symbol?: string;
  /** Ring inner space (fill plane). "none" = α-0 transparent. */
  fill?: "none" | "paper" | "wash" | "tint";
  /** Ring stroke colour — a colour-token name (gold · bronze · sage · …). */
  ringColor?: string;
  /** Symbol colour — a colour-token name. */
  symbolColor?: string;
  /** Surface texture on the ring (requires fill ≠ none). */
  texture?: "none" | "hatch" | "dense" | "cross" | "grid" | "lines" | "vert" | "dots";
  /** Ambient/entrance motion. */
  motion?: "none" | "breathe" | "pulse" | "bob" | "tilt" | "spin" | "float" | "glow";
  /** Elevation / shadow depth. */
  depth?: "flat" | "d1" | "d2" | "d3" | "d4" | "d5" | "d6" | "normal";
  /** Overall size in px. */
  size?: number;
  /** Allocated value (e.g. "active", "warning") — colours via the meaning profile. */
  value?: string;
}

export declare function Glyphic(props: GlyphicProps): JSX.Element;
export default Glyphic;
