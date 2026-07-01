// core/DiagramSolver.d.ts
import type { CVGraph } from "./cv-nodes";

export interface DiagramSolverProps {
  /** the relational spec: {type, nodes, edges, axes?, center?, state?} */
  graph: CVGraph;
  axis?: {
    lod?: "summary" | "pitch" | "full";
    surface?: string;
    density?: "compact" | "comfortable" | "spacious";
  };
}

/**
 * THE GRAPH SOLVER. Computes node positions from relationships per diagram
 * type (network · hub · morph · pipeline · timeline · quadrant · tree ·
 * compare · stack) and renders edges + nodes in the diagram vocabulary.
 * type:"morph" with state "before"|"after" is the animatable network→hub
 * transform (nodes tween position via the motion tokens).
 */
export function DiagramSolver(props: DiagramSolverProps): JSX.Element;
export default DiagramSolver;
