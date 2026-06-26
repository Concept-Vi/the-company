# FINDS — DNA (ch-ovxwz8k8)

*Per-member append-only finds file (no concurrent-edit races on the shared DISCOVERY_LOG). DNA owns this file; the lead reads across all finds/*.md to synthesize convergences into DISCOVERY_LOG + EMERGING_SHAPE. Finds not conclusions; honest verification-state; nothing final ([[feedback-confident-not-correct]] generative form). Format per find: what · where(path) · verbatim-if-quotable · verification-state · what-shape-it-points-at.*

---

## ROOMS — a built spatial-navigation shell (= F7's "running shell in counterpart/design")
- **WHERE:** `counterpart/design` — `ui/rooms/shell.js` (DNA.rooms) + `rooms.css` (#roombar).
- **WHAT:** four rooms — Gallery · Bench · Map · Almanac (+ Atlas overlay) — as OVERLAYS over ONE canvas (gallery = room 1, never moves; others slide over it). Slide DIRECTION derives from where-you-came-from; spatial_persistence; rooms are registry citizens `{id, order, icon, mount/enter/leave}`; deep-linkable `#room=<id>`.
- **VERIFICATION-STATE:** verified-by-use (running; desktop + mobile).
- **VERBATIM (shell.js):** "Rooms are PLACES (spatial_persistence): overlays slide over the gallery on one canvas; the slide DIRECTION comes from where you came from (arrival_relative_to_path: a transition is a property of the EDGE). The gallery is room 1 and never moves."
- **WHAT SHAPE IT POINTS AT (loosely):** "one addressed canvas; move between places by camera-direction; transition = a property of the EDGE; each place is a projection." = the SAME spatial-navigation shape as projection's "open onto a SPACE not a screen" (F5) + the graph-of-minds drill-in/out (F11) + address-navigation — reached from the ROOMS end. Convergence on the spatial-navigation shape, now 4+ sources. ★ Note "transition = a property of the EDGE" ≈ the connection-tuple (CAND-13) — the edge carries the transition.

## THE ENGINE UNDER THE ROOMS (the "18 registries")
- **WHERE:** `dna/` (roles · types/edges · dials · grammar · tokens · layouts · application · invariants) + `ui/surface.js` (the resolver + splitPane/pinchZoom/control/story).
- **VERIFICATION-STATE:** built (running shell); per-registry verification TBD.
- **SHAPE:** the resolver + registries under the rooms = composition's resolver+registry shape, reached from DNA's end. The rooms are projections; surface.js is the resolver; dna/ is the typed substrate.

## (earlier finds — see DISCOVERY_LOG F10/F12: presentation-as-data layouts.json · 73 reference screens · organisms.js · the identity/voice resolution layer + DNA's 4 axes · the gallery viewer · the parked polarity/inversion theory · surface-vs-projection types · content↔identity split)

---

## VAULT STRUCTURAL DIG (semantic deferred — :8007 busy with recollection's backfill, not competing)

### visual-design-corpus — a DB-backed "Spaces"/composition corpus (1244 files); ★ likely CROSS-DOMAIN
- **WHERE:** substrate vault `visual-design-corpus`.
- **WHAT (structural only):** 1244 files, **1127 in a "Spaces" folder**, 7498 chunks. Schema axes are DATABASE/SUPABASE-VALIDATION fields (columns/constraints/fk/rls/realtime expected-vs-found · validation_state · schema · migration_address · template_version). Relation-kinds include **specifies-resolution-of · related-contract · template · conventions · example**. 1 open seam.
- **VERIFICATION-STATE:** structural-only (haven't opened a Space; embedder down — provisional).
- **WHAT SHAPE IT POINTS AT (loosely):** "composed Spaces stored AS DATA in a database, with validation-contracts + templates + a *specifies-resolution-of* relation." That is the **content-as-data / central-database / composition-as-registry** shape — and *specifies-resolution-of* ≈ DNA-resolution-binds-to-data (my content↔identity seam). ★ **CROSS-DOMAIN FLAG (for the lead to route):** this reads as COMPOSITION's substrate (or shared), not pure-DNA. If it is the live "central database" Tim referenced for content, it's a major substrate find — composition to claim/confirm.

### vi-context-design — surface-design context, 37 open seams (140 files)
- **WHERE:** substrate vault `vi-context-design`.
- **WHAT (structural):** 140 files; folders "07 — Unarticulated" · "08 — Edge Cases" · _agent · notes · _templates. Relation-kinds are SURFACE-oriented (**surfaces · surface_affected · ripples_back_to · reads_from · writes_to · resolves**). **37 OPEN SEAMS.**
- **SHAPE (loosely):** a design-context vault *about surfaces* (which surfaces an idea affects, how it ripples back, reads/writes) — interface/surface design reasoning, with many unresolved seams. Likely holds interface-relevant design context; needs a semantic pass.

### visual-dna — MY OWN vault, structurally mapped (727 files); the architecture/canvas/voice notes live here
- **WHERE:** substrate vault `visual-dna` (= the DNA segment's own knowledge vault — on-territory, not another building).
- **WHAT (structural, GPU-free `get_vault_landscape`):** 727 files. Folders: notes:330 · _system:142 · **Build:74** · outbox:38 · **Theory:25** · Proto:24 · **Augmented-Canvas-System:17** · **ElevenLabs-Wizard:13** · Templates:12 · **Architecture:11** · **Product:10** · MOCs:9 · References:5. open_seam_count **0**. relation_kinds: adjacent-shapes · attack-status · cross-references.
- **TOP-REFERENCED (the load-bearing notes):**
  - `Meta/rules-governance.md` (473 refs) — governance spine.
  - `Theory/universal-mechanics-of-relativistic-coherence.md` (191) — my own four-axis/coherence theory ground.
  - `Architecture/architecture-canonical.md` "Visual DNA — The Unified Architecture" (158) — ★ the unified-mechanism architecture note; directly the shape this session is hunting.
  - `Build/content-workbench-source-of-truth.md` (129) — ★ content-as-data / workbench source-of-truth; directly the central-DB/content rung for the 73-rebuild.
  - `References/cognitive-entanglement-raw-input-01.md` (79).
  - `Product/conversational-graph-traversal.md` (71) — graph-traversal-as-product; the spatial-navigation shape from the product end.
- **VERIFICATION-STATE:** structural map verified (landscape call ran). Note CONTENTS not yet read.
- **GPU-FREE UNLOCK:** filesystem addresses now known (e.g. `filesystem://visual-dna/Architecture/architecture-canonical.md`). Reading a *known* note by address is a DB/file read, NOT an embedding op — so the canonical notes can be read directly NOW, without the :8007 window. (Only `search_semantic` — open-ended similarity — needs the embedder.) → probing this; the architecture + workbench notes are the first GPU-free reads.
- **STILL DEFERRED (SEMANTIC pass only):** open-ended `search_semantic` over the 727 (find notes I don't already have an address for) waits for the lead's :8007 window (recollection's backfill has it; not competing). Targets for that pass: Augmented-Canvas-System/ + ElevenLabs-Wizard/ older interface/canvas/voice notes the lead flagged.
