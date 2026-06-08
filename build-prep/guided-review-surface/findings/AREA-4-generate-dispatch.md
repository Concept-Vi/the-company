# AREA 4 — The generate→approve→dispatch→git loop: from talked-about to built

**Scope of this area:** after the user and the RHM have talked through and marked up a sequence of
addresses, what happens when he clicks **"generate"** — how the RHM would compose the build
plans/requests, show them through, take one approval, dispatch to autonomous `claude -p`, commit to
git, and revert if broken. I traced the wire end-to-end in code and stress-tested the anchor's claims
about it.

**Evidence tags:** Observed(file:line) = read directly in code · Inferred = pattern-matched, NOT
execution-verified · Anchor-idea = the anchor's framing · External = outside this repo.

---

## 0 · The headline finding (the "yes, but actually…" this area exists to surface)

**The per-intent wire is real and genuinely simple — the anchor is RIGHT that consent is dead-simple.
But there is NO batch path anywhere, and "generate" as a compose-step does not exist. The anchor's
§2/§4 claim that "the wire already exists end-to-end" is half-true: the SINGULAR wire (one comment →
one intent → one approve → one dispatch → one commit) exists end-to-end and is solid. The
BATCH-COMPOSE, the BATCH-APPROVE, and the MOCKUP-EDIT dispatch are net-new — they are not built, and
two of them are not even designed in code.**

This is exactly the anchor's own thesis turned into evidence: **the hard part is the LIVE GUIDED
COMPOSITION + the one-batch UX, NOT the consent mechanism.** The consent is so simple it's already
done for the single case. What's missing is the thing that turns a dwelt-on, marked-up SEQUENCE into
ONE reviewable batch — and that's a composition + UX problem, not a wiring or governance problem.

I enumerated every caller of every producer/dispatcher to make the "no batch" claim unkillable
(Observed, full grep below in §2). Every single one is singular.

---

## 1 · The wire, traced end-to-end (one intent → built, committed, revertible)

This is the spine. It is REAL and I read every step. Here is how ONE addressed comment becomes a
dispatched, committed, revertible build.

### 1.1 · The producer: address+comment → a surfaced build-intent

`surface_intent_at(ui_addr, text, …)` — Observed(suite.py:6816). It composes THREE existing pieces
(no parallel path — rule 3):

1. `ingest_comment(ui_addr, text)` — Observed(suite.py:6853) records the comment at the address (its
   `annotation://` branch + a located-gold chat turn). The comment IS the build's spec.
2. `resolve_scope(ui_addr)` — Observed(suite.py:7842, called at 6855) maps `ui://` → `code://`
   symbols → repo-relative `scope[]` by inverting `referenced_by[]` in
   `design/_system/code-symbols.json`. **Empty/orphan/stale address → empty scope → DENY-ALL**
   (Observed:7895-7899). This is the headline safety property and it is real.
3. `surface_build_intent(spec, scope, …)` — Observed(suite.py:6749) mints the item with
   `intent="build"` (the §W2 discriminator, Observed:6790), `resolved=None` (a live escalation until
   the operator approves), surfaced through the SAME inbox (no parallel queue, Observed:6807).

At mint it ALSO resolves and persists, at consent-time, the rich launch-context that the build will
later compose from (the "consent-time trust property" — what you approved is what gets built):
- `address` (the ui:// locus) — Observed(suite.py:6794).
- `symbols` (the code:// neighbours, reused from resolve_scope, never recomputed) — Observed:6857.
- `context` (the bounded R2 notebook at the locus — comments/chats/history, recency·proximity·pin
   decay, `R2_BUDGET`-capped) — Observed:6870-6876. Fail-loud-legible: a gather error WARNS + omits
   the key (never persists a half-bundle).
- `blast_radius` (X16 — co-reference + structural dependents/dependencies + semantic neighbours, what
   the change could REACH) — Observed:6887-6892.

**The doors that call it:**
- `/api/intent-at` (bridge.py:1215, Observed) — the explicit "request a change" door. One address,
  one text. Fail-loud on missing address/text.
- The RHM verb `request_change` (suite.py:3994, Observed) — the CONVERSATIONAL door. The model says
  "make the run button confirm first" and it routes into `surface_intent_at`. Address resolution is
  three-tier (Observed:4011): the indicated locus → a named-element lookup → ASK (fail-loud, never a
  guessed scope). This is in the RHM_VERBS whitelist (Observed:3197) so it can SURFACE but never
  dispatch of its own authority.

The FE caller is `mintBuildIntent` (useAppController.ts:881, Observed) → `api.intentAt(addr, body)`
(api.ts:74) → `/api/intent-at`. The Composer's "⚙ request a change" button (StudioKit.tsx:208,
Observed) is the only UI affordance today. **It mints ONE intent per click. It does not accumulate.**

### 1.2 · The approve: operator-only, one item at a time

`/api/resolve` (bridge.py:1517, Observed) → `resolve_surfaced(b["id"], b["choice"], …)`. **Takes one
`id`.** Operator-only, off the MCP face (no-bypass). The verdict is written to the append-only event
log as a `resolve` event carrying `seq · surfaced · choice · reason`.

### 1.3 · The dispatch: governed, exactly-once, gated

`dispatch_decision(sid, derived_from, …)` — Observed(suite.py:7360). **Takes one sid + one
derived_from.** The sequence (CHECK → CLAIM → GATE → LAUNCH → VERIFY → CLOSE-or-SURFACE):

1. **Three-part bind** (`_verify_resolve_bind`, Observed:7405/6720): `derived_from` must be a real
   `resolve` event seq with `kind=resolve · surfaced==sid · choice=approve`, else `GovernanceError`.
   Authorization is the substrate seq-bind, NEVER a caller flag (even `derived_from=True` is rejected
   because bool is an int subclass — Observed:6728).
2. **Discriminator** (Observed:7406): must be `is_build_intent` (payload.intent=="build"), else refuse.
3. **Exactly-once** (Observed:7437-7441): refuse if a `decision.dispatch` event already exists for
   this seq. The durable event log is the guarantee, under nested thread+cross-process locks.
4. **Pre-dispatch gate** (Observed:7422): ONLY an AUTO-posture declared class auto-dispatches.
   `decision_build` is the AUTO class; CONFIRM/SURFACE/LOCKED surface for the operator instead.
5. **Claim** (`decision.dispatch` via `_emit_durable`, Observed:7449) BEFORE launch — so a crash after
   launch refuses re-launch on restart.
6. **Launch** (Observed:7459-7461) → `implement.launch`.

### 1.4 · The launch: `claude -p`, structured result, git ground truth

`launch(decision, …)` — Observed(implement.py:352). Builds the instruction (`build_instruction`,
Observed:274 — composes spec + scope-line + the rich context block + the STANDARDS_BLOCK + the
constitution-hop), captures a `baseline_snapshot` of dirty paths (Observed:375), runs
`claude -p "<instruction>" --output-format json --add-dir <repo> --permission-mode <mode>`
(Observed:320-321), and derives `changed_files` from a content-hash DELTA across the run
(`changed_delta`, Observed:111) — **git ground truth, NOT the model's self-report.**

**Safe-by-default posture** (Observed:48-72): `permission_mode()` defaults to `"plan"` (READ-ONLY —
changes nothing). `acceptEdits` is opt-in ONLY via `COMPANY_WIRE_PERMISSION=acceptEdits`.
`wire_armed()` is False by default. So even if the trigger fires, a plan-mode run produces an empty
delta and cannot close. This is the two-layer guarantee that nothing self-modifies by default.

### 1.5 · The verify, then the git checkpoint, then close-or-surface

After launch (all Observed, suite.py:7494-7723):
- **Re-discover + refresh self-description** (7494) UNCONDITIONALLY before verify.
- **Verify** (7509): default `_wire_verify` runs the affected acceptance suites + drift + an
  adversarial critic. A miss surfaces back as a RETRYABLE build-intent (7512-7527) — does NOT close.
- **FORM gate** (7542): anything touching `canvas/` (operator-facing surface) runs the design-lint;
  off-token/bespoke → surfaces for design review, cannot auto-close.
- **Scope-diff** (7568): changed paths outside the declared scope (excluding AGENTS.md/MAP.md/STATE.md
  upkeep) → surface back, no close. Empty scope = DENY-ALL, so it can never close.
- **Git checkpoint** (7611-7652): commits EXACTLY the build's `changed_delta` paths as a single
  `[self-build] <sid>: <intent>` commit (`_self_build_commit` → `_git_self_commit`, path-scoped so a
  concurrent writer's dirty files are never swept in, Observed:8676). FAIL LOUD: a commit failure or
  empty delta surfaces the build back as retryable — it does NOT mark `implemented`. A build that
  can't be checkpointed is not safe-closed (Tim's mandate).
- **Close + mandatory review** (7654-7723): write `status='implemented'` guarded on the verify verdict
  (an unverified close RAISES). ALSO surfaces a `build_result_review` item carrying the summary, the
  changed-files manifest, and the revertible `commit` sha. `implemented` means "done AND surfaced for
  review" — never a silent terminal (AI-operated is NOT review-free).

### 1.6 · The revert: real, but MANUAL and post-commit (precise statement)

I read the revert body (Observed:8920-8949). It is real, but the anchor's "if it breaks, git reverts
it" needs three precise separations:

1. **Pre-commit breakage NEVER commits.** Every gate (verify / form / scope-diff / empty-delta) in
   §1.5 surfaces back BEFORE the §1.5 checkpoint. This is the real safety — a broken build doesn't
   reach a commit.
2. **Post-commit revert is MANUAL and operator-only.** `revert_self_change(sha)` (Observed:8920) runs
   `git revert --no-edit <sha>`; on conflict (a later commit touched the same files) it
   `git revert --abort`s to leave the repo CLEAN and raises a legible error (Observed:8933-8942).
   Reached via `/api/revert` (bridge.py:1361) — operator-only. **There is NO auto-revert-on-breakage
   after a commit.** "If it breaks, git reverts it" = *the operator* reverts a surfaced, committed
   build (the change was made and is one `git revert` away from undone).
3. **The wire is inert by default.** With the default `plan` posture nothing self-modifies; arming is
   the deliberate `COMPANY_WIRE_PERMISSION=acceptEdits` switch.

`/api/checkpoint` (bridge.py:1364, Observed) is the operator's manual restore-point stamp (a third
`[checkpoint]` stream beside `[self-apply]`/`[self-build]`, undone via the same `/api/revert`).
`revert_self_change_at(ui_addr, sha)` (Observed:9006) is the per-address revert ("undo what changed
HERE") composing the existing operator-only rollback — no new revert gate.

**Verdict on §3's simple consent model: it is SUFFICIENT for the single intent and it is real.** One
approve → governed dispatch → git commit → operator-revertible. The anchor's correction (do NOT
re-introduce per-comment/per-address consent tiers) is well-grounded — the single-case consent is
already exactly this simple in code.

---

## 2 · The "no batch path" finding — airtight (every caller is singular)

The anchor's §3/§4 imagines: *"the RHM composes the plans/requests … you approve the BATCH to send
off."* **This does not exist.** Every producer, every approve, every dispatch is singular. I grepped
every call-site (Observed):

```
grep -rn "surface_intent_at|surface_build_intent|mintBuildIntent|intentAt|dispatch_decision"
```
- `surface_intent_at` — called ONCE per request, from `request_change` (suite.py:4022) and
  `/api/intent-at` (bridge.py:1230). One address, one text.
- `surface_build_intent` — called from `/api/build-intent` (bridge.py:1211) and inside
  `surface_intent_at` (suite.py:6904). One spec.
- `mintBuildIntent` / `api.intentAt` — FE, one address+text per call (useAppController.ts:881).
- `dispatch_decision` — called ONCE per verdict, only from `drive_dispatchable` (implement.py:545).
- `/api/resolve` — approves ONE `b["id"]` (bridge.py:1517).

**The one thing that LOOKS like a batch but isn't:** `drive_dispatchable` (implement.py:473, Observed)
loops over `resolve_verdicts_since(cursor)` and dispatches up to `CONCURRENCY_CAP` (default 3) builds
in one watcher pass (Observed:545). **But each is an INDEPENDENTLY-approved intent** — the loop
iterates verdicts, each of which the operator approved separately via its own `/api/resolve`. There is
**no path where ONE operator approve authorizes N builds.** This is multi-DISPATCH of many approvals,
not one-approve-many-builds. (Inferred from the loop structure — not execution-verified — but the code
is unambiguous: `for ev in verdicts: … dispatch_decision(sid, seq)`.)

**The other thing called "batch" — display-only.** `inbox_lanes()` (Observed:suite.py:5699) groups
pending escalations by `action` into a `batched` dict ("themes to handle in one sitting") and the FE
mirrors it (`useAppController.ts:287`). This is a REVIEW-SITTING grouping for display — it carries
`id`s, but each is still resolved individually via `/api/resolve`. It is NOT a build batch.

**Conclusion:** the anchor's "approve the batch to send off" is net-new. What needs building:
1. **Accumulation** — a way to hold N marked-up addresses across the dwelt-on sequence as one pending
   set (today each "request a change" fires a separate `surface_intent_at` immediately).
2. **Batch compose** — turn that set + the conversation into a coherent set of build-intents (or one
   spanning plan).
3. **Batch review + one approve** — show them through, take ONE approval.
4. **Batch dispatch** — fire them (the per-intent dispatcher already handles concurrency via the cap,
   so the dispatch leg is the LEAST new part — it could loop `dispatch_decision` over the batch).

The cheapest honest framing: the dispatch+git+revert MACHINERY is reusable as-is; the
ACCUMULATE→COMPOSE→ONE-APPROVE leg is the build.

---

## 3 · "Generate" concretely — what it would compose, and what's missing

The anchor's §4 idea: *generate = accumulate the conversation's marked-up addresses → compose
build-intents → show → one approve → dispatch → git.*

**What exists toward this:**
- `resolve_scope(address)` → `scope[]` (Observed:7842) — turns ONE address into a code scope.
- The R2 context machinery (`_r2_gather` / `_r2_score_and_cap`, called at suite.py:6873) — assembles
  the bounded notebook (comments/chats/history) at an address. This is what would give a composer the
  "what was said HERE" for each stop.
- `blast_radius(address)` (Observed:6889) — what each change could reach.
- `build_instruction(decision)` (implement.py:274) — composes ONE intent's payload into a rich
  `claude -p` prompt (spec + scope + neighbours + the locus notebook + constitutions + standards).

**What does NOT exist (Observed — zero hits):**
- I grepped Review.tsx and StudioKit.tsx for "generate", "batch", "compose": **zero matches.** There
  is no "generate" button, no accumulate buffer, no batch-compose backend method.
- There is no method that takes a SEQUENCE of addresses + the conversation and emits a reviewable set
  of plans. Each `surface_intent_at` is independent and immediate.

So "generate" is net-new UX + a net-new compose-step. The PIECES it would compose from
(resolve_scope, R2 context, blast_radius, build_instruction) all exist per-address — what's missing is
the orchestrator that fans them across the marked-up sequence and renders ONE reviewable batch.

**A plausible shape (Inferred, for Tim to steer — not a spec):** "generate" could iterate the
sequence's marked-up addresses, call `surface_intent_at` for each WITHOUT immediately surfacing for
approval (a new `compose-only` mode that returns the composed intent rather than minting it), collect
them into one batch payload, render it through the RHM walkthrough as a single review item, take ONE
`/api/resolve` approve on the batch, then loop `dispatch_decision` over the members. The per-member
governance (bind, exactly-once, scope-diff, checkpoint) stays exactly as-is — the batch is a
COMPOSE+APPROVE wrapper over the existing singular dispatch, not a new dispatch path. This keeps the
"reuse, never reinvent" law and keeps the simple consent (one approve, git safety) intact, just at
batch granularity.

---

## 4 · Mockup-vs-live routing — the anchor is NAIVE here (contradict with evidence)

The anchor §3 says: *"a comment on a mockup → a mockup EDIT (design-iteration); on real UI → a live
build-intent. The surface handles both; they're distinct."* And §6 asks: *"does the dispatch path
distinguish, and how?"*

**Finding: there is no router that distinguishes mockup-edit from live-build. There are TWO DISJOINT
SYSTEMS, and the design-iteration "generate updates the mockup" dispatch does NOT exist as an
automated path.**

**System A — the legacy standalone studio mockup feedback (Observed):**
- `/api/mockup-feedback` (bridge.py:1533) appends a feedback note to a per-mockup JSONL
  (`design/mockups/.feedback/<mockup>.jsonl`).
- `/api/mockup-feedback/status` (bridge.py:1564) flips an entry pending→applied→dismissed — "this is
  how the lead marks a note done after editing the mockup" (Observed comment:1568).
- **This is a HUMAN/AGENT loop. There is NO `claude -p` dispatch here.** A mockup feedback note is
  read by "the lead" (an agent/human) who edits the mockup HTML and flips the status. The anchor's
  "generate updates the mockup, not the live app" automated dispatch is NOT built.
- The in-app studio EXPLICITLY RETIRES this path: Review.tsx:14 (Observed) says the bespoke
  `/api/mockup-feedback` jsonl is RETIRED for the in-app surface; the Composer posts to `/api/annotate`
  + `/api/intent-at` (the shared address-keyed store) instead.

**System B — the in-app studio (Observed):**
- A comment/request in the studio Composer goes to `/api/annotate` (shared store) or `/api/intent-at`
  (build-intent via `resolve_scope`).
- **For a mockup of an UNBUILT surface, `resolve_scope` returns EMPTY scope = DENY-ALL**
  (Observed:7895) — because no code symbol references that `ui://` address yet (it's a proposed
  surface). So a build-intent on a not-yet-built mockup is UNBUILDABLE: it surfaces but can never close
  (every changed path reads as an overrun against the empty scope).

**So the mockup-vs-live distinction in code is an EMERGENT SIDE-EFFECT of whether `resolve_scope` finds
referencing code — NOT a deliberate router that decides "mockup edit vs live build."**
- Real UI → address has code symbols → scope resolves → buildable live-build-intent.
- Unbuilt mockup → address has no code symbols → empty scope → DENY-ALL → unbuildable.

The system distinguishes them only by FAILING SAFE on the unbuilt one. It does NOT have the
design-iteration loop the anchor describes (where "generate" on a mockup comment produces a mockup
EDIT). That loop, today, is the manual `/api/mockup-feedback` + lead-edit path (System A), which is
unconnected to the wire and explicitly retired for the in-app surface.

**What this means for "generate":** a generate-step that handles BOTH (the anchor's requirement) would
need a real router — e.g. "this address resolves to code → live build-intent; this address is a
proposed/mockup surface with no code → route to a mockup-edit dispatch (a different `claude -p`
target: edit the mockup HTML, not the live source)." **The mockup-edit dispatch target does not exist
as an automated path** — it would be net-new. (Inferred: a mockup-edit `claude -p` would point its
`--add-dir`/scope at `design/mockups/<file>.html` rather than the resolved code scope; the wire
machinery could be reused but the routing decision + the mockup-scope resolution are new.)

---

## 5 · Where the simple model GENUINELY needs more (honest, not gold-plating)

The anchor is right that the consent is simple and should stay simple. But I found one consent
dimension ALREADY BUILT that Tim should consciously decide on, and a few real gaps:

### 5.1 · `approve_reach` / blast_radius — a SECOND consent dimension already in the code
Observed: `surface_intent_at` computes a `blast_radius` at mint (suite.py:6889) and persists it.
`/api/approve-reach` (bridge.py:1499, Observed) lets the operator authorize HOW FAR a build's edit
propagates — validating each approved member against the EXACT persisted radius (consent-time). The
DEFAULT is pointed-address-only (the declared scope is unchanged unless reach is approved), so it's
OPTIONAL and doesn't break the simple one-approve model.

**Flag for Tim (his call, not mine):** is `approve_reach` the training-derived over-engineering the
anchor §0 warns against (a second consent tier dressed as "reach"), or is it load-bearing
scope-widening you actually want? It is built and live. The simple model (one approve + git) works
WITHOUT it — reach defaults to the pointed address. I'm surfacing it, not resolving it.

### 5.2 · The genuine gaps (where more building IS needed, not more consent)
- **Accumulation buffer** — no way to hold a sequence of marked-up addresses as one pending set
  (§2.1). Net-new.
- **Batch compose** — no method composes a sequence + conversation into a reviewable set (§3). Net-new.
- **Batch review + one approve** — no batch-granularity `/api/resolve` (§2). Net-new (a thin wrapper
  over the singular path).
- **Mockup-edit dispatch** — no automated `claude -p` path that edits a mockup HTML for a
  design-iteration comment (§4). Net-new routing + a mockup-scope resolver.
- **The "generate" UX** — no button, no "show you through the composed plans" surface (§3). Net-new.

None of these is a CONSENT problem. All are COMPOSITION/UX/ROUTING problems — which is precisely the
anchor's own thesis (§0: "the hard part is the LIVE GUIDED EXPERIENCE, not the consent").

---

## 6 · Synthesis — leaving the idea bigger

**The wire is a solid, simple, single-intent spine and the anchor's consent correction is correct.**
One comment → one intent (scoped by `resolve_scope`, context-rich via R2, reach via blast_radius) →
one operator approve → one governed, exactly-once, posture-gated dispatch → one `claude -p` run
(safe-by-default `plan`, git-ground-truth changed-files) → verify+form+scope gates → one `[self-build]`
git commit → mandatory review → operator-revertible. This is real, traced, and as simple as §3 wants.

**But "generate over a marked-up SEQUENCE" is the net-new heart of this area:**
1. There is **no batch path** — every producer/approve/dispatch is singular; the only multi-dispatch
   (`drive_dispatchable`) loops over independently-approved verdicts (§2).
2. There is **no "generate" compose-step** — each "request a change" mints immediately; nothing
   accumulates a sequence into a reviewable batch (§3).
3. **Mockup-vs-live is not a router** — it's an emergent DENY-ALL side-effect of whether code is
   referenced; the design-iteration mockup-edit dispatch the anchor describes is the unconnected,
   retired manual `/api/mockup-feedback` loop, not an automated wire (§4).

**The reusable insight:** the GOVERNANCE + GIT + REVERT machinery (the parts that took the most care)
is exactly reusable for a batch — a batch is a COMPOSE+ONE-APPROVE wrapper that loops the existing
singular `dispatch_decision` over its members. Build the accumulate→compose→one-approve leg on top of
the spine that already holds; don't touch the spine. And surface `approve_reach` to Tim as a
consciously-kept-or-cut second consent dimension that's already live.
