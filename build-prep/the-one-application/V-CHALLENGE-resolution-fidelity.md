All three checks confirm the thesis cleanly. Critically: the **NODE_STATES registry** (right after ModeSpec) already carries a `render: {token, icon, shape}` block on each state row — colour-as-a-field-on-the-row is **already the demonstrated pattern in this very file**. This makes the mode-colour smuggle (a separate `STATE_MAP` in `palette.js`) an indefensible inconsistency: the codebase already proves how to do it right two screens away from where mode is hardcoded.

I have everything. Writing the audit now as quote→correction pairs, leading with the inversion. This is my durable deliverable, returned directly as my final message.

---

# RESOLUTION-FIRST FIDELITY AUDIT — THE V-SURFACE MAP

**Verdict:** The map's resolution-first SPINE (§1 recipe, the single resolver, schema-additive law) is sound and matches the codebase. But the map **crowns the wrong exemplar** and **endorses three inline-enumeration smuggles as DONE/BUILT** that violate its own recipe. The smuggle signature, swept across the whole map, is one thing: **a closed `Literal[...]` / tuple-of-strings / inline-dict that enumerates INSTANCES in Python, where the resolution-first form is a file-discovered registry row.** I hold every correction to a standard the codebase *already meets six times over* — the `_CORPUS_REGISTRIES` table (`runtime/suite.py:360`) discovers `mark_type · generation_policy · relation_type · ai_tic · projection · mind` from `<kind>/<id>.py` dirs, and `RoleRegistry().discover([roles_dir])` (`suite.py:371`) does the same for roles. That is the repo's own demonstrated standard. I am not importing an ideal.

(Footnote, stated once: the map's file citations are missing the `runtime/` prefix — it writes `suite.py:2138`, the file is `runtime/suite.py`. The composition runtime it cites — `factory-mount.js`, `connection-mount.js`, `component.schema.json` — is **not in this repo**, matching the map's own honest caveat; all §4/§A critiques below are against the map's *proposed design*, not verifiable code.)

---

## THE HEADLINE INVERSION: mode is the ANTI-exemplar, not the exemplar

**The map says (§1 table, mode row):**
> **mode** | `MODE_REGISTRY` (one dict, 8 entries, all axes) | … | **BUILT — the most complete type-with-schema in the system; the exemplar**

**This is exactly backwards on the resolution-first axis.** Verified in code:
- `MODE_REGISTRY` is an **inline Python dict literal** at `runtime/suite.py:2138` (`MODE_REGISTRY = { "listening": {...}, ... }`).
- There is **no `modes/` directory** (`ls modes/` → does not exist).
- `mode` is **absent from `_CORPUS_REGISTRIES`** (`suite.py:360` — the table has exactly 6 kinds; mode is not one).
- Therefore **editing a mode = editing Python**. It cannot be authored by `_write_registry_file`, has no first-row file, is not discovered.

By the map's OWN §1 recipe ("registry row → `_CORPUS_REGISTRIES` → first row file `<kind>/<id>.py` → discovered"), `MODE_REGISTRY` is the *least* resolution-first of the core types — a hand-maintained code table. The map crowns the one type that most violates its thesis.

**Correction — rewrite the mode row Status:**
> ~~BUILT — the most complete type-with-schema in the system; the exemplar~~
> **BUILT AS INLINE CODE — the ANTI-exemplar. `MODE_REGISTRY` (`runtime/suite.py:2138`) is a hand-maintained Python dict, not a discovered registry: no `modes/` dir, absent from `_CORPUS_REGISTRIES`. Resolution-first form = file-discovered `modes/<id>.py` rows, exactly as `RoleRegistry().discover([roles_dir])` (`suite.py:371`) already does for roles. REQUIRED, not optional: the map's own MAKE keystone (B1) says "Tim ADDS A MODE by speaking to the RHM … one MODE_REGISTRY row via `_write_registry_file`, zero screen-code" — but `_write_registry_file` only works on kinds in `_CORPUS_REGISTRIES`, and mode is not one. The keystone the map promises is impossible against the code as it stands.**

**Crown the real exemplar instead — `window` / mark_type:** the map's own §1 window row is genuinely resolution-first and should be named the spine's model: the live/empty states are **file-discovered mark_type rows** (`mark_type` IS in `_CORPUS_REGISTRIES`; states live as data with a `render:{token,icon,shape}` block — `NODE_STATES`, `suite.py:~227`), and only the `window://` *scheme label* is net-new (a legitimate one-line resolver addition per the recipe). Honest finding: window needs no complaint. It is what mode pretends to be.

**Pre-empting the obvious rebuttal** ("mode carries `frozenset({...})` in its `resolution` block — `_write_registry_file` *fails loud on callables*, so mode CAN'T be a row"): this conflates two authoring tiers. (a) **File-discovery** (`roles/<id>.py`, the 6 corpus dirs) imports Python literal files — `frozenset` is a literal, perfectly fine. (b) **MCP-JSON authoring** (`_write_registry_file`) renders a spec to a Python literal and chokes on callables. Mode belongs in tier (a) — a discovered `modes/<id>.py` dir, precedent `roles/` — even if it is never reachable from tier (b). The frozensets are not an obstacle to file-discovery; they are only an obstacle to *JSON-over-MCP* authoring. The map never makes this distinction and so leaves mode stranded as code.

---

## THE FOUR TASK-NAMED ITEMS — the specific smuggle in each

### 1. mode-colour → smuggle: `STATE_MAP` is a SECOND enumeration of modes, hardcoded in `palette.js`

**The map says (§3):**
> **Palette registry (type + resolver — built):** `palette.js` — … `STATE_MAP` `:46-53` (idle→slate-blue, tool-use→classic-gold, …); `resolveStateColor(state)` `:62-66` (**the mode→colour resolver**)

The map presents `STATE_MAP` as the resolver. It is the **smuggle**: a frozen state→colour dict, a *parallel enumeration* living in a different file from `MODE_REGISTRY`. The mode→colour binding belongs as **a field on the mode row**, not a second table that must be kept in sync by hand.

**The irony the map walks straight past:** `ModeSpec`'s own docstring (`suite.py:155`) *brags* that it killed precisely this class of drift —
> "Replaces the two parallel literals `MODES` (the tuple) and `MODE_DIRECTIVES` (the prose map), which could drift: both are now DERIVED from `MODE_SPECS`."

The map then reintroduces the exact drift ModeSpec eliminated — a third parallel literal (`STATE_MAP`) carrying a mode axis (colour) in a separate file. **And the codebase already shows the fix two screens away:** `NODE_STATES` (`suite.py:~227`) carries `render: {token, icon, shape}` *on each state row*, with a comment stating the surface "paints the status vocabulary FROM the registry (one-source, rule 3) instead of the FE hardcoding a state→token switch (the thing F3 must avoid)." Colour-as-a-field-on-the-row is the demonstrated, in-file standard.

**Correction:** the colour token is a `render`/`primary` field on the mode (or processing-state) registry row, resolved like `NODE_STATES.render.token` — NOT a `STATE_MAP` dict in `palette.js`. (Note the axis split your §3 already half-sees: AI *processing-state* and operator *presence-mode* are two different registries; the colour field lands on whichever row is the active source — but it is a row field either way, never a parallel JS map.) The map's step 1 ("Name `--vi-mode-primary`") is correct and resolution-first; its step 2 ("use `paletteCssVars()` as the preloaded registry") is correct; its mistake is leaving the **mode→colour mapping** as `STATE_MAP` code instead of a resolved row field. The map's BEYOND item "make mode-colour a 5th NAMED grammar dial" is therefore **REQUIRED, not BEYOND** — it is the only form that isn't a smuggle.

### 2. expansion-setting → smuggle: `'resting'|'radial'|'window'|'sub-surface'` Literal union + frozen `EXPANSION_HANDLERS` key set

**The map says (§4):**
> `socket.connection.expansion: 'resting' | 'radial' | 'window' | 'sub-surface'` … dispatched in `mountConnection` … to a handler registry keyed by the tag: `const handler = EXPANSION_HANDLERS[binding.expansion || …]`

This is the smuggle in its purest form: a **closed string-union enumerating the instances** plus a **frozen handler dict keyed by those literals**. Adding a 5th expansion mode = editing the union AND the handler object AND the CSS class set (`vi-conn-window`, `vi-conn-sub-surface`, `vi-conn-resting` — also enumerated as code in §A's BUILD list). Three hand-edited enumerations for one instance set.

**Correction:** expansion is an `expansion_mode_registry` — discovered rows `expansion_modes/<id>.py`, each `{id, choreography(addressable), expansionParams_schema, css_token}`. The dispatch reads the row, not a frozen key set. **The map already concedes this in §4 BEYOND** ("expansion as a separately-addressable registry type (`expansion_mode_registry`)"). Under the task's standard that concession is **REQUIRED, not BEYOND** — the Literal union is the smuggle; the registry is the only resolution-first form. (Weaker, separately-labelled note: even the per-kind `expansionParams` sub-schemas the map lists — `radial:{arc_start,...}`, `window:{size,...}` — should be a `params_schema` field on the row, not a code branch per kind.)

### 3. window → already data; honest finding, NO complaint

The map is right here and I will not manufacture a grievance. The two states are file-discovered `mark_type` rows (`suite.py:257-264`), `mark_type` is in `_CORPUS_REGISTRIES`, resolution runs through the one `resolve_address`. Only the `window://` scheme label is net-new — a legitimate one-line additive resolver branch, which the recipe explicitly blesses. **This is the replacement exemplar.** Keep it as written.

### 4. sub-surface → smuggle: `ADDRESS_KINDS` frozen tuple in `ui_info.py`

**The map says (§1 sub-surface row):**
> `ADDRESS_KINDS=("chrome","field","canvas","panel","ext")` `ui_info.py:163` … **BUILT (addressing)**

Verified: `ADDRESS_KINDS = ("chrome", "field", "canvas", "panel", "ext")` (`contracts/ui_info.py:163`), and it is the **live dispatch gate** — `parse_ui_address` raises if `rec.kind not in ADDRESS_KINDS` (`ui_info.py:389`). So adding a new sub-surface KIND = editing a frozen tuple in code. The map labels this "BUILT" without flagging that the kind vocabulary is hardcoded.

**Correction:** the address-kind vocabulary is a discovered registry (`address_kinds/<id>.py` rows, or — minimally — a kind-registry the validator reads), exactly as `NODE_STATES` made node-state "a REGISTERED, single-source set, NOT a hardcoded enum" (`suite.py:~205`). The map's own §1 BEYOND ("formal sub-surface-as-typed-registry-row `UiPanelSlot`") points the right way but understates it: the *kinds themselves* are the smuggle, not just the panel slots. **REQUIRED, not net-new-someday.**

---

## SECONDARY SMUGGLES (swept by the same signature)

| Map location | The smuggle (verified) | Resolution-first correction |
|---|---|---|
| §1 expansion-setting row | `RenderMode = Literal["collapsed","expanded","full","workshop"]` (`contracts/node_type.py:10`) — map calls it **BUILT as Literal; promotion is "an upgrade, not a ground-up build"** | A closed instance Literal. Resolution-first = `render_modes/<id>.py` discovered rows (precedent: the 6 corpus dirs). The map's "upgrade path" parenthetical is **REQUIRED** under the task's standard, not an optional polish. Same file also smuggles `Kind = Literal["process","content","presentation"]` (`node_type.py:11`) — the node-kind vocabulary is itself a frozen enum. |
| §1 / §5 resolution-spine | `SCHEMES = ("run","cas",…,"vi-vision")` — a tuple (`contracts/address.py:129`) | **Defensible as-is, with a caveat.** Each scheme legitimately needs a resolver *branch* (code) — the recipe says so. But the tuple membership gate is still a hand-edited enumeration. Acceptable because scheme = code-coupled; flag only that "additive to SCHEMES" still means a code edit, so `decision://`/`window://`/`archetype://` are **code work, not row work**, contra the map's "grows by adding rows" framing for these. |
| §A / §4 | CSS class names `vi-conn-window`, `vi-conn-sub-surface`, `vi-conn-resting` enumerated in the BUILD list | These mirror the expansion instance set in a 3rd place. Fold into the `expansion_mode_registry` row as a `css_token` field; do not hand-author per-class. |
| §C BUILD | "**6 null organism generators**" + "the generic archetype compositor" | **Correctly code, not a smuggle.** Generators and the compositor are genuine logic — the resolver-branch-per-thing the recipe allows. Do NOT over-reach into calling these smuggles; the thesis is *instance sets frozen as Literals*, not "all code is bad." Keep as written. |

---

## RECLASSIFICATION — where the map's own hedges become REQUIREMENTS

The map repeatedly parks the resolution-first form in BEYOND or as an "upgrade path." Under the task's standard, every one of these is the *only* non-smuggling form, so it is REQUIRED:

1. **mode → discovered `modes/<id>.py`** (currently inline dict). The map says BUILT; it is the anti-exemplar. *Active misclassification — sharpest fire.*
2. **mode-colour as a row field / grammar dial** (currently `STATE_MAP` JS dict). Map: BEYOND → **REQUIRED.**
3. **expansion as `expansion_mode_registry`** (currently proposed Literal union). Map: BEYOND → **REQUIRED.**
4. **`ADDRESS_KINDS` as a discovered kind-registry** (currently frozen tuple). Map: implied net-new → **REQUIRED.**
5. **`RenderMode` / `Kind` as `render_modes/`, `node_kinds/` rows** (currently Literals). Map: "upgrade, not ground-up" → **REQUIRED.**

**Ranking note:** items 2–5 are *deferred* resolution (the map knows and hedges). Item 1 is *asserted-done* misclassification (the map crowns the smuggle as exemplar) — that is the highest-priority correction, because a reader trusts "BUILT — the exemplar" and copies it as the pattern, propagating inline-dict types across the whole surface the map promises to grow "by adding rows."

---

## THE ONE-LINE THESIS, CORRECTED

The map's circuit ends: *"every node is a type that resolves; the surface grows by adding rows."* That is true for `window`/mark_type, the 6 corpus kinds, and roles. It is **false today** for `mode` (inline dict), `mode-colour` (`STATE_MAP` JS), `expansion` (proposed Literal union), `sub-surface kind` (`ADDRESS_KINDS` tuple), and `RenderMode`/`Kind` (Literals). For those, the surface grows by **editing Python**, not adding rows. The fix is uniform and already demonstrated in the same repo: **move each frozen instance-enumeration into a file-discovered `<kind>/<id>.py` registry, carrying its colour/render/params as row FIELDS** — `NODE_STATES.render` and `RoleRegistry().discover()` are the patterns to copy, and `mode` — not anywhere it sits today — must be the first thing fixed and the new exemplar named.

**Grounded files for follow-up:** `/home/tim/company/runtime/suite.py:2138` (MODE_REGISTRY inline dict — the anti-exemplar), `:360` (`_CORPUS_REGISTRIES` — the 6-kind standard), `:371` (`RoleRegistry().discover` — the file-discovery precedent for `modes/`), `:~205-264` (`NODE_STATES` with `render:{token,icon,shape}` — the colour-as-row-field precedent); `/home/tim/company/contracts/node_type.py:10-11` (`RenderMode`/`Kind` Literals); `/home/tim/company/contracts/ui_info.py:163,389` (`ADDRESS_KINDS` frozen tuple + its dispatch gate); `/home/tim/company/contracts/address.py:129` (`SCHEMES` tuple — defensible-with-caveat). `palette.js`/`STATE_MAP` and the composition runtime are NOT in this repo — those corrections are against the map's proposed design, unverifiable here.