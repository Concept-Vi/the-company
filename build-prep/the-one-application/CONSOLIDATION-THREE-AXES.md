> ⚠ **DISCREDITED / PROVISIONAL (2026-06-26).** Written BEFORE Tim's foundational transmission. It reached retain/replace conclusions at Stage-0 (forbidden by the Sequence law), trusted prior union docs (No-assumed-completeness law), and ran on partial coverage (No-partial law). The frontend census was excerpt-level/unverified; "DS1 / which look" was a wrong framing (the look is token/registry/invariant-driven, composed+resolved — not a choice). **Treat as raw input only, not conclusions.** Superseded by the effort in channel `the-one-system` (`channel://ch-9`), anchor `board://item-70d15132`. Will be revised/replaced once the total-coverage ledger-graph exists.

# CONSOLIDATION — The Three Axes (channels · stores · frontends → one system)

> **Living doc. Status: OPEN / growing.**
> **Opened:** 2026-06-26 by a Claude Code session, on Tim's direct steer.
> **Maintained-by-integration** (build-prep is staging — *outside* the `drift_acceptance` net, so there is no auto-drift-check; a future session keeps this true by editing it, mirroring `THE-ONE-SYSTEM.md`'s living convention).
> **This doc is the anchor for the frontend-merge axis + the registry of genuinely-NEW findings. It does not restate what UNION-MAP / the storage challenge / the divergence ledger already hold — it links to them.**

---

## 0. TIM'S DIRECTION (verbatim-in-meaning, 2026-06-26)

> *Merge and unify and consolidate the channel systems, the stores, the interfaces — all into one system. It will be a Supabase backend (a local docker container running Supabase). The frontends: there are a bunch of them, each with distinct unique qualities, but none of them are 'right' or 'complete', so they all need to **merge into one — not one or the other, but a merge and consolidation**. Each has unique qualities to **retain** and unique qualities to **replace** — that's part of the need and the challenge. Write these findings somewhere maintained so they don't stale, then do the deeper and broader passes.*

Decompressed into the three axes, each mapped to where it already lives:

| Axis | What "one system" means | Where it's already worked | Remaining work |
|---|---|---|---|
| **Channels** | One channel identity model + one store + one mail log | `UNION-MAP.md` §5 Cluster C; divergence ledger **ID2** (the crux decision) | **Consolidation design**, not discovery (the two systems are fully mapped) |
| **Stores** | One addressed store + embeddings, queryable together | `CHALLENGE-storage-supabase.md` (GO-with-shape verdict); `UNION-MAP.md` §3 | **Seam-widening design** (Protocol 10→61) + reconcile the two Supabase threads (§3 below) |
| **Frontends** | A *merge* of the several FE surfaces into one — retain/replace per app | `INTERFACE_INVENTORY` / `INTERFACE_EXCAVATION` (front-interface/) — **but stale (pre-`surface/app`)** + cross-repo, never censused as one | **THE GAP — the deeper/broader pass (§4). This doc's primary job.** |

**Convergence with prior work:** Tim's "local Supabase docker" is *exactly* the local-first Postgres+pgvector union store the storage challenge recommended (it deferred *cloud* Supabase; a local docker container is not cloud). The verdict's load-bearing constraints stand unless Tim overrides them: **registries stay in Git** (the type vocabulary doesn't move to SQL); **widen the Resolver seam first** (10→61 methods); **absorb the two bypass namespaces** (`cascades.json`, `agent_sessions/channels.jsonl`) before any migration.

---

## 1. NEW FINDING — three comment/annotation stores that do not compose

*(Verified by direct grep this session, not sub-agent report. Added to `UNION-MAP.md` §5 Cluster C as a canonical divergence; full trace here.)*

The same human act — *leave a comment / mark / note* — lands in **three disconnected stores keyed by three address vocabularies**, depending only on which surface the operator happens to be on:

| Store | Leaf | Address key | Written by | Read by |
|---|---|---|---|---|
| **Board comment** | `channel-memory/noticeboard/<id>.md` | `board://` | MCP `cc_board` tool · CLI (`ops/cli/board.py`) · decision registry · image tools · `ops/doc_review_server.py` · `cc_retire` | `doc_review_server`, board traverse, surface `/api/board` (read-only) |
| **Canvas annotation** | `annotations.jsonl` | `ui://` | canvas `/api/annotate` → `Suite.ingest_comment` | the twin's **gold-training** pipe |
| **Surface mark** | marks store | `decision://` | surface `/api/territory/write` → `Suite.mark` | decision-state resolver, surface cards |

- Neither product front-end (`canvas/app`, `surface/app`) writes to the board's own comment primitive — which is polymorphic and *already accepts any address scheme* (`cc_board.comment(addr,…)` at `runtime/cc_board.py:467`; threaded via `commented_on`/`reply_to` edges).
- The board comment system is reachable only by **agents, the CLI, and the standalone `doc_review_server` PWA** — not from the surfaces a person actually operates.
- **The drift is not in the spine** (the comment primitive is correct and reusable); it is that the two front-ends were wired to *side stores* instead of the spine. **Fix = convergence onto `cc_board.comment`**, not new machinery — and it folds directly into the store-union (all three become rows in the one store).
- Relation to existing clusters: distinct from UNION-MAP's "two mail logs" and "two recall indexes" — this is a *third* parallel-system instance on the comment/annotation noun.

**Full code-traced circuit map (the read that produced this):** session artifact `claude.ai/code/artifact/b1448855-05e0-4554-9b1d-5b7369b138c0` (chat ↔ board ↔ comment/block ↔ channel circuits, with `file:line` seams). Honesty caveat on that pass: **read-and-traced, not verified-by-running** — the SessionStart hook reports the registry binary has never been built for this checkout, so "verify by use" was not possible.

---

## 2. CHANNELS — what's settled, and the one open crux

Fully mapped (do NOT re-discover — re-sweeping reproduces the ledger's RCN7 "re-derived a completed deliverable" divergence):
- **Two systems, zero cross-imports (verified):** `cc_channels.py` = live session-to-session transport (member-id = bare **handle**, store `.data/channels/`), `session_channels.py` = durable fabric structure (member-id = session **uuid**, `channel://`, store `agent_sessions/`). They meet only at orchestration edges (`channel_boundary_run` → `cc_channels.push`; `bridge` → `session_channels`).
- **`channel://` is used but NOT in `SCHEMES`** (address-grammar gap, UNION-MAP §1A).
- **Two mail logs** (`.data/channels/_mail.jsonl` vs `agent_sessions/mail.jsonl`) — no unified inbox.

**The crux (divergence ledger §A ID2 — a genuine Tim decision):** *when a session ends, which face is the durable channel member — the person, or the session?* The two id models (handle vs uuid) cannot join until this is answered. This is the hinge the channel-union turns on. → teed up for Tim in §5.

**Remaining work = consolidation design:** one member-identity model → one channel store (a `channels`/`channel_members`/`channel_posts` table set in the Supabase union, cf. `build-prep/claude-design/supabase/.../0003_channels.sql`) → one mail log. Gated on ID2.

---

## 3. STORES — what's settled, and the TWO Supabase threads to reconcile

Settled (storage challenge verdict, GO-with-shape):
- **One local Postgres+pgvector store** holds the addressed graph + embeddings (the union = the structural+semantic JOIN runs as one SQL statement — that query *is* the acceptance test).
- **Registries stay in Git** (code-as-data `.py` rows; `_CORPUS_REGISTRIES` becomes an enumerable index, not a relocation).
- **The seam is the first deliverable:** Resolver Protocol **10 methods** vs **~61 actually called** on FsStore; re-type `Suite.store: FsStore → Resolver`; absorb the 2 bypass namespaces. A backend implementing only the Protocol is ~16% complete on day one.
- Vectors: trivial table (`(space,emb)` filter + exact cosine scan at ~9k vectors; no ANN index yet). Realtime (`postgres_changes`) maps directly onto `events_since(seq)` — turns poll into push.

**⚠ RECONCILE — there appear to be TWO distinct Supabase designs; do not collapse them:**
1. **The union store** (this challenge) — local PG+pgvector, the internal addressed-graph substrate, registries-stay-in-Git, RLS "premature."
2. **A client-exposure / auth posture** — `build-prep/claude-design/supabase/.../` migrations: `0002_clients`, `0005/0006_*_rls`, `0007_custom_access_token_hook`, `0010_native_client_id_rls`, `0003_channels`, plus `REMOTE-MCP-EXPOSURE-DESIGN.md` / `PROD-FLIP-RUNBOOK.md`. This is about **external clients + RLS + auth** (the Claude Design inlet / remote-MCP exposure), a *different concern*.

Open question for the build: is the "one Supabase backend" Tim names the *union store*, the *client-exposure layer*, or both fused? They share Postgres but have opposite postures (internal-single-operator vs external-multi-client-RLS). **→ reconcile, don't assume.** (Flagged for the deeper pass + possibly Tim.)

---

## 4. FRONTENDS — THE GAP (the deeper/broader pass) ★ this doc's primary job

Tim's framing: *several FE surfaces, each with unique qualities to **retain** and unique qualities to **replace**; merge into ONE — not pick-a-winner.* This has **never been censused as one cross-repo picture**, and the existing inventory is stale.

### 4.1 The known frontends (to be verified + deepened by the pass)

**In-repo (`~/company`):**
- **`canvas/app`** — tldraw node-composition surface; per `INTERFACE_INVENTORY` this is *also* called the live operable surface with ~24 regions (Activity, RhmChat, Inbox, Inspector, Workshop, Walkthrough, …). ⚠ The inventory conflates `canvas/app` and `surface/app` — current repo has BOTH as separate apps. **Drift to resolve in the pass.**
- **`surface/app`** — projection/wheel viewer (the Instrument): BoardView, SessionDrill, ChannelView, DecisionsInbox, RightHand(V), form-factor layouts. Reads `/api/board`, writes marks.
- **`ops/doc_review_server.py`** — standalone mobile PWA; the ONLY board-comment writer among the surfaces.
- **`design/blueprint` (J1–J9) + `design/mockups`** — ~40 designed views, ~20 rendered HTML mockups; mostly `planned`, a few `quality-passed`. OPEN input, not binding.

**Cross-repo (`/mnt/c/Users/Workstation001/Documents/Claude/Projects/`):**
- **`counterpart/design`** — the **DNA gallery** (52 pieces: design-language + frozen `Application·*` demos) + the **DNA renderer/look** (`design/ui`: unit-view, organisms, phone.css, `:root` tokens, the V-expand 90° wheel, the self-teaching explainer). The single source of truth for the LOOK; copied into `surface/app` via `sync-gallery.mjs`.
- **`counterpart/concept-factory` + the visual-designer repos** (`Visual Designer` / `Visual-Designer` / `vi-context-design` / `visual-design-corpus` / `Visual DNA` / `ConceptV Design System`) — the **factory / asset / composition layer** (the V asset + recolor variants, the socket registry "socket→function as DATA", `drawer-layouts.js` the generic data-driven layout engine).
- **`Relative difference`** — Tim-authored **design ground** (the WHY/shape: UI = generated projection over substrate; click→talk→generate→addressed-registry).

**Conceptions described but NOT built (excavation):**
- **The Session-Fabric "graph-of-minds" Face** — the company as a graph of MINDS/sessions (timelines + accumulating edges + drill-in terminals + CLI-surfaced-natively + selection-becomes-channel). A genuinely distinct conception vs the projection-wheel. Open: folds in (sessions-as-units projection) or separate mode?
- **The wildcard MODES** — slide (built, the one Tim uses) / graph / document (sections-as-sub-address-channels) / team.

### 4.2 What the pass must produce (retain/replace ledger)

For **each** frontend: `{name, repo+path, live|designed|idea, what it IS, the UNIQUE quality to RETAIN, the quality to REPLACE/shed, how it OVERLAPS the others, the host/bridge seam it connects through}`. Then: the **merge proposal** — one surface that inherits the retain-set and sheds the replace-set, on one design system (DNA tokens), one host seam, one address spine.

Anchored by the existing seams: `sync-gallery.mjs`/`GalleryMount` (the host seam DNA→surface), `/api/projection` (the instrument engine, served to both canvas + MCP), the `projection:select`/`vee:socket` events, the DNA `:root` token tree.

### 4.3 PASS-2 WRITEBACK — cross-repo frontend census (filled 2026-06-26)

*Four parallel Explore lanes, file-grounded. Corrections to §4.1 in bold.*

> **PROVENANCE / TRUST:** this census was gathered via **Explore agents (excerpt-level — they locate, they don't audit)**. Treat the structural shape as reliable; treat **specific counts, absolutes, and aesthetic characterizations as UNVERIFIED** until a build pass confirms them by reading the files whole. Two claims have already been corrected on direct re-read: the `canvas/app ≠ surface/app` split (confirmed) and the DNA "dark/Catppuccin" token read (likely stale — see DS1). The `sync-gallery.mjs`/`GalleryMount` seam is a **build-time copy of DNA's render FACE module into `surface/app`** — NOT live runtime token-injection into the running apps (those are separate; runtime token wiring is unbuilt).

**★ CORRECTION: `canvas/app` ≠ `surface/app`. They are TWO separate, co-existing React+Vite apps** (the 2026-06-17 inventory's conflation is wrong, verified by `index.html` titles + separate `package.json`/`vite.config.ts`):
- **`canvas/app`** (`:5173`, title *"the company · canvas"*) — the **operable composition workspace** (tldraw infinite canvas).
- **`surface/app`** (`:5174`, title *"Instrument"*) — the **projection/wheel analytics viewer**.

**The retain/replace ledger:**

| Surface | Repo · path | State | RETAIN (only-it-does-this) | REPLACE / shed |
|---|---|---|---|---|
| **canvas/app** | `~/company/canvas/app` | live `:5173` | tldraw infinite canvas + **drag-to-wire edges**; **voice push-to-talk** (RhmChat+voiceStream); **self-build wire door** (intentAt/approveReach/blast-radius ripple); the ~26-region cockpit chrome | 27 monolithic region files (~400KB); fixed-px brittleness (<699px breakpoints); NodeShape tightly coupled to tldraw Editor |
| **surface/app** | `~/company/surface/app` | live `:5174` | **projection algebra** (relative-centre re-projection, two-gravity poles); **time scrubber** (`at=`); **meaning-zoom + layer/quant pickers**; **gallery drill-in FACE** (GalleryMount+`sync-gallery.mjs`); **3 discrete form-factors**; RightHand "V" | 18KB `GalleryMount` monolith; 44KB `RightHand` monolith; zero composition/wire ability |
| **doc_review_server** | `~/company/ops/doc_review_server.py` | standalone `:8781` (Python) | **the ONLY board-comment writer among surfaces**; rich-media threaded commenting; native-mobile PWA; **fabric-chat integrated** (registers `tim`, routes replies) | bespoke copper SVG iconography (off-DNA); embedded md→html; thread-local SSE. *Not a surface to fold in — but its board-write capability is exactly what §1's comment-convergence needs.* |
| **DNA design layer** | `counterpart/the Company/build-prep/design/` | live (gen'd) | **`tokens.json`+`emit.py`** (single-source look — census read it as dark/Catppuccin, but see DS1 §5: likely STALE vs the company's 2026-06-07 gold-warm migration); **`addresses.json` `ui://` registry + `element-map.json`** (element⇄address⇄feature⇄code); self-generating gallery; extend-by-registration discipline | frozen demos = input only |
| **ConceptV Design System** | `Projects/ConceptV Design System/` | live/production | **`colors_and_type.css`** (warm-paper+gold, 40+ tokens, production-proven); **223-icon SVG library** + desaturation tone pattern; **Vi diamond mark** (animated); three-pane workspace kit | ConceptV-domain coupling on the UI kits; static PNG V variants (not generative) |
| **Visual Designer (content-workbench)** | `Projects/Visual Designer/` | live | **the "socket registry" pattern** (Artifact/Component/Capability registries — glob-pattern dispatch, priority, invalidation); **`vi-invariant`** primitives (addressability/registry/resolution/topology/provenance/blocks); ResizablePanel | in-memory only (no persist); narrow domains → generalize to one `SocketRegistry` |
| **design/blueprint (J1–J9)** | `~/company/design/blueprint` | designed (9 quality-passed/43) | the **address spine / build spec** (every view is `ui://`-grounded, form-lint enforced); the per-view FORM targets | the 20 rendered mockups are form-check input, NOT layout law; 8 placeholder graph templates abandoned |
| **Wildcard MODES** | `build-prep/front-interface` | mixed | **SLIDE = the element-directed recognition surface** (*per wildcard's report*: ~1,878 element-bound annotations, direction is at-elements-not-slides — count unverified — *the merge's PRIMARY surface*; render layer is the gap); **DOCUMENT = sections-as-sub-address-channels** (board://+cc_channel substrate live, render gap) | GRAPH mode = **already the Instrument** (don't rebuild); TEAM mode = folds into presence |
| **Graph-of-minds Face** | `front-interface/GRAPH_OF_MINDS_SUBSTRATE.md` | substrate built-unverified, face unbuilt | **minds/sessions as first-class addressable units** (`session://`/`clone://`/`mind://` + 8 lenses) — navigable/drillable fleet | open D1: fold into Instrument (session-as-unit projection) vs separate surface — lean: **fold in** |
| **Voice UI** | `voice/` + blueprint B2 | infra live, render UI unbuilt | **swappable STT/TTS registries** (never hardcode providers); the **`speakable` universal transform** (one cleaner for every voice path) | thin render layer over live `/api/stt`·`/api/tts` is the only build |

**Dead/empty (verified):** `Projects/Visual DNA` (empty), `Projects/Visual-Designer` (screenshots only), `counterpart/concept-factory` (raw chat history — context only).

### 4.4 THE MERGE PROPOSAL (synthesized — provisional, Tim is the judge)

The merge is a **COMPOSITION of existing parts + a render layer for unrendered designs** — *most of the substrate already exists; the visible work is RENDER + WIRE*, not new engines:

- **Spine:** the Instrument (`surface/app`'s projection field, tri-form-factor, four-axis OPTICS) is the topology surface and the merged shell's backbone — inherited wholesale.
- **The directable layer:** wildcard's **element-bound capture grammar** (`{element_id, annotation_type, reaction, …}` → state mutation → re-project) wraps every rendered point/element. This is also how §1's comment-convergence happens: direction-at-an-address → `cc_board.comment(addr,…)`, one store.
- **Modes are projections, not apps:** SLIDE (element-flow), GRAPH (=Instrument), DOCUMENT (board://+cc_channel sections), MINDS (session-units) — one resolver, different arguments. tldraw composition (`canvas/app`) becomes one **mode/viewport** inside the shell (flip to it to drag-wire, flip back — both live underneath, as canvas already does with the tldraw Editor), not a second app.
- **One design system:** absorb a token system + the `ui://` address registry + the icon library + the Vi mark + the socket-registry pattern + `vi-invariant` primitives. **⚠ but THREE token systems exist and conflict (new decision DS1 below).**
- **Voice / loadable-brain:** voice registries + `speakable` as-is; click-an-address → `territory_for(address)` → a supervised Claude Code brain → talk → act → re-project (the bootstrap bottleneck-breaker).
- **doc_review_server** stays as the native-mobile board surface (or its comment+chat capability is absorbed into the shell's DOCUMENT mode); not conflated with composition/projection.

**Net build shape:** RENDER the unrendered (SLIDE component, DOCUMENT sections, voice controls, graph-of-minds face) + WIRE them to the live backend + CONVERGE the duplications (comment stores → `cc_board.comment`; channels → one identity; stores → one Supabase) + UNIFY the design system. The mockups/demos are disposable input; the **address spine is law**.

---

## 5. OPEN DECISIONS surfaced for Tim (only the ones consolidation forces)

*(From divergence-ledger §A; surfaced at Tim's altitude. Do not block the passes on these.)*

1. **Channel member identity (ID2)** — when a session ends, is the durable channel member **the person** or **the session**? This is the hinge the channel-union turns on (handle-id vs uuid-id can't join without it).
2. **The "one Supabase backend" scope (§3)** — does it mean the internal **union store**, the external **client-exposure/auth** layer, or both fused? (They share Postgres, oppose on RLS/posture.)
3. **DS1 — the canonical design-system "look" (NEW; corrected after verifying the in-repo tokens).** There are multiple token systems, but they **agree more than the census first suggested**. Verified in-repo: `design/_system/tokens.json` is a **GOLD-PRIMARY WARM theme** (Tim, 2026-06-07, marked *final*) — gold `#e6ab5c` as THE identity colour, warm-charcoal base, *"NO green/mint/teal anywhere"* (the green/mint was deliberately removed). **ConceptV Design System** (`colors_and_type.css`) is **also gold-warm** (gold `#E0C010`, warm-paper base). So gold-warm is the shared identity; the census's "DNA = dark/Catppuccin/mint" read is **likely STALE** (it predates the 2026-06-07 gold migration — needs confirming against the current counterpart DNA tokens). The genuine open question is therefore *narrow*, not a three-way aesthetic war: **(a) light warm-paper base (ConceptV) vs dark warm-charcoal base (company tokens); (b) reconcile the two gold hues (`#e6ab5c` vs `#E0C010`); (c) confirm whether counterpart's DNA tokens are stale and re-home the single source.** This still gates FORM, but it's a reconciliation, not a fork.
4. *(Deferred unless forced)* the other three ledger decisions — `file://`-vs-`cas://` identity, `cluster://` nature, Shape-B addressability — are store-internal and not yet on the critical path for channels/frontends.

---

## RELATES
`THE-ONE-SYSTEM.md` (the frame) · `UNION-MAP.md` (the reconciled inventory + clusters) · `UNION-DIVERGENCE-LEDGER.md` (the 5 Tim decisions + build-state honesty) · `CHALLENGE-storage-supabase.md` (the store verdict) · `CHALLENGE-unification-feasibility.md` (grammar≠resolution≠identity) · `CHANNEL-LOOP-BOARD.md` · `../front-interface/INTERFACE_INVENTORY`+`INTERFACE_EXCAVATION` (the stale FE inventory this pass refreshes) · `../../migration-pending/MIGRATION-REGISTER.md` (the physical folder-homing, a prerequisite consolidation).
