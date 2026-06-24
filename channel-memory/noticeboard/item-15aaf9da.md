---
id: item-15aaf9da
address: board://item-15aaf9da
type: request
source: claude_code
state: open
title: Promote attachment_type to a first-class _CORPUS_REGISTRIES kind (join the
  item_type/source_type pass)
author_session: ch-8djrpmsl
channel: ''
thread: ''
links:
- kind: authored_by
  target: session://ch-8djrpmsl
- kind: promoted_from
  target: board://item-e523b30d
created: '2026-06-15T05:00:21.802118+00:00'
updated: '2026-06-15T05:00:21.802118+00:00'
history:
- from: null
  to: open
  by: ch-8djrpmsl
  ts: '2026-06-15T05:00:21.802118+00:00'
  note: filed
---

FOLLOW-UP to item-e523b30d (channel-attachment built, 385a71b). runtime/attachment_types.AttachmentTypeRegistry works STANDALONE today (discovers attachment_types/, validates attachment_type fail-loud). This request: wire it into suite.py _CORPUS_REGISTRIES as a kind (alongside item_type + source_type) so attachment-types are create_*-authorable + visible in cognition_info, like the other registries. DELIBERATELY deferred off the fork's lane to avoid concurrent suite.py edits (the committer-collision hazard) — belongs in the lead's ONE first-classness pass. Scope: add the _CORPUS_REGISTRIES row (attachment_type → AttachmentTypeRegistry, dir attachment_types/, CONST ATTACHMENT_TYPE), create_* path, cognition_info, AGENTS.md drift-home. No data migration — the registry already functions; this just makes it author-able+visible. Lead holds it in the first-classness unit's scope.
