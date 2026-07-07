"""store/pg_vectors.py — the vector namespace on SUPABASE (① of NORTH-STAR: the read-path cutover).

The ONE seam all ~7 semantic-search readers funnel through (query_index / space_matrix / index_addresses /
get/put/remove_vector) — reimplemented on `ledger.embedding` (pgvector 0.8.2, halfvec multi-dim, HNSW).
FsStore's vector methods DELEGATE here; the old file-per-vector IO (.data/store/vectors/*.json) is
COMMENTED OUT at those sites per Tim's no-fallback rule (inert, legible, recoverable — zero influence).

BEST-KNOWN-WAY notes (north-star: proactively bring the standard approach, Tim can't request what he
can't see):
  · SEARCH runs IN Postgres (`vec <=> query` under the per-dim HNSW indexes) — the whole point of pgvector.
    We never ship 76k vectors to Python to do cosine in numpy (the old file-store necessity, now inverted).
  · ENUMERATION ships addresses only. FULL matrices are pulled ONLY for offline clustering (scale.py) —
    a batch consumer, explicitly not the hot path.
  · One table, per-dim halfvec columns (vec_3584 nomic / vec_2560 pplx / vec_1024 bge), space+emb_layer
    keyed, content_hash for incrementality — see build-prep/the-one-system/SUPABASE-VECTOR-SCHEMA.md.

FAIL-LOUD BREADCRUMBS (no humans in the loop — a resolving agent needs the trail): every miss/failure
names the table+host, the RETIRED old path, and the fix command.
"""
from __future__ import annotations
import json
import os
import subprocess

PG = {
    "host": os.environ.get("COMPANY_LEDGER_PGHOST", "127.0.0.1"),
    "port": os.environ.get("COMPANY_LEDGER_PGPORT", "15432"),
    "user": os.environ.get("COMPANY_LEDGER_PGUSER", "postgres"),
    "db":   os.environ.get("COMPANY_LEDGER_PGDB", "postgres"),
    "pw":   os.environ.get("COMPANY_LEDGER_PGPASSWORD", "postgres"),
}
DIM_COL = {3584: "vec_3584", 2560: "vec_2560", 1024: "vec_1024"}
BREADCRUMB = (f"source = ledger.embedding (Supabase {PG['host']}:{PG['port']}; halfvec, HNSW). The retired "
              f"pre-cutover source was .data/store/vectors/*.json (FsStore). To (re)populate a space: "
              f"ops/build_embeddings.py --space <s> then ops/migrate_vectors_to_supabase.py --space <s> — "
              f"or re-run the producer that owns it.")


class PgVectorError(RuntimeError):
    """Loud, breadcrumbed vector-store failure (never a silent empty ranking)."""


def _psql(sql: str, timeout: int = 60) -> str:
    r = subprocess.run(["psql", "-h", PG["host"], "-p", PG["port"], "-U", PG["user"], "-d", PG["db"],
                        "-v", "ON_ERROR_STOP=1", "-tAc", sql], capture_output=True, text=True,
                       timeout=timeout, env={**os.environ, "PGPASSWORD": PG["pw"]})
    if r.returncode != 0:
        raise PgVectorError(f"ledger.embedding query failed: {(r.stderr or '').strip()[:300]} — {BREADCRUMB}")
    return r.stdout


def _lit(s) -> str:
    return "$pgv$" + str(s).replace("$pgv$", "") + "$pgv$"


def _veclit(vector) -> str:
    return "[" + ",".join(repr(float(x)) for x in vector) + "]"


# ── the namespace primitives (FsStore delegates) ────────────────────────────────────────────────

def put_vector(address: str, vector: list, content_hash: str, *, dim: int, model: str,
               space=None, source=None, emb=None) -> dict:
    # A known dim → its typed halfvec column (HNSW-indexed, the hot path). ANY OTHER dim → the
    # unconstrained `vec_any vector` overflow column (exact-scan) — so a NEW embedder (or a test fixture)
    # lands with NO schema change ("add a row, not a branch"; the growing-model-layer principle). Promote
    # a hot new dim later: add vec_<dim> halfvec + HNSW, re-put, done.
    dim = len(vector)                                        # the vector IS its dim (a fixture may declare
    col = DIM_COL.get(int(dim))                              # another; storing the declared lie was the old
    cast = f"halfvec({int(dim)})" if col else "vector"       # store's silent behaviour — truth wins here)
    col = col or "vec_any"
    sp = space if isinstance(space, str) and space else "__default__"
    _psql(f"insert into ledger.embedding (source_address,space,emb_layer,model,dim,content_hash,{col}) values "
          f"({_lit(source or address)},{_lit(sp)},{_lit(emb or 'unknown')},{_lit(model or '')},{int(dim)},"
          f"{_lit(content_hash)},'{_veclit(vector)}'::{cast}) "
          f"on conflict (source_address,space,emb_layer) do update set {col}=excluded.{col}, "
          f"content_hash=excluded.content_hash, model=excluded.model, dim=excluded.dim, ts=now()")
    return {"address": address, "space": space, "emb": emb, "dim": dim, "model": model,
            "content_hash": content_hash, "source": source or address}


def get_vector(address: str, *, space=None, emb=None) -> dict | None:
    """Entry by SOURCE address (+ optional space/emb narrowing). Honest None when never built."""
    cond = f"source_address={_lit(address)}"
    if isinstance(space, str) and space:
        cond += f" and space={_lit(space)}"
    if isinstance(emb, str) and emb:
        cond += f" and emb_layer={_lit(emb)}"
    out = _psql("select space, emb_layer, model, dim, content_hash, "
                "coalesce(vec_3584::text, vec_2560::text, vec_1024::text, vec_any::text) "
                f"from ledger.embedding where {cond} limit 1")
    line = out.strip().splitlines()
    if not line:
        return None
    sp, el, model, dim, ch, vec = line[0].split("|", 5)
    return {"address": address, "source": address, "space": None if sp == "__default__" else sp,
            "emb": el, "model": model, "dim": int(dim), "content_hash": ch,
            "vector": json.loads(vec) if vec else None}


def remove_vector(address: str, *, space=None, emb=None) -> bool:
    cond = f"source_address={_lit(address)}"
    if isinstance(space, str) and space:
        cond += f" and space={_lit(space)}"
    if isinstance(emb, str) and emb:
        cond += f" and emb_layer={_lit(emb)}"
    out = _psql(f"with d as (delete from ledger.embedding where {cond} returning 1) select count(*) from d")
    return out.strip() not in ("", "0")


def _ns_cond(ns: str) -> str:
    """The namespace guard: a namespaced (test/tmp-root) store sees ONLY its rows; the canonical store
    sees everything EXCEPT test namespaces (per-root isolation, the old file-store contract)."""
    return f"space like {_lit(ns + '%')}" if ns else "space not like '__root_%'"


def index_addresses(space=None, ns: str = "") -> list:
    """(source, space, emb_layer) rows in scope — the caller composes the verbatim storage keys.
    Addresses ONLY (never the vectors; enumeration is not search)."""
    if space is None:
        cond = f"space={_lit(ns + '__default__')}"
    elif isinstance(space, str):
        cond = f"space={_lit(ns + space)}"
    else:                                                        # ALL_SPACES sentinel
        cond = _ns_cond(ns)
    out = _psql(f"select distinct source_address, space, emb_layer from ledger.embedding where {cond}")
    rows = []
    for l in out.splitlines():
        if l.count("|") >= 2:
            s, sp, el = l.split("|", 2)
            rows.append((s, sp, el))
    return rows


def search(query_vector: list, *, space, emb, k: int = 8, kw_ns: str = "") -> list:
    """Top-k cosine IN Postgres → [{id, score}] (score = cosine similarity, query_index's contract).
    A known dim ranks on its typed halfvec column (HNSW, the hot path); any other dim ranks on the
    vec_any overflow column (exact scan, dim-scoped — fixtures + not-yet-promoted new embedders).
    space=None → all spaces; the DIM scopes the layer either way (never a cross-dim cosine)."""
    dim = len(query_vector)
    col = DIM_COL.get(dim)
    if col:
        expr = f"1 - ({col} <=> '{_veclit(query_vector)}'::halfvec({dim}))"
        notnull = f"{col} is not null"
    else:
        expr = f"1 - (vec_any <=> '{_veclit(query_vector)}'::vector)"
        notnull = f"vec_any is not null and dim = {dim}"
    ns = kw_ns
    cond = f"{_ns_cond(ns)} and {notnull}" if space is None else f"space={_lit(ns + space)} and {notnull}"
    if isinstance(emb, str) and emb:
        cond += f" and emb_layer={_lit(emb)}"
    out = _psql(f"select source_address, {expr} "
                f"from ledger.embedding where {cond} order by 2 desc limit {int(k)}", timeout=90)
    hits = []
    for l in out.splitlines():
        if "|" in l:
            a, s = l.rsplit("|", 1)
            hits.append({"id": a, "score": float(s)})
    if not hits:
        # FAIL-LOUD dim guard (the retired retrieve._cosine contract): if the target space HAS vectors but
        # none at THIS query's dim, that's a wrong-dim query — raise, never a silent wrong/empty ranking.
        spc = _ns_cond(ns) if space is None else f"space={_lit(ns + space)}"
        if isinstance(emb, str) and emb:
            spc += f" and emb_layer={_lit(emb)}"
        other = _psql(f"select count(*) from ledger.embedding where {spc} and dim <> {dim}").strip()
        if other and other != "0":
            raise ValueError(f"search: query dim {dim} does not match the space's stored dim(s) "
                             f"({other} vectors at other dims in scope) — a wrong-dim query must fail "
                             f"loud, never rank against the wrong layer (the retrieve._cosine contract). "
                             f"{BREADCRUMB}")
    return hits


def space_vectors(space, emb):
    """(ids, [vector lists]) for a whole space — OFFLINE full-space consumers only (scale.py clustering,
    index_corpus). Plain lists, no numpy dependency. Empty space → ([], []). Ragged dims fail loud."""
    cond = f"space={_lit(space)}"
    if isinstance(emb, str) and emb:
        cond += f" and emb_layer={_lit(emb)}"
    out = _psql("select source_address, coalesce(vec_3584::text, vec_2560::text, vec_1024::text, vec_any::text) "
                f"from ledger.embedding where {cond}", timeout=300)
    ids, rows = [], []
    for l in out.splitlines():
        if "|" not in l:
            continue
        a, vec = l.split("|", 1)
        if vec:
            ids.append(a)
            rows.append(json.loads(vec))
    if ids and len({len(r) for r in rows}) != 1:                 # ragged dims must fail loud, never a silent matrix
        raise PgVectorError(f"space_vectors({space!r},{emb!r}): mixed dims in one space — split by emb_layer. {BREADCRUMB}")
    return ids, rows


def space_matrix(space, emb):
    """(ids, numpy unit-row matrix) — the numpy face of space_vectors, for consumers doing matmul.
    Returns ([], None) for an empty space (honest); raises if numpy is unavailable (offline consumers
    run where numpy exists; the QUERY path never comes here — search() runs in Postgres)."""
    import numpy as np
    ids, rows = space_vectors(space, emb)
    if not ids:
        return [], None
    M = np.asarray(rows, dtype=np.float32)
    M /= (np.linalg.norm(M, axis=1, keepdims=True) + 1e-9)
    return ids, M


def content_hashes(space, emb) -> dict:
    """{source_address: content_hash} for a whole (space, emb) in ONE query — the pyramid builder's
    incrementality prefetch (replaces a per-member get_vector round-trip; at symbol scale that was 6,201
    psql calls per build, and against the WRONG key — the default space — so hashes read '∅' and
    incrementality silently keyed on membership only)."""
    cond = f"space={_lit(space)}"
    if isinstance(emb, str) and emb:
        cond += f" and emb_layer={_lit(emb)}"
    out = _psql(f"select source_address, content_hash from ledger.embedding where {cond}", timeout=120)
    d = {}
    for l in out.splitlines():
        if "|" in l:
            a, h = l.rsplit("|", 1)
            d[a] = h
    return d
