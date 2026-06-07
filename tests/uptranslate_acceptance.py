"""tests/uptranslate_acceptance.py — F1 · the GENERALIZED up-translate move ("present-this-at-altitude").

WHAT up_translate IS (the F1 foundation "up-translate everywhere" stands on):
address_help up-translates ONE address (3 legs); coa up-translates ONE surfaced decision. `up_translate
(kind, ref)` is the REUSABLE move callable on ANY system artifact — an address, a surfaced decision, a
drift/coherence finding, an event — returning ONE altitude envelope:
    {kind, ref, lead (plain-language), mechanism (drillable), legs_present, grounded, degraded, note}
It is a THIN COMPOSER (rule 3, one-source): each kind DISPATCHES to the existing proven organ
(address_help / coa / blast_radius) and normalizes the result. The FE F1 surface + G2 (detectors-as-RHM-
signal) will CONSUME this — they are LATER lanes, NOT built here.

WHAT THIS PROVES (by USE — real Suite + temp FsStore + real discovered nodes + real corpus, NO live model):
  A. ADDRESS — up_translate('address', ui://…) composes address_help into the envelope: a plain-language
     LEAD (what-this-is + how-to-use) + a drillable MECHANISM (how-to-change), legs_present carried through,
     grounded from a REAL registry row. DEGRADE-CLEAN on an unregistered address (the address_help pattern,
     generalized). FAIL LOUD on a malformed address (S0 raise propagates).
  B. DECISION — up_translate('decision', surfaced_id) composes coa (model-free via the canned-completion
     injection): LEAD = the value-framing, MECHANISM = the raw (drillable), the grounding guard's
     grounded/degraded carried through. FAIL LOUD on a missing surfaced_id (coa's KeyError propagates).
  C. FINDING — up_translate('finding', {...}) up-translates a drift/coherence finding the caller holds
     (the shape G2 will feed): LEAD from the finding's content, MECHANISM enriched with the address's
     blast-radius (REUSE blast_radius — what a fix here would touch). GROUNDING GUARD: an empty finding
     ABSTAINS (grounded=False), never invents a finding.
  D. EVENT — up_translate('event', {...}) up-translates one recorded event to a plain line; an empty
     event ABSTAINS.
  E. FAIL LOUD — an UNKNOWN kind raises (rule 8: never fabricate a kind).
  F. REUSE PROOF — up_translate('address') returns the SAME how-to-change as address_help directly, and
     up_translate('decision') returns the SAME raw as coa directly — proving it COMPOSES the organs, not
     a parallel reimplementation.

MODEL-DEPENDENT (flagged): the WORDING quality of the decision lead (inherited from coa) needs a live model
— everything STRUCTURAL (dispatch, envelope shape, grounding guard, degrade, reuse) is proven model-free.

COMPANY_TEST_RUN is set for inbox-hygiene parity with the sibling suites.
"""
import os, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ["COMPANY_TEST_RUN"] = "1"

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite, CoaFraming, CoaOption

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
    return Suite(FsStore(tempfile.mkdtemp(prefix="uptr-")), reg)


def canned_valid(sys_p, user, model, base_url):
    return CoaFraming(meaning="A test framing.",
                      options=[CoaOption(label="A", tradeoff="t1"), CoaOption(label="B", tradeoff="t2")],
                      recommendation="Pick A.")


# Real corpus fixtures (READ from the corpus, never hardcoded prose).
RICH = "ui://toolbar/run"            # all 3 legs authored (rich howto + code scope + represents)
UNREG = "ui://nope/notathing"        # well-formed grammar, NOT in the registry
MALFORMED = "not-a-ui-address"       # violates the S0 grammar → raises
NOCODE = "ui://canvas/wire-request"  # registered (represents) but resolves to NO code symbol

print("F1 · generalized up-translate move (compose the organs, one altitude envelope)")
su = fresh_suite()

# ── A · ADDRESS — composes address_help into the envelope ─────────────────────────────────────────
a = su.up_translate("address", RICH)
check("A1: ADDRESS — the envelope carries kind + ref", a.get("kind") == "address" and a.get("ref") == RICH)
check("A2: ADDRESS — a plain-language LEAD (what-this-is + how-to-use)",
      isinstance(a.get("lead"), str) and len(a["lead"]) > 0)
check("A3: ADDRESS — a drillable MECHANISM (how-to-change: scope + blast_radius)",
      isinstance(a.get("mechanism"), dict))
check("A4: ADDRESS — legs_present carried through (the degrade signal)", isinstance(a.get("legs_present"), dict))
check("A5: ADDRESS — grounded from a REAL registry row (a registered address)", a.get("grounded") is True)
# DEGRADE-CLEAN on an unregistered address (the address_help pattern, generalized).
au = su.up_translate("address", UNREG)
check("A6: ADDRESS-DEGRADE — an unregistered address degrades clean (grounded=False, no crash)",
      au.get("grounded") is False and au.get("degraded") is True and isinstance(au.get("lead"), str))
# FAIL LOUD on a malformed address (S0 raise propagates from address_help).
raised = False
try:
    su.up_translate("address", MALFORMED)
except (ValueError, TypeError):
    raised = True
check("A7: ADDRESS-FAIL-LOUD — a malformed address raises (S0 gate propagates), never a silent envelope",
      raised)

# ── B · DECISION — composes coa (model-free via the injected completion) ──────────────────────────
sid = su.inbox.surface("register_type", {"name": "wc", "code": "def run(): ..."}, default="reject")
d = su.up_translate("decision", sid, _complete=canned_valid)
check("B1: DECISION — the envelope carries kind + ref", d.get("kind") == "decision" and d.get("ref") == sid)
check("B2: DECISION — LEAD = the value-framing (from coa, the schema-shaped text)",
      isinstance(d.get("lead"), str) and "Pick A." in d["lead"])
check("B3: DECISION — MECHANISM = the raw (drillable behind the lead)",
      isinstance(d.get("mechanism"), dict) and d["mechanism"].get("name") == "wc")
check("B4: DECISION — the grounding guard carries through (grounded=True, degraded=False)",
      d.get("grounded") is True and d.get("degraded") is False)
check("B5: DECISION — framing_struct exposed for a drill-to-struct surface", isinstance(d.get("framing_struct"), dict))
# FAIL LOUD on a missing surfaced_id (coa's KeyError propagates).
raised = False
try:
    su.up_translate("decision", "s999-nope", _complete=canned_valid)
except KeyError:
    raised = True
check("B6: DECISION-FAIL-LOUD — a missing surfaced_id raises (coa's KeyError propagates)", raised)

# ── C · FINDING — up-translate a drift/coherence finding (the G2-shaped artifact; G2 NOT wired here) ─
finding = {"address": RICH, "what": "this address drifted from its code refs", "detail": "addresses.json line refs stale"}
f = su.up_translate("finding", finding)
check("C1: FINDING — the envelope carries kind", f.get("kind") == "finding")
check("C2: FINDING — a plain-language LEAD from the finding's content (grounded in the supplied finding)",
      isinstance(f.get("lead"), str) and "drifted" in f["lead"])
check("C3: FINDING — grounded from the REAL supplied finding (not invented)", f.get("grounded") is True)
check("C4: FINDING — MECHANISM enriched with what a fix TOUCHES (REUSE blast_radius on the named address)",
      isinstance(f.get("mechanism"), dict) and f["mechanism"].get("touches") is not None)
check("C5: FINDING — legs_present marks the touches leg resolved",
      (f.get("legs_present") or {}).get("touches") is True)
# GROUNDING GUARD: an empty/malformed finding ABSTAINS, never invents a finding.
fe = su.up_translate("finding", {})
check("C6: FINDING-ABSTAIN — an empty finding abstains (grounded=False, an honest 'can't frame' lead)",
      fe.get("grounded") is False and "can't frame" in (fe.get("lead") or "").lower())
# DEGRADE-CLEAN: a finding whose address can't resolve still frames (best-effort enrichment, never fabricates).
fnc = su.up_translate("finding", {"address": NOCODE, "what": "stale ref here"})
check("C7: FINDING-DEGRADE — a no-code address still frames the finding (best-effort touches, no crash)",
      fnc.get("grounded") is True and isinstance(fnc.get("lead"), str))

# ── D · EVENT — up-translate one recorded event to a plain line ───────────────────────────────────
ev = su.up_translate("event", {"kind": "warning", "summary": "embedder unreachable", "address": RICH})
check("D1: EVENT — a plain-language LEAD from the event summary", "embedder unreachable" in (ev.get("lead") or ""))
check("D2: EVENT — grounded from the real event, MECHANISM = the raw event (drillable)",
      ev.get("grounded") is True and isinstance(ev.get("mechanism"), dict))
eve = su.up_translate("event", {})
check("D3: EVENT-ABSTAIN — an empty event abstains (grounded=False)", eve.get("grounded") is False)

# ── E · FAIL LOUD — an unknown kind raises (rule 8) ───────────────────────────────────────────────
raised = False
try:
    su.up_translate("nonsense", RICH)
except ValueError:
    raised = True
check("E1: FAIL LOUD — an unknown kind raises (never fabricate a kind, rule 8)", raised)

# ── F · REUSE PROOF — up_translate COMPOSES the organs (same results), not a parallel reimplementation ─
direct_help = su.address_help(RICH)
check("F1: REUSE — up_translate('address') returns the SAME how-to-change as address_help directly "
      "(it composes, never re-implements)", a["mechanism"] == direct_help["how_to_change"])
direct_coa = su.coa(sid, _complete=canned_valid)
check("F2: REUSE — up_translate('decision') returns the SAME raw as coa directly (composes the organ)",
      d["mechanism"] == direct_coa["raw"])

print(f"\n{PASS} checks PASSED — the generalized up-translate move proven by use (address · decision · "
      "finding · event · fail-loud · reuse), model-free. WORDING-QUALITY flagged model-dependent.")
