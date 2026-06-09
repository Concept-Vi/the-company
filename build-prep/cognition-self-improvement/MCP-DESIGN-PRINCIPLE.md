# MCP Design Principle — the company MCP is the top priority (the standing law for the tool face)

> **The objective (Tim, 2026-06-09 — top priority):** every capability built in `~/company` reachable THROUGH `mcp__company__*` so **"direct" (shell / python harness / engine-method calls) is never necessary**, AND the server **intuitive enough that an agent uses it unaided**. This doc is the standing law every agent/the loop follows when touching the face. Grounded in: Anthropic, *Writing effective tools for AI agents* (anthropic.com/engineering/writing-tools-for-agents, 2025-09-11) + the company's own engine axes + the 2026-06-09 surface audit (61 tools).

## THE TWO OBJECTIVES (both, or it's not done)
1. **COVERAGE** — full capability reach through the MCP. Reaching for "direct" = a coverage GAP to expose, not a workaround to keep. The dogfooding rule: drive EVERYTHING through the MCP; each time you'd drop to direct, log it + expose it; until direct is never needed.
2. **INTUITIVENESS** — agent-usable unaided. The bar is **evaluation-driven** (below), not the author's familiarity.

## THE PUBLISHED PRINCIPLES (Anthropic — distilled, they govern here)
1. **Choose the right tools — fewer, workflow-shaped.** More tools ≠ better; overlapping/flat tools DISTRACT the agent + burn context. Build a few thoughtful tools targeting **high-impact workflows**, and **consolidate multiple ops under one tool** where the agent's task wants it: `search_contacts` not `list_contacts`; `schedule_event` not `list_users`+`list_events`+`create_event`; `get_customer_context` not three `get_*`. Tools should mirror how a human would subdivide the task.
2. **Namespacing.** Group related tools by resource (prefix/suffix). The company is already client-namespaced (`mcp__company__*`); within that, resource-prefix the consolidated tools (`corpus_*`, `run_*`).
3. **Return meaningful context, not low-level IDs.** High-signal fields (path, summary, name) over `cas://`/hashes/raw vectors. A **`response_format`/`detail` enum (`concise|detailed`)** controls verbosity — concise by default. (This directly fixes `list_corpus` returning 65k chars.)
4. **Token-efficiency.** Pagination · range · filter · truncation with sane defaults; cap big responses.
5. **Helpful, steering errors.** Fail-loud WITH guidance (the G18 fix — "this is a retrieval key; content goes in `output`" — generalized), never an opaque traceback. The error teaches the agent the right call.
6. **Prompt-engineered descriptions.** Describe each tool like to a new hire; unambiguous param names (`role_id` not `role`); strict schemas + clear enums.

## THE COMPANY-SPECIFIC LAW: the face mirrors the engine's axes
The ENGINE is already well-parameterized — `run_role(op=generate|embed)`, `run_reduce(mode=role|rule|cluster)`, the file-discovered registries. That IS the composable-primitive philosophy. The READ/discovery + authoring FACE drifted into flat-per-method sprawl. **The law: a tool per RESOURCE (noun) + a small verb/selector param (`op`/`by`/`kind`), parameterised along the engine's own axes (`resource × op × space × by`).** A new need = a new `op` value, NOT a new tool. The flat sprawl is a **built-twice / drift from the company's OWN laws** (registry-is-truth, reuse-don't-parallel) applied to the tool surface — the very thing ② drift-radar catches, on the MCP.

### The trade-off (honour it — don't over-collapse)
Parameterise by resource + a SMALL verb-enum where params are **mostly shared** across verbs. DON'T collapse unrelated ops into a **god-tool** (a 15-field schema where most fields are conditionally-ignored — the model gets *more* confused, validation can't guard "valid only when op=X"). Genuinely-distinct nouns/intents stay separate tools. Keep CQRS: reads vs the consequential writes (`resolve`/`apply`/`dispatch` — the floor) stay split. KEEP the compute primitives (`run_role`/`run_items`/`run_reduce`/`run_cascade`) — they're already right.

## THE AUDIT (2026-06-09 — 61 exposed tools → the consolidation plan, ~25–30)
| Flat cluster (today) | → consolidated | Δ |
|---|---|---|
| `list_corpus` · `find_corpus` · `read_corpus_record` · (query_corpus unexposed) | **`corpus(op=list\|find\|read\|query, …, detail=concise\|detailed)`** | 4→1 |
| `create_role\|skill\|context\|projection\|mark_type\|relation_type\|ai_tic\|generation_policy` (8) | **`create(kind=, spec=)`** (kinds ARE the registry — registry-is-truth) | 8→1 |
| `mark` (write) · `marks_for` · `marks_by_type` · `findings_for` | `mark` (write, CQRS-kept) + **`marks(by=target\|type)`** | 4→2 |
| `list_runs` · `find_runs` · `get_results` · `get_events` · `get_state` | **`runs(op=list\|find)`** + a `read(what=results\|events\|state)` (care: distinct nouns) | 5→~2 |
| `create_node` · `delete_node` · `apply_node` · `propose_node` | **`node(op=create\|delete\|apply\|propose)`** | 4→1 |
| `attach_rule` · `dry_run_rule` · `validate_rule` | **`rule(op=attach\|dry_run\|validate)`** | 3→1 |
| `list_types` · `list_by_type` · `list_skills_contexts` · `field_types` · `reduce_rule_names` · `models_for_role` | fold into **`cognition_info`/`registry(what=)`** (the discovery face) | 6→~2 |
| `propose_role` · `edit_role` · `delete_role` | `role(op=edit\|delete\|propose)` (+ create via `create(kind=role)`) | 3→1 |
KEEP as-is (already right / distinct): `run_role` · `run_items` · `run_reduce` · `run_cascade` · `save_cascade` · `list_cascades` · `run_draft(_items)` (compute core) · `capture` · `find_relations` · `chat` · `now` · `set_config` · `inspect_address` · `object_info` · `preview_turn` · `inbox` · `list_surfaced` · `self_change_log` · `capabilities` · `cognition_info` · `cognition_inputs` · `run_graph`/`list_graphs`. *(run_draft could fold into `run_role(draft=…)` — a candidate.)*

## THE INTUITIVENESS BAR — evaluation-driven (Anthropic's method = the verification)
"Intuitive enough for an agent" is **tested, not asserted**: spawn a FRESH agent (no context), give it real cognition tasks ("ask the codebase about X", "register a new role", "find drift", "mine the transcripts"), and measure — tool errors · redundant calls · wrong-tool selection · confusion in its reasoning. Where it stumbles = the tool to fix. Then refactor + re-eval. This is where agents/workflows fit (Tim 2026-06-09: "use any of your agents or workflows"): the eval is a fan of fresh-agent tasks; the analysis is an agent reading the transcripts (the Anthropic loop: Claude optimizing its own tools). The standing acceptance: **a fresh agent completes the core cognition workflows through the MCP unaided.**

## EXECUTION (Tim chose C, 2026-06-09)
1. **This principle** (A) — the law. ✎ (committing now).
2. **B — corpus consolidation** (instance 1): `corpus(op=list|find|read|query, detail=)` — the query becomes `op=query` (NOT a 5th flat tool); + the `detail` enum fixes the 65k. Proves the pattern + closes G20 (query) the right way. (Serial — one hot file `mcp_face/server.py`.)
3. **Sweep** — `create(kind=)` (biggest win, 8→1), then `marks`, `runs`/`read`, `node`, `rule`, the discovery cluster. Each a serial beat (mcp_face is one file → NOT parallel lanes; an agent per cluster per beat, or direct — keep agent turns bounded, G8).
4. **Coverage pass** — expose the still-direct-only capabilities (the compositions ②/③/⑥/⑦/⑩ as runnable via the MCP; `ingest_paths` for path-keyed ingest [G21]; etc.) until direct is unnecessary.
5. **Eval** — the fresh-agent intuitiveness test → refactor → re-eval.

## THE WHOLE-APPLICATION AWARENESS (Tim 2026-06-10 — instilled so autonomous calls are good)
The MCP is not standalone — it's the agent face of the COMPANY, and every decision carries the whole shape:
- **The laws apply to EVERY tool (no exceptions):** registry-is-truth — *nothing hardcoded; every enum/list/capability loaded from its source-of-truth registry* (op/kind enums DERIVE from the live registries) · build-against-contracts · schema-additive · fail-loud-no-silent-fallback · reflects-never-owns · reuse-don't-parallel · the FLOOR (operator-only resolve/approve/dispatch/claude-p; declarative DIRECT, code/node-type GATED) · deterministic-gates/no-confidence · update-the-self-description (drift) · prove-by-use · NO Gemini.
- **Coverage = link ALL built capabilities to tools, from their source of truth:** the cognition quartet over the file-discovered registries (roles·skills·contexts·projections·lifters·mark_types·generation_policies·relation_types·ai_tics·forms·mode_detection_rules·nodes) · corpus/embedder/spaces · marks/findings · run-index · governance/inbox + the wire · activation · graph/nodes · the compositions ①–⑫.
- **THREE CONSUMERS (the design constraint):** (1) EXTERNAL agents (cold, zero company-knowledge) → bar = maximal self-description + intuitiveness AND the **FLOOR is a hard SECURITY boundary** (a stranger's agent must be unable to escalate — declarative-direct only, never resolve/dispatch/claude-p). (2) INTERNAL crew agents → fluent composition. (3) the RHM/right-hand-man → the same composability SURFACES as Tim's UI (coherence + self-teaching responses = the UI's quality by nature). **Design for the coldest consumer (external) → the other two are served.** Hold the floor as a boundary because external agents touch this.
- **Two faces, one composability:** MCP (agent) ⟂ Surface/RHM (human) — the FRAME (FRAME-the-two-halves.md). Getting the MCP right makes the UI intuitive by nature.

## THE MANDATE (widened — Tim 2026-06-10)
**The whole MCP** — all capabilities, all use — not only the named compositions. And **not only gap-closing**: opportunities · additions · upgrades · anything that makes the collective better is in scope. **Tim is not a developer and cannot give terminology or specific instructions** — so this is NOT spec-driven from him; cognition OWNS the architect judgment, drives it from the system's evidence + design reasoning, and surfaces OUTCOMES for Tim to react to (never asks him *what* to build). Standing frame at full scope: not-a-developer → the AI supplies the domain depth; expand-don't-echo; make-the-calls-myself; render outcomes for his reaction.

**TWO ENGINES** (both feed the backlog; cognition drives):
1. **FLOOR — eval-driven (find friction):** fresh agents drive real compositional flows MCP-only; their friction = the gap list (mcp-compose-eval.workflow.js).
2. **CEILING — opportunity-generation (make it excellent):** cognition proactively analyses the WHOLE surface + the engine's latent capabilities + REFERENCE MCPs (substrate-mcp's `suggest_tool`/`get_type_graph`/`get_neighborhood`/`traverse_links` — a maturer compositional/navigational face to learn from) + the compositions' needs → upgrades, not just fixes.

**THE UPGRADE DIMENSIONS (where "better" lives, beyond consolidation):**
- **Composability/chaining** — outputs→inputs (`run://`) frictionless; consistent address-in/address-out; a result carries what feeds the next step.
- **Discovery/self-description** — ONE intuitive "what can I compose + how do they connect" map (`cognition_info` as the composition vocabulary, enriched with chain-shapes + examples).
- **Self-teaching responses** — a result suggests the next move (cf. substrate `suggest_tool`); errors that teach (G18 generalised).
- **Response ergonomics everywhere** — `detail=concise|detailed` across all reads; high-signal-not-IDs; pagination/limits.
- **Coverage** — every engine capability + composition (②/③/⑥/⑦/⑩) reachable as an MCP tool (direct unnecessary).
- **Whole-surface coherence** — consistent names/params/op-enums/shapes so the MCP feels like ONE designed thing.

## STANDING RULES (every face change)
Reuse-don't-parallel (extend the consolidated tool, never add a flat sibling) · registry-is-truth (the `kind`/`op` enums DERIVE from the live registries, not hardcoded lists) · CQRS (reads vs the floor's writes) · helpful fail-loud errors · `detail=concise` default · meaningful context (no raw hashes/vectors in responses) · update the tool description like onboarding a new hire · **never ADD a flat tool — add an `op`** · verify by fresh-agent use. NO Gemini.
