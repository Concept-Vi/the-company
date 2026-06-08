# The Semantic Layer — the grounded artefact

> **What this is.** The synthesis of the semantic-layer research wave (anchor `SEMANTIC-LAYER-ANCHOR.md` +
> six companions in `findings/SEM-*.md`), written after reading all six whole. Like `COHERENCE-SUBSTRATE.md`
> for the structural round, this is no longer "what if" — the research grounded it in real code, corrected
> the anchor in several places (some with a live empirical probe), and decided the open questions. Not a
> spec — the shared grounded understanding for Tim and the cognition session to shape. The final section
> joins this round to the structural round into one picture, which is the point.
>
> **The one-line version:** a cheap 4B swarm CAN add a *semantic* detector class to the coherence
> substrate — finding the meaning-level incoherence static analysis can't — but it is **a high-recall
> candidate-generator, never an adjudicator**; its trust rests on **a stronger model confirming before
> anything reaches Tim** (not on the mechanisms the anchor proposed); it clears the bar only for
> *surface-consistency* classes, conditionally for *single-module intent*, and **never** for
> *deep-reasoning/lifecycle/dataflow*; and the single highest-value thing the whole two-round effort
> produces is the finding **neither layer can make alone: structural-says-wired ∧ semantic-says-meaningless.**

---

## 1 · The verdict, grounded (and it was tested, not reasoned)

The make-or-break question — *can a 4B judgment be trusted enough to act on, even as a candidate, without
becoming noise that trains Tim to ignore the panel (cry-wolf)?* — was answered by **running the resident 4B
on the canonical `/api/mockup-feedback` half-migration incident** (SEM-3, Verified this session). The real
numbers:

```
canonical half-migration   →  temp-0 ×3 BIT-IDENTICAL, is_half_migration=true, correct reasoning
                               temp-1 jury ×5  →  5/5 true, all correct       ✓ CATCHES the real bug
clean migration (control)   →  3/3 correctly NOT flagged                       ✓ doesn't blindly over-flag
cosmetic rename (control)   →  3/4 correct, 1/4 FALSE-POSITIVE (high conf)     ⚠ ~25% FP on a trivial case
additive change (control)   →  2/4 correct, 2/4 MALFORMED JSON                 ⚠ malformed 2-in-6 at temp>0
```

So the honest answer is **tiered, and both extremes are wrong**: the 4B is *not* "can't judge code" (it
caught the real incident 5/5 with correct reasoning) and *not* "judges code reliably" (it false-positived a
rename and ran off into whitespace). It is a **usable high-recall pre-filter — a router of candidates, never
an adjudicator.** That boundary is the entire design, and it is *exactly* the ceiling the structural round
hit from the other side: Area 3 said the structural graph "flags the candidate, never proves the lifecycle";
the 4B is the same, reached semantically.

## 2 · The trust stack — and why it's NOT the one the anchor sketched

This is the most important correction the round produced, and it was already half-written in the codebase a
session ago. Each proposed trust mechanism, mapped to what it *actually* buys (SEM-3, Observed + Verified):

```
schema-constrained decoding   →  kills MALFORMED output, says NOTHING about TRUTH
                                  (and "structured output creates false confidence" — a clean record
                                   FEELS trustworthy regardless of whether it's right)
same-model jury (run_jury)    →  smooths VARIANCE (flaky draws), USELESS against SYSTEMATIC error
                                  ← the codebase's OWN verify_jury.py:12-18 says this verbatim:
                                    "N draws on ONE model are N CORRELATED samples … variance, not error"
determinism (C0.2)            →  NOT a trust leg at all — it's the ROUTING RULE's property, not the
                                  JUDGMENT's; and temp-0 vs jury pull opposite directions (CATEGORY ERROR)
self-reported confidence      →  VERIFIED-USELESS — the 4B said "high" on both a correct answer AND the
                                  wrong rename; no discriminating signal; never gate on it
stronger-model confirm        →  THE KEYSTONE — the ONLY leg that catches a confidently-wrong 4B finding,
   (a Claude Code agent)          because it's the only judge that doesn't share the 4B's blind spots
positive-only / candidate     →  the FLOOR against auto-action — but does NOT reduce noise VOLUME
```

The load-bearing truth, confirmed independently by **three** companions (SEM-2, SEM-3, SEM-6) and written
into `verify_jury.py` before this round even started: **a same-model swarm measures its own variance, not
its error.** So no amount of 4B voting corrects a systematic 4B mistake — **the stronger-model confirm is
the keystone, not an optional final tier.** The codebase already shaped the slot for it (`verify_jury.py`'s
verdict-rule signature is built to accept a 2nd-model/cloud tiebreak).

And the cheap optimization (SEM-3's idea): the confirm needn't be full Claude Code for every candidate — a
*cheaper second, different small model* as a first filter, escalating only disagreements/high-stakes to a
Claude Code agent. "Weak judges, strong panel," as a cascade.

## 3 · The organizing insight: the two layers CHAIN (find → adjudicate)

SEM-2's sharpest result, and it refines the whole composition: **a 4B is a good adjudicator of a candidate
*pair*, a poor discoverer of one** — and `run_swarm` is a *map* over independent units, not a *join*. So the
structural and semantic layers don't merely coexist; they **chain**:

```
STRUCTURAL layer  →  finds the candidate        (exact, cheap, "these two mechanisms both still referenced")
       │
       ▼  the structural flag becomes the semantic read-unit
SEMANTIC layer    →  adjudicates the candidate   (the 4B judges the PAIR it's handed — its strong mode)
       │
       ▼  positive-only: a candidate, never a verdict
STRONGER MODEL    →  confirms before Tim          (the only systematic-error gate)
```

This is why half-migration and built-twice need a candidate-*pairing* pre-stage the swarm can't do alone:
you don't ask the 4B to *discover* that two things are the same; you let the structural layer surface the
pair, then ask the 4B to *judge* it. (Built-twice *discovery* specifically is blocked on embedding-clustering
that has no in-Company home yet — a real gap, flagged not papered.)

## 4 · The honest tiering — which semantic checks clear the bar, which never do

Grounded in the mechanism analysis + the probe + external prior art ("constrained decoding helps
classification, degrades reasoning"):

```
S1 · CLEARS as a candidate on the 4B alone   (surface-consistency / classification-shaped)
     concept/vocabulary coherence (built-twice) · doc contradiction+staleness ·
     docstring/AGENTS-vs-signature surface match
     trust: schema + variance-jury + positive-only; stronger-model confirm only on the consequential ones
     → these populate the panel cheaply + densely (the bulk enrichment)

S2 · CLEARS ONLY with the stronger-model confirm   (reasoning-shaped, single-locus)
     intent-vs-implementation drift for one module (does the code still do what its docstring CLAIMS)
     the anchor's highest-value detector — and genuinely reasoning, so candidate-only, scoped
     (changed-files/pre-commit, not whole-repo-every-tick, to keep confirm-volume affordable)

S3 · NEVER clears at the 4B, with or without the full stack   (deep / cross-file / dataflow / lifecycle)
     half-migration ADJUDICATION (defect vs by-design retirement) · subtle dataflow/logic ·
     semantic coverage-equivalence
     → don't route through the 4B at all; the 4B candidate is indistinguishable from noise and the only
       thing that could verify it (a strong model) doesn't need the 4B's prompt. Human-or-strong-model only.
```

The S3 verdict, plainly (SEM-3 was asked to say so if true, and it is): **the trust problem is unsolvable for
the deep-reasoning classes using the 4B, even as candidates.** Pretending the 4B contributes there is the
over-claim that would train Tim to distrust the whole panel. This mirrors Area 3 exactly — same ceiling, both
sides.

## 5 · Where cry-wolf actually lives: the confirm tier's economics, not the 4B's throughput

The anchor framed cry-wolf as "noisy findings train Tim to ignore them." True — but the *seat* of it is not
where the anchor implied (SEM-3 + SEM-1 + SEM-5, Verified numbers):

- **Candidate generation is genuinely cheap** — but the corrected numbers are ~**2,241 tok/s aggregate at
  concurrency 32** (plateaus there), not 3,000; ~**14 concurrent** on real source files, not 32; whole-repo
  semantic sweep ~**1–2 minutes**, not "seconds" (reading is prefill-fast; *judging* is the bottleneck). And
  `suite.py` (716KB ≈ 180K tokens) **doesn't fit the 65K context** — the most coherence-critical file needs a
  chunk-and-compose tier (which the cross-file checks need anyway). "Free in a minute, mostly," not "free in
  seconds" — still a huge value set, just honestly priced.
- **The confirm tier is the bottleneck, and it's a *trust* constraint, not just a cost one.** You cannot get
  cheap + high-recall + high-precision-at-Tim's-eyes from the 4B alone. The trust bar is therefore a *joint*
  condition: **(1)** 4B precision high enough that the confirm tier is affordable, **AND (2)** confirm
  precision high enough that what reaches Tim is real. The 4B is the cheap high-recall pre-filter; the
  stronger model is the high-precision gate; the cascade keeps both affordable.

## 6 · It is not a sibling of the cognition swarm — it IS the swarm (build-on, strongest form)

SEM-6's reframe: the semantic detector isn't *like* the cognition swarm — it **is** `run_swarm`, with a repo
artifact as the "utterance" and a finding-schema as the output. `roles/check.py` (`{contradicts, note}`) is
the literal template. Consequences (all Observed): the anchor's "future" what-ifs are mostly *already-built
mechanism* — the `background`/`rollup` activation contexts exist (driver-gated), VRAM contention is already
solved (the sweep fires at the resident 4B over HTTP, loads nothing; the contention is *sweep-vs-cognition-
waves* on one ~14-slot pool, fixable with a polite second slot budget), and a semantic finding-type is just a
**role file the registry already discovers** (finding-types-as-declared-roles, the "more types not more
tools" law). The one real net-new seam (SEM-1): `run_role` hardcodes `ctx["utterance"]` → a file-reading role
needs a generalized ctx→messages mapping (the `input_addresses` schema field exists but is descriptive-only
today). Corrected, the capability still clears the bar.

## 7 · The composition into one model — minimal, and the disagreement is the prize

SEM-4's grounded join. Adding the entire semantic class to the coherence finding-model costs **+1 field**
(`source: structural | semantic`) and one semantic-only *derived* `confidence`. The discipline expresses as a
**propose-only fourth leg** in Area 3's directional demote-only rule: a 4B "looks fine" is *discarded, never
recorded* (not even as a fact); a 4B "looks wrong" is a candidate. **Semantic can never demote structural.**
The loop discriminates by **disposition, not source** — a semantic finding is simply *born non-actionable*,
so the Area 4 loop consumes both classes unchanged. Closure differs by class: a structural finding closes by
re-running its detector; a **semantic finding can only close by the confirming authority** (a swarm re-read
can't close it without becoming a forbidden demoter — SEM-4's correction of Area 4). And semantic dedup keys
*coarse* on `(type, target, source)`, not on a content-hash (prose varies → a hash re-orphans every run).

**The prize — the finding neither layer makes alone** (SEM-4 + SEM-6, the literal join of the two rounds):

> **structural-says-WIRED ∧ semantic-says-MEANINGLESS** — a route that *is* called, by code that on reading
> turns out to be obsolete/vestigial/contradictory. Structure can't see it's meaningless; meaning can't see
> it's wired. The *disagreement between the two layers* is the highest-value finding-type in the whole system,
> and it only exists because both rounds exist.

## 8 · The one durable artefact to build first: a calibration harness

SEM-3's strongest recommendation, and the thing that turns this synthesis's tiering from *reasoned judgment*
into *measurement* — the semantic analog of Area 3's "3 of 82". The labelled eval set **already exists in the
project's own history**, with known ground truth:
- `/status` half-migration (a known true-positive — the 4B catches it, Verified);
- mode-dial-built-twice (a known concept-coherence true-positive);
- `/api/knobs`-on-unexported-module (a known intent-drift true-positive);
- Area 3's 3 measured false-wires (structural truths to check semantic *agreement* against);
- plus deliberate true-negatives (the clean migration / rename / additive cases from the probe).

The harness scores **precision + recall + confirm-tier load per check-class**, so each class ships to the
panel only if its measured numbers clear thresholds Tim sets. **Build this before trusting the layer** — it
reuses `run_jury`'s shape with the eval set as fixed inputs, and it makes the S1/S2/S3 split a number, not an
assertion.

## 9 · The two rounds, joined — one coherence model, two detector classes, one loop

This is the picture the whole effort was for:

```
                              THE COHERENCE MODEL  (one model, typed · addressed · dispositioned)
                                        ▲
        ┌───────────────────────────────┴────────────────────────────────┐
   STRUCTURAL detectors                                          SEMANTIC detectors
   (round 1 — built/near-plan)                                  (round 2 — this)
   AST · registry · call-graph · string                         the 4B swarm = run_swarm on repo artifacts
   sees WIRING · exact · AUTO-ACTABLE                           sees MEANING · fuzzy · CANDIDATE-ONLY
   FINDS candidates ─────────────────────────────────────────▶ ADJUDICATES the pair it's handed
        │                                                                  │
        │              the highest-value finding lives in the GAP:         │
        └────────▶  structural-WIRED ∧ semantic-MEANINGLESS  ◀─────────────┘
                                        │
                          a stronger model (Claude Code) CONFIRMS the consequential
                                        │
                          the loop (a Claude Code agent) reads the model, acts on
                          structural + CONFIRMED-semantic findings, surfaces the rest;
                          burns down, or halts loud
```

The disciplines are shared and now proven from both sides: **positive-only / demote-only** (structure
proposes-dead but registry+log only demote; semantic proposes-wrong but only a stronger model confirms —
*nothing declares from absence or from a 4B's say-so*); **own/reflect** (re-derive detection cheaply, own
only the disposition); **the stronger-model/human as the systematic-error gate**; and **the calibration
number** as what makes each class trustworthy (Area 3's "3 of 82" for structure; SEM-3's harness for
meaning). Two rounds, one substrate, one loop, one human at the judgment points — which is exactly the
"keep the whole system coherent without humans holding it together" goal, now with *both* the wiring and the
meaning watched.

## 10 · The decisions this puts to Tim + the cognition session

1. **Is the semantic layer worth building, and when?** It's cheap (it's the cognition swarm re-pointed),
   high-leverage (it cracks the classes structure can't), but it depends on the structural substrate existing
   first (it adjudicates structure's candidates) and on the confirm-tier discipline. Sequence question, yours.
2. **The cognition session co-owns this** — it *is* their swarm engine (`run_swarm`, roles, `run_jury`, the
   `json_schema` transport). The one net-new seam (generalized ctx→messages so a role can read a repo artifact)
   is in their code. This wants co-design, not a solo build — posted to them.
3. **The confirm-tier shape** — the cheap-2nd-model → Claude-Code cascade is the trust keystone *and* the cost
   control. Worth deciding deliberately (it's the semantic analog of round 1's standing-grant decision).
4. **Build the calibration harness first** — before trusting any class, measure precision/recall per class on
   the system's own incidents. The one concrete first step both rounds point at.

## 11 · One paragraph for the cross-read

The semantic layer is real, buildable, and mostly already-built mechanism (it *is* the cognition swarm pointed
at the repo) — but it is narrower and differently-shaped than the anchor hoped, and the research proved it by
running the model: a 4B is a **high-recall candidate-generator, never an adjudicator**, trustworthy only for
surface-consistency classes on the 4B alone, conditionally for single-module intent with a stronger-model
confirm, and **never** for deep-reasoning/lifecycle/dataflow (the same ceiling structure hit, reached from
meaning's side). The trust stack the anchor sketched was mostly wrong — a same-model jury measures variance
not error (the codebase said so a session ago), determinism is a category error, self-confidence is
useless — and the *only* systematic-error gate is **a stronger model confirming before anything reaches Tim**,
which makes cry-wolf a precision-and-economics problem at that confirm tier, not a throughput problem at the
cheap 4B. Joined to the structural round, it completes the picture: structure finds the candidates and
auto-acts on the exact ones; the swarm adjudicates the fuzzy ones it's handed; their **disagreement —
wired-but-meaningless — is the highest-value finding neither makes alone**; a stronger model confirms the
consequential; and a calibration harness from the system's own named incidents turns every class's
trustworthiness from a judgment into a measured number. Build it that way and the system watches its own
*meaning*, not just its *wiring*, without a human holding it together — and that is the whole point.
