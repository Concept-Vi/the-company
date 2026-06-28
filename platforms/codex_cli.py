"""platforms/codex_cli.py — OpenAI Codex CLI (`codex`) as INSTANCE #3 of the Mirror-Registry System.
Mirror-Registry System, LANE-INTROSPECTION-CORE / C-GENPROOF (the lift, applied a third time).

THE LIFT, A THIRD TIME — and the first instance with a LIVE in-fabric CONSUMER. Where instance #2
(`gh_cli.py`) proved a 2nd known-kind CLI is "almost free" but is registered-only (nothing drives it
yet), `codex` is registered AND already used: the ledger interpretive layer drives `codex exec` as a
producer (ops/ledger_interpret_codex.py) on the OpenAI/ChatGPT token pool, off the Claude limit. So
this row both extends the proof and wires a real platform the Company actively invokes.

PURE DATA (ROW-PURITY): imports + ONE `PLATFORM = {...}` dict, NO def/class — the gh_cli.py template
shape. Reuses the EXISTING cli-help adapter (DiscoverySource.type == "cli-help") with ZERO edits to
introspection/engine.py / rules.py / discover.py / adapters/. The engine never learns `codex` exists.

WHY `codex` strengthens the proof (verified by use, not assumed, 2026-06-28):
  - `codex` is a RUST/clap CLI — a THIRD tool family (instance #1 = Commander.js, #2 = Cobra). Its
    `codex exec --help` emits an "Options:" block whose flag tokens are the SAME option-row SHAPE the
    generic parser keys on (`-c, --config <key=value>` / `-o, --output-last-message <FILE>`). 24 option
    rows observed → floor_guard=12 (a parse regression / wrong binary fails loud, never a partial).
  - KNOWN QUIRK (a recorded gap, NOT a blocker — see build-prep/the-one-system/REGISTRY-NOTES.md):
    clap prints each flag's DESCRIPTION on the NEXT indented line, while the cli-help parser's
    `_OPTION_ROW` regex expects the description on the SAME line (>=2-space gap). So flags DISCOVER
    correctly (the flag token matches) but their `description` comes back EMPTY. This does NOT affect
    CLASSIFY — R1-R5 key off the flag NAME + the declared signal_sets, and R2 hazard is flag_name_only
    by law. A future `clap-options` parse_rule (or a continuation-line join in cli_help.py) would
    recover descriptions; until a 2nd clap platform needs it, the gap is surfaced, not papered.

WHAT THIS PLATFORM DOES NOT NEED (like gh, unlike claude-code): `codex` is invoked-and-exits in fabric
use (`codex exec -o <file> -`), not a held-open injected session. So NO consumer_reserved_invariants
body-key machinery, NO stream-init source, NO held-open state machine. No head_builder thunk is wired,
so its DECLARED `transport_invariants` IS the engine-validated R1 input (PlatformRegistry only overwrites
when a thunk exists). (Codex CAN run as an MCP server / held agent — `codex mcp-server` — but the Company
does not drive it that way today; if it later does, that is a stream-init/held-session extension, a new
discovery_source on this same row, surfaced when built.)
"""
from __future__ import annotations


PLATFORM = {
    "id": "codex-cli",
    "display_name": "OpenAI Codex CLI (codex)",

    # executable-locator — env override → PATH → known path (the generic ExecutableLocator)
    "executable_locator": {
        "name": "codex", "env_override": "COMPANY_CODEX_BIN",
        "which_fallback": True,
        "known_paths": ["/home/linuxbrew/.linuxbrew/bin/codex", "~/.local/bin/codex", "/usr/local/bin/codex"],
    },

    # invocation kind — the SAME built SubprocessAdapter as instances #1 and #2
    "invocation_kind": "subprocess",

    # discovery-source — the EXISTING cli-help adapter, ZERO edits. `codex exec --help` emits a clap
    # "Options:" table whose flag tokens the generic option-row parser reads (descriptions land on the
    # next line → empty, per the recorded quirk above; flags + classification are unaffected).
    "discovery_sources": [
        {"type": "cli-help",
         "command": ["{binary}", "exec", "--help"],
         "stderr_merge": True,
         "format": "commander-options-text",
         "parse_rule": "option-row",
         "floor_guard": 12},
        # subcommand surface (so "run any capability" covers subcommands: exec/mcp/login/…, not just flags)
        {"type": "cli-help",
         "command": ["{binary}", "--help"],
         "stderr_merge": True,
         "format": "commander-options-text",
         "parse_rule": "subcommand-list",
         "floor_guard": 3},
    ],

    # version-source — `codex --version` → "codex-cli 0.142.3"; strip the "codex-cli " prefix-substring,
    # then the probe takes the first remaining token → "0.142.3".
    "version_source": {"command": ["{binary}", "--version"], "strip_suffix": "codex-cli ",
                       "format": "semver-token"},

    # signal-sets — the CLASSIFY inputs, declared as DATA from codex's REAL flags (observed, not invented):
    #   R1 transport_invariants: the machine-output / non-interactive guards the fabric emits when it
    #     drives `codex exec` as a producer (DECLARED — codex is invoked, not held-open, no spawn head).
    #   R2 hazard_name_vocabulary: codex's danger naming (flag-NAME scope ONLY) — catches both
    #     `--dangerously-bypass-approvals-and-sandbox` and `--dangerously-bypass-hook-trust`.
    #   R3 capability_axes: where a codex flag widens the session surface (model, sandbox, dirs/cwd,
    #     provider, image input, config). `--add-dir`/`--cd` ride the `dirs` axis exactly as claude-code's
    #     `--add-dir` does (directory widening → CONSENT, not a transport lock).
    "signal_sets": {
        "transport_invariants_derived_from": "declared (codex is invoked exec-and-exit — no held-open spawn head)",
        "transport_invariants": ["--output-last-message", "--output-schema", "--json", "--skip-git-repo-check"],
        "hazard_name_vocabulary": ["dangerously", "bypass"],
        "hazard_scope": "flag_name_only",
        "capability_axes": {
            "model": ["-m", "--model"],
            "sandbox": ["-s", "--sandbox"],
            "dirs": ["--add-dir", "-C", "--cd"],
            "provider": ["--oss", "--local-provider"],
            "image-input": ["-i", "--image"],
            "config": ["-c", "--config"],
        },
    },

    # projection-targets — the faces this platform projects to (same closed set as instances #1 and #2)
    "projection_targets": ["capabilities_key", "resolver"],
}

# ROW-PURITY (2026-06-28). PURE DATA — imports + the one `PLATFORM = {...}` dict, NO def/class. Instance
# #3 copies the gh_cli.py template and reuses the cli-help adapter with ZERO engine/adapter edits. The
# engine dispatches on DiscoverySource.type == "cli-help" (a stable selector), never on `codex`'s identity.
