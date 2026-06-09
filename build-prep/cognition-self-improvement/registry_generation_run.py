#!/usr/bin/env python3
"""registry_generation_run.py — COMPOSITION (V-A / RG10) the registry-generation convergence, the
REUSABLE MANUAL form of design/_system/registry-generation.cascade.json (parallels exocortex_ingest.py).

WHY MANUAL, not run_cascade: the cascade spec's own _validation note flags run_cascade('registry-generation')
as SHAPE-VALID but NOT end-to-end runnable — three open [C] engine seams: (1) the resolve-once shared
exemplars/inventory ctx, (2) the {mockup}-keyed screen_reader ground wiring, (3) the confirm jury+refcheck
firing (vs a single run_role). This module SUPPLIES all three MANUALLY — which IS the spec for what the
engine seam must later auto-thread (the bounded run is the convergence proof + the seam's executable
reference). The manual threads:
  · GROUND  : run_role(screen_reader) on the mockup -> one at-altitude summary (seam 2, single-mockup form).
  · exemplars+inventory : real addresses.json entries + register.json feature ids + the capability vocab,
                          delivered ONCE via run_items' shared ctx (seam 1, the resolve-once vehicle).
  · the {mockup} input  : threaded as a BARE-NAME `ground` shared input (an in-memory role variant) — the
                          manual form of the unbuilt run://<turn>/screen_reader/{mockup} chaining.
  · CONFIRM : run_jury(confirm_registration) per reconciled dossier + confirm_status() two-layer combine
                          (seam 3, the jury+refcheck firing).

THE CHAIN (RG3-RG6): GROUND -> MAP(run_items register_element x N) -> REDUCE(run_reduce cluster dedup) ->
CONFIRM(per-cluster representative: run_jury + the deterministic refcheck floor) -> {confirmed, flagged}.
NO-CONFIDENCE (G16): register_element now emits a `grounding` TAG (built|proposed|uncertain|defer), never a
float. FLAG-don't-drop: a floor-fail or non-built grounding marks for extra operator scrutiny, never dropped.
THE FLOOR: pure run:// computation — PROPOSES; never resolve/approve/dispatch (RG8 PROPOSE / RG9 WRITE-BACK
are the operator-gated path AFTER this lands its confirmed set). Operator-only.
"""
import os, sys, json
sys.path.insert(0, "/home/tim/company")

EXEMPLAR_KEYS = ["ui://inbox", "ui://inbox/coa", "ui://inbox/build-review", "ui://inbox/walk", "ui://toolbar"]


def _load_suite():
    from runtime.suite import Suite
    from runtime.registry import NodeRegistry
    from store.fs_store import FsStore
    return Suite(FsStore(".data/store"), NodeRegistry().discover(["nodes"]), nodes_dir="nodes")


def _grounding_payload(exemplar_keys):
    addrs = json.load(open("design/_system/addresses.json"))["addresses"]
    exemplars = "\n".join(f"{k} -> {json.dumps(addrs[k])}" for k in exemplar_keys if k in addrs)
    fids = [f["id"] for f in json.load(open("design/register.json")).get("features", [])]
    inventory = ("ALLOWED CAPABILITIES (choose ONLY from): pointable, spotlit, presentable, openable, driven\n"
                 "ALLOWED FEATURE IDS for maps_to_feature — copy ONE of these VERBATIM, else the literal "
                 "'proposed':\n" + ", ".join(fids))
    return exemplars, inventory, set(fids)


def _unit_of(c):
    return (f"ELEMENT visible_text: {c.get('visible_text','')!r}\n"
            f"tag: {c.get('tag')}  selector: {c.get('selector')}\n"
            f"parent registered address: {c.get('ancestor_address')}\n"
            f"parent dossier: {c.get('ancestor_dossier')}\n"
            f"HTML: {c.get('outerHTML','')[:600]}")


def run_registry_generation(suite, *, mockup, max_candidates=None, exemplar_keys=EXEMPLAR_KEYS,
                            turn="rg10", verbose=True):
    """The manual registry-generation convergence over ONE mockup. Returns the full artifact dict."""
    from runtime import cognition as C
    from runtime.roles import RoleRegistry, Role
    import importlib.util

    rr = RoleRegistry().discover(["roles"])
    reg, sr, conf, reduce_role = (rr.get("register_element"), rr.get("screen_reader"),
                                  rr.get("confirm_registration"), rr.get("reduce_synth"))
    # in-memory variant: thread `ground` as a BARE-NAME shared input (manual form of the {mockup} seam)
    spec2 = dict(reg.spec); spec2["input_addresses"] = ("utterance", "ground", "exemplars", "inventory")
    reg_v = Role(id=reg.id, spec=spec2, prompt_template=reg.prompt_template, output_schema=reg.output_schema,
                 mode_scope=reg.mode_scope, draws=reg.draws, op=reg.op)
    cspec = importlib.util.spec_from_file_location("confirm_reg_mod", "roles/confirm_registration.py")
    cm = importlib.util.module_from_spec(cspec); cspec.loader.exec_module(cm)
    confirm_status = cm.confirm_status

    exemplars, inventory, fids = _grounding_payload(exemplar_keys)

    cands = json.load(open("design/_system/candidates.json"))["candidates"]
    sel = [c for c in cands if c.get("mockup_file") == mockup]
    if max_candidates:
        sel = sel[:max_candidates]
    if not sel:
        raise RuntimeError(f"no candidates for mockup {mockup!r}")
    units = [_unit_of(c) for c in sel]

    # 1. GROUND — screen_reader on the mockup
    mpath = os.path.join("design/mockups", mockup)
    mock = open(mpath).read()[:8000] if os.path.exists(mpath) else f"(mockup file {mpath} not found)"
    g = C.run_role(sr, {"utterance": f"MOCKUP UNDER REVIEW ({mockup}):\n{mock}"}, store=suite.store, max_tokens=300)
    ground = json.dumps(g)
    if verbose:
        print(f"[GROUND] {mockup}: {g.get('what_this_is','')[:120]}", flush=True)

    # 2. MAP — register_element over N candidates, grounding via shared ctx
    res = C.run_items(reg_v, units, suite.store, turn_id=f"{turn}-map",
                      ctx={"ground": ground, "exemplars": exemplars, "inventory": inventory}, max_tokens=400)
    resolved = res.resolved if isinstance(res.resolved, dict) else {i: v for i, v in enumerate(res.resolved)}
    if verbose:
        print(f"[MAP] {len(resolved)}/{len(units)} dossiers (failed={len(getattr(res,'failed',[]) or [])})", flush=True)

    # 3. REDUCE — cluster dedup (the same surface recurring collapses to one)
    red = C.run_reduce(res.addresses, suite.store, turn_id=f"{turn}-reduce", mode="cluster",
                       role=reduce_role, cluster_threshold=0.85)
    clusters = red.joined.get("clusters", []) if isinstance(red.joined, dict) else []
    if verbose:
        print(f"[REDUCE] {len(resolved)} dossiers -> {len(clusters)} clusters", flush=True)

    # 4. CONFIRM — per-cluster REPRESENTATIVE (dedup-then-confirm): run_jury + the deterministic floor
    confirmed, flagged = [], []
    for ci, cluster in enumerate(clusters):
        rep = cluster[0]                                   # the representative unit_id of this cluster
        dossier = resolved.get(rep)
        if not dossier:
            continue
        element = units[rep] if isinstance(rep, int) and rep < len(units) else ""
        jres = C.run_jury(conf, {"utterance": json.dumps(dossier), "element": element},
                          suite.store, turn_id=f"{turn}-confirm-{ci}")
        cs = confirm_status(dossier, jres.verdict, feature_ids=fids)
        entry = {"dossier": dossier, "cluster_size": len(cluster), "cluster_members": cluster,
                 "confirm": {"status": cs["status"], "confirmed": cs["confirmed"],
                             "jury": cs["jury"], "reasons": cs["reasons"]},
                 "mockup": mockup}
        (confirmed if cs["confirmed"] else flagged).append(entry)
        if verbose:
            mark = "OK " if cs["confirmed"] else "FLAG"
            print(f"  [{mark}] {dossier.get('address')} <- {dossier.get('maps_to_feature')} "
                  f"({dossier.get('grounding')}) {cs['reasons'][:1]}", flush=True)

    return {"mockup": mockup, "ground": g, "n_candidates": len(units), "n_dossiers": len(resolved),
            "n_clusters": len(clusters), "confirmed": confirmed, "flagged": flagged,
            "map_addresses": res.addresses}


if __name__ == "__main__":
    os.chdir("/home/tim/company")
    mockup = sys.argv[1] if len(sys.argv) > 1 else "C1-inbox-desktop.html"
    maxc = int(sys.argv[2]) if len(sys.argv) > 2 else None
    s = _load_suite()
    out = run_registry_generation(s, mockup=mockup, max_candidates=maxc)
    # persist the artifact for surfacing (RG8) — a readable batch, NOT a registry write (operator-only floor)
    outdir = "build-prep/cognition-self-improvement"
    fp = os.path.join(outdir, f"rg10-batch-{mockup.replace('.html','')}.json")
    json.dump({"mockup": out["mockup"], "ground": out["ground"], "n_candidates": out["n_candidates"],
               "n_dossiers": out["n_dossiers"], "n_clusters": out["n_clusters"],
               "confirmed": out["confirmed"], "flagged": out["flagged"]},
              open(fp, "w"), indent=2)
    print(f"\n=== RG10 DONE: {out['n_candidates']} candidates -> {out['n_dossiers']} dossiers -> "
          f"{out['n_clusters']} clusters -> {len(out['confirmed'])} confirmed / {len(out['flagged'])} flagged ===")
    print(f"batch artifact: {fp}")
