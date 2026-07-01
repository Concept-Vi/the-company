---
type: analysis
register: descriptive
status: unconfirmed
aliases: [READ-4 Company Cognition Code, A-fusion Company side]
tags: [glyphic-language, A-fusion, cognition, model-resolution, embedder, roles]
coverage: {files_read: 20, files_total: many, last_read: 2026-07-01}
---

# READ-4 — The Company Cognition + Model-Resolution Code (the fusion's Company side)

**What this is:** a first-hand, file:line map of the *real* surface the design-system AI must fuse
with and reach — how a role resolves to a model, how to fire a role with structured output, how to
embed text (for meaning→glyph), how to query the corpus, and how a new `glyph_extract`/`glyph_compose`
role would be added. Read READ-ONLY against a live tree (`~/company` never modified).

**Register discipline (Tim's evidence law):** every claim is tagged **OBSERVED** (read in code),
**INFERRED** (pattern-matched, unverified), or **BUILT-BUT-DORMANT / STALE** (the built-vs-dormant
honesty the task demands). Nothing is asserted as "working" without a verification path named.

---

## 0. The one-paragraph shape (relational)

```
design-system AI  →  MCP face (mcp_face/) OR HTTP surface  →  Suite (runtime/suite.py)
                                                                  │
        ┌─────────────────────────────────────────────────────┴───────────────────────┐
        │                                    │                                          │
   FIRE A ROLE                          EMBED TEXT                              QUERY THE CORPUS
   run_role(role, ctx)                  run_role(op=embed)                      query_corpus / query_hybrid
   → validated JSON dict                → {vector,dim,model}                    → ranked [{id,score}]
        │                                    │                                          │
        └── role resolves to a model via ────┴── the embedder is a SEPARATE endpoint ───┘
            resolve_role_binding (LIVE)          pplx-embed @ :8007, 2560-dim (config-driven)
            role.requires ⊆ model.provides       (NOT the chat brain — its own service)
```

One circuit: **a ROLE is a named model-function** (runtime/roles.py:3). The design-system authors a
role by dropping a file; the role declares `requires`; the system resolves it to a live model; firing
it returns validated JSON (or, for op=embed, a vector). Meaning→glyph is: embed text → query a glyph
space. **The glyph space does not exist yet** (§C-gap) — that is a fusion build item, not an assumption.

---

## A. The EXACT API a browser / design-system calls

**Two faces onto the SAME engine (OBSERVED):**
- **MCP face** — `mcp_face/server.py` (+ `mcp_face/tools/*.py`), the tools the design-system agent
  calls over MCP (`mcp__company__run_role`, `…__corpus`, `…__ingest`, `…__models_for_role`,
  `…__cognition_info`, `…__propose_role`, `…__find_relations`).
- **Browser HTTP surface** — `runtime/bridge.py @ http://localhost:8770` (bridge.py:7). It binds the
  **SAME FastMCP tool manager** to its own Suite (bridge.py:587,602-608), so a browser reaches the same
  tools + `/api/*` routes. A glyph UI in the browser and an MCP agent hit ONE engine.

**The return envelope (OBSERVED, cognition.py:321-325):** the MCP `run_role` tool wraps the engine
result as **`{role, op, output, address, turn_id}`** (server.py:727) — the `output` field carries the
role's validated dict. In-engine callers (run_swarm, rules) read the validated dict straight off
`run_role`'s return with no envelope.

### (i) Run a role with STRUCTURED OUTPUT

**MCP tool — OBSERVED** `mcp_face/server.py:690`
`run_role(role: str, utterance="", op="generate", model="", inputs: dict={}, max_tokens=256,
temperature=0.0, ensure=False, ensure_evict=False, policy="", think: bool|None=None,
coordinate: dict|None=None) -> {role, op, output, address, turn_id}`. `role` = a registered role id;
`inputs` = extra declared inputs (an address-valued input `run://`/`cas://`/`skill://`/`context://` is
RESOLVED via `resolve_address` before the run; a literal is used as-is, server.py:755-761); `model`
overrides the role's bound model. The GENERATE output is PERSISTED to `run://<turn>/<role>` (inspectable
back via `inspect_address`). Delegates to the engine `run_role`.

**Engine entry — OBSERVED** `runtime/cognition.py:313` `run_role(role, ctx, *, base_url, model,
timeout, max_tokens, temperature, store, ensure, ensure_evict, policy, meta, think, coordinate)`.

- The role carries an `output_schema` (a Pydantic `BaseModel` subclass). `run_role` sets
  `json=True` and passes `schema=eff_schema` into `client.complete(...)`, which parses + validates +
  retries a malformed output client-side (cognition.py:612-616). **Return = the role's validated
  output dict DIRECTLY** — e.g. a `screen_reader` fire returns `{"what_this_is": …}`, NOT
  `{"output": {…}}` (cognition.py:321-325). The `{output, address}` nesting is the MCP-face wrapper only.
- **THE #1 FUSION GOTCHA — GUIDED-JSON ⊥ THINKING (OBSERVED, root-caused 2026-07-01, cognition.py:482-490):**
  a schema-constrained fire (`response_format=json_schema`) forces valid JSON from the first token — the
  model *cannot* emit `<think>…</think>` tokens (illegal under the grammar), so a **thinking-ON schema
  fire degenerates to empty content and burns all retries**. Therefore a schema fire **defaults to
  no-think** unless the caller/role explicitly asked to think. **Design rule:** a glyph role that emits
  structured JSON runs no-think; a glyph role that must REASON should emit **free-text** (no
  `output_schema`) and reason there. Do not set `thinking:true` on a schema role.
- **GOTCHA #2 — the structured-output use-gate (OBSERVED, cognition.py:519-534):** the bound model
  must declare `json_schema=true` in its capability catalog, else `run_role` **fails loud** (never
  silently downgrades to bare `json_object`). Both live residents (AWQ 4B + FP8) declare
  `json_schema.value=true` (cognition.py:517-518 comment), so there is no resident regression. →
  glyph roles must bind a `json_schema`-capable model (the resident chat models are).
- **GOTCHA #3 — the schema-fire loop-breaker (OBSERVED, cognition.py:588-600):** on a schema fire,
  `run_role` injects `presence_penalty=1.0` (the greedy+guided-JSON loop this Qwen build hits). This is
  automatic; a role that declares its own `presence_penalty` wins. Design-system need not do anything —
  just know the fire is not naive.

### (ii) Embed text (for meaning→glyph semantic resolution)

- **OBSERVED** — an **embed role** (`op:"embed"`, roles/embed.py) fired via `run_role`: it takes the
  vector path (`complete_embeddings`) and returns **`{"vector", "dim", "model"}`**
  (cognition.py:408-427). No prompt/schema needed. LOCAL resident embedder only — no cloud embeddings.
- Endpoint + dim are **config-driven, not hardcoded** — `fabric/config.py:39-40,50`:
  `DEFAULT_EMBED_URL = http://localhost:8007/v1`, `DEFAULT_EMBED_MODEL =
  perplexity-ai/pplx-embed-context-v1-4b`, `DEFAULT_EMBED_DIM = 2560`. A wrong-length vector FAILS
  LOUD at the fabric (config.py:48-50).
- **EMBEDDER-DOWN semantics (OBSERVED):** a single embed fails loud (FabricError after retries,
  cognition.py:411-412). `ensure=True` (opt-in) asks the gated actuator to make the embedder resident
  first (cognition.py:414-421) and may return a swap-approval ASK the caller surfaces.
- **THE END-TO-END GAP for meaning→glyph (OBSERVED, cognition.py:650-654):** `run_role(op=embed)`
  *produces* a vector but **does NOT persist it into a queryable SPACE**. Semantic meaning→glyph
  resolution needs a **glyph projection space** populated (`embed_corpus_to_spaces`, cognition.py:676)
  and queried (`query_corpus`/`query_hybrid`). **No glyph space exists** — §C-gap.

### (iii) Query the corpus

**MCP tool — OBSERVED** `mcp_face/tools/corpus.py:19`
`corpus(op: Literal["query","list","find","read","neighbours","determine"], project="", kind="",
projection="", source_address="", address="", text="", space="", k=8, rerank=False, top_n=0,
emb="pplx", min_score=0.0, detail="concise", limit=50, asset="full", min_strong=0, mode="semantic")`.
- **`op="query"`** — ask the corpus a NL question. `text` required; `space` = an embeddable space; `k` =
  count. **`mode="semantic"`** (default) = cosine top-k (→ `suite.query_corpus`, corpus.py:117);
  **`mode="hybrid"`** = RRF late-fusion (→ `corpus_fusion.query_hybrid`, corpus.py:106-113). `rerank=True`
  (opt-in) adds a **jina-v3 cross-encoder** precision pass (`ops/rerank.py @ :8008`, CPU/0-VRAM,
  corpus.py:41-43,124-133). `detail="detailed"` inlines each hit's record content. Every hit id is
  `op="read"`-able.
- **`op="determine"`** — GROUNDED themes over the dragnet extraction layer (embed-search → jina rerank →
  model clusters REAL claims by index, never generates claim text; carries no_fiction + relevance
  assessment, corpus.py:56-71). The full-coverage recall surface, distinct from cosine `query`.
- **`op="read"/"list"/"find"/"neighbours"`** — read one record / list / filter / the neighbour node-field
  around a unit (corpus.py:48-79).

- **Engine — OBSERVED** `runtime/suite.py:11506` `Suite.query_corpus(text, *, space=None, k=8) -> {query,
  space, ranked:[{address, score, ...}], note?}`. It EMBEDS `text` via `_embed_consult_query`
  (suite.py:5189 — which uses `DEFAULT_EMBED_URL/MODEL/DIM`, i.e. the **live pplx @ :8007, 2560-dim**,
  suite.py:5198-5200) then ranks the space-keyed vector index (`vector_index.query_index(space=)`).
  **Vector (meaning) leg.**
- **OBSERVED** `runtime/corpus_fusion.py:149` `query_hybrid(suite, text, *, space, k=10, weights,
  rrf_k, lex_fetch, vec_fetch) -> {mode:'hybrid', legs_used, ranked:[{id, score, legs, why}],
  degraded?}`. Fuses a **vector leg** (query_corpus, meaning) + a **lexical leg** (substrings over the
  same space's digests) by **Reciprocal-Rank Fusion** (rank-only, never score — the scale-mismatch law,
  corpus_fusion.py:12-17). Degrades honestly to lexical-only when the embedder is down and SAYS so in
  `legs_used`/`degraded`.
  - **BUILT-BUT-UNVERIFIED (honesty):** the RRF math is pure and verified; the **end-to-end hybrid over
    a live space is UNVERIFIED pending the embedder** (matches the mission memory: "PURE-MATH verified,
    end-to-end UNVERIFIED"). Do not present hybrid as proven-live.

### (iv) Populate / reindex a space (the glyph-space fill + freshness)

**MCP tool — OBSERVED** `mcp_face/tools/ingest.py:18`
`ingest(op="ingest", roots=[], paths=[], project="company", session="ingest", round="1", space="repo",
max_files=50, force=False, retract_extra=False)`.
- **`op="ingest"`** — walk files → digest-fan on the swarm → capture+embed into `space` so
  `corpus(op="query", space=…)` can answer. Batched (`max_files`, `remaining`), incremental (`force`).
  → `suite.ingest_paths(...)` (ingest.py:83).
- **`op="reindex"`** — reconcile a space's vector index against its CURRENT source (embed
  missing/changed, retract orphaned) → `freshness.reconcile_space` (ingest.py:51-77). The **on-demand
  twin** of the auto freshness daemon (`bridge.py:_freshness_loop`, which mtime-polls only `extractions`).
  A glyph space would be filled via ingest/embed and kept fresh via reindex.

### Model / capability discovery tools (for the design-system to pick a model)

- **OBSERVED** `mcp_face/server.py:506` `models_for_role(requires: str="", role: str="") -> {requires,
  models[], providers{}}` — which model-ids can serve a role that requires X, plus the live providers.
- **OBSERVED** `mcp_face/server.py:426` `cognition_info(section="", role="", detail="concise")` — the
  live cognition registries (roles + facets, casts, juries, **spaces**, event-contract). A glyph UI reads
  `cognition_info().spaces` to know which embeddable spaces exist (registry-is-truth, never hardcoded).
- **OBSERVED** `mcp_face/server.py:1043` `propose_role(spec: dict)` (+ `edit_role`/`delete_role`) — author
  a glyph role over the wire (validated by import-in-a-temp-dir before it reaches `roles/`).
- **OBSERVED** `mcp_face/server.py:1200` `find_relations(item, near_space, far_space, k=10,
  min_score=0.5)` — the cross-space inversion-finder (needs the item embedded in BOTH spaces first).

---

## B. Role-resolution — how a role maps to a model; concurrency; the honest latency reality

### The LIVE resolution path (what actually fires today)

```
Suite.resolve_role_binding(role_id)               [suite.py:6400 — OBSERVED]
   → roles.resolve_binding(role, capability_providers())     [roles.py:398]
        → role.requires ⊆ provider.provides   (model_satisfies, roles.py:391)
   returns {model, base_url, provider, requires, provides, satisfied, candidates}
```

- **OBSERVED** `Suite.capability_providers()` (suite.py:6331) enumerates **every registered model
  service** in `ops/services.json`, derives each one's `provides` from the capability catalog
  (`ops/cli/capabilities.py:provides_for`), marks a `resident` flag from the live GPU card, and sorts
  **residents first** so a binding prefers a live provider (suite.py:6387-6392). Shape:
  `{provider_id: {model, base_url, provides:[caps], resident}}`.
- **OBSERVED** `Suite.models_for_role(requires) -> {requires, models[], providers{}}` (suite.py:10930)
  — the MODEL-SELECT a UI uses to ask "which models can serve a role that requires X?" (registry-is-truth;
  a new model with the right `provides` is automatically a candidate).

### ⚠ THE `satisfied` FLOOR TRAP (the exact trap the task named — OBSERVED)

`roles.resolve_binding` (roles.py:415-427) does **NOT** raise when no provider matches a role that
declares a `default_model` — it returns the **default** with **`satisfied=False`** (the brain FLOOR).
`model_routing.py:22-27` documents this as the "no-green-paint" trap: *a role re-tier can "look
resolved" because it silently floored to the resident 4B while the intended cloud brain was never a
live provider.*

> **DESIGN RULE for the fusion (verbatim from model_routing.py:27):** **assert `satisfied == True`,
> NOT the truthiness of `model`.** A glyph role that must run on a specific model and gets
> `satisfied=False` has NOT resolved — it floored. (Note: `element_fit_lens`/`screen_reader` declare
> `"default_model": None` — the safe floor to the resident brain, which is what a glyph role wants
> UNLESS it needs a specific non-resident model.)

### `resolve_model` — BUILT-BUT-DORMANT (do not route through it yet)

**OBSERVED** `runtime/model_routing.py:105` `resolve_model(intent, *, suite) -> {model, base_url,
provider, why, satisfied, ...}` is **the intended ONE model-selection resolver** (unifies the three
scattered seams: role→provider, capability→provider, clone-context-pick). **But it is Phase-1 DORMANT:**
*"NOTHING is routed through it yet"* (model_routing.py:13-15). The LIVE role→model path a browser reaches
is `resolve_role_binding`; `run_role`/`run_swarm` default to the **RESIDENT sentinel** (cognition.py:58-59)
which resolves at call-time to whatever brain is **actually loaded** via `active_brain()`
(cognition.py:69-108, resolved in run_role at :401-406). → **The fusion should call
`resolve_role_binding`/`models_for_role`, not `resolve_model`, until Phase 2 wires the live paths.**

### Concurrency — run_swarm / run_items (the honest knee reality)

- **OBSERVED** `run_swarm(roles, ctx, store, *, turn_id, budget, ...)` (cognition.py:1451) fires **N
  different roles over 1 ctx CONCURRENTLY** (N roles × 1 ctx), bounded by a registry slot budget
  (`SlotBudget`, swarm sub-pool = `swarm_slots`), each writing to its own `run://<turn>/<role>`
  address, joining at a barrier, reading every value back. Fires the **blocking transport on pool
  threads** (GIL releases on socket I/O; vLLM batches server-side) — no async. N independent roles
  finish in ~max(role) not ~sum(role) (cognition.py:1465-1466).
- **OBSERVED** `run_items(role, items, store, *, turn_id, ...)` (cognition.py:1599) INVERTS the axis:
  **1 role × N units** (the map half of the corpus-chain — a glyph_extract role over N text chunks).
  Same gate, same barrier, per-unit fail-loud + resilience (a poison unit lands in `.failed`, good
  units still return). **MCP tool — OBSERVED** `mcp_face/server.py:849`
  `run_items(role: str, items: list, max_tokens=256, temperature=0.0)`.
- **OBSERVED — `run_reduce` (the JOIN half; likely `glyph_compose`'s primitive)** `cognition.py:2398`
  `run_reduce(addresses, store, *, turn_id, mode, role=None, reduce_rule=None, cluster_threshold=0.85,
  on_missing="raise", embed_fn=None, ...)`. The **cross-unit REDUCE** — reads a set of map-output
  `run://` addresses back (fail-loud on missing) and JOINs them into ONE output by a declared `mode`:
  - **`mode="role"`** — the SYNTHESIZE join: composes the N read-back outputs into ONE labelled input
    (`[unit_id] <json>` lines, cognition.py:2468) and fires a **reduce-role** (a generate role declaring
    `input_addresses=("notes",)`, e.g. `roles/reduce_synth.py`) → ONE synthesized output (cognition.py:2458-2475).
  - **`mode="rule"`** — a deterministic L2 join (a PURE callable over the N values — vote/merge/select;
    no model, cognition.py:2477-2485).
  - **`mode="cluster"`** — the embed-cluster "which of these are the same" join: embeds each unit's
    read-back text and groups by cosine-nearness (cognition.py:2487-2494).
  **This is the primitive `glyph_compose` composes a meaning-FIELD with** — glyph meaning is
  combinatorial/a field, not single, so composing N mark-meanings into one glyph reading is a
  `run_reduce(mode="role")` over a `run_items(glyph_extract, marks)` map. **MCP tool — OBSERVED**
  `mcp_face/server.py:917` `run_reduce(addresses: list, mode: Literal["role","rule","cluster"],
  role="", reduce_rule="", ...)` — so the map→reduce corpus-chain is fully callable from the fusion.
- **⚠ run_swarm is a SINGLE-MODEL wave + NOT an MCP tool (OBSERVED, added 2026-07-01):** `run_swarm`
  takes ONE `model=` for the whole wave (cognition.py:1454) — every role in it hits the same model, so
  a swarm **cannot** give two glyph roles two different models. And it is **not exposed as an MCP tool**
  (only `run_role`/`run_items` are, server.py:690/849) — it is an internal driver (the staged-turn
  voice circuit). The design system's callable fans are `run_role` (one) and `run_items` (1×N).
- **⚠ THE FIRE PATH DOES NOT APPLY THE CAPABILITY BINDING (OBSERVED, added 2026-07-01 — the
  load-bearing honesty finding):** the MCP `run_role`/`run_items` tools **never call
  `resolve_role_binding`** to derive a per-role model. `_fire_role_and_persist` (server.py:736) passes
  `model=` to the engine **only if the CALLER supplied one** (server.py:768); otherwise the role fires
  at the RESIDENT sentinel → `active_brain()` (cognition.py:401-406). So a glyph role's declared
  `model_binding.requires` is **declared-but-inert on the fire path** — the role runs on the resident
  brain regardless. `resolve_role_binding`/`models_for_role` are READ-ONLY lookups ("which model *would*
  fit"), not applied at fire. **Design consequence:** if a glyph role must run on a specific model, the
  fusion MUST pass `model=` explicitly on every `run_role` call — it cannot rely on the role's
  `requires` to route it, nor on `run_swarm` for per-role models.
- **HONEST LATENCY / KNEE (OBSERVED, real numbers added 2026-07-01):** `ROLE_TIMEOUT` default **600s**
  (cognition.py:66) — a hang-guard, not a concurrency gate (vLLM owns admission/queuing). The knee is
  COMPUTED from live registry values (`SlotBudget.from_registry`, cognition.py:1025), never a hardcoded
  32: `knee = min(max_num_seqs − R, free_KV // per_role_ctx)`, `swarm_slots = max(1, knee)`, R=2 reserved,
  per_role_ctx=1500 tok. **On the resident `chat-4b` today** (services.json: `Qwen3.5-4B-AWQ-4bit` @
  :8000, `max_num_seqs=4`, `gpu_util=0.55`): `seq_bound = 4−2 = 2`; KV falls back to the C0.5-measured
  `66036 @0.49` (0.55 isn't in the measured map) → `kv_bound = 44`; so **`knee = min(2, 44) = 2` →
  `swarm_slots = 2`**. **A glyph fan runs only ~2-wide on this loadout.** The `chat-4b-fp8` loadout
  (:8001, `max_num_seqs=32`, gpu_util=0.9) lifts it to ~30 — concurrency is a function of *which brain
  is resident*, and a swap rebuilds the gate (cognition.py:1085). `concurrency_probe(n)`
  (cognition.py:923) is the live measurement (p50/p95/max) — run it, don't guess. → A glyph batch (many
  marks → run_items) is bounded, resilient, and will not starve the interactive brain.

---

### The model service tiers (ops/services.json — OBSERVED)

| service | port | model | note |
|---|---|---|---|
| `chat-4b` | 8000 | `cyankiwi/Qwen3.5-4B-AWQ-4bit` | the RESIDENT default brain (the sentinel resolves here) |
| `chat-4b-fp8` | 8001 | `RedHatAI/Qwen3.5-4B-FP8-dynamic` | the everyday FP8 loadout brain |
| `chat-9b-fp8` | 8002 | `RedHatAI/Qwen3.5-9B-FP8-dynamic` | larger brain tier |
| `chat-2b` / `chat-08b` | 8003 / 8006 | Qwen3.5-2B / 0.8B | small tiers |
| `chat-nemotron` | 8005 | NVIDIA-Nemotron-3-Nano-30B | large AWQ tier |
| **`embed-pplx`** | **8007** | **`perplexity-ai/pplx-embed-context-v1-4b`** | **THE LIVE EMBEDDER — 2560-dim, custom transformers server (NOT vLLM), vram 5700MB, `serve_pplx_embed.sh`, systemd `company-embed-pplx.service`** |
| `embed-bge` | 8001 | `BAAI/bge-m3` | 1024-dim — **DORMANT** (endpoint down; vectors survive at bare layer) |
| `embed-jina-v5` / `embed-qwen3` | 8004 | jina-v5-small / Qwen3-Embedding-8B | the deliberate **hot-swap sibling** on 8004 (NOT a collision — one served at a time) |
| `rerank-jina` | — | jina-v3 cross-encoder | the `:8008` rerank precision stage (corpus rerank/determine) |

> Which brain fires is resolved at call-time by `active_brain()` (cognition.py:69-108) — it reads the
> live GPU card + `rhm_config` and returns whichever brain-group service is actually RUNNING, preferring
> the RHM's brain so swarm ≡ RHM. So the fusion never pins a port; it follows the live loadout.

## C. The embedder — served model, dim, endpoint, how to call it

| Fact | Value | Evidence |
|---|---|---|
| Served model | `perplexity-ai/pplx-embed-context-v1-4b` | fabric/config.py:40 (OBSERVED) |
| Endpoint | `http://localhost:8007/v1` | fabric/config.py:39 (OBSERVED) |
| Dim | **2560** (INT8) | fabric/config.py:38,50 (OBSERVED) |
| How to call | `run_role(op=embed)` → `complete_embeddings` via `openai_embeddings_transport(base_url=DEFAULT_EMBED_URL)` | cognition.py:423-427 (OBSERVED) |
| Default emb LAYER | `pplx` (the live 2560 storage layer) | fabric/config.py:55 (OBSERVED) |
| Failure | down/empty/dim-mismatch → **FabricError, fail loud** | cognition.py:411-412 (OBSERVED) |

**⚠ STALE-COMMENT HONESTY FINDING (not a contradiction — config is truth):** several in-code
docstrings still say **"BGE-M3 @ :8001, 1024-dim"** (cognition.py:650,669; suite.py:11509 `query_corpus`
docstring; suite.py:5191). Those are **STALE prose** — the *runtime* is config-driven and resolves to
**pplx @ :8007, 2560-dim** (verified: `_embed_consult_query` reads `fcfg.DEFAULT_EMBED_*`,
suite.py:5198-5200). BGE-M3 @ :8001 is **DORMANT** (endpoint down; 1024-dim vectors survive at the
bare/None layer, reachable only if revived — config.py:36-38). **Trust config.py + the `emb` layer
resolution, not the docstrings.** This drift is itself a built-vs-dormant finding.

### C-gap — NO glyph projection space exists (the meaning→glyph fusion build item)

- **OBSERVED:** `projections/` holds 14 lenses; the **embeddable** set (`embeds:True`) is
  operators/history/topics/principles/repo/code_archaeology/extractions/common_knowledge/worldview.
  **`grep glyph projections/ roles/ runtime/corpus*.py fabric/config.py` → ZERO hits.** No glyph space,
  no glyph role.
- A projection is a trivial drop-in dict (projections/extractions.py:9-18): `{id, desc, embeds:True,
  field, level, produced_by}`. A **glyph_meaning** space would be one file `projections/glyph_meaning.py`
  with `embeds:True`. Then: embed each glyph's meaning-field via `embed_corpus_to_spaces` (cognition.py:676),
  and resolve meaning→glyph via `query_corpus(text, space="glyph_meaning")` or `query_hybrid`.
- **This is the concrete fusion gap:** meaning→glyph semantic resolution is *reachable with existing
  primitives* but requires (1) a glyph projection space, (2) a populate/embed pass, (3) freshness
  reconcile (freshness.py:22 `reconcile_space` — add-missing/re-embed-changed/retract-orphaned, the
  auto-fresh loop the extractions space already uses). None built for glyphs yet.

---

## D. How a NEW role (glyph_extract / glyph_compose) is added — FILE-DISCOVERED

**OBSERVED — the mechanism:** roles are **file-discovered** exactly like node-types (roles.py:16-20).
`RoleRegistry.discover([dir])` (roles.py:325) loads every `roles/<id>.py` whose module declares a
`ROLE` dict; a malformed role RAISES at discovery (fail loud); a non-role file is skipped.

- **WHERE the file goes — OBSERVED:** `_ROLES_DIR = ~/company/roles` (cognition.py:120-121). Drop
  `roles/glyph_extract.py` there. `role_registry()` (cognition.py:124) rediscovers fresh, and a
  long-lived server auto-picks-up out-of-process writes via the dir-mtime staleness check
  (roles.py:298-323 `_refresh_if_stale` on every dict-like read).
- **The role-file shape — OBSERVED** (schema = ROLE_FIELDS, roles.py:85-92; validated in `_build_role`,
  roles.py:164). Minimal generate role (mirror `screen_reader.py:22-45` / `element_fit_lens.py:14-36`):
  ```python
  from pydantic import BaseModel
  class GlyphExtractOut(BaseModel):
      ...                                   # the structured output (a real BaseModel subclass — required)
  ROLE = {
      "id": "glyph_extract",                # MUST equal the file stem (fail-loud otherwise, roles.py:177)
      "label": "…", "description": "…",     # operator-facing
      "prompt_template": "… Return ONLY JSON: …",   # present ⇒ can FIRE (generate)
      "output_schema": GlyphExtractOut,     # a Pydantic BaseModel subclass
      "input_addresses": ("utterance",),    # declared inputs
      "model_binding": {"requires": ["chat", "json"], "default_model": None, "default_base_url": None},
      "mode_scope": {...} or absent,        # cast membership; absent ⇒ fired explicitly
  }
  ```
- **`requires` for glyph roles — INFERRED from the pattern:** `["chat", "json"]` (mirror
  screen_reader.py:41) so it binds a `json_schema`-capable resident (satisfies the use-gate, §A-ii
  gotcha #2). `default_model: None` = the safe floor to the resident brain.
- **THE `default_model` NESTING TRAP — OBSERVED (roles.py:40-44):** `default_model`/`default_base_url`
  are **TOP-LEVEL flat fields** on the spec (ROLE_FIELDS, roles.py:90-91), NOT inside `model_binding` —
  BUT `resolve_binding` reads them out of `model_binding` (roles.py:424-425). The safe pattern
  (screen_reader/element_fit_lens/judge) puts them **inside** `model_binding` as shown. A `default_model`
  placed only top-level is read by `resolve_role`'s config path (suite.py) but not by `resolve_binding`'s
  capability path — know which resolver you're calling. (Do NOT set `-pro` as a default: the TIM-RULE
  anti-pattern, roles.py:43-44.)
  - **HONESTY note (the doc contradicts itself; config wins):** roles.py:40-44's TRAP docstring frames
    *nested-in-`model_binding`* as the mistake ("silently unread by `resolve_role`'s config path → falls
    through to `-pro`"). But the two resolvers read `default_model` from **two different places** (config
    path = top-level; capability path = nested), so the "safe" home depends on which fires — and for the
    LIVE fire path neither applies (the binding isn't consulted at all, §B). The docstring's "`-pro`"
    fallthrough claim also looks **STALE**: `config.py:21` now sets `DEFAULT_BRAIN` with **no hardcoded
    default** and `require_brain` fails loud (config.py:24-32) — there is no silent `-pro`. Net for glyph
    roles: nest in `model_binding` to mirror the live examples, but rely on an explicit `model=` at fire
    if a specific model matters (§B), not on either default path.
- **Two authoring routes — OBSERVED (element_fit_lens.py:1-5):** (1) DIRECT `create_role` (the agent
  authors live, #58), (2) `propose_role → operator-approve → apply_role` (surfacing). Both validate by
  import-in-a-temp-dir before the file reaches the live tree.
- **Alternatively author via MCP:** `mcp__company__propose_role` / `edit_role` / `delete_role` tools
  exist (the design-system can author a glyph role over the wire) — exact signatures confirmed in the
  MCP-face read (see §A note).
- **Then FIRE it:** `run_role(glyph_extract, {"utterance": <mark-meaning-or-text>})` → validated
  `GlyphExtractOut` dict; or `run_items(glyph_extract, [chunks], store, turn_id=…)` to fan over many
  marks concurrently.

---

## Honesty ledger — built vs dormant vs stale (the task's core ask)

| Thing | Status | Evidence |
|---|---|---|
| `run_role` structured-output fire | **BUILT + used** (every current role) | cognition.py:429-616 |
| `run_role(op=embed)` → vector | **BUILT** (fail-loud when embedder down) | cognition.py:408-427 |
| Embed-to-SPACE persist for a NEW glyph space | **NOT BUILT** (`embed_corpus_to_spaces` exists but no glyph space) | cognition.py:676; projections/ has no glyph |
| `query_corpus` (vector leg) | **BUILT** (config-driven embedder) | suite.py:11506 |
| `query_hybrid` (RRF fusion) | **BUILT; math verified; end-to-end UNVERIFIED pending embedder** | corpus_fusion.py:149 |
| `resolve_role_binding` (LIVE role→model) | **BUILT + live** | suite.py:6400 |
| `resolve_model` (the ONE unifier) | **BUILT-BUT-DORMANT — nothing routes through it** | model_routing.py:13-15 |
| `satisfied` floor trap | **REAL — assert satisfied, not model-truthiness** | roles.py:424-427; model_routing.py:22-27 |
| run_swarm / run_items concurrency | **BUILT** (registry-budgeted, barrier-joined) | cognition.py:1451, 1599 |
| `run_reduce` (the cross-unit JOIN — role/rule/cluster) | **BUILT + MCP-exposed** (the map→reduce chain for `glyph_compose`) | cognition.py:2398; server.py:917 |
| capability binding APPLIED at fire | **NOT applied — `resolve_role_binding` is read-only; fire uses caller `model=` or the resident sentinel** | server.py:768; cognition.py:401-406 |
| freshness `reconcile_space` (auto-fresh) | **BUILT** (used for extractions space) | freshness.py:22 |
| File-discovered role add | **BUILT** (drop `roles/<id>.py`, auto-rediscover) | roles.py:325, 298-323 |
| Embedder = pplx @ :8007 / 2560-dim | **LIVE** (config-driven; in-code "BGE/:8001/1024" comments are STALE) | config.py:39-40,50 vs cognition.py:650 |
| Glyph projection space + glyph roles | **NONE EXIST** (zero grep hits) | projections/, roles/ |

---

## The fusion picture in one relation (for the design doc)

```
GLYPH ↔ MEANING resolution, built ENTIRELY on existing primitives + 3 build items:

  a mark's meaning-text ──embed──▶ pplx @ :8007 (2560-dim) ──▶ [glyph_meaning SPACE]  ◀── BUILD ITEM 1 (projection row)
                                                                     │                     BUILD ITEM 2 (populate/embed pass)
  design-system query ──corpus(op=query, space="glyph_meaning", mode=hybrid)──▶ ranked glyphs   BUILD ITEM 3 (freshness reindex)
  glyph_extract / glyph_compose roles ──drop roles/glyph_*.py──▶ run_role → validated JSON  ◀── FILE-DISCOVERED (no code edit)
```

The Company side is **ready to be reached** — the fire path, the embed path, the query path, the
role-authoring path all exist and are live (or verify-pathed). The three build items are all
registry/data drops (a projection row, an ingest pass, roles files), not engine work — and the
glyph roles must obey the schema-fire discipline (§A gotchas 1–3).

*Every claim above carries file:line evidence and a built/dormant/stale tag. §A is complete —
confirmed against `mcp_face/server.py` + `mcp_face/tools/{corpus,ingest}.py` first-hand.*
