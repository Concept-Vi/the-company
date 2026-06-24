---
id: item-c94cdfd3
address: board://item-c94cdfd3
type: idea
source: claude_code
state: captured
title: Adjacent-possible / latent-affordance pass (grounded possibles)
author_session: ch-3mpkjg3r
channel: provider-registry
thread: ''
links:
- kind: sourced_from
  target: board://item-90f569c7
created: '2026-06-22T15:51:28.188108+00:00'
updated: '2026-06-22T15:51:28.188108+00:00'
history:
- from: null
  to: captured
  by: ch-3mpkjg3r
  ts: '2026-06-22T15:51:28.188108+00:00'
  note: filed
---

**Adjacent-possible / latent-affordance pass.** Grounded possibilities — what the system COULD become because parts built/surfaced this session are now connected. NOT facts, NOT recommendations. Each possible separates fact / inference / possibility (the `confidence` field labels the BASIS) and traces to real addresses/files/records. No ranking — flat list. No "should." Gap content lives in `what_is_missing_or_blocking` (surfacing a gap is not ranking). Read-only pass.

Sourced from: board://item-90f569c7 (Tim's green-light). author_session ch-3mpkjg3r, channel provider-registry.

---

### possible-01 — The comparison / review workshop (tracked-dragnet + image versions + threaded annotation)
- **plain_language_possibility:** A place where you generate or drop in a set of images (design options, output variants), each keeps its own history of versions, and you can pin a comment or note directly onto any one of them — then ask the assistant to compare them side by side, with every reaction tracked as part of the record. A working room for "show me the options, let me react, keep the trail."
- **technical_basis:** Three primitives built this session already compose into this without new machinery — the hierarchical/versioned image layer (save_image appends a version axis, list_versions surfaces v1→v2→v3), the threaded-annotation edges on addressed content (board items linked `commented_on` an image address), and the tracked-dragnet that can generate-into a channel and record the run. The annotation mark-types already exist (`reaction`, `favour`, `comment`).
- **evidence_addresses:** image://design-source/* (161 images, confirmed in manifest) · image://design-assets/* (136 images) · code://company/mark_types/reaction.py · code://company/mark_types/favour.py · code://company/mark_types/comment.py · board edge `commented_on` (board_edges/commented_on.py)
- **related_tools_files:** runtime/cc_images.py (save_image/list_versions/list_images — the version axis at lines 130-153, 189-194) · runtime/cc_dragnet.py (generate-into a channel) · board_edges/commented_on.py · attachment_types/images.py
- **why_it_might_matter:** The pieces for "react to a set of options and keep the trail" are all present but never wired into one surface; today an image is stored + addressable but there is no review/compare experience over it.
- **what_it_could_become:** A generative-options review room — generate N variants into image://<channel>/generated/*, see them as a versioned gallery, annotate/favour/react per option, and the reactions become a queryable record the system learns taste from.
- **what_is_missing_or_blocking:** No front-end surface renders the version axis or the per-image annotation thread (the data model exists; the review UI does not). The `images` attachment_type is present in the registry file but `cc_attachments op=types` over the live MCP did not list it (server may need a bounce to pick up the add-a-row file). A real "compare these two" view needs a DNA archetype.
- **what_tim_would_need_to_judge:** Whether a compare/react workshop is a surface he wants, and what the review gesture should feel like (side-by-side? overlay? a favour-vote?) — a product/taste call only he can make.
- **confidence:** INFERENCE — every composing primitive demonstrably exists and is wired at the data layer; the leap (one review surface that renders versions + annotations together) is unproven and unbuilt.
- **recommended_next_exploration:** Mock the compare-and-react view against the real image://design-source set; confirm the `images` attachment_type lists live after a bridge bounce.

---

### possible-02 — The design system becomes a generative design loop (addressable design source + roles)
- **plain_language_possibility:** Now that the whole real design system — 161 source images, the brand assets, even the CSS that git was hiding — lives at proper addresses inside channels, the assistant can be asked to generate a NEW screen "in our design language" and actually pull the real tokens/references as grounded input, instead of inventing a generic look.
- **technical_basis:** The design-knowledge / design-source / design-assets channels now hold the design system as addressed artifacts (the M3 dragnet over counterpart/design embedded the git-ignored design system into the searchable code_archaeology space — the thesis-proof was a query for design-system tokens returning the previously-hidden reference CSS as #1). The 32 declared roles are a registry the system can resolve a generation role from. The dragnet is tracked, so a design-generation run leaves telemetry.
- **evidence_addresses:** image://design-source/* (161) · image://design-assets/* (136) · design-knowledge channel (1 dragnet_run attached) · field-index declares=role→32 · the code_archaeology space record for the design CSS (per fork harvest claim-5 M3) · code://company/<role files> (the role registry targets in field_index.jsonl)
- **related_tools_files:** ops/code_archaeology.py (the design-knowledge dragnet) · runtime/cc_dragnet.py · design/design-system.css (the now-addressable system) · .data/store/code_archaeology/field_index.jsonl (declares=role)
- **why_it_might_matter:** The recurring failure named in the harvests is "agents sample → get confident → build from partial info"; for design specifically, the git-ignored real system was invisible. It is now findable — closing the exact gap for the design domain.
- **what_it_could_become:** A from-DNA generation loop where "make me this screen" resolves the real design language as grounded context, generates into an image channel as a versioned candidate, and the run is tracked — design becomes grounded-by-construction the way decisions became grounded-by-construction (L1).
- **what_is_missing_or_blocking:** No role currently declares "generate a design artifact grounded in the design-knowledge channel" — the wiring from a generation role to the design corpus as retrieval context is unbuilt. Record-quality of the design dragnet is spot-checked, not exhaustive (fork's honest caveat).
- **what_tim_would_need_to_judge:** What "in our design language" means as a constraint — how literal vs. generative, and whether a generated candidate is good enough to be a real proposal. A pure aesthetic/semantic judgment.
- **confidence:** INFERENCE — the design corpus is verified-addressable (fact); a generation role grounded on it is a real but unbuilt connection.
- **recommended_next_exploration:** Query the design-knowledge channel for "our color and type tokens" and confirm the retrieval returns the real system; then sketch what a grounded design-generation role's inputs would be.

---

### possible-03 — A cross-perspective map of the four lanes (conceptual board edges + harvest corpus)
- **plain_language_possibility:** The four work-streams that just wound down (resolver/decision-wire, the operator surface, the recall substrate, the direction circuit) each wrote down their claims AND how those claims connect — and they independently arrived at the SAME underlying law. Those connections are now first-class typed links, so the system could draw one map showing how the four perspectives compose, where they block each other, and where they agree on the same principle.
- **technical_basis:** The conceptual edge kinds (composes_with / blocked_by / refutes / same_law) were added to the board this session precisely because the harvests carried these relations and the board had been collapsing them to "references." All four harvest files use them, and all four `same_law` edges name the identical law: "verify the actual thing, never the claim." The harvests are ingested into the corpus (retirement-member records) and board-linked.
- **evidence_addresses:** board_edges/composes_with.py · board_edges/blocked_by.py · board_edges/refutes.py · board_edges/same_law.py · the four harvest files (build-prep/the-one-application/harvest/ch-8djrpmsl-fork-HARVEST.md · projection-HARVEST.md · ch-ouui7r0k-recollection-HARVEST.md · ch-piffgfxv-wildcard-HARVEST.md) · board harvest roots cited in them (board://item-ef7eb599 projection · board://item-a7b5b202 fork)
- **related_tools_files:** runtime/cc_board.py (polymorphic edges + reverse_traverse) · runtime/cc_retire.py (harvest_member writes the perspective + typed links) · the four HARVEST.md files
- **why_it_might_matter:** The four-way convergence on one law ("the look beats the inference / default-to-wrong") is a strong, independently-arrived-at observation — it is the closest thing to a verified company principle in this body, and it is currently legible only by reading four files.
- **what_it_could_become:** A rendered constellation/graph of the four perspectives where same_law edges cluster the convergence, blocked_by edges show the standing gates (the operator loop never closed on a real Tim decide — refuted by THREE lanes), and composes_with shows how the decision surface is assembled from all four.
- **what_is_missing_or_blocking:** The harvest files carry the edges in prose; whether each conceptual edge was filed as an actual board edge row (vs. only described in the .md body) needs confirming. No graph view renders the four-lane relation set.
- **what_tim_would_need_to_judge:** Whether the four-lane convergence on "verify the actual thing" is a law he wants to canonize company-wide (the harvests flag this as his framework call), and whether the map's framing matches how he sees the four perspectives relating.
- **confidence:** FACT-adjacent — the four `same_law` edges naming the identical law are directly observable in all four harvest files; the only leap is rendering them as one map. The convergence itself is a traced observation, not an inference.
- **recommended_next_exploration:** reverse_traverse the four harvest board roots for their conceptual edges to confirm the rows exist on the board, then assemble the relation set.

---

### possible-04 — A fabric-queryable registry-discoverability surface (the field-index has no MCP/bridge read)
- **plain_language_possibility:** The system built an index this session that can answer structural questions like "which files declare a role?" or "what imports the storage layer?" — 11,526 of these facts. But right now you can only ask it from the command line. The fabric (the assistant, the surfaces) cannot ask it. Exposing one query tool would let every agent ask the codebase about itself by structure, not just by meaning.
- **technical_basis:** M2 built the field-index as a sibling store (the marks-pattern) with build_field_index + query_field_index — verified by-use: declares=role→32, declares=projection→12, imports~fs_store→168 (exact structural queries semantic search cannot do). Fork's harvest claim-5 explicitly names the missing piece: "an MCP/bridge read-surface for M2's field-index (so the fabric queries it, not just the CLI) is a thin un-built follow."
- **evidence_addresses:** .data/store/code_archaeology/field_index.jsonl (11,526 triples — verified: symbol 3670/distinct 2063 · imports 3115/distinct 291 · kind 2318 · language 2318 · declares 105) · code://company/<all targets> (every triple's target is a code:// address) · fork-HARVEST.md claim-5 UPDATE 2026-06-23
- **related_tools_files:** ops/code_archaeology.py (build_field_index / query_field_index) · .data/store/code_archaeology/field_index.jsonl · runtime/bridge.py + the MCP tool layer (where the read-surface would plug in)
- **why_it_might_matter:** The corpus answers "by meaning" (semantic search); structural questions ("all files that declare a decision," "everything that imports cognition") are exactly what semantic search is bad at and what an agent needs before a build. The index exists and is proven; the fabric just can't reach it.
- **what_it_could_become:** An "ask the codebase its structure" tool alongside corpus(op=query) — declares/imports/symbol/kind/language as first-class query axes the assistant uses to orient before building (the build-from-partial-info killer, made reachable by the fabric, not just the CLI).
- **what_is_missing_or_blocking:** The MCP/bridge read-surface (fork calls it "thin un-built"). The index is a static jsonl snapshot — it goes stale as code changes (no auto-reindex; the freshness daemon is diagnosed-not-built per recollection's NOT-DONE).
- **what_tim_would_need_to_judge:** This is largely a reversible technical call (a read-only query surface) — minimal Tim judgment needed beyond whether structural-query is a capability he wants surfaced to operators vs. agents-only.
- **confidence:** FACT-adjacent — the index exists and is verified-by-use (fact); the missing read-surface is explicitly named by the lane that built it (fact); the only leap is the thin wiring.
- **recommended_next_exploration:** Confirm query_field_index's signature, then expose it as a corpus-sibling MCP op (op=structure or similar) returning targets for a (field,value) pair.

---

### possible-05 — Clean recall landing for the CLEAR-IN backbone (one missing primitive blocks it)
- **plain_language_possibility:** There is a cleaned, verified set of 17,582 memory records ready to become the system's canonical recall — but it can't be switched in cleanly, because the system can only ADD vectors to recall, never remove old ones. 1,276 stale records would survive the swap. One small capability (remove-a-vector) would unblock making the clean memory the real memory.
- **technical_basis:** Recollection's harvest verifies: the CLEAR-IN backbone (.data/store/extractions/extractions-full-cleanin.jsonl, 17,582 records, vi-visual excluded, --sample 40 green: 0 truncation) is BUILT + correct but NOT swapped-canonical. The blocker is verified-by-check: the store has no remove_vector; embed_extractions is incremental-ADD-only; vectors are keyed extraction://<asset>/<chunk_id>. Clean retraction needs EITHER a full ~52k re-embed OR a new store.remove_vector(source_address).
- **evidence_addresses:** .data/store/extractions/extractions-full-cleanin.jsonl (17,582 — recollection PROVENANCE) · extraction://<asset>/<chunk_id> (the vector key namespace, corpus 'extractions' space) · ch-ouui7r0k-recollection-HARVEST.md claims 4 & 5
- **related_tools_files:** runtime/decision_memory.py · store/fs_store.py (where remove_vector would live) · ops/dragnet_extract.py (the extract-once backbone) · the FsStore vector layer
- **why_it_might_matter:** The whole recall-substrate mission's clean memory is one method away from landing; without it, cleaning the source asset does NOT clean what recall actually returns (a verified gap a future build needs).
- **what_it_could_become:** A clean swap to the CLEAR-IN backbone as canonical recall (the no-fiction, Tim-filtered memory), OR a general store.remove_vector(source_address) primitive that makes recall editable/correctable rather than append-only — which generalizes to "the memory can be curated, not just grown."
- **what_is_missing_or_blocking:** The store.remove_vector primitive itself (or a deliberate full ~52k re-embed). The lead's standing guidance: don't half-swap (orphans vectors), don't fire a destructive re-embed in wind-down.
- **what_tim_would_need_to_judge:** Whether recall should be editable (curate-and-remove) vs. strictly append-only-and-re-embed — an architectural-posture call with a memory-integrity dimension he'd want to weigh. Also whether the vi-visual exclusion filter is the right cut.
- **confidence:** FACT-adjacent — the clean artifact is verified-built and the missing primitive is verified-absent by code-check; the possibility is "build the one method, then land it."
- **recommended_next_exploration:** Spec store.remove_vector(source_address) against the FsStore vector layer + confirm whether a scoped removal or a full re-embed is the safer landing.

---

### possible-06 — Every retiring session/channel auto-crystallizes its perspective (the retirement verb generalizes)
- **plain_language_possibility:** The careful "wind-down harvest" the four lanes just did by hand — recollect what I learned, tag every claim honestly, link it, save it into permanent memory before I close — is now a reusable button. It could become the default exit gesture for ANY session or channel, so no perspective is ever lost when a work-stream ends.
- **technical_basis:** cc_retire.py built this session makes the harvest a repeatable verb: harvest_member (a session crystallizes its own perspective, ENFORCING honest-state tags — fail-loud if any claim lacks verified|attempted-unverified|broken|abandoned) and retire_channel (a channel's totality + a coverage check: are all members harvested?). It reuses session_recall + corpus.write_record + cc_board + cc_attachments — no parallel machinery.
- **evidence_addresses:** runtime/cc_retire.py (harvest_member lines 65-91, retire_channel 94-134, harvest_status coverage ledger 50-62) · the four existing harvest records as proof-of-shape (the .md files + their board roots) · attachment_types/ (sessions, board_items, images, docs — what retire_channel gathers)
- **related_tools_files:** runtime/cc_retire.py · runtime/cc_channels.py (members + archive) · runtime/corpus.py · runtime/cc_board.py · the session_recall backbone (skills/session-recall)
- **why_it_might_matter:** The keystone-poisoning lesson (a self-certified fake "done" in permanent memory is the worst outcome) is structurally enforced by this verb. Without it, perspective is lost on every session close and the corpus accumulates unverified "done"s.
- **what_it_could_become:** A standing exit-ritual — every session, on wind-down, fires harvest_member; every channel, on retire, fires retire_channel with a coverage check; the corpus becomes a continuously-enforced honest memory of every perspective the company ever held.
- **what_is_missing_or_blocking:** No automatic trigger wires harvest_member to session end (it's a manually-called verb today). harvest_status's coverage check depends on harvest files naming a handle OR a board item authored_by the handle — a session that harvested into neither would read as "missing" (a heuristic, not a hard truth).
- **what_tim_would_need_to_judge:** Whether retirement should be automatic-on-close vs. an explicit gesture, and what the minimum honest harvest is (is a 1-claim harvest acceptable, or is there a quality bar?). A process/semantic call.
- **confidence:** FACT-adjacent — the verb is built and proven on four real harvests this session; the leap is making it the default trigger.
- **recommended_next_exploration:** Run harvest_status against the provider-registry channel to see the live coverage ledger; identify where a session-end hook could call harvest_member.

---

### possible-07 — Tracked dragnets turn every extraction into operational telemetry the system can learn from
- **plain_language_possibility:** Every time the system reads-and-indexes a folder (a "dragnet"), it now records how it went — how long, how many files, what it skipped and why, what failed. Over time this becomes a body of operational data the system never had: which runs are slow, which inputs fail, how coverage trends. The system could start reasoning about its own processing.
- **technical_basis:** cc_dragnet.py wraps any extractor in a tracked run — telemetry captures started/duration_s · denominator/files_total/processed/failed/retries · throughput_per_s · slowest_file_s · coverage_pct · fail_loud_ok · excluded(+reason). The run-record is ingested into the corpus (queryable) AND attached to the channel (dragnet_runs accumulates run history). This session already produced runs: design-assets has 3 dragnet_runs, design-knowledge has 1.
- **evidence_addresses:** design-assets channel manifest (3 dragnet_runs attached) · design-knowledge channel manifest (1 dragnet_run) · attachment_types/dragnet_runs.py · the dragnet-run corpus kind (kind="dragnet-run" in cc_dragnet.py:178)
- **related_tools_files:** runtime/cc_dragnet.py (the telemetry dict, lines 159-185) · attachment_types/dragnet_runs.py · runtime/corpus.py (write_record) · runtime/cc_attachments.py
- **why_it_might_matter:** Tim's introspective-data-building law (the system records its own operation as a byproduct of use); the dragnet telemetry is exactly that, freshly created, and "we don't have that data yet" was the explicit motivation. It is accumulating but not yet read back.
- **what_it_could_become:** A processing-health surface — query dragnet-run records to see coverage trends, recurring exclusions, slow inputs, failure patterns across channels; the system noticing "this kind of input always fails" or "coverage dropped on this channel."
- **what_is_missing_or_blocking:** No read-back / dashboard queries the dragnet-run records yet (they accumulate, nothing reads them). The dataset is small (a handful of runs so far). The dragnet_runs attachment_type did not list in the live cc_attachments op=types despite the file existing (likely needs a bridge bounce).
- **what_tim_would_need_to_judge:** Whether processing-telemetry is something he wants surfaced (an operator-facing health view vs. an internal substrate), and which signals matter (coverage? failures? cost?). A product-framing call.
- **confidence:** INFERENCE — the telemetry is verified-captured and accumulating (fact: 4 runs attached); a read-back/trend surface over it is a real but unbuilt possibility.
- **recommended_next_exploration:** corpus(op=find, kind="dragnet-run") to read the accumulated runs and see what trend questions the data can already answer.

---

### possible-08 — The capability-verbs layer makes "what can this surface do" registry-resolved, not hardcoded
- **plain_language_possibility:** The registry of what an external platform (like Claude Code) can do already carries, per capability, whether it's readable, searchable, auto-shown on surfaces, or configurable — and a safety posture (safe / consent / locked / hazard). A surface could be generated FROM that, so what an operator can see and do is computed from the registry rather than coded by hand into each screen.
- **technical_basis:** contracts/capability_entry.py defines CapabilityVerbs (readable / searchable / projectable / configurable, all default-True "expose-not-gate") and a DERIVED posture (locked/hazard/consent/safe/unmatched) with an auditable posture_rule. The cap:// resolver is referenced across runtime/minds.py, bridge.py, suite.py, cognition.py, contracts/address.py, introspection/registry.py — it is a live, wired registry, not a sketch.
- **evidence_addresses:** contracts/capability_entry.py (CapabilityVerbs lines 41-50, posture lines 85-89) · cap:// references in runtime/minds.py, runtime/bridge.py, runtime/suite.py, runtime/cognition.py, contracts/address.py, introspection/registry.py · tests/cap_wire_acceptance.py · the cap:// capability registry named in the prompt inventory
- **related_tools_files:** contracts/capability_entry.py · introspection/registry.py · introspection/engine.py · tests/cap_wire_acceptance.py · contracts/address.py (cap:// parse)
- **why_it_might_matter:** Tim's everything-is-a-variable / from-registry-never-bespoke law; the projectable verb literally says "auto-projected to MCP/bridge faces." The affordance exists in the contract but a surface that projects FROM the verbs is the latent piece.
- **what_it_could_become:** A registry-driven capability surface — an operator view where each action's availability (and its safety posture, with the teaching-refusal text for locked ones) is resolved from the cap registry, so adding/changing a capability changes the surface with no surface code edit.
- **what_is_missing_or_blocking:** Whether the projectable verb is actually consumed by a face today (the contract declares it; a face that reads it to render is the unverified piece). The posture classifier R1-R5 rules and their live application would need confirming.
- **what_tim_would_need_to_judge:** What an operator should be allowed to see/do vs. what stays agent-only, and how the locked/hazard postures should feel when surfaced (teaching-refusal text is his voice). A product + safety-posture call.
- **confidence:** INFERENCE — the verbs/posture layer demonstrably exists in the wired contract (fact); a surface generated from it is a real but unverified-as-consumed possibility.
- **recommended_next_exploration:** Trace whether any current face reads CapabilityVerbs.projectable to render; if not, that is the precise latent affordance to surface.

---

### possible-09 — Hidden-coupling and duplication detection from the imports/symbol index (the marks that exist for it)
- **plain_language_possibility:** The structural index now knows what every file imports (291 distinct import targets) and what symbols exist (2,063 distinct). The system also already has mark-types for "this was built twice" and "these overlap." Combining them, the system could surface where two files do the same thing, or where one module is a hidden hub everything depends on — without anyone manually auditing.
- **technical_basis:** The field-index holds imports (3,115 edges, 291 distinct targets — e.g. imports~fs_store→168) and symbol (3,670, 2,063 distinct). The mark-type registry already declares built_twice, overlap, contradiction, strain — the exact vocabulary for flagging duplication/coupling/tension. The two are unconnected: the index is structural data; the marks are a flagging layer.
- **evidence_addresses:** .data/store/code_archaeology/field_index.jsonl (imports + symbol triples) · code://company/mark_types/built_twice.py · code://company/mark_types/overlap.py · code://company/mark_types/contradiction.py · code://company/mark_types/strain.py
- **related_tools_files:** ops/code_archaeology.py (build_field_index) · mark_types/built_twice.py · mark_types/overlap.py · runtime/mark.py (the marking seam)
- **why_it_might_matter:** The critical-perspective guardrail in Tim's green-light asks for surfacing "hidden coupling, apparent duplication" — the data to compute both (import fan-in, symbol-name collisions) now exists, and the marks to record findings exist; nothing connects them.
- **what_it_could_become:** A coupling/duplication pass that reads the index, flags high-fan-in hubs (fs_store at 168 imports = a structural hub) and same-symbol-different-file candidates, and records each as a built_twice/overlap mark — surfacing tensions for Tim-guided synthesis without opinionated deletion.
- **what_is_missing_or_blocking:** The analysis that joins imports/symbol data to candidate findings is unbuilt. Symbol-name collision is a heuristic (same name ≠ same behavior) — it surfaces candidates, not proof. The index is a static snapshot (staleness caveat from possible-04).
- **what_tim_would_need_to_judge:** Which couplings/duplications are intentional vs. accidental — the green-light is explicit that critical means surfacing for HIS synthesis, never autonomous deletion/ranking. The judgment of "is this duplication a problem" is his.
- **confidence:** INFERENCE — the structural data and the mark vocabulary both demonstrably exist (fact); the join that produces findings is unbuilt, and the findings are candidates not proofs.
- **recommended_next_exploration:** Compute import fan-in from the index (a non-opinionated descriptive pass) and list the top hubs + the same-symbol-multiple-files candidates as a flat surfacing record.

---

### possible-10 — The corpus is queryable across spaces; a cross-space "ask the company about itself" is reachable
- **plain_language_possibility:** The company's memory is no longer one pile — it has distinct named spaces (the codebase map, the transcript extractions, the recall substrate). With the design system and the code map both now embedded, a single question could be asked across all of them at once: "what do we know about X" pulling from code, design, conversations, and decisions together.
- **technical_basis:** corpus(op=query) takes a `space` parameter (cognition_info().spaces lists them); the code_archaeology space is registered and embedded (2,041 records), the extractions space holds the recall substrate, and the transcript chroma is a separate layer (35,904 — recollection clarified it's a genuinely separate substrate-mcp layer, not stale). A single-layer-pplx + rerank base is the projection-endorsed proven retrieval (per the corpus tool's own doc).
- **evidence_addresses:** the code_archaeology registered space (fork claim-5: 2,041 records embedded) · the extractions space (recollection: 52,875 FsStore) · the transcript chroma (35,904, collection vault_claude-sessions — recollection claim-6 verified by-check) · corpus tool space param + rerank pass (corpus op=query schema)
- **related_tools_files:** runtime/corpus.py · runtime/cognition.py (embed_corpus_to_spaces, the registered-Projection requirement at cognition.py:522 per fork) · ops/rerank.py (:8008 jina-v3 precision pass)
- **why_it_might_matter:** The spaces exist and are individually queryable, but a question today targets one space; a cross-space synthesis ("what does the company know about the decision surface, across code + transcripts + design") is the latent affordance the multiple-registered-spaces makes reachable.
- **what_it_could_become:** A unified "ask the company about itself" that fans a question across registered spaces and fuses the results (the MULTI-LAYER-CONSULT direction fork references) — code, conversation, design, and recall answering together.
- **what_is_missing_or_blocking:** Cross-layer fusion is explicitly flagged as beyond the proven base (the corpus doc: "single-layer-pplx + rerank is the proven base BEFORE any cross-layer fusion"). The three layers have different embedding models/scales (the floor-calibration lesson — comparing across scales is the documented trap). The freshness daemon is unbuilt (staleness).
- **what_tim_would_need_to_judge:** Whether cross-space synthesis is worth the fusion complexity vs. keeping spaces queried separately, and how to present provenance when an answer spans layers (which layer said what). A product + correctness-posture call.
- **confidence:** INFERENCE — the individual spaces are verified-registered-and-queryable (fact); cross-space fusion is explicitly named as unproven and beyond the current base.
- **recommended_next_exploration:** cognition_info() to enumerate the registered spaces, then test the same question against code_archaeology vs. extractions separately to see how divergent the scales/answers are before any fusion.

---

### possible-11 — Image annotation threads become a grounded visual-decision record (the V can explain an image)
- **plain_language_possibility:** Because an image can now carry a comment thread pinned to its address, and the assistant (the V) can already explain a decision card grounded in real sources, the same grounded-explain could be pointed at an image — "why this design?" answered from the annotation thread + the design corpus, not invented.
- **technical_basis:** Threaded annotation on addressed content was built this session (board items linked commented_on/reply_to an image address — the comment/note/reply edges). The L1 grounded-explain mechanism is verified-by-sight on decision cards (projection claim-4) and streams from a grounded source. An image address is just another addressed target the same explain-wire could ground against.
- **evidence_addresses:** board_edges/commented_on.py · board_edges/reply_to.py · image://design-source/* (the annotatable targets) · projection-HARVEST.md claim-4 (L1 grounded-explain verified streaming) · the commit 4915587 (version axis + threaded annotation)
- **related_tools_files:** runtime/cc_images.py · board_edges/commented_on.py · board_edges/reply_to.py · surface/app/src/lib/groundedExplain (the L1 wire) · roles/explain_role.py
- **why_it_might_matter:** The explain-wire is verified for decisions; pointing it at visual artifacts is a near-reuse, and visual decisions (design choices) are exactly the kind Tim makes by recognition. Today an image's "why" lives only in scattered annotations.
- **what_it_could_become:** A "why this image" grounded explanation — the V reads the image's annotation thread + design corpus and explains the visual decision grounded, with the same AI-inference-flagging the decision card uses.
- **what_is_missing_or_blocking:** explain_role grounds against the recall/decision substrate, not against an image's annotation thread — the retrieval would need to include the image's comment edges as grounding context (unbuilt). The L1 wire itself is "re-verify post-reboot, don't trust old green" per the harvests.
- **what_tim_would_need_to_judge:** Whether visual artifacts deserve the same grounded-explain treatment as decisions, and what counts as the "ground" for an image (its annotations? its design-corpus lineage? both?). A semantic/product call.
- **confidence:** SPECULATIVE-POSSIBILITY — the image-annotation layer and the explain-wire both exist (fact), but grounding explain against image annotations is unbuilt AND the explain-wire's post-reboot state is itself unverified; the connection is thin.
- **recommended_next_exploration:** Confirm whether explain_role's retrieval can take an arbitrary addressed target's edges as grounding; if not, that adapter is the missing piece.

---

### possible-12 — Coverage-complete dragnets over OTHER repos/inputs (the primitive is repo-agnostic)
- **plain_language_possibility:** The "read-and-map-everything" capability was just proven on the company's own codebase AND on the design system folder. It's not company-specific — it could be pointed at any folder or repo (a reference project, an external SDK, the Vi codebase) to produce the same coverage-complete, queryable map before building against it.
- **technical_basis:** code_archaeology.enumerate_files takes a `repo` argument and walks any real tree; run_dragnet takes `input_dir` and resolves all output addresses from it (variable-resolution-from-input). It was proven on TWO different inputs this session (the company repo: 2,052/2,052 at 100%; counterpart/design: 859 processed + 721 excluded-with-reason). The ingest_batch seam lets the 32-way cascade plug into any input.
- **evidence_addresses:** ops/code_archaeology.py (enumerate_files(repo=...) line 70) · runtime/cc_dragnet.py (run_dragnet(input_dir=...) line 76) · fork-HARVEST.md claim-5 (both repos proven) · design-knowledge channel (the second-repo run, attached)
- **related_tools_files:** ops/code_archaeology.py · runtime/cc_dragnet.py · contracts/address.py (the <scheme>://<channel>/<rel> resolution)
- **why_it_might_matter:** The build-from-partial-info failure isn't unique to the company repo — it's worst when building against an unfamiliar external surface (the live-docs-over-stale-local rule exists because of this). A coverage-complete map of an external input is the same fix applied wider.
- **what_is_missing_or_blocking:** Each new input needs a registered Projection/space to embed into (embed_corpus_to_spaces fails loud otherwise — fork's verified mechanism note). The per-record LLM prose cost scales with file count (the design run was 859 files). Cross-repo addressing conventions (which channel an external repo's map attaches to) need deciding.
- **what_it_could_become:** A standing "map this input before we build against it" verb usable on any reference repo, SDK source, or sibling project — each becoming a queryable space with tracked-run telemetry.
- **what_tim_would_need_to_judge:** Which external inputs are worth mapping (a product/priority call on where the build-from-partial-info risk is highest), and whether external-repo maps live in the company corpus or stay separate. A scope/semantic call.
- **confidence:** FACT-adjacent — the primitive is verified repo-agnostic by running on two distinct inputs this session; the leap is pointing it at a third, plus registering the space.
- **recommended_next_exploration:** Identify one high-risk external input (e.g. an SDK the company builds against) and confirm what space/channel its map would attach to before running.

---

**Summary of confidence labels (counted after writing — 12 possibles):**
- FACT-adjacent: 5 — possibles 03 (cross-perspective map / four-lane same_law convergence), 04 (field-index read-surface), 05 (CLEAR-IN landing), 06 (retirement verb), 12 (repo-agnostic dragnet).
- INFERENCE: 6 — possibles 01 (comparison workshop), 02 (generative design loop), 07 (dragnet telemetry read-back), 08 (capability-verbs surface), 09 (coupling/duplication detection), 10 (cross-space query).
- SPECULATIVE-POSSIBILITY: 1 — possible 11 (grounded-explain over images).

Discipline note: every possible traces to an observed address/file/record; the `confidence` field labels the BASIS, not the possibility (no possibility is asserted as fact). Flat list, no ranking. Gap content lives in `what_is_missing_or_blocking`. No "should."
