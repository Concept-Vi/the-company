# Registry-Coverage Audit — findings (the "what's not in a registry but should be" test)

> Tim's test (2026-06-09): use the models to scan the whole repo for everything that should be registry-driven but is hardcoded. The hard part (his warning): "small models can't make judgement/subjective calls freely." This is the by-use result + the composition lesson it earned.

## The composition that worked (the earned design)
```
TIER-1 EXTRACT (deterministic): whole-repo scan → 39 candidate vocabulary-literals (from thousands of files)
TIER-2a OVERLAP (DETERMINISTIC set-compare — the FIX): a literal's members ⊆/∩ an authoritative member-set
         (12 file-discovered registries + the closed grammars SCHEMES/_SAMPLING_KEYS/CONTENT_KINDS/...)
TIER-2b KIND-CALL (the 4B — the ONLY model call): vocabulary vs incidental
TIER-3 CANDIDACY (escalate to Tim): "should this vocabulary be its OWN registry?" — the subjective call
```

## What the test PROVED (two confirmations of Tim's thesis)
1. **The deterministic overlap is grounded; the model overlap hallucinated.** The loose first run let the 4B guess overlaps → 7 HALLUCINATED (`idle/ready→contexts`, `role/rule→roles`, …). The tightened run set-compares against the real member-sets → **3 findings, zero hallucination.** The fix holds.
2. **Even the NARROW binary kind-call is unreliable on the 4B.** It labelled 34/39 literals "vocabulary" — including field-name tuples, method-name pairs (`load_voice/unload_voice`), CLI verbs (`up/restart`), booleans (`on/off`). So the model tier adds NOISE here; the deterministic tier carries the signal. **Lesson: in registry-coverage, push the judgement to deterministic set-compare; the model's contribution is marginal; the candidacy is Tim's.**

## ★ TIER-1 FINDINGS — deterministic, high-confidence (registry-is-truth violations to fix)
- **`runtime/suite.py:2231`** `("temperature","max_tokens","top_p")` — **subset of `_SAMPLING_KEYS`** (fabric/transport.py). Should reference `_SAMPLING_KEYS`, not hardcode.
- **`runtime/suite.py:5653`** `("temperature","max_tokens","top_p")` — **subset of `_SAMPLING_KEYS` AGAIN** (a 3rd copy of the sampling-key vocabulary). ← found only because deterministic-overlap is exhaustive.
- **`runtime/authoring.py:494`** `("skill","context")` — **subset of `SCHEMES`** (skill://, context://). The entity-kind test should derive from SCHEMES.

## ★ UNIFICATION findings (LAW-0 — the "no humans hold the picture → fragmentation" problem, found by use)
The same vocabulary hardcoded in multiple places (built-twice/thrice):
- **sampling-keys × 3:** fabric `_SAMPLING_KEYS` (authoritative) + suite.py:2231 + suite.py:5653.
- **`("plan","apply")` × 2:** bridge.py:2028 + generate_mockup.py:306.
- **`("propose","panel","extend")` × 2:** suite.py:4254 + suite.py:4648.
→ each should be one source. These are the exact AI-fragmentation Tim's unification law targets.

## TIER-3 — ESCALATE TO TIM (the candidacy call is yours; my judgement-seat triage of the 34)
The model dumped 34 into "vocabulary"; most are incidental by shape. The GENUINE domain-vocabulary candidates worth your call (could each be a small registry or a one-sourced closed-grammar):
- `("responsive","generative")` governance.py:158 — origin polarity
- `("pending","applied","dismissed")` bridge.py:2002 — a status lifecycle
- `("resolved","pruned","failed")` rules.py:340 — run-states
- `("switched","suggested")` activation_driver.py:212 — detection outcomes
- `("role","rule","cluster")` cognition.py:1775 — the reduce-modes (referenced by the MCP tool; one-sourced nowhere)
- `("generate","embed")` roles.py:173 — the op-axis (the B5 selects reference it; hardcoded)
- `("plan","apply")` / `("propose","panel","extend")` — the duplicated ones above (unify first, then decide registry)
The rest (field-name tuples like `("verb","name","tool")`, method pairs, CLI verbs, `on/off`, `true/false`) read as **incidental** — correctly NOT registries.

## The ⑫ backlog this produced
- Fix the 3 deterministic violations + the 3 built-twice dups (reference the one source) — a careful suite.py/bridge.py edit (hot files; a future beat).
- The composition lesson → SYSTEM-GAPS: registry-coverage = deterministic-overlap-primary; the model kind-call is low-value, consider dropping it or replacing with a deterministic shape-heuristic (field-name-tuple detector, CLI-verb detector).
