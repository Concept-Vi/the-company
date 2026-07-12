"""tests/fabric_principal_acceptance.py — the Phase-4 identity door (design v2): principal + principal_act.

PROVES BY USE (tmp reg dir; never ~/company/.data): resolve returns ONE enriched row (presence + kind +
durable record) · honest not-found + honest ambiguity (never a guess) · roster = registry rows with live
enrichment · whoami teaches on ambiguity · describe writes self-description idempotently · register is
an honest cross-repo TEACHING stub (never a faked fold). Access stays a separate door (unchanged here).

Exit 0 = PASS · 1 = FAIL.
"""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from runtime import cc_channels as cc         # noqa: E402
from runtime import identity                  # noqa: E402
from mcp_face.tools import principal as p_mod  # noqa: E402

FAIL = []


def check(name, cond):
    print(("  ok  " if cond else "  XX  ") + name)
    if not cond:
        FAIL.append(name)


class _StubMCP:
    def __init__(self):
        self.tools = {}
        self.annotations = {}

    def tool(self, annotations=None):
        def deco(fn):
            self.tools[fn.__name__] = fn
            self.annotations[fn.__name__] = annotations
            return fn
        return deco


class _FakeSuite:
    def get_agent_session(self, sid):
        if sid == "u-1":
            return {"id": "u-1", "state": "closed", "title": "known one", "cwd": "/w"}
        raise ValueError(f"unknown session {sid}")


def main():
    tmp = tempfile.mkdtemp(prefix="fabric-principal-")
    cc.CHAN_DIR = tmp

    live_reg = {"handle": "ch-abc", "session_id": "u-1", "cwd": "/w", "pid": 1, "claude_pid": 1,
                "port": 9}
    json.dump(live_reg, open(os.path.join(tmp, "ch-abc.json"), "w"))
    json.dump({"handle": "tim", "port": 5, "transport": "channel", "cwd": "/home/tim"},
              open(os.path.join(tmp, "tim.json"), "w"))

    live_row = {"uuid": "u-1", "uuid_how": "reg.session_id", "handle": "ch-abc", "as_id": None,
                "agent_id": None, "cwd": "/w", "description": "d", "model": "", "kind": "agent",
                "state": "unsupervised-live", "transports": ["channel"], "reachable": True,
                "port": 9, "pid": 1, "claude_pid": 1, "forked_from": None, "reg": live_reg,
                "sources": ["cc_channels"]}
    identity.resolve = lambda target, **kw: dict(live_row) if target in ("u-1", "ch-abc") else None
    identity.presence_all = lambda base=None, deep=False: [dict(live_row)]

    mcp = _StubMCP()
    p_mod.register(mcp, _FakeSuite())
    principal, principal_act = mcp.tools["principal"], mcp.tools["principal_act"]

    # ── resolve: one enriched row ──
    r = principal(op="resolve", target="ch-abc")
    check("resolve found + live presence", r["found"] and r["reachable"] and r["transports"] == ["channel"])
    check("enriched with principal KIND", r.get("principal_kind", {}).get("kind") == "agent")
    check("enriched with the durable RECORD", (r.get("record") or {}).get("title") == "known one")
    check("raw reg NOT leaked on the row", "reg" not in r)

    r2 = principal(op="resolve", target="nope")
    check("not-found is HONEST (never fabricated)", r2["found"] is False and "directory" in r2["reason"])

    def _amb(target, **kw):
        raise identity.AmbiguousTarget("2 match")
    identity.resolve = _amb
    r3 = principal(op="resolve", target="x")
    check("ambiguity honest, never a guess", r3["found"] is False and r3.get("ambiguous") is True)
    identity.resolve = lambda target, **kw: dict(live_row) if target in ("u-1", "ch-abc") else None

    # ── roster: registry rows + live enrichment ──
    r4 = principal(op="roster")
    by_handle = {p.get("handle"): p for p in r4["principals"]}
    check("roster lists the agent + the viewer", "ch-abc" in by_handle and "tim" in by_handle)
    check("agent kind derived", by_handle["ch-abc"]["kind"] == "agent")
    check("viewer kind derived (tim.json)", by_handle["tim"]["kind"] == "viewer")
    check("live state enriches the live one, absent on the viewer",
          (by_handle["ch-abc"].get("live") or {}).get("reachable") is True
          and by_handle["tim"].get("live") is None)

    # ── whoami: teaching on ambiguity ──
    from runtime import session_scan
    def _boom(*a, **kw):
        raise session_scan.AmbiguousSelfError("multiple transcripts — set COMPANY_SESSION_ID")
    orig_own, orig_member = session_scan.resolve_own_session, session_scan.resolve_self_member
    session_scan.resolve_own_session = _boom
    session_scan.resolve_self_member = lambda: {"handle": "ch-me", "name": "me", "description": ""}
    try:
        r5 = principal(op="whoami")
        check("whoami ambiguous → TEACHING, not a guess",
              r5.get("ambiguous") is True and "COMPANY_SESSION_ID" in r5.get("teaching", ""))
        check("whoami still surfaces the member reg", r5.get("member", {}).get("handle") == "ch-me")
        session_scan.resolve_own_session = lambda **kw: {"session_id": "u-me", "how": "marker", "cwd": "/w"}
        r6 = principal(op="whoami")
        check("whoami resolves the durable address", r6.get("address") == "session://u-me")
    finally:
        session_scan.resolve_own_session, session_scan.resolve_self_member = orig_own, orig_member

    # ── describe: idempotent self-description write ──
    cc.register_self = lambda name="", description="", **kw: {
        "handle": "ch-me", "session_id": "u-me", "name": name, "description": description,
        "transport": "mail"}
    r7 = principal_act(op="describe", name="builder", description="doing the redesign")
    check("describe writes name+description", r7["name"] == "builder" and "redesign" in r7["description"])
    try:
        principal_act(op="describe")
        check("describe with nothing raises teaching", False)
    except ValueError:
        check("describe with nothing raises teaching", True)

    # ── register: the honest cross-repo teaching stub ──
    r8 = principal_act(op="register", name="my-role")
    check("register TEACHES the substrate path (never a faked fold)",
          r8["ok"] is False and "agent_register" in r8["teaching"])

    # ── posture: read safe, write untagged (operator-tier) ──
    ann_r, ann_w = mcp.annotations["principal"], mcp.annotations["principal_act"]
    def _posture(a):
        return getattr(a, "posture", None) or (getattr(a, "model_extra", None) or {}).get("posture")
    check("principal read posture=safe", _posture(ann_r) == "safe")
    check("principal_act write UNTAGGED (operator-only on the remote front)", _posture(ann_w) is None)

    if FAIL:
        print(f"\nFAIL — {len(FAIL)} failed")
        sys.exit(1)
    print("\nfabric_principal_acceptance: PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
