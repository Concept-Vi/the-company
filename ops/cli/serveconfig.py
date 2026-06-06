#!/usr/bin/env python3
"""serveconfig — emit the vLLM CLI args for a service's `config` block.

Used by ../serve_model.sh (the generic, registry-driven launcher). Prints one arg
per line so the launcher reads them safely (paths may contain spaces). The point:
a model's serve settings are DATA in services.json (editable via `company config`),
not flags hardcoded in a per-model shell script. stdlib-only."""
import os, sys, json

OPS = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


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


def args_for(key):
    c = _config(key)
    a = [c["model"], "--port", str(c["port"]),
         "--host", c.get("host", "0.0.0.0"),
         "--gpu-memory-utilization", str(c["gpu_util"])]
    if c.get("max_model_len"):
        a += ["--max-model-len", str(c["max_model_len"])]
    if c.get("max_num_seqs"):
        a += ["--max-num-seqs", str(c["max_num_seqs"])]
    for f in c.get("flags", []):
        a.append(os.path.expanduser(f) if isinstance(f, str) and f.startswith("~") else str(f))
    return a


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: serveconfig.py <service-key> [--env]")
    if "--env" in sys.argv[2:]:
        print(env_for(sys.argv[1]))
    else:
        print("\n".join(args_for(sys.argv[1])))
