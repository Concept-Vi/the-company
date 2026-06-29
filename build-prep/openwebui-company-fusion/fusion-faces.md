---
type: proposal
register: descriptive
title: "Faces + Surfaces Fusion — how the Company's design-DNA/spatial surfaces and OpenWebUI's chrome relate (open, no horizon)"
aliases: ["fusion — faces", "Area H — faces"]
tags: [company, fusion, openwebui, faces, surfaces, design-dna, proposal]
status: unconfirmed
posture: >
  Both sides incomplete + unreviewed; NO source of truth; NO HORIZON — this does NOT anchor to a
  fixed end-state ("everything inside an OWUI shell"). It surfaces the real options openly with
  honest tradeoffs and does NOT pick a destination. Best parts fused INTO the Company centre; no
  duplicates. Confident prose ≠ correct (every "Observed-from-self-description" line is a module's
  own constitution, which the design charter itself calls a map, never a blueprint).
companion: "[[owui-side-map]] (the donor/host side — OpenWebUI 0.9.6, verified file:line)"
relates-to: ["[[THE FACE — build-grounding anchor]]", "[[FACE-1 HOST-NAV CONTRACT]]", "[[project-design-company-convergence]]", "[[canvas — constitution]]", "[[design/ — the corpus]]", "[[feedback-islands-join-mainland]]", "[[feedback-unions-not-bridges]]"]
evidence_basis: >
  Live filesystem checks (file:line) + the verified owui-side-map. Frontend "in use" claims about
  canvas/surface are Verified (port scan); their CAPABILITIES are Observed-from-self-description
  (AGENTS.md constitutions), labelled as such, not running-verified.
created: 2026-06-28
---

# Faces + Surfaces Fusion — the open option-space

> **Reading note.** The companion `owui-side-map.md` maps the DONOR side (OpenWebUI 0.9.6) with
> verified file:line. This doc is the COMPANY side + the relation between the two faces. The task's
> framing — "two design systems: design/ vs claude-ds?" — turned out **partly false on inspection**:
> there are **three** design lineages, nested/related, not two parallel duplicates (§3). The
> headline constraint is **not** "can't fork" — it is **can't strip OWUI branding above 50 users**
> (§4). Everything below stays OPEN: no option is the winner.

---

## 0 · VERIFICATION DONE (what was checked live, this pass)

| Claim | Method | Result |
|---|---|---|
| Nothing on 5173/5174 | `ss -tlnp \| grep :517[34]` | **Verified: none listening** — canvas + surface are NOT running (dev-only, all in development) |
| Canvas is React/tldraw on :5173 | `canvas/app/package.json` | **Verified**: `deps: react, react-dom, **tldraw**`; `dev: vite --host 127.0.0.1 --port 5173` |
| Surface is React on :5174 | `surface/app/package.json` | **Verified**: name `instrument-surface`, `deps: framer-motion, react, react-dom`; `dev: vite --port 5174`; `<title>Instrument</title>` |
| Surface renders through DNA | `surface/app/scripts/sync-gallery.mjs` | **Verified**: copies DNA's canonical files from `DNA_REPO=/home/tim/repos/counterpart/design` (`dna/`) into `public/gallery/` on every predev/prebuild; FAILS LOUD if DNA source missing |
| `design/` is a synced read-copy | `design/README.md:1-17` | **Verified**: one-way sync `build-prep/design/ → ~/company/design/`; never hand-edit; canonical edit point is `build-prep/design/_system/tokens.json` |
| `claude-ds` lives inside `design/` | `ls design/claude-ds` | **Verified**: NOT a sibling/parallel system — it is nested (the ConceptV brand DS); `design-system.css` = 72 token vars; `claude-ds/tokens/` = 18 CSS files |
| `claude-ds` ≠ the DNA repo | `ls` both; grep | **Verified distinct lineages**: `claude-ds` uses `_ds_bundle.js` + `CV_REGISTRY` + `axes/` + solvers; DNA repo uses `dna/*.json` (layouts/grammar/molecules) + `surface/runtime/archetype.js`. Different renderers (§3) |
| OWUI frontend fork-only + 50-user cap | companion `owui-side-map.md:194-204` | **Adopted as verified** (its evidence_basis = installed Python source + live docs) |

> ⚠️ **Confident ≠ correct.** Canvas/surface *capabilities* below are **Observed-from-self-description**
> (their AGENTS.md constitutions). The design charter itself says these maps are "never blueprints,"
> and `canvas/AGENTS.md` says the surface is "discovered through use — expect it to grow." Treat
> capability claims as the modules' own descriptions, not runtime-verified behaviour.

---

## 1 · BEST PARTS (surface, don't decide)

### COMPANY side — the irreplaceable parts

**1a · The design-DNA / token layers (THREE lineages, all genuine, all real today)**
- **`design/` corpus** (Observed: `design/CLAUDE.md`, `README.md:20-29`) — a one-way synced read-copy of canonical `build-prep/design/`. Registry-as-truth: `_system/tokens.json` → `emit.py` → `design-system.css` (72 vars); `addresses.json` (the `ui://` registry) → `parse.py`; `register.json` → `gallery.py`. A FORM gate (`check.py --target … --fail-on`) that lints app source against the tokens and **exits non-zero** to GATE a build. Code-ref drift validators (`refcheck.py`, `symbols.py`, `codeedges.py`). *Best part: the design IS an addressed, queryable, self-checking model — not a picture pile.*
- **`design/claude-ds`** (Observed: `claude-ds/README.md`) — the **ConceptV Design System**: brand shape-grammar (Circle/Hexagon/Octagon/Diamond per entity), `CV_REGISTRY` 7-layer Type model, **axis-dials** (Colour·Space·Size·Motion·Texture·Depth·Fill·Form·Symbol + Meaning), two solvers (block `ContainmentTree` + graph `DiagramSolver`), `design = f(content, axisPosition)`. *Best part: a compositional Type/axis grammar where a component is `parts·value-slots·sockets·conditions`, acceptance is declarative.*
- **DNA repo** at `/home/tim/repos/counterpart/design` (Observed: `THE-FACE-ANCHOR.md §2`, `sync-gallery.mjs`) — the renderer the **live company surface actually uses**: `DNA.renderArchetype` (`surface/runtime/archetype.js`) reading `dna/layouts.json` (11 archetypes + 22 slot_types), `dna/grammar.json` (29 invariants, nearest-scope-wins), `dna/molecules.json` (atoms→molecules→`slot_bindings`). *Best part: ONE renderer, MANY sources; new face = a new archetype record + slotHTML branch, no bespoke React.*

**1b · The spatial / projection surfaces**
- **Canvas** (Observed: `canvas/AGENTS.md`) — tldraw + React + Tauri desktop board; **one generic `ai-node` shape** data-driven from `/object_info`, so a new node-type needs ZERO frontend code. Reflects state, never owns it (runtime authoritative, peer via the bridge). *Best part: spatial, infinite-canvas, point-and-talk; render-modes are conditional rendering on node props.*
- **Surface** (Observed: `THE-FACE-ANCHOR.md`, `FACE-1-HOST-NAV-CONTRACT.md`) — the "instrument," the projection/territory face. ONE host (`surface/app/src/App.tsx` sibling-overlay mount) · ONE renderer (DNA) · ONE verb bus (`gallery:verb`) · address-resolve to HUMAN meaning (`/api/territory`, raw `ui://` never shown) · device allocation resolved from a coordinate (no `@media`). *Best part: "one system, many faces" — every face is a PROJECTION of one entity, not a parallel app.*

**1c · Resolution-first rendering (the spine)** — `resolve(invariant, coordinate) → surface`; registry rows + schemas RESOLVE into the thing; device is just one axis. *Best part: the whole UI is compositional/data-driven; you add a face by declaring it, not hand-building a screen ([[feedback-resolution-first-compositional]]).*

### OWUI side — the product-grade chrome (from companion §10)
- **Product-grade chrome** — a polished, shipping chat shell: nav/sidebar, model picker, settings, workspace. The thing the Company surfaces are *not yet* (all in development).
- **Mobile PWA** — installable, mobile-first chat the Company has no shipped equivalent of.
- **Polished chat/channels/voice UX** — branching chat DAG (`owui-side-map §6`), Slack-style channels with AI-as-participant + streaming (§2), streaming sentence-split TTS + caching (§3). The *interaction feel* is product-grade.
- **The extension UI** — the rendered admin surface for Functions/Tools/Models/Valves; toggle chips in the chat bar; per-message Action buttons that emit rich UI (§1.4). The *visible* half of the extension model.

> The Company side is **richer substrate, unshipped**. The OWUI side is **shipped chrome, license-capped + fork-only frontend**. The fusion question is how those two faces relate — §2.

---

## 2 · THE FUSED OPTIONS (open — NO single destination)

> Given the verified constraint that OWUI's frontend is a compiled SvelteKit bundle (no `.svelte`
> source in the install) customizable WITHOUT a rebuild ONLY via `static/custom.css` + `static/loader.js`
> + `WEBUI_NAME`/banners/logo (`owui-side-map:194-202`), here are the REAL ways the two relate.
> Each is grounded in a verified mechanism. **None is recommended. The set is deliberately wider than
> a CSS-vs-fork binary** — there are several no-fork doors, and several "keep separate" shapes.

### Option A — Skin OWUI with Company DNA tokens [NO fork]
**Mechanism:** drop a `custom.css` into OWUI `static/` (`owui-side-map:198`); set `WEBUI_NAME`/logo/banners (`:199`). The Company `design/_system/tokens.json` → `emit.py` already produces a token stylesheet (`design-system.css`, 72 vars) — emit an OWUI-targeted variant and restyle OWUI's chrome to the ConceptV look.
**Reach:** colour, type, spacing, hide/restyle elements via CSS.
**Tradeoffs:** (+) zero fork, zero license exposure, single-token-source stays authoritative. (−) CSS can only RESTYLE the existing DOM — no new layout, no new routes, no Company surfaces; (−) brittle against OWUI's compiled class names (version-specific — a 0.9.x bump can break selectors); (−) it's OWUI wearing Company paint, not the Company's spatial surfaces.

### Option B — DOM-mount a Company surface INTO OWUI via `loader.js` [NO fork, deeper than A]
**Mechanism:** `static/loader.js` is arbitrary runtime JS loaded everywhere (`owui-side-map:198,202`). It can mount a Company surface (the DNA renderer is plain JS modules; the surface mounts as a **sibling overlay** by its own contract — `FACE-1-HOST-NAV-CONTRACT SEAM 1`) into OWUI's DOM, talking to the Company bridge directly.
**Reach:** a real Company face (a panel, an overlay, a board) living inside the OWUI shell, without forking.
**Tradeoffs:** (+) no fork/license exposure; (+) genuine Company surface, not just paint; (+) the overlay pattern is already how `GalleryMount`/`DecisionsInbox`/`ToolsPanel` mount. (−) it's an *injected overlay*, not a host-owned route — fragile to OWUI DOM/CSP/auth changes; (−) two state worlds coexist (OWUI's + the Company bridge's) — a seam to manage, not smooth away; (−) no control over OWUI's own pages/nav.

### Option C — Company surfaces as Action-rendered UI inside OWUI chat [limited, NO fork]
**Mechanism:** an **Action function** renders a per-message button; clicking it can return HTMLResponse/tuple → pushes an `embeds` event to the client (`owui-side-map §1.4`); `__event_call__` opens confirm/input prompts. A **Pipe/Manifold** puts a Company "model" in the picker (§1.2); a **Tool** (incl. MCP) makes Company capability model-callable (§1.5).
**Reach:** Company capability + small rendered widgets surface INSIDE OWUI's polished chat, through the sanctioned extension seam.
**Tradeoffs:** (+) the cleanest, most-supported door — uses OWUI exactly as designed; (+) inherits OWUI's chat/voice/mobile UX for free; (+) Company stays the backend brain via MCP/Pipe. (−) UI is confined to message-embeds + dialogs — no full spatial/canvas surface; (−) the plugin loader is no-sandbox `exec` (§1.0) — trust liability to inherit; (−) you get OWUI's *interaction model*, not the Company's projection model.

### Option D — Fork OWUI to host Company surfaces [license-capped]
**Mechanism:** fork the SvelteKit frontend, add routes/pages/components, host Company surfaces as first-class pages (the only way to touch layout/routing/nav — `owui-side-map:202`).
**Reach:** full control of the chrome AND the Company surfaces in one shipped app.
**Tradeoffs:** (+) one unified product; (+) keep OWUI's chat/channels/voice AND add Company spatial faces as real routes. (−) **license cap bites at scale** (§4) — stripping OWUI branding above 50 users/30 days needs an enterprise license; (−) a fork must track upstream (0.9.x moves fast — channels/voice are Beta); (−) maintaining a forked compiled frontend is the heaviest path; (−) risks re-creating a parallel frontend the Company spine ([[feedback-unions-not-bridges]]) is trying to avoid. *(Note: distinct from the Company's OWN internal "fork's read-API" in THE-FACE-ANCHOR — that is a Company-side bridge fork, not the OWUI frontend fork.)*

### Option E — Keep them as separate faces on ONE substrate [no merge of chrome]
**Mechanism:** OWUI and the Company surfaces both ride the SAME backend (Company bridge / MCP / channels), each rendered by its own frontend; the Company's "one system, many faces" already treats every surface as a projection of one entity (`THE-FACE-ANCHOR §1`). OWUI becomes one more *face* (the mobile/chat-product face) over the shared spine, alongside canvas + surface.
**Reach:** OWUI for shipped mobile/chat/voice; Company surfaces for spatial/projection/operator work; one brain + data underneath.
**Tradeoffs:** (+) no fork, no license exposure, no brittle injection; (+) each face plays to its strength; (+) consistent with islands-join-mainland — OWUI's good parts (chrome/PWA/voice UX) get built INTO the centre as a face, not bolted on. (−) two frontends to keep coherent; (−) the design-DNA must be expressed twice unless A-style token emission feeds OWUI too; (−) requires the Company spine to be the real backend OWUI talks to (work, not free).

> **The honest cross-cut:** A/B/C need no fork and no license risk but cede layout/routing to OWUI;
> D buys full control at a license + maintenance cost; E keeps faces separate over a shared brain.
> They are **not mutually exclusive** ([[feedback-both-plus-others]]) — A's token-emit feeds E; C's
> MCP/Pipe seam underlies B and E; a thin D could host what C can't render. The destination is Tim's
> call by recognition; this doc holds the space open.

---

## 3 · COMPANY-INTERNAL issues + proposed resolutions

### Issue 3.1 — Canvas vs Surface: duplication, or two faces?
**Observed:** Canvas (`canvas/`, tldraw board, :5173, "the surface Tim operates") and Surface (`surface/`, `instrument-surface`, :5174, "the instrument / projection-territory"). Both are React, both unshipped, both mount faces. On the face of it: two frontends.
**But:** `THE-FACE-ANCHOR §1` already frames them as projections of ONE entity on ONE spine (one host, one DNA renderer, one verb bus, one resolver). The live surface (`surface/`) is the one wired to DNA via `sync-gallery.mjs`; canvas is the tldraw spatial board.
**VERIFIED (this pass — the renderers are distinct):** `grep -riE "renderArchetype|archetype|dna|sync-gallery" canvas/app/src` → **zero matches**; canvas renders via tldraw custom shapes (`canvas/app/src/NodeShape.tsx`, `ForagerShape.tsx`) data-driven from `/object_info`. Surface renders via the DNA archetype renderer (`sync-gallery.mjs` pulls `counterpart/design`). And `canvas/app/package.json` has NO `sync-gallery` step (deps: react/tldraw only) while `surface/app/package.json` runs `sync-gallery` as predev/prebuild. → **Two distinct render pipelines confirmed, not one renderer with two faces.**
**Proposed resolution (grounded — a genuine convergence candidate):** this IS a real duplication-of-mechanism to converge, not two faces of one spine ([[feedback-unions-not-bridges]]). But the convergence is **not "delete one"** — the two play different roles: canvas = the **spatial/infinite-board** face (tldraw, generic `ai-node` from `/object_info`), surface = the **document/projection** face (DNA archetypes). The accumulate-into-the-centre move ([[feedback-islands-join-mainland]]): pick ONE renderer-spine (DNA is the live, drift-clean one per the convergence audit) and express the spatial board as an archetype/host of it — OR keep tldraw as the spatial substrate but route its node rendering AND surface's through one DNA archetype layer, so a node-type's look is defined once. **Which direction is a build call to confirm by tracing whether tldraw's `NodeShape` can host a DNA-archetype render — but the duplication itself is now confirmed, not hypothetical.**

### Issue 3.2 — "Two design systems" — actually THREE lineages, nested not parallel
**Observed (Verified):** the premise of "design/ vs claude-ds duplication" is partly false.
- `design/` = the synced corpus (tokens.json/register/addresses/mockups + FORM-gate machinery).
- `design/claude-ds` = nested INSIDE it — the ConceptV brand DS (CV_REGISTRY Types, axes, solvers, `_ds_bundle.js`).
- `/home/tim/repos/counterpart/design` (DNA) = a SEPARATE repo — the renderer the live surface actually pulls (`dna/*.json` + `surface/runtime/archetype.js`).
**The real tension:** `design/` (72-var token CSS + `ui://` addresses), `claude-ds` (axis/Type grammar + solvers), and DNA (`dna/layouts.json` archetypes + grammar invariants) are **three expressions of "compositional design"** with **no verified cross-reference** between them (grep found none linking claude-ds ↔ DNA repo). That's the duplication risk — three token/grammar homes.
**Proposed resolution (build on the ALREADY-DECIDED convergence):** the active `project-design-company-convergence` memory (2026-06-27) already establishes the **projection primitive** — *one registry entry, projected, becomes a page / a skill / a component* — and found the DNA system "mature + unusually drift-clean" (archetype catalogue actively de-duplicated 3 homes → 1). The resolution direction is therefore **NOT "pick one design system"** but **"make them projections of one registry, accumulate INTO the centre"** ([[feedback-islands-join-mainland]]):
  - DNA repo = the live renderer + archetype/grammar source (proven, drift-clean) → stays the rendering centre.
  - `design/` corpus = the addressed token/coverage/FORM-gate model → the queryable design-truth, feeds tokens INTO DNA + any OWUI skin (Option A).
  - `claude-ds` (CV_REGISTRY Type/axis grammar) = characterize-then-reconcile against DNA's grammar/molecules — the convergence memory flags the parallel claude.ai "Design System" projects similarly (one canonical `c8f43c46`, others to "characterize-then-merge later"). **Same move here:** verify whether claude-ds's axes/solvers and DNA's grammar/layouts are the same model under two names, then converge to one, regenerated not copied.
  - **#1 open question (from the convergence memory, SETTLE WITH TIM):** the narrative-guide vs instruction-unit sense of "skill" — not a fusion-faces blocker, but it gates the projection-primitive build that would unify the three.

### Issue 3.3 — design/ is a read-copy: the FORM gate edits canonical, never the repo copy
**Observed (Verified):** `design/README.md:8-17` — any token/look change happens in `build-prep/design/` then re-syncs; a hand-edit in `~/company/design/` is silently overwritten. **Proposed resolution:** any fusion work that emits an OWUI-targeted token CSS (Option A) MUST author at canonical `build-prep/design/_system/tokens.json` + `emit.py`, then sync — never hand-write a skin in the repo copy. (Stated so a builder doesn't desync the copy.)

---

## 4 · CONSTRAINTS (design boundaries, stated plainly)

1. **OWUI frontend is fork-only for anything structural.** The install is a compiled SvelteKit bundle (`open_webui/frontend/`, no `.svelte` source, no build toolchain). WITHOUT a fork you can only: `static/custom.css`, `static/loader.js`, `WEBUI_NAME`/banners/logo/favicon, signup/login toggles, and DB-row extensions (Functions/Tools/Models). **Layout, the chat UI itself, components, nav/sidebar, new pages/routes = fork-only** (`owui-side-map:194-202`). So `custom.css` + `loader.js` is the ONLY runtime door into the rendered UI.

2. **The license cap is on BRANDING-AT-SCALE, not on forking.** It is the "Open WebUI License" (BSD-3 + anti-branding clause 4). The BSD-3 core stays modifiable/redistributable — **you may fork freely**. What is prohibited above **50 end-users in any rolling 30-day window** (without prior written permission or an enterprise license) is **removing/replacing the "Open WebUI" name + logo** (`owui-side-map:204`). → A branded public-product fusion that strips OWUI branding at scale needs a paid enterprise license. *This cap, not any technical limit, is what gates Option D as a branded product.* (Stating "can't fork at scale" would be wrong — you can fork; you can't *rebrand* at scale.)

3. **OWUI's strong faces are Beta + version-specific.** Channels (the AI-as-participant differentiator) is docs-marked **Beta** with a public-channel security warning (`owui-side-map §2`); the signature-sniffed dunder contract + compiled class names are version-specific to 0.9.6 — a CSS skin (Option A) or a fork (Option D) inherits that drift surface.

4. **The plugin loader is no-sandbox `exec` (Option C inherits this).** Functions/Tools run as the server, unrestricted imports, `pip`-at-load (`owui-side-map §1.0`). Any Company capability surfaced as an OWUI Function is trust-equivalent to a server fork.

5. **Company side is all in development, nothing shipped.** Verified: nothing listens on 5173/5174. The "fusion" relates an UNSHIPPED richer substrate to a SHIPPED capped chrome — the asymmetry is real and shapes which option carries weight when.

---

## 5 · WHAT IS STILL OPEN (no closure)

- **3.1** — two renderers CONFIRMED distinct (canvas=tldraw, surface=DNA); open part is the *direction* of convergence (one spine hosts both? tldraw hosts DNA-archetype renders?) — a build call.
- **3.2** — are `claude-ds` (CV_REGISTRY/axes/solvers) and DNA (`dna/*.json` grammar/layouts) the same model under two names? Characterize-then-converge.
- **The skill narrative-guide ambiguity** (convergence memory #1) — gates the projection-primitive unification, SETTLE WITH TIM.
- **The destination** — A/B/C/D/E and their combinations are held open by design. Tim judges by recognition; this doc is the option-space, not the pick.
- **User-facing walks through Tim first** ([[feedback-user-facing-walks-through-tim]]) — any of these that lands a *face* in front of users is shaped by Tim before it ships; the reversible engine/token/skin work proceeds.
