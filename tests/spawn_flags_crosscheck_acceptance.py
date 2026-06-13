"""tests/spawn_flags_crosscheck_acceptance.py — the SPAWN_FLAGS cross-check fixture (F-FIX-9).
Mirror-Registry System, LANE-REGISTRIES.

THE GATE ON THE SUPERVISOR SWAP (F-FIX-5 step 4). Before the hand-written
`session_supervisor.SPAWN_FLAGS` dict is ever removed (the DEFERRED LANE-SUPERVISOR-REFACTOR, NOT
this lane), this fixture PROVES the registry rules reproduce the hand-postures: for EVERY SPAWN_FLAGS
key whose flag-name overlaps the registry, the engine's DERIVED posture (classify over the platform's
SignalSets, looked up by the body-key↔flag-name map in platforms/claude_code.py) MUST equal the
SPAWN_FLAGS hand-posture. Any divergence is a LOUD finding to RESOLVE — never silently absorbed
(F-FIX-9 / no-silent-failures law).

This is a STATIC-DATA fixture: it spawns NOTHING (no `claude`, no model). It classifies the 48
SPAWN_FLAGS keys' flag-names directly through `introspection.rules.classify` over the platform's
LIVE-derived SignalSets (transport_invariants derived at PlatformRegistry load via the registered
head_builder thunk). The live ≥30-flag discovery is a SEPARATE LEAD-only criterion (C-REG-1); this
fixture does not need it — it cross-checks the RULES against the hand-dict on the static signal data.

POSTURE MAPPING (the registry posture vocabulary → the SPAWN_FLAGS posture vocabulary):
  rules.classify returns one of: locked | hazard | consent | safe | unmatched.
  SPAWN_FLAGS posture is one of:  locked | consent | safe.
  Equivalence for the cross-check:
    registry "locked"  ≡ SPAWN_FLAGS "locked"   (R1 transport invariant / body-key lock)
    registry "hazard"  ≡ SPAWN_FLAGS "locked"   (R2 self-named-danger is a hand-LOCKED row — e.g.
                                                 dangerously_skip_permissions; the hand-dict has no
                                                 separate hazard bucket, it locks them)
    registry "consent" ≡ SPAWN_FLAGS "consent"  (R3 capability-axis widening)
    registry "safe"    ≡ SPAWN_FLAGS "safe"     (R5 expose-not-gate default)
    registry "unmatched" has NO SPAWN_FLAGS equivalent (R4 is a refresh-time novelty verdict, never a
                                                 standing hand-row) → a divergence if it occurs.

EXPORTS `crosscheck()` → a structured report dict so the deferred LANE-REFRESH acceptance test can
CALL this same gate (F-FIX-9: "the cross-check in the acceptance test") without duplicating the logic.
Run directly (`python3 tests/spawn_flags_crosscheck_acceptance.py`) for the standalone gate.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from introspection import rules
from introspection.platforms import platform_registry


# registry-posture → SPAWN_FLAGS-posture equivalence (the mapping documented in the module docstring)
_POSTURE_EQUIV = {
    "locked": "locked",
    "hazard": "locked",     # a self-named-danger flag is a hand-LOCKED row (no separate hazard bucket)
    "consent": "consent",
    "safe": "safe",
    # "unmatched" deliberately absent — R4 has no standing hand-row; its presence is a divergence.
}


def crosscheck(platform_id: str = "claude-code") -> dict:
    """Run the cross-check. Returns a structured report:
        {
          "platform_id": ...,
          "checked": [ {key, flag, hand_posture, registry_posture, registry_posture_mapped,
                        registry_rule, agree: bool}, ... ],   # one per overlapping SPAWN_FLAGS key
          "agreements": int,
          "divergences": [ {key, flag, hand_posture, registry_posture, registry_rule, reason}, ... ],
          "ok": bool,        # True iff zero divergences
        }
    Imports SPAWN_FLAGS + the body-key↔flag map at call time (so a context without the supervisor
    still imports this module). FAILS LOUD if either is unavailable — the gate cannot run blind."""
    from runtime.session_supervisor import SPAWN_FLAGS
    from platforms.claude_code import SPAWN_FLAG_BODY_KEY_MAP

    reg = platform_registry()
    if platform_id not in reg:
        raise RuntimeError(
            f"crosscheck: platform {platform_id!r} not in the PlatformRegistry (ids: {reg.ids()}) — "
            f"the cross-check cannot run without the platform's SignalSets. Fail loud.")
    platform = reg[platform_id]
    # the LIVE-derived signal_sets (transport_invariants derived at load via the head_builder thunk)
    signal_sets = platform.signal_sets

    checked: list[dict] = []
    divergences: list[dict] = []
    agreements = 0

    for key, spec in SPAWN_FLAGS.items():
        hand_posture = spec["posture"]
        flag = SPAWN_FLAG_BODY_KEY_MAP.get(key) or spec.get("flag") or ""
        if not flag:
            divergences.append({
                "key": key, "flag": "", "hand_posture": hand_posture,
                "registry_posture": None, "registry_rule": None,
                "reason": f"no flag-name mapping for SPAWN_FLAGS key {key!r} — the body-key↔flag map "
                          f"in platforms/claude_code.py must cover every key. Cannot classify without "
                          f"a flag-name. Fail loud.",
            })
            continue
        reg_posture, reg_rule, _axis = rules.classify(flag, signal_sets)
        mapped = _POSTURE_EQUIV.get(reg_posture)
        agree = (mapped == hand_posture)
        assembler_kind = spec.get("kind", "")
        row = {
            "key": key, "flag": flag, "hand_posture": hand_posture,
            "registry_posture": reg_posture, "registry_posture_mapped": mapped,
            "registry_rule": reg_rule, "assembler_kind": assembler_kind, "agree": agree,
        }
        checked.append(row)
        if agree:
            agreements += 1
        else:
            # Characterize the divergence. The KNOWN, resolvable class is the SWAP-KIND HEAD DEFAULT:
            # a flag the consumer EMITS in its transport head (so the F-FIX-2 derivation includes it,
            # as C-CORE-4 requires) but which is CONSENT-overridable via swap (so the hand posture is
            # 'consent', not 'locked'). R1's pure membership test cannot see 'swap'; the deferred
            # LANE-SUPERVISOR-REFACTOR resolves it by reading assembler_kind=='swap' to treat a
            # head-member as consent rather than a hard lock (F-FIX-5 step 2 adds assembler_kind to
            # CapabilityEntry exactly for this). It is a characterized, resolvable finding — NOT an
            # uncharacterized rule error — but it STILL blocks the swap until the refactor handles it.
            is_swap_head_default = (
                assembler_kind == "swap" and reg_posture == "locked" and hand_posture == "consent")
            if is_swap_head_default:
                klass = "swap-head-default"
                reason = (
                    f"registry derives {reg_posture!r} (R1: {flag!r} is in the DERIVED transport-"
                    f"invariant head, which C-CORE-4 requires) but the hand posture is {hand_posture!r}. "
                    f"This is the SWAP-KIND HEAD DEFAULT class: {flag!r} is emitted in the head AND is "
                    f"consent-overridable (assembler_kind='swap'). RESOLUTION (deferred "
                    f"LANE-SUPERVISOR-REFACTOR, F-FIX-5 step 2): when the supervisor reads posture from "
                    f"the registry, a derived-locked flag carrying assembler_kind=='swap' is treated as "
                    f"CONSENT, not hard-locked. This finding BLOCKS the SPAWN_FLAGS removal (F-FIX-5 "
                    f"step 6) until that swap-aware read is built — exactly the F-FIX-9 gate.")
            else:
                klass = "uncharacterized"
                reason = (
                    f"registry derives {reg_posture!r} (rule {reg_rule}, maps to {mapped!r}) but the "
                    f"hand SPAWN_FLAGS posture is {hand_posture!r} — UNCHARACTERIZED divergence; the "
                    f"rules / signal-sets data must be reconciled before the swap. Fail loud.")
            divergences.append({
                "key": key, "flag": flag, "hand_posture": hand_posture,
                "registry_posture": reg_posture, "registry_posture_mapped": mapped,
                "registry_rule": reg_rule, "assembler_kind": assembler_kind,
                "class": klass, "reason": reason,
            })

    uncharacterized = [d for d in divergences if d.get("class") == "uncharacterized"
                       or d.get("flag") == ""]
    return {
        "platform_id": platform_id,
        "checked": checked,
        "agreements": agreements,
        "total_overlapping": len(checked) + sum(1 for d in divergences if d["flag"] == ""),
        "divergences": divergences,
        "uncharacterized_divergences": uncharacterized,
        # ok = zero divergences at all (the gate that blocks SPAWN_FLAGS removal — F-FIX-5 step 6).
        "ok": len(divergences) == 0,
        # clean_for_rules = no UNCHARACTERIZED divergence: the rules themselves are proven correct;
        # the only residual is the known swap-head-default class the deferred refactor resolves.
        "clean_for_rules": len(uncharacterized) == 0,
    }


def main() -> int:
    report = crosscheck()
    print(f"SPAWN_FLAGS cross-check (F-FIX-9) — platform {report['platform_id']!r}")
    print(f"  keys checked: {len(report['checked'])}  agreements: {report['agreements']}  "
          f"divergences: {len(report['divergences'])}")
    # show the agreement breakdown by posture for confidence
    by_posture: dict[str, int] = {}
    for r in report["checked"]:
        if r["agree"]:
            by_posture[r["hand_posture"]] = by_posture.get(r["hand_posture"], 0) + 1
    print(f"  agreements by posture: {by_posture}")
    if report["divergences"]:
        print("  DIVERGENCES (LOUD — gate on the SPAWN_FLAGS removal, F-FIX-5 step 6):")
        for d in report["divergences"]:
            klass = d.get("class", "?")
            print(f"    - [{klass}] key={d['key']!r} flag={d['flag']!r}: {d['reason']}")
        if report["clean_for_rules"]:
            print("  RULES PROVEN: every divergence is the KNOWN, characterized swap-head-default "
                  "class — the registry rules reproduce all NON-swap hand-postures exactly. The "
                  "residual is resolved by the deferred LANE-SUPERVISOR-REFACTOR (swap-aware posture "
                  "read), NOT by a rule change. The gate still BLOCKS the SPAWN_FLAGS removal until "
                  "that swap-aware read is built (F-FIX-9).")
        else:
            print("  UNCHARACTERIZED divergence present — the rules / signal-data must be reconciled.")
        # The gate FAILS on any divergence (it is the gate on the supervisor swap). It is NOT a build
        # error in THIS lane (this lane only builds + runs the gate); it BLOCKS the deferred swap.
        return 1
    print("  OK — every overlapping SPAWN_FLAGS key's hand-posture is reproduced by the registry rules.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
