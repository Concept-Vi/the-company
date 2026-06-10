"""flows/floor_walk.py — the FLOOR WALK: the standing cross-lane sweep for dead/stranded/half-wired
work (born from Tim's wide-pass directive, 2026-06-10: "this is a 100% AI driven system so if it
hasn't been done it won't be" — the walking-the-floor function a human company gets for free).

DETERMINISTIC (no model). Four detectors, each a known death-mode from the lived record:
  1 STRANDED FILES — untracked/modified files whose mtime is OLDER than `stranded_after_s`
    (in-flight work is younger and is NEVER flagged — a rolling sweep must not grab another
    session's mid-edit; the wide pass ran on a settled tree, this preserves that property).
  2 UNMOUNTED COMPONENTS — canvas/app/src/components/*.tsx never imported by any other src file
    (the RegistryProposals death-mode: built, never placed).
  3 STALE DECISIONS — surfaced items unresolved + un-retired for longer than `stale_decision_days`
    (the ~38-item inbox-litter death-mode).
  4 PHANTOM CORPUS SOURCES — corpus records whose code:// source no longer exists on disk
    (the deleted-file staleness the radar skips per-run; here they're INVENTORIED).

PROPOSES ONLY: writes .build/floor-walk/report.json + (when findings exist) surfaces ONE review
card. Adoption/completion stays judgment work — the lead or the owning lane acts on the report;
nothing is auto-committed, auto-mounted, or auto-retired."""
import json
import os
import re
import subprocess
import time

FLOW = {
    "id": "floor_walk",
    "label": "Floor walk (stranded work · unmounted components · stale decisions · phantom sources)",
    "description": (
        "The standing cross-lane sweep for work that died between sessions: stranded uncommitted "
        "files (old enough to not be in-flight), built-but-never-mounted canvas components, "
        "decision cards nobody resolved or retired, and corpus records whose source files are gone. "
        "Deterministic, read-only detectors; writes a report and surfaces one card when findings "
        "exist. Adoption is judgment work the report feeds — nothing is auto-fixed."),
    "params": {
        "stranded_after_s": {"desc": "an uncommitted file older than this is stranded, not in-flight",
                             "default": 7200},
        "stale_decision_days": {"desc": "an unresolved decision older than this is litter",
                                "default": 7},
        "surface": {"desc": "1 = surface a review card when findings exist; 0 = report-only",
                    "default": 1},
    },
    "proposes_only": True,
}


def run(stranded_after_s: int = 7200, stale_decision_days: int = 7, surface: int = 1) -> dict:
    import sys
    sys.path.insert(0, "/home/tim/company")
    os.chdir("/home/tim/company")
    now = time.time()

    # 1 · STRANDED FILES (settled-only — never another session's live edit)
    stranded = []
    out = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout
    for line in out.splitlines():
        status, path = line[:2], line[3:].strip()
        p = path.rstrip("/")
        try:
            newest = max((os.path.getmtime(os.path.join(r, f))
                          for r, _d, fs in os.walk(p) for f in fs), default=0) \
                if os.path.isdir(p) else os.path.getmtime(p)
        except OSError:
            newest = 0
        if newest and now - newest > stranded_after_s:
            stranded.append({"path": p, "git": status.strip(),
                             "settled_hours": round((now - newest) / 3600, 1)})

    # 2 · UNMOUNTED COMPONENTS (built, never imported)
    unmounted = []
    comp_dir = "canvas/app/src/components"
    if os.path.isdir(comp_dir):
        src_text = ""
        for r, _d, fs in os.walk("canvas/app/src"):
            for f in fs:
                if f.endswith((".tsx", ".ts")):
                    try:
                        src_text += open(os.path.join(r, f), encoding="utf-8").read()
                    except OSError:
                        pass
        for f in sorted(os.listdir(comp_dir)):
            if not f.endswith(".tsx") or f.startswith("_"):
                continue
            stem = f[:-4]
            # imported anywhere OTHER than its own file?
            own = open(os.path.join(comp_dir, f), encoding="utf-8").read()
            rest = src_text.replace(own, "", 1)
            if not re.search(rf"from\s+['\"][^'\"]*components/{re.escape(stem)}['\"]", rest):
                unmounted.append({"component": f, "death_mode": "built-but-never-imported"})

    # 3 · STALE DECISIONS (unresolved + un-retired + old)
    from runtime.suite import Suite
    from runtime.registry import NodeRegistry
    from store.fs_store import FsStore
    s = Suite(FsStore(".data/store"), NodeRegistry().discover(["nodes"]), nodes_dir="nodes")
    stale = []
    cutoff_days = stale_decision_days
    for it in s.inbox.list():
        if it.get("resolved") is not None or it.get("status") in ("requeue", "implemented", "resolved"):
            continue
        ts = it.get("ts") or 0
        age_d = (now - ts) / 86400 if ts else None
        if age_d is None or age_d > cutoff_days:
            p = it.get("payload") or {}
            stale.append({"id": it.get("id"), "action": it.get("action"),
                          "title": (p.get("title") or p.get("id") or "")[:60],
                          "age_days": round(age_d, 1) if age_d else "unknown"})

    # 4 · PHANTOM CORPUS SOURCES (records whose code:// file is gone)
    phantoms = []
    for r in s.list_corpus(project="company"):
        sa = r.get("source_address") or ""
        if sa.startswith("code://"):
            p = sa[len("code://"):]
            if not p.startswith("/") and not os.path.exists(p):
                phantoms.append(sa)
    phantoms = sorted(set(phantoms))

    report = {"ts": now, "stranded_files": stranded, "unmounted_components": unmounted,
              "stale_decisions": stale, "phantom_sources": phantoms,
              "totals": {"stranded": len(stranded), "unmounted": len(unmounted),
                         "stale": len(stale), "phantoms": len(phantoms)}}
    os.makedirs(".build/floor-walk", exist_ok=True)
    json.dump(report, open(".build/floor-walk/report.json", "w"), indent=1)

    n = sum(report["totals"].values())
    if n and surface:
        # ONE card, dup-guarded (a live floor-walk card → update the artifact only, no second card)
        live = any((it.get("payload") or {}).get("kind") == "floor_walk_report"
                   and it.get("resolved") is None and it.get("status") not in ("requeue", "implemented")
                   for it in s.inbox.list())
        if not live:
            s.surface_review({
                "title": f"Floor walk: {n} findings ({len(stranded)} stranded · {len(unmounted)} unmounted "
                         f"· {len(stale)} stale decisions · {len(phantoms)} phantom sources)",
                "kind": "floor_walk_report",
                "summary": ("The standing sweep for work that died between sessions. The report names "
                            "each item and its death-mode; adoption/completion is the follow-up work."),
                "artifact": ".build/floor-walk/report.json", **report["totals"]},
                origin="responsive")
    return report["totals"] | {"report": ".build/floor-walk/report.json", "surfaced": bool(n and surface)}
