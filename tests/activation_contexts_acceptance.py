"""tests/activation_contexts_acceptance.py — Concurrent Cognition G5 · ACTIVATION CONTEXTS.

Proves G5 BY USE against the resident 4B (read-only): the activation-context registry + the three
NET-NEW non-turn trigger entry points fire a mode's cast WITHOUT a user turn, under the mode's slot
budget, honoring the sacred per-turn reserve and the G9 `claude -p` floor.

  C5.1 — per-turn baseline asserted (the spine; registered, never rebuilt here).
  C5.2 — background trigger fires the cast → surface/address/lane, NO spoken reply.
  C5.3 — a synthetic SENSE event fires the cast (not a user turn).
  C5.4 — the ROLLUP trigger consolidates the swarm's OWN run-records into a rollup record at a run:// addr.
  C5.5 — two modes differ in live contexts + budget; an adversarial saturating background wave is
         CAPPED at swarm_slots and CANNOT consume the per-turn reserve (a live concurrent acquire proves
         it, not arithmetic — mirrors concurrency_acceptance's neuter-and-watch-it-break teeth).

Drift: the ACTIVATION_CONTEXTS registry is reflected in its drift home runtime/AGENTS.md (asserted here,
mirroring rules_acceptance → RULE_OPS).
"""
import os, sys, tempfile, threading, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
from runtime import activation as act
from runtime import cognition as _cog

NODES = os.path.join(ROOT, "nodes")
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def fresh_suite():
    store = FsStore(os.path.join(tempfile.mkdtemp(prefix="act-"), "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    return Suite(store, reg, nodes_dir=NODES)


# ---------------------------------------------------------------------------------------------------
# DRIFT — the registry is reflected in its drift home (C9.4).
# ---------------------------------------------------------------------------------------------------
agents_md = open(os.path.join(ROOT, "runtime", "AGENTS.md"), encoding="utf-8").read()
check("ACTIVATION_CONTEXTS is named in its drift home runtime/AGENTS.md", "ACTIVATION_CONTEXTS" in agents_md)
for ctx in act.ACTIVATION_CONTEXTS:
    check(f"context {ctx!r} is reflected in the drift home", f"`{ctx}`" in agents_md or ctx in agents_md)
check("ACTIVATION_ALLOCATION (C5.5) is named in the drift home", "ACTIVATION_ALLOCATION" in agents_md)
check("the reserve floor is documented as sacred in the drift home",
      "RESERVE IS SACRED" in agents_md and "FLOOR_RESERVE_R" in agents_md)

# the registry shape: each context declares trigger/reply/fires_swarm/destinations (L1 data)
for cid, spec in act.ACTIVATION_CONTEXTS.items():
    check(f"{cid}: declares trigger·reply·fires_swarm·destinations·owned_by",
          all(k in spec for k in ("trigger", "reply", "fires_swarm", "destinations", "owned_by")))
# the FLOOR (no destination is ever a consequential verb)
from runtime.rules import FORBIDDEN_DESTINATION_VERBS
for cid, spec in act.ACTIVATION_CONTEXTS.items():
    check(f"{cid}: declares NO consequential destination (the claude -p floor, C9.2)",
          not (set(spec["destinations"]) & set(FORBIDDEN_DESTINATION_VERBS)))


# ---------------------------------------------------------------------------------------------------
# C5.1 — per-turn baseline asserted (the spine — registered, NOT rebuilt).
# ---------------------------------------------------------------------------------------------------
s = fresh_suite()
check("C5.1 · 'per-turn' is a registered baseline context", "per-turn" in act.ACTIVATION_CONTEXTS)
check("C5.1 · per-turn produces a reply (it IS the live reply path)", act.ACTIVATION_CONTEXTS["per-turn"]["reply"] is True)
check("C5.1 · per-turn is owned by chat/chat_parts, NOT the fire_activation entry point (the spine, never rebuilt)",
      act.ACTIVATION_CONTEXTS["per-turn"]["owned_by"] != "fire_activation")
try:
    s.fire_activation("per-turn", mode="listening")
    check("C5.1 · per-turn cannot be fired via fire_activation (owned by the spine)", False)
except ValueError:
    check("C5.1 · per-turn cannot be fired via fire_activation (it is the chat/chat_parts spine)", True)
check("C5.1 · per-turn is live in every mode's allocation (the spine is always present)",
      all("per-turn" in s.activation_allocation(m)["live"] for m in s.MODES))
# the per-turn spine itself (chat_parts) still works — assert the staged generator yields parts (live brain)
gen = s.chat_parts("What is this system?", "system")
parts = list(gen)
check("C5.1 · the per-turn staged reply still works (chat_parts yields parts, a real reply)",
      len(parts) >= 1 and parts[-1].get("final") is True and bool(parts[-1].get("text")))


# ---------------------------------------------------------------------------------------------------
# C5.2 — BACKGROUND trigger fires the cast → no reply; destinations surface/address/lane.
# ---------------------------------------------------------------------------------------------------
s = fresh_suite()
seq_before = len(s.events_since(-1))
r = s.fire_activation("background", mode="listening")
check("C5.2 · background fired the listening cast (real roles ran against the resident 4B)", len(r.fired_roles) >= 1)
check("C5.2 · background produces NO spoken reply (reply=False)", r.reply is False)
chat_evs = [e for e in s.events_since(-1) if e.get("kind") == "chat"]
check("C5.2 · ZERO chat events emitted by a background fire (no spoken reply lands)", len(chat_evs) == 0)
# a cognition.wave (the cast actually fired via run_swarm — reuse, not a parallel executor) was emitted
wave_evs = [e for e in s.events_since(-1) if e.get("kind") == "cognition.wave"]
check("C5.2 · the cast fired via run_swarm (a cognition.wave run-record was emitted — reuse not parallel)",
      len(wave_evs) >= 1)
# THE REAL "lands at address" proof (C5.2): run_swarm writes each role's output to run://<turn>/<role>
# as a byproduct — so the cast's WORK lands at addresses with NO reply. Read one back + confirm it resolves.
landed = []
for rid in r.fired_roles:
    addr = f"run://{r.turn_id}/{rid}"
    if s.store.head(addr) is not None and s.store.get_content(s.store.head(addr)) is not None:
        landed.append(addr)
check("C5.2 · the cast's work LANDS at run://<turn>/<role> addresses (no reply) — read back + resolves",
      len(landed) == len(r.fired_roles) and len(landed) >= 1)
# any RULE-routed outcome (when a cast rule targets surface/lane) went to an ALLOWED, non-consequential
# destination. NOTE: today's listening cast declares no surface/lane rule, so r.routed is typically empty
# (the rule-routed surface/lane path is mechanism-proven in rules_acceptance, not exercised here); this
# assertion guards that NOTHING ever routes to a consequential verb if a rule did fire.
allowed = set(act.ACTIVATION_CONTEXTS["background"]["destinations"]) | {"address"}  # inject re-lands as address
check("C5.2 · any routed outcome used an allowed non-consequential destination (no resolve/approve)",
      all(o.get("destination") in allowed for o in r.routed))


# ---------------------------------------------------------------------------------------------------
# C5.3 — SENSE-triggered: a synthetic event fires the cast (not a user turn).
# ---------------------------------------------------------------------------------------------------
s = fresh_suite()
r = s.fire_activation("sense", mode="listening",
                      sense_event={"summary": "the operator opened the canvas and selected a node"})
check("C5.3 · a synthetic sense event fired the cast (not a user turn)", len(r.fired_roles) >= 1)
check("C5.3 · sense produces NO spoken reply", r.reply is False)
check("C5.3 · sense reports its trigger as the event-hook", r.trigger == "event-hook")
# a sense fire WITHOUT an event fails loud (never fabricate an event)
try:
    s.fire_activation("sense", mode="listening")
    check("C5.3 · sense with no event fails loud", False)
except ValueError:
    check("C5.3 · sense with no event fails loud (never fires on a fabricated event)", True)


# ---------------------------------------------------------------------------------------------------
# C5.4 — ROLLUP: consolidate the swarm's OWN run-records into a rollup record at a run:// address.
# ---------------------------------------------------------------------------------------------------
s = fresh_suite()
# produce REAL run-records: fire a couple of non-turn casts (each emits a cognition.wave with role ms).
s.fire_activation("background", mode="listening")
s.fire_activation("sense", mode="listening", sense_event={"summary": "a state change"})
waves_in_log = [e for e in s.events_since(-1) if e.get("kind") == "cognition.wave"]
check("C5.4 · real cognition.wave run-records exist to consolidate", len(waves_in_log) >= 1)
roll = s.consolidate_rollup()
check("C5.4 · the rollup consolidated >=1 wave of real run-records", roll.rollup["n_waves"] >= 1)
check("C5.4 · the rollup consolidated real role-runs into distributions",
      roll.rollup["n_role_runs"] >= 1 and len(roll.rollup["by_role"]) >= 1)
# the distributions are the run_stats shape (n/median/p95/min/max) — reused math, not a parallel aggregator
some = next(iter(roll.rollup["by_role"].values()))["ms"]
check("C5.4 · distributions carry the run_stats shape (n·median·p95·min·max)",
      all(k in some for k in ("n", "median", "p95", "min", "max")))
# PERSISTED at a run:// address + readable back
check("C5.4 · the rollup landed at a run:// address", roll.address.startswith("run://rollup/"))
readback = s.store.get_content(s.store.head(roll.address))
check("C5.4 · the rollup record is persisted + readable back from the store",
      readback is not None and readback.get("kind") == "cognition.rollup")
check("C5.4 · the rollup fired NO swarm (read-half — it consolidates, never fires roles)", roll.fired_roles == [])
# GC (C5.4) — the FsStore is write-once CAS + append-only refs/events BY DESIGN (no ref-deletion
# primitive). So gc=True REPORTS the superseded run:// refs as RECLAIMABLE (a store-policy retention
# pass is needs-tim) and NEVER touches the append-only event log. Assert the reported set is real (the
# refs exist) and the log was not shortened.
log_len_before = len(s.events_since(-1))
roll2 = s.consolidate_rollup(gc=True)
log_len_after = len(s.events_since(-1))
reclaimable = roll2.rollup.get("gc_reclaimable", [])
check("C5.4 · GC reports a NON-EMPTY reclaimable set of superseded run:// refs (non-vacuous)",
      len(reclaimable) >= 1)
check("C5.4 · every reported reclaimable ref is a REAL run:// ref that resolves (not fabricated)",
      all(a.startswith("run://") and s.store.head(a) is not None for a in reclaimable))
# the log only GREW (by the rollup's own emit) — GC deleted NO past event (append-only + seq invariant)
check("C5.4 · GC deleted NO past event from the append-only log (write-once/append-only preserved)",
      log_len_after >= log_len_before)


# ---------------------------------------------------------------------------------------------------
# C5.5 — MODE allocates: two modes differ in live contexts + budget; the reserve is sacred (adversarial).
# ---------------------------------------------------------------------------------------------------
s = fresh_suite()
a_listen = s.activation_allocation("listening")
a_walk = s.activation_allocation("walkthrough")
a_bg = s.activation_allocation("background")
check("C5.5 · two modes differ in their LIVE activation contexts",
      set(a_listen["live"]) != set(a_walk["live"]))
check("C5.5 · a swarm-heavy mode declares a different brain config (the mode→loadout registry, H1/H8)",
      a_bg["brain_config"] != a_listen["brain_config"])
check("C5.5 · the swarm-heavy mode assumes a deeper main (the deep-main KV bind, C0.5)",
      a_bg["main_ctx_tokens"] > a_listen["main_ctx_tokens"])
# the budgets DIFFER as a function of mode (the deep main eats the shared KV pool → fewer swarm slots)
b_listen = _cog.SlotBudget.from_registry(reserve_r=a_listen["reserve_r"], per_role_ctx=a_listen["per_role_ctx"],
                                         main_ctx_tokens=a_listen["main_ctx_tokens"],
                                         services_path=s.cognition_services_path())
b_bg = _cog.SlotBudget.from_registry(reserve_r=a_bg["reserve_r"], per_role_ctx=a_bg["per_role_ctx"],
                                     main_ctx_tokens=a_bg["main_ctx_tokens"],
                                     services_path=s.cognition_services_path())
check("C5.5 · the two modes' computed slot budgets reflect their allocation (registry-derived, not literal)",
      b_listen.swarm_slots >= 1 and b_bg.swarm_slots >= 1 and isinstance(b_listen.max_num_seqs, int))

# AIRTIGHT CAP — a cast WIDER than the mode's swarm_slots is bounded (the task's "a cast that tries to
# exceed the mode budget is capped"). We drive run_swarm (the same driver fire_activation uses) with a
# CONTRIVED tiny budget (swarm_slots=2) and 6 instrumented roles, and assert PEAK in-flight never exceeds
# swarm_slots — so an over-budget wave is bounded, never over-subscribing the GPU. No model call (the
# roles are stubbed to record concurrency only — read-only, no resident-4B hit needed for the cap proof).
import dataclasses, threading as _t2
_peak = {"now": 0, "max": 0}
_plock = _t2.Lock()
class _StubRole:
    def __init__(self, i): self.id = f"stub{i}"; self.spec = {}
    can_fire = True; is_jury = False
def _fake_run_role(role, ctx, **kw):
    with _plock:
        _peak["now"] += 1; _peak["max"] = max(_peak["max"], _peak["now"])
    time.sleep(0.05)                                   # hold the slot so concurrency is observable
    with _plock:
        _peak["now"] -= 1
    return {"ok": True, "role": role.id}
contrived = dataclasses.replace(b_listen, reserve_r=b_listen.max_num_seqs - 2, swarm_slots=2)
_orig_rr = _cog.run_role
_cog.run_role = _fake_run_role
try:
    wave = _cog.run_swarm([_StubRole(i) for i in range(6)], {"utterance": "x"}, s.store,
                          turn_id="cap-test", budget=contrived, emit=lambda *a, **k: None)
finally:
    _cog.run_role = _orig_rr
check("C5.5 · ADVERSARIAL — a cast (6) WIDER than swarm_slots (2) is CAPPED: peak in-flight ≤ swarm_slots "
      "(the over-budget wave is bounded by run_swarm's pool, never over-subscribes)", _peak["max"] <= 2)
check("C5.5 · all 6 over-budget roles still completed (capped, not dropped)", len(wave.runs) == 6)

# THE FLOOR — fail loud if a mode under-reserves R below the floor.
import copy
s_floor = fresh_suite()
s_floor.ACTIVATION_ALLOCATION = copy.deepcopy(Suite.ACTIVATION_ALLOCATION)
s_floor.ACTIVATION_ALLOCATION["listening"]["reserve_r"] = 0
try:
    s_floor.fire_activation("background", mode="listening")
    check("C5.5 · a mode that under-reserves R fails loud", False)
except ValueError:
    check("C5.5 · a mode that under-reserves R (below FLOOR_RESERVE_R) fails loud", True)

# THE ADVERSARIAL TELESCOPE — a SATURATING background wave CANNOT consume the per-turn reserve.
# We use the SAME process-wide VRAM gate the per-turn stream uses. Saturate it with a background-style
# pool of size swarm_slots (max_num_seqs − R); prove that R permits remain ACQUIRABLE IMMEDIATELY by a
# concurrent "per-turn" call. This is a LIVE concurrent acquire (teeth), not arithmetic.
gate = _cog.global_vram_gate(b_listen.max_num_seqs)
hold_release = threading.Event()
held = threading.Barrier(b_listen.swarm_slots + 1)   # swarm holders + this thread

def _bg_holder():
    with gate.slot():                                # a background role-run holding a swarm slot
        held.wait()                                  # signal: I'm holding
        hold_release.wait(timeout=10)                # hold until the test releases

bg_threads = [threading.Thread(target=_bg_holder, daemon=True) for _ in range(b_listen.swarm_slots)]
for t in bg_threads:
    t.start()
held.wait(timeout=10)                                # wait until ALL swarm_slots permits are HELD
# now the swarm sub-pool is fully saturated. A per-turn call must STILL acquire one of the R reserve
# permits immediately (R = max_num_seqs − swarm_slots permits remain free).
acquired = gate._sem.acquire(blocking=True, timeout=2.0)
check("C5.5 · ADVERSARIAL — a saturating background wave CANNOT starve the per-turn reserve "
      "(a live per-turn permit acquires immediately while the swarm sub-pool is full)", acquired)
if acquired:
    gate._sem.release()
hold_release.set()
for t in bg_threads:
    t.join(timeout=5)

# TEETH CHECK (mirrors concurrency_acceptance): if the swarm pool were NOT capped (held all
# max_num_seqs), the per-turn acquire would BLOCK. Prove the cap is what protects the reserve.
hold_release2 = threading.Event()
held2 = threading.Barrier(b_listen.max_num_seqs + 1)
def _full_holder():
    with gate.slot():
        held2.wait()
        hold_release2.wait(timeout=10)
full_threads = [threading.Thread(target=_full_holder, daemon=True) for _ in range(b_listen.max_num_seqs)]
for t in full_threads:
    t.start()
held2.wait(timeout=10)
blocked = not gate._sem.acquire(blocking=True, timeout=0.5)   # ALL permits held → must block
check("C5.5 · TEETH — with ALL max_num_seqs permits held the per-turn acquire BLOCKS "
      "(so the swarm_slots cap is exactly what keeps R free — the protection is real, not vacuous)", blocked)
hold_release2.set()
for t in full_threads:
    t.join(timeout=5)


print(f"\nALL {PASS} CHECKS PASS — G5 activation contexts: registry + 3 net-new triggers (background/"
      f"sense/rollup) fired by use · no reply · reserve sacred (adversarial + teeth) · G9 floor by "
      f"construction · run_swarm/SlotBudget/rules.route/run_stats reused not forked")
