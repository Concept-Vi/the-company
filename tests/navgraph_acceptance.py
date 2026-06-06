#!/usr/bin/env python3
"""tests/navgraph_acceptance.py — B3: filesystem-as-graph reconstructs register.json journeys.

Proves the tree-vs-graph tension is HELD, not cheated:
  - the DIRECTORY holds each view exactly ONCE (its home journey) — structure
  - ADDRESS-REFERENCES (each spec's cross_journeys[]) carry the cross-edges — the web
  - navgraph.py reads layout + refs → reconstructs EVERY journey's ordered step-list, EXACT-equal to
    register.json sequences[] (the production journeys contract)
  - the proof is non-trivial: the cross-journey views (reached from >1 journey) are recovered ONLY via the
    refs (they live under one dir on disk). If the tree trivially encoded the graph, this would prove nothing.

Run:  /home/tim/company/.venv/bin/python tests/navgraph_acceptance.py   (cwd = repo root)
Self-contained: reads only design/ files. Fails loud with the mismatching journey.
"""
import os, sys, json, subprocess, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESIGN = os.path.join(ROOT, "design")
SYS = os.path.join(DESIGN, "_system")
SURFACES = os.path.join(DESIGN, "blueprint", "surfaces")

PASS = 0
FAILS = []


def check(label, cond, detail=""):
    global PASS
    if cond:
        PASS += 1
        print(f"  ok  {label}")
    else:
        FAILS.append((label, detail))
        print(f"  XX  {label}" + (f"  — {detail}" if detail else ""))


def load_navgraph():
    spec = importlib.util.spec_from_file_location("navgraph", os.path.join(SYS, "navgraph.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    # ensure the surfaces tree exists (regenerate so the test is self-contained)
    r = subprocess.run([sys.executable, os.path.join(SYS, "blueprint_emit.py")],
                       capture_output=True, text=True)
    check("blueprint_emit.py runs clean (provides the surfaces tree)", r.returncode == 0,
          r.stderr.strip()[-300:])

    ng = load_navgraph()
    reg = json.load(open(os.path.join(DESIGN, "register.json")))
    seqs = {s["id"]: s for s in reg["sequences"]}

    # --- TREE INVARIANT: each view appears in EXACTLY ONE directory ---
    seen = {}
    dup = []
    for home in os.listdir(SURFACES):
        hdir = os.path.join(SURFACES, home)
        if not os.path.isdir(hdir):
            continue
        for fn in os.listdir(hdir):
            if not fn.endswith(".json"):
                continue
            vid = json.load(open(os.path.join(hdir, fn)))["id"]
            if vid in seen:
                dup.append(f"{vid} in {seen[vid]} AND {home}")
            seen[vid] = home
    check("each view lives in EXACTLY ONE directory (tree holds structure, not the graph)",
          not dup, str(dup))

    # --- the graph builds ---
    graph = ng.build_graph()
    check("graph builds: nodes + spine_edges + cross_edges present",
          graph["nodes"] and graph["spine_edges"] and graph["cross_edges"])

    # --- NON-TRIVIALITY: cross-journey views exist and are recovered via refs, not the tree ---
    # the views reachable from >1 journey per register.json sequences steps
    from collections import defaultdict
    via_steps = defaultdict(set)
    for jid, s in seqs.items():
        for st in s["steps"]:
            via_steps[st].add(jid)
    multi = {v for v, js in via_steps.items() if len(js) > 1}
    check("there ARE cross-journey views (the proof would be hollow otherwise)", len(multi) >= 1,
          f"multi-journey views: {sorted(multi)}")

    # each multi-journey view lives in ONE dir but the cross-edges restore its other memberships
    cross_view_set = {e["view"] for e in graph["cross_edges"]}
    check("every multi-journey view is recovered by a CROSS edge (the ref, not the tree)",
          multi <= cross_view_set, f"not recovered by refs: {sorted(multi - cross_view_set)}")

    # spot-proof: a recovered view physically lives in a DIFFERENT dir than the journey it's recovered into
    off_tree = []
    for e in graph["cross_edges"]:
        if e["tree_home"] == e["journey"]:
            off_tree.append(f"{e['view']} cross-edge to its OWN tree home {e['journey']}")
    check("cross edges point to journeys OTHER than the view's tree home (genuine off-tree edges)",
          not off_tree, str(off_tree))

    # --- THE RECONSTRUCTION: every journey, order-exact, equals register.json ---
    verdict = ng.match_register()
    for jid in sorted(seqs, key=ng.jnum):
        v = verdict[jid]
        check(f"journey {jid} reconstructs order-exact vs register.json sequences",
              v["match"], f"got {v['got']} expected {v['expected']}")
    check("ALL journeys reconstructed (the B3 proof)", verdict["_all"])

    # --- COMPLETENESS: every register.json sequence is reconstructed (none dropped) ---
    reconstructed = ng.reconstruct_journeys()
    missing = set(seqs) - set(reconstructed)
    check("every register.json journey is present in the reconstruction", not missing,
          f"missing: {sorted(missing)}")

    # --- ADVERSARIAL: the FILESYSTEM must be LOAD-BEARING (the anti-circularity proof) ---
    # If reconstruction re-serialised register.json's own steps, corrupting the LAYOUT (dropping the
    # cross-journey refs) would leave the match intact. It must NOT. We corrupt an isolated scratch copy of
    # the surfaces tree, point navgraph at it, and assert the affected journeys NO LONGER match register.
    import tempfile, shutil
    scratch = tempfile.mkdtemp(prefix="navgraph_adv_")
    try:
        scratch_surfaces = os.path.join(scratch, "surfaces")
        shutil.copytree(SURFACES, scratch_surfaces)
        # drop every cross_journeys ref — destroy the web; the tree alone remains
        corrupted_views = []
        for home in os.listdir(scratch_surfaces):
            hdir = os.path.join(scratch_surfaces, home)
            if not os.path.isdir(hdir):
                continue
            for fn in os.listdir(hdir):
                if not fn.endswith(".json"):
                    continue
                p = os.path.join(hdir, fn)
                s = json.load(open(p))
                if s.get("cross_journeys"):
                    corrupted_views.append(s["id"])
                s["cross_journeys"] = []
                json.dump(s, open(p, "w"), indent=2)
        check("there were cross-refs to corrupt (the adversarial test is meaningful)",
              len(corrupted_views) >= 1, f"corrupted: {corrupted_views}")

        # rebuild navgraph against the corrupted layout (monkeypatch its SURFACES + load_register stays same)
        orig = ng.SURFACES
        ng.SURFACES = scratch_surfaces
        try:
            corrupt_verdict = ng.match_register()
        finally:
            ng.SURFACES = orig
        check("corrupting the LAYOUT (dropping cross-refs) BREAKS the reconstruction "
              "(filesystem is load-bearing — NOT a circular re-read of register)",
              corrupt_verdict["_all"] is False,
              "corruption left the match intact → the proof is circular")
        # and specifically: a journey that depended on a cross-ref view now misses it
        # (e.g. J7 borrows C1/C3/B2/A5 from other dirs — losing the refs drops them)
        broke = [j for j in seqs if not corrupt_verdict[j]["match"]]
        check("at least one journey mismatches after layout corruption", len(broke) >= 1,
              f"journeys broken by corruption: {broke}")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    # restore clean reconstruction is still green (the corruption was isolated to the scratch copy)
    check("clean reconstruction still matches after the adversarial run (corruption was isolated)",
          ng.match_register()["_all"])

    print(f"\n{'ALL ' + str(PASS) + ' CHECKS PASS' if not FAILS else str(len(FAILS)) + ' CHECK(S) FAILED'}"
          " — B3 filesystem-as-graph reconstructs register.json journeys")
    if FAILS:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
