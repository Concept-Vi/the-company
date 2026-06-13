# Read 5 — The Fabric Model Layer (through the "bigger local-model intention" lens)

> **What this is.** A code-grounded deep read of the Company's local-model layer — `fabric/` (the model binding + guards + registry), `runtime/cognition.py` + `roles/` (the resident-4B swarm that mines/distills/clusters), and `ops/cli` + the resource-manager (load/swap/evict against the 16 GB card) — read specifically to understand **what the merged memory build can lean on**, and read through Tim's lens (2026-06-11, MERGE-INTENTION §4): *"I intend to do a lot more with the Company's local-model systems. Design assuming a growing model layer — embedding at scale, always-on mining, consolidation passes, on-device cognition over memory — not today's usage."*
>
> **Evidence convention** (Tim's CLAUDE.md): **Observed** = read directly in code/config; **Inferred** = pattern-matched, not executed; **Verified** = confirmed by running (I ran nothing live here, so there are no Verified claims — the constitutions assert several things as "VERIFIED" / "proven by tests" and I label those as *the code claims verified*).
>
> Companion reads in this folder cover the spine, store, substrate-mcp, and conversation-intelligence. This one is the **fabric / model layer**. File paths are absolute.

---

## 0. The one-paragraph shape

**Observed.** The model layer is **one OpenAI-compatible call seam** (`fabric/`) with **guards** in front of it, fed model names from a **file-discovered capability registry**, fired by a **registry-driven role system** (`roles/*.py`) through a **concurrent cognition driver** (`runtime/cognition.py`), all sitting on a **single 16 GB card** policed by **one VRAM resource-manager** (`ops/cli/gpu.py` + `capabilities.py`) operated through the `company` CLID and `services.json`. Everything is **configurable data, not hardcoded** — adding a model = one row in `services.json` (deployment) + one row in `ops/model_capabilities.json` (intrinsic capability); adding a cognition job = one `roles/<id>.py` file. The merge's three heavy demands — **re-embed 75k exchanges + 114k chunks into one vector space**, **mine every exchange through the resident swarm**, **consolidate/cluster over time** — all map onto seams that **already exist and are already exercised by the corpus pipeline**, but at **sample scale, not firehose scale**. The intention is to turn the dials up: continuous, always-on, larger-tier, on-device-over-memory.

---

## 1. EMBEDDING — how it's done today

### 1.1 The provider / endpoint / model (Observed)

- **Endpoint.** Embeddings have their **own dedicated endpoint**, separate from chat. `fabric/config.py:26`:
  ```
  DEFAULT_EMBED_URL   = "http://localhost:8001/v1"   # NOT the chat endpoint (:11434/:4100/:8000)
  DEFAULT_EMBED_MODEL = "BAAI/bge-m3"
  DEFAULT_EMBED_DIM   = 1024
  ```
  The config docstring is explicit: *"Embeddings have their OWN endpoint — they are NOT in litellm.config.yaml. BGE-M3 @ :8001 is the only LIVE, dim-grounded embedder (1024-dim dense)."*
- **This is the SAME endpoint substrate-mcp uses.** `services.json` service `embed-bge` serves `BAAI/bge-m3` on **port 8001**, vLLM with `--runner pooling`, `gpu_util 0.3` (~2.5 GB). So the read 3 finding (substrate-mcp embeds vault chunks via bge-m3 @ localhost:8001) and the fabric embed path **are the same model on the same port** — they already share an embedder, just not a store. *(This is a big merge lever — see §5.)*
- **Provider mechanism.** Not Ollama, not LiteLLM for embeddings — it is **vLLM serving bge-m3 in pooling mode** behind a raw OpenAI `/v1/embeddings` route. The transport (`fabric/transport.py:261-283`, `openai_embeddings_transport`) is stdlib `urllib` POSTing `{"model", "input": [texts]}` to `<base_url>/embeddings` and returning the bare vectors. No SDK, no LiteLLM proxy in the embed path.

### 1.2 The guarded embed call (Observed)

`fabric/client.py:148-190` `complete_embeddings` is the **vector-shaped guard sibling** of the chat guard. It is NOT the text guard (empty/JSON/schema checks are meaningless on a float list). Its guards, each failure → jittered backoff + retry, exhausted → **raise `FabricError` (fail loud, never partial)**:
- transport/network error,
- empty result (no vectors),
- **count mismatch** — `len(vectors) != len(inputs)` (one vector per input, or fail),
- **dim mismatch** — every vector length must `== dim` if `dim` asserted (the 1024 contract).

So a wrong-length vector **fails loud**, never flows through as a bad cosine. This is the embed contract the merge inherits for free.

### 1.3 How an embed is actually invoked (Observed — two real paths, ONE plumbing)

There is **one embed plumbing**, reached two ways:

1. **`run_role(op="embed")`** (`runtime/cognition.py:282-301`). A role declares `op: "embed"` (`roles/embed.py`) and `run_role` routes to `openai_embeddings_transport` + `complete_embeddings`, returning `{"vector", "dim", "model"}`. **Local resident embedder only — no cloud branch** (Tim's correction is in the code comment: *"an embedder takes a small card slot, co-resides, but is NOT a cloud escape from residency"*). A down embedder **raises** (fail-loud), unless the caller passes `ensure=True` (opt-in deliberate load via the resource-manager — §3).
2. **`embed_corpus_to_spaces(...)`** (`runtime/cognition.py:386-451`) → delegates to `store/vector_index.build_index(store, records, space=<projection>)`. This is the **batch, space-keyed persist path** the corpus capture uses. It embeds via the **exact same** `complete_embeddings` (`cognition.py` comment: *"the ONE embed path, not a paralleled one"*), keys each vector by `store.space_address(item, space)`, and gives **content-hash incremental diff + one-round-trip batch + degrade-with-warning** for free.

**The embedder-down semantics differ deliberately** (Observed, `cognition.py:359-385`):
- Single one-shot embed (`run_role(op=embed)`) → **HARD raise** (a deliberate one embed must succeed).
- Batch capture (`embed_corpus_to_spaces` → `build_index`) → **degrade-with-warning**: emits a loud durable `warning` event, writes nothing, returns `degraded=True` **without crashing the whole multi-record pass** — records can be re-embedded when :8001 is back. This is the sanctioned degrade for bulk work.

### 1.4 The embedding SPACE (Observed)

- **Spaces are file-discovered projections, not a hardcoded enum.** `Suite.cognition_inputs()`/`available_inputs()` (`runtime/suite.py:9918-9995`) derives the space set from `projection_registry.embeddable()` — every `projections/<id>.py` declaring `embeds: true` becomes a vector space addressed `vec://<item>#space=<id>`. The `history` and `repo` spaces named in the lens are **projection ids**, not constants.
- A record persisted to a space carries explicit `space`/`source` fields; the key `store.space_address(source_address, projection)` is **the same key `find_relations` reads** (`suite.py:~10298-10348`), so cross-space queries line up by construction. `find_relations` is the cross-space inversion finder ("near in space A, far in space B") — it requires an item embedded in *both* spaces first.
- **Dim is single-source** (`DEFAULT_EMBED_DIM = 1024`, config-driven). Changing embedder = change the config, and the dim contract re-asserts at the guard.

### 1.5 The bigger embedder is already cataloged (Observed — the headroom)

`ops/model_capabilities.json` + `services.json` already declare a **larger embedder tier**:
- `embed-bge` — `BAAI/bge-m3`, 1024-dim, ~2.5 GB, the **live default**.
- `embed-qwen3` — **`Qwen/Qwen3-Embedding-8B`**, `gpu_util 0.92` (~9 GB), `--runner pooling`. This is the `qwen3-embedding:4b`/8B tier the lens and Tim's memory (`project-native-model-layer`, `project-local-ai-stack`) point at as "fabric grade."
- `embed-jina-v4` (multimodal, ~8 GB, custom transformers server) and `embed-jina-v5` (~2 GB) also cataloged.

**Inferred:** the merge's "one fabric-grade embedder" decision (MERGE-INTENTION D4) is a **registry swap**, not new plumbing — flip `COMPANY_EMBED_MODEL`/`COMPANY_EMBED_URL` (or the `embed-*` service the capture path points at) and the dim contract follows. The cost is the **re-embed pass** (sizing), not the wiring.

---

## 2. MINING / DISTILLATION / CONSOLIDATION — how cognition over content is done today

### 2.1 The resident swarm (Observed)

- **The worker.** `services.json` `chat-4b` = `cyankiwi/Qwen3.5-4B-AWQ-4bit`, vLLM @ **:8000**, `gpu_util 0.49` (~7 GB), `max_model_len 65536`, **`max_num_seqs 34`** (the concurrency knee), prefix-caching + auto-tool-choice on. Capability row: `provides: [chat, json, tools, ...]`. The constitution calls it *"a local WORKER (not the RHM brain; the RHM main is a cloud model)."* Measured profile in `services.json`: `kv_kb_per_token 31.7`, 256K-solo gives KV 8.37 GiB / 270k tokens.
- **A model runs ONLY inside a role (L2).** `runtime/roles.py` is the file-discovered role registry (mirrors `NodeRegistry`): a `roles/<id>.py` declares a `ROLE` dict; `run_role` fires it through the fabric guards. Adding a cognition job = adding a file.

### 2.2 The map/reduce engine (Observed — this IS the mining substrate)

`runtime/cognition.py` is the concurrent driver (all parallelism lives here, NOT in the serial `scheduler.py`):

- **`run_items(role, items, ...)`** (`:1095`) — **fan ONE role over N units, concurrently** (the axis-inversion). Each unit rides at `ctx["utterance"]`; output written to `run://<turn>/<role>/<i>`. **Per-unit resilience (F2):** a poison unit (e.g. an over-context exchange → a 400) goes to `.failed` and the **good units still return** — the batch is not all-or-nothing. Bounded by the slot budget + global VRAM gate + a barrier. **This is exactly the transcript-miner's MAP** (`run_items(mine_exchange, [..N exchanges..])`).
- **`run_reduce(addresses, mode=...)`** (`:1889`) — the cross-unit JOIN, three modes:
  - `mode="role"` — synthesize: compose N outputs → fire a reduce-role (`reduce_synth`) → one merged output.
  - `mode="rule"` — deterministic L2 verdict (vote/merge/select), no model.
  - **`mode="cluster"`** (`:1978`, `_cluster_units` `:2019`) — **embed each unit + greedy cosine-group** (reuses `nodes/retrieve._cosine`, dim-mismatch fail-loud) → clusters of near-duplicates. Deterministic (sorted unit order). **This is the pattern_cluster / consolidation primitive** — and it runs through `complete_embeddings` (the same bge-m3 path).
- **`run_swarm` / `run_jury`** — the per-turn cast + N-draws-with-verdict (juries are single-model today; the code flags E4: N draws on one 4B are correlated, accepts a future stronger/cloud tiebreak).

### 2.3 The mining role (Observed)

`roles/mine_exchange.py` is the transcript-miner MAP role. It reads ONE exchange `{tim_message, my_response, session_id?, ts?}` → a validated `MineExchangeOut` `{decision, rationale, tim_correction, my_error, bug_fix, needs_tim, frustration, pattern_tag}` (7 optional strings + the required kebab `pattern_tag`). **No-fiction floor:** absent signals are `""`, never fabricated; a sibling `judge_mining` role re-checks a sampled extract against the raw exchange. `output_schema` is enforced by `complete()`'s parse/validate/retry, and now (G24) by **server-side schema-guided decoding** so the 4B *cannot* emit schema-invalid JSON.

**This is the live pipeline the lens names (`flows/transcript_mine.py` G23):** the corpus pipeline already runs each exchange through the resident 4B and lands `exchange://<sid>/<i>` records. **Observed in MERGE-INTENTION:** it has run on only ~2,111 records (≈ one session), and the `pattern_cluster` reduce is *flagged-but-not-run*. The mechanism is built; the volume isn't.

### 2.4 The cost / concurrency model (Observed)

- **`SlotBudget.from_registry()`** (`cognition.py:717-782`) computes the swarm width from **live `services.json`**, never a hardcoded 32: `knee = min(max_num_seqs − R, free_KV // per_role_ctx)`, `swarm_slots = max(1, knee)`, with `R=2` reserved for the main stream/judge. KV pool by gpu_util is **C0.5-measured** (`66036 @ 0.49`, `135574 @ 0.63`). So with `chat-4b` at `max_num_seqs=34`, the swarm gets up to ~32 concurrent role-fires (minus KV bound at the live main-context depth).
- **`global_vram_gate`** — a process-wide semaphore singleton sized to the knee; every local call (main + swarm) passes it, so the swarm can never starve the main stream.
- **Telemetry** is batched — ONE rollup per wave (`cognition.items`/`cognition.reduce`), not one fsync per fire.
- **Placement policy as data** (`capabilities.py:276-298`, `COGNITION_PLACEMENT_POLICY`): **swarm = resident-always** (never moved to cloud, never lost by a cloud-brain choice); **main_brain = selectable** (resident or cloud); **background = cloud-allowed** ("cloud MAY run background roles — between-turn consolidation"). *This last line is the merge's permission slip for off-card consolidation passes.*

---

## 3. RESOURCE MANAGEMENT — load / swap / evict on one 16 GB card

### 3.1 The one resource-manager (Observed)

- **`ops/cli/gpu.py`** is *the* single VRAM authority (CLI + voice both import it; no second budget). It reads **measured free VRAM from live `nvidia-smi`** (the constitution's hard rule: *"VRAM decisions read live nvidia-smi, never an internal ledger"*), budgets each service as `config.gpu_util × ceiling` (authoritative for vLLM) else learned telemetry else the registry estimate, and does:
  - `check_fit(to_start)` → `(ok, need, free, present)` (measured free vs the sum of not-running budgets),
  - `plan_eviction(...)` → largest-first, **models → brain → voice** priority order,
  - `teardown(svc)` → **orphan-safe cgroup teardown** (the EngineCore VRAM-squat lesson — Tim's memory `project-vllm-gpu-gotchas`),
  - `fit_report(keys)` → the "will this selection fit the card / fit now?" surface.
- **`ops/cli/capabilities.py:ensure_resident(model_or_service, evict=False)`** (`:400`) is **the gated launch/select/evict actuator** — reuses gpu.py's primitives (no second start path). Returns structured `{action: already-resident|loaded|evicted-and-loaded|swap-approval-needed}`. **G14 swap-approval (Tim's design):** a load needing eviction *without* pre-authorization **returns a structured ASK** (`{swap_needed, would_load, would_evict, free_gb, needed_gb, approve}`) — never a silent evict, never a hard block; the agent re-calls with `evict=True`. **Fail-loud:** can't-fit-even-after-full-plan → `EnsureResidentError`.
- **`run_role(ensure=True, ensure_evict=...)`** wires this in: an embed role can request the embedder be made resident before embedding, and surfaces the swap-approval ASK to the caller (`cognition.py:187-301`).

### 3.2 The `company` CLI + services.json (Observed)

- `services.json` is the **single self-describing service registry** — what runs, ports, units, `vram_mb` estimates, `config` (model/gpu_util/max_model_len/max_num_seqs/flags). **Nothing auto-starts at boot** (Tim's 2026-06-06 call); everything is on-demand via `company up <svc>` / `company up @<combo>`.
- **Combos** are named co-resident sets. The `wake` combo (Tim, 2026-06-11) = `bridge + chat-4b + embed-bge + stt-whisper + tts-kokoro` — **~12 GB co-resident, verified together** — i.e. **the resident brain + the embedder already run side-by-side**, which is exactly the merge's steady state (mine on 4B while embedding on bge-m3).
- **Mode→loadout** (`ensure_loadout_for_mode`, `capabilities.py:514`; Tim's memory `project-mode-loadout-registry`): a mode declares a `brain_config` loadout; the actuator ensures the brain service resident. The gpu_util *variant* swap (swarm-16k @ 0.63 vs voice-64k @ 0.49) is honestly surfaced as a `company config + restart` needs-tim, not silently bridged.

### 3.3 The constraint envelope (Observed → the numbers that bound the merge)

| Resource | Today's reality | Bound on the merge |
|---|---|---|
| **Card** | 16,376 MB ceiling, one GPU | Everything competes for this; co-residency is budget arithmetic |
| **Resident brain (4B)** | `chat-4b` ~7 GB @ 0.49, `max_num_seqs 34`, KV 66k tok @ 0.49 / 135k @ 0.63 | Mining throughput = swarm_slots (~32) × per-exchange latency; KV pool caps concurrency × context |
| **Embedder (bge-m3)** | ~2.5 GB @ 0.3, 1024-dim | Co-resides with the 4B (the `wake` combo proves it); throughput = vLLM pooling batch rate |
| **Bigger embedder (qwen3-8B)** | ~9 GB @ 0.92 | Does NOT co-reside with the 4B brain (9 + 7 > card); a re-embed pass would evict the brain or run as a dedicated phase |
| **Bigger reasoner (nemotron-30B)** | ~16.6 GB @ 0.88 + 6 GB CPU-offload | Solo-only; a heavy consolidation/synthesis tier is a swap-in phase, not co-resident |
| **Concurrency** | global VRAM gate + swarm sub-pool (knee − R) | The swarm never starves the main stream; bulk mining shares the same pool |

---

## 4. The integration points the merged memory will use (Observed seams, named)

The merge does not need new model plumbing — it needs to **point existing seams at the firehose and turn them on**. The seams:

1. **Embed at scale →** `cognition.embed_corpus_to_spaces(store, records, projections)` → `vector_index.build_index(space=)`. Batch, incremental (content-hash diff), space-keyed, degrade-with-warning. Re-embedding 75k exchanges + 114k chunks is **N calls to this**, against whichever `embed-*` service is loaded. The dim contract (`DEFAULT_EMBED_DIM`) is the single source to flip for a bigger embedder.
2. **Mine every exchange →** `run_items(mine_exchange, [..exchanges..], budget=SlotBudget.from_registry())`. Per-unit resilient, concurrency from the live registry, batched telemetry. The firehose just becomes a longer `items` list (chunked into waves).
3. **Cluster / consolidate →** `run_reduce(mode="cluster", addresses=<the mined run:// addrs>)` for pattern_cluster; `run_reduce(mode="role", role=reduce_synth)` for synthesis; `find_relations` (`suite.py`) for cross-space inversion ("said often / never acted on"). All three are built; cluster + find_relations need the embedder window.
4. **Resource-gate the bulk work →** `ensure_resident(<embedder-or-brain>, evict=...)` before a pass; the G14 swap-approval ASK is the governed way a background consolidation requests the card. `placement_for("background") = cloud-allowed` permits off-card consolidation when the local card is busy with the live cast.
5. **Capability query for the right model →** `capabilities.suitable_models(["embed"])` → the embedders; `suitable_models(["chat","json"])` → the chat workers. A consolidation role that wants a stronger model declares `requires` and binds via `resolve_binding` (C2.5) — registry-driven, not hardcoded.
6. **The shared embedder is already shared.** bge-m3 @ :8001 is BOTH the fabric embed default AND substrate-mcp's embedder (read 3). One model, two stores today — collapsing to one store (D1) makes them one space.

---

## 5. What "doing a lot more with local models" plausibly means for the merge

> Framed as **enabling a bigger intention**, not constraining to today. These are tentative expansions of Tim's §4 lens — marked for his steer.

**A. Continuous re-embedding into one fabric-grade space (turn the embed dial up, and make it always-on).**
Today: bge-m3 1024-dim, batch, sample volume, three separate stores. The intention: **one vector space at fabric grade** (likely `qwen3-embedding:8B`), with re-embedding as a **standing background metabolism**, not a one-shot. The seam exists (`embed_corpus_to_spaces`, incremental diff). What grows: (i) a **dedicated embed phase** — qwen3-8B (~9 GB) can't co-reside with the 4B brain, so a large re-embed evicts the brain or runs as a scheduled window (governed by `ensure_resident(evict=...)`); (ii) **dim becomes a migration**, not a constant — the single-source `DEFAULT_EMBED_DIM` + per-space dim contract is the lever, but the stored vectors need a versioned re-embed (the episodic-memory MiniLM 384-dim → fabric 1024/qwen-dim crossover from the lens). The growing model layer makes "one living vector space over conversations AND knowledge" affordable because the embedder is **resource-managed and swappable** rather than hardcoded.

**B. Always-on mining over the firehose (the swarm becomes a standing organ, not a per-turn cast).**
Today: `run_items(mine_exchange, ...)` runs on bounded on-demand batches (~2,111 records). The intention: the **resident 4B swarm mines continuously** as the episodic firehose lands new exchanges — every exchange distilled to `{decision, correction, frustration, pattern_tag, ...}` the moment it's captured, idempotent on `exchange://<sid>/<i>`. The seam is built (per-unit resilient, registry-budgeted). What grows: (i) a **standing background mining loop** fed by the capture hook (the `placement: background = cloud-allowed` policy means heavy mining can spill to cloud when the live cast owns the card); (ii) **bigger/better miners** — `mine_exchange` can bind a stronger model via C2.5 `requires` when one is resident, and `judge_mining` (the no-fiction gate) gains the future stronger-model tiebreak the E4 caveat already anticipates; (iii) **mining as introspective-data-building** (Tim's law) — the swarm mining its own run-records, not just transcripts.

**C. Consolidation / clustering passes as the memory's metabolism (the "dream phase").**
Today: `run_reduce(mode="cluster")` + `find_relations` are built but starved (need the embedder window + volume). The intention (MERGE-INTENTION ③): the consolidation, clustering, forgetting, graph-linking, and temporal-asymmetry processes substrate-mcp built become **native Company metabolism**, running over the merged corpus. The growing model layer is what makes this continuous: a **scheduled consolidation window** that (i) loads the embedder, (ii) clusters `pattern_tag`s into named recurring patterns (→ draft `feedback-*.md` for review), (iii) runs `find_relations` to surface "said-often / never-acted-on" inversions, (iv) synthesizes via `reduce_synth`. Resource-managed: the `company` swap/evict machinery + the background-cloud-allowed policy let this run between live sessions without fighting the foreground cast.

**D. On-device cognition over memory (the swarm reasons FROM the merged store, not just over transcripts).**
Today: the listening/walkthrough casts (recall/ground/connect/check) fire per-turn but read a thin store. The intention: with the merged memory as one addressed, embedded space, the **resident swarm reasons over the entity's whole life on-device** — `recall` retrieves from 75k real exchanges, `connect` traverses the provenance graph (tool-call → artefact → exchange → time, MERGE-INTENTION §2), `ground` cites real past decisions, all **self-injecting by condition and time** (`common-memory-temporal`, GC14). The growing model layer means this on-device cognition gets **stronger and more concurrent**: bigger resident tiers (the 2B/0.8B/30B catalog already declared, the mode→loadout registry already deciding what's resident per mode), more swarm slots as the card/config grows, and the embed-resolve-inject loop (the C6/Collective-Cognition seed) running locally over the merged corpus rather than against a sidecar plugin.

**Cross-cutting:** the layer is **already shaped for growth** — models are declared data (`services.json` + `model_capabilities.json`), capabilities are a query (`requires ⊆ provides`), residency is resource-managed with governed swap-approval, placement is policy-data, and the embed/chat/cluster seams are all single-source and already exercised by the corpus pipeline. The merge's job is **volume, continuity, and tier**, not new architecture. The constraint that will bite is the **16 GB card**: the fabric-grade embedder and the resident brain compete, so the bigger embed/consolidation passes are **scheduled windows with eviction**, not free co-residency — and that scheduling is exactly what the resource-manager + the background-cloud-allowed policy exist to govern.

---

## 6. Constraints / open questions to carry into the merge design

- **VRAM is the hard ceiling (Observed).** 16,376 MB. qwen3-8B embedder (~9 GB) + 4B brain (~7 GB) ≈ the whole card with no room for KV/voice → the fabric-grade re-embed is a **phase that evicts**, not a co-resident. *Surface this in D4 sizing.*
- **Three embedders, three dims, one contract (Observed).** episodic-memory = MiniLM/bge-small **384-dim** (hardcoded in `embeddings.ts` + `db.ts`); fabric/substrate = bge-m3 **1024-dim**; qwen3 = its own dim. Unifying the vector space means a **re-embed migration**, and the single-source `DEFAULT_EMBED_DIM` only helps the *new* space — the old 384-dim vectors are not reusable.
- **The swarm is local-resident-always (Observed policy).** Mining/clustering on the 4B is resident; only the *main brain* and *background* tracks may go cloud. So firehose-scale mining throughput is **bounded by the resident 4B + the swarm knee**, unless a background-cloud lane is built (the policy permits it; the wiring is downstream — flagged in the code as not-yet-built control-flow).
- **The reduce output isn't addressed yet (Observed, `cognition.py:1995`).** `run_reduce`'s joined output is not persisted to a `run://` address by default (the caller decides) — for a standing consolidation organ, the merge needs to **land cluster/consolidation outputs as addressed records** (likely `memory://`), which is the corpus side, not the model layer.
- **`mode_loadout` gpu_util-variant swap is needs-tim (Observed).** Switching the brain between swarm-16k @ 0.63 and voice-64k @ 0.49 is a `company config + restart`, not a live re-slot — so a "mining loadout vs live-cast loadout" distinction is a deliberate operator action today, not automatic.

---

*Status: code-grounded read of `fabric/`, `runtime/cognition.py`, `roles/`, `ops/cli/{gpu,capabilities}.py`, `ops/services.json`, `ops/model_capabilities.json`. CURRENT/seam claims are Observed (cited to file:line). The §5 intentions are my expansion of Tim's "bigger model layer" lens — tentative, for his steer. No live execution was run in this read (no Verified claims); where the constitutions assert "VERIFIED/proven by tests," that is the code's own claim, relayed as such.*
