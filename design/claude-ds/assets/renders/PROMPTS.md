# Render / imagery generation prompts — the GENERATOR

> A delivered file is one resolution; the prompt is the generator. These are the
> prompt fragments the `imagery.render` capability (app/ai/ai-imagery.js) composes
> from the active skin's tokens, so the system regenerates skin-matched art rather
> than us hand-collecting files. Capture the ChatGPT session's originals here as
> they arrive; the template below is what the capability emits today.

## ROUND 3 — requested (Jul 2026): depth-slot materials + remaining maps
All tileable, ~2048², flat lighting, no vignette/shadow baked, WebP preferred.
Each texture becomes a SLOT value (tokens/skins.css) already wired and bound to an
existing texture — delivery is a one-token path swap per file.

**Depth-slot surface textures** (the "few for different zone/depth types"):
1. `plaster-fine.webp` — same champagne plaster family but FINER grain (for wells/
   inset zones — reads as sanded/worked stone vs the wall's rough tooth).
2. `plaster-polished.webp` — near-smooth honed stone, faint mottle (overlay/raised
   blocks — the most worked surface sits closest to the viewer).
3. `paper-fine.webp` — tighter vellum fiber (parchment wells).
4. `graphite-fine.webp` — finer brushed graphite (carbon wells).

**Relief maps (for the 3D wells + future CSS relief):**
5. `graphite-normal.png` + `graphite-roughness.png` — same tile as graphite diffuse.
6. `glass-normal.png` — near-flat micro-ripple normal (subtle; for glass 3D wells).

**Optional range-proof:**
7. `ink-depth-deep.webp` — a second darker atmospheric ground (glass/carbon range).

## The camera rule (for reference, lives in tokens/skins.css)
--world-zoom is DERIVED, not hand-set: zoom = stageWidth / designFrameWidth (1440px
reference frame), so texture scale follows the frame exactly like a camera moving
toward/away from the wall. Set by the one resize observer on the skin ground.

## The computed template (imagery.render)
Built from the skin axis meta (world · ground · material) — never hand-written per call:

```
Product render, transparent background (cutout), centered, 3/4 view.
Subject: <subject>.
Material read: <skin.material>.
Lighting: soft key from upper-left, <warm ? "warm champagne studio light, gentle
  warm ambient shadow — never black" : "cool blue rim light on a dark studio field,
  crisp specular highlights">.
Palette: <warm ? "warm travertine / porcelain neutrals, antique-gold accents"
  : "blue-steel glass, graphite, cool highlights">.
Consistent with a <skin.world> world laid on a <skin.ground> ground.
No text, no props, no floor.
```

`warm` derives from the skin's ground/world (stone/plaster/parchment → warm; glass → cool).

## Delivered render set (Jul 2026, user ChatGPT session)
Stone (warm): stone-ball, stone-arch, stone-podium, stone-monolith, stone-cloth.
Glass (cool): glass-blobs, glass-hourglass, glass-slabs, glass-columns, glass-twist.
Grounds: plaster, ink-depth, linen. Overlays: foliage-shadow, light-pool.

## TODO — capture the originals
Paste the exact ChatGPT prompt strings used for the plaster ground and the renders here,
so imagery.render can be tuned to reproduce them and the loop closes.

## ROUND 2 — requested from the user's ChatGPT session (Jul 2026)
Audit of round 1: matched stone/glass render pairs ✓; plaster/ink-depth/linen grounds ✓.
Problems found: (a) every "transparent" PNG had a FAKE checkerboard baked in — no real
alpha (fixed by flood-fill keying, but edges are keyed, not authored); (b) light-pool
arrived as an opaque white wash, unusable as a screen overlay — retired; (c) file #2
corrupt. Round-2 wants:

1. RE-EXPORTS WITH REAL ALPHA (or on a single flat #00FF00 ground for clean keying):
   the 10 object renders + foliage-shadow. Never a checkerboard background.
2. LIGHT-POOL redo: soft radial window-light bloom, WHITE shapes on true transparent,
   heavy feather — for `screen` compositing over any wall.
3. plaster-cool.png — greige/cool plaster variant (proves ground is a range).
4. paper-fiber.png — close-up warm paper/vellum fiber, tileable (parchment card tile).
5. graphite.png — dark machined/brushed graphite, tileable, very low contrast
   (carbon skin's card surface option).
6. FOR THE 3D RUNG (r3f, approved): plaster-normal.png + plaster-roughness.png —
   same tile as the plaster diffuse (normal = purple-blue tangent map; roughness =
   grayscale, white = rough). Same pair for linen if easy.
7. THE PROMPTS: the exact prompt text used for the plaster wall and for one stone
   render and one glass render (paste under "captured originals" below).
## ROUND 5 REQUEST — plaster family REGENERATION (Jul 2026, m0493)
Pack-004's plaster materials are REJECTED: warm-plaster-wall, cool-plaster-wall and
fine-sanded-plaster all carry a baked DIAMOND/WEAVE LATTICE in diffuse + displacement +
ao + normal (see _qa/map-inspection-board.png) — the generator drew woven canvas, not
plaster. champagne-honed-stone / fine-laid-paper / fine-graphite are CLEAN and accepted.

Message to ChatGPT:
"Regenerate 3 PBR materials from pack-004 with the same contract (2048×2048, co-registered
diffuse.webp unlit albedo + normal(+Y).png + roughness.png + ao.png + displacement.png,
worldSpanPx in manifest: 1250 / 1250 / 460): warm-plaster-wall, cool-plaster-wall,
fine-sanded-plaster. HARD NEGATIVES, previous set failed QA on these: no woven/canvas/
fabric texture, no diamond or checkerboard lattice, no repeating diagonal weave, no
regular geometric pattern of ANY kind. Plaster is IRREGULAR: soft trowel sweeps, fine
sanded stochastic grain, subtle pitting and hairline variation, organic non-repeating
structure. Verify by inspecting the displacement map at 100% — if any grid/weave/diamond
pattern is visible, regenerate before delivering."

## Captured originals (paste here)
Delivered Jul 2026 via vi_skin_assets_pack (full text in that pack's prompt-fragments.md,
mirrored here as the imagery.render tuning source):
- **Plaster wall**: "Seamless tileable material texture, 2048², warm champagne plaster wall …
  matte mineral finish, subtle trowel variation, faint chalky grain, very low contrast tonal
  drift, flat even lighting, no cast shadows, no vignette, no perspective, no focal object,
  suitable as a UI ground texture."
- **Stone render**: "Abstract product render on a true transparent background, premium editorial
  3D object, three-quarter view, consistent top-left key light with soft fill, clean silhouette,
  no text, no room, no props … warm stone-world palette of ivory, travertine, pale plaster and
  soft limestone, matte to soft-satin finish, restrained highlights."
- **Glass render**: same skeleton, "… cool dark glass-world palette of smoked glass, graphite,
  obsidian and subtle steel, polished translucent edges, restrained blue-grey reflections."
- **Export rule**: true RGBA; else flat bright-green chroma ground; NEVER checkerboard.

Round-2 pack assessed: grounds plaster-cool/paper-fiber/graphite ✓ (assets/textures/),
overlays foliage-shadow-v2 + light-pool-v2 TRUE ALPHA ✓ (metadata-verified), r3f maps
plaster/linen normal+roughness ✓ (assets/textures/maps/).

## Pack-001 ingestion (Jul 6 2026) — round 1 item 1 RESOLVED
vi-skin-and-card-render-pack-001 delivered the 10 object renders as 2048² TRUE RGBA
(code-segmented edges — the pack's QA report is honest that they're machine-matted, not
authored; acceptable at well sizes). Copied ONTO the existing assets/renders/ names
(monolith→stone-monolith/glass-columns · pedestal→stone-podium/glass-slabs ·
arch→stone-arch/glass-hourglass · blob→stone-ball/glass-blobs · ribbon→stone-cloth/
glass-twist) so every token and card picked them up with zero edits. The pack's refined
prompt fragments (see its prompts/*.md) are synced VERBATIM into imagery.render's
WORLD_PALETTES + EXPORT_RULE. New overlays active-trace-glow + card-lift-shadow staged in
assets/textures/ (not yet consumed). Authored edges / Topaz upscaling: only if a render
ever ships at large scale.


## Round 4 request — PBR material pack (sent Jul 2026, "vi-pbr-material-pack-004")
For the WebGL pipeline (core/render-scene.js). Per material (champagne-honed-stone, fine-sanded-plaster,
fine-laid-paper, fine-graphite + warm/cool plaster walls): co-registered 5-map PBR set —
diffuse.webp 2048² tileable UNLIT + normal(+Y).png + roughness.png + ao.png + displacement.png.
manifest.json is the CONTRACT: per asset { id, role, worldSpanPx, maps:{diffuse,normal,roughness,ao,displacement} }.
worldSpanPx = CSS-px footprint of one tile at zoom 1 (walls ≈1250, card faces ≈460, fine paper ≈350) —
required; the engine (--span-* tokens + GL repeat) scales from it automatically.
Negatives: no baked lighting/shadows/vignette, true seamless tiling, no checkerboards/watermarks.
Full message text in chat (m0421 reply).
