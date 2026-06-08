"""tests/address_help_surface_acceptance.py — D2 · the COMPOSED address-help / altitude SURFACE.

WHAT D2 IS (the operator-facing help/altitude surface of the Operable Interface):
the panel that shows, for an INDICATED ui:// element, the THREE legs of `address_help` composed into ONE
designed surface AT TIM'S ALTITUDE — what-this-is · how-to-use (the plain-language lead) · how-to-change
(the mechanism, behind a drill-down). The BACKEND half (this suite's subject) EXPOSES the EXISTING D1
composer `Suite.address_help` (committed 89f60d9 — NOT rebuilt) via a minimal additive bridge route
`GET /api/address-help?address=ui://…`. The FE half is `canvas/app/src/regions/AddressHelp.tsx` (verified
by USE in chrome, both viewports — see the lane report).

WHAT THIS PROVES (by USE — real Suite + temp FsStore + real discovered nodes + the real corpus registry,
NO live model, mirroring conv_howto_acceptance's method-level contract):
  A. the composed bundle returns the THREE legs for a REAL, fully-authored address (what + how-to-use +
     how-to-change), with `legs_present` all true — the surface's full-panel state.
  B. DEGRADE CLEAN on a THIN-howto address (G-53): what + how-to-change present, how-to-use honestly
     absent (None / legs_present.how_to_use False) — never a crash, never a fabricated help.
  C. DEGRADE CLEAN on a NO-CODE address (a CSS/orphan ref): what present, how-to-change honestly empty
     with a `note` (DENY-ALL, never a fabricated scope) — the surface renders the note, not a blank.
  D. DEGRADE CLEAN on a well-formed-but-UNREGISTERED address: a partial bundle (what_this_is tagged
     '(unregistered)', legs_present.what_this_is False) — never a crash.
  E. FAIL LOUD on a MALFORMED address: `address_help` raises the S0 grammar gate (→ the bridge's
     do_GET try/except sends a 400) — never a silent empty bundle.

The ROUTE itself (GET /api/address-help → SUITE.address_help, missing-param → 400, malformed → 400) is
proven by curl against the live bridge :8771 in the lane's by-use step (no sibling acceptance suite builds
an HTTP harness; the route is a one-line `self._send(200, json.dumps(SUITE.address_help(q["address"])))`
inside the SAME shared try/except every sibling read route uses — KeyError on a missing `address` and
ValueError on a malformed one both fall out as 400 for free).

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
    return Suite(FsStore(tempfile.mkdtemp(prefix="ahelp-")), reg)


# Real fixtures, READ from the corpus (never the text hardcoded). If a seed changes, pick any address of
# the matching shape — the assertions test the BUNDLE STRUCTURE + the legs_present flags, not the prose.
RICH = "ui://toolbar/run"            # all 3 legs authored (rich howto + code scope + represents)
THIN = "ui://toolbar/portal"         # code scope present, NO authored howto (G-53 — the thin how-to-use leg)
UNREG = "ui://nope/notathing"        # well-formed grammar, NOT in the registry
MALFORMED = "not-a-ui-address"       # violates the S0 grammar → raises

# NO-CODE fixture — SYNTHETIC (G-61/GC1 style). The C-section proves a real DEFENSIVE property: that
# address_help DEGRADES CLEAN on a registered-but-codeless address — what-this-is still present, the
# how-to-change scope honestly EMPTY (DENY-ALL) with a legible note, NO fabricated scope (rule 8). That
# property still matters as a regression guard. BUT no REAL registered address triggers it anymore:
#   • GC5 (wave 15, commit 22eef13) CORRECTLY gave ui://canvas/wire-request a resolving code scope — it
#     indexed surface_intent_at as a code symbol (the whole point of GC5), flipping its scope EMPTY→
#     ['runtime/suite.py']. So the former NO-CODE fixture now resolves a real scope.
#   • The connect+unify corpus work then resolved EVERY registered address — ZERO registered addresses
#     now resolve to an empty scope. The "registered-but-codeless" shape is EXTINCT in the real corpus.
# This is the corpus being MORE correct, not a bug. So we drive the degrade path on a SYNTHETIC no-code
# input constructed INSIDE this test (NOT added to design/_system/addresses.json — kept local): a
# well-formed ui:// address injected into su.UI_REGISTRY with a `represents` (so what-this-is resolves
# present) but referenced by NO code symbol in code-symbols.json (so resolve_scope returns empty DENY-ALL
# with a note — never a fabricated scope). This proves the SAME degrade-clean shape on a genuinely-no-code
# input WITHOUT relying on a now-resolving real address, and WITHOUT weakening any assertion.
NOCODE = "ui://canvas/synthetic-nocode-probe"  # SYNTHETIC, injected below — registered, NO code symbol

print("D2 · composed address-help / altitude surface (backend bundle + degrade + fail-loud)")
su = fresh_suite()

# Inject the SYNTHETIC no-code fixture (see NOCODE above): a well-formed ui:// row registered in the LIVE
# UI_REGISTRY (so _describe_ui_address resolves what-this-is via its `represents`) but referenced by NO
# code symbol in code-symbols.json (so resolve_scope returns empty DENY-ALL + a note — never fabricated).
# A UI_REGISTRY row is (ref, kind, title, dom_handle, capabilities, extras{represents,code,howto}). We give
# it `represents` (→ what-this-is present) and NO `howto` (the C-section tests the change-leg, not how-to-use).
# This stays INSIDE the test — design/_system/addresses.json is NOT touched (corpus is a file-disjoint lane).
su.UI_REGISTRY = list(su.UI_REGISTRY) + [
    (NOCODE, "canvas", NOCODE, {"dom_handle": NOCODE},
     {"pointable": True}, {"region": "canvas", "represents": "PROBE-nocode", "code": None}),
]

# ── A · the FULL bundle — three legs for a fully-authored address ────────────────────────────────
b = su.address_help(RICH)
check("A1: the bundle carries the address it was asked for", b.get("address") == RICH)
check("A2: leg WHAT-THIS-IS is a non-empty string", isinstance(b.get("what_this_is"), str) and len(b["what_this_is"]) > 0)
check("A3: leg HOW-TO-USE is the authored howto prose (non-empty string)",
      isinstance(b.get("how_to_use"), str) and len(b["how_to_use"]) > 0)
htc = b.get("how_to_change") or {}
check("A4: leg HOW-TO-CHANGE carries a non-empty code scope (the files a change here edits)",
      isinstance(htc.get("scope"), list) and len(htc["scope"]) > 0)
check("A5: leg HOW-TO-CHANGE carries a blast_radius dict (the X9/X14 reach the surface drills into)",
      isinstance(htc.get("blast_radius"), dict))
lp = b.get("legs_present") or {}
check("A6: legs_present marks ALL THREE legs present for a fully-authored address",
      lp.get("what_this_is") is True and lp.get("how_to_use") is True and lp.get("how_to_change") is True)

# ── B · DEGRADE — a THIN-howto address (G-53): the how-to-use leg honestly absent ─────────────────
b = su.address_help(THIN)
check("B1: a THIN-howto address still returns a bundle (no crash)", isinstance(b, dict) and b.get("address") == THIN)
check("B2: leg WHAT-THIS-IS still present (the represents identity)", bool(b.get("what_this_is")))
check("B3: leg HOW-TO-USE is None — an HONEST absence (G-53), never a fabricated help",
      b.get("how_to_use") is None)
check("B4: legs_present.how_to_use is False (the surface renders 'no how-to authored yet', not a blank)",
      (b.get("legs_present") or {}).get("how_to_use") is False)
check("B5: leg HOW-TO-CHANGE still present (the element has a code scope to change)",
      (b.get("legs_present") or {}).get("how_to_change") is True)

# ── C · DEGRADE — a (SYNTHETIC) NO-CODE address: how-to-change honestly empty WITH a note, never fabricated ─
# Driven on the synthetic registered-but-codeless fixture injected above (the real ui://canvas/wire-request
# now resolves a code scope post-GC5/connect+unify — see NOCODE). Proves the SAME degrade-clean property.
b = su.address_help(NOCODE)
check("C1: a NO-CODE address still returns a bundle (no crash)", isinstance(b, dict) and b.get("address") == NOCODE)
check("C2: leg WHAT-THIS-IS still present (the address IS registered — represents a feature)",
      (b.get("legs_present") or {}).get("what_this_is") is True)
htc = b.get("how_to_change") or {}
check("C3: leg HOW-TO-CHANGE scope is EMPTY (DENY-ALL — never a fabricated scope, rule 8)",
      htc.get("scope") == [])
check("C4: leg HOW-TO-CHANGE carries a legible NOTE (the surface renders WHY there's nothing to change)",
      isinstance(htc.get("note"), str) and len(htc["note"]) > 0)
check("C5: legs_present.how_to_change is False (the genuinely-empty change-leg — the degrade signal)",
      (b.get("legs_present") or {}).get("how_to_change") is False)

# ── D · DEGRADE — a well-formed but UNREGISTERED address: a clean partial, never a crash ───────────
b = su.address_help(UNREG)
check("D1: an UNREGISTERED (well-formed) address still returns a bundle (no crash)",
      isinstance(b, dict) and b.get("address") == UNREG)
check("D2: leg WHAT-THIS-IS carries the '(unregistered)' tag (the honest gap, not a description)",
      "(unregistered)" in (b.get("what_this_is") or ""))
check("D3: legs_present.what_this_is is False (the surface says 'not registered', not the raw tag)",
      (b.get("legs_present") or {}).get("what_this_is") is False)

# ── E · FAIL LOUD — a MALFORMED address raises (S0 grammar gate) → the bridge sends a 400 ──────────
raised = False
try:
    su.address_help(MALFORMED)
except Exception:
    raised = True
check("E1: a MALFORMED address FAILS LOUD (S0 grammar gate raises → bridge 400), never a silent bundle",
      raised)

print(f"\nD2 address-help surface — {PASS} checks PASS (backend bundle + 4 degrade branches + fail-loud)")
