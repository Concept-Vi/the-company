#!/usr/bin/env python3
"""ops/build_embeddings.py — build the ledger's MULTI-MODEL, per-content-type embedding spaces.

Design (Tim, 2026-07-01): different content embedded DIFFERENTLY, each in its own SPACE of the existing
space-keyed vector index (store/vector_index.py) — extend, never a parallel system. Each SPACE = one
(content-type -> text-source -> model):

  space=code : raw source of code files      -> nomic-embed-code (ollama :11434, 3584-dim, 32768-tok ctx) [CODE]
  space=docs : content of real markdown docs  -> pplx-embed-context (:8007, 2560-dim, 32768-tok ctx)       [TEXT]

NO ARBITRARY CHARACTER CAPS. The ONLY limit is each model's REAL context window (32768 tokens). For code we
DETECT truncation exactly (ollama reports usage.prompt_tokens): a file whose token count hits the ceiling is
FLAGGED for chunking and NOT stored (never a silent lying vector). Reusable: --root/--project. In-system:
the Company's own FsStore + vector_index. Incremental: an unchanged file (content_hash match) is skipped.

Run:  python ops/build_embeddings.py --space code
      python ops/build_embeddings.py --space docs
      python ops/build_embeddings.py --space code --query "resolve which brain model to use"
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

SPACES = {
    "code": {"exts": (".py", ".ts", ".tsx", ".js", ".jsx"), "kind": "ollama",
             "model": "nomic-embed-code", "base_url": "http://127.0.0.1:11434", "dim": 3584,
             "n_ctx": 32768, "emb": "nomic-code", "desc": "raw code source -> code-specialised embedder"},
    "symbol": {"kind": "ollama",   # the SCALE below file: each function/method/class/component embedded from
               "model": "nomic-embed-code", "base_url": "http://127.0.0.1:11434", "dim": 3584,   # its own source
               "n_ctx": 32768, "emb": "nomic-code", "desc": "per-symbol source slice -> code embedder (finer scale)",
               # semantic code units — skip bare 1-line constants (thin, low search value); classes too big for
               # the window flag for chunking, but their methods (separate symbols) embed fine — symbol-scale is
               # itself the coverage answer for the giant files.
               "symbol_kinds": ("function", "method", "class", "component", "type", "interface", "registry-dict")},
    "docs": {"exts": (".md",), "kind": "fabric",
             "model": "perplexity-ai/pplx-embed-context-v1-4b", "base_url": "http://127.0.0.1:8007/v1", "dim": 2560,
             "n_ctx": 32768, "emb": "pplx", "desc": "markdown content -> text embedder",
             # pplx's custom server can't report token counts, so docs use a GENEROUS char pre-filter at the
             # real 32768-tok window (~3.4 chars/tok prose) as the only safety net; a doc over it (essentially
             # none) is flagged for chunking, not silently truncated.
             "char_ceiling": 110000},
}
PG = ["psql", "-h", "127.0.0.1", "-p", "15432", "-U", "postgres", "-d", "postgres", "-tAc"]


def psql(sql: str) -> str:
    return subprocess.run(PG + [sql], capture_output=True, text=True,
                          env={**os.environ, "PGPASSWORD": "postgres"}).stdout


def corpus_for(space: str, project: str, root: str):
    cfg = SPACES[space]
    ext_in = ",".join(f"$q${e}$q$" for e in cfg["exts"])
    noise = "and e.path not like $q$channel-memory/%$q$ and e.path not like $q$%/discovery/%$q$" if space == "docs" else ""
    rows = psql(f"select e.path from ledger.entry_latest e where e.project=$q${project}$q$ and e.node_type='file' "
                f"and e.ext in ({ext_in}) and coalesce(e.coverage_state,'') <> 'excluded' {noise} order by e.path").splitlines()
    corpus, empty, missing = [], 0, 0
    for p in (r.strip() for r in rows):
        if not p:
            continue
        ap = os.path.join(root, p)
        if not os.path.isfile(ap):
            missing += 1
            continue
        try:
            text = open(ap, errors="replace").read()
        except Exception:
            missing += 1
            continue
        if not text.strip():
            empty += 1                                   # nothing to embed (e.g. empty __init__.py)
            continue
        corpus.append({"address": f"code://{project}/{p}", "text": text})
    return corpus, empty, missing


def corpus_for_symbols(project, root):
    """The symbol-scale corpus: each semantic symbol → its SOURCE SLICE (line_start..line_end) with a small
    locational header (qual + kind + path), addressed by its ledger code_id. The finer scale under file."""
    cfg = SPACES["symbol"]
    kinds = ",".join(f"$q${k}$q$" for k in cfg["symbol_kinds"])
    rows = psql(f"select s.parent_path||chr(9)||s.name||chr(9)||s.symbol_kind||chr(9)||coalesce(s.line_start,0)"
                f"||chr(9)||coalesce(s.line_end,0)||chr(9)||coalesce(s.signature,'')||chr(9)||s.code_id "
                f"from ledger.symbol_latest s join ledger.entry_latest e on e.path=s.parent_path "
                f"and e.project=$q${project}$q$ where s.symbol_kind in ({kinds}) and s.line_start is not null "
                f"and coalesce(e.coverage_state,'')<>'excluded' order by s.parent_path, s.line_start").splitlines()
    # cache file lines so we read each file once
    filecache, corpus, missing = {}, [], 0
    for r in rows:
        f = r.split("\t")
        if len(f) < 7:
            continue
        path, name, kind, ls, le, sig, code_id = f[0], f[1], f[2], int(f[3]), int(f[4]), f[5], f[6]
        if path not in filecache:
            ap = os.path.join(root, path)
            filecache[path] = open(ap, errors="replace").read().splitlines() if os.path.isfile(ap) else None
        lines = filecache[path]
        if lines is None:
            missing += 1
            continue
        slice_src = "\n".join(lines[max(0, ls - 1):le if le >= ls else ls])
        text = f"{kind} {name}  [{path}]\n{sig}\n{slice_src}".strip()
        if text:
            corpus.append({"address": code_id, "text": text})
    return corpus, 0, missing


def ollama_embed(base_url, model, text, num_ctx):
    """One embedding via ollama /api/embed → (vector, prompt_tokens). CRITICAL: ollama's DEFAULT embedding
    context is ~4096 — it silently truncates to that and IGNORES the model's real window unless num_ctx is
    passed explicitly. So we ALWAYS pass num_ctx (the model's real limit); prompt_tokens then lets us DETECT
    the genuine over-limit files (they report ~num_ctx) vs the rest (their true count)."""
    body = json.dumps({"model": model, "input": text, "options": {"num_ctx": num_ctx}}).encode()
    req = urllib.request.Request(base_url + "/api/embed", data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        d = json.loads(r.read())
    embs = d.get("embeddings") or []
    return (embs[0] if embs else None), d.get("prompt_eval_count", 0)


def build_code_space(store, corpus, cfg, vi, space, force=False):
    """Per-file embed with EXACT truncation detection (no char cap): store only honest vectors; a file whose
    token count hits n_ctx is flagged for chunking. Incremental (skip unchanged content_hash unless force).
    Concurrent. `space` = the vector space to write ('code' file-level or 'symbol')."""
    embedded = skipped = 0
    truncated = []
    n_ctx = cfg["n_ctx"]
    trunc_at = n_ctx - 32                                 # ollama truncates to num_ctx; a file reporting >= this hit it

    def one(item):
        nonlocal embedded, skipped
        src, text = item["address"], item["text"]
        key = store.space_address(src, space, cfg["emb"])
        h = vi.content_hash(text)
        if not force:
            prior = store.get_vector(key)
            if prior is not None and prior.get("content_hash") == h:
                skipped += 1
                return None
        vec, ntok = ollama_embed(cfg["base_url"], cfg["model"], text, n_ctx)
        if vec is None:
            return ("error", src, ntok)
        if ntok >= trunc_at:                             # hit the real ceiling -> the model TRUNCATED this input
            return ("truncated", src, ntok)              # flag for chunking; DO NOT store a lying vector
        store.put_vector(key, vec, h, dim=cfg["dim"], model=cfg["model"], space=space, source=src, emb=cfg["emb"])
        embedded += 1
        return None

    with ThreadPoolExecutor(max_workers=6) as ex:
        for i, res in enumerate(ex.map(one, corpus)):
            if res and res[0] in ("truncated", "error"):
                truncated.append((res[1], res[2]))
            if i % 100 == 0:
                print(f"  ...{embedded} embedded, {skipped} skipped ({i}/{len(corpus)})", flush=True)
    return {"embedded": embedded, "skipped": skipped, "flagged_for_chunking": truncated}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--space", choices=list(SPACES), required=True)
    ap.add_argument("--project", default="company")
    ap.add_argument("--root", default=REPO)
    ap.add_argument("--query", default="")
    ap.add_argument("--force", action="store_true", help="re-embed even if content_hash unchanged (use after a model/ctx fix invalidated stored vectors)")
    a = ap.parse_args()
    from store.fs_store import FsStore
    from store import vector_index as vi
    cfg = SPACES[a.space]
    store = FsStore(os.path.join(REPO, ".data", "store"))
    root = os.path.abspath(a.root)
    if a.space == "symbol":
        corpus, empty, missing = corpus_for_symbols(a.project, root)
    else:
        corpus, empty, missing = corpus_for(a.space, a.project, root)
    print(f"space={a.space} ({cfg['desc']}) | model={cfg['model']} dim={cfg['dim']} n_ctx={cfg['n_ctx']}", flush=True)
    print(f"corpus: {len(corpus)} items | empty-skipped: {empty} | missing-on-disk: {missing}", flush=True)

    if cfg["kind"] == "ollama":
        res = build_code_space(store, corpus, cfg, vi, a.space, force=a.force)
        flagged = res.pop("flagged_for_chunking", [])
        print(f"BUILD: {res}", flush=True)
        if flagged:
            print(f"  flagged for CHUNKING (exceed the model's real {cfg['n_ctx']}-tok window — NOT truncated-and-stored): {len(flagged)}")
            for src, ntok in sorted(flagged, key=lambda x: -x[1])[:10]:
                print(f"    {ntok} tok  {src}")
    else:  # docs via the fabric path (pplx), generous char pre-filter, batched
        ceil = cfg["char_ceiling"]
        over = [c for c in corpus if len(c["text"]) > ceil]
        fit = [c for c in corpus if len(c["text"]) <= ceil]
        tot = {"embedded": 0, "skipped": 0, "degraded": False}
        for i in range(0, len(fit), 16):
            r = vi.build_index(store, fit[i:i + 16], model=cfg["model"], base_url=cfg["base_url"],
                               dim=cfg["dim"], space="docs", emb=cfg["emb"])
            tot["embedded"] += r.get("embedded", 0); tot["skipped"] += r.get("skipped", 0)
            tot["degraded"] = tot["degraded"] or r.get("degraded", False)
            if r.get("degraded"):
                print(f"  DEGRADED at batch {i//16}; stopping", flush=True); break
        print(f"BUILD: {tot} | flagged for chunking (>{ceil} chars): {len(over)}", flush=True)
        for c in sorted(over, key=lambda x: -len(x["text"]))[:8]:
            print(f"    {len(c['text'])} chars  {c['address']}")

    if a.query:
        from fabric import transport, client
        if cfg["kind"] == "ollama":
            qv, _ = ollama_embed(cfg["base_url"], cfg["model"], a.query, cfg["n_ctx"])
        else:
            t = transport.openai_embeddings_transport(base_url=cfg["base_url"])
            qv = client.complete_embeddings(t, [a.query], model=cfg["model"], dim=cfg["dim"])[0]
        hits = vi.query_index(store, qv, k=8, space=a.space, emb=cfg["emb"])
        print(f"\nQUERY '{a.query}' — top matches:")
        for h in hits:
            print(f"  {h.get('score', 0):.3f}  {h.get('id', h)}")


if __name__ == "__main__":
    raise SystemExit(main())
