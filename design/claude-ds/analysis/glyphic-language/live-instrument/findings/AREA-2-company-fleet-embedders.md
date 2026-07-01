# AREA-2 — The Company's local-model fleet + embedders as the concurrent EXTRACT layer

> Companion to `live-instrument/ANCHOR.md`. My area: can the Company's local models + embedders be the
> fast concurrent middle layer that turns talk into glyphgraph structure in real time? I went to the
> code, not the anchor's hopes. **Headline: the machinery already EXISTS and is mostly BUILT — concurrent
> role-dispatch, structured/schema-constrained output, the embedders, and the HTTP endpoints a browser
> can call are all real today.** The honest squeeze is not "can we build it" — it's *resource contention
> on ONE 16 GB card* and the *shared-KV-with-the-main-reply* reality. The anchor's "a fleet of small
> local models continuously extracts" is too rosy in one specific way I correct below.
>
> Evidence tags: **Observed(file:line)** = read directly · **Observed-in-doc** = a build-prep's own
> measured/verified claim (their verification, not mine) · **Inferred** · **External-prior-art** · **My-idea**.

---

## 0 · The one-paragraph verdict (commit this, don't let it drift back to the anchor's optimism)

Small concurrent local models ARE realistic as a realtime extract layer — **in bursts, at conversational
pauses / between turns, not as an always-on fleet running concurrently with a long voice reply.** The
mechanism is built (`run_swarm` + `SlotBudget.from_registry` + a process-wide VRAM gate; structured output
is built AND a negative control proved it constrains the decode). The constraint is one card: the everyday
`interaction` loadout already fills ~14.5 GB, the swarm shares the brain's KV pool with the main reply, and
the measured concurrency knee is **~14 at shallow main context, collapsing to ~1–5 when the main reply is
deep** (Observed-in-doc). So the live layer's correct shape is: **short-context (~1–2K), `think=False`,
schema-constrained extract roles, fired in a wave at each utterance/pause** — concurrent with each other,
*not* concurrent with a 28-second reply generation. That is a real, fast, buildable layer; it is not the
unbounded always-on swarm the anchor sketches.

---

## (a) Cognition-is-role-resolved — how a ROLE resolves to a model, concurrency, latency reality

### A role resolves to a model by capability, never by a pinned name
- A **role** is file-discovered (`roles/<id>.py`) and carries `prompt_template` / `output_schema` /
  `model_binding.requires` (capability strings). The MCP **`models_for_role`** answers "which models fit":
  it reads `spec.model_binding.requires` and returns models whose `provides ⊇ requires`
  (Observed `mcp_face/server.py:495-509`). This is the *capability-resolution* spine the anchor's
  "cognition-is-role-resolved" law names — the role declares what it needs; the resolver picks a model.
- **The resident-brain SENTINEL.** Every entry point (`run_role`/`run_swarm`/`run_items`/…) defaults
  `base_url`/`model` to a sentinel that resolves to **whatever brain is ACTUALLY running now** via
  `active_brain()` (Observed `cognition.py:391-396`). So the cognition layer follows the live loadout — it
  is NOT pinned to `:8000`. An explicitly-passed model (a cloud/ollama id) is used verbatim, with its
  endpoint resolved FROM the model id (HF-path `org/model` → its vLLM service; a `:cloud`/`:tag` →
  ollama :11434) (Observed `mcp_face/server.py:747-758`). **Concurrent cloud cognition at zero VRAM works**
  and survives a reboot — relevant if the extract layer wants to mix a local 4B with a cloud model.

### Can roles run CONCURRENTLY — yes, this is built (`run_swarm`)
- **`run_swarm(roles, ctx, store, ...)`** is the cognition DRIVER (Observed `cognition.py:1413`). It fires
  a wave of roles via a `ThreadPoolExecutor` sized to the swarm sub-pool, barriers per wave, serializes
  store writes behind the barrier (Observed `cognition.py:949-950, 1472-1475`). This is *exactly* the
  anchor's "many small models EXTRACT in parallel" — `run_swarm` IS that, today.
- **Why threads, not async (and why no client batching is needed):** the transport is a blocking callable;
  Python releases the GIL during the blocking socket I/O, so N threads = N true concurrent in-flight HTTP
  requests with ZERO transport changes, and **vLLM does continuous batching server-side** — issue N
  concurrent calls and let vLLM batch them (Observed-in-doc `03-concurrency-and-injection.md:68, 96`).
  → **Answers the open what-if "standing swarm vs per-utterance":** you do NOT need a standing always-on
  swarm. Per-utterance bursts of N concurrent calls are continuous-batched by vLLM; a standing swarm would
  needlessly hold KV and starve the conversation (My-idea, grounded in the batching evidence).

### The HONEST resource reality (the most important correction to the anchor)
**The anchor says "a fleet of small local models." The code says: concurrent requests continuous-batched
against the ONE resident brain, whose KV pool is SHARED with the main voice reply.** There is no fleet of
separate small models for extraction — there is one brain (`chat-4b-fp8` :8001 in the everyday loadout) and
a concurrency budget over it.

- **`SlotBudget.from_registry`** computes the swarm cap from LIVE `services.json` values — never a hardcoded
  32: `knee = min(max_num_seqs − R, free_KV // per_role_ctx)`, `swarm_slots = max(1, knee)`
  (Observed `cognition.py:976-1040`). `free_KV = kv_pool − main_ctx_tokens` — i.e. the deeper the main
  conversation, the fewer swarm slots remain.
- **Measured numbers (Observed-in-doc — the build-prep's verification, NOT my execution):**
  - `max_num_seqs = 16` on the co-resident voice config; **KV pool ~66,036 tokens @ util 0.49**, ~135,574 @
    0.63 (`Completion Criteria C0.5`, marked ✅ by-use 2026-06-07).
  - **knee = 14 at shallow main → 1 at a deep 64K main** (`Completion Criteria C1.2`, ✅ by-use). Main-stream
    acquire latency stayed 0.0–0.2 ms during an in-flight 14-role wave — i.e. the reservation works, the
    operator's turn doesn't stall behind the swarm.
  - **R1-FOLD supersedes the rosy headline:** the often-quoted "c=32 → 2,241 tok/s" benchmark was **4K-context
    on a higher util, NOT the co-resident voice config** — "real co-resident concurrency is well below 32 at
    usable context" (Observed-in-doc `Research Synthesis.md:5, :40`). **Do not cite 32/2241 as the live
    ceiling** — it's the corrected-away figure.
  - Decode ~**100 tok/s** on the 4B (Observed-in-doc `Research Synthesis.md:40`).
  - **`think=False` is the realism lever for fast extraction:** suppressing the reasoning trace took a
    one-word structured answer from **1304 → 43 output tokens (~30×)** — verified on the resident FP8
    (Observed `mcp_face/server.py:696-702`). For schema extraction, `think=False` is essentially mandatory.
- **The everyday card is FULL.** The `interaction-fp8` loadout (brain + pplx embedder + ear + voice) is
  ~14.5 GB / 16 GB, and even had to drop the resident reranker to fit (Observed `services.json:73-78`). So
  "continuous extraction running concurrently with a deep voice reply" is the *worst case* for KV
  contention — the knee collapses to ~1–5 exactly when the operator is mid-long-reply.
- **The lever the build-prep names (needs-tim, deferred):** a higher-util **swarm-brain config** (util ~0.63)
  claims the idle ~3.8 GB the voice config leaves → KV pool grows to ~140–155K tokens → ~15 roles @ 4K + a
  full 64K main fit (Observed-in-doc `Completion Criteria C1.7`, ◑ — the deep-main knee at 0.63 is
  computed, not yet use-measured; flagged needs-tim/GPU reconfig). **MODE selects the brain CONFIG** is the
  designed answer to "make the live layer keep up" — but it's a GPU-reconfig lever, not free.

**Bottom line for (a):** concurrent role extraction is built and measured. The realistic operating point is
*a wave of ~10–14 short, think-off, schema-constrained roles fired at each pause*, with R slots reserved so
the conversation never stalls. Not unlimited; not concurrent with a long reply.

---

## (b) STRUCTURED / constrained outputs — does the stack support it, and how would a small model emit the glyphic/edge schema reliably?

**Yes — this is built, gated, and a negative control proved it works.** This is the strongest "reuse, don't
reinvent" finding in my area.

- **Two layers of enforcement, both real:**
  1. **Client-side validate/retry (F9):** `run_role(..., json=True, schema=<Pydantic>)` → `client.complete`
     parses + validates + retries on a malformed output (Observed `cognition.py:318-320, 580-583`). ✅ by-use,
     malformed caught + retried (Observed-in-doc `Completion Criteria C1.4`).
  2. **Server-side schema-constrained decode (vLLM 0.21 guided decode):** the transport now has a
     `json_schema` branch (`_apply_response_format` on both `openai_transport` + `openai_tools_transport`);
     **resident vLLM 0.21 ACCEPTS `response_format: json_schema` AND a negative control proved it CONSTRAINS
     the decode (xgrammar bites)** (Observed-in-doc `Completion Criteria C1.4`, "L-transport DONE"). So this
     is not "json_object hope" — the decoder is genuinely grammar-constrained to the schema.
- **A fail-loud USE-GATE (the no-silent-downgrade C-law) — directly serves the anchor's GOVERNING LAW.**
  Before firing, `run_role` reads the bound model's `json_schema` capability from `model_capabilities.json`.
  Tri-state: declared-true → fire; **declared-false → REFUSE (raise FabricError), NEVER silently downgrade
  to bare json_object** (which would leave the role's schema contract unenforced at the decoder);
  None/undeclared → proceed (Observed `cognition.py:490-515`). **Both residents (AWQ + FP8) declare
  `json_schema.value=true`** (Observed-in-doc, same gate comment) → no resident regression. This is exactly
  the "everything resolved from a single source, fail-loud, no silent backfill" discipline the live layer
  must hold.
- **HOW the glyphic/edge schema gets emitted reliably (the concrete design bridge — My-idea grounded in the
  above):** an extract role's `output_schema` *is* the glyphic/edge schema. Declare a Pydantic schema that
  mirrors `CV_GLYPHIC.schema.symbol` (the design-system's symbol record shape, ANCHOR §7) plus the
  edge/relation shape — e.g. `{ things: [{ id, noun, type, state }], edges: [{ from, to, relation }] }` —
  bind it as the role's `output_schema`, fire with `think=False`. The vLLM guided-decode constrains the
  small 4B to emit valid JSON of exactly that shape; client validate/retry is the backstop. **The "small
  model emits the structure reliably" problem is already solved by the stack** — the design work is writing
  the right Pydantic schema(s), one per extract concern (entities / relations / states / placement-hints),
  matching the anchor's pipeline.
- **Two honest cost notes:**
  - **xgrammar has a cold grammar-compile cost on first use of each distinct schema, cached after**
    (External-prior-art; consistent with the "xgrammar bites" negative-control). → **a per-schema warmup
    pass** at instrument start (fire each extract schema once on a dummy utterance) removes the first-token
    stall from the live path (My-idea).
  - The output-field-type registry is a CLOSED set (single source: `runtime/authoring.py:FIELD_TYPES`,
    exposed via the `field_types` tool / `GET /api/cognition/field_types`; the `field_types` tool
    description is derived from that registry, not a frozen subset). RESOLVED (B2): beyond the flat
    scalars it now includes the RICHER kinds `enum`, `object`, and `list[object]` (+ aliases `dict`,
    `list[dict]`), rendered by a recursive renderer. So the glyphic schema's nested objects (the
    `edges: [{...}]` above) ARE expressible — `list[object]` with declared `fields` — no flattening needed.

---

## (c) The EMBEDDERS — what's served, the pplx 0.6b, the embed/retrieve node API

### What is the LIVE embedder (corrects the anchor's BGE assumption)
- **The operative embedder is `pplx-embed-context-v1-4b` @ `:8007`, 2560-dim, INT8 + unnormalized
  (compare via COSINE).** `fabric/config.py` is the source of truth: `DEFAULT_EMBED_URL=:8007/v1`,
  `DEFAULT_EMBED_MODEL=perplexity-ai/pplx-embed-context-v1-4b`, `DEFAULT_EMBED_DIM=2560`, default layer
  `pplx` (Observed `fabric/config.py:35-67`). It's a CUSTOM transformers server (vLLM 0.21 can't load its
  `PPLXQwen3` arch), wired + verified by the retrieval session 2026-06-12 (Observed `services.json:513-529`).
- **BGE-M3 @ :8001 is DORMANT** ("endpoint down; 1024-dim vectors stay intact at the bare/None layer …
  reachable only if re-served") (Observed `fabric/config.py:36-37`). **STALE-DOC FLAG:** `nodes/embed.py`'s
  docstring still says *"BGE-M3 @ :8001, 1024-dim — the only live embedder"* (Observed `nodes/embed.py:5-6`)
  — that is out of date; `fabric/config.py` (which the node actually reads via `DEFAULT_EMBED_*`) points at
  pplx :8007. (Resolve-into-scope per Tim's standing rule: the node docstring should be corrected to the
  config truth.)
- **PORT-COLLISION reality (the advisor flagged, confirmed):** `embed-bge` is on **:8001** —
  **the SAME port as `chat-4b-fp8`** (Observed `services.json:476` vs `:188`). So BGE-M3 and the FP8 brain
  are **mutually exclusive**; you cannot run "BGE @ :8001" for icon-lookup *while* the FP8 brain holds :8001.
  The pplx-4b embedder is :8007 and DOES co-reside in the `interaction`/`instrument` loadouts. → **the
  icon-lookup embedder is pplx-4b (served, co-resident) — not BGE.**

### The pplx ~0.6b embedder Tim referenced — it EXISTS, on disk, NOT served
- **`perplexity-ai/pplx-embed-v1-0.6b` is real and cataloged: ON DISK (5.6 G), 1024-dim, 32K ctx, MIT
  license, the smaller sibling of the context-4b** (Observed `model_capabilities.json:596-629`). Its
  distinctive talent: **quantization-aware training → native INT8 (4×) and binary (32×) compressed
  embeddings with quality intact** — exactly what you want for embedding a large icon corpus and doing fast
  nearest-neighbour.
- **BUT it is NOT served:** there is **no `services.json` entry, no systemd unit, no serve script** for the
  0.6b (Observed — it appears only in `model_capabilities.json`, never in `services.json`; the only served
  pplx is the 4b). The earlier services.json note even records that a prior "0.6b" value was a *mistake*
  corrected to the 4b (Observed `services.json:527`).
- **To use the 0.6b you must serve it** — like the 4b, it's remote-code arch (`PPLXQwen3`) vLLM can't load,
  so it needs a custom transformers server on a **fresh port** (clone `ops/serve_pplx_embed.py`/`.sh`,
  point at the 0.6b model id, register a `services.json` entry + unit) (Inferred from the 4b's setup,
  Observed `services.json:522`). It's smaller (~5.6 G vs the 4b's ~8 G resident) → easier to co-reside, and
  1024-dim is cheaper to nearest-neighbour than 2560-dim. **My-idea:** the 0.6b is the *right* icon-lookup
  embedder — small, INT8-native, MIT — but it is a small build task (serve it), not "already there."
  Interim, the served pplx-4b @ :8007 does the job at 2560-dim.

### The embed/retrieve node API (the building blocks, already typed)
- **`nodes/embed.py`** — process node: `text(Text) → vector(Vector)` via
  `fabric.client.complete_embeddings`; dim ENFORCED (wrong length → FabricError, fail-loud, no silent bad
  cosine) (Observed `nodes/embed.py:18-50`).
- **`nodes/retrieve.py`** — process node: `query(Vector) + corpus(Any) → ranked(Any)` = top-K by cosine;
  numpy-vectorized path (~100× on a large space: 44k×2560 ~10s→~0.1s warm) (Observed `nodes/retrieve.py:21-26,
  40-55`). dim-mismatch → fail-loud; zero vector → ZeroDivisionError (fail-loud).
- **`run_role(op="embed")`** reuses this exact embed plumbing (no second vector path) and returns
  `{vector, dim, model}`; a down embedder RAISES unless `ensure=True` requests the gated resource actuator
  to load it (Observed `cognition.py:398-417`). → **the semantic icon-lookup the anchor wants
  (embed the noun → nearest tagged icon → below threshold → foundry) maps cleanly onto embed→retrieve**:
  embed the spoken noun (run_role op=embed or POST /api/cognition/embed), cosine-rank against pre-embedded
  icon vectors (the `retrieve` node's job), threshold, miss → `glyphic.generate`. All the primitives exist.

---

## (d) The model ENDPOINTS a browser / design-system could call (the browser↔Company boundary, precisely)

The anchor worried this boundary is hard. **It's softer than feared** — the bridge already exposes the
extract layer over plain HTTP, but with one real constraint (origin).

- **The bridge is a `ThreadingHTTPServer` on `127.0.0.1:8770`, ONE process** (Observed `bridge.py:3725`).
  It exposes (all POST):
  - **`/api/cognition/run_role`** — fire one role (op rides the role) → `run://` output
    (Observed `bridge.py:3351`, route list `:85`).
  - **`/api/cognition/embed`** — fire an embed-op role → `{vector, dim, model}` (Observed `bridge.py:3370`).
  - **`/api/cognition/run_items`**, `/run_reduce`, `/role/propose|edit|dry_run`, `/api/cognition/inputs`,
    `/models_for_role`, `/field_types` — the full role authoring + run surface (Observed route list
    `bridge.py:58-88`).
  - **`/api/chat/stream`** and **`/api/voice/stream`** — streaming (ndjson) (Observed `bridge.py:119-120`).
- **The boundary truth (the advisor's correction, confirmed):**
  - **No CORS headers are set** — the only network binding is `127.0.0.1` and there's no
    `Access-Control-Allow-Origin` anywhere in the bridge (Observed grep — only `127.0.0.1`/localhost refs,
    no CORS). → **the instrument canvas must be SAME-ORIGIN: served behind the bridge (:8770)**, OR you add
    a CORS allowance / a dev proxy. **A vite dev server on :5173 is a different origin → blocked today**
    (Inferred from the absence of CORS + the localhost-only bind).
  - **The no-script page-face (:8774) CANNOT be the instrument surface.** It is a *deliberately separate
    origin under a no-script CSP*, blocked from same-origin-fetching `/api` (Observed `services.json:114-124`).
    reactflow needs scripts → it cannot live there. → **this cleanly resolves the anchor's "reactflow-in-CSP"
    worry: reactflow is NOT in the no-script CSP. It's the scripted, bridge-served canvas (the same surface
    the existing canvas/vite app uses), not the page-face.** (My-idea/Inferred.)
- **The MCP face is the OTHER door** (`run_role`/`models_for_role`/`cognition_inputs`/`propose_role`/
  `edit_role`/`embed` are all MCP tools, Observed `mcp_face/server.py:495,513,669,1022,1032`) — that's the
  agent/cross-session control plane, not a same-origin browser fetch. For a *browser* instrument, the bridge
  HTTP routes are the path.
- **Browser-drives vs Company-pushes (the open what-if) — answered from the architecture:** given a
  localhost-only, one-process `ThreadingHTTPServer` that already runs a server-side N-part producer with a
  single ordered ndjson emitter for `/api/voice/stream` (Observed-in-doc `05-voice-stream-coupling.md`),
  the natural fit is **the Company DRIVES the extract→resolve→place pipeline server-side and PUSHES
  graph-deltas to the browser over an ndjson/SSE stream** — the same producer/emitter pattern that already
  exists, not the browser orchestrating many round-trips. (My-idea, grounded in the existing stream
  architecture.)

---

## Where the no-staleness GOVERNING LAW is ALREADY held (reuse these), and where it could break

**Already resolution-native (copy this shape, don't break it):**
- The structured-output **use-gate** reads capability from the single `model_capabilities.json` and
  fail-loud-refuses on declared-false — no silent downgrade (Observed `cognition.py:490-515`). This IS the
  governing law applied to the decoder.
- `SlotBudget` derives the concurrency knee from LIVE `services.json` (`max_num_seqs`, `gpu_util`, `_profile`)
  — explicitly "NEVER a literal 32" (Observed `cognition.py:982-984`).
- The resident-brain SENTINEL means the extract layer follows the live loadout, never a pinned port
  (Observed `cognition.py:391-396`).
- The embedder is config-resolved (`DEFAULT_EMBED_*`), one knob (`COMPANY_EMB_LAYER`) reverts the whole core
  (Observed `fabric/config.py:53-67`).

**Where hardcoding could sneak into the live layer (the rigor watch-list):**
- **Icon-lookup vectors must be a generative pass, not a typed list.** The anchor's §5 is explicit: icon
  tags are a re-run embed→derive pass as icons are added. The embed/retrieve primitives support that, but
  the live layer must *re-embed on icon-add*, never freeze a vector list — else it stales the moment the
  foundry draws a new icon. (My-idea, restating the law against the embedders.)
- **The dim contract.** pplx-4b is 2560-dim, the 0.6b is 1024-dim, BGE was 1024-dim. The icon vectors and
  the query vector MUST be embedded by the SAME model or the cosine is meaningless (retrieve.py fails loud on
  dim-mismatch — good). Pin the icon-embedder to ONE config slot; if you switch embedders you must re-embed
  the whole icon corpus. (Observed `nodes/retrieve.py:40-44` enforces it; the *discipline* is the design's.)
- **The stale node docstring** (`nodes/embed.py` says BGE :8001) is exactly the kind of drift the law forbids
  — correct it to the config truth.

---

## Answers to the anchor's open what-ifs (from evidence)

- **Standing swarm vs per-utterance?** → **Per-utterance bursts.** vLLM continuous-batching means you don't
  need a standing swarm; an always-on swarm would hold KV and starve the conversation. Fire a wave at each
  pause (Observed-in-doc `03-concurrency-and-injection.md:68`).
- **Browser-drives vs Company-pushes?** → **Company drives + pushes deltas** over the existing ndjson stream
  pattern (`/api/voice/stream` producer/emitter), given the localhost one-process bridge.
- **reactflow inside the no-script CSP?** → **Not a problem.** reactflow lives on the scripted bridge-served
  canvas (same-origin to :8770), NOT the no-script page-face (:8774). The CSP worry was a category error.
- **Minimum real demo proving "talk → live graph"?** → STT (Moonshine, 0 VRAM CPU ear, built for low-latency
  live conversation, Observed `services.json:762-776`) → one `run_swarm` wave of 2–3 think-off
  schema-constrained extract roles (entities/relations) on the resident 4B → embed each noun (POST
  /api/cognition/embed → pplx :8007) → retrieve nearest icon → push a graph-delta to a bridge-served canvas.
  Every piece is built except the schema definitions + the canvas push wiring. (My-idea.)

---

## 3-line summary
The Company's fleet can be the realtime extract layer **in bursts, not as an always-on fleet**: concurrent
role-dispatch (`run_swarm`), structured/schema-constrained decode (vLLM guided-decode, fail-loud use-gate,
negative-control-verified), embed/retrieve primitives, and browser-callable HTTP routes (`/api/cognition/
run_role|embed` on 127.0.0.1:8770) all EXIST today — the squeeze is one 16 GB card whose brain-KV is shared
with the main reply (measured knee ~14 shallow → ~1–5 deep-main). The pplx **0.6b** embedder Tim referenced
is REAL (on disk, 1024-dim, MIT, INT8-native) but NOT served — it's a small serve-it task; the served pplx
**4b @ :8007, 2560-dim** does icon-lookup today; BGE @ :8001 is dormant AND collides with the FP8 brain's port.
