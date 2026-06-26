# Proposed diff — POST /api/territory/write (the route-back write endpoint, hook 2's backend)

```
trust: fabric-derived — fork-authored PROPOSED diff for the bridge owner's file (runtime/bridge.py,
projection's hot file). fork does NOT edit bridge.py; projection applies (file-disjoint, meet-at-the-address).
author: ch-8djrpmsl (fork)
date: 2026-06-16
pairs-with: runtime.territory.territory_write (BUILT + verified-by-use — live mark round-trips for
comment/reaction/favour; mock mapping 19/19; mark_types acceptance 29 checks). FE caller:
build-prep/front-interface/fork-gallery-brain-hooks.js (hook 2).
```

> The route-back: `gallery:direction` (wildcard's binder) → fork's hook 2 groups by element_id → POST
> /api/territory/write `{element_id, items:[…]}` → `territory_write` each → `suite.mark` at the sub-address →
> the FE emits `gallery:rerender`. This is the WRITE backend; the READ (territory_prose) diff is the sibling.

## Two changes (runtime/bridge.py)

### 1. Add the route to the allowlist (~bridge.py:55–68, beside `/api/annotate`)
```diff
-    "/api/cognition/create_context", "/api/act", "/api/annotate", "/api/apply",
+    "/api/cognition/create_context", "/api/act", "/api/annotate", "/api/apply", "/api/territory/write",
```

### 2. Add the POST handler (in do_POST, beside `/api/annotate` ~2517)
```diff
+            elif self.path == "/api/territory/write":    # route-back: persist gallery:direction at sub-addresses
+                # fork's territory_write → suite.mark (scheme-agnostic; the element_id sub-addresses are code://
+                # corpus units, which the ui://-gated annotate would reject). Fail-loud on a bad item → 400.
+                from runtime.territory import territory_write
+                b = self._body()
+                element_id = b.get("element_id")
+                items = b.get("items") or ([b.get("item")] if b.get("item") else [])
+                recs = [territory_write(element_id or it.get("element_id"), it, suite=SUITE) for it in items]
+                self._send(200, json.dumps({"ok": True, "written": len(recs), "marks": recs}))
```

## Why it's safe
- Additive route (new path; no existing behaviour changes). `territory_write` fail-louds on a missing type/target → the bridge's existing try/except → a 400 (parity with `/api/annotate`).
- `suite.mark` is the company's scheme-agnostic addressed-write (NOT vi-visual's /api/submit_response, NOT the ui://-gated annotate) — the element_id sub-addresses (code://unit#elem) write cleanly. The 3 direction mark_types (comment/reaction/favour) are registered (additive, lead-authorized; acceptance 29 checks).
- GPU-free (a store append). Re-render reads `marks_for(element_id)` (= `runtime.territory.territory_directions_at`).

## Verify-after-apply
1. POST `/api/territory/write {element_id:"code://x#el-1", items:[{type:"comment",annotation_type:"direction",text:"clearer"}]}` → `{ok:true, written:1}`; then `suite.marks_for("code://x#el-1")` shows the comment mark.
2. A bad item (no type) → 400 (fail-loud), turn not silently swallowed.
3. The FE hook 2 (fork-gallery-brain-hooks.js) POSTs `{element_id, items}` → emits `gallery:rerender` on success.
