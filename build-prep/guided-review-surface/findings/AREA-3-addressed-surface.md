# AREA 3 — The Addressed Surface: Context Auto-Resolution, Mark-Up, and the Screen Directory Pattern

Research wave agent 3 of 6. Evidence markers: **Observed(file:line)** / **Inferred** / **External** / **Anchor-idea**.

---

## 1 · What is actually built — the real state of the mark-up system

### annotate / ingest_comment / attach_chat — the full pipeline

The mark-up machinery is real, working, and meaningfully deeper than the anchor described.

**`annotate(address, text, source)`** — Observed(suite.py:4263) — attaches a comment to any `ui://` address, persisted in `annotations.jsonl` via `append_annotation`. S0-gated first (calls `parse_ui_address`, raises on malformed). Emits an addressed SSE event at the locus. The store is append-only; each annotation gets a `ts` from the store leaf. The result is retrievable by `annotations_at(address)`.

**`ingest_comment(address, text, source)`** — Observed(suite.py:4291) — is the WIRED comment-ingest entry point (L4 / Seam 5). It does two things in order: (1) calls the pure `annotate()` leaf, (2) appends ONE additional `append_chat` turn stamped with the address — the "located gold label" for training the twin. This is what `/api/annotate` and the I5 router call. The separation is intentional and enforced by an acceptance test (`annotation_acceptance.py` asserts `annotate()` alone writes zero chat).

**`attach_chat(address, text, role, source)`** — Observed(suite.py:4487) — attaches a chat turn to a `ui://` address via the SAME open `chat.jsonl` record (one-source, no parallel chat store). The turn carries an additive `address` field. The `ts` from the store leaf gives R2's recency decay its clock.

**`set_presentation_pref(address, pref, text, source)`** — Observed(suite.py:4391) — records "how Tim wants this presented" at a `ui://` address. Rides the SAME `annotations.jsonl` leaf with `kind:"presentation_pref"` as the distinguishing marker. Distinct from comments: it is a CONTROL signal, not twin gold — so it deliberately does NOT flow through `ingest_comment`. F1 Learning Loop: the pref persists across sessions, is gathered by R2 as its own stratum, and is applied model-free (deterministic re-ordering, e.g. `lead_with:how_to_change` reorders the address bundle's legs structurally).

**`route_click(address, graph_id, verb, text, args, source)`** — Observed(suite.py:4204) — the I5 annotate-vs-operate router. Routing rule: `ui://` address + NO consequential verb → annotate face (calls `ingest_comment`); any consequential verb OR `run://` address → operate face (calls `act`). The "never blur" guarantee is structural: `annotate()` raises on a non-`ui://` address, so a live graph-node instance is incapable of being commented.

---

### Can the RHM mark up on the user's behalf mid-conversation?

**Answer: not directly, and this is the key gap.**

The anchor says "mark up as you talk = the RHM calling annotate/tag on the locus on the user's behalf." The code contradicts this at the verb-whitelist level.

The RHM's verb whitelist is exactly 7+3 verbs: `run`, `propose`, `build`, `consult`, `show`, `panel`, `extend` + `configure`, `load_voice`, `unload_voice` + `request_change`. — Observed(suite.py:3158–3206, RHM_VERBS tuple).

**`annotate` is NOT in the RHM_VERBS whitelist.** — Observed(suite.py:4031: "verb {verb!r} is not permitted from the RHM — only {self.RHM_VERBS}").

`annotate` is on the OPERATOR face only (`/api/annotate` → bridge.py → `ingest_comment`). The MCP face (the RHM's channel) does not have it. So today, the RHM cannot call `annotate` mid-conversation. The user's text-comments in chat are attached as gold training turns via `ingest_comment` when they come through `/api/annotate`, but the RHM cannot proactively attach them during dialogue.

**However, `request_change` IS in the verb list** — Observed(suite.py:3197) — and it routes a conversational change-request into `surface_intent_at`, which calls `ingest_comment` inside it — Observed(suite.py:3994-4029). So there IS a path from conversation to annotation-like output, but it is scoped to build-intents, not to arbitrary comment mark-up.

**What would be needed:** Adding an `annotate` verb to the RHM whitelist — with the address inferred from `current_locus()` when not explicitly supplied — and putting it on the MCP face. The machinery (`annotate` / `ingest_comment`) is already complete. The gap is one governance decision and one whitelist entry. Confirmed: `grep annotate mcp_face/*.py` → 0 hits — the MCP/agent face has NO annotate path at all.

**The operator-face bridge routes are richer than the anchor listed** — Observed(bridge.py): POST `/api/annotate` (I6, suite.py:1429), POST `/api/attach-chat` (I7, :1485), POST `/api/pin` (the SET-path for the pin override, :1470), GET `/api/annotations` + GET `/api/chats` (:584) + GET `/api/context` (R2 inspector, :544) + GET `/api/address-view` (:594, the composed read). All on the OPERATOR face, none on MCP. So the operator can mark up by address from the UI today; the RHM cannot.

---

### Tags on GROUPS vs single elements — the real story

The anchor states "mark-up on elements OR groups." This needs stress-testing.

The annotation system is address-keyed. `annotate(address, text)` takes a SINGLE address string. There is no batch-annotate, no group-annotation primitive, no region-scoped annotation. — Observed(suite.py:4263-4289, 4291-4324).

However, **group addressing exists implicitly but ONE-DIRECTIONALLY** — through the address tree hierarchy, walked UPWARD only. The `ui://` grammar is hierarchical: `ui://inbox/build-review` is a child of `ui://inbox`, which is a child of `ui://<root>`. `_r2_ancestors` — Observed(suite.py:2556) — walks this tree UPWARD: locus → every ANCESTOR up to the region root, inclusive. It never walks downward and never sideways.

The directionality is the crux:
- **Parent → child inheritance: WORKS.** If you annotate at `ui://inbox` (the parent/region), that comment RESOLVES INTO every child element's context at resolution time. A comment on the region is inherited by every element within it (demoted by proximity, but present). ✓
- **Child → parent rollup: DOES NOT WORK.** If you sit AT the group address `ui://inbox` as your locus, R2 gathers only `ui://inbox`'s OWN comments and its ancestors — NOT the comments on its descendants (`ui://inbox/build-review`, etc.). So "click the group, see everything said about this region" is NOT supported.
- **Sibling sharing: DOES NOT WORK.** Two children of the same parent do not see each other's comments.

**The implication for groups:** you can comment ON a group (annotate the parent address) and have it flow DOWN to all members — that is genuine, useful group-tagging. But you cannot VIEW a group as the aggregate of its members' commentary. The tree is an inheritance mechanism, not a rollup.

**What does NOT exist:** (a) explicitly designating a set of non-hierarchical addresses and annotating them together in one call — you'd call `annotate` three times for three addresses; (b) any downward/aggregate view at a group node.

**Contrast with the anchor's implication:** When the anchor says "comments/tags on elements OR groups," the supported case is "say something ABOUT this region and have it apply to everything inside" (parent annotation → child inheritance). The unsupported case is "stand at the region and see all the marks made on its parts." If the guided-review surface wants the latter (likely — reviewing a screen and seeing all comments on its elements), it needs a NEW descendant-gather, distinct from the existing ancestor-walk.

---

## 2 · Context auto-resolution — R2, how it actually composes

### The full R2 pipeline

R2 is built and running. This is more complete than any design document suggested.

**`_r2_ancestors(locus)`** — Observed(suite.py:2556) — the foundation. Takes a `ui://` locus, returns [locus, parent, grandparent, ..., region-root]. All candidates are S0-validated; malformed ones are silently skipped (never crash the turn).

**`_r2_gather(locus, graph_id, now, resolution)`** — Observed(suite.py:2812) — gathers from ALL strata:
1. `annotation` stratum: `annotations_at(addr)` for locus and each ancestor. Skips `presentation_pref` kind.
2. `presentation_pref` stratum: the learned presentation preferences at each ancestor, pin-persistent.
3. `chat` stratum: `chats_at(addr)` for locus and each ancestor.
4. `event` stratum: `_r2_events_at(addr)` for addressed SSE events.
5. `howto` stratum: `_r2_howto_at(addr, now, detail)` — the authored affordance text from the registry (D1). Pin-persistent (re-stamped with `ts=now` every gather so recency never decays).
6. `run://` bridge stratum: when `graph_id` supplied and locus is `ui://canvas/<node>`, also gathers run:// version history (L6), capped at `R2_RUN_VERSIONS=3` to prevent starvation. — Observed(suite.py:2880-2884).

The gather is mode-parameterizable (E1): `resolution` spec (from `resolution_spec_for(mode)`) declares which strata to admit and `howto_detail` (full/terse/none). background mode gets terse howtos; off mode suppresses howtos entirely.

**`_r2_dedup(items)`** — Observed(suite.py:2894) — collapses the triple-counted comment: one clicked comment lands as annotation + gold-chat + addressed-event echo. Identity is `(address, underlying-text)`; event echoes are truncated so the prefix test is used. Survivors are the full-text annotation/chat items.

**`_r2_score(item, locus, now, semantic)`** — Observed(suite.py:2522) — the scoring formula:
```
score = exp(-R2_LAMBDA * delta_t) * (1 / (1 + R2_PROXIMITY_WEIGHT * tree_distance)) 
        + R2_PIN_WEIGHT * pin_bonus
        + R2_SEMANTIC_WEIGHT * cosine(intent, item)
```
Four dimensions: recency (halves at ~2 days), proximity in the address tree (parent address scores lower than exact match), pin override (always outranks unpinned), semantic relevance to the operator's current intent (X13, requires embedder at :8001, degrades to 0 with warning when down).

**Budget cap: R2_BUDGET = 4000 chars (~1k tokens)** — Observed(suite.py:2482) — HARD CAP, never stuffed. The sorted items are accumulated until the budget is full, then stopped. This is the mechanism that prevents the 396k-char context-flood problem.

**`_resolve_context_at(locus, now, graph_id, intent, resolution)`** — Observed(suite.py:3036) — the production entry point. Returns a ready-to-inject string block `"CONTEXT RESOLVED AT YOUR LOCUS..."` or `''` on failure. Wired into `_chat_context` — Observed(suite.py:2153-2174) — so every RHM chat turn at a locus gets the context injected.

**`context_at(address)`** — Observed(suite.py:3088) — standalone read face. Returns a structured bundle `{address, items, count, budget}` using the same R2 engine. Exposed via `/api/context?address=` bridge route. S0-gated explicitly (unlike the gather, which silent-skips malformed addresses — the standalone read RAISES for a malformed address because silence would lie "no context here").

### Does context include ancestors?

YES, explicitly and by design. The gather iterates `_r2_ancestors(locus)` — Observed(suite.py:2845): `for addr in self._r2_ancestors(locus)`. Every annotation, chat, event, and howto at every ancestor contributes to the resolved context. Proximity scoring demotes them — an exact-address comment outranks a parent-level comment — but parent-level context always contributes.

This means a comment on `ui://inbox` shows up in every `ui://inbox/...` child's resolved context (with lower score than a comment placed exactly on the child). The howto text at `ui://toolbar` (the authored guide for the region) always resolves into any `ui://toolbar/run` context, flood-guarded by R2_HOWTO_MAX.

---

## 3 · The address system + the `ui://` grammar

### Addresses.json → live UI_REGISTRY — the two-grammar problem and its resolution

The anchor identifies a "two non-interoperable grammars" problem. The code shows it has been RESOLVED (S0 + S1 both built and running).

**Grammar** — Observed(contracts/ui_info.py:185-217):
```
ui://<region-or-kind>/<element>[/<sub>][/@state]
```
Structural only; permissive by design so both the corpus element-form (`ui://inbox/build-review`) and the live kind-form (`ui://chrome/inbox`) both parse. `parse_ui_address` validates the shape, raises on malformed.

**`UnionAddressRecord`** — Observed(contracts/ui_info.py:262) — the ONE canonical per-address shape used by both sides:
- `address` — the full `ui://` string
- `kind` — `chrome|field|canvas|panel|ext` (the live resolver dispatch field; required)
- `region` — coarse grouping (required non-empty)
- `capabilities` — bool-object (`pointable/spotlit/presentable/openable/drivenReadOnly`)
- `represents` — feature-id (corpus optional)
- `code` — `code://` symbol (corpus optional, S3)
- `states` — applicable `@state` suffixes
- `tier` — governance posture for COMMANDS at this address (I4)
- `howto` — the authored affordance text (D1, optional)

**Live UI_REGISTRY** — Observed(suite.py:7774-7807) — 9 bare-ref region rows (toolbar, inspector, inbox, activity, chat, workshop, walkthrough, deferred-queue + canvas `*`) plus ALL the corpus element-level rows loaded at class-definition time via `_load_corpus_element_addresses()`. S1 landed: the registry now carries both region-level AND element-level addresses.

**`data-ui-ref` → `addresses.json`** — Observed(design/_system/addresses.json:1) — the design-side registry holds the full `ui://` address strings with region, capabilities (list form), represents, code, howto. `parse.py` and `check.py` use it for orphan detection and traceability.

**`conform_corpus` / `conform_live`** — Observed(contracts/ui_info.py:402-439) — the conformance checks that validate both sides against the ONE grammar. Both sides now validate against the same grammar.

### The `data-ui-ref` → address → DOM chain

A mockup element carries `data-ui-ref="ui://inbox/build-review"`. This address is registered in `design/_system/addresses.json`. The live app picks it up via `_load_corpus_element_addresses()`. The FE's `resolveUiTarget` / `querySelector('[data-ui-ref="..."]')` resolves it to the DOM element. The RHM's `show` verb can drive the view to it.

---

## 4 · The mockup corpus directory structure — what IS the pattern?

### The register.json schema as the pattern

The "screens broken into directories, a pattern" from the anchor is more precisely: **screens are organized into lettered AREAS (A–G) in `design/register.json`, mapped to journey sequences (J1–J9), and the actual HTML files in `design/mockups/` follow the naming convention `<area><number>-<feature>-<platform>.html`.**

Observed(design/register.json:17-25) — the areas:
```
A — The operating surface (canvas)
B — Right-hand-man + review/walkthrough organ
C — Inbox + decisions (chief-of-staff)
D — Self-build / the wire (act on outputs)
E — Models + embeddings
F — Frame, settings, system
G — Responsive system
```

Observed(design/mockups/) — the files follow `<area><view-number>-<feature>-<platform>.html`:
- `A2-canvas-desktop.html`, `A2-canvas-mobile.html`
- `B3-walkthrough-desktop.html`
- `C1-inbox-desktop.html`
- `D6-wire-states-desktop.html`

Each view in `register.json` carries `represents[]` linking to feature-ids, `platforms[]`, `journeys[]` (J-journey links), and `status`. The `sequences` array defines journey steps as ordered view-id lists.

**The "pattern" is a three-layer naming/registry structure (NOT a directory hierarchy today):**
1. Area code (A=canvas, B=RHM, C=inbox...) — a coarse functional grouping carried in the FILENAME PREFIX and `register.json`, not in folders. `design/mockups/` is a FLAT directory — Observed(`ls design/mockups/` → all `.html` files at one level).
2. View variant (desktop/mobile/responsive) — platform-scoped, also in the filename suffix.
3. `represents[]` + `journeys[]` cross-links in register.json — the graph that a tree can't hold.

**Important honesty:** the anchor's "screens broken into directories, a pattern" is a SHOULD-BE, not what exists. B3 (directory layout mirrors the journey sequence) is ☐/unbuilt in the criteria. Today the pattern is a NAMING CONVENTION (`<area><n>-<feature>-<platform>.html`) plus the `register.json` index — the journey graph lives entirely in `register.json`'s `sequences[]`, not in the filesystem layout.

**The mockup itself carries the address** — each mockup element carries `data-ui-ref="ui://..."` so the mockup is not just a picture but an addressed artifact. The `parse.py` script reads the mockups, extracts all `data-ui-ref` attrs, and builds `element-map.json` — the bridge from mockup element to live address to feature to code symbol.

### The screen-directory concept vs the journey-graph concept

The anchor's "sequence is the RHM Walkthrough Organ" maps directly. The review sequences in `register.json` (sequences J1–J9) are journey-step lists of view-ids. `start_session(item_ids)` takes a list of addresses OR inbox item-ids; `start_guide(topic)` uses `GUIDE_SEQUENCES` — Observed(suite.py:3355-3368) — which are lists of `ui://` addresses.

The screen directory pattern IS the journey-graph. `register.json`'s `sequences[]` = the ordered stop list. `GUIDE_SEQUENCES` = the backend-side incarnation of the same idea. They are not the same JSON but they encode the same concept: an ordered walk through addressed UI elements.

---

## 5 · The mockup-vs-live distinction — how it actually works

### The `mockup://` scheme

The anchor's observation that "comments on real UI vs new-UI mockups" need routing is grounded in a real mechanism, but it operates differently than the anchor assumed.

**`mockup://` is a separate, non-`ui://` scheme** — Observed(suite.py:2086-2125) — used in `focus.selected` to indicate the operator is reviewing a design mockup. When `focus` contains `mockup://<filename>.html`, the `_chat_context` method:
1. Validates it as a safe bare `<file>.html` name (path-safe, no escaping)
2. Reads the HTML from `design/mockups/<file>` into the context block (capped at 14,000 chars)
3. Injects it as `MOCKUP UNDER REVIEW (the operator is looking at this design mockup RIGHT NOW...)`
4. The RHM reads it and explains it to the operator at altitude — this IS the "RHM reads the mockup FOR Tim"

This `mockup://` scheme is explicitly NOT a `ui://` address. It is handled BEFORE the `ui://` indicated-address block in `_chat_context`. — Observed(suite.py:2095-2096): `mockups = [s for s in raw_selected if s.startswith("mockup://")]`, and the `indicated` set separately filters for `ui://` starts.

**What does NOT exist:** a `mockup://` address that can be annotated. `annotate(address, text)` calls `parse_ui_address(address)` which raises on anything that doesn't start with `ui://`. So you CANNOT call `annotate("mockup://B3-walkthrough-desktop.html", "needs more contrast")` — it will raise.

**The real routing distinction is:** annotations on `ui://` addresses persist on the LIVE UI component (the same element address exists in both the mockup and the live app). An annotation on `ui://inbox/build-review` attaches to that element whether the operator clicked it in a mockup or in the running app. The address IS the routing key; the `mockup://` handle is just a presentation-context mechanism for the RHM's chat, not a content-branch.

### How the mockup-vs-live distinction SHOULD work

For proposed new surfaces (mockups of things not yet built), the element-level `ui://` addresses are still registered in `addresses.json` and `UI_REGISTRY` (they're loaded from the corpus). An annotation on `ui://canvas/wire-request` attaches to that address regardless of whether it exists in the running app yet. The system doesn't distinguish "does this address exist in the live app right now?" — it stores the annotation, and R2 resolves it.

**The conceptual answer to "how does an address tell which?"**
- `run://` = a LIVE graph-node instance. Clicking → operate face. Never annotatable.
- `ui://` = a UI element (could be live or only in mockups). Clicking → annotate face (I5). The annotation lives in the corpus.
- `mockup://` = a design mockup FILE (a reading context). Not an annotatable address. Used only in `focus.selected` to tell the RHM what the operator is currently looking at.

**What the guided-review surface needs:** When the operator says something about a mockup element, the RHM should resolve the element's `data-ui-ref` address from the HTML, and call `ingest_comment` on THAT `ui://` address — not on the `mockup://` file. The mockup is the visual surface; the `ui://` address is the annotatable coordinate. The `element-map.json` (built by `parse.py`) contains the mapping: mockup filename → elements → `ui://` addresses.

---

## 6 · The walkthrough/review/guide backend — what it actually does and where it falls short

### What `start_session` / `present_current` / `next` actually do

**`start_session(item_ids, mode, teach, indicate)`** — Observed(suite.py:6099) — compiles a review-session GRAPH where each item_id is a step. Calls `run()` with paused go-nodes so the session advances one step at a time only when `next()` opens the gate.

**`present_current(session_id)`** — Observed(suite.py:6198) — the core narration logic. Two branches:
1. If the current item is a `ui://` address: reads the THREE-leg affordance bundle from `address_help` (corpus how-to, what-this-is, blast-radius). Narration = `teach_text + corpus_narration` (C2 bootstrap: teach leads, corpus enriches). Returns `ui_target` = the element address itself, `guide:True`. MODEL-FREE by construction — no LLM call here.
2. If the current item is an inbox review-id: calls `coa(item_id)` (the decision compiler). Fail-safe: if coa errors, presents the raw payload. Returns `ui_target` stamped from `_registry_ui_target(raw)`.

**`next(session_id)`** — Observed(suite.py:6492) — opens the current step's go-gate, runs the session graph (only the opened step fires), advances the cursor atomically with a per-session lock, returns the next presentation. Idempotent past the end.

**`start_walkthrough(item_ids)`** — Observed(suite.py:6287) — the C4 seam. Binds the presence-dial mode "walkthrough" to the ORGAN. Previously, selecting the walkthrough dial only set a cosmetic directive; now it also starts the session over pending inbox items.

**`start_guide(topic)`** — Observed(suite.py:6442) — the C1 system-initiated tour. Resolves `GUIDE_SEQUENCES[topic]` to a list of `ui://` addresses, starts a session over them. Three topics built in:
- `"default"`: [toolbar/run, toolbar/presence, inbox/build-review] — the orientation tour
- `"request-a-change"` / `"self-modify"`: [toolbar/run, canvas/wire-request, inbox, inbox] — the bootstrap self-modify teaching loop (C2)

**GUIDE_TEACH** — Observed(suite.py:6378) — step-by-step narration for the "request-a-change" bootstrap, composed with corpus how-to in `present_current`. The teaching voice IS written in the code.

### Where the walkthrough falls short for the guided-review surface

**1. The RHM talks back only via `/api/chat` — it doesn't narrate autonomously at each step.**

`present_current` returns a `framing` string (the narration text). The FE receives it. But the RHM doesn't SPEAK the framing — the FE must call `speakReply` with the framing text — Inferred from the code comment at suite.py:6223 ("useAppController ~1113 reads session.framing and speaks the how-to FOR FREE"). This is the voice narration effect — it already exists if the FE wires it.

**2. The RHM does NOT proactively explain at his altitude at each stop.**

`present_current`'s narration is corpus-data: the authored `howto` field from the registry. For mockup elements that DO have authored howto text (like `ui://toolbar/run`), this works. For mockup elements WITHOUT authored howto text (most of the 24+ addresses), `address_help` returns only `what_this_is` from the title/represents field — not a rich altitude-appropriate explanation.

The anchor says "tells you, at your altitude, what this IS." That requires either (a) all elements having authored `howto` text, or (b) the RHM generating the explanation using the LLM (the coa path). The guide branch is MODEL-FREE by construction — it uses corpus data only. The coa branch IS model-dependent but is for inbox review-items, not ui:// element tours.

**This is the crux the anchor flagged:** `address_help` only returns what's registered. For redesign mockups, it can only explain what the corpus says — and the corpus howto coverage is incomplete for most elements.

> Line-number corrections to the anchor's §7: `_registry_ui_target` is at suite.py:6161 (anchor cited :5405). `surface_intent_at` is at suite.py:6816 (anchor cited :1025/6642). Both confirmed by grep.

**3. The FE show-me lane is explicitly DEFERRED** — Observed(suite.py:6313-6316): "DEFERRED (the FE show-me lane — noted, NOT built here): the FE wiring that CALLS this when the operator picks the walkthrough mode on the presence dial, and then DRIVES the organ view per step."

The backend is ready (`start_walkthrough` is callable at `/api/walkthrough/start`); the FE wiring that triggers it from the presence-dial selection is not yet built. The result: you CAN call the API directly, but there is no UI surface that starts the walkthrough automatically when you select the mode.

**4. The review/walkthrough/guide backend does MOVE the surface** — partially confirmed.

`present_current` returns `ui_target` (the address of the current step). `_registry_ui_target(payload)` — Observed(suite.py:6161) — resolves the address to a registry-valid FE target. The FE's `resolveUiTarget` consumes this to drive the camera or spotlight the DOM element. The T0-KEYSTONE is noted — Observed(suite.py:6266): "STAMP a registry-valid `ui_target` INTO the payload the FE reads as `session.raw.ui_target`... before this fix nothing wrote a payload-level ui_target, so the FE's per-step view-drive... was ~always undefined → the keystone... silently no-op'd." The backend now stamps the target. Whether the FE wires it is a separate question (noted as "needs-tim until the FE drive is verified by use").

---

## 7 · What the addressed surface looks like for the guided-review context — composing the picture

### The full auto-resolution flow for a locus

When the operator clicks `ui://inbox/build-review` (an element in a mockup or the live app):

1. `focus.selected` carries `"ui://inbox/build-review"` to `/api/chat`
2. `_chat_context` detects the `ui://` prefix → sets `current_locus = "ui://inbox/build-review"` (R1)
3. Injects `"OPERATOR IS INDICATING... clicked ui://inbox/build-review (description from registry)"`
4. R2 gathers context: annotations at `ui://inbox/build-review`, `ui://inbox`, (and region root), chats at those addresses, addressed events, the `howto` text for `ui://inbox/build-review`, any learned presentation prefs
5. R2 scores all gathered items: recency × proximity × semantic relevance to the current message intent
6. Caps at 4000 chars and injects `"CONTEXT RESOLVED AT YOUR LOCUS... bounded by relevance/recency decay"`
7. The RHM answers in that full context

As the operator talks and clicks through a sequence, annotations accumulate at loci. Each subsequent turn at the same locus gets a richer R2 context. **The backend resolves context whenever a `ui://` locus is set; the open dependency is whether the live surface SETS one.**

Two precision corrections (verified after the first draft):
- **`current_locus` IS set in the live `_chat_context`** — Observed(suite.py:2142): `self._current_locus = indicated[-1]`, where `indicated` is the `ui://`-prefixed members of `focus.selected`. And the studio FE DOES ship `ui://` addresses in `focus.selected` — Observed(StudioKit.tsx:219-220: "sendChat → POST /api/chat with focus={selected:['ui://…']} — the focus→locus→context channel"). So in the STUDIO context the locus IS fed and R2 fires live. In the general canvas app, I1 (widen focus beyond node-ids) + F4 (DOM `data-ui-ref`) are still ☐ in the criteria — so outside the studio, the R2 spine is built + unit-tested but DORMANT until those land.
- **Ordinary `chat()` does NOT stamp `address` onto its chat turn** — Observed(suite.py:5200-5201): the `append_chat` calls in `chat()` carry role/text/grade/source but NO `address`. Only the explicit operator mark-up paths (`ingest_comment` :4321, `attach_chat` :4513) stamp it. So `chats_at(locus)` is EMPTY for normal conversation — "the RHM always knows what's been said here" holds ONLY for content the operator explicitly annotated/attached at that address, not for free-flowing chat. The conversation does not self-record at the locus unless mark-up is captured. This is a real gap for the anchor's "as you talk, things get marked up at their addresses."

### What doesn't close yet for the guided-review surface

| Capability | Status | Evidence |
|---|---|---|
| `annotate` by operator via `/api/annotate` | ✅ Built | Observed(bridge.py, suite.py:4263) |
| R2 auto-context at locus | ✅ Built | Observed(suite.py:2812-3086) |
| Ancestor group-addressing | ✅ Via tree | Observed(suite.py:2556) |
| Presentation pref learning | ✅ Built | Observed(suite.py:4391-4450) |
| `context_at` / `/api/context` | ✅ Built | Observed(suite.py:3088) |
| `start_guide` / `start_walkthrough` | ✅ Built | Observed(suite.py:6287-6479) |
| RHM calling `annotate` mid-conversation | ❌ Not in whitelist | Observed(suite.py:RHM_VERBS) |
| FE show-me lane (dial → guide start) | ❌ Deferred | Observed(suite.py:6313) |
| FE per-step view-drive (resolveUiTarget live) | ⚠️ needs-tim | Observed(suite.py:6266) |
| Altitude-rich narration for all elements | ⚠️ Corpus howto coverage incomplete | Inferred from GUIDE_SEQUENCES/address_help |
| Mockup element → `ui://` address annotation routing | 🔧 Gap | Observed(`mockup://` ≠ annotatable; element-map.json exists as bridge) |
| Comment ON a group (parent→child inheritance) | ✅ Via ancestor-walk | Observed(suite.py:2556) |
| VIEW a group (descendant rollup of members' marks) | ❌ Not built (ancestor-walk is upward only) | Observed(suite.py:2556) |
| Batch annotation (multi-address in one call) | ❌ Not built | Observed(annotate signature: one address) |
| Generating plans from accumulated mark-up | ❌ Not wired | Anchor-idea; `surface_intent_at` exists as building block |

---

## 8 · Contradictions and stress-tests of the anchor

### "mark up as you talk — the RHM does it for you"

**Contradicted.** The RHM CANNOT call `annotate` — it is not in `RHM_VERBS`. What exists: `request_change` routes a conversational change-request to `surface_intent_at` which calls `ingest_comment` inside it — but that is scoped to minting build-intents, not arbitrary mark-up. The gap is well-defined and the fix is well-defined (add `annotate` to the verb whitelist with `current_locus()` as the default address).

### "tags on a GROUP (not just a single element)"

**Partially contradicted, and the contradiction is DIRECTIONAL.** There is no explicit group-annotation primitive. The address tree gives group semantics ONE WAY only: a comment on a parent (`ui://inbox`) flows DOWN into every child's R2 context (parent→child inheritance, via the upward ancestor-walk at resolution time). But the REVERSE — standing at a group address and seeing all comments on its descendants — is NOT supported: `_r2_ancestors` walks upward only (suite.py:2556), so a group locus sees only its own + its ancestors' comments, never its children's, and siblings never share. So "comment ON a region" works; "review a region and see all marks on its parts" does NOT, and is net-new (a descendant-gather). The anchor's framing is right in spirit for the comment-down case, wrong for the view-up case.

### "context auto-resolves at each address so it always knows where you are and what's been said"

**Confirmed and stronger than the anchor.** R2 is fully operational with five scoring dimensions (recency, proximity, pin, semantic, presentation-pref), a hard 4000-char budget cap, mode-parameterizable stratum filtering, and deduplication of the triple-counted comment. The `current_locus` persists across turns and the context injected at each turn is genuinely the accumulated history at that locus.

### "the `ui://` grammar (contracts/address.py)"

**Correction.** The grammar itself lives in `contracts/ui_info.py`, specifically `parse_ui_address` — Observed(contracts/ui_info.py:194). `contracts/address.py` defines the SCHEMES list and the `Provenance` model for run/cas/blob/vec — `ui://` is listed there as a scheme but the grammar validation is entirely in `ui_info.py`. This is not a contradiction but a precision: the anchor's reference to `contracts/address.py` is incomplete.

### "the mockup corpus directory structure — screens broken into directories, a pattern"

**Expanded.** The pattern is richer than implied. It is a three-layer system: area (A–G letters = functional zones), view-variant (desktop/mobile/responsive), and journey cross-links in `register.json`. The directory structure reflects the area taxonomy, not the journey graph directly. The journey graph is carried by `register.json`'s `sequences[]` and by `GUIDE_SEQUENCES` in `suite.py`. Each mockup element carries `data-ui-ref` so it participates in the address registry.

### "how does an address tell which [mockup vs live]"

**Fully resolved.** The distinction is: `mockup://` = reading context (the RHM reads the file). `ui://` = the annotatable coordinate (the element's address, same whether in the mockup HTML or the live app DOM). The annotation is address-keyed, not surface-keyed. A comment on `ui://inbox/build-review` is the same record whether the operator clicked it in the mockup or the running app. For truly net-new elements (not yet in the live app), the annotation lives at the `ui://` address which exists in the corpus but has no live DOM counterpart — the annotation persists and will resolve when the element is built.

---

## 9 · What this means for the guided-review surface — building-block inventory

The surface the anchor describes (live guided conversation that walks the commander through screens, marks things up, and generates plans) has most of its building blocks already present:

**READY (observable, working):**
- `start_guide(topic)` — system-initiated guided sequence over `ui://` addresses, model-free narration from corpus
- `start_walkthrough(item_ids)` — operator-triggered guided walk over inbox items
- `present_current(session_id)` — per-step narration (corpus howto) + `ui_target` for view-drive
- `next(session_id)` / `respond(session_id)` — NEXT/BACK / verdict
- `_resolve_context_at` / R2 — context auto-resolves at every locus, bounded and scored
- `ingest_comment` / `annotate` — mark-up via the operator face
- `set_presentation_pref` — adaptation/learning
- `request_change` (RHM verb) → `surface_intent_at` → build-intent for approval
- `context_at(address)` / `/api/context` — standalone context inspector
- `mockup://` in focus → RHM reads the mockup and explains it

**NEEDS WIRING or is DEFERRED:**
- FE show-me lane (dial-select → `start_walkthrough` → per-step `resolveUiTarget` spotlight)
- RHM calling `annotate` mid-conversation (add to whitelist, use `current_locus()` as default)
- Accumulating conversation mark-up → generating plans (the "generate" step in the anchor)
- Altitude-appropriate narration for all elements (requires authoring `howto` in `addresses.json` OR using the model/coa for mockup elements)
- Voice-in (STT → chat → RHM response loop) — exists in voice infrastructure but not wired to the walkthrough

**NOT BUILT (net-new):**
- The guided sequence as a conversational walkthrough (vs. the current cursor-driven review organ)
- Live dialogue model for "talks back" at each stop (the current organ is request/response, not streaming)
- Generating plans from accumulated mark-up (accumulate → compose → show → approve batch)
- Explicit multi-address batch annotation

The make-or-break question the anchor posed — is the live guided experience achievable with the existing machinery? — the honest answer is: the backbone (sequence engine, context resolution, mark-up, view-drive) is built. What is not built is the LIVE CONVERSATIONAL mode (streaming, interruption, voice-in) and the GENERATE step (composing plans from the conversation). These are real gaps that need new building, not just wiring.

---

*Findings written to `/home/tim/company/build-prep/guided-review-surface/findings/AREA-3-addressed-surface.md`*
