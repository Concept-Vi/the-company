# Registry-Generation Chain — Completion Criteria (the truth-table)

> The bar for V-A: the swarm reads the surface → proposes registry entries → Tim approves → the registry grows →
> previously-dead elements resolve richly. Companion to RESEARCH-SYNTHESIS.md (evidence) + IMPLEMENTATION-GUIDE.md
> (how). EVERY criterion two-faced (FUNCTION by-use + FORM the operator face). Marks: ✅verified-by-use ·
> 🟡built-untested · 🔴not-built/needs-tim. No green-paint. Laws: registry-is-truth · no-hardcoding · operator-only
> floor (PROPOSE never auto-write) · no-fiction (feature-inventory grounded) · verify-by-USE · reuse-not-parallel.
> Cross-lane: [M]=mine(guided-review) · [C]=cognition's parallel loop · [J]=joint (the cascade + whole-by-use).

## Priority order (dependency)
RG1 EXTRACT → RG2 GROUND → RG3 register role → RG4 MAP → RG5 REDUCE(dedup) → RG6 CONFIRM → RG7 cascade →
RG8 PROPOSE-surface → RG9 write-back+round-trip → RG10 whole-by-use → RG11 generalize. (RG1/RG8/RG9/RG10 mine;
RG3/RG4/RG5/RG6 cognition; RG7/RG10/RG11 joint.)

## RG1 · EXTRACT — the candidate-element units (the allocation source) · [M] · 🔴
- **FUNCTION:** a `parse.py` pass over the 23 mockups emits the MEANINGFUL elements (buttons, named sections,
  controls, semantic headings; SKIP layout-only divs/spans) as units: `{mockup_file, selector/path, outerHTML
  (bounded), visible_text, tag/role, nearest_registered_ancestor(+its dossier), mockup_base_address}`. Verified
  by use: run it → N≈200-600 units, each with the fields, noise filtered, written to a candidate file.
- **FORM:** N/A (data) — verified structurally (the units are well-formed + the count is sane vs ~3000 raw).
- *Reuse:* EXTEND parse.py (no parallel parser). *Status:* 🔴.

## RG2 · GROUND — per-mockup summaries · [M→reuses C's screen_reader] · 🔴
- **FUNCTION:** `run_role(screen_reader)` × 23 mockups → a per-mockup at-altitude summary, cached as shared
  context for that mockup's elements (each element understood in its screen's purpose). By-use: 23 summaries land.
- **FORM:** N/A. *Reuse:* screen_reader (built). *Status:* 🔴.

## RG3 · The `register_element` role · [C] · 🔴
- **FUNCTION:** `roles/register_element.py` — input: element snippet+text+role + parent dossier + mockup summary +
  corpus exemplars + feature inventory. output_schema `{address(proposed), represents, howto{what,what_you_can_do,
  how_to_change}, capabilities, maps_to_feature|proposed, confidence}`. Op:generate, mode_scope incl. a
  registration context. By-use: fire it on one element → a well-formed dossier grounded in the element (not fiction).
- **FORM:** the dossier reads at-altitude (matches the 82 existing entries' voice). *Reuse:* mirrors screen_reader.
  *Status:* 🔴 [C] (roles/ = the C seam — cognition builds or I build with their say). Reflected in roles/AGENTS.md.

## RG4 · MAP — register every candidate concurrently · [C/J] · 🔴
- **FUNCTION:** `run_items(register_element, units)` → N proposed dossiers at `run://<turn>/register_element/<i>`,
  concurrent on the swarm, each grounded per RG3's context. By-use: a real N-unit run → N dossiers, swarm-fanned,
  no-fiction holds (spot-check: an un-built element marked `proposed`, not invented).
- **FORM:** the run is visible in CognitionView (the swarm working). *Status:* 🔴.

## RG5 · REDUCE — dedup + nest + merge · [C/J] · 🔴
- **FUNCTION:** `run_reduce` does three jobs: (a) **cluster** (embed-dedup): same surface across mockups → one
  entry (ui://inbox in C1 & C5 → merged); (b) nest/validate: parent→child tree, each address checked vs
  `contracts/address.py` grammar, collisions resolved; (c) merge duplicate howtos. By-use: feed N with known
  duplicates → reconciled set has the dup collapsed + a valid tree.
- **FORM:** N/A. *Reuse:* run_reduce cluster mode (Observed). *Status:* 🔴.

## RG6 · CONFIRM — the no-fiction / accuracy gate · [C/J] · 🔴
- **FUNCTION:** a jury / stronger-model + `refcheck.py` pass over the reconciled set: represents accurate? howto
  grounded (code ref resolves via refcheck; capability in the feature inventory)? variance/low-confidence →
  FLAGGED not dropped. By-use (adversarial): a fabricated capability → caught/flagged; a real one → passes.
- **FORM:** flagged entries are visibly marked for extra Tim scrutiny. *Reuse:* run_jury + refcheck. *Status:* 🔴.

## RG7 · The chain is a DECLARED CASCADE (re-runnable, not hardcoded) · [J] · 🔴
- **FUNCTION:** extract→ground→map→reduce→confirm declared as a saved cascade (`save_cascade`); `run_cascade`
  fires it end-to-end, `run://` wiring output→next-input, each step persisted. Re-runs when mockups change. By-use:
  `run_cascade` over a 2-mockup slice → the full pipeline runs, the reconciled+confirmed set lands at run://.
- **FORM:** N/A (the cascade is data) — but it's `list_cascades`-discoverable + re-runnable. *Reuse:* the cascade
  runner (Observed `91dbee8`). *Status:* 🔴 [J] (the definition is data; I author it, cognition's engine runs it).

## RG8 · PROPOSE → operator (the floor; the batch-review surface) · [M] · 🔴
- **FUNCTION:** the confirmed set surfaces as a BATCH `review` decision (governance inbox) — NOT auto-written.
  Tim walks the proposed entries + approves once (simple-consent). By-use: a confirmed set → one inbox item →
  approve → the write-back (RG9) fires; reject → nothing written.
- **FORM:** a navigable batch-review surface (on the review surface / inbox) — the operator SEES each proposed
  dossier (represents + howto, plain), grouped, with the ONE approve gate + per-entry skip; not a JSON wall.
  design-critic + by-use. *Status:* 🔴 [M]. The *feel* of reviewing a batch = 🔴 needs-tim.

## RG9 · WRITE-BACK + round-trip (registry grows; elements get addressed) · [M] · 🔴
- **FUNCTION:** on approve → merge the entries into `addresses.json` (the canonical registry) + stamp the
  `data-ui-ref` attributes into the mockup HTML files + re-run `parse.py` so `element-map.json` regenerates.
  Provenance per entry (run://, model, confidence). By-use: approve a batch → addresses.json gains the entries +
  the mockups gain the refs + a previously-unregistered element now carries a real ui:// + resolves via address_help.
- **FORM:** N/A (data) — verified by RG10 (the element now resolves richly). *Status:* 🔴 [M].

## RG10 · WHOLE-by-use — a dead element comes alive · [J] · 🔴 the gate
- **FUNCTION:** the end-to-end proof: pick a currently-unregistered element (e.g. C1-inbox's "layers" button) →
  run the chain → approve its proposed entry → reload the studio → click that element → it now resolves to a REAL
  dossier (the RHM answers from `represents`/`howto`, NOT V-B's HTML-fallback). The registry grew itself, operator-gated.
- **FORM:** the operator clicks the once-dead element and gets a rich, registered answer. design-critic + chrome.
  *Status:* 🔴 [J] — the convergence-round seam (my surface × cognition's engine). The *feel* = needs-tim.

## RG11 · GENERALIZES — register-a-surface is a faculty (not a mockup one-off) · [J] · 🔴 forward
- **FUNCTION:** the same chain (read elements → propose → reduce → confirm → operator-approve) runs over the LIVE
  app surface (running DOM + code refs), not just mockups — a reusable "register a surface" capability. By-use
  (later): point it at a live surface → proposed live-element registrations. *Status:* 🔴 forward — scope it, don't
  block V-A on it. Marks the chain as general, per the V-D address-as-junction + the substrate-retrieval placeholder.
