---
type: synthesis-report
register: descriptive
aliases: ["interface architecture map", "③ mapping-wave synthesis"]
tags: [the-one-system, world-interface, mapping-wave, canvas, surface, projection, tldraw, useAppController]
status: unconfirmed
created: 2026-07-02
topic: "③ interface architecture map — synthesis of the 128 per-file maps against the WORLD-INTERFACE-CHARTER open questions"
sources: "interface-map/out/**/*.json (128 files, mapper: kimi-k2.7-code:cloud, 124 whole-file / 4 symbols+head)"
answers: "[[WORLD-INTERFACE-CHARTER]]"
---

# ③ Interface Architecture Map — mapping-wave synthesis

*Everything below is grounded in the 128 per-file maps under `interface-map/out/`. Each map was produced by a model reading the file; treat verdicts as **observed-in-map** (structural claims about code as read), not runtime-verified. Nothing here was tested at 76k points — where the maps can't answer, it says NEEDS-DESIGN-WAVE.*

---

## 1. The headline

**Zero `replace` verdicts. 120 of 128 `adapt`, 8 `keep`. 118 of 128 `substantial`.**

The wave confirms Tim's mandate empirically: this was never a pile of stubs — it is a substantially built system whose **semantics, contracts, and domain vocabulary survive**, and whose **forms (monoliths, render loops, component boundaries) uniformly do not**. Nothing is worthless; nothing is untouchable. "Adapt" everywhere means: the maps consistently name *what to keep* (contracts, seams, geometry concepts, token vocabularies) and *what to rebuild* (the component that holds it).

## 2. Aggregate tables

### Reuse × substance, overall (n = 128)

| | substantial | partial | placeholder | total |
|---|---|---|---|---|
| **adapt** | 112 | 8 | 0 | **120** |
| **keep** | 6 | 1 | 1 | **8** |
| **replace** | 0 | 0 | 0 | **0** |
| total | **118** | **9** | **1** | 128 |

### Per area

| area | n | reuse | substance | one-line verdict |
|---|---|---|---|---|
| `canvas/app/src` | 46 (9 root · 12 components · 24 regions · 1 ext) | 43 adapt / 3 keep | 44 subst / 2 partial | The operator IDE face — real, dense, monolithically held together by `useAppController` |
| `surface/app/src` | 67 (wheel 7 · toggles 16 · lib 8 · layouts 4 · +12 feature dirs) | 62 adapt / 5 keep | 59 subst / 7 partial / 1 placeholder | The projection instrument face — real, better-factored, responsive, token-disciplined |
| `surface/app/public/gallery` | 12 | 12 adapt | 12 subst | The DNA runtime — real domain logic trapped in IIFE/innerHTML vanilla-JS form |
| `runtime` (projection.py · scale.py · bridge.py) | 3 | 3 adapt | 3 subst | The engine is conceptually right and formally monolithic |

### The 8 `keep` files (everything else is `adapt`; nothing is `replace`)

| file | why |
|---|---|
| `surface/app/src/tokens/paper.css` | canonical token contract for the visual language — source of truth, cleanup not replacement |
| `surface/app/src/tokens/motion.ts` | single-source motion token layer |
| `surface/app/src/lib/api.ts` | typed, fail-loud data contracts (Projection, ProjPoint, Sector, ContextBundle, Territory) — central to the redesign |
| `canvas/app/src/components/kit.tsx` | token-only shared primitive library, already aligned with one-language direction |
| `canvas/app/src/components/NodeConfigForm.tsx` | schema-driven zero-per-node-type form — the intended architecture |
| `canvas/app/src/AppContext.ts` | minimal typed DI seam |
| `surface/app/src/main.tsx`, `vite-env.d.ts` | standard bootstrap |

### Recurring performance risks (491 statements across 120 files, clustered)

| cluster | statements / files | canonical instance |
|---|---|---|
| full redraw · no memoization · re-render churn | 148 / 91 | `useAppController`: one context, any state change re-renders the whole Hud tree |
| full-dataset shipping (no cap, unbounded, no pagination) | 31 / 27 | `LatticeView`: "no point-count cap or virtualization; large projections render every item every frame" |
| SSE/stream handling (refetch-on-poke, unbounded queues) | 30 / 24 | surface `App.tsx`: 2.5s pulse "can queue bursts of re-fetches"; `bridge.py`: unbounded voice queues |
| layout thrash / synchronous DOM work | 30 / 24 | `surface.js` split-pane pointermove sans rAF; `RightHand` setPos per pointermove |
| no virtualization | 25 / 25 | list/feed regions and both point renderers |
| SVG DOM node count | 24 / 18 | `Wheel.tsx`: framer-motion per point, no virtualization |
| animation/rAF per-frame recompute | 19 / 16 | `LatticeView.draw()` recomputes getComputedStyle + label collision (O(n²)) per frame |
| O(n)+ scans in hot paths | 15 / 14 | `projection.py` O(N·T) cosine scans; `scale.py` O(n³) agglomerate |

### Recurring interaction gaps (theme / mentions / files)

Missing everywhere, i.e. the interaction layer is close to greenfield:

- **error/empty/loading states — 156 mentions in 97 files** (the largest single gap in the codebase)
- **keyboard + accessibility — 140 / 91** (near-zero a11y anywhere)
- direct action (edit/create/dispatch/mint) — 93 / 57 (many verbs are "contract-only", shown as *soon*)
- live-update handling — 57 / 49 · zoom/pan gestures — 56 / 47 · selection/multi-select — 51 / 42
- hover/tooltip/detail — 30 / 27 · search/filter — 25 / 23 · request cancellation — 23 / 23
- URL/deep-link state — 15 / 13 · undo/history — 12 / 10 · provenance drill-down — 6 / 5

The charter's pointing-loop primitive (what are you · what powers you · where from · what near · what depends) exists **as event seams** (`projection:select`, `projection:aim`, `gallery:verb`, `ui://` addresses, `pointables`) but almost nowhere as finished interaction.

---

## 3. Charter answers (evidence-cited)

### (a) Projection geometry per scale — what LatticeView actually does, and 76k

`LatticeView.tsx` (canvas app, ~430 lines, **HTML canvas 2D — not tldraw**) fetches `/api/projection` with lens/time/centre/pole/rung/nucleation params, subscribes to `/api/stream`, and draws points, rings, dyadic grid, sectors, and labels. It already carries six lens modes (temporal now/day/week · semantic · separator two-pole · nucleation · connections chord · **scale ladder with unit-vs-coarse rungs and crossfade**) — so *rung-zoom exists as a UI concept*. The surface app renders the **same projection a second time** in `wheel/Wheel.tsx` as animated SVG (framer-motion per point).

**Would it survive 76k + rung-zoom? No, as-is — on four grounds from the maps:** (1) LatticeView: no point cap/virtualization, per-frame full recompute, O(n²) label collision; (2) Wheel: per-point motion components, multiple full passes over `proj.points` per render; (3) `projection.py`: O(N·T) cosine scans in the request thread, no caching of sectors/labels; (4) the surface app fetches limit 400–600 points — the current regime only works because nobody ships the full set.

**What the scale pyramid makes cheap:** `scale.py` persists cluster centroids as queryable vectors in `scale:<space>:k<K>` spaces with membership, exemplars, and cross-rung parent links — i.e., *server-side rung aggregation already exists as data*. The charter's "ship the rung the zoom resolves" is therefore implementable — **but the maps flag unfinished seams**: no zoom-stepping helper (next finer/coarser), no auto pyramid rebuild on corpus change, per-member `store.get_vector` round-trips, and the pure-Python O(n³) agglomerate "may already be too slow" at its 4000-unit threshold. Finishing these is a build prerequisite, not a design choice.

**Polar vs force/cluster vs hybrid per rung: NEEDS-DESIGN-WAVE.** The maps establish that the existing engine is polar-only (θ categorical, r by pluggable radius mode) and that its binding-driven-sector concept is right; they contain no evidence for or against force layouts at coarse rungs. Same for renderer substrate (canvas 2D vs SVG vs WebGL) — both existing renderers strain, neither was tested at scale.

### (b) tldraw — keep as substrate?

**tldraw appears in only 7 of 128 maps, all canvas-app, none of them the projection instrument.** It hosts the *node-graph editor* (custom `NodeShape`/`ForagerShape`, graph↔canvas sync, select/drag). The projection renderer (`LatticeView`) is a raw `<canvas>` overlaid on it; the surface app doesn't use tldraw at all. The maps also record a structural cost: `registryStore.ts` exists specifically because "components rendered inside tldraw cannot reach Hud-level React context" — a context-boundary workaround.

**Evidence-backed verdict: tldraw is not load-bearing for the world map / data instrument — the instrument already routes around it.** What tldraw genuinely provides is free-form spatial editing (drag, persistence, shape lifecycle) for the graph-editing face. Whether that face keeps tldraw or the world map absorbs graph-editing as one more lens: NEEDS-DESIGN-WAVE. But the design wave should treat tldraw as *optional for one workflow*, not the canvas substrate of the interface.

### (c) useAppController — what it holds, and the seams

The map calls it "a monolithic React context hook that centralizes all application state, editor bindings, API orchestration, and cross-cutting interaction handlers" — and, critically: **"the domain vocabulary, API contracts, and interaction rules are the authoritative source of truth, but the monolithic hook form must be decomposed."** It is the spec of the operator face, written as one hook. Its own map gives the decomposition — eight controllers:

1. **canvas/graph** — editor bindings, nodes, edges, runs, stuck nodes, fitGraph
2. **chat/proposal** — messages, streaming, proposals, threads, inbox offers
3. **voice/audio** — recorders, playback, barge-in, TTS/STT
4. **studio/review** — mockups, corpus, annotations, address help
5. **locus/history** — indicate, resolveUiTarget, journey, self-changes, versions *(this is ②'s pointing half — it must become shared, not canvas-private)*
6. **settings/config** — models, personas, modes, roles, voice config
7. **inbox/escalation**
8. **SSE/event dispatch** — mergeEvents as a dedicated stream controller

Perf grounding: single context ⇒ whole-consumer-tree re-renders; no memoized selectors; SSE merging runs per message; `App.tsx`'s map adds that Hud mounts every overlay unconditionally (mobile merely CSS-hides them). Companion monolith: `canvas/api.ts` — 70+ untyped (`any`) fetch wrappers that constitute **the canonical inventory of the backend surface** — same verdict, adapt by splitting transport / domain modules / streams. And `runtime/bridge.py` (~3,700 lines, ~100 routes) mirrors it server-side; its map lists a 13-module decomposition (transport · static · voice · streaming · cognition API · tool-face · projection math · workflow · graph API · lifecycle · ops · auth · gallery).

### (d) One interface or two?

**Evidence supports ONE — the charter instinct verifies.** The two apps are not two capabilities; they are two independent, partially-overlapping attempts at the same interface:

- **Both render the same `/api/projection`** — LatticeView (canvas 2D) and Wheel (SVG) are parallel implementations of one instrument, with the same lens vocabulary (semantic/separator/nucleation/scale appear on both sides: `wheel/Separator.tsx`, `wheel/Nucleation.tsx`, toggles `RungLadder`/`Lens` ↔ LatticeView's built-in pickers).
- **Both have a conversational brain** (canvas `RhmChat` + `ClaudeChat` vs surface `RightHand` + `fork-brain-core.js`) and **both have a pointing seam** (canvas indicate/`resolveUiTarget`/`ui://` vs surface `projection:select`/`projection:aim`/`pointables.ts` — and `lib/address.ts` is already "the central address-routing spine" on the surface side).

What each *uniquely* does — all of it component-shaped, none of it architecture-shaped: canvas uniquely has graph editing (tldraw), run control, inbox/decisions triage, voice circuit, settings/cognition config, review/walkthrough — the **act** face. Surface uniquely has the responsive form-factor system (Desktop/Portrait/Landscape layouts, `body[data-ff]`, modal allocation via `/api/resolve`), the paper.css token language, the DNA gallery/unit renderer, the draggable RHM handle — the **see** face. The merge: one world interface whose instrument core descends from the surface app's better-factored side, with the canvas app's operator verbs (run, triage, configure, review) as composed views/panels. Exact composition: NEEDS-DESIGN-WAVE (this is precisely the design wave's job).

### (e) The live-update seam (`/api/stream`)

**The seam is right; the protocol and the server under it are not.** Consumers (LatticeView, surface App, `operatorSession.ts`) all use `EventSource` — and every one implements the same pattern: *event arrives ⇒ throttled/debounced **full projection refetch*** (LatticeView 220ms debounce "but still fetches the full projection on each event burst"; surface App 2.5s pulse that "can queue bursts"). The stream is a doorbell, not a delta channel. Server side, `bridge.py`'s map: `ThreadingHTTPServer` thread-per-connection with no limits ("risking exhaustion under many concurrent long streams") and unbounded queues. At 76k units with rung-zoom, poke-then-refetch-everything cannot stand. Keep: SSE as transport, the event bus concept. Rebuild: scoped invalidation or rung-level deltas so a change re-fetches only the resolved rung/sector, plus a server that can hold many long streams. Delta granularity/protocol: NEEDS-DESIGN-WAVE.

### (f) Where the design language lives + component coverage

The maps find **three token dialects, not one**:

1. **surface `tokens/paper.css`** ("Fresh Paper") — **keep**, "the canonical token contract … source of truth", + `motion.ts` (keep).
2. **canvas `app.css` + `kit.tsx`** — maps corpus design tokens to app aliases; kit.tsx is keep but holds only **five primitives** (SectionHead, LaneHead, Badge, Surface, EmptyState).
3. **gallery `dna-tokens.css`** — a *generated* flat DNA token sheet; verdict: real vocabulary, rebuild via a proper token pipeline.

**`claude-ds` itself appears in zero of the 128 maps** — it was outside the mapped file set, so its component coverage for this instrument is **unverified here: NEEDS-DESIGN-WAVE** (the reconciliation the charter mandates — claude-ds canonical, three dialects folded in — needs a dedicated look at claude-ds's actual inventory). What the maps *do* establish about coverage: it is nowhere near sufficient — five kit primitives against 156 missing error/empty/loading states and 140 missing keyboard/a11y affordances means the state-and-interaction layer of the component system is essentially unbuilt.

### (g) What of LatticeView survives

From its own map — survives as concepts/contracts: the **projection-fetch + SSE subscription pattern**, the **lens state machine** (six server-parameterized modes), the **canvas geometry** (rings, dyadic grid, sectors, radius modes), and the **interaction inventory**: time scrubber, radial zoom, rung ladder with crossfade, pole picking, semantic re-centre, point-pick card, working-set → builder handoff. Dies with the form: the monolithic component, the per-frame recompute `draw()`, O(n²) label layout, unbounded point rendering, closure-recreated draw callbacks. Its map's decomposition is a ready skeleton for the new instrument: `useProjection` hook (fetch/SSE/retry) · lens-specific render layers sharing a geometry module · overlay components · animation/tween hook · working-set store · off-thread label collision.

---

## 4. What the design wave inherits

### Constraints (evidence-backed, binding)

1. **The contracts survive.** `surface/lib/api.ts` types (keep-verdict), `canvas/api.ts`'s 70+ endpoint inventory, `projection.py`'s binding/lens registry semantics, and the event seams (`projection:select/aim`, `gallery:verb`, `ui://` addresses, `pointables`, `forkVBrain.attach`) are the vocabulary the new interface is written in. Adapt their form (typing, cancellation, caching, modularity), never their meaning.
2. **Zoom = scale is the only perf story that works.** Never ship the full set; fetch the rung the zoom resolves. Precondition: finish `scale.py`'s seams (zoom-stepping helper, auto-rebuild on corpus change, batch vector fetch, scalable agglomeration) and move `projection.py`'s O(N·T) math out of request threads / behind caches.
3. **The live seam stays SSE-shaped but the payload changes** — scoped invalidation/deltas instead of poke-then-full-refetch, on a server that can hold many long streams (bridge decomposition).
4. **One token language.** paper.css + motion.ts are the in-app keeps; the three dialects reconcile under claude-ds per the charter — through a token pipeline, not another hand-written sheet.
5. **Render discipline is non-negotiable**: the #1 cluster (148 re-render/no-memo risks in 91 files) is the systemic disease. Narrow contexts, memoized selectors, virtualization, capped/rung-scoped datasets — everywhere.
6. **Laws already in the code stay laws**: meaning-in-data-not-instrument (projection.py), fail-loud (surface api.ts, scale.py guards), operator-law humanization, verify-mode write suppression.

### Freedoms (equally evidence-backed)

1. **Zero `replace` — and zero owed to any form.** Every component boundary, render loop, DOM structure, and file split is rebuildable; 120 adapt verdicts each name what to keep, which is never the component itself.
2. **tldraw is optional.** The data instrument already lives outside it; only the graph-editing workflow would miss it.
3. **The two apps are mergeable** — every unique capability is a component, none is an architecture.
4. **The decompositions are pre-mapped.** useAppController (8 controllers), bridge.py (13 modules), LatticeView (7 pieces), projection.py (6 modules), api.ts, surface App.tsx, RightHand, fork-brain-core — the seam lists are in `out/`, per file.
5. **The interaction layer is greenfield.** Keyboard, hover, URL state, undo, search, drill-down, error/empty/loading — near-nothing exists, so nothing constrains; the pointing loop can be designed whole rather than retrofitted.

### Explicitly NEEDS-DESIGN-WAVE (the maps cannot answer)

- Projection geometry per rung (polar vs force/cluster vs hybrid) and the renderer substrate (canvas 2D / SVG / WebGL) at 76k.
- The merge shape of the one interface (what the world map absorbs vs hosts as panels; whether graph editing keeps tldraw).
- The live-delta protocol (granularity, invalidation keys).
- claude-ds reconciliation specifics and its real component inventory (not in the mapped set).
