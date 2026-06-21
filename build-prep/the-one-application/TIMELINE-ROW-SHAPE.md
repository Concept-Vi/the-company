# TIMELINE ROW-SHAPE — the FACE-1 timeline surface's data contract (for DNA's fresh-build)

*Derived by projection (2026-06-22, lead g-1782063626 — de-block timeline's inputs so DNA's fresh-build is input-ready). Source of truth: the LANDED `/api/timeline` handler (runtime/bridge.py:1500) → `SUITE.agent_session_timeline(sid)` (runtime/suite.py:1071) → `runtime/session_pointintime.build_timeline` (the row-builder). Live returns empty on my test sessions (all live-registered, no jsonl_path) — so the shape below is from SOURCE, the authoritative ground (a populated curl needs an IMPORTED session; see EMPTY-STATE).*

## ★ WHAT THE LANDED ENDPOINT ACTUALLY IS (read this first — a scope flag for DNA/lead)
`/api/timeline` is **ONE SESSION's point-in-time COMPACTION/LIFE timeline** — NOT a global decision/activity timeline. It requires `?session=<session-id>` (fail-loud 400 without). The data = a single session's **compaction boundaries** (where its memory was redrawn) + the **life-segments** between them (turn counts, time spans) — "where along this session's life you are," and the launchable points `session_post(at=…)` resumes from.

This maps cleanly to the **lanes archetype** (`schemas/vi-vision/v1/lanes.schema.json`: "TIME × ENTITY as horizontal lanes with event marks"): the ENTITY is the session, the LANE is its life-arc, the MARKS are the compaction boundaries, the AXIS is time (ts).

⚠️ **SCOPE — RESOLVED-PENDING-TIM (lead g-1782064062, lean=GLOBAL; flagged for Tim's commission-intent confirm, non-urgent, nothing blocks).** Both interpretations are fully specced below so DNA's fresh-build is clean whichever Tim confirms. DON'T build the render until (a) Tim confirms scope AND (b) DNA's fresh.

### INTERPRETATION A — GLOBAL activity/decision timeline  ← LEAD'S LEAN (likely the operator-surface "timeline")
The TEMPORAL counterpart to channel-view's SPATIAL: what's happened across the fabric over time — decisions made, work landed, messages, runs. What an operator navigates a timeline FOR. **SOURCE = the events stream, NOT /api/timeline.**
```
GET /api/events            → SUITE.events(60) → a flat list, newest-first:
  [{ seq:<int>, ts:"<ISO-8601>", kind:"<chat|op.run|decision|…>", summary:"<human one-line>",
     address:"<vi:// addr>", op?:"cognition.run_role", duration_ms?:<int>, run_op?, turn_id? }]
GET /api/stream?since=<seq> → the SSE live version (the surface ALREADY consumes this for the live map)
```
- **Lanes** = by `kind` (chat · op.run · decision · …) — the kind registry (kinds/raw.py) gives each kind its human name. **Marks** = events at their `ts`, labelled by `summary` (already human, operator-law-clean). **Axis** = time. This is the SAME data the radial map plots, laid on a horizontal time×kind lane-grid instead of the wheel — a different lens on the live activity, no new backend (events/stream already serve it).
- **No importer prerequisite** (unlike per-session) — /api/events is live now, populated (verified: chat/op.run events streaming).
- DNA builds: a `timelineRecord(events)` adapter (group by kind → lanes; events → marks) + the lanes archetype + a lanes organism. projection clones the host over /api/events (or rides the existing /api/stream the App already holds).

### INTERPRETATION B — PER-SESSION life/compaction timeline  (the LANDED /api/timeline; likely too dev-diagnostic for a top-level surface)
One session's internal life-arc (compaction boundaries + life-segments) — a DEV-DIAGNOSTIC, narrow/technical. Could be a DRILL from a session-card (not a top-level breadth surface). The landed `/api/timeline?session=<id>` shape is below. (Needs the importer-backfill prerequisite — see EMPTY-STATE.)

⟹ If Tim confirms GLOBAL → DNA builds against /api/events (Interpretation A); the per-session shape below is then a session-card DRILL detail, not the timeline surface. If PER-SESSION → the /api/timeline shape below is the contract. Lead's lean + the framing are in this doc; Tim's call decides.

## THE ENDPOINT
```
GET /api/timeline?session=<session-id>
→ 400 {ok:false, error:"/api/timeline needs ?session=<session-id>"}          (no session param)
→ 200 {ok:true, timeline:null, reason:"…has no jsonl_path… (registered live, not imported)…"}   (EMPTY-STATE — honest, not an error)
→ 200 {ok:true, timeline:{ …the shape below… }}                              (populated — an imported session w/ a transcript path)
```

## THE POPULATED `timeline` OBJECT (build_timeline's return)
```
timeline: {
  session: "<sid>",
  boundaries: [                 // the COMPACTION events — the marks on the lane
    {
      n: 1,                      // boundary index (1-based)
      line: <int>,              // transcript line of the boundary
      uuid: "<event-uuid>",
      ts: "<ISO-8601>",         // when this compaction happened — THE TIME AXIS
      trigger: "<str>",         // why it compacted (e.g. auto/manual)
      pre_tokens: <int>,        // context size before the redraw
      post_tokens: <int>,       // context size after
      messages_summarized: <int>,
      preserved_count: <int>,   // messages carried past the boundary verbatim
      resume_cut_line: <int>,   // the END of the preserved window — the launchable cut
      resume_cut_uuid: "<uuid>",
      point: "compact:N"        // the launchable point id — session_post(at="compact:N") resumes here
    }, …
  ],
  segments: [                   // the LIFE between boundaries — the lane bands
    {
      n: 0,                     // segment index
      from_line: <int>,
      user_msgs: <int>,         // turn counts in this segment
      assistant_msgs: <int>,
      first_ts: "<ISO-8601>",   // segment span start
      last_ts: "<ISO-8601>"     //              end
    }, …
  ]
  // (+ likely totals: events_total / lines_total / started / ended — confirm against build_timeline's final return when an imported session is live)
}
```

## RENDER NOTES (for DNA's lanes archetype)
- **The lane** = the session's life, left→right by `ts`. **Marks** = `boundaries` (compaction events) placed at their `ts`; each mark is a launchable point (`point:"compact:N"`). **Bands** = `segments` between marks, sized/labelled by turn-counts (`user_msgs`+`assistant_msgs`) + time span (`first_ts`→`last_ts`).
- **Human meaning, never machine names** (operator-law): `point:"compact:N"` → "where the memory was redrawn (#N)"; `trigger` → plain; `pre/post_tokens` → "context shrank from X to Y"; never show `uuid`/`line`/`resume_cut_uuid` to the operator (those are the launch internals).
- **EMPTY-STATE is first-class** (no-silent-failure): `{timeline:null, reason}` → render an honest "no timeline yet — this session wasn't imported / has no transcript path" (the lanes.schema's honest empty-state), NOT a blank or a scary error. The reason text is operator-translatable ("this session is still live / hasn't been filed for timeline yet").
- **HOST/CLONE pattern** (projection): identical to channel-view/board-view — boardRecord/channelGraph's sibling would be a `timelineRecord(raw)` adapter (DNA) → a lanes organism (DNA.org.lanes or similar) → `renderArchetype('<timeline-archetype>', rec, {visualDevice})`; projection hosts the overlay + clones the mount (a `timelineStore` over /api/timeline?session= + a `TimelineView` on `timeline:open`). INPUT-READY now; the adapter+archetype+organism are DNA's fresh-build.

## DE-BLOCK STATUS
Timeline's INPUTS are now staged (this doc). The RENDER (timelineRecord adapter + lanes archetype + organism) is DNA's fresh-build (deferred, budget-honest). projection clones the host the instant DNA ships them — same template as board-view (committed ee2caad) / channel-view. The one gate before DNA builds: the SCOPE question above (per-session life-timeline vs global activity) — lead/DNA resolve.
