# AGENTS.md — read this first

You are an AI agent working on **company** — the Vi composition suite. There are **no human developers**; this codebase is built and grown entirely by AI. It is therefore designed to be **navigable and extensible by you**. Read this, then read `MAP.md`, then the `AGENTS.md` of whatever module you're working in.

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

## Where things go (one obvious answer each)
| Want to add… | Go to | Read its AGENTS.md, then |
|---|---|---|
| a new **node-type** (process/content/presentation) | `nodes/<name>/` | declare the C2 contract; drop it in; it self-registers |
| a new **model / provider** | `fabric/` | add a config entry (generated from the registry) |
| a new **storage backend** | `store/` | implement the Resolver Protocol (C4); add a backfill |
| a new **context-variable** (for the RHM) | `runtime/context_variables.py` (one file for now; a dir if it grows) | register a ContextVariable (C6) |
| a new **canvas surface / component** | `canvas/` | add a component; node rendering stays generic |
| a genuinely **new operation** (rare) | `mcp_face/` | add one verb (C7) — only for a new *kind* of operation |
| a new **contract** | `contracts/` | a new `Cn`; CONFIRM (it widens the system) |

> If "where does this go?" isn't obvious from this table + the module constitutions, that's a bug in the repo's self-description — flag it.

## The convention
Every module has an `AGENTS.md` (its **constitution**): what it is · what it must guarantee · where new things go · how to extend · its seam · what would violate it. **Read a module's constitution before editing it.** `MAP.md` is the loadable map of the whole thing.
