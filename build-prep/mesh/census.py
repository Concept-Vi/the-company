#!/usr/bin/env python3
"""census.py — THE CENSUS: one full-coverage dragnet over the estate (Tim 2026-07-08: "bank it...
a full inventory, a top logical map of everything"). Unlike the self-steering mesh rounds (8-10
territories, evidence-chosen), this is ONE deliberate total pass: EVERY module, registry, tool
surface, ops dir, doc spine, and corpus space gets an open lens. Same primitives (gather →
observe_territory fan → capture to space='mesh' → triangulate), triangulation BATCHED (8 obs per
seat, then a final seat over the batch syntheses — a reduce tree, since 45+ observations exceed one
context). Output: THE-CENSUS.md (the top logical map + full inventory + dormant/partly-built
register) + mesh://census/1 capture. The census FEEDS the plan (PLAN.md C.3), it never builds."""
import json
import os
import re
import sys
import time

REPO = "/home/tim/company"
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "build-prep/mesh"))
from mesh_triangulate import gather, _slug, _read_head, MATERIAL_CAP  # reuse, never re-derive

OUT = os.path.join(REPO, "build-prep/mesh/THE-CENSUS.md")
STATE = os.path.join(REPO, "build-prep/mesh/.state/census.json")
OBS_TOKENS = 1600
_SKIP_DIRS = {".git", ".venv", ".data", "node_modules", "__pycache__", ".build", ".obsidian",
              ".pytest_cache", ".claude", ".recollection", ".state"}


def territories() -> list[dict]:
    """Deterministic full enumeration — every top-level dir + the doc spine + the known registries
    + the specials. The census's coverage guarantee is THIS list being derived, not curated."""
    ts, seen = [], set()

    def add(t, why):
        if t not in seen:
            seen.add(t)
            ts.append({"territory": t, "why": why})

    for n in sorted(os.listdir(REPO)):
        p = os.path.join(REPO, n)
        if os.path.isdir(p) and n not in _SKIP_DIRS and not n.startswith("."):
            add(n, "top-level module (census: full enumeration)")
        elif os.path.isfile(p) and n.endswith(".md"):
            add(n, "doc spine (census)")
    # sub-territories too coarse at top level:
    for sub, why in [("ops/systemd", "the service units"), ("ops/cli", "the company console"),
                     ("ops/hooks", "hook scripts"), ("mcp_face/tools", "agent verb surface"),
                     ("orienteering/entries", "the hand-kept terrain ledger"),
                     ("contracts/address.py", "the address spine"),
                     ("ops/services.json", "the resource registry"),
                     ("corpus-spaces", "the live substrate census")]:
        add(sub, why)
    return ts


def main() -> dict:
    from runtime.suite import Suite
    from runtime.registry import NodeRegistry
    from store.fs_store import FsStore
    from runtime import cognition as C

    s = Suite(FsStore(os.path.join(REPO, ".data/store")),
              NodeRegistry().discover([os.path.join(REPO, "nodes")]), nodes_dir=os.path.join(REPO, "nodes"))
    obs_role = s.role_registry["observe_territory"]
    tri_role = s.role_registry["triangulate_mesh"]
    ob, tb = s.resolve_role("observe_territory"), s.resolve_role("triangulate_mesh")

    ts = territories()
    units = [{"territory": t["territory"], "why": t["why"], "material": gather(t["territory"], s)}
             for t in ts]
    res = C.run_items(obs_role, units, s.store, turn_id="mesh-census",
                      model=ob["model"], base_url=ob["base_url"], max_tokens=OBS_TOKENS)
    resolved = res.resolved if isinstance(res.resolved, dict) else {}
    observations, records = [], []
    for j, out in sorted(resolved.items()):
        if isinstance(out, dict):
            terr = units[j]["territory"]
            observations.append({"territory": terr, **out})
            records.append({"source_address": f"mesh://territory/{_slug(terr)}",
                            "output": dict(out, territory=terr, round="census"),
                            "projection": "mesh"})
    if not records:
        raise RuntimeError(f"census: 0/{len(units)} observations — {res.failed}")
    s.capture_corpus(records, project="company", session="mesh-census", round="census")

    anchor = _read_head(os.path.join(REPO, "build-prep/mesh/ANCHOR.md"), 3000)
    # reduce tree: batches of 8 → batch syntheses → final synthesis over the syntheses
    batches = [observations[i:i + 8] for i in range(0, len(observations), 8)]
    batch_syn = []
    for bi, chunk in enumerate(batches):
        syn = C.run_role(tri_role,
                         {"notes": json.dumps(chunk)[:60000],
                          "prior": "{}",
                          "anchor": anchor + f"\n\n[CENSUS batch {bi+1}/{len(batches)} — partial view; "
                                             "a final seat reduces the batch syntheses]"},
                         model=tb["model"], base_url=tb["base_url"], store=s.store)
        batch_syn.append({"batch": bi + 1, "territories": [c["territory"] for c in chunk], **dict(syn)})
    final = C.run_role(tri_role,
                       {"notes": json.dumps(batch_syn)[:80000],
                        "prior": "{}",
                        "anchor": anchor + "\n\n[CENSUS FINAL seat: the notes are BATCH SYNTHESES "
                                           "(already triangulated chunks) — reduce them into the ONE "
                                           "top logical map of the whole estate]"},
                       model=tb["model"], base_url=tb["base_url"], store=s.store)
    s.capture_corpus([{"source_address": "mesh://census/1",
                       "output": dict(final, n_territories=len(observations), batches=len(batches)),
                       "projection": "mesh"}], project="company", session="mesh-census", round="census")

    # THE-CENSUS.md — deterministic assembly (the map is data, the prose is the syntheses)
    fd = dict(final)
    lines = ["# THE CENSUS — full-estate inventory + top logical map (2026-07-08)",
             f"*{len(observations)}/{len(units)} territories observed · {len(batches)} batch seats + 1 final seat "
             "(kimi-2.7) · every observation captured at mesh://territory/* · synthesis at mesh://census/1*",
             "", "## The map (final seat's mesh_note)", fd.get("mesh_note", ""), "",
             "## Convergences (load-bearing facts)"]
    lines += [f"- **{c.get('thing','')}** — {', '.join(c.get('addresses',[]))} (seen from: {', '.join(c.get('seen_from',[]))})"
              for c in fd.get("convergences", [])]
    lines += ["", "## Contradictions (the next places to look)"]
    for c in fd.get("contradictions", []):
        lines.append(f"- **{c.get('about','')}**")
        lines += [f"  - {f.get('claim','')} *({f.get('source','')})*" for f in c.get("faces", [])]
    lines += ["", "## Dormant / partly-built register"]
    lines += [f"- [{d.get('verdict','?')}] **{d.get('what','')}** — {d.get('where','')}"
              for d in fd.get("dormant", [])]
    lines += ["", "## Census-proposed next territories"]
    lines += [f"- {t.get('territory','')} — {t.get('why','')}" for t in fd.get("next_territories", [])]
    lines += ["", "---", "", "## Full inventory (every observation, deterministic dump)"]
    for o in observations:
        lines.append(f"\n### {o['territory']}")
        for it in o.get("seen", []):
            lines.append(f"- [{it.get('state','?')}] **{it.get('what','')}** `{it.get('where','')}` — {it.get('note','')}")
        if o.get("dormant_candidates"):
            lines.append("  - dormant-candidates: " + " · ".join(o["dormant_candidates"]))
        if o.get("surprises"):
            lines.append("  - surprises: " + " · ".join(o["surprises"]))
    open(OUT, "w").write("\n".join(lines) + "\n")
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    json.dump({"done": True, "ts": time.time(), "n_obs": len(observations),
               "failures": len(getattr(res, "failed", []) or [])}, open(STATE, "w"), indent=1)
    return {"territories": len(units), "observed": len(observations),
            "unit_failures": len(getattr(res, "failed", []) or []),
            "batches": len(batches), "out": OUT,
            "dormant_found": len(fd.get("dormant", [])),
            "map_head": (fd.get("mesh_note") or "")[:400]}


if __name__ == "__main__":
    print(json.dumps(main(), indent=1, default=str))
