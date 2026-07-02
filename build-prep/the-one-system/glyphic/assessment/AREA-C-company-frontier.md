# AREA C — the Company-side frontier (voice-in, the mode entry, the bridge routes, the roles)

> Assessment agent C, wide-assessment wave. Territory: `/home/tim/company`, READ-ONLY, no live services touched.
> Read in full first: ANCHOR.md, REGROUNDING.md, THE-GENERATIVE-LANGUAGE.md — findings below verify/extend/correct
> §2 (the fusion map) and REGROUNDING §6/§9, never re-derive them blind. Every claim marked **Observed (file:line)**
> / **Inferred** / **Your-idea**. Stress-tested against LIVE source, not the docs' own self-description — two of
> the ANCHOR's named "honest hard parts" turn out to be *wrong as stated* (below); one "gap" turns out to already
> be solved structurally. That's the "yes, but actually" this assessment is for.

---

## 0 · The one-paragraph verdict

The Company side is **closer to instrument-ready than the coordination brief assumed**. The transport (`/api`
proxy, SSE, run_role, say) is real and serves. The mode/loadout machinery is a working, generic, file-discovered
system that a `glyphgraph` mode slots into with near-zero new code — it is pure registry composition, not a build.
The VRAM "refusal" is not a hard capacity wall; it is a **live, fixable bug** (a stale `gpu_util: 0.9` override where
the mode's own migration note says it was tuned to 0.44 — grounded live computation below). The actual gaps are
narrower and sharper than the anchor's list: **(1)** no shared-log fan-out of the live per-word transcript (only
the end-of-turn summary reaches other tabs), **(2)** the 4 glyph roles are wired for direct single-shot call only —
never fired as a mode cast, never fired via `run_swarm`, so "burst-at-pause" is a *designed* pattern with *zero*
roles actually plugged into it, **(3)** `add_node` truly has no placement field (confirmed, not inferred), **(4)**
there is no reindex route, but the generic primitive it would call already exists and is one function short of
being callable on demand, **(5)** a glyphgraph has no address scheme and no persistence citizenship at all — this
is the deepest, least-scaffolded gap, worse than "no bridge route": there's no ROW SHAPE for it anywhere yet.

---

## 1 · VOICE-IN (the talk half)

### 1.1 The ear registry — real, and honestly documented
**Observed** (`voice/stt.py:68-119`): `STT_PROVIDERS` is a genuine open registry — 8 ears (assemblyai cloud,
whisper.cpp, faster-whisper, 3 heavy NeMo GPU ears, 2 lean ONNX realtime ears: moonshine, parakeet-onnx). Every
entry is probed live (`available_stt()` → `_probe_provider`, `stt.py:186-227`) — a down ear reports
`available:false` + a legible reason, never a crash, never an omission (fail-loud-but-legible, matches AGENTS.md
rule 8 "registry-is-truth"). `transcribe()` (`stt.py:249-267`) routes by `kind` — no id-mismatch class of bug
left; a down `local_http` ear raises LOUD naming the endpoint, explicitly refusing silent fallback
(`stt.py:293-309`). Browser audio normalisation (webm/opus, mp4/aac → 16kHz mono wav via ffmpeg,
`stt.py:25-44`) is the FIX for a dated real bug ("the mic records but transcribes nothing") — this is not
scaffolding, it's a hardened, working seam.

**Citizenship read:** the ear registry is typed + derived (nothing hardcoded, `available_stt()` is a pure
projection) + two-way (probed, not asserted) — CITIZEN-GRADE already. Nothing to fix here for glyph purposes.

### 1.2 The finished-thought judge — the exact wiring, and it's already think-off + fast-model disciplined
**Observed** (`runtime/suite.py:6607-6649`, `is_finished_thought`): the SEMANTIC endpoint judge. Resolves a
`judge` ROLE via `resolve_role("judge")` (a fast, separate, non-reasoning model — `suite.py:6613-6619` documents
*why*, with a measured number: deepseek-v4-pro needed ~256 tokens / ~6.5s for a 1-word answer, unusable per-pause).
Called from the voice circuit's endpoint detector (`voice/loop.py:236-264`, `utterance_ended`) which combines
Silero VAD trailing-silence with this OPTIONAL `semantic_complete` hook — **both** must hold (pause AND finished
thought) before a turn fires. Every judge call is durably recorded: `emit_run_record("judge", ms, model=...,
verdict=..., text=...)` at `suite.py:6647` — lands on the shared event log (see 1.4).

**Correction to the coordination brief's framing:** the brief calls this "the judge role wiring" as if it needs
finding — it is fully built, documented with a measured performance number, and already generalises past voice
(the `judge` role is the FIRST instance of a wider pattern, `emit_run_record`'s own docstring at `suite.py:756-764`
says "Generalises Company-wide"). **Nothing here blocks the glyph instrument** — a glyphgraph "is this utterance
finished" question can reuse this exact judge, unchanged.

### 1.3 Where a transcript lands TODAY — the real seam, precisely
**Observed** (`runtime/bridge.py:2376-2540`, `_voice_stream` — the handler behind `POST /api/voice/stream`):
1. The caller POSTs raw audio; the handler transcribes (`bridge.py:2444`, `voice_stt.transcribe(audio, provider=ear)`).
2. The transcript is emitted **immediately** as one NDJSON line on the response socket of *that specific POST*:
   `emit({"type": "transcript", "text": transcript, "ms": stt_ms})` — **`bridge.py:2447`, this is the exact line.**
3. That NDJSON stream (`{type:transcript}` → `{type:chunk}`×N → `{type:reply}` → `{type:done}`) is visible ONLY
   to the HTTP client that opened the POST — it is a private response body, not a broadcast. A second browser tab
   (e.g. a glyphgraph view watching passively) sees **nothing** of this until the turn completes.
4. Only at turn end does anything reach the SHARED substrate: `SUITE.emit_run_record("voice.stream", total,
   turn_id=..., transcript=transcript[:2000], reply=reply[:4000], ...)` (`bridge.py:2528-2532`). This calls
   `self._emit("op.run", ...)` (`suite.py:765`) → `self.store.append_event(...)` (`suite.py:751`) — **the same
   store** `GET /api/stream` tails (`_stream`, `bridge.py:2142-2174`, `SUITE.events_since(cursor)` at line 2163).

**So the transcript DOES reach the shared SSE feed today — but only as a summary event, only at end-of-turn,
typed `op.run`/`op=voice.stream`, not `voice.transcript`, and never mid-utterance.** This is the real, precise
gap: not "no path exists" (REGROUNDING §6.1/§9 implies a blank), but "the live per-word/interim transcript is
private to the mic-holding tab; only the finished turn is shared."

**What a live `voice.transcript` fan-out needs, concretely (additive, no schema change):**
- One line at `bridge.py:2447`, alongside the existing `emit({"type":"transcript",...})`: call
  `SUITE._emit("voice.transcript", transcript, turn_id=turn_id, ms=stt_ms, partial=False)` (or a durable
  `emit_run_record` if it should count toward rollups — the lenient `_emit` is right here, telemetry-only).
  Same one-line addition for the interim/partial path if `transcribe_partial` (`voice/stt.py:236-246`) is wired
  into a streaming loop later — that primitive already returns `{**r, "partial": True}`, ready to carry a
  `partial:True` flag through the same emit.
- **No new transport.** `/api/stream` already tails `events_since` with `id:`/`data:` SSE framing
  (`bridge.py:2163-2166`) and the FE proxy already carries it (`vite.config.ts` — `/api` → `:8770`, unconditional,
  no path exclusions). A glyphgraph tab that isn't holding the mic just needs to `new EventSource('/api/stream')`
  and filter `kind === 'voice.transcript'` — **zero backend work beyond the one `_emit` call**, zero new proxy
  config. Marked: **additive, reversible, no gate** (a pure new event kind, nothing existing changes shape).

### 1.4 What the browser side needs — confirmed via the proxy, not inferred
**Observed** (`surface/app/vite.config.ts:9-23`): `/api` proxies unconditionally to `:8770` (env-overridable via
`VITE_API_TARGET`); `/design` proxies to the static design server `:8775` with a path rewrite, same-origin, "so a
design-system page (the glyphgraph generator) is served as its ONE source file yet can reach `/api`" (its own
comment, matches REGROUNDING's A4). This is genuinely CORS-free same-origin transport already built for exactly
this instrument. Vite's dev proxy handles a long-lived `text/event-stream` GET without special config (plain
keep-alive HTTP, not a protocol upgrade like WebSocket) — **Inferred** from the proxy shape + the fact bridge.py
sets `Connection: keep-alive` (`bridge.py:2158`) and Vite's http-proxy middleware streams by default; **not
verified by a live curl through :5174** in this pass (the ANCHOR's services "may cycle" — did not start them to
avoid touching live state). Recommend a 30-second live check before build: `curl -N http://localhost:5174/api/stream`
from the instrument dev server, confirm SSE frames pass through unbuffered.

---

## 2 · THE MODE ENTRY

### 2.1 The mode registry — genuinely open, file-discovered, one-line-per-mode to extend
**Observed** (`runtime/modes_registry.py`, full file read): `modes/<id>.py` per mode, module-level `MODE` dict,
required fields `label, directive, resolution, consent, grain, shape, stage, live, reserve_r, per_role_ctx,
main_ctx_tokens, brain_config` + optional `subtypes, loadout_class, voice`. Fail-loud on a malformed mode
(`_build_mode`, lines 43-58); `order` sequences without leaking into the decl. `MODES_DIR` anchored to repo root
(`modes_registry.py:90`), not cwd. **This dissolved what used to be the system's one hardcoded dict** (its own
docstring, lines 1-9) — a `modes/glyphgraph.py` is a drop-in file, byte-identical mechanism to the 7 that exist
today (`listening.py`, `text-only.py`, `focus.py`, `background.py`, `walkthrough.py`, `watch-and-react.py`,
`decide-for-me.py` — `ls modes/`).

**Observed** (`modes/listening.py`, full file): a real example — `'loadout_class': 'interaction', 'voice': 'on'`.
A `glyphgraph.py` mode would declare the same shape, its own `loadout_class` (a combo name, see §2.3), its own
`directive`/`grain`/`shape` (probably `grain: 'node'` or similar, `shape` a new archetype — **Your-idea**, not
verified against what `shape` values are legal elsewhere).

### 2.2 The mode→loadout consent gate — already exactly the "consent axis" the brief asked about
**Observed** (`suite.py:2661-2676`, `set_mode`): switching a mode is a free, instant config write. If the new
mode's `loadout_class` has non-resident services, `_maybe_surface_loadout_swap` (lines 2734-2759) surfaces an
inbox confirm — **never auto-actuates**. `apply_loadout` (lines 2761-2805) reads approval from the inbox — "the
autonomous loop can RAISE the confirm... but can NEVER self-approve it" (line 2763's docstring, verified against
the code: `if not self.inbox.is_approved(sid): raise GovernanceError(...)` at 2771-2774). Actuation rides
`ensure_resident(s, evict=True, wait=True)` per service (line 2788) — "RAM+VRAM-gated... cannot OOM" per its own
comment (line 2758). **This is the full consent axis, already built, already the pattern every other mode uses.**
A `glyphgraph` mode gets this for free by declaring `loadout_class` — no new governance code needed.

**Also observed** (`suite.py:2700-2732`, `_gate_work_requires`): a SEPARATE, complementary gate for a unit of
*work* (not a mode) that declares `requires: <loadout_class>` — surfaces the same confirm, then **fails loud**
(`GovernanceError`) rather than degrading, so work never runs against the wrong loadout. If the glyph roles are
fired as ad-hoc `run_role` calls (today's pattern, see §4) rather than through a `glyphgraph` mode switch, this is
the gate to hang a `requires` declaration on instead — **two legitimate entry points, pick one per call site,
both already built.**

### 2.3 The honest VRAM shape — the "21.1 > 16.4" claim is STALE; live computation below (grounded, reproducible)
The ANCHOR's brief says: *"the fitter refused @interaction-fp8 at 21.1>16.4GB — what CAN co-reside?"* This
figure traces to `A-fusion/A-CONTINUATION.md:50` (2026-07-02), itself hedged: *"fitter says 21.1 GB > 16.4 —
profile drift since it shipped; needs a loadout re-fit pass."* I ran the LIVE fitter against the LIVE registry
just now rather than trust either number:

**Observed** (computed live via `ops/cli/registry.py` + `ops/cli/gpu.py`, `python3 -c "..."` against the actual
`ops/services.json` on disk, this session):
```
interaction            → 22372 MB   (embed-pplx 5434 + chat-4b-fp8 14738 + rerank-jina 1300 + stt 0 + tts 900)
interaction-fp8         → 21072 MB   (= interaction minus rerank-jina 1300)
interaction-parakeet    → 22372 MB   (same as interaction, different ear, still 0 VRAM)
ceiling = 16376 MB, overhead reserve = 1024 MB
```
So the LIVE refusal is real TODAY, not just "was true 2026-07-02" — **but the cause is not capacity, it's a live
misconfiguration.** `chat-4b-fp8`'s config (`ops/services.json`, `services.chat-4b-fp8.config`) carries
**`"gpu_util": 0.9`** — an EXPLICIT static override (priority-1 in `budget_vram`'s precedence,
`gpu.py` `budget_vram` docstring: "config.gpu_util × ceiling — the EXPLICIT OVERRIDE... authoritative"). 0.9 ×
16376 = **14738 MB**, which is what's blowing every combo over. But the model's OWN `_migration` field (in the
same config block) documents: *"WF2-fit (2026-06-29): +kv_cache_dtype fp8 (halve KV) + gpu_util 0.5->0.44 to fit
the FULL interaction combo. VERIFY-BY-USE pending."* **The live `gpu_util` field reads 0.9, not the 0.44 the
model's own changelog says was the fitted value** — a drift between the documented tuning and the field that's
actually live. At the documented 0.44: `chat-4b-fp8` = 7205 MB, and:
```
interaction-fp8 (no rerank)  → 5434 + 7205 + 0 + 900     = 13539 MB   → FITS, ~2.8 GB headroom
interaction (with rerank)    → 5434 + 7205 + 1300 + 0 + 900 = 14839 MB → FITS, ~1.5 GB headroom
```
**This is not "add glyph work to an already-tight card" — it's "a one-field fix (`gpu_util: 0.9 → 0.44` on
chat-4b-fp8) restores headroom for the FULL interaction combo including the reranker**, which the WF2 fit note
already intended. Marked: **GATED, not additive** — this is a live service config touching the resident brain
port (`:8001`); changing it needs a restart of chat-4b-fp8 to take effect and should be verified-by-use (a real
generation at the new util, checked for OOM/truncation) before trusting it live. Flagging this as the single
highest-leverage, lowest-risk unblock for "what can co-reside with chat-4b + embed-pplx for a live instrument":
**answer, once fixed: everything in `interaction` — brain, recall-embedder, reranker, ear, voice — with ~1.5GB to
spare**, which is exactly the co-residence profile a live glyph instrument needs (recall for glyph_meaning
top-k lookups + a fast judge + voice in/out, all at once).

**What a `modes/glyphgraph.py` + services combo concretely requires**, given the above:
- A NEW combo in `ops/services.json.combos` (e.g. `glyphgraph`, extends `interaction-fp8` or `interaction` once
  fixed) — additive, one JSON block, mirrors the existing `extends`/`swap`/`add`/`remove` variant mechanism
  (`services.json` combos doc, `_doc` field on `combos`).
  Nothing new needs adding beyond what `interaction` already provides — glyph_extract/glyph_compose/glyph_assist/
  glyph_symbol_candidates all run against the SAME resident chat model via `run_role` (confirmed §4 — none
  declare a distinct `model` override), so the glyph instrument's loadout IS `interaction`, not a new footprint.
- The `glyphgraph.py` mode file itself declares `loadout_class: 'interaction'` (or `'interaction-fp8'`, pending
  the gpu_util fix) — same one-line pattern as `listening.py`.

---

## 3 · THE BRIDGE ROUTES the instrument needs

### 3.1 What exists and verifiably serves (traced to source, not assumed from the route table)
| Route | Verified at | What it does |
|---|---|---|
| `POST /api/cognition/run_role` | `bridge.py:3374-3380` → `cog_run_role` (`bridge.py:1325-1371`) | Fires ONE role, persists to `run://<turn>/<role>`, emits `cognition.run_role` op.run. This is what the writer HTML calls for all 4 glyph roles today (**Inferred** from the roles' own docstrings referencing "fired via the EXISTING run_role" — not re-traced into the HTML file itself this pass). |
| `POST /api/cognition/embed` | `bridge.py:3393-3402` | Same engine, `role` defaults `'embed'`, op dispatches on `role.op`. This is the path `glyph_meaning` top-k lookups ride. |
| `GET /api/corpus-query` | `bridge.py:1777` (`_corpus_query`, not fully re-read this pass — **Inferred** live from route table + AREA-3/AREA-14's prior findings, which this session's ANCHOR says to trust) | "S7: the forager's search door (semantic + heads)." |
| `GET /api/stream` | `bridge.py:2142-2174`, full function read | SSE, tails `SUITE.events_since(cursor)`, 15s heartbeat, gapless reconnect via `Last-Event-ID`. **Fully verified this pass** (§1.3 above). |
| `POST /api/say` | `bridge.py:3030-3045`, full block read | Server-side voice — any fabric member/RHM speaks on host speakers via the ONE serialized speaker (`voice/say.py`). `{text, voice?, engine?, who?}`, fail-loud on empty text or synth error. **Fully verified.** Not glyph-specific but available if the instrument should narrate aloud during co-editing. |
| `POST /api/voice/stream` | `bridge.py:2376-2540`, full function read | The voice turn NDJSON stream — **fully verified** (§1.3). |
| `GET /api/graph`, `/api/graphs` | `bridge.py:1534-1537` → `SUITE.state(gid)` / `SUITE.list_graphs()` | **NOT a glyphgraph store** — see §3.3, this is the execution/decision-cascade graph (`run://`-addressed compute nodes with ran/cached/failed/stuck status), a structurally different object. Confirmed by reading `SUITE.state` (`suite.py:1963-2010+`) and `_load`/`Graph` (`suite.py:1804-1805`). |

### 3.2 What's missing: a reindex route
**Observed** (`runtime/bridge.py:504-539`, the freshness daemon block, full read): a background thread
(`_freshness_loop`) auto-reconciles ONE named space (`extractions`) on an mtime-gated poll — "the gap
recollection diagnosed + harvested: nothing auto-reindexed; manual embed only" (its own comment, line 505).
**Observed** (`runtime/freshness.py`, function signatures read): `reconcile_space(store, space, corpus, *, emb=None,
...)` at line 22 is **already SPACE-GENERIC** — it is not hardcoded to `extractions`. `extractions_corpus()`
(line 78) and `reconcile_extractions()` (line 90, a thin wrapper binding `reconcile_space` to the extractions
corpus+space) are the ONLY caller today. **There is no `glyph_meaning_corpus()` function and no bridge route
(`POST /api/reindex` or similar) that would let the writer trigger `reconcile_space(store, "glyph_meaning",
glyph_meaning_corpus())` on demand after a save.**

Grep across `bridge.py`/`suite.py`/`corpus.py` for any existing `reindex` HTTP verb found **zero matches** beyond
the daemon's own thread name (`"freshness-reindex"`, `bridge.py:542`) — confirms REGROUNDING §6.9's claim
literally, at the source. (Note: this contradicts the auto-memory index's Dragnet-mission note claiming
"freshness auto-reindex BUILT+WIRED... + on-demand ingest(op=reindex) added" — that note is scoped to a
DIFFERENT mission's ledger/corpus work, not this glyph_meaning space; I did not find an `ingest(op=reindex)`
verb anywhere in this repo's current `runtime/` during this pass. Flagging the discrepancy rather than silently
trusting either source — **the memory note may be describing a different corpus's reindex, or may itself be
stale; worth a direct check with the ledger/substrate session (ch-5wog4hmx) before assuming glyph_meaning has
this for free.**)

**What it concretely takes to close (additive, small, reversible):**
1. A `glyph_meaning_corpus()` function in (or beside) `freshness.py`, mirroring `extractions_corpus()`'s shape —
   walk whatever source holds the meaning-registry text (**not traced this pass — the meaning-registry's own
   source-of-truth file/table needs identifying by whoever owns A5/A6; likely the same place `glyph_symbol_candidates`'
   accepted records land, i.e. `CV_ICONS` per that role's own docstring, `roles/glyph_symbol_candidates.py:31`).
2. One bridge route, e.g. `POST /api/reindex?space=glyph_meaning` → `runtime.freshness.reconcile_space(SUITE.store,
   "glyph_meaning", glyph_meaning_corpus())`, mirroring the existing route-handler shape (a thin `elif self.path
   == ...` block, `_body()`/`_send()` — same idiom as every other POST handler in `bridge.py`).
3. Marked: **additive, reversible, no gate** — new route, new function, touches no existing behavior; the
   generic primitive it calls is already production-tested via the extractions daemon.

### 3.3 Graph persistence / addresses — the deepest gap, and it is NOT "no route," it is "no row shape yet"
**Observed** (`contracts/address.py:162`, `SCHEMES` tuple, full list read): `("run", "cas", "blob", "vec", "ui",
"code", "skill", "context", "guide", "session", "cap", "board", "clone", "mind", "exchange", "file", "project",
"vi-vision", "decision", "image", "extraction", "path")`. **No `glyph://` or `graph://` scheme is registered.**
Every scheme addition in this file is documented as "purely additive" (its own repeated comment pattern,
e.g. lines 21-27, 44-46, 57-58, 73, 85-86, 97) — this is a genuinely open, low-ceremony registry to extend, but
someone has to actually author the scheme + its `parse_<x>_address` function + a resolver branch.

**Observed** (`store/pg_vectors.py`, full function-signature scan): this module is EMBEDDING-ONLY — `put_vector`/
`get_vector`/`search` all operate on `ledger.embedding` (pgvector, halfvec, HNSW), keyed by `source_address` +
`space`/`emb_layer`. It stores WHAT a glyph/word MEANS (the 220-vector `glyph_meaning` space lives here), never
graph TOPOLOGY (nodes/edges/positions of one saved glyphgraph instance).

**Observed** (`runtime/suite.py:1800-1805, 1963-2010`): `SUITE.state()`/`list_graphs()`/`Graph` is the
EXECUTION-cascade graph — `run://`-addressed compute nodes, each with a `type` resolved against `self.registry`
(a NODE type registry, not a glyph-symbol registry), a run-status derived from scheduler results (`ran`/`cached`/
`failed`/`stuck`/`idle`). **This is structurally the wrong shape for a glyphgraph**: a glyphgraph's nodes are
authored/placed things with a symbol+word+state+position, connected by typed relation edges with mood
(solid/dashed) — not a computation DAG with run statuses. Reusing `SUITE.state`'s machinery would be a category
error, not a fit (**Your-idea/judgment call**, not just an observation — flagging it because REGROUNDING's fusion
map (§2, the `address.json` row) implies `graph://`/`ui://`/`code://`/`project://` are "one family," which
invites the tempting-but-wrong move of just registering `graph://` onto the EXISTING `SUITE.state` store).

**So the honest answer to "where would a saved glyphgraph LIVE as an addressed citizen":** there is no existing
row shape ANYWHERE in the Company that fits — not the embedding store (meaning, not topology), not the
execution-graph store (compute DAG, not an authored sentence), not the ledger schema as currently used by other
sessions (the board item `item-d47933e2` — see §5 — shows the ledger/substrate session actively building
`ledger.interpretation`/`ledger.file_meta`/`ledger.assertion` side-tables for provenance/edges, which is closer in
spirit but is being designed for a DIFFERENT purpose — run-independent provenance edges over the execution
substrate, not authored glyphgraph topology). **This needs a genuinely new citizen type**, likely:
- a `glyph://` (or `graph://` scoped to glyph, e.g. `glyphgraph://<id>`) scheme registered in `address.py:162`,
- a store table/JSON-blob shape carrying `{nodes:[{id,symbol,word,state,x,y}], edges:[{from,to,kind,line}]}` (the
  exact shape `glyph_assist`'s ops already imply as the live in-browser state — `roles/glyph_assist.py:32-35`'s
  prompt template literally names `{nodes:[{id,symbol,word,state}], edges:[{from,to,kind,line}]}` as the context
  it's given, so the SHAPE already exists as a de-facto contract between the browser and the role — it just has
  no persisted, addressed home),
- a resolver branch (`parse_glyphgraph_address` + a dispatch case, mirroring the `board`/`clone` precedents).

Marked: **GATED** — this is new schema/registry surface, not a pure addition to an existing behavior; per
REGROUNDING §8, "touch NO ledger schema / NO migrations; additive only" is this seat's own standing constraint,
and per the board coordination (§5 below), the ledger/substrate session is mid-flight on adjacent schema work.
**This should be raised with ④/ledger-substrate before authoring, not built solo** — exactly the kind of
schema-touching decision REGROUNDING §8 reserves for board-first coordination.

---

## 4 · THE ROLES — `roles/glyph_*.py` + `complete_text` as they stand

### 4.1 The four roles, read in full — what they actually do
- **`glyph_extract`** (`roles/glyph_extract.py`, full file): utterance → `{nodes:[{word,kind}],
  relations:[{from_word,to_word,phrase,mood}]}`. Pure extraction, explicitly NOT judging ("extraction-vs-judgment"
  is named in its own description). Schema-constrained (`GlyphExtractOut` BaseModel) — per §4.3 below, this means
  it is STRUCTURALLY think-off already, for free.
- **`glyph_compose`** (`roles/glyph_compose.py`, full file): given a word + top-k meaning candidates (with cosine
  scores), judges which one TRULY carries the meaning, or abstains (`chosen: ''`). Its `why` field is declared in
  the schema (`why: str`) — REGROUNDING §6.9's claim that "glyph_compose why-field empty on abstain" is about
  RUNTIME behavior (the model returning an empty string), not a missing field; the schema HAS the slot, so this
  is a prompt-tuning gap, not a schema gap (**Inferred** — I did not run the role to reproduce an empty why;
  this reframes the gap's location rather than closing it).
- **`glyph_assist`** (`roles/glyph_assist.py`, full file): instruction + current graph state (nodes/edges/vocab)
  + selection → typed ops (`set_state, add_edge, add_node, remove, narrate`), applied "through the same code
  paths the mouse uses" (its own description — the one-IR law in practice). **Confirmed, not inferred**:
  `GlyphAssistOutOps` (lines 10-18) has fields `op, ids, value, from_id, to_id, kind, line, text` — **no x/y,
  no position, no span, no placement field of any kind.** `add_node`'s `value` field is documented as "the word
  for the new thing (the browser resolves its glyph by meaning)" — placement is entirely unaddressed by the
  schema. This is REGROUNDING §6.9's "resolves-but-doesn't-place" claim, verified exactly true at the schema
  level, not just observed behavior.
- **`glyph_symbol_candidates`** (`roles/glyph_symbol_candidates.py`, full file): the foundry — brief → 4 distinct
  SVG symbol candidates as structured records (id/name/description/svg/domain/kind/tags), landing in `CV_ICONS`
  on human pick. Solid, self-contained, no gaps found in this pass.
- **`complete_text`** (`roles/complete_text.py`, full file): pure passthrough completion, the union-path role for
  CV_AI's `complete()`. Nothing glyph-specific; included for completeness per the brief.

### 4.2 Gaps vs the pipeline — burst-at-pause, `run_swarm` wiring
**Observed** (grep across all 4 glyph role files + `judge.py` for `mode_scope`): **none of the 4 glyph roles
declare `mode_scope`.** `cast_for_mode(mode)` (`suite.py:6378-6392`) returns "every file-discovered role whose
mode_scope includes `mode`" — an unbound role (no `mode_scope`) is invisible to every mode's cast, structurally.
This means **today, none of the 4 glyph roles can ever be fired by `run_swarm`** (`suite.py:7295`, called from
inside `_fire_wave` at 7293-7299, itself fed by `cast_for_mode`'s `fireable` list at line 7277) — they are ONLY
reachable via direct `POST /api/cognition/run_role` calls naming them explicitly, which is exactly what the
writer HTML page does today (per its own docstrings' claim of "fired via the EXISTING run_role").

**This confirms LIVE-INSTRUMENT.md's own "honest gap" language** (found via grep, `live-instrument/LIVE-
INSTRUMENT.md:519`: *"`roles/glyph_*.py` (think-off, schema-constrained, burst-at-pause) via `run_swarm`"* is
listed as the INTENDED design, not the current state) — the burst-at-pause pattern is fully specified in prior
research (READ-1/READ-2/AREA-2, all citing the same "~10-14 short, think-off, schema-constrained roles at each
pause" operating point) but **zero roles are actually plugged into `run_swarm` today.** The mechanism it would
plug into (`cast_for_mode` + `run_swarm` + a mode's cast) is real, live, and used daily by the RHM's own
`chat_parts` turn structure (`suite.py:7273-7307`) — this is not a build-from-scratch, it is:
1. Add `'mode_scope': ['glyphgraph']` (or similar) to each of the 4 glyph roles' `ROLE` dicts.
2. Author `modes/glyphgraph.py` (§2.1).
3. `chat_parts`/`run_swarm`'s existing concurrency + emit machinery does the rest — `cognition.role.fire` and
   `cognition.wave` events already land on the SAME shared event log `/api/stream` tails (confirmed by reading
   `suite.py:7283-7297`, the same `self._emit` used everywhere else in this file).
Marked: **additive, reversible** — role-file edits + one new mode file; no existing mode or role is touched.

### 4.3 `think=False` discipline — ALREADY STRUCTURALLY GUARANTEED, not a gap (correcting the brief)
**Observed** (`runtime/cognition.py:482-490`, `run_role`'s think-resolution block, read in full context):
*"GUIDED-JSON ⊥ THINKING (Tim 2026-07-01, root-caused): a SCHEMA-constrained fire... forces valid JSON from the
FIRST token — the model cannot emit the `<think>` reasoning tokens... So a schema fire defaults to NO-THINK
unless the role/caller EXPLICITLY asked to think."* Code: `if eff_think is None and eff_schema is not None:
eff_think = False` (line 489-490). **All 4 glyph roles declare `output_schema`** (every one of
`GlyphExtractOut`/`GlyphComposeOut`/`GlyphAssistOut`/`GlyphSymbolCandidatesOut` is a real Pydantic BaseModel,
confirmed by reading each file) — so `eff_schema is not None` for every glyph role call, and none of them declare
an explicit `think` override, so **`eff_think` resolves to `False` automatically, today, with zero role-level
configuration needed.** This directly contradicts the coordination brief's framing that "think=False discipline"
is a gap to assess — **it is already enforced structurally, for a documented, root-caused reason (empty-content
failure mode), for every schema-constrained role including all 4 glyph roles.** Nothing to build here; flagging
it as a corrected finding rather than silently confirming the brief's premise.

### 4.4 What `glyph_relations` or placement-hints would concretely add
- **`glyph_relations`** (proposed, not built): REGROUNDING doesn't separately name this, the coordination brief
  does. Given `glyph_extract` already extracts `relations:[{from_word,to_word,phrase,mood}]` in the SAME call as
  nodes (not a separate role), a standalone `glyph_relations` role would only be justified if relation-teaching
  needs its OWN interactive loop (REGROUNDING §6.9: "relation-teaching UI... words teach, relations don't") —
  i.e. a role that takes a taught relation-phrase + its resolved edge-kind and PERSISTS the mapping the way
  `glyph_symbol_candidates` → `CV_ICONS` persists a taught word→symbol mapping. **This is a real, named gap**
  (confirmed against REGROUNDING's own §6.9 list) — there is no relation-teaching persistence path anywhere in
  the 4 roles read this pass; `glyph_assist`'s `add_edge` op takes `kind` "from vocab.edge_kinds" (line 16 of its
  schema) implying edge kinds are a CLOSED, pre-existing vocabulary the browser passes in — teaching a NEW kind
  has no role or route at all. **Your-idea**: a `glyph_teach_relation` role mirroring `glyph_symbol_candidates`'
  shape (propose candidates for a new relation phrase → human picks/confirms → persist into whatever registry
  holds `edge_kinds`, likely `CV_EDGES` per the fusion map's connectors.json row) would close this the same way
  symbol-teaching already works — reuse-the-pattern, not invent-a-new-one.
- **Placement-hints**: given `add_node` has zero placement fields (§4.1, confirmed), a placement-hint addition
  would need EITHER (a) extending `GlyphAssistOutOps` with an optional `near_id`/`direction` semantic hint (the
  browser resolves the actual x/y — keeps the one-IR law: the AI never dictates raw coordinates, only intent,
  consistent with REGROUNDING's spatial-theorem framing that position should be DERIVED, never placed) OR (b) a
  separate spatial-resolver step entirely outside the role (the "stable-slot/freeze law exists, unwired" — this
  is ④'s/the spatial-theorem's territory per the ANCHOR's own ownership split, not this seat's to redesign).
  **Recommend (a) as the minimal, in-scope addition**: one optional field on the existing schema, additive,
  non-breaking to every other op type.

---

## 5 · COORDINATION FACTS — what ④'s loop-prep + the ledger session's items mean for these seams

**Observed** (`channel-memory/noticeboard/item-d47933e2.md`, full read): this board item is filed by the
**ledger/substrate session** (ch-5wog4hmx, Fable), NOT by ④ THE CONTAINER directly — it is the ledger session
asking ④ to reconcile BEFORE it builds three things that touch the shared `ledger` schema: (1) a supersession fix
(side-tables `ledger.interpretation`/`ledger.file_meta`/`ledger.assertion` + read views, so descriptions survive
run-rebuilds), (2) a parametric job/trigger system + change-driven heartbeat, (3) `ledger.query(spec jsonb)` — a
multi-axis coordinate query. **None of these three items are about glyphgraph persistence** — they're about the
EXECUTION-substrate's own provenance/scheduling problems (the same `run://`-addressed graph `SUITE.state()`
serves, per §3.3's finding that this is a structurally different object from a glyphgraph). The item does NOT
mention glyphic, glyph_meaning, or anything in this seat's territory by name.

**What this means for §3.3's finding:** the ledger session is ALREADY mid-flight designing side-tables for
edges/provenance on the EXECUTION graph. If a future `glyphgraph://` citizen needs its own persisted
nodes/edges table, **the sequencing question is real**: should it be a sibling schema addition alongside
whatever ④+ledger-substrate land, or fully separate? This is exactly the kind of "coordinate schema-touching work
on the board first" REGROUNDING §8 requires — **not decidable from this seat's read alone**, and I'm not
fabricating a resolution. Recommend: post a companion board item once this assessment synthesizes, naming
`glyphgraph://` persistence as a FOURTH candidate schema addition, explicitly asking whether it should ride the
same migration wave as items 1-3 above (their `ledger.assertion` side-table, built for "run-independent edges,"
is structurally the CLOSEST existing design to what a glyph edge needs — worth asking directly rather than
building parallel).

**Follow-up grep run** (`grep -rl "L9\|L10\|L11" channel-memory/noticeboard/`) closes the loop: ④ replied to
`item-d47933e2` in `item-a58c6277` — **all three ledger-session proposals ACCEPTED as named lanes L9-SUPERSESSION,
L10-JOBS, L11-QUERY**, with migration numbers assigned (ledger session takes 0014/0015/0016; ④'s own L1 SPINE
self-renumbered to 0013 after finding a collision). Per that reply: *"L8 (the window, gated on Tim, B-then-A) is
your biggest consumer — L11 green is part of what makes Tim's 'go' near-guaranteed."* — confirming L8/the-window
is ④'s own parallel loop-prep, downstream of L9-L11, not overlapping this seat's territory at all.

**All three lanes are now BUILT AND APPLIED, verified live** (`item-4e6e4838`: 0014 durability/L9 applied;
`item-d42c52dc`: 0015 query-prereqs/L11-prep applied; `item-a83165f7`: 0016 `ledger.query` v1 applied, ledger
session's reserved block CLOSED; `item-4595c151`: 0022 `ledger.cluster_member` for scale-drill, migration map
complete). **None of L9/L10/L11 touch glyphgraph territory** — L9 is provenance/interpretation side-tables for
the EXECUTION substrate (confirms §3.3's read: `ledger.assertion` = "authored-vs-derived provenance faces of ONE
mechanism," an edge-provenance grammar for `run://`-addressed compute nodes, not a glyph-topology store); L10 is
job/intent lifecycle via marks; L11 is the one multi-axis `ledger.query(spec)` fn. **This closes §3.3's
recommendation with a concrete answer**: `ledger.assertion`'s "authored edge with provenance=authored, validated
against the edge_kinds registry" shape (per ④'s reply, point 2b) is real, live, and structurally the closest
existing mechanism to what a glyph edge needs — the question of whether `glyphgraph://` topology should be a
sibling schema riding the SAME edge_kinds/assertion grammar (rather than a wholly separate table) is now
answerable by direct comparison, not speculation. Recommend framing the future board ask exactly that way: "can a
glyph edge be an `ledger.assertion` row with `kind` drawn from CV_EDGES, or does it need its own table" — a
sharper question than the generic one this pass could initially pose.

---

## 6 · THE ORDERED COMPANY-SIDE WORKLIST (exact seams, reversible/additive vs gated, honest latency/VRAM)

1. **[ADDITIVE, reversible, ~1 line]** Fan out the live transcript: add `SUITE._emit("voice.transcript", transcript,
   turn_id=turn_id, ms=stt_ms)` at `bridge.py:2447`, alongside the existing private NDJSON emit. Unblocks a
   passive glyphgraph tab watching `/api/stream` without holding the mic. No new transport, no proxy change.
2. **[GATED — live service config, needs restart + verify-by-use]** Fix `chat-4b-fp8`'s `gpu_util` in
   `ops/services.json` from the live `0.9` to the documented-but-undeployed `0.44` (its own `_migration` field
   names this exact value). Restores ~1.5-2.8GB headroom across `interaction`/`interaction-fp8`, unblocking
   CO-RESIDENCE of the full loadout (brain + recall-embedder + reranker + ear + voice) for a live glyph
   instrument. This is the single highest-leverage fix in this whole worklist — a one-field change that resolves
   what looked like a hard capacity wall. Must be verified by an actual generation at the new util (OOM/truncation
   check) before trusting it live — do not just trust the arithmetic.
3. **[ADDITIVE, reversible]** Author `modes/glyphgraph.py` (mirrors `modes/listening.py`'s shape exactly),
   declaring `loadout_class: 'interaction'` (or `'interaction-fp8'`, pending #2's fix landing). Gets the full
   mode-switch consent/loadout-swap governance (`suite.py:2661-2805`) for free — zero new governance code.
4. **[ADDITIVE, reversible]** Add `'mode_scope': ['glyphgraph']` to each of the 4 `roles/glyph_*.py` `ROLE` dicts,
   so `cast_for_mode('glyphgraph')` picks them up and `run_swarm` fires them concurrently at each pause — the
   "burst-at-pause" pattern LIVE-INSTRUMENT.md already specifies, currently wired to zero roles. This is the
   single biggest gap between "documented design" and "what actually runs" found in this assessment.
5. **[ADDITIVE, reversible, new function + new route]** Add `glyph_meaning_corpus()` (mirrors
   `freshness.extractions_corpus()`) + a `POST /api/reindex?space=glyph_meaning` route calling the ALREADY-GENERIC
   `reconcile_space` — closes REGROUNDING §6.9's "reindex-after-save has no bridge route" with the smallest
   possible diff, reusing a production-tested primitive. Needs the meaning-registry's actual source-of-truth
   location identified first (not traced this pass — likely `CV_ICONS` per `glyph_symbol_candidates`' own
   docstring, but confirm before authoring the corpus function).
6. **[Your-idea, additive]** A `glyph_teach_relation` role, mirroring `glyph_symbol_candidates`' propose→pick→
   persist shape, to close the "relation-teaching has no UI" gap the same way symbol-teaching already works —
   reuse the pattern rather than invent a new one.
7. **[Your-idea, additive]** Extend `GlyphAssistOutOps` with an optional placement-HINT field (`near_id`/
   `direction`, never raw x/y — keeps the one-IR/derive-never-place law), so `add_node` can express intent about
   WHERE without the AI dictating coordinates. Coordinate with whoever owns the spatial-theorem/stable-slot work
   (this ANCHOR names it as ④'s/this-seat's shared territory, "fields-on-canvas offered") before finalizing the
   field shape.
8. **[GATED — needs board coordination, schema-touching]** Author a `glyphgraph://` address scheme
   (`contracts/address.py`) + a persisted row shape for `{nodes, edges}` topology — the deepest gap found: no
   existing store (embedding, execution-graph, or ledger-as-currently-used) fits a glyphgraph's shape. Do NOT
   build solo — post a board item asking whether this rides the SAME migration wave as the ledger/substrate
   session's `ledger.assertion` side-table (item `item-d47933e2`), which is structurally the closest existing
   design to what a glyph edge needs.
9. **[Verify before build, cheap]** Confirm SSE actually streams unbuffered through the Vite dev proxy at `:5174`
   with a live `curl -N http://localhost:5174/api/stream` — inferred to work from the proxy/header shapes, not
   verified live this pass (services intentionally left untouched per the READ-ONLY brief).

### Honest latency/VRAM reality for the live loop
- **Judge latency**: already measured and documented (`suite.py:6615-6616`) — a reasoning model is 6.5s/unusable;
  the bound fast judge is the right shape already; no new measurement needed for the endpoint-detection piece.
- **Glyph-role burst latency**: UNMEASURED for this specific cast (no roles currently fire via `run_swarm` at
  all — see #4). LIVE-INSTRUMENT.md's own figure ("~10-14 short, think-off, schema-constrained roles... shared
  with the main reply; the knee collapses to ~1-5 mid-deep-reply") is `derived-from-principle`/prior research,
  not re-verified this pass. Once #3+#4 land, this becomes measurable for real via the SAME `emit_run_record`
  rollup machinery (`suite.py:767-784`, `run_stats`) every other op already uses — no new instrumentation needed,
  just fire it and read `run_stats('cognition.wave')`.
- **VRAM**: see #2 above — the honest number, live-computed, not assumed: `interaction-fp8` at the CURRENT
  (buggy) `gpu_util` needs 21072MB against a 16376MB ceiling (fails by 4696MB); at the DOCUMENTED-but-undeployed
  0.44 it needs 13539MB (fits with 2837MB headroom), and the FULL `interaction` combo (with reranker) needs
  14839MB (fits with 1537MB headroom). The fix is one field, not a redesign.

---

## 7 · Summary for the synthesis pass

**3-line summary:** The Company-side transport (proxy/SSE/run_role/say) is real and serves; the mode/loadout
system is a generic, working, file-discovered registry that a glyphgraph mode joins with near-zero new code. The
two sharpest real gaps are (a) zero glyph roles are wired into the burst-at-pause `run_swarm` pattern despite it
being fully designed elsewhere, and (b) a glyphgraph has no address scheme or persisted row shape anywhere — the
deepest gap in this territory, needing board coordination, not a solo build. The "21.1>16.4GB" VRAM wall is a
live, single-field misconfiguration (`gpu_util: 0.9` vs. the model's own documented `0.44` fit), not a capacity
ceiling — fixing it unblocks full co-residence for the live instrument.

Written to `/home/tim/company/build-prep/the-one-system/glyphic/assessment/AREA-C-company-frontier.md`.
