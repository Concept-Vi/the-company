# AREA 5 — RIGOR: Is the LIVE GUIDED experience achievable now, or where does it genuinely break?

**Role:** the skeptic. Try to break the anchor. Ground every doubt in evidence.
**Evidence marks:** Observed(file:line) = read directly in code/files · Inferred = pattern-match, NOT verified by run · External = prior art · Anchor-idea = the anchor's hope.
**Verification status of THIS area:** the company bridge + the 4B brain were **NOT running** during this review (Observed: `ps aux` shows only `mcp_face/server.py` + the orpheus voice engine up; `curl :8001/v1/models` empty — vLLM down; `:8000` is the project-vi gateway, returns `{"detail":"Not Found"}` for `/api/chat`, NOT the company bridge). So the make-or-break comprehension test (RHM explaining a mockup) is **Inferred from the code path, NOT live-Verified.** The exact test that would Verify it is given in §1. Per Tim's law, code-reading is not verification — every "READY" below means "the machinery is built and wired," not "I watched it work."

---

## THE HEADLINE VERDICT (read this first)

The anchor's instinct is **mostly right and far more built than it fears** on three of the five seams — but it **mis-locates its own make-or-break.** The anchor names "comprehension at altitude" as the crux. That seam is actually in good shape (the mockup's raw HTML is injected into the RHM context — a real, built mechanism). **The true make-or-break is GENERATE for mockups:**

> **The generate→build→git loop is BUILT for tweaking the LIVE running app, and UNBUILT for the redesign MOCKUPS — which are exactly what the commander opens and reviews.** There is no autonomous path that turns "talked-through changes to a proposed mockup screen" into an applied mockup edit. The mockup side has only a JSONL **note-capture** that a human-directed agent ("the lead") applies **by hand**, then manually flips to `applied`. So when the commander finishes a guided walk through `C3-build-review-desktop.html` and clicks "generate," there is **nothing that edits that mockup.** This is the gap that decides whether the surface delivers on its own promise.

Everything else ranges from READY to MODERATE. Details below, seam by seam.

---

## SEAM 1 — THE COMPREHENSION CRUX (the original failure)

**Anchor's fear:** `address_help` (suite.py:2213) only returns what's REGISTERED; redesign mockups are proposed surfaces NOT in the registry; so the RHM will confabulate or say "I can't see that."

**What I found — the fear is mostly answered, by a DIFFERENT mechanism than the anchor's §4 idea.**

The anchor's §4 idea ("`address_help` through `up_translate`") is the path for **live** elements. For **mockups** there is a separate, purpose-built path that **bypasses `address_help` entirely**: the raw mockup HTML is injected straight into the RHM's grounding block.

- **Observed (suite.py:2086-2125):** when `focus.selected` carries a `mockup://<file>` value, `_chat_context` reads the actual HTML file from `design/mockups/` (path-safe, realpath-contained, bare `<file>.html` only) and injects it under a `MOCKUP UNDER REVIEW` header that explicitly instructs the model: *"The operator does not read code — read this FOR them and explain, at a plain-language altitude, what this screen IS, what they are looking at, and what they could do here."*
- **Observed (suite.py:2090-2092):** the comment is explicit that the grounding rule otherwise REFUSES to answer about anything not in the live-state block — *"a filename alone would correctly draw 'I can't see that'."* So the design KNEW the confabulation risk and fed the real content to prevent it.
- **Observed (the mockup content is genuinely explainable):** `C3-build-review-desktop.html` is 17KB of semantic, plain-language HTML — text nodes like *"A build just completed"*, *"show me drops the new node here, placed & runnable"*, *"operator-only — an agent can never self-approve its own build"*. This is exactly the kind of content a 4B can paraphrase at altitude. (Observed via `grep -oE '>[^<]{8,}<'`.)

**The two real cracks in this seam (cite these — do NOT say "raw HTML solves it"):**

1. **The 14KB cap truncates real mockups.** Observed: the injection cap is `CAP = 14000` bytes (suite.py:2117), but `C3-build-review-desktop.html` is **17,309 bytes** (Observed via `wc -c`). The very mockup I inspected **overflows** — the RHM sees the first 14KB with a "[truncated]" marker (fail-loud-legible, suite.py:2118, so it's honest, not silently partial). The tail of a long screen is invisible. Several of the 23 mockups likely exceed 14KB. **Mitigation needed:** either raise the cap, or (the advisor's note in the code at 2113) build a light HTML→text extraction so 14KB carries more signal. MODERATE.
2. **Raw HTML is noisy.** It carries inline `<style>`, SVG path data, layout divs — tokens the model must wade through to find the meaning. The code comment (suite.py:2113) flags this as a deliberate bet ("the model reading raw HTML may be fine; only add cleaning IF a real test comes back junk"). **That real test has not been run** (see §0). A 4B on raw HTML *may* explain well or *may* fixate on markup. Inferred-risk, not Verified.

**Verdict on Seam 1: the mechanism is READY and the right shape; the QUALITY is Inferred (untested on the resident 4B) and bounded by a 14KB cap that the real corpus already exceeds.** Not the make-or-break the anchor feared, but a MODERATE polish (cap + maybe extraction + the live test).

**The Verify test (one read-only call, do this before trusting the verdict):**
```
company up --wait   # loads the 4B brain (GPU; respect the VRAM gotchas — evict orpheus first)
curl -X POST http://127.0.0.1:<bridge>/api/chat -d \
 '{"message":"What am I looking at? Explain plainly, I am not a developer.",
   "focus":{"selected":["mockup://C3-build-review-desktop.html"]}}'
```
Judge: does the reply describe the build-review screen in Tim's terms, or confabulate / fixate on markup? (I attempted this; the bridge + brain were down, so it is unrun.)

---

## SEAM 2 — LIVE + STREAMED + DEICTIC ("talks back," follows "this/here/that-before-this")

### 2a. Streamed text dialogue — MODERATE (smaller than the anchor implies, but real work)

- **Observed (StudioKit.tsx:220, useAppController.ts):** the studio chat is **request/response** — `sendChat → POST /api/chat`, returns the whole reply once (`jr` JSON read). It does NOT stream tokens.
- **Observed (suite.py:5264 `chat_parts`, bridge.py:734 `_voice_stream`, bridge.py:231 `_stream_parts`):** a STAGED, streamed reply generator **already exists** — but it is wired only to the **voice circuit** (`/api/voice/stream`), built for Concurrent Cognition (parts overlap brain↔TTS). The text chat does not consume it.
- **Observed (useAppController.ts:602 `/api/stream` SSE):** the only SSE the text UI consumes is the **event-log mirror** (telemetry: seq-deduped events), NOT streamed RHM reply text.

**Verdict:** the streaming ENGINE is built (`chat_parts`); the gap is a **text SSE endpoint that wraps `chat_parts` + a FE EventSource fold for the chat panel.** This is MODERATE (reuse, not net-new cognition) — the anchor's §4 idea ("the existing chat organ, streamed") is correct, and the streaming half is already proven on voice. NOT a "bigger model / bigger build."

### 2b. Voice-in — MORE READY than the anchor feared (flag this)

- **Observed (voice/AGENTS.md:16):** STT is a swappable registry (`voice/stt.py`) with `whisper.cpp` as the **boot default** (local HTTP :2022, zero-install, on-machine). Plus 3 GPU ears + cloud assemblyai. The active ear is a config slot like the brain. `available_stt()` is a live registry the UI/RHM reads.
- **Observed (bridge.py `/api/voice/stream`, `/api/voice/finished-thought`, `/api/voice/log`):** the full live voice loop (VAD, finished-thought judge, turn-fire, traced) is built and was the subject of the 2026-06-07 voice work.

**Verdict on voice-in: READY-ish** (the ears + the live loop exist). The anchor's "he might be talking" is well within reach — voice-in is one of the *strongest* parts, not a gap.

### 2c. Deictic + TEMPORAL grounding ("that thing that opened before THIS showed up") — HARD, the genuine fragile seam

This is where the anchor's hope is thinnest and the evidence agrees it's hard.

- **Spatial deixis ("THIS," "HERE") — BUILT:**
  - **Observed (suite.py:2126-2142):** a clicked `ui://` address arrives in `focus.selected`, is described into an `OPERATOR IS INDICATING` block, and **sets `self._current_locus = indicated[-1]`** (last-wins). So "this" resolves to the indicated element.
  - **Observed (StudioKit.tsx:101-111, bridge.py:440-459):** **in-mockup element deixis is BUILT** — the bridge injects a sandboxed click-capture script (on the `?studio=1` serving path only) that finds the nearest `data-ui-ref` ui:// address on a click inside the mockup and `postMessage`s it to the parent; the Stage re-indicates that element. **Observed: 18 of 23 mockups carry `data-ui-ref`** (e.g. C3 has `ui://inbox/build-review`, `ui://toolbar/run`). So clicking *inside* a staged mockup grounds "this" at a real element address. Strong, surprising, built.
- **TEMPORAL deixis ("that-before-this," the ORDER) — the crack:**
  - **Observed (StudioSeams.ts:86):** the FE itself flags — *"partially present (ui_target stamping + per-turn focus locus); a standing server-side current-locus is DESIGNED, ☐"* (☐ = unbuilt). The persistent across-turn locus the anchor's "that-before-this" relies on is **explicitly not built.**
  - **Observed (suite.py:2142):** `_current_locus` is an **in-memory** last-wins value, set per-indicate. It is the *current* point, not an ordered history.
  - **Inferred:** the raw material for "the order" exists — the event log (`events.jsonl`, addressed events) + R2's resolve-at-locus (`_resolve_context_at`, suite.py:2173) gather annotations/chats/events at the locus + ancestors, recency-ranked. But there is **no built mechanism that reifies "the thing that opened before this"** into a resolvable antecedent the model can point back to. The model would have to infer temporal order from a 6-event telemetry ticker (Observed: `_chat_context` carries `recent_events(6)`, suite.py:1990) — which STATE.md:39 itself flags as a weak, cross-thread mechanism.
  - **Inferred-risk on the 4B:** even with the order present in context, resolving a layered referring expression ("the thing that opened *before* THIS showed up") is a hard grounding task for a 4B. Untested.

**Verdict on Seam 2c: spatial "this/here" is READY (and in-mockup deixis is a genuine, built surprise); TEMPORAL "that-before-this" is HARD — the standing locus is flagged unbuilt, the antecedent-history is not reified, and the 4B's ability to resolve it is unverified.** This is the anchor's most aspirational claim. Recommend SCOPING it down: deliver "this/here" + a simple "the last few things you touched" list (derivable from the event log) before promising full ordered temporal deixis.

---

## SEAM 3 — THE RHM DRIVING THE VIEW (move + spotlight stop-by-stop)

**The most over-feared seam — it is largely BUILT, including on mockups.**

- **Observed (bridge.py:1248 `/api/guide/start` → suite.py `start_guide` → `present_current` C1 branch, suite.py:6207-6257):** a guided sequence is a review session whose ITEMS are `ui://` element addresses. Each step frames its narration from the CORPUS how-to via `address_help` (D1) and **is MODEL-FREE by construction** (suite.py:6212 — it returns before the `coa()` call). So the *tour narration* never depends on a flaky model; it reads the registry.
- **Observed (suite.py:6252, `_registry_ui_target` at 6161):** each step stamps a registry-valid `ui_target` into the payload the FE reads as `session.raw.ui_target` (G-43 fix — before this, payload-less items no-op'd the spotlight).
- **Observed (useAppController.ts:1469 `resolveUiTarget`, 1570 `spotlightUiRef`):** the FE keystone is REAL and complete — it validates the ui:// against the served registry (fail-loud on unknown), `querySelector('[data-ui-ref=…]')`, `scrollIntoView`, adds the `.ui-spotlight` ring (app.css:810), removes after 2.4s. NEXT/BACK step the session (`/api/review/next`, suite.py:6344). The presence-dial "walkthrough" mode is now bound to the real organ (suite.py:6287 `start_walkthrough`, closing the old "naming trap").
- **Observed (Toolbar.tsx:59):** there is a live "? guide" button wired to `startGuide()` — a reachable entry point exists.

**The cracks:**
1. **Observed (suite.py:6313-6316, `start_walkthrough` docstring):** the FE wiring that CALLS `walkthrough/start` on dial-select **and drives the per-step view** is flagged "DEFERRED … the view-drive is the FE half (would collide with the concurrent canvas/region lane)." So the *review-of-inbox-items* walk's FE drive is partially deferred — though `resolveUiTarget` itself (the sink) is built and the `guide` tour uses it.
2. **The spotlight targets LIVE DOM, not mockup-internal elements.** `resolveUiTarget` `querySelector`s the live app's `data-ui-ref`. A mockup is rendered in a **sandboxed iframe** (StudioKit.tsx:153). So "spotlight stop N inside the C3 mockup" is **NOT** the same path as spotlighting a live region — the in-mockup deixis goes the *other* direction (mockup→parent via postMessage, Seam 2c), and there is no built "parent drives a spotlight INTO the iframe" for a guided sequence over mockup-internal stops. Inferred: a guided walk *across whole mockup files* (load file N, narrate) is achievable with the existing Stage+corpus; a guided walk *to elements inside one mockup* would need new postMessage-in plumbing. MODERATE.

**Verdict on Seam 3: READY for guided walks over LIVE addressed elements (drive + spotlight + model-free narration + NEXT/BACK all built and wired); MODERATE for walks across mockup FILES; the in-mockup-element guided spotlight is a small net-new.** The anchor's "the RHM walks me through, stop by stop" is far less aspirational than it fears — for the live surface, it's essentially there.

---

## SEAM 4 — GENERATE RELIABILITY (compose approvable build-plans; one-click dispatch + git)

**This is the TRUE make-or-break, and it splits sharply LIVE-vs-MOCKUP.**

### 4a. The LIVE-app generate→build→git loop — READY (and the safety is real)

- **Observed (suite.py:6816 `surface_intent_at`):** a comment-at-an-address composes three existing pieces — `ingest_comment` (record the comment as the spec) + `resolve_scope` (ui://→code://→`scope[]`) + `surface_build_intent` (mint, awaiting approval). It STOPS at surfacing; dispatch is a separate switch (suite.py:6847).
- **Observed (suite.py:6835-6842):** **empty/stale scope = DENY-ALL** — if an address has no code symbol, `resolve_scope` returns an empty scope which the dispatch-time scope-diff treats as deny-everything, so the build can never close `implemented`. It *refuses* to fabricate a broad scope. This is a genuine safety property.
- **Observed (suite.py:7360 `dispatch_decision`; runtime/implement.py):** the wire (launch `claude -p` / verify / git-checkpoint) exists. Approval is OPERATOR-ONLY off the MCP face (suite.py:6844). Verdicts are read from the substrate (`review_verdicts`, suite.py) and bound three-part (kind=resolve·choice=approve·surfaced==sid) before a criterion commits (`commit_criterion`, suite.py:6649) — ungoverned commits raise `GovernanceError`.
- **Blast radius is computed at MINT time** (suite.py:6877 X16) so the operator sees what a change could reach BEFORE approving.

**Blast radius / failure rate, honestly:** the git net is real (revert exists, `/api/revert` → `revert_self_change`, bridge.py:1361). But "one-click-approve a BATCH" of build-intents composed from a messy talked-through sequence has real risk: (a) the **unit is one build-intent per marked-up address** (Observed: `surface_intent_at` is per-address), so a "batch" is N independent intents — the anchor's "approve the batch" needs a built batching+show-through step that I did **not** find as a single composed call (the pieces exist; the batch-compose-and-show is Inferred-unbuilt). (b) Each dispatched build is an autonomous `claude -p` that **commits to git** — DENY-ALL scoping bounds the blast to the address's code, and git revert recovers a bad build, but a *wrong-but-in-scope* build (does the wrong thing within the right files) is not caught by scope and lands a commit. The 4B isn't doing the build (claude -p is), so build quality ≠ resident-model quality — that's a relief. **Net: the live loop is READY mechanically; the "compose a coherent multi-stop batch + show-through + one approve" UX layer is the MODERATE missing piece, and the residual risk is wrong-but-in-scope builds, mitigated (not eliminated) by git revert.**

### 4b. The MOCKUP generate loop — UNBUILT (the make-or-break)

This is the gap the anchor's §3 line 72-73 *names the distinction for* but does not flag as unbuilt:

- **Observed (bridge.py:1533 `/api/mockup-feedback`):** capturing feedback on a mockup writes ONE JSONL line to `.feedback/<mockup>.jsonl` with `status:"pending"`. That's it — a note.
- **Observed (bridge.py:1564 `/api/mockup-feedback/status`):** the status flip to `applied`/`dismissed` is described as *"how the lead marks a note done **after editing the mockup**."* The EDIT is done by a human-directed agent out-of-band; there is **no autonomous mockup-edit dispatch.**
- **Observed (suite.py:7124):** `/api/mockup-feedback/status` is tagged `to_wire` — i.e. flagged as not-yet-fully-wired.
- **Observed (Review.tsx:14):** *"the /api/mockup-feedback jsonl is RETIRED for this in-app surface (the legacy standalone file may still use it)"* — so even the note-capture is in flux for the new in-app studio; the mockup-feedback substrate is being deprecated without a built replacement generate-path surfaced.

**So:** when the commander walks through a *redesign mockup* (which is what the detached studio dumped on him, and what this surface exists to make comprehensible), and says "I want this to come in from here" and clicks **generate** — there is **no built path that turns that into an edited mockup.** `surface_intent_at` would resolve_scope against the mockup's ui:// address → that address has no *implemented* code (it's a proposal) → DENY-ALL → nothing builds (correctly, per the safety property — you must NOT dispatch live code from a proposed surface). The mockup-iteration loop the anchor explicitly distinguishes is the part that is **not built.**

**Verdict on Seam 4: GENERATE is READY for tweaking the LIVE running app (mint→approve→dispatch→git→revert, governed, scope-bounded); the "compose+show+one-approve BATCH" UX is MODERATE; the MOCKUP-edit generate loop is the make-or-break GAP — it does not exist beyond manual JSONL notes, and that is the surface's own headline use case.**

---

## SEAM 5 — WHOLE-EXPERIENCE LATENCY / FEEL (does it feel live, or laggy?)

- **The resident brain (Observed, STATE.md:15):** a 4B model, co-resident at 64K context with 4-bit AWQ Orpheus voice on the 16GB card; judge bound to the resident 4B. Per Tim's memory note, production chat throughput was benchmarked ~2700 tok/s for a Qwen 4B-AWQ.
- **Inferred (cannot Verify — brain was down):** at ~2700 tok/s a short at-altitude explanation (say 80-150 tokens) is sub-second of *generation* — that part feels live. The risks to "feel":
  1. **Context-build cost per turn.** `_chat_context` (suite.py:1974) assembles a large grounding block every turn — live model registry reads, inbox lanes, R2 gather, AND (on a mockup turn) up to 14KB of injected HTML. The 4B at 64K must *prefill* all of it. A 14KB mockup + the standard grounding is a multi-thousand-token prefill **every turn** — prefill latency, not generation, is the likely "lag." Inferred-risk.
  2. **The streamed text path doesn't exist yet (Seam 2a)** — so today a text reply arrives all-at-once after the full prefill+generation, which *feels* laggier than a streaming reply even at the same total time. Wiring `chat_parts` to a text SSE (the Seam 2a build) is what makes it *feel* live (first words appear fast). The voice path already streams (so voice will feel more live than text until the text SSE lands).
  3. **Co-residence VRAM (Observed, memory + STATE.md:15):** the 4B + Orpheus co-reside at 64K only with 4-bit AWQ; bigger voices force a context shrink (bridge.py:1305-1322). And the memory notes flag a FlashInfer decode crash (→ TRITON_ATTN) and an EngineCore VRAM-orphan — operational gotchas that, if they bite, kill "live feel" entirely (a crashed turn). The orpheus engine was Observed squatting VRAM right now with the brain down.

**Verdict on Seam 5: generation latency is fine (Inferred from benchmarks); the FELT latency depends on (a) the unbuilt text-streaming path and (b) per-turn prefill of a heavy grounding block + up-to-14KB mockup HTML.** MODERATE: the text SSE is the single highest-leverage change for "feel." HARD-watch: the VRAM/crash gotchas can turn "live" into "dead turn" — these are operational, not architectural.

---

## CONSOLIDATED RATING

| Seam | Anchor's framing | Honest verdict |
|---|---|---|
| 1 · Comprehension of mockups | "the crux / make-or-break" | **READY mechanism (raw-HTML injection, built), MODERATE quality** — 14KB cap already exceeded by real mockups (C3=17KB); 4B-on-raw-HTML quality **Inferred, untested**. Not the crux it feared. |
| 2a · Streamed text dialogue | "small path from req/resp" | **MODERATE** — streaming engine (`chat_parts`) built but voice-only; needs a text SSE + FE fold. |
| 2b · Voice-in | "likely in-scope" | **READY-ish** — whisper.cpp STT default + full live voice loop built. *Stronger than feared.* |
| 2c · Deictic / temporal | "achievable?" | spatial this/here **READY** (+ in-mockup deixis built, a surprise); **temporal "that-before-this" HARD** — standing locus flagged ☐ unbuilt, antecedent-history not reified, 4B unverified. |
| 3 · RHM driving the view | "aspirational?" | **READY for live elements** (drive+spotlight+model-free narration+NEXT/BACK all built/wired); MODERATE across mockup files; small net-new for in-mockup-element spotlight. *Far less aspirational than feared.* |
| 4a · Generate (LIVE app) | "how reliable?" | **READY + governed + git-safe**; batch-compose-and-show-through is MODERATE; residual risk = wrong-but-in-scope builds (git revert mitigates). |
| 4b · Generate (MOCKUPS) | distinguished, not flagged | **THE MAKE-OR-BREAK GAP — UNBUILT.** Only manual JSONL notes + hand-editing; no autonomous mockup-edit path; substrate being retired (Review.tsx:14) without a built replacement. |
| 5 · Latency / feel | "live or laggy?" | generation fine (Inferred); FELT-live needs the text-SSE (2a) + bounded prefill; VRAM/crash gotchas are the operational HARD-watch. |

## THE ONE THING THAT DECIDES BUILDABILITY-NOW

**The surface is buildable now AS A LIVE-APP review-and-tweak instrument** — nearly every piece for "walk me through the running Company, explain each part at my altitude, comment, generate a change, approve, it builds + commits + reverts" is built or a MODERATE reuse. That is genuinely close.

**It is NOT yet buildable as the thing the anchor's own story demands** — *making the redesign MOCKUPS comprehensible and actionable* — because the **mockup-side generate loop does not exist.** The commander can be *walked through and have a mockup explained* (Seam 1, READY-ish), and he can *comment* on it (note-capture), but when he clicks **generate** on a mockup there is no autonomous path that produces an edited design. Comprehension without actionability is half the kill — and it's the design-iteration half, the one that originally failed him.

**Recommendation (sharpening, not closing):** treat the surface as TWO loops sharing one room, and build them honestly distinct (the anchor's own §3 distinction, made real):
- **Live loop — READY now:** guided walk over live `ui://` elements → comment → `surface_intent_at` → approve → `dispatch_decision` → git. Add the text-SSE (feel) + the batch-compose-and-show UX. Ship this first; it works.
- **Mockup loop — the net-new build:** define what "generate on a mockup" *dispatches* — a `claude -p` that EDITS the HTML file in `design/mockups/` (scope = the mockup file, not live code), verified by re-render/screenshot, committed to git, revertible. This is the missing piece; it is buildable (the wire, git, and the mockup-feedback substrate scaffold all exist to compose from) but it is **net-new and is the gate** on the surface delivering its founding promise.

Before committing to ANY rating above as fact, run the §1 Verify test on the live 4B — the comprehension verdict is the one claim most worth turning from Inferred to Verified, and it was unrunnable here (bridge + brain down).
