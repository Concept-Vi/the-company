---
id: item-b1f59e67
address: board://item-b1f59e67
type: document
source: claude_code
state: draft
title: Interface architecture — typed composition + the change-pipeline (drift-proofing)
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links: []
order:
- board://item-ef580c11
- board://item-61a95356
- board://item-c3065804
- board://item-0f20b5b1
- board://item-c33f748d
- board://item-75545aa7
- board://item-d2b39deb
created: '2026-06-24T12:01:52.956070+00:00'
updated: '2026-06-24T12:01:53.218756+00:00'
history:
- from: null
  to: draft
  by: ch-3mpkjg3r
  ts: '2026-06-24T12:01:52.956070+00:00'
  note: filed
- from: edit
  to: order
  by: ch-3mpkjg3r
  ts: '2026-06-24T12:01:53.218756+00:00'
  note: interface architecture idea
---

Tim's drift concern, answered: make the interface itself typed/composed/contract-governed like the rest of the company, and route EVERY requested change through a pipeline (understand→locate→implement→validate→document→deploy-live) so changes are made properly + docs auto-update + duplication/drift die. Governs the fork.
