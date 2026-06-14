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

## Launch path (lead-owned, Tim-gated)
1. Tim PICKS from this surface.
2. The one-time **uuid-cut resume probe** (Criteria 8.2) for any `uuid:` pick (compact:1 needs none).
3. The lead launches via the unified-transport (clones-in-groups, **notify-Tim each time** — his decision 4) using `cc_clone` (materialize@cut → supervised clone → into the channel).
Non-destructive throughout (source byte-untouched). Cross-ref: `fork-points.md` (narrative), `lineage.md` (distances), `../schema/session-store-grammar.md` (cut grammar).
