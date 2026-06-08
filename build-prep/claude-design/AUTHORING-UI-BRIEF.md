# Authoring UI — Claude-Design-Ready Brief

> **For Claude Design** (Anthropic's front-end design tool: a human clicks + describes, the tool reads/writes
> the repo and renders live). This is the brief for the Company's **cognition authoring UI** — the operator
> screen for creating/editing the *roles* and *rules* of the concurrent-cognition system.
>
> **The backend is built, tested, and live; no front-end exists yet.** This brief tells you WHAT the screen
> is, WHAT it calls, the LAWS it must obey, and the AESTHETIC — so you build the right thing on the existing
> conventions. Everything here is grounded in the real repo with `file:line` citations so it is verifiable.
>
> **No-fiction note:** every screen described here is **PROPOSED / to-be-built**. No authoring FE exists in
> the codebase today. The only *living* cognition surface is the read-only `CognitionView.tsx` (the VIEW). Do
> not treat any authoring UI as existing — you are building it.

**Primary sources (read these):**
- The contract this brief is distilled from: `build-prep/concurrent-cognition/AUTHORING-FE-HANDOFF.md` (the cognition session's FE handoff — endpoint map, data shapes, UX-to-surface map, laws).
- The endpoints: `runtime/bridge.py:487-493` (GET selects), `runtime/bridge.py:1191-1220` (POST authoring), `runtime/bridge.py:305` (`/api/cognition_info`), `runtime/bridge.py:1327` (`/api/resolve`), `runtime/bridge.py:1337` (`/api/apply`).
- The grammar floor: `runtime/rules.py:65-130` (`RULE_OPS`, `MAX_RULE_DEPTH`, `DESTINATION_KINDS`, `FORBIDDEN_DESTINATION_VERBS`).
- The look: `design/_system/tokens.json` → compiled to `design/design-system.css`.
- The living aesthetic reference (the only one that exists): `canvas/app/src/regions/CognitionView.tsx`.
- The reuse components: `canvas/app/src/components/NodeConfigForm.tsx`, `canvas/app/src/components/kit.tsx`, `canvas/app/src/regions/Inbox.tsx`, `canvas/app/src/regions/ProposeAffordance.tsx`, `canvas/app/src/api.ts`.

---

## 1 · WHAT THIS SCREEN IS (in plain terms)

The concurrent-cognition system is how the Company *thinks*: when something comes in (an utterance), a small
set of model-functions — **roles** — fire in parallel, each emitting a small structured result; **rules** then
read those results and route values (inject into the reply, trigger another role, surface to the operator, and
so on); the reply assembles in staged parts from what resolved.

Today, those roles and rules live as **files** in the repo (`roles/<id>.py` + declared rule data). Editing the
system's thinking means editing files. **The authoring UI replaces files with a screen.** On it, the operator
(Tim, or a future operator) can:

- **See every role** the cognition layer has, recognise its character by sight, and add a new one.
- **Author a role**: give it a name, a prompt, define the *fields* it outputs (its structured result), pick
  which models can run it and which modes/casts it belongs to.
- **Author a rule**: build a routing condition from a small fixed set of building blocks, point it at one of
  five destinations, and check it routes the way intended — all without writing code.
- **Test before committing**: run a single role on a sample utterance, or preview a whole staged turn, and
  watch the cognition light up — *before* anything goes live.
- **Approve into existence**: nothing the operator builds goes live on its own. Each change is *surfaced* as a
  proposal the operator reviews (with the rendered result shown) and explicitly approves; only then is it
  written and committed and appears in the live system.

The mental model the screen should make visible (`AUTHORING-FE-HANDOFF.md:23-29`):

```
  utterance ─▶ [role] ─emits structured output▶ run://<turn>/<role>
                  │                                    │
                  └─ rule reads resolved values ──▶ DESTINATION (inject·chain·address·surface·lane)
                                                       │
                            the reply assembles as staged PARTS, enriched by what resolved
```

This is the **same** registry-renderer pattern the app already uses for node-types: the backend serialises the
cognition registries through `build_cognition_info` and the FE is a generic renderer — *drop a role/rule in the
backend → it appears live, no FE code* (`AUTHORING-FE-HANDOFF.md:40-43`). Your authoring forms are the existing
**NodeConfigForm / Inspector** pattern applied to roles + rules instead of node-types.

---

## 2 · THE SURFACES (the IA — proposed)

Three authoring concerns, plus one read foundation already built. **Proposed information architecture:** one
**Authoring** region (a sibling of the existing canvas regions), with three panels and a shared test/preview
strip — co-existing beside, never replacing, the read-only `CognitionView` (the live VIEW).

### 2a · Role authoring
- **Role palette** — the list of all cognition roles (like the node palette `regions/Palette.tsx`), each
  recognisable by sight by its facet: `can_fire` / `is_jury` / which casts it's in. A **"+ new role"**
  affordance opens the role form. Reads `GET /api/cognition_info.roles`.
- **Role config form** — extends `components/NodeConfigForm.tsx` + `regions/Inspector.tsx`. Edits a role's
  `label`, `prompt_template`, `mode_scope`, `requires`. The **model picker** is populated from
  `GET /api/cognition/models_for_role?requires=…` (only models whose `provides ⊇ requires`). The
  **input-wiring** select is populated from `GET /api/cognition/inputs`. Drives `role/propose` (new) or
  `role/edit` (existing).
- **Schema editor** (net-new sub-form inside the role form) — define the role's `output_fields`: each row is
  `name` + a **type dropdown** + an optional `description`; add/remove rows. The type dropdown is populated
  from `GET /api/cognition/field_types` (the closed set: `str·int·float·bool·list[str]·list[int]`).
- **Role dry-run** — "test this role": run it (registered, or a never-saved draft field-set) on a sample
  utterance, see the validated structured output. Fully isolated — no file written, no events.
  Drives `POST /api/cognition/role/dry_run`.

### 2b · Rule authoring (the net-new centerpiece)
- **Rule-builder** — a small recursive **block/condition composer** for the rule's `when` AST. The operator
  picks ops from the **closed grammar only** (the 16 `rule_ops`) and composes leaves/booleans/comparisons —
  *never free text*. A **destination picker** offers **only the 5 `destination_kinds`**. Live, on every edit,
  it calls `POST /api/cognition/rule/validate` and shows: errors, the rendered badge text (`when_text`), the
  role-ids it reads (`references`), the depth, and whether it's still shallow enough to draw (`renderable`).
- **Rule dry-run** — a "test with sample values" panel: the operator supplies sample resolved role outputs and
  sees the routing decision (fire? destination? value? reason?). Drives `POST /api/cognition/rule/dry_run`.
- **Attach / detach** — save a built rule onto a role (or remove one). These **surface like an edit** (they
  return a `role_build` to approve). Drive `POST /api/cognition/rule/attach` / `…/detach`.

### 2c · Preview-a-turn
- **Preview panel** — "preview a turn": run a full staged turn for a draft config on a sample utterance, mode
  optional. Returns the staged `parts` + the `cognition_events`. **Render the returned events by reusing the
  live `CognitionView` rendering** — the same river/dots light up. Drives `POST /api/cognition/preview_turn`.
  Note: preview is non-mutating to chat history/thread/training-signal, but it IS a real staged turn — it emits
  `cognition.*` to the live SSE and writes to `run://<turn>/<role>` CAS, so it is observable on the live stream
  (`AUTHORING-FE-HANDOFF.md:81-90`). That is intended, not a bug — surface it honestly ("this runs a real
  turn; it won't touch your chat history").

### 2d · The approval loop (rides existing surfaces)
- Every write (`role/propose`, `role/edit`, `role/delete`, `rule/attach`, `rule/detach`) **surfaces** a
  proposal — it does not apply. The proposal carries the **rendered `.py` source** for review. The operator
  reviews it in the existing inbox/surfaced flow (`regions/Inbox.tsx`, `regions/ProposeAffordance.tsx`),
  approves via `POST /api/resolve`, and it is applied via `POST /api/apply`. See §4.

---

## 3 · THE EXACT BACKEND CONTRACT

> **Endpoint count clarification (flagged, not invented):** the originating task enumerated
> `role/{propose,apply,edit,delete,dry_run}`, implying a `role/apply` route. **There is no
> `/api/cognition/role/apply`** — verified absent in `runtime/bridge.py`. Apply rides the *existing*
> operator-only `POST /api/apply`. So the count is: **12 cognition authoring endpoints** = 9 POST (4 role POSTs
> — `propose`/`edit`/`delete`/`dry_run`, of which `dry_run` is a TEST that writes nothing — + 4 rule POSTs +
> `preview_turn`) + 3 GET selects — **plus** the 2 reads the FE wires to (`/api/cognition_info`,
> `/api/stream` SSE) **plus** the 2 existing shared operator endpoints the approve-loop rides
> (`/api/resolve`, `/api/apply`). The handoff doc's B.2 got this right; the task's brace-list was off by one.
> All response shapes below are the **verified-live curl examples** at `AUTHORING-FE-HANDOFF.md:100-140`.

### READ (already built — the FE reads these)
| Method · Path | Request | Response | What it does | Source |
|---|---|---|---|---|
| `GET /api/cognition_info` | — | the full registry projection (see §C.1 of handoff): `roles`, `rules`, `edge_kinds`, `thought_shapes`, `activation_contexts`, **`rule_ops`**, **`destination_kinds`**, `casts`, `node_states` | the single read-truth for the whole authoring surface; every dropdown derives from it | `bridge.py:305`, `api.ts:182 cognitionInfo()` |
| `GET /api/stream` (SSE) | — | the live event stream; `cognition.*` lifecycle events fire as a staged turn runs | the live fold; FE already has the `cognition.*` branch | `useAppController.ts:227 foldCognition` |

### WRITE — roles (propose-not-apply)
| Method · Path | Request body | Response | Source |
|---|---|---|---|
| `POST /api/cognition/role/propose` | `{"spec": <RoleFieldSpec>, "model"?: str}` (author a NEW role) OR a brain-draft `{"spec": {"id"?, "brief": "<NL>"}}` | `{"id":"s<N>-role_build","role_id":str,"source":"<rendered .py>"}` OR `{"needs":str,"id":"<question sid>"}`. **Surfaces — NOT applied.** | `bridge.py:1191` → `Suite.propose_role` |
| `POST /api/cognition/role/edit` | `{"role_id":str,"spec":<RoleFieldSpec>,"model"?:str}` | `{"id":str,"role_id":str,"source":str,"edit":true}` OR `{"protected":true,"needs":str,"id":str}`. **Surfaces a replacement.** | `bridge.py:1194` → `Suite.edit_role` |
| `POST /api/cognition/role/delete` | `{"role_id":str}` | `{"id":str,"role_id":str,"delete":true}` OR `{"protected":true,"needs":str,"id":str}`. **Surfaces a removal.** | `bridge.py:1198` → `Suite.delete_role` |

### TEST — role (isolated; non-mutating)
| Method · Path | Request body | Response | Source |
|---|---|---|---|
| `POST /api/cognition/role/dry_run` | `{"role_id":str}` OR `{"fields":<RoleFieldSpec>}` + `{"utterance":str,"model"?,"base_url"?}` | `{"role_id":str,"output":{<validated structured output>}}`. No file written, no events. | `bridge.py:1201` → `Suite.dry_run_role` |

### WRITE / TEST — rules
| Method · Path | Request body | Response | Source |
|---|---|---|---|
| `POST /api/cognition/rule/validate` | `{"ast":<RuleAST>,"destination"?:str}` | `{"ok":bool,"errors":[str],"references":[str],"destination":str|null,"destination_ok":bool|null,"renderable":bool,"when_text":str|null,"depth":int|null}`. **Live, on every edit.** | `bridge.py:1206` → `Suite.validate_rule` |
| `POST /api/cognition/rule/dry_run` | `{"ast":<RuleAST>,"sample_resolved":{role:{field:val}},"destination"?:str(default "inject"),"params"?:{},"on_missing"?:"raise"|"skip"}` | `{"ok":bool,"decision":{rule,fire,destination,value,params,reason},"when_text":str}` OR `{"ok":false,"error":str}` | `bridge.py:1209` → `Suite.dry_run_rule` |
| `POST /api/cognition/rule/attach` | `{"role_id":str,"rule":<RuleDecl>}` | same as `role/edit` (surfaces a `role_build` with the rule added) | `bridge.py:1214` → `Suite.attach_rule` |
| `POST /api/cognition/rule/detach` | `{"role_id":str,"rule_id":str}` | same as `role/edit` (surfaces a `role_build` with the rule removed) | `bridge.py:1217` → `Suite.detach_rule` |

### PREVIEW — full staged turn (read-only to chat state)
| Method · Path | Request body | Response | Source |
|---|---|---|---|
| `POST /api/cognition/preview_turn` | `{"utterance":str,"mode"?:str,"graph_id"?:str}` | `{"utterance":str,"mode":str,"parts":[{part,text,final,staged}],"cognition_events":[<cognition.* events>],"n_parts":int}`. Fires a REAL staged turn but does NOT append to chat history/thread/training-signal. | `bridge.py:1220` → `Suite.preview_turn` |

### SELECT — populate every dropdown from truth (never hardcode)
| Method · Path | Request | Response | Source |
|---|---|---|---|
| `GET /api/cognition/models_for_role?requires=chat,json` | query `requires` (comma-sep capability tags) | `{"requires":[str],"models":[str],"providers":{provider_id:{model,base_url,provides:[str]}}}` — only models whose `provides ⊇ requires` | `bridge.py:487` → `Suite.models_for_role` |
| `GET /api/cognition/inputs` | — | `{"utterance":"utterance","roles":[str],"role_addresses":["run://<turn>/<role>"],"context_variables":[str]}` | `bridge.py:491` → `Suite.available_inputs` |
| `GET /api/cognition/field_types` | — | `{"<type>":{"annotation":str,"gloss":str}}` for `str·int·float·bool·list[str]·list[int]` | `bridge.py:493` → `Suite.field_types` |

### APPLY — rides EXISTING operator endpoints (NOT cognition-namespaced)
| Method · Path | Request body | Response | Source |
|---|---|---|---|
| `POST /api/resolve` | `{"id":"<sid>","choice":"approve"|"reject","reason"?:str}` | `{"ok":true,"verdict":{...},"surfaced":[...]}` — the operator APPROVES the surfaced role/rule here | `bridge.py:1327`, `api.ts:46 resolve()` |
| `POST /api/apply` | `{"id":"<sid>"}` | `{"ok":bool,"path":str,"kind":"role_build"|"role_delete","error":str|null,"types":[...]}` — applies the approved change (writes file, git-commits, the role goes LIVE in `/api/cognition_info`) | `bridge.py:1337`, `api.ts:62 apply()` |

### The data shapes (full definitions in handoff §C, grammar verified in code)
- **`RoleFieldSpec`** (handoff `:171-189`): `{id, label, description, prompt_template, output_fields[{name,type,description}], input_addresses[], mode_scope[], trigger, requires[], rules[]}`. `id` REQUIRED. `prompt_template` present ⇒ the role can fire. `type` ∈ the closed field-type set.
- **`RuleAST`** (handoff `:195-211`; verified `runtime/rules.py:65-88`): a dict-tree over the closed **16-op** grammar — leaves `field`/`lit`; boolean `and`/`or`/`not`; comparison `eq`/`ne`/`lt`/`le`/`gt`/`ge`; arithmetic `add`/`sub`/`mul`; membership `in`/`contains`. **No `now`/`random`/`call`/IO op exists** (determinism is structural). Depth-capped at `MAX_RULE_DEPTH = 6` (`rules.py:93`).
- **`RuleDecl`** (handoff `:213-224`): `{id, label, when:<RuleAST>, destination:<one of 5>, params:{…}, on_missing:"raise"|"skip"}`.
- **The 5 `destination_kinds`** (verified `runtime/rules.py:114-126`): `inject` (params `value_path`), `chain` (params `chain_role`), `address`, `surface` (an `ask`, resolved=None — NOT a resolve), `lane`.

---

## 4 · THE UX FLOW (propose → approve → apply, as the operator experiences it)

The governance floor of this whole surface: **authoring never writes live state directly.** Every write SURFACES
a proposal; the operator reviews and approves; only then is it applied. Rendered for the operator:

```
  [operator builds a role/rule in the form]
        │  (the FE never writes a file — it calls the endpoint)
        ▼
  POST role/propose (or edit/delete/attach/detach)
        │  → returns { id: "s<N>-role_build", source: "<rendered .py>" }   ← a SURFACED proposal, NOT live
        ▼
  [the proposal appears in the INBOX]   (regions/Inbox.tsx + ProposeAffordance.tsx)
        │  the operator REVIEWS the rendered source (sees exactly what will be written)
        │  options, not binary: approve · reject(+reason) · steer/refine
        ▼
  POST /api/resolve  { id, choice:"approve" }    ← the operator's explicit approval
        ▼
  POST /api/apply    { id }                       ← writes the file, git-commits, role goes LIVE
        ▼
  the role/rule now appears in GET /api/cognition_info (and in casts[<mode>]) — live
```

**Proven invariant (do not break):** an `apply` WITHOUT a prior operator approve is REFUSED (HTTP 400,
`GovernanceError`) — `AUTHORING-FE-HANDOFF.md:66-68`. Before approve, the change is NOT live.

**Dry-run / preview affordances** (no approval needed — they don't write live state):
- "Test this role" (`role/dry_run`) — isolated, instant, on a draft or saved role.
- "Test this rule" (`rule/dry_run`) — sample-values-in → routing-decision-out.
- "Preview a turn" (`preview_turn`) — a full staged turn, rendered through the live CognitionView visuals.
- Live validate (`rule/validate`) fires on **every edit** of a rule — the badge text, errors, references and
  depth update as the operator composes.

**Error / fail-loud display** (law 7): a malformed role/rule returns HTTP 400 with the reason. The UI must
**surface the reason**, never silently swallow it or fabricate success. Example verified-live error
(`AUTHORING-FE-HANDOFF.md:123-126`): a forbidden destination returns
`{"ok":false,"errors":["destination 'resolve' must be one of [...] and NEVER one of (resolve,approve,dispatch)…"],"destination_ok":false}`
— show it inline at the destination picker. The `NodeConfigForm` already models the fail-loud pattern
(it surfaces a current value even when off the live option list rather than dropping it silently —
`NodeConfigForm.tsx:24-25`).

**Protected roles** (law 8): `role/edit`/`role/delete` on a runtime-imported role returns
`{protected:true, needs:…}`. Render this as **"needs Tim / can't edit from here"** — a calm boundary, not an
error.

---

## 5 · THE DESIGN BAR

**Built on the existing design system — never bespoke.** The look compiles from `design/_system/tokens.json`
→ `design/design-system.css`. Name the real tokens; do not introduce off-token hex/px.

**Aesthetic — the gold living instrument / commander's bridge** (`tokens.json:10`, `:51`, `:66`):
- **Gold is THE primary** (`--acc` = `#e6ab5c`). No green/mint/teal anywhere. The dark base is **warm
  charcoal** (`--bg #0c0a08`, surface tiers `--s0..--s3`), text a soft warm cream (`--tx #f3ece1`).
- **Status by colour** (preserved as a two-vivid + one-muted split): `--acc` gold = alive/done/signal;
  `--await` orange-amber = in-flight; `--fail` coral = failed; `--cache` taupe-grey = idle/calm. Use these for
  the role-status dots and the live test/preview lighting — exactly as `CognitionView.tsx:34-45 statusToken`
  maps lifecycle states to tokens.
- **Typography** (`tokens.json:51-62`): `--font-display` = **Fraunces** serif (panel headings, titles, role
  output — the calm-authority signature); `--font-mono` = **IBM Plex Mono** (every control, label, value,
  address — the instrument body; the app's base font IS mono). Type scale is the named ladder
  `--fs-micro/-tag/-meta/-body/-lg/-title/-display`.
- **Shape** (`tokens.json:80-91`): the base-4 space ramp `--sp-1..--sp-6`; radii `--r-sm/-r/-r-lg/-r-pill`;
  elevations `--elev-1` (rail/panel), `--elev-2` (floating card/sheet); `--shadow`. The living-instrument
  glow: `--acc-glow`, `--acc-flow` (the gold gradient), `--orb-hi`.

**Components to reuse (compose, don't reinvent):**
- The `kit.tsx` vocabulary: `Surface` (the card — `kit.tsx:60`), `Badge` (toned chip — `:52`),
  `SectionHead` (`:23`), `LaneHead` (collapsible lane — `:38`), `EmptyState` (`:69`). The tone vocabulary
  (`sig`/`dim`/etc.) is how status reads by sight.
- `NodeConfigForm.tsx` — the schema-driven form pattern (fields from a schema, enum→`<select>` from the live
  registry, everything else→`<input>`). The role config form IS this pattern over a role's fields.
- `CognitionView.tsx` — reuse its river/pulse/node-card rendering for the **preview** result; reuse its
  `statusToken`→`node_states` by-sight mapping for role status everywhere.
- `Inbox.tsx` + `ProposeAffordance.tsx` — the surfaced-proposal review + approve/steer/reject UX.

**Recognition-by-sight** (Tim navigates by shape, not by reading text — `CLAUDE.md` render-for-cognition):
- A role's *facet* (`can_fire` / `is_jury` / which casts) must read **by shape/colour**, not by parsing a
  label. (CognitionView already does this — fired vs latent vs failed are different stroke widths/colours, not
  words.)
- A rule must render as its **`when_text` edge-badge** — a short, legible glyph-string — never a code wall.
  If `renderable:false` (too deep to draw), surface *that* as a recognisable "too deep — decompose into a
  role" state, not a silent truncation.
- Side-by-side comparison where the operator weighs options (the `ProposeAffordance.tsx:16-37` pattern:
  alternatives sit side-by-side, selection is visual-only, an explicit second gesture approves).

**Responsive — desktop + mobile** (the corpus standard): forms reflow; comparison cards STACK to a column on
phone rather than crushing a row (as `ProposeAffordance` does); the rule-builder's block tree must remain
operable on touch.

> **No visual precedent exists.** There are **no cognition mockups** in `design/mockups/` (verified — the
> closest siblings are `A3-inspector-desktop.html`, `B4-presence-dial`, the canvas screens). `CognitionView.tsx`
> is the **only living aesthetic reference** for the cognition surface. Build from it + the tokens; this is a
> place where Tim's recognition is the real input (render, let him judge by sight).

---

## 6 · THE LAWS (hard constraints — Claude Design MUST NOT violate)

These are the governance floor of the cognition system. They are not style preferences; they are enforced in
the backend and must be honoured in the UI (`AUTHORING-FE-HANDOFF.md:287-309`, verified in code).

1. **REFLECTS-NEVER-OWNS.** The surface drives via `run://` addresses + the endpoints + the SSE stream; the
   **backend** writes the role/rule files. The FE **never** writes a role file directly — it calls
   `role/propose` etc. (`AGENTS.md` rule 3, one source.) The live VIEW issues no writes
   (`CognitionView.tsx:6-7`); the authoring forms write only through the propose endpoints.

2. **PROPOSE-NOT-APPLY.** Every authoring write SURFACES for operator approval (returns a surfaced `id` + the
   rendered `source`). Nothing is live until the operator approves (`/api/resolve`) and it is applied
   (`/api/apply`). The UI must show the surfaced item + its rendered source for review and route approve→apply.
   **It must NEVER auto-apply** — i.e. never apply *without an operator approval*. (Bridge comment
   `bridge.py:1187-1190`; an apply without a prior approve is refused with HTTP 400 `GovernanceError` —
   proven by use, `AUTHORING-FE-HANDOFF.md:66-68`.)

3. **The rule grammar is CLOSED + RENDERABLE + REGISTRY-DRIVEN.** Offer ONLY the ops in
   `cognition_info.rule_ops` (the 16) and the destinations in `cognition_info.destination_kinds` (the 5).
   **Populate both lists FROM `/api/cognition_info` at runtime — do NOT hardcode them in the FE** (this is the
   teeth of law 6). Never a free-text expression; never a 6th destination. Respect the depth cap
   (`renderable:false` ⇒ surface "too deep to draw", don't render a text-wall). (`rules.py:65-93,114-126`.)

4. **The claude-p / dispatch floor is LEAD-ONLY.** A rule's destination is **NEVER**
   `resolve`/`approve`/`dispatch` (`FORBIDDEN_DESTINATION_VERBS`, `rules.py:130`). The rule-builder must not
   offer them; `validate_rule` refuses them (`destination_ok:false`). A role/rule/authoring path can never emit
   resolve/approve/dispatch. Authoring **surfaces**; the operator approves.
   - **Keep distinct:** the `surface` *destination kind* (`rules.py:120-121`) emits an `ask` event with
     `resolved=None` — it is an escalation to the inbox, explicitly **NOT** a resolve. Do not conflate the
     `surface` destination with the propose-surfaces-for-approval flow (§4). The floor holds by construction:
     only the operator-only `resolve_surfaced` ever emits a `resolve`.

5. **`run://` ADDRESSING.** A rule reads role outputs at `run://<turn>/<role>` (the `inputs` / `role_addresses`
   from `GET /api/cognition/inputs`). Never invent another scheme.

6. **AUTHOR FROM THE REGISTRY, NEVER INVENT** (`AGENTS.md` rule 8). Every dropdown — field types, models,
   inputs, modes, destinations, ops — comes from an endpoint, never a hardcoded FE list. A NEW
   model/role/field-type/op added to the backend appears in the dropdown automatically, with zero FE change.

7. **FAIL LOUD.** A malformed role/rule fails loud at validate/propose (HTTP 400 with the reason). Surface the
   error inline; never silently swallow it or fabricate a success.

8. **PROTECTED ROLES.** `role/edit`/`role/delete` on a runtime-imported role returns `{protected:true,
   needs:…}`. Show as "needs Tim / can't edit from here", not an error.

9. **OPERATOR-ONLY, OFF THE MCP FACE.** These authoring endpoints are the **operator** face — served by the
   bridge beside `/api/resolve` / `/api/act`, explicitly **NOT** the MCP/agent face. Evidence: the bridge
   comment "OPERATOR face only (beside /api/resolve, NOT the MCP/agent face)" at `bridge.py:1227` (and the
   `/api/act` comment "NOT the MCP/agent face"). The authoring UI is for a human operator; do not expose it as
   an agent-callable surface.

---

## 7 · OPEN QUESTIONS (for Tim's eye)

Framed as options, not yes/no — pick a direction or say "none of these":

**A · Approve-then-apply: one gesture or two?**
The loop is two backend calls (`/api/resolve` approve, then `/api/apply`). The law "never auto-applies" means
*never without an operator approval* — it does not, on its own, dictate whether the UI fires `apply`
automatically on a successful approve, or makes `apply` a *second explicit click*. This is genuinely
unspecified in the handoff.
- *Option A1:* approve = one gesture, apply fires automatically on success (fewer clicks; still law-clean).
- *Option A2:* approve and apply are two explicit gestures (a deliberate "now make it live" beat).
- *Recommendation:* lean A1 for authoring (the rendered source review IS the deliberation), but this is Tim's
  call on how heavy the "make it live" moment should feel.

**B · One Authoring region, or split?**
This brief proposes one **Authoring** region with role / rule / preview panels (§2). Alternatives: fold
authoring INTO the existing read-only `CognitionView` (one cognition surface, view+author together), or keep a
dedicated authoring screen separate from the live view. The handoff maps affordances onto existing surfaces but
does not fix the top-level IA.

**C · The `lane` destination is under-specified in the backend.**
`rules.py:122-125` flags the typed-lane destination as a "minimal seam — R2-FOLD H6 flagged typed-lane
under-specified." It works (writes a `cognition.lane` event), but its UX (naming a lane, viewing a lane) has no
defined surface yet. Offer it as a destination, but its richer surface may be a later pass.

**D · Directory-scan source node (C7.5) is downstream / unbuilt.**
The handoff (`:268`) notes the "scan directories → live structured output" pairing depends on a directory-scan
*source* node that is a downstream pairing, flagged for a later build. The structured-output authoring half
(`output_fields` → `role/propose`) and the live-stream rendering it depends on ARE done; the scan source is
not. Scope decision: include a placeholder for it, or leave it out of this UI entirely for now.

**E · Persona theming: Vi-gold only, or switchable?**
`tokens.json:66` defines Atlas (apricot) and Nova (rose-gold) personas as **defined-not-live** — the app
currently runs Vi-gold as the default (no `data-persona` is set in markup). Build the authoring UI in the live
Vi-gold, or wire the persona switch here too?

---

### Next-step options for Tim
1. **Depth** — walk one surface (e.g. the rule-builder) in finer detail before Claude Design touches it:
   trace `validate_rule`/`dry_run_rule` in `runtime/suite.py` to pin the exact decision-record fields and the
   block-composer's interaction model.
2. **Dealer's choice** — produce a quick proposed-IA sketch (a wireframe-level layout of the one Authoring
   region + its three panels) so the screen's *shape* is on the table before pixels.
3. **Tentative artifact** — hand this brief to Claude Design as-is and let it render a first pass of the role
   palette + role config form (the most-grounded, lowest-ambiguity surfaces), then judge by sight and correct.
   *Recommended* — the role-authoring surfaces reuse existing patterns almost entirely, so a first render is
   cheap and gives Tim something to react to; the rule-builder (the net-new, higher-ambiguity piece) can
   follow once the open questions above are steered.
