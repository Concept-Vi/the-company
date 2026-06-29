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
# ── STREAMABLE-HTTP SESSIONS (spec 2025-06-18) ───────────────────────────────────────────
# The MCP Streamable-HTTP transport issues an `Mcp-Session-Id` on the initialize response and
# the client echoes it on every subsequent request; a GET /mcp opens a server→client SSE
# stream. The auth/posture/audit gate is UNCHANGED — session-id is a transport correlator, NOT
# an auth token (auth is ALWAYS the Bearer, validated by _validate_auth on EVERY request incl.
# the GET stream). We track issued ids in a set so we can 404 a stale/unknown id per spec, but
# we never trust the id for access. The official SDK client (OpenWebUI's) tolerates a missing
# id, so this is additive spec-hardening for stricter clients — the Bearer remains the boundary.
MCP_SESSION_ID_HEADER = "Mcp-Session-Id"
_SESSIONS: set[str] = set()
_SESSIONS_LOCK = threading.Lock()
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
    operator → all; client → posture=='safe' only; none → empty.

    THIS REMAINS THE LIVE AUTHORITY (identity fusion: additive + behavior-preserving). The grant
    table (runtime/grants) is wired as a PROVEN-EQUAL SHADOW alongside it (see _grant_shadow_audit /
    _principal_for_tier) — it is consulted + its divergence is recorded, but it does NOT yet decide.
    The posture/tier gate stays the fail-closed floor; flipping authority to grants is a later,
    lead-reviewed one-line change once the shadow is trusted."""
    items = sorted(_TOOL_MANAGER._tools.items())
    if tier == TIER_OPERATOR:
        return items
    if tier == TIER_CLIENT:
        return [(n, t) for n, t in items if _tool_posture(t) == "safe"]
    return []


# ── GRANT SHADOW (identity fusion — GATE-READS-GRANTS, seeded to current, behavior-preserving) ──
# The remote gate's tier decision is the LIVE authority. The company-native grant store
# (runtime/grants) is consulted IN PARALLEL as a shadow, seeded so its answer is IDENTICAL today.
# Divergence is recorded (never silent), proving the binary tier == the grant-row floor, so the
# richer model is purely additive. The shadow NEVER changes the decision this increment.
def _principal_for_tier(tier: str, subject: str) -> tuple[str, str]:
    """Map a remote tier + JWT subject to a (principal_type, principal_id) for the grant table.
    operator → (viewer, OPERATOR_USER_ID); client → (viewer, '*'-resolved by the safe-grants);
    we pass the subject as the viewer id (a client's per-tool safe grants are principal_id='*', so
    any viewer id matches them — exactly today's 'any valid non-operator user → safe subset')."""
    from runtime import grants as _grants
    if tier == TIER_OPERATOR:
        return (_grants.PT_VIEWER, _grants.OPERATOR_USER_ID)
    return (_grants.PT_VIEWER, subject or "unknown-viewer")


def _tool_allowed_via_grants(tool_name: str, tier: str, subject: str) -> bool | None:
    """The grant-driven shadow answer (None if the grant store is empty/unseeded — then there is
    nothing to compare, the shadow is silent). Read-only; degrade-clean (any error → None, never
    affects the live decision)."""
    try:
        from runtime import grants as _grants
        if not _grants.fold_grants():
            return None                          # unseeded → no shadow yet (nothing to diverge from)
        pt, pid = _principal_for_tier(tier, subject)
        return _grants.tool_allowed_via_grants(tool_name, principal_type=pt, principal_id=pid)
    except Exception:
        return None                              # shadow must NEVER break the live gate (read-only)


def _grant_shadow_audit(tool_name: str, tier: str, subject: str, live_allowed: bool) -> None:
    """Compare the grant shadow against the LIVE tier decision; record any divergence to the audit
    jsonl mirror (loud, never silent). Pure observation — does not change `live_allowed`."""
    shadow = _tool_allowed_via_grants(tool_name, tier, subject)
    if shadow is None or shadow == live_allowed:
        return
    line = json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                       "event": "GRANT_SHADOW_DIVERGENCE", "tool": tool_name, "tier": tier,
                       "subject": subject, "live_allowed": live_allowed, "grant_allowed": shadow},
                      default=str) + "\n"
    try:
        with AUDIT_LOCK:
            with open(os.path.join(fcfg.STORE_DIR, "remote_mcp_audit.jsonl"), "a",
                      encoding="utf-8") as f:
                f.write(line)
    except OSError:
        pass

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

    def _send(self, code: int, body: bytes, ctype: str = "application/json",
              extra_headers: dict | None = None) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        for k, v in (extra_headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, obj: dict, extra_headers: dict | None = None) -> None:
        self._send(code, json.dumps(obj, default=str).encode(), "application/json",
                   extra_headers=extra_headers)

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
            # Streamable-HTTP GET opens a server→client SSE stream (the spec's notification
            # channel). Auth ALREADY enforced above (_validate_auth ran before this branch —
            # the Bearer is the boundary on the stream too, never the session id). We hold the
            # connection open with periodic SSE keepalive comments so a strict client's GET
            # raise_for_status() sees 200 + text/event-stream. This gateway emits no
            # server-initiated notifications (capabilities.tools.listChanged == False), so the
            # stream carries only keepalives until the client disconnects.
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache, no-store")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            try:
                # initial comment so proxies/clients flush headers immediately
                self.wfile.write(b": connected\n\n")
                self.wfile.flush()
                while True:
                    time.sleep(15)
                    self.wfile.write(b": keepalive\n\n")
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError, OSError):
                # client disconnected — normal stream close
                return
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

        # initialize handshake — return server info + issue the Streamable-HTTP session id.
        # The id is a TRANSPORT correlator (echoed by the client on later requests + used to
        # open the GET SSE stream); it is NEVER the auth boundary — _validate_auth(Bearer) gates
        # every request above. We track issued ids so a stale id can be 404'd per spec, but the
        # gate never consults them.
        if method == "initialize":
            sid = uuid.uuid4().hex
            with _SESSIONS_LOCK:
                _SESSIONS.add(sid)
            self._json(200, {
                "jsonrpc": "2.0", "id": rid,
                "result": {
                    "protocolVersion": "2025-06-18",
                    "serverInfo": {"name": "company-remote-mcp", "version": "0.1.0"},
                    "capabilities": {"tools": {"listChanged": False}},
                },
            }, extra_headers={MCP_SESSION_ID_HEADER: sid})
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
            # GRANT SHADOW (identity fusion): record the grant-table answer alongside the LIVE tier
            # decision (operator → all; client → safe-only). Pure observation, seeded-to-current so it
            # agrees; divergence is logged loud. Does NOT change the decision below (behavior-preserving).
            _live_allowed = (tier == TIER_OPERATOR) or (
                tool_obj is not None and _tool_posture(tool_obj) == "safe")
            _grant_shadow_audit(tool, tier, subj, _live_allowed)
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

    def do_DELETE(self):
        # Streamable-HTTP session termination. Auth-gated like everything else; we forget the
        # id (best-effort) and return 200. The Bearer remains the boundary; this just frees the
        # tracked id. (The SDK client tolerates 200/204/405 here.)
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
        sid = self.headers.get(MCP_SESSION_ID_HEADER, "")
        if sid:
            with _SESSIONS_LOCK:
                _SESSIONS.discard(sid)
        self._send(200, b"")

    def log_message(self, fmt, *a):  # quieter
        sys.stderr.write(f"[remote-mcp] {self.address_string()} {fmt % a}\n")


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    H = Handler
    # daemon_threads: held SSE GET streams must not block process shutdown.
    # request_queue_size: each open SSE GET pins one worker thread; raise the backlog so
    # listing/calling POSTs are never starved behind a parked stream.
    ThreadingHTTPServer.daemon_threads = True
    ThreadingHTTPServer.request_queue_size = 64
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