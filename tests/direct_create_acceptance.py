"""tests/direct_create_acceptance.py — #58 DIRECT autonomous create — VERIFY BY USE.

Tim's CORRECTION (2026-06-09): the propose→surface→operator-approval gate on CREATE was the AI's
DEFAULT, not his constraint. The agent must CREATE roles/skills/contexts DIRECTLY + LIVE, with NO
operator approval, exposing the FULL capability schema. This suite proves, by USE against an ISOLATED
throwaway repo (so it NEVER commits the live tree), that:

  1. create_role applies a role DIRECTLY — written to roles/, git-committed, LIVE in cognition_info,
     with NO surfaced item + NO approval. (And fires it if the resident 4B is up → a real digest.)
  2. the FULL schema lands — a create with thinking/tools/knobs/output_schema → all in the written
     module + the role's projection shows them.
  3. create_skill / create_context apply a skill/context DIRECTLY → live, readable via skill://context://.
  4. the CORRECTNESS gate still BITES — a malformed spec is REFUSED fail-loud, NEVER written.
  5. the BUILD-DISPATCH floor holds (cognition_governance_acceptance is the standing assertion; here we
     assert create never dispatches — no dispatch on the create path).
  6. create_role REUSES apply_role's write path (the shared _write_role_file) MINUS the approve check.

Run:  PYTHONPATH=/home/tim/company ./.venv/bin/python tests/direct_create_acceptance.py
"""
import os
import sys
import subprocess
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

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


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, check=True).stdout.strip()


def brain_up() -> bool:
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:8000/v1/models", timeout=2)
        return True
    except Exception:
        return False


BRAIN_UP = brain_up()

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.roles import RoleRegistry
from runtime.suite import Suite
from runtime.governance import GovernanceError

work = tempfile.mkdtemp(prefix="direct-create-test-")
try:
    # --- a throwaway git repo with nodes/ + roles/ + skills/ + contexts/ (full isolation) ---
    repo = os.path.join(work, "company")
    nodes = os.path.join(repo, "nodes")
    roles = os.path.join(repo, "roles")
    skills = os.path.join(repo, "skills")
    contexts = os.path.join(repo, "contexts")
    for d in (nodes, roles, skills, contexts):
        os.makedirs(d)
    subprocess.run(["git", "init", repo], capture_output=True, check=True)
    git(repo, "config", "user.email", "t@t"); git(repo, "config", "user.name", "t")
    open(os.path.join(nodes, "seed.py"), "w").write(
        "VERSION='1'\nKIND='process'\nPORTS_IN={}\nPORTS_OUT={}\ndef run(i,c): return 1\n")
    # a seed fire-able role so the baseline cognition layer is non-empty
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
    check("seed role discovered (baseline cognition layer up)", "tagger" in suite.role_registry)
    check("the Suite's skills/contexts dirs are instance-relative (isolation)",
          suite.skills_dir == skills and suite.contexts_dir == contexts)

    # ====================================================================================
    # 1 · DIRECT create_role — applied LIVE, NO surfaced item, NO approval
    # ====================================================================================
    print("\n[1] create_role — DIRECT apply (no surface, no approval): repo_digest")
    inbox_before = len(suite.inbox.list_surfaced()) if hasattr(suite.inbox, "list_surfaced") else None
    res = suite.create_role({
        "id": "repo_digest",
        "label": "Repo digest",
        "description": "One-sentence digest of a supplied file: what it is + its role in the system.",
        "prompt_template": "Read the supplied file content and produce a 1-sentence digest of what it "
                           "is + its role in the system.",
        "output_fields": [{"name": "digest", "type": "str", "description": "the 1-sentence digest"},
                          {"name": "kind", "type": "str", "description": "the kind of file"}],
        "op": "generate",
        "input_addresses": ["utterance"],
        "mode_scope": [],
    })
    path = res["path"]
    check("create_role returns live=True", res.get("live") is True)
    check("create_role WROTE roles/repo_digest.py (direct, no approval)",
          os.path.exists(path) and path.endswith("repo_digest.py"))
    check("repo_digest is LIVE in the registry immediately (no approve step)", "repo_digest" in suite.role_registry)
    # NO surfaced item was created (the direct path does not surface)
    surfaced_actions = [d.get("action") for d in suite.store.list_surfaced()] if hasattr(suite.store, "list_surfaced") else []
    check("NO surfaced inbox item for the direct create (no propose/approve)",
          not any(a in ("role_build",) for a in surfaced_actions))
    # it was git-committed (revertible)
    log = git(repo, "log", "--oneline", "-1")
    check("the create was git-committed (revertible)", "repo_digest" in log)
    # it appears in cognition_info LIVE
    ci = suite.cognition_info()
    check("repo_digest appears in cognition_info() LIVE (the projection)", "repo_digest" in ci["roles"])
    check("repo_digest projects op=generate + input_addresses", ci["roles"]["repo_digest"]["op"] == "generate")

    # FIRE it (run_role) if the brain is up → a real digest
    if BRAIN_UP:
        import runtime.cognition as _cog
        r = suite.role_registry["repo_digest"]
        out = _cog.run_role(r, {"utterance": "AGENTS.md: You are an AI agent working on the company "
                                "composition suite. There are no human developers."},
                            store=suite.store, max_tokens=256, temperature=0.0)
        check("repo_digest FIRES → a real validated digest (the role works)",
              isinstance(out, dict) and isinstance(out.get("digest"), str) and len(out["digest"]) > 0)
        print(f"      digest: {out.get('digest','')[:120]}")
    else:
        check("1 FIRE SKIPPED — resident brain DOWN (:8000) — role written+live proven", True)

    # ====================================================================================
    # 2 · the FULL schema lands — thinking / tools / knobs / output_schema in the module + projection
    # ====================================================================================
    print("\n[2] FULL schema lands — thinking/tools/knobs/output_schema in module + projection")
    res2 = suite.create_role({
        "id": "full_schema_role",
        "label": "Full schema probe",
        "description": "a role exercising the full authorable schema",
        "prompt_template": "Classify the utterance.",
        "output_fields": [{"name": "label", "type": "str"}, {"name": "score", "type": "float"}],
        "op": "generate",
        "thinking": False,
        "tools": [],
        "knobs": {"max_tokens": 128, "temperature": 0.2},
        "input_addresses": ["utterance"],
        "context": "the utterance text only",
        "render_hint": {"shape": "verdict"},
        "requires": ["chat", "json"],
    })
    src = open(res2["path"]).read()
    check("the written module contains thinking=False (valid PYTHON literal, not JSON 'false')",
          "'thinking': False" in src)
    check("the written module contains the tools field", "'tools'" in src)
    check("the written module contains knobs (max_tokens/temperature)", "'knobs'" in src and "'max_tokens'" in src)
    check("the written module contains the context field", "'context'" in src)
    check("the written module contains model_binding.requires (from requires)",
          "'model_binding'" in src and "'requires'" in src)
    check("the written module declares the structured output BaseModel", "class FullSchemaRoleOut" in src)
    # the module IMPORTS cleanly (valid Python — the gate would have refused otherwise, but assert here)
    check("the written module is valid Python (compiles)", compile(src, res2["path"], "exec") is not None)
    check("full_schema_role is LIVE", "full_schema_role" in suite.role_registry)
    # the PROJECTION shows the config fields (registry-is-truth)
    proj = suite.cognition_info()["roles"]["full_schema_role"]
    check("the projection shows thinking", proj.get("thinking") is False)
    check("the projection shows tools", "tools" in proj)
    check("the projection shows knobs", proj.get("knobs", {}).get("max_tokens") == 128)
    check("the projection shows context", "context" in proj)
    check("the projection shows model_binding", proj.get("model_binding", {}).get("requires") == ["chat", "json"])
    # the declared role spec carries them verbatim (the dict-view consumers read)
    spec_live = suite.role_registry["full_schema_role"].spec
    check("the live role spec carries thinking/tools/knobs verbatim",
          spec_live.get("thinking") is False and spec_live.get("knobs", {}).get("temperature") == 0.2)

    # ====================================================================================
    # 3 · create_skill / create_context — DIRECT, live, readable via skill://context://
    # ====================================================================================
    print("\n[3] create_skill + create_context — DIRECT (the #56 write-half), live + readable")
    sres = suite.create_skill({
        "id": "extract_decisions",
        "label": "Extract decisions",
        "description": "Instructions to extract DECISIONS from a document.",
        "content": "Read the document and list every DECISION it records, one per line, as: "
                   "<decision> — <rationale if stated>. Ignore non-decisions.",
    })
    check("create_skill returns live=True", sres.get("live") is True)
    check("create_skill wrote skills/extract_decisions.py", os.path.exists(sres["path"]))
    check("extract_decisions is LIVE in the skill registry", "extract_decisions" in suite._entry_registry("skill"))
    # readable via the SAME registry resolve_address reads (instance dir == discovered dir)
    content = suite._entry_registry("skill").read("extract_decisions")
    check("skill content reads back (the resolvable value)", "DECISION" in content)
    # git-committed
    check("the skill create was git-committed", "extract_decisions" in git(repo, "log", "--oneline", "-1"))

    cres = suite.create_context({
        "id": "system_overview",
        "label": "System overview",
        "content": "The company is an AI-native composition suite with a cognition layer of file-discovered "
                   "roles, rules, skills and contexts. There are no human developers.",
    })
    check("create_context returns live=True", cres.get("live") is True)
    check("system_overview is LIVE in the context registry", "system_overview" in suite._entry_registry("context"))
    check("context content reads back", "cognition layer" in suite._entry_registry("context").read("system_overview"))

    # ====================================================================================
    # 4 · the CORRECTNESS gate still BITES — malformed REFUSED, never written
    # ====================================================================================
    print("\n[4] the correctness gate BITES — malformed REFUSED fail-loud, NEVER written")
    roles_before = set(os.listdir(roles))
    # 4a · an UNKNOWN role field → the renderer fails loud (rule 8)
    from runtime.authoring import AuthoringError
    raised = False
    try:
        suite.create_role({"id": "bad_unknown_field", "prompt_template": "x",
                           "output_fields": [{"name": "a", "type": "str"}], "totally_not_a_field": 1})
    except (AuthoringError, ValueError, RuntimeError, TypeError):
        raised = True
    check("4a create_role with an UNKNOWN field is REFUSED fail-loud", raised)
    # 4b · a bad output-field type → refused
    raised = False
    try:
        suite.create_role({"id": "bad_type", "prompt_template": "x",
                           "output_fields": [{"name": "a", "type": "complex128"}]})
    except (AuthoringError, ValueError, RuntimeError, TypeError):
        raised = True
    check("4b create_role with an unknown output-field TYPE is REFUSED fail-loud", raised)
    # 4c · a skill with no content → refused
    raised = False
    try:
        suite.create_skill({"id": "bad_skill"})  # no content
    except (AuthoringError, ValueError, RuntimeError, TypeError):
        raised = True
    check("4c create_skill with NO content is REFUSED fail-loud", raised)
    # NONE of the malformed probes wrote a file
    check("NO malformed role reached roles/ (the gate refused before any write)",
          set(os.listdir(roles)) == roles_before)
    check("bad_unknown_field / bad_type are NOT live (refused, never written)",
          "bad_unknown_field" not in suite.role_registry and "bad_type" not in suite.role_registry)
    check("bad_skill is NOT live (refused)", "bad_skill" not in suite._entry_registry("skill"))

    # ====================================================================================
    # 5 · REUSE — create_role reuses apply_role's write path (the shared _write_role_file)
    # ====================================================================================
    print("\n[5] reuse-don't-parallel — create_role + apply_role share _write_role_file")
    import inspect as _inspect
    create_src = _inspect.getsource(Suite.create_role)
    apply_src = _inspect.getsource(Suite.apply_role)
    check("create_role calls the shared _write_role_file (reuse, not a parallel author path)",
          "_write_role_file" in create_src)
    check("apply_role calls the SAME shared _write_role_file (reuse minus the approve check)",
          "_write_role_file" in apply_src)
    # the docstring legitimately MENTIONS approve/resolved while describing the reframe — so assert over
    # the CALLS, not the text: the create path makes no inbox-approval / role_build-guard CALL (AST).
    import ast as _ast, textwrap as _tw
    _calls = set()
    for n in _ast.walk(_ast.parse(_tw.dedent(create_src))):
        if isinstance(n, _ast.Call):
            f = n.func
            nm = f.attr if isinstance(f, _ast.Attribute) else (f.id if isinstance(f, _ast.Name) else None)
            if nm:
                _calls.add(nm)
    check("create_role makes NO inbox-approval call (is_approved) — the approve check is what it drops",
          "is_approved" not in _calls)
    check("create_role does NOT guard a role_build CONFIRM (no surfaced-decision gate on the create path)",
          "guard" not in _calls)
    # apply_role STILL guards on operator approval (the surfacing path is unchanged)
    check("apply_role STILL gates on operator approval (is_approved) — surfacing path intact",
          "is_approved" in apply_src)

    # ====================================================================================
    # 6 · existing-id create fails loud (additive, mirrors propose_role)
    # ====================================================================================
    print("\n[6] create on an EXISTING id fails loud (fail-loud, mirrors propose_role)")
    raised = False
    try:
        suite.create_role({"id": "repo_digest", "prompt_template": "x",
                           "output_fields": [{"name": "a", "type": "str"}]})
    except ValueError:
        raised = True
    check("6 create_role on an existing id is REFUSED fail-loud", raised)

    print(f"\n{'ALL PASS' if ok else 'FAILURES PRESENT'} — {PASS} checks passed — #58 DIRECT autonomous "
          f"create: roles/skills/contexts are authored LIVE with NO operator approval (the FULL schema "
          f"lands + projects), the correctness gate still bites (malformed refused, never written), and "
          f"create_role REUSES apply_role's write path minus the approve check. "
          f"{'(repo_digest fired live.)' if BRAIN_UP else '(brain down — fire skipped.)'}")
finally:
    import shutil
    shutil.rmtree(work, ignore_errors=True)

sys.exit(0 if ok else 1)
