---
type: constitution
register: prescriptive
module: platforms
aliases: ["platforms — constitution"]
tags: [company, constitution, platforms, mirror-registry, level-2, data-only]
governs: [Mirror-Registry System, LANE-REGISTRIES]
relates-to: ["[[Company Map]]", "[[introspection — constitution]]", "[[contracts — constitution]]"]
status: living
---

# platforms/ — module constitution

**Is:** the **Level-2 platform table as DATA** — one `platforms/<id>.py` per external platform the
Company mirrors, each declaring a module-level `PLATFORM = {...}` dict that validates against
`contracts/platform_entry.py:PlatformEntry`. `PlatformRegistry` (`introspection/platforms.py`)
discovers these files via the importlib registry-family pattern (mirrors `runtime/roles.py`). A
platform is **ONE row**; the engine (`introspection/`, Level 1) never knows its identity.

**The DATA-ONLY discipline (load-bearing — the lift, PG2 / F-FIX-10; ROW-PURITY tightened 2026-06-14):**
a `platforms/<id>.py` row file is **PURE DATA — imports + dicts, NO def/class.** The one binding a
Pydantic model cannot hold (the `head_builder` thunk the engine derives the R1 transport-invariant set
from, F-FIX-2) does **NOT** live in the row anymore — it moved to **`platforms/_wiring.py`** (a
`_`-prefixed bootstrap module the registry's file-discovery skips). The consumer that needs the live
derivation imports the wiring (`runtime/suite.py`; the crosscheck test); the row keeps only its
DECLARED (engine-validated, post-R6-correct) `transport_invariants` as the fallback. Keeping the row
pure makes it the **clean template** the generalization-proof copies. **No classification logic, no
parse logic, no dispatch logic, no def/class lives in a row** — that is all Level-1 engine code (or
`_wiring.py` for the one sanctioned binding). If you find yourself writing an `if`/`for`/`def` in a
platform row file, it belongs on the engine, as a typed field on the row, or in `_wiring.py`.
The legitimate platform-name strings
(`claude`, `--mcp-config`, `stream-json`, …) live HERE and ONLY here + the row's nested data — never
in `introspection/engine.py` / `rules.py` / `adapters/` (the acceptance leak-gate greps those and
FAILS the build on a hit; the grep is EXPECTED to hit `platforms/`).

**Id ↔ filename:** the row's `id` must equal the file name with `_`↔`-` normalized — a Python module
file cannot contain a hyphen, but the canonical Platform-Registry key is hyphenated, so
`platforms/claude_code.py` carries `id: "claude-code"`. Anything beyond that hyphen/underscore
difference RAISES at discovery (addressable-by-file discipline, mirroring roles/node-types).

**Fail-loud / no silent config (F-FIX-12, PG-D5):** the registry loads each `PLATFORM` via
`PlatformEntry.model_validate(dict)`. A novel `discovery_sources[].type` / `inject_transport` /
`invocation_kind` value is a typed Literal → Pydantic FAILS LOUD at load, surfacing the gap rather
than silently configuring an unrunnable adapter. A platform that selects a VALID-but-UNBUILT adapter
(rest-openapi/mcp/graphql/library/grpc/sdk) fails loud at DISCOVER naming the missing class.

**Instance #1 — `claude_code.py`:** Claude Code expressed as one PURE-DATA row (Spec §7) — imports +
the `PLATFORM` dict + the `SPAWN_FLAG_BODY_KEY_MAP` data dict (the F-FIX-5-step-3 body-key↔flag-name
map the now-LANDED LANE-SUPERVISOR-REFACTOR + the F-FIX-9 cross-check use). The head_builder binding
lives in `_wiring.py` (row-purity), NOT in this row. The engine + the closed adapters + the 5 rules
read the row; nothing about Claude Code lives in the engine. **The supervisor reads spawn-flag posture
from this row's signal_sets via the rules** (`session_supervisor._registry_posture`) — the hand
`SPAWN_FLAGS` posture dict is deleted; the registry is the sole posture truth (F-FIX-5 steps 5-6).

**Instance #2 — `gh_cli.py` (THE GENERALIZATION-PROOF, 2026-06-14):** the GitHub CLI (`gh`, id
`gh-cli`) expressed as a PURE-DATA row — imports + the one `PLATFORM` dict, NO def/class — that reuses
the EXISTING `cli-help` adapter with **ZERO engine/adapter edits**. `gh` is a COBRA-family CLI (a
different tool family from instance #1's Commander.js), yet its `gh pr create --help` FLAGS section is
the same option-row SHAPE the generic parser reads. Lead-verified: DISCOVER→CLASSIFY→PROJECT yields 21
flag rows (19 R5 SAFE + 2 R3 CONSENT) through the unchanged machinery. It is the clean template applied:
**a 2nd known-kind platform is almost-free.** It is much smaller than `claude_code.py` because `gh` is
invoked-and-exits (no held-open injected session) — so NO `consumer_reserved_invariants` body-key
machinery, NO `stream-init` source, NO state machine; it declares its OWN small `signal_sets`
(transport_invariants/hazard vocab/capability axes) so CLASSIFY produces real postures (no head_builder
thunk is wired, so its DECLARED `transport_invariants` IS the engine-validated R1 input). Proof:
`tests/genproof_second_platform_acceptance.py` (11/11 green). The converse (an unbuilt `rest-openapi`
type → `MissingAdapterError` naming the missing class) is proven in the same suite.

**Instance #3 — `codex_cli.py` (the OpenAI Codex CLI, id `codex-cli`, 2026-06-28):** the lift applied a
THIRD time AND the first platform with a LIVE in-fabric consumer. A PURE-DATA row reusing the `cli-help`
adapter with ZERO engine edits, over a THIRD tool family — `codex` is RUST/clap (instance #1 Commander.js,
#2 Cobra). Proven by use: `codex exec --help` → **24 flag rows** through the unchanged machinery,
classified **4 R1 LOCKED + 2 R2 HAZARD (`--dangerously-bypass-*`) + 8 R3 CONSENT + 10 R5 SAFE**; leak-grep
0, acceptance tests green. Unlike `gh-cli` (registered-only), `codex` is actually DRIVEN: the ledger
interpretive producer (`ops/ledger_interpret_codex.py`) resolves the binary via this row's
`executable_locator` (`introspection.discover.resolve_executable`) and runs `codex exec` — so a consumer
reads the registry as truth, not a hardcoded path. KNOWN GAP (recorded, not papered): clap prints flag
descriptions on the NEXT line while the cli-help parser expects them same-line → codex flag `description`s
come back EMPTY (classification unaffected; a `clap-options` parse_rule is the future fix). Full notes:
`build-prep/the-one-system/REGISTRY-NOTES.md`.

**The downstream consumers are now REGISTRY-DRIVEN (2026-06-28 — the 'drop a row wires everything' fix):**
the engine generalized long ago, but three consumers still hardcoded `claude-code`; they were lifted so a
new platform row is picked up automatically: (a) `flows/cc_registry_refresh.py` takes `platform_id=` and
adds `run_all()` (refresh every platform with a `version_source`); (b) `ops/hooks/registry_freshness.py`
(called by the SessionStart hook) iterates ALL platforms' stamps, not just claude's. STILL claude-only and
scoped as the remaining piece: the `cap://` capability wiring in `Suite.__init__` discovers only
`claude-code` (multi-platform `cap://` needs platform-namespacing + the resolver — see REGISTRY-NOTES §5/6).

**Where the mechanism lives:** the four-verb engine, the rules, the adapters, the two registries, the
cached-singleton rationale (F-FIX-1), the derive contract (F-FIX-2), and the leak invariant are all
documented in **`introspection/AGENTS.md`** — read it before adding a platform. Adding a platform of a
KNOWN kind = dropping a `platforms/<id>.py` row (almost free — see `gh_cli.py`); a NOVEL kind = one new
adapter in `introspection/adapters/`, gap-surfaced, never hand-papered.
