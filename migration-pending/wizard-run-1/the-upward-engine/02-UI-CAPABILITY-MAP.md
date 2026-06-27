---
type: concept
register: descriptive
aliases: ["Upward Engine — UI capability map"]
tags: [company, ui, vision, recollection, dragnet, mcp]
status: draft
relates-to: ["[[The Upward Engine — vision]]", "[[Upward Engine — dogfooding plan]]", "[[Upward Engine — system state and locations]]"]
---

# Upward Engine — UI capability map

The surfaces the UI could carry. Each is **a way of looking** at the one upward engine; each is wired to a real system that exists today (or to an organ that needs switching on — flagged). Not a closed list — a starting set to grow.

> Read with [[Upward Engine — system state and locations]] open — "wired to" names real files/tools, and "needs" names the organs not yet switched on.

---

## 1. The run-monitor — *watch the catch-all climb*
**Shows:** a live run as data rises through the tiers — the concurrent small-model fan-out firing, projections/units landing as they complete, clusters forming, and the **cascade economics** (where each tier — code, local 4B, embeddings, Claude, cloud, Tim — is being spent right now).
**Lets Tim:** see a run *happening* instead of inferring it from connection-refused (the wizard had no eyes); catch a degenerate-loop or a VRAM eviction the moment it happens; feel the cost shape.
**Wired to:** the company's run/event surface (`mcp__company__get_events` / `runs` / `cognition.*` SSE), the same telemetry the field report begged for (persist `finish_reason` + status + latency + tokens + run_id per call).
**Needs:** the chains emitting run-events as they execute (recollection's capture/distill, the Dragnet chain).

## 2. The multi-space map — *navigate by meaning*
**Shows:** the corpus as a navigable map — nodes (files / units / projections / marks), typed edges, clusters — and, crucially, **a file as a point in many projection-spaces at once** (principle-space, vocabulary-space, topic-space…). The view lets Tim *move through a space* and see neighbours by that meaning.
**Lets Tim:** run the **inversion-finder** as a visual query — *"near in principle-space but far in topic-space"* surfaces the face-value-hidden relations (the `sequences ↔ wizard` kind) that keyword and raw-text similarity miss; separate his **coined terms (gold)** from generic/AI-fingerprint vocabulary by moving in vocabulary-space.
**Wired to:** recollection's `recall` (meaning-scoped, returns joinable provenance addresses) + `navigate` (the address-mover: walk time/scale from any node); the served lens at `:8007`.
**Needs:** the **multi-vector-per-item / per-projection-space embedding** — the wizard's highest-value *unbuilt* unlock; recollection has the per-lens `vec_<space>` mechanism but distilled units aren't embedded yet. This is the keystone view and the keystone gap.

## 3. The chain-composer — *compose, launch, steer*
**Shows:** a chain as a thing you assemble — which corpus, which models/lenses, which projections, which tiers — and its result as it returns.
**Lets Tim:** build a chain (a wizard-restore over a project, a Dragnet over a data pile, a recollection distill over a session-set), launch it, watch it (view 1), then **choose the next pass from what he sees** — the patterned-visibility loop as an interactive surface, not a pre-scripted run. Dragnet is just one saved chain among many; new chains are compositions, not new code.
**Wired to:** the company's compositional engine (nodes / cascades / `run_cascade` / the MCP verbs); the registry-driven projection set (add a projection = a row).
**Needs:** the chains exposed as composable/launchable units through the MCP (some exist as ops scripts today — `dragnet_extract.py` etc. — not yet a composable surface).

## 4. The marks & reconstruction surface — *Tim's tier, as fast decisions*
**Shows:** proposed **marks** (corroboration, ai-fingerprint, idiosyncratic-vs-generic, a gold-likelihood profile) and reconstructed **intent** — each **with its evidence**, never a black-box score — awaiting Tim.
**Lets Tim:** confirm / correct / reject at a glance — the human reduce-tier of the cascade made a *decision surface*, not a reading chore. "Capture records what's there; marks record how to read it" — and **Tim's confirm is what turns a proposal into truth** (positive-only corroboration: rare ≠ confabulation, rare gets *flagged for Tim*, never silently discounted). For principles specifically this is the **ratify** gate — a principle is a proposition until Tim blesses it.
**Wired to:** the company's decision/surfaced/RHM machinery (`mcp__company__decisions` / `marks` / the review inbox); recollection's `verdicts` + `candidates` tables (the staging is built).
**Needs:** recollection's **ratify** step (currently throws "not wired") + the judge that proposes; the marks passes designed but unrun.

## 5. The cross-project / cross-time view — *omniscience*
**Shows:** the whole corpus across projects and sessions at once — concept families pooled across all time, a project's reconstructed shape beside another's, the timeline of when a thread was discussed.
**Lets Tim:** "merge these two projects"; find every place a concept appeared regardless of which project or session; see what was decided and when (the drift recovery — a decision made in-session, un-recallable an hour later, surfaced again).
**Wired to:** recollection (the OUTER cross-everything layer) unioned with `session_recall` (the INNER per-session layer) at the freshness seam; the crossings provenance graph (`file://`/`exchange://`/`session://`/`project://`).
**Needs:** recollection live and embedded (it's backfilled but parked); the union seam wired.

---

## What's buildable *now* vs what needs the organs switched on
- **Buildable against live pieces today:** views 1 (run-monitor) and 5-partial — the company's event/recall MCP (`session_recall`, `get_events`, `decisions`) is live; recollection's recall *works via CLI* over the backfilled corpus (proven this session).
- **Needs recollection's organs switched on** (see state doc): view 2's multi-space navigation (embed the distilled units), view 4's ratify (wire the judge), view 3's chains-as-MCP-units. None are far — they're stubbed seams with the data model already built.

The honest sequencing: **start with the *look* (views 1 + 2 over what's already embedded), because the look is the whole point** — then the composer and the marks-tier follow as the organs come online. (Sequencing detail: [[Upward Engine — dogfooding plan]].)
