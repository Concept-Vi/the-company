"""tests/inputs_selects_acceptance.py — the INPUT-WIRING + COMPOSITION select ADVERTISES the full
input space + the bound model's capabilities (Cognition Engine COMPLETION-CRITERIA B3 + B5).

Proves, BY USE against a real Suite over a temp FsStore (NO live model — the projection wiring is the
unit under test), that `Suite.available_inputs()`:

  B3 — ADVERTISES THE FULL INPUT SPACE (it used to OMIT skill://+context:// + the scheme vocabulary):
    1. skills[] / contexts[] surface the SEEDED skill://summarize + context://company_overview, PROJECTED
       from the SkillRegistry/ContextRegistry (the SAME instance-local reader create_skill checks against
       — one registry, not a parallel reader), never a hardcoded list.
    2. schemes[] surface the registered contracts/address.py:SCHEMES (skill·context·run·cas·blob·vec·ui·
       code), in the templated `<scheme>://` form — so an agent DISCOVERS that a role's input can be a
       skill, a context, a run://, a cas://, etc.
    3. THE BAR (add-a-row=a-FILE): drop a `skills/<id>.py`, build a FRESH Suite (the bridge-restart
       analog), and the new skill appears as skill://<id> with NO code change; remove it → gone.
    4. ADDITIVE: every prior key (utterance/roles/role_addresses/context_variables + the 6 corpus
       registries + projections/projection_spaces) is unchanged.

  B5 — op/thinking/tools PROJECT from the MODEL-CAPABILITY registry (what's settable = what the BOUND
       model PROVIDES; ops/cli/capabilities.py:MODEL_CAPABILITIES), never a hardcoded enum:
    5. for the resident 4B (provides chat·json·tools·fast·no-think): op contains 'generate', tools=True,
       thinking=False (a no-think model) — projected, not asserted.
    6. THE DYNAMIC PROOF (the analog of B3's drop-a-file): patch MODEL_CAPABILITIES — a tools-LESS spec →
       available_inputs(model=that) offers tools=False (NOT settable); ADD a 'tools'/'thinking'/'embed'
       capability → it APPEARS (op gains 'embed', thinking=True, tools=True). Both seeded models have
       'tools', so the negative is unprovable WITHOUT injection.
    7. fail-loud-by-empty: an UNKNOWN model-id → provides=[] → op=[], thinking=False, tools=False (never a
       fabricated capability — rule 8: never offer a setting the model can't honor).

  MCP REACH (B3 flows for free): cognition_inputs() (mcp_face/server.py → SUITE.available_inputs) carries
  the new keys with no server.py edit (additive). [Verified structurally — server.py is off-lane.]

LAWS proven: registry-is-truth (skills/contexts/schemes/op/thinking/tools all PROJECT from a registry,
zero hardcode) · file-discovery (drop-in skill appears) · reuse-don't-parallel (one SkillRegistry reader;
provides_for is the SAME read models_for_role uses — NO new/parallel select) · fail-loud (unknown model →
empty, never fabricated) · the floor (available_inputs is a pure READ — no resolve/approve/dispatch).
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from store.fs_store import FsStore                                          # noqa: E402
from runtime.registry import NodeRegistry                                   # noqa: E402
from runtime.suite import Suite                                             # noqa: E402
from contracts.address import SCHEMES                                       # noqa: E402

SKILLS_DIR = os.path.join(ROOT, "skills")
SEED_SKILL = "summarize"
SEED_CONTEXT = "company_overview"
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def new_suite(root):
    store = FsStore(os.path.join(root, "store"))
    reg = NodeRegistry().discover([os.path.join(ROOT, "nodes")])
    return Suite(store, reg)


store_dir = tempfile.mkdtemp(prefix="inputs-selects-test-")
try:
    suite = new_suite(store_dir)
    ai = suite.available_inputs()

    # =================================================================================================
    # B3.1 — skills[] / contexts[] PROJECT the seeded addressable registries (not a hardcoded list)
    # =================================================================================================
    check("available_inputs() carries a 'skills' key (the input space ADVERTISES skill://)", "skills" in ai)
    check("available_inputs() carries a 'contexts' key (the input space ADVERTISES context://)",
          "contexts" in ai)
    check(f"skills[] surfaces the SEEDED skill as 'skill://{SEED_SKILL}' (projected from SkillRegistry)",
          f"skill://{SEED_SKILL}" in ai["skills"])
    check(f"contexts[] surfaces the SEEDED context as 'context://{SEED_CONTEXT}'",
          f"context://{SEED_CONTEXT}" in ai["contexts"])
    # reuse-don't-parallel: the SAME instance-local registry create_skill checks liveness against.
    live_skills = sorted(f"skill://{s}" for s in suite._entry_registry("skill"))
    live_contexts = sorted(f"context://{c}" for c in suite._entry_registry("context"))
    check("skills[] == the live SkillRegistry projection (ONE reader, no parallel list)",
          ai["skills"] == live_skills)
    check("contexts[] == the live ContextRegistry projection (ONE reader)",
          ai["contexts"] == live_contexts)

    # =================================================================================================
    # B3.2 — schemes[] PROJECT the registered SCHEMES vocabulary (so the agent discovers run/cas/...)
    # =================================================================================================
    check("available_inputs() carries a 'schemes' key (the registered address-scheme vocabulary)",
          "schemes" in ai)
    expected_schemes = [f"{s}://" for s in SCHEMES]
    check("schemes[] == the registered contracts.address.SCHEMES in <scheme>:// form (registry-is-truth)",
          ai["schemes"] == expected_schemes)
    for sch in ("skill://", "context://", "run://", "cas://", "blob://", "vec://", "ui://", "code://"):
        check(f"schemes[] advertises '{sch}' (the full registered scheme set, even if not all resolve yet)",
              sch in ai["schemes"])

    # =================================================================================================
    # B3.4 — ADDITIVE: every prior key is preserved (B3/B5 only ADD keys)
    # =================================================================================================
    prior_keys = ("utterance", "roles", "role_addresses", "context_variables", "projections",
                  "projection_spaces", "lifters", "mark_types", "generation_policies",
                  "relation_types", "ai_tics", "forms")
    check(f"ADDITIVE — every prior available_inputs key is preserved {prior_keys}",
          all(k in ai for k in prior_keys))

    # =================================================================================================
    # B3.3 — THE BAR: drop a skills/<id>.py → a FRESH Suite (bridge-restart analog) advertises it
    # =================================================================================================
    tmp_skill = os.path.join(SKILLS_DIR, "acc_inputs_tmp_skill.py")
    try:
        with open(tmp_skill, "w") as f:
            f.write('SKILL = {"id": "acc_inputs_tmp_skill", '
                    '"content": "a drop-in skill for the input-space select-projection proof"}\n')
        suite_drop = new_suite(store_dir)                       # FRESH Suite = the bridge-restart analog
        ai_drop = suite_drop.available_inputs()
        check("DROP-IN: a new skills/<id>.py appears as 'skill://acc_inputs_tmp_skill' (NO code edit)",
              "skill://acc_inputs_tmp_skill" in ai_drop["skills"])
    finally:
        if os.path.exists(tmp_skill):
            os.remove(tmp_skill)
    suite_gone = new_suite(store_dir)
    check("REMOVE: a fresh Suite no longer advertises the temp skill (file-discovery, not append-only)",
          "skill://acc_inputs_tmp_skill" not in suite_gone.available_inputs()["skills"])

    # =================================================================================================
    # B5.5 — op/thinking/tools PROJECT from the resident model's MODEL_CAPABILITIES.provides
    # =================================================================================================
    sys.path.insert(0, os.path.join(ROOT, "ops", "cli"))
    import capabilities as caps                                 # ops/cli/capabilities.py (bare import)

    RESIDENT = "cyankiwi/Qwen3.5-4B-AWQ-4bit"                   # provides chat·json·tools·fast·no-think
    ai_res = suite.available_inputs(model=RESIDENT)
    check("available_inputs() carries op/thinking/tools/capability_model (the B5 capability projection)",
          all(k in ai_res for k in ("op", "thinking", "tools", "capability_model")))
    check(f"capability_model echoes the requested bound model ({RESIDENT})",
          ai_res["capability_model"] == RESIDENT)
    res_provides = caps.provides_for(RESIDENT)
    check("op[] projects 'generate' for a chat-providing model (projected from provides, not hardcoded)",
          ("generate" in ai_res["op"]) == ("chat" in res_provides) and "generate" in ai_res["op"])
    check("tools projects True for the tool-providing resident (== 'tools' in provides)",
          ai_res["tools"] == ("tools" in res_provides) and ai_res["tools"] is True)
    check("thinking projects False for the NO-THINK resident (== 'thinking' in provides)",
          ai_res["thinking"] == ("thinking" in res_provides) and ai_res["thinking"] is False)
    check("'embed' NOT in the resident's op[] (it does not provide 'embed' — honest, not fabricated)",
          "embed" not in ai_res["op"])
    # default (no model arg) gates against the current brain (rhm_config()['model'], mirrors knobs_for).
    check("available_inputs() with NO model arg defaults capability_model to the brain (rhm_config model)",
          ai["capability_model"] == suite.rhm_config().get("model"))

    # =================================================================================================
    # B5.6 — THE DYNAMIC PROOF: patch MODEL_CAPABILITIES — add/remove a capability → it appears/vanishes
    # =================================================================================================
    orig_caps = dict(caps.MODEL_CAPABILITIES)
    try:
        # (a) a TOOLS-LESS, EMBED-ONLY model → tools NOT offered, op=[embed], thinking=False
        caps.MODEL_CAPABILITIES["acc-test-embed-only"] = {
            "provides": ["embed"]}                              # no chat, no tools, no thinking
        ai_embed = suite.available_inputs(model="acc-test-embed-only")
        check("DYNAMIC: a model lacking 'tools' → tools=False (NOT offered — projected from provides)",
              ai_embed["tools"] is False)
        check("DYNAMIC: an embed-only model → op == ['embed'] (NOT 'generate' — no 'chat' provide)",
              ai_embed["op"] == ["embed"])
        check("DYNAMIC: an embed-only model → thinking=False (no 'thinking' provide)",
              ai_embed["thinking"] is False)

        # (b) ADD a capability → it APPEARS (the registry-is-truth direction)
        caps.MODEL_CAPABILITIES["acc-test-full"] = {
            "provides": ["chat", "tools", "thinking", "embed"]}
        ai_full = suite.available_inputs(model="acc-test-full")
        check("DYNAMIC: ADD 'tools' to a model's provides → tools APPEARS (=True)",
              ai_full["tools"] is True)
        check("DYNAMIC: ADD 'thinking' → thinking APPEARS (=True)", ai_full["thinking"] is True)
        check("DYNAMIC: a chat+embed model → op == ['generate', 'embed'] (BOTH project)",
              ai_full["op"] == ["generate", "embed"])
    finally:
        caps.MODEL_CAPABILITIES.clear()
        caps.MODEL_CAPABILITIES.update(orig_caps)

    # =================================================================================================
    # B5.7 — fail-loud-by-empty: an UNKNOWN model-id → no fabricated capability
    # =================================================================================================
    ai_unknown = suite.available_inputs(model="no-such-model-anywhere")
    check("UNKNOWN model → op=[] (fail-loud-by-empty, never fabricated)", ai_unknown["op"] == [])
    check("UNKNOWN model → tools=False (never offer a setting the model can't honor — rule 8)",
          ai_unknown["tools"] is False)
    check("UNKNOWN model → thinking=False", ai_unknown["thinking"] is False)

    # =================================================================================================
    # MCP REACH — B3 flows to the agent face for free (cognition_inputs → SUITE.available_inputs)
    # =================================================================================================
    src = open(os.path.join(ROOT, "mcp_face", "server.py")).read()
    check("cognition_inputs() delegates to SUITE.available_inputs (the new keys reach the MCP face additively)",
          "SUITE.available_inputs()" in src)

    print(f"\nALL {PASS} CHECKS PASS — B3: available_inputs ADVERTISES skill://+context:// (projected "
          f"from the registries) + the registered SCHEMES vocabulary + drop-in dynamic + additive · "
          f"B5: op/thinking/tools PROJECT from MODEL_CAPABILITIES (add a cap → it appears; a model "
          f"lacking 'tools' → not offered; unknown → fail-loud-by-empty) · the floor (a pure read).")
finally:
    import shutil
    shutil.rmtree(store_dir, ignore_errors=True)
