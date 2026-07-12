// core/ContainmentTree.jsx
// ------------------------------------------------------------
// THE BLOCK SOLVER (analysis/AXES.md). Takes a CVNode tree + an axis
// position and computes the laid-out containment ladder. Layout is by
// nesting + flow; the zone wash is computed from nesting DEPTH (passed
// down, not hand-set). LOD prunes/grows the tree before layout.
//
// Atom rendering is a REGISTRY (ATOM_RENDERERS), not a chain of if-
// branches — so a new atom is DATA (register a role) not a code edit
// (analysis/HANDOFF §8). Roles ship: metric · hero-number · bullet ·
// chip · badge · note · qr · text. Extend via ContainmentTree.registerAtom.
//
// Pure of literals: every class/var it emits resolves to a design-system
// token. JSX-free (h = createElement) so the binding is unambiguous in
// the compiled bundle. Read in cards via: const { ContainmentTree } = window.<NS>
/* global React */
const h = React.createElement;

// ---- LOD rule: a cutoff on narrative priority + whether "support" shows
const LOD_RULES = {
  summary: { maxPriority: 1, support: false },
  pitch:   { maxPriority: 2, support: false },
  full:    { maxPriority: 99, support: true },
};

function visibleAtLOD(node, lod) {
  const rule = LOD_RULES[lod] || LOD_RULES.full;
  if ((node.priority || 1) > rule.maxPriority) return false;          // prune low-priority
  if (node.detail === "support" && !rule.support) return false;       // drop justification
  return true;
}

const BULLET = { dot: "\u25B8", leads: "\u2192", done: "\u2713" };    // ▸ → ✓

// ---- Entity shape vocabulary (the brand's shape system) -----------
//  circle = User Portal · hex = Property Wizard · octagon = Virtual
//  Hubs · diamond = Vi. Shared with the graph solver.
//  CANONICAL SOURCE: assets/icons/cv-shapes.js (window.CV_SHAPES). The literal
//  below is a byte-identical FALLBACK for the compiled bundle (keep in sync).
const SHAPE_CLIP = (typeof window !== "undefined" && window.CV_SHAPES && window.CV_SHAPES.clip())
  || {
  circle:  null,                                                       // border-radius 50% via style
  square:  null,
  hex:     "polygon(25% 0,75% 0,100% 50%,75% 100%,25% 100%,0 50%)",
  octagon: "polygon(29% 0,71% 0,100% 29%,100% 71%,71% 100%,29% 100%,0 71%,0 29%)",
  diamond: "polygon(50% 0,100% 50%,50% 100%,0 50%)",
};

// ---- inline-edit helper (W6) — when the tree is rendered with an onEdit
// callback, text-bearing leaves become contentEditable and commit on blur to
// the data path the block solver tagged them with (node.edit* fields). Same
// uncontrolled commit-on-blur pattern the app's editor uses (no cursor thrash).
let CURRENT_ONEDIT = null;
let CURRENT_MOTION = false;
let CURRENT_LOADING = false;   // resolve, never pop (states.css §10): render leaves as .skeleton while data streams in
// entrance wave (E1 "nothing teleports") — when motion is on, stagger a
// container's children in via .enter-up; end-state is the base style, so motion
// OFF (composer/registry/print/reduced-motion) just shows static content.
function withMotion(kids) {
  if (!CURRENT_MOTION) return kids;
  return kids.map((k, i) => (k && k.type) ? React.cloneElement(k, {
    className: ((k.props.className || "") + " enter-up").trim(),
    style: Object.assign({}, k.props.style, { animationDelay: "calc(min(" + i + ", var(--stagger-max)) * var(--stagger-step))" }),
  }) : k);
}

// SPACE↔TIME (REQUIREMENTS E2) — a cluster with mode:"time" plays its children
// one at a time over time instead of showing them all in space. Same subtree,
// two renderings; the budget is spent in time, not space.
function TimePlayer(props) {
  const items = props.items || [];
  const n = items.length;
  const [i, setI] = React.useState(0);
  const cur = Math.min(i, Math.max(0, n - 1));
  const btn = { font: "var(--weight-semibold) var(--fs-body) var(--font-body)", width: "28px", height: "28px", borderRadius: "50%", border: "1px solid var(--hairline-strong)", background: "var(--zone-ground)", color: "var(--ink-2)", cursor: "pointer" };
  return h("div", { style: { display: "flex", flexDirection: "column", gap: "var(--d-3)", minWidth: 0 } },
    h("div", { className: "moves", style: { minWidth: 0 } }, items[cur]),
    h("div", { style: { display: "flex", gap: "var(--d-2)", alignItems: "center" } },
      h("button", { style: Object.assign({}, btn, cur === 0 ? { opacity: 0.4, cursor: "default" } : null), onClick: () => setI(x => Math.max(0, x - 1)) }, "\u2039"),
      h("span", { style: { font: "var(--weight-medium) var(--fs-caption)/1 var(--font-mono)", color: "var(--ink-3)" } }, (cur + 1) + " / " + n),
      h("button", { style: Object.assign({}, btn, cur >= n - 1 ? { opacity: 0.4, cursor: "default" } : null), onClick: () => setI(x => Math.min(n - 1, x + 1)) }, "\u203A"),
      h("div", { style: { display: "flex", gap: "5px", marginLeft: "auto" } },
        items.map((_, j) => h("span", { key: j, onClick: () => setI(j), style: { width: "7px", height: "7px", borderRadius: "50%", cursor: "pointer", background: j === cur ? "var(--accent-gold)" : "var(--hairline-strong)" } })))));
}

// PROGRESSIVE DISCLOSURE (REQUIREMENTS F1) — a node can be shown at low LOD with
// a toggle that raises it to full in place. Local LOD = expand a section.
function Disclose(props) {
  const [open, setOpen] = React.useState(false);
  const link = { alignSelf: "flex-start", font: "var(--weight-semibold) var(--fs-caption)/1 var(--font-body)", color: "var(--accent-gold)", background: "none", border: "none", padding: "var(--d-1) 0", cursor: "pointer" };
  return h("div", { style: { display: "flex", flexDirection: "column", gap: "var(--d-3)", minWidth: 0 } },
    open ? props.full : props.summary,
    h("button", { style: link, onClick: () => setOpen(o => !o) }, open ? "\u2212 Show less" : "+ Show more"));
}
function edit(path, content, props, tag) {
  tag = tag || "span";
  const txt = content == null ? "" : content;
  const oe = CURRENT_ONEDIT;
  props = props || {};
  if (oe && path != null) {
    return h(tag, Object.assign({}, props, { contentEditable: true, suppressContentEditableWarning: true, spellCheck: false,
      onFocus: (e) => { if (typeof window !== "undefined" && window.__cvFieldFocus) window.__cvFieldFocus({ el: e.currentTarget, value: txt, path, apply: (nv) => oe(path, nv) }); },
      onBlur: (e) => { const v = e.currentTarget.textContent; if (v !== String(txt)) oe(path, v); },
      onKeyDown: (e) => { if (e.key === "Enter" && tag !== "p") { e.preventDefault(); e.currentTarget.blur(); } } }), txt);
  }
  return h(tag, props, txt);
}

// ---- Atom renderers, keyed by role (the leaf templates) -----------
// Each is (node, key) => element. A role with no renderer falls back to text.
const ATOM_RENDERERS = {
  // number+label — the sacred, LOD-locked payload. gold tabular number.
  metric(node, key) {
    return h("div", { key, className: "cv-atom", style: { display: "flex", flexDirection: "column", gap: "var(--d-1)" } },
      edit(node.editValue, node.value, { style: {
        font: "var(--weight-bold) var(--fs-h2)/1 var(--font-display)",
        color: "var(--accent-gold)", fontVariantNumeric: "tabular-nums",
        letterSpacing: "var(--tracking-tight)",
      } }),
      node.label ? edit(node.editLabel, node.label, { style: {
        font: "var(--weight-medium) var(--fs-caption)/1.3 var(--font-body)",
        color: "var(--ink-3)", textWrap: "balance",
      } }) : null,
      node.delta ? h("span", { style: {
        font: "var(--weight-semibold) var(--fs-meta)/1 var(--font-body)",
        color: node.deltaKind === "down" ? "var(--zone-reject-ink)" : "var(--zone-success-ink)",
      } }, (node.deltaKind === "down" ? "\u25BC " : "\u25B2 ") + node.delta) : null,
    );
  },

  // data-viz leaf — sparkline (default) · bar · gauge, drawn from the tokenised
  // dataviz language (tokens/dataviz.css). node.points (spark) or node.value 0–100
  // (bar/gauge). Gold is the key series. Atomises what was tokens-only (W7).
  chart(node, key) {
    const kind = node.chart || "spark";
    if (kind === "bar") {
      return h("div", { key, className: "cv-atom", style: { display: "flex", flexDirection: "column", gap: "var(--d-1)" } },
        h("div", { className: "viz-bar", style: { "--val": node.value || 0 } }, h("div", { className: "fill" })),
        node.label ? h("span", { style: { font: "var(--weight-medium) var(--fs-caption)/1.3 var(--font-body)", color: "var(--ink-3)" } }, node.label) : null);
    }
    if (kind === "gauge") {
      return h("div", { key, className: "cv-atom", style: { display: "flex", alignItems: "center", gap: "var(--d-2)" } },
        h("div", { className: "viz-gauge", style: { "--val": node.value || 0 } }, (node.value || 0) + "%"),
        node.label ? h("span", { style: { font: "var(--weight-medium) var(--fs-caption)/1.3 var(--font-body)", color: "var(--ink-3)" } }, node.label) : null);
    }
    const pts = (node.points || []).map(Number);
    const W = 100, H = 28;
    const max = Math.max.apply(null, pts.concat([1])), min = Math.min.apply(null, pts.concat([0]));
    const span = (max - min) || 1;
    const xy = pts.map((p, i) => ((pts.length < 2 ? 0 : (i / (pts.length - 1)) * W)).toFixed(1) + "," + (H - ((p - min) / span) * H).toFixed(1));
    return h("div", { key, className: "cv-atom", style: { display: "flex", flexDirection: "column", gap: "var(--d-1)" } },
      h("svg", { className: "viz-spark", viewBox: "0 0 " + W + " " + H, preserveAspectRatio: "none", style: { width: "100%", height: "36px" } },
        pts.length ? h("polygon", { className: "area", points: "0," + H + " " + xy.join(" ") + " " + W + "," + H }) : null,
        pts.length ? h("polyline", { points: xy.join(" ") }) : null),
      node.label ? h("span", { style: { font: "var(--weight-medium) var(--fs-caption)/1.3 var(--font-mono)", color: "var(--ink-3)" } }, node.label) : null);
  },

  // embossed hero metric — a raised/inset light chip (texture & depth §13).
  // Bigger than `metric`; the deck's "$430B" / "70+" treatment.
  "hero-number"(node, key) {
    return h("div", { key, className: "cv-atom", style: {
      display: "flex", flexDirection: "column", gap: "var(--d-1)",
      alignItems: "center", textAlign: "center",
      padding: "var(--d-4) var(--d-5)", borderRadius: "var(--r-lg)",
      background: "var(--zone-ground)",
      boxShadow: "var(--elev-2), inset 0 1px 0 rgba(255,255,255,.6)",
    } },
      edit(node.editValue, node.value, { style: {
        font: "var(--weight-bold) var(--fs-display)/0.95 var(--font-display)",
        color: "var(--accent-gold)", fontVariantNumeric: "tabular-nums",
        letterSpacing: "var(--tracking-tight)",
      } }),
      node.label ? edit(node.editLabel, node.label, { style: {
        font: "var(--weight-medium) var(--fs-caption)/1.3 var(--font-body)",
        color: "var(--ink-2)", textWrap: "balance",
      } }) : null,
    );
  },

  bullet(node, key) {
    const mark = BULLET[node.bullet || "dot"];
    const isLeads = node.bullet === "leads";
    return h("div", { key, className: "cv-atom", style: { display: "flex", gap: "var(--d-2)", alignItems: "baseline" } },
      h("span", { style: { color: isLeads ? "var(--accent-gold)" : "var(--accent-bronze)", flex: "none", fontSize: "0.85em", lineHeight: "1.5" } }, mark),
      h("div", { style: { minWidth: 0 } },
        node.title ? edit(node.editTitle, node.title, { style: { font: "var(--weight-semibold) var(--fs-body)/1.4 var(--font-body)", color: "var(--ink)", marginRight: node.text ? "0.35em" : 0 } }) : null,
        node.text ? edit(node.editText, node.text, { className: "measure", style: { font: "var(--weight-regular) var(--fs-body)/1.5 var(--font-body)", color: node.title ? "var(--ink-3)" : "var(--ink-2)" } }) : null,
      ),
    );
  },

  chip(node, key) {
    return h("span", { key, className: "cv-atom pill",
      style: { background: "var(--zone-ground)", boxShadow: "inset 0 0 0 1px var(--vi-edge)", color: "var(--ink-2)" } },
      edit(node.edit, node.text || node.label, { className: "pill-label" }));
  },

  // entity-shape badge — the brand's signature shape system, rendered as a
  // leaf. node.shape ∈ circle|hex|octagon|diamond; Vi (diamond) gets the
  // "Vᵢ" wordmark with the gold subscript i.
  badge(node, key) {
    const shape = node.shape || "circle";
    const clip = SHAPE_CLIP[shape];
    const isVi = shape === "diamond";
    const face = h("div", { style: {
      width: "var(--badge-size)", height: "var(--badge-size)", flex: "none",
      display: "grid", placeItems: "center", textAlign: "center",
      background: node.tone === "active" ? "var(--vi-surface)"
        : "color-mix(in oklch, var(--pig-content) calc(5% * var(--zone-intensity)), var(--zone-ground))",
      boxShadow: node.tone === "active" ? "var(--glow-active)" : "var(--elev-1)",
      border: "1px solid " + (node.tone === "active" ? "var(--vi-edge)" : "var(--dgm-node-edge)"),
      borderRadius: shape === "circle" ? "50%" : "var(--r-sm)",
      clipPath: clip || undefined,
    } },
      isVi
        ? h("span", { style: { font: "var(--weight-bold) var(--fs-h3)/1 var(--font-display)", color: "var(--ink)" } },
            "V", h("sub", { style: { color: "var(--accent-gold)", fontSize: "0.7em" } }, "i"))
        : h("span", { style: { font: "var(--weight-semibold) var(--fs-caption)/1.05 var(--font-body)", color: "var(--ink)", padding: "0 4px" } }, node.label || node.title));
    // caption below the shape only when explicitly given (else the shape carries the label inside)
    if (!node.caption) return h("div", { key, className: "cv-atom", style: { display: "flex", justifyContent: "center" } }, face);
    return h("div", { key, className: "cv-atom", style: { display: "flex", flexDirection: "column", gap: "var(--d-1)", alignItems: "center", textAlign: "center" } },
      face,
      h("span", { style: { font: "var(--weight-semibold) var(--fs-caption)/1.2 var(--font-body)", color: "var(--ink-2)", textWrap: "balance" } }, node.caption));
  },

  // italic bronze synthesis line — the connective tissue between scenes
  // (pitch-deck §10). A distinct register from body copy.
  note(node, key) {
    return edit(node.edit, node.text || node.title || "", { key, className: "cv-atom measure", style: {
      font: "italic var(--weight-medium) var(--fs-meta)/1.5 var(--font-display)",
      color: "var(--accent-bronze)", margin: 0, textWrap: "pretty",
    } }, "p");
  },

  // phygital "Virtual Tour" QR card (recent-pitches) — placeholder square +
  // outlined caption. The print/screen → live-tour bridge.
  qr(node, key) {
    return h("div", { key, className: "cv-atom", style: {
      display: "flex", flexDirection: "column", gap: "var(--d-2)", alignItems: "center",
      padding: "var(--d-3)", borderRadius: "var(--r-md)",
      boxShadow: "inset 0 0 0 1px var(--hairline-strong)", background: "var(--zone-ground)",
    } },
      h("div", { style: {
        width: "var(--qr-size)", height: "var(--qr-size)", borderRadius: "var(--r-sm)",
        backgroundColor: "var(--zone-ground)",
        backgroundImage: "repeating-conic-gradient(var(--ink-3) 0% 25%, var(--zone-ground) 0% 50%)",
        backgroundSize: "16px 16px", opacity: 0.5,
      } }),
      h("span", { style: { font: "var(--weight-semibold) var(--fs-caption)/1.2 var(--font-body)", color: "var(--ink-2)", textTransform: "uppercase", letterSpacing: "var(--tracking-caps)" } }, node.label || node.text || "Virtual tour"),
    );
  },

  // brand logo placeholder — a bordered wordmark tile (logo wall / partner band /
  // proposal cards). Never a fetched mark; the brand NAME set in a neutral tile.
  logo(node, key) {
    return h("div", { key, className: "cv-atom", style: {
      display: "grid", placeItems: "center", minHeight: "var(--logo-h)", padding: "var(--d-2) var(--d-3)",
      borderRadius: "var(--r-sm)", background: "var(--zone-ground)", boxShadow: "inset 0 0 0 1px var(--hairline)",
    } },
      h("span", { style: { font: "var(--weight-semibold) var(--fs-caption)/1.1 var(--font-body)", color: "var(--ink-3)", textAlign: "center", letterSpacing: "var(--tracking-snug)" } }, edit(node.edit, node.label || node.text || "Logo", null)));
  },

  // ramp-bordered reason card (capital-raise p18) — an outline card whose STROKE
  // steps along the gold→bronze ramp by node.ramp (0..3), so a row of them reads
  // as a sequence/heat. The ramp encodes order on a BORDER, not a fill.
  "ramp-card"(node, key) {
    const tint = ["var(--ramp-1)", "var(--ramp-2)", "var(--ramp-3)", "var(--ramp-4)"][Math.min(node.ramp || 0, 3)];
    return h("div", { key, className: "cv-atom", style: {
      display: "flex", flexDirection: "column", gap: "var(--d-1)", textAlign: "center",
      padding: "var(--d-3) var(--d-4)", borderRadius: "var(--r-md)", background: "var(--zone-ground)",
      boxShadow: "inset 0 0 0 1.5px color-mix(in oklch, " + tint + " 72%, transparent), var(--elev-1)",
    } },
      node.title ? h("span", { style: { font: "var(--weight-bold) var(--fs-body)/1.2 var(--font-display)", color: "var(--ink)" } }, edit(node.editTitle, node.title, null)) : null,
      node.text ? edit(node.editText, node.text, { className: "measure", style: { font: "var(--weight-regular) var(--fs-caption)/1.45 var(--font-body)", color: "var(--ink-3)" } }) : null);
  },

  // image / media placeholder — striped sunken tile + mono caption of what
  // belongs there (never a hand-drawn illustration).
  image(node, key) {
    const cover = node.cover;
    return h("div", { key, className: "cv-atom",
      // RATIO-FIT LAW: a real asset's box IS its measured ratio — stamped by
      // the one law (core/layout-fit.js) when src is given; the declared ratio
      // is only the pre-measure/placeholder fallback.
      ref: node.src && typeof window !== "undefined" && window.CV_LAYOUT_FIT
        ? ((el) => { if (el && !el.__cvArStamped) { el.__cvArStamped = 1; window.CV_LAYOUT_FIT.stampMedia(el, node.src); } })
        : undefined,
      style: {
      width: "100%", height: cover ? "100%" : undefined, aspectRatio: cover ? undefined : "" + (node.ratio || "var(--asset-ar)") + "", borderRadius: cover ? 0 : "var(--r-md)",
      display: "grid", placeItems: "center", overflow: "hidden",
      backgroundColor: "var(--bg-sunken)",
      backgroundImage: "repeating-linear-gradient(45deg, transparent 0 11px, color-mix(in oklch, var(--ink) 5%, transparent) 11px 12px)",
    } },
      h("span", { style: { font: "var(--weight-medium) var(--fs-caption)/1.2 var(--font-mono)", color: "var(--ink-3)", textAlign: "center", padding: "var(--d-2)" } }, edit(node.edit, node.label || node.text || "image", null)));
  },

  // icon — first-class content (DIAGRAMS.md): a CV icon from window.CV_ICONS,
  // in the icon language (24-grid, 1.5px stroke, currentColor → tone). Optional label.
  icon(node, key) {
    const data = (typeof window !== "undefined" && window.CV_ICONS && window.CV_ICONS.data) || {};
    const body = data[node.icon || node.text || node.label];
    const sz = node.size || 26;
    const tone = node.tone === "gold" ? "var(--accent-gold)" : node.tone === "ink" ? "var(--ink)" : "var(--accent-bronze)";
    return h("div", { key, className: "cv-atom", style: { display: "flex", flexDirection: "column", gap: "var(--d-1)", alignItems: "center", minWidth: 0 } },
      body
        ? h("svg", { viewBox: "0 0 24 24", width: sz, height: sz, fill: "none", stroke: tone, strokeWidth: 1.5, strokeLinecap: "round", strokeLinejoin: "round", dangerouslySetInnerHTML: { __html: body } })
        : h("div", { style: { width: sz + "px", height: sz + "px", borderRadius: "var(--r-sm)", boxShadow: "inset 0 0 0 1px var(--dgm-node-edge)" } }),
      node.label ? edit(node.editLabel, node.label, { style: { font: "var(--weight-medium) var(--fs-caption)/1.2 var(--font-body)", color: "var(--ink-3)", textAlign: "center" } }) : null);
  },

  // default: a line / paragraph of text
  text(node, key) {
    return edit(node.edit, node.text || node.title || "", { key, className: "cv-atom measure",
      style: { font: "var(--weight-regular) var(--fs-body)/1.55 var(--font-body)", color: "var(--ink-2)", margin: 0 } }, "p");
  },

  // display-weight title for an overlay/divider (product cover/closing, photo
  // divider) — bigger than `text`, the cover/section title treatment.
  headline(node, key) {
    return edit(node.edit, node.text || node.title || "", { key, className: "cv-atom", style: {
      font: "var(--weight-bold) var(--fs-h2)/var(--lh-tight) var(--font-display)",
      color: "var(--ink)", letterSpacing: "var(--tracking-tight)", margin: 0, textWrap: "balance",
    } }, "h2");
  },
};

function roleFor(node) {
  if (node.role && ATOM_RENDERERS[node.role]) return node.role;
  if (node.value != null) return "metric";
  if (node.bullet) return "bullet";
  return "text";
}

function renderAtom(node, key) {
  if (CURRENT_LOADING) return skeletonFor(node, key);
  return ATOM_RENDERERS[roleFor(node)](node, key);
}

// FOCUS / dim-the-rest (focus.css) — a container with node.focus (a child id or
// index) becomes a .focus-scope.is-focusing: the named child lifts ([data-focus]),
// the rest recede (desaturate/dim/blur). Spatial attention as a mechanism.
function applyFocus(node, kids) {
  if (node.focus == null) return { focusing: false, kids };
  const children = node.children || [];
  const tagged = kids.map((k, i) => {
    const src = children[i] || {};
    const isSubject = node.focus === i || (src.id != null && node.focus === src.id);
    return (k && k.type) ? React.cloneElement(k, isSubject ? { "data-focus": "" } : {}) : k;
  });
  return { focusing: true, kids: tagged };
}

// shaped skeleton placeholder for a leaf while its data resolves. Shape follows
// the role so the layout doesn't jump when real content swaps in (with .enter-*).
function skeletonFor(node, key) {
  const role = roleFor(node);
  if (role === "metric") return h("div", { key, className: "cv-atom", style: { display: "flex", flexDirection: "column", gap: "var(--d-1)" } },
    h("div", { className: "skeleton", style: { width: "2.2em", height: "1.4em" } }),
    h("div", { className: "skeleton text", style: { width: "4.5em" } }));
  if (role === "icon" || role === "badge") return h("div", { key, className: "skeleton circle", style: { width: "26px", height: "26px" } });
  if (role === "image" || role === "chart" || role === "qr") return h("div", { key, className: "skeleton", style: { width: "100%", aspectRatio: role === "qr" ? "1" : "16/9", borderRadius: "var(--r-md)" } });
  // text / bullet / note: a couple of shimmer lines
  return h("div", { key, className: "cv-atom", style: { display: "flex", flexDirection: "column", gap: "var(--d-1)", width: "100%" } },
    h("div", { className: "skeleton text", style: { width: "100%" } }),
    h("div", { className: "skeleton text", style: { width: "72%" } }));
}

// ---- Recursive container walk -------------------------------------
function renderNode(node, axis, depth, key, DiagramSolver) {
  if (!node) return null;                       // tolerate a null node/child (e.g. a divider block)
  const lod = axis.lod || "full";
  if (!visibleAtLOD(node, lod)) return null;

  const kids = (node.children || [])
    .map((c, i) => renderNode(c, axis, node.kind === "zone" ? depth + 1 : depth, key + "-" + i, DiagramSolver))
    .filter(Boolean);

  switch (node.kind) {
    case "band":
      return h("section", { key, className: "cv-band" + (node.bleed ? " cv-band--bleed" : ""), "data-surface": axis.surface || "slide", "data-ground": node.ground || undefined, "data-screen-label": node.title },
        node.title ? h("h2", { style: {
          font: "var(--weight-bold) var(--fs-h1)/var(--lh-tight) var(--font-display)",
          color: "var(--ink)", letterSpacing: "var(--tracking-tight)", margin: 0, textWrap: "balance",
        } }, edit(node.editTitle, node.title, null)) : null,
        withMotion(kids));

    case "section": {
      const head = node.title ? h("div", { className: "cv-section-head" }, edit(node.editTitle, node.title, null)) : null;
      // progressive disclosure: at a low LOD, offer to expand this section to full
      if (node.disclose && lod !== "full") {
        const full = (node.children || []).map((c, i) => renderNode(c, Object.assign({}, axis, { lod: "full" }), depth, key + "-f" + i, DiagramSolver)).filter(Boolean);
        if (full.length > kids.length) {
          return h("div", { key, className: "cv-section" }, head, h(Disclose, { summary: kids, full }));
        }
      }
      return h("div", { key, className: "cv-section" }, head, kids);
    }

    case "zone": {
      const auth = node.author;   // human | vi | suggested — authorship is legible (DESIGN-LANGUAGE §11)
      const byLabel = { vi: "Vi", human: "You", suggested: "Suggested" };
      // overlay placement (a frosted panel over a full-bleed image, product
      // cover/closing): node.place = "<align> <justify>" grid keywords.
      const place = node.place ? { alignSelf: node.place.split(" ")[0], justifySelf: node.place.split(" ")[1] || node.place.split(" ")[0] } : null;
      return h("div", { key, className: "cv-zone" + (auth === "vi" ? " vi-authored" : "") + (node.frosted ? " cv-zone--frosted" : ""), "data-tone": node.tone || "warm",
        // THE DEPTH COORDINATE (unification sweep): nesting depth IS the ladder
        // rung — stamped so skins can resolve zones to 3D physics the moment a
        // zone opts into a material surface. Coordinate always; physics binds
        // to .material, so plain tonal zones are visually unchanged.
        "data-depth": String(Math.min(depth + 1, 5)),
        "data-raised": node.raised ? "" : undefined, "data-author": auth || undefined,
        style: Object.assign({ "--zone-depth": depth }, place, node.maxw ? { maxWidth: node.maxw } : null) },
        (node.title || auth) ? h("div", { style: { display: "flex", alignItems: "baseline", gap: "var(--d-2)" } },
          node.title ? h("div", { style: {
            font: "var(--weight-semibold) var(--fs-h4)/1.15 var(--font-display)",
            color: "var(--ink)", margin: 0, flex: 1, minWidth: 0,
          } }, edit(node.editTitle, node.title, null)) : h("span", { style: { flex: 1 } }),
          auth ? h("span", { className: "by by-" + auth, style: { flex: "none" } }, byLabel[auth] || auth) : null
        ) : null,
        kids);
    }

    case "cluster": {
      const colMin = node.flow === "grid" ? { "--col-min": "180px" } : node.flow === "wall" ? { "--col-min": "120px" } : null;
      const splitVar = node.flow === "split" && node.split ? { "--split": node.split } : null;
      if (node.mode === "time") return h(TimePlayer, { key, items: kids });   // play over time, not space
      const fx = applyFocus(node, kids);   // spotlight one child, recede the rest
      return h("div", { key, className: "cv-cluster" + (fx.focusing ? " focus-scope is-focusing" : ""), "data-flow": node.flow || "col", style: { ...colMin, ...splitVar } }, withMotion(fx.kids));
    }

    case "diagram":
      return node.graph && DiagramSolver
        ? h("div", { key, className: "cv-atom", style: { width: "100%" } }, h(DiagramSolver, { graph: node.graph, axis, onEdit: CURRENT_ONEDIT }))
        : null;

    case "atom":
    default:
      return renderAtom(node, key);
  }
}

export function ContainmentTree(props) {
  const { node, lod = "full", surface = "slide", density = "comfortable", DiagramSolver = null, onEdit = null, motion = false, loading = false } = props;
  const axis = { lod, surface, density };
  const prev = CURRENT_ONEDIT, prevM = CURRENT_MOTION, prevL = CURRENT_LOADING;
  CURRENT_ONEDIT = onEdit; CURRENT_MOTION = !!motion; CURRENT_LOADING = !!loading;   // captured per-leaf during this synchronous walk
  // the tree carries the dials as data-attributes so density/LOD re-tune live
  const out = h("div", { "data-density": density, "data-motion": motion ? "" : undefined, "data-loading": loading ? "" : undefined, style: { width: "100%" } },
    renderNode(node, axis, 1, "n", DiagramSolver || (typeof window !== "undefined" && window.__cvDiagramSolver)));
  CURRENT_ONEDIT = prev; CURRENT_MOTION = prevM; CURRENT_LOADING = prevL;
  return out;
}

// data-extensibility: register a new atom role without editing the solver.
ContainmentTree.registerAtom = function (role, fn) { ATOM_RENDERERS[role] = fn; };
ContainmentTree.atomRoles = function () { return Object.keys(ATOM_RENDERERS); };

if (typeof window !== "undefined") window.__cvContainmentTree = ContainmentTree;
export default ContainmentTree;
