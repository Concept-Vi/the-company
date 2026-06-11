"""runtime/capability_handlers/r3.py — the R3 CLIENT the ③ (and ④ git/ci, ⑤ routines) handlers call
to reach the config_writer SERVICE (Capability Fabric §3.1/§3.2).

WHY a client (the floor + DRY reconciliation): the handler layer is "pure functions over Suite —
socket-free, mcp-free" (§3.2), and the FLOOR is that the face NEVER executes — a sanctioned SERVICE
(config_writer R3, the supervisor R1/R1-prime, the wire R2) acts. A ③ handler therefore does NOT open
`.claude` or shell `claude mcp` itself; it builds the validated request and routes it through THIS
client to the config_writer. The client has TWO modes, one law:

  · IN-PROCESS (the default the bridge + the unit tests use): a `ConfigWriter` instance is bound via
    `bind(writer)`; calls go straight to its methods. The bridge process constructs ONE writer over the
    live store at startup (no extra network hop for the localhost-only writer); the unit tests bind a
    writer over an ISOLATED scratch store + scratch HOME (no live config touched, lead-only law).
  · HTTP (the deployed-service path): if no in-process writer is bound, calls POST to the
    config_writer service at 127.0.0.1:$COMPANY_CONFIG_WRITER_PORT (default 8772) — the same routes
    (`/read /write /cli /git /consent`). A down service FAILS LOUD with a teaching error (no silent
    fallback, no fabricated success — no-silent-failures).

EITHER mode, the config_writer is the SOLE writer of `.claude`/host config and the only thing that
shells the native config CLI. The handler never crosses the floor.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

# the in-process writer (bound by the bridge / the unit tests). None → HTTP mode.
_WRITER = None


def bind(writer) -> None:
    """Bind an in-process ConfigWriter (the bridge at startup; a test with a scratch writer). Pass None
    to clear (return to HTTP mode)."""
    global _WRITER
    _WRITER = writer


def bound() -> bool:
    return _WRITER is not None


def _base() -> str:
    port = os.environ.get("COMPANY_CONFIG_WRITER_PORT", "8772")
    return f"http://127.0.0.1:{port}"


class R3Unavailable(Exception):
    """The R3 config_writer service is unreachable AND no in-process writer is bound — a teaching error
    (no silent fallback). The faces surface this; it names how to bring the service up."""


def _http(path: str, payload: dict, timeout: float = 30.0) -> dict:
    url = _base() + path
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        # the service answered with a 4xx/5xx teaching error — surface its body verbatim (fail loud).
        try:
            body = json.loads(e.read() or b"{}")
        except Exception:
            body = {"error": f"HTTP {e.code}"}
        body.setdefault("ok", False)
        body.setdefault("http_status", e.code)
        return body
    except (urllib.error.URLError, ConnectionError, OSError) as e:
        raise R3Unavailable(
            f"the R3 config_writer service ({_base()}) is not reachable ({e}). It is the SOLE writer of "
            f".claude/host config + the only process that shells `claude mcp`/`claude plugin` + git/gh. "
            f"Bring it up: `company up config-writer` (on-demand). No silent fallback — this write/read "
            f"is refused loud until the rail is live.") from e


# ── the four config_writer ops the ③ handlers route through (in-process OR http, one law) ──

def read(**payload) -> dict:
    if _WRITER is not None:
        return _WRITER.read(**payload)
    return _http("/read", payload)


def write(**payload) -> dict:
    if _WRITER is not None:
        return _WRITER.write(**payload)
    return _http("/write", payload)


def cli(**payload) -> dict:
    if _WRITER is not None:
        return _WRITER.cli(**payload)
    return _http("/cli", payload)


def git(**payload) -> dict:
    if _WRITER is not None:
        return _WRITER.git(**payload)
    return _http("/git", payload)


def consent(klass: str, grant: bool) -> dict:
    if _WRITER is not None:
        return _WRITER.set_consent(klass, grant)
    return _http("/consent", {"class": klass, "grant": grant})
