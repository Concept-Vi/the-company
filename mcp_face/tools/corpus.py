"""mcp_face/tools/corpus.py — the CORPUS tool (consolidated; MCP-DESIGN-PRINCIPLE instance 1).

ONE resource (the corpus), an `op` selector — replaces the flat list_corpus / find_corpus /
read_corpus_record AND exposes `query` (the ask-the-codebase semantic retrieve, G20, previously
unexposed). `detail` (concise|detailed) + `limit` keep responses token-efficient (concise is the
default — the flat list_corpus returned 65k chars; concise returns only the high-signal fields).
Read-only — no resolve/approve/dispatch (the floor). Reuse-don't-parallel: wraps the existing Suite
methods (list_corpus/find_corpus/read_corpus_record/query_corpus), no new engine.
"""


def register(mcp, suite):
    @mcp.tool()
    def corpus(op: str, project: str = "", kind: str = "", projection: str = "",
               source_address: str = "", address: str = "", text: str = "", space: str = "",
               k: int = 8, detail: str = "concise", limit: int = 50) -> dict:
        """Read the corpus — the engine's durable, embedded, addressed records (① repo-exocortex's
        'ask the codebase', + every capture pass's output). Pick `op`:

          op="query"  — ASK the corpus a natural-language question; returns the top-k nearest records by
                        meaning. `text` (required) = the question; `space` (optional) = an embeddable
                        space to search (e.g. 'repo' for the codebase — see cognition_info().spaces);
                        `k` = how many. This is the primary 'ask-the-codebase' retrieve.
          op="list"   — list records, newest-first; narrow with `project`.
          op="find"   — filter records by `project` / `kind` / `projection` / `source_address`.
          op="read"   — fetch ONE record's full content by its `address` (a run:// from list/find).

        `detail`: "concise" (default) returns high-signal fields only {source_address, projection, seq,
        address}; "detailed" returns the full records. `limit` (default 50) caps list/find. Read-only."""
        OPS = ("query", "list", "find", "read")
        if op not in OPS:
            return {"error": f"corpus: unknown op {op!r}. Valid: {list(OPS)} — "
                    "query=ask (text+space) · list=all (project) · find=filter · read=one (address)."}

        def _shape(rows):
            rows = list(rows)[:limit]
            if detail == "detailed":
                return rows
            return [{"source_address": r.get("source_address"), "projection": r.get("projection"),
                     "seq": r.get("seq"), "address": r.get("address")} for r in rows]

        if op == "query":
            if not text:
                return {"error": "corpus(op='query') needs `text` (the question). Optional: `space` "
                        "(an embeddable space, e.g. 'repo' — cognition_info().spaces), `k`."}
            return {"op": op, **suite.query_corpus(text, space=(space or None), k=k)}
        if op == "list":
            rows = suite.list_corpus(project=(project or None))
            return {"op": op, "project": project or None, "total": len(rows), "detail": detail,
                    "records": _shape(rows)}
        if op == "find":
            rows = suite.find_corpus(project=(project or None), kind=(kind or None),
                                     projection=(projection or None), source_address=(source_address or None))
            return {"op": op, "total": len(rows), "detail": detail, "records": _shape(rows)}
        if op == "read":
            if not address:
                return {"error": "corpus(op='read') needs `address` — a run:// corpus record address "
                        "(from op='list'/'find') OR a SOURCE address (e.g. the code:// ids op='query' "
                        "returns — they round-trip here)."}
            rec = suite.read_corpus_record(address)
            if rec is not None:
                return {"op": op, "address": address, "record": rec}
            # N1 — THE ROUND-TRIP: op='query' returns SOURCE ids (code://…); accept them here by
            # finding their record(s) (newest-first) instead of a silent {record:null}.
            rows = suite.find_corpus(source_address=address)
            if rows:
                rec_addr = rows[0].get("address")
                return {"op": op, "address": rec_addr, "source_address": address,
                        "record": suite.read_corpus_record(rec_addr)}
            # N1 — NO SILENT NULL: nothing found → a TEACHING error, never a bare null.
            return {"op": op, "address": address, "record": None,
                    "error": f"no corpus record found for {address!r} — pass a run://corpus record "
                    "address (from op='list'/'find') or a source address of an INGESTED file (the "
                    "code:// ids op='query' returns). If this source was never ingested, feed it "
                    "first: ingest(paths=[...]) — then it becomes readable + queryable."}
    return corpus
