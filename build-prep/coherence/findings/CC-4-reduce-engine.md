# CC-4 — The REDUCE stage: the engine (the strong layer that joins, adjudicates, composes, decides-next)

> Companion to `CORPUS-CHAIN-ANCHOR.md`. My allocated area is **the reduce — the heavy lifter.** The
> anchor §2 gives it four jobs (JOIN · ADJUDICATE/VERIFY · COMPOSE · DECIDE-NEXT) and §7 flags its two
> hard mechanics (hierarchical-reduce-vs-coverage; followup cost). I read the real engine end-to-end
> (`run_swarm`/`run_role`/`run_jury`, the `reduce-tree` archetype, the roles registry, the transport),
> measured the staging threshold against real corpus + real context numbers, and pulled external prior
> art (RAPTOR, ToM, LLM×MapReduce, agentic RAG). I was asked to work the engine concretely, not confirm.
>
> **Marking:** **[OBS]** = read in code (`file:line`). **[VERIFIED]** = I measured it this session.
> **[INF]** = inferred from the code, labelled. **[EXT]** = external prior art. **[idea]** = my proposal.
>
> **The one line:** the map (`run_swarm`) is real and proven; **the reduce is the *least*-built stage of
> the whole engine** — its central job (cross-unit JOIN) has **no mechanism in the code at all**, the
> `reduce-tree` archetype that names it is **declared-but-dead**, and `run_jury` is **not** the JOIN the
> anchor §6 implies. The reduce is the thing to build, and its shape is **staged-or-single decided at
> compile-time from `map_schema` × unit-count vs synth-context** — a *derived* property, not a runtime guess.

---

## 0 · The headline finding (read this first — it corrects the anchor's most load-bearing claim)

The anchor §6 says the corpus-chain "IS `run_swarm`, a third application … `run_jury`'s 2nd-model slot is
the reduce's adjudicate leg." **That is right about the MAP and wrong about the REDUCE.** Grounded:

- **[OBS] The MAP exists and is proven.** `run_swarm` (`cognition.py:523`) fans `run_role` over a
  ready-set on a `ThreadPoolExecutor`, each role writes its schema-validated JSON to a distinct
  `run://<turn>/<role>` address, barriers, reads every value back via the canonical resolver
  (`resolve_run_ref`, `cognition.py:474`), emits one batched `cognition.wave` rollup. Per-unit structured
  extraction over independent units with guaranteed per-unit attention — exactly the anchor's map. **This
  half is real; the SEM round measured its throughput (~2,241 tok/s @ conc-32).**

- **[OBS] The REDUCE's central job — cross-unit JOIN — has NO mechanism in the engine.** I grepped every
  runtime read of the reduce-naming fields. The `reduce-tree` thought-shape exists
  (`suite.py:1474`): `{"archetype":"reduce-tree", "fanout":"cast", "join":"reduce", "render_from":"reduce"}`.
  **Its `join` and `render_from` keys are NEVER read at runtime** — the only references are the declaration
  itself (`suite.py:1474-1476`) and the docstring describing it (`suite.py:1464`, `:1572`). **[OBS] There
  is no `reduce` role file** (`ls roles/` → check · connect · focus · ground · judge · recall ·
  verify_jury · voice — *no reduce, no join, no synth*). Nothing in the code fires a join role over the
  map outputs. **The `reduce-tree` archetype is declared-but-dead — a named slot with no engine behind it.**

- **[OBS] What the live system calls "reduce" is the G3 rule-injection, which is NOT a reduce.** In the
  one path that consumes a wave (`chat_parts`, `suite.py:5374-5399`), after the wave barriers the system
  runs `INJECTION_RULE.decide(resolved)` — a **pure deterministic L2 rule** (`cognition.py:160`,
  `recall.relevant AND ground.in_scope`) that picks a value to inject into the next reply part. That is
  *routing a pre-computed field*, not *a strong model reasoning across the units*. **There is no
  strong-model call that reads the structured digest and composes an answer.** The "smart reduce layer"
  the anchor's whole cost-shape argument rests on (§4: "expensive intelligence applied only to compressed
  structured inputs") **is not built.**

- **[OBS] `run_jury` is NOT the JOIN.** It is `N draws of ONE role on ONE input → a deterministic
  verdict_rule` (`cognition.py:637-715`; `roles/verify_jury.py:majority_vote`). That is *variance
  reduction over a single unit*, not *reasoning across many units*. It has no notion of multiple units'
  outputs at all — `ctx` is one input, fanned into N identical draws. So of the reduce's four jobs,
  **`run_jury` touches only a degenerate slice of ADJUDICATE (intra-unit variance), and touches JOIN,
  COMPOSE, and DECIDE-NEXT not at all.**

> **So the reduce is the build.** The map is the proven, cheap, parallel half the prior rounds already
> grounded. The reduce — the strong layer that the anchor calls "the heavy lifter" — is the *least*-built
> part of the engine, and the part on which the entire corpus-chain value proposition (full coverage at
> cheap cost + correctness at smart quality) depends. Everything below is what it must actually do, what
> it can reuse, the one net-new seam it shares with SEM-1, and the two hard mechanics made concrete.

---

## 1 · The four jobs, against the real engine — what each needs and what exists

The anchor §2 names four reduce jobs. Mapped to the code, with the honest build-state of each:

| Job | What it must do | What exists | Build-state |
|---|---|---|---|
| **JOIN** | strong-model reasoning *across* the per-unit structured outputs (pairs/clusters/cross-refs) — where half-migration & built-twice get adjudicated *because the map can't* | **nothing** — `run_swarm` is a map (independent units), `run_jury` is intra-unit. No code reads >1 unit's output into one model call | **un-built** |
| **ADJUDICATE / VERIFY** | the correctness gate — catch a bad map extraction, re-query; SEM-3's stronger-model-confirm | `run_jury`'s verdict-rule shape (`cognition.py:707`) + the documented 2nd-model slot (`verify_jury.py:12-18`); the validate-and-retry in `client.complete` (catches *malformed*, not *wrong*) | **slot shaped, not wired** |
| **COMPOSE** | produce the answer / companion / synthesis / tagged result | the `render_from` field names it (`suite.py:1475`) but is never read; no compose role | **un-built** |
| **DECIDE-NEXT** | the conditional loop — conclude it needs a targeted re-map → loop back (a query engine, not one-shot) | `INJECTION_RULE` is the *pattern* of "a declared rule routes over a model output" (`cognition.py:160`); AREA-4 owns the loop machinery | **pattern exists, not applied to passes** |

The pattern in the third column matters: **the reduce is not net-new orchestration — it is the existing
primitives re-pointed**, but every one of its four jobs needs a piece that is presently absent. The
sections below build each.

---

## 2 · JOIN — the central job, and the one net-new seam it is blocked on

### 2.1 The blocking seam (shared with SEM-1, must be named)

**[OBS] `run_role` hardcodes its input: `utterance = ctx["utterance"]` (`cognition.py:109`).** A map worker
reads one utterance. **A reduce/JOIN role reads *many units' structured outputs* — not an utterance.** So
the JOIN is blocked on the *exact same net-new seam* SEM-1 flagged for the map: a **generalized
ctx→messages mapping** so a role can be fed something other than a single `ctx["utterance"]`. The role
schema already *declares* the hook — `input_addresses` (`roles.py:67`, e.g. `check.py:37`
`("run://<turn>/part-1", "ground")`) — but it is **descriptive-only today** (SEM-1's finding; confirmed:
nothing in `run_role` reads `role.input_addresses`). So:

> **[INF] The reduce role and the unit-reading map role share ONE net-new seam: generalize `run_role` to
> build its messages from `role.input_addresses` (resolve each `run://`/literal ref → a message block),
> not from a hardcoded `ctx["utterance"]`.** Build it once; the map's unit-reading and the reduce's
> digest-reading both ride it. This is the single most important engine change the corpus-chain needs, and
> it is the same one SEM-1 named — they converge on it from the two ends of the pipe.

### 2.2 Why JOIN is the *value* — and why a lone map can never do it

The anchor §5's coverage-certainty argument is about the *map* (every unit gets a focused pass). But the
**findings that justify the whole two-round effort are cross-unit by nature** and live *only* in the reduce:

- **[OBS, grounded in SEM-4 §3] The disagreement meta-finding IS a reduce-time JOIN.** SEM-4's prize —
  `structural-says-WIRED ∧ semantic-says-MEANINGLESS` — is *derived at read-time over two source-tagged
  findings at one address* (`SEM-4 §3.2`). That derivation **is a cross-unit join**: it reads a structural
  finding *and* a semantic finding and reasons over the pair. It is already live as the measured **3/82
  false-wires** (AREA-3; `/api/mockup-feedback` among them). **This is a worked instance of my area** — the
  highest-value finding in the whole system is a reduce-stage JOIN, and it exists because the reduce reads
  *two units' outputs together*, which no map worker and no `run_jury` can.
- half-migration spans ≥2 files; built-twice spans the repo (anchor §7.2). A map worker sees one unit and
  *guesses* at the other; only the reduce holds both.

So JOIN is not a nice-to-have leg of the reduce — **JOIN is the reduce's reason to exist.** A corpus-chain
whose reduce only composes per-unit summaries (no join) degenerates into "parallel summarize + concatenate"
— useful for `onboard`, useless for coherence/built-twice/half-migration, which are the hard faces.

### 2.3 The pairing pre-stage sidesteps the hardest JOINs (SEM-2's chain, made an engine fact)

**[OBS, SEM-2 + SEM-4 §3]** The sharpest JOINs don't need the reduce to *discover* the pair — they need a
*pairing pre-stage* to surface it, then a cheap second pass to *judge* it. SEM-2: "a 4B is a good
adjudicator of a candidate *pair*, a poor discoverer of one." So the engine's JOIN has **two shapes**, and
the chain config should distinguish them:

```
JOIN-by-reduce      the strong synth reads the whole digest and finds the cross-refs itself
                    (works when the digest fits one context — §4; expensive-model, high-coverage)
JOIN-by-pairing     a cheap structural/embedding stage surfaces the candidate PAIR → a 2nd MAP pass
                    judges the 2-unit input directly (SEM-2's chain; the pair never needs the tree — §4.4)
```

**[idea]** The pairing pre-stage is the answer to the hierarchical-reduce tension (§4): the JOINs most at
risk of being split across clusters are exactly the ones a pairing stage can hand to the reduce *as a
pre-formed 2-unit input*, so they never depend on co-visibility in the tree.

---

## 3 · ADJUDICATE/VERIFY — inherit SEM-3's keystone, do NOT re-use `run_jury` for it

The anchor §6 calls `run_jury`'s 2nd-model slot "the reduce's adjudicate leg." **[INF] This conflates two
different things and SEM-3 already proved why it fails:**

- **[OBS, verify_jury.py:12-18, verbatim]** "N draws on ONE model are N CORRELATED samples — they measure
  the model's VARIANCE, not INDEPENDENT error." So a same-model jury **cannot catch a systematically-bad
  map extraction** — if the cheap worker mis-read a unit, N more draws of the same cheap worker mis-read it
  the same way, unanimously and confidently (SEM-3 measured exactly this: a rename false-positived
  high-confidence; "high" carried no signal).
- **[OBS, SEM-3 §1.4] The ONLY leg that catches a confidently-wrong cheap extraction is a judge that
  doesn't share its blind spots — a *different/stronger* model.** That is SEM-3's keystone, and the reduce
  IS that stronger layer. So the reduce's ADJUDICATE leg is **not** "run N draws of the worker"; it is
  **"the strong synth re-reads the suspect unit's *source* (a targeted re-map at the strong tier) and
  confirms or rejects the cheap extraction."**

> **[idea] The adjudicate leg = the strong reduce model, reading the map's structured output, with the
> power to re-query a unit it distrusts.** `run_jury`'s value is the *verdict-rule call-shape*
> (`cognition.py:707`: `list[draw] → verdict`) — which `verify_jury.py:16-18` *explicitly designed to
> accept a 2nd-model/cloud tiebreak*. So reuse the **shape** (a deterministic rule folding draws), but the
> draws that matter come from *different tiers* (cheap-map extraction vs strong-reduce re-read), not N of
> the same cheap model. The "jury" becomes a **cross-tier panel**, which is SEM-3's "weak judges, strong
> panel" cascade — and that is the only form of jury that adjudicates rather than measuring variance.

This also gives the **re-query mechanism for free**: the adjudicate leg distrusting a unit *is* a targeted
re-map of that unit at a higher tier — the same DECIDE-NEXT machinery (§5), pointed at one unit.

---

## 4 · The staging threshold — a real number, decided at COMPILE, per-face (hard-mechanic #1)

The anchor §7.3 leaves "a 400-file digest may exceed one synth-model context" abstract. I made it a number,
and the answer reframes *when* the decision is made.

### 4.1 The real numbers (measured this session)

- **Synth (reduce) context.** [OBS, `ops/services.json:59`] the resident worker is `max_model_len: 65536`
  (factsheet: effectively ~32K usable at real concurrency, `BENCHMARK_FACTSHEET:13`). A **strong cloud
  synth** (the substitutes-for-me tier the anchor §4 names) is ~200K. So the reduce window is **~32-65K
  (local synth) to ~200K (cloud synth).**
- **Per-unit digest size is a property of the declared `map_schema`** — and it varies by *two orders of
  magnitude* across faces:
  - **coherence-scan** map output = `check.py`'s `{contradicts: bool, note: str}` — [VERIFIED, estimated]
    ~50-150 tokens/unit. 400 files × ~120 tok ≈ **48K tokens** → fits ONE *cloud* synth call comfortably;
    borderline/overflow on the *local* 4B synth.
  - **research-wave** map output = a deep per-area companion — [VERIFIED, measured the real artefacts]
    `SEM-3` = 9,160 tok, `SEM-4` = 10,536 tok. Just **6 companions ≈ 60K tokens** — already at the local
    synth's ceiling, which is *exactly why the round I am reading was reduced by a strong cloud model, not
    the 4B.* At 400 deep units this is ~4M tokens — far past any single context.

### 4.2 The reframe: staging is COMPILE-derived, not a runtime guess

> **[idea, grounded] "Is the reduce one call or staged?" is a *derived property of the chain config*,
> computed at COMPILE time from `n_units × per_unit_digest_tokens` vs `synth_context`.** The compiler
> already emits the `map_schema` (anchor §3); the map schema's expected output size × the unit-count is a
> prediction the compiler can make *before the map spends a token*. So:
>
> ```
> staged := (n_units × est_digest_tokens(map_schema))  >  (synth_context − reduce_prompt − headroom)
> ```
>
> - coherence-scan with a tiny `{contradicts, note}` schema → thousands of units fit one call → **never
>   staged** (and the cloud synth makes the threshold even higher).
> - research-wave with deep companions → tens of units overflow → **always staged.**

This makes staging **per-face and predictable**, and it links COMPILE→REDUCE concretely: the inspect-approve
gate (anchor §2) can *show* "this will be a single reduce / a 2-level hierarchical reduce over ~K clusters"
before spending. [EXT] LangChain's `collapse_documents_chain` uses exactly this "group until under
`token_max`, recurse" loop with a default 3000-token group and an explicit buffer for the summary — the
prior-art confirms the threshold is a token-budget computation, not a heuristic.

### 4.3 Hierarchical reduce is in TENSION with the JOIN — and that's the real hazard (not lost-in-the-middle alone)

The anchor §7.3 frames the staging risk as "lost-in-the-middle returns at the top." The deeper hazard is
**the JOIN, not the summarization**:

> **[INF, my central argument] Hierarchical reduce clusters units to fit context — and a cross-cluster pair
> only meets at a summarized ancestor, where the detail the JOIN needs has been abstracted away.** The
> *clustering objective* silently decides which units are co-visible to a single reduce node. So a generic
> tree (build-once, embedding-clustered — [EXT] RAPTOR's recursive embed→cluster→summarize) optimizes a
> *different* objective than the chain's *specific* JOIN intent.

The direction is **not uniformly adversarial** — be precise:
- For **built-twice** (concept wears divergent names), embedding-clustering *helps*: semantic similarity
  surfaces the duplicate pair into the same cluster *despite* divergent surface names — which is exactly
  why SEM-4 said built-twice discovery is *blocked on embedding-clustering that has no in-Company home*. A
  similarity tree is the right tree for that join.
- For a pair the similarity tree happens to **split** (two files that are a half-migration but read
  dissimilar), the JOIN is lost at the top — the abstracted summaries don't carry the line-level evidence
  the adjudication needs.

**[EXT] The resolution is in the prior art I read, and it is two mechanisms:**
1. **ToM (Tree-oriented MapReduce, arXiv 2511.00489)** propagates `{key_info, rationale, answer,
   confidence}` up the tree and **resolves conflicts/consensus at each parent node** — so pair-relevant
   detail and contradictions survive the ascent instead of being summarized flat. The reduce nodes do not
   pass *prose summaries* up; they pass *structured records with confidence*, and the parent adjudicates.
   This is the same shape as the Company's typed-record discipline (the `json_schema` transport,
   `transport.py:47`) — so it composes natively.
2. **The pairing pre-stage (§2.3)** sidesteps clustering entirely for the hardest joins: a structurally- or
   embedding-surfaced *pair* is handed to the reduce as a 2-unit input — it never depends on co-visibility
   in the tree.

> **[idea] Conclusion: the clustering must be QUERY-DEPENDENT — a function of the reduce's join intent — not
> a generic build-once tree.** The compiler (which holds the `reduce_prompt`/join intent) should emit the
> clustering policy *with* the chain: similarity-cluster for built-twice, structural-pair for half-migration,
> arbitrary-balanced for a pure summarize/onboard (where there is no cross-unit join to protect). And the
> ascending records carry ToM-style `{key_info, confidence}`, not lossy prose, so the parent reduce can
> still join. A generic RAPTOR tree is the right default *only for the join-free faces.*

---

## 5 · DECIDE-NEXT — the driver's rule over the reduce's output, NOT an agentic controller (and not the compiler's)

The anchor §7 asks whether decide-next is the reduce's job or the compiler's. **[idea] Neither — and the
in-idiom answer reuses what exists and avoids the thing Tim's framework rejects.**

- **[EXT] The external prior art is genuinely agentic** — ReAct/Self-RAG/agentic-RAG make the *model* the
  controller that decides retrieve-again-or-stop in a reason-act loop. **But that is precisely the
  agent-as-default the Company rejects** (memory: *not-agent-architecture-by-default* — "LLM use defaults
  to content/variable-resolution dataflow, NOT an agent deciding to act"). Importing an agentic controller
  would be the wrong idiom.
- **[OBS] The Company idiom is already in the engine:** `INJECTION_RULE` (`cognition.py:160`) is *a declared
  L2 rule routing over a model's structured output* — the model produced the judgment, a **pure rule made
  the decision**. Generalize that from intra-turn injection to **pass-sequencing**:

> **[idea] The reduce emits a structured self-assessment field inside its role call — e.g.
> `{answer, status: done | needs_remap | needs_drill, targets:[unit-ids], ...}` — and a DECLARED rule
> routes the next pass.** The model produces the judgment (it's good at "do I have enough to answer this");
> a pure rule reads `status` and either concludes (status=done → COMPOSE the final result) or loops back to
> a *targeted* map over `targets` (the conditional loop that makes it a query engine, anchor §2). The loop
> machinery itself is **AREA-4's** (the burn-down/retry-cap/halt-loud governor) — decide-next is *not* new
> orchestration, it is AREA-4's loop with the reduce's `status` as the worklist signal.

This cleanly splits the three roles: the **reduce model** judges sufficiency (a content judgment), a
**declared rule** decides the next pass (L2 routing), the **compiler** only set the *possible* passes in
the chain config (`passes: single-map | map→pair→map | map→reduce→drill`, anchor §3) — it does not decide
at runtime which fires. So decide-next is **the driver's rule over the reduce's output**, bounded by the
compiler's declared pass-plan, run by AREA-4's loop. No agentic controller enters.

---

## 6 · FOLLOWUP cost — make it FAIL-SAFE so reliability matters less (hard-mechanic #2)

The anchor §7.4: a followup answerable-from-warm-digest = cheap re-reduce; needs-un-extracted-data =
targeted re-map; "the engine must know which — a small smart judgment — how reliable?" **[idea] Reframe so
the reliability of that judgment stops being load-bearing:**

1. **The two errors are asymmetric, so bias the safe way.** A wrong "answerable" → a *wrong answer* (bad,
   reaches the user). A wrong "needs-remap" → *a wasted cheap map pass* (just slower). [OBS, AREA-3's law]
   "over-call is the safe direction." So the judgment should **bias toward re-map** — the cost of being
   wrong is bounded and cheap, not a wrong answer.
2. **Fold the judgment INTO the adjudicate gate (§3), don't build a separate fragile classifier.**

> **[idea] The followup-routing signal is a byproduct of the adjudicate/verify leg: if the reduce cannot
> cite supporting digest units for its proposed answer, *that absence of citation is the re-map signal.***
> A reduce that must ground its answer in named units (the provenance the map already stamps — every
> `run://<turn>/<unit>` is addressed) either finds the support in the warm digest (→ cheap re-reduce) or
> finds it absent (→ the data wasn't extracted → targeted re-map). So "answerable vs needs-data" is not a
> separate smart judgment at all — it is **"can the reduce cite its answer from the digest,"** which the
> adjudicate gate is checking anyway. Reliability of a standalone classifier becomes irrelevant; the
> grounding requirement *is* the router, and it fails safe (no citation → re-map, never → confident
> ungrounded answer).

[EXT] This matches the agentic-RAG literature's own guidance — loops help when "the first retrieval returns
partial information requiring verification," and Self-RAG's core move is *critiquing its own output for
factual support*. The Company form is: make the support-citation mandatory and let its absence drive the
loop, rather than training/trusting a separate decide-to-retrieve model.

---

## 7 · Is the reduce one call or itself staged? — the synthesis

Pulling §4-§6 together, the reduce is **one of three shapes, chosen at compile from the config**, never a
fixed pipeline:

```
SINGLE REDUCE      digest fits synth context (coherence-scan / small corpora / cloud synth)
                   → one strong-model call: JOIN + ADJUDICATE + COMPOSE in one pass, decide-next rule reads status

HIERARCHICAL       digest overflows (research-wave / large corpora / local synth)
REDUCE             → query-dependent clustering (§4.3) → reduce each cluster to a ToM-style
                     {key_info, rationale, confidence} record → reduce the records (parent adjudicates
                     conflicts) → COMPOSE. The JOIN is protected by (a) the pairing pre-stage for the
                     hardest pairs and (b) confidence-carrying structured ascent, NOT lossy prose summaries.

QUERY/AGENTIC      decide-next fires: reduce status=needs_remap/needs_drill → AREA-4 loop → targeted
LOOP               re-map over named units → re-reduce over the (now warm + augmented) digest. The
                   conditional loop that makes it a query engine, governed by AREA-4 (retry-cap, halt-loud).
```

**[INF] The staging is a property of `map_schema × n_units vs synth_context`; the loop is a property of the
reduce's `status` field; the clustering is a property of the `reduce_prompt`'s join intent.** All three are
*derivable from the declared chain config* — which is the corpus-chain's whole point (anchor §3: the chain
is a typed object). So the reduce is **not one call and not a fixed staged pipeline — it is a config-derived
shape**, and the compiler can predict which shape before the map spends.

---

## 8 · Everywhere it connects + what needs building (the map Tim asked for)

**Connects to:**
- **`run_swarm`/`run_role` (`cognition.py`)** — the map half (proven). The reduce reuses `run_role` *iff*
  the §2.1 ctx→messages seam is generalized.
- **`run_jury` + `verify_jury.py`** — donates its *verdict-rule call-shape* to the cross-tier adjudicate
  panel (§3); does NOT donate its same-model semantics (SEM-3 keystone).
- **The `reduce-tree` archetype (`suite.py:1474`)** — the declared-but-dead slot the reduce fills; building
  the reduce is *wiring `join`/`render_from` to a real synth call*, not inventing a new shape.
- **The G3 rule engine (`cognition.py:160`, `runtime/rules.py`)** — donates the decide-next pattern (a
  declared rule over a model output → routes the next pass).
- **AREA-4's loop** — owns the decide-next machinery (burn-down, retry-cap, halt-loud); the reduce's
  `status` is its worklist signal.
- **SEM-3 / SEM-4** — the adjudicate keystone and the disagreement-JOIN are *my area's* trust-floor and
  highest-value worked instance respectively.
- **The model registry + cost shape (anchor §4)** — the reduce is the *strong/cloud* tier; the staging
  threshold (§4.1) is a function of *which* synth tier is bound, so the registry choice changes the
  one-call-vs-staged line.

**Needs building (ordered, minimal delta):**
1. **The generalized `run_role` ctx→messages seam** (§2.1) — reads `role.input_addresses`, resolves each
   ref → a message block. *The* unblocking change; shared with SEM-1. Without it, no reduce role can be fed
   a digest at all.
2. **A `reduce`/`join` role + a `compose` role** (the missing role files) — declared like `check.py`, fed
   the digest via #1, schema = the synthesis/answer shape. Wires the dead `reduce-tree` archetype to a real
   call.
3. **The compile-time staging predictor** (§4.2) — `n_units × est_digest_tokens(map_schema) vs synth_ctx`
   → single | hierarchical, surfaced at the inspect-approve gate.
4. **The query-dependent clustering policy** (§4.3) — emitted by the compiler with the chain; ToM-style
   confidence-carrying ascent + the pairing pre-stage for the hardest joins.
5. **The cross-tier adjudicate panel** (§3) — reuse `verify_jury`'s verdict-shape with *different-tier*
   draws; re-query a distrusted unit = a targeted re-map.
6. **The decide-next status field + routing rule** (§5) — over AREA-4's loop.
7. **The grounded-citation requirement** (§6) — makes followup-routing a byproduct of adjudication, fail-safe.

Items 2-7 are thin compositions over existing primitives. Item 1 is the one real engine change, and it is
the same change SEM-1 named — they meet on it.

---

## 9 · The honest "yes, but actually…" list (where I corrected the anchor)

- **§6 "it IS `run_swarm` … `run_jury`'s slot is the reduce's adjudicate leg."** *Yes for the MAP, no for
  the REDUCE.* The map is proven; **the reduce's central job (JOIN) has no mechanism, the `reduce-tree`
  archetype is declared-but-dead (`suite.py:1474`, never read at runtime, no reduce role file), and the
  live "reduce" is a deterministic injection rule, not a strong-model synthesis.** The reduce is the build.
- **§6 `run_jury` = the adjudicate leg.** *No.* `run_jury` is N draws of *one* role on *one* input —
  variance over a single unit, not cross-unit reasoning, and (SEM-3 + `verify_jury.py:12-18`) same-model
  draws **cannot** catch a systematically-wrong extraction. The adjudicate leg needs a *different/stronger*
  tier — SEM-3's keystone — using `run_jury`'s call-*shape* but cross-tier draws.
- **§7.3 "the reduce must be hierarchical or lost-in-the-middle returns."** *Yes, but the deeper hazard is
  the JOIN, not the summarization* — hierarchical reduce makes a cross-cluster pair meet only at a
  summarized ancestor; the clustering objective silently decides co-visibility. **The clustering must be
  query-dependent** (similarity for built-twice — which *helps*; structural-pairing for half-migration —
  which *sidesteps the tree*), with ToM-style confidence-carrying structured ascent, not lossy prose.
- **§7 "is decide-next the reduce's job or the compiler's?"** *Neither* — it's **the driver's declared rule
  over the reduce's `status` output**, bounded by the compiler's pass-plan, run by AREA-4's loop. The
  external agentic-controller pattern is the wrong idiom (it's the agent-as-default the Company rejects).
- **§7.4 "the engine must know answerable-vs-remap — how reliable?"** *Make it fail-safe so reliability
  doesn't matter* — bias toward re-map (cheap, bounded error), and fold the judgment into the adjudicate
  gate: **no citable digest support ⇒ re-map.** Not a separate fragile classifier.
- **§4 "the smart layer only touches small structured inputs."** *True, but staging is the catch* — measured
  numbers (§4.1): a research-wave digest of 6 deep companions is already ~60K tokens (why this round used a
  cloud synth, not the 4B). Whether the smart layer's input *stays* small is a compile-time computation
  (`map_schema × n_units vs synth_ctx`), not an assumption.

---

## 10 · One-paragraph synthesis for the cross-read

The corpus-chain's MAP (`run_swarm`/`run_role`) is real and proven, but **the REDUCE — the strong layer the
anchor calls the heavy lifter — is the least-built stage of the engine: its central job, cross-unit JOIN,
has no mechanism in the code, the `reduce-tree` archetype that names it is declared-but-dead
(`suite.py:1474`, its `join`/`render_from` never read, no reduce role file), and what the live system calls
"reduce" is a deterministic injection rule, not a strong-model synthesis.** `run_jury` is not the JOIN
(it's N draws of one role on one input — intra-unit variance, and SEM-3 + `verify_jury.py:12-18` prove
same-model draws can't catch a systematically-wrong extraction). So the reduce is the build, and it reuses
existing primitives re-pointed: the JOIN and the adjudicate leg are both blocked on the *one* net-new seam
SEM-1 also named — generalize `run_role` to read `role.input_addresses` instead of a hardcoded
`ctx["utterance"]`. The adjudicate leg inherits SEM-3's keystone (a *different/stronger* tier re-reading a
distrusted unit), reusing `run_jury`'s verdict-shape with cross-tier draws. The staging threshold is a real,
measured, **compile-time** computation (`n_units × est_digest_tokens(map_schema) vs synth_context` — a
`{contradicts,note}` coherence-scan fits one call for thousands of units; six ~10K-token research companions
already overflow the local synth), and the hard part of going hierarchical is not lost-in-the-middle but
**the JOIN**: a cross-cluster pair meets only at a summarized ancestor, so clustering must be
*query-dependent* (similarity helps built-twice, structural-pairing sidesteps the tree for half-migration)
with ToM-style confidence-carrying structured ascent rather than lossy prose. Decide-next is the driver's
declared rule over the reduce's `status` field (not an agentic controller — the Company rejects agent-as-
default), bounded by the compiler's pass-plan and run by AREA-4's loop, and followup-routing is made
fail-safe by folding it into the adjudicate gate (no citable digest support ⇒ targeted re-map, never a
confident ungrounded answer). So the reduce is **not one call and not a fixed pipeline — it is a
config-derived shape** (single | hierarchical | query-loop) the compiler can predict before the map spends,
and the disagreement meta-finding (SEM-4's `structural-wired ∧ semantic-meaningless`, already live as the
3/82) is the worked proof that the highest-value output of the whole system is exactly a reduce-stage JOIN.

— *CC-4. The fact to carry forward: the reduce is the unbuilt stage; the map is proven. Build the
`run_role` input-seam, a reduce role, and a compile-time staging predictor, and re-point `run_jury`'s shape
into a cross-tier adjudicate panel — and the corpus-chain's heavy lifter becomes real.*

Sources (external prior art): [RAPTOR (arXiv 2401.18059)](https://arxiv.org/abs/2401.18059) ·
[Tree-oriented MapReduce / ToM (arXiv 2511.00489)](https://arxiv.org/html/2511.00489v1) ·
[LLM×MapReduce (ACL 2025)](https://aclanthology.org/2025.acl-long.1341.pdf) ·
[LangChain map-reduce/collapse summarization](https://python.langchain.com/docs/how_to/summarize_map_reduce/) ·
[Agentic RAG vs classic RAG control loop](https://towardsdatascience.com/agentic-rag-vs-classic-rag-from-a-pipeline-to-a-control-loop/) ·
[Self-RAG / agentic retrieval taxonomy (arXiv 2603.07379)](https://arxiv.org/html/2603.07379v1)
