# Overnight loop — ALL pyramids + ALL wirings (Tim's go, 2026-07-03 night)

*Tim: "yeah do all the pyramids, all the wirings — do all of that. Give yourself a loop prep, I'm going to
bed. Coordinate with 4 and glyph." Verification bar: every criterion BY USE (a real query, a real render of
output, a real fire) — never code-exists. Commit per criterion to main. Coordinate: ④ (ch-kszn4a1c) is
loop-prepping the window — ping each landing so its Research Synthesis stays current; Glyphic (ch-518m76r0)
is additive-only (no collision). No live-surface changes; the loop switch stays OFF (Tim's).*

## P1 · THE FOUR MISSING PYRAMIDS (the zoom over the code-side lenses)
- [x] P1.1 `scale:docs:*` — pyramid over docs (679 units, pplx/2560): rungs per the ladder rule (~k32/k8);
      centroids in ledger.embedding + membership in cluster_member (reconciled counts, RAISE on mismatch);
      VERIFIED: a drilled query over docs returns on-topic hits with the drill in meta.plan.
- [x] P1.2 `scale:desc:*` — same over desc (1043, pplx).
- [x] P1.3 `scale:code:*` — same over code (1042, nomic/3584 — the FIRST non-pplx pyramid; proves the
      dim-agnostic path).
- [x] P1.4 `scale:symbol:*` — same over symbol (6201, nomic/3584; the big one — kmeans path).
- [x] P1.5 build_scale_pyramid EMITS cluster_member rows going forward (no new sidecars; the sidecar
      writer retired-commented per the no-fallback rule).
- [x] P1.6 pyramid-rebuild registered as a JOB (handler), trigger PROPOSED (never self-armed).

## P2 · THE WIRINGS (the window's text-in feed + embedder routing)
- [x] P2.1 `/api/query` bridge route: text-in → server-side embed → ledger.query → results (the UI face
      of the one function; loud teaching errors pass through). VERIFIED with curl.
- [x] P2.2 embedder ROUTING by space in the shared face(s): code/symbol → nomic (ollama :11434,
      num_ctx set), everything else → pplx (:8007). One routing table, used by /api/query AND the
      coordinate tool (no second dialect). VERIFIED: a text query over space='code' returns real code hits.
- [x] P2.3 the `coordinate` MCP tool passes ALL v2 axes verbatim + uses the routing table.
- [x] P2.4 golden-spec acceptance test: tests/ledger_query_acceptance.py — one spec per axis + the full
      composition + the teaching refusals (bad key/count.by/direction/depth) + plan-echo assertions. GREEN.
- [x] P2.5 (stretch) `semantic.text` accepted INSIDE ledger.query spec? NO — decided against: the fn stays
      pure SQL (no http from Postgres); text-in lives at the faces (bridge + tool). Recorded as the design.

## P3 · COORDINATION + CLOSE
- [x] P3.1 ④ pinged per landing (P1 batch + P2 batch); Glyphic informed of new scale spaces (their
      glyph_meaning can pyramid the same way when they're ready).
- [x] P3.2 STATUS.md updated; board note filed; everything committed; working tree clean of my files.
- [x] P3.3 the morning message to Tim: what landed, what's verified, what waits on him.

## Priority: P1.1→P1.2 (small, prove the chain) → P1.5 (rows-forward) → P1.3→P1.4 → P1.6 → P2.1→P2.4 → P3.
## Loop mechanics: ScheduleWakeup self-paced; each wake = build next unchecked criterion, verify BY USE,
## commit, tick the box here, ping ④ if it changes their synthesis. GPU note: pplx (:8007) + ollama nomic
## (:11434) both up; the pyramids only READ vectors (from pg) + embed NOTHING new (centroids are means) —
## no GPU pressure. If an embedder is needed for verification queries, both are resident.
