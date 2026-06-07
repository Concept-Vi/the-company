# R2 — Rule Determinism: can "full declared logic" be deterministic AND renderable?

*Round-2 deep review answering R1-FOLD **F5** (Adversarial **Attack 5**): "full declared logic" (DECISIONS **Q4**) was chosen, but R1 found determinism **asserted, not enforced** — C3.1 / C0.2 state the constraint and specify no mechanism. This doc designs the enforcement concretely and reports where expressiveness and renderability actually conflict. **READ-ONLY** — grounded in the live code (`nodes/gate.py`, `runtime/scheduler.py`, `nodes/join.py`, `06-rendering.md`); no criteria/guide edits (C3.1 already absorbed the F5 wording — this is the design behind it). Epistemic tags follow the repo rule: **Observed** (read in code), **Designed** (intended, not built), **Open** (decide with Tim).*

---

## TL;DR — the one finding

**Determinism and full expressiveness do NOT fundamentally conflict.** Determinism is fully enforceable even at high expressiveness, *provided* the rule's referenceable inputs are whitelisted to resolved values and its operators are pure.

**Renderability IS the binding constraint.** An arbitrary nested expression cannot be the short edge-label the cognition view draws (`06` lines 67/93: edges labelled `gate`/`feed`/`digest`). "Arbitrary code" is what violates AGENTS.md **rule 9** (no text wall) — not what violates determinism.

So the crisp answer to "can both hold":

- **Full logic AS arbitrary code** (a sandboxed `eval` of a declared string) → CANNOT satisfy *enforceably-deterministic* (you cannot statically prove arbitrary eval is clean) AND CANNOT satisfy *renderable* (an arbitrary AST renders as a blob).
- **Full logic AS a bounded pure-expression grammar over resolved values** → CAN satisfy both. And this bounded grammar is the **maximal** reading that honours Q4's *own four constraints* (declarative-by-inspection · deterministic · renderable · no hidden model judgment).

**The conflict is internal to Q4.** Q4 attached four constraints that already exclude arbitrary code. Resolving toward the bounded grammar *honours Tim's stated constraints* — it does not cut his "power over simplicity" intent. True unbounded power is preserved by **composition** (§6): anything richer than the grammar is computed as an upstream pure compute node — the exact `gate.py` pattern (verdict produced upstream; the gate just routes the resolved value). No power lost; it moves from "bigger rule language" to "one more node," which is itself renderable and deterministic.

---

## 1 · The determinism precedent in the code (Observed)

### 1.1 `nodes/gate.py` — how the routing predicate stays deterministic
`gate.run(inputs, config)` (gate.py:26–40) is a **pure function of `(value, verdict)`** — two *resolved input values*. It reads nothing else: no clock, no RNG, no scheduler handle, no "which sibling finished." It returns a single-key dict `{"pass": value}` or `{"fail": value}`. Determinism here is not asserted by a comment — it is **structural**: the function *has nothing nondeterministic in scope to reach* (gate.py:16 confirms it: "NOT VOLATILE — `run()` is a pure function of (value, verdict); the memo gate may cache it"). This is the model the rule evaluator must copy exactly.

The doc-string states the deeper law (gate.py:7–8): branching is **absence-of-write**, *not* a conditional in the scheduler loop — "the scheduler stays a resolver, never control-flow." Routing is data-driven, not flow-driven.

### 1.2 `nodes/join.py` — how a multi-input node reads siblings deterministically
`join.run` (join.py:16–18) reads `[str(inputs[k]) for k in sorted(inputs)]` — **sorted key order, never arrival order**. This is the precedent that defeats "which-sibling-finished-first": a deterministic node over multiple inputs orders by a stable key (the declared port/address), not by the race. The rule evaluator inherits this: aggregation over siblings iterates a **declared, sorted set of addresses**, never "the results available now."

### 1.3 `runtime/scheduler.py` — there is NO global barrier (correction to the F5 wording)
The scheduler (scheduler.py:37–184) is a **reactive resolver, barrier-free** — a `while len(processed) < len(execs) and progress` loop that fires each node the instant its inputs resolve (scheduler.py:59–77). There is **no global wave barrier** in the code. So "post-barrier" (the F5 phrasing) must be read precisely as **per-rule readiness**, the discipline the scheduler already enforces for nodes:

> "READY only when every input port its type DECLARES (PORTS_IN) is both wired and resolved — a half-wired node waits (it does not fire on empty input)." (scheduler.py:13–16, 72–77)

```python
declared = set(getattr(node_types[ex.type], "PORTS_IN", {}).keys())
if not declared <= set(ex.inputs.keys()):          # a required port is unwired -> wait
    continue
if not all(store.head(a) for a in ex.inputs.values()):   # an input is unresolved -> wait
    continue
```

A rule evaluates **only when every address it references is resolved**. That single discipline kills the entire nondeterminism class (count-so-far / which-finished-first / partial-results): the grammar has no "results available now" reference *and* the rule is not ready until all declared refs resolve. "Post-barrier" therefore = "after all referenced addresses resolve." It is the existing node-readiness law applied to the rule.

### 1.4 The memo gate — determinism is already load-bearing
`_memo_sig` (scheduler.py:26–34) keys the cache on `(type, version, config, input-content-hashes)` — **resolved input content only**. The cache is correct *only because* a non-VOLATILE node's output is a pure function of those (scheduler.py:88–94). The system already *depends* on rule-class determinism for resume/re-run correctness. A nondeterministic rule would silently poison this memo gate — so enforcement is not gold-plating; it protects an existing invariant.

---

## 2 · What "full declared logic" MAY and MAY NOT reference (the whitelist)

**Designed.** The evaluator (`cognition/rules.py`, net-new) treats a rule as a **bounded declarative AST**, not a sandboxed eval of a declared string. The single most important design choice is this AST/eval split — see §4 for *why* it is what makes enforcement possible at all.

### 2.1 ALLOWED — the referenceable-input whitelist
| Allowed | What it is | Why it's safe |
|---|---|---|
| **Resolved role-output field values** at `run://<turn>/<role>` (and `…#<port>`) | the JSON a role wrote this turn, read via the store at a *declared* address | the only nondeterminism-free source; identical inputs → identical value (rule's whole purpose: route on previous outputs — L2) |
| **Literals** | strings / numbers / booleans / null declared in the rule | constant by definition |
| **Pure comparison ops** | `==` `!=` `<` `<=` `>` `>=`, membership (`in`) | deterministic over their operands |
| **Pure boolean ops** | `and` `or` `not` | deterministic |
| **Pure arithmetic** | `+ - * /` (guard div-by-zero → reject or null, declared) | deterministic |
| **Field / path access** | `output.intent`, `recall.hits[0].score` over a *resolved* value | deterministic dereference of resolved data |
| **Bounded aggregation over a DECLARED sibling set** | `count(where …)`, `any/all`, `max/min/sum` over `[run://…/recall, run://…/ground]` — addresses named in the rule | iterates a **declared, sorted** address list (the `join.py` precedent), never "siblings done so far"; rule isn't ready until all of them resolve (§1.3) |

### 2.2 BANNED — and *how* each is rejected
| Banned | Why it breaks replay-identity | Rejection mechanism |
|---|---|---|
| `now()` / time / date | wall-clock differs per run | **not in grammar** → static AST reject at commit (C3.4 path) |
| `random()` / any RNG | non-reproducible | **not in grammar** → static reject |
| **wave / arrival order** ("which sibling finished first") | depends on the parallel-dispatch race | **no such reference exists in the grammar** → static reject; structurally there is no "order" value in the eval environment |
| **partial results / count-so-far / "available now"** | reads the race mid-flight | **not in grammar** + **per-rule readiness** (§1.3): rule only fires when *all* declared refs resolve, so "partial" is unrepresentable |
| **any model-or-role call inside a condition** | a model is nondeterministic and is *role* territory, not *rule* (L2) | **not in grammar** → static reject; structurally the evaluator has no model client in scope |
| **filesystem / network / env / external state** | non-reproducible, VOLATILE-class | **not in grammar** + **structurally unreachable** (eval environment holds only resolved values) |

The banned set is enforced **two ways at once** (defence in depth), per §4.

---

## 3 · Renderability — where the line actually is

**Observed (the render substrate, `06-rendering.md`):** the cognition view draws chains as **edges labelled by hop kind** — `gate` / `feed` / `digest` (06:67, 06:93) — short tokens, by sight, rule-9 ("not a text wall"). A role click opens the **Inspector** with the full JSON/config (06:96, reusing `Inspector.tsx`). Edges and ports are **backend-owned data** the generic renderer projects (06:30–32) — "add a node-type → it appears live, no FE code."

**The renderability line (Designed):**
- A rule is **addressable data on the edge** (satisfies C3.3 — "every rule + its firing is addressable data the live view can draw"). It renders in **two tiers**, mirroring the node Inspector pattern:
  1. **Edge label / chip** — a short by-sight summary for the common case (e.g. `if intent=ground` or a destination glyph). This is the rule-9-compliant surface.
  2. **Inspector-expand** — click the edge → the **full predicate** as a small, structured **expression tree** (the AST rendered as nested chips), plus the resolved values it read this turn and the routing trace.
- **Where it conflicts:** a **bounded AST renders as a small expression chip-tree** (legible, navigable — rule-9 OK). **Arbitrary code renders as an opaque blob** — a text wall — which is precisely the rule-9 violation. *That is the line.* Renderability is satisfiable exactly up to the bounded-AST grammar and no further. This — not determinism — is what caps "full logic."

So: **expressiveness and determinism don't conflict; expressiveness and renderability do, and they conflict at the boundary between "a structured AST you can draw" and "arbitrary code you can only dump."**

---

## 4 · How the evaluator ENFORCES it (the missing layer F5 names)

**Designed — `cognition/rules.py`.** "Asserted → enforced" is achieved by the **AST-not-eval** choice plus two enforcement layers. The reason this works: you *can* statically walk a bounded AST and reject any non-whitelisted node; you *cannot* statically prove an arbitrary `eval` string is clean — arbitrary eval would leave determinism "asserted" forever. The AST choice is what makes enforcement *possible*.

1. **Static enforcement (commit-time).** A rule is parsed to an AST and **whitelist-walked**: every node must be an allowed reference / literal / pure-op (§2.1). Any banned construct → **the rule fails validation and never commits.** This rides C3.4's "normal change path" (review + `drift_acceptance`) — a malformed rule is rejected exactly like a malformed node config. (This is the layer C3.1's "a rule that tries to read order/time/partials is rejected by the evaluator" names.)

2. **Structural enforcement (eval-time).** The evaluation environment is constructed to contain **only resolved address values** — no clock object, no RNG, no scheduler/run handle, no model client, no store-iteration-by-arrival. Exactly like `gate.run`: *the evaluator has nothing nondeterministic in scope to reach* (§1.1). Even a hypothetical grammar gap can't smuggle nondeterminism, because the capability simply isn't present in the environment. This is the stronger guarantee; the static layer is the loud, early, commit-time gate.

3. **Per-rule readiness (the race-killer).** The evaluator is invoked **only after every `run://` address the rule references is *settled*** — where **settled = resolved OR provably-never-coming** (the scheduler's PORTS_IN-readiness law, §1.3, applied to rules, *generalized* by §4.1). "Provably-never-coming" is exactly the scheduler's existing `pruned`/`failed` classification (`scheduler.py:155–182` pruned, `:104–116, 57` failed) — so the evaluator consults that **status**, not merely `store.head()`. This is the precise meaning of "post-barrier" given there is no global barrier in the code (§1.3 correction). It makes "partial / count-so-far / which-first" *unrepresentable*, not merely "discouraged." **Readiness is on settled-STATUS, never a timeout** — a timeout would reintroduce wall-clock as a routing input, the exact nondeterminism this whole design kills. (Without the settled-not-resolved reading, a rule referencing a pruned/failed role would hang forever — see §4.1, which this point depends on.)

### 4.1 · Missing / pruned / failed references — THE blocking decision (no-silent-fallback)

**Designed + Open (Tim).** §4.3 readiness assumes every referenced address *eventually* resolves. Under the real graph it may **never** resolve — and this is the single most likely real-world path to accidental nondeterminism, so it must be decided **before** `cognition/rules.py` is built. A `run://<turn>/<role>` address can be permanently absent two ways (both **Observed** in the code):

- **Pruned** — an upstream `gate` did not take that role's branch, so its address is *deliberately never written* (`gate.py:8–13`; scheduler classifies it `pruned`, `scheduler.py:155–182`). The role legitimately did not run.
- **Failed** — the role's `run()` raised; the scheduler writes **no** output ref and records it in `failed` (`scheduler.py:104–116, 57`). The address is absent because of an error.

The convenient-but-WRONG behaviors the plan must NOT inherit:
- `gate.py:38` truthy-tests `None`/empty as **fail** — so a *missing* input silently routes to the `fail` branch, **indistinguishable from a present-but-falsy value**.
- `_resolve_context_at` returns `''` when nothing is attached (R1-FOLD F3) — a silent empty.

Either path **couples routing to resolution-success/timing** — re-introducing exactly the leak the barrier closed, through the back door of "did the address resolve." That violates the **no-silent-fallback law** ([[feedback-no-silent-failures]]): a missing reference must be a **declared outcome**, never an implicit falsy. Two acceptable resolutions (the choice is Tim's; **A is the safe default**):

- **(A) FAIL-LOUD (recommended default).** A referenced address that did not resolve → the rule does **not** silently evaluate; it surfaces a loud, legible `cognition.rule.unresolved` event naming the rule + the missing ref, and that rule's routing this turn is a **named error state**, not a guessed branch. Mirrors `scheduler.py`'s containment-not-swallowing discipline.
- **(B) DECLARED `on_missing`.** A rule may declare, per reference, an explicit `on_missing: <literal | route>` — so the absence is handled *by declaration*, replay-identically and visibly (it renders on the edge). Whether to offer (B) at all, or hold strictly to (A), is the Open decision.

The invariant to hold either way: **resolution-success must never implicitly become a routing input.** A rule reads a *value*; "the value isn't there" is a declared condition, not a falsy. (This generalizes §5 case 8 from div-zero/undefined-field to the upstream pruned/failed-role case, which is the common one under parallel dispatch.)

**Replay-identity (C0.2) then holds by construction:** rule = pure function of resolved address values + per-rule readiness ⇒ re-running identical inputs routes identically, regardless of the order the wave's roles finished. C0.2 must test this on a **non-trivial** rule (one reading multiple resolved fields whose siblings can finish in different orders), not a one-liner — exactly as the hardened C0.2 now requires.

---

## 5 · Adversarial cases the evaluator MUST reject (concrete)

Each is a rule the build's adversarial test (C3.1) should *attempt* and confirm is rejected:

1. **Time-smuggle** — `if now().hour > 12 route A else B`. → static reject (`now()` not in grammar).
2. **Order-smuggle** — `route to whichever_role_finished_first(...)`. → static reject (no order/arrival reference exists).
3. **Count-so-far** — `if count(siblings_done) >= 2 route A`. → static reject (`siblings_done` is not a declared address set; "done" is not representable) + readiness makes it moot.
4. **Partial-peek** — references `run://<turn>/ground` but fires before `ground` resolves. → readiness blocks evaluation until `ground` resolves; cannot read a partial.
5. **Random** — `if random() > 0.5 …`. → static reject.
6. **Model-in-a-rule** — `if classify_with_model(output) == 'x' …` (the L2 violation). → static reject (no model/role-call grammar; structurally no model client in scope). *A model only runs inside a role.*
7. **External-state** — `if read_file('/tmp/flag') …` / a network read. → static reject + structurally unreachable.
8. **Div-by-zero / undefined field** — must resolve to a **declared** outcome (reject-at-commit if statically detectable, else a loud fail at eval — never a silent default), per the no-silent-fallback law (rule 4).
9. **Missing / pruned / failed reference (the common one — §4.1)** — a rule references `run://<turn>/ground`, but `ground` was pruned by an upstream gate or failed. → must **fail-loud or hit a declared `on_missing`**, **never** the implicit truthy-on-missing→`fail` that `gate.py:38` does. Test both pruned and failed upstreams; assert routing is a named outcome, not a silent guess, and is **replay-identical** across runs where the *order* of the surviving siblings differs.

---

## 6 · The escape valve — composition preserves unbounded power

**This is the answer to "but what if a rule needs more than the grammar?"** — and it is the most on-brand resolution for this system (Tim's universal-composition principle).

Anything richer than the bounded grammar is **not** added to the rule language. It is computed as an **upstream pure compute node** — the exact `gate.py` pattern: a node produces a `verdict` value, and the gate (or rule) just routes the *resolved* result. That upstream node:
- is **itself renderable** (a node on the cognition canvas — the generic NodeShape, 06:30),
- is **deterministic by the same memo discipline** (non-VOLATILE → pure function of inputs → cached and replay-identical, scheduler.py:88–96),
- and if it genuinely needs *judgment*, it is a **role** (a model runs inside it) — which is L2-correct: the model lives in a role, never in a rule; the rule still just routes the role's resolved output.

So **no expressive power is lost.** It moves from "a bigger, un-renderable rule language" to "one more node/role + a simple rule over its output." Power → composition, exactly as the framework prescribes.

---

## 7 · Recommendation — the actual constraint set

**Is "full logic" really wanted, or is "rich conditions + chains over resolved values" the safe maximum?**

**Recommendation: adopt "rich conditions + chains over resolved values" as the bounded-AST grammar — and recognise that this IS "full declared logic" in every sense Tim's intent (L2: route based on previous outputs) needs.** This is not a cut to Q4; it is the resolution of a tension *internal to Q4*. Q4 itself attached four constraints — **declarative-by-inspection · deterministic · renderable · no hidden model judgment** — and *those four already exclude arbitrary code*. The bounded grammar is the maximal expressiveness that satisfies all four simultaneously.

**The constraint set to lock:**
1. A rule is a **bounded declarative AST**, never a sandboxed eval of arbitrary code.
2. **Referenceable inputs = resolved `run://` address values only** (the §2.1 whitelist).
3. **Banned**: time / random / wave-arrival-order / partial-results / model-or-role calls / external state (§2.2) — enforced **statically (commit-time AST walk)** *and* **structurally (resolved-values-only eval environment)**.
4. **Per-rule readiness**: a rule evaluates only after *all* referenced addresses resolve (the scheduler's node-readiness law applied to rules) — this is the precise meaning of "post-barrier."
5. **Renderable in two tiers**: short edge-chip (rule-9 by-sight) + Inspector-expand (the AST as an expression chip-tree). The bounded grammar is the renderability ceiling; arbitrary code would be a rule-9 blob.
6. **Unbounded power preserved by composition**: richer logic → an upstream pure compute node (or a role for judgment), routed by a simple rule over its resolved output.
7. **Missing/pruned/failed references are a DECLARED outcome** (fail-loud default; optional declared `on_missing`) — never the implicit truthy-on-missing→`fail` (§4.1). *This is the blocking decision to confirm with Tim — it is the most likely real-world nondeterminism path under parallel dispatch.*

**Why frame it this way:** Tim chose "power over simplicity." The bounded grammar *keeps the power* (full conditions, chains, aggregation, all five destinations C3.2) and *adds the escape valve* (composition) so nothing is unreachable — while making determinism a *property* (enforced) instead of a *hope* (asserted), and keeping the layer drawable on the cognition view. The decision to surface to Tim is the **outcome** (rules are a renderable, statically-checked expression grammar; anything beyond it composes as a node), not the implementation.

---

## 8 · What this means for the criteria (already absorbed; cross-check)
- **C3.1** already states "post-barrier, pure function of fully-resolved address values, referenceable-input whitelist, banned set, adversarial reject." This doc supplies the *mechanism* (AST-not-eval; static + structural layers; readiness = the real meaning of "post-barrier" since there's no global barrier in `scheduler.py`).
- **C0.2** already requires a **non-trivial** rule + replay-identical routing with siblings finishing in different orders. §4 is why it holds by construction; §5 lists what the adversarial half must reject.
- **C3.3 renderable** — §3 gives the two-tier render line and names the conflict boundary (chip-tree vs blob).
- **No criteria/guide edits made** — read-only; this is the design behind the hardened wording.

---

## Evidence ledger
- **Observed:** `gate.py:16,26–40` (pure-fn predicate, NOT VOLATILE, absence-of-write branching); `join.py:16–18` (sorted-key, never arrival-order, multi-input determinism); `scheduler.py:13–16,26–34,59–77,88–96` (barrier-free reactive resolver, PORTS_IN-readiness, memo-sig on resolved-content-only, VOLATILE handling); `address.py:32` (`run://` is a registered scheme; no `cog://`/`swarm://`); `06-rendering.md:30–32,67,93,96` (generic backend-owned edge/label render, hop-kind labels, Inspector-expand pattern).
- **Designed:** `cognition/rules.py` as a bounded-AST evaluator with static + structural enforcement; the §2 whitelist/ban table; the §3 two-tier render line; the §6 composition escape valve.
- **Open (Tim):** confirm the bounded-AST grammar as the reading of "full declared logic" (the §7 outcome to surface); the exact aggregation primitives to expose in v1 (count/any/all/max/min/sum) vs deferred.
