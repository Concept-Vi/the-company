---
type: analysis
register: descriptive
status: unconfirmed
coverage: {areas_read_full: [1, 2, 3, 8, 9, 19, 26], areas_skimmed: [4, 5], last_read: 2026-07-01}
tags: [glyphic-language, A-fusion, cv-ai, company-fleet, embedders, bridge, corpus, mode-loadout, second-hand-research]
aliases: ["READ-2 — Consolidated Research Findings for A (AI/Company Fusion)"]
---

# READ-2 — Consolidated research findings for A (the AI/Company fusion)

**What this is.** A consolidation of the live-instrument research findings that bear on **A** —
the AI/Company fusion for the conversational glyphgraph. This is **second-hand**: it summarises
what the research-wave agents (AREAs 1, 2, 3, 8, 9, 19, 26; skim 4, 5) *found*, so the A-design
can reason on total knowledge without re-reading 200KB of findings. **It is not primary evidence.**

**How to read the tags (this is load-bearing — do not flatten them):**
- **[research-OBSERVED · file:line]** — a code fact a research agent claims to have read directly.
  This is what "confirm against code" means: go to the cited line and check it. The **file:line
  pointers are the verification handles** — kept deliberately.
- **[research-PROPOSED]** — a design move the research *advanced* (the "my-idea" material). It is
  **NOT in the code**; do not hunt for it and report drift. Confirm the *premises* it rests on, not
  the artifact itself.
- **[research-OPEN]** — a gap the research explicitly could not close. Resolve it, don't assume it.

**The one governing frame (AREA-19, C1/C2 — a non-negotiable for A):** the live layer is a **fifth
CONSUMER of the four registries, never a fifth registry**. Every model touch goes through `CV_AI`;
the Company fleet enters as **`CV_AI` providers resolved by role/id**, never a second model client
sprinkled through the pipeline. The recorded failure mode this guards against is the "fourth parallel
strand" (`UNIFICATION.md:122-124`). [research-OBSERVED · INTEGRATION.md:80-83; CLAUDE.md §2]

---

## (a) The design-system CV_AI provider layer, the claude-pins, the CV_HOST seam

**The contradiction, held both ways (AREA-1).** `CV_AI`'s *plumbing is already multi-provider*, but
its *text resolution is a `claude` monoculture*.

- **Plumbing is multi-provider.** `CV_AI` is a layered registry with a `provider` layer; `resolveProvider(id)`
  binds a record to a live runtime by dispatching on **`runtime.kind`** (not a fixed list); six provider
  records are already seeded (`claude`, `openai-image`, `vision`, `host-fs`, `native-model`, `mcp-tools`).
  [research-OBSERVED · ai-seed.js:21-43; host-serializer.js:132-154; ai-registry.js:159-191, 198-238]
- **The `CV_HOST` delegation seam is already cut.** For any `runtime.kind` `CV_AI` doesn't itself
  understand, `resolveProvider` delegates to `window.CV_HOST.resolveProviderRuntime(p)`; if it returns
  a bound runtime, use it, else **throw** unknown-kind. **This is the extension point for the Company
  fleet — a new HTTP runtime kind plugs in here without editing `CV_AI`.** [research-OBSERVED ·
  ai-registry.js:229-237; host-runtime.js:155-170]
- **The `claude` pins (the real target).** Every text path resolves the literal string `'claude'`:
  the build/parse fallback and the one-off `CV_AI.complete()` (`ai-registry.js:315`, `:343`),
  `provider:'claude'` on ~27 canvas TEXT caps (`ai-capabilities-canvas.js:84`), `deck.titlechain`
  (`:105`), and `glyphic.generate` (`ai-glyphic.js:61`). AtomiCity *adds five more* pins
  (VoiceSurface.jsx:19; explore-engine.js:129,137; vi-brain.js:291,298). [research-OBSERVED, enumerated ·
  AREA-1 §2.2; AREA-9 §provider-pins]
- **`window.claude.complete` is defined NOWHERE in-repo** — it's an **ambient sandbox/editor host
  global**. Consequence: the `claude` provider only resolves *inside that host*; a standalone/exported
  tab has no text model (openai is image-only, google absent). This is a strong argument for the
  Company bridge as the real text engine. [research-OBSERVED (grep: only comments + the binder) · AREA-1 §2.3]
- **openai is image-only; google is absent.** `cvOpenAI` exposes image methods only; no text-completion.
  [research-OBSERVED · openai.js:621-644; AREA-1 §2.4]

**The proposed fix (NOT in code — do not report as drift):** a **role-resolution layer** — one config
map `ROLE_PROVIDERS` + a `defaultProvider(role)` function that `execute()`'s line 299 and the two
`'claude'` fallbacks route through, so capabilities declare a **role** (`extract-entities`,
`compose-graph`, `embed`) and flipping the whole DS to Company-local is one edit. This mirrors the
Company's `run_role`/`models_for_role`. [research-PROPOSED · AREA-1 §3; AREA-5 §3 grounds it on the
`cognition-is-role-resolved` law]

**The CV_HOST seam vs the vaporware path.** The `native-model`/`mcp-model` kinds bind
`window.CV_HOST_NATIVE.complete(...)`, but **nothing in-repo sets `CV_HOST_NATIVE`** — it is a
forward-declared export-shell seam, never injected. So the realistic primary is a **new direct-`fetch`
runtime kind** (proposed name `company-http`), modelled on `openai.js`'s direct-to-OpenAI shape, hitting
the bridge. [research-OBSERVED (no `CV_HOST_NATIVE =` assignment) · AREA-1 §4.4; PROPOSED runtime · §4.3]

---

## (b) The Company fleet — role-resolution, run_role/run_swarm, structured outputs, the embedder, latency reality

**Role-resolution (cognition-is-role-resolved).**
- A **role** is file-discovered (`roles/<id>.py`) carrying `prompt_template`/`output_schema`/
  `model_binding.requires`; **`models_for_role`** returns models whose `provides ⊇ requires`.
  [research-OBSERVED · mcp_face/server.py:495-509]
- A **resident-brain SENTINEL** defaults every entry point to whatever brain is *actually running*
  via `active_brain()` — cognition follows the live loadout, never a pinned port. An explicitly-passed
  model id is used verbatim (endpoint resolved from the id). [research-OBSERVED · cognition.py:391-406;
  mcp_face/server.py:747-758]
- **`resolve_model` is BUILT but DORMANT** — its own docstring says "Phase 1 … NOTHING is routed
  through it yet." Live role→model resolution flows through **`roles.resolve_binding`**, which carries
  the **`satisfied` FLOOR trap**: an unmatched role with a `default_model` returns the resident brain
  with `satisfied=False` — it *looks* resolved but silently floored. **Assert `satisfied`, never a
  non-empty `model`.** [research-OBSERVED · model_routing.py:13-15, 22-28, 61-81; AREA-8 §4]

**Concurrency — `run_swarm` (this IS the extract layer, today).**
- `run_swarm(roles, ctx, store, …)` fires a wave of role-runs **concurrently** via a `ThreadPoolExecutor`
  sized to the swarm sub-pool, barriers per wave, serializes store writes behind the barrier; each role
  writes validated JSON to `run://<turn>/<role>`; **fail-loud** (a role failure re-raises after the
  barrier). This is Tim's extraction-vs-judgment law as the field's own mechanism: many small role-runs
  EXTRACT in parallel, one strong role JUDGES. [research-OBSERVED · cognition.py:1413-1482]
- The map/reduce siblings: **`run_items`** (1 role × N units — the ingest DIGEST-FAN, per-unit
  resilience), **`run_reduce`** (N→1 join: role|rule|cluster modes). [research-OBSERVED · cognition.py:1590+, 2389+]
- **Threads not async, no client batching needed:** blocking transport releases the GIL during socket
  I/O; N threads = N concurrent in-flight requests; **vLLM does continuous batching server-side.**
  → per-utterance bursts of N calls, NOT a standing always-on swarm (which would hold KV and starve the
  conversation). [research-OBSERVED-in-doc · 03-concurrency-and-injection.md:68,96; AREA-2 §a]

**Structured / constrained outputs (the extract layer's lifeblood — strongest reuse finding).**
- Two enforcement layers: **client validate/retry** (`run_role(json=True, schema=<Pydantic>)`) and
  **server-side schema-constrained decode** (vLLM 0.21 guided decode; a **negative control proved
  xgrammar constrains the decode** — not "json_object hope"). [research-OBSERVED / OBSERVED-in-doc ·
  cognition.py:318-320, 492-515; Completion Criteria C1.4]
- A **fail-loud use-gate**: declared-false `json_schema` → REFUSE (raise), never silent downgrade;
  both residents (AWQ + FP8) declare `json_schema=true`. [research-OBSERVED · cognition.py:490-515]
- The output field-type registry supports `enum`/`object`/`list[object]` — nested glyphic/edge schemas
  ARE expressible. [research-OBSERVED · AREA-2 §b]
- **CAVEAT to confirm end-to-end:** a `transport.py` passthrough for some params was flagged **"not yet
  complete"** — verify the `json_schema` field actually forwards to vLLM before relying on it.
  [research-OPEN · AREA-1 §4.6; AREA-2 corroborates]

**The embedder (corrects earlier BGE/0.6b assumptions).**
- **Served, operative:** `perplexity-ai/pplx-embed-context-v1-4b` @ **:8007**, **2560-dim**, INT8 +
  unnormalized (compare via COSINE); custom transformers server (vLLM can't load `PPLXQwen3`);
  co-resides in the interaction/instrument loadouts. This is the icon-lookup embedder today.
  [research-OBSERVED · fabric/config.py:39-66; services.json:513-529]
- **The `pplx-embed-v1-0.6b` Tim referenced is REAL but NOT served** — on disk (5.6G, 1024-dim, 32K ctx,
  MIT, INT8/binary quant-aware). Using it is a **small serve-it task** (custom transformers server on a
  fresh port), not "already there." It is arguably the *right* icon-lookup embedder (smaller, cheaper
  NN); interim, the served 4B does the job. [research-OBSERVED · model_capabilities.json:596-629; no
  services.json entry]
- **BGE-M3 @ :8001 is DORMANT and PORT-COLLIDES with the FP8 brain** (`chat-4b-fp8` also :8001) — they
  are mutually exclusive. The pplx-4B @ :8007 is the co-resident one. `nodes/embed.py`'s docstring still
  says "BGE @ :8001" (stale — the node reads `DEFAULT_EMBED_*` = pplx). [research-OBSERVED · services.json:476
  vs :188; nodes/embed.py:5-6]
- Embed/retrieve primitives are typed + dim-enforced fail-loud: `nodes/embed` (`text→vector`),
  `nodes/retrieve` (cosine top-K, ~100× vectorized). `run_role(op="embed")` reuses the same path.
  [research-OBSERVED · nodes/embed.py:18-50; nodes/retrieve.py:21-55; cognition.py:398-427]

**Latency reality (the correction to hold — do NOT let it drift back to optimism).**
- **One resident brain, shared KV.** There is no fleet of separate small models — one brain
  (`chat-4b-fp8` :8001 in the everyday loadout) with a concurrency budget over it; its KV pool is
  **shared with the main voice reply.** [research-OBSERVED-in-doc · cognition.py:976-1040; AREA-2 §a]
- **The measured knee: ~14 concurrent at shallow main context, collapsing to ~1–5 when the main reply
  is deep** (`SlotBudget.from_registry` computes it from live services.json, never a literal 32).
  **Do NOT cite the "c=32 → 2241 tok/s" figure** — it was 4K-context/higher-util, NOT the co-resident
  voice config; it is the corrected-away number. Decode ~100 tok/s on the 4B. [research-OBSERVED-in-doc ·
  Completion Criteria C0.5/C1.2; Research Synthesis.md:5,40]
- **`think=False` is essentially mandatory on the hot path** — suppressing the reasoning trace took a
  one-word structured answer from 1304 → 43 tokens (~30×). The finished-thought judge lesson generalises:
  *any* per-pause/per-utterance model call on the live path must be a fast no-think classifier, or the
  live feel dies (deepseek-reasoner measured ~6.5s/pause = unusable). [research-OBSERVED · mcp_face/server.py:696-702;
  suite.py:6552-6555]
- **Operating shape:** a wave of ~10–14 short, `think=False`, schema-constrained extract roles fired at
  each conversational pause, with R slots reserved so the operator's turn never stalls — concurrent with
  each other, NOT concurrent with a 28s reply. A higher-util swarm-brain config (~0.63) is the named lever
  to grow KV, but it's a GPU-reconfig (needs-tim), not free. [research-OBSERVED-in-doc · AREA-2 §a]

---

## (c) The bridge /api/cognition surface + the CORS open-question

**The door: the bridge HTTP/SSE API at `127.0.0.1:8770`** (a single-process `ThreadingHTTPServer`; a
single-source `BRIDGE_ROUTES` tuple, drift-checked). The vLLM model ports (:8000/8001/8002/8007) have
**no CORS** — a browser cannot fetch them directly; the bridge is the only door. [research-OBSERVED ·
bridge.py:45-140, 3725; AREA-1 §4.1; AREA-26 §d]

**The cognition surface A would target** (pass a *role*, the Company picks the model):
- `POST /api/cognition/run_role` — fire one role → `run://` output. [research-OBSERVED · bridge.py:825-831]
- `POST /api/cognition/embed` — embed-op role → `{vector, dim, model}`. [research-OBSERVED · bridge.py:844-853]
- `POST /api/cognition/run_items` / `/run_reduce` / `/preview_turn`; `GET /api/cognition/inputs` /
  `/field_types` / `/models_for_role`. [research-OBSERVED · bridge.py:832-843, 814-824, 2029]
- Streaming: `POST /api/chat/stream` (NDJSON `{type:part}`/`{done}`), `POST /api/voice/stream`
  (transcript→parts→wav→reply→done), `GET /api/stream` (SSE tail of the shared `events.jsonl`, gapless
  reconnect via `Last-Event-ID`). [research-OBSERVED · bridge.py:2946-2950, 2943-2945, 1449-1451]

**The CORS question — present BOTH readings, they were left different:**
- **AREA-1 left it OPEN** ("the one open fact between here and a working demo"): it confirmed the *vLLM*
  ports don't send CORS but did **not** confirm the bridge's posture on :8770. [research-OPEN · AREA-1 §4.2, §4.5]
- **AREA-2 was DEFINITE:** grep found **no `Access-Control-Allow-Origin` anywhere** and the bind is
  **127.0.0.1-only** → a cross-origin browser (e.g. vite dev :5173) is **blocked**; the instrument
  surface must be **SAME-ORIGIN** (served behind :8770) or use a dev proxy / a CORS allowance added
  Company-side. [research-OBSERVED (grep) · AREA-2 §d]
- **Resolution for A:** treat "same-origin, or add a permissive-CORS option to :8770" as the working
  assumption; the reconcile is to *read the bridge headers directly* to close AREA-1's open vs AREA-2's
  definite. AREA-2 also resolved the "reactflow-in-CSP" worry: the no-script page-face (:8774) is a
  deliberately separate origin and **cannot** be the instrument; reactflow lives on the *scripted,
  bridge-served* canvas — not a CSP problem. [research-OBSERVED · services.json:114-124]

**Browser-drives vs Company-pushes (open what-if, answered from architecture):** given a localhost
one-process bridge with an existing server-side NDJSON producer/emitter, the natural fit is **the Company
drives the extract→resolve→place pipeline server-side and PUSHES graph-deltas** to the browser over the
existing stream — not the browser orchestrating many round-trips. [research-PROPOSED, grounded · AREA-2 §d; AREA-3 §9]

---

## (d) The corpus / embed / index apparatus (how meaning→glyph resolution + generate-on-miss rides it)

**The spine (AREA-26):** *Walk → Digest → Type → Corpus-Record (`cas://` + `run://` + event) →
Embed-to-Space (`vec://`) → Query (vector ∥ lexical → RRF fuse → rerank) → Resolve-by-address (ONE
resolver) → serve over the bridge.* The property to carry into A: **ONE addressed state, ONE resolver** —
every thing (code symbol, UI element, session, decision, extraction, corpus record) is a row reachable by
a typed `scheme://` address; `resolve_address` is the single seam turning an address into content.
[research-OBSERVED · corpus.py:4-7; cognition.py:1129-1415]

**Ingest / embed / index (each a reuse target for the icon corpus):**
- Two ingest doors: `ingest_paths` → a projection SPACE (walk → `repo_digest` role fan via `run_items`
  → typed `corpus.record`, **lineage-gated** [session/round/project required or RAISE] → embed), and the
  **dragnet extract-bake → the `extractions` space** (the rich entities/claims/relations superset — the
  likely door for a non-repo document corpus). [research-OBSERVED · suite.py:11137-11320; freshness.py:78-95]
- **`vector_index.build_index`** — content-hash **incremental** (re-embeds only NEW/CHANGED; an
  all-unchanged rebuild touches the endpoint zero times), **space-keyed** (`vec://<item>#space=<proj>#emb=<layer>`
  — the same item under multiple lenses/embedders is distinguishable → the substrate for "a glyph means a
  FIELD, not a single thing"), **degrade-with-warning** (embedder down → no vectors, loud event, never a
  fabricated/zero vector). [research-OBSERVED · store/vector_index.py:64-140]
- **Query:** `query_index` (fast numpy matmul path, honest-empty + weak-match `<0.33` flag);
  `corpus_fusion.query_hybrid` (vector ∥ lexical → **RRF late-fusion by RANK only** — never concat/avg
  across bge-1024 vs pplx-2560; degrade-honest to lexical-only). [research-OBSERVED · vector_index.py:143-218;
  corpus_fusion.py:75-146]
- **Freshness / auto-reindex:** `freshness.reconcile_space` (staleness-diff → embed only changed →
  retract orphans → re-check); the bridge runs an auto-freshness daemon. **This IS the discipline the
  icon index needs — re-embed on icon-add, never a frozen vector list.** [research-OBSERVED · freshness.py:22-95]

**How meaning→glyph resolution + generate-on-miss rides this (the fusion):**
- **RESOLVE (noun → glyphic)** = embed the spoken noun (`run_role op=embed` / `POST /api/cognition/embed`)
  → cosine-rank against pre-embedded icon vectors (`retrieve`) → threshold. All primitives exist.
  [research-OBSERVED · cognition.py:398-427; nodes/retrieve.py — via AREA-2 §c]
- **The current icon-tag store is the headline STALENESS BUG (already live, not hypothetical):**
  `CV_ICONS.facets` is a **frozen hand-written literal** `name→{domain,kind,tags}` (131/132 faceted,
  0 empty tags — dense, but the provenance is a snapshot), and `CV_ICONS.search` is **purely lexical
  substring** — no embedder in `claude-ds/` at all. Tags are whatever the LLM wrote at save time, never
  re-derived. This violates the no-staleness law **by construction**. [research-OBSERVED · cv-icons.js:246,273-418,430,498-518;
  AREA-4 §0-1; AREA-5 §2]
- **The fix (proposed):** make icon tags a **derived projection** — embed each icon's representative
  text via the existing `nodes/embed`, tags/nearest a re-runnable computed field (the `symbols.py
  semantically_nearest[]` precedent, `nodes/embed`+`retrieve` reused not reinvented); resolve
  noun→glyphic by cosine; below threshold → `glyphic.generate` (the foundry); deep-link domain/kind
  from a **file-discovered** taxonomy (kill the silent `'feature'` default). [research-PROPOSED, grounded
  in existing precedents · AREA-5 §2; symbols.py:235-309]
- **GENERATE-ON-MISS station already exists:** the Glyphic Foundry (`system/glyphic-foundry.html`) is a
  working conversational propose→feedback→iterate→**Save** loop — candidates live-render as glyphics,
  Save → `CV_ICONS.add` → **rebuilds the Symbol axis** so the icon appears instantly. It routes through
  `CV_AI.execute('glyphic.generate'/'glyphic.save')` (never raw `window.claude`). **Its live-provider
  path is flagged owed/unfinished (verified demo-side only).** The fusion adds STT in front + semantic
  lookup before generate + the saved candidate becoming a live graph node. [research-OBSERVED (structure)
  · glyphic-foundry.html:106-242; ai-glyphic.js; live-provider path research-OPEN · AREA-19 A5/B1]

**Adding a glyph identity to the addressed state (additive recipe):** append a scheme to `SCHEMES`
(`contracts/address.py:145` — 21 today), optionally declare a `parse_<x>_address` grammar, add one
lazy-import resolver branch in `resolve_address`. Modes, projections (spaces), relation-types are all
file-discovered registries (drop a file, no code edit). [research-OBSERVED · address.py:145,164-168;
cognition.py:1129-1415; AREA-26 §b]

---

## (e) The mode/loadout entry + the CV_MODE-vs-modes_registry reconcile

**The entry mechanism Tim named ("a MODE/LOADOUT the system SWITCHES INTO") already exists end-to-end
and is acceptance-verified (AREA-8).** The SPINE is Observed/verified; the glyphgraph-specific *files*
are proposed — hold that split.

**The spine (Observed / acceptance-verified — confirm the cited lines, expect them to exist):**
- A **MODE is a file-discovered registry row** (`modes/<id>.py` with a module-level `MODE` dict;
  `discover_modes` = listdir→importlib, fail-loud, id==stem). 8 shipped modes, explicitly a **starter
  set, "none final"** — the open door. Schema fields include `directive`, `resolution`, `consent`,
  `grain/shape/stage`, `live`, `reserve_r/per_role_ctx/main_ctx_tokens`, `brain_config`, optional
  `loadout_class`/`voice`. [research-OBSERVED · modes_registry.py:1-91, 30-32; modes/AGENTS.md]
- **`Suite.set_mode(mode)`** writes mode + clears overlays (FREE, always succeeds), emits presence to
  the toolbar, and **`_maybe_surface_loadout_swap`** — if the new mode's `loadout_class` services aren't
  resident, **SURFACE a confirm** (never auto-actuate). The switch is free; changing the resident loadout
  is CONFIRM-gated governance; the autonomous loop can raise the confirm but **never self-approve** it.
  [research-OBSERVED · suite.py:2626-2641]
- **The atomic-switch actuator** (Tim's Loadout-Resolution "repoint-RHM fix", BUILT + verified):
  `apply_loadout(sid)` [approval READ FROM INBOX, never a caller flag] → `ensure_resident(evict,wait)`
  [RAM+VRAM-gated, **can't OOM**] → `_repoint_rhm_for_loadout` [finds the loadout's OWN brain, **VERIFY
  BY USE** via a real inference probe; if the new brain won't answer → **REVERT to prior + raise** — "no
  silent broken brain"]. Two doors, one repoint logic: the mode door + the bare CLI door
  (`company up @loadout`). [research-OBSERVED · suite.py:2726-2837]
- **A LOADOUT (combo) is a services.json entry** with class-variants (`extends`/`swap`/`add`/`remove`),
  resolved centrally fail-loud. Real: `interaction` (`embed-pplx`,`chat-4b-fp8`,`rerank-jina`,
  `stt-moonshine`,`tts-kokoro`), `interaction-fp8` (fits 16GB), `instrument` (`bridge`,`embed-pplx`).
  [research-OBSERVED · ops/services.json combos]
- **A WRINKLE for Tim:** two loadout concepts on one mode row — `loadout_class` (a services.json combo,
  full atomic switch) vs `brain_config` (a gpu_util variant of ONE brain, **`variant_applied=False` /
  needs-tim**). For the glyphgraph, use `loadout_class` — it's the only one that loads *several* services
  together. [research-OBSERVED · ops/cli/capabilities.py:558-602; AREA-8 §2]
- **The RHM** is a config slot + conversation engine + source-router (no `rhm_*.py`; lives in `suite.py`
  + `brain_router.py`). `rhm_config()`/`set_rhm_config()` hold the brain pointer + persona + voice slots
  + per-role bindings + `think` (default False). `voice_enabled()` precedence: mode `off` → never; else
  operator override; else the mode's `voice` default. [research-OBSERVED · suite.py:3084-3196, 3142-3158]
- **The CONSENT axis governs the voice-correction loop's safety** — `consent:'act'` routes RHM verbs
  through `autonomous_dispatch` **by verb posture** (reversible AUTO verbs run; CONFIRM verbs surface;
  **never self-approves**). "add/mutate a node" reversible → live; destructive → surfaces. `consent:'offer'`
  = ask first (a one-field change). This is the loop-safety the layer-1 plan never named. [research-OBSERVED ·
  suite.py:6986, 5696]

**The glyphgraph-specific artifacts (PROPOSED — do NOT hunt for these in the source):**
- `modes/glyphgraph.py` (a presence mode: directive to co-author the graph, `consent:'act'`,
  `loadout_class:'glyphgraph'`, `voice:'on'`, `live:['per-turn','background','sense']`).
- `services.json` combo `glyphgraph` (`extends: interaction` — the pipeline's service list IS the combo:
  embed-pplx=icon lookup, chat-4b-fp8=extract workers + composer, stt=LISTEN, tts=NARRATE).
- `roles/glyph_entities.py`/`glyph_relations.py`/`glyph_states.py`/`glyph_placement.py` (extract roles
  modelled on `judge`: `thinking:False`, schema-constrained, short-context, no tools), fired via
  `run_swarm`; `roles/glyph_compose.py` the strong JUDGE role.
- Entry path: `set_mode('glyphgraph')` → confirm → `apply_loadout` → resident swarm + repointed brain +
  voice on + directive injected. [research-PROPOSED · AREA-8 §5]

**The CV_MODE ↔ modes_registry reconcile (AREA-9 — and the task's-own-premise correction):**
- **Premise correction:** the Company `modes_registry` is **server-side Python**, NOT "a separate
  browser-side mode system." [research-OBSERVED · modes_registry.py:1-21; AREA-9 §b]
- They are **two different axes sharing one registry mechanism**, not duplicates:
  - **CV_MODE** (`atomicity/mode-engine.js`) = *what a CLICK does* (`operator`/`inspect`; pushes the
    mode's `behaviours` as `CV_AI`'s active set) — the browser interaction dial.
  - **Company modes_registry** = the RHM's *presence/consent/resolution posture* — the server-side
    conversation dial.
- **Reconcile, do NOT merge** (resist the unions reflex here — wrong level). The instrument needs BOTH:
  canvas interaction-modes (CV_MODE-shaped: talk/arrange/inspect/correct) AND a conversation presence-mode
  (a `modes/<id>.py` whose directive is "extract structure and build the glyphgraph"). Same mechanism,
  two homes. [research-OBSERVED · mode-engine.js:9,60-89; AREA-9 §b]

**Cross-stream note (belongs to sibling streams; referenced, not reproduced here):** AREA-9 found a
**working non-voice skeleton of the correction loop** in AtomiCity (interpret→action-protocol→
override-stick→shot-capture→learn), so the loop's novelty is the *voice front* + the *glyphgraph
surface*, not the loop; AREA-3 found the **transcript is hardwired to ONE consumer (the brain)** — the
build is to fan `transcript → {brain, extract-swarm}` — and narration is a solved sink (`/api/say`);
AREA-19 holds the one-IR / no-fifth-strand / stable-incremental-placer constraints. These feed the
graph/voice streams; for A they matter only as: (i) the swarm is fed by a transcript fan-out, (ii)
everything downstream of STT is server-side (favourable), (iii) A must not become a second model client.

---

## Open items A must resolve (the research-OPEN set, gathered)
1. **Bridge :8770 CORS posture** — AREA-1 open vs AREA-2 definite-no-CORS/127.0.0.1-only. Read the
   bridge headers directly; decide same-origin-serve vs add-CORS.
2. **`json_schema` end-to-end forward** — vLLM honours it, but a `transport.py` passthrough was flagged
   "not yet complete." Verify the schema field reaches vLLM before relying on structured extraction.
3. **`run_role` HTTP response shape** — the route exists; the exact JSON keys weren't read. Confirm before
   wiring a `company-http` runtime.
4. **The Foundry's live-provider path** — flagged owed (verified demo-side only); the generate-on-miss
   station needs a live provider bound.
5. **Serve the pplx-0.6b** (optional/later) — a small serve-it task if the 1024-dim smaller embedder is
   wanted for the icon corpus over the co-resident 2560-dim 4B.

---

## 3-line summary
For A, the machinery mostly EXISTS and is verified: `CV_AI` is already multi-provider with a `CV_HOST`
delegation seam (the pins to dissolve are the literal `'claude'` fallbacks; a role-resolution layer is
*proposed*), the Company fleet's concurrent `run_swarm` + fail-loud schema-constrained decode + the
served pplx-4B@:8007 embedder + the corpus/embed/index/freshness apparatus are all built, and the
MODE/LOADOUT entry (`set_mode`→confirm→`apply_loadout`→`ensure_resident`→`_repoint_rhm`, verify-by-probe)
is acceptance-verified — glyphgraph rides it as a proposed mode+combo+roles, NOT a parallel app.
The honest squeeze is one 16GB card (one resident brain, KV shared with the reply; knee ~14 shallow →
~1–5 deep, `think=False` mandatory; ignore the corrected-away 32/2241 figure), the icon-tag store is a
LIVE staleness bug (frozen literal + lexical search, no embedder in claude-ds), and the load-bearing
opens are the bridge :8770 CORS posture (AREA-1 open / AREA-2 definite-no) and whether json_schema
forwards end-to-end.

Path: `/home/tim/company/design/claude-ds/analysis/glyphic-language/A-fusion/reads/READ-2-findings.md`
