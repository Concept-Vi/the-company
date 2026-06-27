"""orienteering_drift — a structural coherence detector for the terrain ledger (orienteering/).

Declared INTO the coherence substrate, not beside it: it emits findings in the SAME shape
`coherence_detect` uses, folds them with the SAME `burn_down`/`reconcile`, and rides `company suites`
via its acceptance test. Two checks, split by trust exactly as the substrate's discipline requires:

  EXACT (gate-able) · `entry-path-missing` — a ledger entry whose `path:` no longer exists on disk
                       (catches a move/delete like foundation's). A path either exists or it does not —
                       trustworthy, fails the gate on a NEW one. The whole point: the ledger can't
                       silently rot when a thing moves.
  CANDIDATE (propose) · `orbit-uncatalogued` — a top-level home-dir thing with neither a ledger entry
                       (or a parent of one) nor a row in `_orbit-dispositions.json`. "Should this be in
                       the ledger?" is a judgment (the is-it-company? problem), so it is POSITIVE-ONLY:
                       surfaces for Tim, NEVER auto-fails and NEVER auto-classifies. Mirrors
                       `coherence_detect.capability_no_consumer`.

The disposition registry (`orienteering/_orbit-dispositions.json`) is the declared "deliberately out of
the ledger" set — the `orphan-routes.json` pattern: catalogued = accounted-for, uncatalogued = surface,
stale = self-heals. Status/lifecycle is NEVER inferred here (the ledger's confirmed-only rule).
"""
from __future__ import annotations

import glob
import json
import os
import re

from runtime.coherence_detect import burn_down, reconcile, _handle  # reuse the finding model (one substrate)

ENTRIES_GLOB = "orienteering/entries/*.md"
DISPOSITIONS_REL = "orienteering/_orbit-dispositions.json"
HOME = os.path.expanduser("~")


def _entry_path(md_text: str) -> str | None:
    m = re.search(r"(?m)^path:\s*(.+?)\s*$", md_text)
    return m.group(1).strip() if m else None


def entry_paths(repo_root: str) -> dict[str, str]:
    """{slug: absolute path} from every ledger entry's `path:` frontmatter (the things the ledger claims exist)."""
    out: dict[str, str] = {}
    for f in glob.glob(os.path.join(repo_root, ENTRIES_GLOB)):
        slug = os.path.basename(f)[:-3]
        p = _entry_path(open(f, errors="ignore").read())
        if p:
            out[slug] = os.path.expanduser(p).rstrip("/")
    return out


def path_existence(repo_root: str) -> list[dict]:
    """EXACT (gate-able): ledger entries whose `path:` no longer exists on disk. Trustworthy — a path is or
    is not there; no heuristic. Returns [{slug, path}] sorted."""
    return [{"slug": slug, "path": p}
            for slug, p in sorted(entry_paths(repo_root).items()) if not os.path.exists(p)]


def _dispositions(repo_root: str) -> dict:
    path = os.path.join(repo_root, DISPOSITIONS_REL)
    if not os.path.exists(path):                          # fail loud — never treat the whole orbit as uncatalogued
        raise FileNotFoundError(f"orbit-dispositions registry missing: {path}")
    return json.load(open(path, encoding="utf-8")).get("paths", {})


def orbit_coverage(repo_root: str) -> dict:
    """CANDIDATE (positive-only): top-level home-dir DIRS that are neither covered by a ledger entry (the dir
    equals or contains a ledger path) nor declared in the disposition registry → `uncatalogued` (surface for
    Tim, never auto-fail). `stale` = dispositioned paths that no longer exist (self-heal signal). Never
    classifies; never decides is-it-company — only "accounted-for vs not"."""
    ledger = set(entry_paths(repo_root).values())
    disp = _dispositions(repo_root)
    disp_paths = {os.path.expanduser(k).rstrip("/") for k in disp}

    def covered(d: str) -> bool:
        return any(p == d or p.startswith(d + "/") for p in ledger)

    top = [os.path.join(HOME, n).rstrip("/") for n in sorted(os.listdir(HOME))
           if os.path.isdir(os.path.join(HOME, n))]
    uncatalogued = sorted(d for d in top if not covered(d) and d not in disp_paths)
    stale = sorted(d for d in disp_paths if not os.path.exists(d))
    return {"uncatalogued": uncatalogued, "stale": stale}


def record_orienteering_findings(store, repo_root: str) -> dict:
    """Write the EXACT findings into the store so the substrate flows end-to-end (detector → finding-store →
    burn_down) on real data. Each missing entry-path lands as an `entry-path-missing` finding, undispositioned
    → open (the burn-down target). The CANDIDATE orbit-coverage is NOT written here (positive-only, like
    capability-no-consumer — it never inflates the must-fix count). Returns {recorded}."""
    recorded = 0
    for m in path_existence(repo_root):
        store.append_finding({"kind": "entry-path-missing", "address": f"orienteering://{m['slug']}",
                              "path": m["path"], "state": "ledger-path-vanished",
                              "source": "structural", "owner": "orienteering"})
        recorded += 1
    return {"recorded": recorded}


def orienteering_signoff(repo_root: str) -> dict:
    """The gate boolean: PASS iff no ledger entry's path has vanished (the exact, gate-able check). The
    candidate orbit-coverage and stale dispositions are reported but NEVER fail the gate (surface/self-heal).
    Returns {pass, reasons, evidence}."""
    missing = path_existence(repo_root)
    cov = orbit_coverage(repo_root)
    reasons = []
    if missing:
        reasons.append(f"ledger entries whose path vanished (the ledger has rotted): {[m['slug'] for m in missing]}")
    return {"pass": not missing, "reasons": reasons,
            "evidence": {"missing": missing, "uncatalogued": cov["uncatalogued"], "stale": cov["stale"],
                         "entries": len(entry_paths(repo_root))}}


def scan(repo_root: str, store=None) -> dict:
    """The on-demand read (own/reflect: re-derived each call, no maintained state). Records the exact findings
    into `store` (a fresh temp store if none) + folds burn_down, and runs the candidate orbit-coverage as a
    separate positive-only report. Returns {burn_down, orbit}."""
    if store is None:
        import tempfile
        from store.fs_store import FsStore
        store = FsStore(os.path.join(tempfile.mkdtemp(prefix="orienteering-drift-"), "store"))
    record_orienteering_findings(store, repo_root)
    return {"burn_down": burn_down(store), "orbit": orbit_coverage(repo_root)}


def format_scan(result: dict) -> str:
    """Render scannably (the FORM bar): the exact must-fix headline, then the positive-only candidates."""
    b, o = result["burn_down"], result["orbit"]
    lines = [f"ORIENTEERING DRIFT — {b['open']} open · {b['accepted']} accepted · {b['closed']} closed"]
    if b["open_findings"]:
        lines.append("  OPEN (must-fix — a ledger path vanished):")
        for f in b["open_findings"]:
            lines.append(f"    [{f['kind']}] {f['address']}")
    lines.append(f"\n  candidates (positive-only — adjudicate/disposition, never auto-acted):")
    lines.append(f"    orbit-uncatalogued ({len(o['uncatalogued'])}): "
                 + (", ".join(os.path.basename(p) for p in o['uncatalogued'][:12]) + (" …" if len(o['uncatalogued']) > 12 else "") if o['uncatalogued'] else "—"))
    if o["stale"]:
        lines.append(f"    stale dispositions (path gone, self-heal): {[os.path.basename(p) for p in o['stale']]}")
    return "\n".join(lines)
