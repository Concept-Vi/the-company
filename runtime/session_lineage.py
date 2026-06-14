"""runtime/session_lineage.py — the lineage + DISTANCE map across sessions (vision §1.4 + §1.5).

Given a set of transcripts, discover the fork tree via the `forkedFrom` provenance field (STRUCTURAL,
not guessed), and compute the distances that orient every session relative to each other and to the
START:  the shared TRUNK (root → branch), and each fork's DIVERGENCE (branch → tip) measured in
time-span, message counts, and output tokens.  This is the map §1.5 reuses to decide how many more
points-in-time to clone and WHERE to fork them.

Output is DATA (json) + a readable md (COMMIT-GRAMMAR §4: data primary, prose explains).
Read-only.  Reuses session_scan (per-session metrics) + session_pointintime.build_timeline (boundaries).

API:  build_lineage([path,…]) -> {nodes, edges, distances, narrative} ;  write_lineage(paths, out_dir)
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

from runtime.session_scan import scan_session, _iso_to_epoch
from runtime.session_pointintime import _iter_jsonl


def _branch_of(jsonl_path: str) -> dict | None:
    """A fork's branch point = the provenance of its inherited prefix: the parent sessionId, and the
    LAST (max-ts) inherited event's original messageUuid — that's the parent event it diverged after.
    Returns {parent_sid, branch_uuid, branch_ts, inherited, own} or None for a root."""
    parent_sid = None
    inherited = own = 0
    last_inherited_uuid = None
    last_inherited_ts = None
    for _, ev in _iter_jsonl(jsonl_path):
        if not isinstance(ev, dict) or not ev.get("type"):
            continue
        ff = ev.get("forkedFrom") if isinstance(ev.get("forkedFrom"), dict) else None
        if ff:
            inherited += 1
            parent_sid = parent_sid or ff.get("sessionId")
            mu = ff.get("messageUuid")
            ts = ev.get("timestamp")
            # track the latest inherited event by ts (the divergence frontier)
            ep = _iso_to_epoch(ts)
            if ep is not None and (last_inherited_ts is None or ep >= last_inherited_ts):
                last_inherited_ts = ep
                last_inherited_uuid = mu
        elif ev.get("type") in ("user", "assistant"):
            own += 1
    if inherited == 0:
        return None
    return {"parent_sid": parent_sid, "branch_uuid": last_inherited_uuid,
            "inherited": inherited, "own": own}


def _node(jsonl_path: str) -> dict:
    s = scan_session(jsonl_path)["summary"]
    sid = os.path.splitext(os.path.basename(jsonl_path))[0]
    branch = _branch_of(jsonl_path)
    return {
        "sid": sid, "path": os.path.abspath(jsonl_path),
        "first_ts": s["first_ts"], "last_ts": s["last_ts"], "duration_sec": s["duration_sec"],
        "events": s["events_total"], "boundaries": [b["point"] for b in s["boundaries"]],
        "n_boundaries": len(s["boundaries"]),
        "human_turns": s["by_attribution"].get("user", 0),
        "assistant_turns": s["by_attribution"].get("assistant", 0),
        "out_tokens": s["tokens_total"].get("out", 0), "in_tokens": s["tokens_total"].get("in", 0),
        "models": s["by_model"], "is_root": s["fork_provenance"]["is_root"],
        "branch": branch, "segments": s["segments"],
    }


def build_lineage(paths: list[str]) -> dict:
    nodes = {n["sid"]: n for n in (_node(p) for p in paths)}
    edges = []
    for sid, n in nodes.items():
        if n["branch"] and n["branch"]["parent_sid"]:
            edges.append({"child": sid, "parent": n["branch"]["parent_sid"],
                          "branch_uuid": n["branch"]["branch_uuid"]})

    distances = {}
    for e in edges:
        child = nodes.get(e["child"]); parent = nodes.get(e["parent"])
        if not child:
            continue
        # branch ts = the parent boundary the child inherited up to = child.first_ts (the fork starts AT the branch)
        branch_ep = _iso_to_epoch(child["first_ts"])
        d = {"child": e["child"], "parent": e["parent"], "branch_ts": child["first_ts"]}
        # shared trunk: parent.start -> branch
        if parent:
            start_ep = _iso_to_epoch(parent["first_ts"])
            d["trunk_sec"] = round((branch_ep - start_ep), 1) if (branch_ep and start_ep) else None
            d["trunk_days"] = round(d["trunk_sec"] / 86400, 2) if d["trunk_sec"] else None
            # parent's post-branch divergence (its seg after the branch)
            post = [s for s in parent["segments"] if s.get("from_line") and _iso_to_epoch(s.get("first_ts") or "") and
                    (_iso_to_epoch(s["first_ts"]) or 0) >= (branch_ep or 0) - 5]
            if post:
                d["parent_divergence_msgs"] = sum(s["user_msgs"] + s["assistant_msgs"] for s in post)
                d["parent_tip_ts"] = parent["last_ts"]
                pe = _iso_to_epoch(parent["last_ts"])
                d["parent_divergence_sec"] = round((pe - branch_ep), 1) if (pe and branch_ep) else None
        # child's own divergence: branch -> child tip
        ce = _iso_to_epoch(child["last_ts"])
        d["child_divergence_sec"] = round((ce - branch_ep), 1) if (ce and branch_ep) else None
        d["child_own_msgs"] = (child["branch"] or {}).get("own")
        d["child_own_out_tokens"] = child["out_tokens"]
        d["child_compactions_since_branch"] = child["n_boundaries"]
        distances[f"{e['parent']}->{e['child']}"] = d

    return {"lineage_ver": "lineage-1", "built_at": datetime.now(timezone.utc).isoformat(),
            "nodes": nodes, "edges": edges, "distances": distances}


def _short(sid: str) -> str:
    return sid.split("-")[0]


def to_markdown(lin: dict) -> str:
    L = ["# Session Lineage & Distance Map", "",
         "```", "trust: fabric-derived", "author: ch-8djrpmsl / 11e7d395 (fork)",
         f"date: 2026-06-14", "verified: by-execution (session_lineage over the live transcripts)",
         "```", "> Per [[COMMIT-GRAMMAR]] §2 §4. DATA is `lineage.json`; this is the readable projection.", ""]
    roots = [n for n in lin["nodes"].values() if n["is_root"]]
    for r in roots:
        L.append(f"## ROOT — `{_short(r['sid'])}`  (the true beginning)")
        L.append(f"- start **{r['first_ts']}** → tip **{r['last_ts']}**  ({round((r['duration_sec'] or 0)/86400,2)} days)")
        L.append(f"- {r['human_turns']} human turns · {r['assistant_turns']} assistant turns · {r['out_tokens']:,} output tokens · boundaries {r['boundaries']}")
        L.append(f"- models: {r['models']}")
        L.append("")
    for key, d in lin["distances"].items():
        c = lin["nodes"][d["child"]]
        L.append(f"## BRANCH — `{_short(d['parent'])}` ⟶ fork `{_short(d['child'])}`")
        L.append(f"- branch at **{d['branch_ts']}**, after a shared TRUNK of **{d.get('trunk_days')} days** "
                 f"({d.get('trunk_sec')}s) from the root start")
        L.append(f"- since the branch, the two diverged in PARALLEL:")
        L.append(f"    - parent (`{_short(d['parent'])}`) ran on ~{round((d.get('parent_divergence_sec') or 0)/3600,1)}h "
                 f"past the branch, ~{d.get('parent_divergence_msgs')} msgs, tip {d.get('parent_tip_ts')}")
        L.append(f"    - fork (`{_short(d['child'])}`) ran ~{round((d.get('child_divergence_sec') or 0)/3600,1)}h, "
                 f"{d.get('child_own_msgs')} own msgs, {d.get('child_own_out_tokens'):,} output tokens, "
                 f"{d.get('child_compactions_since_branch')} compactions (incl. inherited)")
        L.append(f"- the fork carries the trunk as a COMPACTION SUMMARY (inherited prefix), not the raw {round((d.get('trunk_days') or 0),1)} days of events.")
        L.append("")
    L.append("## Orientation (the one-paragraph picture)")
    L.append("The root is the shared past; the branch is one compaction boundary on it; parent and fork "
             "are PARALLEL SIBLINGS diverging from that boundary, each living its own time since. The fork's "
             "view of everything before the branch is the compaction SUMMARY, not the lived events — which is "
             "exactly why a point-in-time clone AT a boundary resumes 'as it was then'.")
    return "\n".join(L)


def write_lineage(paths: list[str], out_dir: str) -> dict:
    lin = build_lineage(paths)
    os.makedirs(out_dir, exist_ok=True)
    jpath = os.path.join(out_dir, "lineage.json")
    with open(jpath, "w", encoding="utf-8") as f:
        json.dump(lin, f, ensure_ascii=False, indent=2)
    mpath = os.path.join(out_dir, "lineage.md")
    with open(mpath, "w", encoding="utf-8") as f:
        f.write(to_markdown(lin))
    return {"json": jpath, "md": mpath, "nodes": len(lin["nodes"]), "edges": len(lin["edges"])}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: python3 -m runtime.session_lineage --out-dir DIR <t1.jsonl> <t2.jsonl> …"); sys.exit(2)
    a = sys.argv[1:]
    out_dir = a[a.index("--out-dir") + 1] if "--out-dir" in a else "."
    paths = [x for x in a if x.endswith(".jsonl")]
    print(json.dumps(write_lineage(paths, out_dir), indent=2))
