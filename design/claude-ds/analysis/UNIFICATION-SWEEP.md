# UNIFICATION SWEEP — the connection inventory
> The audit of every law × every consumer: what is wired, what is NOT, and connections
> that must be made OUTSIDE this project's scope (recorded here because nowhere else
> will). Slice 156. Update this file as connections land — it is the sweep's ledger.

## 0. How to read
Each law has ONE home. A ✅ consumer resolves through it; a ❌ is an unmade connection
(drift risk: that surface will hand-set what the law computes); a ◐ is partial.

## 1. The laws and their consumers
> Slice 157 sweep: every ❌ below marked ✓157 has been wired — see FINDINGS-LOG slice 157 for the joints.

| Law (home) | skin-system demo | app/index.html (flagship) | templates/* | Slide/RenderType engines | DiagramSolver | React components | specimens/cards |
|---|---|---|---|---|---|---|---|
| Skins re-bind roles (`tokens/skins.css`) | ✅ dial | ❌ no `data-skin`/`skin-ground` scope | ❌ predate skins | ❌ | ◐ edge tokens only | ◐ glass tokens only | ❌ |
| Depth ladder `data-depth` (skins.css) | ✅ chrome() stamps | ❌ blocks unstamped | ❌ | ❌ | ❌ | ❌ | ❌ |
| Cross-depth tone (`--depth-tint`) | ✅ | ❌ (needs depth stamps) | ❌ | ❌ | ❌ | ❌ | ❌ |
| World sampling `--mat-tex-pos` (material.css) | ✅ but stamp loop is DEMO-LOCAL | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Asset span fields `--span-*` (skins.css) | ✅ | auto (CSS) once ground exists | auto | auto | auto | auto | auto |
| World camera derive+moves (`core/world-camera.js`) | ✅ | ◐ script loaded, no `.skin-ground` to couple | ❌ | — | — | — | ❌ |
| Morph law flip/crossfade/expand (`core/morph.js`) | ✅ all three | ❌ transitions still hard swaps | ❌ | ❌ | ❌ morph type re-renders, no FLIP | ❌ | — |
| Ratio-fit (`core/layout-fit.js`) | ✅ wells | ❌ | ❌ | ❌ media atoms letterbox | — | ❌ Card media | ❌ |
| Block chrome() (`app/registry/block-type.js`) | ✅ | ◐ registry loaded; canvas blocks partially resolve | ❌ hand-laid | ◐ | ❌ | ❌ | ◐ |
| Text-type ladder (`tokens/text.css` + text-type.js) | ✅ | ◐ | ❌ | ◐ | ❌ node labels | ❌ | ◐ |
| Glyphic compose w/ skin gold | ✅ satellites | ◐ | ❌ | ◐ | ❌ | ✅ Glyphic comp | ◐ |
| Pigment translation per skin | ✅ | ❌ (needs skin scope) | ❌ | ❌ | ❌ | ❌ | ❌ |
| render3d token-lit wells (`core/render3d.js`) | ✅ | ❌ | ❌ | ❌ | — | — | ❌ |
| Actions registry sockets | ✅ corner affordance | ◐ | ❌ | ❌ | — | ◐ Button | — |
| AI capabilities emit through laws (`CV_AI`) | — | ◐ block gen exists; emits no depth/skin stamps | ❌ | ◐ | ◐ | — | — |

## 2. The priority order (each unlocks the next) — ALL LANDED (slices 156–157)
1. ✓ stamp loop → camera home. 2. ✓ flagship skin scope + studio World dial (Settings).
3. ✓ templates: ds-base.js sets the skin scope (inert glass default, never overrides authored).
4. ✓ engines: cv-zone stamps data-depth from nesting (coordinate always; physics binds to .material);
   image atoms resolve --asset-ar via ratio-fit when src given; .dgm-node positions tween via motion
   tokens (the morph type animates). 5. ✓ chrome() emits data-morph-id (+ data-depth it already had) —
   generator output resolves identically to authored blocks. 6. ✓ Card carries data-material="skin";
   [data-skin] .cv-card consumes the material slots (un-skinned pages byte-identical).

## 3. Out-of-scope connections (recorded HERE because nowhere else)
These need actors other than this design system's own files:
- **Claude Code sessions** consuming the DS: must load `_ds_bundle.js` (gets all laws) AND
  add `.skin-ground data-skin` on their page scope + call `CV_WORLD_CAMERA.observe/stampMaterials`
  after their own layout passes. Document lives in SKILL.md — needs a §"Skinned pages" addition.
- **ChatGPT asset pipeline** (Vi's account): future texture packs must declare a WORLD-SPAN
  field per asset (physical coverage, px at zoom 1) in their manifest — the system consumes it
  as `--span-*`; without it every new asset needs hand-tuning. Also still open: authored
  (non-segmented) alpha for object renders; per-skin brass/metal accent materials.
- **Topaz upscale** (user offered): only worthwhile for the 1024² lit bakes if cards render
  >500px wide at zoom 1 — revisit when the flagship ships skins.
- **A real lighting library** (three.js already vendored for render3d): page-wide light pools /
  normal-mapped wall lighting would replace the baked-texture approximation. Decision recorded:
  stay scoped-per-well until the flagship consumes skins; then evaluate a `light-field` kind.
- **Consuming projects** (other repos binding this DS): their pages get laws only via the bundle;
  the `ds-base.js` template loader covers CSS+bundle but pages must add the skin scope themselves.
- **Fonts**: check_design_system reports "Fonts: (none)" — Sora/DM Sans/JetBrains Mono load from
  Google at runtime; offline/export contexts need @font-face with local files (an asset request).

## 4. Verification bar for "everywhere"
A surface counts as unified when: flipping `data-skin` restyles it completely; its blocks carry
`data-depth` + `data-morph-id`; its textures show unique grain per block; its media never
letterboxes; its state changes animate through CV_MORPH. The flagship is the reference proof.
