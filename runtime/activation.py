"""runtime/activation.py — Concurrent Cognition G5 · ACTIVATION CONTEXTS (the dial, generalised).

NET-NEW substrate (R1-FOLD F7 / R2-FOLD H6): the repo had NO activation substrate — `background` was
only a presence-MODE directive string, there were zero `.timer` units, and the sole backend `while`
loop was the SSE keepalive. G5 generalises "mode" (the presence dial) into a small set of **activation
contexts** — the named ways a cast can fire. Per-turn (the live reply) is already the spine of G0–G4;
G5 adds the THREE non-turn triggers as declared data + real entry points:

  • background — an IDLE-LOOP tick fires the mode's cast → destinations surface/address/lane (NO reply).
  • sense      — an EVENT-HOOK (screen/app/state change) fires the cast given a synthetic sense event.
  • rollup     — a TIMER tick runs the introspective-data-building consolidation of the swarm's OWN
                 `run://`-addressed run-records (the C1.6 `cognition.wave` telemetry) into ONE rollup
                 record at a run:// address (read-half — it does NOT fire a swarm).

WHAT THIS BUILDS vs WHAT IS needs-tim:
  This builds the activation-context REGISTRY (L1 declared data), the trigger ENTRY POINTS, and the
  mode→loadout allocation. The ALWAYS-ON DRIVERS that *call* these entry points (the idle-loop daemon,
  the OS/bridge event-hook source, the timer/`.timer` scheduler) are a SYSTEM-LIFECYCLE + GPU-always-on
  concern → flagged needs-tim (per the loadout directive — do NOT stand up an always-on GPU-consuming
  daemon; that is Tim's call). The mechanism is proven by USE: invoking the entry point fires the cast.

THE LAWS THIS HONORS (binding):
  L1 — activation contexts are DECLARED registry data; a MODE allocates which are live + the budget.
  L2 — a model runs only inside a ROLE (run_swarm fires run_role); rules ROUTE the outputs.
  run:// — every address is run:// (never swarm://; contracts/address.py SCHEMES).
  THE FLOOR (G9 / C9.2) — a background/sense/rollup cast emits NO resolve/approve/dispatch. It reuses
    rules.route() over the FIVE DESTINATION_KINDS (surface goes through surface_review → an `ask`, never
    a resolve). The floor holds BY CONSTRUCTION — this module never names a forbidden verb.
  THE RESERVE IS SACRED — a non-turn cast runs under the mode's SlotBudget, bounded by the SAME
    process-wide VRAM gate (cognition.global_vram_gate) the per-turn stream uses; the swarm sub-pool is
    capped at swarm_slots = max_num_seqs − R, so R permits ALWAYS stay free for the live per-turn call.
    fire_activation FAILS LOUD if a mode declares reserve_r below the floor (FLOOR_RESERVE_R).
  reuse-don't-parallel — run_swarm (G1), rules.route (G3), surface_review (the inbox), run_stats' dist
    (the rollup math) are all REUSED. No second scheduler, no second executor, no second inbox.

DRIFT HOME: the ACTIVATION_CONTEXTS registry declares its self-description home in runtime/AGENTS.md
(alongside RULE_OPS/DESTINATION_KINDS/THOUGHT_SHAPES/PART_GRAIN); tests/activation_contexts_acceptance.py
asserts it stays reflected there (mirrors rules_acceptance → RULE_OPS).
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable

from runtime import cognition as _cog
from runtime import rules as _rules


# The floor on R: a mode may NEVER declare fewer reserved slots than this for the live per-turn stream.
# (C5.5 — the live-stream reserve is sacred; a background swarm can't starve the per-turn call.)
FLOOR_RESERVE_R = _cog.DEFAULT_RESERVE_R   # 2 (R2-FOLD H1: R=2 reservation)


# =====================================================================================================
# THE ACTIVATION-CONTEXT REGISTRY (L1 declared data) — the net-new substrate.
#
# Each context DECLARES (never invents at fire-time): its TRIGGER kind (what wakes it — the needs-tim
# always-on driver), whether it produces a spoken REPLY, the allowed DESTINATION_KINDS its routed
# outputs may use, and whether it FIRES A SWARM (rollup is read-half — it consolidates, it does not fire).
# A MODE allocates which contexts are LIVE + the slot budget (see Suite.ACTIVATION_ALLOCATION, C5.5).
# Add a context = a row here + reflect it in runtime/AGENTS.md (the drift home) or the acceptance fails.
# =====================================================================================================
ACTIVATION_CONTEXTS: dict[str, dict] = {
    # C5.1 — PER-TURN: the live reply (the spine of G0–G4). NOT fired here (chat()/chat_parts() own it);
    # registered as the BASELINE context so C5.5 can compare it + the spine is asserted, never rebuilt.
    "per-turn": {
        "trigger": "turn",
        "trigger_driver": "the operator's chat/voice turn (bridge /api/chat, the voice stream) — ALREADY LIVE",
        "reply": True,
        "fires_swarm": True,
        "owned_by": "chat()/chat_parts() (G0–G4 spine — NOT fire_activation)",
        "destinations": ["inject"],            # the staged reply injects role outputs into the final part
        "desc": "the live per-turn reply — the cognition spine; G5 asserts it, never rebuilds it",
    },
    # C5.2 — BACKGROUND: an IDLE-LOOP tick fires the mode's cast between turns; NO spoken reply.
    "background": {
        "trigger": "idle-loop",
        "trigger_driver": "an idle-loop tick (system-lifecycle; NEEDS-TIM — no always-on daemon stood up)",
        "reply": False,
        "fires_swarm": True,
        "owned_by": "fire_activation",
        "destinations": ["surface", "address", "lane"],   # never inject (no reply) / never resolve (floor)
        "desc": "between-turn consolidation/preparation under the mode's budget; lands at surface/address/lane",
    },
    # C5.3 — SENSE-TRIGGERED: an EVENT-HOOK (screen/app/state change) fires the cast given a sense event.
    "sense": {
        "trigger": "event-hook",
        "trigger_driver": "a screen/app/state-change event source (system-lifecycle; NEEDS-TIM — synthetic event proves it)",
        "reply": False,
        "fires_swarm": True,
        "owned_by": "fire_activation",
        "destinations": ["surface", "address", "lane"],
        "desc": "fires the cast on a sense event (not a user turn); the cast sees the event as its utterance",
    },
    # C5.4 — ROLLUPS: a TIMER tick consolidates the swarm's OWN run-records (cognition.wave) → ONE rollup.
    "rollup": {
        "trigger": "timer",
        "trigger_driver": "a timer/scheduler tick (system-lifecycle; NEEDS-TIM — no .timer stood up)",
        "reply": False,
        "fires_swarm": False,                  # READ-HALF: consolidates existing run-records, fires no role
        "owned_by": "consolidate_rollup",
        "destinations": ["address"],           # the rollup record lands at a run:// address
        "desc": "introspective-data-building: the swarm's run-records consolidated into a rollup distribution",
    },
}


@dataclass
class ActivationResult:
    """The captured artifact of one fired activation context (the proof C5.2/C5.3/C5.4 read by use)."""
    context: str
    mode: str
    turn_id: str
    trigger: str
    reply: bool                               # did this context produce a spoken reply? (background/sense: False)
    fired_roles: list = field(default_factory=list)     # role ids fired this wave (empty for rollup)
    routed: list = field(default_factory=list)          # the route() outcome records (surface/address/lane)
    budget: dict = field(default_factory=dict)          # the SlotBudget snapshot (the reserve proof)
    rollup: dict | None = None                # the consolidated distribution (rollup context only)
    address: str | None = None                # where the rollup landed (rollup context only)
    wall_s: float = 0.0


def _gather_rules(fireable, suite) -> list:
    """Gather the buildable G3 declared rules from the cast (reuse-don't-parallel — the SAME engine
    chat_parts() uses for C4.2): the canonical INJECTION_RULE plus any AST-shaped `rules` a role
    declares. Descriptive (non-AST) role rule entries are skipped (not routing rules)."""
    out = []
    if getattr(_cog, "INJECTION_RULE", None) is not None:
        out.append((None, _cog.INJECTION_RULE))
    for role in fireable:
        rspecs = (role.spec.get("rules") if hasattr(role, "spec") else None) or []
        for rspec in rspecs:
            rule = suite._rule_from_spec(rspec)   # reuse the Suite's G3 builder (one engine)
            if rule is not None:
                out.append((role.id, rule))
    return out


def fire_activation(suite, context: str, *, mode: str | None = None,
                    sense_event: dict | None = None,
                    turn_id: str | None = None,
                    base_url: str = _cog.RESIDENT_BASE_URL,
                    model: str = _cog.RESIDENT_MODEL) -> ActivationResult:
    """THE NON-TURN TRIGGER ENTRY POINT (C5.2/C5.3) — fire a mode's cast in an activation context WITHOUT
    a user turn. Reuses run_swarm (G1) to fire the cast and rules.route (G3) to dispatch the outputs over
    the FIVE non-consequential DESTINATION_KINDS — so the G9 floor (no resolve/approve/dispatch) holds by
    construction. Produces NO spoken reply (C5.2 — destinations surface/address/lane, never inject).

    `context` — 'background' (idle-loop trigger) or 'sense' (event-hook trigger). 'per-turn' is owned by
                chat()/chat_parts() and 'rollup' by consolidate_rollup — calling those here fails loud.
    `mode`    — the presence mode whose CAST + slot BUDGET allocate this fire (C5.5; default = current).
    `sense_event` — for the sense context: the screen/app/state event the cast sees as its utterance
                (the real event SOURCE is needs-tim; a synthetic event proves the mechanism).

    THE RESERVE (C5.5, sacred): the cast runs under the mode-allocated SlotBudget bounded by the SAME
    process-wide VRAM gate as the per-turn stream; the swarm sub-pool is capped at swarm_slots so R
    permits ALWAYS remain free for the live per-turn call. Fails loud if the mode under-reserves R."""
    spec = ACTIVATION_CONTEXTS.get(context)
    if spec is None:
        raise ValueError(f"fire_activation: unknown activation context {context!r} — registered: "
                         f"{sorted(ACTIVATION_CONTEXTS)} (fail loud, never fire a fabricated context).")
    if spec["owned_by"] != "fire_activation":
        raise ValueError(f"fire_activation: context {context!r} is owned by {spec['owned_by']!r}, not the "
                         f"non-turn trigger entry point (per-turn=chat/chat_parts; rollup=consolidate_rollup).")
    mode = mode or suite.get_mode()
    turn_id = turn_id or _activation_turn_id(context)

    # C5.5 — the MODE allocates the live contexts + the slot budget. Fail loud if this context is not
    # declared LIVE for this mode (rule 8 — never fire a context the mode didn't allocate).
    alloc = suite.activation_allocation(mode)
    if context not in alloc["live"]:
        raise ValueError(f"fire_activation: context {context!r} is NOT live for mode {mode!r} "
                         f"(live: {sorted(alloc['live'])}). A mode allocates its activation contexts (C5.5).")
    # THE RESERVE FLOOR (sacred): a mode may never under-reserve R for the live per-turn stream.
    reserve_r = int(alloc["reserve_r"])
    if reserve_r < FLOOR_RESERVE_R:
        raise ValueError(f"fire_activation: mode {mode!r} declares reserve_r={reserve_r} < the FLOOR "
                         f"{FLOOR_RESERVE_R} — a non-turn cast may NEVER starve the per-turn reserve (C5.5).")
    budget = _cog.SlotBudget.from_registry(reserve_r=reserve_r,
                                           per_role_ctx=int(alloc["per_role_ctx"]),
                                           main_ctx_tokens=int(alloc.get("main_ctx_tokens", 0)),
                                           services_path=suite.cognition_services_path())

    cast = suite.cast_for_mode(mode)
    fireable = [r for r in cast if getattr(r, "can_fire", False) and not getattr(r, "is_jury", False)]

    # the CAST sees a context-appropriate utterance (background/sense have no user utterance — define it):
    if context == "sense":
        if not isinstance(sense_event, dict):
            raise ValueError("fire_activation('sense'): needs a sense_event dict (the screen/app/state "
                             "change the cast reacts to) — fail loud, never fire on a fabricated event.")
        utterance = sense_event.get("summary") or str(sense_event)
    else:  # background
        utterance = "[background] consolidate/prepare between turns; surface only what genuinely needs the operator."

    result = ActivationResult(context=context, mode=mode, turn_id=turn_id, trigger=spec["trigger"],
                              reply=spec["reply"], budget={"swarm_slots": budget.swarm_slots,
                              "reserve_r": budget.reserve_r, "max_num_seqs": budget.max_num_seqs,
                              "knee": budget.source.get("knee"), "source": budget.source})
    result.fired_roles = [r.id for r in fireable]

    suite._emit("activation", f"{context} cast fired ({mode}, {len(fireable)} roles, no reply)",
                context=context, mode=mode, turn_id=turn_id, trigger=spec["trigger"],
                address="ui://chrome/toolbar")

    t0 = time.monotonic()
    if not fireable:
        # a mode whose cast is empty fires nothing (never a crash, never a default-fire — rule 8).
        result.wall_s = round(time.monotonic() - t0, 3)
        return result

    wave = _cog.run_swarm(fireable, {"utterance": utterance}, suite.store, turn_id=turn_id,
                          budget=budget, emit=suite._emit, base_url=base_url, model=model)
    resolved = dict(wave.resolved)

    # G3 declared rules decide what is ROUTED — reuse rules.route() over the non-consequential destinations.
    # An inject decision is DROPPED for a no-reply context (background/sense produce no part to inject into).
    for role_id, rule in _gather_rules(fireable, suite):
        if not (rule.inputs <= set(resolved)):
            continue                                       # per-rule readiness: not ready this wave → skip
        decision = rule.decide(resolved)                   # fail loud on a real error (the law)
        if not decision.get("fire"):
            continue
        if rule.destination == "inject":
            # no reply part exists in a non-turn context → an inject route has nowhere to land. We do NOT
            # silently no-op; we RE-LAND it at a run:// address (a durable write, no reply impact) so the
            # value isn't lost AND the floor stays clean (address is in the allowed set, never resolve).
            addr = f"run://{turn_id}/bg-inject/{decision.get('rule')}"
            cas = suite.store.put_content(decision.get("value"))
            suite.store.set_ref(addr, cas)
            result.routed.append({"rule": decision.get("rule"), "destination": "address",
                                  "from": "inject(no-reply→address)", "address": addr, "acted": True})
            continue
        if rule.destination not in spec["destinations"]:
            raise ValueError(f"fire_activation: rule {decision.get('rule')!r} routes to "
                             f"{rule.destination!r}, not allowed for context {context!r} "
                             f"(allowed: {spec['destinations']}). Fail loud.")
        out = _rules.route(decision, store=suite.store, suite=suite, turn_id=turn_id, emit=suite._emit)
        result.routed.append(out)

    result.wall_s = round(time.monotonic() - t0, 3)
    return result


def consolidate_rollup(suite, *, since: int = -1, mode: str | None = None,
                       turn_id: str | None = None, gc: bool = False) -> ActivationResult:
    """THE ROLLUP TRIGGER ENTRY POINT (C5.4) — the introspective-data-building consolidation of the
    swarm's OWN run-records into ONE rollup record at a run:// address. This is the READ-HALF (it
    fires NO swarm — rule 8): it reads the existing `cognition.wave` telemetry (the C1.6 batched
    rollups run_swarm already emits), aggregates per-role latency into DISTRIBUTIONS (reusing run_stats'
    `dist` math — never a parallel aggregator), and lands the result at run://rollup/<id>.

    'persisted + GC'd' (C5.4): the rollup is PERSISTED at its run:// address (content-addressed store).
    On GC — the FsStore is WRITE-ONCE CAS + append-only refs/events BY DESIGN (no ref-deletion / tombstone
    primitive; `set_ref` takes a cas string, never None). So GC here REPORTS the run:// refs the rollup
    superseded (the per-role run://<turn>/<role> refs it consolidated) as RECLAIMABLE — it does NOT delete
    them, and it NEVER touches the append-only event log (the seq invariant forbids deletion). Actual
    reclamation is a STORE-POLICY concern (a retention/GC pass on the addressed store) — out of G5's scope
    and flagged needs-tim, never bolted on as a parallel deleter. gc=True returns the reclaimable set.

    `since` — an event seq (default -1 = all); the timer driver advances this cursor each tick.
    The TIMER that calls this on a cadence is needs-tim (no .timer stood up)."""
    import statistics
    mode = mode or suite.get_mode()
    turn_id = turn_id or _activation_turn_id("rollup")

    # READ the swarm's own run-records: the cognition.wave events run_swarm emits (C1.6). Each carries
    # `summary` = the batched dict {turn_id, n_roles, wall_s, roles:[{role, address, ok, ms, ...}]}.
    waves = [e for e in suite.events_since(since) if e.get("kind") == "cognition.wave"]
    per_role: dict[str, list[int]] = {}
    addresses: list[str] = []
    n_waves = 0
    for e in waves:
        payload = e.get("summary")
        if not isinstance(payload, dict):
            continue
        n_waves += 1
        for rr in payload.get("roles", []):
            if not isinstance(rr, dict):
                continue
            rid = rr.get("role")
            ms = rr.get("ms")
            if rid is not None and isinstance(ms, (int, float)):
                per_role.setdefault(rid, []).append(int(ms))
            if rr.get("address"):
                addresses.append(rr["address"])

    def dist(vals):                                        # the run_stats distribution shape (reused math)
        vals = sorted(v for v in vals if isinstance(v, (int, float)))
        if not vals:
            return None
        n = len(vals)
        return {"n": n, "median": round(statistics.median(vals), 1),
                "p95": vals[min(n - 1, int(round(0.95 * (n - 1))))], "min": vals[0], "max": vals[-1]}

    rollup = {
        "kind": "cognition.rollup", "turn_id": turn_id, "mode": mode, "since": since,
        "n_waves": n_waves, "n_role_runs": sum(len(v) for v in per_role.values()),
        "by_role": {rid: {"ms": dist(ms)} for rid, ms in sorted(per_role.items())},
    }
    # PERSIST the rollup at a run:// address (content-addressed; durable).
    addr = f"run://rollup/{turn_id}"
    cas = suite.store.put_content(rollup)
    suite.store.set_ref(addr, cas)
    suite._emit("activation", f"rollup consolidated {n_waves} waves · {rollup['n_role_runs']} role-runs → {addr}",
                context="rollup", mode=mode, turn_id=turn_id, trigger="timer", address="ui://chrome/toolbar")

    reclaimable = []
    if gc:
        # REPORT the run:// refs this rollup superseded as RECLAIMABLE (the store is write-once CAS +
        # append-only — there is no ref-deletion primitive; actual reclamation is a store-policy pass,
        # needs-tim). We NEVER touch the append-only event log. This is the honest "GC" surface today:
        # which addresses a retention pass could reclaim, not a deletion this module performs.
        reclaimable = [a for a in addresses if a.startswith("run://") and suite.store.head(a) is not None]

    result = ActivationResult(context="rollup", mode=mode, turn_id=turn_id, trigger="timer",
                              reply=False, fired_roles=[], rollup=rollup, address=addr)
    result.routed = [{"destination": "address", "address": addr, "acted": True}]
    if gc:
        result.rollup["gc_reclaimable"] = reclaimable
    return result


def _activation_turn_id(context: str) -> str:
    return f"act-{context}-" + time.strftime("%Y%m%d-%H%M%S-") + str(int(time.monotonic() * 1000) % 100000)
