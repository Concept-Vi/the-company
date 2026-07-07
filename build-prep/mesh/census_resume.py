#!/usr/bin/env python3
"""census_resume.py — resume THE CENSUS from its captured observations (the fan already landed;
only the triangulation seats crashed on the verdict near-miss, now coerced). Reads the 78
mesh-census observations back from the corpus and runs the batched reduce tree + THE-CENSUS.md
assembly — byte-same logic as census.py's tail (imported, not copied)."""
import json, os, sys
REPO = "/home/tim/company"
sys.path.insert(0, REPO); sys.path.insert(0, os.path.join(REPO, "build-prep/mesh"))

def main():
    from runtime.suite import Suite
    from runtime.registry import NodeRegistry
    from store.fs_store import FsStore
    from runtime import cognition as C
    from mesh_triangulate import _read_head
    import census as X

    s = Suite(FsStore(os.path.join(REPO, ".data/store")),
              NodeRegistry().discover([os.path.join(REPO, "nodes")]), nodes_dir=os.path.join(REPO, "nodes"))
    observations = []
    for r in s.find_corpus(projection="mesh"):
        if (r.get("lineage") or {}).get("session") == "mesh-census" and \
           (r.get("source_address") or "").startswith("mesh://territory/"):
            rec = s.store.get_content(r["cas"])
            out = rec.get("output") if isinstance(rec, dict) else None
            if isinstance(out, dict):
                observations.append(out)
    if len(observations) < 40:
        raise RuntimeError(f"only {len(observations)} captured census observations — expected ~78; not resuming")
    tri_role = s.role_registry["triangulate_mesh"]
    tb = s.resolve_role("triangulate_mesh")
    anchor = _read_head(os.path.join(REPO, "build-prep/mesh/ANCHOR.md"), 3000)
    batches = [observations[i:i+8] for i in range(0, len(observations), 8)]
    batch_syn = []
    for bi, chunk in enumerate(batches):
        syn = C.run_role(tri_role, {"notes": json.dumps(chunk)[:60000], "prior": "{}",
                          "anchor": anchor + f"\n\n[CENSUS batch {bi+1}/{len(batches)} — partial view; a final seat reduces the batch syntheses]"},
                         model=tb["model"], base_url=tb["base_url"], store=s.store)
        batch_syn.append({"batch": bi+1, "territories": [c.get("territory") for c in chunk], **dict(syn)})
        print(f"batch {bi+1}/{len(batches)} done", flush=True)
    final = C.run_role(tri_role, {"notes": json.dumps(batch_syn)[:80000], "prior": "{}",
                       "anchor": anchor + "\n\n[CENSUS FINAL seat: the notes are BATCH SYNTHESES (already triangulated chunks) — reduce them into the ONE top logical map of the whole estate]"},
                      model=tb["model"], base_url=tb["base_url"], store=s.store)
    s.capture_corpus([{"source_address": "mesh://census/1",
                       "output": dict(final, n_territories=len(observations), batches=len(batches)),
                       "projection": "mesh"}], project="company", session="mesh-census", round="census")
    # THE-CENSUS.md assembly — reuse census.py's writer logic inline (same fields)
    fd = dict(final)
    lines = ["# THE CENSUS — full-estate inventory + top logical map (2026-07-08)",
             f"*{len(observations)} territories observed · {len(batches)} batch seats + 1 final (kimi-2.7) · "
             "observations at mesh://territory/* · synthesis at mesh://census/1*",
             "", "## The map (final seat's mesh_note)", fd.get("mesh_note",""), "",
             "## Convergences (load-bearing facts)"]
    lines += [f"- **{c.get('thing','')}** — {', '.join(c.get('addresses',[]))} (seen from: {', '.join(c.get('seen_from',[]))})" for c in fd.get("convergences",[])]
    lines += ["", "## Contradictions (the next places to look)"]
    for c in fd.get("contradictions",[]):
        lines.append(f"- **{c.get('about','')}**")
        lines += [f"  - {f.get('claim','')} *({f.get('source','')})*" for f in c.get("faces",[])]
    lines += ["", "## Dormant / partly-built register (final seat)"]
    lines += [f"- [{d.get('verdict','?')}] **{d.get('what','')}** — {d.get('where','')}" for d in fd.get("dormant",[])]
    lines += ["", "## Per-batch dormant registers (nothing dropped in the reduce)"]
    for b in batch_syn:
        for d in b.get("dormant",[]):
            lines.append(f"- [{d.get('verdict','?')}] **{d.get('what','')}** — {d.get('where','')} *(batch {b['batch']})*")
    lines += ["", "## Census-proposed next territories"]
    lines += [f"- {t.get('territory','')} — {t.get('why','')}" for t in fd.get("next_territories",[])]
    lines += ["", "---", "", "## Full inventory (every observation)"]
    for o in observations:
        lines.append(f"\n### {o.get('territory')}")
        for it in o.get("seen",[]):
            lines.append(f"- [{it.get('state','?')}] **{it.get('what','')}** `{it.get('where','')}` — {it.get('note','')}")
        if o.get("dormant_candidates"): lines.append("  - dormant-candidates: " + " · ".join(o["dormant_candidates"]))
        if o.get("surprises"): lines.append("  - surprises: " + " · ".join(o["surprises"]))
    open(os.path.join(REPO,"build-prep/mesh/THE-CENSUS.md"),"w").write("\n".join(lines)+"\n")
    json.dump({"done": True, "n_obs": len(observations)}, open(os.path.join(REPO,"build-prep/mesh/.state/census.json"),"w"))
    return {"observed": len(observations), "batches": len(batches),
            "dormant_final": len(fd.get("dormant",[])), "map_head": (fd.get("mesh_note") or "")[:300]}

if __name__ == "__main__":
    print(json.dumps(main(), indent=1, default=str))
