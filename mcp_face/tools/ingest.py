"""mcp_face/tools/ingest.py — the INGEST tool (① repo-exocortex, first-class; G21).

ONE tool, an `op` selector (MCP-DESIGN-PRINCIPLE): op='ingest' (default) feeds files into the embedded,
queryable corpus so corpus(op='query') can answer questions about the codebase; op='reindex' is the inverse
— it RECONCILES a space's vector index against a CURRENT source corpus (embed missing/changed, retract
orphaned), the EXPLICIT/on-demand twin of the auto freshness daemon (runtime/bridge.py:_freshness_loop,
which mtime-polls ONLY the 'extractions' space). ingest is a thin wrapper over Suite.ingest_paths (the ONE
walk+fan+capture+embed pipeline); reindex is a thin wrapper over runtime/freshness.reconcile_space /
reconcile_extractions (reuse-don't-parallel — the COMPLETE reconcile loop already exists; this just makes it
invokable for any space, on demand). Bounded ingest per call (max_files) with a self-teaching response.
FLOOR: declarative — no resolve/approve/dispatch. GPU: the digest fan needs the chat brain + the embed needs
the embedder resident (both fail/degrade LOUD on a down embedder — never a silent unembedded record).
"""


def register(mcp, suite):
    @mcp.tool()
    def ingest(op: str = "ingest", roots: list = [], paths: list = [], project: str = "company",
               session: str = "ingest", round: str = "1", space: str = "repo",
               max_files: int = 50, force: bool = False, retract_extra: bool = False) -> dict:
        """Feed files into the embedded corpus (op='ingest') OR reconcile a space's index against its current
        source (op='reindex'). Pick `op`:

        op='ingest' (default) — walk → digest-fan on the swarm → capture+embed, so corpus(op='query',
                      space='repo') can ANSWER QUESTIONS about the files.
          `roots`     — directories to walk (deterministic; skips junk/binaries; .py/.md).
          `paths`     — explicit files (an unreadable explicit path fails loud).
          `space`     — the embeddable space to populate (default 'repo' — see cognition_info().spaces).
          `max_files` — bounds ONE call (default 50). The response's `remaining` > 0 → call again with the
                        same args (already-ingested files are skipped, so batches compose to full coverage).
          `force`     — re-ingest even if a file's record exists (default False = incremental skip).
          Returns {walked, skipped_existing, digested, captured, failed, remaining, corpus_total}.

        op='reindex' — make a SPACE's vector index reflect its CURRENT source: embed missing/changed,
                      retract orphaned (runtime/freshness.reconcile_space). The EXPLICIT/on-demand twin of the
                      auto freshness daemon (bridge.py:_freshness_loop, which mtime-polls ONLY 'extractions').
                      `space` — the space to reconcile. 'extractions' uses its live asset files
                        (reconcile_extractions). Other spaces reconcile against their INGESTED corpus records
                        (the source_address+digest set) — an ADD/UPDATE reconcile.
                      `retract_extra` (default False — the CONSERVATIVE default for an on-demand call over a
                        possibly-partial corpus view; the auto daemon uses True for the full 'extractions'
                        asset set): True drops index entries no longer in the source. Embed leg needs the
                        embedder (:8007) up — degrades HONESTLY (reports degraded=true), never a silent
                        partial. Returns the freshness report {space, fresh_before, embedded, retracted,
                        degraded, fresh_after, counts}.
        Lineage (project/session/round) rides into every ingested record — required, never defaulted away."""
        if op not in ("ingest", "reindex"):
            return {"error": f"ingest: unknown op {op!r}. Valid: 'ingest' (feed files → corpus) | "
                    "'reindex' (reconcile a space's index against its current source)."}

        if op == "reindex":
            from runtime import freshness as _fr
            sp = space or "extractions"
            if sp == "extractions":
                # the high-value default: reconcile against the live asset files (reconcile_extractions)
                rep = _fr.reconcile_extractions(suite.store, retract_extra=retract_extra)
            else:
                # any other space: reconcile against its INGESTED corpus records (source_address → digest).
                # Reuse the corpus projection + the digest resolve (no new scan path) to build the
                # [{address, text}] reconcile input, then call reconcile_space.
                from runtime import corpus as _corpus, corpus_fusion as _cf
                seen, src = set(), []
                for row in _corpus.find_corpus(suite.store, projection=sp):   # ONE scan
                    sa = row.get("source_address")
                    if not sa or sa in seen:
                        continue
                    seen.add(sa)
                    txt = _cf._digest_from_cas(suite.store, row)              # cas already on the row — no re-scan
                    if isinstance(txt, str) and txt.strip():
                        src.append({"address": sa, "text": txt})
                if not src:
                    return {"op": "reindex", "space": sp, "error": f"reindex: no ingested corpus records "
                            f"found for space {sp!r} (find_corpus(projection={sp!r}) is empty) — there is "
                            "nothing to reconcile the index against. Feed it first: ingest(roots=[...], "
                            f"space={sp!r}). 'extractions' reconciles against its asset files instead."}
                rep = _fr.reconcile_space(suite.store, sp, src, retract_extra=retract_extra)
            return {"op": "reindex", **rep}

        if not roots and not paths:
            return {"error": "ingest(op='ingest'): pass `roots` (directories to walk) and/or `paths` "
                    "(explicit files). E.g. roots=['runtime','store'] — then ask: "
                    "corpus(op='query', space='repo', text=...)."}
        out = suite.ingest_paths(roots=list(roots) or None, paths=list(paths) or None, project=project,
                                 session=session, round=round, projection=space,
                                 max_files=max_files, force=force)
        if out.get("remaining"):
            out["_hint"] = (f"{out['remaining']} file(s) remaining — call ingest again with the same args "
                            "(already-ingested files are skipped automatically).")
        return {"op": "ingest", **out}
    return ingest
