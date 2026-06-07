#!/usr/bin/env python
"""model_capabilities_acceptance — G8 / L-model (C8.1–C8.4): the model-TYPE capability registry.

Proves BY USE:
  C8.1  MODEL_CAPABILITIES keyed by model-id; every field carries {value, source} with a valid
        provenance; resident json_schema/tools = served (live-proven, citing L-transport).
  C8.2  THE JOIN — capabilities_for(resident) reads its backing service via gpu.py (the REAL VRAM
        number, REUSED not duplicated); role_can_bind / suitable_models queries.
  C8.3  cloud decoupled — placement policy as DATA + the swarm-survives-cloud invariant query.
  C8.4  residency fail-loud — is_resident / require_resident loud structured miss (no auto-load).
  C9.4  drift home — every catalog entry has the required fields + provenance; provides ⊆ tag vocab.

Run: PYTHONPATH=/home/tim/company-cognition /home/tim/company/.venv/bin/python tests/model_capabilities_acceptance.py
The live-probe checks (served upgrade) are SKIPPED-not-failed if the resident :8000 is down — the
registry value stays served (from L-transport's proof); the probe only re-confirms it.
"""
import os
import sys

# ops/cli modules use BARE imports (stdlib-only package); add it to the path to import the module.
_OPS_CLI = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ops", "cli")
sys.path.insert(0, _OPS_CLI)

import registry
import gpu
import capabilities as cap

RESIDENT = "cyankiwi/Qwen3.5-4B-AWQ-4bit"
CLOUD = "deepseek-v4-pro:cloud"

_passed = 0
_failed = 0


def check(name, cond, detail=""):
    global _passed, _failed
    if cond:
        _passed += 1
        print(f"  PASS  {name}" + (f"  — {detail}" if detail else ""))
    else:
        _failed += 1
        print(f"  FAIL  {name}" + (f"  — {detail}" if detail else ""))


def main():
    reg = registry.load()

    print("\n[C9.4] drift home — registry hygiene (every entry: required fields + valid provenance)")
    REQUIRED = ("tools", "json_schema", "thinking", "context_ceiling",
                "concurrency_knee", "speed_profile", "provides")
    for mid, spec in cap.MODEL_CAPABILITIES.items():
        for f in REQUIRED:
            check(f"{mid}: has field {f!r}", f in spec)
        for f, v in spec.items():
            if f == "provides":
                check(f"{mid}: provides ⊆ CAPABILITY_TAGS",
                      set(v) <= set(cap.CAPABILITY_TAGS), detail=str(v))
            else:
                check(f"{mid}.{f}: provenance valid",
                      isinstance(v, dict) and v.get("source") in cap.PROVENANCE,
                      detail=str(v.get("source")))
    # json_schema is a FIELD, never a provides-tag (matches the live capability_providers seam)
    check("json_schema is NOT a provides-tag (it is a field)",
          "json_schema" not in cap.CAPABILITY_TAGS or
          all("json_schema" not in s["provides"] for s in cap.MODEL_CAPABILITIES.values()))

    print("\n[C8.1] capabilities_for(resident) — fields + provenance (json_schema/tools served)")
    c = cap.capabilities_for(RESIDENT, reg)
    check("resident is known", c.get("known") is True)
    check("tools served=True", c["tools"]["value"] is True and c["tools"]["source"] == "served",
          detail=str(c["tools"]))
    check("json_schema served=True (L-transport proof)",
          c["json_schema"]["value"] is True and c["json_schema"]["source"] == "served",
          detail=str(c["json_schema"]))
    check("thinking declared=False (no-think model)",
          c["thinking"]["value"] is False and c["thinking"]["source"] == "declared")
    # context ceiling is the model's REAL capacity (262144), not the current max_model_len (65536)
    check("context_ceiling = 262144 served (the JOIN, not max_model_len)",
          c["context_ceiling"]["value"] == 262144 and c["context_ceiling"]["source"] == "served",
          detail=str(c["context_ceiling"]))
    # concurrency-knee is DATA (the C0.5 numbers), never the stale literal 32
    knee = c["concurrency_knee"]["value"]
    check("concurrency_knee is C0.5 DATA (max_num_seqs=16, NOT 32)",
          knee["max_num_seqs"] == 16 and knee != 32, detail=str(knee["max_num_seqs"]))
    check("concurrency_knee carries both loadout points (0.49 voice / 0.63 swarm)",
          set(knee["loadout_points"]) == {"voice_coresident_u0.49", "swarm_mode_u0.63"})
    check("swarm-mode KV = 135574 tokens (C0.5 measured)",
          knee["loadout_points"]["swarm_mode_u0.63"]["kv_pool_tokens"] == 135574)

    print("\n[C8.2] THE JOIN — gpu.py reused for the real VRAM number (not duplicated)")
    check("served_by = chat-4b (the model-id↔service-key JOIN)", c["served_by"] == "chat-4b")
    expected_budget = gpu.budget_vram(reg, "chat-4b")          # the ONE authority — reused
    check("vram_budget_mb == gpu.budget_vram(chat-4b) (REUSE, exact)",
          c["vram_budget_mb"] == expected_budget,
          detail=f"{c['vram_budget_mb']} MB (= config.gpu_util×ceiling, NOT the 7000 estimate)")
    check("vram_budget_mb is the config-derived 8024 (0.49×16376), not the estimate",
          c["vram_budget_mb"] == 8024, detail=str(c["vram_budget_mb"]))
    check("resident_capable DERIVED via gpu.py (budget ≤ card ceiling)",
          c["resident_capable"] is True)

    print("\n[C8.2] role_can_bind / suitable_models queries (requires ⊆ provides)")
    check("role_can_bind({chat,json}, resident) → True",
          cap.role_can_bind({"chat", "json"}, RESIDENT) is True)
    check("role_can_bind({vision}, resident) → False (fail-loud-by-empty)",
          cap.role_can_bind({"vision"}, RESIDENT) is False)
    check("role_can_bind({no-think,fast,json}, resident) → True (the judge's needs)",
          cap.role_can_bind({"no-think", "fast", "json"}, RESIDENT) is True)
    check("provides_for(resident) matches the live capability_providers seam",
          cap.provides_for(RESIDENT) == ["chat", "json", "tools", "fast", "no-think"],
          detail=str(cap.provides_for(RESIDENT)))
    check("suitable_models({chat,json}) includes resident",
          RESIDENT in cap.suitable_models({"chat", "json"}))
    check("role_can_bind({chat}, UNKNOWN-MODEL) → False (never bind to unknown)",
          cap.role_can_bind({"chat"}, "no/such-model") is False)

    print("\n[C8.1] unknown model-id → explicit ASK (never a fabricated row, rule 8)")
    u = cap.capabilities_for("no/such-model", reg)
    check("unknown → known=False + action=ASK", u.get("known") is False and u.get("action") == "ASK")

    print("\n[C8.3] cloud decoupled — placement policy as DATA + the swarm invariant")
    check("swarm placement = resident-always",
          cap.placement_for("swarm")["placement"] == "resident-always")
    check("main_brain selectable resident|cloud",
          cap.placement_for("main_brain")["options"] == ["resident", "cloud"])
    check("background cloud-allowed", cap.placement_for("background")["placement"] == "cloud-allowed")
    check("swarm_survives_cloud_brain() → True (invariant)", cap.swarm_survives_cloud_brain() is True)
    cloud = cap.capabilities_for(CLOUD, reg)
    check("cloud json_schema UNKNOWN (value None, declared) — L-transport gap recorded",
          cloud["json_schema"]["value"] is None and cloud["json_schema"]["source"] == "declared")
    check("cloud has NO local VRAM (served_by None)",
          cloud["served_by"] is None and cloud["vram_budget_mb"] is None)
    try:
        cap.placement_for("nonsense")
        check("placement_for(unknown) fails loud", False, detail="did NOT raise")
    except KeyError:
        check("placement_for(unknown) fails loud (KeyError)", True)

    print("\n[C8.4] residency fail-loud (reuse gpu.py active-view; never auto-load)")
    rr = cap.require_resident(RESIDENT, reg)
    # the resident 4B is normally UP in this env; assert the loud structured SHAPE either way
    if rr["resident"]:
        check("require_resident(resident) → resident=True (live up)", rr["resident"] is True)
        check("is_resident(resident) agrees with gpu.py running-view", cap.is_resident(RESIDENT, reg))
    else:
        check("require_resident(resident, down) → OFFER_LOAD + load_command (no auto-load)",
              rr.get("action") == "OFFER_LOAD" and rr.get("load_command") == "company up chat-4b")
    # an unloaded-but-LOCAL model → loud OFFER_LOAD (pick a registered-but-likely-down service)
    nemo_model = reg["services"]["chat-nemotron"]["config"]["model"]
    rn = cap.require_resident(nemo_model, reg)
    if not rn["resident"]:
        check("require_resident(unloaded local) → OFFER_LOAD + load_command + budget (loud, no degrade)",
              rn["action"] == "OFFER_LOAD" and "company up" in rn["load_command"]
              and rn.get("vram_budget_mb"), detail=rn["load_command"])
    else:
        check("require_resident(local) resident=True", True)
    rc = cap.require_resident(CLOUD, reg)
    check("require_resident(cloud) → resident=False + ASK (no local service)",
          rc["resident"] is False and rc.get("action") == "ASK")

    print("\n[C8.1] LIVE PROBE — re-confirm served (read-only USE of resident :8000)")
    if cap.is_resident(RESIDENT, reg):
        cp = cap.capabilities_for(RESIDENT, reg, live_probe=True)
        check("live tools probe → served=True (probe wins over declared)",
              cp["tools"]["value"] is True and cp["tools"]["source"] == "served",
              detail=cp["tools"].get("note", ""))
    else:
        print("  SKIP  resident :8000 not up — registry value stays served (L-transport proof); "
              "probe only re-confirms")

    print(f"\n=== {_passed} passed, {_failed} failed ===")
    sys.exit(1 if _failed else 0)


if __name__ == "__main__":
    main()
