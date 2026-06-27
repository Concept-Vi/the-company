---
type: terrain-entry
name: docs
register: descriptive
aliases: ["docs", "archaeology-docs"]
status: unconfirmed
coverage: { files_read: 5, files_total: 192, last_read: 2026-06-26 }
relation: resource
kind: data
path: /home/tim/docs
created: 2025-08-06
last_active: 2026-03-27
size: 2.8M
git_remote: none
secrets: false
move_intent: none
prospected-for: ["[[company]]"]
relates-to: ["[[world-keeper-profile]]", "[[creations]]", "[[universal-mechanics]]", "[[ai-systems-strategic-overview]]"]
era: 2025-08 → 2026-03
themes: [universal-composition, pattern-synthesis, agent-rpg-narrative, vi-integration, cross-session-rebirth]
concepts: [referential-property-manifestation, registry-mediated-late-binding, VECO-circuit, environment-enforced-coordination, autonomy-ladder-gating, session-as-graph, reference-protocol, six-principles]
tags: [mcp, memory, fabric]
---

# docs

## What it is
A mixed doc tree whose substantive payload is `/home/tim/docs/archaology/` (misspelled) — the artifact trail of a gamified multi-agent **"archaeology team" expedition**. A swarm of Claude agents were given RPG personas (The Librarian, a World Keeper, Quest Master Twins, Code Archaeologists, an Integration Weaver, a Crafter, a Cartographer, a Scout, a Keeper Council) and dispatched across four "Sites" to *excavate design patterns* out of Tim's real systems (Project Vi, Conversation Intelligence transcripts, the Supabase/Vi-Sync graph) and synthesize them. Beneath the fiction it is a **pattern-mining + architecture-spec exercise**: extract Tim's recurring primitives, prove they collapse to one mechanism, and write a spec to wire them into Project Vi. The other two subtrees are inert: `design-system/projects/` is **empty** (placeholder dirs only); `geepers/` is an **unrelated** 7-file MCP-documentation bundle (a "Geepers MCP ecosystem", 2025-12-23).

## Key ideas worth mining
- **Universal Composition (the spine)** — *"The 24 patterns synthesized in Quest #175 collapse to this single primitive: properties reference behaviors through registry resolution"* (`archaology/Universal_Composition_Implementation.md:16`). Implemented as a Universal Circuit Engine with a 5-layer stack `L1 Configuration → L2 Reference → L3 Resolution → L4 Execution → L5 Observation`, each layer a typed interface contract. An embryonic, RPG-costumed version of the Company's "everything-is-a-variable that resolves against a registry" — late binding, no hardcoding, registry-mediated behavior resolution. Quest #175 is glossed verbatim as Tim's law: *"identifying relational primitives once and reusing everywhere."*
- **Pattern Synthesis — the Fivefold Convergence** (`PATTERN_SYNTHESIS_001.md`, framework name *"Environment-Mediated Agent Coordination Through Late-Bound Property Manifestation"*): (1) **Environment-Enforced Coordination** — "the database IS the coordination layer", no central coordinator; (2) **Autonomy-Ladder Gating** — earned trust L1–L5 (Observer→Assistant→Collaborator→Delegate→Autonomous); (3) **Session-as-Graph** — a session is a traversable graph, "graph IS the workflow engine"; (4) **Property-Encodings** — data values drive visual/behavioral manifestation, registry-driven; (5) **Reference-Protocol** — `reference://{type}/{id}` for runtime late binding. Distilled into **Six Principles**: Environment-as-Source-of-Truth, Trust-as-Permission-Architecture, Graph-as-Primary-Interface, Late-Binding-Architecture, Primitives-over-Frameworks, Convergence-Drives-Emergence.
- **The VECO circuit, mapped** — Part 6 maps the 5 layers onto `Principal | Domain | Intent | Proposal | Approval | Execution | Observation` — Tim's exact relational circuit. The decision→proposal→approval→execution wire predates the Company under this name.
- **The REBIRTH / phases narrative** — agents persist identity via `REBIRTH_CHECKPOINT.md` and "reincarnate" across context loss (literally tracking some twins as "DECEASED — Context death — no rebirth"). An early mythologized articulation of the Company's cross-session continuity / agent-memory problem.
- **Vi Integration ("two worlds" gap)** — `PHASE_2_VI_INTEGRATION_ARCHITECTURE.md` frames "Archaeology Prime (pattern discovery)" vs "Project Vi (pattern execution)" with NO BRIDGE, and designs one (a `vi-pattern-ingest` MCP, Pattern-to-Graph Mapper, registry extension). It cites the real Vi tree at `/mnt/c/00_ConceptV/06_Project_Vi/` — the fiction was grounded in Tim's actual system.

## How it relates conceptually to the Company
A **direct early articulation of the Company's spine.** Archaeology's **Referential Property Manifestation** (`property → registry lookup → resolved behavior`) and **Reference-Protocol late binding** ARE the Company's everything-is-a-variable / registry-resolution idea in embryo. The VECO circuit mapped onto the 5 layers is verbatim Tim's relational flow — the decision→proposal→approval→execution wire by another name. "Environment-as-Source-of-Truth" → introspective-data / shared-substrate law; "Session-as-Graph" → graph-driven coordination; "Autonomy-Ladder L1–L5" → the propose/approve gating now in the decision-wire. `relation: resource` — mineable conceptual ancestor and pattern catalog, scaffolding-not-spec, never wired into the running Company.

## When / where
Created 2025-08-06 (oldest file `archaology/unknown_scattered_4/orchestration_redesign.md`); last active 2026-03-27 (`design-system/` dir mtime; archaeology content tops out 2026-03-02). Path `/home/tim/docs`, 2.8M, 192 files, no git anywhere under the tree. Read 5 of 192.

## Notes / evidence
- Read in full: `archaology/Universal_Composition_Implementation.md`, `PATTERN_SYNTHESIS_001.md`, `PHASE_2_VI_INTEGRATION_ARCHITECTURE.md`, `agents/the_librarian/memory/REBIRTH_CHECKPOINT.md`, `characters/the-librarian.md`. Partial: `site_3/genesis_event_playbook.md`, `geepers/README.md`.
- Top-level `Rebirth`/`REBIRTH-002`/`Entry`/`EOF` files are 0 bytes (empty placeholders — the real REBIRTH content is `agents/the_librarian/memory/REBIRTH_CHECKPOINT.md`). Many `*:Zone.Identifier` files (Windows-download cruft) inflate the count.
- NOT read: `PHASE_2_IMPLEMENTATION_ROADMAP.md`, `site_3/findings/` quest reports, `crafter_workspace/` TS (autonomy_ladder, quest_generation, fivefold_framework), `keeper_relations_workspace/`, `unknown_2/vi-visual-suite-findings/` (the raw mined-pattern corpus).
- **[[world-keeper-profile]]** is from this SAME archaeology-team narrative — the World Keeper is the L5 spawning authority cited throughout (`REBIRTH_CHECKPOINT.md:177` "spawned_by → World Keeper"). Its own file does not survive under this tree, so that profile is the sibling record.
- Honest caveat: the entire archaeology narrative is in a gamified fictional register (quests, stats, NPCs, "the Living World breathes"). All "COMPLETE / Operational / LIVE" status claims are in-fiction, not verified execution; the implementation specs reference `/src/universal-composition/` and `/mnt/c/00_ConceptV/06_Project_Vi/` files not verified to exist.
