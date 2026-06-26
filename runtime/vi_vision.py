"""vi_vision — the factory's address GOOD-PART, built INTO the company spine (CANONICAL copy).

The company resolver (`runtime/cognition.py:resolve_address`, the scheme dispatcher) lazy-imports this:
  read  → `resolve_vi_vision(addr)`                  (the vi-vision:// READ branch)
  write → `write_vi_vision(addr, definition, …)`     (the generate/keystone WRITE step's factory target)
The factory's Supabase asset library stays the source of TRUTH; the spine resolves/writes INTO it through this
bridge (separate + bridged, never joined). Fail-loud (RAISES; never a silent empty), the cc_board/cc_clone pattern.

SECURE + PRIVATE (Tim 2026-06-17): authenticates as a DEDICATED COMPANY SERVICE-ACCOUNT principal (option B —
session/refresh flow, revocable via normal auth, no JWT-signing-secret). NOT anon (anon = read-global-only, no
write), NOT service_role (RLS-bypass hazard). The EXISTING RLS does the enforcement, no migration:
  read  `vd_component_read`  = (scope='global' OR user_id=auth.uid())  → global library + the company's own rows.
  write `vd_component_write` = (user_id=auth.uid())                    → the company writes its OWN rows.
So the principal reads the shared library + its own assets, writes its own; other users' private rows stay
private. WRITE-SCOPING: the address FRAME = the write scope (global→shared library; project→private project).

OPERATIONAL (not happy-path): scope/frame CASCADE (most-specific-wins), select-then-write (robust vs the
COALESCE-indexed table, mirrors component-store.js), honest error paths, token cache+refresh; pure logic
unit-tested without any backend.

GRAMMAR (THE_FACTORY §8):  vi-vision://<frame>/<type>/<id>
    <frame> = global | project/<id> | user/<id> | session/<id>   <type> = atom|molecule|organism|template
    <id> = component_id (dots, no slashes)

ENV (the lead provisions; never in channel):
    VI_VISION_SUPABASE_URL (or SUPABASE_URL)            — project URL
    VI_VISION_ANON_KEY (or SUPABASE_ANON_KEY)           — the apikey (PostgREST requires it; read-only by itself)
    service-account cred (option B), one of:
      VI_VISION_SA_EMAIL + VI_VISION_SA_PASSWORD        — grant_type=password (restart-robust; recommended)
      VI_VISION_SA_REFRESH_TOKEN                        — grant_type=refresh_token
    VI_VISION_RESOLVE_URL (optional)                    — a read-only HTTP endpoint (no write)
"""
from __future__ import annotations

import os
import json
import time
import base64
from urllib.request import urlopen, Request
from urllib.parse import urlencode
from urllib.error import URLError, HTTPError

SCOPE_KINDS = ("global", "project", "user", "session")
ASSET_TYPES = ("atom", "molecule", "organism", "template")
_SCOPE_RANK = {"global": 0, "project": 1, "user": 2, "session": 3, "runtime": 4}
_REGISTRY = "visual_dev_component_registry"


class ViVisionAddressError(ValueError):
    """Malformed vi-vision:// address (fail-loud)."""


class ViVisionNotFound(LookupError):
    """Parsed but no asset resolved at/under the frame (fail-loud — never a silent empty)."""


class ViVisionTransportError(RuntimeError):
    """Store unreachable / returned garbage (fail-loud — never degrade to empty)."""


class ViVisionAuthError(RuntimeError):
    """The service-account principal could not authenticate (fail-loud; write needs auth)."""


def parse_vi_vision_address(addr: str) -> dict:
    """vi-vision://<frame>/<type>/<id> → {frame, scope_kind, scope_id, type, id}. RAISES on anything else."""
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
        raise ViVisionAddressError(f"unknown frame {head!r} in {addr!r} — expected {SCOPE_KINDS}. Fail loud.")
    if len(tail) < 2 or not tail[0] or not tail[1]:
        raise ViVisionAddressError(f"malformed {addr!r} — expected '<frame>/<type>/<id>'. Fail loud.")
    atype = tail[0]
    if atype not in ASSET_TYPES:
        raise ViVisionAddressError(f"unknown asset type {atype!r} in {addr!r} — expected {ASSET_TYPES}. Fail loud.")
    aid = "/".join(tail[1:])
    if "/" in aid:
        raise ViVisionAddressError(f"asset id {aid!r} in {addr!r} contains '/'. Fail loud.")
    frame = "global" if scope_kind == "global" else f"{scope_kind}/{scope_id}"
    return {"frame": frame, "scope_kind": scope_kind, "scope_id": scope_id, "type": atype, "id": aid}


def _row_scope_kind(row: dict) -> str:
    sc = row.get("scope")
    if isinstance(sc, dict):
        return str(sc.get("kind") or sc.get("scope") or "global")
    if isinstance(sc, str):
        return sc.split(":", 1)[0].split("/", 1)[0] or "global"
    return "global"


def select_scoped(rows: list, parsed: dict) -> dict | None:
    """Most-specific-wins over candidate rows (PURE, unit-testable). Type-guarded; never returns a more-specific
    row than the frame asked; global is the base of the fallback chain."""
    want_rank = _SCOPE_RANK.get(parsed["scope_kind"], 0)
    best, best_rank = None, -1
    for row in rows or []:
        if not isinstance(row, dict) or str(row.get("type")) != parsed["type"]:
            continue
        rank = _SCOPE_RANK.get(_row_scope_kind(row), 0)
        if rank > want_rank:
            continue
        if rank > best_rank:
            best, best_rank = row, rank
    return best


# ── service-account auth (option B): cache the access token, refresh from password/refresh_token ───────────
_TOKEN = {"access": None, "exp": 0.0}


def _b64url_json(segment: str) -> dict:
    pad = "=" * (-len(segment) % 4)
    return json.loads(base64.urlsafe_b64decode(segment + pad).decode("utf-8"))


def jwt_sub(access_token: str) -> str:
    """The principal's uid = the access token's `sub` claim (decode-only; it's our own token, no verify)."""
    try:
        return str(_b64url_json(access_token.split(".")[1])["sub"])
    except Exception as e:  # noqa: BLE001
        raise ViVisionAuthError(f"could not read sub from the access token: {e}. Fail loud.") from e


def _supabase_url() -> str | None:
    return os.environ.get("VI_VISION_SUPABASE_URL") or os.environ.get("SUPABASE_URL")


def _anon_key() -> str | None:
    return os.environ.get("VI_VISION_ANON_KEY") or os.environ.get("SUPABASE_ANON_KEY")


def _post_json(url: str, headers: dict, payload) -> tuple[int, str]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = Request(url, data=body, headers={**headers, "Content-Type": "application/json"},
                  method="POST")
    try:
        with urlopen(req, timeout=10) as r:  # noqa: S310
            return r.status, r.read().decode("utf-8")
    except HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except (URLError, TimeoutError) as e:
        raise ViVisionTransportError(f"POST {url} failed: {e}. Fail loud.") from e


def _access_token(*, force=False) -> str:
    """Get a fresh access token for the SA principal (cached; refreshed near expiry). RAISES ViVisionAuthError."""
    now = time.time()
    if not force and _TOKEN["access"] and _TOKEN["exp"] - 30 > now:
        return _TOKEN["access"]
    url, anon = _supabase_url(), _anon_key()
    if not (url and anon):
        raise ViVisionAuthError("SUPABASE_URL + ANON key required to authenticate. Fail loud.")
    email = os.environ.get("VI_VISION_SA_EMAIL")
    pw = os.environ.get("VI_VISION_SA_PASSWORD")
    refresh = os.environ.get("VI_VISION_SA_REFRESH_TOKEN")
    if email and pw:
        grant, payload = "password", {"email": email, "password": pw}
    elif refresh:
        grant, payload = "refresh_token", {"refresh_token": refresh}
    else:
        raise ViVisionAuthError(
            "no service-account cred — set VI_VISION_SA_EMAIL+PASSWORD or VI_VISION_SA_REFRESH_TOKEN. Fail loud.")
    status, body = _post_json(f"{url.rstrip('/')}/auth/v1/token?grant_type={grant}", {"apikey": anon}, payload)
    if status >= 300:
        raise ViVisionAuthError(f"SA auth ({grant}) failed [{status}]: {body[:200]}. Fail loud.")
    try:
        tok = json.loads(body)
    except json.JSONDecodeError as e:
        raise ViVisionAuthError(f"SA auth returned non-JSON: {e}. Fail loud.") from e
    acc = tok.get("access_token")
    if not acc:
        raise ViVisionAuthError(f"SA auth returned no access_token: {body[:200]}. Fail loud.")
    _TOKEN["access"] = acc
    _TOKEN["exp"] = now + float(tok.get("expires_in", 3600))
    return acc


def _read_headers() -> dict:
    """READ headers — anon ONLY (read-only). Reads the GLOBAL shared library per RLS (incl. generated assets
    written to global). The read NEVER uses the write-capable SA principal — least-privilege: reading never
    needs write (fork's split, 2026-06-17). apikey + Bearer = the anon key."""
    anon = _anon_key()
    if not anon:
        raise ViVisionTransportError("ANON key required (apikey). Fail loud.")
    return {"apikey": anon, "Authorization": f"Bearer {anon}"}


def _write_headers() -> dict:
    """WRITE headers — the WRITE-CAPABLE SA principal ONLY (apikey=anon, Bearer=SA access token). RAISES if no
    SA cred. The write path is the SOLE user of the SA principal; it is GATED (the keystone's build-this step),
    never a brain-callable MCP tool (the brain's company server carries no consequential verbs)."""
    anon = _anon_key()
    if not anon:
        raise ViVisionTransportError("ANON key required (apikey). Fail loud.")
    has_sa = bool((os.environ.get("VI_VISION_SA_EMAIL") and os.environ.get("VI_VISION_SA_PASSWORD"))
                  or os.environ.get("VI_VISION_SA_REFRESH_TOKEN"))
    if not has_sa:
        raise ViVisionAuthError("write requires the service-account principal — no SA cred set. Fail loud.")
    return {"apikey": anon, "Authorization": f"Bearer {_access_token()}"}


def _candidates_http(component_id: str) -> list:
    url = os.environ.get("VI_VISION_RESOLVE_URL")
    if not url:
        return []
    q = urlencode({"component_id": component_id})
    try:
        with urlopen(f"{url}?{q}", timeout=10) as r:  # noqa: S310
            body = r.read().decode("utf-8")
    except (URLError, HTTPError, TimeoutError) as e:
        raise ViVisionTransportError(f"read endpoint failed for {component_id!r}: {e}. Fail loud.") from e
    if not body:
        return []
    try:
        data = json.loads(body)
    except json.JSONDecodeError as e:
        raise ViVisionTransportError(f"read endpoint non-JSON for {component_id!r}: {e}. Fail loud.") from e
    return data if isinstance(data, list) else ([data] if data else [])


def _candidates_supabase(component_id: str) -> list:
    url = _supabase_url()
    if not (url and _anon_key()):
        return []
    q = urlencode({"component_id": f"eq.{component_id}", "select": "*"})
    req = Request(f"{url.rstrip('/')}/rest/v1/{_REGISTRY}?{q}", headers=_read_headers())
    try:
        with urlopen(req, timeout=10) as r:  # noqa: S310
            body = r.read().decode("utf-8")
    except (URLError, HTTPError, TimeoutError) as e:
        raise ViVisionTransportError(f"Supabase read failed for {component_id!r}: {e}. Fail loud.") from e
    try:
        rows = json.loads(body or "[]")
    except json.JSONDecodeError as e:
        raise ViVisionTransportError(f"Supabase non-JSON for {component_id!r}: {e}. Fail loud.") from e
    return rows if isinstance(rows, list) else []


def _transport_configured() -> bool:
    return bool(os.environ.get("VI_VISION_RESOLVE_URL") or _supabase_url())


def resolve_vi_vision(addr: str, *, candidates=None) -> dict:
    """READ: vi-vision:// → the factory registry record, scope-cascaded. RAISES ViVisionAddressError /
    ViVisionTransportError / ViVisionNotFound. Reads ANON (read-only; the global shared library) — NEVER the
    write-capable SA principal (fork's read/write split: reading never needs write). `candidates` injects a
    fetcher for tests."""
    parsed = parse_vi_vision_address(addr)
    if candidates is not None:
        rows = candidates(parsed["id"])
    else:
        if not _transport_configured():
            raise ViVisionTransportError(f"no transport for {addr!r} — set VI_VISION_SUPABASE_URL. Fail loud.")
        rows = _candidates_http(parsed["id"]) or _candidates_supabase(parsed["id"])
    chosen = select_scoped(rows, parsed)
    if chosen is None:
        raise ViVisionNotFound(
            f"no {parsed['type']} {parsed['id']!r} at/under frame {parsed['frame']!r} "
            f"({len(rows or [])} candidate(s)). Fail loud.")
    return chosen


def build_write_row(addr: str, definition: dict, *, user_id: str, name=None, tags=None, context=None) -> dict:
    """PURE: the registry row a write produces from an address (scope = the frame; owner = the principal uid).
    Unit-testable without a backend. RAISES ViVisionAddressError on a bad address."""
    parsed = parse_vi_vision_address(addr)
    if not isinstance(definition, dict) or not definition:
        raise ViVisionAddressError(f"write needs a non-empty definition dict for {addr!r}. Fail loud.")
    row = {
        "component_id": parsed["id"],
        "type": parsed["type"],
        "name": name or definition.get("name") or parsed["id"],
        "definition": definition,
        "context": context or definition.get("context") or {},
        "scope": parsed["scope_kind"],            # the frame IS the write scope
        "user_id": user_id,                        # RLS WITH CHECK user_id=auth.uid()
        "tags": tags or definition.get("tags") or [],
    }
    if parsed["scope_kind"] == "project":
        row["project_id"] = parsed["scope_id"]
    return row


def write_vi_vision(addr: str, definition: dict, *, name=None, tags=None, context=None, poster=None) -> dict:
    """WRITE (the generate/keystone step's factory target): UPSERT a generated asset as the SA principal,
    scope = the address frame. Select-then-write (UPDATE if the row exists for this component_id+scope, else
    INSERT) — robust vs the COALESCE-indexed table, mirrors component-store.js. RLS enforces user_id=auth.uid().
    RAISES ViVisionAddressError / ViVisionAuthError / ViVisionTransportError. `poster(row, parsed)` injects the
    writer for tests; default does the authenticated PostgREST write."""
    parsed = parse_vi_vision_address(addr)
    if poster is not None:
        uid = "test-uid"
        row = build_write_row(addr, definition, user_id=uid, name=name, tags=tags, context=context)
        return poster(row, parsed)
    headers = _write_headers()                                  # SA principal ONLY; RAISES if no SA cred
    uid = jwt_sub(_access_token())
    row = build_write_row(addr, definition, user_id=uid, name=name, tags=tags, context=context)
    url = _supabase_url().rstrip("/")
    # select-then-write: find an existing row for (component_id, scope) owned by the principal.
    sel = urlencode({"component_id": f"eq.{parsed['id']}", "scope": f"eq.{parsed['scope_kind']}",
                     "user_id": f"eq.{uid}", "select": "id", "limit": "1"})
    existing = _candidates_http(parsed["id"]) if False else None  # (read endpoint is read-only; use REST)
    req = Request(f"{url}/rest/v1/{_REGISTRY}?{sel}", headers=headers)
    try:
        with urlopen(req, timeout=10) as r:  # noqa: S310
            found = json.loads(r.read().decode("utf-8") or "[]")
    except (URLError, HTTPError, TimeoutError) as e:
        raise ViVisionTransportError(f"write pre-select failed for {addr!r}: {e}. Fail loud.") from e
    if found:
        # UPDATE the existing row (PATCH); bump version.
        row["version"] = (found[0].get("version", 1) or 1) + 1 if isinstance(found[0], dict) else 1
        patch = {k: v for k, v in row.items() if k not in ("user_id",)}  # never re-assert ownership on update
        q = urlencode({"id": f"eq.{found[0]['id']}"})
        status, body = _patch_json(f"{url}/rest/v1/{_REGISTRY}?{q}", headers, patch)
    else:
        status, body = _post_json(f"{url}/rest/v1/{_REGISTRY}",
                                  {**headers, "Prefer": "return=representation"}, row)
    if status >= 300:
        raise ViVisionTransportError(f"write {addr!r} failed [{status}]: {body[:200]}. Fail loud.")
    try:
        out = json.loads(body or "[]")
    except json.JSONDecodeError:
        out = []
    return (out[0] if isinstance(out, list) and out else (out if isinstance(out, dict) else row))


def _patch_json(url: str, headers: dict, payload) -> tuple[int, str]:
    body = json.dumps(payload).encode("utf-8")
    req = Request(url, data=body, headers={**headers, "Content-Type": "application/json",
                                           "Prefer": "return=representation"}, method="PATCH")
    try:
        with urlopen(req, timeout=10) as r:  # noqa: S310
            return r.status, r.read().decode("utf-8")
    except HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except (URLError, TimeoutError) as e:
        raise ViVisionTransportError(f"PATCH {url} failed: {e}. Fail loud.") from e


def vi_vision_catalog(frame: str = "global", *, fetch=None) -> list:
    """READ-ONLY library PALETTE for the brain's CONTEXT-enrich (runs in the BRIDGE, anon, NEVER in the brain).
    The available pieces at `frame` (default 'global' = the shared library the brain composes from) →
    [{component_id, type, name, tags, desc}]. fork renders name+type (NOT raw ids) + caps to a summary.
    RAISES ViVisionTransportError on a store error (fork GUARDS it → degrade-clean, territory_prose never-raise);
    [] on empty. `fetch(frame)->rows` injects for tests. (frame='global' for the compose-palette; a narrower
    frame would need the read-only principal — out of scope for the anon catalog.)"""
    kind = frame.split("/", 1)[0]
    if kind not in SCOPE_KINDS:
        raise ViVisionAddressError(f"vi_vision_catalog: unknown frame {frame!r} (expected {SCOPE_KINDS}). Fail loud.")
    if fetch is not None:
        rows = fetch(frame)
    else:
        url = _supabase_url()
        if not (url and _anon_key()):
            raise ViVisionTransportError("vi_vision_catalog: SUPABASE_URL + ANON key required. Fail loud.")
        q = urlencode({"scope": f"eq.{kind}", "select": "component_id,type,name,tags,context"})
        req = Request(f"{url.rstrip('/')}/rest/v1/{_REGISTRY}?{q}", headers=_read_headers())
        try:
            with urlopen(req, timeout=10) as r:  # noqa: S310
                body = r.read().decode("utf-8")
        except (URLError, HTTPError, TimeoutError) as e:
            raise ViVisionTransportError(f"vi_vision_catalog read failed ({frame!r}): {e}. Fail loud.") from e
        try:
            rows = json.loads(body or "[]")
        except json.JSONDecodeError as e:
            raise ViVisionTransportError(f"vi_vision_catalog non-JSON ({frame!r}): {e}. Fail loud.") from e
    out = []
    for row in (rows if isinstance(rows, list) else []):
        if not isinstance(row, dict):
            continue
        ctx = row.get("context") if isinstance(row.get("context"), dict) else {}
        out.append({
            "component_id": row.get("component_id"),
            "type": row.get("type"),
            "name": row.get("name") or row.get("component_id"),
            "tags": row.get("tags") or [],
            "desc": (str(ctx.get("description") or ""))[:120],
        })
    return out


if __name__ == "__main__":
    # OPERATIONAL self-test — parse · scope-cascade · type-guard · errors · jwt-sub · write-row · write-auth-gate · catalog.
    g = parse_vi_vision_address("vi-vision://global/organism/component.organism.brand-icon")
    assert g["scope_kind"] == "global" and g["type"] == "organism", g
    assert parse_vi_vision_address("vi-vision://project/p1/molecule/component.molecule.chip")["frame"] == "project/p1"
    for bad in ("palette://x", "vi-vision://", "vi-vision://global/widget/x", "vi-vision://nope/organism/x",
                "vi-vision://project//organism/x", "vi-vision://global/organism"):
        try:
            parse_vi_vision_address(bad); raise SystemExit(f"FAIL parse: {bad!r}")
        except ViVisionAddressError:
            pass
    rows = [{"component_id": "x", "type": "organism", "name": "global-V", "scope": "global", "definition": {}},
            {"component_id": "x", "type": "organism", "name": "proj-V", "scope": "project:p1", "definition": {}}]
    assert resolve_vi_vision("vi-vision://project/p1/organism/x", candidates=lambda _i: rows)["name"] == "proj-V"
    assert resolve_vi_vision("vi-vision://global/organism/x", candidates=lambda _i: rows)["name"] == "global-V"
    for addr, exc in (("vi-vision://global/atom/x", ViVisionNotFound),
                      ("vi-vision://global/atom/ghost", ViVisionNotFound)):
        try:
            resolve_vi_vision(addr, candidates=lambda _i: rows if addr.endswith('/x') else []); raise SystemExit("FAIL nf")
        except ViVisionNotFound:
            pass
    # jwt_sub decode (a hand-made unsigned token payload {"sub":"company-123"}).
    payload = base64.urlsafe_b64encode(json.dumps({"sub": "company-123"}).encode()).decode().rstrip("=")
    assert jwt_sub(f"h.{payload}.s") == "company-123"
    # write-row construction: scope = frame, user_id = principal, project_id on project frame.
    r1 = build_write_row("vi-vision://global/atom/component.atom.chip", {"type": "atom", "name": "Chip"},
                         user_id="company-123")
    assert r1["scope"] == "global" and r1["user_id"] == "company-123" and r1["component_id"] == "component.atom.chip"
    r2 = build_write_row("vi-vision://project/p9/organism/component.organism.card", {"type": "organism"},
                         user_id="company-123")
    assert r2["scope"] == "project" and r2["project_id"] == "p9", r2
    # write via injected poster (offline): echoes the built row.
    w = write_vi_vision("vi-vision://global/molecule/component.molecule.m1", {"type": "molecule"},
                        poster=lambda row, parsed: {**row, "_posted": True})
    assert w["_posted"] and w["scope"] == "global" and w["type"] == "molecule", w
    # write without SA cred (no env) → auth gate raises.
    for k in ("VI_VISION_SA_EMAIL", "VI_VISION_SA_PASSWORD", "VI_VISION_SA_REFRESH_TOKEN"):
        os.environ.pop(k, None)
    os.environ["VI_VISION_SUPABASE_URL"] = "https://x.supabase.co"; os.environ["VI_VISION_ANON_KEY"] = "anon"
    try:
        write_vi_vision("vi-vision://global/atom/component.atom.z", {"type": "atom"}); raise SystemExit("FAIL auth-gate")
    except ViVisionAuthError:
        pass
    # catalog: read-only library palette (offline via injected fetch) → name+type+desc shape.
    cat = vi_vision_catalog("global", fetch=lambda _f: [
        {"component_id": "component.organism.brand-icon", "type": "organism", "name": "The V",
         "tags": ["brand"], "context": {"description": "The Vi brand mark."}},
        {"component_id": "component.atom.text", "type": "atom", "name": "Text", "context": {}}])
    assert len(cat) == 2 and cat[0]["name"] == "The V" and cat[0]["type"] == "organism" and cat[0]["desc"], cat
    try:
        vi_vision_catalog("nope", fetch=lambda _f: []); raise SystemExit("FAIL catalog-frame")
    except ViVisionAddressError:
        pass
    print("vi_vision OPERATIONAL self-test: ALL PASS (parse·scope·type-guard·not-found·jwt-sub·write-row·write-auth-gate·catalog)")
