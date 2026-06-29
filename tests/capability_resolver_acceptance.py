#!/usr/bin/env python
"""capability_resolver_acceptance — the SAFE half (C1 registries + C2 resolver) of the
capability-resolution architecture (CAPABILITY-RESOLUTION-DESIGN-CORRECTED.md).

This is the drift/acceptance home for runtime/capabilities/ (the three file-discovered registries
+ resolver.py). It proves the SAFE half WITHOUT wiring anything live — nothing imports the resolver
into the launch path yet (that is the later LIVE phase). The proof of correctness is that
serve_flags() REPRODUCES the current launch flags for the EXISTING config-driven services,
byte-for-byte, read from ops/services.json as the ground truth.

Proves BY USE:
  1. resolve_capabilities works — family defaults resolve; a per-model capability_overrides ⊕
     merges on top (override wins); an unknown family fails loud.
  2. serve_flags REPRODUCES the current launch flags for the existing models — for each
     config-driven service (chat-4b/chat-2b/chat-08b · embed-bge/embed-jina-v5/embed-qwen3),
     serve_flags(migrated_declaration) == services.json config.flags, VERBATIM. The expected list
     is read from services.json (NOT hand-transcribed) — services.json IS the ground truth.
  3. Adding a capability / stack / family is ONE row — add a row to a registry FILE -> it appears
     via the resolver with NO code edit (reload_registries from a temp file).
  4. FAIL-LOUD — a missing/malformed/empty registry RAISES; a stack that cannot express an owned
     capability RAISES (on_unexpressible=fail_loud, no silent flag drop).

Run: PYTHONPATH=/home/tim/company /home/tim/company/.venv/bin/python tests/capability_resolver_acceptance.py
"""
import json
import os
import sys
import tempfile

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO)

from runtime.capabilities import resolver as R

_SERVICES_PATH = os.path.join(_REPO, "ops", "services.json")

# The vLLM config-driven services that route through serve_model.sh -> serveconfig.args_for (the LIVE
# launch path). Each is now MIGRATED in services.json (config.family declared, flags[] RETIRED). The
# [5] section calls serveconfig.args_for(key) on EACH and asserts it emits the migrated flags WITHOUT
# RAISING — the proof that BUG 1's loud-fail no longer fires for any migrated model (the resolver-on-
# in-memory-declarations test does NOT prove the services.json migration; this does).
VLLM_CONFIG_SERVICES = [
    "chat-4b", "chat-4b-fp8", "chat-2b", "chat-08b", "chat-nemotron",
    "embed-bge", "embed-jina-v5", "embed-qwen3",
]

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


def _load_services():
    with open(_SERVICES_PATH) as f:
        return json.load(f)["services"]


def main():
    svcs = _load_services()

    print("\n[1] resolve_capabilities — family defaults ⊕ overrides (override wins), fail-loud on unknown")
    base = R.resolve_capabilities("qwen3.5")
    check("qwen3.5 resolves to the vllm stack", base["stack"] == "vllm", detail=base["stack"])
    check("qwen3.5 provides the chat tags",
          set(base["provides"]) == {"chat", "json", "tools", "fast", "no-think"}, detail=str(base["provides"]))
    check("qwen3.5 capabilities are the ORDERED serve_ref set",
          base["capabilities"] == ["prefix_caching", "tools", "reasoning", "trust_remote_code"],
          detail=str(base["capabilities"]))
    check("qwen3.5 serve_params carries the qwen3_xml tool parser",
          base["serve_params"].get("tool_parser") == "qwen3_xml")
    check("qwen3.5 serve_params carries the qwen3 reasoning parser (the real reasoning fix)",
          base["serve_params"].get("reasoning_parser") == "qwen3")
    check("qwen3.5 serve_params NO LONGER carries the RETIRED nothink chat_template (shipping shape)",
          "chat_template" not in base["serve_params"])
    check("qwen3.5 fields default thinking=false (the no-think workers)",
          base["fields"].get("thinking") is False)
    # ⊕ overrides: a per-model override of a field wins; a serve_param override wins per key.
    merged = R.resolve_capabilities("qwen3.5", {
        "fields": {"thinking": True},
        "serve_params": {"tool_parser": "custom_parser"},
    })
    check("override thinking=True wins over the family default", merged["fields"]["thinking"] is True)
    check("the non-overridden field json_schema is still inherited", merged["fields"].get("json_schema") is True)
    check("override tool_parser wins per key", merged["serve_params"]["tool_parser"] == "custom_parser")
    check("the non-overridden serve_param reasoning_parser is still inherited",
          merged["serve_params"].get("reasoning_parser") == "qwen3")
    # a wholesale capability-list override replaces the family's list
    cap_ov = R.resolve_capabilities("qwen3.5", {"capabilities": ["trust_remote_code"]})
    check("a capability_overrides.capabilities list replaces the family list",
          cap_ov["capabilities"] == ["trust_remote_code"])
    try:
        R.resolve_capabilities("no-such-family")
        check("unknown family RAISES", False, detail="did NOT raise")
    except R.CapabilityResolutionError:
        check("unknown family RAISES (fail-loud, no silent default)", True)

    print("\n[2] serve_flags BYTE-REFERENCE — PARTITIONED per model (build-log 01-serving §D6)")
    # The byte-reference DIFFERS by model class (the flag-match proof must NOT conflate them):
    #   • embedders + nemotron + chat-4b-fp8 (the LIVE brain) → MUST reproduce their CURRENT flags exactly;
    #   • chat-4b/2b/08b (AWQ) → INTENDED CHANGE (shipping shape: nothink template dropped, --reasoning-parser
    #     added; Tim directed this). Their reference is the qwen3.5 shipping shape (= fp8 minus vision), NOT
    #     the old flags[]. So they are checked against the shipping shape, flagged as an intended change.
    # services.json no longer carries flags[] for migrated services (RETIRED) — the EXACT byte-references are
    # the literals the live services run / ran with (the prior flags[], git HEAD).
    QWEN_SHIPPING = ["--enable-prefix-caching", "--enable-auto-tool-choice", "--tool-call-parser",
                     "qwen3_xml", "--reasoning-parser", "qwen3", "--trust-remote-code"]
    EMBED_REF = ["--runner", "pooling", "--trust-remote-code"]
    NEMOTRON_REF = ["--quantization", "compressed-tensors", "--cpu-offload-gb", "6",
                    "--enforce-eager", "--trust-remote-code"]
    FP8_LIVE_REF = ["--enable-prefix-caching", "--enable-auto-tool-choice", "--tool-call-parser",
                    "qwen3_xml", "--reasoning-parser", "qwen3", "--language-model-only", "--trust-remote-code"]

    # SAFETY-CRITICAL: chat-4b-fp8 is the LIVE brain on :8001 — a restart MUST emit byte-identical flags.
    fp8 = R.serve_flags({"family": "qwen3.5", "capability_overrides": {"vision": "lm-only"}})
    check("LIVE-BRAIN chat-4b-fp8 {qwen3.5 + vision:lm-only} == its current flags BYTE-FOR-BYTE (restart-safe)",
          fp8 == FP8_LIVE_REF, detail=f"\n        gen={fp8}\n        exp={FP8_LIVE_REF}")

    # embedders MUST reproduce their current flags exactly (no intended change).
    for key in ("embed-bge", "embed-jina-v5", "embed-qwen3"):
        gen = R.serve_flags({"family": "embed-pooling"})
        check(f"{key} (family embed-pooling) == current flags BYTE-FOR-BYTE",
              gen == EMBED_REF, detail=str(gen))

    # nemotron MUST reproduce its current flags exactly (its own family).
    nem = R.serve_flags({"family": "nemotron"})
    check("chat-nemotron (family nemotron) == current flags BYTE-FOR-BYTE", nem == NEMOTRON_REF,
          detail=str(nem))

    # chat-4b/2b/08b — INTENDED CHANGE: the shipping shape (nothink dropped + --reasoning-parser added).
    chat = R.serve_flags({"family": "qwen3.5"})
    check("chat-4b/2b/08b (family qwen3.5) == the SHIPPING shape (INTENDED change: nothink dropped, "
          "--reasoning-parser qwen3 added; NOT the old flags[])", chat == QWEN_SHIPPING, detail=str(chat))
    check("the RETIRED nothink chat_template is NOT emitted by the shipping qwen3.5 family",
          "--chat-template" not in chat and not any("nothink" in t for t in chat))

    # extra_flags are appended verbatim AFTER the generated flags (the escape hatch)
    with_extra = R.serve_flags({"family": "embed-pooling", "stack": "vllm",
                                "extra_flags": ["--some-escape-hatch", "X"]})
    check("extra_flags are appended verbatim after the generated flags",
          with_extra[-2:] == ["--some-escape-hatch", "X"]
          and with_extra[:-2] == ["--runner", "pooling", "--trust-remote-code"],
          detail=str(with_extra))

    print("\n[2b] vision capability INJECTION via enum capability_override (the BUG 2 dissolution)")
    # vision:lm-only injects --language-model-only at order rank 40 (between reasoning 30 and trust 90).
    lm = R.serve_flags({"family": "qwen3.5", "capability_overrides": {"vision": "lm-only"}})
    check("vision:lm-only INJECTS --language-model-only between reasoning and trust_remote_code",
          lm.index("--language-model-only") == lm.index("--reasoning-parser") + 2
          and lm.index("--language-model-only") < lm.index("--trust-remote-code"), detail=str(lm))
    # vision:full = a declared NO-OP (vision tower loaded; NO flag) — must NOT emit --language-model-only.
    full = R.serve_flags({"family": "qwen3.5", "capability_overrides": {"vision": "full"}})
    check("vision:full emits NO flag (declared no-op — tower loaded, no --language-model-only)",
          "--language-model-only" not in full and full == QWEN_SHIPPING, detail=str(full))
    # an UNKNOWN enum value fails loud (never guesses a fragment).
    try:
        R.serve_flags({"family": "qwen3.5", "capability_overrides": {"vision": "bogus"}})
        check("an unknown vision enum value FAILS LOUD", False, detail="did NOT raise")
    except R.CapabilityResolutionError:
        check("an unknown vision enum value FAILS LOUD (never guesses a serve fragment)", True)
    # an override key naming NO capability-type row fails loud (registry-is-truth).
    try:
        R.serve_flags({"family": "qwen3.5", "capability_overrides": {"made_up_cap": True}})
        check("an override key with no capability-type row FAILS LOUD", False, detail="did NOT raise")
    except R.CapabilityResolutionError:
        check("an override key with no capability-type row FAILS LOUD (registry-is-truth)", True)

    print("\n[3] ADD-A-ROW = ONE row, NO code edit — a new FAMILY appears via reload_registries")
    # Build a temp family registry = live families + ONE net-new family. Reload FROM it.
    NEW_FAM = "test-chat-family"
    # re-read the canonical file so we serialize the full annotated form faithfully
    with open(os.path.join(_REPO, "runtime", "capabilities", "family_capabilities.json")) as f:
        fam_file = json.load(f)
    fam_file[NEW_FAM] = {
        "_note": "test-only family injected by capability_resolver_acceptance to prove add-a-row.",
        "stack": "vllm",
        "provides": ["chat", "json"],
        "capabilities": ["prefix_caching", "trust_remote_code"],
        "serve_params": {},
        "fields": {"tools": False},
    }
    tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    try:
        json.dump(fam_file, tmp); tmp.close()
        R.reload_registries(family_path=tmp.name)   # the seam: re-read the FILE into the live name
        check("the new family appears after a FILE add (no code edit)", NEW_FAM in R.FAMILIES)
        new_res = R.resolve_capabilities(NEW_FAM)
        check("resolve_capabilities sees the new family", new_res["provides"] == ["chat", "json"])
        new_flags = R.serve_flags({"family": NEW_FAM, "stack": "vllm"})
        check("serve_flags generates the new family's flags from registry data alone",
              new_flags == ["--enable-prefix-caching", "--trust-remote-code"], detail=str(new_flags))
        # _strip_annotations fired: the RAW file row carries _note, the RESOLVED output does NOT.
        check("the _note annotation is in the raw file row but stripped from the resolved output",
              "_note" in fam_file[NEW_FAM] and "_note" not in new_res)
    finally:
        os.unlink(tmp.name)
        R.reload_registries()                        # restore from canonical files (no residue)
    check("after restore, the temp family is GONE", NEW_FAM not in R.FAMILIES)
    check("after restore, the canonical families are all back",
          {"qwen3.5", "embed-pooling"} <= set(R.FAMILIES))

    print("\n[3b] ADD-A-ROW = ONE row — a new STACK appears + is usable, NO code edit")
    NEW_STACK = "test-stack"
    with open(os.path.join(_REPO, "runtime", "capabilities", "stack_capabilities.json")) as f:
        stack_file = json.load(f)
    stack_file[NEW_STACK] = {
        "_note": "test-only stack injected to prove add-a-stack.",
        "prefix_caching": {"serve": ["--ts-prefix-caching"], "use": None},
        "trust_remote_code": {"serve": ["--ts-trust"], "use": None},
    }
    tmp2 = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    try:
        json.dump(stack_file, tmp2); tmp2.close()
        R.reload_registries(stack_path=tmp2.name)
        check("the new stack appears after a FILE add (no code edit)", NEW_STACK in R.STACKS)
        ts_flags = R.serve_flags({
            "family": "qwen3.5", "stack": NEW_STACK,
            "capability_overrides": {"capabilities": ["prefix_caching", "trust_remote_code"]},
        })
        check("serve_flags uses the new stack's expression (new stack is usable, no code edit)",
              ts_flags == ["--ts-prefix-caching", "--ts-trust"], detail=str(ts_flags))
    finally:
        os.unlink(tmp2.name)
        R.reload_registries()
    check("after restore, the temp stack is GONE", NEW_STACK not in R.STACKS)

    print("\n[3c] ADD-A-ROW = ONE row — a new CAPABILITY-TYPE appears, NO code edit")
    NEW_CAP = "test_capability"
    with open(os.path.join(_REPO, "runtime", "capabilities", "capability_types.json")) as f:
        ctype_file = json.load(f)
    ctype_file[NEW_CAP] = {
        "_note": "test-only capability-type injected to prove add-a-capability.",
        "value_shape": "bool", "layer": "field", "declare": "test",
        "serve_ref": "test_capability", "use_ref": None, "verify": None,
        "on_unexpressible": "fail_loud",
    }
    tmp3 = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    try:
        json.dump(ctype_file, tmp3); tmp3.close()
        R.reload_registries(capability_types_path=tmp3.name)
        check("the new capability-type appears after a FILE add (no code edit)",
              NEW_CAP in R.CAPABILITY_TYPES)
        check("the new capability-type's serve_ref is readable from the registry",
              R.CAPABILITY_TYPES[NEW_CAP]["serve_ref"] == "test_capability")
    finally:
        os.unlink(tmp3.name)
        R.reload_registries()
    check("after restore, the temp capability-type is GONE", NEW_CAP not in R.CAPABILITY_TYPES)

    print("\n[4] FAIL-LOUD — missing/malformed/empty registry RAISES; unexpressible capability RAISES")
    try:
        R._load_json_registry("/no/such/registry.json", "test")
        check("missing registry RAISES", False, detail="did NOT raise")
    except R.CapabilityResolutionError:
        check("missing registry RAISES (fail-loud, no empty dict)", True)
    bad = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    bad.write("{ not json ")
    bad.close()
    try:
        R._load_json_registry(bad.name, "test")
        check("malformed registry RAISES", False, detail="did NOT raise")
    except R.CapabilityResolutionError:
        check("malformed registry RAISES (fail-loud)", True)
    finally:
        os.unlink(bad.name)
    empty = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    json.dump({"_doc": "only annotations, no rows"}, empty)
    empty.close()
    try:
        R._load_json_registry(empty.name, "test")
        check("a registry with NO rows RAISES", False, detail="did NOT raise")
    except R.CapabilityResolutionError:
        check("a registry with NO rows RAISES (fail-loud)", True)
    finally:
        os.unlink(empty.name)
    # on_unexpressible=fail_loud — a family owning a capability the stack can't express RAISES.
    # ollama has no `prefix_caching` entry; force a family on the ollama stack that owns it.
    try:
        R.serve_flags({"family": "qwen3.5", "stack": "ollama"})
        check("a stack that cannot express an owned capability RAISES", False, detail="did NOT raise")
    except R.CapabilityResolutionError:
        check("a stack that cannot express an owned capability RAISES (on_unexpressible=fail_loud)", True)
    # a custom-server model is NOT flag-generated — returns only extra_flags (escape hatch).
    cust = R.serve_flags({"family": "embed-pooling", "stack": "custom-server",
                          "capability_overrides": {"capabilities": ["embed"]}, "extra_flags": []})
    check("a custom-server model generates NO vLLM flags (bespoke-script launch)", cust == [],
          detail=str(cust))

    print("\n[5] THE REAL DELIVERABLE — serveconfig.args_for(key) over the MIGRATED services.json")
    # Proves BUG 1 is fixed end-to-end: every vLLM config service now resolves a full launch arg list
    # WITHOUT the loud-fail firing (it would raise SystemExit if a `family` were missing). This exercises
    # the actual shipping path (services.json -> serveconfig.args_for -> resolver), not in-memory decls.
    sys.path.insert(0, os.path.join(_REPO, "ops", "cli"))
    import serveconfig as SC
    EXPECTED_FLAGS = {
        # the post-runtime-param flag list each migrated service must emit (the byte-references, §D6)
        "chat-4b":       ["--enable-prefix-caching", "--enable-auto-tool-choice", "--tool-call-parser",
                          "qwen3_xml", "--reasoning-parser", "qwen3", "--trust-remote-code"],
        "chat-2b":       ["--enable-prefix-caching", "--enable-auto-tool-choice", "--tool-call-parser",
                          "qwen3_xml", "--reasoning-parser", "qwen3", "--trust-remote-code"],
        "chat-08b":      ["--enable-prefix-caching", "--enable-auto-tool-choice", "--tool-call-parser",
                          "qwen3_xml", "--reasoning-parser", "qwen3", "--trust-remote-code"],
        "chat-4b-fp8":   ["--enable-prefix-caching", "--enable-auto-tool-choice", "--tool-call-parser",
                          "qwen3_xml", "--reasoning-parser", "qwen3", "--language-model-only",
                          "--trust-remote-code"],
        "chat-nemotron": ["--quantization", "compressed-tensors", "--cpu-offload-gb", "6",
                          "--enforce-eager", "--trust-remote-code"],
        "embed-bge":     ["--runner", "pooling", "--trust-remote-code"],
        "embed-jina-v5": ["--runner", "pooling", "--trust-remote-code"],
        "embed-qwen3":   ["--runner", "pooling", "--trust-remote-code"],
    }
    for key in VLLM_CONFIG_SERVICES:
        try:
            args = SC.args_for(key)
        except SystemExit as e:
            check(f"serveconfig.args_for({key}) resolves WITHOUT loud-fail (BUG 1 fixed)", False,
                  detail=f"RAISED SystemExit: {e}")
            continue
        check(f"serveconfig.args_for({key}) resolves WITHOUT loud-fail (BUG 1 fixed)", True)
        # the trailing flags (after model/port/host/gpu-util/max-model-len/max-num-seqs) == the reference
        exp = EXPECTED_FLAGS[key]
        tail = args[len(args) - len(exp):]
        check(f"  {key} emits the expected migrated flags", tail == exp,
              detail=f"\n        tail={tail}\n        exp={exp}")
    # chat-4b's gpu_util is AUTO-ALLOCATED from its _profile (static literal removed) — never vLLM's 0.9.
    # ~0.45 = (5838 fixed + 31.7*16384/1024 KV + 1024 overhead) / 16376 ceiling. The overhead term is the
    # registry-global vram_overhead_mb, raised 512->1024 in C5 (2a04661) when the 9B measurement proved the
    # real non-weight/non-KV footprint of a near-card-filling model is ~900 MiB, not 512 — so this expected
    # value moved 0.4187->0.45 as the AUTO math corrected for ALL profiled models. The assertion still proves
    # the class (computed from _profile, NOT a static literal, NOT vLLM's 0.9 default).
    c4 = SC.args_for("chat-4b")
    gi = c4.index("--gpu-memory-utilization")
    check("chat-4b gpu_util is AUTO-ALLOCATED (~0.45 from _profile w/ 1024 overhead, not a static literal)",
          abs(float(c4[gi + 1]) - 0.45) < 0.01, detail=f"gpu_util={c4[gi + 1]}")

    print(f"\n=== {_passed} passed, {_failed} failed ===")
    sys.exit(1 if _failed else 0)


if __name__ == "__main__":
    main()
