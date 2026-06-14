#!/usr/bin/env python3
"""ops/fabric_clone_probe.py — live proof of the point-in-time CLONE -> fabric extension
(runtime/cc_clone.py). Lead-only (spawns a real supervised claude clone; no model load).

Clones a real multi-boundary source @compact:1, DMs the clone, and asserts it answers from the
PAST-point context (not the live tip), then tears down (materialized deleted, source untouched).
Run: .venv/bin/python ops/fabric_clone_probe.py [<source.jsonl>] [<at>]
"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runtime import cc_clone

SRC = sys.argv[1] if len(sys.argv) > 1 else \
    "/home/tim/.claude/projects/-home-tim/7c2c1b74-075d-41ac-b208-1e67124d32ca.jsonl"
AT = sys.argv[2] if len(sys.argv) > 2 else "compact:1"

print(f"=== clone_at({os.path.basename(SRC)}, {AT}) ===")
t0 = time.time()
c = cc_clone.clone_at(SRC, AT, description="cc_clone live probe")
print(f"  handle={c['handle']} sup={c['supervisor_session']} sid={c['session_id'][:8]} "
      f"source_untouched={c['source_untouched']} ({time.time()-t0:.0f}s)")
ok_launch = c["source_untouched"] and c["supervisor_session"]

print("=== msg_clone (ask the past-point context) ===")
r = cc_clone.msg_clone(c["handle"], "In one short sentence, what is the most recent thing we were discussing?")
print(f"  REPLY @{r['at']}: {r['reply'][:280]}")
ok_reply = bool(r["reply"])

print("=== end_clone ===")
e = cc_clone.end_clone(c["handle"])
src_ok = os.path.exists(SRC)
print(f"  {e} | source present+untouched: {src_ok}")

ok = ok_launch and ok_reply and e.get("materialized_deleted") and src_ok
print(f"\nRESULT: {'PASS' if ok else 'FAIL'} — clone launched supervised, DM'd, answered from past "
      f"context, torn down non-destructively. (Read the reply: it should be the @{AT} topic, not the tip.)")
sys.exit(0 if ok else 1)
