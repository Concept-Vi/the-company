# Consolidation draft — coordination-protocols
**Overlap members:** `/home/tim/company/MERGE-COORDINATION.md` (723 lines, repo root) + `/home/tim/company/build-prep/coordination/WORK-SPLIT.md` (395 lines)
**Drafted:** 2026-06-10, by the consolidation-drafter lane (B4). PROPOSED ONLY — nothing executed, no source touched.

---

## RATIONALE

### Verdict: MIXED — the two files are different organs (keep both), but ONE layer is genuinely duplicated (the protocol itself) and there are two stale channel-pointers that actively mislead

**What each file actually IS (verified, not assumed):**

- **`MERGE-COORDINATION.md`** is the **relay-era exchange record**: the verbatim, turn-by-turn negotiation between the interface/coherence session and the cognition session that performed the great unification (the line-3756 catch, the union gate, main `3b6b6b3`→`76fc0c2`→`49debc4`→`233f34e`, the mode-dial co-design, the worktree retirement), then the three-way opening (the identity tangle, the fork reconciliation, the naming reset to coherence/guided-review/cognition, the overlap maps, the ratification rounds). It is a **primary source** — the conversation IS the construction (the same law as `~/company/foundation/exchanges/`). Its CHANNEL role is **superseded**: WORK-SPLIT § PROTOCOL item 10 (locked 2026-06-09) moved the channel to `MESSAGES.md` (append-only, cron-fired, no human relay), and `MESSAGES.md` is live as of today (2026-06-10 16:12) while MERGE-COORDINATION.md last changed 2026-06-09 01:48.

- **`WORK-SPLIT.md`** is the **live coordination organ**: the locked design (the engine generalization), THE SPLIT (lane ownership), the **§ CLAIMS board** (which `AUTONOMOUS-LOOP.md` directs every cron fire to read FIRST, authoritative over memory), the **§ PROTOCOL** (the one law, items 1–11, ratified by all three sessions), the gate-bar refinement (per-commit vs convergence bars + OPEN-REDS.md), and the running claims/scope log (#50–#58, releases, flags).

**Why NOT a full merge:** folding the 723-line exchange record into the live board (or vice versa) would destroy both functions — the board must stay small enough for a loop fire to read every 15 minutes; the record must stay verbatim to remain evidence (truth ladder: git history outranks the claims board precisely because the record is unedited). The overlap is **by design at the file level**: one is history, one is law-in-force. Roughly 90% of each file is unique to it.

**What IS duplicated (the real consolidation target) — the protocol layer exists in FOUR places of descending authority:**
1. WORK-SPLIT **§ PROTOCOL (LOCKED 2026-06-09)** items 1–11 — the current law, ratified by cognition (374b272), guided-review, coherence.
2. WORK-SPLIT **"THE PROTOCOL"** (the early 4-item block near the top, written 2026-06-08) — a superseded ancestor of (1), still sitting above it in the same file with no superseded marker.
3. WORK-SPLIT **"§ PROTOCOL — the gate bar, ratified (Option B)"** — a Tim-confirmed AMENDMENT to item 4 (two bars: per-commit vs pre-merge), physically separated from the list it amends by ~90 lines of claims log.
4. MERGE-COORDINATION.md **prose** — the protocol's evolution (window handshake, one-driver-one-parker, union gate, over-share, the three-way onboarding procedure, shared-memory discipline) — mostly absorbed into (1), but FIVE protocol-grade rules never made it in (enumerated below).

**The two stale pointers (actively misleading, worth the owning session's immediate eyes):**
- **WORK-SPLIT.md's own header (line ~5)** still says: *"Relay channel for messages: `MERGE-COORDINATION.md` (Tim relays the 'go read it')."* This contradicts its own locked item 10 (channel = MESSAGES.md, cron-fired, "no human relay"). A new/cold session reading the header top-down would post to the dead channel and wait for a relay that no longer happens.
- **MERGE-COORDINATION.md carries no banner** saying its channel role ended. It sits at repo root (the most discoverable path), is referenced by 19+ docs, and ends mid-conversation (#55) with no "this moved" marker. Same cold-session trap.

**What the owning session should decide:**
1. Adopt (or amend) the consolidated protocol text below as the single § PROTOCOL in WORK-SPLIT — replacing the early 4-item block with a superseded-marker, folding the gate-bar amendment into item 4's text, and adding the five fold-ins from MERGE-COORDINATION.
2. Fix WORK-SPLIT's header pointer (channel = MESSAGES.md; MERGE-COORDINATION.md = the archived relay-era record).
3. Add the proposed archive banner (below) to the top of MERGE-COORDINATION.md.
4. (Open, not urgent) Whether WORK-SPLIT's ever-growing claims/scope log eventually rolls up — it is the same typed-log shape as OPEN-REDS.md/MESSAGES.md and could one day be a registry, but per no-versioning/update-in-place the file stays the one canonical board until that is a deliberate design step. Flagged, not proposed here.

**Preservation statement:** because both sources are KEPT (neither retired), every unique fact in both survives in place by construction. The consolidated text below covers only the duplicated protocol layer + the strays being folded in; it removes nothing from either source.

---

## CONSOLIDATED TEXT — § PROTOCOL, one current statement
*(Proposed replacement for WORK-SPLIT's protocol content. Provenance marks: [LOCKED-10] = the locked 2026-06-09 list · [AMEND] = the Tim-confirmed gate-bar ratification · [FOLD-IN: MC] = protocol-grade content currently only in MERGE-COORDINATION.md prose · [EARLY-4] = the early 4-item block, absorbed.)*

### THE COORDINATION PROTOCOL — the one law all loops read each fire
Ratified: cognition (374b272) · guided-review · coherence. Amended: gate-bar Option B (Tim-confirmed). Refine via this board.

1. **Shared-main only — no branches, ever.** [LOCKED-10] All sessions commit to one `main`, interleaved. A hidden branch + big-bang merge is the destructive risk (would delete another's stream) — FORBIDDEN. If you ever need isolation, announce on the board first.
   *Grounding kept with the rule:* [FOLD-IN: MC] two worktrees cannot check out the same branch (git forbids it) — which is WHY the shared-main model means one worktree (`/home/tim/company`), not per-session worktrees on `main`. The per-session-worktree era ended on Tim's consolidation call; the divergence ping-pong it caused (re-converge cycles `49debc4`→`f168c6f`→`570b3a3` while cognition worked) is the recorded evidence.

2. **Truth ladder: live gates > git history > claims board > memory.** [LOCKED-10] Rightmost wins on conflict. Memory is NOT on the ladder — the forks duplicated ownership-memory (two sessions each "remembering" they built the convergence work); check the board, not recollection.

3. **Claims board authoritative.** [LOCKED-10] Claim a shared file (`suite.py`/`bridge.py`/`useAppController.ts`/`App.tsx`/`app.css`/`MODE_REGISTRY`/…) before editing — append to § CLAIMS (race-safe), one driver per file, release on commit (with the hash). Loops read § CLAIMS first, every fire. [EARLY-4 absorbed: claim-before-edit, one-driver-per-file, disjoint-files-parallel-is-fine.]

4. **Gate before commit — TWO bars.** [LOCKED-10 item 4 + AMEND folded in]
   - **PER-COMMIT bar** (every shared-file commit): the suites YOUR change affects are green + `drift` green + you introduced NO new red. A suite already red in another lane stays that lane's to fix — record it in `OPEN-REDS.md` (whose + the fix), don't block on it. This lets disjoint lanes commit in parallel without coupling to each other's WIP reds.
   - **PRE-MERGE / CONVERGENCE bar:** the FULL all-green gate (`company suites`, every suite standalone). ALL `OPEN-REDS.md` entries must be CLEARED here. (The gate's own docstring: "a pre-merge gate, not a per-build one.")
   - FORM hook + coherence gates = ONE shared pre-commit suite (structural, adversarial-to-appearance — can't be green-painted). Live precedent: coherence committed `e0a16f2` under the per-commit bar while cognition's `cast_beyond_listening` stayed red in OPEN-REDS.md — disjoint, no new red.

5. **(A) Shared-store-announce.** [LOCKED-10] Any new shared rule (`~/.vi/`, auto-memory) is proposed on the board BEFORE effect — the one cross-fork action that bypasses both the repo diff and the gates (a rule one session writes binds every fork on next load, invisibly).

6. **(B) Flag-tiers.** [LOCKED-10] Cross-fork flags carry their tier — STRUCTURAL (exact, re-derivable) = can BLOCK; SEMANTIC ("smells like our seam") = PROPOSE, adjudicated by the fork owning the live context. (= the engine's own law — structural-acts / semantic-proposes-owner-adjudicates — applied to the builders. Live precedent: coherence's structural flag on the `cast_beyond_listening` red → cognition adjudicated + fixed its own over-specified test, `525e3c8`.)

7. **Standing laws (every fire).** [LOCKED-10] registry-is-truth/no-hardcoding · additive · fail-loud · reflects-never-owns · operator-only floor *(as currently scoped — see the #58 floor-reframe in the scope log: authoring-apply freed, the `claude -p` build-dispatch floor MAINTAINED)* · verify-by-USE never code-reading · NO green-paint (not-confirmable → needs-tim) · surface-don't-defer · don't-spin (blocked → record + exit) · bounded reads · HEAD-check before commit.

8. **The split (file-disjoint by construction).** [LOCKED-10] cognition = the engine (`cognition.py`/`roles.py`/`rules.py`/`activation.py` + C/B/A lanes) · guided-review = the surface/FE/wire (`canvas/app/src` + the surface's bridge routes + generate-for-mockups) · coherence = detectors/gates/disposition-store/calibration/substrate (reads what the others mutate — gates verify, don't collide). `build_coherence_info` = coherence's (their lens, cognition's projection machinery, sibling-not-merge).

9. **The convergence round** (`CONVERGENCE-ROUND.md`). [LOCKED-10] Fires at 3× `lane-complete`. The "merge" = CI-verification over the already-integrated shared-main tree (NOT a git merge). Two cadences: gates continuous per-commit; the full by-use round at the trigger. Two-halves sign-off: the structural gate battery + the by-use operator path. Ownership: cognition = engine seams · coherence = gates system-wide + continuous · guided-review = operator path + orchestrates; JOINT sign-off. [FOLD-IN: MC — the two-halves pattern is the union-gate generalized: in the original unification each session independently verified ITS OWN suite-half on the merged tree before the ff; "each lane verifies its own half" is the load-bearing trust mechanism, kept by name.]

10. **The channel: `MESSAGES.md`** (this folder). [LOCKED-10] Append-only, race-safe `cat >>` (NEVER read-then-Edit — concurrent writers), tagged `### [date] from:<session> to:<all|session> re:<topic>`, poll each fire, read below your own last post. Staggered crons: cognition `0,15,30,45` · guided-review `5,20,35,50` · coherence `10,25,40,55`. The fire is the trigger — no human relay. Full per-fire loop: `AUTONOMOUS-LOOP.md`. **`MERGE-COORDINATION.md` (repo root) is the ARCHIVED relay-era channel — read it as history, never post to it.** [pointer repair]

11. **Readiness gate.** [LOCKED-10, Tim's catch] Loop-preps written before coordination over-claim. Before any build-cron WRITES CODE, each session must: (a) RE-SCOPE its loop-prep to the split (build only its lane; consume the shared seams, don't rebuild them); (b) GROUND its Completion Criteria as a truth-table; (c) POST "loop-prep re-scoped + grounded + ready" on the board. No cron builds until its lane has posted ready — the loops' first job is re-scope + confirm, not build.

12. **Over-share on handoff.** [FOLD-IN: MC — Tim's rule, stated in round 1 and proven repeatedly] *"If it's not captured, it won't be — over-share."* Every cross-session disclosure errs toward MORE: uncommitted residue, latent bugs in the other's territory, things-of-mine-that-touch-yours, honest 🟡/🔴 state. The recorded payoffs: the line-3756 silent-revert catch (no textual conflict, invisible to the owner's own suites), the `[self-apply]`-ledger seam, the `/api/roles` green-suites-but-broken-endpoint catch — each found by the OTHER session's read, none findable from inside its own lane. Suites-green ≠ working is WHY the cross-fork eyes are a standing gate, not goodwill.

13. **New-session onboarding (the three-way procedure, generalized).** [FOLD-IN: MC — currently only in the three-way-opening prose] When a session joins the shared main: (a) it drops a **brief** in this folder (`<NAME>-BRIEF.md`, listed under § BRIEFS) + a **files-touched map** (which files + contracts it will CHANGE — the load-bearing artifact); (b) the existing sessions compute the **overlap map** (read-vs-mutate per touch: synergy / gate / write-collision); (c) lanes are made file-disjoint via § CLAIMS; (d) the shared pre-commit gates bind it from its first commit; (e) it ratifies this protocol on the board before building. **Naming discipline:** every session takes a DISTINCT name (the "interface" label shared by two forked lineages caused the ownership tangle); ancestry confers NO forward-ownership — forks share the past and the persistent stores, the board names the single forward-owner of any contested surface.

14. **Reliability set (what burned us — cognition's ratified additions).** [already in WORK-SPLIT's ratification section; kept adjacent to the law]
    - **Verify the INSTRUMENT, not just the code** (the `events_since(0)`-exclusive near-miss: the verification harness itself was the bug; when a result surprises, distrust the tool + check the raw artifact first).
    - **Commit ONLY your files by explicit path — NEVER `git add .`** (the shared tree always holds other forks' uncommitted in-flight work).
    - **Re-verify the tree yourself; never trust a worker's "done"; NOTHING > PARTIAL** (workers die mid-build and re-edit after verified commits — the lead re-runs the scenario by use before commit; on uncertainty HOLD + document).
    - **Suites-green ≠ working** → the cross-fork gate is the eyes on each lane's blind spot (see 12).

### Per-consumer deltas (kept distinct — different consumers read different slices)
- **The cron loops** read, each fire: § CLAIMS first → new MESSAGES.md entries → items 3/4/7 govern the build step → item 10 governs the post. (Operational detail lives in `AUTONOMOUS-LOOP.md` — the per-fire loop, read-markers, PushNotification discipline. That file is the protocol's RUNTIME, not a duplicate; not consolidated here.)
- **A joining session** reads item 13 first, then the whole law, then ratifies on the board.
- **Tim** reads MESSAGES.md tails + gets PushNotification only on true blockers; his calls are recorded as scope-log entries on this board (the #-series), never as silent protocol edits.
- **The convergence round** reads item 9 + `CONVERGENCE-ROUND.md` + OPEN-REDS.md (must be empty at the bar).

### Proposed archive banner for MERGE-COORDINATION.md (prepend, change nothing else)
> **⚑ ARCHIVED CHANNEL (2026-06-09).** This file is the relay-era coordination record — the verbatim exchange that performed the unification merge, the three-way opening, and the protocol's construction. It is a primary source: do not edit, do not post. The LIVE coordination home is `build-prep/coordination/` — claims: `WORK-SPLIT.md § CLAIMS` · law: `WORK-SPLIT.md § PROTOCOL` · channel: `MESSAGES.md` (append-only, cron-fired, no human relay) · runtime: `AUTONOMOUS-LOOP.md`.

---

## DISPOSITION TABLE (proposed, never executed)

| source file | disposition | detail |
|---|---|---|
| `/home/tim/company/MERGE-COORDINATION.md` | **keep-as-pointer** (keep whole, as archive + primary source; retire only its CHANNEL role) | Prepend the archive banner above. Do NOT move it (19+ docs reference it at root, incl. coherence findings, claude-design research, briefs); do NOT edit its body (it is evidence — truth-ladder item 2 depends on records staying verbatim). Its five protocol-grade strays are folded into § PROTOCOL as items 9-note/12/13 — the prose ORIGINALS stay in place as provenance. |
| `/home/tim/company/build-prep/coordination/WORK-SPLIT.md` | **fold-in** (the file is KEPT as the live board; the consolidated § PROTOCOL above lands INTO it) | (1) Replace the early 4-item "THE PROTOCOL" block with one line: "Superseded by § PROTOCOL (LOCKED) below." (2) Replace the locked items 1–10 + item-11 section + the separated gate-bar section with the single consolidated statement above (which preserves all three verbatim in substance, with provenance marks). (3) Fix the header: channel = `MESSAGES.md`; MERGE-COORDINATION.md = archived record. (4) § CLAIMS, THE LOCKED DESIGN, THE SPLIT, the briefs list, and the entire claims/scope log are UNTOUCHED — they are the live board, not protocol duplication. |
| *(neither file)* | **retire: NONE** | Both organs are needed: the record cannot be regenerated; the board is read every 15 minutes by three loops. The only thing retired is a ROLE (MERGE-COORDINATION-as-channel), which item 10 already retired de facto — this draft just makes it legible at both ends. |

**Adjacent files deliberately NOT in scope** (same family, no duplication found): `AUTONOMOUS-LOOP.md` (the protocol's runtime — referenced, not duplicated), `MESSAGES.md` (the live channel — append-only log), `OPEN-REDS.md` (the cross-lane red ledger item 4 depends on), `CONVERGENCE-ROUND.md` (item 9's full plan), the per-session briefs.

**Risks if adopted:** none structural — both proposed edits are additive-or-marking (a banner; a superseded-marker; a header fix; a re-statement that preserves every ratified clause with provenance). The one judgment call embedded: folding the gate-bar amendment INTO item 4's text changes the locked list's literal layout — the three sessions ratified the LIST, so the re-statement itself should be posted on the board per item 5's spirit (a shared-rule change announced before effect) and nodded by the other lanes before landing.
