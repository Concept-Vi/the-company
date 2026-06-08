# Surface Design-Intent Layer — the per-surface skeletons + intent (the §3E pack at full scope)

> **What this is.** The SURFACE DESIGN-INTENT layer of the application-structure pack: the per-surface
> skeletons + their designed intent, assembled from the vault build-prep design narrative. **Depth-first on
> the Interactive Addressed Surface** (the studio's end-state spec), then an architecture-level survey of the
> other two surface triads + the cross-cutting primitives, then the surface relationship map (the IA as the
> parent that places the others).
>
> **Honesty contract (carried from `claude-design/findings/intent-studio.md`).** Every claim is tagged:
> - **DESIGNED** — intent, from chat or vault. Was meant to be; not proof it exists.
> - **BUILT** — confirmed in code on `main` (`~/company`), with the `suite.py`/`bridge.py` path the
>   intent-studio §5 read in the function body. Present-tense claims only here.
> - **DESIGNED-☐** — named in a Completion Criteria with a test, marked ☐ there, and **not yet built on main**
>   (verified against intent-studio §5, NOT inherited from the ☐ marker).
> - **INFERRED** — my synthesis across sources. Reasoned, not directly observed.
>
> **Critical methodology note (per the advisor + Tim's verify-before-claiming law).** The Interactive
> Addressed Surface — Completion Criteria marks **every** line ☐. That is the *worktree-build-loop's*
> "not-built-in-this-loop" view — it is **NOT main's reality.** intent-studio §5 read the actual `suite.py`
> function bodies on `main` and proved a substantial chunk of the I/R/L group is already BUILT. This report
> maps each criterion against **§5 (code-truth)**, not against the ☐. The `CONNECTION-CONTRACT.md` IS/SHOULD-BE
> tags are **stale** (§5.4) and are not quoted as truth.
>
> **Sources backing each section are named per-section.** Primary depth source: the Interactive Addressed
> Surface triad (`Completion Criteria` + `Research Synthesis`, both read; `Implementation Guide` consulted by
> ID, not read linearly — it is build-how, out of scope). Cross-ref: `claude-design/findings/intent-studio.md`
> §5. Survey sources: `Operable Composition Surface — Completion Criteria`, `Operable Interface — Completion
> Criteria`, `Collective Cognition — the context-resolution spine`, `RHM Walkthrough Organ — Sequenced Systems`.
> IA source: `design/mockups/IA-desktop.html` (read structurally).

---

# PART 1 ★ THE INTERACTIVE ADDRESSED SURFACE — the studio's end-state spec (depth)

> Source: `build-prep/Interactive Addressed Surface — Completion Criteria.md` (full read) +
> `Interactive Addressed Surface — Research Synthesis.md` (the navigable evidence base, full read of the
> nav-index + Rounds 1–4) + intent-studio.md §5 (code-truth on main). Design source the Criteria itself
> names: `design/"Possibility Space — free-ball (my ideas).md"` Block 21 (+17–20).

## 1.0 · The one-sentence intent

This surface is **the address system made operable as a face**: every meaningful UI element carries a
`ui://` address; clicking an element **indicates + consents** (it does not execute); the right-hand-man
**proposes** the action in chat; the action runs only through **governance + see-and-approve**. Context,
history, comments, chats, twin-gold, versions, and self-changes all **live at the address** and
auto-resolve into the RHM's awareness when the operator is at that locus. The mockup studio is the first
concrete consumer: "the studio surface implementing I1+I5+I6+R2+L1 on the mockup corpus" (intent-studio §5.5,
§7).

## 1.1 · The load-bearing interaction model (DESIGNED — Tim, 2026-06-04; baked into the Criteria header)

> **"Click INDICATES + CONSENTS; the RHM proposes in chat; action goes through governance + see-and-approve
> — NOT click=execute."**

This is the spec's spine. A click is *attention + consent to consider*, not actuation. The Research
Synthesis frames the open fork this resolves (§R1-rhm HEADLINE): does a click route through governance
posture, OR *is* the human click the authorization event? The Criteria resolves it as **address-keyed
governance** (I4): the tier comes from the address's union record, not the verb — so an AUTO-tiered address
(a bare run/build) acts immediately (preserving the already-fixed canvas RUN, U1), while a CONFIRM/LOCKED
address PROPOSES → see-and-approve → then acts. INFERRED: this is the same law as everywhere in the Company
— route on **declared type/consequence/posture, never a confidence value or generic judgement** (mirrored
verbatim in Collective Cognition §2.5 Triage).

## 1.2 · The full designed shape, per-criterion — DESIGNED-shape + BUILT/DESIGNED-☐ status

### GROUP 0 · PREREQUISITE

**C0 · CORPUS-IMPORT** — *Designed shape:* the corpus design-system (`design-system.css`, `tokens.json`,
`addresses.json`, `_system/check.py`+`emit.py`) lives in `~/company/design/` as a one-way synced copy;
`check.py` runs against `canvas/app/**` and exits non-zero on a planted off-token literal (proves the lint
works in-repo). *Status:* **DESIGNED-☐** (Criteria; confirm: review-executability B-1 — corpus not in repo).
*The FORM gate's prerequisite.*

### GROUP 1 · SPINE (addressing + concurrency)

| ID | Designed intent (the shape) | Test | Status (vs §5 code-truth) |
|---|---|---|---|
| **S0** | ONE canonical address grammar `ui://<region>/<element>[/<sub>][/@state]` + one union record `{address, region, capabilities[], represents→feature, code→code://symbol, kind, state-applies}`; BOTH `design/addresses.json` and the live `UI_REGISTRY` validate against it. | `address_grammar_acceptance.py` | **DESIGNED-☐**. Two non-interoperable grammars today, only `canvas` overlaps (Research Synthesis §R3 CONTRACT.0 — Verified mismatch). The single load-bearing reconcile. |
| **S1** | `UI_REGISTRY` carries 24+ **element**-level addresses (not just 7 regions); `/api/ui_info` serves them; orphan check = zero used-but-unregistered. | `ui_registry_acceptance.py` | **DESIGNED-☐**. Today 7 region handles (`suite.py:2559`); FE has 9 DOM attrs, 7 served — internally inconsistent (Synthesis §R2 §8). |
| **S2** *(keystone)* | every relevant `_emit` site stamps the `ui://` address into `meta` (additive); `events_since`/`/api/stream` carry it; a test asserts each of ~20 emit kinds carries `address`. | `event_address_acceptance.py` | **DESIGNED-☐ (substrate REUSE)**. The store keystone holds — `append_event` writes `{seq, ts, **event}`, meta fully open, zero reader breakage (Synthesis §R1-engine SEAM 1, Verified). Work = ~20 emit sites, not the store. |
| **S3** | a backend resolver maps `ui://`→`code://` symbol(s)→file `scope[]`; reachable from a face; proven on a real address (establishes `code://` in the backend). | `address_scope_acceptance.py` | **BUILT on main** — `Suite.resolve_scope(ui_addr)` (`suite.py:6929`), sourced from `design/_system/code-symbols.json`; empty scope ⇒ DENY-ALL (fail-safe). intent-studio §5.2; corroborated live by Operable Interface GC1/GC5 (`address_scope_acceptance`, `resolve_scope('ui://canvas/wire-request')`). **⚠️ SOURCE CONFLICT, RESOLVED: the IA Research Synthesis (2026-06-04) calls S3 NET-NEW ("no `code://` scheme; `grep code://`=0"). intent-studio §5 (2026-06-08) supersedes it — §5 is 4 days newer and read the live `resolve_scope` function body. S3 was BUILT in the interval; this is time-staleness in the Synthesis, NOT a worktree-vs-main split. Trust §5.** |
| **S4** *(foundational 🔴)* | graph load→mutate→save + dispatch-claim guarded by `fcntl` across bridge+MCP; hot writes `fsync`; concurrent-writer test shows no lost-update/double-dispatch; deadlock-safety = timeout-wrapped. | `concurrency_acceptance.py` | **DESIGNED-☐ + RISK(HIGH)**. Two processes, one store, in-process `threading` locks only, no `fcntl`/`fsync` (Synthesis §R1-engine SEAM 8b, Verified). The surface ADDS writers → the load-bearing engine risk. |
| **S5** | each of the 7 `node_states` carries a `render` (token+icon+shape) served via `capabilities()`. | `node_states_render_acceptance.py` | **DESIGNED-☐ (EXTEND)**. Vocabulary served (7 states, `suite.py:56`); **no `render` field** (Synthesis §R1-engine SEAM 7). Corpus has the bindings; backend lacks them. |

### GROUP 2 · SURFACE / FORM (the FE rebuilt on the spine)

| ID | Designed intent | Status |
|---|---|---|
| **F0** *(FE gate)* | FE componentized (no 1659-line `Hud()`); a state container (not 37 useState + 6 globals); a top-level layout shell (grid/dock, not absolute-px islands); every preserved capability still works. | **DESIGNED-☐ (NET-NEW restructure)**. The whole app is one file today (Synthesis §R2 §0). |
| **F1** | app imports the in-repo corpus `design-system.css`; zero off-token hex/rgba + zero bespoke inline styles (lint-clean); whole app on corpus tokens. | **DESIGNED-☐**. ~29 hex + ~12 rgba + 22 inline today; app imports only its own `app.css` (Synthesis §R2 §3, §R3 §1 — drop-in feasible for tokens). |
| **F2** | usable at 1440/768/390, no overlap, panels dock/collapse; the corpus 3-breakpoint grid. | **DESIGNED-☐**. Responsiveness = zero today (`@media`=0, `grid-template`=0; fixed-px islands overlap on phone — Synthesis §R2 §4). |
| **F3** | the 4 render sites read `capabilities().node_states`; `failed` shows distinctly w/ error string; portal `live`/`empty` from derived state. | **DESIGNED-☐**. `node_states` never referenced in `App.tsx` (grep=0); status hardcoded 4× (Synthesis §R2 §2 — the decisive negative finding). Pairs with S5. |
| **F4** | every meaningful element carries `data-ui-ref="ui://…"` conforming to S0/S1; orphan check clean. *(needs S0,S1)* | **DESIGNED-☐**. Enables the design-critic's address coverage + the I-group (clicks need DOM addresses). |
| **F5** | `api.chat`+siblings check `r.ok`, surface the 400 `{error}` as a visible error state; shell wrapped in error boundary; forced backend-down does NOT white-screen. | **DESIGNED-☐**. `api.chat` no `r.ok` → `setChat(undefined)` → white-screen; Hud shell unwrapped (Synthesis §R2 §5). |
| **F6** | RHM model = registry dropdown (same source as node configs), not free-text. | **DESIGNED-☐**. Free-text today; split-brain vs node dropdowns (Synthesis §R2 §7). |
| **F7** | silent `catch{}` swallows (boot/SSE/poll) surface a visible notice; no silently-empty panel (rule 4 — fail-loud). | **DESIGNED-☐**. Silent catches at boot/SSE/poll today. |
| **F8** | live fleet (model·kind·alive), registry-fed, at `ui://models`; navigable panel. | **DESIGNED-☐**. |
| **F9** *(FORM gate live)* | corpus `check.py` runs against `canvas/app/**` with `--fail-on` AND `suite._design_critic` (the stub at `suite.py:2186` that hard-returns `(False,…)`) is replaced with the real `design_lint`+critic call. | **DESIGNED-☐**. The stub's documented graduation (Criteria; confirm review-executability V-1). |

### GROUP 3 · INTERACTION (click INDICATES+CONSENTS → RHM proposes → governance + see-approve)

| ID | Designed intent | Test | Status (vs §5) |
|---|---|---|---|
| **I1** | clicking ships the element's `ui://` address as the locus (widen `focus` beyond canvas node-ids); the RHM reply reflects the indicated thing; the indicated element visibly selected. *(needs F4)* | — | **DESIGNED-☐**. `focus` is FE-ephemeral, canvas-only today (Synthesis §R1-rhm SEAM 4). The widen-the-`focus`-vocabulary point. |
| **I2** | a new operator-face `/api/act` builds the structured `{verb,address,args}` dict and calls `_dispatch_rhm_action` directly (bypassing prose-parse), re-folding `_confirmation_for`+governance; inherits the 7-verb whitelist + no-self-apply; proven by a real click → verb → result. | `act_endpoint_acceptance.py` | **DESIGNED-☐ (REUSE dispatcher + EXTEND endpoint)**. `_dispatch_rhm_action(dict)` exists (`suite.py:1205`); tests already call it directly — the cleanest seam (Synthesis §R1-rhm SEAM 1 + HEADLINE). intent-studio §5.4. |
| **I3** | the RHM proposes an action rendered as an **approve-able affordance** in chat (verb+address); approving fires `/api/act`; action runs only on approve. | — | **DESIGNED-☐ (NET-NEW, REFUTE)**. Today is execute-then-render (`App.tsx:920-943`); no path constructs an un-committed `{verb,address}` affordance (Synthesis §R1-rhm SEAM 2). The heart of the click-model. |
| **I4** | a click's tier is resolved by **address→tier** (the union record's governance field), NOT by verb; AUTO acts immediately; CONFIRM/LOCKED PROPOSES → see-approve → acts; **a bare run/build stays AUTO** (preserves U1). | `click_tier_acceptance.py` | **DESIGNED-☐ (EXTEND)**. `guard()`+postures exist (`governance.py:10-48`) but verb-keyed; run/build ARE AUTO (review-code-truth ISSUE-1 — the explicit do-not-build is the verb-keyed mislabel). |
| **I5** *(two faces; needs-tim)* | clicking a `ui://` (design) attaches a comment; clicking a `run://` (live) with a consequential verb proposes an operation; never blur. The *visible signal* of which mode a click is in is a **reserved Tim design call** (build a reasonable default, design-critic judges, flag for Tim). | — | **DESIGNED-☐ + needs-tim**. The clean ui://=annotate/run://=operate split is overstated — `show`/walkthrough drive the camera via `ui://` read-only; the real safety seam is `capabilities`+`tier`, not the scheme (Synthesis §R3 CONTRACT.2). |
| **I6** | `POST` attaches a comment/`annotation://` to a `ui://` address; persisted; retrievable by address. | `annotation_acceptance.py` | **BUILT on main** — `Suite.annotate(address, text, source)` (`suite.py:3967`, S0-gated, addressed event) + `annotations_at(address)` (`suite.py:4030`, disk-backed thread). intent-studio §5.1. *(The studio's free-text-jsonl box is the degenerate stand-in for THIS.)* |
| **I7** *(§21.1's 4th attach-type)* | a chat thread attaches to a `ui://` address (`chat://`), persisted, retrievable; feeds the RHM's context resolution (R2) for that locus. | `addr_chat_acceptance.py` | **BUILT on main** — `Suite.attach_chat(address, text, role)` / `chats_at(address)` (`suite.py:4191`/`4223`). intent-studio §5.1. |

### GROUP 4 · RESOLUTION (attention → context)

| ID | Designed intent | Test | Status (vs §5) |
|---|---|---|---|
| **R1** | the backend holds the operator's current `ui://` locus (none today); set on indicate (I1), readable by the RHM. | — | **DESIGNED-☐ (partial substrate)**. No persistent backend locus; `focus` is per-request, canvas-only (Synthesis §R1-rhm SEAM 4). BUT `_registry_ui_target` (`suite.py:5405`) already stamps a registry-valid `ui_target` into payloads — the locus *carrier* exists; a persistent current-locus is the net-new (intent-studio §5.2). |
| **R2** | info attached to addresses/types/screens (incl. I6 annotations + I7 chats) **auto-resolves** into the RHM context at the locus; re-keyed keyword→address; a **relevance/recency decay** bounds it (no flood). | `addr_context_acceptance.py` | **DESIGNED-☐**. Today retrieval is keyword-keyed (`suite.py:917-939`); `annotate`'s docstring says it *feeds* R2 but the single `/api/context?address=` resolver is net-new (Synthesis §R3 CONTRACT.3; intent-studio §5.4). Replaces context-stuffing. |

### GROUP 5 · BLUEPRINT (corpus as importable build-spec)

- **B1 · importable blueprint** — the corpus dir carries a buildable spec (tokens + component-inventory +
  surface-specs + connection contract + lint-rules + annotated examples) such that a fresh Claude Code
  session builds a faithful FE from it; demonstrated by building one surface from the blueprint alone.
  **DESIGNED-☐** (the substrate is largely built — Synthesis §R3 PART 2 CONTRACT.5).
- **B2 · connection-contract doc** = the S0 artifact written as the importable contract (what the FE sends,
  reads, how an element declares its address). **DESIGNED-☐** (a partly-stale `CONNECTION-CONTRACT.md`
  exists — §5.4 says verify every tag against `suite.py`).
- **B3 · filesystem-as-graph** *(fidelity ISSUE-2)* — screens laid out in a directory mirroring the journey
  sequence (the layout = the nav graph); **address-references carry the cross-edges** (the tree holds
  structure, addresses hold the web). A tool reads layout+refs → the journey graph (matching
  `register.json`). **DESIGNED-☐**. *(The tree-vs-graph tension is held, not resolved.)*

### GROUP 6 · LOOPS CLOSED

| ID | Designed intent | Status (vs §5) |
|---|---|---|
| **L1** | a comment-at-address becomes a **build-intent** (spec + `scope[]` via S3) via `surface_build_intent`; surfaces for approval at that address. *(needs S3)* | **DESIGNED-☐ (front-door BUILT)**. `surface_build_intent` IS built on main (the wire's entry seam); the address→intent leg is the net-new bind (intent-studio §5.4, G7). **This is the studio's actionable-feedback end-state.** |
| **L3** | clicking an element shows everything that happened at its address (`decision_view` filter widened `sid→address`); navigable history. *(needs S2)* | **DESIGNED-☐ (substrate BUILT, near-free post-S2)**. `address_view(address)` exists (`suite.py:8199`); the filter-widen is near-free once S2 stamps addresses (intent-studio §5.2). |
| **L4** | an addressed comment flows `append_chat→training_signal` carrying its address (gold+located). | **BUILT on main** — `ingest_comment(address, text, source)` (`suite.py:3995`) does `annotate` + one `append_chat` → located gold for the twin, provenance-graded (intent-studio §5.1). Near-free. |
| **L5** | "what changed here?" filters `self_change_log` by the S3 address→code join; revert at `ui://workshop/self-changes`; per-address change list. *(needs S3)* | **DESIGNED-☐ (substrate BUILT)**. `self_changes_at(ui_addr)` (`suite.py:7622`) + `revert_self_change(sha)` exist; the corpus-side join is the net-new (intent-studio §5.2; Synthesis §R1-engine SEAM 5). |
| **L6** | a ref→version index exists (today `set_ref` overwrites); a portal shows prior versions of an addressed output; navigable version surface. | **DESIGNED-☐ (NET-NEW)**. No ref→version index; CAS bytes survive but nothing maps ref→prior-hashes (Synthesis §R1-engine SEAM 4). |
| **L7** *(voice deixis)* | "run this / why is this stuck" resolves "this" to the locus (R1). *(needs R1/R2)* | **DESIGNED-☐ + needs-tim** (STT-gated, not headlessly closable). |
| **L8** *(gain #9)* | a surfaced inbox item carries its `ui://` target; clicking navigates to the thing in context. *(needs S1)* | **DESIGNED-☐ (near-free)**. Surfaced items are open dicts; a `ui://` target lands in `payload` cleanly (Synthesis §R1-engine SEAM 2). |
| **L9** *(gain #2)* | a click-path through addresses is recordable as a journey/walkthrough. *(needs F4)* | **DESIGNED-☐ (NET-NEW reverse)**. Forward walkthrough-drive is BUILT; reverse journey-capture is net-new (Synthesis §R1-rhm SEAM 3). |
| **L10** *(gain #10)* | a surface shows "cached/stale at this address" from `_memo_sig` (recompile+input-hash compare). | **DESIGNED-☐**. "cached" is a served node-state (free); "stale" derivation is net-new (Synthesis §R1-engine SEAM 8a). |
| **L2** *(the wire trigger — 🔒)* | a production caller for `drive_dispatchable` + `resolve_surfaced`-approve→`dispatch_decision` link + `COMPANY_WIRE_PERMISSION=acceptEdits` as a flag; the circuit **proven by firing `claude -p` ONCE on a throwaway test build-intent** end-to-end in the worktree (gated, logged). Does **NOT** autonomously self-modify real surface code unattended (🔒 after the test proof). | **DESIGNED-☐🔒 (built-not-armed)**. `resolve_surfaced` approve only EMITS the resolve event — it does NOT call `dispatch_decision`; `drive_dispatchable` has NO production caller; `PERMISSION_MODE` default = `plan` (Synthesis §R1-wire MISSING TRIGGER, Verified). The loop has never closed live. |

## 1.3 · BUILT-on-main vs DESIGNED-☐ — the summary cut (cross-ref intent-studio §5)

> The advisor's verification check, confirmed against §5 verbatim:

**BUILT on main (read in the `suite.py` function body — present-tense true):**
- **I6** `annotate` / `annotations_at` (the comment thread at an address)
- **I7** `attach_chat` / `chats_at` (the chat thread at an address)
- **F1-presentation** `set_presentation_pref` / `presentation_pref_at` (how Tim wants *this* presented,
  per-address, pin-persistent — the up-translate organs consult+apply it) — *note: this is the F1 of the
  intent-studio §5.1 reading; distinct from the Interactive-Surface F1 token-source criterion above*
- **S3** `resolve_scope` (`ui://`→`code://`→file `scope[]`, fail-safe DENY-ALL on empty)
- **L4** `ingest_comment` (located twin-gold)
- **L3/L5 substrate** `address_view`, `self_changes_at`, `revert_self_change`
- **address_help** (`suite.py:1959`) — the composed 3-leg resolver (what_this_is · how_to_change w/
  blast_radius · how_to_use) — and **up_translate** (`suite.py:5100`), **`_registry_ui_target`**
  (`suite.py:5405`, the locus carrier), all BUILT.
- The bridge GET route table for them (`/api/ui_info`, `/api/scope`, `/api/address-help`, `/api/annotations`,
  `/api/chats`, `/api/presentation-pref`, `/api/self-changes-at`, `/api/address-history`, …) — BUILT.

**DESIGNED-☐ (net-new binds, not yet on main):**
- **S0** one canonical grammar (the reconcile) · **S1** element-level registry · **S2** event-address-stamp
  (~20 sites) · **S4** cross-process `fcntl`/`fsync` safety · **S5** render field
- **F0–F9** the entire FORM rebuild (the FE is one 1659-line file, zero responsive, doesn't consume
  `node_states`, doesn't import the corpus CSS)
- **I1** persistent locus widen · **I2** `/api/act` · **I3** propose-affordance · **I4** address→tier ·
  **I5** annotate-vs-operate signal (needs-tim)
- **R1** persistent backend locus · **R2** the single `/api/context?address=` auto-resolver
- **L1** address→intent leg · **L6** version index · **L9** reverse journey · **L10** stale-at · **L2** the
  wire trigger (🔒)

**INFERRED — the shape of the gap.** The *attach-context primitives* (I6/I7/F1/L4) and the *resolution
substrate* (S3/address_help/up_translate/`_registry_ui_target`) are BUILT. What is missing is **the spine
that addresses every element (S0/S1/S2/F4), the FORM rebuild that renders on it (F0–F9), and the
interaction loop that makes a click a governed proposal (I1–I4) auto-resolving context (R1/R2) and closing
the build loop (L1/L2).** The studio's whole disconnect (intent-studio §4) is that it reinvented the
already-built primitives instead of composing on them.

---

# PART 2 · PER-SURFACE SKELETONS + INTENT — the §3E pack at full scope

> Source: `design/mockups/*.html` (the corpus, structurally read for IA-desktop), the studio's GROUPS array
> (intent-studio §3.1, 7 groups / 20 mockups), the IA proposal, and the surface narratives in
> `context-13-the-surface`, the Operable triads, and the Sequenced-Systems doc. Each surface: designed
> intent + how it composes. Tag per row.

Every surface below **composes the same primitives**: it is *assembled from the registries* (views from
`register.json`, look from `tokens.json`, addresses from `addresses.json`, actions through the wire, modes
from the mode-registry, context from the spine — Operable Interface law G1/G2), it carries `ui://`
addresses, and it threads the RHM. The IA is the **container** that places them (Part 4).

## 2.1 · The Mockup Studio — *the first surface Claude Design designs*

- **Intent (DESIGNED).** Tim's design-review portal, run *before* the real build. Three parts: GALLERY RAIL
  (corpus) · DEVICE STAGE (iframe of the chosen mockup, phone/desktop) · FEEDBACK / RHM PANEL. The loop:
  VIEW → give feedback **conversationally to the RHM** → feedback CAPTURED as structured data at the
  element's `ui://` address → RHM/agent updates the mockups. (intent-studio §2.1)
- **Built reality (BUILT, worktree-only).** A standalone HTML portal; "element" is a **free-text string** in
  a **private `.feedback/<file>.jsonl`** via a bespoke `/api/mockup-feedback`; the right panel is a **static
  textarea with RHM chrome**, not the organ. Explicitly **superseded by a rebuild as a page of the main app
  reusing the real RHM organ** (`MERGE-COORDINATION.md:143`). (intent-studio §3, §1)
- **Composes (DESIGNED end-state).** = I1 (click-to-indicate the element's `ui://`) + I5 (annotate-vs-operate)
  + I6 (`annotate` to the address) + R2 (context auto-resolves at the locus) + L1 (feedback→build-intent via
  `surface_build_intent`) + L4 (located twin-gold) — on the mockup corpus, with the right panel = the real
  `chat` organ. (intent-studio §5.5, §7)

## 2.2 · Information Architecture — *the commander's bridge* (the PARENT — see Part 4)

- **Intent (DESIGNED — IA-desktop.html head comment).** "Tim reacts by sight BEFORE the real build." The
  proposed desktop IA: **three zones + a thin grouped top toolbar + a docked RHM pane.** The native desktop
  value = **SIMULTANEITY**: one subject (the `ask` node, `ui://canvas/node/ask`) threaded LEGIBLY through all
  three regions AT ONCE — selected on the BOARD (gold ring, state=ran) · its config+output in the INSPECTOR ·
  a conversation ABOUT it in the RHM pane — *the same address visible in all three, so the eye threads them.
  That coherence IS the demonstration.*
- **Layout skeleton (BUILT-as-mockup).** A CSS grid: `rows: 48px toolbar / 1fr / 232px RHM` ×
  `cols: auto rail / 1fr board / 360px inspector`; areas `toolbar·toolbar·toolbar / rail·board·inspect /
  rail·rhm·rhm`. So: **toolbar** (grouped verbs — Run carries the gold, demoted rest; a presence dial;
  teach/show-me) · **rail** (the node palette — process/content/config-slot node-types) · **board** (the
  tldraw canvas) · **inspector** (right rail: selected node config+output, *plus* the addressed strata:
  what-can-I-do-here / comments&chat-here / history-at-this-address / versions / self-changes-here /
  code-behind-this — **the Part-1 I/R/L group surfaced as inspector panels**) · **queue** (review · 3
  need-you, the inbox) · **RHM pane** (the docked chat, scoped to the selected address).
- **Surface-everything (DESIGNED — Tim's locked decision).** Every LATENT capability gets a desktop home as a
  **recognisable collapsed affordance** (chip / count / sparkline / one-row ledger w/ chevron) —
  progressively disclosed, NOT an 8-deep junk-drawer. Named by real route, **no fiction**: `/api/knobs` (live
  model knobs) · `run-stats` (learning-by-use) · R2 composition (live tuning) · panel/extend (grow the UI) ·
  annotations/chats readback · self-change-log · voice-trial debrief.
- **Composes.** Everything — it is the assembly of all other surfaces into one instrument. (Part 4.)

## 2.3 · Canvas / operating surface (A1 empty · A2 desktop+mobile · A3 inspector)

- **Intent (DESIGNED + BUILT-as-mockup).** The core operating surface: compose nodes, wire chains, run, see
  outputs, configure. The Operable Composition Surface bar (Tim, 2026-06-02): *"compose and run processes
  over my own model fleet, and act on what they produce"* — A (node config) · B (full model fleet, chat +
  embedding) · C (chains of any shape, persist) · D (run/rerun/force/legible) · E (embeddings first-class) ·
  F (act on outputs) · G (live event stream, pushed not polled).
- **Built reality (BUILT on `operable-surface` branch, not merged).** A–G verified by use 2026-06-02:
  editable inspector, 15 live models, persistent layout, force+status, EventSource replaces poll,
  embeddings, act-on-outputs. **needs-tim:** the drag-to-connect *gesture* (nubs render, wire-button
  fallback works). (Operable Composition build log)
- **Composes.** The board+inspector zones of the IA; the node subsystem is the one place the
  generic-render-from-registry pattern is real (Sequenced-Systems round-3 validation).

## 2.4 · Portals / transclusion (A11)

- **Intent (DESIGNED).** Present-in-place: "show me something from elsewhere" is a **portal** (a resolved
  reference window onto another address's output), not a bolted-on overlay (context-13:32,43,87;
  Sequenced-Systems C). The mechanism the RHM uses to drive the shared surface during a walkthrough.
- **Composes.** Consumes a resolved `ui_target`/address; the live window resolves the *current* pointer
  (BUILT); *prior versions* (L6) is net-new.

## 2.5 · Workshop (A12 — full-detail node)

- **Intent (DESIGNED + BUILT-as-modal).** The full-detail view of a node/output — the deep inspect surface;
  also the `workshop` chrome region where self-changes + revert live (L5 / `ui://workshop/self-changes`).
- **Composes.** The address strata of Part 1 at full depth (history, versions, self-changes, code-behind).

## 2.6 · RHM presence / scenario player (SCENARIO-PLAYER.html · A2-rhm-elevated)

- **Intent (DESIGNED).** The aesthetic + **presence** reference — the living-instrument layer (aurora, orb,
  gold range, status-by-light) the IA borrows. The RHM as a felt, alive co-presence. The voice surface
  expressing the resolved field (Collective Cognition §8 — "alive because the subconscious has already
  perceived").
- **Composes.** The visual language of the whole product (one design language — Operable Interface H2); the
  conscious surface of the collective cognition.

## 2.7 · Walkthrough (B3 — the RHM drives the view)

- **Intent (DESIGNED).** The RHM drives the shared surface step-by-step to direct Tim's attention — system-
  INITIATED step-sequences (Operable Interface C1: "show me how"). The walkthrough **IS a graph**:
  review-items = nodes, the session = a graph-run, cursor = operator-paced readiness, Next = fire
  (Sequenced-Systems #3). The Show-me bootstrap teaches Tim to request-a-change-and-approve from inside
  (Operable Interface C2).
- **Built reality.** Forward drive is **BUILT** — `present_current` stamps a registry-valid `ui_target`; the
  FE `resolveUiTarget` drives camera/spotlight; `show` resolves bare handles leniently (Synthesis §R1-rhm
  SEAM 3). Net-new: the sequencer/pacing as a system-initiated organ, element-level `show` (Operable
  Interface C3), reverse journey-capture (L9).
- **Composes.** The Sequences primitive made operable for the human-in-the-loop (Part 3). Its first consumer
  is the build loop reviewing its own build (recursive).

## 2.8 · Presence dial (B4 — 8 modes)

- **Intent (DESIGNED).** The dial of **how much the RHM presents vs. acts** — modes as a **hierarchical
  type-registry** (≤8 top-level, each with sub-types), each mode-type carrying its **context-resolution
  declarations** (modes and context-resolution are ONE system — Operable Interface E1). Auto-detect is a
  positionable config toggle (off/suggest/auto — E2). `walkthrough` drives the sequencer; `decide-for-me`
  raises autonomy, twin-gated.
- **Built reality (BUILT-backend, partial).** The mode type-registry + per-mode context-resolution
  declarations + the off/suggest/auto toggle are exposed in `capabilities().mode_registry` (Operable
  Interface GC3, GC6 — the runtime setter is LIVE). Deferred: the FE mode surface; consent declarations
  wired into the offer path; the auto-detect *detector*.
- **Composes.** Modes resolve context (the spine); the dial is a view-mode of the one mode-registry
  substrate, NOT a separate command center (Collective Cognition §7).

## 2.9 · The twin / model-of-Tim (B6)

- **Intent (DESIGNED).** The model-of-Tim — the RHM's predictive core, the **self underneath** the voice
  (Collective Cognition §8). It is what makes `decide-for-me` real and shrinks how much reaches Tim over time
  (the escalation ladder). Fed by **located gold** (L4) — every addressed operator comment trains it,
  provenance-graded (Tim's words gold; the twin's working-grade).
- **Built reality.** `model_of_tim.py` exists; `suite._model_of_tim_digest()` injects it into chat; it is
  **corpus-pending / cold-start** (reasons from explicit principles, doesn't yet *predict*).
- **Composes.** The write-half of the collective cognition (Part 3); consumes located-gold from every
  addressed surface.

## 2.10 · Inbox (C1 — three lanes) — *the chief-of-staff*

- **Intent (DESIGNED).** ONE place where **anything** needing Tim lands with ONE lifecycle (a build flag, a
  decision, a verification, an idea) — the shared substrate of attention (Sequenced-Systems A). Three lanes
  (the triage of Collective Cognition §2.5): **just remember** (silent) · **inject quietly** (calm surface) ·
  **escalate now** (interrupt + contact). One queue with an `origin: responsive|generative` polarity (idea-
  capture is the generative twin — Sequenced-Systems reply #5). The IA's `queue · review` zone.
- **Built reality (BUILT).** The inbox + COA surface exist; surface-output→inbox is wired (Operable
  Composition F2). Net-new: the three-lane typed triage, the live-conversation-on-revisit (Operable
  Interface B3), the `ui://` target on each item (L8).
- **Composes.** The SURFACE station (A) of the Sequences circuit; the deposit point for the wire's review.

## 2.11 · Build review (C3) — *demonstrate-first; the wire's review surface*

- **Intent (DESIGNED).** Where a self-build result is reviewed **demonstrate-first** before it is accepted —
  the see-and-approve face of the decision→implementation wire. The IA shows it inside the queue:
  *"build result · review · The self-build added a retrieve node + wired it. Verified by use. ⌗ 2 files
  changed · diff ready · git-reversible · accept / send-back / diff."*
- **Composes.** The RESPOND/ACT stations of the Sequences circuit; consumes L1/L2 (the wire); operator-gated
  `resolve` (off the agent face — no-bypass).

## 2.12 · Replay / decision trajectory (C5)

- **Intent (DESIGNED).** The decision-trajectory surface — replaying what happened, the addressed history at
  scale (L3 generalised). The `coa` decision-compiler records the WHY *down*; replay reads it back.
- **Composes.** `address_view` / `decision_view` (BUILT substrate); the trajectory faculty of the context
  spine.

## 2.13 · Wire states / lifecycle (D6)

- **Intent (DESIGNED).** The decision→implementation wire's lifecycle made legible: `surface_build_intent →
  [operator approve] → dispatch_decision → implement.launch (claude -p) → verify → guarded close →
  surface-for-review`. The states of a build-intent as it moves.
- **Built reality (front-door BUILT, trigger 🔒).** `surface_build_intent` + `/api/build-intent` BUILT;
  the MISSING TRIGGER (approve→dispatch) is built-not-armed (Synthesis §R1-wire; Part-1 L2).
- **Composes.** L1 (entry) + L2 (the trigger) + build review (C3, the review face).

## 2.14 · Self-mod / revert (D7) — *the self-change audit ledger*

- **Intent (DESIGNED).** The ledger of what the system changed about itself, with **revert at the address**
  (L5: `ui://workshop/self-changes`). "What changed here?" filtered by the S3 address→code join.
- **Built reality (BUILT substrate).** `self_change_log` carries `changed_files`; `revert_self_change`
  (operator-only, conflict-aware) exists; `self_changes_at(ui_addr)` exists. Net-new: the element-level
  addressing + the corpus-side join + the "revert at this address" affordance.
- **Composes.** L5; the `workshop` region; the no-bypass guarantee (revert is operator-gated).

## 2.15 · Model fleet (E1)

- **Intent (DESIGNED).** The live chat+embed model fleet (model·kind·alive), **registry-fed** (`/api/ui_info`
  / `list_models`, never a baked list — the path-of-least-resistance correctness rule, Operable Composition
  B1). The latent-gold knobs/run-stats land here (`/api/knobs`, `run-stats`). Part-1 F8 (`ui://models`).
- **Composes.** The native-model-layer; the "awake subconscious" VRAM working-set view (Collective
  Cognition §5 — resource-management IS attention).

## 2.16 · Activity / now + events (F4) — *the SSE event stream*

- **Intent (DESIGNED + BUILT).** The live event stream surface — the engine pushes (SSE `/api/stream`,
  gapless via `Last-Event-ID`), the canvas subscribes, cross-process co-presence (an MCP-face or 2nd-browser
  event appears live). The IA shows it as `activity · ambient · feed`.
- **Built reality (BUILT).** SSE + `mergeEvents` seq-dedup + gapless resume are built and solid (Operable
  Composition G; Synthesis §R2 §7). The substrate S2 stamps addresses onto.
- **Composes.** The keystone S2 (addressed events) feeds L3 (addressed history); the WORLD/system-events
  layer of the cognition (Collective Cognition §1).

## 2.17 · Settings (A3 — elevated, consolidated)

- **Intent (DESIGNED).** One consolidated, designed settings surface — config-lab, modes, models, voice,
  personas — NOT scattered (Operable Interface A3, H). The two-tier model config: load-time capability vs
  live per-request knobs (Collective Cognition §6).
- **Composes.** The mode-registry (E1/E2), the model fleet (E1), the voice trial; folds the mode surface
  (GC3) in.

---

# PART 3 · THE SEQUENCES PRIMITIVE — what it is, why it's foundational, how surfaces use it

> Source: `RHM Walkthrough Organ — Sequenced Systems (build-session take).md` (the "one circuit" frame +
> architecture-session reply), `context-05` (named equivalence at :150), `Collective Cognition` (§4 the
> write-half), the Operable Composition engine model. *Characterized by triangulation across the three
> instances I hold — no further reading needed (advisor).*

## 3.1 · What it is

**The Sequences primitive is one relational loop — `resolve → present/work → persist → next/trigger` — that
the Company runs at every scale, pointed at different content.** It is not a feature; it is the **mechanic**.
context-05:150 names the equivalence explicitly: the human-in-the-loop walkthrough runs the *same*
`resolve → present → persist → next` loop the engine runs over graph nodes — pointed at *review items*
instead of *graph nodes*.

> **"Read it as a circuit, not a checklist. A break anywhere breaks the organ."** (Sequenced-Systems)

The circuit's stations (the walkthrough instance):
```
SURFACE          PRESENT            RESPOND             ACT
(needs-Tim  →  RHM drives the  →  verdict + WHY  →  system acts  →  resolved │ requeue→new work
 → inbox)      UI to it,          recorded,         (governed,        (no-repeat)
               voice-first        operator-gated)   verdict-derived)
```

## 3.2 · Why it's foundational (the recurrence — three citations)

The primitive earns "universal substrate" by **recurring as the same shape across independent instances**:

1. **The engine** (Operable Composition; `scheduler`/`compile`) — graph nodes resolve in dependency order:
   `resolve → work → persist → trigger`. A node fires when its inputs resolve; the output persists to CAS;
   the trigger cascades to fixpoint. *(Operable Composition D1; Collective Cognition §2 "the same operation
   the runtime uses to fire nodes.")*
2. **The walkthrough / review organ** — review-items = nodes, the session = a graph-run, cursor =
   operator-paced readiness, Next = fire. The architecture-session validated this against the live code:
   "operator-paced readiness isn't a new scheduler mode — readiness already waits on any unresolved input,
   so it's a human-writable `go`-gate input on each review-node + a verb that writes it. Zero scheduler-core
   change." *(Sequenced-Systems reply #3, round-3 validation.)*
3. **The collective cognition** — the context cascade runs the *same* `resolve → work → persist → trigger`,
   and the **write-half does four things at once** (Collective Cognition §4): context assembly (the now-field)
   · memory forming (events/CAS = episodic) · learning (gold-grade grows the twin) · skill development
   (recurring resolutions register as new faculties). "One cascade, four functions — which is what makes it
   *cognition*, not a pipeline."

**INFERRED.** Because the same loop is the engine, the human-interaction organ, AND cognition, building any
new capability is **registering a new station/node-type on the existing loop**, not building a new pipeline.
This is why "interact with any part of the UI" becomes *structurally true* once every UI thing is a
registered, addressed node on the loop (the Part-1 spine) — and why the walkthrough-IS-a-graph unification
*shrinks* the build (reuse the scheduler, human-paced) rather than adding to it.

## 3.3 · How surfaces use it

- **The inbox (2.10)** is the SURFACE station — one queue, one lifecycle, `origin` polarity.
- **The walkthrough (2.7)** is the full circuit made operable for the human — the sequencer is the missing
  iterator that turns the inbox pile into a *walk* (Next = page-turn + trigger).
- **Build review (2.11) + the wire (2.13)** are the RESPOND/ACT stations — the verdict (with WHY) becomes the
  system's next action, governed and verdict-derived (`derived_from = resolve-event seq` — the structural
  no-bypass gate, Sequenced-Systems reply #2).
- **The twin (2.9)** is fed by the write-half's *learning* function on every pass.
- **Replay (2.12)** reads the *persist* station back as trajectory.
- **The canvas (2.3)** is the loop's original instance (graph nodes) — every other surface is the same loop
  pointed at different content.

---

# PART 4 · THE SURFACE RELATIONSHIP MAP — the IA as the parent that places the others

> Source: `IA-desktop.html` (read structurally), intent-studio §6 (the derived surface list + the IA-as-parent
> inference), the Operable Interface assembly law (G1).

## 4.1 · The parent: the commander's bridge

**The Information Architecture (the commander's bridge) is the parent surface — it is the one container that
PLACES every other surface as a zone, panel, or progressively-disclosed affordance within it.** The IA is
not a peer of the canvas or the inbox; it is the *instrument* they are mounted in. (intent-studio §6:
"the IA proposal is the parent surface that decides where every other surface lives.")

The placement (from the IA-desktop grid):

```
┌──────────────────────────── TOOLBAR (grouped verbs · presence dial · teach) ────────────────────────────┐
│  Run(primary) · layers · fit          [presence: mode·listening]              ☆teach        ⚙settings(2.17)│
├──────────┬─────────────────────────────────────────────┬─────────────────────────────────────────────────┤
│  RAIL    │              BOARD (2.3 canvas)              │   INSPECTOR (2.3/2.5 — the addressed strata)      │
│ (palette │   tldraw · nodes · status-by-light          │   selected node config + output                   │
│  of node │   the SCENARIO-PLAYER aesthetic (2.6)        │   ⌖ what can I do here  (address_help · D2)        │
│  types)  │   show-me overlay (2.7 walkthrough)          │   💬 comments & chat here  (I6/I7)                 │
│          │   portals (2.4)                              │   ⧗ history at this address  (L3)                 │
│          │                                              │   ⎘ versions of this output  (L6)                 │
│          │                                              │   ⟲ self-changes here  (L5 · 2.14)                │
│          │                                              │   ⟢ code behind this  (S3 scope)                  │
│          ├─────────────────────────────────────────────┴─────────────────────────────────────────────────┤
│          │  RHM PANE (2.6 chat, scoped to the selected ui:// address)    │  QUEUE · review (2.10 inbox /     │
│          │  "I see the ask node you've selected" · listening             │  2.11 build review · 2.13 wire)   │
└──────────┴───────────────────────────────────────────────────────────────┴───────────────────────────────┘
   ┌ surfaced-everything strip (collapsed affordances, no fiction): /api/knobs · run-stats (2.15) ·
     R2-composition · panel/extend · annotations/chats readback · self-change-log (2.14) · voice-trial debrief ┘
```

## 4.2 · The threading principle (why the IA is a parent, not a menu)

The IA's reason-to-exist is **simultaneity / the threaded address**: the *same* `ui://canvas/node/ask` is
visible on the BOARD (selected), in the INSPECTOR (config+output+strata), and in the RHM PANE (a conversation
about it) **at once** — so the operator's eye threads the three. This is **Part 1's R1/R2 (the current locus
auto-resolving context) rendered as spatial layout**: the locus is set by indicating on the board (I1), and
every zone re-resolves to that address. The IA is therefore not a navigation shell that *switches between*
surfaces — it is a **co-resolution surface** where all surfaces show the *same locus* simultaneously. That is
the structural meaning of "parent."

## 4.3 · The placement rules (the assembly law)

Per the Operable Interface law (G1/G2), every placed surface is **assembled from the registries, not authored
against them**: the rail palette from the node-type registry, the look from `tokens.json`, the addresses from
`addresses.json`, the actions through the wire, the modes from the mode-registry, the context from the spine.
A surface authored as a bolt-on (the standalone studio, the hardcoded GROUPS array, the parallel `.feedback`
store) is **wrong by this law** — which is exactly why the studio is being superseded by an in-app page
reusing the organ (intent-studio §1, §3.3).

## 4.4 · The relationship graph (who places / who consumes whom)

```
                          IA (commander's bridge) — the parent container
                                          │ places
        ┌──────────────┬─────────────────┼──────────────────┬───────────────┐
     TOOLBAR         BOARD            INSPECTOR            RHM PANE          QUEUE
    (verbs+modes)   (canvas 2.3)   (addressed strata)     (RHM 2.6)        (inbox 2.10)
        │            │  └ portals(2.4) │                     │              ├ build review(2.11)
   settings(2.17)    │  └ walkthrough  ├ I6/I7 comments      │ scoped to    └ wire states(2.13)
   presence dial     │    (2.7)        ├ L3 history          │ the locus          │
   (2.8 modes)       │  └ workshop     ├ L5/2.14 self-mod    │ (R1/R2)            │ deposits
        │            │    (2.5)        ├ L6 versions         │                    ▼
        ▼            │                 └ S3 code-behind      └────────────► twin (2.9)  ◄── learning(§4)
   mode-registry     ▼                        │                                  │
   (substrate)   model fleet(2.15)    address_help/up-translate            replay(2.12)
                 activity/SSE(2.16)    (BUILT substrate)                   (persist read-back)

  The studio (2.1) = a CHILD page of the IA app (the rebuild target), reusing the RHM PANE + I6/R2/L1.
  The Sequences primitive (Part 3) = the loop EVERY zone runs on (resolve→present→persist→next).
```

## 4.5 · Mobile (IA-mobile)

INFERRED (from the Operable Interface A2 parity law + the IA-mobile file's existence — not read in full): the
phone is **not a shrunk desktop** but the **same interaction (point · talk · see · approve)** thumb-first /
voice-first — the "brainwave-on-a-walk" situation. The simultaneity hero gives way to a single-locus-at-a-time
flow (one zone foregrounded, the others a swipe/voice away), because a phone cannot thread three regions at
once. Co-presence survives because any device is a view onto the one server-authoritative session
(reflects-never-owns — Sequenced-Systems reply #6).

---

# PART 5 · SOURCE LEDGER (which sources backed which section — honesty per Tim's rule)

- **Part 1** — `Interactive Addressed Surface — Completion Criteria.md` (full read) +
  `Interactive Addressed Surface — Research Synthesis.md` (full read of nav-index + Rounds 1–4) +
  `claude-design/findings/intent-studio.md` §5 (code-truth on main, function bodies read). The BUILT/DESIGNED
  cut is from §5, NOT the Criteria's ☐ markers. The Implementation Guide was consulted by ID only (build-how,
  out of scope).
- **Part 2** — `design/mockups/IA-desktop.html` (structural read, §2.2); intent-studio §3.1 (the GROUPS
  array) + §6 (derived surface list); `Operable Composition Surface — Completion Criteria.md` (§2.3, 2.10,
  2.16); `Operable Interface — Completion Criteria.md` (§2.7, 2.8, 2.10, 2.11, 2.17 + the assembly law);
  `Collective Cognition` (§2.6, 2.9, 2.15); `RHM Walkthrough Organ — Sequenced Systems` (§2.7, 2.10, 2.11,
  2.14); `context-13-the-surface` (portals, §2.4). Some rows (replay C5, twin B6) are DESIGNED from secondary
  mention — the mockup files themselves were not read.
- **Part 3** — `RHM Walkthrough Organ — Sequenced Systems` (the circuit + replies); `context-05:150` (named
  equivalence); `Collective Cognition §4` (the write-half); `Operable Composition` (the engine loop).
  Characterized by triangulation across these three instances.
- **Part 4** — `IA-desktop.html` (the grid + zones, read structurally); intent-studio §6 (IA-as-parent
  inference); `Operable Interface` G1 (the assembly law). IA-mobile inferred, not read in full.

**Naming note (Collective vs Concurrent Cognition) — distinct things, honestly scoped.** This pass used
`Collective Cognition — the context-resolution spine.md` (the layered perception/context-resolution spine —
how an address becomes awareness). The task also named "Concurrent Cognition docs," which is a **distinct**
system per Tim's own memory: the staged main-stream fed by a swarm of rule-routed small-model roles, "voice
speaks part-N while brain thinks N+1" (backend-build-complete on the `concurrent-cognition` branch; the
`cognition-build` skill). **There is NO separate Concurrent Cognition doc in this build-prep corpus** —
grep over build-prep returns only incidental mentions in other files; that design lives on the branch/skill,
not here. It is backend-cognition (the staged-stream runtime), not a surface, so it is out of this surface
pass's scope — **flagged for a next wave** if the staged-stream needs a surface treatment.

**What is NOT verified here (flagged for a next wave):** the individual mockup file contents for surfaces
2.4/2.5/2.6/2.9/2.11–2.16 (only the IA-desktop and the studio were read structurally; the rest are
DESIGNED from the GROUPS list + narratives); IA-mobile's actual layout; whether the rebuilt in-app studio
exists yet on any branch beyond the supersession note; the Concurrent Cognition staged-stream (above).
