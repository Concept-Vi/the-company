---
type: constitution
module: root
aliases: ["Company — read first", "AGENTS", "Company Constitution"]
tags: [company, constitution, root, orientation]
governs: []
relates-to: ["[[Company Map]]", "[[Company State]]", "[[Vault Conventions]]"]
status: living
---

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
9. **AI-operated is NOT review-free, and FORM is half of done.** Every feature includes a UI/UX *design + implementation* pass; **review (the operator via the RHM organ + a separate design-critic agent) is MANDATORY and is a SEPARATE stage from implementation.** "Done" is **two-faced — FUNCTION and FORM** — and the AI default is to ship the function half and call it done. That default is wrong here. The FORM half is the **product bar**, made concrete: any operator-facing surface is **built on the design system** (its components + design tokens — *never* hardcoded values or bespoke one-offs), coherent in scale/type/spacing/layout, responsive, settings consolidated, and a **navigable visual/spatial surface, not a text-wall or list** (the operator recognises by sight, not by reading). A surface that works but is bespoke, overlapping, or prototype-grade is **half-done, which is not done.** FORM is verified by a **separate design-critic** (the implementer cannot grade its own form — it defaults to function, exactly why correctness gets a separate adversary) and, where machine-checkable, **gated by a design-lint that fails loud** (off-token / bespoke-element → the build cannot be marked done — the path-of-least-resistance law applied to design). No implementation is "done" until its result is **surfaced for review** AND its FORM passes; a backend-only change still updates the surface that exposes it. Concretely in the decision→implementation wire: `implemented` means "done AND surfaced for review" (a `decision.surfaced_for_review` event + a review inbox item carrying the result + the changed-files diff), **never a silent terminal**. Coherent with rule 4 (fail loud — a silent close is a silent failure) and *reflects-never-owns*: the wire writes the `status` lane and surfaces a review item; it **never** writes the operator `resolved` field. The operator resolves the review.

10. **Commit to `main` — NO feature branches.** This repo has **no developers and no merge orchestration.** Tim runs multiple sessions in parallel and assumes every session is building on `main` (on what every other session has done). A feature branch left unmerged when a session ends is **stranded work nobody knows to merge** — a recurring, real headache. So: work on `main`; **verify by tests BEFORE you commit** (fail-loud — never commit broken); concurrent sessions committing to `main` is fine (git serialises). If you truly need isolation, use a `git worktree` (not a branch) and merge back the same session. To shelve work without losing it: tag it (`archive/<name>`) then delete — never leave a stranded branch. *(This overrides any inherited build-skill convention that says "branch off main, never commit to main" — that assumes orchestrated human merge, which does not exist here.)*

## Where things go (one obvious answer each)
| Want to add… | Go to | Read its AGENTS.md, then |
|---|---|---|
| a new **node-type** (process/content/presentation) | `nodes/<name>.py` | declare VERSION/KIND/PORTS + `run`; drop it in; it self-registers (auto-discovered). If it reads **mutable truth** (repo, index, model-of-someone, clock) → also `VOLATILE=True` or the memo gate freezes it |
| a new **model / provider** | `fabric/config.py` | repoint `DEFAULT_BASE_URL` / register; `transport.list_models` exposes them |
| a new **storage backend** | `store/` | implement the Resolver Protocol (C4); add a backfill |
| a new **RHM action verb** | `runtime/suite.py` | add to `RHM_VERBS` + `_parse_rhm_action` + `_dispatch_rhm_action`; whitelist-gated |
| a new **presence mode** | `runtime/suite.py` `MODES` + `MODE_DIRECTIVES` | the mode IS a node (`rhm_mode`); behavior comes from the directive |
| a **settings/control panel** (declarative) | ask the RHM (`propose_panel`) | fields edit real config; the 'others' tier; git-reversible |
| a **new UI component in code** (arbitrary) | ask the RHM (`propose_extension`), operator-only | build-GATED → `src/extensions/` → error boundary → git-revert |
| a new **canvas surface** (structural) | `canvas/app/src/App.tsx` | external-agent edit; node/panel/extension rendering stays generic |
| a genuinely **new operation** (rare) | `mcp_face/` + `runtime/suite.py` | add one verb (C7) — only for a new *kind* of operation |
| a new **contract** | `contracts/` | a new `Cn`; CONFIRM (it widens the system) |

**Every change updates the self-description** (this file · `MAP.md` · `STATE.md` · the module's `AGENTS.md`) — it is part of the change, not optional. The *factual* blocks (MAP's live registry, STATE's suite index) regenerate themselves via `Suite.refresh_self_description()` (run on every apply); the *prose* (STATE's "what's built / what can't be done yet", a module's constitution) you update **by integration** — change what the new piece makes untrue, keep the rest coherent. `tests/drift_acceptance.py` **fails loud** if a registered capability or an acceptance suite isn't reflected — so drift is caught, never silent. **Updating the self-description is itself a clause of rule 9** (review-not-free): the next agent and the operator navigate by it, so a change that doesn't update it is not "done" — and an operator-facing surface the change touches must meet the product bar as part of the same change.

> If "where does this go?" isn't obvious from this table + the module constitutions, that's a bug in the repo's self-description — flag it.

## The convention
**Every folder** has an `AGENTS.md` (its **constitution**): what it is · what it must guarantee · where new things go · how to extend · its seam · what would violate it. **Read a folder's constitution before editing it.** `MAP.md` is the loadable map of the whole thing.

This repo is **also an Obsidian vault** — the same markdown is a navigable knowledge graph (frontmatter + `[[wikilinks]]` + a folder-note per folder). The full convention is [[Vault Conventions]]; the vault home is [[Company Map]]. When you add or change a folder, decorate its constitution to that convention as part of the change — the knowledge face is not optional documentation, it is how the next agent (and the operator) navigates.
