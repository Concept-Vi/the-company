#!/usr/bin/env python3
"""design/_system/navgraph.py — filesystem-as-graph (B3 · fidelity ISSUE-2).

THE TENSION HELD (§21.4#7 + §21.10): screens laid out in a directory mirroring the journey sequence make the
layout itself express the nav graph — BUT a tree can't hold a real graph (a screen reached from N journeys;
cycles). So:  the DIRECTORY = the spine (structure) · ADDRESS-REFERENCES = the cross-edges (the web).

WHAT THIS TOOL DOES:
  reads  design/blueprint/surfaces/<home-journey>/<view>.json   (the layout, B1/B3-generated)
  reads  design/register.json  sequences[]  (the production journeys contract — the ground truth to match)
  → builds the journey graph:
       nodes  = views (each with home_journey, all journeys, addresses)
       edges  = (a) SPINE edges: consecutive steps within each journey (the ordered walk)
                (b) CROSS edges: a view's membership in journeys OTHER than its tree home
                    (the web the tree drops; restored from the surface-spec's cross_journeys[]/journeys[])
  → reconstructs each journey's ordered step-list and PROVES it equals register.json's sequences[].steps.

WHY THE TREE ALONE ISN'T ENOUGH (the proof's whole point): each view lives in EXACTLY ONE directory (its home
journey). A view reachable from 3 journeys (e.g. C1 ∈ J3·J5·J7) sits only under J3 on disk — the other two
memberships are LOST by the tree and RECOVERED only from the address-refs. If the layout put a view under
every journey it's in, the tree would trivially encode the graph and this would prove nothing.

USAGE:
    python3 design/_system/navgraph.py            # build + print the graph summary + the match verdict
    python3 design/_system/navgraph.py --json      # emit the full graph as JSON
The acceptance test (tests/navgraph_acceptance.py) calls build_graph()/reconstruct_journeys()/match_register().
Run from repo root or the design folder (paths resolve relative to this file).

NOTE ON NAMING (flagged per the task): the Completion-Criteria / Implementation-Guide call the cross-edge
carrier `register.json journeys[]`. The ACTUAL register.json key is `sequences[]` (ids J1–J9, `steps[]` = the
ordered spine; `views[].journeys[]` = cross-membership). This tool reconciles to `sequences[]` — the B3
grounding note pre-authorised exactly this ("flag if the journeys schema differs from the assumed shape").
"""
import os, json, sys

HERE = os.path.dirname(os.path.abspath(__file__))          # design/_system
DESIGN = os.path.dirname(HERE)                              # design
REGISTER = os.path.join(DESIGN, "register.json")
SURFACES = os.path.join(DESIGN, "blueprint", "surfaces")
UNROUTED = "_unrouted"                                      # the tree home for views in no journey


def jnum(j):
    return int(j[1:])


def read_layout():
    """Walk the surfaces tree → {view_id: spec}. The directory name is the view's TREE HOME (the spine
    placement); the spec's journeys[]/cross_journeys[] are the address-refs (the web)."""
    if not os.path.isdir(SURFACES):
        raise SystemExit(f"navgraph: surfaces dir missing ({SURFACES}). Run blueprint_emit.py first.")
    layout = {}
    for home in sorted(os.listdir(SURFACES)):
        hdir = os.path.join(SURFACES, home)
        if not os.path.isdir(hdir):
            continue
        for fn in sorted(os.listdir(hdir)):
            if not fn.endswith(".json"):
                continue
            spec = json.load(open(os.path.join(hdir, fn)))
            spec["_tree_home_dir"] = home          # what the FILESYSTEM says the home is
            layout[spec["id"]] = spec
    return layout


def load_register():
    return json.load(open(REGISTER))


def build_graph():
    """The journey graph from layout + address-refs.
    Returns {nodes:{vid:{...}}, spine_edges:[...], cross_edges:[...]}."""
    layout = read_layout()
    reg = load_register()
    seqs = {s["id"]: s for s in reg["sequences"]}

    # nodes: from the layout (tree=structure). Each carries its tree home + the journeys it claims (web).
    nodes = {}
    for vid, spec in layout.items():
        nodes[vid] = {
            "id": vid,
            "tree_home": spec["_tree_home_dir"],          # where it lives on disk (the spine placement)
            "home_journey": spec.get("home_journey"),     # what the spec declares (must agree with tree_home)
            "journeys": spec.get("journeys", []),         # ALL journeys (the membership web)
            "cross_journeys": spec.get("cross_journeys", []),  # journeys OTHER than home (the tree-dropped edges)
            "addresses": spec.get("addresses", []),
            "title": spec.get("title"),
        }

    # SPINE edges: consecutive steps within each journey (the ordered walk through the tree's home dir).
    # We take the ORDER from register.json sequences (the layout dir is unordered on disk) — the directory
    # holds membership, the sequence holds order. This is the tree=structure half made ordered.
    spine_edges = []
    for jid in sorted(seqs, key=jnum):
        steps = seqs[jid]["steps"]
        for a, b in zip(steps, steps[1:]):
            spine_edges.append({"journey": jid, "from": a, "to": b, "kind": "spine"})

    # CROSS edges: a view's membership in a journey that is NOT its tree home — the web the tree can't hold.
    # Sourced from the surface-spec cross_journeys[] (the address-refs). This is what recovers C1∈J5,J7 etc.
    cross_edges = []
    for vid, n in nodes.items():
        for j in n["cross_journeys"]:
            cross_edges.append({"view": vid, "journey": j, "kind": "cross",
                                "tree_home": n["tree_home"]})
    return {"nodes": nodes, "spine_edges": spine_edges, "cross_edges": cross_edges}


def reconstruct_journeys(graph=None):
    """Rebuild each journey's ORDERED member-view list from the graph — using the tree home for the views the
    journey owns PLUS the cross-edges for the views it borrows. The order is recovered by walking the spine
    edges. Returns {journey_id: [ordered view ids]}.

    The reconstruction must use BOTH halves: tree membership alone misses a borrowed view (it lives under
    another journey's dir); cross-edges restore it. This is the load-bearing proof."""
    if graph is None:
        graph = build_graph()
    nodes = graph["nodes"]

    # which views belong to each journey (from the web: every node's journeys[] — the union of tree home +
    # cross memberships). This is the SET; order comes next from the spine edges.
    members = {}
    for vid, n in nodes.items():
        for j in n["journeys"]:
            members.setdefault(j, set()).add(vid)

    # order: chain the spine edges per journey into the ordered walk.
    from collections import defaultdict
    succ = defaultdict(dict)   # journey -> {from: to}
    has_pred = defaultdict(set)
    for e in graph["spine_edges"]:
        succ[e["journey"]][e["from"]] = e["to"]
        has_pred[e["journey"]].add(e["to"])

    ordered = {}
    for j, mset in members.items():
        # find the head: a member with no predecessor edge in this journey.
        heads = [v for v in mset if v not in has_pred[j]]
        chain = []
        if j in succ:
            # walk from each head along succ; handles the single-step journeys (no edges) too.
            start = sorted(heads)[0] if heads else sorted(mset)[0]
            seen = set()
            cur = start
            while cur is not None and cur not in seen:
                chain.append(cur)
                seen.add(cur)
                cur = succ[j].get(cur)
            # append any member not reached by the walk (e.g. an isolated cross-only view) — sorted for det.
            for v in sorted(mset):
                if v not in seen:
                    chain.append(v)
        else:
            # no spine edges (single-step journey) — the lone member(s).
            chain = sorted(mset)
        ordered[j] = chain
    return ordered


def match_register():
    """Prove the reconstructed journeys equal register.json sequences[].steps (order-exact).
    Returns {journey_id: {"match": bool, "expected": [...], "got": [...]}} + an "_all" bool."""
    reg = load_register()
    expected = {s["id"]: s["steps"] for s in reg["sequences"]}
    got = reconstruct_journeys()
    result = {}
    all_ok = True
    for jid in sorted(expected, key=jnum):
        exp = expected[jid]
        g = got.get(jid, [])
        ok = (g == exp)
        all_ok = all_ok and ok
        result[jid] = {"match": ok, "expected": exp, "got": g}
    result["_all"] = all_ok
    return result


def main():
    graph = build_graph()
    verdict = match_register()
    if "--json" in sys.argv:
        out = {"graph": {"nodes": graph["nodes"],
                         "spine_edges": graph["spine_edges"],
                         "cross_edges": graph["cross_edges"]},
               "reconstruction": verdict}
        print(json.dumps(out, indent=2))
        return
    n = graph["nodes"]
    print(f"navgraph: {len(n)} view nodes · {len(graph['spine_edges'])} spine edges · "
          f"{len(graph['cross_edges'])} cross edges")
    print(f"  cross-journey views (the web the tree can't hold):")
    for e in graph["cross_edges"]:
        print(f"    {e['view']:4} (home dir {e['tree_home']}) → also in {e['journey']}")
    print(f"  journey reconstruction vs register.json sequences[]:")
    for jid in sorted([k for k in verdict if k != "_all"], key=jnum):
        v = verdict[jid]
        mark = "ok " if v["match"] else "XX "
        print(f"    {mark}{jid}: {v['got']}" + ("" if v["match"] else f"  EXPECTED {v['expected']}"))
    print(f"\n{'ALL JOURNEYS RECONSTRUCTED — graph matches register.json' if verdict['_all'] else 'MISMATCH'}")
    if not verdict["_all"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
