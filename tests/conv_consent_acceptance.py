"""tests/conv_consent_acceptance.py — Convergence X5 · CONSENT-TIME RESOLUTION (the trust property).

THE PRINCIPLE (Completion Criteria X5 / Implementation Guide X5):
  The launch context is resolved at MINT/approve time (X3 gathers it, X1/X2 the address+symbols) and
  PERSISTED into the build-intent's payload. The launched build must compose from that SAME persisted
  bundle and NEVER re-resolve a fresh one at launch. So the record the operator approved == EXACTLY
  what the build's prompt sees. The operator consents WITH the context in hand; the build cannot
  resolve a different context behind them. This is the load-bearing trust property after the
  unsupervised-fire scare: surfaced == launched.

WHY IT ALREADY HOLDS (X3 + X4), proven structurally before this test asserts it:
  • MINT (suite.surface_intent_at): resolve_scope (X1/X2) + _r2_gather→_r2_score_and_cap (X3) run ONCE,
    at consent time, and thread address/symbols/context INTO the payload, persisted via
    surface_build_intent → inbox.surface → store.save_surfaced (to disk).
  • DISPATCH (suite.dispatch_decision): d = self.inbox.get(sid) → store.get_surfaced(sid) RELOADS the
    persisted record FROM DISK; launch(d) is called with THAT record. No _r2_gather / resolve_scope /
    embed anywhere in the dispatch→launch path.
  • COMPOSE (implement.build_instruction): a PURE decision-in→string-out formatter that reads ONLY
    decision["payload"] (X4). It does not gather/embed/re-resolve.
  So the context the build composes from IS the persisted bundle resolved at mint — never a fresh one.

X5 makes that property EXPLICIT, ENFORCED (this named test is the regression lock), and PROVEN.
  NO enforcement guard was needed inside dispatch/launch mechanics — the task forbids changing the
  dispatch mechanics, and the property is already structural (X3 persists at mint; X4 composes pure
  from the persisted payload; dispatch reloads from disk). This test PROVES it and GUARDS it: if a
  future change made the launch path re-resolve (a fresh gather/scope at dispatch), the mutation proof
  below goes RED.

PROOF MODEL:
  • SURFACED == LAUNCHED (the unit) — drive dispatch_decision with a MOCKED launcher that CAPTURES the
    decision it WOULD run claude -p on (it NEVER spawns a subprocess — it records + raises a sentinel).
    Assert the captured decision's payload["context"] == the SURFACED record's payload["context"]
    (identical list), and that build_instruction(captured) CONTAINS each surfaced item's text. The
    build saw exactly what was approved.
  • CONSENT-TIME FREEZING (the key property) — mutate the LIVE attached context AFTER mint+approve
    (attach a NEW comment B). A POSITIVE CONTROL proves the live notebook genuinely moved on: a fresh
    _r2_gather→cap at the address NOW contains B. THEN dispatch → assert the launched bundle is STILL
    the mint-time bundle (== [A]) and B's text is ABSENT from the composed prompt. The pair (B would be
    gathered if re-resolved, yet the build does not see it) is what proves resolve-at-consent, not
    at-launch — "B absent" alone false-passes without the positive control.
  • RETRIEVABLE FOR THE APPROVAL SURFACE (X5 function half) — inbox.get(sid)["payload"]["context"]
    carries the resolved bundle, readable via the existing inbox read path, so the (needs-tim) visual
    approval surface has the data to show the operator the context they are consenting to.
  • PRESERVE (the wire's governed path + DENY-ALL) — the three-part bind still gates dispatch (a forged
    seq refuses); an empty-scope build-intent is DENY-ALL (refused, never builds anywhere). Unchanged.

NO real claude -p / subprocess EVER spawned (HARD LAW): the launcher is MOCKED and short-circuits via a
  sentinel raised at capture (before any verify/refresh path), so dispatch_decision never reaches a real
  launch and never reaches _make_live_and_refresh (which is why MAP.md stays clean — no git checkout).

Run: /home/tim/company/.venv/bin/python tests/conv_consent_acceptance.py
"""
import os
import sys
import faulthandler
import tempfile

# faulthandler hang-guard (HARD LAW companion): if anything in this path blocked on a real subprocess
# (it must NOT — the launcher is mocked), dump every thread + abort, never hang the loop silently.
faulthandler.dump_traceback_later(60, exit=True)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ["COMPANY_TEST_RUN"] = "1"

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
from runtime import implement as impl
from runtime.implement import build_instruction
from runtime.governance import GovernanceError

PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def raises(label, fn, exc=Exception):
    global PASS
    try:
        fn()
    except exc:
        PASS += 1
        print(f"  ok  {label}")
        return
    raise AssertionError(f"FAIL: {label} — expected {exc.__name__}, none raised")


NODES = os.path.join(ROOT, "nodes")


def fresh_suite():
    store_root = os.path.join(tempfile.mkdtemp(prefix="conv-consent-"), "store")
    store = FsStore(store_root)
    reg = NodeRegistry(); reg.discover([NODES])
    s = Suite(store, reg, nodes_dir=NODES)
    # STUB the verify-by-suites runner — exactly as the launch is mocked. We short-circuit at launch
    # (the sentinel below), so verify is never reached; this stub is belt-and-braces so NO real suite
    # subprocess can ever spawn even if the short-circuit pattern changed.
    s._default_suite_runner = lambda suite: (True, "stubbed (consent-time test; no real verify)")
    return s, reg, store_root


# A launch RECORDER (the MOCKED launcher — HARD LAW: NEVER a real claude -p). It CAPTURES the decision
# dispatch_decision passes to launch (the EXACT record the build would compose its prompt from), then
# SHORT-CIRCUITS by raising a non-LaunchError sentinel. dispatch_decision only catches _impl.LaunchError,
# so the sentinel propagates out — proving launch was REACHED with the persisted decision WITHOUT any
# subprocess AND without reaching the verify/_make_live_and_refresh path (so MAP.md stays clean).
class _LaunchReached(Exception):
    pass


def make_capturing_launcher():
    captured = {}

    def fake_launch(decision, *, repo):
        captured["decision"] = decision
        captured["repo"] = repo
        # ALSO compose the prompt the build WOULD receive — from the captured decision ONLY (the same
        # pure path the real launch uses: build_instruction(decision)). This is what the build sees.
        captured["instruction"] = build_instruction(decision)
        raise _LaunchReached("launch reached (recorded) — short-circuit, NO real subprocess")

    return captured, fake_launch


def approve_seq(suite, sid):
    """Operator approves (operator-only resolve) → return the resolve event's unique seq for the bind."""
    suite.resolve_surfaced(sid, "approve", reason="authorize this build (consent-time test)")
    return next(e["seq"] for e in reversed(suite.store.events_since(-1))
               if e.get("kind") == "resolve" and e.get("surfaced") == sid)


def drive_capture(suite, sid, seq):
    """Drive dispatch_decision with the mocked capturing launcher; return the captured launch payload.
    The sentinel is expected (it short-circuits before any real launch/verify). NO subprocess spawns."""
    captured, fake_launch = make_capturing_launcher()
    try:
        suite.dispatch_decision(sid, seq, launcher=fake_launch,
                                verifier=lambda r: (True, "verified (unreached — sentinel short-circuit)"))
    except _LaunchReached:
        pass
    return captured


# A real, live corpus address with attachable context (same fixture conv_context uses).
CHATIN = "ui://chat/input"   # → symbols=['code://App'], scope=['canvas/app/src/App.tsx']


# ════════════════════════════════════════════════════════════════════════════════════════════════
print("\n=== SANITY — the corpus address resolves (X1/X2 ground truth for the persisted bundle) ===")
# ════════════════════════════════════════════════════════════════════════════════════════════════
s, reg, store_root = fresh_suite()
rs = s.resolve_scope(CHATIN)
check(f"{CHATIN} resolves a real scope (S3 corpus): scope non-empty (build is NOT DENY-ALL)",
      bool(rs.get("scope")))


# ════════════════════════════════════════════════════════════════════════════════════════════════
print("\n=== 1 — SURFACED == LAUNCHED: the build composes from the EXACT persisted-at-mint bundle ===")
# ════════════════════════════════════════════════════════════════════════════════════════════════
# Pre-attach a notebook item A at the address BEFORE mint — the accumulated context the operator will
# see + approve, and the build must inherit verbatim.
CTX_A = "context-A: the run button has felt sluggish since last week — the accumulated notebook note"
s.annotate(CHATIN, CTX_A, source="operator")

MINT_COMMENT = "context-mint: this run button is too loud — tone it down"
out = s.surface_intent_at(CHATIN, MINT_COMMENT, source="operator",
                          consequence_class="decision_build")   # AUTO posture → dispatch_decision accepts
sid = out["id"]

# The SURFACED record == what the operator approves WITH. Read it back via the existing inbox read path
# (a fresh Suite on the same store proves it is on DISK, not an in-memory artifact).
s_reload, _, _ = (Suite(FsStore(store_root), reg, nodes_dir=NODES), None, None)
surfaced = s_reload.inbox.get(sid)
check("the surfaced build-intent persists + reloads from disk (a fresh Suite, same store)",
      surfaced is not None and Suite.is_build_intent(surfaced))
surfaced_ctx = surfaced["payload"].get("context")
check("the SURFACED record carries a resolved context bundle (a list — what the operator approves)",
      isinstance(surfaced_ctx, list) and len(surfaced_ctx) > 0)
surfaced_text = "\n".join((it.get("text", "") or "") for it in surfaced_ctx)
check("the surfaced bundle includes the pre-attached note A (the notebook the operator consents to)",
      CTX_A in surfaced_text)

# X5 FUNCTION HALF (retrievable for the approval surface): the resolved context is readable via the
# SAME inbox read path the (needs-tim) visual approval surface will use — the data is there to show.
approval_view = s.inbox.get(sid)["payload"].get("context")
check("X5 RETRIEVABLE: inbox.get(sid).payload.context carries the bundle for the approval surface",
      isinstance(approval_view, list) and approval_view == surfaced_ctx)

# Operator approves WITH that context in hand → governed bind.
seq = approve_seq(s, sid)

# Drive dispatch with the MOCKED launcher → capture the EXACT decision the build composes from.
captured = drive_capture(s, sid, seq)
check("launch was REACHED with a decision (mocked launcher captured it; NO real subprocess spawned)",
      "decision" in captured)
launched = captured["decision"]
check("the launched decision IS the operator-approved build-intent (right item, by id)",
      launched.get("id") == sid)

launched_ctx = (launched.get("payload") or {}).get("context")
# THE UNIT — surfaced == launched: the build's context bundle is IDENTICAL to the approved one.
check("X5 SURFACED == LAUNCHED: launched payload.context == surfaced payload.context (IDENTICAL list)",
      launched_ctx == surfaced_ctx)

# And the COMPOSED PROMPT the build receives contains each surfaced item's text (the build sees it).
instr = captured["instruction"]
check("the composed prompt the build receives is derivable from the persisted record alone (a str)",
      isinstance(instr, str) and len(instr) > 0)
for it in surfaced_ctx:
    t = (it.get("text") or "")
    if t:
        check(f"the build's prompt CONTAINS the approved context item: {t[:40]!r}…", t in instr)
check("the build's prompt contains the mint comment the operator approved", MINT_COMMENT in instr)


# ════════════════════════════════════════════════════════════════════════════════════════════════
print("\n=== 2 — CONSENT-TIME FREEZING: a POST-mint mutation does NOT reach the build (the key proof) ===")
# ════════════════════════════════════════════════════════════════════════════════════════════════
# Fresh suite (clean event log → a clean exactly-once + bind for this case).
s2, reg2, root2 = fresh_suite()
CTX_A2 = "context-A2: the ORIGINAL accumulated note present at consent time"
s2.annotate(CHATIN, CTX_A2, source="operator")
MINT2 = "context-mint2: make the header calmer"
out2 = s2.surface_intent_at(CHATIN, MINT2, source="operator", consequence_class="decision_build")
sid2 = out2["id"]
frozen_ctx = s2.inbox.get(sid2)["payload"].get("context")
frozen_text = "\n".join((it.get("text", "") or "") for it in frozen_ctx)
check("mint-time bundle captured (the frozen consent bundle, includes A2)", CTX_A2 in frozen_text)

# Operator approves WITH the frozen bundle in hand.
seq2 = approve_seq(s2, sid2)

# NOW MUTATE THE LIVE ATTACHED CONTEXT — attach a NEW comment B AFTER mint + approve.
CTX_B = "context-B: a NEW comment added AFTER the operator already approved — must NOT reach the build"
s2.annotate(CHATIN, CTX_B, source="operator")

# POSITIVE CONTROL (without it, "B absent" is meaningless — maybe B was never gatherable). Prove the
# LIVE notebook genuinely moved on: a FRESH gather→cap at the address NOW contains B. So IF the launch
# path re-resolved, the build WOULD see B. The proof is that it does NOT.
from datetime import datetime as _dt, timezone as _tz
live_now = s2._r2_score_and_cap(s2._r2_gather(CHATIN), CHATIN, _dt.now(_tz.utc))
live_now_text = "\n".join((it.get("text", "") or "") for it in live_now)
check("POSITIVE CONTROL: a FRESH gather at the address NOW contains B (the live notebook moved on)",
      CTX_B in live_now_text)
check("POSITIVE CONTROL: the persisted frozen bundle does NOT contain B (it was resolved BEFORE B)",
      CTX_B not in frozen_text)

# Dispatch → capture what the build composes from.
captured2 = drive_capture(s2, sid2, seq2)
launched2 = captured2["decision"]
launched2_ctx = (launched2.get("payload") or {}).get("context")

# THE KEY PROOF — the build STILL sees the mint-time bundle, NOT the post-approval addition B.
check("X5 KEY PROOF: launched payload.context == the FROZEN mint-time bundle (NOT re-resolved at launch)",
      launched2_ctx == frozen_ctx)
instr2 = captured2["instruction"]
check("X5 KEY PROOF: B is ABSENT from the build's composed prompt (resolve-at-consent, not at-launch)",
      CTX_B not in instr2)
check("X5 KEY PROOF: the build's prompt STILL contains the consent-time note A2 (the frozen context)",
      CTX_A2 in instr2)
# The pair is the proof: B WOULD be gathered if re-resolved (positive control) yet the build does NOT
# see it → the launch composed from the persisted-at-consent bundle, never a fresh resolution. If a
# future change re-resolved at launch, this goes RED.


# ════════════════════════════════════════════════════════════════════════════════════════════════
print("\n=== 3 — NO RE-RESOLUTION AT LAUNCH (structural confirmation: the launch path is pure) ===")
# ════════════════════════════════════════════════════════════════════════════════════════════════
# Confirm the composer that the launch path uses is a PURE function of the decision — re-composing from
# the captured decision ALONE reproduces the build's prompt byte-for-byte (no suite/address/network in
# the loop). This is X4's pure boundary, which IS X5's enforcement: the build can ONLY see the payload.
recomposed = build_instruction(launched2)
check("build_instruction(launched_decision) is reproducible from the decision ALONE (pure → byte-for-byte)",
      recomposed == instr2)
# And source-level: the launch path (launch → build_instruction) contains NO re-resolution calls.
launch_src = (impl.launch.__doc__ or "") + "\n" + (build_instruction.__doc__ or "")
import inspect as _inspect
launch_code = _inspect.getsource(impl.launch) + "\n" + _inspect.getsource(build_instruction)
check("the launch path source contains NO _r2_gather (no attached-context re-resolution at launch)",
      "_r2_gather" not in launch_code)
check("the launch path source contains NO resolve_scope (no scope/symbol re-resolution at launch)",
      "resolve_scope" not in launch_code)


# ════════════════════════════════════════════════════════════════════════════════════════════════
print("\n=== 4 — PRESERVE: the wire's governed path + DENY-ALL unchanged ===")
# ════════════════════════════════════════════════════════════════════════════════════════════════
s3, reg3, root3 = fresh_suite()
# the three-part bind still gates dispatch: a forged seq refuses (governed path preserved).
intent3 = s3.surface_build_intent("a guarded build", scope=["runtime/"], consequence_class="decision_build")
sid3 = intent3["id"]
raises("PRESERVE governed path: a forged/missing resolve seq refuses dispatch (three-part bind)",
       lambda: s3.dispatch_decision(sid3, 999999, launcher=make_capturing_launcher()[1]),
       exc=GovernanceError)

# DENY-ALL: an empty-scope build-intent never builds anywhere (surface_intent_at folds the empty scope
# into a DENY-ALL build-intent; resolve_scope on a non-resolvable address yields empty scope).
ORPHAN = "ui://chrome/nonexistent-orphan-no-code"   # an address with no resolvable code scope
orphan_out = s3.surface_intent_at(ORPHAN, "an orphan comment with no code scope", source="operator",
                                  consequence_class="decision_build")
orphan_scope = s3.inbox.get(orphan_out["id"])["payload"].get("scope")
check("PRESERVE DENY-ALL: an orphan address mints with EMPTY scope (never builds anywhere — deny-all)",
      orphan_scope == [] or not orphan_scope)


# ════════════════════════════════════════════════════════════════════════════════════════════════
print("\n=== 4b — REAL FACE: the resolved context is retrievable over the operator HTTP face ===")
# ════════════════════════════════════════════════════════════════════════════════════════════════
# FUNCTION bar ('a real face calls the capability'): the (FORM=needs-tim) visual approval surface will
# read the surfaced build-intent over HTTP — so prove the resolved context bundle is retrievable via the
# EXISTING operator-face read route (GET /api/surfaced), not just the inbox METHOD. Spin the real
# runtime/bridge.py ThreadingHTTPServer against a TEMP store (point COMPANY_STORE + reload), drive the
# operator face: POST /api/annotate (attach the notebook note) → POST /api/intent-at (mint the
# build-intent at the address) → GET /api/surfaced (the approval-surface READ path) and assert the
# returned item carries payload.context including the attached note. This is a READ path: the launcher
# is NEVER invoked, acceptEdits is NEVER armed (no dispatch over the wire — surfacing only, exactly L1).
import importlib
import threading
import http.client
import json as _json
import fabric.config as _fcfg

_FACE_STORE = os.path.join(tempfile.mkdtemp(prefix="conv-consent-face-"), "store")
_prev_store = os.environ.get("COMPANY_STORE")
os.environ["COMPANY_STORE"] = _FACE_STORE
os.environ.pop("COMPANY_WIRE_PERMISSION", None)   # belt-and-braces: the wire stays SAFE-BY-DEFAULT
importlib.reload(_fcfg)                            # re-read COMPANY_STORE into fcfg.STORE_DIR
import runtime.bridge as _bridge
importlib.reload(_bridge)                          # rebuild bridge.SUITE on the temp store
httpd = _bridge.ThreadingHTTPServer(("127.0.0.1", 0), _bridge.H)   # ephemeral port
_port = httpd.server_address[1]
_t = threading.Thread(target=httpd.serve_forever, daemon=True)
_t.start()
try:
    FACE_NOTE = "face-context: the operator's accumulated note, must be readable over the wire"
    FACE_ADDR = "ui://chat/input"

    def _post(p, body):
        c = http.client.HTTPConnection("127.0.0.1", _port, timeout=20)
        c.request("POST", p, _json.dumps(body), {"Content-Type": "application/json"})
        r = c.getresponse(); data = r.read(); c.close()
        return r.status, (_json.loads(data) if data else None)

    def _get(p):
        c = http.client.HTTPConnection("127.0.0.1", _port, timeout=20)
        c.request("GET", p)
        r = c.getresponse(); data = r.read(); c.close()
        return r.status, (_json.loads(data) if data else None)

    st, _ = _post("/api/annotate", {"address": FACE_ADDR, "text": FACE_NOTE, "source": "operator"})
    check("REAL FACE: POST /api/annotate attached the note over HTTP (200)", st == 200)
    st, minted = _post("/api/intent-at", {"address": FACE_ADDR,
                                          "text": "face-mint: tone the run button down",
                                          "source": "operator", "consequence_class": "decision_build"})
    check("REAL FACE: POST /api/intent-at minted a build-intent over HTTP (200, surfacing-only)",
          st == 200 and isinstance(minted, dict) and minted.get("id"))
    face_sid = minted["id"]
    # the approval-surface READ path — the existing operator-face GET that lists surfaced items.
    st, surfaced_list = _get("/api/surfaced")
    check("REAL FACE: GET /api/surfaced returned the surfaced items (the approval-surface read path, 200)",
          st == 200 and isinstance(surfaced_list, list))
    face_item = next((d for d in surfaced_list if d.get("id") == face_sid), None)
    check("REAL FACE: the minted build-intent is retrievable over the operator face (by id)",
          face_item is not None)
    face_ctx = (face_item.get("payload") or {}).get("context")
    check("X5 RETRIEVABLE (real face): the surfaced item's payload.context is a list, readable over HTTP",
          isinstance(face_ctx, list) and len(face_ctx) > 0)
    face_text = "\n".join((it.get("text", "") or "") for it in face_ctx)
    check("X5 RETRIEVABLE (real face): the bundle the operator reads over HTTP includes the attached note",
          FACE_NOTE in face_text)
    # the approval-surface reads the SAME resolved-at-consent bundle the build will compose from
    # (surfaced == launched, now confirmed end-to-end through the operator's actual read face).
    check("REAL FACE: the build-intent surfaced with resolved=None (operator-only approve still pending)",
          face_item.get("resolved") is None)
finally:
    httpd.shutdown(); httpd.server_close()
    # restore the store env + reload config back to the default (leave no global side-effect).
    if _prev_store is None:
        os.environ.pop("COMPANY_STORE", None)
    else:
        os.environ["COMPANY_STORE"] = _prev_store
    importlib.reload(_fcfg)


# ════════════════════════════════════════════════════════════════════════════════════════════════
print("\n=== 5 — NO autonomous spawn ANYWHERE in this test (HARD LAW) ===")
# ════════════════════════════════════════════════════════════════════════════════════════════════
# The launcher was MOCKED in every drive (make_capturing_launcher → fake_launch, which records + raises
# the _LaunchReached sentinel and NEVER spawns). Prove it behaviorally: a fresh capturing launcher,
# called directly the way dispatch_decision calls it, raises the sentinel WITHOUT invoking the real
# round-trip (no subprocess, no claude binary). We do NOT string-grep this file's own source — its
# docstring legitimately *names* what it avoids (subprocess/claude/acceptEdits) in prose.
_probe_captured, _probe_launch = make_capturing_launcher()
raises("the mocked launcher short-circuits via the sentinel (NEVER reaches a real claude -p)",
       lambda: _probe_launch({"id": "probe", "payload": {"spec": "probe", "scope": ["runtime/"]}}, repo=ROOT),
       exc=_LaunchReached)
check("the mocked launcher captured + composed PURELY (build_instruction on the decision; no subprocess)",
      isinstance(_probe_captured.get("instruction"), str))
# The env was never armed: the default posture stays 'plan' (we drove dispatch_decision DIRECTLY with an
# injected launcher, never the env-gated trigger — so acceptEdits/COMPANY_WIRE_PERMISSION were untouched).
check("the wire stays SAFE-BY-DEFAULT throughout (permission_mode() == 'plan'; acceptEdits never armed)",
      impl.permission_mode() == "plan" and impl.wire_armed() is False)


faulthandler.cancel_dump_traceback_later()
print(f"\nALL {PASS} CHECKS PASSED — conv_consent_acceptance (X5 · consent-time resolution / surfaced==launched)")
