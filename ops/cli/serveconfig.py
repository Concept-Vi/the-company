#!/usr/bin/env python3
"""serveconfig — emit the vLLM CLI args for a service's `config` block.

Used by ../serve_model.sh (the generic, registry-driven launcher). Prints one arg
per line so the launcher reads them safely (paths may contain spaces). The point:
a model's serve settings are DATA in services.json (editable via `company config`),
not flags hardcoded in a per-model shell script. stdlib-only."""
import os, sys, json

OPS = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
_REPO = os.path.dirname(OPS)                       # repo root, so `runtime.capabilities` imports
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
if os.path.dirname(os.path.realpath(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))   # so `import gpu`/`registry` resolve


def _config(key):
    reg = json.load(open(os.path.join(OPS, "services.json")))
    svc = reg["services"].get(key)
    if not svc:
        raise SystemExit(f"serveconfig: unknown service {key!r}")
    c = svc.get("config")
    if not c:
        raise SystemExit(f"serveconfig: {key!r} has no `config` block "
                         f"(legacy script-based service — see cli/UPDATING.md)")
    return c


def env_for(key):
    """Per-service env vars (config.env) — as KEY=VALUE lines for the launcher to export.
    Each serve script set its own env; capturing it here keeps migration faithful."""
    return "\n".join(f"{k}={v}" for k, v in _config(key).get("env", {}).items())


def _resolved_gpu_util(key, c):
    """The --gpu-memory-utilization fraction to emit, in priority (build-log 01-serving §D3):
      1. explicit config.gpu_util  — the EXPLICIT OVERRIDE escape-hatch (a hand-set static value wins);
      2. auto_gpu_util(reg,key)     — COMPUTED from the measured _profile footprint + KV + overhead
                                      (the dissolution of the static-allocation class — the default path);
    No fallback: a config-driven model that yields NEITHER (no static gpu_util AND no _profile to compute
    from) FAILS LOUD — never lets vLLM apply its 0.9 default and grab the whole card (NO-fallback law)."""
    if c.get("gpu_util"):
        return c["gpu_util"]                       # explicit static override (authoritative)
    import registry, gpu                            # stdlib-only modules, importable before vllm-env activate
    auto = gpu.auto_gpu_util(registry.load(), key)
    if auto is not None:
        return round(auto, 4)
    raise SystemExit(
        f"serveconfig: {key!r} has no `gpu_util` AND no `_profile` to auto-allocate from — cannot resolve a "
        f"GPU memory fraction. FAIL LOUD (no fallback to vLLM's 0.9 default, which would grab the whole "
        f"card). Either declare a `_profile` (config.fixed_mb/kv_kb_per_token) to auto-size, or set an "
        f"explicit static `gpu_util` override.")


def _resolved_flags(key, c):
    """The post-runtime-param launch FLAGS, GENERATED from the model's capability DECLARATION via the
    resolver (build-log 01-serving §D1/D2; CAPABILITY-WIRING-MAP.md (a)). RETIRES the hand-authored
    `flags[]`: a config-driven vLLM model declares `family` (+ optional `stack`/`capability_overrides`/
    `extra_flags`) and the resolver emits the flag list. NO `flags[]` fallback — a config model that
    cannot resolve a family FAILS LOUD (forces it to be declared; registry-is-truth)."""
    from runtime.capabilities import resolver
    if not c.get("family"):
        raise SystemExit(
            f"serveconfig: {key!r} has no `family` declaration — cannot generate launch flags. FAIL LOUD "
            f"(the hand-authored `flags[]` path is RETIRED; no fallback). Migrate it to a declaration "
            f"({{family, stack?, capability_overrides?, extra_flags?}}) so the resolver generates its "
            f"flags from registry data (registry-is-truth). Known families: see "
            f"runtime/capabilities/family_capabilities.json.")
    decl = {"family": c["family"]}
    for opt in ("stack", "capability_overrides", "extra_flags"):
        if opt in c:
            decl[opt] = c[opt]
    flags = resolver.serve_flags(decl)
    # the resolver emits ~-paths VERBATIM (literal ~); expand them exactly as the old flags[] path did.
    return [os.path.expanduser(f) if isinstance(f, str) and f.startswith("~") else str(f) for f in flags]


def args_for(key):
    c = _config(key)
    a = [c["model"], "--port", str(c["port"]),
         "--host", c.get("host", "0.0.0.0"),
         "--gpu-memory-utilization", str(_resolved_gpu_util(key, c))]
    if c.get("max_model_len"):
        a += ["--max-model-len", str(c["max_model_len"])]
    if c.get("max_num_seqs"):
        a += ["--max-num-seqs", str(c["max_num_seqs"])]
    a += _resolved_flags(key, c)
    return a


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: serveconfig.py <service-key> [--env]")
    if "--env" in sys.argv[2:]:
        print(env_for(sys.argv[1]))
    else:
        print("\n".join(args_for(sys.argv[1])))
