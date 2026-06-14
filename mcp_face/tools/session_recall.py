"""mcp_face/tools/session_recall.py — SEMANTIC recall + lenses over a session, as a first-class MCP tool.

The meaning-search layer on the structural scanner (Tim 2026-06-14: "build the embedding into the scanner
system… many ways useful, not just decisions"). Bridge-free: embeds via the Company-served :8007, reranks
via the Company-served :8008 — no overlord venv bridge, no in-process model deps.

File-drop tool (pkgutil auto-register) — takes effect on the NEXT MCP server start.

## Ops (lenses)
  op="find"       — semantic recall: q="what was said about X". General meaning search.
  op="decisions"  — q=<topic>: surfaces the DECISION (chose/switched/locked), not just discussion.
  op="open_loops" — UNRESOLVED threads: blockers, gaps, Tim's open questions (latest-first + resolution hint).
  op="catch_up"   — since=<iso ts | omit>: what happened in the window / since the last away-gap.
  op="timeline"   — q=<topic>: every place the topic was discussed, sorted by TIME (its arc).
  op="directives" — every genuine Tim ask, chronologically (the whole-slate ledger).

`session` = a transcript .jsonl path OR a bare session-id (resolved under ~/.claude/projects/*/<sid>.jsonl).
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

OPS = ("find", "decisions", "open_loops", "catch_up", "timeline", "directives")
INDEX_DIR = os.environ.get("RECALL_INDEX_DIR", str(Path.home() / "company" / ".data" / "recall-index"))


def _resolve(session: str) -> str:
    """A .jsonl path as-is, or a bare session-id resolved to its transcript under ~/.claude/projects/."""
    if session.endswith(".jsonl") and os.path.exists(session):
        return session
    base = Path.home() / ".claude" / "projects"
    hits = list(base.glob(f"*/{session}.jsonl"))
    if not hits:
        raise FileNotFoundError(
            f"session {session!r} — not a .jsonl path and no transcript found at "
            f"~/.claude/projects/*/{session}.jsonl. Pass the full transcript path or a known session-id.")
    return str(hits[0])


def register(mcp, suite):
    @mcp.tool()
    def session_recall(op: Literal["find", "decisions", "open_loops", "catch_up", "timeline", "directives"],
                       session: str, q: str = "", since: str = "", k: int = 8) -> dict:
        """Semantic recall + lenses over a session (meaning-search on the scanner; bridge-free, Company-served).

          op="find"       q=<query>     — general semantic recall.
          op="decisions"  q=<topic>     — the decision about a topic (what was chosen + why).
          op="open_loops"               — unresolved threads (blockers/gaps/open questions), latest-first.
          op="catch_up"   since=<iso?>  — what happened in the window / since the last away-gap.
          op="timeline"   q=<topic>     — when a topic was discussed, across the session (its arc).
          op="directives"               — every genuine Tim ask, chronologically.

        `session` = transcript .jsonl path OR a bare session-id. Embeds via :8007, reranks via :8008.
        """
        from runtime import session_lens as L
        try:
            jsonl = _resolve(session)
        except FileNotFoundError as e:
            return {"op": op, "ok": False, "error": str(e)}
        try:
            if op == "find":
                if not q:
                    raise ValueError("op='find' needs q=<query>.")
                return {"op": op, **L.find(jsonl, q, k=k, index_dir=INDEX_DIR)}
            if op == "decisions":
                if not q:
                    raise ValueError("op='decisions' needs q=<topic>.")
                return {"op": op, **L.decisions(jsonl, q, k=k, index_dir=INDEX_DIR)}
            if op == "open_loops":
                return {"op": op, **L.open_loops(jsonl, k=max(k, 25))}
            if op == "catch_up":
                return {"op": op, **L.catch_up(jsonl, since=since or None, k=max(k, 20))}
            if op == "timeline":
                if not q:
                    raise ValueError("op='timeline' needs q=<topic>.")
                return {"op": op, **L.timeline(jsonl, q, index_dir=INDEX_DIR)}
            if op == "directives":
                return {"op": op, **L.directives(jsonl)}
        except Exception as e:
            return {"op": op, "ok": False, "error": f"{type(e).__name__}: {e}"}
        raise ValueError(f"session_recall: unknown op {op!r} — one of {OPS}.")
