"""tests/mode_loadout_acceptance.py — WS1 acceptance: the mode→loadout link (confirm-gated).

A presence mode may bind a `loadout_class` (a combo in services.json) — the model loadout it wants
resident. Switching the mode is FREE (a config write); changing the resident loadout is expensive +
service-affecting, so it is CONFIRM (governance): set_mode SURFACES a loadout_swap, never auto-actuates;
apply_loadout runs it ONLY on operator approve (read from the inbox). The autonomous loop can RAISE the
confirm but can NEVER self-approve it — and the actuation rides ensure_resident's WS-R RAM+VRAM gate, so
an approved swap cannot OOM.

VERIFY-BY-USE, no service started: the actuation path (apply_loadout on an APPROVED swap) starts real
services, so it is the supervised-on-first-real-use path (R2) — NOT exercised here. This suite proves the
SURFACE side (the confirm is raised, not actuated) and the GUARD (an unapproved swap raises).

Run: `python3 tests/mode_loadout_acceptance.py`  (exit 0 = all green; non-zero = a FAIL line printed).

Covers:
  T1  the registry carries loadout_class: listening binds 'interaction'; modes_registry _OPTIONAL lists it.
  T2  governance POLICY['loadout_swap'] == CONFIRM (single-source gate posture).
  T3  _resolve_loadout('interaction') → (services, missing⊆services); an unknown loadout_class fails loud.
  T4  set_mode('off') (no loadout_class) surfaces NO loadout_swap — byte-identical to pre-WS1 behaviour.
  T5  set_mode('listening') with a non-resident loadout surfaces EXACTLY ONE loadout_swap (and dedups).
  T6  apply_loadout on a NOT-approved swap RAISES GovernanceError — the loop-can't-self-approve guard.
  T7  apply_loadout on a non-loadout_swap sid RAISES ValueError (fail loud, never a wrong actuation).
"""
import os
import sys
import tempfile
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "ops", "cli"))

PASS, FAIL = [], []


def ok(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f"  — {detail}" if detail and not cond else ""))


os.environ.pop("COMPANY_CAP_DISCOVER_AT_INIT", None)
os.environ["COMPANY_CAP_LOAD_FROM_LEDGER"] = "0"

from runtime.modes_registry import discover_modes, MODES_DIR, _OPTIONAL
from runtime import governance
from runtime.governance import GovernanceError, CONFIRM
from runtime.suite import Suite
from runtime.registry import NodeRegistry
from store.fs_store import FsStore

NODES = os.path.join(ROOT, "nodes")

# ── T1 — the registry carries loadout_class ──────────────────────────────────────────────────────
print("\n[T1] modes carry an optional loadout_class")
modes = discover_modes([MODES_DIR])
ok("T1a listening binds loadout_class 'interaction'", modes["listening"].get("loadout_class") == "interaction",
   f"got {modes['listening'].get('loadout_class')!r}")
ok("T1b 'loadout_class' is a recognised optional field", "loadout_class" in _OPTIONAL, f"_OPTIONAL={_OPTIONAL}")
ok("T1c off does NOT bind a loadout_class (open set; unset is fine)", "loadout_class" not in modes["off"])

# ── T2 — governance posture ──────────────────────────────────────────────────────────────────────
print("\n[T2] loadout_swap is CONFIRM (single-source gate)")
ok("T2a POLICY['loadout_swap'] == CONFIRM", governance.POLICY.get("loadout_swap") == CONFIRM,
   f"got {governance.POLICY.get('loadout_swap')!r}")

# ── build a Suite on a temp store ────────────────────────────────────────────────────────────────
store_dir = tempfile.mkdtemp(prefix="mode-loadout-test-")
exit_code = 1
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)

    # ── T3 — _resolve_loadout ──────────────────────────────────────────────────────────────────────
    print("\n[T3] _resolve_loadout reads the ONE combos table; unknown fails loud")
    services, missing = suite._resolve_loadout("interaction")
    ok("T3a interaction resolves to its service list", isinstance(services, list) and len(services) >= 3, f"{services}")
    ok("T3b missing ⊆ services", set(missing) <= set(services), f"missing={missing}")
    try:
        suite._resolve_loadout("no-such-loadout")
        ok("T3c unknown loadout_class RAISES", False, "did not raise")
    except ValueError as e:
        ok("T3c unknown loadout_class RAISES", "names no combo" in str(e), f"msg={str(e)[:120]!r}")

    # ── T4 — set_mode with NO loadout_class surfaces nothing ────────────────────────────────────────
    print("\n[T4] set_mode('off') surfaces NO loadout_swap (byte-identical pre-WS1)")
    before = [d for d in suite.inbox.list() if d.get("action") == "loadout_swap"]
    suite.set_mode("off")
    after = [d for d in suite.inbox.list() if d.get("action") == "loadout_swap"]
    ok("T4a mode set to off", suite.get_mode() == "off")
    ok("T4b no loadout_swap surfaced for off", len(after) == len(before), f"before={len(before)} after={len(after)}")

    # ── T5 — set_mode('listening') surfaces exactly one (and dedups) ────────────────────────────────
    print("\n[T5] set_mode('listening') surfaces a loadout_swap when the loadout isn't resident (dedups)")
    # only meaningful if the interaction loadout has a non-resident service right now
    _, miss_now = suite._resolve_loadout("interaction")
    suite.set_mode("listening")
    suite.set_mode("listening")    # second call must NOT add a duplicate pending swap
    swaps = [d for d in suite.inbox.list()
             if d.get("action") == "loadout_swap" and (d.get("payload") or {}).get("loadout_class") == "interaction"]
    if miss_now:
        ok("T5a exactly one pending loadout_swap (deduped across 2 set_mode calls)", len(swaps) == 1,
           f"count={len(swaps)} missing={miss_now}")
        ok("T5b it was SURFACED not actuated (resolved is None)", swaps and swaps[0].get("resolved") is None)
    else:
        ok("T5a (loadout fully resident now → nothing to surface, correct)", len(swaps) == 0, f"swaps={len(swaps)}")

    # ── T6 — apply_loadout guard: unapproved RAISES (loop can't self-approve) ───────────────────────
    print("\n[T6] apply_loadout on an UNAPPROVED swap RAISES (the loop-can't-self-approve guard)")
    sid = suite.inbox.surface("loadout_swap",
                              {"mode": "listening", "loadout_class": "interaction",
                               "services": ["tts-kokoro"], "missing": ["tts-kokoro"]},
                              default="reject", resolved=None)
    try:
        suite.apply_loadout(sid)
        ok("T6a unapproved apply_loadout RAISES GovernanceError", False, "did not raise (DANGER: would self-approve)")
    except GovernanceError as e:
        ok("T6a unapproved apply_loadout RAISES GovernanceError", "not approved" in str(e), f"msg={str(e)[:120]!r}")

    # ── T7 — apply_loadout on a wrong sid type fails loud ───────────────────────────────────────────
    print("\n[T7] apply_loadout on a non-loadout_swap sid RAISES ValueError")
    other = suite.inbox.surface("question", {"question": "x"}, default="reject")
    try:
        suite.apply_loadout(other)
        ok("T7a non-loadout_swap sid RAISES ValueError", False, "did not raise")
    except ValueError as e:
        ok("T7a non-loadout_swap sid RAISES ValueError", "not a surfaced loadout_swap" in str(e), f"msg={str(e)[:120]!r}")

    # ── T8 — apply_surfaced routes a loadout_swap to apply_loadout (operator-applyable, guard holds) ──
    print("\n[T8] apply_surfaced(loadout_swap) routes to apply_loadout — unapproved still RAISES (the gate)")
    sid2 = suite.inbox.surface("loadout_swap",
                               {"mode": "listening", "loadout_class": "interaction",
                                "services": ["tts-kokoro"], "missing": ["tts-kokoro"]},
                               default="reject", resolved=None)
    try:
        suite.apply_surfaced(sid2)   # routes to apply_loadout; unapproved → GovernanceError (not apply_node)
        ok("T8a apply_surfaced(unapproved loadout_swap) RAISES", False, "did not raise — routed wrong or self-approved")
    except GovernanceError as e:
        ok("T8a apply_surfaced routes loadout_swap → apply_loadout + the gate holds", "not approved" in str(e),
           f"msg={str(e)[:120]!r}")

    print(f"\n[RESULT] {len(PASS)} pass / {len(FAIL)} fail")
    exit_code = 1 if FAIL else 0
    if FAIL:
        print("FAILED: " + ", ".join(FAIL))
finally:
    shutil.rmtree(store_dir, ignore_errors=True)

sys.exit(exit_code)
