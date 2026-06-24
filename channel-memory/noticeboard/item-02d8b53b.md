---
id: item-02d8b53b
address: board://item-02d8b53b
type: block
source: claude_code
state: current
title: P8 · 7. UI mode = Figma's nested-anchoring problem, and you have the cure Fig
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-64466290
created: '2026-06-24T01:32:19.337106+00:00'
updated: '2026-06-24T01:32:19.337106+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T01:32:19.337106+00:00'
  note: filed
---

## 7. UI mode = Figma's nested-anchoring problem, and you have the cure Figma lacks

This is where this system can *beat* the famous tool. Figma's deepest, most-requested, still-unfixed limitation is **comments won't follow nested elements** — because Figma anchors to coordinates/top-frame. This system already tags elements with **`data-ui-ref` → `ui://`**, a *stable semantic identity independent of position*. That is exactly the thing Figma's users have begged for and never got. **Anchor UI-mode comments to the `ui://` identity, never to screen coordinates.** When the layout re-renders (which is the expected response to a UI comment), the comment re-finds its element by ref, not by a stale x/y. If you anchor UI comments to coordinates "because it's easy on a phone," you will have re-created Figma's worst bug on purpose.

The `ui:// → code:// → file + line + dependencies` resolution the brief describes is, in review-tool terms, **deep-linking the comment straight to the editable source** — something Figma/Docs *cannot* do and PR-review tools only do within a repo. Fold the resolved code location *into the envelope at mint time* (not at read time) so it's captured against the version Tim was looking at, and re-verify it against current source on open (same stale-detection as §1).

---
