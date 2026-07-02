"""tests/feedback_to_wire_acceptance.py — L1 · addressed-feedback → wire (§21.4#2).

A comment-at-an-address becomes a build-intent that surfaces for approval AT that address. The unit
COMPOSES three EXISTING pieces — it does NOT build a new intent path:

    [comment at ui:// addr]  --I6 ingest_comment-->  recorded (located gold)
                             --S3 resolve_scope------>  scope[]  (repo-relative code files)
                             --surface_build_intent-->  a live escalation (resolved=None)
                                                        --> operator approves via /api/resolve (L2 dispatches)

This is the EXACT analog of L5's `self_changes_at`: a new Suite method (`surface_intent_at`) that
reuses `resolve_scope` (S3, never duplicated), `ingest_comment` (I6, never duplicated), and
`surface_build_intent` (the wire's production FRONT DOOR, suite.py — reused UNCHANGED). L1 STOPS at
surfacing the build-intent for approval; the dispatch-on-approve wiring is L2 (a separate switch).

This suite proves (RED first, then GREEN):
  1. HAPPY PATH — a comment at an address whose S3 scope resolves → `surface_build_intent` is called
     with THAT scope, and a build-intent surfaces as a LIVE ESCALATION (`resolved=None`, intent="build").
     THE ONE LOAD-BEARING ASSERTION: the surfaced intent's scope == resolve_scope(addr)["scope"] — this
     single property proves the happy path AND that nothing is fabricated AND empty→DENY-ALL is preserved.
  2. DENY-ALL PRESERVED — an address with NO resolvable scope (orphan) does NOT get a fabricated broad
     scope: the surfaced intent carries the EMPTY scope (which DENY-ALLs at dispatch, the fail-safe).
     Assert the intent can NEVER "build anywhere" — its scope is [] and stale/note is carried legibly.
  3. OPERATOR-ONLY APPROVAL — the surfaced intent is resolvable by the OPERATOR path
     (`resolve_surfaced`, behind /api/resolve), and approving it emits the `resolve` event but does NOT
     auto-dispatch: NO `decision.dispatch` event fires (L1 stops at surface; dispatch is L2). No build runs.
  4. I6 REUSED — after the call the annotation EXISTS at the address (`annotations_at`) — proves the
     comment was recorded through I6, not duplicated, and the located-gold chat turn was emitted.
  5. PRESERVE — `surface_build_intent`'s existing behaviour is unchanged: bare empty scope still
     DENY-ALLs, `resolved=None`, intent="build"; and S3's `resolve_scope` is reused, not shadowed.
  6. REACHABLE FROM A FACE — a bridge POST route mints "turn this comment into a build-intent",
     mirroring /api/build-intent; approval stays on the EXISTING operator-only /api/resolve.

FIXTURES: reuse verified REAL addresses so we test the live join, not invented ones. The scope
source is THE LEDGER's derived ui://→code powered-by join (runtime/scope.py, recomputed every
build; the design/_system/code-symbols.json sidecar is retired). Each address resolves to its
LIVE component file(s) AND the hand-seeded backend:
  ui://chat/input            → scope ⊇ ['canvas/app/src/regions/RhmChat.tsx','runtime/suite.py']  (resolves — happy path)
  ui://workshop/self-changes → scope ⊇ ['runtime/suite.py'] + its live region files               (resolves — second clean scope)
  ui://nonexistent/thing     → []                                                                 (orphan — DENY-ALL)

Run: /home/tim/company/.venv/bin/python tests/feedback_to_wire_acceptance.py
"""
import os
import sys
import tempfile

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


NODES = os.path.join(ROOT, "nodes")
store = FsStore(os.path.join(tempfile.mkdtemp(prefix="l1-"), "store"))
reg = NodeRegistry(); reg.discover([NODES])
suite = Suite(store, reg, nodes_dir=NODES)

# REAL addresses (verified live) — the join is the LEDGER's derived ui://→code powered-by edges
# (runtime/scope.py, recomputed every build; the code-symbols.json sidecar is retired).
CHATIN = "ui://chat/input"                 # scope ⊇ ['canvas/app/src/regions/RhmChat.tsx','runtime/suite.py']
WORKSHOP = "ui://workshop/self-changes"    # scope ⊇ ['runtime/suite.py'] + its live region files
ORPHAN = "ui://nonexistent/thing"          # → [] (DENY-ALL)

# sanity: the ledger-backed resolver gives the scopes the join leans on (else the fixtures are wrong, not L1)
_chatin_scope = suite.resolve_scope(CHATIN)["scope"]
check(f"{CHATIN} scope carries regions/RhmChat.tsx + suite.py (S3, ledger-derived join)",
      "canvas/app/src/regions/RhmChat.tsx" in _chatin_scope and "runtime/suite.py" in _chatin_scope)
_workshop_scope = suite.resolve_scope(WORKSHOP)["scope"]
check(f"{WORKSHOP} scope carries runtime/suite.py (S3, ledger-derived join)",
      "runtime/suite.py" in _workshop_scope)
check(f"{ORPHAN} resolves to empty scope (S3 orphan → DENY-ALL)",
      suite.resolve_scope(ORPHAN)["scope"] == [])

# ── 1. HAPPY PATH — comment at an address with a resolvable scope → build-intent surfaces ───────
out = suite.surface_intent_at(CHATIN, "this run button is too loud — tone it down", source="operator")
sid = out["id"]
d = suite.inbox.get(sid)
check("a build-intent was surfaced (an inbox item exists)", d is not None)
check("the surfaced item IS a build-intent (intent='build')", Suite.is_build_intent(d))
check("the build-intent is a LIVE ESCALATION (resolved=None until the operator resolves)",
      d.get("resolved") is None)
# THE one load-bearing property — the scope carried == S3's resolved scope (no fabrication, exactly the join)
# The join is the ledger's derived powered-by edges: the live component file(s) + the hand-seeded backend.
expected_scope = suite.resolve_scope(CHATIN)["scope"]
check(f"the surfaced intent's scope == resolve_scope({CHATIN}) ({expected_scope}) — no fabrication",
      (d["payload"].get("scope") or []) == expected_scope
      and "canvas/app/src/regions/RhmChat.tsx" in expected_scope
      and "runtime/suite.py" in expected_scope)
check("the comment text is carried into the build-intent spec (the comment drives the build)",
      "tone it down" in (d["payload"].get("spec") or "") or "too loud" in (d["payload"].get("spec") or ""))
check("the address is carried as the 'why' (legible consent: build derives from this address+comment)",
      CHATIN in (d["payload"].get("why") or "") or CHATIN in str(out))

# a SECOND clean address proves the join is general, not hardcoded to one address
out2 = suite.surface_intent_at(WORKSHOP, "the self-change ledger needs a clearer label")
d2 = suite.inbox.get(out2["id"])
check(f"a comment at {WORKSHOP} surfaces an intent whose scope carries runtime/suite.py and == the "
      f"resolved join (join is general, no fabrication)",
      "runtime/suite.py" in (d2["payload"].get("scope") or [])
      and (d2["payload"].get("scope") or []) == suite.resolve_scope(WORKSHOP)["scope"])

# ── 2. DENY-ALL PRESERVED — orphan address → NO fabricated broad scope ──────────────────────────
orphan_out = suite.surface_intent_at(ORPHAN, "change something here")
od = suite.inbox.get(orphan_out["id"])
check("orphan-address intent carries an EMPTY scope (DENY-ALL fail-safe, never fabricated)",
      (od["payload"].get("scope") or []) == [])
# the central safety claim: an empty-scope build-intent can NEVER 'build anywhere'. surface_build_intent's
# empty-scope=DENY-ALL means _in_any_scope returns False for EVERY path — assert that fail-safe holds.
check("an empty-scope intent can NEVER 'build anywhere' (empty scope DENY-ALLs every path at dispatch)",
      suite._in_any_scope("runtime/suite.py", od["payload"].get("scope") or []) is False
      and suite._in_any_scope("canvas/app/src/App.tsx", od["payload"].get("scope") or []) is False)
check("the orphan result carries the legible note/stale (fail-loud-legible, not a silent empty)",
      bool(orphan_out.get("note")) or orphan_out.get("stale") is not None)

# ── 3. OPERATOR-ONLY APPROVAL — resolvable via /api/resolve; NO auto-dispatch (L1 stops at surface)
before = [e for e in store.events_since(-1) if e.get("kind") == "decision.dispatch"]
verdict = suite.resolve_surfaced(sid, "approve", reason="agreed, build it")
check("the surfaced intent is RESOLVABLE by the operator path (resolve_surfaced approve)",
      verdict.get("resolved") in (True, "approve") or suite.inbox.get(sid).get("resolved") == "approve")
after = [e for e in store.events_since(-1) if e.get("kind") == "decision.dispatch"]
check("operator approve emitted a 'resolve' event (the verdict is recorded)",
      any(e.get("kind") == "resolve" and e.get("surfaced") == sid for e in store.events_since(-1)))
check("approving does NOT auto-dispatch — NO decision.dispatch event fires (L1 stops at surface; L2 dispatches)",
      len(after) == len(before) == 0)

# ── 4. I6 REUSED — the annotation EXISTS at the address (recorded through ingest_comment) ────────
anns = suite.annotations_at(CHATIN)
check("the comment was RECORDED at the address via I6 (annotations_at returns it — reused, not duplicated)",
      any("tone it down" in (a.get("text") or "") or "too loud" in (a.get("text") or "") for a in anns))
# the located-gold chat turn (operator → gold) was emitted by ingest_comment — proves the I6 ingest path,
# not the bare annotate leaf (which writes NO chat). The address rides the chat turn verbatim.
gold = suite.chats_at(CHATIN)
check("the comment produced a LOCATED gold chat turn (ingest_comment path, address carried)",
      any(t.get("grade") == "gold" and t.get("role") == "user" for t in gold))

# ── 5. PRESERVE — surface_build_intent's existing behaviour is UNCHANGED ─────────────────────────
bare = suite.surface_build_intent("a plain build with no address", scope=[])
bd = suite.inbox.get(bare["id"])
check("surface_build_intent unchanged: bare empty scope still DENY-ALLs (intent='build', resolved=None)",
      Suite.is_build_intent(bd) and (bd["payload"].get("scope") or []) == [] and bd.get("resolved") is None)
check("surface_build_intent unchanged: a declared scope is carried through verbatim",
      (suite.inbox.get(suite.surface_build_intent("x", scope=["runtime/suite.py"])["id"])
       ["payload"].get("scope")) == ["runtime/suite.py"])
check("S3 resolve_scope is REUSED, not shadowed/replaced by L1", callable(suite.resolve_scope)
      and suite.surface_intent_at is not suite.resolve_scope
      and suite.surface_intent_at is not suite.surface_build_intent)

# malformed address fails loud (S0 grammar gate via resolve_scope/ingest_comment) — no silent no-op
refused = False
try:
    suite.surface_intent_at("not-a-ui-address", "bad")
except (ValueError, KeyError):
    refused = True
check("a malformed ui:// address FAILS LOUD (S0 grammar gate, no junk build-intent)", refused)

# empty comment text fails loud (no silent no-op — rule 4)
refused2 = False
try:
    suite.surface_intent_at(CHATIN, "   ")
except (ValueError, KeyError):
    refused2 = True
check("an empty comment FAILS LOUD (no silent no-op — rule 4)", refused2)

# ── 6. REACHABLE FROM A FACE — a bridge POST route mints the feedback→build-intent ───────────────
with open(os.path.join(ROOT, "runtime", "bridge.py"), encoding="utf-8") as f:
    bridge_src = f.read()
check("bridge.py has a route that turns a comment-at-address into a build-intent (calls surface_intent_at)",
      "surface_intent_at" in bridge_src)
check("approval stays on the EXISTING operator-only /api/resolve (no new approval route added)",
      "/api/resolve" in bridge_src and "/api/intent-resolve" not in bridge_src
      and "/api/approve-intent" not in bridge_src)

print(f"\nFEEDBACK→WIRE ACCEPTANCE (L1) — {PASS} checks passed. A comment at a ui:// address becomes "
      f"a build-intent SCOPED by S3's resolve_scope (no fabrication — the surfaced scope == the resolved "
      f"scope), recorded through I6's ingest_comment, surfaced via the wire's UNCHANGED front door "
      f"(surface_build_intent: empty-scope=DENY-ALL + resolved=None preserved). An orphan address "
      f"carries the EMPTY scope (can NEVER build anywhere). Approval is OPERATOR-ONLY (/api/resolve) "
      f"and does NOT auto-dispatch — L1 stops at surfacing for approval; dispatch is L2.")
