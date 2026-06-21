"""runtime/decision_memory.py — the COMMON-MEMORY seam for the Live Decision Surface (recollection's piece).

THE SEAM (DECISION-SURFACE-BUILD.md): the surface SHOWS a pending decision → the RHM EXPLAINS it using
the common company memory → Tim decides → write-back. This module is the EXPLAIN-half's memory retrieve:
given a decision (its text + optional address), return the CONTEXT BUNDLE the RHM draws on — prior
discussion, related units, the why, provenance — as ONE shared memory across the channels.

REUSE-DON'T-PARALLEL (the union law): composes the pieces already built into the centre —
  • suite.query_corpus(text, space) — semantic retrieve over the embeddable spaces (the shared corpus)
  • runtime.corpus_rerank.rerank_hits — the jina-v3 precision pass (recollection's committed stage)
  • runtime.corpus_neighbours.neighbours — recall-under-a-unit, when the decision has an address
No new memory, no second store — the corpus IS the shared memory; this is the decision-shaped read of it.

CHANNEL-NATIVE: the bridge exposes this as /api/cognition/recall-for-decision (projection's lane); the
RHM (fork's run_turn) calls it to compose the explanation; every channel member draws on the SAME corpus.

PROVENANCE / LEGIBILITY: every context item carries its source address + space + score, so the RHM's
explanation is GROUNDED (cite-able), and the surface renders MEANING (the digest), never machine ids.
"""
from __future__ import annotations

# the spaces a decision's context can come from, broadest-meaning first. common_knowledge = comprehended
# project/design content; principles/worldview/topics = the why-layer; history = prior discussion; repo =
# the code it touches. Registry-is-truth: this list is the embeddable set (cognition_info().spaces).
DEFAULT_DECISION_SPACES = ("common_knowledge", "principles", "worldview", "topics", "history", "repo")
# the HOT-PATH card-resolve spaces — fast (each 0.3-0.6s, the whole set well under territory's 3s memory-leg
# budget). NO 'extractions' here: the dragnet space is 44k vectors and its query is ~10s warm (measured
# 2026-06-21) — adding it to the hot-path BLEW the 3s budget → every decision card resolved UNGROUNDED
# (the memory leg timed out, degrade-clean). The grounding-flip caught its own regression by-use.
#
# EXPLAIN_DECISION_SPACES = the hot-6 PLUS the 44k extraction layer (session+visual-dna+theorem). The rich
# extraction grounding belongs in the DEDICATED explain turn (explanation_grounding), which has the time the
# 3s card-resolve can't spare — and that IS where the flip's value lands (the RHM's explanation grounds in
# the richer layer incl. the theorem = the company grounding decisions on its OWN base; the card-resolve
# point-summary only needs fast decidable context). _attach_digest_text resolves extraction:// text so they
# render MEANING. The ~10s extractions query is a follow-on speed target (a fast index for the 44k space).
EXPLAIN_DECISION_SPACES = DEFAULT_DECISION_SPACES + ("extractions",)

# ── the never-assert law's canonical text (recollection owns it — single-source, two renderings) ──────────
# THE LAW (lead 2026-06-21): a theorem-fork decision's explanation grounds in Tim's OWN written maths and
# FLAGS AI-projection — never asserts a gloss as his theorem (the cube-error proved the AI errs here). It is
# DOUBLE-surfaced so Tim can't miss it: (1) IN-CARD by DNA via the theorem-fork subtype's `ai_uncertainty_caveat`
# required-element — THEOREM_FORK_CAVEAT_OPERATOR below (operator-facing, second-person, Tim-altitude); (2)
# IN the explanation by explain_role via explanation_grounding(...).caveat (model-facing directive). BOTH derive
# from this one law so they can't drift. recollection supplies the text; composition's theorem-fork row declares
# the element; DNA renders it.
THEOREM_FORK_CAVEAT_OPERATOR = (
    "Grounded in your own framework — not asserted beyond it. This is built only from your written "
    "mathematics (traceable to your notes); wherever it would go past what you've actually stated, that step "
    "is flagged as the AI's projection, never claimed as your theorem."
)
# a one-line banner variant for tight in-card space (DNA picks by available room):
THEOREM_FORK_CAVEAT_BANNER = "⚠ Grounded in your maths — anything beyond is flagged as the AI's projection, not asserted as yours."


def prior_decisions_about(suite, topic_text: str, *, k: int = 6, rerank: bool = True) -> list[dict]:
    """"Decisions made about X resurfacing" (the lead's step-6 framing) — surface PRIOR decision-content
    about a topic so Tim sees "you've decided about this before." Decision-FRAMED recall over the
    history + common_knowledge spaces (where decision-notes/comprehended-choices live). Returns
    [{source, space, score}] (rerank-precision when available). Read-only; degrade-clean (a down space →
    fewer items, never fabricated).

    FUTURE (when the decision-surface produces decision-ARTIFACTS — write-backs with scope/kind=decision):
    this filters to those artifacts (find_corpus by the decision kind), so "prior decisions" becomes the
    real decided-artifact set, not just decision-shaped prose. Today it's the decision-framed recall —
    the same compute, a richer source once the surface runs."""
    if not (isinstance(topic_text, str) and topic_text.strip()):
        return []
    framed = f"prior decision, ruling, or chosen approach about: {topic_text}"
    pooled: list[dict] = []
    for sp in ("history", "common_knowledge"):                   # where decisions/choices are recorded
        try:
            out = suite.query_corpus(framed, space=sp, k=k)
        except Exception:
            continue
        for h in out.get("ranked", []):
            pooled.append({"source": h.get("id") or h.get("address"), "space": sp,
                           "score": round(h.get("score", 0.0), 4)})
    if not pooled:
        return []
    if not rerank:                                                # HOT-PATH (3s budget): cosine order, skip the
        return sorted(pooled, key=lambda p: -p["score"])[:k]      # CPU jina rerank (13-20s for ~24 hits — off the live path)
    try:                                                          # precision pass (reuse the committed stage)
        from runtime import corpus_rerank as _cr
        rr = _cr.rerank_hits(suite.store, framed,
                             [{"id": p["source"], "score": p["score"]} for p in pooled],
                             top_n=k, skip_missing=True)
        by = {p["source"]: p for p in pooled}
        return [{**by.get(r["address"], {}), "source": r["address"], "rerank_score": r["rerank_score"]}
                for r in rr["reranked"]]
    except Exception:
        return sorted(pooled, key=lambda p: -p["score"])[:k]


def _clean_meaning(rec: dict, *, max_chars: int = 600) -> str:
    """A corpus record → render-ready MEANING (legibility: prose, NOT raw JSON, NOT machine ids). The
    digest `output` is often a STRUCTURED dict (e.g. {"decision": "...", "bug_fix": "", "frustration": ""}):
    take the NON-EMPTY string fields as `key: value` (skipping the empties that json.dumps would dump as
    noise), so the consumer gets clean meaning. A plain-string output / text / content is used as-is.
    Returns '' when there's nothing legible (caller leaves the item text-less — degrade-clean)."""
    if not isinstance(rec, dict):
        return (str(rec).strip()[:max_chars]) if rec else ""
    out = rec.get("output")
    if isinstance(out, str) and out.strip():
        return out.strip()[:max_chars]
    if isinstance(out, dict):
        if isinstance(out.get("text"), str) and out["text"].strip():
            return out["text"].strip()[:max_chars]
        if isinstance(out.get("summary"), str) and out["summary"].strip():
            return out["summary"].strip()[:max_chars]
        parts = [f"{k}: {v.strip()}" for k, v in out.items()
                 if isinstance(v, str) and v.strip()]          # the non-empty meaningful fields, labelled
        if parts:
            return " · ".join(parts)[:max_chars]
    if isinstance(out, list):                                  # a list of insight strings (or dicts) — common
        items = []                                             # digest shape for code:// units; join them
        for el in out:
            if isinstance(el, str) and el.strip():
                items.append(el.strip())
            elif isinstance(el, dict):
                sub = (el.get("text") or el.get("summary") or
                       " ".join(f"{k}: {v.strip()}" for k, v in el.items() if isinstance(v, str) and v.strip()))
                if isinstance(sub, str) and sub.strip():
                    items.append(sub.strip())
        if items:
            return " · ".join(items)[:max_chars]
    for k in ("text", "content"):
        v = rec.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()[:max_chars]
    return ""


_EXTRACTION_CACHE: dict = {}


def _extraction_text(source: str, *, max_chars: int = 600) -> str:
    """Surface MEANING for an `extraction://<asset>/<chunk_id>` context item — the dragnet extraction layer
    (about + summary + claims), so the 'extractions' grounding space (when added to the decision spaces)
    renders real meaning, not a bare address. Reads the extraction jsonl (cached per asset). The ENABLER for
    grounding decisions on the extraction layer; inert until 'extractions' is in the grounding spaces."""
    import os as _os, json as _json
    if not source.startswith("extraction://"):
        return ""
    rest = source[len("extraction://"):]
    asset, _, cid = rest.partition("/")
    if not asset or not cid:
        return ""
    if asset not in _EXTRACTION_CACHE:
        path = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
                             ".data", "store", "extractions", f"extractions-{asset}.jsonl")
        idx = {}
        if _os.path.exists(path):
            for line in open(path):
                try:
                    r = _json.loads(line)
                    idx[str(r.get("chunk_id"))] = r
                except Exception:
                    continue
        _EXTRACTION_CACHE[asset] = idx
    r = _EXTRACTION_CACHE[asset].get(str(cid))
    if not r:
        return ""
    parts = [r.get("about", ""), r.get("summary", "")] + (r.get("claims") or [])[:3]
    return ". ".join(p for p in parts if p).strip()[:max_chars]


def _attach_digest_text(store, context: list[dict], *, max_chars: int = 600) -> list[dict]:
    """Surface each context item's DIGEST MEANING in-place, so a consumer (fork's RHM / territory_prose)
    renders the grounding WITHOUT a second fetch — and renders MEANING, never the source id or raw JSON
    (legibility: Tim never sees machine shapes). recall already fetches this to RERANK; the cosine hot-path
    didn't surface it at all (fork flagged the gap 2026-06-18: 'recall_for_decision fetches CAS digests for
    rerank but doesn't surface the text in returned items'). ONE list_corpus pass for all sources (not N
    scans), then read_record per source → _clean_meaning. Bounded to the already-trimmed top_n. Degrade-
    clean: a text-less / non-string-output source keeps its other fields (the `text` key is simply absent;
    that residue is the corpus-write normalisation tracked in GAP-corpus-output-nonstring.md), never a crash."""
    try:
        from runtime import corpus as _corpus
        wanted = {c.get("source") for c in context if c.get("source")}
        if not wanted:
            return context
        latest: dict[str, dict] = {}                          # source_address -> its newest corpus row (ONE scan)
        for row in _corpus.list_corpus(store):                # newest-first already (dedup-on-read)
            sa = row.get("source_address")
            if sa in wanted and sa not in latest:
                latest[sa] = row
        for c in context:
            src = c.get("source") or ""
            if src.startswith("extraction://"):                 # the dragnet extraction layer (own resolver)
                t = _extraction_text(src, max_chars=max_chars)
                if t:
                    c["text"] = t
                continue
            row = latest.get(src)
            if not row:
                continue
            rec = _corpus.read_record(store, row["address"])
            meaning = _clean_meaning(rec, max_chars=max_chars) if rec else ""
            if meaning:
                c["text"] = meaning
    except Exception:
        pass                                                  # legibility nicety, never fatal to the bundle
    return context


def recall_for_decision(suite, decision_text: str, *, address: str | None = None,
                        spaces: tuple | list | None = None, k_per_space: int = 4,
                        rerank: bool = True, top_n: int = 10,
                        include_prior_decisions: bool = True) -> dict:
    """The decision's memory-context bundle for the RHM's explanation.

    `decision_text` — the decision/question text (what the RHM explains). `address` — optional code://
    /run:// of the decision's subject (adds its neighbour node-field). `spaces` — which corpus spaces to
    draw context from (default = the why+content+history set). `include_prior_decisions` — add the
    "decisions made about this before" leg (step-6 framing). Returns
    {decision, context:[{source, space, score, ...}], neighbours:[...]?, prior_decisions:[...]?, note}.
    Read-only.

    DEGRADE-CLEAN (the no-silent-failure floor): a down embedder / empty space yields a smaller bundle +
    an honest note, never a fabricated context. FAIL-LOUD only on a malformed call."""
    if not (isinstance(decision_text, str) and decision_text.strip()):
        raise ValueError("recall_for_decision: decision_text required (the decision/question to explain).")

    spaces = tuple(spaces) if spaces else DEFAULT_DECISION_SPACES
    notes = []
    pooled: list[dict] = []
    for sp in spaces:
        try:
            out = suite.query_corpus(decision_text, space=sp, k=k_per_space)
        except Exception as e:                                   # a space may be unembedded/down — honest, not fatal
            notes.append(f"{sp}: {type(e).__name__}")
            continue
        for h in out.get("ranked", []):
            pooled.append({"source": h.get("id") or h.get("address"), "space": sp,
                           "score": round(h.get("score", 0.0), 4)})
        if out.get("note") and not out.get("ranked"):
            notes.append(f"{sp}: empty")

    # rerank the POOLED cross-space context against the decision (precision over the union of spaces) —
    # reuse the committed stage; it fetches each hit's CAS digest text (fail-loud on a blank).
    if rerank and pooled:
        try:
            from runtime import corpus_rerank as _cr
            # skip_missing=True: cross-space pool — some spaces' sources lack a CAS digest; skip those so
            # the precision pass FIRES on the with-text majority instead of degrading the whole call to cosine.
            rr = _cr.rerank_hits(suite.store, decision_text,
                                 [{"id": p["source"], "score": p["score"]} for p in pooled],
                                 top_n=top_n, skip_missing=True)
            by_src = {p["source"]: p for p in pooled}
            context = [{**by_src.get(r["address"], {}), "source": r["address"],
                        "rerank_score": r["rerank_score"], "cosine": r.get("cosine")}
                       for r in rr["reranked"]]
            notes.append(f"reranked {len(context)} (jina-v3)")
        except Exception as e:
            # rerank is precision, not correctness — degrade to cosine order, named
            context = sorted(pooled, key=lambda p: -p["score"])[:top_n]
            notes.append(f"rerank-degraded: {type(e).__name__}")
    else:
        context = sorted(pooled, key=lambda p: -p["score"])[:top_n]
        if pooled:
            # OPERATOR-VISIBLE (no-silent-failures): the degraded precision must SHOW on the card, not ride
            # invisibly. Tim-altitude wording (DNA renders this note on the explanation); points at the
            # rerank-loadout decision (board://item-a3844c46) that, once decided, can restore the sharper sort.
            notes.append("grounded by rough similarity for now — the sharper re-sorting of this context "
                         "is itself a decision waiting for you")

    # surface the digest TEXT (meaning) in each context item — the consumer (RHM/territory_prose) renders
    # the grounding from this, no re-fetch, no source-id leak (fork's gating ask, 2026-06-18). Bounded to top_n.
    _attach_digest_text(suite.store, context)

    result = {"decision": decision_text, "context": context}

    # if the decision names an addressed subject, add its neighbour node-field (recall-under-the-unit)
    if address:
        try:
            from runtime import corpus_neighbours as _nb
            nb = _nb.neighbours(suite.store, address, space="common_knowledge", k=6)
            result["neighbours"] = nb.get("neighbours", [])
            if nb.get("note"):
                notes.append(f"neighbours: {nb['note'][:60]}")
        except Exception as e:
            notes.append(f"neighbours: {type(e).__name__}")

    # "decisions made about X resurfacing" (step-6) — prior decision-content on the same topic
    if include_prior_decisions:
        try:
            pd = prior_decisions_about(suite, decision_text, k=6, rerank=rerank)
            if pd:
                result["prior_decisions"] = pd
                notes.append(f"prior_decisions: {len(pd)}")
        except Exception as e:
            notes.append(f"prior_decisions: {type(e).__name__}")

    if notes:
        result["note"] = " · ".join(notes)
    return result


def _rerank_claims(query: str, claims: list[dict], *, top_n: int = 12,
                   url: str = "http://localhost:8008/rerank", timeout: int = 60) -> list[dict]:
    """Order raw claim strings by jina-v3 relevance to `query` (the decision) — the cross-encoder reads
    query+claim TOGETHER, so it catches the homonym noise a diffuse cosine/candidate set lets through (e.g.
    a decision that says 'the INSTRUMENT drops through dimensions' pulling instrument-DISCIPLINE claims). The
    claims are raw strings with no CAS digest, so this hits the :8008 reranker transport directly (inline
    text) rather than corpus_rerank.rerank_hits (which is for addressed hits). Keyed by INDEX (chunk_id is
    not unique — one chunk yields many claims). Degrade-clean: any reranker error → claims unchanged."""
    import json as _json, urllib.request as _u
    items = [c for c in claims if isinstance(c.get("claim"), str) and c["claim"].strip()]
    if len(items) < 2:
        return claims
    try:
        cands = [{"address": str(i), "text": c["claim"], "cosine": None} for i, c in enumerate(items)]
        body = _json.dumps({"query": query, "candidates": cands, "top_n": top_n}).encode()
        req = _u.Request(url, data=body, headers={"Content-Type": "application/json"})
        resp = _json.loads(_u.urlopen(req, timeout=timeout).read())
        by_idx = {str(i): c for i, c in enumerate(items)}
        ordered, seen = [], set()
        for r in resp.get("ranking", []):
            it = r.get("item")
            idx = it.get("address") if isinstance(it, dict) else None
            c = by_idx.get(idx)
            if c is not None and idx not in seen:
                ordered.append({**c, "rerank_score": r.get("rerank_score")})
                seen.add(idx)
        for i, c in enumerate(items):                              # append any the reranker didn't return (top_n cap)
            if str(i) not in seen:
                ordered.append(c)
        return ordered or claims
    except Exception:
        return claims                                             # reranker down → determine order (honest, not a crash)


def explanation_grounding(suite, decision, *, top_n: int = 8, rerank: bool = False,
                          include_prior_decisions: bool = True) -> dict:
    """The co-owned EXPLAIN-WIRE grounding — recollection's half of projection's explain call-site.

    ★ THIS IS THE AUTHORITATIVE explain-turn ctx — NOT territory_prose. territory's memory leg auto-grounds
    the decision-CARD RESOLVE (recall_for_decision, the fast 3s cosine bundle); it carries NO theorem_claims,
    NO caveat, NO claim-rerank. The never-assert THEOREM-FORK LAW + the framework-led grounding live ONLY
    here. The dedicated explain turn (run_role(explain_role, …)) MUST draw ctx from explanation_grounding, or
    a theorem-fork explanation silently won't flag AI-projection. (Don't push the law down into
    recall_for_decision — the ~13s theorem determine would blow territory's 3s card-resolve budget.)

    projection's RHM runs the decision-explanation; the three halves MEET here:
        ctx    = explanation_grounding(suite, decision)            # ← THIS: the CONTENT (recollection)
        policy = explanation_policy_for(decision)                  # fork's seam: the SAMPLING regime
        run_role(explain_role, ctx, policy=policy,                 # the FRAMING via the subtype prompt_slot
                 coordinate={'subtype': decision['subtype']})

    `decision` — the decision RECORD (a dict carrying `meaning`/`text`/`decision` + optional `subtype` and
    `address`/`explanation_source`), OR a bare decision-text string. Composes the recall_for_decision bundle
    over the now-extraction-enriched spaces. `rerank` DEFAULTS FALSE (responsive ~5-18s for the first-run UX
    the lead is driving — the extraction layer already leads the cosine sort, verified); pass rerank=True for
    the deep jina cross-space precision pass (~57s — a background/refine turn, NOT the interactive first hit).
    NOTE: rerank governs only the CROSS-SPACE context order; the theorem-fork law (the no-fiction theorem
    determine + the per-claim rerank that orders the FRAMEWORK block) fires INDEPENDENTLY of this flag, so a
    theorem-fork explanation is correctly framework-led even at the fast default. The grounding is the CONTENT
    the explanation draws FROM — Tim's own math/relationships for a theorem-fork · the security/risk + the
    condition for an authorize · the prior decisions + the why. fork's policy picks HOW the model samples it;
    the prompt_slot picks the FRAMING; THIS supplies the WHAT.

    Returns {decision, subtype, context, prior_decisions?, neighbours?, theorem_claims, caveat, block, note}:
      • context — [{source, space, score, rerank_score?, text}] (chunk-traced, meaning-resolved, no id-leak)
      • block   — ONE ready-to-fold operator-legible MEANING string (context + priors), so projection drops a
                  single ctx field, no second render. MEANING only (recall already attached clean digest text).
      • subtype — echoed through (the coordinate projection passes to run_role) for convenience.
    No-fiction (every item is a real corpus/extraction record), read-only, degrade-clean (a down embedder →
    a thinner bundle + an honest note, never a raise — the explanation still runs)."""
    if isinstance(decision, dict):
        text = (decision.get("meaning") or decision.get("text") or decision.get("decision")
                or decision.get("question") or "")
        subtype = decision.get("subtype")
        cand = decision.get("address") or decision.get("explanation_source")
        subj = cand if (isinstance(cand, str) and cand.startswith("code://")) else None
    else:
        text = decision if isinstance(decision, str) else ""
        subtype, subj = None, None
    if not (isinstance(text, str) and text.strip()):
        raise ValueError("explanation_grounding: decision must carry text "
                         "(meaning/text/decision/question) or be a non-empty string.")

    # theorem-fork grounds in the FRAMEWORK-ONLY block (the determine over the theorem asset, below) — its
    # block DISCARDS the comprehended recall_for_decision context (it drifts; co-verified). So SKIP the full
    # 7-space recall bundle for theorem-fork — computing it then throwing it away wasted ~6-12s of the
    # explain-turn wall-clock (the 7-space query incl. the slow extractions space + prior_decisions). Other
    # subtypes need the comprehended bundle (it IS their grounding).
    _is_theorem_fork = (subtype == "theorem-fork")
    if _is_theorem_fork:
        bundle = {"context": [], "note": ""}
    else:
        bundle = recall_for_decision(suite, text, address=subj, spaces=EXPLAIN_DECISION_SPACES,
                                     rerank=rerank, top_n=top_n,
                                     include_prior_decisions=include_prior_decisions)

    # PROVENANCE per context item (operator-law + the never-assert guard): WHICH grounding is Tim's OWN
    # framework vs comprehended knowledge. The theorem extraction layer (extraction://theorem/…) is extracted
    # from Tim's own maths docs; other extractions are prior sessions/design; corpus spaces are AI-comprehended.
    ctx = bundle.get("context", [])
    for c in ctx:
        src = c.get("source") or ""
        c["provenance"] = ("your own framework" if src.startswith("extraction://theorem/")
                           else "prior sessions & design" if src.startswith("extraction://")
                           else "comprehended project knowledge")

    # THEOREM-FORK: "ground in Tim's maths, never assert" (the lead's law, 2026-06-21). The NO-FICTION
    # determine over the THEOREM asset returns ONLY Tim's real, chunk-traced theorem claims — the model
    # groups them BY INDEX and CANNOT invent claim text — so the explanation grounds in his ACTUAL
    # mathematics; the caveat forbids asserting anything beyond as his. A STRUCTURAL guard (recollection's
    # no-fiction machinery), not a prompt plea — AI-projected gloss can't masquerade as Tim's theorem.
    caveat = None
    theorem_claims: list[dict] = []
    if subtype == "theorem-fork":
        try:
            from runtime import recall_determine as _rd
            det = _rd.determine(text, asset="theorem", suite=suite, max_claims=40)
            _seen_cl = set()
            for th in det.get("themes", []):
                for cl in th.get("claims", []):
                    c = cl.get("claim")
                    if isinstance(c, str) and c.strip() and c.strip().lower() not in _seen_cl:
                        _seen_cl.add(c.strip().lower())            # dedup the near-identical preserve/cancel pairs
                        theorem_claims.append({"claim": c.strip(), "chunk_id": cl.get("chunk_id"),
                                               "theme": th.get("theme", "")})
            # ORDER by relevance to the decision (the cross-encoder catches homonym noise the determine's
            # candidate-filter let through) → the framework block LEADS with Tim's most on-topic maths.
            theorem_claims = _rerank_claims(text, theorem_claims, top_n=12)
        except Exception:
            pass
        caveat = ("GROUND ONLY in the framework statements below — these are the SYSTEM'S EXTRACTIONS of Tim's "
                  "written mathematics (traceable to his notes, faithful compressions — NOT his literal words). "
                  "So: attribute the IDEAS to him, but do not present the wording as his exact quote, and frame "
                  "them as 'your framework, as the system reads it.' Anything NOT in these statements is YOUR "
                  "projection — flag it explicitly as AI-inference, NEVER assert a gloss as his theorem. When "
                  "unsure, say so. (The cube-error proved the AI misreads here — under-claim, never over-claim.)")

    # render ONE operator-legible meaning block, so projection folds a SINGLE ctx field. recall already
    # attached each context item's clean digest text (operator-law: meaning, never a source-id/jargon leak).
    # theorem-fork LEADS with Tim's verbatim framework (the never-assert anchor) before the surrounding
    # context; other subtypes use the clean reranked context. This formats recollection's OWN bundle — NOT a
    # second territory_prose (that renders the full multi-leg operator card; this is the narrower explain ctx).
    # ★ THEOREM-FORK = FRAMEWORK-ONLY block (the never-assert law made structural; co-verified by-use
    # 2026-06-21 with fork's explain_role). The law is "ground ONLY in his WRITTEN MATHEMATICS" — so a
    # theorem-fork explanation grounds in the chunk-traced theorem claims ALONE. The comprehended surrounding
    # context (history/repo/project chatter) and prior decisions are NOT his maths, and the co-verify proved
    # they DRIFT the small model: on the dimension-meaning (cube-error) decision, one '[history] expanded
    # multi-embedding' context item pulled the whole explanation off onto embedding-models; framework-only made
    # it correctly explain his dimension=recursion-axis theorem. So for theorem-fork: framework claims only.
    # (The full `context`/`prior_decisions` still ride the RETURN for transparency/other consumers — just not
    # the explain BLOCK.) Other subtypes: the clean reranked comprehended context + priors (their grounding IS
    # the project context — no never-assert restriction).
    lines: list[str] = []
    pri = bundle.get("prior_decisions") or []
    if theorem_claims:
        lines.append("YOUR FRAMEWORK — the system's faithful EXTRACTIONS of your written mathematics (traceable "
                     "to your notes; compressions, not your literal words). Ground ONLY here; attribute the ideas "
                     "to you, but don't quote them as your exact wording, and flag anything beyond as the AI's reading:")
        for tc in theorem_claims[:12]:
            lines.append(f"  • {tc['claim']}")
    else:
        for c in ctx:
            t = c.get("text")
            if isinstance(t, str) and t.strip():
                lines.append(f"- {t.strip()}")
        if pri:
            _attach_digest_text(suite.store, pri)
            for pd in pri:
                t = pd.get("text")
                if isinstance(t, str) and t.strip():
                    lines.append(f"- (you've weighed this before) {t.strip()}")
    block = "\n".join(lines)

    return {"decision": text, "subtype": subtype, "context": ctx,
            "prior_decisions": pri, "neighbours": bundle.get("neighbours", []),
            "theorem_claims": theorem_claims, "caveat": caveat,
            "block": block, "note": bundle.get("note", "")}


if __name__ == "__main__":
    # verify-by-use self-test: a real pending-decision-shaped query → the context bundle
    import sys, os, json
    sys.path.insert(0, "/home/tim/company"); os.chdir("/home/tim/company")
    from runtime.suite import Suite
    from runtime.registry import NodeRegistry
    from store.fs_store import FsStore
    s = Suite(FsStore(".data/store"), NodeRegistry().discover(["nodes"]), nodes_dir="nodes")
    q = "should file/content identity be addressed by path or by content hash — the union's identity decision"
    out = recall_for_decision(s, q, k_per_space=4, top_n=8)
    print(f"decision: {out['decision'][:60]}…")
    print(f"note: {out.get('note','')}")
    print(f"context ({len(out['context'])} items, the RHM's grounding):")
    for c in out["context"][:8]:
        sc = c.get("rerank_score", c.get("score"))
        print(f"  [{sc:+.3f}] ({c.get('space','?')}) {(c.get('source') or '')[:62]}")
