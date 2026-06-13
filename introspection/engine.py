"""introspection/engine.py - the four-verb Mirror-Registry engine (Level 1, platform-agnostic).
Mirror-Registry System, LANE-INTROSPECTION-CORE.

The engine operates ONE circuit over a PlatformEntry + the two registries:

    DISCOVER  -> CLASSIFY -> PROJECT -> REFRESH

  DISCOVER  (discover.py): run the platform's DiscoverySources through their adapters -> rows.
  CLASSIFY  (rules.py):    run the 5 closed rules over each flag row -> posture + posture_rule + axis.
  PROJECT   (here):        shape the classified rows into a face-neutral projection (counts by kind,
                           the rows themselves) the MCP tool / bridge route / cap:// resolver read.
  REFRESH   (here):        re-DISCOVER, diff against a prior snapshot {added, changed, vanished},
                           detect novelty so the R4 fail-closed verdict can fire at refresh time.

ZERO platform-name literals (F-FIX-10 / PG2). Everything platform-specific arrives as DATA on the
PlatformEntry passed in. derive_transport_invariants() (rules.py, F-FIX-2) is invoked HERE at
classify time so the R1 input is the LIVE derivation from the consumer's spawn template, never a
hand-list - but the spawn-template thunk + body_key_overrides are bound on the PlatformEntry's
signal_sets (Level-2 data), so no consumer flag strings live in this file.

LEAD-only: classify_platform()/refresh() with live discovery spawn the platform binary. The engine
is unit-verified with a STUB PlatformEntry + a stub discoverer that returns fixture rows (no live
subprocess) - the live path is 'built - lead live-verify queued'.

NOTE: this file is Level-1 platform-agnostic code; it carries NO platform-name literals (the
acceptance gate, F-FIX-10, greps it). All examples below name the consumer's spawn-template function
by its generic role, never by a vendor string.
"""
from __future__ import annotations
from typing import Callable, Optional

from contracts.capability_entry import CapabilityEntry
from contracts.platform_entry import PlatformEntry
from introspection import rules
from introspection.discover import discover as run_discover


# ── transport-invariant derivation binding (F-FIX-2) ─────────────────────────────────────────
#
# The R1 input is the LIVE derivation of the consumer's transport invariants. The consumer's
# command builder + its keyword binding are Level-2 platform code; the PlatformEntry's signal_sets
# carries a way to obtain them WITHOUT naming them here. A platform binds a head_builder thunk
# (a zero-arg callable returning the unconditional spawn-head argv) - the engine CALLS it and the
# returned argv is parsed for flag tokens. The binding registry below maps a platform_id -> thunk
# so the platform row stays pure DATA (a Pydantic model cannot hold a callable). A platform's
# build-time module registers its thunk via register_head_builder(); the engine looks it up.

_HEAD_BUILDERS: dict[str, Callable[[], list[str]]] = {}


def register_head_builder(platform_id: str, thunk: Callable[[], list[str]]) -> None:
    """A platform's Level-2 module registers the zero-arg thunk that returns the consumer's
    unconditional spawn-head argv (it wraps the consumer's command-builder called with minimal
    arguments, e.g. resume=None, fork=False - the builder + its binding live in Level-2 platform
    code). That binding lives in Level-2 code; the engine only stores + calls it."""
    _HEAD_BUILDERS[platform_id] = thunk


def derived_transport_invariants(platform: PlatformEntry) -> list[str]:
    """Derive the platform's transport invariants (the R1 input) LIVE from its registered head_builder
    thunk + its consumer_reserved_invariants.body_key_overrides (F-FIX-2). If no thunk is registered,
    fall back to the signal_sets.transport_invariants ALREADY populated at PlatformRegistry load
    (which itself was populated by derive_transport_invariants at load - never hand-typed). FAIL LOUD
    if NEITHER is available (an empty R1 input silently demotes locked flags to R5 - forbidden)."""
    thunk = _HEAD_BUILDERS.get(platform.id)
    body_overrides = platform.consumer_reserved_invariants.body_key_overrides
    if thunk is not None:
        return rules.derive_transport_invariants(thunk, body_overrides)
    pre = list(platform.signal_sets.transport_invariants)
    if pre:
        return pre
    raise RuntimeError(
        f"platform {platform.id!r}: no head_builder thunk registered AND signal_sets.transport_"
        f"invariants is empty - the R1 (LOCKED) input cannot be derived. Register a head_builder "
        f"(register_head_builder) or populate transport_invariants at load via "
        f"derive_transport_invariants. Refusing to classify with an empty R1 set (it would silently "
        f"demote every locked transport flag to R5/SAFE). Fail loud.")


# ── CLASSIFY ─────────────────────────────────────────────────────────────────────────────────

def classify_entries(entries: list[CapabilityEntry], platform: PlatformEntry, *,
                      novel_ids: Optional[set[str]] = None) -> list[CapabilityEntry]:
    """Run the 5 closed rules (rules.classify_with_novelty) over each FLAG entry and stamp posture +
    posture_rule + axis ONTO a copy of the entry. Non-flag kinds (tool/mcp_tool/...) are NOT flag-rule
    targets - they keep their default posture (the rules are the flag-classifier; other kinds carry
    their own posture model). The R1 input is the LIVE-derived transport-invariant set; the engine
    mutates a fresh SignalSets copy so the platform row's cached set is not the classify input of
    record (registry-is-truth: the derivation is the truth, the cache is a projection of it)."""
    novel_ids = novel_ids or set()
    # Build the live R1 input and substitute it into a working copy of the signal_sets so the rules
    # read the DERIVED set (F-FIX-2), not whatever was cached on the row.
    live_invariants = derived_transport_invariants(platform)
    signal_sets = platform.signal_sets.model_copy(update={"transport_invariants": live_invariants})

    classified: list[CapabilityEntry] = []
    for entry in entries:
        if entry.kind != "flag":
            classified.append(entry)
            continue
        is_novel = entry.id in novel_ids
        posture, rule, axis = rules.classify_with_novelty(
            entry.name, signal_sets, is_novel=is_novel)
        # carry the locked_reason teaching text for locked rows from body_key_overrides if present
        locked_reason = entry.locked_reason
        if posture in ("locked", "hazard") and not locked_reason:
            locked_reason = _locked_reason_for(entry.name, platform)
        classified.append(entry.model_copy(update={
            "posture": posture, "posture_rule": rule, "axis": axis,
            "locked_reason": locked_reason,
        }))
    return classified


def _locked_reason_for(flag_name: str, platform: PlatformEntry) -> str:
    """Look up the teaching-refusal text for a locked flag from the platform's body_key_overrides
    (each override may carry a 'why'/'reason'). Generic lookup by the flag string the override
    declares - no platform flag literals here."""
    for _key, spec in (platform.consumer_reserved_invariants.body_key_overrides or {}).items():
        if isinstance(spec, dict) and spec.get("flag") == flag_name:
            return str(spec.get("why") or spec.get("reason") or "")
    return ""


# ── PROJECT ──────────────────────────────────────────────────────────────────────────────────

def project(entries: list[CapabilityEntry]) -> dict:
    """Shape classified rows into a FACE-NEUTRAL projection the MCP tool / bridge route / cap://
    resolver all read. Not a face itself (the faces are LANE-PROJECTION) - the single shaped view they
    project from. counts: per-kind tally; postures: per-posture tally; entries: the rows (as dicts)."""
    counts: dict[str, int] = {}
    postures: dict[str, int] = {}
    for e in entries:
        counts[e.kind] = counts.get(e.kind, 0) + 1
        postures[e.posture] = postures.get(e.posture, 0) + 1
    return {
        "counts": counts,
        "postures": postures,
        "total": len(entries),
        "entries": [e.model_dump() for e in entries],
    }


# ── DISCOVER+CLASSIFY (the read half of the circuit) ───────────────────────────────────────────

def classify_platform(platform: PlatformEntry, *, executable: str | None = None,
                      version: str | None = None,
                      discover_fn: Callable[..., list[CapabilityEntry]] | None = None,
                      novel_ids: Optional[set[str]] = None) -> list[CapabilityEntry]:
    """DISCOVER then CLASSIFY a platform end-to-end. LEAD-only when discover_fn is the live discover
    (it spawns the binary). A unit test injects discover_fn=stub returning fixture rows + executable/
    version overrides to verify the classify+project path with NO live subprocess spawn."""
    discover_fn = discover_fn or run_discover
    entries = discover_fn(platform, executable=executable, version=version)
    return classify_entries(entries, platform, novel_ids=novel_ids)


def snapshot(platform: PlatformEntry, **kw) -> dict:
    """The full read: DISCOVER -> CLASSIFY -> PROJECT. Returns the projection dict."""
    return project(classify_platform(platform, **kw))


# ── REFRESH ────────────────────────────────────────────────────────────────────────────────────

def diff(prior: list[CapabilityEntry], current: list[CapabilityEntry]) -> dict:
    """Diff two CapabilityEntry lists by id -> {added, changed, vanished}. `changed` is an id present
    in both whose comparable shape (name/description/posture/takes_value/choices) differs. Used by the
    REFRESH verb to produce the inbox batch payload (F-FIX-4) + to drive novelty (added ids are the R4
    novelty set at refresh time, F-FIX-7)."""
    prior_by_id = {e.id: e for e in prior}
    cur_by_id = {e.id: e for e in current}
    prior_ids = set(prior_by_id)
    cur_ids = set(cur_by_id)
    added = sorted(cur_ids - prior_ids)
    vanished = sorted(prior_ids - cur_ids)
    changed = []
    for i in sorted(prior_ids & cur_ids):
        a, b = prior_by_id[i], cur_by_id[i]
        if _comparable(a) != _comparable(b):
            changed.append(i)
    return {"added": added, "changed": changed, "vanished": vanished}


def _comparable(e: CapabilityEntry) -> tuple:
    return (e.name, e.description, e.posture, e.takes_value, tuple(e.choices), e.value_type)


def refresh(platform: PlatformEntry, prior: list[CapabilityEntry], *,
            version_from: str = "", version_to: str = "",
            discover_fn: Callable[..., list[CapabilityEntry]] | None = None,
            **kw) -> dict:
    """REFRESH: re-DISCOVER + CLASSIFY (added ids are the R4 novelty set), diff against `prior`, and
    return the inbox batch payload shape (F-FIX-4): {added, changed, unclassified, vanished,
    version_from, version_to}. The flow (LANE-REFRESH) calls surface() ONCE with this payload and only
    writes the version stamp after curator approval (fail-closed write order, F-FIX-7).

    Guard: if version_to != version_from but the diff is empty, RAISE (a version bump with no surface
    change is a broken read - the empty-diff guard, C-REF-3). Same-version is a no-op for the caller."""
    discover_fn = discover_fn or run_discover
    # discover RAW first to compute novelty (added ids), then classify with that novelty set.
    raw_current = discover_fn(platform, **kw)
    prior_ids = {e.id for e in prior}
    novel_ids = {e.id for e in raw_current if e.id not in prior_ids}
    current = classify_entries(raw_current, platform, novel_ids=novel_ids)
    d = diff(prior, current)
    if version_to and version_from and version_to != version_from \
            and not (d["added"] or d["changed"] or d["vanished"]):
        raise RuntimeError(
            f"refresh: version changed {version_from!r} -> {version_to!r} but the capability diff is "
            f"EMPTY - a version bump that surfaces nothing is a broken read (wrong binary, parse "
            f"regression, or stale cache), never 'nothing changed across a version'. Fail loud "
            f"(the empty-diff guard, C-REF-3).")
    unclassified = [e.id for e in current if e.posture == "unmatched"]
    return {
        "added": d["added"],
        "changed": d["changed"],
        "vanished": d["vanished"],
        "unclassified": unclassified,
        "version_from": version_from,
        "version_to": version_to,
        "_current": current,   # the flow persists this as the new cache after approval
    }
