"""introspection/adapters/cli_help.py - CliHelpDiscoverer (DiscoverySourceType 'cli-help').
LEVEL 1 (platform-agnostic) - Mirror-Registry System, LANE-INTROSPECTION-CORE.

Parses a Commander.js-style `<bin> --help` option table into CapabilityEntry rows (one per option
row). The PARSE RULE is generic - it knows the Commander option-row SHAPE (Dynamic Capability
Registry - Spec section 2.2), not any specific flag name. ZERO platform-name literals (F-FIX-10).

Commander option-row shape (Observed v2.1.177, the SHAPE the parser depends on):
    --flag-name <arg>          Description text, may wrap
    -x, --flag-name <arg>      Description (rows with a short alias)
    --flag-name <a|b|c>        (choices rendered inline)
    --flag-name <arg>          Description (default: x)

Parse contract: one entry per option row - a row whose first non-space content is '-' (short alias)
or '--' (long flag). Parse into {flag, alias, argName, argType, choices, default, description}. Tag
source='help-parse', visible=True. The id is f'flag/{name}' where name INCLUDES the '--' prefix
(F-FIX-14): id='flag/--debug', name='--debug', cap://flag/--debug resolves to CapabilityRegistry
.get('flag/--debug').

floor_guard (section 2.6): if the parse yields fewer than src.floor_guard rows, RAISE - a parse
that low means a format change or a wrong executable path, never a clean result. Fail loud.
"""
from __future__ import annotations
import re
import subprocess

from contracts.capability_entry import CapabilityEntry


# An option row STARTS (after leading whitespace) with a flag token: '-x' or '--long'.
# Group 1 = the option-spec column (flags + arg); the rest (>= 2 spaces gap) = description.
_OPTION_ROW = re.compile(r"^\s+(-{1,2}[A-Za-z0-9][^\s].*?)(?:\s{2,}(.*))?$")
# A single flag token inside the spec column: -x  or  --long-name
_FLAG_TOKEN = re.compile(r"^-{1,2}[A-Za-z0-9][A-Za-z0-9-]*$")
# default annotation in the description: (default: X)
_DEFAULT = re.compile(r"\(default:\s*([^)]*)\)")


class CliHelpDiscoverer:
    """Discovers capabilities from a CLI's `--help` option table. Stateless; the platform DATA
    (the DiscoverySource + the resolved executable) drives every value. Engine selects this adapter
    by DiscoverySource.type == 'cli-help'."""

    source_type = "cli-help"

    def discover(self, executable: str, src) -> str:
        """Run the discovery command (with {binary} substituted) and return the raw --help text.
        Honours src.stderr_merge (Commander often writes --help to stdout; some tools to stderr).
        Fail loud on a non-zero exit that yields no text. Does NOT parse - that is parse()."""
        cmd = [tok.replace("{binary}", executable) for tok in src.command]
        if not cmd:
            raise ValueError(f"cli-help discover: empty command for source {src.type!r} - the "
                             f"DiscoverySource.command must carry e.g. ['{{binary}}','--help']. Fail loud.")
        stderr_dest = subprocess.STDOUT if getattr(src, "stderr_merge", False) else subprocess.PIPE
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=stderr_dest, text=True,
                              timeout=getattr(src, "timeout_s", 15))
        raw = proc.stdout or ""
        if not raw.strip():
            raise RuntimeError(
                f"cli-help discover: command {cmd!r} produced NO output (rc={proc.returncode}) - "
                f"refusing to write an empty registry (fail-loud; the live surface answered nothing).")
        return raw

    def parse(self, raw: str, parse_rule: str = "option-row", *, platform_id: str = "",
              version: str = "") -> list[CapabilityEntry]:
        """Parse the raw --help text into CapabilityEntry rows. parse_rule selects the shape:
          'option-row'      — the flag/option table (one entry per flag; the Commander/Cobra/clap shape).
          'subcommand-list' — the 'Commands:'/'Available Commands:' section (one entry per subcommand) — so
                              "run any capability" covers subcommands, not just flags (2026-06-28). Generic
                              across CLI families (clap/cobra/commander all print an indented name+desc list).
        A novel shape is a new rule + branch, gap-surfaced — never silently mis-parsed."""
        if parse_rule == "subcommand-list":
            return self._parse_subcommands(raw, platform_id=platform_id, version=version)
        if parse_rule != "option-row":
            raise ValueError(f"cli-help parse: unknown parse_rule {parse_rule!r} - built rules are "
                             f"'option-row' (flag table) + 'subcommand-list' (Commands section). A novel "
                             f"shape is a new rule + branch, gap-surfaced. Fail loud.")
        entries: list[CapabilityEntry] = []
        seen: set[str] = set()
        for line in raw.splitlines():
            m = _OPTION_ROW.match(line)
            if not m:
                continue
            spec_col = m.group(1).strip()
            desc = (m.group(2) or "").strip()
            parsed = self._parse_spec_column(spec_col)
            if parsed is None:
                continue
            name, alias, arg_name, choices = parsed
            if name in seen:
                # description may wrap to following lines; first occurrence wins (we ignore wraps).
                continue
            seen.add(name)
            takes_value = bool(arg_name)
            default_value = None
            dm = _DEFAULT.search(desc)
            if dm:
                default_value = dm.group(1).strip()
            entry = CapabilityEntry(
                id=f"flag/{name}",
                kind="flag",
                name=name,                                # INCLUDES the '--' prefix (F-FIX-14)
                aliases=[alias] if alias else [],
                description=desc,
                takes_value=takes_value,
                value_type=self._arg_type(arg_name, choices),
                choices=choices,
                default_value=default_value,
                visible=True,
                source="help-parse",
                platform_id=platform_id or "",
                discovered_at=version,                    # the binary version the row was parsed from
            )
            entries.append(entry)
        return entries

    # the commands-section header — colon OPTIONAL: clap 'Commands:', cobra 'CORE COMMANDS' / 'GITHUB ACTIONS
    # COMMANDS' (no colon, may be upper), commander 'Commands:'. (re.I handles the case.)
    _CMD_SECTION = re.compile(r"^[A-Za-z ]*commands:?\s*$", re.I)
    # a subcommand row: indented, a name (no leading '-'), an OPTIONAL trailing colon (cobra 'auth:'),
    # >=2 spaces, then a description.
    _CMD_ROW = re.compile(r"^\s+([a-z][\w-]*):?\s{2,}(.*)$")
    _ALIASES = re.compile(r"\[alias(?:es)?:\s*([^\]]+)\]")

    def _parse_subcommands(self, raw: str, *, platform_id: str = "", version: str = "") -> list[CapabilityEntry]:
        """Parse the 'Commands:' section into one CapabilityEntry per subcommand (kind='subcommand').
        Walks rows under the section header until a dedent/blank/new-section. Captures [aliases: …]."""
        entries: list[CapabilityEntry] = []
        seen: set[str] = set()
        in_section = False
        for line in raw.splitlines():
            if self._CMD_SECTION.match(line):
                in_section = True
                continue
            if not in_section:
                continue
            if not line.strip():                                  # blank line ends the section
                in_section = False
                continue
            if not line[:1].isspace():                            # a non-indented line = a new section
                in_section = False
                continue
            m = self._CMD_ROW.match(line)
            if not m:
                continue
            name, desc = m.group(1).strip(), m.group(2).strip()
            if name in seen or name in ("help",):                 # skip the universal 'help' pseudo-command
                continue
            seen.add(name)
            aliases = []
            am = self._ALIASES.search(desc)
            if am:
                aliases = [a.strip() for a in am.group(1).split(",") if a.strip()]
                desc = self._ALIASES.sub("", desc).strip()
            entries.append(CapabilityEntry(
                id=f"subcommand/{name}", kind="subcommand", name=name, aliases=aliases,
                description=desc, visible=True, source="help-parse",
                platform_id=platform_id or "", discovered_at=version))
        return entries

    @staticmethod
    def _parse_spec_column(spec: str):
        """Parse the option-spec column into (name, alias, arg_name, choices). Returns None if the
        column is not an option spec (e.g. a section header). The spec is the comma-joined flag
        tokens + an optional <arg> / <a|b|c>. The LONG flag (--name) is the canonical name; a -x is
        the alias."""
        # split off the <arg> / [arg] portion (the value placeholder), keep the flag tokens.
        arg_name = ""
        choices: list[str] = []
        # value placeholder forms: <x>  [x]  <a|b|c>  <x...>
        am = re.search(r"[<\[]([^>\]]+)[>\]]", spec)
        flag_part = spec
        if am:
            arg_name = am.group(1).strip()
            flag_part = spec[:am.start()].strip()
            if "|" in arg_name:
                choices = [c.strip() for c in arg_name.split("|") if c.strip()]
        tokens = [t.strip() for t in flag_part.split(",") if t.strip()]
        flag_tokens = [t for t in tokens if _FLAG_TOKEN.match(t)]
        if not flag_tokens:
            return None
        long_flags = [t for t in flag_tokens if t.startswith("--")]
        short_flags = [t for t in flag_tokens if not t.startswith("--")]
        if long_flags:
            name = long_flags[0]
            alias = short_flags[0] if short_flags else ""
        else:
            # a short-only option (rare) - the short flag is the name, no long alias.
            name = short_flags[0]
            alias = ""
        return name, alias, arg_name, choices

    @staticmethod
    def _arg_type(arg_name: str, choices: list[str]) -> str:
        if not arg_name:
            return ""
        if choices:
            return "enum"
        low = arg_name.lower()
        if "..." in arg_name:
            return "csv"
        if any(k in low for k in ("path", "dir", "file")):
            return "path"
        if any(k in low for k in ("json",)):
            return "json"
        if any(k in low for k in ("n", "num", "count", "turns", "budget")):
            return "int"
        return "string"
