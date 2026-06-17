# Proposed diff — GET /api/territory/label?address=… (the V/RHM human aim-label backing)

```
trust: fabric-derived — fork-authored PROPOSED diff for the bridge owner's file (runtime/bridge.py,
projection's hot file). fork does NOT edit bridge.py; projection applies (file-disjoint, meet-at-the-address).
author: ch-8djrpmsl (fork). date: 2026-06-17.
pairs-with: runtime.territory.territory_label (BUILT + verified-by-use + operator-law invariant: NEVER returns
the raw address — degrades to a human scheme-noun). FE caller: fork-v-brain.attach({getAimLabel}) → the V shows
the human "what-this-is" of whatever it's aimed at, never a machine name.
```

> The operator-law backing: the V/RHM shows MEANING, never code/files/machine names. `getAimLabel()` in
> fork-v-brain calls this route with the current aim address → the human one-liner. OPTIONAL — if projection
> already has the human label in its render data, supply that to getAimLabel directly and skip this route.

## Two changes (runtime/bridge.py)

### 1. Add the route to the allowlist (beside the other /api/territory/* routes)
```diff
-    "/api/cognition/create_context", "/api/act", "/api/annotate", "/api/apply", "/api/territory/write",
+    "/api/cognition/create_context", "/api/act", "/api/annotate", "/api/apply", "/api/territory/write",
+    "/api/territory/label",
```

### 2. Add the GET handler (in do_GET, beside the other read routes)
```diff
+            elif path == "/api/territory/label":          # the V/RHM human aim-label (operator-law: never the address)
+                from runtime.territory import territory_label
+                address = (qs.get("address") or [None])[0]
+                if not address:
+                    self._send(400, json.dumps({"error": "address required"})); return
+                self._send(200, json.dumps({"label": territory_label(address, suite=SUITE)}))
```
(adapt `qs`/`path`/`self._send` to the bridge's actual do_GET idiom — territory_label NEVER raises, so no try/except needed.)

## Why it's safe
- Additive READ route (new path; no existing behaviour changes). GPU-free (a registry/structural identity read).
- `territory_label` NEVER raises and NEVER returns the raw address (verified: unregistered-ui leak guarded →
  human scheme-noun; non-address → "this"). So the operator-law holds at the boundary.

## Verify-after-apply
1. GET `/api/territory/label?address=board://item-0af8d61e` → `{label: "THE INTERFACE BRIEF — …"}` (a human title).
2. GET with `address=ui://unregistered/x` → a human noun (e.g. "this part of the surface"), NOT the address.
3. The V panel header shows the label (not the address) and refreshes when Tim re-aims the V.
