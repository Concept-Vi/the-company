# Coverage Round — `area://substrate`
## contracts/ + store/ + fabric/ — full territory sweep

> **Sweep method:** Full territory, not a query. Every source file in contracts/, store/, and fabric/ read in full. Evidence marks follow the synthesis convention: **Observed (file:line)** = read directly · **Inferred** = pattern-matched, not execution-verified · **Unification-opportunity** = a gap, latent capability, or inconsistency the surface build would resolve or expose.
>
> Relations tagged by the four kinds from `BUILD-ADDRESS-MAP.md`:
> **(1) USE** — the surface composes this directly · **(2) TOUCH** — a contract/seam the surface changes or extends · **(3) UNIFY/IMPROVE** — a half-wired thing, a latent capability, an inconsistency the surface would activate or resolve · **(4) RELATE** — the Sequences primitive and conceptual kinship

---

## 1 · The address grammar — `contracts/address.py`

**Observed (contracts/address.py:32)**
```python
SCHEMES = ("run", "cas", "blob", "vec", "ui", "code")
```
Six schemes in the canonical set. The schemes `doc://` and `area://` — used right now in `BUILD-ADDRESS-MAP.md` as the coordinate system for this entire coverage round — are **NOT in SCHEMES**. They are working vocabulary in docs/build-prep but unregistered in the grammar.

**USE (1):** The surface uses `ui://` addresses everywhere — as walkthrough stop coordinates, as annotation keys, as locus identifiers for R2 context-resolution, as the registry lookup key for `_registry_ui_target`, and as the grammar gate (`parse_ui_address`) that every `annotate`, `ingest_comment`, `surface_intent_at`, and `address_help` call validates against. The address grammar is the floor the whole surface stands on.

**USE (1):** `contracts.address.scheme(addr)` and `is_cas(addr)` are the parse utilities. `scheme()` returns `None` for any unregistered scheme including `mockup://` — which means a `mockup://` address silently has scheme=None rather than failing loud. Observed (contracts/address.py:51-55).

**TOUCH (2):** The BUILD-ADDRESS-MAP.md itself proposes `doc://` and `area://` as a grammar extension and flags it as "a candidate unification (addresses-for-everything, the address system reaching its own build)" — Observed (BUILD-ADDRESS-MAP.md:10-13). Whether to formalize these is explicitly left as "a build decision." The surface build is the natural occasion to resolve it.

**TOUCH (2):** `mockup://` is already used as a working scheme in `suite.py:2086-2100` (the REVIEW WORKSPACE path parses `mockup://` strings by string-prefix, not through the grammar). It is NOT in SCHEMES. If the mockup-aware guided stop (Synthesis Bucket C-c) is built, `mockup://` will need a grammar home — either in SCHEMES or as a declared exception. The current silent-None treatment creates a latent inconsistency.

**UNIFY/IMPROVE (3):** Three scheme gaps exist simultaneously:
- `mockup://` — already in operational use (suite.py), not in SCHEMES
- `doc://` — proposed in BUILD-ADDRESS-MAP.md, not in SCHEMES
- `area://` — proposed in BUILD-ADDRESS-MAP.md, not in SCHEMES

These are not blocking issues today, but they are the same pattern: the address grammar is the Company's one coordinate system, and schemes are proliferating outside it. Adding them to SCHEMES is additive (address.py docstring says explicitly: "Adding it here is purely additive" — Observed contracts/address.py:16), schema-ver stays unchanged, and it would make the grammar self-describing of the full build vocabulary. This is a small, clean unification the surface build naturally surfaces.

**TOP UNIFICATION OPPORTUNITY in address.py:** Add `mockup` (already in operational use) + optionally `doc` and `area` to SCHEMES. One-line change. Makes the grammar self-consistent and gives `scheme(addr)` a truthful return for mockup addresses, which the mockup-aware stop (C-c) and the generate-for-mockups dispatch (C-a) will need.

---

## 2 · The `ui://` grammar and union record — `contracts/ui_info.py`

**Observed (contracts/ui_info.py:120-160):** S0 landed a full `parse_ui_address` / `UnionAddressRecord` / `normalize_capabilities` / `conform_corpus` / `conform_live` suite. The grammar is permissive-structural (any `ui://`-prefix + ≥1 segment + optional `/@state` parses). The record shape carries the semantic teeth: `kind` (the live resolver dispatch field), `region`, `capabilities` (bool-object), and optional join fields (`represents`, `code`, `howto`, `tier`).

**USE (1):** `parse_ui_address` is the S0 grammar gate called by every address-sensitive method in the suite: `annotate` (suite.py:4291), `ingest_comment` (suite.py:4263), `attach_chat` (suite.py:4487), `surface_intent_at` (suite.py:6816), the `_r2_ancestors` walk (suite.py:2562), and every `_describe_ui_address` call. Observed (suite.py:2194, 2241, 2319, 2391, 2562, 2608). The surface build routes every locus action through this gate — it is already active infrastructure.

**USE (1):** `UnionAddressRecord` is used by the suite at boot to load the corpus element addresses (suite.py:59-68), projecting each `addresses.json` entry to the union shape. The `howto` field on this record is the D1 foundational affordance stratum — the per-address authored text that `_r2_howto_at` reads and `address_help` joins as the how-to-use leg. Observed (contracts/ui_info.py:288-295).

**USE (1):** `Capabilities` Pydantic model (contracts/ui_info.py:43-55) defines the affordances the surface can offer at each address: `pointable`, `spotlit`, `presentable`, `openable`, `drivenReadOnly`. These are the five axes the guided surface uses when it drives the view to a stop. They are already declared per-address in the registry.

**TOUCH (2):** The `UnionAddressRecord.howto` field (contracts/ui_info.py:286-295) is explicitly the D1 foundational affordance text — "the help that resolves AT the locus." It is optional (a `None` default), and the synthesis confirms that addresses without authored `howto` degrade cleanly (the how-to-use leg of `address_help` is empty). The guided-review surface would populate this field as the mockup registration path (Synthesis D6-A: "Register intent at author-time — the mockup arrives annotated with what each surface is for"). When generate-for-mockups builds a new mockup, auto-populating `howto` in the resulting address record is the durable fix. **The field exists and is ready; the population path is what's net-new.**

**TOUCH (2):** S1 (inferred from `from_live` docstring at contracts/ui_info.py:340-370) grew the live registry with 24 corpus element addresses as full-string refs. The `from_live` method now handles both bare-ref rows and full-string rows. This means the registry is in a two-form state — not a problem, but the guided surface walkthrough (which keys on `ui://` addresses) needs to be aware that some entries arrive as bare-ref + kind-prefix and some as full-string region-first form.

**UNIFY/IMPROVE (3):** `validate_address_record` (contracts/ui_info.py:373-398) returns a LIST of problems rather than raising, so the conformance check can enumerate all failing addresses at once. However, the guided surface's `address_help` / `_describe_ui_address` path RAISES on the first failure. A batch conformance report (run `conform_corpus` + `conform_live` + diff the two address sets) would surface orphaned addresses (on one side only) and the `mockup://` addresses that are entirely absent from both registries. This batch check is a net-new build tool but one the surface would naturally trigger, since unregistered addresses are exactly the mockup-aware stop's challenge.

**RELATE (4):** The `howto` field on `UnionAddressRecord` is the Sequences primitive landing at the contract level: "resolve" = the address grammar gate, "present" = the how-to text, "persist" = write it at address. The surface, the cognition layer, and the tool layer all flow through the same record shape. That is the structural reason the surface is designed-general.

---

## 3 · The resolver protocol — `contracts/resolver.py`

**Observed (contracts/resolver.py:1-26):** The `Resolver` Protocol (C4) is minimal and clean: `put_content`/`get_content`/`exists` (cas://), `set_ref`/`head` (run://), `write_provenance`/`provenance`/`lineage`, `memo_get`/`memo_set`. Eight methods total. The docstring states explicitly: "The only thing that changes filesystem → Supabase."

**RELATE (4):** The Resolver is the Sequences primitive at the persistence layer: `resolve` = `head(logical)` → `get_content(cas)`, `persist` = `put_content(data)` → `set_ref(logical, cas)`. The surface's whole "generate → git-commit → revert-if-broken" wire lands here — the dispatch writes results through `set_ref`, the revert reads through `head` and `ref_history`.

**UNIFY/IMPROVE (3):** The Resolver Protocol does NOT include `append_event`, `append_annotation`, `chats_for`, `save_session`, `save_journey`, `append_pin`, `put_vector`, or any of the other FsStore methods that the guided-review surface uses heavily. These are FsStore-specific, not part of the C4 Protocol. If a Supabase backend were built, these methods would need to be added to the Protocol or split into a second Protocol. The surface build will exercise ALL of them (annotations at loci, chat at loci, journeys as navigation records, pins, vector index). This is a latent gap in the Protocol that the surface build makes visible. Not blocking today, but worth flagging: the Protocol is narrower than the surface's actual store contract.

---

## 4 · Node-type and node-record contracts — `contracts/node_type.py`, `contracts/node_record.py`

**Observed (contracts/node_record.py:30-37):** `EDGE_KINDS` = `{"data", "injection", "gate", "fan_in"}`. The `injection` kind is the cognition ref-read — a reply part reads a role's resolved `run://` output into its context. This is the mechanism the surface's live dialogue uses when the cognition layer injects context into a reply.

**USE (1):** `NodeInstance.status` (contracts/node_record.py:52-63) includes "surfaced" in the `Status` Literal (via `contracts/node_record.py:21`). A surfaced node is one that has been presented to the operator. The surface's review-session organ drives nodes through `idle → ready → running → ran → surfaced`. The status transition is the walkthrough's progress model.

**RELATE (4):** `NodeType.config_schema` and `inspector_schema` (contracts/node_type.py:28-33) are the fields the surface's node-configuration panel would expose. The guided surface, when it walks a node in the live app, needs to be able to explain what each config field DOES at a non-developer altitude — which maps directly to the `howto` field that should be part of the node-type's registered affordance. Currently there is no `howto` on `NodeType`. Inferred gap: the D1 foundational affordance stratum is on `UnionAddressRecord` (the UI address layer) but not on `NodeType` (the type layer). For the surface to explain a node at altitude, it needs help text that lives at the type level, not just the address level.

**UNIFY/IMPROVE (3):** `NodeType.extends` (contracts/node_type.py:23) is the type-graph relation (S4). The guided surface's ancestor walk (`_r2_ancestors` in suite.py:2556) climbs the `ui://` address tree, not the type graph. There is no parent-address-inherits-from-child-type relationship bridged yet. A group-level address (`ui://inbox`) and the node-types rendered within it are parallel hierarchies. The surface's group roll-up (Synthesis Bucket C-g) is a descendant-gather on the address tree; the type hierarchy is a separate axis. Both exist; neither speaks to the other. This is conceptually clean but worth naming: the two hierarchies (address tree for context, type graph for capability) are complementary, not competing.

---

## 5 · The object_info serializer — `contracts/object_info.py`

**Observed (contracts/object_info.py:61-85):** `build_object_info` serializes the C2 type library for the frontend: `{name: {title, category, kind, ports, config_schema, output_schema, render_set, inspector_schema, actions, version}}`. The fail-loud key/name mismatch check mirrors the same pattern in `build_ui_info`.

**TOUCH (2):** The guided surface will call `address_help` on a `ui://canvas/<node-id>` address. `_describe_ui_address` resolves that to the live node's type via `NodeType`, then reads `title`/`category`/`kind`/`config_schema`. But the `address_help` "what-this-is" leg is the NARRATED form — the model explaining what a Prompter node IS in plain language — not the raw schema. The `ObjectInfoEntry.inspector_schema` contains structured field descriptions, but there is no prose `howto` field on `ObjectInfoEntry` (paralleling the `UnionAddressRecord.howto` gap noted above). The live-app loop relies on `address_help`'s corpus narration; for node types, the narration is always LLM-generated (inferred, not registry-authored). This is not a blocking gap but a quality gap: authored `howto` on node types would make the narration deterministic and non-confabulatory for live-app nodes.

---

## 6 · The cognition_info serializer — `contracts/cognition_info.py`

**Observed (contracts/cognition_info.py:52-97):** `COGNITION_EVENT_KINDS` declares the per-turn lifecycle events the surface's live dialogue emits:
- `cognition.turn.start` carries `address: "ui://cognition/<turn>"`
- `cognition.role.fire` carries `address: "run://<turn>/<role>"`
- `cognition.inject` carries `address: "run://<turn>/<source>"`
- `cognition.part` carries `address: "ui://cognition/<turn>"`
- `cognition.turn.done` carries `address: "ui://cognition/<turn>"`

**USE (1):** These events are the live surface's narration substrate. When the RHM talks back, the surface listens to `cognition.part` events (streamed parts landing live in the panel) and `cognition.inject` events (injection edges lighting up in the cognition view). The guided surface's "feels live" depends on these event shapes being correct.

**TOUCH (2):** The addresses carried in cognition events use a `ui://cognition/<turn>` scheme — but `cognition` is not an `ADDRESS_KINDS` value (contracts/ui_info.py:163: `ADDRESS_KINDS = ("chrome", "field", "canvas", "panel", "ext")`). So `ui://cognition/<turn>` would FAIL `validate_address_record`'s kind check. This is a latent inconsistency: cognition events carry `ui://` addresses that the canonical record-shape would reject. The addresses are for live event routing/display, not for the corpus registry — so the failing check may be intentional — but it means the cognition locus addresses are NOT valid UnionAddressRecords. **Inferred gap:** a `cognition` kind should be added to `ADDRESS_KINDS` if the surface will ever annotate or comment at a cognition locus. Whether that is needed is a build decision.

**RELATE (4):** `COGNITION_EVENT_KINDS` is the emit-contract the FE binds to. The synthesis confirms `contracts/cognition_info.py` is the drift home for this contract (Observed runtime/AGENTS.md:261-265). The surface's live streaming leg (Synthesis Bucket B + C-d) will read these event kinds directly.

---

## 7 · The bridge messages contract — `contracts/bridge_msgs.py`

**Observed (contracts/bridge_msgs.py:40-57):** `NodeState` carries `address: str | None` (the `run://` pointer for the node) and `content_hash: str | None` (its `cas://` integrity hash). `GraphState` is the live shared document pushed to the canvas.

**USE (1):** The guided surface drives the live app's canvas view. When it spotlights a node (via `_registry_ui_target`), the FE reads the `GraphState` to find the node's position and status. `NodeState.address` is the run-address the surface would use to show "this node last ran at this address" — which is part of the at-altitude explanation.

**RELATE (4):** `ActionRequest`/`ActionResponse` (contracts/bridge_msgs.py:25-38) are the C7 verb request/response shapes. The surface's "generate → approve → dispatch" wire sends an `ActionRequest` to the bridge, which routes it to the suite, which runs the dispatch. The `ok`/`error` fields on `ActionResponse` feed the surface's "it built + committed" or "it failed + reverted" feedback.

---

## 8 · The MCP tools contract — `contracts/tools.py`

**Observed (contracts/tools.py:367-468):** `TOOLS` dict has 23 verbs in five categories: introspection, sources, graphs/compositions, runs, results, surfaced decisions. Each `ToolSpec` carries honest `ToolAnnotations` (readonly/destructive/idempotent — "a verb is never both readonly and destructive").

**USE (1):** The guided surface is the human face of the same system the MCP tools expose. `ListSurfaced` / `ResolveSurfaced` are the tool-face of the surface's "pending decisions" queue — the same surfaced items the surface displays in the Inbox lane. The surface and the MCP tools share a substrate (the `store.list_surfaced()` / `store.save_surfaced()` path). This is designed-general: the surface is the visual face, the tools are the agent face, both over the same objects.

**UNIFY/IMPROVE (3):** There is no tool verb for annotating a `ui://` address, attaching a chat to an address, or querying annotations/chats at an address. The surface does these operations via the HTTP bridge (`/api/annotate`, `/api/attach_chat`, `/api/chats_at`), but an agent using the MCP face has no equivalent verbs. If the surface is the Commander's bridge AND the agent face is used for automated reasoning, the agents should be able to read/write annotations at addresses too. The MCP tools contract is a candidate to extend with a small `AnnotateAddress` / `ChatsAt` verb pair. This is a clean unification (one source — the store's annotation/chat primitives — exposed through both faces).

---

## 9 · The addressed store — `store/fs_store.py`

This is the richest substrate file. Full inventory by section:

### 9a · Cross-process locking (`_CrossProcessLock`, `graph_lock`, `dispatch_lock`)

**Observed (store/fs_store.py:27-165):** The `_CrossProcessLock` composes a threading `RLock` (in-process re-entrancy) with an `fcntl.flock` (OS-level cross-process exclusive lock) taken only at the outermost acquire. Per-graph lockfiles live in `<root>/locks/`. `dispatch_lock` is a named alias routing to `graph_lock` with a `dispatch-claim:` key prefix.

**USE (1):** The surface's generate → dispatch → exactly-once dispatch-claim path uses `store.graph_lock(f"dispatch-claim:{seq}")` (Observed suite.py:7437) composed with the Suite's own `_dispatch_lock(derived_from)`. The store provides the cross-PROCESS guarantee; the suite provides the in-process thread guarantee. This two-layer locking is the foundation the "exactly-once generate" requirement rests on.

**RELATE (4):** The store's AGENTS.md explicitly calls out that `store.dispatch_lock(seq)` is the cross-process dispatch-claim primitive (Observed store/AGENTS.md). The suite's `_dispatch_lock` uses a plain `threading.Lock` — a different implementation from the store's `_CrossProcessLock`. The two are composed in suite.py:7437, not substituted for each other. This is by design (thread-lock first, then cross-process lock inside), but the two-layer complexity is worth naming for any build that touches the dispatch path.

### 9b · Atomic writes (`_atomic_write_fsync`)

**Observed (store/fs_store.py:101-116):** Every write that matters (set_ref, save_graph, save_session, save_journey, memo_set, write_provenance, save_surfaced, put_vector) uses the `_atomic_write_fsync` primitive: write to a unique `pid+threadid` temp file, `fsync` the temp's fd, `os.replace` (atomic rename), `fsync` the parent dir. This is the crash-durable write pattern.

**RELATE (4):** `append_annotation`, `append_chat`, `append_event` do NOT use `_atomic_write_fsync`. They use `open("a")` + `write` (append mode). For append-only JSONL files, POSIX guarantees that a single `write()` under 4KB is atomic (one line is never torn), so this is correct and intentional. The distinction is: whole-record writes use tmp+replace; append-only logs use append-mode.

**UNIFY/IMPROVE (3):** `append_event` is in-process thread-safe (under `_event_lock`) but NOT cross-process safe. The store AGENTS.md explicitly surfaces this as a known gap: "two PROCESSES can still both read seq=N and append N+1 → a duplicated seq." The event log is the SSE stream cursor and the dispatch-claim authoring event. For the guided surface's live dialogue (multiple users, or two sessions simultaneously), event seq uniqueness matters for the `events_since(seq)` SSE cursor. This is flagged as a Tim-decision in the store constitution (AGENTS.md: "surface cross-cutting, don't decide unilaterally"). The build should name this explicitly rather than inherit it silently.

### 9c · Annotation and chat at address (I6 / I7)

**Observed (store/fs_store.py:533-531):** `append_annotation(rec: dict)` writes `{ts, **rec}` to `annotations.jsonl`. `annotations_for(address)` filters by the `address` field. The address is the retrieval key; it is the caller's responsibility to pass a valid `ui://` address. The store does NOT validate the address.

**Observed (store/fs_store.py:494-531):** `append_chat(turn: dict)` writes to `chat.jsonl`. `chats_for(address)` filters by the `address` field. Both are append-only JSONL, oldest-first.

**USE (1):** These are the two substrate stores the R2 context-resolution (`_r2_context_at`) reads from at every locus in the guided walk. Every time the RHM reaches a stop, R2 gathers `annotations_for(address)` + `chats_for(address)` + events for that address + ancestors (Observed suite.py:2812-2867). The annotation and chat stores are the surface's institutional memory — marks accumulate here as the walk proceeds.

**TOUCH (2):** `attach_chat` in the suite (suite.py:4487-4516) writes `{role, text, address, source, ts}` to `chat.jsonl`. `annotate` writes `{address, text, ts, source, grade}` to `annotations.jsonl`. Both paths are already wired. The surface's "RHM annotates as you talk" (Synthesis Bucket C-f) would add `annotate` to `RHM_VERBS` and call the same `append_annotation` path. **The store substrate is already complete for this capability.**

**UNIFY/IMPROVE (3):** Neither `annotations.jsonl` nor `chat.jsonl` is indexed. Every `annotations_for(address)` call reads the whole file. For a surface that accrues comments across many sessions and many addresses, this becomes a scan. A pragmatic improvement is a lightweight in-memory index built at `FsStore.__init__` time — but more importantly, this is the "Supabase future" seam: Supabase would give an indexed `WHERE address = ?` query. The surface build will exercise this path enough to make the scan visible. Worth flagging, not blocking.

### 9d · Pin-state overlay (X7)

**Observed (store/fs_store.py:569-615):** `append_pin(address, target_ts, pinned)` writes to `pins.jsonl`; `pin_state_for(address)` returns `{target_ts: bool}` last-wins. The pin is an additive control-state overlay on the annotation/chat stores — it does NOT modify the immutable log, it adds a separate pin record.

**USE (1):** The surface's `annotations_at` / `chats_at` methods (via R2 context-resolution) apply the pin overlay to merged results. An annotation the Commander pinned ("keep this in context") gets weighted higher in R2's scoring. This is live infrastructure for the guided surface.

**RELATE (4):** The pin is the "this matters" signal the Commander leaves as he walks. It accrues at `ui://` addresses. As the guided walk sequences through stops, pinned annotations from PRIOR stops can be included in the R2 context at LATER stops (via ancestor-walk if the addresses are hierarchically related). The cross-stop memory effect is already latent in the substrate — it depends on the ancestor walk finding the pinned item.

### 9e · Session, journey, and chat-thread persistence

**Observed (store/fs_store.py:345-420):** Three distinct whole-record stores:
- `sessions/` — review sessions (item-ids + cursor + mode + graph-id)
- `journeys/` — navigation records (ordered addressed steps + done flag)
- `chat_threads/` — conversation threads (thread metadata; turns stay in chat.jsonl with additive `thread_id`)

**USE (1):** `save_session` / `load_session` are the server-authoritative store for the walkthrough cursor. Every `next()` / `respond()` call in the suite writes through here. The guided surface's "you set the pace" (next/back/dwell) state lives here.

**USE (1):** `save_journey` / `load_journey` are the navigation-record store (L9). A journey records `{id, ts, steps:[{address, ts, **}], done}`. This is the REVERSE path the synthesis Bucket C-e calls "locus-trail / temporal deixis." The journey store is BUILT. What the synthesis calls "net-new" is the emit of `navigate` events on locus change + a `recent_loci()` reader. **The store substrate for journey persistence exists; the runtime wiring (auto-emit on locus change) is the gap.**

**TOUCH (2):** The journey record shape is open (`{id, ts, steps:[{address, ts, **}], done, **}` per the store constitution: "schema-additive, never schema-breaking"). A `navigate` event emission path could append to this record via `append_journey_step` (Observed suite.py:6581). The method exists. `stop_journey` finalizes it (suite.py:6601). `replay_journey` hands back the ordered addresses (suite.py:6622). The explicit start/stop model (not auto-capture) is the store's stated design decision. **For the "recent_loci" path (the scoped temporal deixis of Synthesis Bucket C-e), a lightweight bridge would be: start a journey at session-open, auto-append each `indicate()` call, and read the last N steps as the locus trail.** This reuses the existing store primitives without net-new storage.

**UNIFY/IMPROVE (3):** The `chats_in_thread` method (store/fs_store.py:412-420) filters the global `chat.jsonl` by `thread_id`. The `chats_for` method filters the same file by `address`. These two filter axes (thread_id and address) are INDEPENDENT and do NOT compose: there is no `chats_in_thread_at_address`. If the guided walk wants all chats in THIS session thread at THIS address, it must filter twice manually. A `chats_at_in_thread(address, thread_id)` helper or a two-predicate version of `chats_for` would close this. **Inferred gap, not a blocker — current code works by address-only.**

### 9f · Vector index substrate (X12)

**Observed (store/fs_store.py:617-682):** The `vectors/` namespace stores `{address, vector, content_hash, dim, model, ts}` per address. `put_vector` is atomic/crash-durable. `index_corpus()` returns `[{id: address, vector}]` — the exact shape `nodes/retrieve.run` consumes.

**USE (1):** The surface's R2 context-resolution includes a semantic-ranking step (mentioned in suite.py Observed — "scored by recency × proximity × pin × semantic"). The vector index is the substrate that makes address-level semantic ranking possible. A query like "what did we discuss near the inbox area?" would rank by cosine over the vector index.

**RELATE (4):** `store/vector_index.py` (X12 module) builds and queries this index via the existing `fabric` transport. It is CORPUS-AGNOSTIC: it takes `[{address, text}]`. The guided surface could use it to index every annotation and chat turn (keyed by `ui://` address) so R2's semantic leg has a persistent index rather than scanning all text live. The incremental build (re-embeds only changed content) means this scales as the walk accrues comments.

---

## 10 · The model fabric — `fabric/config.py`, `fabric/client.py`, `fabric/transport.py`, `fabric/vram.py`

### 10a · Config

**Observed (fabric/config.py:12-39):**
- `STORE_DIR` = `~/company/.data/store` (env-overridable). One store, two faces.
- `LITELLM_PROXY` = `:4100/v1`. `OLLAMA_DIRECT` = `:11434/v1`. `DEFAULT_BASE_URL` = OLLAMA_DIRECT.
- `DEFAULT_BRAIN` = `deepseek-v4-pro:cloud`. The RHM's brain is one swappable model slot.
- `DEFAULT_EMBED_URL` = `:8001/v1`. `DEFAULT_EMBED_MODEL` = `BAAI/bge-m3`.
- `DEFAULT_EMBED_DIM` = 1024. `DEFAULT_TIMEOUT` = 180s. `DEFAULT_CLOUD_TIMEOUT` = 300s.
- `FORBIDDEN = ("gemini",)` — enforced via `forbid_gemini`, fail loud.

**USE (1):** The guided surface's live dialogue calls the RHM brain through this config. `DEFAULT_BRAIN` is the model the surface talks back through. The surface relies on this being a real, reachable model.

**TOUCH (2):** The synthesis's "cap-raise or HTML→text pre-digest" decision (D2) would affect the `DEFAULT_TIMEOUT` — a large mockup pumped as 73KB HTML at every turn increases prefill latency. The config provides the knobs; the build decision is which knob to turn.

### 10b · Guarded model calls (`fabric/client.py`)

**Observed (fabric/client.py:54-172):** Three guarded call paths:
- `complete(transport, messages, model, schema=None)` — text or schema-validated JSON, retry/backoff.
- `complete_with_tools(transport, messages, model, tools)` — native tool calling, tool-aware validity (empty content + tool_calls = success).
- `complete_embeddings(transport, inputs, model, dim=None)` — vector guards (count + dim), not text guards.

**USE (1):** The surface's RHM dialogue uses `complete` (or `chat_parts` — the streaming generator version) for every turn. The model guard (non-empty, retry, backoff) is the reliability layer the live dialogue depends on.

**USE (1):** `complete_with_tools` is the path for any agent-driven step that uses the MCP tools — e.g., the autonomous `claude -p` dispatch in the generate-for-mockups wire. Tool-calling responses are allowed to have empty content (the model calls a tool rather than speaking), which plain `complete` would treat as a failure. This distinction is already handled correctly.

**UNIFY/IMPROVE (3):** There is no streaming version of `complete_with_tools`. The surface's text-streaming path (Synthesis Bucket B: wrap `chat_parts()` in SSE) exists for plain text. But if the RHM ever needs to call a tool MID-conversation (e.g., to look up the address registry, or to check blast_radius) while also streaming text, the streaming-with-tools path is not available. This is a net-new capability (Inferred gap) — not blocking the current build, but worth naming as the surface's "feels live + tool-using" convergence point.

**TOUCH (2):** `_backoff(attempt, base=1.0, cap=30.0)` uses exponential + jitter. The live dialogue's "feels live" depends on the brain being fast. If the RHM brain is a cloud model (default: `deepseek-v4-pro:cloud`) and it transiently fails, the retry introduces up to 30s of apparent silence. The surface's text-streaming (Synthesis Bucket B) would show partial output before a retry kills the stream — which is exactly the "interruptible text-streaming cancel path" (Synthesis Bucket C-d). The retry and the streaming cancellation interact: a cancelled stream should not retry.

### 10c · Transport

**Observed (fabric/transport.py:15-25):** `list_models(base_url)` returns live registered models from the endpoint, filtered for no-Gemini. This is the "self-coding brain never invents model names" utility — it picks from what actually exists.

**USE (1):** The surface's node-configuration panel (when the Commander configures a model node) should call `list_models` to populate the model dropdown. This is existing infrastructure for the "configure any model from a live registry" goal.

**TOUCH (2):** `model_supports_tools` (fabric/transport.py:112-193) is the fail-loud tool-capability detector for three endpoint kinds (ollama/litellm/vllm). This is the gate the surface would use before sending a tool-calling request to a model that might not support tools. It raises rather than returning False-when-uncertain (never assume-capable). The surface build should use this before wiring any tool-calling path to a model.

**OBSERVED (fabric/transport.py:28-51):** `_apply_response_format` is the one shared structured-output decision path, used by both `openai_transport` and `openai_tools_transport`. It handles the three response format levels: `json_schema` (server-side constrained decoding), `json_object` (bare JSON), and free text. This is the path a mockup-feedback model call with a structured output schema would use.

### 10d · VRAM gate

**Observed (fabric/vram.py:13-25):** `VramGate(limit=1)` is a `Semaphore`-backed slot: `with gate.slot(): <model call>`. Cloud calls don't acquire (no local VRAM). Local models acquire one slot.

**RELATE (4):** The VRAM gate is the resource guard between the surface's live dialogue (which uses the RHM brain — currently a cloud model, so no VRAM) and any local model nodes running on the same RTX 4080. If the surface's comprehension path shifts to a local model (e.g., the resident 4B for mockup narration), the VRAM gate would mediate between the narration call and any concurrently running graph nodes. This is already correct by construction; the surface does not need to manage VRAM directly.

---

## 11 · The vector index orchestration — `store/vector_index.py`

**Observed (store/vector_index.py:64-123):** `build_index(store, corpus)` is incremental (content-hash diff → embed only changed items), degrade-with-warning (endpoint down → empty index + durable warning event, never a crash). `query_index(store, query_vector)` reuses `nodes/retrieve.run` (the cosine is not reimplemented). `index_staleness(store, corpus)` is a read-only check (no network, no model).

**USE (1):** The surface's R2 semantic leg (scoring annotations/chats by semantic similarity to the current locus query) would use `query_index`. The corpus for the index is `[{address, text}]` — every annotation text keyed by its `ui://` address. Building and querying this index is the substrate for the surface's "context auto-resolves at each locus" (R2) semantic dimension.

**UNIFY/IMPROVE (3):** `index_staleness` is the missing interrogation method that was called out in STATE.md. It exists now. But there is no AUTOMATIC trigger that runs `build_index` when `index_staleness` reports stale. The surface's `R2` context-resolution currently calls the semantic leg opportunistically; if the index is empty or stale, it falls back to keyword/consult. Adding a stale-check → auto-rebuild trigger in the R2 path (or in the suite's boot sequence) would make semantic ranking live without a manual rebuild step. This is a moderate build (a boot-time staleness check + async rebuild if stale). It rides the existing `build_index` / `index_staleness` path.

---

## 12 · The Sequences Primitive — conceptual synthesis across the substrate

The synthesis names the Sequences primitive at `APPLICATION-STRUCTURE-PACK.md:504-541`: `resolve → present/work → persist → next/trigger`. Every piece of the substrate maps to one step:

| Sequences step | Substrate mechanism |
|---|---|
| `resolve` | `contracts/address.py` scheme + `contracts/ui_info.py` parse_ui_address + `contracts/resolver.py` head/get_content |
| `present` | `contracts/ui_info.py` UnionAddressRecord.howto + `contracts/cognition_info.py` COGNITION_EVENT_KINDS (the live part emissions) |
| `persist` | `store/fs_store.py` append_annotation / append_chat / put_vector / save_session / save_journey |
| `next/trigger` | `store/fs_store.py` events_since(seq) (the SSE cursor) + `contracts/node_record.py` Status transitions |

**RELATE (4):** The substrate is not just infrastructure — it IS the Sequences primitive materialised as storage. The surface is the human face of the same primitive. This is why the surface is designed-general: the Sequences primitive runs at every scale, and the substrate stores every step of it, keyed by address.

---

## 13 · The `doc://` / `area://` dogfood thread

**TOUCH (2):** The BUILD-ADDRESS-MAP.md uses `doc://` and `area://` addresses as this build round's coordinate system. These schemes are outside SCHEMES (contracts/address.py:32). The address grammar has no `doc` or `area` scheme. Using these as working addresses while the grammar doesn't know about them is a dogfood inconsistency — the system designed to address everything hasn't yet addressed its own build artefacts.

**UNIFY/IMPROVE (3):** The minimum fix is to add `"doc"` and `"area"` to SCHEMES — purely additive, zero schema_ver change, and makes the grammar self-consistent about the coordinate system the build round is using. Whether these should also be registered in the `ui://` address registry (so `annotations_for("doc://grs/synthesis")` would work) is a deeper question and a Tim-decision. The additive grammar step is the non-controversial one.

---

## Summary of relations and gaps

### USE: surface uses these substrate seams directly
1. `parse_ui_address` (the S0 gate) — every locus action flows through it
2. `annotations_for` / `chats_for` / `pin_state_for` — the R2 address-keyed context stores
3. `save_session` / `load_session` — the walkthrough cursor store
4. `save_journey` / `load_journey` / `append_journey_step` — the navigation record (locus-trail)
5. `append_event` / `events_since` — the SSE stream and event log
6. `UnionAddressRecord.howto` — the D1 foundational affordance text per address
7. `COGNITION_EVENT_KINDS` — the live dialogue event shapes the surface consumes
8. `complete` / `chat_parts` (via fabric) — the RHM brain call path
9. `VramGate` — the resource guard for any local-model narration path
10. `query_index` + `build_index` — the semantic leg of R2 context-resolution

### TOUCH: surface changes or extends these seams
1. `contracts/address.py SCHEMES` — extend with `mockup` (and optionally `doc`/`area`)
2. `contracts/ui_info.py UnionAddressRecord.howto` — populate at author-time via generate-for-mockups
3. `contracts/cognition_info.py ADDRESS_KINDS` — add `cognition` kind if annotating at cognition loci
4. `store/fs_store.py journey` — auto-emit `append_journey_step` on every `indicate()` for locus-trail
5. `contracts/resolver.py` — Protocol is narrower than the surface's actual store contract; flag for Supabase

### UNIFY/IMPROVE: surface activates or resolves these gaps
1. **`mockup://` scheme is in operational use but not in SCHEMES** — one-line additive fix, makes `scheme()` truthful for mockup addresses
2. **`ui://cognition/<turn>` addresses fail `validate_address_record` kind check** — `cognition` kind missing from ADDRESS_KINDS
3. **Event log is not cross-process seq-unique** — known gap, surfaced to Tim (store AGENTS.md), surface build will exercise it
4. **Resolver Protocol narrower than FsStore** — `append_annotation`, `chats_for`, `save_session`, `save_journey`, `put_vector` etc. not in C4 Protocol
5. **No `AnnotateAddress` / `ChatsAt` MCP verbs** — agent face cannot read/write annotations; surface exposes a USE the tool face lacks
6. **Journey store built; auto-emit not wired** — `save_journey`/`append_journey_step`/`stop_journey` exist; the locus-trail (C-e) is a runtime-wiring gap, not a storage gap
7. **No `howto` on `NodeType`** — D1 affordance text lives on `UnionAddressRecord` but not on `NodeType`; live-app node narration is always LLM-generated
8. **Index staleness check exists; auto-rebuild trigger does not** — boot-time stale-check + async rebuild would make semantic R2 live without manual steps

### RELATE: conceptual kinship
1. The Sequences primitive (`resolve→present→persist→next`) is the substrate materialised as storage
2. Edge kinds (`injection`) + cognition events = the live dialogue's mechanism layer
3. `VramGate` + `DEFAULT_BRAIN` = the model-layer the surface's comprehension rides

---

## Top unification opportunity

**Add `mockup` to `contracts/address.py SCHEMES`.**

It is a one-line change (`SCHEMES = ("run", "cas", "blob", "vec", "ui", "code", "mockup")`), purely additive per the file's own doctrine, and it resolves three converging gaps at once:

1. `scheme("mockup://some-file")` currently returns `None` — a silently wrong answer about a scheme already in production use (suite.py:2086-2100). After the fix it returns `"mockup"`.
2. The mockup-aware guided stop (Synthesis Bucket C-c) and the generate-for-mockups dispatch (Synthesis Bucket C-a) both need the grammar to recognise `mockup://` addresses. Without this, any grammar gate (`parse_ui_address` already handles non-`ui://` inputs by raising) would reject a mockup address passed to a locus-aware method.
3. It is the smallest possible step toward the dogfood coherence the BUILD-ADDRESS-MAP.md already diagnosed: "the live address grammar has no scheme for DOCS or DIRECTORY-AREAS."

The fix costs one line. It unblocks both net-new build items that gate the mockup loop. It is the substrate's contribution to making the make-or-break buildable.
