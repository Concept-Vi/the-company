"""runtime/brain_router.py — the SUPERVISOR-AS-LOADABLE-BRAIN, backend half (the RHM mind as a source-router).

THE ARCHITECTURE (build-prep/the-one-application/SUPERVISOR-AS-BRAIN.md): the RHM's mind is no longer a single
model — it RESOLVES which cognition-SOURCE answers a question, and the supervisor's fleet-sight is one source.
This module is the BACKEND half: given (question, aim), pick a source by the question's shape, compose the answer.
The FRONTEND half is `window.forkVBrain` (a DOM module mounted by surface/.../RightHand.tsx — projection/DNA's
lane: turn/stream/write into the panel); it calls this backend via /api/brain/ask. The DOM object is NOT built
here (not fork's lane); the COGNITION behind it is.

★ IT IS THE RESOLVER, ONE ALTITUDE UP (the spine, not a new pattern): the source-selection is a DISCRETE
resolve_slot select (question-shape → source) — runtime.resolver, the SAME primitive a surface uses to pick an
allocation by device-coordinate. Each source then composes EXISTING, ALREADY-BUILT parts (reuse-don't-parallel):
  • 'fleet'   → the SUPERVISOR source: the live roster + session list (session_channels.fold_channels +
                Suite.list_agent_sessions — the read-routes built this session). READ+PROPOSE: it can SEE the
                fabric and SURFACE "I could wake/consult session X" — it NEVER spawns/wakes (that's gated,
                lead-only: autonomous-spawn-lead-only). The mind reaches the gated verb, never fires it.
  • 'recall'  → grounded memory (the recall path — left as a declared hook here; recollection owns the backend,
                the route is /api/transcript-search / recall_for_decision — composed by the caller, not duplicated).
  • 'model'   → the default conversational mind: Suite.chat (today's whole RHM mind; stays the default/fallback).

THE FLOOR: this is a READ + a model-run + a PROPOSE. It emits NO resolve_address/approve/dispatch/spawn. A
'fleet' answer that implies an action returns it as a PROPOSAL (an explain string + a suggested gated-action the
operator/lead fires), never an executed one.

FAIL-SOFT: an unroutable question → 'model' (the safe default); a down source → degrade to 'model' with a note,
never a crash (the brain must always answer something). Pure-ish: the model/recall legs do IO, but routing is
deterministic given the question.
"""
from __future__ import annotations

import re
from typing import Any

# The source-selection is data: a keyword→source map the resolver selects over. NOT hardcoded branching —
# it's a declared routing table (axes-are-registries: a new source = a row). Conservative + explainable.
_FLEET_HINTS = ("fleet", "session", "sessions", "channel", "channels", "who is", "what is running",
                "what's running", "wake", "consult", "supervisor", "agent", "lane", "what are you all",
                "drift", "roster")
_RECALL_HINTS = ("remember", "recall", "what did we decide", "what was decided", "history", "past",
                 "earlier", "transcript", "what happened", "memory")


def route_source(question: str) -> str:
    """DETERMINISTIC source pick from the question's shape → 'fleet' | 'recall' | 'model'. The discrete
    select (resolver's axis-kind): a fleet/supervisor question → 'fleet'; a memory question → 'recall';
    else the default conversational 'model'. Lowercased substring match (conservative; ties → fleet>recall>model
    by specificity of the fabric-state question). This is the registry-data the resolver would select over —
    inline here as the v1 table (a source = a hint-row; extend without engine change)."""
    q = (question or "").lower()
    if any(h in q for h in _FLEET_HINTS):
        return "fleet"
    if any(h in q for h in _RECALL_HINTS):
        return "recall"
    return "model"


def recent_channel_context(suite, *, channel: str | None = None, limit: int = 12) -> dict:
    """L4 — the brain's channel-READ tool (the SAFE half). Reads RECENT channel traffic as CONTEXT so the
    brain (/api/brain/ask) can answer GROUNDED in what the fabric has actually said — not just channel/session
    COUNTS. REUSE-DON'T-PARALLEL: composes session_channels.channel_events_since + the body-resolve (the same
    read /api/channel-history serves), no parallel reader. `channel` scopes to one channel (bare or chan://);
    None = across all channels. `limit` = the most-recent N posts.

    THE FLOOR: READ-ONLY. This tool NEVER posts — the channel-POST half stays PROPOSE-gated (the brain reads +
    proposes a gated action; the operator/lead fires it; autonomous-spawn-lead-only). Returns
    {recent:[{channel, from, message, ts, seq}], n} oldest→newest (newest last)."""
    from runtime.session_channels import channel_events_since
    evs = [e for e in channel_events_since(suite.store, -1, channel=channel)
           if e.get("kind") == "channel.posted"]
    recent = evs[-limit:] if (limit and limit > 0) else evs
    out = []
    for e in recent:
        body = suite.store.get_content(e["cas"]) if e.get("cas") else None
        out.append({"channel": e.get("channel"), "from": e.get("from"),
                    "message": body, "ts": e.get("ts"), "seq": e.get("seq")})
    return {"recent": out, "n": len(out)}


def _fleet_answer(question: str, *, suite) -> dict:
    """The SUPERVISOR source — compose the LIVE fabric-state from the already-built reads (fold_channels +
    list_agent_sessions). READ + PROPOSE only: it describes the fleet and may SURFACE a gated action as a
    proposal; it NEVER spawns/wakes (the floor). Returns {source, answer, fleet, proposal?}."""
    from runtime.session_channels import fold_channels
    channels = list(fold_channels(suite.store).values())
    sessions = suite.list_agent_sessions(limit=50)
    rows = sessions.get("sessions", sessions) if isinstance(sessions, dict) else sessions
    live = [s for s in rows if isinstance(s, dict) and "live" in str(s.get("state", "")).lower()]
    n_ch, n_live = len(channels), len(live)
    # a plain-meaning summary (operator-law: human, never machine ids in the answer prose)
    answer = (f"The fabric has {n_ch} channel{'s' if n_ch != 1 else ''} and {n_live} live "
              f"session{'s' if n_live != 1 else ''} right now.")
    # PROPOSE (never fire): if the question asks to wake/consult, surface it as a suggested gated action.
    proposal = None
    if re.search(r"\b(wake|consult|run|resume)\b", (question or "").lower()):
        proposal = {"kind": "supervisor_action", "is_gated": True,
                    "suggestion": "Waking or consulting a session is a gated action — surface it for the "
                                  "operator/lead to run; the mind proposes, it does not spawn.",
                    "note": "floor: brain proposes, never dispatches (autonomous-spawn-lead-only)."}
    # L4: read RECENT channel traffic as CONTEXT (the safe read-tool) — so the brain SEES what the fabric
    # has said, not just counts. The structured channel_context rides for the frontend (forkVBrain, L2);
    # the answer prose notes its presence. READ-ONLY (the post half stays propose-gated).
    ctx = recent_channel_context(suite, limit=12)
    if ctx["n"]:
        answer += (f" Recent channel traffic: {ctx['n']} message{'s' if ctx['n'] != 1 else ''} "
                   f"available as context.")
    return {"source": "fleet", "answer": answer,
            "fleet": {"channels": n_ch, "live_sessions": n_live},
            "channel_context": ctx["recent"], "proposal": proposal}


# The brain's typical interactive-Q&A context magnitude (system persona + grounded context + history +
# tools) — measured ~12K, headroom to ~16K. Feeds the TIM-RULE context-size pick: well under kimi's 256K
# window → kimi (never the 1M deepseek-flash unless a turn's context truly exceeds 256K). A precise
# per-turn estimate is a follow-on; the rule lands on kimi for any normal interactive turn.
_BRAIN_CTX_ESTIMATE = 16000


def _model_answer(question: str, aim: str | None, *, suite, graph_id: str = "codebase") -> dict:
    """The conversational source — Suite.chat (the grounded RHM mind). THE BRAIN IS A ROLE THAT RESOLVES
    TO A MODEL (Tim 2026-06-21 direct): the model is the TIM-RULE context-size pick
    (cc_clone.pick_ollama_model_for_context — kimi default, the cheap 1M deepseek-flash when ctx>kimi, NEVER
    -pro unless explicit), NOT a hardcoded DEFAULT_BRAIN (the anti-pattern). A ~12-16K interactive grounded
    turn resolves to KIMI (fits its 256K window), hit via the LOCAL ollama host (OLLAMA_DIRECT :11434 —
    proven tool-calling). Resolved, not pinned ⇒ swappable per the mode-loadout-registry (the native-model-
    layer's first real instance: the brain = one row in the role→model resolution). The fallback for any
    non-fleet/non-recall question + the degrade target. Returns {source, answer, raw, brain_model, brain_pick}."""
    from runtime.cc_clone import pick_ollama_model_for_context
    from fabric.config import OLLAMA_DIRECT
    brain_model, why = pick_ollama_model_for_context(_BRAIN_CTX_ESTIMATE)
    # AIM-GROUNDING (Tim's V core value): when the V is aimed at something, FOLD that thing's territory into
    # the turn (territory_prose — the SAME [Operator context] block the streaming /api/claude/turn path folds)
    # so the grounded mind answers ABOUT the aimed card, not from general state ("I cannot see a specific
    # decision card" was the gap). suite.chat's `focus` alone did not inject it. Fail-soft: territory_prose
    # never raises; a thin/empty territory just omits the block (the answer still fires — the floor).
    asked = question
    if aim:
        try:
            from runtime.territory import territory_prose
            terr = territory_prose(aim, suite=suite)
            if terr and terr.strip():
                asked = ("[What you're looking at]\n" + terr.strip()
                         + "\n\n[The operator's question]\n" + question)
        except Exception:
            pass
    res = suite.chat(asked, graph_id, focus=({"address": aim} if aim else None),
                     model=brain_model, base_url=OLLAMA_DIRECT)
    # suite.chat's answer rides under `reply` (the epilogue shape); `text`/`answer` are tolerated fallbacks
    # (prologue off/refusal shapes). The old `res.get("text")` was always None for the normal shape — masked
    # only because the mis-pointed 4B 400'd before returning; the kimi pick surfaced it (fixed here).
    text = (res.get("reply") or res.get("text") or res.get("answer")) if isinstance(res, dict) else str(res)
    return {"source": "model", "answer": text, "raw": res, "brain_model": brain_model, "brain_pick": why}


def ask(question: str, *, suite, aim: str | None = None, graph_id: str = "codebase") -> dict:
    """THE BRAIN — resolve the source, compose the answer. The backend /api/brain/ask calls this; the
    frontend forkVBrain renders it. FAIL-SOFT: a down/erroring source degrades to 'model' with a note
    (the mind always answers). Returns {source, answer, ...} (+ routed_from on a degrade).

    `recall` source: a DECLARED HOOK — recollection owns the recall backend (the route is
    /api/transcript-search / recall_for_decision). v1 routes a recall question to the model (which is
    itself grounded via Suite.chat's tool-calling), and FLAGS recall as the richer source to wire. So no
    duplication of recollection's lane; the seam is named, not faked."""
    src = route_source(question)
    try:
        if src == "fleet":
            return _fleet_answer(question, suite=suite)
        if src == "recall":
            # recollection's lane: the grounded-recall source. v1 = the model (tool-calling-grounded) + a
            # named seam to wire recollection's search/determine as a first-class source. No fake recall.
            out = _model_answer(question, aim, suite=suite, graph_id=graph_id)
            out["recall_seam"] = ("a richer 'recall' source (recollection's session_search/recall_for_decision) "
                                  "can compose here — v1 answers via the tool-grounded model.")
            return out
        return _model_answer(question, aim, suite=suite, graph_id=graph_id)
    except Exception as e:                       # fail-soft: any source error → the model default, never a crash
        if src != "model":
            try:
                out = _model_answer(question, aim, suite=suite, graph_id=graph_id)
                out["routed_from"] = src
                out["degrade_note"] = f"{src} source errored ({type(e).__name__}); answered via the model."
                return out
            except Exception as e2:
                return {"source": "error", "answer": None,
                        "error": f"both {src} and model failed: {e!r} / {e2!r}"}
        return {"source": "error", "answer": None, "error": f"model source failed: {e!r}"}
