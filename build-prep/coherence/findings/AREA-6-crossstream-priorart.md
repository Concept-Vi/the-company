# Area 6 — Cross-stream convergence · conceptual prior art · the bigger frame

> Companion to `../ANCHOR.md`. My allocated area is two threads:
> **(1)** is the Coherence model the *same kind of thing* as the cognition stream's live model — could they
> share machinery, or be one substrate with two lenses? **(2)** external prior art on how systems hold
> structural integrity over time, then the anchor's bigger what-ifs (finding-types as a growable registry,
> burn-down-as-institutional-memory, the recursion, the introspective-data law).
>
> Marking convention used throughout:
> **[OBS]** observed in real code (file:line) · **[INF]** inferred from what I read · **[PRIOR-ART]** external
> · **[IDEA]** my own proposal. The line I hold hardest: *the convergence is real in code* is **[OBS]**;
> *they could be one substrate* is **[IDEA]**.
>
> Headline finding, stated once up front so the rest can be read against it:
> **The cognition model and the Coherence model share a real, already-built pattern — but they differ in
> KIND on one axis that turns out to be the whole design. Cognition is per-turn and ephemeral; Coherence is
> whole-system and persistent. The clean synthesis: Coherence should *reflect-never-own its detection* (a
> finding is re-derivable from code, exactly like a cognition turn is re-derivable from a run) but must
> *own its disposition* (the by-design judgment is NOT recomputable — it is a decision). That own/reflect
> split is the load-bearing distinction, and it wires Thread 1 straight into Thread 2: a disposition is a
> micro-ADR, the one piece of the model that is institutional memory rather than a derived view.**

---

## THREAD 1 — Cross-stream: is Coherence the same KIND of thing as cognition?

### 1.1 What the cognition stream actually built (grounded, not from the docs' claims)

I read the real engine, not just the build-prep prose. The cognition stream is substantially built and the
shape the anchor §4 gestures at is concretely there:

- **Roles** are a *file-discovered registry* — `runtime/roles.py` `RoleRegistry().discover([_ROLES_DIR])`
  **[OBS roles.py:70-73]**, explicitly mirroring `NodeRegistry.discover` (the node-type library). Adding a
  role = adding a file; it self-registers; a removed file un-registers on rediscover **[OBS roles.py
  docstring 1-13]**. This is the system's "declare data, don't write control-flow" law made physical.
- **Rules** are *declared data-AST*, interpreted by a restricted evaluator that **never** eval/exec/compile
  **[OBS rules.py:9, 133-203]**. The grammar is a closed op-set `RULE_OPS` **[OBS rules.py:65-88]**; the
  whitelist is *structural* — `now`/`random`/`call`/IO literally cannot be expressed because there is no
  such op **[OBS rules.py:13-24]**. A rule is a **pure decision** handed only fully-resolved values; the
  *driver* performs the effect (mirrors gate.py) **[OBS rules.py:25-32]**.
- **Addresses** are `run://<turn>/<role>` throughout; the canonical resolver is `store.head → get_content`,
  with **no parallel resolver** **[OBS cognition.py:473-496, resolve_run_ref]**. Fail-loud on an unresolved
  ref is the default **[OBS cognition.py:491-495]**.
- **The live view** (`CognitionView.tsx`) is *reflects-never-owns*: it issues no writes, reads
  `/api/cognition_info` + the folded live turn, and the River's tributaries come from the turn's `cast[]`
  and the projection's roles — **no hardcoded role list** **[OBS CognitionView.tsx:1-9]**. A new role
  registered engine-side appears in the view with zero FE code **[OBS CognitionView.tsx:6-8]**.
- **The projection** `build_cognition_info` is explicitly *"the sibling of contracts/object_info.py"* —
  where `build_object_info` serializes the NodeType library, `build_cognition_info` serializes the cognition
  registries, both *generated from the registries, never hand-written* **[OBS cognition_info.py:9-21]**.

### 1.2 The convergence is REAL — and most of it is reusable machinery, not analogy

These are the things the Coherence model would need and the cognition stream already proved out. **[OBS]**
on each:

| Coherence needs… | Already built in cognition (file:line) | Reusable as |
|---|---|---|
| A registry projected to the FE, generated not hand-written | `build_cognition_info`, the sibling of `build_object_info` (cognition_info.py:9-21) | **A third sibling: `build_coherence_info`** (see §1.6) |
| Live surface that reads + never owns | `CognitionView.tsx` reflects-never-owns (1-9); SSE `cognition.*` branch | A `CoherenceView` that folds a `coherence.*` event branch |
| An event-kind CONTRACT the FE binds to (not invented) | `COGNITION_EVENT_KINDS` declared as data (cognition_info.py:52-97) | A declared `COHERENCE_EVENT_KINDS` (finding.appeared/resolved/dispositioned) |
| "Declare a check, not code a gate" | `RULE_OPS` closed grammar + declared-AST `Rule` (rules.py:65-88, 298-410) | The disposition/routing half of a finding (see §1.4 — NOT detection) |
| A typed disposition with a reason | `_ORPHAN_ROUTES` tag+note table (suite.py:7017-7054) | **The embryonic finding-disposition store, already in the codebase** |
| Address-anchored, registry-driven, fail-loud | run:// resolver (cognition.py:473-496); drift homes (rules.py:43-46) | The same laws, one more lens |

The single most striking confirmation of the anchor's §3 prediction: **the disposition system the anchor
imagines ("finish / defer / by-design") already exists in embryo.** `Suite._ORPHAN_ROUTES`
**[OBS suite.py:7017-7054]** is a hand-kept table mapping each known orphan route to a `(tag, reason)`:
- `to_build_ui` → "needs a screen — a Claude Design target" (= the anchor's *defer-with-reason*, blocked-on-build)
- `to_wire` → "built, should have an FE caller — a real connect-it item" (= the anchor's *finish*)
- `voice_owned` → "the concurrent voice session's lane" (= *defer*, owned elsewhere)
- `backend_only` → "legitimately no FE — an agent/operator/internal entry point" (= the anchor's *by-design*)

And `reachability()` already does exactly the anchor's "new orphan fails loud, catalogued orphan passes"
**[OBS suite.py:7056-7089]**: `new_orphans` (not in the table) → `all_accounted=False` → gate fails;
`documented` orphans → the gate passes and the table *doubles as the connect-it backlog*; `stale` entries
(now wired) self-correct. **This is the anchor's whole §2 thesis ("from catching drift to holding integrity,
with dispositions") running today, in miniature, for one finding-type.** The Coherence Substrate is, at
minimum, the generalization of `_ORPHAN_ROUTES` from one detector to a registry of them.

### 1.3 But actually — they differ in KIND on the one axis that matters

This is the *but-actually* the anchor §9 asked for. The convergence above is real, but a naive "they're the
same, merge them" would be wrong, and the difference is the design:

**Cognition's model is per-turn and ephemeral. Coherence's model is whole-system and persistent.** **[OBS]**:
- Cognition addresses are `run://<turn>/<role>` — *turn-scoped* **[OBS cognition.py:235, 559]**. The view
  folds **one** live turn (`cognitionTurn`, a single `turn` object) **[OBS CognitionView.tsx:54-58]**.
- A cognition turn is fully *re-derivable*: rerun the swarm on the same utterance + resolved inputs and you
  get the same routing (determinism, C0.2 — identical resolved inputs route identically regardless of finish
  order) **[OBS cognition.py:122-127, 160-176]**. Nothing about a past turn needs to be *kept* to be true;
  it is a pure function of its inputs.
- A Coherence finding's *detection* is likewise re-derivable (re-run reachability on the same tree → same
  orphans). **But a Coherence finding's *disposition* is NOT** — "this orphan is by-design because X" is a
  **decision a human (or a consented agent) made**, and re-running the detector can never recompute *why*.

So the load-bearing distinction is an **own/reflect split** that cognition does not have to make (because
cognition owns nothing — it is pure narration of a turn):

> **[IDEA] Coherence reflects-never-owns its DETECTION (findings are re-derived from the live code, exactly
> as a cognition turn is re-derived from its run) — and OWNS its DISPOSITION (the by-design / defer-with-reason
> judgment, which is not recomputable and must persist).** Detection is a view; disposition is a record.

This resolves three things at once:
1. It satisfies the anchor §7.3 "build-on-not-beside" worry precisely: the *detection* lens rides the
   existing reflects-never-owns + projection machinery (no new store). Only the *dispositions* are net-new
   persisted data — and they ride the **typed structured-record substrate the project already has** (the
   "typed fences" / address-keyed annotation store the anchor §4 names), so even that is build-on.
2. It tells you what survives a re-scan and what doesn't: re-detect freely (cheap, stateless, trustable);
   never recompute a disposition (look it up, it's a decision).
3. It is the bridge to Thread 2: **a disposition is a micro-ADR** (§2.4). The burn-down history is
   institutional memory *because the dispositions are the un-recomputable part.*

### 1.4 What the rules engine teaches Coherence (and where it must stay in its lane)

`rules.py` is the killer evidence for the anchor's §9 what-if "declare a check, don't code a gate." But it is
the **disposition/routing half**, not the detection half — I'm holding the advisor's line here so this doesn't
annex Area C's territory.

- **The closed grammar IS "more types, not more tools."** `RULE_OPS` (rules.py:65-88) + `DESTINATION_KINDS`
  (rules.py:114-126) are a registry; a new routing behaviour is a *declared rule*, not a new bespoke function.
  For Coherence this maps to: a finding's *disposition logic* ("auto-finish iff …", "always surface iff …")
  could be a declared rule over the finding's resolved fields, not hand-coded per finding-type. **[OBS+IDEA]**
- **The `surface` destination is exactly how a finding escalates to the human.** `DESTINATION_KINDS["surface"]`
  routes through the **existing** `Suite.surface_review` → an `ask` event with `resolved=None` — *never a
  resolve* **[OBS rules.py:114-126, 562-572]**. So "this finding needs Tim's disposition" reuses the one
  inbox; it cannot forge an approval. **[OBS]**
- **The unforgeable floor is structural, and Coherence inherits it for free.** No destination is — or may
  ever be — `resolve`/`approve`/`dispatch` (`FORBIDDEN_DESTINATION_VERBS`, asserted in `Rule.__post_init__`)
  **[OBS rules.py:128-130, 313-322]**. This is the anchor §5's "what stops it finishing something the wrong
  way to clear a finding" answered by construction: the Coherence loop can *surface* "I want to finish this"
  but the *resolve/dispatch* is operator-only. The build-wire's consent gate is the same floor.
- **Where it must NOT bleed:** the rule engine evaluates *already-resolved values*. It does not extract the
  connection graph. **Detection rigor — the AST-level real call/route/registry graph — is Area C's make-or-
  break**, and my code-property-graph prior art (§2.2) belongs there. The rule engine is what you do *with*
  a finding once detected, not how you find it. The anchor §7.1 is right that detection is the whole game;
  rules.py does not touch it.

### 1.5 Two concrete teach-acrosses that answer the anchor's hard §5 questions with real code

These are the parts of cognition that are *not* just "same shape" but actually solve open Coherence problems:

**(a) Per-rule readiness → the anti-thrash / blocked-on-human-without-stalling mechanism.**
`Rule.ready(settled)` fires a rule only when **every declared input is *settled*** — `resolved` OR provably
`pruned`/`failed` — and **never on a timeout** (a timeout would re-admit wall-clock = nondeterminism)
**[OBS rules.py:332-342]**. Apply this to the Coherence loop (anchor §5/§7.4 "does it converge, how does it
avoid thrash, how does blocked-on-human not stall"): **[IDEA]** a finding's auto-finish should trigger only
when its inputs are *settled* — including "the disposition is settled" (finish | by-design | defer). A finding
whose disposition is still `pending` (needs Tim) is **not ready** → the loop *declines to act* on it and moves
on, without stalling and without thrash. "Blocked-on-human" is just an unsettled input in the readiness
predicate — it represents naturally, and the loop provably never spins on it. This is a far cleaner answer
than the anchor's tentative "probably needs a notion of net burn-down."

**(b) Determinism → the trust property the autonomous loop requires.**
C0.2: identical resolved inputs route *identically regardless of finish order* **[OBS cognition.py:122-127]**;
the evaluator reads only resolved values, never time/random/order **[OBS rules.py:241-249]**. The Coherence
analogue **[IDEA]**: *identical codebase state → identical findings, regardless of which session built what or
which detector ran first.* This is the property that makes a model "the autonomous loop trusts enough to act
on" (anchor §7.1). It also implies a falsifiable acceptance test for the substrate itself: scan a fixed tree
twice, in two orders, assert byte-identical findings (mirrors how the cognition merge verified the mode-dial
join by a *byte-for-byte before/after dump* — MERGE-COORDINATION §c614761 **[OBS]**).

### 1.6 One-substrate-two-lenses: my recommendation, marked as [IDEA] not [OBS]

The anchor §9 asks "could they be one substrate with two lenses — *how it thinks* and *how whole it is*?"

**[OBS]** the convergence (the table in §1.2) is real and the machinery is genuinely shared.
**[IDEA]** my recommendation is **not** "merge them into one model," but: *build Coherence as an explicit
third sibling lens, on the shared machinery, beside the other two.*

```
contracts/object_info.py     →  build_object_info      ("what node-types exist")      [OBS exists]
contracts/cognition_info.py  →  build_cognition_info   ("how it thinks", per-turn)    [OBS exists]
contracts/coherence_info.py  →  build_coherence_info   ("how whole it is", standing)  [IDEA — net-new sibling]
```

Why a *sibling*, not a *merge* — and this is grounded in something that literally just happened in this very
build, not theory: **the MERGE-COORDINATION log records that "the mode dial was built twice"** — the interface
session's `MODE_SPECS`/`resolution_spec_for` and the cognition session's `THOUGHT_SHAPES`/`shape_for` were two
halves of one declaration, independently built in two sessions, only unified after the fact into `MODE_REGISTRY`
**[OBS MERGE-COORDINATION.md §"the mode dial is built twice", §c614761]**. That is the no-human-developer
disconnection the anchor §1 is *about*, caught in the build of the very system meant to prevent it. The lesson:
**the way to stop Coherence being "the next thing built twice" is to make it an explicit, named sibling lens
from the start** — `build_coherence_info` declared as the third projection, sharing the registry/projection/SSE
pattern, so no future session re-invents it beside cognition. That is "build-on-not-beside" (anchor §7.3) made
concrete *and* "more types not more tools" applied to the lens itself.

So: **one set of machinery, two (then three) lenses; not one model.** Cognition's model stays per-turn and
ephemeral; Coherence's model is standing and partly-owned (the dispositions). They share the *pattern*, not the
*data*.

---

## THREAD 2 — Prior art + the bigger frame

I map each body of prior art to **the delta** — what the anchor's idea adds that the prior art lacks — rather
than summarizing it, per the advisor's steer.

### 2.1 Evolutionary architecture / fitness functions — and the leap the anchor makes past them **[PRIOR-ART]**

Neal Ford, Rebecca Parsons et al., *Building Evolutionary Architectures*. A **fitness function** is "an
objective integrity assessment of some architectural characteristic(s)" using tests, metrics, monitoring,
logging — to protect architectural dimensions against degradation as the system evolves
([InfoQ](https://www.infoq.com/articles/fitness-functions-architecture/),
[nealford.com](https://nealford.com/books/buildingevolutionaryarchitectures.html)). The three gates the anchor
§1 describes (drift / all-green / reachability) **are textbook fitness functions** — they are exactly the
"objective integrity assessment of an architectural characteristic" the literature defines.

**The delta the anchor leaps to (and why it's genuinely novel):**
- **Fitness functions are stateless: run → pass/fail → forget.** The anchor's §2 insight ("a finding stops
  being a log line that scrolls away; it becomes a typed, addressed, *living record* with a state and a
  disposition that *persists*") is precisely the move *from a fitness function to a held, stateful model of
  integrity.* The literature has no standing object that *remembers* what was frayed and what was deliberately
  accepted. **The statefulness IS the contribution.** [marking: the gates = [OBS] fitness functions; the
  *persistence/disposition* = the anchor's leap past the prior art.]
- **Fitness functions assume a human reads the dashboard and decides.** The anchor points the same model at an
  *autonomous loop's worklist* (§5). The "definition of done = the model is empty of open findings" (anchor
  §5) is "fitness function as a measurable system property" turned into a *convergence criterion for a builder*,
  not a quality gate for a reviewer. That consumer (a build loop, not a human) is not in the EvolArch frame.

### 2.2 Code property graphs / queryable code knowledge graphs — the detection-rigor backbone (Area C's, flagged) **[PRIOR-ART]**

A **code property graph (CPG)** merges AST + control-flow graph + program-dependence graph into one graph where
nodes are functions/variables/classes and edges are call/data/control relations; it was designed "to mine large
codebases for instances of programming patterns" via graph traversals
([Wikipedia](https://en.wikipedia.org/wiki/Code_property_graph),
[Joern docs](https://docs.joern.io/code-property-graph/)). **Joern** (open-source) and **CodeQL** are the mature
implementations; **CodeGraph** maps Git repos into queryable knowledge graphs using AST parsing (+ LLMs) and
explicitly "traces calls and finds dead code"
([FalkorDB](https://www.falkordb.com/blog/code-graph/)).

**Where this lands:** this is the prior art for **Area C's make-or-break** (anchor §7.1 — accurate AST-level
extraction of the real connection graph, not string-matching). I flag it *for Area C* deliberately rather than
annexing it. The cross-stream relevance is only this: the anchor §3's "graph the system keeps of itself" (nodes
= routes/methods/surfaces/suites; edges = called-by/exposed-at/migrated-to) **is a CPG specialized to this
codebase's own seams.** The delta the anchor adds over a generic CPG: (1) the nodes are not just code symbols
but the system's *declared* elements (registry node-types, `ui://` addresses, suites, migrations) — a CPG over
*intent + code*, not code alone; (2) edges carry a *state* (`wired`/`half-migrated`/`orphan`) and a
*disposition*, which a CPG does not model — a CPG tells you the edge is absent; it cannot tell you the absence
is *by-design*. (CodeGraph's "find dead code" is the unwired-route detector; it stops exactly where the
disposition begins.)

### 2.3 Autonomous/agentic dev systems keeping generated code coherent — external corroboration the problem is real **[PRIOR-ART]**

This is the most direct external hit on the anchor's *premise*. From AgentField's "Beyond Vibe Coding" (shipping
production code with ~200 autonomous agents): they name "**the convergence problem** — getting N autonomous
processes to produce one coherent result," and give a documented case where **"agents built an entire API layer
on a module another agent never exported"**
([AgentField](https://agentfield.ai/blog/beyond-vibe-coding)). **That is, almost verbatim, the anchor §1
problem** (the `/api/knobs` built with no front-end caller; the half-migrated feedback store) — external
corroboration that "the system drifts apart at the seams because nobody holds the whole" is a *named industry
problem at scale*, not a quirk of this project.

Their answer is prior art for the anchor §5 loop: **a verifier agent checks every acceptance criterion against
the actual codebase; failures generate targeted fix-issues fed back through the execution engine**
([AgentField](https://agentfield.ai/blog/beyond-vibe-coding),
[Sonar](https://www.sonarsource.com/resources/library/agentic-coding/)). The standard agentic loop is
read→plan→write→run tests/linters→loop-until-success ([Verdent](https://www.verdent.ai/guides/ai-coding-agent-2026)).

**The delta the anchor adds:** in all the prior art, the verifier's worklist is the **original requirements**
(does the code meet the spec it was given?). The anchor's worklist is the **system's own emergent
incompleteness** (does every built thing connect to something?) — a *self-derived* definition of done, not a
human-supplied one. And critically, the prior-art verifier is *stateless per task*; the anchor's model is the
**standing, persistent** integrity object across sessions (the §2.1 delta again). The combination — a persistent
held model whose burn-down IS the convergence criterion for the loop — is what I haven't found in the external
work.

### 2.4 ADRs as institutional memory → burn-down-as-institutional-memory, and dispositions-as-micro-ADRs **[PRIOR-ART → IDEA]**

An **Architecture Decision Record** (popularized by Michael Nygard) captures *a decision, its context, the
alternatives considered, and the consequences* — and "creates an institutional memory that outlives individual
team members," preventing "decision amnesia where teams re-debate settled decisions"
([adr.github.io](https://adr.github.io/),
[em-tools](https://www.em-tools.io/frameworks/architecture-decision-records)). The exact framing: *"if the
answer lives only in the head of an engineer who left last year, you have an institutional memory problem."*

**This is the anchor §1 problem and §9 what-if, stated by the industry in the human-developer world.** The
anchor's no-human-developer constraint makes it *sharper*: there is no engineer whose head holds the answer —
there never was one. So the institutional memory cannot be a document a person maintains; it has to be a
*property of the substrate.*

**The synthesis, which is the §1.3 own/reflect split paying off** **[IDEA]**: **a disposition IS a micro-ADR.**
When Tim (or a consented agent) marks an orphan `by-design: this is an internal operator entry point`, that is
an ADR in miniature — a decision, its context (the finding), the rationale (the reason string), persisted.
`_ORPHAN_ROUTES`'s `(tag, reason)` pairs (suite.py:7017-7054) are *already* one-line ADRs **[OBS]**. So:

> **The burn-down history is the project's institutional memory precisely because the dispositions are the
> un-recomputable part of the model.** Detection is re-derivable and therefore *not* memory (you can always
> recompute "is this wired?"). The disposition — *why* a gap is acceptable, *when* a migration left a seam,
> *who* accepted it and on what reasoning — is the ADR layer, and it is the thing that replaces "the developer
> who remembers." The anchor §9's "queryable: when did this connect, what migration left this, who
> dispositioned that as by-design and why" is **a query over the disposition records**, i.e. an ADR log keyed
> by `code://`/`ui://` address. **[IDEA]** Recommend: dispositions carry `{decided_by, decided_at, reason,
> supersedes}` (the ADR fields) so the by-design set literally *is* the architecture documentation, accreting,
> exactly as the anchor §3 hopes ("the by-design ones, accumulated, quietly become the documented
> architecture").

### 2.5 The recursion (the model watching the coherence of its own mechanisms) — already partly real **[OBS + IDEA]**

The anchor §9's recursive what-if has real grounding in this codebase, not just as a thought experiment:

- **Drift homes:** `RULE_OPS` and `DESTINATION_KINDS` *must stay reflected* in `runtime/AGENTS.md`, and
  `tests/rules_acceptance.py` asserts they do **[OBS rules.py:43-46]**. The same pattern guards `EDGE_KINDS`
  against `contracts/AGENTS.md`, `THOUGHT_SHAPES`/`ACTIVATION_CONTEXTS` against their drift homes
  **[OBS roles.py docstring, activation.py docstring, cognition_info.py:44-46]**. The system *already* checks
  that the declarations describing its mechanisms stay true to the mechanisms.
- **Meta-gates are themselves suites:** `reachability_acceptance` and `suite_health_acceptance` are acceptance
  suites — and `suite_health` explicitly *excludes itself* (recursion guard) **[OBS suite.py:6969, 6988-6989]**;
  `reachability` explicitly excludes the meta-gates' own docstrings from the caller-scan so a doc-mention of
  `/api/knobs` doesn't falsely "wire" it **[OBS suite.py:7071-7076]**. The coherence mechanisms are *already*
  subject to coherence checks, *and* the codebase has already had to reason about the recursion's edge cases
  (self-reference, doc-mention-isn't-a-caller).

**[IDEA]** So the recursion isn't speculative — it's the natural reading of "Coherence is just another lens."
The Coherence model's own nodes include *the detectors themselves* (each detector is a method; does it have a
drift home? is it reflected?). The guard against infinite regress is the same self-exclusion the suite_health
gate already uses **[OBS]**. Recommend: the detector-registry (Thread-2 §2.6) is itself a tracked element, with
the same self-exclusion rule, so "the model watches the coherence of the mechanisms that maintain coherence"
terminates cleanly rather than spiraling.

### 2.6 Finding-types as a growable registry — the cleanest "more types, not more tools" instance **[IDEA, grounded]**

The anchor §9's "what if *types of finding* is itself a registry — declare a check, don't code another bespoke
gate" is the strongest structural recommendation, and the codebase shows exactly how to build it, because the
cognition stream already did the isomorphic thing twice:

- A **role** is a self-registering file (`roles/*.py`, discovered by `RoleRegistry`) **[OBS roles.py:70-73]**.
- A **rule** is declared data validated at build (`build_rule` + `validate_role_rules`, the commit-time static
  walk) **[OBS rules.py:441-483]**.

**[IDEA]** A **finding-type** should be the third instance of that exact pattern: a self-registering declaration
`{kind, detector, address_scheme, default_disposition, drift_home}` discovered the way roles/node-types are.
Adding a new integrity check (e.g. "every migration has a forward-and-back test") = adding a *file*, not editing
a gate. The detector is the only code; the *type, its states, its disposition vocabulary, its rendering* are
declared. This keeps Coherence inside the project's deepest law (one substrate, more types not more tools —
anchor §4) and makes the three gates that exist today (`doc_drift`, `suite_health`, `reachability`) the *first
three rows of a finding-type registry* rather than three hand-built methods — which is literally what the anchor
§4 says they are ("the first three detectors of the model, today, in embryo"). The `_ORPHAN_ROUTES` table is the
proof-of-concept disposition store for one such type already **[OBS]**.

### 2.7 Ties to the introspective-data-building law **[OBS + INF]**

The anchor §4 closes by naming this the introspective-data law pointed at integrity. The cognition stream
already instantiates that law in a way Coherence should mirror: `run_swarm` emits **one batched rollup per wave**
(`cognition.wave`) containing every role's run-record **[OBS cognition.py:600-611]**, and the `rollup`
activation-context is *"a TIMER tick [that] runs the introspective-data-building consolidation of the swarm's
OWN run://-addressed run-records into ONE rollup record"* **[OBS activation.py docstring 12-17]**. That is the
law's full cycle — *operation self-instruments → run-records → substrate → rollups → knowledge* — already wired
for cognition. **[INF]** Coherence is the same cycle with integrity as the instrumented operation: each
detection run emits findings (the run-records); they accrete into the standing model (the substrate); the
burn-down history + the by-design set are the rollups that become knowledge (the institutional memory of §2.4).
The own/reflect split (§1.3) is what keeps this honest: the run-records (findings) are re-derivable telemetry;
only the rollup-of-decisions (dispositions) is kept truth.

---

## Summary of what I'd put in front of Tim (the expansion-ratio-greater-than-one residue)

1. **The convergence is real and mostly already-built** (§1.2 table) — but cognition and Coherence differ in
   *kind* on one axis: ephemeral-per-turn vs persistent-whole-system. **[OBS for the machinery; the distinction
   is the design.]**
2. **The load-bearing distinction is own/reflect** (§1.3): Coherence *reflects-never-owns its detection*
   (re-derivable, like a turn) and *owns its disposition* (a decision, not recomputable). This simultaneously
   satisfies build-on-not-beside, defines what survives a re-scan, and makes dispositions = micro-ADRs. **[IDEA]**
3. **Build it as an explicit third sibling lens** `build_coherence_info` beside cognition/object info, *because*
   the mode-dial-built-twice incident in this very build proves "the next thing built twice" is the live failure
   mode. **[OBS incident → IDEA recommendation.]**
4. **Cognition solves two of the anchor's hard §5 questions with real code:** per-rule readiness → anti-thrash /
   blocked-on-human-without-stalling; determinism → the trust property the loop needs. **[OBS mechanisms → IDEA
   transfer.]**
5. **rules.py is the "declare a check, don't code a gate" engine** — but only the *disposition* half; detection
   rigor (AST/CPG) is Area C, prior art at §2.2. **[OBS + flagged.]**
6. **Prior-art deltas:** fitness functions but *stateful/held* (§2.1); CPGs but over *intent+code with
   disposition* (§2.2); agentic verifier loops but worklist = *self-derived incompleteness, persistent* (§2.3);
   ADRs but *as substrate, keyed by address, replacing the developer-who-remembers* (§2.4). **[PRIOR-ART → IDEA.]**
7. **The recursion is already partly real** (drift-homes + self-excluding meta-gates) and terminates via the
   same self-exclusion rule (§2.5); **finding-types should be a self-registering registry** like roles/rules,
   making the three existing gates its first three rows (§2.6); the whole thing is the **introspective-data law
   pointed at integrity** (§2.7). **[OBS + IDEA.]**

### Sources (external prior art)
- [Fitness Functions for Your Architecture — InfoQ](https://www.infoq.com/articles/fitness-functions-architecture/)
- [Building Evolutionary Architectures — nealford.com](https://nealford.com/books/buildingevolutionaryarchitectures.html)
- [Code property graph — Wikipedia](https://en.wikipedia.org/wiki/Code_property_graph)
- [Code Property Graph — Joern Documentation](https://docs.joern.io/code-property-graph/)
- [CodeGraph: Build Queryable Knowledge Graphs from Code — FalkorDB](https://www.falkordb.com/blog/code-graph/)
- [Beyond Vibe Coding: Shipping Production Code with 200 Autonomous Agents — AgentField](https://agentfield.ai/blog/beyond-vibe-coding)
- [Agentic Coding — Sonar](https://www.sonarsource.com/resources/library/agentic-coding/)
- [AI Coding Agents: Autonomous Development — Verdent](https://www.verdent.ai/guides/ai-coding-agent-2026)
- [Architectural Decision Records — adr.github.io](https://adr.github.io/)
- [Architecture Decision Records: Template & Guide — EM Tools](https://www.em-tools.io/frameworks/architecture-decision-records)
