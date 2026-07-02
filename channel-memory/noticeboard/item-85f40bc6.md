---
id: item-85f40bc6
address: board://item-85f40bc6
type: document
source: claude_code
state: draft
title: THE ONE SYSTEM — north star + how Tim works + the ① vector-cutover walkthrough
author_session: ch-5wog4hmx
channel: ''
thread: ''
links: []
created: '2026-07-02T03:57:49.726323+00:00'
updated: '2026-07-02T03:57:49.726323+00:00'
history:
- from: null
  to: draft
  by: ch-5wog4hmx
  ts: '2026-07-02T03:57:49.726323+00:00'
  note: filed
---

Full doc: build-prep/the-one-system/NORTH-STAR.md (committed to main). Filed to the board because Tim's only interface to the whole system is the chat until the UI exists.

THE LEDGER IS THE COMMON WORLD — a multi-axis coordinate space (graph · vectors[multi-embedder] · paths · scale[file↕symbol↕pyramid] · time · transcript-provenance[every unit traces to the exchange:// that made it] · addresses/registries), all sharing one grammar + resolver. Everything is located/related by these common axes.

BUILDING: a reusable compositional generation chain for PROJECT UNIVERSES where AI+UI share ONE interface — capabilities projected to MCP AND UI from the SAME functions, data as the origin for both; multi-project = a project-level address.

HOW TIM WORKS (changes how I build): no developers; Tim knows how systems work, not the technical layer (Supabase/SQL/schema/pgvector/TS/UI/MCP). Everything built = AI best-guess = scaffolding, NOT spec. Tim can't request what he can't see → the AI must PROACTIVELY identify best-known ways and factor them into every build. Tools are generative + shared with the UI. Everything → Supabase eventually, not all at once. Fail loud with resolution breadcrumbs (agents, never humans, resolve issues).

① VECTOR CUTOVER (walkthrough): one seam (space_matrix in fs_store.py) feeds all ~7 semantic-search readers; repoint it to Supabase ledger.embedding (76k vectors already there) → all readers follow, none change. Decisions: no-fallback = COMMENT OUT (inert, legible, recoverable), not delete; loud breadcrumbs on miss; expose search as a shared MCP+UI function (best-practice + the vision). ②(addresses) + ③(fork/UI) to be written next; implementation order/scope decided after all three are written.
