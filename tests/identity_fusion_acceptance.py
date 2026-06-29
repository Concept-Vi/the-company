"""tests/identity_fusion_acceptance.py — identity fusion teeth (additive + behavior-preserving).

Proves, executed (non-tautological):
  1. PRINCIPAL KIND resolves for both kinds on REAL regs: a ch-* → AGENT, tim.json → VIEWER; and
     operator.json is FLAGGED (ambiguous), not silently bucketed.
  2. The SEEDED grants reproduce EXACTLY today's remote.py decision: the grant-driven tool list ==
     the untouched posture/tier tool list, per tier {operator → all, client → safe-only, none → none},
     over the LIVE _TOOL_MANAGER._tools.
  3. Nothing weakened: the grant store is empty until seeded (the shadow stays silent / fail-closed),
     and the seed is derived from the LIVE posture-safe set (no hardcoded subset).

Run: .venv/bin/python tests/identity_fusion_acceptance.py
The live auth path (no-token → 401) is verified by the existing remote gateway behavior + the gate
functions are exercised here in-process (no HTTP/socket needed)."""
import os
import sys
import json
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runtime import principals as P
from runtime import grants as G
from mcp_face import remote as R

FAILS = []


def check(cond, msg):
    print(("  PASS " if cond else "  FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def test_principal_kinds():
    print("\n[1] PRINCIPAL KIND resolves for both kinds (real regs)")
    # 1a — a real ch-* agent reg
    ch_regs = [r for r in P.list_principals() if str(r.get("handle") or "").startswith("ch-")]
    check(bool(ch_regs), f"found {len(ch_regs)} ch-* agent reg(s) on disk")
    if ch_regs:
        check(all(r["kind"] == P.KIND_AGENT for r in ch_regs),
              f"every ch-* resolves kind=agent (got {[r['kind'] for r in ch_regs]})")
    # 1b — tim.json viewer
    try:
        tim = P.resolve_handle("tim")
        check(tim["kind"] == P.KIND_VIEWER, f"tim.json resolves kind=viewer (got {tim['kind']})")
    except ValueError as e:
        check(False, f"tim.json present + resolves ({e})")
    # 1c — operator.json flagged, not silently bucketed
    try:
        op = P.resolve_handle("operator")
        check(op["kind"] == P.KIND_AMBIGUOUS and op["kind_source"] == "flagged",
              f"operator.json is FLAGGED ambiguous, not silently classified (got {op})")
    except ValueError:
        check(True, "operator.json absent (nothing to misclassify)")
    # 1d — inc.3 member-kind mapping is total + non-forking
    check(P.member_kind_to_principal_kind("human") == P.KIND_VIEWER, "member human → viewer")
    check(P.member_kind_to_principal_kind("live-session") == P.KIND_AGENT, "member live-session → agent")
    check(P.member_kind_to_principal_kind("model") == P.KIND_AGENT, "member model → agent")
    try:
        P.member_kind_to_principal_kind("nope"); check(False, "unknown member kind fails loud")
    except ValueError:
        check(True, "unknown member kind fails loud (no silent default)")


def _live_tools_for_tier(tier):
    """The UNTOUCHED posture/tier decision (remote.py's live authority) — the comparison baseline."""
    return sorted(n for n, _ in R._tools_for_tier(tier))


def _grant_tools_for_tier(tier, subject, leaf):
    """The GRANT-DRIVEN tool list for a tier: every live tool the grant table authorizes."""
    pt, pid = R._principal_for_tier(tier, subject)
    out = []
    for name in R._TOOL_MANAGER._tools:
        if G.tool_allowed_via_grants(name, principal_type=pt, principal_id=pid, leaf=leaf):
            out.append(name)
    return sorted(out)


def test_seed_reproduces_current():
    print("\n[2] SEEDED grants reproduce EXACTLY today's remote.py decision (live registry)")
    all_tools = sorted(R._TOOL_MANAGER._tools)
    safe = sorted(n for n, t in R._TOOL_MANAGER._tools.items() if R._tool_posture(t) == "safe")
    print(f"  (live: {len(all_tools)} tools, {len(safe)} posture-safe)")

    with tempfile.TemporaryDirectory() as d:
        leaf = os.path.join(d, "access_grants.jsonl")
        # 3 — empty until seeded: the shadow is silent (nothing authorized) → fail-closed, not weakened
        check(G.fold_grants(leaf=leaf) == [], "grant store empty until seeded (nothing leaks pre-seed)")
        check(not G.tool_allowed_via_grants(all_tools[0], principal_type=G.PT_VIEWER,
                                            principal_id="someone", leaf=leaf),
              "pre-seed: a client is granted NOTHING (fail-closed floor preserved)")

        summary = G.seed_current_tool_grants(safe, leaf=leaf)
        print(f"  seeded: {summary}")
        check(summary["client_grants"] == len(safe), "one client grant per live safe tool (no hardcode)")

        # operator: grant list == ALL live tools
        op_grants = _grant_tools_for_tier(R.TIER_OPERATOR, G.OPERATOR_USER_ID, leaf)
        check(op_grants == all_tools,
              f"operator: grant-list == ALL tools ({len(op_grants)} == {len(all_tools)})")

        # client: grant list == posture-safe subset (for any non-operator subject)
        cl_grants = _grant_tools_for_tier(R.TIER_CLIENT, "some-other-user-uuid", leaf)
        check(cl_grants == safe,
              f"client: grant-list == posture-safe subset ({len(cl_grants)} == {len(safe)})")
        check(cl_grants == _live_tools_for_tier(R.TIER_CLIENT),
              "client: grant-list == the UNTOUCHED live tier decision (proven equal)")
        check(op_grants == _live_tools_for_tier(R.TIER_OPERATOR),
              "operator: grant-list == the UNTOUCHED live tier decision (proven equal)")

        # none tier: live decision is empty; the grant shadow has no viewer-* match either
        check(_live_tools_for_tier(R.TIER_NONE) == [], "none tier: live decision is empty (unchanged)")

        # per-tool divergence count == 0 (the strongest equivalence statement)
        div = 0
        for name in all_tools:
            live_op = name in all_tools                       # operator sees all
            g_op = G.tool_allowed_via_grants(name, principal_type=G.PT_VIEWER,
                                             principal_id=G.OPERATOR_USER_ID, leaf=leaf)
            live_cl = name in safe
            g_cl = G.tool_allowed_via_grants(name, principal_type=G.PT_VIEWER,
                                             principal_id="x-user", leaf=leaf)
            div += (live_op != g_op) + (live_cl != g_cl)
        check(div == 0, f"ZERO live-vs-grant divergence across {len(all_tools)} tools × 2 tiers (got {div})")


def test_principal_type_axis():
    print("\n[3] principal_type is the KIND AXIS; '*' is a principal_ID (OWUI correction held)")
    check(G.PT_VIEWER in G.PRINCIPAL_TYPES and G.PT_AGENT in G.PRINCIPAL_TYPES,
          "viewer + agent are principal_TYPES (the extended kind axis)")
    check(G.WILDCARD == "*", "'*' is the wildcard principal_ID value (not a principal_type)")
    try:
        with tempfile.TemporaryDirectory() as d:
            G.grant(G.RT_TOOL, "x", "*", "y", leaf=os.path.join(d, "g.jsonl"))
        check(False, "principal_type='*' must fail loud (it is an id wildcard, not a type)")
    except ValueError:
        check(True, "principal_type='*' fails loud (correctly rejected as a type)")


def test_shadow_divergence_logs():
    print("\n[4] the gate's GRANT-SHADOW logs divergence (loud, never silent) + never changes the decision")
    audit = os.path.join(G._fcfg.STORE_DIR, "remote_mcp_audit.jsonl")
    before = os.path.getsize(audit) if os.path.exists(audit) else 0
    orig = R._tool_allowed_via_grants
    try:
        R._tool_allowed_via_grants = lambda *a, **k: True       # force shadow=True
        R._grant_shadow_audit("identity_fusion_test_tool", "client", "subj", live_allowed=False)
    finally:
        R._tool_allowed_via_grants = orig
    lines = open(audit).read().splitlines() if os.path.exists(audit) else []
    div = [l for l in lines if "GRANT_SHADOW_DIVERGENCE" in l and "identity_fusion_test_tool" in l]
    check(bool(div), "a forced divergence writes a GRANT_SHADOW_DIVERGENCE audit row (loud)")
    # agreeing path writes nothing new
    n0 = len(lines)
    R._grant_shadow_audit("identity_fusion_test_tool", "operator", G.OPERATOR_USER_ID, live_allowed=True)
    n1 = len(open(audit).read().splitlines()) if os.path.exists(audit) else 0
    check(n1 == n0, "an AGREEING shadow logs nothing (no noise when grant == live)")


if __name__ == "__main__":
    test_principal_kinds()
    test_seed_reproduces_current()
    test_principal_type_axis()
    test_shadow_divergence_logs()
    print("\n" + ("ALL GREEN" if not FAILS else f"{len(FAILS)} FAIL(S):"))
    for f in FAILS:
        print("  - " + f)
    sys.exit(1 if FAILS else 0)
