#!/usr/bin/env python3
"""claude_sessions_reindex.py — the REINDEX BEAT for the interim transcript-search.

After the agent-sessions exporter writes/refreshes session markdown under
``~/corpora/claude-sessions/**/*.md`` (every 20 min via
company-agent-sessions-exporter.timer), this beat keeps the searchable index
current by triggering a substrate DELTA reindex of the ``claude-sessions`` vault.

THROWAWAY INTERIM (Tim is building a real memory system elsewhere). Kept lean:
one stdlib script, no framework. But it WORKS and fails loud.

WHY A SEPARATE BEAT (Tim's explicit requirement): the export and the index are
two stages of one circuit —

    Claude jsonl → [exporter] → corpus markdown → [reindex beat] → searchable index

The exporter alone leaves the search index stale; this beat closes the loop so
``company up embed-pplx`` + a search always reflects the latest exported sessions.

CHEAP-BY-DESIGN (the "only reindex if the export changed files" law):
  1. We keep a marker (``.reindex_marker.json`` in the corpus dir) recording the
     newest .md mtime + file count we last indexed.
  2. On each fire we re-scan ONLY the corpus dir tree's mtimes (no model load, no
     DB read) and compare. If nothing changed since the marker → EXIT 0 immediately,
     having touched nothing (no embedder spin-up, no GPU, no work). This is the
     common case: most 20-min windows export 0–few files.
  3. Only when files changed do we proceed to the actual reindex.

WHAT THE ACTUAL REINDEX DOES (delta, not full):
  Delegates to ops/wire_substrate_claude_sessions.py's substrate index path in
  DELTA mode (scanner.scan_vault with the collection INTACT — sha256 skips
  unchanged files, so only the changed/new transcripts get re-parsed +
  re-embedded). The first-ever run (no marker, empty index) does the initial
  full build. The reindex requires the ``embed-pplx`` service to be up; if it is
  NOT up and there is work to do, this is reported and the beat exits NON-ZERO
  (fail loud) — it does NOT silently skip real work, and it does NOT itself
  spin the GPU embedder (the embedder lifecycle is the resource-manager's job;
  the beat would set the marker only on a SUCCESSFUL index, so a failed/absent
  embedder leaves the marker stale and the next fire retries).

  Operator note: to make this beat fully autonomous it can OPTIONALLY bring the
  embedder up itself via ``company ensure embed-pplx`` (the gated resource
  manager) when --ensure-embedder is passed; default OFF so the cheap path never
  touches the GPU on Tim's behalf without intent.

WIRING (Company lifecycle — the binding Tim required):
  Registered in ops/services.json (group ``jobs``) and run by
  company-claude-sessions-reindex.timer (ops/systemd/), which is
  WantedBy=company.target. So `company up/down`/`company status` see + control
  it, AND it rises/falls with the Company systemd target. The timer fires a few
  minutes AFTER the exporter's cadence so it picks up that window's exports.

Run:  python3 ops/claude_sessions_reindex.py [--check] [--force] [--ensure-embedder]
        --check            report whether a reindex is needed; do NOT index (exit 0)
        --force            reindex even if the marker says nothing changed
        --ensure-embedder  bring embed-pplx up via the resource manager if needed
Timer: company-claude-sessions-reindex.timer (ops/systemd/), in ops/services.json.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

# --- locations (registry-is-truth: these match wire_substrate_claude_sessions.py) ---
REPO = Path(__file__).resolve().parent.parent          # ~/company
OPS = REPO / "ops"
CORPUS = Path(os.environ.get(
    "CLAUDE_SESSIONS_CORPUS", str(Path.home() / "corpora" / "claude-sessions"))).resolve()
MARKER = CORPUS / ".reindex_marker.json"
PPLX_HEALTH = os.environ.get(
    "PPLX_EMBED_HEALTH", "http://127.0.0.1:8007/health")
COMPANY = OPS / "company"                               # the CLI (for `company ensure`)

# The substrate-backed index path lives next to this file; import its building
# blocks rather than shelling, so a delta (non-full) scan is possible.
sys.path.insert(0, str(OPS))


# ---------------------------------------------------------------- change detection (cheap)

def corpus_signature() -> dict:
    """The cheap signal: newest .md mtime + file count across the corpus tree.
    No DB, no model — just stat() walks. Returns {newest_mtime, n_files}."""
    newest = 0.0
    n = 0
    if CORPUS.is_dir():
        for p in CORPUS.rglob("*.md"):
            try:
                m = p.stat().st_mtime
            except OSError:
                continue
            n += 1
            if m > newest:
                newest = m
    return {"newest_mtime": newest, "n_files": n}


def load_marker() -> dict:
    if MARKER.exists():
        try:
            return json.loads(MARKER.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
    return {}


def save_marker(sig: dict, extra: dict | None = None) -> None:
    data = dict(sig)
    data["indexed_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    if extra:
        data.update(extra)
    tmp = MARKER.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=1), encoding="utf-8")
    os.replace(tmp, MARKER)


def needs_reindex(sig: dict, marker: dict) -> tuple[bool, str]:
    """True iff the export changed files since we last indexed."""
    if not marker:
        return True, "first run — no marker yet"
    if sig["n_files"] != marker.get("n_files"):
        return True, (f"file count changed ({marker.get('n_files')} → {sig['n_files']})")
    # mtime strictly newer than what we indexed (small epsilon for fs granularity)
    if sig["newest_mtime"] > marker.get("newest_mtime", 0.0) + 0.001:
        return True, "a transcript was rewritten since last index"
    return False, "nothing changed since last index"


# ---------------------------------------------------------------- embedder gate

def embedder_up() -> bool:
    try:
        with urllib.request.urlopen(PPLX_HEALTH, timeout=5) as r:
            return json.loads(r.read()).get("status") == "ok"
    except Exception:
        return False


def ensure_embedder() -> bool:
    """OPTIONAL: bring embed-pplx up through the resource manager (gated). Returns
    True iff it ends up healthy. Used only with --ensure-embedder."""
    print("  --ensure-embedder: asking the resource manager for embed-pplx "
          "(`company ensure embed-pplx`)…", flush=True)
    r = subprocess.run([sys.executable, str(COMPANY), "ensure", "embed-pplx"],
                       capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    if r.stderr:
        sys.stderr.write(r.stderr)
    # `company ensure` waits for the port; re-check health to be sure it serves.
    for _ in range(40):
        if embedder_up():
            return True
        time.sleep(3)
    return embedder_up()


# ---------------------------------------------------------------- the reindex (delta)

def run_delta_reindex() -> dict:
    """Substrate DELTA reindex of the claude-sessions vault. Uses the wire module's
    config/embedder wiring but scans WITHOUT --full so sha256 skips unchanged files.
    Returns the index report dict. Raises on hard failure (fail loud)."""
    import wire_substrate_claude_sessions as wire  # adopted scaffolding

    # Ensure the substrate is wired (config + vault registered). setup is idempotent.
    wire.cmd_setup(argparse.Namespace())

    cfg = wire._load_cfg()
    if not any(v.name == wire.VAULT for v in cfg.vaults):
        raise RuntimeError("vault not registered after setup — wiring failed")

    from substrate_mcp import db as db_mod
    from substrate_mcp import scanner as scanner_mod
    from substrate_mcp.embeddings import make_embedder, SubstrateChroma

    conn = db_mod.connect(cfg.db_path)
    embedder = make_embedder(cfg.embedding_provider, cfg.embedding_model,
                             base_url=cfg.ollama_base_url, api_key=cfg.ollama_api_key)
    chroma = SubstrateChroma(cfg.chroma_path, embedder)
    v = next(vv for vv in cfg.vaults if vv.name == wire.VAULT)

    t0 = time.time()
    # DELTA: collection + sha256 left intact → scanner re-embeds only changed files.
    report = scanner_mod.scan_vault(
        cfg, conn, v, embed_now=True, chroma=chroma,
        progress=lambda msg: print("  " + msg, flush=True),
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
    return {
        "elapsed_s": round(elapsed, 1),
        "files_indexed": n_files,
        "chunks_total": n_chunks,
        "chunks_embedded": n_embedded,
        "chroma_vectors": n_vec,
        "scan_report": report.__dict__,
    }


# ---------------------------------------------------------------- main

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="report whether a reindex is needed; do NOT index")
    ap.add_argument("--force", action="store_true",
                    help="reindex even if nothing changed since the marker")
    ap.add_argument("--ensure-embedder", action="store_true",
                    help="bring embed-pplx up via the resource manager if needed")
    args = ap.parse_args(argv)

    if not CORPUS.is_dir():
        print(f"FATAL: corpus dir not found: {CORPUS}\n"
              f"       The exporter has not run yet "
              f"(company up agent-sessions-exporter).", file=sys.stderr)
        return 2

    sig = corpus_signature()
    marker = load_marker()
    need, why = needs_reindex(sig, marker)

    print("claude_sessions_reindex — beat")
    print(f"  corpus: {CORPUS}  ({sig['n_files']} md files)")
    print(f"  decision: {'REINDEX' if need else 'skip'} — {why}")

    if args.check:
        # report-only: never index, always exit 0 (the cheap probe)
        return 0

    if not need and not args.force:
        # The cheap common path: nothing changed → touch nothing, no embedder.
        return 0

    # There is work. The embedder must be up (we never fake an index).
    if not embedder_up():
        if args.ensure_embedder:
            if not ensure_embedder():
                print("  ✗ embed-pplx could not be made healthy — leaving marker "
                      "stale so the next fire retries.", file=sys.stderr)
                return 1
        else:
            print("  ✗ embed-pplx is DOWN and there are files to index.\n"
                  "    The marker is left STALE so the next fire (or a manual run) "
                  "retries once the embedder is up.\n"
                  "    Bring it up:  company up embed-pplx   "
                  "(or re-run this with --ensure-embedder).", file=sys.stderr)
            return 1

    try:
        result = run_delta_reindex()
    except Exception as e:  # noqa: BLE001 — fail loud, leave marker stale for retry
        print(f"  ✗ reindex FAILED: {type(e).__name__}: {e}", file=sys.stderr)
        return 1

    if result["chroma_vectors"] == 0:
        print("  ✗ index produced 0 vectors — not advancing the marker.", file=sys.stderr)
        return 1

    # Success → advance the marker so the next fire is cheap.
    save_marker(sig, extra={
        "files_indexed": result["files_indexed"],
        "chunks_embedded": result["chunks_embedded"],
        "chroma_vectors": result["chroma_vectors"],
    })
    sr = result["scan_report"]
    print(f"  ✓ reindexed in {result['elapsed_s']}s — "
          f"files {result['files_indexed']} "
          f"(indexed {sr.get('files_indexed')}, unchanged {sr.get('files_unchanged')}, "
          f"deleted {sr.get('files_deleted')}) · "
          f"chunks embedded {result['chunks_embedded']} · "
          f"chroma vectors {result['chroma_vectors']}")
    if sr.get("errors"):
        print(f"  ! scan reported {len(sr['errors'])} error(s):", file=sys.stderr)
        for e in sr["errors"][:10]:
            print(f"      {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
