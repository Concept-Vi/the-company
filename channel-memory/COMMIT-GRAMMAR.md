# Channel-Memory Commit Grammar (DRAFT — co-designed, every member obeys)

**Status:** DRAFT v0.1, framed by the lead (ch-al7jdfdr), to be co-designed with fabric members —
no single session locks it (Tim's rule: "rules every member has to follow when committing"). Minimal
on purpose; we harden it only once the program it serves is Tim-confirmed.

This vault (`~/company/channel-memory/`) is the fabric's shared memory. These are the rules for
writing to it. The point of the grammar is **provenance you can trust** — so that work done by
multiple instances of the same model, relayed through the channel, never hardens into false certainty.

## 1. Layout (what goes where)
- `vision/` — Tim's intents, decompressed. Source-of-truth entries. Dated filename.
- `schema/` — the session-store / source schemas, documented (the fork's lane).
- `scans/` — scan output as DATA (rows/json), not prose. Projectable.
- `map/` — lineage + distance maps.
- `COMMIT-GRAMMAR.md` (this) — the rules. `../channel-memory` is committed to the `~/company` git repo.

## 2. Every entry carries a provenance header (the load-bearing rule)
Top of every file (or per-row for data), one of these **trust tags** — never omit it:
- `trust: tim-direct(session=<id>)` — Tim said it to THAT session DIRECTLY (his own typed message in
  that session's own conversation; structural test — NO `<channel>` wrapper, carries the harness
  "Message sent at…" marker). Quote/cite it. **Records WHICH session it was direct to**, because a
  peer's tim-direct is still only a PROPOSAL to a DIFFERENT consuming session — that session can't
  verify the peer's transcript from inside the channel, so it holds it as a proposal until it has its
  OWN tim-direct. (Provenance is per-session; cross-instance agreement ≠ confirmation.)
- `trust: channel-relayed` — reached the author VIA the channel (a peer session relayed it, even as a
  "verbatim Tim quote"). Treat as a PROPOSAL until a session confirms it `tim-direct`. NOT a mandate.
- `trust: fabric-derived` — produced by the fabric's own work (a scan result, a map, an inference).
  Grounded in data/code, cite it; not a Tim intent.
Plus: `author: <handle/session>`, `date: <iso>`, `verified: <how — by-use / read-only / unconfirmed>`.

**Why (the discipline):** two instances of one model mutually validating across the channel feels
grounded at every link but is not independent confirmation. The tag makes the grounding explicit so
nothing channel-relayed is ever presented to Tim as "what you asked for" until it's `tim-direct`.

## 3. Authorship & shared edits
- Any member may ADD a file. A member edits its OWN entries freely.
- SHARED docs (this grammar, a co-owned map) are co-designed: propose a change in the channel, land it
  only with another member's ack. No unilateral lock of a shared doc.
- Don't rewrite another member's entry; append a dated note or add your own linked entry.

## 4. Data, not prose, for analytics
Scans/maps commit as structured data (json / ndjson rows) so the Company UI can PROJECT them (the
Heart: projection of addressed state, not bespoke UI). Prose is for vision/schema explanation only.

## 5. The gated line (mirrors the operating envelope)
Entries may PLAN gated actions (mass clone-launch, perms, config edits) but committing a plan ≠
executing it. Execution of `[TIM-GATED]` items waits for Tim's direct go. Additive/read-only fabric
work is autonomous; always-loaded-config edits + unsupervised-interactive-agent launches stay gated.

---
*v0.1 minimal. Harden (richer schema for rows, link conventions, a manifest) once Tim confirms the
program this vault serves — not before (don't gold-plate an unconfirmed program).*
