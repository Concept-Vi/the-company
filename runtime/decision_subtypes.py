"""runtime/decision_subtypes.py — the file-discovered DECISION-SUBTYPE registry (the decision FORMED right).

A DECISION-SUBTYPE is the KIND of a decision that determines HOW it's FORMED INTO CONTENT for the operator:
which CARD-VARIANT renders it (the elements/layout — DNA's lane) and which EXPLANATION-POLICY the RHM explains
it through (the regime — fork's generation_policies). One knob (decision.subtype) → both halves resolve. The
subtype the decision row declares is the discriminator; render resolves the variant, explain resolves the policy.

## DERIVED, never invented (Tim's law)
The subtype VOCABULARY DERIVES from the real pending decisions (the DECISION-GATHER) by clustering — the kinds
+ each kind's required elements FALL OUT of the actual set. Seeded from the first gather (2026-06-21, 16+
decisions: composition C1-6 · fork F1-6 · lead L1-4 · DNA D1-4 · corpus). REFINE as the set grows (a decision
of a new shape — ranking/allocation/workflow, DNA's unbuilt variant candidates — adds a ROW, never a code edit).

## The subtype schema — each `decision_subtypes/<id>.py` declares `DECISION_SUBTYPE` (a ROW):
  - id                 — required; MUST equal the module name (addressable by file — fail-loud otherwise).
  - card_variant       — required; the variant the decision-card renders for this kind (DNA's variant vocabulary:
                         binary · n-panel · … — variant.schema / dna layouts). The decision row resolves THIS.
  - explanation_policy — required; a generation_policies id (fork) — the REGIME the RHM explains this kind through
                         (run_role(policy=…)). Theorem-grounding ≠ risk-grounding ≠ trade-off-neutral.
  - required_elements  — optional; the elements this kind's card MUST carry (drives the decoration-ban + the
                         render — a card missing a required element fails the bar). DERIVED from the kind's need.
  - desc               — optional; operator-facing one-liner (+ which gathered decisions it covers).
A malformed entry FAILS LOUD at discovery.

## How it resolves (the chain): decision.subtype → this row → (a) card_variant [DNA renders] · (b)
explanation_policy [fork's run_role] · (c) required_elements [the gate checks]. card_variant is DNA's render
vocabulary (meet-at-the-contract); explanation_policy is fork's generation_policies (meet-at-the-contract).

LAWS honoured: no-hardcoding (subtypes FILE-DISCOVERED, derived) · reuse-don't-parallel (mirrors AxisRegistry/
StackItemTypeRegistry — the ONE mechanism) · fail loud · the floor (reading a subtype is a READ).
"""
from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass


DECISION_SUBTYPE_FIELDS = ("id", "card_variant", "explanation_policy", "required_elements", "desc")
REQUIRED_FIELDS = ("id", "card_variant", "explanation_policy")


@dataclass
class DecisionSubtype:
    """A discovered decision-subtype — the declared dict (`spec`) verbatim + typed accessors. card_variant →
    DNA's render; explanation_policy → fork's run_role regime; required_elements → the gate."""
    id: str
    card_variant: str
    explanation_policy: str
    spec: dict

    @property
    def required_elements(self) -> list:
        return list(self.spec.get("required_elements") or [])

    @property
    def desc(self):
        return self.spec.get("desc")


def _load_module(path: str):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(f"_ds_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return name, mod


def _build_decision_subtype(name: str, decl: dict) -> DecisionSubtype:
    """Validate + build a DecisionSubtype. FAIL LOUD on a malformed entry (mirrors _build_axis)."""
    if not isinstance(decl, dict):
        raise TypeError(f"decision-subtype module {name!r}: DECISION_SUBTYPE must be a dict, got {type(decl).__name__} — fail loud.")
    sid = decl.get("id")
    if not sid or not isinstance(sid, str):
        raise ValueError(f"decision-subtype module {name!r}: declares no string `id` — fail loud (never unnamed).")
    if sid != name:
        raise ValueError(
            f"decision-subtype module {name!r}: id {sid!r} != module name {name!r} — id must equal the file name. Fail loud.")
    unknown = [k for k in decl if k not in DECISION_SUBTYPE_FIELDS]
    if unknown:
        raise ValueError(f"decision-subtype {sid!r}: unknown field(s) {unknown} — schema is {list(DECISION_SUBTYPE_FIELDS)}. Fail loud.")
    cv = decl.get("card_variant")
    if not cv or not isinstance(cv, str):
        raise ValueError(f"decision-subtype {sid!r}: `card_variant` must be a non-empty string (DNA's variant id). Fail loud.")
    ep = decl.get("explanation_policy")
    if not ep or not isinstance(ep, str):
        raise ValueError(f"decision-subtype {sid!r}: `explanation_policy` must be a non-empty string (a generation_policies id). Fail loud.")
    re = decl.get("required_elements")
    if re is not None and (not isinstance(re, list) or not all(isinstance(x, str) for x in re)):
        raise ValueError(f"decision-subtype {sid!r}: `required_elements` (when present) must be a list of strings. Fail loud.")
    return DecisionSubtype(id=sid, card_variant=cv, explanation_policy=ep, spec=dict(decl))


class DecisionSubtypeRegistry:
    """The file-discovered DECISION-SUBTYPE registry — mirrors AxisRegistry's mechanism (the ONE registry
    mechanism), own row shape. Dict-like. Adding a subtype = dropping a `decision_subtypes/<id>.py`."""

    def __init__(self):
        self.subtypes: dict[str, DecisionSubtype] = {}

    def discover(self, dirs: list[str]) -> "DecisionSubtypeRegistry":
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                name, mod = _load_module(os.path.join(d, fn))
                decl = getattr(mod, "DECISION_SUBTYPE", None)
                if decl is None:
                    continue
                self.register(name, decl)
        return self

    def rediscover(self, dirs: list[str]) -> "DecisionSubtypeRegistry":
        self.subtypes.clear()
        return self.discover(dirs)

    def register(self, name: str, decl: dict) -> None:
        self.subtypes[name] = _build_decision_subtype(name, decl)

    def as_records(self) -> list[dict]:
        return [dict(self.subtypes[k].spec) for k in sorted(self.subtypes)]

    # --- dict-like ---
    def __getitem__(self, sid: str) -> DecisionSubtype:
        return self.subtypes[sid]

    def __contains__(self, sid: str) -> bool:
        return sid in self.subtypes

    def __iter__(self):
        return iter(self.subtypes)

    def __len__(self) -> int:
        return len(self.subtypes)

    def get(self, sid: str, default=None):
        return self.subtypes.get(sid, default)
