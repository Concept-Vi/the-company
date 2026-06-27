---
type: convention
module: docs
register: prescriptive
aliases: ["Vault Conventions", "dual-repo convention", "the vault convention"]
tags: [company, convention, knowledge-space, obsidian]
status: unconfirmed
coverage: { files_read: all, files_total: all, last_read: 2026-06-26 }
relates-to: ["[[Company Map]]", "[[Company — read first]]", "[[Concepts and Principles]]"]
governed-by: ["[[Coherence Gate — Spec]]"]
---

# Vault Conventions — the repo as a knowledge space

> **What this is:** the canonical definition of how `~/company` is **simultaneously a code
> repository and an Obsidian vault**. It governs the shape of every `.md` in the repo. It is
> written to its own convention (its own first example). *Fused 2026-06-26* from the original
> repo-self-description convention and the orienteering terrain-ledger schema — two designs for
> two purposes (describing the system from inside; mapping the terrain from above), now one.

## The principle

The repo has faces over one brain — the reactive **runtime**, the **MCP agent face**, and a
**knowledge face**: the *same* markdown that instructs an agent becomes, with frontmatter and
links, the **nodes of a navigable graph**. Nothing is forked — the documentation *is* the
self-model. An operating agent's path of least resistance becomes *"follow the links."*

Two kinds of note live on this one substrate:
- **prescriptive** notes — *rules / how to build* (constitutions, this convention, contracts). Binding.
- **descriptive** notes — *a map of what is* (the MAP, STATE, and the terrain entries in `orienteering/`). Reporting, not binding.

Every note declares which it is (`register:`). This is the **note-scale version of the two-vault
boundary** below (reality vs intent) — so "is this binding, or just describing?" is always answerable
from a field, and a descriptive map is never mistaken for a blueprint.

## Scope — what this schema governs

This schema governs the **self-description / knowledge-graph notes**: the constitutions (`AGENTS.md`),
the maps (`MAP.md`, `STATE.md`), this convention, concept notes, hubs, and the `terrain-entry` ledger.
**Working documents** — `build-prep/` specs, `channel-memory/` items, `foundation/exchanges/`, generated
artifacts — keep their **own** frontmatter and their own lifecycle vocabulary (a build doc's
`status: building|planned|live` is *build state*, set by its authors — not the confirmed-lifecycle field
below). The convention *recommends* they carry `aliases` (so the graph stays navigable) but does not
force `register`/`coverage` on them. The strict fields below are **required on self-description notes,
recommended elsewhere.**

## The frontmatter schema

**Shared by every self-description note:**
```yaml
type:      # constitution | map | state | convention | concept | hub | terrain-entry | terrain-index | …(open)
register:  # descriptive | prescriptive   (which kind of note this is)
aliases:   ["<unique vault link target>"]   # links target the alias, never the bare filename
tags:      [company, …]                      # cross-cutting themes only
status:    # CONFIRMED lifecycle only — default `unconfirmed`. See "Status" below.
coverage:  { files_read: <n|all>, files_total: <n|all>, last_read: <YYYY-MM-DD> }
# typed relations — see "Relations" (zero or more; each key is a relation KIND, values are [[aliases]])
relates-to: ["[[…]]"]
```

**`type: constitution` (folder-notes) add:**
```yaml
module:  nodes            # the folder it governs ("root" for the top level)
governs: [C2]             # contracts/invariants this folder implements; [] if none
```

**`type: terrain-entry` (orienteering ledger) add:**
```yaml
relation:    # company | external | connected | candidate | resource   (orbit membership — see orienteering)
kind:        # (for external) work | data | config | engine
path:        /home/tim/…   # absolute, always
created:     <YYYY-MM-DD>   # earliest evidence
last_active: <YYYY-MM-DD>   # latest evidence (the thing's own mtime — a fact, not a judgment)
size:        <human>
git_remote:  <url|none>
secrets:     true|false
move_intent: none | into-company | delete | archive | done
```
> Note the two different "relation" senses, kept distinct: **`relation:`** (a terrain-entry field) =
> *orbit membership* (is this the company, external, connected, …); the **typed relation keys** below
> = *graph edges* between notes. Membership is a category; edges are links.

## Relations — many typed link kinds, not one

A relation is expressed by a **frontmatter key whose name IS the relation kind**, with a list of
`[[alias]]` targets. Use as many kinds as apply; the vocabulary is **open** (a new key = a new edge
kind). Seed vocabulary:

| Kind | Means | Typical on |
|---|---|---|
| `relates-to` | generic neighbour (fallback) | any |
| `calls` / `called-by` | runtime call edge | constitutions |
| `governs` / `governed-by` | a contract/invariant or the gate | constitutions, convention |
| `part-of` / `contains` | containment | any |
| `depends-on` / `depended-on-by` | hard runtime dependency | terrain engines |
| `launched-by` / `launches` | a process/service launches this | engines ← systemd |
| `indexes` / `indexed-by` | a store indexes a corpus | corpora ↔ recall index |
| `data-of` / `data-store-for` | code ↔ its external data store | recollection ↔ its data |
| `derived-from` / `produced` | provenance | prototypes, foundation outputs |
| `aimed-at` | being pointed at a goal (not yet wired) | vi-visual-bridge → front-end |
| `prospected-for` | a resource mined for ideas by | resource entries |
| `supersedes` / `superseded-by` | lifecycle replacement | any |

All targets use the **alias** (e.g. `[[runtime — constitution]]`, `[[corpora]]`), never the bare
filename — many files share a name (`AGENTS.md`), so a bare `[[AGENTS]]` is ambiguous. An unresolved
link is fine: it marks a neighbour that exists-elsewhere or is coming.

## Status — confirmed only

The confirmed-only rule applies to **`terrain-entry` notes** (descriptive maps of *external* things whose
liveness is a judgment the catalogue can't make). For a terrain-entry, `status` carries a **confirmed
lifecycle judgment, and only Tim confirms it.** Agents and automation may set **only `unconfirmed`** — the
default. (A constitution's or a build-doc's `status` is a *different* field — the note's own build/lifecycle
state, set by its authors: `living`, `building`, `planned`, etc. That is legitimate and untouched.) They must NOT assign `live`/`dormant`/`dead`/`superseded`
by inference; whether something is alive or dead is a judgment about *intent*, which the catalogue
cannot know. Factual observations that *look* like status are recorded as facts, not status:
emptiness is `coverage.files_total: 0`; last-touched is `last_active`; a stopped timer is stated in
the body. `status` stays `unconfirmed` until Tim sets it. (There is no `empty` status.)

## Coverage — honesty about what was actually read

Every **terrain-entry** carries `coverage: { files_read, files_total, last_read }` — it may never
silently imply completeness: if 5 of 1,863 files were read, it says so, and `last_read` dates the
verification. Other self-description notes carry `coverage` **when there is a verification to cite**
(a constitution may instead point at the suite that proves it via `governs` + `tests/`); it is required
on terrain-entries, optional elsewhere. This ties the knowledge layer to **prove-by-use**.

## The rules (apply uniformly)

1. **Every folder has a constitution-note named `AGENTS.md`** (the folder-note and the constitution
   are the same artifact) — code modules and `tests/`, `docs/`, `orienteering/`, etc. alike. Body
   format in practice: **Is · Guarantees · Where new things go · To extend · Seam · Never.**
2. **Frontmatter on every note**, per the schema above.
3. **Keep the `AGENTS.md` filename; disambiguate with `aliases`; all links use the alias.** Em-dash
   ` — ` matches the vault aesthetic (`[[nodes — constitution]]`). This applies to generated content
   too: even an id-named note (`item-<hex>.md`) must carry a meaningful alias + title, or the graph
   is unnavigable.
4. **`[[wikilinks]]` carry relations, typed by key** (see Relations). The graph is the self-model.
5. **`MAP.md` is the one Map of Contents** (alias `Company Map`) — the single vault home. Do not
   create a parallel home. A region (like `orienteering/`) may have a **sub-map index** that is
   *linked from* MAP, not a competing home.
6. **Relational descriptions, not enumerated lists that rot.** Describe what a thing is *for* and *how
   it connects*; link the single source rather than copy a list. Freshness is owned by the
   **[[Coherence Gate — Spec]]** (commit-time check; structural half live via `tests/drift_acceptance.py`,
   semantic half designed in `build-prep/coherence/`).
7. **The knowledge face must not depend on the Obsidian app.** Agent-facing value rests on
   **frontmatter + a generated/maintained index + greppable wikilinks** — all readable from raw files.
   Dataview, `.base`, canvas, graph view, and our own future front-ends are **upside that lights up
   when a renderer attaches** — never the only way to read the data. (Tim does not open Obsidian; the
   app may be run periodically/headless only for link-auto-update + device sync.)

## The two-vault boundary (do not collapse without a decision)

- **`~/company`** = the built **reality** + the terrain map of where the Company physically lives
  (`orienteering/`). Descriptive + the prescriptive constitutions of what's built.
- **`build-prep/` (and the counterpart vault)** = the design **intent** — specs, decisions, open
  threads. Prescriptive-of-the-future.

Obsidian does not resolve links across vaults, so they reference each other **by name in prose**, not
live `[[ ]]`. Reality-vs-intent is meaningful; merging is a decision, not a default.

## Obsidian housekeeping

There is **one vault: `~/company`** (do not create nested `.obsidian/` folders in subdirectories — a
region is a folder within the one vault). When the vault is opened in Obsidian, the `.obsidian/` it
creates holds shared settings (trackable) + per-user workspace state (gitignored — see `.gitignore`).

## One line

The repo's documentation, decorated to this convention, *is* a navigable knowledge graph — one
substrate an agent executes, an operator reads, and (when a renderer attaches) a graph view shows as
the system's own self-model; descriptive maps and prescriptive rules are distinguished, statuses are
only ever confirmed, and no note pretends to a completeness it didn't verify.
