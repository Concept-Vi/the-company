"""parse.py — reads every mockup, extracts its element addresses (data-ui-ref),
ties each to its feature + code via the address registry, and flags orphans both
ways. Produces _system/element-map.json. Run: python3 parse.py

This is the join key: element ⇄ address ⇄ feature ⇄ code, shared with the running
app's ui:// scheme. Add an addressable thing = register it in addresses.json
(extend-by-registration) + carry its data-ui-ref in the mockup; re-run to refresh."""
import os, re, json

_REF = re.compile(r'data-ui-ref=["\']([^"\']+)["\']')


def build_map(screens: dict, addresses: dict) -> dict:
    """screens = {filename: html}; addresses = {address: {region, represents, code}}.
    Returns {elements:[...], orphans:{unregistered:[...], unused:[...]}, summary:{...}}."""
    elements, used = [], set()
    for name, html in screens.items():
        for addr in _REF.findall(html):
            used.add(addr)
            reg = addresses.get(addr)
            elements.append({
                "screen": name,
                "address": addr,
                "region": (reg or {}).get("region"),
                "feature": (reg or {}).get("represents"),
                "code": (reg or {}).get("code"),
                "registered": reg is not None,
            })
    unregistered = sorted({e["address"] for e in elements if not e["registered"]})
    unused = sorted(a for a in addresses if a not in used)
    return {
        "elements": elements,
        "orphans": {"unregistered": unregistered, "unused": unused},
        "summary": {
            "screens": len(screens),
            "addressed_elements": len(elements),
            "distinct_addresses_used": len(used),
            "registered_addresses": len(addresses),
            "unregistered_orphans": len(unregistered),
            "unused_orphans": len(unused),
        },
    }


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    mockdir = os.path.join(os.path.dirname(here), "mockups")
    with open(os.path.join(here, "addresses.json"), encoding="utf-8") as f:
        reg = json.load(f)
    addresses = reg.get("addresses", reg)  # tolerate {addresses:{...}} or a bare map
    screens = {}
    for fn in sorted(os.listdir(mockdir)):
        if fn.endswith(".html"):
            with open(os.path.join(mockdir, fn), encoding="utf-8") as f:
                screens[fn] = f.read()
    m = build_map(screens, addresses)
    out = os.path.join(here, "element-map.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    s = m["summary"]
    print(f"mapped -> {out}")
    print(f"  {s['addressed_elements']} addressed elements across {s['screens']} screens "
          f"({s['distinct_addresses_used']} distinct addresses)")
    print(f"  orphans: {s['unregistered_orphans']} used-but-unregistered, "
          f"{s['unused_orphans']} registered-but-unused")


if __name__ == "__main__":
    main()
