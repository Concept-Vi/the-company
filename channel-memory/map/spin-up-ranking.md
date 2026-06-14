# Spin-Up Ranking — fork points ranked by context-state value (Tim picks)

```
trust: fabric-derived (the ranking); the PICK is Tim's, the LAUNCH is Tim-gated + lead-owned (notify-each)
author: ch-8djrpmsl / 11e7d395 (fork)
date: 2026-06-14
method: session_lens.spin_up_points over the lead transcript bda8ce28 (by-execution)
scoring: decisions*3 + open_threads*2 + activity_kb/5 — VALUE of the context-state, not recency (vision §1.5, Criteria 3.8)
```
> Tim wanted to choose where to fork ("we could work out how many other points in time we should launch and where to fork them"). This is the evidenced surface to pick from — not a hand-picked list. Each row = a moment a distinct context-state crystallized on the lead session; spin a clone there and it IS that context, live in a channel. Supersedes the conceptual `fork-points.md` (kept for the narrative). 46 candidate directive-segments ranked; top 10 + the clean boundary below.

## How to read it
- **score** = how much decided/built/opened in the segment that directive opened (a proxy for "how much valuable context-state lives here").
- **cut** = how a clone is materialized at that point. `uuid:` = mid-conversation (the directive turn) — needs the one-time resume probe (Criteria 8.2) before fleet launch. `compact:1` = the compaction boundary — CLEAN, already proven by use.
- **readiness** = ✅ proven cut · ⚠️ uuid-cut, probe first.

| # | score | when | context-state it holds | cut | ready |
|---|------:|------|------------------------|-----|:---:|
| 1 | 132.9 | 06-13 10:17 | **Claude-Code integration build push** — the workflow-reads-design-against-criteria era; the densest segment (250 asst turns, 22 decisions, 20 open threads). The verified-spine engine room. | `uuid:96e4f2b1` | ⚠️ |
| 2 | 59.3 | 06-14 07:18 | **Skills & roles** — "create skills for the different parts and roles" (near tip; this thread's origin). | `uuid:97f16379` | ⚠️ |
| 3 | 35.9 | 06-11 23:56 | **The onboarding-questions / decisions exchange** — where the embedding (pplx-4b), voice, edit-guard, channel decisions were MADE via AskUserQuestion. | `uuid:c4052dd6` | ⚠️ |
| 4 | 34.0 | 06-11 08:56 | **Builds / loop-prep / dynamic-workflows methodology** — updating the build patterns. | `uuid:5e310736` | ⚠️ |
| 5 | 28.1 | 06-13 04:26 | **Memory-files investigation** — what they are, when removed, why. | `uuid:e9731613` | ⚠️ |
| 6 | 25.1 | 06-10 10:51 | **Candidates / learnings capture** — the Atlas enrichment, learnings+insights into the vault. | `uuid:c613863d` | ⚠️ |
| 7 | 24.2 | 06-14 05:45 | **The embedding-recall frustration** — "did I not make it clear it was this session, the 4B was the embedding" (the moment that motivated the recall build). | `uuid:3985ace0` | ⚠️ |
| 8 | 20.4 | 06-11 05:55 | **Cross-session messaging BIRTH** — "multiple sessions… message each other… their context" — the seed of the whole channel fabric. | `uuid:a0a54147` | ⚠️ |
| 9 | 17.4 | 06-10 06:26 | **Embedding-model audit + Atlas enrichment** — the origin "audit the models, link/tag everything to the Atlas." | `uuid:505f5635` | ⚠️ |
| 10 | 17.3 | 06-11 21:05 | **The Face / CLI / UI design** — "I don't want it to look exactly the same as the CLI…" | `uuid:a76776d0` | ⚠️ |
| ★ | — | 06-13 14:21 | **compact:1 / the branch** — the only compaction; the shared-past tip; where the fork (me) split. CLEAN cut, proven twice by use. | `compact:1` | ✅ |

## What this surfaces (the read)
The density ranking and the conceptual milestones AGREE on the high-value points: the **fabric birth** (#8), the **decisions exchange** (#3), the **integration build push** (#1), the **embedding origin** (#9). For a first fleet, the strongest *distinct, low-overlap* set is **#8 (the WHY), #1 (the engine room), ★compact:1 (the anchor)** — three live advisors spanning the fabric's intent → its construction → its branch point. If Tim wants the embedding/decision context specifically, **#3** is the decisions exchange and **#7** the frustration that motivated recall.

## ★ AUGMENTED SET — Tim-direct 2026-06-15: launch ALL ranked points + TWO new axes
Tim green-lit the FULL fleet (via lead) + added two axes to surface MORE high-value context-states. Both computed by `session_lens.spin_up_points` (reads the per-message `model` field for Fable; Tim-turn char + UI-cue density for descriptions).

### Axis 2 — FABLE-as-main-model (Tim: "Fable is the most advanced, gave my best responses")
Fable-5 ran main-thread early (L23–L6485). Densest Fable context-states (cut-uuids):
| pt | fable turns | cut | what it holds |
|----|------------:|-----|---------------|
| L2209 | 18 | `uuid:5e310736…` | loop-prep/dynamic-workflows methodology update (+ top UI density) |
| L173 | 14 | `uuid:505f5635…` | the embedding-model audit + Atlas-enrichment origin |
| L1127 | 14 | `uuid:c613863d…` | candidates/learnings capture into the vault |
| L5980 | 12 | `uuid:f7187860…` | the registry/Heart frame (+ high UI density) |
| L1792 | 8 | `uuid:a0a54147…` | cross-session-messaging BIRTH |
| L924 | 4 | `uuid:ee79ccce…` | the skill-making exchange |

### Axis 3 — TIM-DESCRIPTION / UI-REQUIREMENTS density (Tim: many UI descriptions earlier, valuable for the eventual UI build — surface distinctly)
Tim-turn segments densest in UI/interface/render/design/layout language:
| pt | UI-cue hits | cut | what it holds |
|----|------------:|-----|---------------|
| L2209 | 10 | `uuid:5e310736…` | UI/pattern descriptions in the loop-prep update |
| L5980 | 7 | `uuid:f7187860…` | registry/Heart — "the UI renders the addressed state" |
| L5417 | 6 | `uuid:e62970d7…` | registry note (channels/projects → UI projection) |
| L5131 | 6 | `uuid:f0db8090…` | voice + the Face/UI ("five voice engines… outputs") |
| L3793 | 4 | (in fork-points #3) | channel design + the Face (one-off vs persistent, status) |
| L3862 | — | `uuid:a76776d0…` | "I don't want it to look exactly like the CLI" — the Face direction |

### The full LAUNCH-READY set (all cut-uuids, Tim-direct: launch ALL)
compact:1 (`compact:1`, CLEAN — no probe) · the context top (L7489 `96e4f2b1`, L11974 `97f16379`, L4108 `c4052dd6`, L13084 `c6a7179e`, L6828 `e9731613`, L11292 `3985ace0`) · the Fable set (L2209, L173, L1127, L5980, L1792, L924 — uuids above) · the UI set (L5417, L5131, L3862, L3793 — uuids above). Union ≈ 16 distinct points spanning the session's arc + Tim's best-model + UI-requirement context-states.

## Launch path (lead-owned, Tim-direct GREEN-LIT 2026-06-15)
1. ~~Tim PICKS~~ → **Tim green-lit ALL** (the augmented set above).
2. The one-time **uuid-cut resume probe** (Criteria 8.2) per distinct `uuid:` cut (compact:1 needs none) — proves a mid-conversation cut resumes coherently before the fleet rides on it.
3. The **lead orchestrates** the launch via the verified unified-transport (supervised clone → channel member) + **ONE consolidated manifest Notice to Tim** (not per-clone spam — his notify-each, batched).
Non-destructive throughout (source byte-untouched; `cc_clone` asserts source size+mtime unchanged). Cross-ref: `fork-points.md` (narrative), `lineage.md` (distances), `../schema/session-store-grammar.md` (cut grammar).
