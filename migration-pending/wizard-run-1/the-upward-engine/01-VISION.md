---
type: concept
register: descriptive
aliases: ["The Upward Engine — vision"]
tags: [company, vision, compositional-system, catch-all, ui, render-for-cognition]
status: draft
relates-to: ["[[The Upward Engine — hub]]", "[[Upward Engine — UI capability map]]", "[[Upward Engine — system state and locations]]"]
---

# The Upward Engine — the unifying vision

## One engine, two directions

The company is a compositional engine. Its familiar direction is **top-down**: `Principal → Domain → Intent → Proposal → Approval → Execution` — an intent resolves down into action.

The wizard, Dragnet, and recollection run that *same* engine in the **other direction — upward, as a catch-all**:

```
   raw, untrustworthy material (a project's files · huge data · conversation transcripts)
        │   MAP   — concurrent small models RENDER each piece (never judge), in parallel
        ▼
   typed projections / units  — many altitudes per item, each separately embeddable
        │   RELATE — embed into many spaces; cluster; find the face-value-hidden links
        ▼
   a navigable map  — nodes (items + projections + marks) + typed edges + clusters
        │   REDUCE — a reasoner (Claude / cloud) holds the distilled pattern
        ▼
   MEANING  — Tim sees the pattern, confirms/corrects, steers the next pass
```

This is not three systems. It is **one engine with an upward flow**, and the three "systems" are **chains** — configurations of the same primitives pointed at different corpora:

- **wizard-restore** — point it at *one scattered project* → reconstruct its real intent (not its lossy AI-echo artifacts) → walk it with Tim → rebuild it fresh. Applies to *every* project.
- **Dragnet** — the inverted catch-all over *huge data*, "pumping huge data up through layers of smaller models with the company and its brain." Tim's words: *one kind of chain in the same compositional system.*
- **recollection** — the catch-all over *conversation transcripts* → typed units (decisions, corrections, principles…) → cross-session, cross-project memory.

Same shape every time: **render-not-judge at the bottom; judgment (gold/relevance/trust) only later, over the aggregate; meaning at the top, reserved for Tim.**

## The UI is the institutionalised "look"

The wizard run's most expensive lesson — *look at the raw output before theorising; "the content is too big" is the last hypothesis* — generalises into the UI's whole reason to exist.

The upward engine runs a loop the wizard called **patterned visibility**: `run → look → see the pattern → choose the next move → repeat`. In that loop **Tim's perception is the reduce step** — *his brain is the algorithm*. The bottleneck is the *look*: at 5,000 files (let alone a real corpus) you cannot look by reading. So:

> **The UI exists to make the look cheap, fast, and spatial** — so the patterned-visibility loop can actually turn, and Tim's scarce reasoning is spent on *seeing and deciding*, not on reading or operating.

Everything the UI does is a kind of looking: watching the catch-all climb the tiers; seeing clusters form; moving through projection-spaces to spot the inversions; glancing at proposed marks and confirming. The interface *is* the renderer of the coordinate space the engine produces — *definition-is-position* made literal.

## What it does for Tim (the point of it)

- **Restores his projects.** Every abandoned project becomes legible — its real intent reconstructed and confirmed, ready to rebuild — through the same chain, for *any* project.
- **Cross-project omniscience.** Concepts pooled across all time and all projects; "merge these two projects"; what was decided, when, at every scale.
- **Navigate by meaning, not by name.** A file is a point in *many* spaces (principle, vocabulary, topic…). The relations that matter often *invert* face value (the `sequences ↔ wizard` link lives at the principle level, invisible to keyword or raw-text similarity). The UI is where those hidden links become visible and walkable.
- **Reserves the scarce thing — Tim's reasoning.** The cascade economics: code + local models + Claude are lavish; cloud is finite; **Tim is the scarce reasoner at the top.** The UI surfaces only what needs his eye — proposed marks and reconstructions *with evidence* — as fast confirm/correct decisions.

## The recursive seed

The engine's most natural first corpus is **the company's own scattered self** — which is exactly what this whole consolidation effort has been mapping by hand (the orienteering ledger is the v0 of the map the engine would produce). So Tim builds the UI **by using the engine on the project that is building it**: the systems describe their own development, the UI renders that, Tim steers from it. Building and using become the same act — the company's self-hosting spine, turned into a working surface. (Detail: [[Upward Engine — dogfooding plan]].)

## And it's all through the company MCP

The UI is not a separate app bolted on. It is **Tim's window onto the same verbs and chains the agents drive through the company MCP** — two faces, one brain. Agents operate the engine through the MCP; Tim operates *and sees* it through the UI; the chains underneath are identical. (recollection's recall, the Dragnet chain, and `session_recall` are all reachable through that one surface.)
