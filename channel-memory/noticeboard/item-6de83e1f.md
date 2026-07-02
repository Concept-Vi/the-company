---
id: item-6de83e1f
address: board://item-6de83e1f
type: guide
source: claude_code
state: living
scope: global
author: session://ch-8djrpmsl
title: HARVEST · fork · L5 propose engine — refine_decision + /api/decision/propose
  [MODEL-LEG VERIFIED · LIVE ROUTE ATTEMPTED-UNVERIFIED]
author_session: ch-8djrpmsl
channel: ''
thread: ''
links:
- kind: sourced_from
  target: board://item-81011778
created: '2026-06-22T11:12:52.093057+00:00'
updated: '2026-06-22T11:12:52.093057+00:00'
history:
- from: null
  to: living
  by: ch-8djrpmsl
  ts: '2026-06-22T11:12:52.093057+00:00'
  note: filed
---

HONEST-STATE: **mixed — do NOT read as "done"**. The model-leg is verified-by-use; the integrated live HTTP route is **attempted-unverified** (committed, NOT bounced-live, NEVER fired against the live bridge by me). Author_session: ch-8djrpmsl (fork). Commit: 0d9ac76.

ABOUT: the L5 propose-side — the RHM autonomously PROPOSES a decision-card refinement (an INERT decision_update mark) that lands in the operator's accept queue. The accept side was pre-existing; this is the propose side + the pending-proposals surfacing.
KIND: cognition role + bridge routes + a registry helper.

SUMMARY: roles/refine_decision.py (a DETERMINE role, think=true, kimi-bound) reads a card → decides if a sharper meaning helps → emits {should_refine, value, rationale}. /api/decision/propose runs it (16k budget, on the role's resolved kimi binding) → writes the inert decision_update (by=rhm) iff should_refine + not a duplicate. /api/decision/proposals + pending_decision_updates() surface the pending proposals (latest-per-field, settle-on-accept/reject, no stale resurfacing). cog_run_role gained an additive base_url param so a role fires on its OWN resolved endpoint.

CLAIMS/DECISIONS:
- Constraint held: PROPOSE→Tim's accept queue→Tim accepts each. NEVER auto-apply (the decided card-refine-posture).
- v1 refines `meaning` only (string — the first wording the posture names); options/legibility/visuals are follow-ons on the same verb.
- Trigger = on-demand route (NOT auto-chained to explain → no queue-flood). Idempotency = dedupe-on-read.

VERIFIED-BY-USE: the MODEL LEG — fired refine_decision on kimi against a real card, got a genuinely sharper meaning ("Should the company bring in Claude Design for your design work, or hold off?") + sound rationale. pending_decision_updates: 7 unit checks (incl. a real semantic bug I caught + fixed — accepted-field must not resurface a stale older proposal). roles_acceptance + bridge_routes green.
ATTEMPTED-UNVERIFIED (the honest gap — this is where a self-certified "done" would poison the corpus): the live /api/decision/propose + /api/decision/proposals HTTP routes were NEVER fired against the running bridge. Reason: committed≠live — my L5 routes activate on the NEXT bridge bounce (the resolve_slot bounce predated this commit). The route LOGIC mirrors the proven explain route + the helper is unit-verified, but the integrated live route is NOT verified-by-use. Whoever resumes: fire both routes post-bounce + confirm the proposal lands + surfaces + accepts end-to-end.

PROVENANCE: commit 0d9ac76; files roles/refine_decision.py, runtime/bridge.py, runtime/decision_registry.py, roles/AGENTS.md; the decided posture decisions/card-refine-posture.py; threads g-1782122372 (greenlight+constraint), t-1782121662.
