# Source-registry (Mirror-Registry / platforms) — intention, integration map, and gaps-into-scope

*Written while adding the Codex CLI as platform instance #3. Per Tim's develop-as-you-go method: anything
noticed (gaps, missing wirings, unintuitive parts) is recorded here and folded into scope — noticing ≈ in-use.*

## What the source registry IS (intention, as built)
The **Mirror-Registry System** — the Company mirroring external platforms (CLIs, APIs, MCP servers) as
typed, governed data so it can drive them safely. Two levels:
- **Level 2 — DATA:** `platforms/<id>.py`, each a pure-data `PLATFORM = {...}` dict validating against
  `contracts/platform_entry.py:PlatformEntry`. One platform = one row. No logic in a row.
- **Level 1 — ENGINE:** `introspection/` — platform-agnostic, **zero platform-name literals** (a build
  grep fails on a leak). Four verbs: **DISCOVER** (run the platform's `--help`/init, parse capabilities)
  → **CLASSIFY** (5 rules R1–R5 derive a posture per flag: locked/hazard/consent/safe/unmatched) →
  **PROJECT** (face-neutral) → **REFRESH** (re-discover on version bump, surface novelty).
- Postures are **derived, never opinions**: `(flag_name, signal_sets) → posture`, reproducible.

## How the three platforms are integrated (the map)
| platform | row | discovery | consumer (who actually USES it) | freshness |
|---|---|---|---|---|
| **claude-code** (#1) | `claude_code.py` (+`_wiring.py` head_builder) | cli-help **+ stream-init** (held session) | DEEP: session_supervisor reads spawn-flag posture from the registry; `cap://` resolver; Suite wires CapabilityRegistry at init | `store/claude-code.version_stamp` + SessionStart hook |
| **gh-cli** (#2) | `gh_cli.py` | cli-help (`gh pr create --help`, 21 flags) | **NONE** — registered/discoverable only; nothing in the fabric invokes `gh` | none |
| **codex-cli** (#3, NEW) | `codex_cli.py` | cli-help (`codex exec --help`, 24 flags → 4 locked/2 hazard/8 consent/10 safe) | **LIVE**: the ledger interpretive producer drives `codex exec` (ops/ledger_interpret_codex.py) | none |

Claude Code is the deep instance (held-open injected sessions, supervisor posture, cap:// wiring). gh
proved the lift (a 2nd known-kind CLI is ~free). codex is the first **non-claude platform with a real
fabric consumer** — so it's where "registered" meets "used."

## GAPS found → folded into scope (noticing = in-use)
1. **clap-vs-commander parse quirk (codex).** The `cli-help` adapter's `_OPTION_ROW` regex expects a
   flag's description on the SAME line (≥2-space gap); clap (codex) prints descriptions on the NEXT
   indented line → codex flag `description`s come back EMPTY. Flags + classification are unaffected
   (R1–R5 key off flag name + signal_sets; R2 is flag_name_only). FIX (when a 2nd clap platform needs
   it): a `clap-options` parse_rule, or a continuation-line join in `introspection/adapters/cli_help.py`.
2. **gh-cli has no consumer.** It's registered but nothing drives it — a dead-registered platform. The
   GitHub integration is latent. Opportunity (surfaced, not built): wire `gh` to a real fabric use —
   e.g. file a GitHub issue/PR from a board item, or push a branch — so the registry entry earns its keep.
3. **Consumers hardcode the binary instead of resolving via the registry.** `ledger_interpret_codex.py`
   hardcoded `CODEX = /home/linuxbrew/.linuxbrew/bin/codex`. The registry already declares the
   `executable_locator` (env → PATH → known_paths). A consumer should resolve through the registry so the
   registry is the single truth. FIXED for codex (see "connection made" below) — the pattern to copy.
4. **Freshness/refresh is claude-code-only.** `store/claude-code.version_stamp` + the SessionStart hook
   (`ops/hooks/cc_registry_freshness_check.sh`) check only claude. gh and codex can drift silently. FIX:
   generalize the freshness check to iterate the platform registry (every platform with a `version_source`).
5. **`cap://` + CapabilityRegistry are single-platform at init.** `Suite.__init__` discovers only the
   claude-code PlatformEntry into the CapabilityRegistry, so `cap://flag/--model` for codex/gh wouldn't
   resolve. FIX: discover all registered platforms into the cap:// space (namespaced by platform id).
6. **No `cap://` namespacing by platform.** `cap://flag/--model` is ambiguous now that 3 platforms each
   have flags. Likely needs `cap://<platform>/flag/--model`. Surfaced for the cap-wire owner.

## Integration status — "drop a row wires everything" (your never-touch-again bar)
Done 2026-06-28 — the consumers that hardcoded `claude-code` are now REGISTRY-DRIVEN, so a future
`platforms/<id>.py` row is picked up automatically:
- ✅ **DISCOVER/CLASSIFY/PROJECT engine** — always was registry-driven (platform-agnostic, leak-gated).
- ✅ **Refresh flow** (`flows/cc_registry_refresh.py`) — `run(platform_id=…)` + `run_all()` (every platform with a version_source).
- ✅ **Freshness SessionStart hook** — `ops/hooks/registry_freshness.py` iterates ALL platforms; the bash hook calls it (claude-only fallback kept).
- ✅ **MCP capability tool** — already filters by `platform_id`.
- ✅ **codex consumer** — resolves the binary via the registry's `executable_locator`.
- ✅ **Self-describing constitutions** updated (`platforms/AGENTS.md`, `introspection/AGENTS.md`) — no drift.
- ⏳ **`cap://` capability resolution** (the ONE remaining piece — needs a design decision, NOT a blind edit):
  `runtime/cognition.py` resolves `cap://flag/--model` FLAT (`registry.get("flag/--model")`), and
  `Suite.discover_capabilities()` discovers ONLY `claude-code`. Multi-platform requires (a) discovering
  all platforms into the registry (entries are already `platform_id`-tagged) AND (b) **namespacing the
  scheme** — likely `cap://<platform>/<kind>/<name>` — which CHANGES existing `claude-code` cap:// ids, so
  it touches the resolver + `CapabilityRegistry.get` + `cap_wire_acceptance`. Surfaced for Tim's call on
  the namespacing convention before it's built (don't silently break claude-code's existing addresses).

## OPTION C BUILT (2026-06-28) — source-namespaced capability addresses + the ledger convergence
The cap:// scheme + capability layer is now source-first and joins the one addressed graph. Done + verified:
- ✅ **Nested address grammar** `cap://<platform>[@version]/<kind>/<name>` (`contracts/address.py:parse_cap_address`/`cap_address`), with the **legacy `cap://<kind>/<name>` → claude-code alias** (back-compat). Version pin supported.
- ✅ **Open kind vocabulary** (`contracts/capability_entry.py`): `kind` is now an open `str` (was a closed Literal) with `KNOWN_KINDS` as the reference set — so a REST `endpoint`, a gRPC `method`, a GraphQL `subscription` from any future source land without a contract edit. `platform_id` now stamped from the discovering platform (was defaulting to claude-code).
- ✅ **Multi-platform registry** (`introspection/registry.py`): entries keyed by full nested id `<platform>/<kind>/<name>`; `discover()` MERGES (many platforms in one registry); `get`/`in`/`[]` accept nested + legacy. The **codex-vs-claude `--model` collision is resolved** (two distinct nodes).
- ✅ **Resolver** (`runtime/cognition.py` cap branch) resolves both nested + legacy via the registry.
- ✅ **Suite runtime discovery** (`discover_capabilities(platform_id=None)`) discovers ALL platforms into the registry, per-platform fail-isolated — so `cap://<any-platform>/…` resolves at runtime.
- ✅ **Capabilities as LEDGER NODES** (`ops/ledger_capabilities.py`): 438 nodes (claude 390 / codex 24 / gh 21 + 3 platform nodes) + 435 `capability-of` + 17 `on-axis` edges in project `platforms` — "what can codex do" is now a graph query, source-addressed, version-aware. **This is the convergence: capabilities live in the same addressed graph as code.**
- ⏳ **Step 7 auto deep-link (code→capability)** — ATTEMPTED, found insufficient, PULLED (no fiction): string-matching can't distinguish a flag MENTIONED in a comment from one actually INVOKED (e.g. `address.py` matched codex flags in its own docstrings). The correct version is AST invocation-context matching (parse subprocess/exec calls where argv[0] is the binary). Kept as code + negative result; `--link` gated. The honest next step.

Acceptance: `introspection_acceptance`, `genproof_second_platform_acceptance`, `cap_wire_acceptance` all still PASS; leak-grep clean. The whole thing is general: a new `platforms/<id>.py` row gets nested addressing, multi-platform resolution, refresh, freshness, AND a place in the ledger graph — for free.

## SETUP (so a fresh machine has codex — captured, was ad-hoc)
- **Install:** `npm install -g @openai/codex` (needs node; node v25 present). Lands `codex` on PATH
  (`/home/linuxbrew/.linuxbrew/bin/codex`). Version pinned in the row's `version_source` probe.
- **Auth:** `codex login` (ChatGPT-account device/loopback flow) — credential in `~/.codex/`. Verify:
  `codex login status` → "Logged in using ChatGPT"; `codex exec "reply with codex-ok"` confirms headless.
- **No company-managed key needed** for the ChatGPT-plan path (the interpretive producer uses `codex exec`).

## Connection made (this pass)
- **codex registered + proven** (24 flags, classifies clean, zero engine edits, leak-grep clean,
  acceptance tests still green).
- **codex consumer now resolves via the registry** — `ledger_interpret_codex.py` resolves the binary
  through `introspection.discover.resolve_executable(platform)` (the `executable_locator`), so the running
  interpretive producer is a genuine registry CONSUMER, not a hardcoded path. This is the template for
  giving gh a consumer too.
