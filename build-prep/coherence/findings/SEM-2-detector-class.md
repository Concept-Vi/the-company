# SEM-2 — The semantic DETECTOR class: what meaning-level checks a 4B swarm can feasibly run, and how far to trust each

> Companion to `SEMANTIC-LAYER-ANCHOR.md`. My area: the anchor's §4① detectors — half-migration,
> intent-vs-implementation drift, concept/vocabulary coherence (the "built-twice" detector),
> documentation contradiction/staleness, semantic coverage mapping. For each: the real repo artifacts
> it reads (grounded in actual files), the prompt/schema shape (the swarm emits schema-enforced JSON),
> the false-positive risk + how positive-only/candidate discipline applies, and an HONEST per-detector
> tiering — **feasible-now / candidate-only / not-reliable** — with the reasoning, the read-unit, and the
> schema. Stress-tested against the two test cases the anchor names: the `/api/mockup-feedback/status`
> half-migration and the mode-dial-built-twice incident.
>
> Evidence marking, per Tim's template:
> **Verified** = I executed/measured it this session. **Observed** = read in the code (file:line).
> **Inferred** = pattern-match, labelled. **External-prior-art** = literature/measured benchmarks.
> **[my idea]** = design proposal, not yet in the code.

---

## 0 · The one-paragraph thesis (read this first)

The single most important thing the structural rounds (AREA-2, AREA-3) and the swarm engine itself force
me to say is this: **a 4B is a good ADJUDICATOR of a candidate pair, and a poor DISCOVERER of one.** Both
test cases prove it. Given the `/api/mockup-feedback/status` handler *and* the `/api/annotations` handler
side by side, a 4B can very plausibly judge "the new store carries no status field; the old one had
`pending→applied→dismissed`" — that is field-presence semantics, the model's home turf. Given the
`MODE_SPECS` declaration *and* the `THOUGHT_SHAPES` declaration in one context, a 4B can plausibly judge
"these describe the same eight modes under different names" — same-concept-different-names is its better
territory. **What it cannot do** — and what `run_swarm` is structurally not shaped to do (cognition.py:554-558:
every role is independent and reads only `ctx.utterance`) — is **surface the pair in the first place** out
of a flat whole-repo fan-out. A blind sweep of 537 markdown files + the code corpus gives you N independent
per-unit reads; it does not discover that `/api/mockup-feedback` and `/api/annotations` are the old and new
of one migration, nor that two role files are two halves of one mode dial. So the honest architecture is
**two-stage**: a candidate-PAIRING pre-stage (structural references à la AREA-3, or embedding clustering)
curates the read-units; the swarm ADJUDICATES them. The per-unit detectors (doc-staleness, shallow
intent-drift) fit the flat swarm directly. The relational detectors (half-migration, concept-coherence) do
**not** without the pre-stage — and that pre-stage is the load-bearing missing piece this file makes
explicit. **This is exactly the composition AREA-3 was reaching for:** it said the structural graph can only
*flag* the half-migration candidate, never *adjudicate* it (AREA-3:333-341). The semantic layer is the thing
that adjudicates the candidate the structural layer flags. That hand-off is the headline of this area.

The second headline is a trust correction with primary-source evidence: the anchor's proposed `run_jury`
trust mechanism (§6.1) does **not** buy correctness, and the code says so itself (verify_jury.py:12-14:
"N draws on ONE model are N CORRELATED samples — they measure the model's VARIANCE, not INDEPENDENT error").
The real backstop is **positive-only + a stronger-model confirm**, not a jury of one model voting with
itself.

---

## 1 · The engine, as it really is (Observed) — and what shape a semantic detector must take to ride it

Before tiering the detectors I have to be precise about the machine they'd run on, because three of its
properties decide what is feasible and what is not.

**`run_swarm` fires INDEPENDENT roles, each reading only its own context (Observed, cognition.py:554-558):**
> "A role is 'ready' iff its declared inputs are available — here every role in `roles` reads only
> `ctx.utterance` (independent), so the whole list is the ready-set."

So the swarm's native shape is: take a list of N read-units, fan them out concurrently bounded by the slot
budget, each writes its validated JSON to `run://<turn>/<role>`, join at the barrier, read every value back
(cognition.py:570-621). It is a **map** over independent units. It is not a join, not a clustering, not a
cross-unit comparison. Any detector that needs to compare *two* units must either (a) be handed both units
already paired in one `ctx`, or (b) run as a pairing pre-stage *outside* the swarm and then feed the pairs
in. This is the architectural fact behind the §0 spine.

**Output is schema-enforced JSON by construction (Observed, transport.py:33-38, run_role:116-117).** A role
declares an `output_schema` (a Pydantic `BaseModel`); `run_role` passes `schema=role.output_schema` into
`complete()`, and `_apply_response_format` turns it into the server-side `response_format`
`{"type":"json_schema","json_schema":{"name": role.id, "schema": <model_json_schema>}}` branch — vLLM ≥0.21
guided/structured-output decoding, with client-side validate-and-retry as the guarantee (transport.py:44-48,
run_role:100-101). **This is huge for the semantic layer's trust story:** a semantic finding is a *typed
record by construction*, not an essay the system must parse a verdict out of. The 4B is constrained to the
finding schema. (`check.py` is the cleanest template — see §3.2.)

**Temperature defaults to 0; juries fire at temperature>0 (Observed, run_role:95, run_jury:639).** This is
the determinism knob. It matters for §6 below, and the subtlety the anchor misses: **temperature 0 buys
determinism, NOT correctness.** A deterministically-wrong 4B judgment is *stably* wrong — it recurs
identically every scan, which is *worse* for cry-wolf than a flickering error, because the operator sees the
same false finding every time and learns to dismiss the whole instrument.

**The jury primitive exists and its own docstring warns it does not give correctness (Observed,
verify_jury.py:12-18, run_jury:637-678).** `run_jury` fires the same role N times at temperature>0 → a pure
deterministic `majority_vote` verdict. The E4 caveat in the file is the load-bearing sentence for §6.1:
> "N draws on ONE model are N CORRELATED samples — they measure the model's VARIANCE, not INDEPENDENT error.
> A jury whose CORRECTNESS truly matters needs MODEL DIVERSITY (a 2nd small model / a cloud tiebreak), not
> just more draws of the same."

So the anchor's "use `run_jury` to clear the trust bar" is half-right at best, and the code already knows it.

---

## 2 · The benchmark claim — recomputed honestly, not just debunked (Verified + External-prior-art)

The anchor's §2 figure is "**~32 concurrent inferences at ~3000 tokens/second**… the entire repo and all
documentation could be read in seconds." The benchmark factsheet (`~/vllm-tests/BENCHMARK_FACTSHEET.md`)
**corrects the specific number** but, read carefully, **supports the conclusion** — which is the more useful
result than either repeating or killing the claim:

- **The 3000 tok/s figure is wrong as stated.** Measured (factsheet:11, :24): best aggregate throughput is
  **2,241 tok/s at concurrency 32** (input concurrency 128 feeding a 32-batch). That is *aggregate across all
  concurrent requests*, not 3000 *per* request — per-request decode is "rock-steady at ~100 tok/s"
  (factsheet:64). So "32 concurrent × 3000 tok/s" overstates by roughly an order of magnitude on the
  generate side.
- **But the semantic workload is PREFILL-bound, and prefill is the cheap part.** A semantic detector reads a
  file + its docstring (a large *input*) and emits a tiny schema-constrained JSON verdict (a small *output*
  — `CheckOut` is `{contradicts: bool, note: str}`, well under 100 tokens). The factsheet's biggest win is
  exactly here: "Prefill throughput **scales sublinearly with length** — 30K tokens prefilled in just over 1
  second… the model's biggest win for RAG / document-QA workloads" (factsheet:45-53). **Reading the repo is
  a document-QA workload, the model's strongest case**, not the decode-bound generation the 3000-tok/s
  framing implies.
- **The honest arithmetic [my idea, grounded in the measured prefill rate].** The corpus is ~537 markdown
  files (Verified: `find … -name "*.md" | wc -l` = 537) plus the code. At ~30K input tokens prefilled per
  ~1.07s on a *single* concurrency-4 stream, and far better aggregate at concurrency 32, a whole-corpus
  *read* (the expensive part being input, which is the model's efficient part) is plausibly a **minute-or-two
  on-demand sweep**, not seconds, and not free-per-token on the generate side. The anchor's *spirit*
  ("whole-repo affordable on demand") survives; its *specific number* does not. **State both.**
- **The contention caveat is real (anchor §6.4).** The 4B is the cognition stream's resident model and the
  `SlotBudget`/`global_vram_gate` machinery (cognition.py:545-553) already reserves R slots so a live
  cognition/chat call never queues behind a swarm. A whole-repo semantic sweep is a *big* swarm; it must run
  under the same budget (on-demand, off the hot path), or it starves the live system. "Free" is only free if
  it yields to the resource manager — which the existing budget gate makes enforceable, not hypothetical.

**Net:** the capability is real enough to build on, at corrected magnitude. Use "whole-repo readable
affordably, on-demand, in a minute-or-two, prefill-bound (the model's strongest workload)" — not "32×3000,
in seconds, free."

---

## 3 · The two-stage architecture every relational detector needs (the load-bearing design point)

This generalizes §0 into the concrete shape the rest of the file assumes.

```
STAGE 1 · PAIRING (outside the swarm)                STAGE 2 · ADJUDICATION (the swarm)
  surfaces CANDIDATE pairs/clusters                    a 4B reads a curated read-unit (the pair) →
  - structural references (AREA-3's graph)             emits a schema-enforced finding
  - shared route/symbol/concept proximity              - per-unit: doc-staleness, shallow intent-drift
  - embedding clustering [net-new home, §5.3]          - relational: half-migration, concept-coherence
  CHEAP, deterministic, no model                       FUZZY, candidate-only, never auto-acts
        └──────────── feeds curated ctx ──────────────────┘
```

- **Per-unit detectors** (doc-staleness, shallow intent-drift) need **no Stage 1** — the read-unit is a
  single file/module, the swarm maps over them directly. These are the feasible-now ones.
- **Relational detectors** (half-migration, concept-coherence/built-twice) are **gated on Stage 1**, because
  the swarm cannot discover the pair. Without a pairing pre-stage they are not buildable on this engine —
  this is the single most important "yes, but actually" of my area.
- **Stage 1 is where the structural layer earns its keep semantically.** AREA-3's three-leg graph already
  produces exactly the candidate sets Stage 2 needs: "both the old (`/api/mockup-feedback`) and the new
  (`/api/annotations`) still have references" is an AREA-3 candidate (AREA-3:335-339). The semantic layer is
  the adjudicator bolted onto the structural flagger. **Build-on-not-beside, cross-class.**

---

## 4 · The detectors, tiered honestly (the core deliverable)

For each: read-unit · what real artifacts it reads · the prompt/schema shape · false-positive risk +
positive-only application · the verdict (feasible-now / candidate-only / not-reliable) with reasoning.

The schema template for every one is `roles/check.py` (Observed) — a Pydantic `BaseModel` + a
`prompt_template` that spells out the JSON fields with an example, flowing through the `json_schema`
server-side branch. I give a concrete Pydantic class per detector in that exact style.

---

### 4.1 · Documentation contradiction + staleness — **FEASIBLE-NOW** (the easiest, highest-confidence one)

**Read-unit:** one markdown/doc file (or one doc-block) + the named artifact it claims to describe. Per-unit
— **no Stage 1 pairing** needed when the doc names a concrete symbol/file/route (the name *is* the pair key).

**Real artifacts it reads (Observed):** the 537-file markdown corpus (Verified count); the `AGENTS.md`
self-descriptions (one per module dir — `runtime/AGENTS.md`, `roles/AGENTS.md`, the repo root `AGENTS.md`);
`MAP.md`'s auto-maintained `<!--REGISTRY-->` block and `STATE.md`'s `<!--SUITES-->` block
(refresh_self_description, suite.py:823-839); the project memory notes (e.g. naming a "deleted file or a
renamed symbol" — anchor §4①). The detector reads the doc's claims against the live `capabilities()`
projection (suite.py:683-767) and the actual file tree.

**Why this is the 4B's home turf:** it is **text-vs-text and text-vs-name-existence** — "this doc says
function `resolve_surfaced` is operator-only; does the codebase still have `resolve_surfaced`, and does its
docstring still say operator-only?" No call-graph, no dataflow. It is the *semantic complement* to the
existing structural `doc_drift()` (AREA-2:855-869), which only checks "is the registry name *present* in the
doc-block"; this checks "is the *prose still true*." That complementarity is precisely the gap the anchor
§1 names ("the structural drift check only asks 'is the suite listed'… It cannot ask 'is the prose still
true'").

**Prompt/schema shape:**
```python
class DocStalenessOut(BaseModel):
    """One doc-claim judged against the named artifact it describes."""
    claim_holds: bool          # does the artifact still match what the doc says?
    drift_kind: str            # "" | "renamed" | "removed" | "behavior-changed" | "contradicts-other-doc"
    note: str                  # one line: what the doc says vs what is true (or "" if it holds)

ROLE = {
  "id": "doc_staleness",
  "prompt_template": (
    "You are the DOC-STALENESS role. You are given (1) a documentation excerpt that makes a claim about a "
    "named code artifact, and (2) the current source of that artifact (or 'ARTIFACT NOT FOUND'). Decide "
    "whether the doc's claim still holds. Return ONLY JSON:\n"
    '  "claim_holds": boolean,\n'
    '  "drift_kind": one of "" | "renamed" | "removed" | "behavior-changed" | "contradicts-other-doc",\n'
    '  "note": one-line explanation (or "" if it holds).\n'
    'Example: {"claim_holds": false, "drift_kind": "removed", "note": "doc references _OLD_ROUTES; symbol gone."}'
  ),
  "output_schema": DocStalenessOut,
  "model_binding": {"requires": ["chat", "json"], "default_model": None},
}
```

**False-positive risk + positive-only:** moderate, and *self-limiting* in the right direction. The dangerous
direction here is a false "claim_holds: false" (cry-wolf) — and the positive-only discipline handles it: a
doc-staleness finding **proposes** "this doc looks stale," never **declares** "this doc IS wrong and I edited
it." It surfaces as a candidate; the disposition (fix the doc / mark by-design / the doc is aspirational) is
owned by a human or a stronger-model confirm. The "contradicts-other-doc" kind is genuinely valuable and
genuinely safe because it is two texts the model holds in one context — pure reading.

**Verdict: FEASIBLE-NOW.** Per-unit, text-vs-text, schema-constrained, positive-only. This is the one to
ship first and the one most likely to earn trust rather than erode it.

---

### 4.2 · Intent-vs-implementation drift — **SPLIT: shallow = FEASIBLE-NOW, deep = NOT-RELIABLE**

The anchor calls this "the highest-value one." It is — and it must be **split into two tiers**, because
treating it monolithically is exactly the over-claim that erodes trust.

**Read-unit:** one module/function + its declared self-description (its docstring, its `AGENTS.md` entry,
the design doc that spawned it). Per-unit — no Stage 1 (the module *is* its own pair with its own doc).

**Real artifacts it reads (Observed):** the docstrings are *dense* in this codebase and are themselves the
self-model — e.g. `judge.py:1-20` declares the role's facet, `check.py:1-12` declares what `check` reads and
when, `bridge.py:1533-1540` declares the `/api/mockup-feedback` contract incl. "status starts 'pending'."
Plus the per-dir `AGENTS.md` constitutions and the design-doc corpus in `build-prep/`.

**Tier A — SHALLOW drift (FEASIBLE-NOW).** "The docstring claims fields/behavior the code visibly does not
have." This is shaped *exactly* like `check.py`'s `CheckOut {contradicts, note}` (forming-answer vs ground)
— here it is docstring-claim vs code-body. Examples a 4B can reliably catch: the docstring says it returns
`{a, b, c}` and the code returns `{a, b}`; the docstring names a parameter the signature dropped; the
docstring says "fires via the swarm" but the role declares no `prompt_template` (the judge's own facet
note). All **surface-readable** — the claim and the contradicting evidence are both literally in the text.

**Tier B — DEEP drift (NOT-RELIABLE).** "The docstring says 'idempotent' / 'exactly-once' / 'fail-loud' /
'no write race' but the code has a subtle race / a silent fallback / a dropped lock." This is the **dataflow
ceiling** the anchor §6.5 names. A 4B cannot reliably trace whether `set_ref` is actually atomic, whether
the `finish_lock` actually covers the right region (cognition.py:564-578), whether a retry path actually
has no counter (the infinite-retry vector AREA-4 found). Asking a 4B to adjudicate a concurrency claim is
asking it to do the thing it is worst at. A "looks fine" here proves nothing (positive-only); a "looks
wrong" here is *low-confidence* and must be demoted to candidate-for-a-stronger-judge, never surfaced to Tim
raw.

**Prompt/schema shape (one role, two confidence tiers via a `depth` field the swarm sets per read-unit):**
```python
class IntentDriftOut(BaseModel):
    """A module's docstring/AGENTS claim judged against its implementation."""
    matches: bool
    drift_class: str       # "" | "missing-field" | "wrong-signature" | "behavior-claim-unverifiable"
    confidence: str        # "high" (surface-readable) | "low" (requires dataflow — DEMOTE to candidate)
    note: str

ROLE = {
  "id": "intent_drift",
  "prompt_template": (
    "You are the INTENT-DRIFT role. You are given a module's DECLARED claim (docstring/AGENTS entry) and "
    "its IMPLEMENTATION. Decide whether the implementation still matches the claim. If the claim is about "
    "concurrency/atomicity/idempotency/ordering that you CANNOT verify by reading alone, set matches=true "
    "ONLY if nothing visibly contradicts it, set confidence='low', and SAY in the note that it needs a "
    "deeper check. Never assert a race exists unless the code visibly shows it. Return ONLY JSON:\n"
    '  "matches": boolean, "drift_class": "" | "missing-field" | "wrong-signature" | '
    '"behavior-claim-unverifiable", "confidence": "high" | "low", "note": one line.'
  ),
  "output_schema": IntentDriftOut,
}
```

**False-positive risk + positive-only:** Tier A low risk (surface-readable, schema-constrained). Tier B
**high risk** — this is the cry-wolf danger zone. The `confidence: "low"` field is the discipline made
machine-legible: low-confidence findings are demoted to candidate-for-stronger-judge by construction, never
surfaced as a real finding. **Make the model declare its own confidence and route on it** — this is the
single most important false-positive control in my area.

**Verdict: SPLIT — Tier A FEASIBLE-NOW (the institutional-memory-keeping value the anchor wants), Tier B
NOT-RELIABLE (dataflow ceiling; candidate-only at best, and honestly mostly out of reach).** The anchor's
"highest-value" claim is true *for Tier A* and is the layer's strongest single justification (keeping the
self-description honest), but it must not be sold as covering deep behavior.

---

### 4.3 · Concept / vocabulary coherence — the "built-twice" detector — **CANDIDATE-ONLY, and GATED on Stage 1**

This is the mode-dial test case. **The adjudication is feasible; the discovery is not a swarm property.**

**Read-unit:** a *cluster* of declarations that Stage 1 has flagged as concept-proximate (e.g. two role
files, two registries, two config blocks). **Fully dependent on Stage 1 pairing** — this detector cannot
exist on the flat swarm alone.

**The test case, grounded (Observed, MERGE-COORDINATION.md:210, :256):** the mode dial was built twice —
the interface session's `MODE_SPECS`/`resolution_spec_for` (what context resolves) and the cognition
session's `THOUGHT_SHAPES`/`shape_for`/`ACTIVATION_ALLOCATION` (shape/grain/staging/cast) were "two halves
of one declaration on the 8 modes," only unified after the fact into one `MODE_REGISTRY` (the join landed at
`c614761`, MERGE-COORDINATION.md:401). These are two *valid* symbols in two files — structurally invisible
as "the same idea built twice" (anchor §1: "Structural analysis sees two valid symbols; it cannot see they
are the same idea built twice").

**Would a concept-coherence sweep have caught it? Honest two-part answer:**
1. **Stage 2 (adjudication): YES, plausibly.** A 4B *given both declarations in one context* and asked "do
   these describe the same underlying concept under different names?" is doing same-concept-different-names
   recognition — its better territory. Both declarations enumerate the same 8 modes; the overlap is strong
   signal a 4B can read.
2. **Stage 1 (discovery): NO, not on the swarm.** The flat swarm reads each role file independently
   (cognition.py:554-558) and would never bring `MODE_SPECS` and `THOUGHT_SHAPES` into one context. Catching
   it requires a pairing pre-stage that says "these two declarations are concept-proximate, adjudicate them."
   The two sessions building them were in *different processes coordinating through a markdown file* — the
   pre-stage would have to cluster across the whole declaration corpus to surface the candidate.

**The Stage 1 pre-filter — and its feasibility gate (§5.3):** the natural pre-filter is **embedding
clustering** — embed every declaration/concept-name, cluster, and flag clusters where ≥2 members live in
different files/sessions. **Verified:** the Company fabric *has* an embeddings transport
(`openai_embeddings_transport`, `complete_embeddings` — transport.py:196-217, client.py:130-157) — the *call
mechanism* exists. But **no embedder is registered** (Verified: `services.json` has no `embed`/`jina`
entry), and there is **no clustering primitive** in `runtime/` or `fabric/` (Verified: grep for
`cluster`/`cosine`/`similarity` hits only unrelated strings). So embeddings are *callable* but the
clustering-for-pairing is **net-new**, with no native home. Per the "found-elsewhere ≠ replacement" law, the
fact that `substrate-mcp` has `cluster_by_embedding`/`search_semantic` is a *separate system* — it INFORMS,
it does not drop in. **This is a real feasibility gate on the built-twice detector, not a detail:** the
detector's whole value rides on a pairing pre-stage that has no in-Company home yet.

**Prompt/schema shape (Stage 2 adjudication):**
```python
class ConceptCoherenceOut(BaseModel):
    """Two+ declarations judged for being the same concept under divergent names."""
    same_concept: bool
    relationship: str    # "" | "two-halves-of-one" | "duplicate" | "divergent-names-same-thing" | "name-collision-diff-concepts"
    shared_evidence: str # what they share (e.g. "both enumerate the same 8 modes")
    note: str
```

**False-positive risk + positive-only:** the adjudication has real false-positive risk (two genuinely
distinct things that *sound* alike — "name-collision-diff-concepts" is the inverse failure). Positive-only
is the backstop: a concept-coherence finding **proposes** "these look like the same idea built twice" and a
human/stronger-model confirms before any unification — exactly how the mode dial was actually resolved
(co-designed after the fact, MERGE-COORDINATION.md:256, not auto-merged).

**Verdict: CANDIDATE-ONLY, and GATED on a net-new Stage-1 pairing primitive.** Stage 2 adjudication is
feasible and would plausibly have caught the mode dial *given the pair*; Stage 1 discovery is the blocker.
Flag the pre-filter dependency loudly — it is the difference between "this detector is buildable" and "this
detector needs a primitive that does not yet exist in the Company."

---

### 4.4 · Half-migration — **CANDIDATE-ONLY (value = adjudicator of the AREA-3-flagged candidate)**

The originating test case, and the cleanest demonstration of the pairing/adjudication spine.

**Read-unit:** the OLD mechanism + the NEW mechanism, paired. **Stage 1 supplies the pair** — and AREA-3
*already produces it* ("both the old and new still have references" is an AREA-3 candidate, AREA-3:335).

**The test case, grounded precisely (Observed — and a CORRECTION to the anchor's framing):** the anchor §1
and §3.5 say the lead "wrongly deleted `/status`." **What is actually observable in the tree is different
and more useful:** the `/api/mockup-feedback/status` handler **still exists right now** at bridge.py:1564,
with the full `pending|applied|dismissed` lifecycle intact (bridge.py:1564-1572, and the `status: "pending"`
write at bridge.py:1559). What happened is a **half-migration with coexistence**: the studio's *in-app*
surface (`Review.tsx`) moved the feedback thread to the annotation store (`/api/annotations`, bridge.py:573)
— and the annotation store has **no status lifecycle**. So the two mechanisms coexist, and the *new* one
silently lacks the `pending→applied→dismissed` lifecycle the *old* one carries. (MERGE-COORDINATION.md:385
confirms the studio "RETIRED" the mockup-feedback route for the in-app surface; AREA-3:110 found the route
reads as dead-but-wired.)

**Why the correction matters for the detector (the consequence to make explicit):** adjudicating
*coexistence + lifecycle-asymmetry* needs **no git-awareness** — the swarm reads both live mechanisms and
compares their record shapes. That is feasible. Detecting a *deletion* would need **diff/history-awareness**
the swarm does not have (it reads the tree, not the git log). So framing it as coexistence (the true,
observable state) makes the detector *more* buildable, not less. **Would a 4B reading both have caught it?
Plausibly YES** — given the two handlers in one context and asked "does the new mechanism carry every
lifecycle state the old one had?", the answer "the annotation store has no `status` field; the feedback path
had `pending|applied|dismissed`" is field-presence semantics, the 4B's strength.

**Prompt/schema shape (Stage 2):**
```python
class HalfMigrationOut(BaseModel):
    """Old vs new mechanism: does the new carry the old's full lifecycle/behavior?"""
    fully_migrated: bool
    dropped: list[str]      # lifecycle states / fields / behaviors present in OLD, absent in NEW
    note: str

ROLE = {
  "id": "half_migration",
  "prompt_template": (
    "You are the HALF-MIGRATION role. You are given an OLD mechanism and a NEW mechanism that appears to "
    "replace it. List any lifecycle states, fields, or behaviors the OLD one has that the NEW one LACKS. "
    "Return ONLY JSON:\n"
    '  "fully_migrated": boolean (true ONLY if the new carries everything the old did),\n'
    '  "dropped": list of strings (states/fields/behaviors lost; [] if none),\n'
    '  "note": one line.\n'
    'Example: {"fully_migrated": false, "dropped": ["pending","applied","dismissed status lifecycle"], '
    '"note": "annotation store has no status field; old feedback path tracked pending->applied->dismissed."}'
  ),
  "output_schema": HalfMigrationOut,
}
```

**False-positive risk + positive-only:** the candidate is supplied by AREA-3 (so the false-positive rate of
*pairing* is the structural layer's, already disciplined). The adjudication's risk is over-claiming a
"dropped" state that was intentionally retired — handled by positive-only: it **proposes** "the new
mechanism looks to have dropped the status lifecycle; is that intentional?" and a human confirms
(by-design / real gap). AREA-3 was explicit this "is NOT a connectivity property… surface it, never
auto-finish" (AREA-3:333-341) — the semantic adjudicator is the surface, the disposition stays human.

**Verdict: CANDIDATE-ONLY — and this is the headline composition.** AREA-3 flags the candidate it cannot
adjudicate; SEM-2 adjudicates it. The `/status` bug that motivated the whole anchor is *plausibly caught* by
the structural-flag → semantic-adjudicate pipeline — "proven by the very bug that motivated it" (anchor
§4①), with the honest caveat that it needs AREA-3's pairing and a human disposition, and is never
auto-acted.

---

### 4.5 · Semantic coverage mapping — **NOT-RELIABLE (the declared-`COVERS` fallback stays the honest answer)**

**Read-unit:** a (suite, capability) pair — Stage 1 supplies the pairing.

**Real artifacts:** the ~118 `*_acceptance.py` suites (free Python that imports and asserts) + the
`capabilities()` projection (suite.py:683-767).

**Why a 4B read is NOT-RELIABLE:** judging whether a suite *actually exercises* a capability requires the
**execution paths the test triggers** — does this `assert`-laden Python actually drive capability C through
its real code path, or does it just import and check a string? That is the deepest dataflow question of all
five detectors, and AREA-2 (Tier 3, AREA-2:271-279) + AREA-3 (AREA-3:344) both already concluded "no clean
machine signal." A 4B reading the test source can *guess* "this test mentions capability C" — but mention is
not exercise (AREA-3:110-113 measured exactly this failure mode for routes: a test asserting a route exists
reads as a consumer of it). So a 4B coverage judgment reproduces the substring-mention false-positive in
semantic clothing.

**What stays honest:** the declared-`COVERS=[...]` constant per suite (AREA-2:276-279) — extend the
declaration pattern to suites, author it honestly, check the set-difference structurally. That is cheap and
trustworthy; the 4B read is not. A 4B might *assist* by *proposing* a draft `COVERS` list for a human to
confirm (candidate-only, an enrichment), but it cannot *be* the coverage detector.

**Schema (if used as a draft-proposer only):**
```python
class CoverageDraftOut(BaseModel):
    likely_covers: list[str]   # capability names this suite PLAUSIBLY exercises (a DRAFT for human confirm)
    note: str
```

**Verdict: NOT-RELIABLE as a detector.** Candidate-only as a *draft-`COVERS` proposer* at best; the real
detector is the declared-`COVERS` structural set-difference. Do not over-claim that the swarm "cracks the
Tier-3 the structural research called not-spec-able" (anchor §4①) — it does not crack it; it can at most
seed a human-authored declaration.

---

## 5 · The trust mechanism, corrected (the make-or-break — anchor §6.1) (Observed + [my idea])

The anchor lists candidate trust mechanisms; the code lets me adjudicate them with evidence rather than
guess.

### 5.1 · The jury (`run_jury`) does NOT buy correctness — the code says so
verify_jury.py:12-18 (quoted §1) is explicit: N draws on one model are **correlated samples measuring
variance, not independent error**. So `run_jury` over the 4B gives you *agreement-among-its-own-samples*,
which catches *high-variance* judgments (the model is unsure) but is *blind* to *confident-and-wrong*
judgments (the deterministically-wrong case). For semantic findings — where the dangerous failure is a
confident false positive — the jury is **necessary-not-sufficient**: it filters the model's noise, it does
not validate its truth. The E4 escape hatch (verify_jury.py:16: "designed so a 2nd-model / cloud tiebreak
can SLOT IN later") is the *real* correctness mechanism, and it is not yet wired.

### 5.2 · Determinism (temperature 0) solves §6.6, NOT §6.1
temperature 0 (run_role:95) gives **stable findings** — identical inputs → identical judgment, so a finding
is not a flickering ghost across scans (anchor §6.6 dissolved). **But a stable wrong finding is worse for
cry-wolf than a flickering one** — the operator sees the same false positive every scan and learns to
dismiss the instrument wholesale. So determinism is a reproducibility win, *not* a trust win. State the two
separately; the anchor conflates them.

### 5.3 · The positive-only + stronger-model-confirm backstop is the real one [my idea, grounded]
The honest trust stack, in order:
1. **Schema constraint** (transport.py:33-38) — the 4B can only emit a typed finding, not a persuasive
   essay. Removes a whole class of "the model talked me into it."
2. **Confidence self-declaration** (§4.2's `confidence` field) — the model routes its own low-confidence
   (dataflow-dependent) judgments to candidate-only by construction.
3. **Positive-only / candidate-only** (the project law) — **no semantic finding auto-acts, ever.** A 4B
   "looks fine" proves nothing; a 4B "looks wrong" is a candidate. This is the backstop the whole layer
   rests on, and it is the *same discipline shape* as AREA-3's positive-only — with the **danger inverted**:
   AREA-3's positive-only guards against false-*dead* (the structural risk); SEM-2's positive-only guards
   against false-*wrong* / cry-wolf (the semantic risk). Same rule, opposite failure mode — worth stating so
   the discipline transfers cleanly.
4. **Stronger-model confirm** — a Claude Code agent (the loop's actual agent, COHERENCE-SUBSTRATE §3.5)
   confirms the *consequential* candidates before they reach Tim. This is the E4 slot-in (§5.1) realized as
   "the big model is the jury's second voice." The cheap 4B fans out the whole-repo read; the expensive
   model adjudicates only the small candidate remainder. **That asymmetry is the economic point of the whole
   layer** — exactly mirroring AREA-3's directional discipline (static proposes cheaply, the trusted leg
   demotes), one class up.

**Make-or-break verdict:** the layer clears the trust bar **only as a candidate-generator feeding a
stronger confirmer**, never as an autonomous actor. The anchor's §6.1 "can you trust a 4B enough to act" has
a clean answer: **no — and you never ask it to act; you ask it to propose, cheaply, at whole-repo scale, and
let positive-only + a stronger model be the floor.** Built that way it is a tool; built as an auto-actor it
is the cry-wolf curiosity the anchor fears.

---

## 6 · The honest summary table (the deliverable, at a glance)

| Detector | Read-unit | Stage-1 pairing? | Verdict | Why |
|---|---|---|---|---|
| **Doc contradiction/staleness** | one doc + named artifact | no (name is the key) | **FEASIBLE-NOW** | text-vs-text + name-existence; the 4B's home turf; semantic complement to structural `doc_drift` |
| **Intent-drift — shallow** | module + its docstring/AGENTS | no | **FEASIBLE-NOW** | surface-readable claim-vs-code; shaped like `check.py`; keeps the self-description honest |
| **Intent-drift — deep** | module + behavior claim | no | **NOT-RELIABLE** | concurrency/atomicity/idempotency = the dataflow ceiling; candidate-only at best, mostly out of reach |
| **Concept-coherence (built-twice)** | cluster of declarations | **YES (net-new embedding-clustering, no in-Company home)** | **CANDIDATE-ONLY, GATED** | adjudication plausible (would've caught the mode dial *given the pair*); discovery is not a swarm property + the pre-filter doesn't exist yet |
| **Half-migration** | old mechanism + new | **YES (AREA-3 supplies it)** | **CANDIDATE-ONLY** | the headline composition: AREA-3 flags, SEM-2 adjudicates; coexistence+lifecycle-asymmetry is feasible (no git-awareness needed); /status plausibly caught |
| **Semantic coverage mapping** | (suite, capability) | yes | **NOT-RELIABLE** | mention ≠ exercise; deepest dataflow question; declared-`COVERS` structural check stays the honest answer; 4B = draft-proposer only |

---

## 7 · Net (the unbiased verdict)

The semantic detector class is **real and worth building — at two of five detectors feasible-now, two
candidate-only-and-gated, one not-reliable** — and the value is unlocked entirely by getting the
architecture and the trust discipline right, not by the throughput claim (which is overstated ~10× on the
generate side but survives at corrected magnitude because the workload is prefill-bound, the model's
strongest case). The organizing truth, proven by both test cases: **a 4B adjudicates a candidate pair well
and discovers one poorly**, and `run_swarm` is a map over independent units, not a join — so every
relational detector (half-migration, built-twice) needs a candidate-PAIRING pre-stage the swarm cannot
provide, and the per-unit detectors (doc-staleness, shallow intent-drift) ride the flat swarm directly. The
half-migration detector is the keystone composition: **AREA-3's structural graph flags the candidate it
explicitly cannot adjudicate; SEM-2's swarm adjudicates it** — and the `/api/mockup-feedback/status` bug
that motivated the whole anchor is *plausibly caught* by that two-class pipeline (with the correction that
it is a live *coexistence + lifecycle-asymmetry*, not a deletion — which makes it *more* buildable, since
adjudicating coexistence needs no git-awareness). The mode-dial-built-twice would *also* plausibly have been
caught — *in adjudication, given the pair* — but its discovery is blocked on an embedding-clustering
pre-filter that has no in-Company home (the fabric can *call* embeddings; nothing clusters; nothing is
registered). And the make-or-break trust answer, corrected against the code's own E4 caveat: the jury does
**not** buy correctness (correlated samples measure variance, not error), determinism buys stable-not-true
findings (worse for cry-wolf), and the only honest floor is **positive-only + a stronger-model confirm** —
the cheap 4B proposes at whole-repo scale, the expensive model adjudicates the small candidate remainder,
nothing semantic ever auto-acts. Built as a candidate-generator under that floor it is a genuine tool that
finds the class structural analysis constitutionally cannot; built as an auto-actor it is the cry-wolf
curiosity the anchor rightly fears.

— *SEM-2, written to leave the idea bigger and more real. The one line to carry forward: a 4B adjudicates a
pair, it does not discover one — so the structural layer's flag is the semantic layer's read-unit.*
