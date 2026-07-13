"""tests/bridge_write_gate_acceptance.py — B4 leg 2: the bridge consequential-write gate (SKELETON).

Co-designed (board://item-33970ac8): fabric authors this declaration+test; the lead wires enforcement
in bridge.py; fabric reviews the wiring against it. THIS is the drift-teeth + the doctrine assertion.

Two layers:
  LAYER 1 (LIVE NOW — the doctrine holds regardless of wiring): enumerate every POST route the bridge
    dispatches, and assert the manifest's FREE set is a real subset of them (no manifest rot / typo
    naming a route that doesn't exist). The consequential set = all POST routes − FREE — is derived,
    so a NEW route is consequential automatically (fail-closed); this layer proves that derivation and
    prints the consequential set for the lead to wire against.
  LAYER 2 (ACTIVATES when the lead lands enforcement): with COMPANY_OPERATOR_TOKEN_ENFORCE=1, a
    consequential POST with no/invalid X-Operator-Session must TEACH-AND-REFUSE (403 + a body naming
    the route + how to mint), and a FREE POST must run without a token. Skipped-loud until the
    enforcement seam exists (so the skeleton is honest, never a green that proves nothing).

Exit 0 = PASS · 1 = FAIL · 2 = LAYER-2-PENDING (layer 1 green, enforcement not yet wired).
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

FAIL = []


def check(name, cond, detail=""):
    print(("  ok  " if cond else "  XX  ") + name + (f"\n      {detail}" if detail and not cond else ""))
    if not cond:
        FAIL.append(name)


def _post_routes() -> set:
    """Enumerate the POST route literals from bridge.do_POST — the same path literals the dispatcher
    branches on. Regex over the do_POST region (the dispatcher is a giant if/elif over path literals;
    there is no route table to import — extracting it here is exactly why LAYER 1 exists)."""
    src = open(os.path.join(ROOT, "runtime", "bridge.py")).read()
    i = src.index("def do_POST")
    region = src[i:]
    pairs = re.findall(r'(?:self\.path == "(/api/[^"]+)"|u\.path == "(/api/[^"]+)")', region)
    return {a or b for a, b in pairs}


def main():
    from mcp_face.bridge_write_manifest import BRIDGE_FREE_POST

    routes = _post_routes()
    check("bridge exposes POST routes (enumeration works)", len(routes) > 20,
          f"found {len(routes)} — the do_POST scrape may have broken; update _post_routes")

    # LAYER 1 — the doctrine: FREE ⊆ routes; consequential = the rest (derived, fail-closed)
    stale = sorted(BRIDGE_FREE_POST - routes)
    check("every FREE entry is a real POST route (no manifest rot)", not stale,
          f"FREE names non-existent routes {stale} — a rename/removal left the manifest stale; fix here.")
    consequential = sorted(routes - BRIDGE_FREE_POST)
    check("the consequential set is non-empty + derived (a new route is gated by default)",
          len(consequential) > 0)

    # LAYER 2 — enforcement (activates when the lead's wiring lands)
    enforce_wired = os.environ.get("COMPANY_OPERATOR_TOKEN_ENFORCE") == "1" and _enforcement_present()
    if not enforce_wired:
        print(f"\n  LAYER 1 GREEN. Consequential POST routes gated-by-default ({len(consequential)}):")
        for p in consequential:
            print(f"      · {p}")
        print(f"\n  FREE (token-free) POST routes ({len(BRIDGE_FREE_POST)}): {sorted(BRIDGE_FREE_POST)}")
        print("\n  LAYER 2 PENDING — enforcement not wired yet (lead's leg). This skeleton asserts the "
              "doctrine + hands the derived consequential set to wire against; it flips to a live "
              "403-teach / free-runs assertion the moment COMPANY_OPERATOR_TOKEN_ENFORCE=1 and the "
              "gate is present.")
        if FAIL:
            print(f"\nFAIL — {len(FAIL)} failed"); sys.exit(1)
        print("\nbridge_write_gate_acceptance: LAYER 1 PASS (layer 2 pending)")
        sys.exit(2)

    # LAYER 2 body (lead-filled on landing the wiring, 2026-07-13 — fabric reviews): a LIVE ephemeral
    # bridge on a scratch port; behavior asserted, not inferred.
    import json as _json, threading, time, urllib.request, urllib.error
    from http.server import ThreadingHTTPServer
    import runtime.bridge as _bridge
    PORT = 8977

    def _req(path, method="POST", token=None, body=b"{}"):
        r = urllib.request.Request(f"http://127.0.0.1:{PORT}{path}",
                                   data=body if method == "POST" else None, method=method,
                                   headers={"Content-Type": "application/json",
                                            **({"X-Operator-Session": token} if token else {})})
        try:
            with urllib.request.urlopen(r, timeout=15) as resp:
                return resp.status, _json.loads(resp.read() or b"{}")
        except urllib.error.HTTPError as e:
            try:
                return e.code, _json.loads(e.read() or b"{}")
            except ValueError:
                return e.code, {}

    srv = ThreadingHTTPServer(("127.0.0.1", PORT), _bridge.H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    time.sleep(0.3)
    try:
        code, out = _req("/api/journey/start")
        check("consequential POST w/o token → 403 TEACH-AND-REFUSE", code == 403,
              f"expected 403, got {code}: {out}")
        check("…the refusal names the route + the manifest + the mint door",
              "/api/journey/start" in str(out) and "bridge_write_manifest" in str(out)
              and "operator-session" in str(out), f"teaching body incomplete: {out}")
        code, out = _req("/api/operator-session", method="GET")
        tok = out.get("operator_session", "")
        check("the mint door answers (GET face, ungated)", code == 200 and bool(tok), f"{code} {out}")
        code, out = _req("/api/journey/start", token=tok)
        check("the SAME consequential POST WITH the minted token runs", code == 200, f"{code} {out}")
        code, out = _req("/api/voice/log", body=b'{"event":"gate-probe"}')
        check("a FREE POST runs without a token (the voice loop never breaks on auth)",
              code == 200, f"{code} {out}")
        code, out = _req("/api/voice/log?src=probe", body=b'{"event":"q-probe"}')
        check("a FREE POST + query-string is NOT wrongly GATED (gate classifies by route, not path+query)",
              code != 403, f"gate refused a free route over a query param: {code} {out}")
        # (whether dispatch 200s or 404s on the query is the dispatcher's raw-path-match concern, NOT the
        #  gate's — the gate's sole job here is to never wrongly refuse a free route; that is what we assert.)
        code, out = _req("/api/route-invented-tomorrow")
        check("an UNDECLARED route gates fail-closed (403 before any 404)", code == 403,
              f"{code} {out}")
        code, out = _req("/api/journey/start?x=1")
        check("a CONSEQUENTIAL route + query-string still gates (strip never opens a hole)", code == 403,
              f"{code} {out}")
    finally:
        srv.shutdown()
    if FAIL:
        print(f"\nFAIL — {len(FAIL)} failed"); sys.exit(1)
    print("\nbridge_write_gate_acceptance: PASS (both layers)")
    sys.exit(0)


def _enforcement_present() -> bool:
    """Detect whether the lead's teach-and-refuse gate exists yet (so layer 2 stays honestly skipped
    until it does). Heuristic: the enforcement seam names the manifest."""
    try:
        src = open(os.path.join(ROOT, "runtime", "bridge.py")).read()
        return "bridge_write_manifest" in src or "BRIDGE_FREE_POST" in src
    except OSError:
        return False


if __name__ == "__main__":
    main()
