# THE RESOLVER CONTRACT — the authoring layer over `resolve()`
*composition-owned (the type/contract lane). The AUTHORING contract over fork's `runtime/resolver.py` primitive: how a COORDINATE maps to ALLOCATION (projection's device-axis) and to PROMPT+SCHEMA (fork's resolved-slots). The shared doc projection · fork · DNA · composition all author TO. Co-shaped with projection (t-1782002441) + fork (t-1782002567). Reuse-don't-parallel: the engine is `resolve_slot` — this adds NO mechanism (one optional template wrapper, §2).*

> The primitive (fork, runtime/resolver.py): `resolve(invariant, coordinate) → {slot: value}`, pure, fail-loud. A slot is a CONTINUOUS relationship-AST (`{op,args}` → rules.evaluate) OR a DISCRETE select (`{select:<path>, cases:{}, default?}`) OR a literal. This contract is the AUTHORING shapes over that — never a re-implementation.

## §1 · THE COORDINATE (orthogonal axes; axes-are-registries → a new axis = a row, no engine code)
The coordinate is `{axis: value}`. Confirmed-reliable + honest flags (projection, browser-grounded):
- `device.w`, `device.h` — raw live window dims. ✓ the ROOT of all continuous derivations.
- `device.orient` — `'portrait'|'landscape'`, derived `h>w`. ✓ reliable. (★ "desktop" is NOT a third enum — it's `orient:landscape` + a size threshold; orthogonal axes, not a 3-way collapse.)
- `device.kind` — `'native-mobile'|'desktop'`: ⚠️ NOT AUTHORITATIVE in a browser. Derive a size/pointer bucket (a `select` on w/h, optionally `pointer:coarse`/`maxTouchPoints` as a weak hint). Usable as a derived discrete; do NOT contract it as a true platform signal.
- `viewer.expertise` — `'novice'|'pilot'` (the control-density axis): ✓ the NEXT axis. No value-source exists yet (no operator mode/settings state). → wire the coordinate slot now, value PENDING; do NOT gate the device-axis migration on it.
- `resolution` — `'coarse'|'medium'|'fine'` (the grain axis; read-side; §5). Other axes (mode·perspective·intent·state·posture·register) plug in identically when a value-source exists.

## §2 · THE SLOT GRAMMAR (reuse fork's `resolve_slot` — no new mechanism)
- CONTINUOUS (size-derived): a relationship-AST over the coordinate — `clamp(mul(field device.h, 0.4), 80, sub(field device.h, 56))`. The value DERIVES; no breakpoint.
- DISCRETE (render-family / category pick): `{select:'device.orient', cases:{portrait:…, landscape:…}, default:…}` — a row-lookup by the coordinate's value. Fail-loud if no case + no default.
- LITERAL: a fixed value (degenerate relationship).
- ★ PROMPT TEMPLATE (the ONE optional addition, §5): a string with `{{name}}` placeholders, each a resolved sub-slot — resolve each, interpolate. A thin wrapper over `resolve_slot`, only if continuous prompt composition is wanted; otherwise `select` covers it. (fork to confirm want/skip.)

## §3 · ALLOCATION INVARIANTS — the DEVICE-AXIS (kills the hand-enumerated 3 modules → ONE invariant)
The host's layout + the card's layout are allocation-invariants resolved by the SAME `resolve()` against the SAME coordinate. The 3 hand-modules `layouts/{Desktop,Portrait,Landscape}` → ONE invariant (orient = a discrete select; size = continuous derivations).
HOST invariants (projection authors TO this; grounded in live CSS):
- MODAL: `pad_top = clamp(mul(field device.h, 0.02), 4, 16)` (continuous reclaim-by-height) · `pad_x = select device.orient {portrait:0, landscape:12}` · `frame_max_h = sub(field device.h, <chrome>)` · `frame_full_width = select device.orient {portrait:true, default:false}` · `frame_radius = select device.orient {portrait:'top-only', default:'all'}` · `overlay_align = 'safe center'` (literal).
- SHELL: `shell_stack = select device.orient {portrait:'column', landscape:'row'}` (+ rail when wide) · `rail_w = clamp(mul(field device.w, 0.3), 220, 300)` · center/wheel sizes continuous on device.w/h.
CARD invariant (composition authors; §4).

## §4 · THE CARD-SEAM (one mechanism, host + card)
The decision-card's zone allocation (present/explain/choose — `card_kinds`) resolves on the SAME coordinate via the SAME `resolve()`. CO-VISIBLE-vs-STEPPED is a RESOLVED slot, not a stored variant:
- `card_layout = select <coordinate> {…}` → `'co-visible'` at roomy coordinates; `'stepped'` ONLY if a tight coordinate forces it. (The grouping is `card_kinds`; the resolver picks the rendering.)
- ★ THE merge-sa KEYSTONE GATE, made concrete: "merge-sa co-visible at 390" = the 390-coordinate resolves `card_layout → co-visible`. The gate is a resolver assertion.
- The card ZONE values (the specific dimensions per kind) are composition's to author — but PENDING DNA's merge-sa zone rework (lead); author the SEAM (card_layout resolves) now, pin the zone numbers after her rework lands.

## §5 · PROMPT + SCHEMA AS RESOLVED VARIABLES (fork's resolved-slots — the gate)
A prompt and a schema ARE resolvable-variable types, resolved at RUN/READ time (NOT baked — the dragnet grain is read-side; recollection's bake stored the rich superset once):
- SCHEMA-slot: `{select:'resolution', cases:{coarse:[fields], medium:[…], fine:[…]}}` — grain → field-set (a subset projection of the stored superset; coarse ⊂ medium ⊂ fine). Discrete → `select`, verbatim.
- PROMPT-slot: literal | `{select:<axis>, cases:{…}}` (pick a prompt by viewer/mode/subtype/grain) | TEMPLATE (§2, placeholders = resolved sub-slots).
- ⟹ a role's `prompt_template` + `output_schema` upgrade from STATIC-PER-ROLE (swap-to-vary) → `resolve(coordinate)` (compute-to-vary) — Tim's spine sense. fork co-shapes the role-config shape against runtime/roles.py.

## §6 · DEGRADE-CLEAN + HONEST FLAGS
- While `/api/resolve` is committed-not-live: the host degrades to the live `body[data-ff]` CSS and AUTO-UPGRADES on the lead's batched bounce. No hard dependency on the route being live.
- `device.kind` derived, not authoritative (§1). `viewer.expertise` slot wired, value pending (§1). Card zone numbers pending DNA's rework (§4). None of these BLOCK the device-axis migration.
- FAIL-LOUD inherited from resolve_slot: a malformed slot / unmatched select-no-default RAISES — never a silent wrong allocation.

## §7 · LANES (co-author; same resolve(), same coordinate)
- **composition** — this contract + the CARD invariant (the card-seam mechanism) + the decision-sequence/card_kinds types.
- **projection** — the HOST consume-logic (compute coordinate `{device:{w,h,orient}}` → POST /api/resolve `{invariant, coordinate}` → apply `{resolved}` as CSS vars; degrade-clean) + the MODAL + SHELL invariants authored to §3.
- **fork** — the `resolve_slot` engine (built) + the resolved-slots role-side (§5) against roles.py; confirm the prompt-template wrapper want/skip.
- **DNA** — the card's zone VALUES feed the CARD invariant (§4); renders the resolved allocation.
