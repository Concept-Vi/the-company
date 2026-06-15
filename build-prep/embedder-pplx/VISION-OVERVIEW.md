# pplx + the Instrument — Vision Overview (the through-line)

*Index + synthesis of the embedder-pplx file set. Born from Tim's 2026-06-15 think-aloud ("huge amount of
potential… stretch it out… think it all back"). Tim sets direction; the per-domain depth is mine. Living docs.*

## The through-line (one sentence)
The instrument is becoming a **dual-interface frame-chooser** (Tim by sight · agents by MCP) over data that is no
longer fixed vectors but **accumulating layers** — each layer a reading of a thing under a chosen frame
(embedder · context · resolution · precision · centre · time · scale) — all riding a real substrate
(Postgres/Supabase/pgvector) instead of the provisional flat files.

## The four moves (each its own file)
1. **The model, leveraged** → `LEVERAGE-AND-TOOL-REQUESTS.md` — pplx-context-4b is the embedder; the @instrument
   loadout; the migration to PLAIN pplx (the quality win); context proven SELECTIVE (homogenizes a registry).
2. **The instrument as a control surface** → `INSTRUMENT-DUAL-INTERFACE-AND-LAYERS.md` — we USE it (not a viewer);
   dual face (Tim + MCP, one engine); the multi-layer re-embeddable model (read·override·store·stack·promote);
   framing as the unifying primitive; the pure-read→authoring evolution (the key tension to confirm).
3. **Every capability as an affordance** → `MODEL-CAPABILITIES-AS-AFFORDANCES.md` — dense · context-as-frame ·
   **MRL semantic-zoom** · **binary full-corpus scale** · 32K whole-composites · no-instruction · isolated↔context
   (+ **context-strain**) · multilingual · **embedder-as-a-lens** (the loadout). Each a frame-knob, dual-face.
4. **The substrate** → `DATA-SUBSTRATE-POSTGRES-SUPABASE.md` — flat-JSON (provisional) → pg/pgvector via Supabase
   (local→cloud); the layer schema; realtime spine; migrate behind the injected store seam (swap backend, revert-safe).

## The single mental model (build toward this)
> **choose a frame → read the data in it → see it (a lens) → keep it (a layer) → compare / override / promote.**

Every existing lens (nucleation, strain, separator, connections, scale, grid) is a *way of drawing a framed
reading*. Every capability is a *frame knob*. Every kept reading is a *layer on the address*. The seed is the
geometry of one framed reading; the layers are the seed's "one object, many coordinate systems" made literal.

## How it connects to the rest of the Company
- **The seed** ([[the-seed-geometric-substrate]]) — framing = origin-selection (§8); layers = many coordinate
  systems over one object; MRL/rung = the scale axis.
- **The Heart / fractal registries** ([[the-heart]], [[project-company-compositional-architecture]]) — the layer
  set per item is itself a registry; the dual interface is one verb projected two ways.
- **Address accumulation** ([[project-address-accumulation]]) — layers accumulate onto the address over time.
- **Introspective data-building** ([[project-introspective-data-building]]) — layer provenance = use builds data.
- **Loadout registry** ([[project-mode-loadout-registry]], [[native-model-layer]]) — embedder-as-a-lens.
- **Collective cognition** ([[project-collective-cognition]]) — the dual (human+agent) instrument as shared body.
- **Supabase realtime future** ([[project-company-vi-supabase-future]], [[project-vichat-supabase-history]]) — the
  substrate's realtime = the live spine at cloud scale.
- **The keystone / GATE** — layer lifecycle (provisional→ratified) IS sample→ratified-discrete.

## Consolidated open questions for Tim (the forks I shouldn't decide alone)
1. ✅ **RESOLVED (Tim 2026-06-15): the instrument AUTHORS.** Not read-only — "everything is a variable" = everything
   authorable; the data is loadable + filterable; drop the consent-fixation, git-revert is the safety. (DUAL-INTERFACE
   §5/§5.1, [[feedback-instrument-authors-not-readonly]].) The remaining forks below are real but lower-stakes.
2. **Layer slot identity** — override/store keyed on `(address, space, embedder, reading_mode, context_frame)`?
   (Drives the schema — SUBSTRATE §4/§7.)
3. **Substrate timing** — stand up Supabase-local + PgStore now, or fold it into the embedder migration (embed
   once, land in pg)? (I lean: together.)
4. **Default visibility of layers** — show only the "current" reading, layers on demand (text-minimal), or always
   hint the stratigraphy?
5. **Capability priority** — which affordances first? (My picks: MRL semantic-zoom · binary full-corpus scale ·
   embedder-as-a-lens · context-as-pole/context-strain.)

## Sequencing (proposed — each a verifiable beat, none started here; this fire was THINK+WRITE)
- Foundation: the embedder migration to PLAIN pplx **+** the pg/Supabase substrate, done together (embed once → pg).
- Then: the layer operations (read/override/store/stack/promote) on both faces.
- Then: the high-leverage affordances (MRL zoom, binary scale, embedder-as-lens, context-strain).
- Throughout: the FORM bar (minimal, spatial, non-developer, interface-is-half) + dual-face parity + design-critic.
