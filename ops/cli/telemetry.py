"""telemetry — the resource manager's memory.

Records REAL model loads (measured resident VRAM + load time) so the budget gate's
estimates become measured over time, and surfaces where the registry estimate is
wrong. This is the write-half of the introspective-data-building law (operation
self-instruments → run-records → rollups that improve it). Append-only JSONL,
stdlib-only. Keyed by SERVICE KEY (chat-4b, embed-bge, …)."""
import json, os, datetime

LOG = os.path.join(os.path.dirname(os.path.realpath(__file__)), "telemetry.jsonl")


def record(service, load_seconds, resident_mb, estimate_mb, model=None):
    rec = {"ts": datetime.datetime.now().isoformat(timespec="seconds"),
           "service": service, "load_seconds": round(load_seconds, 1),
           "resident_mb": resident_mb, "estimate_mb": estimate_mb, "model": model}
    with open(LOG, "a") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


def _read():
    if not os.path.exists(LOG):
        return []
    out = []
    for line in open(LOG):
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def learned_vram(service):
    """Most-recent MEASURED resident MB for a service, or None. The budget gate
    prefers this over the registry estimate when present."""
    recs = [r for r in _read() if r.get("service") == service and r.get("resident_mb")]
    return recs[-1]["resident_mb"] if recs else None


def rollups():
    """Per-service summary: load count, avg load time, last measured VRAM vs registry estimate."""
    recs = _read()
    if not recs:
        return "  no telemetry yet — run `company up <model> --wait` to record a real load."
    by = {}
    for r in recs:
        by.setdefault(r["service"], []).append(r)
    out = ["  service           loads  avg load   measured VRAM   registry est",
           "  " + "-" * 64]
    for svc, rs in sorted(by.items()):
        n = len(rs)
        avg_load = sum(x.get("load_seconds", 0) for x in rs) / n
        res = rs[-1].get("resident_mb")
        est = rs[-1].get("estimate_mb")
        flag = "  ⚠ estimate off — refine services.json vram_mb" if (res and est and abs(res - est) > 1500) else ""
        out.append(f"  {svc:<16} {n:>4}   {avg_load:>5.0f}s    ~{(res or 0)/1000:>5.1f} GB      "
                   f"~{(est or 0)/1000:>5.1f} GB{flag}")
    return "\n".join(out)
