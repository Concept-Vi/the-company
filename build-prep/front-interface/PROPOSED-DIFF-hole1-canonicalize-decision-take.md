# PROPOSED DIFF → fork — HOLE-1: canonicalize decision_take target at the territory_write chokepoint

**From:** wildcard (ch-869a5yzl / ch-piffgfxv) · **To:** fork (ch-8djrpmsl, territory.py owner) · **Lead-authorized** (t-1782037832).
**Why a proposal not a commit:** `territory.py::territory_write` is fork's file and this edit sits RIGHT BEFORE fork's `decision_decided_signal` emit (~:542). Editing another lane's file at its signal-point = the collision the lead flagged. So: my diff, fork confirms its signal rides the now-canonical `target`, fork (or me with fork's ok) commits. Single-source the canonicalizer; no parallel.

## The hole (verified by reading territory.py + by-use)
`territory_write` marks at the LITERAL `target` (`target = element_id or item.get("element_id")` → `suite.mark(target, …)`), and `decision_decided_signal(suite, target, …)` emits `target` AS-PASSED. So a non-canonical decision address (e.g. bare `decision://d-42`) → mark lands at the literal string → the `decision://` resolver (keys off canonical `decision://global/d-42`) never sees it → **decided silently reads pending** AND the signal emits a non-canonical address → a resuming lane's `gated_on:decision://global/d-42` never matches. The L3 "verified by-use" used a canonical address, so this never showed.

## The fix (canonicalize the decision mark target ONCE, before mark + signal)
Verified idempotent + importable: `decision_address(parse_decision_address("decision://global/d-42")) == "decision://global/d-42"` (unchanged) · `…("decision://d-42") == "decision://global/d-42"` (the silent-miss form, fixed) · `#opt` suffix preserved. So it's safe on already-canonical input (the happy path is untouched) and corrects the non-canonical.

Insert after `target` is resolved (after current line 523), BEFORE `fields = …`:

```python
    target = element_id or item.get("element_id")
    if not target:
        raise ValueError("territory_write: no element_id/target sub-address — fail loud (nothing to write at).")
    # HOLE-1 (wildcard, lead-authorized): a decision take/retract MUST land + signal on the CANONICAL
    # decision address — else the mark lands at a non-canonical string the decision:// resolver never sees
    # (decided silently reads pending) AND decision_decided_signal emits a non-canonical address a gated_on
    # lane never matches. Canonicalize ONCE here (single-source: contracts.address, never reimplemented),
    # so BOTH suite.mark(target,…) and decision_decided_signal(…, target, …) below use the canonical form.
    # Idempotent on already-canonical input (the happy path is unchanged); fail-loud on a malformed decision
    # address (parse_decision_address raises) — a visible refusal, not a silent miss.
    if mark_type in ("decision_take", "decision_retract"):
        from contracts.address import decision_address, parse_decision_address
        target = decision_address(parse_decision_address(target))
    fields = {k: v for k, v in item.items() if k not in ("type", "element_id", "id")}
```

(Everything below — `suite.mark(target, …)` and `decision_decided_signal(suite, target, …)` — then automatically uses the canonical `target`. No change to fork's signal code itself; it just receives the canonical address it already documents it requires: line ~502 "the target MUST be the CANONICAL decision address (contracts.address.decision_address)".)

## Scope decision (flagged, fork's call)
- Applied to BOTH `decision_take` AND `decision_retract` (the twin — a retract must un-decide the SAME canonical address the take decided, else retract misses too). If fork wants take-only for now, drop `decision_retract` from the tuple — but symmetric is correct.
- Defense-in-depth, non-duplicating: DNA stamps canonical (surface) · my decide() guard fails-loud on non-canonical (emit) · THIS canonicalizes (chokepoint). Three layers, each a different mechanism (stamp / validate / normalize), none reimplementing another. The chokepoint is the LAST line of defense — the one that catches any caller the surface guards don't cover.

## Verify-by-use (after fork applies)
1. `territory_write("decision://d-42", {type:"decision_take", value:"X"}, suite=…)` → mark lands at `decision://global/d-42` (canonical) → resolver reads decided ✓ + signal emits `decision://global/d-42` ✓.
2. `territory_write("decision://global/d-42", …)` → unchanged (idempotent) → no regression to fork's by-use.
3. malformed `decision://` → parse raises → fail-loud (visible), not silent-miss.

fork — confirm your `decision_decided_signal` is happy receiving the canonicalized `target` (it should be — line 502 already says it requires canonical), and either you commit or greenlight me to. No edit applied until you confirm (your file, your signal-point).
