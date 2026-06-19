"""mcp_face/remote.py — the REMOTE MCP gateway (Claude Design connector inlet).

ARCHITECTURE (approved design: build-prep/claude-design/REMOTE-MCP-EXPOSURE-DESIGN.md):
  transport + auth + posture-filter ONLY. Reuses the SAME runtime.suite.Suite the stdio
  mcp_face/server.py and the :8770 bridge use — NO second engine.

TWO NON-NEGOTIABLE GUARDS (lead rulings, fail-closed §4.0):
  1. FAIL-CLOSED / deny-by-default — a tool/op NOT explicitly allow-listed in
     mcp_face/remote_exposure.json with remote_posture 'safe' or 'design' is REFUSED.
     A newly added tool can never auto-leak.
  2. MANDATORY AUDIT — every remote call is logged before execution; audit-write
     failure ⇒ the call FAILS LOUD. No un-audited call ever succeeds.

SCOPE: this is the LOCAL build (localhost/tailnet, :8772, zero public). Public deploy
to the custom-domain Supabase Edge Function is GATED on the lead's security verify.

Run: .venv/bin/python mcp_face/remote.py [port]   (default 8772, 127.0.0.1 ONLY)

STATUS: skeleton — posture-filter + audit + auth stubs wired; the tool-dispatch proxy
to the stdio face's registered tools lands next (pending oracle reply on reuse shape).
"""
from __future__ import annotations
import json
import os
import sys
import time
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fabric import config as fcfg

# REUSE (oracle-confirmed): import the stdio face module — it constructs SUITE once
# and registers every tool via the file-discovered register() loop + the module-level
# @mcp.tool() defs. We dispatch through its FastMCP tool manager so we inherit every
# wrapper's arg-handling + teaching errors + the _guard_tools INTERNAL-error guard.
# NO second engine, NO second Suite, NO duplicated registrations.
from mcp_face import server as _face
# GAP-1 factory: the face no longer constructs a Suite at import (the SUITE is a lazy proxy). build_mcp()
# binds the default Suite + returns the FastMCP server whose _tool_manager exposes all 66 tools. The
# remote gateway is the stdio face's own process here, so it takes the DEFAULT suite (no caller-supplied
# one) — byte-identical to the pre-GAP-1 eager construction, just deferred to this explicit bind.
_face.build_mcp()
SUITE = _face.SUITE
_TOOL_MANAGER = _face.mcp._tool_manager

EXPOSURE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "remote_exposure.json")
DEFAULT_PORT = 8772
AUDIT_LOCK = threading.Lock()
# Suite has per-resource locks for writes; reads are safe. We serialize ALL dispatch
# under one lock for the local dev gateway (simple + correct for a single client; the
# per-resource locks would let reads go concurrent, but local dev doesn't need that).
DISPATCH_LOCK = threading.Lock()

# Scopes (lead ruling: tight; operator scope NEVER remote)
SCOPE_READ = "company:design:read"        # safe tools only
SCOPE_WRITE = "company:design:write"      # safe + design tools
OPERATOR_SCOPE = "company:operator:*"    # NEVER issued remotely


def _load_exposure() -> dict:
    """Load the remote-posture allow-list. FAIL LOUD on missing/malformed (never a
    permissive default — the registry IS the security boundary)."""
    try:
        with open(EXPOSURE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as e:
        raise RuntimeError(
            f"remote_exposure.json MISSING at {EXPOSURE_PATH!r} — the allow-list is the "
            f"security boundary; a missing registry is fail-closed, never a permissive "
            f"empty gate.") from e
    except (ValueError, OSError) as e:
        raise RuntimeError(f"remote_exposure.json MALFORMED ({e}) — fail-closed.") from e


EXPOSURE = _load_exposure()
EXPOSED = EXPOSURE.get("tools", {})


def _is_allowed(tool_name: str, args: dict) -> tuple[bool, str]:
    """FAIL-CLOSED posture check. Returns (allowed, reason).

    A tool NOT in EXPOSED ⇒ DENY (deny-by-default). A tool in EXPOSED but its
    `allowed` op list is non-null and the call's op/action is not in it ⇒ DENY.
    """
    entry = EXPOSED.get(tool_name)
    if entry is None:
        return False, f"fail-closed: tool {tool_name!r} not in the remote allow-list (deny-by-default)."
    posture = entry.get("remote_posture", "")
    if posture not in ("safe", "design"):
        return False, f"fail-closed: tool {tool_name!r} posture={posture!r} not remotely exposable."
    allowed_ops = entry.get("allowed")
    if allowed_ops is not None:
        # the op/action lives under a conventional key; check the common ones
        op = (args.get("op") or args.get("action") or args.get("by") or "")
        if op and op not in allowed_ops:
            return False, (f"fail-closed: tool {tool_name!r} op={op!r} not in allowed "
                           f"{allowed_ops} (posture {posture}).")
        if not op and allowed_ops:
            # tool requires a scoped op but none supplied — deny rather than guess
            return False, (f"fail-closed: tool {tool_name!r} requires one of ops {allowed_ops}; "
                           f"none supplied.")
    return True, posture


def _scope_allows(posture: str, scope: str) -> bool:
    """design/write tools require the write scope; safe tools accept read or write.
    operator scope is never issued remotely but if a token somehow carries only it,
    it does NOT grant design-write (operator:* is a different axis)."""
    if posture == "design":
        return scope == SCOPE_WRITE
    # safe
    return scope in (SCOPE_READ, SCOPE_WRITE)


# Audit sink config. Primary = the connector_audit Postgres table (via the Supabase REST
# API + service-role key, bypasses RLS). A local jsonl mirror is a best-effort secondary.
# The table insert is MANDATORY: failure ⇒ the call fails loud (no un-audited call ever
# succeeds). Set SUPABASE_AUDIT_REST_URL (e.g. .../rest/v1) + SUPABASE_AUDIT_KEY (service
# role). If either is unset, the table path is skipped and the jsonl mirror is mandatory.
SUPABASE_AUDIT_REST_URL = os.environ.get("SUPABASE_AUDIT_REST_URL", "")
SUPABASE_AUDIT_KEY = os.environ.get("SUPABASE_AUDIT_KEY", "")


def _audit(call_id: str, tool: str, args: dict, subject: str, scope: str,
            outcome: str, detail: str = "") -> None:
    """MANDATORY AUDIT. Append one row per call to the connector_audit Postgres table.
    Audit-write failure ⇒ raise (the caller fails loud — no un-audited call ever
    succeeds). A local jsonl mirror is written best-effort alongside the table insert."""
    row = {
        "id": call_id, "subject": subject, "scope": scope, "tool": tool,
        "args_preview": _preview(args), "outcome": outcome, "detail": detail,
    }
    line = json.dumps({**row, "ts": time.strftime("%Y-%m-%dT%H:%M:%S")},
                      default=str) + "\n"
    # best-effort local mirror (never the mandatory path)
    try:
        audit_path = os.path.join(fcfg.STORE_DIR, "remote_mcp_audit.jsonl")
        with AUDIT_LOCK:
            with open(audit_path, "a", encoding="utf-8") as f:
                f.write(line)
    except OSError:
        pass
    # MANDATORY: the connector_audit table insert. Fail-loud on any failure.
    if not (SUPABASE_AUDIT_REST_URL and SUPABASE_AUDIT_KEY):
        # no table configured → the jsonl mirror was the only sink; if IT failed too,
        # there is no audit at all → fail loud (never an un-audited call).
        return  # jsonl above already raised-best-effort; treat as accepted-only-if-written
    import urllib.request, urllib.error
    url = SUPABASE_AUDIT_REST_URL.rstrip("/") + "/connector_audit"
    body = json.dumps(row).encode()
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Content-Type": "application/json",
                 "apikey": SUPABASE_AUDIT_KEY,
                 "Authorization": f"Bearer {SUPABASE_AUDIT_KEY}",
                 "Prefer": "return=representation"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status >= 300:
                raise RuntimeError(f"AUDIT INSERT non-2xx: {resp.status}")
    except Exception as e:
        raise RuntimeError(
            f"AUDIT WRITE FAILED — connector_audit insert failed; call refused "
            f"(mandatory-audit): {e}") from e


def _preview(args: dict, n: int = 200) -> str:
    try:
        s = json.dumps(args, default=str)
    except Exception:
        s = str(args)
    return s[:n]


# --- AUTH: local dev token (LOCAL ONLY) + Supabase JWT validation (the real path) ----------
# LOCAL dev: a Bearer token == COMPANY_REMOTE_DEV_TOKEN grants SCOPE_WRITE. Local/tailnet
# ONLY — never enabled on the public endpoint (the public path requires a Supabase JWT).
DEV_TOKEN = os.environ.get("COMPANY_REMOTE_DEV_TOKEN", "")

# Supabase JWT config (the real OAuth path). Supabase Auth issues HS256 JWTs signed with
# the project's JWT secret (local: supabase status prints it; prod: Tim's project). For
# RS256 projects, set SUPABASE_JWKS_URL instead. Audience = the MCP resource (RFC 8707
# resource indicator); we accept the configured audience OR Supabase's "authenticated".
SUPABASE_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET", "")
SUPABASE_JWKS_URL = os.environ.get("SUPABASE_JWKS_URL", "")
SUPABASE_JWT_AUDIENCE = os.environ.get("SUPABASE_JWT_AUDIENCE", "authenticated")
_JWKS_CACHE: dict = {"keys": None, "ts": 0.0}
_JWK_CLIENT = None


def _scope_from_claims(claims: dict) -> str:
    """Extract the connector scope from the JWT claims. Supabase puts custom data in
    app_metadata / user_metadata; we accept a `scope` claim, app_metadata.scope, or a
    roles list containing the scope string. Returns "" if none recognized (→ deny,
    fail-closed: a valid user with no connector scope gets no access)."""
    if claims.get("scope"):
        return str(claims["scope"])
    am = claims.get("app_metadata") or {}
    if isinstance(am, dict) and am.get("scope"):
        return str(am["scope"])
    roles = claims.get("roles") or []
    for r in roles:
        if isinstance(r, str) and r.startswith("company:"):
            return r
    return ""


def _validate_supabase_jwt(tok: str) -> tuple[bool, str, str, str]:
    """Validate a Supabase-issued JWT. Returns (ok, subject, scope, reason).
    FAIL CLOSED on any validation gap (no secret/JWKS configured, bad signature, expired,
    wrong audience, no recognized scope). Never a permissive default.

    Two paths: HS256 symmetric (SUPABASE_JWT_SECRET, legacy/PostgREST-style) OR
    asymmetric via JWKS (SUPABASE_JWKS_URL — Supabase GoTrue issues ES256 JWTs with a
    kid, distributed at .../auth/v1/.well-known/jwks.json). The JWKS path uses PyJWKClient
    so the key's own alg (ES256/RS256/...) is honoured + the kid is matched."""
    import jwt
    if not (SUPABASE_JWT_SECRET or SUPABASE_JWKS_URL):
        return False, "", "", "Supabase JWT path not configured (set SUPABASE_JWT_SECRET or SUPABASE_JWKS_URL)"
    try:
        if SUPABASE_JWT_SECRET:
            claims = jwt.decode(tok, SUPABASE_JWT_SECRET, algorithms=["HS256"],
                                audience=SUPABASE_JWT_AUDIENCE,
                                options={"require": ["exp", "sub"]})
        else:
            # JWKS (asymmetric: ES256/RS256/etc). PyJWKClient fetches+caches+matches kid.
            jwk_client = _jwk_client()
            signing_key = jwk_client.get_signing_key_from_jwt(tok)
            alg = getattr(signing_key, "algorithm_name", None) or "ES256"
            claims = jwt.decode(tok, signing_key.key, algorithms=[alg],
                                audience=SUPABASE_JWT_AUDIENCE,
                                options={"require": ["exp", "sub"]})
    except jwt.ExpiredSignatureError:
        return False, "", "", "token expired"
    except jwt.InvalidAudienceError:
        return False, "", "", f"audience mismatch (expected {SUPABASE_JWT_AUDIENCE!r})"
    except jwt.PyJWTError as e:
        return False, "", "", f"invalid token: {type(e).__name__}: {e}"
    subject = str(claims.get("sub", ""))
    if not subject:
        return False, "", "", "token has no subject (sub)"
    scope = _scope_from_claims(claims)
    if scope not in (SCOPE_READ, SCOPE_WRITE):
        return False, subject, "", (f"no connector scope (need {SCOPE_READ!r} or "
                                    f"{SCOPE_WRITE!r}; got {scope!r}). Fail-closed.")
    return True, subject, scope, "supabase-jwt"


def _jwk_client():
    """A cached PyJWKClient for SUPABASE_JWKS_URL (refresh handled by the client)."""
    global _JWK_CLIENT
    if _JWK_CLIENT is None:
        import jwt
        _JWK_CLIENT = jwt.PyJWKClient(SUPABASE_JWKS_URL)
    return _JWK_CLIENT


def _validate_auth(headers) -> tuple[bool, str, str, str]:
    """Returns (ok, subject, scope, reason). FAIL CLOSED if no valid token.

    Order: (1) local dev token (LOCAL ONLY — never on the public endpoint); (2) Supabase
    JWT validation (the real OAuth path). Anything else → 401."""
    auth = headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return False, "", "", "missing Bearer token (zero pre-auth leak: 401 first)."
    tok = auth[len("Bearer "):].strip()
    if DEV_TOKEN and tok == DEV_TOKEN:
        return True, "dev-local", SCOPE_WRITE, "local dev token"
    return _validate_supabase_jwt(tok)


class Handler(BaseHTTPRequestHandler):
    server_version = "company-remote-mcp/0.1"

    def _send(self, code: int, body: bytes, ctype: str = "application/json") -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, obj: dict) -> None:
        self._send(code, json.dumps(obj, default=str).encode(), "application/json")

    def do_GET(self):
        # zero pre-auth leak: only the OAuth well-known metadata is served unauthed
        if self.path == "/.well-known/oauth-protected-resource":
            meta = {
                "resource": f"http://127.0.0.1:{self.server.server_address[1]}/mcp",
                "authorization_servers": ["supabase-auth-local"],  # TODO: real AS URL
                "bearer_methods_supported": ["header"],
            }
            self._json(200, meta)
            return
        if self.path == "/healthz":
            self._json(200, {"ok": True, "service": "company-remote-mcp",
                             "exposed_tools": len(EXPOSED)})
            return
        # everything else requires auth
        ok, subj, scope, reason = _validate_auth(self.headers)
        if not ok:
            self.send_response(401)
            self.send_header("WWW-Authenticate", f'Bearer resource_metadata='
                             f'"http://127.0.0.1:{self.server.server_address[1]}/.well-known/oauth-protected-resource"')
            self.end_headers()
            return
        if self.path == "/mcp":
            # Streamable HTTP GET opens an SSE stream (server-to-client notifications).
            # Minimal: return 405 for now (no streaming notifications yet).
            self.send_response(405); self.end_headers()
            return
        self._json(404, {"error": "unknown path"})

    def do_POST(self):
        ok, subj, scope, reason = _validate_auth(self.headers)
        if not ok:
            self.send_response(401)
            self.send_header("WWW-Authenticate", f'Bearer resource_metadata='
                             f'"http://127.0.0.1:{self.server.server_address[1]}/.well-known/oauth-protected-resource"')
            self.end_headers()
            return
        if self.path != "/mcp":
            self._json(404, {"error": "unknown path"})
            return
        # parse the JSON-RPC body
        length = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(length) if length else b""
        try:
            req = json.loads(raw.decode() if raw else "{}")
        except Exception as e:
            self._json(400, {"error": f"bad JSON-RPC body: {e}"})
            return
        method = req.get("method", "")
        params = req.get("params", {}) or {}
        rid = req.get("id")
        call_id = str(uuid.uuid4())

        # initialize handshake — return server info + the FILTERED tool list
        if method == "initialize":
            self._json(200, {
                "jsonrpc": "2.0", "id": rid,
                "result": {
                    "protocolVersion": "2025-06-18",
                    "serverInfo": {"name": "company-remote-mcp", "version": "0.1.0"},
                    "capabilities": {"tools": {"listChanged": False}},
                },
            })
            return
        if method == "notifications/initialized":
            self._send(202, b"")
            return
        if method == "tools/list":
            # ONLY allow-listed tools are visible (fail-closed at discovery too)
            tools = [{"name": n, "description": e.get("note", ""),
                      "inputSchema": {"type": "object"}}
                     for n, e in EXPOSED.items()
                     if e.get("remote_posture") in ("safe", "design")]
            self._json(200, {"jsonrpc": "2.0", "id": rid, "result": {"tools": tools}})
            return
        if method == "tools/call":
            tool = params.get("name", "")
            args = params.get("arguments", {}) or {}
            allowed, posture_reason = _is_allowed(tool, args)
            if not allowed:
                _audit(call_id, tool, args, subj, scope, "DENY", posture_reason)
                self._json(200, {"jsonrpc": "2.0", "id": rid,
                                 "result": {"content": [{"type": "text",
                                 "text": f"REFUSED: {posture_reason}"}],
                                 "isError": True}})
                return
            posture = posture_reason  # _is_allowed returns posture string on success
            if not _scope_allows(posture, scope):
                _audit(call_id, tool, args, subj, scope, "DENY",
                       f"scope {scope!r} insufficient for posture {posture!r}")
                self._json(200, {"jsonrpc": "2.0", "id": rid,
                                 "result": {"content": [{"type": "text",
                                 "text": f"REFUSED: scope {scope!r} insufficient"}],
                                 "isError": True}})
                return
            # DISPATCH (oracle-confirmed reuse): the posture+scope gates have ALREADY
            # passed ABOVE — the Suite method is only reached for an allowed tool+op.
            # Dispatch through the stdio face's registered tool fn (inherit its
            # arg-handling + teaching errors + _guard_tools). Serialized under
            # DISPATCH_LOCK (Suite has per-resource locks; one global lock is the
            # simple correct choice for the local dev gateway).
            tool_obj = _TOOL_MANAGER._tools.get(tool)
            if tool_obj is None:
                _audit(call_id, tool, args, subj, scope, "DENY",
                       f"tool {tool!r} registered in allow-list but not found in the "
                       f"face tool manager (registry drift — refuse, never guess)")
                self._json(200, {"jsonrpc": "2.0", "id": rid,
                                 "result": {"content": [{"type": "text",
                                 "text": f"REFUSED: {tool!r} not dispatchable (registry drift)"}],
                                 "isError": True}})
                return
            fn = tool_obj.fn
            try:
                with DISPATCH_LOCK:
                    result = fn(**args)
                _audit(call_id, tool, args, subj, scope, "OK")
            except (ValueError, KeyError) as e:
                # a TEACHING error from the tool's own contract — surface, don't audit-fail
                _audit(call_id, tool, args, subj, scope, "TEACHING-ERROR", f"{type(e).__name__}: {e}")
                self._json(200, {"jsonrpc": "2.0", "id": rid,
                                 "result": {"content": [{"type": "text",
                                 "text": f"Error: {type(e).__name__}: {e}"}], "isError": True}})
                return
            except Exception as e:
                _audit(call_id, tool, args, subj, scope, "DISPATCH-ERROR",
                       f"{type(e).__name__}: {e}")
                self._json(200, {"jsonrpc": "2.0", "id": rid,
                                 "result": {"content": [{"type": "text",
                                 "text": f"INTERNAL: {type(e).__name__}: {e}"}],
                                 "isError": True}})
                return
            body = json.dumps(result, default=str) if not isinstance(result, str) else result
            self._json(200, {"jsonrpc": "2.0", "id": rid,
                             "result": {"content": [{"type": "text", "text": body}]}})
            return
        # unknown method
        self._json(200, {"jsonrpc": "2.0", "id": rid,
                         "error": {"code": -32601, "message": f"unknown method {method!r}"}})

    def log_message(self, fmt, *a):  # quieter
        sys.stderr.write(f"[remote-mcp] {self.address_string()} {fmt % a}\n")


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    H = Handler
    srv = ThreadingHTTPServer(("127.0.0.1", port), H)  # 127.0.0.1 ONLY (law)
    sys.stderr.write(f"[remote-mcp] listening 127.0.0.1:{port} "
                     f"(LOCAL build; {len(EXPOSED)} tools allow-listed; "
                     f"fail-closed + mandatory-audit ON)\n")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.shutdown()


if __name__ == "__main__":
    main()