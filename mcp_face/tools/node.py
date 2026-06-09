"""mcp_face/tools/node.py — the NODE tool (consolidated; MCP-DESIGN-PRINCIPLE row 'node').

ONE resource (a graph-node), an `op` selector — replaces the flat create_node / delete_node /
apply_node / propose_node (4→1). All four are WRITES on the `node` resource, so the audit blesses the
grouping (CQRS keeps reads vs writes split, not writes-from-writes). Reuse-don't-parallel: wraps the
existing Suite methods (create_node/delete_node/propose_node/apply_node), no new engine, no 2nd path.

THE FLOOR (governance) is UNCHANGED by this consolidation — it lives INSIDE the Suite methods, not in
this wrapper:
  • op="propose" → Suite.propose_node SURFACES a `code_build` decision (default="reject") for the
    operator. It is NOT applied. Proposing is safe (a model call + a surfaced gate).
  • op="apply"   → Suite.apply_node routes through guard("code_build", confirmed=inbox.is_approved(id)).
    Authorization is READ from the substrate (resolved=='approve'), NEVER a caller flag — the agent that
    proposed cannot self-approve. This wrapper passes ONLY `surfaced_id` through, so NO field on this
    tool can reach `confirmed`. An external (cold) agent gains NO privileged action via consolidation:
    apply on an un-approved decision RAISES (GovernanceError) exactly as the flat tool did.

The instance-ops (create/delete) and the type-ops (propose/apply) take DISJOINT params, so the docstring
per-op guide + the missing-param teaching errors carry the load of steering the agent to the right fields.
"""


def register(mcp, suite):
    @mcp.tool()
    def node(op: str, graph: str = "", type: str = "", config: dict = {},
             node_id: str = "", name: str = "", spec: str = "", surfaced_id: str = "") -> dict:
        """Act on a graph-NODE — the unit of a composition graph (canvas). Pick `op`:

          op="create"  — ADD a node of `type` to `graph` (GENERIC — any registered node-type; see
                         cognition_info()/list_types for the type library). `config` (optional) seeds its
                         config (type defaults first, your config wins). `node_id` (optional) names it;
                         auto-named otherwise. Returns {node_id, address}. AUTO (reversible compose).
          op="delete"  — REMOVE `node_id` from `graph` along with every edge touching it. Returns {ok}.
                         AUTO (reversible).
          op="propose" — BUILD-DISPATCH: ask the brain to WRITE a NEW node-type module named `name`
                         doing `spec`. SURFACES it for the OPERATOR to approve — it is NOT applied here.
                         Returns {surfaced_id, name, code}. Proposing is SAFE.
          op="apply"   — APPLY a proposed node-type by its `surfaced_id` — succeeds ONLY if the OPERATOR
                         approved that surfaced decision (resolved=='approve'). The agent CANNOT
                         self-approve; approval is read from the substrate, not this call. Returns {path}.
                         An un-approved id REFUSES (governance), an unknown id fails loud.

        create/delete touch a LIVE graph (`graph` + node identity); propose/apply touch the node-TYPE
        library (`name`/`spec` to build, `surfaced_id` to apply). Don't mix the two param sets."""
        OPS = ("create", "delete", "propose", "apply")
        if op not in OPS:
            return {"error": f"node: unknown op {op!r}. Valid: {list(OPS)} — "
                    "create=add a node to a graph (graph+type) · delete=remove a node (graph+node_id) · "
                    "propose=brain writes a new node-TYPE (name+spec, surfaces for approval) · "
                    "apply=apply an OPERATOR-approved proposed type (surfaced_id)."}

        if op == "create":
            if not graph or not type:
                return {"error": "node(op='create') needs `graph` (the graph/canvas id) and `type` "
                        "(a registered node-type — see list_types/cognition_info). Optional: `config`, `node_id`."}
            nid = suite.create_node(graph, type, dict(config), node_id or None)
            return {"op": op, "graph": graph, "type": type, "node_id": nid,
                    "address": f"run://{graph}/{nid}"}

        if op == "delete":
            if not graph or not node_id:
                return {"error": "node(op='delete') needs `graph` (the graph id) and `node_id` "
                        "(the node to remove — get_state(graph) lists the live node ids)."}
            suite.delete_node(graph, node_id)
            return {"op": op, "graph": graph, "node_id": node_id, "ok": True}

        if op == "propose":
            if not name or not spec:
                return {"error": "node(op='propose') needs `name` (a name for the new node-TYPE) and "
                        "`spec` (what it should do, in natural language). It SURFACES for the operator — "
                        "not applied. Use op='apply' with the returned surfaced_id AFTER operator approval."}
            r = suite.propose_node(name, spec)
            # propose_node returns {id, name, code} on success, or {needs, id} if it hit unregistered ground.
            if "needs" in r:
                return {"op": op, "needs": r.get("needs"), "surfaced_id": r.get("id"),
                        "note": "the brain needed input it couldn't resolve — surfaced for the operator."}
            return {"op": op, "surfaced_id": r.get("id"), "name": r.get("name"), "code": r.get("code")}

        if op == "apply":
            if not surfaced_id:
                return {"error": "node(op='apply') needs `surfaced_id` (the id returned by op='propose'). "
                        "It succeeds ONLY after the OPERATOR has approved that surfaced decision — the "
                        "agent cannot self-approve (approval is read from the substrate, not this call)."}
            path = suite.apply_node(surfaced_id)
            return {"op": op, "surfaced_id": surfaced_id, "path": path, "applied": True}
    return node
