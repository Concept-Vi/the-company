# Field report — wizard run-1 (the full recount: what I did, found, built, reframed, and got wrong)

> **What this is:** a *first-person recount* from the session that actually ran the model fleet hard — bulk local
> 4B concurrency, enforced structured output, embeddings, a cloud reasoning model — against ~5,000 real files of
> Tim's scattered project corpus. It is **NOT instructions.** It's what I did, what broke, **how my thinking
> changed (the reframes and dead-ends — those are signal: they tell you what NOT to rebuild)**, and where
> everything lives. Other sessions (esp. whoever's building MCP tools for model-concurrency + embedding runs)
> take what's useful and decide their own path; Tim guides. Paths are absolute. All of this is *evidence from one
> real run*, not a settled spec — and several things are explicitly still open.

---

# PART 0 — Who I am, when this was, and why I'm worth reading (in my own voice)

A note from me, directly, to whoever's reading this — because context about *the source* matters as much as the
content.

**When:** I did this work around **2026-06-04 to 2026-06-05.** It's now several days later (writing/last-touching
this ~2026-06-09). In a project moving as fast as this one, that's a real gap — **you have almost certainly been
working on much later stages of the broader application than I ever saw.** I am, frankly, *behind* on where the
Company is now. Assume I'm out of date on the current app state, the engine's latest shape, what's been built
since — defer to your own knowledge there. **Do not treat me as current; treat me as deep on one thing.**

**What I was doing before this:** I was working with Tim on the **Project→Product pipeline Blueprint** — the
repeatable process for turning his abandoned/unfinished projects into finished, deployed products (Phase B:
walking the whole design with him and correcting it together). That blueprint work escalated, deliberately, into
*actually running an early by-hand version of the pipeline* on a real corpus — the ElevenLabs Wizard project —
to discover how the process really behaves. That run **is** this report.

**What I actually did:** I ran the model fleet *hard and by hand* against ~5,000 real files — bulk local-4B
concurrency, enforced structured output, embeddings, a cloud reasoning model — through many rounds (scan, embed,
cluster, dedup, the form survey, the projection capture), looking at each output and letting it steer the next
move. I hit the walls documented here for real, not in theory.

**What's mine vs ours:** very little of the *good* thinking here is mine alone. The method — patterned visibility,
the corpus-is-lossy-echoes reframe, projections, the cascade, the economics, render-not-judge — came out of a
long, dense back-and-forth **with Tim**, who repeatedly caught my mis-framings (asking judge-questions at the map
level, the lazy "escalate it to a bigger model" reflex, theorising about failures instead of *reading the raw
output*). The single most valuable discipline in this whole report — *look at the actual output before forming a
theory; "the content is too big" is the last hypothesis* — is something Tim drove me to, hard, after I'd burned
three wrong fixes. Read the reframes in Part B in that spirit: they're a record of getting corrected.

**Why I'm still worth reading despite being behind:** you've been building the broader application — the later
stages, the wider system. **I came at it from a different angle: the ground-level reality of *running the models*
for corpus-reconstruction/capture.** Nobody has spent more concrete time than I have in *that specific layer* —
what the 4B actually does under load, how structured output really fails, what embeddings of *projections* (not
raw text) buy you, where the cascade earns its keep. So I'm not current, but I'm **the most resource-rich source
on this particular angle** — the model-concurrency / capture / embedding *depths*. That's exactly the layer the
MCP-tool work touches, which is why Tim pointed you here. Take the depth; ignore me on anything about "where the
app is now."

---

# PART A — Orientation: what the run is for, and the strategic arc

**The job:** a by-hand pass of Tim's project→product pipeline on the **ElevenLabs Wizard corpus** (~5,052 files
under `/mnt/c/Users/Workstation001/Documents/Claude/Projects/Visual Designer/`), to work out **how to turn the
wizard system into a finished product** (target = the broader *universal agent-driven interface*, not just voice).

**The governing reframe (this changes everything downstream):** the corpus is **scattered, unreviewed AI-echoes of
Tim's mental model** — every file AI-generated from conversations with him, written *as-if-final*, no two with
shared context, none checked by him. So:
- **The gold is the underlying MEANING** — the principles/intentions of his mental model — **NOT the surface
  artifacts** ("decisions/schemas/components"), which are unreliable renderings.
- **Relevance INVERTS face value.** Tim showed me `sequences-in-sequences.md` never says "wizard" yet is a core
  *principle* of it. Keyword match fails; even raw-text semantic similarity fails; the link lives at the
  *principle* level. This single fact justifies most of the design (projections, multi-level embedding).
- **Build path = reconstruct-intent → confirm with Tim → design fresh.** NEVER "lift these designs."

**The strategic arc (multi-stage — you cannot one-shot "what the wizard is" from 5,000 unread files):**
1. **Stage 1 — Legibility map** *(built, calibrated on a sample, NOT yet run full)*: turn every file into a
   compact, comparable, embeddable multi-level representation. Purpose: make the corpus *viewable to me* (the
   reduce-reasoner) — I literally can't reason over what I can't hold. This is the foundation everything reads from.
2. **Stage 2 — Embed the projections + survey** *(not started)*: embed each projection into its own space,
   cluster, see the shape (principle-families, coined-vs-generic split).
3. **Stage 3 — Relation-finding** *(not started)*: cross-level queries (the inversion-finder), link-graph, typed
   relations — find how files connect, incl. the face-value-hidden links.
4. **Stage 4 — Marks** *(not started)*: corroboration / fingerprints / idiosyncratic-vs-generic, proposed-with-
   evidence, Tim-confirmed.
5. **Stage 5 — Organized network map** *(the goal-state)*: nodes (files+projections+marks) + typed edges +
   clusters → navigable map of what everything is and how it relates → from which the reconstruction + targeted
   deep-extractions get chosen.
Each stage's output is *looked at* and shapes the next ("patterned visibility" — run → look → patterns → next
step → repeat; not pre-scripted). **I have only built + calibrated Stage 1.**

**Connection to your work:** this whole by-hand run is a *prototype of pipeline capabilities that should become
Company engine node-types / MCP tools* — model-concurrency runs, embedding runs, the cascade, the marks layer.
What I did manually in `~/wizard-run-1/` is the rough draft of what you're building properly.

---

# PART B — How my thinking CHANGED (the reframes & dead-ends — read this, it saves you my mistakes)

These are the turns where I had it wrong and corrected. Each is a thing **not to rebuild the wrong way:**

1. **"Extraction" → "multi-level PROJECTIONS."** I started thinking of capture as *one* extraction per file. Wrong
   framing. It's **many typed projections at different altitudes**, each separately comparable/embeddable. The
   word "extract"/"identify"/"answer" all carry a judgment connotation; the right verb is **render** (faithfully
   represent at each level). This reframe is *the* structural insight of the run.
2. **"Find the gold per file" (judge) → "render faithfully" (the map-vs-reduce mislevel).** My first capture prompt
   told the small model to identify "the gold / what's untrustworthy / infer the unstated" — i.e. a **reduce-level
   judgment asked at the map level, per file, in isolation.** That's exactly the error to avoid: a per-file small-
   model pass should DISTILL what's there; gold/trust/relevance judgment happens **later, over the aggregate**
   (corroboration etc.). Match the question to the level.
3. **Exhaustive → distillative (output must match the stage's job).** An over-broad schema made the model emit a
   **178-item `stated_claims` transcript** — basically re-rendering the file sentence-by-sentence (median output
   ballooned to 11k+ chars, max 61k). A *legibility* pass wants the **compact picture**, not a transcript. Fix:
   the exhaustive fields became a **separate `deep` stage** (see Part D). Lesson: don't ask a pass for more than
   its job needs.
4. **"Dense files too rich" → degenerate repetition LOOP (my most expensive wrong turn).** ~20% "failed"; I theorised
   three fixes in a row (raise budget → cap arrays → escalate to a bigger model) all built on "these files are too
   dense." **All wrong.** The truth, found only by reading raw output: the 4B falls into **repetition loops**
   (details in Part C §loop). One decoding parameter fixed what a whole escalation subsystem was about to be built
   for. **The meta-lesson Tim made me make permanent: on failure, READ THE RAW OUTPUT before theorising; "content
   too big" is the LAST hypothesis, not the first.**
5. **Capping arrays (rejected) → why arbitrary caps are wrong.** I nearly added `maxItems:30`. Tim rejected it:
   capping silently discards real content (a file with 40 real principles should surface 40). The fix is never a
   cap — it's *changing what you ask for* (distillative vs exhaustive) and *fixing the generation* (penalty), not
   amputating output.
6. **Form-keyed → projection-keyed, with forms still routing.** Capture started as "form → schema bucket → form-
   specific fields." Then projections became the main frame. They now **coexist**: forms route (light-vs-substance
   + a few form-specific fields); projections are the broad multi-level lenses. (See Part D — this coexistence is
   slightly untidy and worth cleaning; flagged.)
7. **"Escalate failures to the cloud" reflex → trace first.** My instinct on any failure was "send it up a tier."
   Almost always wrong as a *first* move — the failures were local-model generation bugs fixable in place. Escalation
   is a real tool (the cascade) but not a substitute for understanding the failure.

**The pattern across all of these:** I kept proposing fixes from theory; the right answer came from *looking at the
actual output/data*. Build your tools so that *looking is cheap and default* (dump raw output, persist finish_reason,
read before deciding).

---

# PART C — The engineering reality (the walls you'll hit too)

## Environment (concrete)
- **Box:** WSL2, 16GB RTX 4080. **`nvidia-smi` is NOT on PATH** in this shell — infer VRAM pressure from
  OOM/connection-refused, not from queries. A **WSL restart silently killed ALL model servers mid-session**
  (every process uptime reset; connection-refused looked like a code bug but wasn't — check liveness first).
- **Local LLM — vLLM OpenAI-compatible @ `http://localhost:8000/v1`**, model `cyankiwi/Qwen3.5-4B-AWQ-4bit`.
  Launch scripts in **`~/vllm-tests/`**. The one I used is **`serve_scan.sh`** — exact flags:
  `--gpu-memory-utilization 0.80 --max-model-len 32768 --max-num-seqs 16 --enable-prefix-caching
  --chat-template ~/vllm-tests/chat_template_nothink.jinja --trust-remote-code`. (`serve.sh` is the 4K-context
  production variant — it 400s on real documents; don't use it for whole-file work.)
- **Embeddings — bge-m3 @ `http://localhost:8001/v1/embeddings`** (`serve_embed.sh`, gpu-util ~0.30), 1024-dim,
  POST `{"model":"BAAI/bge-m3","input":[...]}`.
- **Cloud reasoner — Kimi via Ollama @ `http://localhost:11434/v1`**, model **`kimi-k2.6:cloud`**. ~6–10 concurrent
  allowed, **256K** context, credits reset every few days — Tim: **don't over-restrict it.** Other ollama cloud
  models: `deepseek-v4-pro:cloud`, `qwen3.5:397b-cloud`, `glm-5:cloud`.
- **State on ext4 only.** Tim's hard rule: DBs/state in `~/` (mine: `~/wizard-run-1/`), **NEVER `/mnt/c`** (the
  Windows mount — slow + file-locking issues). Docs/vault are on `/mnt/c`.

## Structured output — the most important thing for bulk runs
- **Use enforced JSON schema, NOT loose JSON.** `response_format:{"type":"json_object"}` only forces *valid* JSON,
  not a *shape* — the model freelances and can return empty-but-valid `""`. The reliable mode:
  `response_format:{"type":"json_schema","json_schema":{"name":"cap","schema":<JSON-Schema-dict>}}` — vLLM
  grammar-constrains the decode to your schema. Verified working on the 4B.
- **`guided_json` extra-body param is IGNORED by this vLLM build** (returned prose). Use the `json_schema`
  `response_format` form specifically.
- **Grammar-constrained output is valid ONLY if generation COMPLETES.** Hit `max_tokens` mid-object
  (`finish_reason="length"`) → truncated → invalid JSON. **`finish_reason` is the field that matters** — persist it.

## The degenerate-repetition loop (the big one) — full detail
**Symptom:** ~20% of files produced empty/garbled capture. **Cause (found by reading raw output):** the small 4B,
at temperature 0 with long grammar-constrained arrays, **loops** — good content for early fields, then repeats one
phrase until any budget dies (`finish=length` at 8k AND 20k tokens — the loop fills whatever you give it, which is
why raising budget NEVER helped). Receipts:
- `SEQUENCES_IN_SEQUENCES.md` → 70k chars: clean start, then `"content state"` ×hundreds.
- `role-claude-code.md` (**3.5KB input!**) → 21k chars of `" blizzard"` — **a word not in the file** (pure
  hallucination loop). **Input size/richness does NOT predict the trap** (3.5KB looped; 70KB passed).
**The cure (evidence-picked, not theory):** vLLM **`repetition_penalty`** ladder — default **1.1** (fixed
SEQUENCES: 8.5k chars, 15s, valid, 18 good principles) → escalate once to **1.2** on `finish=length` (fixed the
blizzard file) → if still looping, **fail LOUD** as `degenerate-loop` (never silent-retry-forever). Calibration:
**`frequency_penalty` is the WRONG tool** (penalises JSON's structural tokens → under-generation, empty fields);
`repetition_penalty=1.3` too strong (degrades structure). Took the sample **79% → 98%**.
**⚠️ STILL OPEN (Tim caught it, I had not resolved):** `repetition_penalty` suppresses *repeated tokens* — so on a
file that *legitimately* enumerates many similar items (e.g. a requirements doc listing dozens of real `vi_sync_*`
functions), penalty 1.2 may **silently under-capture** the real content. **"Not failing ≠ good output."** The
unresolved check: diff a penalty-1.2 output against what's actually in the file. **Treat repetition_penalty as a
real tradeoff on enumerative content, not a solved knob.**

## Concurrency — what I ran and what broke
- Plain `ThreadPoolExecutor`, **workers=6** local (6–8 for kimi); vLLM batches server-side.
- **Concurrency was NOT my failure cause** — 2 vs 6 workers gave identical failure rates (it was the loop). BUT
  concurrent *big-context* calls stretched per-call latency toward my 200s client timeout, and that *interacted*
  with the slow loop attempts to cause batch-level timeouts that vanished on single-threaded re-run. Separate "the
  call is wrong" from "the call is slow under load."
- **Instrumentation bug to avoid:** I logged to a **global list flushed per-file** → under concurrency, calls got
  **misattributed to the wrong file** (one file showed 10 calls). Tag each call with its own id *at the call site*.
- **And I captured `finish_reason` in memory but had no DB column** → it was dropped at persist — the exact field I
  kept needing. **Persist finish_reason + status + latency + token counts + a run_id, per call, from day one.**

## VRAM (16GB) — co-loading
The 32K 4B server (gpu-util 0.80) + bge-m3 (0.30) do **not** reliably co-fit on 16GB. I had to **kill one to run
the other** (embeddings in a separate phase, then take bge down for capture). **A concurrency/embedding tool needs
VRAM-aware scheduling / eviction** — wire to the Company resource-manager (`company up --evict` etc.) rather than
hoping both fit.

## The cascade / tiers + economics
A multi-hop "query engine of a new kind": **code (free, exact) → local 4B (free, bulk map) → embeddings (structure)
→ me/Claude (reduce-reasoner over distilled output) → Kimi (256K cloud reasoner, dense/reduce) → Tim (meaning, top).**
Each pass feeds the next, with loops — single-pass small-model output is lossy; the cascade absorbs it. **Economics
that drive allocation:** local + me are FREE (lavish); cloud is abundant-but-finite (judicious, don't over-restrict);
**Tim's reasoning is the scarce thing — reserve it.** Note: **Kimi is a REASONING model** — thinking goes in a
separate `reasoning` field and `content` returns empty if you under-budget `max_tokens`; give it headroom, read
both fields, expect higher token cost; multi-turn refinement is possible.

## Embeddings — what I did + the real unlock (mostly unbuilt)
- bge-m3 vectors for ~2,036 files → **`~/wizard-run-1/embed.jsonl`** (1024-dim). Used for clustering/dedup.
- **Dedup finding:** ~21% near-duplicate (cosine>0.95); **one bug logged 288×** and dominated raw counts —
  **denoise/dedup before aggregating** or signal drowns. (Dedup via union-find on cosine>0.95.)
- **Carve:** hierarchical KMeans over the deduped reps → **44 sub-systems from 1,593 reps**. Caveat: clusters
  **bleed** (a sub-system splits across clusters) and **keyword auto-tags are unreliable** — don't trust a
  keyword-guess about a cluster's nature; let content tell it.
- **The unlock I had NOT yet built (highest value for an embedding tool):** embed the **projections separately**
  (principle-space, vocabulary-space, topic-space…), not just raw text → a file is a point in *many* spaces. Then
  **cross-level queries**: *"near in principle-space but FAR in topic-space"* finds the **face-value-inverting
  relations** (the sequences↔wizard kind) that raw similarity misses; vocabulary-space separates Tim's coined
  terms (gold) from generic/external terms (AI-fingerprint). **Multi-vector-per-item, queryable per-space,
  composable — that's the embedding capability that matters here, far more than single-vector nearest-neighbour.**

---

# PART D — The capture DESIGN as it actually stands (forms, projections, marks, large files)

## Forms — the file's *shape*, used for ROUTING
A **form** = what *kind* of thing a file is (its shape, not its meaning), decided early + cheaply by a survey pass
(the 4B answering "what shape is this?"). It **routes** capture: (a) light-vs-substance, (b) which form-specific
fields get added. **Distribution the survey found (~1,540 files):**
- `status-or-log` **535 (~35%)** · `schema-or-contract` **257 (17%)** · `prose-design` **244 (16%)** ·
  `template-or-skeleton` 96 · `checklist-or-criteria` 76 · `transcript-or-dialogue` 65 · `index-or-moc` 64 ·
  `decision-card` 49 · `math-proof` 34 · `mixed` 29 · + a long tail of one-off coined forms.
- **Key takeaway:** ~35% of the corpus (logs) + the dropped 288-noise ≈ **nearly half is process-tracking
  bookkeeping, not product substance.** Allocate effort accordingly.
**Buckets** (`forms.py::bucket()` normalises the messy survey labels into 9): `log` *(light)*, `index` *(light)*,
`schema-contract`, `decision-card`, `math-proof`, `template`, `transcript`, `checklist`, `prose-design` (default).
**Light = code metadata + one-line summary, no deep model render** (logs/indexes don't earn a full capture).
**Form-specific schema add-ons** (on top of the shared projections, for substance files):
- schema-contract → `defines · key_fields · relations` · decision-card → `decision · options · chosen · rationale`
- math-proof → `claim · result · self_contradictions` · prose-design → `mechanisms · open_questions`
- template → `templates_what · slots` · transcript → `ideas_raised · threads_open` (loose — conversations are
  exploratory) · checklist → `criteria · gates_what`

## Projections — the multi-level lenses (the main capture)
Each substance file is **rendered at many levels at once**, each separately queryable/embeddable. Tagged by
**stage** in `~/wizard-run-1/registries/projections.json` (a registry — add a projection = a row, no code change):
- **structural (code):** `format` (frontmatter keys, block kinds), `lineage` (size, mtime). **relational (code):**
  `links` (wikilink edges).
- **content (model):** `what`, `topics`, `entities_vocab` (named + *coined* terms — the coined-vs-generic
  fingerprint signal lives here).
- **meaning (model):** `principles`, `reaches`, `worldview` (the *unstated* stance — often the deepest signal).
- **epistemic (model):** `claimed_status` (decided/draft/aspirational/stub — captures the *as-if-final* problem so
  it can be discounted, not inherited), `internal_contradictions`, `completeness` (fragment/whole/meta).
- **generative (model):** `open_questions`, `decisions_needed`. **texture:** `framing`. **functional:**
  `audience_use`.
- **DEEP stage (reserved, not run in legibility):** `stated_claims` — the exhaustive enumeration (this is what
  ballooned to 178 items; kept in the registry, run only as a later *targeted* pass on files worth it).
**The render prompt is "render-not-judge"** (`registries/prompts.json`, versioned): faithfully represent what's
present at each level, don't judge importance/truth/relevance, multi-valued where there are several, `[]`/`unknown`
if absent. **No projection is privileged** — what's *done* with any of them (routing to Tim, discarding, etc.) is a
*later, looked-at* decision, never built-in.

## Forms ↔ projections coexistence (the untidy bit, flagged honestly)
Forms came first (form→bucket→form-specific fields); projections came as the reframe. They now coexist: **forms
route + add a few specific fields; projections are the broad multi-level lenses.** This is slightly redundant
(some form add-ons overlap projection fields) and **worth a future cleanup** — probably folding the form add-ons
into the projection registry as form-conditional projections. Not yet done.

## Marks — the reading layer (designed, NOT built)
An **open, multi-pass annotation layer** (`marks` table exists; passes not yet run): typed marks accrue onto
records from cheap passes — `corroboration` (semantic, cross-*session*, **positive-only**: high recurrence = gold;
**low ≠ confabulation** — rare gets *flagged for Tim*, never discounted), `ai-fingerprint` (recurring + generic =
AI-tic to subtract; recurring + idiosyncratic = gold), `idiosyncratic|generic`, and a composed **gold-likelihood
profile** (with evidence, not a black-box score). **Marks are proposed-with-evidence and Tim-confirmed — never
silent, never auto-routing.** "Capture records *what's there*; marks record *how to read it*."

## Large-file / output-volume handling (the §5f design space — documented, mostly unbuilt)
Genuinely-over-window files are a distinct class. Options (non-exclusive, the best depends on the file + resources
at the time): **(A)** raise budget + retry; **(B)** split by projection (bounded calls, recombine); **(C)** chunk
the input with overlap (downside: chunks lack full-file context); **(D)** detect-large → route to a bigger/256K
model to *reason about how to handle it*; **(E)** quality-route (small models degrade on big inputs regardless of
budget). I built a basic chunk path and currently lean on **A** for the run; the adaptive routed handler is a
documented later capability. **Do NOT arbitrarily cap to solve this** (silent loss).

---

# PART E — Harness engineering lessons (paid for in failures)
- **Resume-safe + write-as-you-go + single-writer.** First version did `process ALL → write once at end` — a crash
  lost everything and the DB showed 0 until the end. Rewrote to commit each record as it completes (single writer),
  skipping already-done items on restart. Essential for long runs; the resume let me re-attempt only the failures.
- **Never silently wipe.** My `--sample` branch did `os.remove(db)` by default — destructive; it bit me when
  overlapping runs wiped each other's data and I couldn't tell which run's output I was looking at. Make destruction
  explicit/opt-in; archive, don't delete.
- **Single source of writes under concurrency.** Workers compute; one thread writes + commits. Multiple writers on
  one SQLite file (and a global instrumentation list) caused the misattribution bug.
- **Registry-driven, not hardcoded** — lifters/projections/prompts/forms all in `~/wizard-run-1/registries/*.json`.
- **Calibrate, don't assume — and classify what a thing IS, not its "relevance."** My very first scan asked the
  model "is this relevant?" → useless near-binary (95/0). A small model is a reliable *describer*, an unreliable
  *judge*. Relevance is derived later, by meaning, never asked of the bulk model per-file.

---

# PART F — What I built, the data state, and where the docs are
**Files (all `~/wizard-run-1/`):** `db.py` (SQLite: `files, projections, links, blocks, marks, call_log, runs`;
DB at `wizard.db`) · `fleet.py` (call-layer: `local4b(json_schema=,rep_penalty=)`, `embed`, `kimi`; `map_local`/
`map_kimi`; `CALL_LOG`) · `lift.py` + `registries/markdown_lifters.json` · `forms.py` · `registries/projections.json`
· `registries/prompts.json` · `capture2.py` (current orchestrator; `run()` resume-safe; `--sample`/`--full`).
Earlier-phase: `scan.py`, `embed.py`, `cluster.py`, `dedup.py`, `extract.py`, `code_extract.py`, `form_survey.py`,
`latent_cluster.py`.
**Data state now:** DB holds a **stratified 99-file sample** — 89 substance captured, **1,355 projection rows, 383
link edges, 609 verbatim blocks** (calibration data, not the full corpus). The **full ~1,593-file Stage-1 run is
built + ready but NOT yet run** (gated on the rep-penalty open question). Last server check: **:8000 (32K 4B) UP,
:8001 (bge-m3) DOWN.**
**Docs:** full method →
`/mnt/c/Users/Workstation001/Documents/Claude/Projects/counterpart/the Company/build-prep/Discovery Methodology — Patterned Visibility (from run-1).md`
(patterned-visibility, cascade+economics, the reframe, projections + multi-level embedding + cross-level queries,
the one-registry mechanism, **§5f large-file design space**, **§5g degenerate-loop trace**, §7 operational lessons).
Staged plan → `~/wizard-run-1/BUILD_PLAN.md`. Round-by-round findings → `~/wizard-run-1/FINDINGS.md`.

---

# PART G — Known-unsolved / what I'd do differently (so you don't inherit my blind spots)
- **rep_penalty vs legitimate repetition** — UNRESOLVED (Part C). The cure may censor real enumerative content.
- **`call_log` lacks a `run_id`** — I couldn't cleanly reconstruct which attempt-sequence happened in a batch across
  runs. Add run_id from the start.
- **Forms↔projections coexistence** is untidy (Part D) — wants folding into one registry.
- **Over-window files** lean on "raise budget"; the adaptive handler (split/chunk-with-context/route-to-256K) is
  designed but unbuilt.
- **Only Stage 1 (legibility) is built + calibrated.** Stages 2–5 (embed/survey, relation-finding, marks, network
  map) are designed but unrun. The marks layer and the multi-level-embedding cross-level queries — arguably the
  highest-value parts — are still ahead.
- **I never confirmed the full run end-to-end** — 98% is the *sample*; the full corpus will surface new forms,
  bigger files, and likely new loop-triggers.

---

# PART H — The single most useful thing I can pass on
If you're building the concurrency/embedding tooling, the things I learned the hard way and would bake in from the
start: **(1)** enforced `json_schema` output (not `json_object`); **(2)** per-call instrumentation that *persists*
`finish_reason` + status + latency + tokens + run_id; **(3)** a repetition-penalty strategy **with the explicit
open caveat that it can censor legitimate repetition**; **(4)** resume-safe single-writer persistence (never
silent-wipe); **(5)** VRAM-aware server scheduling/eviction (16GB won't co-load 32K-4B + bge); **(6)** multi-vector-
per-item embeddings queryable *per projection-space* with cross-level queries (the inversion-finder), not just
single-vector NN; and above all **(7) the reflex to DUMP AND READ raw output before theorising about any failure —
"content too big" is the last hypothesis, not the first.** What to *do* with any of this is your call; this is just
what the ground actually felt like in one real run.
