"""runtime/resolver.py — THE RESOLVER (the 4th primitive: rules-computation, the VERB).

`resolve(invariant, coordinate) → concrete` — a PURE function. You never store a variant; every concrete
surface/value is COMPUTED on demand from ONE invariant + where-you-are (the coordinate). This is the
"express RELATIONSHIPS, not CASES" discipline (build-prep/the-one-application/RESOLVER-BUILD.md): each output
is a relationship over the coordinate's axes, evaluated here — NOT a hand-written breakpoint/variant.

The engineering reason this exists (stand on THIS, not on any unread-vault claim): today's responsive layout
ENUMERATES cases (`@media (max-width:600px)` = building variants by hand). The resolver makes screen-size (and
every axis) a ROOT VARIABLE and DERIVES each dimension from it by rule — so portrait/landscape/desktop fall out
of evaluating ONE definition at each device-coordinate. Define the relationship once → all coordinates at once.

REUSE-DON'T-PARALLEL: the relationship evaluator IS `runtime.rules.evaluate` (the same validated, PURE,
deterministic data-AST engine the `rule` tool uses — add/sub/mul/div/min/max/clamp/field/lit/comparisons). The
resolver does NOT reimplement evaluation; it holds the per-slot invariant and calls rules.evaluate per slot
against the coordinate. (The layout-allocation op `clamp` was added to rules.py for this — a dimension held
within available space is a relationship, not a breakpoint.)

THE TWO AXIS-KINDS (RESOLVER-BUILD refinement #1 — honored in the SHAPE here; the axis SET stays Tim's call):
  • CONTINUOUS axis (size · detail · warmth) → resolve by DERIVATION: the slot's value is a relationship-AST
    over the coordinate (e.g. height = clamp(device.h * 0.4, 80, device.h - chrome)). evaluate() computes it.
  • DISCRETE/categorical axis (medium incl. voice · viewer · mode · type · posture · preference) → resolve by
    REGISTRY-SELECTION: the slot declares {select: <coordinate-path>, cases: {value: result}, default?} — a
    row-lookup that PICKS a result by the coordinate's value (also NOT a hand-enumerated variant — it's a
    declared mapping resolved by where-you-are). Category-error guard: voice is not a continuous function of
    width; it's a discrete medium selecting a render-family.

PURE + FAIL-LOUD: identical (invariant, coordinate) → identical output, no IO/time/random (rules.evaluate's
guarantee). A malformed slot RAISES at resolve (never a silent skip / silent default). The floor: a computation
— emits NO resolve/approve/dispatch.
"""
from __future__ import annotations

from typing import Any

from runtime import rules


class ResolverError(ValueError):
    """A malformed invariant slot (fail-loud at resolve) — never a silently-wrong allocation."""


def resolve_slot(slot: Any, coordinate: dict) -> Any:
    """Resolve ONE invariant slot against the coordinate. A slot is either:
      • a relationship-AST dict (has an "op") → CONTINUOUS: rules.evaluate(ast, coordinate).
      • a select dict {"select": <dot-path>, "cases": {..}, "default"?: ..} → DISCRETE: pick by the
        coordinate's value at <dot-path>; fail-loud if the value isn't a case and no default given.
      • a plain literal (int/float/str/bool/None) → returned as-is (a fixed value is a degenerate relationship).
    """
    if isinstance(slot, dict) and "op" in slot:
        return rules.evaluate(slot, coordinate)                # CONTINUOUS — derive via the relationship
    if isinstance(slot, dict) and "select" in slot:            # DISCRETE — registry-select by coordinate value
        cases = slot.get("cases")
        if not isinstance(cases, dict) or not cases:
            raise ResolverError(f"resolve: a select-slot needs a non-empty 'cases' dict; got {slot!r}. Fail loud.")
        key = rules._get_path(coordinate, slot["select"])      # reuse the SAME dot-path reader rules.field uses
        if key in cases:
            return cases[key]
        if "default" in slot:
            return slot["default"]
        raise ResolverError(
            f"resolve: select on {slot['select']!r} got value {key!r} not in cases {list(cases)} and no "
            f"'default' — fail loud (never a silent wrong render-family).")
    if isinstance(slot, dict):
        raise ResolverError(
            f"resolve: a dict slot must be a relationship-AST (has 'op') or a select ('select'/'cases'); "
            f"got keys {list(slot)}. Fail loud.")
    return slot                                                # a literal — fixed value (degenerate relationship)


def resolve(invariant: dict, coordinate: dict) -> dict:
    """Resolve a whole invariant (a dict of {slot_name: slot}) against the coordinate → {slot_name: value}.
    PURE. The ONE operation behind a computed surface: feed the SAME invariant a different coordinate
    (e.g. {device:{w:390,h:844}} vs {device:{w:844,h:390}}) and the allocation RE-DERIVES — no breakpoint,
    no stored variant. A malformed slot RAISES (the whole resolve fails loud — never a partial silent result)."""
    if not isinstance(invariant, dict):
        raise ResolverError(f"resolve: invariant must be a dict {{slot: relationship}}, got {type(invariant).__name__}.")
    if not isinstance(coordinate, dict):
        raise ResolverError(f"resolve: coordinate must be a dict {{axis: value}}, got {type(coordinate).__name__}.")
    return {name: resolve_slot(slot, coordinate) for name, slot in invariant.items()}


if __name__ == "__main__":
    # run via:  python -m runtime.resolver   (package context, so `from runtime import rules` resolves)
    # OPERATIONAL self-test — proves the MECHANISM (relationship-derivation + registry-select + fail-loud).
    # The REAL keystone-landscape proof (projection's actual merge-sa component heights fitting at 844×390)
    # is verified WITH projection on their real numbers — this bar proves the primitive computes, not that a
    # specific surface fits (that's the by-use-on-real-data step, never a self-confirm).
    # ONE invariant; TWO device-coordinates → two DIFFERENT derived allocations from one definition.
    INVARIANT = {
        # CONTINUOUS: the header is 40% of available height, but never below 80px and never past (h - 56 chrome).
        "header_h": {"op": "clamp",
                     "args": [{"op": "mul", "args": [{"op": "field", "path": "device.h"}, {"op": "lit", "value": 0.4}]},
                              {"op": "lit", "value": 80},
                              {"op": "sub", "args": [{"op": "field", "path": "device.h"}, {"op": "lit", "value": 56}]}]},
        # CONTINUOUS: the body takes the rest (available height minus header minus the 56 chrome).
        "body_h":   {"op": "sub",
                     "args": [{"op": "sub", "args": [{"op": "field", "path": "device.h"}, {"op": "lit", "value": 56}]},
                              {"op": "clamp",
                               "args": [{"op": "mul", "args": [{"op": "field", "path": "device.h"}, {"op": "lit", "value": 0.4}]},
                                        {"op": "lit", "value": 80},
                                        {"op": "sub", "args": [{"op": "field", "path": "device.h"}, {"op": "lit", "value": 56}]}]}]},
        # DISCRETE: stack direction selects by orientation (a render-family pick, not a continuous function).
        "stack":    {"select": "device.orient", "cases": {"portrait": "column", "landscape": "row"}, "default": "column"},
    }
    portrait = resolve(INVARIANT, {"device": {"w": 390, "h": 844, "orient": "portrait"}})
    landscape = resolve(INVARIANT, {"device": {"w": 844, "h": 390, "orient": "landscape"}})
    assert portrait["header_h"] == max(80, min(844 * 0.4, 844 - 56)) == 337.6, portrait
    assert landscape["header_h"] == max(80, min(390 * 0.4, 390 - 56)) == 156.0, landscape
    assert portrait["stack"] == "column" and landscape["stack"] == "row", (portrait, landscape)
    # the allocation DIFFERS by coordinate from ONE definition (no breakpoint), and body+header+chrome == h (fits).
    for c, alloc in (("portrait", portrait), ("landscape", landscape)):
        h = {"portrait": 844, "landscape": 390}[c]
        assert abs(alloc["header_h"] + alloc["body_h"] + 56 - h) < 1e-9, (c, alloc)
    # fail-loud: a select with no matching case + no default RAISES.
    try:
        resolve({"x": {"select": "device.orient", "cases": {"portrait": 1}}}, {"device": {"orient": "landscape"}})
        raise SystemExit("FAIL: select with no case/default did not raise")
    except ResolverError:
        pass
    # fail-loud: div by zero RAISES (through rules.evaluate).
    try:
        resolve({"x": {"op": "div", "args": [{"op": "lit", "value": 1}, {"op": "lit", "value": 0}]}}, {})
        raise SystemExit("FAIL: div-by-zero did not raise")
    except rules.RuleError:
        pass
    print("resolver OPERATIONAL self-test: ALL PASS "
          "(continuous-derivation · clamp-allocation · discrete registry-select · fits-by-coordinate · fail-loud)")
