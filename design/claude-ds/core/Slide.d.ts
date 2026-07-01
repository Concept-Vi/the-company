// core/Slide.d.ts
import type { CVNode, CVAxis, CVGraph } from "./cv-nodes";

/** A slide archetype is a pure function content -> CVNode tree. */
export type ArchetypeName =
  | "cover" | "split" | "statement" | "compare" | "modes" | "triptych"
  | "metric-band" | "checklist" | "timeline" | "profile" | "terms"
  | "gallery" | "closing" | "stepper" | "diagram";

export interface SlideProps extends CVAxis {
  /** which archetype subtree to build (default "statement") */
  archetype?: ArchetypeName | string;
  /** the content data filling the archetype's typed slots */
  content?: Record<string, any>;
}

/**
 * THE ARCHETYPE LAYER. Builds the chosen archetype's fixed Section/Zone/
 * Cluster subtree from `content`, then renders it through the block solver
 * (diagram nodes go to the graph solver). The same content at a different
 * lod / surface / density is recomputed — design = f(content, axisPosition).
 */
export function Slide(props: SlideProps): JSX.Element;
export default Slide;

/** Registry handle: list archetype names, build a tree, or register a new one. */
export const Archetypes: {
  list: string[];
  build(archetype: string, content?: Record<string, any>): CVNode;
  register(name: string, fn: (content: any) => CVNode): void;
};
