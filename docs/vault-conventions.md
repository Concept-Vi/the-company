---
type: convention
module: docs
aliases: ["Vault Conventions", "dual-repo convention"]
tags: [company, convention, knowledge-space, obsidian]
status: living
relates-to: ["[[Company Map]]", "[[Company — read first]]", "[[Coherence Gate — Spec]]"]
---

# Vault Conventions — the repo as a knowledge space

> **What this is:** the canonical definition of how `~/company` is **simultaneously a code
> repository and an Obsidian vault**. Read once; it governs the shape of every `.md` in the
> repo. It is itself written to this convention (it is its own first example).

## The principle

The repo already has two faces over one brain — the reactive **runtime** and the **MCP**
agent face. This adds a **third face on the same substrate: a knowledge face.** The *same*
markdown that instructs an AI agent (`AGENTS.md`, `MAP.md`, `STATE.md`) becomes, with
frontmatter and links, the **nodes of a navigable graph**. Obsidian reads the `.md` as
notes and the `.py`/`.tsx` as linkable files. Nothing is forked or duplicated — the
documentation *is* the knowledge graph.

**Why this serves the AI-operated principle.** An operating agent's path of least
resistance becomes *"follow the links."* Every claim carries its relations inline, so the
right context is reached by traversal, not by knowing a prescribed reading order. The
relational structure you navigate in Obsidian **is** the system's self-model.

## The rules (apply uniformly)

1. **Every folder has a constitution-note named `AGENTS.md`.** Not just the code modules —
   `tests/`, `panels/`, `docs/`, `canvas/app/src/`, `extensions/` too. The folder-note and
   the constitution are the *same* artifact, everywhere. An agent landing in any folder,
   and the vault graph, both get a self-description for free.

2. **Frontmatter on every note**, this schema:
   ```yaml
   ---
   type: constitution | map | state | convention | hub   # what kind of note
   module: nodes            # the folder it governs ("root" for the top level)
   aliases: ["nodes — constitution"]   # the unique vault link target (see rule 3)
   tags: [company, constitution, nodes]
   governs: [C2]            # contracts/invariants (C1–C8 / S1–S7) this folder implements; [] if none
   relates-to: ["[[Company Map]]", "[[runtime — constitution]]"]   # wikilinks to neighbours
   status: living
   ---
   ```
   Frontmatter drives Obsidian's properties + graph and is ignored harmlessly by an agent
   reading the body.

3. **Keep the `AGENTS.md` filename; disambiguate with `aliases`.** Nine-plus files are all
   named `AGENTS.md`, so a bare `[[AGENTS]]` is ambiguous — but the filename is the
   agent-facing convention and must not change. Each note's frontmatter therefore carries a
   **unique alias** (`"<folder> — constitution"`), and **all links use the alias**:
   `[[nodes — constitution]]`. The graph then shows meaningful node names, and the filename
   convention is preserved. (Em-dash ` — ` matches the vault's existing aesthetic.)

4. **`[[wikilinks]]` carry the relations.** In each constitution, link the modules it
   **calls** and is **called-by**, and its **contracts** — the seams you already document
   become *traversable*. An unresolved link (target not yet created) is fine; it marks a
   neighbour that exists or is coming.

5. **`MAP.md` is the Map of Contents** (alias `Company Map`). It is the vault home: the one
   picture, a rendered relationship graph, and a link to every folder-note. Do not create a
   parallel home note — one source.

6. **Relational descriptions, not enumerated lists that rot.** Describe *what a folder is
   for and how it connects*; do **not** hand-maintain a list that duplicates a live source.
   Where a folder's contents are already a registry (e.g. the node-types in
   `[[Company Map]]`'s auto-maintained REGISTRY block), **link to that single source**
   rather than copy it. Freshness of the prose is owned by the **[[Coherence Gate — Spec]]**
   (the commit-time check) — this knowledge layer expands the self-description surface, so
   it belongs in that gate's reference corpus.

## The two-vault boundary (do not collapse without a decision)

There are two distinct Obsidian vaults, on purpose:

- **This repo (`~/company`)** = the built **reality** — what exists, how it's structured,
  the constitutions of the running system.
- **`build-prep/` in the counterpart vault** = the design **intent** — the specs,
  decisions, open threads ([[Company Build Hub]], the contracts notes, the completion
  criteria).

Obsidian does not resolve links across vaults, so the two reference each other **by name in
prose** (a constitution may say *"spec: `Self-Coding Subsystem — Completion Criteria` in
build-prep"*), not via live `[[ ]]`. Reality-vs-blueprint is a meaningful boundary; merging
them is a larger decision, not a default.

## Obsidian housekeeping

Open `~/company` as a vault in Obsidian. The `.obsidian/` folder it creates holds shared
settings (trackable) plus per-user workspace state (gitignored — see `.gitignore`).

## One line

The repo's documentation, decorated to this convention, *is* a navigable knowledge graph —
the same substrate an agent executes, an operator reads, and the graph view shows as the
system's own self-model.
