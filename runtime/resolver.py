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


# ── THE LADDER slot-kind (④ THE CONTAINER · L7-KEEPER, organ-studies/KEEPER.md §4.2) ─────────────
# The THIRD axis-kind (beside CONTINUOUS-derivation and DISCRETE-select): CONTAINMENT. A value that
# inherits DOWN a containment ladder — universal → space → project → scope — resolving to the DEEPEST
# rung whose address is a containment-prefix of the coordinate's address (walk UP on absence). This is
# the cloud's `keeper_agent_config.override_level` (0=global,1=space,2=project,3=scope) re-expressed as
# ONE pure resolver slot: **override_level WAS containment depth in disguise — the ADDRESS is the level**
# (ci_resolve_keeper_config's `ORDER BY override_level DESC LIMIT 1` == longest-prefix-wins here). Keeper
# config, per-project role framing, and token values (theme/archetype/autonomy/response_style) ALL
# resolve through this ONE mechanism — NOT a second resolver (reuse-don't-parallel, the ONE-ladder law).
#
# Shape:  {"ladder": "<dot-path to the address on the coordinate>",   # e.g. "address"
#          "rungs":  {"": v0,                        # universal   (cloud level 0) — matches EVERY address
#                     "space://x": v1,               # space       (1)
#                     "project://x/y": v2,            # project     (2)
#                     "project://x/y#scope": v3},     # scope       (3)
#          "default"?: v}                             # optional final fallback (below the shallowest rung)
#
# A rung key K MATCHES address A iff K == "" (universal) OR A == K OR A starts with K at a containment
# BOUNDARY ('/' or '#' — so "project://x" matches "project://x#s" and "project://x/y", NEVER "project://xy").
# Deepest (longest) matching rung wins. No match + no default → fail loud (a legible absent + breadcrumb),
# NEVER a silent wrong rung (the resolver's PURE + FAIL-LOUD contract).
def _rung_matches(rung: str, address: str) -> bool:
    """Does containment-rung `rung` cover `address`? "" = universal (covers all); else exact OR a
    containment-prefix ending at a boundary char ('/' or '#'). Prefix WITHOUT a boundary is NOT a match
    (so 'project://x' never spuriously covers 'project://xy')."""
    if rung == "":
        return True
    if address == rung:
        return True
    return address.startswith(rung) and address[len(rung):len(rung) + 1] in ("/", "#")


def _resolve_ladder(slot: dict, coordinate: dict) -> Any:
    """Resolve a CONTAINMENT ladder slot against the coordinate's address (longest-prefix-wins; walk up
    on absence; fail-loud legible-absent below). PURE — the address comes from the coordinate, nothing else."""
    addr_path = slot["ladder"]
    if not isinstance(addr_path, str) or not addr_path:
        raise ResolverError(
            f"resolve(ladder): 'ladder' must be a non-empty dot-path to the coordinate's address "
            f"(e.g. 'address'); got {addr_path!r}. Fail loud.")
    rungs = slot.get("rungs")
    if not isinstance(rungs, dict) or not rungs:
        raise ResolverError(
            f"resolve(ladder): a ladder-slot needs a non-empty 'rungs' dict {{address-prefix: value}}; "
            f"got {slot!r}. Fail loud.")
    # A MISSING/None address means "no containment context" → only the universal ("") rung can apply
    # (never a deeper project/scope rung by accident). Normalise to "" so the match logic is uniform.
    # (_get_path fail-louds on an absent field; here an absent address is a LEGITIMATE "universal-only"
    # coordinate — the containment axis is simply unset — so absence walks to "", it does not raise.)
    try:
        address = rules._get_path(coordinate, addr_path)       # reuse the SAME dot-path reader select uses
    except rules.RuleError:
        address = ""
    if address is None:
        address = ""
    if not isinstance(address, str):
        raise ResolverError(
            f"resolve(ladder): the address at {addr_path!r} must be a string (the containment axis); "
            f"got {address!r} ({type(address).__name__}). Fail loud.")
    best = None
    for k in rungs:
        if _rung_matches(k, address) and (best is None or len(k) > len(best)):
            best = k
    if best is not None:
        return rungs[best]
    if "default" in slot:
        return slot["default"]
    raise ResolverError(
        f"resolve(ladder): address {address!r} matched NO rung {sorted(rungs)} and no 'default' — "
        f"legible absent (a rung must exist AT or ABOVE this address, or declare a 'default'). "
        f"Fail loud, never a silent wrong rung. Fix: write a rung at '' (universal) or a covering prefix.")


def resolve_slot(slot: Any, coordinate: dict) -> Any:
    """Resolve ONE invariant slot against the coordinate. A slot is either:
      • a relationship-AST dict (has an "op") → CONTINUOUS: rules.evaluate(ast, coordinate).
      • a select dict {"select": <dot-path>, "cases": {..}, "default"?: ..} → DISCRETE: pick by the
        coordinate's value at <dot-path>; fail-loud if the value isn't a case and no default given.
      • a plain literal (int/float/str/bool/None) → returned as-is (a fixed value is a degenerate relationship).
    """
    if isinstance(slot, dict) and "op" in slot:
        return rules.evaluate(slot, coordinate)                # CONTINUOUS — derive via the relationship
    if isinstance(slot, dict) and "ladder" in slot:            # CONTAINMENT — longest-prefix on the coordinate's address
        return _resolve_ladder(slot, coordinate)
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
    # LADDER (L7-KEEPER): longest-prefix-on-address, walk-up, fail-loud-below. ONE 3-rung invariant,
    # THREE coordinates → three different resolved rungs from one definition (the containment axis).
    LADDER = {"tier": {"ladder": "address",
                       "rungs": {"": "universal",
                                 "project://counterpart-design": "project",
                                 "project://counterpart-design#mockups": "scope"}}}
    assert resolve(LADDER, {"address": "project://counterpart-design#mockups"})["tier"] == "scope"
    assert resolve(LADDER, {"address": "project://counterpart-design"})["tier"] == "project"      # walk-up: no scope rung
    assert resolve(LADDER, {"address": "project://counterpart-design#other"})["tier"] == "project"  # walk-up past absent scope
    assert resolve(LADDER, {"address": "project://something-else"})["tier"] == "universal"        # walk all the way up
    assert resolve(LADDER, {})["tier"] == "universal"                                              # no address → universal only
    assert not _rung_matches("project://x", "project://xy")                                        # boundary guard (no spurious cover)
    assert _rung_matches("project://x", "project://x#s") and _rung_matches("project://x", "project://x/y")
    # fail-loud: an address below the shallowest rung, no "" universal + no default → RAISES a legible absent.
    try:
        resolve({"t": {"ladder": "address", "rungs": {"project://x/y": 2}}}, {"address": "project://z"})
        raise SystemExit("FAIL: ladder below the shallowest rung (no universal/default) did not raise")
    except ResolverError:
        pass
    # a 'default' catches the below-shallowest case (legible fallback, not a crash).
    assert resolve({"t": {"ladder": "address", "rungs": {"project://x/y": 2}, "default": 0}},
                   {"address": "project://z"})["t"] == 0
    print("resolver OPERATIONAL self-test: ALL PASS "
          "(continuous-derivation · clamp-allocation · discrete registry-select · CONTAINMENT-ladder "
          "longest-prefix+walk-up+fail-loud-below · fits-by-coordinate · fail-loud)")
