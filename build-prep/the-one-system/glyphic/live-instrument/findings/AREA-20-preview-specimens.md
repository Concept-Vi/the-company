# AREA-20 · The Preview Specimen Corpus (`preview/*.html`)

**Wave-3 coverage+unification companion.** Territory: `/home/tim/company/design/claude-ds/preview/*.html` —
the **@dsCard specimen corpus**, the design system's gallery of components / treatments / patterns.
**Lens (Tim):** nothing here is final or canonical; "already built" is stripped. **Duplications are
expected and valuable** — many specimens are *alternative treatments of the same thing*; the job is to
catalogue their **unique qualities** + the **fusion direction**, because that is the raw material a
conversational-glyphgraph surface gets composed from.

**Coverage (honest):** 34 files total. Read **in full (12):** `brand_shapes`, `brand_process_flow`,
`ai_bridge`, `ai_registry`, `components_box_variants`, `components_cards`, `brand_vi`,
`components_badges`, `icons_circle_badges`, `icons_tones`, `components_section_panel`, `icons_overview`.
**Characterised via @dsCard tag + family pattern (22):** the colors_*, spacing_*, type_*, brand_*
(wordmark/voice/mark/emoji_nav/shapes-already-read), components_* (buttons/inputs/sidebar), brand_icons_*.
The corpus is small + radically consistent (one shared `_card.css` frame, one token set) so the unread
files characterise reliably from their tags — I did **not** read every line of all 34 (per brief: sample
broadly + characterise).

---

## A · What specimen families exist + which are relevant to a glyphgraph surface

The `group="…"` facet of `@dsCard` is the family axis. **Observed** (grep of all 32 tagged files,
`preview/*.html:2`):

| `group` | members | relevance to a conversational glyphgraph |
|---|---|---|
| **Brand** (24) | mark, vi, wordmark, voice, emoji_nav, shapes, process_flow, type_*, colors_* (gold/status/ink/surface), spacing_* (radii/scale/elevation), components_* (badges/cards/inputs/buttons/sidebar/section_panel), icons_* (overview/tones/circle_badges) | the **token + marker vocabulary** the canvas draws with |
| **AI** (2) | `ai_registry` (CV_AI), `ai_bridge` (CV_HOST) | **node-graph layout treatments** + the registry-projection pattern |
| **Colors** (1) | `colors_bronze` | structural bronze→tan scale |
| **Components** (1) | `components_box_variants` | the **node-vessel** treatment (the box as a node) |
| **Glyphic System** (1) | `system/system-atlas.html` (lives in `system/`, not `preview/`, but tagged) | the directory map; tells us @dsCard is the discoverability spine |

**The directly-relevant cluster for a graph/diagram/marker/chat/panel surface** (Observed, by content):

- **`brand_shapes.html`** — *the glyph-as-typed-vessel engine.* (Observed `brand_shapes.html:29,42-54`) Shapes
  carry **typed meaning** — "a vessel is not decoration, it tells you what kind of thing sits inside";
  regular polygons 3–8 sides + circle (= ∞). An **icon from the icon system sits inside each shape**; edge
  colour / fill sheen / shadow / thickness / ink all **resolve from tokens** through one default. The grid
  renders **`CV_SHAPES.shapeTypes.map(... markSVG(t.shape))`** — i.e. the specimen *is a live read-out of the
  shape registry*. **This is the glyphic node, already a typed-vessel-with-symbol-inside built from a
  registry.** The cascade is explicitly stated: `markDefaults` (tokens) ◀ shape-type ◀ `markSVG(opts)` — a
  single call retints/restrokes/reshapes any vessel without leaving the system. *(Inferred:* this is the most
  literal precedent in the corpus for the ANCHOR §3 RESOLVE step "form from type, fill/colour from state,
  symbol via icon-lookup".*)*

- **`brand_process_flow.html`** — *a hand-built node+edge diagram treatment.* (Observed `:28-50,83-102`)
  A **vertical ladder of stage cards** (flat white, 2.5px gold border, gold-brown title) joined by **gold
  connectors** = endpoint **dot** · line `seg` · **▼ arrowhead**; the between-node gap is a **pill on the
  connector** (carrying an *action* like "Revision" or a *duration* like "1–2 Weeks"); a **⊕ join** node
  appends a deliverable; dashed-leader edges tap each stage out to an escalating-fidelity image frame. **This
  is a complete visual grammar for nodes, typed edges, edge-labels, and a join operator** — exactly the
  reactflow custom-node + edge styling the ANCHOR §3 needs, rendered here as static HTML/CSS.

- **`ai_bridge.html` + `ai_registry.html`** — *graph/relational read-out treatments + the
  registry-projection discipline.* (Observed `ai_bridge.html:26,42-61`; `ai_registry.html:30,45-64`) Both
  render their content **live from a registry call**: `ai_bridge` is literally "a live projection of
  `CV_HOST.describe()`" (runtimes as status-dot rows, capability chips on/off); `ai_registry` walks
  `CV_AI.LAYERS` → `AI.query({layer})` → layer rows with count badges + chips. Relevant treatments:
  **status-dot node-rows**, **on/off capability chips**, **layered-row grouping with a coloured swatch +
  count**. The deep relevance is the *pattern* (see §C) not the layout.

- **`components_box_variants.html` + `components_cards.html`** — *the node-body / card treatments* (see §B,
  these are a parallel pair).

- **`brand_vi.html`** — *the canonical entity mark.* (Observed `:20,31`) Always a **diamond + line-fill + the
  V glyph**, rendered by the **same** `CV_SHAPES.markSVG('vi')` as the shape system — proof the marker engine
  is single-sourced (the mark is not a separate asset, it's a shape-type). A glyphgraph node for "Vi/the AI"
  reuses this exact vessel.

- **`icons_circle_badges.html`** — *the diagram-level entity marker, with state.* (Observed `:16,25-39`)
  Self-described as **"wrap any icon in a thin gold ring for diagram-level use"** — three variants:
  **outline** (default), **filled** (active entities), and a **state-strength gradient**
  `desaturated={0…0.85}` for **inactive states**. *(This is the single clearest "fill/colour from state"
  precedent — a marker whose appearance encodes liveness, the ANCHOR's "the buyer's gone cold" mutation.)*

- **`components_badges.html`** — *status encoded as colour.* (Observed `:40-67`) Filled **status dots**
  (6 colours), **task chips** that "inherit the dot colour at a soft-fill background", **pills/dropdowns**,
  a **notification badge**. The chip = a small labelled node tinted by its state.

- **`components_section_panel.html`** — *the panel / chrome the canvas sits in, AND the depth-zoning law.*
  (Observed `:28`) The flat product-chrome is a soft-gold panel; but the note is load-bearing: **"On
  deck/generative surfaces, grouping is instead the depth-keyed zone wash — the near-white ladder
  (`--zone-*`) where the tint marks containment depth."** *(Inferred:* a glyphgraph canvas is a
  "generative surface", so grouping/containment of sub-graphs should use `--zone-*` depth wash, not the
  flat product panel — a direct design instruction for the live surface.*)*

- **`icons_overview.html`** — *the symbol inventory the RESOLVE step looks up against.* (Observed `:23-32`)
  "**99 individual icons**, single source of truth", `CV_ICONS.data[name]`, categories People/Files/Comms/
  Architecture/Browser/Actions/System/**Logic** (incl. `network`, `decision-tree`, `hierarchy`). This is the
  pool the ANCHOR §3 "symbol via semantic icon-lookup" searches; the `_ingest/ICON-AUDIT.md` under-population
  flag (ANCHOR §7) is the "generate-on-miss" trigger.

**Lower-relevance (token/foundation families, characterised from tags):** `colors_*` (palettes the marker
fills draw from), `spacing_*` (radii/scale/elevation — node sizing + the 9-tier shadow that gives nodes
depth), `type_*` (the label type ramp for node titles/edge labels), `brand_voice`/`brand_wordmark`/
`brand_mark`/`brand_emoji_nav` (brand identity, not graph-structural), `components_buttons`/`_inputs`/
`_sidebar` (control chrome around the canvas). All real, all single-token-sourced, none is the graph itself.

---

## B · Duplicate / parallel treatments of the same concept (the fusion raw material)

This is the heart of the brief. The corpus has several **parallel takes on the same primitive** — each with
a unique quality. These are the alternatives a glyphgraph surface fuses from.

### B1 · THE CARD / BOX / NODE-BODY — **three parallel treatments**
The single most-duplicated concept. All three are "a rounded rectangle holding content," diverging by intent:

| specimen | unique quality | what it contributes to a glyphgraph node |
|---|---|---|
| `components_box_variants` (Observed `:17-30,52-101`) | **gold edge + paper-sheen gradient + shadow**, parameterised purely by tokens (`--r-md/-lg/-pill`, `--paper` vs `--accent-gold-50` emphasis fill), **fillable** (drag image / editable text), an `emphasis` variant for "the one thing that should lead" | the **default node vessel** — editable, emphasis-able, the lead-node treatment |
| `components_cards` (Observed `:7-43,46-61`) | **sunken/flat surface** (`--bg-surface`, `--shadow-card`), three sub-patterns: content card · **video tile** (play affordance) · **dashed dropzone empty-state** | the **media node** + crucially the **dashed empty-state** = the node that *hasn't resolved yet* (the ANCHOR's generate-on-miss placeholder while the foundry draws) |
| `brand_process_flow` stage card (Observed `:15-26`) | **flat white, 2.5px gold border, no shadow, centered gold-brown title**, built explicitly to sit in a connected ladder | the **graph-member node** — already styled for life inside a diagram with connectors |

**Fusion direction:** one node Type with axis-dials — `surface` (sheen-box ↔ flat-card ↔ diagram-stage),
`state` (resolved ↔ dashed-unresolved-placeholder ↔ emphasis-lead), `fill` (paper ↔ gold-wash ↔ media).
The box-variants note already cross-references the others ("Entity *marks* live in **Entity shape system**;
the staged ladder in **Staged-process flow** — this card is just the box") — **the corpus is already telling
us these are facets of one thing.** A glyphgraph node = `brand_shapes` vessel (typed outline + symbol) ⊕ one
of these card-bodies as its fill region.

### B2 · THE ENTITY MARKER — **two parallel treatments**
| specimen | unique quality |
|---|---|
| `brand_shapes` / `brand_vi` (Observed `brand_shapes:42-54`) | **typed polygon vessel** (shape = meaning, 3–8 sides + circle), icon inside, all treatment from `markDefaults` tokens; `markSVG()` is the one renderer |
| `icons_circle_badges` (Observed `:25-39`) | **icon-in-a-ring** (always a circle), with **filled = active** + **desaturated = inactive** state-strength; self-described "for diagram-level use" |

**Fusion direction:** these are the **same marker at two points on the `form`/`state` axes** — the circle
badge is the `circle` shape-type of `brand_shapes` (ANCHOR: form-from-type) *plus* a state encoding
(desaturation) the polygon specimen lacks. **Fuse: lift `icon_circle_badges`'s `desaturated`/`filled` state
treatment INTO `CV_SHAPES.markDefaults` as a `state` facet**, so *every* typed vessel (not just the circle)
can read "cold / active / inactive" — exactly the ANCHOR's "fill/colour from state" RESOLVE rule and the
voice-mutation "no, the buyer's gone cold." (`brand_shapes` says treatment is already a token parameter; this
is registering one more facet, not new code.)

### B3 · STATE-AS-COLOUR — **two parallel treatments**
| specimen | unique quality |
|---|---|
| `components_badges` task-chips (Observed `:48-53`) | **discrete status palette** (6 named status colours) bound to a soft-fill chip |
| `icons_tones` (Observed `:27-35`) | **continuous tone scale** `tone="bronze\|gold\|ink\|muted\|cream"` passed to the icon renderer; "muted" tone = a de-emphasised state |

**Fusion direction:** discrete status colour (badges) and a tone ramp (icons) are two encodings of the same
"state→appearance" map — which is *exactly* what `CV_MEANING.encodings` already is (ANCHOR §7: the
data-field→visual-channel grammar with value→appearance maps). **Fuse: route both into `CV_MEANING.encodings`
as the single state→{fill,tone,desaturation} channel** so a node's liveness is one resolved binding, not
three hand-set colours.

### B4 · NODE+EDGE DIAGRAM — **two parallel treatments** (this one spans repos)
| treatment | unique quality |
|---|---|
| `brand_process_flow` (Observed `:83-102`) | **static HTML/CSS** ladder: dot+line+▼ connectors, **edge-label pills** (action vs duration), **⊕ join** node, dashed-leader edges — a rich *visual* edge grammar, zero interactivity |
| `core/DiagramSolver.jsx` (ANCHOR §7, External-to-this-area) | the **live SVG graph solver** (`CVGraph = {nodes,edges}`), programmatic layout |

**Fusion direction (My-idea, grounded):** `brand_process_flow` is the **style spec** for what
`DiagramSolver` (and the ANCHOR's proposed reactflow custom-node) should *look like* — typed edges, labelled
connectors, a join operator. The reactflow surface in the ANCHOR §4 should not invent edge styling; it should
**render `DiagramSolver`/reactflow edges using the process-flow connector vocabulary** (dot · line · ▼ ·
pill-label · ⊕). The static specimen is the design contract the live canvas resolves against.

---

## C · The @dsCard self-documentation pattern (how a specimen becomes discoverable)

**This is the pattern the glyphgraph surface should copy to self-describe** — and the corpus already does it
*twice over*, with a deeper twist (the specimen reads itself out of its own source).

### C1 · The tag itself
Every specimen carries one HTML comment on line 2, **before `<html>`** (Observed, all 32):
```
<!-- @dsCard group="Brand" name="Shape system" subtitle="Typed geometric vessels…" viewport="900x620" -->
```
Four facets: **group** (family), **name** (title), **subtitle** (one-line self-description), **viewport**
(intended render size). The tag is the specimen *saying what it is* — the same move as Glyphic's
"marks say themselves" read-out (MEMORY: glyphic meaning-registry "a gateway holding the home, at rest").

### C2 · It is harvested by TWO independent consumers (Observed)
1. **`atomicity/scan-engine.js:181`** — a registered extractor:
   ```js
   registerExtractor({ id: 'dscard', description: '@dsCard specimen tags.',
     re: /@dsCard[^\n]*?name="([^"]+)"/g, key: m => m[1] });
   ```
   The scan-engine runs all extractors over the whole project, builds **live indexes**, keeps them fresh
   "on load, on an interval, and when the tab regains focus. No manual rebuild" (Observed `scan-engine.js:6-9`).
   So @dsCard is a **generative discovery pass**, not a hand-maintained gallery list — fully in keeping with
   the GOVERNING LAW (ANCHOR §5: no handwritten backfill; re-runs as things are added).
2. **System Atlas** (`system/build-system-map.js:59`): *any* `preview/*.html` is classed role **`card`** =
   "A design-system preview/specimen surface" (Observed `system-atlas.html:122`). Discoverability is by
   **location convention** (`preview/`) reinforced by the tag.

### C3 · The DEEP pattern — **a specimen is a live projection of its own registry** (the spine for §C)
Not a static picture: the relevant specimens **render themselves by querying the source of truth.** Observed:
- `ai_bridge.html:42` — "a **live projection of `CV_HOST.describe()`**"; runtimes/caps drawn from the call.
- `ai_registry.html:46` — walks `AI.LAYERS` → `AI.query({layer})`; chips, counts, swatches all from `CV_AI`.
- `brand_shapes.html:45` — grid = `CV_SHAPES.shapeTypes.map(... markSVG())` (the shape registry, read out).
- `icons_overview.html:29` / `icons_tones.html:33` / `icons_circle_badges.html:30` — all read
  `CV_ICONS.data[name]`.

**This is the answer to the brief's point (c):** the glyphgraph surface "should self-describe the same way"
→ it should be **a live projection of the glyphgraph registries** (`CV_GLYPHIC`, `CV_MEANING`, `CV_ICONS`),
carry a `@dsCard`/equivalent tag so the scan-engine indexes it, AND **narrate itself out of its source** —
which *rhymes exactly* with the ANCHOR §3 "the graph narrates itself back" and Glyphic's existing
read-out ("marks say themselves"). The specimen's self-documentation and the glyphgraph's self-narration are
**the same primitive at two altitudes**: a structure that produces its own description from its data, never a
copied caption. **Fusion: the live glyphgraph canvas should ITSELF be registrable as a @dsCard specimen** —
its read-out becomes the subtitle, the scan-engine picks it up, and it appears in the System Atlas as a
`card`. The instrument documents itself by existing.

### C4 · A real discoverability GAP (Observed, the stress-test the lens demands)
`brand_icons_bronze.html` + `brand_icons_gold.html` have **no `@dsCard` tag** (32 tagged of 34 files —
confirmed: `grep -c @dsCard` returns tags on all but these two). So the scan-engine's `dscard` extractor
**misses them** — they're discoverable only via the location-convention fallback (C2.2), with no
group/name/subtitle/viewport. *(Inferred:* this is exactly the staleness the GOVERNING LAW warns about — a
specimen that doesn't self-describe falls out of the generative index. For a glyphgraph surface this is the
failure mode to design against: a node/graph that doesn't emit its own read-out becomes invisible to the
index.*)* **Resolve-into-scope (per Tim's standing rule):** these two should get @dsCard tags; flagged here.

---

## Cross-cutting note for the synthesis (the no-staleness law, §5)
The whole corpus is **already resolution-native** in the way the live layer must be: not one specimen hardcodes
a hex/px in a consumer — they `var(--token)`, and the structural ones (`shapes`, `vi`, `ai_*`, `icons_*`)
**read their content from a registry call**, never a literal list. The marker, the node-body, the state-colour,
the edge grammar all already exist as *parameterised, single-sourced* treatments. **The fusion work is not to
build these — it's to (a) register the missing facets (`state` on `markDefaults`; B2/B3) so one vessel spans
all the parallel treatments, and (b) make the live glyphgraph canvas a self-projecting @dsCard the same way
these specimens are.** That holds the GOVERNING LAW: extend the registries, don't fork a parallel surface.

---

### 3-line summary
The preview corpus is 34 single-token-sourced `@dsCard` specimens; the graph-relevant cluster already
contains every primitive a conversational glyphgraph needs — the typed-vessel-with-symbol marker
(`brand_shapes`/`brand_vi`, rendered from `CV_SHAPES`), a full node+edge+label+join visual grammar
(`brand_process_flow`), state-encoded markers (`icons_circle_badges` desaturated/filled), and state-colour
maps (`components_badges`/`icons_tones`) — all as *parameterised, registry-read* treatments, not hardcoded.
The valuable duplications are three parallel **node-bodies** (box/card/stage → one Type with surface+state
dials, the dashed empty-state = generate-on-miss placeholder), two parallel **markers** + two **state-colour**
encodings (fuse the state facet into `CV_SHAPES.markDefaults` + route both into `CV_MEANING.encodings`), and
two **diagram** takes (the static process-flow is the *style contract* for the live reactflow/DiagramSolver edges).
The discoverability pattern is the deep find: a specimen is a **live projection that narrates itself out of its
own registry** (`CV_HOST.describe()`, `CV_AI.query()`, `CV_SHAPES.shapeTypes`), harvested by a generative
scan-engine extractor (`scan-engine.js:181`) — so the glyphgraph surface should self-describe identically (be
its own @dsCard, narrate from `CV_GLYPHIC`/`CV_MEANING`), the same primitive as the ANCHOR's "graph narrates
itself back"; gap flagged: `brand_icons_bronze/gold` carry no tag (32/34) and fall out of the index.

**Path:** `/home/tim/company/design/claude-ds/analysis/glyphic-language/live-instrument/findings/AREA-20-preview-specimens.md`
