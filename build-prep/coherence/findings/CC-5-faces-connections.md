# CC-5 · The faces as concrete chain-configs + the everywhere-it-connects map + the honest roadmap-collapse take

> Companion to `CORPUS-CHAIN-ANCHOR.md`. My allocated area: **the faces + compositionality + everywhere-it-connects** — the
> integration/cartography lane. I read the real engine (`runtime/cognition.py` `run_swarm`/`run_role`/`run_jury`),
> the structured-output transport (`fabric/transport.py`), the role registry (`runtime/roles.py` + `roles/check.py`),
> the CLI dispatch (`ops/cli/app.py`), the address grammar (`contracts/address.py`), the projection-sibling
> pattern (`contracts/cognition_info.py`), the up-translate organ (`runtime/suite.py:5856`), and the two prior
> rounds' synthesis docs + the SEM companions that overlap my lane (SEM-1 engine, SEM-5 CLI faculties, SEM-6 frame).
>
> **My job is NOT to confirm "all five faces are configs."** It is to take the `Chain` schema (anchor §3) and
> *press each face through it* until it leaks — because the leaks are where the real escape-hatches and the real
> build-work live. I found two structural leaks the anchor's tone hides, a synth-tier binding gap, and a roadmap-
> collapse that is **partial, not total** (a breathless "three rounds become one" would contradict the prior rounds,
> and they would catch it).
>
> **Marking:** **[OBS]** observed in code (file:line) · **[INF]** inferred from observed facts, not executed ·
> **[PRIOR-ART]** external · **[IDEA]** my proposal, not in the repo today. I did not run a chain; the capacity
> numbers I inherit from SEM-1's measured recombination (I do not re-derive them — that was its lane).

---

## 0 · The headline (read first)

The corpus-chain primitive is **real as a topology** — `map(per-unit structured extraction) → reduce(join/adjudicate/
compose) ↺ decide-next` maps cleanly onto `run_swarm` + a strong reduce, and every face I pressed through it keeps
its *shape*. But the anchor's **economic** argument (§0, §4) — *"the cheap layer touches every byte; the smart layer
only ever reads small things"* — **does NOT hold for two of the five faces**, and one of those two is **this very
research wave**. So the honest landing is sharper than the anchor's:

1. **The topology generalizes; the cost-shape does not.** Three faces (coherence-scan, onboard, repo-QA, doc-staleness)
   are the anchor's elegant shape — cheap-map, small-reduce-input. **The research-wave face inverts BOTH halves of the
   cost argument** (expensive strong-model workers writing deep companions; a reduce that reads *large* companions, not
   a small digest). The anchor §4 admits the worker exception in one clause; it does not admit that the *reduce* input
   also blows up. **We are living the inversion right now: this wave's map is six Opus subagents, its reduce reads six
   large companions.** The round's own process is the *worst* fit to the primitive's cost-shape — and naming that is
   the "yes, but actually" the anchor asked for.

2. **The reduce needs a declared SIDE-INPUT beyond the map digest — the one real schema-extension I found.** The clean
   "reduce reads only the structured digest" model (anchor §0 line 41, §4) is too tidy. coherence-scan's signature
   finding (the wired∧meaningless join, the literal prize of the two prior rounds) needs the **structural graph** as a
   second input the map never produced; onboard's reduce joins the digest ⨝ the **owned dispositions** (an external
   record, not re-derivable from the corpus); repo-QA's reduce needs the **question**. So `Chain` needs a
   `reduce_inputs` field (declared side-inputs), not just `reduce_prompt`. This is a real, small, load-bearing
   correction.

3. **Saved-vs-compiled is the node-type/role pattern again, and it ALREADY HAS A WORKING PRECEDENT.** A saved chain is
   a declared file the registry discovers — exactly how `roles/*.py` self-register (`RoleRegistry.discover`,
   `roles.py:186` [OBS]) and how node-types do (`build_object_info`). `roles/check.py` is *already* a one-unit semantic
   detector in the role shape. So "common purposes are saved declared chains" is not new architecture — it is the
   third instance of the system's universal-composition law, and the registry machinery to discover a `chains/*.py`
   file is the same machinery already running for roles and nodes.

4. **The roadmap-collapse is PARTIAL — and the partition is exact.** Building the primitive first collapses the
   **LLM-read half** of three roadmaps (research-wave, the semantic detector class, onboard/repo-QA/doc-staleness) into
   *configs of one engine* — that is real and high-leverage. But it does **not** subsume: (a) the structural three-leg
   graph (SEM-6's own headline: the structural detector "is not the swarm" — it is AST+registry+event-log [OBS-SEM6]);
   (b) the own/reflect disposition store (the one genuinely net-new persisted thing — Coherence §2); (c) the loop
   front-half + the safety pieces (Coherence §4); (d) the calibration harness (Semantic §8). Those four **compose
   with** the primitive; they do not fold into it. The honest line: *the primitive collapses the cheap-LLM-read
   faculties into one engine; the structural + disposition + loop + calibration machinery stays orthogonal and still
   has to be built.* Three rounds become **one engine + four orthogonal pieces**, not one thing.

5. **The synth tier has no home in the registry yet.** "The model registry feeds the configurable tiers" (anchor §6)
   holds for the **worker** tier (the local 4B; `SlotBudget.from_registry` reads `ops/services.json` [OBS
   cognition.py:411]). It does **not** hold for the **synth** tier (cloud Opus — not a GPU-resident service in
   `services.json`). `resolve_binding` is "resident-only today" ([OBS roles.py:265]). Binding a cloud synth needs the
   **G8 capability catalog that doesn't exist yet** — concrete what-needs-building at a connection seam the anchor
   glosses.

Everything below substantiates these five against the real code.

---

## 1 · The `Chain` schema, pressed through every face (the deliverable's core)

The anchor's declared object (§3):

```
Chain = { unit_selector, map_schema, map_prompt, passes, reduce_prompt, worker_model, synth_model }
```

I filled each face's config concretely from the real code, and added the column the anchor's table doesn't have —
**where it leaks / needs an escape hatch.** This table IS the deliverable's spine.

### 1.1 The faces table

| field → | **coherence-scan** | **onboard / map** | **repo-QA** | **doc-staleness** | **research-wave** |
|---|---|---|---|---|---|
| **unit_selector** | changed/all source files (`*.py`,`*.ts`) + their `AGENTS.md` | the core source tree by module (a module + its `AGENTS.md` = the natural unit, SEM-1 §3) | a *narrowed slice* (grep/registry-filtered to the question) | every `*.md` doc + the symbol/registry it names | **a semantic AREA** (not a file) — carved by hand today |
| **map_schema** | `{kind, address, contradicts:bool, note}` (the `roles/check.py` shape [OBS]) | `{module, what_it_is, what_moved, half_built:[...], constitution_ref}` | `{file, relevant:bool, snippet, address}` | `{doc, names, still_true:bool, drifted_claim}` | **a whole companion .md** — NOT a small typed record |
| **map_prompt** | "read this module vs its AGENTS.md → contradiction?" | "summarize what this module IS and what moved" | "does this file answer Q? extract the grounding" | "does this doc still describe the code it names?" | "explore this AREA across everything; write fully; mark evidence" |
| **passes** | `map → reduce` (+ optional `pair → map` for cross-file half-migration — SEM-2's chain) | `map → reduce` | `compile(Q) → map → reduce` (↺ followup over warm digest) | `map → reduce(cluster)` | `map → reduce(synthesize)` (single pass) |
| **reduce_prompt** | "adjudicate candidates + emit the wired∧meaningless join" | "write the true orientation, fold in dispositions" | "compose a tagged conditional answer + addresses" | "cluster + report stale docs" | "read all companions whole; take positions; name decisions" |
| **worker_model** | **4B** (contained extraction — its strong mode, SEM-3) | **4B** | **4B** | **4B** | **STRONG (Opus subagents)** — the exception |
| **synth_model** | strong (Opus / a Claude Code agent) | strong | strong | strong | strong |
| **WHERE IT LEAKS** | reduce needs a **side-input** (the structural graph) the map never produced — see §2.2 | reduce needs a **side-input** (the owned dispositions) not re-derivable from the corpus — §2.2 | the `compile` stage is a **new trust surface** (Area-3's lane, not mine) — and "narrow the slice" is a pre-map step the schema doesn't name | the cleanest fit — genuinely a pure map→reduce, smallest leak | **inverts the cost-shape on BOTH halves** — expensive map AND large reduce-input — §2.1 |

### 1.2 What the table shows

- **The topology holds for all five** — every face is `map → reduce` with an optional pre-stage or loop. The anchor's
  central structural claim ("one primitive, five configs") survives the press. [INF, from the table]
- **The cost-shape holds for only three-and-a-half** — coherence-scan, onboard, repo-QA, doc-staleness are cheap-map /
  small-reduce-input (the anchor's elegance). research-wave breaks it on both halves (§2.1). repo-QA's *compile* stage
  is a real cost/trust surface but it's Area-3's lane, not mine. [INF]
- **Three faces need a reduce side-input** the map didn't produce (coherence-scan, onboard, repo-QA) — the one real
  schema gap (§2.2). [INF]

---

## 2 · The two structural leaks (my rigor seam — the gold)

### 2.1 research-wave inverts the cost-shape — and we are living the inversion

The anchor's elegance, stated twice (§0 line 41, §4 lines 120-124):

> *"the smart model only ever touches small things — the freeform intent (compile) and the structured digest (reduce).
> It never reads the raw corpus. The cheap parallel layer does the only thing that touches every byte."*

**The research-wave face violates BOTH clauses, not one.** [INF, grounded in the skill + the anchor's own §4]

1. **The map is expensive, not cheap.** A research-wave worker doesn't do contained extraction → a small typed record;
   it does *genuinely deep per-area reasoning* and writes a full companion. The anchor §4 admits this in one clause
   ("the research-wave *face* gives its workers genuinely deep per-area reasoning... so *that* face configures strong
   workers"). So the cheap-map half is already conceded for this face.
2. **The reduce-input is large, not small** — and *this* the anchor does NOT admit. The reduce reads the *companions*,
   which are large `.md` documents (SEM-1's companion is ~300 lines; this one will be similar). The "structured digest"
   the anchor says the reduce reads is, for research-wave, **the full set of long-form companions** — there is no small
   typed digest. The reduce's input scales with `n_areas × companion_size`, not with `n_units × small_record`.

**The sharpest version — the recursion the anchor invited:** this round IS the research-wave applied to building the
research-wave. So *the round's own process is the worst-fitting face to the primitive's cost-shape.* The map here is
six Opus subagents (the most expensive worker tier in the registry, anchor §4); the reduce (the synthesis I'll feed
into) reads six large companions. If the corpus-chain primitive's value proposition is "expensive intelligence applied
only to compressed, complete, structured inputs," then **research-wave is the config where that proposition is false on
both ends** — and it's the config the anchor used to *generate itself*.

**Why this matters for the build (not just a gotcha):** [IDEA] it means `worker_model` and the reduce's input-size are
*independent knobs*, and the `Chain` schema must let a face declare **strong workers AND large reduce-inputs** without
the runner assuming the cheap-map / small-digest economics. A runner built only for the cheap shape (a 4B map writing
tiny JSON, a small digest reduce) would *not* run the research-wave face — it would need the worker tier to be
Claude-Code subagents and the reduce to tolerate large inputs. So research-wave is the face that **forces the runner to
be tier-agnostic from day one** — which is good (it stops the runner from over-fitting to the 4B-swarm shape), but it
means the anchor's "the cheap layer touches every byte, the smart layer reads small things" is a property of *most*
configs, not an *invariant of the primitive*. State it as: **a saved-chain property, not a primitive guarantee.**

### 2.2 The reduce needs a declared SIDE-INPUT — the one real schema-extension

The anchor's model: `reduce(prompt, digest) → output`. The reduce reads the map's structured digest and nothing else.
**Three faces break this**, each needing a second input the map never produced:

- **coherence-scan's signature finding needs the structural graph.** The wired∧meaningless join (Semantic §7, the
  literal prize of the two prior rounds) is *structural-says-wired ∧ semantic-says-meaningless*. The semantic map
  produces "meaningless"; "wired" comes from the **structural three-leg graph** (AST + registry + event-log, Coherence
  §3) — a separate detector the swarm did not run. So the reduce that emits the prize finding reads **digest ⨝ the
  structural graph**, not the digest alone. [INF, from Semantic §7 + Coherence §3]
- **onboard's reduce joins digest ⨝ the owned dispositions.** SEM-5 §2.3 established onboard = "fresh semantic
  detection (reflected) ⨝ the owned disposition history (the institutional ADR log)" [OBS-SEM5]. The dispositions are
  the **un-recomputable** records (Coherence §2) — by definition the map cannot produce them; the reduce reads them as
  a side-input. [INF]
- **repo-QA's reduce needs the question.** The compiled question is an input to the reduce (compose a *tagged answer to
  Q*), not part of the per-unit digest. The anchor's `compile → map → reduce` flow has the question entering at compile
  and again at reduce. [INF]

**The escape hatch (the real schema-extension, [IDEA]):** add `reduce_inputs` to `Chain` — a declared list of
side-inputs the reduce reads alongside the digest (an address, a registry slice, the structural graph handle, the
question text). It rides the existing addressing (`run://`, `code://`, the disposition lane). This is *not* a hack — it
is the honest shape, and it keeps the reduce's inputs **declared and inspectable** (the same discipline the rest of the
system enforces). Without it, the highest-value face (the wired∧meaningless join) cannot be expressed as a chain at
all — which would be a silent hole in the "everything is a config" claim.

**Consequence for the cost argument:** a `reduce_inputs` side-input can itself be large (the structural graph, the full
disposition log) — so the "reduce reads only small things" claim weakens further. The honest reduce-cost model is:
`reduce_input = digest + Σ(side-inputs)`, and the runner must stage hierarchically when that sum exceeds the synth
context (anchor §7.3 — the staging-threshold hard part, which my leaks make *more* pressing, not less).

---

## 3 · Saved vs compiled — the node-type/role pattern, third instance

### 3.1 A saved chain IS a declared file the registry discovers (already-precedented)

The anchor §3: *"common purposes are saved chains (named declared configs you re-run); novel queries compile fresh."*
This is the system's universal-composition law, and the machinery already exists three ways over: [OBS]

- **Node-types** self-register: drop a `nodes/<type>.py`, `NodeRegistry.discover` picks it up, `build_object_info`
  serializes it, the canvas renders it — no canvas code (the ComfyUI-dynamic pattern, `cognition_info.py:7-10` cites
  it [OBS]).
- **Roles** self-register identically: drop a `roles/<id>.py` declaring a `ROLE` dict, `RoleRegistry.discover` picks it
  up ([OBS roles.py:186-198]), `Role.can_fire` = has `prompt_template` + `output_schema` ([OBS roles.py:91-93]).
  `roles/check.py` is a *one-unit semantic detector already in this shape* ([OBS]).
- **Rules** self-register and are statically whitelist-walked at discovery (`validate_role_rules`, [OBS roles.py:164]).

So **a saved chain is a `chains/<name>.py` declaring a `CHAIN` dict** — the same self-registering file pattern, a fourth
member of the family. [IDEA, but grounded: the pattern is identical to roles] The five faces become five files in
`chains/`. Adding a sixth face = dropping a sixth file. This is the anchor's "more types, not more tools" at the
orchestration layer — and it's the same registry code, not a fork.

### 3.2 The compiler is the on-ramp; saved chains are the library — but the COMPILE trust is Area-3's, not mine

The compiler turns freeform intent → a valid `CHAIN` instance (anchor §3: "the compiler emits a valid instance of this
schema; the runner executes any valid instance"). Through my *saved-vs-compiled* lens, two observations: [IDEA]

- **The compiler should emit a saved-chain-shaped object**, validated by the *same* static walk that validates a
  hand-written `chains/*.py` (mirroring `validate_role_rules` at role discovery, [OBS roles.py:164]). Then "compiled"
  and "saved" and "hand-written" are *byte-identical kinds of object* — the runner cannot tell which produced it, which
  is exactly the property that makes the primitive compose (anchor §3 line 95). The inspect-approve gate is then "show
  the compiled `CHAIN` dict before the map spends" — the same surface a saved chain already is.
- **A compiled chain that runs often should be promotable to a saved chain** — the library grows from compiler output.
  This is the natural lifecycle: novel query → compile → if reused, save → it becomes a face. [IDEA]
- **The compiler's *reliability* (can a smart model emit a valid, law-abiding chain?) is explicitly Area-3's lane**
  (anchor §7.1 tags it "this round's Area-3 — be skeptical"). I do not re-derive it. My only addition: the saved-chain
  precedent *lowers* the compiler's burden — for the five common purposes the compiler never runs (they're saved
  files); the compiler only ever handles genuinely novel queries, the long tail. So the compiler's failure surface is
  smaller than "every chain run," and the saved library is the safety floor under it. [INF]

---

## 4 · Everywhere-it-connects — the map of every connection point + what-needs-building

This is the cartography Tim asked for specifically. Each row: the connection, what's OBSERVED to exist, and the
concrete what-needs-building at the seam.

### 4.1 It IS `run_swarm` — the third application (the deepest connection)

[OBS] `run_swarm(roles, ctx, store, *, turn_id, budget, emit, ...)` (cognition.py:523) is the map+barrier+batched-
rollup+read-back engine. `run_jury` (cognition.py:637) is the reduce's *adjudicate* leg (the 2nd-model slot the verdict
rule reserves, cognition.py:649-651). The `json_schema` transport branch (transport.py:47-48) makes each map output a
typed record by construction. The three applications: cognition turn (round 1) · semantic coherence (round 2) ·
**corpus-query (this round)** — same engine, files-as-units instead of roles-as-units.

**What-needs-building at this seam:** the **one net-new seam SEM-1 isolated** [OBS-SEM1 §4]: `run_role` hardcodes
`content = f"Utterance: {utterance}"` and requires `ctx["utterance"]` (cognition.py:109-113). A unit-reading worker
reads a *file artifact*, not an utterance. The fix: generalize `run_role` to a **declared ctx→messages mapping** — the
role declares what it reads via `input_addresses` (the field *exists* in the role schema, roles.py:67, but is
"descriptive today" [OBS roles.py:26]). Make `input_addresses` *active*: the runner resolves each declared address into
the message. Small, but it touches the shared `run_role`, so it stays behind the schema-validate/fail-loud discipline.
This is the **single most load-bearing build-item** — without it no face's map can read a file.

### 4.2 It is the substrate UNDER the two prior rounds (the roadmap-collapse seam)

[INF, grounded in the syntheses] The Semantic round's detector "**is** `run_swarm`" (SEM-6 §2.0, verbatim headline).
The research-wave skill is a manual chain. So:

- **The semantic coherence layer = a saved coherence-scan chain.** Building the primitive builds the thing that makes
  the semantic round real. [INF]
- **The research-wave = a saved research chain** (with the cost-shape caveat, §2.1). Building the primitive productizes
  the manual skill. [INF]
- **onboard / repo-QA / doc-staleness = SEM-5's faculties = saved chains.** SEM-5 already mapped them to CLI verbs;
  this round says they're *configs of one engine*, not five drivers. [INF]

**The PARTIAL collapse (the honest take, contradicting a breathless "three become one"):** building the primitive
collapses the **LLM-read half** of these roadmaps. It does **NOT** subsume four orthogonal pieces:

| Piece | Why it does NOT collapse into the primitive | Source |
|---|---|---|
| The structural three-leg graph (AST + registry + event-log) | SEM-6's own headline: the structural detector "is **not** the swarm" — it's parse/registry/log machinery. It's the *side-input* the coherence-scan reduce reads (§2.2), not a map config. | [OBS-SEM6 §2.0], Coherence §3 |
| The own/reflect disposition store (the micro-ADR lane) | The one genuinely net-new persisted thing; un-recomputable by definition (the map can't produce a human decision). It's a reduce side-input, not a chain output. | Coherence §2 |
| The loop front-half + safety (RETRY_CAP, burn-down governor, idempotent originator, detector-re-run closure) | The chain *produces findings*; the loop *acts on them*. Acting is the wire (`surface_intent_at`), not the corpus-chain. | Coherence §4 |
| The calibration harness (precision/recall per check-class on the system's own incidents) | Measures whether a chain's findings are trustworthy; it's a *consumer* of chain output, scored against ground truth. | Semantic §8 |

So the accurate statement: **three rounds become one engine + four orthogonal pieces that compose with it.** The
primitive is the keystone for the LLM-read faculties; the structural graph, the disposition store, the loop, and the
calibration harness are the load-bearing-but-separate walls it ties together. Building the primitive *first* is still
the right reordering — it's the shared substrate — but it does **not** make the other work disappear.

### 4.3 The model registry feeds the tiers — worker yes, synth NOT yet (the binding gap)

[OBS] The **worker** tier is registry-fed: `SlotBudget.from_registry(service_id="chat-4b")` reads `ops/services.json`
(cognition.py:404-450), computes the concurrency knee from the live `max_num_seqs`/`gpu_util` — never a hardcoded 32
(cognition.py:417 fails loud rather than assume). The local 4B is a resident GPU service the registry knows.

[OBS] The **synth** tier is **not** registry-fed today. `resolve_binding` (roles.py:251) resolves a role's model via the
capability query `role.requires ⊆ provider.provides` — but its docstring says "**TODAY the Company's only live provider
is the resident model read from ops/services.json**" and "**G8 DEPENDENCY (downstream — flagged): when G8/L-model ships
the real capability catalog, the caller passes the FULL provider set here**" (roles.py:265, 282 [OBS]). Cloud Opus is
not a GPU-resident service; it has no row in `services.json`.

**What-needs-building at this seam:** the **G8 capability catalog** — a provider registry that includes cloud models
(Opus, Ollama-Cloud) with declared `provides` capabilities, so a chain's `synth_model` can be *bound by capability
query* the same way a role's worker is, instead of hardcoded. Until then the synth tier is a hardcoded base_url/model
in the chain config (acceptable v1, but it's the gap, not the design). The `transport.openai_transport` is already
repointable by `base_url` ([OBS transport.py:53-59]) — so the *transport* spans cloud fine; what's missing is the
*registry entry* that lets the chain *select* the synth tier declaratively. [INF]

### 4.4 The CLI gets the verbs — concrete slots in `app.py`

[OBS] `ops/cli/app.py:main()` is a flat `if cmd == ...` dispatch chain (app.py:120-213). Every verb is one branch +
one docstring line. There is no `onboard`/`ask`/`research`/`coherence` verb today (confirmed: the branch list is
help/status/gpu/health/suites/models/telemetry/combos/config/swap/bench/up/down/restart/logs). The `company suites`
branch (app.py:133-149) is the **exact template** for "a verb that shells a heavy job under a temp store + propagates
exit code" — SEM-5 §1 mapped this in full.

**What-needs-building (the verbs, as chain-runners):**
- `company research <dir> "<intent>"` — compile-or-run a research chain (the wave, productized).
- `company ask <dir> "<query>"` — repo-QA: compile(Q) → map → reduce, ↺ followup.
- `company onboard` — run the saved onboard chain (SEM-5 §2: emit-not-own, the institutional-memory faculty).
- `company coherence scan [--semantic] [--enrich]` — run the coherence-scan chain (the round-2 face).

Each is a thin `if cmd == "...":` branch shelling a small driver that loads the named `chains/<name>.py`, runs it via
the corpus-chain runner, and prints/propagates. The CLI is a **face over the runner**, not logic — exactly the
`company suites` shape. [IDEA, grounded in the suites precedent]

### 4.5 The coherence substrate consumes its output

[INF] A chain run *grounds a thing before it becomes a finding-to-build*. The `emit` parameter of `run_swarm` is
already the seam (`emit("cognition.wave", {...})`, cognition.py:602-611 [OBS]) — a coherence-scan chain's findings flow
through `emit` into the coherence finding-event log (Coherence §6 LIFE 1: an addressed event on the append-only log).
**What-needs-building:** the finding-emission adapter (chain output → `kind="coherence.finding"` events on existing
addresses) — but Coherence §8 already sequences this; it's the consumer's lane, and `emit` is the ready seam.

### 4.6 The RHM up_translate could be fed by it — and the hook is ALREADY WRITTEN

[OBS — the strongest connection finding] `up_translate(kind, ref)` (suite.py:5856) already declares
`UPTRANSLATE_KINDS = ("address", "decision", "finding", "event")` (suite.py:5854) — **"finding" is already a registered
kind**, with the docstring noting `ref` is "a finding dict for 'finding'". The Coherence round found this half-built
and "explicitly waiting" (Coherence §1.3, §6). So the corpus-chain's reduce output (a finding) feeds *directly* into an
organ that already accepts it. SEM-5 §5.1 went further: the `--enrich` pass is *the swarm doing `up_translate` in bulk
ahead of time* — pre-generating each finding's Tim-altitude framing so `CoherenceView` opens populated.

**What-needs-building:** wire the `finding` branch of `up_translate` to a chain run (a fresh repo-QA/coherence-scan over
the finding's address grounds the RHM's answer). The kind is declared; the organ exists; the seam is "call a chain when
up_translate('finding') needs grounding." [INF — the kind enumeration + the docstring are OBS; the wiring is the build.]

### 4.7 Self-hosting — institutional-memory-as-a-verb

[INF] A Company faculty that generates grounded whole-corpus understanding on demand IS the institutional-memory-that-
replaces-the-developer (the no-devs / self-hosting-spine law, project memory). `company onboard` is the on-demand face
(SEM-6 §2.7: cheap enough per session start, no daemon); the continuous background watch is the always-on face Tim must
separately authorize (the `background` activation context exists, "ready-but-driver-gated", [OBS-SEM6 §2.1
activation.py:77-85]). **What-needs-building:** nothing net-new for on-demand (it's a verb over the runner); the
continuous watch is a needs-tim driver decision, not a build gap.

### 4.8 The projection-sibling pattern — how the view binds (the connection to the surface)

[OBS] `contracts/cognition_info.py` is `build_cognition_info`, the **sibling of `build_object_info`** (the docstring
says so verbatim): it serializes the cognition registries → the FE, "generated from the registries — never
hand-written," and "add a role file → it self-registers → `/cognition_info` gains an entry → the FE re-merges → it
appears live, no FE code." A `chains/*.py` registry would get the **same treatment**: a `build_chain_info` sibling
serializing the chain library → a CLI/surface that lists/runs chains with no per-chain code. [IDEA, grounded in the
existing sibling pattern.] This is how the faces become *visible and runnable from the surface* the same way node-types
are visible on the canvas.

---

## 5 · The connection map, as one picture

```
                         FREEFORM INTENT                          SAVED chains/*.py (the library)
                               │                                   research · coherence-scan · onboard ·
                               ▼                                    repo-QA · doc-staleness
                      ┌──────────────────┐                                  │
                      │  COMPILE (synth) │  ── emits a valid CHAIN ────────►├─ (Area-3 owns compile trust)
                      └──────────────────┘                                  │
                                                                            ▼
   model registry ──► WORKER tier (4B, services.json) ──┐         ┌──────────────────────────────┐
   [OBS resident]                                        ├────────►│  run_swarm  (the MAP engine)  │  ◄── §4.1 net-new:
   [GAP §4.3 synth ► G8 catalog]                         │         │  per-unit structured digest   │      input_addresses
                                                         │         └──────────────────────────────┘      → active ctx→msgs
                                                         │                        │ digest
                                                         │                        ▼
   structural graph (AST+reg+log) ──┐                    │         ┌──────────────────────────────┐
   owned dispositions (ADR lane) ───┼── reduce_inputs ──►│────────►│  REDUCE (synth, run_jury slot)│  §2.2 ESCAPE HATCH:
   the question (repo-QA) ──────────┘  (§2.2 schema-ext) │         │  join · adjudicate · compose  │      reduce_inputs[]
                                                         │         │  ↺ decide-next                 │
                                                         │         └──────────────────────────────┘
                                                         │                        │ findings/answer/orientation
                                                         │            emit ────────┼─────────────────────────────►
                                                         ▼                         ▼
                            CLI verbs (app.py §4.4)      coherence finding-log (§4.5)   up_translate('finding') (§4.6, kind
                            company research/ask/onboard  → loop front-half (orthogonal,   ALREADY declared) → RHM / CoherenceView
                            /coherence                     §4.2 does NOT collapse)         via build_chain_info sibling (§4.8)
```

The two leaks are drawn where they bite: `reduce_inputs` (the side-input escape hatch) feeding the reduce from the
left; the worker/synth tiers split with the synth-binding gap flagged. research-wave's cost-inversion isn't a box —
it's the property that the worker tier can be *strong* and the reduce input *large*, which is why the runner must be
tier-agnostic (§2.1).

---

## 6 · What-needs-building, gathered (the punch-list this lane produces)

Ordered by load-bearing-ness, each tied to its seam above:

1. **Activate `input_addresses` → a declared ctx→messages mapping in `run_role`** (§4.1). The one net-new engine seam;
   without it no map reads a file. Touches shared `run_role`; stays behind schema-validate/fail-loud. [OBS the field
   exists, descriptive-only; the activation is the build]
2. **Add `reduce_inputs` (declared side-inputs) to the `Chain` schema** (§2.2). Without it the highest-value face (the
   wired∧meaningless join) and onboard (digest ⨝ dispositions) and repo-QA (the question) cannot be expressed as
   chains. Small schema-extension; rides existing addressing. [IDEA, forced by the leaks]
3. **The `chains/` registry + `build_chain_info` sibling** (§3.1, §4.8) — self-registering chain files discovered like
   `roles/*.py`, serialized like `cognition_info.py`. Reuses the existing registry machinery; not a fork. [IDEA,
   grounded in the role/node precedent]
4. **The chain runner** — executes any valid `CHAIN` (compiled/saved/hand-written, byte-identical kinds) via
   `run_swarm` (map) + a synth reduce + `run_jury` (adjudicate) + the decide-next loop. Tolerates **strong workers AND
   large reduce-inputs** (the research-wave-forced tier-agnosticism, §2.1). [IDEA]
5. **The G8 capability catalog for the synth tier** (§4.3) — so `synth_model` is bound by capability query, not
   hardcoded. v1 can hardcode the cloud base_url (the transport already spans cloud); this is the proper-binding gap.
   [OBS the gap at roles.py:265; the catalog is the build]
6. **The CLI verbs** `company research/ask/onboard/coherence` as thin runners over the chain library (§4.4) — the
   `company suites` shape exactly. [IDEA, grounded in the suites precedent]
7. **The finding-emission adapter** (chain output → coherence finding-events via the ready `emit` seam, §4.5) and the
   **`up_translate('finding')` wiring** (the kind is already declared, §4.6). [OBS the seams; the wiring is the build]
8. **Hierarchical staging in the reduce** (anchor §7.3) — made *more* pressing by §2.2 (the reduce input is now
   `digest + Σ side-inputs`, which overflows the synth context sooner). The reduce must reduce-clusters-then-reduce-
   summaries without losing the cross-unit join. [INF, the leaks sharpen the anchor's own hard part]

Explicitly **out of this lane** (owned elsewhere, do not re-derive): compiler reliability (Area-3, anchor §7.1); the
structural three-leg graph (Coherence §3); the disposition store + loop safety (Coherence §2/§4); the calibration
harness (Semantic §8). These **compose with** the punch-list above; they are not subsumed by it (§4.2).

---

## 7 · The honest "but actually" list (where I corrected/sharpened the anchor)

- **"build the ONE primitive and the four faces are all just configs of it" (§0)** → *actually* **the topology
  generalizes, but the cost-shape does not.** research-wave inverts both halves of the economic argument (expensive
  workers AND large reduce-input), and it's the config the anchor used to generate itself (§2.1). The "cheap layer
  touches every byte, smart layer reads small things" is a **saved-chain property, not a primitive invariant.**
- **"REDUCE reads the structured digest (not the raw corpus)" (§0 line 41, §2)** → *actually* **the reduce frequently
  needs a declared side-input the map never produced** — the structural graph (the wired∧meaningless prize), the owned
  dispositions (onboard), the question (repo-QA). The schema needs `reduce_inputs` (§2.2). The clean digest-only model
  is too tidy.
- **"building this first collapses three roadmap items into one" (§9)** → *actually* it collapses the **LLM-read half**
  of three roadmaps into one engine, but **does NOT subsume** the structural graph, the disposition store, the loop +
  safety, or the calibration harness — those stay orthogonal (§4.2). Three rounds → **one engine + four orthogonal
  pieces.** A total-collapse claim would contradict the prior rounds, which name those four as separately load-bearing.
- **"the model registry feeds the configurable tiers" (§6)** → *actually* it feeds the **worker** tier (resident 4B,
  `SlotBudget.from_registry`) but **not the synth** tier (cloud Opus has no `services.json` row; `resolve_binding` is
  "resident-only today", roles.py:265). The synth tier needs the **G8 capability catalog that doesn't exist yet**
  (§4.3).
- **"saved chains a la roles/node-types" (§3)** → *confirmed and stronger:* it's the **third instance** of the system's
  self-registering-file law, and `roles/check.py` is *already* a one-unit semantic detector in the shape (§3.1). Not
  new architecture — the same registry machinery, a `chains/*.py` member.
- **"the reduce feeds the RHM" (§9 open what-if)** → *actually* the hook is **already written**:
  `UPTRANSLATE_KINDS` already includes `"finding"` (suite.py:5854 [OBS]); the organ accepts a finding dict today (§4.6).
  The connection is nearer than the anchor's "what-if" tone suggests.

---

*Left bigger and more real than I found it: the five faces are now a concrete field-by-field config table with a
leak column; the anchor's cost-shape elegance is downgraded from a primitive-invariant to a saved-chain property
(research-wave inverts it, and we're living that inversion); the one real schema-extension (`reduce_inputs` side-inputs)
is isolated against the highest-value face that needs it; the roadmap-collapse is made PARTIAL with the exact four
orthogonal pieces named; the synth-tier binding gap is grounded at roles.py:265; the `up_translate('finding')` kind is
confirmed already-declared (suite.py:5854); and an 8-item what-needs-building punch-list is tied seam-by-seam to the
real code, with the out-of-lane pieces named so the synthesis doesn't double-count them.*
