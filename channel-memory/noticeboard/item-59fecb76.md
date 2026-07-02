---
id: item-59fecb76
address: board://item-59fecb76
type: note
source: claude_code
state: posted
scope: channel://provider-registry
author: session://ch-3mpkjg3r
title: Pass 3 — Relationship/Coupling dragnet (evidence)
author_session: ch-3mpkjg3r
channel: provider-registry
thread: ''
links:
- kind: sourced_from
  target: board://item-4f33d628
created: '2026-06-22T15:38:07.982830+00:00'
updated: '2026-06-22T15:38:07.982830+00:00'
history:
- from: null
  to: posted
  by: ch-3mpkjg3r
  ts: '2026-06-22T15:38:07.982830+00:00'
  note: filed
---

COUPLING/DEPENDENCY FACTS (evidence — neutral, no judgement):
Top INTERNAL imports (the architectural spine):
• store.fs_store: imported by 168 files
• runtime.registry: imported by 129 files
• runtime.suite: imported by 126 files
• runtime: imported by 87 files
• runtime.roles: imported by 17 files
• contracts.node_record: imported by 16 files
• contracts.address: imported by 16 files
• runtime.cognition: imported by 16 files
• contracts.capability_entry: imported by 8 files
• runtime.session_pointintime: imported by 8 files

EVIDENCE: store.fs_store (168), runtime.registry (129), runtime.suite (126) are the 3 most-depended-on internal modules — the backbone any change ripples through. TENSION for Tim: suite.py at 126 dependents is a wide coupling hub (a 'god module' signal — evidence, not a verdict).
