"""tests/vi_vision_branch_acceptance.py — the resolve_address vi-vision:// DISPATCH branch (fork, 2026-06-17).

Locks the company-spine half of the factory's vi-vision integration (islands-join-mainland): that
runtime/cognition.py:resolve_address dispatches vi-vision:// INTO runtime/vi_vision.resolve_vi_vision and
maps its three operational error types → ValueError (never silent-empty), AND that the scope-cascade flows
through. The MODULE's own logic has its self-test (`python3 runtime/vi_vision.py`); THIS locks the BRANCH
(dispatch + error-mapping + only-vi-vision-routed) — independent of the gated live Supabase read (uses an
injected candidate-fetcher, no real transport).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import runtime.vi_vision as vv
from runtime.cognition import resolve_address

PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def _ve(addr, must):
    """resolve_address(addr) must raise ValueError containing `must` (the branch maps ViVision* → ValueError)."""
    try:
        resolve_address(None, addr)
        return False
    except ValueError as e:
        return must.lower() in str(e).lower()


print("[E] the 3 operational error types → ValueError (fail-loud, never silent-empty)")
# Substrings match STABLE tokens of the resolver's prose (composition owns runtime/vi_vision.py; its exact
# wording may drift — match the durable token, not the full sentence). The point under test = the BRANCH maps
# each ViVision* type → ValueError (the type is erased by resolve_address, so we discriminate via the message).
check("malformed (unknown frame) → ValueError (ViVisionAddressError mapped)",
      _ve("vi-vision://nope/organism/x", "unknown frame"))
check("no transport → ValueError (ViVisionTransportError mapped)",
      _ve("vi-vision://global/organism/component.x", "transport"))

# Inject a candidate-fetcher so the type-guard / scope-cascade run WITHOUT a live transport.
_ROWS = [
    {"component_id": "component.x", "type": "organism", "name": "global-V", "scope": "global",
     "definition": {}, "context": {}},
    {"component_id": "component.x", "type": "organism", "name": "proj-V", "scope": "project:p1",
     "definition": {}, "context": {}},
]
vv._transport_configured = lambda: True
vv._candidates_http = lambda cid: list(_ROWS)
vv._candidates_supabase = lambda cid: []   # http path wins; supabase not consulted in the test

check("type-guard miss (asks atom, only organism rows) → ValueError (ViVisionNotFound mapped)",
      _ve("vi-vision://global/atom/component.x", "at/under frame"))

print("\n[C] scope-cascade flows through the branch (most-specific-wins)")
r_proj = resolve_address(None, "vi-vision://project/p1/organism/component.x")
check("project frame → the project row wins (most-specific)",
      isinstance(r_proj, dict) and r_proj.get("name") == "proj-V")
r_glob = resolve_address(None, "vi-vision://global/organism/component.x")
check("global frame → the more-specific project row is excluded, global wins",
      isinstance(r_glob, dict) and r_glob.get("name") == "global-V")

print("\n[R] only vi-vision is routed — the dispatcher is otherwise unchanged")
check("blob:// still hits the generic 'not content-resolvable yet' (no accidental re-route)",
      _ve("blob://algo:hash", "not content-resolvable yet"))

print(f"\nALL {PASS} CHECKS PASS — resolve_address dispatches vi-vision:// into the factory resolver, maps "
      f"the 3 error types → ValueError, scope-cascades, and routes ONLY vi-vision (injected rows, no live read).")
