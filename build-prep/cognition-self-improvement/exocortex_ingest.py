#!/usr/bin/env python3
"""exocortex_ingest.py — COMPOSITION ① the repo-exocortex ingest (the reusable module).

Adopted: the INGEST lane was meant to write this but died on a stream-timeout (G8); written directly now
(no-defer). Ingests a set of repo files into the embedded, queryable corpus (space='repo') so an agent can
`Suite.query_corpus(text, space='repo')` — ask the codebase instead of cold-reading it.

REUSE-DON'T-PARALLEL: no new corpus/embed/index path. The pipeline is:
  0. WALK (deterministic, no model): collect .py/.md files under the given roots, skip junk.
  1. FAN the digest CONCURRENTLY: cognition.run_items(repo_digest, [file-contents]) — 1 role × N units on
     the swarm (32 slots now), each → a {digest, kind} (RepoDigestOut).
  2. CAPTURE+EMBED: Suite.capture_corpus(records) where each record = {source_address: code://<path>
     (the SHORT retrieval KEY — G18: content goes in output, NOT source_address), output: the digest,
     projection: 'repo'} → write_corpus_record (lineage-gated) + embed-on-write into space='repo'.
IDEMPOTENT / resume-safe: capture_corpus → put_content is write-once (same digest → same cas → no-op
overwrite), so re-running over the whole repo just adds the not-yet-ingested files. GPU-aware: the embed
needs bge-m3 resident (warm it via run_role(op='embed', ensure=True) before calling; co-resides w/ chat-4b).

Usage (in-process):  from exocortex_ingest import ingest ; ingest(suite, roots=[...], project=..., session=..., max_files=...)
The FLOOR: pure run:// computation — no resolve/approve/dispatch.
"""
import os
import sys

SKIP_DIRS = {"__pycache__", ".git", "node_modules", ".venv", ".data", "dist", "build"}
EXTS = (".py", ".md")
MAX_CHARS = 6000  # the per-file content slice fed to the digest role (a digest needs the head, not the whole file)


def walk_files(roots, *, exts=EXTS, max_chars=MAX_CHARS):
    """DETERMINISTIC walk → [{path, text}]. Sorted (stable order = resume-stable). Skips junk dirs + binaries."""
    out = []
    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for fn in sorted(filenames):
                if not fn.endswith(exts):
                    continue
                p = os.path.join(dirpath, fn)
                try:
                    t = open(p, encoding="utf-8").read()
                except (UnicodeDecodeError, OSError):
                    continue
                if len(t) < 80:           # skip near-empty (a digest of nothing is noise)
                    continue
                out.append({"path": p, "text": t[:max_chars]})
    return out


def ingest(suite, *, roots, project="company", session="exocortex", round="1",
           projection="repo", max_files=None, base_url=None, model=None):
    """Ingest `roots` into space=`projection`. Returns {walked, digested, captured, corpus_total}.
    REUSE: cognition.run_items (concurrent digest fan) + Suite.capture_corpus (embed-on-write)."""
    from runtime import cognition as C
    from runtime.roles import RoleRegistry
    rd = RoleRegistry().discover(["roles"]).get("repo_digest")
    if rd is None:
        raise RuntimeError("ingest: roles/repo_digest.py not discovered — cannot digest.")

    files = walk_files(roots)
    if max_files:
        files = files[:max_files]
    if not files:
        return {"walked": 0, "digested": 0, "captured": 0, "corpus_total": len(suite.list_corpus(project=project))}

    # 1. FAN the digest concurrently on the swarm (run_items: 1 role × N units)
    units = [f"FILE {f['path']}:\n\n{f['text']}" for f in files]
    kw = {}
    if base_url:
        kw["base_url"] = base_url
    if model:
        kw["model"] = model
    res = C.run_items(rd, units, suite.store, turn_id=f"ingest-{session}", max_tokens=200, **kw)
    resolved = res.resolved if isinstance(res.resolved, dict) else {i: v for i, v in enumerate(res.resolved)}

    # 2. build records (source_address = the PATH key, output = the digest) + CAPTURE+EMBED
    records = []
    for i, f in enumerate(files):
        dig = resolved.get(i)
        if not dig:                       # a skipped/failed unit (F2 per-unit resilience) — don't fabricate
            continue
        records.append({"source_address": f"code://{f['path']}", "output": dig,
                        "kind": "capture", "projection": projection})
    if records:
        suite.capture_corpus(records, project=project, session=session, round=round)
    return {"walked": len(files), "digested": len(records), "captured": len(records),
            "corpus_total": len(suite.list_corpus(project=project))}


if __name__ == "__main__":
    sys.path.insert(0, "/home/tim/company")
    from runtime.suite import Suite
    from runtime.registry import NodeRegistry
    from store.fs_store import FsStore
    roots = sys.argv[1:] or ["runtime", "store", "contracts", "mcp_face", "fabric", "ops/cli", "roles"]
    s = Suite(FsStore(".data/store"), NodeRegistry().discover(["nodes"]), nodes_dir="nodes")
    print(ingest(s, roots=roots, session="exocortex-core"))
