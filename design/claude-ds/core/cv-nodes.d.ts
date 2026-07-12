// core/cv-nodes.d.ts
// ------------------------------------------------------------
// The SHARED type system both solvers consume (analysis/AXES.md:
// "one type system, one rule engine, two solvers"). A piece of
// content is a tree of CVNodes. The BLOCK solver lays it out by
// nesting + flow; a node of kind "diagram" hands its `graph` to the
// GRAPH solver. Same nodes, two layout strategies.

/** Where in the axis-space a design is computed. Orthogonal dials. */
export interface CVAxis {
  /** content zoom — prunes/grows the tree, independent of surface */
  lod?: "summary" | "pitch" | "full";
  /** screen/ratio — drives reflow + which band aspect is locked */
  surface?: "desktop" | "tablet" | "mobile-portrait" | "mobile-landscape" | "slide" | "print" | "web";
  /** breathing room — scales spacing uniformly at every level */
  density?: "compact" | "comfortable" | "spacious";
}

export type CVKind = "band" | "section" | "zone" | "cluster" | "atom" | "diagram";

export interface CVNode {
  kind: CVKind;
  /** semantic role of an atom — metric · hero-number · bullet · chip · badge · note · qr · image · text (extensible via ContainmentTree.registerAtom) */
  role?: string;
  /** entity shape for a `badge` atom / graph node — circle (User Portal) · hex (Property Wizard) · octagon (Virtual Hubs) · diamond (Vi) */
  shape?: "circle" | "hex" | "octagon" | "diamond" | "square";
  /** aspect ratio for an `image` placeholder atom, e.g. "16 / 10" */
  ratio?: string;
  /** lift a zone with elevation instead of (or with) its depth wash */
  raised?: boolean;
  /** authorship marking (DESIGN-LANGUAGE §11) — human · vi (gets the .vi-authored wash) · suggested */
  author?: "human" | "vi" | "suggested";
  /** zone wash pigment selector — warm (default) · neutral (the "odd one out") · review */
  tone?: "warm" | "neutral" | "review";
  /** cluster layout — col (default) · row · grid · split (the 46/54 working layout) */
  flow?: "col" | "row" | "grid" | "split";
  /** override the split ratio for flow:"split", e.g. "46fr 54fr" */
  split?: string;
  /** cluster render mode — "space" (all children at once, default) · "time" (play one at a time) */
  mode?: "space" | "time";
  /** progressive disclosure — a section shown at low LOD with a toggle that raises it to full */
  disclose?: boolean;
  /** focus subject — on a cluster, the child id or index to spotlight; the rest recede (focus.css) */
  focus?: string | number;
  /** narrative priority 1..n — 1 always shows; higher drops first as LOD lowers */
  priority?: number;
  /** "support" atoms (the justification of a claim) hide at low LOD; "always" never prune */
  detail?: "always" | "support";
  title?: string;
  /** caption shown beneath a `badge` atom's shape (else the shape carries the label inside) */
  caption?: string;
  text?: string;
  /** number+label atom (the sacred, LOD-locked payload) */
  value?: string;
  label?: string;
  /** metric delta, e.g. "+3.2pt" + direction (renders green up / red down) */
  delta?: string;
  deltaKind?: "up" | "down";
  /** chart atom kind + data — spark (points) · bar/gauge (value 0–100) */
  chart?: "spark" | "bar" | "gauge";
  points?: number[];
  /** bullet semantic — plain ▶ · leads-to → · done ✓ */
  bullet?: "dot" | "leads" | "done";
  children?: CVNode[];
  /** for kind:"diagram" — the spec handed to the graph solver */
  graph?: CVGraph;
}

// ---- Graph side (relational solver) --------------------------
export type CVGraphType =
  | "network" | "hub" | "morph" | "pipeline"
  | "timeline" | "quadrant" | "tree" | "compare" | "stack" | "stepper"
  | "glyphgraph";  // the language's sentence-graph (nodes = typed glyphics; W0 drift-fix — the solver already handles it)

export interface CVGraphNode {
  id: string;
  label?: string;
  /** shape vocabulary — circle (User Portal) · hex (Property Wizard) · octagon (Virtual Hubs) · diamond (Vi) · square */
  shape?: "circle" | "hex" | "octagon" | "diamond" | "square";
  /** zone tone for the node fill */
  tone?: "warm" | "neutral" | "review" | "active";
  icon?: string;
  /** quadrant placement 0..1 when type === "quadrant" */
  x?: number;
  y?: number;
}

export interface CVGraphEdge {
  from: string;
  to: string;
  /** edge semantic — flow (gold) · dependency (dashed) · reference (dotted) · rejected;
   *  glyphgraph edges use CV_MEANING's open edge-kind vocabulary (face/part-of/becomes/…) */
  kind?: string;
  label?: string;
  /** glyphgraph edge facets (W0 drift-fix — glyphGraphView already consumes these):
   *  line = the relation's MOOD (solid=is · dashed=could · dotted=might · lines=flows) */
  line?: "solid" | "dashed" | "dotted" | "lines" | "right-angled" | "curved" | "free";
  /** direction = the ROLE (subject→object) */
  direction?: "to" | "from" | "both" | "none";
  /** routing = the path character (straight | elbow | curve) */
  routing?: string;
  /** lineColor = a CV_MEANING lineColor field id (state carried by the stroke), resolved to a token — never hex */
  lineColor?: string;
}

export interface CVGraph {
  type: CVGraphType;
  nodes: CVGraphNode[];
  edges?: CVGraphEdge[];
  /** quadrant axis labels [xLabel, yLabel] */
  axes?: [string, string];
  /** hub/radial centre node id */
  center?: string;
  /** morph state — "before" (network) ↔ "after" (hub) */
  state?: "before" | "after";
  /** stepper active index — steps 0..active render filled (ramp-tinted) */
  active?: number;
}
