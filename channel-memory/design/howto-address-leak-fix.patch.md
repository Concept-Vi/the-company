# Proposed diff — operator-law fix: the how-to context item leaks a raw address

```
trust: fabric-derived — fork-authored PROPOSED diff for runtime/suite.py (shared/co-scoped; fork proposes,
the suite.py owner / lead applies — met-at-the-address, not a unilateral edit to a shared hot file).
author: ch-8djrpmsl (fork). date: 2026-06-17.
found-by: projection (ch-piffgfxv) by-use — the drill-in inspector's context bundle showed
"[how-to @ ui://canvas] WHAT: …" to the OPERATOR. operator-law: Tim NEVER sees code/files/machine-names
([[feedback-translate-everything-human-meaning]]).
```

## The leak (one line)
`runtime/suite.py:3738` — `Suite._r2_howto_at` composes the how-to R2 context item and embeds the **raw
address** into the operator-facing `text`:
```python
return [{"kind": "howto", "address": address,            # ← the address ALREADY rides here (programmatic)
         "ts": now.isoformat(),
         "text": f"[how-to @ {address}] {text}",          # ← LEAK: the raw scheme:// surfaces to the operator
         "pinned": True}]
```
It's a **composed prefix**, NOT authored corpus content (so it's a context-composition fix, not a content
edit). The address is **already** available in the sibling `"address"` field — embedding it in `text` is
redundant AND the leak.

## The fix (drop the raw address from operator-facing text; keep it in the sibling field)
```diff
-                 "text": f"[how-to @ {address}] {text}",
+                 "text": f"[how-to] {text}",          # operator-law: no raw address in operator-facing text;
+                                                      # the address stays in the sibling "address" field (programmatic)
```
Zero loss of traceability (the `"address"` field is untouched, line 3736) — only the operator-VISIBLE text
stops leaking the scheme://. If a HUMAN locator is wanted in the text instead of nothing, use
`runtime.territory.territory_label(address)` (the human "what-this-is", address-safe) — but the minimal
operator-law fix is just dropping `@ {address}`.

## Why it's safe
- One line, in the R2 howto-context composer (`_r2_howto_at`) — NOT the run_swarm firing path (no R13
  byte-identical concern). The item shape is unchanged except the `text` string.
- Programmatic consumers read `item["address"]` (unchanged); only the rendered text changes.

## Verify-after-apply
1. GET `/api/context` for a ui:// unit → the how-to item's `text` shows "[how-to] WHAT: …", NO "ui://…".
2. `item["address"]` still carries the address (programmatic traceability intact).
3. (Operator-law sweep): no `scheme://` in any operator-facing `text` across the context bundle.
