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


# =====================================================================================================
# THE DRIVERS (Group H) — the net-new DECISION LAYER over the (already-built) entry points.
#
# G5 built the activation-context substrate + the entry points (fire_activation / consolidate_rollup),
# but left them UNDRIVEN: nothing decided WHEN to fire them. The always-on CALLER (an idle-loop daemon,
# an OS event source, a `.timer`) is a system-lifecycle + GPU-always-on concern → NEEDS-TIM (we do NOT
# stand up an always-on GPU-consuming daemon — that is the operator's call, per the loadout directive).
#
# So H is built as a TICKABLE decision layer, NOT a daemon: each driver is a pure-ish function the
# always-on caller would invoke ON A CADENCE. The net-new is the DECISION/STATE the driver adds OVER the
# entry point (an idle gate · an event→sense_event intake · a held rollup cursor) — never a re-implement
# of fire_activation/consolidate_rollup (those still enforce the mode budget + the sacred reserve). The
# mechanism is proven by USE: feeding a synthetic idle/event/clock tick fires the cast / lands a rollup.
#
# THE FLOOR (G9 / C9.2) holds by construction — every driver routes ONLY through fire_activation /
# consolidate_rollup, which route over the five non-consequential DESTINATION_KINDS (no resolve/approve/
# dispatch). A driver never names a forbidden verb.
# =====================================================================================================

# How long (seconds) the operator must be quiet before the background context is allowed to tick. A
# DECLARED knob (not a magic literal buried in a branch) so the idle gate is legible + tunable; the
# always-on caller may also pass its own threshold per tick.
DEFAULT_IDLE_SECONDS = 90.0

# The event kinds that count as OPERATOR ACTIVITY (a turn / a deliberate operator act) — reading these
# off the shared event log is how the idle gate knows "the operator is quiet". Declared as data (the
# ACTIVATION_CONTEXTS discipline) so what counts as activity is one legible set, never an inline list.
# A spoken turn (chat) and a completed cognition turn are the strongest "the operator is here" signals;
# direct operator graph acts (create/connect/apply/resolve/move) count too — the system reacting to its
# OWN background activity must NOT reset the idle clock, so activation/op.run/cognition.* mid-wave kinds
# are deliberately EXCLUDED.
OPERATOR_ACTIVITY_KINDS: frozenset = frozenset({
    "chat", "cognition.turn.done", "create", "connect", "delete",
    "config", "apply", "resolve", "move", "pin", "annotation",
})


def _iso_to_epoch(ts: str | None) -> float | None:
    """Parse an event's ISO-8601 UTC `ts` (append_event writes datetime.now(timezone.utc).isoformat())
    to epoch seconds. Returns None on a missing/malformed ts (fail-soft for a READ — a single junk ts
    must never crash the idle gate; the gate treats unknown-age as 'no recent activity')."""
    if not ts:
        return None
    try:
        from datetime import datetime
        s = ts.replace("Z", "+00:00")
        return datetime.fromisoformat(s).timestamp()
    except Exception:
        return None


def activity_signal(suite, *, now_epoch: float | None = None) -> dict:
    """THE SHARED ACTIVITY READER (reused by the background idle gate H1 AND the mode detector I1 —
    reuse-don't-parallel: one reader, two consumers). Reads the shared event log and reports a small,
    DETERMINISTIC signal snapshot the drivers/detector decide over:

      • idle_seconds   — seconds since the last OPERATOR_ACTIVITY_KINDS event (None = no activity seen).
      • last_activity  — the kind of that last operator-activity event (None if none seen).
      • mode           — the live presence mode (the operator's current dial).
      • inbox          — count of items awaiting the operator (a 'work is piling up' signal).
      • recent_kinds   — the kinds in the recent window (a cheap shape of what's happening).

    A READ only — it fires nothing and emits nothing (rule 4: a signal read is not an action)."""
    now_epoch = time.time() if now_epoch is None else now_epoch
    events = suite.events_since(-1)
    last_act_ts = None
    last_act_kind = None
    recent_kinds: list[str] = []
    for e in events[-200:]:                                 # a bounded recent window (cheap; not the whole log)
        k = e.get("kind")
        if k:
            recent_kinds.append(k)
        if k in OPERATOR_ACTIVITY_KINDS:
            ep = _iso_to_epoch(e.get("ts"))
            if ep is not None:
                last_act_ts = ep
                last_act_kind = k
    idle_seconds = None if last_act_ts is None else max(0.0, now_epoch - last_act_ts)
    try:
        # The items awaiting the operator are inbox_lanes()'s `live_escalations` lane (resolved is None) —
        # NOT a key named `awaiting` (which inbox_lanes never returns). Reading the wrong key would make
        # `inbox` permanently 0, killing the inbox-based detection rules (focus's inbox==0 / listening's
        # inbox>0) silently. Use the counts.escalations count (the lane's own count, fail-loud-legible).
        lanes = suite.inbox_lanes() if hasattr(suite, "inbox_lanes") else {}
        inbox = int(lanes.get("counts", {}).get("escalations", 0))
    except Exception:
        inbox = 0
    return {
        "idle_seconds": idle_seconds,
        "last_activity": last_act_kind,
        "mode": suite.get_mode(),
        "inbox": inbox,
        "recent_kinds": recent_kinds[-20:],
    }


def background_tick(suite, *, mode: str | None = None, idle_seconds: float = DEFAULT_IDLE_SECONDS,
                    now_epoch: float | None = None) -> dict:
    """H1 · THE BACKGROUND DRIVER — the idle-gate decision over fire_activation('background').

    The net-new is the GATE: a background tick fires the mode's cast ONLY when (a) the mode declares the
    `background` context live (read from the mode's allocation — never hardcoded) AND (b) the operator has
    been QUIET for >= `idle_seconds` (read from the shared activity signal). When it fires, it delegates to
    `fire_activation('background')` — which enforces the mode budget + the sacred reserve + routes the cast
    over surface/address/lane with NO reply (re-used, not re-implemented). When it does NOT fire, it returns
    a legible reason (rule 4 — no silent no-op): the always-on caller / a test sees exactly why.

    The always-on CALLER (the idle-loop that invokes this on a cadence) is NEEDS-TIM (no daemon stood up);
    this is the tickable mechanism it would call. Returns {fired, reason, signal, result?}."""
    mode = mode or suite.get_mode()
    sig = activity_signal(suite, now_epoch=now_epoch)
    alloc = suite.activation_allocation(mode)
    if "background" not in alloc["live"]:
        return {"fired": False, "reason": f"mode {mode!r} does not allocate the background context",
                "signal": sig}
    idle = sig["idle_seconds"]
    if idle is not None and idle < idle_seconds:
        return {"fired": False,
                "reason": f"operator active {round(idle, 1)}s ago (< idle threshold {idle_seconds}s)",
                "signal": sig}
    # idle is None (no recent operator activity seen) OR >= the threshold → the operator is quiet: fire.
    result = suite.fire_activation("background", mode=mode)
    return {"fired": True,
            "reason": ("no recent operator activity" if idle is None
                       else f"operator idle {round(idle, 1)}s (>= {idle_seconds}s)"),
            "signal": sig, "result": result}


def sense_tick(suite, raw_event: dict, *, mode: str | None = None) -> dict:
    """H2 · THE SENSE DRIVER — the event-intake over fire_activation('sense').

    The net-new is the INTAKE: an OS/bridge event source (screen/app/state change) hands the driver a RAW
    event; the driver SHAPES it into the `sense_event` dict fire_activation('sense') expects (a `summary`
    the cast sees as its utterance + the structured fields preserved), gating on whether the mode allocates
    the `sense` context. It then delegates to `fire_activation('sense')` (reused — budget/reserve/route/no-
    reply all enforced there). FAIL LOUD on a non-dict raw event (rule 4/8 — never fabricate a sense event).

    The always-on event SOURCE is NEEDS-TIM (no OS hook stood up); a synthetic raw_event proves the path.
    Returns {fired, reason, sense_event, result?}."""
    if not isinstance(raw_event, dict):
        raise ValueError(f"sense_tick: raw_event must be a dict (the screen/app/state change), got "
                         f"{type(raw_event).__name__} — fail loud, never fire on a fabricated event.")
    mode = mode or suite.get_mode()
    alloc = suite.activation_allocation(mode)
    if "sense" not in alloc["live"]:
        return {"fired": False, "reason": f"mode {mode!r} does not allocate the sense context",
                "raw_event": raw_event}
    # SHAPE the raw event → the sense_event contract (a `summary` the cast reads as its utterance). A raw
    # event without an explicit summary gets one composed from its kind+detail (never a bare str(dict)).
    summary = raw_event.get("summary")
    if not summary:
        kind = raw_event.get("kind") or raw_event.get("type") or "state-change"
        detail = raw_event.get("detail") or raw_event.get("app") or raw_event.get("window") or ""
        summary = f"[{kind}] {detail}".strip()
    sense_event = {**raw_event, "summary": summary}
    result = suite.fire_activation("sense", mode=mode, sense_event=sense_event)
    return {"fired": True, "reason": f"sense event shaped + dispatched ({summary[:60]!r})",
            "sense_event": sense_event, "result": result}


@dataclass
class RollupDriver:
    """H3 · THE ROLLUP DRIVER — the held-cursor decision over consolidate_rollup().

    `consolidate_rollup` already does the introspective-data math (it reads the swarm's cognition.wave
    run-records since a given seq → ONE distribution at run://rollup/<id>). The net-new the DRIVER adds is
    the STATE a timer needs: a `since` cursor HELD across ticks, so tick 2 consolidates ONLY the waves that
    arrived after tick 1 (never re-consolidating the same waves every tick). The cursor advances to the log
    head each tick; an empty interval (no new waves) is a legible no-op, not a wasted/duplicate rollup.

    The TIMER that calls .tick() on a cadence is NEEDS-TIM (no `.timer` stood up); .tick() is the tickable
    mechanism it would call. Reuse-don't-parallel: it owns ONLY the cursor; the consolidation is the
    existing entry point."""
    suite: Any
    since: int = -1                                          # the held cursor (−1 = from the log start)

    def tick(self, *, mode: str | None = None, gc: bool = False) -> dict:
        """One timer tick: consolidate the waves since the held cursor, advance the cursor to the log head,
        and return {consolidated, reason, since_before, since_after, result?}. An interval with no new
        cognition.wave records is a legible no-op (cursor still advances past any non-wave events)."""
        before = self.since
        head = self._head_seq()
        # any new cognition.wave events in (before, head]? (consolidate_rollup uses seq > since.)
        new_waves = [e for e in self.suite.events_since(before)
                     if e.get("kind") == "cognition.wave"]
        if not new_waves:
            self.since = head                                # advance past the (wave-free) interval anyway
            return {"consolidated": False, "reason": "no new cognition.wave records since last tick",
                    "since_before": before, "since_after": self.since}
        result = self.suite.consolidate_rollup(since=before, mode=mode, gc=gc)
        self.since = head                                    # advance the cursor for the next tick
        return {"consolidated": True,
                "reason": f"consolidated {len(new_waves)} new wave(s)",
                "since_before": before, "since_after": self.since, "result": result}

    def _head_seq(self) -> int:
        """The current log head seq (the cursor's new position). −1 when the log is empty (so the next
        tick re-reads from the start — never skips an event by advancing past an empty log)."""
        evs = self.suite.events_since(-1)
        return evs[-1].get("seq", -1) if evs else -1


# =====================================================================================================
# THE MODE AUTO-DETECTOR (Group I) — the net-new that PRODUCES a candidate for the existing toggle.
#
# `Suite.autodetect_mode(candidate)` already honours the off/suggest/auto TOGGLE over a SUPPLIED candidate
# (proven by autodetect_setter_acceptance). The gap (mode-map lost-opportunity #6): NOTHING produced a
# candidate. I1 builds the DETECTOR — a DETERMINISTIC read of the live signal → a candidate mode — and
# FEEDS it to autodetect_mode (never set_mode directly: the toggle decides the posture, off/suggest/auto,
# and a suggestion SURFACES legibly via the existing 'mode' event — it never silently auto-switches
# outside the declared posture).
#
# DETERMINISTIC + REGISTRY-DRIVEN (NOTHING static): the signal→candidate mapping is FILE-DISCOVERED
# DECLARED DATA — the `mode_detection_rules/` registry (suite.mode_detection_rule_registry), walked in
# first-match-wins PRIORITY order. NOT a model (a model would be non-deterministic + GPU-bound; the
# criteria say deterministic-where-possible), NOT an inline if/else ladder, and NOT a hardcoded list (the
# rules USED to be a `MODE_DETECTION_RULES = [...]` literal here with lambda predicates — converted to a
# file-discovered registry so add-a-rule = a FILE not a code edit, and each condition is a declared
# rules.RULE_OPS data-AST not a lambda; see mode_detection_rules/AGENTS.md + runtime/mode_detection_rules.py).
# Each rule's candidate MUST be a registered mode (validated ∈ suite.MODES at detect time — the registry
# can't see the live mode set at discovery; fail-loud here, rule 8). A rule's `when` is pre-validated at
# discovery (rules.validate_ast) + evaluated PURE via rules.evaluate over the activity_signal snapshot.
#
# The always-on CALLER (a tick that runs the detector on a cadence) is the SAME needs-tim seam as the H
# drivers; detect_mode_candidate/propose_mode are the tickable mechanism it would call. Proven by USE:
# a signal that matches a rule produces the declared candidate, which drives the toggle.
# =====================================================================================================


def detect_mode_candidate(suite, *, now_epoch: float | None = None) -> dict:
    """I1 · THE DETECTOR — read the live signal, walk the FILE-DISCOVERED mode-detection-rule registry
    (deterministic, first-match-wins by declared priority), and PRODUCE a candidate mode (or None). A pure
    READ: it fires nothing, switches nothing, emits nothing — it only computes WHAT mode the signal
    suggests. The candidate is validated against suite.MODES (a rule referencing an unregistered mode
    FAILS LOUD — rule 8, never propose a fabricated mode). The rules' `when` conditions are declared
    rules.RULE_OPS data-ASTs (pre-validated at registry discovery; evaluated PURE via rules.evaluate over
    the activity_signal snapshot). Returns {candidate, why, signal, rule, priority, rule_index}
    (candidate=None ⇒ no rule matched; rule_index is the ordinal in the priority-ordered walk)."""
    sig = activity_signal(suite, now_epoch=now_epoch)
    modes = set(suite.MODES)
    for i, rule in enumerate(suite.mode_detection_rule_registry.ordered()):
        cand = rule.candidate
        if cand not in modes:
            raise ValueError(f"detect_mode_candidate: rule {rule.id!r} proposes unregistered mode "
                             f"{cand!r} — one of {sorted(modes)} (rule 8: never fabricate a mode).")
        try:
            matched = rule.matches(sig)
        except Exception as exc:                             # a malformed condition fails loud (rule 4)
            raise ValueError(f"detect_mode_candidate: rule {rule.id!r} condition raised {exc!r}") from exc
        if matched:
            return {"candidate": cand, "why": rule.why, "signal": sig, "rule": rule.id,
                    "priority": rule.priority, "rule_index": i}
    return {"candidate": None, "why": "no detection rule matched the live signal", "signal": sig,
            "rule": None, "priority": None, "rule_index": None}


def propose_mode(suite, *, now_epoch: float | None = None) -> dict:
    """I1 · THE DETECTOR→TOGGLE WIRE — run the detector, and if it produces a candidate that DIFFERS from
    the live mode, FEED it to the existing `Suite.autodetect_mode` (which honours the off/suggest/auto
    toggle: 'off' no-ops, 'suggest' surfaces a 'mode' event, 'auto' switches via the one set_mode). Never
    calls set_mode directly — the toggle owns the posture; the suggestion surfaces legibly, never a silent
    switch outside the declared posture. A candidate EQUAL to the live mode is a no-op (don't re-propose the
    mode already on). Returns {detected, toggle_result?} — the toggle_result is autodetect_mode's legible
    {toggle, candidate, applied, action}."""
    det = detect_mode_candidate(suite, now_epoch=now_epoch)
    cand = det["candidate"]
    if cand is None:
        return {"detected": det, "toggle_result": None, "reason": "no candidate produced"}
    if cand == suite.get_mode():
        return {"detected": det, "toggle_result": None,
                "reason": f"candidate {cand!r} already the live mode (no-op)"}
    toggle_result = suite.autodetect_mode(cand)              # honours off/suggest/auto (the proven toggle)
    return {"detected": det, "toggle_result": toggle_result}
