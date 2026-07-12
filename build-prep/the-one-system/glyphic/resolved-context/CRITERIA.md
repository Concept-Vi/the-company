# Resolved-Context — Completion Criteria (the truth-table)

> Backend slices only (UI = with Tim). Each criterion is VERIFIED BY USE — a real observed behavior, never
> code-reading. Grounded in RESOLVED-CONTEXT-{A,B,C}. Status: [ ] open · [x] done+verified · [~] partial.

## C0 · Triad
- [x] C0.1 CRITERIA/GUIDE/SYNTHESIS exist, consolidated from A/B/C, loop-ready. *(this commit)*

## C1 · SLICE-SUB — the recursive unit substrate (local Supabase :15432)
- [x] C1.1 **One recursive schema** exists — `ctx.unit` (migrations/001_ctx.sql, applied 2026-07-13). *(Observed:
      session→message→block all rows of the one table.)*
- [x] C1.2 **Types are registry rows** — `ctx.unit_type {states, transitions}` seeded (session/message/block/comment);
      lifecycle changes = INSERTs.
- [x] C1.3 **Illegal transition REFUSED loud** — *Observed: `update … state='answered'` (from draft) → ERROR
      'ctx: illegal transition "draft"->"answered" for type "block". Legal from "draft": ["open"]'.*
- [x] C1.4 **State transitions FIRE** — *Observed: LISTEN ctx_state received a real payload
      `{id…0003, type:block, old:draft, new:open, address:glyphic-session/00000000/00000000}` on the legal flip.*
- [x] C1.5 **Address = the containment path** — *Observed: derived `glyphic-session/00000000/00000000` from the
      parent chain; roots must supply their own (loud otherwise).*
- [x] C1.6 **Anti-loss query works** — *Observed: `state='open'` returned the open block ("one response, many
      faces — the ConceptV echo" — fittingly, the first unit ever to open).*
- [~] C1.7 Coordination: durable channel post landed on chan-provider-registry-a3d23aae (queued to both members;
      the live supervisor :8771 was DOWN so no live inject — they pick up next turn; I adapt if they object).
      NOTE: advisor tool was UNAVAILABLE at the gate — self-applied the scrutiny (additive-only, collision-checked,
      reversible one-drop, idempotent); flagged honestly here.

## C2 · SLICE-S1 — turn-resolution live (lab; NOT Tim's global settings)
- [x] C2.1 **PROVEN**: lab `claude -p` (haiku) asked for the codeword/open decisions → answered **MOSSWOOD-9** +
      the open UI-decision — facts existing ONLY in the substrate, delivered by the UserPromptSubmit resolver.
      *(Artifacts: lab/resolver.sh + lab/lab-settings.json; lab at scratchpad/ctxlab.)*
- [x] C2.2 **PROVEN**: the resolver reads ctx.unit live (state-weighted [open]+relevance query) — the injected
      block listed the three matching units with their addresses. (v0 relevance = ILIKE+state; embed-match = v1 open.)
- [~] C2.3 **Resume-boundary PROVEN**: SessionStart matcher:"resume" re-injection observed (model quoted
      CTXLAB-RESUME-OK on --resume). The compact matcher is wired IDENTICALLY (same mechanism; source=compact
      doc-confirmed) but an actual compaction could not be forced headless — honestly: resume proven, compact
      wired+doc-confirmed, live-compact test with Tim's session later.
- [x] C2.4 **PROVEN loud-fail**: resolver at a dead PG port printed `RESOLVER ERROR: ctx substrate unreachable…
      Connection refused` into the hook output (never silent); resolutions logged to resolutions.jsonl (evidence copy committed).

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
