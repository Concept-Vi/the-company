"""runtime/roles.py — the file-discovered ROLE registry (Concurrent Cognition G2 · C2.1).

A ROLE is a named model-FUNCTION of the collective cognition: a specific job done by a model
that is NOT (necessarily) the conversational brain. Roles were two HARDCODED things before G2:
  - `suite.py`'s one-entry `ROLE_REGISTRY` dict (the `judge`, config-consumed via dict access), and
  - `cognition.py`'s `SPIKE_ROLES` dict (focus/recall/ground, the fire-able spike roles).
G2 PROMOTES both into ONE file-discovered registry — exactly mirroring how node-types self-register
(`runtime/registry.py` `NodeRegistry.discover`): a `roles/` dir, one self-registering file per role.
Adding a role = adding a file; it self-registers + is queryable. A removed file un-registers on
rediscover. (Same property the node library has — the self-extending path, AGENTS.md.)

## The role schema (C2.1) — the SUPERSET of both old notions
Each `roles/<name>.py` declares a module-level `ROLE` dict. The schema is intentionally a SUPERSET so
the judge's rich config dict AND a fire-able cast role's {prompt,output} both fit ONE shape; every
field except `id` is OPTIONAL, and a role's FACET follows which fields are populated:
  - `id`              — the role id (required; must equal the module name, fail-loud otherwise).
  - `label` / `description` — operator-facing (the config lab renders these).
  - `prompt_template` — a system prompt. Present ⇒ the role can FIRE (run_role/run_swarm).
  - `output_schema`   — a Pydantic BaseModel subclass the role's JSON validates against (C1.4).
  - `input_addresses` — the declared inputs the role reads (e.g. ("utterance",) or run:// refs).
  - `trigger`         — descriptive today (the consuming code's actual trigger); a general
                        event→role trigger engine is downstream (G3/activation-contexts).
  - `model_binding`   — {requires:[...], default_model, default_base_url, recommended_*, env_*}.
                        `requires` is the C2.5 capability QUERY shape (role.requires ⊆ model.provides),
                        NOT hand-written suitability prose. resolved against the live provider set.
  - `mode_scope`      — the modes this role is part of the CAST for (e.g. {"listening"}). ABSENT ⇒
                        the role is in NO cast (e.g. the judge: config-only, fired by the voice circuit).
  - `rules`           — the declared routing/verdict rules over this role's resolved output (DATA here;
                        the rich rule ENGINE is G3 — declared, never executed in this module).
  - `render_hint`     — how G7 renders this role's firing (DATA; the live view is G7).
  - `draws`           — N: a JURY role runs N VARIED draws → a deterministic verdict (C2.4 / C1.5).
  - `verdict_rule`    — the pure deterministic verdict over the N draws (quorum/vote) — see roles below.
  - `knobs`           — per-request knobs (max_tokens/temperature/…) the binding/firing reads.
  - `thinking`/`output`/`tools`/`context` — the judge's existing config fields (preserved verbatim).

The judge declares NONE of {prompt_template, mode_scope, draws} → correctly config-only, in no cast,
not a jury. It is NOT forced to fake a prompt. Its dict is served BYTE-IDENTICAL (C2.2): `suite.py`'s
`resolve_role` reads the SAME dict it read before, only from this registry instead of a class constant.

## Drift home (C9.4 / R2-FOLD H5)
This registry's self-description home is `roles/AGENTS.md` (its constitution) + the per-role files
themselves. `tests/roles_acceptance.py` asserts every discovered role is reflected in `roles/AGENTS.md`
(mirrors how `tests/edge_kinds_acceptance.py` guards `EDGE_KINDS` against `contracts/AGENTS.md`). A new
acceptance suite reflects into STATE.md's SUITES block via `Suite.refresh_self_description()`.

LAWS honoured: L1 registry-driven (roles are FILE-DISCOVERED DATA, never a hardcoded dict) · L2 a model
runs only INSIDE a role, routing/verdict rules are pure declared functions (no eval, no model-call) ·
reuse-don't-parallel (ONE registry pattern — mirrors NodeRegistry exactly; not a fork) · fail loud
(a malformed role file RAISES at discovery; a non-role/`_`-file is skipped) · schema-additive.
"""
from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel


# The schema field names a role MAY declare (the C2.1 superset). `id` is required; the rest optional.
# The first row = the G2 role-schema facets. The second row = the judge's LEGACY top-level binding fields
# that `suite.py:resolve_role`/`roles()` read DIRECTLY (preserved verbatim so the judge is byte-identical,
# C2.2) — `model_binding` is the G2 nested capability-query shape, these are the flat fields resolve_role
# consumes today. Both are valid role-schema fields (consumed by a real consumer — never a silent typo).
ROLE_FIELDS = (
    "id", "label", "description", "prompt_template", "output_schema", "input_addresses",
    "trigger", "model_binding", "mode_scope", "rules", "render_hint", "draws", "verdict_rule",
    "knobs", "thinking", "output", "tools", "context",
    # legacy flat binding fields (resolve_role/roles() consume these directly — judge byte-identical):
    "default_model", "default_base_url", "recommended_model", "recommended_base_url",
    "recommended_reason", "env_model", "env_url", "env_knobs",
)


@dataclass
class Role:
    """A discovered role — the superset schema (C2.1). Carries the declared dict (`spec`) verbatim so
    a dict-consumer (suite.py's resolve_role/roles()) reads it UNCHANGED, plus typed accessors the
    cognition driver uses to FIRE it. Every field except `id` is optional; a role's facet follows which
    fields are populated (fires ⟺ prompt_template; in-a-cast ⟺ mode_scope; jury ⟺ draws)."""
    id: str
    spec: dict                                   # the declared dict, verbatim (the dict-view consumers read)
    prompt_template: str | None = None
    output_schema: type[BaseModel] | None = None
    mode_scope: frozenset = field(default_factory=frozenset)
    draws: int = 1

    # --- facet predicates (a role's capabilities follow its populated fields) ---
    @property
    def can_fire(self) -> bool:
        """A role can be FIRED (run_role/run_swarm) iff it declares a prompt_template + output_schema."""
        return bool(self.prompt_template) and self.output_schema is not None

    @property
    def is_jury(self) -> bool:
        """A role is a JURY iff it declares draws > 1 (C2.4 — N varied draws + a verdict)."""
        return self.draws > 1

    def in_mode(self, mode: str) -> bool:
        """Is this role part of the CAST for `mode`? (C2.3 — mode-scoped. No mode_scope ⇒ in no cast.)"""
        return mode in self.mode_scope

    @property
    def verdict_rule(self):
        """The declared pure verdict rule (a callable over the N draws) — None for a non-jury."""
        return self.spec.get("verdict_rule")

    @property
    def model_binding(self) -> dict:
        return dict(self.spec.get("model_binding") or {})

    @property
    def requires(self) -> list:
        """The C2.5 capability QUERY — the capabilities a model must `provide` to bind this role.
        A QUERY (role.requires ⊆ model.provides), never hand-written suitability prose."""
        return list(self.model_binding.get("requires") or [])


def _load_module(path: str):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(f"_role_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return name, mod


def _build_role(name: str, decl: dict) -> Role:
    """Validate + build a Role from a module's declared `ROLE` dict. FAIL LOUD on a malformed role
    (mirrors NodeRegistry._read_output_schema's TypeError-on-declared-but-malformed): a declared role
    with a bad shape RAISES — it is NOT silently skipped (a non-role file is the one that skips)."""
    if not isinstance(decl, dict):
        raise TypeError(
            f"role module {name!r}: ROLE must be a dict (the declared role schema), got "
            f"{type(decl).__name__} — fail loud, never a silent malformed role.")
    rid = decl.get("id")
    if not rid or not isinstance(rid, str):
        raise ValueError(
            f"role module {name!r}: ROLE declares no string `id` — every role declares its id "
            f"(fail loud; rule 8 — author from the registry, never an unnamed role).")
    if rid != name:
        raise ValueError(
            f"role module {name!r}: ROLE id {rid!r} != module name {name!r} — the id must equal the "
            f"file name (so a role is addressable by file, mirroring node-types). Fail loud.")
    unknown = [k for k in decl if k not in ROLE_FIELDS]
    if unknown:
        raise ValueError(
            f"role {rid!r}: unknown role-schema field(s) {unknown} — the C2.1 role schema is "
            f"{list(ROLE_FIELDS)}. Fail loud (never a silent typo'd field that no consumer reads).")
    osch = decl.get("output_schema")
    if osch is not None and not (isinstance(osch, type) and issubclass(osch, BaseModel)):
        raise TypeError(
            f"role {rid!r}: output_schema must be a Pydantic BaseModel subclass (validated/retried "
            f"by complete()), got {osch!r} — fail loud (never a silent un-validated role output).")
    draws = decl.get("draws", 1)
    if not isinstance(draws, int) or draws < 1:
        raise ValueError(f"role {rid!r}: draws must be an int >= 1, got {draws!r} — fail loud.")
    # G3 commit gate (C3.1/C3.4): STATICALLY WHITELIST-WALK every AST-shaped declared rule at role
    # DISCOVERY — so a malformed/out-of-grammar/over-nested rule dropped in a roles/*.py file FAILS
    # LOUD here, riding the normal change path (no special gate). The existing descriptive rule shape
    # ({id,reads,effect,kind}) is NOT an AST rule (is_ast_rule) → passed through unchanged
    # (schema-additive; the G2 role files load untouched). Imported lazily to avoid any import-order
    # coupling (rules.py is stdlib + this module only — no cycle).
    from runtime.rules import validate_role_rules
    validate_role_rules(rid, decl.get("rules"))
    vrule = decl.get("verdict_rule")
    if draws > 1 and not callable(vrule):
        raise ValueError(
            f"role {rid!r}: a jury (draws={draws}) MUST declare a callable verdict_rule (a PURE "
            f"deterministic function over the draws — quorum/vote; L2, never a model call). Fail loud.")
    ms = decl.get("mode_scope") or ()
    return Role(
        id=rid, spec=dict(decl), prompt_template=decl.get("prompt_template"),
        output_schema=osch, mode_scope=frozenset(ms), draws=int(draws),
    )


class RoleRegistry:
    """The file-discovered role registry — mirrors `runtime/registry.py:NodeRegistry` EXACTLY (the ONE
    registry pattern; not a fork). Dict-like (`reg[id] -> Role`, `id in reg`, `.get(id)`) so it drops
    in wherever the old `ROLE_REGISTRY` dict went. Adding a role = dropping a `roles/<id>.py` file."""

    def __init__(self):
        self.roles: dict[str, Role] = {}

    def discover(self, dirs: list[str]) -> "RoleRegistry":
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                name, mod = _load_module(os.path.join(d, fn))
                decl = getattr(mod, "ROLE", None)
                if decl is None:                  # not a role module (mirrors NodeRegistry's `run` check)
                    continue
                self.register(name, decl)
        return self

    def rediscover(self, dirs: list[str]) -> "RoleRegistry":
        """Rebuild from the filesystem (clear + discover) — so a REMOVED role file actually
        un-registers (discover() only adds). Mirrors NodeRegistry.rediscover."""
        self.roles.clear()
        return self.discover(dirs)

    def register(self, name: str, decl: dict) -> None:
        self.roles[name] = _build_role(name, decl)

    # --- queryable (C2.1: roles are queryable) ---
    def cast_for_mode(self, mode: str) -> list[Role]:
        """The CAST for a mode (C2.3): every role whose mode_scope includes `mode`. An UNKNOWN mode (no
        role scopes to it) yields an EMPTY cast — never a crash, never a default-fire (adversarial C2.3).
        Deterministic order (sorted by id) so a wave's ready-set is stable."""
        return [self.roles[rid] for rid in sorted(self.roles) if self.roles[rid].in_mode(mode)]

    def fireable(self) -> list[Role]:
        return [self.roles[rid] for rid in sorted(self.roles) if self.roles[rid].can_fire]

    def juries(self) -> list[Role]:
        return [self.roles[rid] for rid in sorted(self.roles) if self.roles[rid].is_jury]

    def spec(self, role_id: str) -> dict:
        """The role's declared dict, verbatim — the dict-view a dict-consumer (suite.py) reads, so the
        judge's config dict is served BYTE-IDENTICAL (C2.2). Fail loud on an unknown role."""
        if role_id not in self.roles:
            raise ValueError(f"unknown role {role_id!r} — registered roles: {sorted(self.roles)}")
        return self.roles[role_id].spec

    # --- dict-like (so it IS the ROLE_REGISTRY mapping for suite.py) ---
    def __getitem__(self, role_id: str) -> Role:
        return self.roles[role_id]

    def __contains__(self, role_id: str) -> bool:
        return role_id in self.roles

    def __iter__(self):
        return iter(self.roles)

    def get(self, role_id: str, default=None):
        return self.roles.get(role_id, default)


# --- the C2.5 capability QUERY: role.requires ⊆ model.provides (NOT hand-written prose) ----------
def model_satisfies(requires: list, provides: list | set) -> bool:
    """The suitability QUERY (C2.5): a model is suitable for a role iff role.requires ⊆ model.provides.
    A QUERY over declared capability SETS — never hand-written suitability prose. An empty `requires`
    is satisfied by ANY provider (the role declared no demands)."""
    return set(requires).issubset(set(provides or ()))


def resolve_binding(role: "Role", providers: dict) -> dict:
    """C2.5 — resolve a role's model BINDING via the capability query against the available providers.

    `providers` = {provider_id: {"model":..., "base_url":..., "provides":[caps...]}}, the thin seam G8
    will POPULATE from the capability registry. TODAY the Company's only live provider is the resident
    model read from ops/services.json (the caller builds the `providers` dict — see suite.py
    `capability_providers`). The SHAPE is the query (role.requires ⊆ provider.provides), NOT hardcoded
    prose: a role declares `requires`, and the binding is the FIRST provider that satisfies it.

    Returns {model, base_url, provider, requires, provides, satisfied, candidates}. Fail loud: a role
    that declares `requires` no live provider satisfies RAISES (never a silent wrong/empty binding) —
    UNLESS the role declares a hard `default_model` fallback in its model_binding (the judge's safe
    floor: None default → the brain, always available).

    G8 DEPENDENCY (downstream — flagged): when G8/L-model ships the real capability catalog, the caller
    passes the FULL provider set here; this query is unchanged. v1 = resident-only provider."""
    req = role.requires
    cands = [(pid, p) for pid, p in providers.items() if model_satisfies(req, p.get("provides", []))]
    binding = role.model_binding
    if cands:
        pid, p = cands[0]
        return {"model": p["model"], "base_url": p["base_url"], "provider": pid,
                "requires": req, "provides": list(p.get("provides", [])), "satisfied": True,
                "candidates": [c[0] for c in cands]}
    # no provider satisfies the query → the role's declared hard default (the judge's None→brain floor),
    # else fail loud (never silently bind a role to a model that can't do the job).
    if "default_model" in binding:
        return {"model": binding.get("default_model"), "base_url": binding.get("default_base_url"),
                "provider": "default", "requires": req, "provides": [], "satisfied": False,
                "candidates": []}
    raise ValueError(
        f"resolve_binding: role {role.id!r} requires {req} but NO live provider provides that "
        f"(available: {[(pid, p.get('provides')) for pid, p in providers.items()]}). Fail loud — "
        f"never bind a role to a model that does not satisfy its requirements (C2.5).")
