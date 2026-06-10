"""mcp_face/tools/runs.py — the RUNS tool (consolidated; MCP-DESIGN-PRINCIPLE).

ONE resource (the RUN INDEX — #54 storage-discovery), an `op` selector — replaces the flat
list_runs / find_runs. Both fold here because they are the SAME resource: a read-time projection
over the `op.run` event log keyed by run:// addresses, scoped to the closed ENGINE_RUN_OPS, both
returning {runs, total_records}; find_runs literally calls list_runs + a role filter (reuse-don't-
parallel — the log IS the index, no parallel store). Read-only — no resolve/approve/dispatch (the
floor). Reuse-don't-parallel: wraps the existing Suite methods (list_runs / find_runs), no new engine.

DELIBERATELY NOT FOLDED HERE (distinct resources — honoured the don't-god-tool rule):
  - get_state / get_results  → keyed by `graph_id` (a GRAPH noun, not a run); results() is literally
                               a projection of state(). A different resource (a graph) — belongs in a
                               `graph`/`read` resource file, not the run index.
  - get_events               → the GLOBAL captured trajectory; no run/graph key at all (limit-only).
                               A different resource (the trajectory log).
Folding those in would build a god-tool whose params (graph / address-vs-graph-id) are ignored for
most ops — the exact confusion the principle's trade-off section forbids. Left for a separate lane.
"""
from typing import Literal



def register(mcp, suite):
    @mcp.tool()
    def runs(op: Literal["list", "find"], role: str = "", run_kind: str = "", run_op: str = "",
             since: int = -1, limit: int = 50) -> dict:
        """DISCOVER past engine runs — the agent-face RUN INDEX. Lists past
        run_role / run_items / run_reduce runs + their run:// output addresses, NEWEST-FIRST, so an
        agent can feed a DISCOVERED output as an INPUT (run_role inputs= / run_items items=, resolved
        via inspect_address) or re-run it — instead of only reading a run whose address it already
        KNOWS. A read-time projection over the op.run event log (the log IS the index — no parallel
        store). Pick `op`:

          op="list"  — list past runs, newest-first. Optional filters: `run_kind` (one engine run-op),
                       `run_op` (the operation), `since`, `limit`.
          op="find"  — the FILTERED query face: list narrowed by `role` (the runs OF a given role),
                       and/or `run_kind` / `run_op`. E.g. runs(op='find', role='ground') → ground's
                       past runs + their run:// addresses.

        Filters:
          `role`     — (op='find') the cognition role whose runs to return (e.g. 'ground').
          `run_kind` — narrow to ONE engine run-op. Valid values DERIVE from the live registry
                       (suite.ENGINE_RUN_OPS): cognition.run_role | cognition.run_items |
                       cognition.run_reduce. An unknown value fails loud with the live list.
          `run_op`   — narrow by the operation: generate | embed | role | rule | cluster.
          `since`    — an event seq cursor (exclusive); -1 = all. For pagination over the log.
          `limit`    — caps the returned rows (default 50).

        Returns {op, runs:[{address, op, run_op, turn_id, role, duration_ms, seq, ts}],
        total_records}. Read-only (no resolve/approve/dispatch — the floor)."""
        OPS = ("list", "find")
        if op not in OPS:
            return {"error": f"runs: unknown op {op!r}. Valid: {list(OPS)} — "
                    "list=all past runs (newest-first) · find=filtered by `role` (and/or run_kind/run_op)."}
        # registry-is-truth: `run_kind` maps to the engine `op` filter; Suite validates it against the
        # LIVE ENGINE_RUN_OPS and raises a teaching ValueError — so we never hardcode the enum here.
        if op == "list":
            res = suite.list_runs(op=(run_kind or None), run_op=(run_op or None),
                                  since=since, limit=limit)
        else:  # op == "find"
            res = suite.find_runs(role=(role or None), op=(run_kind or None),
                                  run_op=(run_op or None), since=since, limit=limit)
        return {"op": op, **res}
    return runs
