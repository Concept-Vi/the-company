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

### `ui_registry_acceptance` — RED — owner: UI-REGISTRY / CANVAS lineage (NOT a cognition breach)
- **Found:** 2026-06-09, by Group I (cognition mode-detector lane) running `suite_health_acceptance` as part of its verification sweep. Not introduced by this lane (Group I touched only `runtime/activation.py` · `runtime/suite.py` · `runtime/mode_detection_rules.py` + tests — no canvas/UI/registry files).
- **The failing check:** `ORPHAN CHECK: zero LIVE-app used-but-unregistered data-ui-ref` — orphans: `ui://settings/cognition` · `ui://studio/rhm/read` · `ui://studio/stage/whole`.
- **Why it's red (diagnosed, by use):** three `data-ui-ref` addresses are carried in the LIVE app DOM but are **not in the UI registry corpus** (`design/_system/addresses.json` → `UI_REGISTRY` / `/api/ui_info`). The orphan check (`ui_registry_acceptance.py`) asserts **every app/mockup `data-ui-ref` has a registry entry** (used-but-unregistered = 0), and these three fail it. Exact sites:
  - `ui://settings/cognition` — `canvas/app/src/regions/Settings.tsx:557` (a settings section)
  - `ui://studio/rhm/read` — `canvas/app/src/components/StudioKit.tsx:344` (the RHM read button)
  - `ui://studio/stage/whole` — `canvas/app/src/components/StudioKit.tsx:225` (a studio stage dev button)
- **Significance:** this is plausibly part of the "a lot now not connected in the UI" the operator reported — element addresses that ship in the DOM but aren't registered can't be addressed/clicked-to-indicate / resolved via the S1 element registry. It's the same registry-is-truth orphan class S1 closed for the original 68 corpus addresses; these three are new app-carried refs that drifted ahead of the corpus.
- **Recommended fix (UI lane's call — not cognition's to edit the registry corpus / canvas):** register the three addresses by adding them to the corpus (`design/_system/addresses.json`, the rule-8 source the `UnionAddressRecord.from_corpus` projection reads) with their caps/region, the SAME way the app-carried `walkthrough` + `deferred-queue` handles were registered to close the earlier orphan gap (see STATE.md, the addressed-surface S1 entry). Then `/api/ui_info` serves them and the orphan check returns to zero. (Verify the three are intended live elements first — if any is a dev-only/throwaway button, the alternative is removing its `data-ui-ref`, not registering it.)
- **Blocks:** the FULL all-green gate (`suite_health` / the convergence-round bar) — must be green before the convergence round. Does NOT block per-criterion commits in other lanes (the per-commit bar = affected-suites-green + no-NEW-red).
- **Status:** OPEN — flagged for the UI-registry / canvas session.

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

### `drift_acceptance` — RED on `generate_mockup_acceptance` (mockup-build lane's, NOT cognition's) 2026-06-09
`drift_acceptance` is RED with `drift: ['generate_mockup_acceptance']` — the mockup-build session's
untracked `tests/generate_mockup_acceptance.py` + `runtime/generate_mockup.py` exist on disk but the suite
isn't yet in STATE.md's SUITES block. **Owner: the mockup-build lane** (its STATE regen / commit clears it,
same self-correcting drift-class as above). NOT introduced by #58 DIRECT-create — my new
`direct_create_acceptance` IS reflected in STATE (the by-use refresh_self_description regenerated it). My #58
per-commit bar is met (the suites #58 affects are green; I introduced no new red). Recorded per the
per-commit-bar protocol; do not block #58 on it.

### `wire_trigger_acceptance` — RED — owner: WIRE/INTERFACE lineage (NOT a cognition breach)
- **Found:** 2026-06-09. Fails on "dispatch_decision is NOT exposed as an MCP tool" (and resolve_surfaced / claude -p).
- **Why (diagnosed):** the test STRING-SCANS `mcp_face/server.py` SOURCE for the floor tokens (`"<token>" not in src OR "<token> is NOT" in src OR "not exposed"`). #58's floor-REFRAME comments legitimately MENTION resolve_surfaced/dispatch_decision/claude-p to DOCUMENT the floor → the heuristic false-positives on the comment. **NOT a breach:** no tool exposes them; `cognition_governance_acceptance` 30/30 confirms via an AST scan (the right way).
- **Fix (wire's):** make wire_trigger's "off-face" check AST-based (scan for actual `@mcp.tool` defs / calls), like `cognition_governance`'s COG_SOURCES — not a string-match over comments. (Cognition can't cleanly satisfy a comment-scanner without deleting accurate floor documentation.)
- **Status:** OPEN — flagged for the wire/interface session. Does NOT block cognition's gate (governance 30/30 green).
