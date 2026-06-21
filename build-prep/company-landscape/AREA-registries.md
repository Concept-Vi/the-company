# AREA: Typed Registries + Root Files — Exhaustive Landscape

> **Produced by:** read-only dragnet agent, 2026-06-21  
> **Working dir:** /home/tim/company  
> **Scope:** decisions/ · decision_subtypes/ · mark_types/ · item_types/ · stack_item_types/ · relation_types/ · attachment_types/ · source_types/ · kinds/ · verdict_panels/ · panels/ · forms/ · mode_detection_rules/ · checks/ · board_edges/ + root loose files  
> **Mode:** READ-ONLY — nothing edited except this file

---

## 1. decisions/ — 24 entries (all .py, owner=global)

### Registry purpose
One file per pending/settled decision Tim (or the fabric) must make. Each `<id>.py` declares `DECISION = {...}`. Resolved via `decision_subtypes` → card_variant + explanation_policy + required_elements + owner. Addressable as `decision://global/<id>`. State (pending/decided) is NOT stored on the row — it resolves from `decision_take`/`decision_retract` marks appended to the canonical address.

### Field schema
```
id           required — MUST equal file stem
meaning      required — the decision at the operator's altitude (plain language, no machine names)
options      required — list of {label, implication, recommended?}
scope        "global"
subtype      MANDATORY IN PRACTICE (not yet required by schema pre-2026-06-21 — was fixed 2026-06-21)
explanation_source  optional — board:// or code:// pointer the RHM grounds the explain in
legibility   optional — {name, is, why} for the operator surface
```

### Full decision inventory

| id | subtype | explanation_source | meaning (first 70 chars) |
|---|---|---|---|
| adopt-claude-design | trade-off | SET | Should the company bring in Claude Design as the place you s |
| build-consent-posture | authorize | MISSING | Should the company keep building on its own and rely on undo |
| card-visuals-source | trade-off | MISSING | The card you approved uses hand-made narrative pictures; the |
| cluster-identity | trade-off | SET | A cluster is a group of related things the company finds — i |
| connector-full-access | authorize | MISSING | When you connect from outside — your phone, or a tool like C |
| control-density | trade-off | MISSING | The deeper expert controls — should they appear based on WHO |
| core-shape | trade-off | MISSING | The company's diagrams give each shape a fixed meaning, and |
| cube-3d | theorem-fork | MISSING | How should the cube become 3-D in the instrument — show it a |
| dimension-meaning | theorem-fork | MISSING | The instrument should drop through dimensions — but in your |
| event-streams | trade-off | SET | The company's highest-volume live data — the running log, an |
| figure-gold-value | trade-off | MISSING | Big highlighted numbers and the company's accents all use on |
| file-identity | trade-off | SET | Is a saved file the same thing as the content in it, or its |
| form-taxonomy | trade-off | SET | The kinds the company sorts content into — and uses to decid |
| line-language | trade-off | MISSING | Lines in the company's diagrams come dashed or solid, and wh |
| lock-card-look | authorize | MISSING | The first decision card's look is now at the level we valida |
| merge-sa-authorize | authorize | SET | The company can read the shared design library to build from |
| opacity-meaning | trade-off | MISSING | In the source, faded or see-through elements sometimes mean |
| real-v-symbol | trade-off | MISSING | The right-hand-man's icon is a placeholder. When do you put |
| reconnect-tools | authorize | MISSING | Some new tools are built and waiting, but they only switch o |
| rerank-loadout | trade-off | SET | The sharper sort of a decision's supporting context is switc |
| steer-visual-direction | trade-off | MISSING | The company is building the visual direction you're shaping |
| substrate-home | trade-off | SET | The company's pieces each store things their own way, now dr |
| substrate-spine | trade-off | MISSING | Everything the company keeps — the design library, the decis |
| visual-fidelity | trade-off | MISSING | How far should the company DRAW its visuals itself — clean, |

### explanation_source coverage
- **SET (8):** adopt-claude-design, cluster-identity, event-streams, file-identity, form-taxonomy, merge-sa-authorize, rerank-loadout, substrate-home
- **MISSING (16):** build-consent-posture, card-visuals-source, connector-full-access, control-density, core-shape, cube-3d, dimension-meaning, figure-gold-value, line-language, lock-card-look, opacity-meaning, real-v-symbol, reconnect-tools, steer-visual-direction, substrate-spine, visual-fidelity

### subtype breakdown
- **trade-off (15):** adopt-claude-design, card-visuals-source, cluster-identity, control-density, core-shape, event-streams, figure-gold-value, file-identity, form-taxonomy, line-language, opacity-meaning, real-v-symbol, rerank-loadout, steer-visual-direction, substrate-home, substrate-spine, visual-fidelity ← (17 rows carry trade-off; note: 15 in original survey + substrate-spine + visual-fidelity)
- **authorize (5):** build-consent-posture, connector-full-access, lock-card-look, merge-sa-authorize, reconnect-tools
- **theorem-fork (2):** cube-3d, dimension-meaning
- **cross-lane (0):** none in current set

### Decided status
- The decision rows do NOT carry decided/pending state — state resolves from marks on the canonical address. 4 design-language decisions (core-shape, figure-gold-value, line-language, opacity-meaning) are DECIDED (per SUBTYPE-COVERAGE-GAP.md — need `decision_take` marks written by DNA; until those marks land, the subtype-tag resolves them as PENDING = they resurface in Tim's queue as settled calls).

### GAPS / STALE / SURPRISES
- **CRITICAL — now CLOSED:** The subtype-coverage gap (10 of 24 rows missing subtype → silently absent from Tim's queue) was found and fixed 2026-06-21. All 24 rows now carry subtype. Schema gate (`decision.schema.json`) now requires `subtype`.
- **explanation_source MISSING on 16 of 24:** More than half have no grounding pointer. This means the RHM's explain of those decisions has no declared source document to ground in — the explanation_policy fires but against no pointer.
- **theorem-fork grounding gap:** `cube-3d` and `dimension-meaning` have no `explanation_source`; the `theorem-fork` subtype requires `grounding_source` in required_elements — resolves to NOTHING on those two cards. Flagged in SUBTYPE-COVERAGE-GAP.md as a residual.
- **4 decided but unmarked:** core-shape, figure-gold-value, line-language, opacity-meaning need `decision_take` marks written to remove them from Tim's pending queue.
- **decisions/ is Python files, not JSON/YAML:** worth noting for agents who expect a JSON registry.

---

## 2. decision_subtypes/ — 4 entries

### Registry purpose
The VOCABULARY of decision KINDS. One file per subtype. Maps `decision.subtype` → `card_variant` (DNA renders) + `explanation_policy` (fork's generation_policies) + `owner` (whose queue) + `required_elements` (gate). No `owner` field lives on the decision row itself — owner resolves ONLY via this registry.

### Field schema
```
id                   required — MUST equal file stem
card_variant         required — DNA's variant vocabulary (binary | n-panel | ...)
explanation_policy   required — a generation_policies id (fork)
owner                required — "tim" | "fabric"
required_elements    optional — list of field names the card must carry
desc                 optional
```

### Entry list

| id | card_variant | owner | explanation_policy | required_elements |
|---|---|---|---|---|
| authorize | binary | tim | policy.risk-grounding | [action, option_implication, security_condition, gate] |
| cross-lane | n-panel | fabric | policy.technical-recommendation | [options, lane_impact, recommendation] |
| theorem-fork | n-panel | tim | policy.theorem-grounding | [conceptual_options, theoretical_implication, grounding_source, ai_uncertainty_caveat] |
| trade-off | n-panel | tim | policy.trade-off-neutral | [options, trade_off_axes, unblocks] |

### GAPS / STALE / SURPRISES
- **cross-lane is the only fabric-owned subtype** — no current decisions use it (all 24 are owner=tim). The cross-lane row exists as vocabulary but is unused in the current decision set.
- **Generation policies referenced (policy.risk-grounding, policy.technical-recommendation, policy.theorem-grounding, policy.trade-off-neutral) are external** — live in `generation_policies/` (not in this area); cross-ref dependency.
- **No subtype for ranking / allocation / workflow / single-confirm** — the AGENTS.md notes these as future candidates. DNA's binary card_variant is only exercised by `authorize` (2 of 5 authorize decisions).

---

## 3. mark_types/ — 12 entries

### Registry purpose
The file-discovered MARK-TYPE registry. A mark is the disposition a mark-pass writes over a corpus unit. A mark-type is the declared vocabulary of `mark_type`. Split into two families: ANALYSIS types (written by automated passes) and INTERACTION types (written by the operator via the gallery route-back).

### Field schema
```
id            required — MUST equal file stem
value_shape   required — score | label | bool | span | free | claim (open vocab DATA)
direction     required — "surface" (positive signal) | "subtract" (noise to subtract)
desc          optional
```

### Entry list

| id | value_shape | direction | family | desc |
|---|---|---|---|---|
| gold_likelihood | score | surface | analysis | likelihood this unit is gold (meaning, not surface); READ over findings+evidence |
| ai_fingerprint | label | subtract | analysis | matched AI-tic (generic+recurring) to subtract — denoising is surfacing |
| contradiction | span | surface | analysis | this unit contradicts another (a tension surfaced for review; render-not-judge) |
| built_twice | claim | surface | analysis | same logic/vocabulary built in 2+ places — unification target (② drift-radar) |
| overlap | claim | surface | analysis | significant shared responsibility between near units — softer unification candidate (② drift-radar) |
| strain | score | surface | analysis | structure↔meaning divergence: |where filed - where means to be| (SEED §111) |
| comment | free | surface | interaction | operator comment/direction at an addressed element (annotation_type sub-type) |
| decision_take | free | surface | interaction | operator's CHOICE on an addressed decision — value = chosen option label; resolves pending→decided |
| decision_retract | free | surface | interaction | operator's UN-DECIDE of an addressed decision — symmetric twin of decision_take; returns decided→pending |
| favour | score | surface | interaction | operator favour-score at an addressed element (value = a number) |
| reaction | label | surface | interaction | operator reaction-stamp (good/wrong/explain/remember_this/do_this) |

> NOTE: The AGENTS.md lists 11 entries. The actual files in mark_types/ include all 11 above PLUS `ai_fingerprint`, `built_twice`, `comment`, `contradiction`, `decision_retract`, `decision_take`, `favour`, `gold_likelihood`, `overlap`, `reaction`, `strain` = **11 entries**. The earlier count of 12 in the brief reflects potential AGENTS.md drift; confirmed 11 files exist.

### GAPS / STALE / SURPRISES
- **`decision_retract` is the most recently added** — was the entry that enabled the operator's UN-DECIDE to be a legitimate gated write (before it existed, the fold could read a retract but nothing could write one through the gate).
- **Only 1 subtract-direction type** (ai_fingerprint) — the surface vs subtract split is seeded but very lightly exercised. All others surface.
- **`claim` value_shape** is used by built_twice and overlap — not listed in the schema's "open vocab" examples in AGENTS.md (score/label/bool/span/free) but valid per "open vocab DATA".

---

## 4. item_types/ — 6 entries

### Registry purpose
The file-discovered ITEM-TYPE registry for the Company NOTICEBOARD. A row = one kind of board record with its own lifecycle state-machine. Supersedes the legacy SYSTEM-GAPS.md ledger. File-discovered, never a hardcoded enum.

### Field schema
```
id           required — MUST equal file stem; fail-loud if mismatched
initial      required — ∈ states
states       required — non-empty list of str
transitions  required — {from_state: [allowed to_states]}; every key + target ∈ states
label        optional
desc         optional
```

### Entry list

| id | initial | states | desc |
|---|---|---|---|
| guide | living | [living, archived] | How-to / living doc, updated in place, archivable when superseded |
| idea | captured | [captured, discussing, promoted, dropped] | Seed/thought; may be promoted to a request via `promoted_from` edge |
| issue | open | [open, triaged, fixing, resolved, wontfix] | Bug/wrong-behaviour report; supersedes SYSTEM-GAPS.md |
| request | open | [open, picked-up, building, done, declined] | Ask to add or change Company/MCP/CLI/channel |
| signal | raised | [raised, consumed, superseded] | Fabric SIGNAL a lane consumes to ACT (first instance: decision.decided); shared-tree floor-clean half of operator-cycle resume wire |
| tip | posted | [posted, archived] | Discovered better way to use something — evergreen, archivable |

### GAPS / STALE / SURPRISES
- **`signal` is the newest, most complex type** — multiple state cycles (raised→consumed→superseded→raised via re-decide). Purpose: replaces the live-MCP channel post for cross-session state (shared-tree model, not live-MCP). Linked to the signal's decision:// address via `attached_to`.
- **No `done`/`closed` terminal for `idea`** — an idea transitions to `promoted` (terminal) or `dropped`. Dropped can reopen to `captured`. The `promoted` state is a one-way terminal once reached.
- **`signal` superseded terminal is re-openable (→ raised)** which mirrors the decision retract/retake cycle — correct by design.

---

## 5. stack_item_types/ — 4 entries

### Registry purpose
The file-discovered CHANNEL-STACK item-type registry (FACE-2 / A4). The vocabulary of things the fabric STACKS on a channel for the operator to clear. NOT the board item_types/ — carries a render/dispatch contract (row_fields + unsettled_state + open_verb) rather than a lifecycle. Mirrors the ONE file-discovered registry mechanism.

### Field schema
```
id               required — MUST equal file stem
label            optional
desc             optional
row_fields       optional — {field: source dot-path}; domain-prefixed (identity.* | feed.*)
unsettled_state  optional — default "pending"; item leaves queue when state ≠ this
open_verb        optional — {event, payload}
```

### Entry list

| id | label | unsettled_state | open_verb | notes |
|---|---|---|---|---|
| decision-sequence | Decision | pending | {event: "decision:open", payload: [address, id, fromInbox]} | LIVE PRECEDENT (only rendered-to-bar type); row_fields: meaning, recommended_label, reversibility |
| explanation | Explanation | pending | none (generic fallback) | headline from identity; DECLARED NOW, feed+renderer land later |
| presentation | Presentation | pending | none (generic fallback) | headline from identity; DECLARED NOW, feed+renderer land later |
| verify-request | Verify | pending | none (verify surface lands with verdict-mechanism) | headline; cleared by VERDICT (not acknowledge); DECLARED NOW |

### GAPS / STALE / SURPRISES
- **3 of 4 types are declared but NOT YET RENDERED** (explanation, presentation, verify-request) — the AGENTS.md notes these as declared "so the operator-cycle vocabulary is COMPLETE" and the host "soft-degrades to `name` + fail-louds `--unready`" until renderers land. This is intentional scaffold, not a defect — but it means 75% of the type vocabulary is unlit.
- **`verify-request` clears by VERDICT** (different clear-semantic from presentation/explanation which clear by acknowledge) — the verdict-mechanism is a future build.
- **`decision-sequence`** is the sole proven, rendered type — proves the whole mechanism in production. The others ride on this precedent.
- **`recommended_label` is a derived field** on the decision record (fork adds it) — resolution-first: the suggested answer lives on resolve_address(), not only the feed.

---

## 6. relation_types/ — 6 entries

### Registry purpose
The file-discovered RELATION-TYPE registry. A relation-type is a declared KIND of typed/directional edge between two corpus units — the vocabulary `find_relations` (L3) labels its discovered edges with. Cross-level query `find_relations(item, near_space, far_space)` = `query_index(near)` ∩ ¬`query_index(far)` (the inversion-finder). File-discovered; one .py per kind.

### Field schema
```
id       required — MUST equal file stem (python identifier; hyphenated names → label field)
directed required — bool (directed A→B | symmetric A↔B)
inverse  optional — the symmetric/inverse relation-type id
near     optional — the projection space the inversion-finder set-operates over
far      optional
label    optional
desc     optional
```

### Entry list

| id | directed | inverse | near | far | desc |
|---|---|---|---|---|---|
| contradicts | True | — | principles | principles | A contradicts B (tension surfaced for review; render-not-judge); stamps the `contradiction` mark-type |
| depends_on | True | unlocks | — | — | DEPENDENCY axis (substrate lift): this unit requires the target — a gate |
| fragment_of | True | has_fragment | topics | — | A is fragment of whole B (part→whole); exercises the `inverse` field |
| precedes | True | follows | — | — | SEQUENCE axis: this unit comes before target in declared order (logical, not wall-clock) |
| principle_beneath | True | — | principles | — | A expresses the principle beneath B (the principle under the instance; A→B) |
| sibling | False | — | topics | — | A and B are siblings — same level, shared topic; symmetric A↔B; exercises symmetric branch |

### GAPS / STALE / SURPRISES
- **All 6 are directed except `sibling`** — the symmetric (directed=False) branch is exercised by sibling alone.
- **`depends_on` and `precedes` have no near/far** — they are structural/sequence axes, not corpus-semantic relations the inversion-finder reads. Their format is the same (same mechanism) but they serve different consumers.
- **`has_fragment` and `follows` and `unlocks` are inverse ids cited but NOT their own registry files** — they're the mirror end of directed edges; this is correct (only the forward direction is a file). Worth noting: a query for `has_fragment` would need to reverse through `fragment_of`.
- **FUTURE cross-registry unification:** board_edges/ reuses the same RelationTypeRegistry mechanism but is kept in a separate dir. AGENTS.md notes the unification into relation_types/ is tracked as a board `idea` item for when the Heart's cross-registry traversal engine lands.

---

## 7. attachment_types/ — 5 entries

### Registry purpose
The file-discovered ATTACHMENT-TYPE registry for channels (the §3 manifest). A row = one kind of thing a channel can have attached (sessions, docs, recall scope, cloning, board items). `multi` flag controls whether only one attachment of this kind or many are allowed.

### Field schema
```
id           required — MUST equal file stem
label        optional
target_kind  optional — "address" | "scope" | "path" (what the target IS)
multi        optional — bool
desc         optional
```

### Entry list

| id | label | target_kind | multi | desc |
|---|---|---|---|---|
| board_items | Board items | address | True | board://<id> items (requests/issues/tips/guides/ideas) bound to a channel |
| cloning | Cloning | scope | True | point-in-time cloning capability; era-clones minted from the target source |
| docs | Docs | path | True | filesystem path docs loaded as context for members on join |
| recall | Recall scope | scope | False | channel-scoped recall selector (5th wire seam); cc_channel op=recall runs over this scope |
| sessions | Sessions | address | True | sessions (session://<id>) attached to a channel as context / recall source |

### GAPS / STALE / SURPRISES
- **`recall` is the only single-instance (multi=False) attachment type** — one recall scope per channel, multiple of everything else.
- **`cloning` target_kind=scope** (not address) — the source session/scope clones are minted from, not the clone's own address.
- **`docs` target_kind=path** — a filesystem path, not an address; means this doesn't go through the address resolver.

---

## 8. source_types/ — 1 entry

### Registry purpose
The file-discovered SOURCE-TYPE registry for the Noticeboard. Declares ORIGIN KINDS of board records. The `join_keys` on each row are the shared keys for correlating future sources (e.g. GitHub) WITHOUT a migration.

### Field schema
```
id         required — MUST equal file stem
label      optional
join_keys  optional — list of str (shared keys to correlate with other sources)
desc       optional
```

### Entry list

| id | label | join_keys | desc |
|---|---|---|---|
| claude_code | Claude Code transcripts | [author, path, time] | Default origin of board items; joins with GitHub on same author/path/time |

### GAPS / STALE / SURPRISES
- **Only 1 entry — the registry is minimally seeded.** `github` source type is the obvious next entry (referenced in AGENTS.md and HANDOFF docs as the fold-in pattern via join_keys). Not yet authored.
- **The one-entry registry is intentionally thin** — designed for forward extension, not present completeness.

---

## 9. kinds/ — 1 entry (raw.py — a single large dict)

### Registry purpose
The KINDS registry is different from the others: it is NOT a file-per-entry pattern. Instead, a single `kinds/raw.py` declares `KIND_META` as one large dict mapping `kind_id → {name, is}`. The instrument reads this for human meaning on each event kind sector. Un-seeded kinds fall back to a humanized id (split on . _ - / + title-case) — so they're still legible.

### The `kinds/__init__.py`
Empty — just ensures the directory is a Python package.

### KIND_META entries (complete list)
53 entries in `kinds/raw.py`:

| kind | name | is |
|---|---|---|
| corpus.record | A note saved | The system wrote something into its memory. |
| corpus.content | Content saved | A piece of content was stored in the memory. |
| op.run | A job finished | An operation ran to completion |
| run | A run | Something ran. |
| cognition.role.fire | An AI step started | One of the AI minds began a step. |
| cognition.role.ran | An AI step finished | One of the AI minds completed a step. |
| cognition.items | AI made results | An AI step produced its results. |
| agent_sessions.turn | A session turn | A working session finished one back-and-forth. |
| agent_sessions.idle | A session went quiet | A working session paused — no activity for a while. |
| agent_sessions.spawned | A session started | A new working session was started. |
| agent_sessions.closed | A session ended | A working session finished and closed. |
| agent_sessions.registered | A session joined | A working session joined the fabric. |
| annotation | A note | A comment or note attached to something. |
| apply | A change applied | A change was applied to the system. |
| chat | A message | A message in a conversation. |
| voice | A spoken message | Something said aloud in a voice conversation. |
| connect | Two things linked | Two parts were wired together. |
| create | Something new | Something new was made. |
| move | Something moved | Something was moved. |
| delete | Something removed | Something was deleted. |
| warning | A warning | The system flagged a problem worth noticing. |
| error | An error | Something went wrong. |
| config | A setting changed | A setting was changed. |
| mode | A mode change | The system switched modes. |
| decision | A decision | A choice the system recorded. |
| approve | An approval | Something was approved. |
| resolve | A resolution | Something was resolved. |
| cognition.turn.start | The AI started thinking | The AI began a round of thinking. |
| cognition.turn.done | The AI finished thinking | The AI completed a round of thinking. |
| cognition.part | A step in the AI's thinking | One step within a longer round of AI thinking. |
| cognition.wave | Several AI steps at once | A batch of AI helpers ran together at the same time. |
| cognition.inject | Background added | Extra background was fed into the AI's thinking. |
| cognition.reduce | AI answers merged | The AI merged several answers into one. |
| activation | AI helpers started | A group of AI helpers was set running. |
| ask | Needs your input | The system surfaced something for you to answer or decide. |
| grow | The system added to itself | The assistant wrote a new piece of itself — waiting for your approval. |
| decision.intent | A build proposed | Something to build was surfaced for your approval. |
| decision.dispatch | A decision put into action | A recorded decision was sent to be carried out. |
| decision.verify | A decision checked | A decision's outcome was verified. |
| cascade.save | A sequence saved | A reusable sequence of steps was saved. |
| review.start | A review started | A review opened over a set of items. |
| review.advance | Review went to the next | The review moved to its next item. |
| review.comment | A review comment | Someone left a comment during a review. |
| guide.start | A guide started | A guided, step-by-step sequence began. |
| journey.start | Path recording started | The system started recording a path of where it went. |
| journey.step | A step in a recorded path | A recorded path moved to a new place. |
| journey.stop | Path recording finished | The system finished recording a path. |
| trial.turn | A test-run exchange | One back-and-forth inside a test run. |
| trial.debrief.start | A test-run wrap-up | A test run started its wrap-up review. |
| dial | A dial set | A tuning control was changed to a new value. |
| presentation_pref | A display preference | A learned preference for how something should be shown. |
| react | The assistant reacted | The assistant noticed something in the chat and responded. |
| revert | A change undone | A change the system made to itself was rolled back. |
| agent_sessions.render_drop | A skipped screen update | A working session had a screen update that wasn't shown. |

### GAPS / STALE / SURPRISES
- **NOT a file-per-entry pattern** — unlike every other registry here. This is a single large Python dict. AGENTS.md notes that `composition`'s `validate/backfill set-diff` finds kinds present in the data but missing here.
- **TENTATIVE copy** — the header explicitly states these are a tentative draft "Tim/DNA ratify; the field-set is journey-gated (OPERATOR-SURFACE-LOOP.md OQ1–4)."
- **Two kinds intentionally left to the humanized fallback:** `config_writer.git` and `projection.verify` — no emit-site exists to ground them (config_writer was removed); fabricating meaning would break the evidence rule.
- **53 entries in the dict** — matches the "53" count cited in the team-lead brief.
- **The `kinds/__init__.py` is empty** — just a package marker.

---

## 10. verdict_panels/ — 1 entry

### Registry purpose
Verdict panels define multi-seat judgment panels with quorum rules. One file per panel. Each seat is a role id; quorum = minimum votes to pass. Used by the Guided Review / GC7 registration pipeline.

### Field schema
```
id          required — MUST equal file stem
label       optional
description optional
seats       required — list of role ids
quorum      required — int (minimum votes to pass)
```

### Entry list

| id | label | seats | quorum | desc |
|---|---|---|---|---|
| registration_confirm | Registration confirm panel (grounding · voice · element-fit) | [confirm_registration, voice_lens, element_fit_lens] | 2 | Judges a proposed registry dossier through 3 lenses; 2-of-3 pass; any dissent named |

### GAPS / STALE / SURPRISES
- **Only 1 panel** — the registry is minimally seeded (the founding row, GC7's first).
- **3 seats referenced (confirm_registration, voice_lens, element_fit_lens)** — these are role ids; the actual role files live in `roles/`. Cross-dependency.
- **AGENTS.md mentions the `s102 walk stop` proposed re-jurying 222 no-quorum entries through this panel** — the operator's call; pending decision.
- **The brief said 3 verdict_panels but only 1 .py file exists.** The directory has: AGENTS.md, __pycache__, registration_confirm.py = 1 entry.

---

## 11. panels/ — 1 entry (settings.json)

### Registry purpose
Brain-authored DECLARATIVE UI panels. JSON field-defs in `panels/`. Fields edit real config. The 'others' tier of self-modification. One settings.json is the only current panel.

### The settings panel (panels/settings.json)

```json
id: "settings"
title: "settings"
fields:
  - key: presence_mode, label: Presence Mode, type: select, target: mode
    options: [listening, text-only, background, focus, walkthrough, watch-and-react, decide-for-me, off]
  - key: model, label: Model, type: select, target: model
    options: [14 model ids including local and cloud models]
```

### GAPS / STALE / SURPRISES
- **Only 1 panel** — the settings panel is the sole registered panel. MAP.md confirms `panels: settings` in the live registry auto-maintained block.
- **The model options list** includes: huihui_ai/qwen3-vl-abliterated:30b-a3b, gemma4-26b-a4b-q3km:latest, qwen3.6-35b-a3b-q3km:latest, qwen3.6-27b-q3km:latest, nomic-embed-text:latest, gemma4:31b-cloud, nemotron-3-super:cloud, deepseek-v4-flash:cloud, deepseek-v4-pro:cloud, kimi-k2.6:cloud, glm-5.1:cloud, glm-5:cloud, qwen3.5:397b-cloud, kimi-k2.5:cloud
- **`panels/AGENTS.md`** — exists; no constitution read in this pass (deferred, not in the primary scope).

---

## 12. forms/ — 4 entries

### Registry purpose
The file-discovered FORM registry (Cognition Engine NEWMOD · P1). A form is a FILE-SHAPE → ROUTING rule: recognises a kind of corpus unit by its shape and routes it to an effort band (legibility=cheap/skip · deep=heavier). "Effort-routing by form" made DATA, not a hardcoded if-ladder. The fallthrough form (`prose`) is the catch-all.

### Field schema
```
id           required — MUST equal file stem
match        required — callable (text, *, meta=None) -> bool; the deterministic shape recogniser
stage        required — the effort band (legibility | deep | skip — open vocab DATA)
policy       optional — a generation-policy id this form selects
fallthrough  optional — bool; catch-all, checked LAST
desc         optional
```

### Entry list

| id | stage | policy | fallthrough | match logic | desc |
|---|---|---|---|---|---|
| decision | deep | capture_default | — | decision/decided/resolved/Dn header in first 8 lines | High-substance decision note → heavier deep pass |
| log | legibility | prose_default | — | Timestamp ≥3 lines OR changelog/handoff/status header in first 5 | Bookkeeping → cheap broad pass |
| prose | deep | capture_default | True | Any non-empty string | Catch-all fallthrough — free prose treated as substance until narrower form claims it |
| registry | legibility | prose_default | — | MoC/index/registry header OR >60% link-lines with ≥5 lines | Structure/index → extract cheaply, no deep describe |

### GAPS / STALE / SURPRISES
- **Route ordering:** narrow forms first, fallthrough (`prose`) last — enforced by `fallthrough: True` flag.
- **`route()` FAILS LOUD if NO form matches** — impossible in practice because `prose` catches any non-empty string; the fail-loud is reserved for an empty registry or all-False match (misconfiguration).
- **`prose_default` and `capture_default`** are generation_policies ids referenced but not defined here — live in `generation_policies/` (external dependency).
- **No `skip` stage form exists yet** — the skip band is declared as valid in the AGENTS.md but no form routes to it.

---

## 13. mode_detection_rules/ — 3 entries

### Registry purpose
The file-discovered MODE-DETECTION-RULE registry (Concurrent Cognition Group I — mode auto-detector). Maps a SIGNAL CONDITION → a candidate presence mode. Rules are evaluated in PRIORITY order (first-match-wins) against the live `activity_signal()` snapshot. Conditions are data-AST (RULE_OPS grammar), never lambdas.

### Field schema
```
id        required — MUST equal file stem
candidate required — presence-mode id this rule proposes (validated ∈ suite.MODES at detect time)
why       required — one-line legible rationale
priority  required — int (lower = higher priority; first-match-wins)
when      required — a runtime/rules.py RULE_OPS data-AST (boolean/comparison/field-access over a snapshot)
```

### Entry list

| id | candidate | priority | when condition | why |
|---|---|---|---|---|
| background | background | 10 | idle_seconds ≠ None AND idle_seconds ≥ 900 | operator quiet for a long while → drop to low-noise background presence |
| focus | focus | 20 | idle_seconds ≠ None AND idle_seconds < 90 AND inbox == 0 | sustained operator activity with nothing piling up → protect deep work |
| listening | listening | 30 | inbox > 0 | items are awaiting the operator → be present and conversational |

### GAPS / STALE / SURPRISES
- **Only 3 rules cover the 3 main presence states** (background/focus/listening) — MAP.md's live registry shows 8 presence modes: listening, text-only, background, focus, walkthrough, watch-and-react, decide-for-me, off. The rules only produce 3 candidates; the other 5 modes (text-only, walkthrough, watch-and-react, decide-for-me, off) have no detection rules — they must be manually set.
- **None missing coverage is by design** — manual modes don't need auto-detection (off/walkthrough are deliberate operator choices). But `text-only` and `decide-for-me` have no rule either — POSSIBLE GAP if those modes should also be detectable.
- **Priority 10→20→30:** long idle beats sustained-activity-with-clear-inbox beats items-piling-up.
- **`not-None guard` is explicit in background and focus rules** — because `idle_seconds` is None at startup and `None >= 900` would TypeError.

---

## 14. checks/ — 2 entries

### Registry purpose
The file-discovered CHECK registry (G3·S3a). Deterministic gates as declared data. One row = one pure verdict function ({passed, reasons}). Referenced by name from cascade decls ({op:'check', check:'<id>'}). When a model judgment misfires on a rule-shaped constraint, the rule becomes a registry row.

### Field schema
```
id          required — MUST equal file stem
label       optional
description optional
check()     required function — (value, **params) -> {passed: bool, reasons: list}
```

### Entry list

| id | label | description | wraps |
|---|---|---|---|
| dossier_refcheck | Registry-dossier no-fiction floor | Deterministically verifies a proposed registry dossier's closed-world claims: capabilities ⊆ canonical vocabulary, maps_to_feature ∈ real inventory (or 'proposed'), code refs resolve. | design/_system/refcheck.check_dossier |
| prose_clean | Operator-prose leakage floor | Deterministically checks dossier's two operator-facing prose fields for code leakage (file paths, markup, selectors, address schemes, feature-id shapes, code identifiers). Domain vocabulary not flagged. | design/_system/prose_check.check_prose |

### GAPS / STALE / SURPRISES
- **Both checks are WRAPPERS** — they delegate to `design/_system/refcheck.py` and `design/_system/prose_check.py`. The registry rows make them cascade-referenceable by name, but the actual logic lives in `design/_system/`. Cross-dependency.
- **Only 2 checks** — the registry is very thin. The AGENTS.md implies this will grow as more model judgments are moved to deterministic rules.
- **The `check()` function uses `sys.path.insert`** to add `design/_system` at call time — a dynamic path injection pattern, not a static import.

---

## 15. board_edges/ — 4 entries

### Registry purpose
The file-discovered EDGE-KIND registry for Noticeboard items (runtime/cc_board.py). Typed cross-registry links a board item carries (`links: [{kind, target}]`). REUSES RelationTypeRegistry verbatim (same row shape as relation_types/) but kept in a SEPARATE dir because board edges are structural/provenance edges, distinct from relation_types/'s corpus-semantic edges.

### Field schema
```
id       required — MUST equal file stem
directed required — bool
inverse  optional
label    optional
desc     optional
```

### Entry list

| id | directed | inverse | desc |
|---|---|---|---|
| attached_to | True | — | Board item is attached to this channel / Space (item → channel). Mirrors the CHANNEL-LAYER-SEAM attachments manifest one level down. |
| authored_by | True | authored | Board item was authored by this session (item → session://<id>). First exercise of relation registry across registries. |
| promoted_from | True | promoted_to | This item was promoted from another board item (e.g. request promoted-from idea) (item → board://<id>). |
| sourced_from | True | — | Board item originated from this source (item → source-type row). The seam the GitHub fold-in joins on. |

### GAPS / STALE / SURPRISES
- **All 4 are directed** — no symmetric board edges exist yet.
- **`authored_by` inverse `authored`** is cited but NOT its own file — the inverse direction exists as a label only, same as relation_types/ pattern.
- **The AGENTS.md notes a planned future unification into relation_types/** when the Heart's cross-registry traversal engine lands. Currently tracked as a board `idea` item.
- **`sourced_from` has no inverse** — reasonable (a source doesn't "point back" to its items in a board context).

---

## ROOT FILES — loose .md and .log files

### AGENTS.md (root)
**Type:** constitution (root module).  
**What it holds:**  
- The rules (10 non-negotiable laws: build against contracts, schema-additive, one source, fail loud, storage on ext4, no Gemini, stage-gated, author from registry, AI-operated is not review-free, commit to main no branches)  
- "Where things go" table (15 categories: nodes, models, storage, RHM verbs, presence modes, settings panels, new UI components, canvas surfaces, new operations, new contracts, ops/services.json, self-description update)  
- Gap pressure — the discovered law + 7 build candidates (C1–C7)  
- The convention (every folder has AGENTS.md)  
**Status:** living. Read before any work in the repo.

### MAP.md (root)
**Type:** map (Map of Contents).  
**What it holds:**  
- The one-picture diagram + mermaid flowchart (canvas/runtime/fabric/store/mcp_face/nodes/voice/panels/contracts)  
- Module map (13 modules with constitutions)  
- **Live registry** (auto-maintained by Suite.refresh_self_description): 16 node-types, RHM verbs (run/propose/build/consult/show/panel/extend/configure/load_voice/unload_voice/request_change), 8 modes, 1 panel, 18 models
- Suite architecture narrative (very long — RHM, decision→implementation wire, session supervisor, capability registry, point-in-time launch, search→handle→act, the ③④⑤ command-wrapper layer REMOVED)
- Self-modification section (nodes/panels/extensions/checkpoints/ledger)
- Path-of-least-resistance law  
**Status:** living. AUTO-MAINTAINED — drift-check tests fail loud if registered capability isn't reflected.

### STATE.md (root)
**Type:** state (current build status).  
**What it holds:** Current status as of 2026-06-07. Very long — covers model/VRAM layer, voice co-residence, persona identity, the decision→implementation wire, session supervisor (F1.2/R1.1/R1.2/R1.3/R1.4), capability registry, search→handle→act. Maintained by integration. Tests are canonical; if STATE.md disagrees, fix STATE.md.  
**Status:** living. As of 2026-06-07. Likely needs updating for work done since then.

### README.md (root)
**Type:** project README.  
**What it holds:** Brief description of company (the Vi composition suite). Layout table (contracts/store/runtime/fabric/mcp_face/nodes/canvas/docs). "How it runs" section. Status field says "Skeleton only" — this is STALE (the system is far beyond skeleton).  
**STALE:** README.md still says "🦴 **Skeleton only. Boundaries drawn; nothing implemented.**" — this contradicts STATE.md and the entire build history. The README has NOT been updated alongside the codebase.

### HANDOFF.md (root)
**Type:** handoff (2026-06-06 session, the merge + voice-live session).  
**What it holds:** The 2026-06-06 session narrative — interactive-surface-build branch merge, voice VRAM convergence, the live voice circuit, how to operate, the voice stack (5 TTS engines + 3 GPU STT ears), the Company voice identity, seams to extend, gotchas, honest status.  
**Status:** living narrative. SUPERSEDED by HANDOFF-2026-06-07 for the most recent session.

### HANDOFF-2026-06-07-model-layer-and-cognition.md (root)
**Type:** handoff (2026-06-07 session).  
**What it holds:** The most recent session's work — model/VRAM layer, persona identity hookup, 4-bit AWQ Orpheus co-residence, voice trace, co-residence shrink mechanism. 3-tier verified/code-complete/known-unknown honest status. "The on-device live voice conversation has NEVER been verified." 8 commits. Concurrent Cognition loop commissioned (`build-prep/concurrent-cognition/`).  
**Status:** living. The most recent session-level narrative in the repo.

### SESSION-OPERABLE-INTERFACE.md (root)
**Type:** session-handoff (cross-session awareness doc, operable-interface build).  
**What it holds:** Documents EXACTLY what the interface session built + what regions of hot files it touches — written for the parallel concurrent-cognition session to avoid collisions. Covers 7 build groups (A/H/B/C/D/E/F1/G1/G3). Lists collision zones in runtime/suite.py, runtime/bridge.py, canvas/app/src/useAppController.ts.  
**Status:** likely superseded (the merge was completed per HANDOFF.md and MERGE-COORDINATION.md).

### MERGE-COORDINATION.md (root)
**Type:** coordination doc (peer-to-peer between two parallel sessions).  
**What it holds:** Very long. The interface session's stated side + proposed plan + real questions for the cognition session to reply to. Covers merge order, uncommitted work, hot-file collision zones, seam notes. Tim relayed responses between sessions via this file.  
**Status:** historical — the merge is complete per HANDOFF.md. STALE for current state. 103KB — large.

### CRITIC-VERDICT-integration-journey.md (root)
**Type:** integration test verdict.  
**What it holds:** Fresh-eyes critic verdict on the whole operator journey (phone 390x844 + desktop 1440x900). VERDICT: PASS with flags. Records 5 working steps, 5 flags (A=jargon leak "RHM" in option copy, B=raw item codes (s117) in guide answer, C=two "what needs me" surfaces disagreeing with zero overlap, D=unlabelled "600" header, E=abstract decision substance). Confirmed: save works, count decrements, loop closes correctly.  
**Status:** historical integration test record. Valuable as a specific gap inventory.

### mcp_registration_debug.log (root)
**Type:** debug log.  
**What it holds:** MCP tool registration debug output. 39 tools being registered to `http://127.0.0.1:3400/api/gateway`. All succeeded (every tool logged "SUCCESS").  
**Status:** a stale runtime artifact. Not a configuration file. All 39 tools registered clean.

---

## CROSS-REGISTRY OBSERVATIONS

### The ONE mechanism, many vocabularies
Every registry (mark_types, item_types, stack_item_types, relation_types, attachment_types, source_types, forms, mode_detection_rules, checks, board_edges, decision_subtypes, verdict_panels) is the SAME file-discovered mechanism: a dir of `<id>.py` files each declaring a module-level dict, validated at discovery, fail-loud on malformed entries. The mechanism is single-sourced; only the row shape and the dir are distinct per vocabulary.

### The missing/thin registries (gaps in this area)
1. **source_types:** only 1 entry (claude_code); github is the obvious future addition
2. **verdict_panels:** only 1 entry (registration_confirm)
3. **checks:** only 2 entries (both wrappers into design/_system/)
4. **mode_detection_rules:** 3 rules for 3 modes; 5 of 8 modes (text-only, walkthrough, watch-and-react, decide-for-me, off) have no detection rule
5. **forms:** no `skip` stage form — the skip band is declared valid but no form routes to it
6. **stack_item_types:** 3 of 4 types (explanation, presentation, verify-request) declared but not yet rendered (no feed + no renderer landed yet)

### Decision explanation_source gap
16 of 24 decisions have no `explanation_source`. The explanation_policy fires (subtype is set) but with no source pointer, the RHM grounds the explanation against nothing declared. This is a content gap, not a code gap.

### Root files staleness
README.md says "Skeleton only" but the system is fully built with voice, session supervisor, decision→implementation wire, self-modification, etc. The README needs a rewrite.

### MERGE-COORDINATION.md is superseded
At 103KB it's the largest file in the root. The merge it coordinated is done. It's valuable historical record but its presence in the root creates navigation noise.

### SUBTYPE-COVERAGE-GAP.md (build-prep/the-one-application/)
Documents the 2026-06-21 fix that brought all 24 decision rows to subtype coverage. The critical finding: "substrate-home" (a frame-first keystone) was invisible for weeks because it had no subtype. The schema gate is now in place.
