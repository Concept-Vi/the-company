#!/usr/bin/env python3
"""ops/ledger_fact_edges.py — FACT-edge harvest (F1a, Tim 2026-06-29).

The document/semantic graph the deterministic code-edges miss — but ONLY where the relationship is an OBSERVED
fact sitting in frontmatter (no model, no opinion). From channel-memory:
  attachments (att-*.md): attached_to → target ; in_channel → channel
  noticeboard (item-*.md): authored_by → session ; in_channel → channel ; + each typed `links[]` (kind→target)
Every edge cites its evidence (frontmatter) and carries a derivation TAG (no confidence). Idempotent: clears
its own prior pass='fact-edge' rows before re-inserting. A standing Company operation (reflects into ops).

Run:  python3 ops/ledger_fact_edges.py
"""
from __future__ import annotations
import json, os, subprocess, uuid

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PG = {"host": "127.0.0.1", "port": "15432", "user": "postgres", "db": "postgres", "pw": "postgres"}
import yaml


def _psql(sql: str) -> str:
    return subprocess.run(["psql", "-h", PG["host"], "-p", PG["port"], "-U", PG["user"], "-d", PG["db"], "-tAc", sql],
                          capture_output=True, text=True, env={**os.environ, "PGPASSWORD": PG["pw"]}).stdout


def _frontmatter(text: str) -> dict | None:
    if not text.lstrip().startswith("---"):
        return None
    body = text.lstrip()[3:]
    end = body.find("\n---")
    if end < 0:
        return None
    try:
        d = yaml.safe_load(body[:end])
        return d if isinstance(d, dict) else None
    except Exception:
        return None


def _addr(target: str, node_paths: set) -> str | None:
    """Resolve a frontmatter ref to a ledger node address where it maps to a real file (else None — honest)."""
    if isinstance(target, str) and target.startswith("board://item-"):
        p = f"channel-memory/noticeboard/{target[len('board://'):]}.md"
        if p in node_paths:
            return f"code://company/{p}"
    return None


def main():
    rid = _psql("select run_id from ledger.latest_run where project='company'").strip()
    if not rid:
        print("no company run"); return 1
    node_paths = set(p for p in _psql(
        "select path from ledger.entry e join ledger.latest_run r using(run_id) "
        "where r.project='company' and e.node_type='file'").splitlines() if p)
    files = [p for p in _psql(
        "select path from ledger.entry e join ledger.latest_run r using(run_id) where r.project='company' "
        "and e.node_type='file' and e.path ~ 'channel-memory/(channel_attachments|noticeboard)/'").splitlines() if p]
    print(f"harvesting from {len(files)} frontmatter files", flush=True)
    edges = []   # (kind, from_ref, to_raw, to_resolved)

    def emit(kind, frm, to_raw, to_res):
        if to_raw:
            edges.append((kind, frm, str(to_raw), to_res))

    for path in files:
        try:
            fm = _frontmatter(open(os.path.join(REPO, path), errors="replace").read())
        except Exception:
            fm = None
        if not fm:
            continue
        frm = f"code://company/{path}"
        ch = fm.get("channel")
        if ch:
            emit("in_channel", frm, f"channel://{ch}", None)
        if "channel_attachments/" in path:                       # attachment row
            tgt = fm.get("target")
            emit("attached_to", frm, tgt, _addr(tgt, node_paths))
        else:                                                    # noticeboard item
            au = fm.get("author_session")
            if au:
                emit("authored_by", frm, f"session://{au}", None)
            for lk in (fm.get("links") or []):
                if isinstance(lk, dict) and lk.get("target"):
                    emit(lk.get("kind") or "links_to", frm, lk["target"], _addr(lk["target"], node_paths))
            th = fm.get("thread")
            if th:
                emit("in_thread", frm, f"thread://{th}", None)

    print(f"emitted {len(edges)} fact-edges "
          f"({sum(1 for e in edges if e[3])} resolved to a node)", flush=True)
    by_kind = {}
    for k, *_ in edges:
        by_kind[k] = by_kind.get(k, 0) + 1
    print("by kind:", dict(sorted(by_kind.items(), key=lambda x: -x[1])))

    # bulk write: clear prior fact-edges for this run, then CSV \copy
    import csv
    scratch = os.environ.get("CLAUDE_JOB_DIR", "/tmp")
    csvp, sqlp = os.path.join(scratch, "fe.csv"), os.path.join(scratch, "fe.sql")
    now = _psql("select now()").strip()
    extra = json.dumps({"derivation": "frontmatter", "evidence": "channel-memory frontmatter"})
    with open(csvp, "w", newline="") as fh:
        w = csv.writer(fh)
        for kind, frm, to_raw, to_res in edges:
            w.writerow([str(uuid.uuid4()), rid, frm, kind, to_raw, to_res or "", extra, "fact-edge", now])
    open(sqlp, "w").write(
        f"delete from ledger.edge where pass='fact-edge' and run_id='{rid}';\n"
        "create temp table _fe(edge_id uuid, run_id uuid, from_ref text, kind text, to_raw text, "
        "to_resolved text, extra jsonb, pass text, extracted_at timestamptz);\n"
        f"\\copy _fe from '{csvp}' with (format csv, null '')\n"
        "insert into ledger.edge(edge_id,run_id,from_ref,kind,to_raw,to_resolved,extra,pass,extracted_at) "
        "select edge_id,run_id,from_ref,kind,to_raw,nullif(to_resolved,''),extra,pass,extracted_at from _fe;\n")
    r = subprocess.run(["psql", "-h", PG["host"], "-p", PG["port"], "-U", PG["user"], "-d", PG["db"],
                        "-v", "ON_ERROR_STOP=1", "-f", sqlp], capture_output=True, text=True,
                       env={**os.environ, "PGPASSWORD": PG["pw"]})
    print(r.stdout.strip() or r.stderr.strip()[:400])
    print("fact-edges in ledger:", _psql(f"select count(*) from ledger.edge where pass='fact-edge'").strip())


if __name__ == "__main__":
    raise SystemExit(main())
