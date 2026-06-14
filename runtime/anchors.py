"""runtime/anchors.py — PLANTED POLES for the two-gravity separator (Group 9).

A separator pole is just a vector in a lens. Most poles are FOUND (a corpus item, a cluster centroid).
But one kind of pole has no corpus item to point at: the AI-corner — the characterization of how
AI-generated content DEFORMS away from grounded authorship. There is no document in the corpus that IS
"AI deformation", so the AI must PLANT it: characterize the deformation itself (never demand the tells
from Tim — Tim 2026-06-14), embed that characterization through the SAME lens the items live in (so the
cosines are comparable — lens-mismatch is the main source of false noise), and persist it as a vector the
separator binding can name as a pole (anchor://ai-corner).

This is the MECHANISM for the pollution INSTANCE of the general separator — origin (a grounded sample)
vs the AI-corner. It is the named, deferred application: the general two-gravity field is proven on found
real poles (two clustering-separated regions); this planted pole is honestly probed, never claimed as a
verified pollution oracle (the separation_report tells the truth about whether it separates).

Run (the bridge must be live — it holds the embedder):
    ./.venv/bin/python -m runtime.anchors            # plants anchor://ai-corner in the topics lens
"""
from __future__ import annotations
import hashlib
import json
import urllib.request

# The AI's OWN characterization of AI-deformation (the AI supplies its AI-pole — Tim never tells the tells).
# Dense prose so it embeds as a direction, not a keyword: the failure modes Tim has named + the standing
# feedback (closure-form, hedging, premature completion, echoing, generic helpfulness, over-structure).
AI_CORNER_TEXT = (
    "Generic AI-assistant prose and its deformation away from grounded authorship: hedged and "
    "non-committal language (likely, probably, it seems, generally), closure-shaped writing that "
    "summarizes and concludes instead of staying open and growing, premature claims that something is "
    "done or fixed or complete without verification, echoing the prompt back instead of extending it with "
    "independent reasoning, over-structured scaffolding of bullet lists and numbered steps, decontextualized "
    "confident boilerplate, performed helpfulness rather than grounded reasoning, a polished symmetric "
    "surface that avoids taking a real position, safe both-sides framing, filler transitions and restated "
    "context, the smooth average voice of a language model rather than a specific situated human author."
)

AI_CORNER_SOURCE = "anchor://ai-corner"


def embed_via_bridge(text: str, bridge: str = "http://localhost:8770") -> dict:
    """Embed `text` through the SAME embed path the corpus was built with (the live bridge's embed role →
    BGE-M3). Returns {vector, dim, model}. Fail loud: a down embedder / missing vector RAISES (never a
    silent fabricated vector — the anchor must be embedded by the same model as the items or the cosines lie)."""
    req = urllib.request.Request(
        f"{bridge}/api/cognition/embed", method="POST",
        data=json.dumps({"text": text}).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    out = body.get("output") or {}
    vec = out.get("vector")
    if not vec:
        raise RuntimeError(f"embed returned no vector (embedder down?): {body}")
    return {"vector": vec, "dim": out.get("dim") or len(vec), "model": out.get("model") or "BAAI/bge-m3"}


def plant_anchor(store, source: str, text: str, space: str, *, bridge: str = "http://localhost:8770") -> dict:
    """Embed `text` and persist it as the per-space vector keyed by `source` in `space` — so the separator
    can name `source` as a pole. Idempotent by content: re-planting the same text overwrites the same entry."""
    emb = embed_via_bridge(text, bridge=bridge)
    chash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    addr = store.space_address(source, space)
    rec = store.put_vector(addr, emb["vector"], chash, dim=emb["dim"], model=emb["model"],
                           space=space, source=source)
    return {"source": source, "space": space, "address": addr, "dim": rec["dim"], "model": rec["model"]}


def plant_ai_corner(store, space: str = "topics", *, bridge: str = "http://localhost:8770") -> dict:
    """Plant the AI-corner pole (anchor://ai-corner) in `space` — the named pollution instance's AI-pole."""
    return plant_anchor(store, AI_CORNER_SOURCE, AI_CORNER_TEXT, space, bridge=bridge)


if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from store.fs_store import FsStore
    from fabric import config as fcfg
    st = FsStore(fcfg.STORE_DIR)
    info = plant_ai_corner(st)
    print(f"planted {info['source']} in lens {info['space']} "
          f"({info['dim']}-dim, {info['model']}) at {info['address']}")
