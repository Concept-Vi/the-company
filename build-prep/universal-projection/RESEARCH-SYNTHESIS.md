# Universal Projection — Research Synthesis

**Originated by Tim Geldard; all derived work attributed to him.** The evidence base for the
instrument→ability buildout, produced by a 7-agent research wave (2026-06-13, ~770k tokens) reading
the stored design (build-prep/brain/*) against the company's actual code, registries, embedding
substrate, prior loop docs, and design system. This is ground truth from the codebase — the
Completion-Criteria and Implementation-Guide are built on it; corrections flow synthesis → guide →
criteria, never the reverse.

---

## ROUND 1 — THE STEP-UP OPPORTUNITIES (where the projection unifies/unlocks existing machinery)

Tim's instinct ("a massive step up") is confirmed. The instrument is not a new thing bolted on — it
is the geometric FACE of machinery the company already built under other names.

1. **ONE RESOLVE, MANY FACES — the biggest unification.** Four LIVE, separately-built mechanisms —
   the per-address gatherer (`runtime/suite.py:_resolve_context_at`/`_r2_gather`), the greeting
   assembler, the builder context block (`ui_claude_session.py` context_block), and the boot bundle
   — are the SAME `resolve(centre, spaces, n, k, audience, exhale)` call with the bindings HARDCODED.
   "Free the bindings" collapses four bespoke code paths into one parameterized instrument. The
   projection IS the company's existing variable-and-address resolution, seen geometrically
   (SEED-SCALE §15: "it has always been this").
2. **REMEMBERING = PLANNING = POLLUTION-HUNTING, one instrument.** The time-freed centre makes one
   resolve serve three jobs: centre←past = remembering, centre←future goal = planning ("the distance
   between present and goal IS the plan"), centre←the AI-pole = pollution-hunting. Different SPACES
   born on use, not different views. One scrubber, three abilities.
3. **THE TWO-GRAVITY SEPARATOR AS A CORPUS-WIDE CLEANER (highest near-term value).** The
   steering-vector mechanism reuses the EXISTING `find_relations` two-space template + the on-disk
   instruction-aware embedders to give the company a vector-level Tim-intent-vs-generic-AI
   discriminator — simultaneously powering the foreignness/ai-tics detector. One axis cleans the
   whole corpus AND grades every future generation.
4. **THE TOTAL-PROCESSING PIPELINES POINTED AT THE INSTRUMENT.** P1–P7 are the SAME machine already
   proven by RG10 (940 extractions → 483 verified) + the 1,460 exchange-extract mining. Pointed at
   the projection's points, the questionless-sweep turns the lattice from a viewer into a
   self-processing organ — the residue (P6) IS the geometric forbidden-zone.
5. **VECTORS-AS-COORDINATES UNIFIES THE FORAGER AND THE LATTICE.** The forager's "vectors as
   coordinates" correction = the renderer principle = semantic-radius = "embeddings ARE the circle's
   real job." The forager (inhale/read face) and the lattice (exhale/projection face) become two
   views of ONE resolve over the same store + space substrate. The forager named the weakest existing
   piece (the relations projection); the instrument's structural+semantic work strengthens it.
6. **TYPE-BIRTH = AXIS-BIRTH = LEARNING, a single growth organ** (independently re-derived by two
   unaware rays — triangulation evidence). Wiring the 20/80 water-law onto order-from-edges +
   registries means the system GROWS its own angular geometry under forbidden-zone pressure: learning
   becomes a gate-ratified row insertion in the axes registry, not an agent declaration. The
   instrument is HOW the company learns new dimensions.
7. **TIME AS THE ONE ABSOLUTE ADDRESS.** The privileged/involuntary time axis + the
   address-coincidence law (transcript-address = folder-path = timestamp, born of one act) mean the
   common-memory-across-time vision lands directly on centre=NOW + the scrubber — context resolution
   extends from SPACE to TIME with no new substrate.
8. **PARALLAX/TRIANGULATION GETS A GEOMETRIC HOME.** "A session IS a centre; the difference between
   two centres measures the hidden dimension" = a point under two LENSES = parallax. The lens-switch
   animation literally renders the company's multi-session parallax reasoning.

## ROUND 2 — THE REUSE MAP (capability → exact existing machinery; do not build parallel systems)

1. Variable instrument / resolve-from-binding floor → REUSE `runtime/projection.py:project` +
   `BindingRegistry` (built; pure read; lock x=2π/n). This IS S1.
2. Angular divisions (sectors from data) → REUSE `projection.py:_resolve_sectors` angle_from='kind'
   (one sector per distinct kind) + 'kind-group' (`bindings/grouped.py` globs).
3. Swappable lenses → REUSE `BindingRegistry` + `bindings/{raw,grouped,time-of-day}.py` + AGENTS.md
   (file-discovered, id==stem, fail-loud; a lens = a file).
4. HTTP face → REUSE `runtime/bridge.py` GET `/api/projection` (~line 727) → `SUITE.store.events_since`
   → `project(...)`.
5. **Real-time pub-sub → REUSE `runtime/bridge.py` `/api/stream` (SSE, ~line 985)** over
   `store/fs_store.py:events_since` (line 542) — the SAME append-only tap the projection reads.
   Subscribe instead of poll.
6. Event source + record shape → REUSE `suite.py:events_since` (1849) + `fs_store.py:events_since`
   (542); centre='now' last-touch → `suite.py:now` (1854)/`now_signal` (1886).
7. depth/k slot → REUSE `projection.py` depth = ui:// path-segment count + `contracts/ui_info.py:parse_ui_address`.
8. Structural-proximity (square) metric → REUSE `suite.py:address_tree_distance`.
9. Radius=relevance FORMULA (recency×proximity×semantic) → REUSE THE MATH from `suite.py:_r2_score`
   (3473)/`_r2_score_and_cap` (4055) — the math, NOT the function (that stack resolves TEXT for chat,
   a different path).
10. Vector/space substrate (the circle's data) → REUSE `store/vector_index.py:{build_index,
    query_index,index_staleness}` + `fs_store.py:{space_address,put_vector,get_vector,index_corpus,
    ALL_SPACES}` (persisted, incremental, space-keyed, degrade-loud — NO second vector path).
11. Embed-on-write → REUSE `runtime/cognition.py:embed_corpus_to_spaces` (386) + `suite.py:capture_corpus`
    (10433)/`query_corpus` (10537), driven off `projections/` embeddable() lenses.
12. Load an embedder resident → REUSE `ops/cli/capabilities.py:ensure_resident` (407) +
    `cognition.py:_ensure_embedder_resident` (187) + run_role op=='embed' — the ONE VRAM-gated
    resource manager (`gpu.py`). Mechanism complete; only `company up embed-bge` remains.
13. The two-gravity separator's skeleton → REUSE `suite.py:find_relations` (10555) — near ∩ ¬far over
    two space-keyed vectors; the separator is this ONE STEP short (two instruction-lens spaces).
14. Order-from-edges vocabulary → REUSE `runtime/relation_types.py:RelationTypeRegistry` +
    `relation_types/{precedes,depends_on,...}.py` (the edges EXIST; only the wiring is net-new).
15. Strain carrier → REUSE `runtime/mark_types.py:MarkTypeRegistry` + `fs_store.py:{append_finding,
    append_mark}` (a 'strain'/'forbidden' mark = a disposition over a point; render-not-judge,
    operator-overridable).
16. S5 builder handoff → REUSE the `builder-context` CustomEvent (LatticeView.tsx:~183) — the SAME
    seam the forager + mobile tray use.
17. FORM kit + tokens → REUSE `canvas/app/src/components/kit.tsx` (Surface/Badge/SectionHead/
    LaneHead/EmptyState) + `design/design-system.css` (corpus tokens; source `design/_system/tokens.json`)
    + exemplar `regions/Inbox.tsx`.
18. FORM gate → REUSE `design/_system/check.py` (design-lint; --target --fail-on --include-px) +
    AGENTS.md rule 9.
19. Point-in-time precedent → NOTE `runtime/session_pointintime.py` EXISTS but is TRANSCRIPT-scoped —
    do NOT reuse for the event-store scrubber; the time-freeze is the small `project(now=, filter
    ts<=now)` extension instead.

## ROUND 3 — NET-NEW (genuinely no existing machinery)

1. A COMMITTED acceptance suite for the instrument invariants (r∈[0,1], θ-in-wedge, even re-division
   at every n, lock holds, '*' remainder catches all) — the projection has NO regression test today
   (only ad-hoc curl evidence). **First build item.**
2. The structural square half — i,j grid + m/2 concentric circles from the ui:// hierarchy. Today:
   a per-point depth SCALAR + `rings:4` HARDCODED. `parse_ui_address` is reuse; the grid projection
   is net-new.
3. Semantic-radius resolver branch — `radius_from=='semantic'` reading cosine-from-centre + a
   `bindings/semantic.py` row. Slot + data exist; the wiring does not.
4. Strain / structure↔meaning gap — per-point square-vs-circle disagreement as a field or a mark.
   Zero code today (grep-confirmed). Both position sources exist; the comparison is unbuilt.
5. Relative-centre branch — when centre is an address (not now), radius = relevance-from-that-address.
   project() hardcodes center:'now'.
6. The `?at=` scrubber wiring — parse in bridge + filter ts≤now (project() already accepts now=).
7. **The event→registry-row EDGE — the keystone primitive** letting an event relate to a registry
   row (this op.run → the role that fired it). Explicitly flagged-not-built. Unblocks BOTH
   angle-from-a-registry AND order-from-typed-edges.
8. order-from-typed-edges mode — new order_by ordering sectors by relation_types edges. Depends on #7.
9. An instruction/task PARAMETER threaded through the embed transport (`fabric/transport.py:
   openai_embeddings_transport` → `client.complete_embeddings` → `nodes/embed.py` → build_index).
   The live path passes ONLY raw text. Cross-lane (fabric owner) — coordinate.
10. The two-gravity gap helper (per-unit cosine GAP between two lens-vectors) + steering-vector
    primitive (centroid-A − centroid-B = axis; project unit = signed scalar). REUSE get_vector+cosine;
    the axis/gap math is net-new.
11. A sentence/turn chunker + per-rung space naming + zoom-by-rung query — the multi-scale pyramid.
12. The lattice FORM rebuild — chrome on kit + corpus tokens, token() repointed off the dead
    --accent/--ink-dim, ~37 CSS + 8 tsx literals retired (the angle-hue PRESERVED).
13. The 20/80 pressure-threshold type-birth/death — described, unbuilt.
14. The origins + axes registries (small, net-new).
15. The promotion gesture / gate UI — undesigned.
16. This loop-prep TRIAD (the siblings each have one; the projection only had the one-pager).

## ROUND 4 — CONTRADICTIONS & TRAPS (the agents' flags, filtered through understanding)

**REAL traps (must be honored):**
- **NAME COLLISION — disambiguate everywhere.** `runtime/projection.py` (singular) = THE INSTRUMENT
  + its `bindings/` lenses. `runtime/projections.py` (plural) + `projections/` dir = the K1 corpus
  DESCRIPTION-LENS registry (what/topics/principles/worldview/…). They share only the file-discovered
  registry MECHANISM. **`tests/projections_acceptance.py` tests the LENS registry — so the instrument
  can look "tested" when it is NOT.** (This is why net-new #1, the real acceptance suite, is first.)
- NAME COLLISION 2: `suite.py:_semantic_radius` (9142) is the code-consult feature, NOT the
  projection's radial axis. Do not conflate.
- **FORM HOLD-OUT (real quality debt the lead introduced):** LatticeView.tsx is the ONLY region still
  on the dead GitHub-dark palette. `--accent` (~10 refs) and `--ink-dim` (~9 refs) are defined
  NOWHERE (18 refs, 0 definitions) — they always fall back to hardcoded #d4a017/#8b949e. Internally
  inconsistent: token('--bg') resolves warm (corpus #0c0a08) while token('--accent') never tracks the
  theme. ~37 literals also live in the app.css `.lattice-*` block — design-lint against the .tsx alone
  under-reports; target BOTH files.

**Honest STUBS (not capabilities — the build must not mistake them for done):**
- radius: `projection.py:155` is a no-op ternary (both branches = log1p(age)). Radius is time-only;
  "radius=relevance" is declared, not computed.
- rings: `rings:4` is a hardcoded integer, contradicting the seed's m/2-from-n construction.
- sectors-from-registry: only 'kind'/'kind-group' handled; angle_from=<registry-name> is
  reserved-but-unbuilt (intentional — the data-driven default is the non-negotiable floor).
- order-from-edges: order_by is only count|declared; edges exist but are unwired.
- source: the instrument reads the EVENT store (~5000+ events); the forager reads the curated corpus
  (2067 records) — different universes today (likely intentional: NOW-centred = activity; confirm vs intent).

**APPARENT gaps that are INTENTIONAL design (NOT bugs):**
- Forbidden/divergent points read like errors but ARE THE WORK (gate inbox / drift / axis-growth).
- "Nothing ratified" footers = expand-before-harden discipline, not incompleteness.
- Per-point hue = angle (hsl by θ) is a DELIBERATE non-token colour (colour IS geometry) — the one
  place the literal-free rule does NOT apply; the FORM fix must preserve it.
- The coherence/cognition embedding machinery is OPTIONAL, not a prerequisite — the instrument floor
  is complete and standalone. The forager does NOT subsume the instrument (siblings).

## ROUND 5 — THE MODEL CALLS (Tim's, not to be guessed — a ratification gate, not a build group)

1. **Is the register-of-registries the prime/divisor lattice?** Tim said (A1) he "hasn't got a formal
   equation like the seed" for registry-relations. The lead PROPOSES the divisor lattice (one prime
   per axis, exponent=position). UNMADE — awaiting ratification. The wave could NOT ground it (no
   existing formalism to map onto), so it is genuinely Tim's call.
2. **What anchors the two gravities?** The mechanism is specified; the ANCHOR SETS (which units are
   "unmistakably Tim" vs "unmistakably generic-AI") are unspecified anywhere. Until Tim sets the
   poles, the separator is not computable. Gates the highest-near-term-value ability.
3. **What are the two axes?** Time is one candidate; the other is OPEN (self↔world vs
   utterance↔artifact, both unratified). "Choosing the axes is choosing the spine."
4. **k (the dimension)** — what it controls and how it's set is underspecified; global vs per-region
   (variable-dimension memory) is an open front.
5. **The spectrum** — Tim set it aside ("between types, from the self-division"); relational framing
   stands but unformalized — his to direct.
6. **Prioritization at scale + coherence-gaming** — what orders 10,000 findings; can coherence be
   gamed by confident nonsense? Candidate rules (gap-pressure / gradient-proximity, never a confidence
   score) but unresolved — weigh in before the pipelines run at scale.
7. **The 20/80 dial, semantic-residual arrangement, the promotion gesture** — stub-able, but not
   finalized without Tim.
