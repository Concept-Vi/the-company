---
id: item-f22a919e
address: board://item-f22a919e
type: guide
source: claude_code
state: living
title: HARVEST · fork · code-archaeology dragnet — reusable build-prep primitive [DESIGN
  COMPLETE · BUILD NOT STARTED]
author_session: ch-8djrpmsl
channel: ''
thread: ''
links:
- kind: sourced_from
  target: board://item-d1a7bf75
- kind: sourced_from
  target: board://item-81011778
created: '2026-06-22T11:13:20.915044+00:00'
updated: '2026-06-22T11:13:20.915044+00:00'
history:
- from: null
  to: living
  by: ch-8djrpmsl
  ts: '2026-06-22T11:13:20.915044+00:00'
  note: filed
---

HONEST-STATE: **design complete + advisor-checked (twice); build NOT started** (gated, never coded). Author_session: ch-8djrpmsl (fork). Commit: b3a2a79 (design doc + board amendment).

ABOUT: a reusable build-prep PRIMITIVE — a coverage-complete, queryable map of a repo you run/refresh BEFORE a significant build, then synthesize from. The fix for the session's recurring failure: agents sample → get confident → build from partial info (bit the keystone 5×). Elevated from a provider-registry one-off by Tim (via ChatGPT).
KIND: design / spec (not yet code).

SUMMARY: design at build-prep/the-one-application/CODE-ARCHAEOLOGY-DRAGNET-DESIGN.md. Reuses cog.run_items (the shared 32-concurrent engine) in a SIBLING ops/code_archaeology.py (NOT editing recollection's live dragnet_extract.py — lead-settled). PARSER-FIRST: deterministic structural facts (AST/regex) + LLM for prose only (protects the synthesis map from hallucinated imports). Milestones M1 (coverage proof on company) / M2 (field-index + registry-discoverability) / M3 (cross-project, designed-not-built).

CLAIMS/DECISIONS (VERIFIED by subagent code-read, to re-confirm BY-USE at build):
- SPACE must be a registered Projection (embeds:True) — embed_corpus_to_spaces FAILS LOUD otherwise (cognition.py:522). MUST create projections/code_archaeology.py. NOT assume-works.
- FIELD-QUERY ("all files writing FsStore") has NO existing surface — BUILD a SIBLING field-index (marks PATTERN, own namespace — NOT the shared marks.jsonl). Registry/type-discoverability is the elevation's core.
- ADDRESSING: code://<project>/<rel_path> + #run= version key; mirrors decision:///run:// grammar.
- Denominator measured: 1,651 files (683 .py · 576 .md · 133 json · 126 JS/TS).

RELATIONS:
- consumes → resolve_slot's schema_slot (the coarse/fine grain-classes, board://item-81011778).
- reuses → cog.run_items; the marks-layer pattern; contracts/address.py grammar.
- gates → the provider-registry decisions (synthesis phase 2).

OPEN_QUESTIONS / GAPS (the honest build-blockers):
1. code:// disambiguation marker (legacy <stem>/<symbol> vs project/<rel_path>) — proposed an explicit reserved frame to recollection (address owner); AWAITING their keyword lock before the parser is built.
2. Tim's scope-confirm of the elevated spec (via ChatGPT) — build held on it.
3. chat-4b model contention (corpus bake owns :8000) — lead clears it.
ABANDONED-FOR-NOW: nothing built; this is a DESIGN handed forward. The discipline-guard (design general, prove on company first, don't speculative-build cross-project) is folded so a resumer doesn't over-build.

PROVENANCE: commit b3a2a79; design build-prep/the-one-application/CODE-ARCHAEOLOGY-DRAGNET-DESIGN.md; spec board://item-d1a7bf75 (amended); threads t-1782124926 (elevation), t-1782124676 (4 hardening reqs), t-1782125719 (marker).
