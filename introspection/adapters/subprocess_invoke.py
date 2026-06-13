"""introspection/adapters/subprocess_invoke.py - SubprocessAdapter (InvocationKind 'subprocess').
LEVEL 1 (platform-agnostic) - Mirror-Registry System, LANE-INTROSPECTION-CORE.

The closed-set invocation adapter for subprocess platforms: locate the executable, run a command,
capture stdout/stderr. The DISCOVER-time read primitive the discoverers (cli-help, stream-init) and
the version probe sit on - one place that knows how to actually invoke a subprocess platform, so a
discoverer carries the PARSE rule and this carries the INVOKE mechanism. ZERO platform-name literals
(F-FIX-10).

The LIVE held-open session invocation (Popen + stdin NDJSON injection + the stream reader) is the
SessionSupervisor's job today - this adapter is the DISCOVER-side subprocess primitive (run-to-
completion or run-with-timeout capture), the piece the engine's DISCOVER step needs. The held-open
binding (invocation_binding section 2.8) is consumed by the supervisor (LANE-SUPERVISOR-REFACTOR),
not re-implemented here.
"""
from __future__ import annotations
import shutil
import os
import subprocess


class SubprocessAdapter:
    """Subprocess invocation primitive. Stateless; data-driven by the ExecutableLocator + command."""

    invocation_kind = "subprocess"

    def find_executable(self, locator) -> str:
        """Resolve the platform's entry-point: env_override -> PATH (which) -> known_paths. FAIL LOUD
        if none found - never silently absent (section 2.1a). Returns the resolved path/name."""
        # 1. env override
        env_var = getattr(locator, "env_override", "")
        if env_var:
            val = os.environ.get(env_var)
            if val:
                return val
        name = getattr(locator, "name", "")
        # 2. PATH probe
        if getattr(locator, "which_fallback", True) and name:
            found = shutil.which(name)
            if found:
                return found
        # 3. known paths
        for p in getattr(locator, "known_paths", []) or []:
            expanded = os.path.expanduser(p)
            if os.path.exists(expanded):
                return expanded
        raise RuntimeError(
            f"subprocess find_executable: could not locate executable {name!r} - tried "
            f"env[{env_var!r}], PATH (which={'on' if getattr(locator,'which_fallback',True) else 'off'}), "
            f"known_paths={getattr(locator,'known_paths',[])}. Fail loud - never assume a path.")

    def run_capture(self, cmd: list[str], *, stderr_merge: bool = False, timeout_s: int = 15,
                    stdin: str | None = None) -> "subprocess.CompletedProcess":
        """Run a command to completion and capture output. The generic capture used by the
        discoverers/version probe. Fail-loud semantics are the CALLER's (a discoverer decides whether
        empty output is fatal) - this just invokes."""
        stderr_dest = subprocess.STDOUT if stderr_merge else subprocess.PIPE
        return subprocess.run(cmd, input=stdin, stdout=subprocess.PIPE, stderr=stderr_dest,
                              text=True, timeout=timeout_s)
