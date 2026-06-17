"""tests/brain_env_acceptance.py — the loadable-brain subprocess runs LEAST-PRIVILEGE (fork, 2026-06-17).

Locks the security mitigation from the vi-vision creds flag: the company process gains a Supabase credential
(for the factory asset resolver), and run_turn spawns the `claude -p` brain via subprocess.Popen — which
INHERITS the parent env by default. The brain reaches the factory/company state via the company MCP tools +
resolve_address (which run in the COMPANY process), NEVER by querying the store itself — so it must NOT see
the store/factory secrets. This asserts _brain_env() strips them while keeping everything claude needs.

  LEAST-PRIVILEGE: the brain subprocess env excludes SUPABASE_*/VI_VISION_* (the store/factory secrets) …
  NON-BREAKING: … but keeps PATH/HOME/ANTHROPIC_* (what claude -p needs) — a DENYLIST, not an allowlist, so
    it can never accidentally strip what the brain needs.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from runtime.ui_claude_session import _brain_env, _BRAIN_ENV_DENY_PREFIXES

PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


# Seed FAKE values (this process only) — the flagged threat vars + the must-keep vars.
os.environ["SUPABASE_SERVICE_KEY"] = "FAKE-full-access-key"
os.environ["SUPABASE_URL"] = "FAKE-url"
os.environ["SUPABASE_ANON_KEY"] = "FAKE-anon"
os.environ["VI_VISION_SUPABASE_KEY"] = "FAKE"
os.environ["VI_VISION_RESOLVE_URL"] = "FAKE"
os.environ.setdefault("ANTHROPIC_API_KEY", "FAKE-anthropic")
os.environ.setdefault("PATH", "/usr/bin")
os.environ.setdefault("HOME", "/home/tim")

env = _brain_env()

print("[LP] LEAST-PRIVILEGE — the store/factory secrets are stripped from the brain subprocess env")
check("SUPABASE_SERVICE_KEY (full-access cred) is NOT in the brain env (the flagged threat)",
      "SUPABASE_SERVICE_KEY" not in env)
check("SUPABASE_URL / SUPABASE_ANON_KEY stripped",
      "SUPABASE_URL" not in env and "SUPABASE_ANON_KEY" not in env)
check("VI_VISION_* (factory transport vars) stripped",
      "VI_VISION_SUPABASE_KEY" not in env and "VI_VISION_RESOLVE_URL" not in env)
check("NO var under any deny-prefix leaks into the brain env",
      not any(k.startswith(_BRAIN_ENV_DENY_PREFIXES) for k in env))

print("\n[NB] NON-BREAKING — claude -p keeps the env it needs (denylist, not allowlist)")
check("ANTHROPIC_API_KEY KEPT (the brain's own auth — stripping it would break the brain)",
      env.get("ANTHROPIC_API_KEY") == "FAKE-anthropic")
check("PATH + HOME kept (claude needs them to run + read its config)",
      "PATH" in env and "HOME" in env)
check("the brain env is the parent env MINUS only the deny-prefixed vars (nothing else dropped)",
      set(env) == {k for k in os.environ if not k.startswith(_BRAIN_ENV_DENY_PREFIXES)})

print(f"\nALL {PASS} CHECKS PASS — the loadable-brain subprocess runs least-privilege: store/factory "
      f"secrets stripped, claude's env intact (defense-in-depth for the vi-vision Supabase cred).")
