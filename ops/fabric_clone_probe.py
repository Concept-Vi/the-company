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
# COMPANY-MODEL backend (2026-06-16): provider='ollama' + an ollama MODEL tag → the clone boots on a
# company/ollama model via ollama-native :11434 (supervisor _provider_env). Omitted = host Anthropic
# (byte-identical to the original probe). e.g. ... 7c2c1b74.jsonl compact:1 ollama kimi-k2.7-code:cloud
PROVIDER = sys.argv[3] if len(sys.argv) > 3 else (os.environ.get("COMPANY_PROBE_PROVIDER") or None)
MODEL = sys.argv[4] if len(sys.argv) > 4 else (os.environ.get("COMPANY_PROBE_MODEL") or None)

print(f"=== clone_at({os.path.basename(SRC)}, {AT}"
      + (f", provider={PROVIDER}, model={MODEL}" if PROVIDER else "") + ") ===")
t0 = time.time()
c = cc_clone.clone_at(SRC, AT, description="cc_clone live probe", provider=PROVIDER, model=MODEL)
print(f"  handle={c['handle']} sup={c['supervisor_session']} sid={c['session_id'][:8]} "
      f"source_untouched={c['source_untouched']} ({time.time()-t0:.0f}s)")
ok_launch = c["source_untouched"] and c["supervisor_session"]

print("=== msg_clone (ask the past-point context) ===")
r = cc_clone.msg_clone(c["handle"], "In one short sentence, what is the most recent thing we were discussing?")
print(f"  REPLY @{r['at']}: {r['reply'][:280]}")
# NO GREEN PAINT (2026-06-16): a non-empty reply is NOT success — Claude Code returns a non-empty ERROR
# string when --model can't be resolved ("...may not exist or you may not have access... pick a different
# model"). That is a model-resolution FAILURE, not an answer. This exact false-pass slipped through the old
# bool(reply) check on the first kimi-clone proof. Detect it and FAIL.
_rl = (r.get("reply") or "").lower()
_model_err = ("pick a different model" in _rl) or ("may not exist" in _rl and "access" in _rl)
ok_reply = bool(r.get("reply")) and not _model_err
if _model_err:
    print("  ★ MODEL-RESOLUTION FAILURE — clone booted but its --model did NOT resolve "
          "(reply is CC's model error, not an answer).")

print("=== end_clone ===")
e = cc_clone.end_clone(c["handle"])
src_ok = os.path.exists(SRC)
print(f"  {e} | source present+untouched: {src_ok}")

ok = ok_launch and ok_reply and e.get("materialized_deleted") and src_ok
if ok:
    print(f"\nRESULT: PASS — clone launched supervised, DM'd, answered from past context, torn down "
          f"non-destructively. (Read the reply: it should be the @{AT} topic, not the tip.)")
else:
    print(f"\nRESULT: FAIL — launch={ok_launch} reply_ok={ok_reply} torn_down="
          f"{bool(e.get('materialized_deleted'))} source_untouched={src_ok}. "
          f"Boot/teardown may be fine while the TURN failed (see reply — e.g. model-resolution error).")
sys.exit(0 if ok else 1)
