#!/usr/bin/env python3
"""ops/hooks/registry_freshness.py — registry-driven freshness check for ALL platforms.

The 'never touch again' generalization of the claude-only SessionStart check (Mirror-Registry,
LANE-REFRESH). Iterates every platforms/<id>.py that declares a `version_source`, probes its live
version, compares to store/<id>.version_stamp, and prints one `REGISTRY FRESHNESS [<id>]: …` line per
stale/never-built/unreachable platform. Silent for fresh ones. ALWAYS exits 0 (non-blocking — a stale
registry is a warning, never a hard session block). Drop a new platform row → it is checked here for
free, no edit. Fail-isolated per platform (one bad probe never blocks the others or the session)."""
from __future__ import annotations
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)


def _stamp(pid: str) -> str:
    p = os.path.join(ROOT, "store", f"{pid}.version_stamp")
    try:
        return open(p).read().strip()
    except OSError:
        return ""


def main() -> int:
    try:
        from introspection.platforms import PlatformRegistry
        from introspection import discover as D
    except Exception:
        return 0  # introspection unavailable → silent (never break session start)
    try:
        preg = PlatformRegistry().discover([os.path.join(ROOT, "platforms")])
        ids = sorted(preg.ids())
    except Exception:
        return 0
    for pid in ids:
        try:
            p = preg[pid]
            if not getattr(p, "version_source", None):
                continue  # platform declares no version → nothing to check
            try:
                exe = D.resolve_executable(p)
            except Exception:
                print(f"REGISTRY FRESHNESS [{pid}]: binary unreachable — cannot check.")
                continue
            try:
                live = D.probe_version(p, exe)
            except Exception:
                live = ""
            if not live:
                print(f"REGISTRY FRESHNESS [{pid}]: version probe empty — binary may be down.")
                continue
            stamped = _stamp(pid)
            if not stamped:
                print(f"REGISTRY FRESHNESS [{pid}]: never built — run flow cc_registry_refresh (platform_id={pid}).")
            elif stamped != live:
                print(f"REGISTRY FRESHNESS [{pid}]: STALE — stamp={stamped} live={live}. Run cc_registry_refresh (platform_id={pid}).")
            # fresh → silent
        except Exception:
            continue  # any per-platform error → skip it, never break the hook
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
