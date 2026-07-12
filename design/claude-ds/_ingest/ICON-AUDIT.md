# ConceptV icon source → library audit

Reference contact sheets (the WHOLE source, ingested): `_ingest/all-sheet-1.png`,
`_ingest/all-sheet-2.png`, `_ingest/contact-sheet.png` (named gold features),
`_ingest/contact-sheet2.png` (feature/system). Raw copies in `_ingest/src-all/` and
`_ingest/src-icons/`.

## The key finding
The `image (12)–(61)` set IS the authoritative master line-icon library — clean, **bold**
bronze strokes (~2px), generous rounding. This is the definitive reference; everything in
`cv-icons.js` (`window.CV_ICONS.data`, the live home) should match THESE, not approximations.
`image (62)` and `Staged_Delivery` are composites — skip. The gold-circle `Users1-6`, `V`, `Vi`,
`User_Portal`, `Property_Wizard`, `Virtual_Hub` are **entity-node treatments** (glyph inside a
circle/diamond/hex/octagon) — already supported via CvIcon `shape=` prop; they are NOT separate
glyphs.

## Master glyph inventory (image NN) → library status
- image13 / image25 — **people-network** (node cluster, lines). cv-icons: has `network`/`user-network` but NOT this clean people-cluster. **ADD `people-network`.**
- image16 — files/copy (two pages). = `files-stack` (OK, but source has folded corner — TIGHTEN).
- image19 / image47 — **stacked hex layers** (database). cv-icons `database` is a cylinder. **ADD `layers-stack` / re-look `database`.**
- image24 — **crane + building** (detailed). cv-icons `crane` is crude. **REDRAW `crane`.**
- image26 — building + $ = `building-dollar` (cv-icons OK-ish, compare).
- image27 / image59 / image60 — **skyline / house+towers (+tree)**. cv-icons `house-multi` crude. **REDRAW `house-multi` / ADD `skyline`, `house-trees`.**
- image29 — up/down arrows = transfer/sort. **ADD `transfer` (two vertical arrows).**
- image31 — **checklist-double** (stacked checked box). cv-icons only `check-square`. **ADD `checklist-double`.**
- image33 — comments **filled** variant. **ADD `comments-fill`.**
- image38 — flow: two cards + node line = `decision-tree`/`path-flow` (compare, source cleaner).
- image40 — **globe-network** (sphere w/ nodes). cv-icons `globe` is meridians only. **ADD `world-network`.**
- image43/44/45/46 — browser-window variants: house / house+text / analytics(pie+line) / house+info. cv-icons has `browser-house`,`browser-info`,`browser-chart` — **compare & tighten to source; ADD `browser-analytics` (pie+line).**
- image49 — brochure/open book = `brochure` (compare).
- image50 — monitor + 3d house = `monitor-house` (OK).
- image51 — **pen-in-square / 3d-print markup**. **ADD `markup-box` (distinct from current `markup`).**
- image57 — **parquet tile stack** (finishes/flooring). cv-icons `floor-pattern` is a plain grid. **ADD `tile-stack`.**
- image61 — **xyz axis house wireframe** (floorplan-3d). cv-icons `axes-3d` crude. **REDRAW `floorplan-xyz`.**
- MATCH (source confirms current is close): filter(30), file-list(34), file-upload(35), file-pdf(36), megaphone(37), cube-iso(39), handshake(41 — source better, TIGHTEN), pie-chart(42), info-circle(48), eye(52), eye-off(53), sitemap/hierarchy(54), image-stack(55), calendar(56), house(58), search(21/28), gear(20), dollar-circle/price(18), globe(23).

## Named gold feature set (contact-sheet*.png) — status after this session
DONE (added, decent): guided-tour, finishes, drone-view✱, day-night✱, filters, markup, stages,
lighting, unique, web, gyro, thumbs-up, comments, drone(redrawn), m2(redrawn), floorplan(redrawn).
**STILL ROUGH — REDRAW against source (priority):**
- `change-style` — source = **paint roller** dripping onto fanned chips. Current is too abstract.
- `convenient` — source = **open palm (palm-up) holding a clock above it**. Current hand is weak.
- `easy` — source = **thumbs-up inside a circle**. Current thumb cramped.
- `ownership` — source = **two forearms in a clasp/grip** (solidarity grip). Current reads as a mountain. (Consider: alias → improved `handshake` if clasp won't read.)
- `furniture` — source = **arc floor-lamp beside a 2-seat sofa**. Current lamp arc is awkward.
- `finishes` — source = tall sample board + fanned paint chips. Current OK, refine fan.

## Build order for next session
1. REDRAW the 6 rough feature glyphs above, screenshot each vs its `_ingest/src-icons/*.png` source.
2. ADD missing master glyphs: people-network, world-network, layers-stack, checklist-double,
   comments-fill, browser-analytics, markup-box, tile-stack, transfer; REDRAW crane, house-multi,
   floorplan-xyz, skyline, house-trees, handshake (tighten).
3. Regenerate `assets/icons/svg/` from final `CV_ICONS.data` (per-file SVGs for `<img>`/`<use>`).
4. Deprecate `icon-paths.js` + `ConceptVIcon.jsx` → re-point to `cv-icons.js` (single home; kill drift).
5. FINDINGS-LOG slice + `check_design_system` + `ready_for_verification('assets/icons/index.html')`.

## Already shipped this session (live in cv-icons.js / CvIcon.jsx / index.html)
Size-aware brand stroke (~1.55→2.0); alias map (square-meters=m2, settings=gear, price=dollar-circle,
users=people, maps=location-pin, info=info-circle, etc.); `CV_ICONS.brand` list + `resolve`/`get`;
node-shape containers (circle/hex/octagon/diamond) in CvIcon + explorer; explorer regrouped
(Brand vs System) with new categories + shape toggles.
