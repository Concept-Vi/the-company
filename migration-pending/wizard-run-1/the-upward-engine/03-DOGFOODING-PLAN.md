---
type: concept
register: descriptive
aliases: ["Upward Engine — dogfooding plan"]
tags: [company, dogfooding, self-hosting, recollection, dragnet, ui]
status: draft
relates-to: ["[[The Upward Engine — vision]]", "[[Upward Engine — UI capability map]]", "[[Upward Engine — system state and locations]]"]
---

# Upward Engine — the dogfooding plan

The recursive bootstrap: **build the UI by using the engine on the project that is building it.** Not "build the tool, then find a use" — the use and the build are the same act.

## The move
The engine's most natural first corpus is **the company's own scattered self**. This whole consolidation session has been mapping that by hand — the orienteering ledger (`~/company/orienteering/`) is the **v0, hand-made version of exactly the map the engine would produce automatically.** So:

1. **Point the Dragnet at the company's own sprawl** — its files, the scattered folders, the migration. The catch-all's first real catch is the company understanding itself. Output: the typed/addressed/embedded map that the orienteering ledger approximates by hand. (The ledger becomes the *check*: does the engine's map agree with the hand-made one? Where it diverges is signal.)
2. **Point recollection at its own design history** — the corpus already *contains* the sessions where the wizard, Dragnet, and recollection were designed (this session included). So the system can recall its own rationale: "why did we decide render-not-judge?" "what was the rep-penalty open question?" The design is recoverable *from the system*, not from memory.
3. **Render both in the UI, steer from it** — the UI surfaces the engine understanding itself; Tim looks, sees the pattern, corrects, chooses the next pass. The patterned-visibility loop, now turning on the company itself.

That is the company's self-hosting spine (its first real use is itself) turned into a working surface — and it is the safest possible first corpus: the stakes of a wrong reconstruction are low (it's our own repo), and the feedback is immediate (we know the ground truth).

## The seed → real-system path
- **The seed:** the wizard run's unique context — the *real state of Tim's projects* (the only place a real corpus was actually pumped through the fleet), the *ideated process* (the Patterned-Visibility methodology), and the *session transcript* where it was all trialled. (Locations: [[Upward Engine — system state and locations]].)
- **The graft:** the wizard's by-hand prototype (`capture2.py`, the projection/forms/prompt registries, `wizard.db`) is the rough draft of the productised chains. Its outputs are the **first real data the UI renders** — so the UI has something true to show from day one, not a synthetic demo.
- **The path:** by-hand prototype → composable chains through the MCP → the UI as the look-and-steer surface → run on the company's own corpus → the reconstruction loop generalises to *every* project.

## Sequencing (honest, organ-by-organ)
The vision needs recollection's parked organs switched on; the order follows *the look is the point*:

1. **First, the look over what's already real.** The run-monitor + a first cut of the multi-space map over recollection's already-backfilled corpus (proven queryable via `recall` this session). This gives Tim eyes immediately, on real data, before any new build.
2. **Switch on the keystone organ: embed the distilled units** (recollection has the per-lens `vec_<space>` mechanism; units are recorded but unembedded). This unlocks view 2's navigate-by-meaning — the highest-value capability.
3. **Wire the chains as composable MCP units** (Dragnet's `ops/dragnet_*.py` exist as scripts; the wizard's `capture2.py` as a draft) → the chain-composer view; run the company-self corpus through them.
4. **Wire the marks/ratify tier** (the `verdicts`/`candidates` tables are built; ratify throws "not wired"; the proposing judge needs Tim's VRAM greenlight) → the marks-confirm decision surface.
5. **Union recollection (outer) with `session_recall` (inner)** at the freshness seam → the cross-project/cross-time view.

## What dogfooding gives back to the build
- **The UI is validated on real, known-ground-truth data** (the company itself) before it's pointed at projects where Tim can't easily check.
- **Every gap the engine hits on the company corpus is a real spec** — the same way the wizard's walls (the rep-penalty trap, the finish_reason gap, VRAM co-load) became the to-build list. Run-on-self surfaces the next walls cheaply.
- **The reconstruction loop is exercised on a project Tim knows cold**, so the marks/confirm tier is tuned against his real judgment before it matters elsewhere.

> Open question for the build sessions: whether the company-self map *is* the orienteering ledger's successor (the engine replaces the hand-made ledger), or runs *beside* it as a check. Lean: beside-then-supersede — the hand ledger is the acceptance test for the engine's map.
