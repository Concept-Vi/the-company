# AREA-10 — The Studio app: canvases, surfaces, and the talk→surface machinery

> Wave-2 coverage agent. Territory: `claude-ds/app/` — `App.jsx`, all canvases, the
> `workshop/` sub-canvases, and `components/`. Wave-1 never read this directory; the
> synthesis (LIVE-INSTRUMENT.md) checked the **Company** repo for reactflow/tldraw but
> not `claude-ds/app/`. This file grounds "where does the live-instrument surface live,
> and what conversation→surface machinery already exists to reuse" in the actual app code.
> Marks: **Observed (file:line)** / **Inferred** / **My-idea**. Read fully — sized for depth.

---

## TL;DR (the three lines, expanded into the body below)
1. **The propose→preview→accept/correct interaction shell already exists and works** — the
   Workshop `BRIDGE` + ChatRail `WSDiffCard` loop (talk → Vi proposes a *batch diff* → you
   apply or discard → the live doc mutates). This is a direct precedent for the
   voice-correction loop the synthesis calls "wholly novel" — the *integration* is novel,
   the *interaction shell* is not. **Reuse it.**
2. **This app is the wrong host for the live graph canvas, with hard evidence** — it is
   Babel-standalone-from-unpkg, no build step, every canvas a `<script type="text/babel">`
   tag, third-party libs injected as raw CDN `<script>` at runtime
   (three.js via `unpkg`). reactflow/tldraw/cola/dagre/elk appear **nowhere** in `app/` or
   `core/`. This *confirms* the synthesis decision to build the live surface as a separate
   Vite `surface/app`, and supplies the concrete why.
3. **The dual-surface authoring pattern is mature and copyable** — `TypeBuilder` has four
   co-equal authoring modes (`visual | form | vi | json`) over one draft; `RegistryInspector`
   does live inline `R.update()` edits straight onto the registry; `Registry` extends purely
   by typed prompts ("add a thing" → Vi drafts a registered Type). Talk-and-direct-edit
   already co-exist on one object here.

---

## (a) What the Studio app IS + how it's structured

### The shell + the canvas-switch pattern
**Observed (App.jsx:4-5, 222-239)** — `App` holds a single `active` string in state
(`useState('overview')`). The body is a long `if/else if` chain that maps `active` → a JSX
canvas component (`overview`→`<Overview>`, `build`→`<Build>`, … `bridge`→`<Bridge>`),
falling through to `<StubCanvas>`. There is no router — navigation is a state setter
(`setActive`), exposed globally as `window.cvNav` (App.jsx:108-111) so any canvas or chat
link can route without prop-drilling.

**Observed (App.jsx:241-278)** — the layout is a 3-zone shell: `<Sidebar>` (left nav,
collapsible), `<main className="dsa-main">{canvas}</main>` (the active canvas), and
**`<ChatRail scope={active}/>` pinned on the right for every canvas except `registry`**
(App.jsx:262). So **the conversation rail is a first-class, always-present zone of every
surface** — Vi is structurally co-resident with whatever you're looking at. (Relevant: a
live-instrument surface would naturally inherit this same `<main> + <ChatRail>` shell.)

**Observed (App.jsx:6-21, components/usePersisted.js)** — almost all app state is
`window.usePersisted(key, default)` — a thin `localStorage`-backed `useState`
(usePersisted.js header: "Survives refresh; namespaced so we can clear/export everything at
once"). The app is a **single-user, local-first, browser-only** tool — no backend, no
server session. **Inferred:** this matters for the live layer — the Company's server-side
local models live across an HTTP boundary this app has no standing connection to (it only
reaches OpenAI/Claude via `CV_AI` providers). The synthesis's "browser→Company `company-http`
runtime" wire (G-L1) is exactly the missing bridge; nothing in `app/` currently crosses to
`:8770`.

### How generation is already wired into surfaces (the existing pattern)
Two distinct shapes, both routing through the one `CV_AI` catalogue:

- **Per-canvas inline generation** — each canvas calls `window.CV_AI.complete(prompt)` or
  `CV_AI.execute(capabilityId, …)` directly and renders the result into its own UI. E.g.
  `Voice.jsx:82` (`CV_AI.complete` to rewrite copy), `Icons`/`Colors` ("real AI generation"
  per their headers), `Inbox` ("real AI tagging"). The model touch is single-sourced; the
  surface is bespoke.

- **The Build canvas = an in-browser extract→generate→compose fleet** (the strongest
  precedent for the anchor's pipeline). **Observed (Build.jsx:1, 43-87)**: Build is a
  "cross-canvas Vi planner with 3-layer task tree." You give a brief; `CV_AI.execute('build.plan')`
  decomposes it into **2-4 parallel subtasks, each a specialist sub-agent that touches ONE
  canvas** (Build.jsx:49) — `icons-generator`, `colors-generator`, `copy-writer`,
  `type-builder`, **and exactly one `composer` at the end** (Build.jsx:60, 71). Subtasks run,
  then the composer composes the final output (Build.jsx:112-152). **This is Tim's
  extraction-vs-judgment law already implemented in the browser**: many specialist
  generators in parallel, one composer that judges/assembles. The live-instrument's
  extract-roles→compose-graph is the *same shape* pointed at a glyphgraph instead of a
  brochure. (Difference: Build uses cloud `CV_AI` providers and runs once per brief; the
  live layer wants server-side local models firing continuously at speech pauses.)

**Verdict:** the app is **real-reusable as a structural reference** (the shell, the
always-present rail, the CV_AI single-source generation, the plan→fan-out→compose pattern),
but **not as the host** for the live canvas (see (c)).

---

## (b) The conversation→surface pattern — ALREADY EXISTS (the headline find)

There is a working "talk → AI proposes a mutation → you accept/correct → the surface
changes" loop. It is the **Workshop bridge**, and it directly answers "is there already a
conversation→surface pattern to reuse for talk→glyphgraph?" — **yes.**

### The BRIDGE — "what surface Vi is on" + apply-a-diff
**Observed (AIEngine.jsx:813-843)** — a module-global `BRIDGE` object:
- `BRIDGE.setActive(doc, saveDoc, ctx)` records the live doc AND calls
  `CV_AI.setActiveSurface(doc.type, doc, {currentPage, selectedIdx})` (AIEngine.jsx:825) so
  every capability's context resolves from the live surface **without being passed it by
  hand** (the "interface = projection of the registry" contract).
- `BRIDGE.apply(diff)` (AIEngine.jsx:833-838) runs `applyDiff(BRIDGE.doc, diff)` and calls
  `saveDoc(next)` — i.e. it mutates the live document.
- `BRIDGE.subscribe/notify` (AIEngine.jsx:839-842) — pub/sub so any surface re-renders when
  the doc changes. Exported as `window.WS_AI.bridge` (AIEngine.jsx:1256-1269).

### The loop, as the ChatRail drives it
**Observed (ChatRail.jsx:104-156)** — when `scope === 'workshop'` and a live doc exists
(`WS_AI.bridge.getActive()`):
1. `WS_AI.classifyIntent({doc, message})` decides **edit vs question**
   (AIEngine.jsx:624-644 — an LLM JSON classifier, "loud" on failure, no silent downgrade).
2. If `edit`: `WS_AI.generateEdit({doc, message})` (AIEngine.jsx:646-687) returns
   `{summary, diff:{kind:'batch', diffs:[ops…]}}` — a **batch of typed ops**
   (`block.update`, `block.insert`, `page.insert`, `doc.update`, `widget.data`,
   `wizard.step.*` — AIEngine.jsx:665-676), each addressed by index.
3. The proposal is rendered inline as a **`<WSDiffCard>`** (ChatRail.jsx:204-211) with
   **Apply / Discard** buttons.
4. `applyDiffMessage` → `WS_AI.bridge.apply(proposal.diff)` (ChatRail.jsx:146-156) commits
   it; toast says "Applied — ⌘Z to undo." Discard leaves the doc untouched.

**This is the propose→preview→commit/correct interaction shell.** Map it onto the live
instrument: *user speaks → extract/compose role returns a graph delta (a typed batch of
node/edge ops) → render the delta as a reviewable proposal → accept or correct by voice →
the glyphgraph mutates.* The synthesis (LIVE-INSTRUMENT.md "the one thing with no prior
art") is **half-right**: the end-to-end *voice-corrected realtime* integration is novel,
but the **propose→diff→apply/discard shell, the typed-op batch diff, the
`setActiveSurface` context-resolution, and the pub/sub-driven live re-render are all
already built** and reusable. *(My-idea:* a glyphgraph "diff" is the natural analogue of the
Workshop's batch diff — `{kind:'batch', diffs:[{kind:'node.add'…}, {kind:'edge.add'…},
{kind:'node.setState'…}]}` — so the existing `applyDiff` + `WSDiffCard` shapes generalise
almost directly.)

### Other reusable conversation surface bits
- **`computeSuggestions(doc, ctx)`** (AIEngine.jsx:762-807) — deterministic, doc-shape-aware
  suggested next actions ("Fill this empty page", "Add a CTA", "Shorten every block"). A
  live glyphgraph could surface equivalent talk-prompts ("name the missing relation",
  "what state is the buyer in?").
- **`WSCandidateGallery`** (AIEngine.jsx:855+) — streams N candidate variants with keyboard
  nav (arrows/Enter/number keys) and per-candidate refine. The "Vi proposes several, you
  pick" sibling of the single-diff path; reusable for "several ways to lay out / resolve
  this node."
- **`RefinePop`** (components/RefinePop.jsx) — the shared per-item "click ↻, type a change,
  refine" micro-conversation, used across canvases (Voice.jsx:234, Build). The smallest
  unit of talk→change.

### Important correction: the **Voice canvas is NOT speech**
**Observed (Voice.jsx:1-44)** — `canvases/Voice.jsx` is **"voice & tone"** = a *brand-copy
rewriter*: 7 written voice RULES (sentence case, no exclamation marks…), a vocab list, an
LLM "rewrite this text in brand voice" tool, and tone-variant generation. **It has zero
STT/microphone/audio code.** A naive reading of the wave anchor ("Voice/STT") would
wrongly assume this canvas is the speech entry point. It is not — there is **no
speech-to-text anywhere in `claude-ds/app/`**. The LISTEN stage lives entirely in the
**Company** voice system (per A3), across the HTTP boundary this app doesn't yet cross.
**This contradicts any layer-1 assumption that the design-system app already hears.**

---

## (c) Is this the Babel-from-unpkg app? — YES, confirmed, with the implication

**Observed (index.html:100-102)** — React, ReactDOM, and **`@babel/standalone@7.29.0`** are
all loaded from `unpkg.com` as `<script>` tags. **Observed (index.html:108-125)** — the core
solvers (`DiagramSolver`, `ContainmentTree`, `Slide`, `RenderType`) are **fetched as `.jsx`
source at runtime, string-stripped of `export`s, and `Babel.transform(...).code` compiled
in the browser**, then `new Function(...)`-eval'd. **Observed (index.html:153, 175-250)** —
*every canvas and component is a `<script type="text/babel">` tag* compiled live by
Babel-standalone. There is **no bundler, no build step, no `package.json` dep graph** for
the app; load order is hand-managed in the HTML (and CLAUDE.md §5 warns about it).

**Observed (components/Pano360.jsx:7-18)** — when the app needs a real third-party lib
(three.js), it injects `https://unpkg.com/three@0.160.0/build/three.min.js` as a runtime
`<script>` and falls back to a static image if it fails to load (Pano360.jsx:199). So the
app's *only* way to use an external lib is "drop a CDN script tag and hope" — there is no
module system to `import reactflow`.

**Observed (grep)** — `reactflow|react-flow|tldraw|cola.js|dagre|elk|cytoscape|d3-force`
return **nothing** in `app/` or `core/`. The existing graph render is the hand-rolled SVG
`core/DiagramSolver.jsx` (per A6). **My-idea / Inferred:** you *could* shoehorn a live canvas
in here (mechanically trivial — see below), but you would be CDN-script-loading a heavy
canvas lib into a Babel-compiled-in-browser page with hand-ordered globals and a strict
no-script/CSP discipline elsewhere in the corpus. That is exactly the "poor host for a canvas
lib" the wave flagged.

**The implication, stated for the build plan:** the live-instrument canvas should be a
**separate Vite app** (`surface/app`, as the synthesis decided), NOT a new Studio canvas.
This area is the concrete evidence for that decision. Vite gives you real `import` of
reactflow/tldraw + layout libs (cola/dagre/elk), a dev server that can hold a live SSE/WS
connection to the Company bridge, and freedom from the hand-ordered-globals fragility.

### …but note the two-way truth (where the live canvas could *also* touch this app)
**Observed (App.jsx:222-239, index.html:220-250, components/Sidebar.jsx)** — adding a canvas
to *this* app is genuinely trivial: (1) one `<script type="text/babel" src="canvases/X.jsx">`
tag, (2) one `else if (active === 'x')` arm, (3) one Sidebar entry. **So the design system
can host a *projection/launcher* of the live instrument** (a tile, a "page-face marker" — see
the `dsa-face-marker` / `CV_FACES` machinery at index.html:14-95 and Overview.jsx FaceMarker)
even while the live canvas *itself* runs in the Vite surface. *My-idea:* the Studio canvas is
the **map/launcher**; the Vite `surface/app` is the **instrument**. They join the way the
existing page-face markers open the live page at `:8774`.

**Verdict (c):** Studio app = **disposable as the live-canvas host**, **reusable as the
launcher/projection home and as the shell/interaction reference.**

---

## (d) RegistryInspector / TypeBuilder / Registry — the dual-surface authoring pattern

This answers "how are the registries already surfaced/edited?" The pattern is **one object,
many co-equal authoring surfaces, all writing to the single registry home** — the exact
shape the live layer needs (talk authors the same glyphgraph a user can also direct-edit).

### TypeBuilder — four authoring modes over one draft
**Observed (TypeBuilder.jsx:8-16)** — `mode: 'visual' | 'form' | 'vi' | 'json'` over a single
`draft` object. The same Type can be built by direct visual manipulation, a form, **Vi**, or
raw JSON — *interchangeably*. **Observed (TypeBuilder.jsx:52-70)** — `viPropose()` calls
`window.CV_TYPES_VI.proposeType({brief, parentId, layerHint, familyHint})` → drops the result
into `draft` → "Vi drafted a Type — review and Save." This is **talk→draft→review→commit on a
registry object**, the registry-authoring twin of the Workshop diff loop. **Observed
(TypeBuilder.jsx:28-50)** — the direct-edit side is fine-grained `patch`/`patchSlot`/
`patchVariable`/`addSlot`/`addVariable` mutators on the draft. (`TypeBuilder2.jsx` holds the
split-out sub-components — the searchable library rail, etc.)

### RegistryInspector — live inline edits straight onto the registry
**Observed (RegistryInspector.jsx:1-3, 10-73)** — a right-sliding inspector with "Vi
conversation always present." Inline name/description edits **commit on blur via
`R.update(typeId, …)`** (RegistryInspector.jsx:28-33) — editing the *live registry entry* in
place. `duplicate()` / `makeVariant()` (RegistryInspector.jsx:34-67) register new Types with
`extends`/`forkedFrom` lineage. Lineage breadcrumbs (RegistryInspector.jsx:80-89) make the
single-inheritance graph navigable. It `subscribe`s to `CV_REGISTRY` (line 13) so it
re-renders on any change — same pub/sub-projection contract as the Workshop bridge.

### Registry canvas — extend-by-typed-prompt
**Observed (Registry.jsx:1-60)** — reframed as a "Workshop Studio Floor": **workstations**
(decks / brochures / widgets / wizards / shared) each with **shelves** that are *typed
queries* into `CV_REGISTRY` (`query:{layer:'surface', family:'deck-slide'}`) and an
`addPrompt` ("A new slide layout — e.g. 'split image with quote'"). **Adding a registry entry
= typing a natural-language prompt into the right shelf** → Vi drafts a Type at the right
`layer`/`family`/`parent`. The interface is a pure *projection* of the registry (the menus ARE
the query results), and authoring is conversational. **Note** App.jsx:262 hides the ChatRail
specifically on `registry` — because the Registry/Inspector embed Vi *inside* the canvas
instead.

**The pattern, named:** *one home (`CV_REGISTRY` / the doc), N co-equal surfaces (visual,
form, talk, raw), every surface writes through the single mutator + a subscribe-driven
projection re-renders all of them.* **For the live instrument:** the glyphgraph is the one
home; the canvas (direct manipulation) and the voice/extract loop (talk) are two co-equal
authoring surfaces over it, both emitting typed diffs that `apply` to the single store, with
a subscribe-driven render — **exactly the TypeBuilder/Inspector pattern, generalised.**

**Verdict (d):** **real-reusable as the authoring-pattern reference** (the multi-mode,
single-home, projection-rendered, talk-can-draft model is precisely right). The *code* is
Type-Registry-specific and Babel-in-browser, so it's a **pattern to copy into the Vite
surface, not a module to import.**

---

## Reuse / disposable ledger (every surface in the territory)

| Surface | What it is (Observed) | Verdict for the live layer |
|---|---|---|
| `App.jsx` | state-machine shell, `active`→canvas if/else, always-on right ChatRail, `window.cvNav` | **Reference** (shell + rail pattern); not the host |
| `index.html` | unpkg React+ReactDOM+**Babel-standalone**; every canvas a `text/babel` tag; runtime-fetched core | **Disposable as host** — the proof the live canvas needs Vite |
| `components/ChatRail.jsx` | the talk surface; image-intent route + **Workshop diff-propose loop** + plain chat | **Reuse the loop** (propose→`WSDiffCard`→apply/discard); rest is bespoke |
| `workshop/AIEngine.jsx` | `WS_AI`: `BRIDGE`, `classifyIntent`, `generateEdit` (batch typed-op diff), `applyDiff`, `computeSuggestions`, `WSCandidateGallery` | **Reuse the machinery** — closest existing analogue of talk→graph-delta |
| `canvases/Build.jsx` | plan→**2-4 parallel specialist subtasks→one composer** (extraction-vs-judgment, in-browser) | **Reference** — the pipeline shape, cloud+one-shot not realtime |
| `canvases/Voice.jsx` | brand-COPY rewriter (text rules/tone) — **NOT speech** | **Disposable for this layer** (corrects a naive anchor read) |
| `canvases/TypeBuilder.jsx` (+`TypeBuilder2`) | 4 co-equal modes `visual\|form\|vi\|json` over one draft; `viPropose` | **Pattern reference** for dual-surface authoring |
| `canvases/RegistryInspector.jsx` | live inline `R.update` edits + always-present Vi + lineage | **Pattern reference** (single-home + projection re-render) |
| `canvases/Registry.jsx` | projection of `CV_REGISTRY`; extend-by-typed-prompt workstations | **Pattern reference** (conversational extend-by-registration) |
| `canvases/Workshop.jsx` | the doc composer (deck/brochure/widget/wizard) that owns the bridge doc | **Reference** (host of the bridge pattern) |
| `canvases/Architecture.jsx` | static explainer of the registry (diagrams) | Disposable |
| `canvases/Bridge.jsx` | projection of `CV_HOST` — runtimes, staged serialized changes, apply-to-disk | **Adjacent-relevant** — the *propose-change→review→apply-to-real-source* discipline (a sibling of the diff loop, for code writes) |
| `canvases/Imagery.jsx` + `AIStudio.jsx` (orphan-in-App but mounted via Imagery:79) | image gen/edit subsystem (OpenAI) | Disposable for this layer |
| `canvases/Inbox/Icons/Colors/Patterns/Components/Templates/Settings/Overview/StubCanvases` | per-asset canvases; several use inline `CV_AI` generation | Reference at most; mostly out of scope |
| `workshop/{Blocks,Layouts,Polish,Section,Library,Export,WidgetBuilder,WizardBuilder}` | block definitions + per-doc-type builders | Reference for "block kinds as data"; not on the path |
| `components/Pano360.jsx` | three.js loaded via runtime **unpkg `<script>`** | **Disposable**, but its loader is the (c) evidence: CDN-script is the only lib mechanism here |
| `components/{Sidebar,CommandPalette,CanvasHeader,RefinePop,Resizable,ViShape,Toast,usePersisted,ImageEditor,MaskEditor,KitPreviews,ExportPatch}` | shared UI atoms | `RefinePop` = reusable micro-conversation; rest bespoke |

---

## No-staleness watch (where this app would let hardcoding sneak into the live layer)
- **Provider pin lives here too:** `AIEngine.jsx:188` (`resolveProvider(provider || 'claude')`),
  `AIEngine.jsx:1311` (`resolveProvider('claude')`), ChatRail.jsx:80
  (`resolveProvider('openai-image')`). Same `'claude'` literal the synthesis flags at
  ai-registry.js:315/343 — **Observed** it recurs in the app layer, so the role-layer fix
  (G-L1) must cover these call sites, not just the registry.
- **`SYSTEM_CONTEXT` / `BRAND_VOICE` are inline prose** (ChatRail.jsx:35-41; AIEngine
  `BRAND_VOICE`). The brand voice is *supposed* to be sourced from `CV_AI.get('voice.conceptv')`
  (AIEngine.jsx:177) — the ChatRail's hardcoded `SYSTEM_CONTEXT` block is a drift instance to
  not replicate when the live surface composes its prompts.
- **Block-kind / doc-type lists** (`DOC_TYPES` Workshop.jsx, `WS_BLOCKS`) are registry-backed
  where it counts but have inline label/`active` flags — fine as seeds, a caution for the
  live node-type set (keep it one generic render-from-data node, per the synthesis).

---

## Summary (3 lines)
The talk→surface loop the synthesis calls "novel" is **half-built already**: the Workshop
`BRIDGE` + ChatRail `WSDiffCard` propose→diff→apply/discard shell (AIEngine.jsx:624-843,
ChatRail.jsx:104-156) is a directly reusable AI-proposes-mutation/user-corrects interaction
model, and Build.jsx:43-152 is the extraction-vs-judgment pipeline already running in-browser.
This app is confirmed Babel-standalone-from-unpkg with no build step and zero graph-libs
(index.html:100-125; reactflow/tldraw absent), so it is the **launcher/shell reference, not
the host** — proving the synthesis's "separate Vite `surface/app`" decision; and
TypeBuilder/RegistryInspector/Registry give the mature **single-home, multi-mode
(visual+form+talk+json), projection-rendered** authoring pattern the glyphgraph should copy.
Path: `/home/tim/company/design/claude-ds/analysis/glyphic-language/live-instrument/findings/AREA-10-app-canvases-surfaces.md`
