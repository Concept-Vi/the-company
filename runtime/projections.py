"""runtime/projections.py — the file-discovered PROJECTION registry (Cognition Engine K1 / P1).

A PROJECTION is a declared LENS over a corpus unit — one named way to DESCRIBE a file/unit
(what it IS, the topics it covers, the principles it expresses, its claimed status, …). The set
of lenses is the discovery vocabulary of the corpus pillar: a `capture` role's output_schema is
built FROM this registry (the consuming SUITE/ENGINE lanes), each embeddable lens becomes a
vector SPACE (Group L), and `find_relations(near_space, far_space)` set-operates over those
spaces (the inversion-finder). So the lens set must be DATA you can extend by dropping a file —
never a literal list in code.

## Why a FILE-DISCOVERED registry, not a python dict (the adversary-verified BAR — PART 4.3)
The real test of "registry-is-truth" (the dynamic + foundations adversaries, COMPLETION-CRITERIA
PART 4.3): **add-a-row = a FILE, no code edit.** `cognition_info` already PROJECTS code-dicts
(RULE_OPS / THOUGHT_SHAPES) — but projection ≠ dynamic; a dict still needs a source edit to grow.
A projection registry must be **directory-discovered, file-per-entry + create_*-authorable**,
EXACTLY like roles/skills/contexts. So this is NOT `PROJECTIONS = {...}` — it is `os.listdir` →
import a `projections/<id>.py` per lens, each self-registering. Dropping a `projections/<id>.py`
makes that lens appear everywhere (the capture-schema, the spaces, the selects) with ZERO code
change. The registry path IS the rule: create the file, never edit a literal.

## Why SELF-CONTAINED (not importing skills.py's base) — the precedent
This mirrors the MECHANISM of `runtime/skills.py:_BaseEntryRegistry` / `runtime/roles.py:RoleRegistry`
(both of which mirror `runtime/registry.py:NodeRegistry`) — `os.listdir` → `importlib` a directory,
fail-loud on a malformed entry, id==filename, dict-like, `rediscover` for removal. It is a STANDALONE
copy of that pattern, EXACTLY as `roles.py` is a standalone copy (roles.py does NOT import skills.py's
base either). The fork the registries are warned against (skills.py docstring) is a DIFFERENT mechanism
(a globbing/markdown registry) — NOT a second importlib registry, which IS the one sanctioned pattern.
The projection ROW SHAPE differs from skill/context (no `content` field; a lens declares level/field/
embeds/desc), so the validator is projection-specific (`_build_projection`) — mirroring the mechanism,
NOT copying skill's content-required check. *(A shared base for the eventual 7 corpus registries
[projections/lifters/mark-types/ai-tics/relation-types/generation-policies/forms] is a real reuse
question — but extracting it now, for 6 not-yet-designed schemas, would be speculative; it is a FUTURE
NEWMOD pass, surfaced not built. roles/skills already each carry their own copy — one more here is the
established precedent, not new debt.)*

## The projection schema (from ~/company/migration-pending/wizard-run-1/registries/projections.json — an earlier prototype)
Each `projections/<id>.py` declares a module-level `PROJECTION` dict — a registry ROW:
  - `id`          — required; MUST equal the module name (addressable by file, like a role/node-type —
                    fail-loud otherwise). The lens name.
  - `level`       — required; the abstraction BAND the lens reads at (structural · content · relational ·
                    meaning · epistemic · generative · texture · functional in the prototype). DATA, an
                    open string — the bands are a vocabulary, not a closed enum (a new band = a new value,
                    no code change). Lets the render group lenses by depth.
  - `produced_by` — required; "model" (a capture-role DESCRIBES it — the LLM path) | "code" (a `lifters`
                    registry EXTRACTOR produces it deterministically — frontmatter/links/blocks, a later
                    NEWMOD pass). The capture-schema builder includes only `produced_by=="model"` lenses;
                    the lifters lane owns the `code` ones.
  - `embeds`      — required bool; does this lens become a vector SPACE (Group L: per embeddable projection
                    → op=embed → put_vector(vec://<item>#space=<id>))? Only `embeds:true` lenses are spaces;
                    `find_relations(near, far)` ranges over them.
  - `field`       — optional; the OUTPUT field shape the capture-schema renders for this lens
                    ("string" · "array" · "enum"). Absent for a `code` lens (the lifter defines its own).
  - `enum`        — optional; for `field=="enum"`, the allowed values (e.g. claimed_status). Render-only.
  - `desc`        — optional; the render-NOT-judge instruction the capture prompt uses for this lens (K3:
                    a unit is DESCRIBED here — what it claims — judged LATER in a reduce; the 4B is a
                    describer, never a judge). Operator-facing too.
  - `stage`       — optional; effort-routing band ("legibility" the cheap broad pass · "deep" the heavier
                    pass) — the restored effort-routing-by-form discipline (PART 4.7): don't burn full
                    depth on every lens. DATA; the capture lane reads it to tier the work.
Every field except `id`+`level`+`produced_by`+`embeds` is OPTIONAL. A malformed entry (no string id /
id≠filename / missing required / unknown field / bad type) FAILS LOUD at discovery — never a silent skip
(a non-PROJECTION / `_`-file is the one that skips, mirroring the role/skill non-entry skip).

## Drift home (BAR 2 / SD2 — mirrors roles/AGENTS.md · skills/AGENTS.md)
`projections/AGENTS.md` is this registry's constitution (the drift home): Is / Guarantees /
Where-new-go ("add-a-row = a FILE") / To-extend / Never. `tests/projections_acceptance.py` asserts
every discovered projection is reflected in `projections/AGENTS.md` (mirrors how
`tests/roles_acceptance.py` guards roles against `roles/AGENTS.md`). A new acceptance suite reflects
into STATE.md's SUITES block via `Suite.refresh_self_description()`.

## The floor (C9.2) + render-NOT-judge (K3)
A projection is DECLARED DATA — a lens, not an action. Reading the registry is a READ (no resolve/
dispatch/approve; the registry method is `get`/dict-access, never `resolve`). The lens DESCRIBES
(`desc` is a render instruction); JUDGEMENT is a later reduce pass, never the capture lens itself.

LAWS honoured: no-hardcoding (lenses are FILE-DISCOVERED DATA, never a literal dict — the PART 4.3
file-discovery + create_*-authorable BAR) · reuse-don't-parallel (ONE registry mechanism — mirrors
RoleRegistry/SkillRegistry/NodeRegistry, not a fork) · fail loud (a malformed lens RAISES at discovery;
an unknown id RAISES on lookup — registry-is-truth, never fabricate) · render-not-judge (K3) · the floor
(reading a lens is a READ).
"""
from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass


# The schema field names a projection MAY declare. The first four are REQUIRED (a lens with no
# level/produced_by/embeds is meaningless to the capture-schema builder / the space-keying); the rest
# are optional. An unknown field FAILS LOUD (never a silent typo'd field no consumer reads).
PROJECTION_FIELDS = ("id", "level", "produced_by", "embeds", "field", "enum", "desc", "stage")
REQUIRED_FIELDS = ("id", "level", "produced_by", "embeds")

# `produced_by` is a closed two-way split (the capture-schema includes "model" lenses; the lifters
# registry owns "code" lenses). A value outside this is a typo / an unbuilt path → fail loud, not a
# silent lens that no producer ever renders. (Open vocab everywhere else; this one gates a code branch.)
PRODUCED_BY = ("model", "code")


@dataclass
class Projection:
    """A discovered lens — the declared dict (`spec`) verbatim + the typed accessors the consumers read.
    `embeds` decides whether this lens becomes a vector space (Group L); `produced_by` decides whether the
    capture-role describes it (model) or a lifter extracts it (code)."""
    id: str
    level: str
    produced_by: str
    embeds: bool
    spec: dict

    @property
    def field(self) -> str | None:
        return self.spec.get("field")

    @property
    def enum(self) -> list | None:
        return self.spec.get("enum")

    @property
    def desc(self) -> str | None:
        return self.spec.get("desc")

    @property
    def stage(self) -> str:
        return self.spec.get("stage") or "legibility"


def _load_module(path: str):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(f"_proj_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return name, mod


def _build_projection(name: str, decl: dict) -> Projection:
    """Validate + build a Projection from a module's declared dict. FAIL LOUD on a malformed entry
    (mirrors RoleRegistry._build_role / skills._build_entry's RAISE-on-declared-but-malformed): a declared
    PROJECTION with a bad shape RAISES — it is NOT silently skipped (a non-PROJECTION file is the one that
    skips). registry-is-truth: never register a fabricated/unnamed/under-declared lens."""
    if not isinstance(decl, dict):
        raise TypeError(
            f"projection module {name!r}: PROJECTION must be a dict (the declared lens schema), got "
            f"{type(decl).__name__} — fail loud, never a silent malformed projection.")
    pid = decl.get("id")
    if not pid or not isinstance(pid, str):
        raise ValueError(
            f"projection module {name!r}: PROJECTION declares no string `id` — every lens declares its id "
            f"(fail loud; author from the registry, never an unnamed lens).")
    if pid != name:
        raise ValueError(
            f"projection module {name!r}: PROJECTION id {pid!r} != module name {name!r} — the id must equal "
            f"the file name (so a lens is addressable by file, mirroring roles/skills/node-types). Fail loud.")
    unknown = [k for k in decl if k not in PROJECTION_FIELDS]
    if unknown:
        raise ValueError(
            f"projection {pid!r}: unknown projection-schema field(s) {unknown} — the K1 schema is "
            f"{list(PROJECTION_FIELDS)}. Fail loud (never a silent typo'd field that no consumer reads).")
    missing = [k for k in REQUIRED_FIELDS if k not in decl]
    if missing:
        raise ValueError(
            f"projection {pid!r}: missing required field(s) {missing} — a lens MUST declare "
            f"{list(REQUIRED_FIELDS)} (level=the abstraction band · produced_by=model|code · embeds=is-a-space). "
            f"Fail loud (an under-declared lens is meaningless to the capture-schema builder).")
    level = decl.get("level")
    if not isinstance(level, str) or not level:
        raise ValueError(
            f"projection {pid!r}: `level` must be a non-empty string (the abstraction band, e.g. "
            f"'content'/'meaning'/'epistemic'). Got {level!r} — fail loud.")
    produced_by = decl.get("produced_by")
    if produced_by not in PRODUCED_BY:
        raise ValueError(
            f"projection {pid!r}: `produced_by` must be one of {list(PRODUCED_BY)} (model=a capture-role "
            f"describes it · code=a lifter extracts it). Got {produced_by!r} — fail loud (an unknown "
            f"producer = a lens nothing ever renders).")
    embeds = decl.get("embeds")
    if not isinstance(embeds, bool):
        raise ValueError(
            f"projection {pid!r}: `embeds` must be a bool (does this lens become a vector space — Group L). "
            f"Got {embeds!r} — fail loud (a non-bool can't gate the space-keying).")
    fld = decl.get("field")
    if fld is not None and (not isinstance(fld, str) or not fld):
        raise ValueError(
            f"projection {pid!r}: `field` (when present) is the output field shape — a non-empty string "
            f"('string'/'array'/'enum'). Got {fld!r} — fail loud.")
    en = decl.get("enum")
    if en is not None and not isinstance(en, list):
        raise ValueError(
            f"projection {pid!r}: `enum` (when present) is the allowed-value list for an enum field. "
            f"Got {type(en).__name__} — fail loud.")
    return Projection(id=pid, level=level, produced_by=produced_by, embeds=embeds, spec=dict(decl))


class ProjectionRegistry:
    """The file-discovered PROJECTION registry — mirrors `runtime/roles.py:RoleRegistry` /
    `runtime/skills.py:_BaseEntryRegistry` / `runtime/registry.py:NodeRegistry` (the ONE registry
    mechanism; not a fork). Dict-like (`reg[id] -> Projection`, `id in reg`, `.get(id)`, iterate). Adding a
    lens = dropping a `projections/<id>.py` file declaring `PROJECTION = {...}`; it self-registers.

    The capture-schema builder (SUITE/ENGINE lane) reads `model_projections()`; the space-keying (Group L)
    reads `embeddable()`; cognition_info (SURFACE) reads `as_records()` to project the lens set to both
    faces. All of those are READS over this one discovered set — never a parallel literal."""

    def __init__(self):
        self.projections: dict[str, Projection] = {}

    def discover(self, dirs: list[str]) -> "ProjectionRegistry":
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                name, mod = _load_module(os.path.join(d, fn))
                decl = getattr(mod, "PROJECTION", None)
                if decl is None:               # not a projection module (mirrors NodeRegistry's `run` check)
                    continue
                self.register(name, decl)
        return self

    def rediscover(self, dirs: list[str]) -> "ProjectionRegistry":
        """Rebuild from the filesystem (clear + discover) — so a REMOVED projection file actually
        un-registers (discover() only adds). Mirrors RoleRegistry/SkillRegistry.rediscover."""
        self.projections.clear()
        return self.discover(dirs)

    def register(self, name: str, decl: dict) -> None:
        self.projections[name] = _build_projection(name, decl)

    # --- the consumer reads (all pure reads — the floor) ---
    def model_projections(self) -> list[Projection]:
        """The lenses a capture ROLE describes (`produced_by=="model"`) — the set the capture-schema's
        output_schema is built FROM (K1). Sorted by id (deterministic schema order)."""
        return [self.projections[k] for k in sorted(self.projections)
                if self.projections[k].produced_by == "model"]

    def code_projections(self) -> list[Projection]:
        """The lenses a LIFTER extracts deterministically (`produced_by=="code"`) — owned by the lifters
        registry (a later NEWMOD pass). Sorted by id."""
        return [self.projections[k] for k in sorted(self.projections)
                if self.projections[k].produced_by == "code"]

    def embeddable(self) -> list[Projection]:
        """The lenses that become vector SPACES (`embeds==True`) — Group L's space set
        (vec://<item>#space=<id>). Sorted by id."""
        return [self.projections[k] for k in sorted(self.projections) if self.projections[k].embeds]

    def as_records(self) -> list[dict]:
        """The whole lens set as plain dicts (the declared spec verbatim) — for the cognition_info
        projection (SURFACE lane) to serialize to both faces. registry-is-truth: this is the discovered
        set, never a hand-listed one."""
        return [dict(self.projections[k].spec) for k in sorted(self.projections)]

    # --- dict-like (mirrors RoleRegistry / _BaseEntryRegistry) ---
    def __getitem__(self, pid: str) -> Projection:
        return self.projections[pid]

    def __contains__(self, pid: str) -> bool:
        return pid in self.projections

    def __iter__(self):
        return iter(self.projections)

    def __len__(self) -> int:
        return len(self.projections)

    def get(self, pid: str, default=None):
        return self.projections.get(pid, default)
