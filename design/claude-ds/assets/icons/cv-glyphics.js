/**
 * ConceptV — GLYPHIC REGISTRY  (window.CV_GLYPHIC)
 * ============================================================================
 * A "Glyphic" is the compositional unit the system is built on: a small stack
 * of independent, meaning-bearing FACETS — outer form (n-gon) · inner symbol ·
 * fill · colour · texture · motion · size · depth — composed generatively and
 * resolved from single sources. (Spec: system/mark-system.html.)
 *
 * This file is the ONE home for the Glyphic unit. It does NOT redefine geometry,
 * symbols, colours, textures or motion — those live in their own single sources:
 *   · Form geometry + form→meaning  → window.CV_SHAPES   (cv-shapes.js)
 *   · Symbols + faceted taxonomy     → window.CV_ICONS    (cv-icons.js)
 *   · Colour / texture / motion / depth tokens → the token graph (CSS vars)
 * The Glyphic layer only COMPOSES them: it declares the record schema, validates
 * a facet-spec against the live vocabularies, and renders by delegating to
 * CV_SHAPES.markSVG. Mirrors the register/resolve/query shape of the other
 * registries (CV_REGISTRY / CV_AI) so learning one teaches the others.
 *
 * Load order: cv-icons.js → cv-vi-glyph.js → cv-shapes.js → cv-glyphics.js.
 */
(function () {
  'use strict';

  function need(name) {
    var v = window[name];
    if (!v) throw new Error('CV_GLYPHIC: ' + name + ' must load before cv-glyphics.js (load order: cv-icons → cv-shapes → cv-glyphics)');
    return v;
  }

  // ---- the FACET schema: every facet of a Glyphic, its single source, its zero
  // and its value space. This object IS the contract — editors, validators and
  // the AI foundry read it; there is no second list of facets anywhere.
  var FACETS = {
    form:    { source: 'CV_SHAPES.geom',        zero: 'none',  type: 'enum',
               values: function () { return ['none'].concat(Object.keys(need('CV_SHAPES').geom)); },
               means: 'type-class (Entity / Action / Object / Decision / Feature / System / Specialised / Gateway)' },
    symbol:  { source: 'CV_ICONS.data',         zero: null,    type: 'ref',
               values: function () { return Object.keys(need('CV_ICONS').data); },
               means: 'the specific thing the glyphic denotes' },
    fill:    { source: 'token (paper/wash/tint)', zero: 'none', type: 'enum',
               values: function () { return ['none', 'paper', 'wash', 'tint']; },
               means: 'the plane between ring and symbol; secondary state / grouping' },
    color:   { source: 'colors_and_type.css',   zero: null,    type: 'colorset',
               means: 'an allocated value — state OR type OR category (per part: ring / symbol / fill)' },
    texture: { source: 'tokens/texture.css',    zero: 'none',  type: 'enum',
               values: function () { return ['none', 'hatch', 'dense', 'cross', 'grid', 'lines', 'vert', 'dots']; },
               means: 'sub-class / material' },
    // Motion value vocabulary: prefer the Motion axis (single source); the local
    // facet list is a fallback for when axes aren't loaded.
    motion:  { source: 'axes/motion/motion-axis.js', zero: 'none',  type: 'enum',
               values: function () {
                 var AX = window.CV_AXES;
                 if (AX && AX.has && AX.has('motion')) return AX.resolve('motion').ids();
                 return ['none', 'breathe', 'pulse', 'bob', 'tilt', 'spin', 'float', 'glow'];
               },
               means: 'liveness / attention / status' },
    size:    { source: 'tokens/icons.css',      zero: null,    type: 'number',
               means: 'hierarchy / emphasis (px)' },
    depth:   { source: 'tokens/depth.css',      zero: 'flat',  type: 'enum',
               values: function () { return ['flat', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'normal']; },
               means: 'elevation / focus / layering' },
    outline: { source: 'tokens (ring stroke style)', zero: 'solid', type: 'enum',
               values: function () { return ['solid', 'dashed', 'none']; },
               means: 'ring edge-style — firm (solid) / potential (dashed) / open (none); the "could-be-here" mode' },
  };

  // system DEFAULT facet-spec — the one applied across the design system when a
  // facet is unspecified. Every field is a parameter a consumer can override.
  var DEFAULTS = {
    form: 'circle', symbol: 'person', fill: 'paper',
    color: { ring: 'gold', symbol: 'bronze' },
    texture: 'none', motion: 'none', size: 56, depth: 'normal', outline: 'solid',
  };

  // colour tokens a facet value can resolve to (single source = the token graph)
  var COLOR_TOKENS = {
    gold: 'var(--accent-gold)', bronze: 'var(--accent-bronze)', ink: 'var(--fg-primary)',
    sage: 'var(--accent-communication, #5A8A4A)', amber: 'var(--status-warning, #C8881F)',
    clay: 'var(--status-error, #B5482E)', blue: 'var(--status-info, #3E6F9E)',
    muted: 'var(--fg-muted, #9A8E78)', paper: 'var(--paper, #fff)',
  };
  function tok(c) { return COLOR_TOKENS[c] || c || 'currentColor'; }

  // FILL ramps — each is a RECIPE OF TOKENS (single source = the colour token
  // graph in colors_and_type.css), not raw colours. 'tint' is built per-call
  // from the chosen ring colour in compose().
  var FILL_RAMPS = {
    paper: ['var(--bg-surface)', 'var(--paper)', 'var(--paper-2)'],
    wash:  ['var(--accent-gold-50)', 'var(--accent-gold-soft)', 'var(--accent-gold-50)'],
  };
  // DEPTH ramp — the SVG-filter mirror of the elevation ramp in tokens/depth.css
  // (d1≈--elev-1 … d6≈--elev-5; flat=--elev-0; 'normal'=markSVG default). The
  // shape-accurate drop-shadow can't be a CSS box-shadow (it must follow the
  // polygon, not the square element), so the geometry lives here while the TINT
  // single-sources from --shadow-c (tokens/depth.css) so palette swaps carry.
  var DEPTH_TINT = 'var(--shadow-c, #2a211a)';
  var DEPTHS = {
    flat: null,                                                  // = --elev-0
    d1: { color: DEPTH_TINT, dx: 0.4, dy: 1,   blur: 1,   opacity: 0.16 },
    d2: { color: DEPTH_TINT, dx: 0.5, dy: 2,   blur: 1.8, opacity: 0.20 },
    d3: { color: DEPTH_TINT, dx: 0.6, dy: 3,   blur: 2.6, opacity: 0.24 },
    d4: { color: DEPTH_TINT, dx: 0.7, dy: 4.5, blur: 3.6, opacity: 0.28 },
    d5: { color: DEPTH_TINT, dx: 0.8, dy: 6,   blur: 5,   opacity: 0.30 },
    d6: { color: DEPTH_TINT, dx: 1.0, dy: 8,   blur: 6.5, opacity: 0.32 },
    // 'normal' → leave markSVG's default shadow
  };

  var CV_GLYPHIC = {
    facets: FACETS,
    defaults: DEFAULTS,

    // ---- RECORD SCHEMAS (single source) -----------------------------------
    // The shape the AI foundry emits and the registry validates/stores. A
    // SYMBOL record is a new inner-glyph + its faceted taxonomy; a GLYPHIC
    // record is a point in the facet space. Kept here, beside the facet
    // contract, so the foundry and validators never invent a second schema.
    schema: {
      symbol: {
        id:          { type: 'string', required: true,  note: 'kebab-case stable id' },
        svg:         { type: 'string', required: true,  note: '24×24 inner body, stroke=currentColor' },
        name:        { type: 'string', required: true },
        description: { type: 'string', required: false },
        facets: {
          domain: { type: 'enum',   from: 'CV_ICONS.taxonomy.domain' },
          kind:   { type: 'enum',   values: ['object', 'action', 'state'] },
          tags:   { type: 'string[]' },
        },
        provenance:  { type: 'enum', values: ['built-in', 'user', 'vi', 'imported'], default: 'vi' },
      },
      glyphic: {
        form:    { type: 'enum',   from: 'CV_GLYPHIC.valuesOf("form")',    default: 'circle' },
        symbol:  { type: 'ref',    from: 'CV_ICONS.data',                   required: true },
        fill:    { type: 'enum',   from: 'CV_GLYPHIC.valuesOf("fill")',     default: 'paper' },
        color:   { type: 'colorset', note: '{ ring, symbol, fill } colour-token names' },
        texture: { type: 'enum',   from: 'CV_GLYPHIC.valuesOf("texture")',  default: 'none' },
        motion:  { type: 'enum',   from: 'CV_GLYPHIC.valuesOf("motion")',   default: 'none' },
        size:    { type: 'number', default: 56 },
        depth:   { type: 'enum',   from: 'CV_GLYPHIC.valuesOf("depth")',    default: 'normal' },
        value:   { type: 'enum',   from: 'CV_MEANING.valuesFor("color")',   required: false },
      },
    },

    // validate a SYMBOL record against the schema (loud list, never coerces).
    validateSymbol: function (rec) {
      var probs = [];
      if (!rec || typeof rec !== 'object') return ['symbol record must be an object'];
      ['id', 'svg', 'name'].forEach(function (k) { if (!rec[k]) probs.push('missing required "' + k + '"'); });
      if (rec.id && !/^[a-z0-9]+(-[a-z0-9]+)*$/.test(rec.id)) probs.push('id "' + rec.id + '" must be kebab-case');
      if (rec.facets && rec.facets.kind && ['object', 'action', 'state'].indexOf(rec.facets.kind) === -1) probs.push('facets.kind "' + rec.facets.kind + '" invalid');
      return probs;
    },

    // The value space of a facet, resolved live from its single source.
    valuesOf: function (facet) {
      var f = FACETS[facet];
      if (!f) throw new Error('CV_GLYPHIC: unknown facet "' + facet + '"');
      return f.values ? f.values() : null;
    },

    // G8b: resolve any live DATA-BINDING facets in a spec against a data context,
    // via CV_MEANING's ONE resolver (resolveBindings → resolveSet). Returns the spec
    // unchanged when it carries no bindings (so an unbound, context-free spec is a
    // pure pass-through). When it DOES carry bindings, a context is required — the
    // resolver throws loud if it's missing/empty/unmapped. The one home of binding is
    // CV_MEANING; this is just the thread-point, no parallel binder here.
    _bind: function (spec, data) {
      var M = window.CV_MEANING;
      if (!M || !M.hasBindings) {
        // if a spec needs binding but the meaning registry isn't loaded, fail loud.
        if (spec && typeof spec === 'object' && Object.keys(spec).some(function (k) { var v = spec[k]; return v && typeof v === 'object' && typeof v.bind === 'string'; }))
          throw new Error('CV_GLYPHIC: a data-bound spec needs CV_MEANING loaded (the one home of binding)');
        return spec;
      }
      if (!M.hasBindings(spec)) return spec;          // no bindings → untouched (pure pass-through)
      return M.resolveBindings(spec, data);           // loud on missing source / no context / unmapped
    },

    // Normalise a partial spec against DEFAULTS (fills missing facets).
    normalize: function (spec) {
      spec = spec || {};
      var out = {};
      for (var k in DEFAULTS) out[k] = (k in spec) ? spec[k] : DEFAULTS[k];
      if ('value' in spec) out.value = spec.value;   // allocated meaning value (optional)
      if (spec.color && typeof spec.color === 'object') {
        out.color = Object.assign({}, DEFAULTS.color, spec.color);
      } else if (typeof spec.color === 'string') {
        out.color = { ring: spec.color, symbol: spec.color };
      }
      return out;
    },

    // Validate a facet-spec against the LIVE vocabularies. Loud fail: returns a
    // list of problems (empty = valid); throws nothing so callers can surface
    // friendly errors, but never silently coerces an unknown value.
    validate: function (spec) {
      var s = this.normalize(spec), problems = [];
      var shapes = need('CV_SHAPES'), icons = need('CV_ICONS');
      if (s.form !== 'none' && !shapes.geom[s.form]) problems.push('form "' + s.form + '" is not in CV_SHAPES.geom');
      if (!icons.get(s.symbol)) problems.push('symbol "' + s.symbol + '" is not in CV_ICONS');
      ['fill', 'texture', 'depth', 'outline'].forEach(function (fk) {
        var vals = CV_GLYPHIC.valuesOf(fk);
        if (vals && vals.indexOf(s[fk]) === -1) problems.push(fk + ' "' + s[fk] + '" not in {' + vals.join(', ') + '}');
      });
      var mv = this.valuesOf('motion');
      if (mv.indexOf(s.motion) === -1) problems.push('motion "' + s.motion + '" not in {' + mv.join(', ') + '}');
      return problems;
    },

    // Meaning is CONTEXTUAL → resolved through the active meaning profile
    // (CV_MEANING), NOT hardcoded here. meaningOf(facet, value) returns the
    // {value/token, meaning} record for any meaning-bearing facet under the
    // current profile. Falls back to CV_SHAPES.shapeTypes for form only if the
    // meaning registry isn't loaded.
    meaningOf: function (facet, value) {
      // back-compat: meaningOf('hex') with one arg = form lookup
      if (arguments.length === 1) { value = facet; facet = 'form'; }
      var M = window.CV_MEANING;
      if (M) return M.meaningOf(facet, value);
      if (facet === 'form') {
        var t = need('CV_SHAPES').shapeType(value);
        return t ? { value: t.type, meaning: t.meaning } : null;
      }
      return null;
    },

    // resolve an allocated colour VALUE (e.g. 'active') → its token, via the
    // active meaning profile. Used so a glyphic can be driven by state/type.
    colorForValue: function (value) {
      var M = window.CV_MEANING;
      var name = M ? M.tokenForValue(value) : null;   // allocated meaning value (e.g. 'active') → token name
      if (name) return tok(name);
      if (COLOR_TOKENS[value]) return tok(value);      // a raw colour-token name (gold / bronze / …)
      // unknown: neither an allocated meaning value nor a known colour token. LOUD-FAIL (CLAUDE.md §3) —
      // a silent tok(value) would emit the literal as a stroke with zero signal (the typo trap: value:'activ').
      throw new Error('CV_GLYPHIC.colorForValue: unknown colour value "' + value + '" — not an allocated meaning value (CV_MEANING) nor a colour token; refusing to emit a silent literal');
    },

    // Resolve the motion CSS class via the MOTION AXIS (single source). Falls
    // back to the legacy 'mo-'+id only if the axis isn't loaded.
    motionClassFor: function (id) {
      if (!id || id === 'none') return '';
      var AX = window.CV_AXES;
      if (AX && AX.has && AX.has('motion')) {
        var cls = AX.css('motion', id);
        return cls || '';
      }
      return 'mo-' + id;
    },

    // COMPOSE a glyphic to SVG markup. Delegates geometry/fill/texture/shadow to
    // CV_SHAPES.markSVG; resolves colour + depth tokens here. Motion is applied
    // by the consumer (a CSS class) — returned in .motionClass, resolved from the
    // Motion axis.
    compose: function (spec, opts) {
      opts = opts || {};
      // G8b: a facet value may be a live DATA-BINDING ({bind, map}). Resolve every
      // bound facet against the data context (opts.data) FIRST — via CV_MEANING's ONE
      // resolver — so the rest of compose sees a plain literal spec. LOUD if the spec
      // carries bindings but no context is given (resolveBindings → resolveSet throws).
      // PURE: resolveBindings returns a fresh spec; the source `spec` is never mutated,
      // so the SAME bound spec re-composes live as the data changes.
      spec = this._bind(spec, opts.data);
      var s = this.normalize(spec);
      var shapes = need('CV_SHAPES');
      // an allocated value (e.g. 'active','warning') drives colour via the active
      // meaning profile, unless an explicit colour was given. G2.1: `value` may be a
      // single value (ring + symbol share it) OR a per-part object { ring, symbol } so
      // the RING (frame) and SYMBOL (thing) carry colour INDEPENDENTLY.
      var ringVal = null, symVal = null;
      if (s.value != null && !spec.color) {
        if (typeof s.value === 'object') {
          ringVal = (s.value.ring   != null) ? this.colorForValue(s.value.ring)   : null;
          symVal  = (s.value.symbol != null) ? this.colorForValue(s.value.symbol) : null;
        } else { ringVal = symVal = this.colorForValue(s.value); }
      }
      var ring = ringVal || tok((s.color && s.color.ring) || 'gold');
      var ink  = symVal  || tok((s.color && s.color.symbol) || 'bronze');
      var valTok = symVal || ringVal;                         // for the solid-fill plane (the thing's colour leads)
      var size = opts.size || s.size || DEFAULTS.size;
      var svg;
      if (s.form === 'none') {
        var body = need('CV_ICONS').get(s.symbol) || '';
        var isz = Math.round(size * 0.72);
        svg = '<svg viewBox="0 0 24 24" width="' + isz + '" height="' + isz + '" fill="none" stroke="' + ink +
              '" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="color:' + ink + '">' + body + '</svg>';
      } else {
        var o = { size: size, icon: s.symbol, stroke: ring, ink: ink };
        if (s.texture && s.texture !== 'none') o.pattern = s.texture;
        if (s.fill === 'none') o.frameOnly = true;
        else if (FILL_RAMPS[s.fill]) o.fill = FILL_RAMPS[s.fill];
        else if (s.fill === 'tint') o.fill = [tok((s.color && s.color.ring) || 'gold'), 'var(--paper)', 'var(--paper)'];
        else if (s.fill === 'solid') {                                   // 'full / set / committed' — a flat colour fill
          o.fill = (valTok || tok((s.color && s.color.ring) || 'gold')); // single colour → markSVG renders a flat plane
          o.ink = 'var(--paper, #FCFAF2)';                               // light icon/label for contrast on the solid plane
        }
        if (s.depth === 'flat') o.flat = true;
        else if (DEPTHS[s.depth]) o.shadow = DEPTHS[s.depth];
        if (s.outline && s.outline !== 'solid') o.outline = s.outline;   // 'dashed' = potential, 'none' = open
        // G2.1: independent ring vs symbol MOTION. `motion` may be a single value
        // (the whole glyphic animates, via the wrapper class) OR a per-part object
        // { ring, symbol } → markSVG hangs each part's motion class on the RING (base
        // path) and the SYMBOL (icon layer) separately, so they animate independently.
        if (s.motion && typeof s.motion === 'object') {
          if (s.motion.ring   != null) o.ringMotionClass   = this.motionClassFor(s.motion.ring);
          if (s.motion.symbol != null) o.symbolMotionClass = this.motionClassFor(s.motion.symbol);
        }
        svg = shapes.markSVG(s.form, o);
      }
      // wrapper motion class = the single-value motion (whole-glyphic); when motion is
      // per-part the wrapper stays still and the parts carry their own classes (above).
      var wrapMotion = (s.motion && typeof s.motion === 'object') ? 'none' : s.motion;
      return { svg: svg, motionClass: this.motionClassFor(wrapMotion), spec: s };
    },

    // Convenience: compose + wrap with the motion class, ready to inject.
    render: function (spec, opts) {
      var r = this.compose(spec, opts);
      return '<span class="cv-glyphic ' + r.motionClass + '" style="display:inline-flex">' + r.svg + '</span>';
    },

    // ---- READ-OUT — a glyphic SAYS ITSELF. Delegates to the meaning registry
    // (the one home of meaning); the sentence is a projection, the meaning is the
    // facet field-set. LOUD: throws if CV_MEANING isn't loaded (no silent skip).
    // G8b: `data` (2nd arg) is an optional live DATA-CONTEXT. A bound facet ({bind,map})
    // resolves from it FIRST, so describe reads the resolved facet-value and the read-out
    // speaks the current truth (status:pending → "caution"; status:sold → "good — go").
    describe: function (spec, data) {
      var M = window.CV_MEANING;
      if (!M || !M.describe) throw new Error('CV_GLYPHIC.describe: CV_MEANING must load before this (the meaning registry is the one home of meaning)');
      return M.describe(this.normalize(this._bind(spec, data)));
    },

    // ---- RELATIONAL glyphic — the next layer up from a single node. A relation is
    // (sourceNode → typed directional edge → targetNode): two faceted node glyphics
    // joined by a typed edge whose KIND comes from CV_EDGES (single source) and whose
    // GEOMETRY comes from CV_SHAPES.edgeSVG. Delegates exactly like compose() delegates
    // to markSVG — no parallel renderer. `rel` = { source:<glyphic-spec>, edge:{kind,…},
    // target:<glyphic-spec> }. Returns { html, edge:<resolved facets>, spec }.
    composeRelation: function (rel, opts) {
      rel = rel || {}; opts = opts || {};
      var EDGES = window.CV_EDGES;
      if (!EDGES) throw new Error('CV_GLYPHIC.composeRelation: CV_EDGES must load before this (cv-edges.js)');
      var shapes = need('CV_SHAPES');
      var nodeSize = opts.nodeSize || 26;
      // G8b: a relation's nodes (and its lineColor) may be data-bound; opts.data flows
      // to BOTH nodes and into the read-out, so a relation can speak live truth too.
      var data = opts.data;
      var srcSpec = this._bind(rel.source || {}, data);
      var tgtSpec = this._bind(rel.target || {}, data);
      var src = this.compose(srcSpec, { size: nodeSize });            // the typed source node (bindings resolved)
      var tgt = this.compose(tgtSpec, { size: nodeSize });            // the typed target node (bindings resolved)
      // G8b: the edge itself may bind facets (e.g. lineColor:{bind:'status',map:{…}}) —
      // resolve them against the same data context before reading line/lineColor.
      var edgeSpec = this._bind(rel.edge || {}, data);
      var ef = EDGES.resolve(edgeSpec);                                // kind → facets (line/direction/ink)
      // G2.2: the edge's LINE-COLOUR = the relation's STATE (red=blocked / green=approved
      // / gold=active …). EDGES.resolve() drops it, so thread it EXPLICITLY (a silent loss
      // is itself a law violation). Resolve value→token→CSS via the SAME path nodes use
      // (CV_MEANING.tokenForValue → COLOR_TOKENS) — never a second token map. Precedence:
      // resolved line-state colour > the edge-kind's ink default.
      var lineColor = edgeSpec.lineColor || null;
      // resolve the lineColor field's TOKEN (clay/sage/gold…) → CSS, via the same token
      // map nodes use (tok → COLOR_TOKENS). field() throws on a present-unknown value (loud).
      var lineCol = null;
      if (lineColor && lineColor !== 'neutral') {
        var lf = window.CV_MEANING.field('lineColor', lineColor);     // loud on unknown
        lineCol = tok(lf.token || lineColor);
      }
      var edgeOpts = { length: opts.edgeLength || 30, height: Math.round(nodeSize * 0.72), width: opts.edgeWidth };
      if (lineCol) edgeOpts.color = lineCol;                           // explicit rendered colour input (precedence handled in edgeSVG)
      var edgeSvg = shapes.edgeSVG(ef, edgeOpts);
      // the relation SAYS ITSELF — read out via the meaning registry (loud if absent).
      var M = window.CV_MEANING;
      if (!M || !M.describeRelation) throw new Error('composeRelation: CV_MEANING must load before this (meaning is its one home)');
      // G2.4: NEGATION (negate marker) + CONDITIONAL (conditions, the G3.3 key) are
      // dropped by EDGES.resolve (structural), so thread them EXPLICITLY from edgeSpec —
      // same pattern as lineColor above; a silent loss would be a law violation.
      var read = M.describeRelation({ source: srcSpec, edge: { line: ef.line, kind: ef.kind, direction: ef.direction, lineColor: lineColor, negate: edgeSpec.negate, conditions: edgeSpec.conditions }, target: tgtSpec });
      var html = '<span class="cv-rel" title="' + read.sentence.replace(/"/g, '&quot;') +
                 '" style="display:inline-flex;align-items:center;gap:3px">' +
                 '<span style="display:inline-flex">' + src.svg + '</span>' + edgeSvg +
                 '<span style="display:inline-flex">' + tgt.svg + '</span></span>';
      return { html: html, edge: ef, spec: rel, sentence: read.sentence, read: read };
    },

    // Query symbols by facet (delegates to CV_ICONS — the symbol single source).
    symbols: function (q) {
      var icons = need('CV_ICONS');
      if (!q) return icons.search('');
      if (typeof q === 'string') return icons.search(q);
      var names = icons.search('');
      if (q.domain) names = names.filter(function (n) { return (icons.facets[n] || {}).domain === q.domain; });
      if (q.kind)   names = names.filter(function (n) { return (icons.facets[n] || {}).kind === q.kind; });
      return names;
    },
  };

  window.CV_GLYPHIC = CV_GLYPHIC;
})();
