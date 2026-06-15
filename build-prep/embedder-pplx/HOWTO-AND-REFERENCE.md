# The Embedder-Layer System — How To Use It · Purposes · Reference

*The working reference for the multi-layer embedding model in the instrument/engine. Written for Tim + agents
(both faces). Purposes, how-to, the API, and the honest current state. Living doc — update in place.*

---

## 1. What it is (in one breath)
The same data item can carry **multiple embeddings ("layers")** at once — one per embedder. A BGE-M3 vector AND a
pplx vector for the same `repo` file live side by side. You **choose which layer to read** when you query a lens.
This is Tim's 2026-06-15 reframe: *"multiple different embeddings over the same data"* — keep BGE, add pplx,
add more later, no limit. It is the seed's "one object, many coordinate systems" made literal in the store.

## 2. Why (purposes)
- **Non-destructive upgrade.** Moving to a better embedder (pplx > BGE) doesn't overwrite/destroy the old vectors
  — it *adds a layer*. Nothing breaks, nothing is lost, and it's reversible.
- **Different embedders mean different things.** BGE-M3 brings hybrid dense+sparse+ColBERT; pplx brings 2560-d
  context-aware meaning. Keeping both lets the instrument **compare** them — where two embedders *disagree* about
  the same item is itself a signal (embedder-as-a-lens).
- **The keystone needs a matched pair.** Nucleating content against the operator registry requires the items and
  the type-registry to be in the *same* embedding space — layers make that an explicit, honest choice (and the
  dim guard fails loud on a mismatched pair instead of producing nonsense).

## 3. The mechanism (how it works under the hood)
- **The key.** A vector's storage key carries the embedder via the C1 grammar's `#emb=` fragment
  (`contracts/address.py` already reserved it):
  - default layer (BGE):  `vec://<source>#space=<proj>`            ← `emb=None` (every pre-existing key, untouched)
  - a named layer (pplx): `vec://<source>#space=<proj>#emb=pplx`   ← a NEW key beside the default, never over it
- **The seam.** `FsStore.space_address(source, space, emb=None)` composes the key. `emb=None` returns the exact
  legacy key (byte-identical), so all existing data + readers are unchanged. `build_index(..., emb=)` and
  `embed_corpus_to_spaces(..., emb=)` thread the layer through the write; `put_vector` records the `emb` tag (the
  full model id is in the existing `model` field).

## 4. HOW TO — add a layer (write)
Embed an existing space's items with a different embedder, additively. Pattern (see
`$CLAUDE_JOB_DIR/tmp/write_repo_pplx_layer.py` for a working, chunked, resumable example):
```python
from store.fs_store import FsStore
from runtime.cognition import embed_corpus_to_spaces
from runtime.projections import ProjectionRegistry
store = FsStore("/home/tim/company/.data/store")
embeddable = ProjectionRegistry().discover(["/home/tim/company/projections"]).embeddable()
records = [{"source_address": sa, "text": text, "projection": "repo"}, ...]   # the SAME source_addresses
# CHUNK ~24 records/call: build_index sends the whole batch in ONE round-trip; the slow 4B times out on a big one.
embed_corpus_to_spaces(store, records[i:i+24], embeddable,
                       base_url="http://localhost:8007/v1",
                       model="perplexity-ai/pplx-embed-context-v1-4b", dim=2560, emb="pplx")
```
- It's **incremental** (content-hash diff) → re-running skips done items → **resumable**.
- It's **additive** — writes `#emb=pplx` keys; the BGE (`emb=None`) layer is untouched.
- A backup of the BGE vectors is at `.data/store/vectors.bge-backup-20260615` (the data revert net).

## 5. HOW TO — read a layer (query)
Add `&emb=<layer>` to the projection query. `emb` omitted / `emb=None` = the default (BGE) layer (unchanged).
```
# the keystone on the pplx layer — content typed against the operator registry → candidate new operators:
GET /api/projection?binding=by_nucleation&types_space=operators&space=repo&emb=pplx&rung=8
# any lens on the pplx layer (unit rung), e.g. the semantic field of repo from a chosen centre:
GET /api/projection?binding=semantic&space=repo&emb=pplx&center=<addr>
```
- **Layer-aware lenses (done):** nucleation (items), semantic (units + centre), separator (items + poles).
- The active layer rides back on `binding.emb` in the response.
- **Honesty:** the dim guard drops vectors whose length ≠ the types' dim — so a layer-MISMATCHED pair (e.g. pplx
  2560 types × BGE 1024 items) yields no items → fails loud, never a wrong-but-plausible result.

## 6. The KEYSTONE — registries nucleate into candidate operators (how to use)
- `operators` is a registry-as-a-space: the 29 cognition roles embedded (pplx-native, 2560-d) + a scale pyramid.
- Type real content against it on the pplx layer: `types_space=operators & space=<content> & emb=pplx`.
- **What you get (verified live):** content the operators DON'T cover piles up; a coherent pile is a BORN
  candidate-operator. On `repo`: the `*_acceptance.py` cluster → a candidate "test-verifier" operator; an infra
  cluster (`vram.py`); a voice-deps cluster; + the residue (the corner = needs a new axis).
- **Promotion (L15, the GATE):** a born candidate → a `propose_role` proposal via `/api/registry/proposals` +
  the MCP `propose_role`. The instrument authors (it is NOT read-only — [[feedback-instrument-authors-not-readonly]]);
  the promotion delegates to the engine's write API.

## 7. The LOADOUT + GPU ops (how to operate the embedder)
- The instrument's loadout: `company up @instrument` (bridge + embed-pplx). Combos live in `ops/services.json`.
- The embedder is **pplx-embed-context-v1-4b** on `:8007` (~8.2 GB), custom transformers server
  (`ops/serve_pplx_embed.py`) — it ALSO exposes a native contextual mode (`documents:[[chunk,...]]`), see §9.
- **GPU is 16 GB and tight.** The card holds embed-pplx (8.2) + (when up) a TTS. To free the embedder under load:
  `company down tts-qwen3tts` (drops the ~4.4 GB TTS voice). whisper-STT + rerank-jina are CPU (0 GPU). NOTE: on
  WSL2, a stopped model's VRAM can lag before it's reclaimed; `company restart embed-pplx` cycles the context.
- **Embedding is slow on the 4B (~0.5 s/text) and shared** — keep batches small (~24) and expect contention if
  another session is embedding (e.g. a vitest suite hammering `:8007`). The default embed path degrades-with-
  warning if the endpoint is unreachable (never a silent zero vector).

## 8. CURRENT STATE (honest — 2026-06-15)
- ✅ Store write path layer-aware (`909c122`); nucleation/semantic/separator read at `?emb=` (`dc6a542`,`5938b62`);
  acceptance suite 91/91 at every step (emb=None = byte-identical).
- ✅ Layers live: `operators` (pplx types + pyramid); `repo@emb=pplx` (644); `principles/worldview/topics@emb=pplx`
  (162 each); `history@emb=pplx` (1464 — embedding in background, additive/resumable). BGE layers all intact.
- ✅ Keystone LIVE + FULLY-CONSISTENT on the pplx layer (curl-verified): operators@pplx types × repo@pplx items
  (both emb=pplx) → born candidate-operators; BGE default unchanged.
- ✅ SCALE layer-aware (`b5fd53d`): pyramids built + read per embedder layer. pplx pyramids built for operators
  (rung 8) + repo (64/16/4) + principles/worldview/topics (32/8). The THEME rung + **content-as-types** now work
  at a layer (verified: topics@pplx types × repo@pplx items → born). The whole instrument (units+themes+types) is
  layer-switchable via ?emb=.
- ✅ WHOLE corpus dual-layered: every space (history/repo/principles/worldview/topics/operators) carries BOTH a
  default(BGE) and a pplx layer, each WITH a scale pyramid (history@pplx pyramid 64/16/4 over 1464). Self-describing
  at **`GET /api/layers`** → `{space: [default, pplx]}` (the data a layer-picker / agent reads). `store.layers_by_space()`.
- 🟢 BACKEND LAYER MODEL **COMPLETE** up to the UI: EVERY read path is layer-aware — units, themes, types,
  semantic, separator, nucleation, AND find_relations (the inversion-finder, `?emb=` — verified on pplx + BGE).
  Whole corpus dual-layered + pyramids; keystone + content-as-types live; self-describing (`/api/layers`).
  91/91 throughout, BGE byte-identical (non-destructive).
- ✅ UI LAYER PICKER **BUILT + VERIFIED LIVE** (the `LayerChip`, `surface/app/src/toggles/LayerChip.tsx`): a
  registry-true embedder picker that reads `GET /api/layers` (never a hardcoded layer set — a new embedder layer
  becomes a menu row with ZERO surface edit), mirrors the `LensChip` (paper design system, collapsed at rest,
  hidden when ≤1 layer). Mounted in all three layouts (Desktop/Portrait/Landscape) inside a new `.bar-left`
  OPTICS cluster (lens · layer · centre held together, so the layer never floats into the title slot).
  Verified live at **1440×900 AND 390×844 AND 844×390**: the chip drives `?emb=` on every lens (network-traced
  `binding=semantic…&emb=pplx`), and switching default↔pplx on the keystone (nucleation, topics/topics rung 8)
  VISIBLY re-projects — different born/candidate counts + sectors (pplx 2 candidates/10 sectors vs BGE 3/11).
  The dual interface's HUMAN face now works.
- ✅ MCP DOOR (the TOOL face — parity) **BUILT** (`mcp_face/tools/instrument.py`: `project` + `layers`): the
  SAME engine the surface uses (`Suite.project` → `bridge.build_projection`, ONE resolver extracted so neither
  face reimplements it — reuse-don't-parallel). `project` drives every axis the UI does (binding · space · emb ·
  dim · rung · center · at · pole_a/pole_b); `layers` returns `{space:{emb:dim}}` — the MCP twin of BOTH the
  layer picker (/api/layers) AND the resolution picker's dim source (/api/layer-dims) in one door (so an agent
  can discover layers AND the dim bound for `dim=`). Verified through the `Suite.project` path in-process
  (raw/nucleation/semantic, layer- + MRL-aware, emb/res echoed) + the bridge HTTP face re-verified live
  in-browser. FIX (3b57981): bindings were discovered by a cwd-relative path → every binding fell back to raw
  in the MCP process (cwd ≠ repo root); now absolute, proven across all 8 bindings from a wrong cwd. `layers`
  + the bindings fix load on the next MCP reconnect — then `mcp__company__project` returns the true keystone.

## 9. Capabilities roadmap (the leverage not yet wired)
See MODEL-CAPABILITIES-AS-AFFORDANCES.md. Highest-leverage, all riding on this layer substrate:
- **MRL semantic-zoom** — ✅ VERIFIED graceful + ✅ BUILT on ALL vector lenses (`?dim=<N>` truncates every read
  vector to its first N dims before the cosine — a free, continuous coarse↔fine meaning zoom; the 2-D scale:
  rung × dim). Nucleation (`5dd6a14`) + NOW semantic + separator (this beat): the truncation is applied
  CONSISTENTLY to centre/poles + all items so `_cosine`'s dim-mismatch guard never trips; the separator's fifth
  gate then runs AT the chosen resolution; `binding.res` echoes the active dim on every path. VERIFIED applied
  on EACH vector lens (not pattern-matched, through build_projection full↔128d): nucleation visibly
  (1 born/3 cand/11 sectors → 0/2/10); semantic — 11/12 radii move + NN-order changes; separator — 12/12 leans
  move. MRL gracefulness (repo@pplx): dim1024 cos-corr 0.98/NN 86% · 512 0.96/79% · 256 0.92/72% · 128 0.86/61%.
  `dim=None`=full (byte-identical). ✅ The FE resolution PICKER is BUILT (`surface/app/src/toggles/ResChip.tsx`, `◎ full ▸`):
  registry-true — its ladder is DERIVED from the active layer's full dim (`/api/layer-dims` →
  `store.layer_dims()` → `{space:{emb:dim}}`), powers of two below it, never hardcoded; appears ONLY on the
  vector lenses (a `space` in the binding), hidden on structural ones. Verified live (desktop+portrait): on
  topics@default(BGE 1024) it offers full·1024d·512·256·128·64; picking 128d VISIBLY re-projects the keystone
  (1 born/3 cand/11 sectors → 0/2/10 — coarser dim = broader membership). The 2-D scale (rung × dim) is now
  fully drivable by sight + by `?dim=` on every vector lens. NB "axis" here = a DRIVABLE axis (rung, dim) —
  Tim's broader FOUR ROOT AXES are a separate sense; these are likely sub-types under them. See the glossary:
  `../universal-projection/GLOSSARY.md` · memory [[the-four-root-axes]].
- **Binary quantization** — 32× smaller, Hamming similarity → show the WHOLE corpus at once; detail-on-zoom.
- **Context-aware (late-chunking)** — the `:8007` `documents` mode embeds an item in its parent's context;
  proven SELECTIVE (it homogenizes a heterogeneous registry — helps retrieval, hurts differentiation; see §2a of
  LEVERAGE-AND-TOOL-REQUESTS.md). A per-cohesive-parent tool, never blanket.
- **The clean long-term home** for layers = the Postgres `layers` table (DATA-SUBSTRATE-POSTGRES-SUPABASE.md):
  one item row, many layer-vectors — no `#emb=` flat-key duplication, plus realtime + cloud.

## 10. Pointers
- Vision + threads: VISION-OVERVIEW.md · INSTRUMENT-DUAL-INTERFACE-AND-LAYERS.md · MODEL-CAPABILITIES-AS-AFFORDANCES.md
- Substrate plan: DATA-SUBSTRATE-POSTGRES-SUPABASE.md · Leverage/migration: LEVERAGE-AND-TOOL-REQUESTS.md
- Keystone state: ../instrument-surface/EQUATION-AUDIT.md (§7) · ../instrument-surface/STATUS.md
- Memory: [[project-embedding-model-decision]] · [[feedback-instrument-authors-not-readonly]]
