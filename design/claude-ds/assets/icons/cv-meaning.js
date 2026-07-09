/**
 * ConceptV — MEANING REGISTRY  (window.CV_MEANING)
 * ============================================================================
 * Meaning is CONTEXTUAL. A hexagon, a gold ring, a hatch texture or a raised
 * depth do NOT mean one fixed thing — what they signify changes per context
 * (a deck, a product screen, a process diagram). So every facet→meaning binding
 * is LOADABLE and SWAPPABLE, packaged as a named "meaning profile".
 *
 * The ONE exception is SYMBOLS: a house is always a house, a person a person —
 * a symbol's denotation is intrinsic and lives in CV_ICONS.facets, never here.
 *
 * This separates two layers that were tangled before:
 *   · INVARIANT  — geometry (CV_SHAPES.geom), symbols (CV_ICONS), render defaults.
 *   · CONTEXTUAL — what a form / colour-value / texture / depth / motion / fill
 *                  MEANS. That lives here, in profiles you can load and edit.
 *
 * A profile is plain data → it round-trips to JSON (export → edit → load), so
 * Vi/Tim can author meaning sets without touching code. One default ships
 * ('conceptv-default'); register or load others and switch with use(id).
 *
 * Mirrors the register/resolve/use/list shape of the other registries
 * (CV_REGISTRY / CV_AI / CV_GLYPHIC). Load order: cv-shapes.js → cv-meaning.js.
 */
(function () {
  'use strict';

  function fail(msg) { throw new Error('CV_MEANING: ' + msg); }

  // Facets that CARRY contextual meaning (symbols deliberately absent).
  // These facet ids ARE axis ids (CV_AXES): Meaning is the contextual/loadable
  // layer OVER the axes — a profile maps an axis VALUE → what it signifies here.
  // Symbols are excluded because their meaning is intrinsic (not an axis whose
  // values get re-skinned per context).
  var MEANING_FACETS = ['form', 'color', 'fill', 'texture', 'depth', 'motion'];

  // ---- seed the default profile's FORM bindings FROM CV_SHAPES.shapeTypes ----
  // (reference, not a copy — the geometry source stays the home of form→type;
  // the default profile just adopts it. Other profiles may override per context.)
  function seedFormBindings() {
    var S = window.CV_SHAPES;
    var out = { none: { value: 'Plain', meaning: 'No outer ring — the symbol stands alone, untyped.' } };
    if (S && S.shapeTypes) {
      S.shapeTypes.forEach(function (t) {
        out[t.shape] = { value: t.type, meaning: t.meaning };
      });
    }
    return out;
  }

  // The shipped default profile. Authored values below are EDITABLE — export(),
  // tweak the JSON, load() it back. Colour/fill/texture/depth/motion meanings are
  // first drafts meant to be overridden per context.
  function defaultProfile() {
    return {
      id: 'conceptv-default',
      label: 'ConceptV — default',
      description: 'The baseline meaning set. Form types come from the shape system; the rest are editable starting drafts.',
      bindings: {
        // form: ring-shape → type-class (seeded from CV_SHAPES.shapeTypes)
        form: seedFormBindings(),
        // color: an allocated VALUE → a colour token name (resolved by CV_GLYPHIC)
        color: {
          neutral:  { token: 'bronze', meaning: 'Default / inactive — no special state.' },
          active:   { token: 'gold',   meaning: 'Live, selected or in-focus right now.' },
          positive: { token: 'sage',   meaning: 'Success, complete, approved, healthy.' },
          warning:  { token: 'amber',  meaning: 'Needs attention / caution / pending review.' },
          error:    { token: 'clay',   meaning: 'Failed, blocked, or invalid.' },
          info:     { token: 'blue',   meaning: 'Informational / secondary reference.' },
          muted:    { token: 'muted',  meaning: 'De-emphasised / disabled / archival.' },
        },
        // fill: the plane between ring and symbol
        fill: {
          none:  { meaning: 'Empty / placeholder / not-yet-filled.' },
          paper: { meaning: 'Standard, filled, in-use.' },
          wash:  { meaning: 'Highlighted / featured.' },
          tint:  { meaning: 'Categorised by colour value.' },
        },
        // texture: surface pattern on a part
        texture: {
          none:  { meaning: 'Plain — no sub-classification.' },
          hatch: { meaning: 'In progress / draft / under construction.' },
          dense: { meaning: 'High density / heavy / complex.' },
          cross: { meaning: 'Locked / cancelled / excluded.' },
          grid:  { meaning: 'Structured / systematic / measured.' },
          lines: { meaning: 'Generated / computed / AI-derived.' },
          vert:  { meaning: 'Queued / sequential.' },
          dots:  { meaning: 'Sampled / partial / estimated.' },
        },
        // depth: elevation / layering
        depth: {
          flat:   { meaning: 'Inactive / background / disabled.' },
          d1:     { meaning: 'Barely raised — subtle grouping.' },
          d2:     { meaning: 'Low elevation.' },
          d3:     { meaning: 'Resting / base card level.' },
          d4:     { meaning: 'Raised — interactive / hoverable.' },
          d5:     { meaning: 'Selected / focused — lifted above peers.' },
          d6:     { meaning: 'Highest — modal / dragged / top of stack.' },
          normal: { meaning: 'System default elevation.' },
        },
        // motion: animation / liveness
        motion: {
          none:    { meaning: 'Static — settled, nothing happening.' },
          breathe: { meaning: 'Ambient alive / idle-active.' },
          pulse:   { meaning: 'Needs attention / new / unread.' },
          bob:     { meaning: 'Playful / interactive hint.' },
          tilt:    { meaning: 'Hover / responsive feedback.' },
          spin:    { meaning: 'Processing / loading / working.' },
          float:   { meaning: 'Detached / draggable / floating.' },
          glow:    { meaning: 'Live / active / energised.' },
        },
      },
    };
  }

  var profiles = {};      // id → profile
  var activeId = null;

  // shallow structural validation — loud fail on a malformed profile.
  function validateProfile(p) {
    if (!p || typeof p !== 'object') fail('profile must be an object');
    if (!p.id) fail('profile needs an id');
    if (!p.bindings || typeof p.bindings !== 'object') fail('profile "' + p.id + '" needs a bindings object');
    MEANING_FACETS.forEach(function (f) {
      if (p.bindings[f] && typeof p.bindings[f] !== 'object') fail('binding "' + f + '" in "' + p.id + '" must be an object');
    });
    return p;
  }

  var CV_MEANING = {
    facets: MEANING_FACETS,

    register: function (profile) {
      validateProfile(profile);
      profiles[profile.id] = profile;
      if (!activeId) activeId = profile.id;
      return profile;
    },

    // load from a JSON string OR a plain object (the editable form). Registers
    // and returns the profile; does not switch to it unless makeActive.
    load: function (json, makeActive) {
      var p = (typeof json === 'string') ? JSON.parse(json) : json;
      this.register(p);
      if (makeActive) this.use(p.id);
      return p;
    },

    // export a profile to pretty JSON for editing (defaults to the active one).
    export: function (id) {
      var p = profiles[id || activeId];
      if (!p) fail('no profile "' + (id || activeId) + '" to export');
      return JSON.stringify(p, null, 2);
    },

    resolve: function (id) {
      var p = profiles[id];
      if (!p) fail('unknown meaning profile "' + id + '" (have: ' + Object.keys(profiles).join(', ') + ')');
      return p;
    },

    use: function (id) { this.resolve(id); activeId = id; return id; },
    get active() { return activeId; },
    activeProfile: function () { return this.resolve(activeId); },
    list: function () { return Object.keys(profiles).map(function (k) { return { id: k, label: profiles[k].label }; }); },

    // the value vocabulary for a facet under a profile (the set of allocated
    // values + their meanings). e.g. valuesFor('color') → {neutral,active,...}.
    valuesFor: function (facet, profileId) {
      var p = this.resolve(profileId || activeId);
      if (MEANING_FACETS.indexOf(facet) === -1) fail('"' + facet + '" is not a meaning-bearing facet (symbols are intrinsic, see CV_ICONS.facets)');
      return p.bindings[facet] || {};
    },

    // the AXIS a meaning-facet sits over (Meaning is the contextual layer above
    // the axes). e.g. axis('color') → CV_AXES.resolve('color'). null if axes
    // aren't loaded. This is the reconciliation: facet ids ARE axis ids.
    axis: function (facet) {
      var AX = window.CV_AXES;
      return (AX && AX.has && AX.has(facet)) ? AX.resolve(facet) : null;
    },

    // resolve ONE value of a facet → its meaning record, under a profile.
    meaningOf: function (facet, value, profileId) {
      return this.valuesFor(facet, profileId)[value] || null;
    },

    // colour values map to a token NAME (CV_GLYPHIC turns it into a CSS var).
    // e.g. tokenForValue('active') → 'gold'.
    tokenForValue: function (value, profileId) {
      var rec = this.meaningOf('color', value, profileId);
      return rec ? rec.token : null;
    },
  };

  CV_MEANING.register(defaultProfile());
  CV_MEANING.use('conceptv-default');

  // ============================================================================
  // SURFACE ENCODINGS  (System Map — Piece 4)
  // ----------------------------------------------------------------------------
  // Meaning also governs how a SURFACE turns DATA into what you SEE. An encoding
  // profile is surface-scoped: each "set" binds ONE data facet (a node's role,
  // type, link-count, bytes, nesting depth…) to ONE visual CHANNEL (colour, size,
  // texture, border, glow, opacity), with either a discrete value→appearance map
  // or a continuous scale, plus a plain-language description. This is the SINGLE
  // HOME for the System Map's visual vocabulary — the map's Colour/Size selectors
  // are a projection of it (baked into system-map.json by build-system-map.js),
  // and Claude Code extends the texture/border/glow channels from here.
  // Mirrors register/resolve/list. See analysis/SYSTEM-MAP-ENCODING-GRAMMAR.md.
  var encodings = {};
  CV_MEANING.encodings = {
    register: function (surface, profile) { if (!surface) fail('encoding needs a surface id'); profile.surface = surface; encodings[surface] = profile; return profile; },
    resolve:  function (surface) { var p = encodings[surface]; if (!p) fail('no encoding profile for surface "' + surface + '"'); return p; },
    has:      function (surface) { return !!encodings[surface]; },
    list:     function () { return Object.keys(encodings); },

    // ---- the SHARED resolver for an encoding SET (the one home; G8b) ----------
    // An encoding set is `{ facet:<data field>, kind:'discrete'|'scale', values|stops,
    // fallback }`. resolveSet reads ONE data field out of a data context and turns it
    // into an APPEARANCE via the set's map (discrete) or scale (continuous). This is
    // the deterministic core both the System-Map channels AND a glyphic facet-binding
    // (resolveBindings, below) run through — ONE mechanism, never a parallel binder.
    //   · discrete → values[dataValue]; missing key → set.fallback, else LOUD.
    //   · scale    → linear interpolation across set.stops by a 0..1 `t` (set.domain
    //                [min,max] maps the raw value into t; absent → value used as t).
    // The data field must be PRESENT in the context; an absent binding source is LOUD
    // (G8b: "loud-fail on a missing binding source"). A `null`/`undefined` field value
    // is a present-but-empty source and also fails (no silent skip).
    resolveSet: function (set, ctx) {
      if (!set || typeof set !== 'object') fail('resolveSet: needs an encoding set');
      if (!set.facet) fail('resolveSet: a set needs a `facet` (the data field it reads)');
      if (!ctx || typeof ctx !== 'object') fail('resolveSet: a data context is required to resolve set on facet "' + set.facet + '" (loud — a bound facet with no data context throws)');
      if (!(set.facet in ctx)) fail('resolveSet: missing binding source — the data context has no field "' + set.facet + '" (have: ' + Object.keys(ctx).join(', ') + ')');
      var raw = ctx[set.facet];
      if (raw == null) fail('resolveSet: binding source "' + set.facet + '" is present but empty (null/undefined) — loud, never a silent default');
      var kind = set.kind || 'discrete';
      if (kind === 'discrete') {
        var map = set.values || {};
        if (raw in map) return map[raw];
        if ('fallback' in set) return set.fallback;
        fail('resolveSet: data value "' + raw + '" of "' + set.facet + '" is not in the map {' + Object.keys(map).join(', ') + '} and the set has no fallback — loud');
      }
      if (kind === 'scale') {
        var stops = set.stops;
        if (!Array.isArray(stops) || stops.length < 2) fail('resolveSet: a scale set on "' + set.facet + '" needs ≥2 stops');
        var n = Number(raw);
        if (isNaN(n)) fail('resolveSet: scale source "' + set.facet + '"="' + raw + '" is not a number');
        var t = n;
        if (Array.isArray(set.domain)) {
          var lo = set.domain[0], hi = set.domain[1];
          if (hi === lo) fail('resolveSet: scale domain on "' + set.facet + '" has zero width');
          t = (n - lo) / (hi - lo);
        }
        t = Math.max(0, Math.min(1, t));
        var seg = t * (stops.length - 1), i = Math.floor(seg), frac = seg - i;
        if (i >= stops.length - 1) return stops[stops.length - 1].slice();
        var a = stops[i], b = stops[i + 1];
        return a.map(function (av, k) { return Math.round(av + (b[k] - av) * frac); });
      }
      fail('resolveSet: unknown set kind "' + kind + '" (discrete | scale)');
    },
  };

  CV_MEANING.encodings.register('system-map', {
    id: 'system-map', label: 'System Map — node encoding',
    description: 'How the codebase canvas turns a file/folder’s metadata into what you see. Each set binds one data FACET to one visual CHANNEL. Discrete sets list value→appearance; scale sets interpolate. Channels: colour (fill/tint), size (area within folder), texture (surface pattern), border (edge weight/tone), glow (halo), opacity (fade).',
    channels: {
      colour:  'Fill / tint of the node — the primary recognition channel.',
      size:    'Area of the node, always relative to its siblings within the same folder.',
      texture: 'Surface pattern overlaid on the node (hatch / dots / grid / lines / cross).',
      border:  'Edge weight and tone — good for depth / state without changing fill.',
      glow:    'Outer halo — reserve for liveness / attention / selection.',
      opacity: 'Fade — de-emphasis without removal.',
    },
    sets: {
      'role-colour': { channel: 'colour', facet: 'role', label: 'System', kind: 'discrete',
        description: 'Which system a file belongs to — the main spatial-memory anchor (axes gold, registries blue, components green, tokens amber, ingest/inspo muted).',
        values: { axis:'#E0C010','axis-core':'#C8920E','axis-css':'#D6BF57','value-source':'#B98664','glyphic-core':'#F4E89A','glyphic-css':'#C9B58A',meaning:'#7CA85B',registry:'#6BA0E0',component:'#5C8A4C',engine:'#C09D5D',token:'#E0A23C',card:'#988058',spec:'#C8920E',doc:'#8C8A7E',ai:'#E06A50',template:'#A89678',ui_kit:'#5E7CA6','ui-kit':'#5E7CA6',atomicity:'#B49A5C',app:'#9C8C6E',specimen:'#D0C098',other:'#6b6354',folder:'#3a342a',archive:'#5a5048',ingest:'#5b7676',inspo:'#7d709a',upload:'#5f6b7e',shot:'#46423a' }, fallback: '#6b6354' },
      'type-colour': { channel: 'colour', facet: 'ext', label: 'File type', kind: 'discrete',
        description: 'Colour by file extension — see the JS / CSS / Markdown / image mix at a glance.',
        values: { js:'#E0C010',mjs:'#E0C010',jsx:'#6BA0E0',ts:'#5E7CA6',tsx:'#5E7CA6',css:'#E0A23C',html:'#5C8A4C',md:'#8C8A7E',json:'#B98664',png:'#6b6354',jpg:'#6b6354',jpeg:'#6b6354',gif:'#6b6354',webp:'#6b6354',svg:'#7CA85B' }, fallback: '#6b6354', folderColour: '#3a342a' },
      'link-heat': { channel: 'colour', facet: 'links', label: 'Heat (links)', kind: 'scale', scale: 'linear',
        description: 'Cool → gold → red by how many connections a file has. Finds the hubs.',
        stops: [[90,84,72],[224,162,16],[224,90,60]], folderColour: '#3a342a' },
      'usedby-size': { channel: 'size', facet: 'usedBy', label: 'Used-by', kind: 'scale', scale: 'linear',
        description: 'Bigger = more files depend on it. Surfaces the single-sources / load-bearing files.' },
      'filesize-size': { channel: 'size', facet: 'bytes', label: 'File size', kind: 'scale', scale: 'linear',
        description: 'Area ∝ bytes on disk, relative within each folder.' },
      'links-size': { channel: 'size', facet: 'links', label: 'Links', kind: 'scale', scale: 'linear',
        description: 'Bigger = more total connections (in + out).' },
      // ---- draft channels for Claude Code to build live (data + intent only) ----
      'depth-border': { channel: 'border', facet: 'depth', label: 'Nesting depth', kind: 'scale', scale: 'linear', draft: true,
        description: 'DRAFT: deeper files get a lighter, thinner border so shallow structure reads as bolder.' },
      'kind-texture': { channel: 'texture', facet: 'roleGroup', label: 'Kind texture', kind: 'discrete', draft: true,
        description: 'DRAFT: a surface pattern per broad kind, so kind is legible without spending the colour channel.',
        values: { code:'none', token:'grid', asset:'dots', doc:'lines', archive:'cross', ingest:'hatch' } },
      'state-glow': { channel: 'glow', facet: 'state', label: 'Liveness', kind: 'discrete', draft: true,
        description: 'DRAFT: glow for live/attention states (e.g. recently changed, unwired, selected) — reserve glow for liveness only.',
        values: { changed:'gold', unwired:'clay', none:'none' } },
    },
  });

  // ============================================================================
  // LANGUAGE LAYER — a glyphic is a SIGN; its meaning is a FIELD, composed.
  // ----------------------------------------------------------------------------
  // Tim (2026-06-29): "meaning as a language is more a feeling than a single
  // thing." A facet value does NOT map to one meaning — it carries a semantic
  // FIELD (a feeling + a cluster of senses) that context/combination resolve.
  // The English SENTENCE is a READ-OUT — one projection for humans; the meaning
  // lives in the facets, never borrowed from another language.
  //
  // Four layers: (1) FIELDS per (facet,value) {feeling, senses[], type};
  // (2) the meaning TYPE each facet contributes (a glyph carries several at once);
  // (3) COMBINATION reads (mode = fill+outline+icon together); (4) the READ-OUT
  // (describe / describeRelation), composed + nested.
  //
  // LOUD-FAIL LAW (Tim, non-negotiable): an unknown facet / value / required
  // lookup THROWS. No fallback, no silent default, no swallow. A facet simply
  // not present in a spec contributes nothing (that is honest); a facet PRESENT
  // with an unknown value is an error and fails loud.
  // ============================================================================

  // (2) the TYPE of meaning each facet contributes. A glyph means several at once.
  var MEANING_TYPES = {
    form: 'kind', symbol: 'thing', fill: 'mode', outline: 'mode', color: 'state',
    texture: 'material', depth: 'prominence', motion: 'liveness',
    line: 'relation-mood', edge: 'relation', direction: 'role',
    // G2 facets (2026-06-30): an edge's line COLOUR carries the relation's STATE
    // (red=blocked, green=approved, gold=active) — distinct from `color`(node state);
    // `size` carries COMPARISON (a size difference between two related nodes reads
    // "more than"; an absolute large size reads emphasis).
    lineColor: 'relation-state', size: 'comparison',
  };
  CV_MEANING.types = function () { return Object.assign({}, MEANING_TYPES); };

  // the language reads facets that weren't meaning-bearing before: the ring's
  // outline-style, the edge's own facets (line / relation-kind / direction), the
  // edge line's COLOUR (lineColor — relation state), and the comparative `size`.
  ['outline', 'line', 'edge', 'direction', 'lineColor', 'size'].forEach(function (f) {
    if (MEANING_FACETS.indexOf(f) === -1) MEANING_FACETS.push(f);
  });

  // ---- SEED the field dictionary (the starter — grows in use) ----------------
  // Every entry is a FIELD: a feeling + senses. Authored from the conversation,
  // in Tim's words. Merged onto the active profile so it is the ONE home.
  (function seedFields() {
    var P = CV_MEANING.activeProfile();
    function seed(facet, value, feeling, senses, extra) {
      if (!feeling) fail('seed: ' + facet + '/' + value + ' needs a feeling (loud — no empty meaning)');
      if (!P.bindings[facet]) P.bindings[facet] = {};
      P.bindings[facet][value] = Object.assign({}, P.bindings[facet][value] || {}, {
        feeling: feeling, senses: senses || [], type: MEANING_TYPES[facet] || fail('no meaning-type for facet "' + facet + '"'),
        meaning: feeling,  // back-compat: legacy .meaning consumers read the field's feeling
      }, extra || {});
    }

    // FORM = kind / what nature of thing. (circle/square/triangle/diamond per Tim;
    // the rest carry the shape registry's field, feeling-named.)
    // THE REFERENT WORDS ARE FIELD DATA (A1, 2026-07-03): the word a form contributes to
    // its noun phrase lives HERE — `kindWord` (a trailing noun: "… gateway") or `opWord`
    // (a leading phrase: "action on …"). referent() AND parse() read them from the active
    // profile, so authoring a word changes the read-out and the parse live (no code edit).
    // circle/square carry NO word (the bare kind|instance soft cell). STARTER wording (A5).
    seed('form', 'circle',   'the kind itself',     ['a whole / an identity', 'the category', 'the concept — not a specific one']);
    seed('form', 'square',   'a specific one',      ['this particular', 'an instance', 'a bounded object']);
    seed('form', 'triangle', 'an operation on it',  ['an action relative to the thing at the address', 'a step / a change'], { opWord: 'action on' });
    seed('form', 'diamond',  'interacting with it', ['using / operating it', 'deciding about it (one kind of interacting)'], { opWord: 'use of' });
    seed('form', 'pentagon', 'a feature',           ['a composed capability'],                          { kindWord: 'feature' });
    seed('form', 'hex',      'a system',            ['an engine', 'a configurable set of parts'],       { kindWord: 'system' });
    seed('form', 'heptagon', 'a special case',      ['a rare / specialised type'],                      { kindWord: 'special type' });
    seed('form', 'octagon',  'a gateway',           ['an output / endpoint', 'an edge to the outside'], { kindWord: 'gateway' });
    seed('form', 'none',     'untyped',             ['the symbol stands alone']);

    // FILL + OUTLINE = mode / definiteness — the realization gradient.
    // fill/outline DETERMINERS are field data too (A1): the article the noun phrase opens
    // with. Precedence at read = outline first, then fill; no declared determiner → 'a'.
    seed('fill', 'none',  'held as a concept', ['the kind, as an idea', 'the kind-as-subject', 'not any specific one'], { determiner: 'the' });
    seed('fill', 'paper', 'here, in context', ['this kind, present', 'a member, in use'], { determiner: 'this' });
    seed('fill', 'wash',  'featured',         ['highlighted', 'brought forward'],         { determiner: 'this' });
    seed('fill', 'tint',  'categorised',      ['grouped by its colour value']);
    seed('fill', 'solid', 'full / set',       ['committed', 'complete', 'locked in'], { determiner: 'the' });     // aspirational: needs a solid-colour fill value in CV_GLYPHIC
    seed('outline', 'solid',  'firm',      ['a settled edge']);
    seed('outline', 'dashed', 'potential', ['could be here', 'could be added', 'an open slot'], { determiner: 'a possible' });
    seed('outline', 'none',   'open',      ['no bounding edge']);

    // COLOR = state / voice, on common connotation (the strongest field carrier).
    seed('color', 'active',   'active',           ['live', 'the decision', 'look here'],        { token: 'gold' });
    seed('color', 'positive', 'good — go',        ['grow', 'healthy', 'safe', 'the relationship voice'], { token: 'sage' });
    seed('color', 'error',    'stop — wrong',     ['blocked', 'danger', 'urgent'],              { token: 'clay' });
    seed('color', 'warning',  'caution',          ['pending', 'in-between', 'slow down'],       { token: 'amber' });
    seed('color', 'info',     'information',       ['calm', 'reference', 'cool'],                { token: 'blue' });
    seed('color', 'neutral',  'the quiet default', ['structural', 'grounded', 'secondary'],     { token: 'bronze' });
    seed('color', 'muted',    'de-emphasised',    ['inactive', 'archival', 'past'],             { token: 'muted' });

    // TEXTURE = material / sub-class — the most field-like.
    seed('texture', 'grid',  'structured', ['engineered', 'mathematical', 'systematic']);
    seed('texture', 'hatch', 'worked-on',  ['in-progress', 'drafted', 'shaded in']);
    seed('texture', 'lines', 'directional', ['ruled', 'striated', 'flowing']);
    seed('texture', 'dots',  'partial',    ['sampled', 'scattered', 'estimated']);
    seed('texture', 'cross', 'crossed-out', ['locked', 'cancelled', 'excluded']);
    seed('texture', 'dense', 'heavy',      ['saturated', 'complex']);
    seed('texture', 'none',  'plain',      ['no sub-classification']);

    // DEPTH = prominence ; MOTION = liveness / aspect.
    seed('depth', 'flat',   'inactive',    ['background', 'disabled']);
    seed('depth', 'd4',     'interactive', ['raised', 'hoverable']);
    seed('depth', 'd5',     'selected',    ['lifted above its peers']);
    seed('depth', 'd6',     'on top',      ['modal', 'dragged']);
    seed('depth', 'normal', 'settled',     ['system default standing']);
    seed('motion', 'none',    'at rest',      ['settled', 'nothing happening']);
    seed('motion', 'breathe', 'idle-alive',   ['ambient']);
    seed('motion', 'pulse',   'wants attention', ['new', 'unread']);
    seed('motion', 'spin',    'working',      ['processing', 'loading']);
    seed('motion', 'glow',    'live',         ['energised', 'active now']);

    // EDGE = the relation-carrier (NOT a borrowed "verb"). Its own facets.
    // line = the relation's mood ; edge = the specific relation ; direction = role.
    seed('line', 'solid',        'holds now',  ['asserted', 'actual'],          { phrase: 'is' });
    seed('line', 'dashed',       'could',      ['potential', 'possible'],       { phrase: 'could be' });
    seed('line', 'dotted',       'tentative',  ['weak', 'inferred'],            { phrase: 'might be' });
    seed('line', 'lines',        'ongoing',    ['a flow', 'a stream'],          { phrase: 'flows to' });
    seed('line', 'right-angled', 'routed',     ['structured', 'deliberate'],    { phrase: 'routes to' });
    seed('line', 'curved',       'organic',    ['eased', 'flowing'],            { phrase: 'eases to' });
    seed('line', 'free',         'loose',      ['human', 'sketched'],           { phrase: 'sketches to' });
    // THE EDGE LAW (Tim, 2026-07-03 — CRITERIA AMENDMENT A2): a valid typed edge is a
    // DIRECTIONAL VERB with an EQUAL AND OPPOSITE. Each directed relation declares its
    // inverse telling ONCE here ({directed:true, inverse:{feeling,senses}}); readGraph
    // composes it at read time from focus — one stored edge, both tellings, never stored
    // twice. A symmetric relation ({directed:false}) reads with its own words both ways.
    // All wording is STARTER data, live-tuned via CV_MEANING.author (A5).
    seed('edge', 'face',         'the face of', ['the visible page of'],
         { directed: true, inverse: { feeling: 'faced by', senses: ['shown by', 'fronted by'] } });
    seed('edge', 'documents',    'a guide to',  ['explains', 'teaches', 'a how-to for'],
         { directed: true, inverse: { feeling: 'documented by', senses: ['explained by', 'taught by'] } });
    seed('edge', 'higher-order', 'part of',     ['an instance of a higher concept'],
         { directed: true, inverse: { feeling: 'the higher concept of', senses: ['generalises'] } });
    seed('edge', 'navigates',    'goes to',     ['moves to a related place'],
         { directed: false });   // contextual navigation runs both ways (its look already says direction:'both')
    // universal-operator relations (the `= ≠ + → ⊂` sign-class) — near-universal meaning, free logic/maths.
    seed('edge', 'equals',  'equal to', ['the same as', 'is'],      { operator: true, symbol: '=', directed: false });
    seed('edge', 'not',     'not',      ['is not', 'unequal to'],   { operator: true, symbol: '≠', negates: true, directed: false });
    seed('edge', 'and',     'and',      ['combined with', 'plus'],  { operator: true, symbol: '+', directed: false });
    seed('edge', 'becomes', 'becomes',  ['leads to', 'turns into'], { operator: true, symbol: '→',
         directed: true, inverse: { feeling: 'the outcome of', senses: ['comes from', 'made from'] } });
    seed('edge', 'part-of', 'part of',  ['inside', 'belongs to'],   { operator: true, symbol: '⊂',
         directed: true, inverse: { feeling: 'the container of', senses: ['contains', 'holds'] } });
    // the sign-class grown (2026-07-03, the language seat) — feelings are NOUN-PHRASES so the
    // read-out composes: "A is the resolution of B", never "A is resolves B".
    seed('edge', 'resolves',      'the resolution of',  ['derived from', 'computed from'],      { operator: true, symbol: '∴',
         directed: true, inverse: { feeling: 'resolved into', senses: ['computes down to'] } });
    seed('edge', 'projection-of', 'a projection of',    ['a view of', 'one face of'],           { operator: true, symbol: '⇢',
         directed: true, inverse: { feeling: 'projected as', senses: ['viewed as'] } });
    seed('edge', 'mirrors',       'the mirror of',      ['equal and opposite of', 'reflects'],  { operator: true, symbol: '≍',
         directed: false });   // a mirror relation is its own opposite
    seed('edge', 'seeds',         'the seed of',        ['grows into', 'the root of'],          { operator: true, symbol: '∗',
         directed: true, inverse: { feeling: 'grown from', senses: ['rooted in'] } });
    seed('edge', 'frames',        'the frame of',       ['the lens on', 'the way of seeing'],   { operator: true, symbol: '⌐',
         directed: true, inverse: { feeling: 'framed by', senses: ['seen through'] } });
    seed('direction', 'to',   'acts on',     ['subject → object']);
    seed('direction', 'from', 'acted on by', ['object ← subject']);
    seed('direction', 'both', 'mutual',      ['both ways']);

    // LINE-COLOUR = the relation's STATE (independent of the node colours). The edge
    // itself is red/green/gold; combines with line-style (mood) in the relation read-out.
    // Each carries a token (resolved to a CSS colour the same way node colours are) +
    // a `phrase` woven into the relation sentence ("…is blocked from…").
    seed('lineColor', 'blocked',  'blocked',  ['stopped', 'cannot proceed', 'held back'], { token: 'clay',  phrase: 'is blocked from' });
    seed('lineColor', 'approved', 'approved', ['cleared', 'agreed', 'gone through'],       { token: 'sage',  phrase: 'is approved to' });
    seed('lineColor', 'active',   'active',   ['live now', 'in motion', 'the current one'], { token: 'gold',  phrase: 'is actively' });
    seed('lineColor', 'pending',  'pending',  ['waiting', 'not yet decided'],               { token: 'amber', phrase: 'is pending' });
    seed('lineColor', 'neutral',  'plain',    ['no special state'],                         { token: 'bronze' });

    // SIZE = COMPARISON. Not a literal pixel value — the comparison OUTCOME between
    // two related nodes (more / less / equal), or an absolute emphasis on one node.
    // compareSize() maps a numeric difference to one of these fields; the relation
    // read-out weaves it in ("… more than …"). LOUD on an unknown outcome value.
    seed('size', 'more',     'more / primary',  ['bigger', 'greater', 'the dominant one'], { phrase: 'more than' });
    seed('size', 'less',     'less / secondary', ['smaller', 'lesser', 'subordinate'],     { phrase: 'less than' });
    seed('size', 'equal',    'the same as',      ['on par', 'equally weighted'],            { phrase: 'as much as' });
    seed('size', 'emphasis', 'emphasised',       ['prominent', 'made large', 'stands out']);

    // SYMBOL is intrinsic (CV_ICONS) — not re-skinned. A small gloss maps an icon
    // id to its plain word; absent a gloss the icon's own id is used (its real
    // name, not a fabrication).
    P.symbolGloss = Object.assign({ house: 'home',
      // the language family (2026-07-03): each minted symbol arrives with its word
      frame: 'frame', block: 'block', equation: 'law', window: 'window', seed: 'beginning',
      weave: 'weave', judge: 'judge', ring: 'ring', corpus: 'memory', room: 'room',
      territory: 'territory', operator: 'sign' }, P.symbolGloss || {});
  })();

  // (G0) AUTHORING — the language is WRITTEN over time, live, by Tim AND the AI, with EQUAL tools.
  // The dictionary is DATA (the active profile); this is the ONE API both the interface and the AI call
  // to grow the language THROUGH the system (never by editing engine code). Mutates + the profile
  // round-trips via export()/load() (persistence). LOUD-FAIL on malformed input — no empty meaning.
  CV_MEANING.author = {
    setField: function (facet, value, feeling, senses, extra) {
      if (MEANING_FACETS.indexOf(facet) === -1) fail('author.setField: "' + facet + '" is not a meaning-bearing facet');
      if (!value) fail('author.setField: a value is required');
      if (!feeling) fail('author.setField: ' + facet + '/' + value + ' needs a feeling (loud — no empty meaning)');
      var P = CV_MEANING.activeProfile();
      if (!P.bindings[facet]) P.bindings[facet] = {};
      P.bindings[facet][value] = Object.assign({}, P.bindings[facet][value] || {}, {
        feeling: feeling, senses: senses || [],
        type: MEANING_TYPES[facet] || fail('author.setField: no meaning-type for facet "' + facet + '"'),
        meaning: feeling,
      }, extra || {});
      return CV_MEANING.field(facet, value);                       // returns the resolved field (throws if it didn't take)
    },
    removeField: function (facet, value) {
      var P = CV_MEANING.activeProfile();
      if (!P.bindings[facet] || !(value in P.bindings[facet])) fail('author.removeField: no field ' + facet + '/' + value + ' to remove (loud)');
      delete P.bindings[facet][value];
      return true;
    },
    setRelation: function (id, feeling, senses, extra) { return this.setField('edge', id, feeling, senses, extra); },
    setOperator: function (id, feeling, senses, symbol) { return this.setField('edge', id, feeling, senses, Object.assign({ operator: true }, symbol ? { symbol: symbol } : {})); },
    setLine:     function (id, feeling, senses, phrase) { return this.setField('line', id, feeling, senses, phrase ? { phrase: phrase } : {}); },
    setGloss: function (symbol, word) {
      if (!symbol || !word) fail('author.setGloss: needs a symbol and a word');
      var P = CV_MEANING.activeProfile(); P.symbolGloss = P.symbolGloss || {}; P.symbolGloss[symbol] = word;
      return word;
    },
    // persistence — the language as data, round-tripping through the existing profile export/load.
    save: function () { return CV_MEANING.export(); },
    load: function (json) { return CV_MEANING.load(json, true); },
  };

  // (1) FIELD — the normalized semantic field for a (facet,value). LOUD: throws
  // if the facet isn't meaning-bearing (valuesFor) or the value isn't seeded.
  CV_MEANING.field = function (facet, value) {
    var b = this.valuesFor(facet);                  // throws if facet not meaning-bearing
    var rec = b[value];
    if (!rec) fail('no field for ' + facet + '="' + value + '" in profile "' + this.active + '" — loud, never a silent default');
    var feeling = rec.feeling || rec.meaning;
    if (!feeling) fail('field ' + facet + '/' + value + ' has no feeling/meaning');
    // THE FIELD CARRIES EVERYTHING THE AUTHOR DECLARED (2026-07-03 — design-for-the-class).
    // A whitelisting normalizer here silently DROPPED declared data twice (negates/symbol
    // pre-G2.4; directed/inverse at the edge-law build) — the dropped-field trap. Dissolved:
    // the raw record is spread first, so any extra an author sets (kindWord, determiner,
    // inverse, a future word) reaches every reader; the normalized keys are computed on top.
    return Object.assign({}, rec, {
      facet: facet, value: value, feeling: feeling,
      senses: rec.senses || [rec.meaning].filter(Boolean),
      type: rec.type || MEANING_TYPES[facet] || fail('no meaning-type for facet "' + facet + '"'),
      token: rec.token || null, phrase: rec.phrase || null,
      // operator metadata (the SINGLE home of these flags is the seed):
      // `negates` (G2.4 — negation detected via .negates, never a string match),
      // `operator`/`symbol` (the universal-operator sign-class). null/false when absent.
      negates: !!rec.negates, operator: !!rec.operator, symbol: rec.symbol || null,
      // THE EDGE LAW (A2): `directed` (true=a verb-pair, false=symmetric, undefined=
      // predates the law — the inverse read throws naming it) + `inverse` ({feeling,
      // senses?} — the opposite telling, declared once, composed at read).
      directed: (typeof rec.directed === 'boolean') ? rec.directed : undefined,
      inverse: rec.inverse || null,
    });
  };

  // (3) MODE — the combinatorial read of fill + outline + icon-presence (the one
  // meaning that depends on a COMBINATION, not a single facet). LOUD on unknowns.
  function modeOf(spec) {
    var hasIcon = !!spec.symbol && spec.form !== 'none';
    if (spec.outline === 'dashed') return CV_MEANING.field('outline', 'dashed');     // potential wins
    if (!('fill' in spec) || spec.fill == null) return null;                         // fill ABSENT → no mode (honest; not a swallow — absence ≠ error)
    var f = CV_MEANING.field('fill', spec.fill);                                     // PRESENT → must be known (throws on unknown value)
    if (spec.fill === 'paper' && hasIcon) f = Object.assign({}, f, { feeling: 'here, an actual one', senses: ['present', 'a real instance'] });
    return f;
  }

  // (4) READ-OUT — describe ONE glyphic → {sentence, parts, meaningSet}. The
  // meaning is the typed set; the sentence is one projection. LOUD throughout.
  CV_MEANING.describe = function (spec) {
    if (!spec || typeof spec !== 'object') fail('describe: needs a glyphic spec object');
    if (!spec.form) fail('describe: spec.form is required (loud)');
    var P = this.activeProfile();
    var kind = (spec.form === 'none') ? null : this.field('form', spec.form);        // throws if unknown form
    var thing = null;
    if (spec.symbol) {
      var ICN = window.CV_ICONS;
      if (!ICN || !ICN.get) fail('describe: CV_ICONS must be loaded to read a symbol');
      if (!ICN.get(spec.symbol)) fail('describe: unknown symbol "' + spec.symbol + '" (not in CV_ICONS) — loud');
      thing = (P.symbolGloss && P.symbolGloss[spec.symbol]) || spec.symbol;
    }
    var mode = modeOf(spec);
    // STATE — independent on the RING (frame/reference) and the SYMBOL (thing).
    // spec.value may be a single value (both parts share it) OR a per-part object
    // { ring, symbol } (mirroring the `color` colorset). ABSENT → null; PRESENT-
    // unknown → loud (field() throws). This is the G2.1 ring/symbol independence.
    var ringState = null, symbolState = null;
    if (spec.value != null) {
      if (typeof spec.value === 'object') {
        ringState   = (spec.value.ring   != null) ? this.field('color', spec.value.ring)   : null;
        symbolState = (spec.value.symbol != null) ? this.field('color', spec.value.symbol) : null;
      } else {
        ringState = symbolState = this.field('color', spec.value);                   // single value → both parts
      }
    }
    var state = symbolState || ringState;                                            // back-compat: the singular "state" = the thing's
    var material = (spec.texture && spec.texture !== 'none') ? this.field('texture', spec.texture) : null;
    var prominence = (spec.depth && spec.depth !== 'normal' && spec.depth !== 'flat') ? this.field('depth', spec.depth) : null;
    var liveness = this.field('motion', spec.motion || 'none');

    // do the ring and symbol carry DIFFERENT states? (independent G2.1)
    var splitState = ringState && symbolState && ringState.value !== symbolState.value;

    var set = [];
    if (kind) set.push({ type: 'kind', field: kind });
    if (thing) set.push({ type: 'thing', value: thing });
    if (mode) set.push({ type: 'mode', field: mode });          // mode only when fill/outline present
    if (splitState) {                                            // ring-state on the reference, symbol-state on the thing
      set.push({ type: 'ring-state', field: ringState });
      set.push({ type: 'symbol-state', field: symbolState });
    } else if (state) {
      set.push({ type: 'state', field: state });
    }
    if (material) set.push({ type: 'material', field: material });
    if (prominence) set.push({ type: 'prominence', field: prominence });
    set.push({ type: 'liveness', field: liveness });

    // sentence: when ring/symbol states split, the RING state modifies the REFERENCE
    // (the frame) and the SYMBOL state modifies the THING; otherwise the shared state
    // is a plain modifier. (Wording is starter — tuned live; the structure is the point.)
    var s, mods = [];
    if (splitState) {
      s = (kind ? kind.feeling : 'a mark');
      if (ringState.feeling) s += ' that is ' + ringState.feeling;
      if (thing) s += ' holding the ' + (symbolState.feeling ? symbolState.feeling + ' ' : '') + thing;
      else if (symbolState.feeling) s += ', its symbol ' + symbolState.feeling;
      [mode, material, prominence, liveness].forEach(function (fld) { if (fld && fld.feeling) mods.push(fld.feeling); });
    } else {
      s = (kind ? kind.feeling : 'a mark');       // the feeling already carries its article
      if (thing) s += ' holding the ' + thing;
      [mode, state, material, prominence, liveness].forEach(function (fld) { if (fld && fld.feeling) mods.push(fld.feeling); });
    }
    if (mods.length) s += ', ' + mods.join(', ');
    return { sentence: s + '.', parts: { kind: kind, thing: thing, mode: mode, state: state, ringState: ringState, symbolState: symbolState, material: material, prominence: prominence, liveness: liveness }, meaningSet: set };
  };

  // (G2) SIZE-as-comparison. Two related nodes' AUTHORED sizes → a comparison
  // OUTCOME field (more / less / equal). compareSize reads the RAW spec sizes (never
  // normalized — a normalized default would read 'equal' for everything). Both absent
  // → null (no comparison; honest contribution-of-nothing, not a fabricated 'equal').
  // A single absolute large size → 'emphasis' (via emphasisOf). LOUD on a present-but-
  // unknown size facet value, which can only happen through the dictionary, not here.
  CV_MEANING.compareSize = function (aSize, bSize) {
    if (aSize == null && bSize == null) return null;          // neither authored → nothing to compare
    var a = (aSize == null) ? null : Number(aSize), b = (bSize == null) ? null : Number(bSize);
    if (a != null && isNaN(a)) fail('compareSize: source size "' + aSize + '" is not a number');
    if (b != null && isNaN(b)) fail('compareSize: target size "' + bSize + '" is not a number');
    if (a == null || b == null) return null;                  // only one authored → not a comparison
    var outcome = a > b ? 'more' : (a < b ? 'less' : 'equal');
    return this.field('size', outcome);                       // resolves the comparison field (throws if dict missing)
  };

  // (4b) READ-OUT — describe a RELATION (the simplest complex sentence): two
  // nodes + an edge. The relation's meaning NESTS the node meanings. LOUD.
  // G2: the edge's LINE-COLOUR (relation state) and a SIZE comparison between the two
  // nodes both fold into the verb-phrase — the edge says its state, the nodes their
  // relative weight, with no edge text label required.
  CV_MEANING.describeRelation = function (rel, opts) {
    opts = opts || {};
    if (!rel || !rel.source || !rel.target) fail('describeRelation: needs {source, edge, target}');
    if (!rel.edge || !rel.edge.line) fail('describeRelation: edge.line is required (loud — the relation needs a mood)');
    // R1b — THE EDGE LAW on the inspector read-path too: opts.focus='target' tells the SAME stored
    // edge from the target's side with the declared inverse (one fact, both tellings — exactly as
    // readGraph already realises it). Default 'source' = byte-identical to every existing call.
    var inverted = opts.focus === 'target';
    var subject = this.describe(inverted ? rel.target : rel.source);
    var object = this.describe(inverted ? rel.source : rel.target);
    var mood = this.field('line', rel.edge.line);                                    // throws if unknown line
    var relkind0 = rel.edge.kind ? this.field('edge', rel.edge.kind) : null;         // the specific relation
    var relkind = relkind0;
    if (inverted && relkind0 && relkind0.directed !== false) {
      if (relkind0.directed !== true || !relkind0.inverse || !relkind0.inverse.feeling)
        fail('describeRelation: edge kind "' + rel.edge.kind + '" has no declared inverse telling (THE EDGE ' +
             'LAW: a directed relation is a verb-pair — author it via CV_MEANING.author.setRelation(id, ' +
             'feeling, senses, {directed:true, inverse:{feeling:…}}))');
      // realise with the inverse wording; negation/operator flags ride the real field
      relkind = Object.assign({}, relkind0, { feeling: relkind0.inverse.feeling });
    }
    // line-colour = relation STATE. ABSENT contributes nothing; PRESENT-unknown throws.
    var state = ('lineColor' in rel.edge && rel.edge.lineColor != null && rel.edge.lineColor !== 'neutral')
                ? this.field('lineColor', rel.edge.lineColor) : null;
    // size comparison from the two AUTHORED node sizes (raw specs, not normalized) —
    // subject-relative, so it swaps with the telling.
    var compare = inverted ? this.compareSize(rel.target.size, rel.source.size)
                           : this.compareSize(rel.source.size, rel.target.size);
    var subjPhrase = subject.sentence.replace(/\.$/, '');
    var objPhrase = object.sentence.replace(/\.$/, '');
    // verb-phrase: state (if any) precedes the relation verb; G2.4 NEGATION folds into the
    // verb via relationVerb (the relation word survives — "is NOT the face of"); size weaves
    // before the object. relationVerb is the SHARED helper readGraph's edgeClause also uses.
    var negated = isNegated(this, rel.edge);
    var verb = (state ? (state.phrase || state.feeling) + ' ' : '') +
               relationVerb(this, rel.edge, relkind, mood);
    var sizeClause = compare ? (' — ' + (compare.phrase || compare.feeling)) : '';
    var clause = subjPhrase + ' ' + verb + sizeClause + ' ' + objPhrase;
    // G2.4 CONDITIONAL: wrap the whole clause as "if … then …" (shared helper, CV_COND).
    var sentence = conditionalWrap(rel.edge, clause) + '.';
    return {
      sentence: sentence,
      subject: subject, object: object,
      edge: { mood: mood, kind: relkind, state: state, direction: rel.edge.direction || 'to', negated: negated, conditional: !!(rel.edge && rel.edge.conditions) },
      compare: compare,
    };
  };

  // ==========================================================================
  // THE MEANING READ-OUT (the language, NOT the inspector). A node → its REFERENT
  // (a noun phrase, what it points to — never a recitation of its facets). A graph
  // → a real sentence. Wording is STARTER + live-tunable data; gated on Tim's ear.
  // The test: "can you hear the octagon?" — if it narrates the picture, it's wrong.
  // ==========================================================================
  function capF(s) { return s ? s.charAt(0).toUpperCase() + s.slice(1) : s; }

  // referent(spec) → the noun phrase a node refers to. form = the kind (circle/square
  // carry the kind↔instance feel — the SOFT CELL for Tim's ear); fill = definiteness.
  // A1 (2026-07-03): EVERY word here is PROFILE DATA — the determiner comes from the
  // outline/fill field's `determiner` (outline wins; none declared → 'a'), the kind/op
  // word from the form field's `kindWord`/`opWord`. Nothing is a const; the author API
  // reaches all of it (and parse() inverts the same fields, so both directions move together).
  CV_MEANING.referent = function (spec) {
    spec = spec || {};
    if (!spec.form) fail('referent: spec.form required (loud)');
    var formField = this.field('form', spec.form);                  // validate + the word source (throws on unknown form)
    var det = null;
    if ('outline' in spec && spec.outline != null) {
      var of = this.field('outline', spec.outline);                 // present-unknown → loud
      if (of.determiner) det = of.determiner;
    }
    if (!det && 'fill' in spec && spec.fill != null) {
      var ffill = this.field('fill', spec.fill);                    // present-unknown → loud
      if (ffill.determiner) det = ffill.determiner;
    }
    if (!det) det = 'a';                                            // the bare article — no field claimed it
    var thing = null;
    if (spec.symbol) {
      var ICN = window.CV_ICONS;
      if (!ICN || !ICN.get) fail('referent: CV_ICONS must be loaded');
      if (!ICN.get(spec.symbol)) fail('referent: unknown symbol "' + spec.symbol + '" (loud)');
      var P = this.activeProfile();
      thing = (P.symbolGloss && P.symbolGloss[spec.symbol]) || spec.symbol;
    }
    var phrase;
    if (formField.opWord) phrase = det + ' ' + formField.opWord + (thing ? ' the ' + thing : '');
    else phrase = det + (thing ? ' ' + thing : '') + (formField.kindWord ? ' ' + formField.kindWord : '');
    return phrase.replace(/\s+/g, ' ').trim();
  };

  // ==========================================================================
  // G2.4 — NEGATION + CONDITIONALS in the read-out (one home, both read-outs).
  // --------------------------------------------------------------------------
  // NEGATION is single-homed in the dictionary: the `not` operator carries
  // `negates:true` (seedFields). An edge negates when EITHER its kind resolves to
  // a field with `.negates` (e.g. {kind:'not'}) OR it carries an explicit
  // `negate:true` marker alongside a real relation kind ({kind:'face', negate:true}
  // → "is NOT the face of" — the relation word SURVIVES). Detection NEVER string-
  // matches "not"; it reads `.negates` so a future author can mark any operator
  // negating for free. LOUD: an unknown kind still throws via field('edge',…).
  //
  // CONDITIONAL: an edge.conditions (the G3.3 key, shared with CV_REGISTRY/CV_COND
  // — NOT a second home) verbalizes as the antecedent of an "if … then …" reading.
  // CV_COND.normalize() parses the condition into a structured tree; we reuse it,
  // never reinvent a parser. (Evaluating to a boolean is optional polish that only
  // applies when a data context is in play; the read-out only needs to SAY if/then.)
  function isNegated(self, edge) {
    if (!edge) return false;
    if (edge.negate === true) return true;                          // explicit marker (keeps the relation kind)
    if (edge.kind) {
      var f = self.field('edge', edge.kind);                        // LOUD on unknown kind
      if (f && f.negates) return true;                              // the operator itself negates (e.g. 'not')
    }
    return false;
  }

  // verbalize a CV_COND condition tree as an English antecedent clause. Reuses
  // CV_COND.normalize (the shared evaluator's parser) — does not reinvent it.
  function conditionPhrase(cond) {
    var C = window.CV_COND;
    if (!C || !C.normalize) fail('readGraph: CV_COND must be loaded to read a conditional edge (conditions.js)');
    var n = C.normalize(cond);
    function one(c) {
      if (!c) return '';
      if (c.all) return c.all.map(one).filter(Boolean).join(' and ');
      if (c.any) return c.any.map(one).filter(Boolean).join(' or ');
      if (c.not) return 'not ' + one(c.not);
      if (c.fn) return 'a condition holds';
      var f = c.field, op = c.op, v = c.value;
      if (op === 'exists' || op === 'truthy') return f + ' is set';
      if (op === '!exists' || op === 'falsy') return f + ' is not set';
      var word = { '==':'is', '!=':'is not', '>':'is more than', '>=':'is at least',
                   '<':'is less than', '<=':'is at most', 'in':'is one of', '!in':'is not one of' }[op] || op;
      return f + ' ' + word + (v != null ? ' ' + (Array.isArray(v) ? v.join('/') : v) : '');
    }
    return one(n);
  }

  // the verb-phrase a relation contributes (mood + the specific relation), with
  // NEGATION folded in ("is NOT the face of") — single-homed via isNegated. LOUD.
  function relationVerb(self, edge, relkind, mood) {
    var moodPhrase = (mood.phrase || mood.feeling);
    // suppress the relation word when the KIND *is itself* the negation operator (its own
    // feeling is "not") — otherwise {kind:'not'} would read "is not not". A real relation
    // kind ({kind:'face', negate:true}) is NOT a negator, so "the face of" survives.
    var rkPhrase = (relkind && !relkind.negates) ? (' ' + relkind.feeling) : '';
    if (isNegated(self, edge)) {
      // negate the mood: "is" → "is not", "could be" → "could not be". Keep the
      // relation word so "is NOT the face of" survives (the spec example).
      var neg = /\bis\b/.test(moodPhrase) ? moodPhrase.replace(/\bis\b/, 'is not')
              : /\bcould be\b/.test(moodPhrase) ? moodPhrase.replace(/\bcould be\b/, 'could not be')
              : 'is not ' + moodPhrase;                              // generic: prefix "is not"
      // a standalone negation (kind 'not', no surviving relation word) reads "is not".
      return neg + rkPhrase;
    }
    return moodPhrase + rkPhrase;
  }

  // wrap a built clause as "if <antecedent> then <clause>" when the edge is
  // conditional. Shared by readGraph (edgeClause) AND describeRelation.
  function conditionalWrap(edge, clauseText) {
    if (!edge || !edge.conditions) return clauseText;
    return 'if ' + conditionPhrase(edge.conditions) + ' then ' + clauseText;
  }

  // the verb-phrase a relation contributes (mood + the specific relation). LOUD.
  function edgeClause(self, edge) {
    if (!edge || !edge.line) fail('readGraph: an edge needs a line (its mood)');
    var mood = self.field('line', edge.line);
    var rk = edge.kind ? self.field('edge', edge.kind) : null;
    var rkOr = rk ? null : ' related to';                           // fallback when no relation kind
    var verb = isNegated(self, edge)
      ? relationVerb(self, edge, rk, mood) + (rkOr || '')
      : (mood.phrase || mood.feeling) + (rk ? ' ' + rk.feeling : rkOr);
    return verb;
  }

  // THE EDGE LAW (Tim, 2026-07-03 — A2): the INVERSE verb-phrase — the same stored edge
  // told from its TARGET's side. A directed relation is a verb-pair (equal and opposite);
  // the opposite telling is DECLARED ONCE on the meaning field (.inverse) and COMPOSED here
  // at read time — never stored as a second edge. A symmetric relation (directed:false) and
  // a kindless edge read with the same words both ways (edgeClause). LOUD: a directed kind
  // with no declared inverse throws naming itself — the pair IS the grammar.
  function edgeClauseInverse(self, edge) {
    if (!edge || !edge.line) fail('readGraph: an edge needs a line (its mood)');
    var mood = self.field('line', edge.line);
    var rk = edge.kind ? self.field('edge', edge.kind) : null;
    if (!rk || rk.directed === false) return edgeClause(self, edge);   // symmetric / kindless: its own opposite
    if (rk.directed !== true || !rk.inverse || !rk.inverse.feeling)
      fail('readGraph: edge kind "' + edge.kind + '" has no declared inverse telling (THE EDGE LAW: a ' +
           'directed relation is a verb-pair — author it via CV_MEANING.author.setRelation(id, feeling, ' +
           'senses, {directed:true, inverse:{feeling:…}}))');
    // realise with the inverse wording; negation folds exactly as forward (isNegated reads the real field)
    return relationVerb(self, edge, { feeling: rk.inverse.feeling, negates: rk.negates }, mood);
  }

  // ==========================================================================
  // G10 — MULTI-TARGET transglyphing. The meaning IS the graph; a target is one
  // PROJECTION of it. The traversal (focus, the walk recursion, coordination/
  // subordination shape, the conditional front-hoist, the visited/depth guards) is
  // target-INDEPENDENT — it is the graph's structure. What a target supplies is only
  // how a node + an edge-clause REALISE into surface form. So readGraph traverses
  // ONCE and hands each leaf to a TARGET REALISER; English is one realiser, the
  // structured `triples` form another. No forked traversal, no second readGraph.
  //
  // A realiser is `{ node(spec), edgeKind(edge), relation(subj,clauseInfo,obj),
  // coordinate(parts), subordinate(ref,parts), conditional(edge,text), finalize(t) }`.
  // The ENGLISH realiser reproduces the prior behaviour byte-for-byte (the G4.5-DONE
  // path); the TRIPLES realiser reads STRUCTURAL facets only — edge `kind` + node
  // `id` — and NEVER calls referent() (English must not leak into a structured target,
  // or the proof that "the meaning is the graph, not the English" is fake).
  // --------------------------------------------------------------------------
  var READGRAPH_TARGETS = {};   // target id → realiser-factory(self, byId). Extend-by-registration.

  // ENGLISH — the natural-language projection. Byte-identical to the pre-G10 readGraph.
  READGRAPH_TARGETS.english = function (self, byId) {
    return {
      node: function (spec) { return self.referent(spec); },                       // a node → its noun-phrase referent
      // a relation clause: subject-ref + (mood+relation verb, negation folded) + object.
      relation: function (subjRef, edge, objText) {
        return subjRef + ' ' + edgeClause(self, edge) + ' ' + objText;             // edgeClause carries negation
      },
      // the verb-only clause (used when the subject is already on the page, e.g. a sibling edge).
      clause: function (edge, objText) { return edgeClause(self, edge) + ' ' + objText; },
      // THE EDGE LAW: the verb-only INVERSE clause — the focus telling an INCOMING edge with
      // the opposite verb ("… is the container of <source>"). Same shape as clause().
      clauseInverse: function (edge, srcText) { return edgeClauseInverse(self, edge) + ' ' + srcText; },
      coordinate: function (parts) { return parts.join(', and '); },               // "A, and B"
      subordinate: function (ref, parts) { return ref + ', which ' + parts.join(', and '); },
      conditional: function (edge, text) { return conditionalWrap(edge, text); },  // "if … then …"
      finalize: function (text, info) {
        if (info.kind === 'list')        return { sentence: capF(text) + '.', kind: 'list', target: 'english' };
        if (info.kind === 'noun-phrase') return { sentence: capF(text) + '.', kind: 'noun-phrase', target: 'english' };
        return { sentence: capF(text) + '.', focus: info.focus, kind: 'sentence', target: 'english' };
      }
    };
  };

  // TRIPLES — a compact structured/notation projection: an S-expression over the
  // graph's STRUCTURE. A node → its `id` (always present, already validated; arbitrary,
  // NOT an English word). A relation → `(<kind> <subj> <obj>)`. Negation → `(not …)`.
  // Conditional → `(if <cond> …)`. Coordination → `(and …)`. Subordination = nesting.
  // Reads edge `kind` (the structural relation id) NOT its English `feeling`. LOUD on a
  // present-but-unknown kind/line via self.field (same single-source validation).
  READGRAPH_TARGETS.triples = function (self, byId) {
    function kindToken(edge) {
      // validate the edge structurally the same way English does (loud on unknown), but
      // emit the STRUCTURAL token (the kind id), not English. No kind → the line's id.
      if (!edge || !edge.line) fail('readGraph: an edge needs a line (its mood)');
      self.field('line', edge.line);                                               // LOUD on present-unknown line
      if (edge.kind) {
        var f = self.field('edge', edge.kind);                                     // LOUD on present-unknown kind
        // when the kind IS the negation operator (its field .negates, e.g. {kind:'not'}),
        // the `(not …)` wrapper from neg() IS the negation — suppress the relation token so
        // we never emit `(not (not …))`. Mirrors English's relationVerb rkPhrase guard.
        if (f && f.negates) return 'rel';
        return edge.kind;
      }
      return 'rel';                                                                // structural placeholder when no kind
    }
    // negation is folded into the relation triple (the analog of English's edgeClause
    // owning negation); the conditional `(if …)` is owned by T.conditional ALONE (the
    // analog of English's conditionalWrap), so the lone-conditional front-hoist path —
    // which calls relation() THEN T.conditional() — wraps `(if …)` exactly ONCE, never twice.
    function neg(edge, expr) { return isNegated(self, edge) ? '(not ' + expr + ')' : expr; }
    return {
      node: function (spec) {
        if (!spec || !spec.id) fail('readGraph[triples]: node has no id');         // id is the structural handle
        return spec.id;
      },
      // a full relation with subject present → (kind subj obj), negation folded.
      relation: function (subjId, edge, objExpr) { return neg(edge, '(' + kindToken(edge) + ' ' + subjId + ' ' + objExpr + ')'); },
      // the sibling form: triples are explicit, so the clause STILL carries its subject id
      // (threaded in by walk via the third arg). Same shape as relation() — negation folded,
      // conditional left to T.conditional.
      clause: function (edge, objExpr, subjId) { return neg(edge, '(' + kindToken(edge) + ' ' + subjId + ' ' + objExpr + ')'); },
      // THE EDGE LAW at the structural target: the inverse telling NEVER inverts the STRUCTURE —
      // the triple stays canonical (kind source focus). English swaps words; triples swap nothing.
      // (This is the proof the inverse lives in the REALISER, not in the graph.)
      clauseInverse: function (edge, srcExpr, focusId) { return neg(edge, '(' + kindToken(edge) + ' ' + srcExpr + ' ' + focusId + ')'); },
      coordinate: function (parts) { return parts.length > 1 ? '(and ' + parts.join(' ') + ')' : parts[0]; },
      subordinate: function (ref, parts) { return parts.length > 1 ? '(and ' + parts.join(' ') + ')' : parts[0]; },
      conditional: function (edge, text) {
        if (!edge || !edge.conditions) return text;
        return '(if ' + conditionTriple(edge.conditions) + ' ' + text + ')';
      },
      finalize: function (text, info) {
        return { sentence: text, focus: info.focus, kind: info.kind, target: 'triples' };
      }
    };
  };

  // a CV_COND condition tree → a compact S-expr antecedent (the structured sibling of
  // conditionPhrase). Reuses CV_COND.normalize — does NOT reinvent the parser.
  function conditionTriple(cond) {
    var C = window.CV_COND;
    if (!C || !C.normalize) fail('readGraph: CV_COND must be loaded to read a conditional edge (conditions.js)');
    var n = C.normalize(cond);
    function one(c) {
      if (!c) return '';
      if (c.all) return '(and ' + c.all.map(one).filter(Boolean).join(' ') + ')';
      if (c.any) return '(or ' + c.any.map(one).filter(Boolean).join(' ') + ')';
      if (c.not) return '(not ' + one(c.not) + ')';
      if (c.fn) return '(fn)';
      var op = c.op, v = c.value;
      return '(' + op + ' ' + c.field + (v != null ? ' ' + (Array.isArray(v) ? v.join('/') : v) : '') + ')';
    }
    return one(n);
  }

  // readGraph(graph, {target}) → ONE projection of a graph of nodes + edges, into the
  // chosen target (default 'english'). A single node → its referent / id. A relation →
  // a clause / triple. Branches → coordination. Chains → subordination. Bounded recursion;
  // loud on a broken graph OR an unknown target (present-but-unknown → throw; ABSENT →
  // the 'english' default, honest — existing callers pass no target and must keep working).
  CV_MEANING.readGraph = function (graph, opts) {
    opts = opts || {};
    if (!graph || !Array.isArray(graph.nodes) || graph.nodes.length === 0) fail('readGraph: needs { nodes:[...], edges:[...] }');
    // ---- target dispatch (G10) — absent → default; present-unknown → LOUD (colorForValue pattern).
    var target = ('target' in opts && opts.target != null) ? opts.target : 'english';
    if (!READGRAPH_TARGETS[target]) fail('readGraph: unknown target "' + target + '" (loud — known: ' + Object.keys(READGRAPH_TARGETS).join(', ') + ')');
    var self = this, byId = {};
    graph.nodes.forEach(function (n) { if (!n.id) fail('readGraph: every node needs an id'); byId[n.id] = n; });
    var T = READGRAPH_TARGETS[target](self, byId);
    var edges = graph.edges || [];
    if (edges.length === 0) {
      var phrases = graph.nodes.map(function (n) { return T.node(n); });
      return T.finalize(phrases.join(graph.nodes.length === 1 ? '' : (target === 'triples' ? ' ' : '; ')),
                        { kind: graph.nodes.length === 1 ? 'noun-phrase' : 'list' });
    }
    edges.forEach(function (e) {
      if (!byId[e.from]) fail('readGraph: edge.from "' + e.from + '" is not a node');
      if (!byId[e.to]) fail('readGraph: edge.to "' + e.to + '" is not a node');
    });
    // focus = explicit, else a source (a 'from' that is never a 'to'), else the first node.
    var focus = opts.focus;
    if (!focus) {
      var tos = {}; edges.forEach(function (e) { tos[e.to] = 1; });
      var src = graph.nodes.filter(function (n) { return edges.some(function (e) { return e.from === n.id; }) && !tos[n.id]; })[0];
      focus = (src && src.id) || graph.nodes[0].id;
    }
    if (!byId[focus]) fail('readGraph: focus "' + focus + '" is not a node');
    // walk: a node renders as its node-form + (its outgoing edges as clauses to their objects).
    // Identical traversal for every target — only T.* differs (the projection).
    function walk(id, visited, depth) {
      var out = edges.filter(function (e) { return e.from === id; });
      var ref = T.node(byId[id]);
      if (!out.length || depth <= 0) return ref;
      // G2.4: a LONE conditional edge from the focus hoists the antecedent to the FRONT
      // so the whole reads naturally — "if <cond> then <subject> <verb> <object>" — rather
      // than splicing "if…then…" between subject and verb. (Multi-edge keeps the inline
      // wrap below; wording is starter, tuned live.)
      if (out.length === 1 && out[0].conditions) {
        var e0 = out[0], oid = e0.to, t0;
        if (visited[oid] || depth <= 1) t0 = T.node(byId[oid]);
        else { var vv = Object.assign({}, visited); vv[oid] = 1; t0 = walkAsObject(oid, vv, depth - 1); }
        return T.conditional(e0, T.relation(ref, e0, t0));
      }
      var parts = out.map(function (e) {
        var objId = e.to, tail;
        if (visited[objId] || depth <= 1) tail = T.node(byId[objId]);              // stop: just the object's node-form
        else { var v2 = Object.assign({}, visited); v2[objId] = 1; tail = walkAsObject(objId, v2, depth - 1); }
        // English: the subject is shared across siblings (clause has no subject); triples are
        // explicit so the clause-form receives the subject id. Both go through T.conditional.
        return T.conditional(e, T.clause(e, tail, ref));
      });
      return target === 'triples' ? T.coordinate(parts) : (ref + ' ' + T.coordinate(parts));
    }
    // an object that itself has outgoing edges reads as a subordinate ("…, which …" / nesting).
    function walkAsObject(id, visited, depth) {
      var out = edges.filter(function (e) { return e.from === id; });
      var ref = T.node(byId[id]);
      if (!out.length) return ref;
      var parts = out.map(function (e) {
        var objId = e.to;
        var tail = (visited[objId] || depth <= 1) ? T.node(byId[objId]) : walkAsObject(objId, Object.assign({}, visited, (function(o){o[objId]=1;return o;})({})), depth - 1);
        return T.conditional(e, T.clause(e, tail, ref));
      });
      return T.subordinate(ref, parts);
    }
    var v = {}; v[focus] = 1;
    var text = walk(focus, v, opts.depth || 3);
    // THE EDGE LAW (A2): the focus ALSO tells its INCOMING edges, with the inverse verb —
    // ONE stored edge, BOTH tellings, realised from focus. The default focus is a pure
    // source (no incoming), so every existing read is byte-identical; an explicit
    // target-side focus now speaks instead of standing mute. Every target must supply
    // the clauseInverse realiser (loud — the law binds all projections).
    var inc = edges.filter(function (e) { return e.to === focus; });
    if (inc.length) {
      if (!T.clauseInverse) fail('readGraph: target "' + target + '" has no clauseInverse realiser (THE EDGE LAW binds every target)');
      var hasOut = edges.some(function (e) { return e.from === focus; });
      var focusRef = T.node(byId[focus]);
      var invParts = inc.map(function (e) {
        // starter scope: the inverse tail is the source's node-form (no subordinate recursion
        // back through the source — that would re-tell the edge we are inverting).
        return T.conditional(e, T.clauseInverse(e, T.node(byId[e.from]), focus));
      });
      text = (target === 'triples')
        ? T.coordinate((hasOut ? [text] : []).concat(invParts))
        : (hasOut ? text + ', and ' + T.coordinate(invParts) : focusRef + ' ' + T.coordinate(invParts));
    }
    return T.finalize(text, { focus: focus, kind: 'sentence' });
  };

  // ==========================================================================
  // DATA-BINDING (G8b) — a glyphic facet value can be a BINDING that resolves LIVE
  // from a data context, so the language speaks the CURRENT TRUTH about a real thing.
  // ----------------------------------------------------------------------------
  // A binding IS an encoding set (the EXISTING grammar, generalised — NOT a parallel
  // binder): `{ bind:<data field>, map:{ dataValue → facetVALUE }, [kind], [fallback],
  // [stops], [domain] }`. The ONE legitimate divergence from a System-Map set: a set's
  // appearance is raw (a hex / texture id), a glyphic binding's appearance is a FACET-
  // VALUE — a key into the meaning dictionary (e.g. value:'warning', color:'amber').
  // That is exactly what keeps the meaning FIELD intact downstream, so the read-out
  // lives: a bound `value` resolves to 'warning' → the glyph goes amber AND describe()
  // says "caution". Same mechanism (resolveSet), different appearance domain.
  //
  // `bind` is the public alias for a set's `facet` (the data field). isBinding keys on
  // it so a binding is never confused with the `{ring,symbol}` per-part object.
  CV_MEANING.isBinding = function (v) {
    return !!(v && typeof v === 'object' && !Array.isArray(v) && typeof v.bind === 'string' && v.bind);
  };

  // resolveBindings(spec, ctx) → a FRESH spec with every bound facet resolved to its
  // facet-value from the data context. PURE: never mutates the source spec (so the SAME
  // bound spec re-resolves as data changes — G8b.2 liveness). A facet with no binding is
  // copied through untouched. LOUD via resolveSet on a missing/empty/unmapped source.
  // When the spec has bindings but NO context is given, resolveSet throws the clear
  // "a bound facet with no data context throws" error (not a confusing downstream one).
  CV_MEANING.resolveBindings = function (spec, ctx) {
    if (!spec || typeof spec !== 'object') fail('resolveBindings: needs a glyphic spec object');
    var out = {}, self = this;
    Object.keys(spec).forEach(function (facet) {
      var v = spec[facet];
      if (self.isBinding(v)) {
        // a binding → an encoding set: `bind` is the set's `facet`, `map` its `values`.
        var set = { facet: v.bind, kind: v.kind || 'discrete', values: v.map, stops: v.stops, domain: v.domain };
        if ('fallback' in v) set.fallback = v.fallback;
        out[facet] = self.encodings.resolveSet(set, ctx);   // the ONE resolver lives on .encodings (G8b) — loud on missing source / unmapped value / no ctx
      } else {
        out[facet] = v;                            // literal facet (or per-part object) — untouched
      }
    });
    return out;
  };

  // does a spec carry ANY data-binding? (used to decide whether a context is required.)
  CV_MEANING.hasBindings = function (spec) {
    if (!spec || typeof spec !== 'object') return false;
    var self = this;
    return Object.keys(spec).some(function (f) { return self.isBinding(spec[f]); });
  };

  // ==========================================================================
  // G9 — THE REVERSE: parse(text → glyphgraph)  (semantic parsing, STARTER-GRADE)
  // --------------------------------------------------------------------------
  // The inverse of referent()+readGraph(): a simple sentence → a {nodes,edges}
  // glyphgraph. It is NOT an LLM call — it is a deterministic inversion of the
  // SAME forward grammar, reading the SAME single sources the forward path read,
  // AT PARSE TIME from the active profile (NO second home, NO hand-written keyword
  // table). So a word an author adds via author.setField/setGloss is parseable for
  // free (that is G0.5 — authoring develops the language in BOTH directions).
  //
  // Why it lives INSIDE this IIFE (not a sibling glyph-parse.js): the forward
  // referent() and this inverse share the module's private helpers (edgeClause,
  // relationVerb, conditionPhrase…) — a sibling would need copies, a second home that
  // drifts. Since A1 (2026-07-03) the WORDS themselves (kind words, op phrases, the
  // determiner ladder) are all PROFILE FIELD DATA — both directions read the same
  // fields, so an authored word moves the read-out and the parse together.
  //
  // LOSSY-FORWARD (verified, not assumed): referent() is many→one — "the home" comes
  // from circle|square × fill:none, and "the" comes from fill:none|solid. So a graph
  // round-trip (graph==graph') is NOT recoverable and is NOT the contract. The contract
  // is the TEXT round-trip: readGraph(parse(S)).sentence ≈ S. parse() therefore picks a
  // CANONICAL inverse for each lossy case (documented at each choice) — starter data,
  // tuned live like every other reading.
  //
  // STARTER SCOPE (honest): single node (→ a 1-node graph) · a single relation ·
  // coordination ("A <rel> B and <rel> C", the ", and " readGraph emits). NOT YET:
  // subordination (", which"), conditionals ("if…then"), embedded negation — named as
  // starter gaps in the return's `.notes`, never silently mis-parsed.
  //
  // LOUD-FAIL (two-sided): scaffolding words the forward path INSERTS (determiners,
  // mood/relation phrases, "and") are derived from the registries + the determiner
  // ladder and consumed, never thrown on. A CONTENT token that matches no symbolGloss
  // word, no CV_ICONS id, and no kind word THROWS, naming the specific token — never a
  // fabricated node.
  CV_MEANING.parse = function (text, opts) {
    opts = opts || {};
    var self = this;
    if (typeof text !== 'string' || !text.trim()) fail('parse: needs a non-empty sentence string (loud)');

    // ---- build the inverse vocabularies FROM THE ACTIVE PROFILE (+ the consts) ----
    var P = self.activeProfile();

    // determiner ladder, INVERTED FROM THE PROFILE (A1): every outline/fill field that
    // declares a `determiner` contributes an entry — an authored determiner parses for
    // free. Forward is many→one (referent: outline wins, then fill), so the CANONICAL
    // inverse for a word claimed by several fields is the FIRST claimant in read
    // precedence (outline values, then fill values in profile order — e.g. 'the'→
    // fill:none not fill:solid; 'this'→fill:paper not wash — the documented lossy picks).
    // An outline-borne determiner applies {outline, fill:'paper'} (a canonical instance
    // fill so the node is complete); a fill-borne one applies {fill}. The bare article
    // 'a' stays the fallback ({fill:'paper'}) unless a field claims it. Longest first.
    var DET = [];
    var seenDet = {};
    ['outline', 'fill'].forEach(function (facet) {
      var vals = self.valuesFor(facet);
      Object.keys(vals).forEach(function (v) {
        var f = self.field(facet, v);
        if (!f.determiner || seenDet[f.determiner]) return;   // first claimant = the canonical inverse
        seenDet[f.determiner] = true;
        var apply = {};
        if (facet === 'outline') { apply.outline = v; apply.fill = 'paper'; }
        else apply.fill = v;
        DET.push({ det: f.determiner, apply: apply });
      });
    });
    if (!seenDet['a']) DET.push({ det: 'a', apply: { fill: 'paper' } });
    DET.sort(function (a, b) { return b.det.length - a.det.length; });

    // KIND words, INVERTED FROM THE FORM FIELDS (A1 — the same fields referent() reads).
    // `kindWord` is a trailing word ("… gateway"); `opWord` is a leading phrase
    // ("action on …"/"use of …"). circle/square carry NO word, so a bare "<det> <thing>"
    // with no kind word is the kind|instance soft cell → canonical circle (the concept)
    // unless the determiner already forced fill:paper (then square).
    var KIND_SUFFIX = {};  // word → form  (trailing)
    var OP_PREFIX = {};    // phrase → form (leading)
    (function () {
      var forms = self.valuesFor('form');
      Object.keys(forms).forEach(function (formId) {
        var f = self.field('form', formId);
        if (f.kindWord) KIND_SUFFIX[f.kindWord] = formId;
        if (f.opWord) OP_PREFIX[f.opWord] = formId;
      });
    })();

    // SYMBOL words, INVERTED. Forward referent() uses symbolGloss[symbol] || symbol. So
    // invert the gloss (word → icon id) first; else the raw token must be a real CV_ICONS
    // id. Build the gloss inverse from the active profile (author-extended for free).
    var glossInv = {};
    var gloss = P.symbolGloss || {};
    Object.keys(gloss).forEach(function (sym) { glossInv[String(gloss[sym]).toLowerCase()] = sym; });
    var ICN = window.CV_ICONS;
    if (!ICN || !ICN.get) fail('parse: CV_ICONS must be loaded (symbols are intrinsic)');
    function resolveSymbol(word) {
      var w = String(word).toLowerCase();
      if (glossInv[w]) return glossInv[w];          // a glossed word → its icon id
      if (ICN.get(w)) return w;                      // a raw CV_ICONS id used directly
      return null;                                   // not a symbol — caller decides (throw)
    }

    // RELATION phrases, INVERTED from valuesFor('edge'). Forward edgeClause emits
    // mood.phrase + ' ' + edgeField.feeling (e.g. "is" + " the face of"). We need the
    // edge feelings to peel the relation word off the verb-phrase. Longest first so
    // "part of" wins over a hypothetical "part".
    var edgeVals = self.valuesFor('edge');
    var REL = [];
    Object.keys(edgeVals).forEach(function (id) {
      var f = self.field('edge', id);               // LOUD if a seeded edge has no feeling
      REL.push({ kind: id, feeling: f.feeling, negates: f.negates });
      // THE EDGE LAW: the INVERSE telling parses to the SAME canonical edge — swap:true
      // marks that subject/object exchange back to the stored direction. Declared once
      // on the field; the parser learns both sayings of every verb-pair for free.
      if (f.directed && f.inverse && f.inverse.feeling)
        REL.push({ kind: id, feeling: f.inverse.feeling, negates: f.negates, swap: true });
    });
    REL.sort(function (a, b) { return b.feeling.length - a.feeling.length; });

    // MOOD phrases, INVERTED from valuesFor('line'). Forward uses mood.phrase||feeling
    // as the verb head ("is"/"could be"/"flows to"…). Map each phrase → its line value.
    var lineVals = self.valuesFor('line');
    var MOOD = Object.keys(lineVals).map(function (id) {
      var f = self.field('line', id);
      return { line: id, phrase: (f.phrase || f.feeling) };
    }).sort(function (a, b) { return b.phrase.length - a.phrase.length; });

    // ---- referent (noun phrase) → a node spec. The inverse of referent(). ----
    var nodeSeq = 0;
    function parseReferent(phrase) {
      var raw = phrase.trim().replace(/\s+/g, ' ');
      if (!raw) fail('parse: empty noun phrase where a referent was expected (loud)');
      var node = { id: 'n' + (++nodeSeq) };
      var rest = raw;

      // 1) strip + apply a leading determiner (longest first)
      var detApplied = null;
      for (var i = 0; i < DET.length; i++) {
        var d = DET[i];
        if (rest === d.det || rest.indexOf(d.det + ' ') === 0) {
          detApplied = d; Object.assign(node, d.apply);
          rest = rest.slice(d.det.length).trim();
          break;
        }
      }

      // 2) opWord leading phrase ("action on X" / "use of X") → form + the thing
      var opForm = null;
      Object.keys(OP_PREFIX).forEach(function (ph) {
        if (!opForm && (rest === ph || rest.indexOf(ph + ' ') === 0)) opForm = ph;
      });
      if (opForm) {
        node.form = OP_PREFIX[opForm];
        rest = rest.slice(opForm.length).trim();
        if (rest.indexOf('the ') === 0) rest = rest.slice(4).trim();   // "the <thing>" object of the op
      }

      // 3) trailing kindWord ("… gateway"/"… system"/… — form-field data)
      var kindForm = null;
      if (!opForm) {
        Object.keys(KIND_SUFFIX).forEach(function (w) {
          // a real trailing match: the whole rest IS the kind word, OR rest ends with
          // " <word>" at a genuine (>=0) position. (Guard the length math — when w is
          // longer than rest, lastIndexOf returns -1 which used to spuriously equal the
          // negative length expression; the >=0 + endsWith check makes it exact.)
          var atSuffix = rest.length > w.length && rest.lastIndexOf(' ' + w) === rest.length - (w.length + 1);
          if (rest === w || atSuffix) {
            if (!kindForm || w.length > kindForm.length) kindForm = w;   // longest trailing kind word wins
          }
        });
        if (kindForm) {
          node.form = KIND_SUFFIX[kindForm];
          rest = rest.slice(0, rest.length - kindForm.length).trim();
        }
      }

      // 4) what remains is the THING (a symbol word) — or nothing (a kind-only referent)
      if (rest) {
        var sym = resolveSymbol(rest);
        if (!sym) fail('parse: unknown content token "' + rest + '" in "' + raw +
          '" — not a symbol gloss, not a CV_ICONS id, not a kind word (loud, never a fabricated node). ' +
          'Author it via CV_MEANING.author.setGloss to teach the language this word.');
        node.symbol = sym;
      }

      // 5) settle the form for the kind|instance SOFT CELL (no kind word, no op):
      // canonical inverse — fill:none (the concept) → circle ; fill:paper (present) → square.
      if (!node.form) node.form = (node.fill === 'none') ? 'circle' : 'square';
      if (!node.fill && !node.outline) node.fill = 'paper';   // a bare referent: present by default

      return node;
    }

    // ---- a clause "[mood][ relation] [object]" → { line, kind, objPhrase } ----
    // Peel the mood head, then the relation feeling, leaving the object noun phrase.
    function parseClause(clauseText) {
      var c = clauseText.trim();
      var moodHit = null;
      for (var i = 0; i < MOOD.length; i++) {
        var m = MOOD[i];
        if (c === m.phrase || c.indexOf(m.phrase + ' ') === 0) { moodHit = m; break; }
      }
      if (!moodHit) fail('parse: clause "' + clauseText + '" has no recognised mood (expected one of: ' +
        MOOD.map(function (m) { return '"' + m.phrase + '"'; }).join(', ') + ') — loud');
      var afterMood = c.slice(moodHit.phrase.length).trim();

      // relation feeling (longest first); optional — a bare mood ("is X") is allowed
      var relHit = null;
      for (var j = 0; j < REL.length; j++) {
        var r = REL[j];
        if (afterMood === r.feeling || afterMood.indexOf(r.feeling + ' ') === 0) { relHit = r; break; }
      }
      var objPhrase = relHit ? afterMood.slice(relHit.feeling.length).trim() : afterMood;
      if (!objPhrase) fail('parse: clause "' + clauseText + '" names a relation but no object (loud)');
      return { line: moodHit.line, kind: relHit ? relHit.kind : null,
               swap: !!(relHit && relHit.swap), objPhrase: objPhrase };
    }

    // ---- top level: subject, then one-or-more coordinated clauses ("… and …") ----
    // Undo the forward path's two cosmetic edits so the grammar matches: capF()
    // capitalises ONLY the first character, and a trailing "." is appended. Lower the
    // leading char back + strip the period so determiners/glosses (all lowercase) match.
    var sentence = text.trim().replace(/\.\s*$/, '').replace(/\s+/g, ' ');
    if (sentence) sentence = sentence.charAt(0).toLowerCase() + sentence.slice(1);

    // STARTER-GAP guards: LOUD-FAIL with the HONEST reason BEFORE the content-token
    // machinery can produce a misleading "unknown token" message. These constructs are
    // genuinely unparseable in starter scope, so throwing (not fabricating) is correct —
    // but the throw must name the real cause (subordination / conditional), not blame a token.
    var notes = [];
    if (/,\s*which\b/i.test(sentence))
      fail('parse: subordination (", which …") is not parsed yet (STARTER GAP) — only a single node, a single relation, and coordination ("A … and …") are parsed. Loud rather than mis-parse.');
    if (/\bif\b[\s\S]*\bthen\b/i.test(sentence))
      fail('parse: conditionals ("if … then …") are not parsed yet (STARTER GAP) — only a single node, a single relation, and coordination are parsed. Loud rather than mis-parse.');

    // find the FIRST mood phrase in the sentence → that boundary splits subject | predicate.
    // (We search for a mood phrase as a whole-word run so a noun containing "is" can't false-hit.)
    function firstMoodIndex(s) {
      var best = -1, bestMood = null;
      MOOD.forEach(function (m) {
        var re = new RegExp('(^|\\s)' + m.phrase.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '(\\s|$)');
        var mm = re.exec(s);
        if (mm) {
          var at = mm.index + (mm[1] ? mm[1].length : 0);
          if (best === -1 || at < best) { best = at; bestMood = m; }
        }
      });
      return best;
    }

    var mi = firstMoodIndex(sentence);
    if (mi === -1) {
      // NO relation → a single referent (a noun phrase). A 1-node graph (readGraph
      // treats edges:[] of one node as a noun-phrase, the symmetric case).
      var only = parseReferent(sentence);
      return { graph: { nodes: [only], edges: [] }, focus: only.id, kind: 'noun-phrase',
               notes: notes, starter: true };
    }

    var subjPhrase = sentence.slice(0, mi).trim();
    var predicate = sentence.slice(mi).trim();
    var subject = parseReferent(subjPhrase);
    var nodes = [subject];
    var edges = [];

    // coordination: predicate may be "<clause> and <clause> and …". Split on " and "
    // ONLY at clause boundaries — a clause boundary is where a mood phrase begins. We
    // split on " and " then re-stitch fragments that don't themselves start with a mood
    // (so "this team and this project" inside one object stays whole). Starter heuristic.
    // readGraph joins coordinated clauses with ", and " (an OPTIONAL comma) — consume it.
    var rawParts = predicate.split(/\s*,?\s+and\s+/);
    var clauses = [];
    rawParts.forEach(function (frag) {
      var startsMood = MOOD.some(function (m) { return frag === m.phrase || frag.indexOf(m.phrase + ' ') === 0; });
      if (startsMood || clauses.length === 0) clauses.push(frag);
      else clauses[clauses.length - 1] += ' and ' + frag;   // re-stitch into the prior object
    });

    clauses.forEach(function (cl) {
      var parsed = parseClause(cl);
      var obj = parseReferent(parsed.objPhrase);
      nodes.push(obj);
      // THE EDGE LAW: an inverse saying ("B is the container of A") stores the ONE canonical
      // edge (A part-of B) — the swap puts subject/object back in the declared direction.
      edges.push(parsed.swap
        ? { from: obj.id, to: subject.id, line: parsed.line, kind: parsed.kind }
        : { from: subject.id, to: obj.id, line: parsed.line, kind: parsed.kind });
    });

    return { graph: { nodes: nodes, edges: edges }, focus: subject.id,
             kind: edges.length > 1 ? 'coordination' : 'relation',
             notes: notes, starter: true };
  };

  window.CV_MEANING = CV_MEANING;
})();
