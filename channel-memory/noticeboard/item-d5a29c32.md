---
id: item-d5a29c32
address: board://item-d5a29c32
type: block
source: claude_code
state: current
scope: channel://operator-surface
author: agent://lead
title: 'S9 · Block versions with a switcher (Tim: use ''active'' not ''current'')'
author_session: lead
channel: operator-surface
thread: ''
links:
- kind: part_of
  target: board://item-ed91000e
created: '2026-06-28T11:35:00.269030+00:00'
updated: '2026-06-28T13:05:39.843552+00:00'
history:
- from: null
  to: current
  by: lead
  ts: '2026-06-28T11:35:00.269030+00:00'
  note: filed
- from: edit
  to: body
  by: lead
  ts: '2026-06-28T12:56:17.728974+00:00'
  note: v2 MERGE rewrite (in place)
- from: edit
  to: body
  by: lead
  ts: '2026-06-28T13:03:19.403047+00:00'
  note: restore v1 content dropped in v2 rewrite
- from: edit
  to: body
  by: lead
  ts: '2026-06-28T13:05:39.843552+00:00'
  note: fold corroboration corrections (3 unbiased agents)
---

S9 · Block versions with a switcher (Tim: pointer named 'active')
DECISION (Tim): blocks need versions + a clickable indicator to switch; pointer field = `active`.
v2 CONFIRMED: data loss is REAL — edit_item overwrites rec['body'] (cc_board.py:450); history holds NO prior body.
MODEL: each version = an addressable sibling item linked `version_of` → the block + an `active` pointer; switching re-points active (audited via history). Same container pattern as documents, one altitude down.
BUILD: board_edges/version_of.py (add-a-row, auto-accepted by _validate_links) + snapshot-before-overwrite guarding cc_board.py:449-450 + a switch_version op + assemble_document returns {active,versions}. /api/ref-versions (bridge.py:1928) already serves version reads.
PATH/FILE: `active` field — DON'T just bolt onto the closed FRONTMATTER_KEYS (cc_board.py:61-62; _render:177 drops any unlisted key). Fold into COMPANY-IMPROVEMENT #5 (stop gating on a closed allowlist / drive board fields from the registry) so ANY new field persists.
RESTORED(v1): RECONCILES no-versioning — that rule stops FILE proliferation (design-v2.md, -final-FINAL); this is named revisions of ONE canonical address (the block's id never changes), revisions hang off it as typed children. It does not violate no-versioning — it STOPS the current silent data loss (an edit annihilating the prior body). Note for future agents so versions aren't mistaken for a no-versioning breach.
CORRECTED: /api/ref-versions (bridge.py:1928) is keyed on run:// OUTPUT addresses (the set_ref trail), NOT board-block versions — it does NOT serve block-versioning. So the block-version model (version_of edge + active pointer + snapshot + switch op) is ENTIRELY net-new; drop the 'already serves version reads' claim. #5 nuance: FRONTMATTER_KEYS is a PER-MODULE constant (cc_board, cc_images, cc_gate, cc_attachments each own one) — the 'universal' open-the-allowlist fix must cover all four or be scoped to board.
