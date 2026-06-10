#!/usr/bin/env python3
"""drift_radar.py — ② the DRIFT-RADAR at full scale (unblocked by ① — the COMPLETE repo space).

Two channels over space='repo' (587 embedded file-digests):
  A · BUILT-TWICE: all-pairs cosine over the code:// vectors → near-clusters (union-find over pairs
      ≥ threshold) → judge_drift CONFIRM per cluster (the false-positive guard: built-twice | overlap
      | distinct, closed vocabulary, conservative) → a confirmed cluster becomes a MARK
      (mark_type=built_twice/overlap, direction=surface — render-not-judge, the operator decides).
  B · DOC-VS-CODE: each AGENTS.md's vector vs its module files' centroid — LOW similarity = the
      constitution may have drifted from the code. DETERMINISTIC report-only this pass (a low-sim
      doc-pair needs a different judgement than near-cluster confirm — flagged, not judged).

Findings: .build/drift/findings.json; the canonical report (DRIFT-RADAR-REPORT.md) is the lead's
judgment layer. THE FLOOR: judges + marks + reports — never auto-fixes, never resolves."""
import json
import math
import os
import sys
from collections import defaultdict

os.chdir("/home/tim/company")
sys.path.insert(0, "/home/tim/company")
OUT = ".build/drift/findings.json"
PAIR_T = 0.82            # near-pair threshold (conservative; judged anyway — the judge is the guard)
DOC_T = 0.45             # an AGENTS.md below this vs its module centroid = drift candidate
MAX_CLUSTERS = 24        # bound the judge fires per pass


def cos(a, b):
    d = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)); nb = math.sqrt(sum(x * x for x in b))
    return d / (na * nb) if na and nb else 0.0


def main() -> dict:
    from runtime.suite import Suite
    from runtime.registry import NodeRegistry
    from store.fs_store import FsStore
    from store.vector_index import index_addresses, get_vector
    from runtime import cognition as C

    s = Suite(FsStore(".data/store"), NodeRegistry().discover(["nodes"]), nodes_dir="nodes")
    # the repo-space index keys are WRAPPED: vec://code://<path>#space=repo (the per-space key form
    # fs_store.put_vector mints). The radar's first run filtered on bare code:// and swept an EMPTY
    # set (0 findings from 587 files — caught by look-at-output, zero-is-suspicious). Parse the wrap:
    # the vec key fetches the vector; the inner code://<path> is the working id.
    vecs, paths = {}, {}
    for key in index_addresses(s.store, space="repo"):
        inner = key[len("vec://"):].split("#", 1)[0] if key.startswith("vec://") else key
        if not inner.startswith("code://"):
            continue
        p = inner[len("code://"):]
        if p.startswith("/"):
            continue                                        # a stray absolute-path record (pre-normalization) — skip, noted
        if not os.path.exists(p):
            continue                                        # a STALE record (deleted file / phantom path-spelling —
                                                            # e.g. the eval's 'company/'-prefixed ingest); skip, noted
        v = (get_vector(s.store, key) or {}).get("vector")
        if v:
            vecs[inner] = v
            paths[inner] = p

    # ── channel B · DOC-VS-CODE (deterministic) ──
    doc_findings = []
    by_dir = defaultdict(list)
    for a, p in paths.items():
        d = os.path.dirname(p) or "."
        by_dir[d].append(a)
    for a, p in paths.items():
        if os.path.basename(p) != "AGENTS.md":
            continue
        d = os.path.dirname(p) or "."
        sibs = [x for x in by_dir[d] if x != a]
        if len(sibs) < 2:
            continue
        cents = [vecs[x] for x in sibs]
        centroid = [sum(col) / len(cents) for col in zip(*cents)]
        sim = cos(vecs[a], centroid)
        if sim < DOC_T:
            doc_findings.append({"doc": p, "module": d, "sim_to_module": round(sim, 3), "n_files": len(sibs)})
    doc_findings.sort(key=lambda x: x["sim_to_module"])

    # ── channel A · BUILT-TWICE (near-pairs → relation filter → clusters → judge) ──
    code_addrs = [a for a, p in paths.items() if os.path.basename(p) != "AGENTS.md"]

    def relation(pa: str, pb: str) -> str | None:
        """GC11 — the DETERMINISTIC intent-relation between two near files (the same arc as
        refcheck/prose_check: a judgment the model kept misfiring on becomes a data check).
        A named relation = KNOWN-INTENTIONAL nearness — never sent to the judge, reported in its
        own bucket. None = relation-less, the judge's actual job."""
        na, nb = os.path.basename(pa), os.path.basename(pb)
        sa, sb = na.rsplit(".", 1)[0], nb.rsplit(".", 1)[0]
        # test-of: tests/<x>_acceptance.py ↔ the module named <x> (either direction)
        for t, m, sm in ((pa, pb, sb), (pb, pa, sa)):
            if t.startswith("tests/") and (sm in os.path.basename(t).replace("_acceptance", "")
                                           or os.path.basename(t).replace("_acceptance.py", "") in sm):
                return "test-of (a test mirrors its module's vocabulary BY DESIGN)"
        # anchor/summary-of: ANCHOR.md ↔ a doc in the same dir
        if {na, nb} & {"ANCHOR.md", "README.md"} and os.path.dirname(pa) == os.path.dirname(pb):
            return "summary-of (an anchor/readme intentionally restates its dir's main doc)"
        # series-sibling: numbered docs of one design series (00-X.md / 03-Y.md in one dir)
        if (os.path.dirname(pa) == os.path.dirname(pb)
                and na[:2].isdigit() and nb[:2].isdigit()):
            return "series-sibling (numbered chapters of one design series)"
        return None

    pairs, intentional = [], []
    for i, a in enumerate(code_addrs):
        va = vecs[a]
        for b in code_addrs[i + 1:]:
            c = cos(va, vecs[b])
            if c >= PAIR_T:
                rel = relation(paths[a], paths[b])
                if rel:
                    intentional.append({"a": paths[a], "b": paths[b], "cosine": round(c, 3),
                                        "relation": rel.split(" ")[0]})
                else:
                    pairs.append((round(c, 3), a, b))
    pairs.sort(reverse=True)
    parent = {}
    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for _c, a, b in pairs:
        parent[find(a)] = find(b)
    clusters = defaultdict(set)
    for _c, a, b in pairs:
        clusters[find(a)].update([a, b])
    clus = sorted(clusters.values(), key=len, reverse=True)[:MAX_CLUSTERS]

    judge = s.role_registry["judge_drift"]
    judged = []
    for members in clus:
        members = sorted(members)
        lines = []
        for m in members[:6]:                                # bound the cluster text
            rows = s.find_corpus(source_address=m)
            dig = {}
            if rows:
                dig = (s.store.get_content(rows[-1]["cas"]) or {}).get("output") or {}
            lines.append(f"FILE {paths[m]}: {json.dumps(dig)[:400]}")
        top_sim = max(c for c, a, b in pairs if a in members and b in members)
        out = C.run_role(judge, {"utterance": "\n".join(lines)}, store=s.store, max_tokens=250)
        v = out if isinstance(out, dict) else {}
        rec = {"members": [paths[m] for m in members], "top_cosine": top_sim,
               "verdict": v.get("verdict"), "shared": v.get("shared", ""),
               "the_source": v.get("the_source", ""), "note": v.get("note", "")}
        judged.append(rec)
        if v.get("verdict") in ("built-twice", "overlap"):
            s.mark(f"code://{rec['members'][0]}", v["verdict"].replace("-", "_"),
                   value={"with": rec["members"][1:], "shared": rec["shared"], "source": rec["the_source"]},
                   source_pass="drift-radar-2026-06-10", evidence=f"cosine {top_sim}")

    confirmed = [j for j in judged if j["verdict"] in ("built-twice", "overlap")]
    out = {"space_size": len(vecs), "near_pairs": len(pairs),
           "intentional_pairs": intentional, "clusters_judged": len(judged),
           "confirmed": confirmed, "distinct": sum(1 for j in judged if j["verdict"] == "distinct"),
           "doc_drift_candidates": doc_findings, "thresholds": {"pair": PAIR_T, "doc": DOC_T}}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w"), indent=1)
    return {"near_pairs": len(pairs), "intentional_filtered": len(intentional),
            "clusters_judged": len(judged),
            "confirmed_marks": len(confirmed), "distinct": out["distinct"],
            "doc_drift_candidates": len(doc_findings)}


if __name__ == "__main__":
    print(json.dumps(main(), indent=1, default=str))
