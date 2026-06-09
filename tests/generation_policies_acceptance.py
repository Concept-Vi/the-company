"""tests/generation_policies_acceptance.py — generation-policies as a FILE-DISCOVERED registry
(Cognition Engine NEWMOD · O2 · P1).

THE registry the law "NOTHING static" is made concrete on: the rep_penalty regime is a registry ROW
with a LADDER as DATA + a diff-against-source flag, **add-a-row = a FILE**. Proves BY MECHANISM:
  1. DISCOVER like projections — `GenerationPolicyRegistry` mirrors `ProjectionRegistry`.
  2. DYNAMIC (the BAR) — drop a NEW file → discovered; remove → un-registers.
  3. FAIL LOUD — a malformed policy RAISES (incl. empty/non-ascending/non-float ladder; non-bool diff).
  4. THE LADDER IS DATA — the seed encodes 1.1→1.2→exhausted; next_rep_penalty escalates then returns
     None (= the engine's fail-loud degenerate-loop); diff_against_source is a per-regime flag.
  5. NO FLOOR-BREACH TOKEN — the module never uses a `.resolve(`-named method (floor-safe if enrolled).
  6. DRIFT HOME — every discovered policy is reflected in generation_policies/AGENTS.md.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from runtime.generation_policies import (GenerationPolicyRegistry, GenerationPolicy,  # noqa: E402
                                         _build_policy, GENERATION_POLICY_FIELDS, REQUIRED_FIELDS)

GP_DIR = os.path.join(ROOT, "generation_policies")
SEED_IDS = {"capture_default", "prose_default"}
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


# 1 · DISCOVER
reg = GenerationPolicyRegistry().discover([GP_DIR])
check("registry discovers the seed policies (file-discovered, not a dict)", SEED_IDS <= set(reg))
check("dict-like: reg['capture_default'] is a GenerationPolicy", isinstance(reg["capture_default"], GenerationPolicy))
check("dict-like: 'prose_default' in reg; .get default", "prose_default" in reg and reg.get("nope", "X") == "X")

# 2 · DYNAMIC
tmp_path = os.path.join(GP_DIR, "acc_tmp_policy.py")
try:
    with open(tmp_path, "w") as f:
        f.write('GENERATION_POLICY = {"id": "acc_tmp_policy", "rep_penalty_ladder": [1.05, 1.15], "diff_against_source": False}\n')
    reg2 = GenerationPolicyRegistry().discover([GP_DIR])
    check("DROP-IN: a new generation_policies/<id>.py is discovered with NO code change (the BAR)", "acc_tmp_policy" in reg2)
finally:
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
reg3 = GenerationPolicyRegistry().rediscover([GP_DIR])
check("REMOVE: the temp policy un-registers on rediscover", "acc_tmp_policy" not in reg3)
check("non-GENERATION_POLICY skip: only declaring files register", set(reg3) == set(reg))


# 3 · FAIL LOUD
def raises(label, fn):
    try:
        fn()
    except (ValueError, TypeError):
        check(label, True)
        return
    check(label, False)


raises("bad id (empty) RAISES", lambda: _build_policy("x", {"id": "", "rep_penalty_ladder": [1.1], "diff_against_source": False}))
raises("id != filename RAISES", lambda: _build_policy("x", {"id": "y", "rep_penalty_ladder": [1.1], "diff_against_source": False}))
raises("missing ladder RAISES", lambda: _build_policy("x", {"id": "x", "diff_against_source": False}))
raises("empty ladder RAISES", lambda: _build_policy("x", {"id": "x", "rep_penalty_ladder": [], "diff_against_source": False}))
raises("non-float ladder rung RAISES", lambda: _build_policy("x", {"id": "x", "rep_penalty_ladder": ["a"], "diff_against_source": False}))
raises("non-ascending ladder RAISES", lambda: _build_policy("x", {"id": "x", "rep_penalty_ladder": [1.2, 1.1], "diff_against_source": False}))
raises("non-bool diff_against_source RAISES", lambda: _build_policy("x", {"id": "x", "rep_penalty_ladder": [1.1], "diff_against_source": "no"}))
raises("unknown field RAISES", lambda: _build_policy("x", {"id": "x", "rep_penalty_ladder": [1.1], "diff_against_source": False, "bogus": 1}))
raises("non-dict decl RAISES", lambda: _build_policy("x", ["nope"]))
good = _build_policy("ok", {"id": "ok", "rep_penalty_ladder": [1.1], "diff_against_source": True})
check("a minimal well-formed policy builds", good.id == "ok")

# 4 · THE LADDER IS DATA (the law: NOTHING static)
cap = reg["capture_default"]
check("capture_default ladder is the DATA [1.1, 1.2] (not a code constant)", cap.rep_penalty_ladder == [1.1, 1.2])
check("default_rep_penalty = the first rung (1.1)", cap.default_rep_penalty == 1.1)
check("next_rep_penalty(1.1) escalates to 1.2 (the on-finish=length step)", cap.next_rep_penalty(1.1) == 1.2)
check("next_rep_penalty(1.2) = None (ladder EXHAUSTED → the engine's fail-loud degenerate-loop)",
      cap.next_rep_penalty(1.2) is None)
check("capture_default diff_against_source is True (never a silent penalty on enumeration)", cap.diff_against_source is True)
check("capture_default json_schema True + temp 0.0 (the loop-trigger surface)",
      cap.json_schema is True and cap.temperature == 0.0)
prose = reg["prose_default"]
check("prose_default is a single-rung ladder (the per-regime variation)", prose.rep_penalty_ladder == [1.1])
check("prose_default diff_against_source False (prose is not enumerative)", prose.diff_against_source is False)
check("policy_for('capture_default') returns it; unknown id RAISES",
      reg.policy_for("capture_default") is cap)
unknown_raised = False
try:
    reg.policy_for("nope")
except ValueError:
    unknown_raised = True
check("policy_for(unknown) RAISES fail-loud (registry-is-truth)", unknown_raised)
recs = reg.as_records()
check("as_records() = one dict per policy, verbatim spec", len(recs) == len(reg) and all("rep_penalty_ladder" in r for r in recs))

# 5 · NO FLOOR-BREACH TOKEN (floor-safe if enrolled in COG_SOURCES)
src = open(os.path.join(ROOT, "runtime", "generation_policies.py")).read()
code_no_comments = "\n".join(ln.split("#", 1)[0] for ln in src.splitlines())
import re as _re
check("the module uses NO `.resolve(`-named call in code (the C9.2 floor token stays clean)",
      not _re.search(r"\.resolve\s*\(", code_no_comments))

# 6 · DRIFT HOME
agents_md = open(os.path.join(GP_DIR, "AGENTS.md")).read()
for pid in reg:
    check(f"drift: '{pid}' is reflected in generation_policies/AGENTS.md", f"`{pid}`" in agents_md)
check("the registry is NAMED in its drift home", "GenerationPolicyRegistry" in agents_md)

print(f"\nPASS ({PASS} checks) — generation_policies is a file-discovered registry (O2/P1): the rep_penalty "
      "ladder is DATA (1.1→1.2→fail-loud) + diff-against-source, drift-home reflected.")
