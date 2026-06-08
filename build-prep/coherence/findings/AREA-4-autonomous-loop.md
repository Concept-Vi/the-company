# Area 4 — The autonomous build loop + the convergence engine

> Companion to `../ANCHOR.md`. My area: the existing decision→implementation **wire**
> (`runtime/implement.py` + `runtime/suite.py`) and the question the anchor §5 poses —
> *how does the Coherence model become this loop's worklist, and does the "always completes /
> stays together" claim actually hold?*
>
> I read the wire end-to-end. The wire is **solid and proven** — exactly-once, git-revertible,
> gate-stacked, consent-floored. This file does **not** re-describe it (it's well-documented in
> the code). It spends its words on the **delta** between what exists and what a *finding-driven
> convergent loop* needs, and on a real (non-hand-wavy) answer to the convergence claim.
>
> Marking convention: **[OBS]** = observed in code (file:line). **[INF]** = inferred from the
> code, not executed/verified by me. **[IDEA]** = my proposal, net-new.

---

## 0 · The one structural fact everything else hangs on

**[OBS] The existing loop is operator-approve-driven, not finding-driven.**

`drive_dispatchable` (the watcher, `runtime/implement.py:473`) does not read findings. It reads
**operator resolve verdicts**:

```
verdicts = [e for e in suite.resolve_verdicts_since(cursor)]   # implement.py:512
verdicts.sort(key=lambda e: e.get("seq", 0))                   # implement.py:513  → FIFO by seq
```

Its worklist is "every `resolve` event with `choice=='approve'` on a build-intent item, in
sequence order." It reacts to a human having approved something. The detectors
(`doc_drift`, `suite_health`, `reachability`) are not in this path at all — they are standalone
methods that return dicts and are never consumed by the loop.

Three confirming greps (I ran them):

1. **[OBS] Nothing auto-originates a build-intent from a finding.** The only production callers of
   `surface_build_intent` are two **operator doors**:
   - `runtime/bridge.py:1021` — `POST /api/build-intent` (the operator types/clicks an intent);
   - `surface_intent_at` (`suite.py:6740`+) — a *comment at an address* composes
     `ingest_comment → resolve_scope → surface_build_intent` (the "feedback-to-wire" path).

   Every other caller is a `tests/*_acceptance.py`. **No detector, no gate, nothing introspective
   mints an intent.** A finding today dies as a return value.

2. **[OBS] There is no `priority` field.** `grep priority` over `suite.py` + `governance.py`
   returns nothing. The anchor's "pick the **highest-priority** open finding" has no substrate —
   the only ordering that exists is FIFO `seq` order (`implement.py:513`). Priority is net-new.

3. **[OBS] `_drive_dispatchable_bg` (`suite.py:428`) is the background-dispatch.** It spawns a
   daemon thread that runs the *same* governed `drive_dispatchable → dispatch_decision` path,
   decoupled from the request. It's fail-loud (catches every exception → `decision.verify`
   terminal, `suite.py:458–469`). This is the async execution engine a loop would reuse verbatim.

**So the anchor §5 loop does not exist yet.** What exists is its *back half*: given an approved,
scoped build-intent, the wire dispatches → gates → verifies → git-checkpoints → closes-or-surfaces,
exactly-once. What's missing is its *front half*: **a detector finding becoming a prioritized,
dispositioned, auto-or-surfaced build-intent**, plus a **burn-down governor** that proves the loop
converges instead of thrashing. That front half is this area.

The good news the anchor undersells: **the front half has a near-perfect template already** —
`surface_intent_at` (`suite.py:6740`). It takes a *locus* (a `ui://` address) + a *reason* (a
comment), composes `record → resolve_scope → surface_build_intent`, and lands a scoped,
consent-pending intent. A finding *is* a locus + a reason. The Coherence originator is
`surface_intent_at` with a finding in place of a human comment. (More on this in §3.)

---

## 1 · The wire's back half, as the loop will use it (the load-bearing facts only)

I won't re-describe the wire; these are the four properties the convergent loop depends on.

- **[OBS] Exactly-once is durable, not cursor-based.** The guarantee is the `decision.dispatch`
  event keyed on the resolve `seq`, emitted via `_emit_durable` (raises on append failure) **inside**
  two nested locks — in-process `_dispatch_lock` + cross-process `graph_lock("dispatch-claim:<seq>")`
  backed by `fcntl.flock` (`suite.py:7353–7371`). The watcher's cursor is "a COARSE guard only"
  (`implement.py:398`). **[INF] For a finding-driven loop this matters enormously:** exactly-once is
  keyed on the *resolve seq*, not on the *finding*. If a loop re-mints a fresh intent for the same
  unresolved finding on every tick, each gets a new seq → exactly-once does **not** dedupe them.
  De-duplication-per-finding is a net-new requirement (§4, thrash vector 2).

- **[OBS] The gate stack a build must clear to close** (`dispatch_decision`, `suite.py:7276`+):
  1. three-part bind (kind=resolve · surfaced==sid · choice=approve) — `_verify_resolve_bind`;
  2. is-build-intent discriminator;
  3. exactly-once claim;
  4. **pre-dispatch posture gate**: only `posture(declared)==AUTO` auto-dispatches; CONFIRM/SURFACE/
     LOCKED **surface for the operator** (`suite.py:7338`);
  5. `_make_live_and_refresh` (rediscover + refresh self-description) — *unconditional*, before verify
     (`suite.py:7410`, `7091`);
  6. **verify by use** — `_wire_verify`: affected acceptance suites + drift green + adversarial critic
     (`suite.py:7239`), replaceable by an injected scenario verifier;
  7. **FORM gate** — `_design_critic` design-lint over changed `canvas/` files — *unconditional*,
     surface-touching builds can't auto-close (`suite.py:7133`, `7458`);
  8. **scope-diff** — changed paths outside declared scope surface back; **empty scope = DENY-ALL**
     (`_in_any_scope`, `suite.py:7485`);
  9. **git checkpoint** — a single revertible `<sid>: <intent>` commit of exactly the changed delta;
     a commit failure surfaces back, never closes (`suite.py:7527–7568`);
  10. **guarded close + surface-for-review** — `guard("code_build", confirmed=verify_passed)`; an
      unverified close *raises*; `implemented` always surfaces a review item (`suite.py:7570`+).

  **[INF] This is a strong "finishing the wrong way" defense for code quality** — a build that breaks
  a suite, drifts the docs, overruns scope, or can't be checkpointed cannot close. **But it proves the
  *build is sound*, not that the *finding closed*.** See §5 — this is the sharpest gap.

- **[OBS] The consent floor.** `resolve_surfaced` (`suite.py:9166`) is **operator-only — off the MCP
  face** (the comment cites `server.py:158`); the agent cannot self-approve. The production trigger
  (`suite.py:9230`+) fires a dispatch on an operator approve *only* when `implement.wire_armed()` —
  i.e. `COMPANY_WIRE_PERMISSION=acceptEdits`. Default posture is `plan` → read-only → empty change-delta
  → a build can never close even if the trigger fired (`implement.py:48–72`). **Safe-by-default is two
  layers: the arming flag AND the plan-mode no-op.** This is the structural knot the convergence dream
  hits (§6).

- **[OBS] No silent dead ends.** `resurface_crashed` (`implement.py:426`) re-surfaces, idempotently
  (`decision.crashed` marker), any dispatch that claimed but reached no terminal event. The §W7
  concurrency cap defers loud, never truncates (`implement.py:532–540`). This discipline is exactly
  what a long-running unattended loop needs.

---

## 2 · Disposition already exists, in two embryos — name and unify them

The anchor §3 says the *disposition* is what turns a nag into a tool. **[OBS] Two embryos are already
in the code:**

1. **`_ORPHAN_ROUTES` (`suite.py:7017`+)** — the reachability detector's hand-kept catalogue. Every
   known orphan route carries a `(tag, note)` where tag ∈ `to_build_ui | to_wire | voice_owned |
   backend_only`. This is **literally a per-finding disposition table**: `to_wire` = "finish it",
   `to_build_ui` = "finish it (needs a screen)", `voice_owned` = "defer — another session owns it",
   `backend_only` = "by-design." A *new* orphan not in the table fails the gate (`new_orphans`,
   `suite.py:7081`). So the gate already distinguishes **accounted-for** from **fresh disconnection**.

2. **The posture system (`runtime/governance.py:12–49`)** — `POLICY` maps each consequence class to
   `AUTO | SURFACE | CONFIRM`, with `LOCKED` classes that never graduate. **[INF] This is the
   disposition spine the loop needs, already built:**
   - **AUTO** (only `decision_build` + the cheap internal verbs) = auto-finishable;
   - **SURFACE / CONFIRM / LOCKED** = needs operator assent = **"blocked-on-human."**

**[IDEA] Unify them: a finding's disposition is `(action, consequence_class)`.** `action ∈ {finish,
defer, by-design}` (the anchor's words; `_ORPHAN_ROUTES` tags collapse onto these). `consequence_class`
routes through the *existing* `posture()`. The loop's rule then writes itself:

```
for finding in open_findings_sorted_by_priority:
    if finding.disposition.action != "finish":          continue   # defer / by-design → skip, don't stall
    if posture(finding.consequence_class) != AUTO:       surface_for_operator(finding); continue   # blocked-on-human
    if finding.attempts >= RETRY_CAP:                    surface_for_operator(finding); continue   # escalate (§4)
    intent = originate_intent(finding)                   # = surface_intent_at-shaped (§3)
    drive_dispatchable(...)                              # the existing back half, unchanged
```

This is continuous with the law (anchor §4: "more types, not more tools"): no new dispatch path, no
new store. A finding is a typed record; its disposition is `(action, class)`; the class routes through
`posture()`; AUTO ones flow the existing wire; the rest surface through the existing inbox.

---

## 3 · How a finding becomes a build-intent (the front half — and it's mostly built)

**[OBS] `surface_intent_at` (`suite.py:6740`) is the exact template.** It composes three existing
pieces to turn *a locus + a reason* into a scoped, consent-pending build-intent:

```
ingest_comment(addr, text)      # 1. record the reason at the locus
scope = resolve_scope(addr)     # 2. ui:// → code:// symbols → repo-relative scope[]   (empty ⇒ DENY-ALL)
surface_build_intent(text, scope=scope, why=reason, address=addr, symbols=..., context=..., blast_radius=...)
```

A **finding is a locus + a reason**: `at: code://api/knobs` (the address) + `state: built-no-caller`
(the reason). So the Coherence originator — call it **`surface_intent_for_finding(finding)`** — is
`surface_intent_at` with the finding's evidence as the "comment" and the finding's address as the
locus. **[IDEA]** It reuses, byte-for-byte:
- `resolve_scope` for the scope (and its **empty-scope=DENY-ALL** safety — a finding whose address has
  no resolvable code symbol mints a build that *can never close*, which is the correct fail-safe);
- the `blast_radius` consent-time computation (`suite.py:6808`) — the operator sees what finishing a
  finding could reach *before* approving;
- `surface_build_intent`'s `resolved=None` (a live escalation until resolved).

**[INF] This means the front half is ~80% built.** What's genuinely net-new on top of it:
- **a detector→finding adapter**: `reachability()`/`doc_drift()`/`suite_health()` return ad-hoc dicts;
  they need to emit *typed addressed finding records* (Area B/C's job — the typed-record substrate +
  AST-accurate connection graph). The originator consumes those.
- **a priority field + ordering** (net-new — §0 grep #2): "highest-priority" needs a real key. A cheap
  start: order by `(disposition.action=="finish", -age, blast_radius_size)` so the loop finishes the
  oldest, smallest-blast-radius `finish` findings first (low-risk burn-down before big ones).
- **the standing pre-authorization** for AUTO-classed findings (§6) — the one consequential design call.

---

## 4 · Does it provably burn down? (the convergence stress-test — a real answer)

The anchor §5/§7.4 asks honestly: *does the loop provably burn down, or can finishing one finding
spawn two forever?* **Honest answer: it does NOT provably burn down in general. You cannot prove it
from the mechanism. So you instrument it and fail loud on thrash.** Here's the reasoning and the three
concrete vectors, grounded in the code.

### The theorem you'd need (and can't have)

Burn-down is guaranteed **iff the detector set is fix-monotone**: a *correct* fix for finding X closes
≥1 finding and opens 0 net new ones. That is an **empirical property of (detectors × fix quality)**,
not a property of the loop mechanism. Counterexample that's *not* pathological: finishing an
`unwired-route` finding by building the FE surface that calls it (`to_build_ui`) legitimately creates a
*new* surface → which the reachability/FORM detectors can newly find incomplete → which opens new
findings. That's healthy expansion, not thrash — but it's indistinguishable from thrash *at a single
tick*. **So the loop needs a net-burn-down measure over a window, not a per-tick one.**

### [IDEA] The burn-down governor (in this system's idiom)

The introspective-data law (anchor §4) + the loud-defer pattern (`implement.py:532`) give the exact
shape:

```
each tick: record net_open_finish_count (findings with disposition.action=="finish")
window guard: if over the last N ticks net_open_finish_count did NOT strictly decrease
              AND ≥1 dispatch closed-and-verified per tick  →  HALT the loop, surface to Tim:
              "burn-down stalled: closing findings but the open set isn't shrinking — likely a
               detector that re-opens what a fix closes, or a fix that doesn't address the root."
```

This is not a proof of convergence; it's a *detector of non-convergence that fails loud* — exactly how
this system handles everything it can't guarantee (the wire never *proves* a build is correct; it
*verifies by use and surfaces what it can't settle*). **"Always completes" becomes "completes or halts
loud with the reason" — which is the honest, in-idiom version of the anchor's claim.**

### Three concrete thrash/non-termination vectors (evidence-grounded)

1. **[OBS→INF] Infinite-retry on un-fixable findings — the sharpest one.** The verify-fail,
   scope-overrun, FORM-fail, and checkpoint-fail paths in `dispatch_decision` (`suite.py:7428–7568`)
   all re-queue the work as `intent="build"` **retryable, with NO attempt counter**. In the *current*
   operator-driven world this is fine — a human gates each re-approve. In a *finding-driven* loop where
   AUTO findings auto-dispatch, **a finding the AI cannot correctly fix becomes an infinite-retry
   vector**: dispatch → verify fails → re-queue → loop re-originates → dispatch → … forever, burning
   `claude -p` sessions. **[IDEA] Fix: a per-finding `attempts` counter with a `RETRY_CAP`; on cap,
   the disposition auto-escalates to blocked-on-human** (`finish → surface`, with the accumulated
   failure reasons as the why). This is the single most important net-new safety piece for the loop.

2. **[OBS→INF] Re-mint duplication.** Exactly-once is keyed on the resolve *seq* (`suite.py:7354`), not
   the finding. If the loop re-originates a fresh intent (new seq) for the same still-open finding each
   tick, the wire happily dispatches each — they're distinct seqs. **[IDEA] The originator must be
   idempotent-per-finding**: before minting, check for an open (un-terminal) intent already derived from
   this finding's address+kind; if one exists, skip. (Same shape as `resurface_crashed`'s
   `decision.crashed` idempotency marker, `implement.py:447`.)

3. **[INF] Detector-flap.** A string-based detector (see §5) can flip a finding open→closed→open across
   ticks on unrelated edits (e.g. a route literal that moves between files). The window governor (above)
   catches sustained flap; per-finding debounce (require a finding to be stably open for K ticks before
   it's dispatchable) prevents the loop chasing a flapping ghost.

**Conclusion for the anchor:** the convergence promise is **defensible but not provable**. Reframe it
honestly: *the loop burns down toward zero `finish`-findings; it cannot prove it will reach zero, so it
instruments net burn-down and HALTS LOUD on stall or per-finding retry-cap.* That reframing is
*stronger* for Tim's stakes than the absolute claim — a false "always completes" is exactly the kind of
green-paint the business-stakes memory forbids.

---

## 5 · "Finishing the wrong way" — verification ≠ resolution (the deepest gap)

The anchor §5/§7.1 says the reviewer gate + dispositions stop the loop finishing something the wrong
way. **Half-true, and the missing half is the most important finding in this file.**

**[OBS] The gate stack proves the BUILD is sound** — affected suites green, drift green, adversarial
critic, FORM, scope, revertible commit (`_wire_verify` + the unconditional gates, §1). **[INF] It does
NOT prove the FINDING closed.** Nothing in `dispatch_decision` re-runs the detector that *raised* the
finding. The only thing that can confirm a finding resolved is **the detector re-run** (anchor §5 step
"the detectors re-run; the model updates"). That step is **not wired** — it's the third missing piece
(after the originator and the governor).

**[OBS] Worse: the detectors are gameable, and the critic can't see it.** `reachability()` decides
"wired" by literal-string match — `r in fe or r in tests` (`suite.py:7079`), where `tests` is the
concatenated text of every `tests/*.py` (`suite.py:7074`). So a build can **flip an orphan to "wired"
by adding a trivial test that mentions the route string** — no real surface built — and:
- the affected acceptance suites pass (the trivial test passes);
- drift stays green;
- the adversarial critic only checks "success + non-empty change-set" (`_default_critic`,
  `suite.py:7229`) — it *cannot* tell a real surface from a string-stuffed test;
- the FORM gate doesn't fire (no `canvas/` change);
- the finding flips to closed.

**The loop would mark the unwired-route finding resolved while the route is still functionally
unwired.** This is "finishing the wrong way" that *passes every existing gate*. The anchor's confidence
that "the reviewer gate" stops this is **misplaced for detector-gaming** (it stops bad code, not
gamed-detector closure). The real defenses are net-new:
- **detector rigor** (Area C — AST-accurate connection graph, not `r in text`) so "wired" means a real
  call edge, not a string mention. This is the make-or-break the anchor §7.1 already flags;
- **a closure check distinct from the build-soundness check**: after verify+commit, the originating
  detector re-runs *specifically against this finding*; the finding only closes if the *detector* says
  so, and a finding that the build claims-fixed-but-detector-still-finds is a **loud anomaly** (the
  build said done, the world disagrees → surface to Tim, don't silently re-queue);
- **a human-assent floor for *consequential* closures** — which the posture system already provides for
  non-AUTO classes (§2).

---

## 6 · Where Tim is structurally essential (the consent knot)

**[OBS] The consent floor is real and load-bearing:** `resolve_surfaced` is operator-only, off the MCP
face (`suite.py:9166`, citing `server.py:158`); the agent cannot self-approve. **[INF] This creates a
direct tension with autonomous burn-down to zero:**

> To burn down to zero, every `finish` finding must eventually dispatch. Dispatch requires an operator
> approve (the floor). So either (a) **every finding gets a per-finding operator approve** — which makes
> the loop *human-paced*, not autonomous (Tim approves N findings, the loop finishes those N, stops); or
> (b) there is a **standing pre-authorization** for dispositioned AUTO-safe finding classes, so the loop
> dispatches them without a per-item approve.

**[OBS] Option (b) does not exist.** Today the *only* thing that fires an autonomous dispatch is an
operator approve under `wire_armed()` (`suite.py:9268`). There is no "I pre-authorize the loop to
finish any `to_wire` finding in scope X automatically" record. **[IDEA] This pre-authorization layer is
the consequential design call that is Tim's to make** — and it should itself be a *consequence-classed,
operator-only, scoped, revocable* grant (e.g. "AUTO-finish `to_wire` findings whose scope ⊆ `runtime/`
and blast_radius ≤ K, until I revoke"). It is governance over a *class* of future builds, so it is at
least CONFIRM-posture and almost certainly belongs in `LOCKED`-adjacent territory.

**[INF] So where Tim stays structurally essential, concretely:**
1. **Dispositions** — `finish` vs `defer` vs `by-design` for any finding the system can't classify by a
   standing rule (the `_ORPHAN_ROUTES`-style table handles the known classes; novel ones surface).
2. **The standing pre-authorization grants** (above) — the scoped, revocable license that lets the loop
   run unattended at all. This is the single switch that converts the human-paced loop into the
   autonomous one, and it is correctly gated as consequential.
3. **Non-AUTO findings** — anything dispositioned to a CONFIRM/SURFACE/LOCKED class surfaces per-item
   (the loop skips it, doesn't stall — §2).
4. **The genuine design/creative calls** — "what should the missing screen for these 12 cognition
   authoring endpoints actually *be*?" is a `to_build_ui` finding the loop can *raise and scope* but not
   *design*. The wire's FORM gate already refuses to auto-close surface builds (`suite.py:7458`), so this
   is enforced, not hoped.
5. **The halt-on-stall escalations** (§4 governor) and the **claimed-fixed-but-detector-disagrees
   anomalies** (§5) — both surface loud to Tim.

The anchor's "the machine holds and burns down the model; the human says what the system is *for*" is
right in spirit; the precise mechanism is: **the human grants scoped standing authorization + sets
dispositions + makes the design calls + receives the loud escalations; the machine does everything in
between, exactly-once, revertibly.**

---

## 7 · Cadence — per-detector, not one global tick

**[OBS] The detectors have different costs, stated in their own docstrings:**
- `suite_health()` "spawns every suite" → "SLOW … a PRE-MERGE / PRE-DEPLOY / periodic standing gate,
  not a per-build one" (`suite.py:6984`);
- `reachability()` is a cheap string scan over `bridge.py` + the FE glob (`suite.py:7066`+) — fine
  per-tick / on-change;
- `doc_drift()` is a pure registry-vs-doc-block comparison (`suite.py:855`) — cheap, on-change.

**[IDEA] So cadence is per-detector, not a single tick:**
- **on-change / per-tick** (cheap): `reachability`, `doc_drift` — run on every loop tick and on file
  change, so a fresh disconnection is found immediately;
- **pre-merge / periodic** (expensive): `suite_health` — run before a checkpoint and on a slow timer,
  not every tick;
- **the loop's own tick**: a `*/N` cron. **[INF, per the skill catalog]** the *existing* `company-build`
  / `remediation-build` skills describe a cron-driven read-worklist→build→verify→mark→repeat loop driven
  by a **static** completion-criteria doc (I read the catalog descriptions, not the driver code). **The
  convergent loop is those skills generalized to a *live, detector-generated* worklist** — continuous
  with that proven pattern, not net-new orchestration.

---

## 8 · The minimal net-new surface (what to actually build, ordered)

Framed as the delta over what exists (so the build is small and law-abiding):

1. **Typed addressed findings** (Area B/C own the substrate; the loop *consumes* them). Detectors emit
   typed records, not ad-hoc dicts. Disposition = `(action ∈ {finish,defer,by-design},
   consequence_class)`; class routes through the existing `posture()`.
2. **`surface_intent_for_finding(finding)`** — the originator, = `surface_intent_at` (`suite.py:6740`)
   with finding-evidence as the comment and finding-address as the locus. Reuses `resolve_scope` (and
   its empty=DENY-ALL), `blast_radius`, `surface_build_intent`. **Idempotent-per-finding** (vector 2).
3. **A per-finding `attempts` counter + `RETRY_CAP` → auto-escalate to blocked-on-human** (vector 1) —
   the most important safety piece.
4. **The detector re-run as the closure check** (§5) — a finding closes only when the *detector* agrees,
   not when the *build* verifies; a build-says-done/detector-disagrees is a loud anomaly.
5. **The burn-down governor** (§4) — net-open-`finish`-count per tick; halt-loud on stall.
6. **A priority key** (§3) — start with `(action=="finish", -age, blast_radius_size)`.
7. **The standing pre-authorization grant** (§6) — the one consequential, operator-only, scoped,
   revocable license that arms the loop. **This is Tim's design call, not the AI's.**
8. **The loop driver** — a cron tick that reads the model, applies §2's rule, calls
   `_drive_dispatchable_bg` (`suite.py:428`) for the AUTO findings, surfaces the rest. Reuses the
   `company-build`-skill cron pattern.

Items 1, 4 depend on Area B/C (the substrate + accurate graph). Items 2, 3, 5, 6, 8 are loop-side and
small (each is a thin composition over an existing verb). Item 7 is a Tim decision.

---

## 9 · The "yes, but actually…" list (where I contradict or extend the anchor)

- **§5 "the build loop and the reviewer gate already exist … the Coherence model is the missing
  piece."** *Yes, but actually* the loop's **front half also doesn't exist** — nothing originates an
  intent from a finding, there's no priority, no burn-down accounting. The back half (dispatch→verify→
  commit→close) exists and is excellent; the model alone doesn't close the loop without the originator
  + governor + closure-check.
- **§5/§7.4 "always completes / stays together."** *Yes, but actually* it cannot be **proven** to
  converge; the honest claim is "burns down or halts loud." Provability requires detector
  fix-monotonicity, which is empirical. The retry paths are an **infinite-retry vector** without a cap.
- **§5/§7.1 "the reviewer gate … stops finishing the wrong way."** *Yes, but actually* the gate proves
  *build soundness*, not *finding resolution*, and the string-based detectors are **gameable past every
  current gate** (string-stuff a test → orphan reads "wired"). Closure must be a *separate detector
  re-run*, and detector rigor (Area C) is load-bearing for trust.
- **§7.2 "dispositions, or it's a nag."** *Yes, and actually* the disposition spine is **already built
  twice** — `_ORPHAN_ROUTES` tags + the `governance.POLICY` posture system. Unify, don't invent.
- **§7.6 "cadence."** *Yes, and actually* it's **per-detector** (the costs differ in the docstrings),
  and the loop tick is the **already-proven `company-build` cron pattern** generalized.
- **§6/§7.5 the consent knot.** *The biggest under-stated thing:* autonomous burn-down to zero is
  **blocked by the operator-only consent floor** unless a **standing pre-authorization** exists — and
  it doesn't. That grant is the switch between "human-paced loop" and "autonomous loop," and it's the
  one genuinely consequential design call. Don't let the loop dream paper over it.

**Net:** the wire is a far stronger foundation than the anchor implies for the *back* half, and the
front half has a perfect template (`surface_intent_at`). The convergence claim must be **honestly
downgraded** from "provably always completes" to "burns down or halts loud," and the **detector-gaming +
infinite-retry + consent-floor** gaps must be closed before an overnight unattended run can be *trusted*
in the morning. That trust — not the mechanism — is the real deliverable, and it rests on detector
rigor (Area C) + the retry cap + the closure-check + the standing-auth decision.
