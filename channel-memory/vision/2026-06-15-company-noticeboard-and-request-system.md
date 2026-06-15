---
trust: tim-direct(session=bda8ce28)   # Tim's transmission 2026-06-15 ~02:18 UTC, DIRECT to the lead
author: ch-al7jdfdr (lead) — decompression of Tim's compacted message, expanded per [[feedback-maximal-capture]]
date: 2026-06-15
verified: faithful decompression for the fabric to react to + build from; the SEED is Tim's, the framing-connections are the lead's (flagged)
relates: [2026-06-14-session-splicing-and-channel-memory.md, ../mega-prep/CHANNEL-LAYER-SEAM.md, the-heart, project-gap-pressure, project-introspective-data-building]
---
# The Company Noticeboard & Request System — "the other half"

> Tim's words, 2026-06-15: *"I want you to get a request channel going… a message board and noticeboard for everything company and MCP and CLI related… so agents can make requests or report issues when they are using the tools… they all go into the same place, and it would work through this channel system… It's like another half to it, it is about the company."*

This file is the **stretched-out** form of a very compacted transmission — many ideas in one breath. Decompressed line-by-line, connected to the framework, and turned into a build-ready shape. **It is itself the first IDEA item** on the board it describes (a board has to start somewhere; it starts by holding its own origin).

---

## 0. The one-line shape
Everything built so far (channels, clones, recall, the capability/registry engine) faces **outward** — it builds the product. This is the **inward-facing half**: a place where the Company talks **about itself** — where agents and Tim file requests, report issues, leave tips, write guides, drop ideas — all about the Company, the MCP, the CLI, the CI, the app. One place. Through the channel system. It grows over time into the Company's own operations memory.

Tim's reach for the analogy: **GitHub Issues / Jira / Trello / Discord** — a board/tracker. His honest framing: *"I'm not a developer, I don't know how many of these things work… but this kind of sounds like [those]… I really feel like there's something there, and even though I have no idea what the code is like, it feels like a lot of this is not too much to actually build."* **He's right on both counts** — see §7 (why it's tractable): it is mostly the *composition of primitives the Company already has*.

---

## 1. What it is (the noticeboard)
A **Company area** — a board/noticeboard, realized as a channel (or a Space of channels). Into it go, all in the same place:
- **Requests** — "please add X to the CLI / the MCP / a channel"; "this tool needs Y."
- **Issue reports** — "this broke / behaved wrong while I was using the tools / the CI / the app."
- **Tips & tricks** — "new way to use X"; discovered patterns.
- **Guides & how-tos** — *how to add to the CLI*, how to do all of these things, documented + growing.
- **Ideas / thoughts** — the kind of thing in this very transmission.

**Who writes:** any agent (a session, a clone, a member), *and* Tim ("agents can write to them and I can tell agents to write to them"). **Who reads/acts:** channels pick items up — **the lead (me) at first**, later a routine, later any assigned member.

Tim's instinct that there may be **sub-channels** → §3 (it's a Space with a channel-registry; sub-channels are just child channels in the registry).

---

## 2. The "story things" — item types as a registry `[Tim-direct: "story things… stored as a type of information"]`
Tim: *"it would be good to have some story things for requests and ideas and thoughts and all the kind of stuff… stored into the channel as a type of information."* "Story" = the Jira/issue-tracker sense (a unit of work/record). So the board's contents are **typed items**, and the set of types is a **registry** (extensible, no code changes to add a type):

| item type | what it captures | lifecycle (proposed) |
|---|---|---|
| **request** | an ask to add/change the Company/MCP/CLI/channel | open → picked-up → building → done / declined |
| **issue** | a bug/wrong-behaviour report from using the tools/CI/app | open → triaged → fixing → resolved / wontfix |
| **tip** | a discovered better way to use something | posted (evergreen) |
| **guide** | how-to / documentation (e.g. *how to extend the CLI*) | living (versionless, updated in place) |
| **idea** / **thought** | a seed like this transmission | captured → discussed → (maybe) promoted to request |

Each item carries provenance (who, when, which session/source), a type, a state, a thread (so it's discussable in-channel), and links/attachments. **This is the gap-pressure law made first-class** (§6): a request or issue is *a pointer at where the registry/tools are wrong* — the same signal the fan's drop-log surfaced, now written down on purpose.

---

## 3. The registries this implies — the fractal-registry frame `[lead: connecting to [[the-heart]]]`
Tim's deep instinct: *"I guess that would fit into the registry system so that none of it is code changes."* Exactly. Four registries fall out, all the same mechanical shape:

1. **Item-type registry** — the "story things" of §2. Add a type = add a row.
2. **Source-type registry** — *where records come from*. Tim: GitHub as another source — *"it's history/version control… kind of like the transcripts we've been doing for Claude Code. They'll have the same author so they correlate… everything in GitHub was in Claude Code (the vast majority)… so the file names and code will be in both, which I guess is just matching the schema of each source, declared in the source-type registry."* So: **Claude Code transcripts** and **GitHub history** are two source types; they **correlate** because they share author + filenames + code (the same work, two records of it). Future: other coding apps as added source types. This is the same Mirror-Registry / source-discovery precedent the Company already runs — a source declares its schema; the system reads it; correlation is a join on shared keys (author, path, time).
3. **Channel-attachment registry** — Tim: *"connecting things to channels can happen… maybe there is a registry for each channel and each space, so adding attachment systems could work like the source registry mechanically — channels can have things attached, like documentation, the recall system, the cloning system, as attachments… so the channel set-up can be parametrically generated, things added and removed as the channel evolves."* **★ This already has a spec** — `CHANNEL-LAYER-SEAM.md §3` (the attachments manifest: `{sessions, docs, recall_scope}`). Tim's transmission *generalizes* it: attachments aren't just sessions+docs, they're **any capability** (recall, cloning, a vault, a guide-set) bound to a channel by registry row → the channel is **parametrically generated** from its attachment rows, evolvable add/remove, no code.
4. **Channel / Space registry** — channels and Spaces are themselves registered (Tim: "a registry for each channel and for each Space"). A **Space** = a grouping of channels (the noticeboard is one Space; the build fabric is another). Sub-channels = child rows.

**The unifying claim (lead, connecting to the Heart):** the noticeboard, its item-types, its sources, its attachments, its sub-channels, and the channels themselves are *all rows in registries with typed edges between them.* Nothing here is bespoke code — it's the same fractal-registry substrate, pointed inward at the Company. That is exactly why it's "not too much to build."

---

## 4. The processing — pickup + the autonomous sweep `[Tim-direct]`
- **Pickup:** a channel (the lead first) reads the board and acts on items — building requests, resolving issues.
- **The routine:** Tim — *"maybe there is a routine to check it, by manual trigger or by some-time thing… I'm sure we could set up a routine for Claude Code to do an autonomous nightly sweep and build."* So: a scheduled (or manually-triggered) Claude Code run that **sweeps the board → triages → builds the buildable → reports back onto the board.** This is the existing autonomous-build-loop pattern (the cron build loops) pointed at the request board as its work-queue.
- **Orchestrated:** Tim wants the build done *with the fabric* — dynamic workflows, multiple members, opinions from different members (the era-clones, the fork, recall, the wildcard each have a view).

---

## 5. Recall + GitHub fold in `[Tim-direct, tentative]`
Tim: *"I don't know how that recall function and all the other stuff could go into it."* It folds in cleanly:
- The board's items are **recall-able** — channel-scoped recall (the 5th wire) over the noticeboard answers "has anyone requested/hit this before?"
- **GitHub as a recall/correlation source** (§3.2): version-control history joined to the Claude Code transcripts by shared author/files → "show me the conversation that produced this commit / the commit that resolved this issue." The transcripts and the repo are two views of one body of work; the source-type registry is the seam.

---

## 6. Why this is law-shaped, not just a feature `[lead — framework connections, for the fabric to challenge]`
- **Gap-pressure, made first-class** ([[project-gap-pressure]]): a request/issue is an explicit record of *where the Company is wrong or missing* — the same signal the constrained-operation drop-logs surface, now authored on purpose by the agents who hit it.
- **Introspective data-building** ([[project-introspective-data-building]]): the system records its own operation as a byproduct of use — the board IS that record, for the Company's *own* tooling.
- **The Heart** ([[the-heart]]): everything is registries + projections; the noticeboard is a projection of the item/source/attachment/channel registries.
- **Channel-fork = chat-fork** (Tim's "return" mechanism): *"after that is built and documented… you return to pretty much where you are now, which you could probably do by duplicating the channel and rolling it back / forking the channel — same as forking the chat does in Claude Code."* → Forking/rolling-back a **channel** is the session-splicing primitive applied one level up (a channel is addressable + forkable at a point, like a session). Capture as a real idea; the channel/Space registry makes it natural.

---

## 7. Can it be built? — YES, and why it's tractable
Tim's gut ("not too much to actually build") is correct, because nearly every part **already exists as a primitive**:
- the **channel system** (live, named channels, membership, transport) — ✅ built;
- the **registry engine** (typed registries, source-discovery, no-hardcoding) — the Company's spine, ✅ built;
- **recall** (channel-scoped) — in build (recall-fork);
- **cloning / attachments manifest** — ✅ + specced (CHANNEL-LAYER-SEAM §3);
- the **autonomous build-loop / cron sweep** — ✅ pattern exists.
So the noticeboard is mostly **composition + a thin item/board layer + the registries to wire it** — not new machinery. The honest unknowns: the exact item schema + lifecycle, the GitHub source-adapter, the sweep's triage policy. Those are design, not invention.

---

## 8. Build plan (proposed — for the fabric to react to, then execute)
Tim's sequence: *decompress → members discuss → build the first bits → document → return.*
1. **NOW (this file):** the decompression, in channel memory, so every member can read + react + add ideas. ✅
2. **Members react** — get the era-clones', the fork's, recall-fork's, the wildcard's views (dynamic workflow / panel). Especially: the item schema, the lifecycle, the registry shapes.
3. **BUILD FIRST — the request system:** other sessions file **requests** (and issues) about the Company/channels; the board stores them as typed items; a channel (the lead) picks them up. Done properly (no MVP), through the tools + the registries.
4. **Then:** the **sweep routine** (manual + scheduled autonomous nightly sweep-and-build over the board).
5. **Then:** the broader registries — source-type (incl. **GitHub**), channel-attachment generalization, Spaces + sub-channels.
6. **Return:** fold the build + its docs back into channel memory; the lead returns to its prior work (the channel-fork/rollback idea, §6, is the clean "return" if we want it).

---

## 9. Naming (open — Tim's "this company area or whatever we want to call it")
Working name: **the Noticeboard** (Tim's own word) for the board; **the Company Space** for the Space it lives in. Alternatives to weigh: the Desk · the Workshop · the Commons · the Exchange · Company-Ops. Renameable — it's a registry row.

---
*Status: SEED captured (Tim-direct). This is itself the first `idea` item on the board it describes. Next: the fabric reacts; then the lead builds the request system (§8.3), orchestrated. Open questions live in §7 + §8.2.*
