---
type: constitution
module: contracts
aliases: ["contracts — constitution"]
tags: [company, constitution, contracts, spine]
governs: [C1, C2, C3, C4, C5, C6, C7, C8]
relates-to: ["[[Company Map]]", "[[store — constitution]]", "[[runtime — constitution]]", "[[nodes — constitution]]", "[[mcp_face — constitution]]", "[[canvas — constitution]]"]
status: living
---

# contracts/ — module constitution

**Is:** the pinned data shapes — C1 addresses · C2 node-type · C3 node-record · C4 resolver · C5 object_info/compile · C6 context-variable · C7 MCP tools · C8 bridge. The **spine** every other module composes against.
**Guarantees:** shapes carry a **version marker** — `schema_ver` on records/messages (Provenance, bridge msgs, tool schemas), `version` on `NodeType`. Growth is **additive only** — new *optional* fields (with defaults). A breaking change is a **new versioned shape side-by-side**, never an edit to an existing one. No backend types leak in here (shapes are storage-agnostic).
**Where new things go:** a new contract = a new file `Cn.py`; a new field = additive on the existing shape.
**To extend:** add an optional field + bump `schema_ver`; OR add a new versioned shape. Update the vault spec (`build-prep/contracts/`) to match — the vault is source of truth.
**Seam:** everything imports from here; this imports from nothing in the repo. The shapes are consumed by [[store — constitution]] (C1/C4), [[runtime — constitution]] (C5/C6), [[nodes — constitution]] (C2), [[mcp_face — constitution]] (C7), and [[canvas — constitution]] (C8).
**Never:** break/rename/remove an existing field · couple a shape to a storage backend · change a contract without CONFIRM (it's the widest-blast-radius act).

## What's in here

The pinned shapes **C1–C8** (`Cn.py`), one file per contract — the **seams every module composes against**, the spine of the system. Each is a storage-agnostic, version-marked definition the rest of the repo imports and obeys:

- **C1 addresses** · **C2 node-type** · **C3 node-record** · **C4 resolver** — the data and resolution shapes.
- **C5 object_info/compile** · **C6 context-variable** — what the runtime reads to run and render.
- **C7 MCP tools** · **C8 bridge** — the agent-face and the runtime↔UI boundary.

For **which module governs which contract**, see [[Company Map]] — the single source; do not duplicate it here.

### Net-new registries living in this spine (with their drift homes)
- **`EDGE_KINDS` (in `contracts/node_record.py`)** — the declared edge-kind vocabulary (`data` · `injection` · `gate` · `fan_in`), added by Concurrent Cognition G1 (C1.3) alongside the `Edge.kind` field and the `SCHEMA_VER` bump to 2 (schema-additive — `kind` defaults to `data`, so every pre-v2 graph loads unchanged). An edge is a declared kind, not a bare wire; the **`injection`** kind is the cognition ref-read (a reply part reads a role's resolved `run://<turn>/<role>` output into its context — `run://` addressing only). **Drift home:** this constitution (the prose here) + `EDGE_KINDS` itself; **drift assertion:** `tests/edge_kinds_acceptance.py` fails loud if a kind isn't reflected here or if the default/old-graph-load invariant breaks. (`gate`/`fan_in` are renderable labels; their behaviour stays NODE-driven — the scheduler's gate/join nodes — never edge-driven.)

- **`C-CAP` — `contracts/capability_entry.py`** — the `CapabilityEntry` contract (Mirror-Registry System LANE-CONTRACTS, 2026-06-13). One row per discovered capability of an external platform. Binary-discovered, not hand-authored. The SINGLE source all faces project from (MCP / bridge / `cap://` resolver). Key design points: `version: int = 1` (registry-type convention — NOT `schema_ver`; matches `contracts/node_type.py`); `assembler_kind` + `locked_reason` fields for supervisor SpawnFlagAssembler (F-FIX-5); `platform_id` FK to PlatformEntry (Mirror-Registry Spec §2.10); `id = f'{kind}/{name}'` with `--` prefix on flags (`cap://flag/--debug` → get `"flag/--debug"`). **Drift home:** this constitution. **DO NOT** use `schema_ver` on this type — the split is: `schema_ver` on wire messages/Provenance, `version` on registry types. A novel `kind` value (not in `EntryKind` Literal) FAILS LOUD — closed-set discipline.

- **`C-PLAT` — `contracts/platform_entry.py`** — the `PlatformEntry` contract + all nested sub-models (Mirror-Registry System LANE-CONTRACTS, 2026-06-13). One row per external platform the Company exposes. Loaded by `PlatformRegistry` (`introspection/platforms.py`) via importlib discovery of `platforms/*.py:PLATFORM = {...}` dicts (mirrors `roles/*.py:ROLE` pattern). Key design points: `version: int = 1` on ALL sub-models (NOT `schema_ver`); **F-FIX-12 typed Literals**: `InjectTransport`, `OutputProtocolFormat`, `DiscoverySourceFormat`, `DiscoverySourceType`, `InvocationKind` are CLOSED — a novel value FAILS LOUD at `PlatformEntry.model_validate()` time (gap-surface fires, never silently configures an unrunnable adapter); add new Literal members ONLY when their adapter is built. Transport invariants (`signal_sets.transport_invariants`) are populated by `derive_transport_invariants()` in `introspection/rules.py` — NEVER hand-typed in the platform row (F-FIX-2). Loaded via `PlatformEntry.model_validate(dict)` not positional construction (PG-D5). **Drift home:** this constitution. Sub-models: `ExecutableLocator`, `DiscoverySource`, `SignalSets`, `ConsumerReservedInvariants`, `VersionSource`, `InvocationBinding`, `PermissionModel`, `ToolSurface`, `ToolServerWiring`, `ResourceGovernance`.

## Relates to

contracts is the **spine** — everything else composes against these shapes; they are changed only deliberately (a new `Cn`, side-by-side, never edit-in-place).

- **Governs** [[store — constitution]] (C1/C4 — addresses + resolver), [[runtime — constitution]] (C5/C6 — object_info/compile + context-variable), [[nodes — constitution]] (C2 — the node-type contract every node obeys), [[mcp_face — constitution]] (C7 — the MCP tool schemas), and [[canvas — constitution]] (C8 — the bridge between runtime and UI).
- **Imports** nothing in the repo — the spine sits beneath everything and depends on nothing above it.

## Read next
[[Company Map]] (which module governs which contract + the whole picture) · [[Concepts and Principles]] (why the shapes are the spine) · [[runtime — constitution]] (the widest consumer of these shapes).
