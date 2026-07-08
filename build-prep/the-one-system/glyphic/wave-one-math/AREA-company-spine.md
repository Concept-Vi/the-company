# AREA — Company relational/address spine (code side) vs the ONE-MATH brainwave

Territory: `/home/tim/company` code (NOT `design/`) — the address grammar, the resolver, the
relation/edge vocabularies, the glyph_* roles, the glyph_meaning embedding space, and the
container/ledger schema that carries addresses. Read against `BRAINWAVE-ONE-MATH.md` (full) +
`feedback-glyphic-course-corrections.md`. All file:line marked Observed unless noted Inferred.

## §A · Account — what's actually there

**The address grammar (`contracts/address.py`) is much bigger than the anchor implies.** The
anchor's §7/§8 speak of `ui://`/`code://` as the design-side's address vocabulary needing to join
"ONE address space." On the Company side that ONE space already exists and is far along:
`SCHEMES = (run, cas, blob, vec, ui, code, skill, context, guide, session, cap, board, clone,
mind, exchange, file, project, vi-vision, decision, image, extraction, path, mesh)`
(`contracts/address.py:162`) — 22 registered schemes, each with a documented grammar note (added
incrementally, one paragraph per scheme, in the file's own history — this file IS the address
law's changelog). Every scheme is dispatched through exactly ONE resolver:
`runtime/cognition.py:resolve_address` (`runtime/cognition.py:1153`), which the file's own
docstring calls "the EXTENSIBLE SEAM" — unknown/unregistered schemes FAIL LOUD (never silent),
and adding a resolver is "add a dispatch branch here." I traced the branches for
session/cap/board/clone/mind/vi-vision/decision/extraction/project (`runtime/cognition.py:1210
-1480`ish) — each is a lazy-imported registry read that raises on unknown, never fabricates
(registry-is-truth, the same law that governs roles/skills/relation_types).

**Ancestry-in-the-address is not aspirational — it is already built and already a LAW in one
place.** `project://<key>[/<scope-path>[/<resource-key>]]` (`contracts/address.py:363`
`parse_project_address`) is a real three-level containment address backed by Postgres
(`container.projects/scopes/resources`, `0013_container.sql`): `projects.address` is a
**GENERATED column** — `'project://' || project_key` (`0013_container.sql:~50`) — so the address
cannot be hand-placed or drift from its key; ancestry (project ⊃ scope ⊃ resource) is the address
structure itself, resolved by exact-match-by-level, never guessed
(`runtime/cognition.py:1422-1479`, comment: "scope-vs-resource ambiguity in the raw syntax never
guesses"). This is the brainwave's §1/§3 claim (containment = ancestry in the address) already
poured in concrete for one axis of the Company.

**Every relation_type on record** — the small, clean registry the anchor's §3 gestures at:
`relation_types/` (`RelationTypeRegistry`, `runtime/relation_types.py`), file-discovered, schema
`{id, directed, inverse, near, far, label, desc}`. The live set (6 files):
- `principle_beneath` — directed, near=principles (A expresses the principle beneath B)
- `fragment_of` — directed, inverse=`has_fragment`, near=topics (part→whole)
- `contradicts` — directed, near=far=principles (a tension, render-not-judge)
- `sibling` — **symmetric**, near=topics (A↔B)
- `depends_on` — directed, inverse=`unlocks` (agent-authored via `create_relation_type`, #58)
- `precedes` — directed, inverse=`follows` (agent-authored; "SEQUENCE axis... logical order, not
  wall-clock")

This registry's OWN header says its point is corpus-relation labeling for `find_relations`
(`runtime/relation_types.py:1-9`, `relation_types/AGENTS.md:14-21`) — the L3/P1 "Cognition
Engine" cross-space inversion-finder (`find_relations(item, near, far) = query_index(near) ∩
¬query_index(far)`).

**A second, much larger, independently-evolved edge vocabulary sits right beside it and is NOT
the same registry: `edge_kinds/`.** 115 files (`runtime/edge_kinds.py`, "④ THE CONTAINER · L4 ·
the ONE edge-kind grammar", `runtime/edge_kinds.py:1`). Row schema is a strict SUPERSET of
`RELATION_TYPE`: `{id, directed, inverse, face, endpoints, behavior, label, description, near,
far, needs_review}` where `face ∈ {containment, knowledge, lineage}` (`runtime/edge_kinds.py:31`).
Counted by face: **containment=11** (contains, part_of, belongs_to, attached_to, instance_of,
in_thread, in_channel, operates_in, attachment, exchange-contains, maps_instance_of),
**lineage=27** (created, produced, launched-by, derived-from, branched_from, restarted_from,
follows, exchange-precedes, supersedes, promoted_from, discovered, informed_by, authored_by,
sourced_from, generated-by, commented_on, responded_in, creates_in, deploys, decides, launches,
…), **knowledge=77** (the semantic bulk: calls, uses, references, implements, extends,
composes_with, resolves, defines, triggers, feeds, dispatches_to, governed-by, …); 9 declared
symmetric (parallels, parallel_to, collaborates_with, same_law, coordinates, syncs_with,
relates-to, composes_with, on-axis).

`edge_kinds/AGENTS.md:15` states explicitly WHY it's a separate registry from `relation_types.py`
verbatim ("the EDGE_KIND row is a SUPERSET of RELATION_TYPE... reuses the SAME file-discovery
PATTERN in a SEPARATE dir... **Unify into one mechanism when a consumer traverses one unified
relation graph**") — the unification is already named as future work, by the module's own author,
independent of this brainwave.

## §B · Joins to the ONE-MATH (grounded, not asserted)

**1. The brainwave's §3 "spacetime is derivable, never stored" is not a new idea here — it is
already a codified, ENFORCED law for the containment face, predating this brainwave.**
`edge_kinds/AGENTS.md:20-21` (Observed, verbatim): *"Containment is derived, never stored — a
`contains`/`belongs_to`/`part_of` edge (face=containment) is derived from the address hierarchy;
the cloud's 319 stored `belongs_to` rows were DROPPED on landing (excluded-with-reason)."* And:
*"Reverses are declared, composed at read, never stored (law 4)."* This is independent,
pre-existing confirmation of the brainwave's derived/declared split — the brainwave GENERALIZES a
law the container lane already discovered and enforced for one face. The 11 containment-face
`edge_kinds` rows are candidates to become PURELY computed (no file, no DB row) once every
container-graph member (not just `project://`) carries ancestry in its own address — right now
`contains`/`part_of`/`belongs_to`/`attached_to`/`instance_of` are declared files with a DB
existence (`ledger.edge_kind`) precisely because most of the graph's nodes (`cvi.type_instance_edges`
targets, e.g. `code://` symbols) do NOT yet carry that ancestry natively — the derivation exists
for `project://` but not (yet) for the code-symbol graph these particular rows serve. That is the
concrete gap the brainwave's math would close.

**2. The `lineage` face is NOT cleanly "derivable from address math" — don't over-claim it.**
Reading actual rows: `follows`/`exchange-precedes` ARE sequence (order-in-a-walk — exactly the
brainwave's §3 "before/after"), but most of the 27 (`created`, `produced`, `generated-by`,
`authored_by`, `sourced_from`, `discovered`, `informed_by`, `launched-by`, `derived-from`) are
PROVENANCE facts (who/what made this), not position-in-a-sequence — they carry information no
address ancestry encodes. The brainwave's §3 two-space split (spacetime vs semantic) needs a
THIRD bucket the anchor doesn't name: provenance/lineage is neither pure address-derivable
spacetime NOR a "meaning-space field" like `calls`/`implements` — it's authored fact that happens
to correlate with time. Recommend the brainwave's §3 be corrected before it's built against:
**derived (containment + pure sequence) / authored-provenance (lineage-as-fact) / semantic
(knowledge)** — three, not two.

**3. `follows`/`precedes` is a live, EXACT naming collision across the two registries, and it is
NOT resolved in either direction.** `relation_types/precedes.py:9` declares its own inverse as the
STRING `"follows"` — but no `relation_types/follows.py` file exists (a dangling, unregistered
inverse reference — `RelationTypeRegistry` never validates that a declared `inverse` name is
itself a registered id, Observed by reading `runtime/relation_types.py` in full: `_build_relation_type`
checks `inverse` is present but never checks it resolves). Meanwhile `edge_kinds/follows.py`
DOES exist as a real, DB-assembled row (face=lineage, inverse=`preceded_by`) meaning something
adjacent but scoped differently ("step N follows step N-1... `ledger.path_step`"). Two vocabularies,
same word, same rough direction, no join, no test that would catch a semantic drift between them.
This is exactly the fragmentation the brainwave's "one math" would dissolve if order is DERIVED
(§3) rather than named twice in two files in two directories.

**4. `mind://` (`runtime/minds.py`) is the ALREADY-BUILT precedent for the brainwave's §8
"any group, any selection, one operation."** A `minds/<id>.py` with `kind="composition"` declares
`members: [<mind-id>...]` + typed `order: [{from, to, kind}]` edges between them
(`runtime/minds.py:13-14`), and the WHOLE composition resolves through the ONE resolver as
`mind://<id>` (`runtime/cognition.py:1331-1345`), traversable and operable as a single thing. This
is precisely "a registered identity for a selection, with lineage IN the address, giving cascade
certainty" (anchor §8) — except it is scoped ONLY to thinking-units (roles/models/compositions
thereof), not to arbitrary content. **No general `collection://`/`group://`/`selection://` scheme
exists** (confirmed: absent from `SCHEMES`, no such grep hit anywhere in `contracts/address.py`).
The brainwave's groups-as-identities law is a GENERALIZATION of `mind://`'s composition kind, not
a new mechanism — build candidate: lift `kind="composition"` out of `minds/` into a scheme-neutral
"any addresses, ordered/typed member edges, one address" primitive, and `mind://` becomes its
first (thinking-axis) instance rather than the only one.

**5. `project://`'s address = identity (§7) is the strongest existing proof-of-concept for
"identity = addressability."** `container.projects.address` is DB-GENERATED from the key
(`0013_container.sql`) — there is no way for a project to exist without an address, and no way
for its address to diverge from its key. This is the frame law stated in SQL: no row without a
generated address, no address without a row.

## §C · Disconnected / half-built

**`relation_types/` has ZERO production consumers — verified by reading, not inferred.**
`Suite.find_relations` (`runtime/suite.py:11735-11795`, read in full) is the function
`relation_types/AGENTS.md:65` names as the registry's consumer ("Read by Group L's `find_relations`
— a SEPARATE coordinated wiring pass"). Its actual body does pure near∩¬far vector set-difference
over `store/vector_index.py` — it returns raw item ids + scores and **never imports or references
`RelationTypeRegistry`, `relation_types`, or any of the 6 files** at all. The registry is fully
built, tested (`tests/relation_types_acceptance.py`), reflected in its own AGENTS.md — and totally
inert. The brainwave's §3 ("stored, declared vocabulary remains only for SEMANTIC relations") is
being designed against a registry that nothing currently reads.

**`glyph_meaning` embedding space uses an address scheme that isn't registered anywhere on the
spine — verified, not inferred.** `ops/build_embeddings.py:51-59` builds vectors for entries whose
`address` field is literally `glyph://symbol/<id>` and `glyph://field/<facet>/<val>`
(`design/claude-ds/glyph-corpus.json` — confirmed real data, e.g. line 10:
`"address": "glyph://symbol/person"`, hundreds of entries). `glyph` is **absent** from
`contracts/address.py`'s `SCHEMES` tuple, and `resolve_address` has no dispatch branch for it (I
read the full dispatcher; the branches are run/cas/blob/image/skill/context/guide/session/cap/
board/clone/mind/vi-vision/decision/extraction/project — no glyph). So `glyph://` addresses are
real, populated, embedded, and queried by `glyph_compose`'s candidate list — but **not
addressable through the one resolver**: `inspect_address`, `traverse`, and any generic
address-space tool are blind to the entire glyph symbol/meaning corpus. This is precisely the kind
of gap rule 8 (author from the registry) and the anchor's §7 (identity = has-an-address) would
flag as unfinished — a real content space that hasn't joined the ONE address space yet, sitting
right next to 22 schemes that have.

**The glyph_* roles are Company's half of the NL→glyphgraph engine, and they are reachable only
GENERICALLY, never load-bearing-tested.** Four roles exist (`roles/glyph_extract.py`,
`glyph_compose.py`, `glyph_assist.py`, `glyph_symbol_candidates.py`), each declared via the
authoring surface (`create_role`, #58) with a real Pydantic `output_schema` — correctly built
per the roles convention. They are invocable via the generic `/api/cognition/run_role` bridge
route (`runtime/bridge.py:85`) — there is no glyph-specific call site anywhere in the Company repo
(confirmed: zero grep hits outside their own files), and **zero test files reference any of the
four** (confirmed: empty grep over `tests/`). Nothing is broken — generic dispatch is the
intended architecture — but there is no acceptance proof this half of the engine actually works
end-to-end from the Company side, and no wiring exists (nor should it, per extraction-vs-judgment)
between `glyph_extract`'s freeform `phrase`/`mood` output and EITHER edge vocabulary
(`relation_types`/`edge_kinds`) — that composition step doesn't exist as code anywhere yet.

**`glyph_assist`'s `add_edge.kind` is a THIRD, ungoverned edge vocabulary path.**
`roles/glyph_assist.py:16` types `kind` as a bare `str` "from vocab.edge_kinds" — `vocab` is
supplied by the CALLER (browser/design side) at request time, not validated against either
Company registry (`relation_types` or `edge_kinds`). This role can emit ANY string as an edge kind
with zero fail-loud gate on the Company side — the opposite of rule 8 (author from the registry;
never invent) and exactly the kind of drift the EDGE LAW course-correction (memory point 3) was
written to stop ("cv-edges.js as a registry separate from the meaning home = drift"). The
Company-side role itself doesn't invent the drift, but it also doesn't PREVENT it — it passes
through whatever the caller's vocab contains.

## §D · Tim-law candidates (evidence-grounded, not invented)

1. **"Containment is derived, never stored" already IS a Company law** (`edge_kinds/AGENTS.md:21`)
   — the brainwave's §3 should be framed as GENERALIZING this existing law across every graph, not
   introducing it. Recommend the brainwave text cite this as prior art.
2. **Provenance/lineage is a third bucket, not folded into "derived."** Don't let the brainwave's
   two-space split (derived spacetime / authored semantics) silently absorb the 27 `lineage`-face
   edges — most are authored facts, not computable order. (§B.2 above.)
3. **Generalize `mind://`'s `kind="composition"` into a scheme-neutral group/selection primitive**
   before building a NEW groups-as-identities mechanism for glyphgraph — the ordered-typed-member
   pattern already exists, proven, resolver-integrated, and just needs its `role/model` binding
   assumption lifted. (§B.4.)
4. **A declared `inverse` should be validated against the registry it names**, not accepted as a
   free string — `relation_types/precedes.py`'s dangling `"follows"` inverse is a live example of
   exactly the un-caught drift the whole "no-hardcoding, registry-is-truth" law exists to prevent
   (fail loud on registration, not just at use).
5. **One relation/edge home, decided by SCOPE not by rewrite** — `edge_kinds/AGENTS.md` already
   names the unification target; the brainwave's arrival is the trigger, not a reason to invent a
   fourth vocabulary (glyphgraph's client-side `vocab.edge_kinds`) alongside the two that already
   need merging.

## §E · Scope additions (resolved into the mission, not flagged-and-parked)

- **Register `glyph` as a scheme** in `contracts/address.py` SCHEMES + add a `resolve_address`
  dispatch branch (mirrors `board://`/`vi-vision://`: lazy-import a small resolver reading
  `design/claude-ds/glyph-corpus.json` or its DB projection, fail-loud on unknown id) — a small,
  additive, non-breaking join that brings the entire glyph symbol/meaning corpus onto the one
  address space. This is a concrete, scoped, buildable item, not a someday.
- **Wire `find_relations` to actually label its output from `relation_types.as_records()`** — the
  registry has been sitting fully built and totally inert; this is the "next pass" its own
  AGENTS.md already named, and the brainwave's §3 needs a live consumer to build against, not a
  dormant one.
- **Add an inverse-resolves-to-a-registered-id check** to both `RelationTypeRegistry` and
  `edge_kinds.py`'s `_validate_row`/`_build_relation_type` (fail loud on a dangling inverse at
  discovery time, not silently at read time via `compose_inverse`/`forward_of` returning None).

**Verification note:** every file:line above was Read directly (not searched-and-assumed); the
`find_relations` zero-consumer claim was verified by reading the complete method body, not by
absence-of-grep-hit alone. The `glyph://` disconnection was verified against real corpus data
(`design/claude-ds/glyph-corpus.json`), not just the SCHEMES tuple's absence.
