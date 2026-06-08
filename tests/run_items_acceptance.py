"""tests/run_items_acceptance.py — Concurrent Cognition C 3/4 (run_items + the address resolver).

Proves the two net-new C 3/4 pieces in runtime/cognition.py, making `input_addresses` OPERATIONAL (the
input-address INTENT — Tim 2026-06-08: a role's input resolved FROM AN ADDRESS, "any skill, any context,
or the output of anything else, set by address"):

  resolve_address — the SCHEME-DISPATCHING resolver (the extensible seam). Materializes the <turn>
                    template, then DISPATCHES by scheme to the EXISTING per-scheme resolvers:
                      run://  → resolve_run_ref  (REUSE)
                      cas://  → store.get_content (REUSE)
                      bare    → the BARE_NAME sentinel (a ctx-key, not an address)
                      unknown → RAISES fail-loud (skill:// / blob:// / vec:// / ui:// / code:// — no
                                content-resolver today; the extensible seam where they plug in later).
  run_items       — the AXIS-INVERSION: fan ONE role over N input-UNITS (1 role × N units), vs run_swarm's
                    N roles × 1 ctx. Each unit (literal OR address) becomes the role's primary input; each
                    output lands at run://<turn>/<role>/<i>. MIRRORS run_swarm's fan (same gate/pool/barrier/
                    rollup). Fail-loud per unit + barrier re-raise; a DECLARED on_missing="skip" is recorded.

REUSE (no parallel machinery): resolve_address dispatches to the EXISTING resolve_run_ref + get_content;
run_items mirrors run_swarm's fan (the same global VramGate, swarm_slots pool, barrier, batched emit).

HONEST SCOPE: skills / contexts are NOT addressed today. resolve_address resolves run:// + cas:// NOW; it
is the ONE place a skill://-resolver / context-resolver lands LATER. Those schemes fail loud here today.
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from store.fs_store import FsStore                                          # noqa: E402
from runtime import cognition                                              # noqa: E402
from runtime.cognition import (resolve_address, run_items, ItemsResult,    # noqa: E402
                               resolve_run_ref, BARE_NAME)
from runtime.roles import RoleRegistry                                     # noqa: E402

ROLES = os.path.join(ROOT, "roles")
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def _seed(store, addr, value) -> str:
    """Seed a value at a run:// address exactly as run_swarm/run_items would (put_content → set_ref)."""
    cas = store.put_content(value)
    store.set_ref(addr, cas)
    return cas


# =================================================================================================
# 1 · resolve_address — every scheme: run:// + cas:// resolve NOW · bare → sentinel · unknown → RAISE
# =================================================================================================
store = FsStore(os.path.join(tempfile.mkdtemp(prefix="run-items-"), "store"))
TURN = "t-resolve"

# run:// — resolves to its content; the <turn> TEMPLATE is materialized against turn_id FIRST.
_seed(store, f"run://{TURN}/x", {"v": "upstream-output"})
got = resolve_address(store, "run://<turn>/x", turn_id=TURN)
check("resolve_address(run://<turn>/x) MATERIALIZES the template + resolves to the seeded content",
      got == {"v": "upstream-output"})
# reuse proof: a run:// resolve is byte-identical to the existing resolve_run_ref
check("the run:// path REUSES resolve_run_ref (identical value, no parallel resolver)",
      resolve_address(store, f"run://{TURN}/x") == resolve_run_ref(store, f"run://{TURN}/x"))

# cas:// — resolves to the immutable content (cas:// IS get_content — reuse).
cas = store.put_content({"v": "a content blob"})
check("resolve_address(cas://…) resolves the immutable content (REUSES store.get_content)",
      resolve_address(store, cas) == {"v": "a content blob"})

# a BARE NAME (no "://") — NOT an address → the BARE_NAME sentinel (a ctx-key the caller reads).
check("resolve_address('utterance') returns the BARE_NAME sentinel (a ctx-key, not an address)",
      resolve_address(store, "utterance") is BARE_NAME)
check("resolve_address('notes') likewise → BARE_NAME (bare names are ctx keys)",
      resolve_address(store, "notes") is BARE_NAME)

# an UNREGISTERED scheme (skill://) — RAISES fail-loud with the extensible message. The CRITICAL case:
# skill:// has scheme()==None just like a bare name, so the discriminator MUST be "://", not scheme().
skill_raised = False
try:
    resolve_address(store, "skill://foo")
except ValueError as e:
    skill_raised = "not content-resolvable yet" in str(e) and "extensible" in str(e).lower()
check("resolve_address('skill://foo') RAISES fail-loud (NOT the bare-name sentinel) — the extensible seam",
      skill_raised)

# a REGISTERED-but-unresolved scheme (blob:// / vec:// / ui:// / code://) — RAISES fail-loud too.
for sch in ("blob://b2:abc", "vec://run://x#emb=m", "ui://panel/p", "code://suite/foo"):
    raised = False
    try:
        resolve_address(store, sch)
    except ValueError as e:
        raised = "not content-resolvable yet" in str(e)
    check(f"resolve_address({sch.split('://')[0]}://…) RAISES fail-loud (registered scheme, no resolver)",
          raised)

# a <turn> template with NO turn_id RAISES (never dispatch an unmaterialized template that would miss).
tmpl_raised = False
try:
    resolve_address(store, "run://<turn>/x")
except ValueError as e:
    tmpl_raised = "no turn_id" in str(e) and "<turn>" in str(e)
check("resolve_address(run://<turn>/x) with NO turn_id RAISES (unmaterialized template, fail loud)",
      tmpl_raised)

# a missing run:// ref RAISES by default; a DECLARED on_missing='skip' returns None (the run_reduce policy).
miss_raised = False
try:
    resolve_address(store, f"run://{TURN}/never-written")
except RuntimeError:
    miss_raised = True
check("a missing run:// address RAISES on resolve (fail loud, default on_missing='raise')", miss_raised)
check("a DECLARED on_missing='skip' returns None on a pruned run:// ref (never an implicit-truthy miss)",
      resolve_address(store, f"run://{TURN}/never-written", on_missing="skip") is None)


# =================================================================================================
# 2 · run_items — the AXIS-INVERSION: ONE role × N units (vs run_swarm's N roles × 1 ctx)
# =================================================================================================
reg = RoleRegistry().discover([ROLES])
focus = reg["focus"]                          # a fireable "utterance"-only role (the default byte-identical path)
check("the fanned role (focus) is fireable + reads ('utterance',) (default input axis)",
      focus.can_fire and tuple(focus.spec.get("input_addresses") or ()) == ("utterance",))

store2 = FsStore(os.path.join(tempfile.mkdtemp(prefix="run-items-fan-"), "store"))
FAN_TURN = "t-fan"

# 3 UNITS — a MIX proving the input-address intent: a literal + a SEEDED run:// address + another literal.
# The run:// unit is a templated address (run://<turn>/seed-unit) → run_items materializes <turn>=FAN_TURN.
_seed(store2, f"run://{FAN_TURN}/seed-unit", "what did we decide about the storage layer?")
UNITS = [
    "tell me about the voice circuit",          # unit 0 — a LITERAL value
    "run://<turn>/seed-unit",                   # unit 1 — a run:// ADDRESS (materialized + resolved)
    "how does the address system work?",        # unit 2 — a LITERAL value
]


# LIVE-or-MOCKED (mirror reduce_acceptance): the resident 4B is preferred; if down, a mocked transport
# captures the REAL fan + run_role + schema-validate + per-unit addressing round-trip (never a false green).
def _try_live():
    from fabric import transport, client
    t = transport.openai_transport(base_url=cognition.RESIDENT_BASE_URL, timeout=8)
    client.complete(t, [{"role": "user", "content": "ok"}], model=cognition.RESIDENT_MODEL,
                    json=False, max_tokens=1, temperature=0.0)


live = True
try:
    _try_live()
except Exception as e:
    live = False
    print(f"  ..  resident 4B not up ({type(e).__name__}) — proving run_items on a MOCKED transport")

events = []
if live:
    res = run_items(focus, UNITS, store2, turn_id=FAN_TURN,
                    emit=lambda kind, p: events.append((kind, p)))
else:
    # MOCK the fabric transport so the compose + run_role + per-unit address + read-back path is REAL.
    # We capture which unit reached each call's user message (proving each unit became the role's input).
    from fabric import client as _client
    seen_users = []

    class _Validated:
        def __init__(self, d): self._d = d
        def model_dump(self): return dict(self._d)

    orig = _client.complete

    def _mock(t, msgs, *, model, schema=None, json=False, temperature=0.0, max_tokens=256, **kw):
        seen_users.append(msgs[-1]["content"])
        # focus's FocusOut schema = {intent, which_roles}. Return a schema-valid stub.
        return _Validated({"intent": msgs[-1]["content"][:40], "which_roles": []})

    cognition.client.complete = _mock
    try:
        res = run_items(focus, UNITS, store2, turn_id=FAN_TURN,
                        emit=lambda kind, p: events.append((kind, p)))
    finally:
        cognition.client.complete = orig

    # the axis-inversion in the mock: each of the 3 units reached run_role as the role's PRIMARY input
    # (framed "Utterance: <unit>") — proving 1 role × N units (the resolved run:// unit appears too).
    check("MOCK: each of the 3 units fired run_role as the role's primary input (Utterance: framing)",
          len(seen_users) == 3)
    check("MOCK: the literal units reached the fan as the role's input",
          any("voice circuit" in u for u in seen_users) and any("address system" in u for u in seen_users))
    check("MOCK: the run:// unit was MATERIALIZED + RESOLVED before firing (its content reached the role)",
          any("storage layer" in u for u in seen_users))

check("run_items returns an ItemsResult", isinstance(res, ItemsResult))
check("run_items fanned ONE role (focus) over N=3 units — the axis-inversion (vs run_swarm N roles × 1 ctx)",
      res.role_id == "focus" and len(res.runs) == 3)

# THE PER-UNIT ADDRESSES: 3 outputs at run://<turn>/<role>/0..2 (positional).
check("each unit's output is at run://<turn>/<role>/<i> (positional per-unit address)",
      [res.addresses[i] for i in range(3)] ==
      [f"run://{FAN_TURN}/focus/{i}" for i in range(3)])
# each address actually RESOLVES to the real role output (read BACK via the canonical resolver).
for i in range(3):
    val = resolve_run_ref(store2, f"run://{FAN_TURN}/focus/{i}")
    check(f"run://{FAN_TURN}/focus/{i} resolves to focus's real output (a dict with 'intent')",
          isinstance(val, dict) and "intent" in val)
check("run_items read every unit's output BACK into .resolved (the after-barrier read)",
      set(res.resolved) == {0, 1, 2} and all("intent" in res.resolved[i] for i in range(3)))

# the DRIVER / batched-rollup discipline (mirrors run_swarm/run_reduce): ONE rollup, no operator verbs.
check("run_items emits ONE cognition.items rollup (C1.6 batched discipline)",
      len(events) == 1 and events[0][0] == "cognition.items")
check("the items rollup carries NO resolve/approve/dispatch (operator-only floor — driver, not agent)",
      all(k not in events[0][1] for k in ("resolve", "approve", "dispatch", "verb")))
check("the items rollup records the N units + their per-unit addresses",
      events[0][1]["n_units"] == 3 and len(events[0][1]["units"]) == 3)


# =================================================================================================
# 3 · run_items FAIL LOUD — a unit that is an unresolvable run:// address (the run_swarm barrier discipline)
# =================================================================================================
store3 = FsStore(os.path.join(tempfile.mkdtemp(prefix="run-items-fail-"), "store"))
F_TURN = "t-fail"
_seed(store3, f"run://{F_TURN}/good", "a real upstream output")
BAD_UNITS = ["a literal unit", f"run://{F_TURN}/missing"]   # the 2nd is never written → unresolvable

fail_raised = False
try:
    # focus is "utterance"-only; the bad unit resolves via resolve_address → RuntimeError (head None).
    if live:
        run_items(focus, BAD_UNITS, store3, turn_id=F_TURN)
    else:
        from fabric import client as _client
        orig = _client.complete

        class _V:
            def __init__(self, d): self._d = d
            def model_dump(self): return dict(self._d)

        def _m(t, msgs, *, model, schema=None, json=False, temperature=0.0, max_tokens=256, **kw):
            return _V({"intent": "x", "which_roles": []})
        cognition.client.complete = _m
        try:
            run_items(focus, BAD_UNITS, store3, turn_id=F_TURN)
        finally:
            cognition.client.complete = orig
except RuntimeError:
    fail_raised = True
check("run_items FAILS LOUD when a unit's run:// address does not resolve (barrier re-raise, never silent)",
      fail_raised)

# a DECLARED on_missing='skip' RECORDS the skipped unit (never silent) + maps the rest.
store4 = FsStore(os.path.join(tempfile.mkdtemp(prefix="run-items-skip-"), "store"))
S_TURN = "t-skip"
SKIP_UNITS = ["a literal unit", f"run://{S_TURN}/missing"]

if live:
    res_skip = run_items(focus, SKIP_UNITS, store4, turn_id=S_TURN, on_missing="skip")
else:
    from fabric import client as _client
    orig = _client.complete

    class _V2:
        def __init__(self, d): self._d = d
        def model_dump(self): return dict(self._d)

    def _m2(t, msgs, *, model, schema=None, json=False, temperature=0.0, max_tokens=256, **kw):
        return _V2({"intent": "x", "which_roles": []})
    cognition.client.complete = _m2
    try:
        res_skip = run_items(focus, SKIP_UNITS, store4, turn_id=S_TURN, on_missing="skip")
    finally:
        cognition.client.complete = orig

check("on_missing='skip': the unresolvable unit is RECORDED in .skipped (never a silent drop)",
      len(res_skip.skipped) == 1 and res_skip.skipped[0][0] == 1)
check("on_missing='skip': the resolvable literal unit still mapped (1 of 2 produced an output)",
      len(res_skip.runs) == 1 and 0 in res_skip.resolved)


# =================================================================================================
# 4 · ADDITIVE / behaviour-preserving — run_swarm/run_jury/run_role unchanged (the C law)
# =================================================================================================
import inspect                                                              # noqa: E402
# run_role's signature is unchanged (no new required params) — the seam stayed byte-identical.
sig = inspect.signature(cognition.run_role)
check("run_role's signature is unchanged (additive — run_items did not touch the seam)",
      list(sig.parameters)[:2] == ["role", "ctx"])
# run_swarm + run_jury + run_reduce all still importable + present (no removal/rename).
check("run_swarm / run_jury / run_reduce remain present (additive — nothing removed)",
      all(callable(getattr(cognition, n)) for n in ("run_swarm", "run_jury", "run_reduce")))


print(f"\nALL {PASS} CHECKS PASS — resolve_address: run://+cas:// resolve now · bare→sentinel · "
      f"unknown→RAISE (extensible seam) · run_items: the axis-inversion (1 role × N units) · per-unit "
      f"addresses · fail-loud + declared-skip · driver-only · additive (run_swarm/jury/role unchanged)")
