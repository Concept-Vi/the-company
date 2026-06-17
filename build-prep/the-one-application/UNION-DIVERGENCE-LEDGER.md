Confirmed: there are zero lead-decision artifacts in the store for any of the one-application build's "LEAD DECISION recorded" tags (no decision events mention SCHEMES/grammar/lifter/derive; the surfaced dir predates this work; no channel synthesis exists for the build). So the spec at line 31 *requires* the artifacts, but they do not yet exist — that's a live residual, exactly as the advisor flagged. This is the most honest single finding for the ledger.

I have everything verified. Writing the ledger now as my text return.

---

# DIVERGENCE LEDGER — Substrate Unification ("the one application")

**Scope:** the two loop-prep deliverables at `/home/tim/company/build-prep/the-one-application/` — `COMPLETION-CRITERIA.md` + `IMPLEMENTATION-GUIDE.md` — reviewed across two adherence rounds against Tim's confirmed rules, the Company system laws (root AGENTS.md Rules 1-10 + C9.x floor), operator_memory, and the sibling-stream conventions. Bar applied throughout: Tim's "if it is even slightly off, or decisions made without the whole thing compared, it will be a total waste."

**Honest framing — three things kept separate (do not let them collapse):**
1. **Spec-adherence** — has CONVERGED (this is what the rounds measured).
2. **Build-state** — this is UNBUILT loop-prep. Almost every criterion is 🟡-designed; **nothing is verified by-use yet.** The spec now sets the right by-use bars; the build loop still has to clear all of them.
3. **Decision-gates** — 5 open Tim decisions + open reconciles. These are NOT divergences — they are correctly designed-in gates. They are the headline of "what remains open."

The current files on disk are a **third revision** that already absorbed both rounds (verified: STORE1b/STORE4b labelled "NEW"; GR2 explicitly repudiates the prior draft; the 🟠 built-unexercised split and the distinct-method-not-call-site metric are present verbatim).

---

## ROUND 1 — on the original draft: 43 divergences, 5 FATAL

The five fatals were the load-bearing catches — each was a case where the doc invoked its own safety claim while violating a rule:

- **F1 · The G-* decision-gates routed developer/architecture calls to Tim** (G-FORM-MATCH A/B/C, G-EVENT-TAXONOMY A1/A2/A3, G-LIFTER-AUTHOR, G-GRAMMAR). Double violation: not-a-developer (asking Tim a code question) AND no-deferral (parking decidable work behind a gate that should never reach him). The highest-value catch — it inverted the doc's own "route to Tim for safety" into a rule violation.
- **F2 · The keystone self-build loop had no operator-resolution node in the circuit.** It gated the autonomous `claude -p` path on TIMING ("built-not-armed"), but C9.2 is a per-dispatch STRUCTURAL route. Flipping one env-gate would have yielded an autonomous trigger→builder. Arm-once was conflated with resolve-per-dispatch.
- **F3 · The whole build was decided without comparing the five sibling prep streams** (instrument-surface, universal-projection, self-build-surface, live-resolution-surface, front-interface) — the precise SCAN-BEFORE-BUILD failure Tim names: deciding the union without the whole thing compared → drift, not union → total waste.
- **F4 · GR2/"derive _RESOLVABLE first" was labelled a VERIFIED bug and made the lead move — but it is a NON-bug.** `_RESOLVABLE` is the deliberate, correct mirror of the 9 schemes with a live dispatch branch; the 7 absent ones RAISE fail-loud by design. The prescribed `resolution_path=='dispatch'` derivation would have converted a by-design fail-loud into a silent-success risk. (Note: this was the one genuine cross-lens conflict — one lens marked it fatal-as-prescribed, another treated it as a benign drift-guard. The conflict is REAL and the fatal reading won.)
- **F5 · The Definition-of-done accepted the instrument's FORM at 🟡-terminal**, with zero mention of the Rule-9 separate design-critic / fail-loud design-lint / native-mobile face — i.e. the build's defining half (Tim's "the literal operation of my seed equation") had no verification path at all.

The other ~38 (major/minor) clustered as: the single ✅ (INST1) green-painted on a code-read; the C9.4 three-anchor floor omitted for ~6 new registries (which would fail the repo's own `drift_acceptance.py` at commit); FORM faces discharged by "a CLI/inspect listing is the legible face" (Tim never reads a CLI); unconditional "optional/later" deferrals (STORE6 PostgREST/Auth); a ui:// diff-gate that institutionalized a bridge where the law demands a union; "fs-fallback each step" ambiguous between rollback (compliant) and silent runtime degradation (forbidden); the GR1→GR2 dependency inverted in the priority order; and the trigger registry cloning a bespoke parallel registry class instead of reusing the shared mechanism.

---

## WHAT WAS FIXED (verified present in the on-disk revision)

The five fatals are the spine of the fix arc — all five resolved:

- **F1 → RESOLVED.** The G-* gates were reclassified. ~20 carry a **"LEAD DECISION recorded"** tag (the lead decides developer/architecture calls, coordinating via the fabric); only genuine direction/meaning calls reach Tim. The Tim-gate set collapsed from ~13 to **~3 + a residual + the taxonomy**.
- **F2 → RESOLVED.** ACT6 (line 130) now routes the keystone loop *through* the operator-gated wire: trigger fires → `decision.surfaced_for_review` → operator `resolve_surfaced` → `dispatch_decision` launches `claude -p`. Its ✅ bar requires a falsify-first test (a trigger emitting `dispatch` is REJECTED at construction) AND a by-use proof the structural gate holds **independent of arming** — "built-not-armed" demoted to a timing gate on top of, not instead of, the structural one.
- **F3 → RESOLVED.** The sibling streams are reconciled as **RCN1–RCN7** (Group RECONCILE / R-* gates), each artifact-backed and lead/fabric-owned. Coverage (#74) got its own gate (RCN7) converging onto the **completed** `guided-review-surface/findings/coverage/` sweep rather than re-deriving it.
- **F4 → RESOLVED.** GR2 is now explicitly **"a DRIFT-GUARD over the live dispatch set — NOT a bug fix (corrected)"**, derived from the actual dispatch capability (`tuple(SCHEME_HANDLERS)` once GR3 lands), with a falsify-first test that must come up **GREEN on unmodified code** (green = proof there is no bug).
- **F5 → RESOLVED.** Overall-done is now **BLOCKED** until the instrument FORM passes a separate design-critic + design-lint + render-for-cognition on **BOTH faces** + surfaced-for-review; FORM handoffs to sibling streams are **enforced system-memory Gap rows**, not prose pointers.

Round-1 majors/minors also absorbed: INST1 downgraded ✅→**🟠 built-unexercised** (the honest-status three-state split was added); C9.4 three-anchors made a per-registry + Definition-of-done criterion; "CLI is the face" struck in favour of LEG1 meaning-from-data; deferrals given system-memory return-whens; the ui:// diff-gate replaced by a derivation (SCHEMES `= tuple(scheme_registry)`); "fs-fallback" disambiguated to operator-rollback (runtime fs-fallback explicitly forbidden, fault-injection test added); GR5 (recursive grammar) promoted ahead of GR1 in the build order.

---

## ROUND 2 — on the revised draft: 37 divergences, 0 FATAL

Honest verdict from the rounds: the revised draft **substantially honored the synthesis** — no headline regression was manufactured to satisfy a "find divergence" default; the named charges (row-add-unifies, one-edge-law, lifter=predicate, DNA-as-ground-truth, flat-grammar, papered Shape-B, slice-census) were all discharged. The 37 were **omissions / inconsistent application / cross-doc inconsistencies**, not regressions. The strongest round-2 majors:

- **STORE1b — ext4 / never-/mnt/c (data-loss class).** The migration stood up a real Postgres but never pinned the PG data directory to ext4; AGENTS.md Rule 5 forbids /mnt/c (WSL fsync corrupts DBs), and the build-prep tree itself lives under /mnt/c.
- **STORE4b — Rule-7 confirm before touching real source data.** Operator-rollback (recovery-after) was substituted for the surface/confirm-before gate that the migration of 1069 sessions + 6.4k events demands.
- **RCN7 — coverage re-derived.** A completed open coverage sweep already existed; the draft re-ran its core deliverable from scratch (parallel-build, not union).
- **Honest-status split** — 🟡 collapsed "not-written" and "written-but-unverified" into one symbol (the law requires them distinct).
- **Tree-sitter false dichotomy** — TS/JS extraction shipped incomplete regex (deferred tree-sitter as an "upgrade"); but in-process `py-tree-sitter` is available now, installed like the repo's existing `ast`/PyYAML — so "make-each-thing-work" demanded the complete parser, not a silent under-extraction.

Minors: the distinct-method seam metric (61 call-sites vs ~48 distinct names conflated); the stale `1,068`/`1,069` count pinned in STORE0 (whose whole point is "don't trust a number, re-census"); B-3.2 disposition missing C9.4 anchors; the require-vs-assert tension (RCN3 marked open while the body asserted its outcome); doc-pointer/path inconsistencies between the two headers.

---

## WHAT REMAINS OPEN

### A. The 5 genuine Tim decisions (DECISIONS-FOR-TIM — surfaced at his altitude, machine-names removed)
1. **ID1 — file:// vs cas://:** is a saved file "the same thing" as its content, or its own thing? (lead modelled BOTH-with-derivation first; residual = dedup/cache as one identity, or two kinds of reference?)
2. **ID2 — channel:// (RESIDUAL only):** when a session ends, which face is the durable channel member — the person or the session? (lead reconciles the dual-face; reaches Tim only if a residual survives.)
3. **ID3 — cluster://:** is a "cluster" a thing you name and return to, a live re-computing result, or both?
4. **TH2 — Shape-B:** should the event streams (history log, marks, pins, notes — the highest-volume live data) become first-class addressable, stay references-only, or a mix?
5. **COV2 — the form taxonomy:** what are the REAL kinds of things in the corpus? (current `decision/log/registry/prose` are prior-AI scaffolding; YOUR taxonomy is authored from the open coverage; effort-routing is fail-loud-BLOCKED until it's recorded.)

### B. Reconciles that block overall-done
- **RCN2 + RCN6** (instrument-surface / universal-projection / guided-review FORM ownership) — overall-done is explicitly BLOCKED until these record AND the handed-off FORM Gaps return design-critic-passed on both faces. **RCN3 + RCN5** gate the keystone-loop convergence (ACT6/LENS3 build the backend half now, convergence half conditional).

### C. The one residual the spec-text fix does NOT actually close — flag for the build loop
**The "LEAD DECISION recorded" artifacts do not yet exist.** The spec (COMPLETION-CRITERIA line 31) now *requires* every lead-decision tag to be backed by a durable artifact (channel synthesis / decision row), and correctly says a build-worker finding the tag but no artifact must treat the call as **not-yet-made (🔴-needs-the-artifact)**. But I verified the store directly: zero decision events reference SCHEMES/grammar/lifter/derive (the 27 `decision.*` events are all `dispatch`/`intent`/`verify`/`py`), the operator `surfaced/` dir predates this work, and no channel synthesis for this build exists. **Adding the requirement to the spec ≠ the requirement being met.** The ~20 LEAD-DECISION tags are, today, unbacked prose. This is the live residual: the build loop must produce the fabric-coordinated artifacts before treating any of those calls as made.

### D. Build-state (the by-use bar is entirely unmet)
Almost every criterion is 🟡-designed; the single nearest-green line (INST1) is honestly 🟠 built-unexercised. The spec sets the right by-use bars — the loop has to clear them. Residual risk concentrates at: the **ext4/migration data-safety gates** (STORE1b /mnt/c refusal + STORE4b operator-confirm + the kill-PG fault-injection); the **operator-gated-dispatch construction test** (ACT6 — a trigger emitting dispatch rejected at construction, gate holds independent of arming); and the **COV2-before-routing fail-loud predecessor**.

---

## VERDICT — adherence-clean, or another round?

**Spec-adherence has converged: another document-level adherence round is NOT warranted.** All 5 round-1 fatals are fixed in the on-disk revision; the 37 round-2 findings are absorbed (0 fatal in round 2, and the residual round-2 majors — ext4, Rule-7, RCN7, tree-sitter, the honest-status split — are now present as named criteria); the cross-lens GR2 conflict is resolved in the doc itself; the Tim-gate pile is refined to ~3+residual+taxonomy.

**But "adherence-clean" is a statement about the SPEC, not the build.** Bound it in the same breath, per Tim's "slightly off = total waste" bar:
- This is **unbuilt loop-prep** — the by-use verification bar the spec sets is **entirely unmet**.
- **5 Tim decisions + RCN2/RCN6 (and RCN3/RCN5 for the keystone)** gate it — these are designed-in, not divergences, but the build cannot reach "done" until they record.
- **The lead-decision artifacts do not yet exist** (Section C) — the spec requires them; the store does not have them. This is the one place where the text fix outran reality, and the build loop must close it before building to any "LEAD DECISION recorded" tag.

So: ready to enter the build loop, NOT ready to call done. The next gate is Tim's 5 decisions + the lead producing the missing decision artifacts — not a fourth adherence pass.

**Relevant files (absolute):**
- `/home/tim/company/build-prep/the-one-application/COMPLETION-CRITERIA.md`
- `/home/tim/company/build-prep/the-one-application/IMPLEMENTATION-GUIDE.md`
- DECISIONS-FOR-TIM block: foot of COMPLETION-CRITERIA.md (the 5 calls)
- Lead-decision-artifact residual evidence: `/home/tim/company/.data/store/events.jsonl` (no SCHEMES/grammar/lifter decision events), `.data/store/surfaced/` (predates this work)