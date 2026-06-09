"""roles/confirm_registration.py — the CONFIRM role (Registry-Generation chain · RG6 · the gate).

The two-layer no-fiction / accuracy gate that sits between REDUCE (RG5) and PROPOSE (RG8): it gates the
reconciled dossier set for ACCURACY + NO-FICTION before any of it is proposed to the operator. It is the
engine-depth half cognition owns (the C lane); it MIRRORS roles/verify_jury.py exactly — a Pydantic draw
class + a self-registering module-level ROLE dict declaring `draws: N>1` + a callable `verdict_rule` —
and is fired by run_jury (runtime/cognition.py, read-only). NEW file, file-disjoint: roles/ is the C seam.

────────────────────────────────────────────────────────────────────────────────────────────────────────
★ THE KEY DESIGN — TWO LAYERS, because a single-4B jury measures VARIANCE, not ERROR.

The no-fiction guarantee MUST NOT rest on the model. So the gate is two independent layers, and the
deterministic one is the guarantee:

  LAYER 1 — the DETERMINISTIC no-fiction FLOOR (the real ERROR gate, model-independent).
      design/_system/refcheck.py :: check_dossier(dossier) — ALREADY BUILT (LAW 0 unification — we REUSE
      it, we do NOT write a second checker). Per dossier, with NO model: (a) every capability ∈ the
      canonical capability vocabulary (contracts/ui_info — UNKNOWN string = fabrication = FAIL); (b)
      maps_to_feature ∈ register.json features[].id ∪ {"proposed"} (invented id = FAIL); (c) any code ref
      resolves to a real file/symbol (the existing _check_one_ref dispatch). Deterministic: the SAME
      dossier always yields the SAME verdict — it catches FABRICATION regardless of model strength. A
      dossier that FAILS here is FLAGGED, never dropped, never proposed-as-confirmed. This is the floor
      that bites EVEN IF the jury wavers.

  LAYER 2 — the ACCURACY jury (the SOFT judgment on top — THIS role).
      A JURY role (draws=N>1 + a callable verdict_rule), MIRRORING verify_jury.py. Each draw is shown the
      PROPOSED dossier AND the ELEMENT it claims to represent, and judges ONE boolean: is the dossier
      GROUNDED in the element — i.e. is `represents` accurate to what the element actually is, and is the
      `howto` (what / what_you_can_do / how_to_change) honest to the element, with no invented capability?
      The N draws measure AGREEMENT. The verdict_rule is a PURE deterministic QUORUM over the draws (L2 —
      no model in the rule; the model runs only INSIDE a draw), MIRRORING verify_jury.majority_vote.

  THE COMBINE (the two-layer AND) — confirm_status(), a PURE function below:
      confirmed  ⟺  quorum-agree on grounded==true  AND  refcheck.passed==true
      else       →  FLAGGED (never dropped — variance-not-error → flag; error → flag too).
      The final AND is expressed as a DECLARED RULE_OPS data-AST (runtime/rules.py evaluate — registry-is-
      truth / no-hardcoding: the combine is declared data, not a hand-written Python `and`). The QUORUM
      over the variable-length draw list is the callable verdict_rule (RULE_OPS has no aggregation op, so
      the quorum cannot be an AST — it is the jury's pure callable, exactly as verify_jury's is).

⚠ E4 EPISTEMIC-MONOCULTURE CAVEAT (the binding caveat, inherited from verify_jury.py): N draws on ONE 4B
are N CORRELATED samples — they measure the model's VARIANCE, not INDEPENDENT error. So Layer 2 is SOFT:
it does NOT prove a semantic catch. The no-fiction GUARANTEE is Layer 1 (deterministic). Layer 2 raises
confidence + flags low-agreement; it is honestly variance-prone, never the floor. The jury MAY bind a
stronger model from the widened catalog (C2.5 / models_for_role) when a GPU window permits — an
ENHANCEMENT toward independent error, never a requirement (Layer 1 already guarantees no-fiction on the
4B alone). The verdict_rule call shape (list[draw dict] → verdict dict) is the same slot-in point
verify_jury documents: a future per-draw `provider` can weight/tiebreak across MODELS without changing it.

NOT in any mode_scope (a gate fired explicitly via run_jury over the reconciled set, not part of a
listening cast) — adding it does NOT change the listening cast. draws=3.
"""
from pydantic import BaseModel


# =================================================================================================
# LAYER 1 reuse: the deterministic no-fiction floor lives in design/_system/refcheck.py (check_dossier).
# refcheck.py is under design/_system (not on the default import path) — add the design/_system dir so we
# REUSE the existing checker rather than re-spell it (LAW 0 — one checker, no parallel). READ-ONLY import.
# =================================================================================================
import os as _os                                                                       # noqa: E402
import sys as _sys                                                                      # noqa: E402
_SYS_DIR = _os.path.join(_os.path.expanduser("~/company"), "design", "_system")
if _SYS_DIR not in _sys.path:
    _sys.path.insert(0, _SYS_DIR)
from refcheck import check_dossier  # noqa: E402  — LAYER 1, the deterministic floor (REUSED, not forked)


# =================================================================================================
# LAYER 2 — the draw output + the pure quorum verdict_rule (MIRRORS verify_jury.py exactly).
# =================================================================================================
class ConfirmOut(BaseModel):
    """One draw of the confirm jury: is the proposed dossier GROUNDED in the element it claims to
    represent? A boolean + a one-line reason — the SAME clean-count shape verify_jury.VerifyOut uses
    (so the quorum is a simple count), specialised to the registration accuracy judgement."""
    grounded: bool   # true ⟺ `represents` is accurate to the element AND `howto` is honest to it (no fiction)
    reason: str      # a one-line reason (what the draw saw that made it grounded / not)


# The QUORUM threshold for "the jury agrees it is grounded". A strict MAJORITY of the draws must say
# grounded==true (a tie or a minority → not-quorum → FLAGGED). Declared as a constant so the threshold is
# visible data, not buried in the function (drift-home: roles/AGENTS.md — the jury section).
def quorum_grounded(draws: list[dict]) -> dict:
    """The VERDICT rule — a PURE deterministic QUORUM over the N draws (L2). Each draw is a resolved
    ConfirmOut dict ({grounded, reason}). Returns {verdict: bool, votes_grounded, votes_ungrounded, n,
    unanimous, quorum}. Deterministic: the SAME set of draws always yields the SAME verdict regardless of
    the order they finished in (it COUNTS; it does not depend on arrival order — C0.2/H7 scope: the draws
    are intentionally varied, the verdict over them is deterministic).

    QUORUM = a strict MAJORITY say grounded==true (votes_grounded > votes_ungrounded). A jury that SPLITS
    or LEANS not-grounded does NOT reach quorum → the dossier is FLAGGED (variance-not-error → flag). This
    cannot be a RULE_OPS data-AST: RULE_OPS has no aggregation/count op over a variable-length list, so the
    quorum is the jury's PURE callable (exactly as verify_jury's majority_vote is) — NOT a new mechanism.

    E4 slot-in point (verify_jury's): `draws` could later carry a per-draw `provider` so a future verdict
    weights/tiebreaks across MODELS (independent error) rather than counting correlated same-model samples.
    The call shape (a list of draw dicts → a verdict dict) does not change."""
    votes_grounded = sum(1 for d in draws if d.get("grounded") is True)
    votes_ungrounded = len(draws) - votes_grounded
    quorum = votes_grounded > votes_ungrounded                 # strict majority — a tie does NOT pass
    return {"verdict": quorum, "votes_grounded": votes_grounded,
            "votes_ungrounded": votes_ungrounded, "n": len(draws),
            "unanimous": votes_grounded == len(draws) or votes_ungrounded == len(draws),
            "quorum": quorum}


# =================================================================================================
# THE TWO-LAYER COMBINE — confirm_status(): the PURE function refcheck.py names as "the caller" (line
# 368). It ANDs the Layer-1 deterministic floor with the Layer-2 jury verdict. PURE: it runs check_dossier
# internally (no model — deterministic) and ANDs with the jury verdict PASSED IN (it does NOT call
# run_jury — that needs store/turn_id/the engine; the driver/cascade runs the jury and hands the verdict
# here). The final AND is a DECLARED RULE_OPS data-AST evaluated by runtime/rules.py (registry-is-truth /
# no-hardcoding — the combine is declared data, not a hand-written Python `and`).
# =================================================================================================
# The DECLARED two-layer AND rule (a RULE_OPS data-AST — the closed grammar, never eval/exec). It reads
# two resolved fields and ANDs them: the jury reached quorum AND the deterministic floor passed. This is
# the one place the spec's "RULE_OPS — a pure AST" instruction lands (the QUORUM itself is the callable
# verdict_rule above; the COMBINE is this AST). Drift-home for the op-set: runtime/AGENTS.md.
CONFIRM_RULE_AST = {
    "op": "and",
    "args": [
        {"op": "field", "path": "jury.verdict"},       # Layer 2: quorum-agree on grounded==true
        {"op": "field", "path": "refcheck.passed"},    # Layer 1: the deterministic no-fiction floor passed
    ],
}


def confirm_status(dossier: dict, jury_verdict: dict, *, feature_ids=None, bridge_lines=None) -> dict:
    """The CONFIRM verdict for ONE reconciled dossier — the two-layer gate, PURE + model-independent.

    Args:
      dossier       — a register_element output (RG3): {address, represents, howto, capabilities[],
                      maps_to_feature, confidence, code?}.
      jury_verdict  — the Layer-2 jury verdict dict from run_jury(confirm_registration, ...).verdict,
                      i.e. quorum_grounded()'s output ({verdict: bool, votes_grounded, ...}). PASSED IN
                      (this function does NOT fire the jury — the driver/cascade does, then hands it here).
      feature_ids / bridge_lines — optional pre-loaded inputs threaded straight through to check_dossier
                      (so a batch can load the inventory + bridge.py ONCE and reuse them across N dossiers).

    Returns {confirmed: bool, status: "confirmed"|"FLAGGED", refcheck: {...}, jury: {...}, reasons: [str]}.

    confirmed ⟺ refcheck.passed (Layer 1, deterministic floor) AND jury.verdict (Layer 2, quorum). The AND
    is the DECLARED CONFIRM_RULE_AST evaluated by runtime/rules.evaluate (NOT a hand-written `and`). FLAG,
    never drop: a False on EITHER layer → status "FLAGGED" (variance-not-error → flag; error → flag too).
    The deterministic floor BITES even if the jury waved confirmed (the no-fiction guarantee does not rest
    on the model). PURE: no model call, no IO beyond check_dossier's READ-ONLY source resolution."""
    from runtime.rules import evaluate                      # lazy — stdlib + rules.py only, no import cycle

    if not isinstance(jury_verdict, dict) or "verdict" not in jury_verdict:
        raise ValueError(
            f"confirm_status: jury_verdict must be a verdict dict with a 'verdict' key (quorum_grounded's "
            f"output), got {jury_verdict!r} — fail loud (a confirm cannot guess the jury's verdict).")

    # LAYER 1 — the deterministic floor (REUSED check_dossier; it FLAGs on fabrication regardless of model).
    floor = check_dossier(dossier, feature_ids=feature_ids, bridge_lines=bridge_lines)

    # THE COMBINE — the declared RULE_OPS AST over the two resolved layer-results (registry-is-truth).
    resolved = {"jury": {"verdict": bool(jury_verdict.get("verdict"))},
                "refcheck": {"passed": bool(floor.get("passed"))}}
    confirmed = bool(evaluate(CONFIRM_RULE_AST, resolved))   # pure data-AST AND — never eval/exec

    reasons: list = []
    if not floor.get("passed"):
        # Layer-1 reasons are the no-fiction failures (capability/feature/code fabrication) — the floor bit.
        reasons.extend(f"refcheck (Layer 1, deterministic floor): {r}" for r in floor.get("reasons", []))
    if not jury_verdict.get("verdict"):
        reasons.append(
            f"accuracy jury (Layer 2, SOFT — variance not error): no quorum that the dossier is grounded "
            f"in the element ({jury_verdict.get('votes_grounded')} of {jury_verdict.get('n')} draws "
            f"agreed grounded). Flagged for operator scrutiny.")

    return {"confirmed": confirmed, "status": "confirmed" if confirmed else "FLAGGED",
            "refcheck": floor, "jury": jury_verdict, "reasons": reasons}


# =================================================================================================
# THE ROLE — the JURY (draws=3 + the callable verdict_rule). MIRRORS verify_jury.py's ROLE shape exactly.
#   Each draw SEES BOTH the dossier AND the element it claims to represent (input_addresses carry both) —
#   without the element, "grounded" judges the dossier against nothing and Layer 2 is theatre. The draw
#   reads them as labelled inputs (the run_role utterance + declared extra-input path register_element
#   rides) and returns the ConfirmOut boolean. run_jury fires N varied draws (temperature>0) → distinct
#   per-draw run:// addresses → the PURE quorum verdict_rule decides. (The full two-layer combine — AND
#   with the refcheck floor — is confirm_status() above, which the cascade/driver invokes around the jury;
#   the jury OWNS Layer 2 only, by design, so the deterministic floor is never inside the model path.)
# =================================================================================================
ROLE = {
    "id": "confirm_registration",
    "label": "Confirm registration (accuracy jury)",
    "description": (
        "Layer 2 of the RG6 confirm gate: a jury that judges whether a PROPOSED registry dossier is "
        "GROUNDED in the element it claims to represent — `represents` accurate, `howto` honest, no "
        "invented capability. N varied draws → a deterministic quorum verdict (SOFT — variance not error; "
        "the no-fiction GUARANTEE is the deterministic refcheck floor, Layer 1). FLAGs, never drops."
    ),
    "prompt_template": (
        "You are a member of a REGISTRATION CONFIRM JURY. You are shown a PROPOSED REGISTRY DOSSIER for "
        "ONE element of a design mockup, AND the ELEMENT it claims to represent (its visible text, "
        "tag/role, and a bounded HTML snippet). The dossier is what the system would tell a NON-DEVELOPER "
        "operator about that element. Your ONE job: decide whether the dossier is GROUNDED in the element "
        "— i.e. is `represents` ACCURATE to what the element actually is, and is the `howto` (what it is / "
        "what you can do / how to change it) HONEST to the element, with NO invented capability or "
        "feature? Judge the dossier AGAINST the element — read the element as a person SEES the screen, "
        "not as code.\n"
        "\n"
        "Be strict: if the dossier describes something the element plainly is NOT (a label called a "
        "button, a static heading described as a control, a capability the element cannot have), it is "
        "NOT grounded. If the element is genuinely what the dossier says, it IS grounded.\n"
        "\n"
        "Return ONLY JSON with two fields:\n"
        '  "grounded": a boolean — true if the dossier is accurate + honest to the element, false otherwise,\n'
        '  "reason": a one-line reason citing what in the element made you decide.\n'
        'Example: {"grounded": true, "reason": "the element is an Approve button and `represents` says '
        '\'approve the decision\' — accurate, and the howto matches what a button does."}'
    ),
    "output_schema": ConfirmOut,
    # THE SEAM — the draw must SEE both the dossier AND the element (else "grounded" judges nothing):
    #   "utterance"       → the PROPOSED dossier under judgement (the driver/cascade places it here, the
    #                       way run_items places each unit at ctx["utterance"]).
    #   "element"         → the ELEMENT the dossier claims to represent (its snippet/text/tag — the SAME
    #                       candidate-unit context register_element was given, so the jury judges the
    #                       dossier against the very thing it was made from). Delivered as a labelled extra
    #                       input (run_role composes utterance + declared extra inputs into the user msg).
    "input_addresses": ("utterance", "element"),
    "trigger": (
        "fired explicitly as a jury (run_jury) over each reconciled dossier in the RG6 CONFIRM step — its "
        "verdict is ANDed with the deterministic refcheck floor by confirm_status() to gate the set before "
        "it is proposed to the operator (RG8)."
    ),
    # C2.5 capability-query: a confirm draw wants a chat/json model. default_model None keeps the safe
    # floor = the resident brain (the 4B). A STRONGER model from the widened catalog (models_for_role) MAY
    # bind here as an ENHANCEMENT toward independent error when a GPU window permits — never a requirement
    # (Layer 1 already guarantees no-fiction on the 4B alone; this is Tim-fork F-a, the E4 mitigation path).
    "model_binding": {"requires": ["chat", "json"], "default_model": None, "default_base_url": None},
    # NO mode_scope → in no listening cast (a gate fired explicitly via run_jury, not part of listening).
    "draws": 3,                          # C2.4 / C1.5 — N varied draws (per-draw key → distinct addresses)
    "verdict_rule": quorum_grounded,     # PURE deterministic QUORUM over the draws (L2 — no model in rule)
    "rules": [
        {"id": "confirm-verdict", "reads": "confirm_registration.draws",
         "effect": "quorum_grounded over the N draws → a deterministic grounded-verdict (Layer 2)",
         "kind": "verdict"},
    ],
    "render_hint": {"shape": "jury", "lane": "confirm", "draws": 3},
}
