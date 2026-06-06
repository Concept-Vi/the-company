"""bench — run a stack benchmark via the vLLM venv. stdlib-only.

Folded in from the old `vllm-stack`. The bench scripts live in ~/vllm-tests and
need that venv's python (they import its deps); the chat/embed server must be up."""
import os, subprocess

VLLM_PY = os.path.expanduser("~/vllm-env/bin/python")
VLLM_TESTS = os.path.expanduser("~/vllm-tests")
SCRIPTS = {"chat": "bench.py", "embed": "bench_embed.py",
           "suite": "bench_suite.py", "long-ctx": "bench_long_ctx.py"}


def run(args):
    """args[0] = kind; rest forwarded to the bench script. Returns (ok, message)."""
    if not args or args[0] not in SCRIPTS:
        return False, f"usage: company bench <{'|'.join(SCRIPTS)}> [args]"
    if not os.path.exists(VLLM_PY):
        return False, f"vLLM venv python not found: {VLLM_PY}"
    script = os.path.join(VLLM_TESTS, SCRIPTS[args[0]])
    if not os.path.exists(script):
        return False, f"bench script not found: {script}"
    subprocess.run([VLLM_PY, script] + args[1:])
    return True, ""
