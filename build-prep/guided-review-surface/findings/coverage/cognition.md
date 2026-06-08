# Coverage Round — `area://cognition`
# nodes/ + roles/ ↔ The Guided-Review Surface

> **Sweep method:** full-territory walk (not a query). Read nodes/AGENTS.md + roles/AGENTS.md, then
> every file in nodes/ (15 files) and roles/ (8 files), then targeted reads of runtime/suite.py
> (MODE_REGISTRY, walkthrough-mode, GUIDE_SEQUENCES/TEACH/INDICATE, chat_parts cast-fire path,
> RHM_VERB_SPECS, cognition_info, present_current) and runtime/roles.py (RoleRegistry, cast_for_mode).
> All evidence below is tagged: **Observed (file:line)** = read directly ·
> **Inferred** = pattern-matched, not execution-verified ·
> **Unification-opportunity** = a latent composition the surface would activate.

---

## 0 · What area://cognition IS (a precise map)

The two directories are the collective cognition layer — two halves of the same self-registering
extension system:

**nodes/** — 15 node-type modules (C2 declarations). Three kinds:
- **process** — pure transforms (`uppercase`, `titlecase`, `wordcount`, `join`, `pair`, `gate`) and
  AI workhorses (`llm`, `ask`, `embed`, `retrieve`, `similarity`)
- **content** — `constant`, `codebase`, `portal`, `model_of_tim` (VOLATILE — reads ~/foundation),
  `rhm_mode` (VOLATILE — the presence dial AS a node, with `voice_enabled` toggle)
- Each self-registers on drop-in; no change to runtime, UI, or tools

**roles/** — 8 role modules (C2.1 superset declarations). Facets:
- **config-only** — `judge` (finished-thought classifier, voice circuit endpoint; no cast, no fire via swarm)
- **`listening` cast** — `focus`, `recall`, `ground`, `connect`, `check`, `voice` (the locked C2.3 cast)
- **jury** — `verify_jury` (3 draws + majority-vote verdict_rule; in no cast)

**Critical structural fact:** `cast_for_mode("walkthrough")` returns `[]` (an EMPTY CAST).
Every role that declares a `mode_scope` declares `{"listening"}`. No role scopes to `walkthrough`,
`focus` mode, `background`, `watch-and-react`, `decide-for-me`, or `off`.
Observed (roles/focus.py:36, roles/recall.py:31, roles/ground.py:33, roles/connect.py:30,
roles/check.py:40, roles/voice.py:33; runtime/roles.py:210-214 `cast_for_mode`).

---

## 1 · USE — what the guided-review surface would directly USE from this area

### 1.1 · chat_parts() fires the cast — walkthrough mode today fires NOTHING

**Observed (suite.py:5333):** `cast = self.cast_for_mode(mode)` is called at the top of the
`chat_parts()` staged path. When the operator is in the guided dialogue, `mode` is `"walkthrough"`.
`cast_for_mode("walkthrough")` returns `[]`. So the staged-parts engine fires NO concurrent roles
during a guided stop today — the enrichment swarm (recall/ground/connect/check/voice) is completely
absent from the guided dialogue.

**What it means:** The live guided dialogue is operating with a subset of the cognition layer's
capability. The Commander talks to the RHM at a stop; the RHM answers from base context only. No
memory-recall fires. No ground-check. No contradiction sentinel. No tone shaper. The `listening` cast
(the soul of the collective cognition) is idle while the review conversation happens.

This is NOT a build flaw — it is an UNRESOLVED GAP between two built things. The chat_parts engine
already accepts a mode and already fires the cast for that mode. The mode just has no cast declared
yet.

### 1.2 · The `judge` role fires on the voice circuit regardless of mode

**Observed (roles/judge.py:27, suite.py:4841):** `judge` is triggered by `POST /api/voice/finished-thought`
— the always-listen semantic endpoint. This fires independent of the presence mode and is NOT gated
on `walkthrough`. So voice-in for the guided dialogue already has its semantic endpoint working.
The `judge` role is the most-ready leg of the voice circuit; it fires during a guided turn the same
as any other turn.

### 1.3 · `model_of_tim` node — the explicit RHM grounding source

**Observed (nodes/model_of_tim.py:1-29):** reads `~/foundation/system/principles.md` at run time
(VOLATILE — never memo-cached). This is the canonical explicit model of Tim — "Tim's own statements
of how the Company holds itself." The RHM reasons FROM this. It is a node in the composition graph;
during a guided walk where the RHM narrates AT-ALTITUDE "what this IS", it is drawing on the
principles in this node's output.

**What it means for the build:** If the RHM's altitude-shaping (`up_translate`/`coa`) is to narrate
at Tim's altitude in the guided dialogue, `model_of_tim`'s content is the grounding foundation that
makes "altitude" concrete. The synthesis flagged that `up_translate`/`coa` altitude-shaping "may not
be FE-wired." This node is the content source that wiring would draw on.

### 1.4 · `llm` node — the model-slot the RHM brain occupies

**Observed (nodes/llm.py:1-50):** model/base_url/system/temperature/max_tokens/top_p/retries/timeout
are all swappable config slots. The `draw` field (llm.py:27-33) is the per-draw cache-key differentiator
for jury/ensemble patterns. This is the node the `ask` node also builds on.

**What it means for the build:** The guided dialogue uses the RHM brain, which runs through this
node's model-slot infrastructure. The `brain_config: "voice-64k"` declared on the `walkthrough` mode
(suite.py:1291) controls which model config the brain uses for guided turns. The `llm` node's
`draw` mechanism enables the verify_jury pattern — relevant if a "did my request-change get
understood correctly?" jury were to fire during the generate step.

### 1.5 · `rhm_mode` node — the mode IS a node; the guided-review sets it

**Observed (nodes/rhm_mode.py:1-38):** the presence dial lives as a node config in the `system`
graph. `start_walkthrough` and `start_guide` both call `self.set_mode("walkthrough")` (suite.py:6317,
6462) — which IS editing the `rhm_mode` node's config. The `voice_enabled` toggle (rhm_mode.py:25-34)
controls whether voice fires at all — read by `Suite.voice_enabled()`.

**What it means for the build:** Entering guided-review mode IS a node-graph edit via the composition
system. The `voice_enabled` field is read by the conversation loop — if the Commander wants voice-off
during the guided dialogue, toggling `voice_enabled` on this node controls that. The mode-as-a-node
design is already wired; the guided-review surface uses it.

### 1.6 · `codebase` node — what the RHM reads of the Company during the dialogue

**Observed (nodes/codebase.py:1-48):** VOLATILE, reads the live filesystem. The `ask` node takes
`codebase` output as context. During a "consult" verb fired from the guided dialogue
(RHM_VERB_SPECS["consult"] — Observed suite.py:3165), the RHM reads the codebase FOR the Commander.
The guided-review surface already has `consult` in `_M_CONSULT` (the set includes `walkthrough` —
suite.py:3155).

---

## 2 · TOUCH — what the guided surface touches or is touched by in this area

### 2.1 · MODE_REGISTRY entry: `walkthrough` mode declares a `guided` subtype

**Observed (suite.py:1278-1292):**
```
"walkthrough": {
    "resolution": {"strata": None, "howto_detail": "full", "budget": 6000},
    "subtypes": {
        "guided": {},
        "show-me": {"budget": 8000},
    },
    "consent": "offer",
    "grain": "paragraph", "shape": "linear-stream", "stage": True,
    "brain_config": "voice-64k",
}
```
The `"guided"` subtype is declared but empty (`{}`). The `"show-me"` subtype has a wider budget (8000
vs 6000). The `stage: True` means the `chat_parts()` staged path IS supposed to fire for walkthrough
turns (it would fire the cast — but the cast is empty today). The `shape: "linear-stream"` and
`grain: "paragraph"` are the visual shape the cognition view would light up with.

**Touched:** any new `mode_scope` added to roles/ would flow into this mode's cast, changing which
roles fire during guided turns, without changing any other code.

### 2.2 · `present_current` is mode-agnostic — it does not fire or consult the cast

**Observed (suite.py:6198-6285):** `present_current` reads the corpus (`address_help`, `coa`), stamps
the `ui_target`, and returns the framing. It does NOT call `chat_parts()` or `cast_for_mode()`. The
narration is model-free (corpus/registry-read, never generated). The cognition cast fires ONLY when
the Commander asks a question (the chat turn) — NOT during the automated walk step itself.

**Touched:** the guided surface would not add the cast to `present_current` — the cast fires on the
DIALOGUE turns (questions/comments). This is the correct separation: corpus narrates the stop, cognition
enriches the live conversation at the stop.

### 2.3 · RHM_VERBS: `request_change` is already in walkthrough's offered verb set

**Observed (suite.py:3183-3200, 3153-3155):** `request_change` routes a conversational change-request
through `surface_intent_at` → `ingest_comment` (the SAME path the synthesis calls "RHM annotates as
you talk" — partially reachable today). The `_M_BUILDISH` set that gates `request_change` is
`{"listening", "text-only", "decide-for-me"}` — **it does NOT include `"walkthrough"`**.

**Observed (suite.py:3197-3200):** `request_change`'s `mode_primary` = `_M_BUILDISH`. So while the
Commander is in walkthrough mode (the guided dialogue), the `request_change` verb is NOT offered.
This is the Bucket C-f gap (RHM-annotate verb) from a different angle: the verb that would let the
RHM record a change-request mid-dialogue is gated out of the walkthrough mode.

**What it means for the build:** Adding `"walkthrough"` to `_M_BUILDISH` (or `request_change`'s
specific mode set) would make this verb available during the guided dialogue — the annotation/intent
path without new architecture.

### 2.4 · `cognition_info()` serializes cast-per-mode — the FE view sees the empty walkthrough cast

**Observed (suite.py:4742-4779):** `cognition_info()` emits `casts = {m: [r.id for r in
self.role_registry.cast_for_mode(m)] for m in self.MODES}`. Today this returns `{"walkthrough": []}`.
The CognitionView (the sibling live view, `/api/cognition_info`) would show an empty cast for the
walkthrough mode — visually confirming the gap.

---

## 3 · UNIFY / IMPROVE — latent compositions the guided surface would activate

### 3.1 · THE TOP UNIFICATION — the guided dialogue as a `walkthrough` cast (mode→cast declaration)

**Unification-opportunity.** When the guided dialogue is live and the Commander asks a question at a
stop, `chat_parts()` fires and calls `cast_for_mode(mode)`. The mode at that point is `"walkthrough"`
— `start_guide` sets it (suite.py:6462) and nothing restores `"listening"` during the dialogue.
(Stated as an assumption: the walkthrough mode persists through Q&A; nothing observed restores it.)
`cast_for_mode("walkthrough")` returns `[]`. So the cast — the whole enrichment swarm — is idle.

**Calibrated payoff of 6 `mode_scope` edits (what is and is NOT immediate):**

Adding `"walkthrough"` to the `mode_scope` of focus/recall/ground/connect/check/voice would:

1. **Immediately (fires + lights up the CognitionView):** all six roles fire concurrently and write
   their outputs to `run://<turn>/<role>` addresses. The CognitionView emits `cognition.turn.start`
   with `cast=[focus, recall, ground, connect, check, voice]` instead of `[]`. The Commander (or the
   system) can see the concurrent thinking.

2. **Immediately (recall/ground inject via canonical rule):** the `INJECTION_RULE` in cognition.py
   (recall.relevant AND ground.in_scope) IS an AST rule and IS picked up by the injection path at
   suite.py:5402-5409. So memory-recall and live-state grounding inject into Part 2 on the first day.

3. **G3/G4 deferred (connect/check/voice do NOT yet inject):** the `rules` blocks in connect, check,
   and voice are descriptive `{id, reads, effect, kind}` dicts, NOT AST-shaped rules. The comment at
   suite.py:5397-5399 explicitly states: "descriptive {id,reads,effect,kind} role entries are NOT AST
   rules → skipped." Additionally `voice`'s rule is `kind:"route"` — not `"inject"` — so it cannot
   be picked up by the `destination=="inject"` check at suite.py:5418. These roles fire and write their
   outputs, but their outputs do not shape Part 2 until G3/G4.

**The posture question — is the empty walkthrough cast deliberate?** It may be. The code comments at
suite.py:3140-3141 describe walkthrough as "GUIDE/OBSERVE modes (show+consult only) — they do not
RECOMPUTE the graph." This is about the `run` verb, not the cognition cast — but it reveals a design
lean: walkthrough is framed as "lean, show me, guide me" rather than "full cognitive enrichment."
Populating the cast is an OPPORTUNITY, not an obvious fix — and it is a Tim-decision: does the guided
dialogue want the enrichment swarm (memory, grounding) firing on every conversational turn at a stop?

**Evidence base:**
- Observed: `chat_parts()` calls `cast_for_mode(mode)` (suite.py:5333)
- Observed: `cast_for_mode("walkthrough")` returns `[]` today (roles/*.py: no walkthrough mode_scope)
- Observed: `stage: True` on walkthrough mode (suite.py:1289) — the staged path fires
- Observed: canonical INJECTION_RULE picks up recall/ground (suite.py:5402-5409)
- Observed: descriptive rules on connect/check/voice are NOT AST rules → skipped at suite.py:5397-5399
- Inferred: the recall/ground injection would fire for guided turns (same path verified for listening
  turns by the Concurrent Cognition build)

**The deeper unification:** The guided dialogue IS a conversation in listening mode's spirit. The
`walkthrough` mode already has `stage: True` and `consent: "offer"`. Populating its cast with even
recall + ground gives the guided RHM memory of past decisions about the same screen — which is exactly
what "the right-hand-man" reviewing a screen should have. No new code; 6 role file-edits, Tim's call.

### 3.2 · NEW ROLE OPPORTUNITY — a `screen-reader` / `mockup-reader` role for guided stops

**Unification-opportunity.** The synthesis identifies that `mockup://`-addressed stops need the RHM
to narrate from injected HTML (the verified comprehension path — the 14KB injection already works,
Verified-by-use synthesis §0). Today this narration lives in `_chat_context` as an ad-hoc HTML injection
(suite.py:2086-2125). A dedicated cognition role — call it `screen_reader` or `locus_brief` — would:
- `input_addresses: ("mockup_html", "ui_address")` — the injected HTML + the current locus address
- `output_schema: LocusBriefOut` — `{summary: str, zones: list[str], focus_point: str}`
- `mode_scope: {"walkthrough"}` — fires ONLY in guided/walkthrough turns
- `trigger`: fires at the START of a guided stop (before Part 1, or as a concurrent Part-0 that
  pre-digests the mockup HTML into a structured brief Part 1 builds from)

This would move the "read this FOR them" logic out of the ad-hoc `_chat_context` injection and into a
declared role that:
1. Is visible in `cognition_info()` → the CognitionView shows it firing at each guided stop
2. Can be re-bound to a different/faster model (a small embed-and-summarize model for large mockups)
3. Addresses the D2 cap problem (html→text pre-digest is what this role DOES, via a model)
4. Composes with the `check` role — check can read `screen_reader.summary` vs `ground.note` to verify
   the RHM's explanation doesn't contradict the grounded facts about the screen

**Observed basis:** the current mockup injection lives at suite.py:2086-2125 as an ad-hoc block in
`_chat_context` — not a declared role, not visible in the CognitionView, not re-bindable.

### 3.3 · UNIFY: `voice` role (tone) is the altitude-shaping that may not be FE-wired

**Observed (roles/voice.py:1-39):** the `voice` role (tone cognition role, distinct from the TTS
module) takes `(persona, answer)` and returns `(toned, tone)` — the answer rephrased in Tim's persona's
register. **This is `up_translate`/`coa`'s altitude-shaping expressed as a DECLARED ROLE.**

The synthesis flags "confirm `up_translate`/`coa` altitude-shaping is FE-wired (it may be
declared-not-wired-to-surface)." The `voice` cognition role IS that shaping in the collective cognition
path. For the guided dialogue, if the `voice` role is in the walkthrough cast, altitude-shaping is
automatic (the role fires concurrently, its `toned` output arrives before Part 2). If it fires AND
the RHM uses `voice.toned` as Part 2's reply, the altitude-shaping concern in the synthesis is resolved
structurally — not by wiring `up_translate` separately.

**Inferred:** I have not traced whether `chat_parts()` currently reads `voice.toned` vs the brain's
raw output when the voice role fires. The rule in roles/voice.py declares `{"id": "voice-tones-answer",
"reads": "voice.toned", "effect": "deliver the toned phrasing as the reply", "kind": "route"}` — but
whether the G3 rule engine executes this as the actual Part 2 source is the G4 question. This is
declared as a rule; G3/G4 full execution is downstream (flagged in roles/check.py and the Concurrent
Cognition Completion Criteria).

### 3.4 · UNIFY: `gate` node + `verify_jury` role — the GENERATE step verification circuit

**Unification-opportunity.** Bucket C-a (GENERATE-FOR-MOCKUPS) dispatches a `claude -p` scoped to a
mockup HTML file. The synthesis says the dispatch must be "verified by re-render/screenshot, committed,
revertible." A `verify_jury` fired AFTER the dispatch re-render could be the verification gate:
- Claim: "the re-rendered mockup matches the approved change intent"
- 3 draws → majority-vote verdict
- If verdict fails: revert (git revert path already built)

The `gate` node (nodes/gate.py) routes `value` to `pass` or `fail` based on `verdict`. Observed:
`gate` takes `verdict: Any` (truthy-test) — the `verify_jury.verdict` (a `bool`) could wire directly
into a `gate` node's `verdict` port, routing the commit to `pass` or the revert to `fail`. This is the
composition the generate→verify→commit/revert loop is built from — using the existing primitives.

**Observed basis:** gate.py:1-40 (the routing primitive); verify_jury.py:32-45 (majority_vote returns
`{verdict: bool, ...}`); the dispatch → git → revert wire is built (suite.py:7360, 7611, 8920 per
synthesis Bucket A).

### 3.5 · UNIFY: `rhm_mode` VOLATILE + guided-review mode subtype not tracked in live view

**Observed (nodes/rhm_mode.py:29-34):** the `"guided"` and `"show-me"` subtypes are declared in
`MODE_REGISTRY["walkthrough"]["subtypes"]` (suite.py:1284-1286) but the `rhm_mode` node only tracks
the top-level mode string (`config.get('mode', 'listening')`). There is no subtype tracking in the
node. The `cognition_info()` cast serialization also only keys on the top-level modes (`MODES` =
8-tuple). If the guided dialogue wants a richer per-subtype cast (e.g. `"show-me"` fires more roles
than `"guided"`), the subtype axis is not yet threaded to the cast system.

**What it means for the build:** the `"show-me"` subtype has a wider budget (8000 vs 6000) but
currently no different cast. A "show-me leads, Commander follows" experience might want different roles
than "Commander drives, RHM narrates" — this is an open design point, not a build blocker. Flagged as
a future cast-extension axis.

---

## 4 · RELATE — conceptual relationships (the same shape recurring)

### 4.1 · The Sequences primitive in the cognition layer

The synthesis names the Sequences primitive: `resolve → present/work → persist → next/trigger`.
The cognition `chat_parts()` IS this primitive at the intra-turn scale:
- `resolve`: `_chat_prologue` gates + resolves mode/config
- `present/work`: Part 1 (instant from base context) fires + wave runs concurrently
- `persist`: `_chat_epilogue` appends the joined reply to the thread store, emits `chat` event
- `next/trigger`: the declared G3 rules on the cast roles decide what triggers next (inject, chain,
  surface)

The guided-review surface is the Sequences primitive at the inter-stop scale:
- `resolve`: `present_current` resolves the stop's narration and ui_target
- `present/work`: the Commander reads/watches; the RHM talks; `chat_parts()` fires per question
- `persist`: `annotate`/`ingest_comment` accumulates marks at the stop's address
- `next/trigger`: NEXT advances the cursor; the accumulate→generate step reads everything marked

These are the SAME shape at two different scales. The cognition layer IS the implementation of the
Sequences primitive at the turn level; the guided-review surface IS the same primitive at the session
level. They compose vertically (the session step contains the turn loop).

### 4.2 · CognitionView is a sibling live-view — the guided dialogue lights it up

**Observed (suite.py:4742-4779, 5318-5452):** the `cognition_info()` serialization (`/api/cognition_info`)
and the per-turn `cognition.*` SSE events (`cognition.turn.start`, `cognition.role.fire`,
`cognition.role.ran`, `cognition.inject`, `cognition.part`, `cognition.turn.done`) are the data feed
for the CognitionView. These emit on every `chat_parts()` call, regardless of mode.

If the Commander is in a guided stop and asks a question, `chat_parts()` fires. Today it emits
`cognition.turn.start` with `cast=[]` (empty). If the walkthrough cast is populated (unification 3.1),
the CognitionView would light up with `cast=[focus, recall, ground, connect, check, voice]` — the
Commander could see the RHM's concurrent thinking in the sibling view WHILE reviewing a screen. The
CognitionView and the guided-review surface are already designed as siblings (06-rendering.md §F names
them explicitly); this connection is the runtime path.

Observed (suite.py:5340-5342):
```python
self._emit("cognition.turn.start", ..., cast=[r.id for r in fireable], address=_cog_addr)
```

### 4.3 · The portal node and the address grammar — guided sequence as a portal

**Observed (nodes/portal.py:1-24):** a portal is a `RESOLVE='reference'` node — a live window onto
another address. The guided-review sequence (`GUIDE_SEQUENCES`) is an ordered list of `ui://`
addresses, assembled once per guide-start and walked by cursor. A `portal` node whose `config.ref`
points at the current stop's address (`current_locus()`) would make "what I am looking at right now"
a composable node in any canvas graph — another potential bridge between the composition system and
the guided surface.

**Inferred:** I have not verified whether `portal` is used this way today; the GUIDE_SEQUENCES path
and the portal node are separate mechanisms. This is a latent composition, not a confirmed bridge.

### 4.4 · `check` role's chained input address — the `run://` scheme links roles to the guided dialogue

**Observed (roles/check.py:37):** `input_addresses: ("run://<turn>/part-1", "ground")`. The `check`
role reads the forming answer at a `run://` address produced once part-1 begins. This is the same
`run://` addressing scheme the guided-review surface already uses (the R2 context resolution, the
reviewed-item addresses, the annotation store). The intra-turn `run://` ref-read IS the same address
grammar as the inter-turn `run://` addresses in the review session. One address grammar, two scales.

---

## 5 · The gap table (what the cognition layer IS and IS NOT providing today)

| Capability | Status in area://cognition | Relation to guided surface |
|---|---|---|
| judge role — voice semantic endpoint | ✅ built + file-discovered | USE: fires on voice-in during guided stops (any mode) |
| listening cast (focus/recall/ground/connect/check/voice) | ✅ built for `"listening"` | GAP: not declared for `"walkthrough"` — empty cast today |
| walkthrough mode cognition cast | 🔴 missing — no role has `mode_scope: {"walkthrough"}` | TOP UNIFICATION: 6 `mode_scope` declarations would activate the full swarm for guided turns |
| `rhm_mode` node — mode as composition | ✅ built + VOLATILE | TOUCH: entering guided-review sets this node; `voice_enabled` gates voice |
| `model_of_tim` node — explicit altitude grounding | ✅ built + VOLATILE | USE: the grounding source for altitude-shaped narration |
| `llm` + `ask` nodes — AI workhorses | ✅ built | USE: the RHM brain's model slot; `draw` enables jury patterns |
| `gate` node — routing primitive | ✅ built | UNIFY: routes verify_jury verdict → commit/revert in generate step |
| `verify_jury` role — 3-draw majority vote | ✅ built (not in any cast) | UNIFY: explicit jury for generate→verify→commit/revert gate |
| `voice` role — tone shaper | ✅ built for listening | UNIFY: altitude-shaping for guided turns if walkthrough cast populated |
| `screen_reader`/`locus_brief` role | 🔴 not yet declared | NET-NEW OPPORTUNITY: mockup HTML → structured brief as a fireable role in walkthrough cast |
| `request_change` verb in walkthrough mode | 🔴 absent — `_M_BUILDISH` excludes walkthrough | TOUCH: one mode-set addition makes annotate/intent reachable mid-guided-dialogue |
| CognitionView sibling live-view | ✅ wired per chat_parts() events | RELATE: lights up with walkthrough cast if populated |
| `cognition_info()` cast serialization | ✅ built | shows `{"walkthrough": []}` today — would show full cast after unification |

---

## 6 · What it means for the build (the loop-prep appendix)

These findings do NOT introduce new Bucket C items — they ACTIVATE existing built machinery by
declaring the missing join. The hierarchy:

**Immediate (one file-edit per role, no architecture):**
- Add `"walkthrough"` to `mode_scope` in focus/recall/ground/connect/check/voice role files →
  the listening cast enriches the guided dialogue. No runtime change. No suite.py change.
- Add `"walkthrough"` to `request_change`'s mode-primary set (suite.py:3197-3200, the `_M_BUILDISH`
  frozenset or the specific VerbSpec) → RHM can surface a build-intent mid-guided-dialogue.

**Moderate (new role file, no runtime change):**
- Declare `roles/screen_reader.py` with `mode_scope: {"walkthrough"}` → the mockup HTML→brief
  pre-digest lives as a declared, re-bindable role. This is the architectural answer to D2 (cap/
  pre-digest) that is also the Bucket C-f annotate path + the mockup-aware guided stop (Bucket C-c)
  expressed as a role.

**Downstream (G3/G4 execution — already flagged in concurrent cognition build):**
- The `voice` role's tone-shaping and `check` role's contradiction-flag are declared as G3 rules;
  full chained execution waits on G3/G4. Until then the rules are declared data; the roles fire and
  write their outputs to `run://`, but the injection of `voice.toned` as the final Part 2 text is
  partial (the INJECTION_RULE path works; the `voice-tones-answer` route rule is G4).

**Build-sequence implication:** the synthesis §5 step 1 ("text streaming") and step 2 ("walkthrough
↔ chat composition") are still first. Once those are live, the guided dialogue is a real
conversation. THEN declaring the walkthrough cast (this unification) means the Commander's first
guided dialogue gets the full enrichment swarm — memory, ground, contradiction, tone — with zero
additional code beyond the role file edits.

---

*Written by COVERAGE agent, 2026-06-08. Full-territory walk of area://cognition.*
*Path: /home/tim/company/build-prep/guided-review-surface/findings/coverage/cognition.md*
