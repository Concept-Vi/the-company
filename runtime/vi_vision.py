"""resolve_vi_vision — the factory's address GOOD-PART, built INTO the company spine (CANONICAL copy).

The company resolver (`runtime/cognition.py:resolve_address`, the scheme dispatcher) lazy-imports this and calls
`resolve_vi_vision(addr)`. The factory's Supabase asset library stays the source of TRUTH; the spine resolves
INTO it through this bridge (separate + bridged, never joined). Fail-loud (RAISES on malformed/unknown), the
cc_board.get_item / cc_clone.get_by_address pattern.

OPERATIONAL (not happy-path — Tim 2026-06-17): scope/frame CASCADE (most-specific-wins, not exact-match-only),
honest error paths (store down / malformed rows / missing transport → clear raises, never silent), and the
scope-selection logic is pure + unit-tested without any backend. The one live-only piece is the actual
Supabase/HTTP read, verified once a transport env var is set.

GRAMMAR (THE_FACTORY §8):  vi-vision://<frame>/<type>/<id>
    <frame> = global | project/<id> | user/<id> | session/<id>   (the cascade scope authority)
    <type>  = atom | molecule | organism | template
    <id>    = the component_id (e.g. component.organism.brand-icon; dots, no slashes)

RECORD returned: { component_id, type, name, definition (full JSONB), context, scope }  (a registry row).

TRANSPORT (env-selected, decoupled):
    VI_VISION_SUPABASE_URL + VI_VISION_SUPABASE_KEY (or SUPABASE_URL/SERVICE_KEY) → direct PostgREST read.
    VI_VISION_RESOLVE_URL → a tiny HTTP read endpoint the factory exposes.
"""
from __future__ import annotations

import os
import json
from urllib.request import urlopen, Request
from urllib.parse import urlencode
from urllib.error import URLError, HTTPError

SCOPE_KINDS = ("global", "project", "user", "session")
ASSET_TYPES = ("atom", "molecule", "organism", "template")

# Most-specific-wins cascade rank (THE_FACTORY: the cascade resolves nearest-scope-wins). Higher = more specific.
# Mirrors cascade.js SCOPE_ORDER [global, project, user, session, runtime]; runtime isn't an addressable frame.
_SCOPE_RANK = {"global": 0, "project": 1, "user": 2, "session": 3, "runtime": 4}


class ViVisionAddressError(ValueError):
    """Malformed vi-vision:// address (fail-loud — never a guessed-nearest)."""


class ViVisionNotFound(LookupError):
    """Parsed but no asset resolved at/under the frame (fail-loud — never a silent empty)."""


class ViVisionTransportError(RuntimeError):
    """The store could not be reached / returned garbage (fail-loud — never degrade to empty)."""


def parse_vi_vision_address(addr: str) -> dict:
    """vi-vision://<frame>/<type>/<id> → {frame, scope_kind, scope_id, type, id}. RAISES on anything else.
    The ONE canonical parse (shared-grammar law). <id> is a single segment (a component_id has no slash)."""
    if not isinstance(addr, str) or not addr.startswith("vi-vision://"):
        raise ViVisionAddressError(f"not a vi-vision:// address ({addr!r}). Fail loud.")
    rest = addr[len("vi-vision://"):]
    if not rest:
        raise ViVisionAddressError(f"empty vi-vision body ({addr!r}). Fail loud.")
    parts = rest.split("/")
    head = parts[0]
    if head == "global":
        scope_kind, scope_id, tail = "global", None, parts[1:]
    elif head in ("project", "user", "session"):
        if len(parts) < 2 or not parts[1]:
            raise ViVisionAddressError(f"frame {head!r} needs an id ('{head}/<id>') in {addr!r}. Fail loud.")
        scope_kind, scope_id, tail = head, parts[1], parts[2:]
    else:
        raise ViVisionAddressError(
            f"unknown frame {head!r} in {addr!r} — expected one of {SCOPE_KINDS}. Fail loud.")
    if len(tail) < 2 or not tail[0] or not tail[1]:
        raise ViVisionAddressError(
            f"malformed vi-vision address {addr!r} — expected '<frame>/<type>/<id>'. Fail loud.")
    atype = tail[0]
    if atype not in ASSET_TYPES:
        raise ViVisionAddressError(
            f"unknown asset type {atype!r} in {addr!r} — expected one of {ASSET_TYPES}. Fail loud.")
    aid = "/".join(tail[1:])
    if "/" in aid:
        raise ViVisionAddressError(f"asset id {aid!r} in {addr!r} contains '/'. Fail loud.")
    frame = "global" if scope_kind == "global" else f"{scope_kind}/{scope_id}"
    return {"frame": frame, "scope_kind": scope_kind, "scope_id": scope_id, "type": atype, "id": aid}


def _row_scope_kind(row: dict) -> str:
    """The scope KIND of a registry row, tolerant of how `scope` is encoded ('global' | 'project' |
    'project:p1' | {'kind':'project','id':'p1'}). Operational: don't assume one encoding — derive the kind."""
    sc = row.get("scope")
    if isinstance(sc, dict):
        return str(sc.get("kind") or sc.get("scope") or "global")
    if isinstance(sc, str):
        return sc.split(":", 1)[0].split("/", 1)[0] or "global"
    return "global"


def select_scoped(rows: list, parsed: dict) -> dict | None:
    """Most-specific-wins over candidate rows for one component_id, honoring the requested frame.
    PURE (no I/O) so the cascade is unit-testable. A row is ELIGIBLE if its scope-kind is the requested kind
    OR a less-specific one (the cascade fallback chain, ending at global); the winner is the most-specific
    eligible. Type-mismatched rows are rejected (the address asserts the type). None if nothing eligible."""
    want_rank = _SCOPE_RANK.get(parsed["scope_kind"], 0)
    best, best_rank = None, -1
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        if str(row.get("type")) != parsed["type"]:
            continue  # the address asserts the type; a wrong-type row is not this asset
        rank = _SCOPE_RANK.get(_row_scope_kind(row), 0)
        if rank > want_rank:
            continue  # more specific than asked — not in this frame's chain
        if rank > best_rank:
            best, best_rank = row, rank
    return best


def _candidates_http(component_id: str) -> list:
    url = os.environ.get("VI_VISION_RESOLVE_URL")
    if not url:
        return []
    q = urlencode({"component_id": component_id})
    try:
        with urlopen(f"{url}?{q}", timeout=10) as r:  # noqa: S310 (trusted internal endpoint)
            body = r.read().decode("utf-8")
    except (URLError, HTTPError, TimeoutError) as e:
        raise ViVisionTransportError(f"read endpoint failed for {component_id!r}: {e}. Fail loud.") from e
    if not body:
        return []
    try:
        data = json.loads(body)
    except json.JSONDecodeError as e:
        raise ViVisionTransportError(f"read endpoint returned non-JSON for {component_id!r}: {e}. Fail loud.") from e
    return data if isinstance(data, list) else ([data] if data else [])


def _candidates_supabase(component_id: str) -> list:
    url = os.environ.get("VI_VISION_SUPABASE_URL") or os.environ.get("SUPABASE_URL")
    key = os.environ.get("VI_VISION_SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_KEY")
    if not (url and key):
        return []
    q = urlencode({"component_id": f"eq.{component_id}", "select": "*"})  # ALL scopes → select_scoped cascades
    req = Request(f"{url.rstrip('/')}/rest/v1/visual_dev_component_registry?{q}",
                  headers={"apikey": key, "Authorization": f"Bearer {key}"})
    try:
        with urlopen(req, timeout=10) as r:  # noqa: S310
            body = r.read().decode("utf-8")
    except (URLError, HTTPError, TimeoutError) as e:
        raise ViVisionTransportError(f"Supabase read failed for {component_id!r}: {e}. Fail loud.") from e
    try:
        rows = json.loads(body or "[]")
    except json.JSONDecodeError as e:
        raise ViVisionTransportError(f"Supabase returned non-JSON for {component_id!r}: {e}. Fail loud.") from e
    return rows if isinstance(rows, list) else []


def _transport_configured() -> bool:
    return bool(os.environ.get("VI_VISION_RESOLVE_URL")
                or os.environ.get("VI_VISION_SUPABASE_URL") or os.environ.get("SUPABASE_URL"))


def resolve_vi_vision(addr: str, *, candidates=None) -> dict:
    """Resolve a vi-vision:// address → the factory registry record, scope-cascaded (most-specific-wins).
    RAISES: ViVisionAddressError (malformed) · ViVisionTransportError (no transport / store error) ·
    ViVisionNotFound (parsed + reachable, but no asset at/under the frame). Never a silent empty.
    `candidates` injects a fetcher (component_id)->rows for tests / a direct client."""
    parsed = parse_vi_vision_address(addr)
    if candidates is not None:
        rows = candidates(parsed["id"])
    else:
        if not _transport_configured():
            raise ViVisionTransportError(
                f"no transport configured for {addr!r} — set VI_VISION_SUPABASE_URL/KEY or VI_VISION_RESOLVE_URL. "
                f"Fail loud (never a silent empty).")
        rows = _candidates_http(parsed["id"]) or _candidates_supabase(parsed["id"])
    chosen = select_scoped(rows, parsed)
    if chosen is None:
        raise ViVisionNotFound(
            f"no {parsed['type']} asset {parsed['id']!r} resolved at/under frame {parsed['frame']!r} "
            f"({len(rows or [])} candidate row(s) for the id). Fail loud.")
    return chosen


if __name__ == "__main__":
    # OPERATIONAL self-test — parse, scope cascade, type-guard, error paths (no backend needed).
    g = parse_vi_vision_address("vi-vision://global/organism/component.organism.brand-icon")
    assert g["scope_kind"] == "global" and g["type"] == "organism", g
    p = parse_vi_vision_address("vi-vision://project/p1/molecule/component.molecule.chip")
    assert p["frame"] == "project/p1", p
    for bad in ("palette://x", "vi-vision://", "vi-vision://global/widget/x", "vi-vision://nope/organism/x",
                "vi-vision://project//organism/x", "vi-vision://global/organism"):
        try:
            parse_vi_vision_address(bad); raise SystemExit(f"FAIL: {bad!r} did not raise")
        except ViVisionAddressError:
            pass
    # scope cascade: project frame, both a project row and a global row exist → project wins (most-specific).
    rows = [
        {"component_id": "x", "type": "organism", "name": "global-V", "scope": "global", "definition": {}, "context": {}},
        {"component_id": "x", "type": "organism", "name": "proj-V", "scope": "project:p1", "definition": {}, "context": {}},
    ]
    win = resolve_vi_vision("vi-vision://project/p1/organism/x", candidates=lambda _id: rows)
    assert win["name"] == "proj-V", win
    # global frame asks → the project row is MORE specific than asked → excluded → global wins.
    win2 = resolve_vi_vision("vi-vision://global/organism/x", candidates=lambda _id: rows)
    assert win2["name"] == "global-V", win2
    # type-guard: address says atom, only an organism row exists → NotFound (not a wrong-type match).
    try:
        resolve_vi_vision("vi-vision://global/atom/x", candidates=lambda _id: rows); raise SystemExit("FAIL: type-guard")
    except ViVisionNotFound:
        pass
    # unknown id → NotFound; transport error propagates as ViVisionTransportError.
    try:
        resolve_vi_vision("vi-vision://global/atom/ghost", candidates=lambda _id: []); raise SystemExit("FAIL: unknown")
    except ViVisionNotFound:
        pass
    def _boom(_id):
        raise ViVisionTransportError("store down")
    try:
        resolve_vi_vision("vi-vision://global/organism/x", candidates=_boom); raise SystemExit("FAIL: transport")
    except ViVisionTransportError:
        pass
    print("resolve_vi_vision OPERATIONAL self-test: ALL PASS (parse · scope-cascade · type-guard · not-found · transport-error)")
