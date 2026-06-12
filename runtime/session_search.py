"""runtime/session_search.py — the SEARCH→HANDLE join (Session Fabric R4.2/R4.5; research lane 5).

THE CHAIN THIS CLOSES (the spec's R4 decompression): a search hit over the session corpus is not a
file path — it is a LIVE HANDLE. Every result carries the session_id (the join key both systems
already share), the session's LIVE registry state (joined at query time, never cached — a session
that was closed ten minutes ago may be supervised-live now), the matched POINT (turn/speaker/anchor,
the coordinate R3.4's launch-at-point adapter consumes), and the launch-ready commands (the
session_post forms the verb router accepts). Search → handle → act, one envelope.

WHO IT IS FOR — both faces (R4.4): Tim's UI renders these envelopes as cards; MCP agents call
sessions(op="search", q=…) (mcp_face/tools/sessions.py routes here) and post the act themselves.
Not UI-only — the supervisor and any company-MCP agent walk the same chain.

THE TWO SEARCH MODES (a closed, declared registry — MODES below — per the fractal-registries law;
the future heart projects this, R11 frame):

  semantic — the embedding search over the claude-sessions substrate index (pplx-embed-context-v1-4b,
             2560-d int8 cosine, the isolated state dir). The query must be embedded IN THE SAME
             SPACE, so this mode NEEDS the `embed-pplx` service (GPU) up; the vector query runs in
             the overlord venv (which has chromadb; this venv deliberately does not) via the proven
             venv-bridge pattern (the 2-stage rerank precedent: JSON over a subprocess seam,
             ops/wire_substrate_claude_sessions.py --json). Embedder down ⇒ TEACHING error naming
             `company up embed-pplx` — never silent emptiness, never a silent fallback.
  lexical  — term search over the SAME index's chunk text (substrate.db is plain sqlite; the chunk
             text rides in it). Zero models, zero GPU, always available. Honest ranking: distinct
             query terms present, then total occurrences.

  mode="auto" uses semantic when available, otherwise lexical — and DECLARES which it used in the
  envelope (mode_used + semantic.why). A declared choice is not a silent fallback; the caller always
  sees what kind of search answered.

"AT A POINT" — capability-honest (lane 5, settled): headless `claude --resume` restores the TIP;
there is no native resume-at-turn. So the point rides the envelope two ways: (1) `point` carries the
matched chunk's coordinate (anchor `turn-N-speaker[-ts][-pK]`, heading_path, chunk_address) — the
input R3.4's timeline/launch-at-point adapter takes when it lands; (2) the commands quote the matched
snippet into the MESSAGE body (the woken/consulted session has full context and locates the anchor
itself). Soft point now, hard point via R3.4 — both shapes from the same field.

THE FLOOR HOLDS: this module is a PURE READ. It never spawns, never posts mail, never emits fabric
events. Acting on a handle is the caller's second, deliberate step (session_post — the CQRS write
twin), and only the supervisor service executes wake/consult/deliver intents.

UNROUTABLE HONESTY: a corpus hit whose session the registry doesn't know is still a REAL hit — it is
returned with routable=false + the registry's own teaching error, never dropped, never given a
fabricated state.

INDEX PROVENANCE (honest): the corpus + index are the THROWAWAY-INTERIM transcript pipeline
(ops/agent_sessions_exporter.py → ~/corpora/claude-sessions → ops/claude_sessions_reindex.py beat →
the isolated substrate state dir). The envelope's `index` block states counts + embedded coverage on
every call, so a stale/partial index is visible, not assumed away. When the real memory system
replaces the interim index, THIS adapter is the one seam to repoint (MODES["semantic"]/["lexical"]
entries name their backing) — the handle/act layers above do not change.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

# ── the backing index (registry-is-truth: these mirror ops/wire_substrate_claude_sessions.py) ────
STATE_DIR = Path(os.environ.get(
    "SUBSTRATE_MCP_STATE_DIR",
    Path.home() / ".cache" / "company" / "substrate-claude-sessions")).resolve()
DB_PATH = STATE_DIR / "substrate.db"
VAULT = "claude-sessions"
CORPUS = Path(os.environ.get(
    "CLAUDE_SESSIONS_CORPUS", str(Path.home() / "corpora" / "claude-sessions"))).resolve()
PPLX_HEALTH = os.environ.get("PPLX_EMBED_HEALTH", "http://127.0.0.1:8007/health")
OVERLORD = Path(os.environ.get("OVERLORD_REPO", "/home/tim/repos/obsidian-overlord")).resolve()
OVERLORD_PY = OVERLORD / ".venv" / "bin" / "python"
WIRE = Path(__file__).resolve().parent.parent / "ops" / "wire_substrate_claude_sessions.py"

LEX_SCAN_CAP = 5000          # max candidate chunks pulled for python-side lexical scoring
SNIPPET_CHARS = 280          # concise snippet length (detailed carries the full chunk text)

# ── the mode registry (R11 frame: search modes are DATA the future heart projects, not code paths
#    an agent must read to discover). Adding a mode = adding an entry + its _search_<name> fn. ────
MODES = {
    "semantic": {
        "description": "embedding search (pplx-embed 2560-d int8 cosine) over the claude-sessions "
                       "substrate index — meaning, not substrings",
        "needs": "embed-pplx service up (GPU; `company up embed-pplx`) + the overlord venv "
                 "(chromadb) for the vector query",
        "backing": "chroma collection vault_claude-sessions in " + str(STATE_DIR),
    },
    "lexical": {
        "description": "term search over the same index's chunk text (substrate.db sqlite) — "
                       "zero models, always available",
        "needs": "the substrate.db index file (built by ops/claude_sessions_reindex.py)",
        "backing": str(DB_PATH),
    },
    "auto": {
        "description": "semantic when available, else lexical — the choice DECLARED in the "
                       "envelope (mode_used), never silent",
        "needs": "nothing beyond one of the above",
        "backing": "dispatch",
    },
}

_STOP = {"the", "a", "an", "of", "to", "in", "on", "for", "and", "or", "is", "it",
         "was", "what", "how", "did", "do", "we", "i", "you", "about", "with", "that"}

_ANCHOR_RE = re.compile(r"^turn-(\d+)-(tim|claude)(?:-(.*))?$")
_TS_RE = re.compile(r"(\d{4}-\d{2}-\d{2}-\d{4})")


# ── availability + index stats (every envelope states its ground) ────────────────────────────────

def semantic_availability() -> dict:
    """Can the semantic mode answer RIGHT NOW? {available, why}. Three real preconditions, each
    named when missing — the caller (and Tim's surface) sees exactly which leg is down."""
    if not OVERLORD_PY.exists():
        return {"available": False,
                "why": f"overlord venv python missing at {OVERLORD_PY} — the vector query runs "
                       f"there (chromadb is deliberately not in this venv)"}
    if not (STATE_DIR / "chroma").exists():
        return {"available": False,
                "why": f"no chroma index at {STATE_DIR}/chroma — build it: "
                       f"python ops/wire_substrate_claude_sessions.py setup && … index"}
    try:
        with urllib.request.urlopen(PPLX_HEALTH, timeout=3) as r:
            h = json.loads(r.read())
        if h.get("status") != "ok":
            return {"available": False, "why": f"embed-pplx at {PPLX_HEALTH} not ready: {h}"}
    except Exception as e:
        return {"available": False,
                "why": f"embed-pplx embedder DOWN at {PPLX_HEALTH} ({type(e).__name__}) — the "
                       f"query must be embedded in the index's own space. Bring it up: "
                       f"company up embed-pplx (GPU ~8.2G — the resource manager arbitrates)"}
    return {"available": True, "why": "embedder healthy + chroma index + overlord venv present"}


def _db() -> sqlite3.Connection:
    """Read-only connection to the substrate index (URI mode=ro — this module can never write the
    index, by construction). Fail-loud teaching if the index doesn't exist."""
    if not DB_PATH.exists():
        raise ValueError(
            f"session search: no transcript index at {DB_PATH}. The interim pipeline builds it: "
            f"the exporter writes ~/corpora/claude-sessions (company up agent-sessions-exporter), "
            f"then ops/claude_sessions_reindex.py indexes it (needs embed-pplx up). Until then, "
            f"sessions(op='list', q=…) still searches titles/names/ids.")
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def index_stats(conn: sqlite3.Connection) -> dict:
    """The envelope's provenance block: how much corpus, how much of it embedded. A partial embed
    coverage (semantic blind spots) is DECLARED on every result, never discovered by surprise."""
    files = conn.execute(
        "SELECT COUNT(*) c FROM addresses WHERE vault=? AND kind='file'", (VAULT,)).fetchone()["c"]
    chunks = conn.execute(
        "SELECT COUNT(*) c FROM chunks ch JOIN addresses a ON a.id=ch.address_id WHERE a.vault=?",
        (VAULT,)).fetchone()["c"]
    embedded = conn.execute(
        "SELECT COUNT(*) c FROM chunks ch JOIN addresses a ON a.id=ch.address_id "
        "WHERE a.vault=? AND ch.embedded_at IS NOT NULL", (VAULT,)).fetchone()["c"]
    return {"db": str(DB_PATH), "files": files, "chunks": chunks, "chunks_embedded": embedded,
            "embed_coverage": round(embedded / chunks, 3) if chunks else 0.0}


# ── the two search legs (each returns ranked chunk-candidates of one shape) ──────────────────────
# candidate := {chunk_address, anchor, heading_path, text, rel_path, frontmatter(dict), score, why}

_CAND_SQL = ("SELECT c.chunk_address, c.anchor, c.heading_path, c.text, a.rel_path, a.frontmatter "
             "FROM chunks c JOIN addresses a ON a.id = c.address_id WHERE a.vault = ? ")


def _row_to_cand(row, score: float, why: str) -> dict:
    fm = {}
    if row["frontmatter"]:
        try:
            fm = json.loads(row["frontmatter"])
        except (json.JSONDecodeError, TypeError):
            fm = {}
    return {"chunk_address": row["chunk_address"], "anchor": row["anchor"],
            "heading_path": row["heading_path"], "text": row["text"],
            "rel_path": row["rel_path"], "frontmatter": fm, "score": score, "why": why}


def _search_lexical(conn: sqlite3.Connection, q: str, fetch: int) -> list[dict]:
    """Term search over chunk text. Ranking is HONEST and simple: chunks containing more DISTINCT
    query terms rank first, ties broken by total occurrences. No tf-idf theater — the semantic mode
    is where ranking-by-meaning lives."""
    terms = [t for t in re.findall(r"[a-z0-9_./-]+", q.lower()) if len(t) >= 2 and t not in _STOP]
    if not terms:
        raise ValueError(
            f"session search (lexical): the query {q!r} reduced to no searchable terms — "
            f"give it at least one word of 2+ characters that isn't a stopword.")
    where = " AND (" + " OR ".join("instr(lower(c.text), ?) > 0" for _ in terms) + ")"
    rows = conn.execute(_CAND_SQL + where + f" LIMIT {LEX_SCAN_CAP}", (VAULT, *terms)).fetchall()
    scored = []
    for row in rows:
        low = row["text"].lower()
        present = [t for t in terms if t in low]
        occurrences = sum(low.count(t) for t in present)
        score = len(present) * 1000 + occurrences
        scored.append(_row_to_cand(row, float(score),
                                   f"{len(present)}/{len(terms)} terms, {occurrences} occurrences"))
    scored.sort(key=lambda c: -c["score"])
    return scored[:fetch]


def _search_semantic(conn: sqlite3.Connection, q: str, fetch: int) -> list[dict]:
    """Embedding search via the venv bridge: the wire script (overlord venv: substrate config +
    embedder client + chroma) dumps the candidate pool as JSON; chunk metadata resolves back through
    THIS db connection so the envelope shape is identical to the lexical leg. Fail-loud end to end —
    a non-zero bridge exit surfaces the bridge's own stderr (which names the embedder when that is
    what's down)."""
    av = semantic_availability()
    if not av["available"]:
        raise ValueError(
            f"session search (semantic) cannot run: {av['why']}. Either bring the leg up, or call "
            f"mode='lexical' (same index, term-ranked, zero models) — never assume an empty result.")
    with tempfile.TemporaryDirectory(prefix="session-search-") as td:
        out = Path(td) / "pool.json"
        cmd = [str(OVERLORD_PY), str(WIRE), "search", q,
               "--json", str(out), "--fetch", str(fetch), "-k", str(fetch)]
        env = {**os.environ, "SUBSTRATE_MCP_STATE_DIR": str(STATE_DIR),
               "OVERLORD_REPO": str(OVERLORD)}
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180, env=env)
        if r.returncode != 0:
            raise ValueError(
                f"session search (semantic): the vector-query bridge failed "
                f"(exit {r.returncode}): {(r.stderr or r.stdout).strip()[-500:]}")
        pool = json.loads(out.read_text(encoding="utf-8"))
    cands = []
    for item in pool.get("candidates", []):
        addr = (item.get("metadata") or {}).get("address")
        if not addr:
            continue
        row = conn.execute(
            "SELECT c.chunk_address, c.anchor, c.heading_path, c.text, a.rel_path, a.frontmatter "
            "FROM chunks c JOIN addresses a ON a.id = c.address_id WHERE c.chunk_address = ?",
            (addr,)).fetchone()
        if row is None:                       # index moved under the chroma snapshot — honest skip,
            continue                          # the chunk no longer exists to hand anyone
        dist = item.get("distance")
        cos = (1.0 - dist) if isinstance(dist, (int, float)) else 0.0
        cands.append(_row_to_cand(row, cos, f"cosine~{cos:.3f}"))
    return cands[:fetch]


# ── point + handle construction ───────────────────────────────────────────────────────────────────

def _point(cand: dict) -> dict:
    """The matched chunk's COORDINATE — the 'at a point' carrier. turn/speaker parsed from the
    exporter's anchor convention (`turn-N-speaker[-YYYY-MM-DD-HHMM][-pK]`); the raw anchor +
    chunk_address always ride along (R3.4's adapter input; also the substrate's own address form)."""
    m = _ANCHOR_RE.match(cand["anchor"] or "")
    ts = _TS_RE.search(cand["anchor"] or "")
    return {"chunk_address": cand["chunk_address"], "anchor": cand["anchor"],
            "heading_path": cand["heading_path"],
            "turn": int(m.group(1)) if m else None,
            "speaker": m.group(2) if m else None,
            "ts_hint": ts.group(1) if ts else None}


def _commands(sid: str, primary_verb: str | None, snippet: str) -> dict:
    """Launch-ready forms (lane-5 envelope, Layer 2). The point rides the MESSAGE (capability-honest
    — no native resume-at-turn): quote the snippet, the target locates its own anchor. These are the
    EXACT tool calls — an agent copies, fills <>, fires."""
    quote = snippet[:120].replace("'", "’")
    base = {
        "describe": f"sessions(op='describe', session='{sid}')",
        "inspect_transcript": f"read ~/corpora/claude-sessions/<project>/{sid}.md — the full "
                              f"conversation, no waking (R3.2)",
        "consult": f"session_post(to='session://{sid}', verb='consult', message='Re your point "
                   f"“{quote}…” — <your question>', from_session='session://<your-id>')",
        "at_point": "the point rides the message (quote `snippet`; the session has full context). "
                    "Hard launch-at-point = R3.4's timeline adapter, taking `point` as input.",
    }
    if primary_verb == "deliver":
        base["deliver"] = (f"session_post(to='session://{sid}', verb='deliver', "
                           f"message='<push into the live conversation>', "
                           f"from_session='session://<your-id>')")
    if primary_verb == "wake":
        base["wake"] = (f"session_post(to='session://{sid}', verb='wake', message='Re “{quote}…” "
                        f"— <what to do now>', from_session='session://<your-id>')")
    if primary_verb == "queue":
        base["queue"] = (f"session_post(to='session://{sid}', verb='auto', message='<queued for its "
                         f"next turn>', from_session='session://<your-id>')")
    return base


def _handle(suite, sid: str, best: dict, hit_count: int, mode_used: str, detail: str) -> dict:
    """ONE search result = ONE live handle: corpus hit ⨝ live registry row (joined NOW — the state
    is what routing would see at this instant) + point + commands. Unroutable stays honest."""
    routable, registry_error, row = True, None, {}
    try:
        row = suite.get_agent_session(sid)
    except ValueError as e:
        routable, registry_error = False, str(e)
    state = row.get("state")
    # the same routing rule session_post(verb='auto') applies — shown here so the result displays
    # the verb that would fire NOW (lane 5: primary_verb must be computed at query time)
    primary_verb = (None if not routable else
                    {"supervised-live": "deliver", "closed": "wake"}.get(state, "queue"))
    snippet = " ".join((best["text"] or "").split())
    out = {
        "session_id": sid,
        "session_address": f"session://{sid}",
        "title": row.get("title") or (best["frontmatter"].get("title") if best["frontmatter"] else None),
        "state": state,
        "cwd": row.get("cwd") or best["frontmatter"].get("cwd"),
        "last_activity": row.get("last_activity"),
        "routable": routable,
        "score": best["score"], "score_why": best["why"], "mode": mode_used,
        "hits_in_session": hit_count,
        "point": _point(best),
        "snippet": snippet if detail == "detailed" else snippet[:SNIPPET_CHARS],
        "primary_verb": primary_verb,
        "commands": _commands(sid, primary_verb, snippet),
    }
    if registry_error:
        out["registry_error"] = registry_error
    if detail == "detailed":
        out["registry_row"] = row
        out["transcript_rel_path"] = best["rel_path"]
    return out


# ── the one entry point ───────────────────────────────────────────────────────────────────────────

def search_sessions(suite, q: str, k: int = 8, mode: str = "auto", state: str | None = None,
                    detail: str = "concise", include_unroutable: bool = True) -> dict:
    """Search the session corpus by content and return LIVE HANDLES (R4.2). One result per session
    (the best-matching chunk leads; hits_in_session counts the rest), joined at query time against
    the live registry, with the point + the runnable commands. Pure read.

    q       the query (meaning for semantic; terms for lexical).
    k       max sessions returned.
    mode    'auto' | 'semantic' | 'lexical' (MODES — the declared registry above).
    state   optional pre-filter on the LIVE registry state (closed vocabulary — unknown raises).
    detail  'concise' | 'detailed' (full chunk text + full registry row).
    include_unroutable  keep corpus hits the registry doesn't know (routable=false) — default True.
    """
    if not isinstance(q, str) or not q.strip():
        raise ValueError("session search: `q` is required — the content query. "
                         "sessions(op='list', q=…) is the title/name/id substring filter instead.")
    if mode not in MODES:
        raise ValueError(f"session search: unknown mode {mode!r}. Valid: {list(MODES)} — "
                         + " · ".join(f"{m}={v['description']}" for m, v in MODES.items()))
    if state is not None and state not in suite.AGENT_SESSION_STATES:
        raise ValueError(
            f"session search: unknown state filter {state!r} — the registry's closed vocabulary is "
            f"{list(suite.AGENT_SESSION_STATES)}. Fail loud, never filter on a fabricated state.")
    if detail not in ("concise", "detailed"):
        raise ValueError(f"session search: detail must be 'concise' or 'detailed', got {detail!r}.")

    conn = _db()
    try:
        stats = index_stats(conn)
        sem = semantic_availability()
        mode_used = mode
        if mode == "auto":
            mode_used = "semantic" if sem["available"] else "lexical"
        fetch = max(k * 4, 20)                # chunk pool > session count (grouping eats duplicates)
        cands = (_search_semantic(conn, q.strip(), fetch) if mode_used == "semantic"
                 else _search_lexical(conn, q.strip(), fetch))

        # group chunk hits → one handle per session, best chunk leads (candidates arrive ranked)
        by_sid: dict[str, dict] = {}
        counts: dict[str, int] = {}
        for c in cands:
            sid = c["frontmatter"].get("session_id") or Path(c["rel_path"]).stem
            counts[sid] = counts.get(sid, 0) + 1
            by_sid.setdefault(sid, c)

        results = []
        for sid, best in by_sid.items():
            h = _handle(suite, sid, best, counts[sid], mode_used, detail)
            if not h["routable"] and not include_unroutable:
                continue
            if state is not None and h["state"] != state:
                continue
            results.append(h)
            if len(results) >= k:
                break

        return {
            "q": q.strip(), "mode_requested": mode, "mode_used": mode_used,
            "semantic": sem, "index": stats,
            "chunks_matched": len(cands), "sessions_found": len(results),
            "results": results,
            "note": "each result is a LIVE handle: state joined at query time; act via the "
                    "commands (session_post — the write twin); verify the act via "
                    "sessions(op='watch') events after your posted seq. An empty `results` with "
                    "chunks_matched=0 is an honest no-match (the corpus may simply not contain it"
                    " — index provenance above).",
        }
    finally:
        conn.close()
