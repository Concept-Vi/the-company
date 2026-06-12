"""ops/render_declared_stream.py — the R1.2 CONSUMER: render a session's stream FROM ITS
DECLARATIONS (Session Fabric R1.2 proof half 2).

The renderer dispatches ONLY on declaration content (component · placement · fields) — it
never inspects the raw event's type. That is the proof the declaration layer is sufficient:
if every event of a REAL stream renders through this path with zero undeclared and zero
exceptions, a UI given only the registry can draw the whole stream. Un-pretty is fine (the
R1.2 bar); the Face makes it beautiful later from the SAME declarations.

Usage:
  .venv/bin/python ops/render_declared_stream.py <capture.jsonl> [...]   render file(s), report
  .venv/bin/python ops/render_declared_stream.py --scan-corpus           declare EVERY line of
        every real transcript (~/.claude/projects/*/*.jsonl) + every T2 stream capture
        (~/xsession-tests/**/*.jsonl); print per-render_key counts; exit 1 if ANY event is
        undeclared (the completeness proof over reality).

Exit: 0 = every event declared+rendered · 1 = undeclared/family-gap events found (listed).
"""
from __future__ import annotations

import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runtime import render_declaration as rd


def render_one(dec: dict) -> str:
    """ONE rendered line per declared unit — from the declaration only."""
    comp = dec.get("component", "?")
    place = dec.get("placement", "?")
    fields = dec.get("fields") or {}
    bits = []
    for k, v in fields.items():
        if k.endswith("__truncated"):
            continue
        s = json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v
        s = s.replace("\n", "\\n")
        if len(s) > 120:
            s = s[:117] + "..."
        bits.append(f"{k}={s}")
    flags = "".join(
        f" <{f}>" for f in ("undeclared", "family_fallback", "blocks_execution", "is_terminal")
        if dec.get(f))
    line = f"[{place}·{comp}]{flags} {dec.get('render_key')}  " + " ".join(bits)
    out = [line]
    for b in dec.get("blocks") or []:
        out.append("    " + render_one(b))
    return "\n".join(out)


def render_file(path: str, *, quiet: bool = False) -> dict:
    """Declare + render every line of one capture/transcript. Returns the tally."""
    tally = {"events": 0, "rendered": 0, "undeclared": [], "family": [], "non_json": 0,
             "by_key": {}}
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except ValueError:
                tally["non_json"] += 1
                continue
            tally["events"] += 1
            dec = rd.declare(ev)
            text = render_one(dec)        # the consumption — must render, not just classify
            if not text:
                raise AssertionError(f"renderer produced nothing for {dec.get('render_key')}")
            tally["rendered"] += 1
            tally["by_key"][dec["render_key"]] = tally["by_key"].get(dec["render_key"], 0) + 1
            if dec.get("undeclared"):
                tally["undeclared"].append(dec["render_key"])
            if dec.get("family_fallback"):
                tally["family"].append(dec["render_key"])
            for b in dec.get("blocks") or []:
                tally["by_key"][b["render_key"]] = tally["by_key"].get(b["render_key"], 0) + 1
                if b.get("undeclared"):
                    tally["undeclared"].append(b["render_key"])
            if not quiet:
                print(text)
    return tally


def scan_corpus() -> int:
    files = sorted(glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl"))) + \
            sorted(glob.glob(os.path.expanduser("~/xsession-tests/**/*.jsonl"), recursive=True))
    total = {"files": 0, "events": 0, "undeclared": {}, "family": {}, "by_key": {}}
    for fp in files:
        try:
            t = render_file(fp, quiet=True)
        except Exception as e:
            print(f"FILE ERROR {fp}: {e}", file=sys.stderr)
            continue
        total["files"] += 1
        total["events"] += t["events"]
        for k, v in t["by_key"].items():
            total["by_key"][k] = total["by_key"].get(k, 0) + v
        for k in t["undeclared"]:
            total["undeclared"][k] = total["undeclared"].get(k, 0) + 1
        for k in t["family"]:
            total["family"][k] = total["family"].get(k, 0) + 1
    print(f"scanned {total['files']} files · {total['events']} events")
    print("== render_key counts ==")
    for k in sorted(total["by_key"]):
        print(f"  {k}: {total['by_key'][k]}")
    if total["family"]:
        print("== family-fallback hits (registry wants exact entries — gap-pressure) ==")
        for k, v in total["family"].items():
            print(f"  {k}: {v}")
    if total["undeclared"]:
        print("== UNDECLARED (FAIL — every emit must map) ==")
        for k, v in total["undeclared"].items():
            print(f"  {k}: {v}")
        return 1
    print("ZERO undeclared — every real event maps to a declaration.")
    return 0


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == "--scan-corpus":
        return scan_corpus()
    rc = 0
    for path in argv:
        t = render_file(path)
        print(f"-- {path}: {t['events']} events · {t['rendered']} rendered · "
              f"{len(t['undeclared'])} undeclared · {len(t['family'])} family-fallback")
        if t["undeclared"]:
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
