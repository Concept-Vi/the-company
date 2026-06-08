# Area 5 — The Interface + the RHM organ: how a full Coherence interface would compose

> Companion to `../ANCHOR.md`. My allocated area: **what a full Coherence interface would BE — a CLI
> (`company coherence`) AND a first-class in-app surface (sibling of CognitionView) where coherence is
> glanceable, every finding is addressed+clickable, the RHM explains any finding at Tim's altitude, and Tim
> can act through the existing consent+build wire, all live via SSE.** The bet I'm testing: this surface is
> almost entirely *already-present machinery pointed at a new lens* — not a new system. I found that to be
> true, and I found three real seams where it is NOT yet wired. The seams are the gold; I name them precisely
> with file:line so the build can close them, not hand-wave them.
>
> **Legend.** `[OBS file:line]` = I read it in the code. `[INF]` = inferred from pattern, not executed.
> `[IDEA]` = my proposal/extension, not in the code. FORM (the felt aesthetic) is marked `needs-tim`
> throughout — I do NOT self-certify look-and-feel (AGENTS rule 9; CognitionView line 23 does the same).

---

## 0 · The one-sentence shape

A Coherence interface is **AddressHelp's explain-at-altitude move + CognitionView's glanceable
altitude-stepped live surface + the surface_build_intent consent wire, composed over a findings projection
and a `coherence.*` SSE branch** — three organs Tim already has, joined by one lens. It is a **sibling of
CognitionView**, not a forced merge with it. Nothing here is a parallel system; everything reuses an
existing resolver, store, render law, or wire.

The reason this matters for Tim specifically: he drives by sight and by the right-hand-man, not by reading a
call graph. A coherence *report* (even a good CLI one) is the wrong altitude for him. A coherence *surface*
that reads by shape, lets him click a frayed seam, asks the RHM "what is this, what would finishing it mean,"
and lets him say "finish it / leave it, it's by-design" through the consent gate he already uses — that is
the altitude he operates at. The whole area is: **make the integrity model legible and actionable at Tim's
altitude, by reusing the organs that already do exactly this for addresses, cognition, and decisions.**

---

## 1 · The four organs that already exist (the precedents, grounded)

### 1.1 · The RHM organ — `address_help` / `up_translate` / `chat` `[OBS runtime/suite.py]`

This is the heart of "the RHM explains any finding." It is more built-out than the anchor implies.

- **`address_help(ui_addr)` `[OBS suite.py:2174-2265]`** composes THREE legs at one address into one bundle,
  reusing existing resolvers (the docstring is explicit: "no parallel system, rule 3"):
  - `what_this_is` — the registry row's human title / `represents` feature-id (one-source, never invented).
  - `how_to_change` — `resolve_scope` → `blast_radius`: the `code://` scope this address powers + the
    **blast radius** a change would reach (co-reference / structural dependents+dependencies / semantic
    neighbours). This is literally "if you change this, here's what it touches."
  - `how_to_use` — the authored affordance/how-to text.
  - It **degrades clean per leg** (`legs_present:{...}` flags say which legs landed) and **fails loud** only
    on a malformed address (S0 grammar gate, line 2202). This is the exact robustness a findings-explainer
    needs: a finding about an unregistered/no-code address must explain honestly, not crash.

- **`up_translate(kind, ref)` `[OBS suite.py:5775-5868]`** is the generalized "present at Tim's altitude"
  resolver, `kind ∈ UPTRANSLATE_KINDS`. **Crucially, it ALREADY has a `kind == "finding"` branch
  `[OBS suite.py:5828-5855]`** — and the docstring says it verbatim: *"A drift/coherence finding (the shape
  G2 will feed — NOT wired here, that's a later lane)."* The branch:
  - Frames ONLY from the supplied finding (grounding guard — an empty/non-dict finding **abstains** rather
    than confabulating, line 5836-5840).
  - If the finding names a `ui://` address, **enriches the mechanism with that address's blast_radius**
    (reusing the same join address_help uses, line 5849) — so "a drift lead can drill to what a fix would
    reach." That is the RHM explaining a coherence finding *with* its blast radius, already coded.
  - Returns `{kind, ref, lead, mechanism, legs_present, grounded, degraded, note}` — the same envelope shape
    `kind=="address"` and `kind=="decision"` return, so the FE renders all three uniformly.

  **This is the single most important finding in my area: the RHM-explains-a-finding organ is already
  written.** The Coherence interface does not invent it; it *consumes* it. The anchor's §6 wish ("the RHM
  explains it — address_help / up_translate over a finding") is half-built at suite.py:5828.

- **`chat` / `chat_parts` `[OBS suite.py:5142,5183]`** is the conversational RHM, already surfaced as
  `RhmChat.tsx`. A coherence finding can be a *focus* for chat (the chat takes `focus: dict | None`,
  line 5142) — so "talk to me about this gap" reuses the existing chat-with-a-focus path, not a new one.

### 1.2 · The glanceable-live-surface precedent — `CognitionView.tsx` `[OBS canvas/app/src/regions/CognitionView.tsx]`

This is the precedent for the *surface form*. It is exactly the "live, addressed, reflects-never-owns model
rendered as a glanceable surface" the anchor §6 describes, and its design choices are directly transplantable:

- **Three altitudes, default-ambient → drill-down `[OBS lines 11-25, 47-49]`:** Altitude 0 = THE PULSE (a
  breathing iris glyph, `dilation` opens with depth-of-thought, a LOUD red notch when a role failed); Altitude
  1 = THE RIVER (tributaries converge into a brain node, width = contribution); Altitude 2 = THE NODES
  (literal role cards reusing the inspector DOM card pattern). One state var `altitude` (line 49) switches.
- **shape-not-count `[OBS lines 60-61, 68]`:** depth is read as *openness* (a continuous aperture), never N
  literal dots. This is the render-for-Tim's-cognition law in code.
- **reflects-never-owns `[OBS lines 5-8]`:** the view issues NO writes; it only READS `/api/cognition_info`
  (the registry projection) + folds the live `cognition.*` SSE turn. registry-driven (line 9): tributaries
  come from the turn's `cast[]` — no hardcoded role list, so a new role appears with zero FE code.
- **token-only, FORM=needs-tim `[OBS lines 23-25]`:** built on design-system tokens only; the implementer
  explicitly does NOT grade FORM (the iris beauty, the felt shape, on-device legibility are `needs-tim`).
- **Mounting `[OBS App.tsx:46, 183-184]`:** it is one MORE region beside the others, wrapped in a
  `PanelErrorBoundary name="cognition"` so a render-throw degrades to a contained card.
- **Live fold `[OBS useAppController.ts:337-367 (foldCognition), 573-583 (the cognition.* SSE branch)]`:**
  each `cognition.*` event folds synchronously off a ref into `cognitionTurn`; the projection loads at boot
  (line 474, `api.cognitionInfo()`). This is the entire data spine the Coherence surface mirrors.

### 1.3 · The indicate→explain-at-altitude precedent — `AddressHelp.tsx` `[OBS canvas/app/src/regions/AddressHelp.tsx]`

This is the precedent for the *explain* move + the *click-to-element → RHM-explains-it* flow:

- When the operator INDICATES a `ui://` element, this panel shows the three `address_help` legs composed at
  Tim's altitude `[OBS lines 1-7]`. It is NOT a parallel FE composer — the join is backend-side; the region
  only READS the bundle and renders (line 6-7, registry-is-truth).
- **The altitude move `[OBS lines 9-16, 184-219]`:** LEAD with plain-language WHAT + HOW-TO-USE (prose, Tim's
  level); DEMOTE the mechanism (code symbols, files, blast-radius reach) to a **collapsible drill-down, CLOSED
  by default**. "The collapse IS the altitude move." This is the exact pattern a finding-explainer wants: the
  *gap in plain language* up top, the *call-graph drill* hidden until asked.
- **Five degrade states rendered distinctly `[OBS lines 18-27]`** (all-3-present / thin-howto / no-code /
  unregistered / malformed-400) — never blank, never crash. A coherence finding-explainer inherits these.
- **`BlastReach` `[OBS lines 234-278]`** renders the blast radius summarised BY KIND as count chips that
  expand inline (recognition-by-sight, not a wall of symbol names). A finding's "what finishing this touches"
  reuses this component verbatim.
- **The learning loop `[OBS lines 47-68, 126-138]`:** the bundle carries a learned `presentation_pref`; a
  `lead_with:how_to_change` pref auto-hoists the drill-down open. So *how a finding is explained can itself be
  learned per Tim's shaping* — the F1 machinery already there.

### 1.4 · The consent→build wire — `surface_build_intent` → `resolve_surfaced` `[OBS suite.py:6668, 9166]`

This is the precedent for "act from the surface — approve a fix."

- **`surface_build_intent(spec, scope, consequence_class, why, address, symbols, context, blast_radius)`
  `[OBS suite.py:6668-6707]`** mints a build-intent decision into the SAME inbox (no parallel queue). It
  already carries `address` (the `ui://` locus), `symbols` (the `code://` neighbours), `blast_radius`, and a
  bounded `context` bundle. The operator's `approve` is *approve of this scope* (legible consent), and an
  empty declared scope is a DENY-ALL at dispatch (line 6683-6687) — a build can't quietly overrun.
- **`resolve_surfaced(sid, choice, reason)` `[OBS suite.py:9166, 9268]`**: on `choice=="approve"` AND
  `implement.wire_armed()` AND `is_build_intent(d)`, it dispatches the autonomous build (line 9268). This is
  the same path the decision→implementation wire uses.

**A coherence finding maps onto this with almost zero impedance:** a finding *already* carries
`{address, scope/symbols (from resolve_scope), blast_radius (from up_translate's enrichment)}` — exactly the
arguments `surface_build_intent` wants. "Approve a fix for this finding" = build a build-intent from the
finding's fields → operator approves → wire dispatches → reviewer gate verifies → the detector re-runs → the
finding resolves. The anchor §5 loop and §6 "act through the consent-gated build wire" are the SAME wire.

### 1.5 · The disposition embryo — `_ORPHAN_ROUTES` `[OBS suite.py:7014-7034]`

The anchor calls this an "embryonic disposition system." Confirmed and it's exactly that: a hand-kept dict
tagging each orphan route `to_build_ui` / `to_wire` / `voice_owned` / `backend_only` `[OBS suite.py:7015-7016
docstring + 7017-7034 entries]`. `reachability()` `[OBS suite.py:7080-7088]` splits orphans into
`documented` (tagged → accounted-for backlog), `new_orphans` (untagged → the gate FAILS), and `stale`
(listed but now wired → self-corrects). So the system already (a) detects, (b) dispositions by tag, (c)
distinguishes accounted-for from new, (d) self-heals stale dispositions. The Coherence surface's disposition
UI is the human-facing front of *this* mechanism, generalized off a hardcoded dict into a stored,
addressed, per-finding judgment.

### 1.6 · The CLI pattern — `ops/cli/app.py` `[OBS ops/cli/app.py:120-205]`

The single-console pattern is a flat `if cmd == "..."` chain in `main()`. The `suites` command
`[OBS lines 133-149]` is the closest precedent for `company coherence`: it shells the gate suite under a temp
store and propagates the exit code — "the one place to run it by hand." A `company coherence` subcommand
slots into this chain identically (see §4).

---

## 2 · The three seams — the "but actually" gold (verified, with the fix)

The anchor implies the interface mostly composes from what's there. **Mostly true — but there are three
concrete places it is NOT yet wired.** I verified each; each has a clean fix grounded in an existing pattern.

### SEAM 1 · `up_translate('finding', …)` is not reachable over HTTP as-is `[OBS bridge.py:375; suite.py:5836]`

- **Observed:** the route `/api/up-translate` calls `SUITE.up_translate(q["kind"], q["ref"])` where `q["ref"]`
  is a **query-string value (a string)** `[OBS bridge.py:375]`. But the finding branch requires `ref` to be a
  **dict** (`if not isinstance(ref, dict) … return "abstained"` `[OBS suite.py:5836-5840]`). So a GET
  `/api/up-translate?kind=finding&ref=...` would hit the abstain branch immediately and explain nothing.
- **And it's deliberate, not a bug:** the bridge comment says so verbatim `[OBS bridge.py:371-372]`:
  *"finding/event take a dict the caller holds (the G2/FE-surface lane will POST those) — not on this GET
  read."* **The "G2/FE-surface lane" is THIS Coherence interface.** The seam was left open *for us*.
- **The fix `[IDEA]`, modeled on the existing `decision` kind:** `kind=="decision"` takes a **string**
  `surfaced_id` and resolves the full item server-side via `coa(ref)` `[OBS suite.py:5820]`. Do the
  isomorphic thing for findings: persist findings as addressed records (§3), and let
  `up_translate('finding', <finding_id-or-coherence_address>)` resolve the finding dict server-side from the
  findings store, *then* run the existing dict-based framing. This keeps the GET read-face string-keyed and
  consistent with `decision`, and makes the half-built finding branch reachable. (Net change: a small
  resolver `_resolve_finding(ref) → dict` + one branch tweak. The framing logic at 5841-5855 is untouched.)
  Alternatively a POST `/api/up-translate` accepting a finding body — but the string-keyed resolve is truer
  to the `decision` precedent and to addressing (a finding has an address; resolve from it).

### SEAM 2 · There is no `/api/coherence_info` projection and no `coherence.*` SSE branch `[OBS — grep returned nothing]`

- **Observed:** `grep "coherence" runtime/bridge.py` and `canvas/app/src/useAppController.ts` return **zero
  matches**. The data spine the surface mirrors (a `cognition_info`-style projection + a `cognition.*`-style
  live branch) **does not exist yet for coherence.** This is another area's build (the detector-unification /
  store work — Areas C/D), but **my deliverable is to specify the exact contract the surface consumes**, so
  it's a defined seam, not an assumption.
- **The contract I consume `[IDEA]`, modeled precisely on the cognition spine:**
  - **`GET /api/coherence_info`** — the registry-style projection (sibling of `/api/cognition_info`
    `[OBS bridge.py:305]`). Returns, at minimum:
    ```
    { finding_states: [ {id, label, render:{token}} … ],   // wired·unwired·half-migrated·orphan·stale·by-design·…
                                                            //   (mirrors cognition_info.node_states so the FE
                                                            //    reads tokens from the registry — rule 3)
      finding_kinds:  [ {id, label} … ],                    // unwired-route, half-migration, uncovered-capability…
      dispositions:   [ {id, label} … ],                    // to-finish · defer · by-design
      summary: { total, open, by_state:{…}, by_owner:{…}, by_kind:{…},
                 burn_down: [ {ts, open} … ] },              // the temporal silhouette (§3.3)
      findings: [ { kind, address, state, disposition, owner, since, evidence } … ] }
    ```
    The `finding_states[].render.token` mirroring is load-bearing: CognitionView reads its status tokens FROM
    the projection's `node_states` `[OBS CognitionView.tsx:34-36]` so a backend-registered state paints from
    its registered token with zero FE code. The Coherence surface does the same — a *new kind of integrity
    check declared, not coded* (anchor §9) appears on the surface for free.
  - **The `coherence.*` SSE branch** — modeled on the `cognition.*` fold `[OBS useAppController.ts:573-583,
    337-367]`. Events like `coherence.finding.opened` / `.resolved` / `.dispositioned` / `.burn` fold into a
    live `coherenceModel` ref synchronously off the stream, mirroring `foldCognition`. reflects-never-owns:
    the FE only mirrors; the detectors + store own the truth. The existing `openStream` dispatch
    `[OBS useAppController.ts:542-583]` already does `if (k.startsWith('cognition.'))` — add a sibling
    `if (k.startsWith('coherence.'))`.
- **Why this is the right seam-shape:** it's the *identical* spine to cognition. The anchor §9 open question
  ("are the Coherence model and the cognition model the same kind of thing?") — my answer (§5): **same
  *shape* (live, addressed, reflects-never-owns projection + fold), different *lens*; sibling, not merged.**

### SEAM 4 · The RHM-explains-a-finding organ enriches blast_radius for `ui://` ONLY — but the flagship finding type is `code://` `[OBS suite.py:5847; design/_system/code-edges.json]`

This is the sharpest "but actually" and it hits the headline case the whole project is motivated by.

- **Observed:** `up_translate`'s finding branch gates the "what it touches" enrichment on
  `if isinstance(addr, str) and addr.startswith("ui://")` `[OBS suite.py:5847]` — it calls `blast_radius(addr)`,
  which is a `ui://`-keyed resolver. **But the motivating finding type — an unwired route — is about a
  `code://` element** (the anchor's own example is `code://api/knobs`, anchor §3). So the *primary* finding
  that justifies this entire project (built-but-unwired routes) would get `touches: None` from the existing
  branch — **no "what depends on it" drill, the exact leg §5's explain panel leans on.** "The RHM explains
  any finding faithfully" is, as the code stands, true-only-for-UI-findings. (My §7 below initially
  mis-attributed this thinness to AddressHelp's unregistered STATE-4; the real mechanism is this gate, and it
  bites the headline case.)
- **The fix `[IDEA], and the right source already exists:** for a `code://` finding the "what it touches"
  must come from the **structural code-dependency graph**, not `blast_radius`. That graph is
  `design/_system/code-edges.json` `[OBS — keyed by the SAME `code://<file-stem>/<symbol>` ids, with
  `depends_on[]` (dependencies-to-RESPECT) + `depended_by[]` (dependents-to-VERIFY) + a BOUNDED
  `reach()`/`reach_report()` query capped at DEPTH, design/_system/codeedges.py:303-351]`. So: extend the
  finding branch to dispatch on the address scheme — `ui://` → `blast_radius` (as now); `code://` →
  `codeedges.reach_report(addr)`. Both return a "what this touches/what depends on it" shape the same
  `BlastReach`-style render consumes (the `depended_by[]` is literally the "verify these" set). This is the
  difference between the central promise being honest vs. half-honest, and it reuses an existing graph — no
  new analysis. `[IDEA, grounded in OBS code-edges.json + codeedges.py]`

### SEAM 3 · "by-design / defer" is a DIFFERENT write than "approve a fix" `[OBS suite.py:6668, 9166, 4245]`

- **Observed:** the consent→build wire (§1.4) handles "finish it" cleanly. But "defer with a reason" and
  "it's by-design" are **not builds** — they're *judgments recorded against the finding*. There is no single
  existing call that does "record a disposition." The closest precedents are two distinct write paths:
  - **`resolve_surfaced(sid, choice, reason)` `[OBS suite.py:9166]`** writes an operator *verdict*
    synchronously (the docstring at line 303 calls it a durable consent record). `defer`/`by-design` is
    verdict-shaped: a choice + a reason against an inbox item.
  - **`annotations_at(address)` / the annotation store `[OBS suite.py:4245, 2807-2815]`** attaches durable
    addressed records to a `ui://` locus. A by-design *rationale* (the prose "why this is fine") is
    annotation-shaped — and accumulating by-design annotations is exactly the anchor's "the by-design set
    becomes the documented architecture."
- **A wrinkle the fix must respect: `resolve_surfaced` is INBOX-COUPLED `[OBS suite.py:9166].`** It requires
  the finding to already be a *surfaced inbox item*. That is CORRECT for `finish` (a finish legitimately
  enters the inbox as a consent-gated build-intent — §1.4). But routing `defer`/`by-design` through it too
  would mean either flooding the inbox with every finding-to-disposition, or *pre-surfacing things the
  operator is marking "fine"* — backwards, and it risks the exact cry-wolf failure the anchor §7.2 warns
  about (a model that screams about things that are fine). So the dispositions split:
- **The fix `[IDEA]`:**
  1. **`finish`** → mint a build-intent (`surface_build_intent`) → it enters the inbox → `resolve_surfaced`
     approve → wire dispatches (§1.4). The inbox/consent wire is RESERVED for `finish` alone (the only
     disposition that is an action with consequences).
  2. **`defer` / `by-design`** (the non-build dispositions) → the findings store's OWN disposition write
     — `[IDEA]` `set_disposition(finding_id, disposition, reason)` on the store (the generalization of the
     `_ORPHAN_ROUTES` tag, §1.5) — NOT `resolve_surfaced`. This avoids importing inbox/consent baggage for a
     judgment that has no build consequence.
  3. The disposition *rationale* (the "why", for both defer and by-design) is ALSO written as an
     **annotation at the finding's address**
     (`annotate_locus`/the annotation store), so it (a) accumulates as documentation, (b) is gathered by the
     SAME `_r2_gather` that feeds chat/build context `[OBS suite.py:2775-2815]` — so the next agent that
     touches that address *sees the by-design rationale in its context bundle*. That is the institutional
     memory the anchor §9 wants ("who dispositioned that as by-design and why"), achieved by reusing the
     locus-context gather, not a new query.
- **Does a disposition write violate reflects-never-owns?** **No — and the file must say so explicitly so a
  reader doesn't trip.** reflects-never-owns governs *the surface passively mirroring live state* (the
  CognitionView/AddressHelp read-only character). A disposition is an **operator ACTION through an existing
  write path** — exactly like resolving an inbox item or commenting at an address, both of which are writes
  the operator initiates and the system owns. The surface still doesn't *own* the coherence state; it issues
  an operator-initiated write to the backend, which owns it, which then re-emits `coherence.*` and the surface
  re-reflects. The write goes *through* the backend, never *around* it. `[INF — consistent with how
  AddressHelp's ShapeHow POSTs a presentation-pref then re-fetches, OBS AddressHelp.tsx:221-224]`

---

## 3 · What the findings store must be (so the interface composes, not a parallel universe)

The interface's existence depends on findings being **typed + addressed + persisted** (anchor §3). That store
is Area C/D's build, but the interface dictates the contract. Grounded in what's there:

- **Typed like everything else `[OBS — the registry/typed-record law, anchor §4].`** A finding kind
  (`unwired-route`, `half-migration`, `uncovered-capability`) is a *registered type*, projected in
  `coherence_info.finding_kinds` (§2 SEAM 2), so a new check is *declared* not coded — and the FE renders it
  with no change (the token-from-projection mirroring, §2). This is "more types, not more tools" applied to
  integrity.
- **Addressed `[OBS — every element has a ui://·code://·run:// address, anchor §4].`** A finding anchors to
  the address it's about. **My position on anchor §9's `coherence://` question:** findings should **ride
  existing `code://` / `ui://` addresses, NOT mint a new scheme** — because the whole value is that *the same
  address that names a button names the finding about that button*, so clicking the finding drops to the
  element via the **existing `show`/`resolveUiTarget` keystone** `[OBS — resolveUiTarget preserved through the
  layout refactor, App.tsx:21; surface_output carries a `ui_target` for exactly this drop-to-node behavior,
  suite.py:5889-5895]`. A `coherence://` scheme would *break* that reuse (the click would resolve to nowhere
  the rest of the app understands). A finding may carry its OWN id for the store, but its *navigable* handle
  is the `ui://`/`code://` address it's about. `[IDEA, but grounded in the addressing law]`
- **The finding shape (the contract the surface + RHM consume):**
  ```
  { id, kind, address (ui://|code://), state, disposition, owner, since, evidence, scope?, blast_radius? }
  ```
  Note `scope` + `blast_radius` are exactly what `surface_build_intent` wants (§1.4) and what `up_translate`'s
  finding branch enriches (§1.1) — so the same finding record feeds both EXPLAIN and ACT with no reshaping.

- **The burn-down `[IDEA, anchor §9].`** `summary.burn_down: [{ts, open}]` in the projection is the temporal
  silhouette. This is the introspective-data-building law (anchor §4) pointed at integrity: each detector run
  emits a run-record; the rollup is the burn-down; the burn-down rendered is the "are we converging?" shape
  Tim reads by sight (§4 altitude 0/1). It IS the institutional memory that replaces "the developer who
  remembers."

---

## 4 · The CLI — `company coherence` `[grounded in OBS ops/cli/app.py:120-205]`

Slots into the flat command chain exactly like `suites` `[OBS app.py:133-149]`. `[IDEA]`:

```
company coherence                         # the burn-down at a glance: open / by-state / by-owner, last-run ts
company coherence list [--kind K] [--address A] [--owner O] [--disposition D]
                                          # the queryable model (the anchor §6 first cut)
company coherence show <finding>          # the RHM EXPLAINS it in the terminal — calls up_translate('finding', …)
                                          #   once SEAM 1 is closed (the same organ the surface uses; no dupe)
company coherence finish  <finding>       # mint a build-intent (surface_build_intent) → surfaces for approval
company coherence defer    <finding> "why"# resolve_surfaced verdict + annotation (SEAM 3)
company coherence by-design <finding> "why"
company coherence run                     # re-run the detectors (like `company suites` shells its gate)
```

The CLI and the surface call the SAME backend organs (`up_translate`, `surface_build_intent`,
`resolve_surfaced`, the coherence projection). The CLI is the cheap terminal lens; the surface is the
glanceable spatial lens; **neither owns logic the other duplicates** — both are thin faces over suite.py, the
way `company suites` is a thin face over `suite_health` `[OBS app.py:133-149 shells the gate, no logic dup]`.

---

## 5 · The in-app surface — `CoherenceView`, sibling of `CognitionView` `[IDEA, modeled OBS line-for-line on CognitionView.tsx]`

A new region `canvas/app/src/regions/CoherenceView.tsx`, mounted in `App.tsx` beside `CognitionView`
`[OBS App.tsx:46, 183-184]`, wrapped in a `PanelErrorBoundary name="coherence"`, reading the
`coherence_info` projection + folding the `coherence.*` SSE branch (§2 SEAM 2). Three altitudes, mirroring
CognitionView's idiom — **but I give Tim 2-3 candidate SHAPES per altitude, not one, because the shape is the
creative core and he steers by recognising the right one** (and FORM is `needs-tim` — I do not grade it):

### Altitude 0 — the ambient glyph (default; reads whole-vs-frayed by sight)
The CognitionView analogue is the breathing iris (dilation = depth-of-thought, red notch = a failure)
`[OBS CognitionView.tsx:72-90]`. For *integrity*, candidate shapes:
- **(a) A weave/mesh glyph** — tight and whole when coherence is high; threads visibly fray/gap as
  unwired/half-migrated findings open. "Frayed at the seams" rendered literally. Burn-down = the weave
  re-tightening over time.
- **(b) A vessel/fill** — a containing shape filling toward whole; open findings are visible cracks/leaks;
  by-design findings are *sealed* cracks (acknowledged, not leaking). Burn-down = the fill rising.
- **(c) A constellation density** — the system as a field of points; edges between them glow `--ok` when
  wired, go dark/`--fail` when unwired. Wholeness = how lit the constellation is.
- **Common to all:** shape-not-count (continuous wholeness, never N dots), a LOUD token when a *new* untagged
  orphan appears (the `new_orphans` fail-loud, mirroring the red notch), `--cache`/dim when calm. Click →
  altitude 1. *My lean: (a) the weave — it most directly renders "stays together at the seams," the anchor's
  own metaphor.*

### Altitude 1 — the spatial field (one click; where the system's connectedness is a shape)
The CognitionView analogue is the River (tributaries → brain, width = contribution) `[OBS lines 101-150]`.
For integrity, candidates:
- **(a) A seam-map** — clusters grouped by **owner** (interface-stream / cognition-stream / voice / backend)
  or by **kind**; edges between clusters carry the finding-state token (`wired` solid `--ok`, `unwired`
  dashed/dry like the latent river trace at line 124, `half-migrated` two-tone, `orphan` a stub that doesn't
  reach, mirroring the river's failed-silted-stub at line 118/126). Frayed regions are visible *as regions*.
- **(b) A burn-down terrain** — the temporal silhouette (§3.3) as the dominant form: a ridgeline of open-count
  over time, with the current findings as the live leading edge. Answers "are we converging?" by sight — the
  anchor §5 question made visual.
- **(c) A radial integrity dial** — sectors per owner/kind, each sector's arc-fill = how whole that part is;
  a frayed sector reads instantly. (Closest to a dashboard; least novel — listed for completeness.)
- **Common:** tokens come from `coherence_info.finding_states[].render.token` (registry-driven, §2), so the
  palette is the design system, never bespoke hex (mirrors CognitionView's token discipline, line 34-44).
  *My lean: (a) seam-map as primary + (b) burn-down as a secondary band, because together they answer both
  "where is it frayed" (spatial) and "are we winning" (temporal).*

### Altitude 2 — the finding cards (toggle; literal, clickable, RHM-explained)
The CognitionView analogue is the Nodes (role cards reusing the inspector DOM card pattern) `[OBS lines
156-185]`. For integrity: **one card per finding**, reusing the `.cog-node`/inspector card pattern:
- Each card: `kind · address · state token · disposition · owner · since`. The state dot reads its colour
  from the registered token (line 169, the exact `statusToken` mirroring).
- **Click a card → drop to the element it's about** via the existing `show`/`resolveUiTarget` keystone
  (§3) — and **AddressHelp already explains the landing element** (§1.3). So "click a finding → land on the
  thing → the RHM tells you what it is" is *already wired end-to-end* once findings carry the address.
- **The RHM-explains-the-finding panel** (the new bit, but the organ exists): selecting a card calls
  `up_translate('finding', <finding>)` (once SEAM 1 is closed) and renders the **same altitude IDIOM
  AddressHelp uses** (plain `lead` up top ▸ `mechanism`/`touches` behind a closed-by-default drill-down) —
  but **rendered from the `up_translate` envelope, NOT off `address_help`.** (Note: AddressHelp deliberately
  renders off `address_help` and explicitly avoids the `up_translate` envelope because the envelope flattens
  its *three legs* into one prose `lead` `[OBS AddressHelp.tsx:47-54]`. A finding has no three legs — just
  lead + mechanism(touches) — so the flattened envelope is the right shape here, and the builder should NOT
  expect to literally reuse AddressHelp.tsx's render tree.) The `touches` (blast_radius for `ui://` findings,
  code-edges `reach_report` for `code://` findings — SEAM 4) renders with a **`BlastReach`-style component**
  `[OBS AddressHelp.tsx:234-278]` — the same recognition-by-sight count-chips idiom. Reuse of idiom, fresh
  render tree.
- **The three act buttons** — `finish` / `defer` / `by-design` — wired to §1.4 / §3 SEAM 3. `finish` builds a
  build-intent (consent-gated; the operator sees the scope before approving, line 6678). The recognition-by-
  sight chip idiom from `ShapeHow` `[OBS AddressHelp.tsx:221-224]` is the precedent for these.

### The live behaviour (reflects-never-owns + the loop in front of Tim)
As the autonomous loop (anchor §5) works, `coherence.*` events fold in live `[§2 SEAM 2]`: findings appear
(`coherence.finding.opened`), the weave frays a thread; the loop finishes one, the reviewer gate verifies,
the detector re-runs, `coherence.finding.resolved` arrives, the thread re-knits, the burn-down ticks down —
**all in front of Tim, without him doing anything.** This is the anchor §6 "the place Tim stands to watch a
fully-autonomous build keep itself together." The surface is read-only of the *model*; Tim's only writes are
dispositions (operator actions through existing write paths, §2 SEAM 3) — he steers where judgment is needed.

---

## 6 · The aesthetic / design-system constraints (carried, not graded)

- **Token-only, design-lint-clean.** Every colour/spacing is `var(--x)` from `design/_system/tokens.json`; no
  raw hex/rgba beyond self-contained SVG geometry — the exact discipline CognitionView holds
  `[OBS CognitionView.tsx:24-25]`. The in-repo FORM gate `_design_critic` `[OBS suite.py:7133-7216]` runs the
  corpus design-lint over any changed `.tsx`/`.css` and **GATES a build that introduces an off-token literal**
  — so a CoherenceView that uses bespoke hex literally cannot auto-close. The surface must reuse the shared
  kit (`SectionHead / Badge / Surface / EmptyState`, `[OBS AddressHelp.tsx:70]`).
- **FORM = needs-tim.** The weave/vessel/constellation beauty, the seam-map legibility, the felt shape,
  on-device legibility — I do NOT self-certify these (AGENTS rule 9; CognitionView line 23 marks the same).
  The human design-critic agent (browser + screenshots) `[OBS suite.py:7146-7151]` grades them separately at
  verify time. **This whole §5 is a design companion, not a built thing.**
- **The gold-living-instrument language.** The "commander's-bridge" display voice AddressHelp/CognitionView
  speak `[OBS AddressHelp.tsx:142, CognitionView.tsx:3]` carries to coherence: calm authority, the integrity
  of the *whole* rendered as a living instrument Tim reads, not a defect list he audits.

---

## 7 · Where this is harder / more naive than the anchor admits (honest)

- **The explain is only as good as the finding's content.** `up_translate('finding')` *abstains* on an empty
  finding (line 5836) — good, no confabulation — but that means a finding with a thin `evidence`/`detail`
  field gives the RHM nothing to frame, and Tim sees "can't frame this." The detector (Area C) must emit
  *substantive* finding content for the RHM organ to up-translate well. The interface can't paper over a
  detector that emits a bare flag. `[INF from OBS suite.py:5836-5840]`
- **The drop-to-element only works if the finding's address is REGISTERED as a `ui://` surface.** AddressHelp's
  STATE-4 (well-formed-but-unregistered, `[OBS AddressHelp.tsx:160-167]`) means a finding whose only address is
  a `code://` symbol with no registered `ui://` surface lands on "this isn't registered yet" rather than a
  rich UI explain. The richer remedy is SEAM 4 (explain `code://` findings via the code-edges graph so the
  *explain* is faithful even when there's no UI to drop to) — but the *drop-to-element* step still has nowhere
  visual to land for a pure-backend finding. So findings about backend-only elements get a faithful explain
  (post-SEAM-4) but no spatial drop; the surface should signal that honestly, not pretend a landing exists.
- **Convergence-in-front-of-Tim assumes the loop actually burns down.** My area renders the burn-down; it
  does NOT guarantee it (anchor §7.4 — thrash, findings that spawn findings). The surface should render
  *net burn-down* and a *blocked-on-human* lane (findings whose disposition is "needs a design call") so a
  stall is visible as a stall, not a frozen number. `[IDEA]`
- **SEAM 2 is a real dependency, not a detail.** The surface cannot exist before the `coherence_info`
  projection + `coherence.*` branch exist. My contract (§2) de-risks it, but the build order is: detectors+
  store (Area C/D) → projection+SSE → THEN this surface. Building the surface against a missing projection
  would be a dead region. `[OBS — confirmed absent by grep]`

---

## 8 · The composition, in one diagram (the relationships, Tim-style)

```
                          THE COHERENCE LENS (one more lens, not a new system)

 detectors  ──emit──▶  FINDINGS STORE        ──projection──▶  GET /api/coherence_info   ─┐
 (reachability,        {typed, addressed,                     (sibling of cognition_info) │
  drift, suite,         scope, blast_radius}  ──live events──▶ coherence.* SSE branch    ─┤  reflects-
  + new kinds                                                  (sibling of cognition.*)   │  never-owns
  DECLARED)                                                                               │
                                                                                          ▼
   ┌──────────────────────── company coherence (CLI) ──────────────────┐      CoherenceView.tsx
   │  list · show · finish · defer · by-design · run                    │      (sibling of CognitionView)
   └──────────────┬─────────────────────────────────────┬──────────────┘      alt0 glyph→alt1 field→alt2 cards
                  │  EXPLAIN                              │  ACT                       │
                  ▼                                       ▼                            │ click card
        up_translate('finding', …)            ┌── finish ──▶ surface_build_intent ─────┤ → resolveUiTarget
        [SEAM 1: resolve dict from store,     │             (scope+address+blast)       │   drop-to-element
         like decision resolves via coa]      │             ──approve──▶ resolve_       │ → AddressHelp
                  │                            │             surfaced ──▶ WIRE dispatch  │   explains landing
                  ▼  (REUSES address_help +    │             ──▶ reviewer gate ──▶       │
                  blast_radius — the SAME      │             detector re-runs ──▶        │
                  organ AddressHelp renders)   │             finding RESOLVES (live)     │
                  │                            └── defer/by-design ──▶ resolve_surfaced  │
                  ▼                                   verdict + annotation@address       │
        the SAME altitude move:                       [SEAM 3: two existing writes,      │
        lead (plain) ▸ drill (blast)                   NOT a new mechanism; an operator  │
        rendered with BlastReach                       action, NOT a reflects-never-owns │
        [REUSE AddressHelp.tsx]                         violation]                       │
                                                                                          ▼
                                                              Tim watches the loop keep the system whole,
                                                              steers only the dispositions (judgment).
```

**Every box is an existing organ or a named seam with a grounded fix. No parallel store, no parallel
explainer, no parallel consent gate, no parallel render law.** The Coherence interface is one more lens over
the same substrate — which is the only way it doesn't rot (anchor §7.3).

---

## 9 · The one position to bring to Tim (anchor §9's open question, answered)

**Coherence surface = SIBLING of CognitionView, reusing the altitude+fold+projection+token machinery — NOT a
forced single substrate with cognition.** They are the *same kind of thing* (live, addressed,
reflects-never-owns projection + fold), so they share *machinery* (the fold pattern, the token-from-projection
rule, the altitude idiom, the design kit). But they are *different lenses* ("how it thinks" vs "how whole it
is") and should be *different regions* — because forcing one substrate would couple two independently-evolving
models and muddy both surfaces. **Default: sibling.** `[IDEA, but the sibling pattern is exactly how
CognitionView relates to the other regions — OBS App.tsx:46]`

The shared-abstraction option (one "LiveModelView" generic both specialize) is a *your-idea* to weigh, not a
default — it's the kind of premature unification that's easy to regret; better to build the sibling, see what
the two surfaces actually share by use, and extract the abstraction *then* if it's real. I'd put that as a
B-option for Tim, with sibling as the recommendation.

---

## 10 · Next-step options for Tim

- **Option A (depth):** Trace the full click→explain→act path end-to-end on ONE real finding (take a current
  `reachability()` orphan like `/api/knobs`, walk it through: finding record → `up_translate('finding')` with
  SEAM 1's fix → the AddressHelp-style render → `finish` → `surface_build_intent` → approve → wire). This
  proves the composition by walking a real value through it, and would surface any further seam I've inferred
  but not executed. (My finding branch + bridge claims are `[OBS]`; the *end-to-end flow* is `[INF]` — A
  verifies it.)
- **Option B (dealer's choice):** Pin down the `coherence_info` + `coherence.*` contract (SEAM 2) jointly with
  the Area C/D detector/store findings, so the projection shape is agreed across the streams before anyone
  builds — the cross-stream coordination the `MERGE-COORDINATION.md` channel exists for.
- **Option C (artifact):** I draft the `CoherenceView.tsx` region as a *non-functional shell* against a mocked
  projection — the three altitudes, the card→explain→act layout, token-only — so Tim can SEE the surface shape
  (especially the §5 altitude-0/1 candidates) and pick the weave/vessel/seam-map he recognises, before the
  real projection exists. The shell is the steering artifact; FORM stays needs-tim. *(My lean: C — Tim steers
  by seeing the shape, and the altitude-0/1 choice is exactly the kind of recognition-by-sight call he makes
  best against a rendered thing, not prose.)*
- **Option D:** I write the `company coherence` CLI face first (§4) against the contract — it's the cheapest
  real face, slots into the existing chain, and gives a working lens the moment the projection lands, with
  zero FORM risk.
```
