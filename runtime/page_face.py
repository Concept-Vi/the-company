"""runtime/page_face.py — page-as-a-face: a rendered HTML page bound to an address (the strong artifact).

Tim's idea (2026-06-25→28): the Company should host rendered pages the way claude.ai hosts artifacts —
but BETTER, by binding a page to an ADDRESS (the accumulation idea) instead of a flat dead copy. A page
is then just another optional FIELD an address carries (`UnionAddressRecord.page`, v3), served live on
the Company's own surface. This generalises "the gallery is the visible surface" so EVERY address can
have a visible face, not only designs.

## The security posture (built IN, by construction — the 3-review verdict's hard gates)
The security review found two CRITICALs in naively serving stored HTML: (1) same-origin privilege
escalation — a page served on the bridge's control-plane origin could `fetch('/api/…')` and mutate the
system; (2) the bridge has no transport auth. This module is safe BY CONSTRUCTION against both, without
depending on the (deferred-to-Supabase) auth work:
  - **SEPARATE ORIGIN** — pages serve on their OWN port (`PAGE_PORT`, default 8774), NEVER the bridge
    control plane (8770) / supervisor (8771). A browser cannot cross-origin `fetch` the control plane.
  - **NO-SCRIPT CSP** — every page is served under a Content-Security-Policy with NO `script-src` and
    `connect-src 'none'`: no JavaScript executes and no network call can be made FROM a page, so even a
    hostile stored page can neither run JS nor reach any API. (Pages are static design artifacts —
    HTML+CSS — so this costs nothing real.)
  - **SCHEME ALLOW-LIST** — a page's `source` must be CONTENT-ADDRESSED (`cas://`/`blob://` — immutable,
    Tim/system-authored). A `run://`/`skill://`/arbitrary source is REFUSED fail-loud (never served).
  - **FAIL-LOUD** — no binding → 404; disallowed scheme → 403; both explicit, never a silent empty.
Auth (who may reach the page port at all) rides the later Supabase move; on the local-only host now, the
separate-origin + no-script CSP are the load-bearing mitigations and they hold regardless of auth.

## The shape
- A page CONTENT lives at a content-addressed source (`store.put_content(html) -> cas://…`).
- A BINDING (address → {source, title?, content_type}) lives in an overlay (`design/_system/
  page_bindings.json`) — the writable per-address `page` field (the corpus `addresses.json` is
  build-generated; the overlay is the hand/agent-writable accumulation home). `UnionAddressRecord.page`
  reads it.
- `attach_page` writes the blob + the binding; `render_page` resolves + serves; `serve` is the live
  separate-origin server.

LAWS honoured: no silent failures (404/403 loud) · the floor (a page is READ-served; no execution — the
no-script CSP enforces it) · content-addressed-immutable sources only · reuse (rides the store's
put_content/get_content, the cas:// the whole system uses) · additive (the `page` field is optional, v3).
"""
from __future__ import annotations

import json
import os

from contracts.ui_info import parse_ui_address

# --- ports (separate-origin law — NEVER the control plane) ----------------------------------------
PAGE_PORT = 8774          # the page-face origin. bridge=8770 (control plane), supervisor=8771 — distinct.

# --- the no-script CSP (kills script execution + any network call FROM a page, by construction) ----
PAGE_CSP = ("default-src 'none'; img-src 'self' data:; style-src 'unsafe-inline'; font-src data:; "
            "media-src 'self' data:; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")

# --- the page-source scheme allow-list (content-addressed/immutable only) --------------------------
ALLOWED_PAGE_SCHEMES = ("cas", "blob")

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DEFAULT_BINDINGS = os.path.join(_REPO_ROOT, "design", "_system", "page_bindings.json")


class PageFaceError(Exception):
    """A page could not be attached or served safely (bad address, disallowed source). Loud."""


def _scheme(src: str) -> str:
    return src.split("://", 1)[0] if isinstance(src, str) and "://" in src else ""


def _validate_address(address: str) -> None:
    """A page can be the face of ANY addressed thing — not just a ui:// element (Tim, 2026-06-28: the
    interactive addressed surface + page-face are for everything else too, not only UI). So we validate
    the address is WELL-FORMED with a KNOWN scheme (registry-is-truth, contracts.address.SCHEMES), not
    that it is specifically ui://. A `ui://` still gets its richer shape-validation (parse_ui_address)."""
    from contracts.address import SCHEMES
    sch = _scheme(address)
    if not sch:
        raise PageFaceError(f"attach_page: {address!r} is not an address (no '<scheme>://') — fail loud.")
    if sch not in SCHEMES:
        raise PageFaceError(
            f"attach_page: unknown address scheme {sch!r} in {address!r} — known schemes are {list(SCHEMES)} "
            f"(registry-is-truth; a page is the face of an ADDRESSED thing, so its address must be real).")
    if sch == "ui":
        parse_ui_address(address)                          # ui:// keeps its richer grammar validation


def _load_bindings(bindings_path: str) -> dict:
    if not os.path.exists(bindings_path):
        return {}
    with open(bindings_path, encoding="utf-8") as f:
        return json.load(f)


def attach_page(suite, address: str, html: str, *, title: str | None = None,
                bindings_path: str | None = None) -> dict:
    """Bind a rendered HTML page to `address` (ANY addressed thing — a ui:// element, a skill://, a
    run:// output, anything in SCHEMES). Stores the HTML as an immutable content-addressed object
    (`cas://`) and records the binding in the overlay (the address's `page` field). Returns the binding.
    FAIL LOUD on a malformed/unknown-scheme address or empty html (never bind an empty/invalid page)."""
    _validate_address(address)                            # any well-formed, known-scheme address
    if not isinstance(html, str) or not html.strip():
        raise PageFaceError(f"attach_page({address!r}): html must be non-empty — never bind an empty page.")
    bindings_path = bindings_path or _DEFAULT_BINDINGS
    cas = suite.store.put_content(html)                    # immutable, dedup'd — the page content's home
    binding = {"source": cas, "title": title, "content_type": "text/html"}
    bindings = _load_bindings(bindings_path)
    bindings[address] = binding
    os.makedirs(os.path.dirname(bindings_path), exist_ok=True)
    tmp = bindings_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(bindings, f, indent=2, sort_keys=True)
    os.replace(tmp, bindings_path)                         # atomic
    return {"address": address, **binding}


def page_for(suite, address: str, *, bindings_path: str | None = None) -> dict | None:
    """The page binding for an address (its `page` field), or None if it has no page."""
    return _load_bindings(bindings_path or _DEFAULT_BINDINGS).get(address)


def list_pages(suite, *, bindings_path: str | None = None) -> list:
    """Every address that currently carries a page face, with its binding — the page registry view."""
    b = _load_bindings(bindings_path or _DEFAULT_BINDINGS)
    return [{"address": a, **rec} for a, rec in sorted(b.items())]


def _resolve_source(suite, source: str) -> str:
    """Resolve a content-addressed page source to its HTML string. ALLOW-LIST enforced: only
    `cas://`/`blob://` (immutable) — anything else is REFUSED fail-loud (never serve a run://-derived or
    arbitrary source as a page)."""
    sch = _scheme(source)
    if sch not in ALLOWED_PAGE_SCHEMES:
        raise PageFaceError(
            f"page source {source!r}: scheme {sch!r} is not allowed — a page source must be content-"
            f"addressed/immutable ({list(ALLOWED_PAGE_SCHEMES)}). Refused (never serve an arbitrary source).")
    if sch == "cas":
        return suite.store.get_content(source)
    return suite.store.get_blob(source).decode("utf-8")    # blob:// — bytes → text


def render_page(suite, address: str, *, bindings_path: str | None = None) -> tuple:
    """PURE render: resolve an address's page → (status, headers, body). No socket — the live `serve`
    and the tests both call this. 404 (no binding) and 403 (disallowed scheme) are explicit/loud.
    Every 200 carries the no-script CSP + nosniff (the by-construction mitigations)."""
    binding = page_for(suite, address, bindings_path=bindings_path)
    base_headers = {
        "Content-Security-Policy": PAGE_CSP,
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "no-referrer",
        "Cross-Origin-Resource-Policy": "same-origin",
    }
    if not binding:
        return (404, {**base_headers, "Content-Type": "text/plain; charset=utf-8"},
                f"no page bound to {address} (fail-loud, never a silent empty)")
    try:
        html = _resolve_source(suite, binding["source"])
    except PageFaceError as e:
        return (403, {**base_headers, "Content-Type": "text/plain; charset=utf-8"}, str(e))
    return (200, {**base_headers, "Content-Type": "text/html; charset=utf-8"}, html)


def serve(suite, host: str = "127.0.0.1", port: int = PAGE_PORT, *, bindings_path: str | None = None):
    """The LIVE page-face server — a SEPARATE-ORIGIN HTTP server (never the control plane). Route:
    GET /page?addr=<ui://…>. Binds 127.0.0.1 only (local exposure law). This is the live wiring; the
    pure logic is render_page (fully tested). Running it against a browser is the lead-verify slice."""
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from urllib.parse import urlparse, parse_qs

    class _Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path != "/page":
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"page-face: GET /page?addr=<ui://...>")
                return
            addr = (parse_qs(parsed.query).get("addr") or [""])[0]
            status, headers, body = render_page(suite, addr, bindings_path=bindings_path)
            self.send_response(status)
            for k, v in headers.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body.encode("utf-8") if isinstance(body, str) else body)

        def log_message(self, *a):                        # quiet (the bridge owns request logging)
            pass

    httpd = ThreadingHTTPServer((host, port), _Handler)
    return httpd
