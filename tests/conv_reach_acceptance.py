"""tests/conv_reach_acceptance.py — X16 · operator-approves-the-reach.

A consequential build surfaces its BLAST RADIUS (X14: dependents-to-VERIFY,
dependencies-to-RESPECT, co-reference, semantic). The OPERATOR authorizes HOW FAR the edit
propagates. **Default = the pointed address only.** Wider (rename-ripples = the relational
cluster) ONLY on an explicit operator act. Edit-scope NEVER silently expands.

This suite proves (against controlled corpus fixtures so the assertions are exact):

  1. SURFACED CARRIES THE RADIUS — a build-intent minted at an address (surface_intent_at)
     persists its `blast_radius` (X14) into the payload, reloadable from disk, so the operator
     sees what the change could reach.

  2. DEFAULT-NARROW — approve the build WITHOUT a reach-expansion → the build's editable scope
     (payload["scope"], what dispatch_decision reads + the scope-diff gates on) == the pointed
     address's scope. Unchanged from today; never auto-expanded.

  3. EXPLICIT EXPANSION — the operator approves a WIDER reach (named blast-radius members, the
     rename-ripple cluster) → the editable scope now includes the files those members live in.
     The reach-approval is the operator's explicit, consent-time act.

  4. NEVER SILENT EXPANSION — a member NOT named in approve_reach is NOT pulled into scope. Only
     the named members widen the reach.

  5. THE SAFETY GATE (fabricated member rejected) — approving a member that is NOT in the
     SURFACED blast_radius RAISES (fail loud). Reach-approval can only ratify members the operator
     actually saw; it is never a scope-injection path that defeats the governed scope core.

  6. EMPTY-SCOPE = DENY-ALL PRESERVED — an address that resolves to NO code symbol (orphan /
     CSS-selector) mints a build-intent with EMPTY scope; with no resolvable blast radius there is
     nothing to expand, and the scope stays empty (DENY-ALL). The wire's empty=deny core is intact.

  7. OPERATOR-ONLY, OFF THE MCP FACE — `approve_reach` is NOT in RHM_VERBS; the RHM/MCP face gains
     no reach-expansion tool (no-bypass + the 7-verb whitelist + no-self-apply preserved).

  8. ORDERING / IDEMPOTENCY — reach-approval is only valid while the item is unresolved. After a
     terminal resolve, approve_reach RAISES (you can't widen the reach of a decided/launched build).

  9. THE WIRE GOVERNED PATH UNCHANGED — dispatch_decision still reads payload["scope"] and gates
     the scope-diff on it; an EXPANDED scope authorizes the expanded files, a NARROW one does not.
     (Proven WITHOUT a real claude -p — the launcher is MOCKED.)

LEAD-ONLY-SPAWN: this test NEVER fires a real `claude -p` / arms acceptEdits — every dispatch
path uses an injected MOCK launcher + a faulthandler hang-guard.
"""
import faulthandler
import json
import os
import sys
import tempfile

faulthandler.dump_traceback_later(120, exit=True)   # hang-guard: a real spawn/hang aborts loud

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite

PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def expect_raises(label, fn):
    global PASS
    try:
        fn()
    except Exception as e:
        PASS += 1
        print(f"  ok  {label} (raised {type(e).__name__})")
        return
    raise AssertionError(f"FAIL: {label} — expected a raise, none happened")


NODES = os.path.join(ROOT, "nodes")
reg = NodeRegistry(); reg.discover([NODES])


def fresh_suite():
    store = FsStore(os.path.join(tempfile.mkdtemp(prefix="reach-"), "store"))
    return Suite(store, reg, nodes_dir=NODES)


def with_corpus(symbols: dict, edges: dict | None = None):
    """A temp design/_system with a controlled code-symbols.json (+ optional code-edges.json),
    a suite pointed at it. Mirrors conv_blast_both_acceptance.py's fixture builder."""
    tmpsys = tempfile.mkdtemp(prefix="reach-corpus-")
    with open(os.path.join(tmpsys, "code-symbols.json"), "w", encoding="utf-8") as f:
        json.dump({"symbols": symbols,
                   "shared": [sid for sid, e in symbols.items()
                              if len(e.get("referenced_by") or []) >= 2]}, f)
    if edges is not None:
        with open(os.path.join(tmpsys, "code-edges.json"), "w", encoding="utf-8") as f:
            json.dump({"edges": edges, "stale": [], "shared": []}, f)
    s = fresh_suite()
    s._corpus_dir = lambda: tmpsys
    return s


# ── the fixture ──────────────────────────────────────────────────────────────────────────────
# The operator clicks address A, which resolves to symbol S (in runtime/suite.py). The blast
# radius of A:
#   • co_reference     : B (another address that touches S).
#   • dependents (X10) : D (a symbol that DEPENDS ON S — would break on a rename) in nodes/dep.py.
#   • dependencies(X10): P (a symbol S DEPENDS ON) in store/fs_store.py.
# The rename-ripple cluster the operator may approve = the dependent D's file.
A = "ui://inbox/coa"
B = "ui://inbox/build-review"
S = "code://suite/S"
D = "code://dep/D"
P = "code://store/P"

S_FILE = "runtime/suite.py"
D_FILE = "nodes/dep.py"
P_FILE = "store/fs_store.py"

SYMBOLS = {
    # S — clicked via A (referenced_by A so resolve_scope(A) → [S], scope=[S_FILE]); co-ref'd by B.
    S: {"file": S_FILE, "symbol": "S", "kind": "def", "resolves": True, "referenced_by": [A, B]},
    # D — a symbol that depends on S. It is NOT referenced_by A (so it is NOT in A's own scope), but
    # it IS in A's blast radius (structural_dependents). Lives in its own file.
    D: {"file": D_FILE, "symbol": "D", "kind": "def", "resolves": True, "referenced_by": [B]},
    # P — a dependency of S, in another file.
    P: {"file": P_FILE, "symbol": "P", "kind": "def", "resolves": True, "referenced_by": []},
    # B's own symbol so resolve_scope(B) works if needed (not load-bearing here).
}

EDGES = {
    S: {"depends_on": [P], "depended_by": [D], "resolves": True},
    D: {"depends_on": [S], "depended_by": [], "resolves": True},
    P: {"depends_on": [], "depended_by": [S], "resolves": True},
}


# ── 1. SURFACED CARRIES THE BLAST RADIUS (X14) ─────────────────────────────────────────────────
s = with_corpus(SYMBOLS, EDGES)
out = s.surface_intent_at(A, "this run button is too loud")
sid = out["id"]
rec = s.inbox.get(sid)                       # reload from disk
payload = rec["payload"]
check("the minted build-intent is a build-intent (intent=='build')",
      s.is_build_intent(rec))
check("the SURFACED payload carries a persisted blast_radius (X14) — the operator sees the reach",
      isinstance(payload.get("blast_radius"), dict))
br = payload["blast_radius"]
check(f"the persisted radius resolves symbol S → {br.get('symbols')}", br.get("symbols") == [S])
check(f"the radius carries the X10 dependent D (would break on rename) — {br.get('structural_dependents')}",
      D in (br.get("structural_dependents") or []))
check(f"the radius carries the X10 dependency P (to respect) — {br.get('structural_dependencies')}",
      P in (br.get("structural_dependencies") or []))
check(f"the radius carries the X9 co-reference B — {br.get('co_reference')}",
      B in (br.get("co_reference") or []))

# ── 2. DEFAULT-NARROW: no reach-approval → scope stays the pointed address's scope ─────────────
check(f"DEFAULT scope == the pointed address's scope (NOT expanded) — {payload.get('scope')}",
      sorted(payload.get("scope") or []) == [S_FILE])
check("DEFAULT: the dependent's file is NOT in scope (no silent expansion)",
      D_FILE not in (payload.get("scope") or []))
check("DEFAULT: the dependency's file is NOT in scope (no silent expansion)",
      P_FILE not in (payload.get("scope") or []))

# ── 3. EXPLICIT EXPANSION: the operator approves the rename-ripple (the dependent D) ───────────
r = s.approve_reach(sid, [D], reason="rename ripples into D — approve the wider reach")
rec2 = s.inbox.get(sid)
scope2 = rec2["payload"].get("scope") or []
check(f"EXPLICIT: the editable scope now INCLUDES the dependent D's file — {scope2}",
      D_FILE in scope2)
check("EXPLICIT: the original pointed-address file is STILL in scope (union, not replace)",
      S_FILE in scope2)
check("EXPLICIT: the approved member is recorded on the payload (legible consent / audit)",
      D in (rec2["payload"].get("reach_approved") or []))

# ── 4. NEVER SILENT EXPANSION: a member NOT approved is NOT in scope ───────────────────────────
check(f"NEVER-SILENT: P was NOT approved → its file is NOT in scope — {scope2}",
      P_FILE not in scope2)
check("NEVER-SILENT: B's co-reference was NOT approved → not pulled in",
      "ui://" not in " ".join(scope2))   # no ui:// ever leaks into the file scope

# ── 5. THE SAFETY GATE: a fabricated member (NOT in the surfaced radius) is REJECTED ───────────
s2 = with_corpus(SYMBOLS, EDGES)
out2 = s2.surface_intent_at(A, "another build")
sid2 = out2["id"]
expect_raises("SAFETY: approving a member NOT in the surfaced blast_radius RAISES (no scope injection)",
              lambda: s2.approve_reach(sid2, ["code://evil/INJECT"], reason="attack"))
# scope must be UNCHANGED after the refused injection (the refusal didn't half-apply).
check("SAFETY: after the refused injection the scope is UNCHANGED (no partial write)",
      sorted(s2.inbox.get(sid2)["payload"].get("scope") or []) == [S_FILE])
expect_raises("SAFETY: a raw repo path is NOT a valid member either (must be a radius member)",
              lambda: s2.approve_reach(sid2, ["runtime/../etc/passwd"], reason="attack2"))

# ── 6. EMPTY-SCOPE = DENY-ALL PRESERVED (orphan address → nothing to expand) ───────────────────
ORPHAN = "ui://tabbar"     # a CSS-selector / orphan ref — resolves to no code symbol
s3 = with_corpus(SYMBOLS, EDGES)
out3 = s3.surface_intent_at(ORPHAN, "comment on an orphan")
sid3 = out3["id"]
p3 = s3.inbox.get(sid3)["payload"]
check("DENY-ALL: an orphan address mints an EMPTY declared scope (the safety core)",
      (p3.get("scope") or []) == [])
br3 = p3.get("blast_radius") or {}
check("DENY-ALL: the orphan's blast radius is empty across kinds (nothing to expand)",
      not (br3.get("structural_dependents") or []) and not (br3.get("co_reference") or []))
# Approving an empty/absent member list must NOT turn empty-scope into allow-all.
expect_raises("DENY-ALL: approving a member that isn't in an empty radius RAISES (can't widen DENY-ALL)",
              lambda: s3.approve_reach(sid3, [D], reason="try to widen a deny-all build"))
check("DENY-ALL: the orphan build's scope is STILL empty (DENY-ALL intact)",
      (s3.inbox.get(sid3)["payload"].get("scope") or []) == [])

# ── 7. OPERATOR-ONLY, OFF THE MCP FACE ─────────────────────────────────────────────────────────
check("approve_reach is NOT in RHM_VERBS (operator-only, off the MCP face — no-bypass preserved)",
      "approve_reach" not in s.RHM_VERBS and "reach" not in s.RHM_VERBS)
check("the RHM verb whitelist is intact (unchanged by X16 — the 7 governed verbs + the 3 config-as-tools "
      "verbs + request_change, the convo→self-build bridge verb)",
      tuple(s.RHM_VERBS) == ("run", "propose", "build", "consult", "show", "panel", "extend",
                             "configure", "load_voice", "unload_voice", "request_change"))

# ── 8. ORDERING / IDEMPOTENCY: reach-approval invalid after a terminal resolve ─────────────────
s4 = with_corpus(SYMBOLS, EDGES)
out4 = s4.surface_intent_at(A, "yet another build")
sid4 = out4["id"]
s4.resolve_surfaced(sid4, "approve", reason="operator approves the narrow build")
expect_raises("ORDERING: approve_reach RAISES after a terminal resolve (can't widen a decided build)",
              lambda: s4.approve_reach(sid4, [D], reason="too late"))

# ── 9. THE WIRE GOVERNED PATH UNCHANGED — dispatch reads the (expanded) scope; launcher MOCKED ──
# Prove the EXPANDED scope authorizes the dependent's file at the dispatch scope-diff, and the
# NARROW scope does NOT — WITHOUT a real claude -p (the launcher is injected).
from runtime import implement as _impl

def mock_launch_touching(files):
    def _launch(decision, repo=None):
        return {"success": True, "summary": "mock build (no real claude -p)",
                "changed_files": list(files), "permission_mode": "plan"}
    return _launch

def mock_verifier_pass(result):
    # the injected fast verifier — signature verifier(result) -> (passed, reason).
    return True, "mock verify passed (no real suite run)"

# 9a — a NARROW build (no reach-approval) that touches the dependent's file → OVERRUN, NOT closed.
sN = with_corpus(SYMBOLS, EDGES)
outN = sN.surface_intent_at(A, "narrow build")
sidN = outN["id"]
vN = sN.resolve_surfaced(sidN, "approve", reason="approve narrow")
seqN = next(e["seq"] for e in sN.store.events_since(-1)
            if e.get("kind") == "resolve" and e.get("surfaced") == sidN)
resN = sN.dispatch_decision(sidN, seqN, launcher=mock_launch_touching([D_FILE]),
                            verifier=mock_verifier_pass)
check(f"WIRE: a NARROW build that touches the un-approved dependent file is an OVERRUN, not closed — {resN.get('closed')}",
      resN.get("closed") is False and resN.get("overrun"))

# 9b — an EXPANDED build (reach approved for D) touching the dependent's file → within scope.
sE = with_corpus(SYMBOLS, EDGES)
outE = sE.surface_intent_at(A, "expanded build")
sidE = outE["id"]
sE.approve_reach(sidE, [D], reason="approve the rename-ripple reach")
vE = sE.resolve_surfaced(sidE, "approve", reason="approve expanded")
seqE = next(e["seq"] for e in sE.store.events_since(-1)
            if e.get("kind") == "resolve" and e.get("surfaced") == sidE)
resE = sE.dispatch_decision(sidE, seqE, launcher=mock_launch_touching([D_FILE]),
                            verifier=mock_verifier_pass)
check(f"WIRE: an EXPANDED build (reach approved) touching the dependent file is WITHIN scope — closed={resE.get('closed')}",
      resE.get("closed") is True and not resE.get("overrun"))

# 9c — NO real claude -p ran (the launcher was mocked); confirm we never set acceptEdits.
check("LEAD-ONLY-SPAWN: COMPANY_WIRE_PERMISSION is NOT acceptEdits in this test (no real arm)",
      os.environ.get("COMPANY_WIRE_PERMISSION") != "acceptEdits")
check("LEAD-ONLY-SPAWN: implement.wire_armed() is False (the launcher was injected, never the real spawn)",
      _impl.wire_armed() is False)

faulthandler.cancel_dump_traceback_later()
print(f"\nconv_reach_acceptance.py — {PASS} checks GREEN")
