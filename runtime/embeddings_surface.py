"""runtime/embeddings_surface.py — EMBEDDINGS AS AN OPERABLE SURFACE (potentials-loop E1).

The ONE shared implementation behind the `embeddings` MCP tool AND the `company embed` CLI verb
(one function → two faces, the jobs_status precedent). Nothing here is a second dialect: the lens
table IS fabric/embed_routing, the builders ARE ops/build_embeddings (SPACES + corpus_for_space +
build_code_space/build_fabric_space), the pyramid rebuild IS runtime/scale.rebuild_scale_pyramids.

  spaces_status()  — every real embedding space (ledger.embedding, __root_% probe leftovers excluded):
                     units · dims · lenses (emb_layers) · pyramid rungs (ledger.cluster_member) ·
                     freshness (max ts + pyramid_fingerprints.json). THE OPERATOR'S STATUS VIEW.
  route_table()    — the lens table rendered (space → lens → endpoint/model/dim) + HOW to change it
                     (edit fabric/embed_routing.py _NOMIC_SPACES — said honestly; it is code, not a row).
  build_space()    — (re)build ONE registered space through the ops/build_embeddings path (incremental
                     by content_hash; NEVER silently truncated — over-window items are flagged, not
                     stored). Registered spaces only; anything else gets a teaching refusal.
  pyramid_space()  — rebuild one space's scale-pyramid rungs via runtime.scale.rebuild_scale_pyramids
                     (whole-space fingerprint early-exit reported honestly as skipped_whole_space).

Fail-loud with TEACHING refusals (the runtime/jobs discipline): a bad space name comes back with what
was got, what's valid, and the closest match — never a bare error, never a silent no-op.
"""
from __future__ import annotations

import io
import json
import os
import time
from contextlib import redirect_stdout

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _refuse(at: str, got, expected: str, *, closest=None, why: str = "") -> dict:
    """A teaching refusal (the runtime/jobs _teach shape, local so this module stays dependency-thin)."""
    r = {"ok": False, "refused": True, "at": at, "got": got, "expected": expected}
    if closest:
        r["closest"] = closest
    if why:
        r["why"] = why
    return r


def _closest(word: str, pool) -> list:
    word = str(word or "")
    scored = sorted(pool, key=lambda c: (-len(os.path.commonprefix([word, c])), abs(len(c) - len(word))))
    return [c for c in scored if os.path.commonprefix([word, c]) or word in c or c in word][:3] or scored[:2]


def _psql(sql: str) -> str:
    from ops.build_embeddings import psql
    return psql(sql)


def _fingerprints() -> dict:
    from fabric import config as fcfg
    p = os.path.join(fcfg.STORE_DIR, "pyramid_fingerprints.json")
    try:
        with open(p) as f:
            return json.load(f)
    except Exception:
        return {}


# ── spaces: the operator's status view ────────────────────────────────────────────────────────────

def spaces_status() -> dict:
    """Every REAL embedding space in ledger.embedding (probe leftovers `__root_%` excluded; the
    `scale:<space>:k*` centroid rows fold under their base space, not listed as spaces themselves):
    units per lens (emb_layer) + dim, pyramid rungs present (cluster_member), last-embed ts, and
    whether a whole-space pyramid fingerprint is banked (the rebuild early-exit freshness)."""
    rows = _psql("select space, emb_layer, dim, count(*), max(ts) from ledger.embedding "
                 "where left(space,7) <> '__root_' group by 1,2,3 order by 1,2").splitlines()
    rungs_raw = _psql("select space, emb, k, count(*) from ledger.cluster_member "
                      "group by 1,2,3 order by 1,3").splitlines()
    fps = _fingerprints()

    rungs: dict = {}
    for r in rungs_raw:
        f = r.split("|")
        if len(f) < 4:
            continue
        rungs.setdefault(f[0], []).append({"k": int(f[2]), "emb": f[1], "clusters": None,
                                           "members": int(f[3])})

    spaces: dict = {}
    for r in rows:
        f = r.split("|")
        if len(f) < 5:
            continue
        space, emb, dim, n, ts = f[0], f[1], int(f[2]), int(f[3]), f[4]
        if space.startswith("scale:"):
            base = space.split(":", 2)[1]
            s = spaces.setdefault(base, {"space": base, "lenses": [], "scale_centroids": []})
            s["scale_centroids"].append({"space": space, "emb": emb, "dim": dim, "units": n})
            continue
        s = spaces.setdefault(space, {"space": space, "lenses": [], "scale_centroids": []})
        s["lenses"].append({"emb": emb, "dim": dim, "units": n, "last_embed": ts})

    for name, s in spaces.items():
        s["units"] = max((l["units"] for l in s["lenses"]), default=0)
        s["last_embed"] = max((l["last_embed"] for l in s["lenses"]), default=None)
        s["pyramid_rungs"] = sorted(rungs.get(name, []), key=lambda x: x["k"])
        fp_keys = [k for k in fps if k.split("#", 1)[0] == name]
        s["pyramid_fingerprint"] = {k: fps[k][:12] for k in fp_keys} or None

    from ops.build_embeddings import SPACES as REG
    out = sorted(spaces.values(), key=lambda s: -s["units"])
    return {"ok": True, "count": len(out), "spaces": out,
            "buildable": sorted(REG),   # the spaces this surface can (re)build (ops/build_embeddings SPACES)
            "note": ("units = rows in the space's biggest lens; lenses = emb_layers over the SAME items; "
                     "pyramid_rungs from ledger.cluster_member; pyramid_fingerprint = the whole-space "
                     "rebuild early-exit key (.data/store/pyramid_fingerprints.json) — present means the "
                     "next rebuild skips unless content changed. __root_% probe rows excluded.")}


def spaces_render(status: dict | None = None) -> str:
    """The CLI face of spaces_status — legible terminal text (one function, two faces)."""
    s = status or spaces_status()
    lines = [f"EMBEDDING SPACES — {s['count']} real spaces (ledger.embedding)",
             f"  buildable through this surface: {', '.join(s['buildable'])}"]
    for sp in s["spaces"]:
        lenses = "  ".join(f"{l['emb']}({l['dim']}d)×{l['units']}" for l in sp["lenses"])
        lines.append(f"\n  {sp['space']:<18} {sp['units']:>6} units   {lenses}")
        if sp.get("last_embed"):
            lines.append(f"    last embed: {sp['last_embed'][:19]}")
        if sp["pyramid_rungs"]:
            ks = ", ".join(f"k{r['k']}" for r in sp["pyramid_rungs"])
            fp = "  fingerprint: fresh-banked" if sp.get("pyramid_fingerprint") else ""
            lines.append(f"    pyramid rungs: {ks}{fp}")
    return "\n".join(lines)


# ── route: the lens table, rendered ───────────────────────────────────────────────────────────────

def route_table() -> dict:
    """The ONE lens table (fabric/embed_routing) rendered per space: which embedder turns a query into
    a vector for that space, at which endpoint/model/dim. HONEST about how to change it: the routing
    lives in code (fabric/embed_routing.py `_NOMIC_SPACES`) — edit that set, not a registry row."""
    from fabric import embed_routing as er
    from fabric import config as fcfg
    from ops.build_embeddings import SPACES as REG
    lenses = {
        "nomic": {"model": "nomic-embed-code", "endpoint": "http://127.0.0.1:11434/api/embed (ollama)",
                  "dim": 3584, "num_ctx": 32768},
        "pplx": {"model": fcfg.DEFAULT_EMBED_MODEL, "endpoint": fcfg.DEFAULT_EMBED_URL,
                 "dim": fcfg.DEFAULT_EMBED_DIM},
    }
    # every live space (from the ledger) + every registered builder space, each through the ONE router
    live = {s["space"] for s in spaces_status()["spaces"]}
    routes = [{"space": sp, "lens": er.lens_for_space(sp), **lenses[er.lens_for_space(sp)]}
              for sp in sorted(live | set(REG))]
    return {"ok": True, "lenses": lenses, "routes": routes,
            "rule": ("code · symbol · scale:code:* · scale:symbol:* → nomic; everything else → pplx "
                     "(the fabric default)"),
            "how_to_change": ("the routing is CODE, not a registry row (honest): edit "
                              "fabric/embed_routing.py — add/remove the base space name in _NOMIC_SPACES "
                              "(currently {code, symbol}). A new space with the default pplx lens needs "
                              "NO change; a new lens family = a new branch in embed_query.")}


def route_render(table: dict | None = None) -> str:
    t = table or route_table()
    lines = ["EMBED ROUTING — the ONE lens table (fabric/embed_routing.py)",
             f"  rule: {t['rule']}", ""]
    for name, l in t["lenses"].items():
        lines.append(f"  lens {name:<6} {l['model']}  @ {l['endpoint']}  ({l['dim']}-dim)")
    lines.append("")
    for r in t["routes"]:
        lines.append(f"  {r['space']:<18} → {r['lens']:<6} ({r['dim']}d)")
    lines.append(f"\n  to change: {t['how_to_change']}")
    return "\n".join(lines)


# ── build: (re)build one space through the ONE builder path ───────────────────────────────────────

def build_space(space: str = "", force: bool = False, project: str = "company", root: str = "") -> dict:
    """(Re)build ONE space's embeddings through the ops/build_embeddings path — the SAME corpus fns +
    builders the CLI script runs (never a fork). Incremental by content_hash (unchanged items skip;
    `force=True` re-embeds — ollama-kind spaces only, honest refusal otherwise). NEVER silently
    truncates: over-window items come back in flagged_for_chunking, not stored as lying vectors.
    Registered spaces only — a teaching refusal lists the valid ones. Also the `build_space` jobs
    HANDLER body (E3): schedulable/watchable like every other job."""
    from ops import build_embeddings as B
    if space not in B.SPACES:
        return _refuse("space", space, f"a registered buildable space — one of {sorted(B.SPACES)}",
                       closest=_closest(space, B.SPACES),
                       why=("only spaces with a registered corpus+builder in ops/build_embeddings.SPACES "
                            "are buildable here; other ledger spaces (topics, history, extractions…) are "
                            "built by their own ingest pipelines, not this surface"))
    cfg = B.SPACES[space]
    if force and cfg["kind"] != "ollama":
        return _refuse("force", True, "force=False for fabric-kind (pplx) spaces",
                       why=("the fabric build path (vector_index.build_index) is incremental-only — it has "
                            "no force re-embed; only the ollama path (code/symbol) supports force. To force "
                            "a pplx space, clear its rows in ledger.embedding first (deliberate, loud)."))
    from store.fs_store import FsStore
    from store import vector_index as vi
    from fabric import config as fcfg
    root = os.path.abspath(root or REPO)
    store = FsStore(fcfg.STORE_DIR)
    t0 = time.time()
    buf = io.StringIO()                      # builders print progress; capture it (MCP-face safe), return the tail
    try:
        with redirect_stdout(buf):
            corpus, empty, missing = B.corpus_for_space(space, project, root)
            if cfg["kind"] == "ollama":
                res = B.build_code_space(store, corpus, cfg, vi, space, force=force)
            else:
                res = B.build_fabric_space(store, corpus, cfg, vi, space)
    except SystemExit as e:                  # corpus fns raise SystemExit on a missing corpus — re-raise loud
        raise RuntimeError(f"build_space({space!r}): {e}") from e
    flagged = res.pop("flagged_for_chunking", [])
    out = {"ok": not res.get("degraded", False), "space": space, "model": cfg["model"], "dim": cfg["dim"],
           "corpus": len(corpus), "empty_skipped": empty, "missing_on_disk": missing,
           "embedded": res.get("embedded", 0), "skipped_unchanged": res.get("skipped", 0),
           "flagged_for_chunking": [{"address": a, "size": n} for a, n in flagged],
           "elapsed_s": round(time.time() - t0, 1)}
    if res.get("degraded"):
        out["degraded"] = True
        out["why"] = "the embedder raised mid-build (endpoint down / OOM) — the build stopped, counts are partial"
    log = buf.getvalue().strip().splitlines()
    if log:
        out["log_tail"] = log[-6:]
    return out


# ── pyramid: rebuild one space's rungs ────────────────────────────────────────────────────────────

def pyramid_space(space: str = "") -> dict:
    """Rebuild ONE space's scale-pyramid rungs via runtime.scale.rebuild_scale_pyramids (the SAME jobs
    handler body the daily rebuild fires — never a fork). Its whole-space fingerprint early-exit is
    reported honestly: `skipped_whole_space: true` means nothing changed since the last build (that IS
    the fresh state, not a failure). Teaching refusal on a space with no embeddings to cluster."""
    if not space:
        return _refuse("space", space, "a space name with embeddings to cluster (see op='spaces')")
    known = {s["space"] for s in spaces_status()["spaces"]}
    if space not in known:
        return _refuse("space", space, f"a live embedding space — one of {sorted(known)}",
                       closest=_closest(space, known),
                       why="pyramids cluster a space's EXISTING vectors; build the space first (op='build')")
    from runtime.scale import rebuild_scale_pyramids
    buf = io.StringIO()
    with redirect_stdout(buf):
        res = rebuild_scale_pyramids(spaces=space)
    out = {"ok": True, "space": space, "result": res.get(space, res)}
    log = buf.getvalue().strip().splitlines()
    if log:
        out["log_tail"] = log[-6:]
    return out
