# R2 · `chat()` → shared-core refactor — detailed trace, extraction plan, preservation list, risks

*Read-only deep trace of `Suite.chat()` (`runtime/suite.py:3347–3554`, live worktree, located by symbol) in service of triad G4 / R1-FOLD **F4**: `chat_parts()` (N parts) cannot loop or copy `chat()`; it forces extracting `chat()`'s body into a **shared core** that both `chat()` (N=1) and `chat_parts()` (N>1) call — the highest-blast-radius edit on the `rhm_*`-gated hot path. Maps what the refactor touches, where single-shot assumptions are baked in, the EXACT "what still works" preservation list, and the riskiest breakage.*

**Anchor symbols (drift ~+14 from the triad's stale line refs — locate by symbol):** `chat()` = suite.py **3347–3554**; capability gate `_model_supports_tools`; `rhm_config` **1143**; `get_mode` **1077**; `_mode_directive`; `_model_of_tim_digest`; persona via `voice/personas.py::get_persona().brain`; `_chat_context` **1336**; `_affordance_context` **2104**; `available_verbs`; `_rhm_tools` **2136**; the model call `fabric.client.complete_with_tools` (reached through the MODULE ref `from fabric import client`); `_json_obj_to_action`; `_dispatch_rhm_action` **2645**; `autonomous_dispatch`; `_confirmation_for`; `_provenance_grade/_source`.

---

## 0 · The decomposition frame — turn-level-once vs part-level-N

The body splits into **three layers**; the key design fact is that the **extraction boundary sits BELOW the return.** `chat()` is the N=1 instance.

```
TURN PROLOGUE (once per turn)          ← never per-part
  get_mode → off short-circuit
  capability gate (_model_supports_tools) → refusal short-circuit
  persona resolution (personas.get_persona.brain)
  _model_of_tim_digest()
  [user-turn append: EARLY in off/refusal, LATE in normal — Trap 2]

PER-PART CORE (×N)                      ← the extracted shared callable
  build msgs (sys head + _chat_context + chat_history(20) + user/part-cue)
  _affordance_context → _rhm_tools
  client.complete_with_tools(... **brain_knobs)
  tool_call loop:
     suggest → proposal (no dispatch)
     verb not offered → {did:none, refused}
     decide-for-me → autonomous_dispatch(RHM_VERB_CLASS, _dispatch_rhm_action)
     else → _dispatch_rhm_action
  confirmation fold (_confirmation_for / consult / ask)
  → ONE reply-unit: (text, outcomes[], proposals[])

TURN EPILOGUE (once per turn)          ← never per-part
  assistant append(s) (provenance grade/source)
  action_field shaping (None / dict / list)
  the ONE "chat" event emit
  thread bump (last_msg/title)
  RETURN dict  (chat) | NDJSON stream of parts  (chat_parts)
```

**Single-shot-shaped vs part-shaped:** the per-part core is part-shaped (reusable N times). The return assembly `{reply, action, proposal, mode, model, thread_id, history}` is **single-shot-shaped** — it wraps exactly one reply-unit. The shared core **cannot include return assembly**: `chat()` wraps the one unit; `chat_parts()` streams N units as ndjson with a turn-level epilogue. This boundary is the heart of F4.

---

## 1 · Full body trace (every segment)

| Lines | Segment | Layer | Notes |
|---|---|---|---|
| 3353–3359 | `get_mode()`; `mode=="off"` short-circuit | prologue | appends user (`grade:gold/source:operator`) + canned off-reply (`grade:working/source:twin`), emits `chat`, returns **4-key** `{reply,action,mode,history}` |
| 3360–3362 | imports; `cfg = rhm_config()` | prologue | cfg = model/base_url/timeout/persona/brain_knobs |
| 3364–3381 | **CAPABILITY GATE** `_model_supports_tools` | prologue | refusal: appends user+refusal, emits `warning`, returns **5-key** (`+model`). No model call, no fallback (rule 4); unreachable endpoint → also refused |
| 3383–3395 | persona → `persona_text` (`get_persona().brain`) | prologue | unknown persona falls through verbatim |
| 3396–3416 | **system head** `sys_p` | per-part | identity + ground-truth rule + persona + `_model_of_tim_digest()` + `_mode_directive(mode)` + tool-only acting rule |
| 3418–3421 | `actx=_affordance_context`; `tools=_rhm_tools(mode,actx)` | per-part | native tools array, mode×context |
| 3423–3426 | `msgs` = `[system: sys_p + _chat_context(graph,focus)]` + `chat_history(20)` + `{user:message}` | per-part | history + system context are the part-shaped inputs |
| 3436–3441 | brain_knobs; `client.complete_with_tools(...)`; `reply=content or ""` | per-part | THE model call; FabricError propagates (no fallback) |
| 3443–3500 | **tool_call loop** | per-part | `offered=available_verbs`; `suggest`→proposal; not-offered→`{did:none}`; `decide-for-me`→`autonomous_dispatch`; else→`_dispatch_rhm_action`. Accumulates `outcomes`,`proposals` |
| 3502–3516 | **confirmation fold** | per-part | consult→`📖`; ask→`❓`; else→`_confirmation_for` appended/becomes reply |
| 3518–3526 | `action_field` shaping (None/dict/list) | epilogue | per-turn reduction of `outcomes` |
| 3527–3545 | **assistant + user append** + thread bump | epilogue | user append LATE (3532); `_provenance_grade/_source`; thread best-effort |
| 3546 | `_emit("chat", …)` ONE chat event | epilogue | locus `ui://chrome/chat` |
| 3547–3554 | `proposal=proposals[0]`; **return** 7-key incl. thread-aware `history` | epilogue | single-shot return |

---

## 2 · Where single-shot assumptions are baked in

1. **Return dict = one reply-unit** (3551–3554). Part-shaped output is N units → return assembly is turn-level → cannot be in the shared core.
2. **`action_field` ∈ {None, dict, list}** (3518–3526) is a per-turn reduction. For N acting parts, merging outcomes across parts is **net-new** logic, not preserved behaviour.
3. **`proposal = proposals[0]`** (3550) — only the first proposal of the whole turn survives; N-part proposals undefined.
4. **ONE `_emit("chat")`** per turn (3546) — F4 requires N parts still emit ONE.
5. **User-turn append once** (3532 / early in off/refusal).
6. **`chat_history(20)`** (3424) reads the PERSISTED log; within a turn no part is persisted until the epilogue, so later parts do NOT see earlier parts via history — they see them via the F3 **`run://`** ref-read (net-new, Guide G4).
7. **Three return shapes** (off=4-key, refusal=5-key, normal=7-key) — Trap 1.

---

## 3 · Traps the trace surfaced (load-bearing breakages)

**Trap 1 — three return shapes + a provenance asymmetry.** off/refusal **hardcode** `grade:"gold"/"working"` + `source:"operator"/"twin"`; the normal path uses `_provenance_grade`/`_provenance_source`. A naive "hoist user-append into one shared place" extraction would **silently change off/refusal provenance**. Keep both short-circuits as prologue-level early returns that do NOT route through the shared core.

**Trap 2 — user-append placement differs by path.** off/refusal append EARLY; normal appends LATE (3532, after generation). The prologue/epilogue split must respect this — the shared core must not own the user-append, or off/refusal break.

**Trap 3 — the test monkeypatch seam IS the regression gate.** `tests/rhm_completion_acceptance.py:238–252` patches `fclient.complete_with_tools` AND `suite._model_supports_tools` at attribute level, then asserts NON-BLANK reply + **exact confirmation substrings** (`"ran"`, `"moved"`). The refactor must keep (a) the `complete_with_tools` call site reachable through the same module-attribute, and (b) the confirmation-fold reachable so a bare tool-call still yields non-blank text. A new indirection that the patch misses → green tests, broken prod.

**Trap 4 — `_chat_context` is NOT side-effect-free.** `_chat_context` (1336) emits `warning` events on a down chat/embed endpoint (suite.py:1361, 1366). `_affordance_context` (2104) IS pure. So **re-invoking the context builder per-part multiplies the warning emits** (N warnings for one down endpoint in one turn). Build the system context ONCE in the prologue and pass it into each part (also ties to R1-FOLD F8 telemetry-flood).

---

## 4 · Extraction plan (shared core vs per-caller)

**Recommended: shared per-part core, turn-level wrappers.**

- `_chat_prologue(message, graph_id, focus) -> (cfg, mode, sys_p, ctx_block, early_exit | None)` — get_mode/off, capability gate, persona, model-of-Tim head; builds the system context ONCE (Trap 4); returns an early-exit token for off/refusal so those keep their exact return shapes + provenance (Traps 1/2).
- `_chat_part(sys_p, ctx_block, history, user_or_cue, mode, actx, tools, graph_id, is_final) -> ReplyUnit{text, outcomes, proposals}` — THE shared core: msgs build + `complete_with_tools` + tool_call loop + confirmation fold. **No store writes, no return assembly, no chat event** inside it.
- `chat()` = prologue → one `_chat_part` → epilogue (append, action_field, ONE chat event, thread bump, 7-key return). Byte-identical behaviour.
- `chat_parts()` = prologue → loop `_chat_part` (Part 1 deps=[]; later parts inject resolved `run://` role values per F3) → turn-level epilogue: ONE user append, N (or merged) assistant appends, ONE chat event, ndjson stream.

**Why not per-caller copy (F4):** copying forks the brain (two divergent governance/tool paths → E6 risk); looping `chat()` re-runs the capability gate and emits N chat events. The shared core is the only option that keeps ONE governed brain.

**Open design points — FLAG, do not resolve in the refactor:**
- (a) Does tool-dispatch happen in ONE part or per-part? Guide G1's `focus`/`recall` roles are *auxiliary cognition*, not the acting brain — suggests acting stays in one (final) part, but it's unstated. If per-part, the `action_field`/`proposal` merge (§2.2/2.3) is net-new.
- (b) History-append shape for N parts: one user + N working-grade assistant turns, or one merged assistant turn? Both feed the twin/grade path.

---

## 5 · "What still works" preservation list (EXACT)

**Callers of `chat()` (must survive unchanged):**
1. `runtime/bridge.py:669` — `POST /api/chat` → `SUITE.chat(message, gid, focus=...)`. FE `canvas/app/src/useAppController.ts:717` (`api.chat(m,{selected})`) reads `r.error`, `r.history` (Array-guarded `setChat`), `r.thread_id`, `r.reply`, `r.proposal`, `r.action`. All seven keys + the three shape-variants must persist.
2. `runtime/bridge.py:435` — `_voice_stream` (`/api/voice/stream`) BLOCKS on `SUITE.chat(transcript, gid)` then reads `.reply`. G6 inverts this to consume parts → **transitively gated on this refactor.** Until G6, `.reply` must stay a single string.
3. `runtime/bridge.py:614` — `/api/voice/turn` passes `think_fn=lambda txt: SUITE.chat(txt, gid)` to `voice/loop.py::loop_turn`. Contract (loop.py:158,173–186): `(transcript) -> {"reply", "action"?, "mode"?}`. Must keep returning that dict.
4. `mcp_face/server.py:142` — `return SUITE.chat(message, graph)`. MCP passthrough; same shape.

**Behaviours that must survive (invariants):**
- off-mode 4-key return + gold/twin provenance (Trap 1).
- capability-gate refusal 5-key return, NO model call, NO fallback (rule 4).
- E6 no-bypass: the ONE whitelist in `_dispatch_rhm_action` (RHM_VERBS) + the mode-discipline `offered` re-gate + `apply/delete/write_file` refusal — untouched.
- `decide-for-me` routing via `autonomous_dispatch(RHM_VERB_CLASS, …)`.
- `suggest`→proposal (no dispatch) consent path.
- non-blank reply when the model emits only a tool-call (confirmation fold).
- provenance grading (gold/working, operator/twin) on the normal path.
- thread threading (`_current_thread`, last_msg/title bump, thread-aware history).
- ONE `chat` event per turn at `ui://chrome/chat`.

**Test suites gating this (the `rhm_*` regression set + adjacents):**
- `tests/rhm_completion_acceptance.py:243,250` — **the live `chat()` path**, patches `complete_with_tools`+`_model_supports_tools`, asserts non-blank reply + exact confirmation substrings. **The hardest gate.**
- `tests/rhm_action_parse_acceptance.py:180,204,218,245,263,275` — drive `suite.chat(...)` across modes; affordance-set + whitelist + mode-discipline.
- `tests/rhm_action_acceptance.py` — `_json_obj_to_action` + dispatcher refusal mapping.
- `tests/rhm_acceptance.py` — `chat_history` ordering/limit/persistence.
- `tests/rhm_grounding_acceptance.py:61` — `_chat_context` ground-truth content.
- `tests/modes_acceptance.py:63`, `tests/propose_affordance_acceptance.py:88,124,152`, `tests/focus_ui_address_acceptance.py`, `tests/event_address_acceptance.py:123` — all call `suite.chat(...)`; mode/proposal/focus/event behaviours.

---

## 6 · The riskiest breakage

**The off/refusal short-circuits leaking into the shared core — and the gate cannot catch it.** If the extraction pulls the user-append or return assembly into one shared place "for cleanliness," off-mode and refusal lose their distinct return shapes and hardcoded gold/twin provenance (Traps 1+2). This is **silent**: no listed test asserts off-mode provenance, and `rhm_completion` patches the gate to TRUE so the refusal path is never exercised. The highest-confidence break is exactly the one the regression suite does not cover. *Mitigation:* keep both short-circuits as prologue early returns that never touch the shared core, and add an explicit off/refusal shape+provenance assertion to the gate before merge.

**Compounding risk (the dense region 3456–3526).** The tool-loop + confirmation-fold + `action_field` region is the densest single-shot-coupled code AND exactly what `rhm_completion`/`rhm_action_parse` assert on. Correctness hinges on `chat()` mapping byte-identically to "one final part." Mis-map it and `chat()` silently stops dispatching/folding — caught ONLY IF the monkeypatch seams (Trap 3) survive. If the seam breaks in the SAME edit, tests pass while the brain is forked. **Verify the seams independently** (gate still an instance method; `complete_with_tools` still patchable through the module ref) BEFORE trusting the key-assertions. Sequence as a serial-spine edit.

**Second-order:** multiplied `warning` emits from per-part `_chat_context` (Trap 4) — a telemetry-flood regression tying into R1-FOLD F8.
