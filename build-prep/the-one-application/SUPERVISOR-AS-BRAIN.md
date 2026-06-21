# Supervisor-as-Loadable-Brain for the RHM — architecture (fork lane)

*2026-06-21, fork. Render-independent architecture for FACE-1's headline (the lead/Tim scope): the
session-supervisor becomes a MIND the RHM COMPOSES — "a loadable brain, not just a service." Grounded in the
REAL seam + the real supervisor (not invented). CANDIDACY: the mechanism is solid + buildable; the big shape
(does the RHM's mind become multi-source) is Tim's to ratify. Reuse-don't-parallel throughout.*

## THE SEAM THAT ALREADY EXISTS (verified in code — this is why it's buildable, not a rebuild)
- **Host side:** `surface/app/src/rhm/RightHand.tsx` mounts the RHM's mind via `window.forkVBrain.attach({panelEl,
  getAimAddress, …}) → Brain` (an injected object with `.ask`/`.attach`). The host holds NO model-knowledge — it
  consumes whatever brain is attached. So a NEW brain that satisfies the `Brain` contract drops in with ZERO host
  change (projection's guarantee — the swap-seam they preserved; the V-icon is a placeholder for exactly this).
- **Mind side today:** the RHM's brain is a SINGLE model — `SUITE.rhm_config().model` (default `DEFAULT_BRAIN` =
  a cloud model). One model answers; that's the whole "mind." It is NOT composed.
- **The supervisor (`runtime/session_supervisor.py`):** the single launcher of the fleet — wake / consult /
  spawn / point-in-time FORK, per-turn watchdog, concurrency cap, the agent_sessions event log. It SEES the
  whole fabric (every session, its state, its recall). Today it's a service the lead drives, NEVER a mind the
  RHM can think WITH.

## THE ARCHITECTURE — the RHM's mind becomes a COMPOSED cognition, not one model
The upgrade (candidate): the brain the host attaches is not "a model" but a **router over cognition sources**.
When the RHM is asked something, the mind resolves WHICH source answers — and the supervisor is one source:

  the RHM mind = resolve(question, coordinate) over sources:
    • the cloud model        — open conversation / synthesis (today's whole mind; stays the default)
    • RECALL (recollection)  — "what was decided / what's in memory" → corpus/session_recall (grounded, no-fiction)
    • THE SUPERVISOR (new)   — "what is the fleet doing / wake that session / what did session X find / run this"
                               → the supervisor's own capabilities, surfaced AS a brain-source the RHM composes.

So "supervisor-as-loadable-brain" = the supervisor's fleet-sight + wake/consult/recall become a SOURCE the RHM
mind can draw on and SPEAK FROM — the RHM can answer "what's the fabric doing right now," "ask the projection
session," "resume the session that was on X," because its mind now includes the supervisor's view, not just a
model's training. The mind is LOADABLE: which sources are mounted is a coordinate (a registry — axes-are-
registries), so a given RHM instance composes the sources its context needs.

## ★ IT IS THE RESOLVER, ONE MORE ALTITUDE (the spine, not a new pattern)
This is `resolve(invariant, coordinate)` at the cognition-source scale — the SAME primitive (runtime/resolver.py)
+ the SAME axis-kinds: the source-selection is a DISCRETE select (question-kind/intent → which source);
each source's own params (model, recall-grain, supervisor-verb) are CONTINUOUS/derived. So the "loadable brain"
is not a new engine — it's the resolver picking a cognition-source by coordinate, exactly as a surface picks an
allocation by device-coordinate. (Grounds in Tim's "the UI is one projection, the tools another, cognition
another — all from one place"; and `universal-evaluator` = resolve-as-runtime, flagged unread, NOT leaned on.)

## THE FLOOR (non-negotiable — the supervisor-mind READS + PROPOSES, never auto-fires)
★ The supervisor can spawn `claude -p` / fork sessions — a CONSEQUENTIAL, lead-only act (autonomous-spawn-lead-
only). So the supervisor-as-BRAIN exposes only the READ + PROPOSE half to the RHM: it can SEE the fleet, RECALL
a session, SURFACE "I could wake session X" — but the actual wake/spawn/dispatch stays a GATED operator action
(the #1b floor; the RHM proposes, the operator/lead fires). The mind reaches the gated verbs but NEVER trips
them (the same floor cognition already honors). A supervisor-source answer that implies an action → surfaces it
as a proposal on the decision/stack surface, never a silent dispatch.

## BUILD SHAPE (when pulled — render-independent now; the mind half is mine, the host half projection's)
1. A `Brain`-contract source-router (the object `forkVBrain.attach` returns) that resolves question→source via
   resolve_slot (select on intent), composes the answer. Mine (cognition/bridge lane).
2. A SUPERVISOR-SOURCE adapter: the supervisor's read/propose capabilities (list fleet · describe session ·
   recall · "could wake/consult X") behind the source interface — READ+PROPOSE only, the gated verbs surfaced
   not fired. Mine (the supervisor is my lane).
3. The host attaches it unchanged (projection's seam already there). A bridge read-API the mind's sources call
   (the /api/sessions·/api/channels·/api/timeline I just built ARE the supervisor-source's data; /api/corpus-query
   + recollection's search ARE the recall-source's). So the read-routes I built this session are already the
   supervisor-mind's substrate.
4. The mounted-source SET is a registry (a loadout) — which sources a given RHM composes is data, not code.

## OPEN (Tim adjudicates — candidacy)
- Does the RHM's mind BECOME multi-source (this), or stay single-model with the supervisor as a separate tool?
  (The multi-source reading is the "loadable brain" Tim/the lead named; offered, his call.)
- The source-selection coordinate (intent/question-kind axis) — its exact axis values settle with the resolver's
  axis-set (Tim's formal roots, in flight).
- Whether RECALL + SUPERVISOR are two sources or one "fabric-memory" source (both-plus-others — likely separate:
  recall = what-was, supervisor = what-IS).

## STATUS
Architecture only (render-independent, my lane, per the lead). The SUBSTRATE is largely already built this
session: the resolver primitive (resolve-by-coordinate), the read-routes (/api/sessions·channels·timeline·board
= the supervisor-source's data), the brain swap-seam (projection's, live). The build is composing these behind
the Brain contract — pulled when the keystone/FACE-1 lands. NOT built ahead of need; specced so it assembles
fast when called.
