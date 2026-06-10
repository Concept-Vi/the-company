"""mcp_face/tools/rule.py — the RULE tool (consolidated; MCP-DESIGN-PRINCIPLE).

ONE resource (a declarative routing RULE on a role), an `op` selector — replaces the flat
validate_rule / dry_run_rule / attach_rule AND exposes `detach` (the symmetric remove, previously
direct-only on the Suite — mirrors how corpus.py exposed the previously-unexposed `query`). A rule is
a deterministic condition AST + a destination (one of the 5 declarative kinds — NEVER a forbidden
resolve/approve/dispatch/claude-p verb; the floor). Reuse-don't-parallel: wraps the existing Suite
methods (validate_rule/dry_run_rule/attach_rule/detach_rule), no new engine, no 2nd path.

The floor: `validate`/`dry_run` are PURE reads (no effect, never route()). `attach`/`detach` are a
CONSTRAINED edit_role — they SURFACE a role_build proposal for the operator (propose-not-apply); they
never self-apply, and the destination grammar forbids the dispatch/claude-p verbs at construction.
"""
from typing import Literal



def register(mcp, suite):
    @mcp.tool()
    def rule(op: Literal["validate", "dry_run", "attach", "detach"], ast: dict = {}, destination: str = "", sample_resolved: dict = {},
             params: dict = {}, on_missing: str = "raise", role_id: str = "",
             rule: dict = {}, rule_id: str = "") -> dict:
        """Work with a role's declarative routing RULES — the deterministic 'when <condition> → route the
        value to <destination>' that fires after resolution. Pick `op`:

          op="validate" — INSPECT a rule's condition `ast` against the closed grammar (legal/deterministic?
                          which role-inputs does it reference? renderable within depth?) and, if you pass
                          `destination`, check it's one of the 5 declarative kinds (NEVER a forbidden
                          resolve/approve/dispatch verb). PURE read. Returns
                          {ok, errors[], references[], destination_ok, renderable, when_text, depth}.
          op="dry_run"  — RUN the routing DECISION over SAMPLE inputs (no effect, never routes). `ast` =
                          the condition; `sample_resolved` = a dict of resolved role-input values to test;
                          `destination` (default "inject"), `params`, `on_missing` ("raise"|...) shape the
                          rule. Returns {ok, decision:{fire, destination, value, reason}, when_text}.
                          The FE-facing 'with these inputs → this fires → routes to <dest>'.
          op="attach"   — ATTACH a declared `rule` (a full rule dict: id + when-ast + destination) onto a
                          role (`role_id`). Validates the rule (fail loud on a bad AST/destination), then
                          re-PROPOSES the role with the rule added — SURFACES a role_build for the operator
                          (propose-not-apply; never self-applies). Replace-or-add by the rule's id.
          op="detach"   — DETACH a rule from a role: pass `role_id` + `rule_id`. Re-proposes the role
                          WITHOUT that rule (propose-not-apply; surfaces for the operator).

        Params by op: validate→`ast`(+opt `destination`) · dry_run→`ast`+`sample_resolved`(+opt
        `destination`/`params`/`on_missing`) · attach→`role_id`+`rule` · detach→`role_id`+`rule_id`.
        A PROTECTED role refuses attach/detach. Authoring surfaces — never resolves/approves/dispatches."""
        OPS = ("validate", "dry_run", "attach", "detach")
        if op not in OPS:
            return {"error": f"rule: unknown op {op!r}. Valid: {list(OPS)} — "
                    "validate=inspect an AST (ast) · dry_run=route over sample inputs "
                    "(ast+sample_resolved) · attach=add a rule to a role (role_id+rule) · "
                    "detach=remove a rule from a role (role_id+rule_id)."}

        if op == "validate":
            if not ast:
                return {"error": "rule(op='validate') needs `ast` (the condition AST to check). "
                        "Optional: `destination` (validates it's one of the 5 declarative kinds)."}
            # match the flat tool: "" → None so an empty string isn't checked as a destination
            return {"op": op, **suite.validate_rule(ast, destination=(destination or None))}

        if op == "dry_run":
            if not ast:
                return {"error": "rule(op='dry_run') needs `ast` (the condition AST) and "
                        "`sample_resolved` (a dict of resolved role-input values to test the routing over)."}
            # match the flat tool's value-conversions: dict() the inputs; empty params → None
            return {"op": op, **suite.dry_run_rule(ast, dict(sample_resolved),
                                                    destination=destination or "inject",
                                                    params=(dict(params) or None), on_missing=on_missing)}

        if op == "attach":
            if not role_id or not rule:
                return {"error": "rule(op='attach') needs `role_id` (the role to attach onto) and "
                        "`rule` (a full rule dict: id + when-ast + destination). Surfaces a role_build "
                        "proposal for the operator; never self-applies."}
            if role_id not in suite.role_registry:
                return {"error": f"rule(op='attach'): unknown role {role_id!r}. Known roles come from the "
                        "live role registry (see cognition_info() / list_by_type). Fail loud."}
            return {"op": op, "role_id": role_id, **suite.attach_rule(role_id, rule)}

        if op == "detach":
            if not role_id or not rule_id:
                return {"error": "rule(op='detach') needs `role_id` and `rule_id` (the id of the rule to "
                        "remove). Surfaces a role_build proposal for the operator; never self-applies."}
            if role_id not in suite.role_registry:
                return {"error": f"rule(op='detach'): unknown role {role_id!r}. Known roles come from the "
                        "live role registry (see cognition_info() / list_by_type). Fail loud."}
            return {"op": op, "role_id": role_id, "rule_id": rule_id,
                    **suite.detach_rule(role_id, rule_id)}
    return rule
