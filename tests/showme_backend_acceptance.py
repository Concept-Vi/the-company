"""tests/showme_backend_acceptance.py — the SHOW-ME / guided-operation BACKEND foundation (C3 + C4).

The show-me/guided experience needs two BACKEND seams (the FE wiring is a separate lane):

  C3 · `show` resolves ELEMENT-level addresses.
       The `show` verb resolved node/region targets (ui://canvas/<node>, ui://chrome/inbox, bare
       'inbox') but SILENTLY REFUSED S1 element-level addresses (ui://<region>/<element>, e.g.
       ui://toolbar/run) — even though those ARE registered in UI_REGISTRY (keyed by their FULL
       canonical string via _load_corpus_element_addresses). Root cause: the ui:// branch parsed the
       address into kind/<element-SEGMENT> and checked the SEGMENT ('run') against the registry, never
       the full string. Fix: resolve the FULL string against the SAME registry (build_ui_info — no
       parallel resolver) first; a match passes through unchanged for the FE's resolveUiTarget.

  C4 · the walkthrough naming trap (BACKEND half).
       A cosmetic presence-dial 'walkthrough' MODE (MODE_DIRECTIVES — narration only) vs. a real
       walkthrough ORGAN (start_session — the screen-driving review engine). Selecting the dial-mode
       only set the directive; it never bound to / started the organ. Fix: start_walkthrough() — the
       mode-selection → organ-start seam — composes the EXISTING set_mode (dial) + the EXISTING pending
       gather + the EXISTING start_session organ, reachable via POST /api/walkthrough/start.

WHAT THIS PROVES (by USE — real Suite, real corpus registry, real nodes/ registry, NO live model):
  C3-A. `show` of a real element address (ui://toolbar/run) RESOLVES to that target (not a refusal).
  C3-B. the I2 operator-click path (act/_act_dict) also resolves the element address (both faces).
  C3-C. FAIL-LOUD preserved: an unknown element (ui://toolbar/nope) still REFUSES.
  C3-D. REGRESSION: node-id, ui://chrome/inbox, and bare 'inbox' STILL resolve (existing behaviour).
  C4-A. start_walkthrough() over a seeded pending item BINDS the organ (session exists, cursor 0,
        mode=walkthrough) — selecting the guided mode reaches the organ start.
  C4-B. set_mode stays PURE: setting 'walkthrough' alone starts NO organ (contract unchanged).
  C4-C. FAIL-LOUD (no silent no-op): nothing pending → organ_started:False + a reason (dial still set).
  C4-D. REGRESSION: the existing start_session organ still works unchanged.

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
    return Suite(FsStore(tempfile.mkdtemp(prefix="showme-")), reg)


GID = "demo"
# Real S1 element-level addresses (design/_system/addresses.json — read from the corpus, not invented).
ELEM = "ui://toolbar/run"
ELEM2 = "ui://toolbar/presence"
ELEM_REGION_FORM = "ui://inbox/build-review"   # region-first element grammar
UNKNOWN_ELEM = "ui://toolbar/does-not-exist"

print("SHOW-ME backend foundation · C3 (show element addresses) + C4 (walkthrough seam)")

# ── C3 · show resolves ELEMENT-level addresses ───────────────────────────────────────────────────
su = fresh_suite()
# (proof the address really is a registry key — the precondition the bug ignored)
reg = su.build_ui_info()
check("C3-pre: the element address IS a registry key (build_ui_info — full canonical string)",
      ELEM in reg and ELEM_REGION_FORM in reg)

r = su._dispatch_rhm_action({"verb": "show", "targets": [ELEM]}, GID)
check("C3-A1: `show ui://toolbar/run` RESOLVES (did=show, not a refusal)",
      r.get("did") == "show" and ELEM in r.get("targets", []))
r2 = su._dispatch_rhm_action({"verb": "show", "targets": [ELEM_REGION_FORM]}, GID)
check("C3-A2: `show ui://inbox/build-review` (region-first element grammar) RESOLVES",
      r2.get("did") == "show" and ELEM_REGION_FORM in r2.get("targets", []))
# multi-target (a guided walk pointing at several elements at once)
rmulti = su._dispatch_rhm_action({"verb": "show", "targets": [ELEM, ELEM2]}, GID)
check("C3-A3: a multi-element show resolves ALL registered element targets",
      rmulti.get("did") == "show" and set(rmulti["targets"]) == {ELEM, ELEM2})

# C3-B · the I2 OPERATOR-CLICK path (act → _act_dict → _dispatch_rhm_action) also resolves it (both faces)
adict = Suite._act_dict("show", ELEM, {})
check("C3-B1: _act_dict carries the clicked element address into show's targets[]",
      adict.get("verb") == "show" and ELEM in adict.get("targets", []))
ract = su.act("show", GID, address=ELEM)
# act() folds the dispatcher outcome under `action` (+ a friendly `reply`) — read the nested action.
ract_action = ract.get("action", {})
check("C3-B2: act('show', address=ui://toolbar/run) RESOLVES the element (the operator-click face)",
      ract_action.get("did") == "show" and ELEM in ract_action.get("targets", []))

# C3-C · FAIL-LOUD preserved: an unknown element still REFUSES (the gate is not weakened)
rno = su._dispatch_rhm_action({"verb": "show", "targets": [UNKNOWN_ELEM]}, GID)
check("C3-C1: an UNKNOWN element (ui://toolbar/does-not-exist) is REFUSED (fail-loud preserved)",
      rno.get("did") == "none" and "refused" in rno)

# C3-D · REGRESSION: the EXISTING target forms all still resolve unchanged
nid = su.create_node(GID, "constant", config={"value": "x"})
check("C3-D1: REGRESSION — a bare node-id still resolves (existing behaviour)",
      su._dispatch_rhm_action({"verb": "show", "targets": [nid]}, GID).get("targets") == [nid])
check("C3-D2: REGRESSION — ui://canvas/<node> still resolves (camera path)",
      su._dispatch_rhm_action({"verb": "show", "targets": [f"ui://canvas/{nid}"]}, GID).get("targets")
      == [f"ui://canvas/{nid}"])
check("C3-D3: REGRESSION — ui://canvas/* (whole canvas) still resolves",
      su._dispatch_rhm_action({"verb": "show", "targets": ["ui://canvas/*"]}, GID).get("targets")
      == ["ui://canvas/*"])
check("C3-D4: REGRESSION — region kind-form ui://chrome/inbox still resolves",
      su._dispatch_rhm_action({"verb": "show", "targets": ["ui://chrome/inbox"]}, GID).get("targets")
      == ["ui://chrome/inbox"])
check("C3-D5: REGRESSION — bare handle 'inbox' still lenient-resolves to ui://chrome/inbox",
      su._dispatch_rhm_action({"verb": "show", "targets": ["inbox"]}, GID).get("targets")
      == ["ui://chrome/inbox"])
# CRITICAL gate-preservation: ui://canvas/node IS a corpus element row (kind=canvas, full-string key in
# build_ui_info) — but the canvas branch's LIVE-NODE gate must still apply (the FE drives the camera only
# to a node on the loaded graph). The element full-string check lives INSIDE the non-canvas else branch
# precisely so it CANNOT bypass this gate. With no live node literally named 'node', it must REFUSE.
check("C3-D6: REGRESSION — ui://canvas/node (a canvas corpus row) is REFUSED unless a live node 'node' "
      "exists (the live-node camera gate is NOT bypassed by the element-address fix)",
      su._dispatch_rhm_action({"verb": "show", "targets": ["ui://canvas/node"]}, GID).get("did") == "none")

# ── C4 · the walkthrough naming trap (BACKEND half) ──────────────────────────────────────────────
su2 = fresh_suite()
# C4-B · set_mode stays PURE: selecting the dial-mode alone starts NO organ.
su2.set_mode("walkthrough")
check("C4-B1: set_mode('walkthrough') persists the dial (get_mode) — the cosmetic mode",
      su2.get_mode() == "walkthrough")
# PURE-CONTRACT proof: set_mode must NOT start the organ. Assert NO review session AND no review-* graph
# exist after it (it only writes the 'system' rhm_mode node). The organ creates a session record + a graph
# id 'review-<session>'; neither must appear here.
_review_graphs = [g for g in su2.store.list_graphs() if str(g).startswith("review-")]
check("C4-B2: set_mode alone created NO review session + NO review-* graph (pure contract — no organ start)",
      _review_graphs == [] and su2.store.list_sessions() == [])

# C4-C · FAIL-LOUD: nothing pending → organ_started:False + a reason (no silent no-op, no crash)
su3 = fresh_suite()
empty = su3.start_walkthrough()
check("C4-C1: nothing pending → organ_started:False (no silent no-op)",
      empty.get("organ_started") is False)
check("C4-C2: the dial is STILL set to walkthrough even when nothing is pending",
      empty.get("mode") == "walkthrough" and su3.get_mode() == "walkthrough")
check("C4-C3: a human-legible reason is returned (fail-loud, not a fabricated success)",
      isinstance(empty.get("reason"), str) and len(empty["reason"]) > 0)

# C4-A · start_walkthrough over a seeded pending item BINDS the organ (no live model needed)
su4 = fresh_suite()
cap = su4.idea_capture("walk me through this captured idea")    # a real pending generative review item
check("C4-A0 (setup): a pending review item exists", cap.get("id"))
started = su4.start_walkthrough()
check("C4-A1: start_walkthrough BINDS the organ (organ_started:True) — dial-mode reaches the organ start",
      started.get("organ_started") is True)
check("C4-A2: the organ session exists (a real session id is returned)",
      isinstance(started.get("session"), str) and started["session"])
check("C4-A3: the organ presents the FIRST item (cursor 0) — the review walk is live",
      started.get("cursor") == 0 and started.get("done") is False)
check("C4-A4: the dial is set to walkthrough alongside the organ start",
      started.get("mode") == "walkthrough")
# the session is server-authoritative — its graph + record exist (the organ is really running)
sess = su4.store.load_session(started["session"])
check("C4-A5: the session record persisted (server-authoritative organ)",
      sess is not None and sess.get("mode") == "walkthrough" and len(sess.get("items", [])) == 1)
# present_current re-reads the live session (proves the organ lifecycle is reachable, not a one-shot fiction)
pc = su4.present_current(started["session"])
check("C4-A6: present_current re-reads the live session (organ lifecycle reachable)",
      pc.get("session") == started["session"] and pc.get("cursor") == 0)

# explicit pre-selected item_ids path (operator chose a set)
su5 = fresh_suite()
i1 = su5.idea_capture("alpha")["id"]; i2 = su5.idea_capture("beta")["id"]
sel = su5.start_walkthrough([i1])
check("C4-A7: start_walkthrough([item]) walks exactly the pre-selected set (1 item, not all pending)",
      sel.get("organ_started") is True
      and su5.store.load_session(sel["session"]).get("items") == [i1])

# C4-D · REGRESSION: the EXISTING start_session organ still works unchanged
su6 = fresh_suite()
sid_item = su6.idea_capture("a direct review item")["id"]
direct = su6.start_session([sid_item], mode="walkthrough")
check("C4-D1: REGRESSION — start_session organ still presents the first item (UNCHANGED)",
      direct.get("cursor") == 0 and isinstance(direct.get("session"), str))

print(f"\n{PASS} checks PASSED — show-me backend foundation (C3 + C4) proven by use.")
