"""runtime/keeper.py — THE KEEPER as a COMPOSITION (④ THE CONTAINER · L7-KEEPER, organ-studies/KEEPER.md §4).

The tending AI is NOT a new primitive. It is FOUR existing addresses composed at project://<key>:
  · binding      — a member EDGE agent://keeper —member-of→ project://<key> (L1, written at project birth)
  · behavior     — a CAST: cast_for_mode('keeper') — roles/ files declaring mode_scope ⊇ {keeper}
  · parametrization — CONFIG RUNGS: container.config_rung rows keyed (address_prefix, config_key), resolved
                   through the ONE ladder slot-kind (runtime/resolver.py) — longest-prefix-on-address wins
  · identity     — a PERSONA record: config_key='persona' (universal rung = the global persona;
                   a deeper project rung OVERRIDES it; removal restores inheritance — C7.5)

THE ONE LADDER (reuse-don't-parallel, the ONE-ladder law): keeper config, per-project role framing, and
token values ALL resolve through runtime.resolver.resolve — NOT a second resolver. ci_resolve_keeper_config's
`ORDER BY override_level DESC LIMIT 1` == the ladder's longest-prefix-wins. override_level WAS containment
depth in disguise — the ADDRESS is the level (KEEPER.md §4.2).

DB READ CONVENTION: reuses runtime.scope._q/_lit (the ONE env-overridable ledger-Postgres convention) —
no parallel connection code. A down DB / absent rung → a LEGIBLE absent (never a silent wrong value).

ONE FUNCTION, TWO FACES (C7.4): keeper_answer(address, question, token) is called BY the MCP `keeper` tool
AND the /api/keeper bridge route — the same envelope from both (law 9: the faces cannot diverge).
"""
from __future__ import annotations

import json
from typing import Any

from runtime.scope import _q, _lit
from runtime.resolver import resolve_slot, ResolverError

_BREADCRUMB = ("source = container.config_rung (0023_keeper.sql, ④ L7-KEEPER; Supabase 127.0.0.1:15432). "
               "If a rung is missing, apply the migration + seed: psql -f build-prep/claude-design/supabase/"
               "supabase/migrations/0023_keeper.sql")


# ── config rungs → the ONE ladder ────────────────────────────────────────────────────────────────
def _rungs_for(config_key: str) -> dict[str, Any]:
    """Every rung of ONE config_key as {address_prefix: config_value}. Reuses scope._q (the ONE DB
    convention). A down DB RAISES (fail loud — never a silent empty ladder that would mis-resolve)."""
    ok, out = _q(
        "select coalesce(json_object_agg(address_prefix, config_value), '{}'::json) "
        f"from container.config_rung where config_key = {_lit(config_key)}")
    if not ok:
        raise RuntimeError(f"keeper: container.config_rung unreachable ({out[:200]}) — {_BREADCRUMB}. Fail loud.")
    return json.loads(out.strip() or "{}")


def resolve_config(config_key: str, coordinate: dict) -> Any:
    """Resolve ONE config_key at the coordinate's address through the ONE ladder (longest-prefix-wins,
    walk up on absence). A config_key with NO rungs at all is the cloud's LEGIBLE ABSENT
    ({_not_configured: true} — ci_resolve_keeper_config's contract), NOT an error. A config_key that HAS
    rungs but none covers the address AND has no default falls back to the legible absent too (walk-up
    exhausted → not configured here). This is the CONFIG layer's choice; the raw ladder slot itself
    fail-louds (that fail-loud-below is proven directly against resolve_slot / in keeper_acceptance)."""
    rungs = _rungs_for(config_key)
    if not rungs:                                             # never configured anywhere → legible absent
        return {"_not_configured": True, "config_key": config_key}
    invariant_slot = {"ladder": "address", "rungs": rungs,
                      "default": {"_not_configured": True, "config_key": config_key}}
    return resolve_slot(invariant_slot, coordinate)


# ── the capability flags GATE the governed verb whitelist (C7.2) ───────────────────────────────────
# The cloud navigation_capabilities / creation_capabilities flags "finally execute" (KEEPER.md §4.5 step 3,
# §3 IMPLIED-BUT-ABSENT: "A's flags never gate anything observable; B's verb whitelist (RHM_VERBS) is
# exactly the gate they should feed"). Each GOVERNED verb (Suite.RHM_VERBS) requires a capability flag; the
# keeper may perform the verb IFF the flag resolves TRUE at its address. A verb with no mapping is a
# keeper SELF-op (configure/voice) — never capability-gated. The mapping is the SEAM (data, documented):
#   navigation_capabilities  → the READ/NAVIGATE verbs   (the keeper reads + moves the view)
#   creation_capabilities    → the CREATE/CHANGE verbs   (the keeper makes/annotates)
_VERB_CAPABILITY = {
    # verb        (config_key,                 flag)
    "run":            ("navigation_capabilities", "search_resources"),
    "consult":        ("navigation_capabilities", "search_resources"),
    "show":           ("navigation_capabilities", "traverse_hierarchy"),
    "build":          ("creation_capabilities",   "create_resources"),
    "extend":         ("creation_capabilities",   "create_resources"),
    "panel":          ("creation_capabilities",   "create_resources"),
    "propose":        ("creation_capabilities",   "create_workflows"),
    "request_change": ("creation_capabilities",   "annotate_entities"),
    # configure / load_voice / unload_voice → keeper self-ops, NOT capability-gated (see _SELF_OPS).
}

# EXPLICIT self-op allowlist (④ L7 adversary fix — fail-CLOSED on an unmapped verb): a governed verb is
# permitted without a capability gate ONLY if it is a declared keeper self-op. Any governed verb that is
# neither in _VERB_CAPABILITY nor here is DENIED (a future RHM verb added without a mapping fails closed,
# never silently allowed). A drift check (keeper_acceptance) asserts every governed verb is classified.
_SELF_OPS = frozenset({"configure", "load_voice", "unload_voice"})


def _governed_verbs() -> tuple[str, ...]:
    """The governed verb whitelist = Suite.RHM_VERBS (the ONE source; lazy import avoids a load cycle —
    suite calls keeper, not the reverse)."""
    from runtime.suite import Suite
    return tuple(Suite.RHM_VERBS)


def keeper_verbs(coordinate: dict) -> dict:
    """The keeper's ALLOWED governed verbs at the coordinate's address, gated by the resolved capability
    flags. Returns {allowed:[...], denied:{verb: reason}, capabilities:{navigation, creation}} — the
    keeper's effective whitelist, LEGIBLE (what it may + why each denial). Fail-closed: a flag that does
    not resolve truthy DENIES its verb."""
    nav = resolve_config("navigation_capabilities", coordinate)
    crt = resolve_config("creation_capabilities", coordinate)
    caps = {"navigation_capabilities": nav, "creation_capabilities": crt}
    allowed, denied = [], {}
    for verb in _governed_verbs():
        req = _VERB_CAPABILITY.get(verb)
        if req is None:                                      # not capability-mapped
            if verb in _SELF_OPS:                            # a DECLARED self-op — allowed, not gated
                allowed.append(verb)
            else:                                            # unmapped governed verb → FAIL CLOSED
                denied[verb] = ("unclassified governed verb: not in _VERB_CAPABILITY and not a declared "
                                "keeper self-op (_SELF_OPS). Fail-closed — add a capability mapping or "
                                "declare it a self-op in runtime/keeper.py. Never silently permitted.")
            continue
        cfg_key, flag = req
        flags = caps[cfg_key]
        if isinstance(flags, dict) and flags.get(flag) is True:
            allowed.append(verb)
        else:
            state = "not configured" if (isinstance(flags, dict) and flags.get("_not_configured")) \
                else f"{cfg_key}.{flag} is not enabled at this address"
            denied[verb] = f"denied: {state} (keeper capability rung excludes it; {_BREADCRUMB})"
    return {"allowed": allowed, "denied": denied, "capabilities": caps}


def keeper_guard(verb: str, coordinate: dict, do, *, confirmed: bool = False, inbox=None,
                 payload: dict | None = None, ceiling: str | None = None):
    """Perform a GOVERNED verb AS the keeper: FIRST the capability whitelist gate (a verb the keeper's
    rung excludes FAILS LOUD, naming the excluding rung), THEN the ordinary governance posture gate
    (governance.guard on the verb's action-class — reuse, NOT a parallel gate; the delegation `ceiling`
    still applies). This is where the cloud's inert flags finally EXECUTE (C7.2)."""
    from runtime import governance
    from runtime.suite import Suite
    if verb not in _governed_verbs():
        raise governance.GovernanceError(
            f"keeper: {verb!r} is not a governed verb (whitelist = {list(_governed_verbs())}); the "
            f"conversational keeper surface can never reach apply/delete/file-write (no-bypass). Fail loud.")
    v = keeper_verbs(coordinate)
    if verb in v["denied"]:
        raise governance.GovernanceError(
            f"keeper may not '{verb}' at {coordinate.get('address')!r} — {v['denied'][verb]}")
    action_class = Suite.RHM_VERB_SPECS[verb].action_class    # the ONE verb→class source (no drift)
    return governance.guard(action_class, do, confirmed=confirmed, inbox=inbox,
                            payload=payload, ceiling=ceiling)


# ── the persona record resolves into the prompt (C7.5) ─────────────────────────────────────────────
def resolve_persona(coordinate: dict) -> dict | None:
    """The keeper's persona AT this address (universal rung = global; a deeper project rung OVERRIDES;
    removal restores inheritance). Returns the persona dict, or None when unconfigured (legible absent)."""
    p = resolve_config("persona", coordinate)
    if isinstance(p, dict) and p.get("_not_configured"):
        return None
    return p


def _persona_block(persona: dict | None) -> str:
    """Render the persona INTO the prompt under '## Persona' (mirrors vi_persona's 'read into every prompt
    under ## Persona'). Absent persona → an empty string (no block), never a fabricated identity."""
    if not persona:
        return ""
    name = persona.get("name", "Keeper")
    voice = persona.get("voice", "")
    stance = persona.get("stance", "")
    return f"## Persona\nYou are the {name}. {voice}\n{stance}".strip()


# ── the CONTEXT ENVELOPE + keeper_answer (C7.4) ────────────────────────────────────────────────────
def _coordinate(address: str, token: dict | None) -> dict:
    """Build the turn COORDINATE from the address + the surface token (KEEPER.md §4.3). Only the small,
    serializable coordinate + trail accrete; territory is composed (never accreted). `response_style`
    resolves through the ladder (a token value = ladder-then-select), defaulting to 'standard' so a
    keeper role's prompt_slot select on it always has a value (the ladder specialises it per project)."""
    coord = {"address": address, "mode": "keeper"}
    if isinstance(token, dict):
        coord.update({k: v for k, v in token.items() if k not in ("address", "mode")})
    rs = resolve_config("response_style", coord)
    coord["response_style"] = rs if isinstance(rs, str) else "standard"
    return coord


def compose_envelope(address: str, question: str, token: dict | None = None, *, suite=None, store=None) -> dict:
    """Compose the CONTEXT ENVELOPE (KEEPER.md §4.3) at an address — the DETERMINISTIC half of a keeper
    turn: coordinate (accretes) + territory (composed, never accreted) + resolved config/persona/verbs +
    the trail (who accreted what). This is what the two faces must AGREE on (the LLM answer varies; the
    envelope does not). Every leg guarded → a dead leg is a noted-absent, never a killed turn."""
    from runtime.territory import territory_for, territory_prose
    coord = _coordinate(address, token)
    trail: list[dict] = [{"stage": "arrive", "added": ["address", "mode", "response_style"], "at": address}]

    # COMPOSE — territory (guarded; territory_for never raises, it degrades to noted-absent legs).
    try:
        territory = territory_for(address, suite=suite, store=store)
        prose = territory_prose(territory, suite=suite, store=store)
        trail.append({"stage": "compose", "added": ["territory", "prose"],
                     "legs_present": territory.get("legs_present")})
    except Exception as e:                                    # never fatal — a noted-absent territory
        territory = {"identity": None, "notes": [f"territory unresolved ({type(e).__name__}: {e})"]}
        prose = ""
        trail.append({"stage": "compose", "added": [], "note": f"territory degraded: {type(e).__name__}"})

    # PARAMETRIZE — the config rungs resolve through the ONE ladder; the flags gate the verb whitelist.
    init = resolve_config("initialization_procedure", coord)
    domain = resolve_config("domain_expertise", coord)
    persona = resolve_persona(coord)
    verbs = keeper_verbs(coord)
    trail.append({"stage": "parametrize",
                 "added": ["initialization_procedure", "domain_expertise", "persona", "governed_verbs"],
                 "verbs_allowed": verbs["allowed"], "verbs_denied": list(verbs["denied"]),
                 "persona": (persona or {}).get("name") if persona else None})

    return {
        "coordinate": coord,
        "territory": territory,
        "prose": prose,
        "config": {"initialization_procedure": init, "domain_expertise": domain, "persona": persona},
        "verbs": verbs,
        "trail": trail,
    }


def keeper_context_block(envelope: dict) -> str:
    """The keeper's grounding that RESOLVES INTO THE PROMPT (KEEPER.md §4.5 step 4; C7.5). The persona
    ('## Persona', mirroring vi_persona's 'read into every prompt under ## Persona'), the resolved domain
    expertise, and the composed territory prose ('[Project context]') — folded into the model's USER
    content. (run_role does NOT .format the system prompt, so the DYNAMIC, per-address, DB-resolved framing
    rides here; the role's prompt_slot carries the per-project STYLE, C7.3, resolved against the coordinate.)
    A deeper persona rung OVERRIDES the '## Persona' block; removal restores the global one — demonstrable
    by inspecting THIS block (or envelope['config']['persona']) before/after a DB rung write."""
    persona = envelope["config"].get("persona")
    domain = envelope["config"].get("domain_expertise")
    parts = []
    pb = _persona_block(persona)
    if pb:
        parts.append(pb)
    if isinstance(domain, dict) and not domain.get("_not_configured") and domain.get("specializations"):
        parts.append("## Domain expertise\nThis project's keeper specialises in: "
                     + ", ".join(domain["specializations"]) + ".")
    if envelope.get("prose"):
        parts.append("[Project context]\n" + envelope["prose"])
    return "\n\n".join(parts).strip()


def keeper_answer(address: str, question: str, token: dict | None = None, *,
                  suite=None, store=None, fire: bool = True) -> dict:
    """THE keeper answers about its project (KEEPER.md §4.5). ONE function → two faces (MCP + HTTP).

    ARRIVE → COMPOSE (territory over project://<key> — the live ledger data) → PARAMETRIZE (config rungs
    through the ONE ladder; flags gate the verbs) → FIRE (cast_for_mode('keeper'); slots resolve against
    the SAME coordinate; the persona/domain in the system framing; the prose as the [Project context]) →
    ANSWER + ACCRETE (the envelope returns enriched with a trail).

    Returns {answer, envelope, cast}. `fire=False` composes the envelope WITHOUT calling the model (the
    deterministic half — the two faces compare THIS; the model text varies per draw)."""
    from runtime.cognition import role_registry

    envelope = compose_envelope(address, question, token, suite=suite, store=store)
    coord = envelope["coordinate"]
    cast = role_registry().cast_for_mode("keeper")
    envelope["trail"].append({"stage": "fire", "cast": [r.id for r in cast]})

    answer: Any = None
    cast_out: dict[str, Any] = {}
    if fire:
        from runtime.cognition import run_role
        # The persona+domain+prose (DB-resolved, per-address) ride in the USER content; the role's
        # prompt_slot resolves the per-project STYLE (C7.3) against the SAME coordinate as the SYSTEM prompt.
        user = f"{question}\n\n{keeper_context_block(envelope)}".strip()
        for role in cast:
            if not getattr(role, "can_fire", False):
                continue                                     # non-fireable cast members (juries etc.) — skip
            try:
                r = run_role(role, {"utterance": user}, coordinate=coord, store=store, temperature=0)
                cast_out[role.id] = r
            except Exception as e:                           # a dead cast-leg is noted-absent, never fatal
                cast_out[role.id] = {"_error": f"{type(e).__name__}: {e}"}
        # the ANSWER = the keeper_reader role's output (the answering role); else the first fired role.
        primary = cast_out.get("keeper_reader")
        if primary is None:
            primary = next((v for v in cast_out.values() if isinstance(v, dict) and "_error" not in v), None)
        answer = primary
        envelope["trail"].append({"stage": "answer",
                                 "fired": [k for k, v in cast_out.items() if "_error" not in v],
                                 "failed": [k for k, v in cast_out.items() if "_error" in v]})

    return {"answer": answer, "envelope": envelope, "cast": cast_out}
