# CC-1 · The chain primitive + the declared chain-config schema, against the real `run_swarm` engine

> **Allocated area.** The corpus-chain *primitive itself* and the declared `Chain` config (anchor §3) —
> stress-tested against the real engine: `run_swarm`/`run_role`/`run_jury` (`runtime/cognition.py`), the
> `json_schema` transport (`fabric/transport.py`), the file-discovered role registry (`runtime/roles.py`),
> the node-type registry + serial graph scheduler (`runtime/registry.py`/`runtime/scheduler.py`), and the
> two prior rounds' artefacts. The questions: what is the chain-config *actually* shaped like so it (a) rides
> `run_swarm` with minimal net-new code, (b) is emittable-by-a-compiler **and** executable-by-a-runner **and**
> saveable-as-a-named-config, (c) composes the four faces as instances; what's the real net-new seam vs reuse;
> and is "a chain is a declared type discovered like a role" the right framing.
>
> Evidence tags: **Observed (file:line)** = read directly in code · **Inferred** = pattern-match, not run ·
> **External-prior-art** · **Your-idea** = my reasoning/design proposal. Expansion-ratio > 1.

---

## 0 · The headline (read first)

The anchor's `Chain = {unit_selector, map_schema, map_prompt, passes, reduce_prompt, worker_model,
synth_model}` is **the right shape, but three of its load-bearing claims are wrong against the real code, and
correcting them makes the primitive simpler, more honest, and more clearly a reuse.** The five things this
companion establishes:

1. **The net-new seam is NOT "generalize `ctx→messages`" (SEM-1's framing) — it is a fan-out AXIS inversion.**
   `run_swarm` today fans **N roles × 1 shared ctx**; the MAP needs **1 role × N units**. That is a different
   thing, and it is the one real net-new mechanism. Everything else — the gate, the SlotBudget, the `run://`
   addressed writes, the barrier, the batched rollup, fail-loud — is reused **100% verbatim**.

2. **`run_jury` is NOT the reduce.** The anchor (§6, §8) says "`run_jury`'s 2nd-model slot is the reduce's
   adjudicate leg." False against the code: `verdict_rule` is a **pure declared function with an explicit
   no-model-call law** (cognition.py:660-664). `run_jury` is *N varied draws of ONE worker + a deterministic
   vote* — it belongs at the **MAP** tier (a per-unit jury), and SEM-3 already proved it measures *variance,
   not error*. The **reduce is a strong-model call over the digest = a `run_role` at `synth_model`** — there
   is no existing primitive for it, and that is fine, because it *is* `run_role` pointed at the digest.

3. **A compiler emits DATA, not code — so `map_schema` cannot be a Pydantic class.** Roles require
   `output_schema` to be a Pydantic *subclass* (roles.py:150-154); `rules.py` forbids `eval`/`exec`. A
   model-emitted chain can only emit a **JSON-Schema dict**, which must ride transport's `json_schema` branch
   (transport.py:47-48) — *not* the `json=True`+Pydantic path `run_role` uses today (cognition.py:115-118).
   That path is **present-but-unproven** (suite.py:7053 records it "false-greened by INVOCATION"), so the
   map-schema *enforcer* is a real seam, not a solved one.

4. **The load-bearing reuse is the validator + runner, not the registry.** "A chain is a declared type
   discovered like a role" is right for the *saved-library half* but is the *smaller* half. What makes the
   anchor's "the runner executes *any* valid instance — compiled or hand-written or saved" (§3) actually true
   is a **`build_chain(decl)` validator mirroring `_build_role` (roles.py:128)** that gates a discovered file
   **and** a compiled instance **and** a hand-written dict through *one* door. Lead with the validator.

5. **There is a real registry-vs-graph fork the anchor glosses.** The Company has **two** declared-composition
   substrates already — *roles* (workers) and *node-graphs* (dataflow; `save_graph`/`list_graphs`/`run_graph`).
   "Is a chain a saved role-type, or a saved node-graph?" has a grounded discriminator: **the graph scheduler
   is strictly serial** (scheduler.py:64 `while … progress:` single-threaded re-scan; cognition.py:356-357
   says so verbatim), so the *concurrent map* **cannot** ride a node-graph — it must ride `run_swarm` in the
   cognition driver. *That* is the structural reason a chain is its own declared type, not a saved graph.

---

## 1 · What `run_swarm` actually is, and the exact axis it fans (Observed)

The map+reduce engine is real and I read every line. The shape of `run_swarm` (cognition.py:523-621):

```
run_swarm(roles: list[Role], ctx: dict, store, *, turn_id, budget, emit, ...) -> WaveResult
  ready_set = list(roles)                                   # cognition.py:558 — the units ARE the roles
  addresses = {r.id: f"run://{turn_id}/{r.id}" for r in ready_set}   # :559 — keyed on ROLE id
  with ThreadPoolExecutor(max_workers=budget.swarm_slots): # :585 — bounded by the registry knee
      futs = {pool.submit(_one, r): r for r in ready_set}   # :587 — one future per ROLE
      for fut in as_completed(futs): ...                    # :588 — the BARRIER
  # _one(role):  run_role(role, ctx, ...) → put_content → set_ref(addresses[role.id])  (:566-573)
  emit("cognition.wave", {... per-role run-records ...})    # :603 — ONE batched rollup (C1.6)
  for rid, addr in addresses.items():                       # :619 — read every output BACK via run://
      result.resolved[rid] = resolve_run_ref(store, addr)
```

**The critical observation for the chain.** Look at `_one` (cognition.py:566-578) and the dispatch (:587):
the thing that *varies* across the pool is the **`role`**; the **`ctx` is shared** (closed over — every
worker calls `run_role(role, ctx, ...)` with the *same* `ctx`, cognition.py:571). And `run_role` itself
(cognition.py:109) does `utterance = ctx["utterance"]` — one hardcoded field of that one shared ctx.

So `run_swarm`'s fan-out axis is: **N distinct roles, one shared input.** That is exactly what a *cognition
cast* is (focus, recall, ground, connect, check — each a different job over the same utterance, cognition.py
declares the cast; roles/*.py).

**The MAP is the inverted axis: ONE role (one `map_prompt` + one `map_schema`), N distinct inputs (units).**
You want every unit run through the *same* extraction worker. Today there is **no way to express that** in
`run_swarm`:
- you can't put the unit in `ctx`, because `ctx` is shared across the whole pool (cognition.py:571) — all
  workers would read the same unit;
- you *could* call `run_swarm` once per unit, but that defeats the single pool / single SlotBudget / single
  barrier / single batched rollup — you'd get N pools, N budgets, N rollups, and lose the cross-unit
  concurrency the whole primitive is *for*.

**This is the real net-new seam, and it is sharper than SEM-1's "generalize `ctx→messages`."** SEM-1 (and the
anchor §6/§8) framed the seam as "`run_role` hardcodes `ctx['utterance']` → a unit-reading worker needs a
generalized ctx→messages mapping." That is *necessary but not sufficient*. Even with a generalized
ctx→messages, `run_swarm` still fans roles, not inputs. The full seam is **a per-work-item input axis**: the
ability to dispatch *(role, per-item-ctx)* pairs, addressed by item-id, through the one pool. (`map_prompt`
generalizing `ctx["utterance"]` is the *inner* half; the *outer* half is the dispatch axis.) — **Your-idea**
(the precise decomposition), grounded in Observed code.

---

## 2 · The one engine refactor that unifies all three call shapes — `run_items` (Your-idea, grounded)

Today the engine has **three** fan-out functions, and they are *almost* the same code:

| Function | Fans | Address key | Varies | Reduce/verdict |
|---|---|---|---|---|
| `run_swarm` (cognition.py:523) | N roles × 1 ctx | `role.id` | the role | none (cast) |
| `run_jury` (cognition.py:637) | 1 role × N draws | `role.id#i` | temperature only | pure `verdict_rule` |
| **MAP (needed)** | 1 role × N units | `unit.id` | the unit (ctx) | a strong `run_role` (reduce) |

All three are: *materialize a list of work-items → submit each to a pool bounded by `budget.swarm_slots` →
`run_role` each under `gate.slot()` → `put_content`/`set_ref` at a distinct `run://` address → barrier on
`as_completed` → re-raise on error → read every result back via `resolve_run_ref`.* That body is **literally
duplicated three times** in cognition.py (`_one` at :566, `_draw` at :673, plus the spike's `_role_worker`).

**The universal-composition move at the *engine* level:** factor a single

```python
# Your-idea — the work-item is the unit of all three shapes.
@dataclass
class WorkItem:
    id: str            # the address suffix: role.id (cast) | f"{role.id}#{i}" (jury) | unit.id (map)
    role: Role         # which worker fires
    ctx: dict          # the per-item input (shared for a cast; per-unit for a map)
    knobs: dict        # temperature/max_tokens (varies draws for a jury)

def run_items(items: list[WorkItem], store, *, turn_id, budget, emit, ...) -> WaveResult:
    # the EXACT body of run_swarm's pool/gate/barrier/read-back, keyed on item.id instead of role.id
```

Then:
- **cast** = `run_items([WorkItem(r.id, r, ctx, {}) for r in roles])` — `run_swarm` becomes a thin wrapper;
- **jury** = `run_items([WorkItem(f"{r.id}#{i}", r, ctx, {temperature}) for i in range(n)])` + the
  `verdict_rule` after;
- **map** = `run_items([WorkItem(u.id, map_role, {**base, "unit": u.text}, {}) for u in units])`.

This is a *small* refactor of `_one`/`ready_set`/`addresses` (cognition.py:558-578) — the gate, SlotBudget,
barrier, rollup, fail-loud, `run://` machinery are unchanged. It is the cleanest way to land the net-new axis
(§1) **without** a parallel executor, and it makes the "files-as-units instead of roles-as-units" line in
anchor §6 literally true at the code level. Offer it grounded, not asserted — the alternative (a separate
`run_map` that copy-pastes the pool body a fourth time) works too but violates reuse-don't-parallel.

> **Caveat to verify before building (Inferred):** `run_swarm`'s `_one` closes over `ctx` (cognition.py:571);
> `run_items` must close over `item.ctx`. The `temperature` knob is already threaded for the jury
> (cognition.py:677). I have **not** run a `run_items` refactor; the claim "the body is identical" is read
> from the three functions side-by-side, not executed. It is a strong Inferred, not Verified.

---

## 3 · The `map_schema` enforcer — the real transport story, and the unproven seam (Observed + Inferred)

The anchor §3 wants `map_schema` to be "the structured output shape per unit (`json_schema`-enforced)" and
§6 says "the `json_schema` transport already makes the map output a typed record by construction." Half right.
Here is the *actual* state of structured output in the fabric:

**Two enforcement paths exist, and `run_role` uses the weaker one (Observed, transport.py:28-50):**
```
_apply_response_format precedence:
  1. opts["json_schema"]  →  response_format {"type":"json_schema","json_schema":{"name","schema":<dict>}}
                             SERVER-SIDE schema-CONSTRAINED decoding (vLLM guided outputs)   [transport.py:47]
  2. opts["schema"] or opts["json"]  →  {"type":"json_object"}  (bare JSON, no shape constraint) [:49]
  3. neither → free text
```
`run_role` (cognition.py:115-118) calls `client.complete(t, msgs, schema=role.output_schema, json=True, …)`
— that is **path 2** (the `json_object` path). The shape guarantee there is **client-side**: `complete()`
parses + validates against the Pydantic `output_schema` + retries on malformed (cognition.py:99-100,
transport.py docstring :42-46). It does **not** use server-side constrained decoding.

**Why this matters for a *compiled* chain (the chain-tying observation):** a role's `output_schema` is a
Pydantic *class* (roles.py:84, validated at roles.py:150-154 as `issubclass(BaseModel)`). **A model cannot
emit a Python class** (and `rules.py` forbids `eval`/`exec` of model output). So a *compiled* or *saved*
chain's `map_schema` **must be a JSON-Schema dict** — which means it rides **path 1** (`json_schema`,
transport.py:47-48, which already accepts exactly the `{"name", "schema":<dict>}` shape a compiler would
emit). This single fact ties three findings together:
- the compiler emits data → `map_schema` is a dict, not a class;
- a dict `map_schema` → transport path 1, not the path `run_role` uses today;
- so `run_role`/`run_items` need a **new opt** to pass `json_schema=` through (currently only `schema=`+`json`
  are wired in cognition.py:116) — a one-line addition, but a real one.

**The honest unknown (mark this a SEAM, not solved):** transport.py path 1 is **present-but-unproven on the
resident 4B.** suite.py:7053 records `json_schema_transport false-greened by INVOCATION` — i.e. it passed only
when run under one PYTHONPATH and failed standalone; its server-side honouring on the resident vLLM is *not*
established. SEM-3 separately found the 4B emits **malformed JSON ~2-in-6 at temperature>0** even on the
`json_object` path. So the map-schema enforcer has **two** open questions:
1. does the resident vLLM actually honour server-side `json_schema` constrained decoding? (must probe);
2. if not, the compiled-dict chain needs a **client-side JSON-Schema validator** (the `jsonschema` lib, or
   converting the dict back to a Pydantic model via `pydantic.create_model`) in `complete()`'s retry loop —
   because today `complete()` validates against a *Pydantic class*, which a compiled chain doesn't have.

**Your-idea (the bridge):** `complete()` could accept either `schema=<Pydantic class>` (the hand-authored
role path, unchanged) **or** `json_schema=<dict>` (the compiled-chain path), validating the latter with
`jsonschema.validate` in the same retry loop. That keeps "compiled, saved, and hand-written chains all run
through one door" (§3) true at the *enforcement* layer, not just the dispatch layer. This is net-new but
small, and it is where the "typed record by construction" claim actually has to be earned.

---

## 4 · The reduce — it is `run_role` at `synth_model`, and `run_jury` is the wrong primitive (Observed)

The anchor repeatedly leans on `run_jury` as the reduce's adjudicate leg (§6 "run_jury's 2nd-model slot is the
reduce's adjudicate leg"; §8 lists it as a real anchor for the reduce). **This is wrong against the code, and
the correction is important because it changes what's net-new.**

`run_jury` (cognition.py:637-715): N varied draws of **one** role, then `result.verdict = vrule(ordered)`
where `vrule` is the role's `verdict_rule` — and the law (cognition.py:660-664, roles.py:106-107) is that
`verdict_rule` is a **PURE deterministic function over the draws (quorum/vote) — L2, never a model call.**
The docstring (cognition.py:651-653) explicitly says the 2nd-model/cloud tiebreak is a *future* shape the
`vrule` call-signature *accepts*, **not** something built. And `roles/verify_jury.py` + SEM-2/SEM-3 already
proved: *N draws on one model are correlated samples → variance, not error* — a same-model jury **cannot** be
the cross-unit reasoning/adjudication the reduce needs.

**So the reduce is structurally:**
```
reduce  =  run_role( reduce_role, ctx={"digest": <the joined map outputs>}, model=synth_model )
           └─ a SINGLE strong-model call whose ctx is the structured digest (never the raw corpus) [anchor §4]
```
There is **no existing primitive** for "fire one strong model over an assembled digest." But that is *exactly*
`run_role` (cognition.py:93) pointed at `synth_model` with a `digest`-shaped ctx — i.e. it is the *same*
net-new ctx→messages generalization from §1, used once at the top instead of N times at the bottom. The
reduce isn't a new mechanism; it's `run_role` with a different model binding and a `reduce_prompt`.

**Where `run_jury` *does* belong:** at the **MAP tier**, as a per-unit jury — when a single unit's extraction
is consequential and you want the variance-smoothing of N draws + a quorum verdict on *that one unit*. That is
SEM-3's "S1 clears with schema + variance-jury + positive-only." So `run_jury` is a *map-worker option*, not
the reduce. Put it in the chain config as a per-unit knob (`map_draws: int`), not the reduce stage.

**Consequence for the schema:** the reduce needs a `reduce_prompt` + a `reduce_schema` (the answer's shape) +
the `synth_model` binding — and it runs via the same `run_role`/`complete` path, so the §3 transport seam
covers it. The reduce's *hierarchical staging* (anchor §7.3, the 400-file digest that doesn't fit one
context) is a **`passes`-level** concern (§5), not a primitive-level one — the primitive just needs to be able
to fire reduce over *a* digest; whether that digest is the whole map or a cluster-of-the-map is the `passes`
plan's job.

---

## 5 · The declared `Chain` schema, shaped against the real types (Your-idea, grounded field-by-field)

Holding §1-§4, here is the chain config *actually* shaped so it (a) rides `run_items`/`run_role` with the
minimal seam, (b) is emittable-by-a-compiler / executable-by-a-runner / saveable-as-a-named-config, (c)
composes the four faces. Every field is justified against a real primitive.

```
Chain = {                                                  # a DECLARED DATA dict — a compiler can emit it
  id:            str                                       # the chain id == file name (mirrors role/node)   [roles.py:141]
  label/description: str                                   # operator-facing (the config lab renders these)  [roles.py:18]

  # --- the MAP stage ---
  unit_selector: { kind: "dir_glob"|"file_list"|"registry_slice",
                   value: str|list }                       # which units. NET-NEW: a unit enumerator (§6)
  map_prompt:    str                                       # the contained per-unit instruction (≈ a role prompt_template) [roles.py:84]
  map_schema:    <JSON-Schema dict>                        # the per-unit output shape — a DICT, not a Pydantic class (§3)
  map_model:     { requires:[...], default_model, default_base_url }  # the WORKER tier — the role.model_binding shape EXACTLY [roles.py:110-117]
  map_draws:     int = 1                                    # >1 ⇒ each unit is a per-unit JURY (run_jury at the map tier — §4)

  # --- the PASSES plan (the multi-pass / conditional loop) ---
  passes:        "single" | "map_reduce" | "map_pair_map" | "map_reduce_drill"   # the staging plan (§7)

  # --- the REDUCE stage ---
  reduce_prompt: str                                       # how the strong layer joins/composes
  reduce_schema: <JSON-Schema dict>                        # the answer's shape
  reduce_model:  { requires:[...], default_model, default_base_url }  # the SYNTH tier — same binding shape [roles.py:251 resolve_binding]
}
```

**Why each field maps to a real primitive (the reuse argument, field by field):**

- `id` == filename → discovered exactly like a role (roles.py:141 `rid != name → raise`) or a node-type
  (registry.py:55 `discover`). **Observed.**
- `map_prompt` + `map_schema` → **a role, expressed as data.** A role *file* declares `prompt_template`
  (str) + `output_schema` (Pydantic class). A chain declares `map_prompt` (str) + `map_schema` (dict). The
  only delta is class-vs-dict, which is the §3 transport seam. So **a chain's MAP stage *is* a synthesized
  role** — `build_chain` can mint an in-memory `Role` from `(map_prompt, map_schema_as_validator, map_model)`
  and hand it straight to `run_items`. **Your-idea, grounded in roles.py:84/:128.**
- `map_model`/`reduce_model` → the **exact `model_binding` shape** roles already declare (roles.py:110-117)
  and `resolve_binding` already resolves via the capability query `requires ⊆ provides` (roles.py:251-284).
  The "configurable tiers read from the model registry" (anchor §4) is **already built** — a chain reuses it
  verbatim. The worker-tier rule (anchor §4: match worker to the per-unit task) is enforced by `requires`:
  the research-wave face declares `requires:["deep-reasoning"]` (strong workers), the coherence face declares
  the 4B's caps. **Observed (the binding machinery) + Your-idea (the per-face requires).**
- `unit_selector` → the **one genuinely net-new sub-mechanism besides the dispatch axis**: a *unit
  enumerator* that turns a selector into a `list[WorkItem]`. `dir_glob`/`file_list` are pure filesystem;
  `registry_slice` reuses the existing registries (the node library, the role registry, the address store).
  Net-new but small and pure. **Your-idea.**
- `passes` → the conditional loop. v1 = `single`/`map_reduce`; `map_pair_map` is SEM-2's "structural surfaces
  the pair → a 2nd map judges it"; `map_reduce_drill` is the anchor's decide-next. This is the field that
  carries the most unbuilt machinery (§7) — keep it a small enum in v1, grow it. **Your-idea.**

**This composes the four faces as instances (anchor §3 / SEM-1, grounded):**
```
research-wave  = unit_selector(per-area) · map_model.requires=[deep-reasoning] · passes=map_reduce
                 · map_prompt="write a grounded companion for this area" · reduce_prompt="synthesize companions"
coherence-scan = unit_selector(dir_glob *.py) · map_model.requires=[chat,json] (the 4B) · map_draws=3 (jury)
                 · passes=map_pair_map (structural surfaces the pair) · reduce_prompt="adjudicate + wired∧meaningless"
onboard/map    = unit_selector(dir_glob) · 4B map · passes=map_reduce · reduce_prompt="write the true orientation"
repo-QA        = compile(question)→Chain · passes=map_reduce_drill · reduce decide-next over the warm digest
```
The faces differ **only in field values** — same runner. That is the universal-composition claim, *earned*
against the schema rather than asserted.

---

## 6 · "Is a chain a declared type discovered like a role?" — yes for the library, but the registry is the small half (Observed + Your-idea)

The Company has **two** existing declared-composition substrates, and a chain has to be located against both:

1. **Roles** (runtime/roles.py) — file-discovered (`RoleRegistry.discover`, :186), self-registering, one
   file per role, `id == filename`, validated at `_build_role` (:128), discovered the way node-types are.
2. **Node-graphs** (runtime/registry.py + scheduler.py) — node-*types* are file-discovered (registry.py:55),
   and *graphs* (compositions of node instances) are **saveable named configs**: `Suite.save_graph`
   (suite.py:1018) + `Suite.list_graphs` (suite.py:883) + `run_graph` (MCP). A graph is literally "a declared,
   compilable, configurable map over a corpus" *shaped* — which is suspiciously close to a chain.

**So the fork the anchor glosses: is a chain a saved role-type, or a saved node-graph?** The grounded
discriminator settles it:

> **The node-graph scheduler is strictly serial** (scheduler.py:64 `while len(processed) < len(execs) and
> progress:` — a single-threaded re-scan loop, synchronous `mod.run()` per node, *no* ThreadPoolExecutor;
> confirmed by cognition.py:356-357 "leaving `runtime/scheduler.py:run()` strictly serial so the app's
> Suite.run behaviour is UNCHANGED — *one substrate, two drivers*"). **The concurrent MAP cannot ride a
> node-graph** — it would run N units one-at-a-time. It MUST ride `run_swarm`/`run_items` in the *cognition
> driver*, which is the parallel one.

That is the *structural* reason a chain is **not** a saved node-graph: the two declared substrates split on
the **serial/parallel driver line** (the "two drivers, one substrate" law). A chain lives on the *parallel*
(cognition) side. So: **a chain is a declared type discovered like a role/node-type — but it is its own type,
not a reuse of the graph type.** A `chains/` directory, one `chains/<id>.py` (or `.json`) file per saved
chain, `id == filename`, a `ChainRegistry.discover` mirroring `RoleRegistry`/`NodeRegistry` exactly.

**BUT — the registry is the *small* half, and leading with it would mis-frame the build (the key correction).**
The anchor's load-bearing claim (§3) is *"the runner executes any valid instance — it doesn't care if the
config was compiled or hand-written or saved."* What makes that true is **not** the registry (the registry
only handles the *saved* case). It is a **single validator+builder, `build_chain(decl) -> Chain`, mirroring
`_build_role` (roles.py:128)**, that:
- the **compiler** calls on its emitted dict (catches a mis-compiled chain at the door — anchor §7.1);
- the **registry** calls on each discovered file (the saved-library path);
- an **ad-hoc/hand-written** dict goes through unchanged.

One door, three sources, validated identically. `_build_role` is the exact template: it type-checks the dict
(roles.py:132), requires `id` (:137), checks `id == name` (:141), rejects unknown fields (:145), validates
the `output_schema` type (:150), validates declared rules with a static whitelist-walk (:164-165), and
fail-louds on every malformed shape. **`build_chain` is the same function for the chain schema** — it
validates `unit_selector.kind` is known, `map_schema` is a well-formed JSON-Schema dict (not a class —
§3), the `map_model`/`reduce_model` bindings resolve, and `passes` is a known plan. **That validator is the
real reuse and the real net-new core — write it first, the registry second.** **Your-idea, grounded in
roles.py:128.**

---

## 7 · The hard parts, against the code (what's genuinely net-new vs reuse)

A clean ledger of net-new-seam vs reuse, since Tim asked for "what needs building":

**REUSED 100% (Observed — these are *not* net-new):**
- the pool / barrier / `as_completed` / fail-loud-re-raise (cognition.py:585-595);
- the `SlotBudget` derived from the live registry (cognition.py:403-450) — the chain's worker concurrency
  is *already* registry-derived, never a hardcoded N;
- the `global_vram_gate` cross-driver bound (cognition.py:462-470);
- the `run://` addressed write + canonical `resolve_run_ref` read-back (cognition.py:474-496) — the digest is
  *already* a set of addressed records by construction (this is anchor §9's "digest as a `run://`-addressed
  warm substrate" — it's *already true* of every map output);
- the batched-rollup telemetry (cognition.py:602-611) — the chain's run-record is the wave's run-record;
- the `model_binding`/`resolve_binding` capability-query tiering (roles.py:251-284) — the configurable
  worker/synth tiers are already built;
- the role-registry discovery pattern (roles.py:186) — the chain registry is a copy of it.

**NET-NEW (the real seam list, smallest-first — Your-idea, grounded):**
1. **The fan-out axis inversion** (§1-§2): `run_items(work_items)` so 1 role × N units rides one pool. The
   single most important net-new mechanism. ~a refactor of `_one`/`ready_set`/`addresses`.
2. **`run_role` per-item ctx** (the inner half of SEM-1's seam): `ctx["utterance"]` (cognition.py:109)
   generalizes to a declared input mapping so a worker can read a *unit* (and the reduce can read a *digest*).
3. **The `json_schema` (dict) enforcement path** (§3): wire `json_schema=` through `run_role`/`complete`, and
   **probe whether the resident vLLM honours server-side constrained decoding** (suite.py:7053 says unproven)
   — else a client-side `jsonschema` validator. This is the trust-bearing seam.
4. **The unit enumerator** (§5): `unit_selector → list[WorkItem]`. Pure, small.
5. **`build_chain(decl)` validator** (§6): the one-door reuse of `_build_role`. Net-new but templated.
6. **The compiler** (anchor §7.1, the make-or-break): a strong-model `run_role` that emits a `Chain` dict,
   gated by `build_chain`. This is the *new load-bearing unknown* — and `build_chain` is exactly the
   inspect-approve gate that catches a mis-compiled chain (anchor §7.1's "is the inspect-approve gate
   enough?" — the gate *is* the validator; a chain that fails `build_chain` never runs).
7. **The `passes` executor** (§5): v1 = `single`/`map_reduce` (trivial — fire map via `run_items`, fire
   reduce via `run_role`). `map_pair_map`/`map_reduce_drill`/hierarchical-reduce (anchor §7.2/§7.3) are the
   genuinely harder, later passes. The conditional decide-next loop (anchor §7.4) is a small smart judgment
   = another `run_role` at `synth_model` — itself a chain stage, the recursion the anchor §9 notices.

**The CLI verbs** (anchor §6): `company research <dir>` / `company ask <dir> "<q>"` / `company onboard` slot
into `ops/cli/app.py`'s flat verb dispatch (app.py:124-200, a `if cmd == "...":` chain) exactly like
`company suites` (app.py:133) — each verb loads a saved chain by id and runs it. Thin wiring, no net-new
engine. **Observed.**

---

## 8 · Two corrections the chain inherits from SEM-3 that the *primitive* must encode (Observed + Inferred)

The primitive is not trust-neutral; two SEM-3 results must be **structural in the schema**, not left to the
caller:

1. **`map_draws` (per-unit jury) smooths variance, never error** (cognition.py:660-664; SEM-3). So a chain
   whose *correctness* depends on the map being right (any deep-reasoning face) **must** route through a
   strong `reduce_model`, not a bigger `map_draws`. The schema should make this hard to get wrong: if
   `map_model.requires` lacks `deep-reasoning` AND `passes == "single"` (no reduce), `build_chain` should
   **warn or refuse** — a cheap-map-only chain that claims to answer a deep question is the confidently-wrong
   trap (anchor §7.5's "does compile introduce a new trust surface"). **Your-idea, grounded in SEM-3.**

2. **The reduce is the correctness gate; the map is candidate-generation** (SEM-3 trust ladder). The primitive
   encodes this by *construction*: the map output is always a `run://`-addressed *candidate record*, never an
   action; only the reduce (or a stronger-model confirm) produces the answer. This is already how `run_swarm`
   works (it writes records, takes no action — cognition.py:573). The chain inherits positive-only for free.

---

## 9 · Everywhere it connects (the map Tim asked for)

```
                         ┌──────────────────────  THE CORPUS-CHAIN PRIMITIVE  ──────────────────────┐
                         │                                                                          │
  fabric/transport.py    │   compile (run_role @ synth) ── build_chain(decl) ──┐                    │
   json_schema path  ────┼──▶ map (run_items: 1 role × N units, run:// each) ──┤  ALL three stages  │
   (§3 seam, unproven)   │   reduce (run_role @ synth over the digest) ────────┘  are run_role/items │
                         │        ↺ decide-next (run_role @ synth) — the recursion                  │
                         └────┬──────────────┬───────────────┬───────────────┬─────────────────────┘
        runtime/cognition.py  │   roles.py    │  registry.py  │  scheduler.py │   ops/cli/app.py
        run_swarm/run_jury    │ model_binding │ discover ptn  │  SERIAL (why  │   company research/
        (the engine, REUSED)  │ resolve_bind  │ (chains dir)  │  chain≠graph) │   ask/onboard verbs
                              │ _build_role   │               │               │
                              │ (→ build_chain│               │               │
                              │  template)    │               │               │
```

- **The two prior rounds are faces (anchor §6).** coherence-scan = `map(per-file 4B findings) → reduce
  (adjudicate + wired∧meaningless)`; research-wave = `map(deep per-area) → reduce(synthesize)`. **Building
  the primitive *is* building both** — which is the anchor §9 reorder-the-roadmap claim, and it's *grounded*:
  every field of both faces maps to a chain field (§5), and the engine is the one in cognition.py the
  cognition session already owns. The coherence substrate's *finding-type-as-declared-role* (COHERENCE §6) is
  the same registry move as *chain-as-declared-type* (§6 here) — one discovery pattern, two consumers.
- **The model registry** (native-model-layer) feeds `map_model`/`reduce_model` via `resolve_binding` — already
  built (roles.py:251). The configurable-tiers claim (anchor §4) costs **zero** net-new.
- **The RHM / up_translate** (COHERENCE §1.3, suite.py:5828 `up_translate('finding')`) consumes a reduce
  output: a fresh corpus-chain read is the whole-repo digest the right-hand-man answers over (anchor §9). The
  reduce *is* the up-translate's grounded input.
- **Self-hosting** (the introspective-data law): the chain's run-record (the batched rollup, cognition.py:603)
  is itself a corpus the chain could later map over — the system instrumenting its own understanding-passes.
- **The digest as a cached artifact** (anchor §9 "ingest once, query many"): every map output is *already*
  `run://`-addressed and content-addressed (`put_content` is CAS, cognition.py:573). The cache-invalidation
  story (anchor §7.6) is the existing own/reflect split (COHERENCE §2): re-derive the map when the corpus
  changes (detection = reflect), keep the disposition/answer (reduce output = own). The chain inherits the
  coherence substrate's *exact* warm-cache discipline — they are the same law.

---

## 10 · The "yes, but actually" list (what I corrected in the anchor)

- **"generalize `ctx→messages` is the one net-new seam" (SEM-1, anchor §6/§8)** → *actually* that is the
  *inner* half; the *outer* half is a **fan-out axis inversion** (N roles×1 ctx → 1 role×N units), which
  `run_swarm` cannot express today (cognition.py:558-571). Both are net-new; the axis is the bigger one.
- **"`run_jury`'s 2nd-model slot is the reduce's adjudicate leg" (anchor §6/§8)** → *actually* `verdict_rule`
  is a **pure no-model function** (cognition.py:660-664); `run_jury` is a *map-tier* variance-smoother, not the
  reduce. The reduce is a strong `run_role` over the digest — no existing primitive, but it *is* `run_role`.
- **"the `json_schema` transport already makes the map a typed record by construction" (anchor §6)** →
  *actually* `run_role` uses the weaker `json_object`+client-Pydantic path (cognition.py:115); the
  `json_schema` server-side path exists (transport.py:47) but is **unproven on the resident 4B**
  (suite.py:7053) and the 4B emits malformed JSON ~2/6 (SEM-3). The enforcer is a real trust seam, not solved.
- **"a chain is a declared type discovered like a role" (anchor §3)** → *actually* true, but it must be its
  **own** type, not a saved node-graph — because the graph scheduler is **serial** (scheduler.py:64) and the
  map is parallel; and the registry is the *small* half — the **validator (`build_chain`)** is the load-bearing
  reuse that makes "runs any valid instance, compiled/saved/hand-written" true.
- **"`map_schema` is `json_schema`-enforced" (anchor §3)** → *actually* it must be a **JSON-Schema dict**
  (a compiler emits data, not a Pydantic class — roles.py:150), which forces transport path 1 + a new
  `json_schema=` opt on `run_role`/`complete`.

---

## 11 · One paragraph for the cross-read

The corpus-chain primitive is real and is *mostly already built* — it is `run_swarm`'s engine (the pool,
the registry-derived `SlotBudget`, the cross-driver VRAM gate, the `run://` addressed writes + canonical
read-back, the batched rollup, fail-loud) reused 100% verbatim, plus the configurable worker/synth tiers
that `resolve_binding`'s capability query *already* provides — but the anchor mis-described three load-bearing
pieces, and the corrections make it simpler. The one real net-new mechanism is a **fan-out axis inversion**
(`run_swarm` fans N roles × 1 shared ctx; the MAP needs 1 role × N units), cleanest landed as a small
`run_items(work_items)` refactor that *also* subsumes the cast and the jury — universal composition at the
engine level. The reduce is **not** `run_jury` (a pure no-model variance-smoother that belongs at the map
tier as `map_draws`); it is a strong `run_role` over the digest at `synth_model`. The `map_schema` cannot be a
Pydantic class because a compiler emits **data**, so it must be a JSON-Schema dict riding transport's
`json_schema` branch — which is present but **unproven** on the resident 4B and is the one genuine trust seam.
And "a chain is a declared type discovered like a role" is right but secondary: the chain is its **own** type
(not a saved node-graph, because the graph scheduler is serial and the map is parallel — the "two drivers, one
substrate" line is the discriminator), and the load-bearing reuse is a single **`build_chain(decl)` validator**
mirroring `_build_role`, which gates the compiled, the saved, and the hand-written instance through one door —
*that* is what makes the anchor's "the runner executes any valid instance" actually true, and it is the first
thing to build. The four faces (research-wave, coherence-scan, onboard, repo-QA) then differ only in field
values of one schema over one runner, which is the universal-composition payoff, earned field-by-field against
the real types rather than asserted — and building the primitive *is* building the two prior rounds, since
every field of both faces maps onto a chain field.
