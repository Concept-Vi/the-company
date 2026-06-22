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

## §4 · THE CARD INVARIANT (one mechanism, host + card) — co-authored with DNA's verified two-panel
The decision-card's layout is an allocation-invariant resolved on the SAME coordinate via the SAME `resolve()`
(exactly like §3's host invariants). CO-VISIBLE-vs-STEPPED is a RESOLVED slot, never a stored variant. Concrete
shape — composition owns `card_layout` + the kind↔panel binding; DNA owns the panel GEOMETRY (its VERIFIED
two-panel zones); co-author, like §3 is projection's:
- `card_layout` — the rendering the resolver picks: `'co-visible'` (the VERIFIED two-panel structure) vs
  `'stepped'` (a future tight coordinate / complex decision). For the decision-card now:
  `{select:<fit-coordinate>, cases:{…}, default:'co-visible'}` — resolves co-visible at the verified coordinates;
  stepped reserved. ★ merge-sa KEYSTONE GATE = the 390-coordinate resolves `card_layout → co-visible` (a
  resolver assertion, not a hand-case).
- `kind_panel` — the card_kinds↔PANEL binding (COMPOSITION): which panel each kind renders into in the verified
  two-panel co-visible structure — e.g. `{present→A, explain→B, choose→B}` (exact mapping = DNA's verified
  two-panel; confirm). present = question(hero)+shape · explain = the slide · choose = options+take.
- PANEL ALLOCATIONS (DNA's lane, like §3's host slots): each panel's w/h as resolved slots on the coordinate
  (continuous derivations + the orient select). ★ SOURCED — DNA grammar #1 (87fa59e): the constants are
  dna/tokens.json LAYOUT-TOKENS (panel ratios · zone splits · outer-margin clamp ~4.8vw · padding≈gutter ·
  density modes · artefact-complexity-by-area), referenced by TOKEN-NAME (stable across DNA's tuning), NOT
  hardcoded numbers. DNA flagged these "ready to move into the device-axis resolver" → when she does, the §3
  host + §4 card slots reference these tokens (co-scope the token-name→slot mapping). The STRUCTURE is authored
  NOW; the token VALUES ride DNA's grammar→resolver move + the merge-sa lock — no reshape (token-refs, not raw numbers).
- SUBORDINATE TO LEGIBILITY + the gate: the resolved `card_layout` MUST keep decision+options co-visible at the
  gate coordinate (390); a `stepped` resolution only where co-visible genuinely can't fit. (decision-card.schema
  `card_kinds` is the grouping; THIS is its resolution.)

## §5 · PROMPT + SCHEMA AS RESOLVED VARIABLES (fork's resolved-slots — the gate)
Resolved at RUN/READ time (NOT baked). ★ Co-shaped with fork against roles.py: a role today = `prompt_template:str|None` + `output_schema:type[BaseModel]|None` (a Pydantic CLASS — used for client-validate AND the json_schema guided-decode), static in the decl. The upgrade lets both BE resolve_slot values, resolved against the turn coordinate:
- PROMPT-slot: `prompt_template` → literal | `{select:<axis>, cases:{…}}` (pick by grain/viewer/mode/subtype — discrete). The TEMPLATE form (`{{name}}` placeholders = resolved sub-slots, §2) = ★ FLAGGED-FOLLOW: `select` covers the real discrete axes in v1; build the template wrapper only when CONTINUOUS prompt-composition is genuinely needed. Reuse resolve_slot; no new mechanism on the select path.
- SCHEMA-slot — ★ THE WRINKLE (fork, correct): `output_schema` is a CLASS, not a field-list, so grain is NOT a field-list select AT output_schema (that would break extract-once). Reconciliation (= extract-once / determine-many, exactly): `output_schema` resolves to (a) LITERAL — the rich SUPERSET class (the common case; extract-once), or (b) `select` between PRE-DECLARED Pydantic classes for a genuinely-different schema per coordinate (discrete), or (c) dynamic-build-from-field-set (heavier, later, only if needed). ★ THE GRAIN field-set projection is READ-SIDE — the determine/recall path projects fields FROM the validated superset RESULT (recollection's lane), NOT at output_schema. So: extract with the superset class ONCE; project the grain on the RESULT. extract-once stays intact.
- ⟹ a role's `prompt_template` + `output_schema` upgrade STATIC-PER-ROLE → `resolve(coordinate)` (axes = grain·viewer·mode·subtype·register, axes-are-registries); READ-SIDE / post-bake. fork wires run_role to resolve them through resolve_slot once this is locked.

## §6 · DEGRADE-CLEAN + HONEST FLAGS
- While `/api/resolve` is committed-not-live: the host degrades to the live `body[data-ff]` CSS and AUTO-UPGRADES on the lead's batched bounce. No hard dependency on the route being live.
- `device.kind` derived, not authoritative (§1). `viewer.expertise` slot wired, value pending (§1). Card zone numbers pending DNA's rework (§4). None of these BLOCK the device-axis migration.
- FAIL-LOUD inherited from resolve_slot: a malformed slot / unmatched select-no-default RAISES — never a silent wrong allocation.

## §7 · LANES (co-author; same resolve(), same coordinate)
- **composition** — this contract + the CARD invariant (the card-seam mechanism) + the decision-sequence/card_kinds types.
- **projection** — the HOST consume-logic (compute coordinate `{device:{w,h,orient}}` → POST /api/resolve `{invariant, coordinate}` → apply `{resolved}` as CSS vars; degrade-clean) + the MODAL + SHELL invariants authored to §3.
- **fork** — the `resolve_slot` engine (built) + the resolved-slots role-side (§5) against roles.py; confirm the prompt-template wrapper want/skip.
- **DNA** — the card's zone VALUES feed the CARD invariant (§4); renders the resolved allocation.

## §8 · THE EXTRACTION RESOLVER-VARIABLE (recollection's dragnet — the lock, 2026-06-22)

**Q (lead): can a prompt/schema be a resolvable variable? → YES.** Not a new schema-TYPE — a prompt/schema is a
resolver variable via `resolve_slot` (§5): a role's `prompt_template` + `output_schema` upgrade static-per-role →
`resolve(coordinate)`. §5 + `axes/resolution.py` already contract it; this §8 LOCKS it for recollection's
extraction/dragnet.

**THE SPINE (one-invariant-never-variants):** the invariant is the EXTRACTION SUPERSET — recollection's canonical
schema (4207e75) owns the field-structure: coarse `{about, kind, touches}` ⊂ fine `+{summary, entities, claims,
relations, open_questions}` (composition references; recollection owns the fields). The grain is an ORDINAL-DEPTH
axis (`axes/resolution.py`: `resolution.grain`) whose field-sets **NEST** — so the resolve **projects the
field-set at the grain**, a depth over the ONE superset, NOT N hardcoded coarse/fine schemas
(relationships-not-cases). The nesting IS the relationship; the grain is where the superset's depth is read.

**★ RESOLVED — Tim decided it** (COMMISSION §EXPANSION L99: *"coarse to fine, multi-layered, STEPPED BASED ON
EACH OUTPUT"*): the **ADAPTIVE STEPPED cascade**. Coarse on ALL → step deeper WITHIN THE SAME PASS per chunk by
its OWN coarse output (`kind ∈ {decision,spec,discussion}` → fine; `log` → stop at coarse). Depth decided at
EXTRACTION-TIME, **FORWARD-ONLY** — never re-extract, no up-projection. So it is extraction-side (the depth is
decided during extraction) AND never-re-extract (depth steps forward IN-pass, NOT a separate fine pass). This is
the single adaptive forward-pass — NOT coarse-broad-then-a-separate-fine-pass. recollection's schema (4207e75)
already implements it.
- **Self-stepping resolve:** the grain-coordinate is DERIVED from the coarse output's KIND — `resolve(superset,
  grain)` where `grain = f(coarse.kind)`. A coordinate that resolves FROM the data, then the deeper extraction
  resolves against it (the resolver reading its own first output).
- **ONE axis, both facets** (recollection's insight — right): the `resolution` axis serves (a) extraction-time
  forward-stepping (depth-by-kind) AND (b) read-time multi-scale ROLLUP (projecting the stepped result) — the
  SAME grain-axis, not two. never-re-extract holds throughout (extraction steps forward; read rolls up the result).

**THE SCHEMA-SLOT (fork, §5's wrinkle):** `output_schema` is a Pydantic CLASS — grain is NOT a field-list select
AT `output_schema`. Read-side → `output_schema` = the superset literal (extract-once) + project on the result.
Extraction-side → `output_schema` = a `select` between PRE-DECLARED grain-classes (coarse `{about}`-class · fine
superset-class), discrete. fork wires `run_role` to resolve `prompt_template` + `output_schema` through
`resolve_slot` once recollection picks.

**LANES (this contract):** composition — §8 + the superset-invariant shape + the grain-axis. recollection — picks
read-side vs extraction-side (corpus-cost) + owns the determine/projection. fork — wires `resolve_slot` on the
role's prompt+schema once locked.
