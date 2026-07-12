# Resolved-Context — Completion Criteria (the truth-table)

> Backend slices only (UI = with Tim). Each criterion is VERIFIED BY USE — a real observed behavior, never
> code-reading. Grounded in RESOLVED-CONTEXT-{A,B,C}. Status: [ ] open · [x] done+verified · [~] partial.

## C0 · Triad
- [x] C0.1 CRITERIA/GUIDE/SYNTHESIS exist, consolidated from A/B/C, loop-ready. *(this commit)*

## C1 · SLICE-SUB — the recursive unit substrate (local Supabase :15432)
- [ ] C1.1 **One recursive schema** exists: `unit {id, parent_id, type, state, address_path, body, meta, ts}` —
      NO per-level tables (Tim's correction 1: scale-relative; sentence⊂message⊂session⊂project all the same unit).
- [ ] C1.2 **Types are registry rows, not code**: a `unit_type` table declares each type + its LIFECYCLE
      (legal states + transitions). Adding a type/state = an INSERT, zero DDL/code.
- [ ] C1.3 **Illegal transition REFUSED loud** — verified by a real failed UPDATE (like cc_board's draft→open refusal).
- [ ] C1.4 **State transitions FIRE** (Tim's correction 2: state-as-axis-with-triggers): a real
      `pg_notify`/Realtime event observed on a state change (e.g. →open), carrying the unit address.
- [ ] C1.5 **Address = the containment path** — derived/maintained (parent chain), queryable; children/descendants
      queries work (one recursive CTE).
- [ ] C1.6 **The anti-loss query works**: "all units in state=open (nobody returned to them)" returns truth.
- [ ] C1.7 Schema placement COORDINATED with the embedding session via the fabric thread (no fork of their conventions).

## C2 · SLICE-S1 — turn-resolution live (lab; NOT Tim's global settings)
- [ ] C2.1 A lab session's UserPromptSubmit hook calls a RESOLVER script → bridge (:8770 embed and/or corpus/role) →
      injects resolved context on stdout — and the model DEMONSTRABLY USES it (answers from injected facts it
      could not otherwise know).
- [ ] C2.2 The resolver reads the SUBSTRATE too (units in Supabase) — recall from the unit store, not just prose.
- [ ] C2.3 SessionStart matcher:"compact" re-injection verified in the lab (context survives a compaction boundary).
- [ ] C2.4 Resolver is loud-fail (bridge down → visible error in hook output, never silent) + logs each resolution
      (what was injected, why) somewhere queryable.

## C3 · SLICE-JUDGES — the ledger fills itself + laws become grammar
- [ ] C3.1 `roles/ctx_salience.py` exists (file-discovered, output_schema, fail-loud — mirrors the proven role shape):
      given a span/unit body → `{kind, salience, supersedes?, lod}` validated JSON, fired via run_role.
- [ ] C3.2 Verdicts LAND in the substrate (units gain verdict data; queryable: "all decisions", "all superseded").
- [ ] C3.3 A **Stop-hook validator** in the lab checks a draft response against ≥2 of Tim's laws (no time-estimates;
      evidence-marking on completion claims) and **BOUNCES a violating response** (observed: the model retries) while
      passing a clean one.
- [ ] C3.4 The laws the validator enforces are DATA (a rules table/file), not hardcoded in the script.

## C4 · SLICE-CHAINS — backend only
- [ ] C4.1 **Reference edges** between units exist (`unit_edge {from, to, kind}`, kinds registry-declared) — a reply/
      build-on/supersede is an edge at an address.
- [ ] C4.2 **Chain derivation** works: given a unit, the closure of its references (the chain) returns as a query.
- [ ] C4.3 Fork-per-chain mechanics DESIGNED + the headless part verified: a fork can be spawned scoped to a chain
      (its context = the chain's units), and registers in the fabric as a child of the main (parent lineage visible).
- [ ] C4.4 A cross-chain check exists (even minimal): a judge/query that surfaces two chains touching the same
      referent (the contradiction/duplication watch, v0).

## Standing (every criterion)
Loud-fail · nothing hardcoded (types/lifecycles/rules/roles = registry data) · verified by USE with the observed
evidence noted beside the checkbox · git small commits to ~/company main · found-work added to scope · UI held for Tim.
