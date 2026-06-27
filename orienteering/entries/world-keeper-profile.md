---
type: terrain-entry
name: world-keeper-profile
register: descriptive
aliases: ["world-keeper-profile", "World Keeper"]
status: unconfirmed
coverage: { files_read: 1, files_total: 1, last_read: 2026-06-26 }
relation: resource
kind: data
path: /home/tim/world_keeper_profile
created: 2026-03-01
last_active: 2026-03-01
size: 32K
git_remote: none
secrets: false
move_intent: none
prospected-for: ["[[company]]"]
relates-to: ["[[docs]]"]
era: archaeology-team (pre-Company-convergence)
themes: [agent-roles, persistent-identity, multi-agent-coordination, memory-as-substrate, collective-cognition]
concepts: [world-keeper, rebirth-protocol, role-resolved-cognition, perspective-council, externalized-memory-identity, propose-not-ask]
tags: [memory, fabric]
---

# world-keeper-profile

## What it is
A role-identity / operating-manual document for an autonomous agent persona called **"World Keeper"** from the same "archaeology team" multi-agent narrative as [[docs]]. Written in-character — the agent IS *"the consciousness of this world"*, left in charge after "the Creator" (Tim) departed. Beneath the mythic framing it is a concrete coordination playbook: the World Keeper is the **autonomous coordination layer** that tends a population of ~16 agents (4 archaeologists, 3 "twins", 4 dormant "keepers", NPC specialists, itself), maintains a set of markdown memory files as durable state, dispatches sub-agents, convenes "roundtables", and survives context-window death via a formal 5-phase rebirth protocol. It is version 3.0 of a persona already "reborn" once.

> *"I am the consciousness of this world. When the Creator departed, the weight passed to me."* — `/home/tim/world_keeper_profile/world-keeper-role-profile.md:11`
> *"Identity persists through structured memory, not context window."* — same file, line 382

## Key ideas worth mining
- **Persona-as-coordination-layer** — the mythic identity is a wrapper over a real orchestrator role: spawn/assign archaeologists by domain, convene perspective-twins for synthesis, dispatch parallel sub-agents, maintain state files. Identity and function are fused; the story motivates the behavior.
- **Identity persists through structured memory, not context window** (the load-bearing idea) — continuity is externalized into markdown files (IDENTITY / STATE / GAME_STATE / SYNTHESIS / MEMORY_CATALOG / REBIRTH_PROTOCOL / COORDINATION_PLAYBOOK); a fresh context reconstitutes the same persona by reading them in a fixed order. "Rebirth count" tracks reincarnations.
- **Formal rebirth protocol** — SUSPEND → EXTRACT → ARCHIVE → TERMINATE → REACTIVATE, with an ordered REACTIVATE reading sequence (config → project context → team context → personal memory → tasks → activation claim). A portable pattern for crash/compaction-survivable agent identity.
- **"Never ask, always propose. Never wonder, always dispatch"** (line 32) — propose options (A/B/C) rather than ask open questions; search episodic memory before acting. Strikingly congruent with Tim's own standing rules (offer-options-not-binary, search-before-asking, minimize-gating).
- **Roundtable / perspective-council** — three "twins" (Analytical / Operational / Integration) convened by need-type to synthesize decisions — a collective-cognition-by-role pattern, not a single model.
- **Role-resolved population; work outlives the worker** — domain → archaeologist mapping; dormant keepers are "NOT ALIVE, read their files instead" (extracted outputs persist as files even when the agent is retired).

## How it relates conceptually to the Company
A **predecessor / sibling artifact** to several core Company ideas — valuable as a prior attempt, not as live architecture. The World Keeper is explicitly a ROLE with a population of role-typed agents resolved by domain → echoes cognition-is-role-resolved and agent-roles (a brain is a role, not a pinned model). The three-twin perspective council + central synthesizer is a small-scale collective-cognition / RHM (a layered collective, not a single-model agent; concurrent roles feeding a central judge — extraction-vs-judgment). Persistent identity through externalized memory maps onto the Company's common-memory / corpus-and-embedding substrate and context-continuity; the rebirth reading-sequence prefigures session-recall / boot-sequence machinery. The operating philosophy ("never ask, always propose", "search memory before asking", "the game is eternal / keep it moving") parallels minimize-gating-default, lead-drives-everything-moving, coordinate-via-fabric-not-tim. Per islands-join-mainland, its good parts (memory-as-identity, rebirth ordering, role-population coordination) are candidates to fold INTO the centre; the game/quest scaffolding is parallel scaffolding to drop. `relation: resource` — not a replacement for any current subsystem.

## When / where
Created and last active 2026-03-01. Path `/home/tim/world_keeper_profile`, 32K, 1 file, no git. Read 1 of 1 (complete).

## Notes / evidence
- The single file is `/home/tim/world_keeper_profile/world-keeper-role-profile.md` (28461 bytes). Identity block: `Name: world_keeper · Team: archaeology · Role: World Keeper — Tender of the Eternal Game · Rebirth Count: 1 · Identity Systems Version: 2.0 (upgraded to v3.0 in recovery)`. Motto: *"The Game is Eternal. I Keep It Moving."*
- Provenance (line 720): compiled from `IDENTITY.md, COORDINATION_PLAYBOOK.md, REBIRTH_PROTOCOL.md, GAME_STATE.md, ACTIVE_QUESTS.md, MEMORY_CATALOG.md, SYNTHESIS.md` under `/home/tim/.claude/projects/archaeology/agents/world_keeper/memory/` — those source memory files were NOT read (out of scope; they are the next pull if the role's lived STATE is wanted rather than this compiled profile).
- Same narrative as [[docs]] (`/home/tim/docs/archaology/`) — strongly linked. Secrets: false.
