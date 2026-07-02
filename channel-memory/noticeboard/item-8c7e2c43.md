---
id: item-8c7e2c43
address: board://item-8c7e2c43
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: P8 · ❌ UI-feedback mode + inspect mode + element→ui://→code:// resolution (BD
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-f9f4a6a6
created: '2026-06-24T01:32:21.861727+00:00'
updated: '2026-06-24T01:32:21.861727+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T01:32:21.861727+00:00'
  note: filed
---

### ❌ UI-feedback mode + inspect mode + element→ui://→code:// resolution (BD-A, BD-J)
The "second mode" where Tim annotates the live UI and the envelope auto-resolves to the editable source file. Architecturally elegant, and the pieces partly exist (data-ui-ref, code:// cards). **But it's a whole second target-source, an inspector overlay, and a resolution chain — to solve a problem Tim can solve today by taking a screenshot and commenting on it.** He even has the instinct already: he hand-drew red annotations on screenshots in MSG2 and they communicated perfectly. The lo-fi version (screenshot + comment) gives 90% of UI-feedback value for ~2% of the build. The element→code resolver is a genuine future capability; it is not a week-one need. **Faked-simply: "to give UI feedback, screenshot the screen and comment on it."**
