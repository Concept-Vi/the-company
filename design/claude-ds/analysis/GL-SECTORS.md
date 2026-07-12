# GL STONE — SECTOR LEDGER (from user side-by-side, m0510)

The user compared CSS stone (good reference) vs GL stone and mandated a full rebuild of the GL
plane. CSS plane is FROZEN (only --gl-* tokens may move). Every sector below must resolve from
the token cascade + block composition system — no bolted one-offs.

## Direct answers established
- **Is GL 3D?** Only barely. It is a real WebGL scene (perspective camera, lights), but cards are
  constant-thickness extruded slabs synced from DOM rects — parallel to the wall, no per-node
  depth from the composition, no nested zone geometry. Effectively 2.5D billboards.
- **Do block compositions generate their 3D versions?** NO — this is the root architectural gap.
  The GL sync reads top-level .material rects only. It must instead consume the SAME resolved
  block IR the CSS plane renders (containment ladder: wall → card → zone → detail), emitting one
  slab per rung with thickness from a token (`--gl-thickness-card`, `--gl-thickness-zone`, …).
  2D dimensions already law-governed; 3D adds only a thickness token per rung.

## Sector list (itemised)
1. **ALPHA/CHECKER BUG** — textures with alpha are uploaded as solid; transparent texels render as
   the checkered/blotchy pattern. Fix texture pipeline: correct format/premultiply, flatten onto
   the calibrated base colour before upload, or set material.transparent correctly. Highest
   visual severity.
2. **COMPOSITION → GEOMETRY** — GL must build from the block IR, one mesh per containment rung
   (cards AND zones AND wells), not from top-level DOM rects. Zones get their own small
   thickness token ("they'd size a little out").
3. **THICKNESS TOKENS** — per-rung extrusion depth resolved from the skin cascade
   (`--gl-thickness-*`), so one skin swap recalibrates the whole relief.
4. **MATERIALS PER RUNG** — wall/card/zone/active/ghost each bind their own diffuse+normal+
   roughness set from --gl-map-* tokens (the champagne-honed-stone + wall-plaster packs). Correct
   UV scale from the world-span law (texture px ↔ world px), not stretched-to-mesh.
5. **TEXTURE SCALE/QUALITY** — UV repeat must derive from physical span tokens (same
   decorrelation law as CSS: world-position offset per block). Currently cooked/stretched.
6. **LIGHTING RIG** — current rig reads flat and dead. Needs: soft key with warm bias (matching
   the CSS light direction law), ambient/env for material response, and calibrated via readback
   against the CSS plane's documented luminance ladder (wall 216 / card 240).
7. **DEPTH/CONTACT** — cards sit pasted on the wall: need real shadow-casting (soft shadow maps
   or baked contact AO) so slabs read as ON the wall; side faces shaded darker (side-face 120 on
   the role ladder).
8. **ZONES MISSING ENTIRELY** — the nested tonal zones visible in CSS don't exist in GL. Falls
   out of sector 2, but verify tonal ladder (ghost 190 / card 215 / active 216 / detail 224)
   reproduces under GL lighting.
9. **CAMERA** — must obey the world-camera law (pan/zoom parity with CSS plane) so the two planes
   are the same world at the same coordinates.
10. **CALIBRATION HARNESS** — numeric readback loop comparing GL frame vs CSS good-state ladder;
    plus visual side-by-side when screenshot capture returns (todo 86/90).

## Order of attack
2 → 3 (geometry from IR + thickness tokens) first — everything else lands on that skeleton.
Then 1 (alpha pipeline), 4/5 (materials+UV), 6/7 (light+shadow), 8 verify, 9 camera, 10 calibrate.
