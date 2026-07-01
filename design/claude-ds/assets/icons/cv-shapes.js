/**
 * cv-shapes.js — THE single home for the ConceptV SHAPE SYSTEM.
 *
 * Shapes carry TYPED MEANING. A geometric vessel is not decoration — each shape
 * encodes a semantic class (Entity, Action, Object, Decision, Feature, System,
 * Specialised, Gateway). An icon from the ConceptV icon system (cv-icons.js) sits
 * inside the shape; the edge, fill, shadow, thickness and ink all resolve from
 * design tokens via `markDefaults`. Everything is a PARAMETER: there is one default
 * treatment that applies across the design system, and any of it can be overridden
 * per call (or per shape-type).
 *
 *   layer cascade:  markDefaults (tokens)  ◀ shapeType overrides  ◀ markSVG(opts)
 *
 * Connected systems:
 *   - assets/icons/cv-icons.js     → the glyph inside each shape (window.CV_ICONS)
 *   - colors_and_type.css + tokens → every colour/shadow/thickness (var(--…))
 *   - assets/icons/CvIcon.jsx      → entity-badge node shapes (polygon points)
 *   - core/ContainmentTree.jsx     → block/graph solver leaf badges (clip-paths)
 *   - preview/brand_shapes.html    → the "Shape system" specimen (typed meanings)
 *
 * Geometry: TRUE REGULAR polygons (3–8 sides; never more than 8) + circle, authored
 * on a 100×100 box with vertices on a r=50 circle. The sizing rule (markBox) anchors
 * every shape's HEIGHT to one shared circle and lets WIDTH compute, so shapes stay
 * regular (undistorted) and align in a row. Consumers keep a byte-identical FALLBACK
 * so the compiled bundle never hard-fails before this module loads.
 */
(function () {
  // ---- regular n-gon on the 100-box (vertex at top unless rotated) -------
  function ngon(n, rotDeg, R) {
    R = R || 50;
    const rot = (rotDeg || 0) * Math.PI / 180, out = [];
    for (let i = 0; i < n; i++) {
      const a = -Math.PI / 2 + rot + i * 2 * Math.PI / n;
      out.push((50 + R * Math.cos(a)).toFixed(1) + ',' + (50 + R * Math.sin(a)).toFixed(1));
    }
    return out.join(' ');
  }
  function clipFromPoints(pts) {
    return 'polygon(' + pts.split(' ').map(p => { const c = p.split(','); return c[0] + '% ' + c[1] + '%'; }).join(',') + ')';
  }
  // points are INSET (r=46) so a stroked <polygon> (CvIcon, sw 7) has room; the clip-path
  // is FULL-BLEED (r=50) so clipped content fills the cell. markSVG re-fits via roundedFit.
  function poly(sides, rotDeg) { return { kind: 'poly', sides, points: ngon(sides, rotDeg, 46), clip: clipFromPoints(ngon(sides, rotDeg, 50)) }; }

  // Geometry — orientation chosen so each reads "right": triangle/pentagon/heptagon
  // point up, hexagon is pointy-top, octagon flat-top, diamond a square on its point,
  // square axis-aligned. NEVER above 8 sides (a circle is the limit of ∞ sides).
  const geom = {
    circle:   { kind: 'circle', sides: 0 },
    triangle: poly(3, 0),
    square:   poly(4, 45),
    diamond:  poly(4, 0),
    pentagon: poly(5, 0),
    hex:      poly(6, 0),     // key kept as 'hex' for back-compat consumers
    heptagon: poly(7, 0),
    octagon:  poly(8, 22.5),
  };
  geom.hexagon = geom.hex;   // alias

  // ---- TYPED MEANING registry — the semantic layer (one shape = one type) ----
  // Each carries its meaning + description, a default icon (from the icon system),
  // and any treatment overrides (pattern, ink role). These are the system DEFAULTS;
  // every field is a parameter a consumer can override.
  const shapeTypes = [
    { shape: 'circle',   type: 'Entity',       sides: '∞', icon: 'person',
      meaning: 'A whole, continuous thing — a person, account or identity. No edges, no hierarchy: the most complete vessel.' },
    { shape: 'triangle', type: 'Action',       sides: 3,   icon: 'play',
      meaning: 'Direction and momentum — a step, a process, a change of state. The fewest sides: pure intent.' },
    { shape: 'square',   type: 'Object',       sides: 4,   icon: 'file',
      meaning: 'A stable, bounded object — data, a document, a record. Neutral and foundational.' },
    { shape: 'diamond',  type: 'Decision',     sides: 4,   icon: 'atom', pattern: 'lines', ink: 'ink',
      meaning: 'Intelligence and judgement — AI, logic, a branch or pivot. A square turned to attention.' },
    { shape: 'pentagon', type: 'Feature',      sides: 5,   icon: 'star',
      meaning: 'A composed capability — a product feature or module assembled from parts.' },
    { shape: 'hex',      type: 'System',       sides: 6,   icon: 'gear', pattern: 'hatch',
      meaning: 'An engine or configurable system — interlocking building blocks that tile without gaps.' },
    { shape: 'heptagon', type: 'Specialised',  sides: 7,   icon: 'unique',
      meaning: 'A rare, specialised type — reserved for the exceptional case that resists the regular grid.' },
    { shape: 'octagon',  type: 'Gateway',      sides: 8,   icon: 'globe',
      meaning: 'An output, endpoint or boundary — buyer-facing surfaces and terminals. The most sides before the circle.' },
  ];

  // ---- brand ENTITIES (compat layer): instances that adopt a shape type --------
  // Kept so CvIcon / ContainmentTree / decks keep resolving. The brand maps each
  // platform entity to a typed shape; Vi keeps its traced wordmark instead of an icon.
  const entities = [
    { id: 'userPortal',     name: 'User Portal',     shape: 'circle',  role: 'Login & account',      ink: 'bronze', pattern: 'none'  },
    { id: 'propertyWizard', name: 'Property Wizard', shape: 'hex',     role: 'Configuration engine', ink: 'bronze', pattern: 'hatch' },
    { id: 'virtualHubs',    name: 'Virtual Hubs',    shape: 'octagon', role: 'Buyer-facing output',  ink: 'gold',   pattern: 'none'  },
    { id: 'vi',             name: 'Vi',              shape: 'diamond', role: 'AI framework',          ink: 'ink',    pattern: 'lines', wordmark: true },
    { id: 'generic',        name: 'Generic entity',  shape: 'square',  role: 'Fallback',              ink: 'bronze', pattern: 'none'  },
  ];

  const CV_SHAPES = {
    geom,
    shapeTypes,
    entities,
    entity(id) { return entities.find(e => e.id === id) || null; },
    shapeType(key) { return shapeTypes.find(t => t.shape === key || t.type.toLowerCase() === String(key).toLowerCase()) || null; },
    points() { const o = {}; for (const k in geom) if (geom[k].points) o[k] = geom[k].points; return o; },
    clip()   { const o = {}; for (const k in geom) o[k] = geom[k].clip || null; return o; },

    // THE sizing rule (single home): every vessel is anchored to one shared circle.
    // span = the circle's diameter = the common HEIGHT of every mark; each shape is a
    // regular polygon scaled uniformly to that height and centred (width computes).
    markBox: { span: 86, stroke: 2.5, radius: 6, labelSize: 13.5, labelWeight: 700, labelTracking: -0.4 },

    // THE default treatment — every value is a TOKEN (single source: colors_and_type.css
    // + tokens/*). This default applies across the whole design system; any field is a
    // parameter overridable per shape-type or per markSVG call.
    markDefaults: {
      stroke:      'var(--accent-gold)',                              // edge colour
      strokeWidth: 2.5,                                               // in 100-box units (≈ markBox.stroke)
      fill:        ['var(--bg-surface)', 'var(--paper)', 'var(--paper-2)'], // sheen gradient stops
      ink:         'var(--accent-bronze-2)',                          // icon / label colour
      shadow:      { color: 'var(--accent-bronze)', dx: 0.7, dy: 2, blur: 1.8, opacity: 0.22 },
      pattern:     'none',                                            // 'none' | 'hatch' | 'lines'
      iconScale:   0.42,                                              // icon box as fraction of span
    },
    // ink ROLE → token (so a type can say ink:'gold' and stay token-pure)
    inkRole: { bronze: 'var(--accent-bronze-2)', gold: 'var(--accent-gold)', ink: 'var(--fg-primary)' },

    // Pixel-sampled palette from the real brand marks — an OPTIONAL preset for exact
    // reproduction (pass markSVG(.., {preset:'sampled'})); the default is token-pure.
    markPalette: { gold: '#E2C521', goldInk: '#D5B82A', ink: '#837857', fillTop: '#FDFDFC', fillMid: '#F8F8F6', fillBot: '#EEEEEA', shadow: '#5a5038' },
  };

  // ---- geometry helpers --------------------------------------------------
  const SW0 = CV_SHAPES.markBox.stroke, SPAN = CV_SHAPES.markBox.span, INSET = (100 - SPAN) / 2, RAD = CV_SHAPES.markBox.radius;

  function rp(ptsStr, r) {
    const pts = ptsStr.trim().split(/\s+/).map(p => p.split(',').map(Number));
    const n = pts.length, sub = (a, b) => [a[0]-b[0], a[1]-b[1]], len = v => Math.hypot(v[0], v[1]), nrm = v => { const l = len(v) || 1; return [v[0]/l, v[1]/l]; };
    let d = '';
    for (let i = 0; i < n; i++) {
      const p0 = pts[(i-1+n)%n], p1 = pts[i], p2 = pts[(i+1)%n];
      const v1 = nrm(sub(p0, p1)), v2 = nrm(sub(p2, p1));
      const rr = Math.min(r, len(sub(p0, p1))/2, len(sub(p2, p1))/2);
      const a = [p1[0]+v1[0]*rr, p1[1]+v1[1]*rr], b = [p1[0]+v2[0]*rr, p1[1]+v2[1]*rr];
      d += (i === 0 ? `M ${a[0].toFixed(1)} ${a[1].toFixed(1)} ` : `L ${a[0].toFixed(1)} ${a[1].toFixed(1)} `);
      d += `Q ${p1[0]} ${p1[1]} ${b[0].toFixed(1)} ${b[1].toFixed(1)} `;
    }
    return d + 'Z';
  }
  // Round, then anchor the ROUNDED outline's HEIGHT to the shared span (uniform scale →
  // regular/undistorted) and centre it. Returns {d, verts} — verts are the fitted CORNER
  // points, used to find the true centroid + inscribed radius for icon placement.
  function roundedFit(ptsStr, r) {
    const pts = ptsStr.trim().split(/\s+/).map(p => p.split(',').map(Number));
    const n = pts.length, sub = (a, b) => [a[0]-b[0], a[1]-b[1]], len = v => Math.hypot(v[0], v[1]), nrm = v => { const l = len(v) || 1; return [v[0]/l, v[1]/l]; };
    const segs = [];
    for (let i = 0; i < n; i++) {
      const p0 = pts[(i-1+n)%n], p1 = pts[i], p2 = pts[(i+1)%n];
      const v1 = nrm(sub(p0, p1)), v2 = nrm(sub(p2, p1));
      const rr = Math.min(r, len(sub(p0, p1))/2, len(sub(p2, p1))/2);
      segs.push({ A: [p1[0]+v1[0]*rr, p1[1]+v1[1]*rr], V: p1, B: [p1[0]+v2[0]*rr, p1[1]+v2[1]*rr] });
    }
    let mnx = 1e9, mxx = -1e9, mny = 1e9, mxy = -1e9;
    const acc = (x, y) => { mnx = Math.min(mnx, x); mxx = Math.max(mxx, x); mny = Math.min(mny, y); mxy = Math.max(mxy, y); };
    for (const s of segs) { acc(s.A[0], s.A[1]); acc(s.B[0], s.B[1]); acc(0.25*s.A[0]+0.5*s.V[0]+0.25*s.B[0], 0.25*s.A[1]+0.5*s.V[1]+0.25*s.B[1]); }
    const sc = SPAN / (mxy - mny), cx = (mnx + mxx) / 2;
    const FX = x => 50 + (x - cx) * sc, FY = y => INSET + (y - mny) * sc;
    let d = ''; const verts = [];
    for (let i = 0; i < segs.length; i++) { const s = segs[i];
      verts.push([FX(s.V[0]), FY(s.V[1])]);
      d += (i === 0 ? `M ${FX(s.A[0]).toFixed(1)} ${FY(s.A[1]).toFixed(1)} ` : `L ${FX(s.A[0]).toFixed(1)} ${FY(s.A[1]).toFixed(1)} `);
      d += `Q ${FX(s.V[0]).toFixed(1)} ${FY(s.V[1]).toFixed(1)} ${FX(s.B[0]).toFixed(1)} ${FY(s.B[1]).toFixed(1)} `;
    }
    return { d: d + 'Z', verts };
  }
  // Area centroid + inscribed radius (min centroid→edge distance) of a convex polygon.
  function centroidInradius(verts) {
    let A = 0, cx = 0, cy = 0, n = verts.length;
    for (let i = 0; i < n; i++) { const [x0, y0] = verts[i], [x1, y1] = verts[(i+1)%n]; const cr = x0*y1 - x1*y0; A += cr; cx += (x0+x1)*cr; cy += (y0+y1)*cr; }
    A *= 0.5; cx /= (6*A); cy /= (6*A);
    let inr = 1e9;
    for (let i = 0; i < n; i++) { const [x0, y0] = verts[i], [x1, y1] = verts[(i+1)%n]; const dx = x1-x0, dy = y1-y0, L = Math.hypot(dx, dy) || 1; inr = Math.min(inr, Math.abs((cx-x0)*dy - (cy-y0)*dx) / L); }
    return { cx, cy, inr };
  }

  // The Vi wordmark (traced glyph) — drawn in the ink colour, centred.
  function viWordmark(ink) {
    const G = (typeof window !== 'undefined' && window.CV_VI_GLYPH) || null;
    if (!G) return `<text x="50" y="63" text-anchor="middle" font-family="var(--font-display)" font-weight="800" font-size="40" fill="${ink}">Vi</text>`;
    const target = 44, s = target / Math.max(G.w, G.h), gw = G.w * s, gh = G.h * s;
    return `<g transform="translate(${(50-gw/2).toFixed(1)} ${(50-gh/2).toFixed(1)}) scale(${s.toFixed(4)})"><path d="${G.path}" fill="${ink}" fill-rule="evenodd"/></g>`;
  }

  // The icon layer — pulls the glyph body from the ICON SYSTEM (cv-icons.js) and centres
  // it at the shape's CENTROID (cx,cy), sized to the shape's inscribed circle (inr) so it
  // fits each shape proportionally. Tinted with the ink colour (currentColor).
  function iconLayer(name, ink, cx, cy, inr, scale) {
    const ICN = (typeof window !== 'undefined' && window.CV_ICONS);
    const body = ICN && ICN.get ? ICN.get(name) : null;
    if (!body) return '';
    const box = inr * 2 * (scale || 0.74);
    return `<svg x="${(cx - box/2).toFixed(1)}" y="${(cy - box/2).toFixed(1)}" width="${box.toFixed(1)}" height="${box.toFixed(1)}" viewBox="0 0 24 24" fill="none" stroke="${ink}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="color:${ink}">${body}</svg>`;
  }

  // markSVG(spec, opts) — THE one renderer. `spec` is a shape key ('hex'), a type id
  // ('System'), or an entity id ('vi'); opts overrides ANY treatment field. Renders a
  // token-styled vessel with an icon (from the icon system) or the Vi wordmark inside.
  CV_SHAPES.markSVG = function (spec, opts) {
    opts = opts || {};
    const D = this.markDefaults, P = this.markPalette, sampled = opts.preset === 'sampled';
    // resolve spec → shape key + type/entity treatment
    let shapeKey = spec, t = this.shapeType(spec), e = this.entity(spec);
    if (t) shapeKey = t.shape; else if (e) shapeKey = e.shape;
    const g = geom[shapeKey] || geom.square;
    const treat = t || e || {};

    // cascade: default ◀ type/entity ◀ opts (+ optional sampled preset)
    const stroke = opts.stroke || (sampled ? P.gold : D.stroke);
    const sw     = opts.strokeWidth != null ? opts.strokeWidth : D.strokeWidth;
    // ring edge-style (the `outline` facet): solid (default) · dashed (potential) · none (open).
    const outline   = opts.outline || 'solid';
    const dashAttr  = outline === 'dashed' ? ' stroke-dasharray="5 3.5"' : '';
    const strokeEff = outline === 'none' ? 'none' : stroke;   // 'none' removes the ring edge, not the texture
    const inkRole = opts.ink || treat.ink;
    const ink    = (this.inkRole[inkRole] || inkRole) || (sampled ? P.ink : D.ink);
    const fill   = opts.fill || (sampled ? [P.fillTop, P.fillMid, P.fillBot] : D.fill);
    const pattern = opts.pattern || treat.pattern || D.pattern;
    const shadow = opts.flat ? null : (opts.shadow || (sampled ? { color: P.shadow, dx: 0.7, dy: 2, blur: 1.8, opacity: 0.22 } : D.shadow));
    const wantIcon = ('icon' in opts) ? opts.icon : treat.icon;
    const size = opts.size || 120;

    const u = String(shapeKey) + Math.random().toString(36).slice(2, 7);
    const grad = 'gr-' + u, sh = 'sh-' + u, pat = 'pat-' + u;
    const stops = (Array.isArray(fill) ? fill : [fill, fill, fill]);
    let defs = `<linearGradient id="${grad}" x1="6%" y1="4%" x2="96%" y2="98%"><stop offset="0%" stop-color="${stops[0]}"/><stop offset="55%" stop-color="${stops[1] || stops[0]}"/><stop offset="100%" stop-color="${stops[2] || stops[0]}"/></linearGradient>`;
    if (shadow) defs += `<filter id="${sh}" x="-40%" y="-40%" width="180%" height="180%"><feDropShadow dx="${shadow.dx}" dy="${shadow.dy}" stdDeviation="${shadow.blur}" flood-color="${shadow.color}" flood-opacity="${shadow.opacity}"/></filter>`;
    let patDef = '', hasPat = false;
    if (pattern && pattern !== 'none') {
      const P = { weight: 1, opacity: 0.36, gap: 6.5 }, sw2 = P.weight, op = P.opacity;
      const PAT = {
        hatch: `width="6.5" height="6.5" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6.5" stroke="${stroke}" stroke-width="${sw2}" opacity="${op}"/`,
        lines: `width="6" height="6"><line x1="0" y1="0" x2="6" y2="0" stroke="${stroke}" stroke-width="0.8" opacity="${op}"/`,
        vert:  `width="6" height="6"><line x1="0" y1="0" x2="0" y2="6" stroke="${stroke}" stroke-width="0.8" opacity="${op}"/`,
        cross: `width="6.5" height="6.5" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6.5" stroke="${stroke}" stroke-width="${sw2}" opacity="${op}"/><line x1="0" y1="0" x2="6.5" y2="0" stroke="${stroke}" stroke-width="${sw2}" opacity="${op}"/`,
        grid:  `width="6" height="6"><line x1="0" y1="0" x2="6" y2="0" stroke="${stroke}" stroke-width="0.7" opacity="${op}"/><line x1="0" y1="0" x2="0" y2="6" stroke="${stroke}" stroke-width="0.7" opacity="${op}"/`,
        dots:  `width="6" height="6"><circle cx="3" cy="3" r="1" fill="${stroke}" opacity="${op}"/`,
        dense: `width="4" height="4" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="4" stroke="${stroke}" stroke-width="0.8" opacity="${op}"/`,
      };
      const frag = PAT[pattern];
      if (frag) { patDef = `<pattern id="${pat}" patternUnits="userSpaceOnUse" ${frag}></pattern>`; hasPat = true; }
    }

    const interior = opts.frameOnly ? 'none' : `url(#${grad})`;
    const sref = shadow ? `filter="url(#${sh})"` : '';
    // (a transparent/frameOnly interior still allows a texture overlay on top)
    let base, overlay = '', cen = { cx: 50, cy: 50, inr: SPAN / 2 };
    if (g.kind === 'circle') {
      const r = SPAN / 2;
      base = `<circle cx="50" cy="50" r="${r}" fill="${interior}" stroke="${strokeEff}" stroke-width="${sw}"${dashAttr} ${sref}/>`;
      if (hasPat) overlay = `<circle cx="50" cy="50" r="${r}" fill="url(#${pat})"/>`;
    } else if (g.kind === 'rect') {
      base = `<rect x="${INSET}" y="${INSET}" width="${SPAN}" height="${SPAN}" rx="${RAD}" fill="${interior}" stroke="${strokeEff}" stroke-width="${sw}"${dashAttr} ${sref}/>`;
      if (hasPat) overlay = `<rect x="${INSET}" y="${INSET}" width="${SPAN}" height="${SPAN}" rx="${RAD}" fill="url(#${pat})"/>`;
    } else {
      const f = roundedFit(g.points, RAD);
      cen = centroidInradius(f.verts);
      base = `<path d="${f.d}" fill="${interior}" stroke="${strokeEff}" stroke-width="${sw}"${dashAttr} stroke-linejoin="round" ${sref}/>`;
      if (hasPat) overlay = `<path d="${f.d}" fill="url(#${pat})"/>`;
    }

    // inner content: explicit label > wordmark > icon
    let content = '';
    if (opts.label != null && opts.label !== false) {
      const words = String(opts.label).split(' ');
      const lines = words.length > 1 ? [words.slice(0, -1).join(' '), words.slice(-1)[0]] : words;
      const fs = this.markBox.labelSize, lh = fs * 1.04, y0 = 50 - (lines.length - 1) * lh / 2 + fs * 0.34;
      content = `<text text-anchor="middle" font-family="var(--font-display)" font-weight="${this.markBox.labelWeight}" font-size="${fs}" letter-spacing="${this.markBox.labelTracking}" fill="${ink}">${lines.map((l, i) => `<tspan x="50" y="${(y0+i*lh).toFixed(1)}">${l}</tspan>`).join('')}</text>`;
    } else if (treat.wordmark) {
      content = viWordmark(sampled ? P.goldInk : ink);
    } else if (wantIcon) {
      content = iconLayer(wantIcon, ink, cen.cx, cen.cy, cen.inr, opts.iconScale);
    }

    const sizeAttr = opts.stretch ? `width="100%" height="100%" preserveAspectRatio="none"` : `width="${size}" height="${size}"`;
    // G2.1: independent ring vs symbol MOTION. When per-part motion classes are passed
    // (by CV_GLYPHIC.compose), the RING (base shape + its texture overlay) and the SYMBOL
    // (the inner content) become separately-animatable <g> elements, each carrying its own
    // motion hook — so the frame can spin while the symbol rests, etc. CSS transforms on a
    // <g> animate about the part; transform-box keeps the origin centred. Without the opts
    // the markup is unchanged (back-compat).
    const ringG = opts.ringMotionClass
      ? `<g class="${opts.ringMotionClass}" style="transform-box:fill-box;transform-origin:center">${base}${overlay}</g>`
      : `${base}${overlay}`;
    const symG = (opts.symbolMotionClass && content)
      ? `<g class="${opts.symbolMotionClass}" style="transform-box:fill-box;transform-origin:center">${content}</g>`
      : content;
    return `<svg class="cv-mark" viewBox="0 0 100 100" ${sizeAttr} style="overflow:visible"><defs>${defs}${patDef}</defs>${ringG}${symG}</svg>`;
  };

  // ---- EDGE geometry — the relational sibling of markSVG. Draws the textured, directional line that
  // joins two node glyphs in a relational glyphic. Geometry lives HERE (the geometry single source);
  // the edge KINDS/vocabulary live in CV_EDGES; CV_GLYPHIC.composeRelation composes node+edge+node.
  // facets: { line, direction:'to'|'from'|'both'|'none', ink }.
  //   line texture/mood: 'solid' | 'dashed' | 'dots' | 'lines'  (the dash pattern — relation MOOD)
  //   line ROUTING (the path shape between two points): 'straight' (default) | 'right-angled' (orthogonal
  //     L-route) | 'curved' (eased bezier) | 'free' (loose, sketched). Routing is meaningful too
  //     (CV_MEANING seeds right-angled='routes to', curved='eases to', free='sketches to').
  //
  // TWO MODES, one renderer (no parallel edge geometry):
  //   • BOX mode (default — used by composeRelation for the inline node→edge→node glyphic): a self-
  //     contained <svg w×h> with a horizontal line in its own little box.
  //   • POSITIONED mode (opts.from/opts.to given — used by DiagramSolver's glyphgraph layout): emits a
  //     bare <g> (NO wrapping <svg>) — a <path> + an inline arrow polygon — drawn between two real
  //     coordinates in the caller's coordinate space. The arrow shares the line colour, so per-edge
  //     line-COLOUR (state) reaches the arrowhead for free (no fixed <marker> needed).
  // Both share the SAME facet→dash/colour/routing resolution below — one geometry source, two framings.
  CV_SHAPES.edgeSVG = function (facets, opts) {
    facets = facets || {}; opts = opts || {};
    const sw = opts.width || 1.8, cap = 4;
    // G2.2: line COLOUR = the relation's STATE. An explicit resolved colour (opts.color,
    // passed by composeRelation from the lineColor field's token) WINS; else the edge-kind's
    // ink role; else the default. The arrow shares the line colour so the edge reads as one.
    const col = opts.color || (this.inkRole && this.inkRole[facets.ink]) || facets.ink || 'var(--accent-bronze)';
    const dash = facets.line === 'dots' ? '1.4 3' : facets.line === 'dashed' ? '4 3'
               : facets.line === 'lines' ? '6 2.5' : '';     // 'solid' → no dasharray
    const routing = facets.routing || facets.lineType || 'straight';   // path shape between the two points
    const dir = facets.direction || 'to';
    const dashAttr = dash ? ' stroke-dasharray="' + dash + '"' : '';

    // an inline arrowhead polygon pointing along a unit vector (ux,uy) at point (px,py), in the line colour.
    const arrowAt = function (px, py, ux, uy) {
      // perpendicular
      const nx = -uy, ny = ux;
      const tip = px + ',' + py;
      const a = (px - ux * cap + nx * cap) + ',' + (py - uy * cap + ny * cap);
      const b = (px - ux * cap - nx * cap) + ',' + (py - uy * cap - ny * cap);
      return '<polygon points="' + tip + ' ' + a + ' ' + b + '" fill="' + col + '"/>';
    };

    // -------- POSITIONED mode: draw between two real coords (DiagramSolver glyphgraph) --------
    if (opts.from && opts.to) {
      const ax = opts.from.x, ay = opts.from.y, bx = opts.to.x, by = opts.to.y;
      // shorten both ends so the line stops at the node edge (gap = node radius-ish), not the centre.
      const gapA = opts.gapFrom != null ? opts.gapFrom : 0;
      const gapB = opts.gapTo != null ? opts.gapTo : 0;
      let dx = bx - ax, dy = by - ay; const len = Math.hypot(dx, dy) || 1; const ux = dx / len, uy = dy / len;
      const sx = ax + ux * gapA, sy = ay + uy * gapA;     // start (off the source node)
      const ex = bx - ux * gapB, ey = by - uy * gapB;     // end   (off the target node)
      let d;
      if (routing === 'right-angled') {
        // orthogonal L: horizontal first, then vertical (a routed/structured feel).
        d = 'M ' + sx + ' ' + sy + ' L ' + ex + ' ' + sy + ' L ' + ex + ' ' + ey;
      } else if (routing === 'curved' || routing === 'free') {
        // a quadratic bow off the midline; 'free' bows harder (looser/sketched).
        const mx = (sx + ex) / 2, my = (sy + ey) / 2;
        const bow = (routing === 'free' ? 0.34 : 0.18) * len;
        // control point offset perpendicular to the line
        const cxp = mx + (-uy) * bow, cyp = my + (ux) * bow;
        d = 'M ' + sx + ' ' + sy + ' Q ' + cxp.toFixed(1) + ' ' + cyp.toFixed(1) + ' ' + ex + ' ' + ey;
      } else {
        d = 'M ' + sx + ' ' + sy + ' L ' + ex + ' ' + ey;   // straight
      }
      const parts = ['<path d="' + d + '" fill="none" stroke="' + col + '" stroke-width="' + sw +
                     '" stroke-linecap="round" stroke-linejoin="round"' + dashAttr + '/>'];
      // arrow direction at each end follows the local tangent. For curved/right-angled the simple
      // chord direction (ux,uy) reads correctly enough at this scale.
      if (dir === 'to' || dir === 'both') parts.push(arrowAt(ex, ey, ux, uy));
      if (dir === 'from' || dir === 'both') parts.push(arrowAt(sx, sy, -ux, -uy));
      const titleEl = opts.title ? '<title>' + String(opts.title).replace(/</g, '&lt;') + '</title>' : '';
      return '<g class="cv-edge"' + (opts.gClass ? ' data-routing="' + routing + '"' : '') + '>' + titleEl + parts.join('') + '</g>';
    }

    // -------- BOX mode (default): self-contained little svg (composeRelation inline glyphic) --------
    const w = opts.length || 30, h = opts.height || 18, midY = h / 2, x1 = 3, x2 = w - 3;
    const parts = ['<line x1="' + x1 + '" y1="' + midY + '" x2="' + x2 + '" y2="' + midY + '" stroke="' + col +
                   '" stroke-width="' + sw + '" stroke-linecap="round"' + dashAttr + '/>'];
    const arrow = function (x, pointsLeft) {
      const pts = pointsLeft
        ? (x + cap) + ',' + (midY - cap) + ' ' + x + ',' + midY + ' ' + (x + cap) + ',' + (midY + cap)
        : (x - cap) + ',' + (midY - cap) + ' ' + x + ',' + midY + ' ' + (x - cap) + ',' + (midY + cap);
      return '<polygon points="' + pts + '" fill="' + col + '"/>';
    };
    if (dir === 'to' || dir === 'both') parts.push(arrow(x2, false));
    if (dir === 'from' || dir === 'both') parts.push(arrow(x1, true));
    return '<svg width="' + w + '" height="' + h + '" viewBox="0 0 ' + w + ' ' + h + '" fill="none" style="overflow:visible">' + parts.join('') + '</svg>';
  };

  if (typeof window !== 'undefined') window.CV_SHAPES = CV_SHAPES;
  if (typeof module !== 'undefined' && module.exports) module.exports = { CV_SHAPES };
})();
