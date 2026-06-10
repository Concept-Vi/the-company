---
type: constitution
module: dials
aliases: ["dials — constitution"]
tags: [company, constitution, dials, registry, cognition]
governs: [Track-1]
relates-to: ["[[Company Map]]", "[[runtime — constitution]]"]
status: living
---

# dials/ — module constitution

**Is:** the **file-discovered DIALS registry** — the entity's adjustable CHARACTER TRAITS. Born
2026-06-10 (Track-1, the brain conversation): Tim — "yes they should be dials. I should be able to
adjust them, and not need to make a decision." A dial turns a would-be design decision into a knob:
definitions are rows here; **values persist on the system graph's `dials` node** (the same seam as
the presence mode) via `Suite.set_dial` / `Suite.dial_state`; the MCP face is
`mcp_face/tools/dials.py` (`dials(op=list|describe|set)`).

**Row shape:** module-level `DIAL = {id (==stem) · label · governs (the consumer seams, named
HONESTLY — including not-yet-built ones) · positions (ordered non-empty [{name, meaning}]) · default
(a position name)}`. Malformed rows FAIL LOUD at discovery.

**Condition-scoped overrides:** a value record may carry `overrides: [{when, value}]` — `when` is
declared condition data in the rules-engine shape (conditions COMBINE, per Tim). Overrides are
stored + validated NOW, evaluated once the now-organ + rules wiring exists; until then the flat
value applies and `dial_state` says so (`overrides_evaluated: False`) — never silently.

**The dials (drift home — reflect every add):**
- **anticipation** (reactive · warm · hot; default warm) — how much idle compute becomes foresight.
  Consumer seam: the resolver/now-organ (GC14/Track-1), unbuilt.
- **stability** (museum · workshop · stage; default workshop) — how much the surface may rearrange
  itself. Consumer seam: the RHM surface-composer / resolved-UI layer, unbuilt.

**Never:** hardcode a trait a dial governs · add a consumer that ignores the dial · evaluate
overrides before the rules wiring exists (no silent pseudo-conditions) · a dial without named
positions.

## Read next
[[Company Map]] · `build-prep/brain/THINKING-MEMORY-IDENTITY-PRESENCE.md` (rounds 2–3: where each
dial came from).
