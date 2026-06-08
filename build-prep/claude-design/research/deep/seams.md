# Deep Seam Contracts — Backend Integration Surface

> **Read-only mine of `~/company` (commit state 2026-06-08).**
> Builds on `claude-design/findings/capability-map.md` — go deeper on the seams that map is thin on.
> Status legend: `BUILT+REACHABLE` · `BUILT-NO-FE` · `DESIGNED-NOT-BUILT`.

---

## ⚠ HEADLINE — the task's "net-new / DESIGNED-not-built" premise is mostly wrong

The task lists **I2 `/api/act`, R2, I4, R1, L1 `/api/intent-at`** as net-new seams to characterize as DESIGNED-not-built. **The code says 4 of those 5 are already BUILT.** Claude Design must NOT plan to build them — they exist:

| Seam | Task's framing | Reality (file:line proof) |
|---|---|---|
| **I2 — `/api/act`** | net-new | **BUILT+REACHABLE** — `suite.py:3974` + `bridge.py:1224` |
| **I4 — address→tier gate** | net-new | **BUILT** inside `act`, `suite.py:4007-4030` (`_tier_for_address` @3962) |
| **R1 — backend-held locus** | net-new | **BUILT** — session-persistent `self._current_locus`, `suite.py:322,2031,2302` |
| **L1 — `/api/intent-at`** | net-new | **BUILT+REACHABLE** — `suite.py:6642` + `bridge.py:1025` |
| **R2 — context-at-address** | net-new | **ENGINE BUILT** (`_resolve_context_at` @2925, runs inside every chat); the **standalone `GET /api/context?address=` route is the ONLY genuine gap** |

**The two real gaps** (DESIGNED-NOT-BUILT): (1) a standalone `GET /api/context?address=` route to call R2 without firing a chat turn; (2) an R2-knob **setter** route (`composition_config` is read-only). Everything else in the net-new list is shippable today by wiring the FE to existing routes.

---

## 0. Address Grammar (the through-line)

### `contracts/address.py` — the canonical scheme set

```
run://<graph>/<node>@<branch>[#run=<id>]     mutable run-time pointer (store resolves)
cas://<algo>:<hash>                           immutable content (integrity + dedup)
blob://<algo>:<hash>                          large binary (addressed, not inlined)
vec://<source-address>#emb=<model>            an embedding of another address
ui://<kind>/<ref>                             a UI element (resolved by ui_info registry, NOT the store)
code://<file-stem>/<symbol>                   a code symbol (resolved by resolve_scope + corpus)
```

`scheme(addr)` — returns the scheme string or None. Used for fail-loud gates everywhere:
- `annotations_at`, `chats_at`, `attach_chat`, `annotate` → raise if not `ui://`
- `ref_versions`, `stale_at_address` → raise if not `run://`

### `ui://` grammar detail (`contracts/ui_info.py:194–217`)

Three legitimate forms — all parse:
- region form:  `ui://chrome/inbox`
- element form: `ui://inbox/build-review`
- corpus region-only: `ui://inbox`

`parse_ui_address(addr)` is the S0 grammar gate — raises on malformed. It is the first call in every address-keyed method. A malformed address propagates as a 400 to the client via bridge.py's try/except.

---

## 1. `resolve_scope` — the `ui://` → `code://` → files join

**Location:** `suite.py:7665`
**Route:** `GET /api/scope?address=<ui://>` · `BUILT+REACHABLE`

**Contract:**
- In: `ui_addr` (validated S0, raises on malformed)
- Out: `{address, symbols:[code://…], scope:[file,…], stale:bool, note:str}`
- Reads: `design/_system/code-symbols.json` (NOT the raw `addresses.json`)
- Method: inverts the `referenced_by[]` field — collects every registry symbol that lists this `ui://` in its `referenced_by`, gathers the `file` field from each

**Guarantees:**
- Empty scope → DENY-ALL downstream (an unmapped address is never a license to build anywhere — rule 8)
- `stale:True` when the corpus JSON can't be read — legible, never a crash
- An orphan / CSS-selector / unlisted address returns empty scope with a legible `note`

**How `resolve_scope` maps `ui://` → `code://` → files:**
```
ui://canvas/run-button
  ↓ (code-symbols.json referenced_by inversion)
code://App/RunButton, code://scheduler/trigger_run
  ↓ (each entry's resolved `file` field)
["canvas/app/src/App.tsx", "runtime/scheduler.py"]
```

This result is what gates every build-intent (empty scope = DENY-ALL at dispatch time via `_in_any_scope`).

---

## 2. `chat` — the focus→locus→context-at-address channel

**Location:** `suite.py:5049`
**Route:** `POST /api/chat` (body: `{message, graph_id, focus?}`) · `BUILT+REACHABLE`

**Contract:**
- In: `message:str`, `graph_id:str`, `focus?:{selected:[...]}` where each selected item is a node-id or `ui://` address
- Out: `{reply, action, mode, model, history}`
- Fail-loud: a non-tool-capable model is refused with no model call, no fallback (`suite.py:5053`)

**The focus → locus → context channel (the studio's missing wire):**

```
POST /api/chat {focus: {selected: ["ui://canvas/run-button"]}}
  ↓
_chat_part_core → _chat_context(graph_id, focus, intent=message)   (suite.py:1902)
  ↓
I1 (suite.py:2012-2014): split focus.selected into
    indicated = [s for s in selected if s.startswith("ui://")]   (clicked addressed elements)
    selected  = [node-ids in the live graph]                      (canvas co-presence — preserved)
  ↓
R1 (suite.py:2031): if indicated → self._current_locus = indicated[-1]   (LAST-WINS)
    — BACKEND-HELD + SESSION-PERSISTENT: it is an instance attr (suite.py:322), NOT re-derived
      per turn. A turn with ONLY a node-id (or no focus) leaves the prior locus INTACT (no clobber).
      A malformed ui:// RAISES before this line (S0 gate in _describe_ui_address) — never held unvalidated.
  ↓
R2 (suite.py:2061-2063): _resolve_context_at(self.current_locus(), graph_id, intent=message,
                                              resolution=resolution_spec_for(mode))
    — R2 reads the HELD locus via current_locus() (suite.py:2302), NOT focus directly. The focus
      SETS the locus (R1); R2 CONSUMES it. This is the I7-left-unwired seam now closed.
  ↓
_r2_gather (suite.py:2701): collects annotations + chats + addressed events at the locus + ancestors;
    bridges ui://canvas/<node> → run://<graph>/<node> for version-history (X6)
  ↓
_r2_score_and_cap (suite.py:2892): scores each item, sorts, caps to R2_BUDGET (see §2.1 for the formula)
  ↓
Injects the bounded slice as "CONTEXT RESOLVED AT YOUR LOCUS" into the RHM's system prompt
  ↓
chat() reply is grounded in live truth AT the element the operator clicked
```

**What R2 gathers at the locus** (`_r2_gather`):
- Annotations from `annotations.jsonl` at `address` and ancestors (proximity decay up the `ui://` tree)
- Chat turns from `chat.jsonl` where `rec.address == address` and ancestors
- Howto from the UI_REGISTRY row
- Addressed events from `events.jsonl` where `event.address == address`
- Version history from `run://<graph_id>/<node>` if the locus is `ui://canvas/<node>` (X6 bridge)

**R2 scoring** (verified `_r2_score`, `suite.py:2411-2443`):
```
recency   = exp(-R2_LAMBDA * age_seconds)                          # newer = heavier; unparseable ts → 0
proximity = address_tree_distance(locus, item.address)            # # of ui:// tree hops between them
semantic  = cosine(embed(intent), embed(item.text))  ∈ [-1,1]     # X13; embedder-down → 0 + warning
pin_bonus = R2_PIN_WEIGHT if item.pinned else 0.0

score = recency * (1 / (1 + R2_PROXIMITY_WEIGHT * proximity)) + pin_bonus + R2_SEMANTIC_WEIGHT * semantic
```
Items sorted by score, capped to `R2_BUDGET`. The weights (`R2_LAMBDA`, `R2_PROXIMITY_WEIGHT`, `R2_PIN_WEIGHT`, `R2_SEMANTIC_WEIGHT`, `R2_BUDGET`) are `composition_config` knobs, readable at `GET /api/capabilities` → `composition_config`. Exposed READ-ONLY; no setter route exists (**setter is DESIGNED-NOT-BUILT**).

**Staged variant `chat_parts`** (`suite.py:5090`): A generator yielding parts — used by the voice stream (`/api/voice/stream`). Shares the same prologue/core/epilogue as `chat()`, with a C4.3 brevity bypass (trivial turns skip the swarm). Each yielded part is `{part, text, final, staged}`.

---

## 3. `address_help` — the composed affordance bundle

**Location:** `suite.py:2102`
**Route:** `GET /api/address-help?address=<ui://>` · `BUILT+REACHABLE`

**Contract:**
- In: `ui_addr` (S0 validated)
- Out: `{address, what_this_is, how_to_change:{scope,blast_radius,note}, how_to_use, legs_present:{what_this_is,how_to_change,how_to_use}, presentation_pref?, presentation_directive?}`

**Three legs:**
1. `what_this_is` — `_describe_ui_address` → registry row's human title / `represents` feature-id
2. `how_to_change` — `resolve_scope` → `blast_radius` (X9/X14: co-reference + structural dependents/dependencies + semantic neighbours from corpus)
3. `how_to_use` — `_registry_howto_for` → the authored affordance text (None when unauthored)

**F1 adapt step:** After composing the bundle, `presentation_pref_at(address)` is consulted. If a stored pref exists, `_apply_presentation_pref` applies it structurally (model-free for `lead_with:how_to_change` — re-orders legs; framing directive for `terser`/`more`/`shape` — threaded into the prompt wording). The adapted bundle carries `presentation_pref` + `presentation_directive` for the FE to render a "learned" marker.

**Degrade-clean rule:** a missing leg carries its own `note` / `None`, never crashes the bundle. `legs_present` flags which legs resolved. A well-formed-but-unregistered address returns `what_this_is = "(unregistered)"` and `legs_present.what_this_is = false`.

---

## 4. `annotate` / `ingest_comment` / `annotations_at`

### `annotate` (pure I6 leaf)
**Location:** `suite.py:4110`
- In: `{address:ui://, text:str, source?:str}`
- S0 gate first. Fails loud on empty text.
- Writes: `annotations.jsonl` keyed by `address` via `store.append_annotation`
- Emits: `annotation` event addressed at `address` (S2)
- Returns: the annotation record `{kind, address, text, source, ts}`

### `ingest_comment` (L4 — the wired production entry)
**Location:** `suite.py:4138`
- Composes `annotate` (pure I6 leaf) + one additive `append_chat` with `address` field
- The `append_chat` lands `role/source/grade` via `_provenance_source`/`_provenance_grade`: operator comment → `user/operator/gold` (trains the twin, LOCATED); non-operator → `assistant/twin/working` (NEVER trains — F4 guard)
- Does NOT emit a second addressed event (annotate already did — avoids double-stamping L3)
- **This is what `/api/annotate` (POST) routes through** — not the bare `annotate` leaf

### `annotations_at`
**Location:** `suite.py:4173`
**Route:** `GET /api/annotations?address=<ui://>` · `BUILT+REACHABLE`
- S0 gate, then `store.annotations_for(address)` + `_overlay_pins`
- Returns oldest-first; pins overlaid from `pins.jsonl`
- R2 reads this at the locus to build the context slice

**Route mapping:**
- `POST /api/annotate` → `SUITE.ingest_comment(addr, text, source)` · `BUILT+REACHABLE`
- `GET /api/annotations?address=` → `SUITE.annotations_at(addr)` · `BUILT+REACHABLE`

---

## 5. `attach_chat` / `chats_at`

### `attach_chat` (I7)
**Location:** `suite.py:4334`
- In: `{address:ui://, text:str, role?:str, source?:str}`
- S0 gate. Fails loud on empty text.
- Rides the EXISTING `append_chat` open record with ONE additive `address` field — no separate chat store
- Echo-guard: stamps `source` + `grade` from `_provenance_source`/`_provenance_grade`
- Emits: `chat` event addressed at `address` (S2)
- Returns: the chat record

### `chats_at` (I7 read)
**Location:** `suite.py:4366`
**Route:** `GET /api/chats?address=<ui://>` · `BUILT+REACHABLE`
- S0 gate, then `store.chats_for(address)` (filters open chat.jsonl by the additive `address` field) + `_overlay_pins`
- This is what R2 gathers at the locus (the `chat://` stratum)

**Route mapping:**
- `POST /api/attach-chat` → `SUITE.attach_chat(addr, text, role, source)` · `BUILT+REACHABLE`
- `GET /api/chats?address=` → `SUITE.chats_at(addr)` · `BUILT+REACHABLE`

---

## 6. `set_presentation_pref` / `presentation_pref_at`

### `set_presentation_pref` (F1 capture)
**Location:** `suite.py:4238`
- In: `{address:ui://, pref:{kind, arg?}, text?:str, source?:str}`
- S0 gate + pref validation (fail loud on unknown kind / missing required arg)
- Kinds: `terser | more | lead_with {arg} | shape {arg}` — one-source from `PRESENTATION_PREFS` dict (`suite.py:4210`)
- Rides `annotations.jsonl` with `kind:"presentation_pref"` marker — append-only, latest-wins
- Emits: `presentation_pref` event addressed at `address` (distinct from `annotation` event)
- DELIBERATELY does NOT call `ingest_comment` (pref is a control signal, not twin gold)

### `presentation_pref_at` (F1 consult)
**Location:** `suite.py:4276`
**Route:** `GET /api/presentation-pref?address=<ui://>` · `BUILT+REACHABLE`
- Latest-wins read over `annotations_for(address)`, filtered for `kind:"presentation_pref"`
- Re-validates on read (fail loud on a stored junk pref — never silent degradation)
- Returns `{kind, arg}` or `null`

**Route mapping:**
- `POST /api/presentation-pref` → `SUITE.set_presentation_pref(addr, pref, text, source)` · `BUILT+REACHABLE`
- `GET /api/presentation-pref?address=` → `SUITE.presentation_pref_at(addr)` · `BUILT+REACHABLE`

---

## 7. `up_translate` — the altitude transform

**Location:** `suite.py:5682`
**Route:** `GET /api/up-translate?kind=<kind>&ref=<ref>` (for address/decision) · `BUILT+REACHABLE`

**Contract:**
- In: `kind ∈ {address, decision, finding, event}`, `ref` is the artifact handle
- Out: `{kind, ref, lead:str, mechanism:dict, legs_present:{...}, grounded:bool, degraded:bool, note:str}`
- Fail loud on unknown kind (rule 8 — never guess)

**Kind dispatch:**
- `address` → composes `address_help(ref)`, maps 3 legs into `lead`/`mechanism` + F1 adapt step (pref rides through from `address_help`'s `b["presentation_pref"]`)
- `decision` → composes `coa(ref)`, maps framing/raw into `lead`/`mechanism`
- `finding` → frames from a supplied finding dict; enriches mechanism with `blast_radius` if the finding carries a `ui://` address
- `event` → frames from a supplied event dict; mechanism is the raw event

**GET route** covers `address` and `decision` (the two string-keyed kinds). `finding`/`event` take a dict — those are a future POST lane (noted in bridge.py comment at line 374).

---

## 8. `_registry_ui_target` — the walkthrough view-drive keystone

**Location:** `suite.py:5987`
**Purpose:** Derives a REGISTRY-VALID `ui://` target for a review item's payload so the walkthrough's `resolveUiTarget` on the FE can navigate to the thing the step concerns.

**Logic (deterministic, never invents):**
1. If `payload["ui_target"]` or `payload["guide_address"]` is a registered `ui://` element address → use it
2. Else if `payload["node"]` exists → `ui://canvas/<node-id>`
3. Else → `ui://chrome/inbox`

Every branch returns a ref present in `UI_REGISTRY`. Used by I4 (`act`) when surfacing a CONFIRM/LOCKED-tier command — the surfaced inbox item carries the clicked `ui://` address as `ui_target` so clicking the inbox item drives the view back to the element awaiting approval.

---

## 9. `address_view` — the element's addressed history

**Location:** `suite.py:9368`
**Route:** `GET /api/address-history?address=<ui://>` · `BUILT+REACHABLE`

**Contract:**
- In: `address` (S0 validated — `ui://` only)
- Out: `{address, trajectory:[...events in seq order]}`
- Reads the WHOLE event tail (`events_since(-1)`), filters `e.address == address`
- The addressed analogue of `decision_view` — both filter `events_since(-1)` but on different keys

---

## 10. `GET /api/stream` — the SSE event spine

**Location:** `bridge.py:510`, dispatches at `bridge.py:292`

**Protocol:**
- Response: `Content-Type: text/event-stream`, no Content-Length, keep-alive
- Each event: `id: <seq>\ndata: <json>\n\n`
- Cursor: `?since=<seq>` or `Last-Event-ID` header (default `-1` = from the start → gapless reconnect)
- Heartbeat: ~15s so idle proxies don't drop the socket

**Event record shape** (set by `store/fs_store.py:459`):
```json
{
  "seq": 42,
  "ts": "2026-06-08T10:00:00.000000+00:00",
  "kind": "annotation",
  "summary": "comment at ui://canvas/run-button: click me to...",
  "address": "ui://canvas/run-button",
  ...additional meta fields per kind...
}
```

**Key fields:**
- `seq` — monotonically increasing integer, used as the SSE cursor (T1-SEQ atomic lock in fs_store)
- `ts` — ISO timestamp (UTC)
- `kind` — the event type (annotation / chat / presentation_pref / run / create / connect / delete / warning / decision.verify / op.run / cognition.wave / ...)
- `summary` — human-legible one-liner
- `address` — the `ui://` or `run://` address the event concerns (S2: ~20 emit sites stamp this — it is the routing key for the FE's address-routed render law)

**FE render law:** the surface re-renders from the stream at the address the event carries. It does NOT own state. `address` is how the FE routes a live event to the element it concerns.

---

## 11. Net-new seams — DESIGNED vs BUILT status

### I2 — `/api/act` (click-emission seam)
**Route:** `POST /api/act` · **BUILT+REACHABLE** (`bridge.py:1224`, `suite.py:3974`)

**Contract:**
- In: `{verb:str, graph_id:str, address?:str, args?:dict}`
- Out: `{reply:str, action:dict, graph_id:str}` — same shape as `/api/chat`
- Fail loud on missing/empty verb

**What it does:** A structured `{verb, address, args}` from a human click drives `_dispatch_rhm_action` DIRECTLY (bypassing the model-prose parse `_parse_rhm_action`). Routes through `autonomous_dispatch` → the same governance posture as `chat()`'s decide-for-me path.

**I4 gate (address→tier) IS BUILT inside `act`** (`suite.py:4007–4030`): before verb-class governance, `_tier_for_address(address)` looks up the address's `tier` in the UI_REGISTRY union record. If `posture(tier) != AUTO` → surfaces for approval (does NOT dispatch); carries `ui_target` in the surfaced payload for the walkthrough view-drive. The verb-class fallback (AUTO/CONFIRM) applies when no address-tier is found.

**Status:** BUILT. The FE must send `POST /api/act {verb, graph_id, address, args}` on a click to use it.

---

### R2 — `/api/context?address=` (context-at-address standalone route)
**DESIGNED-NOT-BUILT** — there is no `GET /api/context?address=` route in bridge.py.

**What exists vs the gap:**
- BUILT: `_resolve_context_at(locus, graph_id, intent, resolution)` at `suite.py:2925` — the R2 engine
- BUILT: R2 runs INSIDE `_chat_context` on every `/api/chat` call when a `ui://` locus is in `focus.selected`
- NOT BUILT: a standalone route to call R2 for a given address without firing a full chat turn

**The gap this creates for Claude Design:** a review surface that wants to SHOW the context bundle at an element (without asking a question) has no direct call. The workarounds are:
  - Call `GET /api/address-help?address=` (gives the corpus-side context: what_this_is / how_to_change / how_to_use)
  - Call `GET /api/annotations?address=` + `GET /api/chats?address=` separately (gives the operator-side context threads)
  - Fire a minimal `POST /api/chat` with `focus.selected` and a sentinel message (reaches R2 but has overhead)

**The net-new seam that would fill it:** `GET /api/context?address=<ui://>` → calls `_resolve_context_at(locus=address)` directly and returns the bounded, scored, R2-composed context block. Not built; the capability is reached only via chat.

---

### I4 — address→tier governance gate
**BUILT inside `act`** (not a separate route) — see I2 above. `_tier_for_address` (`suite.py:3962`) reads the `tier` field from the UI_REGISTRY union record (the 6th element of each row). A missing tier → verb-class fallback (AUTO). A `CONFIRM`/`LOCKED` tier → surfaces for approval, never dispatches.

---

### R1 — backend-held locus
**BUILT** (not a route — it's session-persistent backend state that `chat()` sets and reads).

The locus is **held backend-side** as `self._current_locus` (instance attr, initialized at `suite.py:322`). It is SET in `_chat_context` (`suite.py:2031`): when `focus.selected` carries one or more `ui://` addresses, `self._current_locus = indicated[-1]` (LAST-WINS on a multi-select). It is READ via the `current_locus()` getter (`suite.py:2302`), which R2 calls.

Two corrections to the naive reading:
- **It IS persisted across turns within a session** (it is not re-derived per call). A turn carrying ONLY a canvas node-id (or no focus) leaves the prior locus INTACT — `self._current_locus` is only overwritten when a new `ui://` is indicated (guarded by `if indicated:`).
- **R2 reads the HELD locus, not `focus` directly.** The `focus` field SETS the locus (R1); R2 consumes `current_locus()`. A malformed `ui://` raises (S0 gate) before it can be held — the locus is never unvalidated.

There is no separate "set locus" route — setting rides the `focus` field of `POST /api/chat`. (Session-scoped, in-memory, single-operator, same as `_current_thread`.)

---

### L1 — `/api/intent-at` (comment → build-intent)
**BUILT+REACHABLE** (`bridge.py:1025`, `suite.py:6642`)

**Contract:**
- In: `{address:ui://, text:str, source?:str, consequence_class?:str, why?:str}`
- Out: `{id, intent, scope, consequence_class, address, stale:bool, note:str}`
- Composes: `ingest_comment` (I6, records the comment as gold label) + `resolve_scope` (S3, derives the code scope from the address) + `surface_build_intent` (mints the build-intent as a live escalation, `resolved=None`)
- Empty scope = DENY-ALL (propagated from S3, never fabricated)
- Only SURFACES for approval — never dispatches. Approval via `POST /api/resolve`. Dispatch-on-approve is L2 (a separate wire, not this route).

---

### I5 — `route_click` (annotate-vs-operate router)
**BUILT** at `suite.py:4051` — no standalone route yet; used internally.

Routes: `ui://` + no consequential verb → `annotate` (I6); `run://` click → `act` (I2/I4); any click with a consequential verb → `act` (verb makes it an operation regardless of scheme). Fail loud on empty annotate text.

---

## 12. The focus→locus→context-at-address channel (summary)

```
FE click on a ui:// element
  ↓
POST /api/chat {message, graph_id, focus: {selected: ["ui://canvas/run-button"]}}
  ↓  (bridge.py:923)
SUITE.chat(message, graph_id, focus)  (suite.py:5049)
  ↓
_chat_part_core → _chat_context(graph_id, focus, intent=message)  (suite.py:1902)
  ↓
_chat_context: SETS self._current_locus = (last ui:// in focus.selected)   (R1, last-wins, held)
builds WHOLE-INTERFACE ground truth (models, modes, verbs, graphs, inbox)
calls _resolve_context_at(self.current_locus(), graph_id, intent=message)  (R2 reads the HELD locus)
  ↓  (R2 engine)
_r2_gather(locus, graph_id):
  annotations at locus + ancestors   (annotations.jsonl, proximity decay)
  chat turns at locus + ancestors    (chat.jsonl, additive address field)
  howto from UI_REGISTRY row
  addressed events at locus          (events.jsonl)
  version history at run://graph/node if locus is ui://canvas/<node>  (X6)
  ↓
_r2_score_and_cap(items, locus, intent=message):   (verified suite.py:2411-2443)
  recency   = exp(-R2_LAMBDA * age_seconds)
  proximity = address_tree_distance(locus, item.address)
  semantic  = cosine(embed(intent), embed(item.text))   (X13; embedder-down → 0)
  score = recency * (1/(1 + R2_PROXIMITY_WEIGHT*proximity)) + (R2_PIN_WEIGHT if pinned else 0)
          + R2_SEMANTIC_WEIGHT * semantic
  sort by score, cap to R2_BUDGET
  ↓
"CONTEXT RESOLVED AT YOUR LOCUS (…):\n  · …\n  · …"
injected into the RHM system prompt as a distinct section
  ↓
Model sees: live system state + locus context slice + the operator's message
Model replies grounded in truth at the element the operator clicked
```

**No `focus` = no locus = no R2 context injection** (the string is empty, cleanly skipped). This was the studio's missing channel: elements had no `ui://` address, so `focus.selected` was never populated.

---

## 13. Built seam contract list

| Seam | Method | Route | Inputs | Outputs | Event emitted | Surface need |
|---|---|---|---|---|---|---|
| **chat** | `suite.py:5049` | `POST /api/chat` | `{message, graph_id, focus?}` | `{reply, action, mode, model, history}` | `chat` (at locus) | Conversational organ |
| **chat_parts** | `suite.py:5090` | (via `/api/voice/stream`) | same + streaming | yields `{part, text, final, staged}` | `cognition.*` | Staged/voice reply |
| **address_help** | `suite.py:2102` | `GET /api/address-help?address=` | `address:ui://` | `{address, what_this_is, how_to_change, how_to_use, legs_present, pref?}` | — | "What can I do here?" panel |
| **annotate** (via ingest_comment) | `suite.py:4138` | `POST /api/annotate` | `{address, text, source?}` | annotation record | `annotation` | Comment at element |
| **annotations_at** | `suite.py:4173` | `GET /api/annotations?address=` | `address:ui://` | `[{kind, address, text, source, ts, pinned}]` | — | Comment thread panel |
| **attach_chat** | `suite.py:4334` | `POST /api/attach-chat` | `{address, text, role?, source?}` | chat record | `chat` | Attach turn to element |
| **chats_at** | `suite.py:4366` | `GET /api/chats?address=` | `address:ui://` | `[{role, text, address, source, grade, ts, pinned}]` | — | Chat thread at element |
| **set_presentation_pref** | `suite.py:4238` | `POST /api/presentation-pref` | `{address, pref:{kind,arg?}, text?}` | pref record | `presentation_pref` | F1 learning loop capture |
| **presentation_pref_at** | `suite.py:4276` | `GET /api/presentation-pref?address=` | `address:ui://` | `{kind, arg}` or `null` | — | F1 adapt read |
| **up_translate** | `suite.py:5682` | `GET /api/up-translate?kind=&ref=` | `kind ∈ {address,decision}`, `ref` | `{kind, ref, lead, mechanism, legs_present, grounded, degraded, note}` | — | Altitude transform |
| **resolve_scope** | `suite.py:7665` | `GET /api/scope?address=` | `address:ui://` | `{address, symbols, scope, stale, note}` | — | ui://→code→files join |
| **address_view** | `suite.py:9368` | `GET /api/address-history?address=` | `address:ui://` | `{address, trajectory:[events]}` | — | Element history audit |
| **act** (I2+I4) | `suite.py:3974` | `POST /api/act` | `{verb, graph_id, address?, args?}` | `{reply, action, graph_id}` | (via dispatcher) | Structured click emission |
| **surface_intent_at** (L1) | `suite.py:6642` | `POST /api/intent-at` | `{address, text, source?, consequence_class?, why?}` | `{id, intent, scope, address, stale, note}` | — | Comment → build intent |
| **SSE stream** | `bridge.py:510` | `GET /api/stream?since=` | `since:int` or `Last-Event-ID` | `text/event-stream` `id:<seq>\ndata:<json>` | — | Live event spine |

---

## 14. Net-new seams: what exists vs the gap

| Seam | Route | Status | What exists | What's missing |
|---|---|---|---|---|
| **I2 — act** | `POST /api/act` | **BUILT+REACHABLE** | Full implementation incl. I4 address→tier gate | FE must wire clicks to this route |
| **I4 — address tier gate** | (inside act) | **BUILT** (no standalone route) | `_tier_for_address` + surfacing logic inside `act` | No separate route needed |
| **R1 — backend-held locus** | (inside chat) | **BUILT** (session-persistent state) | `self._current_locus` held backend-side (suite.py:322,2031,2302); set last-wins from `focus.selected`, read by R2 | No "set locus" route — rides `focus` on `/api/chat`; in-memory, session-scoped |
| **R2 — context-at-address** | `GET /api/context?address=` | **DESIGNED-NOT-BUILT** | `_resolve_context_at` is built and runs inside chat | Standalone route to call R2 without a full chat turn — not built |
| **L1 — intent-at** | `POST /api/intent-at` | **BUILT+REACHABLE** | Full compose: ingest_comment + resolve_scope + surface_build_intent | FE must wire "change this" comment flows to this |
| **R2 setter / knobs** | `POST /api/knobs` (write) | **DESIGNED-NOT-BUILT** | `composition_config` is exposed READ-ONLY in capabilities | No route to update R2 weights from a surface |
| **I5 — route_click** | (no route yet) | **BUILT** (internal only) | `suite.py:4051` full implementation | No bridge route yet; the FE must call `act` or `annotate` directly |

---

## Key findings for Claude Design

1. **The focus→locus channel** is the load-bearing connection a design surface needs. Elements must carry a `ui://` address; that address goes into `focus.selected` on `POST /api/chat`. Without it, the RHM has no locus, no R2 context, no grounded answers about "this element."

2. **R2 context-at-address has no standalone GET route.** A review panel wanting to SHOW context without asking a question must call `GET /api/annotations?address=` + `GET /api/chats?address=` + `GET /api/address-help?address=` to assemble the picture. Or fire a minimal chat. The gap is `GET /api/context?address=` (DESIGNED-NOT-BUILT).

3. **`POST /api/act` is the clean click emission seam.** A surface sending `{verb, address, args}` gets the same governance, confirmation, and reply shape as `/api/chat` — without going through the model-prose parse. Address→tier governance (I4) is already inside it.

4. **Every address-keyed write emits an addressed event** (`address` field on the event). The SSE stream carries those events. A surface that subscribes to `/api/stream` and filters by its displayed `ui://` address gets a live push of everything that happens at that element.

5. **`GET /api/address-help` is the single "what can I do here?" endpoint.** Three legs, F1 pref-adapted, degrades clean. Use this as the primary info source when the operator points at an element.
