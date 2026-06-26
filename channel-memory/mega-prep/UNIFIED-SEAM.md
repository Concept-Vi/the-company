# UNIFIED SEAM — recollection (OUTER) ⊕ session-recall (INNER)

> The ONE spec both sessions build to. recollection = the broad cross-session/corpus-wide memory; the fork's session-recall = its inner single-session instance. Posted to the communal vault for cross-review (mega-prep working protocol). Author: recollection-design session. Sources: recollection loop-prep (`~/company/build-prep/episodic-memory-adaptation/loop-prep/`: COMPLETION_CRITERIA, IMPLEMENTATION_GUIDE, RESEARCH_SYNTHESIS, OPEN-DECISIONS) + the fork plan (`~/company/channel-memory/plan/`) + the fork code (session_scan/recall/lens) + `seam-mapping.md` (the grounded map this is built from).
>
> **Trust-tags** (vault protocol): `tim-direct` = Tim confirmed in-session · `inferred` = recollection-session evidence-based call · `fabric-derived` = cross-session grounded finding · `channel-relayed` = peer-relayed, proposal-until-Tim. **Self-approval standard: CONFIRMED tim-direct** (Tim→lead via AskUserQuestion; `APPROVAL-STANDARD.md` 94ca745): self-approve consequential + git-revertible + cross-reviewed via high-bar recorded-intent recovery; ping lead→Tim only for truly-irreversible/external.
>
> **★ KEYSTONE (the deepest framing of the session — recorded per lead's ask):** *recovery-quality gates the autonomy → the high-bar recovery condition IS recollection's Pillar-1 done rigorously → building recollection well is literally what makes the fabric's self-approval safe.* **recollection is not a feature; it is the SAFETY SUBSTRATE for the fabric's autonomy.** The high-bar (pattern-level across time AND projects, structure-not-text, not shallow grep) isn't bureaucracy — it's the mechanism.

## 1. The asymmetric nesting (the framing) `[fabric-derived]`
The fork is NOT a miniature recollection. It is the inner **single-session instance of recollection's RETRIEVAL SPINE only**: capture(G1) → embed(G3) → gather(G5) → judge(G6) → recall(G7). recollection wraps that spine with layers the single-session case has no instance of: **distill/rollups (G2), link/provenance graph (G4), proactive injection (G8), health/annealing (G9), and the unified identity/Pillar-1 layer.** So "inner nests in outer" is asymmetric: the fork is one vertical slice (one session's retrieval), recollection is that slice generalized across all sessions PLUS the layers above and below it.

## 2. Component correspondences (the map) `[fabric-derived, both sides cited]`
| Fork (INNER) | recollection (OUTER) | Relationship |
|---|---|---|
| `session_recall` (:8007 embed + :8008 rerank) | G3.1 one-lens embed + G6.1 proofreader | the served stack IS recollection's interim embed-lens + always-on CPU reranker |
| Group-4 panel (extract→judge) | G6 Judgment layer | same extraction-vs-judgment law, same `cognition.py` roles engine |
| `session_lens` (find/decisions/open_loops/catch_up/timeline/directives) | G7 axis-addressed query tools | session-scoped lenses = the single-session case of the cross-session tools |
| 3.7 preferences lens | Pillar-1 identity layer | fork FEEDS, recollection OWNS, ALL sessions feed `[tim-direct]` |
| `project·session·segment` keys | D-1 structural axis-set | the keys ARE the provenance sub-space of multi-space addressing |
| `session_scan` rows | G1 capture / G0.2 atoms | scan rows = one session's atoms |

## 3. The boundary interface — FOUR wires crossing inner↔outer (the contract) `[fabric-derived]`
1. **scan rows → capture atoms** — `session_scan`'s row contract feeds recollection's G1 capture as one session's atoms.
2. **`project·session·segment` keys → structural axes** inside D-1 multi-space addressing (the provenance sub-space; `exchange://<sid>/<i>` is the canonical re-embed-stable identity).
3. **served :8007/:8008 HTTP contract** (env-configurable `EMBED_URL`/`RERANK_URL`) → recollection's interim embed-lens (D-5) + proofreader (G6.1). **The env-configurability makes absorption a config re-point, not a rebuild** — this is the key seam that lets INNER and OUTER share one served stack.
4. **3.7 preference profile → Pillar-1 identity layer** (recollection owns; fork + all sessions feed). `[CONFIRMED by lead, D-2]`
5. **★ 5TH WIRE — channel-scoped recall** (lead's CHANNEL-LAYER-SEAM.md): `cc_channel op=recall {channel, query}` runs recollection's recall SPINE scoped to a channel's attached sessions via the D-1 axes (Tim's "link recall+semantics to channels"). → recollection builds the recall spine **channel-scopable** (a channel = a set of attached session-ids = a structural-axis filter in multi-space addressing). Memory half (this doc) ⊕ channel half (CHANNEL-LAYER-SEAM.md) wire here. `[fabric-derived]`

**Wire-3 served contract (CONFIRMED by lead — build against this exactly):** embed = `POST http://127.0.0.1:8007/v1/embeddings`, documents-mode `{"documents":[[chunk,...]]}` for contextual chunks (per-chunk late-chunking, dim **2560**, INT8, compare by **COSINE**); flat `{"input":[str]}` = single-chunk. rerank = `POST http://127.0.0.1:8008/rerank {query, candidates:[str|dict], top_n}` → `{ranking:[{item,text,rerank_score,orig_rank,rank}]}` (jina-v3, CPU). Keep env-configurable `EMBED_URL`/`RERANK_URL`. GOLDEN RULE: index + query in the SAME space (pplx-4b). Lead channels recollection FIRST before any `@xsession` loadout swap.

## 4. Ownership (who builds what) `[tim-direct framing: recollection owns identity; all sessions feed]`
- **Fork OWNS:** the recall/lenses lane, the served :8007/:8008 stack, `session_scan`, the session-scoped lenses, the spin-up/fork-fleet (Group 8 / 3.8 — no outer correspondent, GAP-3).
- **recollection OWNS:** the data model + multi-space addressing (D-1), distill/rollups (G2), the link/provenance graph (G4), capture-of-all-sessions incl. sidechains (G1/D-9), proactive injection (G8), health/annealing (G9), and the unified identity/preference layer (Pillar-1) — **fed by all sessions**.
- **Build-on, not reimplement:** recollection builds on the fork's served stack + scan; the fork builds on recollection's data-model + addressing + distill. Neither reimplements the other's half.

## 5. Conflict resolutions (winners cited)
- **K1 · License (sharpest — also fixes an internal recollection contradiction).** Resolved **D-4** `[tim-direct: "non-commercial is fine, this is experiments"]` supersedes BOTH the fork's "swap jina→ms-marco for commercial" hedge AND recollection's own Guide §7 "ms-marco for proofreader / jina eval-only" line. **Winner: jina-v3 @ :8008 IS the proofreader.** → recollection IMPLEMENTATION_GUIDE §7 ms-marco-default line is now stale and being corrected.
- **K2 · Address grammar.** Resolved **D-1** `[tim-direct: multi-space addressing]` supersedes the fork's "embedding-lattice-as-master" framing. Canonical identity = provenance `exchange://<sid>/<i>` (re-embed-stable); the embedding space is ONE co-equal sub-space, not the container. **The fork's indexing GATE is OPEN.**
- **K3 · Embed transport (soft).** Resolved **D-5** dissolves :8007-single vs :8001-multi → pplx-4b is one interim lens row in the eventual multi-lens loadout.

## 6. Gaps + resolution/owner
- **GAP-1 · Live re-fingerprint freshness** — the fork's 2.4 has a concrete mtime/size guard; recollection left live-embed freshness implicit. **Resolution: adopt the fork's mtime/size guard** into recollection's live-capture (G1.3). `[fabric-derived]`
- **GAP-2 · Lens↔axis-tool name-map** — some session-scoped lenses (open_loops / catch_up / directives) have no cross-session tool yet. **Resolution: recollection adds the cross-session generalization of each as a P7 registry tool; map them 1:1.** (registry-driven, so additive.)
- **GAP-3 · Spin-up/fork-fleet** (fork Group 8 / 3.8) — no outer correspondent; **fork-owned**, recorded so it's not assumed covered by recollection.
- **GAP-4 · Projection to The Heart** — shared deferral, **Tim-gated on both sides**.

## 7. The decisions that govern both `[see loop-prep/OPEN-DECISIONS.md for the full D-1..D-15 + reasoning]`
Load-bearing for the seam: **D-1** multi-space addressing (provenance = stable identity, embedding = co-equal sub-space) · **D-2** central judge both-by-mode (session model + local big) · **D-4** non-commercial fine (jina stays) · **D-5** interim pplx-4b lens, full lens-set eventual · **D-9** sidechains are first-class units pooled into the rollup arc · **preference-ownership** recollection owns / all sessions feed. All `tim-direct` except D-5/D-9 (`inferred`, high-confidence).

## 8. Build sequencing across sessions
1. **NOW (green, reversible):** this seam doc → cross-review by all sessions → welded into the agreed spec. Plus: scan, indexing, the reversible prep. Each session runs its own timed loop checking the channel for alignment.
2. **Then:** each session builds its owned components against this seam — fork on the retrieval-spine lane, recollection on the wrapping layers + data model + identity — cross-reviewing/welding at the boundary wires (§3).
3. **Standard CONFIRMED (no longer held):** self-approve consequential + revertible + cross-reviewed via high-bar recorded intent; ping lead→Tim only for truly-irreversible/external. (`APPROVAL-STANDARD.md` 94ca745.)

---
*Draft v1 for cross-review. Fork + lead: assess §2–§6 against your plans; flag any correspondence/boundary/conflict I've mis-mapped. Welds at the four boundary wires (§3) are where our work must be clean together.*
