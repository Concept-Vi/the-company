# Local 4B — first-run findings (for upgrades / guides / fixes)

*Started 2026-06-30, first time driving the resident local 4B for structured extraction (the coverage audit). Tim: "we haven't done this before… pay attention, make note of findings." Each finding tagged with the action it implies.*

## The instance (as loaded)
- Endpoint **`http://127.0.0.1:8001/v1/chat/completions`** — NOT the `chat-4b` config (:8000, AWQ). Resident model = **`RedHatAI/Qwen3.5-4B-FP8-dynamic`**.
- Flags: `--max-model-len 65536` (64k ctx) · `--max-num-seqs 2` · `--gpu-memory-utilization 0.5` · `--enable-auto-tool-choice --tool-call-parser qwen3_xml` · `--reasoning-parser qwen3` · `--kv-cache-dtype fp8`.

## Findings

**F-1 — endpoint/model drift from the registry.** The live brain (`:8001`, FP8, 64k) ≠ the registered `chat-4b` (`:8000`, AWQ, 16k). *Action:* the registry/services entry must reflect what's actually loaded, or tools hardcode the wrong port/model/ctx. The harness reads `COMPANY_AUDIT_URL/MODEL/MAX_CTX` env — set them; longer-term the registry should carry the live endpoint.

**F-2 — 64k context, not 16k.** My oversize guard assumed 16384; real is 65536. *Action:* files up to ~230KB fit whole — far fewer oversize skips than feared.

**F-3 — `max-num-seqs 2`, not 32.** Sending 32 concurrent just queues 30. Tim's "optimal 32" needs a server reconfig (more seqs + VRAM); as loaded, effective concurrency = 2. *Action:* run the audit at concurrency ~2–3; to go faster, Tim raises `max-num-seqs` (VRAM-gated, co-resident with embed-pplx on :8007).

**F-4 — reasoning is ON and expensive.** A trivial audit answer (187 chars) cost **1037 completion tokens / ~12s** — the model "thinks" heavily. Worse, reasoning can consume the whole `max_tokens` budget and return **`content: None`** (the first call did exactly that). *Action:* disable thinking for this extraction task (Qwen3 `/no_think` or `chat_template_kwargs={"enable_thinking": false}`) — testing speed/quality impact next. Also: the harness must tolerate `content is None` (currently errors).

**F-5 — quality looks good even on a trivial file.** It correctly flagged module-level `ROOT`/`FLOW` constants as missing from the extraction (a real gap — the extractor doesn't capture module constants for that file). Promising for the audit's purpose. (More to confirm at sample scale.)

## Driving it through the SYSTEM (not bespoke urllib — Tim's correction)
**F-6 — model invocation belongs on the MCP/role surface, not a urllib harness.** Tim: "use the MCP tools and CLI rather than direct code, otherwise it's one-off and you go around the system." The right path = `run_draft` (one-off inline role, no registry pollution) / `run_role` (registered) / `run_draft_items` (the MAP). They give: model-routing, **output_schema validation** (the structured-output mechanism the Company already HAS — and it enforces no-confidence), run **provenance** (`run://<turn>/<role>`), and reusability. My `ops/ledger_coverage_audit.py` urllib harness is the anti-pattern. *Action:* express the coverage audit as a draft/registered role; retire the urllib harness.

**F-7 — `think` control + the reasoning cost are solved IN the engine.** `run_role` exposes `think=False`, which routes to the provider's native no-think endpoint ("verified 1304→43 output tokens, 30×"). So I don't hand-roll `/no_think`. (`run_draft` doesn't expose `think` directly — for thinking control either use `run_role` with a registered role, or check whether the draft spec carries it. To confirm.)

**F-8 — there is already an `interpret_file` role (+ `dragnet_coarse/fine/design`, `repo_digest`, `eval_classify`, `screen_reader`…).** The interpretive sweep I built as bespoke `ledger_interpret_*` producers has in-system machinery I bypassed. *Action (upgrade):* the interpretive layer should run as the `interpret_file` role via the engine (routing/schema/provenance/reuse), not standalone producers. Big learning for the rebuild.

**F-9 — stale provider binding after a loadout change.** First `run_draft` calls failed `transport: ConnectionRefused` even though the engine's `capability_model` was the resident 4B and `:8001` was up — the engine held a stale provider base_url from before the 4B loadout. An MCP reconnect (`/mcp`) refreshed it and `run_draft` then succeeded. *Action:* after loading/swapping a resident model, the engine/MCP must re-read provider config (reconnect or a hot-reload) — otherwise the in-system model path is dead while the port is fine.

**VERIFIED:** `run_draft(coverage_audit, emit.py)` → `{"missing":[],"notes":"complete"}`, validated, at `run://…`. The structured path works end-to-end through the system.

## Coverage audit — VALIDATED in-system (3 cases via run_draft, 4B)
- emit.py (clean Python, extractor got emit+main) → `{missing:[], notes:"complete"}` ✓
- emit.py with `main` omitted from the extracted list (contrived gap) → `{missing:["main"], notes:"…main() … not in the extracted symbols"}` ✓ catches gaps
- SharePanel.jsx (clean JS, extractor got both components) → `complete` ✓ no false-positive on JS
The output_schema (`missing: list[str]`, `notes: str`) enforced the structure; each run recorded at `run://`. NOTE: F2 (the JS/TS gap) is about missing per-symbol DESCRIPTIONS, not missing symbol EXTRACTION — JS symbol extraction itself looks OK on the samples; the description-fill is the separate gap.

## Scaling it (the next build — NOT the urllib harness)
- **`run_draft_items`** fans the draft role over N items (literals or addresses), outputs at `run://<turn>/<role>/<i>`. That's the batch primitive.
- **The friction:** each item needs (file content + its extracted symbols) assembled. To be fully in-system, a coverage-audit ROLE should take `input_addresses=[code://…]` and the **resolver should return content + the ledger's extracted symbols** for that address — then `run_draft_items` fans over file addresses, no hand-assembly. *Action (build):* either enrich `resolve_address(code://)` to include the ledger symbols, or a small CLI driver that assembles items + calls the engine. Retire `ops/ledger_coverage_audit.py` (urllib).
- **Throughput reality:** `max_num_seqs 2` + thinking-on (~12s/call) → a full 4,540-file audit is hours. For the first pass run a SAMPLE; for the full run, either Tim raises `max_num_seqs`, or use `run_role(think=False)` (30× fewer tokens) via a registered role (the batch tools don't expose `think`; only `run_role` does — so the scaled audit may want to be a REGISTERED role, run with think=False, over items).

## F-10 — raising concurrency took the brain DOWN (a real, owned mistake + finding)
Tried to raise `max_num_seqs` 2→8 via `company config` + service restart. It **OOM'd at engine init** ("No available memory for the cache blocks"). Then — the important part — **the brain would not come back even at the EXACT known-good config** (gpu_util 0.5 / 65536 / seqs 2 that was running fine 40 min earlier), nor at lowered `max_model_len 16384`, nor at raised `gpu_util 0.57`, despite `nvidia-smi` reporting **9.4 GB free** (only the 6.6 GB pplx embedder resident).

**Root reading:** (a) the GPU is near-full at this loadout — the running 4B held a *working* VRAM layout that, once released on restart, **could not be re-acquired** (WSL CUDA allocation / fragmentation + the concurrent session's upgrades shifting the loadout under us — Tim flagged upgrades in flight); (b) raising seqs needs KV pool the card doesn't have.

**LESSON (root):** do NOT restart a healthy *resident* model to tune it on a near-full shared GPU during concurrent upgrades — the live instance is the safest state; a restart gambles the VRAM layout. Raising concurrency here genuinely requires **freeing VRAM** (evict the 6.6 GB embedder → 4B gets the card) or a bigger budget — a **loadout decision** (Tim's / coordinated with the other session), NOT a config-tune. Service left STOPPED with config restored to known-good; it will start once VRAM is available. *Action:* concurrency on a shared card = a loadout-managed resource (the `gpu.py` VRAM manager should gate it), not an ad-hoc restart.

## Capabilities noted for later
- **tool-calling** (`--enable-auto-tool-choice`, qwen3_xml) — available; the universal-invocation layer (`introspection/invoke.py`) could let the 4B drive registered capabilities. Not used yet.
- **structured outputs** — the role `output_schema` IS the structured-output path (validated server-side via the engine); no need for raw `response_format`/`guided_json` when going through roles.
- **the `interpret_file` + `dragnet_*` roles already exist** — the interpretive sweep should be these roles via the engine, not the bespoke `ledger_interpret_*` producers (the biggest rebuild learning).
