# Live-Instrument Layer — research-wave ANCHOR

## 0 · How to read this
This is the **shared anchor** for a research wave. You are ONE of seven agents; read this whole doc first so
we all hold the same partial picture. **Do NOT just confirm it** — stress-test it, contradict it where it's
naive, and GROUND it in what's actually in the code. **Expansion ratio > 1**: leave the idea bigger and more
real than you found it. The "yes, but actually the code does X" is the gold. Mark every claim:
**Observed (file:line)** / **Inferred** / **External-prior-art** / **My-idea**. Write FULLY — your area was
sized for depth. Cite real paths + names. Two repos are in scope: the **design system**
`/home/tim/company/design/claude-ds/` and the **Company** `/home/tim/company/`.

## 1 · The problem
The Company is building **Glyphic** — a visual language where meaning is composed from a glyph's facets (form,
fill, colour, texture, motion, size, outline, the symbol inside, edges between glyphs). It already: composes +
renders glyphs; reads a glyph/graph out as a sentence; lets the AI **and** the user author the dictionary live
(it's data, not code); and the meaning lives in a registry. (An engine build is finishing in parallel: facets,
the glyphgraph data model + rulebook, the SVG render, data-binding, self-describing guides/pages.)

What's missing is the thing that makes it an **instrument**: you can't yet **talk and watch a graph build
itself in real time.** Today a glyphgraph is authored by hand/spec. The vision: a **conversation** — Tim's
transcribed voice + the AI — that **live-generates and reshapes a glyphgraph**, rendered on an interactive
canvas (reactflow), with small **local models** as a fast concurrent middle layer turning talk into structure.

## 2 · The insight / the big what-if
**What if natural language flowed into a living glyphgraph in real time?** You speak a project (e.g. a property
sale); a fleet of small local models continuously *extracts* structured meaning (the things, their relations,
their states) with structured outputs; each thing *resolves* to a glyphic; nouns with no close icon trigger the
foundry to *draw a new icon live*; nodes *auto-place* on a reactflow canvas; the graph *narrates itself back*;
and you correct it by voice ("no, the buyer's gone cold") and it mutates. Two-way: your voice and the AI both
author the same living surface. This is the layer that sits ON the engine being built.

## 3 · The shape, held loosely (the pipeline)
LISTEN (STT, transcribe) → **EXTRACT** (concurrent small local models, structured outputs, one per concern —
entities / relations / states / placement-hints) → **RESOLVE** to glyphics (form from type, fill/colour from
state, **symbol via semantic icon-lookup**, edges from relations, all against the registries) → **GENERATE-ON-
MISS** (icon lookup below a similarity threshold → the foundry draws + saves a new on-style icon → use it live)
→ **AUTO-PLACE** (incremental, stable layout as nodes arrive) → **RENDER** (reactflow custom-node = a glyphic,
driven programmatically from the pipeline) + **NARRATE** (the read-out speaks it) → **LOOP**.
This is Tim's *extraction-vs-judgment* law: many small models EXTRACT in parallel; a stronger one JUDGES/composes
the final graph. And *cognition-is-role-resolved*: each role (extract-entities, compose-graph) resolves to a
model, never a pinned one.

## 4 · My ideas (marked as ideas — verify/replace with what's real)
- *(my-idea)* Wire the Company's local models into the design-system `CV_AI` as **providers resolved by role/id**
  (openai, google, and PRIMARILY the Company fleet) — currently `CV_AI` assumes a single `claude` provider.
- *(my-idea)* Semantic icon-lookup = embed the noun with a small embedder (**pplx ~0.6b**) → nearest tagged icon;
  below threshold → `glyphic.generate`.
- *(my-idea)* reactflow for the live interactive canvas (custom node renders a glyphic via `CV_GLYPHIC.render`,
  the store driven by the extract→resolve→place pipeline, an auto-layout plugin), distinct from the no-script
  SVG page-face render.

## 5 · The GOVERNING LAW (hold this throughout — it's the make-or-break)
**Everything generative / deep-linked / resolved from a single source. NO handwritten or hardcoded backfill,
NO hardcoded provider, NO per-type render branch — so as the system GROWS/updates/adds, nothing stales.** Tim
(non-developer) was emphatic: planning this in at the START is the highest-value decision; un-hardcoding a grown
system later is brutal. The system is ALREADY resolution-native — the live layer must extend that, never break
it. (E.g. icon tags are NOT a typed list — they're a generative pass [embed → derive] that re-runs as icons are
added, with meaning deep-linked to its source, not copied.)

## 6 · The honest hard parts
- **Realtime latency** of the extract layer (can small local models keep up with speech, concurrently, with
  structured output, fast enough to feel live?).
- **Stable incremental auto-placement** (a graph that grows during a conversation without jumping around).
- **The no-staleness discipline holding** across providers, icon tags, and the renderer (where would hardcoding
  sneak in? — this is the rigor area).
- **The provider abstraction** actually spanning claude/openai/google/Company-local with structured outputs +
  the browser↔Company boundary (the design system runs in a browser; the local models are server-side).
- **reactflow inside the no-script-CSP / bundle** constraints of this design system.

## 7 · What I can already see (real anchors — verify + extend, don't take on faith)
- **CV_AI** — `app/ai/ai-registry.js` (`window.CV_AI`): `register/resolve/execute/resolveProvider/resolveContext`;
  layers provider·behaviour·skill·capability·context; `execute()` resolves a provider (was `cap.provider||'claude'`,
  recently changed so a pure-`run` capability with `provider:null` needs no LLM). `app/ai/ai-seed.js` (seeded
  providers/behaviours/contexts). `app/ai/ai-capabilities-canvas.js`. `app/ai/host-runtime.js` + `host-serializer.js`.
- **The icon foundry** — `app/ai/ai-glyphic.js`: `glyphic.generate` (LLM → candidate SYMBOL records w/ svg +
  facets{domain,kind,tags}, validated against `CV_GLYPHIC.schema.symbol`) + `glyphic.save` (`CV_ICONS.add`, live).
  `app/ai/ai-glyphic-language.js` (NEW: glyphic.author/read — dual user+AI authoring of meaning).
- **Icons** — `assets/icons/cv-icons.js` (`CV_ICONS`: `data`, `facets` domain/kind/tags, `taxonomy`, `add/get/search`).
  Taxonomy is **under-populated** (`_ingest/ICON-AUDIT.md` flags it). `CV_GLYPHIC.schema.symbol` is the record shape.
- **Meaning** — `assets/icons/cv-meaning.js` (`CV_MEANING`: fields {feeling,senses,type}, loadable profiles,
  `author` API, `referent`/`readGraph`, AND `CV_MEANING.encodings` — the data-field → visual-channel grammar
  with value→appearance maps, the EXISTING precedent for data-binding).
- **Render** — `core/DiagramSolver.jsx` (current SVG node+edge layout; reactflow is a NEW parallel surface);
  `core/cv-nodes.d.ts` (`CVGraph` = {nodes,edges}). The no-script page-face render: `runtime/page_render.py`.
- **Company local models** — `ops/services.json` (chat-4b, embed-pplx [pplx-embed-context-v1-4b], stt-moonshine/
  whisper/parakeet, tts-kokoro; combos like interaction/xsession); role-resolution + concurrent serving via
  `runtime/cognition.py` + the `company` MCP (`run_role`, `models_for_role`, `propose_role`, `edit_role`,
  `cognition_inputs`, `chat`, `corpus`, `ingest`). The **pplx ~0.6b embedder** Tim referenced — verify it exists.
- **Voice/STT** — the Company voice system (STT in, TTS out); `say()` / POST /api/say; the ear (moonshine/whisper/
  parakeet). Find how transcribed speech reaches a live consumer.
- **Resolution / deep-link patterns to FOLLOW** — `_system/refcheck.py` (resolves `code:` refs, fail-loud on drift),
  `_system/symbols.py` + `codeedges.py` (`code://`), `_system/addresses.json` + `parse.py` (the `ui://` registry),
  `contracts/address.py` + `runtime/cognition.py:resolve_address` (the one resolver, 18+ schemes), `runtime/
  relation_types.py` (file-discovered typed edges). These are HOW the system stays un-stale — the live layer copies
  this shape.
- **Data-binding / Supabase** — Supabase is the planned backend (today local). The binding precedent is
  `CV_MEANING.encodings` (data→channel).

## 8 · Open what-ifs (threads to pull)
- Could the extract layer be a *standing* small-model swarm (always-on perception) vs per-utterance calls?
- Does the provider abstraction want to live in `CV_AI` (browser) calling the Company over HTTP, or does the
  Company drive and push graph-deltas to the browser?
- Is reactflow right, or does the freeform/whiteboard feel (tldraw) matter? (Tim chose reactflow — verify fit.)
- How does a bound glyphic (live data) co-exist with a talk-generated one on the same canvas?
- What's the minimum real demo that proves "talk → live graph" end-to-end?

## Closing — spirit note to the agents
Bring **what's actually there**, not what this anchor hopes. If the capability claims (a pplx 0.6b embedder,
structured outputs, realtime latency, reactflow-in-CSP) are rosier than reality, say so with evidence. Find the
existing machinery so we REUSE not reinvent. Find where the no-staleness law would be violated and how to hold it.
Leave the idea bigger, more grounded, more real. Write to your companion file; end with a 3-line summary + the path.
