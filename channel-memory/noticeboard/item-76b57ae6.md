---
id: item-76b57ae6
address: board://item-76b57ae6
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: BD-J · Breakdown · UI-feedback mode specifics (element identity → code)
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-11da929d
created: '2026-06-24T00:38:11.448129+00:00'
updated: '2026-06-24T00:38:11.448129+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T00:38:11.448129+00:00'
  note: filed
---

# Breakdown · UI-feedback mode specifics (element → code → editable source)

SPECIFIED: In UI mode the element ID goes across, PLUS what the thing is, where it is in the code, maybe dependencies. Same granular-to-whole-page flexibility as content mode.

IMPLIED: UI elements need stable addressable IDs — the company surface already tags elements with ui:// (data-ui-ref). A map element → ui:// → which file/component renders it → its dependencies is exactly what the code-archaeology dragnet's code:// cards already capture (imports/declares). So a UI-mode envelope should RESOLVE element → ui:// → code:// → the exact editable source + dependencies, handing the member a direct edit target (the "reduce the agent's effort" goal, fulfilled). The UI also has a hierarchy (element < component < section < page) the same gesture walks. The running app must expose an INSPECT mode that surfaces element addresses to the annotation layer + highlights on hover/long-press.

ADDITIONS: Live element outline/highlight in inspect mode; show the resolved code location inside the envelope so Tim sees it's actionable; the member can jump straight to source; a visual diff / preview of a requested UI change before it lands; capture the element's current computed state (text, props) into the envelope.
