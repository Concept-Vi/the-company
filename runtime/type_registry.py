"""runtime/type_registry.py — THE GENERATIVE TYPE REGISTRY (④ the-one-system · L3 · organ-studies/REGISTRY.md §3).

The rebuilt organ: **B's registration act driving A's cascade** — one INSERT that mints a complete citizen,
with the fan-out's completeness itself registered, tested, and served to both faces from one function.

  "A knew what registration should CAUSE; B knew what registration should BE."  — REGISTRY.md

## The two file-discovered registries this module carries (vocabulary = FILES, law 3)
  · `types/<id>.py`     — one file per universal TYPE, exporting `TYPE = {...}` (the union of both cloud row
                          shapes: data_schema + faces{} + states/transitions). The `faces` keys ARE the
                          cascade ids — presence of a face = `generates[]` membership. RECONSTRUCTED types
                          carry the de-facto schema recovered from lived usage (HOLLOW-TYPES.md).
  · `cascades/<id>.py`  — A's cascade_registry re-homed file-per-row: a module-level `CASCADE = {...}`
                          (id/target/priority/requires/desc/cloud_only) + a `handle(type_row, ctx)` callable.
                          Auto-discovered like nodes/. Iterated by PRIORITY with per-cascade EXCEPTION
                          isolation → honest {ok|error|skipped:reason}.

## The completeness ledger (the net-new REGISTRY.md §2 flagged as IMPLIED-BUT-ABSENT)
A generated artifact is a DERIVED projection row (`type://<id>/face/<cascade>`) recorded in the DB
(container.generated_artifact, migration 0019 — the interim edge home PENDING L4's edge store; breadcrumbed).
ONE direction is stored — `generated_from` = the row's `type_id` (artifact → type). The equal-and-opposite
`generates` (type → artifact) is COMPOSED AT READ (`artifacts_for(type_id)`), never stored — law 4
(reverses declared/composed at read, never duplicated). The drift test asserts every type × applicable
cascade has an artifact OR a recorded skip; a hand-removed artifact fails it loud.

## generated artifacts are NEVER migrated — always REGENERATED (law: one-source; derive-never-place)
The 30 cloud mcp_tool rows / 20 decorators / 16 board rows are NOT imported. The 16 cloud TYPES land as
files; `generate_all` re-derives their artifacts. A DB artifact row whose source TYPE no longer exists is a
GHOST — fails loud.

LAWS: registry-is-truth · vocabulary=FILES / data=DB · fail-loud+breadcrumbs · one-source (types/ is a
PEER dir beside the engine's registries; cascades reference INTO them) · reverses composed at read (law 4) ·
law 11 (states+transitions declared in the type socket; illegal transition refused fail-loud).
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
from dataclasses import dataclass, field
from typing import Any, Callable

# ─────────────────────────────────────────────────────────────────────────────────────────────
# TYPE — the row shape (REGISTRY.md §3.2). Every field except id/label/data_schema is optional, but a
# TRIVIAL data_schema is REFUSED (fixes A's 7 empty {"type":"object"} rows — the hollow gate).
# ─────────────────────────────────────────────────────────────────────────────────────────────
TYPE_FIELDS = ("id", "label", "data_schema", "faces", "states", "initial", "transitions",
               "state_requirements", "version", "desc", "provenance")
TYPE_REQUIRED = ("id", "label", "data_schema")


def _is_trivial_schema(schema: Any) -> bool:
    """The hollow gate: a data_schema is TRIVIAL if it declares no real shape — {} / {"type":"object"}
    alone / no non-empty `properties`. These were A's 7 hollow rows (blocker/decision/… — see
    HOLLOW-TYPES.md); the cascade fanned them out happily, meaning-empty. A trivial schema is REFUSED
    with a teaching error naming the de-facto-schema evidence path."""
    if not isinstance(schema, dict) or not schema:
        return True
    props = schema.get("properties")
    if isinstance(props, dict) and len(props) > 0:
        return False
    # allow a $ref / oneOf/anyOf/allOf composite as non-trivial (a real shape by reference)
    if any(k in schema for k in ("$ref", "oneOf", "anyOf", "allOf", "items", "enum")):
        return False
    return True


TRIVIAL_SCHEMA_TEACHING = (
    "type {id!r}: `data_schema` is TRIVIAL ({schema!r}) — a type with no real shape is exactly A's 7 hollow "
    "rows that the cloud cascade fanned out meaning-empty. REFUSED (registry-is-truth: ask, don't fabricate). "
    "Recover the de-facto schema from lived usage before registering: the 319 board posts' content keys per "
    "type (see build-prep/the-one-system/organ-studies/HOLLOW-TYPES.md — the per-type de-facto schemas + the "
    "shared core {{title, description, priority, issue_number}} + the per-type closure/verification block). "
    "A real `data_schema` declares a non-empty `properties` (or a $ref/oneOf/items composite)."
)


@dataclass
class Type:
    """A discovered universal TYPE — the declared dict (`spec`) verbatim + typed accessors."""
    id: str
    label: str
    spec: dict

    @property
    def data_schema(self) -> dict:
        return self.spec.get("data_schema") or {}

    @property
    def faces(self) -> dict:
        return self.spec.get("faces") or {}

    @property
    def states(self) -> list[str]:
        return list(self.spec.get("states") or [])

    @property
    def initial(self) -> str | None:
        return self.spec.get("initial")

    @property
    def transitions(self) -> dict:
        return self.spec.get("transitions") or {}

    @property
    def state_requirements(self) -> dict:
        return self.spec.get("state_requirements") or {}


def _validate_states(rid: str, spec: dict) -> None:
    """Law 11: if a type declares states, they must be self-consistent — initial ∈ states, every
    transition source/target ∈ states. FAIL LOUD (a malformed lifecycle socket is a bug, never silent)."""
    states = spec.get("states")
    if states is None:
        return                                             # a type MAY be stateless (additive)
    if not isinstance(states, list) or not all(isinstance(s, str) for s in states):
        raise ValueError(f"type {rid!r}: `states` must be a list[str] (law 11 state vocabulary). Got {states!r}.")
    sset = set(states)
    initial = spec.get("initial")
    if initial is not None and initial not in sset:
        raise ValueError(f"type {rid!r}: `initial` {initial!r} not in states {states} — fail loud (law 11).")
    trans = spec.get("transitions") or {}
    if not isinstance(trans, dict):
        raise ValueError(f"type {rid!r}: `transitions` must be a dict state→[allowed]. Got {type(trans).__name__}.")
    for src, dsts in trans.items():
        if src not in sset:
            raise ValueError(f"type {rid!r}: transition source {src!r} not in states {states} — fail loud (law 11).")
        if not isinstance(dsts, list) or any(d not in sset for d in dsts):
            raise ValueError(
                f"type {rid!r}: transition targets {dsts!r} from {src!r} must all be in states {states} — "
                f"fail loud (law 11: no transition to an undeclared state).")


def _build_type(name: str, decl: dict) -> Type:
    """Validate + build a Type. FAIL LOUD on malformed (mirrors _build_relation_type). Enforces the
    HOLLOW GATE (trivial data_schema refused) so a hollow row can never go live from ANY door."""
    if not isinstance(decl, dict):
        raise TypeError(f"type module {name!r}: TYPE must be a dict, got {type(decl).__name__} — fail loud.")
    rid = decl.get("id")
    if not rid or not isinstance(rid, str):
        raise ValueError(f"type module {name!r}: declares no string `id` — fail loud (never unnamed).")
    if rid != name:
        raise ValueError(f"type module {name!r}: id {rid!r} != module name {name!r} — id must equal file stem.")
    unknown = [k for k in decl if k not in TYPE_FIELDS]
    if unknown:
        raise ValueError(f"type {rid!r}: unknown field(s) {unknown} — schema is {list(TYPE_FIELDS)}. Fail loud.")
    missing = [k for k in TYPE_REQUIRED if k not in decl]
    if missing:
        raise ValueError(f"type {rid!r}: missing required field(s) {missing} — a type MUST declare "
                         f"{list(TYPE_REQUIRED)}. Fail loud.")
    label = decl.get("label")
    if not isinstance(label, str) or not label:
        raise ValueError(f"type {rid!r}: `label` must be a non-empty string. Fail loud.")
    schema = decl.get("data_schema")
    if _is_trivial_schema(schema):
        raise ValueError(TRIVIAL_SCHEMA_TEACHING.format(id=rid, schema=schema))
    faces = decl.get("faces")
    if faces is not None and not isinstance(faces, dict):
        raise ValueError(f"type {rid!r}: `faces` must be a dict (face-key → spec). Got {type(faces).__name__}.")
    _validate_states(rid, decl)
    return Type(id=rid, label=label, spec=dict(decl))


def _load_module(path: str):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(f"_type_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return name, mod


class TypeRegistry:
    """The file-discovered TYPE registry — mirrors RelationTypeRegistry/RoleRegistry/NodeRegistry (the ONE
    registry mechanism, reuse-don't-parallel). Dict-like. Adding a type = dropping a `types/<id>.py`
    declaring `TYPE = {...}` (via create(kind='type') — gated, committed). A removed file un-registers on
    rediscover()."""

    def __init__(self):
        self.types: dict[str, Type] = {}

    def discover(self, dirs: list[str]) -> "TypeRegistry":
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                name, mod = _load_module(os.path.join(d, fn))
                decl = getattr(mod, "TYPE", None)
                if decl is None:
                    continue
                self.register(name, decl)
        return self

    def rediscover(self, dirs: list[str]) -> "TypeRegistry":
        self.types.clear()
        return self.discover(dirs)

    def register(self, name: str, decl: dict) -> None:
        self.types[name] = _build_type(name, decl)

    def as_records(self) -> list[dict]:
        return [dict(self.types[k].spec) for k in sorted(self.types)]

    # dict-like
    def __getitem__(self, rid: str) -> Type:
        return self.types[rid]

    def __contains__(self, rid: str) -> bool:
        return rid in self.types

    def __iter__(self):
        return iter(self.types)

    def __len__(self) -> int:
        return len(self.types)

    def get(self, rid: str, default=None):
        return self.types.get(rid, default)


# ─────────────────────────────────────────────────────────────────────────────────────────────
# CASCADE — A's cascade_registry re-homed file-per-row. A module exports CASCADE={...} (DATA) + a
# handle(type_row, ctx) callable (CODE — so cascades are code-authored like nodes/, NOT create()-authorable;
# a cascade carries a function, which pprint can't serialize — exactly the lifter/form line in suite.py).
# ─────────────────────────────────────────────────────────────────────────────────────────────
CASCADE_FIELDS = ("id", "target", "priority", "requires", "cloud_only", "desc")
CASCADE_REQUIRED = ("id", "target", "priority")


@dataclass
class Cascade:
    id: str
    target: str
    priority: int
    handle: Callable
    requires: list[str] = field(default_factory=list)
    cloud_only: bool = False
    spec: dict = field(default_factory=dict)


def _build_cascade(name: str, decl: dict, handle: Callable) -> Cascade:
    if not isinstance(decl, dict):
        raise TypeError(f"cascade module {name!r}: CASCADE must be a dict, got {type(decl).__name__}.")
    cid = decl.get("id")
    if not cid or not isinstance(cid, str):
        raise ValueError(f"cascade module {name!r}: no string `id` — fail loud.")
    if cid != name:
        raise ValueError(f"cascade module {name!r}: id {cid!r} != module name {name!r} — id must equal file stem.")
    unknown = [k for k in decl if k not in CASCADE_FIELDS]
    if unknown:
        raise ValueError(f"cascade {cid!r}: unknown field(s) {unknown} — schema is {list(CASCADE_FIELDS)}.")
    missing = [k for k in CASCADE_REQUIRED if k not in decl]
    if missing:
        raise ValueError(f"cascade {cid!r}: missing required field(s) {missing}. Fail loud.")
    if not isinstance(decl.get("priority"), int):
        raise ValueError(f"cascade {cid!r}: `priority` must be an int (iteration order). Fail loud.")
    if not callable(handle):
        raise ValueError(f"cascade module {name!r}: must export a `handle(type_row, ctx)` callable. Fail loud.")
    return Cascade(id=cid, target=decl["target"], priority=decl["priority"], handle=handle,
                   requires=list(decl.get("requires") or []), cloud_only=bool(decl.get("cloud_only")),
                   spec=dict(decl))


class CascadeRegistry:
    """The file-discovered CASCADE registry. A removed file un-registers on rediscover(). Sorted by PRIORITY
    (the run order — A's priority discipline preserved)."""

    def __init__(self):
        self.cascades: dict[str, Cascade] = {}

    def discover(self, dirs: list[str]) -> "CascadeRegistry":
        for d in dirs:
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if not fn.endswith(".py") or fn.startswith("_"):
                    continue
                name, mod = _load_module(os.path.join(d, fn))
                decl = getattr(mod, "CASCADE", None)
                if decl is None:
                    continue
                self.cascades[name] = _build_cascade(name, decl, getattr(mod, "handle", None))
        return self

    def rediscover(self, dirs: list[str]) -> "CascadeRegistry":
        self.cascades.clear()
        return self.discover(dirs)

    def by_priority(self) -> list[Cascade]:
        return [self.cascades[k] for k in sorted(self.cascades, key=lambda k: (self.cascades[k].priority, k))]

    def as_records(self) -> list[dict]:
        return [dict(self.cascades[k].spec) for k in sorted(self.cascades)]

    def __contains__(self, cid): return cid in self.cascades
    def __iter__(self): return iter(self.cascades)
    def __len__(self): return len(self.cascades)
    def get(self, cid, default=None): return self.cascades.get(cid, default)


# ─────────────────────────────────────────────────────────────────────────────────────────────
# THE ARTIFACT STORE — the DERIVED projection (data = DB). Injectable (like the wire's committer) so
# acceptance can prove the fan-out mechanism without a live DB, AND a real psql round-trip proves the
# projection. ONE direction stored (type_id = generated_from); `generates` composed at read (law 4).
# INTERIM edge home PENDING L4's edge store (breadcrumb — REGISTRY.md / IMPLEMENTATION-GUIDE §L3).
# ─────────────────────────────────────────────────────────────────────────────────────────────
def artifact_address(type_id: str, cascade_id: str) -> str:
    """The artifact identity (law 1: text address = identity). One per (type, cascade)."""
    return f"type://{type_id}/face/{cascade_id}"


class MemoryArtifactStore:
    """In-memory artifact store — for acceptance without a live DB (the mechanism is DB-independent)."""

    def __init__(self):
        self._rows: dict[str, dict] = {}                   # address → row

    def put(self, address, type_id, cascade_id, target, payload):
        self._rows[address] = {"address": address, "type_id": type_id, "cascade_id": cascade_id,
                               "target": target, "payload": payload}

    def retract_type(self, type_id) -> int:
        gone = [a for a, r in self._rows.items() if r["type_id"] == type_id]
        for a in gone:
            del self._rows[a]
        return len(gone)

    def retract_address(self, address) -> int:
        return 1 if self._rows.pop(address, None) is not None else 0

    def artifacts_for(self, type_id) -> list[dict]:      # the `generates` reverse, composed at read (law 4)
        return [dict(r) for r in self._rows.values() if r["type_id"] == type_id]

    def all_artifacts(self) -> list[dict]:
        return [dict(r) for r in self._rows.values()]


class PgArtifactStore:
    """The live projection: container.generated_artifact (migration 0019). Reached via psql (the scope.py
    convention — one connection home). FAIL LOUD on an unreachable/failed query (never a silent success)."""

    def __init__(self, pg: dict | None = None):
        self.pg = pg or {
            "host": os.environ.get("COMPANY_LEDGER_PGHOST", "127.0.0.1"),
            "port": os.environ.get("COMPANY_LEDGER_PGPORT", "15432"),
            "user": os.environ.get("COMPANY_LEDGER_PGUSER", "postgres"),
            "db":   os.environ.get("COMPANY_LEDGER_PGDB", "postgres"),
            "pw":   os.environ.get("COMPANY_LEDGER_PGPASSWORD", "postgres"),
        }

    def _q(self, sql: str) -> str:
        r = subprocess.run(["psql", "-h", self.pg["host"], "-p", self.pg["port"], "-U", self.pg["user"],
                            "-d", self.pg["db"], "-tAc", sql], capture_output=True, text=True, timeout=30,
                           env={**os.environ, "PGPASSWORD": self.pg["pw"]})
        if r.returncode != 0:
            raise RuntimeError(f"generated_artifact query FAILED (fail loud): {(r.stderr or '').strip()[:300]}. "
                               f"Fix: apply migrations/0019_type_registry.sql (psql -f ...).")
        return r.stdout

    @staticmethod
    def _lit(s: str) -> str:
        s = str(s)
        i = 0
        while True:
            tag = f"$a{i}$"
            if tag not in s:
                return f"{tag}{s}{tag}"
            i += 1

    def put(self, address, type_id, cascade_id, target, payload):
        import json as _json
        pj = self._lit(_json.dumps(payload))
        self._q(f"insert into container.generated_artifact(address,type_id,cascade_id,target,payload) "
                f"values({self._lit(address)},{self._lit(type_id)},{self._lit(cascade_id)},"
                f"{self._lit(target)},{pj}::jsonb) on conflict(address) do update set "
                f"type_id=excluded.type_id,cascade_id=excluded.cascade_id,target=excluded.target,"
                f"payload=excluded.payload,generated_at=now();")

    def retract_type(self, type_id) -> int:
        out = self._q(f"with d as (delete from container.generated_artifact where type_id={self._lit(type_id)} "
                      f"returning 1) select count(*) from d;")
        return int((out or "0").strip() or 0)

    def retract_address(self, address) -> int:
        out = self._q(f"with d as (delete from container.generated_artifact where address={self._lit(address)} "
                      f"returning 1) select count(*) from d;")
        return int((out or "0").strip() or 0)

    def artifacts_for(self, type_id) -> list[dict]:
        out = self._q(f"select address,cascade_id,target from container.generated_artifact "
                      f"where type_id={self._lit(type_id)} order by address;")
        rows = []
        for ln in out.splitlines():
            if not ln.strip():
                continue
            a, c, t = (ln.split("|") + ["", "", ""])[:3]
            rows.append({"address": a, "type_id": type_id, "cascade_id": c, "target": t})
        return rows

    def all_artifacts(self) -> list[dict]:
        out = self._q("select address,type_id,cascade_id,target from container.generated_artifact order by address;")
        rows = []
        for ln in out.splitlines():
            if not ln.strip():
                continue
            a, ty, c, t = (ln.split("|") + ["", "", "", ""])[:4]
            rows.append({"address": a, "type_id": ty, "cascade_id": c, "target": t})
        return rows


# ─────────────────────────────────────────────────────────────────────────────────────────────
# generate_all — the FAN-OUT. Iterate cascades by priority; per-cascade EXCEPTION isolation → honest
# {ok|error|skipped:reason}. IDEMPOTENT per type: each ok cascade UPSERTS its artifact by address, so a
# re-run never duplicates (and never false-trips completeness). Records the generated_from edge (the
# artifact row's type_id); `generates` is the read-time reverse (law 4).
# ─────────────────────────────────────────────────────────────────────────────────────────────
def generate_all(type_row: Type, cascades: CascadeRegistry, store, *, ctx: dict | None = None) -> dict:
    ctx = dict(ctx or {})
    faces = type_row.faces
    results = []
    for cas in cascades.by_priority():
        entry = {"cascade": cas.id, "target": cas.target, "priority": cas.priority}
        # skipped — a declared cloud-only target that does not exist in ④ (honest decline, not a dead handler)
        if cas.cloud_only:
            results.append({**entry, "status": "skipped",
                            "reason": f"target {cas.target!r} is cloud-only, not present in ④ (regenerate on the "
                                      f"cloud/read side; ④ derives only the in-scope faces)"})
            continue
        # skipped — the type declares no face this cascade REQUIRES (presence of a face = generates[] membership)
        missing = [f for f in cas.requires if f not in faces]
        if missing:
            results.append({**entry, "status": "skipped",
                            "reason": f"type {type_row.id!r} declares no {missing} face — nothing to generate "
                                      f"(add a faces.{missing[0]} to generate this target)"})
            continue
        # ok / error — run the handler under per-cascade isolation (A's exception isolation preserved)
        try:
            payload = cas.handle(type_row.spec, ctx)
            address = artifact_address(type_row.id, cas.id)
            store.put(address, type_row.id, cas.id, cas.target, payload or {})
            results.append({**entry, "status": "ok", "address": address,
                            "generated_from": type_row.id, "payload": payload or {}})
        except Exception as e:                             # noqa: BLE001 — deliberate per-cascade containment
            results.append({**entry, "status": "error", "error": f"{type(e).__name__}: {e}"})
    counts = {"ok": sum(1 for r in results if r["status"] == "ok"),
              "skipped": sum(1 for r in results if r["status"] == "skipped"),
              "error": sum(1 for r in results if r["status"] == "error")}
    return {"type": type_row.id, "results": results, "counts": counts}


# ─────────────────────────────────────────────────────────────────────────────────────────────
# THE COMPLETENESS LEDGER — the run-all-report-holes loop A never had (30-vs-4 counts proved its absence).
# For every type × cascade: an artifact OR a recorded skip. A hand-removed artifact (present face, missing
# row) is DRIFT → fails loud. A GHOST (an artifact row whose source type no longer exists) also fails loud.
# ─────────────────────────────────────────────────────────────────────────────────────────────
def completeness(types: TypeRegistry, cascades: CascadeRegistry, store) -> dict:
    drift, ghosts, per_type = [], [], {}
    live_type_ids = set(types)
    for tid in sorted(types):
        trow = types[tid]
        faces = trow.faces
        arts = {r["cascade_id"]: r for r in store.artifacts_for(tid)}
        cells = []
        for cas in cascades.by_priority():
            applicable = (not cas.cloud_only) and all(f in faces for f in cas.requires)
            has = cas.id in arts
            if applicable and not has:
                drift.append({"type": tid, "cascade": cas.id,
                              "why": "applicable cascade produced no artifact (hand-removed or never generated)"})
            cells.append({"cascade": cas.id, "applicable": applicable, "artifact": has})
        per_type[tid] = cells
    # GHOSTS — a DB artifact row with no source type file (registry-is-truth: files author, DB derives)
    for r in store.all_artifacts():
        if r["type_id"] not in live_type_ids:
            ghosts.append({"address": r["address"], "orphan_type": r["type_id"],
                           "why": f"artifact for type {r['type_id']!r} which has no types/{r['type_id']}.py "
                                  f"(a DB row with no source file is a ghost — fix: create(kind='type',…) or "
                                  f"delete_type retract)"})
    complete = not drift and not ghosts
    return {"complete": complete, "drift": drift, "ghosts": ghosts, "per_type": per_type}


# ─────────────────────────────────────────────────────────────────────────────────────────────
# LAW 11 — states declared in the type socket; illegal INSTANCE transition refused fail-loud; a resolver
# read varies by state. One function each, both faces (law 9).
# ─────────────────────────────────────────────────────────────────────────────────────────────
def validate_transition(type_row: Type, from_state: str, to_state: str) -> dict:
    """Refuse an illegal instance transition FAIL-LOUD (law 11). Returns the accepted move on success."""
    states = set(type_row.states)
    if not states:
        raise ValueError(f"type {type_row.id!r} declares no states — it has no lifecycle to transition (law 11).")
    if from_state not in states:
        raise ValueError(f"type {type_row.id!r}: unknown from-state {from_state!r} (declared: {sorted(states)}).")
    if to_state not in states:
        raise ValueError(f"type {type_row.id!r}: unknown to-state {to_state!r} (declared: {sorted(states)}).")
    allowed = type_row.transitions.get(from_state, [])
    if to_state not in allowed:
        raise ValueError(
            f"type {type_row.id!r}: ILLEGAL transition {from_state!r} → {to_state!r}. Legal from {from_state!r}: "
            f"{allowed or '[]'} (law 11: transitions declared in the type socket; a resolver refuses the rest).")
    return {"type": type_row.id, "from": from_state, "to": to_state, "ok": True}


def state_view(type_row: Type, state: str) -> dict:
    """A resolver read that VARIES BY STATE (law 11, grounded in the task verification-block glow): closure
    states (e.g. task 'done') REQUIRE the closure/verification block; open states do not. Same function,
    both faces (law 9)."""
    states = set(type_row.states)
    if state not in states:
        raise ValueError(f"type {type_row.id!r}: unknown state {state!r} (declared: {sorted(states)}).")
    reqs = type_row.state_requirements.get(state, [])
    outgoing = type_row.transitions.get(state, [])
    return {
        "type": type_row.id, "state": state,
        "is_terminal": len(outgoing) == 0,
        "next_states": outgoing,
        "closure_required": list(reqs),                    # the state-varying payload — empty for open states
        "requires_closure_proof": bool(reqs),
    }
