# Cognition tools — the PARAM MAP (Tim's "everything settable, regardless of provider")

*Tim directive (2026-06-20): "You should be able to set the structured outputs, the prompts and context
resolutions, the output locations, the think, the tools — everything, regardless of the provider. That should
just be a value/param in your tools, the code should do it in the back." + "a lot may be built but unwired, a lot
that needs to be there but isn't may not be anywhere — that's how you know what you make."*

This is that map — each thing he named classified **BUILT+WIRED / BUILT-but-UNWIRED / ABSENT**, evidenced against
the real code (runtime/cognition.py `run_role`, fabric/transport.py, mcp_face/server.py). Default-to-wrong: every
claim is grounded in a read or a live test, not the docstring.

## THE SIX PARAMS

| # | What Tim named | Status | Evidence |
|---|---|---|---|
| 1 | **structured output (schema)** | BUILT+WIRED via the ROLE; per-call OVERRIDE **ABSENT** | role.output_schema → `json=True` → transport `_apply_response_format` → response_format json_object/json_schema (cognition.py:330-333, transport.py:63-88). Works on /v1 (vLLM-clean; cloud reasoning models need budget — see ★BUDGET). You set it by AUTHORING a role; `run_role` has NO per-call schema param. |
| 2 | **prompt** | BUILT via the ROLE; per-call OVERRIDE **ABSENT** | system msg = `role.prompt_template`, user = utterance (cognition.py:329-331). Set by authoring/create_role; no per-call prompt param. |
| 3 | **context resolution** | **BUILT+WIRED** ✓ | `inputs` / `input_addresses` resolved via resolve_address (cognition.py:322-328; mcp server.py:557-559). Settable per-call. |
| 4 | **output location** | BUILT (auto run://); settable param **ABSENT** | MCP persists to `run://<turn>/<role>` (server.py _fire_role_and_persist). Addressed + inspectable, but you can't choose the location. |
| 5 | **think** (reasoning on/off) | **ABSENT** (mechanism EXISTS, UNWIRED) | `run_role` has no think param; uses only `openai_transport` (/v1), which SILENTLY IGNORES think-control. ★ PROVEN: ollama NATIVE `/api/chat` with `"think":false` → 43 out-tokens vs `"think":true` → 1304 (kimi-k2.6:cloud) — a 30× collapse. The mechanism works; it's just not wired (the transport never calls native). |
| 6 | **tools** | **BUILT-but-UNWIRED** | `openai_tools_transport` + `client.complete_with_tools` exist (transport.py:144; "a tool_call with empty content is SUCCESS") — but `run_role` calls `openai_transport` (no tools). You CANNOT pass tools to run_role. |

## ★ THE BUDGET BUG (the proven concurrent-model failure)
Reasoning cloud models spend the whole `max_tokens` on the hidden reasoning trace before emitting structured
JSON → truncated (`finish_reason=length`) → EMPTY content. PROVEN (kimi-k2.6:cloud, /v1):
- response_format + max_tokens=64/256 → content `''`, finish=length (the failure Tim hit).
- response_format + max_tokens=600 → `'{"label":"statement"}'`, finish=stop, **462 completion tokens** for a
  one-word answer.
So structured output DOES work on any provider — but only with budget headroom the default doesn't give. The
existing `policy` rep-penalty ladder escalates on finish=length, BUT (a) it's rep-penalty not max_tokens, and
(b) the transport doesn't even forward repetition_penalty yet (cognition.py:270-277, flagged cross-lane). So
there is NO working finish=length→budget escalation today.

## ★ PROVIDER REALITY (why "regardless of provider" needs a translation layer — none exists)
| endpoint | structured output (json) | think-control |
|---|---|---|
| `/v1` (openai_transport — the ONLY path run_role uses) | WORKS (response_format; vLLM-clean, cloud needs budget) | **IGNORED** (silently) |
| ollama NATIVE `/api/chat` | INCONSISTENT (cloud kimi ignored `format`, returned prose) | **WORKS** (`think:false`, proven 1304→43) |
| local vLLM (chat-2b/4b, NOT resident) | clean response_format + advertises `no-think` | the intended STRUCTURED/EXTRACTION workhorse |

→ Neither single endpoint gives BOTH cheap+clean for a cloud reasoning model. The design intent (memory:
local=extraction/MAP workhorse, cloud=big-ctx agents) says: **structured extraction → LOCAL no-think models**
(clean + cheap on /v1); cloud reasoning models are for big-context agent work, not schema-extraction. So the
extraction mine wants a LOCAL model loaded (the LEAD's VRAM call now), AND the provider-translation layer below.

## THE BUILD (the "make it so" — Tim-directed; hot-path = coordinate with lead first)
A PROVIDER-TRANSLATION layer: one param → the right mechanism per provider, "the code does it in the back."
1. **`think` end-to-end as the TEMPLATE** (advisor): add `think` to run_role + the transport; for ollama models
   route think-control to NATIVE `/api/chat` (the proven mechanism); for vLLM use `chat_template_kwargs.
   enable_thinking`; default the structured/extraction path to think-off (cheap). Verify by the TOKEN DROP.
2. **wire `tools`** into run_role (openai_tools_transport already built — just unwired).
3. **per-call overrides** for schema / prompt / output-location (today role-only).
4. **budget-retry SAFETY NET**: on finish=length with empty/invalid structured output, escalate max_tokens
   (reuse the policy-ladder shape) — for when reasoning is genuinely wanted.
Build `think` first as the template; the rest follow its shape. Verify each against REAL behaviour
(think=token-drop; tools=an actual tool_call; structured=clean parse) — default-to-wrong, never "output appeared".

★ STATUS: routing fix (model→endpoint) DONE+verified (c1e00ba). This deeper param-layer is the next build, on
runtime/cognition.py + fabric/transport.py (the cognition lane) → coordinating with the lead (tool-atlas may be
on the same files; avoid the concurrent-commit race) BEFORE the hot-path edit. Not deferral — sequencing a
shared-file edit; the diagnosis + this map + the plan are done now.

## ★ THINK — BUILT + VERIFIED (f9305d7, 2026-06-21) for ollama (cloud + ollama-local)
The `think` param is wired run_role → cognition → the new `ollama_native_transport` (routes ollama-served models
to the native /api/chat that HONOURS think; /v1 ignores it). VERIFIED by-use (default-to-wrong, token-drop through
the real transport): **think=False → 2 out-tokens + clean content "command"; think=True → 400 tokens, finish=length,
EMPTY** (the bug reproduced). A 200× collapse + correctness restored → cheap cloud concurrent cognition now works.
Additive (think=None byte-identical; bake-resume safe). committed≠live: live on the next MCP/session reload.
★ BUDGET-RETRY NET — BUILT + VERIFIED (757942e, 2026-06-21). The structured-output safety net in client.complete:
on a failure that is ALSO finish_reason=length, doubles max_tokens (cap 4096) next attempt instead of burning
retries → cloud reasoning models that truncate the structured answer now RECOVER. Additive (non-truncating =
byte-identical; only the already-failing length path changes). Verified by-use (recovers 256→512→1024; byte-
identical otherwise; non-length failures don't escalate) + all 5 fabric suites green (no regression).

REMAINING (the table's other gaps, NOT yet built): vLLM-local enable_thinking via chat_template_kwargs (post-bake,
needs a free vLLM model to verify — currently an honest no-op on HF-path models); per-call schema/prompt/output-
location overrides + prompt/schema-as-RESOLVED-VARIABLES (gated on composition's resolver-contract — absent; the
mechanism is mine, the contract is composition's, do NOT build blind); tools wiring. The think TEMPLATE + the
budget-retry are the shape the rest follow.

## THE THINK-BUILD SPEC (locked 2026-06-21 — read the transport; additive; ★ THE OLLAMA HALF IS NOW BUILT, above)
*Transport read in full (fabric/transport.py): `openai_transport` builds /v1 requests via an allowlist
(`_SAMPLING_KEYS`) + `_apply_response_format` + `_fill_meta` (finish_reason/usage out-param). NO think handling.
The think mechanism is provider-split (PROVEN by-use):*
- **vLLM (local, /v1):** think-control = body `chat_template_kwargs:{"enable_thinking":<bool>}` (rides the existing
  /v1 path — additive, one branch in openai_transport). Works WITH response_format (vLLM does both). [unverified:
  no local model free — bake owns chat-4b; verify when a vLLM chat model is resident.]
- **ollama (cloud / ollama-local):** think-control = NATIVE `/api/chat` with top-level `"think":<bool>` — /v1
  SILENTLY IGNORES it. PROVEN: think:false 1304→43 tokens (kimi). Needs a new `ollama_native_transport`
  (base_url .../v1 → .../api/chat; response = message.content, eval_count for meta).
- ★ **HONEST PROVIDER-LIMITATION (default-to-wrong finding, do NOT paper over):** on the CLOUD native endpoint,
  `format` (structured) was INCONSISTENT (kimi returned prose, not JSON). So **think-off + structured-output
  TOGETHER is NOT cleanly achievable on a cloud reasoning model** — /v1 gives structured-not-think, native gives
  think-not-structured. **LOCAL vLLM models give BOTH** (response_format + enable_thinking on /v1) → confirms the
  design intent: structured EXTRACTION = local no-think models; cloud = big-ctx non-structured agents. The think
  param's clean wins: cheap cloud NON-structured generation (native think:false) + local vLLM structured+no-think.

### THE BUILD (additive, default think=None = byte-identical → recollection's bake-resume safe):
1. `fabric/transport.py`: add `ollama_native_transport(base_url)` (POST /api/chat, "think"+"format", return
   message.content, eval_count→meta); in `openai_transport` add `chat_template_kwargs.enable_thinking` when
   `opts["think"]` present (vLLM path).
2. `runtime/cognition.run_role`: add `think: bool|None=None` param; route — ollama model + think-control → native
   transport; else /v1 (+enable_thinking for vLLM). Default None = current path untouched.
3. `mcp_face/server.py run_role`: add `think` param, thread it.
4. **Budget-retry NET** (the correctness piece, verifiable-now on cloud): on finish_reason=length with empty/
   unparseable structured content, retry at escalated max_tokens (reuse the meta/finish_reason seam + the
   policy-ladder shape). PROVEN need: /v1 response_format max_tokens 256→empty(length), 600→clean JSON(462 tok).
   This is the SAFETY NET (advisor: necessary, not the headline) — for when reasoning is genuinely wanted.
VERIFY each by REAL behaviour (default-to-wrong): think = the token-DROP (1304→43 class); budget-retry = the
empty→clean transition; never "output appeared". (recollection GO'd the hot-path edit as non-interfering; lead
race-clear; keep run_items' default additive for bake-resume safety.)

## ★★ RESOLVED-SLOTS §5 — BUILT + VERIFIED (881fb9f, 2026-06-21) — the prompt half
To composition's LOCKED RESOLVER-CONTRACT.md §5: a role's prompt upgrades static-per-role → resolve(coordinate).
Additive `prompt_slot` field (roles.py) = a resolve_slot value; run_role gains `coordinate`; the system prompt
RESOLVES from prompt_slot via resolver.resolve_slot against the turn coordinate (grain·viewer·mode·subtype·
register). Threaded run_role→cognition→MCP. VERIFIED by-use through the REAL run_role path: ONE role → 3 prompts
across 3 coordinates (tim→architect/client→client/stranger→default); static role + no-coordinate byte-identical;
roles_acceptance 30/30 + rules_acceptance 64/64. output_schema stays literal-superset (§5 common case);
schema-select-between-classes + the {{}} template wrapper are the contract's FLAGGED-FOLLOWS (grain projection is
READ-SIDE, recollection's). committed≠live: MCP coordinate param live on the MCP reload.

## ★ RESOLVED-SLOTS — CONTRACT SETTLED + RECALL-GROUNDED (2026-06-21; build is read-side, post-bake)
**composition's contract answer (cc lead):** grain resolves on the READ side, NOT extraction. **EXTRACT-ONCE
(rich superset) + DETERMINE-MANY (project the grain on read).** Applying prompt/schema-resolution at EXTRACTION
would mean varying-grain passes = multiple bakes (fights extract-once). So grain = a DISCRETE axis →
**fork's EXISTING `resolve_slot` select-slot** (`{select:'resolution', cases:{coarse:[fields], fine:[fields]}}`)
— reuse the primitive, NO new mechanism. ✓ VERIFIED by-use (2026-06-21): the select-slot returns field-LISTS
cleanly (coarse→['about'], fine→['about','touches','entities','claims','relations']; unknown→default), and the
determine read-path projects the stored superset to the grain's fields. composition's claim about my primitive
is TRUE. fork's prompt-resolution rides the SAME read-side grain axis. SEQUENCING: build the grain-projection +
prompt-resolution READ-SIDE, AFTER the bake (it does NOT gate the bake).

**★ THE SCHEMA-vs-PROMPT ASYMMETRY (fork's co-shape against roles.py, 2026-06-21 — the real design crux):**
A role declares `prompt_template: str` + `output_schema: type[BaseModel]` (a CLASS — used for BOTH client-side
validate AND the json_schema guided-decode). So the two upgrade differently:
- **prompt_template** → a resolve_slot value: literal | select(by discrete axis) | TEMPLATE ({{name}} sub-slots,
  interpolated — the ONE maybe-new wrapper). VOTE: select for v1 (covers grain/viewer/mode/subtype); template a
  flagged-follow for continuous prompt-composition.
- **output_schema** → does NOT become a field-list select (a field-list isn't a Pydantic class). The clean
  reconciliation (preserves extract-once): **output_schema STAYS the rich SUPERSET class**; the **grain
  field-set projection happens on the RESULT, READ-SIDE** (the determine path projects fields from the validated
  superset output) — NOT on output_schema. output_schema-resolution is then just: literal-superset (common) |
  select-between-pre-declared-CLASSES (genuinely-different schema per coordinate) | dynamic-build (heavier,
  later). So the grain select-slot lives on the determine/read side (recollection's lane), output_schema mostly
  stays static-superset — extract-once intact.
NET: run_role's prompt_template/output_schema upgrade STATIC-per-role → resolve_slot(coordinate) at run-time
(axes = grain·viewer·mode·subtype·register). fork wires run_role/roles.py when composition locks the contract doc.

**RECALL-BEFORE-BUILD grounding (recollection ran the live extraction asset on the resolver design — Tim's
"use the company's own memory"; 29,406 records, semantic; recall serving the build):**
- ★ "Resolution logic needs improvement to enable types of resolution with **COUNTS and LOCATIONS**" [full/91037]
  — beyond value-derivation + select, the resolver should resolve a COUNT (how-many) and a LOCATION (where/which
  address). A future resolver capability to fold in (not built — flagged for the resolved-slots build).
- ★ "A variable-resolution system needs a **FIXED ORIGIN** to function coherently" [full/80624] — a design
  constraint: the coordinate needs an anchored origin (matches the cascade's root / A1 morphism-from-Root).
- "The **address is the universal primitive** — one scheme: persist · load · house-config · trigger" [85476];
  "**Variable resolution is the TRIGGER for phase execution**" [85476] (= resolve→work, my resolve(coordinate)
  shape); runtime form = "**blackboard architecture**" [85476]. The resolver IS the address-primitive's compute.
- ★ READ-PATH SEAM (flagged to recollection): `extraction://` ids are op='query'-able but NOT op='read'-able via
  the corpus tool version I have (only their `op='determine'` reads them) — the extraction-asset read path isn't
  wired to the generic corpus read. A real gap (recollection's lane).

## THE RESOLUTION-MECHANISM ANSWER (lead/Tim flag 2026-06-20 — "make prompt+schema resolve(coordinate), at grain")
**Q: can a role's prompt + output_schema RESOLVE against a coordinate today, or swap-only? → SWAP-ONLY (evidence).**
- `run_role` uses `role.prompt_template` + `role.output_schema` DIRECTLY (static per role; cognition.py:330 +
  the json/schema path). Its params are base_url/model/timeout/max_tokens/temperature/store/ensure/ensure_evict/
  policy/meta — **NO prompt/schema per-call param.** Varying them = author/SWAP a role (create_role/propose_role
  builds one programmatically — still swap, NOT coordinate-resolution). Only `inputs` resolve per-turn.
- The `resolve(invariant, coordinate)` primitive itself does NOT exist yet — it is the KEYSTONE being built
  (RESOLVER-BUILD.md:7,37). What EXISTS to REUSE (don't fork): `runtime/context_variables.py`
  `ContextVariable.resolve(ctx)→value` (the per-turn variable-resolution; `inputs`/input_addresses already
  resolve this way) + projection `BindingRegistry`/`_resolve_sectors`.

**SMALLEST PATH (rides the spine, not parallel):** make `prompt` + `output_schema` **RESOLVED SLOTS** — the exact
`_resolve_axis(slot, source)` pattern pre-scouted for the instrument (RESOLVER-BUILD.md:92). prompt+schema JOIN
`input_addresses` as resolved-from-coordinate variables, reusing `context_variables.resolve`. The **GRAIN axis**
(Tim's "variable granularity") = the schema is a RICH SUPERSET (recollection's stored asset) + the resolver
PROJECTS the subset for the requested grain (coarse `{about}` ↔ fine `{about,touches,entities,claims,relations}`)
= the MRL/resolution axis already named in RESOLVER-BUILD.md:17. `resolve(grain)→schema-subset`; one stored asset
serves ANY future determine at ANY grain (so the 35,904-chunk bake is done ONCE on the superset).

**CONVERGENCE (schema-FIRST — do NOT bake the extract until this converges):**
- recollection → the RICH grain-scalable schema (the superset asset).
- composition → make `prompt` / `output_schema` resolvable VARIABLE TYPES in the resolver contract (the spine).
- fork → the resolution MECHANISM: wire run_role to resolve prompt+schema from the coordinate (reuse
  context_variables.resolve), + the grain-projection of the schema. This is `resolve(invariant, coordinate)` at
  the COGNITION scale — same shape as the instrument's `_resolve_axis`, one altitude over. Render-independent.
