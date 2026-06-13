---
type: constitution
module: introspection
aliases: ["introspection — constitution"]
tags: [company, constitution, introspection, mirror-registry, platform-agnostic]
governs: [Mirror-Registry System, LANE-INTROSPECTION-CORE, LANE-REGISTRIES]
relates-to: ["[[Company Map]]", "[[contracts — constitution]]", "[[runtime — constitution]]"]
status: living
---

# introspection/ — module constitution

**Is:** the **platform-agnostic Mirror-Registry engine** (Level 1) + the **instance-#1 CLI adapters**.
The engine operates ONE four-verb circuit — **DISCOVER → CLASSIFY → PROJECT → REFRESH** — over a
`PlatformEntry` (contracts/platform_entry.py) and the two registries (Platform Registry +
Capability Registry, LANE-REGISTRIES). A *platform* (Claude Code, a REST API, an MCP server, a vLLM
gRPC endpoint) is **ONE data row** in `platforms/<id>.py`; the engine never knows its identity.

**The lift (PG2 / F-FIX-10 — load-bearing, the whole point):** `introspection/engine.py`,
`introspection/rules.py`, and everything in `introspection/adapters/` carry **ZERO platform-name
literals**. No `claude`, no `claude-code`, no `dangerously`, no `--mcp-config`, no `stream-json` as a
literal anywhere in Level-1 code. Every platform-specific string arrives as **DATA** on a
`PlatformEntry` / `SignalSets` / `DiscoverySource`. `tests/introspection_acceptance.py` greps these
files for the banned strings and **FAILS the build on any hit** — a hit means Level-2 data leaked into
Level-1 code and the lift is broken. The legitimate home for those strings is `platforms/claude_code.py`
(Level 2, LANE-REGISTRIES); the grep is EXPECTED to hit there.

**The four verbs (engine.py + discover.py + rules.py):**
- **DISCOVER** (`discover.py`): resolve the executable (the invoker's find primitive), run EACH
  declared `DiscoverySource` through the adapter selected from the **CLOSED** `DISCOVERERS` map by
  `src.type`, collect `CapabilityEntry` rows. A declared source whose adapter is **not built** →
  `MissingAdapterError`, LOUD, naming the missing class (the §8.3 boundary / C-GENPROOF converse) —
  **never a silent empty registry**. A parse below `floor_guard` → RAISE.
- **CLASSIFY** (`rules.py`, driven by `engine.classify_entries`): the **five closed rules** R1–R5 at
  priority **R1 > R2 > R3 > R5 > R4** over a `SignalSets`. Posture is **DERIVED, never an opinion** —
  `(posture, posture_rule, axis)` is reproducible from `(flag_name, signal_sets)`.
- **PROJECT** (`engine.project`): shape classified rows into a **face-neutral** projection (counts by
  kind/posture + the rows) the MCP tool / bridge route / cap:// resolver read. Not a face itself.
- **REFRESH** (`engine.refresh`): re-DISCOVER, diff against the prior snapshot
  `{added, changed, vanished}`, drive **R4 novelty** (added ids are pending the curator gate). The
  empty-diff-on-version-bump path RAISES (broken-read guard). Write order is fail-closed (LANE-REFRESH).

## The five rules (R1–R5) — what each reads, and the scope guards

- **R1 LOCKED** — the flag is in `signal_sets.transport_invariants` (a set **DERIVED** from the
  consumer's spawn template, see F-FIX-2). A property of the **fabric**, not the flag name.
- **R2 HAZARD** — the flag NAME contains a hazard signal word from `hazard_name_vocabulary`. **SCOPE:
  the flag-NAME string ONLY — NEVER description text.** `hazard_scope` MUST be `"flag_name_only"`; the
  rule ASSERTS it (fail loud) so a future row cannot silently widen the scope to descriptions.
- **R3 CONSENT** — the flag is in a declared `capability_axes` set (widens the session surface).
  Returns the axis name so the entry records WHICH axis (auditable). Includes `--add-dir` on the
  `dirs` axis (directory widening) and the R6 swap-kind head-defaults (`--allowedTools`/`--mcp-config`).
- **R6 SWAP-KIND HEAD-DEFAULT** (spec §2.4a) — NOT a classify rule; an EXCLUSION applied INSIDE
  `derive_transport_invariants()` BEFORE R1 sees the set. A flag in the unconditional spawn head that
  is ALSO a `capability_axes` member is an operator-supplied head default (the operator can swap its
  value), NOT a transport lock — so it is REMOVED from the derived R1 set, letting R3 CONSENT fire
  instead of R1 LOCKED. Computed purely from `capability_axes` DATA (the leak invariant holds — no
  flag-name literal in `rules.py`). A `body_key_overrides` flag is never R6-excluded (the dedicated
  body-key UNION re-adds it — owning a mandated body key is a harder lock than head presence).
- **R5 SAFE** — NOT(R1) AND NOT(R2) AND NOT(R3) — the **EXPOSE-not-gate default** (Tim Ruling 1). Most
  of the surface lands here.
- **R4 UNMATCHED** — a genuinely **novel** flag (first-seen at a refresh, pending the curator gate) or
  a rail/host-incompatible flag → **fail-CLOSED + surfaced**, teaching-refusal, **NEVER silent**. R4 is
  lowest priority (a novel flag that ALSO matches R1/R2/R3 takes the higher posture). Driven by
  `classify_with_novelty` at REFRESH time, not by the membership classifier.

## F-FIX-2 / PG-D1 — TRANSPORT_INVARIANTS is DERIVED, never a hand-list (law: registry-is-truth)

`rules.derive_transport_invariants(head_builder, body_key_overrides, capability_axes)` is **REAL
CODE**. It returns the UNION of (a) the flag tokens the consumer's command builder ALWAYS emits in its
transport HEAD — obtained by CALLING a zero-arg `head_builder` thunk — MINUS (c) the **R6 swap-kind
head-defaults** (head flags that are ALSO `capability_axes` members — see R6 above), PLUS (b) the flag
names of the `body_key_overrides` locked rows. The thunk is bound by Level-2 platform code (it wraps
the consumer's `_build_spawn_cmd` — **the function is `_build_spawn_cmd`, NOT `_build_cmd`**; F-FIX-8).
The row's `signal_sets.transport_invariants` field is **populated by this function at PlatformRegistry
load**, **never hand-typed**. `engine.classify_entries` re-derives LIVE at classify time so a future
supervisor flag addition is reflected automatically. **Drift gate (acceptance test):** every
unconditional-head flag that is NOT an R6 swap-default MUST appear in the derived set — a future head
flag not reflected fails the test loudly rather than silently mis-classifying R1 → R5.

## ROW-PURITY + LANE-SUPERVISOR-REFACTOR (2026-06-14) — registry is the SOLE posture truth

- **The instance row is PURE DATA.** `platforms/claude_code.py` is imports + the `PLATFORM` dict +
  the `SPAWN_FLAG_BODY_KEY_MAP` data dict — **NO def/class**. The head_builder thunk binding (F-FIX-2)
  moved OUT of the row into `platforms/_wiring.py` (a `_`-prefixed bootstrap module the registry's
  file-discovery skips). The consumer that needs the LIVE derivation imports the wiring
  (`runtime/suite.py`; the crosscheck test); a contracts-only context skips it and the row's DECLARED
  (post-R6-correct) `transport_invariants` stands. Cycle discipline (PG-D6) holds: `_wiring.py` is in
  `platforms/` and imports `runtime` (platforms→runtime, ALLOWED); `introspection/` never imports it.
- **Supervisor posture is DERIVED, not hand-stored.** The hand `session_supervisor.SPAWN_FLAGS` dict
  (which carried a `posture` column per flag) is **DELETED** (F-FIX-5 steps 5-6). `_apply_spawn_flags`
  now reads posture from `_registry_posture(flag)` → `rules.classify` over the claude-code signal_sets
  (swap-aware via R6). The remaining `SPAWN_FLAG_ASSEMBLY` table holds ONLY consumer-emission data
  (flag-name, assembler kind, teaching text) — no posture. The cross-check fixture
  (`tests/spawn_flags_crosscheck_acceptance.py`) was the gate on the swap (proved 48/48, zero
  divergence); post-deletion it is the standing **regression gate** (every flag's derived posture
  must equal the frozen verified ground-truth + classify to a real posture).
- **`--add-dir` is CONSENT, not locked.** It widens the session's filesystem reach (an R3 `dirs`
  capability axis), so it rides the operator-consent beat. It was previously mis-locked because it sat
  in `body_key_overrides` (which the F-FIX-2 derivation unions into the R1 set, R1 > R3). Resolution:
  declared on `capability_axes["dirs"]` + removed from `body_key_overrides`.

## F-FIX-1 / PG-D2 — the CapabilityRegistry singleton is a NEW pattern, NOT a sibling-registry copy

**This is a deliberate divergence; a build agent who greps the code WILL find a contradiction unless it
reads this.** The sibling registries (`skill_registry()`, `context_registry()` at
`runtime/cognition.py:86,92`) are **fresh-discover-on-each-call factories** (their docstrings literally
say "fresh each call"). There is **no `_registry_singleton`, no `set_skill_registry`** anywhere in
runtime/. **CapabilityRegistry does NOT copy that pattern.** It is a **module-level singleton**
(`introspection/registry.py`, LANE-REGISTRIES): `_registry_singleton` + `set_capability_registry(reg)`
+ `capability_registry()` that **RAISES fail-loud if unset** ("Suite init must call
set_capability_registry"). **Why the divergence:** binary discovery is **EXPENSIVE** — it spawns a
`claude` subprocess (`--help`) and a `system/init` scratch session. Fresh-discover-on-each-call would
spawn a process on EVERY `cap://` resolution — forbidden here. `Suite.__init__` calls
`set_capability_registry()` ONCE. **State the divergence; never "fix" the singleton to match the
siblings.**

### LANE-CAP-WIRE (built 2026-06-13) — the consumer wiring + DEFERRED discovery (no spawn at init)
`Suite.__init__` now (runtime/suite.py, after the registry block): resolves the `claude-code`
`PlatformEntry` from `introspection.platforms.platform_registry()`, constructs an **empty**
`CapabilityRegistry`, and calls `set_capability_registry()` on it ONCE — so
`runtime/cognition.py:resolve_address` resolves `cap://<kind>/<id>` via `capability_registry().get(rest)`
(lazy import inside the branch; PG-D6 cycle-free — `introspection` never imports `runtime/`, and the
supervisor head-builder `platforms/claude_code.py` registers does NOT import `Suite`). **Discovery is
DEFERRED, NOT run at init:** the live `CapabilityRegistry.discover()` spawns the binary (LEAD-only), so
`__init__` installs an un-discovered registry and `cap://` stays fail-loud-correct meanwhile (an empty
registry RAISES "unknown capability" for any id — registry-is-truth, never a fabricated row). A LEAD run
populates it via `suite.discover_capabilities()` (the default spawns the binary) or
`suite.discover_capabilities(discover_fn=<stub>)` (no-spawn unit/CI), or opts in at construction with
`COMPANY_CAP_DISCOVER_AT_INIT=1`. The registry is mutated IN PLACE, so every `cap://` resolution + the
`capabilities()['introspection']` summary read the same object the moment discovery lands.
**Unit-verified** (no live claude / no model load): `tests/cap_wire_acceptance.py` (14 checks — import
cycle-free, wired-at-init, empty-is-fail-loud, stub-entry resolves end-to-end through the real
`resolve_address`, unknown fails loud, the `introspection` capabilities key reflects the populated rows).
**🟡 LEAD live-verify queued:** C-WIRE-1/2/3 — the live-binary `discover()` (≥30 real flags) + a real
`cap://` resolution from the running server.

## F-FIX-15 / PG-D3 — store write convention: direct `open()`, NOT FsStore CAS

The discoverer/refresh flow writes `store/introspection_cache.json` and
`store/<platform_id>.version_stamp` via **direct `open()` against the store path**. FsStore is
content-addressed for NODES; the version stamp + cache are **flat operational files**, not CAS content.
Do not reach for an FsStore method — these are plain files. (LANE-REFRESH owns the actual write.)

## PG-D5 — PlatformEntry loads via `model_validate`

`PlatformRegistry` loads each `platforms/<id>.py` `PLATFORM = {...}` dict via
`PlatformEntry.model_validate(dict)` — the deeply-nested sub-models need validation, not positional
construction. A novel `discovery_sources[].type` / `inject_transport` / `invocation_kind` value is a
typed Literal → Pydantic FAILS LOUD at load (F-FIX-12), surfacing the gap rather than configuring an
unrunnable adapter.

## The closed adapter set (the instance-#1 CLI members; the rest gap-surface)

`introspection/adapters/` — selected by STABLE selector, never by platform identity:
- `CliHelpDiscoverer` — `DiscoverySource.type == "cli-help"` (Commander `--help` option-row parse).
- `StreamInitDiscoverer` — `DiscoverySource.type == "stream-init"` (running-session init self-declare).
  **LEAD-only live verify**: `discover()` spawns a real session; unit-verified with a fixture init event.
- `VersionProbe` — reads the running version (the freshness key) from a `VersionSource`.
- `SubprocessAdapter` — `InvocationKind == "subprocess"` (the DISCOVER-side run primitive; find_executable
  is env → PATH → known_paths, **fail loud** if absent).

`DISCOVERERS` / `INVOKERS` (adapters/__init__.py) are the **single registration point** — adding a kind
is adding a row. **REST / GraphQL / MCP / library / grpc / sdk** discoverers + invokers are
**NAMED-but-UNBUILT** (Build Plan §7 R-ADAPTERS, F-FIX-16). A platform that selects one **FAILS LOUD**
naming the missing class; it is built when platform #2 of that kind registers. `grpc` (Tim's vLLM
endpoint) and `sdk` (SDK-native streaming) are the near-term-real gaps.

## C-GENPROOF (THE LIFT GATE) — PROVEN BY USE with a REAL 2nd platform (2026-06-14)

The generalization-proof is no longer a stub: **`platforms/gh_cli.py`** registers the GitHub CLI (`gh`,
a COBRA-family tool — a different tool family from instance #1's Commander.js) as INSTANCE #2, a PURE
data row reusing the EXISTING `cli-help` adapter with **ZERO edits** to `engine.py`/`rules.py`/
`discover.py`/`adapters/`. Lead live-verify (`gh` 2.74.1, `gh pr create --help`):
`CapabilityRegistry().discover(gh_cli)` → **21 flag CapabilityEntry rows** through
`DISCOVERERS["cli-help"]` unchanged, classified **19 R5 SAFE + 2 R3 CONSENT** (`--repo`→repo-target,
`--web`→browser on the declared axes); live version probe → `2.74.1`. **The headline: a 2nd known-type
platform was almost-free — a single data row, no engine code.** Converse PROVEN: a platform declaring
`discovery_sources[].type="rest-openapi"` (a VALID Literal whose adapter is UNBUILT) passes
`model_validate`, then `discover()` raises `MissingAdapterError` naming `RestOpenApiDiscoverer` + the
built set (the §8.3 gap-surface, not a crash). Leak-grep over the 8 Level-1 files = **0 hits** (the
engine stayed platform-agnostic through a 2nd platform). Proof test:
`tests/genproof_second_platform_acceptance.py` (11/11 green).

## CapabilityEntry id construction (F-FIX-14)

`entry.id = f"{kind}/{name}"`. For flags, `name` **INCLUDES the `--` prefix**:
`CapabilityEntry(id="flag/--debug", kind="flag", name="--debug")`. `cap://flag/--debug` →
`rest="flag/--debug"` → `CapabilityRegistry.get("flag/--debug")` resolves. The discoverers construct
ids this way from the parse output.

## LANE-REFRESH (built 2026-06-14) — version-triggered refresh + SessionStart warning

`flows/cc_registry_refresh.py` — the REFRESH verb's registered flow:
1. Reads the stored stamp (`store/<platform_id>.version_stamp` — direct `open()`, not FsStore CAS,
   per F-FIX-15 / PG-D3).
2. Probes the live binary version via the PlatformEntry's `VersionSource`.
3. **Same-version fast path:** returns `{"status":"unchanged"}` immediately — NO surface call, NO
   false novelty.
4. **Version-bump path:** calls `engine.refresh(platform, prior, ...)` → diff payload
   `{added,changed,unclassified,vanished,version_from,version_to}`, then calls `inbox.surface()` ONCE
   with `action_class="cc_registry_gap"`, `default="reject"` (fail-closed — F-FIX-4 / PG-D4).
5. **Stamp is NOT written by this flow** (proposes_only discipline). `write_stamp_and_cache()` is
   exported for the post-curator-approval governance action — fail-closed write order (F-FIX-7).

`ops/hooks/cc_registry_freshness_check.sh` — SessionStart hook (F-FIX-13 / C-REF-1):
Compares `store/claude-code.version_stamp` to `claude --version`; emits `REGISTRY FRESHNESS: STALE`
warning if mismatched; **silent** on current; **exits 0 always** (non-blocking). Wired via
`.claude/settings.json` `hooks.SessionStart`. First file in `ops/hooks/` — a **NEW pattern**, no prior
template.

Verification (44/44, no live claude): `tests/introspection_acceptance.py` — covers C-REF-1..5 (partial),
C-GENPROOF-known/novel, FLOW-REGISTRATION, STAMP-LOGIC, SETTINGS-JSON.
**🟡 LEAD live-verify queued:** C-REF-1 full (live SessionStart hook injection), C-REF-2 full (real
Inbox.surface() in a live session), stamp+cache persist post-approval.

## What this module must NEVER do

- **Never** name a platform in `engine.py` / `rules.py` / `adapters/` (the leak invariant — the build
  fails on it).
- **Never** hand-type `transport_invariants` (derive it; the drift gate fails on a hand-list).
- **Never** return a silent empty registry — an unbuilt adapter, an empty discovery, a sub-floor parse
  all **FAIL LOUD** (fail-loud / no-silent-failures law).
- **Never** silently drop an init field — an unmapped field is captured into `raw_extra` with a note
  (the no-self-report=gap law), or escalates to a raise on an empty `field_kind_map`.
- **Never** classify with an empty R1 set (it would silently demote every locked transport flag to
  SAFE) — `derived_transport_invariants` RAISES if neither thunk nor cache is available.
