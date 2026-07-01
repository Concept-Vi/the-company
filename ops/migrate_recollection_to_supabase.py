#!/usr/bin/env python3
"""ops/migrate_recollection_to_supabase.py — the MEMORY half of the full-migrate.

Moves recollection's fingerprints (8222 conversation-exchange embeddings, sqlite, int8 2560-dim, addressed
`exchange://<sid>/<i>`) INTO the unified ledger.embedding as space='exchange' emb='pplx'. int8→halfvec
preserves cosine ranking (scale-invariant). Additive + idempotent (on-conflict). This lands the CONVERSATION
side alongside the CODE side in one store — the merge-intention spine, both halves in one place.
"""
from __future__ import annotations
import os, sqlite3, struct, subprocess, tempfile

DB = "/home/tim/company/.recollection/conversation-index/db.sqlite"
PG = ["psql", "-h", "127.0.0.1", "-p", "15432", "-U", "postgres", "-d", "postgres", "-v", "ON_ERROR_STOP=1"]
SCRATCH = os.environ.get("CLAUDE_JOB_DIR", "/tmp") + "/tmp"


def q(sql):
    return subprocess.run(PG + ["-tAc", sql], capture_output=True, text=True,
                          env={**os.environ, "PGPASSWORD": "postgres"}).stdout.strip()


def main():
    os.makedirs(SCRATCH, exist_ok=True)
    con = sqlite3.connect(DB)
    rows = con.execute("select source, model, dim, element_type, vector from fingerprints").fetchall()
    print(f"recollection fingerprints: {len(rows)}", flush=True)
    done = skipped = 0
    batch = []

    def flush():
        nonlocal done
        if not batch:
            return
        with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, dir=SCRATCH) as f:
            f.write("BEGIN;\n")
            for line in batch:
                f.write(line + "\n")
            f.write("COMMIT;\n")
            p = f.name
        r = subprocess.run(PG + ["-f", p], capture_output=True, text=True, env={**os.environ, "PGPASSWORD": "postgres"})
        os.unlink(p)
        if r.returncode != 0:
            raise RuntimeError(f"batch failed (rolled back): {r.stderr.strip()[:400]}")
        done += len(batch)
        batch.clear()

    for source, model, dim, etype, blob in rows:
        if not blob or not source:
            skipped += 1
            continue
        if etype == "int8":
            vals = struct.unpack(f"{len(blob)}b", blob)   # signed int8
        elif etype == "float":
            vals = struct.unpack(f"{len(blob)//4}f", blob)
        else:
            skipped += 1                                  # fail loud: unknown element_type recorded, not guessed
            print(f"  UNKNOWN element_type {etype} for {source[:40]} — skipped, not fabricated", flush=True)
            continue
        if len(vals) != dim:
            skipped += 1
            print(f"  DIM MISMATCH {len(vals)}!={dim} for {source[:40]} — skipped", flush=True)
            continue
        col = {3584: "vec_3584", 2560: "vec_2560", 1024: "vec_1024"}.get(dim)
        if not col:
            skipped += 1
            continue
        vec_lit = "[" + ",".join(repr(float(x)) for x in vals) + "]"
        src = source.replace("$q$", "")
        batch.append(
            f"insert into ledger.embedding (source_address,space,emb_layer,model,dim,content_hash,{col}) values "
            f"($q${src}$q$,'exchange','pplx',$q${model}$q$,{int(dim)},'recollection','{vec_lit}'::halfvec({dim})) "
            f"on conflict (source_address,space,emb_layer) do update set {col}=excluded.{col}, ts=now();")
        if len(batch) >= 200:
            flush()
            if done % 1000 == 0:
                print(f"  ...{done}/{len(rows)} migrated", flush=True)
    flush()
    con.close()
    n = q("select count(*) from ledger.embedding where space='exchange';")
    print(f"DONE: fingerprints={len(rows)} migrated={done} skipped={skipped} | Supabase space=exchange rows={n}", flush=True)
    print("  ✓" if n.isdigit() and int(n) == done else "  ⚠ CHECK")


if __name__ == "__main__":
    raise SystemExit(main())
