"""platforms/gh_cli.py — GitHub CLI (`gh`) as INSTANCE #2 of the Mirror-Registry System.
Mirror-Registry System, LANE-INTROSPECTION-CORE / C-GENPROOF (THE LIFT GATE).

THE GENERALIZATION-PROOF IN ONE FILE. This is the second platform — registered to PROVE the lift is
real: a second platform of a KNOWN kind (a CLI that emits a `--help` option table) is "almost free" —
it is PURE DATA, imports + ONE `PLATFORM = {...}` dict, NO def/class (ROW-PURITY, mirroring the now-
clean platforms/claude_code.py template). It reuses the EXISTING cli-help adapter
(introspection/adapters/cli_help.py:CliHelpDiscoverer) with ZERO edits to introspection/engine.py /
rules.py / discover.py / adapters/. The engine never learns `gh` exists — it dispatches on the STABLE
selector DiscoverySource.type == "cli-help" and parses whatever option-row table the binary emits.

WHY `gh` (the real second CLI chosen, 2026-06-14 — verified by use, not assumed):
  - `gh` is a COBRA-style CLI, a DIFFERENT tool family from Claude Code's Commander.js help — yet its
    `<cmd> --help` FLAGS section is the SAME option-row SHAPE the generic parser depends on
    (`-a, --assignee login   Description` / bare `--dry-run   Description`). Proving the lift against a
    genuinely different tool family (not a hand-made stub) is the stronger proof.
  - The discovery command is `gh pr create --help` (NOT bare `gh --help`): bare `gh --help` is a
    command-LIST + a 2-flag FLAGS block (parser yields 2 rows — below a meaningful floor); the
    per-subcommand help carries a real 21-row option table. (Lead-verified 2026-06-14: bare git
    `--help` yields 0 rows — a usage block, no option-row table — which is exactly why `gh pr create
    --help` was chosen: a real, substantial Commander-shape option table reachable with zero parser
    edits.) floor_guard=10 so a parse regression / wrong binary fails loud, never a partial registry.

WHAT THIS PLATFORM DOES NOT NEED (and why the row is so much smaller than claude_code.py): `gh` is NOT
driven as a held-open injected session by the fabric — it is invoked, it runs, it exits. So there is
NO consumer_reserved_invariants body-key machinery, NO stream-init discovery source, NO held-open
state machine. The engine demands a NON-EMPTY R1 (transport_invariants) input or it RAISES (an empty
R1 silently demotes locked flags — forbidden); `gh` declares its OWN small genuine fabric-lock set +
hazard vocabulary + capability axes below, so CLASSIFY produces real R1/R2/R3/R5 postures over the
discovered flags. A platform with no head_builder thunk keeps its DECLARED transport_invariants as the
engine-validated R1 input (PlatformRegistry._derive_invariants only overwrites when a thunk is wired —
none is wired here, by design: `gh` has no held-open spawn head).
"""
from __future__ import annotations


PLATFORM = {
    "id": "gh-cli",
    "display_name": "GitHub CLI (gh)",

    # executable-locator — env override → PATH → known path (the generic ExecutableLocator)
    "executable_locator": {
        "name": "gh", "env_override": "COMPANY_GH_BIN",
        "which_fallback": True, "known_paths": ["/usr/bin/gh", "~/.local/bin/gh"],
    },

    # invocation kind — selects SubprocessAdapter (the SAME built invoker as instance #1)
    "invocation_kind": "subprocess",

    # discovery-source — the EXISTING cli-help adapter, ZERO edits. `gh pr create --help` emits a
    # cobra FLAGS option table the generic Commander-shape parser reads unchanged.
    "discovery_sources": [
        {"type": "cli-help",
         "command": ["{binary}", "pr", "create", "--help"],
         "stderr_merge": True,
         "format": "commander-options-text",
         "parse_rule": "option-row",
         "floor_guard": 10},
    ],

    # version-source — `gh --version` → "gh version 2.74.1 (2025-06-10)"; strip the "gh version "
    # prefix-as-substring, then the probe takes the first remaining token → "2.74.1".
    "version_source": {"command": ["{binary}", "--version"], "strip_suffix": "gh version ",
                       "format": "semver-token"},

    # signal-sets — the CLASSIFY inputs (gh's OWN small genuine sets, declared as DATA):
    #   R1 transport_invariants: the flags the fabric would lock if it drove `gh` non-interactively
    #     (machine-readable output + non-interactive guards). DECLARED (no head_builder thunk —
    #     `gh` has no held-open spawn head), so this list IS the engine-validated R1 input.
    #   R2 hazard_name_vocabulary: gh's own danger naming (flag-NAME scope ONLY).
    #   R3 capability_axes: where a gh flag widens the session surface (repo target, web/browser).
    "signal_sets": {
        "transport_invariants_derived_from": "declared (gh is invoked, not held-open — no spawn head)",
        "transport_invariants": ["--json", "--jq", "--template", "--no-color"],
        "hazard_name_vocabulary": ["force", "delete", "yes", "confirm"],
        "hazard_scope": "flag_name_only",
        "capability_axes": {
            "repo-target": ["--repo", "-R"],
            "browser": ["--web", "-w"],
        },
    },

    # projection-targets — the faces this platform projects to (same closed set as instance #1)
    "projection_targets": ["capabilities_key", "resolver"],
}

# ROW-PURITY (2026-06-14). This file is PURE DATA — imports + the one `PLATFORM = {...}` dict, NO
# def/class. It is the generalization-proof made concrete: a second platform of a known kind copies the
# claude_code.py template shape and reuses the cli-help adapter with ZERO engine/adapter edits. The
# engine dispatches on DiscoverySource.type == "cli-help" (a stable selector), never on `gh`'s identity.
