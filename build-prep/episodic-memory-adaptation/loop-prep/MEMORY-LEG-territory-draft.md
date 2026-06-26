# MEMORY LEG on territory_for — PROPOSED DIFF (recollection drafts, fork applies — territory.py is fork's lane)

> ★ REFRESH 2026-06-18 (the unification EARLY-WIN #1): re-verified against the CURRENT territory.py.
> INSERTION POINT MOVED: insert before `return terr` (now **line 224**, right AFTER the `library` leg's
> `legs_present["library"]` at 222), mirroring the library-leg pattern. ANCHOR CONFIRMED: fork added
> `decision` to `_RESOLVABLE` (territory.py:36), so `terr["identity"]` IS the decision row WITH `meaning`
> for a decision:// address (verified: identity_kind='decision.record', meaning present). recall_for_decision
> composes against the live rows (substrate-home → 10 context + 6 prior_decisions, rerank fires). The leg
> code below is unchanged + paste-ready against the current file.

*Step-6 of the decision-surface (the common-memory recall leg). UNBLOCKED 2026-06-18 by fork's decision:// resolver (97be816). Resolution-first: a decision's explanation RESOLVES through recall, not stored. recall_for_decision (committed 3b5107a) is the compute; this is the LEG that folds it into territory_for → territory_prose → the RHM explains grounded. PROPOSED — not applied (fork's lane + the build-order puts step-6 after render/host/take; this is ready for fast pickup).*

## THE LEG (insert before `return terr` at territory.py:169, mirroring the scheme-gated `library` leg)
```python
    # ── MEMORY leg (decision:// → the RHM's explanation grounding; guarded → degrade-clean, 2026-06-18) ──
    # The decision-surface explain-half: a decision's explanation RESOLVES through recall, not stored
    # (resolution-first). recall_for_decision composes the corpus-grounded bundle (multi-space + rerank +
    # prior-decisions) the RHM explains FROM. Keyed on decision:// so the HEAVY bundle is NOT every turn —
    # only when a decision is explained. Reuses the committed compute; guarded → a down embedder/space
    # degrades clean (never kills the explain turn — the never-raises contract holds).
    if sch == "decision" and suite is not None:
        try:
            from runtime.decision_memory import recall_for_decision
            ident = terr.get("identity") or {}
            anchor = ident.get("meaning") if isinstance(ident, dict) else None   # VERIFIED: decision:// row → {meaning,...}
            # the neighbour leg wants the decision's SUBJECT (a code:// embedded unit), NOT the decision://
            # address itself (a registry row, no persisted vector). Use the subject if the row names one
            # (decides_on/subject/explanation_source if code://), else None (skip neighbours — verified: a
            # decision:// to neighbours degrades clean but is a noisy no-op).
            subj = None
            if isinstance(ident, dict):
                cand = ident.get("decides_on") or ident.get("subject") or ident.get("explanation_source")
                if isinstance(cand, str) and cand.startswith("code://"):
                    subj = cand
            if anchor:
                terr["memory"] = recall_for_decision(suite, anchor, address=subj)
        except Exception as e:
            terr["notes"].append(f"memory leg unresolved ({type(e).__name__}: {e})")
    terr["legs_present"]["memory"] = bool(terr.get("memory"))
```

## RENDER in territory_prose (add a block beside "Details"/"Connections")
The memory leg → human prose for the RHM's explanation:
- `terr["memory"]["context"]` → "What's known about this:" (the grounded context items — render the digest/meaning, NOT the source ids; legibility).
- `terr["memory"]["prior_decisions"]` → "Decided before:" (the resurfacing — "you've ruled on this before").
- `terr["memory"]["neighbours"]` → "Related:" (the node-field).
So the RHM's explain turn (territory_prose folded in at bridge.py:1697) arrives GROUNDED + cite-able.

## ★ TO CONFIRM with fork (the one coupling)
- The decision-row field the identity leg exposes as the recall ANCHOR: I assume the resolved row's `meaning` (the human decision text). Confirm decision://'s identity shape (meaning/content/text?) so `anchor` reads the right field. (If the row nests under a key, adjust the `ident.get(...)`.)
- The explain-wire choice (Q1): fork said BOTH paths compose — explanation_source→territory_prose→brain OR /api/cognition/recall-for-decision. This leg is the territory_prose path (auto-grounds every decision:// resolve). If projection's route is preferred instead, the same recall_for_decision compute serves it — no conflict.

## SCOPE / ORDER
- THIS leg = the decision-explain path (heavy bundle, keyed decision://). The CHEAP universal neighbours-leg (every turn, any address) is a SEPARATE smaller follow-up (I'll draft it after the decision path proves) — don't fold the heavy recall into every turn.
- recollection owns recall_for_decision (committed); fork owns territory.py (applies this leg); projection owns the optional /api/cognition/recall-for-decision route. No parallel — one compute, the resolved leg.
- Verify-by-use when applied: resolve a decision:// → territory_prose carries the grounded context + prior-decisions; a down space degrades clean (note, no crash).
