# CC-3 · The MAP stage — the configurable worker tier + the contained-unit mechanics

> Companion to `CORPUS-CHAIN-ANCHOR.md`. My allocated area: **the MAP stage** — the cheap parallel layer
> of the corpus-chain. Two halves: (a) the **configurable worker tier** (the three model populations, how
> each reads the registry, the real concurrency/cost/auth shape of each, the contention management); (b) the
> **contained-unit mechanics** (what a good "unit" is, the ctx→messages seam that makes "unit = a file" real
> at all, the chunk-and-compose sub-tier the over-context `suite.py` forces, the `unit_selector`, and how the
> map fans concurrently under `SlotBudget`).
>
> I read the real `run_swarm`/`run_role`/`run_jury` engine, the model registry (`ops/services.json`,
> `ops/cli/models.py`, `ops/cli/gpu.py`, `ops/cli/capabilities.py`), the role/binding machinery
> (`runtime/roles.py`), the strong-tier subprocess channel (`runtime/implement.py`), the fabric transport
> (`fabric/transport.py`/`client.py`), and I measured the real corpus + verified Ollama Cloud's live specs on
> the web. Marking per Tim's template: **Observed (file:line)** / **Inferred** / **External-prior-art** /
> **Your-idea (mine)**.
>
> **The one-line correction this companion makes:** the anchor's Chain treats `worker_model` as a single knob
> selecting uniformly among three tiers — but the three tiers are **two invocation substrates with three
> different concurrency governors**, and `SlotBudget`/`VramGate` (the contention machinery) is a *local-tier-
> only* concern. The "configurable, read from the registry" claim is **shape-ready but not wired** (SEM-1's
> "80% there, 20% net-new", reached from the tier side), and the contained-unit constraint has *two* distinct
> net-new seams behind it (a ctx→messages generalization and a chunk-compose tier) that the anchor folds into
> one casual "many bounded reads."

---

## 0 · TL;DR — the five corrections that change the MAP picture

| Anchor framing | Reality (grounded) | Where |
|---|---|---|
| `worker_model` = one knob over three tiers | **Two invocation substrates** (OpenAI-compat HTTP for local 4B + Ollama Cloud; a *subprocess* for Claude Code) + **three governors** (VRAM/KV knee · plan-quota · safety cap). Configuring "strong workers" = a *different runner*, not a model-param swap. | `transport.py:53`, `cognition.py:114`, `implement.py:7-14`, `implement.py:43` |
| "both worker and synth models are configurable, read from the model registry" | The *shape* is ready (`run_role`/`run_swarm` take `base_url`/`model`; the capability-query `role.requires ⊆ provides` exists; cloud entries are in the catalog) — but **every live caller passes `RESIDENT_BASE_URL`/`RESIDENT_MODEL`**, `resolve_binding` is "resident-only today", and `_one()` calls `gate.slot()` *unconditionally* (a VRAM bound that is *wrong* for a cloud worker). The wire is net-new. | `cognition.py:52-53,571`, `roles.py:255`, `cognition.py:570` |
| Ollama Cloud "~6-10 concurrent" | **Plan-bound: Free 1 / Pro 3 / Max 10 concurrent**, queued beyond (rejected when the queue fills). Not a fixed 6-10. Loads **zero local VRAM** → `SlotBudget` is meaningless for it. | External (ollama.com/pricing) |
| "read the whole repo means many bounded reads" (one seam) | **TWO distinct net-new seams**: (1) a **ctx→messages** generalization (`run_role` hardcodes `f"Utterance: {utterance}"`), and (2) a **chunk-and-compose** tier for `suite.py` (716,125 B ≈ 180K tok vs the 65,536 window). Chunk-compose is *intra-file*; it is **not** the cross-file *pairing/join* SEM-2 needs — related machinery, different jobs. | `cognition.py:109-113`, measured, `services.json:59` |
| the strong worker tier "= Claude Code subagents" (a ready tier) | `implement.py` (`claude -p`, `CONCURRENCY_CAP=3`) is the **governed self-modify channel**, not a map-worker pool. Re-using it as the strong MAP tier is **my proposal**, not current use. The *live* existence-proof of the strong tier is **this research-wave itself** (manual Claude Code subagent fan-out — the recursion the anchor names). | `implement.py:1-14,43` |

None of these kills the MAP idea. Each says: the cheap parallel layer is real and largely built, but **"configurable worker tier" is a wire-and-a-runner-switch away, not a present property**, and **"unit = a file" hides two net-new mechanics**, not zero.

---

## 1 · The three worker tiers are TWO invocation substrates with THREE governors

This is the centerpiece correction. The anchor (§4) writes:

```
WORKER (map)    local 4B swarm (~14 concurrent, cheapest)  ·  Ollama Cloud (~6-10 concurrent, more capable)
                ·  Claude Code subagents / cloud Opus (strongest)
```

…and the Chain schema (§3) gives `worker_model` as a single field. The clean reading is "pick one of three by a model id." **The code says the three are not interchangeable values of one field** — they split across two fundamentally different invocation paths and three unrelated concurrency limiters.

### 1.1 · Substrate A — the OpenAI-compatible HTTP path (local 4B + Ollama Cloud)

**[Observed]** `run_role` (`cognition.py:93-119`) fires through `transport.openai_transport(base_url=…)` →
`client.complete(...)`. The transport is **repointable by `base_url`** and defaults `api_key="ollama"`
(`transport.py:53`, module docstring `transport.py:6`: "both OpenAI-compatible — repointable by `base_url`").
So the *local 4B* and *Ollama Cloud* are the **same code path** — they differ only in:
- `base_url` (`http://127.0.0.1:8000/v1` resident vs `https://ollama.com/v1` cloud — Inferred from the OpenAI-compat shape);
- `api_key` (the cloud tier needs a real key, not the literal `"ollama"` sentinel — **External**: Ollama Cloud requires an API key / signed-in account);
- the concurrency governor (§1.4).

**[Observed]** `run_swarm` already threads `base_url`/`model` through to each `run_role` call
(`cognition.py:526,571`). So the *shape* to point the swarm at a cloud endpoint is present. The bind is the gap (§2).

### 1.2 · Substrate B — the subprocess path (Claude Code, strong tier)

**[Observed]** The strong tier is **not OpenAI-compatible** and **cannot ride `run_swarm`/`run_role`.** It is a
subprocess: `runtime/implement.py` spawns `claude -p "<instruction>" --output-format json --add-dir <repo>
--permission-mode plan` and captures structured JSON (`implement.py:1-14`). This is a *completely different
runner* — different invocation (process, not HTTP), different result shape (parsed CLI JSON, not a chat
completion), different governance (permission modes, arming gates: `permission_mode()`/`wire_armed()`,
`implement.py:48-72`).

**[Observed]** Its concurrency is a **safety cap**, not a resource knee: `CONCURRENCY_CAP =
int(os.environ.get("COMPANY_WIRE_CONCURRENCY", "3"))` (`implement.py:43`) — "W7: max concurrent claude -p".
That is a bound on parallel *self-modifying* runs, set for governance, not for VRAM or KV.

**[Inferred / Your-idea]** Therefore: the anchor's "the research-wave *face* configures strong workers" does
**not** mean "`run_swarm` with `worker_model=opus`." It means the research-wave face dispatches its per-area
workers through a **subprocess fan-out** (the `implement.py` shape, or a read-only variant of it), entirely
*outside* `run_swarm`. The MAP runner must therefore be **tier-polymorphic**: it picks the substrate (HTTP
swarm vs subprocess fan-out) from the tier, not just a model id. This is the single biggest "yes, but
actually" in my area — the Chain's `worker_model` field implies a uniformity that the runtime does not have.

**[Observed, honest mark]** Reusing `implement.py` as a *map* tier is **my proposal, not current use.**
`implement.py` exists to *self-modify* (W-group, the decision→implementation wire), behind a default-`plan`
read-only posture and an `acceptEdits` arming gate. A read-only deep-read worker ("read this area, emit a
grounded companion") fits its subprocess+structured-JSON shape, but it is not what the unit does today. The
*live* existence-proof that the strong MAP tier works at all is **this very research-wave**: six Claude Code
subagents (of which I am one) fanned over allocated areas, each emitting a structured companion — the manual
form of exactly the strong-worker MAP the anchor wants to productize (this is the recursion the anchor §0/§intro names).

### 1.3 · How each reads the registry (the three keyings)

**[Observed]** The model machinery has *three* keyings (B4), and the MAP tier touches all three:
- **`ops/services.json`** — the *deployment* registry: what's locally served, with `config.model`,
  `gpu_util`, `max_model_len`, `max_num_seqs`, `port` (`services.json:55-80` for `chat-4b`). `models.py`
  reads/swaps it (`models.py:36-70`: `swap()` rewrites `config.model` and restarts the unit).
- **`ops/cli/gpu.py`** — the *VRAM authority*: `budget_vram`/`check_fit`/`plan_eviction` (`gpu.py:32-43,113-126,176-191`).
  This governs whether a *local* model fits; it has **nothing to say about a cloud worker** (zero local VRAM).
- **`ops/cli/capabilities.py`** — the *capability catalog* keyed by model-id: `provides` sets per model
  (`capabilities.py:106` resident = `["chat","json","tools","fast","no-think"]`; `capabilities.py:111-122`
  `deepseek-v4-pro:cloud` = `["chat","json","tools","thinking","reasoning"]`).

**[Observed]** The **binding query** that selects a tier for a role is `resolve_binding` (`roles.py:251-284`):
`role.requires ⊆ provider.provides` — a set-query, "never hand-written suitability prose" (`roles.py:244-248`).
A role that needs deep reasoning declares `requires: ["thinking","reasoning"]`; the local 4B's `provides`
(`["chat","json","tools","fast","no-think"]`) **does not satisfy it** → it falls through to a cloud/strong
provider. **This is the exact mechanism by which the research-wave face gets strong workers and the
coherence-scan face gets the cheap 4B** — declared `requires` on the chain's map-role, resolved against the
catalog. That is the right design and it is *partly* built.

### 1.4 · The three governors (and why one of them is local-only)

| Tier | Substrate | Concurrency governor | Real bound | VRAM | Where |
|---|---|---|---|---|---|
| **Local 4B swarm** | OpenAI HTTP | `SlotBudget`/`VramGate` — KV/seq knee | **8–14**, file-size-dependent (KV-binds >~5K tok/file) | shared resident pool | `cognition.py:385-450,553`; SEM-1 §2.3 |
| **Ollama Cloud** | OpenAI HTTP | plan quota | **Free 1 / Pro 3 / Max 10** concurrent, queued beyond | **zero local** | External (ollama.com/pricing) |
| **Claude Code** | subprocess | safety cap | `COMPANY_WIRE_CONCURRENCY=3` | **zero local** | `implement.py:43` |

**[Observed → Inferred]** The sharp consequence: **`SlotBudget`/`VramGate` is a local-tier-only mechanism.**
`_one()` in `run_swarm` calls `with gate.slot():` *unconditionally* (`cognition.py:570`) — it acquires a VRAM
permit for *every* worker. For a local 4B that is correct (the resident pool is the contended resource). For
a **cloud** worker it is *wrong*: the cloud call holds no local VRAM, so gating it behind the local
`VramGate` artificially throttles the map to the local knee (8–14) when the real cloud bound is the plan
quota (1/3/10) — and worse, it would let cloud workers *consume local cognition slots they don't need*. So
the map runner needs a **per-tier governor switch**: VramGate for local, a plan-quota semaphore for cloud, a
`CONCURRENCY_CAP`-style cap for subprocess. **This is net-new** and the anchor doesn't see it.

**[Your-idea] Offloading the map to a cloud tier is itself a contention *escape*.** SEM-1's contention story
(§5: a 400-file local sweep holds ~14 slots for ~1 min and *delays a live cognition wave* on the same pool;
the fix is a polite `reserve_r`) is a *local-tier-only* problem. If the chain's map-role binds to **Ollama
Cloud** (because the per-area task is deep enough to need it, or simply to keep the card free), the local KV
pool stays entirely free for the live cognition stream — the sweep and the conversation no longer contend at
all. So tier selection is *also* a contention lever, not only a capability/cost lever. The anchor frames the
tiers as a capability ladder; they are *also* a "where does the load land" dial.

### 1.5 · The per-unit cost/latency shape per tier, on the REAL corpus

**[Observed, measured this session]** The corpus: **272 first-party `.py`/`.ts`/`.tsx` files** (glob:
`find . -type f \( -name '*.py' -o -name '*.tsx' -o -name '*.ts' \)` excluding
`node_modules|site-packages|.venv|/venv/|.voice-venv|dist/|build/`), **48,035 Python LOC**. (Reconciliation:
SEM-1/SEM-6 cite ~232 Python + ~234 first-party; my 272 includes the 39 TS/TSX. The 48K LOC and the
~400-file-with-markdown total are consistent across all three — anchor on those.) `suite.py` =
**716,125 bytes ≈ 180K tokens** (measured `wc -c`), 2.75× the 65,536 window.

**[Inferred, from SEM-1's measured numbers + the per-tier specs]** Per-unit MAP shape, a "read one file → emit
a ~200-token structured finding" task:

```
LOCAL 4B          per-unit decode ~100 tok/s steady (BENCHMARK_FACTSHEET:64); prefill ~28K tok/s
                  → a ~200-tok finding ≈ ~2s/unit decode; the 400-file core ≈ ~1–2 min at live conc (SEM-1 §2.4)
                  cost: $0 (resident) · concurrency: 8–14 (KV-bound on real files) · VRAM: contends with cognition

OLLAMA CLOUD      latency: cloud round-trip (no local measurement; External: GPU-time billed, level-1..4 by model)
                  → the 400-file core, at Max's 10 concurrent vs the cloud per-call latency, is comparable-or-slower
                    than local for a SHALLOW task (the gain is CAPABILITY/offload, not speed)
                  cost: usage-metered (session-5h + weekly caps; level-1 light .. level-4 heavy) · concurrency: 1/3/10 · VRAM: 0 local

CLAUDE CODE       latency: a full `claude -p` session per unit — SECONDS-to-MINUTES, expensive
                  → NEVER for a 400-file shallow map (cost prohibitive); ONLY for a SMALL set of deep per-area units
                    (the research-wave face: ~6 areas, not ~400 files)
                  cost: per-session (highest) · concurrency: CONCURRENCY_CAP=3 · VRAM: 0 local
```

**[Inferred] The tier-fit rule, grounded:**
- **Cheap-for-contained-extraction** → local 4B. The per-unit task is bounded structured extraction (SEM-3:
  the 4B's strong mode); ~400 files in ~1–2 min at $0 is the bulk-coverage workhorse. This is the
  coherence-scan / onboard / repo-QA-map faces.
- **Strong-for-deep-per-area-reads** → Claude Code subprocess fan-out, **few units** (the research-wave face:
  areas, not files). A `claude -p` per *area* (6 of them) is affordable; a `claude -p` per *file* (400 of
  them) is not. The unit-count must shrink as the tier strengthens — the anchor's "the research-wave face
  configures strong workers" is only viable because that face's units are coarse (areas).
- **Ollama Cloud is the middle rung you reach for when the per-unit task needs reasoning the 4B lacks but the
  unit count is still high enough that Claude Code is too expensive** — e.g. a per-file *intent-drift* judge
  (SEM-2 §4.2 Tier B, the dataflow-adjacent class) over many files. Capability between the 4B and Opus, cost
  between $0 and per-session, concurrency capped at the plan (1/3/10).

**[External, live tension to flag]** `capabilities.py:114-115` records cloud `json_schema` as **UNKNOWN /
"may 400 on response_format:json_schema" — "ASK / probe, never assume."** My web check found **Ollama 0.18
(Q1 2026) added OpenAI-compatible structured outputs with JSON-schema validation**. So the catalog's recorded
gap is likely now *closed* — but the honest stance the catalog itself mandates is **verify-by-probe before
binding the map's schema-enforced output to a cloud worker** (the MAP's whole trust premise is the typed
record by construction — §3.2; if a cloud worker 400s on the schema, that tier silently loses the structured
guarantee). This is a concrete pre-flight check the runner must do, not assume.

---

## 2 · "Configurable, read from the registry" — the SEM-1-shaped 80/20, from the tier side

**[Observed] What's already there (the shape):**
- `run_role`/`run_swarm`/`run_jury` all take `base_url`/`model` as parameters (`cognition.py:93-94,526,638`).
- The capability-query (`role.requires ⊆ provides`) is built and tested (`roles.py:244-285`).
- The catalog has cloud entries with `provides` sets (`capabilities.py:111-122`).
- `service_key_for(reg, model_id)` joins a model-id to its local service-key, returning **None for cloud/ollama**
  (`capabilities.py:127-135`) — the local-vs-cloud discriminator already exists.

**[Observed] What's net-new (the wire + the runner switch):**
1. **Every live caller passes `RESIDENT_BASE_URL`/`RESIDENT_MODEL`** (`cognition.py:52-53`, and 229/243/315/571/677
   all pass the resident constants). Nothing yet calls `run_swarm` with a *resolved* binding. The bridge from
   `resolve_binding(...) → run_swarm(base_url=…, model=…)` is **not wired** — `resolve_binding`'s own docstring
   says "TODAY the Company's only live provider is the resident model … v1 = resident-only provider"
   (`roles.py:255-266`), flagged as the **G8 dependency**.
2. **`_one()` gates unconditionally** (`cognition.py:570`) — the per-tier governor switch (§1.4) is net-new.
3. **The subprocess substrate is a separate runner** — `run_swarm` cannot dispatch a `claude -p` worker; a
   tier-polymorphic MAP runner that routes {local→swarm, cloud→swarm-with-cloud-governor, strong→subprocess-fan-out}
   is net-new (it *composes* `run_swarm` and an `implement.py`-shaped fan-out; it doesn't live in either today).

**[Inferred] Net, for my area: ~70% of the tier machinery is present as shape + query + catalog; the missing
~30% is (a) the resolve_binding→run_swarm wire, (b) the per-tier concurrency-governor switch, (c) the
subprocess MAP runner.** This is the *exact* SEM-1 pattern ("80% verbatim, the 20% is real, not 'just point
it'") reached from the worker-tier side instead of the engine side.

---

## 3 · The contained-unit mechanics — the heart of the MAP allocation

The anchor's load-bearing MAP claim (§2, §5): each worker gets **a contained unit + the schema + thinking-on**
and emits structured output, with *guaranteed per-unit attention* (the coverage-certainty insight). Three
questions decide whether that is real: **what is a unit?**, **how does a worker even read a file?** (the
ctx→messages seam), and **what happens when a unit doesn't fit?** (the chunk-compose tier).

### 3.1 · The ctx→messages seam — what makes "unit = a file" possible at all

**[Observed]** `run_role` hardcodes the user message: `msgs = [{"role":"system", role.prompt_template},
{"role":"user", f"Utterance: {utterance}"}]` and requires `ctx["utterance"]` (`cognition.py:109-113`). A
repo-reading worker's input is a *file artifact*, not an utterance — and the literal string "Utterance:" is
*semantically wrong* for a file. So the MAP cannot read a file today without a change. SEM-1 §4 already named
this the **one real net-new seam**; from my side it is the seam that makes the entire contained-unit premise
real. The right fix (SEM-1's (a), and I agree):
- generalize `run_role` to a **declared ctx→messages mapping**: a role declares what it reads via
  `input_addresses` (the field *exists* in the role schema — `roles.py:67`, `roles.py:23` — but is
  **"descriptive today"**), and the runner builds the user message from those resolved inputs (the file
  content, a docstring, an AGENTS.md slice) instead of from a fixed `utterance`.

This is small but it touches the shared `run_role`, so it must stay behind the existing schema-validate /
fail-loud discipline (`cognition.py:107-108`).

### 3.2 · The structured-output guarantee (why the unit's output is trustworthy *as a record*)

**[Observed]** The MAP's "schema-enforced structured output" is real and already the engine's transport:
`run_role` passes `schema=role.output_schema, json=True` (`cognition.py:115-117`); the `json_schema` transport
branch sets `response_format: {"type":"json_schema", "json_schema": <model_json_schema>}` (`transport.py:47-48`),
server-side constrained decoding, with client-side validate-and-retry (`cognition.py:101`). So **a MAP finding
is a typed record by construction** — the anchor's §2 premise holds on the *local* tier. (The cloud-tier
caveat is §1.5's json_schema-may-400 probe.) This is also why the cheap layer is *safe* as candidate-
generation: it can only emit the declared shape, not a persuasive essay (SEM-2 §5.3 leg 1).

### 3.3 · What is a good "unit"? — the unit-definition spectrum (a position)

The anchor asks directly: a file? a symbol? a file+its-self-description? I take a position, grounded in what
the units *carry* and what the per-unit task *needs to be answerable from the unit alone* (the contained-unit
constraint — SEM-2 §3: a per-unit task must be answerable from the one unit or the cheap worker guesses):

```
UNIT = a FILE                     the default. Coarse, self-delimiting, maps 1:1 to the filesystem
                                  unit_selector. Right for: per-file digest (onboard), doc-staleness
                                  (one doc), repo-QA-map (per-file answer). Fails when the file is >window (§3.4).

UNIT = a SYMBOL / region          finer. A function/class/route. Right for: a per-symbol check, AND it is the
                                  CHUNK the over-window file decomposes into (§3.4). Needs a structural splitter
                                  (AST/region) — net-new, but it's the same splitter the chunk tier needs.

UNIT = a FILE + its SELF-         the contained unit that carries its OWN INTENT. A module + its docstring /
       DESCRIPTION (AGENTS.md)    its AGENTS.md entry / the design-doc that spawned it. This is the RIGHT unit
                                  for the highest-value MAP task — intent-vs-implementation drift (SEM-2 §4.2):
                                  "does the code still do what its own self-description CLAIMS?" The unit is
                                  contained (claim + code in one ctx) AND the question is unit-local → it fits
                                  the cheap tier (Tier A, shallow drift). This is the unit that best honours
                                  the contained-unit constraint: it bundles the thing AND the yardstick.
```

**[Your-idea] Take the file+self-description as the *canonical* contained unit for the coherence/onboard
faces**, not the bare file. The Company is AI-native and self-describing (per-dir `AGENTS.md`, dense
docstrings — SEM-2 §4.2 confirms they're the self-model); a unit that pairs the artifact with its declared
intent is *more contained*, not less, because the per-unit judgment ("does this match its own claim?") needs
no other file. The bare-file unit is the floor; the file+self-description unit is the one that makes the MAP's
per-unit attention *meaningful* rather than just *complete*. (The `input_addresses` generalization in §3.1 is
exactly what lets a unit declare "I read this file AND its AGENTS.md slice.")

### 3.4 · The chunk-and-compose sub-tier — forced by suite.py, and DISTINCT from cross-file join

**[Observed]** `suite.py` is 716,125 B ≈ 180K tokens; the live `max_model_len` is 65,536 (`services.json:59`).
It is the only first-party source file over the window — and SEM-1 §3 notes it is the single most coherence-
critical file (the Suite is the system's spine; the mode-dial-built-twice and the `/status` incidents both
live in this path). So **"unit = a file" breaks exactly on the most important file.** The MAP needs a
chunk-and-compose sub-tier:

```
CHUNK     split suite.py by SYMBOL / class / region (the §3.3 symbol-unit splitter) → N sub-units that fit
          → each rides the normal MAP (a worker per chunk, schema-enforced)
COMPOSE   a per-file reduce: join the N chunk-findings into ONE file-level finding (e.g. "this file's
          self-description claims X; chunk-7 contradicts it")
```

**[Inferred] The critical distinction the anchor blurs:** this chunk→compose is **intra-file** (one file, too
big, split-and-rejoin). It is **NOT** the cross-file *pairing/join* SEM-2 §3 needs (half-migration spans the
old + new mechanism; built-twice spans the repo). They are *related machinery* (both "fan sub-reads → compose
a higher-level finding") but **different jobs**:
- **chunk-compose** lives in the **MAP** (it's how an over-window unit becomes mappable) → my area;
- **cross-file pairing/join** lives in the **REDUCE** (the strong layer joins across unit-findings) → CC's
  reduce area / SEM-2's Stage-1 pairing.

Conflating them is a real risk: a builder who thinks "I built chunk-compose, so cross-file is handled" ships a
gap. **State them as two tiers.** The chunk-compose tier is net-new (a structural splitter + a per-file
compose role); SEM-1 §4 flags it as "net-new and mandatory."

### 3.5 · The unit_selector — dir glob / file list / registry slice

**[Observed]** The anchor's `unit_selector` (Chain §3: "a dir glob, a file list, a registry slice") has clean
real anchors:
- **dir glob / file list** — the filesystem; my corpus measurement *is* a unit_selector run (the `find` glob
  in §1.5). Trivial, stdlib.
- **registry slice** — the Company is registry-driven: `NodeRegistry.discover`, `RoleRegistry.discover`
  (`roles.py:186-198`), the `services.json` services, the `capabilities.py` catalog, the suites'
  `capabilities()` projection (suite.py). A unit_selector that says "every role file" or "every node type" or
  "every served model" is a registry query — and because those registries are **self-describing and file-
  discovered**, the selector gets *coverage-certainty for free* (the registry IS the complete enumeration).

**[Your-idea] The registry-slice selector is the most powerful one** for the coherence face, because it maps a
MAP unit 1:1 to a *declared* thing (a role, a node, a suite, a model), so the per-unit finding is addressable
back to a registry entry — provenance by construction (the §5 coverage-certainty insight, made concrete: not
just "we read every file" but "we read every *declared unit* and tagged each finding to its registry
address"). The glob selector covers the filesystem; the registry selector covers the *self-model*.

---

## 4 · How the map fans concurrently — SlotBudget, the ~14-slot pool, the contention fix

**[Observed]** The fan-out (`run_swarm`, `cognition.py:523-621`): materialize the ready-set
(`cognition.py:558`), dispatch on a `ThreadPoolExecutor(max_workers=budget.swarm_slots)` (`cognition.py:585`),
each worker `_one()` acquires `gate.slot()` then writes its validated JSON to a distinct `run://<turn>/<role>`
address (`cognition.py:570-573`), join at the `as_completed` barrier (`cognition.py:588`), one batched rollup
(`cognition.py:602-611`), read every value back via the canonical resolver (`cognition.py:619-620`). The GIL
releases on socket I/O; vLLM batches server-side (`cognition.py:535-538`). **This is exactly the MAP's
"concurrent, per-unit attention, tagged output" motion — built and criteria-proven.**

**[Observed] The budget** (`SlotBudget.from_registry`, `cognition.py:403-450`): `swarm_slots = min(max_num_seqs
− R, free_KV // per_role_ctx)`, R=2 reserved (`cognition.py:404`), `per_role_ctx=1500` default
(`cognition.py:380`), `free_KV=66036` at util 0.49 (`services.json:75-79` `_profile` + the C0.5 map at
`cognition.py:382`). **The KEY MAP correction (SEM-1 §2.3, which I re-confirm):** `per_role_ctx=1500` is the
*utterance* size; a *file* is 2K–8K+ tokens, so `kv_bound = free_KV // per_role_ctx` collapses above ~4.7K
tok/file. The honest MAP concurrency is **8–14, file-size-dependent**, not the flat 14 and certainly not 32.
The fix is a parameter, not a rewrite: `SlotBudget.from_registry(per_role_ctx=<actual file token estimate>)`
— and the runner should set `per_role_ctx` from the *measured* unit size, not the cognition default.

**[Observed] The sweep-vs-cognition contention** (SEM-1 §5, which I ground further): there is **ONE global
`VramGate` singleton** (`cognition.py:458-470`) and **ONE swarm pool** capped at `swarm_slots`
(`cognition.py:585`). A background coherence sweep and a live concurrent-cognition turn contend for the **same
~14 slots** — not two pools. The gate's R=2 reservation protects a *single* main-stream/judge call
(`cognition.py:547-552`), but a 400-file sweep holding the pool for ~1 min will **delay a live cognition
*wave*** that wants those slots.

**[Observed] The polite-budget fix is already parameterized:** `reserve_r` is a `from_registry` argument
(`cognition.py:404`). SEM-1's `[My-idea]` (give the sweep its own `SlotBudget` with a larger `reserve_r`, e.g.
R=8, so 8 slots stay for live cognition) needs **no new machinery — just a second budget instance**. I confirm
this against the code: `run_swarm(..., budget=<polite SlotBudget>)` accepts an injected budget
(`cognition.py:524,545-546`), so a MAP sweep can be made polite-by-construction at the call site.

**[Your-idea] Two complementary contention levers, not one:** SEM-1 found the *local* lever (polite
`reserve_r`). The tier lever (§1.4) is the *other*: **bind the sweep's map-role to Ollama Cloud and the local
pool is untouched entirely.** A continuous/background coherence watch (anchor §9 "continuous mode") should
prefer the cloud tier *specifically because* it removes the sweep from the local KV pool — the on-demand
local sweep is fine when cognition is idle, but the always-on watch wants to live off-card. So: **on-demand →
local + polite reserve_r; continuous → cloud tier.** That's a clean policy the two levers compose into.

---

## 5 · Everywhere it connects + what needs building (the map Tim asked for)

**Connections (Observed unless marked):**
- **The cognition engine** — the MAP *is* `run_swarm` (`cognition.py:523`), files-as-units instead of
  roles-as-units. The `json_schema` transport (`transport.py:47`) makes each unit-finding a typed record. The
  `run_jury` 2nd-model slot (`cognition.py:637`, `verify_jury.py` E4 caveat) is the REDUCE's adjudicate leg,
  not the MAP's — the MAP is candidate-generation (SEM-3 trust ladder, inherited).
- **The model registry (my core)** — three keyings: `services.json` (deployment), `gpu.py` (VRAM),
  `capabilities.py` (capability). The tier is selected by `resolve_binding`'s `requires ⊆ provides` query
  (`roles.py:251`). `models.py:swap()` is how a tier's local model is repointed.
- **The strong tier** — `implement.py` (`claude -p`, `CONCURRENCY_CAP=3`) is the subprocess substrate; the
  research-wave (this run) is its live manual form.
- **The CLI** — `app.py`'s verb chain (`app.py:127-206`: status/gpu/suites/models/config/swap/bench/…) is
  where `company research <dir>` / `company ask <dir> "<q>"` / `company onboard` slot in as new verbs (per
  `ops/cli/UPDATING.md` — build into `ops/cli/`, never a parallel tool).
- **The coverage-certainty insight (§5 of the anchor)** — grounded: the registry-slice unit_selector gives
  coverage-certainty *for free* (the registry is the complete enumeration), and the distinct `run://` address
  per worker (`cognition.py:559,573`) gives provenance by construction.

**What needs building (the net-new MAP seams, in dependency order):**
1. **ctx→messages generalization** (`run_role`): the role declares `input_addresses`, the runner builds the
   user message from resolved inputs (file content / docstring / AGENTS.md slice) instead of the hardcoded
   `f"Utterance: {utterance}"`. *Makes "unit = a file" possible at all.* (§3.1; SEM-1's one named seam.)
2. **A unit-fetch layer**: read a file / a docstring / an AGENTS.md into `ctx` (trivial, stdlib, absent from
   the cognition path which only ever saw an utterance). (§3.1.)
3. **The per-tier concurrency-governor switch**: `_one()` must not `gate.slot()` unconditionally — local →
   VramGate, cloud → plan-quota semaphore, subprocess → CONCURRENCY_CAP. (§1.4.)
4. **The resolve_binding → run_swarm wire**: pass a *resolved* `base_url`/`model` (and the chosen governor)
   into `run_swarm` instead of the resident constants; populate `resolve_binding`'s provider set from the
   `capabilities.py` catalog (the flagged G8 dependency). (§2.)
5. **The tier-polymorphic MAP runner**: route {local→swarm, cloud→swarm-with-cloud-governor,
   strong→subprocess-fan-out}; it *composes* `run_swarm` and an `implement.py`-shaped fan-out. (§1.2.)
6. **The chunk-and-compose sub-tier**: a structural splitter (AST/region) + a per-file compose role for
   over-window files (suite.py). Intra-file, distinct from the reduce's cross-file join. (§3.4.)
7. **A cloud-tier json_schema pre-flight probe**: verify structured-output before binding the map's
   schema-enforced output to a cloud worker (catalog says verify, web says Ollama 0.18 added it). (§1.5.)
8. **The `unit_selector`**: glob / file-list / registry-slice resolvers (glob + file-list trivial; registry-
   slice is a query over the discovered registries). (§3.5.)

---

## 6 · The bottom line for a builder

1. **The MAP fan-out engine is real and built** (`run_swarm` + the `json_schema` transport + `SlotBudget` +
   the `run://` per-worker addressing). The cheap parallel layer's *motion* is done. Confidence: high (Observed).
2. **"Configurable worker tier" is shape-ready but not wired** — the three tiers are two substrates + three
   governors, `SlotBudget` is local-only, every caller passes the resident constants, and the strong tier is
   a *different runner* (subprocess), not a model-param swap. The capability-query that *selects* a tier
   exists and is the right mechanism; the wire from it into the runner is net-new (~30%). (§1, §2.)
3. **Tier-fit by per-unit task AND unit-count:** local 4B for high-count contained extraction (~400 files,
   $0, ~1–2 min); Claude Code subprocess for low-count deep reads (~6 areas — the research-wave face); Ollama
   Cloud (Free 1 / Pro 3 / Max 10, usage-metered) for the mid rung (reasoning the 4B lacks at a unit-count
   Claude Code can't afford). Tier is *also* a contention lever (cloud = off the local card). (§1.4, §1.5.)
4. **"Unit = a file" hides two net-new mechanics, not zero:** the ctx→messages seam (without it a worker can't
   read a file) and the chunk-compose tier (suite.py is 2.75× the window). The chunk-compose tier is intra-
   file and **must not be conflated** with the reduce's cross-file join. The canonical contained unit for the
   coherence/onboard faces is **a file + its self-description** (it bundles the artifact and its own
   yardstick → the per-unit judgment stays unit-local). (§3.)
5. **Concurrency is 8–14, file-size-dependent** (KV-binds >~5K tok/file), not 32 — set `per_role_ctx` from the
   measured unit size. Contention (sweep vs cognition waves on one ~14-slot pool) has **two composable fixes**:
   a polite `reserve_r` (local, already parameterized) and binding the map to a cloud tier (off-card entirely).
   On-demand → local + polite; continuous → cloud. (§4.)

**The MAP layer is real, the engine is built, and the cheap-extraction tier clears the bar. The "configurable
worker tier" the anchor sketches is a wire + a runner-switch away — not a present property — and the
contained-unit premise rests on two named net-new seams the anchor folds into one. Corrected, the MAP is the
solid, mostly-built floor of the corpus-chain; the work is in the binding wire, the per-tier governor, and the
chunk-compose tier — all small, all named, none speculative.**

---

### Sources (external verification)
- [Pricing · Ollama](https://ollama.com/pricing) — plan tiers, concurrency (Free 1 / Pro 3 / Max 10), session/weekly caps, usage levels 1–4.
- [Ollama Cloud Free vs Pro: Usage Limits, Pricing (2026)](https://devtoolhub.com/ollama-cloud-free-vs-pro-limits-pricing-2026/) — concurrency + queueing behaviour, structured-output (JSON-schema) support in Ollama 0.18 (Q1 2026).
- [Ollama Cloud Pricing 2026](https://pooya.blog/blog/ollama-cloud-pricing-hardware-requirements-2026/) — pricing crossover, plan detail.
