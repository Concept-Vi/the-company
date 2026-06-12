#!/usr/bin/env python3
"""wire_substrate_claude_sessions.py — wire the obsidian-overlord SUBSTRATE to the
local pplx-embed-context-v1-4b service and index the Claude-session transcript
corpus as a substrate vault named `claude-sessions`.

THROWAWAY INTERIM (Tim is building a real memory system elsewhere). This is the
substrate-backed path (distinct from the standalone ops/transcript_search.py
numpy fallback): it gives the transcripts the full substrate query surface —
search_semantic, traverse_links, get_neighborhood, addresses, type-graph — via
the same MCP the rest of the Company uses.

WHY A SEPARATE STATE DIR (isolation, non-destructive):
  The overlord substrate's default .state is configured for ollama/bge (a
  DIFFERENT embedding space). The pplx embedder is its OWN search space
  (2560-d int8, not bge-m3's unified space — expected for a throwaway). Mixing
  two embedders in one Chroma store would corrupt similarity. So this throwaway
  lives in an ISOLATED state dir:
      $SUBSTRATE_MCP_STATE_DIR (default ~/.cache/company/substrate-claude-sessions)
  Nothing in the existing substrate is touched.

WIRING (registry-is-truth):
  provider   = "openai"  (OpenAIEmbedder added 2026-06-10)
  model      = "perplexity-ai/pplx-embed-context-v1-4b"
  base_url   = http://127.0.0.1:8007/v1  (the `embed-pplx` service, ops/services.json)
  The substrate's `ollama_base_url` config field doubles as the generic base_url
  passed to make_embedder() (same convention ServerState/set_embedding_model use),
  so an openai-provider config routes through the OpenAIEmbedder at the pplx port.

COSINE INTEGRITY (the int8/unnormalized detail, grounded):
  The model card REQUIRES cosine comparison; vectors are int8 + UNNORMALIZED.
  SubstrateChroma creates its collection with metadata={"hnsw:space":"cosine"}.
  Cosine is scale-invariant, so int8 magnitude is irrelevant and the substrate
  does NOT need to pre-normalize — Chroma's cosine distance compares directions
  correctly. Query and corpus go through the SAME pplx endpoint → same space.
  (Verified against modeling.py encode() + embeddings.py SubstrateChroma.)

USAGE:
  # 1) the embedder must be up first:  company up embed-pplx   (and healthy)
  python ops/wire_substrate_claude_sessions.py setup   # config + register vault (no embed)
  python ops/wire_substrate_claude_sessions.py index   # scan + embed the corpus
  python ops/wire_substrate_claude_sessions.py status  # counts
  python ops/wire_substrate_claude_sessions.py search "your query" [-k 8]
  python ops/wire_substrate_claude_sessions.py all "probe query"  # setup+index+search

FAIL LOUD (repo law): every step raises / exits non-zero on the first real
error. No silent fallback, no fake results.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

# --- locate the substrate package (obsidian-overlord) ---
OVERLORD = Path(os.environ.get(
    "OVERLORD_REPO", "/home/tim/repos/obsidian-overlord")).resolve()
SRC = OVERLORD / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Isolated, non-destructive state dir for this throwaway search space.
STATE_DIR = Path(os.environ.get(
    "SUBSTRATE_MCP_STATE_DIR",
    Path.home() / ".cache" / "company" / "substrate-claude-sessions",
)).resolve()
os.environ["SUBSTRATE_MCP_STATE_DIR"] = str(STATE_DIR)  # so config_mod.load() honors it

CORPUS = Path(os.environ.get(
    "CLAUDE_SESSIONS_CORPUS", str(Path.home() / "corpora" / "claude-sessions"))).resolve()
VAULT = "claude-sessions"
PROVIDER = "openai"
MODEL = "perplexity-ai/pplx-embed-context-v1-4b"
BASE_URL = os.environ.get("PPLX_EMBED_URL_BASE", "http://127.0.0.1:8007/v1")
HEALTH = BASE_URL.rstrip("/").replace("/v1", "") + "/health"
EXPECT_DIM = 2560

from substrate_mcp import config as config_mod  # noqa: E402
from substrate_mcp import db as db_mod  # noqa: E402
from substrate_mcp import scanner as scanner_mod  # noqa: E402
from substrate_mcp.embeddings import make_embedder, SubstrateChroma  # noqa: E402


# ---------- embedder health (fail loud) ----------

def _require_embedder_up() -> dict:
    try:
        with urllib.request.urlopen(HEALTH, timeout=5) as r:
            h = json.loads(r.read())
    except Exception as e:
        sys.exit(
            f"FAIL: pplx embedder not reachable at {HEALTH} ({type(e).__name__}: {e}).\n"
            f"      Start it:  company up embed-pplx   (and wait for /health status=ok)"
        )
    if h.get("status") != "ok":
        sys.exit(f"FAIL: embedder at {HEALTH} not ready: {h}")
    return h


def _load_cfg() -> config_mod.Config:
    return config_mod.load(STATE_DIR)


# ---------- steps ----------

def cmd_setup(_args) -> int:
    """Configure the isolated substrate for the pplx embedder and register the vault.
    Idempotent: re-running updates the config and (re-)registers the vault if absent."""
    if not CORPUS.is_dir():
        sys.exit(f"FAIL: corpus dir does not exist: {CORPUS}\n"
                 f"      Run the exporter first: python ops/agent_sessions_exporter.py")
    md = list(CORPUS.rglob("*.md"))
    if not md:
        sys.exit(f"FAIL: corpus {CORPUS} has no .md files.\n"
                 f"      Run the exporter first: python ops/agent_sessions_exporter.py")

    cfg = _load_cfg()
    # Point the substrate at the pplx OpenAI-compatible endpoint.
    cfg.embedding_provider = PROVIDER
    cfg.embedding_model = MODEL
    cfg.ollama_base_url = BASE_URL  # doubles as the generic base_url (see module docstring)
    config_mod.save(cfg)

    # Register the vault (skip if already registered).
    if not any(v.name == VAULT for v in cfg.vaults):
        cfg = config_mod.add_vault(cfg, name=VAULT, path=str(CORPUS), ignore=[], extensions=[".md"])
    print(json.dumps({
        "ok": True, "state_dir": str(STATE_DIR),
        "embedding_provider": cfg.embedding_provider,
        "embedding_model": cfg.embedding_model,
        "base_url": cfg.ollama_base_url,
        "vault": VAULT, "corpus": str(CORPUS),
        "corpus_md_files": len(md),
    }, indent=2))
    return 0


def cmd_index(args) -> int:
    """Scan + embed the corpus into the substrate (Chroma cosine space)."""
    _require_embedder_up()
    cfg = _load_cfg()
    if not any(v.name == VAULT for v in cfg.vaults):
        sys.exit("FAIL: vault not registered. Run `setup` first.")
    if cfg.embedding_provider != PROVIDER or cfg.embedding_model != MODEL:
        sys.exit(f"FAIL: config not wired to pplx (provider={cfg.embedding_provider}, "
                 f"model={cfg.embedding_model}). Run `setup` first.")
    conn = db_mod.connect(cfg.db_path)
    embedder = make_embedder(cfg.embedding_provider, cfg.embedding_model,
                             base_url=cfg.ollama_base_url, api_key=cfg.ollama_api_key)
    chroma = SubstrateChroma(cfg.chroma_path, embedder)
    v = next(v for v in cfg.vaults if v.name == VAULT)

    if args.full:
        try:
            chroma._client.delete_collection(name=f"vault_{v.name}")
        except Exception:
            pass
        conn.execute(
            "DELETE FROM chunks WHERE address_id IN "
            "(SELECT id FROM addresses WHERE vault = ?);", (v.name,))
        conn.execute("UPDATE addresses SET sha256 = NULL WHERE vault = ?;", (v.name,))

    t0 = time.time()
    report = scanner_mod.scan_vault(
        cfg, conn, v, embed_now=True, chroma=chroma,
        progress=lambda msg: print(msg, flush=True),
    )
    elapsed = time.time() - t0
    n_files = conn.execute(
        "SELECT COUNT(*) c FROM addresses WHERE vault=? AND kind='file';", (v.name,)
    ).fetchone()["c"]
    n_chunks = conn.execute(
        "SELECT COUNT(*) c FROM chunks ch JOIN addresses a ON a.id=ch.address_id "
        "WHERE a.vault=?;", (v.name,)
    ).fetchone()["c"]
    n_embedded = conn.execute(
        "SELECT COUNT(*) c FROM chunks ch JOIN addresses a ON a.id=ch.address_id "
        "WHERE a.vault=? AND ch.embedded_at IS NOT NULL;", (v.name,)
    ).fetchone()["c"]
    n_vec = chroma.count(v.name)
    print(json.dumps({
        "ok": True, "vault": v.name, "elapsed_s": round(elapsed, 1),
        "files_indexed": n_files, "chunks_total": n_chunks,
        "chunks_embedded": n_embedded, "chroma_vectors": n_vec,
        "scan_report": report.__dict__,
    }, indent=2, ensure_ascii=False))
    if n_embedded == 0 or n_vec == 0:
        sys.exit("FAIL: nothing embedded — index did not work.")
    return 0


def cmd_status(_args) -> int:
    cfg = _load_cfg()
    conn = db_mod.connect(cfg.db_path)
    out = {
        "state_dir": str(STATE_DIR),
        "embedding_provider": cfg.embedding_provider,
        "embedding_model": cfg.embedding_model,
        "base_url": cfg.ollama_base_url,
        "vaults": [v.name for v in cfg.vaults],
    }
    if any(v.name == VAULT for v in cfg.vaults):
        out["files_indexed"] = conn.execute(
            "SELECT COUNT(*) c FROM addresses WHERE vault=? AND kind='file';", (VAULT,)
        ).fetchone()["c"]
        out["chunks_total"] = conn.execute(
            "SELECT COUNT(*) c FROM chunks ch JOIN addresses a ON a.id=ch.address_id "
            "WHERE a.vault=?;", (VAULT,)
        ).fetchone()["c"]
        out["chunks_embedded"] = conn.execute(
            "SELECT COUNT(*) c FROM chunks ch JOIN addresses a ON a.id=ch.address_id "
            "WHERE a.vault=? AND ch.embedded_at IS NOT NULL;", (VAULT,)
        ).fetchone()["c"]
        try:
            embedder = make_embedder(cfg.embedding_provider, cfg.embedding_model,
                                     base_url=cfg.ollama_base_url, api_key=cfg.ollama_api_key)
            out["chroma_vectors"] = SubstrateChroma(cfg.chroma_path, embedder).count(VAULT)
        except Exception as e:
            out["chroma_vectors"] = f"(unavailable: {e})"
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


def cmd_search(args) -> int:
    """Semantic search through the substrate's Chroma cosine face."""
    _require_embedder_up()
    cfg = _load_cfg()
    if not any(v.name == VAULT for v in cfg.vaults):
        sys.exit("FAIL: vault not registered. Run `setup`+`index` first.")
    embedder = make_embedder(cfg.embedding_provider, cfg.embedding_model,
                             base_url=cfg.ollama_base_url, api_key=cfg.ollama_api_key)
    chroma = SubstrateChroma(cfg.chroma_path, embedder)
    results = chroma.query(VAULT, args.query, n_results=args.k)
    if not results:
        sys.exit("FAIL: query returned 0 results (empty index?).")
    print(f"\nTop {args.k} for: {args.query!r}\n" + "=" * 72)
    for rank, r in enumerate(results, 1):
        m = r.get("metadata") or {}
        dist = r.get("distance")
        cos = (1.0 - dist) if isinstance(dist, (int, float)) else None
        text = (r.get("text") or "").strip().replace("\n", " ")
        print(f"\n#{rank}  cos~{cos:.3f}  dist={dist:.4f}" if cos is not None
              else f"\n#{rank}  dist={dist}")
        print(f"    addr: {m.get('address')}")
        print(f"    {text[:280]}{'...' if len(text) > 280 else ''}")
    print()
    return 0


def cmd_all(args) -> int:
    cmd_setup(args)
    cmd_index(args)
    return cmd_search(args)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("setup").set_defaults(func=cmd_setup)
    pi = sub.add_parser("index"); pi.add_argument("--full", action="store_true", default=True)
    pi.set_defaults(func=cmd_index)
    sub.add_parser("status").set_defaults(func=cmd_status)
    ps = sub.add_parser("search"); ps.add_argument("query"); ps.add_argument("-k", type=int, default=5)
    ps.set_defaults(func=cmd_search)
    pa = sub.add_parser("all"); pa.add_argument("query"); pa.add_argument("-k", type=int, default=5)
    pa.add_argument("--full", action="store_true", default=True); pa.set_defaults(func=cmd_all)
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
