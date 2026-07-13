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

    # (LAYER 2 body — filled in when enforcement lands: spin the bridge on a tmp port, POST a
    #  consequential route w/o a token → assert 403 + teaching body naming the route; POST a FREE route
    #  → assert it runs; POST a consequential route WITH a minted token → assert it runs.)
    check("LAYER 2 enforcement asserted", False, "layer-2 body not yet implemented — lead's wiring landed?")
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
