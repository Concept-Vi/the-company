"""tests/roles_acceptance.py — the file-discovered ROLE registry (Concurrent Cognition G2).

Asserts C2.1–C2.4 BY MECHANISM (no live model needed — the firing-by-use proof is /tmp/g2_byuse.py
against the resident 4B; this suite is the durable convergence record of the registry's structure):
  C2.1  roles are FILE-DISCOVERED registry data — drop a file → discovered+queryable; remove → it
        un-registers on rediscover; a malformed role FAILS LOUD; a non-role/_-file is skipped.
  C2.2  the judge is role #0 in the registry, bound to its resident-4B recommendation, UNCHANGED in
        behaviour (its resolve_role-relevant keys are byte-identical to the old hardcoded dict; it is
        config-only — in no cast, not fireable).
  C2.3  the `listening` cast exists (focus·recall·ground·connect·check·voice) + is mode-scoped; an
        unknown mode yields an EMPTY cast (never a default-fire).
  C2.4  jury/ensemble is first-class — a role may declare draws:N + a callable verdict_rule; a jury
        with no verdict_rule FAILS LOUD; the verdict is a PURE function over the draws.
  + the laws: a role declares the C2.5 requires query (not prose); the registry mirrors NodeRegistry
    (reuse-don't-parallel); the roles drift home (roles/AGENTS.md) reflects every discovered role.
"""
import os, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from pydantic import BaseModel
from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.roles import RoleRegistry, model_satisfies, resolve_binding
from runtime.suite import Suite

ROLES = os.path.join(ROOT, "roles")
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def _unsat(su):
    """A role requiring an UNprovided capability with NO declared default must fail loud (C2.5)."""
    class _R:
        id = "x"; requires = ["vision"]
        @property
        def model_binding(self): return {}
    try:
        resolve_binding(_R(), su.capability_providers()); return False
    except ValueError:
        return True


store = FsStore(os.path.join(tempfile.mkdtemp(prefix="roles-"), "store"))
reg = NodeRegistry(); reg.discover([os.path.join(ROOT, "nodes")])
su = Suite(store, reg, nodes_dir=os.path.join(ROOT, "nodes"))
rr = su.role_registry

# ---- C2.1 — file-discovered registry data, queryable ----
check("roles are discovered from roles/*.py (the judge + the listening cast + the jury)",
      {"judge", "focus", "recall", "ground", "connect", "check", "voice", "verify_jury"} <= set(rr.roles))
check("RoleRegistry mirrors NodeRegistry (discover/rediscover/register present)",
      all(hasattr(rr, m) for m in ("discover", "rediscover", "register")))
# drop a role file → discovered + queryable WITHOUT code change
probe = os.path.join(ROLES, "g2t_probe.py")
try:
    open(probe, "w").write(
        'from pydantic import BaseModel\n'
        'class O(BaseModel):\n    ok: bool\n'
        'ROLE={"id":"g2t_probe","prompt_template":"x","output_schema":O,"mode_scope":{"listening"}}\n')
    rdrop = RoleRegistry().discover([ROLES])
    check("dropping a role FILE → it is discovered (no code change)", "g2t_probe" in rdrop)
    check("the dropped role is queryable in its mode cast", "g2t_probe" in [r.id for r in rdrop.cast_for_mode("listening")])
finally:
    os.remove(probe)
rrm = RoleRegistry().rediscover([ROLES])
check("removing the role file → it un-registers on rediscover", "g2t_probe" not in rrm)

# C2.1 adversarial — a malformed role file FAILS LOUD (not silently skipped)
bad = os.path.join(ROLES, "g2t_bad.py")
try:
    open(bad, "w").write('ROLE={"id":"NOTMYNAME","prompt_template":"x"}\n')
    try:
        RoleRegistry().discover([ROLES]); raise AssertionError("did not fail loud")
    except (ValueError, TypeError):
        check("a MALFORMED role file FAILS LOUD at discovery (not silently skipped)", True)
finally:
    os.remove(bad)
# a jury without a verdict_rule fails loud
jbad = os.path.join(ROLES, "g2t_jurybad.py")
try:
    open(jbad, "w").write(
        'from pydantic import BaseModel\n'
        'class O(BaseModel):\n    ok: bool\n'
        'ROLE={"id":"g2t_jurybad","prompt_template":"x","output_schema":O,"draws":3}\n')
    try:
        RoleRegistry().discover([ROLES]); raise AssertionError("jury w/o verdict_rule did not fail loud")
    except ValueError:
        check("a jury (draws>1) with NO verdict_rule FAILS LOUD", True)
finally:
    os.remove(jbad)
# a non-role / _-prefixed file is SKIPPED (not raised)
nr = os.path.join(ROLES, "_g2t_notrole.py")
try:
    open(nr, "w").write("X = 1\n")
    rnr = RoleRegistry().discover([ROLES])
    check("a non-role / _-prefixed file is SKIPPED (not registered, not raised)",
          "g2t_notrole" not in rnr and "_g2t_notrole" not in rnr)
finally:
    os.remove(nr)

# ---- C2.2 — the judge is role #0, byte-identical behaviour ----
judge = rr["judge"].spec
check("the judge is in the registry (role #0)", "judge" in rr)
RESOLVE_KEYS = ("default_model", "default_base_url", "thinking", "output", "tools", "context",
                "knobs", "env_model", "env_url", "env_knobs")
OLD = {"default_model": None, "default_base_url": None, "thinking": False,
       "output": "one word: FINISHED | MORE", "tools": [],
       "context": "the utterance text only (no system grounding)",
       "knobs": {"max_tokens": 2048, "temperature": 0},
       "env_model": "COMPANY_JUDGE_MODEL", "env_url": "COMPANY_JUDGE_URL",
       "env_knobs": {"max_tokens": "COMPANY_JUDGE_MAX_TOKENS"}}
check("the judge's resolve_role-relevant keys are BYTE-IDENTICAL to the old hardcoded dict (C2.2)",
      all(judge.get(k) == OLD[k] for k in RESOLVE_KEYS))
check("resolve_role('judge') resolves through the registry (unchanged effective binding)",
      su.resolve_role("judge")["role"] == "judge" and su.resolve_role("judge")["knobs"] == OLD["knobs"])
check("the judge is config-only — in NO mode cast", all("judge" not in [r.id for r in su.cast_for_mode(m)] for m in su.MODES))
check("the judge is NOT fireable (no prompt_template — it is fired by is_finished_thought, not the swarm)",
      not rr["judge"].can_fire)
check("the judge declares its recommended resident-4B model (the day-one pick)",
      judge["recommended_model"] == "cyankiwi/Qwen3.5-4B-AWQ-4bit")
# C2.2 BY-USE (offline part): the judge FIRES through the file-discovered registry. The full live
# firing (a real FINISHED/MORE verdict against the resident 4B) is in /tmp/g2_byuse.py — captured:
# complete thought -> FINISHED (336ms), fragment -> MORE (62ms), empty -> MORE (no model call). Here
# we assert the EMPTY path (no live model needed) so this suite proves the firing chain wiring too.
check("the judge fires via is_finished_thought (empty -> not finished, no model call — chain wired)",
      su.is_finished_thought("")["finished"] is False)

# ---- C2.3 — the listening cast exists + is mode-scoped ----
cast = [r.id for r in su.cast_for_mode("listening")]
check("the `listening` cast = focus·recall·ground·connect·check·voice (C2.3)",
      set(cast) == {"focus", "recall", "ground", "connect", "check", "voice"})
check("every listening-cast role is fireable (declares prompt_template + output_schema)",
      all(rr[rid].can_fire for rid in cast))
check("every listening-cast role declares input_addresses + an output_schema + a rule",
      all(rr[rid].spec.get("input_addresses") and rr[rid].output_schema is not None
          and rr[rid].spec.get("rules") for rid in cast))
check("an UNKNOWN mode yields an EMPTY cast (never a default-fire, never a crash)",
      su.cast_for_mode("zzz-not-a-mode") == [])
check("a different mode has a different/empty cast (mode-scoped, not global)",
      su.cast_for_mode("off") != cast)

# ---- C2.4 — jury/ensemble first-class ----
jury = rr["verify_jury"]
check("a jury role declares draws:N (>1)", jury.is_jury and jury.draws == 3)
check("a jury declares a CALLABLE verdict_rule (a pure function, not a model call)", callable(jury.verdict_rule))
# the verdict_rule is PURE + deterministic over draws (no live model needed)
draws_a = [{"holds": True, "reason": "x"}, {"holds": False, "reason": "y"}, {"holds": True, "reason": "z"}]
v1 = jury.verdict_rule(draws_a)
v2 = jury.verdict_rule(list(reversed(draws_a)))  # order-independent → deterministic
check("the verdict is a deterministic majority vote (2 of 3 true → verdict True)", v1["verdict"] is True and v1["votes_true"] == 2)
check("the verdict is order-INDEPENDENT (deterministic over the draws — C0.2/H7 scope)", v1 == v2)

# ---- laws: C2.5 requires-query (not prose) · reuse-don't-parallel · role cannot emit resolve ----
check("a role declares a `requires` capability QUERY (C2.5 — not hand-written prose)",
      rr["focus"].requires == ["chat", "json"])
check("the C2.5 query is role.requires ⊆ provider.provides", model_satisfies(["chat"], ["chat", "json"]))
check("an unsatisfiable requires with no default FAILS LOUD (never a silent wrong binding)",
      _unsat(su))
# a role has NO path to emit resolve/approve/dispatch — it is pure data + a model call (claude -p floor lead-only)
check("a role's spec carries no resolve/approve/dispatch verb (the build-dispatch floor is lead-only)",
      all(k not in rr[rid].spec for rid in rr.roles for k in ("resolve", "approve", "dispatch", "verb")))

# ---- drift home: roles/AGENTS.md reflects every discovered role (mirrors edge_kinds drift home) ----
constitution = open(os.path.join(ROLES, "AGENTS.md")).read()
missing = [rid for rid in rr.roles if rid not in constitution]
check(f"every discovered role is reflected in its drift home roles/AGENTS.md (drift: {missing})", not missing)
check("the role registry is NAMED in its drift home", "RoleRegistry" in constitution)

print(f"\nALL {PASS} CHECKS PASS — file-discovered roles · judge byte-identical · listening cast mode-scoped · jury first-class · drift home")
