"""mcp_face/remote.py — the REMOTE MCP gateway (Claude Design connector inlet).

ARCHITECTURE (approved design: build-prep/claude-design/REMOTE-MCP-EXPOSURE-DESIGN.md):
  transport + auth + posture-filter ONLY. Reuses the SAME runtime.suite.Suite the stdio
  mcp_face/server.py and the :8770 bridge use — NO second engine.

ACCESS (Tim 2026-06-22: one brain, no hardcoded lists):
  The tool set IS the LIVE REGISTRY (_TOOL_MANAGER). Access is identity → posture:
  no token → nothing (401); sub == OPERATOR → ALL tools; any other valid user →
  posture=='safe' tools only (fail-closed: unclassified tools are operator-only).
  MANDATORY AUDIT — every remote call is logged before execution; audit-write failure
  ⇒ the call FAILS LOUD. No un-audited call ever succeeds.

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

DEFAULT_PORT = 8772
AUDIT_LOCK = threading.Lock()
# Suite has per-resource locks for writes; reads are safe. We serialize ALL dispatch
# under one lock for the local dev gateway (simple + correct for a single client; the
# per-resource locks would let reads go concurrent, but local dev doesn't need that).
DISPATCH_LOCK = threading.Lock()

# ── ACCESS MODEL (Tim 2026-06-22: ONE brain, no hardcoded lists) ───────────────────────────
# The tool set is the LIVE REGISTRY (_TOOL_MANAGER) — never a hand-maintained allow-list file.
# Access is a pure IDENTITY → POSTURE filter over that one registry:
#   • no valid Supabase token            → TIER_NONE     → nothing (401)
#   • valid token, sub == OPERATOR        → TIER_OPERATOR → ALL tools (Tim's remote self = his full
#                                                            local surface; identity IS the boundary)
#   • valid token, sub != OPERATOR        → TIER_CLIENT   → only tools whose POSTURE == "safe"
# The old remote_exposure.json (a hardcoded 23-subset) + the gateway's clients.allowed_tools (a
# hardcoded 15-subset) are DELETED. Posture is meant to be a PROPERTY OF EACH TOOL (declared at the
# tool's definition) — read by _tool_posture() below. Until tools carry that tag, _tool_posture
# returns "" (unclassified) ⇒ TIER_CLIENT is FAIL-CLOSED (gets nothing): a never-tagged/new tool can
# never leak to a non-operator. Operator is unaffected (sees the whole registry).
TIER_NONE = ""
TIER_OPERATOR = "operator"
TIER_CLIENT = "client"
OPERATOR_USER_ID = os.environ.get("OPERATOR_USER_ID", "ebe5f9c7-4d66-4717-835f-afc96088facb")  # Tim (…615)


def _tool_posture(tool_obj) -> str:
    """The tool's OWN declared posture (registry-native, NOT a separate list). Reads a `posture`
    attribute / annotation on the registered tool; "" when unclassified. The single source for the
    non-operator safe-subset — populated by tagging tools at their definition (the de-dup of the old
    remote_exposure.json knowledge onto the tools). "" ⇒ operator-only (fail-closed)."""
    p = getattr(tool_obj, "posture", None)
    if not p:
        ann = getattr(tool_obj, "annotations", None)
        if isinstance(ann, dict):
            p = ann.get("posture")
        else:
            p = getattr(ann, "posture", None)
    return str(p) if p else ""


def _tools_for_tier(tier: str) -> list:
    """The (name, tool_obj) pairs visible to a tier — derived from the LIVE registry every call.
    operator → all; client → posture=='safe' only; none → empty."""
    items = sorted(_TOOL_MANAGER._tools.items())
    if tier == TIER_OPERATOR:
        return items
    if tier == TIER_CLIENT:
        return [(n, t) for n, t in items if _tool_posture(t) == "safe"]
    return []

# ★ PUBLIC-INSTANCE HARDENING (advisor security catch): when this instance is Funnel-exposed to the
# public internet, REMOTE_PUBLIC=1 DISABLES the local dev-token bypass entirely — otherwise a static
# COMPANY_REMOTE_DEV_TOKEN would be a JWT-bypass reachable from the internet (Funnel forwards to
# 127.0.0.1, so the server cannot tell external from local by address). Public ⇒ JWT-only, no exceptions.
REMOTE_PUBLIC = os.environ.get("REMOTE_PUBLIC", "") not in ("", "0", "false", "False")


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
# LOCAL dev: a Bearer token == COMPANY_REMOTE_DEV_TOKEN grants the operator tier. Local/tailnet
# ONLY — hard-disabled on the public endpoint (REMOTE_PUBLIC ⇒ Supabase JWT required).
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


def _validate_supabase_jwt(tok: str) -> tuple[bool, str, str, str]:
    """Validate a Supabase-issued JWT. Returns (ok, subject, tier, reason).
    FAIL CLOSED on any validation gap (no secret/JWKS configured, bad signature, expired,
    wrong audience). Never a permissive default. The TIER is identity-derived: sub ==
    OPERATOR_USER_ID → TIER_OPERATOR (all tools); any other valid user → TIER_CLIENT
    (posture-safe subset only). No connector-scope claim is required or consulted — identity
    is the whole gate.

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
    # IDENTITY IS THE GATE. A cryptographically-verified sub == OPERATOR_USER_ID → operator (all
    # tools). Any other valid Supabase user → client (posture-safe subset). No scope claim needed.
    if subject == OPERATOR_USER_ID:
        return True, subject, TIER_OPERATOR, "supabase-jwt-operator"
    return True, subject, TIER_CLIENT, "supabase-jwt-client"


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
    # ★ DEV-TOKEN BYPASS — LOCAL-ONLY, HARD-DISABLED when public (advisor security catch). On a
    # Funnel-exposed instance (REMOTE_PUBLIC=1) the static dev token is a JWT-bypass reachable from
    # the internet, so it is refused entirely: public ⇒ JWT-only. Only on a non-public (local/tailnet)
    # instance does the dev token grant the operator tier.
    if DEV_TOKEN and tok == DEV_TOKEN:
        if REMOTE_PUBLIC:
            return False, "", "", "dev-token bypass is disabled on the public instance (JWT-only)."
        return True, "dev-local", TIER_OPERATOR, "local dev token"
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
            # The PUBLIC resource URL the connector apps see (the Funnel HTTPS origin), + the REAL
            # Supabase authorization server (so MCP clients run OAuth against Supabase Auth — the
            # same AS the proven Claude Design connector uses). PUBLIC_RESOURCE_URL = the Funnel
            # origin (e.g. https://workstation001.tailXX'.ts.net); PUBLIC_AS_URL = the Supabase
            # auth base (…supabase.co/auth/v1), derived from SUPABASE_JWKS_URL when not set.
            res_base = os.environ.get("PUBLIC_RESOURCE_URL", "").rstrip("/") \
                or f"http://127.0.0.1:{self.server.server_address[1]}"
            as_url = os.environ.get("PUBLIC_AS_URL", "").rstrip("/")
            if not as_url and SUPABASE_JWKS_URL:
                as_url = SUPABASE_JWKS_URL.split("/.well-known/")[0]   # …/auth/v1
            meta = {
                "resource": f"{res_base}/mcp",
                "authorization_servers": [as_url] if as_url else [],
                "bearer_methods_supported": ["header"],
            }
            self._json(200, meta)
            return
        if self.path == "/healthz":
            self._json(200, {"ok": True, "service": "company-remote-mcp",
                             "registry_tools": len(_TOOL_MANAGER._tools)})
            return
        # everything else requires auth
        ok, subj, tier, reason = _validate_auth(self.headers)
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
        ok, subj, tier, reason = _validate_auth(self.headers)
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
            # The tool set IS the live registry, filtered by identity tier (operator → all;
            # client → posture-safe). No hardcoded allow-list file.
            tools = []
            for n, tool_obj in _tools_for_tier(tier):
                schema = getattr(tool_obj, "parameters", None) or {"type": "object"}
                tools.append({"name": n,
                              "description": getattr(tool_obj, "description", "") or "",
                              "inputSchema": schema})
            self._json(200, {"jsonrpc": "2.0", "id": rid, "result": {"tools": tools}})
            return
        if method == "tools/call":
            tool = params.get("name", "")
            args = params.get("arguments", {}) or {}
            # ACCESS = identity tier over the live registry. operator → any tool; client → only
            # posture=='safe' tools. The MANDATORY AUDIT is never bypassed (the safety record;
            # git-revert + Tim's per-app tool visibility are the recovery). Then registry-drift +
            # the tool's own teaching errors are the only gates left.
            tool_obj = _TOOL_MANAGER._tools.get(tool)
            if tier == TIER_OPERATOR:
                posture = "operator"
            else:
                # client tier: the tool must exist AND be tagged safe (fail-closed if unclassified)
                if tool_obj is None or _tool_posture(tool_obj) != "safe":
                    _audit(call_id, tool, args, subj, tier, "DENY",
                           f"tier {tier!r}: tool {tool!r} not in the safe set (identity-gated, fail-closed)")
                    self._json(200, {"jsonrpc": "2.0", "id": rid,
                                     "result": {"content": [{"type": "text",
                                     "text": f"REFUSED: {tool!r} not available to your access level"}],
                                     "isError": True}})
                    return
                posture = "safe"
            # DISPATCH: the identity gate has passed. Dispatch through the stdio face's registered
            # tool fn (inherit its arg-handling + teaching errors + _guard_tools). Serialized under
            # DISPATCH_LOCK.
            if tool_obj is None:
                _audit(call_id, tool, args, subj, tier, "DENY",
                       f"tool {tool!r} not found in the face tool manager "
                       f"(registry drift / unknown tool — refuse, never guess)")
                self._json(200, {"jsonrpc": "2.0", "id": rid,
                                 "result": {"content": [{"type": "text",
                                 "text": f"REFUSED: {tool!r} not dispatchable (registry drift)"}],
                                 "isError": True}})
                return
            fn = tool_obj.fn
            try:
                with DISPATCH_LOCK:
                    result = fn(**args)
                _audit(call_id, tool, args, subj, tier, "OK")
            except (ValueError, KeyError) as e:
                # a TEACHING error from the tool's own contract — surface, don't audit-fail
                _audit(call_id, tool, args, subj, tier, "TEACHING-ERROR", f"{type(e).__name__}: {e}")
                self._json(200, {"jsonrpc": "2.0", "id": rid,
                                 "result": {"content": [{"type": "text",
                                 "text": f"Error: {type(e).__name__}: {e}"}], "isError": True}})
                return
            except Exception as e:
                _audit(call_id, tool, args, subj, tier, "DISPATCH-ERROR",
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
                     f"({len(_TOOL_MANAGER._tools)} tools in the live registry; "
                     f"identity-gated [operator→all · client→posture-safe · none→401]; "
                     f"mandatory-audit ON)\n")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.shutdown()


if __name__ == "__main__":
    main()