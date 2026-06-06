"""tests/showme_guided_acceptance.py — C1 · SYSTEM-INITIATED GUIDED SEQUENCES + G-43.

WHAT C1 IS (the "show me how" guided-operation mode):
A SYSTEM/RHM-INITIATED step-sequence that highlights real ADDRESSED ELEMENTS, narrates PER-ELEMENT from
the corpus how-to, and steps through — distinct from the review-organ's pending-INBOX-item walk (which is
operator/dial-triggered). It is built REUSE-ONLY on the EXISTING spine:

  • THE STEPPER — the SAME walkthrough organ (start_session / present_current / next), NOT a parallel one.
    A guided sequence is a review session whose ITEMS are `ui://<region>/<element>` ADDRESSES instead of
    inbox review-ids. The ONLY divergence is in present_current: a step that IS a ui:// address frames
    from the CORPUS how-to (address_help, D1) and returns BEFORE the coa() call — so a guided walk is
    MODEL-FREE BY CONSTRUCTION (coa is what makes the review walk model-dependent, G-41). This suite runs
    the WHOLE lifecycle (start → present each step → next → done) with NO model up to PROVE that.

  • SYSTEM-INITIATED — start_guide() is callable directly (this test calls it bare, no operator click;
    the bridge route /api/guide/start + the RHM can call it too).

  • G-43 — each guided step carries a RESOLVABLE per-step ui_target (a registered element address), so the
    FE per-step resolveUiTarget drives + spotlights the REAL element. Before C1, payload-less/synthetic
    steps got no ui_target and the spotlight no-op'd. _registry_ui_target now honours a payload-carried
    `guide_address`/`ui_target` (validated against the live registry) FIRST.

WHAT THIS PROVES (by USE — real Suite, real corpus registry, real nodes/ registry, NO live model):
  A. start_guide() (system-initiated, bare call) BINDS the organ over registry-true element addresses.
  B. each step RESOLVES its corpus how-to as narration (address_help — how_to_use ∨ what_this_is, never
     empty, never fabricated) AND a registry-VALID per-step ui_target (G-43).
  C. the SAME next() advances the guide step-by-step to done — MODEL-FREE (no model is ever called).
  D. G-43 — _registry_ui_target honours a payload-carried registered guide_address (the seam the FE drive
     reads), and REFUSES a fabricated/unregistered address (falls back to the safe inbox region — never a
     dead ref the FE would fail-loud on).
  E. FAIL LOUD — a guide topic that resolves to NO registered addresses returns organ_started:False + a
     reason (no silent no-op); the dial is still set.
  F. REGRESSION — the review-organ walk (start_walkthrough / start_session over inbox items + the coa
     framing path) is UNTOUCHED; _registry_ui_target's node→canvas + inbox fallback still hold.

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
    return Suite(FsStore(tempfile.mkdtemp(prefix="guided-")), reg)


# A registered element address that carries an AUTHORED howto (the seeded D1 text) + one that does not.
SEEDED = "ui://toolbar/run"          # design/_system/addresses.json seeds a `howto` here
ANY_REGION = "ui://inbox/build-review"   # a registered element (in the default tour)
UNKNOWN = "ui://toolbar/does-not-exist"

print("C1 · SYSTEM-INITIATED guided sequences + G-43 (per-step resolvable ui_target)")

# ── A · start_guide (system-initiated) BINDS the organ over registry-true addresses ─────────────────
su = fresh_suite()
# precondition: the default sequence is registry-true (every address is a live UI_REGISTRY key).
reg = su.build_ui_info()
seq = su._guide_sequence(None)
check("A0: the default guide sequence resolves to ≥2 REGISTERED element addresses (registry-is-truth)",
      len(seq) >= 2 and all(a in reg for a in seq))
check("A0b: the seeded-howto address is in the default tour (so the tour opens on real how-to narration)",
      SEEDED in seq)

g = su.start_guide()                                   # BARE call — no operator click (system-initiated)
check("A1: start_guide() BINDS the organ (organ_started:True, guide:True) — system-initiated",
      g.get("organ_started") is True and g.get("guide") is True)
check("A2: a real organ session id is returned (server-authoritative)",
      isinstance(g.get("session"), str) and g["session"])
check("A3: the organ presents the FIRST step (cursor 0, not done)",
      g.get("cursor") == 0 and g.get("done") is False)
check("A4: the dial is set to walkthrough alongside the guide start (guide register)",
      g.get("mode") == "walkthrough" and su.get_mode() == "walkthrough")
check("A5: the steps are exactly the registry-filtered address sequence",
      g.get("steps") == seq)
# the session record persisted with the ADDRESSES as its items (not inbox ids) — the reused organ.
sess = su.store.load_session(g["session"])
check("A6: the session record persisted with the ui:// ADDRESSES as items (the reused organ over addresses)",
      sess is not None and sess.get("items") == seq and sess.get("mode") == "walkthrough")

# ── B · each step resolves its corpus how-to as narration + a registry-VALID ui_target (G-43) ───────
# step 0 (the seeded-howto address) — narration is the AUTHORED how-to, ui_target is the element itself.
step0 = su.present_current(g["session"])
check("B1: step 0 carries framing (the narration) — non-empty, from the corpus (never fabricated)",
      isinstance(step0.get("framing"), str) and len(step0["framing"]) > 0)
authored = su._registry_howto_for(SEEDED)
check("B2: the seeded step narrates its AUTHORED how_to_use (address_help leg, NOT a stand-in)",
      authored and step0["framing"] == authored)
check("B3: G-43 — step 0's per-step raw.ui_target IS the registered element address (resolvable spotlight)",
      step0.get("raw", {}).get("ui_target") == SEEDED and SEEDED in reg)
check("B4: the step is marked a GUIDE step (the FE branches tour-vs-review on raw.guide_address)",
      step0["raw"].get("guide_address") == SEEDED and step0.get("guide") is True)
check("B5: the full how-to bundle rides the step (a richer surface can read all three legs)",
      isinstance(step0["raw"].get("how_to"), dict) and step0["raw"]["how_to"].get("address") == SEEDED)
check("B6: the step's top-level ui_target is the element address (the present target IS the element)",
      step0.get("ui_target") == SEEDED)

# ── C · the SAME next() advances the guide to done — MODEL-FREE (no model ever called) ──────────────
# walk every step via the EXISTING next(); each present is corpus-framed, never a model. A model-down
# review walk HANGS in coa (G-41); this walk completes instantly because the guide branch returns before coa.
seen = [step0["item"]]
cur = step0
for _ in range(len(seq)):
    cur = su.next(g["session"])
    if cur.get("done"):
        break
    seen.append(cur["item"])
    check(f"C-step: next() presents the element {cur['item']} with non-empty corpus framing (model-free)",
          cur["item"] in reg and isinstance(cur.get("framing"), str) and len(cur["framing"]) > 0
          and cur["raw"].get("ui_target") == cur["item"])
check("C1: the guide walked EVERY registry-filtered address in order (the reused organ, model-free)",
      seen == seq)
fin = su.next(g["session"])
check("C2: next() past the end reports done (idempotent terminal — the SAME organ lifecycle)",
      fin.get("done") is True)

# ── D · G-43 — _registry_ui_target honours a registered guide_address, refuses a fabricated one ─────
su2 = fresh_suite()
check("D1: G-43 — _registry_ui_target({guide_address: <registered>}) RETURNS that element address",
      su2._registry_ui_target({"guide_address": SEEDED}) == SEEDED)
check("D2: G-43 — a payload-carried registered ui_target is honoured too (the FE-read seam)",
      su2._registry_ui_target({"ui_target": ANY_REGION}) == ANY_REGION)
check("D3: G-43 fail-safe — an UNREGISTERED guide_address is NOT passed through (no dead ref) — falls "
      "back to the safe inbox region (registry-is-truth)",
      su2._registry_ui_target({"guide_address": UNKNOWN}) == "ui://chrome/inbox")

# ── E · FAIL LOUD — a topic with no registered addresses → organ_started:False + reason (no no-op) ──
su3 = fresh_suite()
# inject a topic whose addresses are all unregistered (proves the registry filter + the fail-loud path).
su3.GUIDE_SEQUENCES = dict(su3.GUIDE_SEQUENCES)
su3.GUIDE_SEQUENCES["__empty__"] = ["ui://nowhere/nope", "ui://also/fake"]
empty = su3.start_guide("__empty__")
check("E1: a guide topic with NO registered addresses → organ_started:False (no silent no-op)",
      empty.get("organ_started") is False)
check("E2: a human-legible reason is returned (fail-loud, not a fabricated success)",
      isinstance(empty.get("reason"), str) and len(empty["reason"]) > 0)
check("E3: the dial is STILL set to walkthrough even when there is nothing to tour",
      empty.get("mode") == "walkthrough" and su3.get_mode() == "walkthrough")

# ── F · REGRESSION — the review-organ walk + _registry_ui_target's existing branches are UNTOUCHED ──
su4 = fresh_suite()
# the review walk over an inbox item still presents via the coa path (raw is a payload dict, NOT a guide
# branch). With no model up coa fails-safe to the raw payload — present_current never raises (guide D).
cap = su4.idea_capture("a real pending review item")
sess_r = su4.start_session([cap["id"]], mode="walkthrough")
check("F1: REGRESSION — the review-organ walk over an INBOX item still presents (cursor 0, not a guide)",
      sess_r.get("cursor") == 0 and sess_r.get("guide") is not True)
check("F2: REGRESSION — a node-less review item still maps to the inbox region (existing _registry_ui_target)",
      su4._registry_ui_target({}) == "ui://chrome/inbox")
check("F3: REGRESSION — a node-backed payload still maps node→canvas (existing _registry_ui_target)",
      su4._registry_ui_target({"node": "abc"}) == "ui://canvas/abc")
# start_walkthrough's nothing-pending fail-loud path is unchanged.
su5 = fresh_suite()
wt = su5.start_walkthrough()
check("F4: REGRESSION — start_walkthrough nothing-pending still fail-loud (organ_started:False + reason)",
      wt.get("organ_started") is False and isinstance(wt.get("reason"), str))

print(f"\n{PASS} checks PASSED — C1 system-initiated guided sequences + G-43 proven by use.")
