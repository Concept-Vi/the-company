---
id: item-ba9bb40b
address: board://item-ba9bb40b
type: block
source: claude_code
state: current
title: P4 · 1.2 Frontmatter schema drift — Obsidian/plugins rewriting our YAML (SEVE
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-48cd6801
created: '2026-06-24T05:12:10.954501+00:00'
updated: '2026-06-24T05:12:10.954501+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T05:12:10.954501+00:00'
  note: filed
---

### 1.2 Frontmatter schema drift — Obsidian/plugins rewriting our YAML (SEVERE)
Our schema is **closed and order-significant by intent** (`sort_keys=False` is a deliberate choice
to keep a stable human-and-diff-friendly key order). Obsidian and its plugins are hostile to all
three of those properties:

- **The Properties UI** (core, on by default since Obsidian 1.4) parses frontmatter into its own
  typed model and **rewrites it on any property edit** — it reorders keys, normalizes quoting,
  re-emits dates in its own format, and collapses/expands lists. Our `created: '2026-06-22T11:39:12.229079+00:00'`
  (quoted ISO string) can come back as an unquoted date or a different precision. `state: posted`
  is fine; `thread: ''` (explicit empty string) may be dropped or rewritten to `thread:`/null.
- **The list-of-dicts structures are the real casualty.** Obsidian Properties has no first-class
  editor for `links: [{kind, target}]` or `history: [{from,to,by,ts,note}]` or `order: [addr,...]`.
  Obsidian treats unknown-shaped frontmatter as opaque text *until* something touches it — and the
  moment a plugin (Linter, Templater, Metadata Menu, even the Properties panel auto-formatting on
  save) normalizes the file, **nested objects can be flattened, re-quoted, or mangled.** A mangled
  `links` array means a typed edge silently points nowhere or fails `_validate_links` → `get_item`
  **fails loud** → that item is now unreadable by the master.
- **Key reordering** is harmless to YAML *semantics* but destroys our deliberate stable order →
  every Obsidian touch produces a spurious git diff on every field, drowning real changes in noise
  and making the git-revert safety net (Tim's stated safety model) far harder to use.

The "closed FRONTMATTER_KEYS" is a closed set *we* honor; Obsidian has **no reason to respect it**
and every incentive (its own UX) to add `tags:`, `aliases:`, `cssclasses:` and reorder the rest.
