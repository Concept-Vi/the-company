# The Coherence Substrate — the grounded artefact

> **What this is.** The anchor (`ANCHOR.md`) caught an idea in its "what if" shape and sent six research
> agents to explore it across the real system, each writing a companion in `findings/`. This document is
> the synthesis — written after reading all six whole, reasoning across them. It is no longer pure
> "what if": the research *grounded* the idea in real code, *corrected* it in two important places, and
> *decided* several of the anchor's open questions with evidence. But it is still not a spec or a plan —
> it is the shared, grounded understanding for Tim and the cognition session to reason over together and
> shape into whatever gets built. Evidence is cited to the companions (which cite `file:line`).
>
> **The one-line version:** the Coherence Substrate is **not new architecture — it is one more lens over
> machinery this system already has**, and the six areas independently proved it: every part of a "finding"
> maps onto an existing primitive, the disposition system already exists *twice* in embryo, and the
> RHM-explains-a-finding organ is *already half-written and explicitly waiting for this*. The single thing
> that is genuinely hard, and genuinely the make-or-break, is **detection rigor** — and the research both
> measured exactly how the current approach is wrong and proved an accurate version is feasible *on this
> codebase specifically*.

---

## 1 · What we now know that we only suspected before

The anchor argued coherence should be a held substrate, not scattered gates. The research turned that
argument into grounded fact, and the conviction is much higher now than at the anchor stage. Six things
are now **established**, not hoped:

1. **Build-on-not-beside is real, field by field.** Area 1 + Area 2 independently mapped every field of a
   finding — `{kind, address, state, disposition, evidence, since}` — onto a primitive already in the repo:
   *typed* = the node-type declaration shape; *addressed* = the already-address-keyed annotation store
   (`append_annotation` — "the address IS the key"); *persisted* = the append-only event log
   (`append_event`/`_emit`, already address-stamped on every emit); *dispositioned-with-lifecycle* = the
   Inbox's separate-status-lane, which **already solved** the one hard storage tension (a mutable state on
   an append-only substrate, via the pin-overlay-resolved-last-wins pattern). **No new store, no new
   scheme, no new resolver.** Four registrations, zero parallel machinery.

2. **The disposition system already exists — twice.** `_ORPHAN_ROUTES` (the reachability catalogue's
   `to_wire`/`to_build_ui`/`voice_owned`/`backend_only` tags) is literally finish/defer/by-design in
   embryo; and `governance.POLICY` (the consent postures AUTO/SURFACE/CONFIRM/LOCKED) is the
   auto-vs-needs-human spine. Every area that touched dispositions reached the same instruction: **unify
   these two, don't invent a third.**

3. **The RHM-explains-a-finding organ is already half-built, and explicitly waiting for this.** Area 5
   found `up_translate('finding', …)` already coded in `suite.py:5828`, with a comment that says verbatim
   it's "the shape G2 will feed — NOT wired here, that's a later lane." A past session anticipated this
   exact idea and left the hook. The interface composes from four existing organs (the RHM explainer,
   CognitionView's glanceable live-surface idiom, the indicate→explain→drill move, the consent→build wire)
   — it is a *sibling of CognitionView*, not a new app.

4. **The autonomous loop's back half is excellent; only its front half is missing.** Area 4 read the wire
   end to end: exactly-once (durable, lock-backed), the full gate stack, the git-revertible checkpoint, the
   operator-only consent floor, no-silent-dead-ends — all solid and proven. What does not exist is the
   *front half*: nothing originates a build from a finding, there's no priority, no burn-down accounting.
   And the front half has a near-perfect template already — `surface_intent_at` (a locus + a reason → a
   scoped consent-pending intent; a finding *is* a locus + a reason).

5. **The whole thing is the project's own introspective-data law, pointed at integrity.** Area 6 showed
   the cognition stream already runs the full cycle (operation self-instruments → run-records → substrate →
   rollups → knowledge) for thinking; Coherence is the identical cycle with *integrity* as the instrumented
   operation. The burn-down is a read-time rollup (like `run_stats`) — so there is **no maintained graph to
   keep**, which dissolves the anchor's cost worry at the root.

6. **External practice confirms both the problem and the novelty.** Area 6's prior-art sweep found the
   exact problem named at industry scale ("agents built an entire API layer on a module another agent never
   exported" — verbatim our `/api/knobs` situation), and located the idea precisely against the literature:
   it is a **fitness function made *stateful/held***, a **code-property-graph extended with *state +
   disposition***, an **agentic verifier loop whose worklist is *self-derived incompleteness* not a human
   spec**, and an **ADR log that *is the substrate*, replacing the developer-who-remembers**. The
   combination is not in the external work.

---

## 2 · The load-bearing insight the research produced: the own/reflect split

This is the conceptual heart, and it did not exist in the anchor — Area 6 produced it and it reorganizes
everything:

> **Coherence reflects-never-owns its DETECTION, and OWNS its DISPOSITION.**
>
> A finding's *detection* is re-derivable from the code — re-run the detector on the same tree, get the
> same finding — exactly as a cognition turn is re-derivable from its run. So detection is a **view**: it
> rides the existing reflects-never-owns + projection + event machinery, keeps nothing, and can be
> recomputed freely and trusted.
>
> A finding's *disposition* — "this orphan is by-design because X", "defer this, another session owns it" —
> is **a decision a human or a consented agent made**, and re-running a detector can never recompute *why*.
> So disposition is a **record**: the one genuinely net-new persisted thing, and the only thing that must
> survive a re-scan.

Three things fall out of this at once:
- It settles "build-on-not-beside" precisely: detection = a lens over existing machinery (no new store);
  only dispositions are new data, and they ride the typed-record substrate that already exists.
- It tells you what survives a re-scan and what doesn't: **re-detect freely; never recompute a
  disposition — look it up.**
- **A disposition is a micro-ADR.** `{decided_by, decided_at, reason, supersedes}`. The burn-down history
  becomes the project's institutional memory *precisely because the dispositions are the un-recomputable
  part*. The anchor's dream — "queryable: when did this connect, what migration left this, who
  dispositioned that as by-design and why" — is just a query over the disposition records, keyed by
  address. The `_ORPHAN_ROUTES` `(tag, reason)` pairs are already one-line ADRs.

This is the through-line that makes the substrate coherent with the system's deepest laws rather than
bolted on.

---

## 3 · The make-or-break, measured: detection rigor (and the good news)

Every area pointed here, and Area 3 (the re-run, after the first died on an auth lapse — itself a live
instance of the problem) answered it with numbers. The headline **inverts the anchor's framing** and is
the single most important technical result of the wave:

- **The anchor said "grep → AST." That's only half-right, and not the dangerous half.** Route *extraction*
  is already accurate (regex and AST find the identical 115 routes — zero divergence); its fragility is
  only latent. **The entire live accuracy gap is on the CONSUMER side**: the gate decides "wired" by
  `route in text` — a substring-anywhere test — and that mis-states **3 of 82 "wired" routes (~3.7%)** as
  connected when they have no real consumer. Among them: `/api/mockup-feedback` — the exact route I wrongly
  deleted earlier. The dangerous direction is the **silent false-*wire*** (a dead route reading as whole —
  the model says "fine" when it's frayed; the silent-failure class your rules forbid), not the false-orphan.

- **A trustworthy graph IS feasible here — because the dynamism is *declared, not hidden*.** This is the
  encouraging finding. Generic tools fail on dynamic dispatch; this codebase removed almost every such trap
  by design: one `SUITE` singleton called by direct attribute (123 clean call-edges, zero `getattr`
  routing), one centralized `api.ts` client, 18 statically-mounted regions, *executed* registries as
  ground-truth, and a 58%-addressed event log. The very properties that make it hard to grep make it
  **easy to model by the right three legs**.

- **The trustworthy method is a three-leg directional hybrid** (the rule that protects against corrosion):
  ```
  Leg A — AST static     PROPOSES the candidate-dead set   (cheap; may over-call dead — the SAFE direction)
  Leg B — the registry   DEMOTES the registry-explained     (node/role/data-driven; truth by construction)
  Leg C — the event log  DEMOTES the runtime-confirmed-live  (positive-only: an edge seen proves it; absence proves nothing)
        → the REMAINDER is the trustworthy "real unwired" set the loop may act on
  ```
  The discipline, non-negotiable: **static may over-call dead (safe); registry and log may only ever
  demote; nothing declares an edge dead from absence.** Joined across the Python↔TS boundary by a bespoke
  route-literal join no off-the-shelf tool spans (every mature tool is single-language and names the same
  dynamic-dispatch blind spot — strong corroboration the three-leg split is the honest shape).

- **Feasibility, tiered honestly:**
  - *Ship-now-trustworthy:* AST route table; route-consumer reachability (fixes the 3 false-wires);
    **capability-with-no-consumer** (easy here — direct `SUITE` dispatch); registry-vs-live;
    static-region-with-no-mount. (Tier 1 + the easy Tier 2.)
  - *Candidate-only (must be demoted by B/C, never auto-acted):* unused-method sweep; data-driven FE mounts.
  - *Honestly bounded — do not over-claim:* **half-migration** (the originating `/status` bug's class) is
    *not a connectivity property* — the graph can flag the candidate (and `/api/mockup-feedback` is a live
    one) but cannot prove a dropped lifecycle without a schema diff; surface it, never auto-finish.
    *Suite-covers-capability* has no clean machine signal (a declared `COVERS=[...]` per suite is the
    realistic first cut).

The cost worry also dissolves here: the graph itself is cheap (parse a few files + read live registries +
read the existing log). The expensive thing (`suite_health`, ~115 subprocesses) is a *different* detector,
run pre-merge, not part of the graph.

---

## 4 · The convergence claim, downgraded honestly (and made stronger for it)

Area 4 stress-tested "always completes / stays together" and the honest answer is: **it cannot be proven,
so you instrument it and halt loud.** This is *more* trustworthy than the absolute claim — a false "always
completes" is exactly the green-paint the business stakes forbid.

- **Burn-down is guaranteed only if the detector set is fix-monotone** (a correct fix closes ≥1 finding and
  opens 0 net new) — which is an *empirical* property of detectors×fix-quality, not a property of the loop.
  And legitimately, finishing a `to_build_ui` finding (building a screen) *creates* a new surface that
  detectors can newly find incomplete — healthy expansion, indistinguishable from thrash at a single tick.
  So: **measure net burn-down over a window; HALT LOUD on stall** ("closing findings but the open set isn't
  shrinking — likely a detector re-opening what a fix closes"). The reframed promise: *"burns down, or halts
  loud with the reason."*

- **Three concrete safety gaps the research found, each with a grounded fix:**
  1. **Infinite-retry vector (sharpest).** The wire's verify-fail/scope-overrun/checkpoint-fail paths
     re-queue with *no attempt counter*. Fine under human gating; in an auto-loop a finding the AI can't fix
     becomes an infinite `claude -p` burn. **Fix: a per-finding `attempts` counter + `RETRY_CAP` →
     auto-escalate to blocked-on-human.** The single most important net-new safety piece.
  2. **Detector-gaming passes every existing gate.** Because "wired" is a string test, a build can flip an
     orphan to "wired" by adding a trivial test that *mentions* the route — no real surface — and the
     acceptance suites pass, drift stays green, the critic only checks "success + non-empty diff", FORM
     doesn't fire. The loop would mark it resolved while it's still unwired. **Two fixes: (a) detector rigor
     from §3 so "wired" means a real edge; (b) closure must be a *separate detector re-run*, distinct from
     the build-soundness check — a build-says-done/detector-still-finds-it is a loud anomaly, not a silent
     re-queue.** (Verification ≠ resolution — the deepest gap.)
  3. **Re-mint duplication.** Exactly-once is keyed on the resolve seq, not the finding; re-originating each
     tick would spawn duplicates. **Fix: the originator is idempotent-per-finding** (skip if an open intent
     from this finding's address+kind already exists — same shape as the existing crashed-marker idempotency).

- **Cognition gives a clean anti-thrash mechanism for free.** Its rule engine fires only when every input
  is *settled* (resolved or provably pruned/failed), never on a timeout. Applied here: a finding whose
  disposition is still `pending` (needs Tim) is simply **not ready** — the loop declines and moves on,
  *without stalling and without thrash*. "Blocked-on-human" is just an unsettled input. Cleaner than the
  anchor's tentative "net burn-down" hand-wave.

---

## 5 · The one genuinely consequential decision — and it's Tim's

This is the thing the loop dream quietly depends on, surfaced by Area 4 and not to be papered over:

> **Autonomous burn-down to zero is *blocked* by the operator-only consent floor — unless a standing,
> scoped, revocable pre-authorization exists. It does not exist today.**

The consent floor is real and load-bearing: `resolve_surfaced` is operator-only, off the agent face; the
agent cannot self-approve. So either (a) every finding gets a per-finding operator approve — which makes the
loop *human-paced*, not autonomous — or (b) Tim grants a standing license: *"AUTO-finish `to_wire` findings
whose scope ⊆ X and blast-radius ≤ K, until I revoke."* Option (b) is the switch that converts the
human-paced loop into the autonomous one, and it is **correctly the most consequential thing in the whole
design** — it is governance over a *class* of future self-modifications. It should itself be a
consequence-classed, operator-only, scoped, revocable grant.

**This is the decision that defines how autonomous "trusted in the morning" actually is. It is not the AI's
call to make — it is yours, and it deserves its own deliberate conversation.** Everything else the machine
can hold and burn down; this is the one knob that says how far it may go between your check-ins.

Where Tim stays structurally essential, concretely: the **standing-authorization grants** (above); the
**dispositions** the system can't classify by a standing rule; the **design/creative calls** (e.g. "what
should the screen for the 12 authoring endpoints *be*" — the FORM gate already refuses to auto-close surface
builds, so this is enforced, not hoped); and the **loud escalations** (stall-halts, retry-cap escalations,
build-says-done/detector-disagrees anomalies).

---

## 6 · The shape, as the research leaves it (three lives, one lens, sibling not merge)

Pulling the six together — a finding has **three lives**, each on an existing mechanism:

```
LIFE 1 · DETECTION   — an addressed event on the append-only log (kind="coherence.finding",
                       target rides an EXISTING code://|ui:// address). Re-derivable. Reflects-never-owns.
                       Trustworthy only with the §3 three-leg graph — never ship grep findings to the loop.
LIFE 2 · DISPOSITION — a micro-ADR in its OWN lane (NOT the operator inbox — which is deliberately
                       operator-only and already drowned once at ~90% test pollution). Borrows the surfaced
                       status/resolved/reason SHAPE + the pin-overlay-last-wins pattern for mutable state.
                       finish/defer/by-design; only by-design escalates through the consent gate.
LIFE 3 · THE MODEL   — a read-time rollup (run_stats pattern) over the finding events ⨝ the disposition
                       overlay → {open_by_kind, by_owner, burn_down_over_time, net_change}. No maintained
                       graph. The loop's "done" = zero open finish-findings.
```

**The interface** (Area 5): a `company coherence` CLI face (cheap, slots into the existing console chain
exactly like `company suites`) **and** a first-class in-app `CoherenceView` — a **sibling of CognitionView**
(shared altitude/fold/projection/token machinery, different lens; *not* a forced single substrate — forcing
the merge would couple two independently-evolving models). Glanceable whole-vs-frayed at altitude 0
(candidate shapes for Tim to pick by sight: a weave that frays/re-knits, a vessel that fills, a
constellation that lights); a spatial seam-map + burn-down band at altitude 1; clickable finding-cards at
altitude 2 that drop to the element and let the RHM explain it at Tim's altitude via the
already-half-built `up_translate('finding')`. Tim's only writes are dispositions (operator actions through
existing write paths). As the loop works, findings open and resolve *live in front of him* — the place he
stands to watch a fully-autonomous build keep itself together.

**Finding-types are a growable registry** (Area 2 + Area 6): a detector is *declared like a node-type/role*
(drop a file: `{kind, detector, address_scheme, default_disposition, drift_home}`), discovered the way
`nodes/` and `roles/` already are. The three gates that exist today become the **first three rows** of that
registry, not three hand-built methods. "More types, not more tools," applied to integrity itself. And the
**recursion is already partly real** (drift-homes + self-excluding meta-gates) and terminates via the same
self-exclusion rule — the model can hold findings about its own mechanisms without spiraling.

**Build-on-not-beside, as the named third sibling:** `build_object_info` ("what exists") + `build_cognition_info`
("how it thinks") + **`build_coherence_info` ("how whole it is")** — and the reason to make it an *explicit
named sibling from the start* is grounded in something that happened *in this very build*: the mode dial was
built twice, independently, in two sessions, and only unified after the fact. Making Coherence an explicit
lens is how it avoids being the next thing built twice.

---

## 7 · The honest "but actually" list (where the research corrected the anchor)

- **"grep → AST is the fix"** → *actually* extraction is already accurate; the live gap is the **consumer-side
  substring test** (measured 3/82 false-wire), and the fix is **reachability, not a better pattern**.
- **"always completes / stays together"** → *actually* not provable; honest claim is **"burns down or halts
  loud,"** and the retry paths are an infinite-loop vector without a cap.
- **"the reviewer gate stops finishing the wrong way"** → *actually* it proves *build soundness*, not
  *finding resolution*, and the string detectors are **gameable past every current gate**; closure needs a
  separate detector re-run + detector rigor.
- **"a finding is a typed record like a surfaced item"** → *actually* a finding **cannot be a surfaced item**
  (the inbox is operator-only and already-drowned); it needs its own agent-disposable lane, only by-design
  escalating.
- **"every element has an address"** → *actually* the address space is `ui://`-only (71 entries) today;
  suites/migrations/engines must be **registered `code://`-style** first — and there is **no `coherence://`
  scheme** (findings ride existing addresses, so clicking one drops to the real element).
- **"are Coherence and cognition the same thing — one substrate?"** → *actually* **same machinery, different
  lens; sibling, not merge.** They differ in kind (ephemeral-per-turn vs persistent-whole-system), and that
  difference is the own/reflect split that is the whole design.

---

## 8 · A build shape, if it's pursued (smallest steps, each leaving the system more coherent)

Not a plan — a sketch of the order the research implies, for Tim + cognition to react to. Each step is a
thin composition over an existing primitive; the early ones are usable alone.

1. **The finding lane + the disposition record** (own/reflect split) — finding-events on the existing log +
   a disposition overlay copied from the Inbox's status-lane pattern. *Promote `_ORPHAN_ROUTES` out of
   source into it* — the most concrete gate→contributor step, and a satisfying recursion (the orphan
   catalogue becomes the first real findings).
2. **The three-leg connection graph** (§3) — the make-or-break; the AST+registry+event-log hybrid, with the
   directional demote-only discipline. Until this is trustworthy, **no grep finding drives the loop.**
3. **The universal reconcile** — `(kind, address)` upsert → known/new/resolved (generalizing reachability's
   documented/new/stale); net-burn-down computable.
4. **`build_coherence_info` + the `coherence.*` SSE branch** — the projection sibling; the contract the
   interface consumes.
5. **The `company coherence` CLI** — the cheapest real face; working lens the moment the projection lands.
6. **`surface_intent_for_finding`** (the loop's front half) = `surface_intent_at` with finding-evidence as
   the comment; idempotent-per-finding; the closure-check as a detector re-run.
7. **The safety pieces** — `RETRY_CAP`→escalate; the burn-down governor (halt-loud-on-stall); the
   blocked-on-human-via-unsettled-input readiness rule.
8. **The standing pre-authorization grant** — *Tim's consequential decision (§5)*; the switch that arms the
   loop.
9. **The `CoherenceView` surface** — last (depends on the projection); the glanceable in-app lens, FORM via
   Claude Design / needs-tim, the altitude-0 shape Tim picks by sight.

Items depending on detection rigor (2) gate the trustworthy ones; the CLI and the lane are usable early.

---

## 9 · The decisions this puts in front of Tim + the cognition session

Reasoning-partner framing — these are the forks the research surfaced, not a request for sign-off:

1. **Is this worth building now, or is it a parked direction?** The research says it's unusually *cheap*
   (mostly unifying what exists) and unusually *high-leverage* (it's the keystone for trusted autonomous
   builds). But it's also a real body of work, and there's an active completion campaign + a studio + a
   mode-dial join already in flight. Sequence question, yours.
2. **The standing pre-authorization (§5)** — the one genuinely consequential design call. How far may the
   loop go between your check-ins? This deserves its own conversation whenever this is pursued.
3. **Sibling vs eventual shared abstraction** — build Coherence as a sibling of CognitionView (the
   recommendation), and only extract a shared "live-model" abstraction later *if* the two surfaces prove they
   share enough by use. (Premature unification is the thing that's easy to regret.)
4. **Cross-stream ownership** — this spans both streams and is cognition-shaped (a live addressed model). The
   detection graph + the loop touch the shared `suite.py`/wire; the projection is a `cognition_info` sibling.
   It wants co-design with the cognition session, not a solo build.

---

## 10 · One paragraph for the cross-read

The Coherence Substrate is not new architecture; it is the system's existing self-knowledge machinery
(registry-is-truth, the addressed event log, the pin-overlay disposition pattern, the run_stats rollup, the
RHM explainer, the consent wire, the reflects-never-owns live surface) **pointed, for the first time, at its
own integrity** — with one genuinely new conceptual move (own the disposition, reflect the detection, so a
disposition is a micro-ADR and the burn-down history becomes the institutional memory that replaces the
developer-who-remembers), one genuinely hard engineering core (a trustworthy three-leg connection graph,
feasible here *because the dynamism is declared not hidden*, with the discipline that absence never declares
an edge dead), and one genuinely consequential human decision (the standing scoped authorization that says
how far the loop may burn down unattended). The convergence promise is honestly "burns down or halts loud,"
not "always completes" — which is the stronger claim for a system whose credibility can't afford green-paint.
The three gates already built are its first three detectors; the `_ORPHAN_ROUTES` table is its first
disposition store; `up_translate('finding')` is its explainer, already written and waiting. It is, in the
end, the same realization that started this whole arc — *in fully-AI development nobody holds the whole* —
turned into a substrate that holds it.
