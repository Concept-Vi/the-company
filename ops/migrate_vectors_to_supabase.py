#!/usr/bin/env python3
"""ops/migrate_vectors_to_supabase.py — S3: migrate FsStore vector spaces into ledger.embedding (Supabase).

Reads the FsStore vectors/ records for a space and upserts them into the unified pgvector table
(ledger.embedding) — the right per-dim halfvec column by dim (3584 nomic / 2560 pplx / 1024 bge). Additive
+ idempotent (unique on source_address,space,emb_layer → on-conflict update). Batched (DB wedged before under
heavy passes). Verifies per space: FsStore count == Supabase row count. KEEP FsStore as the source-of-truth
fallback until the read path is cut over.

Run:  python ops/migrate_vectors_to_supabase.py --space code
      python ops/migrate_vectors_to_supabase.py --space code,symbol,docs,desc     # my spaces
      python ops/migrate_vectors_to_supabase.py --space extractions --batch 200    # a big corpus space
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys, tempfile
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
PG = ["psql", "-h", "127.0.0.1", "-p", "15432", "-U", "postgres", "-d", "postgres", "-v", "ON_ERROR_STOP=1"]
DIM_COL = {3584: "vec_3584", 2560: "vec_2560", 1024: "vec_1024"}


def psql_file(sql_path):
    return subprocess.run(PG + ["-f", sql_path], capture_output=True, text=True,
                          env={**os.environ, "PGPASSWORD": "postgres"})


def q(sql):
    return subprocess.run(PG + ["-tAc", sql], capture_output=True, text=True,
                          env={**os.environ, "PGPASSWORD": "postgres"}).stdout.strip()


def _lit(s):  # dollar-quote for SQL string literals
    return "$q$" + str(s).replace("$q$", "") + "$q$"


def migrate_space(store, vi, space, emb, batch):
    from store.fs_store import FsStore
    st = getattr(store, "store", store)
    addrs = vi.index_addresses(st, space=space)
    print(f"  space={space} emb={emb}: {len(addrs)} FsStore vectors", flush=True)
    done = skipped = baddim = 0
    buf = []

    def flush():
        nonlocal done
        if not buf:
            return
        with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, dir=os.environ.get("CLAUDE_JOB_DIR", "/tmp")) as f:
            f.write("BEGIN;\n")
            for row in buf:
                f.write(row + "\n")
            f.write("COMMIT;\n")
            p = f.name
        r = psql_file(p)
        os.unlink(p)
        if r.returncode != 0:
            raise RuntimeError(f"batch insert failed (rolled back): {r.stderr.strip()[:400]}")
        done += len(buf)
        buf.clear()

    for a in addrs:
        rec = st.get_vector(a)
        if not rec or not rec.get("vector"):
            skipped += 1
            continue
        dim = rec.get("dim") or len(rec["vector"])
        col = DIM_COL.get(dim)
        if not col:
            baddim += 1  # fail loud: an unmapped dim is recorded, never silently dropped
            print(f"    UNMAPPED DIM {dim} at {rec.get('source')} — needs a vec_{dim} column", flush=True)
            continue
        vec_lit = "[" + ",".join(repr(float(x)) for x in rec["vector"]) + "]"
        src = rec.get("source") or a
        buf.append(
            f"insert into ledger.embedding (source_address,space,emb_layer,model,dim,content_hash,{col}) values "
            f"({_lit(src)},{_lit(space)},{_lit(rec.get('emb') or emb or 'unknown')},{_lit(rec.get('model') or '')},"
            f"{int(dim)},{_lit(rec.get('content_hash') or '')},'{vec_lit}'::halfvec({dim})) "
            f"on conflict (source_address,space,emb_layer) do update set {col}=excluded.{col}, "
            f"content_hash=excluded.content_hash, model=excluded.model, ts=now();")
        if len(buf) >= batch:
            flush()
            if done % (batch * 5) == 0:
                print(f"    ...{done}/{len(addrs)} migrated", flush=True)
    flush()
    n_supabase = q(f"select count(*) from ledger.embedding where space={_lit(space)};")
    print(f"  DONE space={space}: FsStore={len(addrs)} inserted/updated={done} skipped(no-vec)={skipped} "
          f"baddim={baddim} | Supabase rows now={n_supabase}", flush=True)
    return {"space": space, "fsstore": len(addrs), "migrated": done, "skipped": skipped, "baddim": baddim,
            "supabase": int(n_supabase) if n_supabase.isdigit() else n_supabase}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--space", required=True, help="comma-separated space names")
    ap.add_argument("--emb", default="", help="emb-layer hint if a record lacks one")
    ap.add_argument("--batch", type=int, default=200)
    a = ap.parse_args()
    from store.fs_store import FsStore
    from store import vector_index as vi
    store = FsStore(os.path.join(REPO, ".data", "store"))
    results = []
    for space in [s.strip() for s in a.space.split(",") if s.strip()]:
        results.append(migrate_space(store, vi, space, a.emb, a.batch))
    print("\n=== MIGRATION SUMMARY ===")
    for r in results:
        ok = "✓" if r["supabase"] == r["fsstore"] - r["skipped"] - r["baddim"] else "⚠ MISMATCH"
        print(f"  {r['space']}: FsStore {r['fsstore']} → Supabase {r['supabase']}  {ok}")


if __name__ == "__main__":
    raise SystemExit(main())
