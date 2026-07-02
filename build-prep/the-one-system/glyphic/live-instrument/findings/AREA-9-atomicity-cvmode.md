# AREA-9 — AtomiCity & CV_MODE (the un-read sub-app)

> Wave-2 coverage agent. Territory: `claude-ds/atomicity/` (~21 files, all read in full except the
> three section-renderers Foundations/Ingest.jsx which were read partially + characterized from their
> headers + the atlas-model section defs — see coverage note §0). Marks: **Observed (file:line)** /
> **Inferred** / **External-prior-art** / **My-idea**. Reads *with* the anchor + LIVE-INSTRUMENT.md and
> contradicts both where they're naive about this code.

## 0 · Coverage honesty
Fully read: `mode-engine.js`, `vi-brain.js`, `ViConsole.jsx`, `VoiceSurface.jsx`, `AtomiCity.jsx`,
`atlas-model.js`, `explore-engine.js`, `scan-engine.js`, `picker.js`, `override.js`, `shot.js`,
`kit.jsx`, `Explore.jsx`, `Home.jsx`, `index.html`, `runtime/modes_registry.py` + `modes/AGENTS.md`
(Company side, for §b). Partial: `Atlas.jsx` (read tree + detail head; rest is per-`kind` detail
renderers — characterized, not line-verified), `Foundations.jsx` / `Ingest.jsx` (read header +
`atlas-model.js` section defs; they are **section renderers**, not engines — `CV_SOURCE` engine in
`ingest.js` *was* read fully). No coverage claim beyond this.

---

## HEADLINE (the correction the layer-1 plan needs)
**LIVE-INSTRUMENT.md calls the "integrated, voice-corrected, live NL→glyphgraph loop … genuinely new …
the one thing with no prior art" (LIVE-INSTRUMENT.md:93-96). That is too strong. A NON-VOICE, non-graph
skeleton of EXACTLY that loop is already built and working in AtomiCity** — talk to an agent → it acts on
a live surface → the change sticks → it's captured visually → the agent reacts → and the feedback folds
back so it improves. The novelty collapses from "the whole loop" to **two specific legs**: (1) the
*voice* front of it, and (2) the surface being a *glyphgraph* instead of the DOM. The correction loop's
*spine* is prior art **inside this repo**.

The loop, with the inert leg named precisely:
```
ViConsole.send()           user message (text)              ViConsole.jsx:32
  → VI_BRAIN.interpret()    model turn → {say, actions[], proposals[], options[]}   vi-brain.js:132
  → ATOMICITY.act(verb)     the ACTION PROTOCOL drives the surface   AtomiCity.jsx:56
  → CV_OVERRIDE.apply()     the edit STICKS (survives React re-render)   override.js:60
  → CV_SHOT.snapshot()      before/after capture   shot.js:47 / ViConsole.jsx:73-83
  → CV_AI.execute('vision.diff')   the agent SEES the result + says if it hit intent   shot.js:86
  → VI_BRAIN.learn()        folds feedback → live CV_AI behaviour + CV_HOST proposal   vi-brain.js:213
```
**Inert leg (state it loud, don't overclaim):** `vision.diff` (shot.js:86-94) **throws in the sandbox** —
`resolveProvider('vision')` has no runtime, so the "AI sees the after-image and reacts" leg is loud-fail,
not verified end-to-end (callers `.catch(() => {})` and fall back to the computed-style diff, ViConsole.jsx:88).
So: **skeleton exists and runs for the text→act→stick→capture→learn path; the see-and-react leg is wired but
unproven** (no vision provider in sandbox). [Observed]

This is the single most load-bearing finding for the build: the live instrument should **reuse this brain-
console + action-protocol + correction/learn pattern**, re-pointing its verbs from DOM-restyle to graph-mutation.

---

## (a) What AtomiCity IS — runtime-disposable, architecturally load-bearing
**Verdict: a sandbox/prototype harness at RUNTIME (not a FORM reference, not production), but architecturally
a genuine reusable-pattern mine.** Tim's "the canvas/test apps are often disposable AI scaffolding" applies to
the *runtime artifact*; it does NOT apply to the *architecture inside it*.

**Disposable-harness signals [Observed]:**
- CDN React **development** build + `@babel/standalone` compiling JSX in the browser at load (index.html:14-16) —
  a prototyping rig, never a shipped runtime.
- Persistence is `localStorage` everywhere — learnings (vi-brain.js:30,55), explored atoms (explore-engine.js:107),
  ingested sources (ingest.js:30). No backend.
- Sandbox stubs: `vision.diff` throws (shot.js:91); `host-tree` scan source returns `[]` when no runtime is
  connected (scan-engine.js:162); the file-write Bridge runtime (`fsapi`/`host-fs`) is opt-in via a "connect"
  gesture (AtomiCity.jsx:62-66). It runs read-only-against-itself by default.
- `index.html:2` self-labels it `@dsCard … "A standalone browser for the whole design system"` — it is a
  *specimen card in the gallery*, i.e. a demo of an idea, consistent with the design-folder's "mockups are
  scaffolding not spec" rule.

**Architecturally load-bearing (REUSE these) [Observed / Inferred]:**
- **The projection-never-drifts Atlas** (`atlas-model.js`) — the whole nav tree is *derived* from the four
  registries (`_ds_manifest.json` + `CV_REGISTRY` + `CV_AI` + `CV_HOST`), so it cannot drift; add a token/
  capability/type and it appears on next `build()` (atlas-model.js:1-20, 213-252). This is the registry-is-truth
  law realized as a UI. [Observed]
- **The override layer** (`override.js`) — the real solution to "a live edit that survives React re-render":
  stamp `data-cv-ov="N"` + write a keyed `!important` rule into a dedicated stylesheet (override.js:60-76). Reusable
  for any live-mutation surface. [Observed]
- **The action protocol** (AtomiCity.jsx:56-85 + the `ACTIONS` vocabulary vi-brain.js:36-48) — a clean
  agent→surface verb contract (open/expand/highlight/search/run/propose/connect/ingest/explore/restyle/pageshot).
  This is the exact shape the glyphgraph canvas needs, re-verbed. [Observed]
- **The scan engine** (`scan-engine.js`) — a continuously-rebuilt index `f(sources × extractors)` — see §d/§G-L2. [Observed]
- **The visual-capture memory** (`shot.js`) — element/page snapshot + FIFO image memory + before→after pairs. [Observed]

So: **strip the runtime (CDN React/Babel/localStorage/sandbox stubs); keep the patterns.** [My-idea, grounded]

---

## (b) mode-engine.js / CV_MODE vs the Company modes_registry — RECONCILE, do not unify

**Correct the prompt's premise first:** the prompt calls the Company `modes_registry` "a separate
*browser-side* mode system." It is **not browser-side — it is server-side Python** (`runtime/modes_registry.py`,
discovering `modes/<id>.py`). [Observed: modes_registry.py:1-21; modes/AGENTS.md:11-16]

These are **two different axes that share one mechanism**, not duplicates:

| | **CV_MODE** (browser) | **Company modes_registry** (server) |
|---|---|---|
| File | `atomicity/mode-engine.js` | `runtime/modes_registry.py` + `modes/*.py` |
| Axis | **what a CLICK does** — `interaction = f(mode)` (mode-engine.js:9) | the RHM's **presence / consent / resolution posture** |
| Members | `operator` (click navigates/edits), `inspect` (click selects → Vi) (mode-engine.js:71-89) | `listening`, `text-only`, `background`, `focus`, `walkthrough`, `watch-and-react`, `decide-for-me`, `off` (modes/AGENTS.md:12) |
| A mode declares | `{id,label,icon,hint,cursor,accent,config{},onEnter,onExit,onPick,behaviours}` (mode-engine.js:11-13) | `{order,label,directive,resolution,consent,grain,shape,stage,live,reserve_r,per_role_ctx,main_ctx_tokens,brain_config,…}` (modes_registry.py:30-32) |
| Effect on AI | `activate()` pushes the mode's `behaviours` as `CV_AI`'s active set (mode-engine.js:60-62) | the mode's `directive` is injected into the RHM prompt; `brain_config` selects the loadout (modes/AGENTS.md:21-22) |

**The deep parallel worth naming (the real finding):** *both gate AI posture by mode, and both are
registry-discovered (register/resolve/query/activate/subscribe, fail-loud, id==key, order-bearing).* One law —
**"AI-posture = f(mode); a mode is a registry row, not a code branch"** — realized at **two layers** (the
browser interaction layer and the server presence layer). CV_MODE even mirrors modes_registry's own self-
description ("modes are data + lifecycle, so new ones drop in without touching the shell", mode-engine.js:4-7;
cf. "add a mode = drop a file", modes/AGENTS.md:8-9). [Observed both]

**Do NOT merge them** (resist the unions-not-bridges reflex here — it's the wrong level). They govern
different domains. **The live instrument needs BOTH:**
- **canvas interaction-modes** (CV_MODE-shaped): e.g. `talk` (utterances build the graph), `arrange` (drag/
  pin nodes), `inspect` (click a glyphic → Vi reads it out), `correct` (click a node → "this is wrong, …").
  `interaction = f(mode)` is exactly the dial the instrument's canvas wants. [My-idea, grounded in mode-engine.js]
- **conversation presence-modes** (modes_registry-shaped): the RHM is *already* listening in
  `walkthrough`/`watch-and-react` etc.; the live-instrument session IS one of these presence modes (likely a
  new `modes/<id>.py`, e.g. a `compose` / `instrument` mode whose `directive` is "extract structure from what
  Tim says and build the glyphgraph"). [Inferred — the instrument is a presence the RHM is in]

**One sentence for the synthesis:** CV_MODE is the borrowable *pattern* for the canvas's interaction dial;
the Company modes_registry is the place a new *presence mode* for the instrument session gets registered. Same
mechanism, two homes — don't collapse them.

---

## (c) VoiceSurface / vi-brain / ViConsole — there is NO voice surface here; there IS a reusable brain-console

**Lead with the misnomer — this directly contradicts the prompt's framing and any layer-1 assumption that
a voice/conversation surface already exists here:**

- **`VoiceSurface.jsx` is NOT a voice/STT/audio surface.** Its own header reads `// atomicity/Voice.jsx …
  the generative COPY surface` (VoiceSurface.jsx:1-4). It is a **copywriting tool**: pick a product moment
  (CTA / headline / insight / empty-state / error, VoiceSurface.jsx:31-37), Vi writes microcopy options in
  the house voice (`voice.conceptv` behaviour), you pick one, save it as a voice example. "Voice" = **brand
  voice / tone**, not spoken audio. [Observed]
- **`ViConsole.jsx` is a TEXT chat console** — `<textarea>` + send button, message feed, suggestion pills,
  Chat/Teach/Memory modes (ViConsole.jsx:106-236). No microphone, no audio, no STT/TTS anywhere in the file. [Observed]
- **No voice/STT/audio code exists anywhere in `atomicity/`.** [Observed — grepped + read all 21 files]

**So the live instrument does NOT inherit a voice surface from here.** The voice front must come from the
**Company** side (the ears/STT + speak-back the anchor §7 names, and AREA-3 confirmed are built). What it
DOES inherit from here is the much more valuable thing:

**The reusable pattern = the brain-console + action-protocol + correction/learn loop** (`vi-brain.js` +
`ViConsole.jsx`). Concretely:
- `VI_BRAIN.systemPrompt(ctx)` composes a live **census** of the system + the architecture rules + applicable
  learnings + the action protocol — so the agent "knows everything without being told" (vi-brain.js:88-126).
  The instrument's brain composes the same way over the **glyph/meaning registries** instead. [Observed → My-idea]
- `VI_BRAIN.interpret()` returns `{say, actions[], proposals[], options[], followup}` from one model turn,
  parsing a fenced ```` ```atomicity ```` JSON block out of prose (vi-brain.js:132-160, extractBlock:305). This is
  exactly the "extract structure from talk" shape the instrument needs — **schema-constrained JSON out of an
  utterance** (the anchor's EXTRACT stage). [Observed]
- **The verb mapping for the instrument [My-idea, grounded]:** AtomiCity's verbs
  (open/restyle/propose, AtomiCity.jsx:56-85) → graph verbs (`addNode`/`addEdge`/`setState`/`relate`/`place`/
  `narrate`). The protocol shape (host implements each verb; the vocabulary is single-sourced in the brain;
  the agent returns a list the host executes) is directly reusable.
- `VI_BRAIN.learn()` (vi-brain.js:213-251) distils conversational feedback → a crisp instruction → registers
  it LIVE into `CV_AI` as a behaviour → proposes it to `CV_HOST` for permanence. This is the "voice-correction
  improves it" leg, already built (just not over a graph). [Observed]

**Caveat for §c:** `vi-brain.js` *hardcodes* `provider:'claude'` on its own capabilities (atomicity.interpret
vi-brain.js:291, atomicity.learn:298) — see §provider-pins. If reused, role-resolve the provider.

---

## (d) Explore / Atlas / scan engines — what's relevant to the glyphgraph canvas

**There is NO existing node-graph / reactflow / spatial-graph canvas in `atomicity/`.** (Consistent with
AREA-6's finding that reactflow appears nowhere and the live graph-canvas is `canvas/app` on tldraw.) [Observed]

What IS here, ranked by relevance to the instrument:

1. **`scan-engine.js` (CV_SCAN) = the prior art for the plan's G-L2 re-runnable icon index.** Its whole
   identity is `scan-index = f(sources × extractors)`, **continuously** rebuilt — on load, on a 45s interval,
   and on tab-refocus (scan-engine.js:7-9, 94-101). You **register what to scan + what to extract**, never a
   hand-built index (scan-engine.js:42-49, 121-183). It builds a live `token-usage` graph (which token is
   used where) keyed by id, **deep-linked not copied** (re-derived each run, scan-engine.js:85-91). It's
   *lexical regex*, not embeddings — but it is **exactly the discipline LIVE-INSTRUMENT.md G-L2/stage-4 wants
   for the semantic icon index** ("a re-runnable cosine index keyed by icon id … deep-linked to CV_ICONS.facets,
   NOT copied"). The instrument's icon index should be a CV_SCAN-shaped registered pass, swapping the regex
   extractor for an embed-extractor. **Name this connection in the synthesis** — it's a same-repo precedent the
   layer-1 plan describes as "BUILD (new)" without noticing the pattern already exists. [Observed → My-idea]

2. **`explore-engine.js` (CV_EXPLORE) + `Explore.jsx` = the generate→steer→converge→promote loop**, and a
   **2D click-on-surface selection gesture** (NOT a node graph). `Explore.jsx` renders a real product card whose
   every part is a selectable hotspot (`Canvas`, Explore.jsx:155-190); click a part → Vi generates N distinct
   style directions → like/dislike steers a local taste profile (explore-engine.js:142-163, no model) → iterate
   ("More like these / Bolder / Quieter / Refine this", Explore.jsx:130-135) → **promote** a chosen recipe into
   a registered `CV_REGISTRY` Type, staged via `CV_HOST` (explore-engine.js:91-104). Relevance: this is a
   **divergent-options-then-converge** interaction (extract-vs-judgment at the UI layer) and a **"selection on a
   live surface"** gesture — both transferable to the glyphgraph (e.g. generate-on-miss offering N candidate
   icons; selecting a node to correct it). It is NOT a spatial/graph layout engine. [Observed]

3. **`atlas-model.js` (ATLAS) = a hierarchical TREE projection, not a graph.** It's the registry-is-truth
   pattern (projection can't drift, atlas-model.js:11-16) and a `census()` the brain reads (atlas-model.js:293-316).
   Relevant as the **"derive the surface from the registries"** discipline the glyphgraph render should follow
   (render-from-data), but it is a tree, not the node/edge spatial canvas. The actual node/edge type lives
   elsewhere (`core/cv-nodes.d.ts` `CVGraph`, per anchor §7). [Observed]

4. **`picker.js` (CV_PICK)** — document-wide element selection: hover-spotlight + click → a structured
   descriptor (role/tag/text/box/computed-styles) + a live node ref (picker.js:55-87). The instrument's
   "click a glyphic on the canvas → hand it to the brain to correct" is the same gesture over graph nodes
   instead of DOM elements. [Observed]

**Net for §d:** the glyphgraph canvas is genuinely NEW here (no node-graph engine), but **the disciplines it
needs — derive-from-registry, continuous re-runnable index, click-to-select-and-hand-to-agent, generate-N-then-
converge — all have working precedents in this folder.** Reuse the disciplines; build the spatial canvas fresh
(or on `canvas/app`'s tldraw per AREA-6).

---

## Cross-cutting finding · PROVIDER PINS (reinforces AREA-1's staleness finding)
AtomiCity *adds new* hardcoded `provider:'claude'` literals — the exact pattern LIVE-INSTRUMENT.md wants the
gate to catch:
- `voice.write` capability — `provider:'claude'` (VoiceSurface.jsx:19)
- `explore.variations` / `explore.run` — `provider:'claude'` (explore-engine.js:129, 137)
- `atomicity.interpret` / `atomicity.learn` — `provider:'claude'` (vi-brain.js:291, 298)
- (vision capabilities pin `provider:'vision'`, host capabilities pin `provider:'host-fs'` — those are
  capability-class names, less problematic, but still literal — shot.js:82,88; explore-engine.js:133)

**Implication:** if the instrument reuses this brain-console, the role-layer fix (LIVE-INSTRUMENT.md G-L1)
must apply to these too — **role-resolve, don't copy the pin.** This is *new* drift introduced by the sub-app,
so the gate detector (G-L8 provider-literal) would flag `atomicity/` itself. [Observed]

---

## Threads / open what-ifs this area opens
- **The action-protocol is the reusable contract** for "talk → mutate a live surface." Define the glyphgraph
  verb set ONCE in the instrument's brain (as vi-brain.js does for DOM verbs) and the canvas implements each.
- **`vision.diff` is the model for the instrument's self-check** — after the graph mutates, capture it and let
  the brain *see* whether it matched intent. Currently throws (no sandbox vision runtime); on the Company side
  a vision-capable role exists, so this leg can actually close there. [Inferred]
- **CV_SCAN's continuous-rebuild + extractor registry should be the literal substrate of the icon index** —
  one new extractor (embed) instead of regex, same loop. Worth a line in G-L2.
- **A new Company presence mode** (`modes/<id>.py`) likely needs to exist for the live-instrument session
  itself — its `directive` = "extract structure from Tim's speech and compose the glyphgraph." [Inferred]

---

## 3-line summary
AtomiCity is a **runtime-disposable** sandbox harness (CDN React-dev + in-browser Babel + localStorage + sandbox
stubs) but **architecturally load-bearing** — and it already contains a **working non-voice, non-graph skeleton of
the exact correction loop** LIVE-INSTRUMENT.md calls "no prior art" (interpret→action-protocol→override-stick→shot-
capture→vision.diff[throws in sandbox]→learn-folds-back), so the true novelty is just the voice front + the
glyphgraph surface, not the loop. Its "Voice" surface is **brand-copywriting, not audio** (no STT/TTS anywhere);
the reusable asset is the **brain-console + action-protocol + learn loop** (re-verb DOM→graph) and the
**CV_SCAN continuous `f(sources×extractors)` index** as the literal pattern for G-L2's re-runnable icon index;
**CV_MODE (browser "what a click does") and the Company server-side modes_registry (RHM presence/consent posture)
are different axes sharing one registry mechanism — reconcile (the instrument needs both), never merge** — and the
sub-app *adds* new `provider:'claude'` pins (5 sites) that reinforce A1's role-layer fix + the gate detector.

Path: `/home/tim/company/design/claude-ds/analysis/glyphic-language/live-instrument/findings/AREA-9-atomicity-cvmode.md`
