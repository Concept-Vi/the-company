---
type: concept
module: docs
aliases: ["Concepts and Principles", "principles", "the why"]
tags: [company, concept, principles, foundation]
governs: []
relates-to: ["[[Company Map]]", "[[Company — read first]]", "[[Vault Conventions]]", "[[Coherence Gate — Spec]]"]
status: living
---

# Concepts and Principles — the *why* under the repo

> **What this is:** the conceptual ground the rest of the repo stands on — *what* this thing
> is and *what it believes*, as opposed to *where things go* ([[Company — read first]]) or
> *what exists* ([[Company Map]]). Written open: these are living principles, meant to be
> extended, not a closed creed. The fuller philosophical source is the design vault
> (`build-prep`: `context-06-the-foundation-laws`, the five invariants) — referenced here,
> not duplicated.

## The concept

**One entity, many faces, one brain.** This repo is a reactive **composition substrate** —
content lives at addresses, nodes fire when their inputs resolve, results persist and
trigger more. Over that one substrate sit faces that never fork it: the **runtime** (it
executes), the **MCP agent face** (an AI operates it), and now the **knowledge face** (it is
also an Obsidian vault — the documentation *is* the navigable self-model). Same brain
underneath. Adding a face extends the entity; it does not build a second system.

**It is built to be run and grown entirely by AI.** There are no human developers. Tim
commands; the crew (agents) build. So the repo is shaped to be *navigable and extensible by
an agent* — which is exactly why its self-description is load-bearing, not decoration.

**It is self-hosting.** Its first real use is *itself*: it reads its own codebase and
answers about it, and it grows its own capabilities from a request (governed). The map is
maintained by the system about itself. The thing being built and the first thing it operates
on are the same thing — construction is recursive.

**It is relational.** Modules are not a pile of parts; they relate through **seams** (the
contracts). The knowledge graph makes those relations *traversable* — so understanding any
part means following its links, not memorising an order. The relationships are the content.

## The principles (as embodied here)

Each is live in the repo today; the parenthetical points to where it bites.

1. **Path of least resistance.** Make the *correct* action the agent's *easiest* path. The
   registry is the source of truth; making something up is a failure equal to not acting; if
   needed info isn't registered, **ask**, don't fabricate. (root rules · [[Company Map]]'s
   PoLR section · the in-band authoring prompts.)
2. **One source.** Define a thing once and project it everywhere; never duplicate a
   definition across surfaces — including docs (describe relationally, link the single
   source, don't copy a list that will rot). (C2 node contract · [[Vault Conventions]].)
3. **Fail loud.** No silent failures, no silent fallbacks, no pretending success. Surface a
   problem, or abstain. (root rule 4 · the RHM abstains rather than confabulate.)
4. **Schema-additive, never breaking.** Extend with optional fields; a breaking change is a
   new version *beside* the old, never an edit-in-place. Existing graphs keep working.
5. **Governed self-modification.** The system changes itself only *additively*,
   *build-gated*, *git-revertible*, and *operator-approved* — the agent **proposes**, the
   operator **disposes**. Approval is governance, not a safety guarantee; the floors are the
   gate + error boundary + git-revert. ([[runtime — constitution]] self-mod.)
6. **Self-describing, self-maintaining.** The map regenerates its factual registry and a
   drift-check **fails loud** when a capability isn't reflected. Semantic truth of the prose
   is becoming enforced too — see [[Coherence Gate — Spec]].
7. **Relational navigation.** The knowledge graph *is* the self-model; the easiest way to
   understand a part is to follow its links. ([[Vault Conventions]].)
8. **One entity across time.** Coherent voice and memory across sessions and agents — the
   answer to "a thousand instances": entity-memory, no-repeat. (The corpus/twin work, when
   it comes, serves this.)
9. **Prove by use.** The acceptance suites are the convergence record; "no error" is not
   "works"; never claim done without fresh evidence. ([[Company State]] · `tests/`.)

## How to hold these

They are not a checklist to satisfy once — they are the **shape** every change should keep.
When a change would make one of them less true, that's the signal to stop. When a new
principle emerges from the work, add it here (open, expansion-welcome). This note is part of
the system it describes; keep it true the same way the constitutions are kept true.

## Read next
[[Company — read first]] (the rules) · [[Company Map]] (the structure) · [[Vault Conventions]] (the knowledge-space form) · [[Coherence Gate — Spec]] (how truth is enforced).
