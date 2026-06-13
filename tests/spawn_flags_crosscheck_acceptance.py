"""tests/spawn_flags_crosscheck_acceptance.py — the spawn-flag posture cross-check (F-FIX-9).
Mirror-Registry System, LANE-SUPERVISOR-REFACTOR.

HISTORY + ROLE CHANGE (2026-06-14). This fixture WAS the gate on the supervisor swap (F-FIX-5 step
4): before the hand-written `session_supervisor.SPAWN_FLAGS` dict carried a `posture` column, this
proved the Mirror-Registry rules reproduce every hand-posture (it passed 48/48, zero divergence).
That gate cleared, so F-FIX-5 steps 5-6 fired: the supervisor now DERIVES posture from the registry
(`session_supervisor._registry_posture` → `introspection.rules.classify`), and the hand SPAWN_FLAGS
dict was DELETED — the registry is the SOLE truth for posture. `session_supervisor.SPAWN_FLAG_ASSEMBLY`
now carries ONLY the consumer-emission data (flag-name, assembler kind, teaching text); it has NO
posture column.

POST-DELETION ROLE — the standing REGRESSION + SELF-CONSISTENCY gate. With no hand-posture to compare
against, this fixture now asserts TWO things, still spawning NOTHING (no `claude`, no model — pure
static data over the platform's R6-corrected SignalSets):

  1. REGRESSION — every spawn-flag's registry-DERIVED posture equals the FROZEN curated ground-truth
     captured below (`_EXPECTED_POSTURE`, the 48 postures the swap was verified against). A future
     signal-set / rule edit that drifts ANY flag's posture fails LOUD here (no-silent-failures law).
     This is the same 48/48 the swap cleared on, frozen so it cannot silently regress.
  2. SELF-CONSISTENCY — every `SPAWN_FLAG_ASSEMBLY` key has a non-empty flag-name and classifies to a
     REAL posture (locked|hazard|consent|safe), never R4 `unmatched` (an unmatched spawn flag means
     the supervisor would refuse a flag it declares it can assemble — a contradiction).

POSTURE VOCABULARY: rules.classify returns locked|hazard|consent|safe|unmatched. The supervisor
treats locked+hazard as refuse-locked, consent as the consent-gated widen, safe as apply-freely.
`_EXPECTED_POSTURE` stores the raw rules vocabulary (so a hazard→locked collapse would still surface
as a drift, not be hidden by an equivalence map).

EXPORTS `crosscheck()` → a structured report dict (so a LANE-REFRESH acceptance test can CALL this
same gate without duplicating the logic). Run directly for the standalone gate.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from introspection import rules
from introspection.platforms import platform_registry


# ── the FROZEN curated ground-truth (the 48 postures the supervisor swap was verified against) ──────
# Captured at the 48/48 zero-divergence pass that gated F-FIX-5 step 4. Stored in the RAW rules
# vocabulary (locked|hazard|consent|safe). A future rule / signal-set change that moves any of these
# fails LOUD (regression gate). NOT a re-introduction of the hand-posture column — it is a TEST
# expectation, the frozen snapshot the registry must keep reproducing.
_EXPECTED_POSTURE: dict[str, str] = {
    "add_dir": "consent",          # dirs capability axis (R3) — the 2026-06-14 fix
    "advisor": "safe", "agent": "safe", "agents": "safe",
    "allowed_tools": "consent",    # R6 swap-kind head-default → R3 consent (tools-builtin)
    "append_system_prompt": "safe", "append_system_prompt_file": "safe",
    "bare": "locked", "betas": "safe", "continue": "safe",
    "dangerously_skip_permissions": "locked",   # R1 body-key lock fires before R2 hazard
    "debug": "locked", "debug_file": "safe", "disable_slash_commands": "safe",
    "disallowed_tools": "consent", "effort": "locked",
    "exclude_dynamic_system_prompt_sections": "safe",
    "fallback_model": "locked", "fork_session": "locked", "include_hook_events": "safe",
    "include_partial": "locked", "input_format": "locked", "json_schema": "safe",
    "max_budget_usd": "safe", "max_turns": "safe",
    "mcp_config": "consent",       # R6 swap-kind head-default → R3 consent (mcp)
    "model": "locked", "name": "safe", "no_session_persistence": "safe",
    "output_format": "locked", "permission_mode": "locked", "permission_prompt_tool": "consent",
    "plugin_dir": "consent", "plugin_url": "consent", "print": "locked",
    "prompt_suggestions": "safe", "replay_user_messages": "safe", "resume": "locked",
    "safe_mode": "locked", "session_id": "safe", "setting_sources": "safe", "settings": "locked",
    "strict_mcp_config": "locked", "system_prompt": "safe", "system_prompt_file": "safe",
    "teammate_mode": "safe", "tools": "consent", "verbose": "locked",
}
_REAL_POSTURES = {"locked", "hazard", "consent", "safe"}   # `unmatched` (R4) is a contradiction here


def crosscheck(platform_id: str = "claude-code") -> dict:
    """Run the post-deletion regression + self-consistency gate. Returns a structured report:
        {
          "platform_id": ...,
          "checked": [ {key, flag, expected, registry_posture, registry_rule, agree: bool}, ... ],
          "agreements": int,
          "divergences": [ {key, flag, expected, registry_posture, registry_rule, reason}, ... ],
          "ok": bool,        # True iff zero divergences AND every key covered AND no unmatched
        }
    Imports SPAWN_FLAG_ASSEMBLY + the body-key↔flag map at call time (so a context without the
    supervisor still imports this module). FAILS LOUD if either is unavailable — the gate cannot run
    blind. Spawns NOTHING — pure static classification over the platform's R6-corrected SignalSets."""
    from runtime.session_supervisor import SPAWN_FLAG_ASSEMBLY
    from platforms.claude_code import SPAWN_FLAG_BODY_KEY_MAP
    import platforms._wiring  # noqa: F401 — register the head_builder thunk so the registry derives
    # transport_invariants LIVE from the spawn template (ROW-PURITY: the binding lives in the wiring
    # module now, not in the pure-data claude_code.py row).

    reg = platform_registry()
    if platform_id not in reg:
        raise RuntimeError(
            f"crosscheck: platform {platform_id!r} not in the PlatformRegistry (ids: {reg.ids()}) — "
            f"the cross-check cannot run without the platform's SignalSets. Fail loud.")
    platform = reg[platform_id]
    signal_sets = platform.signal_sets    # R6-corrected transport_invariants derived at load

    checked: list[dict] = []
    divergences: list[dict] = []
    agreements = 0

    # 1 — the assembly table must be fully covered by the frozen expectation (no key drift either way)
    assembly_keys = set(SPAWN_FLAG_ASSEMBLY)
    expected_keys = set(_EXPECTED_POSTURE)
    missing_expectation = sorted(assembly_keys - expected_keys)   # an assembly key with no frozen posture
    stale_expectation = sorted(expected_keys - assembly_keys)     # a frozen posture for a removed key
    for k in missing_expectation:
        divergences.append({
            "key": k, "flag": SPAWN_FLAG_ASSEMBLY[k].get("flag", ""), "expected": None,
            "registry_posture": None, "registry_rule": None,
            "reason": f"SPAWN_FLAG_ASSEMBLY key {k!r} has NO frozen expectation — a new spawn flag was "
                      f"added without recording its verified posture in _EXPECTED_POSTURE. Add it (with "
                      f"the posture you verified) so the regression gate covers it. Fail loud.",
        })
    for k in stale_expectation:
        divergences.append({
            "key": k, "flag": "", "expected": _EXPECTED_POSTURE[k],
            "registry_posture": None, "registry_rule": None,
            "reason": f"_EXPECTED_POSTURE has a frozen posture for {k!r} but SPAWN_FLAG_ASSEMBLY no "
                      f"longer declares it — remove the stale expectation. Fail loud.",
        })

    # 2 — every assembly key: registry-derived posture == frozen expectation, AND a real posture
    for key, spec in SPAWN_FLAG_ASSEMBLY.items():
        flag = spec.get("flag") or SPAWN_FLAG_BODY_KEY_MAP.get(key) or ""
        if not flag:
            divergences.append({
                "key": key, "flag": "", "expected": _EXPECTED_POSTURE.get(key),
                "registry_posture": None, "registry_rule": None,
                "reason": f"no flag-name for assembly key {key!r} (neither the row's `flag` nor the "
                          f"body-key↔flag map covers it). Cannot classify. Fail loud.",
            })
            continue
        reg_posture, reg_rule, _axis = rules.classify(flag, signal_sets)
        expected = _EXPECTED_POSTURE.get(key)
        real = reg_posture in _REAL_POSTURES
        agree = (reg_posture == expected) and real
        row = {
            "key": key, "flag": flag, "expected": expected,
            "registry_posture": reg_posture, "registry_rule": reg_rule, "agree": agree,
        }
        checked.append(row)
        if agree:
            agreements += 1
        elif not real:
            divergences.append({
                "key": key, "flag": flag, "expected": expected,
                "registry_posture": reg_posture, "registry_rule": reg_rule,
                "reason": f"assembly flag {flag!r} classifies {reg_posture!r} (R4 unmatched / unreal) — "
                          f"the supervisor declares it assemblable but the rules refuse to classify it. "
                          f"A spawn flag must derive a real posture. Fail loud.",
            })
        else:
            divergences.append({
                "key": key, "flag": flag, "expected": expected,
                "registry_posture": reg_posture, "registry_rule": reg_rule,
                "reason": f"REGRESSION — {flag!r} now derives {reg_posture!r} (rule {reg_rule}) but the "
                          f"frozen verified posture is {expected!r}. A signal-set/rule change drifted "
                          f"this flag's posture. Reconcile (or update _EXPECTED_POSTURE only if the new "
                          f"posture is deliberately correct). Fail loud.",
            })

    return {
        "platform_id": platform_id,
        "checked": checked,
        "agreements": agreements,
        "total_keys": len(SPAWN_FLAG_ASSEMBLY),
        "divergences": divergences,
        "ok": len(divergences) == 0,
    }


def main() -> int:
    report = crosscheck()
    print(f"spawn-flag posture cross-check (F-FIX-9, post-swap regression gate) — "
          f"platform {report['platform_id']!r}")
    print(f"  keys checked: {len(report['checked'])}/{report['total_keys']}  "
          f"agreements: {report['agreements']}  divergences: {len(report['divergences'])}")
    by_posture: dict[str, int] = {}
    for r in report["checked"]:
        if r["agree"]:
            by_posture[r["registry_posture"]] = by_posture.get(r["registry_posture"], 0) + 1
    print(f"  agreements by posture: {by_posture}")
    if report["divergences"]:
        print("  DIVERGENCES (LOUD — registry-is-truth regression / self-consistency gate):")
        for d in report["divergences"]:
            print(f"    - key={d['key']!r} flag={d['flag']!r}: {d['reason']}")
        return 1
    print("  OK — every spawn-flag's registry-derived posture matches the frozen verified ground-truth "
          "(48/48), and every assembly key classifies to a real posture. The registry is the sole "
          "posture truth; the hand SPAWN_FLAGS dict is deleted (F-FIX-5 steps 5-6).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
