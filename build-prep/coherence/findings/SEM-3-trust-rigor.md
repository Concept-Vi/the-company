# SEM-3 — Trust rigor: can a 4B semantic judgment be trusted enough to ACT on (even as a candidate), and how do you keep semantic findings from becoming noise?

> Companion to `SEMANTIC-LAYER-ANCHOR.md`. This is the **semantic analog of Area 3** — the make-or-break.
> Area 3 proved a *structural* graph can be made trustworthy on this codebase. My question is the
> harder, fuzzier one the anchor §6.1 names as the thing the whole layer collapses on: **a 4B
> half-understands code; it will hallucinate, miss context, over-flag. If its findings are noise, they
> train Tim to ignore them (cry-wolf) and the layer is a curiosity, not a tool.** I was asked to be
> skeptical, not to confirm. I ran the resident 4B on the canonical incident to get real numbers rather
> than reason in the abstract.
>
> **Evidence marking (Tim's template):**
> **Verified** = I executed it this session (real model output, this run).
> **Observed** = read in the code (file:line).
> **Inferred** = pattern-match, labelled as such.
> **External-prior-art** = from the literature.
> **[my idea]** = a design proposal, not yet in the code.

---

## 0 · The one-paragraph verdict (read this first)

**Yes — there is a trust bar a 4B semantic finding can clear *as a candidate*, but it is narrower than
the anchor implies, and the anchor proposes the wrong mechanism to reach it.** The bar is cleared by a
**necessary-but-not-sufficient ladder** where each leg buys exactly one thing and oversold legs are the
trap: schema-constraint kills *malformed* output (format, not truth — Verified it both works and that the
4B still occasionally runs off into junk under it); a same-model jury reduces *variance* (flaky draws) but
**is provably useless against systematic error** — the codebase already says this verbatim
(`verify_jury.py:12-18`, the "E4 epistemic-monoculture caveat"), and my probe shows draws that are
unanimous-and-confident even when borderline-wrong; **the determinism property C0.2 is NOT a trust leg for
a finding at all** — it is a property of the *routing rule* (a pure Python function), explicitly NOT of the
*model's judgment* (`cognition.py:122-127, 168-171`), and the jury *intentionally abandons* determinism
(temp>0) to get varied draws — so invoking it for semantic stability is a category error; the 4B's
**self-reported confidence is Verified-useless** as a filter (it emitted "high" on both the correct
true-positives *and* the wrong rename — no discriminating signal); the **only leg that addresses systematic
4B error is a stronger-model confirm** (a Claude Code agent), which is therefore
the *keystone* of the stack, not an optional tier — and `verify_jury.py:16-18` already designs the slot for
it. The cry-wolf failure is a **precision-at-Tim's-eyes** problem, and the stronger-model-confirm is the
filter that protects his attention — which makes its *economics* load-bearing: the trust bar is
"4B precision high enough that the confirm tier is affordable, AND confirm precision high enough that what
reaches Tim is real." **Empirically (Verified, n small but real): on the canonical half-migration incident
the 4B was bit-stable at temp-0 and 5/5 unanimous-correct at temp-1 with correct reasoning — but on a
trivial true-negative (cosmetic rename) it false-positived 1-in-4 at temp>0, and on an additive case it
emitted malformed JSON 2-in-6.** So: surface-consistency classes (naming, vocab, doc-match) clear the bar
as candidates; single-module intent-drift is borderline (needs the confirm leg); and the deep-reasoning
classes — half-migration lifecycle, dataflow, subtle logic — **never clear at 4B, even with the full
stack**, exactly as Area 3 found their structural twin "is not a connectivity property." The honest shape
is a **three-tier trust ladder, gated by a stronger-model confirm, with positive-only/candidate as the
backstop against auto-action — and a calibration harness built from the real named incidents as the thing
that gives the tiering teeth instead of assertion.**

---

## 1 · The mechanisms that exist, and *exactly* what each one buys (the necessary/not-sufficient ladder)

The anchor lists five candidate trust mechanisms (§6.1). The single most important discipline of this file
is to refuse to let any of them be oversold. Here is each, mapped to what it provably buys and what it
provably does **not**.

### 1.1 Schema-constrained decoding — kills malformed output, NOT wrong output
**Observed.** `fabric/transport.py:28-49` — `_apply_response_format` sets `response_format` to a
server-side `json_schema` (vLLM guided decoding) when `json_schema` is passed, else a bare `json_object`.
**Observed.** `fabric/client.py:54-87` — `complete()` then *also* parses + validates against the Pydantic
schema and **retries on malformed/unparseable/schema-mismatch** with jittered backoff, raising
`FabricError` only after retries exhausted (fail loud, never silent empty). So there are **two** layers:
server-side constrained decoding *and* client-side validate-and-retry.

**Verified (factsheet §5, `~/vllm-tests/BENCHMARK_FACTSHEET.md:83-96`):** `response_format: json_schema`
produces valid, schema-conforming JSON reliably — "Reliable for production."

**Verified (this run):** Even so, the constrained 4B *does* still emit malformed output under load. In my
additive-case probe, **2 of 6 temp>0 draws ran off into a long run of whitespace** after `"confidence":`
(e.g. `{"is_half_migration": false, "confidence":` then ~80 blank lines until max_tokens) — well-formed
*start*, unparseable *whole*. This is exactly the failure `client.py`'s retry layer is built to catch (and
would have caught — I bypassed it by calling the raw endpoint).

**What it buys:** the finding can be a *typed record by construction*, not parsed out of prose (anchor §5 is
right about this). Malformed-JSON hallucination → ~0 after the retry layer.
**What it does NOT buy:** anything about *truth*. A schema guarantees `is_half_migration` is a boolean; it
says nothing about whether that boolean is *correct*.
**External-prior-art (the discriminating nuance):** "Let Me Speak Freely?" (arXiv 2408.02442) finds format
restriction / constrained decoding **hinders reasoning but *enhances classification* accuracy.** This maps
*precisely* onto the tiering below: schema-constraint *helps* the classification-shaped checks (naming,
consistency, doc-match) and can mildly *hurt* the reasoning-shaped ones (logic, dataflow). And a HN/practitioner
thread on the same paper names the exact trap: **"structured outputs create false confidence"** — a clean,
schema-valid record *feels* trustworthy regardless of whether its content is right. That false confidence is
itself a cry-wolf vector: the finding looks authoritative because it is well-typed.

### 1.2 Same-model jury (`run_jury`) — reduces VARIANCE, useless against SYSTEMATIC error
**Observed.** `cognition.py:637-715` — `run_jury` fires N draws of one role at **temperature>0** (default
1.0, line 639) so the draws *vary*, writes each to a distinct `run://<turn>/<role>#i` address, barriers on
all draws, then applies a **pure deterministic `verdict_rule`** (e.g. `majority_vote`, `verify_jury.py:32-45`)
over them. The verdict is L2 — no model call, just counting.

**Observed — and this is the load-bearing admission, already in the codebase:**
`roles/verify_jury.py:12-18`, verbatim:
> "⚠ E4 EPISTEMIC-MONOCULTURE CAVEAT … N draws on ONE model are N CORRELATED samples — they measure the
> model's VARIANCE, not INDEPENDENT error. A jury whose CORRECTNESS truly matters needs MODEL DIVERSITY
> (a 2nd small model / a cloud tiebreak), not just more draws of the same model."

This is the single most important sentence for the trust verdict, and it is *already written by a past
session*. A same-model jury answers "is this model *stable* on this input," not "is this model *right*."

**Verified (this run):** the canonical half-migration probe — 5/5 draws `is_half_migration=true`,
all `confidence=high`, all with correct dropped-lifecycle reasoning. Unanimous-and-correct.
**Verified (this run):** the cosmetic-rename true-negative — 3/4 correct (`false`), **1/4 false-positive**
(`true`, `confidence=high`). The jury would have voted it down (majority 3:1) — so here the jury *did* its
variance-smoothing job. **But** if the *systematic* tilt had been the other way (all draws agreeing on a
wrong answer), the jury would have been confidently, unanimously wrong, and `unanimous=true` would have
*amplified* the false confidence, not corrected it.

**External-prior-art:** "Weak judges, strong panel" (orq.ai) and the agreeableness-bias work (arXiv
2510.11822) both find ensembles help *when the judges have independent error* — and that a panel of the
*same* weak judge does not manufacture independence. Microsoft's LLM-judge variance guidance names
self-bias and recommends *diverse* judges, not more samples of one.

**What it buys:** kills flaky/borderline *variance* — a finding that flickers true/false across runs gets
resolved to the majority. Real value for the "is this a stable finding or a ghost" question.
**What it does NOT buy:** nothing against the 4B's *systematic* blind spots. All N draws share the model's
weaknesses. Unanimity here is correlation, not corroboration.

### 1.3 Determinism (C0.2) — NOT a trust leg for a finding at all (the anchor's category error)
**Observed.** `cognition.py:15-17` defines C0.2: "ROUTING is rule-based + DETERMINISTIC — the rule is a
PURE function of fully-resolved address values (no now()/random/wave-order/partials), so identical
resolved inputs route identically regardless of the order roles finished in." `cognition.py:122-127` +
`168-171` make explicit that this determinism is a property of the **rule evaluator** (`runtime/rules.py`,
a closed grammar, never eval/exec) reading *already-resolved* values — **the model call happens *inside* a
role, *upstream* of the deterministic part.**

**The anchor §6.6 says:** "Can the swarm be made reproducible enough (temperature 0, schema-constrained,
jury-voted) that a semantic finding is stable across runs, not a flickering ghost?" **This is internally
contradictory and a category error, and I have the code to say so:**

1. C0.2 determinism is the routing rule's, **not the judgment's.** The judgment is a `run_role` model output
   (`cognition.py:93-119`). C0.2 says identical *resolved inputs* route identically — it presupposes the
   judgment already happened. It cannot make the judgment itself reproducible.
2. **"temp-0" and "jury-vote" pull in opposite directions.** `run_role` defaults temperature=0 for
   routing-stable single outputs (`cognition.py:95`, `101-103`); `run_jury` *deliberately* sets temp>0 so
   the draws *vary* (`cognition.py:639, 675`). You can have a stable single draw **or** a variance-averaging
   jury — not both at once. The anchor lists them as if they compose; they don't.
3. **Even temp-0 is not bitwise-reproducible under the swarm's own mode.** *(Inferred / External-prior-art,
   one line.)* vLLM continuous batching makes a token's logits depend on the batch it was scheduled with
   (floating-point non-associativity across varying batch composition); the semantic swarm's *whole point*
   is concurrent batching (32-wide). So even a temp-0 semantic draw can differ run-to-run when the batch
   differs. **Verified caveat:** my temp-0 half-migration draws *were* bit-identical (sig `32db42c8` ×3) —
   but that was 3 *sequential* calls to an idle server, not 32 concurrent draws contending in one batch. The
   reproducibility I observed is the easy case, not the swarm's operating condition.
4. **Stability ≠ correctness regardless.** A stably-wrong answer is still wrong. Determinism would buy
   "the ghost doesn't flicker" — it would never buy "the finding is true."

**What it buys:** nothing for a semantic finding's trustworthiness. (It is genuinely load-bearing for the
*routing* — keep it there.)
**What it does NOT buy:** reproducibility of the model's judgment, and certainly not its correctness.
Do not list C0.2 in the semantic trust stack. This is a real "yes, but actually" the anchor handed me.

### 1.4 Stronger-model confirm — the ONLY leg that touches systematic 4B error (the keystone)
**Observed.** `verify_jury.py:16-18` already designs the slot: "The verdict_rule signature below is designed
so a 2nd-model / cloud tiebreak can SLOT IN later: it receives the list of draws (each a dict); a future
build can tag each draw with its `provider` and weight/tiebreak across providers." `cognition.py:649-651`
repeats it as the E4 caveat in `run_jury`'s own docstring. So the codebase already knows model diversity is
the missing leg and has shaped the interface for it.

Because §1.2 establishes that *no amount of same-model voting* corrects systematic 4B error, and §1.3
establishes that determinism does nothing, **the only mechanism in the whole list that can catch a
confidently-wrong 4B finding is a judge that does not share the 4B's blind spots — a stronger model.** In
this system that is a **Claude Code agent** (the anchor §3 + the coherence substrate §3.5 both establish
the Claude Code agent as the confirming/acting layer). So:

> **The stronger-model confirm is not an optional final tier. It is the keystone. It is the *only* leg that
> converts a 4B "looks wrong" into something Tim can trust reaches his eyes for the right reason.**

**What it buys:** the actual error-correction. A 4B candidate that a strong model rejects never reaches Tim.
**What it does NOT buy:** "free in seconds." Every 4B candidate that survives to confirm costs a strong-model
call — see §3, the economics, which is where the cry-wolf problem actually lives.
**[my idea]:** the confirm need not be full Claude Code for every candidate. A *tiered* confirm — a 2nd
*different small model* (the E4 "model diversity" leg) as a cheap first filter, only escalating
disagreements-or-high-stakes to a Claude Code agent — would protect the economics. This is the
"weak judges, strong panel" pattern (orq.ai) applied as a cascade, not a flat panel.

### 1.5 Self-reported confidence / calibration — Verified-useless as a trust filter
**The anchor §6.1 lists "calibration / confidence" as a candidate trust signal.** I have direct, damning
evidence that the 4B's self-reported confidence field **cannot be used to gate findings.**

**Verified (this run):** in my probes, `confidence:"high"` appeared on the *correct* true-positives (the
canonical half-migration, 5/5) **and** on the *wrong* rename false-positive alike. "High" carried **no
discriminating signal** between a right answer and a confidently-wrong one. This is the textbook signature of
an uncalibrated model confidence.

**External-prior-art:** small models are documented as both weak *and* poorly-calibrated judges
(the "weak judges" framing, orq.ai; small-judge unreliability across the LLM-as-judge survey). Self-reported
confidence from a 4B is not a probability; it's a token the model learned to emit, uncorrelated with
correctness on this task.

**What it buys:** nothing usable. **Do NOT gate semantic findings on the model's own confidence field.**
A finding's trust must come from the *external* legs (jury for variance, stronger-model for error), never
from the 4B asserting its own certainty. (Asking for the field is fine for *display* — "the model said
high" — but it must never be a *gate*.)

### 1.6 Positive-only / candidate-only — backstop against AUTO-ACTION, NOT against noise volume
**Observed.** The discipline is real and already two of the project's laws (anchor §3; coherence substrate
§2 own/reflect split; Area 3 §5 directional demote-only). A semantic finding may **propose**, never
**declare** or **auto-act**.

**The subtle point the anchor blurs:** positive-only is a backstop against the *consequence* of a wrong
finding (it can't silently delete a `/status` route), but it does **nothing about the *volume* of wrong
findings reaching Tim.** A layer that proposes 100 candidates of which 60 are noise does not auto-break
anything — but it absolutely trains Tim to ignore the panel. **So positive-only alone does NOT solve
cry-wolf.** Cry-wolf is solved by *precision before Tim's eyes*, which is the confirm leg's job (§1.4), with
positive-only as the floor under it.

---

## 2 · The empirical probe — converting the central claim from reasoning to Verified

The repo measures the 4B's throughput, structured-output, and needle-recall (`BENCHMARK_FACTSHEET.md`) — but
**nothing measures the 4B's reliability on code-semantic judgment.** `verify_jury` is explicitly
*demonstrative* ("NOT in any mode_scope," `verify_jury.py:20`) with a generic claim-checking prompt, never
tested on code. So the anchor's §6.5 "real ceiling on code" was, before this, *unanswered by the repo*. I
ran the experiment the anchor itself proposed (§4①: "would a 4B reading both the mockup-feedback path and the
annotation store have flagged the dropped status lifecycle?").

**Setup (Verified, this session):** resident 4B up at `127.0.0.1:8000`
(`cyankiwi/Qwen3.5-4B-AWQ-4bit`), `response_format: json_schema`, `enable_thinking: false`, faithful
excerpts of the *real* `/api/mockup-feedback` + `/status` JSONL mechanism (`bridge.py:1533-1586`, which
carries the `pending→applied→dismissed` lifecycle) vs the annotation store the FE migrated to (api.ts:192,
Review.tsx:14 say the jsonl is "RETIRED"; `bridge.py:573` the annotation endpoint).

| Probe | Expected | Result | Read |
|---|---|---|---|
| **Canonical half-migration**, temp-0 ×3 | flag it | **bit-identical** (sig `32db42c8` ×3), `is_half_migration=true`, correct dropped-lifecycle reason | **the originating bug is catchable by a 4B** — the anchor's "proven by the very bug that motivated it" holds, *as a candidate* |
| Same, temp-1 jury ×5 | flag it | **5/5 `true`, all `high`, all correct reasoning** (`majority_vote` verdict True, unanimous) | true-positive is robust across draws |
| **Clean migration** (lifecycle preserved), temp-1 ×3 | do NOT flag | 3/3 `is_half_migration=false`, `new_carries=true` | does **not** blindly over-flag every migration |
| **Cosmetic rename** (identical behaviour), temp~0.6 ×4 | do NOT flag | **3/4 `false`, 1/4 `true` (high conf)** | **measured false-positive: 1-in-4 on a trivial case at temp>0** |
| **Additive** (new adds, drops nothing), temp~0.6 ×4 | do NOT flag | 2/4 `false`; **2/4 malformed JSON** (ran off into whitespace) | reasoning *mostly* right; **measured malformed-output: 2-in-6 overall** |

**What this Verified evidence establishes (and its honest limits):**
- **The 4B genuinely can do surface-level migration judgment** — true-positive on the real incident, and it
  correctly *declined* both true-negatives the majority of the time. This is not nothing; it is the empirical
  floor under "a candidate can clear the bar."
- **But the false-positive rate on borderline cases is real and material** — ~25% on the rename at temp>0.
  In a whole-repo sweep over hundreds of files, even a modest FP rate is *exactly* the cry-wolf volume the
  confirm leg must filter — **but note the honest limit: this is 1 false event across 4 draws of ONE
  hand-built rename, a single labelled point, not a measured rate** (the per-class rate needs the §5
  harness). The jury smoothed this one (3:1) — but the jury cannot smooth
  a *systematic* tilt (§1.2), and a rename being flagged is a *systematic* over-eagerness, not random noise.
- **Malformed output is a live ~2-in-6 event** at temp>0 even under schema constraint — vindicating the
  `client.py` retry layer as non-optional infrastructure, not belt-and-suspenders.
- **n is small.** This is a probe, not a benchmark. It is enough to refute "a 4B can't judge code at all" and
  enough to refute "a 4B judges code reliably" — both extremes are wrong. The honest conclusion is *tiered*,
  which §4 spells out, and §5 proposes the harness that would make the tiering rigorous.

**One nuance I must flag honestly:** the half-migration here is *borderline real*. `bridge.py:1564` shows
`/api/mockup-feedback/status` *still exists* in the backend — the lifecycle wasn't deleted from the server,
the **FE** retired the route. So the 4B's "true" is judging "the new in-app surface dropped the status
lifecycle" which is *correct for the FE migration* but would need a human to adjudicate "is the orphaned
backend lifecycle a problem or fine." This is precisely Area 3's verdict on the structural twin: *"the graph
flags the candidate; it cannot adjudicate the migration."* **The 4B is the same — a good candidate-router,
not an adjudicator.** That boundary is the whole design.

---

## 3 · Where cry-wolf actually lives: the economics of the confirm tier

The anchor frames cry-wolf as "noisy findings train Tim to ignore them." True, but the *mechanism* that
prevents it has an economic constraint the anchor doesn't surface:

```
4B swarm  →  N candidates  →  [confirm tier]  →  M survive  →  Tim's eyes
            (cheap, ~free)      (NOT free)         (must be high-precision)
```

- **Verified throughput correction (factsheet:24):** the anchor's "32 concurrent / 3000 tok/s" is **over-
  stated.** Real measured peak is **2,241 tok/s aggregate at concurrency 32**, and aggregate *plateaus* at 32
  (line 30: "Beyond that … throughput stays flat — later requests just wait"). So ~2,250 tok/s, not 3,000,
  and 32 is a ceiling not a midpoint. The 4B *candidate-generation* layer is genuinely cheap. (Cost is not my
  area; I note it only because it sets up the real constraint, which *is* a trust constraint:)
- **The confirm tier is the bottleneck, and it is a trust constraint not just a cost one.** If 4B *precision*
  is low (many candidates are noise — and my §2 rename probe says it's materially nonzero on borderline cases),
  then either (a) every candidate hits the expensive Claude-Code confirm and the "free in seconds" payoff
  erodes into a slow expensive pipeline, or (b) you skip confirm to stay cheap and the noise reaches Tim —
  *(my §2 rename probe is one labelled point suggesting precision on borderline cases is materially below 1;
  the §5 harness is what would turn "materially nonzero" into a per-class number)* —
  cry-wolf. **You cannot have all three of cheap, high-recall, and high-precision-at-Tim's-eyes from the 4B
  alone.**

> **Therefore the trust bar, stated precisely, is a *joint* condition:**
> **(1) 4B precision high enough that the confirm tier is affordable (few enough false candidates to confirm),
> AND (2) confirm precision high enough that what survives to Tim is trustworthy.**
> Neither alone is the bar. The 4B's job is to be a *cheap high-recall pre-filter with tolerable precision*;
> the confirm tier's job is to be the *high-precision gate*. The §1.4 cascade (cheap 2nd-model filter →
> Claude Code only on disagreement/high-stakes) is what keeps both legs of this affordable. **[my idea]**

---

## 4 · The honest tiering — which semantic checks clear the bar, and which NEVER do

This is the semantic analog of Area 3's Tier-1/2/3 split, grounded in §1's mechanism analysis, §2's probe,
and the external prior art. The organizing principle, from "Let Me Speak Freely?" (External-prior-art):
**classification-shaped checks clear; reasoning-shaped checks degrade — and the deepest reasoning never
clears at 4B.**

### Tier S1 — Clears as a candidate on the 4B alone (surface-consistency / classification-shaped)
These are pattern/consistency judgments, the 4B's strong mode, and the ones schema-constraint *helps*:
- **Concept / vocabulary coherence** (the "built-twice" detector — does one concept wear divergent names?).
  Clustering + naming consistency is classification, not reasoning.
- **Documentation contradiction + staleness** (a doc names a deleted file / renamed symbol; two docs
  disagree on a surface fact). Local, checkable, classification-shaped.
- **Docstring/`AGENTS.md`-vs-signature surface match** (does the prose describe the function that's actually
  there *at the surface* — same args, same returns, same named behaviour).
- **Trust mechanism for S1:** schema-constraint (helps here) + a same-model jury for variance-smoothing.
  Positive-only as the floor. **Stronger-model confirm only on the consequential ones** (e.g. before a doc
  edit is *written*). These are the ones that can populate the panel cheaply and densely (anchor §4②, the
  bulk enrichment) without flooding the confirm tier.

### Tier S2 — Borderline; clears ONLY with the stronger-model confirm leg (reasoning-shaped, single-locus)
- **Intent-vs-implementation drift** for a *single module* — "does the implementation still do what the
  docstring/design-doc *claims*," where "claims" includes behaviour, not just signature. This is the
  anchor's highest-value detector (§4①) and it is genuinely reasoning, not classification. My §2 probe is the
  evidence: the 4B got the *clear* migration cases right but false-positived the borderline one 1-in-4.
- **Trust mechanism for S2:** the 4B is a **candidate-generator only**; the finding does **not** reach Tim
  until a stronger model (the cascade of §1.4) confirms it. The jury reduces flicker but is explicitly *not*
  sufficient here (E4). This is where the confirm tier's economics (§3) bite hardest — keep S2 sweeps scoped
  (changed files, pre-commit) rather than whole-repo-every-tick to keep the confirm volume affordable.

### Tier S3 — NEVER clears at 4B, with or without the full stack (deep reasoning / cross-file / dataflow)
This is the tier I was asked to name plainly if the trust problem is unsolvable for some classes. **It is.**
- **Half-migration lifecycle adjudication** — *whether a dropped behaviour is actually a defect* (vs by-design
  retirement). My §2 probe + the `bridge.py:1564` nuance show the 4B can *flag the candidate* but the
  adjudication needs a human-or-strong-model with whole-system context. Area 3 §8 reached the identical
  bound on the structural twin: "NOT a connectivity property … needs a schema diff." Semantically it's the
  same: the 4B asked "does the new carry the old's *full* lifecycle" is doing deep multi-file reasoning, its
  weakest mode, and even a 5/5 unanimous jury (§2) is 5 correlated samples of that weak mode.
- **Subtle dataflow / logic correctness** — "is this value actually propagated," "does this branch ever fire,"
  "is this lock held across the right region." The 4B's context is bounded (§ context-window, anchor §6.2) and
  the reasoning is exactly what constrained decoding *degrades* (External-prior-art). Same-model jury cannot
  fix a systematic logic blind spot.
- **Semantic coverage (does this suite actually *exercise* this capability)** — Area 2/Area 3 already called
  this "no clean machine signal"; semantically it's a deep behavioural-equivalence judgment, S3.
- **Why even the full stack doesn't rescue S3:** the stack's only systematic-error-corrector is the
  stronger-model confirm (§1.4) — but for S3 classes the *stronger model is doing the real work*, the 4B
  candidate adds ~nothing but noise and confirm-cost. So for S3, **don't route through the 4B at all** — these
  are human-or-strong-model-only checks. Pretending the 4B contributes here is the over-claim to resist.

> **The S3 verdict, plainly:** the trust problem is **unsolvable for the deep-reasoning / cross-file /
> lifecycle / dataflow classes using the 4B**, even as candidates, because the 4B's candidate there is
> indistinguishable from noise and the only thing that *could* clear it is the expensive judge that doesn't
> need the 4B's prompt anyway. Keep these human-or-strong-model-only. This mirrors Area 3 exactly: the
> structural graph "flags the candidate, never proves the lifecycle" — the semantic layer has the *same*
> ceiling, reached from the other side.

---

## 5 · The thing that gives the tiering teeth: a calibration harness from the real incidents [my idea]

My §2 probe is n-small. A verdict that stays a probe under-delivers. The move that closes the empirical hole
— and the one durable artefact this area recommends building *before* trusting the layer — is a
**calibration harness**: a labelled eval set drawn from the system's *own named incidents*, scored for
**precision and recall per check-class**, so the S1/S2/S3 tiering is *measured*, not asserted.

The labelled set already exists in the project's history — these are real, with known ground truth:
- **`/status` half-migration** (`bridge.py:1533-1586` + the retired FE) — a known true-positive for the
  half-migration class. (My §2 confirms the 4B flags it.)
- **mode-dial-built-twice** (anchor §1; coherence substrate §3.5) — a known true-positive for the
  concept-coherence class.
- **`/api/knobs` / API-on-unexported-module** (coherence substrate §1.6) — a known true-positive for
  intent-vs-implementation drift.
- **The 3-of-82 false-wires Area 3 measured** (`/api/mockup-feedback`, `/api/scope`, `/api/voice/turn`) —
  known structural truths the semantic layer can be checked against for *agreement* (the anchor §8 "what if
  they disagree" case).
- **Plus deliberate true-negatives** (clean migrations, cosmetic renames, additive changes — the cases I
  hand-built in §2) so precision is measured, not just recall.

**What the harness measures per class:** precision (of the candidates the 4B raises, how many are real),
recall (of the known incidents, how many it catches), and the *confirm-tier load* (how many candidates a
class generates per scan — the §3 economics). **The trust bar (§3) becomes a number per class**: a class
ships to the panel only if its measured precision-after-confirm and confirm-load clear thresholds Tim sets.
This is the semantic analog of Area 3's "3 of 82" — the one number that made its verdict concrete instead of
hand-wavy. **Without this harness, the S1/S2/S3 split is my reasoned judgment; with it, it's a measurement.**
Recommend building it as the first real artefact of any semantic-layer build, reusing `run_jury`'s shape
(`cognition.py:637`) with the eval set as fixed inputs.

---

## 6 · Direct answers to the deliverable questions

1. **Is there a trust bar a 4B semantic finding can clear (as a candidate)?** **Yes, for the
   surface-consistency / classification classes (S1), on the 4B alone with schema + variance-jury +
   positive-only.** **Conditionally yes for single-locus intent-drift (S2), only with a stronger-model
   confirm.** **No for the deep-reasoning / lifecycle / dataflow classes (S3), with or without the full
   stack.** Verified empirically that the 4B catches the canonical half-migration as a candidate (5/5) but
   false-positives borderline cases (~25% on a rename) — so it is a usable *high-recall pre-filter*, never an
   adjudicator.

2. **What is the verification stack that gets a candidate to the bar?**
   `schema-constrain (kills malformed, not wrong) → same-model jury (smooths variance, NOT systematic error)
   → stronger-model confirm (the ONLY systematic-error corrector — the keystone) → positive-only/candidate
   (backstop against auto-action, NOT against volume)`, with the §1.4 **cascade** (cheap 2nd-model filter,
   escalate to Claude Code only on disagreement/high-stakes) protecting the confirm-tier economics that §3
   shows are the real seat of cry-wolf. **Determinism / C0.2 is NOT in this stack** — it's a property of the
   routing rule, not the judgment, and the jury intentionally abandons it (§1.3). The anchor's §6.6 framing
   of determinism-as-trust-mechanism is a category error. **The 4B's self-reported confidence is also NOT
   in the stack** — Verified-uncalibrated (§1.5): it said "high" on both correct and wrong answers, so it
   carries no discriminating signal and must never be a gate.

3. **What can NEVER clear the bar (human-or-strong-model-only)?** Half-migration *adjudication* (vs flagging),
   subtle dataflow/logic correctness, behavioural coverage equivalence — the S3 tier. The 4B's candidate there
   is indistinguishable from noise, and the only thing that could verify it (a strong model) doesn't need the
   4B's prompt. Don't route S3 through the 4B at all.

---

## 7 · The "yes, but actually" list (where I corrected the anchor)

- **"temp-0 + schema + jury-vote → stable, not a flickering ghost" (§6.6)** → *actually* temp-0 and jury
  pull opposite directions; determinism is the *routing rule's*, not the *judgment's* (cognition.py:122-127);
  and stability ≠ correctness anyway. **Determinism is not a semantic trust leg.** (§1.3)
- **"multi-role agreement (`run_jury`) verifies a finding" (§6.1)** → *actually* the codebase's own
  `verify_jury.py:12-18` says same-model draws are *correlated* — a jury smooths *variance*, never
  *systematic* error. Unanimity can amplify a confident wrong answer. (§1.2, Verified)
- **"32 concurrent / 3000 tok/s" (§2)** → *actually* measured **2,241 tok/s at concurrency 32**, plateauing
  there (factsheet:24-30). Candidate-generation is cheap; that's not where the trust constraint is. (§3)
- **"the swarm reads the whole repo's meaning … essentially free" (§3)** → *actually* free *candidate
  generation* is not free *verification*; the confirm tier is the bottleneck, and cry-wolf lives in its
  economics, not in the 4B's throughput. (§3)
- **"positive-only is the backstop" (§3, §6.3)** → *actually* positive-only stops auto-*action*, not finding
  *volume*; it does **not** by itself solve cry-wolf — precision-at-Tim's-eyes (the confirm tier) does. (§1.5)
- **"half-migration detector … proven by the very bug that motivated it" (§4①)** → *actually* Verified the
  4B *flags* the candidate (good), but `bridge.py:1564` shows the backend lifecycle still exists — so the
  *adjudication* (defect or by-design retirement?) is S3, human-or-strong-model-only. Flag, never adjudicate.
  Identical ceiling to Area 3's structural twin, reached from the semantic side.

---

## 8 · Net (the unbiased verdict)

A 4B semantic finding **can** clear a trust bar *as a candidate* — but only for the surface-consistency
classes, only with the right stack, and the right stack is **not** the one the anchor sketches. The anchor's
trust legs are mostly real but each is narrower than stated, and one (determinism) does not belong. The
load-bearing truth, *already written into the codebase a session ago* (`verify_jury.py:12-18`), is that a
same-model swarm measures its own **variance, not its error** — so the **stronger-model confirm is the
keystone, not an optional tier**, and cry-wolf is a **precision-at-Tim's-eyes** problem whose real seat is
the **economics of that confirm tier**, not the 4B's (genuinely cheap, ~2,250 tok/s) candidate generation.
Empirically the 4B is a usable high-recall pre-filter — it caught the canonical half-migration 5/5 and
declined clean true-negatives — but it false-positived a trivial rename 1-in-4 and emitted malformed JSON
2-in-6, so it is a *router of candidates*, never an *adjudicator*. The deep-reasoning / lifecycle / dataflow
classes (S3) **never clear at the 4B, with or without the full stack** — the same ceiling Area 3 found on the
structural side, reached from the other direction — and pretending otherwise is the over-claim that would
train Tim to distrust the panel. The discipline that makes the layer a tool and not a curiosity: **the 4B
proposes (high recall, tolerable precision), schema makes it well-typed, a jury de-flickers it, a *different*
stronger model confirms before Tim ever sees it (the only systematic-error gate), positive-only is the floor,
and a calibration harness built from the system's own named incidents turns the S1/S2/S3 tiering from my
reasoned judgment into a measured number per class.** Build it that way and a 4B semantic finding is a
trustworthy candidate; ship it as "the swarm read the repo and these are the problems," and three confident,
well-typed, unanimous, *wrong* findings will teach Tim to close the panel — and that is the cry-wolf death
the anchor named.

— *SEM-3, written to leave the idea bigger and more real. The one fact to carry forward: a same-model jury
measures variance, not error — so the stronger-model confirm is the keystone, and the trust bar is the
confirm tier's precision-and-economics, not the 4B's throughput. (And the 4B did catch the `/status` bug —
as a candidate.)*
