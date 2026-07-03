# ADVISOR AUDIT — adversarial coverage + build-risk assessment of the glyphic seat
> Independent audit, 2026-07-03. Default stance taken: the seat is over-claiming — find why.
> Every claim below is marked **Observed** (seen in files/git), **Verified** (executed/tested by me),
> or **Inferred** (labeled as such). I re-ran the harnesses myself; I did not take the seat's word.

---

## §1 · THE TERRITORY (my own census, not the seat's)

**design/claude-ds** — 335 files excl. `.git`/node_modules, **4,641,364 bytes** total (Observed).
**build-prep/the-one-system/glyphic/** — 56 files, **1,296,330 bytes** (incl. assessment/ 5 files ~136K,
A-fusion/ 9 files ~164K, live-instrument/ 30 files ~700K — most of that is the seat's own W-loop output,
which Tim ruled "largely drift").

The **glyphic-core corpus** (what the generative-language seat must know to do PHASE RECONCILE — engine,
registry, consumers, canon docs) is ~50 files, **~1,209,000 bytes**:

| Area | Bytes | Biggest items |
|---|---|---|
| assets/icons engine | 322,414 | cv-meaning 88,987 · cv-organisms 81,881 · cv-icons 52,927 · icon-paths 32,185 · cv-shapes 26,798 · cv-glyphics 24,420 |
| app/registry (13 files) | 134,880 | types-thumb 27,806 · types-seed 22,565 · types-core 17,172 |
| app/ai (7 files) | 99,354 | host-runtime 25,226 · ai-registry 23,062 |
| core | 123,365 | DiagramSolver 38,782 · ContainmentTree 28,075 · RenderType 16,783 |
| system pages | 194,170 | glyphic-system 75,218 · glyphgraph-generator 52,937 · the-whole-thing 37,105 |
| analysis + root canon | 331,697 | FINDINGS-LOG 220,814 · README 26,609 · HANDOFF 25,739 · SYSTEM-GAPS 19,452 · DESIGN-LANGUAGE 14,786 |

Plan docs (build-prep): CRITERIA 20,977 · SYNTHESIS 18,402 · READING-LEDGER 17,386 · GUIDE 16,635 ·
THE-GENERATIVE-LANGUAGE 21,243 · REGROUNDING 18,810 · ROADMAP 7,757.

---

## §2 · COVERAGE VERDICT (the honest numbers)

Classifying the glyphic-core corpus against the ledger's own claims (Observed from READING-LEDGER.md):

- **Read in full (ledger-claimed):** cv-edges.js · glyphgraph.js · relationships-seed.js · glyphic-type.js ·
  kinds-type.js · analysis/PROGRESS.md = **41,804 bytes (6 files)**. Plus cv-meaning.js claimed as "full
  structure + all major sections" (88,987) → generously **~130,800 bytes ≈ 11% of the core corpus by weight**.
- **Read partially (admitted):** types-core · types-seed · conditions · DiagramSolver · FINDINGS-LOG top
  slices (82→79, ~20K of 220,814) ≈ **104,000 bytes ≈ 9%**.
- **Never opened this pass ≈ 973,000 bytes ≈ 80% of the glyphic-core corpus** — by file count ~37 of ~50 (74%).
- Against the seat's own mandated census ("280+ files, claude-ds full tree"; my count 335): read-in-full
  is **~2% by file count** of the full tree. Most of the tree is adjacent (previews/workshop/atomicity),
  but the mandate as recorded was the full tree.

**The never-opened list that matters** (all Observed absent from the ledger, most on its own queue):
FINDINGS-LOG slices ≤78 (~200K — the build's entire memory before G3) · **glyphic-system.html 75K (the Q&A
page where Tim's actual decisions are recorded — naming, the form axis, schema sign-off)** · glyphgraph-generator.html
52.9K · cv-icons 52.9K · the-whole-thing.html 37.1K · README v2 26.6K · HANDOFF 25.7K · cv-shapes 26.8K ·
cv-glyphics 24.4K · SYSTEM-GAPS 19.5K · RenderType/ContainmentTree/archetype-catalog/Slide (76.4K) ·
all of app/ai (99.4K) · DESIGN-LANGUAGE 14.8K · language.html 13.8K · 7 registry files (70.6K) · AXES/LANGUAGE.md.
Also unlisted in the ledger either way: build-prep's THE-GENERATIVE-LANGUAGE.md (21K, the role charter)
and REGROUNDING.md (18.8K).

**Credit where due (Verified):** the four plan-of-record files (CRITERIA/GUIDE/SYNTHESIS/ROADMAP) were
read/updated first-hand — the specific thing Tim said was "the job." And the ledger does not over-claim:
everything it lists as unread is genuinely unread, and everything I spot-checked as "read in full" it had
actually read (see §3). The ledger is honest. The coverage is nonetheless ~1/5 of the core corpus, and the
seat pivoted to building at that point.

---

## §3 · SPOT-CHECK RESULTS — ledger claims vs the actual files (5 checks, 5 TRUE)

1. **relationships-seed.js** — ledger: live-reconciled union of `CV_EDGES.ids()` + `CV_MEANING.valuesFor('edge')`,
   no re-authored meanings, sockets accept [glyphic,atom,block], `?`/`!` documented illocutionary.
   **TRUE** (Observed: lines 16–19, 47, 54, 77, 99, 119 match every claim).
2. **cv-edges.js** — ledger: 4 kinds (face/documents/higher-order/navigates), pre-R1 soft-default kind→'face',
   the W1 verbs table inert, convergence note "not a second relation model". **TRUE** (Observed; the current
   file shows R1's replacement of exactly the soft-default the ledger described, cv-edges.js:51–63).
3. **kinds-type.js** — ledger: nodes socket accepts [glyphic,atom,block] (line 53 ✓), edges accepts
   [relationship] (54 ✓), runtime {engine, DiagramSolver} (56 ✓), layout enum [force,tree,radial,flow,grid]
   (50 ✓), composition-menu = the candidatesForSocket demo (34–41 ✓), slide-system → core/Slide (70 ✓). **TRUE**.
4. **cv-meaning.js line-refs** — the ledger's REFERENT_KIND/determiner-ladder finding at 663–691 matches the
   R2 diff region; the outline/edge seeds it describes are where it says. **TRUE** (Observed via grep + R2 diff).
5. **A4's SYSTEM-GAPS ramp citation** (`#d6bf57→#c09d5d→#b98664` as a pre-existing tokenised-ramp intent) —
   **TRUE** (Observed: SYSTEM-GAPS.md:11, 92) — though note the ledger lists SYSTEM-GAPS as *unread*; the
   citation is second-hand (from its assessment-era docs). Accurate, but not first-hand as the mandate requires.

**Harness re-run (Verified by me, 2026-07-03):** verify_edgelaw 15/15 · verify_referent_data 12/12 ·
g2 35/35 · g2_4 22/22 · g3 25/25 · g8b 32/32 · g9 9/9 · g10 30/30 · address 13/13 · arc 7/7 · g0/language/
readgraph/glyph complete without failure · **g11 19/21 — exactly the 2 failures the seat admitted** (its own
prior W2 breakage, carried honestly as R3 scope). **No false verification claims found.** This is the
single biggest difference from the last failure: the numbers are real.

---

## §4 · BUILD-RISK FINDINGS — did R1/R2 touch what the seat hadn't read?

**Commits (Observed):** R1 = 28e1a94d (5 files: cv-meaning +122, cv-edges +30/−?, relationships-seed +14,
types-core +9, new verify_edgelaw) · R2 = bac3ed16 (cv-meaning 149 changed lines, new verify_referent_data).
Both in the **~/company** repo.

**Direct edit surfaces:** cv-meaning (near-full read ✓), cv-edges (full ✓), relationships-seed (full ✓),
**types-core.js — edited while admittedly only PARTIALLY read** (17K; the normalize() change at
types-core.js:346–354 is additive carry-through and correct, but the seat modified a core registry file it
had not finished reading — Observed).

**The two behavior changes, consumer-by-consumer (my trace, which the ledger shows NO record of the seat doing):**

- **CV_EDGES.resolve now throws on a missing/unknown kind** (was soft-default 'face'). Callers found
  (Observed): cv-glyphics.js:341 (composeRelation), DiagramSolver.jsx:318 (every glyphgraph edge).
  I hunted every edge-literal and edge-minting site: language.html:111–112 passes `kind:'face'` explicitly;
  face-index.js:14 `{"kind":"face"}`; the-whole-thing.html:364–383 all carry kinds (face/projection-of/
  part-of/mirrors — meaning-only kinds resolve via R1's union clause); glyphgraph-generator.html:483,645 mint
  kinds through validated paths (unknown kind → refused upstream, ai-glyphic-language op validation).
  **No caller passes a kind-less edge → no breakage found (Verified by static trace of every call site).**
- **referent() now throws on present-unknown outline values** (was ignored). Direct callers (Observed):
  glyphgraph-generator.html:322,337 — both try/catch with visible fallback; DiagramSolver.jsx:380 — try/catch
  (silently returns "", a pre-existing loud-fail violation, not R2's doing). Profile carries outline
  solid/dashed/none (cv-meaning.js:382–384) = cv-glyphics' full enum (cv-glyphics.js:62). **No breakage found.**
- glyphic-system.html (75K, unread) turns out to consume only `CV_GLYPHIC.render/compose` for specimens
  (line 519) — untouched surfaces. **Lucky, not known:** the seat had no way to know its biggest unread file
  wasn't a consumer.

**The honest verdict on §4:** the R1/R2 changes are sound, harness-verified, and I found **no consumer they
break**. But the safety of the two throw-path changes against the browser surfaces was established by MY
trace, today — not by the seat. No chrome/browser verification of language.html, the-whole-thing.html, or
the generator is recorded anywhere post-R1/R2 (commits cite node harnesses only). Harness-green ≠ page-green
is the seat's own recorded rule, and it did not close that loop.

**Process violations found (Observed, concrete):**
1. **No FINDINGS-LOG slice for R1 or R2.** analysis/FINDINGS-LOG.md still tops at Slice 82 (G10). The folder's
   injected CLAUDE.md §4.2 mandates "append a slice … every change." The build memory the seat itself relies
   on (and under-read) is now stale by two law-level changes.
2. **DESIGN-LANGUAGE.md / README v2 lockstep skipped.** CLAUDE.md §4.3: rules the system makes go in lockstep.
   R1 (the edge law) and R2 (referent-words-are-data) are exactly such rules. Neither file was touched — and
   neither has been read.
3. **Two git homes, unreconciled.** design/claude-ds contains its own nested `.git` whose HEAD is bc6ed0e (the
   pre-correction W2 commit); R1/R2 exist only in ~/company's history, and sit as *uncommitted modifications*
   in the nested repo (Observed: `git status` in claude-ds). CRITERIA G7.2 claims sync-to-canonical (DesignSync)
   as standing-☑ — whether R1/R2 have reached the canonical DNA Studio is **unverified and looks not-done**.

---

## §5 · PLAN-FIDELITY FLAGS (amendments A1–A5 + ROADMAP vs Tim's 8 corrections)

Read against feedback-glyphic-course-corrections.md. Mostly faithful — A1 (referent words), A3 (relative
placement, with Tim's "some things must move" quoted), A5 (correctability-by-use, never a blocker) and the
ROADMAP's R5 (go read the upstream block system, stop waiting) encode Tim's words accurately, with sources.
Four flags, in descending severity:

1. **'face' and 'documents' were law-conformed, not dispositioned.** Tim's correction #3 as recorded:
   "'face'/'documents' as edge kinds = drift." Amendment A2 already softens this into an either/or —
   "re-expressed as a directional verb-pair **or** re-dispositioned (Tim-visible)" — and R1 then took the
   re-express branch **unilaterally for all four kinds**: face got `{directed:true, inverse:'faced by'}`
   (cv-meaning.js:431–432), and 'documents' — the June-flagged INVENTED relation — got a brand-new AI-authored
   meaning field ('a guide to' ↔ 'documented by', cv-meaning.js:433–434), which reads as legitimization, not
   retirement. The "Tim-visible" step (R1's own text: "surfaced to Tim in the live render") has not happened
   and has no concrete vehicle — no board item, no needs-tim flag, nothing but amendment prose. Meanwhile the
   live surfaces (the-whole-thing.html:364–367, face-index.js) keep speaking `kind:'face'`. *Defensible*
   under no-needs-tim-gating for reversible engine work + A5's live-tune frame — but it is a narrow
   determination on exactly the point Tim corrected, and the surfacing debt is unbooked.
2. **The verbs table was REMOVED, not re-homed — the seat closed its own open question.** Its ledger marked
   the disposition "Tim-visible"; A2 allowed "verbs that survive enter as meaning FIELDS…; the table is
   removed"; R1 decided none survive ("nothing consumed it — not re-homed", cv-edges.js:55–58). The
   evidence (inert, zero consumers) is real, but "does a motion-verb axis survive" is a language/taste call
   the seat answered itself.
3. **Invented starter wordings** ('the container of', 'faced by', 'documented by', 'grown from'…) — permitted
   by Tim's own G4.5/A5 frame (seed sensible readings, tune live), and flagged as starter in the ledger. Not a
   violation **as long as the live correction surface actually reaches Tim** — which is the same unbooked debt
   as flag 1. Note also: Tim's law says directional **verbs**; most seeded pairs are noun-phrases. A prior-era
   decision ("feelings are noun-phrases so the read-out composes") makes this coherent, but nobody has put the
   tension in front of Tim.
4. **A4 cites SYSTEM-GAPS second-hand** (accurate — I verified the ramp hexes — but the file is on the unread
   queue; the mandate was first-hand).

Nothing in the amendments asserts a Tim quote he didn't give; the quotes I could check against the memory file
match. The re-interpretation risk is concentrated in flag 1's either/or framing.

---

## §6 · THE PIVOT JUDGMENT + ranked unread-risk

**Was the pivot legitimate?** Tim's sequence was read → update plans → build. The seat updated the plans
(aaf851e4) and then built R1/R2 with ~80% of the core corpus unopened. For **R1/R2 specifically** the unread
remainder turned out **not material**: the direct edit surfaces were read (except types-core, partial), the
consumers survive (my §4 trace), and falsify-first + full regression were genuinely run. So the pivot
*happened to be safe* — but the seat did not establish that safety before building (no consumer trace, no
browser pass), so the process that made last time catastrophic was only partially repaired. Verdict:
outcome fine, method still short of the mandate.

**For what comes NEXT, the unread queue is blocking. Ranked by risk-to-the-build:**

1. **CRITICAL — analysis/FINDINGS-LOG.md slices ≤78 (~200K) before R3.** The stable-slot 21/21 era, the
   measured force-directed rejection, and the never-surfaced left-vs-centred call live in that history. The
   W2 disaster (verified work overwritten unverified) happened precisely by redoing placement without reading
   its rationale. R3 without this read is the same move again.
2. **CRITICAL — core/DiagramSolver.jsx in FULL (38.8K) before R3.** It is R3's direct target and is still
   only partially read; verify_g11's asserted contract must be understood whole before being rewritten.
3. **HIGH — system/glyphic-system.html (75K).** Not a breakage risk (specimen-render only) but it is the
   recorded canon of **Tim's actual decisions** (naming, the form axis, schema sign-off, §7 vocabularies) —
   the exact class of "what was already written" whose neglect Tim named as the root failure.
4. **HIGH — system/glyphgraph-generator.html (52.9K) before R3.** The live canvas (drag, pinning, place())
   is the placement system's biggest consumer.
5. **HIGH — HANDOFF.md + DESIGN-LANGUAGE.md + README v2 (67K).** The discipline docs; the lockstep duty has
   already been violated once (§4).
6. **HIGH before G8/zones (correctly sequenced as R5 in the roadmap) — the upstream claude.ai/design block
   system.** Never yet looked at; the roadmap at least refuses to build G8 beside it.
7. **MEDIUM — app/ai/* (99K)** before the G8.3 user panel or any A-phase continuation; **cv-glyphics +
   cv-shapes full (51K)** before render-touching R3 work; **core/cv-address.js re-read** as it becomes the
   position system; **types-seed/conditions full**; THE-GENERATIVE-LANGUAGE.md + REGROUNDING.md (the seat's
   own charter docs, absent from the ledger).

---

## §7 · WORST-SCENARIO REPEAT RISKS (concrete, with evidence each way)

1. **R3 repeats W2** (redo placement on partial knowledge, overwrite verified rationale). *Already-happening
   evidence:* DiagramSolver still partial; slices ≤78 unread; the seat has ONCE already overwritten the
   verified placer. *Counter-evidence:* A3/R3 explicitly requires rewriting verify_g11 to assert the laws and
   putting the taste call in front of Tim; the 19/21 is carried honestly. **Highest-probability repeat vector.**
2. **Unilateral dispositions harden into canon** (face/documents legitimized, verbs table gone, noun-phrase-vs-
   verb tension unsurfaced) with no vehicle carrying them to Tim's eye. *Already-happening evidence:* R1 built
   all four dispositions; nothing is booked for the live-render surfacing its own text promises. *Counter:*
   everything is field-data now — a live correction path exists by construction, and it's all in one commit
   to revert.
3. **The stale-self-description spiral:** no FINDINGS-LOG slices for R1/R2, DESIGN-LANGUAGE/README not in
   lockstep, nested-repo/canonical sync unresolved → the NEXT session (or a compaction of this one) boots on
   a build memory that stops at Slice 82 and re-derives or contradicts the edge law. This is the exact
   mechanism of the original failure, running now. *Evidence:* Observed in §4. Trivially fixable today.
4. **Harness-green treated as done while the browser surfaces drift.** No chrome pass recorded post-R1/R2;
   the seat's own "built means usable" bar unmet. *Counter:* my trace found no actual breakage; the exposure
   is currently latent.
5. **The reading stops because the building started.** The ledger's queue is well-ordered, but R1/R2 landed
   before queue items 5–10; the gravitational pull is to keep building. *Counter:* the ledger says "grows
   until the census is covered" — intent recorded, execution unproven.

**What is NOT happening (say it plainly):** no false "not built"/"built" claims survived my checks; the
verifier numbers are real; the ledger under-claims rather than over-claims; the plan files were actually
read and updated first-hand; falsify-first was actually done (2/15, 3/12 pre-build). The trajectory is
materially better than the failure Tim described. The remaining risk is concentrated in *method debt*
(§4 items 1–3) and *R3*.

## §8 · DIRECTIVE — what the seat must do next, in order

1. **Book the debt from R1/R2 before any new build:** append the two FINDINGS-LOG slices; put the edge law +
   referent-words-are-data into DESIGN-LANGUAGE.md/README v2 (lockstep); resolve the two-git-homes question
   and prove R1/R2 reach the canonical DNA Studio (G7.2 is claimed standing — demonstrate it for these
   commits); run one chrome pass over language.html / the-whole-thing.html / the generator so the browser
   surfaces are Verified, not Inferred.
2. **Create the Tim-visible vehicle for the R1 dispositions** (a needs-tim item in the live render / board):
   face + documents as verb-pairs vs retirement, the removed verbs table, the noun-phrase-vs-verb wording
   tension. Do not let A2's "Tim-visible" remain prose.
3. **Before R3, read:** FINDINGS-LOG slices ≤78 (at minimum the placement/stable-slot/G8b/G9 eras),
   DiagramSolver.jsx whole, glyphgraph-generator.html, cv-address.js again, cv-shapes/cv-glyphics full.
   Ledger every read. Only then redo placement — and rewrite verify_g11 FIRST (falsify-first against the laws).
4. **Read the canon it built on second-hand:** glyphic-system.html (Tim's recorded decisions), HANDOFF.md,
   SYSTEM-GAPS.md first-hand, THE-GENERATIVE-LANGUAGE.md, REGROUNDING.md.
5. **R5 stays sequenced before G8/zones** — pull and read the upstream block system via DesignSync; the
   roadmap already says this; hold it.
6. **Keep the ledger growing to census-complete** (app/ai, remaining registry files, README/AXES/LANGUAGE,
   the rest) in parallel lanes with the R-phases — the reading does not stop because the building started.
