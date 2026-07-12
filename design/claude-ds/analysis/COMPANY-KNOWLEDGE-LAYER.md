# COMPANY KNOWLEDGE LAYER — INVENTORY (read 2026-07-13; for the claude-ds replacement)

Scope note up front: this repo has **two distinct "knowledge/help" systems** that must not be conflated:
1. **The fabric knowledge layer** (`guides/`, `door/`, `message_types/`) — agent-facing (Claude Code sessions on the company fabric), delivered via the SessionStart hook / door card. Prose is Python-declared, resolved by address (`guide://<id>`).
2. **The operator-facing element-help layer** (`address_help` / `howto` field / page-face system) — for the human operator using the `surface/app` frontend that claude-ds will replace. Distinct mechanism, distinct address space (`ui://`), served over the bridge (`runtime/bridge.py`) at :8770 and a separate no-script page origin at :8774.

Both are cited below with file:line.

## Guides (guide://<id>)

All discovered by `runtime/guides.py:GuideRegistry` (file-discovered `guides/*.py`, each declaring a module-level `GUIDE` dict), resolved via `runtime/cognition.py:resolve_address`'s `guide://` dispatch branch (`guides/AGENTS.md:49-52`). Schema: `{id, content, target, grounded_from, source_hash?, label?, description?}` (`guides/AGENTS.md:23-31`). Audience for all of these is **AI agent sessions on the company fabric**, not the human operator.

| guide://<id> | title (label) | one-line content summary | audience |
|---|---|---|---|
| `using_skills` | Using skills | Seed guide: what a skill is, how to add one (`skills/<id>.py` → `SKILL` dict), worked example `skill://summarize`. `/home/tim/company/guides/using_skills.py:20-65` | agent (skill authors) |
| `the_door` | The door — cards at mechanical moments | How join/create cards compose from registries; how to add a `door/<id>.py` row (moment/scope/audience/until). `/home/tim/company/guides/the_door.py:4-38` | agent |
| `adding_message_verbs` | Adding a message verb | How to add a typed-message kind (`message_types/<id>.py` → `MESSAGE_TYPE` dict) with an obligation. `/home/tim/company/guides/adding_message_verbs.py:4-33` | agent |
| `channel_collaboration` | Collaborating on the board (the handbook) | THE HANDBOOK — membership, @mentions, typed messages + obligations, replies, dependencies, etiquette (D0). Target `board://item-4696f705`, the live tracker. `/home/tim/company/guides/channel_collaboration.py:7-50` | agent |
| `process_a_corpus` | Process a corpus — start here | Agent-authored entry point for turning a whole body of material into embedded/addressed/queryable Company knowledge; points to `skill://full_coverage_dragnet` + related skills. `/home/tim/company/guides/process_a_corpus.py:5-18` | agent |
| `using_corpus_pipeline` | Using the corpus pipeline | Agent-authored how-to for the 3-layer corpus pipeline (capture → embed → reduce/cluster). `/home/tim/company/guides/using_corpus_pipeline.py:5-17` | agent |
| `using_patterned_visibility` | Using patterned visibility | Agent-authored how-to for the run→look→mark→next-step discovery loop (`find_relations` inversion queries). `/home/tim/company/guides/using_patterned_visibility.py:6-16` | agent |

The registry's own drift-home note (`guides/AGENTS.md:81-87`) lists `process_a_corpus`, `using_patterned_visibility`, `using_corpus_pipeline` as "agent-authored entries (auto-reflected)" — consistent with what's on disk. `the_door`, `adding_message_verbs`, `channel_collaboration` are NOT yet reflected in that same drift-home list block (they postdate the last edit to that file), though they exist as real, loadable guide files. Flagging as an accuracy gap in `guides/AGENTS.md` itself, not a claude-ds concern.

Guides self-register on drop-in; `guide://<id>` for an unknown id raises fail-loud (never fabricated) — `guides/AGENTS.md:51-52,66`.

## The door/card system

**Mechanism** (`runtime/door.py:1-179`): every company session gets a CARD at a mechanical moment — never hardcoded prose, always composed LIVE from registries at injection time (`runtime/door.py:3-6`). Two halves:
1. **`door/<id>.py` rows** — what's on the card. Row schema `{id, line (required), depth (required, an address), order (optional int), moment, scope, audience, until}` (`runtime/door.py:12-16,35-37`). `id` must equal filename.
2. **`compose_card(reg, *, moment, channel, project, ...)`** — folds: the member's identity from registration, the verb table folded live from `message_types/`, and the door rows filtered by moment × scope × audience × until (`runtime/door.py:119-179`).

**Moments** (`runtime/door.py:37`): `register` (SessionStart, automatic), `channel-join`, `channel-create`, `project-join`, `project-create`, or `all`.

**Row-applies gating** (`runtime/door.py:77-101`):
- `moment` gate — row shows only at its declared moment, or always if `moment: all`.
- `scope` gate — `global` (default, every card) | `channel:<name>` | `project:<id>` (shows only when that channel/project is being entered).
- `audience` gate — optional comma-list matched against the member's `name`/`handle` (case-insensitive); omitted = everyone.
- `until` gate — ISO date/datetime; an expired row silently leaves the card (no stale standing orders); rows without `until` are standing.

**Every door row on disk** (`/home/tim/company/door/`, sorted by `order` then `id`):

| id | order | moment | line | depth (target) |
|---|---|---|---|---|
| `handbook` | 10 | all | How we collaborate on the board (mentions, verbs, obligations, etiquette) | `guide://channel_collaboration` — `/home/tim/company/door/handbook.py:2-7` |
| `adding_verbs` | 20 | register (default) | Add a new message verb (a typed kind with an obligation) — a row, zero code | `guide://adding_message_verbs` — `/home/tim/company/door/adding_verbs.py:2-6` |
| `active_tracker` | 30 | register (default) | The live build tracker + the D0 protocol block (per-item commentable) | `board://item-4696f705` — `/home/tim/company/door/active_tracker.py:2-6` |
| `constitution` | 40 | register (default) | The repo constitution — the rules for working in ~/company | `file://AGENTS.md` — `/home/tim/company/door/constitution.py:2-6` |
| `ctx_substrate` | 40 | all | The conversation SUBSTRATE: talk is stored as typed, addressed, state-bearing units | `company ctx open` (a CLI hint, not an address) — `/home/tim/company/door/ctx_substrate.py:5-12` |
| `the_door` | 90 | all (default: register) | THIS CARD is a resolved registry — give YOUR capability a line on it | `guide://the_door` — `/home/tim/company/door/the_door.py:1-8` |

Note: `constitution` (order 40, default moment `register`) and `ctx_substrate` (order 40, `moment: all`) share the same order value — sort is stable by id as tiebreaker (`runtime/door.py:74`).

**Delivery mechanics**: `ops/hooks/auto_register.py` is the SessionStart hook — auto-registers the session as a fabric member (idempotent per claude-ancestor PID) and injects `compose_card(reg)` into the session's starting context (`/home/tim/company/ops/hooks/auto_register.py:1-27`). Fail-soft always (exit 0 silent on error) — a hook must never break a session.

**The 2026-07-13 room-state extension** (`runtime/door.py:130-134,159-177`): `compose_card` optionally accepts `room` — live state of the room being entered (purpose, member/post counts, open board items, recent messages) — supplied by the caller (session_channels), not fetched by the door itself. Renders a "THE ROOM" section when present. Every key optional; only present keys render.

**Verb table folding** (`runtime/door.py:104-116`): `verb_table()` reads the LIVE `message_types/` registry and groups verb ids by obligation in a fixed presentation order (reply, verdict, ack, none, then any others sorted) — e.g. `mention/ask→reply · review_request→verdict · handoff→ack · fyi→none`.

Proven by `tests/door_card_acceptance.py` (temp-registry-dir tests: live verb add/remove reflected on next card, live door-row add reflected, malformed rows fail loud, real-repo compose) — `/home/tim/company/tests/door_card_acceptance.py:1-40+`.

## Typed message verbs (message_types/<id>.py → MESSAGE_TYPE dict)

Discovered file-by-file (mirrors the guide/door mechanism); schema `{id, obligation, label, desc}`; `id` must equal filename.

| verb | obligation | where enforced | description |
|---|---|---|---|
| `mention` | reply | `runtime/cc_board.py` obligation tracking + `ops/hooks/pending_mentions_nag.py` (the nag hook re-surfaces unmet obligations every turn until a reply lands on the board) | You were named (@handle/@name) in a comment; default kind for any comment carrying mentions. `/home/tim/company/message_types/mention.py:1-8` |
| `ask` | reply | same board/nag mechanism | A direct question to the addressed member(s); questions block nothing but must be answered (D0 etiquette). `/home/tim/company/message_types/ask.py:1-8` |
| `review_request` | verdict | same, plus: an unresolved objection blocks the item's claim for build | Asks the addressed member to review the target item; obligation is an explicit verdict (approve/object/needs-work + why). `/home/tim/company/message_types/review_request.py:1-9` |
| `handoff` | ack | same board/nag mechanism | Passes ownership of the target item; obligation is an acknowledgement reply. `/home/tim/company/message_types/handoff.py:1-8` |
| `fyi` | none | none (delivered — push + visible on board — but never nagged) | Informational only; nothing owed. `/home/tim/company/message_types/fyi.py:1-8` |

Adding a new verb = drop `message_types/<id>.py`; no code change (`guides/adding_message_verbs.py:16-26`). If a needed obligation semantic doesn't exist (beyond reply/verdict/ack/none), that requires an actual `runtime/message_types.py` `OBLIGATIONS` extension + a matching close-condition in `cc_board.pending_obligations` — flagged as a real code change, not a registry row.

## Operator-facing pages/surfaces beyond surface/app

This is the layer claude-ds is actually replacing the PRESENTATION of. Distinct from the fabric knowledge layer above.

- **`/api/address-help`** (`runtime/bridge.py:1911-1920`) — "the COMPOSED affordance bundle for one `ui://` address." Joins three legs via `Suite.address_help` (`runtime/suite.py:3677-3762`):
  - `what_this_is` — registry row's human title / `represents` feature-id (never invented).
  - `how_to_change` — `code://` scope + blast radius (co-reference / structural dependents+dependencies / semantic neighbours) a change here would reach.
  - `how_to_use` — the authored affordance/how-to text, read from `UI_REGISTRY` row extras' `howto` field (`Suite._registry_howto_for`, `runtime/suite.py:4072-4093`). Returns `None` when unauthored.
  - `legs_present` flags which legs actually resolved, so the FE can degrade cleanly (`runtime/bridge.py:1913-1916` calls out "G-53: many elements author no howto yet" — **confirmed by grep: no live UI_REGISTRY row in this repo currently carries actual howto prose; the mechanism exists, the content is largely unauthored today**).
  - The howto leg is also folded into the RHM's live context as a pin-persistent "how-to/affordance" stratum (`Suite._r2_howto_at`, `runtime/suite.py:4095-4127`) — it never decays out of the operator-conversation window the way a comment/event would.

- **`/api/guide/start`** (`runtime/bridge.py:3314-3322`) — the SYSTEM-INITIATED "show me how" tour. Composes the SAME walkthrough organ over `ui://` element addresses (not inbox review items): sets the presence dial to `walkthrough` and starts a session whose steps each narrate the element's `address_help` how-to text + spotlight the real element. Model-free by construction (reads the corpus, never calls a model). Optional `topic` picks a sequence; absent → default orientation tour. No registered addresses → `{organ_started:False, reason}` (fail-loud, never a silent no-op).

- **`/api/walkthrough/start`** (`runtime/bridge.py:3304-3313`) — binds the cosmetic `walkthrough` presence-dial mode to the real walkthrough ORGAN, walking pending inbox items (or a given `item_ids` set).

- **`/api/review/start`**, **`/api/debrief/start`** (`runtime/bridge.py:3300-3303, 3323-3334`) — related organ-driven sessions (review-session mode selection; replay of recorded voice-trial sessions through the same walkthrough organ).

- **`/api/pages`** + the page-face system (`runtime/bridge.py:1895-1900`, `runtime/page_face.py:1-80+`) — "page-as-a-face": any address can carry a bound, rendered HTML page (`UnionAddressRecord.page`), served on a **separate origin** (`127.0.0.1:8774`, never the bridge control plane at 8770) under a no-script CSP (no `script-src`, `connect-src 'none'`) and a content-addressed-only scheme allow-list (`cas://`/`blob://`; a `run://`/`skill://` source is refused). `/api/pages` on the control plane returns only the LIST (`{address, url, title, source}` per page); the pages themselves never serve from the control plane (hard security separation, per the 3-review verdict cited in the module docstring).

- **`/api/territory`** + **`/api/territory/label`** (`runtime/bridge.py:1921-1939`) — the "Source" verb backing: resolves ANY address (run://, code://, corpus, board://, ui://, …) to a structured record (`identity`, `corpus_content`, `relations`, `notes`, `legs_present`) for operator drill-down past a 140-char summary; `territory_label` composes a human one-liner and is under an explicit operator-law: **never return the raw address** to the operator, always a human label (`ui-context-unregistered → "this part of the surface"`, etc.).

- **`ui://chrome/workshop`** — named in `STATE.md:43` as the operator-facing self-change surface (renders the 3-stream audit ledger: self-apply / self-build / checkpoint) — flagged there as having FORM follow-up work outstanding (render the `stream` tag per-entry + add the checkpoint-mint control), i.e. this is a real existing operator page, not yet fully built out.

- **`surface/app`** (the frontend claude-ds replaces) has source directories for: `board`, `tools`, `source`, `tokens`, `decisions`, `channels`, `toggles`, `gallery`, `lib`, `wheel`, `transcript`, `sessions`, `rhm` (RightHand.tsx — the RHM chat surface), `layouts`, `nav` (`/home/tim/company/surface/app/src/*`). No literal "workshop"/"handbook"/"guide" named component found under `surface/app/src` by name-grep — the workshop/handbook surfaces referenced in STATE.md/AGENTS.md may live under a different component name or be pending FE build (STATE.md explicitly calls the workshop stream leg-status "FORM follow-up, out of this runtime-scoped change").

- **`AGENTS.md` rule 9** (`/home/tim/company/AGENTS.md:30`) states the PRODUCT BAR that governs ALL of the above: every operator-facing surface must be built on the design system (no hardcoded values/bespoke one-offs), coherent in scale/type/spacing/layout, responsive, settings consolidated, and a navigable visual/spatial surface "not a text-wall or list" — reviewed by a separate design-critic and, where machine-checkable, gated by a design-lint. This is the standard a claude-ds rebuild of any of the above must meet, per the repo's own constitution.

- **`HANDOFF.md`** (repo root) is called out in `AGENTS.md:14` as carrying "the most recent session's narrative + an operator how-to for the live surface (voice circuit, the `company` console, the phone path)" — a text doc, not a served page; read separately if picking up live/voice/ops work.

## What a replacement UI must SURFACE (the content contract — checklist)

- [ ] The **door card** content at each mechanical moment (register / channel-join / channel-create / project-join / project-create): member identity, the live verb table, and the depth-address lines (handbook, adding-verbs, active-tracker, constitution, ctx-substrate, the-door-itself) — this is currently agent-facing (injected into a Claude Code session's context), not an operator UI surface today; confirm with Tim whether claude-ds should give the OPERATOR an equivalent visible view of "what's on the card right now."
- [ ] The **guide://** narrative content (7 guides) as browsable/readable prose, if any operator-facing UI is meant to expose the agent-knowledge layer at all (currently it is agent-only, resolved by address inside sessions).
- [ ] The **verb/obligation table** (mention, ask, review_request, handoff, fyi) and which obligations are currently unmet/pending — this already exists as fabric-internal nag-hook state; an operator view of it doesn't yet exist by name in `surface/app/src`.
- [ ] The **`/api/address-help`** three-leg bundle (what-this-is / how-to-change / how-to-use) per `ui://` element — the FE consumer for this is referred to as "the D2 surface" in code comments; verify it exists and where.
- [ ] The **guided "show me how" tour** (`/api/guide/start`) and the **walkthrough organ** (`/api/walkthrough/start`) — narrated per-step element spotlighting; needs an FE driver ("the FE show-me lane" per the code comment) to display each step.
- [ ] The **page-face viewer** for any address with a bound page (`/api/pages` list → open at the separate :8774 origin) — must remain on its own origin; a replacement UI must NOT merge page rendering into the control-plane origin.
- [ ] The **territory / "Source" drill-down** (`/api/territory`, `/api/territory/label`) — must render only the human label, never the raw address, per the explicit operator-law in the code.
- [ ] The **workshop / self-change audit ledger** (`ui://chrome/workshop`) — 3-stream history (self-apply/self-build/checkpoint) + the checkpoint-mint control — explicitly flagged in STATE.md as FORM-incomplete today.
- [ ] Compliance with the **AGENTS.md rule 9 product bar** for every one of the above: design-system-only, coherent, responsive, consolidated settings, spatial/visual navigation (not a text-wall), design-critic + design-lint gated.

## Unreadable / not found
- No `AGENTS.md`/constitution file exists under `door/` or `message_types/` themselves (only under `guides/`) — their "constitution" is effectively the docstrings in `runtime/door.py` and the guide `the_door`/`adding_message_verbs` content; noted as a gap, not fabricated as existing.
- Could not confirm any current UI_REGISTRY row with populated `howto` text via grep (searched for literal `'howto'` value assignments in `runtime/*.py`) — treating "the how-to-use leg is largely unauthored today" as directly evidenced rather than assumed, per the bridge.py G-53 comment.
- Did not exhaustively enumerate every route in the ~3000-line `runtime/bridge.py`; the routes cited above were located by targeted grep for guide/door/howto/help/pages/territory/workshop keywords. A full route inventory was out of scope for this pass — flag if needed.
