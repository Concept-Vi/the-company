// core/RenderType.d.ts
import type { CVNode, CVAxis } from "./cv-nodes";

/** A registry Type (the CV_REGISTRY schema — the one type system). */
export interface CVType {
  id: string;
  name?: string;
  layer: "token" | "atom" | "block" | "system" | "surface" | "doc" | "template";
  family?: string;
  runtime?: { kind: string; key?: string };
  defaults?: Record<string, any>;
  slots?: Record<string, any>;
  [k: string]: any;
}

export interface RenderTypeProps extends CVAxis {
  /** a resolved registry Type object … */
  type?: CVType;
  /** … or an id to resolve in `registry` (defaults to window.CV_REGISTRY, then CoreTypes) */
  typeId?: string;
  registry?: { resolve?(id: string): CVType | null; get?(id: string): CVType | null };
  /** the instance content filling the Type's slots/defaults */
  data?: Record<string, any>;
}

/**
 * THE BRIDGE. Resolves a CV_REGISTRY Type + its data into the solver IR and
 * renders it through the one rule engine (block + graph solvers) under the
 * axis-dials. Welds the type system to the engine — UNIFICATION.md W1.
 */
export function RenderType(props: RenderTypeProps): JSX.Element;
export default RenderType;

/** Map a registry Type (+ data) to the solver IR — `{ node }` or `{ nodes }`. */
export function typeToNode(type: CVType, data: any, axis: CVAxis): { node?: CVNode; nodes?: CVNode[] };

/** The core archetypes/atoms exposed AS registry-shaped Type seeds, so the
 *  app's CV_REGISTRY single-sources its catalogue from the bundle (W2). */
export const CoreTypes: {
  archetypeSeeds(): CVType[];
  seeds(): CVType[];
  seedInto(registry: { registerMany(types: CVType[], opts?: any): void }): CVType[];
  get(id: string): CVType | null;
  resolve(id: string): CVType | null;
};
