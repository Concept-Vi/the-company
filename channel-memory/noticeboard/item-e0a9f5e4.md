---
id: item-e0a9f5e4
address: board://item-e0a9f5e4
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: BD-H · Breakdown · Image & file attachment
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-11da929d
created: '2026-06-24T00:38:11.388303+00:00'
updated: '2026-06-24T00:38:11.388303+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T00:38:11.388303+00:00'
  note: filed
---

# Breakdown · Image & file attachment

SPECIFIED: Be able to attach images and files to comments, in both modes.

IMPLIED: The envelope carries ATTACHMENTS as blob:// addresses (the blob store already exists). Mobile upload from camera / photo library / files. The member receives attachments as part of the envelope. In UI mode, a SCREENSHOT is a natural attachment (annotate what you saw). Needs MIME handling + thumbnails + a mobile-friendly picker.

ADDITIONS: Annotate ON an attached image (draw/circle/point); AUTO-screenshot the current UI state in UI mode and attach it; voice notes as attachments (he prefers voice — see his transcription); paste from clipboard; size/format guards with loud failure not silent drop.
