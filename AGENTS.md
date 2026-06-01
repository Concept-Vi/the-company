# AGENTS.md — read this first

You are an AI agent working on **company** — the Vi composition suite. There are **no human developers**; this codebase is built and grown entirely by AI. It is therefore designed to be **navigable and extensible by you**. Orientation order: **this** (the rules) → `MAP.md` (the structure + the live registry of what exists) → `STATE.md` (the current status: what's built + proven, what cannot be done yet, how to run + verify, the gotchas) → the `AGENTS.md` of whatever module you're working in. After those four you should be able to act correctly without re-deriving anything.

## Source of truth
The **specs live in the vault**, not in code comments:
`/mnt/c/Users/Workstation001/Documents/Claude/Projects/counterpart/the Company/build-prep/`
Start at `Company Build Hub.md`. Contracts = `contracts/` notes (C1–C8). Engine = S1–S7. This repo *implements* those; it does not redefine them.

## The rules (non-negotiable)
1. **Build against the contracts** (`contracts/`). They are the spine. Don't work around them.
2. **Schema-additive, never schema-breaking.** Add optional fields + bump `schema_ver`. A breaking change is a **new version side-by-side**, never an edit-in-place. Existing graphs must keep working.
3. **One source.** A node-type is defined once (C2) → UI, runtime, and tools all project from it. Never duplicate a definition across surfaces.
4. **Fail loud.** No silent failures, no silent fallbacks. Surface a problem; never pretend success.
5. **Storage on ext4** (`~/...`), never under `/mnt/c` (WSL fsync corrupts DBs there).
6. **NO Gemini**, ever. (Hard constraint.)
7. **Stage-gated** (decision D7): work within your assigned stage; act freely in-scope; SURFACE cross-cutting changes; CONFIRM anything irreversible (esp. changing a contract, or touching real source data).
8. **Author from the registry; never invent.** The source of truth for what exists is `Suite.capabilities()` (models, node-types, verbs, panels). Use registered values; **making one up is a failure, the same as not acting.** If something you need isn't registered, **ASK the operator** (surface it) rather than fabricate. This is the *path-of-least-resistance law* — and it binds the system's own self-coding brain as hard as it binds you.

## Where things go (one obvious answer each)
| Want to add… | Go to | Read its AGENTS.md, then |
|---|---|---|
| a new **node-type** (process/content/presentation) | `nodes/<name>.py` | declare VERSION/KIND/PORTS + `run`; drop it in; it self-registers (auto-discovered) |
| a new **model / provider** | `fabric/config.py` | repoint `DEFAULT_BASE_URL` / register; `transport.list_models` exposes them |
| a new **storage backend** | `store/` | implement the Resolver Protocol (C4); add a backfill |
| a new **RHM action verb** | `runtime/suite.py` | add to `RHM_VERBS` + `_parse_rhm_action` + `_dispatch_rhm_action`; whitelist-gated |
| a new **presence mode** | `runtime/suite.py` `MODES` + `MODE_DIRECTIVES` | the mode IS a node (`rhm_mode`); behavior comes from the directive |
| a **settings/control panel** (declarative) | ask the RHM (`propose_panel`) | fields edit real config; the 'others' tier; git-reversible |
| a **new UI component in code** (arbitrary) | ask the RHM (`propose_extension`), operator-only | build-GATED → `src/extensions/` → error boundary → git-revert |
| a new **canvas surface** (structural) | `canvas/app/src/App.tsx` | external-agent edit; node/panel/extension rendering stays generic |
| a genuinely **new operation** (rare) | `mcp_face/` + `runtime/suite.py` | add one verb (C7) — only for a new *kind* of operation |
| a new **contract** | `contracts/` | a new `Cn`; CONFIRM (it widens the system) |

After adding a capability, `MAP.md`'s registry block auto-updates (`Suite.refresh_map`); `tests/drift_acceptance.py` fails loud if the map ever falls behind.

> If "where does this go?" isn't obvious from this table + the module constitutions, that's a bug in the repo's self-description — flag it.

## The convention
Every module has an `AGENTS.md` (its **constitution**): what it is · what it must guarantee · where new things go · how to extend · its seam · what would violate it. **Read a module's constitution before editing it.** `MAP.md` is the loadable map of the whole thing.
