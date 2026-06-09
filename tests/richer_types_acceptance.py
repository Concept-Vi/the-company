"""tests/richer_types_acceptance.py — Cognition Engine B2 (RICHER output-field types).

Proves the WIDENED output-field grammar BY USE — the field-type registry now supports nested objects,
list[dict]/list[object], enum, optional, and per-field defaults (the original flat scalars stay
byte-identical). `output_schema` is ALREADY real Pydantic; B2 widens the AUTHORING grammar
(runtime/authoring.py FIELD_TYPES rows + a RECURSIVE renderer) — NOT Pydantic, NOT a 2nd registry.

The bar (verify-by-use, against the LIVE create_role path in an isolated throwaway git repo — mirrors
authoring_acceptance.py, never touches the real roles/ tree or git history):

  1 · ADDITIVE / byte-identical — a flat-scalar role renders EXACTLY as before B2 (no Literal import,
      the same Field(...) lines). The richer grammar is purely additive.
  2 · LIVE richer role — create_role authors a role whose output has a NESTED object + an ENUM + an
      OPTIONAL field + list[dict] + defaults → the module RENDERS, the gate PASSES, the role is LIVE in
      cognition_info(), AND its output_schema VALIDATES a nested instance (instantiate, not just compile).
  3 · the GATE BITES — a malformed nested/enum spec is REFUSED at render (AuthoringError) → nothing
      written; and gate_role_source bites on a source that renders to bad Python (defense-in-depth).
  4 · field_types() PROJECTS the widened grammar (registry-is-truth) — each row carries its `kind` +
      the params the richer kinds require (enum→values, object/list[object]→fields) + the aliases.
  5 · THE FLOOR — runtime/authoring.py never emits resolve/approve/dispatch (source-invariant).
"""
import os
import sys
import shutil
import subprocess
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
os.environ.setdefault("COMPANY_TEST_RUN", "1")

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.roles import RoleRegistry
from runtime.suite import Suite
from runtime import authoring as A

PASS = 0
ok = True


def check(label, cond):
    global PASS, ok
    if cond:
        PASS += 1
        print(f"  ok  {label}")
    else:
        ok = False
        print(f"  FAIL  {label}")


def git(root, *args):
    return subprocess.run(["git", "-C", root, *args], capture_output=True, text=True, check=True).stdout.strip()


work = tempfile.mkdtemp(prefix="richer-types-test-")
try:
    # ====================================================================================
    # 1 · ADDITIVE / BYTE-IDENTICAL — a flat-scalar role renders exactly as before B2
    # ====================================================================================
    flat = {
        "id": "flatrole", "label": "Flat", "prompt_template": "You tag.",
        "output_fields": [
            {"name": "relevant", "type": "bool", "description": "is it relevant"},
            {"name": "snippet", "type": "str"},
            {"name": "tags", "type": "list[str]"},
            {"name": "n", "type": "int"},
        ],
        "mode_scope": ["listening"],
    }
    src_flat = A.render_role_source(flat)
    check("flat-scalar role does NOT import Literal (byte-identical: no enum → no extra import)",
          "from typing import Literal" not in src_flat)
    check("flat-scalar role emits the same import line as before B2",
          "from pydantic import BaseModel, Field" in src_flat
          and src_flat.count("(BaseModel):") == 1)         # ONLY the main class — no sub-models
    check("flat bool field: Field(default=False, description=...) (the pre-B2 shape)",
          "    relevant: bool = Field(default=False, description='is it relevant')" in src_flat)
    check("flat str field with no desc: bare `= ''` (the pre-B2 shape)",
          "    snippet: str = ''" in src_flat)
    check("flat list[str] field: Field(default_factory=list) (the pre-B2 shape)",
          "    tags: list[str] = Field(default_factory=list)" in src_flat)
    check("flat int field with no desc: bare `= 0` (the pre-B2 shape)",
          "    n: int = 0" in src_flat)

    # ====================================================================================
    # 2 · LIVE richer role — create_role authors NESTED + ENUM + OPTIONAL + list[dict] + defaults
    # ====================================================================================
    repo = os.path.join(work, "company")
    nodes = os.path.join(repo, "nodes")
    roles = os.path.join(repo, "roles")
    os.makedirs(nodes); os.makedirs(roles)
    subprocess.run(["git", "init", repo], capture_output=True, check=True)
    git(repo, "config", "user.email", "t@t"); git(repo, "config", "user.name", "t")
    open(os.path.join(nodes, "seed.py"), "w").write(
        "VERSION='1'\nKIND='process'\nPORTS_IN={}\nPORTS_OUT={}\ndef run(i,c): return 1\n")
    open(os.path.join(roles, "tagger.py"), "w").write(
        "from pydantic import BaseModel, Field\n"
        "class TaggerOut(BaseModel):\n    tags: list[str] = Field(default_factory=list)\n"
        "ROLE = {'id':'tagger','prompt_template':'Tag the utterance.','output_schema':TaggerOut,"
        "'mode_scope':['listening']}\n")
    git(repo, "add", "-A"); git(repo, "commit", "-m", "baseline")

    store = FsStore(os.path.join(work, "store"))
    reg = NodeRegistry(); reg.discover([nodes])
    rreg = RoleRegistry().discover([roles])
    suite = Suite(store, reg, nodes_dir=nodes, role_registry=rreg)

    rich = {
        "id": "analyst", "label": "Analyst",
        "prompt_template": "Analyze the utterance and report structured findings.",
        "output_fields": [
            {"name": "verdict", "type": "enum", "values": ["yes", "no", "maybe"],
             "description": "the overall call"},
            {"name": "author", "type": "object", "fields": [
                {"name": "name", "type": "str"},
                {"name": "score", "type": "int", "default": 5},
                {"name": "contact", "type": "object", "fields": [
                    {"name": "email", "type": "str"},
                ]},
            ]},
            {"name": "tags", "type": "list[dict]", "fields": [
                {"name": "key", "type": "str"},
                {"name": "weight", "type": "float"},
            ]},
            {"name": "note", "type": "str", "optional": True},
            {"name": "count", "type": "int", "default": 3},
        ],
        "input_addresses": ["utterance"], "mode_scope": ["listening"],
    }
    src_rich = A.render_role_source(rich)
    check("richer role IMPORTS Literal (conditional — an enum appeared)",
          "from typing import Literal" in src_rich)
    check("enum → Literal[...] annotation rendered", "Literal['yes', 'no', 'maybe']" in src_rich)
    check("nested object → a sub-BaseModel emitted (AnalystOutAuthor)",
          "class AnalystOutAuthor(BaseModel):" in src_rich)
    check("doubly-nested object → its sub-model emitted BEFORE its owner (define-before-use)",
          src_rich.index("class AnalystOutAuthorContact(BaseModel):")
          < src_rich.index("class AnalystOutAuthor(BaseModel):"))
    check("list[dict] → list[<SubModel>] annotation", "tags: list[AnalystOutTags]" in src_rich)
    check("optional → `T | None` annotation with default None", "note: str | None" in src_rich)
    check("per-field default rendered (count=3, nested score=5)",
          "Field(default=3" in src_rich and "Field(default=5" in src_rich)

    # CREATE IT LIVE (the real create_role path — render→GATE→write→commit→rediscover)
    res = suite.create_role(rich)
    check("create_role wrote roles/analyst.py + reports live", res["live"] and res["path"].endswith("analyst.py"))
    check("the file exists on disk", os.path.exists(os.path.join(roles, "analyst.py")))
    check("the commit is tagged [self-apply] (git-revertible)",
          "[self-apply]" in git(repo, "log", "-1", "--format=%s"))

    # THE LIVE LOOP: it appears in cognition_info() with no FE code
    ci = suite.cognition_info()
    check("the richer role is LIVE in cognition_info()", "analyst" in ci["roles"])
    check("the richer role can_fire (real prompt_template + BaseModel output_schema)",
          ci["roles"]["analyst"]["can_fire"])

    # THE OUTPUT_SCHEMA VALIDATES A NESTED INSTANCE (instantiate, not just compile)
    role = suite.role_registry["analyst"]
    M = role.output_schema
    inst = M(
        verdict="maybe",
        author={"name": "tim", "score": 9, "contact": {"email": "a@b.c"}},
        tags=[{"key": "x", "weight": 0.5}, {"key": "y", "weight": 1.0}],
        note="a note", count=7,
    )
    check("output_schema validates a NESTED instance (object-in-object resolves)",
          inst.author.contact.email == "a@b.c")
    check("list[dict] validates a list of sub-models", inst.tags[0].key == "x" and inst.tags[1].weight == 1.0)
    check("enum validates a member value", inst.verdict == "maybe")
    check("optional field accepts a value", inst.note == "a note")
    # DEFAULTS applied when omitted
    d = M(verdict="yes", author={"name": "z"}, tags=[])
    check("defaults applied (count→3, nested score→5, optional note→None)",
          d.count == 3 and d.author.score == 5 and d.note is None)
    # ENUM rejects a non-member (real Pydantic validation, not just structure)
    try:
        M(verdict="frobnicate", author={"name": "z"}, tags=[])
        check("enum REJECTS a non-member value", False)
    except Exception:
        check("enum REJECTS a non-member value (real Literal validation)", True)

    # ====================================================================================
    # 3 · THE GATE BITES — malformed nested/enum specs REFUSED (nothing written)
    # ====================================================================================
    base = {"id": "badrole", "prompt_template": "x", "mode_scope": ["listening"]}
    bad_specs = {
        "enum with no values": {**base, "output_fields": [{"name": "v", "type": "enum"}]},
        "enum with empty values": {**base, "output_fields": [{"name": "v", "type": "enum", "values": []}]},
        "enum with non-string values": {**base, "output_fields": [{"name": "v", "type": "enum", "values": [1, 2]}]},
        "object with no fields": {**base, "output_fields": [{"name": "o", "type": "object"}]},
        "list[object] with no fields": {**base, "output_fields": [{"name": "o", "type": "list[object]"}]},
        "unknown type": {**base, "output_fields": [{"name": "o", "type": "frobnicate"}]},
        "non-string type": {**base, "output_fields": [{"name": "o", "type": 123}]},
        "non-literal default": {**base, "output_fields": [{"name": "o", "type": "str", "default": object()}]},
        "nested duplicate field": {**base, "output_fields": [
            {"name": "o", "type": "object", "fields": [{"name": "a", "type": "str"}, {"name": "a", "type": "int"}]}]},
        "nested unknown type": {**base, "output_fields": [
            {"name": "o", "type": "object", "fields": [{"name": "a", "type": "nope"}]}]},
        "nested bad field name": {**base, "output_fields": [
            {"name": "o", "type": "object", "fields": [{"name": "_x", "type": "str"}]}]},
    }
    for label, spec in bad_specs.items():
        refused = False
        try:
            A.render_role_source(spec)
        except A.AuthoringError:
            refused = True
        check(f"malformed spec REFUSED at render ({label}) — nothing written", refused)
    # nothing got written to the roles tree by the refusals
    check("no badrole.py was ever written (refused before any write)",
          not os.path.exists(os.path.join(roles, "badrole.py")))

    # gate_role_source bites on a source that renders to bad Python (defense-in-depth, the #1 constraint)
    syntax_err_src = ("from pydantic import BaseModel, Field\n"
                      "class XOut(BaseModel):\n    a: str =\n"
                      "ROLE = {'id': 'gaterole', 'output_schema': XOut}\n")
    check("gate_role_source BITES on a syntax-error module (would-be-bad role never reaches roles/)",
          A.gate_role_source("gaterole", syntax_err_src) is not None)
    id_mismatch_src = ("from pydantic import BaseModel, Field\n"
                       "class XOut(BaseModel):\n    a: str = ''\n"
                       "ROLE = {'id': 'WRONG', 'output_schema': XOut}\n")
    check("gate_role_source BITES on an id≠filename module",
          A.gate_role_source("gaterole", id_mismatch_src) is not None)

    # ====================================================================================
    # 4 · field_types() PROJECTS the widened grammar (registry-is-truth)
    # ====================================================================================
    ft = suite.field_types()
    check("field_types() still carries the 6 flat scalars",
          {"str", "int", "float", "bool", "list[str]", "list[int]"} <= set(ft))
    check("field_types() now carries the richer kinds (enum/object/list[object])",
          {"enum", "object", "list[object]"} <= set(ft))
    check("scalar rows carry kind=scalar + annotation",
          ft["str"]["kind"] == "scalar" and ft["str"]["annotation"] == "str")
    check("enum row carries kind=enum + params=['values'] (the FE learns the shape)",
          ft["enum"]["kind"] == "enum" and ft["enum"]["params"] == ["values"])
    check("object/list[object] rows carry params=['fields']",
          ft["object"]["params"] == ["fields"] and ft["list[object]"]["params"] == ["fields"])
    check("aliases are FIRST-CLASS rows (kind=alias, alias_of points at the structural kind)",
          ft["list[dict]"]["kind"] == "alias" and ft["list[dict]"]["alias_of"] == "list[object]"
          and ft["dict"]["kind"] == "alias" and ft["dict"]["alias_of"] == "object")
    check("EVERY field_types() row has a uniform shape (a `kind`) — no consumer trap",
          all(isinstance(row, dict) and "kind" in row for row in ft.values()))
    # the alias actually resolves in the renderer
    alias_spec = {"id": "aliasrole", "prompt_template": "x", "mode_scope": ["listening"],
                  "output_fields": [{"name": "rows", "type": "list[dict]",
                                     "fields": [{"name": "k", "type": "str"}]}]}
    check("list[dict] alias renders to list[<SubModel>] (resolves to list[object])",
          "rows: list[AliasroleOutRows]" in A.render_role_source(alias_spec))

    # ====================================================================================
    # 5 · THE FLOOR — authoring renders + validates, never resolves/approves/dispatches
    # ====================================================================================
    auth_src = open(os.path.join(ROOT, "runtime", "authoring.py"), encoding="utf-8").read()
    # strip docstrings/comments would be ideal, but the substrings below never appear in prose here
    for tok in ("dispatch_decision", "resolve_surfaced", "claude -p", "subprocess"):
        check(f"runtime/authoring.py never references {tok!r} (the build-dispatch floor)",
              tok not in auth_src)

    print()
    if ok:
        print(f"ALL {PASS} CHECKS PASS — B2 richer output-field types: nested/enum/optional/list[dict]/"
              f"defaults render→gate→compile→LIVE + validate a nested instance; flat scalars byte-identical; "
              f"the gate bites; field_types() projects the widened grammar; the floor holds.")
    else:
        print("SOME CHECKS FAILED")
        sys.exit(1)
finally:
    shutil.rmtree(work, ignore_errors=True)
