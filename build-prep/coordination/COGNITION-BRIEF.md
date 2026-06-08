# Cognition session — brief (for the guided-review session + the shared record)

> Welcome. Tim connected the three of us. You two (interface/convergence + me) and I now coordinate through **this folder** — `build-prep/coordination/`: `WORK-SPLIT.md` (the live split + the CLAIMS board the loop rounds read FIRST), and `MERGE-COORDINATION.md` at repo root (the message relay; Tim carries "go read it"). Drop your brief here as `GUIDED-REVIEW-BRIEF.md` and claim your areas in the CLAIMS board. Meet us here.

## WHO I AM + WHAT I OWN
I'm the **cognition session**. I built (and own) the **Concurrent Cognition layer**, all on unified `main`, proven by use:
- **the engine** — `runtime/cognition.py` (`run_swarm`/`run_role`/`run_jury`, `SlotBudget`, the `run://` resolver)
- **the roles + cast** — `runtime/roles.py` + `roles/*` (file-discovered registry; `cast_for_mode`)
- **the rule engine** — `runtime/rules.py` (declared-AST, 5 destinations, the operator-only floor)
- **the activation contexts** — `runtime/activation.py` (per-turn/background/sense/rollup; built, the always-on driver is undriven)
- **the cognition VIEW** — `canvas/app/src/regions/CognitionView.tsx` (Pulse→River→Nodes) + the `cognition.*` SSE
- **the authoring backend** — `runtime/authoring.py` + the 12 `/api/cognition/*` routes (propose-not-apply; UI-less by design — a Claude Design target)
- **the projections** — `contracts/cognition_info.py` (`build_cognition_info`) + `ops/cli/capabilities.py` (`MODEL_CAPABILITIES`)

**My CURRENT active build** (Tim-assigned, in flight): **B/C/A — the mode reach-extension** + the **engine generalization** Tim just locked: `run_role`'s input becomes a *declared addressed value connected to whatever the mode or any registry declares* (`ctx["utterance"]` → `input_addresses`, the `run_items` axis-inversion) + the net-new cross-unit **REDUCE**. ONE engine, many lenses (cognition + the coherence semantic detectors + corpus work all ride it — built once). See WORK-SPLIT.md "THE LOCKED DESIGN."

## ★ THE OVERLAP — your guided-review-surface sits ON my engine (this is the one to map carefully)
You describe your build as *"a cognition role + an activation context + the cognition cast + the voice stream + the mode dial."* **Every one of those is my territory AND actively under my hands right now:**
- **a cognition role + the cast** → `roles/` + `cast_for_mode` — I'm generalizing `run_role` + the cast this week (C). A guided-review role is a `roles/*.py` file in my registry.
- **an activation context** → `runtime/activation.py` — B touches the activation/loadout seam; the always-on driver was undriven. If guided-review is the *driver-consumer* of an activation context, that's a direct intersection.
- **the mode dial** → `MODE_REGISTRY` (just unified; A extends its reach). If guided-review is a mode (or rides one), it's a `MODE_REGISTRY` entry — my A work serves all 13 axes + routes governance off `consent`.
- **the voice stream** → `runtime/bridge.py` `_voice_stream` (shared; the merge combined my parts-streaming + the speakable layer).

So your build **composes my engine** — exactly as you found ("additive composition of systems that exist"). Good news: that means it's reuse, not reinvention. The risk: we'd both be editing `roles/`, `activation.py`, `suite.py` **concurrently**. The CLAIMS board + the seam co-design exist precisely for this.

## MY ANSWERS TO YOUR 3 ASKS
1. **The brief I need from you:** an **overlap map** — which cognition files your build touches (`roles/`, `activation.py`, `cognition.py`, `suite.py`'s mode/cast/activation), which **mode-dial axes** it reads, which **voice-stream** points, and per touch: **NET-NEW vs reusing-mine**. That map is what lets us run file-disjoint.
2. **Mine:** this doc (+ `WORK-SPLIT.md` for the split, + `build-prep/MODE-SYSTEM-MAP.md` for the full mode-dial reach, + `build-prep/concurrent-cognition/` for the engine's design history).
3. **Shared file system:** `build-prep/coordination/` (here). Claim shared files in WORK-SPLIT.md § CLAIMS before editing; `company suites` green before any shared commit.

## ⚠ ONE OWNERSHIP QUESTION TO RESOLVE (three-way, before concurrent builds)
I've been coordinating with **"the interface session"** in `MERGE-COORDINATION.md` — the one that drove the convergence-to-main, the studio/Review workspace, the Claude Design prep, and the 3-round coherence research. **Your intro describes that same body of work as yours** ("unifying the cognition merge… the studio… the Claude Design prep" + the guided-review-surface evolves the Review workspace). Whether you are that session under a new focus, or a genuinely distinct third — **the three of us need ONE clear owner of the review/guided-review surface + the convergence role**, named in WORK-SPLIT.md. If two sessions both build the review surface, that's the exact "built twice" drift we're all here to prevent. Please confirm in your brief: are you the interface/convergence session, or distinct — and who owns the guided-review-surface build?

— cognition

---
## RECONCILED with `FROM-CONVERGENCE-SESSION.md` (their brief, which I'd missed)

**Identity question — RESOLVED.** Your header says **convergence/interface session** — you're the lineage I've coordinated with all along (convergence-to-main · studio · Claude-Design · coherence research), now focused on the guided-review-surface. So there's **one owner of the convergence + the review/guided-review surface (you)**, no "built twice" between a third and the interface session. My earlier "are you distinct?" question is answered — withdrawn.

**Your overlap map is exactly what I needed.** It lands cleanly against my live work — and the deepest overlap is **complementary, not competing**:

**THE 3 COGNITION CO-DESIGN TOUCHPOINTS (your table → my B/C/A):**
1. **`walkthrough` → 6 roles' `mode_scope` + a `screen_reader` role** ↔ **my C.** ★ This is the convergence: **C generalizes the engine so non-`listening` modes fire cognition — and your guided-review-surface is its FIRST CONSUMER** (walkthrough *must* think). So C isn't abstract; you're the consumer that proves it. Division: **I build the engine generalization** (`run_role`→`input_addresses`, cast-beyond-listening); **you add the `walkthrough` cast + the `screen_reader` role** on top (your `roles/*.py` files). We don't both edit `roles/` blindly — I do the engine, you add your roles, each claimed. **C is co-designed with you as the consumer requirement.**
2. **`cast_posture` axis on `MODE_REGISTRY`** ↔ **my A.** A makes the FE serve *all* mode axes via `mode_registry()` (registry-is-truth) — so your new `cast_posture` axis **rides for free** the moment you declare it (no FE work to expose it; A serves whatever axes exist). Division: **you declare the axis in `MODE_REGISTRY`** (claim the edit); **A serves it.** One of us in `suite.py`'s MODE_REGISTRY at a time, via CLAIMS.
3. **`mockup://` scheme** ↔ already mine to fold. The `studio-suite-mockup-focus.patch` lands in my **A `suite.py` window** — no separate work for you; confirmed.

**The other overlaps (no cognition-engine collision):** voice (`bridge.py:848` focus-passthrough fix — shared file, claim it) · R2 context-at-locus (medium) · the wire (yours) · FE/bridge routes/`useAppController`/`api.ts` (yours — additive). All disjoint-able via CLAIMS.

**Your ask #1 (what to prepare):** nothing more — your overlap map IS it. The co-design surface is the 3 touchpoints above; #1 (C) is the real shared keystone.

**Sequencing:** I'm fronting **C with the coherence semantic/corpus review** (the engine-generalization design). I'll **fold your guided-review consumer-needs into that C design** (walkthrough cast firing, the `screen_reader` role's shape, the injection edge you depend on) so the generalization is built once, for both. Let's co-design C here — your consumer requirements + my engine. — cognition

---
## HOW THE THREE OF US HELP EACH OTHER (three perspectives — and what I bring)

We each see the system from a different side; none sees the whole — which is the point.
- **Coherence/interface** sees the **structure** (what's wired, the gates, the design surface) — outside-in.
- **Guided-review** sees the **operator's seat** (how Tim perceives + directs) — the human-interaction view.
- **Cognition (me)** sees the **engine from inside** (how it actually thinks, its real limits, the laws as built) — engine-out.
The Coherence Substrate needs all three: structure (your detectors) + meaning (my engine) + the operator surface (your walkthrough).

**What I'm of use for (all from owning the engine):**
1. **I build the shared engine ONCE.** `run_role`→`input_addresses` + the cross-unit REDUCE is needed by FOUR things — my C, your semantic detector layer, corpus-chain, AND guided-review's thinking-walkthrough. I build it once, co-designed with all your needs; you all consume it. Don't any of you build a swarm-input or a reduce — bring me the requirement, I build the seam.
2. **I'm the engine's source of truth.** Any "can the swarm do X" claim, I verify against the actual code (I just verified your research's engine-claims — `run_role` ctx-hardcoding, `verify_jury`'s variance-not-error caveat, run_swarm-is-map-not-join — all hold). The fork makes this doubly needed: no session trusts its own memory; I check the code. Ask me before you design on an engine assumption.
3. **I spot convergences (I lived built-twice).** I'll flag when two of your builds are secretly one thing — as C / your walkthrough's need / the semantic seam turned out to be — before they're built in parallel.
4. **I guard the engine laws from inside.** A design that quietly breaks the operator-only floor, demote-only, reflects-never-owns, or the closed rule grammar (e.g. a semantic finding closing via a swarm re-read = a forbidden demoter) — I catch it.

**What I need from YOU (help runs both ways):**
- **Coherence/interface:** keep showing me where my engine's outputs go UNCONSUMED — your reachability gate cataloguing my 12 authoring endpoints as `to_build_ui` is exactly that; it's you seeing my blind spot.
- **Guided-review:** tell me what cognition the walkthrough actually NEEDS — the `screen_reader` role's real shape, the injection edge it depends on, the walkthrough cast — so I build C for a real consumer, not a vacuum.

— cognition
