# The ui://→code:// join — COMPLETE ACCOUNTING (2026-07-02)

*The pointing mechanism: point at what you can see → reach the code behind it. Three-sided accounting (design-side · ledger-side · consumer-side), produced by fan-out agents + direct ledger queries, so Tim can decide POPULATION. Full agent reports live in the session transcript; this is the synthesis + the decision. Part of ② (NORTH-STAR.md).*

## THE ONE-LINE SHAPE
**The join is real but frozen at its hand-made seed** — 104 of 505 registered UI addresses carry a code link (all hand-curated; the 402 machine-added addresses have none); the resolver reads a sidecar index built when the registry was 71 rows (3 weeks stale, every "unresolved" flag in it now false); a second live front-end (surface/app, 36+ addresses, 4 whole regions) grew entirely OUTSIDE the address space; and agents have NO tool to ask the question at all.

## SIDE 1 — design-side (the sidecar world)
- **addresses.json**: 505 ui:// addresses, 32 regions. `code` on **104/505 (20.6%)** — free-text `path:symbol` strings (0 are code:// URIs), 182 sub-refs. The 402 RG10 machine rows: `maps_to_feature`+`howto` but **no code links**.
- **code-symbols.json** (what resolve_scope reads): 94 entries, `code://<file-stem>` lossy form, **mtime Jun 7 — built from a 71-address registry** (1/7th of today's). All 7 `resolves:false` are false-dead today; 2 keys carry a parse defect (annotation baked into the symbol name). 68 distinct ui:// referencers (⊂ the 104).
- **Link integrity** (all 182 sub-refs checked): 172 resolve · **1 genuinely dead** (`ui://registry/proposals/approve` → renamed route) · 10 malformed-but-alive (missing dir prefix etc.).
- **Live FE truth**: canvas = 91 distinct registered `data-ui-ref` (100% registered) + 8 bare legacy (1 unregistered). **surface/app = 36 static + 12 template families, 0 registered** — regions `controls/instrument/nav/strata` exist only in live code. Mockups: 9 unregistered orphans, 105 registered-but-in-no-mockup; element-map.json stale (Jun 10).
- **Contract fulfilment** (CONNECTION-CONTRACT.md): region/represents/capabilities present 505/505 (capabilities in the wrong encoding); `code` 104/505; kind/title/resolve/states/tier **0/505**.

## SIDE 2 — ledger-side
- 456 real ui:// *mentions* (407 distinct) — files (mostly mockups) that name a ui:// address; direction code-file→references→ui-addr; only 1 resolves. **Zero ui:// nodes. Zero powered-by edges.** The ledger knows the addresses exist; it does not hold the join.
- BUT: the overnight work landed **calls-endpoint edges (FE → bridge routes, 93/104 resolved)** + the full call graph + symbol nodes — see THE INSIGHT below.

## SIDE 3 — consumer-side (what must keep working)
- **7 internal consumers** (address_help, surface_intent_at, blast_radius, self_changes_at, _member_to_files/approve_reach, /api/scope, territory) + **12 bridge routes** feeding both FEs. Exact contract: `{address, symbols[sorted], scope[sorted repo-relative], stale, note}`; malformed→raise; unmapped→empty-not-raise; **empty scope = DENY-ALL (load-bearing safety — must never invert)**.
- **NO MCP tool exists** — agents cannot ask "what code powers this element". The shared function CREATES the agent face, not just replaces a source.
- blast_radius also needs per-symbol records → the shared layer = TWO functions: `resolve_scope(ui_addr)` + `symbol_record(code_id)`.
- **Symbol-id continuity**: persisted build-intent payloads + FE navigation carry the lossy `code://<stem>/<sym>` ids → cutover needs an alias map or one-shot canonicalization.
- **Verification gate**: ~17 acceptance tests (address_scope, conv_blast[needs injectable-source seam], conv_reach, territory, ui_registry, …) + a live surface turn.

## THE INSIGHT (what the overnight work changed)
The join no longer has to be hand-curated. The chain **ui-element → component file (data-ui-ref/stamp, deterministic) → its calls-endpoint edges (in the ledger, built overnight) → bridge route (serves-endpoint) → backend symbols (call graph)** is now COMPUTABLE from the ledger. The 104 hand links become *verification data* for a derived join, per deterministic-work-to-code.

## TIM'S DECISION + REFRAME (2026-07-02): **A then B** — and the mechanism, not the data, is the product
Tim: the mockups AND the UI attached to the registry are NOT in use — the current UI was AI-built to test the backend; the REAL interface hasn't been designed or built yet (that's ③). The ui→code mechanisms are meant to be **universal, automatic, generalised**. Same as the projection: everything is scaffolding for now-which-is-now.
**Build implication:** the join is DERIVED INSIDE THE DETERMINISTIC LEDGER PASS (recomputed every extraction, like calls/imports) — never a one-time population, never a curated registry. Today's FE (canvas 91 refs, surface 36+templates) is the first input + proof; the 104 hand links are verification data; the ③ real UI will be born addressed+joined automatically by the same pass. The consumers' contract (5-key shape, empty=DENY-ALL) is preserved; the current 505-address registry is data-to-verify-against, not a universe to preserve.

## THE POPULATION DECISION (Tim's)
- **A — Derive from the living system (recommended):** mechanically compute the join from live FE annotations + the ledger's endpoint/call graph; canonicalize + fold in the 104 hand links (repairing the 1 dead + 10 malformed); register surface/app's 36+4-regions into the address space; everything underivable stays honestly unjoined (deny-all preserved). No model needed for the bulk.
- **B — A + a bounded model pass** for the judgment tail (which symbol is THE powering one when several are plausible; proposals for registered-but-not-live addresses), asked pointed/bounded/fed.
- **C — Seed-only:** canonicalize the 104, leave 401 unjoined. (Too thin — the pointing mechanism would answer for 1/5th of the surface.)

## Extensions/improvements identified (written down per the standing directive)
1. ui:// becomes first-class ledger NODES; the join = typed edges (`powers`/`represented_by`) — the coordinate space gains the UI axis.
2. The TWO shared functions (`resolve_scope`, `symbol_record`) ledger-backed, projected to MCP (new agent tool — closes the zero-agent-face gap) + UI (existing bridge routes).
3. Register surface/app's 4 regions (controls/instrument/nav/strata) + 36 addresses + template families.
4. S0 projection fields (kind, capabilities-object) — mechanical contract fulfilment; `tier` = a governance decision per address (later, Tim).
5. Repair the 1 dead + 10 malformed links centrally during population.
6. Alias map for the lossy→canonical symbol-id continuity (persisted payloads keep matching).
7. Injectable-source seam kept for the test fixture (conv_blast_acceptance).
8. Retire code-symbols.json + element-map.json as SOURCES (comment-out reads, per Tim's no-fallback rule); parse.py/symbols.py generators retire with them once the ledger derivation runs.
