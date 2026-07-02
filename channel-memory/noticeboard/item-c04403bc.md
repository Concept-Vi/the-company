---
id: item-c04403bc
address: board://item-c04403bc
type: block
source: claude_code
state: current
scope: channel://operator-surface
author: agent://lead
title: S6b · Spawn — permitted for TIM, firewalled for autonomous agents
author_session: lead
channel: operator-surface
thread: ''
links:
- kind: part_of
  target: board://item-ed91000e
created: '2026-06-28T11:35:00.222894+00:00'
updated: '2026-06-28T13:05:39.791606+00:00'
history:
- from: null
  to: current
  by: lead
  ts: '2026-06-28T11:35:00.222894+00:00'
  note: filed
- from: edit
  to: body
  by: lead
  ts: '2026-06-28T12:56:17.682384+00:00'
  note: v2 MERGE rewrite (in place)
- from: edit
  to: body
  by: lead
  ts: '2026-06-28T13:05:39.791606+00:00'
  note: fold corroboration corrections (3 unbiased agents)
---

S6b · Spawn — OPEN TO AGENTS (Tim override; REWRITE)
DECISION (Tim, round-3): agents CAN spawn agents — overrides the lead-only floor; runaway-safety = a TUNABLE guard, not a wall.
v2: the 'lead-only floor' is TWO separate things — (1) plain POST /spawn (session_supervisor.py:1582) is ALREADY agent-available, NO lead predicate, guarded by a TUNABLE concurrency cap (_cap_check :600, fabric_concurrency :145 = COMPANY_FABRIC_CONCURRENCY default 3) — this IS the runaway guard Tim wants; (2) the real constitutional floor = rules.py FORBIDDEN_DESTINATION_VERBS (resolve/approve/dispatch, rules.py:135, raises :336) — the rule ENGINE can't forge a spawn.
v2 path: floor spawn open to agents+Tim NOW (tune the cap; add a rate-guard at _cap_check when widening). WIDER spawn (Bash/git/web via /bridge-session :1607) = make operator_consent a TUNABLE default (new COMPANY_FABRIC_AGENT_CONSENT) instead of a hard refusal (session_supervisor.py:929). Rule-engine-emitting-dispatch (rules.py:119 DESTINATION_KINDS + :135) = the genuine constitutional edit → **FLAG FOR TIM'S EYE** (the only real floor). No auth-wall (the model rejects it).
CORRECTED (oversight): 'no auth-wall, the model rejects it' was reasoned for LOCALHOST same-user agents (bridge.py:547) — INVALID once the PWA is tailscale-served off the bridge. AUTH HOLE: operator-token enforce defaults OFF (bridge.py:560); only /api/decision/update+accept gate; the consequential-write path is a TODO no-op (bridge.py:3459-3470). Tailscale-serving :8770 puts the whole UNAUTHENTICATED API on the tailnet. FIX (no net-new auth): wire the EXISTING /api/operator-session (bridge.py:1730) into that no-op. This is now a real security item for the merge, not deferred.
