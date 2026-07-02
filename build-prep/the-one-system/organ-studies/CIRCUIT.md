# ORGAN REBUILD STUDY — THE CIRCUIT (propose → approve → execute)

*(④ the-one-system · fusion session, 2026-07-02. Verbatim study by the CIRCUIT investigator; Observed = read/queried directly, Inferred labeled.)*

## (1) SIDE A — the cloud intent circuit

### IS (Observed, schema.sql refs)
- **intents** (37549): intent_type, Context Token tuple (user_id, actor_id, space_id, correlation_id), source, source_event_id, parent_intent_id; required_autonomy L0–L5; status pending|running|succeeded|failed|cancelled; retry_count/max_retries/next_retry_at; started_at/completed_at; run_id, thread_id ("LangGraph Cloud thread ID for workflow resumption after HITL approval"); wizard_state, composition_type, suspended_at_action. Comment: "Durable work queue. All non-trivial agent work flows through intents."
- **proposals** (38588): preview, bounded_effects, execution_intent, idempotency_key (all NOT NULL), delivery_style immediate|batched, status pending|approved|denied|expired|withdrawn, edited_params, delivered_at, expires_at. Comment: "L3→L4 approval gate. Previewable, bounded, idempotent candidate actions requiring explicit authorization."
- **approvals** (33672): proposal_id, decision approve|deny, decided_by/at, decision_note, edited_params, user_id, correlation_id. "Every L4 execution must trace back to an Approval."
- **delegations** (36397): user → grantee_actor, optional space (NULL=global), scopes[], max_autonomy L0–L5 (default L3), constraints, validity window, status. "Vi can only access user data where delegation exists and is active."

### WORKS (Observed)
1. IN: event_to_intent trigger (56061) → handler (12114) via event_routing_registry (registry-driven); create_intent RPC (10036).
2. EXECUTE: process_intent trigger (56117) + intent-executor edge fn: polls 10 pending, sets running+started_at, routes by prefix — vi.* → LangGraph Cloud (thread/run stored), send_sms → Twilio, publish_content → update. Inline types get terminal writes.
3. GATE: immediate proposals auto-queue to SMS (56539 → proposal-delivery: per-type templates "[Vi] @agent → 'title' … YES/NO/?", quiet hours + daily caps).
4. CONSENT: approval INSERT fires auto-resume (56553); proposal approved fires execute_approved_proposal (56588): emits proposal.approved event; dispatch_agent fans notice_board.decorator_matched events — **which re-enter step 1**. Approval → events → intents: one loop.
5. RESUME: approval-resume-webhook (cron/min): recent approvals → proposal's intent → requires thread_id → LangGraph resume → succeeded.
6. TRACE: get_correlation_chain (15211) — hardcoded 5-step UNION on correlation_id.

### What actually flowed (Observed, cvi_mine)
107 intents (2026-01→04). vi.decorator_dispatch 57 ALL running; vi.draft_reply 28; L2×91, L1×6, L3×4, L4×6. **73 stuck 'running'; 0 of 107 have thread_id; 0 parent_intent_id** — resume's `if (!thread_id) continue` skipped all forever; executor line 71: `continue; // Don't mark as succeeded yet`. Zombies are structural. 31 proposals (15 delivered, 1 edited_params, 0 expires_at ever set). 18 approvals (all approve, two users, 1:1). 14 delegations: 13 near-identical vi:global L3 duplicates (no idempotency) + 1 L5 (create:agent_workflow, deploy:langgraph, manage:user_agents). 26 correlation_ids shared across tables — the thread was real.

### REACHING (Inferred from observed)
Composition-native execution (wizard/suspend columns, writers barely arrived) · intent trees (parent, 0 rows) · self-healing (retry RPC, metrics) · approval-as-edit (edited_params both tables) · the recursion: the circuit as its own execution substrate.

## (2) SIDE B — the engine's governance/decision organ

### IS (Observed, /home/tim/company)
- **runtime/governance.py** — POLICY: action classes → posture on reversibility·cost·externality. AUTO incl. decision_build (the ONE auto-dispatch; auto-dispatch ≠ auto-close, results still surface). SURFACE (proceed on default+deadline). CONFIRM (destructive/code_build/external/source_data/frozen_contract/…). LOCKED={source_data, external, frozen_contract} never graduates. Unknown class → CONFIRM. guard(): AUTO runs; SURFACE runs+records; CONFIRM raises unless confirmed.
- **Inbox** — surfaced decisions in the shared store (both faces). Two lanes by law: operator-only `resolved` (off the MCP face) vs `status` lifecycle inbox→presented→responded→resolved|requeue|implemented. surface_review(); test_origin tagging; persisted-max id under store lock.
- **runtime/decision_registry.py** — decisions as file-discovered rows (decisions/<id>.py: meaning, options with implication+recommended, scope, subtype, owner), addressed decision://<frame>/<id>. **compose_state(row, marks)** — state is NEVER authored; folds latest decision_take/retract by ts. compose_definition — RHM proposes decision_update marks; compose only on operator decision_update_accept; options-change on a decided card auto-reopens. decision_decided_signal — decide emits event + noticeboard signal; record-only.
- **The wire** (AGENTS.md rule 9) — implemented = done AND surfaced (event + review inbox item + diff), never silent; reflects-never-owns.
- **runtime/cc_gate.py** — per-step GATE/ABORT/REWIND on live sessions as observer; gate records with transition history; steps session://<sid>/step/<tool_use_id> or run://<turn>/<member>[/<i>] ("a composition-step pre-leg pause is enforceable, unlike the native-loop HONEST-LIMIT"); ABORT = interrupt+teardown; REWIND = materialize fork.
- **runtime/operator_memory.py** — propose→confirm lifecycle; evidence mandatory ("a memory of Tim without his words is fabrication").
- **mark_types/** — decision_take/retract/update/update_accept, comment, contradiction, strain, favour…

### WORKS (Observed)
One shape at every scale: agent proposes; only operator's inbox approval actuates; state composed from immutable marks; every terminal surfaces for review. guard() the chokepoint; apply-verbs read resolved=='approve' from the inbox, never a caller flag.

### REACHING (Observed comments → Inferred)
Earned trust/graduation (LOCKED implies the rest graduate; mechanism absent) · enforced pre-execution pause anywhere (own-driver execution) · a control-type registry (4th verb addable as a row) · scoped memory injection (designed, partial) · deadline machinery (documented for SURFACE, not built).

## (3) COMMON CORE · UNION'S EDGES · IMPLIED-BUT-ABSENT

### Common core
1. Agents floored at propose (A: L3 default ceiling, L4 needs Approval; B: propose-only, resolve off the MCP face).
2. Consent = a separate, attributed, traceable record neither executor can write (A: approvals table; B: decision_take mark).
3. Preview before consent (A: preview/bounded_effects; B: meaning/options in Tim's words).
4. Default-safe (A: L3 default; B: unknown→CONFIRM).
5. An inbox as the meeting surface.
6. Consent can carry an amendment (A: edited_params; B: decision_update+accept).
7. The decide fires the resume (A: triggers; B: decided_signal).

### Union's edges
A only: Principal/Delegation axis (multi-user, scopes, windows, space scoping) · durable work queue with retries+metrics · correlation thread first-class + chain query · registry-driven event→intent routing · delivery machinery (templates, quiet hours, caps) · L0–L5 gradation · wizard/suspension columns · idempotency_key.
B only: marks-composed immutable state · retract · the two-lane law · surfaced-for-review as part of done · per-step live gating+abort+rewind · posture from reversibility·cost·externality with LOCKED floor · propose→confirm with mandatory verbatim evidence · fail-loud · registry-discovery · test-origin hygiene · origin responsive|generative.

### Implied-but-absent
1. **Liveness (heartbeat/lease)** — A's 73 zombies prove the need; B's gates concede they can't hold sessions. Neither has "running must keep proving it's alive."
2. **The execution→closure back-edge, generically** — A trusted a webhook needing a thread_id nothing wrote; B closes the loop for build-class only.
3. **Approval retraction window** — B retracts decisions; A executes instantly on INSERT. Both imply: retract legal until execution claims the take.
4. **Delegation as a composed, propose→confirm object** — A's 13 duplicates = hand-inserted; B has the lifecycle, no authorization semantics.
5. **Deadline→escalate loop** — A has expires_at (unused); B documents it (unbuilt).
6. **Enforced idempotent execution** — A declares the key, never checks it; B has no exactly-once.

## (4) THE REBUILT ONE

**The unifying move (B applied to A's spine): every circuit object is an immutable, addressed row; every state transition a typed, attributed, timestamped MARK; every "status" a FOLD over marks — including over the clock.** A mutated status column can lie forever; a composed state cannot.

### Addresses
```
principal://<id> · delegation://<frame>/<id> · intent://<frame>/<id> · proposal://<frame>/<id>
thread://<correlation_id> · session://<sid>/step/<tid> · run://<turn>/<member>[/<i>]
```
Frame = B's decision:// scope grammar (global|space|user|session).

### The circuit
PRINCIPAL —grants→ DELEGATION —ceilings→ INTENT —surfaces→ PROPOSAL —take→ APPROVAL(=mark) —claims→ EXECUTION —terminal→ SURFACED-FOR-REVIEW —resolve→ closed. The operator resolves the review (reflects-never-owns).

### Mechanics
- **Delegation × Posture**: class registry (POLICY as rows: AUTO|SURFACE|CONFIRM + LOCKED) × delegation rows (A's semantics + B's lifecycle: immutable grant, propose→confirm activation, idempotency_key kills duplicates; state composed from grant/suspend/revoke marks). **Effective posture = most restrictive of (class posture, delegation ceiling); LOCKED ignores delegations.** L5≈AUTO-in-scope, L3≈propose floor, L4-needs-approval≈CONFIRM; LOCKED is what L0–L5 never expressed.
- **Intent lifecycle = marks only**: intent_claim{by, session, lease_until} · heartbeat{lease_until} · intent_suspend{at_step, awaiting} · terminal{succeeded|failed|cancelled, result}.
- **Zombie-proof by construction**: compose_state(intent, marks, now): no claim→pending; claim with now≤lease_until→running; terminal→terminal; **claim with now>lease_until and no terminal→LAPSED** — derived, no reaper. Lapsed is re-claimable (idempotency_key prevents double effect); auto-escalates past threshold. Dead executors can't lie: the lie requires continuously asserting liveness.
- **Proposal**: a surfaced item in the ONE inbox (no parallel queue), carrying A's payload (preview/bounded_effects/execution_intent/idempotency_key) + default+deadline. SURFACE-class → default=proceed at deadline; CONFIRM-class → default=reject, escalate. Delivery (SMS/push, quiet hours, caps) = a projection of the inbox; proposal-delivery's templates = a renderer.
- **Approval = a decision_take mark** on the proposal address {by, ts, value, edited_params?, reason} — legal only from a principal whose effective posture covers the class (checked at mark-write, fail-loud). Consequences: retractable until an intent_claim references the take; audit trail IS the data; two-lane safe (executor writes claim/heartbeat/terminal; only the operator's channel writes takes); "approvals" survives as a VIEW over take marks.
- **Execution**: claim records the live handle (session:// or run://) — generalizes A's thread_id to any runtime. cc_gate as-is; ABORT = cancelled terminal; REWIND = fork + fresh claim. Terminal → surfaced_for_review → review item; operator resolve = the true terminus; resolve fires decided_signal (A's resume + B's signal, one wire).
- **thread://<correlation_id>** first-class; every row carries part_of; the chain = marks_for(thread) ordered — derives what get_correlation_chain hardcoded, grows without breaking.

### Data landing (107+31+18+14) — translation into synthesized marks, healing on arrival
- 107 intents → immutable intent:// rows; created_at→created; started_at→synthesized intent_claim with **zero-length lease** (honest: liveness never proven); completed→terminal marks (34). **The 73 stuck-running land as claim-without-terminal → compose to LAPSED immediately.** History stops lying with zero destructive edits. 6 wizard rows → intent_suspend marks; pendings stay re-claimable.
- 31 proposals → surfaced items verbatim; delivered_at (15) → presented marks; pendings lapse via the new deadline default, surfaced as a batch.
- 18 approvals → 18 decision_take marks on their proposal addresses; the table becomes the view.
- 14 delegations → 13 duplicates collapse to ONE confirmed delegation with 13 evidence entries (timestamps preserved — evidence law); the L5 lands separately with its window. 2 live grants + full provenance.
- correlation_ids → thread:// addresses with part_of edges; the chain reproduces as the mark fold.

### NEW (neither side had, both implied)
The lease/heartbeat fold · approval-retract window bounded by claim · delegation idempotency + propose→confirm grants · deadline→default/escalate actually built · idempotency enforced at claim · one inbox projecting to every channel · the chain as derivation.

## (5) EACH SIDE'S PARTIALITY
**A stopped at the far side of the executor** — built the full descent, handed execution to an external runtime that never honoured the return contract (the cliff is literal: executor:71 continue + a webhook precondition satisfied by zero rows). Articulated the durable/multi-principal/delivered half; stopped where execution ownership began.
**B stopped at the single-operator boundary** — total rigor on the law half (postures, marks, two lanes, review, gating) for exactly one principal; no user_id anywhere, no delegation, no push delivery, no durable queue; even the pause seam belongs to the native loop (HONEST LIMIT).
**Mirror images of one gap**: each owned one half of the seam and trusted the other half to something external. The lease fold exists precisely so no half can ever again depend on an external party remembering to report back.

**Key refs:** schema.sql intents:37549 proposals:38588 approvals:33672 delegations:36397 create_intent:10036 event_to_intent:12114 chain:15211 triggers:56061–56911 · functions/{intent-executor,approval-resume-webhook,proposal-delivery}/index.ts · runtime/{governance,decision_registry,cc_gate,operator_memory}.py · mark_types/ · AGENTS.md rule 9 · NORTH-STAR.md.
