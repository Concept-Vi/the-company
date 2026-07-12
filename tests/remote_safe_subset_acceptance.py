"""tests/remote_safe_subset_acceptance.py — FL1: the public safe-tier gate (B4's second front).

PROVES, against the LIVE tool registry (the same one the public remote front reads):
  1. the safe-tier set == the DECLARED manifest (mcp_face/remote_safe_manifest.py), BOTH directions —
     an untracked safe tool is an accidental PUBLIC EXPOSURE; a manifest entry no longer tagged is
     accidental removal/rot. Either fails loud with the deliberate-edit teaching.
  2. no safe-tier tool is a WRITE: every one must carry readOnlyHint=True and destructiveHint=False —
     the public tier is read-only by construction, forever.
  3. the gate function itself (remote._tools_for_tier) returns exactly the manifest for the client
     tier, everything for the operator tier, and nothing for no-tier — the enforcement matches the
     declaration, not just the tags.

Suite-free: build_mcp(suite=None) registers every tool lazily (~1.5s) — no Suite is constructed, no
store touched. Exit 0 = PASS · 1 = FAIL.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

FAIL = []


def check(name, cond, detail=""):
    print(("  ok  " if cond else "  XX  ") + name + (f"\n      {detail}" if detail and not cond else ""))
    if not cond:
        FAIL.append(name)


def main():
    from mcp_face import server as srv
    from mcp_face import remote
    from mcp_face.remote_safe_manifest import REMOTE_SAFE_MANIFEST

    mcp = srv.build_mcp(suite=None)
    tools = dict(getattr(mcp, "_tool_manager")._tools)
    live_safe = {n for n, t in tools.items() if remote._tool_posture(t) == "safe"}

    # 1 — BOTH-DIRECTION manifest equality, teaching on drift
    exposed = sorted(live_safe - REMOTE_SAFE_MANIFEST)
    check("no tool is safe-tagged OUTSIDE the manifest (no accidental public exposure)",
          not exposed,
          f"UNDECLARED safe tools {exposed} — a tool became publicly visible with nobody deciding it. "
          f"Either remove its posture='safe' tag, or ADD it to mcp_face/remote_safe_manifest.py in the "
          f"same reviewed commit (the manifest edit IS the decision).")
    missing = sorted(REMOTE_SAFE_MANIFEST - live_safe)
    check("every manifest entry is still safe-tagged (no silent removal / manifest rot)",
          not missing,
          f"MANIFEST entries {missing} are no longer safe-tagged in the registry — client visibility "
          f"changed (or a tool was renamed/removed). Update the manifest deliberately.")

    # 2 — the public tier is READ-ONLY by construction
    not_readonly = []
    for n in sorted(live_safe):
        ann = getattr(tools[n], "annotations", None)
        ro = getattr(ann, "readOnlyHint", None) if not isinstance(ann, dict) else ann.get("readOnlyHint")
        de = getattr(ann, "destructiveHint", None) if not isinstance(ann, dict) else ann.get("destructiveHint")
        if ro is not True or de is True:
            not_readonly.append((n, ro, de))
    check("every safe-tier tool is read-only (readOnlyHint=True, destructive=False) — writes never public",
          not not_readonly, f"safe-but-not-readonly: {not_readonly}")

    # 3 — the GATE enforces the declaration (not just the tags)
    client_view = {n for n, _ in remote._tools_for_tier(remote.TIER_CLIENT)} \
        if hasattr(remote, "TIER_CLIENT") else set()
    if hasattr(remote, "_TOOL_MANAGER"):
        # point the gate's manager at THIS registry for the check (the module normally binds at serve time)
        remote._TOOL_MANAGER = getattr(mcp, "_tool_manager")
        client_view = {n for n, _ in remote._tools_for_tier(remote.TIER_CLIENT)}
        operator_view = {n for n, _ in remote._tools_for_tier(remote.TIER_OPERATOR)}
        none_view = remote._tools_for_tier("")
        check("client tier sees exactly the manifest", client_view == REMOTE_SAFE_MANIFEST,
              f"client-view − manifest: {sorted(client_view - REMOTE_SAFE_MANIFEST)}; "
              f"manifest − client-view: {sorted(REMOTE_SAFE_MANIFEST - client_view)}")
        check("operator tier sees everything", operator_view == set(tools))
        check("no-tier sees nothing (fail-closed)", none_view == [])
    else:
        check("gate check ran", False, "remote._TOOL_MANAGER not found — gate wiring changed; update this test")

    print(f"\n  registry: {len(tools)} tools · safe-tier: {len(live_safe)} · manifest: {len(REMOTE_SAFE_MANIFEST)}")
    if FAIL:
        print(f"\nFAIL — {len(FAIL)} failed")
        sys.exit(1)
    print("remote_safe_subset_acceptance: PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
