"""tests/walkthrough_acceptance.py — the RHM walkthrough/review organ end-to-end (T2-RHM-COVERAGE).

The review organ had ZERO automated coverage: no committed suite exercised the session lifecycle
(start_session / present_current / next / respond / session_status, suite.py ~998-1124), the `ui://`
component resolver (build_ui_info, suite.py ~1779), or the governance that holds it (operator-only resolve;
a recorded verdict cannot be contradicted). The "8/8 adversarial verified" was by-use only, never codified.
This suite drives the REAL Suite (no mocks) and asserts:

  1. LIFECYCLE — a session compiles to a Graph run by the existing scheduler, operator-paced: present_current
     names the cursor item + carries the `ui://review/{id}` target; next() turns exactly one page (cursor
     advances by one, the step's gate opens, the run fires the opened step), and runs idempotently past the
     end (done). session_status reflects cursor/opened/done. (Deterministic fields only — `framing` comes
     from a live LLM via coa(), with a raw-payload fail-safe, so it is treated best-effort, never asserted.)
  2. THE ui:// RESOLVER — build_ui_info serializes the UI-component registry into the addressable map the
     `show` verb / frontend resolve `ui://<kind>/<ref>` against (chrome handles + the canvas camera ref).
  3. GOVERNANCE (the no-bypass guarantees):
       - a recorded terminal verdict CANNOT be contradicted — a second terminal resolve REFUSES (GovernanceError);
       - code can NEVER write the operator `resolved` field — advancing the lifecycle STATUS lane
         (inbox→presented→responded→implemented) leaves `resolved` None throughout; only the operator-only
         resolve_surfaced flips it; and resolve_surfaced is NOT on the MCP face (the agent cannot self-approve).

Run: ./.venv/bin/python tests/walkthrough_acceptance.py
"""
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
from runtime.governance import GovernanceError

NODES = os.path.join(ROOT, "nodes")
PASS = 0
ok = True


def check(label, cond):
    global PASS, ok
    ok &= bool(cond)
    if cond:
        PASS += 1
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")


def main():
    store_dir = tempfile.mkdtemp(prefix="walkthrough-acc-")
    try:
        store = FsStore(os.path.join(store_dir, "store"))
        reg = NodeRegistry(); reg.discover([NODES])
        suite = Suite(store, reg, nodes_dir=NODES)

        # --- seed: three real review items in the inbox (the operator's queue) ---
        r1 = suite.surface_review({"title": "first item", "kind": "idea"}, origin="generative")
        r2 = suite.surface_review({"title": "second item", "kind": "idea"}, origin="generative")
        r3 = suite.surface_review({"title": "third item", "kind": "idea"}, origin="generative")
        item_ids = [r1["id"], r2["id"], r3["id"]]
        check("surface_review lands items as live escalations (resolved is None)",
              all(suite.inbox.get(i).get("resolved") is None for i in item_ids))

        # =========================== 1. LIFECYCLE ===========================
        started = suite.start_session(item_ids, mode="walkthrough")   # returns present_current of cursor 0
        sid = started["session"]
        check("start_session returns a session id", isinstance(sid, str) and sid)
        check("start_session presents the FIRST item (cursor 0)",
              started.get("cursor") == 0 and started.get("item") == r1["id"])
        check("present target is the registry-addressed ui://review/{id}",
              started.get("ui_target") == f"ui://review/{r1['id']}")
        check("start_session reports the total item count", started.get("total") == 3)
        # a fail-safe item: framing may be None (LLM down) OR a string (LLM up) — best-effort, never block
        check("the presentation carries a framing slot (None or str — best-effort, never blocks the walk)",
              ("framing" in started) and (started["framing"] is None or isinstance(started["framing"], str)))

        # session_status mirrors the live walk
        st0 = suite.session_status(sid)
        check("session_status: cursor 0, total 3, mode walkthrough, not done",
              st0["cursor"] == 0 and st0["total"] == 3 and st0["mode"] == "walkthrough" and st0["done"] is False)

        # present_current is idempotent / re-readable without advancing
        pc = suite.present_current(sid)
        check("present_current re-reads the SAME current item (does not advance)",
              pc.get("item") == r1["id"] and suite.session_status(sid)["cursor"] == 0)

        # NEXT turns exactly one page: cursor 0 → 1, step0 fires, step1 still gated
        nx1 = suite.next(sid)
        st1 = suite.session_status(sid)
        check("next() advanced the cursor by exactly one (0 → 1)", st1["cursor"] == 1)
        check("next() recorded step 0 as opened", 0 in st1["opened"])
        check("next() presents the SECOND item", nx1.get("item") == r2["id"])
        # the opened step actually FIRED through the scheduler (its go-gate was written + the step ran)
        check("the opened step 0 fired through the scheduler (its output address resolved)",
              store.head(f"run://review-{sid}/step0") is not None)
        check("the NEXT step's gate is still CLOSED (step1 not yet fired — operator-paced)",
              store.head(f"run://review-{sid}/step1") is None)

        # respond() — record the operator's verdict for the CURRENT step (cursor 1 → r2), tagged to the
        # walk (session_id + position). This is the half of C-WALK resolve_surfaced alone doesn't give:
        # respond targets the cursor item and stamps the session/position onto the verdict + resolve event.
        resp = suite.respond(sid, "approve", reason="second item looks right")
        check("respond() records a terminal verdict for the CURRENT cursor item (r2 → approve)",
              resp["resolved"] is True and suite.inbox.get(r2["id"]).get("resolved") == "approve")
        check("respond() stamps the session id onto the verdict (tagged to the walk)",
              suite.inbox.get(r2["id"]).get("session_id") == sid)
        check("respond() stamps the cursor position onto the verdict (position 1)",
              suite.inbox.get(r2["id"]).get("position") == 1)
        check("respond() does NOT advance the cursor (next() does that)",
              suite.session_status(sid)["cursor"] == 1)

        # walk to the end
        suite.next(sid)   # → cursor 2 (step1 fires)
        end = suite.next(sid)   # → cursor 3, done
        check("walking past the last item marks the session done", end.get("done") is True)
        check("session_status reports done with cursor at total",
              suite.session_status(sid)["done"] is True and suite.session_status(sid)["cursor"] == 3)
        # idempotent past the end (no crash, no over-advance)
        again = suite.next(sid)
        check("next() past the end is idempotent (still done, cursor unchanged)",
              again.get("done") is True and suite.session_status(sid)["cursor"] == 3)

        # =========================== 2. THE ui:// RESOLVER ===========================
        ui = suite.build_ui_info()
        check("build_ui_info returns the UI-component registry map (a non-empty dict)",
              isinstance(ui, dict) and len(ui) > 0)
        check("the resolver carries the chrome regions the walk points at (inbox, chat, activity)",
              all(k in ui for k in ("inbox", "chat", "activity")))
        check("a chrome entry resolves via a DOM handle (domHandle present on inbox)",
              ui["inbox"].get("domHandle") == "inbox" and ui["inbox"]["kind"] == "chrome")
        check("the node canvas entry resolves via a camera ref",
              ui["*"].get("cameraRef") == "*" and ui["*"]["kind"] == "canvas")
        check("capabilities are serialized per component (inbox is spotlit + openable)",
              ui["inbox"]["capabilities"]["spotlit"] is True and ui["inbox"]["capabilities"]["openable"] is True)

        # =========================== 3. GOVERNANCE ===========================
        # (a) operator-only resolve via the STATUS lane: advancing status NEVER writes `resolved`.
        item = r1["id"]
        check("a fresh review item has resolved = None", suite.inbox.get(item).get("resolved") is None)
        for status in ("presented", "responded", "implemented"):
            suite.inbox.set_status(item, status)
            check(f"after set_status({status!r}) the operator `resolved` field is STILL None (code can't write it)",
                  suite.inbox.get(item).get("resolved") is None)
        check("the status lane moved while resolved stayed None (separate lifecycle)",
              suite.inbox.get(item).get("status") == "implemented"
              and suite.inbox.get(item).get("resolved") is None)

        # (b) ONLY the operator-only resolve_surfaced writes `resolved`.
        v = suite.resolve_surfaced(item, "approve", reason="looks right")
        check("resolve_surfaced('approve') is what finally writes resolved=approve",
              v["resolved"] is True and suite.inbox.get(item).get("resolved") == "approve")

        # (c) a recorded terminal verdict CANNOT be contradicted — a second terminal resolve REFUSES.
        refused = False
        try:
            suite.resolve_surfaced(item, "reject", reason="changed my mind")
        except GovernanceError:
            refused = True
        check("a forged/contradictory SECOND terminal verdict is REFUSED (GovernanceError)", refused)
        check("the original verdict is intact after the refused contradiction (still approve)",
              suite.inbox.get(item).get("resolved") == "approve")

        # (d) operator-only: resolve_surfaced is NOT exposed on the MCP (agent) face — it can't self-approve.
        import mcp_face.server as mcp_server
        src = open(mcp_server.__file__, encoding="utf-8").read()
        check("resolve_surfaced is NOT callable from the MCP face (agent cannot self-approve)",
              "self.suite.resolve_surfaced(" not in src and "suite.resolve_surfaced(" not in src)

        print("\n" + (f"ALL {PASS} CHECKS PASS — RHM walkthrough organ: lifecycle + ui:// resolver + no-bypass governance"
                      if ok else "WALKTHROUGH ACCEPTANCE FAILED"))
        return 0 if ok else 1
    finally:
        shutil.rmtree(store_dir, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
