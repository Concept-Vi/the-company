"""tests/no_confidence_acceptance.py — the NO-CONFIDENCE INVARIANT (G16 · Tim's standing law).

Tim, 2026-06-09: **"No confidence, tags and counts."** + **"Enforce, don't convention."** This suite is the
ENFORCEMENT (not a per-role cleanup): it walks EVERY file-discovered role's output_schema (and every nested
Pydantic sub-model reachable from it) and FAILS LOUD if any field is named `confidence`. Evidence is tags +
counts + structured observations — never a probability float that pretends at precision (PRINCIPLE-tags-
counts-temporal.md §1). A new role that ships a `confidence` field can no longer pass the gate — the law is
a standing invariant, caught at the registry boundary, not left to reviewer vigilance.

Registry-is-truth: the walk is over RoleRegistry().discover(["roles"]) — drop a role with a confidence
field and this goes RED; migrate it to a tag/count and it goes green. Model-free, deterministic.
"""
import os
import sys
from typing import get_args

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from pydantic import BaseModel              # noqa: E402
from runtime.roles import RoleRegistry      # noqa: E402

PASS = 0


def check(msg, cond):
    global PASS
    assert cond, f"FAIL: {msg}"
    PASS += 1
    print(f"  ok  {msg}")


def _models_in(annotation):
    """BaseModel subclasses reachable from a type annotation: X · list[X] · Optional[X] · dict[_, X] · etc."""
    out = []

    def rec(a):
        if isinstance(a, type) and issubclass(a, BaseModel):
            out.append(a)
            return
        for arg in get_args(a):
            rec(arg)

    rec(annotation)
    return out


def confidence_fields(schema):
    """Every field path named `confidence` (case-insensitive) in `schema` + its nested sub-models."""
    hits, seen = [], set()

    def walk(model, prefix):
        if not (isinstance(model, type) and issubclass(model, BaseModel)) or model in seen:
            return
        seen.add(model)
        for name, f in model.model_fields.items():
            if name.lower() == "confidence":
                hits.append(f"{prefix}{name}")
            for sub in _models_in(f.annotation):
                walk(sub, f"{prefix}{name}.")

    walk(schema, "")
    return hits


print("NO-CONFIDENCE INVARIANT (G16 — Tim: 'no confidence, tags and counts; enforce, don't convention')")
rr = RoleRegistry().discover(["roles"])

violations, checked = {}, 0
for rid, role in sorted(rr.roles.items()):
    sch = role.output_schema
    if sch is None:                        # an embed role / config-only role has no output_schema — skip
        continue
    checked += 1
    hits = confidence_fields(sch)
    if hits:
        violations[rid] = hits

check(f"walked {checked} fireable role output-schemas (+ nested sub-models) — registry-is-truth", checked > 0)
check(f"NO role output_schema carries a `confidence` field — the law is enforced (violations: {violations})",
      not violations)

print(f"\nALL {PASS} CHECKS PASS — no-confidence is a STANDING INVARIANT "
      f"({checked} role schemas clean; tags+counts, never a confidence float)")
