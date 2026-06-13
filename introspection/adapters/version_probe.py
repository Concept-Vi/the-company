"""introspection/adapters/version_probe.py - VersionProbe. LEVEL 1 (platform-agnostic).
Mirror-Registry System, LANE-INTROSPECTION-CORE.

Reads the running platform version via the VersionSource (section 2.7): run the command (with
{binary} substituted), strip the declared suffix, return the cleaned version string. The version is
the PRIMARY freshness key (REFRESH section 4.4 compares it to the .version_stamp). ZERO platform-name
literals (F-FIX-10) - the command + strip_suffix are platform DATA on the VersionSource.
"""
from __future__ import annotations
import subprocess


class VersionProbe:
    """Probe the running platform version from a VersionSource. Stateless; data-driven."""

    def probe(self, executable: str, version_source) -> str:
        """Run version_source.command (with {binary} -> executable), strip version_source.strip_suffix,
        return the cleaned string. Fail loud if the command yields nothing (a version probe that
        returns empty is a broken read, not 'no version')."""
        cmd = [tok.replace("{binary}", executable) for tok in version_source.command]
        if not cmd:
            raise ValueError("version-probe: empty VersionSource.command - cannot read the running "
                             "version. Fail loud.")
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                              timeout=getattr(version_source, "timeout_s", 15))
        out = (proc.stdout or "").strip()
        if not out:
            raise RuntimeError(f"version-probe: command {cmd!r} produced NO version output "
                               f"(rc={proc.returncode}). Fail loud - never a fabricated version.")
        suffix = getattr(version_source, "strip_suffix", "")
        if suffix and out.endswith(suffix):
            out = out[: -len(suffix)].strip()
        elif suffix and suffix in out:
            out = out.replace(suffix, "").strip()
        # take the first whitespace-delimited token if the line carries extra words after stripping.
        return out.split()[0] if out.split() else out
