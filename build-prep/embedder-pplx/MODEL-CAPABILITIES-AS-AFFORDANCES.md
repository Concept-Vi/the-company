# Every Model Capability → an Instrument Affordance (dual-face) + my ideas + connections

*Stretched out from Tim's 2026-06-15 think-aloud ("this was also just one capability… lots of other capabilities
worth exposing with the instrument… think of all of the capabilities of the model, your thoughts and ideas, what
it connects to"). Tim supplies the WHY/where; I supply the per-capability depth. Living doc.*

The frame (from INSTRUMENT-DUAL-INTERFACE-AND-LAYERS.md): every capability is a way to **choose a frame to read
the data in**, exposed on BOTH faces (a visual affordance for Tim · an MCP tool for agents), held to the FORM
bar (minimal, spatial, non-developer). Each entry: *what it is · the dual affordance · my idea/extension · the
connection.*

---

## A. Dense embedding — the base semantic space  (HAVE; the floor)
- **Is:** pplx-4B dense vectors (2560-d) — the meaning-space nucleation/strain/find_relations already read.
- **Affordance:** already the wheel's circle (radius = relevance, angle = kind). No new work — the quality is
  the upgrade (pplx > BGE-M3).
- **Connection:** the seed's circle (meaning). The migration (DATA-SUBSTRATE / leverage §4) just makes it sharper.

## B. Context-aware reading (late-chunking) — a SELECTIVE framing layer  (HAVE; proven selective)
- **Is:** embed a thing *in the context of its parent thing* (the `:8007` `documents` mode). Proven (leverage
  §2a): homogenizes a heterogeneous registry → hurts differentiation; helps disambiguation/retrieval.
- **Affordance:** **"read in the context of ___"** — a frame-choice (UI: pick a parent on the wheel → re-read
  the children in its context, as a new layer; MCP: `embed(context_parent=…)`). Because it's selective, it is a
  *layer the operator chooses*, never the default — exactly Tim's "selective use… whatever ways I want."
- **My idea:** a context-frame can be ANY grouping, not just the structural parent — *"read these in the context
  of THAT set"* (read the principles in the context of the roles; read this session's units in the context of
  last week's). Context becomes a **comparative frame** — and a comparative frame is a POLE (see G9): the
  two-gravity separator's poles could be two CONTEXTS. Context-as-pole is a real new lens.
- **Connection:** the seed's origin/frame selection (§8); the separator (G9); address-accumulation (each context
  read is a layer).

## C. MRL / Matryoshka — SEMANTIC-RESOLUTION ZOOM  (HAVE in the model; unexposed — high potential)
- **Is:** the 2560-d vector is *truncatable* — the first 1024 / 512 / 256 dims are themselves a valid (coarser)
  embedding. One embed, many resolutions, free.
- **Affordance:** a **"meaning detail" dial** — slide from coarse (256-d: broad gist, fast, fewer distinctions)
  to fine (2560-d: full nuance). UI: a continuous zoom on the meaning axis; MCP: `read(dim=…)`.
- **My idea (a real one):** this is a SECOND, orthogonal scale axis. The rung pyramid (G11) zooms *cluster
  granularity* (how many groups); MRL zooms *representation resolution* (how much nuance per point). Together
  they make a **2-D scale control**: `rung × dim`. Coarse-rung + coarse-dim = the executive overview; fine-rung
  + fine-dim = the microscope. No other instrument I know exposes both. This is the seed's scale/recursive-zoom
  (§2) given two real knobs. And MRL is *free* (truncation), so it's a cheap, continuous, always-available zoom.
- **Connection:** the seed's scale axis; G11 (rung pyramid); render-for-cognition (a dial the eye drives).

## D. Native INT8 / binary quantization — SCALE vs PRECISION  (HAVE in the model; unexposed)
- **Is:** the model emits int8 (4× smaller) and binary (32× smaller) natively, quantization-aware-trained
  (binary loses <1.6 pts at 4B). Binary similarity is Hamming distance (bitwise, blazing fast).
- **Affordance:** a **precision/scale mode** — fp/int8 for nuance, binary for *reach*. UI: not a user-facing
  dial so much as what it UNLOCKS (below); MCP: `read(quantization=…)`, storage-mode per space.
- **My idea (high potential):** binary embeddings let the instrument show the **WHOLE corpus at once** — the
  wheel currently caps ~600 points; with 32× compression + Hamming, *every event* (tens of thousands) becomes
  drawable and clusterable in real time. Binary for the all-of-it overview → switch to fp/int8 when you zoom
  into a region for nuance. "Scale view in binary, detail view in float" — precision follows attention. This is
  how the instrument scales from a sample to the entire memory without lying about coverage.
- **Connection:** the scale pyramid (binary makes full-corpus pyramids cheap); no-silent-caps (binary removes
  the 600-cap that silently truncates today); the live spine at scale (DATA-SUBSTRATE).

## E. 32K context window — embed LARGE composites whole  (HAVE; was 8192 on BGE)
- **Is:** up to 32,768 tokens per read (vs BGE's 8,192) — long units never truncated.
- **Affordance:** **"embed the whole thing as one"** — a long file, a whole thread, an entire small registry,
  a composed document — read as a single point, not chopped. UI: a unit-granularity choice (point = unit / file
  / thread / registry); MCP: just works (no truncation).
- **My idea:** combined with context-mode (B), 32K lets you embed *a parent WITH all its children in one window*
  — the late-chunking that actually has room to see the whole parent. The window size is what makes "a thing in
  the context of its (large) parent" feasible at all.
- **Connection:** the seed's multi-granularity; the unit/scale choice.

## F. No instruction prefix — PURE-CONTENT meaning  (HAVE; a simplification + a property)
- **Is:** unlike most modern embedders, pplx needs no `"query:"/"passage:"` prefix. The embedding is of the
  content itself, no prompt bias, no indexing/query drift.
- **Affordance:** nothing to expose — it's a *removal* of friction + a *cleanliness* property: the meaning-space
  is the content's own, not an artifact of a chosen instruction. Tim's instrument shows *the data's* geometry.
- **Connection:** registry-is-truth (no hidden prompt shaping the space); the no-green-paint ethos (the space is
  honest content-meaning).

## G. Dense vs context VARIANTS — a reading-mode toggle  (HAVE both at 0.6B/4B)
- **Is:** `pplx-embed-v1` (isolated dense) and `pplx-embed-context-v1` (in-context). The server has the context
  one; the dense behaviour is the `input` (single-chunk) path.
- **Affordance:** **isolated-meaning ↔ in-context-meaning** as two reading modes (a layer kind each). Most lenses
  want isolated (differentiation); retrieval/disambiguation lenses may want in-context. The operator picks.
- **My idea:** the *difference* between an item's isolated vector and its in-context vector is itself a signal —
  **"how much does context change what this means?"** That delta is a new kind of STRAIN (context-strain): a
  thing whose meaning shifts a lot in its parent's presence is context-dependent; one that doesn't is
  context-free. The instrument could render context-strain exactly like structure↔meaning strain (G7). A second
  tension axis, free from the two variants.
- **Connection:** G7 strain (the delta-as-tension pattern); B (context); the seed's translation-loss.

## H. Multilingual (30 languages) — cross-lingual proximity  (HAVE; latent)
- **Is:** one shared space across ~30 languages — a concept in English sits near its expression in another tongue.
- **Affordance:** latent now (the corpus is English). Future: a thing near its cross-lingual kin; a
  language-agnostic meaning-space. MCP: just works on non-English input.
- **Connection:** future reach; the universal-meaning-space property.

## I. The embedder LOADOUT — embedder-as-a-lens  (the bigger frame; [[mode-loadout-registry]])
- **Is:** pplx is one embedder; Tim wants a *purpose-loadout* — code, visual, long-arc, scale embedders — not one
  winner. Each embedder is a different *way of meaning*.
- **Affordance:** **"which meaning?"** — the embedder itself becomes a frame-choice / a lens. Read the data
  through the code-embedder vs the prose-embedder vs pplx → different geometries of the same items (different
  layers). UI: an embedder picker (like the lens picker); MCP: `read(embedder=…)`.
- **My idea:** embedder-choice is the *outermost* frame — above context, resolution, centre. The same item read
  through two embedders = two layers whose *disagreement* is informative (where do "code-meaning" and
  "prose-meaning" of a file diverge?). The loadout turns the instrument into a *comparative meaning microscope*.
- **Connection:** [[mode-loadout-registry]]; [[native-model-layer]]; the @instrument loadout (services.json); the
  multi-layer model (each embedder = a layer dimension).

---

## The synthesis — the instrument's control vocabulary (all of the above, as ONE surface)
Every capability is a knob in **one frame-chooser**, each a layer when kept, each on both faces:

| Frame knob | Coarse ←→ Fine / A ←→ B | the capability |
|---|---|---|
| **embedder** | code · prose · pplx · visual | I (loadout) |
| **reading mode** | isolated ←→ in-context | B, G |
| **context-parent** | (none) ←→ chosen parent/set | B |
| **resolution (dim)** | 256 ←→ 2560 | C (MRL) |
| **precision** | binary ←→ int8 ←→ fp | D |
| **cluster scale (rung)** | themes ←→ units | G11 (have) |
| **centre / poles** | root ←→ chosen origin / two gravities | have (G3/G9) |
| **time** | past ←→ now | have (G3) |
| **unit granularity** | registry ←→ file ←→ chunk | E |

The instrument is the place an operator (Tim by sight, an agent by MCP) sets these knobs, reads the data in that
frame, sees it as a lens, and keeps it as a layer. Most are *free* off one embed (MRL, precision, rung, centre,
time); a few need a re-embed (embedder, reading-mode, context-parent) → a new layer. THAT is the "read the same
data heaps of times, in all sorts of ways" Tim described — made into a finite, legible control vocabulary.

## My biggest-leverage picks (where I'd point the energy)
1. **MRL semantic-zoom (C)** — free, continuous, orthogonal scale axis; pairs with the rung pyramid into a 2-D
   zoom. Cheap to expose, high cognitive payoff.
2. **Binary-scale full-corpus view (D)** — removes the silent 600-cap; lets the instrument honestly show the
   whole memory and zoom to detail. Unlocks scale.
3. **Embedder-as-a-lens / the loadout (I)** — the comparative meaning microscope; the deepest long-arc capability.
4. **Context-as-pole + context-strain (B/G)** — turns the proven-selective context feature into two genuinely new
   lenses (comparative-context, context-dependence-as-tension).
