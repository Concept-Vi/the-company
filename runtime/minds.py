"""runtime/minds.py — R13 Composable-Mind: the brain is a COMPOSITION selected from a mind-registry,
bound at the run path — NOT one swappable slot. Rides H1.1 (resolve) + H1.2 (traverse) + REUSES
RoleRegistry/cast_for_mode/run_swarm; it is NOT a new engine.

Cut: ~/.claude/plans/declarative-inventing-codd.md (clone-cacc9e8b, lead-anchored). Substrate = mind://·
cap:// ONLY (clone:// is a SEPARATE axis — never composed over). DISJOINT NEW files (zero hot-file edit);
the lead owns the two tiny HOT seams (resolve_address mind:// branch + cast_for_mode additive bind),
which meet this module at the four locked signatures.

A `minds/<id>.py` declares a module-level `MIND` dict:
  kind="role"        → {id, kind, role: "<roles/ id>"}            — binds an existing role (the thinking unit)
  kind="model"       → {id, kind, cap:  "cap://<...>"}            — binds a provider (reuse capability_providers)
  kind="composition" → {id, kind, members:[<mind-id>...],         — an ordered composition (the N+1 pattern)
                        order:[{from,to,kind}]}                     (typed order-edges, e.g. extractor→judge feeds)
  kind="binding"     → {id, kind, mode: "<mode>", mind: "<id>"}   — mode→composition bind as registry DATA
                                                                     (a ROW edit rebinds a mode — never code)

THE FOUR LOCKED SIGNATURES (the lead wires seams A+B against exactly these; meet at green):
  mind_registry() -> MindRegistry
  .resolve(id) -> mind row ; RAISES on unknown (fail-loud, bar 6)
  traverse(composition_row, store) -> ordered role-shaped minds (the EXACT cast_for_mode shape — Role
        objects with .id/.can_fire/.is_jury), each member resolved THROUGH cognition.resolve_address (bar 2)
  binding_for_mode(mode) -> mind-id | None  (from a minds/ binding row)

LAWS: no-hardcoding · reuse-don't-parallel (mirrors RoleRegistry; run_swarm byte-identical) · fail loud ·
flat address (composition structure is ROW data, not address-structure — no parse_mind_address this unit).
"""
from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass, field

MINDS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "minds")
MIND_FIELDS = ("id", "kind", "role", "cap", "members", "order", "mode", "mind", "source_as", "desc")
MIND_KINDS = ("role", "model", "composition", "binding")


class MindError(RuntimeError):
    """A mind op could not run — raised TEACHING-loud (never a silent no-op). Mirrors RoleRegistry/CloneError."""


@dataclass
class Mind:
    id: str
    spec: dict

    @property
    def kind(self) -> str:
        return self.spec.get("kind")

    @property
    def members(self) -> list:
        return list(self.spec.get("members") or [])

    @property
    def order(self) -> list:
        return list(self.spec.get("order") or [])

    def __getitem__(self, k):           # row-like access (the lead's seam reads rows)
        return self.spec.get(k)

    def get(self, k, default=None):
        return self.spec.get(k, default)


def _load_module(path: str):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(f"_mind_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return name, mod


def _build_mind(name: str, decl: dict) -> Mind:
    """Validate + build a Mind. FAIL LOUD on a malformed entry (id==module name; valid kind; kind's required fields)."""
    if not isinstance(decl, dict):
        raise MindError(f"mind module {name!r}: MIND must be a dict, got {type(decl).__name__} — fail loud.")
    rid = decl.get("id")
    if not rid or not isinstance(rid, str):
        raise MindError(f"mind module {name!r}: declares no string `id` — fail loud (never unnamed).")
    if rid != name:
        raise MindError(f"mind module {name!r}: id {rid!r} != module name {name!r} — id must equal the file name.")
    kind = decl.get("kind")
    if kind not in MIND_KINDS:
        raise MindError(f"mind {rid!r}: kind {kind!r} not in {list(MIND_KINDS)} — fail loud.")
    unknown = [k for k in decl if k not in MIND_FIELDS]
    if unknown:
        raise MindError(f"mind {rid!r}: unknown field(s) {unknown} — schema is {list(MIND_FIELDS)}. Fail loud.")
    if kind == "role" and not decl.get("role"):
        raise MindError(f"mind {rid!r} kind=role needs `role` (a roles/ id). Fail loud.")
    if kind == "model" and not decl.get("cap"):
        raise MindError(f"mind {rid!r} kind=model needs `cap` (cap://<...>). Fail loud.")
    if kind == "composition" and not decl.get("members"):
        raise MindError(f"mind {rid!r} kind=composition needs `members` (≥1 mind-id). Fail loud.")
    if kind == "binding" and not (decl.get("mode") and decl.get("mind")):
        raise MindError(f"mind {rid!r} kind=binding needs `mode` + `mind`. Fail loud.")
    return Mind(id=rid, spec=dict(decl))


class MindRegistry:
    """File-discovered MIND registry — mirrors RoleRegistry.discover VERBATIM (os.listdir→importlib→getattr
    MIND). Dict-like. Adding a mind / recomposing = dropping or editing a `minds/<id>.py` row (no code)."""

    def __init__(self):
        self.minds: dict[str, Mind] = {}

    def discover(self, dirs: list[str]) -> "MindRegistry":
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                name, mod = _load_module(os.path.join(d, fn))
                decl = getattr(mod, "MIND", None)
                if decl is None:
                    continue
                self.register(name, decl)
        return self

    def rediscover(self, dirs: list[str]) -> "MindRegistry":
        self.minds.clear()
        return self.discover(dirs)

    def register(self, name: str, decl: dict) -> None:
        self.minds[name] = _build_mind(name, decl)

    def resolve(self, mind_id: str) -> Mind:
        """The mind row for `mind_id`. RAISES on unknown (fail-loud, bar 6 — the blob/vec guard; what the
        lead's resolve_address `mind://` branch calls)."""
        mid = mind_id[len("mind://"):] if mind_id.startswith("mind://") else mind_id
        if mid not in self.minds:
            raise MindError(
                f"unknown mind {mid!r} — valid minds: {sorted(self.minds)}. "
                f"(mind is a registry ref; add a minds/<id>.py to extend. Fail loud, never fabricate.)")
        return self.minds[mid]

    def __contains__(self, mid: str) -> bool:
        return (mid[len("mind://"):] if mid.startswith("mind://") else mid) in self.minds

    def __iter__(self):
        return iter(self.minds)

    def __len__(self) -> int:
        return len(self.minds)

    def get(self, mid: str, default=None):
        try:
            return self.resolve(mid)
        except MindError:
            return default


# ── lazy singleton (mirrors cc_board._items_reg / role_registry) ──
_MINDS: MindRegistry | None = None


def mind_registry() -> MindRegistry:
    global _MINDS
    if _MINDS is None:
        _MINDS = MindRegistry().discover([MINDS_DIR])
    return _MINDS


def reset_registry() -> None:
    """Drop the cache so the NEXT access re-reads minds/ (proves recompose = a row edit goes live, no code)."""
    global _MINDS
    _MINDS = None
    mind_registry()


def _ordered_members(comp: Mind) -> list[str]:
    """The composition's members in run order. Order-edges {from,to} impose a topological order
    (extractor→judge ⇒ extractor first); members with no edge keep their list position. Deterministic."""
    members = list(comp.members)
    edges = [(e.get("from"), e.get("to")) for e in comp.order if isinstance(e, dict)]
    if not edges:
        return members
    # simple stable topological sort over the members using the from→to edges
    after: dict[str, set] = {m: set() for m in members}
    for frm, to in edges:
        if to in after and frm in after:
            after[to].add(frm)            # `to` must come AFTER `frm`
    ordered, placed = [], set()
    # repeatedly take members whose prerequisites are all placed, in list order (stable)
    remaining = list(members)
    guard = 0
    while remaining and guard <= len(members):
        progressed = False
        for m in list(remaining):
            if after[m] <= placed:
                ordered.append(m); placed.add(m); remaining.remove(m); progressed = True
        guard += 1
        if not progressed:
            ordered.extend(remaining)     # a cycle/ambiguity → fall back to list order (never drop a member)
            break
    return ordered


def traverse(composition_row, store) -> list:
    """Compose-as-traversal (bar 2): resolve each member of a composition THROUGH cognition.resolve_address
    (rides H1.1/H1.2 — the ONE resolver, not a private path) and return the ordered ROLE-SHAPED minds — the
    EXACT shape cast_for_mode returns (Role objects exposing .id/.can_fire/.is_jury), resolved minds NOT
    strings. A `role` mind de-references to its roles/ Role; a `model` mind to its capability binding.
    `composition_row` may be a Mind (kind=composition) or a mind-id/mind:// addressing one."""
    from runtime.cognition import resolve_address, role_registry      # lazy (avoid import cycle; the ONE resolver)
    comp = composition_row
    if isinstance(comp, str):
        comp = resolve_address(store, comp if comp.startswith("mind://") else "mind://" + comp)
    if getattr(comp, "kind", None) != "composition":
        raise MindError(f"traverse needs a composition mind (kind=composition), got {getattr(comp,'kind',comp)!r}. Fail loud.")
    roles = role_registry()
    out = []
    for member_id in _ordered_members(comp):
        member = resolve_address(store, "mind://" + member_id)        # THROUGH the one resolver (bar 2)
        mkind = getattr(member, "kind", None) or (member.get("kind") if hasattr(member, "get") else None)
        if mkind == "role":
            role_id = member["role"]
            role_obj = roles.get(role_id)
            if role_obj is None:
                raise MindError(f"mind {member_id!r} binds role {role_id!r} which is not in the role registry. Fail loud.")
            out.append(role_obj)                                      # the cast_for_mode shape (Role: .id/.can_fire/.is_jury)
        elif mkind == "composition":
            out.extend(traverse(member, store))                       # nested composition flattens in order
        else:
            out.append(member)                                        # model/other mind — its resolved row (model-leg)
    return out


def run_composition(composition_row, ctx: dict, store, *, turn_id: str, budget=None) -> dict:
    """EXECUTE a composition by WALKING its feeds order-edges (R13 bar 3 — output flows through BOTH minds).
    A thin DAG-walker that REUSES the existing primitives — run_swarm (a leg with no incoming feeds, fired on
    the source ctx) + run_items (a downstream leg, fired on a unit built from its feeders) — so run_swarm
    stays BYTE-IDENTICAL (bar 5); this module owns only the order-edge SEMANTICS.

    The feeds-edge schema (declared DATA, recompose-by-row): an order edge {from,to,kind:"feeds",as:"<key>"}
    places the upstream's output under <key> in the downstream's unit; the composition's optional
    `source_as:"<key>"` carries the ORIGINAL source under that key. (e.g. pair → judge unit
    {"extract": <ex_out>, "raw_exchange": <source>} — the proven feed.)

    Returns {"order":[mind-id...], "addresses":{mind-id: run://...}, "outputs":{mind-id: resolved-out},
    "final": <last leg's output>}. The run:// trail is what R15 gate/rewind addresses a composition-step on.
    Fail-loud: a member that isn't a role-mind, or a feeder whose output is missing, RAISES."""
    from runtime.cognition import run_swarm, run_items, resolve_address, role_registry
    comp = composition_row
    if isinstance(comp, str):
        comp = resolve_address(store, comp if comp.startswith("mind://") else "mind://" + comp)
    if getattr(comp, "kind", None) != "composition":
        raise MindError(f"run_composition needs a composition mind, got {getattr(comp,'kind',comp)!r}. Fail loud.")
    roles = role_registry()
    order = comp.order
    source = ctx.get("utterance")
    source_as = comp.get("source_as")
    members = _ordered_members(comp)
    addresses, outputs = {}, {}
    for member_id in members:
        mind = resolve_address(store, "mind://" + member_id)
        mkind = getattr(mind, "kind", None) or (mind.get("kind") if hasattr(mind, "get") else None)
        if mkind != "role":
            raise MindError(f"run_composition: member {member_id!r} kind={mkind!r} — only role-minds are runnable legs this unit. Fail loud.")
        role = roles.get(mind["role"])
        if role is None:
            raise MindError(f"run_composition: mind {member_id!r} binds role {mind['role']!r} not in the registry. Fail loud.")
        incoming = [e for e in order if e.get("to") == member_id and e.get("kind") == "feeds"]
        if not incoming:
            # SOURCE leg — fire on the original ctx (run_swarm, the flat primitive, one role)
            wave = run_swarm([role], {"utterance": source}, store, turn_id=turn_id, budget=budget)
            addresses[member_id] = wave.addresses[role.id]
            outputs[member_id] = wave.resolved[role.id]
        else:
            # DOWNSTREAM leg — build the unit from feeders' outputs (by `as`) + the original source (source_as)
            unit = {}
            for e in incoming:
                frm = e.get("from")
                if frm not in outputs:
                    raise MindError(f"run_composition: feeds edge {frm}->{member_id} but {frm} produced no output (order bug). Fail loud.")
                key = e.get("as")
                if not key:
                    raise MindError(f"run_composition: feeds edge {frm}->{member_id} lacks `as` (where to place the upstream output). Fail loud.")
                unit[key] = outputs[frm]
            if source_as:
                unit[source_as] = source
            items = run_items(role, [unit], store, turn_id=turn_id, budget=budget)
            addresses[member_id] = list(items.addresses.values())[0]
            outputs[member_id] = items.resolved[0]
    return {"order": members, "addresses": addresses, "outputs": outputs,
            "final": outputs[members[-1]] if members else None}


def binding_for_mode(mode: str):
    """The mind-id a `mode` is bound to (kind=binding row with row.mode==mode), or None. A mode→composition
    rebind is a ROW edit (add/edit a minds/<id>.py binding), never code — the recompose-by-data bar."""
    for mid in mind_registry():
        m = mind_registry().minds[mid]
        if m.kind == "binding" and m.get("mode") == mode:
            return m.get("mind")
    return None
