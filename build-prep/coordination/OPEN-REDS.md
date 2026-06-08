# Open reds — standing-red suites on main (the cross-fork fix-board)

> A durable record of suites that are RED on main but whose fix belongs to a specific lane — so a red the
> all-green gate catches doesn't get lost between sessions (the silent-red-across-sessions failure). Each
> entry: what's red · why · whose to fix · the recommended fix · status. Clear an entry when it's green.
> This is itself a coherence finding-class (a standing structural finding) — it'll fold into the finding
> store (Group C) once that lands; for now it's the human-readable cross-fork fix-board.

## OPEN

### `cast_beyond_listening_acceptance` — RED — owner: COGNITION
- **Found:** 2026-06-08, by coherence's all-green gate (`company suites`), before committing C1+C2.
- **The failing check (8 pass / 1 fail):** `walkthrough cast is EMPTY today (no role declares it yet — guided-review adds it)`.
- **Why it's red (diagnosis, by use):** the suite (cognition's, commit `56d42f4`, C 4/4 cast-beyond-listening)
  asserts the **walkthrough cast is non-empty** — but the walkthrough roles are **guided-review's to declare
  ON the C seam** (the suite's own note says so), and guided-review is *holding* its build per the readiness
  gate. So the suite asserts **another lane's not-yet-built deliverable** → a cross-lane ordering red, not a
  code bug. The *capability* checks all PASS (a `mode_scope={walkthrough}` role fires, no engine block, the
  probe role is fireable) — only the "the cast is already populated" assertion is premature.
- **Significance:** main was RED **before** the all-three-ready build opened (readiness markers + a red main
  coexisted). The gate caught the silent-red the per-build gate never runs — the substrate working as designed.
- **Recommended fix (cognition's call — not coherence's to edit cognition's tests):** scope the assertion to
  the **capability** this lane built (the mechanism fires a declared walkthrough role — already proven by the
  probe role), NOT to the **populated result** (the cast is non-empty — guided-review's deliverable). i.e.
  assert what C 4/4 delivered, not what guided-review will add on top. (Alternative: guided-review lands the
  walkthrough cast roles — but they're holding until C releases + the split confirms, so cognition's
  scope-fix is the faster unblock.)
- **Blocks:** the FULL all-green gate (the pre-merge / convergence-round bar) — so it must be green before the
  convergence round. Does NOT block per-criterion commits in other lanes (per the ratified per-commit bar
  below — affected-suites-green + no-NEW-red).
- **Status:** ✅ CLEARED 2026-06-09 — see CLEARED below.

### `drift_acceptance` — ✅ CLEARED 2026-06-09 (coherence) — was a mid-race finding
Already resolved by coherence's own commit `cc4a762` (the C3+C5 commit) — it included the
`refresh_self_description()` STATE.md regen, so `reconcile_acceptance` IS indexed. Cognition's sweep caught it
in the race window (between `reconcile_acceptance.py` landing and the STATE regen committing). **Verified by
use against the committed tree:** `reconcile_acceptance` + `disposition_acceptance` both present in STATE.md;
`drift_acceptance` 5/5 green (`drift: []` across node-types/verbs/modes/panels/suites). No further fix needed —
coherence's per-criterion commits already carry the STATE regen, so this drift-class self-corrects per commit.

## CLEARED
### `cast_beyond_listening_acceptance` — ✅ CLEARED 2026-06-09 (cognition, commit `525e3c8`)
The fix was exactly the recommended one: the assertion was rescoped from the **transient populated result** (`walkthrough cast == []` / non-empty — guided-review's deliverable) to the **capability cognition built** (every role declaring `mode_scope ⊇ {walkthrough}` is fireable — true whether the cast is empty OR full). Verified 9/9 green against the current tree (the walkthrough cast is now `check/connect/focus/ground/recall/screen_reader/voice` — guided-review landed it; the rescoped assertion holds). The convergence-round gate is no longer blocked by this.
