// core/DiagramSolver.jsx
// ------------------------------------------------------------
// THE GRAPH SOLVER (analysis/AXES.md + DIAGRAMS.md). Same content
// substrate as the block solver, different layout strategy: position is
// COMPUTED FROM RELATIONSHIPS (edges, axes, hub), not from nesting. One
// {type, nodes, edges} spec → a laid-out diagram in the system's
// vocabulary. type:"morph" with state before↔after is the animatable
// network→hub transform.
//
// Token-pure (strokes/fills/shapes from tokens/diagram.css + zones).
// JSX-free; read in cards via const { DiagramSolver } = window.<NS>.
/* global React */
const h = React.createElement;
const VB = 320;                 // square viewbox; layout normalised to it
// inline-edit a graph node label (W6 graph) — contentEditable + commit on blur
function edLabel(onEdit, path, content, props) {
  props = props || {};
  const txt = content == null ? "" : content;
  if (onEdit && path != null) {
    return h("span", Object.assign({}, props, { contentEditable: true, suppressContentEditableWarning: true, spellCheck: false,
      onFocus: (e) => { if (typeof window !== "undefined" && window.__cvFieldFocus) window.__cvFieldFocus({ el: e.currentTarget, value: txt, path, apply: (nv) => onEdit(path, nv) }); },
      onBlur: (e) => { const v = e.currentTarget.textContent; if (v !== String(txt)) onEdit(path, v); },
      onKeyDown: (e) => { if (e.key === "Enter") { e.preventDefault(); e.currentTarget.blur(); } } }), txt);
  }
  return h("span", props, txt);
}
const R = 130;                  // radial radius

// ---- position solvers, one per diagram type ----------------------
function layout(graph) {
  const { type, nodes, center } = graph;
  const n = nodes.length;
  const cx = VB / 2, cy = VB / 2;
  const pos = {};

  const ring = (items, radius) => items.forEach((nd, i) => {
    const a = -Math.PI / 2 + (i * 2 * Math.PI) / items.length;
    pos[nd.id] = { x: cx + radius * Math.cos(a), y: cy + radius * Math.sin(a) };
  });

  switch (type) {
    case "hub": {
      const c = center || nodes[0].id;
      pos[c] = { x: cx, y: cy };
      ring(nodes.filter(nd => nd.id !== c), R);
      break;
    }
    case "morph": {            // before = ring (network); after = hub
      if (graph.state === "after") { const c = center || nodes[0].id; pos[c] = { x: cx, y: cy }; ring(nodes.filter(nd => nd.id !== c), R); }
      else ring(nodes, R);
      break;
    }
    case "network": ring(nodes, R); break;
    case "pipeline":           // left→right evenly spaced
      nodes.forEach((nd, i) => { pos[nd.id] = { x: 40 + (i * (VB - 80)) / Math.max(1, n - 1), y: cy }; });
      break;
    case "timeline":           // same as pipeline but anchored lower
      nodes.forEach((nd, i) => { pos[nd.id] = { x: 40 + (i * (VB - 80)) / Math.max(1, n - 1), y: cy + 30 }; });
      break;
    case "quadrant":           // explicit x/y in 0..1
      nodes.forEach(nd => { pos[nd.id] = { x: 40 + (nd.x ?? 0.5) * (VB - 80), y: VB - 40 - (nd.y ?? 0.5) * (VB - 80) }; });
      break;
    case "glyphgraph": {       // G5: a meaning-graph of full glyphics.
      // Position priority: (1) AUTHORED x/y in 0..1 (like quadrant — the author placed it),
      // else (2) a LAYERED fallback — rank nodes by longest-path-from-a-source (a simple DAG
      // layering) into rows, spread evenly across each row; a cyclic/source-less graph falls
      // back to a ring. No external layout lib (CSP/bundle) — closed-form, like the siblings.
      const authored = nodes.every(nd => nd.x != null && nd.y != null);
      if (authored) {
        nodes.forEach(nd => { pos[nd.id] = { x: 30 + nd.x * (VB - 60), y: 30 + nd.y * (VB - 60) }; });
        break;
      }
      const E = graph.edges || [];
      // rank = longest distance from any source (a node that is never a target). BFS-ish relax.
      const tos = {}; E.forEach(e => { tos[e.to] = 1; });
      const rank = {}; nodes.forEach(nd => { rank[nd.id] = tos[nd.id] ? null : 0; });
      // sources start at 0; if every node is a target (cycle), seed the first node at 0.
      if (nodes.every(nd => rank[nd.id] == null)) rank[nodes[0].id] = 0;
      let changed = true, guard = 0;
      while (changed && guard++ < nodes.length + 2) {
        changed = false;
        E.forEach(e => {
          if (rank[e.from] != null) {
            const r = rank[e.from] + 1;
            if (rank[e.to] == null || r > rank[e.to]) { rank[e.to] = r; changed = true; }
          }
        });
      }
      nodes.forEach(nd => { if (rank[nd.id] == null) rank[nd.id] = 0; });   // orphans → row 0
      // group by rank → rows top→bottom. PUSH order = the node's AUTHOR order, so a node's slot
      // index within its row is stable (the order it was authored, not "who's present now").
      const rows = {}; nodes.forEach(nd => { (rows[rank[nd.id]] = rows[rank[nd.id]] || []).push(nd); });
      const rankKeys = Object.keys(rows).map(Number).sort((a, b) => a - b);
      const nR = rankKeys.length;
      if (nR <= 1) { ring(nodes, R); break; }   // flat (no structure) → ring
      // G11 · STABLE-SLOT placement (staged-reveal stability). Each node sits at a slot whose
      // coordinate is a function of its FIXED slot index + a FIXED pitch — NEVER the live count.
      // So adding a same-rank sibling does NOT move any existing node (the old even-spread
      // `ci*(VB-88)/(m-1)` re-centred the whole row on every addition — a 116px jump on a 320
      // canvas, verified). Growth is absorbed by the unused slots / margin, not by reflow.
      // Pitch is derived from a FIXED reference glyphic size (LAY_SIZE) — independent of the
      // count-dependent RENDER size, so crossing the 4/6-node render-shrink thresholds does not
      // move positions either. Slots/row beyond CAP is the declared SCOPE boundary (bounded
      // viewbox + unbounded fan-out cannot both hold) — extra slots run off the right edge
      // honestly rather than silently re-packing the row (no green-paint compression).
      const LAY_SIZE = 58;                       // fixed overlap floor (== glyphGraphView's max node size)
      const LAY_PITCH = LAY_SIZE * 1.55;         // slot stride: a node + a gap (~90px)
      const LAY_MARGIN = 44;                     // edge gutter (matches the sibling layouts)
      const LAY_ROW_PITCH = (VB - 2 * LAY_MARGIN) / Math.max(1, nR - 1);  // row stride; nR only grows when a NEW RANK appears (out of same-rank-sibling scope)
      rankKeys.forEach((rk, ri) => {
        const row = rows[rk];
        const y = nR === 1 ? cy : LAY_MARGIN + ri * LAY_ROW_PITCH;
        // ANCHOR LEFT (slot 0 at the margin). The honest staged-reveal tradeoff: in a bounded
        // viewbox you cannot BOTH keep existing nodes pinned AND re-centre the row when a sibling
        // appears — centring would move every node. We pin (left-anchor by fixed slot), accept an
        // off-centre / left-hugging row. The visual consequence (graph hugs the left, right gutter
        // empty for small rows) is FLAGGED for Tim — not papered over.
        row.forEach((nd, ci) => { pos[nd.id] = { x: LAY_MARGIN + ci * LAY_PITCH, y }; });
      });
      break;
    }
    case "tree": {             // root top, children spread below
      const root = center || nodes[0].id;
      pos[root] = { x: cx, y: 48 };
      const rest = nodes.filter(nd => nd.id !== root);
      rest.forEach((nd, i) => { pos[nd.id] = { x: 40 + (i * (VB - 80)) / Math.max(1, rest.length - 1), y: VB - 70 }; });
      break;
    }
    case "stack":              // vertical layers
      nodes.forEach((nd, i) => { pos[nd.id] = { x: cx, y: 50 + (i * (VB - 100)) / Math.max(1, n - 1) }; });
      break;
    default: ring(nodes, R);
  }
  return pos;
}

const EDGE_CLASS = { flow: "dgm-edge dgm-edge--flow", dependency: "dgm-edge dgm-edge--dep", reference: "dgm-edge dgm-edge--ref", rejected: "dgm-edge dgm-edge--rej", communication: "dgm-edge dgm-edge--comm", bidirectional: "dgm-edge dgm-edge--bi" };
const SHAPE = {
  circle:  (s) => ({ borderRadius: "50%" }),
  square:  (s) => ({ borderRadius: "var(--r-sm,6px)" }),
  hex:     (s) => ({ clipPath: "polygon(25% 0,75% 0,100% 50%,75% 100%,25% 100%,0 50%)" }),
  octagon: (s) => ({ clipPath: "polygon(29% 0,71% 0,100% 29%,100% 71%,71% 100%,29% 100%,0 71%,0 29%)" }),
  diamond: (s) => ({ clipPath: "polygon(50% 0,100% 50%,50% 100%,0 50%)" }),
};
// the brand ramp, indexed — diagram tint maps sequence/position onto it
const RAMP = ["var(--ramp-1)", "var(--ramp-2)", "var(--ramp-3)", "var(--ramp-4)"];
const TONE_FILL = {
  warm:    "var(--zone-pigment, color-mix(in oklch, var(--pig-content) calc(6% * var(--zone-intensity)), var(--zone-ground)))",
  neutral: "color-mix(in oklch, var(--pig-panel) calc(8% * var(--zone-intensity)), var(--zone-ground))",
  review:  "color-mix(in oklch, var(--pig-review) calc(10% * var(--zone-intensity)), var(--zone-ground))",
  active:  "var(--vi-surface)",
};

// ============================================================
//  NEW SUB-TYPE VIEWS (capital-raise grammar, DIAGRAMS.md). Each is an
//  early-return HTML layout (like the chevron stepper) — token-pure, off the
//  square SVG path, so they reflow with flex/grid and survive direct edits.
//  All shapes/fills/strokes resolve to diagram + brand tokens; no literals.
// ============================================================
const SOFT_CARD = {
  background: "var(--zone-ground)", borderRadius: "var(--r-lg)",
  boxShadow: "var(--elev-2), inset 0 1px 0 rgba(255,255,255,.6)",
};
const CAP = { font: "var(--weight-semibold,600) var(--fs-caption)/1.15 var(--font-body)", color: "var(--ink-3)" };
function shapedNode(label, shape, opts) {
  opts = opts || {};
  const active = opts.tone === "active";
  const stroke = active ? "var(--vi-edge)" : "var(--accent-gold)";
  const fill = active ? "var(--vi-surface)" : "var(--zone-ground)";
  const size = opts.size || "86px";
  const base = { position: "relative", display: "grid", placeItems: "center", textAlign: "center", boxSizing: "border-box",
    minWidth: size, minHeight: "54px", padding: "var(--d-2) var(--d-3)",
    font: "var(--weight-semibold,600) var(--fs-caption)/1.1 var(--font-body)", color: "var(--ink)" };
  // circle / square keep a real CSS border (border-radius doesn't clip it).
  if (shape === "circle")
    return h("div", { style: Object.assign({}, base, { borderRadius: "50%", aspectRatio: "1", background: fill, border: "1.5px solid " + stroke, boxShadow: active ? "var(--glow-active)" : "var(--elev-1)" }) }, label);
  const POLY = { hex: "25,3 75,3 97,50 75,97 25,97 3,50", octagon: "29,3 71,3 97,29 97,71 71,97 29,97 3,71 3,29", diamond: "50,3 97,50 50,97 3,50" };
  if (!POLY[shape])   // square / unknown
    return h("div", { style: Object.assign({}, base, { borderRadius: "var(--r-md)", background: fill, border: "1.5px solid " + stroke, boxShadow: active ? "var(--glow-active)" : "var(--elev-1)" }) }, label);
  // hex / octagon / diamond: a real SVG OUTLINE behind the label — clip-path
  // would strip the border (invisible on a light ground); this keeps the stroke.
  return h("div", { style: Object.assign({}, base, { background: "transparent" }) },
    h("svg", { viewBox: "0 0 100 100", preserveAspectRatio: "none", style: { position: "absolute", inset: 0, width: "100%", height: "100%", zIndex: 0, filter: active ? "drop-shadow(0 0 6px color-mix(in oklch, var(--accent-gold) 40%, transparent))" : "none" } },
      h("polygon", { points: POLY[shape], fill: fill, stroke: stroke, strokeWidth: 2, vectorEffect: "non-scaling-stroke", strokeLinejoin: "round" })),
    h("span", { style: { position: "relative", zIndex: 1 } }, label));
}

// ORBITAL verb-ring (hub subtype, capital-raise p5): a central shaped node
// ringed by VERB labels on concentric arcs — the process AROUND the node.
function orbitalView(graph, onEdit) {
  const c = graph.center || {};
  const verbs = graph.verbs || [];
  const ring = (pct, dash) => h("div", { key: "r" + pct, style: { position: "absolute", left: "50%", top: "50%", width: pct + "%", height: pct + "%", transform: "translate(-50%,-50%)", borderRadius: "50%", border: "1px " + (dash ? "dashed" : "solid") + " color-mix(in oklch, var(--accent-gold) " + (dash ? 34 : 22) + "%, transparent)" } });
  return h("div", { className: "cv-diagram cv-diagram--orbital", style: { position: "relative", width: "100%", maxWidth: "460px", aspectRatio: "1 / 1", margin: "0 auto" } },
    ring(58, false), ring(84, true),
    h("div", { style: { position: "absolute", left: "50%", top: "50%", transform: "translate(-50%,-50%)" } }, shapedNode(edLabel(onEdit, c.edit, c.label || "Hub"), c.shape || "hex", { tone: "active", size: "108px" })),
    verbs.map((v, i) => {
      const a = -Math.PI / 2 + (i * 2 * Math.PI) / Math.max(1, verbs.length);
      const rad = 42;
      return h("div", { key: "v" + i, style: { position: "absolute", left: (50 + rad * Math.cos(a)) + "%", top: (50 + rad * Math.sin(a)) + "%", transform: "translate(-50%,-50%)", display: "flex", flexDirection: "column", alignItems: "center", gap: "2px" } },
        h("span", { style: { font: "var(--weight-bold,700) var(--fs-caption)/1 var(--font-body)", letterSpacing: "var(--tracking-caps,0.08em)", textTransform: "uppercase", color: "var(--accent-bronze)" } }, edLabel(onEdit, v.edit, v.label || v)));
    }));
}

// STACKED pipeline (flow subtype, capital-raise p4/p9): a left→right row of
// nodes, each a COLLAPSED SET — category members peek above (〈) and below (⌬).
// `+` join nodes and shape-coding honoured. Bidirectional-friendly.
function stackedView(graph, onEdit) {
  const nodes = graph.nodes || [];
  const member = (m, pos) => h("div", { key: pos + (m.label || m), style: { font: "var(--weight-medium,500) var(--fs-meta)/1.2 var(--font-body)", color: "var(--ink-2)", background: "var(--zone-ground)", borderRadius: "var(--r-sm,6px)", boxShadow: "var(--elev-1)", padding: "3px 9px", whiteSpace: "nowrap" } }, m.label || m);
  const chev = (d) => h("span", { style: { color: "var(--accent-gold)", font: "var(--weight-bold,700) 0.7em/1 var(--font-body)" } }, d === "up" ? "⌃" : "⌬");
  const arrow = (plus) => h("div", { style: { flex: "none", display: "grid", placeItems: "center", color: "var(--accent-gold)", width: plus ? "26px" : "22px", height: plus ? "26px" : "auto", alignSelf: "center", border: plus ? "1.5px solid var(--accent-gold)" : "none", borderRadius: plus ? "50%" : 0, font: "var(--weight-bold,700) var(--fs-body) var(--font-body)" } }, plus ? "+" : "→");
  const out = [];
  nodes.forEach((nd, i) => {
    const top = nd.top || [], bottom = nd.bottom || [];
    out.push(h("div", { key: "n" + i, style: { flex: "1 1 0", minWidth: 0, display: "flex", flexDirection: "column", alignItems: "center", gap: "4px" } },
      top.length ? chev("up") : null,
      top.map((m) => member(m, "t")),
      shapedNode(edLabel(onEdit, nd.edit, nd.label || nd.id), nd.shape || "square", { tone: nd.tone, size: "100%" }),
      bottom.map((m) => member(m, "b")),
      bottom.length ? chev("down") : null));
    if (i < nodes.length - 1) out.push(h("div", { key: "a" + i, style: { flex: "none", alignSelf: "center" } }, arrow(nodes[i + 1] && nodes[i + 1].join === "plus")));
  });
  return h("div", { className: "cv-diagram cv-diagram--stacked", style: { display: "flex", alignItems: "center", gap: "var(--d-1)", width: "100%" } }, out);
}

// SPECTRUM 1-D axis (positioning subtype, capital-raise p13): a single
// gold→bronze GRADIENT directional axis with plotted cards, segment labels and
// an optional hatch zone marking a sub-range. `at` ∈ 0..1 along the axis.
function spectrumView(graph, onEdit) {
  const ends = graph.ends || ["", ""];
  const segs = graph.segments || [], cards = graph.cards || [], hatch = graph.hatch;
  const track = { position: "relative", margin: "0 8%" };   // inset so edge cards/labels never clip
  return h("div", { className: "cv-diagram cv-diagram--spectrum", style: { position: "relative", width: "100%", padding: "var(--d-6) 0" } },
    h("div", { style: Object.assign({}, track, { height: "18px", marginBottom: "var(--d-2)" }) },
      segs.map((s, i) => h("span", { key: "s" + i, style: { position: "absolute", left: ((s.at != null ? s.at : 0.5) * 100) + "%", transform: "translateX(-50%)", whiteSpace: "nowrap", font: "var(--weight-semibold,600) var(--fs-caption) var(--font-body)", color: "var(--ink-2)" } }, edLabel(onEdit, s.edit, s.label)))),
    h("div", { style: Object.assign({}, track, { height: "7px", borderRadius: "999px", background: "linear-gradient(90deg, var(--ramp-1), var(--ramp-4))" }) },
      hatch ? h("div", { style: { position: "absolute", top: "-7px", bottom: "-7px", left: (hatch[0] * 100) + "%", width: ((hatch[1] - hatch[0]) * 100) + "%", backgroundImage: "repeating-linear-gradient(45deg, transparent 0 6px, color-mix(in oklch, var(--accent-gold) 30%, transparent) 6px 7px)", border: "1px dashed color-mix(in oklch, var(--accent-gold) 40%, transparent)", borderRadius: "var(--r-sm,6px)" } }) : null,
      h("span", { style: { position: "absolute", left: "-16px", top: "50%", transform: "translateY(-50%)", fontSize: "0.7em", color: "var(--ramp-1)" } }, "◀"),
      h("span", { style: { position: "absolute", right: "-16px", top: "50%", transform: "translateY(-50%)", fontSize: "0.7em", color: "var(--ramp-4)" } }, "▶")),
    h("div", { style: Object.assign({}, track, { height: "40px", marginTop: "var(--d-2)" }) },
      cards.map((cd, i) => h("div", { key: "c" + i, style: { position: "absolute", left: (cd.at * 100) + "%", top: 0, transform: "translateX(-50%)", display: "flex", flexDirection: "column", alignItems: "center", gap: "2px" } },
        h("span", { style: { width: "1px", height: "8px", background: "var(--hairline-strong)" } }),
        h("span", { style: Object.assign({}, SOFT_CARD, { padding: "4px 10px", font: "var(--weight-semibold,600) var(--fs-caption)/1.1 var(--font-body)", color: "var(--ink)", whiteSpace: "nowrap" }) }, edLabel(onEdit, cd.edit, cd.label))))),
    h("div", { style: { display: "flex", justifyContent: "space-between", marginTop: "var(--d-1)", padding: "0 1%" } },
      h("span", { style: Object.assign({}, CAP, { color: "var(--ink)", fontWeight: 700 }) }, ends[0]),
      h("span", { style: Object.assign({}, CAP, { color: "var(--ink)", fontWeight: 700, textAlign: "right" }) }, ends[1])));
}

// MANIFOLD / converging-summation (tree subtype, capital-raise p12/p28): N
// branch cards → a dashed horizontal MANIFOLD → a single drop to one total chip.
function manifoldView(graph, onEdit) {
  const branches = graph.branches || [], total = graph.total || {};
  return h("div", { className: "cv-diagram cv-diagram--manifold", style: { display: "flex", flexDirection: "column", alignItems: "stretch", gap: "var(--d-3)", width: "100%" } },
    h("div", { style: { display: "grid", gridTemplateColumns: "repeat(" + Math.max(1, branches.length) + ", 1fr)", gap: "var(--d-4)" } },
      branches.map((b, i) => h("div", { key: "b" + i, style: { display: "flex", flexDirection: "column", alignItems: "center", textAlign: "center", gap: "var(--d-1)" } },
        b.title ? h("span", { style: CAP }, edLabel(onEdit, b.editTitle, b.title)) : null,
        h("span", { style: { font: "var(--weight-bold,700) var(--fs-h3)/1 var(--font-display)", color: "var(--accent-gold)", fontVariantNumeric: "tabular-nums" } }, edLabel(onEdit, b.editValue, b.value)),
        b.label ? h("span", { style: CAP }, edLabel(onEdit, b.editLabel, b.label)) : null))),
    h("div", { style: { height: "1px", borderTop: "1.5px dashed var(--accent-gold)", margin: "var(--d-1) 0" } }),
    h("div", { style: { width: "1px", height: "14px", borderLeft: "1.5px dashed var(--accent-gold)", alignSelf: "center" } }),
    h("div", { style: { alignSelf: "center", display: "flex", alignItems: "center", gap: "var(--d-3)" } },
      h("span", { style: Object.assign({}, SOFT_CARD, { padding: "var(--d-3) var(--d-5)", font: "var(--weight-bold,700) var(--fs-h2)/1 var(--font-display)", color: "var(--accent-gold)", fontVariantNumeric: "tabular-nums" }) }, edLabel(onEdit, total.editValue, total.value)),
      total.label ? h("span", { style: { font: "var(--weight-medium,500) var(--fs-body)/1.3 var(--font-body)", color: "var(--ink-2)", maxWidth: "14ch" } }, edLabel(onEdit, total.editLabel, total.label)) : null));
}

// PROGRESSIVE-FIDELITY stepper (flow×timeline, capital-raise p22): a VERTICAL
// pill stepper with interstitial mini-nodes (durations / "Revision") paired to
// media tiles whose render fidelity ESCALATES with the step (the LOD/loading
// axis made visible). fidelity bars = i+1 of n.
function fidelityView(graph, onEdit) {
  const steps = graph.steps || [];
  const n = steps.length;
  return h("div", { className: "cv-diagram cv-diagram--fidelity", style: { display: "grid", gridTemplateColumns: "minmax(140px, 0.8fr) 1fr", columnGap: "var(--d-5)", rowGap: "var(--d-2)", alignItems: "stretch", width: "100%" } },
    steps.map((st, i) => [
      st.inter ? h("div", { key: "i" + i, style: { gridColumn: "1", justifySelf: "center", font: "var(--weight-semibold,600) var(--fs-meta)/1 var(--font-body)", color: "var(--ink-3)", background: "var(--zone-ground)", border: "1px solid var(--hairline-strong)", borderRadius: "999px", padding: "2px 10px", margin: "2px 0" } }, edLabel(onEdit, st.editInter, st.inter)) : null,
      h("div", { key: "p" + i, style: Object.assign({ gridColumn: "1", display: "flex", flexDirection: "column", gap: "2px", padding: "var(--d-3) var(--d-4)", borderRadius: "var(--r-md)", border: "1.5px solid var(--accent-gold)", background: "color-mix(in oklch, " + RAMP[Math.min(i, RAMP.length - 1)] + " 18%, var(--zone-ground))" }) },
        h("span", { style: { font: "var(--weight-bold,700) var(--fs-caption)/1.15 var(--font-body)", color: "var(--ink)" } }, edLabel(onEdit, st.editLabel, st.label)),
        st.text ? h("span", { style: { font: "var(--weight-regular,400) var(--fs-meta)/1.35 var(--font-body)", color: "var(--ink-3)" } }, edLabel(onEdit, st.editText, st.text)) : null),
      h("div", { key: "m" + i, style: { gridColumn: "2", gridRow: "auto", position: "relative", borderRadius: "var(--r-md)", overflow: "hidden", minHeight: "58px",
        backgroundColor: "color-mix(in oklch, var(--pig-content) 8%, var(--zone-ground))",
        backgroundImage: "repeating-linear-gradient(45deg, transparent 0 " + (12 - i * 2) + "px, color-mix(in oklch, var(--ink) " + (4 + i * 2) + "%, transparent) " + (12 - i * 2) + "px " + (13 - i * 2) + "px)",
        opacity: (0.55 + 0.45 * (n > 1 ? i / (n - 1) : 1)), display: "grid", placeItems: "end start" } },
        h("span", { style: { margin: "6px", font: "var(--weight-medium,500) var(--fs-meta)/1.1 var(--font-mono)", color: "var(--ink-3)", display: "flex", gap: "2px", alignItems: "center" } },
          Array.from({ length: n }, (_, k) => h("span", { key: k, style: { width: "6px", height: "6px", borderRadius: "1px", background: k <= i ? "var(--accent-gold)" : "var(--hairline-strong)" } })),
          h("span", { style: { marginLeft: "4px" } }, edLabel(onEdit, st.editImage, st.image || "render")))),
    ]));
}


// GLYPHGRAPH view (G5): a laid-out MEANING-graph. Each node is a FULL GLYPHIC
// (CV_GLYPHIC.render — not a shape-clip); each edge carries its meaning VISUALLY
// via CV_SHAPES.edgeSVG (positioned mode): line-style = mood, colour = state,
// routing = the line-type, arrow = direction. EDGE LABELS ARE OFF BY DEFAULT —
// the read sits in a <title> (native hover tooltip, zero layout) and, when
// graph.labels is on (a labels-mode), a small chip at the edge midpoint. The graph
// MUST read from the visual facets alone (Tim: "otherwise it's not the language").
// Reuses the SAME layout() positions (the 320 viewBox) as the rest of the solver.
function glyphGraphView(graph) {
  const GL = (typeof window !== "undefined") && window.CV_GLYPHIC;
  const SH = (typeof window !== "undefined") && window.CV_SHAPES;
  const ME = (typeof window !== "undefined") && window.CV_MEANING;
  if (!GL || !SH) throw new Error("glyphgraph: CV_GLYPHIC + CV_SHAPES must be loaded (the glyphic + geometry single sources)");
  const pos = layout(graph);
  const nodeSize = graph.nodeSize || 58;                 // glyphic px; sized down for >4 nodes below
  const n = graph.nodes.length;
  const size = n > 6 ? 44 : n > 4 ? 50 : nodeSize;       // shrink so a busy graph doesn't overlap
  const labelsOn = !!graph.labels;                       // off by DEFAULT

  // edges first (under the nodes). Each resolves its facets + the per-edge line COLOUR (state)
  // through the SAME path the inline relation uses: CV_MEANING.field('lineColor', v).token → token.
  const EDGES = (typeof window !== "undefined") && window.CV_EDGES;
  const edgeEls = (graph.edges || []).map((e, i) => {
    const a = pos[e.from], b = pos[e.to];
    if (!a || !b) return null;
    const ef = EDGES ? EDGES.resolve({ kind: e.kind, line: e.line, direction: e.direction }) : { line: e.line || "solid", direction: e.direction || "to", kind: e.kind };
    // line ROUTING (right-angled/curved/free) is an edge facet too; default straight.
    const routing = e.routing || "straight";
    // per-edge colour = the lineColor STATE field's token (loud on a present-unknown value).
    let color;
    if (e.lineColor && e.lineColor !== "neutral" && ME && ME.field) {
      const lf = ME.field("lineColor", e.lineColor);     // throws on unknown (loud-fail law)
      const tokenName = lf.token || e.lineColor;
      // reuse the glyphic colour-token map (single source) — token NAME → CSS via CV_GLYPHIC.
      color = tokenForName(tokenName);
    }
    // the read-out for THIS edge (its title — hover reveal, never drawn by default). Use a
    // 2-node readGraph on this edge's endpoints — the CLEAN transglyph clause ("this owner is
    // part of the project"), NOT describeRelation's facet-narration (which fails the octagon oracle).
    let title = "";
    try {
      if (ME && ME.readGraph) {
        title = ME.readGraph({ nodes: [nodeSpec(graph, e.from), nodeSpec(graph, e.to)],
          edges: [{ from: e.from, to: e.to, line: e.line, kind: e.kind, direction: e.direction, lineColor: e.lineColor }] }).sentence;
      }
    } catch (titleErr) {                                 // a hover title is a nicety — don't blank the graph,
      title = "";                                        // but DON'T swallow silently (no-silent-failure law):
      if (typeof console !== "undefined") console.warn("glyphgraph: edge title read-out failed for", e, "—", titleErr && titleErr.message);
    }
    const gap = size * 0.52;                             // stop the line at the glyphic edge, not the centre
    const svg = SH.edgeSVG({ line: ef.line, direction: ef.direction, ink: ef.ink, routing },
      { from: a, to: b, gapFrom: gap, gapTo: gap, color, title, width: 1.8 });
    return h("g", { key: "e" + i, dangerouslySetInnerHTML: { __html: svg } });
  }).filter(Boolean);

  // optional label chips (labels-mode only) at edge midpoints. Chip text = explicit label, else
  // the relation's MEANING (the edge field's feeling: "part of" / "the face of") — never the raw
  // kind id. The chip is a REVEAL; the graph already reads without it.
  const labelEls = labelsOn ? (graph.edges || []).map((e, i) => {
    const a = pos[e.from], b = pos[e.to]; if (!a || !b) return null;
    const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
    let txt = e.label;
    if (!txt && e.kind && ME && ME.field) { try { txt = ME.field("edge", e.kind).feeling; } catch (_) { txt = e.kind; } }
    if (!txt) return null;
    return h("div", { key: "lbl" + i, style: { position: "absolute", left: (mx / VB * 100) + "%", top: (my / VB * 100) + "%", transform: "translate(-50%,-50%)",
      font: "var(--weight-semibold,600) var(--fs-meta)/1 var(--font-body)", color: "var(--ink-3)", background: "var(--zone-ground)", border: "1px solid var(--hairline)", borderRadius: "var(--r-sm,6px)", padding: "1px 6px", whiteSpace: "nowrap", pointerEvents: "none" } }, txt);
  }).filter(Boolean) : [];

  const nodeEls = graph.nodes.map((nd) => {
    const p = pos[nd.id]; if (!p) return null;
    const html = GL.render(nd, { size });                // FULL glyphic — facets read at node top-level
    return h("div", { key: nd.id, title: (function () { try { return ME && ME.referent ? ME.referent(nd) : ""; } catch (_) { return ""; } })(),
      style: { position: "absolute", left: (p.x / VB * 100) + "%", top: (p.y / VB * 100) + "%", transform: "translate(-50%,-50%)", lineHeight: 0 },
      dangerouslySetInnerHTML: { __html: html } });
  }).filter(Boolean);

  return h("div", { className: "cv-diagram cv-diagram--glyphgraph", style: { position: "relative", width: "100%", aspectRatio: "1 / 1", maxWidth: "440px", margin: "0 auto" } },
    h("svg", { className: "dgm-layer", viewBox: `0 0 ${VB} ${VB}`, preserveAspectRatio: "none", style: { position: "absolute", inset: 0, width: "100%", height: "100%", overflow: "visible" } }, edgeEls),
    labelEls,
    nodeEls);
}
// node spec (top-level facets) by id — fed to readGraph/describeRelation unchanged.
function nodeSpec(graph, id) { return (graph.nodes || []).find(nd => nd.id === id) || {}; }
// resolve a colour-token NAME (clay/sage/gold/amber/bronze…) → its CSS, via the glyphic colour
// token map (single source). CV_GLYPHIC.colorForValue takes an allocated VALUE; here we already
// have the token NAME from the lineColor field, so map it through the same COLOR_TOKENS table.
function tokenForName(name) {
  const G = (typeof window !== "undefined") && window.CV_GLYPHIC;
  // CV_GLYPHIC.colorForValue(value) routes value→token→CSS; for a raw token name the identity
  // path (tok) applies — colorForValue falls through to tok(name) when the value isn't allocated.
  if (G && G.colorForValue) return G.colorForValue(name);
  return name;
}

export function DiagramSolver(props) {
  const { graph, onEdit } = props;
  if (!graph) return null;
  if (graph.type === "glyphgraph") return glyphGraphView(graph);

  // ---- CHEVRON STEPPER (DIAGRAMS.md type 4 subtype) -----------------
  // A horizontal sequence of chevron segments; the accent slides ALONG
  // the gold→bronze ramp by position (vt-family: ramp = a variant-theming
  // parameter). `graph.active` (index) fills steps up to & including it.
  if (graph.type === "stepper") {
    const steps = graph.nodes;
    const active = graph.active == null ? steps.length - 1 : graph.active;
    return h("div", { className: "cv-stepper", style: { display: "flex", width: "100%", gap: "2px" } },
      steps.map((nd, i) => {
        const on = i <= active;
        const tint = RAMP[Math.min(i, RAMP.length - 1)];
        const first = i === 0, last = i === steps.length - 1;
        const notch = "13px";
        // interlocking chevron: arrow tip on the right (except last = flat),
        // concave notch on the left (except first = flat)
        const pts = [
          "0 0",
          last ? "100% 0" : "calc(100% - " + notch + ") 0",
          last ? null : "100% 50%",
          last ? "100% 100%" : "calc(100% - " + notch + ") 100%",
          "0 100%",
          first ? null : notch + " 50%",
        ].filter(Boolean);
        return h("div", { key: nd.id || i, style: {
          flex: "1 1 0", minWidth: 0, position: "relative",
          marginLeft: first ? 0 : "-" + notch,
          display: "flex", alignItems: "center", justifyContent: "center", gap: "var(--d-1)",
          padding: "var(--d-3) var(--d-4) var(--d-3) " + (first ? "var(--d-4)" : "calc(var(--d-4) + " + notch + ")"),
          font: "var(--weight-semibold,600) var(--fs-caption)/1.1 var(--font-body)",
          color: on ? "var(--ink)" : "var(--ink-3)", textAlign: "center",
          background: on
            ? "color-mix(in oklch, " + tint + " 34%, var(--zone-ground))"
            : "color-mix(in oklch, var(--pig-content) calc(3% * var(--zone-intensity)), var(--zone-ground))",
          boxShadow: on ? "inset 0 0 0 1px color-mix(in oklch, " + tint + " 60%, transparent)" : "inset 0 0 0 1px var(--hairline)",
          clipPath: "polygon(" + pts.join(",") + ")",
        } },
          edLabel(onEdit, nd.edit, nd.label || nd.id, { className: "truncate", style: { maxWidth: "100%" } }));
      }));
  }

  // ---- NEW SUB-TYPE VIEWS (capital-raise) — early HTML returns ------
  if (graph.type === "orbital")  return orbitalView(graph, onEdit);
  if (graph.type === "stacked")  return stackedView(graph, onEdit);
  if (graph.type === "spectrum") return spectrumView(graph, onEdit);
  if (graph.type === "manifold") return manifoldView(graph, onEdit);
  if (graph.type === "fidelity") return fidelityView(graph, onEdit);

  // the SVG graph path needs a node list; node-less specs were dispatched above.
  if (!graph.nodes) return null;
  const pos = layout(graph);
  const NODE = 52;            // node box px in viewbox units

  const edges = (graph.edges || []).map((e, i) => {
    const a = pos[e.from], b = pos[e.to];
    if (!a || !b) return null;
    const kind = e.kind || "flow";
    const marker = kind === "flow" ? "url(#cv-arrow)" : kind === "communication" ? "url(#cv-arrow-comm)" : kind === "bidirectional" ? "url(#cv-arrow)" : undefined;
    return h("path", { key: "e" + i, className: EDGE_CLASS[kind] || EDGE_CLASS.flow,
      d: `M ${a.x} ${a.y} L ${b.x} ${b.y}`, markerEnd: marker,
      markerStart: kind === "bidirectional" ? "url(#cv-arrow-back)" : undefined });
  }).filter(Boolean);

  const nodeEls = graph.nodes.map((nd) => {
    const p = pos[nd.id]; if (!p) return null;
    const isCenter = (graph.center || (graph.type === "hub" && graph.nodes[0].id)) === nd.id;
    const shapeStyle = (SHAPE[nd.shape] || SHAPE.circle)();
    return h("div", { key: nd.id,
      style: {
        position: "absolute", left: (p.x / VB * 100) + "%", top: (p.y / VB * 100) + "%",
        transform: "translate(-50%,-50%)",
        width: (isCenter ? NODE + 10 : NODE) + "px", height: (isCenter ? NODE + 10 : NODE) + "px",
        display: "grid", placeItems: "center", textAlign: "center",
        background: TONE_FILL[nd.tone || (isCenter ? "active" : "warm")],
        boxShadow: isCenter ? "var(--glow-active)" : "var(--elev-1)",
        border: "1px solid " + (isCenter ? "var(--vi-edge)" : "var(--dgm-node-edge)"),
        font: "var(--weight-semibold,600) var(--fs-caption)/1.1 var(--font-body)",
        color: "var(--ink)", padding: "var(--d-1)", boxSizing: "border-box",
        ...shapeStyle,
        transition: "left var(--dur-move,280ms) var(--ease-emphasized), top var(--dur-move,280ms) var(--ease-emphasized)",
      } },
      (function () {
        const ic = nd.icon && typeof window !== "undefined" && window.CV_ICONS && window.CV_ICONS.data && window.CV_ICONS.data[nd.icon];
        const label = edLabel(onEdit, nd.edit, nd.label || nd.id, { key: "l", className: "truncate", style: { maxWidth: "100%", fontSize: ic ? "0.82em" : "1em" } });
        if (!ic) return label;
        return [
          h("svg", { key: "i", viewBox: "0 0 24 24", width: 16, height: 16, fill: "none", stroke: isCenter ? "var(--ink)" : "var(--accent-bronze)", strokeWidth: 1.5, strokeLinecap: "round", strokeLinejoin: "round", dangerouslySetInnerHTML: { __html: ic } }),
          label,
        ];
      })());
  }).filter(Boolean);

  // quadrant axes
  const axisEls = graph.type === "quadrant" && graph.axes ? [
    h("div", { key: "ax", style: { position: "absolute", inset: 0, pointerEvents: "none" } },
      h("div", { style: { position: "absolute", left: "50%", top: "6%", bottom: "6%", width: "1px", background: "var(--dgm-stroke-color-faint)" } }),
      h("div", { style: { position: "absolute", top: "50%", left: "6%", right: "6%", height: "1px", background: "var(--dgm-stroke-color-faint)" } }),
      h("span", { style: { position: "absolute", right: "2%", top: "50%", transform: "translateY(-50%)", font: "600 var(--fs-caption) var(--font-body)", color: "var(--ink-3)" } }, graph.axes[0]),
      h("span", { style: { position: "absolute", left: "50%", top: "1%", transform: "translateX(-50%)", font: "600 var(--fs-caption) var(--font-body)", color: "var(--ink-3)" } }, graph.axes[1]),
    )] : [];

  return h("div", { className: "cv-diagram", style: { position: "relative", width: "100%", aspectRatio: "1 / 1", maxWidth: "440px", margin: "0 auto" } },
    h("svg", { className: "dgm-layer", viewBox: `0 0 ${VB} ${VB}`, preserveAspectRatio: "none", style: { position: "absolute", inset: 0, width: "100%", height: "100%", overflow: "visible" } },
      h("defs", null,
        h("marker", { id: "cv-arrow", markerWidth: 8, markerHeight: 8, refX: 6, refY: 3, orient: "auto", markerUnits: "strokeWidth" },
          h("path", { d: "M0,0 L6,3 L0,6 z", fill: "var(--accent-gold)" })),
        h("marker", { id: "cv-arrow-back", markerWidth: 8, markerHeight: 8, refX: 0, refY: 3, orient: "auto", markerUnits: "strokeWidth" },
          h("path", { d: "M6,0 L0,3 L6,6 z", fill: "var(--accent-gold)" })),
        h("marker", { id: "cv-arrow-comm", markerWidth: 8, markerHeight: 8, refX: 6, refY: 3, orient: "auto", markerUnits: "strokeWidth" },
          h("path", { d: "M0,0 L6,3 L0,6 z", fill: "var(--comm-line, #7CA85B)" }))),
      edges),
    axisEls,
    nodeEls);
}

if (typeof window !== "undefined") window.__cvDiagramSolver = DiagramSolver;
export default DiagramSolver;
