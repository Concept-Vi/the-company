"""tests/authoring_acceptance.py — Concurrent Cognition AUTH (the authoring BACKEND, C7.4/C7.5).

Proves the WRITE-side of the cognition layer BY USE, in an isolated throwaway git repo (mirrors
selfmod_acceptance.py — never touches the real roles/ tree or git history):

  - the create→approve→LIVE loop: propose_role SURFACES (not applied) → simulate operator approve →
    apply_role writes roles/<id>.py + git-commits + the role appears in cognition_info() LIVE (dynamic).
  - the GATE: a role spec that would NOT discover is REFUSED at propose (never reaches roles/, so a bad
    approve can't brick RoleRegistry.discover — the #1 constraint).
  - propose-not-apply governance: apply WITHOUT operator approve is refused (authorization READ from the
    inbox, never a caller flag).
  - validate_rule: a good AST (ok, references, renderable) AND a bad one (now/random/nondeterministic ops
    → fail loud with the reason; a forbidden resolve/approve/dispatch destination → refused).
  - dry_run_rule: the routing decision over sample resolved values.
  - dry_run_role: a draft field-set fires (against the resident 4B if up; offline-skipped otherwise).
  - the selects: models_for_role (only capable models), available_inputs, field_types (the closed set).
  - delete_role: a NON-protected role surfaces + applies (un-registers); a PROTECTED role is REFUSED.
  - THE FLOOR (C9.2): no authoring path emits resolve/approve/dispatch (source-invariant, asserted).
"""
import os
import sys
import shutil
import subprocess
import tempfile
import urllib.request
import urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
os.environ.setdefault("COMPANY_TEST_RUN", "1")             # tag surfaced items as test-origin (inbox hygiene)

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


def _resident_up() -> bool:
    try:
        urllib.request.urlopen("http://127.0.0.1:8000/v1/models", timeout=2)
        return True
    except Exception:
        return False


work = tempfile.mkdtemp(prefix="authoring-test-")
try:
    # --- a throwaway repo with nodes/ + roles/ (a real seed role so discovery has something) ---
    repo = os.path.join(work, "company")
    nodes = os.path.join(repo, "nodes")
    roles = os.path.join(repo, "roles")
    os.makedirs(nodes); os.makedirs(roles)
    subprocess.run(["git", "init", repo], capture_output=True, check=True)
    git(repo, "config", "user.email", "t@t"); git(repo, "config", "user.name", "t")
    open(os.path.join(nodes, "seed.py"), "w").write(
        "VERSION='1'\nKIND='process'\nPORTS_IN={}\nPORTS_OUT={}\ndef run(i,c): return 1\n")
    # a seed FIRE-able role (so cast/cognition_info has content; NOT protected here so delete works)
    open(os.path.join(roles, "tagger.py"), "w").write(
        "from pydantic import BaseModel, Field\n"
        "class TaggerOut(BaseModel):\n    tags: list[str] = Field(default_factory=list)\n"
        "ROLE = {'id':'tagger','prompt_template':'Tag the utterance.','output_schema':TaggerOut,"
        "'mode_scope':['listening']}\n")
    git(repo, "add", "-A"); git(repo, "commit", "-m", "baseline")
    base_head = git(repo, "rev-parse", "HEAD")

    store = FsStore(os.path.join(work, "store"))
    reg = NodeRegistry(); reg.discover([nodes])
    rreg = RoleRegistry().discover([roles])
    suite = Suite(store, reg, nodes_dir=nodes, role_registry=rreg)
    check("seed role discovered (baseline cognition layer up)", "tagger" in suite.role_registry)

    # ====================================================================================
    # 1 · THE CREATE → APPROVE → LIVE LOOP (propose-not-apply)
    # ====================================================================================
    spec = {"id": "sentiment", "label": "Sentiment", "description": "classify tone",
            "prompt_template": "Classify the sentiment of the utterance as positive/negative/neutral.",
            "output_fields": [{"name": "label", "type": "str", "description": "positive/negative/neutral"},
                              {"name": "score", "type": "float"}],
            "input_addresses": ["utterance"], "mode_scope": ["listening"], "requires": ["chat", "json"]}
    p = suite.propose_role(spec)
    sid = p["id"]
    check("propose_role SURFACED a role_build (not applied)", suite.inbox.get(sid)["action"] == "role_build")
    check("propose_role did NOT write the file yet (propose-not-apply)",
          not os.path.exists(os.path.join(roles, "sentiment.py")))
    check("propose_role rendered a real BaseModel module (gate passed)", "class SentimentOut" in p["source"])
    check("the new role is NOT live before approve", "sentiment" not in suite.role_registry)

    # apply WITHOUT operator approve → REFUSED (authorization read from the inbox, never a caller flag)
    from runtime.governance import GovernanceError
    try:
        suite.apply_role(sid); check("apply WITHOUT approve refused", False)
    except GovernanceError:
        check("apply WITHOUT operator approve is REFUSED (authorization read from inbox)", True)
    check("still not written after the refused apply", not os.path.exists(os.path.join(roles, "sentiment.py")))

    # simulate the OPERATOR approve (the operator-only resolve channel), then apply
    suite.resolve_surfaced(sid, "approve")
    path = suite.apply_role(sid)
    check("apply_role wrote roles/sentiment.py", os.path.exists(path) and path.endswith("sentiment.py"))
    head_after = git(repo, "rev-parse", "HEAD")
    check("apply_role made a git commit (the safety net)", head_after != base_head)
    check("the commit is tagged [self-apply]", "[self-apply]" in git(repo, "log", "-1", "--format=%s"))
    # THE LIVE LOOP: it appears in cognition_info() with no FE code (dynamic)
    ci = suite.cognition_info()
    check("the new role is LIVE in cognition_info (create→approve→live)", "sentiment" in ci["roles"])
    check("the live role carries its declared facet (can_fire/mode_scope)",
          ci["roles"]["sentiment"]["can_fire"] and "listening" in ci["roles"]["sentiment"]["mode_scope"])
    check("the live role is in the listening cast (mode-scoped)",
          "sentiment" in ci["casts"]["listening"])

    # apply_surfaced ROUTING: a role_build routes to apply_role, NOT apply_node (constraint C)
    p2 = suite.propose_role({"id": "router_role", "prompt_template": "x",
                             "output_fields": [{"name": "a", "type": "str"}]})
    suite.resolve_surfaced(p2["id"], "approve")
    r2 = suite.apply_surfaced(p2["id"])
    check("apply_surfaced routes role_build → apply_role (kind=role_build, not code_build)",
          r2["kind"] == "role_build")
    check("router_role landed in roles/ not nodes/",
          os.path.exists(os.path.join(roles, "router_role.py")) and
          not os.path.exists(os.path.join(nodes, "router_role.py")))

    # ====================================================================================
    # 2 · THE GATE — a role that would NOT discover is refused at propose (never reaches roles/)
    # ====================================================================================
    try:
        suite.propose_role({"id": "broken", "output_fields": [{"name": "x", "type": "not_a_type"}]})
        check("bad field-type refused at propose", False)
    except Exception as e:
        check("a bad field-type is REFUSED at propose (gate; never bricks discover)",
              "not_a_type" in str(e) or "unknown type" in str(e))
    check("the broken role never reached roles/", not os.path.exists(os.path.join(roles, "broken.py")))
    # a path-traversal id is rejected
    try:
        suite.propose_role({"id": "../evil", "output_fields": []}); check("traversal id refused", False)
    except Exception:
        check("a path-traversal role id is REFUSED (no escape)", True)

    # ====================================================================================
    # 3 · RULE authoring — validate_rule (good + bad), dry_run_rule
    # ====================================================================================
    good_ast = {"op": "and", "args": [{"op": "field", "path": "recall.relevant"},
                                       {"op": "field", "path": "ground.in_scope"}]}
    v = suite.validate_rule(good_ast, destination="inject")
    check("validate_rule(good) → ok", v["ok"])
    check("validate_rule reports the references it reads", set(v["references"]) == {"recall", "ground"})
    check("validate_rule reports renderable + when_text", v["renderable"] and v["when_text"])
    check("validate_rule(inject) → destination_ok", v["destination_ok"] is True)
    # a non-deterministic op cannot even be expressed — an unknown op fails loud
    bad = suite.validate_rule({"op": "now", "args": []})
    check("validate_rule(now/nondeterministic op) → FAILS LOUD with a reason",
          (not bad["ok"]) and bad["errors"])
    # a forbidden destination (the claude -p floor) is refused
    floor = suite.validate_rule(good_ast, destination="resolve")
    check("validate_rule(destination=resolve) → REFUSED (claude -p floor lead-only)",
          (not floor["ok"]) and floor["destination_ok"] is False)

    # dry_run_rule over sample resolved values → the routing decision
    fire = suite.dry_run_rule(good_ast, {"recall": {"relevant": True}, "ground": {"in_scope": True}},
                              destination="inject")
    check("dry_run_rule(both true) → FIRES", fire["ok"] and fire["decision"]["fire"] is True)
    nofire = suite.dry_run_rule(good_ast, {"recall": {"relevant": False}, "ground": {"in_scope": True}})
    check("dry_run_rule(one false) → does NOT fire", nofire["ok"] and nofire["decision"]["fire"] is False)
    miss = suite.dry_run_rule(good_ast, {"recall": {"relevant": True}})   # ground absent
    check("dry_run_rule(missing input) → fail loud (never route on a missing ref)", not miss["ok"])

    # attach_rule → re-proposes the role with the rule (propose-not-apply, surfaces)
    att = suite.attach_rule("sentiment", {"id": "sent-inject", "when": good_ast, "destination": "inject",
                                          "params": {"value_path": "recall.snippet"}})
    check("attach_rule surfaced a role_build edit (propose-not-apply)",
          suite.inbox.get(att["id"])["action"] == "role_build" and att.get("edit"))
    # APPLY the edit + FIDELITY: the role keeps its ORIGINAL output fields AND gains the rule (no lossy
    # round-trip through _role_spec_to_authoring_fields).
    suite.resolve_surfaced(att["id"], "approve")
    suite.apply_role(att["id"])
    s_spec = suite.role_registry["sentiment"].spec
    fnames = set((s_spec.get("output_schema").model_fields or {}).keys())
    check("after attach+apply: the role KEEPS its original output fields (label, score)",
          {"label", "score"} <= fnames)
    check("after attach+apply: the role GAINED the rule (sent-inject)",
          any(r.get("id") == "sent-inject" for r in (s_spec.get("rules") or [])))
    # list[int] round-trip fidelity (the _role_spec_to_authoring_fields edge the advisor flagged)
    fields_back = Suite._role_spec_to_authoring_fields({
        "id": "rt", "output_schema": A.load_role_from_source(
            "rt", A.render_role_source({"id": "rt", "output_fields": [
                {"name": "nums", "type": "list[int]"}, {"name": "txt", "type": "list[str]"}]})).output_schema
    }).get("output_fields", [])
    by = {f["name"]: f["type"] for f in fields_back}
    check("list[int]/list[str] survive the edit round-trip (no silent list[int]→list[str])",
          by.get("nums") == "list[int]" and by.get("txt") == "list[str]")

    # ====================================================================================
    # 4 · THE SELECTS — populated from truth, never hardcoded
    # ====================================================================================
    mfr = suite.models_for_role(["chat", "json"])
    check("models_for_role returns a models list + the live providers", "models" in mfr and "providers" in mfr)
    check("models_for_role(impossible cap) → no model claims it",
          suite.models_for_role(["does_not_exist_cap"])["models"] == [])
    inp = suite.available_inputs()
    check("available_inputs lists the utterance + the fire-able roles' run:// addresses",
          inp["utterance"] == "utterance" and "tagger" in inp["roles"])
    ft = suite.field_types()
    check("field_types is the closed registry (str/int/float/bool/list[str]/list[int])",
          set(ft) == {"str", "int", "float", "bool", "list[str]", "list[int]"})

    # ====================================================================================
    # 5 · DELETE — non-protected surfaces + applies (un-registers); protected refused
    # ====================================================================================
    dprot = suite.delete_role("focus") if "focus" in suite.role_registry else {"protected": True}
    # 'focus' isn't in this throwaway repo, so test the PROTECTED guard directly via a protected-name role:
    open(os.path.join(roles, "judge.py"), "w").write(
        "from pydantic import BaseModel\nclass JudgeOut(BaseModel):\n    ok: bool=True\n"
        "ROLE={'id':'judge','prompt_template':'judge','output_schema':JudgeOut}\n")
    suite._rediscover_roles()
    dj = suite.delete_role("judge")
    check("delete_role(PROTECTED 'judge') → REFUSED (would break runtime import)", dj.get("protected") is True)
    # delete a non-protected role: surfaces → approve → applies → un-registers
    dd = suite.delete_role("tagger")
    check("delete_role(non-protected) SURFACED a role_delete", suite.inbox.get(dd["id"])["action"] == "role_delete")
    suite.resolve_surfaced(dd["id"], "approve")
    suite.apply_role_delete(dd["id"])
    check("after approved delete, the role file is GONE", not os.path.exists(os.path.join(roles, "tagger.py")))
    check("after approved delete, the role UN-registered (live)", "tagger" not in suite.role_registry)

    # ====================================================================================
    # 6 · dry_run_role (a draft field-set fires) — resident-gated
    # ====================================================================================
    if _resident_up():
        out = suite.dry_run_role({"id": "ephemeral_test", "prompt_template":
                                  "Reply with the word 'ok' in a JSON field named done.",
                                  "output_fields": [{"name": "done", "type": "str"}]},
                                 "hello there")
        check("dry_run_role(draft field-set) fired → validated structured output",
              isinstance(out.get("output"), dict) and "done" in out["output"])
        check("dry_run_role draft did NOT write a file (in-isolation)",
              not os.path.exists(os.path.join(roles, "ephemeral_test.py")))
    else:
        print("  skip  dry_run_role by-use (resident 4B at :8000 not up — offline)")

    # ====================================================================================
    # 7 · THE FLOOR (C9.2) — no authoring source emits resolve/approve/dispatch
    # ====================================================================================
    auth_src = open(os.path.join(ROOT, "runtime", "authoring.py")).read()
    # the authoring module never resolves/approves/dispatches (it RENDERS + VALIDATES; governance is in Suite)
    for verb in ("resolve_surfaced", "dispatch_decision", ".resolve(", "is_approved"):
        check(f"runtime/authoring.py never emits {verb} (the floor — authoring renders, never resolves)",
              verb not in auth_src)

    print(f"\nALL {PASS} CHECKS PASS — the authoring backend: create→approve→live, validate/dry-run, "
          f"selects, delete, floor intact" if ok else f"\n{PASS} passed; FAILURES above")
    sys.exit(0 if ok else 1)
finally:
    shutil.rmtree(work, ignore_errors=True)
