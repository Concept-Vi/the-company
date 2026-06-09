"""C5 (sibling) — `/cognition_info` serialization: the cognition registries → frontend.

The live COGNITION VIEW (build-prep/concurrent-cognition/06-rendering.md §F) is a GENERIC
renderer of the collective-cognition layer — exactly as the canvas is a generic renderer of
node-types. It holds no per-role / per-rule code: it asks the runtime for the whole cognition
registry, SERIALIZED, and from that draws roles-as-nodes, chains/injections-as-edges, the
status vocabulary, the rule badges, the edge-kind labels.

This module is the **sibling of contracts/object_info.py** (06 §B.3 / §F#1 names it exactly):
where `build_object_info` serializes the C2 `NodeType` library, `build_cognition_info`
serializes the cognition registries —
  - the FILE-DISCOVERED roles (runtime/roles.py · roles/*.py),
  - the declared routing RULES (runtime/rules.py — the G3 AST rules + RULE_OPS/DESTINATION_KINDS),
  - the EDGE_KINDS vocabulary (contracts/node_record.py — the C1.3 edge labels),
  - the THOUGHT_SHAPES archetypes (the ~5 reply shapes),
  - the ACTIVATION_CONTEXTS (the dial generalised — when a cast fires),
  - the per-turn cognition.* event-kind CONTRACT the live view binds to.

GENERATED FROM the registries — never hand-written (mirrors object_info.py:7-10). Add a role
file / a rule / an edge-kind → it self-registers → `/cognition_info` gains an entry → the FE
re-merges → it appears live, no FE code (the ComfyUI pattern 06 §B.3 cites — "dynamic").

Fail loud (rule 4 / object_info.py:79-83): a registry KEY that disagrees with the thing's own
`id` raises rather than emitting a silently-wrong projection.

Schema-additive (rule 2): new serialized fields carry defaults; an older FE ignores fields it
doesn't know, so backend and FE evolve at different speeds. `SCHEMA_VER` is bumped additively.
"""
from __future__ import annotations

from typing import Any

# Bumped when the SERIALIZATION shape changes (additively). Lets the FE reason about which
# serialized fields it can expect. Distinct from any one registry's own version marker.
# v2: the corpus pillar's file-discovered registries (projections/spaces + lifters/mark_types/
# generation_policies/relation_types/ai_tics/forms) are now serialized keys — schema-additive,
# so an older FE ignores them; a v2-aware FE keys off schema_ver>=2 to expect the 6 registries.
SCHEMA_VER = 2


# =====================================================================================================
# THE COGNITION.* EVENT-KIND CONTRACT (the emit-contract the live FE binds to — 06 §F#3)
#
# The per-turn lifecycle events the staged-turn path (Suite.chat_parts) emits onto the ONE event log,
# served on /api/stream. Declared HERE as DATA (registry-is-truth) so the FE binds to a REAL contract,
# not an invented one (06 §F: "a render design that binds to event kinds nothing emits would float").
# Drift home: runtime/AGENTS.md (alongside RULE_OPS/DESTINATION_KINDS/THOUGHT_SHAPES/PART_GRAIN/
# ACTIVATION_CONTEXTS); tests/cognition_info_acceptance.py asserts it stays reflected there + that the
# live emits match these field declarations (mirrors edge_kinds_acceptance → contracts/AGENTS.md).
#
# THE FLOOR (C9.2): these are NARRATION (lenient telemetry via _emit) — they READ-only reflect backend
# truth (reflects-never-owns). NONE is a resolve/approve/dispatch; a cognition.* event can never forge
# an operator action (the claude -p floor is lead-only).
# =====================================================================================================
COGNITION_EVENT_KINDS: dict[str, dict] = {
    "cognition.turn.start": {
        "desc": "a staged turn began — the swarm is about to fire. The view opens a turn frame.",
        "fields": {"turn_id": "str", "mode": "str", "shape": "str (THOUGHT_SHAPES archetype)",
                   "grain": "str (PART_GRAIN grain)", "cast": "list[str] (fireable role ids)",
                   "address": "str — ui://cognition/<turn> (the turn locus, C7.2)"},
    },
    "cognition.role.fire": {
        "desc": "a role's model call is being launched (the role dot goes 'firing'). Emitted "
                "synchronously before the wave starts — deterministic, one per fireable role.",
        "fields": {"turn_id": "str", "role": "str (role id)", "model": "str (effective model)",
                   "address": "str — run://<turn>/<role> (the role instance locus, reuse not cog://)"},
    },
    "cognition.role.ran": {
        "desc": "a role returned (the dot goes 'ran' / 'failed'). Read off the wave's RoleRun records "
                "after the barrier — carries its run:// address + ok + ms.",
        "fields": {"turn_id": "str", "role": "str", "ok": "bool", "ms": "int",
                   "error": "str|None (present only on failure)",
                   "address": "str — run://<turn>/<role>"},
    },
    "cognition.inject": {
        "desc": "a declared G3 rule injected a role's resolved output into the final reply part (the "
                "injection edge SOURCE role → brain lights up — 06 §C/§D). One per firing inject rule. "
                "The `source` role is always identified (recovered from the rule's value_path when the "
                "rule isn't role-attached) so L-fe can draw the source→brain edge. `cost` (the edge "
                "weight — cheap/loads-corpus, 06 §F) is DEFERRED until C6 faculty injections exist; "
                "today's injects are role-output injections, so no cost field is emitted yet.",
        "fields": {"turn_id": "str", "rule": "str (rule id)",
                   "source": "str (the SOURCE role id — the injection edge origin; the 06 §F field)",
                   "role": "str (alias of `source`, kept for back-compat)",
                   "into": "int (the reply part the value enters — the final part)",
                   "chars": "int (size of the injected value)",
                   "address": "str — run://<turn>/<source> (the injection SOURCE instance locus)"},
    },
    "cognition.part": {
        "desc": "a staged reply part was emitted (the river fills). part=1 is the instant base part; "
                "part=2 is the final enriched part. final=True on the last part.",
        "fields": {"turn_id": "str", "part": "int", "final": "bool", "staged": "bool",
                   "address": "str — ui://cognition/<turn>"},
    },
    "cognition.turn.done": {
        "desc": "the staged turn completed — the view closes the turn frame + shows the total.",
        "fields": {"turn_id": "str", "total_ms": "int", "n_parts": "int", "n_roles": "int",
                   "address": "str — ui://cognition/<turn>"},
    },
}


def _serialize_role(rid: str, role: Any) -> dict:
    """Serialize ONE file-discovered role to the FE's draw-truth (the cognition-node card). Generated
    from the role's declared spec — never hand-written. Fail loud if the registry KEY disagrees with
    the role's own id (rule 3 — one source; mirrors object_info.py:79-83).

    `role` is a runtime.roles.Role (carries `.id`, `.spec`, facet predicates). The fields are exactly
    what 06 §C's role render-rule needs: label/description (card title + sub-line), the facet
    (can_fire/is_jury/draws/mode_scope — the dot + which cast), `requires` (the capability query), and
    the role's declared `render_hint` / `rules` (the chains + injection edges G7 draws)."""
    real_id = getattr(role, "id", None)
    if real_id is not None and real_id != rid:
        raise ValueError(
            f"/cognition_info: registry key {rid!r} disagrees with role.id {real_id!r} — "
            f"one source (rule 3) violated; never ship a silently-wrong cognition projection.")
    spec = getattr(role, "spec", {}) or {}
    return {
        "id": rid,
        "label": spec.get("label"),
        "description": spec.get("description"),
        "can_fire": bool(getattr(role, "can_fire", False)),
        "is_jury": bool(getattr(role, "is_jury", False)),
        "draws": int(getattr(role, "draws", 1)),
        "mode_scope": sorted(getattr(role, "mode_scope", ()) or ()),
        "requires": list(getattr(role, "requires", []) or []),
        # C-build facets (the engine generalization — so the surface/registry/gates SEE them):
        # `op` (generate|embed — the operation axis, C 1/4) and `input_addresses` (what the role reads,
        # resolved from the address system: a skill/context/upstream output, C 3/4+3b). Projected so a
        # role's full declared shape is one-source-visible — never re-derived or hardcoded FE-side.
        "op": spec.get("op", "generate"),
        "input_addresses": list(spec.get("input_addresses") or ()),
        "trigger": spec.get("trigger"),
        "render_hint": spec.get("render_hint"),
        # #58 FULL-SCHEMA projection — the per-request CONFIG fields the agent can set on a role
        # (create_role exposes the full ROLE_FIELDS). Projected verbatim from the declared spec so a
        # role's full declared shape is one-source-visible on the surface — never re-derived FE-side.
        # Present-only (a role that doesn't declare them omits the key, like render_hint).
        **({"thinking": spec["thinking"]} if "thinking" in spec else {}),
        **({"tools": spec["tools"]} if "tools" in spec else {}),
        **({"knobs": spec["knobs"]} if "knobs" in spec else {}),
        **({"context": spec["context"]} if "context" in spec else {}),
        **({"model_binding": spec["model_binding"]} if "model_binding" in spec else {}),
        # the role's declared routing rules AS DATA (06 §C — the chain/injection edges the view draws).
        # Verbatim declared dicts (descriptive OR AST-shaped); the FE reads `when`/`destination` to draw.
        "rules": list(spec.get("rules") or []),
    }


def _serialize_rule(rid: str, rule: Any) -> dict:
    """Serialize ONE declared G3 Rule to its addressable/renderable record (rules.py:as_record). Fail
    loud if the key disagrees with the rule's own id (defense-in-depth, mirrors the role check)."""
    real_id = getattr(rule, "id", None)
    if real_id is not None and real_id != rid:
        raise ValueError(
            f"/cognition_info: rule key {rid!r} disagrees with rule.id {real_id!r} — "
            f"one source (rule 3) violated.")
    # Rule.as_record() is the pure serialization the view (G7) draws (when/when_text/destination/inputs).
    if hasattr(rule, "as_record"):
        return rule.as_record()
    return {"id": rid, **(rule if isinstance(rule, dict) else {})}


def build_cognition_info(
    *,
    roles: dict[str, Any],
    rules: dict[str, Any] | None = None,
    edge_kinds: dict[str, str] | None = None,
    thought_shapes: dict[str, dict] | None = None,
    activation_contexts: dict[str, dict] | None = None,
    rule_ops: dict[str, str] | None = None,
    destination_kinds: dict[str, str] | None = None,
    casts: dict[str, list] | None = None,
    node_states: list[dict] | None = None,
    projections: Any | None = None,
    lifters: Any | None = None,
    mark_types: Any | None = None,
    generation_policies: Any | None = None,
    relation_types: Any | None = None,
    ai_tics: Any | None = None,
    forms: Any | None = None,
) -> dict:
    """Serialize the cognition registries for the frontend — the SIBLING of build_object_info.

    Returns a plain JSON-serializable dict the live cognition view (06 §D) renders from:
      {
        "schema_ver": int,
        "roles":        {"<id>": {label, description, can_fire, is_jury, draws, mode_scope, ...}},
        "rules":        {"<id>": {id, label, when, when_text, destination, inputs, ...}},
        "edge_kinds":   {"<kind>": "<gloss>"},          # the C1.3 edge vocabulary (chain/inject labels)
        "thought_shapes": {"<archetype>": {...}},        # the ~5 reply shapes
        "activation_contexts": {"<ctx>": {...}},         # when a cast fires (the dial generalised)
        "rule_ops":     {"<op>": "<gloss>"},             # the closed rule grammar (badge legend)
        "destination_kinds": {"<dest>": "<gloss>"},      # the 5 routing destinations (the floor)
        "casts":        {"<mode>": ["<role id>", ...]},  # the cast per presence mode
        "node_states":  [...],                           # cognition status vocabulary (the dot legend)
        "event_kinds":  {"<kind>": {desc, fields}},      # THE EMIT-CONTRACT the FE binds to (06 §F#3)
        # --- the corpus pillar's file-discovered registries (Cognition Engine K1/P1 + NEWMOD) ---
        # Each projected via its registry's own as_records() (registry-is-truth — the discovered set,
        # never a hand-listed one). The FE/agent SEE the lens/lifter/mark-type/policy/relation/tic/form
        # vocabularies in the SAME live view as roles/rules; drop a file → restart → it appears here.
        "projections":  [...],                           # the lens set (K1) — the capture/space vocabulary
        "spaces":       ["<projection id>", ...],         # the embeddable lens subset (the Group-L vec spaces)
        "lifters":      [...],                           # code EXTRACTORS (frontmatter/links/blocks) — `extract` is a qualname
        "mark_types":   [...],                           # the mark VOCABULARY (the mark-pass draws a registered type)
        "generation_policies": [...],                     # the rep_penalty ladders / decode regimes (O2)
        "relation_types": [...],                          # the near/far relation vocabulary (find_relations)
        "ai_tics":      [...],                           # the generic-AI fingerprint markers (the inversion subtract-set)
        "forms":        [...],                           # the form→stage/policy routing (effort-by-form) — `match` is a qualname
      }

    GENERATED FROM the registries (rule 3, one source): UI, runtime, and tools all project from the
    SAME registries. Fail loud (rule 4): a key that disagrees with its thing's own id raises; a
    THOUGHT_SHAPES row whose value isn't a dict carrying `archetype`, an ACTIVATION_CONTEXTS row whose
    value isn't a dict — raise rather than emit a silently-malformed projection.

    `roles` is the file-discovered RoleRegistry (dict-like {id: Role}). `rules` is the declared-rule
    map {id: Rule}. The remaining vocab args are the net-new cognition registries (EDGE_KINDS,
    THOUGHT_SHAPES, ACTIVATION_CONTEXTS, RULE_OPS, DESTINATION_KINDS). `projections`/`lifters`/
    `mark_types`/`generation_policies`/`relation_types`/`ai_tics`/`forms` are the corpus pillar's
    file-discovered registries — each an object exposing `as_records()` (and `projections` also
    `embeddable()` for `spaces`); each OPTIONAL (None => absent => `[]`, schema-additive so the existing
    caller that passes none still gets a valid shape). ALL passed IN — this module imports nothing from
    the runtime (the spine imports nothing above it)."""
    out_roles: dict = {}
    for rid in sorted(roles):
        out_roles[rid] = _serialize_role(rid, roles[rid])

    out_rules: dict = {}
    for rid in sorted(rules or {}):
        out_rules[rid] = _serialize_rule(rid, (rules or {})[rid])

    # THOUGHT_SHAPES: fail loud on a malformed row (the value must be a dict carrying `archetype`).
    out_shapes: dict = {}
    for sid, sval in (thought_shapes or {}).items():
        if not isinstance(sval, dict) or "archetype" not in sval:
            raise ValueError(
                f"/cognition_info: thought_shape {sid!r} value is not a dict carrying 'archetype' "
                f"({sval!r}) — fail loud (never a silently-malformed shape).")
        if sval.get("archetype") != sid:
            raise ValueError(
                f"/cognition_info: thought_shape key {sid!r} disagrees with archetype "
                f"{sval.get('archetype')!r} — one source (rule 3) violated.")
        out_shapes[sid] = dict(sval)

    # ACTIVATION_CONTEXTS: fail loud on a malformed row (the value must be a dict).
    out_acts: dict = {}
    for cid, cval in (activation_contexts or {}).items():
        if not isinstance(cval, dict):
            raise ValueError(
                f"/cognition_info: activation_context {cid!r} value is not a dict ({cval!r}) — "
                f"fail loud.")
        out_acts[cid] = dict(cval)

    return {
        "schema_ver": SCHEMA_VER,
        "roles": out_roles,
        "rules": out_rules,
        "edge_kinds": dict(edge_kinds or {}),
        "thought_shapes": out_shapes,
        "activation_contexts": out_acts,
        "rule_ops": dict(rule_ops or {}),
        "destination_kinds": dict(destination_kinds or {}),
        "casts": {m: list(c) for m, c in (casts or {}).items()},
        "node_states": [dict(s) for s in (node_states or [])],
        "event_kinds": {k: {"desc": v["desc"], "fields": dict(v["fields"])}
                        for k, v in COGNITION_EVENT_KINDS.items()},
        # The corpus pillar's file-discovered registries (rule 3, ONE source: each is its OWN
        # registry's as_records() — the discovered set verbatim, never a hand-listed literal). Passed IN
        # (this module imports nothing from runtime — the spine that imports nothing above it); None =>
        # absent => [] (schema-additive: an older caller that doesn't pass them still gets a valid shape).
        # projections/spaces ride the SAME kwarg home as the 6 new registries (the uniform serialization
        # home the SUITE lane flagged) — projections via as_records(), spaces via the embeddable() subset.
        "projections": projections.as_records() if projections is not None else [],
        "spaces": [p.id for p in projections.embeddable()] if projections is not None else [],
        "lifters": lifters.as_records() if lifters is not None else [],
        "mark_types": mark_types.as_records() if mark_types is not None else [],
        "generation_policies": generation_policies.as_records() if generation_policies is not None else [],
        "relation_types": relation_types.as_records() if relation_types is not None else [],
        "ai_tics": ai_tics.as_records() if ai_tics is not None else [],
        "forms": forms.as_records() if forms is not None else [],
    }
