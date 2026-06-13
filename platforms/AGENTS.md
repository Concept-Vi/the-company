---
type: constitution
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

**Where the mechanism lives:** the four-verb engine, the rules, the adapters, the two registries, the
cached-singleton rationale (F-FIX-1), the derive contract (F-FIX-2), and the leak invariant are all
documented in **`introspection/AGENTS.md`** — read it before adding a platform. Adding a platform of a
KNOWN kind = dropping a `platforms/<id>.py` row (almost free); a NOVEL kind = one new adapter in
`introspection/adapters/`, gap-surfaced, never hand-papered.
