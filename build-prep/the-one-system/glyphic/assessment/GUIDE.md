# IMPLEMENTATION GUIDE — per group: files, seams, reuse, traps

> Companion to SYNTHESIS.md (why) + CRITERIA.md (what done means). Sources of truth: the five
> AREA companions (file:line evidence lives there — cite, don't re-derive).

## W0
- `.d.ts`: core/cv-nodes.d.ts — add `"glyphgraph"` to CVGraphType; add `line/direction/routing/lineColor`
  optional fields on CVGraphEdge (shapes per DiagramSolver's glyphGraphView consumption, AREA-D).
- gpu_util: ops/services.json → chat-4b-fp8.config.gpu_util (or `company config chat-4b-fp8 gpu_util 0.44`)
  — the value 0.44 is the service's own migration note (AREA-C). Board-announce (services.json is a named
  collision surface). Do NOT restart anything running hot without checking `company status` first.

## W1 (all ports: COPY from counterpart @ its current commit, provenance header `ported-from:
counterpart/design@<sha> <path>`; never edit the source repo — ④ is live in it)
- cv-organisms: source surface/runtime/organisms.js (894 lines, IIFE, window.DNA.org). Re-point colour:
  `--dna-gold`→`--accent-gold` etc. (~30 refs; map against colors_and_type.css names; keep a token-map
  comment block at top). Keep the seeded RNG (determinism = derive-never-place in time). Harness page in
  _demo/ for the render check; run design/_system/check.py --target on it.
- cv-address: port zones()/span arithmetic + add lca(addressA, addressB) (the tree-walk on nested
  fractions). Keep the proof harness as _demo/verify_address.js (node-runnable, like verify_language.js).
- cv-arc: port the planner; rename deck-page-kinds → growth-event-kinds (open/argue/show/prove/plan/
  people/close stay as the seed vocabulary until the glyphgraph's own arc vocabulary is authored — it's
  DATA). Proofs as _demo/verify_arc.js.
- cv-edges verb facet: additive fields on resolve(); the 4 existing kinds keep exact behavior (boot-check
  the writer + language.html after).
- TRAP (AREA-B): counterpart's tokens.json is mid-edit by ④ — do not port token VALUES this phase, only
  machinery. The tokens diff is a flagged follow-up, not a W1 item.

## W2
- Stable-slot-by-address: DiagramSolver.jsx glyphgraph branch — today `ci` = author-order index at a fixed
  pitch (AREA-D traced it). Change: node.address (from cv-address, assigned at insertion, FROZEN) → slot.
  A drag writes nd.x/nd.y (the authored-override branch that already exists). Rank recompute (longest-path)
  becomes initial-placement-only.
- Growth animator: on graph change, diff by node.address; movers get FLIP-style transforms (measure→apply);
  the LCA of changed addresses is the boundary that must NOT move (assert it). Respect the change budget
  (cap simultaneous movers; batch if exceeded — motion.json's law).
- Fields: new axes/ordinal/ordinal-axis.js — values = ramp stops (from the axis_ramp), monotonic-lightness
  enforced at registration (loud). Paint via the zone-wash color-mix mechanism (containers.css:76-92
  pattern), driven by telling-order (the arc resolver's output), NOT by hand.
- Read-out coverage: the auto-focus walk drops clauses (FINDINGS-LOG:42) — per-edge subgraph reads joined
  (the proven the-whole-thing.html pattern) as the coverage floor; the chained walk stays for paths.
- TRAP (AREA-E): do NOT touch register/wording beyond coverage — that's W5, Tim's ear.

## W3
- Recomposition order: containers first (Band/Zone/Cluster with computed depth), then chrome (CanvasHeader),
  then the panels (RefinePop for per-item refine; Icons.jsx .dsa-gen-panel pattern for propose→adopt).
  The writer's LOGIC (compose pipeline, session substrate, teach/persist) is sound — the SHELL changes.
- Sockets: glyphic-type.js subscriptions replace hand-enumerated chip lists (AREA-A named the exact lists).
- Relation-teaching: on unresolved phrase (the existing loud toast), offer teach → glyphic.author-relation
  ({id, feeling(noun-phrase!), senses}) → persistGloss-equivalent for relations → re-write. The feeling-
  must-be-noun-phrase law (taught to ④) applies.
- Icon-gen fusion: extract writer's makeIcon into a shared module (app/ai/ or a component); Icons.jsx and
  foundry call it. One engine, three doors — or fewer doors if the Studio pattern absorbs the foundry page.
- Production shell: the vite instrument-surface (:5174) is the precedent — precompile the writer (its React
  use is modest) or serve compiled assets; kill unpkg. CSP-clean, offline-tolerant. This is a developer
  call (mine), not Tim's.
- Studio/gallery: an app canvas entry (thin — mounts the same writer) + @dsCard. Boot-check: 55+ caps
  distribution unchanged; gallery scan picks the card up.

## W4
- Mode: modes/<id>.py is file-discovered (AREA-C verified) — modes/glyphgraph.py {directive, consent:'act',
  voice on}; services.json combo `glyphgraph {extends: interaction}` (APPEND; board-announce; the gpu_util
  fix from W0 is what makes it fit).
- Burst-at-pause: the judge's finished-thought boundary is the trigger (built, measured — AREA-C); fire
  glyph_extract (+relations later) via run_swarm at that seam; glyph_compose judges the burst.
- voice.transcript: ONE `_emit("voice.transcript", …)` at the STT-return point AREA-C located; rides the
  existing SSE. Ping the ledger thread first (their overnight P2 touches the bridge) — additive route,
  different path, but announce.
- Reindex route: bridge route calling emit_glyph_corpus (node) + build_embeddings --space glyph_meaning
  (python) — subprocess with loud capture; POST-only; document in the writer's toast (replace the
  shell-command toast).
- Persistence: file the board ask (AREA-C's sharpened form: "can a glyph edge ride ledger.assertion —
  authored-edge-with-provenance, validated against edge_kinds — or does a glyphgraph need its own table?")
  linked to item-ecb0b169; build AFTER the answer (address scheme: glyph://graph/<id>? — settle with the
  one-resolver owner).

## Standing traps (from E)
services.json = append+announce · migrations next-free-at-write-time, never assume 00NN · stay additive on
ledger.embedding; reads via ledger.query when it serves · counterpart = read-only, port-by-copy · the CDN
scaffold must not spread to new pages (W3 kills it; until then, no new page uses unpkg) · every port keeps
its proof harness runnable in _demo/.
