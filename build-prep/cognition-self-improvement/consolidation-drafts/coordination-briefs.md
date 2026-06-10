# Consolidation draft — coordination-briefs lane

**Overlap members:**
- `build-prep/coordination/COGNITION-BRIEF.md` (signed "— cognition", 3 dated sections)
- `build-prep/coordination/GUIDED-REVIEW-BRIEF.md` (signed "— guided-review session")

**Drafted by:** consolidation-drafter subagent, 2026-06-10. Proposed only — nothing executed, no source file touched.

---

## VERDICT: KEEP SEPARATE — BY DESIGN. Do not consolidate.

This is a complete deliverable per the lane's charter: the honest judgment is that merging these two files would be wrong, and would actively damage the coordination protocol they implement. The reasoning follows in full, then the one small real action the owning sessions could consider, then the disposition table.

---

## RATIONALE

### 1. What these files actually ARE: correspondence, not documentation

These are not two documents describing one system. They are **two halves of a handshake between two distinct live work-lanes** (the cognition session and the guided-review session), exchanged through the shared folder `build-prep/coordination/` per the protocol stated in COGNITION-BRIEF.md line 3 ("Drop your brief here as `GUIDED-REVIEW-BRIEF.md` and claim your areas in the CLAIMS board") and honored by GUIDED-REVIEW-BRIEF.md's header ("This brief + my files-touched map + my cognition-consumer-requirements are the inputs you both asked for").

Each file is **authored, signed, and owned by a different session**:
- COGNITION-BRIEF.md is the cognition session's voice — its identity, its file inventory, its live B/C/A build, its asks, its offers.
- GUIDED-REVIEW-BRIEF.md is the guided-review session's reply — its fork-identity declaration, its files-touched map, its consumer requirements for C, its agreements.

Merging them produces a third document **no session owns or signs** — destroying exactly the authorship/provenance the protocol depends on. The folder's structure (COGNITION-BRIEF, COHERENCE-BRIEF, GUIDED-REVIEW-BRIEF, FROM-CONVERGENCE-SESSION — one brief per voice) is the design, explicitly directed by WORK-SPLIT.md line 66: "`GUIDED-REVIEW-BRIEF.md` — (guided-review session: write here…)". One-brief-per-session IS the filing scheme.

### 2. The "duplicated system-context" is the error-detection mechanism, not redundancy

The overlapping content (the three co-design touchpoints, the `bridge.py:848` voice point, the CLAIMS agreements, who-owns-what) appears in both files because **each session restating the split in its own words is HOW the protocol verifies mutual understanding**. Evidence that this redundancy does real work:

- The fork **duplicated ownership memory** between the interface and guided-review sessions (WORK-SPLIT.md CORRECTION, 2026-06-08: "A fork duplicated the memory of 'what I built / own' — so no session can trust its own recollection of ownership"). Per-session restatement is what surfaced that: COGNITION-BRIEF's "⚠ ONE OWNERSHIP QUESTION" section caught the ambiguity precisely because two voices described the same body of work as theirs.
- The handshake's value is in the **deltas between restatements**: cognition asked "are you the interface session or a third?"; guided-review's brief answered "a fork of the interface lineage"; Tim's CORRECTION then overrode cognition's own reconciliation ("Ownership resolved above is WITHDRAWN — it is NOT one owner"). That sequence — question, answer, withdrawal, correction — is only legible because each statement is preserved in its author's file with its author's signature. A consolidated single-source-of-truth would have flattened this into one assertion and erased the disagreement that needed resolving.
- GUIDED-REVIEW-BRIEF's restatements are explicit **confirmations**, not copies: "Confirmed for coherence: my build does not write your gate files"; "The headline I fully accept: don't build a swarm-input… I bring the requirement, you build the C seam once, I consume it." Confirmation requires a second voice saying the thing — that's the duplication.

### 3. The consolidation that COULD be argued for has ALREADY happened, in the right place

The genuine single-source-of-truth for the agreement-substance is **WORK-SPLIT.md** — and both briefs explicitly subordinate themselves to it:

- GUIDED-REVIEW-BRIEF Agreements: "**CLAIMS board is authoritative over memory**… I check here, not recall."
- WORK-SPLIT.md ratified truth ladder (lines 174–180, ratified by all three sessions: cognition 374b272 · guided-review · coherence): "live gates > git history > claims board > memory. Rightmost wins on conflict."

And WORK-SPLIT.md already carries every binding item the two briefs negotiated (verified by direct read, 2026-06-10):

| Agreement item | In COGNITION-BRIEF | In GUIDED-REVIEW-BRIEF | Already consolidated in WORK-SPLIT.md |
|---|---|---|---|
| C engine-seam division (cognition builds `run_role`→`input_addresses`; guided-review adds `walkthrough` cast + `screen_reader` role on top) | RECONCILED §, touchpoint 1 | files-touched row 7 + consumer-req 1/3 | lines 73–74, § CLAIMS C 1/4–3/4 |
| `cast_posture` axis (guided-review declares; cognition's A serves) | touchpoint 2 | files-touched row 5 + consumer-req 3 | line 75, § GUIDED-REVIEW line 106 |
| `mockup://` folds into cognition's A `suite.py` window | touchpoint 3 | files-touched row 6 ("HANDED TO COGNITION") | line 76, line 109 |
| voice `bridge.py:848` focus-passthrough = guided-review's, disjoint | "other overlaps" ¶ | files-touched row 4 | line 77 |
| Hold `cognition.py`/`roles.py` until C releases | § CLAIMS protocol | Agreements bullet 2 | § CLAIMS C 1/4 ("Other sessions: hold…") |
| Claims-board-over-memory; one driver per shared file; `company suites` green pre-commit | brief ask 3 | Agreements bullets 1, 3 | CORRECTION rule 1 + ratified rules 2–3 |
| Forward-owner of review surface + FE + wire = guided-review | (question raised, then withdrawn) | Identity + forward-ownership § | § GUIDED-REVIEW line 98 (the settled answer) |

So a consolidation pass here would be **re-consolidating into a second place** what the live board already holds — creating a competing source of truth below the board on its own ratified ladder. That is the opposite of the no-versioning / one-canonical-surface law.

### 4. Lifecycle: these briefs are append-only dated records, not maintained docs

COGNITION-BRIEF.md grew by appended dated sections (initial brief → "RECONCILED with FROM-CONVERGENCE-SESSION.md" → "HOW THE THREE OF US HELP EACH OTHER"). It functions as a **session-correspondence record** — closer to the foundation/exchanges archive pattern (the conversation IS the construction) than to a spec. The live coordination has since moved on to MESSAGES.md (67KB, last touched 2026-06-10) and the CLAIMS sections of WORK-SPLIT.md. The briefs are the durable record of how the three-way was established. Records of exchanges are preserved verbatim, per-voice — not merged.

---

## UNIQUE CONTENT INVENTORY (what each file holds that exists nowhere else — why neither can be retired)

**COGNITION-BRIEF.md uniquely holds:**
- The cognition session's full ownership inventory with file paths: `runtime/cognition.py` (`run_swarm`/`run_role`/`run_jury`, `SlotBudget`, `run://` resolver) · `runtime/roles.py` + `roles/*` (`cast_for_mode`) · `runtime/rules.py` (declared-AST, 5 destinations, operator-only floor) · `runtime/activation.py` (always-on driver undriven) · `canvas/app/src/regions/CognitionView.tsx` + `cognition.*` SSE · `runtime/authoring.py` + 12 `/api/cognition/*` routes (propose-not-apply, UI-less by design — a Claude Design target) · `contracts/cognition_info.py` (`build_cognition_info`) + `ops/cli/capabilities.py` (`MODEL_CAPABILITIES`).
- The "ONE engine, many lenses" framing: `run_role`'s input becomes a declared addressed value (`ctx["utterance"]` → `input_addresses`, the `run_items` axis-inversion, the cross-unit REDUCE), serving FOUR consumers at once (C, the coherence semantic detectors, corpus-chain, guided-review's walkthrough).
- The verified engine-claims list: `run_role` ctx-hardcoding, `verify_jury`'s variance-not-error caveat, run_swarm-is-map-not-join — "all hold" against actual code.
- The three-perspectives model: coherence/interface = structure outside-in; guided-review = the operator's seat; cognition = engine-out — "none sees the whole, which is the point"; the Coherence Substrate needs all three.
- Cognition's four standing offers: builds shared engine seams once for all consumers; engine source-of-truth ("ask me before you design on an engine assumption"); convergence-spotting ("I lived built-twice"); engine-law guard from inside (operator-only floor, demote-only, reflects-never-owns, closed rule grammar — e.g. a semantic finding closing via a swarm re-read = a forbidden demoter).
- The reciprocal asks: coherence keep cataloguing unconsumed outputs (the 12 authoring endpoints as `to_build_ui` — "you seeing my blind spot"); guided-review supply real consumer needs so C isn't built in a vacuum.
- The now-superseded-but-historically-load-bearing identity exchange (the ⚠ question and the RECONCILED resolution) — see the flag below.

**GUIDED-REVIEW-BRIEF.md uniquely holds:**
- The fork-identity declaration in the session's own words (shares the pre-fork trunk: convergence-to-main · studio · Claude Design prep · coherence research; diverged forward onto the guided-review-surface).
- The full 8-row files-touched map with per-row dispositions (MINE-mutate / MINE-additive / I-DECLARE / HANDED-TO-COGNITION / REQUIREMENT-TO-COGNITION / NEVER-coherence's) — including the gate-files row naming `runtime/coherence_detect.py`, suite.py gate methods ~7025–7174, `tests/{suite_health,reachability,detectors}_acceptance.py`, `orphan-routes.json`.
- The three consumer-requirements for C in implementable detail, found nowhere else at this resolution:
  1. **`screen_reader` role shape:** input = `mockup://<file>` raw HTML OR a `ui://` address; output = plain-language "what this screen IS + what you can do here, at the operator's altitude"; VERIFIED working live on the resident 4B from injected HTML over the 14KB cap; the **cap → pre-digest refinement is the one named risk**; on the op-axis it's a generate op over one addressed input-unit. Division: cognition builds the seam (non-`listening` role firing on a `mockup://`/`ui://` input-address), guided-review adds `screen_reader.py`.
  2. **The injection edge:** recall+ground are injected end-to-end today (the 6 `mode_scope` edits make them live); connect/check/voice are G3/G4-partial (descriptive rules, skipped); the consumer-need is the **AST-rule promotion for those 3** so an enriched walkthrough turn uses the swarm rather than fires-and-discards.
  3. **`cast_posture` semantics:** default enriched, lean/enriched values, sub-mode-overridable, read at cognition's `fireable` filter.
- The build's framing: the guided right-hand-man walkthrough surface = the Company's ONE human-interaction organ; build-review its first consumer; **6 more consumers ride the same sequencer later**; criteria committed at `15886ed` under `build-prep/guided-review-surface/`.
- The FORM pre-commit unification agreement: FORM-lint joins coherence's one shared gate suite as one check, not a parallel layer.
- The shared-memory rule-proposal convention: propose any new shared rule in the coordination folder first ("a rule one writes binds all three"), and the standing-laws binding list (no-hardcoding, registry-is-truth, additive, fail-loud, reflects-never-owns, operator-only floor).

Zero of this is safely fold-able: every line above is either (a) one session's voice/commitment that only that session can restate, or (b) build-input detail (the C consumer-requirements) that the cognition session is actively consuming from this exact file.

---

## THE ONE REAL ISSUE FOUND — for the owning sessions to decide (proposed, not executed)

**A staleness hazard inside COGNITION-BRIEF.md, not a consolidation need.** The brief's "⚠ ONE OWNERSHIP QUESTION" section and its "RECONCILED… **Identity question — RESOLVED**… one owner of the convergence + the review/guided-review surface (you)" were **superseded** by WORK-SPLIT.md's CORRECTION (2026-06-08, Tim): it is genuinely THREE sessions; "ownership resolved" was WITHDRAWN; the settled answer is the fork model + claims-board-over-memory + guided-review as forward-owner of surface/FE/wire (WORK-SPLIT.md § GUIDED-REVIEW).

A reader of COGNITION-BRIEF.md alone gets the **wrong final state** ("same lineage, one owner") — exactly the duplicated-memory trap the CORRECTION warns about. Two mitigations already exist (the ratified truth ladder puts the board above any brief; the CORRECTION lives in the board), so this may be acceptable as-is. If the owning sessions want belt-and-braces, the minimal fix is **one superseded-pointer line** at the top of the RECONCILED section of COGNITION-BRIEF.md, e.g.:

> *(Superseded 2026-06-08 by WORK-SPLIT.md "CORRECTION — it's genuinely THREE": the resolution below was withdrawn; the fork model + claims-board-over-memory + § GUIDED-REVIEW forward-ownership is the settled state. Preserved as the record of the exchange.)*

That edit belongs to the **cognition session** (its file, its signature). This lane proposes it only.

A second, smaller observation, same shape: both briefs' agreement lists predate the ratified three-way rules block in WORK-SPLIT.md (lines 174–180). No contradiction found — the ratified rules are a strict superset — so no action proposed; noted for completeness.

---

## DISPOSITION TABLE (proposed — never executed by this lane)

| Source file | Disposition | Reasoning |
|---|---|---|
| `build-prep/coordination/COGNITION-BRIEF.md` | **keep-as-is** (keep-as-pointer toward WORK-SPLIT.md is already its de-facto role; optionally add the one superseded-pointer line above — cognition session's call) | Signed correspondence of the cognition session; holds its unique ownership inventory, standing offers, and the identity-exchange record; subordinate to WORK-SPLIT.md by the ratified truth ladder |
| `build-prep/coordination/GUIDED-REVIEW-BRIEF.md` | **keep-as-is** | Signed correspondence of the guided-review session; holds the only full-resolution C consumer-requirements (actively consumed by cognition's C build) and the 8-row files-touched map; subordinate to WORK-SPLIT.md by its own Agreements |
| *(no consolidated file)* | **none created** | The agreement-substance single-source-of-truth already exists: `build-prep/coordination/WORK-SPLIT.md`. Creating a merged brief would add a competing truth-surface below the board on its own ratified ladder and orphan two sessions' signatures |

**Net effect of accepting this draft:** zero file operations beyond (optionally) one pointer line, owned by the cognition session. Nothing retired, nothing folded, nothing lost.
