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

**The DATA-ONLY discipline (load-bearing — the lift, PG2 / F-FIX-10):** a `platforms/<id>.py` file is
DATA, not logic. It declares the dict and — at most — the **single sanctioned binding** that a
Pydantic model cannot hold: a `head_builder` thunk registered with the engine
(`engine.register_head_builder`) so the R1 transport-invariant set DERIVES from the consumer's live
spawn template (F-FIX-2), and any other build-time registration the engine seam explicitly invites.
**No classification logic, no parse logic, no dispatch logic lives here** — that is all Level-1 engine
code. If you find yourself writing an `if`/`for` over capability values in a platform file, the value
belongs on the engine or as a typed field on the row. The legitimate platform-name strings
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

**Instance #1 — `claude_code.py`:** Claude Code expressed as one row (Spec §7). It also carries the
`SPAWN_FLAG_BODY_KEY_MAP` (the F-FIX-5-step-3 body-key↔flag-name map the deferred
LANE-SUPERVISOR-REFACTOR + the F-FIX-9 cross-check use) and the head_builder binding. The engine +
the closed adapters + the 5 rules read the row; nothing about Claude Code lives in the engine.

**Where the mechanism lives:** the four-verb engine, the rules, the adapters, the two registries, the
cached-singleton rationale (F-FIX-1), the derive contract (F-FIX-2), and the leak invariant are all
documented in **`introspection/AGENTS.md`** — read it before adding a platform. Adding a platform of a
KNOWN kind = dropping a `platforms/<id>.py` row (almost free); a NOVEL kind = one new adapter in
`introspection/adapters/`, gap-surfaced, never hand-papered.
