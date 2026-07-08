# AREA: design-machinery — `/home/tim/company/design/` (parent corpus, excl. claude-ds)

Reader scope: `_system/` machinery, `design-system.css`, root MDs (`conventions.md`, `README.md`,
`CONNECTION-CONTRACT.md`), `CLAUDE.md` (folder charter), a sample of `mockups/`, `blueprint/`,
`interface-mockups/`. Register: provisional — Observed/Inferred/Verified tagged throughout. This is
NOT confirming the anchor; several findings below complicate it.

---

## §A · What's here (dense account)

This folder is **two live address systems plus a third, half-documented one**, all generating off
`register.json` (Observed, `register.json`: 43 views, 76 features, 7 areas A–G, `sequences[]` = 9
named journeys J1–J9, a `coverage` map, a `status_flow`).

**1. `ui://` — the interface-element address (Observed, `_system/addresses.json`).**
Grammar (Observed, `CONNECTION-CONTRACT.md` §0, and `addresses.json`'s own `"scheme"` field):
`ui://<region>/<element>[/<sub>][@<state>]` for chrome, `run://<graph>/<node>[#<port>]` for live
canvas-node instances. 505 registered addresses (Observed, `len(addresses)`). Each entry:
`region · capabilities[] · represents · code · howto` (a fixed WHAT / WHAT-YOU-CAN-DO / HOW-TO-CHANGE-IT
prose triple), plus **inconsistently present** `provenance{}`, `roles[]`, `maps_to_feature` (see §C).
This is address-as-registry-row exactly like tokens/types elsewhere in the Company — "extend by
registration, run the script" (Observed, `conventions.md` L98-110).

**2. `code://` — the code-symbol address (Observed, `_system/symbols.py`, `code-symbols.json`).**
The REVERSE index of every `code:` ref in `register.json`/`addresses.json`: `code://<file-stem>/<symbol>`
→ `{file, symbol, kind, resolves, referenced_by[]}`. `referenced_by` 2+ = a shared symbol (ripple
signal). **X11 (built)** adds `semantically_nearest[]` — a SIBLING semantic edge (cosine via the
existing `nodes/embed`+`nodes/retrieve`, BGE-M3 @ :8001), degrading to *absent* (never fabricated) if
the embedder is down. Currently absent corpus-wide (Observed: `semantic_edges: 0` in the live
`code-symbols.json`) — the embedder was down at last generation.

**3. The structural code-dependency graph, symbol→symbol (Observed, `_system/codeedges.py` +
`code-edges.json`).** `depends_on[]` / `depended_by[]`, DIRECT edges only stored; transitive reach is
a bounded query (`codeedges.reach`, capped at `DEPTH` 2-3 hops, X17-configurable via
`CODEEDGES_DEPTH`) — an explicit, named **explosion guard**: "a reach that hits the bound is reported
`capped`, no silent truncation." This is the sibling of `code-symbols.json`, same `code://` id space.

**4. Two generator chains layered on top, one documented, one not.**
- **Documented** in `conventions.md`/`CLAUDE.md`: `tokens.json`→`emit.py`→`design-system.css` (the
  look); `addresses.json`+mockups→`parse.py`→`element-map.json` (the join); `register.json`→
  `gallery.py`→`index.html`; `refcheck.py` (forward drift), `symbols.py` (reverse index),
  `codeedges.py` (dep graph); `mechanisms.json` (a registry-of-checks, extend-by-registration,
  Layer-0-structural + a reserved model-augmentation layer per entry).
- **UNDOCUMENTED** in either file (Observed — absent from both the file-map and the operations list):
  `blueprint_emit.py` (register.json+addresses.json → `blueprint/component-inventory.json` +
  `blueprint/surfaces/<journey>/<view>.json`, per-view surface specs) and `navgraph.py` (reads
  `surfaces/` back + `register.json.sequences[]`, reconstructs the journey graph, PROVES it against
  the production contract). Also undocumented: the entire **registry-generation (RG) chain** —
  `parse.py --extract-candidates` (RG1) → `candidates.json` → a swarm role `register_element` (RG3,
  MAP/RG4 fan-out) → RG5 REDUCE dedup → `registry-generation.cascade.json` (RG7, the cascade
  declared as DATA, run via `runtime/cognition.run_cascade`) → Tim-approval (RG8) →
  `registry_writeback.py` (RG9: merges into `addresses.json`, STAMPS `data-ui-ref` into the mockup
  HTML, re-runs `parse.py`). This is a full **identity-minting pipeline with a human consent gate** —
  built, real, operator-only-floor, fail-loud on ambiguous element location — and it is invisible to
  anyone who reads only `conventions.md`/`CLAUDE.md` as instructed.

**5. `navgraph.py`'s tree/graph split (Observed, its own docstring, `_system/navgraph.py` L1-20) is
independently-arrived-at proof of the anchor's §3/§9 pattern**, built for UI journeys, not glyphics:
"a tree can't hold a real graph (a screen reached from N journeys; cycles). So: the DIRECTORY = the
spine (structure) · ADDRESS-REFERENCES = the cross-edges (the web)." It PROVES this concretely: view
C1 belongs to journeys J3/J5/J7 but lives on disk under exactly one (its "home journey"); the other
two memberships are recovered only from `cross_journeys[]`/`journeys[]` address-refs in the surface
spec, and an acceptance test verifies the reconstructed journey graph matches `register.json`'s
`sequences[]` exactly.

**6. `mockups/` self-description (Observed, sampled `A2-canvas-desktop.html`, `C1-inbox-desktop.html`,
`E1-fleet-desktop.html`).** Every mockup opens with a metadata comment: `REPRESENTS[]` (feature-id ·
what it surfaces · code ref), a "NO FICTION" honesty statement enumerating exactly what real states/
kinds are drawn (e.g. "node status dots are ONLY idle · ran · cached · stuck... 'await' is
INBOX/presence, never a node dot"). Elements carry `data-ui-ref="ui://…"` inline (13-28 refs/mockup
sampled). This self-describing-artefact discipline is the same "no fiction, ground in the inventory"
law as the glyphic corpus's own honesty rules.

**7. `blueprint/` (Observed, `blueprint/README.md`).** A THIRD spec surface: `component-inventory.json`
(region/element → rendering component, built|planned), `surfaces/<journey>/<view>.json` (43 files,
one per view). Its own README claims "the ui:// registry, 25 element/region addresses" — **stale by
20×** against the live 505 (see §C).

---

## §B · Joins to the one-math (concrete designs)

**B1 — `ui://` addresses ARE identity-by-registration, but the address string does NOT carry its own
ancestry (unlike `cv-address`'s mixed-radix `span(k,n,parent)`).** The grammar is capped at
`region/element/sub/@state` — three segments plus a state suffix, not an arbitrary-depth chain. The
folder DOES compute ancestry (Observed, `parse.py`'s `_CandidateExtractor._ancestor_address()`: "the
nearest STRICTLY-ABOVE frame carrying a data-ui-ref"), but it does so by **walking the live DOM tree
at parse-time**, never by decoding the address string itself. This is exactly the gap the brainwave's
§1/§7 close: under the one math, `ui://inbox/build-review/drill` would not need a DOM walk to find its
parent — the address itself, encoded as a `cv-address` span-chain, would carry `ui://inbox` and
`ui://inbox/build-review` as decodable prefixes, the same way glyphic block addresses carry lineage.
**Concrete design:** re-express `ui://` addresses as a `cv-address`-style mixed-radix path (each
segment is a `span(k,n,parent)` slot, with the CURRENT segment *names* kept as a friendly alias
resolving to the numeric slot) so `parse.py`'s ancestor-walk becomes `decode(address).parent` — a
pure function, no DOM traversal, no re-parsing needed when the mockup HTML nests differently.

**B2 — The registry-generation (RG) chain IS the anchor's §8 "groups are addresses too," already
built for one axis.** RG1→RG9 (extract candidate elements → swarm proposes a dossier → Tim approves
→ write back an address + stamp `data-ui-ref`) is literally "any group/filter/selection becomes
operable-as-one by REGISTERING AN IDENTITY," proven end-to-end with a human consent gate and
fail-loud ambiguity handling. **Concrete design:** the SAME cascade shape (declared as DATA, run via
`run_cascade`, gated by Tim-approval, write-back with provenance) is the mechanism for minting
addresses over glyphic fill-cells/groups too — not a new pipeline, a new INPUT SOURCE feeding the
existing RG3→RG9 spine (candidate units = addressed fill-cells instead of DOM elements; the writeback
target = the glyphic address registry instead of `addresses.json`).

**B3 — `navgraph.py`'s tree-is-spine/edges-are-web split is a WORKING, TESTED implementation of the
anchor's §3 spacetime/semantic split**, at a different scale. Anchor §3: "the spacetime layer need not
be STORED as edge records at all — it is DERIVABLE from the address math... Stored, declared
vocabulary remains only for SEMANTIC relations." `navgraph.py` does precisely this for journeys:
containment (home-journey = directory placement) is structural/derivable-by-location; cross-journey
membership (a view reachable from N journeys) is the declared, stored edge (`cross_journeys[]`) that
a tree topologically cannot hold. **This is not a new design — it is existing, proven evidence** that
should be cited directly when the spacetime/semantic split is specified for the glyphic address space,
including its acceptance-test PATTERN (reconstruct the graph from the tree+edges, prove it equals the
independently-declared ground truth — `register.json.sequences[]` here, whatever the glyphic
equivalent of a "journey contract" becomes).

**B4 — X11's semantic-edge pattern (`semantically_nearest[]` beside `referenced_by[]`, computed by
reusing `nodes/embed`+`nodes/retrieve`, degrading to *absent* not fabricated) is the template for how
the anchor's semantic layer should sit beside the derived spacetime layer.** Two SIBLING edge types
per node — one structural/derived (never touched by the model), one semantic/embedded (always
optional, always the SAME cosine path reused, never reimplemented) — is a pattern this folder has
already built and hardened (degrade-with-warning tested per its own docstring) for `code://`
addresses. The glyphic address space can reuse the identical shape: `contains/ancestry` (derived) +
`semantic-neighbours` (embedded, optional) as the two edge families per glyphic address, with NO
third "meaning" edge type invented (course-correction #3, the edge law — verbs need an opposite;
`semantically_nearest` sidesteps this entirely by being a RANKED LIST, not a typed verb-edge).

**B5 — `mechanisms.json`'s "Layer-0 structural, no models; a local-model layer augments each entry
later" pattern is the resolution-first floor the one-math's "ratios all the way, nothing hardcoded"
(§4) should sit on.** Every mechanism here is EXACT and FREE before any model touches it (refcheck,
symbols, codeedges are all pure functions over text/AST). The glyphic partition math (`span(k,n)`,
`zones(parts, axisPx)`) is the identical shape: a deterministic Layer-0 the corpus can trust
completely, with model judgement (which cell "means" what) strictly additive on top — never load-
bearing for the geometry itself.

**B6 — `check.py --target ... --fail-on` (the design-lint, "FORM gate") generalises directly to a
glyphic-geometry lint.** It already does "flag a SINGLE off-token occurrence, gate a build" for CSS/
colour literals; the identical shape (an addressed square/circle partition asserted by ratio, any
literal pixel/angle constant in a glyphic mark = an off-token/off-ratio finding) is a one-line
extension of an existing, tested mechanism — not new machinery.

**B7 — The Company's one-resolver spine is the actual convergence target for BOTH `ui://` and
`code://`, and `LEDGER-SPEC.md` §8 has already named this as an open, tracked gap** (see §C4): "code://
resolving into the ledger via `runtime/cognition.resolve_address`... closing the 'one resolver is
actually two' gap." This means the anchor's §7 ("identity = addressability... the deep join to the
Company's one-resolver spine, `resolve_address`") is not speculative — it is a **named, already-agreed
target** the design folder's own addressing machinery is waiting to be re-pointed at. The glyphic
address space joining the SAME spine is the third leg of a fusion already in motion for the other two.

---

## §C · Disconnected / unused / stale (evidence)

**C1 — `code-edges.json` and `code-symbols.json`, described as "SIBLINGS, one coordinate system," are
now generated by two DIFFERENT pipelines at wildly different scale, and no longer agree.**
Observed: `code-edges.json`'s own `_what` field says *"GENERATED FROM THE LEDGER (`ops/ledger_build.py
--emit-legacy`) — supersedes the standalone `codeedges.py` AST build. Whole-tree + resolved."*
Summary: `{"symbols": 4908, "source": "ledger"}`. `code-symbols.json` is still generated by the
ORIGINAL `symbols.py` (Observed, its own docstring, unedited) and its live summary reads
`{"symbols_indexed": 94, "semantic_edges": 0}` — a 52× scale mismatch against its stated sibling.
`codeedges.py`'s own docstring (Observed, L4-9) states: *"⚠ SUPERSEDED (2026-06-27)... This standalone
AST build is RETIRED, keep it only as reference/fallback."* `symbols.py` carries NO such notice and is
still the live generator for `code-symbols.json`.

**C2 — `LEDGER-SPEC.md` §8 (Observed, `build-prep/the-one-system/LEDGER-SPEC.md` L126-131) names this
exact gap as a decided-but-not-executed follow-up**: *"`design/_system/{code-symbols.json,
code-edges.json, field_index}` → superseded by `ledger.symbol` + `ledger.edge`. Re-pointing their
consumers (`codeedges.reach`/blast-radius, `refcheck`, `symbols.py`) onto the ledger is a **TRACKED
FOLLOW-UP** — not done this pass."* One half of that follow-up (`code-edges.json`) IS done;
`code-symbols.json`/`symbols.py` is NOT. This is not a hypothetical gap — it is a documented,
half-executed migration, sitting in the corpus right now.

**C3 — The corpus's own self-maintenance discipline (its central, repeatedly-stated law) has already
drifted, measurably.** File mtimes (Observed, `ls -la --time-style=full-iso`):
`addresses.json` 2026-06-28 (505 addresses) is NEWER than `element-map.json` 2026-06-10 (built when
`addresses.json` had 483 — Observed, the file's own `summary.registered_addresses: 483`). Per
`conventions.md`'s own rule ("Update register.json + re-run `gallery.py`/`parse.py` whenever a mockup
is added/changed... generated files never lag") and `CLAUDE.md`'s ("self-description out of date is a
DEFECT to fix loud, never leave") — `element-map.json` is currently stale by 22 addresses' worth of
growth, un-flagged, in the live corpus. `candidates.json` (2026-06-09) is even older; the RG chain has
not been re-run since, while `addresses.json` kept growing by other means afterward — meaning **not
all address growth since Jun 9 went through the documented RG1→RG9 pipeline**; some entries were added
by an unrecorded path.

**C4 — `blueprint/README.md` states "the ui:// registry, 25 element/region addresses" (Observed, its
own text) against the live 505** — a 20× stale count in a file whose entire purpose is to be "the
importable build-spec a fresh Claude Code session reads to build a faithful front-end" (its own
opening line). A fresh builder session trusting this number would radically under-provision.

**C5 — `conventions.md`/`CLAUDE.md` (the two files explicitly designated "read-first" and
"self-description that must never drift") do not mention `blueprint_emit.py`, `navgraph.py`,
`registry_writeback.py`, `registry-generation.cascade.json`, `corpus-meta.json`, `candidates.json`,
`orphan-routes.json`, `page_bindings.json`, or `generate-config.json` — roughly HALF the files present
in `_system/` (Observed: `_system/` contains 34 files; the documented chain covers ~14 of them). The
undocumented half includes two entire generator chains (the blueprint chain, the RG identity-minting
chain) that are fully built and, per C3, still partially active.

**C6 — Three overlapping field-names for the same relational concept inside `addresses.json` itself**
(Observed, direct sampling): `represents` (singular string, present on most entries, e.g.
`"represents": "RUN-run"`), `roles` (an array, e.g. `["CAN-compose", "WIRE-intent"]`, present on a
subset), and `maps_to_feature` (singular string, present on a different subset, e.g.
`"maps_to_feature": "EVT-now"`) — three different keys, from different generation waves
(`registry_writeback.py`'s own docstring names the RG3 output schema field as `maps_to_feature`, while
the ORIGINAL 82 curated entries and most later ones use `represents`). No single entry observed
carries all three; the corpus has not reconciled them into one canonical key.

**C7 — `provenance{}` is present on 402/505 entries but with NO fixed shape** (Observed: one entry
carries `{"howto_filled_by": "rg10-curated-pass..."}`, another carries `{"run": "rg10-refined",
"model": "chat-4b..."}`) — different keys per wave, and neither instance carries "the confidence" that
`registry_writeback.py`'s own docstring promises every merged entry will record ("which `run://`
produced it, which model, the confidence"). The promised contract and the actual data disagree.

**C8 — `CONNECTION-CONTRACT.md`'s projected union record (§1) documents a `states[]` field and a
`kind` field as part of "the canonical address grammar," but ZERO of the 505 live `addresses.json`
entries carry a `states` key** (Observed, grep count = 0), and `kind` is explicitly noted in the same
document as "absent from the compact corpus rows... the S0 projection adds it." The contract's "IS"
tag on the read fields overstates what the raw corpus rows actually store — the union shape is
produced only by a projection step, not present in the source of truth itself.

**C9 — X11 semantic edges are built (code, tested per docstring) but currently DEAD in the live
artefact**: `code-symbols.json`'s summary reads `semantic_edges: 0` — the embedder (`:8001`) was down
at last generation, so every entry lost its `semantically_nearest[]` silently-to-the-file (loud in the
run's stderr, per design, but the artefact on disk shows no trace it was ever attempted).

---

## §D · Law-candidates (recurring principles worth naming)

**D1 — "The tree is the spine; edges are the web."** Observed independently in THREE places: (a)
`navgraph.py`'s own stated law ("a tree can't hold a real graph... DIRECTORY = spine, ADDRESS-REFS =
cross-edges"), proven with an acceptance test; (b) `LEDGER-SPEC.md` §1 ("the path-tree is one
dimension (the anchor); typed edges add the others... completeness becomes a diff, not a claim"); (c)
the anchor itself, §3/§9 ("the containment tree is the spine of every axis," spacetime derivable from
ancestry vs. semantics stored as declared edges). Proposed law: **A hierarchical container (directory,
DOM, address-ancestor-chain) gives exactly ONE relational dimension for free — containment/depth/
order. Every OTHER relationship a node has (multi-membership, cross-reference, semantic likeness)
MUST be a separate, typed, stored edge, because a tree is topologically incapable of representing
multi-parent membership or cycles.** This is not a preference; `navgraph.py`'s own proof (view C1 in
three journeys, recoverable only from address-refs) is a structural demonstration, not an opinion.

**D2 — "Structural first, semantic second, never merged, always degrading honestly."** Observed in
`symbols.py`/X11 (referenced_by = structural, semantically_nearest = semantic sibling, ABSENT not
fabricated when the embedder is down) and in `mechanisms.json`'s own registry shape (every mechanism:
`layer: structural`, with a reserved `model_augmentation` note — none of the three registered
mechanisms have their model layer built yet, all three have it *specified*). Proposed law: **Any
analysis mechanism ships its deterministic/structural layer FIRST and completely, with the semantic/
model layer registered as a NAMED, OPTIONAL sibling from day one — never retrofitted, never blocking
the structural build, and its absence must be loud (a summary count of 0, not a silently-missing
key).**

**D3 — "One relational concept, one field — never a synonym-per-wave."** Observed as a violation
(§C6: `represents`/`roles`/`maps_to_feature` all encoding "which feature(s) does this address serve"),
which is direct, concrete evidence FOR the anchor's own §5 ("purpose = names attached to addresses...
it's just names attached to addresses" — implying ONE address, many NAMES layered over it, not many
FIELDS competing to be the name). Proposed law: **When a corpus grows across multiple generation
waves, a new wave that needs "the feature this address represents" must extend the EXISTING field
(or explicitly deprecate+migrate it), never add a new key with the same meaning. A registry with two
names for one relation is drift, not richness.**

**D4 — "A capped/bounded query beats a precomputed closure."** Observed in `codeedges.py`'s named
`DEPTH` constant (2-3 hops, X17-configurable, reach reported `capped` not silently truncated) and
explicitly reasoned about ("a transitive code-dependency graph can degenerate to all-touches-all... we
do NOT precompute the transitive closure into the file — that is exactly where the explosion would
live; the bound lives in the query"). Proposed law, directly relevant to the one-math's groups/cascade
axis (§8, LCA-based cascade certainty): **A relational query over an address space with ancestry
(reach, blast-radius, group-cascade) must be a BOUNDED, on-demand traversal with an honest "capped"
signal — never a precomputed, unbounded materialisation that silently degenerates when the graph gets
dense.**

**D5 — "Self-description drift is measurable, not just asserted."** `CLAUDE.md`'s own words ("self-
description out of date is a defect to fix loud, never leave") are, per §C3/§C4/§C5, currently
violated in exactly the file that states the rule. Proposed law (a sharpening, not a new law):
**"Self-description must never drift" needs a CHECK, not just a charter sentence** — the same
Layer-0-structural-mechanism pattern (D2) applied reflexively: a mechanism that diffs a folder's
documented file-map against `os.listdir()`, and its documented counts (address counts, symbol counts)
against the live registries, on the same cadence as `check.py`/`refcheck.py`. Without this, the
"never drift" law has no enforcement arm and drifts anyway (as measured, twice, above).

---

## §E · Scope additions (what must enter the build)

1. **Re-express `ui://` (and by extension `code://`) as a `cv-address`-decodable path**, so ancestry is
   read FROM the address (decode), not recomputed by walking the DOM/mockup structure per parse. This
   retires `parse.py`'s `_ancestor_address()` DOM-walk as the ONLY source of lineage — it becomes a
   cache/fast-path over what the address itself can already answer.
2. **Finish the LEDGER-SPEC §8 tracked follow-up**: re-point `symbols.py`/`code-symbols.json` onto
   `ledger.symbol`, the same way `code-edges.json` was already re-pointed onto `ledger.edge`. Until
   this happens, any consumer treating `code-symbols.json` and `code-edges.json` as "one coordinate
   system" (as both files' own docstrings claim) is working with two systems at 94 vs 4908 symbols.
3. **Reconcile `represents` / `roles` / `maps_to_feature` into one field** across all 505 addresses
   (a corpus migration, not a design decision — the target shape already exists, it's a matter of
   which name wins and a script to fold the other two into it).
4. **Build the reflexive self-description-drift check (D5)** as a new entry in `mechanisms.json` —
   Layer-0, structural, no models: diff `conventions.md`'s documented `_system/` file list against
   `os.listdir(_system/)`, diff any hardcoded address/symbol COUNTS in prose (`blueprint/README.md`'s
   "25 addresses," etc.) against the live registry lengths, fail loud on mismatch.
5. **Document the two undocumented chains** (blueprint_emit.py/navgraph.py; the RG1-RG9
   registry-generation cascade) in `conventions.md` and `CLAUDE.md` as first-class citizens — they are
   real, built, and (per B2/B3) directly load-bearing for the one-math build, not peripheral.
6. **Adopt X11's structural/semantic sibling-edge shape (D2) as the template** for whatever the
   glyphic address space's own semantic layer becomes — reuse `nodes/embed`+`nodes/retrieve`
   verbatim, do not reimplement cosine ranking a third time.
7. **Adopt `codeedges.py`'s bounded-reach pattern (D4)** as the mechanism for the anchor's §8 LCA
   cascade-certainty queries over glyphic groups — a named DEPTH, a `capped` flag, never a
   precomputed closure.
8. **Re-run `navgraph.py`'s acceptance-test PATTERN** (reconstruct a graph from tree+edges, prove it
   equals an independently-declared ground truth) as the acceptance test shape for the glyphic
   spacetime/semantic split once it's built — the pattern, not just the citation, should carry over.
