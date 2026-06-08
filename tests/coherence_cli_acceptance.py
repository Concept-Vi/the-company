"""tests/coherence_cli_acceptance.py — the `company coherence` read face (C5 CLI FORM).

The on-demand coherence read, re-derived fresh (own/reflect). Proves scan() produces the real model and
format_scan() renders it scannably (the FORM bar for this lane: a navigable surface, not a dict dump),
cleanly separating the trustworthy burn-down backlog from the positive-only candidates.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from runtime import coherence_detect as cd

PASS = 0
def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")

res = cd.scan(ROOT)
b = res["burn_down"]
check("scan re-derives the real model (findings recorded from the live repo)", b["total"] > 0)
check("open + accepted + closed == total (every finding classified)",
      b["open"] + b["accepted"] + b["closed"] == b["total"])
check("candidates present + separated (positive-only)", "capability_no_consumer" in res["candidates"] and "hardcoding" in res["candidates"])

out = cd.format_scan(res)
check("format_scan renders the headline COHERENCE line", out.startswith("COHERENCE —"))
check("the OPEN backlog is labelled the burn-down target", "OPEN (the burn-down target)" in out)
check("candidates are labelled positive-only / adjudicate (never confused with must-fix)",
      "adjudicate, never auto-acted" in out)
check("it's a scannable surface, not a raw dict dump", "{" not in out and "}" not in out)

print(f"\nALL {PASS} CHECKS PASS — `company coherence` reads the real substrate state, re-derived fresh, "
      f"rendered scannably (burn-down backlog separated from positive-only candidates).")
