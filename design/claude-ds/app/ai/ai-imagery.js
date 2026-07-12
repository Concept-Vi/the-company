// app/ai/ai-imagery.js
// ============================================================================
// Registers the IMAGERY move into CV_AI — skin-conditioned render generation
// for block wells. One capability:
//
//   imagery.render — generate an in-card RENDER (a product/object image) whose
//                    lighting, palette and mood are COMPUTED FROM THE ACTIVE
//                    SKIN's tokens (the gold role, shadow warmth, ground colour
//                    → lighting words), so the same slot re-generates a stone-
//                    world or glass-world image when the skin flips. The prompt
//                    is the generator; a delivered file is one resolution of it.
//
// SINGLE SOURCE: the skin descriptors come from the skin axis + tokens/skins.css
// at prompt-build time (never copied); image bytes come ONLY through
// CV_AI.resolveProvider('openai-image') (loud-fail if absent) — never a direct
// window.cvOpenAI call. (analysis/SKINS.md §7b · CLAUDE.md §2.)
//
// Load after ai-registry.js (+ axes).
// ============================================================================
(function () {
  'use strict';
  var AI = window.CV_AI;
  if (!AI) { console.error('ai-imagery.js: CV_AI must load first'); return; }

  // the per-skin lighting/palette descriptor — READ from the skin axis meta
  // (single source: axes/skin/skin-axis.js). No inlined skin adjectives.
  function skinDescriptor(skinId) {
    var AX = window.CV_AXES;
    if (!AX || !AX.has('skin')) throw new Error('imagery.render: skin axis not loaded');
    var v = AX.resolve('skin').values().filter(function (s) { return s.id === skinId; })[0];
    if (!v) throw new Error('imagery.render: unknown skin "' + skinId + '"');
    var m = v.meta || {};
    // the world descriptor + a ground/material phrase drive the lighting words
    return {
      world: m.world || v.label,
      ground: m.ground || 'neutral',
      material: m.material || 'matte',
      renderWorld: m.renderWorld,
    };
  }

  // ---- THE CAPTURED GENERATOR (assets/renders/PROMPTS.md) -------------------
  // The user's original ChatGPT prompts, decomposed into a shared SKELETON plus
  // per-world PALETTE fragments — data keyed by the skin's renderWorld meta,
  // never inline adjectives in the call path. Extending: add a world entry.
  var RENDER_SKELETON = 'Abstract product render on a true transparent background, premium editorial 3D object, three-quarter view, consistent top-left key light with soft fill, clean silhouette, no text, no room, no props';
  var WORLD_PALETTES = {
    // exact fragments from pack-001 prompts/object-renders.md — the strings that
    // produced the shipped assets, so regeneration matches the delivered set.
    stone: 'warm champagne stone world, ivory and travertine palette, pale limestone, plaster and marble cues, matte to soft-satin finish, gentle warm highlights, occasional restrained gold seam accent',
    glass: 'cool glass-dark world, smoked blue-black glass, obsidian, graphite and steel cues, polished surface, translucent edges, cool reflections, restrained blue specular highlights',
  };
  var EXPORT_RULE = 'True RGBA transparent background. If true alpha is unavailable, render on flat chroma green only. Never use checkerboard. Never bake a drop shadow into the background.';

  function buildPrompt(a) {
    var p = a.params || {};
    var subject = p.subject || a.subject || 'an architectural monolith form with gentle faceting and a stepped base';
    var skin = p.skin || (a.ctx && a.ctx.skin) || 'stone';
    var d = skinDescriptor(skin);
    var world = d.renderWorld || (/stone|plaster|parchment|linen/.test(d.ground + d.world) ? 'stone' : 'glass');
    var palette = WORLD_PALETTES[world];
    if (!palette) throw new Error('imagery.render: no palette fragment for world "' + world + '" — add it to WORLD_PALETTES');
    return RENDER_SKELETON + ', ' + subject + ', ' + palette + ', elegant and minimal, suitable for a direction card object render. ' + EXPORT_RULE;
  }

  AI.register({
    id: 'imagery.render', name: 'Render (skin-conditioned)', layer: 'capability', family: 'imagery',
    surfaces: ['blocks', 'canvas', '*'], behaviours: [], role: 'image',
    params: { subject: '', skin: 'stone' }, icon: 'image', provenance: 'built-in',
    description: 'Generate an in-card render whose lighting/palette/mood are computed from the active SKIN\u2019s tokens; flip the skin and the same slot re-renders in the other world. Prompt from the skin axis; bytes via the openai-image provider.',
    build: buildPrompt,
    run: function (a) {
      var prompt = buildPrompt(a);
      var prov = AI.resolveProvider('openai-image'); // loud-fail if absent
      if (!prov || typeof prov.generateImage !== 'function') throw new Error('imagery.render: openai-image provider has no generateImage()');
      return prov.generateImage({ prompt: prompt, size: (a.params && a.params.size) || '1024x1024', background: 'transparent' });
    },
    tags: ['imagery', 'skin', 'generative'],
  }, { silent: true });
})();
