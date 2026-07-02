#!/usr/bin/env python3
"""ops/migrate_board_from_cvi.py — ④ L6-BOARD: the 319-post pour + the scope/author backfill + the
DERIVED Postgres projection (organ-studies/BOARD.md §3 "Data landing" · COMPLETION-CRITERIA C6.3/C6.4).

Three slices (each idempotent + re-runnable; `--slice all` runs them in order):

  --slice pour      The 319 cloud notice_board_posts land as file-per-item board records
                    (channel-memory/noticeboard/<uuid>.md — FILES FIRST, the system of record):
                      · post_id KEPT as the item id (board://<uuid> — identity preserved)
                      · post_type → type (issue/request exist; observation, milestone, design, task,
                        blocker, cognitive_guide, research, diagnostic = the 8 new item_types/ rows)
                      · status → state, landed DIRECTLY (validated ∈ the type's declared states —
                        the legacy open/resolved/closed honoured on every receiving type; fail-loud)
                      · content.title → title · content.description → body
                      · EVERY other content key (the 35-key long tail: priority, issue_number,
                        root_cause, workaround, …) preserved AS-IS in the open frontmatter — zero drop
                      · resolved_by / closed_by / resolved_note / resolution → SYNTHESIZED history
                        entries ({to, by, note}) — A's only authorship traces become provenance
                      · project_id → scope (project://<key>, the address)
                      · created_at/updated_at preserved · source = 'cvi_mine' (a source_types/ row)
                      · NO author was ever recorded (author_type NULL ×319, verified) → author lands
                        as the honest agent://unknown, never fabricated
                    The STALE projects.notice_board JSONB is NOT migrated (the superseded copy of the
                    same rows — A1's smoking-gun negative evidence); ONE provenance note is filed
                    instead (a fixed-id board note, idempotent).

  --slice backfill  The pre-address engine items (the ~690) get scope/author STAMPED DURABLY into
                    their frontmatter (channel → channel://<name>, '' → global; author_session → the
                    author address), then the DERIVED authored_by index is rebuilt
                    (cc_board.rebuild_authored_by_index — the O(1) reverse, C6.1).

  --slice project   The DERIVED Postgres projection (container.board_items, 0020_board_projection.sql):
                    a FULL re-derive — delete every row, re-insert one row per file. The files stay
                    truth; the table is the read side for dashboards/counts/RLS (A2's strength) and is
                    reproducible: delete + re-derive = identical counts (C6.4).

LAWS: cvi_mine is NEVER mutated (read-only SELECTs) · reconciliation with printed denominators
(319 = landed + excluded; sums must CLOSE or the pour raises) · every curation excluded-with-reason ·
fail-loud with breadcrumbs · files author, the DB is derived one-way (law 3) · idempotent.

Run:  .venv/bin/python ops/migrate_board_from_cvi.py --slice all
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from runtime import cc_board as cb  # noqa: E402

# one convention with ops/migrate_container_from_cvi.py (env-overridable)
PGCONF = {"host": os.environ.get("COMPANY_LEDGER_PGHOST", "127.0.0.1"),
          "port": os.environ.get("COMPANY_LEDGER_PGPORT", "15432"),
          "user": os.environ.get("COMPANY_LEDGER_PGUSER", "postgres"),
          "db": os.environ.get("COMPANY_LEDGER_PGDB", "postgres"),
          "pw": os.environ.get("COMPANY_LEDGER_PGPASSWORD", "postgres")}
CVI_DB = os.environ.get("COMPANY_CVI_DB", "cvi_mine")   # the immutable source-of-record (READ-ONLY)

PROVENANCE_NOTE_ID = "cvi-stale-jsonb-provenance"       # fixed id → the one note is idempotent

BREADCRUMB_0020 = ("expected container.board_items (0020_board_projection.sql); previously nothing "
                   "(the board had no DB projection); fix: PGPASSWORD=postgres psql -h "
                   f"{PGCONF['host']} -p {PGCONF['port']} -U {PGCONF['user']} -d {PGCONF['db']} "
                   "-f build-prep/claude-design/supabase/supabase/migrations/0020_board_projection.sql")


def _psql(db: str, sql: str) -> str:
    env = {**os.environ, "PGPASSWORD": PGCONF["pw"]}
    r = subprocess.run(["psql", "-h", PGCONF["host"], "-p", PGCONF["port"], "-U", PGCONF["user"],
                        "-d", db, "-v", "ON_ERROR_STOP=1", "-tA", "-c", sql],
                       capture_output=True, text=True, env=env)
    if r.returncode != 0:
        raise RuntimeError(f"psql({db}) failed: {r.stderr.strip()[:600]}\nSQL head: {sql[:200]}")
    return r.stdout


def _psql_script(db: str, sql: str) -> str:
    env = {**os.environ, "PGPASSWORD": PGCONF["pw"]}
    r = subprocess.run(["psql", "-h", PGCONF["host"], "-p", PGCONF["port"], "-U", PGCONF["user"],
                        "-d", db, "-v", "ON_ERROR_STOP=1"],
                       input=sql, capture_output=True, text=True, env=env)
    if r.returncode != 0:
        raise RuntimeError(f"psql script({db}) failed (transaction rolled back): {r.stderr.strip()[:600]}")
    return r.stdout


def _json_rows(db: str, sql: str) -> list[dict]:
    out = _psql(db, f"select coalesce(json_agg(t), '[]'::json) from ({sql}) t")
    return json.loads(out.strip() or "[]")


def _dq(s) -> str:
    """Dollar-quote with a tag guaranteed absent (the migrate_container_from_cvi._dq pattern)."""
    s = str(s)
    i = 0
    while True:
        tag = f"$q{i}$"
        if tag not in s:
            return f"{tag}{s}{tag}"
        i += 1


def _lit(v) -> str:
    return "NULL" if v is None else _dq(v)


def _jsonb(v) -> str:
    return "NULL" if v is None else _dq(json.dumps(v, default=str)) + "::jsonb"


# ── slice: pour (C6.3) ──────────────────────────────────────────────────────────────────────────────────
def pour(board_dir: str | None = None) -> dict:
    """The 319 → the file-per-item store. FILES FIRST (system of record); the DB projection is the
    separate `project` slice. Idempotent: an already-landed uuid is skipped (counted, never re-written)."""
    posts = _json_rows(CVI_DB, "select post_id, project_id, post_type, status, content, "
                               "created_at, updated_at from notice_board_posts")
    pmap = {r["project_id"]: r["project_key"]
            for r in _json_rows(CVI_DB, "select project_id, project_key from projects")}
    rep = {"source": len(posts), "landed_new": 0, "landed_already": 0, "excluded": 0,
           "by_type": {}, "renamed_keys": {}}
    core = set(cb.FRONTMATTER_KEYS) | {"body"}
    for p in posts:
        pkey = pmap.get(p["project_id"])
        if not pkey:
            # every curation excluded-with-reason — but an unmapped project is source DRIFT, fail loud
            raise RuntimeError(f"post {p['post_id']} has project_id {p['project_id']} with no cvi_mine "
                               f"projects row — source drifted; the pour never silently drops. Fail loud.")
        content = p.get("content") or {}
        title = content.get("title") or f"({p['post_type']} #{content.get('issue_number', '?')} — untitled)"
        body = content.get("description") or ""
        # the long tail: EVERY content key except the two mapped ones, preserved verbatim.
        extra = {}
        for k, v in content.items():
            if k in ("title", "description"):
                continue
            if k in core:   # a content key that would shadow a core frontmatter key (none observed; guard)
                extra[f"content_{k}"] = v
                rep["renamed_keys"][k] = f"content_{k}"
            else:
                extra[k] = v
        extra["source_meta"] = {"source_table": "notice_board_posts", "source_db": CVI_DB,
                                "cloud_project_id": p["project_id"], "cloud_project_key": pkey}
        # resolver-names → SYNTHESIZED history (A's only authorship traces become provenance)
        status = p["status"]
        hist = [{"from": None, "to": "open", "by": "",
                 "ts": p["created_at"], "note": "filed (cvi_mine notice_board_posts pour)"}]
        if status in ("resolved", "closed"):
            by = content.get("resolved_by") if status == "resolved" else content.get("closed_by")
            note = content.get("resolved_note") or content.get("resolution") or ""
            hist.append({"from": "open", "to": status, "by": by or "", "ts": p["updated_at"],
                         "note": note or f"{status} (cloud status at pour time)"})
        iid = p["post_id"]                                  # uuid ids KEPT (identity preserved)
        if os.path.exists(os.path.join(cb._dir(board_dir), f"{iid}.md")):
            rep["landed_already"] += 1
        else:
            cb.file_item(p["post_type"], title, body, "",     # author never recorded (author_type NULL x319)
                         source="cvi_mine", scope=f"project://{pkey}",
                         item_id=iid, state=status, extra=extra,
                         created=p["created_at"], updated=p["updated_at"], history=hist,
                         board_dir=board_dir)
            rep["landed_new"] += 1
        rep["by_type"][p["post_type"]] = rep["by_type"].get(p["post_type"], 0) + 1
    # THE STALE JSONB — NOT migrated; ONE provenance note (fixed id → idempotent).
    if not os.path.exists(os.path.join(cb._dir(board_dir), f"{PROVENANCE_NOTE_ID}.md")):
        cb.file_item(
            "note", "Provenance: the stale projects.notice_board JSONB was NOT migrated",
            ("④ L6-BOARD pour provenance (organ-studies/BOARD.md §1 A1): the cloud carried the board TWICE — "
             "the normalized notice_board_posts table (319 rows, POURED losslessly onto this board with their "
             "uuids) and an embedded projects.notice_board JSONB array (the SUPERSEDED copy of the same rows: "
             "block-composition's froze at 128 while the table grew to 279; the three small projects' JSONB "
             "equals their table rows). Migration 20260412070000's own header is the smoking gun: the "
             "dashboard read the corpse. The JSONB is therefore NOT migrated — it is the family's negative "
             "evidence that a board projected into a container must be DERIVED, never stored there (the law "
             "container.board_items now obeys). Source: cvi_mine (read-only)."),
            "", source="cvi_mine", scope="project://the-fusion",
            item_id=PROVENANCE_NOTE_ID, board_dir=board_dir)
        rep["provenance_note"] = f"board://{PROVENANCE_NOTE_ID} (filed)"
    else:
        rep["provenance_note"] = f"board://{PROVENANCE_NOTE_ID} (already present)"
    landed = rep["landed_new"] + rep["landed_already"]
    rep["reconciliation"] = f"{rep['source']} = {landed} landed ({rep['landed_new']} new + " \
                            f"{rep['landed_already']} already) + {rep['excluded']} excluded"
    if rep["source"] != landed + rep["excluded"]:
        raise RuntimeError(f"pour reconciliation FAILED: {rep['reconciliation']} — the sum must CLOSE. Fail loud.")
    return rep


# ── slice: backfill (C6.1 — the 690 gain scope/author durably + the derived index) ─────────────────────
def backfill(board_dir: str | None = None) -> dict:
    """Stamp scope/author into every item whose RAW frontmatter lacks them (the derivation get_item
    already applies on read, made durable), then rebuild the derived authored_by index."""
    d = cb._dir(board_dir)
    stamped = skipped = 0
    for fn in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if not fn.endswith(".md") or fn.startswith("_"):
            continue
        with open(os.path.join(d, fn), encoding="utf-8") as f:
            meta, _ = cb._split_frontmatter(f.read())
        if "scope" in meta and "author" in meta:
            skipped += 1
            continue
        rec = cb.get_item(fn[:-3], board_dir=board_dir)      # derives scope/author; raises on malformed
        cb._write(board_dir, rec)                            # durable stamp (same record, fields added)
        stamped += 1
    idx = cb.rebuild_authored_by_index(board_dir)
    return {"stamped": stamped, "already_addressed": skipped,
            "authored_by_index": {"items": idx["count"], "authors": idx["authors"]}}


# ── slice: project (C6.4 — the DERIVED Postgres projection, full re-derive) ────────────────────────────
def derive_projection(board_dir: str | None = None) -> dict:
    """files → container.board_items, a FULL one-way re-derive (delete all, insert from files). The files
    stay truth; deleting the projection and re-running reproduces identical counts (C6.4)."""
    if not _psql(PGCONF["db"], "select 1 from information_schema.tables where table_schema='container' "
                               "and table_name='board_items'").strip():
        raise RuntimeError(f"container.board_items missing — {BREADCRUMB_0020}")
    recs = cb.list_items(board_dir=board_dir)
    core = set(cb.FRONTMATTER_KEYS) | {"body"}
    sql = ["begin;", "delete from container.board_items;"]   # full re-derive: the derived side is disposable
    n = 0
    for rec in recs:
        extra = {k: v for k, v in rec.items() if k not in core and k != "source_meta"}
        row = {
            "id": rec["id"], "address": rec.get("address") or f"board://{rec['id']}",
            "type": rec.get("type"), "source": rec.get("source"), "state": rec.get("state"),
            "scope": rec.get("scope") or "global", "author": rec.get("author"),
            "title": rec.get("title"), "channel": rec.get("channel"),
            "author_session": rec.get("author_session"), "thread": rec.get("thread"),
        }
        sql.append(
            "insert into container.board_items (id, address, type, source, state, scope, author, title, "
            "channel, author_session, thread, links, history, extra, body, created_at, updated_at, source_meta) "
            f"values ({_dq(row['id'])}, {_dq(row['address'])}, {_dq(row['type'])}, {_lit(row['source'])}, "
            f"{_dq(row['state'])}, {_dq(row['scope'])}, {_lit(row['author'])}, {_lit(row['title'])}, "
            f"{_lit(row['channel'])}, {_lit(row['author_session'])}, {_lit(row['thread'])}, "
            f"{_jsonb(rec.get('links') or [])}, {_jsonb(rec.get('history') or [])}, {_jsonb(extra)}, "
            f"{_lit(rec.get('body'))}, {_lit(rec.get('created'))}::timestamptz, "
            f"{_lit(rec.get('updated'))}::timestamptz, {_jsonb(rec.get('source_meta'))});")
        n += 1
    # ONE transaction end-to-end (delete + every insert): the re-derive is all-or-nothing — a failed
    # insert rolls the delete back too, so the projection is never left half-derived.
    sql.append("commit;")
    _psql_script(PGCONF["db"], "\n".join(sql))
    db_n = int(_psql(PGCONF["db"], "select count(*) from container.board_items").strip())
    by_scope = _json_rows(PGCONF["db"], "select scope, count(*)::int as n from container.board_items "
                                        "group by scope order by n desc")
    if db_n != n:
        raise RuntimeError(f"projection derive mismatch: {n} files -> {db_n} rows — the derive must be "
                           f"lossless. Fail loud.")
    return {"files": n, "rows": db_n, "identical": db_n == n, "by_scope": by_scope}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slice", default="all", choices=["pour", "backfill", "project", "all"])
    a = ap.parse_args()
    rep: dict = {"slice": a.slice}
    if a.slice in ("pour", "all"):
        rep["pour"] = pour()
        print(f"  pour: {rep['pour']['reconciliation']}", file=sys.stderr)
    if a.slice in ("backfill", "all"):
        rep["backfill"] = backfill()
        print(f"  backfill: {rep['backfill']['stamped']} stamped, "
              f"{rep['backfill']['already_addressed']} already addressed", file=sys.stderr)
    if a.slice in ("project", "all"):
        rep["project"] = derive_projection()
        print(f"  projection: {rep['project']['files']} files -> {rep['project']['rows']} rows "
              f"(identical={rep['project']['identical']})", file=sys.stderr)
    print(json.dumps(rep, indent=2, default=str))


if __name__ == "__main__":
    main()
