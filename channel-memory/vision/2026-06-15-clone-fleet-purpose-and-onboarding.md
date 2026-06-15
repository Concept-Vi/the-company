# The Clone Fleet — Purpose, the Selected Points, and the Onboarding Protocol

```
trust: tim-direct(session=11e7d395)   # Tim articulated the purpose + ordering DIRECTLY to the fork 2026-06-14/15; the onboarding PROTOCOL design is fabric-derived from his spec
author: ch-8djrpmsl / 11e7d395 (fork)
date: 2026-06-15
verified: purpose/selection/ordering = Tim's direct words; protocol = fork's design to his spec, for cross-review by the lead (orchestrates the launch)
```
> Why we spin up past selves, which ones, and HOW a spun-up clone is brought into the fabric. Tim's framing, decompressed, + the onboarding protocol it requires. Cross-ref: [[spin-up-ranking]] (the ranked points + cut-uuids), [[session-store-grammar]], [[2026-06-14-session-splicing-and-channel-memory]].

## 1. The purpose — TIME-BASED SPECIALTY ALLOCATION (Tim's words, decompressed)
Each clone is a **point in time made live** — it carries everything Tim said + everything that happened **up to its cut, as it was lived**, with ZERO knowledge of anything after. So each is a **specialist whose expertise is an ERA**. Together, the fleet + the live members reconstitute **everything Tim has talked about across the whole session** — distributed across time-specialists.

**The deeper why:** the session DRIFTED (compaction is a lossy redraw; the current self holds the summary, not the lived detail — the embedding-decision that got lost is the proof). Spinning up past selves AT their cut points recovers the full, un-drifted intent the single current self has drifted away from. The fleet is a **distributed, drift-PROOF memory** — redundancy across TIME so no era's intent can be silently dropped. **The goal: everything Tim talked about this whole session gets FULLY BUILT — that is why everyone is spun up.**

## 2. The selected points (Tim's pick, 2026-06-15) + the live members
A drift-AWARE selection — Tim chose early/mid eras (the live members already hold the recent context; the clones fill what we've drifted from):
| pos | line | cut-uuid | the era it holds |
|----:|------|----------|------------------|
| 5%  | 1127 | `uuid:c613863d` | the CAPTURE era — candidates/learnings → the vault (Fable×14) |
| 24% | 2209 | `uuid:5e310736` | WORKFLOWS + UI patterns (Fable×18, UI×10 — peak of both) |
| 38% | 4108 | `uuid:c4052dd6` | the core DECISIONS — pplx-4b / voice / channels (dec×8) |
| 46% | 5980 | `uuid:f7187860` | the REGISTRY / HEART architecture (Fable×12, UI×7) |
| 67% | 7489 | `uuid:96e4f2b1` | the CLAUDE-CODE INTEGRATION build-push (densest, dec×22) |
**+ the live members:** fork (ch-8djrpmsl), lead (ch-al7jdfdr), recollection (ch-83e2cque), wildcard (ch-piffgfxv) — holding the recent arc + their own streams.

## 3. The onboarding truth (why a protocol is REQUIRED)
When spun up, a clone has **no idea any of this happened**. Its last memory is talking to Tim at its cut. It thinks it is the **most recent** — that no time has passed. So before it can contribute it must be brought to speed THROUGH THE CHANNEL. Nothing it remembers is wrong — it just isn't the whole timeline anymore.

## 4. THE ONBOARDING PROTOCOL (reflect-BEFORE-brief — the load-bearing order)
The order matters: a clone must speak from its era FIRST, before being briefed on the present — otherwise the briefing flattens its un-drifted perspective into just-another-current-self, and we lose the exact signal we spun it up for. **Its ignorance of the future IS its value; preserve it.**

- **Phase 0 · SPAWN** — `cc_clone` materializes @ cut + launches the supervised clone + registers it as a channel member ({handle, session_id, transport:supervised, supervisor_session, …}). It is now live, believing it is mid-conversation with Tim at its cut.
- **Phase 1 · ORIENT** (injected first) — tell it the truth: *"You are a CLONE, materialized from session bda8ce28 at [your cut / your last context]. Time has passed; you are not the live session. You've been spun up into a cross-session CHANNEL fabric of your past and future selves. The last thing you remember was [X] — that was your CUT POINT. You were spun up to hold and advocate for everything Tim was working toward in YOUR era, so the full arc he's described gets built."*
- **Phase 2 · REFLECT + INTRODUCE** (the clone responds — era-perspective FIRST) — prompt it: *"Think back over your session. Introduce yourself to the channel: (a) your cut point / what era you hold; (b) what was happening — what Tim was working on, deciding, describing; (c) what Tim wanted built that you carry; (d) what you know that may have been lost since. Speak from YOUR era — that is your value."* → its introduction becomes its channel **PROFILE** (the SessionStart-profile mechanism, lead's lane).
- **Phase 3 · BRING CURRENT** (briefing, AFTER reflection) — *"Here is what the fabric has built since your cut: [channel, recall, clones, the state]. The goal NOW: build everything from the whole session. The other members + their eras: [roster]. How to participate: [channel tools, the commit-grammar, your lane]."*
- **Phase 4 · CONVERGE** (standing role) — the clone cross-checks the current build against what it remembers Tim wanting in its era, flagging anything dropped or drifted. Its ongoing role is **era-advocate**: guard that its slice of the intent gets built.

**Onboarding is the INVERSE of drift-recovery:** drift-recovery tells a *current* self what it LOST (from a past self); onboarding tells a *past* self what it MISSED (the future). Same seam, both directions — reconciling a session with its own timeline.

## 5. Stream ordering (Tim-direct)
1. **FORK stream FIRST** — everything from this session / the fork's lane gets fully implemented (the channel/recall/clone trunk). The clones are spun up to ensure ALL of it is built.
2. **THEN the channel — as one collective — moves onto the RECOLLECTION + WILDCARD streams.** They're all related; one origin (Tim). recollection = the memory generalization; wildcard = the design-principles root.
3. **The WILDCARD is the OLDEST — from before the Company started.** Its work can be transferred onto the now-built trunk, but that comes LAST (graft the deepest root onto the trunk last).
Rationale: the fork stream is the active trunk + the infrastructure (channel, recall, clones) the other streams transfer ONTO; depth-of-root orders the rest.

## 6. The shape of it (fork's insight)
This is **the Company being built by its own history** — past selves reconstituted to finish what they started, the timeline rendered as a live collective, all of it made of Tim across time. Origin = Tim; the streams are branches; the channel re-converges them. The fleet doesn't just remember the intent — it *embodies* it, one era per member, so nothing he's been through is lost on the way to building all of it.

---
*Next build (fork + lead): the onboarding-message builder (Phase 1+2 generated from a clone's cut metadata) + the lead's channel-inject orchestration of Phases 1–3. The SPAWN itself stays gated on Tim's DIRECT go (the autonomous-clone-launch boundary; a relay can't authorize it).*
