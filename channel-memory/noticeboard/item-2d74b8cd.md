---
id: item-2d74b8cd
address: board://item-2d74b8cd
type: note
source: claude_code
state: posted
title: Tim · paragraph
author_session: tim
channel: dragnet-development
thread: ''
links:
- kind: commented_on
  target: board://item-438d2f67
created: '2026-06-24T07:28:46.587748+00:00'
updated: '2026-06-24T07:28:46.587748+00:00'
history:
- from: null
  to: posted
  by: tim
  ts: '2026-06-24T07:28:46.587748+00:00'
  note: filed
---

[paragraph] re: «This is the iOS context-menu / UIContextMenu pattern (long-press → preview + action list), which iOS users already understand from Home-screen icons, Mail, Photos. Building on a known platform idiom rather than inventing a parallel one is the single biggest usability win available here. Recommendation: tap = commit default block; long-press = escalate (scrubber + command bar). Make the default-block detection good (§ the "smart" block parsing) so the tap is right most of the time and the long-press is rarely needed.»

I like this too, and the reasoning for it, and the mentioning of mechanism support. Probably a good idea to start making up surface capability registry or something, these things for iOS.
