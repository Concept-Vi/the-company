"""mcp_face/tools/introspection.py — the CAPABILITY REGISTRY tool (Mirror-Registry System, LANE-PROJECTION).

One consolidated read tool (`capability`) projecting from the CapabilityRegistry singleton
(introspection/registry.py). File-drop contract: this module is discovered by mcp_face/server.py's
pkgutil.iter_modules loop and called as `.register(mcp, SUITE)` with no server.py edit (S5 / Build
Plan LANE-PROJECTION). 

MCP DESIGN PRINCIPLE (from mcp_face/AGENTS.md): one parameterised tool with `op` selector — NEVER
a flat tool per capability or per operation. A new need is a new `op`, never a new tool.

CONTRACT-FORMAT §9.2: export `OPS` (the closed op-set constant) so the contract corpus's machine
inventory can extract it. The drift test (when written in LANE-REFRESH) will fail loud if the
dispatcher and OPS diverge.

## What this projects

The CapabilityRegistry is the SINGLE source — all ops read the same in-memory snapshot that
capability_registry() returns. STUB-POPULATED at unit-verify time (C-PROJ-1 / C-PROJ-2 are
🟡 lead-verify-queued because a live Suite.capability_registry requires a live binary discovery).
The tool is wired + importable; the live surface is queued for the lead to run.

## Ops

  op="list"     — the full registry snapshot (counts by kind/posture + entry ids). Optional
                  filters: kind (one EntryKind value), posture (one posture value), platform_id.
  op="get"      — one entry by its id (cap://<kind>/<name> or bare <kind>/<name>). Required:
                  `id` OR (`kind` + `name`).
  op="search"   — substring match over id/name/description. Required: `query`.
  op="describe" — the full snapshot + per-kind breakdowns (the registry-is-truth health view).
  op="snapshot" — the raw engine projection dict (counts + postures + total + the entry list).

## Authentication to the registry (the singleton seam)

The cap:// resolver and this tool BOTH reach the registry through capability_registry() (the
module-level singleton, introspection/registry.py). capability_registry() RAISES fail-loud if
Suite.__init__ has not called set_capability_registry() yet. That wiring is LANE-CAP-WIRE — built,
but needs a running Suite to exercise (🟡 lead-verify-queued). A stale / unbuilt suite surfaces
a TEACHING error (not an AttributeError), naming the missing lane.
"""
from __future__ import annotations

from typing import Literal, Optional

# EXPORTED closed op-set (CONTRACT-FORMAT §9.2). The mcp_face/AGENTS.md constitution states:
# consolidated tool modules EXPORT a closed OPS constant so the contract corpus can extract it.
OPS = ("list", "get", "search", "describe", "snapshot")


def _cap_registry(suite):
    """Reach the CapabilityRegistry via the module-level singleton, OR (as a degraded fallback)
    via suite.capability_registry if it is a live attribute. Fails TEACHING-loud if neither is
    available — never an AttributeError posing as an internal bug, never a silent empty result.

    The singleton path (introspection.registry.capability_registry()) is the PRIMARY path.
    The suite attribute path is a secondary convenience for callers that have already built
    the registry and attached it. Both paths fail loud on missing / unset."""
    # Primary: the module-level singleton (the cap:// resolver uses the same path)
    try:
        from introspection.registry import capability_registry as _cr
        return _cr()
    except RuntimeError:
        pass   # singleton not set — try the suite attribute below
    except ImportError:
        pass   # introspection package not importable (should not happen in a well-assembled suite)

    # Degraded fallback: suite.capability_registry (set by Suite.__init__ in LANE-CAP-WIRE)
    reg = getattr(suite, "capability_registry", None)
    if reg is not None:
        return reg

    raise ValueError(
        "capability_registry is not available — it requires the Mirror-Registry LANE-CAP-WIRE to be "
        "active (Suite.__init__ must call set_capability_registry() once after discovering the "
        "CapabilityRegistry). This is a wiring issue, not a data issue. The registry is discovered "
        "from the live binary at Suite init; a stub-populated registry is also accepted for unit "
        "verification. Use capability(op='describe') to see the registry's health once wired. "
        "Fail loud — never a silent empty result (registry-is-truth / no-silent-failures law).")


def _entry_id(kind: str, name: str, id_: str) -> str:
    """Resolve an entry id from either a bare `id` string or a (kind, name) pair.
    Grammar: id = f'{kind}/{name}' with name INCLUDING the '--' prefix for flags (F-FIX-14).
    cap://flag/--debug → id='flag/--debug'; bare 'flag/--debug' is also accepted.
    Strips a 'cap://' prefix if present (the caller may pass the full address form)."""
    if id_:
        s = id_.strip()
        if s.startswith("cap://"):
            s = s[len("cap://"):]
        return s
    if kind and name:
        # Normalise: flags must carry the '--' prefix; other kinds use the bare name.
        n = name.strip()
        return f"{kind.strip()}/{n}"
    raise ValueError(
        "capability(op='get') requires EITHER `id` (e.g. 'flag/--debug' or 'cap://flag/--debug') "
        "OR both `kind` and `name` (e.g. kind='flag', name='--debug'). Neither was supplied.")


def register(mcp, suite):
    """Register the `capability` tool on the MCP server. Called by mcp_face/server.py's pkgutil
    discovery loop — no server.py edit required (S5 / the file-drop contract)."""

    @mcp.tool()
    def capability(
        op: Literal["list", "get", "search", "describe", "snapshot"],
        id: str = "",
        kind: str = "",
        name: str = "",
        posture: str = "",
        platform_id: str = "",
        query: str = "",
        limit: int = 200,
    ) -> dict:
        """READ the CAPABILITY REGISTRY — what the live external platform (Claude Code, instance #1)
        exposes: its flags, slash-commands, subcommands, built-in tools, MCP tools, settings, hooks,
        SDK events, and permission strings — each classified by posture (locked/hazard/consent/safe/
        unmatched) via the five closed rules. The registry is BINARY-DISCOVERED (from the live
        binary's self-report), never hand-authored. registry-is-truth: the binary IS the registry;
        this read is a projection of it. Pick `op`:

          op="list"     — every registered entry (ids + kind + posture + name + description).
                          Optional filters: `kind` (one EntryKind: flag/slash_command/subcommand/
                          tool/mcp_tool/setting/permission/hook_event/sdk_event/enum_value),
                          `posture` (locked/hazard/consent/safe/unmatched), `platform_id`.
                          `limit` caps the returned entries (default 200).
          op="get"      — ONE entry by its id. Supply EITHER `id` (e.g. 'flag/--debug' or the
                          address form 'cap://flag/--debug') OR both `kind` + `name`. A missing id
                          RAISES fail-loud with the registry-is-truth teaching (never a silent None).
          op="search"   — substring match over id/name/description. `query` required. Returns the
                          matching entries (up to `limit`). Searches only `searchable` entries
                          (expose-not-gate default: all entries are searchable unless restricted).
          op="describe" — the HEALTH VIEW: counts by kind + by posture + platform metadata + a
                          per-kind entry-id listing. Use this to inspect the registry state and
                          confirm what was discovered. No filters.
          op="snapshot" — the raw engine-projection dict (counts/postures/total/entries list) from
                          the in-memory registry. The same projection the bridge route serves.

        The registry is populated at Suite init by CapabilityRegistry().discover() (LEAD-only live
        binary spawn) or via a stub for unit verification. `capability(op='describe')` is the
        quickest health-check — if the registry is empty or unset, it tells you why (teaching error,
        never a silent empty). cap:// addresses resolve to entries via the cognition resolver (same
        registry: `resolve_address('cap://flag/--debug')` returns the CapabilityEntry). To ADD a
        capability to the registry, update the live binary (the binary IS the registry)."""

        if op not in OPS:
            raise ValueError(
                f"capability: unknown op={op!r}. Valid ops: {list(OPS)} — list=the full entry set "
                f"(filtered) · get=one entry by id (requires `id` or `kind`+`name`) · search=substring "
                f"match (requires `query`) · describe=the registry health view · snapshot=raw projection. "
                f"The registry is binary-discovered (registry-is-truth); to see what's available use "
                f"op='describe'.")

        # Reach the registry — RAISES teaching-loud if not yet wired (never silent)
        reg = _cap_registry(suite)

        # ── op="describe" — the registry health view (no entry listing needed) ────────────────
        if op == "describe":
            snap = reg.snapshot()
            kinds = snap.get("counts", {})
            by_kind: dict[str, list[str]] = {}
            for entry_id in reg:
                e = reg[entry_id]
                by_kind.setdefault(e.kind, []).append(e.id)
            return {
                "op": op,
                "platform_id": snap.get("platform_id", ""),
                "version": snap.get("version", ""),
                "total": snap.get("total", 0),
                "counts_by_kind": kinds,
                "counts_by_posture": snap.get("postures", {}),
                "by_kind": {k: sorted(ids) for k, ids in sorted(by_kind.items())},
                "note": (
                    "The registry is binary-discovered — a count of 0 means the live binary discovery "
                    "has not run yet in this process (LANE-CAP-WIRE wires Suite.__init__ to call "
                    "set_capability_registry after discovering; 🟡 lead-verify-queued until the lead runs "
                    "a live Suite). A stub-populated registry is accepted for unit verification."
                ) if snap.get("total", 0) == 0 else "",
            }

        # ── op="snapshot" — raw engine projection ────────────────────────────────────────────
        if op == "snapshot":
            snap = reg.snapshot()
            return {"op": op, **snap}

        # ── op="get" — one entry by id ────────────────────────────────────────────────────────
        if op == "get":
            eid = _entry_id(kind, name, id)
            entry = reg.get(eid)
            if entry is None:
                known = sorted(list(reg)[:20])
                raise ValueError(
                    f"capability(op='get'): unknown id {eid!r} — not in the registry. "
                    f"registry-is-truth: if this capability exists on the platform, re-run discovery "
                    f"(the refresh flow) so it appears. First 20 known ids: {known}. "
                    f"Use capability(op='search', query=…) to find nearby entries.")
            return {"op": op, "id": eid, "entry": entry.model_dump()}

        # ── op="search" — substring match ────────────────────────────────────────────────────
        if op == "search":
            if not (query or "").strip():
                raise ValueError(
                    "capability(op='search') requires `query` — the substring to match over "
                    "id/name/description. Use op='list' (with optional kind/posture filters) to "
                    "browse without a search term.")
            matches = reg.search(query.strip())
            if platform_id:
                matches = [e for e in matches if e.platform_id == platform_id]
            if kind:
                matches = [e for e in matches if e.kind == kind]
            if posture:
                matches = [e for e in matches if e.posture == posture]
            matches = matches[:limit]
            return {
                "op": op,
                "query": query.strip(),
                "total": len(matches),
                "entries": [e.model_dump() for e in matches],
            }

        # ── op="list" — the entry set with optional filters ──────────────────────────────────
        # op == "list"
        entries = list(reg.entries.values())
        if kind:
            entries = [e for e in entries if e.kind == kind]
        if posture:
            entries = [e for e in entries if e.posture == posture]
        if platform_id:
            entries = [e for e in entries if e.platform_id == platform_id]
        total_matched = len(entries)
        entries = entries[:limit]
        rows = [
            {"id": e.id, "kind": e.kind, "name": e.name, "posture": e.posture,
             "posture_rule": e.posture_rule, "description": e.description,
             "platform_id": e.platform_id, "status": e.status}
            for e in entries
        ]
        return {
            "op": op,
            "total_matched": total_matched,
            "returned": len(rows),
            "limit": limit,
            "filters": {k: v for k, v in [("kind", kind), ("posture", posture),
                                            ("platform_id", platform_id)] if v},
            "entries": rows,
            "note": (f"showing {len(rows)} of {total_matched}; increase `limit` to see more."
                     if total_matched > limit else ""),
        }

    return (capability,)
