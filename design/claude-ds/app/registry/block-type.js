// app/registry/block-type.js
// ============================================================================
// Registers the BLOCK into CV_REGISTRY — the container universal component,
// the second worked example (after the Glyphic) of the parts / slots / sockets
// grammar. Blocks are the TANGIBLE UNITS OF ZONES: what glyphics — and every
// other typed thing: text, controls, media, other blocks — live inside.
//
// THE BLOCK IN ONE PARAGRAPH
//   A block is a bounded region of a page with a GROUND (the plane behind it),
//   a SURFACE (a material: glass / parchment / stone / none), a containment-
//   DEPTH COORDINATE (page → region → panel → card → well: the zoning ladder),
//   ordered CONTENT SOCKETS (header → body → footer: order IS reading order),
//   and ACTION SOCKETS (verbs from CV_ACTIONS attached like any other typed
//   occupant). The whole page is itself a block (level 'page'); a page is a
//   composition of blocks; and every block resolves through the ONE operation
//   (CV_NODE.resolve → the 'block' solver) — the entire page eventually made
//   only of resolutions.
//
// SINGLE SOURCE: structure only, exactly like glyphic-type.js. Materials live
// in tokens/material.css (+ glass.css) via the material AXIS; spacing in the
// space axis; elevation in the depth axis; flow in the flow axis; layout rules
// (.keyline/.contain/.flow) in tokens/layout.css; actions in CV_ACTIONS. This
// file only names which of those a block subscribes to, and where things plug in.
//
// COORDINATES: every resolved block gets { level, path } — level is its rung
// on the containment ladder (the zoning ladder made addressable), path is its
// address from the page root through named sockets ("page/main/pipe[2]"), the
// same way a glyphic's parts are addressable (ring.fill). CV_BLOCK.walk()
// assigns them; nothing hand-sets a coordinate.
//
// Load order: types-core.js → axes (incl. material/flow) → cv-node.js →
// actions.js → block-type.js.
// ============================================================================
(function () {
  'use strict';
  var R = window.CV_REGISTRY;
  if (!R) { console.error('block-type.js: CV_REGISTRY must load first'); return; }

  function sub(axisId, extra) {
    var AX = window.CV_AXES;
    var def = (AX && AX.has && AX.has(axisId)) ? AX.resolve(axisId).default() : undefined;
    return Object.assign({ axis: axisId, default: def }, extra || {});
  }

  // ---- the containment ladder — the block's DEPTH COORDINATE.
  // ONE home: the LEVEL AXIS (axes/level/level-axis.js). This file READS it —
  // never a parallel list. Loud-fail if the axis isn't loaded.
  function LADDER() {
    var AX = window.CV_AXES;
    if (!AX || !AX.has('level')) throw new Error('block-type.js: the level axis must load first (axes/level/level-axis.js)');
    return AX.resolve('level');
  }

  // ---- part sub-types --------------------------------------------------------
  var partTypes = [
    {
      id: 'block-ground', name: 'Ground', kind: 'ground', layer: 'token',
      family: 'block-part', classification: ['ground'],
      description: 'The plane BEHIND the surface — what a translucent material refracts. The page block\u2019s ground is the canvas itself (ambient field); any block may re-texture its own ground.',
      icon: 'square',
      valueSlots: {
        color:   sub('color', { groups: ['neutral', 'brand'], optional: true, means: 'ground wash (defaults to the theme\u2019s --zone-ground)' }),
        texture: sub('texture', { means: 'ground texture behind the surface — the FULL texture axis; consumed as data-ground-texture (tokens/material.css)' }),
        motion:  sub('motion', { optional: true, means: 'ambient drift of the ground (the light field)' }),
      },
    },
    {
      id: 'block-surface', name: 'Surface', kind: 'surface-plane', layer: 'token',
      family: 'block-part', classification: ['surface-plane'],
      description: 'The material sheet of the block — what you see and what contains. Material is switchable (glass \u2194 parchment \u2194 stone \u2194 none); its depth modifier derives from the block\u2019s LEVEL, never set by hand.',
      icon: 'browser',
      valueSlots: {
        material:  sub('material'),
        elevation: sub('depth', { means: 'shadow lift — overlays sit higher' }),
        tint:      sub('color', { groups: ['semantic', 'communication'], optional: true,
                                  means: 'optional meaning-tint over the material (the tonal-glass whisper; gold reserved for Vi)' }),
        texture:   sub('texture', { optional: true, means: 'override the material\u2019s own texture' }),
      },
      conditions: ['tint requires material != none'],
    },
  ];

  // ---- the parent Block Type -------------------------------------------------
  var blockType = {
    id: 'block', name: 'Block', kind: 'block', layer: 'block',
    family: 'block', classification: ['block', 'container'],
    description: 'The container universal component — the tangible unit of a zone. Ground + material surface + containment-depth coordinate + ordered content sockets + action sockets. Pages are compositions of blocks; everything a page shows lives inside one.',
    icon: 'browser',
    provenance: 'built-in',

    // whole-unit value slots — the block's own dials, each a subscription
    valueSlots: {
      level:   sub('level', { means: 'containment-depth coordinate (the ladder AXIS); DERIVES the material depth-modifier, zone wash, and the rung’s spacing rhythm' }),
      keyline: sub('space', { values: ['s2', 's3', 's4', 's5', 's6'], optional: true,
                 means: 'override the rung’s DERIVED content inset (--keyline) — normally computed from level' }),
      gap:     sub('space', { values: ['s1', 's2', 's3', 's4', 's5', 's6'], optional: true,
                 means: 'override the rung’s DERIVED child gap' }),
      arrange: { axis: null, values: ['stack', 'split', 'flow', 'none'], default: 'stack',
                 means: 'how the body socket lays out: stack = rows · split = declared columns (cols) · flow = counted group (the flow equation) · none = the block manages no layout' },
      flow:    sub('flow', { means: 'overflow intent when arrange = flow (wrap / reel / fixed)' }),
      density: sub('density', { means: 'the density dial — scales the rung’s keyline/gap via --d-* (tokens/density.css)' }),
      contain: { axis: null, values: ['clip', 'visible'], default: 'clip',
                 means: 'containment rule — clip to the rounded box (.contain) unless this block intentionally overflows (popover host)' },
      state:   { axis: null, values: ['none', 'selected', 'potential', 'stacked'], default: 'none',
                 means: 'block state — selected (the gold rim-glow voice, one per view), potential (dashed ghost: a possible/future block), stacked (a deck of sheets). Each SKIN speaks these in its own language (tokens/skins.css).' },
    },

    // ORDERED sockets. `order` is the reading/flow order — the solver renders
    // occupants in this sequence; it is also the address order (body[0], body[1]…).
    // Content sockets accept typed things; ACTION sockets accept CV_ACTIONS verbs
    // by address ("action:<id>") — resolved by CV_NODE through the actions registry,
    // the same one-mechanic fill as every other socket.
    sockets: {
      header:  { order: 1, label: 'Header',  accepts: ['block', 'atom', 'glyphic', 'text'], optional: true,
                 means: 'title strip — first in reading order' },
      body:    { order: 2, label: 'Body',    accepts: ['block', 'atom', 'glyphic', 'text'], multiple: true,
                 means: 'the content run — blocks nest here; order of occupants = reading order' },
      footer:  { order: 3, label: 'Footer',  accepts: ['block', 'atom', 'glyphic', 'text'], optional: true,
                 means: 'meta strip — last in reading order' },
      primary: { order: 4, label: 'Primary action', accepts: ['action'], optional: true,
                 means: 'THE verb of this block (one gold voice per block, max)' },
      actions: { order: 5, label: 'Actions', accepts: ['action'], multiple: true, optional: true,
                 means: 'secondary verbs — ghost/quiet controls' },
      onActivate: { order: 6, label: 'On activate', accepts: ['action'], optional: true, event: true,
                 means: 'event socket — the action invoked when the block itself is activated (click/enter)' },
    },

    parts: {
      ground:  { type: 'block-ground' },
      surface: { type: 'block-surface' },
    },

    conditions: [
      'reel requires level != page',                       // a page never sideways-scrolls
      'primary requires level != page',                    // the page block has no single verb
    ],

    spec: {
      libraries: ['view.palette-color'],   /* the ladder lives on the LEVEL axis — read CV_BLOCK.levels() */
    },
    tags: ['block', 'container', 'zone', 'universal-component'],
  };

  R.registerMany(partTypes.map(function (t) { return Object.assign({ provenance: 'built-in' }, t); }), { silent: true });
  R.register(blockType, { silent: true });

  // ==========================================================================
  // THE BLOCK SOLVER — kind 'block' in CV_NODE. A resolved block IR → chrome:
  // { tag, classes, attrs, style } referencing ONLY system utilities/tokens
  // (.material + data-material, .keyline, .contain, .flow + data-flow, elev).
  // Layout stays with the existing engines (ContainmentTree for trees, the
  // .flow equation for counted groups) — this solver computes the SURFACE.
  // ==========================================================================
  function levelOf(id) {
    var v = LADDER().resolve(id || 'panel');   // loud on an unknown rung
    return Object.assign({ id: v.id }, v.meta);
  }

  // chrome(spec): spec = { level?, material?, tint?, groundTexture?, arrange?,
  // cols?, flow?, count?, keyline?, gap?, contain?, sockets? } — instance values
  // over the Type's defaults. EVERYTHING dimensional is either an axis value or
  // DERIVED from the rung — nothing hand-set escapes this function.
  function chrome(spec) {
    spec = spec || {};
    var lvl = levelOf(spec.level);
    var AX = window.CV_AXES;
    var mat = spec.material || 'skin';   // “skin” = the active skin's own surface (tokens/skins.css)
    var classes = [];
    var attrs = {};
    var style = {};

    if (mat !== 'none') {
      classes.push('material');
      if (lvl.modifier === 'raised') classes.push('material--raised');
      if (lvl.modifier === 'inset')  classes.push('material--inset');
      attrs['data-material'] = mat;
      // THE DEPTH COORDINATE emitted: the rung's rank from root becomes the
      // block's data-depth, which skins resolve to 3D physics (lift, bevel,
      // surface maps) — a zone within a zone is a level, and levels are depth.
      attrs['data-depth'] = String(lvl.rank);
    }
    // MORPH IDENTITY: the block's name is its stable identity for the morph
    // law (CV_MORPH.flip) — solver-rendered pages animate state changes for
    // free, nothing teleports.
    if (spec.name) attrs['data-morph-id'] = spec.name;
    if (spec.contain !== 'visible') classes.push('contain');

    // RUNG-DERIVED spacing rhythm — but the KEYLINE BELONGS TO SURFACES:
    // a material-'none' block is pure layout and must be TRANSPARENT to the
    // keyline (padding an invisible box double-insets its children and breaks
    // sibling alignment across nesting depths). The page is the one exception:
    // its keyline is the artifact's outer margin.
    if (mat !== 'none' || lvl.id === 'page') {
      classes.push('keyline');
      if (AX) style['--keyline'] = AX.css('space', spec.keyline || lvl.keyline);
    }
    var gapCSS = AX ? AX.css('space', spec.gap || lvl.gap) : null;

    if (spec.tint) attrs['data-glass-zone'] = spec.tint;            // the tonal whisper (home: tokens/glass.css §TINT)
    if (spec.groundTexture && spec.groundTexture !== 'none') attrs['data-ground-texture'] = spec.groundTexture;
    if (spec.density) attrs['data-density'] = spec.density;
    if (spec.state && spec.state !== 'none') classes.push('is-' + spec.state);

    // ARRANGE — the block's own layout, RESOLVED here (never hand-set by pages):
    //   flow  = counted group → the flow equation (tokens/layout.css §FLOW)
    //   split = declared column template
    //   stack = rows (the default when the body socket holds occupants)
    var arrange = spec.arrange || (spec.count ? 'flow' : (spec.cols ? 'split' : ((spec.sockets && spec.sockets.body && spec.sockets.body.length) ? 'stack' : 'none')));
    if (arrange === 'flow') {
      classes.push('flow');
      attrs['data-flow'] = spec.flow || (AX && AX.has('flow') ? AX.resolve('flow').default() : 'wrap');
      style['--count'] = String(spec.count || (spec.sockets && spec.sockets.body ? spec.sockets.body.length : 1));
      if (gapCSS) style['--flow-gap'] = gapCSS;
    } else if (arrange === 'split') {
      style['display'] = 'grid';
      style['grid-template-columns'] = spec.cols || '1fr 1fr';
      style['align-content'] = 'start';
      if (gapCSS) style['gap'] = gapCSS;
    } else if (arrange === 'stack') {
      style['display'] = 'grid';
      style['align-content'] = 'start';
      if (gapCSS) style['gap'] = gapCSS;
    }
    return { tag: 'section', level: lvl, arrange: arrange, classes: classes, attrs: attrs, style: style };
  }

  // walk(spec, fn): assign COORDINATES over a nested block spec — path from the
  // page root through named sockets, depth = ladder rank. fn(node, coord) per
  // block. Nothing hand-sets an address; composition IS the coordinate system.
  function walk(spec, fn, _path, _depth) {
    var path = _path || 'page';
    var depth = _depth != null ? _depth : 0;
    fn(spec, { path: path, depth: depth, level: spec.level || 'panel' });
    var kids = (spec.sockets && spec.sockets.body) || [];
    kids.forEach(function (child, i) {
      var name = child.name || ('body[' + i + ']');
      walk(child, fn, path + '/' + name, depth + 1);
    });
  }

  function blockSolver(ir, ctx) {
    var payload = (ctx && ctx.spec) || (ir.payload && ir.payload.id === undefined ? ir.payload : {});
    return chrome(payload);
  }
  // register the solver now if CV_NODE is up, else as soon as the page settles —
  // load-order tolerant (some pages load cv-node.js after the type files).
  function ensureSolver() {
    // check the kind-specific slot directly — hasSolver() also matches the '*'
    // fallback, which would silently skip this registration.
    if (window.CV_NODE && !window.CV_NODE._solvers.block) window.CV_NODE.solver('block', blockSolver);
    return !!window.CV_NODE;
  }
  if (!ensureSolver() && typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', ensureSolver);
  }

  // the public face, mirroring R.glyphic
  R.block = {
    type: function () { return R.resolve('block'); },
    levels: function () { return LADDER().values().map(function (v) { return Object.assign({ id: v.id }, v.meta); }); },
    chrome: chrome,
    walk: walk,
    ensureSolver: ensureSolver,
    // ordered sockets of the block type — the ONE place order is read from
    orderedSockets: function () {
      var t = R.resolve('block');
      return Object.keys(t.sockets).map(function (k) { return Object.assign({ name: k }, t.sockets[k]); })
        .sort(function (a, b) { return (a.order || 99) - (b.order || 99); });
    },
  };
  window.CV_BLOCK = R.block;
})();
