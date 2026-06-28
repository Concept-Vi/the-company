"""tests/mode_consent_registry_acceptance.py — WS6 verify-only: the act/surface decision is registry-driven.

SEAM 2 (2026-06-09): the ACT-vs-SURFACE routing of a dispatched RHM verb keys off the mode's DECLARED
`consent` axis (registry-is-truth) — `if self.mode_registry(mode)["consent"] == "act"` (suite.py) — NOT a
hardcoded `if mode == "decide-for-me"` name-branch. A mode that should auto-act declares consent="act"; one
that should not declares "offer"/"none". This is a VERIFY-ONLY workstream (the wiring already shipped); the
teeth here lock it so a regression to a name-branch, or a drifted consent value, fails loud.

THE FLOOR (unchanged, asserted by reference): consent=="act" routes through autonomous_dispatch, which
routes by POSTURE — AUTO-class verbs run (reversible/whitelisted), CONFIRM-class verbs SURFACE a draft;
it NEVER self-approves (apply still needs operator is_approved). So "act" is not "do anything"; it is
"route deterministically by the verb's governance class".

Run: `python3 tests/mode_consent_registry_acceptance.py`  (exit 0 = all green).

Covers:
  T1  every mode surfaces its declared consent through mode_registry; the act-set is EXACTLY
        {background, decide-for-me, focus, watch-and-react} (the documented generalization).
  T2  REGISTRY-IS-TRUTH: the gate predicate flips when a mode's consent VALUE changes (data, not a name) —
        flip listening→'act' makes it route-act; flip decide-for-me→'offer' makes it route-normal.
  T3  STRUCTURAL: the gate routes off mode_registry(...)['consent'] and has NO `mode == "decide-for-me"`
        consent name-branch.
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


os.environ["COMPANY_CAP_LOAD_FROM_LEDGER"] = "0"

from runtime.suite import Suite
from runtime.registry import NodeRegistry
from store.fs_store import FsStore

NODES = os.path.join(ROOT, "nodes")
EXPECTED_ACT = {"background", "decide-for-me", "focus", "watch-and-react"}

store_dir = tempfile.mkdtemp(prefix="mode-consent-test-")
exit_code = 1
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)

    # the EXACT predicate the gate uses (suite.py:~6471)
    def routes_act(mode):
        return suite.mode_registry(mode)["consent"] == "act"

    # ── T1 — the act-set is the declared registry data ───────────────────────────────────────────────
    print("\n[T1] the act-routing set is exactly the modes that DECLARE consent='act'")
    act_set = {m for m in suite.MODES if routes_act(m)}
    ok("T1a act-set == {background, decide-for-me, focus, watch-and-react}", act_set == EXPECTED_ACT,
       f"got {act_set}")
    ok("T1b offer/none modes do NOT route act",
       not any(routes_act(m) for m in ("listening", "text-only", "walkthrough", "off")),
       f"act among them: {[m for m in ('listening','text-only','walkthrough','off') if routes_act(m)]}")

    # ── T2 — registry-is-truth: the predicate follows the VALUE, not the name ─────────────────────────
    print("\n[T2] registry-is-truth — changing a mode's consent value flips routing (data, not a name)")
    ok("T2a baseline: listening routes NORMAL (consent='offer')", routes_act("listening") is False)
    suite.MODE_REGISTRY["listening"]["consent"] = "act"     # mutate the data the gate reads
    ok("T2b after flipping listening→'act' it routes ACT (no name-branch could do this)",
       routes_act("listening") is True)
    suite.MODE_REGISTRY["listening"]["consent"] = "offer"   # restore
    ok("T2c restored: listening routes NORMAL again", routes_act("listening") is False)
    suite.MODE_REGISTRY["decide-for-me"]["consent"] = "offer"
    ok("T2d flipping decide-for-me→'offer' makes the canonical act-mode route NORMAL (name unused)",
       routes_act("decide-for-me") is False)
    suite.MODE_REGISTRY["decide-for-me"]["consent"] = "act"  # restore

    # ── T3 — structural: registry-driven gate, no name-branch ─────────────────────────────────────────
    print("\n[T3] the gate source routes off consent, not a mode name")
    src = open(os.path.join(ROOT, "runtime", "suite.py")).read()
    ok("T3a gate uses mode_registry(mode)['consent'] == 'act'",
       'self.mode_registry(mode)["consent"] == "act"' in src)
    # no consent name-branch (the only decide-for-me references are mode-SETS / the dispatcher, not the gate)
    ok("T3b no `mode == \"decide-for-me\"` consent name-branch", 'mode == "decide-for-me"' not in src,
       "a name-branch would re-introduce the hardcoding SEAM 2 removed")

    print(f"\n[RESULT] {len(PASS)} pass / {len(FAIL)} fail")
    exit_code = 1 if FAIL else 0
    if FAIL:
        print("FAILED: " + ", ".join(FAIL))
finally:
    shutil.rmtree(store_dir, ignore_errors=True)

sys.exit(exit_code)
