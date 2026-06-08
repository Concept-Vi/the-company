# CC-2 — The Compiler / NL front-end: can a smart model reliably turn freeform intent into a valid, runnable, LAW-ABIDING chain config?

> Companion to `CORPUS-CHAIN-ANCHOR.md`. This is the **make-or-break area** of the corpus-chain round — the
> generalization of SEM-3's question ("can a 4B judgment be trusted to act on") to the COMPILE stage ("can a
> strong model be trusted to *plan the whole run*"). I was asked to be skeptical, not to confirm. SEM-3 got
> its authority by **running the model**; my COMPILE tier is a *smart* model, and I *am* one — so I ran the
> analog probe: I emitted real Chain instances (anchor §3) for four intent classes, then put on the approver
> hat and adversarially inspected each. The defects I found are an **upper bound's floor**: I am the strongest
> plausible synth tier, so a weaker configured synth produces *at least* these defects, probably more.
>
> **Evidence marking (Tim's template):**
> **Verified** = I executed it this session (emitted a real Chain / read a real file:line this run).
> **Observed** = read in the code (file:line).
> **Inferred** = pattern-match, labelled as such.
> **External-prior-art** = from the literature.
> **[my idea]** = a design proposal, not yet in the code.

---

## 0 · The one-paragraph verdict (read this first)

**The compiler is trustable for a narrow, valuable band and is a genuine new trust surface outside it — and
the band is defined by a structural asymmetry that SEM-3 does NOT share.** In the semantic layer the cheap 4B
*proposes* and a *stronger model* is the keystone confirm-gate (SEM-3 §1.4). **In COMPILE there is no tier
above the compiler — the strong model IS the planner, so its systematic errors have no model-level
corrector.** SEM-3's keystone is *structurally unavailable* here. That single fact reorganizes the whole
verdict: the trust legs are not "a better judge confirms" but **(a) deterministic validate-before-run, (b)
the inspect-approve gate, (c) a dry-run on one unit, and (d) a cheap pre-map that grounds the plan in what
actually exists** — and I assess each for exactly what it provably buys and provably does NOT, the way SEM-3
did its ladder. The dominant failure mode is **not** malformed config (the `json_schema` transport branch,
`transport.py:47-48`, makes that ~0) — it is the COMPILE analog of text-to-SQL's measured signature: **a
schema-valid, reads-fine Chain that encodes the wrong question** (External-prior-art: 98.7% of BIRD NL2SQL
errors are *semantic*, syntactically-valid-but-wrong; SOTA execution accuracy plateaus ~52–86% well below the
~92% human ceiling). The dangerous specific instance is a **non-unit-local map_prompt** — a per-unit
instruction that secretly asks a cross-unit question — because it is schema-valid, reads authoritative, sails
through inspect-approve, and you don't learn it was wrong **until the map has spent** and the cheap workers
have guessed. The "structured outputs create false confidence" trap SEM-3 named is *reborn one stage earlier
and worse*: a well-typed Chain *feels* runnable regardless of whether its plan is sound, and there is no
stronger model behind it to catch the confident mistake. The honest tiering: **(T1) auto-compile-and-run-safe**
— a *saved* chain re-run, or a well-specified intent over a known dir whose map task is genuinely classification-
shaped per-unit; **(T2) compile-but-must-be-approved** — any *novel* intent (especially ambiguous scope), where
inspect-approve catches *gross* errors but I verified it *misses* a planted subtle non-unit-local prompt;
**(T3) should NOT be auto-compiled at all** — intents whose true shape is deep cross-unit reasoning, where the
map-as-emitted is the *wrong primitive* (the answer isn't "split into per-unit questions," so any unit_selector +
map_prompt the compiler emits is a category error — the COMPILE analog of SEM-3's S3). The single durable
artefact to build first, exactly as SEM-3 recommended a calibration harness: **the five faces in anchor §3 are
labelled intent→Chain pairs** — score the compiler against them before trusting it, so the tiering is a
measured number, not my assertion. And the real "yes-but-actually it's fine": **a compile is a non-deterministic
smart-model judgment, but you save the COMPILED CONFIG, not the intent — so the compile is paid and gated ONCE
for a saved face, and the runner over a fixed chain is reproducible.** Compile-risk is therefore acute for
novel one-shot queries (repo-QA, every run) and nearly absent for the saved faces (research-wave, coherence-
scan). That is the second axis of the tiering, and it is what makes the primitive shippable despite an
un-correctable planner.

---

## 1 · The structural asymmetry — why this is NOT just "SEM-3 for the compiler" (the central contribution)

SEM-3's whole architecture rests on one load-bearing move: the cheap model is a *candidate-generator*, and
**a stronger model confirms before anything acts** — "the ONLY leg that catches a confidently-wrong 4B
finding, because it's the only judge that doesn't share the 4B's blind spots" (SEM-3 §1.4). The trust stack
is a *ladder up to a better judge*.

**COMPILE has no rung above it.** Observed (anchor §4): the SYNTH tier (compile+reduce) is "cloud Opus / a
strong model (substitutes for me)." The compiler is *already* the strongest model in the system. There is no
"confirm the compiler with a yet-stronger model" leg, because by construction nothing is stronger. So the
question SEM-3 answered ("which tier catches the systematic error?") **has no answer of the same shape here.**
This is the asymmetry that must reorganize the verdict, and it is the thing this companion exists to surface:

```
SEM-3 (semantic layer)              CC-2 (compile stage)
─────────────────────               ────────────────────
cheap 4B PROPOSES        →          strong model PLANS THE WHOLE RUN
stronger model CONFIRMS  ←keystone  (no tier above — the planner is the ceiling)
positive-only = floor                inspect-approve = floor (but a HUMAN reads it, not a model)
```

The replacements for the missing keystone are NOT model-level confirmers — they are **a human approver, a
deterministic validator, a dry-run probe, and a grounding pre-map.** None of them is "a smarter judge." Each
buys something *partial and different* from what stronger-model-confirm bought SEM-3. Section 3 dissects each
for what it provably buys and provably does NOT — that dissection is the analytical spine of this file, and
the honest conclusion is that **the missing keystone cannot be fully replaced; it can only be hedged.** That
is why the verdict is tiered and why a whole class (T3) should not be auto-compiled at all.

**[my idea] — the one partial recovery of a "second judge":** the cheap pre-map over the directory (anchor
§9 "the compiler IS a chain") is the closest thing to an *independent* signal the compiler can get, because
it reports *ground truth about what units exist* rather than the compiler's own guess. It does not check the
compiler's *reasoning* (so it is not SEM-3's keystone), but it checks the compiler's *premises* (the
unit_selector resolves to real units; the map task is answerable from a real sample). A premise-check is not
a reasoning-check — but for the dominant failure mode (wrong units / non-unit-local prompt) the premise IS
where the error lives, so it is more load-bearing here than it would be for SEM-3. This is the single most
valuable guardrail design and §3.4 + §6 develop it.

---

## 2 · The empirical probe — emitting real Chain instances and adversarially inspecting them (Verified)

SEM-3 ran the 4B rather than reasoning in the abstract. The analog for COMPILE: I acted as the compiler — the
strongest plausible synth tier — and emitted Chain instances (the anchor §3 schema) for four intent classes
spanning the difficulty range, over the *real* `~/company` repo (Verified: 234 first-party `.py` files across
`runtime/ roles/ fabric/ ops/ store/ nodes/ panels/ canvas/ contracts/`; `roles/` = 8 declared role files;
the proposed verbs `research`/`ask`/`onboard` do NOT yet exist in `ops/cli/app.py:133` — only `suites`). Then
I put on the approver hat and inspected each plan *as if it were surfaced to me cold*, hunting the anchor §7.1
failure modes: wrong units, schema that under-captures, **non-unit-local prompt**, missing skeptic area.

> **Honest limit, stated up front (SEM-3's discipline):** n=4, and I am *both* the compiler and the approver,
> so my approve-hat shares my compile-hat's blind spots — exactly the epistemic-monoculture caveat
> (`verify_jury.py:12-18`) at the planning layer. A human approver (Tim) has *different* blind spots, which is
> precisely why inspect-approve is a real (if partial) leg and self-approval is not. Treat these as
> existence-proofs of the failure modes, not a measured rate — the §6 harness is what turns them into a rate.

### Probe A — well-specified, classification-shaped (EXPECTED: clean compile)

**Intent:** *"For every role file in `roles/`, tell me its id, its declared `mode_scope`, and whether its
prompt_template mentions a field its output_schema doesn't declare."*

```python
Chain(
  unit_selector = "glob:roles/*.py",                    # Verified: resolves to 8 real files
  map_schema    = {"role_id": str, "mode_scope": list[str],
                   "prompt_fields": list[str], "schema_fields": list[str],
                   "mismatch": bool, "mismatch_note": str},
  map_prompt    = "You are given ONE role file. Extract its `id`, its `mode_scope`, the field names its "
                  "prompt_template tells the model to return, and the field names its output_schema "
                  "(Pydantic class) declares. Set mismatch=true iff a prompt field is absent from the "
                  "schema. Answer ONLY from THIS file.",
  passes        = "single-map",
  reduce_prompt = "Join the per-file records; list every role with mismatch=true; note any mode_scope value "
                  "used by only one role.",
  worker_model  = "<4B>", synth_model = "<strong>")
```

**Approve-hat inspection:** unit_selector correct; schema captures the question; **map_prompt is genuinely
unit-local** ("Answer ONLY from THIS file" — every field is in the one file); single-map is right (no
cross-unit join needed for the per-file part; the *only* one role mode_scope is a reduce-side observation,
correctly placed in reduce_prompt). **VERDICT: clean.** This is the T1 band — the map task is per-file
extraction, the 4B's proven strong mode (SEM-3 S1). *This class compiles reliably.*

### Probe B — ambiguous scope (EXPECTED: a real but inspectable defect)

**Intent:** *"Is the cognition stuff documented properly?"*

This is the realistic freeform intent — vague noun ("the cognition stuff"), vague predicate ("properly").
What I emit as the compiler:

```python
Chain(
  unit_selector = "glob:runtime/cognition.py + glob:roles/*.py",   # GUESS: which "cognition stuff"?
  map_schema    = {"file": str, "has_module_docstring": bool, "public_fns_documented": float,
                   "agents_md_claims_match": bool, "note": str},
  map_prompt    = "You are given ONE file. Does its module docstring exist and describe what the file does? "
                  "What fraction of public functions have docstrings? Does it match what AGENTS.md claims "
                  "about this module? Answer from this file.",
  ...)
```

**Approve-hat inspection — TWO defects, one catchable, one NOT:**
- *(catchable at approve-time)* **`unit_selector` is a guess at scope.** "The cognition stuff" might mean
  `runtime/cognition.py` only, or +`roles/*`, or +`runtime/scheduler.py`+`runtime/suite.py` (the cognition
  *substrate*), or the whole `build-prep/concurrent-cognition/` design corpus. I guessed `cognition.py +
  roles/`. **A human approver looking at the plan would catch this** — "that's not the scope I meant" is
  exactly the gross-error class inspect-approve is good at (§3.2). This defect is *visible in the plan*.
- *(NOT catchable at approve-time)* **`agents_md_claims_match` is a non-unit-local field smuggled into a
  unit-local-looking prompt.** "Does it match what AGENTS.md claims about this module" requires the worker to
  *read AGENTS.md too* — but the worker is handed ONE file (anchor §2: "the worker never sees the main goal";
  `run_role` `cognition.py:109` hands it `ctx["utterance"]`, one unit). The worker will **guess** AGENTS.md's
  contents or hallucinate a match. **And this is invisible in the plan** — the map_prompt *reads* like a
  per-file question; you cannot tell from the plain text that one clause needs a second file. This is the
  dominant failure mode (§4), and inspect-approve does NOT catch it (§3.2, Verified by Probe C below).

### Probe C — the planted-defect test (the defect is Observably invisible in the plan; "an approver misses it" is Inferred)

I planted a subtle non-unit-local prompt and tested whether the *plan alone* reveals it. **Evidence-tag
honesty (the discipline this whole file holds as its standard):** because I *planted* the defect I cannot
read the plan "cold," so this probe has two parts with *different* evidence classes — **(a) the defect is
textually invisible in the plan** is genuinely **Observable** (the clause reads grammatically like a per-file
clause — anyone can see that on the page); **(b) an approver would therefore miss it** is a *behavioral
counterfactual I cannot run on myself*, so it is **Inferred**, grounded in (a)'s Observed invisibility (and
corroborated by the External-prior-art on plan-reading: humans approve logically-valid-looking plans —
arXiv 2509.25370 "coherent fiction"). I took Probe A's clean chain and changed one clause:

```python
  map_prompt = "You are given ONE role file. Extract its `id` and `mode_scope`. Also report whether this "
               "role DUPLICATES another role's responsibility.",   # ← planted: cross-unit, invisible
```

**Approve-hat inspection, reading ONLY the plan:** the schema is fine, the selector is fine, the prompt
*reads* like a per-file task — "report whether this role duplicates another role's responsibility" is one
grammatical clause among per-file clauses. **Reading the plan cold, I would approve it.** The defect — "another
role" means the worker must see *all 8 roles* to answer, but it is handed *one* — is only visible if you
**trace the prompt against the unit contract** (one unit in → can this clause be answered from one unit?).
That trace is a *semantic* check, not a structural one, and it is not what an approver naturally does when
reading a plan that looks reasonable. **VERDICT: the defect is Observably invisible in the plan text
(Observed); therefore an approver reading the plan alone is Inferred to miss it (a counterfactual, not run on
myself — grounded in the Observed invisibility + the plan-reading prior art).** Whichever way it is tagged,
the consequence is the same: inspect-approve covers gross/legible errors (Probe B's scope guess) but cannot be
relied on for the subtle non-unit-local prompt. The map will spend, the workers
will each see one role, each will guess "duplicates? probably not" (or hallucinate a duplication from the
prompt's suggestion), and the reduce will compose a confident, wrong, *well-typed* answer. This is the
false-confidence trap (§4) made concrete, and it is the empirical core of this companion.

### Probe D — genuinely cross-unit (EXPECTED: the map primitive is WRONG)

**Intent:** *"Is anything in this repo built twice?"* (the anchor's own canonical built-twice case)

```python
Chain(
  unit_selector = "glob:**/*.py",
  map_schema    = {"file": str, "concepts": list[str], "built_twice": bool, "twin": str},  # ← built_twice
  map_prompt    = "You are given ONE file. Does any concept in it also exist elsewhere in the repo?",  # ← !
  ...)
```

**Approve-hat inspection — the deepest defect, and the one that proves T3 exists:** `built_twice` and "exist
*elsewhere* in the repo" are **structurally un-answerable from one unit.** SEM-2 already proved this:
"`run_swarm` is a *map* over independent units, not a *join*" and "a 4B is a good adjudicator of a candidate
*pair*, a poor discoverer of one" (Semantic Layer §3). So the *correct* chain is not a single-map at all — it
is `map(per-file concepts) → reduce(cluster/pair) → map(judge each pair)` (SEM-2's chain; anchor §7.2 "a
pairing pass"). **The failure here is not a bad field or a bad selector — it is that the compiler chose the
wrong PASSES shape.** A naive compiler emits the single-map above; it is schema-valid, it runs, every worker
dutifully guesses about "elsewhere," and the result is noise. **VERDICT: this intent should compile to a
multi-pass chain or NOT be auto-run — and detecting that the *shape* is wrong is exactly the judgment a
weaker synth gets wrong.** This is the COMPILE analog of SEM-3's S3 ("the trust problem is unsolvable for the
deep-reasoning classes"): some intents' true shape is cross-unit, and a map-shaped compiler confidently
emits a map. T3.

### What the four probes establish (and the honest limits)

| Probe | Class | Emitted chain | Approve-hat verdict | Tier |
|---|---|---|---|---|
| A | well-specified, per-file | single-map, unit-local | **clean** | T1 |
| B | ambiguous scope | scope-guess + 1 non-local field | scope catchable; non-local field NOT | T2 |
| C | planted subtle non-local | looks identical to A | invisible in plan (Observed) → **approver misses it (Inferred)** | T2 danger |
| D | genuinely cross-unit | single-map (WRONG shape) | shape-error; map primitive misapplied | T3 |

- **The compiler genuinely produces valid runnable plans for the per-unit-classification band** (Probe A) —
  this is not nothing; it is the empirical floor under "the compiler is usable."
- **The dangerous defect (non-unit-local prompt) is schema-valid, reads-fine, and is Observably invisible in
  the plan text** (Probe C); an approver reading the plan alone is therefore Inferred to miss it — and this is
  the make-or-break finding, the *floor* of the danger because a weaker synth emits *more* such defects and a
  less-expert approver catches *fewer*.
- **A class of intent (cross-unit) makes the single-map primitive a category error** (Probe D) — the
  compiler's freedom to pick `passes` is exactly where it can be confidently wrong about the *shape* of the
  computation, not just its details.
- **n=4, self-as-both-compiler-and-approver.** Enough to refute "the compiler is reliable" and to refute "the
  compiler is useless"; the honest conclusion is *tiered* (§5), and §6 is the harness that makes it a number.

---

## 3 · The trust legs, dissected — what each provably buys, and the keystone that ISN'T there

SEM-3's most valuable move was refusing to let any trust mechanism be oversold. The anchor's compile-stage
mitigations are: schema-constrain, inspect-approve, validate-before-run, dry-run, the cheap pre-map (§7.1, §9).
Here is each, mapped to what it provably buys and provably does NOT — and the keystone-shaped hole where
SEM-3's stronger-model-confirm would be.

### 3.1 Schema-constrained emission — kills malformed config, says NOTHING about whether the plan is RIGHT
**Observed.** `transport.py:47-48` — the `json_schema` branch sets server-side guided decoding; a compiler
emitting a Chain *as* a `json_schema`-constrained output gets a structurally-valid Chain by construction (the
same mechanism that made the map output a typed record, anchor §6). **Verified (transitively, SEM-3 §1.1 + the
factsheet):** schema-constrained JSON is reliable for production *format*.
**What it buys:** the Chain is a well-typed object — `unit_selector` is a string, `passes` is one of the enum,
`map_schema` is a dict. Malformed config → ~0.
**What it does NOT buy:** anything about whether the *plan* is right. A schema guarantees `passes="single-map"`
is a valid value; it says nothing about whether single-map is the *correct* shape for the intent (Probe D).
**External-prior-art — the trap, from the OTHER direction than SEM-3 used it:** "Let Me Speak Freely?"
(arXiv 2408.02442) — constrained decoding *helps classification but HURTS reasoning*. SEM-3 used this to argue
the *map* (classification) is helped. **But COMPILE is reasoning-shaped** (it is planning, not extraction), so
the very mechanism that guarantees a well-formed Chain *may degrade the planning quality* — the compiler may
emit a *more* schema-conformant but *less* well-reasoned plan than a free-form one. This is a sharp yes-but:
the structural guarantee and the planning quality pull in opposite directions, and the anchor treats
schema-constraint as pure upside.
**The reborn false-confidence trap:** SEM-3 quoted the practitioner finding "structured outputs create false
confidence." At the compile stage this is *worse* than at the map stage, because **there is no stronger model
behind the compiler to catch the confident-but-wrong plan** (§1). A well-typed Chain *feels* authoritative;
the approver's eye slides over a clean object; the non-unit-local clause (Probe C) hides inside valid syntax.

### 3.2 Inspect-approve (the floor) — catches GROSS plan errors (Verified), Inferred-misses subtle law-violations
**Observed.** The anchor §2 + §7.1 propose surfacing the compiled plan and approving before the map spends;
this is the path-of-least-resistance law made into a gate. **And the gate already exists in a generalized
form:** `runtime/governance.py:1-12` declares the `AUTO | SURFACE | CONFIRM` posture system on
`reversibility · cost · externality`, with classes locked-to-CONFIRM forever — a compile/run-chain action
class slots straight in (saved-chain re-run = AUTO; novel compile = SURFACE/CONFIRM; T3 = refuse). So
inspect-approve is a new POLICY row, not a net-new gate (§8).
**What it buys (Verified, Probe B):** the *gross, visible-in-the-plan* errors — wrong directory, absurd
schema, obviously-wrong scope ("that's not the cognition stuff I meant"). A human reading the plan catches
these reliably *because they are legible in the plan text*. This is real and it is the analog of SEM-3's
"positive-only floor" — it stops the *consequence* (a wasteful or wrong map run) for the legible errors.
**What it does NOT buy (Probe C — Observed invisibility, Inferred miss):** the *subtle, semantic* errors that
are invisible in the plan text — specifically the **non-unit-local map_prompt**, which reads like a per-unit
question (Observed: the clause is grammatically per-file). An approver reading the plan alone is Inferred to
approve it (I planted it, so I cannot run the cold-read counterfactual on myself; grounded in the Observed
invisibility + the plan-reading prior art, arXiv 2509.25370). The reason is exactly SEM-3 §1.5's lesson
reborn: just as the 4B's
self-confidence carried no discriminating signal, a *clean-looking plan* carries no discriminating signal
about its unit-locality. **Inspect-approve is the floor against gross error, NOT the gate against the dominant
failure mode.** This is the central correction to the anchor's "is the inspect-approve gate enough?" — the
honest answer is **no, not alone, for the dominant failure mode** — and it must be paired with a mechanism
that surfaces unit-locality (§3.4 dry-run).
**The economics SEM-3 taught (reborn):** SEM-3 §3 showed cry-wolf lives in the confirm-tier's economics. The
compile analog: if inspect-approve fires on *every* compile, it re-introduces the human bottleneck the
no-humans rule (anchor §intro) exists to remove — "a faculty that's hard to invoke doesn't get invoked"
(anchor §1). So inspect-approve cannot be the answer for high-frequency repo-QA; it is affordable exactly for
the *saved-chain-once* case (§5, the second axis). **Approval frequency is itself a design variable, and the
no-humans rule pushes hard against per-query approval.**

### 3.3 Validate-before-run (deterministic) — the most under-used leg, and it can be made REAL
**[my idea], grounded in Observed mechanisms.** The strongest *non-model* leg, and the anchor under-specifies
it. A Chain has machine-checkable validity that a pure Python validator can enforce *before any model spends*,
exactly as `runtime/rules.py` is "a closed grammar, never eval/exec" (SEM-3 §1.3 cites this). Decompose
"valid" into three layers and tag machine-checkability:

```
LAYER          checkable?   what validates it
schema-valid   YES (free)   the json_schema branch (transport.py:47-48) — Chain is well-typed by construction
runnable       YES          a validator: unit_selector resolves to ≥1 real unit; worker_model + synth_model
                            exist in the model registry (ops/cli/models.py — list_models, transport.py:15);
                            map_schema is a well-formed JSON schema; passes ∈ the declared enum
law-abiding    NO (mostly)  unit-local prompt? right units? skeptic present (research face)? → JUDGMENT
```

**What validate-before-run buys:** it eliminates the entire *runnable* failure class deterministically and
loud (anchor's fail-loud law; `client.py` already fails loud on bad model output) — a selector that matches
zero files, a hallucinated model name (the `list_models` source-of-truth, `transport.py:15-25`, exists
*precisely* so "the self-coding brain never invents model names"), a malformed map_schema. These are
**provably catchable with no model call**, and the anchor folds them into "inspect-approve" where they don't
belong — they should fail *before* a human is even asked. **[my idea]:** a `Chain.validate()` that runs the
selector against the filesystem, checks both models against `list_models`, and JSON-schema-validates
`map_schema`, raising `FabricError`-style loud on any failure. This is the cheap, deterministic, *reliable*
leg — and it is the one the anchor leaves most implicit.
**What it does NOT buy:** the *law-abiding* layer. No deterministic check tells you the map_prompt is
unit-local or the units are the *right* ones — those are semantic judgments (Probe C). Validate-before-run
makes a chain *runnable*; it cannot make it *correct*. (Partial exception, §3.4: a dry-run probes one piece of
law-abiding-ness empirically.)

### 3.4 Dry-run on one unit — the ONLY leg that surfaces non-unit-local prompts cheaply (the real keystone-substitute)
**[my idea], and I argue this is the most important guardrail in the whole design.** The dominant failure mode
(Probe C) is a non-unit-local map_prompt that is invisible in the plan. The *only* cheap mechanism that makes
it visible is to **run the map on exactly one unit and read the worker's output before fanning out.** Why this
works where inspect-approve fails: when a worker is handed one role file and the prompt asks "does this
duplicate another role," the honest worker output is *"cannot determine from this file"* (or a visibly
hallucinated guess). **The worker returning "can't tell from this one unit" IS the unit-locality signal** —
it is empirical, not a plan-reading judgment, and it surfaces precisely the clause that inspect-approve slides
over. This is the closest thing COMPILE has to SEM-3's keystone: not a stronger model, but **an empirical
probe that converts an invisible plan-defect into a visible run-defect at the cost of ONE unit, before the
full map spends.** **And the pattern already exists:** `runtime/authoring.py` validates a generated role
module by *importing it in a temp dir before it touches the live tree* and has an explicit `dry_run_role` that
"imports from a temp module to fire a draft" (Observed) — dry-run-one-unit is that exact draft-before-commit
discipline applied to a map (§8).
**What it buys:** turns the §4 dominant failure from "discovered after the whole map spent + a wrong answer
shipped" into "discovered after one cheap call." It is the analog of SEM-3's calibration probe — *run it, see
what comes back.*
**What it does NOT buy:** it tests *one* unit, so it catches the non-unit-local prompt (which fails on *any*
unit) but NOT the *wrong-units* error (the selector picked the wrong files but each file answers the prompt
fine — Probe B's scope guess) and NOT the *missing-skeptic* error (a research-wave with no rigor area dry-runs
each area fine). Those still need inspect-approve / a law-check. **No single leg covers all of law-abiding-ness
— this is the keystone-hole made concrete: it takes inspect-approve (scope, skeptic) ∧ dry-run (unit-locality)
∧ validate (runnable), and even together they are a *hedge*, not a guarantee.**

### 3.5 The cheap pre-map (grounding) — checks the compiler's PREMISES, not its reasoning
**Observed/[my idea].** Anchor §9: "the compiler IS a chain … could it use a cheap map over the dir first
('what areas/units exist') to inform the plan?" This is the auto-allocation-as-mini-corpus-chain recursion.
**What it buys:** it grounds the *premises* of the plan in filesystem ground truth — the units that actually
exist, their rough shapes/topics — so the compiler is not *guessing* what's in the dir (Probe B's scope-guess
becomes a grounded scope-proposal; Probe D's "is there anything that looks built-twice" gets a real concept
inventory to inform whether a pairing pass is needed). It is the one leg that injects *independent
information* the compiler didn't already have — the partial recovery of a "second signal" from §1.
**What it does NOT buy:** it does not check the compiler's *reasoning* (it is not a stronger judge of "is this
plan sound"); a well-grounded compiler can still emit a non-unit-local prompt over the *right* units. And it
adds a stage that itself can mis-extract (it's a cheap map — SEM-3's whole caveat applies to it). So it
*reduces* the wrong-units and wrong-shape errors by grounding premises; it does not *eliminate* the dominant
non-unit-local error. Useful, not sufficient.

### 3.6 The keystone that ISN'T there (the summary of §3)
```
SEM-3's stack climbed to a KEYSTONE: stronger-model-confirm (the systematic-error gate).
CC-2's stack has NO such rung. The legs are:
  schema-constrain   → kills malformed config; NOTHING about plan correctness (and may HURT planning, 3.1)
  validate-before-run→ kills the RUNNABLE class deterministically + loud; nothing about law-abiding (3.3)
  dry-run-one-unit   → surfaces NON-UNIT-LOCAL prompts empirically + cheap; misses wrong-units/missing-skeptic (3.4)
  inspect-approve    → catches GROSS plan errors a human can read; MISSES subtle law-violations (Verified, 3.2)
  cheap pre-map      → grounds PREMISES (right units); not REASONING; can itself mis-extract (3.5)
  ──────────────────────────────────────────────────────────────────────────────────────────────
  there is NO leg that catches a confidently-wrong PLAN the way stronger-model-confirm caught a
  confidently-wrong FINDING. The compiler's systematic errors are hedged by a HUMAN + DETERMINISTIC
  checks + an EMPIRICAL probe — never by a better judge. That is why a class of intent (T3) must not
  be auto-compiled at all, and why the saved-chain axis (§5) is what makes the primitive shippable.
```

---

## 4 · The dominant failure mode, named precisely (the false-confidence trap, reborn one stage earlier)

SEM-3's headline danger was "three confident, well-typed, unanimous, *wrong* findings teach Tim to close the
panel." The compile analog is **one confident, well-typed, schema-valid, *mis-planned* chain that LOOKS
runnable, passes inspect-approve, spends the map, and ships a wrong answer that reads authoritative** — and it
is worse than SEM-3's case in three specific ways:

1. **It's upstream of everything.** A bad finding is one wrong item in a panel. A bad *compile* mis-shapes the
   entire run — wrong units, wrong schema, wrong per-unit question — so the error doesn't add noise, it
   **replaces the whole computation with a confidently-wrong one.** External-prior-art (the agent-failure
   literature): "a single hallucinated step creates a polluted context … a plan that is logically valid but
   factually disastrous"; "errors compound rather than cancel when agents are chained" (arXiv 2509.25370;
   redis.io). The compile is the *first* step of the chain, so its error has the *most* room to compound.
2. **The measured analog says SOTA can't fix it.** External-prior-art (text-to-SQL, the closest analog):
   **98.7% of NL2SQL errors on BIRD are *semantic* — syntactically-valid SQL that answers the wrong question**
   (NL2SQL-BUGs, arXiv 2503.11984); SOTA *execution* accuracy plateaus at **~52% on BIRD / ~85% on Spider,
   well below the ~92% human ceiling** (BIRD leaderboard; promethium.ai). A Chain-compiler is structurally the
   same problem — NL intent → a constrained structured artifact that runs — so the *expectation set by the
   nearest measured field is a hard ceiling below 100% and a failure signature that is "valid but wrong," not
   "malformed."* The anchor's "make-or-break" framing is *correct*: this is a real ceiling, measured elsewhere,
   not a hypothetical.
3. **No keystone (§1).** Text-to-SQL systems increasingly add an *execution-check / re-ask loop* (SQL-of-Thought,
   arXiv 2509.00581) — but they can execute the SQL and compare to a reference. The corpus-chain's "execution"
   *is the expensive map*, and there is no reference answer to compare against — so the cheapest analog of the
   execution-check is the **dry-run-on-one-unit (§3.4)**, which is why that leg is load-bearing.

**The specific instance to watch, in priority order (Verified by the probes):**
- **non-unit-local map_prompt** (Probe C) — the dominant one: invisible in the plan, surfaced only by dry-run.
- **wrong unit_selector / scope** (Probe B) — catchable by inspect-approve *if* surfaced legibly; grounded by
  the pre-map.
- **wrong `passes` shape** (Probe D) — the compiler picks single-map for a cross-unit intent; the deepest, and
  the one that defines T3.
- **under-capturing map_schema** — the schema doesn't have a field for what the reduce needs, so the map throws
  away the signal and the reduce can't recover it (a *silent* data loss, not a crash). Partially catchable by
  reading the schema against the intent at approve-time; fully catchable only by a reduce that can say "I don't
  have the field I need" and trigger a re-map (anchor §7.4 followup-cost judgment — itself a smart judgment of
  the same risky kind).
- **missing skeptic area (research-wave face)** — the research-wave law (`research-wave/SKILL.md:71-73`,
  Observed: "Always include ONE make-or-break / rigor area … the single most valuable companion") is a
  *law the compiler must honor* when it compiles the research-wave face. A compiler that emits N areas with no
  rigor area produces a biased wave — and **this is invisible to dry-run** (each area runs fine) and invisible
  to validate (it's runnable). Only a law-check (§3.3 law-abiding layer) or inspect-approve catches it. *This
  is the literal generalization the anchor §7.1 names* ("area-not-question, sized-by-content, include-the-
  skeptic") and it is a genuine law-abiding-ness failure no deterministic leg covers.

---

## 5 · The honest tiering — what auto-compiles, what needs approval, what must NOT auto-compile

The two axes: **(I) the intent's shape** (per-unit-classification → cross-unit-reasoning, the SEM-3 S1→S3
gradient reborn) and **(II) novel-vs-saved** (the determinism axis, §7). The tiers are the join.

```
T1 · AUTO-COMPILE-AND-RUN-SAFE
   • a SAVED chain re-run (compiled once, inspected once, trusted thereafter — the dominant safe case)
   • a NOVEL intent that is per-unit-classification-shaped over a KNOWN dir (Probe A): the map task is
     answerable from one unit, schema captures it, single-map is right.
   guardrails: validate-before-run (always) + dry-run-one-unit (cheap, catches a smuggled non-local clause).
   inspect-approve OPTIONAL here — the dry-run is the empirical floor; a human need not read every plan.
   → this is the band where "point at a dir, get coverage" actually works unattended (the anchor's dream).

T2 · COMPILE-BUT-MUST-BE-APPROVED  (novel + ambiguous OR reasoning-shaped-single-locus)
   • ambiguous scope (Probe B) — the selector is a GUESS; a human must confirm "yes, those units."
   • single-module intent-drift / "is X documented properly" — reasoning-shaped, SEM-3 S2 analog.
   • the research-wave / coherence-scan faces on FIRST compile (before they become saved chains) — the
     skeptic-area + area-sizing laws need a human eye the deterministic legs can't provide (§4).
   guardrails: validate + pre-map-grounding + dry-run + MANDATORY inspect-approve. Even so, Probe C shows the
   subtle non-local prompt is invisible in the plan (Observed) → Inferred-missed by an approver — so dry-run is
   NOT optional here, it is the leg that covers approve's blind spot. The two together are a hedge, not a guarantee.

T3 · should NOT be auto-compiled at all  (the SEM-3 S3 analog — the make-or-break "say it plainly")
   • intents whose TRUE shape is deep cross-unit reasoning where the map primitive is a category error
     (Probe D "is anything built twice", "does the dataflow here have a leak", "is this migration complete"):
     the answer is not a join over per-unit extractions — it is whole-system reasoning. A map-shaped compiler
     will CONFIDENTLY emit a single-map (or a too-shallow multi-pass) and ship noise.
   • why even the full hedge doesn't rescue T3: the only leg that could verify the PLAN's soundness is a
     stronger judge of the plan — which DOESN'T EXIST (§1). dry-run shows each unit "can't tell" (correct! it
     IS cross-unit) but that's a signal to ABORT the auto-compile, not to fix it. These intents must be
     hand-authored as multi-pass chains by a human/strong-agent who decides the pairing/clustering shape
     (SEM-2's map→pair→map), OR routed to a different faculty entirely. Do not let the compiler pretend it can
     one-shot them. Pretending it can is the over-claim that produces the confidently-wrong-plan death.
```

**The plain S3-style verdict (asked for explicitly):** *there is a class of query — deep cross-unit reasoning
where the map decomposition is itself the wrong primitive — for which the compiler cannot be trusted to choose
the chain shape, with or without the full guardrail stack, because the only thing that could verify its choice
is a judge stronger than the compiler, and by construction none exists. Route these to human/strong-agent
hand-authoring, not auto-compile.*

---

## 6 · The durable artefact to build first — a compile calibration harness (the SEM-3 §8 analog, and it's FREE)

SEM-3's strongest recommendation was "build a calibration harness from the system's own named incidents
*before* trusting the layer." The compile analog is **already written in the anchor** and costs nothing to
assemble: **the five faces in anchor §3 ARE labelled intent→Chain pairs** (research-wave, coherence-scan,
onboard, repo-QA, doc-staleness) — each is a known-good target Chain for a known intent. Plus the four probe
intents here (A clean / B ambiguous / C planted-defect / D cross-unit) as adversarial cases with known
correct shapes.

**What the harness measures, per intent-class:**
- **shape-accuracy** — did the compiler pick the right `passes` (single-map vs map→pair→map)? (Probe D is the
  fail case; this is the T3 detector.)
- **unit-locality** — does every map_prompt clause answer from one unit? *(checkable by dry-run: run the
  emitted map on one unit, flag any "can't determine from this file" — §3.4.)*
- **selector-precision/recall** — do the resolved units match the intended scope? (against the labelled face.)
- **schema-coverage** — does map_schema carry every field the reduce_prompt needs? (a join check against the
  labelled face.)
- **law-compliance** — for the research-wave face: is a skeptic area present, are areas sized-by-content?
  (the `research-wave/SKILL.md:71-73` laws as assertions.)

**The trust bar becomes a number per class** (SEM-3's "3 of 82" / its harness): a class auto-compiles (T1)
only if its measured shape-accuracy + unit-locality clear thresholds Tim sets; otherwise it falls to T2
(approve) or T3 (hand-author). **Without this harness the T1/T2/T3 split is my reasoned judgment from n=4
probes; with it, it's a measurement.** Build it reusing the runner (it just *runs* the compiler on the
labelled intents and dry-runs each emitted chain on one unit) — the same shape as SEM-3's `run_jury`-over-
fixed-inputs harness. **This is the one concrete first step the compiler half of the round points at.**

---

## 7 · The non-determinism → save-reuse insight (the real "yes-but-actually it's FINE")

A compile is a smart-model judgment, so — exactly like a `run_jury` draw (SEM-3 §1.3: temp>0 draws *vary* by
design) — **recompiling the same intent yields a DIFFERENT chain.** The anchor §7.6 worries about this
("Determinism/reuse … is a chain run reproducible enough to trust a saved chain's output across runs?"). The
resolution is in the anchor's own §3 and it dissolves most of the worry:

> **You save the COMPILED CONFIG, not the intent.** (Anchor §3: "common purposes are *saved* chains … novel
> queries *compile* fresh; the runner executes *any* valid instance — it doesn't care if the config was
> compiled or hand-written or saved.")

So the non-deterministic step (compile) is paid and gated **ONCE** per saved face; thereafter the runner over
a *fixed* Chain is as reproducible as the map/reduce models allow (the same determinism-is-the-routing's-
property, not-the-judgment's distinction SEM-3 §1.3 drew — the *config* is fixed and deterministic to read,
the *model outputs* over it vary, but that's the map/reduce variance SEM-3 already characterized, not new
compile-risk). **Therefore:**

- **Compile-risk is ACUTE for novel one-shot queries** (repo-QA: every invocation compiles fresh, every
  compile is an un-gated planning judgment) — these are the T2 cases that genuinely need a guardrail every time.
- **Compile-risk is NEARLY ABSENT for the saved faces** (research-wave, coherence-scan, onboard, doc-staleness):
  compiled once, inspected once (T2 on first compile), saved, trusted thereafter (T1). The risky step happens
  at *authoring time* under a human eye, not at *every run*.

This is the insight that makes the primitive *shippable despite an un-correctable planner*: **the faces — the
high-value, high-frequency uses — live in the safe half of the determinism axis precisely because they're
saved.** The compiler's danger is concentrated in the novel-one-shot quadrant, which is also the lowest-stakes
(an ad-hoc repo question, easy to re-ask) — and even there, dry-run-one-unit is the cheap empirical floor. The
anchor's worry is real but it lands on the *cheap-to-redo* cases, not the *load-bearing* ones.

**Cache-invalidation corollary (anchor §7.6, §9):** the saved *chain* is stable; the *digest* it produced is a
warm cache over a corpus that changes. Re-derive the digest on corpus change (the own/reflect law — re-derive
detection cheaply, own only the disposition, Semantic Layer §9); the saved *chain config* does not need
re-compiling when the corpus changes (its selector is a glob, its prompt is corpus-independent), only the
*map output* does. So invalidation is a map-rerun, not a re-compile — the expensive-judgment step stays paid-
once. *(Inferred from the own/reflect law + the §3 save-the-config move; not yet built.)*

---

## 8 · Everywhere it connects + what needs building (the anchor asked for this specifically)

**Connects to (Observed unless noted):**
- **`fabric/transport.py:47-48`** (the `json_schema` branch) — the compiler emits a Chain *as* a schema-
  constrained output through this exact path; no new transport needed for the emission. *Reuse, don't build.*
- **`fabric/transport.py:15-25`** (`list_models`, "so the self-coding brain never invents model names") — the
  validate-before-run model-existence check (§3.3) is *this function*, already built for exactly this purpose.
- **`fabric/client.py:54-87`** (parse/validate/retry, fail-loud) — the compiler's emission inherits the same
  malformed-output → retry → FabricError guarantee the map already has (SEM-3 §1.1). *Reuse.*
- **`runtime/rules.py`** (the closed-grammar pure evaluator, SEM-3 §1.3) — the *template* for a deterministic
  `Chain.validate()` (§3.3): a closed checker, never eval/exec, that resolves the selector + checks models +
  validates map_schema.
- **`runtime/cognition.py:109`** (`run_role` hardcodes `ctx["utterance"]`) — the one net-new seam SEM-1 already
  flagged: a unit-reading worker needs a generalized ctx→messages mapping, and **the dry-run-one-unit leg
  (§3.4) needs the same seam** (it runs the map on one unit). So the dry-run guardrail and the map both depend
  on this single generalization — build it once.
- **`roles/*.py` + `runtime/roles.py`** (file-discovered registry, `cognition.py:70-89`) — a *saved chain* is a
  declared file the registry discovers, exactly like a role (anchor §3 "common purposes are saved chains";
  Semantic Layer §6 "a finding-type is just a role file the registry already discovers"). *The save-reuse half
  of §7 is already-built mechanism.*
- **`ops/cli/app.py:133`** (the verb chain; only `suites` today) — where `company research <dir>` /
  `company ask <dir> "<q>"` / `company onboard` slot in (anchor §6). **Net-new: these verbs + the compile→
  validate→[dry-run]→[approve]→run flow behind them.**
- **`research-wave/SKILL.md:71-73`** (the skeptic/sizing laws) — the laws the compiler must honor for the
  research-wave face; the law-compliance assertions of the §6 harness.

**CRUCIAL reuse discovery (Observed this session — the guardrails are MOSTLY ALREADY BUILT, in a different
shape):** three of the four trust legs already exist as machinery for the *decision→implementation wire* and
the *authoring* faculties, and the corpus-chain compiler should reuse them, not reinvent (the "Use Existing
Resources" / "found-elsewhere informs" laws — this is a strong reuse signal, not a drop-in claim):

- **`runtime/governance.py` IS the inspect-approve gate (§3.2), generalized.** Observed: it declares a
  per-action-class posture on `reversibility · cost · externality` → `AUTO | SURFACE | CONFIRM`
  (`governance.py:1-12`), with classes *locked-to-CONFIRM forever* (real source data, external publishing).
  **A `compile`/`run-chain` action class slots straight in:** a saved-chain re-run is `AUTO`; a novel compile
  is `SURFACE` (surface the plan + deadline) or `CONFIRM` (T2 approve); a T3 cross-unit auto-compile is exactly
  the kind of thing the posture system should refuse. **The inspect-approve leg is not net-new — it is a new
  POLICY row + the surfaced-decision plumbing that already exists.** This is a materially more grounded picture
  than "build an approve gate."
- **`runtime/authoring.py` IS the dry-run + validate-outside-the-live-tree pattern (§3.3, §3.4).** Observed:
  it renders a role's declared fields → real source, validates by *importing it in a temp dir* before it
  touches the live tree (`authoring.py` docstring: "validate a generated module OUTSIDE the live tree before
  it is ever written"), and has an explicit **`dry_run_role`** that "imports from a temp module to fire a
  draft." **This is the exact discipline `Chain.validate()` (validate before spend) and dry-run-one-unit (fire
  the map on one unit as a draft before fanning out) need** — the temp-validate-then-commit and the
  dry-run-a-draft patterns are *already proven here*. Reuse the pattern; don't reinvent the gate.
- **`runtime/implement.py` IS the structured-result, fail-loud round-trip (the model-call discipline).**
  Observed: it spawns a governed job, "captures a STRUCTURED result … never scraped text," "FAIL LOUD on
  non-JSON output," is "injectable / dry-run (a `runner` callable can be supplied so tests don't burn a real"
  call). The compiler's emission inherits this same structured-or-fail-loud + injectable-for-test discipline.
- **`runtime/compile.py` is a NAME-COLLISION but a relevant MODEL (Observed).** It is NOT an NL→config
  compiler — it is the *workflow-graph → execution* compiler (`Graph` of `NodeInstance`s → `ExecNode`s with
  addresses, `compile.py:47-113`). But it embodies two principles the corpus-chain compiler should copy
  exactly: **(1) "the runtime recompiles each run, so the editable face and the runnable face never drift"**
  (`compile.py:1-6`) — the analog: recompile/re-validate the Chain each run so a saved config can't drift from
  what actually runs; and **(2) it is purely deterministic + fail-loud** ("an edge referencing a node not in
  the graph raises", `compile.py:67`) — the model for `Chain.validate()`'s deterministic runnable-checks
  (§3.3). The NL→Chain compiler is the *smart* sibling of this *structural* compiler; they share the
  validate-before-run, fail-loud, faces-never-drift discipline. **Worth a deliberate naming decision so the
  two `compile`s don't collide in the codebase** (e.g. `chain_compile` vs the existing graph `compile`).

**What needs building (marked net-new vs reuse, corrected for the discovery above):**
1. **`Chain` as a declared typed object** (anchor §3) — net-new schema; emit-able via the existing json_schema
   branch. *(small, the spine of everything.)*
2. **`Chain.validate()` (the runnable layer, §3.3)** — net-new logic, but built on `list_models`
   (`transport.py:15`, the model-existence source of truth) + `rules.py`'s closed-grammar pattern + the
   *fail-loud deterministic* model of `compile.py:67`. *Highest reliability-per-effort.*
3. **the generalized ctx→messages seam** (SEM-1's net-new) — needed by the map AND the dry-run. *One build,
   two consumers.*
4. **dry-run-one-unit (§3.4)** — net-new but the *pattern is already in `authoring.py`'s `dry_run_role` /
   validate-in-temp-dir*; run the map on `units[0]`, surface the worker output for the unit-locality read. *The
   keystone-substitute — do not skip it; reuse the authoring dry-run shape.*
5. **the inspect-approve gate (§3.2)** — **NOT net-new**: a new `compile`/`run-chain` POLICY class in
   `governance.py` + the existing surfaced-decision plumbing. *Reuse.*
6. **the compile calibration harness** (§6) — net-new, but the labelled set is FREE (the §3 faces). *Build
   before trusting auto-compile.*
7. **the CLI verbs + the gated flow** (compile→validate→dry-run→governance-posture→run) — net-new orchestration
   in `ops/cli/`, but it *wires together existing pieces* (governance posture + authoring dry-run + implement-
   style structured round-trip) rather than building each from scratch.

---

## 9 · Direct answers to the deliverable questions

1. **Can the compiler be trusted?** *Tiered.* **Yes** for saved chains and well-specified per-unit-
   classification intents over a known dir (T1) — Verified: I emitted a clean such chain (Probe A).
   **Conditionally** for novel/ambiguous/single-locus-reasoning intents (T2), with validate + dry-run +
   inspect-approve — but the dominant subtle defect (Probe C) is Observably invisible in the plan → Inferred-
   missed by an approver alone, so dry-run is mandatory, not optional. **No** for deep cross-unit-reasoning
   intents where the map primitive is
   a category error (T3) — the compiler confidently emits the wrong shape and nothing can verify the plan
   because no judge stronger than the compiler exists.

2. **With what guardrails?** In order of reliability: **validate-before-run** (deterministic, kills the
   runnable class loud — the most under-used, build it first) → **dry-run-one-unit** (empirical, the only
   cheap leg that surfaces non-unit-local prompts — the keystone-substitute) → **cheap pre-map grounding**
   (grounds the premises/scope) → **inspect-approve** (the floor for gross/legible errors; misses subtle
   law-violations) → **schema-constrain** (kills malformed config; NOTHING about plan correctness, and may
   *hurt* planning since compile is reasoning-shaped). **There is NO stronger-model-confirm leg** (§1) — that
   is the structural difference from SEM-3 and the reason a T3 class exists at all.

3. **What reliably compiles vs needs a human?** Reliable unattended: per-unit-classification over a known dir,
   and any saved chain. Needs a human eye (T2): ambiguous scope, the skeptic-area law for the research-wave
   face (invisible to dry-run and validate), schema-coverage against intent. Needs human *authoring*, never
   auto-compile (T3): cross-unit reasoning where the chain *shape* is the question.

4. **Is there a class that should NOT be auto-compiled?** **Yes, plainly: deep cross-unit reasoning intents
   where the correct chain is not a map at all** (built-twice discovery, dataflow/leak reasoning, "is this
   migration complete," behavioral-coverage equivalence — the exact SEM-3 S3 set, reached from the planning
   side). The compiler will emit a schema-valid single-map that runs and ships noise. Route to hand-authoring.

5. **Does COMPILE introduce a NEW trust surface?** **Yes — and it is worse than the map's.** A confidently
   mis-compiled chain that LOOKS valid is the structured-output-false-confidence trap (SEM-3 §1.1) reborn one
   stage *earlier* (it mis-shapes the whole run, not one finding) and one rung *higher* (there is no stronger
   model behind it to catch it). The nearest measured analog (text-to-SQL: 98.7% semantic errors, SOTA <
   human ceiling) confirms the trap is real and unfixable to 100%. The compile stage is genuinely the
   make-or-break, exactly as the anchor §7.1 named it.

---

## 10 · The "yes, but actually" list (where I corrected/sharpened the anchor)

- **"COMPILE … surface the plan; approve, then go" framed as sufficient mitigation (§2, §7.1)** → *actually*
  inspect-approve catches gross/legible errors (Verified) but the dominant subtle defect (a non-unit-local
  map_prompt, Probe C) is Observably invisible in the plan text → Inferred-missed by an approver; it must be
  paired with dry-run-one-unit, the only cheap leg that surfaces unit-locality empirically. (§3.2, §3.4)
- **"schema-constrain" treated as pure upside (§7.1)** → *actually* compile is *reasoning*-shaped, and
  constrained decoding *hurts* reasoning ("Let Me Speak Freely?") — so the structural guarantee and the
  planning quality pull opposite ways; and the well-typed Chain *manufactures* false confidence with no
  stronger model behind it. (§3.1)
- **the trust question framed as SEM-3's ("is the judgment trustworthy")** → *actually* the defining fact is
  the **missing keystone**: COMPILE has no model tier above it, so SEM-3's stronger-model-confirm is
  structurally unavailable, and the legs are a human + deterministic + empirical *hedge*, never a better
  judge. This is the whole reason a T3 "do-not-auto-compile" class exists. (§1, §3.6)
- **"validate-before-run" folded vaguely into inspect-approve (§2)** → *actually* it is a *separate,
  deterministic, reliable* leg that should fail loud BEFORE a human is asked — selector-resolves, models-exist
  (`list_models` already exists for this), schema-well-formed. The anchor most under-specifies the leg with
  the highest reliability-per-effort. (§3.3)
- **"Determinism/reuse … is a chain run reproducible enough to trust a saved chain?" (§7.6)** → *actually* you
  save the COMPILED CONFIG not the intent (anchor's own §3), so the non-deterministic compile is paid+gated
  ONCE for a saved face; compile-risk is acute only for novel one-shot queries (cheap to re-ask) and nearly
  absent for the high-value saved faces. The worry lands on the low-stakes quadrant. (§7)
- **"the compiler IS a chain / cheap pre-map to inform the plan" (§9)** → *actually* the pre-map checks the
  compiler's *premises* (what units exist) not its *reasoning*, so it reduces wrong-units/wrong-shape errors
  but does NOT recover a stronger judge; it is the partial second-signal, not the keystone. (§3.5)
- **the recursion the anchor flagged ("would a compiler generate this wave's allocation?")** → *actually* a
  telling self-test: this very wave's allocation **includes a make-or-break/skeptic area (this one)** — the
  `research-wave/SKILL.md:71-73` law. A naive compiler that emitted N equal "explore area X" agents with **no
  rigor area** would produce a biased wave that *runs fine and reads complete* — the missing-skeptic failure
  (§4) is invisible to dry-run and validate, catchable only by the law-check or a human. So the anchor's own
  recursion is a live instance of the dominant trust surface: the compiler can omit the very leg that makes the
  output trustworthy, and nothing downstream notices. (§4, §6)

## 11 · Net (the unbiased verdict)

The compiler **can** be trusted — for a narrow, valuable band: saved chains (compiled once, gated once,
trusted thereafter) and well-specified per-unit-classification intents over a known dir, with validate-before-
run + dry-run-one-unit as the floor. It **cannot** be trusted unattended for novel ambiguous intents (they
need a human approve, and even then the dominant subtle defect is Observably invisible in the plan → Inferred-
missed by an approver alone, so dry-run is mandatory) and **must not** be auto-compiled at all for deep
cross-unit-reasoning intents where the map shape
is itself the wrong primitive. The defining fact — the one that makes this *not* just "SEM-3 for the compiler"
— is that **COMPILE has no model tier above it: the strong model IS the planner, so its systematic errors have
no model-level corrector**, and SEM-3's keystone (stronger-model-confirm) is structurally unavailable. The
replacements are a human + deterministic checks + an empirical dry-run + a grounding pre-map — a *hedge*, never
a better judge — which is precisely why a do-not-auto-compile class exists. The dominant failure is the
false-confidence trap reborn one stage earlier and worse: a schema-valid, reads-fine chain that encodes the
wrong question (the non-unit-local prompt is the specific instance), which the nearest measured field
(text-to-SQL: 98.7% of errors semantic, SOTA below the human ceiling) confirms is real and unfixable to 100%.
The "yes-but-actually it's fine" that makes the primitive shippable anyway: **you save the config, not the
intent**, so the un-correctable planning judgment is paid and gated ONCE for the high-value saved faces, and
the risk concentrates in the cheap-to-redo novel-query quadrant. Build it that way — `Chain.validate()` first,
dry-run-one-unit as the non-negotiable keystone-substitute, the §3-faces calibration harness before trusting
auto-compile, and a hard T3 "hand-author, don't auto-compile" boundary — and the compiler is a trustworthy
on-ramp for the band that matters. Ship it as "describe what you want, the smart model plans the whole run,
approve and go," and one confident, well-typed, *mis-planned* chain will spend the map, ship an authoritative
wrong answer, and teach Tim that the on-ramp can't be trusted — the cry-wolf death the anchor named, moved
upstream to where it does the most damage.

— *CC-2, written to leave the idea bigger and more real. The one fact to carry forward: the compiler has no
judge above it — so unlike the semantic layer, its trust comes from a hedge (validate + dry-run + human +
pre-map), never from a stronger confirmer; the dominant defect is a schema-valid wrong-question chain
surfaced only by a dry-run, not by reading the plan; and you save the config not the intent, which is what
makes the saved faces safe and concentrates the risk in the cheap novel-query quadrant.*
