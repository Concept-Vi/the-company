"""runtime/edge_kinds.py — ④ THE CONTAINER · L4 · the ONE edge-kind grammar (GRAPH-PATH §3.1).

The file-discovered edge-kind registry: each `edge_kinds/<id>.py` declares a module-level `EDGE_KIND`
dict (a registry ROW). This module DISCOVERS them, ASSEMBLES them into `ledger.edge_kind` (the derived
read side — law 3: vocabulary=files, DB=data), VALIDATES a kind fail-loud (the loader's write gate), and
COMPOSES the declared inverse AT READ (law 4: reverses never stored).

Why a purpose-built registry (not runtime/relation_types.py verbatim): the EDGE_KIND row is a SUPERSET
of RELATION_TYPE — it adds `face` (containment|knowledge|lineage — the JOB), `endpoints`, `behavior`,
`needs_review`. relation_types.RelationTypeRegistry FAILS LOUD on those extra fields (its
RELATION_TYPE_FIELDS is closed). So this reuses the SAME file-discovery PATTERN in a SEPARATE dir with a
richer shape (exactly the board_edges/ precedent: one grammar via one mechanism-shape, separate dir per
vocabulary). Unify into one mechanism when a consumer traverses one unified relation graph.

CLI:  python -m runtime.edge_kinds assemble     # fold edge_kinds/*.py → ledger.edge_kind (upsert; prune stale)
      python -m runtime.edge_kinds show         # print the registry (from files)
      python -m runtime.edge_kinds validate <k> # exit 0 if registered, 1 (fail-loud) if not
"""
from __future__ import annotations
import importlib.util
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDGE_KINDS_DIR = os.path.join(ROOT, "edge_kinds")

# EDGE_KIND row shape (GRAPH-PATH §3.1). Required: id, directed, face. The rest optional.
EDGE_KIND_FIELDS = ("id", "directed", "inverse", "face", "endpoints", "behavior",
                    "label", "description", "near", "far", "needs_review")
FACES = ("containment", "knowledge", "lineage")


def _validate_row(name: str, decl) -> dict:
    """Validate one EDGE_KIND declaration fail-loud (never a silent typo'd field)."""
    if not isinstance(decl, dict):
        raise ValueError(f"edge_kinds/{name}.py: EDGE_KIND must be a dict, got {type(decl).__name__} — fail loud.")
    unknown = [k for k in decl if k not in EDGE_KIND_FIELDS]
    if unknown:
        raise ValueError(f"edge_kinds/{name}.py: unknown EDGE_KIND field(s) {unknown} — allowed "
                         f"{list(EDGE_KIND_FIELDS)}. Fail loud.")
    kid = decl.get("id")
    if kid != name:
        raise ValueError(f"edge_kinds/{name}.py: EDGE_KIND id {kid!r} must equal the filename {name!r} "
                         f"(the address IS the identity — law 1). Fail loud.")
    if "directed" not in decl:
        raise ValueError(f"edge_kinds/{name}.py: EDGE_KIND must declare `directed` (bool). Fail loud.")
    face = decl.get("face", "knowledge")
    if face not in FACES:
        raise ValueError(f"edge_kinds/{name}.py: face {face!r} not one of {FACES} — fail loud.")
    return decl


def discover(dir_path: str = EDGE_KINDS_DIR) -> dict[str, dict]:
    """Load every edge_kinds/<id>.py → {id: row}. Registry-is-truth; a malformed row RAISES."""
    if not os.path.isdir(dir_path):
        raise FileNotFoundError(f"edge_kinds registry dir missing: {dir_path} — fail loud.")
    rows: dict[str, dict] = {}
    for fn in sorted(os.listdir(dir_path)):
        if not fn.endswith(".py") or fn.startswith("_"):
            continue
        name = fn[:-3]
        path = os.path.join(dir_path, fn)
        spec = importlib.util.spec_from_file_location(f"edge_kinds.{name}", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        decl = getattr(mod, "EDGE_KIND", None)
        if decl is None:
            raise ValueError(f"edge_kinds/{fn}: no module-level EDGE_KIND dict — fail loud.")
        row = _validate_row(name, decl)
        row = {**row, "source": f"edge_kinds/{fn}"}
        rows[name] = row
    if not rows:
        raise ValueError(f"edge_kinds registry {dir_path} is EMPTY — no kinds discovered. Fail loud "
                         f"(a silent empty registry would reject every ledger.edge write).")
    return rows


# ── the read-composition: declared inverse applied AT READ (law 4 — reverses never stored) ────────────
def inverse_map(rows: dict[str, dict] | None = None) -> dict[str, str]:
    """kind → its declared inverse NAME (the composed equal-and-opposite). Built from the files."""
    rows = rows or discover()
    return {k: r["inverse"] for k, r in rows.items() if r.get("inverse")}


def forward_of(inverse_name: str, rows: dict[str, dict] | None = None) -> str | None:
    """Given an INVERSE query kind (e.g. 'imported_by'), return the stored forward kind ('imports').
    This is how a query for the reverse composes: look up which forward kind declares this inverse."""
    rows = rows or discover()
    for k, r in rows.items():
        if r.get("inverse") == inverse_name:
            return k
    return None


def compose_inverse(store_q, addr: str, inverse_kind: str, rows: dict[str, dict] | None = None) -> list[dict]:
    """Compose the inverse of a stored edge AT READ — NEVER a stored reverse row (law 4).

    A query for `inverse_kind` (e.g. 'imported_by') resolves to the forward kind that DECLARES it
    ('imports'), then reads ledger.edge WHERE to_resolved/to_raw = addr AND kind = forward, and FLIPS
    each row so the caller sees a clean inverse edge {from: addr, kind: inverse_kind, to: <the importer>}.

    `store_q` is a (sql)->(ok, out) runner (runtime.scope._q or a scratch-DB equivalent). Fail-loud if
    the inverse isn't declared by any registered kind (never a silent empty)."""
    rows = rows or discover()
    fwd = forward_of(inverse_kind, rows)
    if fwd is None:
        raise ValueError(f"compose_inverse: {inverse_kind!r} is not the declared inverse of any registered "
                         f"edge kind (edge_kinds/) — cannot compose. Fail loud, never a silent empty.")
    from runtime.scope import _lit as _l
    ok, out = store_q(
        f"select from_ref, kind, to_raw, to_resolved from ledger.edge "
        f"where kind = {_l(fwd)} and (to_resolved = {_l(addr)} or to_raw = {_l(addr)}) limit 5000")
    if not ok:
        raise ValueError(f"compose_inverse: ledger unreachable composing {inverse_kind!r} on {addr!r} "
                         f"({out[:160]}). Fail loud.")
    composed = []
    for line in out.splitlines():
        if not line.strip():
            continue
        parts = line.split("|")
        if len(parts) < 4:
            continue
        frm, _k, to_raw, to_res = parts[0], parts[1], parts[2], parts[3]
        composed.append({"from": addr, "kind": inverse_kind, "to": frm,
                         "composed_from": {"forward_kind": fwd, "stored_from": frm,
                                           "stored_to": to_res or to_raw}})
    return composed


# ── assemble: fold the files → ledger.edge_kind (the DERIVED read side) ────────────────────────────────
def _pg_array(xs) -> str:
    from runtime.scope import _lit as _l
    if not xs:
        return "NULL"
    inner = ",".join(x.replace("\\", "\\\\").replace('"', '\\"') for x in xs)
    return _l("{" + inner + "}") + "::text[]"


def assemble(store_q=None) -> dict:
    """Upsert every discovered row into ledger.edge_kind + PRUNE rows whose file vanished (registry-is-
    truth). Returns {seeded, pruned, faces:{...}}. Idempotent."""
    from runtime.scope import _q as _default_q, _lit as _l
    q = store_q or _default_q
    rows = discover()
    values = []
    for k, r in rows.items():
        values.append(
            "(" + ", ".join([
                _l(k),
                "true" if r.get("directed", True) else "false",
                _l(r["inverse"]) if r.get("inverse") else "NULL",
                _l(r.get("face", "knowledge")),
                _pg_array(r.get("endpoints")),
                _l(r["behavior"]) if r.get("behavior") else "NULL",
                _l(r["label"]) if r.get("label") else "NULL",
                _l(r["description"]) if r.get("description") else "NULL",
                _l(r["near"]) if r.get("near") else "NULL",
                _l(r["far"]) if r.get("far") else "NULL",
                "true" if r.get("needs_review") else "false",
                _l(r["source"]),
            ]) + ")")
    sql = (
        "INSERT INTO ledger.edge_kind (id,directed,inverse,face,endpoints,behavior,label,description,"
        "near,far,needs_review,source) VALUES\n" + ",\n".join(values) + "\n"
        "ON CONFLICT (id) DO UPDATE SET directed=excluded.directed, inverse=excluded.inverse, "
        "face=excluded.face, endpoints=excluded.endpoints, behavior=excluded.behavior, "
        "label=excluded.label, description=excluded.description, near=excluded.near, far=excluded.far, "
        "needs_review=excluded.needs_review, source=excluded.source, assembled_at=now();")
    ok, out = q(sql)
    if not ok:
        raise RuntimeError(f"edge_kinds.assemble: upsert FAILED ({out[:300]}). Fail loud.")
    # prune stale rows (a file was deleted → its DB row is a ghost — registry-is-truth)
    keep = ",".join(_l(k) for k in rows)
    ok, out = q(f"DELETE FROM ledger.edge_kind WHERE id NOT IN ({keep})")
    if not ok:
        raise RuntimeError(f"edge_kinds.assemble: prune FAILED ({out[:300]}). Fail loud.")
    faces: dict[str, int] = {}
    for r in rows.values():
        faces[r.get("face", "knowledge")] = faces.get(r.get("face", "knowledge"), 0) + 1
    return {"seeded": len(rows), "faces": faces}


def all_ids(store_q=None) -> set[str]:
    """The registered kind ids (from the DB — the read side the loader validates against)."""
    from runtime.scope import _q as _default_q
    q = store_q or _default_q
    ok, out = q("select id from ledger.edge_kind")
    if not ok:
        raise RuntimeError(f"edge_kinds.all_ids: ledger.edge_kind unreachable ({out[:160]}). Fail loud.")
    return {ln.strip() for ln in out.splitlines() if ln.strip()}


def validate_kinds(kinds, store_q=None) -> None:
    """Loader write-gate: RAISE naming edge_kinds/ if any kind is unregistered (fail-loud, C4.1)."""
    registered = all_ids(store_q)
    missing = sorted({k for k in kinds if k and k not in registered})
    if missing:
        raise ValueError(
            f"ledger.edge write BLOCKED — unregistered edge kind(s) {missing}: not in the ledger.edge_kind "
            f"registry. Author a row (edge_kinds/<id>.py declaring EDGE_KIND) then re-assemble "
            f"(python -m runtime.edge_kinds assemble). ABSORB-never-reject: register the kind, never drop "
            f"the edge. Fail loud.")


def _main(argv):
    cmd = argv[1] if len(argv) > 1 else "show"
    if cmd == "assemble":
        print(json.dumps(assemble(), indent=1))
    elif cmd == "show":
        rows = discover()
        for k in sorted(rows):
            r = rows[k]
            print(f"  {k:22} face={r.get('face','knowledge'):11} "
                  f"inverse={r.get('inverse') or '-':22} directed={r.get('directed', True)}")
        print(f"total {len(rows)} kinds")
    elif cmd == "validate":
        k = argv[2]
        try:
            validate_kinds([k])
            print(f"ok: {k!r} is registered")
        except ValueError as e:
            print(str(e), file=sys.stderr)
            sys.exit(1)
    else:
        print(__doc__)
        sys.exit(2)


if __name__ == "__main__":
    _main(sys.argv)
