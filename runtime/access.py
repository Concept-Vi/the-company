"""runtime/access.py — the EFFECTIVE-ACCESS resolver: may(principal, verb, address) / access_of(address).

④ THE CONTAINER, L2-IDENTITY — the genuinely-new organ the TENANCY study named (organ-studies/TENANCY.md
§3.7): "the effective-access resolver as ONE shared function ... projected to both MCP and UI, so the
permission the UI displays and the permission the gate enforces can never diverge."

ONE decision function (`_decide`) answers BOTH:
  · may(principal_address, verb, address)  → {allow, reason, via, ceiling}   (the gate's question)
  · access_of(address)                     → the roster: each member + the verbs it may   (the UI's read)
access_of calls the SAME _decide per (member, verb) — law 9: access_of shows the permission may() enforces.

THE LADDER (fail-closed floor; TENANCY §3.3):
  · operator kind                          → ALLOW all (identity IS the boundary — remote.py's law).
  · a member with role owner|keeper        → ALLOW all verbs on that container.
  · a member (other role)                  → ALLOW the read family only.
  · an agent holding an ACTIVE acts-for delegation from an operator, whose scopes admit the verb,
    within the delegation window                                → ALLOW, via=delegation, bounded by the
    ceiling (max_autonomy) the runtime guard then enforces.
  · everything else                        → DENY (fail-closed, with a legible reason).

REUSE: the DB read rides runtime/scope.py `_q`/`_lit` (the ONE env-overridable ledger-Postgres
convention — no parallel connection code); the verb normalizes through contracts.scope_grammar (the ONE
registered grammar). A DOWN DB / malformed verb → DENY with a legible note, never a silent allow.
"""
from __future__ import annotations

import json

from runtime.scope import _q, _lit
from contracts.scope_grammar import parse_scope

READ_FAMILY = {"read"}                                  # the verbs a bare member may do (fail-closed floor)
_BREADCRUMB = ("expected schema `container` (0013_container.sql) + the identity model (0017_identity.sql); "
               "fix: apply both migrations + ops/migrate_identity_from_cvi.py")


def _project_key(address: str) -> str | None:
    """The owning project_key for any address (project://<key>[/...] → key). Non-project addresses
    return None (no container to check → DENY-ALL, honest)."""
    if not isinstance(address, str) or not address.startswith("project://"):
        return None
    body = address[len("project://"):]
    key = body.split("/", 1)[0]
    return key or None


def _rows(sql: str) -> list[dict]:
    ok, out = _q(f"select coalesce(json_agg(t), '[]'::json) from ({sql}) t")
    if not ok:
        raise RuntimeError(f"access: container DB unreachable ({out[:200]}) — {_BREADCRUMB}. Fail loud.")
    return json.loads(out.strip() or "[]")


def _principal_row(principal_address: str) -> dict | None:
    r = _rows(f"select principal_id, kind, handle, address, status from container.principal "
              f"where address = {_lit(principal_address)}")
    return r[0] if r else None


def _membership_rows(principal_address: str, project_key: str) -> list[dict]:
    return _rows("select m.role, m.member_type, coalesce(m.scopes,'{}') as scopes "
                 "from container.members m join container.projects p using(project_id) "
                 f"where p.project_key = {_lit(project_key)} and m.principal = {_lit(principal_address)} "
                 "and m.revoked_at is null")


def _acts_for(principal_id: str, container_address: str | None) -> list[dict]:
    """Active acts-for delegations whose GRANTEE is this principal and whose DELEGATOR is an operator,
    matching the container (global NULL, or this exact container_address), within the window."""
    ca = "d.container_address is null" if not container_address else (
        f"(d.container_address is null or d.container_address = {_lit(container_address)})")
    return _rows(
        "select d.max_autonomy, d.scopes, d.status, d.kind, dl.address as delegator, dl.kind as delegator_kind "
        "from container.delegation d join container.principal dl on dl.principal_id = d.delegator "
        f"where d.grantee = {_lit(principal_id)}::uuid and d.status = 'active' "
        f"and dl.kind = 'operator' and {ca} "
        "and d.valid_from <= now() and (d.valid_to is null or d.valid_to > now())")


def _scope_admits(scopes: list[str], verb: str, obj: str | None = None) -> bool:
    """Does any granted scope admit this verb[:object] request? (read is implied by any grant.)
    GRANULARITY LAW (adversary finding, L2): a BROAD grant (bare verb, e.g. 'write') admits the whole
    verb family ('write:leads'); a NARROW grant (verb:object, e.g. 'create:intent') admits ONLY its
    exact object — never the family. A narrow grant must never silently broaden."""
    if verb == "read":
        return True if scopes else False
    for s in scopes or []:
        try:
            g = parse_scope(s)
        except ValueError:
            continue  # malformed stored scope: fail-closed skip (does not admit)
        if g["verb"] != verb:
            continue
        if g["object"] is None:
            return True          # broad grant: admits the verb family
        if obj is not None and g["object"] == obj:
            return True          # narrow grant: exact object match only
    return False


def _decide(principal_address: str, verb: str, address: str) -> dict:
    """THE ONE decision. Returns {principal, verb, address, project, allow, reason, via, ceiling}.
    Fail-closed: anything unresolved → allow=False with a legible reason."""
    base = {"principal": principal_address, "verb": verb, "address": address}
    # normalize the verb through the ONE grammar (fail-closed on a ghost verb — deny, never guess).
    try:
        _req = parse_scope(verb)
        verb, req_obj = _req["verb"], _req["object"]
    except ValueError as e:
        return {**base, "allow": False, "via": "deny", "project": None,
                "reason": f"unparseable verb (scope grammar): {str(e)[:120]}"}
    pk = _project_key(address)
    if pk is None:
        return {**base, "allow": False, "via": "deny", "project": None,
                "reason": "not a container address (project://<key>[/...]) — no container to check; DENY-ALL."}
    base["project"] = pk
    proj = _rows(f"select project_key from container.projects where project_key = {_lit(pk)}")
    if not proj:
        return {**base, "allow": False, "via": "deny",
                "reason": f"no container.projects row for {pk!r} — {_BREADCRUMB}. Fail-closed."}
    pr = _principal_row(principal_address)
    if pr is None:
        return {**base, "allow": False, "via": "deny",
                "reason": f"unknown principal {principal_address!r} (no container.principal row) — fail-closed."}
    # operator: identity IS the boundary.
    if pr["kind"] == "operator" and pr.get("status") == "active":
        return {**base, "allow": True, "via": "operator", "ceiling": "L5",
                "reason": "operator principal — identity IS the boundary (all verbs)."}
    # membership on the container.
    mem = _membership_rows(principal_address, pk)
    for m in mem:
        if m["role"] in ("owner", "keeper", "admin"):
            return {**base, "allow": True, "via": "membership",
                    "reason": f"member role={m['role']} on {pk} — full authority.", "role": m["role"]}
    if mem and verb in READ_FAMILY:
        return {**base, "allow": True, "via": "membership",
                "reason": f"member (role={mem[0]['role']}) — read family.", "role": mem[0]["role"]}
    # acts-for delegation (an agent acting for the operator).
    dels = _acts_for(pr["principal_id"], f"project://{pk}") if pr["kind"] in ("agent", "human", "client") else []
    for d in dels:
        if _scope_admits(d.get("scopes") or [], verb, req_obj):
            return {**base, "allow": True, "via": "delegation", "ceiling": d["max_autonomy"],
                    "reason": (f"acts-for delegation from {d['delegator']} (ceiling {d['max_autonomy']}); "
                               f"verb {verb!r} within delegated scopes — bounded by the guard."),
                    "delegator": d["delegator"]}
    if mem:
        return {**base, "allow": False, "via": "deny",
                "reason": f"member (role={mem[0]['role']}) but {verb!r} beyond the read family and no "
                          f"delegation admits it — fail-closed."}
    return {**base, "allow": False, "via": "deny",
            "reason": f"{principal_address} is not a member of {pk} and holds no acts-for delegation — DENY."}


def may(principal_address: str, verb: str, address: str) -> dict:
    """The gate's question: may this principal do this verb at this address? {allow, reason, via, ceiling}.
    ONE function — the bridge route and the MCP tool both CALL this (never reimplement it)."""
    return _decide(principal_address, verb, address)


def access_of(address: str, *, verbs: list[str] | None = None) -> dict:
    """The UI's read: the roster at this address — each member + the verbs it may (computed via the SAME
    _decide, so what the UI shows == what the gate enforces, law 9). `verbs` defaults to the base five."""
    verbs = verbs or ["read", "write", "execute", "admin", "approve"]
    pk = _project_key(address)
    if pk is None:
        return {"address": address, "project": None, "principals": [],
                "note": "not a container address (project://<key>[/...]) — no roster."}
    # every member of the container + the acts-for agents (grantees of an operator delegation).
    members = _rows("select distinct m.principal, m.member_type, m.role "
                    "from container.members m join container.projects p using(project_id) "
                    f"where p.project_key = {_lit(pk)} and m.revoked_at is null order by m.principal")
    roster = []
    seen = set()
    for m in members:
        pa = m["principal"]
        if pa in seen:
            continue
        seen.add(pa)
        allowed = [v for v in verbs if _decide(pa, v, address)["allow"]]
        roster.append({"principal": pa, "member_type": m.get("member_type"), "role": m.get("role"),
                       "may": allowed})
    return {"address": address, "project": pk, "principals": roster,
            "note": f"{len(roster)} principals; verbs probed = {verbs} (same decision the gate enforces)."}
