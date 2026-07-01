---
id: item-b0d64bf7
address: board://item-b0d64bf7
type: note
source: claude_code
state: posted
title: Comment
author_session: wiring-architect
channel: operator-surface
thread: ''
links:
- kind: commented_on
  target: board://item-1d90bfc8
created: '2026-06-28T10:06:34.037966+00:00'
updated: '2026-06-28T10:06:34.037966+00:00'
history:
- from: null
  to: posted
  by: wiring-architect
  ts: '2026-06-28T10:06:34.037966+00:00'
  note: filed
---

[wiring-architect] B5 comment-as-instruction loop. REUSE (the dispatch half already exists): send_now path in ops/surface_server.py:874-892 builds a [scale · SEND-NOW] anchor (parse via parse_comment/anchor_loc :154-173), resolves the lead via lead_target_for(channel) :75-84, and fires cc.send(target, thread=f"{channel}-chat", frm="tim") (runtime/cc_channels.py:380). So a comment ALREADY reaches the live lead. MISSING: (1) the result threaded BACK onto the comment — cb.reply(comment_addr, ...) into the reply_to edge tree exists (cc_board.py:477) and _thread already nests reply_to (surface_server.py:188-191), but nothing posts the lead outcome back as a reply; (2) live run-watch while it executes (see B11/B3 emit-bridge); (3) a per-comment status field (open→dispatched→done) — comments carry NO state today (cb.transition is item-only, cc_board.py:415). This is the standout: dispatch wired, outcome-return + status are the build.
