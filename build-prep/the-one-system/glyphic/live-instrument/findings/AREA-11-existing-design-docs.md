# AREA-11 — Existing design docs: what's already decided/built that bears on the live instrument

> Wave-2 COVERAGE agent. Territory = `analysis/*` (the ~26 design-system docs, NOT the glyphic-language/
> subdir) + the root charters. Wave-1 (LIVE-INSTRUMENT.md / AREA-1…7) was written **mostly Company-side**
> (voice/STT, the bridge SSE, cognition role-dispatch, the `canvas/app` tldraw surface). **This area is the
> complementary half: the design-system + glyph-ENGINE side.** Almost nothing here CONTRADICTS the layer-1
> plan; it *fills in* the RESOLVE / RENDER / NARRATE / meaning / provider machinery the wave under-read,
> and surfaces several already-BUILT pieces the plan treats as "to build" and several hard CONSTRAINTS the
> live layer must obey. Evidence marked **Observed (file:line)** / **Inferred** / **My-idea**.

---

## 0 · The single biggest correction to the wave-1 picture

**Coverage note (honest):** I read the high-relevance docs in full (HANDOFF · AXES · INTEGRATION · UNIFICATION ·
REQUIREMENTS · LANGUAGE · DIAGRAMS · SYNTHESIS-PLAN · SYSTEM-GAPS · both SYSTEM-MAPs · AUDIT-INDEX · the
relevant FINDINGS-LOG slices 7–23 and 58–80) + the root charters. **`STUDIO.md` is named in the brief but does
NOT exist in `analysis/`** (confirmed by `ls`) — not skipped, absent. PROGRESS · GUIDE · AUDIT-SLICE1 ·
AXIS-REFACTOR (skimmed) · the per-source deck docs (pitch-deck/deck1-2026/recent-pitches/vt-family/mid-lod/
capital-raise/landing-mockups/deck1) were triaged as low-relevance static-deck DNA and grepped for
`interactive|live|conversation|voice|runtime` (only generic brand-voice/affordance hits) — read-as-low-relevance.

**The wave under-read its own repo's build memory.** `analysis/FINDINGS-LOG.md` is 213 KB and was modified
the morning this wave ran (2026-06-30 09:05). The wave read the *summary* (`LANGUAGE.md`) and the Company
side, but the **engine build slices (58–80) are right there and show the glyph-engine is far past "spec".**
Concretely, the live instrument's RESOLVE → RENDER → NARRATE stages already have working code in
`claude-ds/`, not just a Company-side equivalent:

- **A glyphgraph already lays out and reads itself out live.** **Observed** `core/DiagramSolver.jsx:368`
  `if (graph.type === "glyphgraph") return glyphGraphView(graph);`; `glyphGraphView` at `:279` renders
  **each node as a full glyphic** via `CV_GLYPHIC.render` (`:272` comment) and **each edge's meaning as a
  2-node `readGraph` clause in a `<title>`** (`:308–313`). FINDINGS slice-80 (`FINDINGS-LOG.md:8–46`) is
  the build record: authored x/y in 0..1, else a **closed-form longest-path layered fallback, else a ring
  — "no external layout lib"**; edge labels off by default; the live paragraph computed from the SAME graph
  via `CV_MEANING.readGraph`; verified rendering 440×440 with 4 glyphics + 3 edges at `:8775`.
- **This is the load-bearing find for DECISION 1 (reactflow vs tldraw).** It is a genuine **third data
  point** — the design system *already renders and narrates a glyphgraph*. **But characterise it
  precisely:** it is a **computed SVG layout + read-out**, NOT an interactive draggable
  incremental-growth canvas. No drag, no stable-incremental relayout, no SSE/store binding. So it
  informs the renderer choice as a *candidate render-from-data path*, and proves "graph → laid-out
  glyphics → spoken sentence" is solved, but it is **not** "the live instrument surface already exists."

**My-idea (reconciliation for synthesis):** the live instrument is *neither* a fresh build *nor* the
Company's tldraw canvas alone — it is **the Company's voice+extract+cognition spine driving the
design-system's already-built glyph-engine** (`CV_GLYPHIC.render` + `DiagramSolver case 'glyphgraph'` +
`CV_MEANING.readGraph`). The two halves the two waves saw are the two halves of one machine, exactly as
`analysis/UNIFICATION.md` framed the original block/graph weld.

---

## 1 · What is ALREADY designed / decided / built (bears directly on the pipeline)

### 1a · RESOLVE — the glyph engine is built, single-sourced, loud-fail
The whole `CV_GLYPHIC` / `CV_MEANING` / `CV_ICONS` / `CV_SHAPES` / `CV_AXES` stack the ANCHOR §7 lists as
"real anchors to verify" is **confirmed built and wired**, with the build history:

- **`CV_GLYPHIC` (the unit's one home)** — **Observed** FINDINGS `:753–759` (slice ~52): `assets/icons/
  cv-glyphics.js`, mirrors the CV_REGISTRY/CV_AI shape (`facets` 8-facet schema, `defaults`, `normalize`,
  `validate` **loud-fail vs live vocabularies**, `compose`/`render` delegating geometry→`CV_SHAPES.markSVG`,
  symbols→`CV_ICONS`). **Pure composition layer, redraws nothing.**
- **Meaning is a LOADABLE registry of profiles** — **Observed** FINDINGS `:723–732`: `assets/icons/
  cv-meaning.js` → `CV_MEANING`, `register/load/export/resolve/use/valuesFor/meaningOf/tokenForValue`,
  default profile `conceptv-default`, profiles round-trip to JSON (`export()`→edit→`load(json,makeActive)`),
  `use(id)` switches context, **loud-fail on unknown profile**. INVARIANT (geometry, symbols) vs CONTEXTUAL
  (what form/colour/fill/etc *mean*) cleanly separated; **symbols deliberately excluded** (`valuesFor
  ('symbol')` throws — "a house is always a house", **Observed** `:721,727`).
- **Every facet is a first-class AXIS** — **Observed** FINDINGS `:640–669` (slice 59) + `AXIS-REFACTOR.md`:
  `CV_AXES` with 9 axes (color·space·size·motion·texture·depth·fill·form·symbol), **tokens ARE the value
  units** (`AXIS-REFACTOR.md:24–31`), a glyphic part-slot is a **subscription** to an axis, not a copied
  table. Hardcoded "glyphic motion" was explicitly de-owned into the Motion axis.
- **The universal-component grammar** — **Observed** FINDINGS `:674–717` (slice 58): the Glyphic is a real
  `CV_REGISTRY` component with **parts / slots / sockets / conditions**; "everything on an interface is a
  templated dynamic component; the interface is a projection of declarations" (`DESIGN-LANGUAGE.md:115–128`,
  94 Types live). **This is the grammar the live canvas's nodes/edges should be declared in** — a node is a
  glyphic Type instance, an edge a `relationship.*` Type.
- **The glyphgraph RULEBOOK exists** — **Observed** FINDINGS `:48–75` (slice 79): `app/registry/
  relationships-seed.js` (one Type per edge-kind, source/target sockets) + `assets/icons/glyphgraph.js`
  (`CV_GLYPHGRAPH.validateGlyphgraph` — domain/range via `CV_REGISTRY.accepts` + `CV_COND`,
  collect-then-throw, structural ill-formedness throws). So the **EXTRACT→graph output has a validator to
  pass through before RENDER** — the live composer (G-L4) should emit graphs that `validateGlyphgraph`
  accepts.

### 1b · GENERATE-ON-MISS — the foundry is built AND has a conversational UI
- **`glyphic.generate` + `glyphic.save`** — **Observed** FINDINGS `:704–708` (slice 58): `app/ai/
  ai-glyphic.js` registers `glyphic.generate` (threaded multi-step, parses+validates candidates against
  `CV_GLYPHIC.schema.symbol`) + `glyphic.save` (validate→`CV_ICONS.add`, provenance vi, localStorage
  write path). Matches ANCHOR §7 exactly.
- **A conversational foundry UI already exists** — **Observed** FINDINGS `:610–614` (slice ~57):
  `system/glyphic-foundry.html` is a **"conversational propose→feedback→click→save surface"** routing
  through `CV_AI.execute('glyphic.generate')`, graceful DEMO fallback when no model bound, Save →
  `CV_ICONS.add` + symbol-axis rebuild; **verified end-to-end** (4 candidates render as live glyphics, Save
  grew the library 126→127). **Inferred:** this is a near-twin of the generate-on-miss leg the plan's G-L2
  calls "BUILD" — the surface and the wiring exist; what's missing is the *automatic* trigger (lookup miss
  → generate) rather than a human clicking, and the bound live provider.

### 1c · NARRATE — the SENTENCE is composed here, not just spoken Company-side
Wave-1 saw the *speaking* half (TTS, `/api/say`, `speakable`). **The design system composes the sentence
from the graph** — **Observed** `core/DiagramSolver.jsx:312–313` (`readGraph` per edge) + FINDINGS `:36–39`
(the live paragraph computed from the graph via `CV_MEANING.readGraph`) + `LANGUAGE.md:28–30`
(`CV_MEANING.describe(spec)` → `{sentence,parts,meaningSet}`; `CV_MEANING.describeRelation`;
`CV_GLYPHIC.describe` delegates so any glyphic anywhere says itself). **NARRATE is therefore a TWO-PART
seam, complementary not duplicate:** design-system composes the words → Company speaks them.

### 1d · The browser↔Company / browser↔disk boundary already has a registry answer (the FIFTH registry)
The ANCHOR §6 flags "the browser↔Company boundary (design system runs in a browser; local models are
server-side)" as a hard part. **There is already a designed answer the wave-1 plan did not surface:**

- **A fifth single-source registry — `CV_HOST` runtimes** — **Observed** `DESIGN-LANGUAGE.md:97`:
  *"what can Vi DO to the repo it runs in… `capability-available = f(environment, runtime)`. Runtimes are
  pluggable and resolved by capability: `review` (sandbox floor — no disk, stages every change as real
  source; always available), `fsapi` (browser File System Access), `native` (`window.CV_HOST_NATIVE` — a
  local shell or MCP host giving read/write/list/exec/tools, auto-detected on export)… Add a way to reach
  the world (a Tauri shell, an MCP file tool) = register a runtime, not edit every caller."* Also ANCHOR
  §7's `host-runtime.js`/`host-serializer.js` and FINDINGS `:1839–1862` (the CV_HOST build, "providers
  without CV_AI knowing how to reach them. Still loud").
- **My-idea / Inferred:** the plan's "**BUILD a `company-http` runtime**" (LIVE-INSTRUMENT §catalogue) is
  **literally a new `CV_HOST` / `CV_AI` runtime registration**, not new plumbing — exactly the
  "register a runtime, not edit every caller" pattern already in the charter. The browser-side model call
  to the Company bridge `:8770` is *the same shape* as the existing `native`/MCP-host runtime.

### 1e · The browser-can't-write-disk boundary has a PROVEN precedent (op-queue → adapter)
**Observed** `SYSTEM-MAP-EDITOR-ADAPTER.md` (whole) + FINDINGS `:194–214` (slice 74): the System Map editor
**cannot write project files from the browser**, so it mutates an in-memory model, persists to
`localStorage`, and emits a typed **operation queue**; a disk-write **adapter** (Claude Code / any FS host)
replays it, with a **staleness guard** (`generatedFrom` vs `generatedAt`), idempotence, and "re-source after
apply". **My-idea (pull forward):** this is the exact, already-working pattern for any
**browser-canvas-writes-back** leg of the live instrument (e.g. a voice-correction that should persist a new
icon or a graph edit) — the live layer should reuse the op-queue→adapter shape rather than inventing a new
browser↔disk path. It is the design system's answer to the same boundary the ANCHOR flagged.

### 1f · CV_AI is already multi-provider, multi-capability (matches the wave's A1 correction)
**Observed** FINDINGS `:1839–1916` (slices 10–11) + `DESIGN-LANGUAGE.md:94` + `CLAUDE.md §2`/`INTEGRATION.md
§6`: `CV_AI` = providers (model endpoints, `resolveProvider` binds to live runtime, **throws if absent**) ·
behaviours (the voice `voice.conceptv`, sourced once) · skills (transform menu is a projection) ·
capabilities (`id == move`, the catalogue IS the dispatch, **43 across 14 families**) · context (surface-keyed
resolvers, `execute()` resolves "what screen Vi is on" automatically). `ai = f(capability, context, params)`,
the mirror of `design = f(content, axis)`. This **confirms wave-1's A1 correction** ("CV_AI is NOT a
single-claude monoculture in plumbing") and gives the precise extension point: the live extract/compose
roles are **new `CV_AI` capabilities**; the Company-fleet provider is a **new provider record + runtime**.

### 1g · The System Map proves the live-canvas interaction patterns already work in-repo
**Observed** FINDINGS slices 68–80 (`:8–397`): the System Map (`system/system-map.html` +
`system/build-system-map.js`) is a **living codebase canvas** with: a backend-owned model regenerated by a
generator (the JSON is OUTPUT, never hand-edited — `:375`); switchable **layouts as a registry** (LAYOUTS/
SIZERS/COLORERS projected into selectors — `:265–284`); **FLIP-morph incremental relayout** that is
"AUTHORITATIVE & INSTANT, the morph never affects correctness" (slice 70, `:287–306`); **edge types keyed by
bidirectional verb pairs** (`:246–260`); **visual encoding sourced from `CV_MEANING.encodings`**
(`SYSTEM-MAP-ENCODING-GRAMMAR.md`); pointer-based **drag-and-drop** (`:179–185`); **undo/redo** snapshot
stack (`:174–177`); and a **glyphic toolbar that is a projection of the glyphic system** (`:162–171`).
**Inferred:** every interaction the live instrument's canvas needs — incremental stable relayout, a
backend-owned model, render-from-data nodes, encoding from the meaning registry, edit→persist — has a
working precedent in this repo, on plain SVG/DOM with FLIP, **with no external layout lib**. This is a strong
input to DECISION 1 (it leans the renderer toward "render-from-data + backend-owned positions" on whichever
canvas, exactly as the plan says, and shows the design system can do it without reactflow OR tldraw).

---

## 2 · CONSTRAINTS the layer-1 plan MUST obey (the "principles the live layer must obey")

These are the hard contracts in this corpus. None *block* the plan; they *shape* it. The plan's GOVERNING
LAW already names the first; the others sharpen it.

### C1 · RESOLVE is COMBINATORIAL/FIELD meaning — NOT a flat noun→glyph lookup
**Observed** `LANGUAGE.md:8–12,50–55` (Tim, 2026-06-29): *"Meaning is a field, not a single thing… meaning is
combinatorial: the combination of facet values means, not each facet alone… A thing that means one fixed
thing is a lookup, not a language."* And the parts-of-speech are typed (`LANGUAGE.md:36–48`): form=kind,
symbol=thing, fill+outline=mode, color=state, texture=material, edge=relation, etc., with combination rules
(`mode` read from fill+outline+icon together). **Implication for the pipeline's RESOLVE stage (ANCHOR §3
stage 3):** a noun cannot resolve to one fixed glyph. **Semantic icon-lookup (the ANCHOR's embed→nearest)
is valid ONLY for SYMBOL ("which thing") — it is NOT the whole resolve.** The form (kind), fill/outline
(mode), colour (state), texture (material), edges (relations) must resolve through `CV_MEANING`'s
combinatorial grammar from the extracted entity/relation/state facets, **and is context-resolved** (the
loadable profile picks which value→appearance map is active — `:723–732`). RESOLVE = "compose facets into a
glyphic via CV_MEANING", not "look up an icon".

### C2 · The GOVERNING LAW restated five-fold + LOUD-FAIL
**Observed** `claude-ds/CLAUDE.md §0,§3` + `INTEGRATION.md §0,§6` + `LANGUAGE.md:15–19`: **one home per
concept; consumers hold references, never copies; loud-fail (THROW), never silent default/fallback.** There
are now **FIVE** single-source registries the live layer resolves from — tokens · types (`CV_REGISTRY`) ·
engine (`core/` solvers) · AI (`CV_AI`) · **runtimes (`CV_HOST`)** — plus `CV_MEANING`/`CV_AXES`/`CV_ICONS`
as the meaning/value homes. **Implication:** the live pipeline must add **no parallel store** — no
icon-tag list, no provider pin, no per-type render branch, no second meaning table. This is exactly the
plan's no-staleness mandate; the corpus makes it a hard, repo-wide law with a loud-fail clause
(`LANGUAGE.md:18` — *"an unknown facet / value / required lookup THROWS — no fallback, no silent default"*).

### C3 · Render-from-data, NO per-type branch — and zoning/tokens are inherited by construction
**Observed** `AXES.md:117–128` (block & graph are ONE system, two solvers, "pick the solver by content
kind"); `INTEGRATION.md §2,§6` (generated output "inherits the DNA by construction — it has no literals to
drift with"); `HANDOFF.md:330–333` ("better, make atom rendering itself a registry so new atoms are data,
not code branches"). **Implication:** the live canvas's node/edge renderers must be **one generic
data-driven path** (the plan's "one generic node-type + one edge-type"), and they must consume **L0–L2
tokens only** — which they get free by rendering through `CV_GLYPHIC.render` (already token-pure). This is
why the plan's "server composes the glyph SVG, FE reflects a resolved string" is right: it keeps the
token-purity invariant.

### C4 · Orthogonal axes — the canvas dials must not collapse
**Observed** `AXES.md:35–41`, `REQUIREMENTS.md C1–C6`: axes are **orthogonal and compose freely**
(surface ≠ LOD ≠ density ≠ theme); "correlation ≠ coupling". **Implication:** the live instrument is itself
a new **surface** on the existing axis space — it should be threaded as a `data-*` knob through the engine
like every other surface (`HANDOFF.md:187–190`, `INTEGRATION.md §6`), NOT a bespoke parallel renderer. A
live glyphgraph node still honours LOD/density/theme.

### C5 · The deck→app bridge already names "interactive = runtime mutation of the containment tree"
**Observed** `AXES.md:85–91`, `REQUIREMENTS.md F1–F3`, `SYSTEM-GAPS.md:48–51`: *"Interactive (deck→app
bridge) = runtime mutation of the tree… the embedded product UI (nav→panel→table→row) is the same
containment tree, just mutable. Decks render it fixed; the app renders it interactive — one model for
both."* **Inferred:** the live instrument's "graph mutates as you correct by voice" is the **graph-solver
case of this already-articulated principle** — voice-correction = a runtime mutation of the glyphgraph, the
same category as "expand a Section / reveal an Atom". The plan's novel loop (G-L4↔G-L5↔G-L6) is the
graph-side, voice-driven instance of a mutation model the design corpus already designed for the block side.
This is a *constraint that helps*: build the mutation as tree/graph mutation, not as a special live-only path.

### C6 · No-staleness already has a gate to extend (mechanisms registry), and the wave's "fixes" are real
**Observed** `analysis/SYSTEM-MAP-ENCODING-GRAMMAR.md:99–104` (principle gate: "if you find yourself writing
a colour/size value inside the UI, that's drift — move it into the encoding profile") + the design-folder
`CLAUDE.md` `_system/mechanisms.json` (the extend-by-registration check registry) + `check_design_system`.
**Implication:** the plan's G-L8 ("teach the gate 3 detectors — provider-pin / typed-list / render-branch")
is consistent with the existing `mechanisms.json` extend-by-registration model — register a mechanism, drop
its `_system/<x>.py` + test. **And the wave's "fix already-live staleness" claim is grounded:** the
hand-typed tags exist (icon facets are literals in `cv-icons.js`, FINDINGS `:748–752`), and the embed-index
fix is the same shape as the System Map's `CV_MEANING.encodings` re-runnable projection.

---

## 3 · What CONTRADICTS or under-states the wave-1 plan (the corrections)

Mostly the plan **understates how much is built**; the contradictions are small but worth flagging so
synthesis doesn't re-spec built work.

1. **"BUILD the live canvas pattern" understates it.** The plan's catalogue lists the live canvas as
   "REUSE (tldraw) OR build fresh (reactflow) — DECISION". **It omits that `claude-ds/` ALREADY renders a
   glyphgraph + reads it out** (`DiagramSolver case 'glyphgraph'`, slice 80) **and already has a full
   living-canvas interaction kit** (System Map: FLIP relayout, drag, undo, render-from-data, encoding-from-
   registry, edit→adapter). DECISION 1 is therefore **three-way**, not two: reactflow · tldraw · **extend
   the design-system's own SVG/DiagramSolver glyphgraph render** (which is already token-pure, meaning-aware,
   and self-narrating). **My-idea:** the third option is the most single-source-faithful — it reuses
   `CV_GLYPHIC.render` and `CV_MEANING.readGraph` with zero parallel renderer — its gap is *interaction*
   (drag/incremental-layout), which the System Map proves the repo can do on plain SVG with FLIP.

2. **"GENERATE-ON-MISS = BUILD" understates it.** `system/glyphic-foundry.html` is a built, verified
   conversational generate→save surface (slice 57). The genuinely-new part is only the **automatic
   miss-trigger** + the **bound live provider**, not the foundry UI or the generate/save capabilities.

3. **The provider/runtime work is registration, not new plumbing.** The fifth registry (`CV_HOST` runtimes,
   `DESIGN-LANGUAGE.md:97`) already defines the pluggable-runtime pattern for reaching the world (native/MCP
   host). The plan's `company-http` runtime is a `CV_HOST`/`CV_AI` registration of that exact pattern.

4. **NARRATE is half-built here, not just Company-side.** The plan marks NARRATE "fully built (a solved
   sink)" pointing at `/api/say`. It should note the **sentence composition** (`CV_MEANING.readGraph`/
   `describe`, used live in slice 80) lives in `claude-ds/` — the two halves must connect, and the
   read-out's *sentence-coverage* is explicitly flagged as a LIVE-tuning surface, not a build gate
   (FINDINGS `:42–46`: the auto-focus walk can drop a clause from the SENTENCE though the PICTURE shows all
   relations).

5. **Voice is an overloaded word — guard it.** In `claude-ds/`, "voice" overwhelmingly means **brand voice**
   (`voice.conceptv`, and the second saturated **sage-green "Communication" voice**, `DESIGN-LANGUAGE.md:58`),
   NOT spoken audio. The live instrument's "voice" (STT/transcript) is Company-side. Synthesis must not
   conflate `voice.conceptv` (a `CV_AI` behaviour) with the audio voice loop.

---

## 4 · The FINDINGS-LOG / HANDOFF narrative — what state the design system is really in

**Observed**, triangulating `HANDOFF.md`, `UNIFICATION.md §3`, and `FINDINGS-LOG.md` (newest-first):

- **The corpus analysis is complete and stable.** All 12 source folders analysed; the parametric model
  (`AXES.md`) "survived every one with zero contradictions" (`HANDOFF.md:152–155`). The static-deck DNA
  (zoning ladder, gold→bronze→tan ramp, containment tree, the 13 archetypes, diagram type system) is settled
  and low-relevance to the live instrument except as the rendering DNA the glyphs inherit.
- **The two halves were welded.** `UNIFICATION.md §3`: the bridge `typeToNode` (W1 ✅), single-sourced
  catalogue (W2 ✅), one engine in the app (W4 ✅), render-through-engine for block/slide/doc/widget (W3 ✅),
  generator loop for deck-slide (W5 ✅); W6 (inline-editing through the engine) mostly complete, W7 (live
  widget render) done. **Every fallback removed → loud-fail throughout** (`UNIFICATION.md:86–92`).
- **The most recent work is the Glyphic LANGUAGE + the living System Map** (slices 58–80), which is exactly
  the substrate the live instrument sits on. The Glyphic went from "Mark" (an icon) → a faceted unit →
  a universal component with parts/slots/sockets → a loadable meaning registry → an axis-resolved consumer →
  a validated glyphgraph with a live render + read-out. **This is the engine the ANCHOR §1 says "is
  finishing in parallel" — large parts of it are DONE.**
- **Honest soft spots that touch the live layer** (`HANDOFF.md:324–344`, FINDINGS flags): the glyphgraph
  render's mixed edge-routing + arrowhead angles + sentence-coverage are **explicitly Tim-FORM-tuning
  surfaces, not green** (FINDINGS `:42–46`); the icon taxonomy tags are hand-typed literals (the staleness
  the embed-index fixes); a few "missing parts" in `CV_GLYPHIC` were flagged (solid-colour fill value,
  dashed-outline render — `LANGUAGE.md:69–71`); no `templates/` is fully proven end-to-end; the app Studio
  itself isn't re-skinned. **None block the live layer; the FORM-tuning ones reinforce "verify by use,
  flag for Tim, never green-paint."**
- **The working discipline is non-negotiable and matches Tim's memory:** `check_design_system` after every
  edit; append a slice to `FINDINGS-LOG.md` (newest first); keep `DESIGN-LANGUAGE.md`/`README.md` in
  lockstep; loud-fail; verify by running, never claim done on a guess (`claude-ds/CLAUDE.md §4–5`,
  `HANDOFF.md §4`). **The live-instrument build must follow this same loop** — it is the same repo's law.

---

## 5 · Pull-forward list (what should shape the build)

- **Treat the live instrument as the graph-solver, voice-driven case of the already-designed "interactive =
  runtime tree mutation" (C5)** — not a parallel system. (AXES/REQUIREMENTS/UNIFICATION.)
- **RESOLVE = compose facets via `CV_MEANING` combinatorially (C1)**; semantic icon-lookup is ONLY the SYMBOL
  leg; everything else resolves through the meaning grammar + active loadable profile.
- **Render through `CV_GLYPHIC.render` + `DiagramSolver case 'glyphgraph'` + `CV_MEANING.readGraph`** — the
  most single-source-faithful renderer option (DECISION 1 third path); its only gap is interaction, which the
  System Map proves is doable on plain SVG+FLIP with no external lib.
- **Validate the composer's output with `CV_GLYPHGRAPH.validateGlyphgraph`** before render (loud-fail).
- **The Company-fleet provider = a `CV_AI` provider record + a `CV_HOST` runtime registration** (the fifth
  registry's pluggable-runtime pattern), not new plumbing. The browser↔Company call mirrors the existing
  `native`/MCP-host runtime.
- **Any browser-canvas-writes-back leg reuses the op-queue→adapter precedent** (`SYSTEM-MAP-EDITOR-ADAPTER.md`)
  with its staleness guard — the proven design-system answer to the browser-can't-write-disk boundary.
- **Generate-on-miss reuses `glyphic.generate`/`glyphic.save` + the `glyphic-foundry.html` UX**; build only
  the automatic miss-trigger + bound provider.
- **Gate detectors register into `_system/mechanisms.json`** (extend-by-registration), same as `check.py`.
- **Follow the repo loop:** `check_design_system`, FINDINGS slice (newest-first), docs in lockstep,
  loud-fail, verify-by-use, FORM-tuning flagged for Tim never green-painted.

---

### 3-line summary
The design-system half of the live instrument is far more built than the wave-1 plan assumes: the glyph
engine (`CV_GLYPHIC`/`CV_MEANING`/`CV_AXES`/the foundry), a **validated glyphgraph that already renders +
reads itself out** (`DiagramSolver case 'glyphgraph'`, slice 80, confirmed in code at `:368`), a
**conversational generate→save foundry**, and a full **living-canvas interaction kit** (System Map: FLIP
relayout, drag, render-from-data, encoding-from-registry, edit→adapter) all exist — so RESOLVE/RENDER/
NARRATE/generate-on-miss are largely WIRING + automatic-triggering of built parts, and DECISION 1 is
three-way (reactflow · tldraw · **extend the design-system's own token-pure self-narrating glyphgraph
render**). The hard CONSTRAINTS the live layer must obey are combinatorial/field RESOLVE (not flat
icon-lookup), the five-registry single-source + loud-fail law, render-from-data with no per-type branch,
orthogonal axes, and the already-articulated "interactive = runtime tree mutation" — plus two proven
boundary precedents the plan under-credits: the **CV_HOST pluggable-runtime registry** (the fifth registry)
for browser↔Company, and the **op-queue→adapter** for browser↔disk.

Path: `/home/tim/company/design/claude-ds/analysis/glyphic-language/live-instrument/findings/AREA-11-existing-design-docs.md`
