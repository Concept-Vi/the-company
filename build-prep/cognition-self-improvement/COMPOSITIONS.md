# Cognition Self-Improvement — The Compositions

> **What this is.** The next phase of the cognition-engine build: the engine turning on itself + on Claude Code's own work — *compositional free AI on tap, supercharging a strategic+tactical mind.* Twelve compositions, each specified at **chain grain** (the GROUP-V bar): purpose · how-it-works · the models · the exact tool-calls · the codebase addresses. Each is designed to become a **runnable stored graph** in the MCP/system (`save_cascade` → `run_cascade` with variable substitution for template inputs), so they are authored once and re-run on new inputs.
>
> **The asymmetry these exploit.** *I* (Opus / Claude Code) am the scarce resource — deep judgment, novel reasoning, strategic sight — but I can't read 19k files, run continuously, hold the whole project in context, burn premium tokens on grunt work, or remember across the context boundary. The cognition engine is the exact inverse: **free · concurrent · local · broad · continuous · addressed · persistent.** Every composition is one trade across that line: push the broad/shallow/repetitive/continuous DOWN to the swarm; reserve the deep/novel/judgment UP for me. A token-and-latency-and-memory multiplier on a strategic mind — an **exocortex**.
>
> **The two invariant laws (what makes turning this on SAFE):**
> 1. **The floor is invariant** — every composition *surfaces / marks / drafts / proposes*; none auto-mutates the repo or self-approves. Declarative authoring (roles/skills/contexts/projections/mark-types) is DIRECT; executable-code/build-dispatch (`claude -p`) stays GATED + operator-only. GROUNDED: `tests/cognition_governance_acceptance.py` — **42/42 checks passing** (the floor source-invariant scans `COG_SOURCES = [cognition.py · rules.py · roles.py · mcp_face/server.py · skills.py · projections.py · corpus.py · lifters/mark_types/generation_policies/relation_types/ai_tics/forms.py · mode_detection_rules.py · activation_driver.py] + roles/*` — every cognition-reachable surface; an AST scan asserts none emit resolve/approve/dispatch or launch `claude -p`).
> 2. **No-fiction / grounding-is-everything** — every MAP role gets the real artifact + the real law/feature-inventory as per-unit context; a CONFIRM jury cross-checks against source; ungrounded claims are FLAGGED, never dropped (variance-not-error → stronger-model-confirm).
>
> **How a composition becomes a stored graph (GROUNDED).** A composition below = a sequence of engine calls over deterministically-extracted units. Saving it = **`save_cascade(decl)`** where `decl = {name: str, steps: [{op, role, model?, kind?, reduce_mode?, reduce_rule?, ...}], output_schema?: dict}` — validated through the ONE door `coherence_actions.build_action(decl, *, models)` (`runtime/coherence_actions.py:23`; fail-loud on an invalid decl or an unknown model — registry-is-truth) and persisted in the `ActionRegistry` (`runtime/coherence_actions.py:49`, survives reload) via `Suite.save_cascade` (`runtime/suite.py:861`). Re-running = **`run_cascade(name, inputs=...)`** → `Suite.run_cascade` (`runtime/suite.py:888`) → the GROUP-N runner rides the existing primitives (run_role/run_items/run_reduce), threading each step's output→next step's input via the run:// resolver, persisting + op.run-indexing each step. **The seam (output→input):** step 0 reads `run_cascade(inputs)`; step N reads step N-1's output address. **Template substitution:** the single `inputs` argument is the first step's value (a `run://`/`cas://` address is resolved, a literal is used as-is) — so the per-task variable (the `${task}`/`${seed}`/`${question}` below) enters as `run_cascade(name, inputs="<the task>")`. *(Per-step richer templating — multiple named `${vars}` interpolated into a step's prompt — is a flagged extension: today the decl carries one threaded input + fixed per-step roles; multi-var substitution into prompt_template is the next cascade-runner rung, noted needs-build.)*

---

## DEPENDENCY SPINE (why these are ONE circuit, not twelve features)

```
①  repo exocortex (ingest→embed→retrieve)        ← THE FLOOR. ②③④⑨⑫ all read its corpus/spaces.
②③ drift-radar + transcript-miner                 ← read ①, write MARKS/drafts (surface-not-fix)
④⑥⑩⑦ scout / jury / option-panel / spec-compiler  ← the SERVE-THE-COLLABORATION layer (swarm → my judgment → Tim)
⑤  background self-audit                            ← ①+② lenses on the CALLER cadence (Tim's enable)
⑪  grunt-offload reflex                             ← the DAILY HABIT under all of them
⑧  self-extending toolmaking                        ← what makes it ACCRETE (roles grow from the wants)
⑫  engine-improves-engine                           ← what makes it CLOSE (the loop's next phase, self-drafted)
```

**The circuit:** `ingest(①) → retrieve(④⑨) → offload-the-broad(⑪) → reserve-the-deep(me) → verify-from-all-angles(⑥) → audit-continuously(⑤) → grow-the-toolset(⑧) → re-ingest(①)`. ⑦+⑩ feed Tim. ⑫ points the circuit back at itself.

**The GPU dependency, honest (GROUNDED):** ①'s embed step + ⑤'s cadence + ⑨'s embeds need the **bge-m3 embedder live** — service `embed-bge`, model `BAAI/bge-m3`, `:8001`, 1024-dim dense (`fabric/config.py:26-27`); a role triggers its load with `run_role(role, op="embed", ensure=True)` (the gated #50 actuator `capabilities.ensure_resident`; `ensure_evict=True` authorizes largest-first eviction) — so it's a GPU window, the SAME window the standing needs-tim wants (live 32-knee measure + real-vector embed). One window lights the keystone + closes two needs-tim. **The non-embed compositions (⑥ jury · ⑦ spec-compiler · ⑩ panels · ⑪ offload · ⑫ scout-plan) need NO GPU window** — they run on the resident swarm brain today: service `chat-4b`, model `cyankiwi/Qwen3.5-4B-AWQ-4bit`, `:8000`, `max_model_len 65536` (`ops/services.json:44-59`; `RESIDENT_BASE_URL` is run_role's default).

---

## THE SHARED PRIMITIVES (every composition is built from these — wire, don't rebuild)

| Primitive | What it does | MCP tool (sig) | Engine fn / address |
|---|---|---|---|
| MAP (1 role × N units) | the axis-inversion — fan a role over a unit-list, concurrent on the swarm | `run_items(role, items[], max_tokens=256, temperature=0)` → `{role,turn_id,n_units,addresses,resolved,finish_order,skipped,wall_s}` | `runtime/cognition.py:1085 run_items()` |
| REDUCE (cross-unit join) | role\|rule\|cluster — synthesize / deterministic-verdict / embed-dedup | `run_reduce(addresses[], mode, role="", reduce_rule="", cluster_threshold=0.85, max_tokens=512)` | `runtime/cognition.py:1736 run_reduce()` |
| single role-run | one role, input from any address, op=generate\|embed | `run_role(role, utterance="", op="generate", model="", inputs={}, policy="", ensure=False, ensure_evict=False)` | `runtime/cognition.py:203 run_role()` (the `ctx["utterance"]`→`input_addresses` seam) |
| chunk-and-compose | over-context unit → split→map→compose | (internal to run_items / called directly) | `runtime/cognition.py:1444 run_chunked()` |
| embed-on-write | corpus record → space-keyed vector | (via `capture`) | `runtime/cognition.py:376 embed_corpus_to_spaces()` |
| corpus capture | write+embed a record (lineage-gated), both faces one seam | `capture(role, units[], project, session, round="1", projection="", record_kind="capture", max_tokens=512)` | `runtime/suite.py:9633 Suite.capture_corpus()` |
| retrieve / relate | k-NN over a space; near∩¬far cross-space inversion | `find_relations(item, near_space, far_space, k=10, min_score=0.5)` → `{relations[],near[],far[]}` | `Suite.find_relations` → `store/vector_index.py query_index` (space-filter) |
| corpus read-back | list/find/read corpus records | `list_corpus` · `find_corpus` · `read_corpus_record(address)` | `runtime/suite.py:9720/9728/9713` |
| run discovery | list/find past runs by op/role (the run-index) | `list_runs(op,run_op,limit)` · `find_runs(role,op,run_op,limit)` | `runtime/suite.py:721/762` |
| mark | claim/span target + mark_type, retrievable | `mark(target, mark_type, value=None, confidence=None, ...)` | `store/fs_store.py:677 append_mark()` · `:705 marks_for()` |
| address resolve | run:// cas:// skill:// context:// → content | `inspect_address(address, turn_id="")` | `runtime/cognition.py:832 resolve_address()` |
| declarative authoring (DIRECT) | create a role/skill/context/projection/mark-type live, no approval | `create_role(spec)` · `create_skill(spec)` · `create_projection(spec)` · `create_mark_type(spec)` | `runtime/suite.py:8932 create_role()` · `:9004 create_skill()` · `:9127 create_mark_type()` (render→correctness-gate→commit→rediscover) |
| saved cascade | save / list / run a stored chain | `save_cascade(decl)` · `list_cascades()` · `run_cascade(name, inputs=None, max_tokens=256)` | `runtime/suite.py:861/888` · validator `runtime/coherence_actions.py:23 build_action` + `:49 ActionRegistry` |
| activation tick | fire the H/I drivers + detector (dormant by default) | `POST /api/activation/tick` | `runtime/activation_driver.py:162 ActivationCaller.activation_tick()` · `:84 activation_loop_enabled()` (env `COMPANY_ACTIVATION_LOOP`, default off) |
| field types (richer) | the output_schema grammar — nested/enum/optional/list[dict] | `field_types()` | `runtime/suite.py:9574 field_types()` + the `runtime/authoring.py` recursive renderer (kind: scalar/enum/object/list[object]) |
| inputs select | the advertised input space (skills/contexts/schemes/op/thinking/tools) | `cognition_inputs()` | `runtime/suite.py:9455 available_inputs()` |
| model catalog | which models provide chat/embed/tools/thinking (role↔model query) | `models_for_role(requires="")` | `ops/cli/capabilities.py MODEL_CAPABILITIES` (loaded from `ops/model_capabilities.json`) |

**The role spec shape (`create_role(spec)` — the full schema, `ROLE_FIELDS` `runtime/roles.py:71`):** `id · label · description · prompt_template · output_schema · input_addresses · op · trigger · model_binding · mode_scope · rules · render_hint · draws · verdict_rule · knobs · thinking · output · tools · context · default_model · default_base_url · recommended_model · ...` — every field but `id` optional; a role's facet follows which fields are set (fires ⟺ `prompt_template`; in-a-cast ⟺ `mode_scope`; jury ⟺ `draws`). `output_schema` is real Pydantic with the richer grammar (nested/enum/optional/list[dict]/defaults). So every NEW role below is one `create_role(spec)` call, DIRECT (declarative authoring, no approval) — git-revertible, correctness-gated.

**Model assignment, across all twelve (the loadout discipline — GROUNDED):**
- **MAP rounds** (broad, shallow, N-fold) → the **resident 4B swarm** (`chat-4b` / `cyankiwi/Qwen3.5-4B-AWQ-4bit` @ :8000; the swarm slot-budget is `SlotBudget.from_registry` reading `max_num_seqs` — registry-driven, the C-lane work) — cheap, concurrent, this is the whole point.
- **EMBED rounds** → **bge-m3** (`BAAI/bge-m3` @ :8001, 1024-dim) via `run_role(op="embed", ensure=True)`.
- **CONFIRM/jury rounds** → a **stronger model** where correctness matters — selected from the widened catalog `models_for_role(requires=...)` (`ops/model_capabilities.json` catalogs the cloud reasoner + larger local tiers); single-4B-jury measures *variance* not *error*, so a real correctness gate wants model diversity (the verify_jury `verdict_rule` slot was built to take a 2nd-model/cloud tiebreak).
- **REDUCE(rule)** → **no model** (deterministic AST over resolved values — `runtime/rules.py:65 RULE_OPS`, the closed grammar; `:114 DESTINATION_KINDS`).
- Per-role model is `model_binding` in the role spec (registry-is-truth) — never hardcoded in the chain; a cascade step's optional `model` must be a live-registry member or `build_action` fails loud.

---

# ① THE REPO EXOCORTEX — ingest the project into an addressable, embedded, queryable corpus

### What it does
Turns the whole project (`~/company` code + `build-prep/` + docs + transcripts) into a **queryable semantic corpus**. Instead of cold-reading files into my context, I *ask* ("where does X happen / what was decided about Y / what did a past session conclude") and get the **addressed top-k slice**. This is the D-layer's first real use — built, only ever proven on seeded vectors. The keystone the other compositions read.

### How it works (the chain)
- **0 · EXTRACT (deterministic, no model):** walk the repo → one unit per file `{path, kind: code|doc|criteria|transcript, text, sha, mtime, module_home}`. Skip `.git`/binaries/`node_modules`. Files > context window → flag for chunk-and-compose. The file list IS the ingest source (the cheap exact floor first). **Lineage gate** (sequencing): `{project: "company", session: "<id>", round: "ingest-1"}` in the corpus-record BEFORE the first capture run.
- **1 · GROUND:** per module → one line "what this module is" from its `AGENTS.md` (declared, no model). Shared as per-file context.
- **2 · MAP** (the swarm): NEW role **`digest_for_index`** × N files → `{one_line_purpose, summary, public_surface, depends_on[], concepts[]}`. Per-unit context: file text (chunked if over-ctx) + module header + 2-3 existing digests as few-shot. Then **embed** `{summary+concepts}`. Output: a corpus-record per file in `space="repo"`, embedded, with `{run://, model, sha}` provenance.
- **3 · REDUCE:** (a) `cluster` → near-duplicate seeds; (b) a `concept→files` inverted index; (c) the `module→files` tree.
- **4 · CONFIRM:** NEW role **`verify_digest`** (jury) re-reads sampled files → grounded? variance → re-digest, never drop.
- **5 · QUERY (the payoff, READ-ONLY):** retrieve-as-input — a role's input = a query over `space="repo"` → top-k addressed slices.

### The models
MAP=resident-4B swarm · EMBED=bge-m3 · CONFIRM=stronger model · the concept-index reduce = rule (no model).

### The exact tool calls (stored-graph steps)
```
# 0. EXTRACT (deterministic, my code / a worker — produces the unit list):
#    units = [{path, kind, text, sha, mtime, module_home}, ...]   # one per file
# 2. MAP+EMBED+CAPTURE (ONE call — capture fans the role AND writes+embeds each record into space="repo"):
capture(role="digest_for_index", units=<file units>,
        project="company", session="${session_id}", round="ingest-1", projection="repo")
#    → per-unit digest at run://<turn>/digest_for_index/<i>, persisted as a corpus record in space "repo",
#      embedded on write (embed_corpus_to_spaces → vector_index.build_index(space="repo")). Lineage GATED.
# 3. REDUCE (cluster — near-duplicate seeds; the inverted index/tree are read-side projections):
run_reduce(addresses=<the repo record addresses>, mode="cluster", cluster_threshold=0.85)
# 4. CONFIRM (jury over a sample):
run_items(role="verify_digest", items=<sampled {digest, file} units>)
# 5. QUERY (the payoff — retrieve-as-input; READ-ONLY, no operator gate):
find_relations(item="${query_item}", near_space="repo", far_space="repo", k=12)   # or a direct query path
```
*Stored-graph form:* `save_cascade({name:"repo-ingest", steps:[{op:"generate",role:"digest_for_index",kind:"items"},{op:"reduce",reduce_mode:"cluster"}], ...})` then `run_cascade("repo-ingest", inputs="<file-list address>")`. (Capture's lineage args ride as fixed decl fields; the file-list is the threaded `inputs`.)
### Codebase addresses
- EXTRACT walker: NEW (mine / a worker) — a `parse.py`-style deterministic scan; lands beside the corpus reader.
- roles: NEW `roles/digest_for_index.py`, `roles/verify_digest.py` — file-discovered via `runtime/roles.py:205 RoleRegistry.discover(["roles"])`; authored by `create_role(spec)`.
- capture+embed: `runtime/suite.py:9633 Suite.capture_corpus` → `runtime/cognition.py:376 embed_corpus_to_spaces`.
- query: `Suite.find_relations` → `store/vector_index.py query_index`.
- staleness (selective re-ingest on sha-change): `store/vector_index.py:175 index_staleness(store, corpus)` (read-only content-hash compare — no embed, no :8001 dependency).

---

# ② DRIFT RADAR — built-twice & doc-vs-code contradiction on the live repo

### What it does
Surfaces **duplicated logic / parallel systems** and **doc-vs-code contradictions / decisions-made-twice-differently** across the live codebase — the coherence prize pointed at the repo. A drift map I could never cheaply produce by hand. (The "criteria-doc said verified but the boxes were stale 🔴" class I hit this very session.)

### How it works (the chain)
- **0 · EXTRACT:** reuse the `space="repo"` corpus + concept-index from ① (no re-embed).
- **3 · REDUCE (the core):** (a) `cluster` over `space="repo"` → the **inversion**: pairs near in *concept*-space but far in *module*-space = same logic in two places (built-twice); (b) per-concept, a role compares doc-digest vs code-digest → "agree?" → contradictions.
- **4 · CONFIRM:** NEW role **`judge_drift`** (jury) reads the actual flagged pairs → "genuinely duplicated/contradicting, or legitimately distinct?" — variance→flag (false-positive guard).
- **5 · ACT:** confirmed → `mark(target, mark_type=built-twice|drift|doc-code-contradiction)` → triage inbox. **Floor: marks + surfaces, NEVER auto-fixes.**

### The models
REDUCE(cluster)=embed-geometry (no generation) · the doc-vs-code compare=4B · CONFIRM=stronger model.

### The exact tool calls
```
# (a) built-twice: the cross-space inversion — near in concept-space, far in module-space:
find_relations(item="${concept_or_file}", near_space="repo", far_space="module", k=10, min_score=0.5)
#     → relations[] = same-logic-different-place candidates (near∩¬far).
# (a') OR cluster the whole space for duplicate groups:
run_reduce(addresses=<repo record addresses>, mode="cluster", cluster_threshold=0.85)
# (b) doc-vs-code contradiction: a role compares the doc-digest vs code-digest per concept:
run_items(role="judge_drift", items=<[{concept, doc_digest, code_digest}, ...]>)
# 5. ACT — confirmed flags become marks (NEVER auto-fix):
mark(target="<file-or-span>", mark_type="built-twice" | "drift" | "doc-code-contradiction", confidence=<j>)
```
### Codebase addresses
- reuses ①'s `space="repo"` corpus + `runtime/cognition.py:1736 run_reduce` (cluster) + `Suite.find_relations`.
- marks: `store/fs_store.py:677 append_mark`; `mark_type` is a member of the file-discovered mark-types registry (`runtime/mark_types.py`, `create_mark_type`-authorable).
- NEW `roles/judge_drift.py` (jury — stronger model via `model_binding`).

---

# ③ TRANSCRIPT MINER — learn how-Tim-thinks + what-keeps-going-wrong from the record

### What it does
Mines the previous session transcripts into structured knowledge: every decision+rationale, every Tim-correction+what-I-did-wrong, every bug+fix, every needs-tim, every named frustration → clustered into **recurring failure-patterns** + an as-built decision log + the standing needs-tim list. Self-improvement *from the record*. (The incomplete-work lesson Tim just gave me would have self-surfaced here.)

### How it works (the chain)
- **0 · EXTRACT (deterministic):** parse the transcript jsonl → per session, exchange-units `{session_id, ts, tim_message, my_response, tools_used, commit_shas}`; over-long → chunk. Lineage `round=transcript-mine-1`.
- **1 · GROUND:** per session → one-line "what this session was about" (cheap 4B over first+last exchange).
- **2 · MAP:** NEW role **`mine_exchange`** × N → `{decision, rationale, tim_correction?+my_error, bug+fix?, needs_tim?, frustration?, pattern_tag}`. Per-unit context: the exchange + session header. → `space="history"`, embedded.
- **3 · REDUCE:** (a) `cluster` the corrections → recurring failure-patterns; (b) cluster decisions → the decision log; (c) collate `needs_tim` → standing open-list.
- **4 · CONFIRM:** NEW role **`judge_mining`** validates a sampled cluster against the raw exchange (no-fiction).
- **5 · ACT:** failure-clusters → **DRAFT `feedback-*` memory files** → I review + write (the memory write is mine). **Floor: drafts, I confirm before writing.**

### The models / addresses
MAP=4B · EMBED=bge-m3 · CONFIRM=stronger. Transcript path (GROUNDED): `/home/tim/.claude/projects/-home-tim/*.jsonl`. NEW `roles/mine_exchange.py`, `roles/judge_mining.py`. Memory dir (GROUNDED): `/home/tim/.claude/projects/-home-tim/memory/` (the `feedback-*.md` files + `MEMORY.md` index — where the drafted lessons land, after I confirm).
```
# 0. EXTRACT (deterministic): parse the jsonl → exchange units [{session_id,ts,tim_message,my_response,...}]
# 2. MAP+EMBED+CAPTURE into space="history":
capture(role="mine_exchange", units=<exchange units>,
        project="company", session="${session_id}", round="transcript-mine-1", projection="history")
# 3. REDUCE (cluster the corrections → recurring failure-patterns):
run_reduce(addresses=<the history record addresses>, mode="cluster", cluster_threshold=0.82)
# 4. CONFIRM:
run_items(role="judge_mining", items=<sampled {cluster, raw_exchange} units>)
# 5. ACT: draft feedback-*.md → I review + write (the memory write is MINE, not auto).
```

---

# ④ PRE-FLIGHT SCOUT BRIEF — a saved cascade so I arrive grounded, not cold

### What it does
Given a task, the *free swarm* assembles my brief: what exists · related code (addresses) · prior decisions · risks · what's-been-tried · live criteria. The expensive "read everything first" moves off my budget. The first real **`save_cascade`** — authored once, `run_cascade("preflight-brief", task=X)` per task.

### How it works (the chain)
- **1 · RETRIEVE:** query `space="repo"` (①) on the task → top-k slices.
- **2 · MAP:** NEW role **`scout`** × the slices → `{relevant_how, risk, prior_decision?, what_exists}`. Per-unit context: slice + task.
- **3 · REDUCE** (`mode=role`, NEW role **`brief_synth`**): → ONE brief at `run://<turn>/brief`.
- **5 · OUTPUT:** I read the brief, start grounded. **No confirm — advisory, I judge it.**

### Stored-graph + template vars (the canonical example)
```
# Author once:
save_cascade(decl={
  "name": "preflight-brief",
  "steps": [
    {"op": "generate", "role": "scout",       "kind": "items"},   # MAP over the retrieved slices
    {"op": "reduce",    "role": "brief_synth", "reduce_mode": "role"}  # JOIN → one brief
  ],
  "output_schema": {"what_exists": "str", "related_code": "list[str]", "prior_decisions": "list[str]",
                    "risks": "list[str]", "tried": "list[str]", "live_criteria": "list[str]"}
})
# Run per task (the ${task} enters as the threaded `inputs`):
run_cascade("preflight-brief", inputs="<the task description, or a run:// address of the retrieved slice-set>")
#   → final_output = the brief at final_address; each step op.run-indexed (find_runs sees them).
```
*(Step 0's retrieve is `find_relations`/query over `space="repo"` on the task — run inline before the cascade, OR as a `retrieve`-op step once that engine primitive lands [flagged N2/needs-build: retrieve/similarity ops have no engine primitive yet; today retrieve runs inline and feeds the cascade `inputs`].)*
### Codebase addresses
NEW `roles/scout.py`, `roles/brief_synth.py`; reuses `runtime/suite.py:861 save_cascade` / `:888 run_cascade` + the GROUP-N runner + ①'s retrieve (`Suite.find_relations`).

---

# ⑤ BACKGROUND SELF-AUDIT — the system watches its own changes between my turns

### What it does
On a cadence (the dormant CALLER, Tim's enable), the swarm scans recent diffs/commits for floor-violations, hardcoding, self-description drift, **unverified "done" claims**, registry-is-truth violations → a triage inbox. I wake to "what needs attention," not a cold re-derive (the exact pain of every build-loop fire). The introspective-data law, live.

### How it works (the chain, per tick)
- **0 · EXTRACT (deterministic):** `git diff` since the audit-cursor → changed hunks; run-index events since cursor; the inbox.
- **1 · GROUND:** changed files' module headers + the relevant law text (`AGENTS.md`).
- **2 · MAP:** NEW role **`audit_change`** × hunks → `{floor_violation?, hardcoding?, drift?, unverified_done?, registry_violation?}`. Per-unit: hunk + law.
- **3 · REDUCE:** collate → triage by severity.
- **4 · CONFIRM:** jury re-checks high-severity (false-positive guard).
- **5 · ACT:** surface a triage inbox (the rollup destination). **Floor: surfaces only; cadence is Tim's.** Provenance per finding.

### The models / addresses / gate
MAP=4B · CONFIRM=stronger. Reuses the CALLER + rollup driver + run_items + marks. NEW `roles/audit_change.py`. The dormant gate (GROUNDED): `runtime/activation_driver.py:84 activation_loop_enabled()` reads env `COMPANY_ACTIVATION_LOOP` (default OFF — importing the bridge auto-starts nothing); a tick is `runtime/activation_driver.py:162 ActivationCaller.activation_tick()`. The diff cursor: a held high-water cursor (like the run-index incremental fold).
```
# Manual / external drive (today): POST /api/activation/tick   (fires the DUE clock drivers + detector)
# The audit MAP each tick (the rollup driver's work):
run_items(role="audit_change", items=<changed-hunk units [{hunk, file, module_law}, ...]>)
run_items(role="judge_audit",  items=<high-severity flags>)        # CONFIRM
#   → flags surface to a triage inbox (the rollup destination). FLOOR: surfaces only; cadence is Tim's
#     greenlight (COMPANY_ACTIVATION_LOOP=1 + the interval).
```

---

# ⑥ VERIFICATION JURY — defense-in-depth verification of every change, for free

### What it does
On any change, instead of one verification pass (mine, serialized), fan a **jury of distinct lenses** (correctness · floor · drift · matches-criterion · registry-is-truth · adversarial-disprove) of free models → I consume the tallied verdict + only the failing/uncertain evidence. Every commit gets six parallel angles at ≈zero token-cost to me. The first composition I'd `save_cascade` and run as the standard close of every lane. **Needs no GPU window — runs on the 4B today.**

### How it works (the chain)
- **0 · EXTRACT (deterministic):** the change = `{diff_hunks, criterion, test_paths, module_law}`.
- **1 · GROUND:** the criterion's FUNCTION+FORM bars + the floor law + module `AGENTS.md` — what each juror is held to.
- **2 · MAP:** NEW role **`verify_lens`** × the lenses (same role, N lens-prompts via the unit's `lens` field) → `{lens, verdict: pass|fail|uncertain, evidence, the-case-that-breaks-it}`. Per-unit: the diff + the bar for *that* lens.
- **3 · REDUCE** (`mode=rule`, deterministic — NOT a model): tally → `green only if every lens passes; any fail→fail; any uncertain→FLAG`. Replay-identical (C0.2 determinism) despite nondeterministic juror finish-order.
- **5 · OUTPUT:** I read the verdict + failing evidence only. **Floor: advisory — a juror NEVER commits; I commit.**

### The models / addresses
MAP=4B (the adversarial-disprove lens is the variance-not-error gate built in; for correctness-critical, one juror = stronger model via `model_binding`) · REDUCE=rule (no model — `runtime/rules.py:65 RULE_OPS` closed grammar, `:114 DESTINATION_KINDS`). NEW `roles/verify_lens.py`. Reuses `run_items` / `run_reduce(mode="rule")`.
```
# 2. MAP — one role, N lenses (the lens rides in each unit):
run_items(role="verify_lens", items=[
  {"lens":"correctness",          "diff":"${diff}", "bar":"${criterion_function}"},
  {"lens":"floor",                "diff":"${diff}", "bar":"<no resolve/dispatch/claude -p>"},
  {"lens":"drift",                "diff":"${diff}", "bar":"<self-description updated>"},
  {"lens":"matches-criterion",    "diff":"${diff}", "bar":"${criterion_function}"},
  {"lens":"registry-is-truth",    "diff":"${diff}", "bar":"<no hardcoded list>"},
  {"lens":"adversarial-disprove", "diff":"${diff}", "bar":"<find the input that breaks it>"}])
# 3. REDUCE — deterministic tally (NO model; replay-identical):
run_reduce(addresses=<the verify_lens output addresses>, mode="rule", reduce_rule="<all_pass_else_flag>")
#   → green iff every lens passed; any fail→fail; any uncertain→FLAG for me. FLOOR: advisory, I commit.
```
*Stored-graph:* `save_cascade({name:"verify-jury", steps:[{op:"generate",role:"verify_lens",kind:"items"},{op:"reduce",reduce_mode:"rule",reduce_rule:"<tally>"}]})` — the standard close of every lane; `run_cascade("verify-jury", inputs="<diff+criterion address>")`.

---

# ⑦ SPEC-COMPILER — Tim's dense seed → a loop-prep triad, drafted from the project corpus

### What it does
Tim's seed → a chain drafts the three loop-prep docs (Completion-Criteria, Implementation-Guide, Research-Synthesis) grounded in the project corpus; I refine, Tim steers. The loop-prep I keep building by hand, compiled. **No GPU window** (uses ①'s corpus if present; degrades to direct file-read scout if not).

### How it works (the staged chain)
- **0 · EXTRACT:** the seed = root unit + retrieve the relevant corpus-slice on the seed's concepts (explore-before-specifying, automated).
- **1 · GROUND:** the slices + existing build-prep triads as few-shot (house style: two-faced FUNCTION/FORM, honest-status, registry-is-truth).
- **2a DECOMPOSE** (role **`decompose_seed`**, 1×1): seed → candidate criteria-groups + systems-touched.
- **2b EXPAND** (run_items, role **`expand_criterion`** × groups): each → a full two-faced criterion `{id, FUNCTION, FORM, files-touched, reuse-vs-net-new, preserves}`. Per-unit: group + its slice + few-shot.
- **2c GROUND-CHECK** (run_items, role **`ground_criterion`** × criteria): each vs the corpus → "build-on exists? cite file" → `reuse` (cite) vs `net-new` (honest). No-fiction on the spec.
- **3 · REDUCE** (`mode=role`, role **`triad_synth`**): assemble → the three docs (synthesis = the reduce of 2c).
- **4 · CONFIRM:** jury vs the seed → "covers it? any group fabricated / reuse-claim unverifiable?" → flags.
- **5 · PROPOSE → me → Tim. Floor: a draft — never a build off an unconfirmed compiled spec.**

### Addresses
NEW roles `decompose_seed`, `expand_criterion`, `ground_criterion`, `triad_synth` (+jury). Reuses retrieve + `run_items`/`run_reduce` + the few-shot pattern. Output dir: `build-prep/<topic>/` (the triad lands as 3 .md files I refine).
```
# 2a DECOMPOSE (1×1):
run_role(role="decompose_seed", utterance="${seed}")          # → candidate criteria-groups
# 2b EXPAND (MAP over the groups):
run_items(role="expand_criterion", items=<[{group, corpus_slice, fewshot}, ...]>)
# 2c GROUND-CHECK (MAP over the criteria — no-fiction on the spec):
run_items(role="ground_criterion", items=<[{criterion, corpus_slice}, ...]>)   # → reuse(cite) | net-new
# 3 REDUCE → the triad:
run_reduce(addresses=<the grounded-criterion addresses>, mode="role", role="triad_synth")
# 4 CONFIRM (jury vs the seed) → flags. 5 PROPOSE → me → Tim. FLOOR: a draft, never a build off it.
```
*Stored-graph:* `save_cascade({name:"spec-compiler", steps:[{op:"generate",role:"decompose_seed"},{op:"generate",role:"expand_criterion",kind:"items"},{op:"generate",role:"ground_criterion",kind:"items"},{op:"reduce",role:"triad_synth",reduce_mode:"role"}]})`; `run_cascade("spec-compiler", inputs="${seed}")`.

---

# ⑧ SELF-EXTENDING TOOLMAKING — the registry accretes the faculty the work reveals

### What it does
When I (or a worker) repeatedly want a lens/role/skill that doesn't exist and improvise it inline, that want is the signal: distill it into a real, discoverable, composable registry primitive — DIRECT (declarative) or GATED (code). Over sessions the role/skill registry becomes a fingerprint of every lens the work ever needed. **This is the self-advancing cycle, literally.**

### How it works (a reflex with a guard, not a fixed pipeline)
- **TRIGGER:** "I improvised a prompt/logic inline and used it 2-3×."
- **0 · EXTRACT:** the improvised prompt/logic + the places used.
- **2 · MAP** (role **`distill_faculty`**, 1×1): → a clean role spec `{id, prompt_template, output_schema (richer types — nested/enum/optional), input_addresses, op, few-shot from the real uses}` OR a skill recipe (multi-step → AK3 skill).
- **3 · THE GATE (the floor distinction, Tim's correction):**
  - **declarative** faculty (role/skill/context/projection/mark-type) → `create_*` **DIRECT, no approval** (renders→correctness-gate→commit→rediscover→live, git-revertible).
  - **executable-code** faculty (node-type / a lifter|form that's a Python callable) → stays **GATED** (propose→surface→operator).
- **5 · OUTPUT:** next session `cognition_info` shows it; the pipelines compose it.

### Addresses
NEW `roles/distill_faculty.py`. Reuses `create_role`/`create_skill`/`create_projection`/`create_mark_type` (`runtime/suite.py:8932`/`9004`/`9127`) — the correctness-gate (render in tempdir → it must import + the role-registry must discover it → else REFUSED, nothing written) is what enforces the declarative-direct vs code-gated line (governance 42/42 asserts no `create_*` path can reach a build-dispatch). Richer `output_schema` grammar: `runtime/authoring.py` recursive renderer (kind: scalar/enum/object/list[object]).
```
# 2. DISTILL the improvised faculty into a spec (1×1):
run_role(role="distill_faculty", utterance="<the inline prompt/logic + the 2-3 places it was used>")
# 3. THE GATE — declarative → DIRECT (no approval):
create_role(spec={"id":"<new_role>", "prompt_template":"...", "output_schema":{...richer...},
                  "op":"generate", "thinking":false, "tools":[], "model_binding":"...",
                  "input_addresses":[...], "mode_scope":[...], "rules":[...], "context":[...]})
#   → renders roles/<new_role>.py → correctness-gate → commit → rediscover → LIVE in cognition_info.
#   (an executable-code faculty — a node-type / callable lifter|form — instead goes propose→surface→operator: GATED.)
```

---

# ⑨ DURABLE CROSS-SESSION MEMORY — the project remembers itself past the context boundary

### What it does
Each session embeds its handoff `{commits, decisions, needs-tim, lane-state, next-move, gotchas}` into the corpus (addressed); a new session **retrieves** the relevant prior context by semantic match instead of the lossy auto-compaction summary. Retrieval-augmented continuity — I lost context 3× this session and rebuilt from a summary; this makes the boundary stop being amnesia.

### How it works (the chain)
- **0 · EXTRACT (session-end, deterministic):** this session's `{commits, decisions, needs-tim, lane-state, handoff}` (much of which ③ already structures).
- **2 · MAP** (role **`session_memo`**, 1×1): → a memo `{what-changed, why, what's-open, next-obvious-move, gotchas}`; embed → `space="history"`, addressed `run://session/<id>/memo`.
- **5 · QUERY (next session-start):** retrieve over `space="history"` on the opening task → relevant prior memos surface by semantic match.

### The honest reuse-decision (surface, don't assume)
This **overlaps episodic-memory + the existing memory system** (GROUNDED): there's already (a) the `episodic-memory` plugin (`search-conversations` agent — semantic conversation search), (b) the file memory at `/home/tim/.claude/projects/-home-tim/memory/` (`feedback-*`/`project-*` + `MEMORY.md` index), and (c) the `agent-boot-sequence` skill that loads context at session-start. The right build is "embed the session handoff into `space="history"` (③'s space) + point the boot-sequence at a retrieve over it," NOT a parallel memory store (reuse-don't-parallel). **Decision for Tim** (which of the three this complements vs extends).
```
# 0. EXTRACT (session-end): {commits, decisions, needs-tim, lane-state, handoff}
# 2. MAP+EMBED+CAPTURE the memo into space="history":
capture(role="session_memo", units=[<the session handoff>],
        project="company", session="${session_id}", round="memo", projection="history")
# 5. QUERY (next session-start, via the boot-sequence):
find_relations(item="${opening_task}", near_space="history", far_space="history", k=8)   # or direct query
#   → the relevant prior memos by semantic match (not the lossy compaction summary). FLOOR: read-only retrieval.
```

---

# ⑩ OPTION-PANELS — a pre-scored A/B/C option-space for Tim's forks, generated by a panel

### What it does
For a design fork (Tim's A/B/C pattern), fan independent free-model roles each developing a *distinct* approach (MVP-first · risk-first · reuse-first · framework-first · radical-recompose) + a judge reduce → a **pre-scored option-space with a reasoned recommendation that grafts the best of runners-up**. The CLAUDE.md "offer options" rule, supercharged — generated by a diverse panel, not my single framing. **No GPU window.**

### How it works (the chain)
- **0 · EXTRACT:** the decision-point = `{question, constraints, corpus-slice}`.
- **1 · GROUND:** the slice (what exists/constrains) + Tim's framework (relational-systems, offer-options) as the *scoring rubric*.
- **2 · MAP** (run_items, role **`develop_option`** × the lenses): each lens independently → a full approach `{approach, buys, costs, touches, risk}`. Per-unit: question + constraints + that lens's bias.
- **3 · REDUCE** (`mode=role`, role **`score_options`**): score vs the rubric + synthesize a recommendation grafting runner-up strengths (judge-panel pattern — beats one-attempt-iterated when the space is wide).
- **5 · OUTPUT → Tim:** a pre-scored space + reasoned rec. **Floor: advisory — Tim decides; I never pick a fork.**

### Addresses
NEW `roles/develop_option.py`, `roles/score_options.py`. Reuses retrieve + `run_items`/`run_reduce`.
```
# 2. MAP — each lens independently develops a full approach:
run_items(role="develop_option", items=[
  {"lens":"mvp-first",        "question":"${question}", "constraints":"${constraints}"},
  {"lens":"risk-first",       "question":"${question}", "constraints":"${constraints}"},
  {"lens":"reuse-first",      "question":"${question}", "constraints":"${constraints}"},
  {"lens":"framework-first",  "question":"${question}", "constraints":"${constraints}"},
  {"lens":"radical-recompose","question":"${question}", "constraints":"${constraints}"}])
# 3. REDUCE — score vs Tim's rubric + synthesize a rec grafting runner-up strengths:
run_reduce(addresses=<the develop_option output addresses>, mode="role", role="score_options")
#   → a pre-scored option-space + reasoned recommendation. FLOOR: advisory — Tim decides; I never pick a fork.
```
*Stored-graph:* `save_cascade({name:"option-panel", steps:[{op:"generate",role:"develop_option",kind:"items"},{op:"reduce",role:"score_options",reduce_mode:"role"}]})`; `run_cascade("option-panel", inputs="${question}")`.

---

# ⑪ THE GRUNT-OFFLOAD REFLEX — the standing law, not a feature

### What it does
Any sub-task that is **broad + shallow + repetitive + judgment-light** does NOT touch my context — it becomes a `run_items` fan over the swarm, and I consume the structured result. Not a feature: a **routing reflex** I apply to myself. Kills the failure mode of *me burning Opus context on work a 4B does as well and 100× cheaper, while losing the deep thread.*

### How it works (the shape, every time)
EXTRACT the units (files / callers / issues / failures) deterministically → `run_items` a fit-for-purpose role (often `create_role`'d on the spot per ⑧) → `run_reduce` or just read the structured map.

### Standing instances (each a one-line `run_items`)
- rename-impact: "every caller of `X`, classified safe/risky-to-rename"
- "summarize these 50 files" · "first-pass-triage these 200 issues by theme"
- "classify these test failures by root-cause" · "which of these 80 files mention the deprecated pattern"

### The discipline
Before I default to *reading*, I default to **"can the swarm do the broad part?"** It's the whole asymmetry operationalized into a habit. No new files — it's `run_items` + a per-task role (often `create_role`'d on the spot per ⑧, then it's a reusable registry primitive).
```
# The bare grunt fan (the reflex):
run_items(role="<fit-for-purpose, e.g. classify_caller>", items=<the N units (files/callers/issues/failures)>)
#   → a structured map I read; OR run_reduce to collapse it. The role is created inline (⑧) if it doesn't exist.
# e.g. rename-impact:  run_items(role="classify_caller", items=[{symbol:"X", file, snippet}, ...])
```

---

# ⑫ ENGINE-IMPROVES-ENGINE — the build's next phase, self-drafted

### What it does
The engine's own open items (the needs-tim list + flagged follow-ups + ②/⑤ findings) become corpus units; a scout swarm grounds each against the code + drafts a fix-plan + a buildable lane-cut; I review + dispatch (the same build-loop I've run, **but the plan was drafted by the engine reading itself**). Closes the self-build.

### How it works (the chain)
- **0 · EXTRACT:** the open items → units `{gap, related-criterion, named-files}`. Sources: the needs-tim list + follow-ups (role-scoped capability gating · `capability_providers()` live-bind · retrieve-as-input first-class · cluster-on-live-corpus · the run_items-scheme edge) + ②/⑤ findings.
- **1 · GROUND:** each gap's named files, retrieved from ①.
- **2 · MAP** (run_items, role **`scout_fix`** × gaps): each → `{root-location, the-seam, fix-sketch, reuse-vs-net-new, risk, blast-radius}`. Per-unit: gap + code-slice + law.
- **3 · REDUCE:** order by `{leverage, file-disjointness}` → a buildable lane-plan (literally the next loop's lane-cut).
- **4 · CONFIRM:** jury checks each sketch is grounded + floor-safe + reuse-not-parallel.
- **5 · PROPOSE → me → dispatch.** **Floor: the PLAN is swarm-drafted; the build-dispatch (`claude -p`) stays mine — workers never self-dispatch.**

### Addresses
NEW `roles/scout_fix.py`, `roles/lane_plan_synth.py`. Reuses ①'s corpus + `run_items`/`run_reduce` + jury. The needs-tim source (GROUNDED): `.build/cognition-engine/WALKTHROUGH.md` (the needs-tim checklist + 🟡-partial list) + the lane reports' `flag` fields in `.build/cognition-engine/state.json`.
```
# 0. EXTRACT: the open items → gap units (from WALKTHROUGH.md + state.json flags + ②/⑤ findings)
# 2. MAP — scout each gap against its code:
run_items(role="scout_fix", items=<[{gap, related_criterion, named_files, code_slice}, ...]>)
# 3. REDUCE — order by {leverage, file-disjointness} → the buildable lane-cut:
run_reduce(addresses=<the scout_fix output addresses>, mode="role", role="lane_plan_synth")
# 4. CONFIRM (jury: grounded? floor-safe? reuse-not-parallel?). 5. PROPOSE → me → I dispatch the build-workers.
#   FLOOR: the PLAN is swarm-drafted; the build-dispatch (claude -p) stays MINE — workers never self-dispatch.
```
*This is the build-loop's new front-end: the engine reads its own open items and drafts the next lane-cut; I review + dispatch (the loop I've run by hand, now self-fed).*

---

## FIRST-USE FRICTION IS THE ⑫ INPUT (the self-advancing mechanism, concretely)
Using these by-use *will* surface bugs / confusions / missing capabilities — the first time any app is used. The difference now: I fix them **from all sides at once** — hit a missing capability mid-composition → `create_role` it (⑧) or dispatch a worker to build the engine seam (⑫) while the composition keeps running. **The first-use friction becomes the ⑫ input.** Using it generates the list of how to improve it, and I implement that list immediately, in parallel, from both the strategic seat and the agent-swarm. That is the cycle.

## BUILD ORDER (dependency + GPU-honest)
1. **⑥ verification-jury** (no GPU; makes every *other* build safer-by-use — build first).
2. **① repo exocortex** (GPU window — also closes the live-embed + 32-knee needs-tim; the floor for ②③④⑨⑫).
3. **④ scout-brief + ⑦ spec-compiler + ⑩ panels** (on ①; the serve-Tim layer).
4. **② drift-radar + ③ transcript-miner** (on ①).
5. **⑤ background self-audit** (CALLER cadence — Tim's enable).
6. **⑧ toolmaking + ⑪ offload** are reflexes — live from day one, no "build".
7. **⑫ engine-improves-engine** — runs continuously once ① exists; the loop's new front-end.

## STATUS / GROUNDING
- **v1 — GROUNDED (2026-06-09).** Every tool-call block + codebase address resolved against the LIVE MCP tool schemas (`run_items`/`run_reduce`/`run_role`/`capture`/`find_relations`/`save_cascade`/`run_cascade`/`list_cascades`/`mark`/`create_role`/`inspect_address` — all confirmed loaded as `mcp__company__*` this session) + the real `file:line` (`runtime/cognition.py`, `runtime/suite.py`, `runtime/coherence_actions.py`, `store/fs_store.py`, `store/vector_index.py`, `runtime/activation_driver.py`, `ops/services.json`, `fabric/config.py`). Service ids: `chat-4b`/Qwen3.5-4B-AWQ@:8000 (swarm) · `embed-bge`/BAAI/bge-m3@:8001/1024-dim. Floor 42/42.
- **Two honest needs-build flagged in-line** (not green-painted): (a) per-step *multi-variable* prompt substitution in a cascade decl — today the decl threads one `inputs` value + fixed per-step roles; (b) the `retrieve`/`similarity` cascade *ops* have no engine primitive yet (today retrieve runs inline and feeds the cascade `inputs`). Both are real cascade-runner rungs, surfaced.
- Floor invariant + no-fiction law hold across all twelve (asserted by the 42/42 governance scan + the per-role grounding contexts, not assumed).
- **These twelve are themselves corpus units** — once ① ingests `build-prep/`, this doc becomes retrievable, and ⑫ can scout *it* for the next build. The compositions describe the engine that will read them.
