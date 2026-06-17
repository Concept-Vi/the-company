Both decisive confirmations are in:

1. **`resolve_scope` (suite.py:9117) is a genuinely parallel resolution path** — it reads `design/_system/addresses.json` + `code-symbols.json` (regenerated JSON join data, explicitly "NOT live"), entirely separate from `resolve_address`'s dispatch chain. `ui://` and `code://` resolve here, not through the one resolver. "One resolver" is two.

2. **RULE_OPS is a closed PREDICATE grammar** — ops are: field/lit (leaves), and/or/not (boolean), eq/ne/lt/le/gt/ge (comparison), add/sub/mul (arithmetic), in/contains (membership). It evaluates to a truthy/value result for routing. There is **no extraction/produce/transform op** — no way to express "pull these spans out of a document and emit structured records." A lifter's `extract()` produces new typed units; RULE_OPS can only test and route. The predicate-vs-producer category split is real and verified in the grammar itself.

I have all anchors. Writing the verdict now as my final response.

---

# UNIFICATION-FEASIBILITY ADVERSARY — VERDICT

I verified every load-bearing claim against `/home/tim/company`. The map's reconciliation is **honest** (16 schemes confirmed at `contracts/address.py:116`; channel/cluster genuinely absent; the 10-vs-77 seam is real and worse than stated). But the unification it declares conflates two layers. **Grammar unifies trivially. Resolution and identity do not — and that is exactly where "unions not bridges" hits the wall.**

## THE CORE CUT: grammar ≠ resolution ≠ identity

The map's hinge is *"granularity is a field on the scheme row → one address space queried one way."* That sentence silently fuses three layers that fail independently:

- **Syntax** (`scheme://body#frag`): one tagged-string space. Unifies trivially — it already is one. **Spine 1's grammar claim is sound.**
- **Resolution** (address → content): **NOT one mechanism.** Verified: `resolve_address` (cognition.py:842) is one dispatch chain for 9 schemes; `Suite.resolve_scope` (suite.py:9117) is a **second, parallel resolver** for `ui://`/`code://` backed by regenerated JSON (`design/_system/addresses.json`, explicitly "NOT live"). "One resolver" is two.
- **Identity** (what makes two addresses the same thing): **schemes carry incompatible identity models that cannot be unified by adding a row** (below).

"One address space queried one way" is true only at the syntax layer. The map presents syntax-unity as if it were resolution-unity. It isn't.

## THE PER-SCHEME FEASIBILITY TEST (does it resolve through one mechanism with one identity model?)

| Scheme(s) | Verdict | Why |
|---|---|---|
| run, cas, skill, context, session, cap, board, clone, mind (the 9 `_RESOLVABLE`, verified `territory.py:32`) | **GENUINELY UNIFY** | One dispatch, one identity-per-scheme. Spine 1's table-dispatch refactor is real and feasible. |
| **vec://** | **Conditional** | Compound grain `(item, space, emb)` where *item is itself an address* (nesting). The map never states a nesting rule in the grammar. Unifies only if the grammar permits addresses-inside-addresses — undeclared. |
| **ui://, code://** | **PARALLEL RESOLVER** | Resolve through `resolve_scope` + JSON, not the dispatch. Union = collapsing `resolve_scope` into the chain. That is real work, **not a row-add.** |
| **file://, project://** | **IDENTITY-MODEL CLASH (blocks)** | `file://<abs-path>` = mutable-location identity. `cas://` = immutable-content identity. They cannot dedup/cache/resolve the same way. Putting both in "one space" needs an identity-reconciliation decision, not a row. |
| **channel://** | **CONFLICT, not duplication (blocks)** | Two registries claim it: `cc_channels` (member-ID = handle) vs `session_channels` (member-ID = session UUID), **no join key**. The map files this under Cluster-C "duplication to absorb." It is a conflict that *blocks* adding a single `channel://` row until someone decides the identity. Elevate it. |
| **cluster://** | **CATEGORY MISMATCH** | A centroid is a *computed aggregate*, not a stored unit — re-clustering changes it, so the address isn't stable. Is it an address (stable referent) or a query result (recomputed)? Different granularity *category*, not a row alongside the others. |

## SPINE 3 IS A CATEGORY ERROR — infeasible as stated (the strongest finding)

The map: seven surfaces are "seven surfaces of ONE law — a verb with an equal opposite." Against the code, these are **categorically different relations**, not instances of one law:

- **Node graph PORTS** (`Number→Text` rejected at connect): a *type-compatibility check*. Has no "inverse verb." Type compatibility is not directional-relation-with-opposite.
- **source_types join_keys**: a *correlation on shared fields*. A join key is not "a verb with an equal opposite" — it's set intersection.
- **Provenance.inputs lineage**: an *immutable DAG* walked by `FsStore.lineage()`. Direction is intrinsic (made-from), not "which end you read from."
- **relation_types / board_edges** (`directed/inverse/near/far`): these *genuinely* fit the equal-opposite law.

So the law holds for ~2 of the 7 surfaces. Ports and join_keys are **not** instances of it. "Express it once, each surface consumes it" cannot work because three of the surfaces are not the same kind of edge. **This blocks.** It's not unbuilt — it's a wrong abstraction.

Compounding: **the cited authority for the law does not exist in the repo.** `dna/types.json` (cited as "the typed-edge law stated") and `counterpart/design/substrate/` + `substrate-assemble.py` (cited as "the proven substrate cut, 1,050 edges, the equal-opposite built") are **not in `/home/tim/company`** — they live in a separate DNA design repo. In-repo, the concept exists only as design prose in `build-prep/` and one phrase in `projection.py`. So "that is the equal-opposite, **built**" is an overclaim: aspiration in another repo, cited as Company ground truth. (This is a citation-discipline flag, not the headline — fixing the citation doesn't rescue the category error above.)

## SECTION 6's "ONE CRUX" repeats the same conflation — predicate vs producer

The keystone move: *"forms.match, lifters.extract, triggers.when are all recognisers → make them RULE_OPS data-AST → all become Tier-B authorable through one gate."*

Verified against `rules.py:65`: **RULE_OPS is a closed PREDICATE grammar.** Its ops are field/lit, and/or/not, eq/ne/lt/le/gt/ge, add/sub/mul, in/contains — every one evaluates to a truthy/scalar for *routing*. There is **no produce/extract/emit op.**

- `triggers.when` and `forms.match` are **predicates** → fit RULE_OPS. ✅
- `lifters.extract` is a **producer/transform** — it pulls spans out of a document and emits new typed records. **RULE_OPS cannot express this.** A predicate grammar cannot author an extraction. ❌

So the "one move makes forms + lifters + triggers ALL Tier-B rows" is false for lifters. The callable-guard I verified (`suite.py:9886` — explicitly *"a guard against a future row, not the live path"* for lifter/form) blocks lifters for a reason RULE_OPS does not remove: extraction is code, not a predicate. Triggers + forms unify via RULE_OPS; **lifters need a separate producer-authoring contract.** The map's keystone over-reaches by one element.

## WHAT ACTUALLY HOLDS (don't let the critique erase the real wins)

- **Spine 1 grammar + table-dispatch: FEASIBLE.** SCHEMES→registry, `resolve_address` if/elif→`SCHEME_HANDLERS` table, `_RESOLVABLE` (verified separate at `territory.py:32`) derived from `SCHEMES.keys()`. Real, mechanical, correct.
- **Spine 2 registry-of-registries: FEASIBLE.** The ~25× copied `os.listdir→importlib→fail-loud→id==stem` pattern → one `FileDiscoveredRegistry` base is sound (the repo already names it the "FUTURE NEWMOD reuse pass"). `_CORPUS_REGISTRIES` is **6 rows today** (mark_type, generation_policy, relation_type, ai_tic, projection, mind — verified `suite.py:360`), not enumerating all; extending it is real work but no category clash. Skill≡Context and board_edges≡relation_types merges are genuine.
- **The storage seam: the map UNDERSTATES it correctly.** 10-method Protocol vs **77**-method FsStore (not 70), Suite typed to concrete FsStore. A Supabase backend on the Protocol alone is immediately ~87% incomplete. This is the most honest part of the map.

## THE UNIFIED GRAMMAR THAT ACTUALLY SUBSUMES THE GRAINS (and the line it can't cross)

A grammar can subsume every granularity **only if it separates the referent's identity model from its resolution path.** The map needs three things it doesn't currently state:

1. **A nesting rule** — `vec://run://graph/node#space=X` — addresses-inside-addresses, because vec/cluster grains are *functions of other addresses*, not flat bodies. Without this, vec/cluster don't fit.
2. **An identity-class field on each scheme row** — `{content-hash | location | uuid | computed}`. This is the field that actually matters, not "granularity." `cas`/`run` = content-hash; `file`/`project` = location; `session`/`clone` = uuid; `cluster` = computed. **You cannot put location-identity and content-identity in "one resolver" without declaring how they reconcile** — that's a decision, and it's the real friction.
3. **A resolution-path field, not an assumption of one path** — `{dispatch | resolve_scope | recollection-lane | deferred}`. The map asserts one resolver; the code has at least two. Honest grammar names the path per scheme.

With those three fields, the grammar subsumes the grains **as a catalog**. What it still cannot do — and where "unions not bridges" genuinely breaks — is make `file://` and `cas://` *the same kind of thing*. That's not a bridge to remove; it's a semantic incompatibility that a union has to either pick a winner for or carry as two identity classes forever.

## THE ONE SENTENCE (corrected)

One address **syntax** (16 schemes, verified) is real and unifies trivially; but it fronts **at least two resolvers** (`resolve_address` + `resolve_scope`), **multiple irreconcilable identity models** (content-hash vs mutable-location vs uuid vs computed-centroid), a **typed-edge "law" that fits ~2 of its 7 claimed surfaces** (ports and join-keys are not verb-with-opposite edges), and a **recogniser-unification that holds for predicates but not for the producer (`lifters.extract`)** — so the feasible union is Spine 1 (grammar-as-data) + Spine 2 (registry base) + the storage-seam widening; the **blocks** are file://↔cas:// identity, the channel:// two-registry conflict, Spine 3-as-one-law, and lifter-as-RULE_OPS — none of which a row-add resolves.

**Key anchors (all verified in-repo):** `contracts/address.py:116` (SCHEMES=16), `contracts/resolver.py` (10 methods), `store/fs_store.py` (77 methods), `runtime/cognition.py:842` (`resolve_address` if/elif dispatch), `runtime/suite.py:9117` (`resolve_scope` — the *second* resolver, JSON-backed), `runtime/territory.py:32` (`_RESOLVABLE`=9, separate tuple), `runtime/suite.py:360` (`_CORPUS_REGISTRIES`=6 rows), `runtime/suite.py:9886` (callable-guard, "guard against a future row"), `runtime/rules.py:65` (RULE_OPS = closed *predicate* grammar, no producer op). **Phantom anchors (NOT in `/home/tim/company`):** `dna/types.json`, `counterpart/design/substrate/`, `substrate-assemble.py` — cited as built Company ground truth for Spine 3; they live in a separate repo.