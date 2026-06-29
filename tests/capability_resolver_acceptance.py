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

# The would-be-migrated FAMILY for each config-driven service (the LIVE phase would add
# `config.family` to services.json; here we declare the mapping in memory for the proof).
# qwen3.5 = the three Qwen3.5 chat workers; embed-pooling = the three vLLM pooling embedders.
SERVICE_FAMILY = {
    "chat-4b": "qwen3.5",
    "chat-2b": "qwen3.5",
    "chat-08b": "qwen3.5",
    "embed-bge": "embed-pooling",
    "embed-jina-v5": "embed-pooling",
    "embed-qwen3": "embed-pooling",
}

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
    check("the non-overridden serve_param chat_template is still inherited",
          merged["serve_params"].get("chat_template") == "~/vllm-tests/chat_template_nothink.jinja")
    # a wholesale capability-list override replaces the family's list
    cap_ov = R.resolve_capabilities("qwen3.5", {"capabilities": ["trust_remote_code"]})
    check("a capability_overrides.capabilities list replaces the family list",
          cap_ov["capabilities"] == ["trust_remote_code"])
    try:
        R.resolve_capabilities("no-such-family")
        check("unknown family RAISES", False, detail="did NOT raise")
    except R.CapabilityResolutionError:
        check("unknown family RAISES (fail-loud, no silent default)", True)

    print("\n[2] serve_flags REPRODUCES the current launch flags BYTE-FOR-BYTE (services.json = ground truth)")
    for key, family in SERVICE_FAMILY.items():
        cfg = (svcs[key].get("config") or {})
        expected = cfg["flags"]                      # the ground truth — read from services.json
        migrated = {"family": family, "stack": "vllm", "extra_flags": []}
        generated = R.serve_flags(migrated)
        check(f"serve_flags({key}) == services.json config.flags (verbatim)",
              generated == expected, detail=f"\n        gen={generated}\n        exp={expected}")
    # the `~`-path is emitted VERBATIM (literal `~`), matching flags[] cleanly
    chat = R.serve_flags({"family": "qwen3.5", "stack": "vllm"})
    check("the chat-template path is emitted with a LITERAL ~ (matches flags[]; args_for expands at launch)",
          "~/vllm-tests/chat_template_nothink.jinja" in chat)
    # extra_flags are appended verbatim AFTER the generated flags (the escape hatch)
    with_extra = R.serve_flags({"family": "embed-pooling", "stack": "vllm",
                                "extra_flags": ["--some-escape-hatch", "X"]})
    check("extra_flags are appended verbatim after the generated flags",
          with_extra[-2:] == ["--some-escape-hatch", "X"]
          and with_extra[:-2] == ["--runner", "pooling", "--trust-remote-code"],
          detail=str(with_extra))

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

    print(f"\n=== {_passed} passed, {_failed} failed ===")
    sys.exit(1 if _failed else 0)


if __name__ == "__main__":
    main()
