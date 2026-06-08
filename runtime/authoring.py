"""runtime/authoring.py — the AUTHORING BACKEND (Concurrent Cognition C7.4/C7.5, the write-side).

THE PURE HALF of authoring cognition. This module owns the ONE place a role's declared FIELDS become
a real `roles/<id>.py` Python module, and the gate that validates a generated module OUTSIDE the live
tree before it is ever written. The GOVERNED half (propose→approve→apply, surface_review, the
capability/rule selects) lives in `Suite` (runtime/suite.py) — it CALLS this module; it never re-implements
the renderer (reuse-don't-parallel — there is no second schema builder).

WHY a fields→SOURCE renderer (C7.5 · "dynamically define structured outputs"):
  A role's `output_schema` MUST be a real Pydantic `BaseModel` subclass — `roles._build_role` (roles.py:150)
  REJECTS anything else (fail loud). So "the operator defines a structured output on the surface" means:
  operator field-set → a generated module declaring `class <Name>Out(BaseModel): ...` + `ROLE = {...}`.
  We render ONE source string; the SAME source is what `apply_role` commits AND what `dry_run_role` imports
  from a temp module to fire a draft. No in-memory `create_model` parallel path that drifts from the file.

WHY the GATE matters (the #1 constraint — see advisor):
  Unlike a node (nodes self-register loosely), a malformed `roles/*.py` makes `RoleRegistry.discover` RAISE
  (roles.py `_build_role` fail-loud), which would take down ALL role discovery — and thus `cognition_info()`,
  `cast_for_mode`, the whole cognition layer. So a role module is validated by IMPORTING it in a temp dir
  (mirrors `Suite._gate_extension` running the syntax-gate OUTSIDE the live tree): we build a one-file
  RoleRegistry over a temp dir and confirm it discovers cleanly. A bad spec FAILS LOUD at propose/validate
  time and NEVER reaches the live `roles/` dir.

LAWS honoured: L1 registry-driven (the field-types are a closed registry; an unknown type fails loud) ·
L2 (a rule is a declared AST, never executed here — validation only) · fail loud (every malformed input
RAISES; no silent fallback) · schema-additive · reuse-don't-parallel (ONE renderer; the gate reuses the
real RoleRegistry discovery, never a second validator) · the claude-p floor is untouched (this module
never resolves/approves/dispatches — it RENDERS + VALIDATES; governance lives in Suite).
"""
from __future__ import annotations

import json
import os
import re
import tempfile
from typing import Any


class AuthoringError(Exception):
    """A malformed authoring request — a bad field-type, a bad role id, a role module that won't
    discover. Fail loud; never write a broken file to the live roles/ tree."""


# --- C7.5 · the closed field-type registry (registry-is-truth; an unknown type fails loud) --------
# Maps an operator-facing field-type → the Python annotation rendered into the generated BaseModel.
# A closed set by construction (mirrors RULE_OPS being a closed grammar). Adding a type = a row here
# (+ reflect it in the FE-HANDOFF doc). The FE schema-editor reads this set from /api/cognition/field_types.
FIELD_TYPES: dict[str, dict] = {
    "str":        {"annotation": "str",             "default": "''",   "gloss": "a text field"},
    "int":        {"annotation": "int",             "default": "0",    "gloss": "an integer"},
    "float":      {"annotation": "float",           "default": "0.0",  "gloss": "a decimal number"},
    "bool":       {"annotation": "bool",            "default": "False","gloss": "a true/false flag"},
    "list[str]":  {"annotation": "list[str]",       "default": "list", "gloss": "a list of strings"},
    "list[int]":  {"annotation": "list[int]",       "default": "list", "gloss": "a list of integers"},
}


def field_types() -> dict[str, dict]:
    """The closed field-type registry as a STATUS read (the FE schema-editor's dropdown source —
    registry-is-truth, never a hardcoded FE list). Mirrors how knobs_for()/roles() expose registries."""
    return {k: {"annotation": v["annotation"], "gloss": v["gloss"]} for k, v in FIELD_TYPES.items()}


def _safe_role_id(rid: Any) -> str:
    """A role id must be a plain lower identifier (it becomes the file name AND the ROLE['id'], which
    roles._build_role asserts equals the module name). Reject path-traversal / non-identifiers — the
    same discipline as Suite._safe_node_name, applied to roles. Fail loud."""
    if not isinstance(rid, str) or not rid:
        raise AuthoringError(f"role id must be a non-empty string, got {rid!r}")
    if "/" in rid or "\\" in rid or ".." in rid:
        raise AuthoringError(f"unsafe role id {rid!r} — looks like a path, not a name")
    if not rid.isidentifier() or rid.startswith("_") or rid != rid.lower():
        raise AuthoringError(
            f"role id {rid!r} must be a plain lower-case identifier (no '_'-prefix, no caps, no "
            f"spaces/paths) — it is the file name AND the ROLE id (roles._build_role asserts they match). "
            f"Fail loud.")
    return rid


def _schema_class_name(rid: str) -> str:
    """Derive the generated output_schema class name from the role id ('my_role' → 'MyRoleOut')."""
    return "".join(p.capitalize() for p in re.split(r"[^a-z0-9]+", rid) if p) + "Out"


def render_role_source(spec: dict) -> str:
    """C7.5 — RENDER a `roles/<id>.py` module SOURCE from a declared field-spec. The ONE renderer:
    `apply_role` commits this string; `dry_run_role` imports it from a temp module. Never a second
    builder.

    The declared spec (the operator's field-set, all optional except id+output fields):
      {
        "id": "my_role",                         # required — the file/ROLE id (plain lower identifier)
        "label": "My Role", "description": "...", # operator-facing (the config lab renders these)
        "prompt_template": "You are ...",         # the system prompt (present ⇒ the role can FIRE)
        "output_fields": [                         # the STRUCTURED OUTPUT (C7.5 — fields → BaseModel)
          {"name": "relevant", "type": "bool", "description": "is it relevant"},
          {"name": "snippet",  "type": "str"},
        ],
        "input_addresses": ["utterance"],          # declared inputs (DATA)
        "mode_scope": ["listening"],               # the casts this role is part of
        "trigger": "per-turn",                     # descriptive
        "requires": ["chat", "json"],              # the capability QUERY (role.requires ⊆ model.provides)
        "rules": [ <declared rule dict>, ... ],    # declared routing rules (DATA — AST validated)
      }

    Returns the module source string. Fail loud (AuthoringError) on a bad id / unknown field-type /
    malformed output field. The output_schema is ALWAYS a real BaseModel subclass (roles._build_role's
    hard requirement). A role with no output_fields gets a minimal {ok: bool} schema so it is still a
    valid fire-able role (never a None output_schema)."""
    if not isinstance(spec, dict):
        raise AuthoringError(f"role spec must be a dict, got {type(spec).__name__}")
    rid = _safe_role_id(spec.get("id"))
    cls = _schema_class_name(rid)

    # --- the structured-output fields → the BaseModel body (C7.5) ---
    out_fields = spec.get("output_fields") or []
    if not isinstance(out_fields, list):
        raise AuthoringError(f"role {rid!r}: output_fields must be a list, got {type(out_fields).__name__}")
    field_lines: list[str] = []
    seen: set[str] = set()
    for f in out_fields:
        if not isinstance(f, dict):
            raise AuthoringError(f"role {rid!r}: each output field must be a dict, got {f!r}")
        fname = f.get("name")
        if not isinstance(fname, str) or not fname.isidentifier() or fname.startswith("_"):
            raise AuthoringError(
                f"role {rid!r}: output field name {fname!r} must be a plain identifier (no '_'-prefix). "
                f"Fail loud.")
        if fname in seen:
            raise AuthoringError(f"role {rid!r}: duplicate output field {fname!r}. Fail loud.")
        seen.add(fname)
        ftype = f.get("type", "str")
        if ftype not in FIELD_TYPES:
            raise AuthoringError(
                f"role {rid!r}: field {fname!r} has unknown type {ftype!r} — one of {sorted(FIELD_TYPES)} "
                f"(the closed field-type registry; never invent a type — rule 8). Fail loud.")
        ann = FIELD_TYPES[ftype]["annotation"]
        default = FIELD_TYPES[ftype]["default"]
        desc = f.get("description")
        if desc:
            field_lines.append(
                f"    {fname}: {ann} = Field(default_factory={default}, description={desc!r})"
                if default == "list" else
                f"    {fname}: {ann} = Field(default={default}, description={desc!r})")
        else:
            field_lines.append(
                f"    {fname}: {ann} = Field(default_factory={default})"
                if default == "list" else
                f"    {fname}: {ann} = {default}")
    if not field_lines:
        field_lines.append("    ok: bool = True   # minimal schema (no fields declared) — still a valid BaseModel")

    # --- the ROLE declared dict (DATA — verbatim what the file consumers read) ---
    # #58 DIRECT-CREATE: the renderer now emits the FULL role schema the agent can set — every
    # ROLE_FIELDS key (roles.py), not the original C7.5 subset. A field present in the spec lands
    # verbatim in the written module; an UNKNOWN spec key FAILS LOUD (rule 8 — never a silent typo'd
    # field that no consumer reads; mirrors roles._build_role's own unknown-field fail-loud). The
    # output_schema is rendered by NAME below (a class ref, not JSON) — so it is NOT a JSON-spec key.
    from runtime.roles import ROLE_FIELDS
    # The spec keys that are AUTHORING-TIME params (mapped/handled specially), NOT verbatim ROLE_FIELDS:
    #   id            → set above (the file/ROLE id)
    #   output_fields → rendered into the BaseModel + spliced as output_schema (the class ref)
    #   output_schema → un-authorable as JSON (a class object); set by NAME below. A spec that passes
    #                   it (e.g. round-tripping a serialized role) is IGNORED here — output_fields is
    #                   the authoring surface for the schema.
    #   requires      → mapped to model_binding.requires (the C2.5 capability query)
    #   model / brief → propose-time params (the model override / the brain-draft brief), NOT role fields
    _AUTHORING_ONLY = {"id", "output_fields", "output_schema", "requires", "model", "brief"}
    role_dict: dict[str, Any] = {"id": rid}
    for k, v in spec.items():
        if k in _AUTHORING_ONLY:
            continue
        if k not in ROLE_FIELDS:
            raise AuthoringError(
                f"role {rid!r}: unknown role-schema field {k!r} — the authorable role schema is "
                f"{sorted(set(ROLE_FIELDS) - {'output_schema'}) + ['output_fields', 'requires']} "
                f"(rule 8 — never an invented field that no consumer reads). Fail loud.")
        if v is not None:
            role_dict[k] = list(v) if k == "mode_scope" else v
    # `requires` → the C2.5 model_binding query shape. If the spec ALSO declares an explicit
    # model_binding (the full nested binding), that WINS (no silent merge — fail loud on conflict).
    requires = spec.get("requires")
    if requires:
        if "model_binding" in role_dict and "requires" in (role_dict["model_binding"] or {}):
            raise AuthoringError(
                f"role {rid!r}: both top-level `requires` and `model_binding.requires` declared — "
                f"these conflict (one source). Declare requires in ONE place. Fail loud.")
        role_dict.setdefault("model_binding", {})
        role_dict["model_binding"] = {**role_dict["model_binding"], "requires": list(requires)}
    # output_schema is set by NAME below (the class object reference, not JSON) — handled in the template.

    # The role module is PYTHON, not JSON — the FULL schema now carries booleans (thinking),
    # nested dicts (knobs/model_binding/tools/context), etc. `json.dumps` would emit `false`/`true`/
    # `null` (invalid Python — the gate would (correctly) refuse the module). `pprint.pformat` emits a
    # valid PYTHON literal (False/True/None) for any JSON-shaped value. We render that, then splice the
    # output_schema key in as a bare class reference (output_schema is a class object, not a literal).
    import pprint as _pprint
    body = _pprint.pformat(role_dict, indent=1, width=100, sort_dicts=False)
    # turn the closing brace into ", 'output_schema': <cls>}" so output_schema is the class object.
    assert body.rstrip().endswith("}")
    body = body.rstrip()[:-1].rstrip()
    if body.rstrip().endswith("{"):                       # only the id was present (no trailing comma needed)
        body = body + f"\n    'output_schema': {cls},\n}}"
    else:
        body = body + f",\n    'output_schema': {cls},\n}}"

    src = (
        f'"""roles/{rid}.py — authored cognition role (Concurrent Cognition C7.4/C7.5 · #58 direct-create).\n'
        f'Authored through the cognition surface — DIRECTLY via create_role (the agent authors live, #58)\n'
        f'OR via propose_role→operator-approve→apply_role (surfacing, kept available). Either way validated\n'
        f'by import-in-a-temp-dir (the correctness gate) before it reached the live roles/ tree. A declared\n'
        f'role: the output_schema is a real BaseModel subclass (fail-loud requirement); rules are declared ASTs."""\n'
        f"from pydantic import BaseModel, Field\n\n\n"
        f"class {cls}(BaseModel):\n"
        + "\n".join(field_lines) + "\n\n\n"
        f"ROLE = {body}\n"
    )
    return src


def gate_role_source(rid: str, source: str) -> str | None:
    """THE GATE (the #1 constraint): validate a generated role module by DISCOVERING it in a temp dir
    OUTSIDE the live tree — exactly as Suite._gate_extension runs the syntax-gate on a temp file. Returns
    an error string if the module would not discover cleanly (so a bad role NEVER reaches roles/ and
    bricks RoleRegistry.discover for the WHOLE cognition layer), else None.

    Reuse-don't-parallel: the gate IS the real `RoleRegistry().discover` over a one-file temp dir — the
    SAME fail-loud `_build_role` the live registry uses. We never write a second validator that could
    disagree with discovery."""
    from runtime.roles import RoleRegistry
    d = tempfile.mkdtemp(prefix="role-gate-")
    try:
        path = os.path.join(d, rid + ".py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(source)
        reg = RoleRegistry().discover([d])
        if rid not in reg:
            return (f"role {rid!r} did not register from the generated module (no ROLE dict discovered) "
                    f"— a role module must declare a module-level ROLE dict whose id equals the file name.")
        return None
    except Exception as e:
        return f"{type(e).__name__}: {e}"
    finally:
        import shutil
        shutil.rmtree(d, ignore_errors=True)


def load_role_from_source(rid: str, source: str):
    """Import a generated role module from a temp dir and return its discovered `Role` — the seam
    `dry_run_role` uses to fire a DRAFT role (never-yet-written) in isolation. Reuses the real
    RoleRegistry discovery (the SAME object run_role/run_swarm fire), so a dry-run role behaves
    identically to an applied one. Fail loud (AuthoringError) if it won't discover."""
    from runtime.roles import RoleRegistry
    d = tempfile.mkdtemp(prefix="role-draft-")
    try:
        path = os.path.join(d, rid + ".py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(source)
        reg = RoleRegistry().discover([d])
        if rid not in reg:
            raise AuthoringError(f"draft role {rid!r} did not discover (no ROLE dict).")
        return reg[rid]
    except AuthoringError:
        raise
    except Exception as e:
        raise AuthoringError(f"draft role {rid!r} failed to load: {type(e).__name__}: {e}") from e
    finally:
        import shutil
        shutil.rmtree(d, ignore_errors=True)


# ── #56/#58 · skill + context AUTHORING (the write-half of the skill://context:// registries) ─────
# The same PURE pattern as roles: a fields→SOURCE renderer + an import-in-a-tempdir GATE. A skill/
# context is a registry ROW (`runtime/skills.py:ENTRY_FIELDS` = id·content·label·description) — far
# simpler than a role (no BaseModel, no rules), but the CORRECTNESS GATE is the same #1 constraint:
# a malformed `skills/*.py` makes the registry's `.discover` RAISE (skills.py `_build_entry` fail-loud),
# which would brick skill:// resolution for the whole cognition layer. So a bad entry is validated
# OUTSIDE the live tree and NEVER reaches the live skills/contexts dir. reuse-don't-parallel: the gate
# IS the real SkillRegistry/ContextRegistry discovery, never a second validator.

def _safe_entry_id(eid: Any, kind: str) -> str:
    """A skill/context id must be a plain lower identifier (it becomes the file name AND the id, which
    skills._build_entry asserts equals the module name). Mirrors _safe_role_id. Fail loud."""
    if not isinstance(eid, str) or not eid:
        raise AuthoringError(f"{kind} id must be a non-empty string, got {eid!r}")
    if "/" in eid or "\\" in eid or ".." in eid:
        raise AuthoringError(f"unsafe {kind} id {eid!r} — looks like a path, not a name")
    if not eid.isidentifier() or eid.startswith("_") or eid != eid.lower():
        raise AuthoringError(
            f"{kind} id {eid!r} must be a plain lower-case identifier (no '_'-prefix, no caps, no "
            f"spaces/paths) — it is the file name AND the {kind} id (skills._build_entry asserts they "
            f"match). Fail loud.")
    return eid


def render_entry_source(spec: dict, *, kind: str) -> str:
    """RENDER a `skills/<id>.py` (kind='skill') or `contexts/<id>.py` (kind='context') module SOURCE
    from a declared spec. The ONE renderer for the entry registries (create_skill/create_context
    commit this string). `kind` selects the module-level dict name (SKILL|CONTEXT — the only difference
    between the two registries, exactly mirroring `runtime/skills.py`).

    Spec: {id (plain lower identifier), content (the resolvable value — required), label?, description?}.
    Fail loud (AuthoringError) on a bad id / missing content / unknown field — never write a broken
    entry to the live tree (it would brick the registry's discover)."""
    from runtime.skills import ENTRY_FIELDS
    if not isinstance(spec, dict):
        raise AuthoringError(f"{kind} spec must be a dict, got {type(spec).__name__}")
    if kind not in ("skill", "context"):
        raise AuthoringError(f"render_entry_source: kind must be 'skill'|'context', got {kind!r}")
    attr = "SKILL" if kind == "skill" else "CONTEXT"
    eid = _safe_entry_id(spec.get("id"), kind)
    content = spec.get("content")
    if not isinstance(content, str) or not content:
        raise AuthoringError(
            f"{kind} {eid!r}: must declare a non-empty string `content` (what {kind}://{eid} resolves "
            f"TO — the instructions/blob a role reads). Got {content!r} — fail loud.")
    unknown = [k for k in spec if k not in ENTRY_FIELDS and k != "model"]
    if unknown:
        raise AuthoringError(
            f"{kind} {eid!r}: unknown {kind}-schema field(s) {unknown} — the schema is "
            f"{list(ENTRY_FIELDS)} (rule 8 — never an invented field). Fail loud.")
    entry_dict: dict[str, Any] = {"id": eid, "content": content}
    for k in ("label", "description"):
        if spec.get(k) is not None:
            entry_dict[k] = spec[k]
    body = json.dumps(entry_dict, indent=4, ensure_ascii=False)
    src = (
        f'"""{kind}s/{eid}.py — agent-authored {kind} (Concurrent Cognition C 3b · #56/#58 write-half).\n'
        f'Authored DIRECTLY through the agent surface (create_{kind}); validated by import-in-a-temp-dir\n'
        f'before it ever reached the live {kind}s/ tree. A registry ROW: {kind}://{eid} resolves to its\n'
        f'declared `content` (the reusable {"instructions" if kind == "skill" else "context blob"} a role reads)."""\n'
        f"{attr} = {body}\n"
    )
    return src


def gate_entry_source(eid: str, source: str, *, kind: str) -> str | None:
    """THE GATE for a skill/context (the #1 constraint, mirroring gate_role_source): validate a
    generated entry module by DISCOVERING it in a temp dir OUTSIDE the live tree — so a bad entry NEVER
    reaches the live skills/contexts dir and bricks the registry's discover. Returns an error string if
    it would not discover cleanly, else None. reuse-don't-parallel: the gate IS the real
    SkillRegistry/ContextRegistry discovery (the SAME fail-loud `_build_entry`), never a second validator."""
    from runtime.skills import SkillRegistry, ContextRegistry
    Reg = SkillRegistry if kind == "skill" else ContextRegistry
    d = tempfile.mkdtemp(prefix=f"{kind}-gate-")
    try:
        path = os.path.join(d, eid + ".py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(source)
        reg = Reg().discover([d])
        if eid not in reg:
            return (f"{kind} {eid!r} did not register from the generated module (no {kind.upper()} dict "
                    f"discovered) — a {kind} module must declare a module-level "
                    f"{'SKILL' if kind == 'skill' else 'CONTEXT'} dict whose id equals the file name.")
        return None
    except Exception as e:
        return f"{type(e).__name__}: {e}"
    finally:
        import shutil
        shutil.rmtree(d, ignore_errors=True)
