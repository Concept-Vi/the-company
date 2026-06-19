# FACET RETURN — THE INVARIANT LAW (what every axis obeys at every scale)

*Widening+deepening pass for the orchestrator. READ-ONLY sources; this is a return artefact, not an edit to the canon. Provisional — convergence between fragments is the signal, never any single fragment. Tim judges.*

---

## (a) THE DEEPENING — pushing the law further, new substrate content, filling the continuous-name gap

### A1. The cascade is not "addressing up + resolving down" — it is ONE morphism read in two directions, and that is WHY decontextualisation is structurally impossible.

The formal body (BRR §9.5–§9.7) is sharper than the map records. The address is not a tuple-with-a-rule-against-truncation; it is literally a **morphism in the containment category**:

- §9.5 / `fully-qualified-address-def`: `addr(c)=(p₀…pₙ)` where each `pᵢ` is the position of `Aᵢ₊₁` inside `Aᵢ`. (verbatim formal)
- §9.5 / `claim-5-5-A`: each `pᵢ` "articulates with meaning *contextual on (p₀…pᵢ₋₁)*" — a coordinate has no meaning except inside the frame its prefix establishes.
- §9.5 / `claim-5-5-B` ("decontextualisation impossibility"): "no valid address articulates with fewer than n+1 components. **The path IS the address; truncation produces ambiguity or invalidity.**"
- §9.5 / `claim-5-5-C` ("address-as-morphism"): `addr(c)` is "the unique-up-to-equivalence morphism Root → c" in the containment category (objects = bounded units, morphisms = composed embeddings).
- §9.7 / `resolve-def`: `resolve: (Frame, Address) → Target`; addressing and resolution "articulate as inverse operations on a well-formed containment graph."

**The deepening (new):** the "one way" Tim names is not a sequencing convention — it is a *categorical fact*. Addressing produces the morphism Root→c; resolution **traverses** it; they are inverse arrows, not two procedures. Decontextualisation is impossible **because a morphism cannot exist without its domain** — `pᵢ` is a position *in* `Aᵢ`, and `Aᵢ` is only reachable *through* `(p₀…pᵢ₋₁)`. Strip the prefix and `pᵢ` doesn't become a "shorter address," it becomes **not-an-arrow** (no domain → no morphism). This is the precise mechanism behind Tim's "every address requires its ancestors": ancestry is not metadata attached to the address, it is the *composability condition* of the arrow. An orphaned coordinate is not under-specified; it is **type-error** (its source object is absent).

**Two truncation branches (not one — §9.5 says "ambiguity OR invalidity"):** (i) an *isolated coordinate* with NO prefix → no domain-object → genuinely **not-an-arrow / type-error / invalid**; (ii) a *short-but-prefixed* address `(p₀…pₖ)`, k<n → a **valid morphism to an intermediate frame Aₖ**, ambiguous about which descendant of Aₖ is meant → **contextually completable** ("the third one", with type implied by the frame). Both are "decontextualised" in Tim's sense, but only (i) is invalid; (ii) is the resolver's everyday partial-resolution. (This reconciles A1 with S-cascade1 below.)

**Consequence for the instrument:** the address-spine ("every element stamped, one sink", map §5) is not a logging convenience — it is what makes any element *resolvable at all*. A node with NO ancestral path (branch i) is not a node with a missing field; it is **not a legal position in the space**. This is the law-level justification for fail-loud on un-rooted units (the un-prefixed kind).

### A2. Type-registry-per-scale = authority-is-fractal, and the formal body states it three times in three vocabularies (strong convergence).

- BRR §11.3 / `claim-7-3-A`: "Each frame in a containment hierarchy articulates with its own type vocabulary, generally distinct from those above and below… the address-and-resolution operations work the same at every level; what changes is what types are available to be addressed."
- projected-into-obsidian §14.3 / `p8-s8-3-claim` (the cleanest statement): "Within any unity, the schema is authoritative for its contents… A vault's schema specifies what is valid at the vault scale; that authority does not extend to a parent scale… or a finer scale (each folder has its own schema). **The authority structure is fractal — every unity is authoritative for its contents and is itself a content of its parent unity, governed by the parent's schema.**"
- type-registry-working-notes §1: "**A type can only be referred to from within a frame if it has been registered there, because reference requires address, and address requires the type to occupy a position in some bounded unit's contents.**"

**The deepening (new join):** put §1 of the registry notes next to BRR §9.5 and a sharp identity falls out — **registration = the operational act of bringing a type into the addressable lattice; reference = building the morphism to it.** Authority-is-fractal is therefore *the same law as the cascade, applied to types instead of to content*: a type at scale k is reachable only by the prefix `(p₀…pₖ₋₁)` of registered ancestor-frames. "Visibility = legality" (Tim) is then not a separate rule — it is `claim-5-5-B` (truncation→invalidity) restated in the type face: **an unregistered type has no domain-object to be an arrow from, so it cannot be referenced; it is invisible because it is unaddressable, and unaddressable because un-rooted.** The closed-world assumption (unregistered = doesn't exist) is *derived*, not assumed.

### A3. Operationally-fractal, not geometrically-fractal — and the body draws the distinction Tim's intuition needs.

BRR §12.1 / `claim-8-1-A` makes a distinction the map should carry explicitly: substrate-scale is **recursive depth in the containment graph** (step-out = up, step-in = down; *no privileged level, the start-point is "observational not structural"*) and is **distinct from magnitude-scale** (a range of sizes). type-registry-working-notes §9 names the matching geometric fact: the nesting is "a literal geometric fractal — though **not self-similar in the Mandelbrot sense (n varies with content)**, it is *form-similar*: every node is a polygon, every recursion is 'a vertex becomes a polygon,' every polygon has the (S,A,B,I,C) schema-form."

**The deepening (vocabulary for Tim):** the invariant that recurs is the **form/operation**, never the content. This is the load-bearing meaning of "no privileged level": you cannot tell which scale you are at by looking at the *operations available* (they are identical everywhere — address, resolve, bound, type, nest); you can only tell by looking at the *content/vocabulary* (which differs per frame). This is exactly Tim's "the thing that changes at each scale isn't the content but the rules" (SEED-SCALE §8) read from the law side: **operations invariant ⊗ schema-vocabulary variable.** "Form-similar not self-similar" is the precise correction to any reading of the fractal as visual self-repetition.

### A4. ★ FILLING THE CONTINUOUS-NAME GAP — the genuinely-new half, and exactly where the formal body stops short.

What the body HAS (verified):
- **Folder** (proj-obsidian §22.2): "each folder is a unity for its contained notes **with its own schema** (what notes belong, what naming conventions apply, what type-vocabulary the contents use). Folder paths are composed coordinate paths." → folder = nested frame, characterised by its **positive schema**.
- **File** (proj-obsidian §22.3, §15.3): ".md files… **file types contain the schema for valid content inside the file**" → file = bounded unit holding **content of its type**.
- The **discrete extension / type-slot** is fully present (file-type = the schema discriminator).
- The **slot/socket** Vieta pair (`n₋+n₊=1`, `n₋·n₊=1/τ`) is present in composition (map §3) — the discrete fill-vs-frame pair.

What the body does NOT have (confirmed — structural search for "filename"/"name"/"continuous-name" returns nothing in the canon; semantic search down, structural exhaustive): **the folder defined NEGATIVELY, by its distinct ABSENCE of an extension, and the continuous-NAME as a slot in its own right.** The body always characterises a folder by what it *contains* (its schema), never by the *mark that distinguishes it* (no extension). It never pairs "folder" with the absence-as-signal law.

**Tim's 06-19 transmission supplies exactly this missing half and welds two laws that the canon kept apart:**
> "a folder is the continuous slot defined by its distinct ABSENCE of an extension; a file holds content of its type, a folder the space where files do not."

Decompressed against the substrate, this is a precise dual:

| | the NAME (continuous slot) | the EXTENSION (discrete slot) |
|---|---|---|
| domain | any legal string — **open / free / not from a registered vocabulary** | drawn from the **registered type-vocabulary** of the frame (closed) |
| file | the file's name (continuous) | `.md`, `.png` — its **type** (six required, §22) |
| folder | the folder's name (continuous) | **distinct-absence** — extension present-as-rule, magnitude-zero |
| reads as | DENOTATION (what it is called) | SORT (what kind it is) |
| in the seed-geometry | the **circle** half — felt, continuous, lands on grid only by coincidence | the **square** half — discrete, indexable, addressable |

So a folder is **not** "a file with a blank extension" and **not** merely "a nested frame with a schema." It is the unit whose *type-slot is filled by distinct-absence* — the extension-rule is present (every unit has one), expressing zero. That is **six-states §13 (distinct absence: "structurally present at that point, expressing zero" vs absence-simpliciter) applied to the file/folder type-slot.** The folder is "the space where files do not" = negative space at the type-axis = `claim p7-s7-1` ("structurally present, quantitatively absent") instantiated on the extension dimension. **This connection — folder = distinct-absence on the type-slot — is nowhere in the formal body; it is Tim's net-new weld of the unit/edge duality to the absence law.**

### A5. ★ ABSENCE-AS-SIGNAL — how absence is actually computed (PUSH 2 answered from the substrate).

The mechanism is fully formal in six-states-of-unity, and it answers "how is the unregistered made legible by what doesn't show":

**The four combinations (§13.3 / `p7-s7-3-claim`) — the absence algebra.** Structural-presence (address declared, rule present) × quantitative-magnitude (content at address) are **independent attributes**, giving four conditions:
1. **present × present** = filled (occupied slot).
2. **present × absent** = **distinct absence / proto-state** — *address established, content empty* (the folder; the open seam; the skeleton subheading).
3. **absent × present** = content without articulated address ("inverse-proto").
4. **absent × absent** = **absence simpliciter** — no rule, no content (invisible by construction).

**Only condition 2 is computable/legible.** absence-simpliciter (4) is structurally invisible — closed-world: no rule means nothing declares it should be there. The system can *only* see absence where a rule is present declaring a slot that resolution finds empty. **Absence = (declared slot) ⊖ (occupancy).** This is `registry minus presence`, evaluated against the registry, never against the void.

**The 5-step information-carrying mechanism (§15.2 / `p8-s8-2-claim`) — "substrate-conformant, no additional machinery":**
1. surrounding positive structure has articulated content (headings, type-vocabulary, cross-refs);
2. that structure **bounds** the empty position (gives it an address);
3. the bounding **types** the empty position (what kind of content the surrounding frame implies there);
4. a reader/articulator **reads the bounding**;
5. they **produce content that fits** — *without explicit instruction.*

→ "the negative space's shape is determined by the surrounding positive structure" (§12.2, Tim verbatim: *"the empty/negative space is a marker for undefined boundaries by indicating where the boundaries are not… it doesn't need to be explicitly stated or described except where it is part of it"*). The unregistered is made legible by the SHAPE the registered leaves — figure-ground: you read the hole by its rim.

**Distinct-absence is itself scale-invariant (§13.2):** the *same* law operates at parametric-rule scale (rule expressing zero), sentence scale (parenthetical seam), section scale (empty subheading / skeleton), artifact scale (skeleton-doc), corpus scale (open seams collectively), identity scale (proto-state). One law, every rung — it obeys the invariant.

**Filtering / clustering fall out (the map's "same invariant"):** filtering = take the registered positions, apply a predicate; the *empties among the matched* are visible distinct-absences (declared-and-empty). Clustering's gaps = the deep-holes / maximal-divergence points (CONVERGENCE-OBJECT: odd multiples of π/4, √2/2) where nothing settles — a *persistent* distinct-absence between two clusters is the thermal signature of a **missing registered position** (CONVERGENCE-OBJECT derivation-4: "types born at deep holes"; = gap-pressure). So: filtering surfaces *declared* absences; clustering surfaces *undeclared-but-pressured* absences (candidates for promotion). The gate's act = promoting absence-simpliciter→distinct-absence by **declaring a slot** — the same "rotate onto the axis" move as recognition (THE-SEED §3).

### A6. ★ THE KEYSTONE — "everything is a variable" is the LAW being agnostic to its content.

THE-SEED §8 (Tim verbatim): "There is no definition. The axes are variables. So are the divisions… The relative centre can change — it is the object of attention… It's an instrument." The separation: **invariant = the RELATIONSHIP** (the duality about a shared centre; the resonance law `2π/n=(1/n)^k` holding at every n); **variable = everything that fills it** (axes, divisions, every integer slot, the centre).

**The deepening (this is the unifying through-line of every section above):** every law I verified is *a relationship that survives total content-substitution*:
- the cascade is a relationship (prefix-composability) over **variable** coordinates;
- authority-is-fractal is a relationship (schema-governs-contents) over **variable** vocabularies;
- form-similar fractality is operation-invariance over **variable** schemas;
- the name⊥extension duality is a relationship (free-slot ⊥ registered-slot) over **variable** name-strings and **variable** type-sets;
- absence-as-signal is a relationship (declared ⊖ occupied) over **variable** occupancy.

"Everything is a variable" is therefore not one law among the others — it is the **meta-statement of why they are LAWS**: each is the *invariant relationship* left when you let the content range over everything. That is precisely what makes the instrument *agnostic* (any domain = an axis-assignment + content) and what makes hardcoding *illegal* (freezing a variable replaces a law with one of its instances — the recurring "first-binding" error, map A1).

---

## (b) CONVENTIONAL OFFERINGS (labelled — offerings, not identities; "this resembles X — does it capture your Y?")

- **Ultrametric / p-adic numbers** — for the cascade. A prefix-closed address tree induces an *ultrametric*: distance(x,y) = depth-of-deepest-common-ancestor; it satisfies the strong triangle inequality (every triangle isosceles). The substrate already says "triangulation through shared ancestors" (BRR §9.6) — ultrametric is the clean name for *why* common-ancestry is the only cross-frame bridge. p-adic numbers are the number system built on exactly this "closeness = shared prefix" idea. **Not in the formal body; strong fit; offer as "does p-adic/ultrametric capture the 'closeness is shared-ancestry' you mean?"**
- **Sheaves & locality** — for type-registry-per-scale (§11.3). A *sheaf* assigns local data to local regions with consistency on overlaps and gluing into global data — the formal echo of "each frame its own vocabulary, glued by shared ancestors." Offer with the deviation: sheaves presuppose a fixed base topology; the substrate's base (the containment tree) is itself variable.
- **Closed-world assumption** (logic/databases: not-provable = false) — for visibility=legality and absence-simpliciter's invisibility. Direct. The substrate's "if information is invalid it doesn't exist" (SEED-SCALE §10) IS the CWA.
- **Negative space / figure-ground** (Gestalt) — for absence-as-signal. The body uses "negative space" already; the offering names the perceptual law: the ground is shaped by the figure; you read the hole by its rim.
- **Name-vs-type = denotation vs sort** (logic/PLT) — for the continuous-name ⊥ discrete-extension duality. A name *denotes* (picks out, free); a sort/type *classifies* (constrains, from a registered set). The folder/file split is this distinction made into storage.
- **Tries / prefix trees** — for the address structure: a trie keys by path-prefix, exactly the cascade's `(p₀…pₙ)`. Cheap, exact, familiar offering for the engineer-facing layer.
- **Filesystems / namespaces / paths; type systems & registries** — the working substrate the projection literally lands on (proj-obsidian §22). Already inhabited; name them so the build team sees the law IS the filesystem, not a metaphor over it.
- **Subobject classifier / type-of-types** (topos / constructive type theory) — for "the schema-form is the universal common ancestor of every registry" (registry-notes §2). The notes already flag it *with* the right deviation: the classifier lives in a containing category; the substrate rejects the containing level (no privileged scale). Offer with that caveat intact.
- **Universes U₀⊂U₁⊂…** (type theory) — for type-of-type recursion (BRR §10.3): the standard ladder for "types are themselves typed without privileged level." The body explicitly accommodates it.
- **Autopoiesis / dissipative structures** (Maturana-Varela / Prigogine) — peripheral but adjacent: registry-notes §11 already cites these for the *viability/throughput* condition, the law-level reason a bounded unit persists. Flag only if the orchestrator wants the persistence facet.

---

## (c) NEW SEAMS / questions surfaced by this pass

- **S-name1 — does name⊥extension generalise to EVERY axis (PUSH 1)?** Evidence says **yes, and it clears the hardest case (the privileged TIME axis), with a held fork.** Every unit carries a **registered/discrete face** (type, address, extension, square/structural) ⊥ a **free/continuous face** (name, value, embedding, circle/semantic) — square⊥circle (SEED), structural⊥semantic (CONVERGENCE-OBJECT §I), location(discrete)⊥state(continuous) (map §3), even Tim's own type-registry §3 open-seam asks "whether more than two axes operate at every type… the structural-semantic axis is one candidate further axis." **The discriminating test — TIME, the one axis the corpus privileges (involuntary, the "1"):** it too splits into a **discrete-registered slot** (the prime-factored scale-rung — which registry: second/minute/hour/day/week, 60=2²·3·5, 24=2³·3, 7=7; the divisor-lattice prime-coordinate, SEED-SCALE §9) ⊥ a **continuous-free slot** (the instant *within* the rung; the now-relative radius, continuous). So even the exceptional axis carries the duality — the generalization is *robust*, not merely asserted from the easy axes. (Lane caveat: this is "does the duality hold FOR time," NOT "is time the 1 / which are the four roots" — S1–S5 untouched.) **The fork (do NOT collapse):** is the duality *WITHIN each axis* (state = the continuous half of location; every axis = a discrete-name-slot + a continuous-value-slot) — OR *BETWEEN two coordinate systems each axis projects into* (the whole square vs the whole circle)? These may be one thing seen at two scales (a per-axis duality that, summed over axes, IS the square/circle split). Surface both; this is Tim's to adjudicate. **Lane discipline:** the duality holds *regardless* of how the four root axes are named — I did NOT touch S1–S5 (out of lane).
- **S-name2 — the free slot is open-world, the registered slot is closed-world; is "continuous" the SAME predicate as "open/unregistered-vocabulary"?** The name is "continuous" (any legal string) precisely because it is *not* drawn from a registered set; the extension is "discrete" because it *is*. If that identification holds, **continuous ⟺ open-world ⟺ free-slot** and **discrete ⟺ closed-world ⟺ registered-slot** — which would mean PUSH 1 and PUSH 2 are *one* law (the duality's continuous half IS the absence-engine's input). Candidate, not settled.
- **S-absence1 — the three un-articulated combinations.** six-states §13.3 leaves an OPEN SEAM: only the proto-state (present×absent) is articulated; **absent×present ("inverse-proto": content with no address)** and the full four-way structure are unworked. The folder is present×absent on the type-slot — what storage-object is *absent×present*? Candidate: an embedding/orphan with meaning but no ratified path (THE-SEED §10 "circle-without-square"). Worth a dedicated pass.
- **S-absence2 — is the gate's "declare a slot" the inverse of resolution?** Promoting absence-simpliciter→distinct-absence = adding a frame+position = *extending the containment morphism*. If addressing/resolution are the inverse pair (§9.7), the gate is a *third* operation that grows the category itself (new objects/arrows), not a traversal within it. The law spine may need a "lattice-growth" operation beside address/resolve. New.
- **S-cascade1 — partial/broken/contextual addresses.** BRR §9.7 `territory-5-7` explicitly DEFERS truncated/malformed/ellipsis-completable addresses ("the third one" with type implied by context) to "future address-and-resolution working notes" that do not yet exist. This is the formal home for the instrument's real-world resolver behaviour (the resolve(centre, …) call, SEED-SCALE §2) — currently an unbuilt formal seam.

---

## (d) WHAT I READ (sources, all READ-ONLY)

- `build-prep/universal-projection/UNIFICATION-MAP.md` (full; esp. §2 the invariant law) — the frame.
- `build-prep/brain/SEED-SCALE-PRIMES-SEPARATOR.md` (full + Appendix A verbatim) — scale-as-rules §8, primes §9, polygon=viewpoint §11, legality/CWA §10.
- `build-prep/brain/THE-SEED-geometric-substrate.md` (full) — square/circle duality, "everything is a variable" §8, forbidden/discrete-vs-continuous §10–11.
- `build-prep/brain/CONVERGENCE-OBJECT.md` (full) — convergence law, deep-holes, the four laws.
- `relative-difference` vault (substrate-mcp, structural + get_by_address/get_chunks; semantic confirmed DOWN, fell back to structural):
  - `…/universal-mechanics-bounded-recursive-relativity.md` — §6.1 `law-articulation` (the law spine, verbatim), §6.2 name-parsed, §9.5 `fully-qualified-address-def`+`claim-5-5-A/B/C` (cascade, decontextualisation-impossibility, address-as-morphism), §9.7 `resolve-def`+`territory-5-7` (resolution = inverse; partial-address seam), §10.3 type-of-type/universes, §11.3 `claim-7-3-A` (type-vocabulary-per-depth), §12.1 `claim-8-1-A` (scale = recursive depth, no privileged level).
  - `…/six-states-of-unity.md` — §12.2 negative-space-shape (Tim verbatim), §13.1–13.3 distinct-absence + the four combinations (the absence algebra), §15.1–15.3 the 5-step information-carrying mechanism.
  - `…/universal-mechanics-projected-into-obsidian.md` — §14.3 `p8-s8-3` schema-authority-is-fractal, §15.3 file-types-as-schema, §22.1–22.8 storage primitives (vault/folder/file/attachment/canvas/bases) — the literal files-and-folders projection.
  - `…/extensions/session-1/type-registry-working-notes.md` (full body) — §1 registration/reference-requires-address, §2 schema-form as universal ancestor, §3 dual-axis naming (containment ⊥ specialisation) + open-seam on more-axes-per-type, §9 form-similar fractal, §13 schema-IS-the-type method.
- Structural confirmation that NO existing canon doc articulates "continuous filename / name-as-slot / folder=absence-of-extension" (searches for "filename","name" empty of relevant hits) — the continuous-name gap is real.
