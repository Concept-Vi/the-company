#!/usr/bin/env python3
"""design/_system/blueprint_emit.py — assemble the importable blueprint (B1) + the
filesystem-as-graph layout (B3) FROM the corpus, deterministically.

GENERATES (never hand-edit the outputs):
  design/blueprint/component-inventory.json   — every UI region/element → the component that renders it
  design/blueprint/surfaces/<home-journey>/<view-id>.json
                                              — per-view surface-spec. Directory layout = the journey SPINE
                                                (tree=structure); cross-journey edges carried as
                                                `journeys[]` + `cross_journeys[]` address-refs (the web the
                                                tree can't hold). This SAME directory is what navgraph.py
                                                reads back (B3).

SOURCE OF TRUTH (read-only here):
  design/register.json            — views · features · sequences(journeys) · areas
  design/_system/addresses.json   — the ui:// address registry (S0/S1 union rows)

LAW (design/CLAUDE.md): edit data not generated files; never invent an address; no fiction
(only register.json views/features). The home-journey rule + the cross-edge rule are deterministic so the
graph is reconstructible (B3). Re-run after register.json / addresses.json changes:
    python3 design/_system/blueprint_emit.py
Run from the repo root OR the design folder (paths are resolved relative to this file).
"""
import os, json, sys

HERE = os.path.dirname(os.path.abspath(__file__))          # design/_system
DESIGN = os.path.dirname(HERE)                              # design
REGISTER = os.path.join(DESIGN, "register.json")
ADDRESSES = os.path.join(HERE, "addresses.json")
BLUEPRINT = os.path.join(DESIGN, "blueprint")
SURFACES = os.path.join(BLUEPRINT, "surfaces")

# region -> the component file that actually renders it (post-F0 carve), with build status.
# Built rows MUST point at a real file under canvas/app/src; planned rows carry no path (status gates the
# existence assertion in blueprint_acceptance.py — honest, not fiction).
REGION_COMPONENT = {
    "toolbar":    {"component": "canvas/app/src/regions/Toolbar.tsx",    "status": "built"},
    "rail":       {"component": "canvas/app/src/regions/Palette.tsx",    "status": "built"},
    "canvas":     {"component": "canvas/app/src/App.tsx",                "status": "built",
                   "note": "canvas + nodes render in App.tsx via tldraw + NodeShape.tsx"},
    "inspector":  {"component": "canvas/app/src/regions/Inspector.tsx",  "status": "built"},
    "inbox":      {"component": "canvas/app/src/regions/Inbox.tsx",      "status": "built"},
    "chat":       {"component": "canvas/app/src/regions/RhmChat.tsx",    "status": "built"},
    "activity":   {"component": "canvas/app/src/regions/Activity.tsx",   "status": "built"},
    "walkthrough":{"component": "canvas/app/src/regions/Walkthrough.tsx","status": "built"},
    "workshop":   {"component": "canvas/app/src/regions/Workshop.tsx",   "status": "built"},
    "models":     {"component": None,                                    "status": "planned",
                   "note": "fleet surface (F8) — not yet a dedicated component"},
    "tabbar":     {"component": None,                                    "status": "planned",
                   "note": "mobile bottom-nav — rendered inline in App.tsx shell; no dedicated file yet"},
    "twin":       {"component": None,                                    "status": "planned",
                   "note": "twin surface (B6 mockup) — not yet carved into a region component"},
}

# shared components (not region-keyed) the builder reuses — assert these exist too.
SHARED_COMPONENTS = [
    {"name": "PanelView",         "component": "canvas/app/src/components/PanelView.tsx",        "status": "built"},
    {"name": "PanelErrorBoundary","component": "canvas/app/src/components/PanelErrorBoundary.tsx","status": "built"},
    {"name": "NodeConfigForm",    "component": "canvas/app/src/components/NodeConfigForm.tsx",    "status": "built"},
    {"name": "BuildIntentCard",   "component": "canvas/app/src/components/BuildIntentCard.tsx",   "status": "built"},
    {"name": "NodeShape",         "component": "canvas/app/src/NodeShape.tsx",                    "status": "built"},
]


def load():
    reg = json.load(open(REGISTER))
    addr = json.load(open(ADDRESSES))["addresses"]
    return reg, addr


def jnum(j):
    """J7 -> 7 (sortable journey id)."""
    return int(j[1:])


def view_journey_membership(reg):
    """For each view: the set of journeys whose sequence STEPS contain it (the authoritative edge source).
    Returns {view_id: sorted-list-of-journey-ids}. Empty list = an unrouted view (in no journey)."""
    seqs = {s["id"]: s for s in reg["sequences"]}
    appears = {}
    for jid in sorted(seqs, key=jnum):
        for step in seqs[jid]["steps"]:
            appears.setdefault(step, set()).add(jid)
    return {v["id"]: sorted(appears.get(v["id"], set()), key=jnum) for v in reg["views"]}


def home_journey(view_id, membership):
    """The tree home = the lowest-numbered journey the view's STEPS appear in (deterministic spine home).
    Unrouted views (no journey) → '_unrouted' (in the tree, outside the journey graph)."""
    js = membership[view_id]
    return js[0] if js else "_unrouted"


def addresses_for_view(view, addr):
    """Join a view to its registered ui:// addresses by feature-id (`represents`), region as fallback.
    Returns (addresses[], gap_note|None). A view with reps but no registered address is a flagged GAP —
    surfaced, never fabricated into an invented address."""
    feat2addr = {}
    reg2addr = {}
    for a, rec in addr.items():
        feat2addr.setdefault(rec.get("represents"), []).append(a)
        reg2addr.setdefault(rec.get("region"), []).append(a)
    reps = view.get("represents", [])
    hits = []
    for rp in reps:
        hits += feat2addr.get(rp, [])
    # region fallback: view area letter lower-cased rarely == region; only use explicit represents hits.
    hits = sorted(dict.fromkeys(hits))  # de-dupe, stable
    gap = None
    if reps and not hits:
        gap = f"view {view['id']} represents {reps} but no registered ui:// address joins by feature-id"
    return hits, gap


def build_component_inventory(addr):
    """Every region/element address → the component that renders it. The inventory the blueprint hands the
    builder: 'these addresses live in these components.'"""
    from collections import defaultdict
    by_region = defaultdict(list)
    for a, rec in addr.items():
        by_region[rec["region"]].append(a)
    regions = []
    for region in sorted(by_region):
        ci = REGION_COMPONENT.get(region, {"component": None, "status": "planned",
                                           "note": "region in addresses.json with no component mapping"})
        regions.append({
            "region": region,
            "component": ci["component"],
            "status": ci["status"],
            **({"note": ci["note"]} if ci.get("note") else {}),
            "addresses": sorted(by_region[region]),
        })
    return {
        "_what": "GENERATED by blueprint_emit.py. Every UI region (and its ui:// addresses) → the React "
                 "component that renders it (post-F0 carve). status=built rows point at a real file under "
                 "canvas/app/src (blueprint_acceptance.py asserts existence); status=planned rows have no "
                 "component yet (honest — not fiction).",
        "regions": regions,
        "shared_components": SHARED_COMPONENTS,
    }


def build_surface_spec(view, reg, addr, membership):
    """One per-view surface-spec: what the view IS, the addresses it carries (tree=structure), and the
    journey edges (cross_journeys[] = the address-refs the tree can't hold)."""
    vid = view["id"]
    js = membership[vid]
    home = home_journey(vid, membership)
    cross = [j for j in js if j != home]   # the cross-edges the tree drops; refs restore them
    addrs, gap = addresses_for_view(view, addr)
    spec = {
        "_what": f"GENERATED surface-spec for view {vid}. Directory = journey spine (tree); journeys[]/"
                 f"cross_journeys[] = the address-refs that carry the web (B3). Built by a Claude Code "
                 f"session to the addresses below (never invent an address).",
        "id": vid,
        "area": view.get("area"),
        "title": view.get("title"),
        "platforms": view.get("platforms", []),
        "represents": view.get("represents", []),
        "status": view.get("status"),
        "home_journey": home,
        "journeys": js,                    # ALL journeys this view belongs to (the full membership)
        "cross_journeys": cross,           # journeys OTHER than home (the cross-edges; the web)
        "addresses": addrs,                # the registered ui:// addresses the view carries
        "build_to": {
            # regions touched: ui://<region>/... -> <region>
            "components": sorted({a[len("ui://"):].split("/")[0] for a in addrs}),
            "design_lint": "check.py --target canvas/app/src --fail-on  (the FORM gate)",
            "tokens": "design/_system/tokens.json → design-system.css (the only look-source)",
        },
    }
    if gap:
        spec["address_gap"] = gap
    return spec


def emit():
    reg, addr = load()
    membership = view_journey_membership(reg)

    # clean + rebuild the surfaces tree (generated; safe to wipe)
    if os.path.isdir(SURFACES):
        import shutil
        shutil.rmtree(SURFACES)
    os.makedirs(SURFACES, exist_ok=True)

    written = []
    gaps = []
    for view in reg["views"]:
        home = home_journey(view["id"], membership)
        jdir = os.path.join(SURFACES, home)
        os.makedirs(jdir, exist_ok=True)
        spec = build_surface_spec(view, reg, addr, membership)
        if "address_gap" in spec:
            gaps.append(spec["address_gap"])
        path = os.path.join(jdir, f"{view['id']}.json")
        with open(path, "w") as f:
            json.dump(spec, f, indent=2)
        written.append(os.path.relpath(path, DESIGN))

    # component inventory
    os.makedirs(BLUEPRINT, exist_ok=True)
    inv = build_component_inventory(addr)
    with open(os.path.join(BLUEPRINT, "component-inventory.json"), "w") as f:
        json.dump(inv, f, indent=2)

    home_dirs = {os.path.relpath(p, os.path.relpath(SURFACES, DESIGN)).split(os.sep)[0] for p in written}
    print(f"blueprint_emit: wrote {len(written)} surface-specs across "
          f"{len(home_dirs)} home dirs ({', '.join(sorted(home_dirs))}) + component-inventory.json")
    if gaps:
        print(f"  {len(gaps)} address-gap(s) flagged (view with reps but no registered address):")
        for g in gaps:
            print(f"    - {g}")
    return written, inv, gaps


if __name__ == "__main__":
    emit()
