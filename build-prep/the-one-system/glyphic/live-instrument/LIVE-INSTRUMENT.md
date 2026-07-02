# Conversational Glyphgraph — Unification Map + Grounded Build Direction

> Synthesis of a 3-wave, 20-area research wave (`findings/AREA-1…20-*.md`; read those for full
> evidence). This **supersedes** the earlier "Live-Instrument Layer — grounded build plan" written from
> the first 7 areas. That earlier draft was wrong in *framing*: it sorted every capability into
> `REUSE / EXTEND / BUILD / DECISION` verdicts and recommended winners ("reuse the tldraw pattern", "use
> the served 4B"). **This document holds the opposite stance**, stated up front as the lens.

---

## The lens (the governing reframe — non-negotiable, stated first)

1. **Nothing is final, canonical, done, or in-use.** "It exists / it's built / acceptance-verified" is a
   *structural fact about one version*, never a verdict that it is the design or that the work is over. No
   one knows what still must be built. Treating anything as settled, or adopting "one-or-the-other", fails.
2. **Duplications are expected, many, and valuable.** The job — half of it or more — is to **find every
   version of each capability and fuse the best parts of all into one.** Never pick a winner. The wave found
   the system is *full* of parallel versions (three conversation surfaces, three Vi-mark drawers, three
   node-bodies, two token systems, two data→visual binding registries, four-plus graph render substrates,
   five-plus places `'claude'` is pinned). Each duplicate is fusion raw material, catalogued by its **unique
   quality**, never by which one "wins."
3. **Many things are ALREADY the glyphgraph primitive under another name.** Recognising these unnamed
   instances is the richest fusion source — they have their own §.
4. **One IR law.** There is one `CVGraph` IR (`core/cv-nodes.d.ts`). Any surface — reactflow, tldraw, the
   SVG solver, the `.spatial` scaffold — is a **projection** of it, never a parallel render strand with its
   own node model. (Anchored on `UNIFICATION.md §4`'s recorded "fourth parallel strand" mistake.)
5. **Deep-linked / single-source everywhere, incl. STORAGE.** A stored glyphic *references* its
   type/facets/meaning/sockets — never copies — so growth never stales. Colour resolves
   `CV_AXES → var(--token)`, never hex. Loud-fail (unknown → throw; absent → silent-OK is wrong, surface a
   Notice + record a Gap). Render-from-data, no per-type branch.
6. **Unify INTO the Company.** design↔Company is a SEAM, not a wall. The tokens/model flow *into* the
   Company centre; touching `~/company` (with care) is part of the convergence, not forbidden.
7. **A glyphgraph node is a FULL typed glyphic** — slots / sockets / triggers / values / tags / state /
   click-actions per `app/registry/glyphic-type.js` — **not a bare triple.**
8. **mode / app / panel is NON-EXCLUSIVE.** A glyphgraph can be a MODE (with loadouts), an APP bound to a
   mode, AND/OR a modular PANEL/iframe in the RHM's surface. Hold all three; force none.

**Evidence is marked** Observed(file:line) where read directly · Inferred · Cross-area where one area's
finding is confirmed/extended by another.

---

## Headline

The conversational glyphgraph is **realtime natural-language → a living glyphgraph: you talk and watch a
graph get BUILT, DESCRIBED, EXPLAINED, and corrected/extended — by Tim's transcribed voice and the AI
together.** Across 20 areas the wave found that **almost every part of this exists in some form, often in
several forms** — and that *this is the finding, not a reason to declare it done.* The work is to **fuse the
many versions of each capability into one**, hold the one-IR law so no surface forks a parallel graph, and
build the genuinely-thin missing parts: the **transcript fan-out wire**, the **role-resolution layer over
the model pins**, the **incremental-stable placer**, a **semantic icon index**, and the **integrated
voice-corrected loop** that closes BUILD → DESCRIBE → EXPLAIN → correct/extend. The loop is the frontier; its
parts are all enacted somewhere already.

---

## The pipeline — LISTEN → EXTRACT → RESOLVE → generate-on-miss → PLACE → RENDER → NARRATE → LOOP

Each stage: the versions/precedents that exist (file:line), the honest gap, the fusion direction. **The loop
is BUILD + DESCRIBE + EXPLAIN + correct/extend — not just "correct."**

### LISTEN — speech in
- **Versions found:** A complete headless-verified live-speech circuit exists Company-side — **8 STT ears**
  in a swappable registry (`voice/stt.py:68-119`; Moonshine the everyday 0-VRAM ear; `parakeet-onnx` has
  hotword/context biasing), VAD endpointing (Silero headless + browser RMS), a **role-resolved semantic
  finished-thought judge** (`suite.py:6544-6586`, the `judge` role — measured: a reasoner is unusable per
  pause, so it must be a fast no-think model), push-to-talk + auto-listen + barge-in (`useAppController.ts`),
  all swappable by config slot. [A3 Observed]. The design-system browser app has **no STT at all** — its
  "Voice" canvas is brand-copy tone, not audio (`canvases/Voice.jsx`) [A10/A11/A16 Observed, corrects a
  naive read].
- **Honest gap:** the ears are **batch ASR, not streaming** — "live" = utterance-chunked turns per
  finished-thought, not per-token. There is no browser-native STT; speech is Company-side. [A3]
- **Fusion direction:** reuse the whole capture/VAD/judge machinery; voice feeds the **same message stream**
  a typed turn does (a transcribed turn is just a `Message from:'user'`). The extract roles inherit the
  judge's measured "fast no-think model on the hot path" constraint. [A3, Cross-area A17]

### EXTRACT — concurrent small models turn talk into structure
- **Versions found:** (i) **`run_swarm`** fires a wave of role files concurrently via a ThreadPoolExecutor,
  `SlotBudget.from_registry` deriving the concurrency knee from live `services.json` (never a literal 32);
  `think=False` took a one-word answer 1304→43 tokens (~30×); schema-constrained decode is real (vLLM guided
  decode, fail-loud use-gate) (`cognition.py:1413, 976-1040, 490-515`) [A2 Observed]. (ii) The **in-browser
  Build canvas** already does plan→2-4 parallel specialist subtasks→one composer — extraction-vs-judgment in
  the browser (`Build.jsx:43-152`) [A10]. (iii) **`generateCandidatesStream`** fires N parallel single-shot
  calls with `onCandidate` incremental arrival (`AIEngine.jsx:1413-1459`) [A16]. (iv) **ViConsole** returns
  structured `{say, actions, proposals, options}` from one turn (`vi-brain.js:132`) [A9/A17]. (v)
  **`CV_TYPES_VI.proposeType`** — AI returns a registry-validated structured spec (`types-vi.js:109`) [A13].
  (vi) Prior art: GraphRAG / LangChain `LLMGraphTransformer` / **REBEL (~400M)** / Graphiti — schema-guided
  triple extraction, "split extract from judge" *is independently the field's answer to Tim's
  extraction-vs-judgment law* [A7-B4].
- **Honest gap:** the realistic operating point is **a burst of ~10-14 short, think-off, schema-constrained
  roles at each pause** — NOT an always-on fleet running concurrently with a long voice reply (the brain-KV is
  shared with the main reply; the knee collapses to ~1-5 mid-deep-reply). Per-utterance bursts, vLLM
  continuous-batches them. [A2 — the key correction to "always-on swarm"]
- **Fusion direction:** extract concerns (entities / relations / states / placement-hints) are **role files**
  (`roles/glyph_*.py`) modelled on `judge`; a strong `glyph_compose` role JUDGES. The browser fan-out idioms
  (Build, `generateCandidatesStream`, ViConsole's interpret-spine, `proposeType`) are the same shape — fuse
  toward one `CV_AI.execute()`-driven structured-output path that resolves to Company roles. Triples may be the
  *extract wire-format* (A7-B4), but the stored/rendered unit stays a full typed glyphic (lens 7).

### RESOLVE — each thing → a full typed glyphic (NOT a flat noun→icon)
- **Versions found:** the glyph engine is built and single-sourced — `CV_GLYPHIC.compose/render`, the 9
  `CV_AXES` (color/space/size/motion/texture/depth/fill/form/symbol) with `register/resolve/candidates/
  validate`, `CV_MEANING` loadable profiles, `CV_COND` the condition evaluator, `CV_REGISTRY.accepts /
  candidatesForSocket`, and `CV_GLYPHGRAPH.validateGlyphgraph` (reuses `accepts`+`CV_COND`, collect-then-throw)
  [A11/A12/A13/A19 Observed]. `kind.graph` is **already a declared Type** (`nodes` accepts glyphic/atom/block,
  `edges` accepts relationship, a `layout` value-slot, `runtime:{kind:'engine',key:'DiagramSolver'}`) — the
  live canvas is *a new runtime for an existing kind*, not a new kind [A13:2.3].
- **Honest gap:** RESOLVE is **combinatorial/field meaning** — "meaning is the combination of facet values,
  not each facet alone" (`LANGUAGE.md:8-12`, Tim). **Semantic icon-lookup is ONLY the SYMBOL leg.** Form (kind),
  fill/outline (mode), colour (state), texture (material), edges (relations) resolve through `CV_MEANING`'s
  grammar from the extracted facets, context-resolved by the active profile. A flat noun→glyph lookup is "a
  lookup, not a language." [A11:C1]
- **Fusion direction:** RESOLVE = compose facets via `CV_AXES.css → var(--token)` + `CV_AXES.validate/
  candidates` (the loud-fail vocabulary gate; give the LLM `candidates(sub)` as its closed enum), validated by
  `CV_GLYPHGRAPH.validateGlyphgraph` before render. [A11/A12/A15/A19]

### GENERATE-ON-MISS — draw a new icon live when none is close
- **Versions found:** the **foundry** is built — `glyphic.generate` (LLM → candidate SYMBOL records, threaded,
  validated) + `glyphic.save` (`CV_ICONS.add`, instant) (`ai-glyphic.js:59,72`); a **conversational foundry UI**
  (`system/glyphic-foundry.html`) propose→feedback→click→save, candidates live-render as glyphics, save rebuilds
  the symbol axis (`CV_AXES.resolve('symbol').rebuild()`) so a new icon is instantly resolvable [A4/A11/A14
  Observed]. `CV_SCAN` is a continuously-rebuilt `f(sources × extractors)` index — the literal re-runnable-index
  pattern (`scan-engine.js:6-9, 181`) [A9/A20].
- **Honest gap:** there is **no semantic icon-lookup** to *trigger* a miss — lookup today is lexical
  `String.includes` (`cv-icons.js:430`); there is **no embedder reachable from the design system**, no cosine
  index. Generation is unconditional (human clicks), not miss-triggered [A4/A5 Observed]. The icon tags are
  hand-typed literals — the §5 "embed→derive re-runnable pass" is **violated by construction today**, and 131
  built-in facets carry no `name`/`description`, only tags+domain+kind+id [A4 corrects the anchor's
  "under-tagged" + "ICON-AUDIT.md" — both stale].
- **Fusion direction:** add a re-runnable **embed index keyed by icon id, deep-linked to `CV_ICONS.facets`
  (never copied)**, re-run on `CV_ICONS.add` (the `symbol.rebuild()` discipline) — this *also fixes the live
  hand-typed-tag staleness*; a **tuned (not guessed) threshold** gates generate-on-miss; keep lexical search as
  the deterministic floor (both-plus-others). The embedder enters as a role-resolved provider (see map). [A4/A5/
  A12/A9]

### PLACE — incremental, stable layout as nodes arrive
- **Versions found:** `DiagramSolver.glyphGraphView` already lays out + renders + narrates a glyphgraph; its
  `layout()` has an **authored-x/y branch** (honour frozen coords) + an auto branch (DAG-layering / ring), "no
  external layout lib (CSP/bundle)" (`DiagramSolver.jsx:63-100, 279-351`) [A11/A12/A19 Observed]. `canvas/app`
  (Company, tldraw) owns positions backend-side ("never invent coordinates", "reflect-never-own") with FLIP-style
  transitions [A6/A14]. `tokens/canvas.css` is a **`.spatial-*` pan/zoom plane** with "programmatic moves glide,
  drag is 1:1" already wired (`canvas.css:50-58`) [A15]. `FloorplanOverlay` is percent-positioned nodes with an
  active-dot pulse [A18]. System-map does **FLIP-morph incremental relayout** ("authoritative & instant") [A11/A14].
  Prior art: **cola.js/WebCola seed-then-relax + position-seeding + pinning**; dagre/elk install fine under Vite
  [A6/A7-B6].
- **Honest gap:** the existing auto layout **re-ranks every render** — a new node can change an existing node's
  longest-path rank → it moves → the graph jumps. The static render does **not** solve the live incremental case.
  [A19:3-A — traced exactly]
- **Fusion direction:** an **incremental placer** assigns + **freezes** x/y per node as it arrives (seed near its
  relation, relax locally with placed nodes pinned), then render through the **authored-x/y branch unchanged**; a
  drag writes a new frozen x/y (override, not a styled literal). Pipeline/backend owns positions; the FE reflects.
  cola/dagre/elk are a "tidy" affordance, not the live path. [A19/A6/A12]

### RENDER — the node is a full glyphic; the surface is a projection of the one IR
- **Versions found:** (i) `glyphGraphView` — the only **glyphic-native** render today; nodes are full glyphics,
  edges carry meaning by sight (line=mood, colour=state via `CV_MEANING.field('lineColor')→token→var`), labels
  off by default [A12/A14/A19]. (ii) `canvas/app` tldraw (Company) — rich interaction (drag/zoom/ports/edges),
  but renders a generic *card*, not a glyphic (`NodeShape.tsx`); "ports from the registry → new node-type with
  zero per-type code" [A6/A14]. (iii) reactflow — **absent from both repos** (verified); a forward choice, not a
  fact [A6/A16]. (iv) the `.spatial` scaffold (token-pure, CSP-clean) [A15]. (v) `brand_process_flow` — a built
  static node+edge+label-pill+⊕-join visual grammar = the **style contract** any live edge should match [A20].
  `Glyphic.jsx` is the React socket around the one `CV_GLYPHIC.compose` (incl. an edge path) — never write a
  second drawer [A13:1.3].
- **Honest gap:** which substrate is partly an open decision (below) — but the **highest-risk failure is the
  "fifth parallel strand"**: a surface that holds its own node model instead of projecting the one `CVGraph` IR.
  `UNIFICATION.md §4` records this exact past mistake. [A19:C1 — make loud]
- **Fusion direction:** one generic node-type + one generic edge-type, **render-from-data via `CV_GLYPHIC.render`
  / `glyphGraphView`'s node logic**; edges resolve facets/colour through `CV_EDGES`/`CV_MEANING`/`CV_AXES`, never
  a surface-side style map; positions resolved not invented. Server-composes-glyph (FE reflects a resolved SVG
  string) keeps the FE holding zero compositor logic (the canvas/app law) — Fork B as spine, Fork A (FE imports
  the compositor) optional later. [A6/A11/A12/A19/A20]

### NARRATE — the graph speaks itself (DESCRIBE + EXPLAIN)
- **Versions found:** the **sentence is composed in the design system** — `CV_MEANING.readGraph` / `describe` /
  `describeRelation` (used live in `language.html`, `DiagramSolver` per-edge `<title>`); read-out **already does
  negation + conditionals** ("is NOT the face of", "if … then …" via `CV_COND`) [A11/A14/A19 Observed]. The
  **speaking** is fully built + universal — `POST /api/say` (server host-speaker queue), `/api/tts`, the
  `speakable` transform that cleans any text for any engine; TTS engines are a registry [A3 Observed].
- **Honest gap:** **sentence-coverage is a known-open tuning surface** — the auto-focus walk can drop a clause
  from the SENTENCE though the PICTURE shows all relations (`FINDINGS-LOG.md:42`, flagged FORM/Tim, not green)
  [A19:3-D]. NARRATE is a **two-part seam** (design composes words → Company speaks) the two halves must connect.
- **Fusion direction:** the read-out is the **DESCRIBE** half — narration generated from the SAME graph object,
  single-sourced; closing sentence-coverage is in-scope (no-deferral); routing/arrowhead taste walks through Tim;
  narration could be a third consumer of the same event bus. **EXPLAIN** — interrogating the graph ("why is the
  buyer cold? what depends on this node?"), distinct from the read-out's DESCRIBE — is the conversation-surface /
  RHM Q&A route (ChatRail's plain-chat path + `brain_router`'s `model` leg over the live graph context), the
  fourth verb of the loop. [A11/A14/A19/A3 + A8/A10/A17]

### LOOP — BUILD + DESCRIBE + EXPLAIN + correct/extend, by voice and AI together
- **Versions found:** a **non-voice, non-graph skeleton of exactly this loop already runs** in AtomiCity:
  interpret → action-protocol → override-stick → shot-capture → vision.diff → learn-folds-back (`ViConsole.jsx`,
  `vi-brain.js`) [A9 — the prize correction to the old synthesis's "no prior art"]. The Workshop **BRIDGE +
  WSDiffCard** propose→typed-batch-diff→apply/discard with `invertDiff` undo is the talk→surface-mutates shell
  (`AIEngine.jsx:813-843, 48-129`) [A10/A16]. System-map's **typed op-queue** (one code path per op, staleness
  guard, FLIP reflow) is the operator-mutates→backend-owns-truth pattern [A11/A14/A19]. The mode **`consent`**
  axis governs whether the AI acts vs surfaces (`suite.py:6986`) [A8].
- **Honest gap:** the **integrated, voice-corrected, realtime** version is genuinely new — but as *integration of
  enacted parts*, not invention. ChatRail's diff path is single-shot request→propose→apply; the live loop wants
  a continuous extract-as-you-speak stream [A16]. AtomiCity's `vision.diff` self-check throws in the sandbox (no
  vision provider) but closes on the Company side [A9].
- **Fusion direction:** a voice correction ("no, the buyer's gone cold") is a **typed graph-mutation op**
  (`setState`/`addNode`/`addEdge`/`relate`/`place`/`narrate`) on the in-memory `CVGraph`, applied through one
  code path per op with FLIP reflow — the state-morph the engine already animates; human edits and pipeline edits
  append to one op-queue against one model (two-way authoring). Conditionals/negation already exist in the read-out
  grammar — voice maps to existing markers, doesn't invent syntax. [A19/A9/A10/A14]

---

## The unification map — per capability: every version · its unique quality · the fused direction

This is the core. **No verdicts, no winners.** Each capability lists every version found (file:line), the
unique quality that fusion must keep, and the fused best-of-all direction.

### 1 · Provider / model-resolution
| Version (file:line) | Unique quality | |
|---|---|---|
| `CV_AI` registry — 6 provider records, `runtime.kind` dispatch, `resolveProvider` delegates unknown kinds to `CV_HOST.resolveProviderRuntime` (`ai-registry.js:198-238`; `ai-seed.js:21-43`) [A1] | The multi-provider *plumbing* + the delegation **seam** for kinds `CV_AI` can't itself reach | |
| `CV_HOST` — the **fifth registry**: runtimes `review`/`fsapi`/`native`, `capability-available=f(env,runtime)`, `commit`+serializers (`host-runtime.js:67-309`; `DESIGN-LANGUAGE.md:97`) [A11] | "Add a way to reach the world = register a runtime, not edit every caller" | |
| Company `run_role`/`models_for_role` — capability-resolved role→model; resident-brain sentinel follows the live loadout; `resolve_model` unified entry **built but dormant**, with the `satisfied` FLOOR trap (a role silently floors to the resident 4B) (`cognition.py:303,391-396`; `model_routing.py:13-81`) [A2/A8] | True role-resolution + the loud honest-status flag (`satisfied`, not truthiness) | |
| **The `'claude'` pins** (the dead-pin fuse material — all sites): `ai-registry.js:315,343`; `ai-glyphic.js:61`; ~27 canvas caps (`ai-capabilities-canvas.js:84`); `deck.titlechain:105`; `vi-brain.js:291,298`; `explore-engine.js:129,137`; `VoiceSurface.jsx:19`; AIEngine **dead `typeof provider` guard** (~16 sites, always falls to claude); foundry `window.claude` liveness check (`glyphic-foundry.html:124`) [A1/A5/A9/A10/A14/A16 Observed] | Each is a place the *resolution* (not the registry) pins a single model — the staleness to dissolve | |
| `window.claude` itself — an **ambient sandbox-host global defined nowhere in-repo** (`ai-registry.js:204-211`) [A1] | A standalone/exported tab has no text model at all today → argues for the Company bridge as the real text engine | |

**Fused direction:** a **role-resolution layer** in `CV_AI` — capabilities declare a *role*
(`extract-entities`, `compose-graph`, `embed`, `text`), one `ROLE_PROVIDERS` config maps role→provider id, the
single place an id is pinned. `execute()`'s line 299 + the two fallbacks route through it; the ~27 caps drop
`provider:'claude'`. Flipping the whole DS to Company-local = one edit. The Company fleet enters as a
`company-http` runtime (modelled on `openai.js` direct-fetch) hitting the bridge `/api/cognition/run_role`
(role-resolved, json_schema structured outputs) — **NOT** the `CV_HOST_NATIVE` export path (vaporware, never
injected). The dead `typeof provider` guard and the foundry `window.claude` check become
`CV_AI.resolveProvider`-based. Assert `satisfied`. This realises `cognition-is-role-resolved` in `CV_AI`,
mirroring `run_role`/`models_for_role`. The single open fact: whether bridge `:8770` sends cross-origin CORS
(or the surface is served same-origin). [A1/A5/A8/A11/A16]

### 2 · The extract layer
| Version (file:line) | Unique quality |
|---|---|
| `run_swarm` + `SlotBudget.from_registry`, `think=False`, schema-constrained decode + fail-loud use-gate (`cognition.py:1413,976-1040,490-515`) [A2] | True concurrent role-dispatch on the live fleet, with the resource knee computed from `services.json`, not guessed |
| `Build.jsx` plan→2-4 parallel specialist subtasks→one composer (`Build.jsx:43-152`) [A10] | Extraction-vs-judgment **already running in-browser**, with triage-driven refinement |
| `generateCandidatesStream` — N parallel single-shot, `onCandidate` incremental arrival (`AIEngine.jsx:1413-1459`) [A16] | The "nodes arrive incrementally" UI precedent |
| `ViConsole`/`vi-brain.interpret` → `{say,actions,proposals,options}` (`vi-brain.js:132`) [A9/A17] | Structured-output-from-an-utterance that **auto-acts on the surface** |
| `CV_TYPES_VI.proposeType` — AI returns a registry-validated spec, fed a compact live catalogue (`types-vi.js:61,109`) [A13] | The "AI authors the living surface, validated against the registry" idiom |
| Prior art: GraphRAG, LangChain `LLMGraphTransformer`, **REBEL (~400M)**, Graphiti; MeetMap staged-reveal [A7-B4/B5] | Schema-guided triple extraction + "split extract from judge" = the field's own answer to Tim's law; staged-reveal makes it *feel* live |

**Fused direction:** extract concerns are **role files** (`roles/glyph_entities|relations|states|placement.py`)
modelled on `judge` (`thinking:False`, schema-constrained, short-context), fired in **bursts at pauses** via
`run_swarm`; a strong `roles/glyph_compose.py` JUDGES the wave into one graph delta. The browser fan-out idioms
(Build, `generateCandidatesStream`, ViConsole, `proposeType`) converge on one `CV_AI.execute()` structured-output
path resolving to those roles. Staged-reveal: place the node the instant an utterance resolves, infer relations
async. [A2/A8/A10/A16/A7]

### 3 · The conversation surface
| Version (file:line) | Unique quality |
|---|---|
| `app/components/ChatRail.jsx` [A10/A16/A17] | The **production-wired** rail: real `CV_AI.complete`, intent-routing (image / workshop-edit-diff / Q&A), apply/discard inline proposals |
| `ui_kits/vi/ChatPanel.jsx` [A13/A17/A18] | The pipeline-stage **card vocabulary**: `ReadCard` (extraction-in-progress), `MissingPrompt` (resolve-on-miss gap-fill), `ApproveCard` (confirm-before-mutate) |
| `atomicity/ViConsole.jsx` [A9/A17 — net-new prize] | The **act-on-the-surface** spine: structured interpret → auto-run actions → before/after diff → element-selection → Teach/learn fold-back |
| Workshop BRIDGE + WS_AI (`AIEngine.jsx:813-843`) [A10/A16] | `setActive(doc,save,ctx)` + `CV_AI.setActiveSurface` (context auto-resolves), `applyDiff`/`invertDiff` typed-batch + undo |
| Company `surface/app` RhmChat / `canvas/app` (Company repo) [A14] | The server-side operator console + RHM/walkthrough organ tailing `/api/stream` — the 4th surface (cross-repo seam) |
| The 3 `ui_kits/` + the two-bridge split (CV_AI vs WS_AI) [A16/A18] | Three layout grammars (vi 3-pane · platform dashboard · virtual-hub canvas-first) on one shared token base |

**Fused direction:** **one conversation surface** = ViConsole's act-on-surface interpret-spine + ChatRail's real
provider/intent-routing + ChatPanel's stage cards, through **one message-kind renderer**, built on the 11
token-class components (`Input`/`Button`/`Segmented`) + a new `.cv-feed` list primitive (three surfaces hand-roll
`scrollTop`), with **`<Glyphic/>` entity icons** (killing ChatPanel's emoji). The three originals retire into it;
voice feeds the same message stream. Everything routes through `CV_AI.execute()` (one bridge, not WS_AI vs CV_AI).
Cross-repo: it must send transcribed-intent to / receive graph-deltas from the Company surface, not be a closed
browser-only chat. [A17/A10/A16/A14/A18]

### 4 · The canvas / renderer
| Version (file:line) | Unique quality |
|---|---|
| `DiagramSolver.glyphGraphView` (`DiagramSolver.jsx:279-351`) [A11/A12/A14/A19] | The **only glyphic-native** render — nodes are full glyphics, edges carry meaning by sight, **reads itself out** via `readGraph`; token-pure, CSP-clean, no external lib; **static / light interaction** |
| `~/company/canvas/app` — tldraw 3.13.1 (Company repo, verified) [A6/A14] | Rich interaction (drag/zoom/ports/edges/SSE), backend-owns-positions, "ports from the registry → zero per-type code"; renders a generic *card*, not a glyphic |
| reactflow / @xyflow — **absent from both repos** (verified grep) [A6/A16] | First-class typed edges + dagre/elk ecosystem; a forward choice to introduce, not an existing fact |
| `tokens/canvas.css` `.spatial-*` plane (`canvas.css:24-58`) [A15] | A token-pure, CSP-clean pan/zoom scaffold with "programmatic glides, drag 1:1" already wired |
| `system/system-map.html` + op-queue [A11/A14/A19] | A working interactive graph canvas at scale: layout registry, FLIP-morph relayout, drag-reparent, undo/redo, **typed edit-op queue → adapter → rescan** |
| `FloorplanOverlay` / `brand_process_flow` [A18/A20] | A latent node-on-canvas (percent nodes + active-dot pulse + pick); a built static node+edge+label-pill+⊕-join **style contract** |

**Fused direction (a multi-way decision on MECHANICAL FIT, not "pick a library"):** all are projections of the
one `CVGraph` IR — the choice is which interaction substrate best fits the real needs (ports + click-actions per
`glyphic-type.js` + state + a programmatic store + the existing tokens/`canvas.css` scaffold), and **whichever
wins renders nodes via `CV_GLYPHIC.render` and resolves edges/colour through the registries.** The candidates:
glyphics-inside-tldraw (reuse the canvas/app console + NodeShape, gain interaction; cross-repo) · an
interaction-layer over `glyphGraphView` (keep the auto read-out for free) · the `.spatial` scaffold (zero
bundle, CSP-clean) · reactflow introduced in a Vite app. The hard law governing all of them is the **one-IR /
no-fifth-strand** rule. The static `glyphGraphView` stays the page-face render AND a projection target, so the
heavy interactive surface serializes frozen x/y back to the same IR. [A6/A11/A12/A14/A15/A19/A20]

### 5 · Tokens + axes
| Version (file:line) | Unique quality |
|---|---|
| **System α — `claude-ds/`**: L0→L1→L2 `color-mix`-derived roles + the `data-*` knob layer (`--density`, `data-theme`, `data-ground`, `--cv-scale`) + the typed `CV_AXES` validation layer — **hand-authored CSS, no `_system/`, no emit, no GENERATED header** (verified) [A12/A15] | The **richer MODEL**: derived roles, runtime knobs, the axis `candidates`/`validate` loud-fail gate |
| **System β — `~/company/design/_system/tokens.json → emit.py → design-system.css`** [A15] | **Real machine single-source + generation** + the `check.py`/`refcheck`/`code://`/`mechanisms.json` governance; carries the **dated `GOLD-PRIMARY WARM THEME` palette (Tim, 2026-06-07)** |
| `CV_AXES` — registry-of-axes, `css(axis,value)→var(--token)`, `symbol.rebuild()` live (`axis-core.js:134-161`; `symbol-axis.js:31-43`) [A12/A15] | "tokens ARE the value-units of an axis"; the generate-on-miss no-staleness pattern |

**Fused direction:** lift α's MODEL (derived roles via a `mix:{toward,pct}` recipe + the knob layer + the typed
`CV_AXES` view with `candidates`/`validate`) INTO β's emit pipeline + governance, keeping β's dated palette as the
centre (Islands-Join-Mainland; α's light/green becomes a theme variant). Collapse the **three-colour-map drift**
(`gold→accent-gold` lives in color-axis + `CV_GLYPHIC.COLOR_TOKENS` + `CV_MEANING` seeds) as part of the lift, or
the live layer adds a fourth. The live RESOLVE rides `CV_AXES.css → var(--token)`, never hex. [A12/A15]

### 6 · The colour / state encoding
| Version (file:line) | Unique quality |
|---|---|
| `CV_MEANING.encodings` — surface-keyed facet→channel profiles, discrete + scale (`cv-meaning.js:210-255`) [A7/A12/A15/A19] | The existing data→visual-channel grammar; the documented extension path (authorable, round-trips to JSON) |
| **The hex short-circuit** — the `system-map` profile binds facet→bare hex (`#E0C010`) instead of a token id (`cv-meaning.js:232`) [A7/A12/A15] | The drift to fix: a second home for the literal; the `lineColor` seeds already do it right (`{token:'gold'}`) |
| `icons_circle_badges` desaturated/filled state; `components_badges` status dots; `icons_tones` tone ramp; `CalChip` `{kind→{bg,dot}}` [A20/A18] | Multiple state→appearance treatments scattered across specimens/kits |
| β's node-type tokens (`kind-process→{ref:gold}`) [A15] | A static facet(node-kind)→colour binding, machine-emitted |

**Fused direction:** one state→{fill,tone,desaturation} channel, the live glyphgraph surface registered as a
`CV_MEANING.encodings('glyphgraph')` profile, **keyed to token/axis-value ids, never hex**, resolved at paint
through `CV_AXES.css`, emitted/validated by β's machinery so a hex drift is caught at build. A new live facet
(e.g. `temperature` for "buyer gone cold") = compute-on-node + a referencing set — the documented path. Lift the
scattered state treatments (desaturated/filled, status dots, tone) INTO this one channel. [A7/A12/A15/A18/A19/A20]

### 7 · The mode / loadout / RHM switching spine
| Version (file:line) | Unique quality |
|---|---|
| Company presence-MODE registry — file-discovered `modes/<id>.py`; `set_mode` → governed loadout-swap confirm → `apply_loadout` → `ensure_resident` (OOM-safe) → `_repoint_rhm_for_loadout` (verify-by-probe + revert) (`modes_registry.py`; `suite.py:2626-2837`) [A8] | The whole "switch presence + load the right models + repoint the brain, atomically, governed" machine; the `consent` axis governs the act-vs-surface loop |
| `services.json` combos (loadout-class, `extends`/`swap`/`add`) [A8] | Named multi-service loadouts (the pipeline's service list IS a combo) |
| Browser **CV_MODE** (`atomicity/mode-engine.js`) — `interaction=f(mode)` (operator/inspect) [A9] | "What a CLICK does" — the canvas interaction-dial pattern |
| `brain_router.route_source` — RHM source router (fleet/recall/model) [A8] | The supervisor-as-loadable-brain resolver, one altitude up |

**Fused direction:** glyphgraph is a presence MODE (`modes/glyphgraph.py`: directive to co-author a graph,
`consent:'act'` so reversible mutations run live and irreversible ones surface, voice on, a `'sense'` live-lane)
+ a `services.json` `glyphgraph` combo (`extends: interaction`) + the extract role files — entered by
`set_mode('glyphgraph')`, riding the existing atomic-switch machine. **CV_MODE (canvas click-dial) and
modes_registry (RHM presence) are different axes sharing one registry mechanism — reconcile, the instrument needs
BOTH, never merge.** Wrinkles for Tim: use `loadout_class` not the partial `brain_config`; `resolve_model` is
dormant (live resolution still flows through `roles.resolve_binding`); assert `satisfied`. [A8/A9 — lens 8: this
is the MODE facet of "mode/app/panel non-exclusive"]

### 8 · The icon lookup + foundry
| Version (file:line) | Unique quality |
|---|---|
| `CV_ICONS` — 132 symbols, 131 faceted (0 tagless), lexical `search` (`cv-icons.js:430`) [A4] | The single icon source; the corpus is **dense, not under-tagged** (corrects the anchor) |
| `glyphic.generate`/`glyphic.save` + `glyphic-foundry.html` [A4/A11/A14] | The built propose→render→save loop; save → `symbol.rebuild()` → instant availability |
| pplx-embed-context-v1-4b @ :8007 (2560-dim, served) vs pplx-embed-v1-**0.6b** (1024-dim, INT8-native, MIT, **on disk NOT served**) [A2/A4] | Two embedder versions; the 0.6b is the *right* small icon-lookup embedder but needs serving; the served 4b does it now |
| `CV_SCAN` `f(sources × extractors)` continuous index (`scan-engine.js:181`); `nodes/embed`+`nodes/retrieve` cosine (Company) [A9/A2/A5] | The re-runnable-index pattern (swap regex extractor for embed) + the reusable cosine primitives |

**Fused direction:** an `embed` provider (role-resolved) → a re-runnable cosine index keyed by icon id,
deep-linked to `CV_ICONS.facets` (never copied), re-run on `CV_ICONS.add` (the `symbol.rebuild()` + `CV_SCAN`
disciplines) — this fixes the live hand-typed-tag staleness; a tuned threshold gates generate-on-miss; lexical
stays the floor. The gloss deep-links to its facet source (derived, re-runnable), written through the existing
`CV_MEANING.author.setGloss`, not 110 hand literals. [A4/A5/A9/A12 — the §5 violation dissolved as a class]

### 9 · Data-binding + storage
| Version (file:line) | Unique quality |
|---|---|
| `runtime/channel_boundary.py` — Supabase **Realtime WebSocket** subscriber, RLS-scoped, reconnect-with-backoff (`channel_boundary.py:119-245`) [A7] | The proven no-staleness **delivery** primitive (a row changes → a delta arrives → re-resolve; no polling) |
| `resolve_address` — the ONE resolver, scheme-dispatched, fail-loud, additively extensible (`cognition.py:1100-1218`) [A5/A7] | The single home an addressed glyphic re-resolves through; `project://` declared but **not yet dispatched** there |
| op-queue → adapter (`SYSTEM-MAP-EDITOR-ADAPTER.md`); `usePersisted`/`Resizable` localStorage [A11/A14/A19/A17] | The browser-can't-write-disk pattern (typed ops, staleness guard, one code path per op) + the transient/session layer |
| Prior art: extract-AS-triples / store-AS-property-graph; **no domain schema exists** (no projects/properties/buyers tables) [A7-B3] | Triples = a free incremental-merge extract wire-format; LPG = properties-on-edges |

**Fused direction (bring background, not a binary):** the stored unit is a **deep-linked typed glyphic** — it
references its type/facets/meaning/sockets, never copies (lens 5), and is a full glyphic, **not a bare triple**
(lens 7). Triples may be the *extract wire-format* (free incremental merge, A7-B3) but they do not collapse the
stored node. The binding chain: glyphic facet ← `CV_MEANING.encodings` (token-keyed) ← live state ←
`resolve_address` (add the additive `project://`/`property://` dispatch branch) ← `channel_boundary` Realtime
push. A bound glyphic and a talk-generated one are the **same spec with two provenances** — the discriminator is
whether it carries an `addr`; voice-correction and a CRM delta converge on the same facet mutation. The domain
schema (generic `entities`+`relations`+`states` vs per-noun tables) is an open decision; today a binding can be
demonstrated on `design_seeds.status`. [A7/A5/A11/A14/A19]

### 10 · The meaning / read-out
| Version (file:line) | Unique quality |
|---|---|
| `CV_MEANING.readGraph` / `describe` / `describeRelation` (`cv-meaning.js:476-688`; used in `language.html`) [A11/A14/A19] | The graph narrates itself from the SAME object; **does negation + conditionals** ("is NOT…", "if … then …") |
| Symbol gloss — deep-linked default, profile-overridable (`cv-meaning.js:407,618`) [A4] | Contextual word for a symbol, swappable per profile |
| `@dsCard` self-projection — a specimen narrates itself out of its own registry, harvested by the scan-engine [A20] | "Marks say themselves" — the same primitive at two altitudes |

**Fused direction:** the read-out is the DESCRIBE+EXPLAIN half of the loop, single-sourced from the graph; the
gloss derives from `CV_ICONS.facets` (re-runnable, written through `setGloss`); the live glyphgraph surface should
itself be a self-projecting `@dsCard` (its read-out = its subtitle, indexed by the scan-engine). Sentence-coverage
(does narration cover every relation the picture shows?) is a known-open in-scope tuning surface. [A4/A11/A14/
A19/A20]

---

## Latent glyphgraphs — the primitive already enacted, unnamed

These are the richest fusion source: things that are **already the glyphgraph primitive under another name**.
Recognising them means the instrument is mostly assembly + the thin missing parts, not a greenfield build.

- **`FloorplanOverlay.jsx`** (`virtual-hub/`) — **node-on-canvas**: rooms/dots positioned by percent, per-node
  `active` pulse state, click-to-pick (`onPick`). The static ancestor of auto-placed nodes. [A18]
- **`CaptureComment.jsx`** (`virtual-hub/`) — **node-detail popup, fully built**: click a point → popup anchored
  + clamped to the viewport + a tap-marker, a 4-state status pill, a rich composer. Exactly "click a glyph-node →
  detail card." [A18]
- **`brand_process_flow.html`** — **edge grammar**: node-cards joined by dot·line·▼ connectors, edge-label pills
  (action/duration), a ⊕ join operator, dashed-leader edges. The visual style-contract for any live edge. [A20]
- **`ViConsole` / AtomiCity** — **talk → surface mutates**: interpret → action-protocol → override-stick →
  shot-capture → vision.diff → learn-folds-back. A working (non-voice, non-graph) skeleton of the whole
  correction loop. [A9]
- **The Glyphic Foundry** (`ai-glyphic.js` + `glyphic-foundry.html`) — **the live propose→generate→save loop**:
  candidates render as glyphics, save rebuilds the symbol axis. The GENERATE-ON-MISS station. [A4/A11/A14]
- **The System Map** (`system-map.html` + `build-system-map.js`) — an **interactive graph canvas + typed
  op-queue** at scale: layout registry, FLIP-morph relayout, drag, undo, encoding-from-registry, edit→adapter→
  rescan. The operator-mutates→backend-owns-truth loop, proven. [A11/A14/A19]
- **`language.html`** — **render + narrate from one graph**: `DiagramSolver(type:'glyphgraph')` draws glyphics +
  meaning-edges AND `CV_MEANING.readGraph` speaks the same object, with live `setGloss` authoring. The closest
  precedent to RENDER + NARRATE + correct. [A14]
- **The Workshop BRIDGE + WSDiffCard** — **talk → typed-batch-diff → apply/discard → live re-render**, with
  `invertDiff` undo and `setActiveSurface` context resolution. [A10/A16]
- **`Build.jsx`** — **extract→compose in-browser**: plan → parallel specialists → one composer
  (extraction-vs-judgment). [A10]
- **`CV_SCAN`** — a **re-runnable `f(sources × extractors)` index**, kept fresh on load/interval/refocus, keyed +
  deep-linked. The literal substrate for the semantic icon index. [A9/A20]
- **The `@dsCard` self-projection** — a surface that **narrates itself out of its own registry** and is harvested
  by a generative scan extractor. The glyphgraph surface should self-describe identically. [A20]

---

## The hard laws (the 8, concrete — and machine-enforceable)

1. **One IR.** Every render surface is a projection of the one `CVGraph` IR (`core/cv-nodes.d.ts`); a surface
   that holds its own node model is the fifth parallel strand (`UNIFICATION.md §4`). reactflow/tldraw/`.spatial`
   hold *references* to CVGraph nodes; the static `glyphGraphView` renders the same IR for the page-face.
2. **Deep-linked storage.** A stored glyphic references type/facets/meaning/sockets — never copies — so growth
   never stales. Triples are at most the extract wire-format; the stored/rendered unit is a full typed glyphic.
3. **Colour via `CV_AXES → var(--token)`, never hex.** Kill the three-colour-map drift and the encodings
   hex short-circuit as part of the work, not after.
4. **Loud-fail.** Unknown facet/value/provider/runtime/type → throw. A resolve-miss → foundry-or-Notice + a
   recorded Gap; never a dropped node, never a silent placeholder, never a silent fallback to claude.
5. **Render-from-data, no per-type branch.** One generic node-type + one generic edge-type through
   `CV_GLYPHIC.render`; edges resolve through the registries; a new entity type just renders.
6. **Role-resolution, never a pinned model.** Capabilities declare a role; one config maps role→provider; the
   Company fleet resolves the model. Assert `satisfied`, not a non-empty model.
7. **A node is a full typed glyphic** (slots/sockets/triggers/values/tags/state/click-actions per
   `glyphic-type.js`), validated by `CV_GLYPHGRAPH.validateGlyphgraph` before render.
8. **mode/app/panel non-exclusive.** Build it as a MODE (`modes/glyphgraph.py`), runnable as an APP, embeddable
   as a PANEL in the RHM surface — hold all three.

**Make them machine-enforceable:** register three new `_system/mechanisms.json` detectors —
**provider-literal** (a `'claude'`/provider-id string passed to `resolveProvider`/`provider:`),
**typed-list** (a large hand-written `name→{...}` map that should be a generative/file-discovered registry),
**render-branch** (a `switch`/`if` on `.type`/`.kind` in a render fn) — each a `_system/<x>.py` + `test_<x>.py`,
same shape as `check.py`/`refcheck.py`. The existing design-lint catches **colour only** — it is blind to all of
these today. [A5/A11]

---

## The honest hard parts / gaps

- **No browser STT.** The "talk→" half is Company-side (8 ears); the design-system browser app only ever
  receives typed text. Speech crosses at the bridge; everything downstream (brain, extract, narrate) is
  server-side. [A3/A10/A16]
- **Renderer substrate is partly open + a cross-repo discrepancy to reconcile.** **Resolved here:** `canvas/app`
  (tldraw 3.13.1) and `surface/app` live in **`~/company/`, NOT in `claude-ds/`** (verified). AREA-16's grep of
  `claude-ds/app/` correctly found **zero** canvas libs; AREA-6/AREA-14 read the Company-side apps. So adopting
  the tldraw canvas is a **cross-repo seam move** (lens 6), and there is no live-canvas lib *inside the design
  system* — the `.spatial`/`glyphGraphView` paths are the in-`claude-ds` options. This is the AREA-6-vs-AREA-16
  discrepancy, reconciled. [A6/A14/A15/A16 + verified]
- **The layout-jump problem.** The existing auto layout re-ranks every render → nodes jump as the graph grows.
  Fix: an incremental placer that freezes x/y per node on arrival, then render through the authored-x/y branch.
  [A19:3-A]
- **Extract-layer latency reality.** It is **one resident brain with concurrency**, not a fleet — the brain-KV
  is shared with the main reply; the knee collapses to ~1-5 mid-deep-reply. The realistic shape is short-context,
  think-off, schema-constrained roles fired in a burst at each pause. A higher-util swarm-brain config is a
  GPU-reconfig lever (needs-tim), not free. [A2]
- **The provider role-layer + the dead claude-pin guards.** ~5 literal sites + ~27 caps + the AIEngine dead
  `typeof provider` guard (~16 sites, always falls to claude) + the foundry `window.claude` liveness check must
  be role-resolved before extraction can ever run on Company-local models. [A1/A16/A14]
- **The un-@dsCard'd files falling out of the index.** `brand_icons_bronze.html` + `brand_icons_gold.html` carry
  no `@dsCard` tag (32/34) → the scan-engine's `dscard` extractor misses them. The failure mode the glyphgraph
  surface must design against (a node/graph that doesn't emit its own read-out goes invisible). Resolve-into-scope:
  tag them. [A20]
- **No domain schema** (no projects/properties/buyers tables); `project://` is declared but the one resolver
  doesn't dispatch it yet. The "property sale" domain is unbuilt; a binding can be demonstrated today on
  `design_seeds.status`. [A7]
- **`.d.ts` vs runtime drift** — `"glyphgraph"` is handled in the solver but absent from the `CVGraphType` union;
  the edge facets (`line`,`direction`,`lineColor`,`routing`) aren't in the `.d.ts`. Resolve-into-scope hygiene.
  [A19:A4]
- **Sentence-coverage** — the read-out can drop a clause the picture shows; a known-open FORM/Tim tuning surface,
  in-scope (no-deferral), not green-painted. [A19:3-D]

---

## The open DECISIONS for Tim (the wave surfaces; it does not decide)

1. **Renderer substrate — on MECHANICAL FIT for the real needs, under the one-IR law.** The need set: ports +
   per-node click-actions (per `glyphic-type.js`) + node state + a programmatic store the pipeline drives +
   the existing tokens/`canvas.css` scaffold + stable incremental placement. The candidates (all projections of
   the one IR, all render nodes via `CV_GLYPHIC.render`): **glyphics-inside-tldraw** (reuse the Company canvas/app
   console + NodeShape "ports-from-registry"; cross-repo seam) · **an interaction-layer over `glyphGraphView`**
   (the only glyphic-native render, gets the auto read-out for free) · **the `.spatial` scaffold** (token-pure,
   zero bundle, CSP-clean) · **reactflow in a Vite app** (first-class edges + dagre/elk, absent today). The
   decision is which interaction model fits — not which library — and the no-fifth-strand law governs all of them.
2. **The storage model — deep-linked typed-glyphic persistence (bring background, not a binary).** The stored
   unit references its type/facets/meaning/sockets and is a full glyphic, not a bare triple; triples may be the
   extract wire-format. The open part is the domain schema underneath (a generic `entities`+`relations`+`states`
   store vs per-noun tables), addressed via `resolve_address` (+ a `project://`/`property://` dispatch branch),
   delivered by `channel_boundary` Realtime. [A7]
3. **Honoring the dated palette.** The `GOLD-PRIMARY WARM THEME` decision (β `tokens.json`, Tim 2026-06-07, "gold
   is THE primary, no green") is the centre's palette; α's light/green becomes a theme variant in the unified
   model (Islands-Join-Mainland). Surfaced, not silently overridden. [A15]
4. **mode/app/panel composition.** How the glyphgraph composes as a MODE (with loadouts), an APP, and a PANEL in
   the RHM surface — non-exclusive (lens 8). The `consent` axis governs whether the loop acts vs surfaces. [A8]
5. **One fact to verify (not a design choice):** does bridge `:8770` send cross-origin CORS to a Vite surface, or
   is the surface served same-origin (the canvas/app way)? Gates the browser→Company wire. [A1/A14]

---

## Build groups (sequenced, all in scope, no "later" — naming design-side vs cross-into-company)

> Every group folds the many versions of its capability into one; none picks a winner. "Design-side" = inside
> `claude-ds/`; "cross-into-company" = touches `~/company` (lens 6, with care). All in scope (no-deferral).

- **G1 · Provider role-layer + `company-http` runtime.** *Design-side + cross-into-company.* `ROLE_PROVIDERS` +
  `defaultProvider(role)` in `CV_AI`; route the ~5 literal sites + ~27 caps + the dead `typeof provider` guard +
  the foundry `window.claude` check through it; add `cvCompany`/`company-http` reaching the bridge
  `/api/cognition/run_role`. Verify the CORS fact. [A1/A5/A16]
- **G2 · Semantic icon index + generate-on-miss.** *Design-side + cross-into-company (embedder).* An `embed`
  provider + a re-runnable cosine index keyed by icon id, deep-linked to `CV_ICONS.facets`, re-run on add (the
  `symbol.rebuild()`/`CV_SCAN` pattern) — fixes the hand-typed-tag staleness; a tuned threshold gates the foundry;
  derive the gloss. [A4/A5/A9/A12]
- **G3 · Transcript fan-out + extract roles.** *Cross-into-company.* One `_emit("voice.transcript", …)` at the
  STT-return point so the transcript rides the existing `/api/stream` SSE bus (today hardwired to one consumer);
  `roles/glyph_*.py` (think-off, schema-constrained, burst-at-pause) via `run_swarm`. [A2/A3/A14]
- **G4 · RESOLVE composer + JUDGE.** *Design-side + cross-into-company.* `roles/glyph_compose.py` folds the swarm
  into one graph delta; RESOLVE composes facets via `CV_AXES`/`CV_MEANING` (combinatorial, not flat lookup),
  validated by `CV_GLYPHGRAPH.validateGlyphgraph`; emit a `CVGraph{type:'glyphgraph'}`. [A2/A8/A11/A12/A13/A19]
- **G5 · The conversation surface (fused).** *Design-side (+ cross-repo seam to the Company surface).* One
  surface = ViConsole's act-spine + ChatRail's provider/routing + ChatPanel's stage cards, one message-kind
  renderer, on the token-class components + a `.cv-feed` primitive + `<Glyphic/>` icons; the three originals
  retire into it. [A10/A16/A17/A18]
- **G6 · The canvas (renderer decision → the chosen substrate).** *Design-side and/or cross-into-company per the
  decision.* render-from-data node + edge (server-composes-glyph, FE reflects), the `brand_process_flow` edge
  style-contract, the **incremental placer** (freeze x/y → authored-x/y branch), positions backend-owned; the
  static `glyphGraphView` stays the page-face projection of the same IR. Reconcile the `.d.ts` drift. [A6/A11/
  A12/A14/A15/A18/A19/A20]
- **G7 · NARRATE wire.** *Cross-into-company.* Connect the design-side sentence composition (`readGraph`/
  `describe`) to the Company speak-back (`/api/say`/`/api/tts`/`speakable`); close sentence-coverage; narration as
  a consumer of the same bus. [A3/A11/A14/A19]
- **G8 · Data-binding + storage.** *Cross-into-company.* `CV_MEANING.encodings('glyphgraph')` token-keyed (fix
  the hex short-circuit); a deep-linked typed-glyphic persistence with the domain schema decision; the
  `project://`/`property://` dispatch branch + `channel_boundary` delivery; the op-queue→adapter for any
  browser-write-back. [A7/A11/A14/A19]
- **G9 · The mode/loadout entry.** *Cross-into-company.* `modes/glyphgraph.py` (directive, `consent`, voice,
  `'sense'` lane) + a `services.json` `glyphgraph` combo (`extends: interaction`); reconcile (do not merge)
  CV_MODE as the canvas click-dial. [A8/A9]
- **G10 · The gate detectors + hygiene.** *Design-side.* Register provider-literal / typed-list / render-branch
  mechanisms; tag the two un-@dsCard'd files; close the `.d.ts`/`"glyphgraph"`-union drift. [A5/A19/A20]
- **G11 · The integrated voice-corrected loop (the frontier).** *Cross-into-company.* Close BUILD → DESCRIBE →
  EXPLAIN → correct/extend: a voice correction is a typed graph-op on the in-memory `CVGraph`, applied through one
  code path per op with FLIP reflow; human + pipeline edits append to one op-queue against one model; the
  `consent` axis governs act-vs-surface; AtomiCity's interpret→act→capture→learn is the skeleton, the Company
  vision role closes the self-check. Build with iteration, verify by use. [A8/A9/A10/A14/A19]

---

## Executive summary

The conversational glyphgraph — talk and watch a graph get BUILT, DESCRIBED, EXPLAINED, and corrected/extended by
Tim's voice + the AI — exists in *many* partial versions across both repos, and the lens forbids reading that as
"done": the work is to **fuse the versions of each capability into one, never pick a winner.** The unification map
catalogues, per capability (providers · extract · conversation surface · canvas · tokens+axes · colour/state ·
mode/loadout · icon foundry · data-binding+storage · read-out), every version with its unique quality and a
fuse-not-choose direction — and a dedicated section names the **latent glyphgraphs** already enacted unnamed
(FloorplanOverlay, CaptureComment, brand_process_flow, ViConsole, the Foundry, the System Map+op-queue,
language.html, the Workshop diff-loop, Build, CV_SCAN, the @dsCard self-projection). The hard laws: one CVGraph IR
(no fifth render strand), deep-linked typed-glyphic storage (not bare triples), colour via CV_AXES→var(--token)
never hex, loud-fail, render-from-data, role-resolution not pinned models, a node is a full typed glyphic,
mode/app/panel non-exclusive — made machine-enforceable by three new gate detectors. The honest gaps: no browser
STT (speech is Company-side), the layout-jump (fixed by a freeze-x/y incremental placer), the one-resident-brain
latency reality (burst-at-pause, not an always-on fleet), the dead claude-pins to role-resolve, the
two un-@dsCard'd files. **Resolved cross-area discrepancy:** the tldraw `canvas/app`/`surface/app` live in
`~/company`, NOT in `claude-ds/` — so adopting them is a cross-repo seam, and there is no live-canvas lib inside
the design system itself. The open decisions for Tim: renderer substrate on mechanical fit (tldraw · interaction-
over-glyphGraphView · the .spatial scaffold · reactflow — all projections of the one IR), the deep-linked storage
model (bring background), honoring the dated GOLD-PRIMARY palette, and mode/app/panel composition. Build groups
G1-G11 sequence all of it (none deferred), naming design-side vs cross-into-company; the integrated voice-corrected
loop is the frontier — its parts are all enacted somewhere, the integration is new.

Path written: `/home/tim/company/design/claude-ds/analysis/glyphic-language/live-instrument/LIVE-INSTRUMENT.md`
