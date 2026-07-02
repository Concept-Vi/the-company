---
id: item-4ddf2a4b
address: board://item-4ddf2a4b
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: P11 · 9 · The `.obsidian` config itself
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-4baaab55
created: '2026-06-24T05:12:09.522969+00:00'
updated: '2026-06-24T05:12:09.522969+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T05:12:09.522969+00:00'
  note: filed
---

## 9 · The `.obsidian` config itself

Reuse the already-configured vault rather than starting cold: `/home/tim/vaults/Obsidian Builder/.obsidian/` already has `community-plugins.json`, `graph.json`, `types.json`, `.base` files, mobile workspace, icons. **[Observed]**

- For **A1**: copy that `.obsidian/` into the noticeboard dir (and `.gitignore` it in the company repo).
- For **A2**: the mirror gets a copy of that `.obsidian/` and inherits the plugin/Bases setup.
- Key config to set regardless: enable Dataview/Bases (for §2), graph filters to hide the `%%obsidian-host%%` fenced noise, and `Front Matter Title` for §8.

---
