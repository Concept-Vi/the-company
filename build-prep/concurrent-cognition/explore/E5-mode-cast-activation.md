---
type: exploration
module: build-prep/concurrent-cognition/explore
aliases: ["E5 — Mode Casts × Activation Contexts", "Concurrent Cognition E5"]
tags: [company, design, concurrent-cognition, roles, modes, activation-contexts, thought-shapes, exploration]
status: generative-draft
relates-to:
  - "[[Concurrent Cognition — Completion Criteria]]"
  - "[[Concurrent Cognition — Implementation Guide]]"
  - "[[DECISIONS]]"
  - "[[01-role-registry]]"
  - "[[04-staged-response-queue]]"
---

# E5 — The full realization of mode-as-the-dial: role-casts, thought-shapes, and the four activation-contexts

**What this is.** A *generative* exploration (not a build spec, not a locked decision) of what Tim's settled
"mode = the dial" decision **fully unlocks** once you stop treating the dial as a single per-turn knob and
start treating it as the selector over a **{mode × activation-context} matrix**. The `listening` cast is the
only one designed (DECISIONS Batch-4 Q1: `focus · recall · ground · connect · check · voice`). This doc
designs the **other modes' casts**, the **per-mode grain / slot-budget / brain-config**, the **three
non-per-turn activation-contexts** concretely, and a starter **THOUGHT-SHAPES library** — then surfaces the
cross-mode patterns and what the dial unlocks.

> [!important] Epistemic status
> Everything here is **Inferred design** — a proposal for Tim to react to (keep / cut / add / rename), in
> the same spirit as the `listening` cast was proposed and then locked. It builds ON the locked decisions
> (L1/L2/L3, Batches 1–5) and the file:line-anchored reuse map in `01`/`04`; it does not relitigate them.
> Where a face-value reading of a locked constraint forces a call (e.g. text-only's per-turn cast), I make
> the call explicitly and flag it as a Tim-decision, never silently.

---

## 0. The reframe that makes the whole doc coherent

The locked budget table (`04:266-270`) and `shape_for(mode)` (`04:149`) say plainly:
**`focus · background · text-only · watch-and-react · decide-for-me` → the `direct` shape → they do NOT
stage** (focus is `max_concurrent_roles: 0`). So you **cannot** write a per-turn *multi-part* cast for those
modes without contradicting a settled decision. That is the trap, and the resolution is the second half of
the task — the activation-contexts decision (R4 / G5):

> **A mode's cast is not one per-turn list. It is a {mode × activation-context} matrix.**
> For the staging modes (`listening`, `walkthrough`) the cast's centre of gravity is **per-turn parts**.
> For the non-staging modes the cast's centre of gravity moves into **background · sense · rollup** —
> their "concurrent thoughts" happen *between* turns, on *sensed events*, on *a schedule*, not as extra
> reply-parts. This is why the task pairs "casts for the other modes" with "design the three non-per-turn
> contexts": **for most modes they are the same design.**

**One precision that keeps the per-turn question alive for every mode:**

> `direct` means **one PART**, not **zero ROLES**.

A direct-shape mode can still fire a small per-turn cast whose outputs **inject into that single part's
context** (the `run://<turn>/<role>` ref-read branch, C4.2) — and, in `decide-for-me`, **trigger governed
actions** (C9.1). It just never spawns *additional parts*. So the per-turn axis is a gradient:

```
  per-turn role richness  (parts AND/OR injected enrichers)
  off ── focus ── watch ── text-only ── background ── decide-for-me ── listening ── walkthrough
   0      ~0       ~1        1-2          1-2            2-3 + act       6            6-8
  (parts:1 for all the left of listening; listening/walkthrough spawn parts)
```

This single gradient is the first cross-mode pattern: **the dial is a continuous attention-spend, and the
"staging" cliff is just the point on the gradient where spend buys *extra parts* rather than *a richer
single part*.**

---

## 1. The matrix (the spine of the whole doc)

Every mode gets a row; every activation-context gets a cell. A cell answers: *does this {mode × context}
fire cognition, and if so what does it do?* Fill once, read everywhere — exactly the `MODE_DIRECTIVES`
discipline (`suite.py:1046`), now two-dimensional.

| mode | shape (per-turn) | grain | slot budget (R reserved · swarm cap) | brain-config | per-turn cast | background | sense | rollup |
|---|---|---|---|---|---|---|---|---|
| **listening** | `ack_retrieve_synth_offer` (stages) | beat | floor R≈4 · swarm≤6 | **64K deep** / 0.7 | full 6 (focus·recall·ground·connect·check·voice) | light: warm-recall pre-fetch | medium: notice-and-mark | yes (conversational memory) |
| **walkthrough** | `narrate_step_confirm` (stages, narrate-heavy) | paragraph | floor R≈4 · swarm≤6 | **64K deep** / 0.7 | full 8 (+ `step` + `attend`) | light: prepare-next-step | medium: progress-watch | yes (session digest) |
| **text-only** | `direct` (1 part, inject-only) | line→beat | floor R≈4 · swarm≤2 | **16K swarm-lean** / 0.6 | minimal 2-3 (focus·ground·[recall]) → inject | off | low: notice-only | yes |
| **decide-for-me** | `direct` + act (1 part, inject + govern) | beat | floor R≈4 · swarm≤4 | **16K swarm-lean** / 0.5 | act-cast (classify·route·ground·check) + governed actions | medium: queue-prep | high: act-on-sensed (governed) | yes (decision ledger) |
| **background** | `direct` (1 part, terse) | line | floor R≈4 · swarm≤3 | **16K swarm-lean** / 0.6 | ~0 (one-line ack only) | **PRIMARY**: consolidate·prewarm·prepare-proactive-surface | medium: surface-if-needed | **PRIMARY** (the rollup home) |
| **watch-and-react** | `direct` (1 part, terse) | line | floor R≈4 · swarm≤3 | **16K swarm-lean** / 0.6 | ~0 (comment only when relevant) | low | **PRIMARY**: sense-watch cast (relevance·salience·interrupt-judge) | yes (what-I-saw log) |
| **focus** | `direct` (1 part, ≤2 lines) | line | floor R≈4 · **swarm 0** | **16K swarm-lean** / 0.5 | **0** (suppressed) | **0** | minimal: interrupt-guard ONLY (a genuine emergency) | deferred (flushed on focus-exit) |
| **off** | — (chat short-circuits) | — | — | — | **empty** | **off** | **off** | **off** |

Reading the matrix as relationships (Tim-style), not cells:

```
  the dial picks a ROW; the row is a PROFILE across four contexts.
  staging modes  → weight lands on the per-turn column.
  ambient  modes → weight lands on sense.
  idle     modes → weight lands on background + rollup.
  deep-work mode → weight lands NOWHERE (everything suppressed but a guard).
  the floor (R≈4) is the ONE invariant across every non-off row — the live stream is never starved.
```

---

## 2. One registry, mode-scoped — the reuse skeleton (the cross-mode pattern)

Per L1 / C2.1 there is **one** file-discovered role registry; "a mode's cast" is the subset of roles whose
`modes` tuple contains that mode (the `available_verbs(mode, ctx)` pattern, `suite.py:2113`). So the design
question is **not** "six disjoint sets" — it is **which roles carry across modes and which are mode-unique.**
The carries ARE the pattern:

- **`ground`** (live state → citable facts) — appears in *every* non-off mode. It is the universal
  "don't speak past the truth" role. Pure reader; cheapest; brain-shared (`default_model=None`).
- **`recall`** (utterance/topic + memory → past context) — in listening, walkthrough, text-only,
  background, rollup. The universal "what do we already know" role.
- **`focus`** (the *selector* role — reads the utterance, outputs which-roles-to-fire + part-1 shape;
  note the unfortunate name-collision with the `focus` *mode* — see §8 naming) — in every mode that fires a
  per-turn cast (listening, walkthrough, text-only, decide-for-me). It is the **cast's own dispatcher**:
  the role that reads the turn and decides which siblings are worth spending slots on this turn. This is the
  single most reusable role and the most powerful — it makes the cast *adaptive per turn within a mode*.
- **`check`** (forming answer vs ground → contradiction; chains AFTER a part starts) — in the staging
  modes and decide-for-me (where it gates an action). The universal "catch yourself" role.
- **`connect`** (topic + thread → a link) — listening, walkthrough, background (where it builds the
  proactive surface). The "weave it into what came before" role.
- **`voice`** (persona + answer → tone) — listening, walkthrough (the spoken modes). The "say it as
  *her*" role; reads `voice/personas.py`. NOT in the text/ambient modes (no voice to shade).

**Mode-unique roles** (the new ones this doc proposes):

- `step` / `attend` — walkthrough's narration spine (§4).
- `classify` / `route` — decide-for-me's action-cast (§5).
- `salience` / `interrupt-judge` — watch-and-react's sense-watch (§6).
- `consolidate` / `prewarm` / `prepare-surface` — background's between-turns work (§7).
- `digest` / `cluster` / `extract-pattern` — the rollup cast (§7.4).
- `interrupt-guard` — focus's single sense role (§3 focus row).

> [!note] The pattern stated once
> **~6 roles are the shared spine across modes; each mode adds 0–2 unique roles + tunes the budget.**
> A new mode is mostly a *recombination* of existing roles + a budget + a brain-config — not a new cast
> built from scratch. This is "identify the relational primitive once, reuse everywhere" applied to roles.

---

## 3. The non-staging modes' per-turn casts (inject-into-one-part)

These modes are `direct` (one part) but most still fire a *small* per-turn cast that injects into that part.
The face-value reading of the locked budget table is honored: **one part, no extra parts** — the roles
enrich the single answer, they don't multiply it.

### text-only
- **Per-turn cast:** `focus` (selector) → `ground` (always) → `recall` (if the selector says the turn
  references prior work). 2-3 roles, all injecting into the one part. No `voice` (no spoken delivery), no
  `connect`/`check` by default (concise, "only to what is addressed", `MODE_DIRECTIVES:1048`).
- **OPEN CALL (Tim-decision, flagged):** the locked table maps text-only → `direct`. I read this at
  face value as **direct + a minimal injecting cast** (not pure-zero like focus), because text-only is
  "listening's affordances, written" — it wants grounding, just not staging or voice. The alternative
  (pure-direct, zero roles, identical to focus) is cleaner but loses grounding on typed turns. **My
  recommendation: the minimal injecting cast** — it costs ≤2 swarm slots and keeps typed answers as honest
  as spoken ones. Tim picks.

### decide-for-me — see §5 (it is rich enough to be its own section).

### background / watch-and-react
- **Per-turn cast: ~0.** When the operator *does* address them, the directive is "surface only what needs
  you / comment only when relevant, briefly" (`:1049`, `:1052`). The single part runs with at most `ground`
  injected. Their cognition lives in the *other* columns (sense/background), not the rare direct turn.

### focus
- **Per-turn cast: 0.** Suppressed by design (`swarm 0`). The answer is ≤2 lines from base context. The
  *only* cognition focus permits anywhere is a **sense-context `interrupt-guard`** (§6) — a single cheap
  role that fires on a sensed event and decides "is this a genuine emergency worth breaking deep-work for?"
  Everything else is queued for focus-exit (the rollup flush).

### off
- **Empty cast, no contexts live.** `chat()` short-circuits before any directive (`suite.py:1055`). Stated
  explicitly so the matrix has no hole: switching off the dial switches off cognition entirely.

---

## 4. `walkthrough` — the second STAGING cast (the natural companion to listening)

Walkthrough is the *other* mode that spawns parts (`04:65`, "the staging-WANTS-IT mode"). Its directive is
"actively guide: narrate what you are doing and direct the operator's attention step by step" (`:1051`). So
its cast and shape are **narration-heavy** — it carries the listening spine **plus two unique roles**:

**Cast (8): `focus · recall · ground · connect · check · voice · step · attend`**

- `step` (NEW) — reads the current task/graph state + where the operator is in the procedure → outputs
  *the next concrete step* as structured JSON `{step_label, what, why, target_address}`. This is what makes
  walkthrough *guide* rather than *answer*. Chains into the `narrate` part.
- `attend` (NEW) — reads `current_locus()` (`suite.py:1500`) + the step → outputs *what to direct the
  operator's attention to* (`{ui_address, gesture: "look"|"click"|"watch"}`). Routes a render-hint that the
  surface can use to highlight the node/region the walkthrough is pointing at. This is "direct the
  operator's attention" made literal — a cognition role driving the canvas's attention.

**Shape: `narrate_step_confirm`** (new, §9). Paragraph-grain (a walkthrough beat is a fuller explanation).
The `check` role here is load-bearing: in a guide, a wrong step compounds, so `check` runs as a **jury**
(C2.4, `draws:3`, verdict = majority) before the `step` part commits — the volatile-memo fix matters most
exactly where being wrong is most expensive.

---

## 5. `decide-for-me` — the per-turn DIRECT cast that ALSO acts

decide-for-me is the most interesting non-staging mode: it is `direct` (one part) but it **acts through the
existing governance posture** (C9.1, `:1053`). So its cast has two halves: an **enrich half** that injects
into the one decisive part, and an **act half** that routes to *governed actions* via the deterministic
posture router — never bypassing the gates ([[feedback-autonomous-spawn-lead-only]]; C9.2: roles never
reach `claude -p`).

**Cast: `focus · classify · route · ground · check` + governed-action routing**

- `classify` (NEW) — reads the turn → outputs the *action-class* of what's being asked
  (`{intent: propose_node|run_graph|surface|answer, posture_class: AUTO|REVERSIBLE|APPROVAL}`). This is the
  input the deterministic `decide-for-me` router already consumes (`suite.py:3476-3483`, the posture decides,
  not a judgement call — L2).
- `route` (NEW) — a pure **rule-target**, not a model: given `classify`'s output, a *declared rule*
  (G3) maps `posture_class → destination`: AUTO/REVERSIBLE → chain a governed verb dispatch through the
  EXISTING `_dispatch_rhm_action` whitelist; APPROVAL → `surface` to the inbox/decisions lane. **The model
  classifies; the rule routes; governance gates.** Three-layer separation held (L2 + C9.1).
- `check` — gates the action: a contradiction/safety abstain BEFORE the AUTO action fires (the abstain
  state, `latent/firing/ran/injected/failed/**abstained**`, C7.1). If `check` abstains, the action does NOT
  auto-fire — it surfaces instead. This is the "you still cannot self-approve" line (`:1053`) enforced in
  the cast, not just the router.

**Shape: `act_then_report`** (new, §9) — one part that *reports what it did/queued*, after the act-half has
routed. Grain: beat.

> [!warning] The governance boundary, stated loudly
> A decide-for-me role can **trigger** a reversible/AUTO governed verb — but ONLY through
> `_dispatch_rhm_action` (the ONE whitelist, E6), ONLY in the posture the action declares, and NEVER
> build-dispatch / `claude -p` (lead-only). The cast does not widen what's reachable; it only removes the
> "ask first" step for the classes the posture already marks AUTO. Adversarially verify a role cannot
> escalate (C9.2).

---

## 6. SENSE context — what senses trigger which casts

**The HOW (net-new, G5/C5.3):** an event-hook on screen/app/state changes. The repo has the substrate to
build this on — `_affordance_context()` (`suite.py:2090`) already derives a live context dict from
`state()`/`now()`/focus reads, and the event log (`_emit`/`_emit_durable`) is the append-only stream a hook
watches. A **sense trigger** is: *an event of a watched kind lands → a role whose `trigger.event` matches +
whose `predicate(_affordance_context())` holds + whose `modes` includes the current mode → fires.* (Exactly
the `available_verbs` gate, two-dimensional now.) **No spoken reply** — sense casts route to
surface/address/typed-lane (never inject-into-reply: there is no reply, §0 / constraint).

**What the senses ARE (the watched event-kinds) and the cast each triggers:**

| sensed event | predicate (illustrative) | mode(s) | cast fired | destination |
|---|---|---|---|---|
| operator selects a node (`node_selected`) | `ctx["node_selected"]` | watch-and-react, listening | `salience` (is this worth a comment?) → if yes `ground`+`connect` | surface a chip / inject-into-NEXT-turn |
| canvas/state change (`graph_changed`) | `ctx["graph_nonempty"]` & changed | watch-and-react | `salience` → `check` (did this break something?) | surface-to-inbox if `check` flags |
| a run completes (`run_done`) | event kind | decide-for-me, background | `route` (is a follow-up AUTO action warranted?) | governed chain OR surface |
| an inbox item arrives (`surface_review`) | event kind | decide-for-me, background | `classify` → `route` | governed/surface per posture |
| screen/app focus changes (`app_changed`) | sense-hook (net-new) | watch-and-react | `salience` → `interrupt-judge` | surface only if salient |
| ANY event, in **focus mode** | always | focus | `interrupt-guard` ONLY | surface ONLY if a genuine emergency; else swallow |

**The sense cast's spine: `salience` + `interrupt-judge`/`interrupt-guard`** (NEW).

- `salience` — reads the event + live context → `{worth_surfacing: bool, why, urgency}`. The
  gatekeeper that stops watch-and-react from narrating every twitch.
- `interrupt-judge` (watch) / `interrupt-guard` (focus) — same role, different threshold by mode: watch
  surfaces on "relevant"; focus surfaces ONLY on "genuine emergency" (the highest bar). This is **one role,
  mode-tuned by a config threshold** — the §2 reuse pattern again.

**Floor sacred (constraint 3):** a sense cast runs under the mode's swarm cap, never the reserved R floor.
A storm of sensed events cannot starve a live turn — the live stream's R≈4 is untouchable.

---

## 7. BACKGROUND context — what cognition does between turns

**The HOW (net-new, G5/C5.2):** an idle-loop trigger. When no turn is in flight AND the mode permits AND
slots are free under the cap, the loop fires the mode's **background cast**. **No spoken reply** — outputs
route to **address** (prepared for the next turn to read) or **surface** (a proactive offer). This is where
the *idle* modes (background, also decide-for-me's queue-prep) do their real work.

### 7.1 `consolidate` (NEW) — the between-turns memory worker
Reads recent turns' `run://` records + the conversation → writes a compacted "what we've established"
note to an **address** the next turn's `recall` reads. This is *cheaper recall at turn-time* bought with
*idle compute* — the attention economy moving spend off the hot path. (Mirrors the rollup but turn-local.)

### 7.2 `prewarm` (NEW) — predictive pre-fetch
Reads the conversation trajectory → predicts the *likely next topic* → fires `ground`/`recall` for it
**ahead of the turn**, writing to an address. When the predicted turn arrives, Part 1 can read an
already-resolved enricher → the staged reply is *faster* because the swarm ran before the operator spoke.
This is the deepest unlock: **cognition that happens in the silence between turns**, so the next turn starts
already-thought-about. (Honors the floor: prewarm yields the moment a real turn starts.)

### 7.3 `prepare-surface` (NEW) — the proactive offer
Reads accumulated state → if something genuinely warrants the operator's attention, builds a *proactive
surface item* (a suggest-proposal via the existing `suggest` path, routed to the inbox). This is "surface
only what genuinely needs the operator" (`:1049`) made active rather than reactive — background mode's whole
reason to exist.

### 7.4 ROLLUP context — the introspective-data-building loop (C5.4)
**The HOW (net-new, G5):** a timer/scheduler fires the consolidation of the swarm's OWN `run://`-addressed
run-records (persisted per Tim's carried dev-call, GC'd). This is [[project-introspective-data-building]]
applied to cognition itself: *the operation self-instruments → run-records → substrate → rollups →
knowledge that improves the next run.*

**The rollup cast: `digest · cluster · extract-pattern`** (NEW).

- `digest` — reads a window of run-records (which roles fired, latencies, verdicts, abstains) → a
  human-legible "what the cognition did" summary, surfaced to the cognition view / a typed-lane.
- `cluster` — groups recurring turn-shapes / role-firing-patterns → "these turns all triggered the same
  cast" — the input to *learning which casts a mode actually needs* (the cast tunes itself by use, the
  Batch-4 "tuned by use" promise made mechanical).
- `extract-pattern` — finds where a role *consistently abstained / failed / was pruned* → flags a
  candidate role/budget change to the inbox (rides the normal change path, C3.4 — no special gate). **The
  cognition proposing its own tuning, governed like any change.**

> [!note] Rollup is itself a SHAPE (the generalization the advisor flagged)
> A rollup is a *staged consolidation* — `digest` depends on the window, `cluster` depends on `digest`,
> `extract-pattern` depends on `cluster`. That is a thought-shape (§9 `rollup_consolidate`) running NOT
> per-turn but per-schedule, writing to surface/typed-lane instead of inject. **The thought-shape concept
> generalizes from "the reply as parts" to "any staged structured output" — per-turn, background, OR
> rollup.** This is a real unlock: one shape grammar, three activation contexts.

---

## 8. Per-mode grain / slot-budget / brain-config (the three remaining dials the mode sets)

### 8.1 Part-grain (C4.1 — a config table, tuned by use)
Tim's own examples (focus=line · listening=beat · explaining=paragraph) extended across the matrix:

```python
MODE_GRAIN = {
    "focus":          "line",       # ≤2 lines, terse
    "background":     "line",       # one-line ack / one-line surface
    "watch-and-react":"line",       # a brief comment
    "text-only":      "beat",       # a written beat, concise
    "decide-for-me":  "beat",       # report what was done/queued
    "listening":      "beat",       # conversational beats (the default)
    "walkthrough":    "paragraph",  # fuller, guiding explanation
    # off → n/a
}
```
Pattern: **grain widens monotonically with the per-turn richness gradient (§0).** Deep-work/ambient → line;
conversational → beat; guiding/explaining → paragraph. The grain IS the spend made visible in the prose.

### 8.2 Slot-budget (Batch-2 Q1 — reserve a floor, mode tunes the rest)
The floor `R≈4` (reserved for main stream + judge, never starved) is **invariant across every non-off row**.
The mode tunes only the *swarm cap* (`32 − R`, capped lower per mode). From the matrix:

```python
MODE_BUDGET = {  # R reserved is constant ≈4; this is the SWARM cap (additional)
    "off":            0,
    "focus":          0,    # per-turn 0; sense interrupt-guard is 1 transient, off the cap
    "background":     3,    # idle work, generous in idle but yields to a real turn
    "watch-and-react":3,    # sense-heavy
    "text-only":      2,    # minimal inject cast
    "decide-for-me":  4,    # enrich + act cast
    "listening":      6,    # the full conversational cast
    "walkthrough":    6,    # full + narration (step/attend cheap)
}
```
Pattern: **budget tracks the per-turn gradient too, EXCEPT background/watch — which spend their budget in a
*different column* (idle/sense), not per-turn.** The budget is "budget = attention, literally" (`00:22`):
deep-work spends ~nothing; the swarm's reach is the mode's chosen breadth of concurrent thought.

### 8.3 Brain-config (R2-FOLD H1 — mode selects the brain too)
The genuinely under-explored lever. Two brain profiles exist as the poles:

```python
MODE_BRAIN = {
    # voice-conversational modes → the DEEP brain (big context for rich grounded talk)
    "listening":   {"ctx": "64K", "temp": 0.7},
    "walkthrough": {"ctx": "64K", "temp": 0.7},
    # swarm/idle/ambient modes → the LEAN swarm-brain (small ctx, frees KV for concurrency)
    "text-only":     {"ctx": "16K", "temp": 0.6},
    "background":    {"ctx": "16K", "temp": 0.6},
    "watch-and-react":{"ctx":"16K", "temp": 0.6},
    "decide-for-me": {"ctx": "16K", "temp": 0.5},   # decisive, low-temp
    "focus":         {"ctx": "16K", "temp": 0.5},   # terse, low-temp
}
```
**Why this matters (the R1-FOLD finding):** the resident 4B's KV pool is shared between the main context and
the swarm's short role contexts — **real co-resident concurrency is well below 32 at a 64K main context.**
So a *swarm-heavy* mode can't ALSO run a 64K main context: it must pick the lean brain to free KV for the
swarm. This is why brain-config is a *mode* lever, not a global setting:

```
  deep brain (64K) ⇄ swarm breadth  is a SEESAW on one 16GB card.
  conversational modes BUY a big context and SPEND fewer swarm slots on richer parts.
  ambient/idle modes BUY swarm breadth (more concurrent thoughts) and SPEND a smaller context.
  the mode IS the choice of where on the seesaw to sit.
```
This is arguably the deepest thing "mode = the dial" unlocks: **the dial physically reallocates the one
card's KV between depth-of-context and breadth-of-concurrency.** (Honors Batch-2 Q3: swarm always on the
resident model; the *brain* is a separate selectable; mode auto-decides.)

---

## 9. The starter THOUGHT-SHAPES library

Currently two exist (`acknowledge_retrieve_synthesise_offer`, `direct`, `04:107-137`). Proposed additions,
each declarative data run by the one generic runner (`04:101`). Shapes are registry data, mode-selected via
`shape_for(mode)`, and — per §7.4 — the grammar now spans per-turn / background / rollup.

| shape | used by (mode × context) | parts (deps) | grain | acts? |
|---|---|---|---|---|
| **`direct`** (exists) | all non-staging modes, per-turn | `answer[]` | line/beat | final only |
| **`ack_retrieve_synth_offer`** (exists) | listening, per-turn | acknowledge[] → synthesise[role:recall,ground] → offer[] | beat | synth part |
| **`narrate_step_confirm`** (NEW) | walkthrough, per-turn | acknowledge[] → narrate[role:step,ground] → attend[role:attend] → confirm[] | paragraph | narrate part |
| **`act_then_report`** (NEW) | decide-for-me, per-turn | (act-half: classify→route→govern, off-stream) → report[role:route-result] | beat | via router only |
| **`enrich_one`** (NEW) | text-only, per-turn | answer[role:ground,recall] (one part, roles inject) | beat | final only |
| **`watch_comment`** (NEW) | watch-and-react sense | comment[role:salience] (fires only if salient) | line | none |
| **`prepare_surface`** (NEW) | background context | gather[role:consolidate] → offer[role:prepare-surface] | line | suggest-path |
| **`rollup_consolidate`** (NEW) | rollup context | digest[window] → cluster[role:digest] → extract[role:cluster] | paragraph | surface/typed-lane; propose-change |

**The pattern across shapes:** every shape is `[an instant/cheap opener] → [the substance, gated on
resolved role addresses] → [an optional offer/confirm/report tail]`. The three *positions* (open · substance
· tail) are invariant; what changes per shape is *which roles gate the substance* and *whether the tail
acts/offers/reports*. **One skeleton, parameterized — the same "find what doesn't change across contexts"
move as the roles (§2) and the grain/budget (§8).**

---

## 10. What "mode = the dial" fully unlocks (the synthesis)

Pulling the patterns together — the dial is not one knob, it is a **coordinated reallocation across six
coupled axes from one source**:

```
  MODE  ─┬─→ which CAST fires           (subset of one registry; ~6 shared + 0-2 unique)
         ├─→ which ACTIVATION-CONTEXTS  (per-turn / background / sense / rollup — the matrix)
         ├─→ which SHAPE                 (per-turn parts; OR a background/rollup staged output)
         ├─→ the GRAIN                   (line → beat → paragraph, tracks per-turn richness)
         ├─→ the SLOT-BUDGET             (floor R≈4 invariant; swarm cap = chosen breadth)
         └─→ the BRAIN-CONFIG            (deep-64K ⇄ lean-16K seesaw of KV on one card)
```

The four things this unlocks that weren't visible when "mode" meant "a brevity directive":

1. **The non-staging modes aren't "less cognition" — they're cognition that moved columns.** focus looks
   empty per-turn but its sensed interrupt-guard is the *highest-stakes* role in the system (it alone may
   break deep work). watch-and-react does almost nothing per-turn and almost everything on sense. The dial
   doesn't turn cognition *down*; it turns it *toward* a different activation-context.

2. **Cognition in the silence (background prewarm).** The next turn can start *already-thought-about* — the
   swarm runs in the idle gap and writes its result to an address Part 1 reads. The dial decides whether a
   mode spends idle compute buying turn-time speed.

3. **The brain-config seesaw is a physical reallocation of one card.** A mode literally chooses
   depth-of-context vs breadth-of-concurrency on the shared KV pool — the hardware constraint (R1-FOLD)
   becomes an expressive dial rather than a wall.

4. **The cognition tunes itself, governed.** The rollup cast (`digest·cluster·extract-pattern`) reads the
   swarm's own run-records and *proposes its own cast/budget changes* through the normal change path — the
   matrix is not hand-frozen, it's a starting point the system refines by use (the Batch-4 "tuned by use"
   promise made mechanical, the introspective-data-building law applied to cognition itself).

---

## 11. Open calls surfaced for Tim (not decided silently)

- **`focus` role-name collision.** There is a `focus` *mode* AND a `focus` *role* (the cast selector). Two
  options: (a) rename the role → `selector` / `dispatch` / `triage`; (b) accept the collision (context
  disambiguates). Recommendation: **rename the role to `triage`** — it's clearer about what it does and ends
  the collision. (Tim picks; this is a rename, cheap.)
- **text-only: minimal injecting cast vs pure-direct (zero roles).** §3. Recommendation: the minimal cast
  (keeps typed answers grounded for ≤2 slots). Tim picks.
- **Whether `prewarm` (predictive background) is in the first activation-context build or deferred.** It's
  the highest-value but most speculative background role (it predicts the next topic). Recommendation: ship
  `consolidate` + `prepare-surface` first (concrete), add `prewarm` once per-turn + background are proven.
- **The per-mode brain-config table is a hypothesis, not a measurement.** The 64K⇄16K poles and the per-mode
  assignments must be **measured by use** against the real co-resident KV ceiling (the G0 spike measures
  exactly this). The table is the starting allocation, not a locked truth.
- **Sense substrate scope.** §6 lists six watched event-kinds; `app_changed` (screen/OS focus) is the only
  one with NO repo substrate today (the rest ride the existing event log). It is the heaviest net-new piece
  of the sense context — flag for sequencing (probably after the log-driven senses prove out).

---

## 12. How this composes back into the build (no new spine)

Nothing here is a new mechanism — it is **registry data** filling the schema the triad already specifies:
roles are files in `roles/` (C2.1) with a `modes` tuple; shapes are rows in `THOUGHT_SHAPES` (`04`); the
grain/budget/brain tables are config tables (C4.1, `04:266`, R2-FOLD H1); the activation-contexts are the
three net-new triggers G5 already names (idle-loop · event-hook · scheduler). This doc just **fills the
matrix** the dial selects over. It rides the locked architecture; it adds casts, shapes, and tables — the
exact growth the registry was built to absorb (L1: "everything is declared registry data by type").

*Generative draft for Tim to react to — keep / cut / add / rename, per mode, per role, per shape.*
