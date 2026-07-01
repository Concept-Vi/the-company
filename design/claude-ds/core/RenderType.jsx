// core/RenderType.jsx
// ------------------------------------------------------------
// THE BRIDGE (analysis/UNIFICATION.md W1). Welds the two halves that were
// built in isolation: the TYPE SYSTEM (app/registry CV_REGISTRY — layers,
// inheritance, slots, the Vi generator) and the RULE ENGINE (the core block
// & graph solvers, f(content, axis)). It does ONE job: resolve a registry
// Type + its data into the solver IR (a CVNode / CVGraph), then render it
// through the one engine under the axis-dials. No new design — it reuses the
// existing archetype builders (window.__cvArchetypes) and atom registry.
//
//   CV_REGISTRY Type ──typeToNode──▶ CVNode IR ──ContainmentTree/DiagramSolver──▶ DNA-pure output
//
// `CoreTypes` exposes the core's archetypes + atoms AS registry-shaped Type
// seeds, so the app's registry single-sources its catalogue from the bundle
// instead of declaring parallel stubs (UNIFICATION W2). JSX-free; read via
// const { RenderType, CoreTypes } = window.<NS>
/* global React */
const h = React.createElement;

const idTail = (id) => String(id || "").split(".").pop();
// register / pace meta-dial (REQUIREMENTS C3): presenter↔reader sets LOD +
// density + motion together — but any explicit prop overrides it (separable).
const REGISTER = {
  presenter: { lod: "pitch", density: "compact",     motion: true },
  reader:    { lod: "full",  density: "comfortable", motion: false },
};
const keyOf = (type) => (type && type.runtime && type.runtime.key) || idTail(type && type.id) || type;

// ---- block/atom Type → CVNode IR, using ONLY existing atom roles + the graph
// solver (a faithful re-expression of the WHOLE WS_BLOCKS taxonomy in the core
// vocabulary — the atom/block weld, UNIFICATION W3; no new atom invented).
function blockToNode(key, d) {
  d = d || {};
  const items = d.items || [];
  const A = (role, o) => Object.assign({ kind: "atom", role }, o);
  const clu = (flow, kids) => ({ kind: "cluster", flow, children: kids.filter(Boolean) });
  const zn = (title, kids, extra) => Object.assign({ kind: "zone", title, children: (kids || []).filter(Boolean) }, extra);
  const dia = (graph) => ({ kind: "diagram", graph });
  const flowEdges = (n) => Array.from({ length: Math.max(0, n - 1) }, (_, i) => ({ from: "s" + i, to: "s" + (i + 1), kind: "flow" }));

  switch (key) {
    // ---- text & simple ----
    case "headline":  return { kind: "section", title: d.text || d.headline, editTitle: "text", children: d.eyebrow ? [A("note", { text: d.eyebrow, edit: "eyebrow" })] : [] };
    case "body":      return A("text", { text: d.text, edit: "text" });
    case "quote": case "pullquote": case "bigQuote":
      return A("note", { text: (d.text || d.lead || "") + (d.who ? " — " + d.who : "") });
    case "callout":   return zn(d.label, [A("text", { text: d.text, edit: "text" })], { editTitle: "label" });
    case "button":    return A("chip", { text: d.text, edit: "text" });
    case "divider":   return null;
    case "image":     return A("image", { label: d.label || d.imageLabel, edit: d.label != null ? "label" : "imageLabel" });
    case "imageGrid": case "showcase":
      return clu("grid", items.map((it, i) => A("image", { label: typeof it === "string" ? it : it.label, edit: typeof it === "string" ? "items." + i : "items." + i + ".label" })));

    // ---- lists & chip rows ----
    case "bullets":   return clu("col", items.map((t, i) => A("bullet", { bullet: "dot", text: typeof t === "string" ? t : t.text, edit: typeof t === "string" ? "items." + i : "items." + i + ".text" })));
    case "checklist": return zn(d.title, items.map((t, i) => A("bullet", { bullet: "done", text: typeof t === "string" ? t : t.text, edit: typeof t === "string" ? "items." + i : "items." + i + ".text" })), { editTitle: "title" });
    case "icons": case "chipRow": case "iconStrip":
      return clu("row", items.map((it, i) => A("chip", { text: typeof it === "string" ? it : (it.label || it.text || it), edit: typeof it === "string" ? "items." + i : "items." + i + ".label" })));
    case "palette":   return clu("row", (d.colors || []).map((c, i) => A("chip", { text: c.n || c.h, edit: "colors." + i + ".n" })));
    case "pillars":   return { kind: "section", title: d.subtitle, editTitle: "subtitle", children: [clu("row", items.map((t, i) => A("chip", { text: typeof t === "string" ? t : t.label, edit: typeof t === "string" ? "items." + i : "items." + i + ".label" })))] };
    case "logoStrip": return { kind: "section", title: d.title, editTitle: "title", children: [clu("row", (d.logos || []).map((l, i) => A("chip", { text: l, edit: "logos." + i })))] };

    // ---- metrics ----
    case "stats":     return clu("grid", items.map((m, i) => A("metric", { value: m.v || m.value, label: m.l || m.label, editValue: "items." + i + ".v", editLabel: "items." + i + ".l" })));
    case "statPills": return clu("row", items.map((m, i) => A("metric", { value: m.v || m.value, label: m.l || m.label, editValue: "items." + i + ".v", editLabel: "items." + i + ".l" })));
    case "metricRow": return clu("grid", items.map((m, i) => A("hero-number", { value: m.v || m.value, label: m.l || m.label, editValue: "items." + i + ".v", editLabel: "items." + i + ".l" })));
    case "featureCards": return clu("grid", items.map((it, i) => zn(it.title, [it.stat ? A("hero-number", { value: it.stat, editValue: "items." + i + ".stat" }) : null, it.body ? A("text", { text: it.body, edit: "items." + i + ".body" }) : null], Object.assign({ editTitle: "items." + i + ".title" }, i === 2 ? { tone: "neutral" } : null))));
    case "labeledCard": return zn(d.title, (d.lines || []).map((ln, i) => A("bullet", { bullet: "dot", title: ln.stat, text: ln.body, editTitle: "lines." + i + ".stat", editText: "lines." + i + ".body" })), { editTitle: "title" });
    case "statTable": return zn(d.title, [d.hero ? A("hero-number", { value: d.hero.v || d.hero.value, label: d.hero.l || d.hero.label, editValue: "hero.v", editLabel: "hero.l" }) : null, clu("grid", (d.rows || []).map((r, i) => A("metric", { value: r.v, label: r.l, editValue: "rows." + i + ".v", editLabel: "rows." + i + ".l" })))], { editTitle: "title" });

    // ---- people / contact / badges ----
    case "bio":       return clu("split", [zn(null, [A("badge", { shape: "circle", label: d.avatarInitials || d.initials }), d.name ? A("text", { text: d.name, edit: "name" }) : null, d.role ? A("note", { text: d.role, edit: "role" }) : null]), clu("grid", (d.stats || []).map((s, i) => A("metric", { value: s.v, label: s.l, editValue: "stats." + i + ".v", editLabel: "stats." + i + ".l" })))]);
    case "photoBio":  return clu("grid", items.map((p, i) => zn(null, [A("badge", { shape: "circle", label: p.initials }), p.name ? A("text", { text: p.name, edit: "items." + i + ".name" }) : null, p.desc ? A("note", { text: p.desc, edit: "items." + i + ".desc" }) : null])));
    case "contactCard": return zn(d.brand, (d.lines || []).map((ln, i) => A("bullet", { bullet: "dot", title: ln.label, text: ln.value, editTitle: "lines." + i + ".label", editText: "lines." + i + ".value" })), { editTitle: "brand" });
    case "hexBadge":  return clu("row", items.map((it) => A("badge", { shape: "hex", label: (it.label || "").replace(/\n/g, " "), caption: it.version })));

    // ---- side-by-side ----
    case "comparison": return clu("split", [
      zn(d.left && d.left.title, [d.left && d.left.label ? A("image", { label: d.left.label, edit: "left.label" }) : null, d.left && d.left.caption ? A("note", { text: d.left.caption, edit: "left.caption" }) : null], { editTitle: "left.title" }),
      zn(d.right && d.right.title, [d.right && d.right.label ? A("image", { label: d.right.label, edit: "right.label" }) : null, d.right && d.right.caption ? A("note", { text: d.right.caption, edit: "right.caption" }) : null], { tone: "neutral", editTitle: "right.title" }),
    ]);
    case "hero": return clu("split", [
      { kind: "section", title: null, children: [d.eyebrow ? A("note", { text: d.eyebrow, edit: "eyebrow" }) : null, d.headline ? A("text", { text: d.headline, edit: "headline" }) : null, d.body ? A("text", { text: d.body, edit: "body" }) : null, d.cta ? A("chip", { text: d.cta, edit: "cta" }) : null].filter(Boolean) },
      zn(null, [A("image", { label: d.imageLabel || d.label || "image", edit: "imageLabel" })]),
    ]);

    // ---- diagrams → the graph solver ----
    case "process":   return dia({ type: "pipeline", nodes: (d.steps || []).map((s, i) => ({ id: "s" + i, label: s.title || s.stage || s.label, edit: "steps." + i + ".title" })), edges: flowEdges((d.steps || []).length) });
    case "funnel":    return dia({ type: "pipeline", nodes: (d.steps || []).map((s, i) => ({ id: "s" + i, label: s.label, shape: s.shape === "hex" ? "hex" : s.shape === "circle" ? "circle" : "square", edit: "steps." + i + ".label" })), edges: flowEdges((d.steps || []).length) });
    case "timeline":  return dia({ type: "timeline", nodes: (d.milestones || []).map((m, i) => ({ id: "m" + i, label: m.label, edit: "milestones." + i + ".label" })) });
    case "tagCluster": { const labels = (d.branches || []).flatMap((b) => (b.items || []).map((it) => it.label)); return dia({ type: "hub", center: "hub", nodes: [{ id: "hub", label: d.hub, shape: "square", tone: "active" }].concat(labels.map((l, i) => ({ id: "n" + i, label: l }))), edges: labels.map((_, i) => ({ from: "hub", to: "n" + i, kind: "flow" })) }); }
    case "orgDiagram": { const ns = d.nodes || []; return dia({ type: "hub", center: "hub", nodes: [{ id: "hub", label: (d.hub && d.hub.label) || "Vi", shape: (d.hub && d.hub.shape) || "diamond", tone: "active", edit: "hub.label" }].concat(ns.map((n, i) => ({ id: "n" + i, label: (n.label || "").replace(/\n/g, " "), shape: n.shape || "circle", edit: "nodes." + i + ".label" }))), edges: ns.map((_, i) => ({ from: "hub", to: "n" + i, kind: "flow" })) }); }

    // ---- cross-doc embeds belong to the widget/wizard engine, not the slide solver ----
    case "embedWidget": case "embedWizard":
      throw new Error("[typeToNode] block '" + key + "' is a cross-doc embed — rendered by the widget engine (WidgetRender), not the slide solver");

    default:          return A("text", { text: d.text || d.headline || d.label || "" });
  }
}

// ---- the bridge: a resolved registry Type (+ instance data) → solver IR ----
// Returns { node } for the block solver, or { nodes:[…] } for a doc sequence.
function typeToNode(type, data, axis) {
  if (!type) return { node: { kind: "atom", role: "text", text: "" } };
  const content = data || type.defaults || {};
  const key = keyOf(type);

  // surface · deck-slide  → an archetype band (render = the archetype builder)
  if (type.layer === "surface" && type.family === "deck-slide") {
    const A = typeof window !== "undefined" && window.__cvArchetypes;
    if (!A) throw new Error("[typeToNode] archetype builders (window.__cvArchetypes) not loaded — unification broken");
    return { node: A.build(key, content) };
  }
  // doc  → a sequence of slide/section Types (its `slides`/`sections`/`pages` data)
  if (type.layer === "doc") {
    const seq = content.slides || content.sections || content.pages || [];
    const nodes = seq.map((s) => typeToNode(
      { layer: "surface", family: "deck-slide", runtime: { key: s.archetype || s.kind || "statement" } },
      s.content || s.data || s, axis).node);
    return { nodes };
  }
  // graph-bearing Type (a diagram) → diagram node straight to the graph solver
  if (content.graph) return { node: { kind: "diagram", graph: content.graph } };
  // widget (system/surface, family widget) → a Zone tile (REQUIREMENTS F2: the
  // product UI is the same containment tree). Charts/deltas are placeholders
  // until a dataviz atom lands (W7).
  if ((type.layer === "system" || type.layer === "surface") && type.family === "widget") {
    return { node: widgetToNode(content) };
  }
  // block / atom  → the core atom vocabulary
  return { node: blockToNode(key, content) };
}

// widget doc {system, data:{eyebrow,title,kpis,rows,media,chart,cta}} → a Zone tile.
function widgetToNode(doc) {
  doc = doc || {};
  const d = doc.data || doc;
  const sys = doc.system || "kpi";
  const A = (role, o) => Object.assign({ kind: "atom", role }, o);
  const clu = (flow, kids) => ({ kind: "cluster", flow, children: kids.filter(Boolean) });
  const kids = [];
  if (d.eyebrow) kids.push(A("note", { text: d.eyebrow }));
  if ((sys === "media" || sys === "hybrid") && d.media) kids.push(A("image", { label: d.media.label || "media", ratio: "16 / 9" }));
  if ((sys === "kpi" || sys === "hybrid") && (d.kpis || []).length)
    kids.push(clu("grid", d.kpis.map((k) => A("metric", { value: k.value, label: k.label, delta: k.delta, deltaKind: k.deltaKind }))));
  if (d.chart) kids.push(A("chart", { chart: "spark", points: d.chart.points || [], label: d.chart.label }));
  if (sys === "hybrid" && (d.rows || []).length)
    kids.push(clu("col", d.rows.map((r) => A("bullet", { bullet: "dot", title: r.label, text: r.value }))));
  if (d.cta) kids.push(A("chip", { text: (d.cta && d.cta.label) || d.cta }));
  // bodyOnly: just the data-viz body (kpis/media/chart/rows) for a host that
  // supplies its own frame/header/cta chrome (e.g. WidgetRender).
  if (doc.__bodyOnly) return clu("col", kids.filter((n) => n.role !== "note" && n.role !== "chip"));
  return { kind: "zone", title: d.title, raised: true, children: kids };
}

// ---- React entry point -------------------------------------------
// Accepts a resolved `type` object, OR (`typeId` + a `registry` to resolve in,
// defaulting to CoreTypes). Renders via the one engine under the axis-dials.
export function RenderType(props) {
  const { type, typeId, registry, data, surface = "slide", onEdit = null, register } = props;
  const rg = REGISTER[register] || {};
  const lod = props.lod || rg.lod || "full";
  const density = props.density || rg.density || "comfortable";
  const motion = props.motion != null ? props.motion : (rg.motion != null ? rg.motion : false);
  const loading = !!props.loading;
  const CT = typeof window !== "undefined" && window.__cvContainmentTree;
  const DS = (typeof window !== "undefined" && window.__cvDiagramSolver) || null;
  // LOUD: the one engine must be present. No placeholder, no silent skip.
  if (!CT) throw new Error("[RenderType] core engine (window.__cvContainmentTree) not loaded — unification broken");

  const reg = registry || (typeof window !== "undefined" && window.CV_REGISTRY) || CoreTypes;
  const resolved = type || (reg && reg.resolve ? reg.resolve(typeId) : (reg && reg.get ? reg.get(typeId) : null));
  if (!resolved) throw new Error("[RenderType] type not found: " + typeId);

  const axis = { lod, surface, density };
  const ir = typeToNode(resolved, data, axis);
  const render = (node, k) => node ? h(CT, { key: k, node, lod, surface, density, DiagramSolver: DS, onEdit, motion, loading }) : null;
  if (ir.nodes) return h("div", { style: { display: "flex", flexDirection: "column", gap: "var(--d-8)" } }, ir.nodes.map(render).filter(Boolean));
  return render(ir.node, "n");
}

// ============================================================
//  CoreTypes — the core's archetypes as registry-shaped Type SEEDS, read from
//  the SINGLE-SOURCE catalogue (core/archetype-catalog.js → window.CV_ARCHETYPE_CATALOG).
//  The app's types-seed.js seeds FROM the same module, so the catalogue is not
//  duplicated (UNIFICATION W2). If the catalogue script isn't on the page
//  (e.g. a lean template), fall back to minimal seeds derived from the live
//  archetype builder list.
// ============================================================
function archetypeSeeds() {
  // LOUD: the single-source catalogue must be loaded (core/archetype-catalog.js).
  if (typeof window === "undefined" || !window.CV_ARCHETYPE_CATALOG) {
    throw new Error("[CoreTypes] archetype catalogue not loaded — include core/archetype-catalog.js");
  }
  return window.CV_ARCHETYPE_CATALOG;
}

const CoreTypes = {
  /** registry-shaped Type seeds for the core archetypes (+ later: atoms). */
  archetypeSeeds,
  seeds() { return archetypeSeeds(); },
  /** seed a CV_REGISTRY instance from the core catalogue (UNIFICATION W2). */
  seedInto(R) { if (R && R.registerMany) R.registerMany(this.seeds(), { silent: true }); return this.seeds(); },
  /** minimal standalone lookup so RenderType works without the app registry. */
  get(id) { return this.seeds().find((t) => t.id === id) || null; },
  resolve(id) { return this.get(id); },
};

if (typeof window !== "undefined") { window.__cvRenderType = RenderType; window.__cvTypeToNode = typeToNode; }
export { CoreTypes, typeToNode };
export default RenderType;
