# SEM-5 · The whole-corpus on-demand FACULTIES — the new CLI verbs and their value

> Companion to `SEMANTIC-LAYER-ANCHOR.md` §4②③. My allocated area: the on-demand faculties — what each
> reads, what it emits, where it slots into the real single-console CLI, the value vs the real cost, and how
> `company onboard` relates to the existing structural self-description machinery. `company onboard` is
> developed most: it is the faculty that most directly attacks the *no-humans-lose-the-thread* problem the
> whole coherence arc exists for.
>
> **Marking discipline (per the anchor):** **Observed** = directly in the code, cited `file:line`.
> **Inferred** = my reasoning from what I read, never stated as fact. **External-prior-art** = outside this
> repo. **Your-idea** = my proposal, not in the repo today. Every latency/quality claim is **Inferred** and
> labelled — I have not run a semantic sweep; I have read the benchmark sheet and the code.

---

## 0 · The headline, up front

The five faculties (anchor §4②③) are **not five new subsystems** — they are **two interactive verbs +
three bulk pre-generation passes**, all built on machinery that already exists: `run_swarm` (the swarm
driver), the `json_schema` decode branch (structured output by construction), `refresh_self_description`
(the structural self-description they *supplement*), `_critic_recheck` (the injectable gate the pre-commit
review *complements*), and `up_translate('finding')` (the half-built RHM organ the enrichment passes
*feed*). The honest shape:

| Faculty (anchor) | Shape | Slots as | Interactive? |
|---|---|---|---|
| `company onboard` | **interactive verb** — top-level | `if cmd=="onboard"` (peer of `suites`) | yes (whole-repo read; ~the slow end) |
| Repo-wide semantic QA | **interactive verb** — top-level or `coherence ask` | `if cmd=="ask"` / `coherence` subcmd | yes (reads a *slice*, fast) |
| Pre-commit semantic review | **verb + injectable critic** (two invocations) | `if cmd=="review"` AND `_critic_recheck` critic= | yes (reads a *diff*, fastest) |
| Auto-explain-every-finding | **bulk enrichment pass**, not an interactive verb | `coherence scan --semantic --enrich` phase | no — pre-generates, populates the model |
| Candidate-disposition-for-all | **bulk enrichment pass**, not an interactive verb | same enrich phase | no — pre-generates, populates the model |

**Inferred (corrected from the anchor):** §4② "auto-explain" and "candidate-disposition" are **not naturally
top-level verbs**. They are bulk passes that fan the swarm across *all current findings* and write the
enriched fields into the finding model so the `CoherenceView` opens fully-populated with no per-click
latency. They belong as a `--enrich` phase of the semantic scan, not as their own `company` verb. Forcing
them into the verb mould would misrepresent what they are. (The anchor groups them under "ENRICHMENT" and is
right to — I'm only naming that they don't become CLI verbs.)

So the deliverable below treats them in two tiers: **the interactive verbs** (onboard, QA, review — a human
or a Claude Code session types these and waits for an answer) and **the bulk enrichment passes** (run inside
a scan, no human waiting on a single answer).

---

## 1 · The real CLI structure these slot into (Observed)

`ops/cli/app.py` is a **flat `if cmd == ...` dispatch chain** in `main()` (app.py:120-213). Every verb is
one branch; there is no framework, no subcommand router, no plugin registry — stdlib-only, by design
(app.py:6 *"stdlib-only"*; the module docstring lists every verb, app.py:8-26). Adding a faculty is
**literally one `if` branch + one line in the docstring's help list**. This is the path-of-least-resistance
shape: the correct way to add a verb is the only obvious way.

**The precedent to copy is `company suites` (Observed, app.py:133-149).** It is the exact template for
"a verb that shells a heavy job under a temporary store":

```python
if cmd == "suites":
    import os as _os, subprocess as _sp, tempfile as _tf
    repo = _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))   # ../../.. → repo root
    venv_py = _os.path.join(repo, ".venv", "bin", "python")
    py = venv_py if _os.path.exists(venv_py) else sys.executable
    gate = _os.path.join(repo, "tests", "suite_health_acceptance.py")
    if not _os.path.exists(gate):
        sys.exit(f"  ✗ the all-green gate is missing: {gate}")
    env = dict(_os.environ, COMPANY_STORE=_tf.mkdtemp(prefix="company-suites-"))   # TEMP store — never touches live data
    print("running the all-green gate … This takes a few minutes…\n")
    sys.exit(_sp.run([py, gate], cwd=repo, env=env).returncode)                    # shells the heavy job, propagates exit
```

Four properties of this precedent that every semantic faculty inherits (Observed):
1. **It shells out** (`subprocess.run`) — no logic duplicated into the CLI; the CLI is a thin face over a
   heavy job. *Inferred:* the semantic verbs shell a small driver that calls `run_swarm` the same way the
   suites verb shells `suite_health_acceptance.py`.
2. **It uses a TEMP store** (`COMPANY_STORE=mkdtemp(...)`) so the heavy job "never touches the live data."
   *Inferred:* a semantic read is even safer — it's read-only over the repo and emits a transient artifact;
   onboard/QA need no store at all, only the read; the *enrichment* passes write to the coherence finding
   model (the one store they do touch).
3. **It is honestly slow and says so** (`"This takes a few minutes…"`). The semantic faculties claim the
   *opposite* latency profile (interactive-fast) — see §6, the load-bearing contrast.
4. **It propagates the exit code** — a real red is named, non-zero exits. *Inferred:* `company review`
   should exit non-zero when it finds a hard law-violation, so a pre-commit hook can gate on it.

**Verb hierarchy decision (Your-idea):** `onboard` and `ask` read top-level (`company onboard`,
`company ask "…"`) — they are first-orientation acts a session reaches for, like `status`. The detector +
enrichment faculties live under `company coherence` (the structural round's planned face, COHERENCE-SUBSTRATE
§6 / §8.5) as `company coherence scan --semantic [--enrich]`. `review` is top-level (`company review`) so a
git hook can call it by one name. This keeps the top level for *acts a human/session types* and nests the
*model-maintenance* passes under the coherence face that owns the finding model.

> **Observed:** there is **no** `onboard`, `ask`, `review`, or `coherence` verb in `app.py` today (the full
> branch list is app.py:125-213: help/status/gpu/health/suites/models/telemetry/combos/config/swap/bench/
> up/down/restart/logs). So **every verb below is Your-idea** — a proposed branch, not an existing one. The
> *machinery they shell* is Observed.

---

## 2 · `company onboard` — regenerate true institutional memory on demand (developed most)

This is the faculty that most directly attacks the problem the whole no-humans premise rests on. I'll build
it fully: the problem, the relationship to the existing structural self-description, the writes-vs-emits
design call, inputs/outputs, where it slots, value, cost, and the honest tensions.

### 2.1 · The problem it attacks (Observed, in the substrate doc + memory)

The no-humans rule (anchor line 16-17): *no human review holds the picture together across sessions.* The
substrate doc names three **live incidents from this very build** where a Claude Code session lost coherence
with what other sessions did (COHERENCE-SUBSTRATE §3.5, lines ~182-187, Observed):

- **main drifted under the lead** — "HEAD advanced to commits the lead didn't recognise; a worktree's
  studio-landing was committed by a continuation the lead had lost the thread of."
- **the mode dial got built twice** — two sessions independently built two halves of one mode declaration.
- **the lead wrongly deleted `/status`** — unable to see it was a half-migration.

Every one is *a session starting without a true picture of what other sessions did* — starting blind, or
re-discovering state by grep, and getting it wrong. That is the institutional-memory gap a human team fills
by a person who "remembers." `company onboard` is **the institutional-memory-that-replaces-the-developer,
generated fresh in seconds each time** (anchor line 235-236).

### 2.2 · The relationship to the EXISTING self-description machinery — this is the crux

The system **already maintains a structural self-description**, and onboard is its *semantic supplement*, not
its replacement. The seam is exact and sits in two functions:

**`Suite.refresh_self_description()` (Observed, suite.py:823-839)** regenerates the **factual blocks** of the
orientation files from the system itself, on every apply:
- `MAP.md` REGISTRY block ← `capabilities()`: node-types, RHM verbs, modes, panels, models (suite.py:829-835).
- `STATE.md` SUITES block ← `_acceptance_suites()`: the suite index (suite.py:836-839).
- The docstring is explicit about the split (suite.py:826-827, Observed): *"The PROSE is integration-
  maintained; doc_drift fails loud if anything falls behind."*

**`Suite.doc_drift()` (Observed, suite.py:855-869)** is the enforcement — but read *what it actually checks*:
it checks that each capability **name is reflected** in the maintained block (`t.lower() not in reg`, a
substring presence test, suite.py:864-868). The root AGENTS.md confirms the boundary (Observed, AGENTS.md:48):
*"the factual blocks … regenerate themselves … the prose … you update by integration."* And
`tests/drift_acceptance.py` *"fails loud if a registered capability or an acceptance suite isn't reflected."*

> **The seam, stated precisely (Observed → Inferred):** `refresh_self_description` regenerates the factual
> *registry/suite* blocks; `doc_drift` only checks a *name is present*. **Neither asks whether the prose is
> true.** The prose — STATE.md's "what's built / what can't be done yet," a module's constitution — is the
> institutional memory, and **it goes quietly false the moment meaning drifts while names hold** (the anchor's
> intent-vs-implementation-drift class, anchor lines 36-39). `doc_drift` would still pass: the name is still
> there. *That gap — true-prose orientation — is exactly where `onboard` lives.*

So the relationship is: **structural self-description = the skeleton (names, registry, suite list,
auto-maintained, name-checked). `company onboard` = the semantic flesh (a fresh, true, prose orientation
read of what the system actually is right now, generated by the swarm reading everything).** Build-on-not-
beside: onboard does not duplicate `refresh_self_description`; it *starts from its factual blocks* (the
registry/suite index are the trustworthy skeleton it hangs meaning on) and adds the meaning-layer
`refresh_self_description` constitutionally cannot produce.

### 2.3 · The genuine design call: does onboard WRITE the prose, or EMIT a transient read? (the meat)

This is the consequential question and it is **decidable by the substrate's own law.** Two options:

- **Option A — onboard WRITES the prose** back into STATE.md / AGENTS.md (owns/maintains the orientation).
- **Option B — onboard EMITS a fresh transient orientation** each session, keeps nothing.

**Decision (Your-idea, grounded in the substrate's own/reflect split): Option B — emit, don't own.** The
reason is the coherence substrate's load-bearing insight (COHERENCE-SUBSTRATE §2, Observed): *detection is
re-derivable → reflected, never owned; only disposition is owned.* A semantic orientation read is **pure
detection** — re-run the swarm, get the orientation again; there is no human decision in it that a re-run
can't recompute. So by the substrate's own discipline it **must be reflected, never owned** — generated
fresh, kept nothing. This also dodges a real hazard of Option A: if onboard *wrote* prose, a 4B's
imperfect read would *overwrite* the human-integration-maintained prose with possibly-wrong text — turning
the institutional memory *less* true, the cry-wolf failure made permanent. Emit-not-own keeps the 4B's
output as a *consultable transient*, never a committed source-of-truth.

> **Inferred consequence:** onboard's output is to **stdout / a transient file a starting session reads**,
> not a commit. It is regenerated every session because regeneration is cheap and the alternative (a stale
> committed map) is the exact drift it's curing. This is "institutional-memory-as-substrate" as a *faculty*,
> not a *file*: the memory is the *ability to regenerate the true map on demand*, not a document that rots.

**Where the OWNED part lives:** the *dispositions* — "this orphan is by-design because X" — stay in the
coherence finding model's disposition lane (the micro-ADR records, COHERENCE-SUBSTRATE §2). Onboard *reads*
those (they're the un-recomputable human decisions) and folds them into the orientation: "these 3 things look
unwired but are dispositioned by-design, here's why." So onboard = **fresh semantic detection (reflected) ⨝
the owned disposition history (the institutional ADR log)** — the full own/reflect split, in one read.

### 2.4 · Inputs / outputs / where it slots

**Reads (Observed targets that exist):**
- The factual self-description skeleton: `MAP.md` REGISTRY block + `STATE.md` SUITES block (suite.py:829-839)
  — the trustworthy names to hang meaning on.
- The prose: STATE.md "what's built / what can't be done yet," root + per-module `AGENTS.md` constitutions
  (the implement.py walk already enumerates these: `SELF_DESCRIPTION_FILES = ("AGENTS.md","MAP.md","STATE.md")`
  at implement.py:140, and the per-module AGENTS.md ancestor-walk at implement.py:238-268 — Observed; that
  walk is *reusable* as onboard's "which constitutions govern what" map).
- Recent commits / the event log (`store.recent_events`, suite.py:896 pattern) — what changed lately, the
  raw material for "main moved under you since your last session."
- The coherence finding model's open findings + dispositions (the substrate the structural round builds).
- The core source tree — ~20K LOC across `runtime/ contracts/ ops/ nodes/ roles/ fabric/ store/` (measured,
  §6) — read in bounded chunks (a module + its AGENTS.md is the natural unit, anchor §6.2).

**Emits (Your-idea):** a fresh **orientation artifact** at Tim's altitude AND a session's altitude — a
plain-language LEAD ("here is what this system is right now, what moved since, what's half-built, what other
sessions touched") + a drillable MECHANISM (the registry skeleton + per-area true prose + the by-design
dispositions). *This is the exact two-part shape `up_translate` already produces* (a "plain-language LEAD + a
drillable MECHANISM," Observed, suite.py:5836-5837) — onboard is `up_translate` pointed at *the whole system*
instead of one artifact. Build-on-not-beside again.

**Slots as (Your-idea):** a top-level `if cmd == "onboard":` branch in `app.py`, peer of `suites`,
shelling a driver that fans `run_swarm` across the bounded read-units and composes the orientation. One
branch + one help line (app.py:8-26 docstring).

### 2.5 · Value (high) vs cost (the honest, measured part)

**Value (Inferred, high):** this is the faculty that fires on **every session start** — the highest-frequency
consumer of the semantic layer, and the one whose absence caused the three named incidents. A session that
runs `company onboard` first starts *oriented* (true picture, knows what moved, sees the by-design
dispositions) rather than *blind* (re-discovering by grep, the failure mode that deleted `/status`). It is
the most direct answer to "in fully-AI development nobody holds the whole" (COHERENCE-SUBSTRATE §10).

**Cost (Inferred from real measured numbers — §6 has the full math):** onboard reads *everything*, so it is
the **most expensive** faculty. Whole-corpus ≈ ~800K tokens of input (≈200K code + ≈600K md). At the
benchmark's measured 32-concurrency and its **sublinear prefill** (30K input prefilled in ~1.07s, Observed,
BENCHMARK_FACTSHEET.md:13,45-53), chunked into ~30 reads fanned across 32 slots, this is **order-of-magnitude
seconds-to-low-minutes, not "seconds"** as the anchor says (anchor line 56-57). The anchor's "whole repo in
seconds" is right for a *slice* (QA, review), optimistic for *onboard* (whole corpus). Still: a one-minute
orientation that prevents a `/status`-class deletion is overwhelmingly worth it — and it's *on-demand at
session start*, not per-tick, so the cost is paid once where it matters most.

---

## 3 · Repo-wide semantic QA — `company ask "…"`

**What it answers (anchor line 141-142):** "where does X actually happen / what would break if I change Y /
where is the consent floor enforced" — from the whole corpus, in seconds.

**Reads:** a *slice* of the repo relevant to the question — found by first narrowing (grep/registry/the
structural reachability catalogue) then fanning the swarm to *read and judge* the candidate files. Inputs are
the question + the candidate read-units.

**Emits:** a plain-language answer + the `code://`/`ui://` addresses it's grounded in (so the session can
click straight to the element — the addresses are real, anchor §7 / COHERENCE-SUBSTRATE §7).

**Slots as (Your-idea):** `if cmd == "ask":` top-level, or `company coherence ask`. Shells a driver: narrow →
fan `run_swarm` over the slice → compose. The "where is the consent floor enforced" example is a real,
answerable one *today* — the answer is `resolve_surfaced` is operator-only, off the agent face
(COHERENCE-SUBSTRATE §5, Observed) — which is exactly the kind of cross-cutting truth a session needs and
can't grep.

**Value (Inferred, high day-to-day):** this is the faculty a session reaches for *mid-work*, repeatedly. It
substitutes a fresh whole-relevant-slice semantic read for the grep-and-guess that produced the build's
errors. It also directly feeds the RHM (anchor line 230): when Tim asks the right-hand-man about an element,
the answer is grounded in a fresh semantic read, not just the structural registry.

**Cost (Inferred, low):** reads a *slice*, not everything. With sublinear prefill (30K in ~1.07s), a typical
QA over a few-dozen-file slice is **genuinely seconds** — the anchor's claim holds here. This is the cheapest,
highest-frequency interactive verb. (Trust caveat: a 4B answer is candidate-quality — §7.)

---

## 4 · Pre-commit semantic review — `company review` AND an injectable critic

This is the most architecturally interesting one, because it is **the same faculty in two invocations** —
mirroring exactly how COHERENCE-SUBSTRATE §3.5 frames the loop ("one agent, two invocations").

### 4.1 · What it does + its relationship to the existing adversarial critic (Observed)

The anchor (line 143-146) asks: before a commit lands, judge "does this diff match its stated intent, does it
touch things it shouldn't, does it violate any AGENTS.md law?" — and notes the relationship to *"the wire's
existing adversarial critic — this is the bulk/semantic complement."*

The wire's critic is real and I read it (Observed):
- `_critic_recheck` (suite.py:7302-7310) is *"an ADVERSARIAL re-check, SEPARATE from the builder's
  self-report,"* and crucially **`INJECTABLE`** (suite.py:7308: *"INJECTABLE so a stronger critic (or a test)
  can supply its own verdict"*).
- The **default critic is purely structural / deterministic** (`_default_critic`, suite.py:7312-7321): it
  only checks `result["success"]` is truthy and `result["changed_files"]` is non-empty — *"a 'success' with
  no change-set is not an implementation."* It has **no idea what the diff means.**
- It runs inside `_wire_verify` (suite.py:7323-7358) as one fail-loud gate alongside the affected acceptance
  suites + drift.

> **The complement, stated precisely (Observed → Your-idea):** the existing critic proves the diff is
> *consequential* (success + non-empty). It is **blind to whether the diff matches its intent or obeys the
> laws.** The semantic review is the **meaning half** of the same adversary — and because `_critic_recheck`
> is *already injectable*, the semantic reviewer **slots straight in** as the `critic=` argument
> (suite.py:7309 `run = critic or self._default_critic`). No new gate; the existing seam was built for
> exactly this. This is the cleanest build-on-not-beside point in my whole area.

So: **two invocations of one faculty** —
1. `company review` (Your-idea verb) — a human/session runs it on a staged diff before committing; a git
   pre-commit hook can shell it and gate on the exit code.
2. The **injected wire critic** — the wire's autonomous loop passes the semantic reviewer as `critic=` so
   every auto-build is meaning-checked, not just consequential-checked, before it can close.

### 4.2 · Which laws can a 4B actually check? (the honest tiering the anchor §6.5 demands)

The diff is judged against the 10 non-negotiable rules (Observed, AGENTS.md:20-30). **Inferred tiering — the
semantic analog of the structural Tier-1/2/3 split:**

- **Grep already catches these — do NOT spend the 4B on them:** rule 5 (storage on ext4, not `/mnt/c` — a
  path string test), rule 6 (NO Gemini — a string test), rule 10 (commit to main, no feature branches — a
  git state test). These are mechanically exact; a 4B adds only false-positive risk.
- **4B is genuinely good for these (consistency/naming/match — the anchor's likely-yes class, line 200):**
  rule 3 (One source — "is this a duplicate definition of something that already exists?" = the built-twice
  detector, the mode-dial class), rule 4 (Fail loud — "does this add a silent fallback / a bare except / a
  no-op masquerading as success?"), rule 8 (Author from the registry — "does this invent a model/node-type
  name not in `capabilities()`?"), and the headline **intent-vs-implementation match** ("does this diff do
  what its commit message / the intent it was dispatched for says?").
- **4B is NOT reliable for these (the likely-no class, anchor line 201):** rule 1 (build against the
  contracts — needs deep dataflow), rule 2 (schema-additive not schema-breaking — needs real schema
  diffing, a structural job), rule 9's FORM half (a design-critic agent's job, suite.py:7217-7299 — separate
  machinery). Surface as candidate; never block on a 4B's verdict here.

### 4.3 · The honest tension: a blocking critic collides with positive-only

Here is the hard part my area must not paper over. The anchor's discipline is **positive-only / never
auto-act** (anchor lines 88-91): a semantic finding may *propose*, never *declare*. But a critic that returns
`(False, reason)` **blocks the close** (suite.py:7347-7349: `if not ok: return False, why`) — that is
**auto-acting on a 4B judgment.** The two collide.

**Resolution (Your-idea, the honest line):** the semantic critic may **hard-block only on the
mechanically-confirmable laws** (which the 4B *flags* but a deterministic check *confirms* before the block —
e.g. the 4B says "this looks like a Gemini reference," the block fires only after a string-confirm; the 4B
says "this looks like a duplicate," the block fires only after the structural one-source detector confirms a
real duplicate symbol). For the **fuzzy laws** (intent-match, fail-loud-smell), the critic **does not block**
— it attaches its concerns as *candidate findings surfaced for review* (the same surfacing the wire already
does, AGENTS.md:29 *"surfaced for review … never a silent terminal"*), which a stronger judge (a Claude Code
agent) or Tim confirms. So:

> **Pre-commit semantic review = a hard gate ONLY where a deterministic check seconds the 4B's flag;
> elsewhere a candidate-surfacer, never a blocker.** This honors positive-only (no fuzzy 4B verdict
> auto-acts) while still being useful (it routes attention). The line is: *the 4B never blocks alone; a
> structural confirm or a stronger judge blocks; the 4B proposes.*

**Cost (Inferred, lowest):** reads only the *diff* + the touched files' AGENTS.md + the intent text — the
smallest read-unit of the three interactive verbs. **Genuinely sub-second-to-seconds** even pre-commit. This
is the cheapest place to put a semantic check, which is why putting it *in front of* the structural gates
(anchor line 145) is the right economics.

---

## 5 · The two bulk ENRICHMENT passes (§4②) — not verbs, scan phases

These populate the coherence finding model so the `CoherenceView` opens fully-populated. They feed the
**already-half-built** RHM organ.

### 5.1 · Auto-explain every finding at Tim's altitude

**Reads:** every open finding in the coherence model + the element each rides (its `code://`/`ui://`
address). **Emits:** for *each* finding, the pre-generated plain-language "what is this gap, what would
finishing it mean, what depends on it" — written into the finding's enriched field.

**Feeds (Observed):** this is **literally what `up_translate('finding')` is for.** Area 5 found it
half-coded at suite.py:5828 with a comment that it's "the shape G2 will feed — NOT wired here, that's a later
lane" (COHERENCE-SUBSTRATE §1.3). I confirmed the surrounding F1 organ (suite.py:5834-5840, Observed): it's
*"the GENERALIZED up-translate move … callable on ANY system artifact — an address, a surfaced decision, a
drift/coherence finding, an event — returning its Tim-altitude framing (a plain-language LEAD + a drillable
MECHANISM)."* The enrichment pass is **the swarm doing this in bulk, ahead of time** — so the per-click
big-model `up_translate` cost is replaced by a cheap pre-generated field. The half-built organ is the
single-finding shape; this is the same shape fanned across all findings.

**Slots as (Your-idea):** a `--enrich` phase of `company coherence scan --semantic`, NOT a verb. No human
waits on one answer; it's a model-maintenance pass.

### 5.2 · Candidate disposition + reason for every finding

**Reads:** every open finding + its context. **Emits:** for *each*, a *candidate* disposition + reason —
"this looks by-design (internal entry point)" / "this looks like a real to-wire (an FE caller is missing),
because…" — written as a **candidate** (positive-only; never the owned disposition). The owned disposition
stays the human/agent's confirm (COHERENCE-SUBSTRATE §2). This burns down the dispositioning labour that
otherwise falls on Tim, *as a proposal he confirms by sight*, not a decision the 4B makes.

**Grounds in (Observed):** the `_ORPHAN_ROUTES` tags (`to_wire`/`to_build_ui`/`voice_owned`/`backend_only`,
COHERENCE-SUBSTRATE §1.2 / §2) are the disposition vocabulary the candidate-disposer proposes into — it's the
existing `(tag, reason)` one-line-ADR shape, pre-filled as a candidate.

**Slots as:** same `--enrich` phase. **Cost (Inferred):** these two run over *N current findings* (tens to
low-hundreds), one bounded read per finding, fanned 32-wide — **a minute, on demand, inside a scan.** Not
per-tick; not in front of a human.

---

## 6 · The cost / latency reckoning (the measured part — anchor line 56-57 checked)

The anchor's capability claim is **"~32 concurrent inferences at ~3000 tok/s … the entire repo and all
documentation read in seconds, or at most a minute or two."** I checked it against the real benchmark sheet
and the real repo size.

**Measured throughput (Observed, `~/vllm-tests/BENCHMARK_FACTSHEET.md`):**
- Model: `Qwen3.5-4B-AWQ-4bit`, vLLM 0.21.0, prefix caching ON (line 4-5).
- Best throughput: **concurrency 32, 4K ctx → 2,250 tok/s aggregate, ~150ms TTFT** (line 11). *Not 3000* —
  the anchor's 3000 is **optimistic by ~33%.** Aggregate tok/s **plateaus at concurrency 32** (line 30).
- Max safe concurrency 64 (TTFT 250-500ms); never exceed 128 (line 14-15,30).
- **The decisive number for whole-repo reads — sublinear prefill: 30K input tokens prefilled in ~1.07s**
  (line 13,45-53), *"actually gets more efficient per-token as the input grows … the model's biggest win for
  RAG / document-QA workloads."* Decode is steady ~100 tok/s per request (line 64).

**Measured repo size (Observed, `find` over `~/company`):**
- Hand-written **core source ≈ 20,229 LOC** (`runtime/ contracts/ ops/ nodes/ roles/ fabric/ store/`).
  *(Note: a naive `*.py` LOC count returns ~5M — that is vendored deps; the real core is ~20K.)*
- **530 markdown files ≈ 59,347 lines** (the docs corpus the doc-sweep + onboard read).

**The math (Inferred, order-of-magnitude):**
- Whole-corpus read ≈ ~200K tokens code + ~600K tokens md ≈ **~800K input tokens** for `onboard`'s
  everything-read.
- The cost is **prefill-dominated** (the swarm *reads* large inputs and *emits* short schema-constrained JSON
  — `max_tokens=256` default, cognition.py:527). With sublinear prefill (~30K/1.07s) and 32-wide fan-out,
  ~800K input ≈ ~27 chunks of ~30K, fanned 32-wide = essentially **one-to-a-few prefill waves**:
  **single-digit-to-low-tens of seconds for the reads, plus the short decodes** — call it **~30s to ~2min for
  full onboard.** The anchor's "a minute or two" is right *for onboard*; its "seconds" undersells onboard and
  correctly describes QA/review (slice/diff reads, genuinely seconds).

**The load-bearing latency CONTRAST (Inferred — ties back to §1):** `company suites` shells a heavy job and
is *fine being slow* — it's a pre-merge gate, it says "this takes a few minutes." The semantic faculties
claim the **opposite profile: interactive-fast.** That contrast is the whole value: it is the sublinear
prefill + 32-wide fan that makes "read the relevant corpus and judge it" **affordable to run interactively /
on-demand / pre-commit** rather than as a slow batch gate. **"Free" is honest only with three caveats:**
1. It is **prefill-cheap, not free** — measured 2,250 tok/s aggregate, not infinite.
2. It **contends for the same VRAM** the live cognition + chat use (the 4B is the *resident* cognition model,
   anchor §6.4 / §7). A whole-repo sweep mid-conversation competes for the card. The resource manager
   (`ops/cli/gpu.py`, `services.json`, `company up/down/swap`, Observed via app.py:36) governs this — *Inferred:*
   the right cadence is **on-demand only** (a human/session typed it) so the operator chose to spend the VRAM,
   *not* a background tick that silently starves the live stream. (The "continuous background watch" of anchor
   §8 is the tempting-but-dangerous variant — it's where the contention bites.)
3. The 32-concurrency budget is **shared with the live swarm** — `SlotBudget` reserves R slots so a live
   main-stream call never queues behind the swarm (cognition.py:547-553, Observed: *"R permits ALWAYS remain
   free for a concurrent main-stream/judge call"*). A semantic sweep is *another swarm* on the same budget —
   *Inferred:* it must respect the same reserve, or it starves live cognition. The mechanism to honor it
   already exists; the sweep must pass the same `SlotBudget`.

---

## 7 · The trust floor every faculty rides on (the make-or-break, anchor §6.1)

None of these faculties is worth anything if the 4B's output is noise that trains Tim to ignore it. The
machinery for the trust floor **already exists** (Observed):
- **Schema-enforced JSON** — `run_role` passes `schema=role.output_schema, json=True` (cognition.py:115-118);
  the transport's `json_schema` branch (anchor §5/§7) means a finding is a *typed record by construction*,
  not an essay to parse. So the 4B is constrained to a *finding schema*, never asked to free-write.
- **Determinism** — `run_role` defaults `temperature=0.0` (cognition.py:95) for routing-stable output, so
  identical inputs → identical judgment (the reproducibility the substrate's trust rests on, anchor §6.6).
- **The jury** — `run_jury` (cognition.py:637) runs N varied draws → a deterministic `verdict_rule` (quorum/
  vote, a pure function, no model call, cognition.py:646-647). Multi-role agreement is the calibration
  mechanism for a consequential semantic flag. *Documented limit (Observed, cognition.py:649-651):* N draws on
  ONE model are **correlated** — variance, not independent error; the verdict_rule shape *"accepts a future
  2nd-model/cloud tiebreak."* So jury raises confidence but is not a substitute for a stronger judge on the
  consequential ones.
- **The positive-only backstop** — across every faculty: the 4B *proposes*; a structural confirm or a Claude
  Code agent or Tim *confirms* before anything acts. onboard emits (owns nothing); QA answers (acts on
  nothing); review blocks only where deterministic; the enrichment passes write *candidate* fields. **No
  faculty lets a 4B verdict auto-act.** That is the discipline that makes a half-understanding-code 4B safe
  to point at the repo.

---

## 8 · Summary table — each faculty as a concrete verb

| Faculty | Verb (Your-idea) | Reads | Emits | Slots (Observed seam) | Value | Cost (Inferred) |
|---|---|---|---|---|---|---|
| **onboard** | `company onboard` | factual skeleton (suite.py:823-839) + prose + AGENTS walk (implement.py:238-268) + commits + dispositions + core src | transient true orientation (up_translate shape, suite.py:5836); **emit-not-own** | `if cmd=="onboard"` peer of suites (app.py:133) | **highest** — every session start; cures the 3 named drift incidents | ~30s–2min (whole-corpus ~800K tok; prefill-dominated) |
| **semantic QA** | `company ask "…"` | a narrowed *slice* | answer + grounding addresses | `if cmd=="ask"` / `coherence ask` | **high** — mid-work grep-replacement; feeds RHM | seconds (slice; sublinear prefill) |
| **pre-commit review** | `company review` **+** injected `critic=` | the *diff* + touched AGENTS.md + intent | hard-block on deterministic-confirmable laws; candidate-surface the fuzzy ones | `if cmd=="review"` **AND** `_critic_recheck` critic= (suite.py:7308-7309) | **high** — meaning-half of the existing structural critic | sub-second–seconds (smallest read) |
| **auto-explain findings** | `coherence scan --semantic --enrich` (phase, not verb) | all open findings + their elements | pre-generated altitude framing per finding (feeds half-built up_translate('finding'), suite.py:5828) | scan phase | populates CoherenceView, kills per-click latency | ~1min over N findings, on demand |
| **candidate-disposition** | same `--enrich` phase | all open findings | candidate disposition+reason (into `_ORPHAN_ROUTES` tag shape) — never owned | scan phase | burns down Tim's dispositioning labour as confirm-by-sight | ~1min over N findings |

---

## 9 · The honest "but actually" list (where I corrected/sharpened the anchor)

- **"~32 concurrent at ~3000 tok/s"** → *actually* measured **2,250 tok/s aggregate at concurrency 32**
  (BENCHMARK_FACTSHEET.md:11) — the throughput claim is ~33% optimistic; but the **sublinear prefill (30K/
  1.07s)** is the real unlock and the anchor underweights it.
- **"whole repo in seconds"** → *actually* **seconds for a slice (QA/review), ~30s–2min for onboard's
  whole-corpus read** (~800K real tokens). The anchor's "or at most a minute or two" is the accurate half.
- **§4② auto-explain + candidate-disposition are faculties** → *actually* they are **bulk enrichment passes,
  not interactive CLI verbs** — they belong as a `--enrich` scan phase, and they feed the *already-half-built*
  `up_translate('finding')` organ (suite.py:5828), not a new top-level command.
- **"pre-commit review judges and gates"** → *actually* a blocking 4B verdict **collides with positive-only**;
  the honest design is **hard-block only where a deterministic check seconds the flag, candidate-surface the
  fuzzy laws** — and it slots into the *already-injectable* `_critic_recheck` (suite.py:7308), so it's the
  existing critic's meaning-half, not a new gate.
- **"`company onboard` regenerates institutional memory"** → *actually* the system **already** auto-maintains
  a *structural* self-description (`refresh_self_description`, suite.py:823); **onboard is its semantic
  supplement** — it fills the gap `doc_drift` can't (suite.py:855-868 checks a *name is present*, never that
  the *prose is true*) — and by the substrate's own/reflect law it must **emit, not own** (re-derivable
  detection is reflected; only dispositions are owned).
- **"free in seconds"** → *actually* **prefill-cheap, not free**: it contends for the resident 4B's VRAM and
  the shared 32-slot `SlotBudget` (cognition.py:547-553) the live cognition stream needs — so the honest
  cadence is **on-demand, respecting the reserve**, not a background tick that starves the live stream.

---

*Left bigger and more real than I found it: the five §4②③ items are now two interactive verbs + one
verb-and-injectable-critic + two scan-phase enrichment passes, each grounded in the exact existing seam it
rides (`if cmd==…` in app.py:133 · `refresh_self_description`/`doc_drift` in suite.py:823-868 · the injectable
`_critic_recheck` at suite.py:7308 · the half-built `up_translate('finding')` at suite.py:5828), with the
"free in seconds" claim converted to measured numbers (2,250 tok/s @ 32, sublinear prefill, ~800K-token
whole-corpus onboard ≈ 30s–2min) and the positive-only trust floor + VRAM-contention caveat made explicit.*
