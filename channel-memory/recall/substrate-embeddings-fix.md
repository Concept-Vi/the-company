---
trust: fabric-derived
author: ch-al7jdfdr (lead, session bda8ce28)
date: 2026-06-14
verified: by-execution
---
# Substrate embeddings — recall-failure root cause FIXED + a second issue surfaced

## Root cause (fork-found, lead-VERIFIED by execution) — FIXED
`runtime/session_search.py` semantic mode was dead because `src/substrate_mcp/embeddings.py`
(in /home/tim/repos/obsidian-overlord) was DELETED — only bytecode survived in `__pycache__/`.
Verified: `ls embeddings.py` → not found; three `.pyc` survive (310/311/314); `import
substrate_mcp.embeddings` → ModuleNotFoundError. This broke the wire bridge AND cli.py/server.py.

**FIX (reversible, applied):** dropped the matching bytecode as a sourceless module —
`cp src/substrate_mcp/__pycache__/embeddings.cpython-311.pyc src/substrate_mcp/embeddings.pyc`
(venv is Python 3.11.13). VERIFIED: `import substrate_mcp.embeddings` OK (symbols make_embedder /
SubstrateChroma / OllamaEmbedder / OpenAIEmbedder); cli.py ✓ and server.py ✓ now import; a real
search runs PAST the import into the actual chroma query (root cause gone).
**Reversible:** `rm src/substrate_mcp/embeddings.pyc`. **Durable follow-up (held):** decompile the
.pyc → a real `embeddings.py` (no decompiler installed; pycdc handles 3.11). It's Tim's substrate
repo (untracked git) — flag to Tim.

## Second issue (NEWLY surfaced, NOT the same bug, NOT fixed — no green-paint)
With the import fixed, a real query now fails deeper: `chromadb.errors.InternalError: Error sending
backfill request to compactor: Failed to apply logs to the hnsw segment writer` (the old
21626-chunk transcript chroma index, chromadb 1.5.9). This is index/hnsw state, separate from the
import. NOT chased now because: (a) it's the throwaway transcript-search index; (b) the fork's NEW
recall scanner is SELF-CONTAINED (builds its own index via the pplx embedder on :8007 — does not use
this old chroma bridge), so the forward recall path is unaffected; (c) chasing chroma hnsw internals
is a rabbit hole. If the old 21626-chunk index is wanted, it needs a re-index (or a chroma reset).

## The check that should have caught this (no-silent-failures) — to coordinate
`session_search.semantic_availability()` returns available:True from THREE preconditions (venv exists
/ index dir exists / pplx :8007 /health ok) but never EXERCISES the bridge — so it green-lit a broken
bridge (import error before, chroma error now). Fix: exercise the bridge with a real 1-result query
and fail loud with the actual error. session_search.py is consumption-side (ambiguous-owned) —
coordinate with the fork before editing.
