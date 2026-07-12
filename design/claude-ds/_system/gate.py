#!/usr/bin/env python3
"""gate.py — the census as a GATE (detector #2 of the one design gate).

Runs the emitter, then compares the fresh symbol registry against the LAST
COMMITTED one (git show HEAD:registry/symbol-registry.json). The rule:

  · any gap COUNT that INCREASES vs HEAD  -> FAIL (regression)
  · any NEW ghost key (a token/icon/type/action/global/axis consumed or wired
    that resolves nowhere)                -> FAIL, named
  · counts equal or falling               -> PASS

Exit 0 = pass, 1 = fail (typed findings on stdout, one JSON line at the end for
machine consumption). Composes with the adherence lint (which owns raw-value
STYLE findings; this gate owns SYSTEM-level holes) and the QA harness runner
(which takes its coverage denominator from registry/address-registry.json).

Usage:  python3 _system/gate.py          # in a claude-ds checkout
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# 1. re-derive the map (registry-is-truth; the gate never trusts a stale one)
r = subprocess.run([sys.executable, "_system/substrate-map.py"], capture_output=True, text=True)
if r.returncode != 0:
    print("GATE FAIL — the emitter itself failed:\n" + r.stderr)
    sys.exit(1)

fresh = json.load(open("registry/symbol-registry.json"))
new_counts = fresh["_meta"].get("gap_counts", {})
new_keys = set(fresh["_meta"].get("ghost_keys", []))

# 2. the committed baseline
p = subprocess.run(["git", "show", "HEAD:registry/symbol-registry.json"],
                   capture_output=True, text=True)
if p.returncode != 0:
    print("GATE PASS (no committed baseline yet — first run records one; commit the registry)")
    print(json.dumps({"gate": "pass", "reason": "no-baseline", "counts": new_counts}))
    sys.exit(0)
base = json.loads(p.stdout)
base_counts = base["_meta"].get("gap_counts", {})
base_keys = set(base["_meta"].get("ghost_keys", []))

# 3. verdict
REGRESSION_COUNTS = [k for k in new_counts
                     if k.startswith(("ghost_", "dead_", "deaf_")) or k == "raw_colour_values"]
findings = []
for k in REGRESSION_COUNTS:
    if new_counts.get(k, 0) > base_counts.get(k, 0):
        findings.append({"kind": "count-regression", "counter": k,
                         "was": base_counts.get(k, 0), "now": new_counts.get(k, 0)})
for key in sorted(new_keys - base_keys):
    findings.append({"kind": "new-ghost", "address": key,
                     "detail": "consumed/wired but resolves nowhere (see registry/GAPS.md)"})

if findings:
    print(f"GATE FAIL — {len(findings)} finding(s):")
    for f in findings:
        if f["kind"] == "count-regression":
            print(f"  ✗ {f['counter']}: {f['was']} -> {f['now']}")
        else:
            print(f"  ✗ NEW GHOST {f['address']}")
    print(json.dumps({"gate": "fail", "findings": findings, "counts": new_counts}))
    sys.exit(1)

improved = {k: (base_counts.get(k, 0), new_counts.get(k, 0))
            for k in REGRESSION_COUNTS if new_counts.get(k, 0) < base_counts.get(k, 0)}
print("GATE PASS" + (f" — improved: {', '.join(f'{k} {a}->{b}' for k, (a, b) in improved.items())}" if improved else ""))
print(json.dumps({"gate": "pass", "improved": improved, "counts": new_counts}))
sys.exit(0)
