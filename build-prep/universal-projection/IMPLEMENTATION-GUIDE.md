# Universal Projection — Implementation Guide

**Originated by Tim Geldard; all derived work attributed to him.** HOW to make each Completion
Criteria item true. Built on RESEARCH-SYNTHESIS.md (the evidence). Tense is exact: "IS" = exists,
"SHOULD BE" = planned.

## Cross-cutting principles (why the system is the way it is)

- **The instrument is the geometric face of the company's resolution system.** It is not new — it is
  `resolve(centre, spaces, n, k, audience, exhale)` with the bindings freed. Four live mechanisms
  (the per-address gatherer, the greeting, the builder context block, the boot bundle) are the SAME
  call hardcoded; the long arc collapses them into one. Build toward that, not a parallel viewer.
- **No hardcoded sectors, ever.** The instrument RESOLVES its divisions from data/registries. The
  data-driven default (raw kinds) is the non-negotiable floor; lenses are swappable rows. "No first
  binding ruins the system" (Tim). A binding that enumerates sectors is the sin.
- **Pure read floor.** The instrument never emits resolve/approve/dispatch. Strain/forbidden zones
  are rendered and surfaced to the gate (the operator), never auto-corrected.
- **Form is half of done.** Every operator-facing surface meets the design rubric, gated by
  design-lint + a separate design-critic. The lattice is the one region that violated this — fixing
  it (Group 5) is debt repayment, not polish.

## DON'Ts (each with a because — these are lessons already paid for)

- DON'T trust `tests/projections_acceptance.py` as the instrument's test — it tests the unrelated
  PLURAL lens registry (`runtime/projections.py`). The name collision means the instrument can look
  green when it has NO test. Write Group 1's suite against `runtime/projection.py:project`.
- DON'T conflate `suite.py:_semantic_radius` (the code-consult feature) with the projection's radial
  axis — different system, same words.
- DON'T mistake the honest stubs for capabilities: `radius` line 155 is a no-op (time-only),
  `rings:4` is hardcoded, angle_from=<registry> is reserved-not-built, order_by=edges is unwired.
  Each is the explicitly-named next ring, not done.
- DON'T tokenise the per-point hue — colour = angle is deliberate geometry (the one literal-free
  exception). DO tokenise everything else in the chrome.
- DON'T build a second vector path — `store/vector_index.py` + `fs_store` vectors are THE substrate
  (persisted, incremental, space-keyed, degrade-loud). Add spaces, never a parallel index.
- DON'T reuse `session_pointintime.py` for the scrubber — it's transcript-scoped; the event-store
  time-freeze is the tiny `project(now=, filter ts<=now)` extension.
- DON'T edit the embedder serving rows in `ops/services.json` blind — another session owns them; read
  the WHOLE row first, coordinate.
- DON'T treat forbidden zones / "nothing ratified" as bugs — they are the work and the discipline.

## Per-group HOW (file:symbol seams)

**G1 · The floor + acceptance suite.** REUSE `runtime/projection.py:project`/`BindingRegistry` (built).
NET-NEW: `tests/projection_instrument_acceptance.py` (distinct name to dodge the collision) —
assert over `project(events, binding)`: every point r∈[0,1]; θ within `[sector.from, sector.to]`;
re-division even (sector widths all = 2π/n); the kind-group '*' remainder catches unmatched kinds;
`bindings/` discovery is fail-loud on a malformed row. Run with the venv python.

**G2 · The square/structure half.** REUSE `contracts/ui_info.py:parse_ui_address` for path segments +
`suite.py:address_tree_distance`. NET-NEW in `projection.py`: derive an (i,j) grid cell per point from
its address path (recursive quadrant subdivision — the Morton/dyadic path), and emit `rings` as m/2
from the active n (replace the `rings:4` literal). The FE draws the grid inside the box, the circle
over it. SEQUENCE: after G1 (changes point shape → the suite guards it).

**G3 · Time-freed / relative centre.** `runtime/bridge.py` ~line 727: parse `?at=` (and `?center=`),
pass `now=` into `project()`; filter `stamped` to ts≤now. For an address-centre: add a branch where
radius = `address_tree_distance(centre, point)` + (later) cosine, instead of age. project() already
accepts now=; the handler override + the filter + the branch are net-new (small).

**G4 · Real-time pub-sub.** FE `LatticeView.tsx`: open an `EventSource('/api/stream')`, on each event
recompute that point's position and add it; advance `now` by a smooth client clock (rAF/eased), not a
refetch; retire the `setInterval(pull, 15000)`. REUSE the SSE handler `bridge.py:_stream` (~985) —
the same `events_since` tap. Keep the live/frozen toggle (freeze = unsubscribe).

**G5 · The FORM rebuild.** Rebuild `LatticeView.tsx` chrome (detail card, set-bar, foot HUD, error
state) on `components/kit.tsx` (Surface/Badge/SectionHead/EmptyState). Repoint the `token()` helper
off `--accent`/`--ink-dim` (DEFINED NOWHERE) to the real corpus tokens (`--acc`/`--tx`/`--bg` per
`design/design-system.css`). Move the ~37 literals out of the `.lattice-*` block in `app.css` (lines
~1811-1872) onto tokens. PRESERVE the angle-hue `hsl(θ)`. Verify: `design/_system/check.py` clean
against BOTH files; a separate design-critic on the whole screen at desktop AND 390×844. Exemplar:
`regions/Inbox.tsx` (layout-only CSS; look lives in `.kit-*`).

**G6 · Semantic radius.** NET-NEW: `radius_from=='semantic'` branch in `projection.py` reading
cosine-from-centre off the persisted index (`store.get_vector` + cosine, or `suite.query_corpus`); a
`bindings/semantic.py` row. REQUIRES G8 (a resident embedder + the query/centre embedded). REUSE the
relevance MATH from `suite.py:_r2_score` (not the function).

**G7 · Strain / forbidden zones.** NET-NEW: per point, compute square-position (G2) vs circle-position
(G6) disagreement; surface as a strain field on the render OR a `'strain'`/`'forbidden'` mark via
`mark_types.py` + `fs_store.append_finding`/`append_mark`. Render-not-judge; operator-overridable.
REQUIRES G2 + G6.

**G8 · Embedding substrate live.** OPERATIONAL: `company up embed-bge` (or the chosen embedder) via
`ops/cli/capabilities.py:ensure_resident`; a capture+embed pass (`cognition.py:embed_corpus_to_spaces`
/ `suite.capture_corpus`) over the `projections/` embeddable() lenses to populate the named spaces;
confirm `vector_index.index_staleness`. Mechanism is complete — this is running it, coordinated with
the retrieval/ops session.

**G9 · Two-gravity separator.** NET-NEW + GATED on Model Call 2. Thread an instruction/task parameter
through `fabric/transport.py:openai_embeddings_transport` → `client.complete_embeddings` →
`nodes/embed.py` CONFIG → `build_index` (cross-lane: fabric owner — coordinate). Build two lens spaces
(Tim-intent instruction, generic-AI instruction). Steering-vector: centroid(Tim-anchors) −
centroid(AI-anchors) = the axis; project each unit = signed scalar = its pull. The per-unit gap helper
is a thin sibling of `suite.find_relations` (cosine GAP, not set-difference). Anchors come from Tim.

**G10 · The event→row edge + order-from-edges.** NET-NEW keystone: formalize the event→registry-row
edge (this op.run → the role that fired it; via lineage/source_address). Then `_resolve_sectors`
gains angle_from=<registry-name> (sectors = that registry's rows) and order_by=typed-edge (order via
`relation_types` precedes/depends_on). REUSE `relation_types.py:RelationTypeRegistry`. Sequenced after
G1 (changes sector resolution → the suite guards it).

**G11 · Multi-scale pyramid.** NET-NEW: a sentence/turn chunker feeding `build_index(space=
'scale:<rung>')` per rung; a zoom-by-rung query. `build_index` is granularity-agnostic (caller
pre-chunks) — REUSE it; the chunking strategy + per-rung naming + zoom are net-new.

**Small registries + gate + 20/80 (last).** origins + axes registries (the dial/file-discovered
pattern); the promotion gesture (the act pinning a sample to the spine — the gate UI); the 20/80
pressure-threshold type-birth/death (the water-law n-increment under forbidden-zone pressure). GATED
on the axis-selection model call.

## What each change PRESERVES (enumerate before shipping)

- G2/G3/G10 change `project()` output shape → the Group-1 suite must stay green (r-bounds, θ-wedge,
  even division) through every one. That's the suite's whole job.
- G5 changes only LatticeView chrome → the lens switch, cycle frames, forager `builder-context` seam,
  recentre, live/frozen ALL still work (verify each by use after the rebuild).
- G4 changes the data source (poll→stream) → the projection payload shape is unchanged; only how the
  FE acquires it changes.
- Every instrument change keeps the floor: still a pure read, no consequential verb introduced.
