"""tests/coa_acceptance.py — F1 · coa, the up-translate ORGAN (the #1 foundation shore-up).

WHAT coa IS (F1's core up-translate organ):
`coa(surfaced_id)` translates a raw technical decision into a COMMANDER-ALTITUDE value choice — what it
MEANS in plain terms, 2-3 value options with trade-offs, a recommendation — while the raw payload stays
DRILLABLE. The operator decides on value, never the raw fork (C2). It is F1's core primitive; "up-translate
everywhere" stands on it. Before this suite it had ZERO acceptance coverage + an unguarded live-model call.

WHAT THIS PROVES (by USE — real Suite + temp FsStore + real discovered nodes, NO live model):
The brief's bar splits STRUCTURE (prove model-free) from WORDING-QUALITY (live-model-dependent). The
structure is now CODE-ENFORCED (the CoaFraming schema) so this suite proves it deterministically via an
injected canned response (`_complete=`), with NO live model:

  A. ROUTING + SHAPE — a real surfaced decision routes to coa and the up-translate SHAPE is
     {plain-language meaning, 2-3 value options each with a trade-off, a recommendation}; the schema is
     code-enforced (CoaFraming), the FE-contract `framing` string carries every part, framing_struct is
     the validated struct.
  B. RAW STAYS DRILLABLE — the raw payload is attached on every return path (drill-down preserved).
  C. GROUNDING GUARD (a) ABSTAIN-ON-EMPTY — a surfaced item with NO payload does NOT call the model
     (no confabulation from emptiness): grounded=False, an honest "can't frame" lead, raw attached.
  D. GROUNDING GUARD (b) DEGRADE-ON-MODEL-ABSENT — when the framing model is unavailable (a raising
     stub stands in for a down model), coa FAILS LOUD-LEGIBLE: a "model unavailable" framing, degraded=True,
     raw still drillable, NO fabricated framing.
  E. SCHEMA IS THE BAR — a model that emits a SHAPE coa cannot satisfy degrades (treated like model-absent),
     it does NOT pass malformed prose through. (Proven via an injected stub that returns the wrong shape →
     the schema-construction in the test mirrors the live `client.complete(schema=)` raise.)
  F. FAIL LOUD — a missing surfaced_id RAISES KeyError (asked to frame a thing that doesn't exist), never
     a silent empty.
  G. FE CONTRACT (additive-only) — id/raw/framing(string) preserved for Grow.tsx; framing_struct/grounded/
     degraded added alongside (the FE ignores unknown keys; canvas/** is out of this lane's file set).

MODEL-DEPENDENT (flagged, NOT proven here): whether a LIVE model, given a real decision, EMITS a good,
on-payload framing that SATISFIES the CoaFraming schema (the wording quality + schema-satisfiability). That
is the live-model-up check; everything STRUCTURAL is proven model-free above.

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
    return Suite(FsStore(tempfile.mkdtemp(prefix="coa-")), reg)


# A canned VALID framing (the model-free stand-in for the live model's output). It satisfies the
# CoaFraming schema exactly, so the structure/routing/projection are all proven WITHOUT a model.
def canned_valid(sys_p, user, model, base_url):
    # the system prompt + user prompt are passed through (so the test could assert grounding if needed);
    # we ignore them and return a fixed, schema-valid struct — proving SHAPE deterministically.
    return CoaFraming(
        meaning="Adding the wordcount node changes how the pipeline measures document size.",
        options=[
            CoaOption(label="Approve the node as drafted", tradeoff="gain the capability now; trust the draft"),
            CoaOption(label="Send it back for a tweak", tradeoff="safer wording; costs another round"),
        ],
        recommendation="Approve — the draft is small and git-reversible if wrong.")


# A stub that RAISES — stands in for a DOWN / unreachable model (FabricError-class). coa must degrade
# clean-loud, never fabricate.
def model_down(sys_p, user, model, base_url):
    from fabric.client import FabricError
    raise FabricError("transport error: connection refused (model down)")


print("F1 · coa — the up-translate organ (structure + grounding guard + degrade, model-free)")
su = fresh_suite()

# Surface a REAL decision with a real payload (a 'register_type' draft — the propose path's shape).
sid = su.inbox.surface("register_type",
                       {"name": "wordcount", "code": "def run(...): ...  # the drafted node"},
                       default="reject")

# ── A · ROUTING + SHAPE (code-enforced via the schema, proven with the canned model) ──────────────
out = su.coa(sid, _complete=canned_valid)
check("A1: a real surfaced decision ROUTES to coa and returns the up-translate bundle", out.get("id") == sid)
fs = out.get("framing_struct")
check("A2: SHAPE — framing_struct carries the plain-language MEANING (a non-empty string)",
      isinstance(fs, dict) and isinstance(fs.get("meaning"), str) and len(fs["meaning"]) > 0)
check("A3: SHAPE — framing_struct carries 2-3 value OPTIONS",
      isinstance(fs.get("options"), list) and 2 <= len(fs["options"]) <= 3)
check("A4: SHAPE — each option carries a label AND a trade-off (the value-choice shape, not raw code)",
      all(o.get("label") and o.get("tradeoff") for o in fs["options"]))
check("A5: SHAPE — framing_struct carries a RECOMMENDATION",
      isinstance(fs.get("recommendation"), str) and len(fs["recommendation"]) > 0)
check("A6: FE-CONTRACT — `framing` is a STRING (Grow.tsx renders surf.coa as text) carrying every part",
      isinstance(out.get("framing"), str)
      and fs["meaning"] in out["framing"]
      and fs["options"][0]["label"] in out["framing"]
      and fs["recommendation"] in out["framing"])

# ── B · RAW STAYS DRILLABLE (drill-down preserved on the success path) ────────────────────────────
check("B1: DRILL-DOWN — the raw payload is attached (drillable behind the altitude lead)",
      isinstance(out.get("raw"), dict) and out["raw"].get("name") == "wordcount")
check("B2: a successful framing is grounded + not degraded",
      out.get("grounded") is True and out.get("degraded") is False)

# ── C · GROUNDING GUARD (a) — ABSTAIN-ON-EMPTY (no payload → no model call → no confabulation) ─────
empty_sid = su.inbox.surface("result", {}, default="reject")   # a surfaced item with an EMPTY payload
# inject a model that, if called, would PROVE the guard failed (it must NOT be called for an empty payload).
called = {"n": 0}
def must_not_call(sys_p, user, model, base_url):
    called["n"] += 1
    return canned_valid(sys_p, user, model, base_url)
out_e = su.coa(empty_sid, _complete=must_not_call)
check("C1: ABSTAIN — an empty-payload decision does NOT call the model (no confabulation from emptiness)",
      called["n"] == 0)
check("C2: ABSTAIN — grounded=False (honestly: nothing real to frame)", out_e.get("grounded") is False)
check("C3: ABSTAIN — the framing is an HONEST 'can't frame' line, never a fabricated decision",
      isinstance(out_e.get("framing"), str) and "can't frame" in out_e["framing"].lower())
check("C4: ABSTAIN — framing_struct is None (no invented struct)", out_e.get("framing_struct") is None)
check("C5: ABSTAIN — the raw is still attached (drill-down preserved even when abstaining)",
      "raw" in out_e)

# ── D · GROUNDING GUARD (b) — DEGRADE-ON-MODEL-ABSENT (down model → legible degrade, never faked) ──
out_d = su.coa(sid, _complete=model_down)
check("D1: DEGRADE — a down/unreachable model yields a LEGIBLE 'model unavailable' framing (fail-loud)",
      isinstance(out_d.get("framing"), str) and "unavailable" in out_d["framing"].lower())
check("D2: DEGRADE — degraded=True (the surface knows the framing is not a real up-translate)",
      out_d.get("degraded") is True)
check("D3: DEGRADE — framing_struct is None (NO fabricated framing in place of the real one)",
      out_d.get("framing_struct") is None)
check("D4: DEGRADE — the raw stays DRILLABLE so the operator can still act on the real decision",
      isinstance(out_d.get("raw"), dict) and out_d["raw"].get("name") == "wordcount")

# ── E · SCHEMA IS THE BAR — a wrong-shape model output cannot pass as a framing ───────────────────
# The live path is `client.complete(schema=CoaFraming)` — it RAISES on a shape it can't validate, so coa
# degrades. We prove the SAME outcome with a stub that emits a shape coa cannot accept (raises like the
# schema-validation path would). This is the structural proof of "shape miss → degrade, not malformed prose".
def model_wrong_shape(sys_p, user, model, base_url):
    # mimic complete(schema=)'s behaviour: an output that fails schema validation RAISES (FabricError).
    from fabric.client import FabricError
    try:
        CoaFraming.model_validate({"meaning": "x"})   # missing options + recommendation → ValidationError
    except Exception as e:
        raise FabricError(f"schema validation failed: {e!r}")
out_w = su.coa(sid, _complete=model_wrong_shape)
check("E1: SCHEMA-BAR — a wrong-SHAPE model output degrades (never passed through as a framing)",
      out_w.get("degraded") is True and out_w.get("framing_struct") is None)
check("E2: SCHEMA-BAR — the raw is still attached on the schema-miss degrade",
      isinstance(out_w.get("raw"), dict))

# ── F · FAIL LOUD — a missing surfaced_id RAISES ──────────────────────────────────────────────────
raised = False
try:
    su.coa("s999-nope", _complete=canned_valid)
except KeyError:
    raised = True
check("F1: FAIL LOUD — a missing surfaced_id raises KeyError (asked to frame a thing that isn't there)",
      raised)

# ── G · FE CONTRACT (additive-only) — the keys Grow.tsx + useAppController.ts:272 read are preserved ─
# useAppController.ts:272 reads: c.id, c.raw?.name, c.raw?.code, c.framing. All present + the right types.
check("G1: FE-CONTRACT — id present (c.id)", isinstance(out.get("id"), str))
check("G2: FE-CONTRACT — raw present + a dict (c.raw?.name / c.raw?.code read off it)",
      isinstance(out.get("raw"), dict) and "name" in out["raw"] and "code" in out["raw"])
check("G3: FE-CONTRACT — framing present + a string (rendered in the grow-coa div)",
      isinstance(out.get("framing"), str))

# ── H · LIVE-PATH BACKSTOP — exercise the REAL _live_complete (client.complete + schema + json) ─────
# The A-G sections inject `_complete` and so BYPASS _live_complete's real prompt->parse->validate seam.
# That is exactly where a regression hides (the schema kwarg alone does NOT make the endpoint emit JSON;
# the prompt must request it). So here we DON'T inject `_complete` — we inject a FAKE TRANSPORT into the
# real fabric path, driving client.complete(schema=CoaFraming, json=True) end-to-end with NO live model.
# This proves: (a) a healthy model returning the CoaFraming JSON parses+validates+frames (the live SUCCESS
# path works — the regression backstop); (b) a model returning PROSE degrades clean (not passed through).
import runtime.suite as _suitemod
from fabric import transport as _transport

# (a) a fake transport that returns valid CoaFraming JSON content (what a healthy, schema-prompted model
#     emits). It asserts response_format was requested (json=True threaded → transport.py:37).
_seen = {}
def _fake_transport_json(model, messages, **opts):
    _seen["opts"] = opts
    import json as _json
    return _json.dumps({"meaning": "Live-path framing.",
                        "options": [{"label": "Opt A", "tradeoff": "gain x / lose y"},
                                    {"label": "Opt B", "tradeoff": "gain y / lose x"}],
                        "recommendation": "Pick A — it's reversible."})

_orig = _transport.openai_transport
try:
    _transport.openai_transport = lambda **kw: _fake_transport_json   # patch the fabric transport builder
    out_live = su.coa(sid)                                            # NO _complete → the REAL live path
finally:
    _transport.openai_transport = _orig
check("H1: LIVE-PATH — json=True is threaded so the endpoint is asked for a JSON object (response_format)",
      _seen.get("opts", {}).get("json") is True)
check("H2: LIVE-PATH — a healthy model's CoaFraming JSON parses+validates+frames (the SUCCESS path WORKS, "
      "not a perpetual degrade — the regression backstop)",
      out_live.get("degraded") is False and out_live.get("grounded") is True
      and isinstance(out_live.get("framing_struct"), dict)
      and out_live["framing_struct"]["meaning"] == "Live-path framing.")
check("H3: LIVE-PATH — the framing string carries the recommendation (FE-renderable)",
      "Pick A" in (out_live.get("framing") or ""))

# (b) a fake transport that returns PROSE (what an UN-prompted model would emit) → _parse fails → retries
#     → FabricError → coa DEGRADES (never passes prose through as a framing). retries=1 keeps the test fast.
def _fake_transport_prose(model, messages, **opts):
    return "Here is my prose analysis of the decision, with no JSON whatsoever."
def _complete_prose(sys_p, usr, model, base_url):
    from fabric import client
    return client.complete(_fake_transport_prose, [{"role": "user", "content": usr}],
                           model=model, schema=CoaFraming, json=True, retries=1, sleep=lambda *_: None)
out_prose = su.coa(sid, _complete=_complete_prose)
check("H4: LIVE-PATH — a PROSE (non-JSON) model output degrades clean (never passed through as a framing)",
      out_prose.get("degraded") is True and out_prose.get("framing_struct") is None
      and isinstance(out_prose.get("raw"), dict))

print(f"\n{PASS} checks PASSED — coa up-translate organ proven by use (structure + grounding guard + "
      "degrade + fail-loud + LIVE-PATH parse/validate backstop), model-free. WORDING-QUALITY flagged "
      "model-dependent (only the actual model wording needs a live model).")
