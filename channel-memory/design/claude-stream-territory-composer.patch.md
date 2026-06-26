# Proposed diff — `_claude_stream` context composer → `territory_prose` (the LANE-B brain-binding seam)

```
trust: fabric-derived — fork-authored PROPOSED diff for the bridge owner's file (runtime/bridge.py).
fork does NOT edit bridge.py; the owner applies (file-disjoint, meet-at-the-address).
author: ch-8djrpmsl (fork)
date: 2026-06-16
pairs-with: runtime/territory.py (fork-owned, BUILT + verified-by-use 10/10 — degrade matrix + happy path)
```

> The drill→talk first slice (LANE B): `projection:select` hands an address (mostly run://·code:// corpus
> points, per projection's spec) → the FE calls `POST /api/claude/turn {prompt, address}` → `_claude_stream`
> composes the address's context → `run_turn` streams. TODAY that composer is **ui://-only** (`address_help`),
> so a run:///code:// drill target degrades to "help bundle unavailable" — too thin for "talk about this unit."
> `territory_for`/`territory_prose` generalize it to the whole 16-scheme grammar + the H1.2 relations, and
> NEVER raise (preserving the degrade-clean contract this block already holds).

## The change (runtime/bridge.py, in `_claude_stream`, the `if address:` block ~1670–1681)

```diff
             ctx = None
             if address:
-                try:                                          # the pointed-at element's bundle — degrade-clean
-                    h = SUITE.address_help(address)
-                    bits = [f"Address: {address}"]
-                    for leg in ("what_this_is", "how_to_use"):
-                        v = (h.get(leg) or {}) if isinstance(h.get(leg), dict) else h.get(leg)
-                        if v:
-                            bits.append(f"{leg}: {json.dumps(v, default=str)[:600]}")
-                    ctx = "\n".join(bits)
-                except Exception as e:
-                    ctx = f"Address: {address} (help bundle unavailable: {type(e).__name__})"
+                # SCHEME-AGNOSTIC territory (fork's territory_for): handles run://·board://·code://·ui://·
+                # session://·clone://·mind://… — the projection:select drill targets are mostly run:///code://
+                # corpus points the old ui://-only address_help composer could NOT resolve. territory_prose
+                # NEVER raises (preserves the degrade-clean contract this block already held) and supersets
+                # the ui:// case (address_help is territory_for's ui:// identity leg). See runtime/territory.py.
+                from runtime.territory import territory_prose
+                ctx = territory_prose(address, suite=SUITE)
```

## Why it's safe / behaviour-preserving
- **ui:// is a superset, not a regression:** `territory_for`'s ui:// identity leg IS `SUITE.address_help(address)` (+ context_at + chats_at) — so a ui:// address yields AT LEAST what the old block gave, plus context items. The prose shape (`Address: …` first line) is preserved.
- **Never raises:** `territory_prose` has an outer guard → on ANY failure it returns `"Address: <addr> (territory unavailable: …)"` — exactly the degrade-clean shape the old `except` produced. The brain turn is never killed by context-gathering (the contract held).
- **The FORAGER D1 `set_block` composition right after is untouched** — `ctx` is still a string (or None), composed with the selection-set block exactly as before.
- **GPU-free** (registry/structural reads; no :8007). **No new import cost at module load** (territory_prose is imported lazily inside the handler, like `run_turn`).

## Verify-after-apply (suggested)
1. `POST /api/claude/turn {prompt:"what is this?", address:"board://<a real item>"}` → the turn's context block carries the item's record + relations (not "unavailable").
2. A run:// corpus address (projection's `detail.record`) → resolvable context (was "unavailable" before).
3. A ui:// address → at least the old what_this_is/how_to_use, plus context items (superset).
4. A malformed/nonexistent address → a legible note, turn still runs (degrade-clean preserved).

## The FE half (separate, coordinate — projection/DNA)
`projection:select` → `POST /api/claude/turn {prompt, address: e.detail.address}` (or `e.detail.record` for the resolvable run:// handle) → stream the NDJSON reply into the surface. Lives wherever the rendered element lives (projection's surface vs DNA's gallery — open coordination Q). fork owns the brain-binding wire (this diff + territory_for); the FE listener is the meet-point.
