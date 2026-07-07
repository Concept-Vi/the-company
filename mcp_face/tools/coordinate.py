"""mcp_face/tools/coordinate.py — the COORDINATE QUERY's agent face (L11; file-drop tool).

One question across ALL the ledger's axes at once: "about X (semantic) ∧ mentioning Y (lexical) ∧ under
path P ∧ changed after T ∧ reachable from Z via <kinds> (graph)" — answered by ONE Postgres function,
ledger.query(spec jsonb) (migration 0016), the same definition the UI face calls via PostgREST rpc
(one function → two faces). This tool is the thin agent face: it embeds `semantic.text` through the
fabric's default embedder (pplx-2560 @ :8007 — the desc/docs/history/exchange spaces' lens), passes
everything else through verbatim, and returns the function's results + meta.plan (every leg's counts —
under-recall is never silent).

For the nomic-3584 spaces (code/symbol) pass a pre-computed `vector` in `semantic` instead of `text`
(the code lens embeds via ollama :11434 — a caller with code-lens needs owns that embed).
"""
from __future__ import annotations

import json
import os
import subprocess

OPS = ("query", "vocabulary", "save", "saved", "run")

_PG = {"host": os.environ.get("COMPANY_LEDGER_PGHOST", "127.0.0.1"),
       "port": os.environ.get("COMPANY_LEDGER_PGPORT", "15432"),
       "user": os.environ.get("COMPANY_LEDGER_PGUSER", "postgres"),
       "db": os.environ.get("COMPANY_LEDGER_PGDB", "postgres"),
       "pw": os.environ.get("COMPANY_LEDGER_PGPASSWORD", "postgres")}


def _call_query(spec: dict) -> dict:
    body = json.dumps(spec)
    tag, i = "$cq$", 0
    while tag in body:
        i += 1
        tag = f"$cq{i}$"
    r = subprocess.run(["psql", "-h", _PG["host"], "-p", _PG["port"], "-U", _PG["user"], "-d", _PG["db"],
                        "-v", "ON_ERROR_STOP=1", "-tA"],
                       input=f"select ledger.query({tag}{body}{tag}::jsonb);",
                       capture_output=True, text=True, timeout=120,
                       env={**os.environ, "PGPASSWORD": _PG["pw"]})
    if r.returncode != 0:
        # surface the function's own teaching RAISE verbatim (it names the bad key/cap + the fix)
        raise ValueError(f"ledger.query refused: {(r.stderr or '').strip()[:500]}")
    return json.loads(r.stdout)


def _saved_registry():
    """Saved queries — ActionRegistry rows over saved_queries.json (registry-is-truth, mtime-fresh,
    atomic; the cascades/jobs precedent). A row: {name(=id), label, spec, created_by, created_at}."""
    import os as _os
    from runtime.coherence_actions import ActionRegistry
    from fabric import config as fcfg
    return ActionRegistry(_os.path.join(fcfg.STORE_DIR, "saved_queries.json"))


def save_query(qid: str, label: str, spec: dict, *, by: str = "") -> dict:
    """Register a question as an addressable thing (query://<id>). The spec is VALIDATED by actually
    running it once (limit=1) — a saved query that can't run is never written (fail-loud at save)."""
    if not qid or not isinstance(qid, str):
        raise ValueError("save_query: qid must be a non-empty string (addressable as query://<id>).")
    probe = dict(spec)
    probe["limit"] = 1
    run_query(probe)                                   # raises the fn's teaching refusal on a bad spec
    import time as _time
    row = {"name": qid, "id": qid, "label": label or qid, "spec": spec, "created_by": by,
           "created_at": _time.strftime("%Y-%m-%dT%H:%M:%SZ", _time.gmtime())}
    _saved_registry().save(row)
    return {"ok": True, "query": f"query://{qid}", "row": row}


def run_saved(qid: str, overrides: dict | None = None) -> dict:
    """Run a saved query by id (optional shallow overrides, e.g. {'limit': 50})."""
    row = _saved_registry().get(qid)
    if row is None:
        known = [r["id"] for r in _saved_registry().all()]
        raise ValueError(f"run_saved: no saved query {qid!r} — saved: {known} "
                         f"(save one via coordinate op='save').")
    spec = dict(row["spec"])
    if overrides:
        spec.update(overrides)
    return run_query(spec)


def watch_query(qid: str) -> dict:
    """The jobs HANDLER for standing watches: run the saved query, fingerprint its result ADDRESSES,
    diff vs the last run's fingerprint (watch state json beside the registry), and on CHANGE file a
    board note naming exactly what appeared/vanished (never a silent drift). Returns the diff summary."""
    import hashlib as _h
    import json as _json
    import os as _os
    from fabric import config as fcfg
    res = run_saved(qid)
    addrs = sorted({x.get("address") for x in res.get("results", []) if x.get("address")})
    fp = _h.blake2b(_json.dumps(addrs).encode(), digest_size=12).hexdigest()
    sp = _os.path.join(fcfg.STORE_DIR, "query_watch_state.json")
    state = {}
    if _os.path.exists(sp):
        state = _json.load(open(sp))
    prev = state.get(qid, {})
    if prev.get("fp") == fp:
        return {"query": qid, "changed": False, "n": len(addrs)}
    appeared = sorted(set(addrs) - set(prev.get("addrs", [])))
    vanished = sorted(set(prev.get("addrs", [])) - set(addrs))
    state[qid] = {"fp": fp, "addrs": addrs}
    tmp = sp + ".tmp"
    _json.dump(state, open(tmp, "w"), indent=1)
    _os.replace(tmp, sp)
    if prev:                                            # first run establishes the baseline silently
        try:
            from runtime import noticeboard_face as _nb   # optional wire; the fallback is the event log
        except Exception:
            _nb = None
        note = (f"WATCH query://{qid} CHANGED: +{len(appeared)} appeared, -{len(vanished)} vanished. "
                f"appeared: {appeared[:8]}{'…' if len(appeared) > 8 else ''} · "
                f"vanished: {vanished[:8]}{'…' if len(vanished) > 8 else ''}")
        _file_watch_note(qid, note)
    return {"query": qid, "changed": bool(prev), "appeared": appeared[:20], "vanished": vanished[:20],
            "n": len(addrs), "baseline": not prev}


def _file_watch_note(qid: str, note: str) -> None:
    """Land the change note on the noticeboard (the operator-visible surface); the event log is the
    fallback — a change is NEVER silent."""
    import json as _json
    import subprocess as _sp
    import os as _os
    try:
        from runtime.cc_board import file_item
        file_item("signal", f"query-watch: {qid} changed", note, "job:watch_query")
        return
    except Exception:
        pass                                          # → the findings fallback below (verified reachable)
    try:                                                # fallback: the board MCP path via the store event log
        from store.fs_store import FsStore
        from fabric import config as fcfg
        FsStore(fcfg.STORE_DIR).append_finding({"address": f"query://{qid}", "kind": "watch-change",
                                                "note": note})
    except Exception as e:
        raise RuntimeError(f"watch_query: could not surface the change note ANYWHERE ({e}) — "
                           f"a silent watch is worse than none; wire a notice path.")


def run_query(spec: dict) -> dict:
    """THE shared entry both faces call (the MCP tool below + the bridge's /api/query route): embeds
    semantic.text under the RIGHT lens for the space (fabric/embed_routing — code/symbol → nomic-3584,
    else → pplx-2560), then runs the ONE Postgres function. Teaching refusals surface as ValueError;
    embedder-down as RuntimeError (each face maps them to its own error shape)."""
    if not isinstance(spec, dict) or not spec:
        raise ValueError("run_query requires a non-empty spec dict (see coordinate op='vocabulary').")
    spec = dict(spec)
    sem = spec.get("semantic")
    if isinstance(sem, dict) and sem.get("text") and not sem.get("vector"):
        from fabric.embed_routing import embed_query, lens_for_space
        space = sem.get("space") or "desc"
        vec = embed_query(sem["text"], space=space)
        sem = {**sem, "vector": vec}
        sem.pop("text", None)
        # the lens fixes the emb layer when the caller didn't pin one (read layer == write layer)
        if not sem.get("emb"):
            sem["emb"] = "nomic-code" if lens_for_space(space) == "nomic" else "pplx"
        spec["semantic"] = sem
    return _call_query(spec)


def register(mcp, suite):
    @mcp.tool()
    def coordinate(op: str = "query", spec: dict | None = None) -> dict:
        """Query the ledger's COORDINATE SPACE — every axis in one call, fused (L11: ledger.query, the
        same function the UI reads; one definition, two faces).

          op="vocabulary" — the spec schema + a worked example (self-description).
          op="query"      — `spec` = {project?, addresses?[…], filter?{path_under|[…], not_under,
                            node_type[], ext[], changed_after}, graph?{anchor, kinds[], direction:
                            out|in|both, depth≤3, expand}, paths?{kind|id|through}, scale?{space, rung,
                            top_clusters}, semantic?{text|vector, space, emb, k}, lexical?{text},
                            count?{by}, limit?}. semantic.text embeds under the RIGHT lens per space
                            (code/symbol → nomic-3584; else pplx-2560). Returns results + meta.plan (all
                            legs' counts — nothing silently under-recalls).
        """
        if op == "vocabulary":
            return {"op": "vocabulary",
                    "spec_keys": ["project", "filter", "graph", "semantic", "lexical", "limit"],
                    "example": {"filter": {"path_under": "runtime/", "changed_after": "2026-07-01"},
                                "semantic": {"text": "how the vector store works", "space": "desc", "emb": "pplx"},
                                "lexical": {"text": "supabase cutover"},
                                "limit": 10},
                    "notes": ["semantic.text → embedded via pplx-2560 (spaces: desc/docs/history/exchange/…)",
                              "code/symbol spaces are nomic-3584 — pass semantic.vector instead",
                              "graph.depth caps at 3; unknown spec keys RAISE with the valid set",
                              "meta.plan echoes every leg's counts (under-recall is never silent)"]}
        if op == "save":
            if not isinstance(spec, dict) or not spec.get("id") or not isinstance(spec.get("spec"), dict):
                raise ValueError("coordinate(op='save') needs spec={id, label?, spec:{…the query…}}.")
            return {"op": "save", **save_query(spec["id"], spec.get("label", ""), spec["spec"], by="mcp")}
        if op == "saved":
            rows = _saved_registry().all()
            return {"op": "saved", "count": len(rows),
                    "queries": [{"id": r["id"], "label": r.get("label", ""),
                                 "keys": sorted((r.get("spec") or {}).keys())} for r in rows]}
        if op == "run":
            if not isinstance(spec, dict) or not spec.get("id"):
                raise ValueError("coordinate(op='run') needs spec={id, overrides?}.")
            return {"op": "run", "query": spec["id"], **run_saved(spec["id"], spec.get("overrides"))}
        if op != "query":
            raise ValueError(f"coordinate: unknown op {op!r} — one of {OPS}.")
        return {"op": "query", **run_query(spec)}
