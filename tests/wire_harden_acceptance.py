"""tests/wire_harden_acceptance.py — WIRE-HARDEN (H1–H8): the wire's definition-of-done == the
HUMAN BUILD LOOP's discipline. Proves, BY USE, that an autonomous build can never leave the system
broken / incoherent / half-done — the gap that let the reverse incident through (a node-type built
but the self-description NOT refreshed → drift went red, silently).

This is the SOLE exercise of the default `_wire_verify` path. Every OTHER wire suite injects a
`verifier=lambda r:(True,...)` and so takes the fast bypass — they prove the bypass still holds, NOT
the hardening. So here we drive `dispatch_decision` with `verifier=None` and inject only
`launcher` / `suite_runner` / `critic`, exercising the real verify gate.

To stay deterministic + sandbox-safe (never touch the real repo's MAP.md/STATE.md/nodes/ — that would
poison the wholesale `tests/*.py` run), we point `nodes_dir` at a TEMP repo: `_repo_root` is just
`dirname(nodes_dir)`, so the whole self-description machinery follows. The sandbox carries the marker
blocks `refresh_self_description` needs (`<!--REGISTRY-->`, `<!--SUITES-->`). The injected
`suite_runner` evaluates drift IN-PROCESS via `suite.doc_drift()` (faithful to what
`drift_acceptance.py` asserts) rather than spawning the real suite (which computes its own ROOT).

H-items proven:
  H1 — a build that breaks an affected suite does NOT close → surfaces back, reason names the suite.
  H2 — the close runs refresh_self_description + the verify runs the drift check; a node build leaves
       drift GREEN (the reverse incident reproduced THEN fixed: rediscover-only = drift RED;
       rediscover+refresh = drift GREEN → the refresh is load-bearing, not a tautology).
  H3 — after a successful node build the new type is LIVE in suite.registry (not just on disk).
  H4 — a surface-touching build (canvas/) CANNOT auto-close → surfaces a dispatcher-INERT review item.
  H5 — the adversarial critic is a first-class part of verify, SEPARATE from the builder's self-report.
  H6 — ANY verify miss → surfaces back, never a silent close; the item does NOT reach implemented.
  H7 — build_instruction carries the FULL standard (design system + self-description + tests/drift).
  H8 — a node build that also edits MAP.md/STATE.md (per H7) does NOT read as a scope overrun.

Run: .venv/bin/python tests/wire_harden_acceptance.py
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
from runtime import implement as impl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


# ---------------------------------------------------------------------------------------------
# A self-contained SANDBOX repo so _wire_verify's make-it-live + refresh + drift run against a
# throwaway tree, never the real repo. nodes_dir → sandbox/nodes; _repo_root → sandbox.
# ---------------------------------------------------------------------------------------------
def fresh_sandbox():
    base = tempfile.mkdtemp(prefix="wire-harden-")
    nodes = os.path.join(base, "nodes")
    tests = os.path.join(base, "tests")
    os.makedirs(nodes); os.makedirs(tests)
    # stub acceptance-suite files so _affected_suites (which reads _repo_root/tests/*.py) finds the
    # names it always-includes (drift + the wire suites) + a nodes-related one. The injected
    # suite_runner decides pass/fail — these files are never executed (no spawn), they only NAME the
    # suites that exist so the affected-set is realistic in the sandbox.
    for stub in ("drift_acceptance", "wire_acceptance", "wire_loop_acceptance", "wire_adversarial",
                 "e4_registry", "nodes_acceptance"):
        open(os.path.join(tests, stub + ".py"), "w").write("# stub\n")
    # one trivial pre-existing node so the registry is non-empty.
    with open(os.path.join(nodes, "seed.py"), "w") as f:
        f.write("def run(inputs, config):\n    return {}\n")
    # the marker blocks refresh_self_description needs (it returns early if the file is absent).
    with open(os.path.join(base, "MAP.md"), "w") as f:
        f.write("# sandbox map\n<!--REGISTRY:START--> placeholder <!--REGISTRY:END-->\n")
    with open(os.path.join(base, "STATE.md"), "w") as f:
        f.write("# sandbox state\n<!--SUITES:START--> placeholder <!--SUITES:END-->\n")
    store = FsStore(os.path.join(base, "store"))
    reg = NodeRegistry(); reg.discover([nodes])
    s = Suite(store, reg, nodes_dir=nodes)
    return s, base, nodes


def approve_seq(suite, sid):
    suite.resolve_surfaced(sid, "approve", reason="authorize this build")
    ev = next(e for e in reversed(suite.store.events_since(-1))
              if e.get("kind") == "resolve" and e.get("surfaced") == sid)
    return ev["seq"]


def in_process_drift_runner(suite):
    """Inject the affected-suite runner so 'drift_acceptance' is evaluated IN-PROCESS via doc_drift()
    (faithful to what drift_acceptance.py asserts) instead of spawning the real suite (wrong ROOT in a
    sandbox). Every other affected suite is reported green (not exercised in-sandbox)."""
    def runner(name):
        if name == "drift_acceptance":
            bad = {k: v for k, v in suite.doc_drift().items() if v}
            return (not bad, f"drift RED: {bad}") if bad else (True, "drift green")
        return (True, "n/a in sandbox")
    return runner


def node_launch(sandbox, nodes, name="newnode", changed=None):
    """A launcher that WRITES a real node file into the sandbox (the build's side effect) and reports it
    changed — so make-it-live + refresh + drift run for real against the sandbox."""
    chg = changed if changed is not None else [f"nodes/{name}.py"]
    def _launch(decision, *, repo):
        with open(os.path.join(nodes, name + ".py"), "w") as f:
            f.write("def run(inputs, config):\n    return {}\n")
        return {"finished": True, "success": True, "exit_code": 0, "summary": "added " + name,
                "changed_files": list(chg), "permission_mode": "acceptEdits"}
    return _launch


print("\n=== H7 — build_instruction carries the FULL standard (design system + self-desc + tests/drift) ===")
instr = impl.build_instruction({"payload": {"spec": "add a node", "scope": ["nodes/"]}})
check("instruction names the DESIGN SYSTEM bar for operator-facing surfaces",
      "design system" in instr.lower() and ("components" in instr.lower() and "token" in instr.lower()))
check("instruction requires UPDATING the self-description as part of the change",
      "self-description" in instr.lower())
check("instruction requires keeping the tests + the drift-check GREEN",
      "green" in instr.lower() and "drift" in instr.lower())
check("instruction still carries the existing REVIEWED / separate-review standard (no regression)",
      "REVIEWED" in instr and "separate review pass" in instr.lower())


print("\n=== H2/H3 — the REVERSE INCIDENT reproduced THEN fixed (refresh is load-bearing, not tautology) ===")
s, sandbox, nodes = fresh_sandbox()
# write a node on disk WITHOUT making it live / refreshing — exactly the reverse incident's state.
with open(os.path.join(nodes, "manual.py"), "w") as f:
    f.write("def run(inputs, config):\n    return {}\n")
s.registry.rediscover([nodes])               # rediscover ONLY (the bug: live on disk, MAP stale)
drift_after_rediscover = {k: v for k, v in s.doc_drift().items() if v}
check("rediscover WITHOUT refresh → drift RED (the reverse incident reproduced: node live, MAP stale)",
      bool(drift_after_rediscover.get("map_node_types")))
ok, why = s._make_live_and_refresh()         # rediscover + refresh (the fix)
check("_make_live_and_refresh succeeds", ok)
check("after refresh → drift GREEN (the refresh is load-bearing — fixes the incident)",
      not any(s.doc_drift().values()))
check("H3: the manually-written node is LIVE in the registry (rediscovered, not just on disk)",
      "manual" in s.registry.types)
map_text = open(os.path.join(sandbox, "MAP.md")).read()
check("H2: refresh_self_description wrote the new node into the MAP registry block",
      "manual" in map_text)


print("\n=== H2/H3 by-use — a NODE build through dispatch_decision closes + leaves drift GREEN + live ===")
s, sandbox, nodes = fresh_sandbox()
intent = s.surface_build_intent("add a node-type", scope=["nodes/"], consequence_class="decision_build")
sid = intent["id"]; seq = approve_seq(s, sid)
out = s.dispatch_decision(sid, seq,                       # NO verifier → the real _wire_verify path
                          launcher=node_launch(sandbox, nodes, "builtnode"),
                          suite_runner=in_process_drift_runner(s))
check("the node build CLOSED (verified, in scope, drift green) → status=implemented",
      out.get("closed") and out.get("status") == "implemented")
check("H3 by-use: the built node-type is LIVE in suite.registry", "builtnode" in s.registry.types)
check("H2 by-use: drift is GREEN after the build (self-description refreshed)",
      not any(s.doc_drift().values()))
check("the build surfaced a (dispatcher-inert) review item — implemented ≠ silent close",
      bool(out.get("review_surfaced")) and s.is_build_intent(s.inbox.get(out["review_surfaced"])) is False)


print("\n=== H1 — a build that BREAKS an affected suite does NOT close → surfaces back ===")
s, sandbox, nodes = fresh_sandbox()
intent = s.surface_build_intent("a build that breaks a test", scope=["nodes/"],
                                consequence_class="decision_build")
sid = intent["id"]; seq = approve_seq(s, sid)
def breaking_runner(name):
    if name == "drift_acceptance":
        return (True, "drift green")
    return (False, "boom: this suite is red after the build")   # an affected suite fails
out = s.dispatch_decision(sid, seq, launcher=node_launch(sandbox, nodes, "n2"),
                          suite_runner=breaking_runner)          # NO verifier
check("a broken affected suite does NOT close the item (H1)",
      not out.get("closed") and s.inbox.get(sid)["status"] != "implemented")
check("the failure surfaced back as a responsive review item (H6)", bool(out.get("requeued")))
req = s.inbox.get(out["requeued"])
check("the surfaced reason names the failing suite (fail-loud, not silent)",
      "FAILED" in req["payload"].get("why", "") or "boom" in req["payload"].get("why", ""))


print("\n=== H2b — a build that leaves DRIFT RED does NOT close → surfaces back ===")
# Simulate a build whose refresh can't reflect it (force drift red via the in-process runner). We
# wedge drift red by having the launcher NOT actually create the node it claims changed → after
# rediscover+refresh the claimed type isn't present, but we assert via a runner that reports drift red.
s, sandbox, nodes = fresh_sandbox()
intent = s.surface_build_intent("a build that leaves drift red", scope=["nodes/"],
                                consequence_class="decision_build")
sid = intent["id"]; seq = approve_seq(s, sid)
def drift_red_runner(name):
    if name == "drift_acceptance":
        return (False, "drift RED: {'map_node_types': ['ghost']}")
    return (True, "n/a")
out = s.dispatch_decision(sid, seq, launcher=node_launch(sandbox, nodes, "n3"),
                          suite_runner=drift_red_runner)
check("a drift-red build does NOT close (the reverse incident is now CAUGHT, not silent)",
      not out.get("closed") and s.inbox.get(sid)["status"] != "implemented")
check("drift-red surfaces back with the reason (H2/H6)",
      bool(out.get("requeued")) and "drift" in s.inbox.get(out["requeued"])["payload"].get("why", "").lower())


print("\n=== H4 — a SURFACE-touching build (canvas/) CANNOT auto-close → surfaces INERT for design review ===")
s, sandbox, nodes = fresh_sandbox()
intent = s.surface_build_intent("touch the canvas surface", scope=["canvas/"],
                                consequence_class="decision_build")
sid = intent["id"]; seq = approve_seq(s, sid)
out = s.dispatch_decision(
    sid, seq,
    launcher=lambda d, *, repo: {"finished": True, "success": True, "exit_code": 0,
                                 "summary": "ui change", "changed_files": ["canvas/app/src/App.tsx"],
                                 "permission_mode": "acceptEdits"},
    suite_runner=in_process_drift_runner(s))                 # NO verifier → real FORM gate runs
check("a surface-touching build does NOT auto-close (FORM is unverifiable, no design system yet) (H4)",
      not out.get("closed") and s.inbox.get(sid)["status"] != "implemented")
check("it is flagged form_unverifiable + surfaced back (H4/H6)",
      out.get("form_unverifiable") and bool(out.get("requeued")))
form_item = s.inbox.get(out["requeued"])
check("the surfaced form item is DISPATCHER-INERT (NOT a build-intent — re-approving it never rebuilds)",
      s.is_build_intent(form_item) is False and form_item["payload"].get("kind") == "build_form_review")
check("the form item names the missing design-critic / FORM bar (the named plug-in hook)",
      "FORM" in form_item["payload"].get("why", "") and "design" in form_item["payload"].get("why", "").lower())
# the named seam exists as a real method (not a comment) and currently forces surface-back for surfaces.
ok_be, _ = s._design_critic(["runtime/x.py"])
ok_fe, _ = s._design_critic(["canvas/app/src/App.tsx"])
check("_design_critic is a real seam: backend build passes, surface build fails (the fail-safe default)",
      ok_be is True and ok_fe is False)
# CRITICAL (the FORM gate is STRUCTURAL, not part of the replaceable verifier): a surface build with an
# INJECTED PASSING verifier (the live WIRE-LOOP path — wire_loop_acceptance injects verifier=ok_verify)
# must STILL surface inert, never close. If FORM lived inside the bypassable _wire_verify this would
# wrongly close → violating H4. This proves the gate runs unconditionally in dispatch_decision.
s2, sb2, nd2 = fresh_sandbox()
it2 = s2.surface_build_intent("touch the canvas surface (loop path)", scope=["canvas/"],
                              consequence_class="decision_build")
sid2 = it2["id"]; seq2 = approve_seq(s2, sid2)
out2 = s2.dispatch_decision(
    sid2, seq2,
    launcher=lambda d, *, repo: {"finished": True, "success": True, "exit_code": 0,
                                 "summary": "ui change", "changed_files": ["canvas/app/src/App.tsx"],
                                 "permission_mode": "acceptEdits"},
    verifier=lambda r: (True, "scenario passed"))            # INJECTED passing verifier (the loop path)
check("a surface build with an injected PASSING verifier STILL does NOT auto-close (FORM is structural)",
      not out2.get("closed") and out2.get("form_unverifiable") and s2.inbox.get(sid2)["status"] != "implemented")
check("the injected-verifier surface build also surfaced a DISPATCHER-INERT form item",
      s2.is_build_intent(s2.inbox.get(out2["requeued"])) is False)


print("\n=== H5 — the adversarial CRITIC is first-class + SEPARATE from the builder's self-report ===")
# default critic: a 'success' with an EMPTY change-set is a no-op masquerading as done → critic vetoes.
ok, why = Suite._default_critic({}, {"success": True, "changed_files": []})
check("default critic VETOES success-with-empty-changeset (no-op is not a build)", ok is False)
ok, why = Suite._default_critic({}, {"success": True, "changed_files": ["nodes/x.py"]})
check("default critic PASSES a consequential build (success + non-empty change-set)", ok is True)
# an INJECTED critic can veto independently of the builder's self-reported success (the adversary).
s, sandbox, nodes = fresh_sandbox()
intent = s.surface_build_intent("a build the critic rejects", scope=["nodes/"],
                                consequence_class="decision_build")
sid = intent["id"]; seq = approve_seq(s, sid)
out = s.dispatch_decision(sid, seq, launcher=node_launch(sandbox, nodes, "n4"),
                          suite_runner=in_process_drift_runner(s),
                          critic=lambda d, r: (False, "critic: adversarial re-check rejected this build"))
check("an injected critic that vetoes blocks the close (critic is first-class in verify) (H5)",
      not out.get("closed") and "critic" in (out.get("reason", "")))
check("the critic veto surfaced back (H6)", bool(out.get("requeued")))


print("\n=== H8 — a node build that ALSO edits MAP.md/STATE.md (per H7) is NOT a scope overrun ===")
s, sandbox, nodes = fresh_sandbox()
intent = s.surface_build_intent("add a node + update the self-description", scope=["nodes/"],
                                consequence_class="decision_build")
sid = intent["id"]; seq = approve_seq(s, sid)
# the build changes nodes/n5.py (in scope) AND MAP.md + STATE.md (H7 upkeep — must NOT read as overrun).
out = s.dispatch_decision(
    sid, seq,
    launcher=node_launch(sandbox, nodes, "n5",
                         changed=["nodes/n5.py", "MAP.md", "STATE.md"]),
    suite_runner=in_process_drift_runner(s))
check("a node build that also edits MAP.md/STATE.md CLOSES (H8: self-description is upkeep, not overrun)",
      out.get("closed") and not out.get("overrun"))
# the H8 helper is exact: root self-description files allowed; a module's own AGENTS.md is NOT blanket-allowed.
check("H8 helper: MAP.md / STATE.md / AGENTS.md at root are self-description (allowed)",
      all(Suite._is_self_description(p) for p in ("MAP.md", "STATE.md", "AGENTS.md")))
check("H8 helper: a module file is NOT blanket self-description (must be in declared scope)",
      Suite._is_self_description("nodes/evil.py") is False
      and Suite._is_self_description("nodes/AGENTS.md") is False)
# and a genuine overrun OUTSIDE both scope and the self-description allow-set still surfaces back.
s2, sb2, nd2 = fresh_sandbox()
it2 = s2.surface_build_intent("stay in nodes/", scope=["nodes/"], consequence_class="decision_build")
sid2 = it2["id"]; seq2 = approve_seq(s2, sid2)
out2 = s2.dispatch_decision(
    sid2, seq2,
    launcher=node_launch(sb2, nd2, "n6", changed=["nodes/n6.py", "runtime/sneaky.py"]),
    suite_runner=in_process_drift_runner(s2))
check("a genuine overrun (runtime/sneaky.py outside nodes/ scope) STILL surfaces back (H8 didn't widen)",
      not out2.get("closed") and out2.get("overrun") == ["runtime/sneaky.py"])


print("\n=== H6 / reverse incident — a build that breaks the REGISTRY (a broken node) surfaces back ===")
s, sandbox, nodes = fresh_sandbox()
intent = s.surface_build_intent("a build that writes a broken node", scope=["nodes/"],
                                consequence_class="decision_build")
sid = intent["id"]; seq = approve_seq(s, sid)
def broken_node_launch(decision, *, repo):
    with open(os.path.join(nodes, "broken.py"), "w") as f:
        f.write("def run(inputs, config):\n    return {}\nthis is not valid python !!!\n")
    return {"finished": True, "success": True, "exit_code": 0, "summary": "oops",
            "changed_files": ["nodes/broken.py"], "permission_mode": "acceptEdits"}
out = s.dispatch_decision(sid, seq, launcher=broken_node_launch,
                          suite_runner=in_process_drift_runner(s))
check("a build that breaks the registry (un-loadable node) does NOT close (H6)",
      not out.get("closed") and s.inbox.get(sid)["status"] != "implemented")
check("the broken-registry build surfaced back with a reason (fail loud, no silent close)",
      bool(out.get("requeued")))


print("\n=== operator-only resolve preserved (the wire writes status, never `resolved`) ===")
s, sandbox, nodes = fresh_sandbox()
intent = s.surface_build_intent("verify operator-only", scope=["nodes/"],
                                consequence_class="decision_build")
sid = intent["id"]; seq = approve_seq(s, sid)
out = s.dispatch_decision(sid, seq, launcher=node_launch(sandbox, nodes, "n7"),
                          suite_runner=in_process_drift_runner(s))
check("the operator `resolved` field was written ONLY by the operator approve (code wrote `status`)",
      s.inbox.get(sid)["resolved"] == "approve" and s.inbox.get(sid)["status"] == "implemented")


print(f"\nALL {PASS} CHECKS PASS — WIRE-HARDEN: the wire's definition-of-done == the loop's discipline. "
      f"A build that breaks a suite / leaves drift red / breaks the registry / touches a surface / "
      f"fails the critic does NOT close — it surfaces back (H1·H2·H4·H5·H6). A node build is made LIVE "
      f"(H3) + leaves the self-description refreshed and drift GREEN (H2 — the reverse incident fixed, "
      f"proven load-bearing). The standard rides build_instruction (H7) + the self-description regen is "
      f"upkeep, not overrun (H8). Operator-only resolve preserved; no confidence value anywhere.")
