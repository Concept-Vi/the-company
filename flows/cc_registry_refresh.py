"""flows/cc_registry_refresh.py — Mirror-Registry version-triggered refresh (LANE-REFRESH).

Reads the live platform version vs the stored stamp (store/<platform_id>.version_stamp); on a
mismatch, re-introspects (via the engine's DISCOVER+CLASSIFY), diffs against the prior snapshot,
and surfaces ONE cc_registry_gap inbox item (F-FIX-4: a single surface() call per version bump
with the full batch payload {added, changed, unclassified, vanished, version_from, version_to}).

THE STAMP WRITE IS NOT DONE BY THIS FLOW.  The flow is PROPOSE-ONLY (proposes_only: True, the
floor discipline).  The stamp write and cache update happen ONLY after curator approval through the
governance flow — the stamp is deliberately NOT advanced here.  If the operator never approves,
the stale-stamp warning from cc_registry_freshness_check.sh keeps firing at every SessionStart
(fail-closed: no fabricated-fresh snapshot).

SAME-VERSION FAST PATH: if the live version == the stored stamp, this flow returns immediately
with {"status": "unchanged", "version": <ver>} and calls surface() zero times.  No false novelty.

RETIRE-NOT-DELETE: vanished capabilities land in the payload's "vanished" list.  The CURATOR
APPROVAL step (governance, not this flow) flips their status to "retired" in the registry.

VERIFY WITHOUT A CLAUDE SPAWN (task mandate): the run() method accepts an injectable
discover_fn parameter (the test injects a stub); the default is None which activates the live
discover (LEAD-queued).  Same-version no-op is verified directly against the live binary.

Flow registration: id == "cc_registry_refresh" (file stem).
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FLOW = {
    "id": "cc_registry_refresh",
    "label": "Capability-registry version refresh (Mirror-Registry LANE-REFRESH)",
    "description": (
        "Compares the live Claude Code binary version against the stored version stamp "
        "(store/<platform_id>.version_stamp). On a mismatch, re-introspects the binary's "
        "capability surface (DISCOVER+CLASSIFY), diffs against the prior JSON snapshot "
        "(store/introspection_cache.json), and surfaces ONE 'cc_registry_gap' inbox item "
        "carrying the full diff payload {added, changed, unclassified, vanished, version_from, "
        "version_to}.  On a match, returns immediately (no surface, no novelty).  Stamp write "
        "happens ONLY after curator approval — this flow proposes, never advances the stamp."
    ),
    "params": {
        "discover_fn": {
            "desc": ("Optional callable(platform, *, executable, version) -> list[CapabilityEntry]. "
                     "Injected by tests to avoid a live binary spawn; omit for real operation."),
            "default": None,
        },
        "executable": {
            "desc": "Override the resolved binary path (used by tests alongside discover_fn).",
            "default": None,
        },
    },
    "proposes_only": True,
}


def _store_path() -> str:
    """Canonical path to the company store/ directory (flat operational files, not CAS)."""
    return os.path.join(ROOT, "store")


def _stamp_path(platform_id: str) -> str:
    """Per-platform version stamp: store/<platform_id>.version_stamp (direct open(), not FsStore
    CAS — F-FIX-15 / PG-D3 decision: flat operational file, not content-addressed)."""
    return os.path.join(_store_path(), f"{platform_id}.version_stamp")


def _cache_path() -> str:
    """Snapshot cache for the prior capability set: store/introspection_cache.json."""
    return os.path.join(_store_path(), "introspection_cache.json")


def _read_stamp(platform_id: str) -> str:
    """Read the stored version stamp.  Returns '' if the stamp file does not exist (a missing stamp
    means the registry has NEVER been built — treat as stale, always re-introspect on first run)."""
    p = _stamp_path(platform_id)
    if not os.path.exists(p):
        return ""
    with open(p, encoding="utf-8") as fh:
        return fh.read().strip()


def _read_cache() -> list:
    """Read the prior capability snapshot.  Returns [] if absent (first-run: diff against empty)."""
    p = _cache_path()
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as fh:
        try:
            data = json.load(fh)
        except Exception:
            return []  # corrupt cache → treat as empty; the new snapshot replaces it after approval
    return data if isinstance(data, list) else []


def _probe_live_version(platform) -> str:
    """Read the live binary version via the platform's VersionSource.  Fail loud on empty output."""
    sys.path.insert(0, ROOT)
    from introspection.discover import resolve_executable, probe_version
    exe = resolve_executable(platform)
    return probe_version(platform, exe)


def run(discover_fn=None, executable=None) -> dict:
    """Entry point.  Loaded and called by the MCP flows tool (op='run', flow='cc_registry_refresh').

    Parameters
    ----------
    discover_fn : callable, optional
        Injected by tests to avoid a live binary spawn.  Signature:
        (platform, *, executable=None, version=None) -> list[CapabilityEntry].
        Omit for real operation (the default live discover runs).
    executable : str, optional
        Override the resolved binary path (used by tests alongside discover_fn).

    Returns
    -------
    dict with keys:
      status        — 'unchanged' (same version) | 'surfaced' (diff surfaced) | 'first_run' (no prior stamp)
      version       — the live version string
      payload       — the diff payload (only present when status == 'surfaced' or 'first_run')
      surfaced_id   — the inbox sid returned by surface() (only present when a surface call was made)
    """
    sys.path.insert(0, ROOT)

    from contracts.capability_entry import CapabilityEntry
    from introspection.platforms import PlatformRegistry
    from introspection import engine as _engine

    # ── Resolve the PlatformEntry (instance #1 — claude-code) ─────────────────────────────────
    preg = PlatformRegistry().discover([os.path.join(ROOT, "platforms")])
    if "claude-code" not in preg:
        raise RuntimeError(
            "cc_registry_refresh: 'claude-code' PlatformEntry not found in PlatformRegistry "
            "(platforms/claude_code.py must be discoverable). Fail loud.")
    platform = preg["claude-code"]
    platform_id = platform.id

    # ── Read the stored stamp ────────────────────────────────────────────────────────────────────
    stored_version = _read_stamp(platform_id)
    is_first_run = (stored_version == "")

    # ── Probe the live version ───────────────────────────────────────────────────────────────────
    if executable is not None:
        # test/override path: call the probe with the supplied binary
        from introspection.discover import probe_version
        live_version = probe_version(platform, executable)
    else:
        live_version = _probe_live_version(platform)

    if not live_version:
        raise RuntimeError(
            "cc_registry_refresh: live version probe returned EMPTY — the binary is unreachable or "
            "the VersionSource.command produced no output. Fail loud (no fabricated version).")

    # ── SAME-VERSION FAST PATH ───────────────────────────────────────────────────────────────────
    if stored_version and stored_version == live_version:
        return {"status": "unchanged", "version": live_version}

    # ── Read the prior snapshot ──────────────────────────────────────────────────────────────────
    prior_raw = _read_cache()
    prior: list[CapabilityEntry] = []
    for row in prior_raw:
        try:
            prior.append(CapabilityEntry.model_validate(row))
        except Exception:
            pass  # corrupt row in cache → treated as absent from the prior set

    # ── DISCOVER + CLASSIFY the current surface ───────────────────────────────────────────────────
    # discover_fn injected for testing; None → the real live discover (LEAD-only path, spawns binary)
    payload = _engine.refresh(
        platform, prior,
        version_from=stored_version,
        version_to=live_version,
        discover_fn=discover_fn,
        executable=executable,
    )
    # _current holds the newly classified list; peel it for the cache (written post-approval, not here)
    new_entries: list[CapabilityEntry] = payload.pop("_current", [])

    # ── EMPTY-DIFF GUARD (also asserted by engine.refresh, but verify the contract) ──────────────
    # engine.refresh() already raises on version-changed + empty-diff; we don't double-raise here.
    # If we're on a first-run (no prior stamp → is_first_run) with the same discover, the diff vs
    # the empty prior will be non-empty (all flags are "added") — that is the expected first-run path.

    # ── SURFACE ONE inbox item (F-FIX-4 / PG-D4) ────────────────────────────────────────────────
    # One surface() call per version bump with the FULL batch payload.  The presentation layer
    # (MCP tool / RHM surface) renders confirm-all for high-confidence vs per-item for low.
    # default="reject" (fail-closed): a non-response means nothing enters the trusted surface.
    # The stamp is NOT written here — it is written ONLY after curator approval.
    surfaced_id = _surface_gap(
        action_class="cc_registry_gap",
        payload=payload,
        default="reject",
    )

    status = "first_run" if is_first_run else "surfaced"
    return {
        "status": status,
        "version": live_version,
        "payload": payload,
        "surfaced_id": surfaced_id,
        "_new_entries_for_post_approval_cache": [e.model_dump() for e in new_entries],
    }


def _surface_gap(action_class: str, payload: dict, default: str) -> str:
    """Surface the diff batch into the governance inbox.  Reaches governance via the stored FsStore
    (same path the Suite uses) so both faces (UI + MCP) see the same inbox."""
    from store.fs_store import FsStore
    from runtime.governance import Inbox
    store = FsStore(os.path.join(_store_path()))
    inbox = Inbox(store)
    return inbox.surface(action_class, payload, default=default)


def write_stamp_and_cache(platform_id: str, version: str, new_entries: list) -> None:
    """Write the version stamp AND the snapshot cache AFTER curator approval.  This is NOT called
    by run() — it is called by the post-approval governance action (LANE-REFRESH step 6 in the
    spec: stamp written ONLY after approval, fail-closed write order).  Exported here so the
    post-approval handler can import it without reimplementing the path logic.

    Writes:
      store/<platform_id>.version_stamp   — the new live version (one line)
      store/introspection_cache.json      — the new classified entry list (JSON array)
    """
    sp = _stamp_path(platform_id)
    os.makedirs(os.path.dirname(sp), exist_ok=True)
    with open(sp, "w", encoding="utf-8") as fh:
        fh.write(version + "\n")
    with open(_cache_path(), "w", encoding="utf-8") as fh:
        json.dump(new_entries, fh, indent=2)
