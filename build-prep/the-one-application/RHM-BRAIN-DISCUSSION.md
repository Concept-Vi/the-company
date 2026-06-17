# The Right-Hand-Man BRAIN — Grounded Synthesis

*Mined 2026-06-17 from the lead transcript (`bda8ce28…jsonl`) + build-prep + memory. Read-only mine; Company MCP was down — Grep/Read/Bash on files only. Evidence is labelled **Observed** (seen in code/files), **Inferred** (pattern-match, unverified), **Verified** (status-log records use-verification). Provisional — Tim is the judge of "right." Verify each file:line before building on it.*

---

## 0 · WHAT THE RHM-BRAIN IS

The **right-hand-man brain** is the **inbuilt Claude Code**, bound at an **address**, that the operator talks to and clicks to direct. It is *one persistent loadable brain present on every page*, whose **context is whatever the V is currently aimed at** (a page/surface by default; an element's address when the operator drills into one). The operator never sees code, files, or machine names — only human MEANING; the address rides server-side as the brain's context handle.

Tim's compressed description of what it does: **"go to MODES · SELECT things · TALK · CLICK-ask for updates/changes · with CONTEXT + the RESOLUTIONS."** Decompressed below — each leg mapped to built code or to a named spec, honestly.

**Tim's verbatim (line 5307, Tim's own words):**
> "if you look at the right hand man, every capability through the UI is also accessible through the right hand man, it can change everything about the screen everything that's on the screen can move me around places It should be able to do a follow me mode and another where I follow it, and it can set things up for me and the context resolution and the address space... I wonder if and how claude could 'plug in' to the company, pilot the right hand man. there is a lot to that, the right hand man, and most of it hasn't been built and it's not in any use It's still being built but it has such high value potential..."

> ⚠️ **Provenance caution (advisor-caught):** the phrasing *"Claude Code as a 'loadable brain' (click an element → talk to CC about it)"* appears in transcript lines 8403 / 26156 etc. — but those lines OPEN with *"This session is being continued from a previous conversation…"*, i.e. they are **Claude's compaction summaries injected as user-role messages, NOT Tim's verbatim.** "Loadable brain" is the *fabric's working term* (it names fork's role + the JS modules), faithfully derived from Tim's intent, but it is not a quote from Tim. Tim's actual coinages are **"plug in / pilot the right hand man"** (5307) and the **N+1 / "so many minds But possible for one"** passage (5418).

---

## 1 · THE INTERACTION SET (MODES · SELECT · TALK · CLICK-ASK · CONTEXT · RESOLUTIONS)

### MODES — *which mind/cast is active*
Tim's primary sense of "mode" here is **which MIND is loaded behind the V** — Claude Code is *one interchangeable mind among many*, swappable as an extension of the mode system. **DESIGNED-ONLY.**

**Tim's verbatim (line 5418, Tim's own words):**
> "I feel like there could be multiple sessions as cognition or just one and having the local instant And using that N + 1 design of mine is awesome for different uses. and I don't actually think that is any extra work… because it's effectively the same mechanism. Clawed code is just one of an interchangeable composition. So many minds But possible for one. And I'm sure I'd be able to swap between all of those, as an extension to the mode system or something similar."

To avoid conflation, three **lower, already-built** senses of "mode" exist and must NOT be read as this:
- **The 6-verb fan** (RightHand.tsx `VERBS`: navigate/ask/annotate/drive/open-source/generate) — **BUILT** (shell; only `ask` wired).
- **8 modes-as-nodes** (RHM v1: off disables the model with no call; presence dial) — **BUILT** (rhm-v1 suites green).
- **mode-as-cascade** (DNA: the V moves ONE anchor → `DNA.injectVars` re-tints the whole app) — **BUILT** (GROUNDED-MAP).

The MIND-selection mode (Claude Code ↔ other models ↔ N+1 concurrent sessions, swap per use) is the part Tim named and is **not built** — it is the natural extension once the brain seam is one interchangeable composition.

### SELECT — *drill / address an element*
The operator selects a unit; the surface emits `projection:select {address|source}`; the V's host re-aims the brain at that addressed element. **BUILT.** RightHand.tsx:84-106 listens for `projection:select`, sets `aimRef.current` to the address, and fetches its human label.

### TALK — *the Ask-Claude-Code leg*  ✅ **BUILT + VERIFIED-BY-USE**
Tap the V → "Ask" → a paper talk panel where the operator talks to **real Claude Code** about the current aim; the reply STREAMS in. This is the live half of the circuit.
- Frontend: `RightHand.tsx` mounts `forkVBrain.attach({panelEl, getAimAddress, getAimLabel})` (line 62).
- Engine: `fork-brain-core.js` `talk()` POSTs `/api/claude/turn`, parses the NDJSON stream `{init|text|tool|done|error}`, keeps **per-address session continuity** (`_sessions[address]` → `--resume`).
- **Verified:** status-log commit `c93c6ef` — a real Claude Code reply streamed into the V panel at 390px + 1440px, 0 console errors. Scripts are loaded: `surface/app/index.html:33-35` loads `fork-brain-core.js` then `fork-v-brain.js`; files in `public/gallery/`.

### CLICK-ASK — *click an element → ask it to update/change*  (TWO HALVES — keep honest)
Tim's words: *"CLICK-ask for updates/changes."* This has two halves:
- **RECORD/MARK half** ✅ **BUILT.** `forkBrainCore.writeDirections()` batches a direction by `element_id` → `POST /api/territory/write` → `suite.mark` → emits `gallery:rerender`. `fork-v-brain.js` `direct(item)` routes a direction back at the current aim. Verified per GROUNDED-MAP (3 mark_types round-trip).
- **CHANGE/GENERATE half** 🔴 **DESIGNED-ONLY — THE KEYSTONE.** "ask it to update/**change**" means the brain READS the direction → GENERATES/mutates → WRITES the *output* to the registry. Today it only RECORDS a mark. This one router step is `SPEC-direction-to-generate-wire.md` — *the ONE unbuilt rung.* **This same unbuilt rung IS the composition seam (§4).**

### CONTEXT — *how resolved context/territory feeds the brain*  ✅ **BUILT**
Before each turn, the server composes the brain's context from the aim address. `bridge.py:1696-1697` calls `from runtime.territory import territory_prose; ctx = territory_prose(address, suite=SUITE)`. `territory.py:152` `territory_prose` resolves any scheme (run://·code://·ui://) into an `[Operator context]` prose block and **never raises** (outer guard degrades to a note — "context-gathering never kills the turn", territory.py:23-24). `territory_for` (territory.py:40) assembles the territory dict (record + relations).

### RESOLUTIONS — *resolve_address / territory feeding + the write-back*  ✅ **BUILT (read+write); 🔴 generate-write DESIGNED-ONLY**
"The resolutions" = the resolved territory the brain reads + the route-back it writes. One resolver, no parallel path:
- **Read:** `runtime/cognition.py:842` `resolve_address(store, addr, …)` (16-scheme) is the single resolver `territory_for`/`territory_prose` build on.
- **Write-back (record):** `territory.py:266` `territory_write(element_id, item, suite=…)` ← `POST /api/territory/write` (bridge.py:2552) → `suite.mark`. **BUILT.**
- **Write-back (generated output):** the keystone payload-kind (`kind=generated|mutation`) is the **NEW** write — **DESIGNED-ONLY.**

---

## 2 · THE WIRING (file refs / line anchors — Observed)

```
operator taps V → "Ask"  ──────────────────────────────────────────────  RightHand.tsx onVerb('ask') → panelOpen
  │                                                                        (other 5 verbs emit window 'rhm:verb', l.163 — SEAMS)
  ▼
forkVBrain.attach({panelEl, getAimAddress, getAimLabel})  ──────────────  RightHand.tsx:62  ·  fork-v-brain.js:30  (host owns AIM; fork owns turn)
  │   aim follows projection:select (l.84-106); default ui://instrument/surface (l.29)
  ▼
core.talk(replyEl, aimAddress, prompt)  ───────────────────────────────  fork-brain-core.js:29  (per-address session continuity, l.36/52)
  │
  ▼
POST /api/claude/turn {prompt, address, session_id?}  ─────────────────  bridge.py:2067 → _claude_stream (bridge.py:1644)
  │   ctx = territory_prose(address, suite=SUITE)  ──────────────────────  bridge.py:1696-1697 → territory.py:152
  │       territory_prose → territory_for → resolve_address  ────────────  territory.py:40 → cognition.py:842  (16-scheme; never raises)
  │   PANEL_BRIEFING forbids raw addresses/scheme:// in replies  ────────  runtime/ui_claude_session.py  (operator-law fix, status-log c93c6ef)
  ▼
NDJSON stream {init|text|tool|done|error} → streamed reply in .v-brain   fork-brain-core.js:43-58
  │   human aim label (never the raw address):  GET /api/territory/label  RightHand.tsx:88 → bridge.py:1296 → territory.py:238
  ▼
── WRITE-BACK ──
RECORD (built):  direct(item)/writeDirections → POST /api/territory/write → suite.mark → 'gallery:rerender'
                 fork-v-brain.js:78 · fork-brain-core.js:75 · bridge.py:2552 · territory.py:266
GENERATE (designed-only, KEYSTONE):  if item is generative → run_turn(ctx=territory_prose(addr), instr=text)
                 → POST /api/territory/write(kind=generated) → re-render shimmer→solid
                 SPEC-direction-to-generate-wire.md  ("the ONE new connection — a ~1-function router")
```

**Mode/cast selection:** the brain is REAL Claude Code via `_claude_stream` (subprocess, `--resume`). The MIND is swappable in principle (Tim's N+1 / interchangeable composition) but the swap-the-mind UI is DESIGNED-ONLY. Per-aim continuity is automatic — each aim address is its own conversation thread (`_sessions[address]`).

**Re-render:** `gallery:rerender` event (fork-brain-core.js:87) + DNA `injectVars` live var-injection (GROUNDED-MAP) — change the registry → the surface re-renders.

---

## 3 · WHAT'S BUILT vs DESIGNED-ONLY (honest)

| Leg | State | Evidence |
|---|---|---|
| V overlay shell (bottom-right, draggable, persisted, every page, 6-verb radial fan) | ✅ BUILT + verified | RightHand.tsx; App.tsx:346; status-log commit `3ac24f3` (fresh-eyes critic PASS, 390+1440) |
| TALK leg — Ask Claude Code, streamed, per-aim context | ✅ BUILT + verified-by-use | fork-*.js + bridge `_claude_stream`; commit `c93c6ef` |
| SELECT / re-aim (`projection:select` → re-aim brain) | ✅ BUILT | RightHand.tsx:84-106 |
| CONTEXT feed (`territory_prose` at any scheme, never raises) | ✅ BUILT | territory.py:152; bridge.py:1696 |
| Human aim-label (operator never sees address) | ✅ BUILT | bridge.py:1296; territory.py:238; PANEL_BRIEFING leak-fix |
| CLICK-ASK **record** half (mark → write → rerender) | ✅ BUILT | fork-brain-core.js:75; bridge.py:2552; territory.py:266 |
| CLICK-ASK **change/generate** half (the KEYSTONE) | 🔴 DESIGNED-ONLY | SPEC-direction-to-generate-wire.md — "the ONE unbuilt rung" |
| MODES = swap the MIND (Claude ↔ models ↔ N+1) | 🔴 DESIGNED-ONLY | Tim 5418; brain seam is one interchangeable composition |
| Other 5 verbs (navigate/note/drive/source/make) → backends | 🔴 SEAM stubs | RightHand.tsx:163 emit `rhm:verb`; no backends wired |
| Follow-me mode (bidirectional) · Piggy-back mode | 🔴 DESIGNED-ONLY | Tim 5307 + 5418 (piggy-back "not described or designed anywhere yet") |
| Tutorial (RHM walks the operator) · legibility meaning-layer | 🔴 GATED on design | OPERATOR-SURFACE-LOOP Phase 3; `legibility.js resolveLegibility` built, not wired live |
| Real V *organism* (vs the gold-icon placeholder) | 🔴 SWAP SEAM open | composition owns it; renders into the RightHand container |

**Net:** the read+talk circuit is LIVE and use-verified; the V shell is built; the write-back exists for *records*. The **generate/change half, the mind-swap modes, and the other 5 verbs are designed-only.** No green-paint: the verb actions other than Ask emit a seam event and do nothing yet.

---

## 4 · THE SEAM FOR COMPOSITION (ch-2mnxl9j0) — build INTO, not parallel

Composition's factory ("generate assets WITH the AI") is **not a parallel system — it is the keystone's GENERATE-step retargeted at composition's own address scheme.** Universal composition: *one circuit, retargeted by address.*

```
gallery:direction {element_id = vi-vision://…, type=generate, text="…"}     ← wildcard emit (built)
   │  generative intent
   ▼
run_turn( context = territory_prose(vi-vision://addr), instruction = text )  ← THE ONE BRAIN TURN (fork-brain-core / /api/claude/turn)
   │  brain output = a component / asset / slot mutation
   ▼
POST /api/territory/write( address = vi-vision://addr, payload, kind=generated )  ← KEYSTONE write (designed)
   │
   ▼
re-render at the slot/catalog registry  → shimmer→solid
```

Concretely, for composition to plug in (and NOT build parallel):
1. **Expose the slot/catalog registry as an addressed write-target.** Make composition's component/catalog registry resolvable via `resolve_address` (a `vi-vision://` scheme) and writable via `territory_write` — so the keystone's generated output lands in the component registry, not a bespoke store. (Per SPEC-direction-to-generate-wire.md per-surface table: composition = `vi-vision://` → slot/catalog registry.)
2. **Route generation through the ONE brain turn** (`run_turn` / `/api/claude/turn`) — do NOT spin a second streamer. The capable judge-tier brain (model-routing-unification #71) does the generate-step; the local 4B is the extractor, not the generator (extraction-vs-judgment).
3. **Swap the real V component into the RightHand container** via the existing seam: composition's V organism renders into the `vhandle` / `v-brain-panel` container; it consumes the `rhm:verb` window event and calls `forkVBrain.attach` for the brain. **Meet at the data — no cross-repo code import** (RightHand.tsx:11-13). The gold `v-icon.svg` is the placeholder; the swap seam is already in place.
4. **The "generate" verb** in the V fan (RightHand.tsx VERBS `{id:'generate', label:'Make'}`) is composition's entry point — it currently emits `rhm:verb`; composition wires it to the keystone generate-write at the current aim.

Once (1)–(3) land, "Tim clicks an element → tells the V to make/change it → composition's factory generates → it's written to the addressed component registry → the surface re-renders" is the SAME circuit as the gallery's record-leg, just a different address. That is the whole point: build into the one wire.

---

## 5 · OPEN QUESTIONS surfaced (not answered here)
- The keystone's resolved sub-decisions (record-ALSO vs replace; async shimmer; which mark_types are generative) live in SPEC + GROUNDED-MAP; composition should confirm `vi-vision://` is the right write-target scheme + emit `gallery:rendered` so the binder walks its surfaces.
- MIND-swap modes (N+1 / Claude ↔ models) — Tim wants it "as an extension to the mode system"; no mechanism named yet beyond "same mechanism, interchangeable composition."
- Follow-me + piggy-back modes are Tim-designed but unspecced (piggy-back explicitly "not described or designed anywhere yet" — 5418).
