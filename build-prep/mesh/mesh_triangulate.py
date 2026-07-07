#!/usr/bin/env python3
"""mesh_triangulate.py — the MESH TRIANGULATION loop (2026-07-07, Tim's inversion directive).

NOT plan-and-dispatch. Each round: gather real material per territory (deterministic — code does the
mechanics), fan `observe_territory` open lenses over it (cheap cloud kimi — bulk looking), capture
every observation into space='mesh' (mesh://territory/<slug>, rounds DEEPEN by re-capture), then fire
`triangulate_mesh` (frontier kimi — judgment) over ALL of this round's observations + the prior
synthesis + the anchor core. The triangulator's `next_territories` BECOME the next round's fan — the
swarm steers itself; no planner. Synthesis captured at mesh://round/<n>: the mesh's growing self-model,
readable by ANY agent via corpus(space='mesh').

Round 1 territories are seeded from the anchor's "what is already real" — after that the loop is
self-directing. Models come from the ROLES' declared bindings via resolve_role (never constants here).

Run one round:   .venv/bin/python build-prep/mesh/mesh_triangulate.py
Run N rounds:    .venv/bin/python build-prep/mesh/mesh_triangulate.py 3
"""
import json
import os
import re
import sys
import time

REPO = "/home/tim/company"
sys.path.insert(0, REPO)

STATE_DIR = os.path.join(REPO, "build-prep/mesh/.state")
STATE = os.path.join(STATE_DIR, "mesh.json")
ANCHOR = os.path.join(REPO, "build-prep/mesh/ANCHOR.md")
MATERIAL_CAP = 7000          # chars of gathered material per territory (bounded, honest-truncated)
OBS_TOKENS = 1200            # observer output budget (list-valued)
SYN_TOKENS = 2400            # triangulator output budget (think=False — the explain_role ollama lesson:
#                              hidden reasoning burns the budget -> truncation-empty; suppress it, keep the budget for output)

# Round-1 seed: concrete, gatherable territories named in the anchor's "already real" section.
SEED = [
    {"territory": "roles",                 "why": "the cognition registry — the mesh's role seats live here"},
    {"territory": "flows",                 "why": "the registered production lines — proven chains, possibly under-used"},
    {"territory": "projections",           "why": "the corpus lenses — what kinds of self-knowledge exist"},
    {"territory": "contracts/address.py",  "why": "the address spine — the mesh coordinate space"},
    {"territory": "ops/services.json",     "why": "the resource/loadout half — models, services, combos"},
    {"territory": "orienteering/entries",  "why": "the hand-kept terrain ledger — what the estate THINKS it contains"},
    {"territory": "corpus-spaces",         "why": "the live substrate — which spaces exist and how full they are"},
    {"territory": "mcp_face/tools",        "why": "the agent-facing verb surface — the doors agents actually have"},
]


def _slug(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")[:60] or "territory"


def _read_head(path: str, cap: int) -> str:
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read(cap)
    except OSError as e:
        return f"[unreadable: {e}]"


def gather(territory: str, suite) -> str:
    """Deterministic material-gathering (mechanics-to-code): a dir → listing + AGENTS.md head + file
    heads; a file → its head; 'corpus-spaces' → live space census. Unknown → corpus query fallback.
    Always bounded to MATERIAL_CAP; truncation is visible ('...[truncated]'), never silent."""
    t = territory.strip().lstrip("/")
    out = []
    if t == "corpus-spaces":
        from collections import Counter
        c = Counter(r.get("projection") or "?" for r in suite.find_corpus())
        out.append("live corpus spaces (projection -> record count):")
        out.extend(f"  {k}: {v}" for k, v in sorted(c.items(), key=lambda kv: -kv[1]))
    else:
        p = os.path.join(REPO, t)
        if os.path.isdir(p):
            names = sorted(os.listdir(p))[:120]
            out.append(f"DIR {t}/ ({len(names)} entries shown):\n  " + "\n  ".join(names))
            ag = os.path.join(p, "AGENTS.md")
            if os.path.exists(ag):
                out.append(f"\n--- {t}/AGENTS.md (head) ---\n" + _read_head(ag, 2800))
            shown = 0
            for n in names:
                fp = os.path.join(p, n)
                if os.path.isfile(fp) and n != "AGENTS.md" and shown < 4:
                    out.append(f"\n--- {t}/{n} (head) ---\n" + _read_head(fp, 900))
                    shown += 1
        elif os.path.isfile(p):
            out.append(f"FILE {t}:\n" + _read_head(p, MATERIAL_CAP - 100))
        else:
            # not a path — ask the substrate what it knows (the mesh reading itself)
            try:
                hits = suite.query_corpus(territory, k=5, space="repo")
                out.append(f"(not a path) corpus 'repo' nearest to {territory!r}:")
                out.extend(f"  {h.get('id')} score={h.get('score'):.3f}" for h in hits.get("ranked", []))
            except Exception as e:
                out.append(f"(not a path; corpus lookup failed: {e})")
    m = "\n".join(out)
    return m[:MATERIAL_CAP] + ("\n...[truncated]" if len(m) > MATERIAL_CAP else "")


def _load(path, default):
    try:
        return json.load(open(path))
    except (OSError, json.JSONDecodeError):
        return default


def run_round() -> dict:
    from runtime.suite import Suite
    from runtime.registry import NodeRegistry
    from store.fs_store import FsStore
    from runtime import cognition as C

    os.makedirs(STATE_DIR, exist_ok=True)
    state = _load(STATE, {"round": 0, "prior_synthesis": {}})
    s = Suite(FsStore(os.path.join(REPO, ".data/store")), NodeRegistry().discover([os.path.join(REPO, "nodes")]),
              nodes_dir=os.path.join(REPO, "nodes"))

    state["round"] += 1
    rnd = state["round"]
    territories = (state.get("next_territories") or SEED) if rnd > 1 else SEED
    # normalize: triangulator emits [{territory, why}]; seed already matches
    territories = [t if isinstance(t, dict) else {"territory": str(t), "why": ""} for t in territories][:10]

    obs_role = s.role_registry["observe_territory"]
    tri_role = s.role_registry["triangulate_mesh"]
    obs_bind = s.resolve_role("observe_territory")
    tri_bind = s.resolve_role("triangulate_mesh")

    units = [{"territory": t["territory"], "why": t.get("why", ""),
              "material": gather(t["territory"], s)} for t in territories]
    res = C.run_items(obs_role, units, s.store, turn_id=f"mesh-r{rnd}",
                      model=obs_bind["model"], base_url=obs_bind["base_url"], max_tokens=OBS_TOKENS)
    resolved = res.resolved if isinstance(res.resolved, dict) else {}
    observations = []
    records = []
    for j, out in sorted(resolved.items()):
        if not isinstance(out, dict):
            continue
        terr = units[j]["territory"]
        observations.append({"territory": terr, **out})
        records.append({"source_address": f"mesh://territory/{_slug(terr)}",
                        "output": dict(out, territory=terr, round=rnd),
                        "projection": "mesh"})
    if not records:
        raise RuntimeError(f"round {rnd}: 0/{len(units)} observations resolved — failed: {res.failed}")
    s.capture_corpus(records, project="company", session="mesh-triangulate", round=f"r{rnd}")

    anchor_core = _read_head(ANCHOR, 3500)
    syn = C.run_role(tri_role,
                     {"notes": json.dumps(observations)[:60000],
                      "prior": json.dumps(state.get("prior_synthesis") or {})[:12000],
                      "anchor": anchor_core},
                     model=tri_bind["model"], base_url=tri_bind["base_url"],
                     store=s.store, max_tokens=SYN_TOKENS, think=False)
    s.capture_corpus([{"source_address": f"mesh://round/{rnd}",
                       "output": dict(syn, round=rnd, n_observations=len(observations)),
                       "projection": "mesh"}],
                     project="company", session="mesh-triangulate", round=f"r{rnd}")

    state["prior_synthesis"] = syn
    state["next_territories"] = syn.get("next_territories") or []
    json.dump(state, open(STATE, "w"), indent=1)
    return {"round": rnd, "observed": [u["territory"] for u in units],
            "n_observations": len(observations), "unit_failures": len(getattr(res, "failed", []) or []),
            "convergences": len(syn.get("convergences", [])), "contradictions": len(syn.get("contradictions", [])),
            "dormant": syn.get("dormant", []), "next": state["next_territories"],
            "mesh_note": syn.get("mesh_note", "")}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    for _ in range(n):
        print(json.dumps(run_round(), indent=1, default=str))
