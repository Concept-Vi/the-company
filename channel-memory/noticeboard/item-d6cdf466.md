---
id: item-d6cdf466
address: board://item-d6cdf466
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: P5 · 4. The "V" radial menu — right symbol, but watch the well-documented rad
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-a5b7cf79
created: '2026-06-24T01:32:18.709806+00:00'
updated: '2026-06-24T01:32:18.709806+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T01:32:18.709806+00:00'
  note: filed
---

## 4. The "V" radial menu — right symbol, but watch the well-documented radial pitfalls

Tim wants the company's **V symbol** to open a **radial menu** holding: mode toggle (block ⇄ element), submit-all, draft count, supervisor chat, replies/decisions-needing-eyes. Two lenses on this:

**The good:** radial/pie menus are genuinely *faster* for touch than list menus because every item is the same short flick-distance from center, and they support **directional muscle memory** — after a few uses you flick "up-left for submit" without reading (this is the "marking menu" property; the well-known finding is that radial selection is gesture-learnable in a way linear lists never are). For a single recurring operator who'll use this hundreds of times, that learnability is exactly the right bet. (Sources: Big Medium "Touch Means a New Chance for Radial Menus," Pushing Pixels "The usability of radial menus.")

**The pitfalls — all documented, all directly relevant:**
- **The hand occludes the menu.** A *full* circle puts half the items under his thumb/palm. The repeated expert recommendation is an **arc, not a full circle** — fan the items *away* from the thumb. Since Tim holds the phone one-handed and the V should "open toward the thumb" (his own words in BD-G), the menu should bloom as a **quarter/half arc anchored in the bottom corner, opening up-and-inward** — into the screen, away from the holding hand. (Source: the touchscreen-game radial thread — "a full radial menu can be obscured by the user's hand; making the menu items an arc above the touch point.")
- **Radial menus don't scale past ~6–8 items and hate text labels / submenus.** Tim's list is already at the edge (5–6 destinations) and several items (supervisor *chat*, *replies* inbox, *decisions*) are not quick-actions — they're *places you go and stay.* **Don't force those into radial wedges.** The clean split: the **radial ring = quick verbs** (toggle mode, submit-all, attach, multi-select); **destinations = a panel/sheet the radial opens into.** Mixing "do it now" verbs with "go here and dwell" sections inside one radial is the classic overload that makes pie menus feel cluttered. (Source: Prototypr "Putting the Rad back in Radial Menus" on icon-only, low-count, no-submenu discipline.)
- **Icon-only is required (radials have no room for labels) — and Tim *hates emoji and wants the DNA brown-circle iconography* (MSG2).** That's a hard constraint that lands perfectly here: radial menus *demand* a clear, learnable icon set, which is exactly what the DNA system provides. Good alignment — but it means every wedge needs a real, legible glyph at thumb size (44pt minimum target), no fallback to text.

**The badge problem (his "number of comments" + "unread replies"):** the V button must carry **two distinct ambient signals while closed** — pending-draft count and unread-replies — without opening. Don't stack two numbers on one dot. I'd use the count for drafts (the thing *he* is building) and a distinct colored pip for "something needs your eyes" (the thing *they* sent back). The closed V is his only persistent status surface; it's doing more work than he framed it as.

---
