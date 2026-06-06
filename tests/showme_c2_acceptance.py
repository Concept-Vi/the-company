"""tests/showme_c2_acceptance.py — C2 · TEACH-TO-REQUEST-CHANGE (the bootstrap).

WHAT C2 IS (the bootstrap that wires the operator into self-modifying the Company by sight):
The FIRST thing show-me teaches is HOW TO REQUEST A CHANGE AND APPROVE IT FROM INSIDE — the point→ask→
surface→approve loop. It is a NAMED GUIDED SEQUENCE (topic 'request-a-change' / 'self-modify') built
REUSE-ONLY on the C1 mechanism (start_guide / present_current's guide branch / next), NOT a parallel
walkthrough:

  • THE STEPPER — the SAME C1 guided-sequence organ over `ui://` ELEMENT addresses. The C2 sequence walks
    the REAL request-a-change elements: ui://toolbar/run (point), ui://canvas/wire-request (ask — the
    wire-door), ui://inbox (surface), ui://inbox (approve). Every address is a LIVE registry key
    (registry-is-truth filter), so each step has a RESOLVABLE per-step ui_target the FE spotlights (G-43).

  • THE TEACH NARRATION — the bootstrap's own teaching voice rides a PARALLEL side-channel (GUIDE_TEACH,
    positionally aligned), COMPOSED WITH the corpus how-to in present_current's guide branch (teach leads,
    the element's what_this_is grounds it). The session ITEMS stay address STRINGS (the organ keys on a
    ui:// string), so C1 stays byte-identical. MODEL-FREE by construction (the guide branch returns before
    coa — the tour reads the corpus + the teach side-channel, never a model).

  • THE INDICATE HINT — the wire-door (ui://canvas/wire-request) renders ONLY while a ui:// element is
    indicated (FE clickMode==='annotate'); so the 'point' step carries an INDICATE hint (GUIDE_INDICATE,
    side-channel) = ui://toolbar/run, which the FE indicates to MOUNT the door before spotlighting it.

  • SYSTEM/OPERATOR-STARTABLE — start_guide('request-a-change') is callable directly (this test calls it
    bare, no operator click; the bridge route /api/guide/start + the RHM + the toolbar "teach me to
    self-modify" control all start it).

WHAT THIS PROVES (by USE — real Suite, real corpus registry, real nodes/ registry, NO live model):
  A. start_guide('request-a-change') BINDS the organ over the registry-true point→ask→surface→approve
     element sequence (system-initiated, bare call) — and 'self-modify' is an alias for the same spine.
  B. each step NARRATES the flow leg (the teach side-channel) model-free, never empty, composed with the
     corpus what_this_is — AND carries a registry-VALID per-step ui_target (G-43, resolvable spotlight).
  C. the 'point' step carries the INDICATE hint (= the address that mounts the wire-door) so the FE can
     mount the hard-gated door before its spotlight; the later steps carry no indicate.
  D. the SAME next() advances the bootstrap end-to-end to done — MODEL-FREE (no model is ever called).
  E. FAIL LOUD — a guide topic that resolves to NO registered addresses returns organ_started:False + a
     reason (no silent no-op); a teach/indicate length mismatch on start_session RAISES (no silent misalign).
  F. REGRESSION — the C1 default tour (no teach/indicate) narrates byte-identical (corpus-only), the review
     organ is untouched, and the session record stays C1-shaped when teach/indicate are absent.

COMPANY_TEST_RUN is set for inbox-hygiene parity with the sibling suites.
"""
import os, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ["COMPANY_TEST_RUN"] = "1"

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite

NODES = os.path.join(ROOT, "nodes")
PASS = 0


def check(label, cond):
    global PASS
    if cond:
        PASS += 1
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}")
        raise SystemExit(1)


def fresh_suite():
    reg = NodeRegistry()
    reg.discover([NODES])
    return Suite(FsStore(tempfile.mkdtemp(prefix="c2-")), reg)


POINT = "ui://toolbar/run"           # the point step (also the indicate-target that mounts the wire-door)
ASK = "ui://canvas/wire-request"     # the request-a-change door (the heart of C2)
INBOX = "ui://inbox"                 # the surface + approve steps (always-mounted region)

print("C2 · TEACH-TO-REQUEST-CHANGE (the bootstrap: point → ask → surface → approve)")

# ── A · start_guide('request-a-change') BINDS the organ over the registry-true flow sequence ─────────
su = fresh_suite()
reg = su.build_ui_info()
seq = su._guide_sequence("request-a-change")
check("A0: the request-a-change sequence resolves to the 4-step point→ask→surface→approve element flow",
      seq == [POINT, ASK, INBOX, INBOX])
check("A0b: every step is a LIVE registry key (registry-is-truth — resolvable spotlight per step)",
      all(a in reg for a in seq))
check("A0c: the wire-door (the ASK heart of C2) IS in the flow (the request-a-change element)",
      ASK in seq)
check("A0d: 'self-modify' is an alias for the SAME bootstrap spine",
      su._guide_sequence("self-modify") == seq)

g = su.start_guide("request-a-change")                 # BARE call — system/operator-startable
check("A1: start_guide('request-a-change') BINDS the organ (organ_started:True, guide:True)",
      g.get("organ_started") is True and g.get("guide") is True)
check("A2: a real organ session id is returned (server-authoritative)",
      isinstance(g.get("session"), str) and g["session"])
check("A3: the organ presents the FIRST step (cursor 0, not done) — the 'point' step",
      g.get("cursor") == 0 and g.get("done") is False and g.get("item") == POINT)
check("A4: the dial is set to walkthrough (guide register) alongside the bootstrap start",
      g.get("mode") == "walkthrough" and su.get_mode() == "walkthrough")
check("A5: the steps are exactly the registry-filtered flow sequence",
      g.get("steps") == seq)
# the session items are address STRINGS (the organ keys on a ui:// string) — C1 shape preserved.
sess = su.store.load_session(g["session"])
check("A6: the session items are address STRINGS (the C1 organ shape — teach/indicate are side-channels)",
      sess.get("items") == seq and all(isinstance(i, str) for i in sess["items"]))
check("A6b: the teach + indicate side-channels persisted on the session, aligned to the items",
      isinstance(sess.get("teach"), list) and len(sess["teach"]) == 4
      and isinstance(sess.get("indicate"), list) and len(sess["indicate"]) == 4)

# ── B · each step narrates the flow (model-free, composed with corpus) + a registry-VALID ui_target ──
step0 = su.present_current(g["session"])
check("B1: step 0 (point) carries non-empty flow narration (the teach side-channel, model-free)",
      isinstance(step0.get("framing"), str) and len(step0["framing"]) > 40)
check("B2: step 0's narration teaches POINTING/requesting a change (the bootstrap's own voice, not bare what-this-is)",
      "point" in step0["framing"].lower() or "change the company" in step0["framing"].lower())
check("B3: G-43 — step 0's per-step raw.ui_target IS the registered element address (resolvable spotlight)",
      step0.get("raw", {}).get("ui_target") == POINT and POINT in reg)
check("B4: the step is marked a GUIDE step (the FE branches tour-vs-review on raw.guide_address)",
      step0["raw"].get("guide_address") == POINT and step0.get("guide") is True)
check("B5: the teach text rides raw.teach AND the composed framing leads with it (auto-enriches with corpus)",
      step0["raw"].get("teach") and step0["framing"].startswith(step0["raw"]["teach"]))

# ── C · the 'point' step carries the INDICATE hint that MOUNTS the wire-door; later steps do not ────
check("C1: step 0 (point) carries the INDICATE hint = the address the FE indicates to MOUNT the wire-door",
      step0["raw"].get("indicate") == POINT)
ask_step = su.next(g["session"])                       # advance to the ASK step (the wire-door)
check("C2: step 1 IS the wire-door (the ASK heart) with its own flow narration + resolvable ui_target",
      ask_step.get("item") == ASK and ask_step["raw"].get("ui_target") == ASK
      and isinstance(ask_step.get("framing"), str) and len(ask_step["framing"]) > 40)
check("C3: step 1 (ask) carries NO indicate hint (the door is already mounted by step 0's indication)",
      ask_step["raw"].get("indicate") is None)
check("C4: step 1's narration teaches the ASK (describe the change → a scoped build-intent)",
      "build-intent" in ask_step["framing"].lower() or "describe" in ask_step["framing"].lower())

# ── D · the SAME next() advances the bootstrap end-to-end to done — MODEL-FREE (no model ever called) ─
surf_step = su.next(g["session"])                      # the SURFACE step
check("D1: step 2 (surface) — the build-intent surfaces in the inbox (registry-valid, model-free narration)",
      surf_step.get("item") == INBOX and surf_step["raw"].get("ui_target") == INBOX
      and ("surface" in surf_step["framing"].lower() or "inbox" in surf_step["framing"].lower()))
appr_step = su.next(g["session"])                      # the APPROVE step
af = appr_step["framing"].lower()
check("D2: step 3 (approve) — narrates the operator-only approve gate (approval is yours)",
      appr_step.get("item") == INBOX and "approv" in af)
check("D2b: the approve narration is FIDELITY-TRUE to the wire's safe-by-default model (inert/plan-mode "
      "until armed — NOT 'approve = the change happens'), so the bootstrap matches the real wire-door copy",
      ("plan-mode" in af or "inert" in af or "until it is deliberately armed" in af
       or "nothing modifies" in af or "behind your back" in af))
fin = su.next(g["session"])
check("D3: next() past the end reports done (idempotent terminal — the SAME organ lifecycle, model-free)",
      fin.get("done") is True)

# ── E · FAIL LOUD ───────────────────────────────────────────────────────────────────────────────────
su2 = fresh_suite()
su2.GUIDE_SEQUENCES = dict(su2.GUIDE_SEQUENCES)
su2.GUIDE_SEQUENCES["__empty__"] = ["ui://nowhere/nope", "ui://also/fake"]
empty = su2.start_guide("__empty__")
check("E1: a topic with NO registered addresses → organ_started:False + reason (no silent no-op)",
      empty.get("organ_started") is False and isinstance(empty.get("reason"), str) and len(empty["reason"]) > 0)
check("E2: the dial is STILL set to walkthrough even when there is nothing to tour",
      empty.get("mode") == "walkthrough")
# a teach/indicate length mismatch on start_session RAISES (no silent misalign).
su3 = fresh_suite()
raised = False
try:
    su3.start_session([POINT, ASK], mode="walkthrough", teach=["only one"])   # 1 teach for 2 items
except ValueError:
    raised = True
check("E3: start_session with a teach length != items length RAISES (fail loud — no silent misalign)",
      raised)
raised2 = False
try:
    su3.start_session([POINT, ASK], mode="walkthrough", indicate=["a", "b", "c"])  # 3 indicate for 2 items
except ValueError:
    raised2 = True
check("E4: start_session with an indicate length != items length RAISES (fail loud)", raised2)

# ── F · REGRESSION — C1 default tour byte-identical (corpus-only), session record C1-shaped ─────────
su4 = fresh_suite()
gd = su4.start_guide()                                  # the DEFAULT tour — no teach/indicate
sess_d = su4.store.load_session(gd["session"])
check("F1: REGRESSION — the default tour session record carries NO teach/indicate keys (C1-shaped)",
      "teach" not in sess_d and "indicate" not in sess_d)
d0 = su4.present_current(gd["session"])
# the default-tour step 0 narration must be the CORPUS narration byte-for-byte (the seeded howto on run).
corpus0 = su4._registry_howto_for("ui://toolbar/run") or su4.address_help("ui://toolbar/run").get("what_this_is")
check("F2: REGRESSION — the default tour narrates the CORPUS how-to byte-for-byte (no teach injected)",
      d0.get("framing") == corpus0 and d0["raw"].get("teach") is None and d0["raw"].get("indicate") is None)
# the review organ (start_walkthrough nothing-pending) still fail-loud.
su5 = fresh_suite()
wt = su5.start_walkthrough()
check("F3: REGRESSION — start_walkthrough nothing-pending still fail-loud (organ_started:False + reason)",
      wt.get("organ_started") is False and isinstance(wt.get("reason"), str))

print(f"\n{PASS} checks PASSED — C2 teach-to-request-change bootstrap proven by use.")
