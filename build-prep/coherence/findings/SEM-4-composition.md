# SEM-4 — How the two detector classes compose into ONE coherence finding-model

> Companion to `../SEMANTIC-LAYER-ANCHOR.md` (read §3, §8) and to the grounded
> `../COHERENCE-SUBSTRATE.md`. My allocated area is the **composition**: how a STRUCTURAL finding
> (exact, deterministic, auto-actable) and a SEMANTIC finding (a 4B-swarm candidate, fuzzy,
> positive-only, never auto-acted) live in *one* finding-model — the same `{kind, address, state,
> disposition, evidence}` substrate the structural round already decided — without the cheap fuzzy
> class corroding the trustworthy exact one.
>
> This is **not** a detector doc (what the swarm checks — that's a sibling SEM area) and **not** the
> substrate doc (where a finding is stored — that's `AREA-1`). It is the *join*: the record shape that
> carries both classes, the confirm-path that promotes a candidate before it can act, the
> disagreement-as-finding (the anchor §8 what-if, which I argue is the single highest-value thing the
> semantic class adds), the own/reflect split *at the semantic level* (where it bends), and how
> `AREA-4`'s loop consumes a model with both classes.
>
> Marking convention: **[OBS]** observed in code (`file:line`) · **[INF]** inferred from the code,
> not executed · **[your-idea]** my net-new proposal · **[external]** prior art. The hardest line I
> hold: the composition must be *positive-only by construction* — not by a rule someone remembers to
> follow, but by the shape of the record and the lanes it can move through.

---

## 0 · The headline (read this first)

The composition is **smaller than it looks and the discipline is load-bearing in exactly one place.**
Five claims, each grounded below:

1. **The schema delta is +1 discriminator and +1 semantic-only field.** A finding is the AREA-1 record
   `{kind, finding, target, also, state, evidence, owner, seq}` (`AREA-1` §6) **plus `source:
   structural | semantic`** and a semantic-only **`confidence`**. Nothing else. `evidence` is *already*
   polymorphic — structural fills it with an AST reach-result (`file:line`), semantic fills it with the
   swarm's schema-enforced JSON + the jury's `distinct_signatures`/verdict. One field tells the
   confirm-path which lane the finding is allowed to travel; the model is otherwise one shape. **[your-idea, grounded]**

2. **Positive-only is not a rule — it is which LEG the class is allowed to be.** `AREA-3` proved the
   trustworthy graph is a *directional* hybrid: static **PROPOSES** the candidate-dead set; the registry
   and the event-log may only ever **DEMOTE** it; *nothing declares an edge dead from absence*
   (`AREA-3` §0, the three-leg discipline). The semantic class composes into that exact frame as a
   fourth, deliberately **propose-only** leg: **semantic may ADD a candidate; it may NEVER demote, close,
   or "confirm-live" a structural finding.** A 4B "looks fine" is *absence-of-concern* — and absence
   never clears anything in this codebase's discipline — so it is **discarded, never recorded.** A 4B
   "looks wrong" is an additive candidate. This is the keystone, and it is *composed*, not bolted on.

3. **Structural↔semantic disagreement is a read-time-DERIVED meta-finding, and it is the spine.** When
   structural says "wired" and semantic says "this is only referenced by an obsolete test" — the
   disagreement is the highest-value finding (it is precisely the meaning neither class catches alone).
   It is **not a new stored object**: it is re-derived from the two source-tagged findings at one target,
   so it keeps the own/reflect split (nothing new is owned). And it is the *only* clean place a 4B is
   allowed to touch a structural verdict — not by demoting it (forbidden, claim 2), but by *raising a
   conflict candidate for a stronger judge*. This connects directly to the **3/82 measured false-wires**
   (`AREA-3` §0) — they are live disagreement candidates today. **[your-idea, grounded in AREA-3]**

4. **The confirm-path has two distinct levels, and they must not be conflated.** Jury agreement (the
   `run_jury` N-draws→verdict pattern, `cognition.py:637-715`) raises a candidate's *quality* — but a
   unanimous 4B jury is **still a candidate**; agreement never crosses propose→act. **Promotion to
   actionable is a separate act** by a stronger authority (a Claude Code agent, or Tim), recorded as an
   *owned disposition event*. The asymmetry `AREA-4` will tempt you into: its "closure = re-run the
   detector" rule **does not transfer to semantic** — a 4B "looks fine now" cannot close a finding
   (positive-only again). Semantic findings close **only** by the confirming authority, never by a swarm
   re-read.

5. **The loop discriminates by DISPOSITION, not by SOURCE.** `AREA-4`'s existing rule
   `if disposition.action != "finish": continue` (`AREA-4` §2) already absorbs both classes for free.
   The invariant that makes this safe: **a semantic finding is *born* with `action != finish`; only a
   confirmation event rewrites it.** So the loop ideally never reads `source` at all — `source` governs
   the *confirm-path*, not the *act-path*. An unconfirmed semantic candidate is an **unsettled input**
   (the cognition rule-engine's "fires only when every input is settled" property, `COHERENCE-SUBSTRATE`
   §4) → the loop *skips it, without stalling and without thrash*. **[your-idea, grounded]**

The one-line version: **one record shape, one discriminator field; the discriminator decides which
lane a finding may travel, never whether it is real; semantic adds only candidates, its single power
over the structural skeleton is to raise a disagreement for a stronger judge, and the loop reads the
disposition the confirm-path produced — never the source.**

---

## 1 · The finding-record shape that carries both classes

### 1.1 The base record (decided by the structural round — reuse, do not re-invent)

`AREA-1` §6 grounded the structural finding-record on the **already-address-stamped event log**
(`Suite._emit`, `suite.py:497` — every emit carries `address=`, enforced by `event_address_acceptance`).
The detection life is an event:

```
store.append_event({                      # LIFE 1 — detection (re-derivable, reflects-never-owns)
    kind:    "coherence.finding",
    finding: "unwired-route",             # the finding-TYPE (a finding_types registry row)
    target:  "code://bridge/api_knobs",   # rides an EXISTING scheme (no coherence:// — AREA-1 §5)
    also:    "ui://config/knobs",         # the surface that SHOULD consume it
    state:   "built-no-caller",
    evidence:"reachability(): no caller in canvas/app/src or tests/",
    owner:   "interface-stream",
    seq:     <monotonic, from append_event>
}, address="code://bridge/api_knobs")
```

### 1.2 The delta — exactly two fields **[your-idea, grounded]**

```
    source:     "structural" | "semantic"   # +1 DISCRIMINATOR — the whole composition hinges on this
    confidence: <float 0..1>                 # SEMANTIC-ONLY — DERIVED from the jury, never owned (§4.4)
```

That is the entire schema change. Why this is sufficient, field by field:

| field | structural fills it with | semantic fills it with |
|---|---|---|
| `finding` (type) | `unwired-route`, `stale-symbol`, `uncovered-capability` (registry rows) | `half-migration`, `intent-impl-drift`, `concept-built-twice`, `doc-contradiction` (registry rows — same registry, anchor §8: "a semantic finding-type is a declared role + a schema + a prompt") |
| `target` | a `code://`/`ui://` address (an AST symbol, a surface) | the **same** address space — the swarm reads a module + its self-description and anchors the finding to the `code://` symbol it judged |
| `state` | a closed-vocabulary structural state (`built-no-caller`) | a closed-vocabulary semantic state (`new-claims-old-lifecycle-dropped`, `docstring-contradicts-impl`) — declared per finding-type, same fail-loud `set_status` discipline (`governance.py`) |
| `evidence` | **an AST reach-result** — `code-edges.json` reach + `file:line` (`AREA-1` §7, `codeedges.py reach()`) | **the swarm's schema-enforced JSON** (the `json_schema` decode branch the swarm already produces, anchor §7) + the jury's `signatures`/`distinct_signatures`/`verdict` (`cognition.py:704-714`) — so the candidate carries *what it judged and how varied the draws were*, not an opaque score |
| `owner` | the stream/registry that owns the target | same |
| `seq` | monotonic event seq | same |

**The crucial property: `evidence` is already polymorphic, so the two classes do NOT need divergent
record shapes — they need divergent *evidence contents*.** A structural finding's evidence is a
traceable reach result a human can verify by reading code; a semantic finding's evidence is the
swarm's structured judgment a human can verify by reading the draws. Both are *queryable*, both are
*falsifiable* — and the record is one shape. This is the build-on-not-beside answer for SEM-4:
**the structural finding-record needs +1 discriminator and +1 derived field to carry the semantic
class — no second store, no second schema, no parallel model.** **[INF — grounds on AREA-1 §6 +
the json_schema branch the anchor cites]**

### 1.3 Why `confidence` is *derived*, not *owned* (the own/reflect tie-in)

`confidence` is **not** a stored ground-truth number — it is read off the jury result that lives in
`evidence`. `run_jury` returns a `JuryResult` carrying `signatures`, `distinct_signatures`, and the
`verdict` (`cognition.py:700-707`). A candidate's confidence is a *pure function of that result*
(e.g. `agreeing_draws / draws`, or `1 - distinct_signatures/draws`) — so re-running the swarm
re-derives it, exactly as the structural reach-result is re-derivable. **It rides the reflect side of
the own/reflect split: never maintained, always recomputed from the detection.** The only owned
number anywhere in a finding's life is in the *disposition* (§4) — never in detection. **[your-idea,
grounded in cognition.py:700-707 + COHERENCE-SUBSTRATE §2]**

---

## 2 · Positive-only, composed into AREA-3's directional discipline (the keystone)

This is the section that makes the composition *safe*. The temptation is to write "semantic findings
are candidate-only" as a standalone rule. It is much stronger — and much harder to violate by
accident — when it is expressed as **a leg in the directional hybrid `AREA-3` already proved.**

### 2.1 The directional frame `AREA-3` established **[OBS — AREA-3 §0, §3]**

```
Leg A — AST static     PROPOSES the candidate-dead set    (cheap; may over-call dead — the SAFE direction)
Leg B — the registry   DEMOTES the registry-explained     (truth by construction)
Leg C — the event log   DEMOTES the runtime-confirmed-live  (positive-only: a seen edge proves it; absence proves NOTHING)
       → the REMAINDER is the trustworthy "real unwired" set the loop may act on
```

The non-negotiable discipline, verbatim from `AREA-3`: *static may over-call dead (safe); registry and
log may only ever demote; **nothing declares an edge dead from absence.**"*

### 2.2 The semantic class is a fourth, **propose-only** leg **[your-idea, grounded]**

```
Leg D — the 4B swarm   PROPOSES a semantic candidate       (fuzzy; may over-flag — the SAFE direction)
                       MAY NEVER demote / close / confirm-live any finding (NOT a demoter)
```

Two halves, and the asymmetry is the whole point:

- **A 4B "looks wrong" → an additive candidate** (a new `source:semantic` finding-event). This is the
  *propose* direction — and like Leg A's static-over-calls-dead, over-flagging is the **safe** failure
  mode, because (claim 5) a candidate is born non-actionable; the worst a false candidate does is sit
  unconfirmed in the lane until a stronger judge discards it. It never sends the loop anywhere.

- **A 4B "looks fine" → DISCARDED, never recorded.** This is the part that *must not* be a demote leg.
  In `AREA-3`'s frame, only the registry (truth-by-construction) and the event-log (a *seen* edge) are
  trusted to demote — because their positive signal is *real*. A 4B's "looks fine" is **absence of
  concern**, which is exactly the thing the discipline forbids from clearing anything. So semantic
  output is **filtered at ingestion**: only the swarm's negative judgments become finding-events; its
  positive judgments are dropped on the floor (logged as a cheap telemetry count for calibration —
  "swarm read 412 modules, flagged 7" — but *never as a finding, never as a demote*). **[your-idea —
  this filter is the mechanical form of the positive-only law; it lives in the detector→finding adapter,
  the same place AREA-4 §3 puts the structural adapter]**

### 2.3 Why this composition is the honest one **[INF]**

`AREA-3` already named *why* the structural class can auto-act and the semantic cannot, in its own
language: the structural legs are trustworthy *because the dynamism is declared, not hidden* (one
`SUITE` singleton, executed registries, a 58%-addressed log — `AREA-3` §0). The 4B has none of those
guarantees — it half-understands code, it is non-deterministic by default (§5), it hallucinates. So
the composition is not "semantic is second-class for politeness"; it is "semantic *cannot earn a
demote-leg's trust*, so by the very discipline that makes the structural graph trustworthy, semantic
is structurally confined to propose-only." The discipline is identical; only the leg differs. **A
single discipline, two classes — that is the composition the task asked for.**

---

## 3 · Disagreement-as-finding — the spine, grounded in the measured 3/82

The anchor §8 asks the killer what-if: *"What if the structural and semantic findings disagree —
structural says 'wired,' semantic says 'this is dead code that's only referenced by an obsolete test'
— and the disagreement itself is the highest-value finding (the thing neither class catches alone)?"*

I argue: **yes — and this is the single most valuable thing the semantic class adds to the structural
model, so it should be the spine of the composition, not a footnote.** It is also the *only* place a
4B is permitted to bear on a structural verdict — and it does so without violating positive-only.

### 3.1 It is already live, measured, today **[OBS — AREA-3 §0]**

`AREA-3` measured it: of 82 routes the gate calls "wired," **at least 3 (~3.7%) are wired only by a
*mention*** — "a test that merely *asserts the route exists*, with no real consumer call-site at all."
Among them: `/api/mockup-feedback` — *the exact route the lead wrongly deleted* (`COHERENCE-SUBSTRATE`
§3). The structural detector cannot see this is fake-wiring, because `route in tests_blob` is true
(`suite.py:7121`, the substring test). **A semantic detector reading that test can judge it obsolete —
that the reference is not a real consumer.** That is the meaning structural is constitutionally blind
to. The 3/82 are not a hypothetical; they are the **first three disagreement findings** waiting to be
generated.

### 3.2 How the disagreement is modeled — a read-time-DERIVED meta-finding **[your-idea, grounded]**

The disagreement is **not a fourth stored thing.** It is re-derived, at read time, from the two
source-tagged findings that share one `target`:

```
DISAGREEMENT(target) := derived when, at one target address, there exist
    a structural finding asserting one state  (e.g. structural reachability: NO finding → "wired")
    AND a semantic finding asserting the contradicting meaning (source:semantic, "consumer-is-obsolete-test")

  → a derived finding:  { finding: "structural-semantic-conflict",
                          source: "derived",
                          target: <the shared address>,
                          evidence: [<the structural reach-result>, <the semantic swarm judgment>],
                          state: "structural=wired · semantic=dead-via-obsolete-test" }
```

Three properties this gives, each grounded:

- **It keeps the own/reflect split (`COHERENCE-SUBSTRATE` §2).** Nothing new is *owned* — the
  disagreement is a **fold over two existing finding-events at the same address**, exactly as the
  burn-down model is a `run_stats`-style read-time rollup (`AREA-1` §3, `suite.py emit_run_record →
  run_stats`). Re-run both detectors, the disagreement re-derives or vanishes. **No maintained
  conflict store.** **[your-idea — composes AREA-1 §3 rollup pattern with the two source-tagged
  events]**

- **It does NOT let semantic demote structural (claim 2 preserved).** The structural "wired" verdict
  is *untouched* — semantic did not flip it, close it, or demote it. It raised an *additive* candidate;
  the *join* of the two surfaces the conflict. So the positive-only discipline holds even at the one
  point where the fuzzy class bears on the exact class. **This is the whole reason disagreement is the
  *right* shape for the conflict** — any design where semantic *overrides* structural would violate §2.

- **It is the highest-priority class for the confirm-path (§4).** A plain semantic candidate at a
  *quiet* address (no structural finding) is low-stakes — it sits until a judge gets to it. A
  *disagreement* means the trustworthy class and the meaning class actively contradict at a consequential
  spot — which is exactly the `/api/mockup-feedback`-deletion failure mode. So a disagreement finding
  **routes to the confirm-path with priority**, and it is the canonical input to the `run_jury`
  2nd-model tiebreak (§4.2). **[INF]**

### 3.3 The two disagreement directions are *not* symmetric **[your-idea]**

- **structural-clean / semantic-flags** (the 3/82 case): structural sees a real edge, semantic judges
  the edge meaningless. **High value** — this is the silent-false-wire class (`AREA-3` §0 names it the
  dangerous direction: "a dead route reading as whole"). Semantic is the *only* detector that can raise
  it. Route to confirm with priority.
- **structural-flags / semantic-clean**: structural calls something unwired, semantic reads it and says
  "this looks intentional/by-design." **This must NOT auto-demote the structural finding** (claim 2 —
  a 4B "looks fine" proves nothing). It may at most attach as a *candidate disposition-reason*
  (anchor §4②: "this looks by-design (internal entry point) — with a reason") that a human/stronger
  agent reads when dispositioning — i.e. it pre-fills the `reason` field a confirmer would otherwise
  type, but **never sets the disposition itself.** The semantic "clean" here is enrichment, not a verdict.

This asymmetry is itself the positive-only law showing through: semantic *adding* a concern is
trustworthy-as-a-candidate; semantic *removing* a concern is forbidden as a verdict and permitted only
as a human-read hint.

---

## 4 · The confirmation flow — two levels, who confirms, how it's recorded

Anchor §3: *"a semantic candidate must be confirmed before it acts."* The grounded answer has **two
distinct levels** that the anchor's prose blurs, and conflating them is the failure mode.

### 4.1 Level 1 — quality (jury agreement), still candidate-only **[OBS — cognition.py:637-715]**

The cognition stream already ships the mechanism: `run_jury` fires N *varied* draws of one role at
`temperature>0` (`cognition.py:639,678`), writes each to a distinct per-draw address
`run://<turn>/<role>#<i>` (`cognition.py:668`), then applies a **pure deterministic `verdict_rule`
over the draws** (`cognition.py:707` — quorum/vote, no model call). It captures `distinct_signatures`
to *prove the draws actually varied* (`cognition.py:704-705,712`).

Applied to a semantic finding: a candidate is raised only if the jury's verdict-rule concurs (e.g. ≥K
of N draws flag the same concern). This **raises the candidate's `confidence`** (§1.3) and filters
flicker — but it is **still a candidate.** Even a unanimous 4B jury does not cross propose→act. The
draws are correlated (one model — `cognition.py:650-651` documents this explicitly: *"N draws on ONE
model are CORRELATED — variance, not independent error"*), so agreement is necessary-not-sufficient
for trust. **Jury agreement is a *noise filter*, not a *confirmation*.** [OBS on the mechanism; INF on
the application]

### 4.2 Level 2 — promotion to actionable (a stronger authority) **[OBS mechanism + your-idea application]**

Crossing propose→act is a *separate act by a stronger judge*. Two confirmers, in escalation order:

- **A stronger Claude Code agent.** The very `verdict_rule` call-shape `run_jury` exposes is documented
  to *"accept a future 2nd-model/cloud tiebreak slotting in"* (`cognition.py:650-651`). **This is the
  hook for the confirmer**: the 4B swarm raises the candidate; a stronger model (a Claude Code agent —
  the same agent that is the loop's worker, `COHERENCE-SUBSTRATE` §3.5) reads the candidate's evidence
  + the actual code and *confirms or discards*. The confirm step is itself a single, cheap, large-model
  judgment over a *pre-narrowed* candidate — not a whole-repo large-model sweep. The economics the
  anchor §2 promises hold: 4B does the bulk fan-out for free; the big model only adjudicates the few
  candidates that cleared the jury.

- **Tim.** Consequential candidates (a disagreement at a high-blast-radius target; a `by-design`
  proposal) escalate to Tim through the *existing* consent gate — `posture(action_class)`
  (`governance.py:56`) → CONFIRM surfaces for the operator (`governance.py:60-75`). This reuses the
  exact machinery `AREA-1` §4 decided: only the consequential disposition (`by-design`) routes through
  the operator gate; the rest are agent-disposable.

### 4.3 How promotion/demotion is recorded — the owned disposition lane **[OBS — AREA-1 §4 + governance.py]**

Promotion is recorded **exactly where structural dispositions are recorded** — there is no separate
semantic lane. `AREA-1` §4 decided: a finding's standing disposition is a **surfaced-*like* record in
the coherence lane** (NOT the operator inbox — the inbox is operator-only and already-drowned,
`governance.py:123-133`), with the pin-overlay last-wins pattern for the mutable state
(`fs_store.append_pin/pin_state_for`, `AREA-1` §3 Pattern B). A confirmation is a disposition event:

```
coherence_disposition.jsonl  (last-wins overlay, keyed §4.5)
  { finding-id, action: "finish", confirmed_by: "claude-code-agent" | "tim",
    confirmed_at, reason, supersedes }            # a micro-ADR (COHERENCE-SUBSTRATE §2)
```

The **promotion** event rewrites `action` from its birth value (`candidate`/`defer`) to `finish` (or
`by-design`). A **demotion** (the confirmer discards the candidate) writes `action: discarded` with a
reason. Both are **owned** — un-recomputable, the one net-new persisted thing (`COHERENCE-SUBSTRATE`
§2). This is the same disposition substrate the structural findings use; **the confirm-path is the only
thing `source` changes** — a structural finding can earn `finish` from a *standing rule*
(`_ORPHAN_ROUTES` `to_wire` tag → auto), a semantic finding can earn `finish` **only** from a
confirmation event. Same lane, different gate to enter it.

### 4.4 How it stays positive-only — the closure asymmetry AREA-4 will tempt you to break **[your-idea, grounded — the catch]**

`AREA-4` §5 establishes for structural findings: **closure = a *separate detector re-run*** ("a finding
closes only when the *detector* agrees, not when the *build* verifies"). This is correct and trustworthy
*for structural* — a re-run of the AST graph deterministically re-checks the edge.

**It does NOT transfer to semantic, and importing it uncritically violates positive-only.** A 4B
"looks fine now" on a re-read is the *forbidden* signal (claim 2: a 4B clearing a concern is the
absence-proves-nothing case). If a semantic finding could close itself by a swarm re-read, the fuzzy
class would have gained a demote power the discipline denies it. So:

> **A semantic finding closes ONLY by the confirming authority (the stronger agent or Tim), recorded as
> an owned `resolved` disposition — NEVER by a swarm re-read.** The re-read may *re-derive the candidate*
> (own/reflect — the detection is reflected), and if the candidate vanishes on re-read that is *evidence*
> the confirmer reads — but the *resolved* state is owned, set by the authority, and survives a re-scan
> (`COHERENCE-SUBSTRATE` §2: "never recompute a disposition — look it up").

This is the cleanest demonstration that the own/reflect split *is* the positive-only enforcement: the
detection (reflected) can flicker and re-derive freely; the disposition (owned) is the only thing that
can say "this is fine" — and only a trusted authority writes it. **The 4B can never write the
own-side.** [your-idea; grounds on AREA-4 §5 + COHERENCE-SUBSTRATE §2 + claim 2]

### 4.5 The dedup-key wrinkle — AREA-1's content-hash is right for structural, WRONG for semantic **[your-idea]**

`AREA-1` §9 proposes keying finding identity on `(kind, target-address, content-hash)` so a duplicate
detection *dedups* rather than forks. **That is right for structural** — a structural finding's content
is deterministic (the same reach-result), so the content-hash is stable across re-runs and a re-detection
collapses onto the same id (and the confirmation stays attached).

**It is wrong for semantic.** A semantic finding's `evidence`/`state` is *prose the 4B generated*, and
even at temperature 0 + schema-constrained, the wording can vary across re-reads (anchor §6.6: "a
sampling LLM is not deterministic by default"). If the dedup key includes the content-hash, **every
re-worded re-read orphans the prior confirmation** — the loop would re-raise the "same" finding as new,
the confirmer's disposition would not attach, and a confirmed-discarded candidate would keep coming
back. That is a cry-wolf generator (anchor §6.1).

> **Fix [your-idea]: semantic findings key the disposition on a COARSE id `(finding-type, target,
> source:semantic)` — NOT the content-hash.** The *content* lives in `evidence` and is allowed to vary
> (it is reflected); the *identity* the confirmation attaches to is coarse and stable, so a confirmed
> disposition survives every re-wording. This is the own/reflect split applied to identity: the owned
> disposition keys on the stable coordinate; the reflected evidence is free to re-derive differently
> each run.

This is a clean correction to a sibling area's proposal, and it is *forced* by the non-determinism the
anchor §6.6 flags — it's the same root cause.

---

## 5 · How AREA-4's loop consumes a model with both classes

The punchline of the whole composition: **the loop discriminates by DISPOSITION, not by SOURCE.**

### 5.1 The existing rule already absorbs both classes **[OBS — AREA-4 §2]**

`AREA-4` §2 grounded the loop's core rule:

```
for finding in open_findings_sorted_by_priority:
    if finding.disposition.action != "finish":  continue   # defer / by-design / candidate → skip, don't stall
    if posture(finding.consequence_class) != AUTO:  surface_for_operator(finding); continue
    if finding.attempts >= RETRY_CAP:  surface_for_operator(finding); continue
    intent = surface_intent_for_finding(finding)           # AREA-4 §3, = surface_intent_at-shaped
    drive_dispatchable(...)                                 # the existing back half, unchanged
```

**Notice: `source` does not appear in this rule.** The loop reads `disposition.action`. So the
composition requires *no change to the loop's act-path* — it requires only that the confirm-path set
`action` correctly per class:

- A **structural** finding earns `action: finish` from a **standing rule** (the `_ORPHAN_ROUTES`
  `to_wire` tag, `suite.py:7098`, promoted to a disposition record per `AREA-1` §7) → auto-actionable,
  exactly today's behaviour.
- A **semantic** finding is **born `action: candidate`** (≠ finish) and earns `action: finish`
  **only** via a §4.2 confirmation event. Until then the loop's first line skips it.

### 5.2 The invariant that makes this safe **[your-idea, grounded]**

> **A semantic finding is born non-actionable (`action != finish`); the ONLY thing that rewrites it to
> `finish` is a confirmation event from a stronger authority.**

Given that invariant, an unconfirmed semantic candidate is, in the cognition rule-engine's terms, an
**unsettled input** — and the engine's settled-or-pruned property (`COHERENCE-SUBSTRATE` §4: "a finding
whose disposition is still pending is simply *not ready* — the loop declines and moves on, without
stalling and without thrash") handles it *for free*. The loop does not need to know *why* a candidate
is unsettled (because it's semantic-and-unconfirmed vs because a human hasn't dispositioned it) — both
are "not ready," both are skipped, neither stalls the burn-down.

**So the ideal is: the loop never reads `source` at all.** `source` governs the confirm-path
(structural → standing rule; semantic → confirmation event); the confirm-path produces the disposition;
the loop reads the disposition. This is the clean separation — and it means the existing `AREA-4` loop
is *already* a both-classes consumer the moment the confirm-path is wired. **[your-idea — composes
AREA-4 §2 with the born-non-actionable invariant]**

### 5.3 The one place the loop *does* care: the disagreement priority **[INF]**

The single exception: the priority *ordering* (`open_findings_sorted_by_priority`, `AREA-4` §3 starts
with `(action=="finish", -age, blast_radius_size)`) should rank a **confirmed disagreement finding**
(§3) highly, because it is the silent-false-wire class `AREA-3` named the dangerous direction. But this
is the *ordering* of already-confirmed `finish` findings — it still does not make the loop act on an
unconfirmed semantic candidate. The discriminator earns its keep in the confirm-path and (lightly) in
the priority sort; never in the act-decision.

### 5.4 What closes, and what surfaces loud **[OBS — AREA-4 §5 + §4.4 above]**

- A **structural** `finish` finding closes by the detector re-run (`AREA-4` §5).
- A **semantic** `finish` finding closes only by the confirming authority's `resolved` disposition
  (§4.4) — never by a swarm re-read.
- A **build-says-done-but-detector-disagrees** (structural) or a
  **confirmer-discarded-but-swarm-keeps-raising** (semantic) is a **loud anomaly**, surfaced to Tim, not
  silently re-queued (`AREA-4` §5; the no-silent-failures law). The coarse dedup key (§4.5) is what
  makes the second one *detectable* — without it, the re-raised candidate looks new and the anomaly is
  invisible.

---

## 6 · Own/reflect at the semantic level — where it bends (and the non-determinism wrinkle)

`COHERENCE-SUBSTRATE` §2 (from `AREA-6`) is the load-bearing split: **reflect the detection, own the
disposition.** At the semantic level it holds — with one wrinkle the structural level didn't have.

### 6.1 What's reflected: the meaning-graph, re-derived cheaply each run **[your-idea, grounded]**

The anchor §2 + §8 imagine the swarm reading the whole repo "in seconds, essentially free." That maps
onto reflect-never-own perfectly: **the semantic meaning-graph is never stored; it is re-derived by
re-running the swarm.** The economics (anchor §2) are *what make this possible* — you can only "reflect,
never own" a detection if re-deriving it is cheap, and a 32-concurrent 4B fan-out is cheap. So the
semantic class is the *most* reflect-able detector class: re-read the corpus, re-emit the candidates,
keep none of the graph.

This is the same property the cognition stream has (`COHERENCE-SUBSTRATE` §10: "reflects-never-owns the
live surface") — a `coherence.*` event branch the FE folds, no owned state (`AREA-1` §8). The semantic
candidates appear and vanish on the live surface as the swarm re-reads; only the confirmed dispositions
persist in front of Tim.

### 6.2 The wrinkle: AREA-6's "re-run → SAME finding" assumed determinism — semantic isn't **[your-idea, grounded in anchor §6.6]**

`AREA-6`'s own/reflect split rests on *"a finding's detection is re-derivable from the code — re-run the
detector on the same tree, get the same finding"* (`COHERENCE-SUBSTRATE` §2). **For structural that is
literally true** (an AST walk is deterministic). **For semantic it is not true by default** — a sampling
LLM re-read can flicker (anchor §6.6: "can the swarm be made reproducible enough… that a semantic
finding is stable across runs, not a flickering ghost?").

So "reflect" at the semantic level needs an extra discipline to be *trustworthy-as-reflected* rather
than *a flickering ghost*:

- **temperature 0** for the routing/judgment draws (`run_role` defaults to `temperature=0.0`,
  `cognition.py:95` — "routing-stable outputs") — the stable read.
- **schema-constrained output** (the `json_schema` decode branch, anchor §7; `run_role`'s
  `schema=role.output_schema`, `cognition.py:116`) — the candidate is a typed record by construction,
  not parsed from prose, so structural variation is bounded to the *field values*, not the *shape*.
- **jury for the candidate that must be stable** (§4.1) — a quorum verdict over varied draws filters
  the residual flicker into a stable yes/no, and `distinct_signatures` *measures* how stable
  (`cognition.py:704`).
- **the coarse dedup key** (§4.5) — so even when the *prose* of the evidence varies across re-reads, the
  *identity* the disposition attaches to is stable. **This is the structural-level "re-run → same
  finding" property recovered at the identity layer, since it can't be recovered at the content layer.**

Net: the own/reflect split survives at the semantic level, but **"reflect" must be re-read at
temperature 0 + schema + jury, and identity must key coarse — because the semantic detection is
re-derivable only *approximately*, and the coarse-keyed owned disposition is what turns an approximate
re-derivation into a stable model.** **[your-idea — this is the SEM-level correction to AREA-6's split,
forced by anchor §6.6]**

### 6.3 What's owned: still only the disposition — and the 4B can never write it

Unchanged from `COHERENCE-SUBSTRATE` §2 and reinforced by §4.4: **the only owned thing is the
confirmed disposition, and the 4B can never write the own-side.** The swarm writes detection-events
(reflected); a stronger authority writes dispositions (owned). This is the structural guarantee that
positive-only holds: the fuzzy class is *mechanically incapable* of writing the one record that says
"this is settled / fine / resolved," because that record is set only through the confirm-path (§4),
which the 4B is not an authority on.

---

## 7 · The composition, in one diagram

```
                       ONE coherence finding-model  (typed · addressed · dispositioned)
                       record: {kind, finding, target, also, state, evidence, owner, seq,
                                source: structural|semantic,  confidence(semantic-only, DERIVED)}

  STRUCTURAL (Legs A/B/C, AREA-3)                         SEMANTIC (Leg D — propose-only)
    AST ⋈ registry ⋈ event-log                              the 4B swarm (run_swarm)
    deterministic · re-run→SAME                             temp0 + schema + jury · re-run→APPROX-same
    evidence = reach-result (file:line)                     evidence = swarm JSON + jury signatures
    PROPOSES dead; registry/log DEMOTE                      PROPOSES a concern; NEVER demotes/clears
    born action via STANDING RULE (auto)                    born action = "candidate" (NON-actionable)
            \                                                      /  "looks fine" → DISCARDED (absence proves nothing)
             \                                                    /
              \                              JOIN at shared target address (read-time, own/reflect)
               \                                    │
                \                          DISAGREEMENT meta-finding (derived, not owned)
                 \                         structural=wired · semantic=obsolete-test  ← the live 3/82
                  \                                 │  highest-value · highest priority to confirm
                   \                                ▼
                    ──────────────▶  CONFIRM-PATH  ◀──────── (the ONLY thing `source` governs)
                       L1 jury agreement      → raises confidence, STILL candidate
                       L2 promotion:          → a stronger Claude Code agent (run_jury 2nd-model hook,
                                                cognition.py:650-651)  OR  Tim (posture()→CONFIRM gate)
                       recorded as an OWNED disposition event (micro-ADR), coarse-keyed (§4.5)
                       semantic CLOSES only here — never by a swarm re-read (§4.4)
                                                │
                                                ▼
                       THE LOOP (AREA-4)  reads disposition.action, NOT source
                       if action != "finish": skip (unsettled input → no stall, no thrash)
                       structural earns finish via standing rule; semantic via a confirmation event
```

---

## 8 · The honest "yes, but actually…" list (where I corrected the anchor and the siblings)

- **Anchor §3 "candidate-only / never auto-acted."** *Yes, but actually* the strong form is not a rule —
  it is **Leg D being propose-only in `AREA-3`'s directional hybrid** (§2), enforced *mechanically* by
  discarding "looks fine" at ingestion and by the 4B being incapable of writing the owned disposition
  (§6.3). State it as composition, not as a slogan, or it will get violated by accident.

- **Anchor §3 "confirmed before it acts" (one step).** *Yes, but actually* it is **two distinct levels**
  (§4): jury agreement (quality, still candidate) and promotion (a stronger authority crosses
  propose→act). Conflating them lets a unanimous-but-wrong 4B jury self-promote.

- **`AREA-4` §5 "closure = re-run the detector."** *Yes for structural, NO for semantic* (§4.4) — a 4B
  re-read can't close a finding without becoming a forbidden demoter. Semantic closes only by the
  confirming authority. Importing AREA-4's closure-check uncritically *breaks positive-only*.

- **`AREA-1` §9 "key identity on (kind, target, content-hash)."** *Yes for structural, NO for semantic*
  (§4.5) — semantic content varies across re-reads (anchor §6.6), so a content-hash key orphans every
  confirmation. Semantic keys coarse: `(finding-type, target, source:semantic)`.

- **`AREA-6` / `COHERENCE-SUBSTRATE` §2 "re-run detector → SAME finding."** *Yes for structural, only
  APPROXIMATELY for semantic* (§6.2) — so "reflect" at the semantic level needs temp0+schema+jury+coarse-key
  to be trustworthy-as-reflected rather than a flickering ghost. The owned, coarse-keyed disposition is
  what turns an approximate re-derivation into a stable model.

- **Anchor §8 "is the disagreement the highest-value finding?"** *Yes — and it is the SPINE* (§3), the
  one place the fuzzy class bears on the exact class, modeled as a read-time-derived meta-finding so
  positive-only and own/reflect both survive, and it is *already live* as the measured 3/82 false-wires.

---

## 9 · One-paragraph synthesis for the cross-read

The two detector classes compose into one finding-model with a **+1-field schema delta** (`source:
structural|semantic` plus a semantic-only, *derived* `confidence`) — `evidence` is already polymorphic
enough to carry an AST reach-result or a schema-enforced swarm judgment, so there is no second store, no
second schema. The composition is kept honest by **expressing positive-only as a leg in `AREA-3`'s
directional hybrid**: the semantic class is a fourth, *propose-only* leg — it may ADD a candidate, never
demote/close/confirm-live, and a 4B "looks fine" is discarded (absence never clears anything), which is
the same discipline that makes the structural legs trustworthy. The single point where the fuzzy class
touches the exact class is **structural↔semantic disagreement** — modeled as a read-time-DERIVED
meta-finding over two source-tagged events at one address (so nothing new is owned and structural is
never demoted), which is the highest-value class the semantic layer adds and is *already live* as the
measured 3/82 false-wires (`/api/mockup-feedback` among them). Confirmation is **two distinct levels** —
jury agreement (raises quality, still candidate; `run_jury` `cognition.py:637-715`) then promotion by a
stronger authority (a Claude Code agent via the documented 2nd-model tiebreak `cognition.py:650-651`, or
Tim via the `posture()→CONFIRM` gate), recorded as an **owned, coarse-keyed disposition** (a micro-ADR);
crucially, a semantic finding **closes only via that authority, never via a swarm re-read** (importing
`AREA-4`'s detector-re-run closure uncritically would break positive-only). The loop **discriminates by
disposition, not source**: a semantic finding is *born non-actionable* and earns `finish` only through a
confirmation event, so `AREA-4`'s existing `if action != "finish": continue` already consumes both
classes — an unconfirmed candidate is an unsettled input the loop skips without stalling. Own/reflect
holds at the semantic level with one bend: the meaning-graph is the *most* reflect-able detector (re-read
the whole repo cheaply, own none of it), but because a sampling LLM re-read is only *approximately*
deterministic, "reflect" requires temp0+schema+jury and the disposition must key *coarse* — the owned,
coarse-keyed disposition is what turns an approximate re-derivation into a stable model, and the 4B is
mechanically incapable of writing that owned side, which is the final guarantee that positive-only holds.
