# Completion Criteria — "The Core, Self-Serve for Every Session" (scope C)

*loop-prep doc 2. The truth-table the build loop runs against. Each item is a VERIFIABLE statement about the system, checked BY USE (run it on real data), never by code-reading. Built on RESEARCH_SYNTHESIS.md (the evidence base) — most primitives exist; these criteria are the new work. Additive to a (clone-fleet, done) + b (Heart/R13, structural done).*

## Verification rules (read before checking any box)
- **FUNCTION bar:** the behaviour is real, verified BY USE on real data (a real session, a real query, a real spawn) — no stub, no mock, no "the code looks right." State Observed/Inferred/Verified; only Verified checks a box.
- **FORM bar (every surface):** built from the design system's components (`canvas/app/src/components/kit.tsx`) + tokens (`design/_system/tokens.json`) — NO hardcoded values, NO bespoke one-offs; no overlaps; responsive; consistent scale/type/spacing; a NAVIGABLE visual/spatial surface, not a text-wall or list; empty/loading/error states present. A surface is green on form only when a design-critic pass (browser, screenshots) + `design/check.py` design-lint both pass. FORM is half of done.
- **Honest status:** ☐ = designed/not-built-or-verified · ☑ = verified by use. Today ALL are ☐ (the primitives exist; the C-work is not built). Never mark ☑ from code-reading.
- **Reuse-don't-parallel gate:** each item must EXTEND an existing primitive (named in the synthesis), not create a parallel one. An item that introduces a 2nd engine/registry/parser FAILS review regardless of function.

---

## C1 · Search hierarchy — live-edge ⊕ deep-corpus, scoped (FOUNDATION)
*Architecture: recollection (OUTER) = deep backfilled corpus, all scopes via its filters; session_recall (INNER) = the live edge; UNION at the freshness seam. Company builds the union + the project-stamp + exposure; recollection builds the delegation surface.*

- **C1.1 · live-edge recall (own session, zero lag)**
  FUNCTION — a session recalls its OWN current history including a turn from seconds ago (session_recall over the live transcript, no backfill wait) ☐ verified by use
- **C1.2 · the freshness-seam UNION**
  FUNCTION — one recall query returns BOTH a just-now live-edge hit AND an old deep-corpus hit, deduped at the seam (live-edge ⊕ recollection's deep corpus); a turn present in both appears ONCE ☐ verified by use
- **C1.3 · project scope on the live edge**
  FUNCTION — every live-spawned session carries a `project` (the supervisor stamps it at spawn, not only `cwd`); `list_agent_sessions(project=X)` returns exactly that project's sessions without an O(all) client scan ☐ verified by use
- **C1.4 · the three scopes resolve through ONE grammar**
  FUNCTION — a scoped recall with scope ∈ {own | project=X | cross-project} returns correct, scope-respecting results (own→only mine; project→only that project's sessions, live+deep; cross-project→the fleet), delegating deep scopes to recollection's filtered recall (NOT a parallel Company engine) ☐ verified by use
- **C1.5 · delegation surface is a real call-target (recollection's lane)**
  FUNCTION — Company's union layer calls recollection's filtered recall over the backfilled corpus via a stable seam (CLI/subprocess JSON), returning project/session_ids/sources-filtered hits ☐ verified by use (lands when recollection's backfill greens)
- **C1.6 · fail-loud + freshness honesty**
  FUNCTION — if the deep corpus is stale/un-backfilled for a scope, the result DECLARES it (never silently returns live-edge-only as if complete); embedder/engine down → teaching error, never silent empty ☐ verified by use

## C2 · Self-serve onboarding / discoverability (FOUNDATION)
*The pieces exist (capabilities(), start_guide, the supervisor mailbox, guide board-items); the gap is the ENTRY POINT that orchestrates them for a fresh/spawned session.*

- **C2.1 · a fresh session self-orients (pull)**
  FUNCTION — a brand-new session calls ONE onboarding op and learns: what it can do (capabilities), who it can talk to (live channels + members), what past-selves exist (era-clones), and how to learn the interface (guide entry) — composed, fail-loud on any missing leg ☐ verified by use
- **C2.2 · the supervisor delivers ORIENT at spawn (push)**
  FUNCTION — a supervisor-spawned session receives a Phase-1 ORIENT via the mailbox at spawn (it knows it's materialized/in-the-fabric) without a human telling it ☐ verified by use
- **C2.3 · the how-to guides are durable + discoverable**
  FUNCTION — the how-tos (set up scans/eras/channels/attachments/rules) exist as durable, addressed guide board-items a fresh session can list + read (not tribal channel knowledge) ☐ verified by use
- **C2.4 · prepared for BOTH fresh and spawned**
  FUNCTION — both a freshly-launched session and a supervisor-spawned clone reach the same onboarding answer (no path is left un-onboarded) ☐ verified by use

## C3 · Self-serve gap closures
- **C3.1 · a session creates its OWN era clone end-to-end**
  FUNCTION — a session (incl. a supervised one) discovers its own source transcript, picks a cut point, and creates+consults its own era clone via MCP — no lead/operator hand-holding ☐ verified by use
- **C3.2 · a clone is discoverable in a common channel**
  FUNCTION — a created/onboarded clone is reachable in a named/common channel and its reflection is surfaced there (not only in `.data/clones/`) ☐ verified by use
- **C3.3 · channel RULES + PROJECT-INFO as first-class data**
  FUNCTION — a session sets a channel's rules + project-info and another session reads them back (durable channel data, via the attachment-type registry or a channel event — reuse, not a parallel store) ☐ verified by use
- **C3.4 · add a NEW attachment type self-serve**
  FUNCTION — a session adds a new attachment type and it goes live without a manual server restart (an MCP create op + registry refresh; attachment_type promoted into `_CORPUS_REGISTRIES` so create_*/cognition_info see it) ☐ verified by use

## C4 · MCP coherence
- **C4.1 · scoped search is a clean MCP tool**
  FUNCTION — the session⊂project⊂cross-project recall (C1) is one coherent MCP op any session calls with a scope arg (not split across tools/servers) ☐ verified by use
- **C4.2 · session/peer/clone discovery in one place**
  FUNCTION — a session discovers past+live sessions, its channels, and era-clones through coherent MCP ops (session_search exposed; not only live `cc_channel list`) ☐ verified by use
- **C4.3 · supervisor + service health are queryable**
  FUNCTION — a session can check (via MCP) whether the supervisor + the model/embed/TTS services are up, so a missing service fails LOUD not silently ☐ verified by use
- **C4.4 · one bootstrap door**
  FUNCTION — a fresh session joins the fabric without the operator-only `--mcp-config` flag being the sole path (the split mcp_face vs company-channel bootstrap is resolved or bridged) ☐ verified by use

## C5 · Frontend exposure (on the existing design system) — FORM-heavy
- **C5.1 · search scope picker**
  FUNCTION — the frontend search (ForagerBar) lets the operator choose scope (own / project / cross-project) and results respect it (the C1 hierarchy, by use) ☐ verified by use
  FORM — built from kit.tsx + tokens (no bespoke), a navigable picker (not a raw dropdown of strings), coherent with the existing ForagerBar, responsive, empty/loading/error states ☐ verified by design rubric
- **C5.2 · unified onboarding / discovery region**
  FUNCTION — one frontend surface composes capabilities + live peers + era-clones + "learn the interface" (the C2 answer, rendered) ☐ verified by use
  FORM — kit.tsx + tokens, navigable visual surface not a text-wall, design-lint clean, fail-loud on missing legs ☐ verified by design rubric

## Product Face (standing group — the whole scope-C frontend)
- **PF.1** every scope-C surface uses design-system components + tokens only (design-lint `design/check.py` passes — no hardcoded values) ☐
- **PF.2** no overlaps; responsive at the stated widths; consistent scale/type/spacing ☐
- **PF.3** every surface reads as a navigable visual/spatial surface, not a text-wall or list ☐
- **PF.4** a design-critic pass (browser + screenshots), lens = the design rubric, passes every surface (subjective taste calls flagged to Tim, never green-painted) ☐

---

## PRIORITY ORDER (foundations before features)
1. **C1** (search hierarchy) — the spine everything queries; sits on recollection's backfill (sequence C1.5 against the backfill greening).
2. **C2** (self-serve onboarding) — the entry every fresh session needs; reuses the supervisor mailbox + capabilities + guides.
3. **C3** (gap closures) — clones-self-serve, rules/project-info, attachment-types; independent, parallelizable.
4. **C4** (MCP coherence) — exposes C1/C2/C3 as one coherent session-self-service surface.
5. **C5** (frontend) — exposes the scopes + onboarding on the design system (FORM-gated); last, because it renders C1–C4.

## Cross-references
- HOW to build each → IMPLEMENTATION_GUIDE.md (next).
- WHAT EXISTS that each extends → RESEARCH_SYNTHESIS.md (the file:line evidence base).
- C1.5 delegation-surface detail → recollection brings it into the C1 guide section when its backfill driver (w9wl941ro) greens.
