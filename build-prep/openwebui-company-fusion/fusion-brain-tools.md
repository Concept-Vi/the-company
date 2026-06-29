---
type: proposal
title: The Fused Brain + Tools — RHM × OpenWebUI (model + tool seam)
subject: how the Company's RHM/loadout/MCP-tools and OpenWebUI's manifold-models + native-MCP tool surface fuse into ONE thing, built INTO the Company
posture: both sides incomplete, AI-generated, unreviewed; no source of truth; no horizon; best parts fused, built INTO THE COMPANY; no duplicates. Written provisional — assumptions + file:line refs inline; correct directly.
created: 2026-06-28
verified_live: 2026-06-28 (results in §5 — trust nothing; these are the checks actually run)
relates-to: ["[[area-A-runtime-core]]", "[[area-C-ops-foundation]]", "[[area-E-mcp-roles-skills]]", "[[owui-side-map]]"]
---

# The Fused Brain + Tools

> Reading note. Two questions are kept SEPARATE on purpose (the advisor caught me conflating them):
> **(a) DESIGN** — which seam should carry the brain, and which should carry the tools, so there are no duplicates.
> **(b) A LIVE BUG** — the bridge HTTP face (`:8770`) wedged mid-session under load (every route hung), while the
> underlying brain was healthy (in-process `SUITE.chat`→"PONG" in 2.9s). **A clean `company restart bridge` cleared
> it; `/api/chat/stream` then streamed fine** — so the wedge is load-induced, not a logic bug, and the §2c stream
> seam is sound. Section 4 traces it; the durable per-request-deadline fix is still owed.

---

## 1. BEST PARTS (what each side is genuinely good at — surface, don't decide)

### Company side
- **RHM as a source-resolver, not a model** (`runtime/brain_router.py:54 route_source`, `:120 ask`). The brain is
  ONE altitude up: it RESOLVES which cognition-SOURCE answers — `fleet` (live fabric roster), `recall` (grounded
  memory, declared seam), `model` (the conversational mind). Read+propose floor; never spawns. This is the spine's
  resolver primitive, not a parallel brain.
- **Brain-is-a-role-resolved-to-a-model** (`brain_router.py:_model_answer`, `runtime/suite.py:2680 rhm_config`).
  The model is a CONFIG SLOT (`rhm_config().model`), swappable at runtime via `set_rhm_config` (suite.py:2732),
  governed verbs (`configure` sets model/persona/mode/stt/tts/roles — suite.py:4281,4348). VERIFIED live: the slot
  currently resolves to the local vLLM 4B at `:8000/v1` (§5), and the TIM-RULE context-size pick
  (`cc_clone.pick_ollama_model_for_context`, kimi default) is the brain_router leg's resolver.
- **80 MCP `op`s across 28 consolidated tools** (`mcp_face/tools/*.py`, one-tool-per-resource + `op` selector;
  file-discovered via pkgutil; `mcp_face/server.py`). Governed: floor = NO resolve/approve/dispatch/claude -p;
  CQRS read/write split; per-tool `posture` annotation the remote gateway reads. (Count caveat in §5.)
- **Governed verbs + fail-loud tool gate** — `suite.py:4485 _model_supports_tools` PROBES the endpoint
  (ollama `/api/show` caps · litellm `model_info` · vLLM forced-tool-call), RAISE→False = the safe refusal. No
  silent assume-capable.
- **Loadout = service registry** (`ops/services.json` combos: wake / interaction / xsession-brain), VRAM-gated by
  `company` CLI; the brain model is one row that the loadout brings up.

### OpenWebUI side (donor — stock upstream 0.9.6, `owui-side-map.md`)
- **Manifold Pipe = dynamic, runtime-computed model list** (`functions.py:71-144,84-121`). A Pipe that returns
  `pipes` injects N sub-models into the picker — the clean way to expose a *list* of role-models, not a single id.
- **Native MCP tool surface** (`utils/tools.py:321-427`, and CONFIRMED in `routers/tools.py:117`: a tool server with
  `type:'mcp'` is resolved into the same `tools_dict` as in-process/OpenAPI/terminal tools). OWUI models can call an
  external MCP server's tools natively, with OAuth 2.1 auth (`utils/tools.py` execute_tool_server).
- **Tool-calling UX** — native (specs to model API) and default (prompt+parse) from the SAME callable; `citation`,
  `file_handler`, per-model `meta.toolIds`, access-gated.
- **Channels + AI-as-participant** (`owui-side-map.md §2`) — already exploited by `ops/owui_room.py` (see §2.4).
- **Streaming + voice-call UX** (sentence-split TTS) — the reason the adapter exists at all (voice-chat the RHM).

---

## 2. THE FUSED BRAIN + TOOLS (the design — concrete, de-duped)

There are **THREE live OWUI↔Company seams today**, not one. The de-dup answer must span all three:

| # | Seam | What it carries | File | State |
|---|------|-----------------|------|-------|
| S1 | **OpenAI-shim adapter `:4300`** | the RHM as a single model `operator` | `ops/fabric_openai_adapter.py` | LIVE (picker entry present); upstream `/api/chat` works on a healthy bridge (§4.1) |
| S2 | **owui_room channels-operator** | a spawned Claude Code session (`operator`) with FULL `mcp__company` tools, reached via channel webhooks | `ops/owui_room.py:363 op_spawn_operator` | LIVE path; parallel mechanism |
| S3 | **native MCP gateway `:8772` (remote)** | the 28-tool/80-op MCP face, OAuth-gated | `mcp_face/remote.py`, `serve_remote.sh` | running; transport-fit to OWUI UNVERIFIED (§5) |

### 2a. Should the RHM be ONE 'operator' model or a manifold of role-models?
**Recommendation: BOTH, by role — and it resolves the S1 design cleanly.**
- Keep **one `operator` model** as the default conversational face (what voice-chat talks to). That IS the RHM's
  `ask()` resolver (fleet/recall/model) — a single entry is correct for the conversational altitude; the RHM already
  does the internal source-resolution, so exposing its internals as separate picker models would duplicate the
  resolver one layer too high.
- ADD a **manifold** (OWUI Pipe returning `pipes`, `functions.py:84-121`) that enumerates the **named brains/roles**
  the loadout/registry actually offers — e.g. `operator` (RHM), `fleet` (supervisor-sight), and the swappable raw
  models the loadout can bring up (4B / nemotron / kimi). The manifold's source of truth = the Company registry
  (`models_for_role`, `rhm_config`, `services.json` combos), so the picker is registry-resolved, not hand-listed.
- Net: ONE conversational operator + a registry-driven manifold for explicit role/model selection. No second brain.

### 2b. Expose the 68/80 MCP tools to OWUI NATIVELY (its `type:'mcp'` surface) instead of via a tool-bearing adapter?
**Recommendation: YES — native MCP, conditional on the transport-fit check (§5 verify-item).**
- OWUI's `routers/tools.py:117` proves a native `type:'mcp'` tool-server is first-class. The Company already has the
  MCP face and a remote HTTP gateway (`mcp_face/remote.py` on `:8772`). The clean fusion is: **register the Company
  MCP gateway as an OWUI MCP tool-server**, so OWUI models call the governed fabric verbs directly — through the SAME
  posture/auth/teaching-error path every other client uses (`remote.py` `_tool_posture` gate).
- This DELETES the need for S2's parallel channels-operator-as-tool-runner *for the tool-calling purpose* (S2's
  Channels value — multi-participant timeline — can remain, but tools should not be a second path).
- **BLOCKER to verify first** (advisor-flagged, not yet proven): `mcp_face/server.py:1242` runs
  `mcp.run(transport="stdio")` — stdio, which OWUI's MCP client CANNOT reach. The HTTP path is `remote.py` (:8772),
  but it was NOT verified to speak the streamable-http/SSE transport OWUI expects, NOR that the Tim-only identity gate
  admits an OWUI service principal. Both are §5 verify-items. The native-tool recommendation rests on them.

### 2c. Is the OpenAI-shim the right seam, or a Pipe function?
**Recommendation: a Pipe, and fold the shim into it — eliminating S1 as a separate process.**
- The shim (`fabric_openai_adapter.py`) is a 90-line stdlib HTTP server re-implementing OpenAI chat-completions +
  SSE streaming + a `/models` list — exactly what OWUI's **manifold Pipe** gives natively (`functions.py:71-144`,
  full streaming `:289-341`). A Pipe that POSTs the RHM endpoint and yields its stream is the same behaviour with:
  zero extra process/port, native picker integration, native injected context (`__user__`, `__chat_id__`,
  `__event_emitter__` — adapter has none), and it lives as a DB row, not an external service to keep alive.
- So: **the operator model + the role manifold both become ONE Pipe function** (§2a), and **tools go native MCP**
  (§2b). The adapter `:4300` retires once the Pipe is in.

### De-dup summary (the whole picture)
```
BEFORE (3 seams, overlapping):           AFTER (clean split, built INTO the Company):
 S1 shim :4300  → RHM (1 model)            BRAIN  = OWUI Pipe/Manifold → RHM /api/chat-stream
 S2 owui_room  → operator-as-CC + tools             (operator + registry-driven role manifold)
 S3 :8772 MCP  → 80 ops (stdio/HTTP?)      TOOLS  = OWUI native type:'mcp' → Company :8772 gateway
                                            CHANNELS = owui_room keeps the timeline value, drops tool-runner role
```
Brain and tools become two clean OWUI-native seams onto the ONE Company spine; the shim and the parallel tool path go.

---

## 3. COMPANY-INTERNAL ISSUES (with resolutions)

1. **`DEFAULT_BRAIN = deepseek-v4-pro:cloud` (the flagged -pro anti-pattern) is STILL the config fallback**
   — `fabric/config.py:21`. VERIFIED. It is referenced as a live fallback in `suite.py:1397, :2684, :9397, :9537,
   :11387, :11484`. The brain ITSELF doesn't hit it (rhm_config resolves to the 4B — §5; brain_router passes kimi
   explicitly), but every code path that does `model or fcfg.DEFAULT_BRAIN` silently lands on -pro if its caller
   omits a model. **Resolution:** make the fallback the TIM-RULE resolver (`pick_ollama_model_for_context`), not a
   pinned -pro constant; or set `COMPANY_BRAIN` env to kimi so the constant can never be -pro. Audit each
   `or fcfg.DEFAULT_BRAIN` call-site (6 found) — these are the silent -pro doors.
2. **The `model_binding`-nesting trap** (`runtime/roles.py:33`, area-E note 6) — `default_model` MUST be top-level
   on a ROLE dict; nested inside `model_binding` it is silently unread → falls to DEFAULT_BRAIN(-pro). **Resolution:**
   a drift/acceptance check that asserts `resolve_role(id)['model'] != DEFAULT_BRAIN` for any role declaring a model
   (verify by-use, not by-read — the doc's own warning).
3. **`_model_supports_tools` gate is correct but cannot-determine → False is uncached** (`suite.py:4485-4517`) — a
   transiently-down endpoint makes the brain refuse tools until it recovers. This is the SAFE choice (no silent
   assume-capable) and recovery is immediate (False not cached). **No change needed**; documented so the OWUI Pipe
   knows a tool-less turn during endpoint warm-up is expected, not a bug.
4. **Loadout model selection is registry-correct** — `rhm_config().model` + `services.json` combos drive it; the
   manifold (§2a) should READ this, never hand-list. No issue; this is the seam to reuse.

---

## 4. BROKEN / HALF-BUILT SEAMS (traced)

1. **THE BRIDGE HTTP FACE `:8770` WEDGED MID-SESSION — load-induced, CLEARED BY RESTART. Brain is healthy.**
   - Symptom: after a run of long hanging requests, `/api/now`, `/api/chat`, `/api/brain/ask`, `/api/chat-models`,
     `/api/rhm-config` ALL hung (0 bytes) — VERIFIED §5. `/api/now` answered INSTANTLY at session start, so the wedge
     developed during the session under my own probing.
   - Discriminator 1 (in-process): `SUITE.chat("...","codebase")` returned "PONG" in **2.9s** (§5) — the
     application/brain layer is healthy; the stall is at the HTTP server.
   - Discriminator 2 (DECISIVE — clean restart, advisor-prompted): after `company restart bridge`, with NO load:
     `/api/now` FAST, `/api/chat/stream` streamed "PONG", `/api/chat` returned "PONG" with
     `model: cyankiwi/Qwen3.5-4B-AWQ-4bit` (§5). **The wedge is LOAD-INDUCED and clears on restart; it is NOT an
     HTTP-path-specific logic bug.** This proves the §2c stream seam (`/api/chat-stream`) is SOUND on a healthy bridge.
   - Mechanism (CANDIDATES — not root-caused; I did not capture a thread dump of the wedged PID): a process-level
     stall on the stdlib `ThreadingHTTPServer` (`area-A` bridge.py:67, "No Flask/FastAPI") under a burst of
     long-blocking requests, plausibly lock contention with the always-on `_freshness_loop`/`_warm_vector_cache`
     background work (bridge.py:106). **Thread-exhaustion-by-holding is RULED OUT** — ThreadingHTTPServer spawns
     unbounded threads, so held workers can't saturate it. **Resolution:** `company restart bridge` clears it (proven);
     the durable fix is a per-request deadline + a bounded worker pool on the bridge (stdlib server has neither). For
     the definitive mechanism, a `py-spy dump` of a wedged PID would name it — owed if the wedge recurs in normal use.
   - This OVERTURNS my first hypothesis (that `/api/chat` hung because it omits `model` and falls to -pro). FALSE:
     `/api/chat` (bridge.py:2976) calls `SUITE.chat` with no model → reads rhm_config → the 4B → works (PONG, §5).
2. **MCP face transport mismatch for OWUI** — `server.py:1242` is stdio-only; the HTTP gateway `remote.py` exists but
   its OWUI-MCP transport-fit + auth-admit is unverified (§2b, §5). Half-built for THIS purpose until proven.
3. **vLLM cold-start / autostart** — `services.json`: nothing autostarts at boot except surface (canvas+bridge);
   the 4B (`chat-4b` :8000) is the resident default brain and was UP (§5). But the brain's loadout dependency is
   implicit — if the operator Pipe is asked while `:8000` is down, the gate refuses tools (issue 3.3). The 4B has no
   warm-on-demand from OWUI's side; the loadout must be up first (`company up wake`/`interaction`). No autostart bug,
   but a documented ordering dependency for the fusion.
4. **`channel_boundary.py` Realtime subscriber still stubbed** (area-A §7) — not on the brain+tools path, flagged for
   completeness: shared-channel inject transport is pending a builder; doesn't block this fusion.

---

## 5. VERIFICATION DONE (live checks + results, 2026-06-28)

| Check | Command / method | Result |
|-------|------------------|--------|
| bridge up (start) | `GET :8770/api/now` | **OK instant** — graph codebase, 19 nodes, seq 9810 |
| bridge up (later, under load) | `GET :8770/api/now`, `/api/chat-models`, `/api/rhm-config` | **ALL HANG** (0 bytes) — wedged mid-session under my own probing (§4.1) |
| **bridge after `company restart bridge`** | `GET /api/now` · `POST /api/chat/stream` · `POST /api/chat` | **ALL FAST** — now OK; stream→"PONG"; chat→"PONG" `model:Qwen3.5-4B-AWQ`. Wedge is load-induced, clears on restart (§4.1) |
| vLLM 4B | `GET :8000/v1/models` | UP — `cyankiwi/Qwen3.5-4B-AWQ-4bit`, max_model_len 16384 |
| ollama / kimi | `GET :11434/api/tags`, `/api/show kimi-k2.7-code:cloud` | UP; kimi caps = `[vision, thinking, completion, tools]` |
| OWUI | `GET :8080/health` | listening (empty body) |
| adapter `:4300` | `GET /v1/models` | UP — returns `operator` model |
| supervisor `:8771` | `GET /health` | UP — 6 sessions (5 closed, 1 idle), cap 3, permission "plan" |
| adapter end-to-end | `POST :4300/v1/chat/completions operator` | **EMPTY** (its upstream `/api/chat` is wedged) |
| `/api/chat` direct | `POST :8770/api/chat` ×3 | **HANG** (0 bytes, 40–95s) |
| `/api/brain/ask` | `POST :8770/api/brain/ask` | **HANG/EMPTY** |
| **rhm_config.model** | in-process `SUITE.rhm_config()` | **`cyankiwi/Qwen3.5-4B-AWQ-4bit` @ `:8000/v1`** (NOT -pro) |
| **SUITE.chat default** | in-process `SUITE.chat("...","codebase")` | **"PONG" in 2.9s** — brain layer healthy |
| DEFAULT_BRAIN | `fabric/config.py:21` + in-process | `deepseek-v4-pro:cloud` — the -pro anti-pattern, live as fallback |
| OWUI native MCP | `routers/tools.py:117` (installed) | CONFIRMED — `type:'mcp'` tool-server is first-class |
| MCP face transport | `mcp_face/server.py:1242` | `mcp.run(transport="stdio")` — stdio only; HTTP is `remote.py` |
| MCP op count | pkgutil over `mcp_face/tools/` | **28 modules; 80 ops measured across 14 importable-in-harness modules.** UNRELIABLE — 14 modules failed to import in the bare harness (no `OPS` reached), so 80 is partial. `remote.py:42` comment says **66 tools**; the prompt says 68. Discrepancy unresolved — report measured, do not manufacture reconciliation. |

### VERIFY-ITEMS still owed (NOT done — flagged, not green)
- Does `mcp_face/remote.py` (:8772) speak **streamable-http/SSE** in the shape OWUI's MCP client connects with? (the native-tool recommendation §2b depends on it)
- Does the Tim-only identity gate on `:8772` admit an **OWUI service principal** (or need a scoped principal)?
- Does an OWUI **manifold Pipe** streaming `/api/chat-stream` reproduce the operator UX (incl. voice-call sentence-split)? (the §2c recommendation depends on it — the seam itself is now PROVEN sound, §4.1; the Pipe wrapper is what's unbuilt)
- ✅ DONE: bridge wedge confirmed load-induced — clears on `company restart bridge`, `/api/chat-stream` fast on a clean bridge (§4.1). The durable per-request-deadline fix is owed (option B).

---

## NEXT-STEP OPTIONS (the design is a proposal — pick a direction)

- **A — Depth/Understanding:** run the four verify-items above (esp. the :8772 transport-fit) before any build, so the native-MCP-for-tools decision is grounded, not inferred. Recommended if the tool seam is the priority — §2b's whole case rests on it.
- **B — Fix the live bug first:** restart the bridge, add a per-request timeout + bounded worker pool to the stdlib server (§4.1). This is independently needed (the wedge will recur) and de-risks every demo of the fusion.
- **C — Tentative artifact:** draft the OWUI **manifold Pipe** (operator + registry-driven role list, streaming `/api/chat-stream`) as a real function file — materialize §2a+§2c so it can be corrected directly. The Pipe is the load-bearing new piece; building it surfaces the real injected-context + streaming questions.
- **D:** kill the `DEFAULT_BRAIN=-pro` anti-pattern at its 6 call-sites + add the role-binding drift check (§3.1, §3.2) — a small, self-contained company-internal cleanup that removes a class of silent-wrong-brain bugs regardless of the OWUI work.
