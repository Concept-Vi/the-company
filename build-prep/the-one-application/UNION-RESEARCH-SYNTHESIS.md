Verified: `_turn_done` exists at session_supervisor.py:1086, and `structured_output` appears only in a docstring at line 279 — `_turn_done` does NOT read `ev["structured_output"]`. The map's claim is **Observed-correct** (the drop is real), but "3-line fix" is Inferred (I did not trace the fix). 

I now have decisive ground truth across all four domains. Writing the synthesis as my final response.

---

# THE UNION RESEARCH SYNTHESIS — Substrate Unification
### The context the build stands on. Provisional, honestly-statused, arbitrated.

This synthesis folds the UNION MAP together with three adversarial challenges (completeness, unification-feasibility, storage-supabase). I re-verified every load-bearing fact against the live repo `/home/tim/company` and arbitrated where map and challenges disagreed. **The map is a strong viewpoint-synthesis with two wrong numbers, one phantom citation, and one over-claimed thesis. The challenges are mostly right but overstate the "unwired" rebuttal.** This document corrects all of them and states what is *earned* vs *not yet earned* before the build.

**Evidence labels used throughout:** Observed (seen in code, no execution) · Inferred (pattern-match, unverified) · Verified (confirmed by execution/test). Per Tim's mandate, load-bearing claims are labelled.

---

## 0. THE ORGANIZING CUT — syntax ≠ resolution ≠ identity

The map's hinge sentence — *"granularity is a field on the scheme row → one address space queried one way"* — silently fuses three layers that fail **independently**. This is the spine of everything below:

- **Syntax** (`scheme://body#frag`): one tagged-string space. **Unifies trivially — it already is one.** [Verified: `SCHEMES` at `contracts/address.py:116`]
- **Resolution** (address → content): **NOT one mechanism.** There are at least **two** resolvers. [Verified: `resolve_address` if/elif at `runtime/cognition.py`; second resolver `resolve_scope` at `runtime/suite.py:9117`, JSON-backed, explicitly *"NOT live"*]
- **Identity** (what makes two addresses the same thing): schemes carry **incompatible identity models** a row-add cannot reconcile (content-hash vs mutable-location vs uuid vs computed-centroid).

> **The corrected thesis (replaces the map's grand one-sentence):** One address **syntax** (16 schemes, verified) unifies trivially and *is* the right spine; but it fronts **two resolvers**, **four irreconcilable identity classes**, a typed-edge "law" that fits ~2 of its 7 claimed surfaces, a recogniser-unification that holds for predicates but **not** for the producer (`lifters.extract`), and an entire **unaddressed Shape-B event tier**. The feasible union is **grammar-as-data + registry-base + storage-seam-widening**; the **blocks** (file://↔cas:// identity, channel:// conflict, nested vec://cluster:// grammar, Spine-3-as-one-law, lifter-as-RULE_OPS, Shape-B addressability) are **decisions, not bridges** — none dissolves by adding a row.

---

## PART 1 — THE RECONCILED PATCHWORK INVENTORY

### 1.0 Authoritative fact reconciliation (map vs challenges, arbitrated against live repo)

| Fact | Map said | Challenge said | **Verified truth** | Source |
|---|---|---|---|---|
| Scheme count | 16 | 16 | **16** ✅ | `contracts/address.py:116` |
| `channel`/`cluster` in SCHEMES | NO (gap) | NO | **NO — real gap** ✅ | grep absent |
| FsStore method count | 70 (×3) | 77 / 79 | **77 top-level defs** (`^    def`); challenge's 79 counts inner defs; **61 called on `self.store`** | `grep -cE "^    def " store/fs_store.py` = 77 |
| Resolver Protocol | 10 | 10 | **10** ✅ | `contracts/resolver.py` |
| **Seam ratio (load-bearing)** | 10/70 = 14% | 10/77 = 13% | **10/61 ≈ 16%** (Protocol vs *call-surface*, the only denominator that matters) | computed |
| `_RESOLVABLE` tuple | "derive it" | 9, 7-out-of-sync | **9 schemes, 7 missing** (blob/vec/ui/code/exchange/file/project) ✅ | `runtime/territory.py:32` |
| `_CORPUS_REGISTRIES` rows | "6 of ~25" | 6 | **exactly 6** (mark_type, generation_policy, relation_type, ai_tic, projection, mind) ✅ | `runtime/suite.py:360` |
| agent_sessions files | **13** | 1,068 | **1,068** — map off by ~82× ✅ | `find .data/store/agent_sessions -maxdepth 1 -type f` = 1,068 |
| objects / events | 18,727 / 6,449 | (confirmed) | **18,727 objects / 6,449 event-lines** ✅ | `find`/`wc -l` |
| `VerdictPanelRegistry` | cited | doesn't exist | **class is `PanelRegistry`** ✅ | `runtime/verdict_panels.py:31` |
| 2nd CapabilityRegistry | missed | exists | **`introspection/registry.py:55` — distinct class** ✅ | grep |
| DNA `dna/types.json`, `counterpart/design/substrate/`, `substrate-assemble.py` | "Company ground truth, **built**" | phantom — separate repo | **PHANTOM in `/home/tim/company`** — they live in **`/home/tim/repos/counterpart/design/`** | `ls` fails in company; `find` locates them in counterpart repo |
| `resolve_model` wired? | "nothing calls it" | "called in 3 places" | **DEFINED (`model_routing.py:105`), imported NOWHERE; the 3 "callers" are COMMENTS saying "does NOT change today's firing"** → map's "unwired" stands; challenge overstated | grep |
| `structured_output` drop at `_turn_done:1086` | "real, 3-line fix" | "didn't open it" | **Drop is real (Observed): `_turn_done` does NOT read `ev["structured_output"]`; the field appears only in a docstring line 279.** "3-line fix" is **Inferred** | grep |

**Meta-finding (arbitration cuts both ways):** the map's two *safest-looking* sections (storage counts, scheme grammar) contained its *worst* error (agent_sessions 13→1,068) and its *biggest* blind spot (the nested `vec://cluster://` grammar). The completeness challenge's Cluster-D rebuttal **overstated** — `resolve_model`/`forms` are *referenced*, not *called*. **The map's "built-but-unwired" cluster stands** once you distinguish exposure from invocation.

### 1.1 Address schemes — ONE grammar, but THREE resolution/identity classes inside it

The 16 schemes are real, but they are **not** one homogeneous space. The field that actually matters is **not granularity** — it is **identity-class** and **resolution-path**:

| Scheme | Identity class | Resolution path | Status | Unify verdict |
|---|---|---|---|---|
| `run`, `cas`, `skill`, `context`, `session`, `cap`, `board`, `clone`, `mind` | content-hash / uuid (per-scheme) | **dispatch** (`resolve_address`) | resolvable | **GENUINELY UNIFY** (the 9 in `_RESOLVABLE`) |
| `vec` | computed, **body is itself an address** | reached via `store.put_vector`, NOT `resolve_address` | deferred-in-resolver | **CONDITIONAL** — needs nesting rule |
| `ui`, `code` | location (JSON join) | **`resolve_scope`** (the *2nd* resolver) | deferred-in-resolver | **PARALLEL RESOLVER — real work, not a row-add** |
| `file`, `project` | **mutable-location** | recollection lane (promised) | register-but-defer | **IDENTITY CLASH with `cas://` (content-hash)** |
| `exchange` | uuid | recollection lane (promised) | register-but-defer | conditional |
| `blob` | content-hash | none wired | fail-loud | trivial when wired |
| **`channel`** | **TWO models, no join key** | resolver would fail-loud | **USED, NOT IN SCHEMES** | **CONFLICT, not duplication** |
| **`cluster`** | **computed aggregate** (re-clustering changes it) | `bridge.py` clustering | **USED, NOT IN SCHEMES** | **CATEGORY MISMATCH — not a stable referent** |

**The big miss the map reduced to one line — the recursive scale/cluster layer.** [Verified: `store/fs_store.py:920` `space_address` is **flat string concatenation** (`addr = f"vec://{source}"; addr += f"#space={space}"`); `runtime/scale.py:34,282` produces the live key `vec://cluster://<space>/k<K>/<label>#space=scale:<space>:k<K>`.] This is **a scheme-inside-a-scheme** (a `vec://` whose body is a full `cluster://` address) **plus a `scale:<space>:k<K>` fragment sub-grammar** that is not a scheme at all. A flat `parse_fn`-per-row table keyed on the leading `scheme://` **cannot parse this** — it splits on the first `://` and mis-keys. **This is the single load-bearing thing the union design must model before flattening SCHEMES.**

### 1.2 Registries — ONE mechanism, but the dedup is PARTLY ALREADY DONE

[Observed] The single pattern (`os.listdir → importlib.spec_from_file_location → fail-loud on FIELDS → id==filename → dict-like → discover()/rediscover()`) is copied across ~25 dirs. **But Spine-2's headline ("collapse ~25 copies into one base") is partly already done and the map didn't notice:**
- `SkillRegistry` and `ContextRegistry` **already share `_BaseEntryRegistry`** [Verified by feasibility challenge; structurally identical ENTRY_FIELDS].
- `board_edges` **already reuses the `relation_types` class** (same RELATION_TYPE schema).
- The repo **already names the consolidation** the "FUTURE NEWMOD reuse pass" (`projections.py`).

**Count by the right unit:** there are **28 `*Registry` class definitions** (incl. **two** `CapabilityRegistry`, and the real `PanelRegistry` ≠ the map's phantom `VerdictPanelRegistry`), but the file-discovered *instances* and the *dirs* are different counts again. Spine-2 must not propose work that exists.

The full registry table from the map stands (NodeRegistry, RoleRegistry, Skill/Context, Projection, Lifter, Form, GenerationPolicy, RelationType+board_edges, MarkType, ItemType, SourceType, AttachmentType, Mind, OperatorMemory, Flow, AiTic, ModeDetectionRule, Dial, Binding, Check, **PanelRegistry**, Routine, Platform) — **with the two corrections above and the two declared outliers** (CapabilityRegistry: binary-discovered singleton + a *second* class at `introspection/registry.py:55` to dedup; UI_REGISTRY: JSON-loaded).

**Hardcoded vocabularies that are NOT registries but should be:** `SCHEMES` literal; `resolve_address` if/elif; `EDGE_KINDS` dict (`contracts/node_record.py`); port-types as bare strings; `_safe()` address→filename transform (lives silently in `fs_store`, belongs in `address.py` as a declared contract); `CONTENT_KINDS` defined twice.

### 1.3 Typed-edge surfaces — NOT one law (see Part 2 for the walk-back)

Seven surfaces exist, but they are **categorically different relations**, not seven instances of one law (full arbitration in Part 2): node-graph PORTS (type-compat check), relation_types+board_edges (genuine equal-opposite), board links, minds order (no registry — gap), Provenance lineage (immutable DAG), source_types join_keys (set-intersection), DNA file-edges (in the **separate counterpart repo**).

---

## PART 2 — THE UNIFIED ADDRESS GRAMMAR + THE ONE TYPED-EDGE LAW (corrected)

### 2.1 The grammar that ACTUALLY subsumes the grains — as a CATALOG, with the line it can't cross

Replace the map's *"granularity is a field on the row"* with **three real fields** the scheme registry must carry (from the feasibility challenge, verified necessary):

```
SchemeRow = {
  scheme:          "run" | "cas" | "vec" | "ui" | ... | "channel" | "cluster",
  identity_class:  "content-hash" | "location" | "uuid" | "computed",   # ← the field that matters
  resolution_path: "dispatch" | "resolve_scope" | "recollection-lane" | "deferred",
  nesting:         bool,        # ← vec/cluster bodies are themselves addresses
  fragment_grammar: str | null, # ← the "scale:<space>:k<K>" sub-grammar
  parse_fn, resolver_fn, granularity, status, desc
}
```

**What this buys (FEASIBLE):**
1. **Promote `SCHEMES` literal → data registry** (one row/scheme). The prose-comment status tracking in `address.py` becomes a machine-readable `status` field.
2. **`resolve_address` if/elif → `SCHEME_HANDLERS[scheme]` table dispatch** — **but only for the 9 flat `_RESOLVABLE` schemes.** [Verified feasible.]
3. **Derive `_RESOLVABLE` from `SCHEMES.keys()`** — kills the verified 7-out-of-sync drift (`territory.py:32`). This is the highest-value, lowest-risk move in the whole build.
4. **All sub-address grammar lives in `address.py`** (`parse_session_address`/`parse_clone_address` already there; add `parse_vec_address`, `parse_mind_address`).

**The line the catalog CANNOT cross (BLOCKS — decisions, not bridges):**
- **Nesting rule is mandatory.** `vec://cluster://...#space=scale:...` proves scheme bodies can be **whole addresses** + carry a **fragment sub-grammar**. Either the grammar is **recursive** (declared) or the flat table is wrong. **This must be proven against the live key before flattening.**
- **`file://` (location) vs `cas://` (content-hash) cannot dedup/cache/resolve the same way.** "One space" needs an **identity-reconciliation decision** (pick a winner, or carry two identity classes forever). Not a row.
- **`channel://` is a conflict, not a duplication** [Verified: `cc_channels` member-ID = handle vs `session_channels` member-ID = session UUID, no join key]. Adding the row requires **deciding the identity model first.**
- **`cluster://` is a computed aggregate** — re-clustering changes the referent, so the address isn't stable. Decide: stable address or recomputed query-result? Different *category*.
- **`ui://`/`code://` resolve through the 2nd resolver** [Verified `resolve_scope` at `suite.py:9117`, JSON `design/_system/addresses.json`, *"NOT live"*]. Union = **collapsing `resolve_scope` into the dispatch chain — real work.**

### 2.2 The typed-edge law — HARD WALK-BACK (the map's biggest abstraction error)

**Do NOT deliver "one law over 7 surfaces."** The law — *"a valid typed edge is a VERB with an EQUAL OPPOSITE; direction is which end you read from"* — holds for **~2 of the 7** claimed surfaces:

| Surface | Is it "verb-with-equal-opposite"? | What it actually is |
|---|---|---|
| `relation_types` (`directed/inverse/near/far`) | **YES** ✅ | the genuine law |
| `board_edges` (reuses relation_types class) | **YES** ✅ | same law (already shares the class) |
| node-graph PORTS (`Number→Text` rejected) | **NO** | a **type-compatibility check** — no inverse verb |
| source_types `join_keys` | **NO** | **set-intersection** on shared fields |
| Provenance lineage | **NO** | an **immutable made-from DAG** — direction intrinsic, not "which end you read" |
| minds composition order | partial | **no registry (gap)** |
| DNA file-edges | n/a | **in a separate repo** (see below) |

So: **express the equal-opposite law once for the relation-type family** (relation_types + board_edges → one `relation_types/` dir with a `scope:["board","corpus"]` field) — and **name ports, join_keys, and lineage as the distinct edge categories they are.** "Express it once, each surface consumes it" **cannot** work across three incompatible edge kinds. **This is a wrong abstraction, not unbuilt work — it BLOCKS as stated.**

**Citation discipline (must fix in the triad):** the cited authority `dna/types.json` and the "1,050-edge proven substrate cut" (`counterpart/design/substrate/`, `substrate-assemble.py`) are **PHANTOM in `/home/tim/company`** — [Verified: they live in **`/home/tim/repos/counterpart/design/`**, a *separate* repo]. *"That is the equal-opposite, built"* is an over-claim: aspiration in another repo cited as Company ground truth. In-repo, the concept exists only as design prose in `build-prep/` and one phrase in `runtime/projection.py`.

---

## PART 3 — STORAGE RECOMMENDATION: GO, WITH SHAPE

**Verdict: GO — local Postgres + pgvector as the union store; cloud Supabase as a *later* sync/realtime/mobile tier, NOT the migration target.** (The storage challenge is the most aligned with the map and the most honest; I carry it, with the seam number corrected.)

**Three things must be true or the recommendation is wrong:**

1. **Local-first deployment, not cloud.** Every `head()`/`get_vector()`/`load_agent_session()` is a cheap local ext4 read today. Pointing the hot path at *cloud* Postgres = network round-trips = a **regression** on a local-first stack (ext4, never `/mnt/c`, RTX-4080-local AI). Run Postgres **locally** (same WSL box / sibling container). Cloud is replication/realtime/mobile, addressed identically because **the address never changes.**
2. **The registries DO NOT move.** Tables hold the **addressed graph + embeddings** (objects, refs, meta/provenance, events, vectors, sessions, marks, findings, annotations, dispositions, pins, memo, graphs, chat). **Git holds every `<registry>/*.py` row** ("Git is the migration system"). `_CORPUS_REGISTRIES` becomes an *enumerable index over them*, not a relocation into SQL.
3. **The seam is the FIRST deliverable — before any backend exists.**

**The seam gap is the load-bearing storage fact [Verified]:** Protocol = **10** methods; FsStore = **77** defs; methods actually **called on `self.store`** ≈ **61**. Ratio = **10/61 ≈ 16%**. A Supabase backend implementing only the Protocol is **immediately ~84% incomplete.** This is the real cost, and it pays off regardless of backend:
- **Step 1a** — widen `Resolver` Protocol 10 → the real ~61-method call surface.
- **Step 1b** — re-type `Suite.store: FsStore` → `Suite.store: Resolver` (stays green on fs; this is what makes a 2nd backend *possible*).
- **Step 1c** — **absorb the two bypass namespaces** (correctness, not polish): `cascades.json` via `_ActionRegistry(store.root / "cascades.json")` [Verified at `suite.py:394`] and `agent_sessions/channels.jsonl` via `session_channels.py` — both reach the store root *outside* the method surface and would be silently stranded.

**Vectors [Verified from real files, simpler than the map implied]:** active `vectors/` is **mixed-dim BY DESIGN** — 2560-dim (`pplx`, `emb=pplx`) AND 1024-dim (`bge-m3`, default) coexist at distinct `(item, space, emb)` keys (Tim's multi-layer model, not corruption). Separate concern: `vectors.bge-backup-20260615/` (2,793 vectors, "no API path") is an **archival decision** — re-ingest as a named `emb` layer or archive out of root; do **not** conflate it with the live bge layer. Schema = one table mirroring `put_vector` verbatim:
```sql
CREATE TABLE vectors (
  address text PRIMARY KEY, source text NOT NULL, space text, emb text,
  dim int NOT NULL, model text NOT NULL, content_hash text NOT NULL,
  vector float4[], ts timestamptz );
CREATE INDEX ON vectors (space, emb);   -- the filter, not the vector
```
At ~9k vectors: **`WHERE space=X AND emb=Y` then exact cosine scan is sub-10ms. Do NOT build HNSW/IVFFlat/halfvec/per-dim-split.** Mixed dims coexist fine because you never compare across them (the `(space,emb)` filter isolates each layer — exactly what `index_corpus` does today).

**The ONE query that makes it a union (= the acceptance test, a ready loop-prep criterion):**
> *Board items of type `request`, with a `responds_to` edge to project P, modified since T, ranked by cosine similarity to query-vector Q.*
```sql
SELECT i.address, 1 - (v.vector <=> :q) AS score
FROM board_items i
JOIN edges   e ON e.source = i.address AND e.kind='responds_to' AND e.target=:project
JOIN vectors v ON v.source = i.address AND v.space='history' AND v.emb='pplx'
WHERE i.type='request' AND i.modified_at >= :t
ORDER BY score DESC;
```
If the migration serves this, the union is real. If you can't write it, the union is hollow.

**Migration shape (ordered, reversible, fs-fallback each step):** 1 Seam (10→61, re-type, absorb bypasses) → 2 Local PG+pgvector stand-up → 3 Shape-B JSONL → tables (`WHERE field=X`; events.jsonl at 6,449 lines is the I/O argument; **agent_sessions at 1,068 files is a bigger dir-scan the map never flagged**) → 4 Shape-A dirs → upsert tables → 5 vectors → the table above → 6 concurrency swap (`flock`/`tmp+rename` → advisory locks + ACID; the `append_event` monotonic-unique seq → SERIAL, load-bearing for the SSE cursor) → 7 CAS blobs → `content` table or Supabase Storage → 8 BGE-backup decision.

**Extensions:** pgvector **YES core**; **Realtime (`postgres_changes`) YES — strongest concrete win** (`events_since(seq)` maps directly onto a logical-replication feed → fabric/board/coherence go poll→push); RLS **conditional/premature** (one entity, single operator — only if the mobile PWA hits Postgres directly); Storage **optional** (CAS blobs); PostgREST/Auth **later**.

---

## PART 4 — WHAT RENDERS THROUGH THE ONE INSTRUMENT (via the registries)

**The instrument = the universal projection (the wheel/lattice).** Engine: `runtime/projection.py` (`build_projection`, pure `project()`). [**Verified-GOOD** — the one map claim that held up under all three challenges: `runtime/bridge.py:866` confirms `/api/projection` AND the MCP `project` door route through the **same** `Suite.project` engine, fulfilling *"everything done through the UI must be done through the MCP doors."*]

**Registries ARE the instrument's configuration (no hardcoded layout):**
- **BindingRegistry** (`bindings/`) fills the seed-equation slots (`angle_from`, `radius_from`, `space`, poles, `order_by`) — the active row determines every sector (`x=2π/n`, `θ=kind/type`, `r=time-from-NOW log | semantic cosine | separator lean`, `depth=address nesting`). No hardcoded sectors.
- **ProjectionRegistry** lenses become `vec://<item>#space=<projection>` spaces the wheel queries.
- **NodeRegistry** → `/api/object_info` → ONE generic `ai-node` shape (zero per-type frontend code; states via CSS custom-property tokens).
- **render_hint** on role rows + **mark_types.direction** = rendering intent declared as data.
- **Drill-in:** wheel tap → `projection:select {address,...}` window event → DNA gallery renders the drilled unit; the address resolves through the one resolver.

**The legibility gap (the root one):** the operator-surface design names six self-describing facets (address/thing, lens, element, control, destination, journey/state) but **labels are currently hardcoded React strings.** The union: a **legibility type** — registry rows carry self-description fields; the instrument reads them at render time. Collapses the hardcoded-string problem and the legibility gap together.

**Frontend duplications to absorb:** two `address.ts` (canvas + surface) → one shared lib; dual `ui://` registry (static `addresses.json` vs runtime `/api/ui_info`, **no diff gate**) → static authoritative, runtime derives, FORM-gate diffs them; `NODE_STATES` tokens disconnected from `dna/tokens.json` → draw from the DNA semantic token tree; `company/design/` is a one-way read-copy from Windows-side canonical (silent-overwrite risk).

---

## PART 5 — OPEN RISKS + WHAT A FURTHER COVERAGE PASS MUST CAPTURE

**Risks the challenges surfaced (all verified):**

1. **The thesis "one flat address space subsumes all granularities" is NOT EARNED.** Contradicted by (a) the live nested key `vec://cluster://...#space=scale:...` and (b) the entire unaddressed Shape-B tier. The union is "one address space for content + one unaddressed event tier" — **state this, do not let the thesis claim subsumption it lacks.**
2. **Shape-B (8 JSONL leaves: events, marks, pins, dispositions, annotations, findings, chat, mail) has NO scheme.** [Verified §6 of map: findings "ride the event log, no `coherence://` scheme" = they *reference* addresses but are not *in* the address space.] events.jsonl = 6,449 lines, the highest-volume live tier. **Decision required:** give them a scheme (admit them to the address space) OR explicitly carve them out. Don't paper.
3. **Storage census was a partial read wearing a verified costume.** agent_sessions 13→1,068 (~82× error) means **every Shape-A count must be re-censused before sizing the migration.** A plan sized on "events.jsonl is the I/O argument" misses that **agent_sessions at 1,068 files is the bigger dir-scan.**
4. **Two resolvers, not one** — collapsing `resolve_scope` into the dispatch chain is real work the map costed as a row-add.
5. **Identity clashes block row-adds:** `file://`↔`cas://` (location vs content-hash), `channel://` (two registries, no join key), `cluster://` (computed, unstable referent).
6. **Lifters need a separate producer-authoring contract** (Part 6).
7. **`structured_output` drop is real** [Verified: `_turn_done` at `session_supervisor.py:1086` does not read `ev["structured_output"]`; field only in docstring line 279] — but **"3-line fix" is Inferred, not traced.** If the keystone loop depends on it, verify the fix scope before building.

**What a further coverage pass MUST capture (before the union design is safe):**
1. **Re-census ALL of Shape-A**, not a slice (the 13→1,068 error invalidates §3 sizing).
2. **Model the scale/cluster/`scale:` layer as first-class grammar** and prove the `parse_fn`-per-row design against the live nested key — either the grammar is recursive or the table design is wrong.
3. **Decide Shape-B addressability** explicitly.
4. **Re-verify every "unwired" claim with a caller-grep that distinguishes invocation from reference** (`resolve_model` = defined, imported nowhere, "callers" are comments → **unwired stands**; `LifterRegistry.extract()` = no caller → **unwired**; `forms` = exposed at `bridge.py:908`, no ingest `route()` caller → **unwired as an ingest path**).
5. **Recount registries by the right unit** (28 class-defs incl. 2 CapabilityRegistry + PanelRegistry; file-discovered instances; dirs) and **note which dedup is already done** (`_BaseEntryRegistry`, board_edges-reuses-relation_types) so Spine-2 doesn't propose existing work.
6. **Census the counterpart-repo DNA substrate** (`/home/tim/repos/counterpart/design/`) as a *cross-repo dependency* — and decide: the Company **generalizes** the engine, it does **not** adopt DNA's design-specific instance.

---

## PART 6 — THE BUILD SEAMS (substrate engine ⨯ act-layer ⨯ structural⨯semantic union)

**The keystone loop (substrate + triggers + routing + self-build):**
```
ghost node detected → trigger fires → cc_launch node runs → writeback → re-census
(structural)          (act-layer)      (build, model-routed)  (corpus)    (structural)
```

**SEAM A — Triggers (FEASIBLE).** A trigger = `event-kind → when-predicate → action`. [Verified: all three halves exist — event taxonomy `activation.py:ACTIVATION_CONTEXTS`, when-predicate `rules.py:RULE_OPS`, action/routing `rules.py:DESTINATION_KINDS + route()`.] **Only the binding is missing** — a file-discovered `trigger/` registry + driver (clone `mode_detection_rules.py`, the strongest template). **Self-trigger guard:** exclude `responds_to`-edged items in the `when` (a reply `file_item` re-emits `board.filed` → runaway spawn; mirror `OPERATOR_ACTIVITY_KINDS`).

**SEAM B — THE "ONE CRUX" IS FALSE FOR LIFTERS (corrected — the map over-reached by one element).** The map: *"forms.match, lifters.extract, triggers.when are all recognisers → make them RULE_OPS data-AST → all become Tier-B authorable."* [**Verified at `rules.py:65`: RULE_OPS is a closed PREDICATE grammar** — ops are field/lit, and/or/not, eq/ne/lt/le/gt/ge, add/sub/mul, in/contains. **There is NO produce/extract/emit op.**]
- `triggers.when` + `forms.match` = **predicates → fit RULE_OPS** ✅
- `lifters.extract` = a **producer/transform** (pulls spans, emits new typed records) → **RULE_OPS CANNOT express this** ❌

So: **triggers + forms unify via RULE_OPS** (both become `_CORPUS_REGISTRIES` Tier-B rows, agent-authorable through one gate); **lifters need a SEPARATE producer-authoring contract.** The callable-guard [Observed at `suite.py:9886`] blocks lifters for a reason RULE_OPS does not remove: **extraction is code, not a predicate.**

**SEAM C — Structured-output gap (BLOCKS the cc_launch structured path).** [Verified: `_turn_done` (`session_supervisor.py:1086`) does not read `ev["structured_output"]`.] A CC launched with `--json-schema` has its output dropped. Fix spans `session_supervisor.py`, `cc_clone.py`, `routine_runner.py`. **"3-line" is Inferred — verify scope before calling it small.**

**SEAM D — corpus (semantic) ⨯ substrate (structural) are TWO LENSES on the SAME addressed units.**
- **Substrate (structural)** = the address-registry. **DNA built a first cut — but in the SEPARATE counterpart repo** (`/home/tim/repos/counterpart/design/`: 621 addresses, 22 types, 1,050 typed edges, 14 ghost nodes; reference engine `engine/substrate-assemble.py`). [These numbers are **DNA-self-reported, uncited to a live Company file** — re-verify before relying on them.]
- **Corpus (semantic)** = the same units embedded into `vec://<source>#space=<projection>` spaces, cosine + rerank.
- **The union:** ONE engine, per-project instances. **DO NOT build the Company's substrate on DNA's design-specific instance — generalize it.** Flag the **cross-repo dependency** explicitly in the triad. The `registry-generation` chain (auto-populate `ui://` from mockups) and DNA's census are **two passes of one pipeline at two granularities** (UI-element vs file) — ★ must reconcile whether registry-generation is ancestor or live.

**SEAM E — Coherence as one lens over the same substrate.** The three gates become the first rows of a `finding-type` registry; findings ride the **existing** event log (`kind="coherence.finding"`, address-stamped — **no new store, no `coherence://` scheme**, which is consistent with the storage GO); dispositions ride the existing pin-overlay; burn-down = read-time rollup. The coherence substrate and the address substrate are the same substrate at different aspects.

**SEAM F — The disposition system exists twice in embryo** (`_ORPHAN_ROUTES` hardcoded dict + `governance.POLICY` AUTO/SURFACE/CONFIRM/LOCKED): **unify these two, don't invent a third.**

---

## THE ONE SENTENCE (corrected, earned)

One address **syntax** (16 schemes, verified) is real and the right spine — and **grammar-as-data + table-dispatch for the 9 flat schemes + the `FileDiscoveredRegistry`/`_CORPUS_REGISTRIES`-extension + the storage-seam widening (10→61) + local-Postgres/pgvector + triggers-and-forms-via-RULE_OPS + the one shared projection engine** are all **FEASIBLE and buildable** — but the union does **NOT** collapse by row-add at four places that are **decisions, not bridges**: the **recursive `vec://cluster://...#space=scale:...` grammar**, the **`file://`↔`cas://` / `channel://` identity clashes**, the **typed-edge law that fits only the relation-type family** (ports/join_keys/lineage are different edge categories), and the **producer `lifters.extract` that no predicate grammar can author** — with an **unaddressed Shape-B event tier** that the thesis must stop claiming to subsume and a **DNA substrate engine that lives in a separate repo** the Company must generalize, not adopt.

**Key file anchors (all verified in `/home/tim/company`):** `contracts/address.py:116` (SCHEMES=16) · `contracts/resolver.py` (10-method seam) · `store/fs_store.py` (77 defs, `_safe()`, `space_address():920` flat-concat) · `runtime/scale.py:34,282` (live nested `vec://cluster://...#space=scale:` key) · `runtime/cognition.py` (`resolve_address` if/elif) · `runtime/suite.py:9117` (`resolve_scope` — the 2nd resolver) · `runtime/suite.py:360` (`_CORPUS_REGISTRIES`=6) · `runtime/suite.py:394` (cascades.json bypass) · `runtime/suite.py:9886` (callable-guard) · `runtime/territory.py:32` (`_RESOLVABLE`=9, 7-out-of-sync) · `runtime/rules.py:65` (RULE_OPS = closed predicate grammar, no producer op) · `runtime/projection.py` + `runtime/bridge.py:866` (one instrument engine — verified-good) · `runtime/session_supervisor.py:1086` (structured_output drop) · `runtime/verdict_panels.py:31` (`PanelRegistry`) · `introspection/registry.py:55` (2nd CapabilityRegistry) · `runtime/model_routing.py:105` (`resolve_model` — defined, imported nowhere). **Cross-repo (NOT in company):** `/home/tim/repos/counterpart/design/dna/types.json`, `/home/tim/repos/counterpart/design/engine/substrate-assemble.py` (the typed-edge "law" + 1,050-edge cut — phantom as Company ground truth; generalize, don't adopt).