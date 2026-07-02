# AREA A — the writer vs the product bar (the instrument surfaces vs claude-ds)

> Assessment agent A, wide-assessment wave. Read in full first: ANCHOR.md, REGROUNDING.md,
> THE-GENERATIVE-LANGUAGE.md (as instructed). This does NOT re-derive §2 of the doctrine — it
> verifies/extends it against live source, stress-testing where the doctrine (and the writer's own
> self-assessment in `the-whole-thing.html` §7) may be optimistic or wrong. Every claim marked
> **Observed (file:line)** / **Inferred** / **Your-idea**.

---

## 0 · Headline verdict

**The writer is not a demo that needs polish. It is a bespoke, disconnected DOM page that
happens to call real engines underneath.** It is technically impressive (composes DiagramSolver,
CV_MEANING, and five live Company roles correctly) and simultaneously **zero-percent a citizen of
claude-ds** — it does not import a single component, does not touch `CV_REGISTRY`, is not reachable
from the Studio, is not styled from `app/app.css`, and duplicates chrome that already exists,
built better, four different ways elsewhere in the same repo. **Observed.**

The doctrine's own self-scoring in `system/the-whole-thing.html` (zone 7, lines 274-308) — "wearing
the DNA: 30%", "provision: 20%", "frame-resolved: 15%" — is **directionally right but still too
generous** on citizenship. On the specific axis "wearing the DNA" I would score it closer to
**10%**, not 30%: the 30% figure appears to credit the *engine* underneath (DiagramSolver,
CV_MEANING) as if using the real solver were the same thing as being *composed from the component
library*. It is not — see §2. **Your-idea**, stress-testing the doctrine's own number.

---

## 1 · The writer + its four siblings — what each actually is

| File | Lines | What it is | Loads component lib? | Loads app.css / Studio chrome? | Reachable from Studio nav? |
|---|---|---|---|---|---|
| `system/glyphgraph-generator.html` | 656 | The writer — talk/type → glyphgraph, co-edit, teach | No | No (own `<style>`, styles.css only) | No |
| `system/glyphic-foundry.html` | 247 | Conversational mark-foundry (older, narrower than Icons.jsx's built-in one — see §3) | No | No | No |
| `system/language.html` | 199 | The language spec-demo (marks say themselves) | No | No | No |
| `system/glyphic-system.html` | 660+ (truncated at 470 read) | The living-spec document (facets, slots/sockets, the plan) | No | No | No |
| `system/the-whole-thing.html` | 451 | The doctrine's own visual essay, with live-rendered glyphgraphs | No | No | No |

**Observed (file:line):** none of the five `<script src>` lists (glyphgraph-generator.html:138-164,
glyphic-foundry.html:9-27, language.html:71-79, glyphic-system.html:11-26,
the-whole-thing.html:318-336) references `components/*.jsx`, `app/app.css`, `app/components/*`, or
`CV_REGISTRY`. All five are **self-contained HTML documents** styled with hand-written `<style>`
blocks, loading the *engine* layer (axes, cv-icons, cv-glyphics, cv-meaning, ai-registry) directly
via `<script src>`, React+Babel from a CDN, with zero build step. This is the `_demo/` harness
pattern (per REGROUNDING §9a, `_demo/glyphic-board.html` is named as a sibling harness) applied to
what is meant to be **the flagship product instrument**.

**This is the single biggest citizenship violation, and it is structural, not cosmetic:** these
pages are not routed through `app/index.html`'s Studio shell at all. They are static files under
`system/` that only a human clicking a gallery thumbnail, or an agent fetching the URL directly,
will ever see. Compare to `app/canvases/Icons.jsx:1` — a real canvas registered as `window.Icons`
that the Studio's router mounts inside its shell, with `CanvasHeader`, the Studio's toast
(`window.dsaToast`), and the Studio's own generation-panel pattern (§3).

---

## 2 · What product-level requires — component/block/token/specimen patterns to reuse

### 2a · The chrome vocabulary already exists, in `app/app.css` — the writer reinvents it badly

**Observed:** `app/components/CanvasHeader.jsx:1-13` — every real canvas (`Icons.jsx:180`,
`Overview.jsx:73`, and 16 others) opens with `<CanvasHeader title=… sub=… actions=…/>`, which
renders `.dsa-canvas-header` / `.dsa-canvas-title` / `.dsa-canvas-sub` / `.dsa-canvas-actions` —
classes defined once in `app/app.css` and shared everywhere. The writer instead hand-rolls its own
`<h1>`/`.lede` pair (glyphgraph-generator.html:79-80) with **bespoke inline CSS** (lines 9-10) that
does not use any `--dsa-*` custom property and will silently drift from the Studio's real header
the next time `app/app.css` changes.

**Observed:** `app/canvases/Icons.jsx:192-229` — the Studio's **real generation-panel pattern**:
a collapsible `.dsa-gen-panel` with a header row (`ViShape` icon + title + close), a `<textarea>`
hint, an actions row with a hint string + primary button, a `.dsa-gen-loading` state with an
animated `ViShape`, and a `.dsa-gen-results` grid of clickable proposal tiles that show "✓ in
system" once adopted. This is a **complete, product-grade, reusable "propose → adopt" UX** —
exactly the shape the writer's own `#suggest` strip (glyphgraph-generator.html:96, 476-507) and
`makeIcon()` candidate strip (lines 581-619) are informally reinventing with raw `<span class="eg">`
chips and no loading state, no dedicated panel chrome, no consistent adopted-state affordance.
**The writer should literally reuse `Icons.jsx`'s `.dsa-gen-panel` markup/CSS**, not its own
`.egrow`/`.eg` chip system (glyphgraph-generator.html:19-25).

**Observed:** `app/components/RefinePop.jsx:1-78` — the Studio's **one shared per-item refine
affordance**: a hover-revealed dot/pill trigger → popover textarea → Enter-to-submit → busy state.
Used identically in `Icons.jsx:289-293` (refining a symbol) and `Voice.jsx`, `workshop/Section.jsx`
(per RefinePop.jsx's own header comment, line 3: "Identical visual language to the dots in Build").
The writer's "Refine form" `<details>` (glyphgraph-generator.html:334-340) and the foundry's
feedback `<input>` (glyphic-foundry.html:613-618, inline in `the-whole-thing... ` — actually
glyphgraph-generator.html:612-618) each **reinvent a narrower, inconsistent version of exactly
this component** — no popover, no hover-reveal, no shared visual grammar with the rest of the
Studio. **This is a token-swap-cheap fix**: literally `import RefinePop` (well — `window.RefinePop`,
since these are non-module scripts) and call it with an `onRefine` callback wired to
`resolveWord`/`makeIcon`.

**Observed:** `core/containers.css:1-198` — the real **Band → Section → Zone → Cluster → Atom**
containment ladder, with zone washes **computed from nesting depth** (`--zone-depth`,
containers.css:76-93), not hand-picked colors. The writer's `.panel` / `.compose` / `.stage`
(glyphgraph-generator.html:13, 31, 33) are all **flat, hand-set `border-radius`/`box-shadow`
boxes with literal hex fallbacks** (`var(--bg-surface,#fff)`, `var(--border-default,#E8DFC5)`,
etc. — every single CSS var in the file carries a hardcoded fallback, e.g. lines 9-77 throughout).
This is the exact anti-pattern claude-ds/CLAUDE.md §3 forbids ("No raw hex/px in consumers") —
present in essentially every rule of the writer's stylesheet. It is not merely "not composed from
containers.css" — it is a **direct violation of the token-purity law**, made systematically, 60+
times in one file.

### 2b · The preview/ specimens are NOT the quality bar the writer should chase — the Studio canvases are

Sampled 6 preview specimens (`components_cards.html`, `components_section_panel.html`,
`icons_overview.html`, plus `_card.css`, `brand_*`, `type_*` by directory scan). **Observed:**
these are **simple, single-viewport, static demonstration cards** — each wrapped in
`preview/_card.css`'s `.card` frame, no interactivity beyond hover, no AI, no state. They exist to
document a token/pattern for the gallery grid, at `viewport="700x280"`-class sizes
(components_cards.html:2). They are a **lower bar than the writer needs**, not a higher one — the
`@dsCard` convention itself (the HTML comment on line 2 of every file, including the writer's own
line 2) is shared between "static token demo" and "full instrument," which is itself a category
error: the gallery currently cannot distinguish "a swatch" from "a working product surface."
**Your-idea:** the gallery's `@dsCard` schema needs a `kind` field (`specimen` | `instrument` |
`canvas`) so quality expectations differ by kind — a specimen is fairly judged as a static card; an
instrument must not be.

The **real quality reference for an instrument-class surface is `app/canvases/*.jsx`** — sampled
`Icons.jsx` (338 lines: categorized sections, search, tone-picker, hover-reveal per-tile actions,
AI-generation panel, adopt/refine/duplicate/delete lifecycle, toast feedback) and `Overview.jsx`
(164 lines: `FaceMarker` — a four-presentation, tweak-driven, registry-sourced "open the real page"
affordance built from `CV_GLYPHIC.composeRelation`, `TweaksPanel`/`TweakRadio` for live
in-product configuration). **These are the actual "gallery-grade" bar**, and the writer falls far
short of both in structure (no categorized sections, no tone system, no tweak panel) despite being
functionally richer in one dimension (real NL parsing + Company roles).

### 2c · What "integrating INTO the Studio/gallery" means mechanically

**Your-idea**, reasoned from the evidence above: it means **both**, not either/or —
1. **A `@dsCard` specimen entry stays** (for the static gallery grid / screenshot review — cheap,
   already works via the HTML comment convention).
2. **A real `app/canvases/GlyphgraphWriter.jsx` canvas is ALSO built**, registered the same way
   `Icons`/`Overview` are (`window.GlyphgraphWriter = GlyphgraphWriter;` — Icons.jsx:338 pattern),
   mounted into the Studio's router, appearing in `Overview.jsx`'s `canvases` array (line 62-69)
   so it has a tile, a `FaceMarker`, and a place in the "System at a glance" stat grid. This is the
   *only* path that resolves the ANCHOR's "the mode/loadout entry + RHM/operator surface... the
   generator is an orphan page" gap (REGROUNDING §6.5) — a gallery card alone can never be "a mode
   the system enters."
3. The five siblings (foundry, language, glyphic-system, the-whole-thing) stay as **documentation/
   spec artifacts** (they are explicitly self-described as such: glyphic-system.html:2's subtitle
   says "a living spec"; the-whole-thing.html:2 says "written by the language seat"). Only the
   **foundry** (glyphic-foundry.html) has a legitimate claim to also become a canvas — but see §3,
   it is redundant with functionality `Icons.jsx` already has, better.

### 2d · Effort-shape per fix (honest, not optimistic)

| Fix | Shape | Why |
|---|---|---|
| Swap hardcoded chrome (`.lede`, `<h1>`, buttons) for `CanvasHeader` + `app/app.css` classes | **Token/component swap** — cheap | Components already exist; it's substitution, not design work |
| Swap `.eg`/`.egrow` suggestion chips for `Icons.jsx`'s `.dsa-gen-panel` pattern | **Small recomposition** | Different DOM shape (panel vs inline chips) but same data (candidates, pick handler) |
| Swap refine `<details>`/feedback `<input>` for `RefinePop` | **Token swap** — cheap | Drop-in component, already generic (`onRefine` callback) |
| Replace hand-rolled `.panel`/`.compose`/`.stage` with `core/containers.css` Band/Zone/Cluster | **Recomposition** — medium | Requires re-deriving the layout as a containment tree (see §5, the placement problem is coupled to this) |
| Register as an `app/canvases/*.jsx` Studio canvas | **New build, but small** — the logic already exists in vanilla JS; it is a port, not new design | The 656-line vanilla-JS body (lines 165-655) would become the canvas's `useEffect`/handlers; the DOM the JSX renders is what needs the containers.css treatment above |
| Wire into `CV_REGISTRY` as a typed component (glyphic-type.js already models parts/slots/sockets!) | **Medium-to-large** | `glyphic-type.js` (registry/glyphic-type.js:1-60+) is real and rich but the writer never calls `CV_REGISTRY.resolve`/`accepts`/`candidatesForSocket` anywhere — it hand-builds tray/chip lists instead of asking the registry what a glyphic's sockets accept. This is the deepest gap: the registry that should govern the writer's editing UI exists and is unused by it. |
| Fields-on-canvas (warmth/ordinal gradients) | **New build** | Nothing today computes or renders this; the laws exist (THE-GENERATIVE-LANGUAGE §1.11, §3.5) but no code path does |
| Real spatial placement (replace the `place()` ring) | **New build, large** — see §5 | Coupled to the unbuilt spatial theorem (REGROUNDING §6.2) |

---

## 3 · Redundancy the doctrine hasn't flagged: TWO AI icon-generation UIs exist

**Observed:** `app/canvases/Icons.jsx:44-92` has a complete, working "Generate with Vi" flow
(prompt → `CV_AI.complete` → JSON-parsed 4 proposals → click-to-adopt into `CV_ICONS.data`) baked
directly into the **real, routed, product-grade** Icons canvas. **Separately**,
`system/glyphic-foundry.html:1-247` is an **entire standalone page** doing almost the same thing —
conversational mark-foundry, thread-based, demo-fallback, routed through `CV_AI.execute` — but as
an orphan `system/*.html` file with its own bespoke rail+stage layout, never linked to the Icons
canvas, never sharing state with it.

This is exactly the **"nothing-canonical → FUSE every version"** law (REGROUNDING §4) the doctrine
states but has not yet applied to itself. **Your-idea, load-bearing:** before building anything new
for the writer's icon-generation UX (§2a's makeIcon), the assessment should flag that **there are
now three parallel generate-an-icon surfaces**: `Icons.jsx`'s built-in generator, the standalone
`glyphic-foundry.html`, and the writer's own inline `makeIcon()` (glyphgraph-generator.html:581-619,
which calls the newer `glyph_symbol_candidates` **role** — the most advanced of the three, since it
gets structured server-side generation, not client-side JSON-parsing). None of the three know about
the other two. **A single foundry capability, callable from all three surfaces, is missing** — this
is a citizenship violation (one-way surfaces, §1.18 of the doctrine) at the *capability* level, not
just the UI level.

---

## 4 · The A0–A6 AI plumbing files — real, but capability-siloed

Read `app/ai/ai-registry.js` (390 lines, not fully re-read here — prior sessions verified this per
REGROUNDING §5), `ai-glyphic.js` (104 lines, read in full), `ai-glyphic-language.js` (156 lines,
read in full), `app/services/company.js` (124 lines, read in full).

**Observed, positive:** the plumbing is genuinely well-built and IS citizenship-respecting in its
own layer:
- `ai-glyphic-language.js:1-17` explicitly implements **two-way by construction**: "a DUAL surface
  by construction: both `CV_AI.execute('glyphic.author', …)` (the AI move) and a UI panel call the
  SAME entry." This is the doctrine's law 18 ("everything flows both ways") correctly applied — at
  the capability layer.
- `ai-glyphic-language.js:90-136` (`glyphic.assist`) is a genuinely strong implementation of
  atomic, loud-fail, registry-validated collaborative editing — every op type is checked against
  live vocab (`states`, `edgeKinds`) before any mutation, and the whole batch is refused atomically
  on one bad op (lines 126-134). This is a real citizen of the one-IR law.
- `app/services/company.js:1-27`'s header comment is a model of honest, evidenced engineering
  writing (READ-4/5/6 citations, explicit trap documentation) — this file is trustworthy.

**Observed, gap:** the capability layer is real but **only reachable from the writer's own
hand-wired call sites**, not from `CV_REGISTRY`'s socket system. `glyphic.assist`
(ai-glyphic-language.js:90) reads `window.CV_GLYPHGRAPH_SESSION` (a **global set by the writer
page itself**, glyphgraph-generator.html:202-205) — meaning **the assist capability only works if
the writer's own script has run and populated that global**. Any other future surface (a canvas,
a second writer instance, a mobile session) that wants collaborative assist has to replicate the
writer's exact session-global contract. **This is a hidden coupling, not a registry contract** —
the "shared selection substrate" comment at glyphgraph-generator.html:202 ("a future AI capability
reads window.CV_GLYPHGRAPH_SESSION.selection + .graph") is honest about this being informal, but
it means the session substrate is NOT yet addressed/typed per the CITIZENSHIP lens — it's a
window-global, not a registry entry.

**Inferred, not verified by execution:** `resolveWord`/`resolvePhrase`/`composeViaCompany`
(glyphgraph-generator.html:413-472) correctly implement the "never trust #1, thin-margin, ask via
judge" pattern the ground-truth doctrine claims (REGROUNDING §3.1 "thin embedding margins"). I have
not run this against a live bridge to confirm behavior; I take the code's internal consistency
(fallback chains, honest error surfacing at every `catch`) as **structural evidence it was built to
the stated law**, but I have not verified it executes correctly end-to-end.

---

## 5 · Every place the writer violates citizenship (file:line)

Consolidated, cross-referenced to the CITIZENSHIP lens (addressed · typed · derived · wearing-DNA
· two-way · frame-resolved):

1. **Not addressed** — the writer's nodes carry no `glyph://` or any coordinate address; `n1`,
   `n2`… are page-local sequence ids (glyphgraph-generator.html:198, `seq`), never resolved against
   the address grammar the doctrine names (§2 fusion map row "address.json ⇄ the spatial theorem").
   Save/reload has no persistence path at all — the whole graph lives in a JS closure and is lost
   on refresh (no `localStorage`/ledger write for the graph itself; only glosses persist,
   lines 188-196).
2. **Not typed via the registry** — `graph.nodes.push({...})` (lines 258, 632) constructs plain
   objects; `CV_REGISTRY.resolve('glyphic')`/`accepts()`/`candidatesForSocket()` (which
   `glyphic-type.js` provides) are never called. The tray (`paintTray`, lines 287-297) and the
   meaning panel (`paintMeaning`, lines 300-354) hand-enumerate value lists
   (`Object.keys(M.valuesFor('color'))`, line 310/343) instead of asking the registry what the
   node's Type accepts.
3. **Placed, not derived** — `place()` (lines 209-219) is an explicit ring layout: "only for nodes
   without a pinned position... a drag/insert PINS x/y." The code comment itself admits this is a
   stopgap ("the spatial theorem: a manual move writes a new frozen address" — describing law, not
   implementing it: there is no mixed-radix address, no n/x span, just `cos`/`sin` around a circle,
   lines 216-217). This matches the doctrine's own self-score (the-whole-thing.html:285, "45% —
   ring layout = placed").
4. **Not wearing the DNA** — see §2a in full: hardcoded hex fallbacks on every token reference
   (60+ instances), no `CanvasHeader`, no `containers.css` Band/Zone/Cluster, no shared button
   component (raw `<button>` + inline CSS, glyphgraph-generator.html:26-29, duplicating what
   presumably a `Button` component in `components/Button.jsx` already provides — **not verified
   by direct read of Button.jsx in this pass, flagged Inferred**).
5. **Two-way partial** — words teach (glosses persist, `AI.execute('glyphic.author-gloss',...)`,
   lines 427, 489, 564, 604) but **relations do not**: there is no equivalent UI for
   `glyphic.author-relation` (which exists and works, ai-glyphic-language.js:37-43) anywhere in the
   writer. An unresolved relation phrase is only ever reported as loose/unconnected (line 470) —
   the human has no way to *teach* the system a new relation-word the way they can teach a new
   symbol-word. **This is the concrete "relation-teaching UI" gap ANCHOR §4 names** — now traced to
   its exact missing call site.
6. **Not frame-resolved** — nothing in the writer asks "who/what is viewing this" and adjusts
   density/wording (the reader-face, THE-GENERATIVE-LANGUAGE §1.8/§3.2). The read-out
   (`M.readGraph`) always renders the same register regardless of caller. Matches doctrine's own
   15% score, the lowest bar in its table (the-whole-thing.html:289) — this assessment confirms
   that number is fair, possibly even generous, since there is literally zero code path that varies
   by reader.
7. **One-way surface (session substrate)** — `window.CV_GLYPHGRAPH_SESSION` (line 204) is written
   by the writer and *read* by `glyphic.assist`, but nothing external can address a specific past
   session or graph — there's no `ui://` or `glyph://` handle to "this conversation's graph" that
   another surface (a second browser tab, the Company's own memory) could resolve. This is the
   "no reindex-after-save bridge route" gap made concrete at the session layer, not just the corpus
   layer (line 606's toast literally tells the human to run a manual `node` + `python3` command —
   an honest but very unproductized admission of a missing route).

---

## 6 · Provision gaps (the 80% law — furniture, not just restraint)

- **No organisms/atmosphere** — the `.stage` (line 33) is a flat `background:var(--paper-2,...)`
  rounded box. No ambient texture, no zone-depth wash (contrast with `containers.css`'s computed
  `.cv-zone` wash, §2a). A "void is not calm" (doctrine §1.11) — the stage before any graph exists
  literally is a void with one centered hint string (line 102, 225).
- **No evidence density** — the Meaning panel (lines 300-354) shows exactly one node's state +
  relations + a collapsed `<details>` for form refinement. No history, no confidence/score display
  for AI-resolved words (the `resolveWord` judge verdict, line 424-430, is silently applied or
  silently asked — never shown to the human as evidence of *why* a word resolved the way it did).
- **No fields** — confirmed unbuilt (ANCHOR §36 already states this; I confirm by absence: no
  gradient/warmth CSS anywhere in the file, no per-node recency/attention data captured or
  rendered).
- **Confident type / fill** — partially present (the compose box has decent typographic weight,
  lines 9-17) but the stage and panel are timid relative to the Studio's real density (compare
  `Icons.jsx`'s categorized-section rhythm, which visually organizes ~150 icons with headers +
  counts + a toolbar — the writer's tray (§287-297) is a flat wrapping row with no grouping at all
  even though nodes plausibly cluster by kind/domain the same way icons do).

---

## 7 · Summary for the build that follows

**Three concrete, sequenced moves**, not a rewrite:
1. **Recompose the chrome** (CanvasHeader, RefinePop, containers.css Band/Zone/Cluster, real
   Button component) — token/component swaps, cheap, immediately raises the "wearing the DNA" bar
   from ~10% toward the Studio's real floor.
2. **Port into `app/canvases/GlyphgraphWriter.jsx`**, registered and tiled in `Overview.jsx`, so it
   stops being an orphan and gains a `FaceMarker`, a nav entry, and Studio-shell membership — this
   is the mechanical answer to "what would integrating into the Studio mean."
3. **Wire to `CV_REGISTRY`** (glyphic-type.js's parts/slots/sockets) instead of hand-enumerated
   value lists, and **add the missing relation-teaching call site** (`glyphic.author-relation`
   already exists and is unused) — these two close the biggest "derived, not placed" and "two-way"
   gaps without inventing new capability, only wiring existing ones.

The placement/spatial-theorem work (item 4 in the effort table) and fields-on-canvas remain
genuinely new builds, correctly flagged as "the honest hard parts" in ANCHOR §4 — this assessment
does not find a shortcut around them, only confirms they are real and separates them cleanly from
the (much cheaper) chrome/registry-wiring work above.

**Also fold in, per §3:** the icon-generation triplication (Icons.jsx built-in / glyphic-foundry.html
/ writer's inline makeIcon) needs a single fused capability-and-surface decision before any of the
three gets more investment — building "the" foundry UI without resolving this trebles the future
maintenance surface for no benefit.
