# Backend Seam Pack — the FE-facing contract surface of the unified Company backend

**For:** Claude Design (Anthropic's FE-design tool). It reads/writes repo code + renders live + emits FE code we
integrate. This is the **one precise description** of the backend's FE-facing contract surface so that
generated FE work lands in the right shapes automatically.

**This is a DOCUMENTATION deliverable.** Every shape below was read from the **live unified code** on branch
`concurrent-cognition` (== unified main `49debc4`) — `runtime/bridge.py`, `runtime/suite.py`, `contracts/*` —
and the response JSON was captured by curling a live bridge (`PYTHONPATH=/home/tim/company-cognition
/home/tim/company/.venv/bin/python runtime/bridge.py <port>`). Where a shape is from a real curl it is marked
**(curled live)**; where it is read off the handler/return it is marked **(from code)**. Nothing here is
invented (AGENTS.md rule 8).

**The conceptual spine** — one unbroken circuit, every route is a point on it:

```
  Principal → Domain → Intent → Proposal → Approval → Execution
  (operator)  (graph/   (chat/   (surfaced  (/api/     (apply /
              address)  act/     item)      resolve)   run / dispatch)
                        build-intent)
```

The FE never owns state. It **reflects** the backend (read the registries/projections), **drives via
addresses + verbs** (POST a structured intent), and **surfaces** every consequential write for the operator to
approve. Six laws (§5) make that non-negotiable.

---

## 0 · Cross-reference: the cognition-AUTHORING side is already documented

The **cognition authoring contracts** (the 12 `/api/cognition/*` write/validate/test/select endpoints, the
`RoleFieldSpec` / `RuleAST` / `RuleDecl` shapes, the UX→surface map, the authoring laws) are documented in
full in:

> **`build-prep/concurrent-cognition/AUTHORING-FE-HANDOFF.md`**

This pack does **not** re-document them — it **points to that doc** and documents the rest of the unified
surface (interface / wire / voice / RHM / settings / graph / the shared substrate) **plus the cognition VIEW
side** (the `/api/cognition_info` read-projection + the `cognition.*` SSE event contract, §2/§4). When this
pack lists a `/api/cognition/*` route it gives the one-line role + a cross-ref, not the full body.

---

## 1 · The HTTP routes (every `/api/*`, grouped by subsystem)

All routes are dispatched in `runtime/bridge.py` — `do_GET` (lines 287–509) and `do_POST` (lines 733–1346).
**Two universal conventions hold for every route:**

- **Fail-loud (law §5.h):** every handler is wrapped in `try/except Exception as e` that returns
  **HTTP 400** with body `{"error": "<ExcType>: <message>"}` (GET: bridge.py:507; POST: bridge.py:1345). The
  FE must surface that `error` string, never swallow it. A 404 with `{}` means an unknown path.
- **`graph_id` defaults to `DEMO`** ( = `"codebase"`, the live graph) on graph-scoped routes; pass
  `graph_id` in the query (GET) or body (POST) to scope to another graph.

Route count by subsystem: **RHM organ 15 · interface/address 16 · wire 6 · settings/models/voice 30 ·
graph/canvas 21 · cognition 14 (2 read/view + 12 authoring→cross-ref) · stream 1 (shared) = 102 distinct
`/api/*` routes** (counting GET and POST on the same path separately, and each alias).

---

### 1.1 · RHM organ — the conversational/decision face (13)

| Route | Method | Request (body/query keys) | Response shape | Law |
|---|---|---|---|---|
| `/api/chat` | GET | — | the last 40 chat turns: `list[turn]` (curled: list) **(from code, suite.chat_history(40))** | reflects |
| `/api/chat` | POST | `{message, graph_id?, focus?}` | `{reply, action, graph_id}` — OR a **face** variant: `{face:"annotate", annotation, action:null, graph_id}` / `{face:"operate", reply, action, graph_id}` / off-mode `{reply, action:null, mode, history}` / a proposal turn `{reply, action, proposal, mode, ...}` **(from code, suite.py:4030/4049/4108/4789/5045)** | propose-not-apply |
| `/api/act` | POST | `{verb, address?, args?, graph_id?}` — **verb is REQUIRED non-empty** (400 if missing) | same `{reply, action, graph_id}` as chat. The address's tier can force a SURFACE-instead-of-act (I4 gate). **(from code, suite.act suite.py:3974)** | operator-only; 7-verb whitelist; no-self-apply |
| `/api/resolve` | POST | `{id, choice, reason?, session?, position?}` — `choice` ∈ approve/reject/comment/skip/decide | `{ok:true, verdict:{...}, surfaced:[...]}` **(from code, bridge.py:1331)** | **operator-only — never on the MCP/agent face** |
| `/api/apply` | POST | `{id}` | `{ok:bool, path, kind, error, types:[...]}` — `ok=false` if the build-gate rejected; routes by action class **(from code, bridge.py:1340)** | apply only succeeds if operator approved |
| `/api/decision` | POST | `{id}` | `{id, decision:{id, action, payload, default, resolved, status, origin, session_id, ...}}` — the surfaced item as an audit view over the log **(curled live)** | audit |
| `/api/inbox` | GET | — | `{live_escalations:[{id, action, payload, default, resolved, status, origin?}], ...lanes}` **(curled live)** | reflects |
| `/api/surfaced` | GET | — | `list[{id, action, payload, default, resolved, status, origin?, session_id?, position?}]` **(curled live)** | reflects |
| `/api/coa` | POST | `{id}` | `{id, raw, framing, framing_struct, grounded, degraded}` — decision-compiler UP (raw stays drillable; `grounded=false`/`degraded=true` on empty/model-down) **(from code, suite.py:5558–5587)** | abstain-on-empty, raw always attached |
| `/api/surface-output` | POST | `{node, graph_id?}` | `{id, node, name:"output · <node>"}` — routes a node's result to the inbox/COA **(from code, suite.py:5777)** | propose |
| `/api/surface-review` | POST | `{item, origin?}` | `{id, origin, status:"inbox"}` — surfaces a review item into the one queue **(from code, suite.py:5811)** | propose |
| `/api/capture-idea` | POST | `{text}` | `{id, origin:"generative", status:"inbox"}` **(curled live)** | — |
| `/api/react` | POST | — (uses DEMO) | `{comment:"<text>"}` (empty string when nothing to react to) **(curled live)** | — |

The B3 offer-defer pair rides here too:
| `/api/defer-offer` | POST | `{proposal:{...}, note?}` — `proposal` REQUIRED object | `{id, name, proposal}` — the queued revivable item (resolved=null) **(from code, suite.py:5849)** | nothing dispatches — consent invariant |
| `/api/revive-offer` | POST | `{id}` | `{id, proposal, ...}` — re-opens the live interactive offer card **(from code, suite.py:5889)** | — |

---

### 1.2 · Interface / address-keyed substrate (16)

The **reflects-never-owns** machinery: everything keyed by a `ui://` (or `run://`) address. **Every one of
these RAISES → 400 on a missing/malformed `address` (fail-loud) and returns a clean partial/empty bundle on a
well-formed-but-unregistered address (never fabricated — DENY-ALL).**

| Route | Method | Request | Response shape | Notes |
|---|---|---|---|---|
| `/api/scope` | GET | `?address=` | `{address, symbols:[], scope:[], stale:bool, note}` — the `ui://→code://→scope[]` join; empty scope = DENY-ALL **(curled live)** | S3 |
| `/api/address-help` | GET | `?address=` | `{address, what_this_is, how_to_change, how_to_use, legs_present}` — the composed 3-leg affordance bundle **(curled live)** | D2 |
| `/api/up-translate` | GET | `?kind=&ref=` — kind ∈ address\|decision | `{kind, ref, lead, mechanism, legs_present, grounded, degraded, note}` — present-at-Tim's-altitude **(curled live)** | F1 |
| `/api/self-changes-at` | GET | `?address=` | `{address, scope:[...], stale:bool, note, changes:[...]}` — self-changes filtered by the address→code scope **(curled live)** | L5 |
| `/api/annotations` | GET | `?address=` | `list[{kind, address, ts, text, source, ...}]` — the comment thread, oldest-first (pin-overlaid); honest `[]` if none **(curled live)** | I6 read |
| `/api/annotate` | POST | `{address, text, source?}` — address REQUIRED | the annotation rec `{kind, address, ts, text, source}` (also emits a located-gold chat turn into `training_signal`) **(from code, suite.ingest_comment suite.py:4138)** | I6 write |
| `/api/presentation-pref` | GET | `?address=` | `{kind, arg}` or `null` (the adapt step degrades to default on null) **(from code, suite.py:4238)** | F1 read |
| `/api/presentation-pref` | POST | `{address, pref:{kind, arg?}, text?, source?}` — both REQUIRED | the recorded pref rec `{kind, address, ts, text, source}` **(from code, suite.py:4238)** | F1 learning capture |
| `/api/chats` | GET | `?address=` | `list[{kind, address, ts, text, source, role}]` — the chat thread attached to the address (pin-overlaid; distinct from `/api/chat`); honest `[]` if none **(curled live)** | I7 read |
| `/api/attach-chat` | POST | `{address, text, role?, source?}` — address REQUIRED | the attached turn rec `{kind, address, ts, text, source, role}` **(from code, suite.attach_chat suite.py:4334)** | I7 write |
| `/api/address-history` | GET | `?address=` | `{address, trajectory:[{seq, ts, kind, summary, surfaced?, intent?, ...}]}` — the chronological events AT the address **(curled live)** | L3 |
| `/api/stale-at` | GET | `?address=` (a `run://<graph>/<node>` addr) | `{stale\|unknown, reason, volatile, ...}` — costed recompute vs cached **(from code)** | L10 |
| `/api/ref-versions` | GET | `?address=` (a `run://` output addr) | `{versions:[...]}` (honest `[]` if none) — the values an address has held **(from code)** | L6 |
| `/api/pin` | POST | `{address, target_ts, pinned?}` — both REQUIRED | the pin/unpin of an attached item **(from code)** | X7; operator-only, off MCP face |
| `/api/journey/replay` | GET | `?journey=` | the ordered `ui://` addresses to step the view through **(from code)** | L9 |
| `/api/journeys` | GET | — | recorded journeys `[{id, step-count, done}]` newest-first **(from code)** | L9 |

Journey **write** (the reverse navigation capture) lives in the graph block: `/api/journey/start` (no body →
`{journey...}`), `/api/journey/step` `{journey, address}`, `/api/journey/stop` `{journey}` (POST, bridge.py:1157–1168).

---

### 1.3 · The decision→implementation WIRE (5)

The operator face that mints build-intents. **These routes ONLY SURFACE (resolved=null); they NEVER dispatch.**
Dispatch is `dispatch_decision`, off this face — it fires only after the operator approves via the operator-only
`/api/resolve`, and the WIRE-LOOP picks it up. This is the floor (§5.c).

| Route | Method | Request | Response shape | Notes |
|---|---|---|---|---|
| `/api/build-intent` | POST | `{spec, scope?, consequence_class?, why?}` — `spec` REQUIRED non-empty | `{id, intent:"build", scope:[...], consequence_class}` **(curled live)** | the REAL production entry seam |
| `/api/intent-at` | POST | `{address, text\|comment, source?, consequence_class?, why?}` — address+text REQUIRED | a build-intent surfaced AT the address (scope DERIVED from the address via S3; orphan addr → empty scope = DENY-ALL); records the comment via I6 **(from code, suite.py:1025)** | L1 addressed-feedback→wire |
| `/api/approve-reach` | POST | `{id, members:[...], reason?}` — both REQUIRED | widens a build's edit reach to the operator-approved blast-radius members (a member NOT in the persisted radius RAISES → 400) **(from code, suite.approve_reach)** | X16; operator-only |
| `/api/checkpoint` | POST | `{paths:[...], label?}` | a reversible `[checkpoint]` restore point (shows in the self-change ledger; undoes via `/api/revert`) **(from code)** | operator-only |
| `/api/revert` | POST | `{sha}` | the rollback of a self-change **(from code)** | operator-only |
| `/api/propose` | POST | `{name, spec}` | dispatches a build (agent/operator) — `suite.propose_node` **(from code)** | the node-build sibling of the wire |

Audit reads of the wire ride `/api/self-change-log` (GET `?limit=`) and `/api/last-change` (GET → the last
self-change or `{}`) in §1.4.

---

### 1.4 · Settings / models / voice / status (22)

| Route | Method | Request | Response shape | Notes |
|---|---|---|---|---|
| `/api/now` | GET | `?graph_id?` | `{graph, nodes_total, nodes_resolved, surfaced_pending, presence, mode, last_event:{seq, ts, kind, summary, ...}}` **(curled live)** | the live status header |
| `/api/capabilities` | GET | — | `{node_types:[...], models:[...], modes:[...], mode_directives:{...}, mode_registry, rhm_verbs:[...], node_states:[{id,label,applies_to,means,derived_when,render:{token,icon,shape}}], panels, stt, panel_field_targets, cognition:{roles,casts,juries,fireable}, composition_config:{R2_*, MODE_AUTODETECT*}, api_verbs:[...]}` **(curled live)** | the master capability projection (§4) |
| `/api/rhm-config` | GET | — | `{mode, model, base_url, persona, timeout, voice_enabled, stt, tts_engine, tts_voice, voice_path, voice_input_mode, roles:{judge:{model,base_url}}, brain_knobs:{temperature,max_tokens}}` **(curled live)** | reflects |
| `/api/rhm-config` | POST | `{<any subset of the above>}` | the updated config — `suite.set_rhm_config` **(from code)** | configure |
| `/api/mode` | POST | `{mode}` | the new `now()` after setting the presence dial **(from code)** | the presence dial |
| `/api/models` | GET | `?kind=&base_url=` | `list[model-id]` — the live per-kind/per-endpoint model list **(curled live)** | author-from-registry |
| `/api/chat-models` | GET | — | `[{model, base_url, service, loadable, up}]` — the picker list, ollama/cloud + local vLLM **(curled live)** | author-from-registry |
| `/api/fit` | GET | `?services=k1,k2` — REQUIRED | the VRAM picture for that selection (each budget, sum vs 16GB, fit/no-fit, what to unload) **(from code, gpu.fit_report)** | S6 |
| `/api/model/load` | POST | `{service}` | `{service, state:"warming", note}` — budget-gated; **fail-loud RuntimeError → 400 naming what to evict** if it won't fit **(from code, bridge.py:927)** | no silent OOM |
| `/api/model/config` | POST | `{service, key, value}` | `{service, key, value, restarted?, note}` (or `{key, value, ...}` for `max_model_len`) **(from code)** | S5 |
| `/api/knobs` | GET | `?model=&base_url=` | `{model, base_url, knobs:{<knob>:{type, label, default, min?, max?, note, available, source}}}` **(curled live)** | G8.1 |
| `/api/run-stats` | GET | `?op=` | `{ops:[{op, who, n, duration_ms:{n,median,p95,min,max}, <metric>:{...}}]}` — run-records → distributions **(curled live)** | G7 rollup |
| `/api/voice` | GET | — | `{stt:{id:bool}, stt_default, stt_registry, stt_active, tts_up, engines:[{engine,url,up,voices,default?}], voice_enabled}` **(from code, bridge.py:467)** | a down engine reports `up:false`, never raises |
| `/api/personas` | GET | — | `[{id, name, shading, engine, voice, voice_shading}]` — the 5-cast registry **(curled live)** | G2.4/G3; author-from-registry |
| `/api/voice/switch` | POST | `{persona}` REQUIRED | `{persona, engine, service, state, note, brain_coresident_ctx?, brain_reconfig?}` — sets active + cold-loads its engine (evicts prior) **(from code, bridge.py:1099)** | Option A |
| `/api/voice/services` (alias `/api/voice/ears`) | GET | — | `{vram:{used_mb, free_mb, total_mb, util_pct}, services:{<id>:{id, title, kind:"ear"\|"engine", port, state:"up"\|"warming"\|"down", vram_mb_est}}}` **(curled live)** | G4.7 |
| `/api/voice/load` (alias `/api/voice/ear/load`) | POST | `{service\|ear}` | `'warming'` (fail-loud if it won't fit) **(from code)** | G4.7 |
| `/api/voice/unload` (alias `/api/voice/ear/unload`) | POST | `{service\|ear}` | frees VRAM **(from code)** | G4.7 |
| `/api/voice/engine-knobs` | GET | `?engine?` | the per-TTS-engine knob catalog **(from code)** | S5 |
| `/api/voice/paths` | GET | — | `{paths:{pipeline:{id,label,built,available,note,active}, s2s:{...}}}` **(curled live)** | Tier-4 swappable voice-path |
| `/api/voice/finished-thought` | POST | `{text}` | `{finished:bool, verdict:"FINISHED"\|..., text, judge_model, ms}` — the semantic-endpoint judge (brain-side) **(curled live)** | G1.3 |
| `/api/voice/log` | POST | `{event, turn_id?, ms?, ...}` | `{logged:bool}` — client-side voice trace into the one event log (lenient) **(from code)** | — |

**Voice turn (binary/streaming) routes** (request/response are NOT JSON-only — kept here for completeness):
`/api/stt` (POST raw audio bytes → transcript), `/api/voice/stt-partial` (POST partial transcript), `/api/tts`
(POST `{text}` → wav bytes, fails loud on a down engine), `/api/voice/turn` (POST → one live hear→think→speak
turn), `/api/voice/stream` (POST → newline-delimited JSON events: `{type:transcript}` · `{type:part,idx,text}`
· `{type:chunk,idx,text,wav_b64,ms}` · `{type:reply,text}` · `{type:done,...}` · `{type:error}`, bridge.py:558–564).

Conversation/thread reads: `/api/conversations` (GET `?limit=` → reopen list), `/api/conversation` (GET
`?thread_id=` → reopen + history), `/api/conversation/new` (POST `{title?}` → fresh thread).

Trial/debrief (voice-trial lane): `/api/trial/sessions` (GET), `/api/trial/transcript` (GET `?session=`),
`/api/trial/turn` / `/api/trial/feedback` / `/api/trial/reflection` (POST), `/api/debrief/start` (POST
`{session_ids:[...], host_persona?, mode?}` — REQUIRED session_ids).

---

### 1.5 · Graph / canvas — the node-graph composition face (11)

| Route | Method | Request | Response shape | Notes |
|---|---|---|---|---|
| `/api/graph` | GET | `?graph_id?` | `{id, nodes:[{id, type, config, kind, layer, status, address, content_hash, output, position:{x,y}, size:{w,h}}], ...}` — the full graph state **(curled live)** | reflects |
| `/api/graphs` | GET | — | every graph in the substrate **(from code, suite.list_graphs)** | C4 |
| `/api/object_info` | GET | — | `{<node-type>:{title, category, kind, ports:{inputs,outputs}, config_schema, output_schema, render_set, inspector_schema, actions, version}}` **(curled live, §4)** | the generic-renderer registry |
| `/api/types` | GET | — | sorted `list[type-name]` **(from code)** | C2 |
| `/api/run` | POST | `{graph_id?, force?:[node]}` | the graph `state(gid, result)` after the run (`force` bypasses the memo gate) **(from code, bridge.py:888)** | D4 |
| `/api/set` | POST | `{node, config, graph_id?}` | the new graph state **(from code)** | config write |
| `/api/move` | POST | `{node, x, y, w?, h?, graph_id?}` | the new graph state (drag-end → sibling position/size) **(from code)** | C5 |
| `/api/node` | POST | `{type, config?, position?, graph_id?}` | `{id, state}` — add a node from the palette **(from code)** | compose |
| `/api/connect` | POST | `{from_node, from_port, to_node, to_port, graph_id?}` | the new graph state (type-checked) **(from code)** | compose |
| `/api/delete-node` | POST | `{node, graph_id?}` | the new graph state **(from code)** | compose |
| `/api/ui_info` | GET | — | `{<ref>:{ref, kind, title, capabilities:{pointable,spotlit,presentable,openable,drivenReadOnly}, domHandle, cameraRef, version}}` **(curled live, §3/§4)** | the UI-component registry |

Read-status/panels/events: `/api/events` (GET → last 60 events), `/api/panels` (GET → op panels),
`/api/self-change-log` (GET `?limit=`), `/api/last-change` (GET).

Review/walkthrough organ (real shapes, curled/from-code):
- `/api/review/start` (POST `{item_ids, mode?}`) → `{session, cursor, total, item, framing}` **(curled live)**
- `/api/review/current` (GET `?session=`) → `{node, framing, ui_target}` (from code, present_current)
- `/api/review/next` (POST `{session}` → opens the gate, fires the step, advances) → `{session, cursor, total, done:bool, ...}` (mirrors status + the fired step) **(from code, suite.py:6318)**
- `/api/review/status` (GET `?session=`) → `{session, cursor, total, ...}` **(from code, suite.py:6360)**
- `/api/walkthrough/start` (POST `{item_ids?}`) → `{organ_started:bool, reason?}` (from code)
- `/api/guide/start` (POST `{topic?}`) → the system-initiated tour, `{organ_started:bool, reason?}`, model-free (from code)

---

### 1.6 · Cognition (14: 2 read/view + 12 authoring — cross-ref)

**Read / VIEW side (documented in this pack — §4 + §2):**

| Route | Method | Response | Notes |
|---|---|---|---|
| `/api/cognition_info` | GET | `{schema_ver, roles, rules, edge_kinds, thought_shapes, activation_contexts, rule_ops:[16 ops], destination_kinds:[5], casts, node_states:[7], event_kinds}` **(curled live, §4)** | the read-truth the live cognition VIEW renders from; the sibling of object_info/ui_info |
| `/api/stream` | GET (SSE) | the live event stream — `cognition.*` lifecycle + all other kinds (§2) | how the FE stays live |

(`capabilities.cognition` also carries `{roles, casts, juries, fireable}` as a summary — §4.)

**AUTHORING side (12 — cross-referenced, NOT re-documented here):**

> See **`build-prep/concurrent-cognition/AUTHORING-FE-HANDOFF.md` §B** for full request→response shapes,
> `RoleFieldSpec`/`RuleAST`/`RuleDecl`, and the UX→surface map.

- `POST /api/cognition/role/propose` · `role/edit` · `role/delete` · `role/dry_run`
- `POST /api/cognition/rule/validate` · `rule/dry_run` · `rule/attach` · `rule/detach`
- `POST /api/cognition/preview_turn`
- `GET /api/cognition/models_for_role` · `inputs` · `field_types`

The authoring write loop is **propose → (operator) `/api/resolve` approve → `/api/apply`** (apply routes by
action class `role_build`/`role_delete` to the role write-path). It rides the SAME operator-only approval seam
as everything else (§5.b/§5.c).

---

## 2 · The SSE event contract — `GET /api/stream`

**The transport** (`runtime/bridge.py:510 _stream`): the bridge **tails the shared `events.jsonl`** (so it
captures BOTH faces — UI and MCP — not an in-memory queue) and pushes each new event as standard SSE:

```
id: <seq>
data: <event-json>

```

- **Cursor:** `?since=<seq>` (default `-1` = from the start), OR the `Last-Event-ID` reconnect header — gives
  **gapless resume** on reconnect. Heartbeat `: keepalive` every ~15s so idle proxies don't drop the socket.
- **The FE protocol** (`canvas/app/src/useAppController.ts`): one `EventSource('/api/stream?since=' + cursor)`
  replaces all polling. Every event is first **merged into the activity log by `seq`** via `mergeEvents`
  (`useAppController.ts:322`) — dedup by `seq`, so the same event from two sources is never duplicated and
  `key={e.seq}` is always unique. `streamSeq` is the high-water mark; an event `<= streamSeq` is a replay and
  drives no refresh. EventSource auto-reconnects on a dropped socket (the one legitimate tolerate).
- **Every event record carries:** `kind` (the dispatch key — **NOT `op`**), `seq`, `ts`, `summary`, and
  kind-specific payload + often an `address` (`suite._emit` / `_emit_durable`, suite.py:497/568).

**The dispatch table** (`useAppController.ts:554–604`) — the FE dispatches BY KIND to the exact refresh:

| Kind(s) | FE reaction |
|---|---|
| `run` · `create` · `connect` · `delete` · `move` | reload the graph (positions/edges/nodes/status); `run` folds the scheduler's stuck/ran arrays first |
| `mode` · `config` | refresh `now()` + `rhm-config`; reload the open Settings surface |
| `cognition.*` | **fold into the live turn frame** (`foldCognition`) — see below |
| `ask` · `reject` · `resolve` · `apply` · `grow` · `revert` · `decision.*` | refresh inbox + now + last-change + panels (the wire surface) |
| `chat` · `react` | refresh the chat history (guarded against a non-array `{error}`) |
| `review.advance` · `review.start` | refresh the review card IF it's our session |
| **anything else** | the default `else` — **`setNow()` only** (see §7 gap note) |

**The `cognition.*` lifecycle** (the 6 contract kinds, `contracts/cognition_info.py:52 COGNITION_EVENT_KINDS`)
— these fold into the live cognition VIEW (Pulse → River → Nodes); a staged turn fires them in order
`turn.start → role.fire×N → part → role.ran×N → inject → part → turn.done`:

| Kind | Payload fields |
|---|---|
| `cognition.turn.start` | `{turn_id, mode, shape, grain, cast:[role_id], address:"ui://cognition/<turn>"}` |
| `cognition.role.fire` | `{turn_id, role, model, address:"run://<turn>/<role>"}` (the dot goes 'firing') |
| `cognition.role.ran` | `{turn_id, role, ok, ms, error?, address:"run://<turn>/<role>"}` |
| `cognition.inject` | `{turn_id, rule, source, role(=alias of source), into:int, chars:int, address:"run://<turn>/<source>"}` |
| `cognition.part` | `{turn_id, part:int, final:bool, staged:bool, address:"ui://cognition/<turn>"}` |
| `cognition.turn.done` | `{turn_id, total_ms, n_parts, n_roles, address:"ui://cognition/<turn>"}` |

> `cognition.wave` (the per-wave swarm-telemetry rollup) is emitted and merged into the activity log, but is
> NOT a per-turn lifecycle kind — `foldCognition` ignores it (only the 6 above touch the frame).

**Other emitted kinds** (emitted by the backend, merged into the log, dispatched by the table above — see §7
for the ones that hit the default branch): `chat`, `run`, `mode`, `config`, `ask`, `resolve`, `review.start`,
`review.advance`, `review.comment`, `review.skip`, `review.requeue`, `decision.intent`,
`decision.surfaced_for_review`, `decision.reach`, `decision.implemented`, `decision.verify`,
`decision.criterion.commit` (`criterion.commit`), `op.run`, `journey.start`, `journey.step`, `journey.stop`,
`guide.start`, `trial.debrief.start`.

---

## 3 · The address + resolution substrate

**The address grammar** (`contracts/address.py`, `SCHEMES = ("run","cas","blob","vec","ui","code")`):

```
run://<domain>/<intent>/<node>@<branch>#run=<id>   mutable pointer  — store-resolved
cas://<algo>:<hash>                                immutable content — store-resolved
blob://<algo>:<hash>                               large binary       — store-resolved
vec://<source-address>#emb=<model>                 an embedding       — store-resolved
ui://<kind>/<ref>                                  a UI component     — UI-registry-resolved (NOT the store)
code://<file-stem>/<symbol>                        a code symbol      — backend ui://→code:// resolver
```

- **`run://<turn>/<role>` resolution** — a role's structured output lands at this address (turn-scoped CAS); a
  rule reads it via a dot-path (`recall.relevant`). The canonical resolver is the `Resolver` protocol
  (`contracts/resolver.py`): `put_content`/`get_content` (cas://), `set_ref`/`head` (run://), `write_provenance`/
  `provenance`/`lineage`, `memo_get`/`memo_set` (the gate). `store/fs_store.py` is the live filesystem impl;
  swapping to Supabase changes only this Protocol's implementation (the one seam that changes FS→Supabase).
- **The `ui://` registry** (`contracts/ui_info.py`): `ui://<kind>/<ref>`, `kind ∈ chrome|field|canvas|panel|ext`
  (`ADDRESS_KINDS`). The FE resolves a target by `kind`: **canvas → camera** (`cameraRef`, a node-id the FE
  zooms to); **chrome/field/panel/ext → DOM** (`domHandle`, the `data-ui-ref` value the FE finds with
  `querySelector('[data-ui-ref="..."]')`). `build_ui_info(entries)` serializes the registry to
  `{<ref>:{...}}` (App.tsx resolver dispatches on `kind`).
- **How the FE drives via addresses (reflects-never-owns):** the FE never writes a file. It (a) reads the
  registries/projections, (b) POSTs a structured `{verb, address, args}` to `/api/act` (or an address-keyed
  intent to `/api/intent-at`, comment to `/api/annotate`, pref to `/api/presentation-pref`), (c) reads back the
  surfaced result. **Empty scope = DENY-ALL** — an orphan/stale address never fabricates reach.

---

## 4 · The projections (registry-as-data — the generic-renderer pattern)

**The pattern (ComfyUI's proven generic renderer):** the FE holds NO per-type code. It asks the backend for the
whole registry, serialized, and builds the palette / every render-mode / every inspector / the cognition view
FROM it. **Add a registry entry backend-side → it appears in the FE, no FE code.** The serializers are
generated FROM the registry and fail loud on a malformed entry (object_info.py:72; ui_info.py:111). These are
the FE's read-truth (mirrored into `registryStore.ts`).

| Projection | Endpoint | Shape (real, curled) | Drives |
|---|---|---|---|
| **object_info** | `GET /api/object_info` | `{<node-type>:{title, category, kind, ports:{inputs,outputs}, config_schema, output_schema, render_set, inspector_schema, actions, version}}`. A `config_schema` field declares `{type:"enum", label, default, options_from:"chat_models"}` — the dropdown's options come from a named endpoint, never hardcoded. | the palette, every node render-mode, the generic inspector form (`registryStore.OINFO`) |
| **ui_info** | `GET /api/ui_info` | `{<ref>:{ref, kind, title, capabilities:{pointable,spotlit,presentable,openable,drivenReadOnly}, domHandle, cameraRef, version}}` | what's addressable + how it resolves (`registryStore.UI_INFO`) |
| **cognition_info** | `GET /api/cognition_info` | `{schema_ver, roles, rules, edge_kinds, thought_shapes, activation_contexts, rule_ops:[field,lit,and,or,not,eq,ne,lt,le,gt,ge,add,sub,mul,in,contains], destination_kinds:[inject,chain,address,surface,lane], casts, node_states:[idle,ran,cached,stuck,failed,live,empty], event_kinds}` | the live cognition VIEW + the authoring dropdowns (`registryStore.COGNITION_INFO`). **rule_ops + destination_kinds ARE the closed grammar** — cross-ref AUTHORING-FE-HANDOFF.md §C |
| **capabilities** | `GET /api/capabilities` | `{node_types, models, modes, mode_directives, mode_registry, rhm_verbs, node_states:[{id,label,applies_to,means,derived_when,render:{token,icon,shape}}], panels, stt, panel_field_targets, cognition:{roles,casts,juries,fireable}, composition_config:{R2_LAMBDA, R2_*, MODE_AUTODETECT, MODE_AUTODETECT_OPTIONS}, api_verbs}` | the master capability/config projection; `node_states` paints status dots everywhere (`registryStore.NODE_STATES`) |
| **MODEL_CAPABILITIES** | (backend table) | `ops/cli/capabilities.py:57` — the intrinsic model-capability registry (`{value, source}` per field). `provides_for`/`suitable_models`/`role_can_bind` drive `GET /api/models`, `/api/chat-models`, and `/api/cognition/models_for_role`. A model NOT in it returns a fail-loud "capabilities unknown" (rule 8). | which models are bindable per role/kind (author-from-registry) |

---

## 5 · The LAWS the FE must honor

These are collected from across the surface (`runtime/AGENTS.md`, `contracts/AGENTS.md`,
`canvas/app/src/AGENTS.md` / the handler comments). They are non-negotiable; generated FE that violates one is
wrong even if it renders.

- **a · Reflects-never-owns.** The backend is the single source of truth. The FE reads registries/projections
  and drives via addresses + endpoints; it NEVER writes a role/node/config file directly. Every `registryStore`
  field is READ TRUTH from the backend (`registryStore.ts:10`).
- **b · Propose-not-apply.** Every consequential write SURFACES for operator approval (returns a surfaced `id`,
  `resolved=null`); nothing is live until the operator approves (`/api/resolve`) and applies (`/api/apply`).
  **Never auto-apply.** Show the surfaced item + its rendered payload for review; route approve→apply.
- **c · The `claude -p` / dispatch floor is OPERATOR-ONLY.** No FE path, no role, no rule may forge
  resolve/approve/dispatch. `/api/resolve`, `/api/act`, `/api/apply`, `/api/checkpoint`, `/api/revert`,
  `/api/pin`, `/api/approve-reach`, `/api/build-intent`, `/api/intent-at` are the OPERATOR face — off the
  MCP/agent face. A rule destination is NEVER `resolve`/`approve`/`dispatch` (`FORBIDDEN_DESTINATION_VERBS`).
- **d · The rule grammar is closed + renderable.** Offer ONLY `cognition_info.rule_ops` (16 ops) and
  `cognition_info.destination_kinds` (the 5: inject/chain/address/surface/lane) — never free text, never a 6th
  destination. Respect the depth cap (validate returns `renderable`; if false, the rule is too deep to draw —
  surface that). (Full: AUTHORING-FE-HANDOFF.md §C/§E.)
- **e · `run://` addressing.** A rule reads role outputs at `run://<turn>/<role>` (the inputs from
  `GET /api/cognition/inputs`). Never invent another scheme; UI targets use `ui://<kind>/<ref>`.
- **f · Author-from-the-registry.** Every dropdown (models, field types, inputs, modes, destinations, ops,
  node-types, voices, personas, knobs) comes from an endpoint — never a hardcoded FE list. A new entry added
  backend-side appears in the dropdown automatically (`config_schema.options_from`, `capabilities`, the
  projections).
- **g · Fail-loud.** A malformed request fails loud: **HTTP 400 with `{"error":"<ExcType>: <msg>"}`**. Surface
  the error string — never silently swallow, never fabricate a success. A down voice engine reports `up:false`
  (greyed out), an OOM-risk model-load names what to evict.
- **h · Design-system tokens only.** Render from `canvas/app/src/design/_system/` tokens (e.g. `node_states[].render.token`
  is a token like `--tx-3`) — no hardcoded colors/spacing. (See §6.)
- **i · tldraw 3.15.6.** The canvas is tldraw 3.15.6 (pinned, symlinked `node_modules` on the worktree). **Bump
  `persistenceKey`** whenever a shape's props change, or stale persisted shapes break the canvas.

---

## 6 · Where Claude Design output lands (the FE structure map)

Generated FE code must extend the existing shapes, not stand up a parallel surface. The FE lives in
`canvas/app/src/`:

```
canvas/app/src/
  App.tsx                 — the shell; pre-carves the regions; the ui://→DOM/camera resolver dispatch
  main.tsx                — entry
  useAppController.ts     — THE CONTROLLER. All state, the EventSource/SSE dispatch (§2), every api call,
                            the folds (foldCognition, decision.*, review). New behavior wires in HERE.
  api.ts                  — THE FETCH LAYER. One method per endpoint (api.chat, api.act, api.resolve,
                            api.buildIntent, api.cognitionInfo, api.uiInfo, ...). A new route → add a method HERE.
  registryStore.ts        — THE READ-TRUTH STORE (reflects-never-owns): OINFO, MODEL_OPTIONS, UI_INFO,
                            NODE_STATES, COGNITION_INFO. Read FROM here; never duplicate a registry in a component.
  NodeShape.tsx           — the tldraw node shape (renders OUTSIDE React context; reads getNODE_STATES())
  AppContext.ts           — shared context
  regions/                — the panels: Activity, AddressHelp, CognitionView, Fleet, Grow, History, Inbox,
                            Inspector, OpPanels, Palette, ProposeAffordance, RhmChat, SelfChanges, Settings,
                            Toolbar, Versions, Walkthrough, Workshop. EXTEND a region (don't add a parallel panel).
  components/             — reusable: BlastRadiusReach, BuildIntentCard, ContextBundle, NodeConfigForm,
                            PanelErrorBoundary, PanelView, ShapeHow, WireRequest, kit.tsx
  extensions/            — extension points
  design/_system/        — the design system (tokens). Render from these (law §5.h).
```

**Placement rules for generated code:**
- A new endpoint → **add one method in `api.ts`** (match the existing `fetch(...).then(jr)` shape; `jr` is the
  fail-loud JSON reader that surfaces `{error}`), then call it from the controller.
- New live behavior → **wire it in `useAppController.ts`** (add to the SSE dispatch table if it reacts to an
  event kind; otherwise a fetch + setState).
- A new read → **read from `registryStore.ts`** (it already holds the projections); do not re-fetch a registry
  into component state.
- A new panel/affordance → **extend a `regions/` component**; reuse `components/NodeConfigForm.tsx` for any
  schema-driven config form (it's the generic form pattern; the cognition role-config form is this pattern over
  a role's fields — AUTHORING-FE-HANDOFF.md §D).
- The propose→approve→apply UX → reuse `regions/Inbox.tsx` + `regions/ProposeAffordance.tsx` + the
  `/api/resolve` + `/api/apply` buttons. The wire surface → `components/BuildIntentCard.tsx` /
  `components/WireRequest.tsx` / `components/BlastRadiusReach.tsx`.
- The live cognition view → reuse `regions/CognitionView.tsx` (Pulse→River→Nodes; already folds the
  `cognition.*` SSE). Authoring forms EXTEND it.

---

## 7 · Genuine gaps found (read-the-code findings — not invented)

1. **`GET /api/roles` is BROKEN (returns HTTP 400, not its data).** Curled live:
   `{"error":"TypeError: Object of type ModelMetaclass is not JSON serializable"}`. `Suite.roles()`
   (`runtime/suite.py:4439`) returns a dict that still holds a Pydantic model **class** (a `BaseModel`
   subclass / `ModelMetaclass`) which `json.dumps` cannot serialize. The route is wired (bridge.py:495) but is
   **not currently consumed by `api.ts`** (no `roles()` method in the fetch layer) — so it is not breaking the
   live FE today, but **any new FE that calls `/api/roles` will get a 400.** This is the model-ROLE registry
   (the judge/config-lab binding, distinct from cognition roles) — it needs a serialization fix backend-side
   before the FE can rely on it. **Flag for the lead.**

2. **Several emitted event kinds have NO dedicated FE dispatch branch — they hit the default `else`
   (`setNow()` only)** (`useAppController.ts:602`). Emitted-but-undispatched: `op.run`, `journey.start`,
   `journey.step`, `journey.stop`, `guide.start`, `trial.debrief.start`, `cognition.wave` (merged to the log
   but no frame fold — that one is intentional). So a journey-record, a guided-tour start, a debrief start, and
   every run-record telemetry event update only the `now()` header, not a purpose-built surface. Not
   necessarily a bug (some are log-only by design), but **any FE that should react live to journeys/guides/
   debriefs/telemetry must add a dispatch branch** — they are not handled today.

3. **`/api/cognition_info` serves an `event_kinds` top-level key** (the serialized `COGNITION_EVENT_KINDS`)
   that the AUTHORING-FE-HANDOFF.md §C.1 shape does not list (it lists the other 9 keys). Confirmed live: top
   keys are `[schema_ver, roles, rules, edge_kinds, thought_shapes, activation_contexts, rule_ops,
   destination_kinds, casts, node_states, event_kinds]`. Additive (an older FE ignores it), but the FE can read
   the SSE event contract directly off this projection rather than hardcoding it — worth using.

4. **`node_states` is served in two places with slightly different shapes** — `capabilities.node_states`
   carries the full `{id,label,applies_to,means,derived_when,render:{token,icon,shape}}` (the FE indexes
   `registryStore.NODE_STATES` from here), while `cognition_info.node_states` is the cognition-view status-dot
   vocabulary. Both are real and consistent in `id` set (`idle,ran,cached,stuck,failed,live,empty`); the FE
   should source the render tokens from `capabilities` (where `render` lives). Noting so generated code reads
   the right one.
