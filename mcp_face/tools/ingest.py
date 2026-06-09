"""mcp_face/tools/ingest.py — the INGEST tool (① repo-exocortex, first-class; G21).

ONE tool: feed files into the embedded, queryable corpus so corpus(op='query') can answer questions
about the codebase. Thin wrapper over Suite.ingest_paths (the ONE walk+fan+capture+embed pipeline —
reuse-don't-parallel). Bounded per call (max_files) with a self-teaching response: `remaining` tells
the agent to call again; `skipped_existing` shows the incremental behaviour. FLOOR: pure run://
computation — declarative records, no resolve/approve/dispatch. GPU: the digest fan needs the chat
brain + the embed needs bge-m3 resident (capture fails LOUD on a down embedder — never a silent
unembedded record).
"""


def register(mcp, suite):
    @mcp.tool()
    def ingest(roots: list = [], paths: list = [], project: str = "company",
               session: str = "ingest", round: str = "1", space: str = "repo",
               max_files: int = 50, force: bool = False) -> dict:
        """Feed files into the embedded corpus so corpus(op='query', space='repo') can ANSWER QUESTIONS
        about them (the ask-the-codebase pipeline: walk → digest-fan on the swarm → capture+embed).

        `roots`     — directories to walk (deterministic; skips junk/binaries; .py/.md).
        `paths`     — explicit files (an unreadable explicit path fails loud).
        `space`     — the embeddable space to populate (default 'repo' — see cognition_info().spaces).
        `max_files` — bounds ONE call (default 50). The response's `remaining` > 0 → call again with the
                      same args (already-ingested files are skipped, so batches compose to full coverage).
        `force`     — re-ingest even if a file's record exists (default False = incremental skip;
                      NOTE: skip is path-keyed, so a CHANGED file needs force=True until the sha-refresh
                      pass lands).
        Returns {walked, skipped_existing, digested, captured, failed, remaining, corpus_total}.
        Lineage (project/session/round) rides into every record — required, never defaulted away."""
        if not roots and not paths:
            return {"error": "ingest: pass `roots` (directories to walk) and/or `paths` (explicit files). "
                    "E.g. roots=['runtime','store'] — then ask: corpus(op='query', space='repo', text=...)."}
        out = suite.ingest_paths(roots=list(roots) or None, paths=list(paths) or None, project=project,
                                 session=session, round=round, projection=space,
                                 max_files=max_files, force=force)
        if out.get("remaining"):
            out["_hint"] = (f"{out['remaining']} file(s) remaining — call ingest again with the same args "
                            "(already-ingested files are skipped automatically).")
        return out
    return ingest
