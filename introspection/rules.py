"""introspection/rules.py — the five closed classification rules (R1-R5) + the transport-invariant
derivation. LEVEL 1 (platform-agnostic) - Mirror-Registry System, LANE-INTROSPECTION-CORE.

THE LEAK INVARIANT (F-FIX-10 / PG2 - load-bearing). This file contains ZERO platform-name
literals. The rule LOGIC is here; every signal VALUE (hazard words, capability axes, the
transport-invariant set) arrives as DATA on a `SignalSets` / `PlatformEntry` (Level 2). A grep
of this file for the banned platform strings MUST return ZERO hits - any hit means Level-2 data
leaked into Level-1 code and the lift is broken (tests/introspection_acceptance.py asserts this,
FAIL on any hit).

THE FIVE RULES (Dynamic Capability Registry - Spec section 3.3; lifted verbatim, parameterized
over SignalSets). Priority: R1 > R2 > R3 > R5 > R4.

  R1 LOCKED   - flag in transport_invariants (a property of the CONSUMER/fabric, DERIVED from the
                spawn template, NOT the flag name; see derive_transport_invariants).
  R2 HAZARD   - the flag NAME contains a hazard signal word (the platform's OWN naming convention).
                SCOPE: flag-NAME string ONLY - NEVER the description text (mandatory).
  R3 CONSENT  - flag in a declared capability_axis (widens the session surface).
  R5 SAFE     - NOT(R1) AND NOT(R2) AND NOT(R3) - the EXPOSE default (Tim Ruling 1).
  R4 UNMATCHED- anything else / a genuinely novel flag pending curator confirm -> fail-CLOSED +
                surface, teaching-refusal, NEVER silent.

F-FIX-2 / PG-D1: derive_transport_invariants() is REAL CODE here. It reads the consumer's spawn
template HEAD (the unconditionally-emitted flags) UNION the body_key_overrides locked rows, and
RETURNS the set at PlatformRegistry load time. The platform row's signal_sets.transport_invariants
is POPULATED by this function, never hand-typed. The consumer's command builder + its keyword
binding live in LEVEL-2 platform data (the engine binds a head_builder thunk) - never as a literal
here, so the leak invariant holds.
"""
from __future__ import annotations
from typing import Callable


# -- The five closed rules over a SignalSets (data) -----------------------------------------
#
# Each rule is a pure predicate over (flag_name, SignalSets). flag_name is the capability's
# `name` field - for flags it INCLUDES the leading dashes (F-FIX-14: name='--debug'). The rules
# read ONLY the data on the passed signal_sets; they hold no membership list of their own.

def r1_locked(flag_name: str, signal_sets) -> bool:
    """R1 - LOCKED: the flag is a transport invariant of the held-open headless loop, OR owns a
    dedicated spawn-body key the flags layer must not override. SCOPE: exact membership in
    signal_sets.transport_invariants - a set DERIVED FROM the consumer's spawn template
    (derive_transport_invariants), never hand-listed. A property of the fabric, not the name."""
    return flag_name in set(signal_sets.transport_invariants)


def r2_hazard(flag_name: str, signal_sets) -> bool:
    """R2 - HAZARD: the flag NAME contains a hazard signal word - the platform's OWN naming
    convention (its self-described hazard signal, a stable signal, not our opinion). SCOPE:
    the flag-NAME string ONLY - NEVER description text (scanning descriptions produces a false
    positive, e.g. a flag whose description says 'skip hooks'). hazard_scope on the SignalSets
    MUST be 'flag_name_only' - we ASSERT it (fail loud) so a future row cannot widen the scope
    to descriptions silently."""
    if signal_sets.hazard_scope != "flag_name_only":
        raise ValueError(
            f"R2 HAZARD scope violation: hazard_scope={signal_sets.hazard_scope!r} - R2 scans the "
            f"flag NAME only (never description text). Set hazard_scope='flag_name_only'. Fail loud.")
    name = flag_name.lower()
    return any(word in name for word in signal_sets.hazard_name_vocabulary)


def r3_consent(flag_name: str, signal_sets) -> tuple[bool, str]:
    """R3 - CONSENT: the flag mutates a declared CAPABILITY AXIS (widens the session surface).
    SCOPE: membership in a capability_axes set. Returns (matched, axis_name) so the caller can
    record WHICH axis on the entry (CapabilityEntry.axis) - auditable, never a bare bool."""
    for axis, members in signal_sets.capability_axes.items():
        if flag_name in members:
            return True, axis
    return False, ""


# Posture result: (posture, posture_rule, axis). axis is '' unless R3 fired.
def classify(flag_name: str, signal_sets) -> tuple[str, str, str]:
    """Run the five rules at priority R1 > R2 > R3 > R5 > R4 and return the DERIVED posture +
    which rule fired (posture_rule) + the axis (R3 only). Posture is never an opinion: it is the
    derivation result, reproducible from (flag_name, signal_sets). EXPOSE-not-gate (R5) is the
    default; R1/R2 are the rare gating exceptions; R3 rides a consent beat; R4 is fail-closed.

    NOTE on R4 here: a flag that misses R1/R2/R3 lands at R5 SAFE *by this classifier* - R5 is the
    expose default for a flag that IS on the live surface (it was discovered, so it exists). R4
    (UNMATCHED, fail-closed + surface) is reserved by the spec for a genuinely NOVEL flag pending
    the curator gate AND for rail/host-incompatible or deprecated/removed flags - that novelty
    decision is made at REFRESH time (diff against the prior registry) and via rail-metadata, not
    by this membership classifier. Use classify_with_novelty() to drive the explicit R4 verdict."""
    # R1 - LOCKED (highest priority: a transport invariant is locked even if its name looks safe)
    if r1_locked(flag_name, signal_sets):
        return "locked", "R1", ""
    # R2 - HAZARD (flag-name self-named danger)
    if r2_hazard(flag_name, signal_sets):
        return "hazard", "R2", ""
    # R3 - CONSENT (widens a capability axis)
    matched, axis = r3_consent(flag_name, signal_sets)
    if matched:
        return "consent", "R3", axis
    # R5 - SAFE/FEATURE (the EXPOSE default - most of the surface lands here)
    return "safe", "R5", ""


def classify_with_novelty(flag_name: str, signal_sets, *, is_novel: bool,
                          rail_incompatible: bool = False) -> tuple[str, str, str]:
    """The full classifier including the R4 fail-closed path. A genuinely NOVEL flag (first seen at
    a refresh, pending curator confirm) OR a rail/host-incompatible flag -> R4 UNMATCHED, fail-closed
    + surfaced, NEVER silently exposed. Otherwise defers to classify() (R1>R2>R3>R5).

    R4 priority is LOWEST overall (R1>R2>R3>R5>R4) - a novel flag that ALSO matches R1/R2/R3 takes
    that higher posture (it is classifiable); R4 fires only when nothing else matched AND it is
    novel/incompatible. This is the audit gate: an unknown flag can never silently auto-enter the
    trusted (R5) set."""
    posture, rule, axis = classify(flag_name, signal_sets)
    if rule == "R5" and (is_novel or rail_incompatible):
        return "unmatched", "R4", ""
    return posture, rule, axis


def teaching_refusal_for_r4(flag_name: str, *, rail: str = "", alternative: str = "",
                            host_boundary: str = "") -> str:
    """R4 teaching-refusal content (section 3.7) - three named parts, NEVER a bare 'unsupported':
      1. why this flag can't apply on THIS rail,
      2. the alternative path if one exists,
      3. the host/rail boundary stated explicitly.
    Fail-CLOSED, LOUD. The caller raises this text; the engine never silently no-ops an R4."""
    parts = [f"REFUSED - capability {flag_name!r} is UNMATCHED (R4): it is not on the trusted "
             f"(R5) surface."]
    if rail:
        parts.append(f"Why on this rail: {rail}")
    if alternative:
        parts.append(f"Alternative path: {alternative}")
    if host_boundary:
        parts.append(f"Host/rail boundary: {host_boundary}")
    parts.append("It is SURFACED for the curator gate (consent beat), never silently allowed and "
                 "never silently dropped.")
    return " ".join(parts)


# -- F-FIX-2 / PG-D1 - derive the transport-invariant set from the consumer's spawn template --

def _flags_in_cmd(cmd: list[str]) -> list[str]:
    """Extract the FLAG tokens from a built command list: any element beginning with '-'. The
    executable path and flag VALUES are not flags. This reads whatever the consumer's builder
    emitted - no flag-name literals live here, so the engine carries no platform-specific flag
    strings."""
    return [tok for tok in cmd if isinstance(tok, str) and tok.startswith("-")]


def derive_transport_invariants(head_builder: Callable[[], list[str]],
                                body_key_overrides: dict | None = None) -> list[str]:
    """DERIVE the transport-invariant set (the R1 input) from the consumer's spawn template - REAL
    code, never a hand-list (F-FIX-2 / PG-D1; law: registry-is-truth). It is the UNION of:

      (a) the flags the consumer's command builder ALWAYS emits in its transport HEAD - obtained by
          CALLING `head_builder()`, a zero-arg thunk the LEVEL-2 platform binds that calls the
          consumer's builder with MINIMAL arguments (no optional body-key params), so the returned
          list is exactly the unconditional head; we keep the '-'-prefixed tokens; and
      (b) the flag names of the body_key_overrides locked rows (each override owns a dedicated
          spawn-body key the flags layer must not override).

    Because `head_builder` is supplied by the platform binding (the consumer's builder + its keyword
    arguments live in Level-2 platform code) and `body_key_overrides` is platform DATA, THIS function
    holds none of those strings as literals - the leak invariant holds. If the consumer's spawn
    template gains/loses an unconditional flag, re-deriving here reflects it automatically (drift
    detection: the acceptance test asserts every unconditional-head flag is in the returned set; a
    future consumer flag addition not reflected fails the test loudly rather than silently
    mis-classifying R1 -> R5).

    head_builder: a zero-arg callable returning the consumer's unconditional spawn-head command
        list (the platform row binds it as `lambda: Supervisor._build_spawn_cmd(<bin>, resume=None,
        fork=False)` - that binding is Level-2 code, never here).
    body_key_overrides: the platform row's consumer_reserved_invariants.body_key_overrides
        ({key: {"flag": "--x", "kind": "value"}, ...}) - each `flag` joins the invariant set."""
    head = head_builder()
    invariants = set(_flags_in_cmd(head))
    for _key, spec in (body_key_overrides or {}).items():
        flag = spec.get("flag") if isinstance(spec, dict) else None
        if flag:
            invariants.add(flag)
    return sorted(invariants)
