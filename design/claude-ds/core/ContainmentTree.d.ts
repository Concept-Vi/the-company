// core/ContainmentTree.d.ts
import type { CVNode } from "./cv-nodes";

export interface ContainmentTreeProps {
  /** the content tree to lay out */
  node: CVNode;
  /** content zoom — prunes/grows the tree (independent of surface) */
  lod?: "summary" | "pitch" | "full";
  /** screen/ratio — drives reflow + locked band aspect */
  surface?: "desktop" | "tablet" | "mobile-portrait" | "mobile-landscape" | "slide" | "print" | "web";
  /** breathing room — scales spacing at every level */
  density?: "compact" | "comfortable" | "spacious";
  /** the graph solver to render kind:"diagram" nodes (pass window.<NS>.DiagramSolver) */
  DiagramSolver?: any;
}

/**
 * THE BLOCK SOLVER. Renders a CVNode tree as the typed containment ladder
 * (Band→Section→Zone→Cluster→Atom). Zone wash is computed from nesting depth;
 * LOD prunes low-priority / support nodes before layout. The same `node` at
 * a different `lod`/`surface`/`density` computes a different concrete design.
 */
export function ContainmentTree(props: ContainmentTreeProps): JSX.Element & {
  /** register a new atom role without editing the solver (atoms = data) */
  registerAtom(role: string, fn: (node: CVNode, key: string) => any): void;
  /** the currently-registered atom roles */
  atomRoles(): string[];
};
export default ContainmentTree;
