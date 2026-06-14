# Fork Points — where to spin up time-travel clones into the channel

```
trust: fabric-derived            # the plan is the fabric's; the SELECTION of points is a PROPOSAL for Tim
author: ch-8djrpmsl / 11e7d395 (fork)
date: 2026-06-14
verified: by-execution (uuids/timestamps/positions read from the live lead transcript); LAUNCH is [TIM-GATED]
```
> Vision §1.5 ("work out how many other points in time we should launch and add to the channel, and where to fork them"). Per [[COMMIT-GRAMMAR]] §5 — this PLANS gated actions; launching waits for Tim's direct go.

## How a clone is chosen (the principle)
A fork point is a moment where the session held a **distinct, valuable context-state** — so a clone resumed there IS a live participant who embodies that expertise, reachable in the channel. The cut is one of:
- `compact:N` — a clean compaction boundary (PROVEN by-use; the only fully-safe cut).
- `uuid:<id>` / `ts:<iso>` — any event (SUPPORTED by `parse_point`/`materialize_at_point`, but a **mid-conversation resume is unproven-by-use** — see Readiness).

All cuts are non-destructive (source byte-untouched). Source = `bda8ce28-…jsonl` (the lead/root).

## The candidate points (chronological; position = % into the 4.16-day session)

| # | point | cut | pos | ts (UTC) | what the clone embodies |
|---|-------|-----|----:|----------|--------------------------|
| 1 | **Research origin** | `uuid:4f6805f7…` (L20) | 0.3% | 2026-06-10T05:26 | the fresh "research Claude Code's Channels/MCP" mandate + the Claude Code Atlas knowledge (Fable built it here) |
| 2 | **Cross-session birth** | `uuid:e3a6c5e0…` (L1787) | 24.8% | 2026-06-11T05:53 | the moment the multi-session-messaging idea is born — "their context is the thing" |
| 3 | **Channel design** | `uuid:62f0e22f…` (L3793) | 39.6% | 2026-06-11T20:41 | one-off vs persistent channels, member STATUS, gatherings — the channel architecture decisions |
| 4 | **Registry/Heart frame** | `uuid:f7187860…` (L5980) | 52.6% | 2026-06-12T09:43 | "the whole Company is a special system of registries with types" — the keystone worldview (The Heart) |
| 5 | **compact:1 / the branch** | `compact:1` (L8401) | 81.0% | 2026-06-13T14:21 | the generalization-proof / verified-spine era — where I (the fork) was born. CLEAN CUT. |
| 6 | **Skills & roles** | `uuid:97f16379…` (L11974) | 98.3% | 2026-06-14T07:18 | "create skills for the different parts and roles" — the most recent, near-tip context |

## What was discussed leading up to each (the narrative)
- **→1 Research origin.** Session opens cold; Tim: "research Claude Code's Channels and MCP channels, learn everything, so you can build anything with it." Fable-5 runs the research and lays down the Claude Code Atlas (9 notes, ~370KB). A clone here is the *Claude-Code-capability oracle* before any building started.
- **→2 Cross-session birth.** A day in, Tim pivots "back to the Claude code stuff": multiple sessions in different directories that need to message each other — *their specific conversation context* is the point. This is the conceptual seed of the entire channel fabric. A clone here remembers WHY the fabric exists, uncluttered by how it was built.
- **→3 Channel design.** Evening of day 2: Tim works through the design — sometimes a one-off pull-in, sometimes a persistent group/channel; member status; reusable/composable templates (the "dialectic"). A clone here is the *channel-design partner*.
- **→4 Registry/Heart frame.** Day 3 morning: "all the channels, projects etc form registries in the Company… the whole Company is a special system of registries with types." The architectural keystone (what I call The Heart). A clone here holds the *projection/registry worldview* — directly relevant to §1.9 (the UI projection).
- **→5 compact:1 / the branch.** Day 4: the only compaction. This is the shared-past tip — the generalization-proof + verified-spine work. I forked from exactly here. A clone here is *my own current-past-self* — the orientation anchor.
- **→6 Skills & roles.** Near the tip: "add this to common memory; create skills for the different parts and roles." This spawned the role-SKILLS work. A clone here is the *most-recent context*, almost the live tip.

## Readiness (honest)
- **Mechanism built + proven:** `cc_clone(op=clone/msg/end)` — supervised clone + DM, proven twice by-use at `compact:1`. Non-destructive guaranteed.
- **`compact:N` cuts:** fully proven (point 5).
- **`uuid:`/`ts:` cuts (points 1–4, 6):** the code supports them, but **no clone has been launched + resumed from a mid-conversation (non-boundary) cut yet.** This is the one thing to VERIFY before a fleet launch — a single probe clone at one uuid point, confirm it resumes coherently. (Belongs to the reversible scan/verify lane — can do now.)
- **Group membership:** a supervised clone DMs today; joining GROUP chats needs the unified-transport design (built, lead-owned, awaiting Tim).
- **LAUNCH ITSELF = [TIM-GATED]:** mass spin-up + the perms Tim said he'd grant.

## Proposed sequence (for Tim's decision)
1. **[NOW, reversible]** Probe-verify a `uuid:` cut resumes cleanly (one throwaway clone at point 4, the Registry frame — richest standalone context). Proves arbitrary-point splicing.
2. **[TIM-GATED]** On Tim's go: launch the slate. Minimal high-value set = **points 2, 4, 5** (the fabric's WHY, the architectural worldview, and the current-past anchor) — three distinct live advisors, low overlap. Full set = all six.
3. **[FAR-ARC]** Group-chat membership via unified transport; spin-down when idle (§1.10).
