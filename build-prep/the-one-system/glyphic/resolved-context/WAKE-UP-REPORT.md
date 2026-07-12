# Resolved-Context — the overnight report (2026-07-13)

> One night, one loop, four slices — the backend you asked for is **built and proven by use**. Every claim
> below was observed running, not read from code. The UI is untouched, waiting for us to do together.

## What exists now (proven)
1. **The substrate is live** (`ctx` schema, local Supabase :15432, beside the ledger): ONE recursive unit table —
   your correction exactly: sentence⊂message⊂session⊂project, all the same unit, address = the containment path.
   Lifecycles are **registry rows** (adding a state = an INSERT). An illegal transition **refuses loudly**
   (observed). A legal one **fires** `pg_notify` with the unit's address (observed, twice) — your state-axis
   correction: the data layer reacts, no agent has to remember.
2. **Turn-resolution works, live**: a session with the resolver hook asked "what's the codeword?" — and the model
   answered **MOSSWOOD-9 + the open decision**, facts that existed only in the substrate. Context is now
   *resolved into the turn*, not hoped-for. Resume-boundary re-injection proven too.
3. **The ledger fills itself**: the `ctx_salience` judge (a drop-in role — no restart needed, 0.56s/judgment)
   classified every unit ({kind, salience, lod}) and the verdicts landed queryable — "show me all decisions" works.
4. **Your laws are becoming grammar**: the form-validator checks drafts against rules-as-data (no-time-estimates,
   completion-claims-need-evidence with an evidence-absolver). Logic proven by test — bounce + absolve both observed.
5. **Chains + the fork brief, as a `company` command** (your mid-build steer — CLI command, not a lab script):
   `company ctx open` (the anti-loss view) · `chain` (the closure) · `brief` (the boot-context a chain-scoped
   fork receives) · `crossings` (the shared-referent watch) · `types`. All ran against the real substrate.

## The honest ~s (what ISN'T proven yet)
- **Post-compaction re-injection**: wired identically to the proven resume-hook + doc-confirmed, but a real
  compaction wasn't forceable headless — we'll see it live in a long session.
- **The live validator bounce**: a real finding — **the Stop hook doesn't fire in `claude -p` headless mode**
  (unit-proven logic, but the interactive bounce demo is for a live session — with you).
- **Fork spawn + fabric-child registration**: the brief (the fork's boot-context) is real; actually spawning +
  registering the child is the interactive half.
- **Coordination**: the schema heads-up to the embedding session is QUEUED (their live path was down) — not yet acked.

## Infra notes (recovered overnight, restart-authority)
Found bridge, litellm, and the resident brain all down (a restart had swept them). Recovered: bridge (systemctl),
litellm (:4100 — the :8000 note in services.json is stale), chat-4b via `company up --evict` — **the policy evicted
the pplx embedder to fit the brain**; rebalance with the wake-ritual combo when you're up. The session supervisor
(:8771) is still down (wasn't needed). Also: role discovery needs no restart (per-call), now proven.

## Ready for the session together
The substrate is live and full of real, typed, addressed, judged units — **the UI we build together today renders
THIS, not a mock**: blocks with states you can click, chains, verdicts, the open-list. Everything committed on
`~/company` main (d32d9e79 → 174bef43 → ed2564f4 → cf456178 → this).
