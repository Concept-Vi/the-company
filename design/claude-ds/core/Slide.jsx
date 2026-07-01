// core/Slide.jsx
// ------------------------------------------------------------
// THE ARCHETYPE LAYER (analysis/AXES.md capstone, DIAGRAMS.md, SYNTHESIS-PLAN §4).
// "Slides ARE templates": a slide archetype is a FIXED Section/Zone/Cluster
// subtree with CONTENT AS DATA (proven by the duplicate "Our Entry Markets"
// slides). So an archetype here is a PURE FUNCTION  content -> CVNode tree —
// not a hand-laid-out layout. The same content at a different lod/surface/
// density is recomputed by the block solver:  design = f(content, axisPosition).
//
// The 13 corpus archetypes (pitch-deck §6) + the diagram/stepper archetypes
// are registered in ARCHETYPES. <Slide archetype="…" content={…} lod surface
// density/> builds the tree and renders it through the block solver (which
// hands diagram nodes to the graph solver). Token-pure by construction: the
// builders emit only typed nodes, the solvers emit only token-backed styles —
// generated output inherits the DNA and cannot drift (INTEGRATION.md).
//
// JSX-free; read in cards/templates via const { Slide, Archetypes } = window.<NS>
/* global React */
const h = React.createElement;

// ---- tiny node constructors (a tree is plain data) ----------------
const band    = (title, children, extra) => ({ kind: "band", title, children: children.filter(Boolean), ...extra });
const section = (title, children, extra) => ({ kind: "section", title, children: children.filter(Boolean), ...extra });
const zone    = (title, children, extra) => ({ kind: "zone", title, children: (children || []).filter(Boolean), ...extra });
const cluster = (flow, children, extra) => ({ kind: "cluster", flow, children: children.filter(Boolean), ...extra });
const atom    = (role, props) => ({ kind: "atom", role, ...props });
const diagram = (graph) => ({ kind: "diagram", graph });
const note    = (text, priority) => text ? atom("note", { text, priority: priority || 2, detail: "support" }) : null;

// bullets[] -> bullet atoms. Each item: string | {title,text,bullet,priority}
function bullets(items, kindDefault) {
  return (items || []).map((it, i) => {
    const o = typeof it === "string" ? { text: it } : it;
    return atom("bullet", { bullet: o.bullet || kindDefault || "dot", title: o.title, text: o.text,
      priority: o.priority || (i < 2 ? 1 : 2), detail: o.detail });
  });
}
// metrics[] -> metric/hero-number atoms. item: {value,label,priority}
function metrics(items, role) {
  return (items || []).map((m, i) => atom(role || "metric", { value: m.value, label: m.label, priority: m.priority || (i === 0 ? 1 : 2) }));
}

// ---- the archetype registry: content -> CVNode (a Band) -----------
const ARCHETYPES = {
  // 1 · full-bleed photographic cover — logo lockup + bronze subtitle
  cover: (c = {}) => band(c.title || "Title", [
    c.image ? zone(null, [atom("image", { label: c.image, ratio: c.ratio || "21 / 9" })], { tone: "warm" }) : null,
    section(null, [
      c.kicker ? note(c.kicker, 1) : null,
      c.subtitle ? atom("text", { text: c.subtitle, priority: 1 }) : null,
    ]),
  ]),

  // 2 · split visual/content — bleeding visual left, title+bullets+note right
  split: (c = {}) => band(c.title, [
    cluster("split", [
      zone(null, [atom("image", { label: c.visual || "diagram", ratio: c.ratio || "4 / 5" })]),
      section(c.heading, [...bullets(c.bullets, c.bulletKind), note(c.note)]),
    ], { split: c.split }),
  ]),

  // 3 · centered title + lede + body — the workhorse statement slide
  statement: (c = {}) => band(c.title, [
    section(null, [
      c.lede ? atom("text", { text: c.lede, priority: 1 }) : null,
      c.body ? atom("text", { text: c.body, priority: 2, detail: "support" }) : null,
      note(c.note),
    ]),
  ]),

  // 4 · two-panel compare — soft panels + italic synthesis footer
  compare: (c = {}) => {
    const pane = (p, tone) => zone(p && p.title, [
      p && p.image ? atom("image", { label: p.image }) : null,
      ...bullets(p && p.bullets, c.bulletKind),
      p && p.caption ? note(p.caption) : null,
    ], { tone });
    return band(c.title, [
      cluster("split", [pane(c.left, "warm"), pane(c.right, "neutral")], { split: "1fr 1fr" }),
      note(c.note),
    ]);
  },

  // 5 · mode columns — parallel screenshot columns + captions
  modes: (c = {}) => band(c.title, [
    cluster("grid", (c.columns || []).map((col) =>
      zone(col.title, [atom("image", { label: col.image || "screen" }), col.caption ? note(col.caption) : null]))),
    note(c.note),
  ]),

  // 6 · triptych cards — 3 columns, 2 warm + 1 neutral
  triptych: (c = {}) => band(c.title, [
    cluster("grid", (c.cards || []).map((card, i) =>
      zone(card.title, [
        card.image ? atom("image", { label: card.image }) : null,
        card.value ? atom("hero-number", { value: card.value, label: card.metricLabel }) : null,
        ...bullets(card.bullets, c.bulletKind),
      ], { tone: i === 2 ? "neutral" : "warm" }))),
    note(c.note),
  ]),

  // 7 · metric band — full-width row of embossed KPIs
  "metric-band": (c = {}) => band(c.title, [
    cluster("grid", metrics(c.metrics, "hero-number")),
    note(c.note),
  ]),

  // 8 · dual checklist + logo strip
  checklist: (c = {}) => band(c.title, [
    cluster("split", (c.columns || []).map((col) =>
      zone(col.title, bullets((col.items || []).map((it) =>
        (typeof it === "string" ? { text: it, bullet: "done" } : { bullet: "done", ...it })))))),
    c.logos && c.logos.length ? section(c.logosTitle || null, [
      cluster("row", c.logos.map((l) => atom("chip", { text: l }))),
    ]) : null,
    note(c.note),
  ]),

  // 9 · timeline / flow split — a graph diagram (timeline | pipeline) + note
  timeline: (c = {}) => band(c.title, [
    diagram(c.graph || { type: "timeline", nodes: (c.steps || []).map((s, i) => ({ id: "s" + i, label: s })),
      edges: (c.steps || []).slice(1).map((_, i) => ({ from: "s" + i, to: "s" + (i + 1), kind: "flow" })) }),
    note(c.note),
  ]),

  // 10 · profile / feature panel — entity badge + name/role + stats + bullets
  profile: (c = {}) => band(c.title, [
    cluster("split", [
      zone(null, [
        atom("badge", { shape: c.shape || "circle", label: c.initials || c.name }),
        c.name ? atom("text", { text: c.name }) : null,
        c.role ? note(c.role, 1) : null,
      ]),
      section(c.heading, [
        c.stats ? cluster("grid", metrics(c.stats)) : null,
        ...bullets(c.bullets, c.bulletKind),
      ]),
    ], { split: c.split || "38fr 62fr" }),
    note(c.note),
  ]),

  // 11 · terms panels — soft panels w/ a hero-number chip + bullet list
  terms: (c = {}) => band(c.title, [
    cluster("grid", (c.panels || []).map((p) =>
      zone(p.title, [
        p.hero ? atom("hero-number", { value: p.hero.value, label: p.hero.label }) : null,
        ...bullets(p.bullets, c.bulletKind),
      ]))),
    note(c.note),
  ]),

  // 12 · gallery grid — lede + tiled image placeholders
  gallery: (c = {}) => band(c.title, [
    c.lede ? section(null, [atom("text", { text: c.lede, priority: 1 })]) : null,
    cluster("grid", (c.items || []).map((it) => atom("image", { label: typeof it === "string" ? it : it.label }))),
    note(c.note),
  ]),

  // 13 · contact / closing — info card + action pills
  closing: (c = {}) => band(c.title, [
    cluster("split", [
      zone(null, (c.lines || []).map((l) =>
        atom("bullet", { bullet: "dot", title: l.label, text: l.value }))),
      section(null, [
        c.subtitle ? atom("text", { text: c.subtitle, priority: 1 }) : null,
        c.actions && c.actions.length ? cluster("row", c.actions.map((a) => atom("chip", { text: a }))) : null,
      ]),
    ], { split: c.split || "54fr 46fr" }),
    note(c.note),
  ]),

  // + chevron stepper (DIAGRAMS.md type 4) — ramp-tinted stage progression
  stepper: (c = {}) => band(c.title, [
    diagram({ type: "stepper", active: c.active, nodes: (c.steps || []).map((s, i) => ({ id: "s" + i, label: s })) }),
    c.lede ? section(null, [atom("text", { text: c.lede })]) : null,
    note(c.note),
  ]),

  // + bare diagram archetype — host any graph spec (hub/network/morph/…) with a title
  diagram: (c = {}) => band(c.title, [
    c.lede ? section(null, [atom("text", { text: c.lede, priority: 1 })]) : null,
    diagram(c.graph),
    note(c.note),
  ]),

  // section divider (chapter break) — a prominent title band, optional kicker
  section: (c = {}) => band(c.title, [c.kicker ? note(c.kicker, 1) : null, c.subtitle ? atom("text", { text: c.subtitle }) : null]),

  // ============ capital-raise archetypes (slice 28) ============

  // product-cover — full-bleed live-product surface + frosted title lockup (p1)
  "product-cover": (c = {}) => band(null, [
    cluster("overlay", [
      atom("image", { label: c.image || "full-bleed product surface (panotour viewer)", cover: true, edit: "image" }),
      zone(null, [
        c.kicker ? atom("logo", { label: c.kicker, edit: "kicker" }) : null,
        c.title ? atom("headline", { text: c.title, edit: "title" }) : null,
        c.subtitle ? note(c.subtitle, 1) : null,
      ], { frosted: true, place: c.place || "center end" }),
    ]),
  ], { bleed: true }),

  // product-closing — full-bleed product surface + frosted contact card (p30)
  "product-closing": (c = {}) => band(null, [
    cluster("overlay", [
      atom("image", { label: c.image || "full-bleed product surface", cover: true, edit: "image" }),
      zone(null, [
        c.kicker ? atom("logo", { label: c.kicker, edit: "kicker" }) : null,
        c.subtitle ? atom("headline", { text: c.subtitle, edit: "subtitle" }) : null,
        ...(c.lines || []).map((l, i) => atom("bullet", { bullet: "dot", title: l.label, text: l.value, editTitle: "lines." + i + ".label", editText: "lines." + i + ".value" })),
      ], { frosted: true, place: c.place || "end start" }),
    ]),
  ], { bleed: true }),

  // photo-divider — full-bleed photographic section break, single word (p20)
  "photo-divider": (c = {}) => band(null, [
    cluster("overlay", [
      atom("image", { label: c.image || "full-bleed section image", cover: true, edit: "image" }),
      zone(null, [atom("headline", { text: c.title || "Section", edit: "title" })], { frosted: true, place: c.place || "start end" }),
    ]),
  ], { bleed: true }),

  // logo-wall — client/partner grid bracketed by hatch-framed stat strips (p11)
  "logo-wall": (c = {}) => band(c.title, [
    c.lede ? section(null, [atom("text", { text: c.lede, priority: 1 })]) : null,
    (c.top && c.top.length) ? cluster("grid", metrics(c.top, "hero-number")) : null,
    cluster("wall", (c.logos || []).map((l, i) => atom("logo", { label: l, edit: "logos." + i }))),
    (c.bottom && c.bottom.length) ? cluster("grid", metrics(c.bottom)) : null,
    note(c.note),
  ]),

  // team — core rows (alternating tint) + advisory icon row + upcoming hires (p16/p17)
  team: (c = {}) => band(c.title, [
    ...(c.core || []).map((m, i) => zone(null, [
      cluster("split", [
        cluster("row", [
          atom("badge", { shape: m.shape || "circle", label: m.initials || m.name }),
          section(null, [m.name ? atom("text", { text: m.name }) : null, m.role ? note(m.role, 1) : null]),
        ]),
        m.credential ? atom("text", { text: m.credential, priority: 2 }) : null,
      ], { split: "44fr 56fr" }),
    ], { tone: i % 2 ? "neutral" : "warm" })),
    (c.advisory && c.advisory.length) ? zone(c.advisoryTitle || "Advisory team", [
      cluster("grid", c.advisory.map((a) => atom("icon", { icon: "person", label: typeof a === "string" ? a : a.label, tone: "bronze" }))),
    ]) : null,
    (c.upcoming && c.upcoming.length) ? section(c.upcomingTitle || "Upcoming hires", [
      cluster("grid", c.upcoming.map((m) => zone(null, [
        atom("badge", { shape: "circle", label: m.initials || m.name }),
        m.name ? atom("text", { text: m.name }) : null, m.role ? note(m.role, 1) : null,
      ]))),
    ]) : null,
    note(c.note),
  ]),

  // dashboard — 2×2 (or N) grid of raised panels, each hosting metrics/chart/
  // bullets/diagram (the deal dashboard + financial chart grid, p15/p19)
  dashboard: (c = {}) => band(c.title, [
    c.lede ? section(null, [atom("text", { text: c.lede, priority: 1 })]) : null,
    cluster("grid", (c.panels || []).map((p) => {
      const kids = [];
      if (p.metrics) kids.push(cluster("grid", metrics(p.metrics)));
      if (p.value) kids.push(atom("hero-number", { value: p.value, label: p.label }));
      if (p.chart) kids.push(atom("chart", { chart: p.chart.kind || "spark", points: p.chart.points, value: p.chart.value, label: p.chart.label }));
      if (p.bullets) bullets(p.bullets, c.bulletKind).forEach((b) => kids.push(b));
      if (p.graph) kids.push(diagram(p.graph));
      return zone(p.title, kids, { raised: true });
    })),
    note(c.note),
  ]),

  // reasons — ramp-bordered card row (stroke steps along the ramp) bridging two
  // summary zones below (the "why now" composition, p18)
  reasons: (c = {}) => band(c.title, [
    c.lede ? section(null, [atom("text", { text: c.lede, priority: 1 })]) : null,
    cluster("grid", (c.cards || []).map((card, i) => atom("ramp-card", { ramp: i, title: card.title, text: card.text, editTitle: "cards." + i + ".title", editText: "cards." + i + ".text" }))),
    (c.zones && c.zones.length) ? cluster("split", c.zones.map((z) => zone(z.title, bullets(z.bullets, c.bulletKind)))) : null,
    note(c.note),
  ]),

  // diagram sub-type archetypes — thin wrappers so each new graph kind is a
  // first-class, catalogued building block (rendered by the graph solver).
  orbital: (c = {}) => band(c.title, [c.lede ? section(null, [atom("text", { text: c.lede, priority: 1 })]) : null, diagram({ type: "orbital", center: c.center, verbs: c.verbs }), note(c.note)]),
  stacked: (c = {}) => band(c.title, [c.lede ? section(null, [atom("text", { text: c.lede, priority: 1 })]) : null, diagram({ type: "stacked", nodes: c.nodes }), note(c.note)]),
  spectrum: (c = {}) => band(c.title, [c.lede ? section(null, [atom("text", { text: c.lede, priority: 1 })]) : null, diagram({ type: "spectrum", ends: c.ends, segments: c.segments, cards: c.cards, hatch: c.hatch }), note(c.note)]),
  manifold: (c = {}) => band(c.title, [c.lede ? section(null, [atom("text", { text: c.lede, priority: 1 })]) : null, diagram({ type: "manifold", branches: c.branches, total: c.total }), note(c.note)]),
  fidelity: (c = {}) => band(c.title, [c.lede ? section(null, [atom("text", { text: c.lede, priority: 1 })]) : null, diagram({ type: "fidelity", steps: c.steps }), note(c.note)]),
};

// app-registry alias keys (the deck-slide Types title/content extend cover/statement)
ARCHETYPES.title = ARCHETYPES.cover;
ARCHETYPES.content = ARCHETYPES.statement;

// build a tree from an archetype name + content (pure; harness-testable). LOUD:
// an unknown archetype throws rather than silently falling back to statement.
function buildSlide(archetype, content) {
  const fn = ARCHETYPES[archetype];
  if (!fn) throw new Error("[Slide] unknown archetype: " + archetype + " (known: " + Object.keys(ARCHETYPES).join(", ") + ")");
  return fn(content || {});
}

// public registry handle (capitalised → exposed on the namespace)
const Archetypes = {
  list: Object.keys(ARCHETYPES),
  build: buildSlide,
  register(name, fn) { ARCHETYPES[name] = fn; },
};

// ---- the consumer-facing component --------------------------------
// Slide is the deck-slide case of RenderType (UNIFICATION.md W1): one render
// path. LOUD: requires the bridge to be loaded — no silent fallback.
export function Slide(props) {
  const { archetype = "statement", content } = props;
  const RT = typeof window !== "undefined" && window.__cvRenderType;
  if (!RT) throw new Error("[Slide] RenderType bridge not loaded — unification broken (load core/RenderType.jsx)");
  return h(RT, { type: { id: "surface.deck-slide." + archetype, layer: "surface", family: "deck-slide", runtime: { kind: "core-archetype", key: archetype } }, data: content, lod: props.lod, surface: props.surface || "slide", density: props.density, motion: props.motion, register: props.register, loading: props.loading });
}

if (typeof window !== "undefined") { window.__cvSlide = Slide; window.__cvArchetypes = Archetypes; }
export { Archetypes };
export default Slide;
