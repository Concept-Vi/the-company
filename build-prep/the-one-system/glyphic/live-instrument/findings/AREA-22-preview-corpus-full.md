# AREA-22 — The full `preview/` specimen corpus (read in full)

**Lens (Tim):** nothing canonical; duplications kept + catalogued by unique quality (fuse-not-pick);
DESCRIPTIVE only. Every claim marked **Observed (file:line)** or **Inferred**.

**Coverage:** all 25 files in my territory read in full. The 4 wave-3 *sampled* files
(`brand_voice`, `colors_bronze`, `components_sidebar`, `spacing_elevation`) are re-read here in full so the
record is complete. `icons_tones.prompt.md` is a 2-line stub (`# ` + blank — Observed,
`icons_tones.prompt.md:1-2`).

This corpus is a set of **design-system "cards"** — each a tiny self-contained HTML page that *shows one
facet of the look*. They are NOT mockups of product screens; they are the **specimen sheets** that depict the
tokens/treatments the rest of the corpus references. Note: `preview/` is a *different* directory from the
charter's `mockups/` — these cards `@import`/`<link>` a **local** `_card.css` (which imports
`../colors_and_type.css`), not the generated `../design-system.css`. **Inferred:** `preview/` is the
**design-system gallery** (the look itself, sheet by sheet), distinct from the grounded product mockups.

---

## (a) The specimen families + what each treatment shows

There are six families. Each family is a *parallel set of treatments of one design dimension* — exactly the
fusion raw material the lens is after.

### Family 1 · BRAND (identity)
- **`brand_mark.html`** — the **V mark in three placements** (Observed `brand_mark.html:16-20`): yellow-on-canvas
  | white-on-gold | yellow-on-dark. The treatment shows: *the mark is the same asset, recoloured by ground*
  (`conceptv-v-yellow.png` reused in panes 1 & 3; `conceptv-v-white.png` on the gold pane). A **placement-by-ground
  rule**: which asset to use is a function of the surface it lands on. Panes are `--bg-canvas` / `--accent-gold`
  / `--bg-dark` (Observed `:7-9`).
- **`brand_wordmark.html`** — the wordmark on canvas vs dark (Observed `brand_wordmark.html:16-22`); on dark the
  rule is **"switch to the V mark"** (the dark pane swaps `conceptv-wordmark-black.png` → `conceptv-v-yellow.png`,
  Observed `:20`). A **conditional-substitution rule** (the asset *changes identity* by ground, not just colour).
- **`brand_voice.html`** — voice & tone as **use/avoid pairs** (Observed `brand_voice.html:24-41`): precise,
  second-person, sentence-case, no marketing voice / no exclamation / no emoji in copy (Observed `:23`). The
  "Use" cards are tinted with `--status-success`, "Avoid" with `--status-error` (Observed `:14-15`) — i.e. the
  status palette is **reused as a do/don't semantic**, not just for system states.
- **`brand_emoji_nav.html`** — the sidebar convention: **CV line icons stroked in a token colour, NEVER emoji**
  (Observed `brand_emoji_nav.html:21,27`). Icons pulled live from `window.CV_ICONS.data` (Observed `:37,42`),
  stroked `--accent-bronze` default, `--accent-gold` on the active row (Observed `:23-24`).
- **`brand_icons_bronze.html`** — the **bronze line-icon library** (~80 glyphs), shown as a *raster image of the
  sheet* (`assets/icons/icon-library-bronze.jpg`, Observed `:14`), with meta: colour `#988058`, stroke ~1.5px,
  round caps, no fill (Observed `brand_icons_bronze.html:16-20`).
- **`brand_icons_gold.html`** — the **gold-circle icon family** (glyph inside a thin gold ring, uniform size),
  also a raster sheet (`assets/icons/icon-library-gold-circles.jpg`, Observed `:14`). Meta: ring 1.5–2px, sizes
  32/48/64; notes the **top row is "the canonical state-strength gradient"** (a desaturation row) — Observed
  `brand_icons_gold.html:13`.

### Family 2 · COLORS
- **`colors_gold.html`** — gold as the **active/decision accent**, 6 interaction tiers (gold-50 → gold-press),
  and explicitly *"a ramp (gold→bronze→tan, `--ramp-1..4`) used to position sequence & depth"* (Observed
  `colors_gold.html:14-21`). The chips here are **raw hex literals** (`#FBF6DC` … `#9C8413`, Observed `:16-21`),
  not `var()`s.
- **`colors_bronze.html`** — bronze as the **structural / quiet voice**, a bronze→tan scale of 6 (Observed
  `colors_bronze.html:35-42`). Uniquely, the values are **sourced** — "sampled directly from the source brand
  vectors (`_ingest/src-all/*.svg`)" with *counts* (`#99885e ×42`, `#7b7055 ×8`, `#c7a961 ×7`) shown per chip
  (Observed `:33,36-41`). Chips here use **`var()`s** (`var(--accent-bronze-deep)` … `var(--accent-bronze-2)`,
  Observed `:36-41`) — unlike `colors_gold`'s raw hex. Foot shows the gold→bronze ramp dots and a "Brand Kit"
  title demo at 36px display in bronze (Observed `:44-53`).
- **`colors_ink.html`** — ink (warm near-black, never pure black), 4 tiers primary/secondary/muted/inverse, each
  shown as an "Aa" on white (Observed `colors_ink.html:16-21`). Raw hex (`#1F1A12`…`#FBF7EC`, Observed `:17-20`).
- **`colors_surface.html`** — 5 warm surface layers canvas/surface/muted/sunken/dark, with a "no cool greys, no
  pure white page bg" rule (Observed `colors_surface.html:16-22`). Raw hex.
- **`colors_status.html`** — 5 status colours success/warning/error/info/pending, **warm-shifted & desaturated**
  to sit in the ivory palette; "Pending uses gold, not amber" (Observed `colors_status.html:16-22`). Each chip is
  a {bg + dot + pill} triple showing the *applied* form (e.g. "Approved" / "Review" / "Rejected"), so it doubles
  as a **status→label semantic map** (Observed `:18-22`). Raw hex throughout.

### Family 3 · TYPE
- **`type_display.html`** — Sora 700 hero specimen, 76px, tracking −2.5%, gold accent span (Observed
  `type_display.html:6-12`). For hero + screen titles.
- **`type_body.html`** — DM Sans, the UI default, with a **glyph specimen** (A–Z, a–z, 0–9 & @ ↗) and weights
  400/500/600/700, optical sizing 9–40 (Observed `type_body.html:25-32`).
- **`type_mono.html`** — JetBrains Mono for URLs/IDs/code; shows a URL with gold + muted spans and a dark code
  block (Observed `type_mono.html:20-23`).
- **`type_scale.html`** — the **9-step ramp** Display(48/700) → H1(36/700) → H2(28/600) → H3(22/600) →
  H4(17/700) → Body(15/400) → Body-sm(13/400) → Caption(11/500) → Eyebrow(11/600, bronze, uppercase) — Observed
  `type_scale.html:15-23`. Sizes are **inline literal `font-size`/`font-weight`** on each row (Observed `:15-23`).
- **`type_screen_title.html`** — the **dashboard H1 pattern**: display 700 at ~38px in **bronze (#988058), not
  gold** (Observed `type_screen_title.html:7,12`). Shown as two stage examples ("Brand Kit", "Virtual Hub
  Settings") with subtitles (Observed `:13-22`).

### Family 4 · SPACING / PROPORTION
- **`spacing_scale.html`** — 8-px base grid, 11 steps `--s-1`..`--s-24` (4 → 96px), drawn as gold bars; rule:
  component padding 16–24, section gutter 32–48 (Observed `spacing_scale.html:14-26`). Step names are token
  names; bar widths are inline px literals (Observed `:16-26`).
- **`spacing_radii.html`** — 6 radius tiers xs(4)/sm(6)/md(8★)/lg(12)/xl(16)/pill(999), with a usage rule per
  tier (chips/checkboxes 4–6, buttons/inputs 8, cards 12, popups 16, only status-dots+Chats-button pill) —
  Observed `spacing_radii.html:15-22`.
- **`spacing_elevation.html`** — the richest spacing sheet: a **9-tier warm-bronze elevation scale**
  (`--lux-0`..`--lux-modal` + `--lux-glow-gold`) defined as **layered shadow recipes** in a local `:root`
  (Observed `spacing_elevation.html:34-78`). Each tier = hairline contact + warm bronze ambient pass(es) + inset
  top-light (Observed `:30-33,305-313`). Tiers map to **roles**: 00 Resting / xs rows / sm chips-badges /
  md★ default-card / lg hover-selected / xl featured-hero / pop popovers-menus-chat / modal dialogs-drawers /
  gold-glow primary-action (Observed `:212-300`). Carries an explicit **discipline footnote**: "step one tier at
  a time on hover; never combine glow with modal; never stack md on md — escalate to lg" (Observed `:314-318`).

### Family 5 · COMPONENTS
- **`components_buttons.html`** — 5 variants primary/outline/dashed/ghost/dark + sm/lg sizes + disabled (Observed
  `components_buttons.html:54-179`). Heavy on the **layered-fill + warm-shadow + inset-highlight** language
  (gradient overlay + `--accent-gold`, multi-layer box-shadows). Rule: "gold earns attention once per surface"
  (Observed `:186-188`). The **dashed** variant carries the brand's signature dashed-gold idiom (Observed
  `:108-122`). Mixes `var()`s (`--accent-gold`, `--ease-out`) with **raw rgba literals** in the shadows
  (Observed `:48-50,57-65`).
- **`components_inputs.html`** — text/search/checkbox/textarea, gold focus ring, **inline URL-preview helper**
  (`URL preview: https://conceptv.io/...`, Observed `components_inputs.html:41`). Checkbox is a gold box with a
  CSS-drawn tick; off-state uses `--accent-gold-soft` (Observed `:24-34`). Search icon is an **inline SVG data-URI**
  stroked `%23A89678` (= bronze-muted, Observed `:19`).
- **`components_sidebar.html`** — sidebar nav states default/hover/active, where **active = white fill + dashed
  gold outline** ("the brand's signature selection treatment", Observed `components_sidebar.html:32`). Icons from
  `CV_ICONS.data`, **each tinted to its own section hue** (teal/charcoal/blue/gold/charcoal/pink — Observed
  `:38-45`) — i.e. a *per-section colour assignment* on top of the icon set.

### Family 6 · INFRASTRUCTURE (not a visual specimen)
- **`_card.css`** — the **shared frame** every card links. Imports `../colors_and_type.css`; defines `.card`,
  `.card-row`, `.card-grid`, `.label`, `.mono` using `var()`s only (Observed `_card.css:1-32`). This is the one
  place the cards single-source their chrome.
- **`image-slot.js`** — a **user-fillable image-placeholder web component** (`<image-slot>`), the only behavioural
  artefact here. Detailed in (c) below — it is structurally the most relevant file to a live interactive surface.
- **`icons_tones.prompt.md`** — empty stub (Observed `icons_tones.prompt.md:1-2`).

---

## (b) DUPLICATE / parallel treatments of the same concept + each one's unique quality (fusion raw material)

This is the heart of the lens. The corpus carries **the same concept treated several ways**. Catalogued, never
collapsed:

### Bronze appears in FOUR distinct roles (one colour, four jobs)
1. **Structural/quiet voice** (`colors_bronze.html:33`) — the scale itself, *source-sampled with counts*.
2. **Nav-glyph default stroke** (`brand_emoji_nav.html:23` — `stroke: var(--accent-bronze)`).
3. **Screen-title colour** (`type_screen_title.html:7,12` — H1s are bronze, explicitly *"not gold"*).
4. **The icon library's own ink** (`brand_icons_bronze.html:13,16` — `#988058`, the printed sheet colour).
   **Fusion value:** bronze is not "a colour" — it's the *quiet/structural register* that surfaces as scale,
   stroke, title, and library-ink. A glyphgraph could treat bronze as the **structural-edge / scaffolding hue**.

### Two ICON systems, parallel (kept, not picked)
- **Bronze line-icons** (`brand_icons_bronze.html`) — ~80 mono-stroke glyphs, no fill, the *working/diagram* set.
- **Gold-circle icons** (`brand_icons_gold.html`) — glyph-in-a-ring, "count as a system component", with a
  desaturation **state-strength gradient** row.
  **Fusion value:** the *same glyph* can be presented as a bare stroke (quiet, structural) OR ringed+gold
  (elevated, "counts as an entity"). That is **two facet-states of one symbol** — directly the glyphic idea
  (form constant, fill/outline/colour carry state). The gold-circle's *desaturation gradient* (Observed
  `brand_icons_gold.html:13`) is a ready-made **state-strength channel**.

### Icon COLOUR rule is treated THREE different ways across specimens
- **Single token default** — bronze stroke, gold when active (`brand_emoji_nav.html:23-24`).
- **Per-section hue** — each nav item carries its own colour (teal/charcoal/blue/gold/pink) (`components_sidebar.html:38-45`).
- **Library-fixed** — the printed sheets are one fixed colour each (`brand_icons_bronze.html:16`, gold ring on the other).
  **Fusion value:** three live policies for "what colour is a glyph" — *role-default*, *category-keyed*,
  *fixed-by-asset*. A glyphgraph's colour-resolution can offer all three as modes rather than choosing one.

### The DASHED-GOLD selection idiom recurs in THREE places
- Active nav row (`brand_emoji_nav.html:19` — `border: 1.5px dashed var(--border-dashed)`).
- Active sidebar item (`components_sidebar.html:32` — "white fill + dashed gold outline … signature selection").
- Dashed button variant (`components_buttons.html:108-122`) and dashed chip-borders.
  **Fusion value:** "dashed gold = selected/optional/provisional" is a **cross-component selection semantic** —
  a candidate **glyphic edge/outline state** for "active" or "tentative".

### Color chips are authored TWO ways (the literal-vs-var split — a drift signal AND a fusion seam)
- **Raw hex literals** in the chips: `colors_gold` (`:16-21`), `colors_ink` (`:17-20`), `colors_surface`
  (`:18-22`), `colors_status` (`:18-22`).
- **`var()` tokens** in the chips: `colors_bronze` (`:36-41`).
  **Inferred:** `colors_bronze` is the *more evolved* sheet (source-traced + tokenised); the others still carry
  the look as literals. Under the design-system charter the literals are *legitimate token definitions on a
  specimen sheet* (the sheet's job is to SHOW the value) — but they are **two parallel ways of expressing the
  same palette**, and the bronze sheet is the pattern the others would converge toward. **This is the cleanest
  in-corpus example of the same-concept-two-treatments the lens wants catalogued.**

### Status palette is REUSED as a do/don't semantic
- As system states (`colors_status.html`).
- As voice "Use"=success-green / "Avoid"=error-red (`brand_voice.html:14-15`).
  **Fusion value:** the status hues already carry *evaluative* meaning beyond state — a glyphgraph could bind
  them to "good/bad/needs-review" judgements, not only lifecycle.

### "Ramp" appears as BOTH a colour-sequence AND a depth/position device
- `colors_gold.html:14` calls gold "a ramp (gold→bronze→tan, `--ramp-1..4`) used to position sequence & depth".
- `colors_bronze.html:47-53` shows the ramp dots "continuing into the gold→bronze ramp".
  **Fusion value:** there is already a **1-D ordered colour channel (`--ramp-1..4`)** meant to encode *sequence /
  depth / position* — a pre-existing **ordinal data-binding channel** a glyphgraph could read for stage/sequence.

### Elevation maps to ROLES, not just sizes (a parallel of the radii role-map)
- `spacing_elevation.html:212-300` — 9 tiers each tied to a role (card/hover/popover/modal/primary-action).
- `spacing_radii.html:15` — 6 radii each tied to a role (chip/button/card/popup/pill).
  **Fusion value:** both spacing sheets already encode **proportion → role** (not raw → raw). The same
  role-keyed resolution a glyphgraph node would want for depth/corner is *already expressed here as prose rules*.

---

## (c) Relevant to a glyphgraph surface

### The `@dsCard` self-projection pattern (the generative-index seam)
Every visual specimen carries a single HTML comment of the shape (Observed, e.g. `colors_status.html:2`):
```
<!-- @dsCard group="Brand" name="Status colors" subtitle="Warm-shifted …" viewport="700x220" -->
```
This is a **self-describing header**: the file *declares its own gallery metadata* (group, name, subtitle,
render viewport) inline, rather than being listed in a separate manifest. **Inferred:** a generator greps
`@dsCard` across `preview/` and builds the gallery index from these declarations — the file IS its own registry
row (the design-system's "register/resolve" idea applied to the specimen sheets). This is **the same
self-projection a glyphgraph node wants**: each node carries its own descriptor (group/name/subtitle + a render
hint), and the surface is assembled by *reading the nodes*, not by a hand-maintained list. The `viewport="WxH"`
field is a **per-node render-size hint** — directly analogous to a glyphgraph node declaring its own footprint
for auto-placement.

### The elevation / depth / proportion treatments (glyphgraph node depth + spacing)
- **9-tier layered-shadow recipe** (`spacing_elevation.html:34-78`) — a ready depth vocabulary for node
  z-ordering / focus (resting → hover-lift → popover → modal → primary-glow). The discipline rules ("step one
  tier on hover", "never glow+modal", "never md-on-md") are **composition constraints** a glyphgraph layout
  engine could enforce as it stacks nodes.
- **8-px grid + 11 steps** (`spacing_scale.html`) and **6 radii role-mapped** (`spacing_radii.html`) — the
  proportion tokens a node renderer would `var()` rather than hardcode.
- **Gold ramp `--ramp-1..4`** (`colors_gold.html:14`) — the ordinal position/sequence channel noted above.

### The colour-status maps (glyphic fill/colour ← state)
- `colors_status.html:18-22` is effectively a **state→{bg,dot,pill,label} map** (success→Approved, warning→Review,
  error→Rejected, info→Info, pending→Pending). This is *exactly* the resolve-fill-from-state step in the
  glyphic pipeline (ANCHOR §3 "fill/colour from state"). The {dot + pill + bg} triple is a small **applied
  vocabulary** a node could adopt for status rendering.
- The gold-circle **desaturation/state-strength gradient** (`brand_icons_gold.html:13`) is a second, *continuous*
  state channel (strength, not category) — pairs with the discrete status map.
- The **per-section hue map** (`components_sidebar.html:38-45`) is a **category→colour map** (a third binding:
  domain/type → hue), complementing state→colour.

### `image-slot.js` — the one live/interactive precedent in this corpus
This is the single behavioural artefact and the most structurally relevant to a *live interactive canvas*:
- **A registered custom element** `<image-slot>` (`customElements.define`, Observed `image-slot.js:640-642`) —
  a self-contained interactive node, the web-component analogue of a reactflow custom node.
- **Persistence via a sidecar + a host bridge**: reads `.image-slots.state.json` via `fetch`, writes via
  **`window.omelette.writeFile`** (Observed `:78,111-114`) — a **browser↔host write boundary** that gates on
  the bridge's presence (`editable = !!(window.omelette && window.omelette.writeFile)`, Observed `:596`). Outside
  the runtime it is **read-only** (Observed `:11-12,595-598`). **Inferred:** `window.omelette` is the same
  host-bridge family the ANCHOR's live layer needs (browser action → server-side effect); this is a working
  precedent for the browser/Company boundary §6 worries about.
- **Loud-fail-adjacent discipline**: serialized writes with a dirty-flag (Observed `:107-117`), tombstones so a
  delete-before-load isn't resurrected (Observed `:69-72,93`), generation counters so a stale async encode bails
  (Observed `:477-482`), merge-on-hydrate so an in-memory change racing the fetch isn't clobbered (Observed
  `:83-96`). These are the **realtime-mutation correctness patterns** a live talk→graph surface will need (nodes
  arriving/mutating during async work — ANCHOR §6 "stable incremental").
- **Sidecar-source distrust**: only accepts `data:image/` URLs from the sidecar because the agent's `write_file`
  could also write it (Observed `:600-605`) — a **don't-trust-the-shared-store** guard relevant to a two-author
  (voice + AI) surface where both write the same state.
- **Self-describing usage block** (`:3-49`) — the component documents its own attributes/shapes/masks inline.
- **It explicitly opts OUT of the design system**: top line `// @ds-adherence-ignore -- omelette starter
  scaffold (raw elements/hex/px by design)` (Observed `:1`), and its shadow-DOM CSS uses **raw hex** (`#c96442`
  the terracotta handle colour, `#fff`, `#b3261e`) and system-ui font (Observed `:164,183,191,200`). **Inferred:**
  `#c96442` is *off-brand* (terracotta, not the gold/bronze palette) — a deliberate scaffold colour, flagged as
  such, not drift. Catalogue it: the live-component precedent currently lives *outside* the token system.

---

## (d) Specimens carrying NO `@dsCard` tag (they fall out of the generative index)

Verified by grep across all 25 files (Observed). **Five** files have no `@dsCard`:

| File | Why it has no tag (Inferred) |
|---|---|
| `_card.css` | Infrastructure — the shared frame the cards link, not itself a card. |
| `image-slot.js` | A behavioural web component, not a render-once specimen; explicitly `@ds-adherence-ignore` (`:1`). |
| `icons_tones.prompt.md` | Empty stub (2 lines) — an un-filled prompt placeholder. |
| `brand_icons_bronze.html` | A specimen sheet **but un-tagged** — it shows a raster `.jpg` of the icon library. |
| `brand_icons_gold.html` | Same — un-tagged raster icon-library sheet. |

**The notable finding:** `brand_icons_bronze.html` and `brand_icons_gold.html` ARE visual specimen cards (same
`_card.css`, same `.lead`/`.sheet`/`.meta` structure as the tagged ones) yet **carry no `@dsCard` header** —
so they **fall out of the generative gallery index** while the other 18 cards are in it. **Inferred:** either an
oversight, or a deliberate exclusion because they embed external raster `.jpg` assets rather than live-rendered
DOM (the other cards render their content from tokens/`CV_ICONS`; these two just `<img>` a flat sheet). Under the
no-staleness law this is a **drift seam**: two real specimens are invisible to the index that's supposed to be
the complete projection. For the glyphgraph lens, it's the concrete demonstration that **"the index is only as
complete as the self-descriptors" — an untagged node is an invisible node.** `_card.css`, `image-slot.js`, and
the empty `icons_tones.prompt.md` are *correctly* outside the index (they aren't cards).

---

## Cross-cutting observations (for the synthesis layer)

- **Two homes for the look, side by side.** `preview/` cards link a **local `_card.css` → `../colors_and_type.css`**
  (Observed `_card.css:2`), while the charter's `mockups/` link the **generated `../design-system.css`**. Both
  ultimately want the same token source; this is a *parallel surfacing of the look* (specimen sheets vs product
  screens) — fusion material, not a conflict to resolve.
- **The self-projection idea is already live here** (`@dsCard` + `image-slot`'s inline usage block + the
  source-counts on `colors_bronze`). The glyphgraph's "each node describes itself, the surface reads the nodes"
  is **continuous with an existing corpus habit**, not a new mechanism.
- **Literal-vs-var is the measurable convergence target.** The bronze sheet (tokenised, source-traced) is the
  shape; the gold/ink/surface/status sheets (raw hex) and the type/spacing sheets (inline px) are the same look
  not-yet-single-sourced. A local-model "recognise-and-propose" pass (charter) would catch exactly these.

---

### 3-line summary
The full `preview/` corpus is **6 specimen families** (brand · colors · type · spacing · components · infra)
where the **same concept is repeatedly treated several ways** — bronze in 4 roles, two parallel icon systems
(bare-stroke vs gold-ringed), icon-colour resolved 3 ways (role-default / per-section / fixed), a recurring
dashed-gold "selected" idiom, and chips authored both as raw-hex and as `var()` (the bronze sheet is the
tokenised, source-traced exemplar the others would converge toward) — all kept and catalogued, not collapsed.
For a glyphgraph surface the live seams are the **`@dsCard` self-projection header** (file = its own registry
row, with a `viewport` render-hint), the **role-keyed elevation/radii/ramp** proportion channels, the
**status/strength/section colour maps** (the resolve-fill-from-state material), and **`image-slot.js`** — the
one interactive custom-element + `window.omelette` host-bridge precedent, carrying realtime-mutation correctness
patterns (serialized writes, tombstones, generation counters, hydrate-merge, sidecar-distrust). **Five files
carry no `@dsCard` tag**; of those, `brand_icons_bronze.html` + `brand_icons_gold.html` are real specimens that
**wrongly fall out of the generative index** — the in-corpus proof that an untagged node is an invisible node.

**Path:** `/home/tim/company/design/claude-ds/analysis/glyphic-language/live-instrument/findings/AREA-22-preview-corpus-full.md`
