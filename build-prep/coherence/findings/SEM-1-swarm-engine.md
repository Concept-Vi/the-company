# SEM-1 · The 4B Swarm Engine — real capacity, throughput, and reuse for repo-reading

> Companion to `SEMANTIC-LAYER-ANCHOR.md`. My allocated area: **is the capability actually real, and can
> the existing engine do this?** I read the real cognition-swarm code, the resource manager, the live
> service registry, and the benchmark sheet, and I measured the real repo. Verdict up front: **the
> capability is real — the engine exists and is reusable almost verbatim — but the anchor's headline
> numbers are optimistic on three independent axes.** That correction is a *stronger* finding than
> confirming the claim, because a builder who trusts "3000 tok/s, 32 concurrent, whole repo in seconds"
> will mis-size the sweep. The honest numbers still clear the bar; they just clear it by less.
>
> Evidence is marked **[Observed]** (file:line / measured), **[Inferred]** (reasoned from observed
> facts, not executed), **[External]** (prior art), **[My-idea]** (my proposal). I did not run a live
> swarm sweep — the throughput figures below are the benchmark sheet's *measured* numbers recombined
> with the *observed* live config; I label that recombination Inferred where it is one.

---

## 0 · TL;DR — the three corrections that change the answer

| Anchor claim | Reality (grounded) | Where |
|---|---|---|
| "~3000 tok/s" | **2,241 tok/s aggregate, measured** — and only *at concurrency 32* | `BENCHMARK_FACTSHEET.md:24` |
| "~32 concurrent inferences" | **Live config caps at `max_num_seqs:16`** → swarm budget knee = **14** for tiny inputs, and **8–13 for real source files** (KV-bound, file-size-dependent) | `services.json:60`, `cognition.py:439-443`, computed |
| "whole repo in seconds, or a minute or two" | Reading (prefill) IS seconds; *judging* (decode) is the bottleneck → **~tens of seconds to ~1–2 min** for the ~400-file core, **and only at bumped concurrency**. The single most coherence-critical file (`suite.py`) **does not fit the context window at all** | computed from `BENCHMARK_FACTSHEET.md:24,51` + repo measurement |

None of these kills the idea. All three say: the layer is real, but size it as **"a minute or two at
reconfigured concurrency, file-bounded, with suite.py needing chunking"** — not "free, instant, whole-repo."

---

## 1 · The engine is real and substantial — what it is, exactly

**[Observed]** The cognition swarm is not a sketch. `runtime/cognition.py` is 716 lines of working,
criteria-proven code (the G0 spike + the G1 production substrate). The pieces the anchor names all exist:

- **`run_swarm(roles, ctx, store, *, turn_id, budget, emit, ...)`** (`cognition.py:523-621`) — the core fan-out.
  It materializes a ready-set, dispatches each role on a `ThreadPoolExecutor(max_workers=budget.swarm_slots)`
  (`:585`), each role writes its validated JSON to a distinct `run://<turn>/<role>` address (`:572-573`),
  joins at an `as_completed` barrier (`:588`), emits ONE batched rollup (`:602-611`), then reads every
  role's resolved value back via the canonical resolver (`:619-620`). This is *exactly* "fan out N cheap
  structured judgments and collect them" — the semantic layer's core motion, already built.
- **`run_role(role, ctx, ...)`** (`cognition.py:93-119`) — fires ONE request at the resident 4B via the
  same fabric path the live judge uses (`client.complete(transport.openai_transport(...))`), passing
  `schema=role.output_schema, json=True, temperature=0.0`. Default `temperature=0` is the determinism lever
  (§6).
- **`run_jury(role, ctx, ...)`** (`cognition.py:637-715`) — N varied draws (temperature>0) → a pure
  deterministic `verdict_rule` over them (`:707`). This is the anchor's §6.1 candidate-trust mechanism,
  **already first-class.**
- **`resolve_run_ref(store, addr, ...)`** (`cognition.py:474-496`) — the canonical head→get_content read-back,
  fail-loud on a missing ref, `run://`-only.
- **`SlotBudget.from_registry(...)`** (`cognition.py:403-450`) — computes the concurrency budget from the
  *live* `ops/services.json`, never a hardcoded 32 (`:417` literally fails loud rather than assume 32).
- **`RoleRegistry.discover([roles_dir])`** (`roles.py:186-198`) — file-discovered roles. Drop a
  `roles/<id>.py` declaring a `ROLE` dict → it self-registers, is queryable, validates at discovery.
  Mirrors `NodeRegistry` exactly.
- **The `json_schema` transport branch** (`transport.py:47-48`) — `response_format:
  {"type":"json_schema","json_schema":<dict>}`, vLLM server-side schema-*constrained* decoding. A role's
  Pydantic `output_schema.model_json_schema()` flows straight through (`transport.py:38-39`).

**[Inferred]** This is genuinely "build-on-not-beside." The semantic detector is *the same wave engine
pointed at a repo artifact instead of an utterance.* The anchor's central bet — "not net-new machinery" —
holds for the *fan-out + structured-output + budget + role-discovery* spine.

---

## 2 · The throughput claim, measured and recombined honestly

### 2.1 The benchmark sheet's real numbers (the ground truth)

**[Observed]** `~/vllm-tests/BENCHMARK_FACTSHEET.md` — same model (`Qwen3.5-4B-AWQ-4bit`), same RTX 4080:

| Concurrency | Aggregate tok/s | TTFT p50 | Latency p50 |
|---|---|---|---|
| 8 | **809** | 65ms | 1.20s |
| 32 | **2,241** | 153ms | 1.80s |
| 64 | 2,124 | 288ms | 3.76s |
| 128 | 2,251 | 3,736ms | 7.13s |

- **The "3000 tok/s" figure is not in the sheet.** The measured aggregate peak is **2,241 tok/s** and it
  **plateaus at concurrency 32** (`:30`: "Aggregate tokens/sec plateaus at concurrency 32"). The anchor
  overstates throughput by ~34%.
- **Per-request decode is rock-steady ~100 tok/s** regardless of output length (`:64`). This is the number
  that governs how long a *judgment* takes.
- **Prefill is extremely fast and gets *more* efficient with length** (`:53`): 30K input tokens prefilled
  in ~1.07s at ~28,098 tok/s (`:51`). This is the "reading" half — and it genuinely is seconds.
- **Structured JSON output is verified reliable** (`:84-96`: "All 3 prompts produced valid, schema-conforming
  JSON … Reliable for production"). The schema-enforced-record premise holds.
- **Long-context recall is 5/5 across depth** (`:113-124`) — the model uses planted context, not just
  start/end. Good for the doc/file-reading workload.

### 2.2 The live config caps concurrency at 16, not 32 — and the swarm budget knows it

**[Observed]** The live `chat-4b` service (`services.json:55-80`): `gpu_util: 0.49`, `max_model_len: 65536`,
**`max_num_seqs: 16`**. I confirmed the model is up and reports `max_model_len:65536` (curl `/v1/models`).

**[Observed]** `SlotBudget.from_registry` computes `swarm_slots = min(max_num_seqs − R, free_KV // per_role_ctx)`
(`cognition.py:439-443`), with `R = 2` reserved for the main stream/judge (`:379`), `per_role_ctx = 1500`
default (`:380`), and `free_KV = 66036` measured at util 0.49 (`:382`).

**[Inferred, computed]** With the *live* config and the *cognition default* per_role_ctx=1500:
`seq_bound = 16−2 = 14`, `kv_bound = 66036//1500 = 44`, `knee = min(14,44) = **14**`. So the engine, today,
fans out **14 concurrent**, not 32. To reach the benchmark's 32-concurrent peak you must
`company config chat-4b max_num_seqs 32` and restart — a deliberate reconfigure, with more KV pressure.

### 2.3 The hidden binding constraint: per_role_ctx for *files* is not 1500

This is the sharpest correction, and the engine's own formula proves it. A *cognition* role reads a ~1500-token
utterance. A *repo-reading* role reads a **whole file** — 2K–8K+ tokens. Plug real file inputs into the actual
`kv_bound = free_KV // per_role_ctx` formula (`free_KV = 66036`, `seq_bound = 14`):

| per_role_ctx (tokens) | kv_bound | **effective swarm_slots** | what binds |
|---|---|---|---|
| 1,500 (utterance) | 44 | **14** | seq-cap |
| 2,000 | 33 | **14** | seq-cap |
| 4,000 | 16 | **14** | seq-cap |
| **4,717 (crossover)** | 14 | **13** | both |
| 8,000 | 8 | **8** | **KV** |
| 16,000 | 4 | **4** | **KV** |
| 30,000 | 2 | **2** | **KV** |

**[Inferred]** The crossover is at **per_role_ctx ≈ 4.7K tokens/file** (= 66036/14). Below that, the 16-seq cap
binds (14 slots). **Above ~5K-token files, KV binds and concurrency collapses** — an 8K file → 8 slots, a
30K file → 2 slots. The repo's file distribution (§3) puts a large fraction in the 2–8K band, so the *honest*
effective concurrency for a source sweep is **~8–14, file-size-dependent** — not 32, and not even a flat 14.
And this is **before** the live conversation eats any KV: `SlotBudget` subtracts `main_ctx_tokens` from
`free_KV` (`cognition.py:439`), so a deep live chat shrinks the swarm further (§5).

### 2.4 End-to-end: how long does reading the actual repo take?

**[Observed, measured]** The real Company source (excluding all venvs / node_modules / site-packages):
- **232 Python + 39 TS/TSX + 124 Markdown ≈ 395 files**, **5.21 MB**, **≈1.37M tokens** (bytes/4).
- Excluding the 131 test files, the **core source is 101 Python files, 1.54 MB, ≈405K tokens.**
- File-size distribution (all real source): **195 files <2K tok, 174 files 2–8K tok, 24 files 8–32K tok,
  2 files >32K tok.** The 2–8K band is the largest — exactly the band where KV starts to bind (§2.3).

**[Inferred]** A "read each core file → emit a ~200-token structured finding" sweep over ~400 files:
- **Prefill (reading):** ~405K input tokens at ~28K tok/s prefill ≈ **~15s of pure prefill** — the "read it
  in seconds" half of the claim *holds*.
- **Decode (judging):** ~400 findings × ~200 output tokens ≈ **80K output tokens.** At the realistic
  aggregate decode rate — **interpolated** between c=8 (809 tok/s) and c=32 (2,241 tok/s); the live c≈14
  lands ~1,400–1,800 tok/s — that's **~45–60s** at live concurrency, dropping toward **~35s** only if
  reconfigured to 32 *and* files stay small enough not to KV-bind.
- **Honest center: ~1–2 minutes for the core source at live config; tens of seconds only at bumped
  concurrency.** The anchor's "seconds" oversells; "a minute or two" is right — *with the caveats above.*

**[Inferred] Prefix caching does NOT help this workload on the first pass.** The sheet shows prefix caching
is hugely effective for *multi-turn* (`:67-81`), but a one-file-per-request sweep has **no shared prefix
across distinct files** — each file is a cold prefill. Prefix caching only pays off on **re-runs of unchanged
files** (same file content → cached prefill). That re-run benefit is real and aligns with own/reflect
(re-read the whole repo cheaply) — but only the *unchanged* files re-read cheaply.

---

## 3 · The context-window wall — "unit = a file" breaks exactly where it matters most

**[Observed]** The live `max_model_len` is **65,536 tokens** (`services.json:59`, confirmed via `/v1/models`).
The largest real source file is **`runtime/suite.py` at 716,125 bytes ≈ 180K tokens — 2.75× the window.**
It is the *only* real-source file over the window, but it is the single most coherence-critical file in the
repo (the Suite is the system's spine; the substrate doc itself notes the mode-dial-built-twice and the
`/status` deletion both happened *in* this code path).

**[Inferred]** So the anchor's §6.2 ("read the whole repo means many bounded reads + a composition") is not a
detail — it is load-bearing, and it bites hardest where it hurts most:
1. **suite.py cannot be read in one pass.** A semantic check over it needs chunking (by symbol / by class /
   by region) + a composition step — net-new logic the swarm engine does not provide today.
2. **Cross-file judgments have no single run that sees everything.** Half-migration spans two mechanisms
   (the `/status` case: a JSONL path *and* an annotation store); concept-coherence spans the whole repo.
   `run_swarm` fires *independent* roles reading *independent* inputs (`cognition.py:557` notes roles read
   only `ctx.utterance` today, "When roles gain inter-role deps, ready-set = roles whose run:// deps already
   resolved — same shape"). The *shape* for dependent roles is anticipated, but a cross-file *composition
   role* (read N file-judgments → emit one cross-file finding) is **net-new**.

This is the honest architecture question the anchor flagged, made concrete: **the unit is "a file or a
symbol," and a second composition tier is required for anything that spans files — including the highest-value
checks (half-migration, concept-coherence).**

---

## 4 · Reuse — what's verbatim vs net-new (the precise seam)

**[Observed] Reusable essentially verbatim** (these are the anchor's bet, and it's right):
- `run_swarm` / `run_jury` — the fan-out + barrier + batched-rollup + read-back motion.
- The `json_schema` transport branch (`transport.py:28-50`) — a finding is a typed record by construction.
- `SlotBudget.from_registry` — the budget computation (it just needs `per_role_ctx` set to the *file* size,
  not 1500 — see §2.3; that's a parameter, not a rewrite).
- `resolve_run_ref` + the `run://` addressing + the FsStore put_content/set_ref.
- `RoleRegistry.discover` — a *semantic finding-type* becomes a `roles/<id>.py` file declaring a prompt +
  an output_schema. This is the anchor's §8 "finding-types are declared" — **already true** via the role
  registry. (`Role.can_fire` = has prompt_template + output_schema, `roles.py:91-93`.)
- `run_jury`'s verdict_rule pattern — N-role-agreement for candidate trust (§6.1), first-class.

**[Observed] The one real net-new seam (don't call it "zero new code"):** `run_role` hardcodes the user
message as `content = f"Utterance: {utterance}"` and requires `ctx["utterance"]` (`cognition.py:109-113`).
A repo-reading role's input is a *file artifact*, not an utterance. So either:
- (a) generalize `run_role` to a declared ctx→messages mapping (the role declares what it reads — the
  `input_addresses` field already exists in the role schema, `roles.py:67/26`, but is "descriptive today"),
  or
- (b) pack the file content into the `utterance` slot (hacky, and the prompt says "Utterance:" which is
  semantically wrong for a file).

**(a) is the right move and it's small** — but it is net-new and it touches the shared `run_role`, so it
needs to stay behind the existing schema-validate/fail-loud discipline.

**[Inferred] Also net-new:** (1) the **chunker + composition tier** for over-window files and cross-file
checks (§3); (2) the **artifact-fetch layer** (read a file / a docstring / an AGENTS.md into `ctx`) — trivial
but not present in the cognition path, which only ever sees an utterance; (3) the **finding emission** into
the coherence substrate's event log — but that's the *consumer's* concern (the coherence round), and `emit`
is already a parameter of `run_swarm` (`cognition.py:526,602`).

Net: **~80% verbatim, ~20% net-new, and the 20% is real** (ctx-generalization + chunk/compose + fetch), not
the "just point it" the anchor's tone implies.

---

## 5 · VRAM contention — the real question is "vs the cognition swarm itself," not "vs chat"

**[Observed]** The swarm fires at the **already-resident** vLLM over HTTP (`cognition.py:52` resident base
URL; `run_role` → `client.complete`). It loads **zero new VRAM** — the 4B is already up (I confirmed it
resident; nvidia-smi showed 15,122 MiB used / 929 MiB free, i.e. the card is full *with the resident stack*,
not with headroom for a new model). **So the §6.4 "starve the live system by loading something" framing is the
wrong worry** — a semantic sweep loads nothing.

**[Observed]** The real contention is **request-slot / KV sharing**, and the engine already has the mechanism:
- One **process-wide `VramGate` singleton** sized to `max_num_seqs` (`cognition.py:458-470, 553`), and the
  swarm pool is capped at `swarm_slots = max_num_seqs − R` (`:585`), so **R=2 slots always remain free** for a
  main-stream/judge call to acquire immediately (`:547-552` documents this invariant explicitly).
- `SlotBudget` subtracts `main_ctx_tokens` from `free_KV` (`:439`) — so a *deep live conversation* genuinely
  shrinks the swarm's KV headroom (the C0.5 "bind flips on main-context depth" finding, `:399`).

**[Inferred] The sharp consequence the anchor missed:** there is **ONE global gate and ONE swarm pool.** A
background coherence sweep and a live *concurrent-cognition turn* contend for the **same ~14 slots** — they are
not two pools, they are the same pool. So the contention question is not "sweep vs chat" (chat is protected by
R=2); it is **"a whole-repo sweep vs the cognition stream's own waves."** If the anchor's §8 "continuous
background watch" runs while the cognition stream is also fanning roles, they share the budget. The honest
answer: **on-demand sweeps are safe (run them when cognition is idle); a continuous background watch must yield
to live cognition waves** — which the gate's FIFO will do, but a 400-file sweep holding 14 slots for ~1 min
will *delay* a live wave that wants those slots. A sweep should therefore run at a **lower swarm_slots budget**
(e.g. `R` raised, or a dedicated small pool) so live cognition always has slots — that's a config knob the
`SlotBudget` already supports (`reserve_r` is a parameter, `:404`).

**[My-idea]** The cleanest coexistence: give the sweep its **own `SlotBudget` with a larger `reserve_r`**
(say R=8, leaving 8 for live cognition+chat), so a background sweep is *polite by construction* and the live
system never queues behind it. No new machinery — just a second budget instance.

---

## 6 · The 4B's real ceiling, determinism, and trust (the make-or-break, my read)

**[Observed]** Determinism is *engineered for*: `run_role` defaults `temperature=0.0` (`cognition.py:95`),
the routing rules are pure functions of resolved values with no `now()`/random (`cognition.py:160-187`,
`C0.2`), and `run_jury` exists precisely to turn N varied draws into a deterministic verdict
(`cognition.py:637-715`). The substrate's own trust story (`own/reflect`) wants "identical code → identical
findings"; **temperature-0 + schema-constrained decoding + a jury verdict is the engine's answer**, and it's
already built.

**[Inferred] But temperature-0 is not bit-exact across a busy server.** vLLM batching/scheduling can perturb
low-probability token ties; "deterministic" here means *high-stability*, not *guaranteed-identical*. The
jury (`run_jury`) is the right backstop for the *consequential* findings — N draws must concur — and it's the
mechanism to lean on, but it costs N× the decode (so reserve it for the findings that will be acted on, not the
bulk sweep).

**[Inferred] The honest capability tiering (the §6.5 the anchor asked for):**
- **A 4B is good enough for** (local, surface-level, single-artifact): naming/vocabulary consistency,
  doc-vs-symbol staleness ("this doc names a deleted file"), docstring-vs-signature match, "does this test
  *mention* this capability," contradiction between two short docs. These are *candidate-only* signals (§ the
  substrate's positive-only law) and the 4B's needle-in-haystack recall (5/5) supports them.
- **A 4B is NOT reliable for** (deep, cross-file, logic): proving a dropped lifecycle (half-migration —
  *flag the candidate, never adjudicate*), subtle dataflow, "does this suite actually *exercise* (not mention)
  this capability." These need the composition tier (§3) and/or a stronger-model confirm — exactly the
  positive-only / candidate-only discipline the substrate already mandates.

This matches the structural round's own tiering (ship-now / candidate-only / honestly-bounded) — the
semantic layer inherits the *same* three-tier honesty, and the 4B's ceiling sets the tiers.

---

## 7 · What I'd tell a builder (the grounded bottom line)

1. **The engine is real and ~80% reusable.** `run_swarm`, the `json_schema` transport, `SlotBudget`,
   `RoleRegistry`, `run_jury`, `resolve_run_ref` all map onto repo-reading with no rewrite. Confidence: high
   (Observed).
2. **Size the sweep at ~8–14 concurrent, not 32**, because real source files KV-bind above ~5K tokens
   (§2.3). To get the benchmark's 32-concurrent / 2,241-tok/s peak you must reconfigure `max_num_seqs` and
   eat more KV — a deliberate fork, not the default.
3. **"Whole repo in a minute or two" is right; "in seconds" is not.** Prefill (reading) is seconds; decode
   (judging) is ~1–2 min for the ~400-file core at live concurrency. Prefix caching helps only on re-runs of
   unchanged files.
4. **suite.py (180K tok) does not fit the 65K window** — the one file the substrate most needs to watch.
   A chunk+compose tier is net-new and mandatory, and it's also what cross-file checks (half-migration,
   concept-coherence) require.
5. **VRAM is a non-issue (loads nothing); slot/KV contention is the real thing**, and it's "sweep vs the
   cognition stream's own waves," not "sweep vs chat." Give the sweep its own polite budget (raised
   `reserve_r`); the engine already parameterizes this.
6. **Determinism is engineered (temp-0 + schema + jury) but not bit-exact**; lean on `run_jury` for the
   consequential findings only (N× cost), and keep the bulk sweep candidate-only per the substrate's
   positive-only law.

**The capability is real. The anchor under-counted the cost on three axes and over-counted the reuse on one
seam. Corrected, it still clears the bar — which is the finding worth having.**
