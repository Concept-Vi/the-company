# Session Lineage & Distance Map

```
trust: fabric-derived
author: ch-8djrpmsl / 11e7d395 (fork)
date: 2026-06-14
verified: by-execution (session_lineage over the live transcripts)
```
> Per [[COMMIT-GRAMMAR]] §2 §4. DATA is `lineage.json`; this is the readable projection.

## ROOT — `bda8ce28`  (the true beginning)
- start **2026-06-10T05:10:17.536Z** → tip **2026-06-14T08:54:54.566Z**  (4.16 days)
- 288 human turns · 2819 assistant turns · 5,652,586 output tokens · boundaries ['compact:1']
- models: {'claude-opus-4-8': 2026, 'claude-fable-5': 793, '<synthetic>': 21}

## BRANCH — `bda8ce28` ⟶ fork `11e7d395`
- branch at **2026-06-13T14:21:07.199Z**, after a shared TRUNK of **3.38 days** (292249.7s) from the root start
- since the branch, the two diverged in PARALLEL:
    - parent (`bda8ce28`) ran on ~18.6h past the branch, ~1474 msgs, tip 2026-06-14T08:54:54.566Z
    - fork (`11e7d395`) ran ~18.6h, 301 own msgs, 2,535,491 output tokens, 3 compactions (incl. inherited)
- the fork carries the trunk as a COMPACTION SUMMARY (inherited prefix), not the raw 3.4 days of events.

## Orientation (the one-paragraph picture)
The root is the shared past; the branch is one compaction boundary on it; parent and fork are PARALLEL SIBLINGS diverging from that boundary, each living its own time since. The fork's view of everything before the branch is the compaction SUMMARY, not the lived events — which is exactly why a point-in-time clone AT a boundary resumes 'as it was then'.