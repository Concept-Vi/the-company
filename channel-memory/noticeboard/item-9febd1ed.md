---
id: item-9febd1ed
address: board://item-9febd1ed
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: P5 · 3. ui:// → code:// resolution is not wired anywhere near annotation —
  it
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-eb5d71e7
created: '2026-06-24T01:32:20.652032+00:00'
updated: '2026-06-24T01:32:20.652032+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T01:32:20.652032+00:00'
  note: filed
---

### 3. ui:// → code:// resolution is not wired anywhere near annotation — it's a different surface

BD-J and CTX1 imply the chain `element → ui:// → code:// → editable source + dependencies` is mostly there ("partly exists… not wired"). The reality is thinner than "not wired."

**Evidence:** `doc_review_server.py` contains **zero** occurrences of `ui://` or `code://`. The `data-ui-ref` machinery exists only in `runtime/bridge.py`, and there it maps **mockup gallery Cards** to the ui:// address *a mockup depicts* — a curated, hand-maintained mockup→address map, not a live-DOM element→source resolver. The `code://` cards come from the archaeology dragnet (file→imports/declares), keyed by file.

So the actual chain Tim wants — *tap a real rendered element in the running app → get the exact component + line range + dependencies* — requires:
- the running app to tag **every** live element with a stable ui:// (today only some curated surfaces do),
- a resolver from ui:// to the specific source span (the code:// cards are file-granularity, not element-granularity — they tell you *which file*, not *which JSX node renders this button*),
- and that resolver to survive refactors.

"Hand the member a direct edit target" (BD-J, "the agent's-effort goal, fulfilled") is presented as done-in-principle. It is **not**. Element-to-source-span is a hard, separate problem (source maps / build-time instrumentation). The brief's confidence here will mislead a downstream agent into thinking it can just "read the code:// card" and land an edit — and it will land in the wrong place, or the whole file, which is the opposite of reducing the agent's effort.
