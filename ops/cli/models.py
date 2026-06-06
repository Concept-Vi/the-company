"""models — model inventory + swap. stdlib-only.

`inventory()` lists what's on disk (HF cache for vLLM/transformers + Ollama's own
store). `swap()` is generic over the registry: it rewrites the `MODEL="${1:-...}"`
default in a service's `serve` script and restarts the unit — works for any model
service whose serve script uses that pattern; refuses cleanly otherwise."""
import os, re, subprocess
import registry
from registry import serve_script
from systemd import control

HUB = os.path.expanduser("~/.cache/huggingface/hub")
_MODEL_RE = re.compile(r'MODEL="\$\{1:-[^"]*\}"')


def inventory():
    lines = ["  Models in HF cache (vLLM / transformers read these):"]
    if os.path.isdir(HUB):
        for d in sorted(os.listdir(HUB)):
            if not d.startswith("models--"):
                continue
            full = os.path.join(HUB, d)
            name = d.replace("models--", "").replace("--", "/")
            sz = subprocess.run(["du", "-sh", full], capture_output=True, text=True).stdout.split("\t")[0]
            lines.append(f"    {sz:>7}  {name}")
    lines.append("")
    lines.append("  Models in Ollama (the GGUF runtime serves these):")
    r = subprocess.run(["ollama", "list"], capture_output=True, text=True)
    for line in r.stdout.splitlines()[1:]:
        p = line.split()
        if p:
            lines.append(f"    {p[0]:<38}{''.join(p[2:4]) if len(p) > 3 else ''}")
    return "\n".join(lines)


def swap(reg, key, model_id):
    """Returns (ok, message). Stops the unit, rewrites the serve-script default, restarts."""
    svcs = reg["services"]
    if key not in svcs:
        return False, f"unknown service {key!r}"
    svc = svcs[key]
    if svc["manage"]["type"] != "user-unit":
        return False, f"{key} is not a user-unit — swap only handles vLLM user units."
    # Config-driven service: set config.model in the registry, save, restart.
    if svc.get("config"):
        svc["config"]["model"] = model_id
        registry.save(reg)
        control(svc, "stop")
        ok, msg = control(svc, "start")
        return ok, (f"config.model → {model_id}; restarted "
                    f"({'ok' if ok else 'start failed: ' + msg}). Tail: company logs {key} -f")
    # Legacy script-based service: rewrite the serve script's MODEL default.
    path = serve_script(svc)
    if not path:
        return False, f"{key} has no `serve` script in the registry — swap not supported."
    if not os.path.exists(path):
        return False, f"serve script not found: {path}"
    if svc["manage"]["type"] != "user-unit":
        return False, f"{key} is not a user-unit — swap only handles vLLM user units."
    text = open(path).read()
    new_text, n = _MODEL_RE.subn(f'MODEL="${{1:-{model_id}}}"', text)
    if n == 0:
        return False, (f'no `MODEL="${{1:-...}}"` line in {os.path.basename(path)} — '
                       f"swap aborted (script unchanged, service untouched).")
    control(svc, "stop")
    open(path, "w").write(new_text)
    ok, msg = control(svc, "start")
    return ok, (f"{os.path.basename(path)} → {model_id}; restarted "
                f"({'ok' if ok else 'start failed: ' + msg}). Cold start can take 30 s–3 min; "
                f"tail with `company logs {key} -f`.")
