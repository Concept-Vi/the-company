---
type: constitution
register: prescriptive
module: operator
aliases: ["operator — constitution"]
tags: [company, operator, constitution, frontend]
governs: []
relates-to: ["[[operator app — constitution]]", "[[runtime — constitution]]", "[[Company Map]]"]
status: building
---

# operator/ — the operator's own surface

**What this is.** The home of the OPERATOR-FACING product surfaces — what Tim actually opens, phone or
desktop. Distinct from `canvas/` (the rich graph canvas, the live PWA) and `surface/` (the instrument
projection surface): this folder is the operator *console* program (the K-spec on the board,
`board://item-67e34f0c` — K0 consumption contract · K1 where/how · K2 view set · K3 order+gates).

**What it must guarantee.**
- Everything here is styled ONLY by the claude-ds design system (K0) — zero raw hex/px, one stylesheet
  chain, components through the sanctioned door.
- Everything here talks to the Company ONLY through the bridge's `/api` face, same-origin (K0's
  SAME-ORIGIN law) — no second backend, no hardcoded hosts.
- Honest surfaces: a view that doesn't exist renders the DS's `.state-block` "not built yet" pattern,
  never a fake.

**Where new things go.** A new operator view/app lane → `app/` (read [[operator app — constitution]]
first). A new kind of operator surface (e.g. a watch face, a TV wall) → a sibling folder here with its
own constitution.

**Seam.** `runtime/bridge.py` serves the BUILT app at `/app` and the DS home at `/ds/*` (B1); the app's
dev server proxies both to the bridge. Local-only (127.0.0.1) until B4 auth is green — never tailnet-expose.
